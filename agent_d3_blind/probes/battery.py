"""Frozen probe batteries.

VALUE_PROBES fix all semantic equivalence in this experiment; every equivalence
claim is therefore probe-relative and is labelled as such.  EXT_PROBES exist
only for the preregistered probe-stability check.
"""
import hashlib
import random

VALUE_PROBES = [
    (),
    (0,),
    (5,),
    (1, 2, 3),
    (3, 2, 1),
    (7, 7, 7, 7),
    (1, -1, 1, -1, 1, -1),
    (2, 4, 6, 8, 10),
    (-3, 9, 0, 4),
    (1, 2, 2, 3, 3, 3),
    (10, 20, 30, 40, 50, 60, 70, 80),
    (0, 1, 0, 2, 0, 3, 0),
]
EXT_PROBES = [
    (12,),
    (-5, -4, -3),
    (9, 9, 1, 1, 9, 9, 1, 1, 2),
    (4, 0, 4, 0, 4, 0, 4, 0, 4, 0, 4, 0),
]
LIVENESS_PROBES = VALUE_PROBES[:4]
ARTIFACT_PROBE_RNG = 913
N_ARTIFACT_PROBES = 4


def probe_hash(probes):
    return hashlib.sha1(repr(probes).encode()).hexdigest()[:16]


def make_artifact_probes(sub, common):
    """Reference executable artifacts, used as *inputs* so that an artifact is
    exercised as a transformer of executable artifacts."""
    rng = random.Random(ARTIFACT_PROBE_RNG)
    out = []
    tries = 0
    while len(out) < N_ARTIFACT_PROBES and tries < 4000:
        tries += 1
        p = sub.random_program(rng, rng.randrange(4, 14))
        if not sub.is_valid(p):
            continue
        pr = common.sem_profile(sub, p, VALUE_PROBES)
        if pr["live"] and p not in out:
            out.append(p)
    return out, tries
