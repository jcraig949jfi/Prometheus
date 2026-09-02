"""
Relational executable history (D7 sections 9, 10, 11, 29) and the matched
same-hoard / shuffled conditions (sections 8, 16, 17, 40).

History is machine-native only: coords changed, local reachability expansion,
resource cost, and PAIRWISE emergent effects (what a pair does that neither
member does alone).  No task labels, no "opens barrier", no target coordinates.

Developmental worlds differ from the proof world (different p / base) and the
history is pure artifact probing -- it never optimizes toward a proof endpoint,
so endpoint exclusion holds by construction (audited in leakage.py).

Conditions on IDENTICAL hoard bytes:
  H2  intact marginals + intact pairwise interaction graph
  H0  marginals only (relational edges removed)      -> "bag of artifacts"
  H1  marginals intact, pairwise graph SHUFFLED        -> same info mass, wrong wiring
"""

from __future__ import annotations
import random
from substrate import run_micro
from worlds import proof_world, prim_lib
from substrate import World, run_z

R, U, S = 0, 1, 2


def developmental_worlds():
    """Several dev worlds; different modulus and/or base -> not the proof world."""
    w7 = proof_world(7)
    w11 = proof_world(11)
    lib = prim_lib(11)
    # a base-variant dev world (fewer base ops) to vary r-control exposure
    w11b = World(name="W-DEV-varbase(p=11)", p=11, nreg=3,
                 base_ops=tuple((nm, lib[nm]) for nm in ("inc_r", "dbl_r", "neg_r")),
                 note="dev variant base")
    return [w7, w11, w11b]


def _probe_states(world, rng, n_extra=6):
    """Base-reachable-ish region: gate coord u=0 (so gated writers stay inert solo).
    nreg-aware: coord0=r varies, coord1=u pinned 0, other coords 0 or light noise."""
    p, n = world.p, world.nreg
    def mk(r, tail):
        return tuple([r, 0] + list(tail))
    probes = [mk(r, [0] * (n - 2)) for r in range(p)]
    for _ in range(n_extra):
        tail = [rng.randrange(p) if i == 2 else 0 for i in range(2, n)]  # only coord2 noisy
        probes.append(mk(rng.randrange(p), tail))
    return probes


def _coords_changed(prog_runner, probes, world):
    changed = set()
    cost = 0
    for v in probes:
        nv, c = prog_runner(v)
        cost += c
        for i, (a, b) in enumerate(zip(v, nv)):
            if a != b:
                changed.add(i)
    return changed, cost


def generate_history(hoard, dev_worlds=None, seed=13, meter=None):
    """
    Returns store = {'marginal': {aid:{coords,frozen,cost}},
                     'pair': {(a,b):{emergent,changed,cost}},
                     'dev_fingerprints': [...]}.
    Frozen coords = coords a base op cannot write (>0 here).  This is machine-native.
    """
    rng = random.Random(seed)
    dev_worlds = dev_worlds or developmental_worlds()
    ids = sorted(hoard.keys())
    marg = {a: {"coords": set(), "frozen": False, "cost": 0} for a in ids}
    pair = {}

    for w in dev_worlds:
        probes = _probe_states(w, rng)
        base_writable = set()
        for v in probes:
            for _, prog in w.base_ops:
                nv, _ = run_micro(prog, v, w.p)
                for i, (a, b) in enumerate(zip(v, nv)):
                    if a != b:
                        base_writable.add(i)

        def runner_for(art):
            return lambda v: art.run(v, w.p)

        solo_changed = {}
        for a in ids:
            ch, cost = _coords_changed(runner_for(hoard[a]), probes, w)
            solo_changed[a] = ch
            marg[a]["coords"] |= ch
            marg[a]["cost"] += cost
            if ch - base_writable:
                marg[a]["frozen"] = True
            if meter:
                meter.tick("history_construction", len(probes))

        # pairwise ordered interactions
        for a in ids:
            for b in ids:
                def prun(v, a=a, b=b):
                    nv, c1 = run_z(("seq", ("quote", a), ("quote", b)), v, w, hoard)
                    return nv, c1
                ch, cost = _coords_changed(prun, probes, w)
                emergent = ch - solo_changed[a] - solo_changed[b]
                key = (a, b)
                rec = pair.setdefault(key, {"emergent": set(), "changed": set(), "cost": 0})
                rec["emergent"] |= emergent
                rec["changed"] |= ch
                rec["cost"] += cost
                if meter:
                    meter.tick("history_construction", len(probes))

    # normalize sets -> sorted lists for hashing/serialization
    store = {
        "marginal": {a: {"coords": sorted(marg[a]["coords"]),
                         "frozen": marg[a]["frozen"],
                         "cost": marg[a]["cost"]} for a in ids},
        "pair": {f"{a}|{b}": {"emergent": sorted(v["emergent"]),
                              "changed": sorted(v["changed"]),
                              "cost": v["cost"]}
                 for (a, b), v in pair.items()},
        "dev_fingerprints": [w.fingerprint() for w in dev_worlds],
        "ids": ids,
    }
    return store


# --------------------------------------------------------------------------
# Matched conditions (identical hoard; only relational organization differs).
# --------------------------------------------------------------------------

def condition(store, which, seed=99):
    ids = store["ids"]
    if which == "H2":
        return store
    if which == "H0":
        s = dict(store)
        s = {**store, "pair": {}, "_cond": "H0"}
        return s
    if which == "H1":
        # shuffle which pair-key holds which pair-value (preserve value multiset,
        # marginals, and pair count -> same information mass, wrong wiring)
        rng = random.Random(seed)
        keys = list(store["pair"].keys())
        vals = list(store["pair"].values())
        perm = keys[:]
        rng.shuffle(perm)
        shuffled = {perm[i]: vals[i] for i in range(len(keys))}
        return {**store, "pair": shuffled, "_cond": "H1"}
    raise ValueError(which)


# --------------------------------------------------------------------------
# Z1 proposal prior derived from the (conditioned) relational store + the task.
# The learner is allowed to read the task's own S and T (that is the problem
# statement); it is NOT given any barrier descriptor or per-artifact label.
# Only art_w differs between arms; node_w is held equal (conservative).
# --------------------------------------------------------------------------

def derive_prior(store, S, T, W_MARG=4.0, W_PAIR=7.0):
    """
    Return art_w{aid:weight}.  MODERATE additive tilt (not exponential): a relevant
    artifact is upweighted a single-digit multiple over baseline so the proposal is
    tilted, not collapsed -- preserving evolutionary diversity.
      baseline           = 1.0
      +marginal hits D   = +W_MARG
      +in a D-emergent pair = +W_PAIR
    """
    ids = store["ids"]
    D = {i for i in range(len(S)) if S[i] != T[i]}  # coords the TASK must change
    marg = store["marginal"]
    pair = store["pair"]

    pair_hit = {a: 0.0 for a in ids}
    for key, rec in pair.items():
        a, b = key.split("|")
        if set(rec["emergent"]) & D:
            pair_hit[a] = 1.0
            pair_hit[b] = 1.0

    art_w = {}
    for a in ids:
        w = 1.0
        if set(marg[a]["coords"]) & D:
            w += W_MARG
        w += W_PAIR * pair_hit.get(a, 0.0)
        art_w[a] = w
    return art_w, sorted(D)
