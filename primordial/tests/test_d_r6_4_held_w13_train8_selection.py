"""D-R6-4: decision rule, gate genome shape and the source rows (archive re-reads are the job's, after the predicate)."""
import numpy as np

from primordial.cohorts.d import r6_4_held_w13_train8_selection as D
from primordial.qd import e7_run as E7


def test_decide():
    t, f = True, False
    assert D.decide(t, t, [f] * 5 + [t] * 3, [t] * 8) == "SEARCH_SHORT"
    assert D.decide(t, t, [t] * 6 + [f] * 2, [t] * 5 + [f] * 3) == "SELECTION"
    assert D.decide(t, t, [t] * 8, [t] * 2 + [f] * 6) == "OVERFIT_ONLY"
    assert D.decide(t, t, [t] * 8, [t] * 4 + [f] * 4) == "MIXED"
    assert D.decide(t, t, [t] * 4 + [f] * 4, [t] * 8) == "MIXED"
    assert D.decide(f, t, [t] * 8, [t] * 8) == "INDETERMINATE"
    assert D.decide(t, f, [t] * 8, [t] * 8) == "INDETERMINATE"


def test_gate_genome_decodes_to_one_weight_and_act():
    g7 = E7.G7(D.GS, "linear")
    raw = D.gate_genome(g7)
    assert raw.shape == (1, g7.glen)
    (W, b), C = g7.unpack(raw)
    assert int((W != 0).sum()) == 1 and W[0, D.GATE["feat"], 1] == D.GATE["dir"]
    assert b[0, 0] == 0 and (b[0, 2:] == -1e3).all() and list(C[0, 1]) == D.GATE["act"] and not C[0, 0].any()


def test_runs_from_rows_finds_8_saved_archives():
    runs = D.runs_from_rows((D.ROOT / D.SRC_ROWS).read_text(encoding="utf-8"))
    assert [x["run_seed"] for x in runs] == list(range(8))
    assert all(x["elites"] for x in runs)
