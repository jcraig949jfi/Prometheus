"""Known-answer tests for the frozen verdict analysis v0.3.2 (method rule: every readout passes a fixture)."""
import numpy as np

from ensorain.lm01.analysis import stratum

RUNGS = ["c/8", "c/4", "c/2", "c", "2c"]


def mk(n=16, lr=2.5, rungs=(0.3, 0.6, 1.0, 1.5, 2.0), warm=2.5, lk=0.0, sel=None, fifo=None, dual=None, s_ladder=1.0,
       l_ac=2.5, gap=0.1, n1=0.0, oracle=1.5, random_pc=0.2, clamped=False, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        e = lambda: rng.normal(0, 0.05)
        met = dict(record_reads=1000, query_ops=10, ops=100, peak_persistent=1000)
        loci = dict(stored_record_bytes=100, hypothesis_bytes=10, transient_hypothesis_bytes=0)
        lad = {"L-R|full": dict(AC=lr + e(), meter=met, loci=loci), "random|full": dict(AC=warm + e(), meter=met, loci=loci)}
        for g, v in zip(RUNGS, rungs):
            lad[f"random|{g}"] = dict(AC=v + e(), meter=met, loci=loci)
            if sel is not None:
                lad[f"keep_worst|{g}"] = dict(AC=sel.get(g, v) + e(), meter=met, loci=loci)
            if g in ("c/4", "c"):
                lad[f"fifo|{g}"] = dict(AC=(fifo or {}).get(g, v) + e(), meter=met, loci=loci)
        dl = {g: dict(clamped=clamped, runs=[dict(AC=(dual or {}).get(g, v) + e()) for _ in range(3)])
              for g, v in zip(RUNGS, rungs) if g in ("c/4", "c")}
        smet = dict(record_reads=500, query_ops=10, ops=100, peak_persistent=100)
        arms = {"L-K": dict(AC=lk + e()),
                "LOSSLESS": dict(label="L-R-r3", AC=l_ac + e(), meter=dict(peak_persistent=1000, record_reads=1000)),
                "HYBRID": dict(AC=1.0, ablation=dict(gap=gap + e())),
                "SELECTIVE_LADDER": dict(label="S-cp", ladder={"128": dict(AC=s_ladder + e(), meter=smet)})}
        rows.append(dict(status="OK", level="L2", N1=n1, cells=512, ladder=lad, dual=dl, arms=arms,
                         posctl=dict(oracle=oracle + e(), random=random_pc + e())))
    return rows


DEV = dict(frame="TESTABLE", posctl_pass=True, visits_per_cell=3.0)
FIX = dict(headline_pc={"L2": True}, ablation_pc=True)


def S(rows, dev=DEV, d=.3, fam="F2_latent", fix=FIX):
    return stratum(rows, dev, d, fam, fix)


def test_transient_contraction_when_LR_beats_every_rung_and_LK_fails():
    v = S(mk())
    assert v["headline"]["label"] == "LOSSLESS_TRANSIENT_CONTRACTION" and v["firings"] == []
    assert "replication" in v["headline"]


def test_countermodel_when_LK_equivalent_to_LR():
    v = S(mk(lk=2.5))
    assert v["headline"]["label"] == "COUNTERMODEL_SIGNAL" and v["firings"][0]["falsifier"] == "F-B"


def test_G1_headline_pair_not_learnable():
    assert S(mk(n1=2.4))["headline"]["label"] == "UNTESTED_HEADLINE_NOT_LEARNABLE"


def test_headline_positive_control_failure():
    v = S(mk(rungs=(0.3, 0.6, 1.0, 2.45, 2.45)), fix=dict(headline_pc={"L2": False}, ablation_pc=True))
    assert v["headline"]["label"] == "UNRESOLVED_INSTRUMENT_CANNOT_FIRE"


def test_bounded_suffices_monotone_and_reported_without_weight():
    v = S(mk(rungs=(2.45, 0.6, 2.45, 2.5, 2.5)))           # non-monotone: c/8 equivalent, c/4 not
    assert v["headline"]["B_star_LR"] == "c/2" and v["headline"]["label"] == "UNRESOLVED"
    assert v["headline"]["reported"] == "BOUNDED_SUFFICES" and v["firings"] == []


def test_eviction_labels_v032():
    base = dict(rungs=(0.3, 0.6, 1.0, 1.5, 2.0))
    ev = lambda **kw: S(mk(**base, **kw))["eviction"]["at"]["c/4"]["label"]
    assert ev(sel={"c/4": 1.2}, dual={"c/4": 1.2}) == "HEURISTIC_BUYS_BYTES"
    assert ev(sel={"c/4": 1.2}, dual={"c/4": 0.6}) == "HEURISTIC_ADVANTAGE"
    assert ev(sel={"c/4": 1.2}, fifo={"c/4": 1.2}, dual={"c/4": 0.6}) == "RECENCY"
    assert ev(sel={"c/4": 0.1}) == "RANDOM_BEATS_HEURISTIC"
    assert ev(sel={}) == "HEURISTIC_EQUIVALENT_TO_RANDOM"
    assert ev(sel={"c/4": 1.2}, dual={"c/4": 1.2}, clamped=True) == "UNRESOLVED_UNMATCHED"


def test_every_eviction_label_gated_on_campaign_E6():
    v = S(mk(sel={"c/4": 0.1}, oracle=0.2))
    assert all(a["label"] == "UNRESOLVED_E6" for a in v["eviction"]["at"].values()) and v["firings"] == []


def test_headroom_gate():
    v = S(mk(sel={}, rungs=(0.3, 0.6, 1.0, 2.45, 2.5)))     # random@c within DELTA of the full store
    assert v["eviction"]["at"]["c"]["label"] == "UNTESTED_NO_HEADROOM"


def test_equivalence_needs_ci_not_noise():
    rows = mk(sel={}, rungs=(0.3, 0.6, 1.0, 1.5, 2.0), n=4)
    for i, r in enumerate(rows):
        r["ladder"]["keep_worst|c/4"]["AC"] += (-1) ** i * 2.0
    assert S(rows)["eviction"]["at"]["c/4"]["label"] == "UNRESOLVED"


def test_F_C_firing_carries_pending_replication():
    v = S(mk(sel={}))
    f = [x for x in v["firings"] if x["falsifier"].startswith("F-C@c/4")]
    assert f and f[0]["replication"]["status"].startswith(("PENDING_REPLICATION", "UNREPLICATED"))


def test_secondary_common_read_convention():
    v = S(mk(s_ladder=3.0, gap=1.0))
    assert v["secondary"]["label"] == "SELECTIVE_ADVANTAGE" and v["supports_pending_replication"][0]["label"] == "SELECTIVE_ADVANTAGE"
    assert v["hybrid"]["label"] == "HYBRID_REQUIRED"
    rows = mk(s_ladder=3.0)
    for r in rows:
        r["arms"]["SELECTIVE_LADDER"]["ladder"]["128"]["meter"]["record_reads"] = 5000   # more reads than LOSSLESS
    assert S(rows)["secondary"]["label"] == "UNRESOLVED"


def test_index_not_required_needs_equivalence_and_pc():
    assert S(mk(gap=0.0))["hybrid"]["label"] == "INDEX_NOT_REQUIRED"
    assert S(mk(gap=0.0), fix=dict(headline_pc={"L2": True}, ablation_pc=False))["hybrid"]["label"] == "UNRESOLVED"


def test_curves_emitted_even_when_untested():
    v = S(mk(), dev=dict(DEV, frame="UNTESTED"))
    assert v["label"] == "UNTESTED" and "random|c/4" in v["curves"]


def test_F1_never_headline_never_fires():
    v = S(mk(lk=2.5), fam="F1_episodic")
    assert v["firings"] == [] and v["supports_pending_replication"] == [] and v["role"].startswith("F1_BRANCH_TRIGGER")
    assert v["lossless_must_win"] is True


def test_win_rule_uses_bounded_rungs_only():                 # diff #16: 2c is reported, not in the WIN rule
    v = S(mk(rungs=(0.3, 0.6, 1.0, 1.5, 2.45)))
    assert v["headline"]["label"] == "LOSSLESS_TRANSIENT_CONTRACTION"
    assert "2c" in v["headline"]["LR_minus_rung"]


def test_R1_win_rule_needs_rungs_above_floor():             # pre-freeze review R1
    v = S(mk(rungs=(-0.5, -0.3, -0.2, -0.1, 2.0), n1=0.0))
    assert v["headline"]["label"] != "LOSSLESS_TRANSIENT_CONTRACTION"


def test_R3_v031_set_label_is_descriptive():
    v = S(mk(rungs=(0.3, 0.6, 1.0, 1.5, 2.45)))
    assert v["headline"]["label"] == "LOSSLESS_TRANSIENT_CONTRACTION" and v["headline"]["v031_set_label"] == "not_firing"


def test_recency_attribution_is_symmetric():
    v = S(mk(sel={"c/4": 0.1}, fifo={"c/4": 0.1}, rungs=(0.3, 0.6, 1.0, 1.5, 2.0)))
    assert v["eviction"]["at"]["c/4"]["label"] == "RECENCY_LOSES"
    assert not [f for f in v["firings"] if "@c/4" in f["falsifier"]]


def test_suffstat_reported_only_never_a_candidate():
    rows = mk(sel={"c/4": 0.1})
    for r in rows:
        r["ladder"]["SUFFSTAT|table"] = dict(AC=2.5, meter=r["ladder"]["L-R|full"]["meter"], loci=r["ladder"]["L-R|full"]["loci"])
    v = S(rows)
    assert v["eviction"]["candidate"] == "keep_worst" and "suffstat_minus_LR" in v["headline"]


def test_R4_missing_fixtures_fail_loudly(tmp_path):
    import pytest
    from ensorain.lm01.analysis import analyse
    with pytest.raises(FileNotFoundError):
        analyse(str(tmp_path), fixtures_path=str(tmp_path / "nope.json"))
