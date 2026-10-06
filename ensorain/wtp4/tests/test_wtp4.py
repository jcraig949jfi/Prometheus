import copy

from ensorain.wtp4.axes import AXES, grid
from ensorain.wtp4.families import families
from ensorain.wtp4.habit import classify
from ensorain.wtp4.score4 import cell_label


def _u(**rates):
    return dict(status="OK", rates=rates)


def test_classify_cheap_first():
    base = dict(random=0.1, frozen=0.1, oracle=1.1)
    assert classify(_u(**base, constant=0.1, lowrank=0.12))["label"] == "DEAD"
    assert classify(_u(**base, table=0.5, lowrank=0.55))["label"] == "CHEAP_PAYS"       # struct must beat cheap by the margin
    assert classify(_u(**base, table=0.5, lowrank=0.7))["label"] == "STRUCT_PAYS"
    assert classify(_u(random=0.5, frozen=0.5, oracle=0.51, table=0.9))["label"] == "INFO_VALUELESS"
    assert classify(dict(status="ILLEGAL"))["label"] == "ILLEGAL"


def test_cell_label_conservative():
    assert cell_label(["STRUCT_PAYS", "CHEAP_PAYS"]) == "CHEAP_PAYS"
    assert cell_label(["STRUCT_PAYS", "DEAD"]) == "SPLIT"
    assert cell_label(["DEAD", "INFO_VALUELESS"]) == "DEAD"
    assert cell_label(["DEAD", "ILLEGAL"]) == "ILLEGAL"
    assert cell_label(["TRAPPED", "TRAPPED"]) == "TRAPPED"
    assert cell_label(["TRAPPED", "DEAD"]) == "DEAD"
    trapped = dict(status="OK", rates=dict(random=0.1, frozen=0.1, oracle=None), lives=dict(oracle=dict(why="topology")))
    assert classify(trapped)["label"] == "TRAPPED"


def test_axes_move_one_gene_only():
    g = families()[0]["g"]
    for ax, lab, f in grid():
        h = f(g)
        diff = [law for law in g if g[law] != h[law]]
        assert len(diff) <= (2 if ax == "topology" else 1), (ax, lab, diff)   # topology: coupled oneway = 0
        assert g == families()[0]["g"]          # transform does not mutate its input


def test_families_rule():
    F = families()
    assert len(F) == 12 and sum(len(f["lineages"]) for f in F) == 13
    assert len({tuple(f["key"]) for f in F}) == 12
    assert len(grid()) == 1 + sum(len(v[1]) for v in AXES.values()) == 54
