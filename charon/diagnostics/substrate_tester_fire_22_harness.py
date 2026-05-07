"""
Substrate-Tester Fire #22 — Lane 11 (batch-sweep) + Lane 10 (real-paper).

Coordination: parallel substrate-tester ran fire #21 (commit f23b9438,
Lane 12 + Lane 6 regression). My fire = #22, lanes 11 + 10.

Lane 11: 30 probes from the v2 Harmonia corpora (combinatorics, dynamics,
analysis, logic, complexity) through SigmaKernel.CLAIM. Verify all probes
ingest cleanly. No verdicts expected — substrate has no general-purpose
CLAIM gauntlet for theorem-style claims (architectural reality, not flaw).

Lane 10: 3 RECENT_POLYNOMIAL_CORPUS entries through DiscoveryPipeline.
Picked OUT-OF-BAND Salem-cluster entries (avoiding fire-#14's network-bound
in-band catalog cross-check deadlock). Different entries than fire #5's
selections (entries 1, 2, 3 vs fire #5's 0, 16).

Author: substrate-tester (Charon-aligned), fire #22, 2026-05-07
"""

from __future__ import annotations

import json
import random
import time
from collections import Counter
from pathlib import Path

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 11 — batch-sweep
# ---------------------------------------------------------------------------


def lane_11_batch_sweep() -> dict:
    """Sample ~30 probes uniformly across the v2 Harmonia corpora;
    submit each as a CLAIM via SigmaKernel.CLAIM; verify all ingest cleanly."""
    from sigma_kernel.sigma_kernel import SigmaKernel
    import os

    rng = random.Random(20260507_22)
    corpus_dir = REPO / "aporia" / "meta" / "pressure_appliers" / "corpora_v2"
    corpus_files = sorted(p for p in corpus_dir.glob("harmonia_*.json"))

    probes = []
    for cf in corpus_files:
        try:
            data = json.loads(cf.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"  WARN: failed to load {cf.name}: {exc}")
            continue
        # Find the probe-list key
        probe_list = None
        for k, v in data.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                first = v[0]
                if "id" in first and ("probe" in str(first).lower() or "question" in str(first).lower() or "prompt" in str(first).lower() or "expected" in str(first).lower()):
                    probe_list = v
                    break
        if probe_list is None:
            print(f"  WARN: no probe list in {cf.name}")
            continue

        # Sample 6 from each corpus → 30 total across 5 corpora
        sample_size = min(6, len(probe_list))
        sampled = rng.sample(probe_list, sample_size)
        for p in sampled:
            probes.append({
                "corpus_file": cf.name,
                "probe_id": p.get("id"),
                "domain": p.get("domain"),
                "subdomain": p.get("subdomain"),
                "raw_probe": p,
            })

    # Submit each probe through SigmaKernel.CLAIM
    kernel = SigmaKernel()
    t0 = time.time()
    submitted = []
    errors = []
    for idx, p in enumerate(probes):
        try:
            # Build CLAIM args from probe
            target_name = f"batch_sweep:{p['probe_id']}"
            hypothesis = (
                p["raw_probe"].get("single_part_probe")
                or p["raw_probe"].get("multi_part_probe")
                or p["raw_probe"].get("probe")
                or "<unspecified>"
            )[:500]
            evidence = {
                "domain": p["domain"],
                "subdomain": p.get("subdomain"),
                "expected": p["raw_probe"].get("single_part_expected") or p["raw_probe"].get("expected"),
                "corpus_file": p["corpus_file"],
            }
            kill_path = f"batch_sweep_pending:{p['domain']}"
            claim = kernel.CLAIM(
                target_name=target_name,
                hypothesis=hypothesis,
                evidence=evidence,
                kill_path=kill_path,
            )
            submitted.append({
                "idx": idx,
                "probe_id": p["probe_id"],
                "claim_id": claim.id,
                "domain": p["domain"],
            })
        except Exception as exc:
            errors.append({
                "idx": idx,
                "probe_id": p["probe_id"],
                "error": repr(exc),
            })

    elapsed = time.time() - t0

    tests = []

    # T1: all 30 probes ingest cleanly
    if len(probes) >= 25 and len(errors) == 0:
        tests.append({
            "id": "T1_batch_sweep_clean_ingest",
            "expected": "30 probes ingested via SigmaKernel.CLAIM with no exceptions",
            "actual": f"{len(submitted)}/{len(probes)} submitted, 0 errors, throughput={len(submitted)/elapsed:.1f}/s",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T1_batch_sweep_clean_ingest",
            "expected": "30 probes ingested",
            "actual": f"{len(submitted)} submitted, {len(errors)} errors",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    # T2: domain coverage
    domain_counts = Counter(s["domain"] for s in submitted)
    if len(domain_counts) >= 3:
        tests.append({
            "id": "T2_domain_coverage",
            "expected": "≥3 domains represented",
            "actual": f"{len(domain_counts)} domains: {dict(domain_counts)}",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T2_domain_coverage",
            "expected": "≥3 domains",
            "actual": f"{len(domain_counts)} domains: {dict(domain_counts)}",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    return {
        "lane": "11_batch_sweep",
        "n_probes_sampled": len(probes),
        "n_submitted": len(submitted),
        "n_errors": len(errors),
        "wall_clock_seconds": elapsed,
        "throughput_per_sec": (len(submitted) / elapsed) if elapsed > 0 else 0,
        "domain_counts": dict(domain_counts),
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
        "errors": errors[:5],
    }


# ---------------------------------------------------------------------------
# Lane 10 — real-paper, out-of-band (avoid network)
# ---------------------------------------------------------------------------


def lane_10_real_paper_oob() -> dict:
    """3 RECENT_POLYNOMIAL_CORPUS entries through DiscoveryPipeline.
    Picked entries 1, 2, 3 (Salem cluster, all out-of-band) to:
      (a) cover different polynomials than fire #5 (entries 0 + 16)
      (b) avoid in-band live-catalog network calls (fire-#14 lesson)
    """
    from prometheus_math._arxiv_polynomial_corpus import RECENT_POLYNOMIAL_CORPUS
    from prometheus_math.discovery_pipeline import DiscoveryPipeline
    from sigma_kernel.sigma_kernel import SigmaKernel
    from sigma_kernel.bind_eval_v2 import BindEvalExtension

    cases = []
    for idx in [1, 2, 3]:  # not 0 (fire-#5) nor 16 (fire-#5 in-band)
        e = RECENT_POLYNOMIAL_CORPUS[idx]
        cases.append({
            "idx": idx,
            "shape": "real_arxiv_oob",
            "coeffs": list(e.coeffs),
            "submitted_M": float(e.mahler_measure),
            "paper_arxiv_id": e.paper_arxiv_id,
            "paper_year": e.paper_year,
            "paper_title": e.paper_title[:80],
        })

    kernel = SigmaKernel()
    ext = BindEvalExtension(kernel)
    pipe = DiscoveryPipeline(kernel=kernel, ext=ext)

    results = []
    for c in cases:
        t0 = time.time()
        rec = pipe.process_candidate(coeffs=c["coeffs"], mahler_measure=c["submitted_M"])
        elapsed = time.time() - t0
        results.append({
            **c,
            "elapsed_s": elapsed,
            "terminal_state": rec.terminal_state,
            "kill_pattern": rec.kill_pattern,
            "claim_id": rec.claim_id,
        })

    tests = []
    for r in results:
        kp = r.get("kill_pattern") or ""
        ts = r.get("terminal_state")
        if ts in ("PROMOTED", "SHADOW_CATALOG", "REJECTED") and (kp or ts != "REJECTED"):
            tests.append({
                "id": f"P_{r['idx']}_clean_routing",
                "expected": "deterministic routing with kill_pattern",
                "actual": f"M={r['submitted_M']:.4f}, terminal={ts}, kill_pattern={kp[:80]!r}",
                "verdict": "PASS",
                "severity": None,
            })
        else:
            tests.append({
                "id": f"P_{r['idx']}_clean_routing",
                "expected": "deterministic routing",
                "actual": f"terminal={ts}, kill_pattern={kp[:80]!r}",
                "verdict": "FAIL",
                "severity": "P1-high",
            })

    return {
        "lane": "10_real_paper_oob",
        "n_probes": len(cases),
        "case_results": results,
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main():
    out_dir = REPO / "charon" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== Substrate-Tester Fire #22 ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n--- Lane 11: batch-sweep (Harmonia v2 corpora) ---")
    lane11 = lane_11_batch_sweep()
    print(f"Sampled: {lane11['n_probes_sampled']}, submitted: {lane11['n_submitted']}, errors: {lane11['n_errors']}")
    print(f"  domain_counts: {lane11['domain_counts']}")
    print(f"  Tests: {lane11['n_tests']}, verdicts: {lane11['verdict_counts']}")
    for t in lane11["tests"]:
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    print("\n--- Lane 10: real-paper (out-of-band, entries 1/2/3) ---")
    lane10 = lane_10_real_paper_oob()
    print(f"Tests: {lane10['n_tests']}, verdicts: {lane10['verdict_counts']}")
    for t in lane10["tests"]:
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    summary = {
        "fire_id": "fire_22_2026_05_07",
        "lanes": ["11_batch_sweep", "10_real_paper_oob"],
        "lane_11": lane11,
        "lane_10": lane10,
    }
    out_path = out_dir / "substrate_tester_fire_22_results.json"
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
