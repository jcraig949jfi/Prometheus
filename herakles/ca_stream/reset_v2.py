"""D-18 amendment v1: a declared non-uniform reset. NOT APPLIED TO THE ALPHA.

VERSIONED AND INERT BY DEFAULT. Nothing in `core.py` imports this module and
the alpha run does not use it. `ca_stream_v1` keeps the all-zero reset and its
obstruction result exactly as recorded. This is the code path for alternative
1, built so the operator can decide against measured evidence rather than
against an argument.

    amendment  D-18
    version    v1
    status     PROPOSED. Applying it creates ca_stream_v2, a NEW kind, because
               changing the reset changes what every previous number means.

WHAT IT CHANGES. One thing: the state a stream starts from.

    ca_stream_v1   reset to all zeros
    D-18 v1        reset to a seeded Bernoulli lattice at a declared density

Everything else is untouched: inject at declared ports, exactly one CA step,
read the post-step lattice; the linear readout over the current lattice; the
matched direct-input and frozen-random baselines; the disjoint partitions.

SEED COUPLING, AND WHY IT IS SEPARATED. The reset randomness must not carry
information about any target. If the reset seed were derived from the stream
index, and the target is a function of the stream, then the reset would be
correlated with the answer and a readout could learn the target from the
initial lattice without any input ever arriving.

So the reset seed is derived from a RESET ROOT that is independent of the
stream content, and the derivation is stated:

    reset_seed(i) = sha256("ca_stream.d18.v1|<reset_root>|<i>") -> 64 bits

where `i` is the stream's POSITION in the catalogue. Position is not the
target: two streams at adjacent positions have unrelated targets. The
independence is nevertheless CHECKED rather than assumed, by
`reset_leakage_probe`, which fits the declared readout on the reset lattices
alone with no input at all and asserts it cannot beat the base rate.

TRANSIENT ACTIVITY IS NOT COMPUTATION. A live lattice under a density rule is
busy for a while and then dies. Busy is not the same as input-dependent. The
development procedure below measures BOTH, separately, and neither is allowed
to stand in for the other:

    relaxation time   how long the lattice takes to reach a uniform state
                      with NO input at all
    driven response   whether injecting input changes the trajectory, measured
                      as the divergence between two runs from the SAME reset
                      lattice under two different input streams

A substrate can have a long relaxation time and zero driven response. That
combination looks alive and computes nothing, and it is exactly what this
procedure exists to detect before a horizon is chosen.

DEVELOPMENT ONLY. Every function here takes a `streams` argument and the
caller passes the TRAINING and DEVELOPMENT partitions. The confirmation
partition is never an input to horizon selection, reset-density selection or
any rule search. There is no argument through which it could arrive.
"""
from __future__ import annotations

import hashlib
from typing import Dict, List, Optional, Sequence

import numpy as np

from herakles import evca
from herakles.ca_stream import core as cs

AMENDMENT = "D-18"
AMENDMENT_VERSION = "v1"
STATUS = "PROPOSED"
#: Applying this creates a NEW kind rather than editing the alpha's.
PROPOSED_KIND = "ca_stream_v2"


def reset_seed(reset_root: int, stream_position: int) -> int:
    """Derived from POSITION, never from stream content or any target."""
    blob = ("ca_stream.d18.v1|%d|%d" % (int(reset_root),
                                        int(stream_position))).encode("ascii")
    return int.from_bytes(hashlib.sha256(blob).digest()[:8], "big")


class NonUniformResetCaSubstrate(cs.CaSubstrate):
    """The alpha substrate with ONE change: the reset state.

    `reset()` alone cannot know which stream is next, so the caller sets the
    stream position before each stream. `run_streams_v2` does that and is the
    only supported driver, so a caller cannot accidentally reuse one reset
    lattice across streams.
    """

    name = "ca_r3_nonuniform_reset"

    def __init__(self, rule_hex: str, n_cells: int = cs.N_CELLS,
                 ports: Sequence[int] = (0,), reset_density: float = 0.5,
                 reset_root: int = 20260910):
        self.reset_density = evca.require_density(reset_density)
        self.reset_root = int(reset_root)
        self._position = 0
        super().__init__(rule_hex, n_cells, ports)

    def set_position(self, i: int) -> None:
        self._position = int(i)

    def reset(self) -> None:
        rng = np.random.default_rng(reset_seed(self.reset_root,
                                               self._position))
        self.state = (rng.random((1, self.n_cells)) < self.reset_density
                      ).astype(np.uint8)

    def descriptor(self) -> Dict[str, object]:
        d = super().descriptor()
        d.update({"amendment": AMENDMENT, "amendment_version": AMENDMENT_VERSION,
                  "reset": "seeded Bernoulli", "reset_density": self.reset_density,
                  "reset_root": self.reset_root,
                  "reset_seed_derivation":
                      "sha256(ca_stream.d18.v1|reset_root|stream_position)"})
        return d


def run_streams_v2(substrate: NonUniformResetCaSubstrate,
                   streams: np.ndarray,
                   positions: Sequence[int]):
    """Like `core.run_streams`, but the reset lattice varies by position."""
    if len(positions) != streams.shape[0]:
        raise cs.CaStreamError("one position per stream is required")
    n, horizon = streams.shape
    feats = np.empty((n, horizon, substrate.width), dtype=np.float64)
    steps = 0
    for i in range(n):
        substrate.set_position(int(positions[i]))
        substrate.reset()
        for t in range(horizon):
            feats[i, t] = substrate.step(int(streams[i, t]))
            steps += 1
    return feats, steps


# ---------------------------------------------------------------------------
# The development-only measurement. Run BEFORE any horizon is fixed.
# ---------------------------------------------------------------------------

def relaxation_time(rule_hex: str, n_cells: int, reset_density: float,
                    reset_root: int, n_samples: int, max_steps: int
                    ) -> Dict[str, object]:
    """How long a live lattice survives with NO INPUT AT ALL.

    Undriven. The substrate is reset and stepped; the first step at which the
    lattice becomes uniform is recorded. A lattice that never becomes uniform
    within `max_steps` is reported as censored, not as a large number.
    """
    table = evca.decode_table(rule_hex)
    firsts: List[Optional[int]] = []
    for i in range(int(n_samples)):
        rng = np.random.default_rng(reset_seed(reset_root, i))
        state = (rng.random((1, n_cells)) < reset_density).astype(np.uint8)
        hit = None
        for t in range(1, int(max_steps) + 1):
            state = evca.step(state, table)
            s = int(state.sum())
            if s == 0 or s == n_cells:
                hit = t
                break
        firsts.append(hit)
    observed = [f for f in firsts if f is not None]
    return {"rule_hex": rule_hex, "n_samples": int(n_samples),
            "max_steps": int(max_steps),
            "n_reached_uniform": len(observed),
            "n_censored": len(firsts) - len(observed),
            "median_relaxation": (int(np.median(observed))
                                  if observed else None),
            "min_relaxation": (int(min(observed)) if observed else None),
            "max_relaxation": (int(max(observed)) if observed else None)}


def driven_response(rule_hex: str, n_cells: int, ports: Sequence[int],
                    reset_density: float, reset_root: int,
                    n_samples: int, horizon: int) -> Dict[str, object]:
    """Does the INPUT change the trajectory at all?

    Two runs from the IDENTICAL reset lattice, differing only in the injected
    stream. If the lattices are the same at every step, the substrate is not
    listening and any activity is transient, not computation.

    Reported per step as the mean Hamming divergence between the two
    trajectories, so a response that appears and then dies is visible as a
    curve rather than collapsed into one number.
    """
    table = evca.decode_table(rule_hex)
    ports = tuple(int(p) for p in ports)
    H = int(horizon)
    div = np.zeros(H, dtype=np.float64)
    ever = 0
    for i in range(int(n_samples)):
        rng = np.random.default_rng(reset_seed(reset_root, i))
        base = (rng.random((1, n_cells)) < reset_density).astype(np.uint8)
        sr = np.random.default_rng(reset_seed(reset_root + 1, i))
        a_bits = (sr.random(H) < 0.5).astype(np.uint8)
        b_bits = 1 - a_bits                       # maximally different stream
        sa, sb = base.copy(), base.copy()
        seen = False
        for t in range(H):
            for p in ports:
                sa[0, p] = a_bits[t]
                sb[0, p] = b_bits[t]
            sa = evca.step(sa, table)
            sb = evca.step(sb, table)
            d = int((sa != sb).sum())
            div[t] += d
            if d > 0:
                seen = True
        ever += int(seen)
    div /= float(n_samples)
    return {"rule_hex": rule_hex, "n_samples": int(n_samples),
            "horizon": H, "ports": list(ports),
            "mean_divergence_by_step": [round(float(x), 4) for x in div],
            "fraction_of_samples_ever_diverging": ever / float(n_samples),
            "max_mean_divergence": round(float(div.max()), 4)}


def reset_leakage_probe(rule_hex: str, n_cells: int, reset_density: float,
                        reset_root: int, streams: np.ndarray,
                        positions: Sequence[int], task: str, delay: int
                        ) -> Dict[str, object]:
    """Can the readout learn the target from the RESET LATTICE ALONE?

    No input is ever injected. If this beats the base rate, the reset seed is
    correlated with the target and the whole design is contaminated. This is
    the check that makes the seed-coupling claim evidence rather than an
    assertion.
    """
    table = evca.decode_table(rule_hex)
    n, horizon = streams.shape
    feats = np.empty((n, horizon, n_cells), dtype=np.float64)
    for i in range(n):
        rng = np.random.default_rng(reset_seed(reset_root,
                                               int(positions[i])))
        state = (rng.random((1, n_cells)) < reset_density).astype(np.uint8)
        for t in range(horizon):
            state = evca.step(state, table)          # no injection at all
            feats[i, t] = state[0].astype(np.float64)
    y = cs.build_targets(streams, task, delay)
    mask = cs.warmup_mask(horizon, task, delay)
    half = n // 2
    w = cs.fit_readout(feats[:half], y[:half], mask)
    r = cs.score_readout(feats[half:], y[half:], mask, w)
    r["leaks"] = bool(r["accuracy"] > r["base_rate"] + 1e-9)
    return r
