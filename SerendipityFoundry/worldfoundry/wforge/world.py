"""Grammar v0 expansion + deterministic integer world runtime.

MECHANICS MODEL (composable primitives, all integer, all seeded):
  STATE        register bank of R values mod M
  TRANSITION   linear maps mod M; optional REGIME_SWITCH (coefficient swap on a
               period); optional seeded stochastic kernel; optional DELAY_QUEUE
               (actions land d ticks late)
  ACTION       act vector of A ints in [0, K); action i adds magnitude to a
               target register (costed per unit)
  RESOURCE     per-slot conserved charge; per-tick metabolic cost; action cost;
               YIELD rule: a slot earns charge on ticks where a hidden predicate
               over registers holds (a value window on a designated register) --
               contested proportionally when several slots qualify
  INTERACTION  (n_slots=2) all slots write into the SAME register bank; the
               interface never distinguishes "other player" from "world"
  OBSERVATION  seeded permutation of a register projection + own charge bucket,
               optional seeded corruption, optional delay
  TERMINATION  horizon; a slot with charge <= 0 is absorbed (dead, no actions)

Determinism: every random draw comes from named xorshift64 streams derived from
(world seed | episode seed | stream tag). No floats. No dict-order iteration.
The full trace is hashed; cross-host replay compares trace hashes with ZERO
divergence tolerance.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .genome import WorldGenome, content_hash

M = 1 << 16          # register modulus
MASK64 = (1 << 64) - 1


class XS64:
    """xorshift64* -- deterministic, portable, integer-only."""

    def __init__(self, seed: int):
        self.s = (seed ^ 0x9E3779B97F4A7C15) & MASK64 or 0xDEADBEEF

    def next(self) -> int:
        s = self.s
        s ^= (s << 13) & MASK64
        s ^= s >> 7
        s ^= (s << 17) & MASK64
        self.s = s
        return (s * 0x2545F4914F6CDD1D) & MASK64

    def below(self, n: int) -> int:
        return self.next() % n


def stream(*tags) -> XS64:
    h = hashlib.sha256(("|".join(str(t) for t in tags)).encode()).digest()
    return XS64(int.from_bytes(h[:8], "big"))


@dataclass
class Mechanics:
    """Expanded mechanics manifest (the phenotype of the genome)."""
    n_regs: int
    n_slots: int
    horizon: int
    lin_ops: list          # [(dst, a, src1, b, src2, c)] applied each tick
    regime_period: int     # 0 = no regime switch; else swap lin coeff sign set
    stoch_rate: int        # 0 = deterministic; else 1-in-rate register kick
    delay: int             # action landing delay in ticks
    act_width: int
    act_targets: list      # register index per action channel
    act_cost: int          # charge per unit magnitude
    step_cost: int         # metabolic cost per tick per live slot
    yield_reg: int         # register the yield predicate reads
    yield_lo: int
    yield_hi: int          # predicate: yield_lo <= reg[yield_reg] % M < yield_hi
    yield_amt: int         # charge minted per qualifying tick (split on contention)
    start_charge: int
    obs_perm: list         # permutation of observed register subset
    obs_regs: list         # which registers are observable
    corrupt_rate: int      # 0 = clean; else 1-in-rate obs element xor-noise
    obs_delay: int         # observe state from obs_delay ticks ago
    horizon_class: str

    def manifest_hash(self) -> str:
        d = {k: getattr(self, k) for k in sorted(self.__dataclass_fields__)}
        return content_hash(d)


def expand(g: WorldGenome) -> Mechanics:
    """PURE FUNCTION genome -> mechanics. Mutation history is interpreted here,
    so a descendant genome alone reproduces the mutated world exactly."""
    r = stream("expand", g.grammar_version, g.generation_seed)
    n_regs = 4 + r.below(9)                      # 4..12
    n_slots = 1 + (r.below(4) == 0)              # 25% two-slot worlds
    horizon = (32, 64, 128, 256)[r.below(4)]
    lin_ops = []
    for _ in range(2 + r.below(4)):              # 2..5 transition ops
        lin_ops.append((r.below(n_regs), 1 + r.below(5), r.below(n_regs),
                        r.below(4), r.below(n_regs), r.below(M)))
    regime_period = 0 if r.below(3) else (8 << r.below(4))
    stoch_rate = 0 if r.below(2) else (4 << r.below(4))
    delay = (0, 0, 1, 4)[r.below(4)]
    act_width = 1 + r.below(3)
    act_targets = [r.below(n_regs) for _ in range(act_width)]
    act_cost = 1 + r.below(3)
    step_cost = 1 + r.below(2)
    yield_reg = r.below(n_regs)
    width = 1 << (10 + r.below(4))               # window width 1k..8k of 64k
    lo = r.below(M)
    yield_amt = 8 + r.below(25)
    start_charge = 64 + r.below(129)
    n_obs = max(2, n_regs - r.below(3))
    obs_regs = sorted(set(r.below(n_regs) for _ in range(n_obs))) or [0]
    perm = list(range(len(obs_regs) + 1))        # +1: own-charge bucket channel
    for i in range(len(perm) - 1, 0, -1):        # seeded Fisher-Yates
        j = r.below(i + 1)
        perm[i], perm[j] = perm[j], perm[i]
    corrupt_rate = 0 if r.below(2) else (8 << r.below(3))
    obs_delay = (0, 0, 0, 2)[r.below(4)]

    mech = Mechanics(
        n_regs=n_regs, n_slots=n_slots, horizon=horizon, lin_ops=lin_ops,
        regime_period=regime_period, stoch_rate=stoch_rate, delay=delay,
        act_width=act_width, act_targets=act_targets, act_cost=act_cost,
        step_cost=step_cost, yield_reg=yield_reg, yield_lo=lo,
        yield_hi=(lo + width) % M or M, yield_amt=yield_amt,
        start_charge=start_charge, obs_perm=perm, obs_regs=obs_regs,
        corrupt_rate=corrupt_rate, obs_delay=obs_delay,
        horizon_class="",
    )

    # --- apply mutation history (each op is a seeded, typed edit) ---
    for mut in g.mutation_history:
        mr = stream("mut", mut.op, mut.op_seed)
        if mut.op == "PARAM_PERTURB":
            k = mr.below(4)
            if k == 0:
                mech.yield_lo = (mech.yield_lo + mr.below(M // 8)) % M
            elif k == 1:
                mech.yield_amt = max(1, mech.yield_amt + mr.below(9) - 4)
            elif k == 2:
                mech.step_cost = max(1, mech.step_cost + mr.below(3) - 1)
            else:
                mech.start_charge = max(16, mech.start_charge + mr.below(65) - 32)
        elif mut.op == "PRIMITIVE_INSERT":
            mech.lin_ops.append((mr.below(mech.n_regs), 1 + mr.below(5),
                                 mr.below(mech.n_regs), mr.below(4),
                                 mr.below(mech.n_regs), mr.below(M)))
        elif mut.op == "PRIMITIVE_DELETE" and len(mech.lin_ops) > 1:
            mech.lin_ops.pop(mr.below(len(mech.lin_ops)))
        elif mut.op == "REWIRE":
            i = mr.below(len(mech.act_targets))
            mech.act_targets[i] = mr.below(mech.n_regs)
        elif mut.op == "BUDGET_MUTATE":
            mech.horizon = max(32, min(512, mech.horizon * (1 + mr.below(2) * 1)))
        elif mut.op == "INTERFACE_MUTATE":
            mech.corrupt_rate = 0 if mech.corrupt_rate else 16
            mech.obs_delay = 0 if mech.obs_delay else 2

    # horizon_class is DERIVED mechanically, never authored
    slow = mech.delay * 8 + mech.obs_delay * 4 + (mech.regime_period or 0)
    mech.horizon_class = ("MICRO" if slow == 0 and mech.horizon <= 64 else
                          "SHORT" if slow <= 8 else
                          "MEDIUM" if slow <= 32 else "LONG")
    return mech


class Encounter:
    """One deterministic episode: world + per-slot players + master seed."""

    def __init__(self, mech: Mechanics, world_id: str, episode_seed: int):
        self.m = mech
        self.world_id = world_id
        self.seed = episode_seed
        self.regs = [stream("init", world_id, episode_seed, i).below(M)
                     for i in range(mech.n_regs)]
        self.charge = [mech.start_charge] * mech.n_slots
        self.alive = [True] * mech.n_slots
        self.tick = 0
        self.pending = []                      # (land_tick, slot, target, amt)
        self.history = []                      # register snapshots (obs delay)
        self.trace = hashlib.sha256()
        self.yield_events = [0] * mech.n_slots
        self.actions_used = [0] * mech.n_slots
        self.abstained = [0] * mech.n_slots
        self._s_stoch = stream("stoch", world_id, episode_seed)
        self._s_corrupt = [stream("corrupt", world_id, episode_seed, i)
                           for i in range(mech.n_slots)]

    def observe(self, slot: int) -> list:
        m = self.m
        src = self.regs
        if m.obs_delay and len(self.history) > m.obs_delay:
            src = self.history[-1 - m.obs_delay]
        vals = [src[i] for i in m.obs_regs] + [min(15, self.charge[slot] // 32)]
        if m.corrupt_rate:
            cr = self._s_corrupt[slot]
            vals = [v ^ (cr.below(M) if cr.below(m.corrupt_rate) == 0 else 0)
                    for v in vals]
        return [vals[p] for p in self.m.obs_perm]     # per-world channel permutation

    def step(self, actions: list) -> bool:
        """actions: per-slot list[int] of length act_width (ignored for dead
        slots). Two-phase: (1) collect+queue all writes, (2) settle world,
        (3) settle economy simultaneously. Returns done."""
        m = self.m
        # phase 1: action intake (simultaneous)
        for s in range(m.n_slots):
            if not self.alive[s]:
                continue
            a = actions[s]
            mag = sum(x % 8 for x in a)
            if mag == 0:
                self.abstained[s] += 1
            cost = mag * m.act_cost
            if cost > self.charge[s]:
                mag, cost = 0, 0                     # cannot afford: forced abstain
            self.charge[s] -= cost
            self.actions_used[s] += mag
            for i, x in enumerate(a[:m.act_width]):
                amt = x % 8
                if amt:
                    self.pending.append((self.tick + m.delay, s,
                                         m.act_targets[i], amt * 251))
        # phase 2: world transition (deterministic order)
        landing = [p for p in self.pending if p[0] == self.tick]
        self.pending = [p for p in self.pending if p[0] > self.tick]
        for _, s, tgt, amt in sorted(landing, key=lambda p: (p[1], p[2])):
            self.regs[tgt] = (self.regs[tgt] + amt) % M
        flip = (m.regime_period and (self.tick // m.regime_period) % 2 == 1)
        for dst, a, s1, b, s2, c in m.lin_ops:
            aa = (M - a) % M if flip else a
            self.regs[dst] = (aa * self.regs[s1] + b * self.regs[s2] + c) % M
        if m.stoch_rate and self._s_stoch.below(m.stoch_rate) == 0:
            self.regs[self._s_stoch.below(m.n_regs)] = self._s_stoch.below(M)
        # phase 3: economy (simultaneous settlement)
        v = self.regs[m.yield_reg]
        in_win = (m.yield_lo <= v < m.yield_hi) if m.yield_lo < m.yield_hi else \
                 (v >= m.yield_lo or v < m.yield_hi)
        winners = [s for s in range(m.n_slots) if self.alive[s]] if in_win else []
        for s in range(m.n_slots):
            if not self.alive[s]:
                continue
            self.charge[s] -= m.step_cost
            if s in winners:
                self.charge[s] += m.yield_amt // len(winners)
                self.yield_events[s] += 1
            if self.charge[s] <= 0:
                self.alive[s] = False                # absorbed
        # trace + bookkeeping
        self.trace.update(bytes(str((self.tick, self.regs, self.charge,
                                     self.alive)), "ascii"))
        self.history.append(list(self.regs))
        if len(self.history) > 8:
            self.history.pop(0)
        self.tick += 1
        return self.tick >= m.horizon or not any(self.alive)

    def outcome(self) -> dict:
        return {
            "trace_hash": self.trace.hexdigest(),
            "ticks": self.tick,
            "per_slot": [{
                "final_charge": self.charge[s],
                "alive": self.alive[s],
                "yield_events": self.yield_events[s],
                "actions_used": self.actions_used[s],
                "abstained": self.abstained[s],
            } for s in range(self.m.n_slots)],
        }
