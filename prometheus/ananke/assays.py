"""Evaluation, controls, twin-perturbation and transplant assays.

Batch layout everywhere: world index = genome * M + replicate, and every
genome in one call sees the SAME M env worlds and physics seeds (common
random numbers), so genome differences are not seed differences.
Replicates come in mirror pairs (envs.py), so M is even and the
independent unit of inference is the PAIR.

Every control asserts it changed something relative to the matched
normal run (Ensorain I4: an intervention that is a silent no-op returns
NOT_APPLICABLE, never a score).
"""
from __future__ import annotations

import dataclasses
import math

import numpy as np
import torch

from . import envs
from .engine import Controls, World
from .physics import Physics


# ----------------------------------------------------------------- evaluation
@dataclasses.dataclass
class EvalResult:
    acc: np.ndarray            # [P, M] per-world accuracy
    tel: dict                  # per-genome telemetry means
    digests: list | None = None
    sens_act: np.ndarray | None = None   # [P] actuator CONTRAST: mean over scored readouts of sign((S0_b - S0_twin) * y_b), in [-1, 1]
    sens_any: np.ndarray | None = None   # [P] frac of sites whose S differs between twins, mean over all ticks

    def pair_acc(self) -> np.ndarray:
        P, M = self.acc.shape
        return self.acc.reshape(P, M // 2, 2).mean(-1)

    def mean(self) -> np.ndarray:
        return self.acc.mean(1)


def world_seeds(base: int, M: int) -> list[int]:
    from .rng import H_int
    return [H_int(base, 0xA11A, m) for m in range(M)]


def evaluate(ph: Physics, genomes: np.ndarray, env: envs.EnvSpec, seeds: list[int],
             ctrl: Controls | None = None, device="cuda", graph=True,
             want_digest=False) -> EvalResult:
    P = genomes.shape[0]
    M = len(seeds)
    assert M % 2 == 0
    # mirror pairs share ALL physics randomness: world m+1 is an exact twin
    # of world m with every input negated (so their divergence is causal)
    ws = [seeds[m - (m % 2)] for _ in range(P) for m in range(M)]
    ep = envs.build(ph, env, seeds)
    sch = ep.schedule
    sch = type(sch)(sch.sense_idx.repeat(P, 1), sch.sense_val.repeat(1, P, 1), sch.read_idx.repeat(P, 1))
    g = np.repeat(genomes, M, axis=0)
    if ctrl is not None and ctrl.reset_state_mask is not None:
        ctrl = dataclasses.replace(ctrl, reset_state_mask=np.tile(ctrl.reset_state_mask, (P, 1)))
    w = World(ph, g, ws, device=device, ctrl=ctrl, schedule=sch)
    use_graph = graph and device == "cuda"
    T = env.T()
    ro_ticks = sorted(set(int(x) for x in ep.ro_tick[0][ep.scored[0]]))
    assert all((ep.ro_tick[b] == ep.ro_tick[0]).all() for b in range(M))
    sa = torch.zeros(P * M // 2, device=w.dev)
    sy = torch.zeros(P * M // 2, device=w.dev)
    ro_set = set(ro_ticks)
    ro_idx = {int(tk): k for k, tk in enumerate(ep.ro_tick[0]) if ep.scored[0][k]}
    y_lead = torch.as_tensor(np.tile(ep.y[0::2], (P, 1)), device=w.dev, dtype=torch.float32)
    ra = w.read_idx.view(P * M // 2, 2, -1)[:, 0, 0]
    for t in range(T):
        w.run(1, graph=use_graph)
        S = w.S.view(P * M // 2, 2, w.N, -1)
        d = (S[:, 0] != S[:, 1]).any(-1)                           # [pairs, N]
        sy += d.float().mean(-1)                                    # integrated over ALL ticks
        if t in ro_set:
            s0 = w.S[..., 0].view(P * M // 2, 2, w.N).gather(2, ra[:, None, None].expand(-1, 2, 1))[..., 0]
            k = ro_idx[t]
            yb = y_lead[:, k]
            sa += torch.sign((s0[:, 0] - s0[:, 1]).float() * yb)      # +1 moves with the target
    sens_act = (sa / max(1, len(ro_ticks))).view(P, M // 2).mean(1).cpu().numpy()
    sens_any = (sy / T).view(P, M // 2).mean(1).cpu().numpy()
    trace = w.trace.cpu().numpy()
    epP = envs.Episode(sch, np.tile(ep.ro_tick, (P, 1)), np.tile(ep.ro_slot, (P, 1)),
                       np.tile(ep.y, (P, 1)), np.tile(ep.scored, (P, 1)), ep.meta)
    acc = envs.score(epP, trace).reshape(P, M)
    tel = telemetry(w, env.T())
    tel = {k: v.reshape(P, M).mean(1) for k, v in tel.items()}
    dg = None
    if want_digest:
        # applied-ness fingerprint: final state + readout trace + counters
        import hashlib
        st = {k: v.cpu().numpy() for k, v in w.stats.items()}
        dg = []
        for i, d in enumerate(w.digest(per_world=True)):
            h = hashlib.sha256(d.encode())
            h.update(trace[:, i].tobytes())
            for k in sorted(st):
                h.update(k.encode() + st[k][i].tobytes())
            dg.append(h.hexdigest()[:16])
    return EvalResult(acc, tel, dg, sens_act, sens_any)


def _entropy(h: np.ndarray) -> np.ndarray:
    tot = h.sum(-1, keepdims=True)
    p = np.where(tot > 0, h / np.maximum(tot, 1), 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        e = -(np.where(p > 0, p * np.log2(p), 0)).sum(-1)
    return e


def telemetry(w: World, T: int) -> dict:
    """Cheap per-world observables. No ratio has a denominator the
    dynamics can drive to zero without a fixed fallback (Ensorain R1)."""
    st = {k: v.cpu().numpy().astype(np.float64) for k, v in w.stats.items()}
    tel = {k: v.cpu().numpy() for k, v in w.tel.items()}
    ST = float(w.N * T)                                  # fixed reference: site-ticks
    out = {
        "emit_rate": st["emitters"] / ST,
        "traffic": st["delivered"] / ST,
        "loss_frac": st["lost"] / np.maximum(st["attempted"], 1),
        "collide_frac": st["collided"] / np.maximum(st["delivered"], 1),
        "awake_frac": st["awake"] / ST,
        "ops_per_site": st["nonnop"] / ST,
        "pay_entropy": _entropy(tel["pay_hist"].astype(np.float64)),
        "chan_entropy": _entropy(tel["chan_hist"].astype(np.float64)),
        "active_frac": tel["ever_emit"].mean(-1),
        "s0_turnover": tel["s0_changes"] / ST,
        "s0_diversity": _entropy(np.stack([np.histogram(np.clip(x, -32767, 32767), bins=16,
                                                        range=(-32768, 32768))[0]
                                           for x in w.S[..., 0].cpu().numpy()]).astype(np.float64)),
        "state_nonzero": (w.S != 0).float().mean((1, 2)).cpu().numpy(),
        "energy_frac": (w.E.float().mean(1) / max(w.ph.e_max, 1)).cpu().numpy(),
    }
    if w.R:
        wt = w.w.to(torch.float64)
        conc = (wt.max(-1).values / wt.sum(-1).clamp(min=1)).mean(1)
        out["route_conc"] = conc.cpu().numpy()
    else:
        out["route_conc"] = np.zeros(w.B)
    # silence use: fraction of emission trace variance (bursty vs constant)
    et = tel["emit_trace"].astype(np.float64)
    out["emit_burst"] = et.std(0) / (w.N)                # fixed reference N
    return out


# ------------------------------------------------------------ inference units
def pair_ci(pair_vals: np.ndarray, level=0.99, n_boot=2000, seed=0):
    """Bootstrap CI of the mean over mirror pairs (the independent unit)."""
    g = np.random.default_rng(seed)
    n = pair_vals.shape[-1]
    idx = g.integers(0, n, size=(n_boot, n))
    bs = pair_vals[..., idx].mean(-1)
    lo = np.quantile(bs, (1 - level) / 2, axis=-1)
    hi = np.quantile(bs, 1 - (1 - level) / 2, axis=-1)
    return pair_vals.mean(-1), lo, hi


# ---------------------------------------------------------------- controls
def control_battery(ph: Physics, env: envs.EnvSpec) -> dict:
    """Named controls (mission s9) as (physics, Controls, applicable)."""
    Pd = env.period()
    T = env.T()
    mid = []
    for k in range(env.trials):
        t0 = k * Pd
        if env.family == "HOLD":
            mid.append(t0 + env.cue_len + env.gap // 2)
        else:
            mid.append(t0 + env.cue_len + max(1, (env.delta - env.cue_len) // 2))
    drop_win = []
    for k in range(env.trials):
        t0 = k * Pd
        end = t0 + (env.cue_len + env.gap if env.family == "HOLD" else env.delta)
        drop_win += list(range(t0, end))
    C = ph.channels
    bat = {
        "zero_comm": (ph, Controls(zero_comm=True), True),
        "shuffle_dest": (ph, Controls(shuffle_dest=True), True),
        "shuffle_time": (ph, Controls(shuffle_time=True), True),
        "randomize_payload": (ph, Controls(randomize_payload=True), True),
        "packet_ablation": (ph, Controls(drop_packets_at=tuple(drop_win)), True),
        "memory_ablation": (ph, Controls(reset_state_at=tuple(mid)), True),
        "adaptation_off": (ph, Controls(no_adapt=True),
                           bool(ph.plastic_route or ph.wimm or ph.setrule or ph.mut_site > 0)),
        "frozen_routing": (ph, Controls(freeze_routing=True), bool(ph.plastic_route)),
        "max_loss": (ph.replace(loss=1.0), Controls(), True),
        "irrelevant_channel": (ph, Controls(distractor_chan=C - 1), C >= 2),
    }
    return bat


def run_controls(ph: Physics, genome: np.ndarray, env: envs.EnvSpec, seeds: list[int],
                 device="cuda") -> dict:
    """Champion under every applicable control, plus the matched normal run,
    plus the environment-permutation null (scores against another world's
    targets) and a no-op guard per control."""
    g1 = genome[None]
    base = evaluate(ph, g1, env, seeds, device=device, want_digest=True)
    out = {"normal": {"acc": float(base.acc.mean()), "pair": base.pair_acc()[0].tolist()}}
    for name, (ph2, ctrl, ok) in control_battery(ph, env).items():
        if not ok:
            out[name] = {"status": "NOT_APPLICABLE", "why": "physics lacks the ablated channel"}
            continue
        r = evaluate(ph2, g1, env, seeds, ctrl=ctrl, device=device, want_digest=True)
        injected = name == "irrelevant_channel"   # applied by construction: every site gets a packet per tick
        if r.digests == base.digests and not injected:
            out[name] = {"status": "NOT_APPLICABLE", "why": "control changed no state (no-op guard)"}
            continue
        out[name] = {"status": "RAN", "acc": float(r.acc.mean()), "pair": r.pair_acc()[0].tolist()}
    # environment permutation: the champion's traces scored against a
    # different world's targets (rotate replicate pairs by one pair)
    ep = envs.build(ph, env, seeds)
    w = World(ph, np.repeat(g1, len(seeds), 0), seeds, device=device, schedule=ep.schedule)
    w.run(env.T())
    tr = w.trace.cpu().numpy()
    # exact permutation null over every rotation of mirror pairs
    M = len(seeds)
    vals = []
    for k in range(1, M // 2):
        perm = np.roll(np.arange(M), 2 * k)
        ep2 = envs.Episode(ep.schedule, ep.ro_tick, ep.ro_slot, ep.y[perm], ep.scored[perm], ep.meta)
        vals.append(float(envs.score(ep2, tr).mean()))
    out["env_permutation"] = {"status": "RAN", "acc": float(np.mean(vals)),
                              "min": float(np.min(vals)), "max": float(np.max(vals))}
    return out


# ----------------------------------------------------- twin perturbation assay
def twin_assay(ph: Physics, genomes: np.ndarray, env: envs.EnvSpec, seeds: list[int],
               trial: int = 2, device="cuda") -> dict:
    """Causal influence of ONE cue: twin worlds identical in everything
    (genome, seeds, all physics draws) except that trial `trial`'s sensor
    input is negated in the twin. Divergence of S between twins measures,
    per genome: reach (max env distance of a diverged site from the
    perturbed sensor), speed, persistence after the cue ends, whether the
    targeted readout flipped, and whether reach exceeds one-hop range."""
    P, M = genomes.shape[0], len(seeds)
    ep = envs.build(ph, env, seeds)
    Pd = env.period()
    t0 = trial * Pd
    t1 = t0 + env.cue_len
    sidx = ep.schedule.sense_idx
    sv = ep.schedule.sense_val
    sv_tw = sv.clone()
    sv_tw[t0:t1] = -sv_tw[t0:t1]
    B = P * M
    sch = type(ep.schedule)(sidx.repeat(2 * P, 1),
                            torch.cat([sv.repeat(1, P, 1), sv_tw.repeat(1, P, 1)], 1),
                            ep.schedule.read_idx.repeat(2 * P, 1))
    g = np.concatenate([np.repeat(genomes, M, 0)] * 2, 0)
    ws = [s for _ in range(P) for s in seeds] * 2
    w = World(ph, g, ws, device=device, schedule=sch)
    Dm = torch.as_tensor(envs.dist_matrix(ph), device=w.dev)
    src = sidx[:, 0].to(w.dev).repeat(P)                      # perturbed sensor per world
    dsrc = Dm[src]                                            # [B, N]
    T = env.T()
    frac = torch.zeros(T, B, device=w.dev)
    reach = torch.zeros(T, B, device=w.dev)
    for t in range(T):
        w.run(1)
        div = (w.S[:B] != w.S[B:]).any(-1) | (w.Msum[:, :B] != w.Msum[:, B:]).any(-1).any(-1).any(0)
        frac[t] = div.float().mean(-1)
        reach[t] = torch.where(div, dsrc, torch.zeros_like(dsrc)).max(-1).values.float()
    frac = frac.cpu().numpy()
    reach = reach.cpu().numpy()
    tr = w.trace.cpu().numpy()
    ro = ep.ro_tick[:, trial]
    a = tr[np.tile(ro, P), np.arange(B), 0]
    b = tr[np.tile(ro, P), np.arange(B, 2 * B), 0]
    flipped = (np.sign(a) != np.sign(b)).astype(float)
    alive = frac > 0
    last = np.where(alive.any(0), T - 1 - np.argmax(alive[::-1], 0), -1)
    persist = np.where(last >= t1, last - t1 + 1, 0)
    # divergence still present at the NEXT trial's cue: memory of the cue
    nxt = min(T - 1, t0 + Pd)
    hop = ph.max_dist() if ph.topology in ("ring", "torus") else 1
    res = {
        "reach": reach.max(0), "persist": persist.astype(float),
        "div_frac_readout": frac[np.tile(ro, P), np.arange(B)],
        "div_frac_next": frac[nxt], "readout_flipped": flipped,
        "beyond_hop": (reach.max(0) > hop).astype(float),
    }
    return {k: v.reshape(P, M).mean(1) for k, v in res.items()}


# ---------------------------------------------------------------- transplants
def transplant_state(src: World, dst: World, parts=("S", "w", "Kp", "r")) -> None:
    """Copy the named mutable components from src into dst (same shapes).
    Asserts something changed (no-op guard)."""
    changed = False
    for p in parts:
        a, b = getattr(src, p), getattr(dst, p)
        if p == "w" and not (src.R and dst.R):
            continue
        if not torch.equal(a, b):
            changed = True
        b.copy_(a)
    if not changed:
        raise RuntimeError("NOT_APPLICABLE: transplant changed nothing")
