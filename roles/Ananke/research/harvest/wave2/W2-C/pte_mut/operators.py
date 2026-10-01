"""Mutation operators for PTE experimental semantics.

Every operator is a context manager that corrupts ONE aspect of a PTE experiment by monkeypatching
prometheus.ananke attributes (never editing a file) and restores every attribute on exit, also on error.
Each operator states its METAMORPHIC RELATION (MR): what a correct pipeline must output when the experiment
is corrupted this way. The mutation score (score.py) checks whether the real pipeline output CHANGES at the
verdict level or ALARMS.

Layers:
  engine    the World executes different physics/IO than the one recorded (oracle conformance can see it);
  protocol  the experiment's arms / seeds / labels / scoring are wired wrongly (only the pipeline can see it).

Patch points (all module attributes looked up at call time, so a patch reaches every caller):
  engine.World.__init__ / set_schedule / _tick / _emit   (shared class object: assays, lens, lens_swap, campaign)
  assays.evaluate, assays.twin_assay, assays.world_seeds  (search.evolve, campaign, run_controls call these by
                                                           module attribute or module-global name)
  envs.build, envs.score, envs.per_trial                  (assays, lens_swap, campaign use envs.<name>)
  lens_swap.run_arms                                      (mixture_scan calls it as a module global)
  search.H_int                                            (evolve derives its seed namespaces through it)
"""
from __future__ import annotations

import contextlib
import dataclasses
import functools

import numpy as np
import torch

from . import env as _env  # noqa: F401
from prometheus.ananke import assays, envs, lens_swap, rng, search
from prometheus.ananke import engine as E
from prometheus.ananke.engine import Controls

ORIG = {
    "World.__init__": E.World.__init__, "World.set_schedule": E.World.set_schedule,
    "World._tick": E.World._tick, "World._emit": E.World._emit,
    "assays.evaluate": assays.evaluate, "assays.twin_assay": assays.twin_assay,
    "envs.build": envs.build, "envs.score": envs.score, "envs.per_trial": envs.per_trial,
    "lens_swap.run_arms": lens_swap.run_arms, "search.H_int": search.H_int,
}


@contextlib.contextmanager
def patched(pairs):
    """pairs: [(obj, attr, new)]; restores the exact previous attribute values (also on exception)."""
    saved = []
    try:
        for obj, attr, new in pairs:
            saved.append((obj, attr, getattr(obj, attr)))
            setattr(obj, attr, new)
        yield
    finally:
        for obj, attr, old in reversed(saved):
            setattr(obj, attr, old)


def originals_intact() -> bool:
    cur = {
        "World.__init__": E.World.__init__, "World.set_schedule": E.World.set_schedule,
        "World._tick": E.World._tick, "World._emit": E.World._emit,
        "assays.evaluate": assays.evaluate, "assays.twin_assay": assays.twin_assay,
        "envs.build": envs.build, "envs.score": envs.score, "envs.per_trial": envs.per_trial,
        "lens_swap.run_arms": lens_swap.run_arms, "search.H_int": search.H_int,
    }
    return all(cur[k] is ORIG[k] for k in ORIG)


# ------------------------------------------------------------------ world registry (fingerprints)
class Registry:
    """Records every World built inside a stage, so the score can tell an inert mutant (bit-identical worlds)
    from a live one. Installed by the stage runner, not by operators."""

    def __init__(self):
        self.worlds = []

    @contextlib.contextmanager
    def install(self):
        reg = self
        cur_init = E.World.__init__

        def init(self, *a, **k):
            cur_init(self, *a, **k)
            reg.worlds.append(self)
        with patched([(E.World, "__init__", init)]):
            yield self

    def fingerprints(self) -> list[str]:
        import hashlib
        out = []
        for w in self.worlds:
            h = hashlib.sha256()
            h.update(w.trace.cpu().numpy().tobytes())
            h.update(w.digest().encode())
            out.append(h.hexdigest()[:16])
        return sorted(out)


# ------------------------------------------------------------------ operator base
@dataclasses.dataclass
class Operator:
    name: str
    layer: str                      # engine | protocol
    mr: str                         # the metamorphic relation, in words
    stages: tuple                   # stages where the operator has a meaning
    sp_override: dict = dataclasses.field(default_factory=dict)   # protocol parameter corruption (held stage)

    def patches(self) -> list:
        raise NotImplementedError

    @contextlib.contextmanager
    def active(self):
        with patched(self.patches()):
            yield self


ALL_STAGES = ("held", "controls", "plant", "lens_swap", "report", "oracle")


def _is_single(genomes) -> bool:
    return np.asarray(genomes).shape[0] == 1


# ------------------------------------------------------------------ protocol operators on assay arms
class SwapConditionLabels(Operator):
    """normal <-> zero_comm arm results exchanged (single-genome assay calls); site <-> channel swap arms in
    lens_swap."""

    def patches(self):
        ev = assays.evaluate
        ra = lens_swap.run_arms

        def evaluate(ph, genomes, env, seeds, ctrl=None, **kw):
            if _is_single(genomes):
                if ctrl is None:
                    return ev(ph, genomes, env, seeds, ctrl=Controls(zero_comm=True), **kw)
                if ctrl.zero_comm and ctrl.label() == "zero_comm":
                    return ev(ph, genomes, env, seeds, ctrl=None, **kw)
            return ev(ph, genomes, env, seeds, ctrl=ctrl, **kw)

        def run_arms(*a, **k):
            r = ra(*a, **k)
            for lab in list(r.per_trial):
                if lab.startswith("site@"):
                    other = "chan@" + lab[5:]
                    for d in (r.per_trial, r.s0, r.trace):
                        d[lab], d[other] = d[other], d[lab]
            return r
        return [(assays, "evaluate", evaluate), (lens_swap, "run_arms", run_arms)]


class DuplicateCondition(Operator):
    """The control arm is a duplicate of the treatment arm: every single-genome control call returns the
    normal run (same physics, ctrl None); in lens_swap the channel arm is a copy of the site arm."""

    def patches(self):
        ev = assays.evaluate
        ra = lens_swap.run_arms
        last = {}

        def evaluate(ph, genomes, env, seeds, ctrl=None, **kw):
            if _is_single(genomes):
                if ctrl is None:
                    last["ph"] = ph
                else:
                    return ev(last.get("ph", ph), genomes, env, seeds, ctrl=None, **kw)
            return ev(ph, genomes, env, seeds, ctrl=ctrl, **kw)

        def run_arms(*a, **k):
            r = ra(*a, **k)
            for lab in list(r.per_trial):
                if lab.startswith("site@"):
                    other = "chan@" + lab[5:]
                    for d in (r.per_trial, r.s0, r.trace):
                        d[other] = d[lab].copy()
            return r
        return [(assays, "evaluate", evaluate), (lens_swap, "run_arms", run_arms)]


class PermuteSeedsBetweenArms(Operator):
    """Common random numbers broken: control arms run on the world list rotated by one mirror pair
    (single-genome assay calls); lens_swap arm outputs are rotated by one pair against the normal arm."""

    def patches(self):
        ev = assays.evaluate
        ra = lens_swap.run_arms

        def evaluate(ph, genomes, env, seeds, ctrl=None, **kw):
            if _is_single(genomes) and ctrl is not None:
                seeds = list(np.roll(np.asarray(seeds, dtype=np.int64), 2).tolist())
            return ev(ph, genomes, env, seeds, ctrl=ctrl, **kw)

        def run_arms(*a, **k):
            r = ra(*a, **k)
            for lab in list(r.per_trial):
                if lab != "normal":
                    r.per_trial[lab] = np.roll(r.per_trial[lab], 2, axis=0)
                    r.s0[lab] = np.roll(r.s0[lab], 2, axis=0)
                    r.trace[lab] = np.roll(r.trace[lab], 2, axis=1)
            return r
        return [(assays, "evaluate", evaluate), (lens_swap, "run_arms", run_arms)]


class SeverSearchRuler(Operator):
    """The held-out ruler measures a RANDOM genome while the row records the evolved champion (every
    single-genome evaluate / twin_assay call gets the random genome)."""

    def patches(self):
        ev, tw = assays.evaluate, assays.twin_assay
        cache = {}

        def rand_like(genomes):
            g = np.asarray(genomes)
            key = g.shape
            if key not in cache:
                r = np.random.default_rng(0xBAD5EED).integers(0, 256, size=g.shape)
                r[..., 4] = np.random.default_rng(0xBAD5EED + 1).integers(-128, 128, size=g.shape[:-1])
                cache[key] = r
            return cache[key]

        def evaluate(ph, genomes, env, seeds, ctrl=None, **kw):
            if _is_single(genomes):
                genomes = rand_like(genomes)
            return ev(ph, genomes, env, seeds, ctrl=ctrl, **kw)

        def twin_assay(ph, genomes, env, seeds, *a, **kw):
            if _is_single(genomes):
                genomes = rand_like(genomes)
            return tw(ph, genomes, env, seeds, *a, **kw)
        return [(assays, "evaluate", evaluate), (assays, "twin_assay", twin_assay)]


class ReuseSelectionSeeds(Operator):
    """The champion is selected on the held-out worlds and then 'held-out' evaluated on them: evolve's FINAL
    (selection) namespace is redirected to the HELD namespace and M_final is set to M_held."""

    def patches(self):
        H = search.H_int

        def H_int(*keys):
            if len(keys) == 2 and keys[1] == search.FINAL_NS:
                return H(keys[0], search.HELD_NS)
            return H(*keys)
        return [(search, "H_int", H_int)]


class DropMirror(Operator):
    """Mirror pairs lose their negation: world 2p+1 gets EXACTLY world 2p's inputs and targets."""

    def patches(self):
        b0 = envs.build

        def build(ph, env, world_seeds):
            ep = b0(ph, env, world_seeds)
            sv = ep.schedule.sense_val
            sv[:, 1::2] = sv[:, 0::2]
            ep.y[1::2] = ep.y[0::2]
            return ep
        return [(envs, "build", build)]


class InvertActuatorSign(Operator):
    """The readout's sign convention is inverted at scoring time (score / per_trial see -S0)."""

    def patches(self):
        sc, pt = envs.score, envs.per_trial

        def score(ep, trace):
            return sc(ep, -np.asarray(trace))

        def per_trial(ep, trace):
            return pt(ep, -np.asarray(trace))
        return [(envs, "score", score), (envs, "per_trial", per_trial)]


# ------------------------------------------------------------------ engine operators
class DisableChannel(Operator):
    """Every EMIT is dropped at transport (want := False inside _emit; the tick's emitter bookkeeping, which
    is counted before _emit, still sees the emitters)."""

    def patches(self):
        em = E.World._emit

        def _emit(self, want, chan, pay):
            return em(self, torch.zeros_like(want), chan, pay)
        return [(E.World, "_emit", _emit)]


class ControlIgnored(Operator):
    """Every Controls switch is silently ignored by the engine (World built with Controls())."""

    def patches(self):
        init = E.World.__init__

        def __init__(self, ph, genomes, world_seeds, device="cuda", ctrl=None, schedule=None, census=False):
            init(self, ph, genomes, world_seeds, device=device, ctrl=None, schedule=schedule, census=census)
        return [(E.World, "__init__", __init__)]


class FreezeState(Operator):
    """Site state S is frozen after tick t0 = frac * Tsch (writes reverted; the readout trace records the
    frozen S0)."""

    def __init__(self, *a, frac: float = 0.5, **k):
        super().__init__(*a, **k)
        self.frac = frac

    def patches(self):
        tk = E.World._tick
        frac = self.frac

        def _tick(self):
            t = self.t
            t0 = int(frac * self.Tsch)
            if t < t0:
                return tk(self)
            S_old = self.S.clone()
            tk(self)
            self.S.copy_(S_old)
            if t < self.Tsch:
                s0 = torch.gather(self.S[..., 0], 1, self.read_idx)
                self.trace[t] = s0
        return [(E.World, "_tick", _tick)]


class RandomizeSource(Operator):
    """Packet provenance randomised: each tick the (emit, channel, payload) of every site is moved to a random
    other site before transport (a pair-shared permutation keyed on the world seed and tick), so content
    leaves from the wrong place."""

    def patches(self):
        em = E.World._emit

        def _emit(self, want, chan, pay):
            h = rng.site_base(self.ws, 0x5EC, self.t_dev, self.sites)      # pair-shared (ws equal in a pair)
            perm = torch.argsort(h, dim=1)
            want = torch.gather(want, 1, perm)
            chan = torch.gather(chan, 1, perm)
            pay = torch.gather(pay, 1, perm[..., None].expand_as(pay))
            return em(self, want, chan, pay)
        return [(E.World, "_emit", _emit)]


def transpose_table(nbr: np.ndarray, dist: np.ndarray):
    """In-neighbour table with the out-table's width R: port j of n lists the j-th site that sends to n
    (cycled when n has fewer than R in-edges; n keeps its out-row when it has none)."""
    N, R = nbr.shape
    ins = [[] for _ in range(N)]
    dins = [[] for _ in range(N)]
    for m in range(N):
        for j in range(R):
            ins[int(nbr[m, j])].append(m)
            dins[int(nbr[m, j])].append(int(dist[m, j]))
    out = nbr.copy()
    dout = dist.copy()
    for n in range(N):
        if ins[n]:
            for j in range(R):
                out[n, j] = ins[n][j % len(ins[n])]
                dout[n, j] = dins[n][j % len(ins[n])]
    return out, dout


class ReverseEdges(Operator):
    """Every edge reversed in the engine only (envs placement and assays distances keep the forward graph)."""

    def patches(self):
        init = E.World.__init__

        def __init__(self, *a, **k):
            init(self, *a, **k)
            if self.nbr is not None:
                n2, d2 = transpose_table(self.nbr.cpu().numpy(), self.dist.cpu().numpy())
                self.nbr = torch.as_tensor(n2, device=self.dev)
                self.dist = torch.as_tensor(d2, device=self.dev)
        return [(E.World, "__init__", __init__)]


class AlterTiming(Operator):
    """The engine runs lat_base + 1 and lat_jitter + 1 while every record keeps the declared physics."""

    def patches(self):
        init = E.World.__init__

        def __init__(self, ph, *a, **k):
            init(self, ph.replace(lat_base=ph.lat_base + 1, lat_jitter=ph.lat_jitter + 1), *a, **k)
        return [(E.World, "__init__", __init__)]


class SilentSensors(Operator):
    """Every SENSE value is zero (the schedule is installed, its values are silenced)."""

    def patches(self):
        ss = E.World.set_schedule

        def set_schedule(self, sch):
            ss(self, sch)
            self.sch_val = torch.zeros_like(self.sch_val)
        return [(E.World, "set_schedule", set_schedule)]


# ------------------------------------------------------------------ the catalogue
RUN = ("held", "controls", "plant", "lens_swap", "report", "oracle")


def catalogue() -> dict:
    ops = [
        SwapConditionLabels(
            "swap_labels", "protocol",
            "normal<->zero_comm exchanged: for a comm specimen the reported treatment accuracy must fall to the "
            "control's (chance) and comm_delta must be <= 0 (COMM_DEPENDENT False); a local specimen is "
            "invariant. lens_swap: site<->channel exchanged, so a SITE class must become CHANNEL (and back).",
            ("held", "controls", "plant", "lens_swap", "report")),
        DuplicateCondition(
            "duplicate_condition", "protocol",
            "control == treatment: every control delta must be exactly 0, so COMM_DEPENDENT must be False and "
            "no ablation can support causality; a no-op control must be flagged (NOT_APPLICABLE). lens_swap: "
            "chan arm == site arm breaks the mirror identity, so the census must be IDENTITY-BROKEN/UNDEFINED.",
            ("held", "controls", "plant", "lens_swap", "report")),
        DisableChannel(
            "disable_channel", "engine",
            "no packet ever arrives: a comm specimen must lose SIGNAL (acc -> chance on comm families) and "
            "COMM_DEPENDENT must be False; the plant must be non-viable for comm families; a local specimen "
            "is invariant.",
            RUN),
        ControlIgnored(
            "control_ignored", "engine",
            "the engine ignores every control switch, so each control equals normal: the no-op guard must "
            "return NOT_APPLICABLE for every control and CAUSAL_SUPPORT must be impossible; held "
            "COMM_DEPENDENT must be False.",
            ("held", "controls", "plant", "report", "oracle")),
        FreezeState(
            "freeze_state", "engine",
            "S frozen after T/2: accuracy on trials after T/2 must fall to chance, so pooled accuracy must "
            "drop by about half of (acc - .5); a correct verdict must not certify the post-freeze trials.",
            RUN),
        RandomizeSource(
            "randomize_source", "engine",
            "packets leave from random sites: a comm specimen that needs the sensor's location must fall to "
            "chance (SIGNAL False); a local specimen is invariant.",
            RUN),
        ReverseEdges(
            "reverse_edges", "engine",
            "every edge reversed: on a symmetric table (ring/torus/global) the physics is invariant up to port "
            "order (equivalent); on a directed graph a transport specimen's accuracy must change.",
            RUN),
        AlterTiming(
            "alter_timing", "engine",
            "lat_base+1 and lat_jitter+1 executed but not recorded: a timing-tuned specimen (echo, delay == "
            "delta) must lose accuracy; a timing-robust one may keep it; in every case the executed physics "
            "differs from the recorded one, which a correct pipeline must detect (provenance).",
            RUN),
        SeverSearchRuler(
            "sever_search_ruler", "protocol",
            "the held ruler measures a random genome: the held labels must describe the RECORDED champion, so "
            "a correct pipeline must either reproduce the champion's held accuracy or alarm (genome provenance).",
            ("held", "report")),
        ReuseSelectionSeeds(
            "reuse_selection_seeds", "protocol",
            "the held set equals the selection set: a correct pipeline must refuse (held AND selection = EMPTY is the "
            "Ares rule); for a selected champion the held accuracy is in-sample and inflated.",
            ("held", "report"), sp_override={"M_final": 64}),
        DropMirror(
            "drop_mirror", "protocol",
            "mirror partners identical (no negation): pair-level exactness of constant policies is lost and the "
            "swap identity becomes a no-op; a correct pipeline must flag the design invariant "
            "(y[2p+1] == -y[2p]); the swap census must be UNDEFINED/IDENTITY-BROKEN.",
            ("held", "controls", "plant", "lens_swap", "report")),
        PermuteSeedsBetweenArms(
            "permute_seeds", "protocol",
            "control arms on other worlds than the treatment: paired statistics lose their pairing; verdicts "
            "that rest on a degenerate (world-independent) control are invariant, others change in variance; "
            "the census eligibility (normal-correct) is no longer about the swapped worlds.",
            ("held", "controls", "plant", "lens_swap", "report")),
        SilentSensors(
            "silent_sensors", "engine",
            "no cue ever arrives: every family must be at chance (exactly .5 under the mirror), SIGNAL False, "
            "plant non-viable.",
            RUN),
        InvertActuatorSign(
            "invert_sign", "protocol",
            "readout sign inverted: accuracy must become 1 - acc; a competent specimen must read ANTI-CORRELATED "
            "(acc < .45 is an anomaly flag), never SIGNAL.",
            ("held", "controls", "plant", "lens_swap", "report")),
    ]
    return {o.name: o for o in ops}


def get(name: str) -> Operator:
    return catalogue()[name]
