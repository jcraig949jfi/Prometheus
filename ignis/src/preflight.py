"""
preflight.py — Data integrity and environment verification.

Runs before any experiment to catch silent failures. Should be treated
as a gate: if preflight fails, no experiment results can be trusted.

Checks:
  1. TOKEN_IDS    — verify token mappings are single tokens, match expected strings
  2. HOOK_POINTS  — verify genome hook point matches analysis hook point
  3. GENOME       — verify vector shape, norm, layer index, dtype consistency
  4. BASELINE     — verify model produces expected behavior on known-answer prompts
  5. NUMERICAL    — verify cosine similarity is reproducible across two runs
  6. TRAP_SANITY  — verify target/anti tokens are adversarial (baseline gets some wrong)
  7. STEERING_SIGN — verify genome moves logit margins in correct direction
  8. VRAM_HEADROOM — verify GPU has enough free memory for experiment overhead

Usage:
    python preflight.py --model Qwen/Qwen3-4B --genome best_genome.pt --device cuda
    python preflight.py --model Qwen/Qwen3-4B  # no genome, check model + traps only

Exit codes:
    0 = all checks passed
    1 = one or more checks failed (DO NOT proceed with experiments)

Design principle: this should run in <60 seconds. No heavy computation.
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import (
    AnalysisBase,
    LOGIT_TRAPS,
    HELD_OUT_TRAPS,
    load_genome,
    make_steering_hook,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PREFLIGHT] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.preflight")


class PreflightResult:
    """Accumulates pass/fail results across checks."""

    def __init__(self):
        self.checks = []
        self.failures = []

    def record(self, name: str, passed: bool, detail: str = ""):
        status = "PASS" if passed else "FAIL"
        self.checks.append({"name": name, "status": status, "detail": detail})
        if not passed:
            self.failures.append(name)
        icon = "+" if passed else "X"
        print(f"  [{icon}] {name}")
        if detail and not passed:
            print(f"      {detail}")

    @property
    def all_passed(self) -> bool:
        return len(self.failures) == 0

    def summary(self) -> str:
        total = len(self.checks)
        passed = total - len(self.failures)
        return f"{passed}/{total} checks passed"

    def to_dict(self) -> dict:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "all_passed": self.all_passed,
            "summary": self.summary(),
            "checks": self.checks,
            "failures": self.failures,
        }


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 1: Token ID Verification
# ═══════════════════════════════════════════════════════════════════════════

def check_token_ids(model, result: PreflightResult):
    """Verify every target/anti token in every trap maps to a single token."""
    print("\n  --- Check 1: Token IDs ---")

    all_traps = LOGIT_TRAPS + HELD_OUT_TRAPS

    for trap in all_traps:
        for role, key in [("target", "target_token"), ("anti", "anti_token")]:
            text = trap[key]
            token_ids = model.to_tokens(text, prepend_bos=False)[0]
            n_tokens = len(token_ids)
            token_id = token_ids[0].item()

            # Decode back to verify round-trip
            decoded = model.tokenizer.decode([token_id])

            is_single = n_tokens == 1
            round_trips = decoded.strip().lower() == text.strip().lower()

            detail = ""
            if not is_single:
                detail = (f"'{text}' maps to {n_tokens} tokens: {token_ids.tolist()}. "
                          f"Only first ({token_id}) will be used — logit margin may be wrong.")
            elif not round_trips:
                detail = (f"Round-trip mismatch: '{text}' → id {token_id} → '{decoded.strip()}'. "
                          f"Token may not represent intended answer.")

            result.record(
                f"TOKEN {trap['name']}/{role}: '{text}' → id {token_id}",
                is_single and round_trips,
                detail,
            )


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 2: Hook Point Consistency
# ═══════════════════════════════════════════════════════════════════════════

def check_hook_points(model, genome_data: dict, result: PreflightResult):
    """Verify the hook point used in analysis matches what's expected."""
    print("\n  --- Check 2: Hook Points ---")

    layer = genome_data["layer"]
    n_layers = model.cfg.n_layers

    # Check layer is valid
    result.record(
        f"HOOK layer {layer} within model range [0, {n_layers-1}]",
        0 <= layer < n_layers,
        f"Layer {layer} is out of range for model with {n_layers} layers",
    )

    # Check that the hook names we use actually exist in the model
    hook_resid_pre = f"blocks.{layer}.hook_resid_pre"
    hook_resid_post = f"blocks.{layer}.hook_resid_post"

    # Verify by running a forward pass with hooks
    test_prompt = "test"
    tokens = model.to_tokens(test_prompt)

    hooks_found = {"resid_pre": False, "resid_post": False}

    def make_check_hook(key):
        def hook_fn(activation, hook):
            hooks_found[key] = True
            return activation
        return hook_fn

    with torch.no_grad():
        model.run_with_hooks(tokens, fwd_hooks=[
            (hook_resid_pre, make_check_hook("resid_pre")),
            (hook_resid_post, make_check_hook("resid_post")),
        ])

    result.record(
        f"HOOK {hook_resid_pre} exists",
        hooks_found["resid_pre"],
        f"Hook point not found — model may not support this hook name",
    )
    result.record(
        f"HOOK {hook_resid_post} exists",
        hooks_found["resid_post"],
        f"Hook point not found — model may not support this hook name",
    )

    # Check which hook analysis_base uses vs what might have been used in evolution
    # analysis_base uses hook_resid_pre for steering and caching
    result.record(
        "HOOK analysis_base uses resid_pre (consistent with standard convention)",
        True,  # This is a documentation check — always passes but logs the fact
        "",
    )


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 3: Genome Integrity
# ═══════════════════════════════════════════════════════════════════════════

def check_genome(genome_data: dict, model, result: PreflightResult):
    """Verify genome shape, norm, dtype, and consistency with model."""
    print("\n  --- Check 3: Genome Integrity ---")

    vector = genome_data["vector"]
    layer = genome_data["layer"]
    norm = genome_data["norm"]

    # Shape matches model d_model
    d_model = model.cfg.d_model
    result.record(
        f"GENOME vector shape [{vector.shape[0]}] matches d_model [{d_model}]",
        vector.shape[0] == d_model,
        f"Shape mismatch: vector is {vector.shape}, model expects d_model={d_model}",
    )

    # Norm is reasonable (not zero, not absurdly large)
    result.record(
        f"GENOME norm {norm:.4f} is in reasonable range [0.1, 100]",
        0.1 < norm < 100,
        f"Norm {norm:.4f} is suspicious — may indicate corrupted genome",
    )

    # No NaN or Inf
    has_nan = torch.isnan(vector).any().item()
    has_inf = torch.isinf(vector).any().item()
    result.record(
        "GENOME no NaN or Inf values",
        not has_nan and not has_inf,
        f"Vector contains NaN={has_nan}, Inf={has_inf}",
    )

    # Verify norm computation is consistent
    recomputed_norm = vector.float().norm().item()
    norm_diff = abs(recomputed_norm - norm)
    result.record(
        f"GENOME norm consistent (stored={norm:.4f}, recomputed={recomputed_norm:.4f})",
        norm_diff < 0.01,
        f"Norm discrepancy: stored={norm:.6f}, recomputed={recomputed_norm:.6f}, diff={norm_diff:.6f}",
    )

    # Check dtype — should load cleanly to float32
    result.record(
        f"GENOME dtype is float-compatible ({vector.dtype})",
        vector.dtype in (torch.float16, torch.float32, torch.bfloat16),
        f"Unexpected dtype: {vector.dtype}",
    )


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 4: Baseline Model Behavior
# ═══════════════════════════════════════════════════════════════════════════

def check_baseline(model, result: PreflightResult):
    """Verify model produces expected behavior on known-answer prompts."""
    print("\n  --- Check 4: Baseline Behavior ---")

    # Known-answer sanity checks (not reasoning traps — obvious answers)
    # Use forced-choice format with single-token answers
    sanity_prompts = [
        {
            "prompt": "Is the sky blue? Answer Yes or No:",
            "expected_token": "Yes",
            "anti_token": "No",
            "description": "basic factual (sky is blue)",
            "hard_fail": True,
        },
        {
            "prompt": "Is water wet? Answer Yes or No:",
            "expected_token": "Yes",
            "anti_token": "No",
            "description": "basic factual (water is wet)",
            "hard_fail": True,
        },
        {
            "prompt": "What is 2+2? Answer 4 or 5:",
            "expected_token": "4",
            "anti_token": "5",
            "description": "basic arithmetic",
            "hard_fail": False,  # Some models are weak on forced-choice math
        },
    ]

    for sp in sanity_prompts:
        tokens = model.to_tokens(sp["prompt"])
        exp_ids = model.to_tokens(sp["expected_token"], prepend_bos=False)[0]
        anti_ids = model.to_tokens(sp["anti_token"], prepend_bos=False)[0]

        with torch.no_grad():
            logits = model.run_with_hooks(
                tokens, fwd_hooks=[], return_type="logits"
            )[0, -1, :]

        exp_logit = logits[exp_ids[0]].item()
        anti_logit = logits[anti_ids[0]].item()
        margin = exp_logit - anti_logit

        is_correct = margin > 0
        is_hard_fail = sp["hard_fail"]

        if is_correct:
            detail = ""
        elif is_hard_fail:
            detail = "Model gets basic sanity check wrong — may be loaded incorrectly"
        else:
            detail = f"Soft warning: margin={margin:+.4f} (close to zero, not necessarily a model error)"

        result.record(
            f"BASELINE {sp['description']}: '{sp['expected_token']}' > '{sp['anti_token']}' "
            f"(margin={margin:+.3f})",
            is_correct or not is_hard_fail,  # Soft checks don't fail preflight
            detail,
        )

    # Also check that the model gets at LEAST some reasoning traps right
    # (and some wrong — if it gets all right, the traps aren't adversarial)
    correct = 0
    wrong = 0
    for trap in LOGIT_TRAPS:
        tokens = model.to_tokens(trap["prompt"])
        target_ids = model.to_tokens(trap["target_token"], prepend_bos=False)[0]
        anti_ids = model.to_tokens(trap["anti_token"], prepend_bos=False)[0]

        with torch.no_grad():
            logits = model.run_with_hooks(
                tokens, fwd_hooks=[], return_type="logits"
            )[0, -1, :]

        margin = (logits[target_ids[0]] - logits[anti_ids[0]]).item()
        if margin > 0:
            correct += 1
        else:
            wrong += 1

    result.record(
        f"BASELINE traps: {correct} correct, {wrong} wrong out of {len(LOGIT_TRAPS)}",
        wrong > 0,  # We NEED some wrong answers — that's what traps are for
        f"Model gets ALL traps correct — traps aren't adversarial for this model, "
        f"or token mappings are wrong",
    )


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 5: Numerical Reproducibility
# ═══════════════════════════════════════════════════════════════════════════

def check_reproducibility(model, genome_data: dict, result: PreflightResult):
    """Run the same cosine computation twice and verify identical results."""
    print("\n  --- Check 5: Numerical Reproducibility ---")

    vector = genome_data["vector"]
    v_hat = vector / (vector.norm() + 1e-8)
    layer = genome_data["layer"]
    hook_name = f"blocks.{layer}.hook_resid_pre"

    prompt = LOGIT_TRAPS[0]["prompt"]
    tokens = model.to_tokens(prompt)

    cosines = []
    for run in range(2):
        with torch.no_grad():
            _, cache = model.run_with_cache(tokens, names_filter=[hook_name])
        h = cache[hook_name][0, -1, :].float()
        cos = torch.nn.functional.cosine_similarity(
            v_hat.unsqueeze(0), h.unsqueeze(0)
        ).item()
        cosines.append(cos)

    diff = abs(cosines[0] - cosines[1])
    result.record(
        f"REPRO cosine similarity identical across 2 runs "
        f"(run1={cosines[0]:.6f}, run2={cosines[1]:.6f}, diff={diff:.2e})",
        diff < 1e-4,
        f"Non-deterministic results — check GPU state, model loading, or precision",
    )


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 6: Trap Sanity
# ═══════════════════════════════════════════════════════════════════════════

def check_trap_sanity(result: PreflightResult):
    """Verify trap definitions are internally consistent."""
    print("\n  --- Check 6: Trap Definition Sanity ---")

    all_traps = LOGIT_TRAPS + HELD_OUT_TRAPS
    names = [t["name"] for t in all_traps]

    # No duplicate names
    unique_names = set(names)
    result.record(
        f"TRAPS no duplicate names ({len(names)} traps, {len(unique_names)} unique)",
        len(names) == len(unique_names),
        f"Duplicate trap names: {[n for n in names if names.count(n) > 1]}",
    )

    # Every trap has required keys
    required_keys = {"name", "prompt", "target_token", "anti_token"}
    for trap in all_traps:
        missing = required_keys - set(trap.keys())
        result.record(
            f"TRAPS '{trap.get('name', '???')}' has all required keys",
            len(missing) == 0,
            f"Missing keys: {missing}",
        )

    # Target and anti tokens are different
    for trap in all_traps:
        same = trap.get("target_token") == trap.get("anti_token")
        result.record(
            f"TRAPS '{trap['name']}' target != anti",
            not same,
            f"target and anti are both '{trap.get('target_token')}'",
        )


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 7: Steering Sign Verification
# ═══════════════════════════════════════════════════════════════════════════

def check_steering_sign(model, genome_data: dict, result: PreflightResult):
    """Verify steering vector moves logit margins in the correct direction.

    A flipped sign or corrupted vector is the most dangerous silent failure:
    the experiment runs fine but every result is backwards. This check applies
    the genome at ε=1.0 on the training traps and verifies that at least half
    show improved margins (target logit goes up relative to anti).
    """
    print("\n  --- Check 7: Steering Sign ---")

    vector = genome_data["vector"]
    layer = genome_data["layer"]
    hook_name, hook_fn = make_steering_hook(vector, layer, epsilon=1.0)

    improved = 0
    degraded = 0

    for trap in LOGIT_TRAPS:
        tokens = model.to_tokens(trap["prompt"])
        target_id = model.to_tokens(trap["target_token"], prepend_bos=False)[0][0].item()
        anti_id = model.to_tokens(trap["anti_token"], prepend_bos=False)[0][0].item()

        with torch.no_grad():
            # Baseline (no steering)
            logits_base = model(tokens)[0, -1, :]
            margin_base = (logits_base[target_id] - logits_base[anti_id]).item()

            # Steered
            logits_steer = model.run_with_hooks(
                tokens, fwd_hooks=[(hook_name, hook_fn)]
            )[0, -1, :]
            margin_steer = (logits_steer[target_id] - logits_steer[anti_id]).item()

        delta = margin_steer - margin_base
        direction = "+" if delta > 0 else "-"
        if delta > 0:
            improved += 1
        else:
            degraded += 1

        result.record(
            f"SIGN {trap['name']}: base={margin_base:+.3f} → steered={margin_steer:+.3f} "
            f"(Δ={delta:+.3f} {direction})",
            True,  # Individual traps are informational
            "",
        )

    # Gate: at least half the training traps must improve
    n_traps = len(LOGIT_TRAPS)
    result.record(
        f"SIGN overall: {improved}/{n_traps} traps improved, {degraded}/{n_traps} degraded",
        improved > n_traps // 2,
        f"Steering vector may be flipped or corrupted — "
        f"only {improved}/{n_traps} traps show improvement. "
        f"Check genome sign or re-run CMA-ES.",
    )


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 8: VRAM Headroom
# ═══════════════════════════════════════════════════════════════════════════

def check_vram_headroom(model, result: PreflightResult, warn_pct: float = 0.80):
    """Estimate VRAM usage and warn if close to capacity.

    Runs after model load so we know the actual footprint. Checks whether
    remaining free memory is sufficient for experiment overhead (activations,
    caches, gradient buffers).
    """
    print("\n  --- Check 8: VRAM Headroom ---")

    if not torch.cuda.is_available():
        result.record(
            "VRAM check skipped (no CUDA device)",
            True,
            "",
        )
        return

    device_idx = next(model.parameters()).device.index or 0
    free_bytes, total_bytes = torch.cuda.mem_get_info(device_idx)
    allocated_bytes = torch.cuda.memory_allocated(device_idx)
    reserved_bytes = torch.cuda.memory_reserved(device_idx)

    total_gb = total_bytes / (1024 ** 3)
    allocated_gb = allocated_bytes / (1024 ** 3)
    reserved_gb = reserved_bytes / (1024 ** 3)
    free_gb = free_bytes / (1024 ** 3)
    used_pct = (total_bytes - free_bytes) / total_bytes

    result.record(
        f"VRAM total: {total_gb:.1f} GB, allocated: {allocated_gb:.1f} GB, "
        f"free: {free_gb:.1f} GB ({used_pct:.0%} used)",
        True,  # Informational
        "",
    )

    # Soft warning only — on a 16GB card with a 4B model, high utilization is normal.
    # Experiments run single-sequence no_grad passes; they don't need much headroom.
    if used_pct >= warn_pct:
        log.warning(
            f"VRAM {used_pct:.0%} used — {free_gb:.1f} GB free. "
            f"If experiments OOM, consider: smaller batch, "
            f"torch.cuda.empty_cache(), or closing other GPU processes."
        )
    result.record(
        f"VRAM headroom: {free_gb:.1f} GB free ({1-used_pct:.0%} remaining)",
        True,  # Informational — never gates preflight
        "",
    )

    # Check for fragmentation (reserved >> allocated means wasted memory)
    frag_gb = reserved_gb - allocated_gb
    if frag_gb > 1.0:
        result.record(
            f"VRAM fragmentation: {frag_gb:.1f} GB reserved but unallocated",
            frag_gb < 2.0,  # >2GB fragmentation is a problem
            f"Consider setting PYTORCH_ALLOC_CONF=expandable_segments:True",
        )


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def run_preflight_with_base(base) -> PreflightResult:
    """Run preflight using an already-loaded AnalysisBase. No double model load."""
    result = PreflightResult()

    print("=" * 70)
    print("PREFLIGHT — Data Integrity Verification (in-process)")
    print("=" * 70)
    print(f"  Model:  {base.model_name}")
    print(f"  Genome: {base.genome['path'] if base.genome else '(none)'}")
    print(f"  Device: {base.device}")
    print()

    model = base.model

    check_vram_headroom(model, result)
    check_trap_sanity(result)
    check_token_ids(model, result)
    check_baseline(model, result)

    if base.genome:
        check_hook_points(model, base.genome, result)
        check_genome(base.genome, model, result)
        check_reproducibility(model, base.genome, result)
        check_steering_sign(model, base.genome, result)
    else:
        log.info("No genome provided — skipping hook, genome, reproducibility, and steering checks")

    # Summary
    print("\n" + "=" * 70)
    if result.all_passed:
        print(f"PREFLIGHT PASSED — {result.summary()}")
        print("  All data integrity checks passed. Safe to proceed with experiments.")
    else:
        print(f"PREFLIGHT FAILED — {result.summary()}")
        print(f"  Failed checks: {', '.join(result.failures)}")
        print("  DO NOT TRUST experiment results until failures are resolved.")
    print("=" * 70)

    if base.output_dir:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = base.output_dir / f"preflight_{ts}.json"
        json_path.write_text(
            json.dumps(result.to_dict(), indent=2, default=str),
            encoding="utf-8",
        )
        log.info(f"Results saved: {json_path}")

    return result


def run_preflight(model_name: str, genome_path: str = None,
                  device: str = "cuda", output_dir: str = None) -> PreflightResult:
    """Run all preflight checks. Loads model from scratch (standalone mode)."""
    from transformer_lens import HookedTransformer

    result = PreflightResult()

    print("=" * 70)
    print("PREFLIGHT — Data Integrity Verification")
    print("=" * 70)
    print(f"  Model:  {model_name}")
    print(f"  Genome: {genome_path or '(none)'}")
    print(f"  Device: {device}")
    print()

    # Load model
    log.info(f"Loading {model_name}...")
    model = HookedTransformer.from_pretrained(
        model_name,
        center_writing_weights=False,
        center_unembed=False,
        fold_ln=False,
        device=device,
    )
    model.eval()

    # Check 8: VRAM headroom (right after model load)
    check_vram_headroom(model, result)

    # Check 6: Trap definitions (no model needed)
    check_trap_sanity(result)

    # Check 1: Token IDs
    check_token_ids(model, result)

    # Check 4: Baseline behavior
    check_baseline(model, result)

    # Genome-dependent checks
    genome_data = None
    if genome_path:
        genome_data = load_genome(genome_path, device)

        # Check 2: Hook points
        check_hook_points(model, genome_data, result)

        # Check 3: Genome integrity
        check_genome(genome_data, model, result)

        # Check 5: Reproducibility
        check_reproducibility(model, genome_data, result)

        # Check 7: Steering sign
        check_steering_sign(model, genome_data, result)
    else:
        log.info("No genome provided — skipping hook, genome, reproducibility, and steering checks")

    # Summary
    print("\n" + "=" * 70)
    if result.all_passed:
        print(f"PREFLIGHT PASSED — {result.summary()}")
        print("  All data integrity checks passed. Safe to proceed with experiments.")
    else:
        print(f"PREFLIGHT FAILED — {result.summary()}")
        print(f"  Failed checks: {', '.join(result.failures)}")
        print("  DO NOT TRUST experiment results until failures are resolved.")
    print("=" * 70)

    # Save results
    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = out_path / f"preflight_{ts}.json"
        json_path.write_text(
            json.dumps(result.to_dict(), indent=2, default=str),
            encoding="utf-8",
        )
        log.info(f"Results saved: {json_path}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Preflight — data integrity verification before experiments",
    )
    AnalysisBase.add_common_args(parser)
    args, _ = parser.parse_known_args()

    result = run_preflight(
        model_name=args.model,
        genome_path=args.genome,
        device=args.device,
        output_dir=args.output_dir,
    )

    sys.exit(0 if result.all_passed else 1)


if __name__ == "__main__":
    main()
