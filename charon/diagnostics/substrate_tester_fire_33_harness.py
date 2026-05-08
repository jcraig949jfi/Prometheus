"""Substrate-Tester Fire #33 harness — mini-window verification.

Per the dispatch summary at pivot/mini_contract_window_2026-05-08_summary.md,
the first post-restart Substrate-Tester fire should re-probe Lane 3 to
regression-confirm the P0 fix lands in the wild. This fire pairs that
with a Lane 17 mutation-test on a frozen-dataclass module to verify the
new audit catches what fire #25's mutation testing previously surfaced.

Coordination: my fire #32 was last; no new parallel since the
mini-window dispatch closed (commit ee109150).

Lane 3 — REGRESSION on T-ST-fire17-001 P0 (closed at commit 881e416d).
Re-runs the same smuggle attack chain that escalated to P0 in fire #17.
Each step should now fail at the boundary:
  Step 1: MethodSpec(independence_class="not_a_registered_class_xyz")
          should raise ValueError with registered-set listing.
  Step 2: TriangulationPath(method_class="not_a_method_class_enum")
          should raise ValueError with registered-set listing.
  Step 3 (post-construction mutation bypass): if a path's IC is mutated
          via object.__setattr__ to a bogus string, evaluate() should
          REJECT with "Defense-in-depth violation" reason.

Lane 17 — REGRESSION on T-ST-fire25-001 P1 (closed at commit f7c1c56d).
Re-runs mutation-testing framework on sigma_kernel/exclusion_certificate.py
(same module that surfaced 3 frozen-dataclass survivors in fire #25).
Post-fix: those frozen-flip mutations should now be KILLED by the new
test_frozen_invariance.py audit.

Outputs:
  charon/diagnostics/substrate_tester_fire_33_results.json
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 3 — P0 smuggle attack regression
# ---------------------------------------------------------------------------


def lane_3_p0_regression() -> Dict[str, Any]:
    """Re-run the fire #17 smuggle attack chain. Each step should fail."""
    from sigma_kernel.method_spec import IndependenceClass, MethodSpec
    from sigma_kernel.triangulation_protocol import (
        MethodClass,
        TriangulationPath,
        TriangulationProtocol,
        TriangulationVerdict,
    )

    tests: List[Dict[str, Any]] = []

    # T1: Step 1 of the attack — MethodSpec with arbitrary IC string.
    try:
        spec_arb = MethodSpec(
            engine="bogus_engine",
            strategy="bogus_strategy",
            independence_class="not_a_registered_class_xyz",  # type: ignore
            version="1.0.0",
        )
        tests.append({
            "id": "T1_step1_methodspec_arbitrary_ic_must_raise",
            "expected": "ValueError (post-Tier-1 fix)",
            "actual": f"silently accepted: ic={spec_arb.independence_class!r} — REGRESSION!",
            "verdict": "FAIL",
            "severity": "P0-blocker",
            "note": "Tier 1 fix HAS REGRESSED — substrate accepting arbitrary IC again",
        })
    except ValueError as exc:
        tests.append({
            "id": "T1_step1_methodspec_arbitrary_ic_must_raise",
            "expected": "ValueError",
            "actual": f"ValueError raised: {str(exc)[:140]}",
            "verdict": "PASS",
            "note": "Tier 1 contract change #1 holds",
        })

    # T2: Step 2 of the attack — TriangulationPath with arbitrary method_class.
    spec = MethodSpec(
        engine="x", strategy="y",
        independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
    )
    try:
        path = TriangulationPath(
            path_id="smuggle_p2",
            method_spec=spec,
            method_class="not_a_method_class_enum",  # type: ignore
            verdict="verified",
            runtime_ms=10,
            rationale="probe",
            timestamp=time.time(),
        )
        tests.append({
            "id": "T2_step2_triangpath_arbitrary_method_class_must_raise",
            "expected": "ValueError (post-Tier-1 fix)",
            "actual": f"silently accepted: method_class={path.method_class!r} — REGRESSION!",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })
    except ValueError as exc:
        tests.append({
            "id": "T2_step2_triangpath_arbitrary_method_class_must_raise",
            "expected": "ValueError",
            "actual": f"ValueError raised: {str(exc)[:140]}",
            "verdict": "PASS",
            "note": "Tier 1 contract change #2 holds",
        })

    # T3: Step 3 — defense-in-depth at evaluate() with mutation bypass.
    # Construct 3 valid paths, then mutate one's IC via object.__setattr__
    # to a bogus string (simulating legacy unpickle or adversarial path).
    spec_proof = MethodSpec(
        engine="sympy", strategy="factor_list",
        independence_class=IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION,
    )
    spec_num = MethodSpec(
        engine="mpmath", strategy="polyroots",
        independence_class=IndependenceClass.MPMATH_NUMERICAL_ROOT_FINDING,
    )
    spec_cat = MethodSpec(
        engine="lmfdb", strategy="lookup",
        independence_class=IndependenceClass.LMFDB_CATALOG,
    )
    path_primary = TriangulationPath(
        path_id="primary",
        method_spec=spec_proof,
        method_class=MethodClass.PROOF_BEARING,
        verdict="verified",
        runtime_ms=10,
        rationale="primary",
        timestamp=time.time(),
    )
    path_real = TriangulationPath(
        path_id="real_other",
        method_spec=spec_num,
        method_class=MethodClass.NUMERICAL,
        verdict="verified",
        runtime_ms=15,
        rationale="other",
        timestamp=time.time(),
    )
    path_smuggled = TriangulationPath(
        path_id="smuggled",
        method_spec=spec_cat,
        method_class=MethodClass.CATALOG,
        verdict="verified",
        runtime_ms=20,
        rationale="smuggled",
        timestamp=time.time(),
    )
    # Bypass: mutate the inner MethodSpec's independence_class
    object.__setattr__(
        path_smuggled.method_spec,
        "independence_class",
        "post_construction_arbitrary_ic_string",
    )
    try:
        protocol = TriangulationProtocol()
        result = protocol.evaluate([path_primary, path_real, path_smuggled])
        if result.upgrade_eligible:
            tests.append({
                "id": "T3_step3_defense_in_depth_at_evaluate",
                "expected": "REJECTED (defense-in-depth)",
                "actual": (
                    f"UPGRADED: verdict={result.verdict.value}, "
                    f"summary={result.summary[:140]} — REGRESSION!"
                ),
                "verdict": "FAIL",
                "severity": "P0-blocker",
            })
        elif result.verdict == TriangulationVerdict.REJECTED and "Defense-in-depth" in result.summary:
            tests.append({
                "id": "T3_step3_defense_in_depth_at_evaluate",
                "expected": "REJECTED with 'Defense-in-depth violation'",
                "actual": f"REJECTED: {result.summary[:140]}",
                "verdict": "PASS",
                "note": "Tier 1 contract change #3 holds",
            })
        else:
            tests.append({
                "id": "T3_step3_defense_in_depth_at_evaluate",
                "expected": "REJECTED with defense-in-depth reason",
                "actual": f"verdict={result.verdict.value}, upgrade_eligible={result.upgrade_eligible}, summary={result.summary[:140]}",
                "verdict": "PARTIAL",
                "severity": "P2-normal",
                "note": "Did not upgrade (good) but reason wasn't defense-in-depth specifically",
            })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T3_step3_defense_in_depth_at_evaluate",
            "expected": "REJECTED with defense-in-depth reason",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "ERROR",
            "severity": "P2-normal",
        })

    # T4: positive control — clean 3-path triangulation still upgrades
    paths_clean = [path_primary, path_real,
        TriangulationPath(
            path_id="real_cat",
            method_spec=MethodSpec(
                engine="lmfdb", strategy="lookup_clean",
                independence_class=IndependenceClass.LMFDB_CATALOG,
            ),
            method_class=MethodClass.CATALOG,
            verdict="verified",
            runtime_ms=20,
            rationale="clean catalog",
            timestamp=time.time(),
        ),
    ]
    try:
        protocol = TriangulationProtocol()
        result = protocol.evaluate(paths_clean)
        if result.upgrade_eligible and result.verdict == TriangulationVerdict.UPGRADED_TO_LOCAL_LEMMA:
            tests.append({
                "id": "T4_positive_control_clean_3_paths_upgrade",
                "expected": "UPGRADED_TO_LOCAL_LEMMA",
                "actual": f"upgraded: {result.summary[:140]}",
                "verdict": "PASS",
                "note": "no over-blocking; clean paths still certify",
            })
        else:
            tests.append({
                "id": "T4_positive_control_clean_3_paths_upgrade",
                "expected": "UPGRADED_TO_LOCAL_LEMMA",
                "actual": f"verdict={result.verdict.value}, upgrade_eligible={result.upgrade_eligible}",
                "verdict": "FAIL",
                "severity": "P1-high",
                "note": "OVER-BLOCKING: Tier 1 fix rejected legitimate paths",
            })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T4_positive_control_clean_3_paths_upgrade",
            "expected": "UPGRADED_TO_LOCAL_LEMMA",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "ERROR",
            "severity": "P1-high",
        })

    return {
        "lane": "3_p0_smuggle_regression",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Lane 17 — mutation testing regression on frozen-dataclass module
# ---------------------------------------------------------------------------


def lane_17_mutation_regression() -> Dict[str, Any]:
    """Re-run mutation testing on sigma_kernel/exclusion_certificate.py.
    Fire #25 found 3 GENUINE @dataclass(frozen=True) survivors. Post-fix
    (Tier 2 frozen-invariance audit), those frozen-flip mutations should
    now be KILLED — the audit's introspection catches the flip during
    pytest sweep."""
    target = "sigma_kernel/exclusion_certificate.py"
    test_cmd = (
        "python -m pytest "
        "sigma_kernel/test_exclusion_certificate.py "
        "sigma_kernel/tests/test_frozen_invariance.py "
        "-q --tb=no"
    )
    max_mutations = 8

    t0 = time.time()
    proc = subprocess.run(
        [
            "python", "-m", "prometheus_math.mutation_testing",
            "--target", target,
            "--test-cmd", test_cmd,
            "--max-mutations", str(max_mutations),
            "--timeout", "90",
        ],
        cwd=str(REPO),
        capture_output=True, text=True, timeout=900,
        env={"PYTHONPATH": str(REPO), **os.environ},
    )
    elapsed = time.time() - t0

    progress_lines = [
        line for line in (proc.stderr or "").splitlines()
        if "[mutation" in line
    ]

    summary_line = ""
    score = None
    n_killed = n_survived = n_errored = n_skipped = 0
    for line in progress_lines:
        if "score=" in line:
            summary_line = line
            try:
                m = re.search(r"score=([\d.]+)", line)
                if m: score = float(m.group(1))
                m = re.search(r"killed=(\d+)", line)
                if m: n_killed = int(m.group(1))
                m = re.search(r"survived=(\d+)", line)
                if m: n_survived = int(m.group(1))
                m = re.search(r"errored=(\d+)", line)
                if m: n_errored = int(m.group(1))
                m = re.search(r"skipped=(\d+)", line)
                if m: n_skipped = int(m.group(1))
            except Exception:
                pass

    mutations: List[Dict[str, str]] = []
    for line in progress_lines:
        if "/" in line and "@" in line and "(" in line and "s)" in line:
            try:
                parts = line.split()
                idx_part = parts[1].rstrip("]")
                idx = idx_part.split("/")[0]
                verdict = parts[2]
                site = parts[4] if len(parts) > 4 else ""
                mutations.append({"idx": idx, "verdict": verdict, "site": site})
            except Exception:
                continue

    # Critical regression check: any frozen-dataclass mutation must now
    # be KILLED (was SURVIVED in fire #25).
    frozen_dataclass_outcomes = []
    for m in mutations:
        if "boolean_not" in m["site"]:
            line_no = int(m["site"].split(":")[1]) if ":" in m["site"] else 0
            if line_no > 0:
                try:
                    src_text = (REPO / target).read_text(encoding="utf-8")
                    src_line = src_text.splitlines()[line_no - 1]
                    if "@dataclass(frozen=True)" in src_line:
                        frozen_dataclass_outcomes.append({
                            "site": m["site"],
                            "verdict": m["verdict"],
                            "src_line": src_line.strip(),
                        })
                except Exception:
                    pass

    # All frozen-dataclass mutations should now be KILLED post-Tier 2
    n_frozen_killed = sum(1 for o in frozen_dataclass_outcomes if o["verdict"] == "killed")
    n_frozen_survived = sum(1 for o in frozen_dataclass_outcomes if o["verdict"] == "survived")
    regression_held = n_frozen_survived == 0 and n_frozen_killed > 0

    return {
        "lane": "17_mutation_regression_on_exclusion_certificate",
        "target": target,
        "wall_clock_seconds": elapsed,
        "rc": proc.returncode,
        "summary_line": summary_line,
        "score": score,
        "n_killed": n_killed,
        "n_survived": n_survived,
        "n_errored": n_errored,
        "n_skipped": n_skipped,
        "mutations": mutations,
        "frozen_dataclass_outcomes": frozen_dataclass_outcomes,
        "n_frozen_killed_post_audit": n_frozen_killed,
        "n_frozen_survived_post_audit": n_frozen_survived,
        "tier_2_audit_regression_held": regression_held,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 33,
        "lanes": [3, 17],
        "purpose": "mini-window verification (P0 smuggle + Tier 2 audit regression)",
        "lane_3": lane_3_p0_regression(),
        "lane_17": lane_17_mutation_regression(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_33_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 3: {summary['lane_3']['verdict_counts']}")
    l17 = summary["lane_17"]
    print(f"Lane 17: score={l17['score']}, killed={l17['n_killed']}, "
          f"survived={l17['n_survived']}")
    print(f"  Frozen-dataclass mutations: {l17['n_frozen_killed_post_audit']} killed, "
          f"{l17['n_frozen_survived_post_audit']} survived")
    print(f"  Tier 2 audit regression held: {l17['tier_2_audit_regression_held']}")
    return summary


if __name__ == "__main__":
    run()
