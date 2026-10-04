"""v2b unit tests (DEV-1). Run: <venv>/python -m pytest roles/Aphrodite/engine/v2b/tests -q"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paths  # noqa: E402,F401
import pytest  # noqa: E402

import gates  # noqa: E402
import supply  # noqa: E402
import capability as CAP  # noqa: E402


# ---------------------------------------------------------------- gates
def test_gate_qualifies_only_if_both_values_reachable():
    g = gates.Gate("beats_sham", lambda ev: ev["treat"] > ev["sham"])
    q = g.qualify({"treat": 2, "sham": 1}, {"treat": 1, "sham": 2})
    assert q["on_pass_fixture"] is True and q["on_fail_fixture"] is False and g.qualified


def test_constant_gate_is_unreachable():
    g = gates.Gate("hostile_evaluation", lambda ev: True)          # the historical S4 condition-4 shape
    with pytest.raises(gates.GateUnreachable):
        g.qualify({"x": 1}, {"x": 0})


def test_unqualified_gate_blocks_seal():
    with pytest.raises(gates.GateUnreachable):
        gates.require_qualified([gates.Gate("g", lambda e: bool(e))])


def test_gate_result_carries_evidence_digest_and_requires_bool():
    g = gates.Gate("g", lambda e: e > 0)
    r = g.evaluate(3)
    assert r.value is True and len(r.evidence_digest) == 16
    with pytest.raises(TypeError):
        gates.Gate("bad", lambda e: 1).evaluate(0)


def test_positive_control_equal_to_treatment_is_rejected():
    c = gates.Control("PC", "(acc + {H})", "POSITIVE")             # the historical S4 positive-control shape
    with pytest.raises(gates.ControlNotDistinct):
        c.check_distinct("(acc + {H})")
    assert gates.Control("PC", "(acc * {H})", "POSITIVE").check_distinct("(acc + {H})")


def test_lint_reproduces_historical_constant_gates():
    eng = paths.ENG
    found = {(Path(h["path"]).name, h["line"]) for f in ("run_s3s4.py", "a16.py", "a17.py", "run_g2.py")
             for h in gates.lint_errors(eng / f)}
    for site in [("run_s3s4.py", 391), ("run_s3s4.py", 420), ("a16.py", 489), ("a16.py", 547),
                 ("a17.py", 581), ("a17.py", 639), ("run_g2.py", 395)]:
        assert site in found, site


def test_v2b_tree_has_no_constant_gates():
    errs = []
    for f in sorted(paths.V2B.glob("*.py")):
        if f.name in ("tribunal_t4_v1a.py", "ruler_v21.py"):
            continue
        errs += gates.lint_errors(f)
    assert errs == []


def test_lint_flags_dict_and_subscript_constants(tmp_path):
    p = tmp_path / "x.py"
    p.write_text('c = {}\nc["4_hostile_evaluation"] = True\nout = {"R5_clean_transplant": True}\n'
                 'ok = True\nfor i in range(3):\n    ok = ok and i < 5\n', encoding="utf-8")
    errs = {(h["kind"], h["name"]) for h in gates.lint_errors(p)}
    assert ("SUBSCRIPT_CONST", "4_hostile_evaluation") in errs
    assert ("DICT_CONST", "R5_clean_transplant") in errs
    assert not any(n == "ok" for _k, n in errs)                      # init-then-computed flag is fine


# ---------------------------------------------------------------- supply
def test_supply_screen_fails_closed():
    rows = [{"name": "a"}, {"name": "b"}]
    rec = supply.screen("X", rows, lambda rows, r: ([], r < 5), replicates=8, quota=6)
    assert rec.replicates_fillable == 5 and not rec.passed and rec.unfilled == [5, 6, 7]
    with pytest.raises(supply.SupplyLimited):
        supply.require(rec)
    assert supply.require(supply.screen("X", rows, lambda rows, r: ([], True), 8, 6)).passed


# ---------------------------------------------------------------- capability (pure logic)
def _fq(ch, cens=False, spur=0):
    return {"charge": ch, "program": None if cens else ["fold"], "censored": cens, "spurious_before": spur}


def test_stratum_assignment():
    assert CAP.stratum(_fq(10)) == "COVERED"
    assert CAP.stratum(_fq(CAP.N_COV + 1)) == "WINDOW"
    assert CAP.stratum(_fq(CAP.DEFAULT_CAP, cens=True)) == "CENSORED"


def test_summary_counts_solves_where_reference_censored_and_cliff_excess():
    cap = CAP.DEFAULT_CAP
    rows = [{"family": "f", "cell": 0, "arms": {"PRISTINE": _fq(cap, True), "T": _fq(5000), "S": _fq(cap, True)}},
            {"family": "g", "cell": 0, "arms": {"PRISTINE": _fq(cap, True), "T": _fq(9000), "S": _fq(7000)}},
            {"family": "h", "cell": 0, "arms": {"PRISTINE": _fq(100), "T": _fq(50), "S": _fq(100)}}]
    s = CAP.summarise(rows, cap)
    assert s["by_arm"]["T"]["CENSORED"]["solves_where_ref_censored"] == 2
    assert s["by_arm"]["S"]["CENSORED"]["solves_where_ref_censored"] == 1
    assert CAP.generic_cliff_excess(s, "T", ["S"]) == 1
    assert s["by_arm"]["T"]["COVERED"]["n"] == 1 and s["by_arm"]["T"]["COVERED"]["median_delta"] > 0


# ---------------------------------------------------------------- walk (slow; exact)
@pytest.mark.slow
def test_walk_first_hit_matches_fast_cost():
    import a18
    import walk
    a18.worker_init()
    r = walk.conformance(n_pairs=10, seed="APHRODITE/V2B/WALK-CONF/pytest")
    assert r["mismatches"] == 0
