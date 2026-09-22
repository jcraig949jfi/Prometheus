"""R8 Route B bound: the four PENDING cells resolve, and the bound is not vacuous (w13 with its learner withheld
must stay UNRESOLVED -- a learner result exists that makes it SURVIVED)."""
from primordial.metric import route_b as RB

W13 = (13, "train128_held64")


def test_four_pending_cells_are_survival_impossible_under_every_variant():
    doc = RB.build()
    assert doc["unresolved"] == []
    assert len(doc["resolved"]) == 4
    for c in doc["cells"]:
        assert c["problems"] == []
        assert c["baseline_sample"] == {"runs_total": 32, "rng_family_count": 4, "runs_per_family": 8}
        for v in c["variants"].values():
            assert v["impossible"] and "SURVIVED" not in v["verdicts_reachable"]


def test_planted_survivable_cell_is_not_resolved():
    fl, base, lrn = RB.committed_rows((W13,))[W13]
    assert lrn is not None                      # w13's learner is committed; withhold it
    out = RB.bound(fl, base, None)
    assert out["status"] == "UNRESOLVED"
    act = out["variants"][out["active_variant"]]
    assert not act["impossible"] and "SURVIVED" in act["verdicts_reachable"]


def test_committed_learner_is_flagged():
    fl, base, lrn = RB.committed_rows((W13,))[W13]
    assert RB.bound(fl, base, lrn)["status"] == "ERROR"
