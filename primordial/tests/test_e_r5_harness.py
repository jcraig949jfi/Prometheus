"""E-R5-3: GPU-1..3 wiring contract (the GPU runs themselves are pilot jobs through primordial.nv.gpuq)."""
from __future__ import annotations

import subprocess
import sys

from primordial.nv import gpuq as GQ
from primordial.nv import r5_harness as H


def test_module_import_loads_no_numba_torch_or_warp():
    code = ("import sys; import primordial.nv.r5_harness; "
            "print(','.join(m for m in ('numba', 'torch', 'warp') if m in sys.modules))")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
    assert out.returncode == 0 and out.stdout.strip() == ""


def test_timing_rows_carry_every_measurement_field_the_arbiter_requires():
    assert tuple(H.MEASURE) == tuple(GQ.MEASURE_FIELDS)
    row = H.timing_row("GPU-1", "warp_cuda", 0.5, 1024.0, 1, "warm", "numba_t4", "PASS", h2d_s=0.01)
    assert row["kind"] == "timing" and all(f in row for f in GQ.MEASURE_FIELDS)
    assert row["batch_size"] == 1024 and row["transfer_included"] is True and row["h2d_s"] == 0.01


def test_jobs_accept_the_child_checkpoint_argument_and_venvs_exist_by_name():
    import inspect
    for fn, venv in ((H.gpu1_cell, "w"), (H.gpu2_cell, "u"), (H.gpu3_cell, "p")):
        assert "checkpoint_path" in inspect.signature(fn).parameters
        assert GQ.venv_python(venv).replace("\\", "/").endswith(f"nv-venv-{venv}/Scripts/python.exe")
    assert H.THREADS == (1, 2, 4, 8)
