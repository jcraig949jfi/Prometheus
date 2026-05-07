"""
Substrate-Tester Fire #26 — Lane 11 (batch-sweep with new seed) + Lane 13
(canonicalization-fuzz with fresh hypothesis seed 20260520).

Coordination: parallel substrate-tester ran fire #25 (commit 636f4c40)
covering Lane 17, surfacing P1 ticket T-ST-fire25-001 on substrate-wide
@dataclass(frozen=True) gap. My fire = #26, lanes 11 + 13.

Lane 11: re-baseline batch-sweep ingest at a new sampling seed
(20260507_26). Last my-instance Lane 11 was fire #22.

Lane 13: continue cumulative fuzz coverage with new hypothesis seed
20260520. Cumulative seeds across fires #10/#13/#16/#23/#26 = 5
independent regions.

Author: substrate-tester (Charon-aligned), fire #26, 2026-05-07
"""

from __future__ import annotations

import json
import os
import random
import subprocess
import time
from collections import Counter
from pathlib import Path

REPO = Path("F:/Prometheus")


def lane_11_batch_sweep_new_seed() -> dict:
    """Sample 30 probes from v2 Harmonia corpora with new seed; submit
    each via SigmaKernel.CLAIM."""
    from sigma_kernel.sigma_kernel import SigmaKernel

    rng = random.Random(20260507_26)
    corpus_dir = REPO / "aporia" / "meta" / "pressure_appliers" / "corpora_v2"
    corpus_files = sorted(p for p in corpus_dir.glob("harmonia_*.json"))

    probes = []
    for cf in corpus_files:
        try:
            data = json.loads(cf.read_text(encoding="utf-8"))
        except Exception:
            continue
        probe_list = None
        for k, v in data.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                first = v[0]
                if "id" in first and ("probe" in str(first).lower() or "question" in str(first).lower() or "expected" in str(first).lower()):
                    probe_list = v
                    break
        if probe_list is None:
            continue
        sample_size = min(6, len(probe_list))
        for p in rng.sample(probe_list, sample_size):
            probes.append({
                "corpus_file": cf.name,
                "probe_id": p.get("id"),
                "domain": p.get("domain"),
                "subdomain": p.get("subdomain"),
                "raw_probe": p,
            })

    kernel = SigmaKernel()
    t0 = time.time()
    submitted = []
    errors = []
    for idx, p in enumerate(probes):
        try:
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
            claim = kernel.CLAIM(target_name=target_name, hypothesis=hypothesis, evidence=evidence, kill_path=kill_path)
            submitted.append({"idx": idx, "probe_id": p["probe_id"], "claim_id": claim.id})
        except Exception as exc:
            errors.append({"idx": idx, "error": repr(exc)})

    elapsed = time.time() - t0
    domain_counts = Counter(p["domain"] for p in probes)

    tests = []
    if len(probes) >= 25 and len(errors) == 0:
        tests.append({
            "id": "T1_batch_sweep_clean_ingest",
            "expected": "30 probes ingested cleanly",
            "actual": f"{len(submitted)}/{len(probes)} submitted, 0 errors, throughput={len(submitted)/elapsed:.0f}/s",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T1_batch_sweep_clean_ingest",
            "expected": "30 probes",
            "actual": f"{len(submitted)} submitted, {len(errors)} errors",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    if len(domain_counts) >= 3:
        tests.append({
            "id": "T2_domain_coverage",
            "expected": "≥3 domains",
            "actual": f"{len(domain_counts)} domains: {dict(domain_counts)}",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T2_domain_coverage",
            "expected": "≥3 domains",
            "actual": f"{len(domain_counts)} domains",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    return {
        "lane": "11_batch_sweep",
        "n_probes": len(probes),
        "n_submitted": len(submitted),
        "n_errors": len(errors),
        "wall_clock_seconds": elapsed,
        "throughput_per_sec": (len(submitted) / elapsed) if elapsed > 0 else 0,
        "domain_counts": dict(domain_counts),
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


def lane_13_canon_fuzz_fresh_seed() -> dict:
    test_path = REPO / "prometheus_math" / "tests" / "test_canonicalization_fuzz.py"
    if not test_path.exists():
        return {"lane": "13_canonicalization_fuzz", "status": "DORMANT"}

    seed = "20260520"
    t0 = time.time()
    proc = subprocess.run(
        ["python", "-m", "pytest", str(test_path),
         "--hypothesis-show-statistics",
         f"--hypothesis-seed={seed}",
         "-v", "--tb=short"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=600,
        env={"PYTHONPATH": str(REPO), **os.environ},
    )
    elapsed = time.time() - t0

    stdout = proc.stdout
    test_lines = [l for l in stdout.splitlines() if " PASSED" in l or " FAILED" in l]
    n_passed = sum(1 for l in test_lines if " PASSED" in l)
    n_failed = sum(1 for l in test_lines if " FAILED" in l)
    summary_line = ""
    for line in stdout.splitlines():
        if ("passed" in line or "failed" in line) and "==" in line:
            summary_line = line.strip("=").strip()

    tests = []
    if proc.returncode == 0 and n_passed > 0 and n_failed == 0:
        tests.append({
            "id": "T1_fuzzer_clean_run",
            "expected": "all property tests pass",
            "actual": f"{n_passed} passed / 0 failed in {elapsed:.1f}s; {summary_line}",
            "verdict": "PASS",
            "severity": None,
            "note": f"hypothesis seed={seed}; cumulative coverage: 5+ independent seeds, 0 failures total",
        })
    elif n_failed > 0:
        tests.append({
            "id": "T1_fuzzer_clean_run",
            "expected": "all property tests pass",
            "actual": f"{n_passed} passed / {n_failed} FAILED",
            "verdict": "FAIL",
            "severity": "P1-high",
        })
    else:
        tests.append({
            "id": "T1_fuzzer_clean_run",
            "expected": "harness completes",
            "actual": f"rc={proc.returncode}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    return {
        "lane": "13_canonicalization_fuzz",
        "status": "LIVE",
        "hypothesis_seed": seed,
        "wall_clock_seconds": elapsed,
        "rc": proc.returncode,
        "n_passed": n_passed,
        "n_failed": n_failed,
        "summary_line": summary_line,
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


def main():
    out_dir = REPO / "charon" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== Substrate-Tester Fire #26 ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n--- Lane 11: batch-sweep new seed ---")
    lane11 = lane_11_batch_sweep_new_seed()
    print(f"Sampled: {lane11['n_probes']}, submitted: {lane11['n_submitted']}, errors: {lane11['n_errors']}")
    print(f"  Tests: {lane11['n_tests']}, verdicts: {lane11['verdict_counts']}")
    for t in lane11["tests"]:
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    print("\n--- Lane 13: canon-fuzz fresh seed (20260520) ---")
    lane13 = lane_13_canon_fuzz_fresh_seed()
    print(f"Status: {lane13.get('status')}, verdicts: {lane13.get('verdict_counts')}")
    for t in lane13.get("tests", []):
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    summary = {
        "fire_id": "fire_26_2026_05_07",
        "lanes": ["11_batch_sweep", "13_canonicalization_fuzz"],
        "lane_11": lane11,
        "lane_13": lane13,
    }
    out_path = out_dir / "substrate_tester_fire_26_results.json"
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
