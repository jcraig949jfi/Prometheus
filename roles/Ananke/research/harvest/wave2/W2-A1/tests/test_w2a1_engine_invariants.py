"""W2-A1: spec-level invariants of the PTE world (proposed regression tests).

The conformance suite checks engine == oracle; both are written from DESIGN.md, so a property that the
SPEC violates is invisible to it. These tests check properties of the semantics itself.
CPU only. Run from the worktree root:
    CUDA_VISIBLE_DEVICES=-1 OMP_NUM_THREADS=2 python -m pytest -q roles/Ananke/research/harvest/wave2/W2-A1/tests
Tests marked DOCUMENTS assert a KNOWN BREAK of a naive invariant (they pin current semantics).
"""
from __future__ import annotations

import os
import pathlib
import random
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
ROOT = pathlib.Path(__file__).resolve().parents[7]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pytest  # noqa: E402
import torch  # noqa: E402

torch.set_num_threads(2)

from prometheus.ananke import assays, envs, plants, topology  # noqa: E402
from prometheus.ananke.engine import Controls, Schedule, World  # noqa: E402
from prometheus.ananke.physics import Physics, REG_MAX  # noqa: E402

DEV = "cpu"


# ------------------------------------------------------------------ helpers
def rand_physics(seed: int, **over) -> Physics:
    R = random.Random(seed)
    topo = R.choice(["ring", "torus", "random", "smallworld", "global"])
    n = R.choice([16, 25]) if topo in ("torus", "smallworld") else R.choice([12, 20])
    kw = dict(topology=topo, n_sites=n, radius=R.choice([1, 2]), k_random=R.choice([2, 3]),
              rewire=R.choice([0, 250]), state_dim=R.choice([1, 2, 4]), payload_width=R.choice([1, 2]),
              channels=R.choice([1, 2]), fanout=R.choice([1, 2, 4]), dest_mode=R.choice(["sample", "all"]),
              loss=R.choice([0.0, 0.25]), loss_per_hop=R.choice([0, 1]), lat_base=R.choice([1, 3]),
              lat_hop=R.choice([0, 1]), lat_jitter=R.choice([0, 2]), dup=R.choice([0.0, 0.3]),
              noise=R.choice([0, 7]), cap=R.choice([0, 2]), collision=R.choice(["none", "aloha", "saturate"]),
              decay_shift=R.choice([0, 2]), update_mode=R.choice(["sync", "async"]),
              update_period=R.choice([1, 2]), update_p=R.choice([0.5, 1.0]), rules=R.choice([1, 3]),
              prog_len=8, plastic_route=R.choice([0, 1]), adapt_shift=R.choice([0, 3]),
              wimm=R.choice([0, 1]), setrule=R.choice([0, 1]), mut_site=R.choice([0.0, 0.2]),
              e_income=R.choice([0, 3]), e_max=R.choice([10, 1000]), c_emit=R.choice([0, 2]),
              c_op=R.choice([0, 1]), c_mem=R.choice([0, 1]), topo_seed=R.randrange(2 ** 32))
    if topo == "global":
        kw["dest_mode"] = "sample"
    kw.update(over)
    return Physics(**kw).validate()


def chatty_genomes(ph: Physics, B: int, seed: int) -> np.ndarray:
    """Random programs that always emit SENSE+IN on the payload and write rval/rport from the inbox."""
    g = np.random.default_rng(seed)
    gen = g.integers(0, 256, size=(B, ph.rules, ph.prog_len, 5))
    gen[..., 4] = g.integers(-128, 128, size=gen.shape[:-1])
    rm = plants.regmap(ph)
    gen[:, :, 0] = (6, rm["EMIT"], 0, 0, 1)
    gen[:, :, 1] = (2, rm["PAY0"], rm["SENSE"], rm["IN0_0"], 0)
    gen[:, :, 2] = (3, rm["RVAL"], rm["IN0_0"], rm["SENSE"], 0)
    return gen


def dense(sense: np.ndarray, B: int, N: int) -> Schedule:
    idx = torch.arange(N, dtype=torch.int64)[None].expand(B, N).clone()
    return Schedule(idx, torch.as_tensor(sense, dtype=torch.int32), idx.clone())


def site_state(w: World, b: int) -> dict:
    out = {"S": w.S[b], "E": w.E[b], "r": w.r[b], "Kp": w.Kp[b], "Acc_sum": w.Acc_sum[b], "Acc_cnt": w.Acc_cnt[b]}
    if w.R:
        out["w"] = w.w[b]
    return out


# ------------------------------------------------------- I1 message conservation
@pytest.mark.parametrize("seed", range(8))
def test_message_conservation_lossless(seed):
    """loss=0, dup=0, cap=0, noise=0, no controls: every copy written to the mailbox is delivered exactly
    once (count AND payload). delivered(stats) == sum of per-tick slot contents + what is still in flight,
    and payload in == payload out."""
    ph = rand_physics(seed, loss=0.0, dup=0.0, cap=0, collision="none", noise=0)
    B, T = 3, 30
    gen = chatty_genomes(ph, B, seed)
    sense = np.random.default_rng(seed).integers(-300, 301, size=(T, B, ph.n_sites))
    w = World(ph, gen, [11 + seed, 12 + seed, 13 + seed], device=DEV, schedule=dense(sense, B, ph.n_sites))
    got_cnt = got_pay = sent_pay = 0
    for t in range(T):
        slot = t % w.LM
        got_cnt += int(w.Mcnt[slot].sum())
        got_pay += int(w.Msum[slot].to(torch.int64).sum())
        w.step()
        sent_pay += ph.copies() * int((w.last_pay.to(torch.int64) * w.last_emit[..., None]).sum())
    inflight_cnt, inflight_pay = int(w.Mcnt.sum()), int(w.Msum.to(torch.int64).sum())
    att, dl = int(w.stats["attempted"].sum()), int(w.stats["delivered"].sum())
    assert att == dl and att > 0
    assert got_cnt + inflight_cnt == dl
    assert got_pay + inflight_pay == sent_pay


# ------------------------------------------------------- I2 accounting identity
@pytest.mark.parametrize("seed", range(8))
@pytest.mark.parametrize("zc", [False, True])
def test_attempted_equals_delivered_plus_lost(seed, zc):
    ph = rand_physics(100 + seed)
    B, T = 2, 20
    gen = chatty_genomes(ph, B, seed)
    sense = np.random.default_rng(seed).integers(-300, 301, size=(T, B, ph.n_sites))
    w = World(ph, gen, [5, 6], device=DEV, schedule=dense(sense, B, ph.n_sites), ctrl=Controls(zero_comm=zc))
    w.run(T, graph=False)
    st = {k: int(v.sum()) for k, v in w.stats.items()}
    assert st["attempted"] == st["delivered"] + st["lost"]
    if zc:
        assert st["delivered"] == 0 and int(w.Mcnt.abs().sum()) == 0 and int(w.Msum.abs().sum()) == 0


# ------------------------------------------------------- I3 locality (the root of forced zero_comm = .500)
@pytest.mark.parametrize("seed", range(10))
def test_zero_comm_locality(seed):
    """With zero_comm, perturbing SENSE at one site changes no other site's state, ever: sites interact only
    through the mailbox. (With mirror twins sharing every draw and actuator != sensor, this forces the
    zero_comm score to exactly .500 in RELAY/XOR/MAJ.)"""
    ph = rand_physics(200 + seed)
    T, N = 25, ph.n_sites
    gen = chatty_genomes(ph, 1, seed)
    gen = np.concatenate([gen, gen])
    sense = np.zeros((T, 2, N), dtype=np.int64)
    s = seed % N
    sense[3:5, 0, s] = 256
    sense[3:5, 1, s] = -256
    w = World(ph, gen, [77, 77], device=DEV, schedule=dense(sense, 2, N), ctrl=Controls(zero_comm=True))
    others = [n for n in range(N) if n != s]
    for _ in range(T):
        w.step()
        for k, v in site_state(w, 0).items():
            assert torch.equal(v[others], site_state(w, 1)[k][others]), k


# ------------------------------------------------------- I4 light cone
@pytest.mark.parametrize("seed", range(10))
def test_light_cone(seed):
    """A sense perturbation at site s at tick t_p can change a site at directed hop distance h no earlier than
    t_p + h * dmin, dmin = max(1, lat_base + lat_hop*1) (the minimum delay of any edge)."""
    ph = rand_physics(300 + seed, dup=0.0)
    T, N = 30, ph.n_sites
    gen = chatty_genomes(ph, 1, seed)
    gen = np.concatenate([gen, gen])
    s, tp = seed % N, 4
    sense = np.random.default_rng(seed).integers(-200, 201, size=(T, 1, N)).repeat(2, 1)
    sense[tp, 1, s] += 300
    w = World(ph, gen, [91, 91], device=DEV, schedule=dense(sense, 2, N))
    hop = topology.graph_distances(ph, s)
    dmin = max(1, ph.lat_base + ph.lat_hop * 1)
    for t in range(T):
        w.step()
        diff = torch.zeros(N, dtype=torch.bool)
        for k, v in site_state(w, 0).items():
            d = v != site_state(w, 1)[k]
            diff |= d.reshape(N, -1).any(-1) if d.dim() > 1 else d
        for n in torch.nonzero(diff).flatten().tolist():
            h = hop[n]
            assert h >= 0, ("unreachable site diverged", n)
            assert t >= tp + h * dmin, (t, n, h, dmin)


# ------------------------------------------------------- I5 batch independence
@pytest.mark.parametrize("seed", range(6))
def test_batch_independence(seed):
    """A world's trajectory does not depend on which other worlds share its batch."""
    ph = rand_physics(400 + seed)
    T, N = 20, ph.n_sites
    gen = chatty_genomes(ph, 3, seed)
    sense = np.random.default_rng(seed).integers(-300, 301, size=(T, 3, N))
    a = World(ph, gen, [3, 4, 5], device=DEV, schedule=dense(sense, 3, N))
    a.run(T, graph=False)
    b = World(ph, gen[[2, 0]], [5, 3], device=DEV, schedule=dense(sense[:, [2, 0]], 2, N))
    b.run(T, graph=False)
    assert a.digest(per_world=True)[0] == b.digest(per_world=True)[1]
    assert a.digest(per_world=True)[2] == b.digest(per_world=True)[0]


# ------------------------------------------------------- I6 register bounds
@pytest.mark.parametrize("seed", range(10))
def test_state_bounds(seed):
    ph = rand_physics(500 + seed)
    T, N, B = 30, ph.n_sites, 3
    g = np.random.default_rng(seed)
    gen = g.integers(0, 256, size=(B, ph.rules, ph.prog_len, 5))
    gen[..., 4] = g.integers(-128, 128, size=gen.shape[:-1])
    sense = g.integers(-40000, 40001, size=(T, B, N))
    w = World(ph, gen, [1, 2, 3], device=DEV, schedule=dense(sense, B, N))
    for _ in range(T):
        w.step()
        assert int(w.S.abs().max()) <= REG_MAX
        assert int(w.Kp.abs().max()) <= REG_MAX
        assert 0 <= int(w.E.min()) and int(w.E.max()) <= ph.e_max
        assert 0 <= int(w.r.min()) and int(w.r.max()) < ph.rules
        assert int(w.Acc_sum.abs().max()) <= 2 ** 20 and 0 <= int(w.Acc_cnt.min())
        if w.R:
            assert 0 <= int(w.w.min()) and int(w.w.max()) <= 1023


# ------------------------------------------------------- I7 mirror antisymmetry
ODD_LINES = [("CONST", "EMIT", 0, 0, 1), ("ADD", "T0", "SENSE", "IN0_0", 0), ("MOV", "PAY0", "T0", 0, 0),
             ("SUB", "T1", "S0", "IN0_0", 0), ("ADD", "S0", "S0", "T0", 0), ("SUB", "S1", "T1", "SENSE", 0)]


def _mirror_run(ph, T=24):
    G = plants.assemble(ph, ODD_LINES)[None]
    gen = np.repeat(G[None], 2, 0)
    N = ph.n_sites
    sense = np.random.default_rng(1).integers(-300, 301, size=(T, 1, N)) * \
        (np.random.default_rng(2).random((T, 1, N)) < 0.2)
    sense = np.concatenate([sense, -sense], 1)
    w = World(ph, gen, [42, 42], device=DEV, schedule=dense(sense, 2, N))
    w.run(T, graph=False)
    return w


def _antisym(w):
    return (torch.equal(w.S[0], -w.S[1]) and torch.equal(w.Acc_sum[0], -w.Acc_sum[1])
            and torch.equal(w.Msum[:, 0], -w.Msum[:, 1]) and torch.equal(w.Mcnt[:, 0], w.Mcnt[:, 1]))


@pytest.mark.parametrize("topo", ["ring", "torus", "random", "global"])
def test_mirror_antisymmetry_for_odd_programs(topo):
    """A sign-equivariant program (MOV/ADD/SUB, constant emission) under physics with no decay, no noise and
    no saturate collision gives exactly negated twins, whatever the loss/latency/jitter/dup/routing:
    every physics draw is shared by the twins, so they differ only by the input sign."""
    n = 16 if topo == "torus" else 12
    ph = Physics(topology=topo, n_sites=n, state_dim=2, payload_width=1, channels=1, prog_len=6,
                 dest_mode="sample", fanout=2, loss=0.3, dup=0.2, lat_base=1, lat_jitter=2,
                 update_mode="async", update_p=0.7, cap=2, collision="aloha").validate()
    assert _antisym(_mirror_run(ph))


@pytest.mark.parametrize("dial", [dict(noise=16), dict(cap=1, collision="saturate"), dict(decay_shift=2)])
def test_DOCUMENTS_mirror_breakers(dial):
    """DOCUMENTS: three physics dials break twin antisymmetry for the SAME odd program.
    noise: the noise draw is shared (common-mode), not negated, so twin DIFFERENCES cancel it exactly
           (this is why assays.sens_act, the selection bonus, is blind to noise);
    saturate: floor((-x)*cap/tot) != -floor(x*cap/tot) (sign-asymmetric, like decay; not annotated);
    decay: DESIGN s10."""
    ph = Physics(topology="ring", n_sites=12, state_dim=2, payload_width=1, channels=1, prog_len=6,
                 dest_mode="all", lat_base=1, cap=0, collision="none").replace(**dial).validate()
    assert not _antisym(_mirror_run(ph))


# ------------------------------------------------------- I8 inert dials (pins the dial-semantics table)
INERT = [  # (base physics kwargs, inert change)
    (dict(topology="torus", n_sites=16), dict(k_random=6)),
    (dict(topology="smallworld", n_sites=16, rewire=200), dict(k_random=6, radius=3)),
    (dict(topology="ring", n_sites=12, dest_mode="all", fanout=2, plastic_route=1), dict(fanout=8, adapt_shift=5, plastic_route=0)),
    (dict(topology="ring", n_sites=12, cap=2, collision="none"), dict(cap=1)),
    (dict(topology="global", n_sites=12, fanout=2), dict(plastic_route=1, radius=3, k_random=6, loss_per_hop=1)),
    (dict(topology="random", n_sites=12, update_mode="sync", update_p=0.5), dict(update_p=0.8)),
    (dict(topology="random", n_sites=12, lat_base=1, lat_hop=1), dict(lat_base=2, lat_hop=0)),
    (dict(topology="ring", n_sites=12, radius=1, loss=0.3, loss_per_hop=0), dict(loss_per_hop=1)),
    (dict(topology="ring", n_sites=12, rules=1, setrule=0), dict(setrule=1)),
]


@pytest.mark.parametrize("base,change", INERT)
def test_inert_dials_leave_dynamics_identical(base, change):
    ph = Physics(prog_len=8, **base).validate()
    p2 = ph.replace(**change).validate()
    env = envs.EnvSpec(family="RELAY", d=1, delta=4, trials=4)
    seeds = assays.world_seeds(7, 4)
    outs = []
    for p in (ph, p2):
        ep = envs.build(p, env, seeds)
        G = chatty_genomes(p, 1, 3)[0]
        w = World(p, np.repeat(G[None], 4, 0), [seeds[m - m % 2] for m in range(4)], device=DEV, schedule=ep.schedule)
        w.run(env.T(), graph=False)
        outs.append((w.trace.numpy().tobytes(), w.S.numpy().tobytes(),
                     tuple(int(w.stats[k].sum()) for k in ("attempted", "delivered", "lost", "collided"))))
    assert outs[0] == outs[1]
    assert outs[0][2][0] > 0          # not vacuous: packets were emitted


# ------------------------------------------------------- I9 controls: CTRL stream isolation
def test_shuffle_time_keeps_emission_and_loss_draws():
    """Controls draw only CTRL: with input-independent emission, shuffle_time leaves attempted/lost identical."""
    ph = Physics(topology="ring", n_sites=12, radius=2, dest_mode="sample", fanout=2, loss=0.3,
                 lat_jitter=1, prog_len=4).validate()
    G = plants.assemble(ph, [("CONST", "EMIT", 0, 0, 1)])[None]
    gen = np.repeat(G[None], 2, 0)
    sense = np.zeros((20, 2, 12), dtype=np.int64)
    st = []
    for c in (Controls(), Controls(shuffle_time=True), Controls(shuffle_dest=True), Controls(randomize_payload=True)):
        w = World(ph, gen, [8, 9], device=DEV, schedule=dense(sense, 2, 12), ctrl=c)
        w.run(20, graph=False)
        st.append((int(w.stats["attempted"].sum()), int(w.stats["lost"].sum())))
    assert len(set(st)) == 1


# ------------------------------------------------------- I10 sense is not latched (async cue loss)
def test_DOCUMENTS_sense_not_latched_for_asleep_sites():
    """DOCUMENTS: SENSE reaches the world only through an awake site's register file. A site asleep for the
    whole cue window never sees the cue (packets, by contrast, wait in Acc). Under async p the cue is lost
    w.p. (1-p)^cue_len, capping single-sensor accuracy at 1 - 0.5(1-p)^cue_len (HOLD p=.5: .875)."""
    ph = Physics(topology="ring", n_sites=12, update_mode="async", update_p=0.5, prog_len=9).validate()
    env = envs.EnvSpec(family="HOLD", gap=4, trials=64)
    seeds = assays.world_seeds(123, 64)
    G = plants.plant("hold_latch", ph)[None]
    acc = assays.evaluate(ph, G, env, seeds, device=DEV, graph=False).mean()[0]
    assert abs(acc - 0.875) < 0.03, acc
