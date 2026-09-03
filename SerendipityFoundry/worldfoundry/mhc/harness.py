"""Encounter harness + interventional replay machinery.

REVISED PER RED TEAM (findings preserved in the packet):
  * Interventional causal depth uses the OPEN-LOOP protocol, preregistered:
    the player is re-run against the RECORDED observation stream with exactly
    one element flipped; the world is never re-stepped, so world chaos
    contributes exactly zero and the exactness claims hold.
  * IMMEDIATE-ACTION STRATIFICATION: an intervention whose action at the
    intervened tick already differs is a REACTIVITY event (lag-0 coordinate);
    lag-k dependence D(k) is computed ONLY on interventions whose immediate
    action was unchanged -- later divergence can then flow only through
    stored internal state, which kills the reactivity-x-recurrence confound.
  * Interventions are PLAYER-FACING (applied to the observation the player
    actually saw, i.e. post-permutation, post-corruption).
  * Twin discipline: all players in a block are independent seeded draws;
    the corruption stream is a function of (world, episode seed, slot) only,
    so twins face bit-identical corruption by construction (verified in
    qualification).
"""
from __future__ import annotations

from wforge.world import Encounter, Mechanics


def run_recorded(mech: Mechanics, world_id: str, ep_seed: int, player):
    """Run one solo encounter, recording the player-facing observation stream
    and the emitted action stream. Returns (obs_seq, act_seq, outcome)."""
    enc = Encounter(mech, world_id, ep_seed)
    obs_w = len(mech.obs_perm)
    player.reset(mech.act_width, obs_w)
    obs_seq, act_seq = [], []
    done = False
    while not done:
        obs = enc.observe(0)
        act = player.act(obs)
        obs_seq.append(obs)
        act_seq.append(list(act))
        done = enc.step([act])
    return obs_seq, act_seq, enc.outcome()


def open_loop_replay(player_factory, obs_seq, flip_tick: int, flip_elem: int,
                     act_width: int):
    """Replay the PLAYER ONLY against the recorded observation stream with one
    element flipped at one tick. Deterministic; the world is not re-stepped.
    Returns the counterfactual action sequence."""
    player = player_factory()
    player.reset(act_width, len(obs_seq[0]))
    acts = []
    for t, obs in enumerate(obs_seq):
        if t == flip_tick:
            obs = list(obs)
            obs[flip_elem] ^= 1          # minimal single-bit intervention
        acts.append(list(player.act(obs)))
    return acts


class CausalProbe:
    """Interventional causal-depth probe for one recorded encounter.

    For each seeded anchor tick tau: flip one seeded observation element at
    tau, open-loop replay, compare actions at offsets {0} + LAGS.
      offset 0 differs  -> REACTIVITY event (counted separately, mu2.r0)
      offset 0 same     -> clean stratum; D(k) counts a divergence at tau+k
    All counts are integers; D values are (count, trials) pairs.
    """
    LAGS = (2, 6, 12)

    def __init__(self, n_anchors: int = 6):
        self.n_anchors = n_anchors

    def profile(self, player_factory, obs_seq, base_acts, anchor_stream):
        T = len(obs_seq)
        span = T - max(self.LAGS) - 2
        result = {
            "r0_count": 0, "r0_trials": 0,
            "d_counts": {k: 0 for k in self.LAGS},
            "d_trials": {k: 0 for k in self.LAGS},
        }
        if span < 8:
            return result                 # episode too short; uninformative
        obs_w = len(obs_seq[0])
        act_w = len(base_acts[0])
        for _ in range(self.n_anchors):
            tau = 4 + anchor_stream.below(span - 4)
            elem = anchor_stream.below(obs_w)
            cf = open_loop_replay(player_factory, obs_seq, tau, elem, act_w)
            immediate_changed = cf[tau] != base_acts[tau]
            result["r0_trials"] += 1
            if immediate_changed:
                result["r0_count"] += 1
                continue                  # reactivity stratum; not depth
            for k in self.LAGS:
                if tau + k < T:
                    result["d_trials"][k] += 1
                    if cf[tau + k] != base_acts[tau + k]:
                        result["d_counts"][k] += 1
        return result

    @staticmethod
    def area(profile) -> int:
        """Integer summary: total clean-stratum divergences across lags."""
        return sum(profile["d_counts"].values())


def trajectory_contrast(act_seq, shuffle_stream) -> int:
    """mu4: held-out order-2 hit-count contrast, integer-exact.
    Train counts on the first half, score argmax hit-count on the second
    half; contrast against the same procedure on a seeded within-player
    shuffle (destroys order, preserves marginals). Both nulls (shuffle here,
    rotation available in analysis) are preregistered sub-coordinates."""
    syms = [tuple(a) for a in act_seq]
    n = len(syms)
    if n < 24:
        return 0

    def hits(seq):
        half = len(seq) // 2
        table = {}
        for i in range(2, half):
            table.setdefault((seq[i - 2], seq[i - 1]), {})
            d = table[(seq[i - 2], seq[i - 1])]
            d[seq[i]] = d.get(seq[i], 0) + 1
        h = 0
        for i in range(max(2, half), len(seq)):
            d = table.get((seq[i - 2], seq[i - 1]))
            if d:
                best = max(sorted(d), key=lambda s: d[s])
                if best == seq[i]:
                    h += 1
        return h

    shuffled = list(syms)
    for i in range(len(shuffled) - 1, 0, -1):    # seeded Fisher-Yates
        j = shuffle_stream.below(i + 1)
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    return hits(syms) - hits(shuffled)
