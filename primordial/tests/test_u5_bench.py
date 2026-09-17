"""U5/U6 bench harness: the cells refuse speed unless every path is exact, the timed restore
path is itself exact, and the VRAM budget is labelled as an extrapolation."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("redis")
pytest.importorskip("numba")
if not torch.cuda.is_available():
    pytest.skip("no CUDA", allow_module_level=True)

from primordial.nv.cudagraph import bench  # noqa: E402


@pytest.mark.parametrize("fam", ["linear", "tt_digits"])
def test_throughput_cell_is_exact_before_speed(fam):
    r = bench.throughput_cell(fam, 64, reps=1)
    assert r["exact"] == {"graph_k1": True, "graph_kT": True, "graph_k1_restore_path": True,
                          "torch_eager_vs_b6": True}
    assert set(r["wall_s"]) == {"torch_eager", "graph_k1", "graph_kT", "b6_numba"}
    assert "speed_verdict" not in r


def test_vram_cells_and_budget_rows():
    rows = [bench.vram_cell("linear", n, K) for n in (64, 256) for K in (1, None)]
    assert all(r["fits"] and r["peak_alloc_bytes"] > 0 for r in rows)
    assert {r["ticks_per_graph"] for r in rows} == {1, rows[1]["T"]}
    b = bench.budget(rows)
    assert len(b) == 2 and all(x["method"].startswith("linear extrapolation") for x in b)
    assert all(x["fit_from_envs"] == [64, 256] for x in b)
