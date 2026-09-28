"""Known-answer tests for the pre-data LM01 adjudication (G1-G9)."""
from ensorain.lm01.tests.test_lm01_analysis import mk, DEV
from ensorain.arc3.lm01_adjudicate import adjudicate_stratum


def _with(rows, n1):
    for r in rows:
        r["N1"] = n1
        r["ladder"]["random|full"]["B"] = 1000
    return rows


def test_G1_gates_unlearnable_headline_pair():
    a = adjudicate_stratum(_with(mk(), n1=2.4), DEV, .3, "F2_latent")["adjudicated"]
    assert a["headline"].startswith("UNTESTED")
    b = adjudicate_stratum(_with(mk(), n1=0.0), DEV, .3, "F2_latent")["adjudicated"]
    assert isinstance(b["headline"], dict)


def test_G9b_all_eviction_labels_gated_on_E6():
    rows = _with(mk(sel={"c/4": 0.1}, rungs=(0.3, 0.6, 1.0, 1.5, 2.0)), n1=0.0)
    a = adjudicate_stratum(rows, dict(DEV, posctl_pass=False), .3, "F3_switch")["adjudicated"]
    assert a["eviction"]["c/4"]["adjudicated"].startswith("UNRESOLVED")
    b = adjudicate_stratum(rows, DEV, .3, "F3_switch")["adjudicated"]
    assert b["eviction"]["c/4"]["adjudicated"] == "RANDOM_BEATS_HEURISTIC"       # G4 relabel


def test_G5_headroom_gate():
    rows = _with(mk(sel={}, rungs=(0.3, 0.6, 1.0, 2.45, 2.5)), n1=0.0)     # random@c within DELTA of full
    a = adjudicate_stratum(rows, DEV, .3, "F2_latent")["adjudicated"]
    assert a["eviction"]["c"]["adjudicated"].startswith("UNTESTED (no headroom")


def test_G3_secondary_bytes_only():
    a = adjudicate_stratum(_with(mk(s_ladder=3.0), n1=0.0), DEV, .3, "F2_latent")["adjudicated"]
    assert a["secondary_bytes_only"]["label"] == "SELECTIVE_ADVANTAGE"


def test_G9h_monotone_bstar():
    rows = _with(mk(rungs=(2.45, 1.0, 2.45, 2.5, 2.5)), n1=0.0)            # non-monotone: c/8 equivalent, c/4 not
    a = adjudicate_stratum(rows, DEV, .3, "F2_latent")["adjudicated"]
    assert a["headline"]["B_star_LR_monotone"] == "c/2"
