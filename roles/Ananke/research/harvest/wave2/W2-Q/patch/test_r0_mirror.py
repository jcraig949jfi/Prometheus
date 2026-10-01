"""Regression test (W2-Q): the actuator's initial rule used as a covariate must be the r0 of the run.
W2-E a1 recomputed r0 from UNMIRRORED world seeds while run() uses mirrored seeds, so odd worlds got
a foreign r0. FAILS with W2Q_PATCHED unset (a1 method), PASSES with W2Q_PATCHED=1 (patched method).
Cheap: builds Worlds without running ticks."""
import os, sys, pathlib
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from q_common import *  # noqa


def a1_r0(ph, g, S, sch, act):
    w0 = World(ph, np.repeat(g[None], len(S), 0), list(S), device="cpu", schedule=sch)
    return w0.r.numpy()[np.arange(len(S)), act]


def patched_r0(run_world, act):
    return run_world.r0.numpy()[np.arange(len(act)), act]


def test_actuator_r0_matches_run():
    r = row("0187372b"); ph, env = spec_of(r); g = genome_of(r)
    S = seeds(H_int(NS, 0x7E57, 1), 32)
    ep = envs.build(ph, env, S)
    w = World(ph, np.repeat(g[None], 32, 0), mirrored(S), device="cpu", schedule=ep.schedule)  # as run() builds it
    act = ep.schedule.read_idx[:, 0].numpy()
    truth = w.r0.numpy()[np.arange(32), act]
    got = patched_r0(w, act) if os.environ.get("W2Q_PATCHED") else a1_r0(ph, g, S, ep.schedule, act)
    assert np.array_equal(got, truth), f"{(got != truth).sum()} of 32 worlds have the wrong r0"
    assert np.array_equal(truth[0::2], truth[1::2]), "mirror partners must share r0"
