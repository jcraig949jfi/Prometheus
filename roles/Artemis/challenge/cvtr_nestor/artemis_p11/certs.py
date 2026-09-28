"""Candidate certificates of PREREG_P11.md s3: CVT-1 / CVT-2 / CVT-R, LOCAL; diagnostics SHUF, DOM."""
from __future__ import annotations

import math
import random
from collections import Counter

from common import shabytes, fid

DRAWS = 3
GENS = 4


def variant_values(G, i, exhaustive, sid):
    x = G[i]
    if exhaustive:
        return [v for v in range(256) if v != x]
    a, b = x ^ 0x01, x ^ 0x80
    j = 0
    while True:
        r = shabytes("VAR", sid, i, j, n=1)[0]
        if r not in (x, a, b):
            return [a, b, r]
        j += 1


def _delta(a, b):
    return tuple((i, a[i]) for i in range(len(a)) if a[i] != b[i])


def _defined(sigs):
    """Same non-empty signature in >= 2 of 3 draws."""
    c = Counter(s for s in sigs if s)
    if not c:
        return None
    s, m = c.most_common(1)[0]
    return s if m >= 2 else None


def cvt(stepfn, G0, sid, exhaustive):
    """stepfn(G, g, k) -> descendant. Returns per-variant defined signatures for g = 1..4 and the baseline lineage."""
    cache = {}

    def st(G, g, k):
        key = (G, g, k)
        r = cache.get(key)
        if r is None:
            r = cache[key] = stepfn(G, g, k)
        return r

    def lineage(G, k):
        out = []
        for g in range(1, GENS + 1):
            G = st(G, g, k)
            out.append(G)
        return out

    base = [lineage(G0, k) for k in range(DRAWS)]
    rows = []
    for i in range(len(G0)):
        for x in variant_values(G0, i, exhaustive, sid):
            Gv = G0[:i] + bytes([x]) + G0[i + 1:]
            lin = [lineage(Gv, k) for k in range(DRAWS)]
            d = [_defined([_delta(lin[k][g], base[k][g]) for k in range(DRAWS)]) for g in range(GENS)]
            rows.append((i, x, d))
    return rows, base


def score(rows, n_sites):
    nv = len(rows)
    c1 = [r for r in rows if r[2][0]]
    c2 = [r for r in c1 if r[2][1]]
    cr = [r for r in c2 if (r[2][2] is not None and r[2][2] == r[2][1]) or (r[2][3] is not None and r[2][3] == r[2][1])]
    k1 = len({r[2][0] for r in c1})
    k2 = len({r[2][1] for r in c2})
    kr = len({r[2][1] for r in cr})
    local_sites = {r[0] for r in c1 if len(r[2][0]) == 1}
    return {
        "n_variants": nv,
        "CVT1": {"accept": len(c1) >= 1, "n": len(c1), "classes": k1, "TB": round(math.log2(1 + k1), 4),
                 "h": round(len(c1) / nv, 4) if nv else 0.0},
        "CVT2": {"accept": len(c2) >= 1, "n": len(c2), "classes": k2, "TB": round(math.log2(1 + k2), 4),
                 "h": round(len(c2) / nv, 4) if nv else 0.0},
        "CVTR": {"accept": len(cr) >= 1, "n": len(cr), "classes": kr, "TB": round(math.log2(1 + kr), 4),
                 "h": round(len(cr) / nv, 4) if nv else 0.0},
        "LOCAL": {"accept": len(local_sites) >= 0.25 * n_sites, "sites": len(local_sites), "n_sites": n_sites},
    }


def dom_share(G):
    b, c = Counter(G).most_common(1)[0]
    return c / len(G), b


def entropy(G):
    c = Counter(G)
    return -sum(v / len(G) * math.log2(v / len(G)) for v in c.values())


def shuf(G, fid_obs, sid):
    rng = random.Random(str(("SHUF", sid)))
    tot = 0.0
    for _ in range(200):
        s = list(G)
        rng.shuffle(s)
        tot += fid(G, bytes(s))
    base = tot / 200
    return {"accept": (fid_obs - base) >= 0.10, "fid": round(fid_obs, 4), "shuffle_base": round(base, 4),
            "excess": round(fid_obs - base, 4)}


def dom(G):
    d, b = dom_share(G)
    return {"accept": d < 0.80, "dominant_share": round(d, 4), "dominant_byte": "%02x" % b,
            "entropy_bits_per_byte": round(entropy(G), 4)}
