"""Proposed standing gate: runtime invariant guards that turn the mutation survivors into self-alarms.

Guards OBSERVE (never alter) a pipeline run through two patch layers:
  outer  (wraps the possibly corrupted assays.evaluate): what each evaluate call was ASKED for (ctrl, seeds,
          genome, physics) -- for protocol corruptions that rewrite arguments, the inner layer sees the rewrite;
  inner  (installed INSIDE, next to the engine): what was EXECUTED (World physics, table, ctrl, schedule,
          episodes, traces, transport counters).
A guard alarm is a disagreement between the two, or a violated design invariant. Every guard is written so
an input that should make it FAIL exists (tests/test_guards.py exercises each one on a known corruption).

G1  PHYSICS_PROVENANCE   executed World physics digest == physics passed by the protocol
G2  TOPOLOGY_PROVENANCE  executed neighbour table == topology.build(physics)
G3  SENSE_LIVE           an env-built schedule that has non-zero cues reaches the World non-zero
G4  MIRROR_INVARIANT     every Episode: y[2p+1] == -y[2p]
G5  CONDITION_PROVENANCE every World built inside an evaluate call runs the ctrl that call requested
G6  CONTROL_DISTINGUISHABLE  a requested control whose per-world accuracy equals the matched normal run is
                         flagged (a no-op control; also flags genuinely local specimens, as NOT_APPLICABLE)
G7  CRN_PAIRING          every control call uses exactly the seeds of the matched normal call
G8  HELD_DISJOINT        held (single-genome) seeds are disjoint from every multi-genome (selection) seed set
G9  GENOME_PROVENANCE    every single-genome held call evaluates the genome the search returned as champion
G10 SCORER_SELFTEST      score(ep, trace = y) == 1 and score(ep, -y) == 0 on the run's own episodes
G11 TRANSPORT_LIVE       a World with emitters, loss < 1 and no zero_comm must deliver >= 1 packet
G12 STATE_LIVE           readout S0 never changes in the second half of the schedule while it changed in the
                         first half, in every world of a World with a live schedule -> flag
G0  DEGENERATE_CONTROL   (advisory, baseline-visible) a control whose every pair is exactly .5 cannot fail
"""
from __future__ import annotations

import contextlib
import hashlib

import numpy as np
import torch

from . import env as _env  # noqa: F401
from . import operators as O
from prometheus.ananke import assays, envs, topology
from prometheus.ananke import engine as E


def _h(a) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(a, dtype=np.int64)).tobytes()).hexdigest()[:16]


class Guards:
    def __init__(self):
        self.calls = []          # outer evaluate calls
        self.worlds = []         # (world, requested ctrl label or None-context)
        self.episodes = []
        self.alarms = set()
        self._req = []           # stack of requested ctrl labels / physics digests
        self.champion = None

    # ---------------------------------------------------------------- layers
    @contextlib.contextmanager
    def outer(self):
        ev0 = assays.evaluate
        g = self

        def evaluate(ph, genomes, env, seeds, ctrl=None, **kw):
            lab = "none" if ctrl is None else ctrl.label()
            g._req.append((lab, ph.digest()))
            i0 = len(g.worlds)
            try:
                r = ev0(ph, genomes, env, seeds, ctrl=ctrl, **kw)
            finally:
                g._req.pop()
            made = [w for w, _, _ in g.worlds[i0:]]
            P = int(np.asarray(genomes).shape[0])
            g.calls.append({"P": P, "ctrl": lab, "ph": ph.digest(),
                            "seeds": tuple(int(s) for s in seeds),
                            "ws_exec": tuple(tuple(w.ws.cpu().tolist()) for w in made),
                            "genome_exec": tuple(_h(w.genome[0].cpu().numpy()[None]) for w in made) if P == 1
                            else None, "acc": r.acc.copy()})
            return r
        with O.patched([(assays, "evaluate", evaluate)]):
            yield self

    @contextlib.contextmanager
    def inner(self):
        init0, build0 = E.World.__init__, envs.build
        g = self

        def init(w, ph, *a, **k):
            init0(w, ph, *a, **k)
            g.worlds.append((w, g._req[-1] if g._req else None, ph.digest()))

        def build(ph, env, seeds):
            ep = build0(ph, env, seeds)
            g.episodes.append(ep)
            return ep
        with O.patched([(E.World, "__init__", init), (envs, "build", build)]):
            yield self

    # ---------------------------------------------------------------- checks
    def check(self) -> list[str]:
        A = set()
        for w, req, ph_passed in self.worlds:
            if req is not None and w.ph.digest() != req[1]:
                A.add("G1_PHYSICS_PROVENANCE")
            nbr, dist = topology.build(w.ph)
            if nbr is not None and w.nbr is not None and not np.array_equal(w.nbr.cpu().numpy(), nbr):
                A.add("G2_TOPOLOGY_PROVENANCE")
            if req is not None:
                want = req[0]
                if want != w.ctrl.label() and not (want == "none" and w.ctrl.label() == "none"):
                    A.add("G5_CONDITION_PROVENANCE")
            st = {k: int(v.sum()) for k, v in w.stats.items()}
            if (st["emitters"] > 0 and w.ph.loss < 1.0 and not w.ctrl.zero_comm and st["delivered"] == 0
                    and w.t > 0):
                A.add("G11_TRANSPORT_LIVE")
            tr = w.trace.cpu().numpy()
            T = min(w.t, tr.shape[0])
            if T >= 8 and w.Tsch > 1 and w.B >= 16:
                # a live specimen's readout keeps changing; under i.i.d. targets a pair shows no change in
                # half a schedule with small probability, so require >= 16 worlds and >= 90% of the worlds that
                # changed in the first half to be silent in the second (a 4-world batch tripped a stricter form)
                h = T // 2
                d1 = (np.diff(tr[:h], axis=0) != 0).any(0).any(-1)
                d2 = (np.diff(tr[h - 1:T], axis=0) != 0).any(0).any(-1)
                if d1.sum() >= 8 and (d1 & ~d2).sum() >= 0.9 * d1.sum():
                    A.add("G12_STATE_LIVE")
        for ep in self.episodes:
            y = ep.y
            if y.shape[0] % 2 == 0 and not (y[1::2] == -y[0::2]).all():
                A.add("G4_MIRROR_INVARIANT")
            if (ep.schedule.sense_val != 0).any():
                live = [w for w, _, _ in self.worlds if w.sch_val.shape[1:] and (w.sch_val == 0).all()]
                if live:
                    A.add("G3_SENSE_LIVE")
            sel = ep.scored
            perfect = envs.score(ep, _trace_from(ep, ep.y))
            inverse = envs.score(ep, _trace_from(ep, -ep.y))
            if not (np.allclose(perfect, 1.0) and np.allclose(inverse, 0.0)):
                A.add("G10_SCORER_SELFTEST")
            del sel
        normals = [c for c in self.calls if c["ctrl"] == "none" and c["P"] == 1]
        for c in self.calls:
            if c["P"] != 1 or c["ctrl"] == "none":
                continue
            match = [n for n in normals if n["seeds"] == c["seeds"]]
            if not match or not any(n["ws_exec"] == c["ws_exec"] for n in match):
                A.add("G7_CRN_PAIRING")
            elif any(np.array_equal(n["acc"], c["acc"]) for n in match):
                A.add("G6_CONTROL_DISTINGUISHABLE")
            if c["acc"].size and (c["acc"].reshape(-1, 2).mean(-1) == 0.5).all():
                A.add("G0_DEGENERATE_CONTROL")
        sel_seeds = set()
        for c in self.calls:
            if c["P"] > 1:
                sel_seeds |= set(c["seeds"])
        for c in self.calls:
            if c["P"] == 1 and sel_seeds & set(c["seeds"]):
                A.add("G8_HELD_DISJOINT")
        if self.champion is not None:
            ch = _h(np.asarray(self.champion)[None])
            if any(c["P"] == 1 and any(x != ch for x in c["genome_exec"]) for c in self.calls):
                A.add("G9_GENOME_PROVENANCE")
        self.alarms = A
        return sorted(A)


def _trace_from(ep, y):
    """A trace whose readout equals y * 256 at every scored readout tick (0 elsewhere)."""
    B, tr = ep.y.shape
    T = int(ep.ro_tick.max()) + 1
    A = ep.schedule.read_idx.shape[1]
    t = np.zeros((T, B, A), dtype=np.int64)
    t[ep.ro_tick, np.arange(B)[:, None], ep.ro_slot] = 256 * y
    return t


@contextlib.contextmanager
def guarded(op=None):
    """with guarded(op) as g: <run a stage>; g.check()  (check INSIDE the block: G10 must see the live scorer).
    Layering: operator (outermost: it is the corrupted protocol/engine) > outer guard (sees what the protocol
    requested of assays.evaluate) > inner guard (sees what the engine executed)."""
    g = Guards()
    ctx = op.active() if op is not None else contextlib.nullcontext()
    with ctx:
        with g.outer():
            with g.inner():
                yield g
