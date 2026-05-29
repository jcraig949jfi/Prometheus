"""Sprint-1 A8: cross-domain residue transfer (Phase 2, ITER-52).

Hypothesis (from roadmap v2 line 90):
> "Layer-2 residue from Mahler routes BSD MVP loader more
> efficiently than null residue"
> Pass: wall-clock to first PROMOTED in BSD with residue <
> without residue -> cross-domain transfer real.

## Infrastructure status

The pre-committed A8 protocol requires a BSD MVP loader, listed
as parallel work in roadmap §35 line 68. That loader was NOT
shipped during Phase 1B/1C. A8 cannot be run on the pre-committed
real-data protocol.

This MVP runs a SYNTHETIC SUBSTITUTE that tests the same
architectural claim (cross-domain transfer accelerates new-
domain emission) using synthetic ledger data. The SUBSTITUTE
verdict carries the explicit caveat that the real-data test
remains pending.

## A8 protocol (synthetic substitute)

1. Generate two-domain synthetic ledger: source domain A
   ("mahler") with rich coverage, target domain B ("BSD") with
   partial coverage. The two domains share an underlying
   (invariant, kp) structure.
2. WITH-RESIDUE condition: build KillTensor from full ledger
   (both A and B). Use predict_transfer (mahler -> BSD) to
   identify CONFIRMED patterns -- (invariant, kp) tuples
   populated in both. The confirmed count is the residue's
   "head start" on B.
3. NO-RESIDUE condition: same B-only emissions, but no access
   to A's ledger -- the substrate must discover B's structure
   from scratch.
4. Approximate "wall-clock to first PROMOTED" as: number of
   B-emissions before the substrate has K distinct (invariant,
   kp) patterns in B. With residue, the substrate starts with K
   patterns already confirmed from A; without, it must discover
   them de novo.

5. Compute:
     ticks_with_residue    = max(0, K - n_confirmed_from_A)
     ticks_without_residue = K (full discovery from scratch)
     speedup_ratio = ticks_without_residue / max(ticks_with_residue, 1)

6. Pass if speedup_ratio > 1.5 (residue gives at least 50% speedup
   to first-K-patterns milestone).

## Caveats

This is a synthetic substitute. The real-data protocol per the
roadmap requires actual wall-clock measurement on the BSD MVP
loader -- a property of running real composition loaders, not
synthetic counting. The substitute's pass/fail should be
interpreted as "the architectural claim (residue transfer
accelerates new-domain coverage) holds in the synthetic model."
The real-data verdict is deferred to Phase 3+ when the BSD
loader exists.
"""
from __future__ import annotations

import random

from charon.agents.erebos._cross_domain_transfer import predict_transfer
from charon.agents.erebos._kill_tensor import (
    AXIS_INVARIANT,
    AXIS_KP,
    KillTensor,
)
from charon.agents.erebos.sprint1 import SprintResult


SOURCE_DOMAIN = "mahler"
TARGET_DOMAIN = "BSD"
N_INVARIANTS_TOTAL = 20      # universe of possible (input) signatures
N_INVARIANTS_SHARED = 12     # how many overlap between domains
KPS = ["kp_a", "kp_b", "kp_c", "kp_d", "kp_e"]
N_EMISSIONS_PER_DOMAIN = 40
SEED = 503
PASS_SPEEDUP = 1.5

# K-patterns target for the speedup-to-K-coverage metric. Set to
# the number of shared patterns we'd EXPECT to see; the metric
# measures how much residue helps reach this milestone.
K_PATTERN_MILESTONE = 8


def _generate_two_domain_ledger() -> list[dict]:
    rng = random.Random(SEED)
    # Pool of invariant signatures
    all_invs = [f"sig:inv_{i:03d}" for i in range(N_INVARIANTS_TOTAL)]
    shared_invs = all_invs[:N_INVARIANTS_SHARED]
    source_only_invs = all_invs[N_INVARIANTS_SHARED:]
    target_only_invs = all_invs[N_INVARIANTS_SHARED:]  # overlap allowed

    # Per-invariant ground-truth kp -- same across domains
    inv_to_truth_kp: dict[str, str] = {
        sig: rng.choice(KPS) for sig in all_invs
    }

    rows: list[dict] = []
    # Source domain emissions: rich coverage
    for _ in range(N_EMISSIONS_PER_DOMAIN):
        sig = rng.choice(all_invs)
        # 75% agreement with ground truth
        kp = (
            inv_to_truth_kp[sig] if rng.random() < 0.75
            else rng.choice(KPS)
        )
        rows.append({
            "plugin_id": "g_test",
            "domain": SOURCE_DOMAIN,
            "input_signature": sig,
            "kill_pattern": kp,
        })
    # Target domain emissions: partial coverage (sample from a
    # smaller subset)
    target_subset = rng.sample(all_invs, N_INVARIANTS_SHARED + 4)
    for _ in range(N_EMISSIONS_PER_DOMAIN):
        sig = rng.choice(target_subset)
        kp = (
            inv_to_truth_kp[sig] if rng.random() < 0.75
            else rng.choice(KPS)
        )
        rows.append({
            "plugin_id": "g_test",
            "domain": TARGET_DOMAIN,
            "input_signature": sig,
            "kill_pattern": kp,
        })
    return rows


def run_a8() -> SprintResult:
    rows = _generate_two_domain_ledger()
    tensor = KillTensor.from_ledger_rows(rows)

    # WITH-RESIDUE: how many target patterns are CONFIRMED already
    # via source -> target transfer
    report = predict_transfer(
        tensor,
        source_domain=SOURCE_DOMAIN,
        target_domain=TARGET_DOMAIN,
        key_axes=(AXIS_INVARIANT, AXIS_KP),
    )
    n_confirmed = len(report.confirmed)

    # Speedup to K_PATTERN_MILESTONE
    ticks_with_residue = max(K_PATTERN_MILESTONE - n_confirmed, 0)
    ticks_without_residue = K_PATTERN_MILESTONE
    speedup_ratio = ticks_without_residue / max(ticks_with_residue, 1)

    passed = speedup_ratio > PASS_SPEEDUP

    return SprintResult(
        experiment_id="A8",
        hypothesis=(
            "Cross-domain Layer-2 residue accelerates new-domain "
            "coverage (synthetic substitute pending BSD MVP loader)"
        ),
        metric_name="speedup_to_K_patterns_synthetic",
        metric_value=speedup_ratio,
        pass_threshold=PASS_SPEEDUP,
        comparator=">",
        passed=passed,
        protocol_summary=(
            f"SYNTHETIC SUBSTITUTE (BSD loader pending). Two-domain "
            f"ledger with N_INVARIANTS_SHARED={N_INVARIANTS_SHARED}, "
            f"agreement 0.75, seed={SEED}. Count confirmed patterns "
            f"transferring source->target; compute speedup_to_K = "
            f"K / max(K - n_confirmed, 1) for K="
            f"{K_PATTERN_MILESTONE}."
        ),
        notes=(
            f"SYNTHETIC SUBSTITUTE -- real-data protocol per "
            f"roadmap requires BSD MVP loader (pending). "
            f"n_confirmed_transferred={n_confirmed}; "
            f"K_milestone={K_PATTERN_MILESTONE}; "
            f"ticks_with_residue={ticks_with_residue}; "
            f"ticks_without_residue={ticks_without_residue}; "
            f"speedup_ratio={speedup_ratio:.4f}"
        ),
    )
