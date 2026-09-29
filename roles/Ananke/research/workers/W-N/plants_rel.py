"""W-N known-answer plants with CONTROLLED normal accuracy, and a batched
SINGLE-trial arm runner that accepts arbitrary between-tick interventions.

Plants (n-back n=1 task of W-L nback.py, physics = W-L m2 physics with
prog_len 28 so the redundant plant fits; W-L's P1S body is copied verbatim for
the noiseless case):
  P1S_q    carrier S1. On the awake cue tick the stored value is the cue with
           its sign FLIPPED with probability q = (256 - th) / 513, drawn by the
           engine's own RAND op (seeded by the world seed, hence identical in
           both mirror partners). normal accuracy = 1 - q by construction.
  P1SK_q   the same noisy bit stored REDUNDANTLY in S1 and Kp[3]; readout
           S0 := S1 + Kp[3] (tie -> 0 -> scored .5). Swapping S alone or Kp
           alone gives a tie: CHANCE by construction; S + Kp gives FLIP.
Interventions (between ticks, after tick k*Pd - 1, i.e. just before cue k, when
the carrier holds c_{k-1}, the answer of trial k):
  S1        swap register S1 only                       -> FLIP        (P1S)
  S0        swap register S0 only (overwritten at cue)  -> NO_EFFECT   (P1S, non-identical arm)
  S1_half   swap S1 in a fixed random HALF of pairs      -> CHANCE      (pair mixture)
  S1_3q     swap S1 in a fixed random 75 % of pairs      -> z = -1/2: INDETERMINATE
  S / Kp / site_all as lens.carriers.
Physics untouched: plants are genomes, interventions act between ticks.
"""
from __future__ import annotations

import dataclasses
import pathlib
import sys

import numpy as np
import torch

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[4]
WL = HERE.parent / "W-L"
for p in (str(REPO), str(WL)):
    if p not in sys.path:
        sys.path.insert(0, p)
import nback as nb  # noqa: E402  (W-L n-back builder; imported, not edited)
from prometheus.ananke import envs, lens, plants, rng  # noqa: E402
from prometheus.ananke.engine import Controls, Schedule, World  # noqa: E402

NS_WN = 0x5E4E            # W-N analysis namespace
NOT_RUN = -(2 ** 40)


def physics():
    return dataclasses.replace(nb.m2()[0], prog_len=28)


def th_for_q(q: float) -> int:
    """RAND in [-256, 256] (513 values); flag iff RAND > th; q = (256 - th)/513."""
    return int(round(256 - q * 513))


def q_of_th(th: int) -> float:
    return (256 - th) / 513


def _noisy_cue(th: int):
    """T2 := cue * (-1 if RAND(|SENSE|) > th else +1). Uses T2, T3."""
    return [("RAND", "T2", "SENSE", 0, 0),
            ("CONST", "T3", 0, 0, th),
            ("GT", "T2", "T2", "T3", 0),           # flag 256 / 0
            ("CONST", "T3", 0, 7, 2),              # 256
            ("SUB", "T3", "T3", "T2", 0),
            ("SUB", "T3", "T3", "T2", 0),          # F = +-256
            ("MULQ", "T2", "SENSE", "T3", 0)]      # +-cue


def body(name: str, ph, th: int | None = None) -> np.ndarray:
    c, gt = nb._cond(), nb._gated
    if name == "P1S":
        if th is None:
            lines = c + gt("S0", "S1", "T1") + gt("S1", "SENSE", "T1")
        else:
            lines = c + gt("S0", "S1", "T1") + _noisy_cue(th) + gt("S1", "T2", "T1")
    elif name == "P1SK":
        th = 300 if th is None else th             # 300 > max RAND 256: never flips
        lines = c + [("ADDI", "T1", "ZERO", 0, 0),                 # line 3: T1 = Kp[3]
                     ("ADD", "T3", "S1", "T1", 0)] \
            + gt("S0", "T3", "T2") + _noisy_cue(th) + gt("S1", "T2", "T3") \
            + [("MOV", "T3", "T1", 0, 0)] + gt("T3", "T2", "RVAL") \
            + [("CONST", "T2", 0, 0, 3), ("WIMM", "T1", "T2", "T3", 0)]
        assert lines[3][0] == "ADDI"
    else:
        raise KeyError(name)
    b = plants.assemble(ph, lines)
    return np.broadcast_to(b, (ph.rules, *b.shape)).copy()


# ------------------------------------------------------------------ interventions
def _pair_mask(rows: torch.Tensor, M: int, frac: float, salt: int) -> torch.Tensor:
    """Fixed pseudo-random subset of pairs (by pair index within the block)."""
    pidx = ((rows % M) // 2).cpu().numpy()
    u = np.array([(rng.H_int(NS_WN, salt, int(p)) % 10_000) / 10_000 for p in pidx])
    return torch.as_tensor(u < frac, device=rows.device)


def make_fn(kind: str, M: int):
    """-> fn(w, rows) acting only on world rows `rows` (one block)."""
    def reg_swap(reg, frac=1.0, salt=0):
        def f(w, rows):
            r = rows if frac >= 1 else rows[_pair_mask(rows, M, frac, salt)]
            if len(r):
                w.S[r, :, reg] = w.S[r ^ 1, :, reg]
        return f

    def arr_swap(names):
        def f(w, rows):
            p = rows ^ 1
            for n in names:
                if n == "w" and not w.R:
                    continue
                a = getattr(w, n)
                if n in lens.FLIGHT_ARRAYS:
                    a[:, rows] = a[:, p]
                else:
                    a[rows] = a[p]
        return f
    table = {"S1": reg_swap(1), "S0": reg_swap(0), "S1_half": reg_swap(1, 0.5, 1),
             "S1_3q": reg_swap(1, 0.75, 2), "S": arr_swap(["S"]), "Kp": arr_swap(["Kp"]),
             "site_all": arr_swap(list(lens.SITE_ARRAYS)), "channel_all": arr_swap(list(lens.FLIGHT_ARRAYS)),
             "inbox": arr_swap(["Acc_sum", "Acc_cnt"]),
             "joint": arr_swap(list(lens.SITE_ARRAYS) + list(lens.FLIGHT_ARRAYS))}
    return table[kind]


@dataclasses.dataclass(frozen=True)
class Arm:
    label: str
    kind: str | None = None     # intervention name (None = normal)
    offset: int = -1            # swap AFTER tick trial*Pd + offset
    trial: int | None = None    # SINGLE: swap and score trial `trial` only


def run_arms(ph, genome, env, seeds, arms, device="cpu", chunk=16, ep=None):
    """Batched SINGLE-trial arms (lens_swap.run_arms design, generic fns).
    Returns (ep, per_trial{label: [M, trials]}, s0{label: [M, trials]})."""
    M = len(seeds)
    ep = ep or envs.build(ph, env, seeds)
    ws1 = [seeds[m - (m % 2)] for m in range(M)]
    Pd, T = env.period(), env.T()
    pt, s0s = {}, {}
    for c0 in range(0, len(arms), chunk):
        part = arms[c0:c0 + chunk]
        K = len(part)
        sch = Schedule(ep.schedule.sense_idx.repeat(K, 1), ep.schedule.sense_val.repeat(1, K, 1),
                       ep.schedule.read_idx.repeat(K, 1))
        w = World(ph, np.repeat(genome[None], M * K, 0), ws1 * K, device=device, ctrl=Controls(), schedule=sch)
        hooks, tmax = {}, 0
        for j, a in enumerate(part):
            tmax = T - 1 if a.trial is None else max(tmax, int(ep.ro_tick[:, a.trial].max()))
            if a.kind is None:
                continue
            rows = torch.arange(j * M, (j + 1) * M, device=w.dev)
            fn = make_fn(a.kind, M)
            for k in (range(env.trials) if a.trial is None else [a.trial]):
                t = k * Pd + a.offset
                if 0 <= t < T:
                    hooks.setdefault(t, []).append((fn, rows))
        for t in range(tmax + 1):
            w.step()
            for fn, rows in hooks.get(t, ()):
                fn(w, rows)
        tr = w.trace.cpu().numpy()
        for j, a in enumerate(part):
            trj = tr[:, j * M:(j + 1) * M]
            p = envs.per_trial(ep, trj).astype(float)
            s0 = trj[ep.ro_tick, np.arange(M)[:, None], ep.ro_slot].astype(np.int64)
            ran = ep.ro_tick <= tmax
            p[~ran] = np.nan
            s0[~ran] = NOT_RUN
            if a.trial is not None:
                keep = np.zeros_like(ran)
                keep[:, a.trial] = True
                p[~keep] = np.nan
            p[~ep.scored] = np.nan
            pt[a.label], s0s[a.label] = p, s0
    return ep, pt, s0s


def run_fork(ph, genome, env, seeds, kinds, trials, offset=-1, device="cpu", ep=None):
    """Equivalent of run_arms for SINGLE arms, by forking: one normal world
    runs the whole episode; at tick k*Pd+offset a deep copy per intervention
    is intervened on (all rows) and stepped only to trial k's readout.
    Returns (ep, normal_per_trial, {kind: [M, trials]}, normal_s0, {kind: s0})."""
    import copy
    M = len(seeds)
    ep = ep or envs.build(ph, env, seeds)
    ws1 = [seeds[m - (m % 2)] for m in range(M)]
    Pd, T = env.period(), env.T()
    w = World(ph, np.repeat(genome[None], M, 0), ws1, device=device, ctrl=Controls(), schedule=ep.schedule)
    rows = torch.arange(M, device=w.dev)
    fns = {k: make_fn(k, M) for k in kinds}
    s0 = {k: np.full(ep.y.shape, NOT_RUN, np.int64) for k in kinds}
    fork_at = {}
    for k in trials:
        t = k * Pd + offset
        if 0 <= t < T:
            fork_at.setdefault(t, []).append(k)
    bi = np.arange(M)
    for t in range(T):
        w.step()
        for k in fork_at.get(t, ()):
            ro = ep.ro_tick[:, k]
            for kind in kinds:
                c = copy.deepcopy(w)
                fns[kind](c, rows)
                for _ in range(t + 1, int(ro.max()) + 1):
                    c.step()
                tr = c.trace.cpu().numpy()
                s0[kind][:, k] = tr[ro, bi, ep.ro_slot[:, k]]
    trn = w.trace.cpu().numpy()
    n0 = trn[ep.ro_tick, bi[:, None], ep.ro_slot].astype(np.int64)
    def score(v):
        p = np.where(v == 0, 0.5, (np.sign(v) == ep.y).astype(float))
        return np.where((v != NOT_RUN) & ep.scored, p, np.nan)
    return ep, score(n0), {k: score(v) for k, v in s0.items()}, n0, s0


def single(label_kind: str, trials, offset=-1):
    return [Arm(f"{label_kind}#{k}", label_kind, offset, k) for k in trials]


def merge(pt: dict, kind: str, trials) -> np.ndarray:
    """Merge the SINGLE blocks of one intervention into one [M, trials] array."""
    ref = next(iter(pt.values()))
    out = np.full_like(ref, np.nan)
    for k in trials:
        out[:, k] = pt[f"{kind}#{k}"][:, k]
    return out


def merge_s0(s0: dict, kind: str, trials) -> np.ndarray:
    ref = next(iter(s0.values()))
    out = np.full(ref.shape, NOT_RUN, np.int64)
    for k in trials:
        out[:, k] = s0[f"{kind}#{k}"][:, k]
    return out


# ------------------------------------------------------------------ post-hoc readout noise
def readout_noise(s0: np.ndarray, y: np.ndarray, scored: np.ndarray, q: float, gen, mode: str,
                  mask: np.ndarray | None = None) -> tuple:
    """Flip (mode 'flip') or zero (mode 'abstain') the readout of a random
    fraction q of world-trials. Pass the same `mask` to several arms for
    ARM-SHARED noise; mask=None draws fresh (ARM-INDEPENDENT). Returns
    (per_trial, mask). Equivalent to a between-tick negation/zeroing of the
    readout S0 after tick ro-1 for P1S (checked in run_plants.py)."""
    if mask is None:
        mask = gen.random(s0.shape) < q
    v = s0.copy()
    run = v != NOT_RUN
    if mode == "flip":
        v = np.where(mask & run, -v, v)
    else:
        v = np.where(mask & run, 0, v)
    p = np.where(v == 0, 0.5, (np.sign(v) == y).astype(float))
    p = np.where(run & scored, p, np.nan)
    return p, mask
