"""Adversarial audit of the AETH-03 propagation assay (research block, Block A).

The assay (`aeth03_propagation.py`) claims that, because every law is
local and the injected hash stream is shared by both twins, every newly
differing site has a differing neighbour, so

    generation = 1 + min(generation of differing neighbours last tick)

is "the exact shortest causal chain from the origin". This module tries to
break that claim three ways. Each part can fail.

  lightcone   For every law, flip ONE random bit of ONE random site in a
              random world (soup and warmed), and for `rcv` also the hidden
              received flag; step both copies once; measure the largest
              Manhattan distance at which ANY state (five bytes + flag)
              differs. The premise fails if any law exceeds its declared
              radius (1; `mov` 2).

  hidden      `rcv` only. Build twins whose five visible bytes are
              identical everywhere and whose received flags differ at one
              site. Show (a) the hidden difference does produce visible
              differences, and (b) a BYTES-ONLY difference predicate --
              what the assay would be without the flag -- produces orphan
              "violations", while the assay's full predicate produces none.
              If (b) shows no violations the flag never mattered and the
              fixture proves nothing.

  parents     The load-bearing attack. A differing neighbour need not be a
              CAUSE: its difference may be in a byte that never reaches the
              new site. For every newly differing site x at t+1 and every
              differing neighbour y at t, build world A_t with ONLY y's state
              replaced by B's, step it, and ask whether x then differs from
              A_{t+1}. y is a SUFFICIENT parent if it alone produces x's
              difference. The causal generation is

                  g_c(x) = 1 + min g_c(y) over sufficient parents y

              and an event with differing neighbours but no single
              sufficient parent is a JOINT event (needs two or more
              differences at once), assigned 1 + min over all its
              differing neighbours and counted separately. Compared with the
              assay's adjacency generation g_a: g_a <= g_c always (the
              assay takes the min over a superset), so the assay's
              generations are LOWER BOUNDS; this measures by how much.
"""

import argparse
import json
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
for _p in (_AETHER, os.path.join(_AETHER, "test", "reference")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from observatory import aeth03_propagation as P          # noqa: E402
from observatory import aeth03_scouts as S               # noqa: E402
from observatory import aeth03_variants as V             # noqa: E402

LAWS = ("v1", "add", "hys", "chg", "cnd", "str", "mov", "rcv", "m4",
        "fwd", "rcv_add", "rcv_cnd", "rcv_str")


def declared_radius(law):
    return P.RADIUS.get(law, 1)


def site_state_diff(a, b):
    site, _ = P.diff_masks(a, b)
    return site


# --------------------------------------------------------------- lightcone

def lightcone(law, n, trials, rng, warm_ticks=200, worlds=8):
    """`worlds` base worlds (half raw soup, half warmed), `trials` flips
    spread across them; each flip is one copy pair stepped once."""
    par = S.params(S.SEED0, S.MUT_ON)
    worst = 0
    hist = {}
    bases = []
    for k in range(worlds):
        w = P.World(law, S.initial(law, n, int(rng.integers(1 << 30))))
        if k % 2:
            for t in range(1, warm_ticks + 1):
                w.step(t, par)
        if law in V.RCV_FAMILY and not (k % 2):
            w.received = rng.random((n, n)) < 0.3
        if law == "fwd" and not (k % 2):
            w.extra["received_value"] = rng.integers(0, 256, size=(n, n),
                                                     dtype=np.uint8)
        bases.append(w)
    for trial in range(trials):
        w = bases[trial % worlds]
        a, b = w.copy(), w.copy()
        r0, c0 = int(rng.integers(n)), int(rng.integers(n))
        ncomp = 5 + (1 if law in V.RCV_FAMILY else 0) + (1 if law == "fwd" else 0)
        comp = int(rng.integers(ncomp))
        if comp == 5:
            b.received[r0, c0] = ~b.received[r0, c0]
        elif comp == 6:
            b.extra["received_value"][r0, c0] ^= np.uint8(1 << int(rng.integers(8)))
        else:
            b.f[comp][r0, c0] ^= np.uint8(1 << int(rng.integers(8)))
        tick = warm_ticks + 1
        a.step(tick, par)
        b.step(tick, par)
        d = site_state_diff(a, b)
        if d.any():
            dist = P.manhattan_from(n, r0, c0)
            r = int(dist[d].max())
        else:
            r = -1
        hist[r] = hist.get(r, 0) + 1
        worst = max(worst, r)
    return {"law": law, "trials": trials, "declared_radius": declared_radius(law),
            "max_radius_observed": worst,
            "radius_histogram": {str(k): v for k, v in sorted(hist.items())},
            "premise_holds": worst <= declared_radius(law)}


# ------------------------------------------------------------------ hidden

def hidden_flag(n, ticks, rng, trials):
    """rcv twins identical in bytes, differing only in one received flag."""
    par = S.params(S.SEED0, 0)
    par_on = S.params(S.SEED0, S.MUT_ON)
    out = {"trials": trials, "visible_later": 0,
           "violations_full_predicate": 0, "violations_bytes_only": 0}
    for trial in range(trials):
        w = P.World("rcv", S.initial("rcv", n, int(rng.integers(1 << 30))))
        for t in range(1, 301):
            w.step(t, par_on)
        a, b = w.copy(), w.copy()
        # choose a site whose flip matters: an inert site with energy that
        # was NOT written (flag False) -> set True in B only
        cand = np.argwhere((~w.received) & (w.f[0] != 1)
                           & (w.f[4].astype(np.int64) >= par["write_cost"]))
        r0, c0 = (int(x) for x in cand[int(rng.integers(len(cand)))])
        b.received[r0, c0] = True
        assert all(np.array_equal(x, y) for x, y in zip(a.f, b.f))
        full_prev, _ = P.diff_masks(a, b)
        bytes_prev = np.zeros((n, n), dtype=bool)
        seen_visible = False
        for t in range(1, ticks + 1):
            a.step(300 + t, par)
            b.step(300 + t, par)
            full, per_field = P.diff_masks(a, b)
            vis = per_field[0] | per_field[1] | per_field[2] | per_field[3] | per_field[4]
            seen_visible = seen_visible or bool(vis.any())
            for pred_prev, pred_now, key in ((full_prev, full, "violations_full_predicate"),
                                             (bytes_prev, vis, "violations_bytes_only")):
                newly = pred_now & ~pred_prev
                nb = P.neighbour_count(pred_prev) > 0
                out[key] += int((newly & ~nb).sum())
            full_prev, bytes_prev = full, vis
        out["visible_later"] += int(seen_visible)
    return out


# ----------------------------------------------------------------- parents

def patched_step(a_state, b_state, sites, tick, par):
    """A_t with the listed sites' full state taken from B_t, stepped once."""
    w = a_state.copy()
    for (r, c) in sites:
        for i in range(5):
            w.f[i][r, c] = b_state.f[i][r, c]
        for key in w.extra:
            w.extra[key][r, c] = b_state.extra[key][r, c]
    w.step(tick, par)
    return w


def site_differs(w1, w2, r, c):
    if any(w1.f[i][r, c] != w2.f[i][r, c] for i in range(5)):
        return True
    return any(bool(w1.extra[k][r, c] != w2.extra[k][r, c]) for k in w1.extra)


def parent_audit(law, n, warmup, ticks, origins, seed_index, mut):
    seed, rng_seed = S.SEED0 + seed_index, S.RNG0 + seed_index
    rng = np.random.default_rng(0xB0A7 + seed_index)        # assay's origins
    par_on = S.params(seed, S.MUT_ON)
    par = S.params(seed, mut)
    w = P.World(law, S.initial(law, n, rng_seed))
    for t in range(1, warmup + 1):
        w.step(t, par_on)
    em = S.emitters(law, w.f, par_on["write_cost"])
    if law in V.RCV_FAMILY:
        em = em | (w.received & (w.f[4].astype(np.int64) >= par_on["write_cost"]))
    cand = np.argwhere(em)
    pick = cand[rng.choice(len(cand), min(origins, len(cand)), replace=False)]
    specs = [(tuple(int(x) for x in p), int(rng.integers(5)), int(rng.integers(8)))
             for p in pick]
    nb = P.stencil(law)
    totals = {"events": 0, "sufficient_single": 0, "joint": 0,
              "min_adjacent_parent_not_sufficient": 0,
              "g_equal": 0, "g_causal_greater": 0, "g_diff_sum": 0,
              "gen1_by_assay": 0, "gen1_by_causal": 0,
              "patched_steps": 0}
    per_origin = []
    for origin, field, bit in specs:
        a, b = w.copy(), w.copy()
        b.f[field][origin] ^= np.uint8(1 << bit)
        site = site_state_diff(a, b)
        g_a = {tuple(x): 0 for x in np.argwhere(site)}
        g_c = dict(g_a)
        max_ga = max_gc = 0
        for t in range(1, ticks + 1):
            prev_site = site
            a_prev, b_prev = a.copy(), b.copy()
            tick = warmup + t
            a.step(tick, par)
            b.step(tick, par)
            site = site_state_diff(a, b)
            newly = np.argwhere(site & ~prev_site)
            keep_a = {k: v for k, v in g_a.items() if site[k]}
            keep_c = {k: v for k, v in g_c.items() if site[k]}
            for (r, c) in newly:
                r, c = int(r), int(c)
                parents = [((r + dr) % n, (c + dc) % n) for dr, dc in nb
                           if prev_site[(r + dr) % n, (c + dc) % n]]
                if not parents:
                    continue            # a locality violation; counted by the assay
                totals["events"] += 1
                ga = 1 + min(g_a[p] for p in parents)
                suff = []
                for p in parents:
                    wp = patched_step(a_prev, b_prev, [p], tick, par)
                    totals["patched_steps"] += 1
                    if site_differs(wp, a, r, c):
                        suff.append(p)
                if suff:
                    totals["sufficient_single"] += 1
                    gc = 1 + min(g_c[p] for p in suff)
                else:
                    totals["joint"] += 1
                    gc = 1 + min(g_c[p] for p in parents)
                amin = min(parents, key=lambda p: g_a[p])
                if amin not in suff:
                    totals["min_adjacent_parent_not_sufficient"] += 1
                totals["g_equal"] += int(gc == ga)
                totals["g_causal_greater"] += int(gc > ga)
                totals["g_diff_sum"] += gc - ga
                totals["gen1_by_assay"] += int(ga == 1)
                totals["gen1_by_causal"] += int(gc == 1)
                keep_a[(r, c)] = ga
                keep_c[(r, c)] = gc
                max_ga, max_gc = max(max_ga, ga), max(max_gc, gc)
            g_a, g_c = keep_a, keep_c
        per_origin.append({"origin": list(origin), "max_gen_assay": max_ga,
                           "max_gen_causal": max_gc})
    return {"law": law, "n": n, "warmup": warmup, "ticks": ticks,
            "origins": len(specs), "seed_index": seed_index,
            "perturbation": "on" if mut else "off", "totals": totals,
            "per_origin": per_origin}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("part", choices=("lightcone", "hidden", "parents"))
    ap.add_argument("--law", default="rcv")
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--trials", type=int, default=400)
    ap.add_argument("--ticks", type=int, default=400)
    ap.add_argument("--warmup", type=int, default=1500)
    ap.add_argument("--origins", type=int, default=32)
    ap.add_argument("--seed-index", type=int, default=0)
    ap.add_argument("--perturbation", choices=("off", "on"), default="off")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rng = np.random.default_rng(0xA0D17 + a.seed_index)
    t0 = time.time()
    if a.part == "lightcone":
        res = {"laws": [lightcone(l, a.n, a.trials, rng) for l in LAWS]}
    elif a.part == "hidden":
        res = hidden_flag(a.n, a.ticks, rng, a.trials)
    else:
        res = parent_audit(a.law, a.n, a.warmup, a.ticks, a.origins, a.seed_index,
                           S.MUT_ON if a.perturbation == "on" else 0)
    res["wall_seconds"] = time.time() - t0
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(res if a.part != "parents" else res["totals"], indent=1)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
