"""Plant families (sealed effect generators) and their matched controls.

QUALIFICATION DISCIPLINE:
  * Every plant has a matched control that is IDENTICAL except for the
    hypothesized effect (same code path, same seeds, epsilon=0), so the twin
    difference isolates exactly the planted mechanism.
  * Effect size epsilon is the per-tick probability that the planted
    mechanism modulates behavior. Power curves sweep epsilon downward until
    the instrument goes blind. That blindness boundary is the deliverable.
  * P5 is SEALED: defined and hash-committed here BEFORE any detector code
    was written, excluded from all tuning, evaluated exactly once at the end
    of qualification. (Solo-build caveat recorded in the packet: the same
    author wrote plant and detector; external sealed plants remain required
    for hostile-reviewer convincibility, per World Foundry R14.)

Plants are built on a seeded-random BASE policy so that the base contributes
zero history dependence: for the base alone, an observation intervention at
tick t changes NO action at any later tick (actions are drawn from a seed
stream, not from observations). Everything the interventional instrument sees
is therefore the planted mechanism -- or a bug.
"""
from __future__ import annotations

from wforge.world import stream


class BasePlayer:
    """Seeded random policy; observation-blind by construction."""
    name = "base"

    def __init__(self, seed: int):
        self.seed = seed

    def reset(self, act_width: int, obs_width: int):
        self.r = stream("mhc-base", self.seed)
        self.act_width = act_width
        self.obs_width = obs_width

    def act(self, obs):
        return [self.r.below(8) for _ in range(self.act_width)]


class P1_DelayedDep(BasePlayer):
    """FAMILY P1 -- TINY DELAYED-STATE EFFECT (signal class A).
    Stores one seeded-chosen observation element each tick. With per-tick
    probability epsilon, action[0] is replaced by 7*parity(stored element
    from LAG ticks ago). epsilon=0 is the matched control (still stores,
    never uses -- 'capacity without use', which must read as exactly zero)."""
    name = "P1_delayed"
    LAG = 6

    def __init__(self, seed: int, eps_milli: int):
        super().__init__(seed)
        self.eps_milli = eps_milli          # epsilon in thousandths (integer)

    def reset(self, act_width: int, obs_width: int):
        super().reset(act_width, obs_width)
        self.rmod = stream("mhc-p1-mod", self.seed)
        self.j0 = stream("mhc-p1-elem", self.seed).below(self.obs_width)
        self.buf = []

    def act(self, obs):
        a = [self.r.below(8) for _ in range(self.act_width)]
        self.buf.append(obs[self.j0])
        trigger = self.rmod.below(1000) < self.eps_milli
        if trigger and len(self.buf) > self.LAG:
            a[0] = 7 * (self.buf[-1 - self.LAG] & 1)
        return a


class P2_InteractionOnly(P1_DelayedDep):
    """FAMILY P2 -- INTERACTION-ONLY EFFECT (dP x dW). The planted mechanism
    is ACTIVE only when the world exhibits action delay (a world feature the
    harness sets via world_has_delay). Marginal tests over mixed worlds are
    diluted; the factorial interaction term concentrates the effect."""
    name = "P2_interaction"

    def __init__(self, seed: int, eps_milli: int):
        super().__init__(seed, eps_milli)
        self.world_has_delay = False        # set by the harness per twin arm

    def act(self, obs):
        a = [self.r.below(8) for _ in range(self.act_width)]
        self.buf.append(obs[self.j0])
        trigger = self.rmod.below(1000) < self.eps_milli
        if trigger and self.world_has_delay and len(self.buf) > self.LAG:
            a[0] = 7 * (self.buf[-1 - self.LAG] & 1)
        return a


class P3_StructureNotOutcome(BasePlayer):
    """FAMILY P3 -- STRUCTURAL CHANGE, OUTCOME-WEAK (signal class B).
    With probability epsilon per tick, the action vector is replaced by a
    deterministic periodic schedule whose MARGINAL magnitude distribution
    matches the base draw (a seeded permutation of the same draws), so the
    economy is disturbed as little as the substrate allows while temporal
    structure changes. Qualification measures BOTH powers: outcome-based
    detection vs structure-based (mu4/mu5) detection, at equal luminosity."""
    name = "P3_structure"

    def __init__(self, seed: int, eps_milli: int):
        super().__init__(seed)
        self.eps_milli = eps_milli

    def reset(self, act_width: int, obs_width: int):
        super().reset(act_width, obs_width)
        self.rmod = stream("mhc-p3-mod", self.seed)
        self.t = 0

    def act(self, obs):
        draws = [self.r.below(8) for _ in range(self.act_width)]
        self.t += 1
        if self.rmod.below(1000) < self.eps_milli:
            k = self.t % max(1, self.act_width)
            draws = draws[k:] + draws[:k]     # same multiset, shifted structure
            draws[0] = (draws[0] + 4) % 8 if self.t % 2 == 0 else draws[0]
        return draws


class DampWrap:
    """Perturbation operator with MECHANICAL COHERENCE (the red team's
    operator-floor artifact, instantiated deliberately): with probability 1/2
    per tick, damp every action element by 1. This shifts cost/yield the SAME
    systematic way in essentially every world -- a coherent cross-block
    direction with ZERO player microstructure. The naive sign test must fire
    on it; the reference-conditioned rank must not (other draws from the same
    operator distribution carry the same systematic effect)."""
    name = "damp_wrap"

    def __init__(self, inner, op_seed: int):
        self.inner = inner
        self.op_seed = op_seed

    def reset(self, act_width: int, obs_width: int):
        self.inner.reset(act_width, obs_width)
        self.rd = stream("mhc-damp", self.op_seed)

    def act(self, obs):
        a = self.inner.act(obs)
        if self.rd.below(2) == 0:
            a = [max(0, x - 1) for x in a]
        return a


class P4_GenealogicalDrift(P1_DelayedDep):
    """FAMILY P4 -- MULTIGENERATION DIRECTIONAL DRIFT (signal class C).
    A lineage of players with epsilon growing by EPS_STEP per generation.
    Each individual sits below per-individual detection power; the lineage
    trend test is what must catch the direction."""
    name = "P4_lineage"
    EPS_STEP_MILLI = 60

    def __init__(self, seed: int, generation: int):
        super().__init__(seed, self.EPS_STEP_MILLI * generation)
        self.generation = generation


class P1_Diffuse(BasePlayer):
    """FAMILY P1-DIFFUSE (red-team revision: authored plants were basis-
    aligned with mu -- concentrated at one locus, one lag, one sign).
    This variant spreads the SAME effect budget across three stored elements,
    three lags {3,6,9}, and SIGN-MIXED action modulation, so the power curve
    measures the diffuse-effect class the target actually belongs to.
    Blindness statements must quote the WORST class."""
    name = "P1_diffuse"
    LAGS = (3, 6, 9)

    def __init__(self, seed: int, eps_milli: int):
        super().__init__(seed)
        self.eps_milli = eps_milli

    def reset(self, act_width: int, obs_width: int):
        super().reset(act_width, obs_width)
        self.rmod = stream("mhc-p1d-mod", self.seed)
        es = stream("mhc-p1d-elem", self.seed)
        self.js = [es.below(self.obs_width) for _ in range(3)]
        self.buf = []

    def act(self, obs):
        a = [self.r.below(8) for _ in range(self.act_width)]
        self.buf.append([obs[j] for j in self.js])
        if self.rmod.below(1000) < self.eps_milli and len(self.buf) > 9:
            for i, (lag, sign) in enumerate(zip(self.LAGS, (1, -1, 1))):
                par = self.buf[-1 - lag][i] & 1
                ch = i % self.act_width
                a[ch] = (a[ch] + sign * (1 + 2 * par)) % 8
        return a


class EchoBase(BasePlayer):
    """Memoryful BASE: genuine lag-2 dependence (action[0] modulated by the
    obs element seen 2 ticks ago), plus seeded randomness. Exists because an
    observation-blind base yields an EXACT-ZERO causal-depth null -- ties
    everywhere, degenerate false-positive calibration. Real nulls need a base
    whose D(k) is intrinsically noisy-positive, so candidate-vs-reference
    ranks are genuinely uniform under H0."""
    name = "echo_base"

    def reset(self, act_width: int, obs_width: int):
        super().reset(act_width, obs_width)
        self.j1 = stream("mhc-echo-elem", self.seed).below(self.obs_width)
        self.buf = []

    def act(self, obs):
        a = [self.r.below(8) for _ in range(self.act_width)]
        self.buf.append(obs[self.j1])
        if len(self.buf) > 2:
            a[0] = (a[0] + (self.buf[-3] & 1)) % 8
        return a


class P1_Echo(EchoBase):
    """P1 mechanism planted ON TOP of the memoryful EchoBase: the realistic
    power/FP column -- detect a tiny added lag-6 dependence against a base
    that already has genuine lag-2 structure. eps=0 is the matched control."""
    name = "P1_echo"
    LAG = 6

    def __init__(self, seed: int, eps_milli: int):
        super().__init__(seed)
        self.eps_milli = eps_milli

    def reset(self, act_width: int, obs_width: int):
        super().reset(act_width, obs_width)
        self.rmod = stream("mhc-p1e-mod", self.seed)
        self.j0 = stream("mhc-p1e-elem", self.seed).below(self.obs_width)
        self.buf6 = []

    def act(self, obs):
        a = super().act(obs)
        self.buf6.append(obs[self.j0])
        if (self.rmod.below(1000) < self.eps_milli
                and len(self.buf6) > self.LAG):
            a[-1] = 7 * (self.buf6[-1 - self.LAG] & 1)
        return a


class GreedyM(BasePlayer):
    """Functional (selected-point stand-in) player: repeats its last action
    when the observation sum rose, else redraws. Used for the FRAGILITY
    demONSTRATION: perturbing it generically degrades outcomes."""
    name = "greedy_m"

    def reset(self, act_width: int, obs_width: int):
        super().reset(act_width, obs_width)
        self.last_sum = None
        self.last_act = [0] * act_width

    def act(self, obs):
        s = sum(obs)
        if self.last_sum is not None and s >= self.last_sum:
            a = list(self.last_act)
        else:
            a = [self.r.below(8) for _ in range(self.act_width)]
        self.last_sum = s
        self.last_act = a
        return a


class NoisyWrap:
    """Perturbation operator dP for the fragility demo: with probability
    eps, replace the wrapped player's action with a fresh seeded draw.
    Distinct op_seed values are distinct draws from the SAME frozen
    perturbation distribution -- which is exactly what the reference-ensemble
    null ranks a specific dP against."""
    name = "noisy_wrap"

    def __init__(self, inner, op_seed: int, eps_milli: int = 200):
        self.inner = inner
        self.op_seed = op_seed
        self.eps_milli = eps_milli

    def reset(self, act_width: int, obs_width: int):
        self.inner.reset(act_width, obs_width)
        self.rn = stream("mhc-noise", self.op_seed)
        self.act_width = act_width

    def act(self, obs):
        a = self.inner.act(obs)
        if self.rn.below(1000) < self.eps_milli:
            a = [self.rn.below(8) for _ in range(self.act_width)]
        return a


# =====================================================================
# SEALED HELD-OUT FAMILY -- DO NOT USE IN TUNING. EVALUATED ONCE, LAST.
# Spec frozen 2026-09-02 before observables.py / stats.py were written.
# Effect class deliberately different from every tuning family:
# TEMPORALLY NON-STATIONARY, CURRENT-OBSERVATION, RELEVANCE-COUPLED.
# =====================================================================
class P5_Sealed(BasePlayer):
    """FAMILY P5 -- SEALED HOLDOUT. Inert for the first half of the episode.
    In the second half, with per-tick probability epsilon, action[0] is set
    from the CURRENT value of one seeded observation element (lag 0, not
    delayed). No tuning family has this shape: it should be invisible to the
    lag-grid causal-depth statistic used for P1/P2/P4 and visible only to
    the immediate-lag (k=0) relevant/irrelevant separation and trajectory
    coordinates -- IF the frozen family generalizes. If V0 is blind to it,
    that blindness is reported, not patched post hoc."""
    name = "P5_sealed"

    def __init__(self, seed: int, eps_milli: int, horizon: int):
        super().__init__(seed)
        self.eps_milli = eps_milli
        self.horizon = horizon

    def reset(self, act_width: int, obs_width: int):
        super().reset(act_width, obs_width)
        self.rmod = stream("mhc-p5-mod", self.seed)
        self.j0 = stream("mhc-p5-elem", self.seed).below(self.obs_width)
        self.t = 0

    def act(self, obs):
        a = [self.r.below(8) for _ in range(self.act_width)]
        self.t += 1
        if (self.t > self.horizon // 2
                and self.rmod.below(1000) < self.eps_milli):
            a[0] = obs[self.j0] % 8
        return a
