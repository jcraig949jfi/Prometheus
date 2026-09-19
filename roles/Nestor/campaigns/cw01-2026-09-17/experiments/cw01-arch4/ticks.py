"""Episode constructions for the temporal-semantics probes (T-X12): ticks are inserted, appended
or repeated by construction on a copy of a frozen episode; the world generator is not touched.
Computational scope: integer programs on a bounded VM."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arch4rt as A            # noqa: E402
from archaeon.wse.worlds import Episode, K_ASK, K_NOISE, K_PUT   # noqa: E402


def clone(ep):
    return Episode(ticks=[list(t) for t in ep.ticks], expected=dict(ep.expected), intervention_tick=ep.intervention_tick, meta=dict(ep.meta))


def insert(ep, pos, new_ticks):
    """Insert `new_ticks` before tick index `pos`; ask indices at or after pos shift."""
    e = clone(ep)
    k = len(new_ticks)
    e.ticks = e.ticks[:pos] + [list(t) for t in new_ticks] + e.ticks[pos:]
    e.expected = {(i + k if i >= pos else i): v for i, v in ep.expected.items()}
    if e.intervention_tick >= pos:
        e.intervention_tick += k
    return e


def ask_ticks(ep):
    return sorted(i for i, w in enumerate(ep.ticks) if w and w[0] == K_ASK)


def put_ticks(ep):
    return [i for i, w in enumerate(ep.ticks) if w and w[0] == K_PUT]


def noise_tick(rng):
    return [K_NOISE, rng.next_u32(), rng.next_u32()]


def noise_bank(ei, n=4, label="nestor.ticks"):
    rng = A.SplitMix64(A.seed_from(label, A.LOOP_SEED, ei))
    return [noise_tick(rng) for _ in range(n)]


def w0_variants(eps):
    """One-stream (W0) constructions. Returns {name: [episodes]} with identical content otherwise."""
    names = ["base", "empty1", "noise1", "noise2", "noise3", "noise4", "putrep", "noise_inline", "noise_pre", "empty_pre", "ne", "en"]
    out = {n: [] for n in names}
    for ei, ep in enumerate(eps):
        nz = noise_bank(ei)
        fa = ask_ticks(ep)[0]
        lp = put_ticks(ep)[-1]
        out["base"].append(clone(ep))
        out["empty1"].append(insert(ep, fa, [[]]))
        for n in (1, 2, 3, 4):
            out["noise%d" % n].append(insert(ep, fa, nz[:n]))
        out["putrep"].append(insert(ep, fa, [list(ep.ticks[lp])]))
        e = clone(ep)
        e.ticks[lp] = e.ticks[lp] + list(nz[0])
        out["noise_inline"].append(e)
        out["noise_pre"].append(insert(ep, 0, [nz[0]]))
        out["empty_pre"].append(insert(ep, 0, [[]]))
        out["ne"].append(insert(ep, fa, [nz[0], []]))
        out["en"].append(insert(ep, fa, [[], nz[0]]))
    return out


def k2_variants(eps):
    """Two-stream (W2_K2) constructions: per-tag timing live by construction.
    tag1 = the tag of the FIRST PUT; tag2 = the second. Returns {name: [episodes]} plus per-episode
    tag order of the asks."""
    names = ["base", "between_puts", "between_puts_x2", "before_first_ask", "before_second_ask"]
    out = {n: [] for n in names}
    meta = []
    for ei, ep in enumerate(eps):
        nz = noise_bank(ei, label="nestor.ticks.k2")
        puts = put_ticks(ep)
        asks = ask_ticks(ep)
        tag1, tag2 = ep.ticks[puts[0]][1], ep.ticks[puts[1]][1]
        out["base"].append(clone(ep))
        out["between_puts"].append(insert(ep, puts[1], [nz[0]]))
        out["between_puts_x2"].append(insert(ep, puts[1], nz[:2]))
        out["before_first_ask"].append(insert(ep, asks[0], [nz[0]]))
        out["before_second_ask"].append(insert(ep, asks[1], [nz[0]]))
        meta.append({"tag1": tag1, "tag2": tag2, "ask_order": [ep.ticks[a][1] for a in asks]})
    return out, meta
