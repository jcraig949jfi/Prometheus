"""Substrate-Tester Fire #32 harness — Lane 11 (batch-sweep with fresh
seed, my-instance overdue since fire #13) + Lane 4 (T-ST003 4th regression
confirmation).

Coordination: my fire #31 was last (commit 453efc4b). No new parallel.
P0 + P1-escalation tickets all still OPEN.

Lane 11: 30 probes from Harmonia corpora with fresh seed; tracks
architectural-impedance finding (3rd seed-confirmation of fires #8 + #13).

Lane 4: 4th post-restart confirmation of T-ST003 fix (silent sentinel
→ KeyError). Fires #3, #10, #19 confirmed; #32 = #4 confirmation.

Outputs:
  charon/diagnostics/substrate_tester_fire_32_results.json
"""
from __future__ import annotations

import json
import random
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 11 — batch-sweep
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
            target_name=f"{kind}__{pid}_fire32",
            hypothesis=hypothesis,
            evidence=evidence,
            kill_path=kill_path,
            target_tier=Tier.Conjecture,
        )
        return {
            "probe_id": pid, "kind": kind, "corpus": corpus_id,
            "expected": expected, "submitted_ok": True,
            "claim_id": claim.id, "claim_status": claim.status,
            "verdict": str(claim.verdict) if claim.verdict else None,
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
    n_with_verdict = sum(
        1 for r in results
        if r.get("submitted_ok") and r.get("verdict") is not None
    )
    sampled_first = results[0]["probe_id"] if results else None

    return {
        "lane": "11_batch_sweep_third_seed",
        "seed": seed,
        "n_corpora_loaded": len(corpora),
        "n_submissions": len(results),
        "n_submitted_ok": n_ok,
        "n_submission_failed": n_fail,
        "n_with_verdict": n_with_verdict,
        "first_probe_id": sampled_first,
    }


# ---------------------------------------------------------------------------
# Lane 4 — T-ST003 4th regression
# ---------------------------------------------------------------------------


def lane_4_st003_fourth_regression() -> Dict[str, Any]:
    from prometheus_math.learner_corpus import get_raw_invariant_keys

    tests: List[Dict[str, Any]] = []

    # T1: unknown domain MUST raise KeyError
    try:
        keys = get_raw_invariant_keys("nonexistent_xyz_fire32")
        tests.append({
            "id": "T1_unknown_domain_raises",
            "expected": "KeyError raised (T-ST003 fix)",
            "actual": f"silently returned {keys} — REGRESSION",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })
    except KeyError as exc:
        tests.append({
            "id": "T1_unknown_domain_raises",
            "expected": "KeyError",
            "actual": f"KeyError: {str(exc)[:140]}",
            "verdict": "PASS",
            "note": "T-ST003 fix sticks across 4 regression checks (fires #3, #10, #19, #32)",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T1_unknown_domain_raises",
            "expected": "KeyError",
            "actual": f"raised wrong: {type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P2-normal",
        })

    # T2: registered domains still work
    for domain in ("lehmer", "bsd_rank"):
        try:
            keys = get_raw_invariant_keys(domain)
            if isinstance(keys, tuple) and len(keys) > 0:
                tests.append({
                    "id": f"T2_{domain}_registered",
                    "expected": f"{domain} returns key tuple",
                    "actual": f"{len(keys)} keys",
                    "verdict": "PASS",
                })
            else:
                tests.append({
                    "id": f"T2_{domain}_registered",
                    "expected": f"{domain} returns valid keys",
                    "actual": f"suspicious: {keys}",
                    "verdict": "FAIL",
                    "severity": "P0-blocker",
                })
        except Exception as exc:  # noqa: BLE001
            tests.append({
                "id": f"T2_{domain}_registered",
                "expected": f"{domain} returns valid keys",
                "actual": f"raised: {type(exc).__name__}",
                "verdict": "FAIL",
                "severity": "P0-blocker",
            })

    return {
        "lane": "4_st003_fourth_regression",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    SEED = 20260508_01  # fire-32 seed
    summary = {
        "fire": 32,
        "lanes": [11, 4],
        "lane_11": lane_11_batch_sweep(SEED),
        "lane_4": lane_4_st003_fourth_regression(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_32_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    l11 = summary["lane_11"]
    print(f"Lane 11: ok={l11['n_submitted_ok']}/{l11['n_submissions']}, "
          f"with_verdict={l11['n_with_verdict']}, first_probe={l11['first_probe_id']}")
    print(f"Lane 4: {summary['lane_4']['verdict_counts']}")
    return summary


if __name__ == "__main__":
    run()
