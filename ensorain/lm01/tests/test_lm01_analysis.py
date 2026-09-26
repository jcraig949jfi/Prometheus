"""Known-answer tests for the frozen verdict analysis (method rule: every readout passes a fixture)."""
import numpy as np

from ensorain.lm01.analysis import stratum

RUNGS = ["c/8", "c/4", "c/2", "c", "2c"]


def mk(n=16, lr=2.5, rungs=(0.3, 0.6, 1.0, 1.5, 2.0), warm=2.5, lk=0.0, sel=None, rnd=None, dual=None, s_ladder=1.0,
       l_ac=2.5, gap=0.1, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        e = lambda: rng.normal(0, 0.05)
        lad = {"L-R|full": dict(AC=lr + e()), "random|full": dict(AC=warm + e())}
        for g, v in zip(RUNGS, rungs):
            lad[f"random|{g}"] = dict(AC=v + e())
            if sel is not None:
                lad[f"keep_worst|{g}"] = dict(AC=sel.get(g, v) + e())
        dl = {g: dict(runs=[dict(AC=(dual or {}).get(g, (rnd or {}).get(g, v)) + e()) for _ in range(3)])
              for g, v in zip(RUNGS, rungs) if g in ("c/4", "c")}
        mem = dict(peak_persistent=100, bytes_read=100)
        arms = {"L-K": dict(AC=lk + e()), "LOSSLESS": dict(label="L-R-r3", AC=l_ac + e(), meter=dict(peak_persistent=1000, bytes_read=1000)),
                "HYBRID": dict(AC=1.0, ablation=dict(gap=gap + e())),
                "SELECTIVE_LADDER": dict(label="S-cp", ladder={"128": dict(AC=s_ladder + e(), meter=mem)})}
        rows.append(dict(status="OK", ladder=lad, dual=dl, arms=arms))
    return rows


DEV = dict(frame="TESTABLE", posctl_pass=True, n_rep=8, replicable=True, visits_per_cell=3.0)


def test_transient_contraction_when_LR_beats_every_rung_and_LK_fails():
    v = stratum(mk(), DEV, 0.3)
    assert v["headline"]["label"] == "LOSSLESS_TRANSIENT_CONTRACTION" and v["firings"] == []


def test_countermodel_when_LK_equivalent_to_LR():
    v = stratum(mk(lk=2.5), DEV, 0.3)
    assert v["headline"]["label"] == "COUNTERMODEL_SIGNAL" and "F-B" in v["firings"]


def test_bounded_suffices_is_reported_without_weight():
    v = stratum(mk(rungs=(0.3, 0.6, 2.45, 2.5, 2.5)), DEV, 0.3)
    assert v["headline"]["B_star_LR"] == "c/2" and v["headline"]["label"] == "UNRESOLVED"
    assert v["headline"]["reported"] == "BOUNDED_SUFFICES" and v["firings"] == []


def test_eviction_labels():
    base = dict(rungs=(0.3, 0.6, 1.0, 1.5, 2.0))
    assert stratum(mk(sel={"c/4": 1.2, "c": 2.1}, dual={"c/4": 1.2, "c": 2.1}, **base), DEV, .3)["eviction"]["at"]["c/4"]["label"] == "SELECTIVE_BUYS_BYTES"
    assert stratum(mk(sel={"c/4": 1.2}, dual={"c/4": 0.6}, **base), DEV, .3)["eviction"]["at"]["c/4"]["label"] == "RESERVOIR_SELECTIVE_ADVANTAGE"
    v = stratum(mk(sel={"c/4": 0.1}, **base), DEV, .3)
    assert v["eviction"]["at"]["c/4"]["label"] == "RANDOM_BEATS_SELECTIVE"
    eq = stratum(mk(sel={}, **base), DEV, .3)
    assert eq["eviction"]["at"]["c/4"]["label"] == "INDISCRIMINATE_EQUIVALENT" and "F-C" in eq["firings"]
    nopc = stratum(mk(sel={}, **base), dict(DEV, posctl_pass=False), .3)
    assert nopc["eviction"]["at"]["c/4"]["label"] == "UNRESOLVED"          # equality without a positive control


def test_equivalence_needs_ci_not_noise():
    rows = mk(sel={}, rungs=(0.3, 0.6, 1.0, 1.5, 2.0), n=4)
    for i, r in enumerate(rows):                                   # a very noisy selective arm: huge CI
        r["ladder"]["keep_worst|c/4"]["AC"] += (-1) ** i * 2.0
    assert stratum(rows, DEV, .3)["eviction"]["at"]["c/4"]["label"] == "UNRESOLVED"


def test_secondary_and_hybrid():
    v = stratum(mk(s_ladder=3.0, gap=1.0), DEV, .3)
    assert v["secondary"]["label"] == "SELECTIVE_ADVANTAGE" and v["supports_pending_replication"] == ["SELECTIVE_ADVANTAGE"]
    assert v["hybrid"]["label"] == "HYBRID_REQUIRED"


def test_untested_gate():
    assert stratum(mk(), dict(DEV, frame="UNTESTED"), .3)["label"] == "UNTESTED"
