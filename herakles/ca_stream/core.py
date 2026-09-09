"""ca_stream_v1: a streaming wrapper over the radius-3 CA library. H2 alpha.

`herakles.evca` IS NOT MODIFIED. This module imports its step function and its
conventions and adds nothing to it. The density-classification kind keeps its
own identity, its own tests and its own qualification.

THE UPDATE ORDER, PINNED. Exactly this, once per time step, no exceptions:

    1. INJECT   write the input bit into the lattice at each declared port
    2. STEP     exactly one CA update of the whole lattice
    3. READ     take the features from the lattice AFTER the step

The features are the post-step lattice and nothing else. There is no
undeclared input history: the readout never sees the input bit directly, and
never sees any earlier lattice. Everything the readout can know about the past
is whatever the lattice itself carried forward. That is the whole point of the
experiment, so it is a structural property here rather than a convention.

RESET. `reset()` before every independent stream, to the declared initial
state, which is all zeros. Streams never see each other's state.

READOUT CLASS, DECLARED. A capacity-limited linear readout over the current
lattice: `n_cells` features plus one bias, fitted by ridge regression in
closed form with a fixed regularisation constant. No iterative search, no
hyperparameter selection, no feature engineering, and no access to anything
but the post-step lattice of the current time step.

FITTING BUDGET, DECLARED. One closed-form solve per (substrate, task). No
restarts. The training partition is the only data the fit ever receives; the
function signature makes that structural rather than a promise.

WHAT THIS MODULE REFUSES TO CONCLUDE. Nothing here attributes computation to
the substrate. A linear readout over 31 cells has real capacity, and the
readout-only and frozen-random baselines exist precisely to measure how much
of any score is the readout's. Attribution is a beta question and needs the
matched interventions this alpha does not perform.
"""
from __future__ import annotations

import hashlib
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from herakles import evca

#: Alpha defaults, all declared, none silently applied: every entry point
#: takes them explicitly and these exist only to be cited in one place.
N_CELLS = 31
HORIZON = 8
N_STREAMS = 1 << HORIZON          # 256, the complete catalogue
INITIAL_STATE = 0                 # all zeros
RIDGE_LAMBDA = 1.0
DECISION_THRESHOLD = 0.5


class CaStreamError(ValueError):
    """Any violation of a pinned convention."""


# ---------------------------------------------------------------------------
# Substrates. Each is reset/step(state, input) -> (state, features).
# The CA is the object of study; the others are controls with an identical
# interface so that readout capacity is matched by construction.
# ---------------------------------------------------------------------------

class Substrate:
    """Interface. `features` must always have width `self.width`."""

    name = "abstract"

    def __init__(self, n_cells: int):
        self.n_cells = int(n_cells)
        self.width = int(n_cells)

    def reset(self) -> None:
        raise NotImplementedError

    def step(self, bit: int) -> np.ndarray:
        raise NotImplementedError

    def descriptor(self) -> Dict[str, object]:
        return {"substrate": self.name, "n_cells": self.n_cells,
                "width": self.width}


class CaSubstrate(Substrate):
    """The radius-3 CA, driven by injection at declared ports.

    Order per step is inject, step, read. `ports` are lattice indices; each
    receives the same input bit in this alpha, which uses one port.
    """

    name = "ca_r3"

    def __init__(self, rule_hex: str, n_cells: int = N_CELLS,
                 ports: Sequence[int] = (0,)):
        super().__init__(n_cells)
        evca.require_lattice(n_cells)          # odd, >= 7, from the library
        self.table = evca.decode_table(rule_hex)
        self.rule_hex = rule_hex
        ports = tuple(int(p) for p in ports)
        if not ports:
            raise CaStreamError("at least one input port is required")
        for p in ports:
            if not (0 <= p < n_cells):
                raise CaStreamError("port %d outside the lattice" % p)
        if len(set(ports)) != len(ports):
            raise CaStreamError("duplicate port: %r" % (ports,))
        self.ports = ports
        self.state = None
        self.reset()

    def reset(self) -> None:
        self.state = np.full((1, self.n_cells), INITIAL_STATE, dtype=np.uint8)

    def step(self, bit: int) -> np.ndarray:
        if bit not in (0, 1):
            raise CaStreamError("input must be 0 or 1, got %r" % (bit,))
        for p in self.ports:                    # 1. inject
            self.state[0, p] = bit
        self.state = evca.step(self.state, self.table)   # 2. exactly one step
        return self.state[0].astype(np.float64).copy()   # 3. read

    def descriptor(self) -> Dict[str, object]:
        d = super().descriptor()
        d.update({"rule_hex": self.rule_hex, "ports": list(self.ports),
                  "radius": evca.RADIUS, "boundary": "periodic",
                  "initial_state": INITIAL_STATE})
        return d


class ShiftRegister(Substrate):
    """INSTRUMENT-POSITIVE CONTROL for delayed recall. Not a CA.

    Cell k holds the input from k steps ago. A linear readout can therefore
    solve delay d for any d < n_cells. It CANNOT solve temporal XOR, because
    XOR of two stored bits is not a linear function of them, and that
    limitation is a fact about the readout rather than about memory.
    """

    name = "shift_register"

    def __init__(self, n_cells: int = N_CELLS):
        super().__init__(n_cells)
        self.buf = None
        self.reset()

    def reset(self) -> None:
        self.buf = np.zeros(self.n_cells, dtype=np.float64)

    def step(self, bit: int) -> np.ndarray:
        self.buf = np.roll(self.buf, 1)
        self.buf[0] = float(bit)
        return self.buf.copy()


class ShiftXorRegister(Substrate):
    """INSTRUMENT-POSITIVE CONTROL for temporal XOR.

    A shift register plus one extra cell that holds the XOR of the two most
    recent stored bits at the declared delay. A linear readout can then solve
    XOR by reading that one cell. This proves the TASK and the composition
    interface can pass, and it is explicitly not a discovered CA mechanism.
    """

    name = "shift_xor"

    def __init__(self, n_cells: int = N_CELLS, delay: int = 1):
        super().__init__(n_cells)
        self.delay = int(delay)
        if not (0 <= self.delay < n_cells - 1):
            raise CaStreamError("delay %d does not fit the register"
                                % self.delay)
        self.buf = None
        self.reset()

    def reset(self) -> None:
        self.buf = np.zeros(self.n_cells, dtype=np.float64)

    def step(self, bit: int) -> np.ndarray:
        self.buf = np.roll(self.buf, 1)
        self.buf[0] = float(bit)
        a = self.buf[self.delay]
        b = self.buf[self.delay + 1]
        out = self.buf.copy()
        out[-1] = float(int(a) ^ int(b))        # the extra logic cell
        return out

    def descriptor(self) -> Dict[str, object]:
        d = super().descriptor()
        d["delay"] = self.delay
        return d


class DirectInput(Substrate):
    """BASELINE. The current input bit, with the readout budget EQUALISED.

    Width matches the CA exactly, so the readout has the same number of free
    parameters. Only the first feature carries information and it carries only
    the CURRENT bit, so this baseline must fail every delayed target. If it
    does not, the target is not testing memory.
    """

    name = "direct_input"

    def reset(self) -> None:
        pass

    def step(self, bit: int) -> np.ndarray:
        f = np.zeros(self.n_cells, dtype=np.float64)
        f[0] = float(bit)
        return f


class FrozenRandom(Substrate):
    """NULL BASELINE. A fixed random vector, independent of the input.

    Same width, same readout budget, zero information. Any score above the
    task's base rate here is an accounting error, not a result.
    """

    name = "frozen_random"

    def __init__(self, n_cells: int = N_CELLS, seed: int = 0):
        super().__init__(n_cells)
        self.seed = int(seed)
        rng = np.random.default_rng(self.seed)
        self.vec = rng.random(n_cells)

    def reset(self) -> None:
        pass

    def step(self, bit: int) -> np.ndarray:
        return self.vec.copy()

    def descriptor(self) -> Dict[str, object]:
        d = super().descriptor()
        d["seed"] = self.seed
        return d


# ---------------------------------------------------------------------------
# The frozen stream catalogue and the tasks
# ---------------------------------------------------------------------------

def all_streams(horizon: int = HORIZON) -> np.ndarray:
    """The complete 2^horizon Boolean catalogue, ascending integer order."""
    if horizon < 1 or horizon > 16:
        raise CaStreamError("horizon %r out of range" % (horizon,))
    idx = np.arange(1 << horizon, dtype=np.int64)
    return ((idx[:, None] >> np.arange(horizon - 1, -1, -1)[None, :]) & 1
            ).astype(np.uint8)


def target_delayed_recall(stream: np.ndarray, delay: int) -> np.ndarray:
    """y[t] = x[t - delay]. Undefined for t < delay."""
    y = np.zeros(len(stream), dtype=np.int8)
    for t in range(len(stream)):
        y[t] = stream[t - delay] if t >= delay else 0
    return y


def target_temporal_xor(stream: np.ndarray, delay: int) -> np.ndarray:
    """y[t] = x[t - delay] XOR x[t - delay - 1]. Undefined for t < delay + 1."""
    y = np.zeros(len(stream), dtype=np.int8)
    for t in range(len(stream)):
        if t >= delay + 1:
            y[t] = int(stream[t - delay]) ^ int(stream[t - delay - 1])
    return y


def warmup_mask(horizon: int, task: str, delay: int) -> np.ndarray:
    """True where the target is DEFINED. Declared, not inferred at fit time.

    A delayed target has no meaning before enough input has arrived. Scoring
    those steps would credit or blame a substrate for a question that was not
    asked.
    """
    m = np.zeros(horizon, dtype=bool)
    first = delay if task == "delayed_recall" else delay + 1
    m[first:] = True
    return m


TASKS: Dict[str, Callable[[np.ndarray, int], np.ndarray]] = {
    "delayed_recall": target_delayed_recall,
    "temporal_xor": target_temporal_xor,
}


# ---------------------------------------------------------------------------
# Partitions. Confirmation labels are structurally out of reach of fitting.
# ---------------------------------------------------------------------------

def partitions(n_streams: int = N_STREAMS, n_train: int = 64,
               n_dev: int = 64, seed: int = 20260909
               ) -> Dict[str, np.ndarray]:
    """Disjoint train / dev / confirmation stream indices.

    Seeded and recorded. The confirmation set is the remainder, so it cannot
    silently shrink if the other two change.
    """
    rng = np.random.default_rng(int(seed))
    perm = rng.permutation(n_streams)
    tr = np.sort(perm[:n_train])
    dv = np.sort(perm[n_train:n_train + n_dev])
    cf = np.sort(perm[n_train + n_dev:])
    if len(cf) != n_streams - n_train - n_dev:
        raise CaStreamError("partition arithmetic is wrong")
    return {"train": tr, "dev": dv, "confirmation": cf}


# ---------------------------------------------------------------------------
# Feature extraction, fitting, scoring
# ---------------------------------------------------------------------------

def run_streams(substrate: Substrate, streams: np.ndarray
                ) -> Tuple[np.ndarray, int]:
    """Features for every (stream, timestep). Resets before EVERY stream.

    Returns (features of shape (n_streams, horizon, width), ca_steps_used).
    """
    n, horizon = streams.shape
    feats = np.empty((n, horizon, substrate.width), dtype=np.float64)
    steps = 0
    for i in range(n):
        substrate.reset()
        for t in range(horizon):
            feats[i, t] = substrate.step(int(streams[i, t]))
            steps += 1
    return feats, steps


def fit_readout(train_features: np.ndarray, train_targets: np.ndarray,
                mask: np.ndarray, ridge_lambda: float = RIDGE_LAMBDA
                ) -> np.ndarray:
    """Closed-form ridge. Receives ONLY the training partition, by signature.

    There is no argument through which confirmation data could arrive, which
    is why this is a structural guarantee rather than a discipline.
    """
    n, horizon, width = train_features.shape
    X = train_features[:, mask, :].reshape(-1, width)
    y = train_targets[:, mask].reshape(-1).astype(np.float64)
    X = np.hstack([X, np.ones((X.shape[0], 1))])          # bias
    A = X.T @ X + ridge_lambda * np.eye(X.shape[1])
    return np.linalg.solve(A, X.T @ y)


def score_readout(features: np.ndarray, targets: np.ndarray,
                  mask: np.ndarray, weights: np.ndarray,
                  threshold: float = DECISION_THRESHOLD) -> Dict[str, float]:
    n, horizon, width = features.shape
    X = features[:, mask, :].reshape(-1, width)
    X = np.hstack([X, np.ones((X.shape[0], 1))])
    y = targets[:, mask].reshape(-1).astype(np.float64)
    pred = (X @ weights >= threshold).astype(np.float64)
    base = max(y.mean(), 1.0 - y.mean())      # majority-class base rate
    return {"accuracy": float((pred == y).mean()),
            "base_rate": float(base),
            "n_scored": int(y.size)}


def build_targets(streams: np.ndarray, task: str, delay: int) -> np.ndarray:
    fn = TASKS[task]
    return np.stack([fn(s, delay) for s in streams])


def catalogue_digest(streams: np.ndarray) -> str:
    h = hashlib.sha256()
    h.update(b"ca_stream_v1.catalogue|")
    h.update(np.ascontiguousarray(streams).tobytes())
    return "sha256:" + h.hexdigest()[:32]
