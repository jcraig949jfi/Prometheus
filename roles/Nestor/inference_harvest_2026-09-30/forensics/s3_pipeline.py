"""s3 per-genome pipeline: single-knockout function profile, dispensable set, pair sample, pair calls, null.

Used by s3_controls.py and s3_pairs.py so controls and panel go through the identical code path.
"""
import hashlib
import itertools
import random

import s3_common as S


def singles(cell, g, dense, sf, positions, known_comp=None):
    """3 single-knockout draws (core_map values) per position; returns {p: [kept bool]*3}.
    known_comp: optional {p: (lost, tried)} existing competence data, used as a determinism check."""
    out, chk = {}, []
    for p in positions:
        ks = []
        for v in S.single_vals(g, p):
            m = bytearray(g); m[p] = v
            ks.append(S.function(cell, bytes(m), dense, sf))
        out[p] = ks
    return out


def comp_draws(cell, g, dense, p):
    res = []
    for v in S.single_vals(g, p):
        m = bytearray(g); m[p] = v
        res.append(S.competent(cell, bytes(m), dense))
    return res


def sample_pairs(g, disp, npairs):
    allp = list(itertools.combinations(sorted(disp), 2))
    if len(allp) <= npairs:
        return allp
    rng = random.Random(int(hashlib.sha256(b"S3SAMPLE" + bytes(g)).hexdigest()[:16], 16))
    return sorted(rng.sample(allp, npairs))


def pair_call(cell, g, dense, sf, i, j):
    muts = S.pair_mutants(g, i, j)
    lethal = S.lethal_call(lambda m: S.function(cell, m, dense, sf), muts)
    confirmed = None
    if lethal:
        confirmed = S.lethal_call(lambda m: S.function(cell, m, dense, sf, suffix="/S3R"), muts)
    return lethal, confirmed
