"""E-R6-3: the dispatch surface reads committed rows only, marks missing cells UNMEASURED, never interpolates."""
from __future__ import annotations

from primordial.nv import dispatch_surface as DS


def _t(backend, wall, threads=None, **kw):
    r = {"kind": "timing", "status": "record", "exactness": "PASS", "speed_status": "VALID", "backend": backend,
         "wall_s": wall, **kw}
    if threads is not None:
        r["threads"] = threads
    return r


def test_gpu1_winner_unmeasured_threads_and_invalid_rows_ignored():
    rows = [_t("numba_t1", 0.004, 1), _t("numba_t8", 0.001, 8),
            _t("warp_cuda", 0.002, kernel_s=0.0015, h2d_s=0.0005),
            dict(_t("numba_t2", 0.0001, 2), speed_status="INVALID")]           # an invalid row is not a measurement
    cells = DS.gpu1_cells({4096: rows}, [])
    by_k = {c["threads"]: c for c in cells}
    assert by_k[1]["winner"] == "warp_cuda" and abs(by_k[1]["ratio"] - 2.0) < 1e-12
    assert by_k[8]["winner"] == "numba_t8"
    assert by_k[2]["status"] == "UNMEASURED" and by_k[4]["status"] == "UNMEASURED"
    assert all(c["status"] != "MEASURED_COMPOSITE" for c in cells)             # no warm h2d at 4096 -> no composite


def test_gpu1_composite_only_where_d52_has_a_warm_median():
    rows = [_t("numba_t8", 0.010, 8), _t("warp_cuda", 0.037, kernel_s=0.0033, h2d_s=0.034)]
    d52 = [_t("h2d_alloc", 0.0051, batch_size=65536), _t("h2d_alloc", 0.0082, batch_size=131072)]
    cells = [c for c in DS.gpu1_cells({65536: rows}, d52) if c["threads"] == 8]
    single, comp = cells
    assert single["winner"] == "numba_t8" and comp["status"] == "MEASURED_COMPOSITE"
    assert comp["winner"] == "warp_cuda_composite" and abs(comp["wall_s"] - 0.0084) < 1e-12


def test_committed_tables_build_and_every_cell_has_a_status():
    doc = DS.build()
    assert doc["cells"] and all(c["status"] in ("MEASURED", "MEASURED_COMPOSITE", "UNMEASURED") for c in doc["cells"])
    assert {c["batch"] for c in doc["cells"] if c["question"] == "GPU-1"} == {1024, 4096, 16384, 65536}
    assert "UNMEASURED regions" in DS.markdown(doc)
