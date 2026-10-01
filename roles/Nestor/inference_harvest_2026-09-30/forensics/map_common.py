"""Shared setup for the T6 map-predicts-outcomes forensics (map_*.py). Read-only on campaign code.

Reproduces the implanted-panel experiments' single-interaction setting exactly:
  world.z8 = run_dc.dense_z8()                       (dense VM, as run_rs.job / run_br.job)
  base = run_ds.cells()[run_br.SPEC7]; cell CF = dict(base["cell"], atlas_axis="NONE",
         representation="Z8_SLOTTED", structure="NICHES_HIGH_MIG")   (run_br.CELLS["CF"])
  runner class = run_rs.runner(world, policy, prng)  (ATOMIC run_ds.runner_cls + the register policy)
The runner is only constructed, never .run(): each interaction is one call of the world's own
_pair_interact on two placed organisms (so conversion, the P-11 causal assay, ATOMIC write-back and the
post-interaction mutation are the world's code, unchanged). No world/evolution run happens.
"""
from __future__ import annotations

import pathlib
import random
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
NESTOR = HERE.parents[1]
CAMP = NESTOR / "campaigns"
P2 = CAMP / "npe-p2-endogenous-heredity-2026-09-27"
W1 = CAMP / "npe-w1-donor-discovery-2026-09-26"
for p in (P2 / "x_p2_regstate", P2 / "x_p2_bridge", W1 / "x_dd_stateless", W1 / "x_dd_establish",
          W1 / "x_dd_dense_copy", W1 / "x_donor_discovery", CAMP / "c9x-explore-2026-09-24" / "x_donor_swap",
          CAMP / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))

import world  # noqa: E402
import p11  # noqa: E402
import run_dc  # noqa: E402
import run_ds  # noqa: E402
import run_br  # noqa: E402
import run_rs  # noqa: E402

DENSE = run_dc.dense_z8()
world.z8 = DENSE
BASE = run_ds.cells()[run_br.SPEC7]


def celld(cell="CF"):
    return dict(BASE["cell"], atlas_axis="NONE", **run_br.CELLS[cell])


class Harness:
    """Two placed organisms in a never-run runner; one world _pair_interact per call."""

    def __init__(self, policy, seed, cell="CF"):
        world.z8 = DENSE
        self.prng = random.Random(repr(("MAP", seed, policy)))
        base = run_rs.runner(world, policy if policy in ("ZERO", "CONST", "RANDOM") else "CARRY", self.prng)
        births = self.births = []

        class H(base):
            def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
                births.append((parent, bool(causal)))

        self.r = H(celld(cell), seed, tier=BASE["tier"])
        self.r.t["epochs"] = 0
        self.n = self.r.L
        self.d = self.r._place(bytes(self.n), 0)
        self.p = self.r._place(bytes(self.n), 1)
        self.k = 0

    def _set(self, o, g, anc):
        r = self.r
        r.mem[o.slot:o.slot + r.slot_size] = bytes(r.slot_size)
        r.mem[o.slot:o.slot + len(g)] = g
        o.length = len(g)
        o.anc = anc

    def interact(self, g, pg, side, d_state=None, p_state=None):
        """Donor genome g (anc 0) vs partner pg (anc 1); donor at tape side `side`.
        d_state / p_state = (regs, fz, fc) set before the call (the policy class may then override them).
        Returns a record of the outcome."""
        r = self.r
        self._set(self.d, g, 0)
        self._set(self.p, pg, 1)
        for o, st in ((self.d, d_state), (self.p, p_state)):
            if st is not None:
                o.regs = None if st[0] is None else list(st[0])
                o.fz, o.fc = st[1], st[2]
        d_oid, p_oid = self.d.oid, self.p.oid
        del self.births[:]
        r.epoch = self.k            # varies the P-11 assay seeds between calls
        self.k += 1
        a, b = (self.d, self.p) if side == 0 else (self.p, self.d)
        r._pair_interact(0, a, b)
        conv_p = [c for (par, c) in self.births if par == d_oid]     # donor converted the partner
        conv_d = [c for (par, c) in self.births if par == p_oid]     # partner converted the donor (hijack)
        gd, gp = r._genome(self.d), r._genome(self.p)
        return {"d_kept": not conv_d, "p_conv": bool(conv_p), "p_conv_causal": bool(conv_p and conv_p[0]),
                "gd": gd, "gp": gp, "d_state": (None if self.d.regs is None else list(self.d.regs), self.d.fz, self.d.fc),
                "p_state": (None if self.p.regs is None else list(self.p.regs), self.p.fz, self.p.fc),
                "d_tel": self.d.last_tel, "label": (self.d.anc == 0) + (self.p.anc == 0)}


def ident(a, b, pos=None):
    if pos is None:
        return p11.fidelity(a, b)
    if not pos:
        return 0.0
    return sum(1 for j in pos if j < len(a) and j < len(b) and a[j] == b[j]) / len(pos)


def gw_survival(p0, p1, p2):
    """s = 1 - q, q the smallest root in [0,1] of q = p0 + p1 q + p2 q^2 (p0+p1+p2 = 1): q = min(1, p0/p2)."""
    if p2 <= p0:
        return 0.0
    return 1.0 - p0 / p2


def rand_genome(rng, n=64):
    return bytes(rng.randrange(256) for _ in range(n))
