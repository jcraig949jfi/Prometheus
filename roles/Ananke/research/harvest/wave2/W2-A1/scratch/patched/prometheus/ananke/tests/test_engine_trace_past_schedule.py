"""H-IMPL regression: engine.World must not overwrite the last scheduled tick's
record when it is run past the end of its Schedule.

engine.py _tick: tv = t.clamp(max=Tsch - 1); trace/emit_trace/census rows are
written with index_copy_ at tv on EVERY tick, so ticks t >= Tsch overwrite row
Tsch - 1 (the last readout). FAILS on the current code, PASSES with
patches/engine_trace_past_schedule.diff. CPU only.
"""
import numpy as np
import torch

from prometheus.ananke import plants
from prometheus.ananke.engine import Schedule, World
from prometheus.ananke.physics import Physics

DEV = "cpu"


def _world(T, census=False):
    ph = Physics(topology="ring", n_sites=8, radius=1, state_dim=1, payload_width=1, channels=1,
                 prog_len=4, dest_mode="all", lat_base=1).validate()
    g = plants.plant("sense_copy", ph)[None].repeat(2, 0)
    g[:, :, 1] = (plants.OPS["CONST"], ph.state_dim + 4, 0, 0, 1)       # emit every tick
    g[:, :, 2] = (plants.OPS["MOV"], ph.state_dim + 8, plants.regmap(ph)["SENSE"], 0, 0)  # PAY0 := SENSE
    sv = torch.zeros(T, 2, 1, dtype=torch.int32)
    sv[T - 1] = 300                                                     # cue on the LAST scheduled tick
    sch = Schedule(torch.zeros(2, 1, dtype=torch.int64), sv, torch.zeros(2, 1, dtype=torch.int64))
    return World(ph, g, [7, 7], device=DEV, schedule=sch, census=census)


def test_trace_last_row_survives_running_past_schedule():
    T = 4
    a = _world(T)
    a.run(T, graph=False)
    b = _world(T)
    b.run(T + 3, graph=False)
    assert a.trace[T - 1, :, 0].tolist() == [300, 300]
    assert torch.equal(a.trace, b.trace), (a.trace[:, :, 0].T, b.trace[:, :, 0].T)
    assert torch.equal(a.tel["emit_trace"], b.tel["emit_trace"])


def test_census_rows_survive_running_past_schedule():
    T = 5
    a = _world(T, census=True)
    a.run(T, graph=False)
    b = _world(T, census=True)
    b.run(T + 2, graph=False)
    for k in a.tel:
        if k.startswith("c_"):
            assert torch.equal(a.tel[k], b.tel[k]), k


def test_within_schedule_is_unchanged():
    """Neutrality: a run that stops at Tsch records every row exactly as a
    tick-by-tick readout of S0 does (the patch touches only t >= Tsch)."""
    T = 6
    w = _world(T)
    rows = []
    for _ in range(T):
        w.step()
        rows.append(w.S[:, 0, 0].clone())
    assert torch.equal(w.trace[:, :, 0], torch.stack(rows))
