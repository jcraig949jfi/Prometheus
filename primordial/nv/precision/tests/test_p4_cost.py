"""P4: cost cells -- the oracle runs before timing, and no speed number is VALID without the lease."""
import pytest

torch = pytest.importorskip("torch")

from primordial.nv.precision import p4_cost as P4  # noqa: E402

needs_cuda = pytest.mark.skipif(not torch.cuda.is_available(), reason="needs cuda")


def test_speed_status_rules():
    assert P4.speed_status(None, 0, True) == "INDETERMINATE"                     # no lease
    assert P4.speed_status({"lost": True}, 0, True) == "INDETERMINATE"           # lease lost
    assert P4.speed_status({"lost": False}, 80, True) == "INDETERMINATE"         # contended GPU
    assert P4.speed_status({"lost": False}, None, True) == "INDETERMINATE"       # util unknown
    assert P4.speed_status({"lost": False}, 3, False) == "INDETERMINATE"         # oracle failed
    assert P4.speed_status({"lost": False}, 3, True) == "VALID"


@needs_cuda
def test_no_lease_run_rows_are_well_formed_and_indeterminate():
    rows = P4.run([64], reps=2, no_lease=True, families=("linear", "tt_feat"), precisions=("fp32", "int8"))
    assert len(rows) == 4
    for r in rows:
        assert r["speed_status"] == "INDETERMINATE" and r["lease"] is False
        assert r["oracle_ok"], r
        assert len(r["t_s"]) == 2 and r["median_s"] > 0
        assert r["vram_peak_bytes"] >= 0 and r["param_bytes"] > 0
    by = {(r["family"], r["precision"]): r for r in rows}
    assert by[("linear", "int8")]["substrate"] == "int8_intmm"
    assert by[("linear", "int8")]["param_bytes"] < by[("linear", "fp32")]["param_bytes"]
