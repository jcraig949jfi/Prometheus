"""Tests for hecate/alien/shadow_decisions.py, the exact-arithmetic shadow of
the PREREG s6/s7 decision layer (AUDIT_A_alien_semantics.md F01-F05).
Frozen code and RESULTS.json are only read."""

from fractions import Fraction as F

import pytest

from hecate.alien import shadow_decisions as SD


# ---- (a) exact threshold edges -------------------------------------------------------

def test_fraction_threshold_edge_h3_is_inclusive():
    assert F(1, 5) - F(1, 10) >= F(1, 10)
    # the frozen float path is the defect the shadow exists for (AUDIT_A F01)
    assert not ((1.0 - 0.8) - (1.0 - 0.9) >= 0.10)


@pytest.mark.parametrize("est,ci,thr,want", [
    (F(1, 10), (F(1, 1000), F(1, 5)), F(1, 10), "SUPPORTED"),        # est == thr counts
    (F(1, 10), (F(0), F(1, 5)), F(1, 10), "INDETERMINATE"),          # CI lower must be > 0
    (F(0), (F(0), F(1, 20) - F(1, 10 ** 9)), F(1, 10), "NOT_SUPPORTED"),
    (F(0), (F(0), F(1, 20)), F(1, 10), "INDETERMINATE"),             # CI upper must be < thr/2
    (F(1, 10 ** 9), (F(0), F(0)), F(1, 10), "INDETERMINATE"),        # est must be <= 0
    (F(3, 20), (F(1, 100), F(1, 4)), F(3, 20), "SUPPORTED"),
    (None, (None, None), F(1, 10), "NOT_ELIGIBLE"),
])
def test_decide_edges(est, ci, thr, want):
    assert SD.decide(est, ci, thr) == want


def test_q_recovers_rationals_from_frozen_floats():
    assert SD.q(1 - 0.85) == F(3, 20)
    assert SD.q(0.6458333333333334) == F(31, 48)
    assert SD.q(0.19999999999999996) == F(1, 5)


def test_auc_exact_ties_and_order():
    assert SD.auc_exact([1, 2], [1, 0]) == F(7, 8)      # (0.5 + 1 + 1 + 1) / 4
    assert SD.auc_exact([0], [0]) == F(1, 2)
    assert SD.auc_exact([], [1]) is None


def test_clopper_pearson_zero_successes():
    lo, hi = SD.clopper_pearson(0, 32)
    assert lo == 0 and abs(float(hi) - (1 - 0.025 ** (1 / 32))) < 1e-12   # 0.1089 (AUDIT_A F04)
    lo, hi = SD.clopper_pearson(20, 20)
    assert hi == 1 and abs(float(lo) - 0.025 ** (1 / 20)) < 1e-12


# ---- real runs -------------------------------------------------------------------

@pytest.fixture(scope="module")
def claude():
    return SD.shadow_cached("claude")


def _primary(res, h):
    return res["readings"][h][0]


def test_per_item_layer_reproduces_frozen_scores(claude):
    """T1/T2 recomputed in Fractions from runs/ equal RESULTS rows; exact
    LEARNED, analogy class and active LEARNED flags flip nowhere (so no
    divergence below comes from the per-item layer)."""
    assert all(v == [] for v in claude["per_item_checks"].values()), claude["per_item_checks"]


# ---- (b) faithful rules reproduce the recorded decision -----------------------------

@pytest.mark.parametrize("h", ["H1_t1", "H1_behav", "H2", "H5", "H6", "DETECTOR"])
def test_shadow_reproduces_recorded_where_code_is_faithful(claude, h):
    """AUDIT_A s3: H1, H2, H5 (s6 rule, bootstrap), H6 and the s7 detector
    (literal sets) are implemented as written; the primary shadow reading must
    agree with RESULTS.json."""
    p = _primary(claude, h)
    assert not p["diverges"], (h, p)


def test_bootstrap_replay_matches_recorded_cis(claude):
    """Same stream, same resampling unit: exact CIs equal the recorded floats."""
    import json
    rec = SD._results("claude")["summary"]
    for h in ("H1_t1", "H1_behav", "H2", "H5"):
        lo, hi = _primary(claude, h)["inputs"]["ci95_boot"]
        rlo, rhi = rec["hypotheses"][h]["ci95"]
        assert abs(float(lo) - rlo) < 1e-12 and abs(float(hi) - rhi) < 1e-12, h
    lo, _ = _primary(claude, "DETECTOR")["inputs"]["ci95_boot"]
    assert abs(float(lo) - rec["detector_validation"]["ci95_low"]) < 1e-12


@pytest.mark.parametrize("model", ["gptoss", "gemini"])
def test_other_families_primary_agrees(model):
    """gpt-oss (29 scored blind rows, no pairs) and Gemini (4 scored rows) on
    the RESULTS.json snapshot: primary readings agree everywhere. Their extra
    readings (s6 eligibility for an empty pair leg / empty H6 group; CP
    fallback for gpt-oss H2 0/8 vs 0/5) are reported, not asserted."""
    assert SD.diverging(model) == []


# ---- (c) the divergences actually observed for Claude -----------------------------

def test_claude_divergence_set(claude):
    """Observed primary divergences for Claude, and why:

    H3  recorded INDETERMINATE, shadow SUPPORTED. On the active subset K is
        4/4 learned in both arms, A 8/10 passive and 9/10 active, so
        (1 - 4/5) - (1 - 9/10) = 1/10 >= 1/10 exactly; the frozen float path
        gives 0.0999... < 0.10 (AUDIT_A F01). One alien (SYS-19722) carries it.
    H4  recorded INDETERMINATE, shadow NOT_SUPPORTED. The PREREG s6 general
        rule applies to H4 (only H3 and H6 have their own rules); every
        blind and reveal false-negative count is 0 (A 0/15, K 0/10), so est
        0 and the bootstrap CI is [0, 0] < 0.05 (AUDIT_A F02). That CI is
        degenerate: under the Clopper-Pearson fallback reading the decision
        is INDETERMINATE again (also asserted below).
    """
    assert SD.diverging("claude") == ["H3", "H4"]
    h3 = _primary(claude, "H3")
    assert (h3["recorded"], h3["decision"]) == ("INDETERMINATE", "SUPPORTED")
    assert h3["inputs"]["diff"] == F(1, 10) and h3["inputs"]["float_diff_as_frozen"] < 0.10
    h4 = _primary(claude, "H4")
    assert (h4["recorded"], h4["decision"]) == ("INDETERMINATE", "NOT_SUPPORTED")
    assert h4["inputs"]["ci95_boot"] == (0, 0)
    cp = [r for r in claude["readings"]["H4"] if r["label"].startswith("s6_rule+CP_fallback/code_predicates")]
    assert cp and cp[0]["decision"] == "INDETERMINATE"


def test_claude_degenerate_ci_and_alternative_readings(claude):
    """Non-primary readings AUDIT_A predicted, now measured exactly:
    - H2: bootstrap CI [0,0] is degenerate; CP upper for A 0/32 = 0.1089 >
      0.075, so the CP reading is INDETERMINATE (F04). With all 40 aliens
      (one ADV RANDOM) the estimate is 1/40 > 0 -> INDETERMINATE.
    - Detector: standard aliens on both legs (AUC 157/160, pairs 19/22) ->
      VALIDATED; all aliens on both legs (pairs 23/30) -> NOT_VALIDATED (F03).
    """
    h2 = {r["label"]: r for r in claude["readings"]["H2"]}
    assert h2["A=standard(32)"]["inputs"]["ci95_boot"] == (0, 0)
    cpr = h2["A=standard(32)+CP_fallback"]
    assert cpr["decision"] == "INDETERMINATE" and cpr["inputs"]["cp_A"][1] > F(3, 40)
    assert h2["A=all aliens(40)"]["decision"] == "INDETERMINATE"
    assert claude["summary"]["H2"]["degenerate_ci"]
    det = {r["label"].split(" ")[0]: r for r in claude["readings"]["DETECTOR"]}
    assert det["consistent_standard"]["decision"] == "NOVELTY_DETECTOR_VALIDATED"
    assert det["consistent_standard"]["inputs"]["pair_acc"] == F(19, 22)
    assert det["consistent_all"]["decision"] == "NOVELTY_DETECTOR_NOT_VALIDATED"
    assert det["literal_code"]["inputs"]["pair_acc"] == F(23, 30)


def test_cli_prints_table(capsys):
    SD.main(["--model", "claude"])
    out = capsys.readouterr().out
    assert "PRIMARY DIVERGES: H3, H4" in out and "DETECTOR" in out
