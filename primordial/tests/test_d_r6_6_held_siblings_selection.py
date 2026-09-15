"""D-R6-6: n-scaled decision rule, gate decode and archive index per cell (re-reads are the job's, after the predicate)."""
from primordial.cohorts.d import r6_4_held_w13_train8_selection as R4
from primordial.cohorts.d import r6_6_held_siblings_selection as D
from primordial.qd import e7_run as E7


def test_decide_n_matches_r6_4_at_8():
    t, f = True, False
    cases = [([f] * 5 + [t] * 3, [t] * 8), ([t] * 6 + [f] * 2, [t] * 5 + [f] * 3), ([t] * 8, [t] * 2 + [f] * 6),
             ([t] * 8, [t] * 4 + [f] * 4), ([t] * 4 + [f] * 4, [t] * 8)]
    for reach, held in cases:
        assert D.decide_n(t, t, reach, held) == R4.decide(t, t, reach, held)


def test_decide_n_scales_to_16_and_refuses_small():
    t, f = True, False
    assert D.decide_n(t, t, [t] * 10 + [f] * 6, [t] * 10 + [f] * 6) == "SELECTION"
    assert D.decide_n(t, t, [t] * 6 + [f] * 10, [f] * 16) == "SEARCH_SHORT"
    assert D.decide_n(t, t, [t] * 7, [t] * 7) == "INDETERMINATE"


def test_cells_decode_and_have_saved_runs():
    text = (R4.ROOT / R4.SRC_ROWS).read_text(encoding="utf-8")
    for c in D.CELLS:
        g7 = E7.G7(c["gs"], "linear")
        (W, b), C = g7.unpack(R4.gate_genome(g7, c["gate"]))
        assert int((W != 0).sum()) == 1 and list(C[0, 1]) == c["gate"]["act"]
        assert len(R4.runs_from_rows(text, c["gs"], c["pressure"])) >= 8
