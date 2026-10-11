"""NS-01 witness library: executable minimal witnesses of the archived mechanism behaviours (FAILURE_ATLAS tier M),
plus viable references. Each entry: name -> (factory make(task) -> System, archived behaviour, evidence pointer).
Knobs are fixed here so every witness is one mechanism, not a family."""
from __future__ import annotations

import numpy as np

from prometheus.cosmos.c3.calib import DelayLine, NoMemory, Register
from prometheus.cosmos.c3.substrates import RNN, Graph, Stig
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot
from prometheus.cosmos.c4.families.cosmos_phase import world as PH
from prometheus.cosmos.c4.families.theseus_sediment import world as SED
from prometheus.cosmos.c4.planted import HiddenCarrier, Reservoir, RotReservoir


class SignMaskedRegister(System):
    """Planted LINEAR-BLIND witness for V-way cues: holds onehot(cue) x s with a random sign s per episode, so every
    class has zero mean in every coordinate (a linear readout sees chance) while |m| carries the cue exactly.
    V-generic replacement for XorCue (which needs V = 2; the NS-01 contract fixes V = 4)."""

    def __init__(self, task: Task):
        self.t = task

    def init(self, E):
        return {"m": np.zeros((E, self.t.V)), "cur": np.zeros(E, dtype=np.int64), "t": np.zeros(E, dtype=np.int64)}

    def noise(self, n, rng):
        return {"s": rng.integers(0, 2, n) * 2.0 - 1.0}

    def step(self, st, o, nz):
        o = np.asarray(o)
        m = st["m"].copy()
        first = st["t"] == 0
        if first.any():
            m[first] = np.eye(self.t.V)[np.clip(o[first], 0, self.t.V - 1)] * nz["s"][first, None]
        return {"m": m, "cur": o.copy(), "t": st["t"] + 1}

    def readout_features(self, st):
        return np.hstack([st["m"], onehot(st["cur"], self.t.n_symbols)])

    def full_state(self, st):
        return np.hstack([st["m"], onehot(st["cur"], self.t.n_symbols), st["t"][:, None].astype(float)])


_PH = PH.sample_natural(np.random.default_rng(11))
_SED = SED.sample_natural(np.random.default_rng(12))

WITNESSES = {
    "nomemory": (lambda t: NoMemory(t), "DEGENERATE: cue never retained", "c3/calib.py NoMemory (N0)"),
    "delayline": (lambda t: DelayLine(t), "viable reference (exact delay)", "c3/calib.py DelayLine (FD)"),
    "register": (lambda t: Register(t, read_register=True), "viable reference (clean register)", "c3/calib.py FX"),
    "register_unread": (lambda t: Register(t, read_register=False), "M-UNREACHABLE: held but not read (PASSIVE)",
                        "c3/calib.py PV"),
    "reservoir_fast": (lambda t: Reservoir(t, 0.5, 0.3, wseed=1), "M-DECAY: contraction loses the cue",
                       "c4/planted.py; EXP-06/07"),
    "reservoir_slow": (lambda t: Reservoir(t, 0.95, 0.1, wseed=1), "slow decay", "c4/planted.py; EXP-06/07"),
    "rotreservoir": (lambda t: RotReservoir(t, 0.9, 0.3, wseed=1), "slow decay, rotated (equivalent to reservoir)",
                     "c4/planted.py"),
    "signmasked": (lambda t: SignMaskedRegister(t), "M-LINBLIND: readable only nonlinearly",
                   "NS-01 planted (V-generic XorCue, c4/planted.py XorCue)"),
    "hidden": (lambda t: HiddenCarrier(t), "M-HIDDEN: carrier outside the declared state", "c4/planted.py"),
    "rnn": (lambda t: RNN(t, 0.9, 0.5, 0.1, wseed=3), "near-linear decaying memory", "c3/substrates.py; EXP-01/02"),
    "graph": (lambda t: Graph(t, 3, -0.3, 0.03, wseed=3), "threshold network", "c3/substrates.py; EXP-01/02"),
    "stig_static": (lambda t: Stig(t, 0.1, 0.0, 0, 0.0), "trace + static sensor", "EXP-05 v = 0"),
    "stig_moving": (lambda t: Stig(t, 0.1, 0.0, 1, 0.0), "M-NONMONOTONE / M-UNREACHABLE: moving sensor, ring return",
                    "EXP-01 stig; EXP-05"),
    "stig_diffusing": (lambda t: Stig(t, 0.05, 0.25, 2, 0.1), "diffusing trace + moving sensor (H-SPREAD)",
                       "EXP-05/09"),
    "phase": (lambda t: PH.build_world(**_PH), "phase coding", "c4/families/cosmos_phase; EXP-03"),
    "sediment": (lambda t: SED.build_world(**_SED), "transport ledger (foreign family)",
                 "c4/families/theseus_sediment; EXP-01/02"),
}
