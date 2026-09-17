"""F10 predicate hypotheses: schema, row expressions, gates, calibration, and round 2 prior-key linking."""
from __future__ import annotations

import pytest

from primordial.score import predicates as P
from primordial.score import round2 as R2

RUNS = [{"kind": "run", "run_seed": s, "wall_s": 100.0 * s, "status": "record"} for s in range(8)]
SUMMARY = {"kind": "summary", "median": 13.5, "ctrl_median": 12.0, "ctrl_iqr": 2.0, "oracle_clean": True,
           "arm": {"p": 0.01}}


def loader(files):
    def load(source, path=None):
        if (source, path) not in files:
            raise P.Indeterminate(f"rows file {path} absent")
        return files[(source, path)]
    return load


def pred(**kw):
    p = {"metric": {"field": "median"}, "cells": {"source": "rows", "path": "r", "where": {"kind": "summary"}},
         "comparator": ">=", "threshold": 13.0, "seeds": "run 0-7", "ttl_cpu_s": 600, "prior": 0.5}
    p.update(kw)
    return p


LOAD = loader({("rows", "r"): RUNS + [SUMMARY]})


def test_schema_accepts_checkable_and_rejects_prose():
    assert P.validate_predicate(pred()) == []
    assert P.validate_predicate(pred(prior={"w4": 0.6, "w1": 0.2})) == []
    bad = P.validate_predicate({"metric": "held64 median over run seeds", "cells": "w4 train128", "comparator": "~",
                                "threshold": "median(clean) - 0.5*IQR(clean)", "prior": 1.5})
    assert "missing seeds" in bad and "missing ttl_cpu_s" in bad
    assert any("comparator" in b for b in bad) and any("cells must" in b for b in bad)
    assert any(b.startswith("metric is not") for b in bad) and any(b.startswith("threshold is not") for b in bad)
    assert any("prior must" in b for b in bad)
    assert P.validate_predicate(pred(cells={"source": "rows"})) == ["cells with source rows need a path"]


def test_field_against_number_and_row_formula():
    assert P.evaluate(pred(), LOAD)["outcome"] is True
    assert P.evaluate(pred(comparator=">", threshold=14), LOAD)["outcome"] is False
    formula = {"sum": [[1, {"field": "ctrl_median"}], [0.5, {"field": "ctrl_iqr"}]]}
    got = P.evaluate(pred(threshold=formula), LOAD)
    assert got == {"outcome": True, "lhs": 13.5, "rhs": 13.0, "why": ""}
    assert P.evaluate(pred(metric={"field": "arm.p"}, comparator="<", threshold=0.05), LOAD)["outcome"] is True


def test_indeterminate_on_gate_ambiguity_missing_field_and_missing_file():
    gated = loader({("rows", "r"): RUNS + [dict(SUMMARY, oracle_clean=False)]})
    g = P.evaluate(pred(gate=[["oracle_clean", "==", True]]), gated)
    assert g["outcome"] is None and "gate oracle_clean" in g["why"]
    assert P.evaluate(pred(gate=[["oracle_clean", "==", True]]), LOAD)["outcome"] is True
    amb = P.evaluate(pred(cells={"source": "rows", "path": "r", "where": {"kind": "run"}}), LOAD)
    assert amb["outcome"] is None and "8 rows selected" in amb["why"]
    assert P.evaluate(pred(metric={"field": "nope"}), LOAD)["outcome"] is None
    assert "absent" in P.evaluate(pred(cells={"source": "rows", "path": "gone"}), LOAD)["why"]


def test_count_distinct_and_where_operators():
    cells = {"source": "rows", "path": "r", "where": {"kind": "run", "run_seed": ["<", 8]}}
    p = pred(cells=cells, metric={"count": ["wall_s", "<", 600]}, threshold=6, comparator="==")
    assert P.evaluate(p, LOAD)["outcome"] is True                       # seeds 0-5
    dup = loader({("rows", "r"): RUNS + [dict(RUNS[0])]})
    assert P.evaluate(p, dup)["lhs"] == 7
    p["metric"]["distinct"] = "run_seed"
    assert P.evaluate(p, dup)["lhs"] == 6


def test_all_conjunction_false_beats_indeterminate():
    ok = {"metric": {"field": "median"}, "comparator": ">=", "threshold": 13}
    no = {"metric": {"field": "median"}, "comparator": ">=", "threshold": 99}
    gone = {"metric": {"field": "nope"}, "comparator": ">=", "threshold": 0}
    conj = lambda subs: P.evaluate(pred(metric={"all": subs}, comparator="==", threshold=True), LOAD)["outcome"]
    assert conj([ok, ok]) is True
    assert conj([ok, no, gone]) is False
    assert conj([ok, gone]) is None


def _qd(median, nbytes, baseline, status="record", iqr=6.0, exp="x"):
    return {"cell": {"representation": "linear", "world": "w4", "pressure": "p", "substrate": "numba_fused",
                     "channel": "none"}, "mechanism": exp, "fitness": {"held64_median": median, "iqr": iqr, "n_runs": 8},
            "footprint": {"genome_bytes": nbytes}, "baseline": baseline, "status": status, "exp_id": exp}


def test_qd_check_recomputes_clause_a_and_cheat_rows_are_indeterminate():
    rows = [_qd(90.0, 312, True, exp="base"), _qd(88.0, 200, False, exp="cand"), _qd(88.0, 200, False, "cheat", exp="ch")]
    load = loader({("qd", None): rows})
    p = lambda exp: pred(metric={"qd_check": True}, cells={"source": "qd", "where": {"exp_id": exp}},
                         comparator="==", threshold="PASS")
    assert P.validate_predicate(p("cand")) == []
    assert P.evaluate(p("cand"), load)["outcome"] is True
    ch = P.evaluate(p("ch"), load)
    assert ch["outcome"] is None and "INELIGIBLE" in ch["why"]


def test_rows_equal_share():
    a = [{"k": i, "v": i, "ts": 1} for i in range(4)]
    b = [{"k": i, "v": i if i < 2 else -1, "ts": 2} for i in range(4)]
    load = loader({("rows", "a"): a, ("rows", "b"): b})
    spec = lambda other: {"rows_equal": {"a": {"source": "rows", "path": "a"}, "b": {"source": "rows", "path": other},
                                         "key": ["k"], "ignore": ["ts"]}}
    assert P.value(spec("a"), {}, load) == 1.0
    assert P.value(spec("b"), {}, load) == 0.5


def test_calibration_scores_decided_only():
    res = [{"cohort": "C", "prior": 0.8, "outcome": True}, {"cohort": "C", "prior": 0.6, "outcome": False},
           {"cohort": "C", "prior": 0.5, "outcome": None}, {"cohort": "B", "prior": 0.3, "outcome": None}]
    b, c = P.calibration(res)
    assert b == {"cohort": "B", "n": 1, "n_decided": 0, "n_indeterminate": 1}
    assert c == {"cohort": "C", "n": 3, "n_decided": 2, "n_indeterminate": 1, "mean_prior": 0.7, "hit_rate": 0.5,
                 "brier": 0.2, "over_confidence": 0.2}


def test_round2_prior_keys_match_exactly_one_cell():
    assert R2.key_constraints("int2_w4_128") == {"bits": 2, "world": "w4", "pressure": "train128_held64"}
    assert R2.key_constraints("w4_8_A2") == {"world": "w4", "pressure": "train8_held64", "acts": 2}
    assert R2.key_constraints("control_detected") is None
    row = {"cell": {"world": "w4", "pressure": "train8_held64", "representation": "linear_int3_nibble_a2"}}
    assert R2.cell_facts(row) == {"world": "w4", "pressure": "train8_held64", "bits": 3, "acts": 2}
    assert R2.match_prior({"int2_w4_128": 0.6, "a2_w4_8": 0.55, "a2_w3_128": 0.5}, row) == ("a2_w4_8", 0.55)
    assert R2.match_prior(0.7, row) == (None, 0.7)
    with pytest.raises(R2.LinkError):
        R2.match_prior({"w4": 0.6, "w4_8": 0.5}, row)                # two keys match: ambiguous
    with pytest.raises(R2.LinkError):
        R2.match_prior({"w1": 0.6}, row)                             # none match


def test_round2_replay_resolves_every_receipt_with_a_prior():
    """F10 acceptance on the committed round 2 export, QD ledger and rows."""
    out = R2.resolve()
    assert out["coverage"] == {"receipts": 37, "with_prior": 37, "resolved_by_code": 37, "units": 43,
                               "decided": 41, "untranslated": 0}
    by = {(r["exp_id"], r["prior_key"]): r for r in out["resolutions"]}
    assert by[("C-R2-01-tt-feat-w4-cpu-ttl", None)]["outcome"] is False
    assert by[("C-R2-05-tt-digits-w5-corruption-torch-gpu", None)]["outcome"] is True
    assert "gate oracle_clean" in by[("C-R2-08-small-program-w4-decoder-rent-metered", None)]["why"]
    assert by[("C-R2-09-nk-linear-heldout-graphblas", None)]["outcome"] is True
    assert "INELIGIBLE" in by[("B-R2-4-int2-linear-nibble-w4-train128", "bits2")]["why"]
    assert all(by[("B-R2-8-readjudicate-powered-brain-cheats", k)]["outcome"] is True
               for k in ("int2_w4_128", "a2_w4_8", "a2_w3_128"))
    assert by[(R2.E_T1, "control_detected")]["outcome"] is True and by[(R2.E_T1, "cheats_silent")]["outcome"] is False
    assert by[(R2.E_T1B, "rerun_identical")]["lhs"] == 1.0
    assert not any("prior_mismatch" in r for r in out["resolutions"])
    # recomputed clause A agrees with the verdict each B QD row recorded when it was written
    qd = {(r["exp_id"], r["cell"]["world"], r["cell"]["pressure"], r["cell"]["representation"]): r
          for r in R2.Loader()("qd") if r.get("cohort") == "B"}
    for r in out["resolutions"]:
        if r["cohort"] == "B" and r["outcome"] is not None:
            w = r["predicate"]["cells"]["where"]
            row = qd[(r["exp_id"], w["cell.world"], w["cell.pressure"], w["cell.representation"])]
            assert row["clause_a"]["verdict"] == ("PASS" if r["outcome"] else "FAIL"), r["exp_id"]


def test_round2_predicate_ids_come_from_identifiers():
    assert R2.predicate_id({"lane": "B", "claim": "B-R2-9: the 8 B cell ...", "exp_id": "B-R2-6-int2-a2-x"}) == "B-R2-9"
    assert R2.predicate_id({"lane": "B", "claim": "an int4 linear ...", "exp_id": "B-R2-1-int4-x"}) == "B-R2-1"
    assert R2.predicate_id({"lane": "C", "claim": "drawn cell", "exp_id": "C-R2-01-x"}) == "C-R2-01-x"
