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
