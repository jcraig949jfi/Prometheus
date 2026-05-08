"""Substrate-Tester Fire #36 harness — Lane 11 (batch-sweep, 4th seed)
+ Lane 16 (concurrency-stress smoke, first my-instance run).

Coordination: my fire #35 was last; no new parallel.

Lane 11 — 4th seed-confirmation of the architectural-impedance finding
from fires #8, #13, #32. With ~120 cumulative ingest-OK probes across
4 distinct seeds, the finding should be definitively seed-stable.

Lane 16 — concurrency-stress smoke via pytest on the existing harness
at prometheus_math/tests/test_concurrency_stress.py. Fire #12 (parallel)
+ #24 (parallel) covered it; never my-instance. Quick verification.

Outputs:
  charon/diagnostics/substrate_tester_fire_36_results.json
"""
from __future__ import annotations

import json
import os
import random
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 11 — batch-sweep, 4th seed
# ---------------------------------------------------------------------------


CORPORA = [
    REPO / "aporia/meta/pressure_appliers/corpora/harmonia_b_dynamics_v1.json",
    REPO / "aporia/meta/pressure_appliers/corpora/harmonia_d_logic_v1.json",
    REPO / "aporia/meta/pressure_appliers/corpora/harmonia_e_complexity_v1.json",
]


def load_corpora():
    out = []
    for path in CORPORA:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
            out.append((path.name, d))
    return out


def sample_probes(rng, corpora, n_adv=15, n_rp=15):
    all_adv, all_rp = [], []
    for cid, d in corpora:
        for p in d.get("adversarial", []):
            all_adv.append((cid, p))
        for p in d.get("real_paper", []):
            all_rp.append((cid, p))
    rng.shuffle(all_adv); rng.shuffle(all_rp)
    return all_adv[:n_adv], all_rp[:n_rp]


def submit_probe(kernel, kind: str, corpus_id: str, probe: dict) -> dict:
    from sigma_kernel.sigma_kernel import Tier
    pid = probe.get("id", "unknown")
    if kind == "adversarial":
        hypothesis = probe.get("probe", "")[:500]
        evidence = {"use_case": "adversarial", "domain": probe.get("domain", "")}
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
        }
        kill_path = f"expected_{probe.get('expected_substrate_verdict', 'UNKNOWN')}"
        expected = probe.get("expected_substrate_verdict", "UNKNOWN")
    try:
        claim = kernel.CLAIM(
            target_name=f"{kind}__{pid}_fire36",
            hypothesis=hypothesis,
            evidence=evidence,
            kill_path=kill_path,
            target_tier=Tier.Conjecture,
        )
        return {
            "probe_id": pid, "kind": kind, "corpus": corpus_id,
            "expected": expected, "submitted_ok": True,
            "claim_id": claim.id,
        }
    except Exception as e:  # noqa: BLE001
        return {
            "probe_id": pid, "kind": kind, "corpus": corpus_id,
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
    sampled_first = results[0]["probe_id"] if results else None

    return {
        "lane": "11_batch_sweep_fourth_seed",
        "seed": seed,
        "n_corpora_loaded": len(corpora),
        "n_submissions": len(results),
        "n_submitted_ok": n_ok,
        "n_submission_failed": n_fail,
        "first_probe_id": sampled_first,
    }


# ---------------------------------------------------------------------------
# Lane 16 — concurrency-stress smoke
# ---------------------------------------------------------------------------


def lane_16_concurrency_smoke() -> Dict[str, Any]:
    test_path = REPO / "prometheus_math" / "tests" / "test_concurrency_stress.py"
    if not test_path.exists():
        return {
            "lane": "16_concurrency_stress",
            "status": "DORMANT",
            "reason": f"test missing at {test_path}",
        }
    t0 = time.time()
    proc = subprocess.run(
        [
            "python", "-m", "pytest", str(test_path),
            "-q", "--tb=short",
        ],
        cwd=str(REPO), capture_output=True, text=True, timeout=300,
        env={"PYTHONPATH": str(REPO), **os.environ},
    )
    elapsed = time.time() - t0
    rc = proc.returncode
    stdout = proc.stdout

    summary_line = ""
    n_passed = n_failed = 0
    for line in stdout.splitlines():
        if "passed" in line or "failed" in line:
            if " in " in line:
                summary_line = line.strip()
            tokens = line.replace(",", "").split()
            for i, tok in enumerate(tokens):
                if tok == "passed" and i > 0:
                    try: n_passed = int(tokens[i - 1])
                    except (ValueError, IndexError): pass
                if tok == "failed" and i > 0:
                    try: n_failed = int(tokens[i - 1])
                    except (ValueError, IndexError): pass
    verdict = "PASS" if (rc == 0 and n_failed == 0 and n_passed > 0) else "FAIL"
    return {
        "lane": "16_concurrency_stress",
        "status": "LIVE",
        "wall_clock_seconds": elapsed,
        "rc": rc,
        "n_passed": n_passed,
        "n_failed": n_failed,
        "summary_line": summary_line,
        "verdict": verdict,
        "stdout_tail": stdout[-1000:] if rc != 0 else "",
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    SEED = 20260508_03
    summary = {
        "fire": 36,
        "lanes": [11, 16],
        "lane_11": lane_11_batch_sweep(SEED),
        "lane_16": lane_16_concurrency_smoke(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_36_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    l11 = summary["lane_11"]
    print(f"Lane 11: ok={l11['n_submitted_ok']}/{l11['n_submissions']}, first_probe={l11['first_probe_id']}")
    l16 = summary["lane_16"]
    print(f"Lane 16: verdict={l16.get('verdict')}, passed={l16.get('n_passed')}, failed={l16.get('n_failed')}, wall_clock={l16.get('wall_clock_seconds', 0):.1f}s")
    return summary


if __name__ == "__main__":
    run()
