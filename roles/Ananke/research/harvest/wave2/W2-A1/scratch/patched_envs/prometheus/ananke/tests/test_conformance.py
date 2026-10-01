"""GPU engine vs independent CPU oracle: bit-identical state (DESIGN.md s9).

The oracle (oracle.py) was written from DESIGN.md by a separate author
who never read engine.py, so agreement here is two implementations of
the spec agreeing, not one implementation agreeing with itself.
Also: eager == CUDA-graph, and checkpoint/resume == uninterrupted.
"""
from __future__ import annotations

import importlib.util
import pathlib
import random

import numpy as np
import pytest
import torch

from prometheus.ananke.engine import World, Schedule, Controls
from prometheus.ananke.physics import Physics

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("pte_oracle", HERE.parent / "oracle.py")
oracle = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(oracle)

DEV = "cuda" if torch.cuda.is_available() else "cpu"


def random_physics(seed: int) -> Physics:
    R = random.Random(seed)
    topo = R.choice(["ring", "torus", "random", "smallworld", "global"])
    n = R.choice([9, 16, 25]) if topo in ("torus", "smallworld") else R.choice([5, 12, 20])
    kw = dict(
        topology=topo, n_sites=n, radius=R.choice([1, 2]), k_random=R.choice([2, 3, 5]),
        rewire=R.choice([0, 250, 1000]), state_dim=R.choice([1, 2, 4]),
        payload_width=R.choice([1, 2, 3]), channels=R.choice([1, 2, 3]),
        fanout=R.choice([1, 2, 4]), dest_mode=R.choice(["sample", "all"]),
        loss=R.choice([0.0, 0.25, 1.0]), loss_per_hop=R.choice([0, 1]),
        lat_base=R.choice([0, 1, 3]), lat_hop=R.choice([0, 1]), lat_jitter=R.choice([0, 2]),
        dup=R.choice([0.0, 0.3]), noise=R.choice([0, 7]), cap=R.choice([0, 1, 3]),
        collision=R.choice(["none", "aloha", "saturate"]), decay_shift=R.choice([0, 2]),
        update_mode=R.choice(["sync", "async"]), update_period=R.choice([1, 2]),
        update_p=R.choice([0.5, 1.0]), rules=R.choice([1, 3]), prog_len=R.choice([4, 9]),
        plastic_route=R.choice([0, 1]), adapt_shift=R.choice([0, 3]), wimm=R.choice([0, 1]),
        setrule=R.choice([0, 1]), mut_site=R.choice([0.0, 0.2]),
        e_income=R.choice([0, 3]), e_max=R.choice([10, 1000]), c_emit=R.choice([0, 2]),
        c_op=R.choice([0, 1]), c_mem=R.choice([0, 1]), topo_seed=R.randrange(2 ** 32))
    if topo == "global":
        kw["dest_mode"] = "sample"
    return Physics(**kw)


def random_inputs(ph: Physics, B: int, T: int, seed: int):
    g = np.random.default_rng(seed)
    gen = g.integers(0, 256, size=(B, ph.rules, ph.prog_len, 5))
    gen[..., 4] = g.integers(-128, 128, size=gen.shape[:-1])
    # bias toward emission so transport is exercised: some programs write O.emit
    ws = [int(x) for x in g.integers(0, 2 ** 32, size=B)]
    sense = g.integers(-400, 401, size=(T, B, ph.n_sites)) * (g.random((T, B, ph.n_sites)) < 0.3)
    return gen, ws, sense.astype(np.int64)


def dense_schedule(sense: np.ndarray, B: int, N: int) -> Schedule:
    idx = torch.arange(N, dtype=torch.int64)[None].expand(B, N).clone()
    return Schedule(idx, torch.as_tensor(sense, dtype=torch.int32), idx.clone())


def compare(ph: Physics, B: int, T: int, seed: int, graph: bool):
    gen, ws, sense = random_inputs(ph, B, T, seed)
    ref = oracle.run(ph.to_dict(), gen, ws, sense, T)
    w = World(ph, gen, ws, device=DEV, schedule=dense_schedule(sense, B, ph.n_sites))
    w.run(T, graph=graph)
    got = {k: v.cpu().numpy().astype(np.int64) for k, v in w.state_arrays().items()}
    for k in ("S", "E", "r", "Kp", "Acc_sum", "Acc_cnt", "Msum", "Mcnt"):
        assert np.array_equal(got[k], np.asarray(ref[k], dtype=np.int64)), (k, ph)
    if w.R:
        assert np.array_equal(got["w"], np.asarray(ref["w"], dtype=np.int64)), ("w", ph)
    assert np.array_equal(w.trace.cpu().numpy(), np.asarray(ref["S0_trace"])), ("trace", ph)
    st = ref["stats"]
    tot = lambda k: int(np.sum(st[k]))
    assert int(w.stats["attempted"].sum()) == tot("emitted") + tot("dup")
    for k in ("delivered", "lost", "collided"):
        assert int(w.stats[k].sum()) == tot(k), (k, ph)
    return int(w.stats["delivered"].sum())


@pytest.mark.parametrize("seed", range(40))
def test_engine_matches_oracle(seed):
    ph = random_physics(seed)
    compare(ph, B=3, T=24, seed=seed, graph=False)


@pytest.mark.skipif(DEV != "cuda", reason="graph replay needs CUDA")
@pytest.mark.parametrize("seed", range(40, 52))
def test_graph_matches_oracle(seed):
    ph = random_physics(seed)
    compare(ph, B=3, T=24, seed=seed, graph=True)


def test_conformance_is_not_vacuous():
    """Cheat check on the test itself: across the suite's configs packets
    must actually be delivered, and a deliberately altered engine
    input must be detected."""
    delivered = sum(compare(random_physics(s), 3, 24, s, graph=False) for s in range(8))
    assert delivered > 50
    ph = random_physics(3)
    gen, ws, sense = random_inputs(ph, 3, 24, 3)
    ref = oracle.run(ph.to_dict(), gen, ws, sense, 24)
    ws2 = list(ws)
    ws2[0] ^= 1  # one bit of one world seed
    w = World(ph, gen, ws2, device=DEV, schedule=dense_schedule(sense, 3, ph.n_sites))
    w.run(24, graph=False)
    same = all(np.array_equal(v.cpu().numpy().astype(np.int64), np.asarray(ref[k], dtype=np.int64))
               for k, v in w.state_arrays().items())
    assert not same, "a flipped seed bit went undetected: the comparison cannot fail"


@pytest.mark.skipif(DEV != "cuda", reason="checkpoint test uses graph path")
def test_checkpoint_resume_identical():
    ph = random_physics(7).replace(update_mode="async", update_p=0.7)
    gen, ws, sense = random_inputs(ph, 4, 30, 7)
    sch = dense_schedule(sense, 4, ph.n_sites)
    a = World(ph, gen, ws, device=DEV, schedule=sch)
    a.run(30)
    b = World(ph, gen, ws, device=DEV, schedule=sch)
    b.run(13)
    ck = b.checkpoint()
    c = World(ph, gen, ws, device=DEV, schedule=sch)
    c.restore(ck)
    c.run(17)
    assert a.digest() == c.digest()
    assert torch.equal(a.trace, c.trace)


def test_controls_touch_only_their_channel():
    """zero_comm must change the outcome of a communicating config, and an
    all-default Controls must not."""
    ph = Physics(topology="torus", n_sites=16, fanout=2, prog_len=6)
    gen = np.zeros((2, 1, 6, 5), dtype=np.int64)
    # emit=1 (O.emit is write index D+4), payload0 := SENSE, S0 := IN_sum[0]
    D, NW = ph.state_dim, ph.n_write()
    sense_reg = NW + ph.channels * ph.payload_width + ph.channels
    gen[:, 0, 0] = (6, D + 4, 0, 0, 1)            # CONST emit = 1
    gen[:, 0, 1] = (1, D + 8, sense_reg, 0, 0)    # MOV pay0 = SENSE
    gen[:, 0, 2] = (2, 0, 0, NW, 0)               # ADD S0 = S0 + IN_sum[0]
    ws = [11, 12]
    sense = np.zeros((10, 2, 16), dtype=np.int64)
    sense[0, :, 5] = 256
    sch = dense_schedule(sense, 2, 16)
    base = World(ph, gen, ws, device=DEV, schedule=sch)
    base.run(10, graph=False)
    same = World(ph, gen, ws, device=DEV, schedule=sch, ctrl=Controls())
    same.run(10, graph=False)
    assert base.digest() == same.digest()
    zc = World(ph, gen, ws, device=DEV, schedule=sch, ctrl=Controls(zero_comm=True))
    zc.run(10, graph=False)
    assert base.digest() != zc.digest()
    assert int(zc.stats["delivered"].sum()) == 0 and int(base.stats["delivered"].sum()) > 0


def forced_emitter_inputs(ph: Physics, B: int, T: int, seed: int):
    """Random programs whose first instruction sets O.emit and whose
    second puts SENSE on the payload, so transport, collisions, loss,
    duplicates and saturation are exercised on every config."""
    gen, ws, sense = random_inputs(ph, B, T, seed)
    D, NW = ph.state_dim, ph.n_write()
    sense_reg = NW + ph.channels * ph.payload_width + ph.channels
    gen[:, :, 0] = (6, D + 4, 0, 0, 1)
    gen[:, :, 1, 0] = 2
    gen[:, :, 1, 1] = D + 8
    gen[:, :, 1, 2] = sense_reg
    gen[:, :, 1, 4] = 0
    sense = np.where(sense != 0, sense, 13)
    return gen, ws, sense


@pytest.mark.parametrize("seed", range(100, 140))
def test_transport_matches_oracle(seed):
    ph = random_physics(seed).replace(cap=random.Random(seed).choice([1, 2, 3]))
    ph = ph.replace(collision="saturate" if seed % 4 < 2 else "aloha")
    B, T = 3, 20
    gen, ws, sense = forced_emitter_inputs(ph, B, T, seed)
    ref = oracle.run(ph.to_dict(), gen, ws, sense, T)
    w = World(ph, gen, ws, device=DEV, schedule=dense_schedule(sense, B, ph.n_sites))
    w.run(T, graph=(DEV == "cuda" and seed % 2 == 0))
    for k, v in w.state_arrays().items():
        assert np.array_equal(v.cpu().numpy().astype(np.int64), np.asarray(ref[k], dtype=np.int64)), (k, ph)
    assert np.array_equal(w.trace.cpu().numpy(), np.asarray(ref["S0_trace"]))
    st = ref["stats"]
    for k in ("delivered", "lost", "collided"):
        assert int(w.stats[k].sum()) == int(np.sum(st[k])), k
    if ph.loss < 1.0 and ph.update_mode == "sync" and ph.update_period == 1 and not ph.economy_on:
        assert int(w.stats["delivered"].sum()) > 0
