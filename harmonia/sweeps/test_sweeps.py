"""
Tests for the Pattern 30/20/19 auto-sweep modules.

Run:  python -m harmonia.sweeps.test_sweeps

The headline regression is F043: the BSD-Sha rearrangement must BLOCK.
"""
from __future__ import annotations

import sys

import sympy

from harmonia.sweeps.pattern_30 import (
    CouplingCheck,
    sweep as sweep30,
    bsd_f043_check,
    f015_szpiro_check,
    classify_entry,
    LINEAGE_TYPES,
)
from harmonia.sweeps.pattern_20 import (
    Pattern20Check,
    StratifiedStat,
    sweep as sweep20,
)
from harmonia.sweeps.pattern_19 import (
    NewMeasurement,
    PriorRecord,
    sweep as sweep19,
)
from harmonia.sweeps.runner import (
    sweep_signature,
    SweepBlocked,
)


FAILS: list = []


def check(name: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


def test_pattern_30_f043_blocks():
    print("Pattern 30 — F043 BSD rearrangement (must BLOCK)")
    r = sweep30(bsd_f043_check())
    check("F043 level is 3 (REARRANGEMENT)", r.level == 3, f"got level={r.level}")
    check("F043 verdict is BLOCK", r.verdict == "BLOCK", r.verdict)
    check("F043 rationale mentions identity", "identity" in r.rationale.lower())


def test_pattern_30_f015_weak():
    print("Pattern 30 — F015 Szpiro (hint: weak_algebraic)")
    r = sweep30(f015_szpiro_check())
    check("F015 level is 1 (WEAK_ALGEBRAIC)", r.level == 1, f"got level={r.level}")
    check("F015 verdict is WARN", r.verdict == "WARN", r.verdict)


def test_pattern_30_clean():
    print("Pattern 30 — clean case (disjoint atoms)")
    x, y, a, b = sympy.symbols("x y a b")
    c = CouplingCheck(X_expr=x + a, Y_expr=y + b, known_identities=[])
    r = sweep30(c)
    check("clean level is 0 (CLEAN)", r.level == 0)
    check("clean verdict is CLEAR", r.verdict == "CLEAR")


def test_pattern_30_shared_variable():
    print("Pattern 30 — shared variable")
    x, y = sympy.symbols("x y")
    c = CouplingCheck(X_expr=x, Y_expr=2 * x + y, known_identities=[])
    r = sweep30(c)
    check("shared-variable level is 2", r.level == 2)
    check("shared-variable verdict is BLOCK", r.verdict == "BLOCK")


def test_pattern_30_identity():
    print("Pattern 30 — exact identity")
    x = sympy.symbols("x")
    c = CouplingCheck(X_expr=sympy.log(x), Y_expr=sympy.log(x), known_identities=[])
    r = sweep30(c)
    check("identity level is 4", r.level == 4)
    check("identity verdict is BLOCK", r.verdict == "BLOCK")


def test_pattern_20_f015_pooled_magnitude():
    print("Pattern 20 — F015 pooled vs per-k strata")
    c = Pattern20Check(
        pooled_value=-0.60,
        pooled_n=30000,
        stratified=[
            StratifiedStat("k=1", -0.13, 5000),
            StratifiedStat("k=2", -0.45, 5000),
            StratifiedStat("k=3", -0.49, 5000),
            StratifiedStat("k=4", -0.36, 5000),
            StratifiedStat("k=5", -0.48, 5000),
            StratifiedStat("k=6", -0.46, 5000),
        ],
        label="szpiro_slope",
    )
    r = sweep20(c)
    check(
        "F015 pooled/stratum ratio > 1.2 -> WARN or BLOCK",
        r.verdict in ("WARN", "BLOCK"),
        f"verdict={r.verdict} ratio={r.ratio:.3f}",
    )
    check("F015 ratio ~1.6", abs(r.ratio - 1.6) < 0.2, f"ratio={r.ratio:.3f}")


def test_pattern_20_no_stratification_warns():
    print("Pattern 20 — pooled alone warns for re-audit")
    c = Pattern20Check(pooled_value=0.45)
    r = sweep20(c)
    check("pooled alone => WARN", r.verdict == "WARN")


def test_pattern_20_sign_discordant_blocks():
    print("Pattern 20 — sign-discordant strata blocks")
    c = Pattern20Check(
        pooled_value=0.4,
        pooled_n=200,
        stratified=[
            StratifiedStat("a", 0.5, 100),
            StratifiedStat("b", -0.2, 100),
        ],
    )
    r = sweep20(c)
    check("sign discordance => BLOCK", r.verdict == "BLOCK")


def test_pattern_20_small_n_flag():
    print("Pattern 20 — tiny strata get FLAG_INCONCLUSIVE")
    c = Pattern20Check(
        pooled_value=0.3,
        stratified=[
            StratifiedStat("a", 0.3, 20),
            StratifiedStat("b", 0.31, 25),
        ],
    )
    r = sweep20(c)
    check("tiny-n WARN", r.verdict == "WARN", f"verdict={r.verdict}")


def test_pattern_19_f012_staleness():
    print("Pattern 19 — F012 stale |z|=6.15 vs clean 0.39")
    prior = PriorRecord(
        feature_id="F012", effect_size=6.15, z_score=6.15, n_samples=4000,
    )
    new = NewMeasurement(
        feature_id="F012", effect_size=0.39, z_score=0.39, n_samples=66158,
    )
    r = sweep19(new, prior)
    check("F012 staleness WARN", r.verdict == "WARN", f"verdict={r.verdict}")


def test_pattern_19_sign_flip_blocks():
    print("Pattern 19 — z sign flip blocks")
    prior = PriorRecord(
        feature_id="F_x", effect_size=0.4, z_score=5.0, n_samples=1000,
    )
    new = NewMeasurement(
        feature_id="F_x", effect_size=-0.4, z_score=-5.0, n_samples=3000,
    )
    r = sweep19(new, prior)
    check("sign-flip BLOCK", r.verdict == "BLOCK")


def test_runner_f043_blocks_ingestion():
    print("Runner — F043 signature is BLOCKed end-to-end")
    outcome = sweep_signature(
        coupling_check=bsd_f043_check(),
        pattern20_check=None,
        pattern19_new=None,
    )
    check("runner overall BLOCK", outcome.overall == "BLOCK")
    check("runner blocked flag", outcome.blocked is True)
    try:
        if outcome.blocked:
            raise SweepBlocked(outcome)
        check("SweepBlocked raised", False)
    except SweepBlocked:
        check("SweepBlocked raised", True)


def test_runner_override_bypasses_block():
    print("Runner — override bypasses BLOCK but records reason")
    outcome = sweep_signature(
        coupling_check=bsd_f043_check(),
        override=True,
        override_reason="test override",
    )
    check("override preserves BLOCK verdict", outcome.overall == "BLOCK")
    check("override unsets blocked flag", outcome.blocked is False)
    check("override reason preserved", outcome.override_reason == "test override")


def test_runner_clean_signature_clears():
    print("Runner — clean signature => CLEAR")
    x, y = sympy.symbols("x y")
    outcome = sweep_signature(
        coupling_check=CouplingCheck(X_expr=x, Y_expr=y, known_identities=[]),
    )
    check("clean runner => CLEAR", outcome.overall == "CLEAR")


# ---------------------------------------------------------------------------
# Taxonomy extension (4-type LINEAGE_REGISTRY schema, 2026-04-20)
# ---------------------------------------------------------------------------

def test_classify_entry_algebraic_lineage_dict():
    print("Taxonomy — algebraic_lineage dict entry classifies like legacy")
    entry = {
        "type": "algebraic_lineage",
        "check": bsd_f043_check,
        "rationale": "F043 BSD rearrangement",
    }
    r = classify_entry(entry)
    check("type preserved", r["type"] == "algebraic_lineage")
    check("verdict BLOCK", r["verdict"] == "BLOCK", r["verdict"])
    check("level 3 REARRANGEMENT", r["level"] == 3, f"got {r['level']}")


def test_classify_entry_algebraic_lineage_legacy_callable():
    print("Taxonomy — bare callable still works (backward compat)")
    r = classify_entry(bsd_f043_check)
    check("legacy callable classifies", r["type"] == "algebraic_lineage")
    check("legacy callable still BLOCKs", r["verdict"] == "BLOCK")
    # F015 legacy shim
    r2 = classify_entry(f015_szpiro_check)
    check("F015 legacy shim verdict WARN", r2["verdict"] == "WARN")
    check("F015 legacy shim level 1", r2["level"] == 1)


def test_classify_entry_frame_hazard():
    print("Taxonomy — frame_hazard emits PROVISIONAL")
    entry = {
        "type": "frame_hazard",
        "sampling_frame": "LMFDB rank-4 corridor",
        "class_4_null_ref": "null_protocol_v1.md#class-4",
        "pending_audit": {
            "task_id": "audit_F044_framebased_resample",
            "on_complete": "re_evaluate",
        },
        "rationale": "rank-4 disc=conductor corridor; Pattern 4 gate",
    }
    r = classify_entry(entry)
    check("verdict PROVISIONAL", r["verdict"] == "PROVISIONAL", r["verdict"])
    check("type frame_hazard", r["type"] == "frame_hazard")
    check("details carry sampling_frame",
          "LMFDB" in (r["details"].get("sampling_frame") or ""))
    check("details carry pending_audit task_id",
          r["details"]["pending_audit"]["task_id"] == "audit_F044_framebased_resample")
    check("no level on PROVISIONAL", r["level"] is None)


def test_classify_entry_killed_no_correlation():
    print("Taxonomy — killed_no_correlation emits N/A_KILLED")
    entry = {
        "type": "killed_no_correlation",
        "rationale": "killed by block-shuffle null",
        "kill_null": "block-shuffle",
    }
    r = classify_entry(entry)
    check("verdict N/A_KILLED", r["verdict"] == "N/A_KILLED", r["verdict"])
    check("type killed_no_correlation", r["type"] == "killed_no_correlation")
    check("no level", r["level"] is None)


def test_classify_entry_non_correlational():
    print("Taxonomy — non_correlational emits N/A_NON_CORRELATIONAL")
    entry = {
        "type": "non_correlational",
        "claim_shape": "variance_deficit",
        "rationale": "GUE first-gap variance deficit",
    }
    r = classify_entry(entry)
    check("verdict N/A_NON_CORRELATIONAL",
          r["verdict"] == "N/A_NON_CORRELATIONAL", r["verdict"])
    check("type non_correlational", r["type"] == "non_correlational")
    check("no level", r["level"] is None)


def test_classify_entry_rejects_unknown_type():
    print("Taxonomy — unknown type raises ValueError")
    try:
        classify_entry({"type": "bogus_lineage"})
        check("unknown type raises", False)
    except ValueError:
        check("unknown type raises", True)


def test_registry_coverage_all_expected_fids():
    print("Registry — all target F-IDs present with correct types")
    from harmonia.sweeps.retrospective import LINEAGE_REGISTRY
    expected = {
        # algebraic_lineage
        "F015": "algebraic_lineage",
        "F041a": "algebraic_lineage",
        "F043": "algebraic_lineage",
        "F013": "algebraic_lineage",
        "F045": "algebraic_lineage",
        # frame_hazard
        "F044": "frame_hazard",
        # killed_no_correlation
        "F010": "killed_no_correlation",
        "F012": "killed_no_correlation",
        "F020": "killed_no_correlation",
        "F021": "killed_no_correlation",
        "F022": "killed_no_correlation",
        "F023": "killed_no_correlation",
        "F024": "killed_no_correlation",
        "F025": "killed_no_correlation",
        "F026": "killed_no_correlation",
        "F027": "killed_no_correlation",
        "F028": "killed_no_correlation",
        # non_correlational
        "F011": "non_correlational",
        "F014": "non_correlational",
    }
    for fid, expected_type in expected.items():
        entry = LINEAGE_REGISTRY.get(fid)
        check(f"{fid} present in LINEAGE_REGISTRY", entry is not None)
        if entry is not None:
            check(f"{fid} type={expected_type}",
                  entry.get("type") == expected_type,
                  f"got {entry.get('type')}")


def test_registry_existing_anchors_still_pass():
    print("Registry — existing F043/F015/F041a anchors unchanged")
    from harmonia.sweeps.retrospective import LINEAGE_REGISTRY
    r_f043 = classify_entry(LINEAGE_REGISTRY["F043"])
    r_f015 = classify_entry(LINEAGE_REGISTRY["F015"])
    r_f041a = classify_entry(LINEAGE_REGISTRY["F041a"])
    check("F043 still Level 3 BLOCK", r_f043["level"] == 3 and r_f043["verdict"] == "BLOCK")
    check("F015 still Level 1 WARN", r_f015["level"] == 1 and r_f015["verdict"] == "WARN")
    check("F041a still Level 1 WARN", r_f041a["level"] == 1 and r_f041a["verdict"] == "WARN")


def test_f013_uses_verbatim_rationale():
    print("Registry — F013 rationale contains James's verbatim text")
    from harmonia.sweeps.retrospective import LINEAGE_REGISTRY
    entry = LINEAGE_REGISTRY["F013"]
    rationale = entry.get("rationale", "")
    check("F013 rationale mentions root number",
          "root number" in rationale)
    check("F013 rationale mentions z=15.31",
          "z=15.31" in rationale)
    check("F013 rationale mentions BSD",
          "BSD" in rationale)


def test_f045_pending_audit_declared():
    print("Registry — F045 carries pending_audit for correlate_F041a_F045")
    from harmonia.sweeps.retrospective import LINEAGE_REGISTRY
    entry = LINEAGE_REGISTRY["F045"]
    pending = entry.get("pending_audit")
    check("F045 pending_audit present", pending is not None)
    check("F045 pending_audit task_id correct",
          pending and pending.get("task_id") == "correlate_F041a_F045_nbp_vs_isogeny")


def test_f044_pending_audit_declared():
    print("Registry — F044 carries pending_audit for audit_F044_framebased_resample")
    from harmonia.sweeps.retrospective import LINEAGE_REGISTRY
    entry = LINEAGE_REGISTRY["F044"]
    pending = entry.get("pending_audit")
    check("F044 pending_audit present", pending is not None)
    check("F044 pending_audit task_id correct",
          pending and pending.get("task_id") == "audit_F044_framebased_resample")
    check("F044 has class_4 ref",
          "class-4" in (entry.get("class_4_null_ref", "") or "").lower() or
          "class_4" in (entry.get("class_4_null_ref", "") or "").lower())


def test_runner_provisional_does_not_block():
    print("Runner — PROVISIONAL does not halt ingestion")
    # Build a verdict-shaped outcome by constructing a runner via a
    # frame_hazard entry. Since sweep_signature takes a CouplingCheck not
    # a lineage entry, we simulate by constructing SweepVerdict + merge
    # directly.
    from harmonia.sweeps.runner import SweepVerdict, _merge
    verdicts = [
        SweepVerdict(pattern="Pattern 30", verdict="PROVISIONAL",
                     rationale="frame_hazard", details={}),
        SweepVerdict(pattern="Pattern 20", verdict="CLEAR",
                     rationale="", details={}),
        SweepVerdict(pattern="Pattern 19", verdict="CLEAR",
                     rationale="", details={}),
    ]
    overall = _merge(verdicts)
    check("merge yields PROVISIONAL", overall == "PROVISIONAL", overall)


def test_runner_merge_precedence():
    print("Runner — BLOCK > PROVISIONAL > WARN > CLEAR precedence")
    from harmonia.sweeps.runner import SweepVerdict, _merge
    # BLOCK dominates PROVISIONAL
    v1 = [
        SweepVerdict(pattern="a", verdict="PROVISIONAL", rationale="", details={}),
        SweepVerdict(pattern="b", verdict="BLOCK", rationale="", details={}),
    ]
    check("BLOCK beats PROVISIONAL", _merge(v1) == "BLOCK")
    # PROVISIONAL dominates WARN
    v2 = [
        SweepVerdict(pattern="a", verdict="WARN", rationale="", details={}),
        SweepVerdict(pattern="b", verdict="PROVISIONAL", rationale="", details={}),
    ]
    check("PROVISIONAL beats WARN", _merge(v2) == "PROVISIONAL")
    # N/A_KILLED is CLEAR-equivalent
    v3 = [
        SweepVerdict(pattern="a", verdict="N/A_KILLED", rationale="", details={}),
        SweepVerdict(pattern="b", verdict="CLEAR", rationale="", details={}),
    ]
    check("N/A_KILLED merges to CLEAR", _merge(v3) == "CLEAR")
    # N/A_NON_CORRELATIONAL is CLEAR-equivalent
    v4 = [
        SweepVerdict(pattern="a", verdict="N/A_NON_CORRELATIONAL", rationale="", details={}),
        SweepVerdict(pattern="b", verdict="CLEAR", rationale="", details={}),
    ]
    check("N/A_NON_CORRELATIONAL merges to CLEAR", _merge(v4) == "CLEAR")


def test_pending_audit_watcher_lazy():
    print("Watcher — resolve_entry attaches pending_audit status")
    from harmonia.sweeps.retrospective import resolve_entry, LINEAGE_REGISTRY
    # F044 has a pending audit; resolve_entry should annotate the result
    # regardless of whether Agora is reachable (it degrades gracefully).
    r = resolve_entry("F044", LINEAGE_REGISTRY["F044"])
    details = r.get("details") or {}
    pending = details.get("pending_audit") or {}
    check("F044 resolved with pending_audit",
          pending.get("task_id") == "audit_F044_framebased_resample")
    check("F044 pending_audit has 'complete' bool",
          "complete" in pending)


def main():
    tests = [
        test_pattern_30_f043_blocks,
        test_pattern_30_f015_weak,
        test_pattern_30_clean,
        test_pattern_30_shared_variable,
        test_pattern_30_identity,
        test_pattern_20_f015_pooled_magnitude,
        test_pattern_20_no_stratification_warns,
        test_pattern_20_sign_discordant_blocks,
        test_pattern_20_small_n_flag,
        test_pattern_19_f012_staleness,
        test_pattern_19_sign_flip_blocks,
        test_runner_f043_blocks_ingestion,
        test_runner_override_bypasses_block,
        test_runner_clean_signature_clears,
        # 4-type taxonomy extension (2026-04-20)
        test_classify_entry_algebraic_lineage_dict,
        test_classify_entry_algebraic_lineage_legacy_callable,
        test_classify_entry_frame_hazard,
        test_classify_entry_killed_no_correlation,
        test_classify_entry_non_correlational,
        test_classify_entry_rejects_unknown_type,
        test_registry_coverage_all_expected_fids,
        test_registry_existing_anchors_still_pass,
        test_f013_uses_verbatim_rationale,
        test_f045_pending_audit_declared,
        test_f044_pending_audit_declared,
        test_runner_provisional_does_not_block,
        test_runner_merge_precedence,
        test_pending_audit_watcher_lazy,
    ]
    for t in tests:
        t()
    print()
    if FAILS:
        print(f"FAILED: {len(FAILS)} test(s)")
        for f in FAILS:
            print(f"  - {f}")
        sys.exit(1)
    print(f"OK: {len(tests)} tests passed")


if __name__ == "__main__":
    main()
