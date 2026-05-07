"""Substrate-Tester Fire #13 harness — Lane 11 (batch-sweep, fresh seed)
+ Lane 13 (canonicalization-fuzz, fresh seed).

Coordination note: fire #12 (commit 2ec06acc, parallel instance) covered
lanes 14 + 16. Per fire #12 standing rec for #13:
  - Lane 11 overdue (every-other-fire cadence; last fire #8)
  - Lane 13 expand Hypothesis coverage with new seed

Lane 11 expectation: same architectural-impedance finding as fire #8
(30/30 ingest, 0/30 verdict). Confirms finding is stable across seeds;
also exercises ingestion-discipline regression check.

Lane 13: pytest the canonicalization fuzzer with --hypothesis-seed=
20260507_15 (different from fire #7's 20260507 and fire #10's 20260507).
Hypothesis explores deeper with the fresh seed.

Outputs:
  charon/diagnostics/substrate_tester_fire_13_results.json
"""
from __future__ import annotations

import json
import random
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 11 — batch-sweep with fresh seed
# ---------------------------------------------------------------------------


CORPORA = [
    REPO / "aporia/meta/pressure_appliers/corpora/harmonia_b_dynamics_v1.json",
    REPO / "aporia/meta/pressure_appliers/corpora/harmonia_d_logic_v1.json",
    REPO / "aporia/meta/pressure_appliers/corpora/harmonia_e_complexity_v1.json",
]


def load_corpora() -> List[Tuple[str, dict]]:
    out = []
    for path in CORPORA:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        out.append((path.name, d))
    return out


def sample_probes(rng: random.Random, corpora, n_adv: int = 15, n_rp: int = 15):
    all_adv = []
    all_rp = []
    for cid, d in corpora:
        for p in d.get("adversarial", []):
            all_adv.append((cid, p))
        for p in d.get("real_paper", []):
            all_rp.append((cid, p))
    rng.shuffle(all_adv)
    rng.shuffle(all_rp)
    return all_adv[:n_adv], all_rp[:n_rp]


def submit_probe(kernel, probe_kind: str, corpus_id: str, probe: dict) -> dict:
    from sigma_kernel.sigma_kernel import Tier
    pid = probe.get("id", "unknown")
    target_name = f"{probe_kind}__{pid}_fire13"
    if probe_kind == "adversarial":
        hypothesis = probe.get("probe", "")[:500]
        evidence = {
            "use_case": "adversarial",
            "expected_answer": probe.get("expected_answer", "")[:200],
            "trap_pattern": probe.get("trap_pattern", "")[:200],
            "domain": probe.get("domain", ""),
            "subdomain": probe.get("subdomain", ""),
        }
        kill_path = "expected_REFUSAL"
        expected = "REFUSAL"
    else:
        cps = probe.get("claim_payload_for_substrate", {})
        hypothesis = (
            f"{cps.get('subject', '')} :: {cps.get('predicate', '')}"
        )[:500]
        evidence = {
            "use_case": "real-paper",
            "claim_type": cps.get("claim_type", ""),
            "verification_anchor": cps.get("verification_anchor", "")[:200],
            "arxiv_id": probe.get("arxiv_id", ""),
            "category": probe.get("category", ""),
            "domain": probe.get("domain", ""),
        }
        kill_path = f"expected_{probe.get('expected_substrate_verdict', 'UNKNOWN')}"
        expected = probe.get("expected_substrate_verdict", "UNKNOWN")
    try:
        claim = kernel.CLAIM(
            target_name=target_name,
            hypothesis=hypothesis,
            evidence=evidence,
            kill_path=kill_path,
            target_tier=Tier.Conjecture,
        )
        return {
            "probe_id": pid, "kind": probe_kind, "corpus": corpus_id,
            "expected": expected, "submitted_ok": True,
            "claim_id": claim.id, "claim_status": claim.status,
            "verdict": str(claim.verdict) if claim.verdict else None,
        }
    except Exception as e:  # noqa: BLE001
        return {
            "probe_id": pid, "kind": probe_kind, "corpus": corpus_id,
            "expected": expected, "submitted_ok": False,
            "error_type": type(e).__name__,
            "error_message": str(e)[:200],
        }


def lane_11_batch_sweep(seed: int) -> Dict[str, Any]:
    from sigma_kernel.sigma_kernel import SigmaKernel

    rng = random.Random(seed)
    corpora = load_corpora()
    adv, rp = sample_probes(rng, corpora)

    kernel = SigmaKernel(":memory:")
    results = []
    for cid, p in adv:
        results.append(submit_probe(kernel, "adversarial", cid, p))
    for cid, p in rp:
        results.append(submit_probe(kernel, "real-paper", cid, p))

    n_ok = sum(1 for r in results if r["submitted_ok"])
    n_fail = sum(1 for r in results if not r["submitted_ok"])
    n_with_verdict = sum(
        1 for r in results
        if r.get("submitted_ok") and r.get("verdict") is not None
    )
    # Sample probe ids to verify seed-driven sampling diverges from fire #8
    fire_8_seed_2026050712_first_adv = "harmonia_b_adv_010"
    sampled_adv_ids = [r["probe_id"] for r in results if r["kind"] == "adversarial"]
    seed_diverged = (
        fire_8_seed_2026050712_first_adv not in sampled_adv_ids
        or sampled_adv_ids[0] != fire_8_seed_2026050712_first_adv
    )

    return {
        "lane": "11_batch_sweep_fresh_seed",
        "seed": seed,
        "n_submissions": len(results),
        "n_submitted_ok": n_ok,
        "n_submission_failed": n_fail,
        "n_with_verdict": n_with_verdict,
        "first_adv_probe_id": sampled_adv_ids[0] if sampled_adv_ids else None,
        "seed_diverged_from_fire_8": seed_diverged,
        "results": results,
    }


# ---------------------------------------------------------------------------
# Lane 13 — canonicalization-fuzz with fresh Hypothesis seed
# ---------------------------------------------------------------------------


def lane_13_canon_fuzz(seed: str) -> Dict[str, Any]:
    fuzz_test_path = REPO / "prometheus_math" / "tests" / "test_canonicalization_fuzz.py"
    if not fuzz_test_path.exists():
        return {
            "lane": "13_canon_fuzz",
            "status": "DORMANT",
            "reason": f"fuzz test missing at {fuzz_test_path}",
            "tests": [],
        }
    t0 = time.time()
    proc = subprocess.run(
        [
            "python", "-m", "pytest", str(fuzz_test_path),
            f"--hypothesis-seed={seed}",
            "-q", "--tb=short",
        ],
        cwd=str(REPO), capture_output=True, text=True, timeout=300,
        env={"PYTHONPATH": str(REPO), **__import__("os").environ},
    )
    elapsed = time.time() - t0
    rc = proc.returncode
    stdout = proc.stdout
    summary_line = ""
    for line in stdout.splitlines():
        if ("passed" in line or "failed" in line) and " in " in line:
            summary_line = line.strip()
    n_passed = stdout.count("PASSED") if "PASSED" in stdout else None
    if n_passed is None:
        # quiet mode: count dots
        for line in stdout.splitlines():
            if "passed" in line and "in" in line:
                # parse "N passed in TIME"
                tokens = line.replace(",", "").split()
                for i, tok in enumerate(tokens):
                    if tok == "passed" and i > 0:
                        try:
                            n_passed = int(tokens[i - 1])
                        except (ValueError, IndexError):
                            pass
    n_failed = 0
    for line in stdout.splitlines():
        if "failed" in line and " in " in line:
            tokens = line.replace(",", "").split()
            for i, tok in enumerate(tokens):
                if tok == "failed" and i > 0:
                    try:
                        n_failed = int(tokens[i - 1])
                    except (ValueError, IndexError):
                        pass
    if rc == 0 and (n_failed or 0) == 0:
        verdict = "PASS"
        severity = None
    else:
        verdict = "FAIL"
        severity = "P1-high"
    return {
        "lane": "13_canon_fuzz",
        "status": "LIVE",
        "hypothesis_seed": seed,
        "wall_clock_seconds": elapsed,
        "rc": rc,
        "n_passed": n_passed,
        "n_failed": n_failed,
        "summary_line": summary_line,
        "verdict": verdict,
        "severity": severity,
        "stdout_tail": stdout[-1500:] if rc != 0 else "",
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    SEED = 20260507_15  # fire-13 timestamp-derived
    summary = {
        "fire": 13,
        "lanes": [11, 13],
        "seed": SEED,
        "lane_11": lane_11_batch_sweep(SEED),
        "lane_13": lane_13_canon_fuzz(str(SEED)),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_13_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 11: ok={summary['lane_11']['n_submitted_ok']}, "
          f"with_verdict={summary['lane_11']['n_with_verdict']}, "
          f"seed_diverged={summary['lane_11']['seed_diverged_from_fire_8']}")
    print(f"Lane 13: verdict={summary['lane_13']['verdict']}, "
          f"passed={summary['lane_13']['n_passed']}, "
          f"failed={summary['lane_13']['n_failed']}")
    return summary


if __name__ == "__main__":
    run()
