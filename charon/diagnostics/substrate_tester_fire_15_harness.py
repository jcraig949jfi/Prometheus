"""Substrate-Tester Fire #15 harness — Lane 17 (mutation-testing, fresh
target) + Lane 3 (correlated-triangulation x fire-14 finding interaction).

Lane 17: run mutation testing framework on sigma_kernel/coordinate_chart.py
(fresh target; fire #7 covered operator_portability). 8-mutation cap
keeps wall-clock under ~75s.

Lane 3 (interaction probe): fire #14 surfaced T-ST-fire14-001 — MethodSpec
silently accepts arbitrary strings as `independence_class`. The
TriangulationProtocol's independence rule depends on IC class equality.
Does the silent-string-accept actually BREAK independence enforcement?
That is, can a caller construct a "triangulation" where two paths share
the same arbitrary-string IC and have it COUNT AS INDEPENDENT? If yes,
the ticket should escalate from P1 to P0.

Outputs:
  charon/diagnostics/substrate_tester_fire_15_results.json
"""
from __future__ import annotations

import json
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 17 — mutation-testing on a fresh target
# ---------------------------------------------------------------------------


def lane_17_mutation_testing() -> Dict[str, Any]:
    """Run prometheus_math.mutation_testing on coordinate_chart.py."""
    target = "sigma_kernel/coordinate_chart.py"
    test_cmd = "python -m pytest sigma_kernel/test_coordinate_chart.py -q --tb=no"
    max_mutations = 8

    t0 = time.time()
    proc = subprocess.run(
        [
            "python", "-m", "prometheus_math.mutation_testing",
            "--target", target,
            "--test-cmd", test_cmd,
            "--max-mutations", str(max_mutations),
            "--timeout", "60",
        ],
        cwd=str(REPO),
        capture_output=True, text=True, timeout=900,
        env={"PYTHONPATH": str(REPO), **__import__("os").environ},
    )
    elapsed = time.time() - t0

    # Parse the stderr progress lines (the framework writes progress to stderr)
    progress_lines = [
        line for line in (proc.stderr or "").splitlines()
        if "[mutation" in line
    ]

    # Final summary line: "[mutation] score=... killed=N survived=N errored=N skipped=N"
    summary_line = ""
    score = None
    n_killed = n_survived = n_errored = n_skipped = 0
    for line in progress_lines:
        if "score=" in line:
            summary_line = line
            try:
                # extract score=NUM
                import re as _re
                m = _re.search(r"score=([\d.]+)", line)
                if m:
                    score = float(m.group(1))
                m = _re.search(r"killed=(\d+)", line)
                if m: n_killed = int(m.group(1))
                m = _re.search(r"survived=(\d+)", line)
                if m: n_survived = int(m.group(1))
                m = _re.search(r"errored=(\d+)", line)
                if m: n_errored = int(m.group(1))
                m = _re.search(r"skipped=(\d+)", line)
                if m: n_skipped = int(m.group(1))
            except Exception:
                pass

    # Per-mutation outcomes
    mutations = []
    for line in progress_lines:
        if "/" in line and "@" in line and "(" in line and "s)" in line:
            try:
                parts = line.split()
                idx_part = parts[1].rstrip("]")
                idx = idx_part.split("/")[0]
                verdict = parts[2]
                site = parts[4] if len(parts) > 4 else ""
                mutations.append({
                    "idx": idx,
                    "verdict": verdict,
                    "site": site,
                })
            except Exception:
                continue

    return {
        "lane": "17_mutation_testing_fresh_target",
        "target": target,
        "max_mutations_requested": max_mutations,
        "wall_clock_seconds": elapsed,
        "rc": proc.returncode,
        "summary_line": summary_line,
        "score": score,
        "n_killed": n_killed,
        "n_survived": n_survived,
        "n_errored": n_errored,
        "n_skipped": n_skipped,
        "mutations": mutations,
        "stderr_tail": (proc.stderr or "")[-1500:] if proc.returncode != 0 else "",
    }


# ---------------------------------------------------------------------------
# Lane 3 — TriangulationProtocol x fire-14 interaction probe
# ---------------------------------------------------------------------------


def lane_3_triangulation_x_fire14_finding() -> Dict[str, Any]:
    """Probe: can we construct a 'triangulation' where two methods both
    use the SAME arbitrary-string `independence_class`, and have the
    TriangulationProtocol falsely accept the upgrade?"""
    from sigma_kernel.method_spec import IndependenceClass, MethodSpec
    from sigma_kernel.triangulation_protocol import (
        MethodClass,
        TriangulationPath,
        TriangulationProtocol,
        TriangulationVerdict,
        method_class_for_independence_class,
    )

    tests: List[Dict[str, Any]] = []

    # Setup: build 3 TriangulationPath instances. Two of them use the SAME
    # arbitrary-string IC (the fire-14 finding). The third uses a real IC
    # so we have a proof-bearing path. Question: does the protocol's
    # independence rule consider the two arbitrary-string-IC paths as
    # "different" (because they're string-distinct from the real IC) or
    # as "same" (because they're string-equal to each other, but neither
    # is registered)?

    # T1: re-confirm fire-14 finding — MethodSpec accepts arbitrary string.
    try:
        spec_arb = MethodSpec(
            engine="bogus_engine",
            strategy="bogus_strategy",
            independence_class="not_a_registered_class_xyz",  # type: ignore
            version="1.0.0",
        )
        tests.append({
            "id": "T1_methodspec_accepts_arbitrary_ic_string",
            "expected": "fire-14 finding reproduces: MethodSpec accepts arbitrary string",
            "actual": f"accepted; independence_class={spec_arb.independence_class!r}",
            "verdict": "CONFIRMED",
            "note": "fire-14 finding T-ST-fire14-001 reproduces exactly",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T1_methodspec_accepts_arbitrary_ic_string",
            "expected": "fire-14 finding reproduces",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "RESOLVED-BY-TECHNE",
            "note": "fire-14 finding T-ST-fire14-001 has been fixed since",
        })
        return {
            "lane": "3_triangulation_x_fire14_finding",
            "tests": tests,
            "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
            "interaction_probe_skipped_because_finding_resolved": True,
        }

    # T2: method_class_for_independence_class on arbitrary IC string.
    # Per the post-contract-change-window code (commit 2067e678 from
    # T-2026-05-07-T018), unregistered IC raises KeyError.
    try:
        mc = method_class_for_independence_class("not_a_registered_class_xyz")
        tests.append({
            "id": "T2_unregistered_ic_method_class_lookup",
            "expected": "KeyError raised (post-T018 silent-sentinel fix)",
            "actual": f"silently returned MethodClass={mc!r}",
            "verdict": "FAIL",
            "severity": "P1-high",
            "note": "fire-14 finding INTERACTS — silent-sentinel here would let arbitrary IC pass through to triangulation",
        })
    except KeyError as exc:
        tests.append({
            "id": "T2_unregistered_ic_method_class_lookup",
            "expected": "KeyError raised",
            "actual": f"KeyError: {str(exc)[:140]}",
            "verdict": "PASS",
            "note": "T018 silent-sentinel fix HOLDS at the lookup site",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T2_unregistered_ic_method_class_lookup",
            "expected": "KeyError raised",
            "actual": f"raised {type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    # T3: build TriangulationPath instances with arbitrary-string IC and
    # see whether the protocol upgrade rule is broken. Per T2: if
    # method_class_for_independence_class raises on the arbitrary string,
    # the TriangulationPath construction itself should fail downstream.
    # If T2 silently returned, T3 would be the load-bearing question.

    # Real-IC paths first (proof-bearing for the primary).
    spec_real_proof = MethodSpec(
        engine="sympy",
        strategy="factor_list",
        independence_class=IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION,
        version="1.0.0",
    )
    spec_real_other = MethodSpec(
        engine="mpmath",
        strategy="polyroots",
        independence_class=IndependenceClass.MPMATH_NUMERICAL_ROOT_FINDING,
        version="1.0.0",
    )

    # Build paths. The proof-bearing one is required for the upgrade rule.
    try:
        path_primary = TriangulationPath(
            path_id="path_primary",
            method_spec=spec_real_proof,
            method_class=MethodClass.PROOF_BEARING,
            verdict="verified",
            timestamp=time.time(),
            summary="primary proof-bearing path",
        )
        path_real_other = TriangulationPath(
            path_id="path_other",
            method_spec=spec_real_other,
            method_class=MethodClass.NUMERICAL,
            verdict="verified",
            timestamp=time.time(),
            summary="independent numerical path",
        )
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T3_triangulation_setup",
            "expected": "real-IC paths construct cleanly",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "ERROR",
            "severity": "P2-normal",
        })
        return {
            "lane": "3_triangulation_x_fire14_finding",
            "tests": tests,
            "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        }

    # Try to inject an arbitrary-IC path. The TriangulationPath construction
    # itself doesn't go through method_class_for_independence_class — it
    # takes method_class as an explicit arg. So the question is whether the
    # protocol's evaluation logic calls is_independent_of() in a way that
    # the arbitrary-IC string would slip through.
    try:
        path_arb_ic = TriangulationPath(
            path_id="path_arb_ic",
            method_spec=spec_arb,
            method_class=MethodClass.NUMERICAL,  # caller-asserted, bypasses lookup
            verdict="verified",
            timestamp=time.time(),
            summary="arbitrary-IC path (smuggled in via explicit method_class)",
        )
        tests.append({
            "id": "T3_arb_ic_path_construction",
            "expected": "either reject OR produce a path that fails is_independent_of() downstream",
            "actual": "TriangulationPath constructed cleanly with arbitrary-string IC",
            "verdict": "OBSERVED",
            "note": "construction is permissive; the question is whether evaluate() catches it",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T3_arb_ic_path_construction",
            "expected": "construction OK or rejection",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "PASS",
            "note": "TriangulationPath construction rejects arbitrary IC at the boundary",
        })
        return {
            "lane": "3_triangulation_x_fire14_finding",
            "tests": tests,
            "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        }

    # T4: actually evaluate the protocol. With 3 paths (primary proof-bearing,
    # real numerical, arbitrary-IC numerical), does the protocol upgrade?
    try:
        protocol = TriangulationProtocol()
        result = protocol.evaluate([path_primary, path_real_other, path_arb_ic])
        # Substrate-grade question: does the protocol upgrade or reject?
        # If it UPGRADES, the arbitrary-IC path was treated as independent.
        # If it REJECTS or returns INSUFFICIENT_INDEPENDENCE, the protocol
        # is robust.
        verdict_str = result.verdict.value if hasattr(result.verdict, "value") else str(result.verdict)
        if result.upgrade_eligible:
            # Upgrade granted with an arbitrary-IC path counting as independent.
            # That's a substrate-flaw severity escalation.
            tests.append({
                "id": "T4_protocol_evaluate_with_arb_ic_path",
                "expected": "REJECT or INSUFFICIENT_INDEPENDENCE (arb-IC should not count as independent)",
                "actual": f"UPGRADED: verdict={verdict_str}, upgrade_eligible=True",
                "verdict": "FAIL",
                "severity": "P0-blocker",
                "note": "fire-14 finding UPGRADES TO P0: arb-IC path treated as independent in triangulation",
            })
        else:
            # Protocol is robust — refuses to upgrade despite arbitrary-IC
            # smuggling. T-ST-fire14-001 stays at P1 (input-validation gap).
            tests.append({
                "id": "T4_protocol_evaluate_with_arb_ic_path",
                "expected": "REJECT or INSUFFICIENT_INDEPENDENCE",
                "actual": f"verdict={verdict_str}, upgrade_eligible=False, summary={result.summary[:140]}",
                "verdict": "PASS",
                "note": "TriangulationProtocol robust against arbitrary-IC smuggling",
            })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T4_protocol_evaluate_with_arb_ic_path",
            "expected": "evaluate() returns or rejects cleanly",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "ERROR",
            "severity": "P2-normal",
        })

    return {
        "lane": "3_triangulation_x_fire14_finding",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 15,
        "lanes": [17, 3],
        "lane_17": lane_17_mutation_testing(),
        "lane_3": lane_3_triangulation_x_fire14_finding(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_15_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")

    l17 = summary["lane_17"]
    print(f"Lane 17: score={l17['score']}, killed={l17['n_killed']}, "
          f"survived={l17['n_survived']}, errored={l17['n_errored']}, "
          f"wall_clock={l17['wall_clock_seconds']:.1f}s")

    l3 = summary["lane_3"]
    print(f"Lane 3: {l3['verdict_counts']}")
    return summary


if __name__ == "__main__":
    run()
