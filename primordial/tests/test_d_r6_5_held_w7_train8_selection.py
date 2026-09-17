"""D-R6-5: w7 parameters wire through D-R6-4's reader (archive re-reads are the job's, after the predicate)."""
from primordial.cohorts.d import r6_4_held_w13_train8_selection as R4
from primordial.cohorts.d import r6_5_held_w7_train8_selection as D
from primordial.qd import e7_run as E7


def test_w7_gate_genome_decodes():
    g7 = E7.G7(D.GS, "linear")
    raw = R4.gate_genome(g7, D.GATE)
    (W, b), C = g7.unpack(raw)
    assert g7.W == 3 and int((W != 0).sum()) == 1 and W[0, D.GATE["feat"], 1] == D.GATE["dir"]
    assert list(C[0, 1]) == D.GATE["act"] and not C[0, 0].any()


def test_w7_runs_from_rows_finds_8_saved_archives():
    runs = R4.runs_from_rows((R4.ROOT / R4.SRC_ROWS).read_text(encoding="utf-8"), D.GS, D.PRESSURE)
    assert [x["run_seed"] for x in runs] == list(range(8))


def test_r6_4_defaults_unchanged():
    runs = R4.runs_from_rows((R4.ROOT / R4.SRC_ROWS).read_text(encoding="utf-8"))
    assert all(x["gen_seed"] == 13 and x["pressure"] == "train8_held64" for x in runs) and len(runs) == 8
