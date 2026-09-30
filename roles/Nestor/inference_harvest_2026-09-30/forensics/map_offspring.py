"""Task 1: single-interaction offspring law per donor and register context, and the GW survival P_est.

    python -B map_offspring.py   -> map_offspring.json

Panels: A = C-ZERO-SPECIFIC (c_zero_specific/DONORS.json), B = X-P2-BRIDGE / X-P2-REGSTATE (x_p2_bridge/DONORS.json),
plus the 7ae3 specimen genome (run_ds.donor_genome()) as a sanity anchor for the earlier 0.49-0.52 probe.
Cells: CF for A and B (the cell of every C-ZERO-SPECIFIC run and of the CF arms of B); C7 additionally for B and 7ae3.
Per (donor, cell, context): N interactions; partner = fresh uniform random 64-byte genome (seeding RANDOM); donor side
drawn 50/50; the world's own _pair_interact (ATOMIC runner + register policy class, dense VM, slice 300, ops mask,
copy-mutation 0.002, P-11 assay, post-interaction mutation). Contexts:
  ZERO / CONST / RANDOM : the run_rs policy class sets both organisms' registers before each interaction (exact);
  CARRY   : donor registers carried from its own previous interaction (chain starts at zero, as the founder does);
            partner registers drawn from a pool of carried states of random genomes (2 prior random-random
            interactions from zero) -- an approximation of the resident population's carried state;
  CARRY_L : (extra) as CARRY but the next focal state is that of a uniformly chosen anc-0 half after the interaction
            (a lineage walk: children carry the VICTIM's post-execution registers, as in the world).
Offspring counts per interaction (0, 1, 2 donor-like halves):
  T      (primary, as specified) donor half counts if not converted (ATOMIC keeps its content); the partner half
         counts if it has identity >= 0.9 to the donor's pre-interaction genome on the donor's TRANSMITTED positions;
  W      the same with whole-genome identity;
  LABEL  the world's anc label (what S5's anc0 share counts);
  CAUSAL donor kept + partner converted with a passing P-11 assay (what causal depth counts).
Transmitted positions of a donor: partner-half positions j where the final victim byte equals donor[j] (and the random
victim byte did not) in >= 50% of the zero-context interactions in which the victim ended >= 0.9 whole identity
(80 draws, sides alternating, p11.interact); if the donor never converts from zero, positions delivered with donor
authorship (p11 prov) in >= 50% of all draws; if none, the whole genome. (A first version used "donor-authored"
positions only; it returned 1-2 positions for donors whose conversions are written by the victim's own context
executing donor code, so it was replaced by "delivered".)
"""
from __future__ import annotations

import json
import random
import time

import map_common as M

N = 500
CTX = ("ZERO", "CONST", "RANDOM", "CARRY", "CARRY_L")
OUT = M.HERE / "map_offspring.json"
t0 = time.process_time()


def transmitted(g, cell="CF"):
    r = M.Harness("CARRY", 1, cell).r
    n, tl = r.L, world_tl(r)
    rng = random.Random("T" + g.hex())
    hits, allw, nconv = [0] * n, [0] * n, 0
    for k in range(80):
        side = k % 2
        v = M.rand_genome(rng, n)
        ga, gb = (g, v) if side == 0 else (v, g)
        tape, prov, lit, wo = M.p11.interact(M.DENSE, n=n, tape_len=tl, ga=ga, gb=gb, st_a=(None, 0, 0),
                                             st_b=(None, 0, 0), budget=r.t["slice"], ops_mask=r._ops_mask(),
                                             cmr=r.copy_mut, rng=random.Random(rng.random()))
        v0 = n if side == 0 else 0
        did = 1 if side == 0 else 2
        fin = bytes(tape[v0:v0 + n])
        conv = M.ident(fin, g) >= 0.9
        nconv += conv
        for j in range(n):
            # delivered: the victim's final byte equals the donor's byte where the random victim byte did not
            a = fin[j] == g[j] and v[j] != g[j]
            allw[j] += a and prov[v0 + j] == did
            if conv:
                hits[j] += a
    if nconv:
        T = [j for j in range(n) if hits[j] >= 0.5 * nconv]
        src = "delivered_in_conversions"
    else:
        T = [j for j in range(n) if allw[j] >= 40]
        src = "donor_authored_delivered_all_draws"
    if not T:
        T, src = list(range(n)), "whole_genome"
    return T, src, nconv


def world_tl(r):
    return M.world._pow2(2 * r.L)


def partner_pool(cell, k=600, seed=7):
    r = M.Harness("CARRY", 2, cell).r
    n, tl = r.L, world_tl(r)
    rng = random.Random(seed)
    pool = []
    for _ in range(k):
        g = M.rand_genome(rng, n)
        st = (None, 0, 0)
        for _j in range(2):
            side = rng.randrange(2)
            o = M.rand_genome(rng, n)
            ga, gb = (g, o) if side == 0 else (o, g)
            ca = [None]

            # re-run the pair to read the carried state of g (p11.interact does not return registers)
            tape = bytearray(tl)
            tape[0:n], tape[n:2 * n] = ga, gb
            for who, start in ((0, 0), (1, n)):
                c = M.DENSE.Ctx(tape, start, n, policy=M.DENSE.ARENA, rng=rng, copy_mut_rate=r.copy_mut, sense=who)
                if who == side:
                    c.regs, c.fz, c.fc = (None if st[0] is None else list(st[0])), st[1], st[2]
                M.DENSE.run(c, start, r.t["slice"], ops_enabled=r._ops_mask())
                if who == side:
                    ca[0] = (None if c.regs is None else list(c.regs), c.fz, c.fc)
            st = ca[0]
        pool.append(st)
    return pool


def law(counts):
    n = len(counts)
    p = [sum(1 for c in counts if c == i) / n for i in range(3)]
    return p


def summarize(counts, rng):
    p0, p1, p2 = law(counts)
    s = M.gw_survival(p0, p1, p2)
    bs = []
    for _ in range(400):
        smp = [counts[rng.randrange(len(counts))] for _ in counts]
        bs.append(M.gw_survival(*law(smp)))
    bs.sort()
    return {"p0": round(p0, 4), "p1": round(p1, 4), "p2": round(p2, 4), "m": round(p1 + 2 * p2, 4),
            "P_est": round(s, 4), "P_est_ci95": [round(bs[10], 4), round(bs[389], 4)]}


def condition(g, cell, ctx, T, pool, seed):
    h = M.Harness(ctx, seed, cell)
    rng = random.Random(repr(("MAPOFF", seed, ctx, g.hex())))
    n = h.n
    rec = {"T": [], "W": [], "LABEL": [], "CAUSAL": []}
    st = (None, 0, 0)
    first = None
    lost = 0
    by_side = {0: [0, 0], 1: [0, 0]}
    for k in range(N):
        side = rng.randrange(2)
        pg = M.rand_genome(rng, n)
        if ctx in ("CARRY", "CARRY_L"):
            x = h.interact(g, pg, side, d_state=st, p_state=pool[rng.randrange(len(pool))])
            if ctx == "CARRY":
                st = x["d_state"]
            else:
                cands = []
                if h.d.anc == 0:
                    cands.append(x["d_state"])
                if h.p.anc == 0:
                    cands.append(x["p_state"])
                st = cands[rng.randrange(len(cands))] if cands else x["d_state"]
        else:
            x = h.interact(g, pg, side)
        dk = 1 if x["d_kept"] else 0
        lost += 1 - dk
        pT = 1 if (x["p_conv"] and M.ident(x["gp"], g, T) >= 0.9) else 0
        pW = 1 if (x["p_conv"] and M.ident(x["gp"], g) >= 0.9) else 0
        rec["T"].append(dk + pT)
        rec["W"].append(dk + pW)
        rec["LABEL"].append(x["label"])
        rec["CAUSAL"].append(dk + (1 if x["p_conv_causal"] else 0))
        by_side[side][0] += 1
        by_side[side][1] += x["p_conv"]
        if k == 0:
            first = x["p_conv"]
    brng = random.Random(seed)
    out = {d: summarize(v, brng) for d, v in rec.items()}
    out["conv_rate_by_side"] = {s: round(v[1] / v[0], 4) if v[0] else None for s, v in by_side.items()}
    out["donor_overwritten_rate"] = round(lost / N, 4)
    return out


def main():
    A = json.loads((M.P2 / "c_zero_specific" / "DONORS.json").read_text())
    B = json.loads((M.P2 / "x_p2_bridge" / "DONORS.json").read_text())
    g7 = M.run_ds.donor_genome()
    panels = {"A": [(i, d["hex"], d["origin"]) for i, d in enumerate(A)],
              "B": [(i, d["hex"], d["origin"]) for i, d in enumerate(B)],
              "S7AE3": [(0, g7.hex(), "7ae3_specimen")]}
    cells = {"A": ("CF",), "B": ("CF", "C7"), "S7AE3": ("C7", "CF")}
    pools = {c: partner_pool(c) for c in ("CF", "C7")}
    res = {"N": N, "contexts": CTX, "panels": {}}
    for pn, donors in panels.items():
        res["panels"][pn] = []
        for i, hx, origin in donors:
            g = bytes.fromhex(hx)
            T, src, nconv = transmitted(g)
            row = {"donor": i, "hex": hx, "origin": origin, "T_n": len(T), "T_src": src, "T_zero_conv_of_80": nconv,
                   "cells": {}}
            for c in cells[pn]:
                row["cells"][c] = {ctx: condition(g, c, ctx, T, pools[c], 30_000 + 97 * i + CTX.index(ctx))
                                   for ctx in CTX}
            res["panels"][pn].append(row)
            print(pn, i, {c: {x: row["cells"][c][x]["T"]["P_est"] for x in CTX} for c in row["cells"]},
                  round(time.process_time() - t0, 1), flush=True)
    res["cpu_s"] = round(time.process_time() - t0, 1)
    OUT.write_text(json.dumps(res, indent=1))
    print("cpu", res["cpu_s"])


if __name__ == "__main__":
    main()
