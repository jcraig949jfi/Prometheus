"""D-R4-3 (ANOM-1789417664459-0): do D1's rent and width valleys survive a symbol-split move?

D1c: the exact-cost (1+32) climber at eps=0 escapes the (alpha, beta) = (0, 0) trap 10/10 with SINGLE
(1 enc + 1 dec), but stays 0/10 in the rent cells (beta = 0.01, alpha < 1.5) and the width cells
(0.1, 0), (0.3, 0). The anomaly's discriminator: add a yield-neutral symbol-split move and pre-register
per cell which traps it crosses.

Operators (per child; split arms draw a split with P_SPLIT, else the SINGLE move):
  single   D1c SINGLE (lingua.signal.mutate n_enc=1, n_dec=1)
  split    yield-neutral split: pick a used symbol u (weighted by its R mass) and an input bit j uniform in
           0..7; the R values with enc == u and bit j set move to the smallest unused symbol inside the
           current width; dec[new] = dec[u]. No free symbol -> no-op. Target-blind: every bit of R is a
           candidate, the operator never reads the bucket (R >> 5).
  macro    the same split, but a saturated width grows by one bit (k + 1) to make the new symbol, and
           dec[new] is drawn uniformly (the split and a decoder re-point in ONE move)
  frozen   D1c FROZEN cheat (no enc, no dec, no width moves): must never escape

Seeds 10..19 are fresh (D1c used 0..9). Instrument: SINGLE and FROZEN at run seeds 0, 1 in cells (0, 0.01)
and (0.1, 0) must reproduce D1c's record rows exactly (cost, k, entries). Control: the split move is
yield-neutral on 512 random genomes (yield identical, entries +1 exactly where a split happened).

    python -m primordial.fabric.worker submit D primordial.cohorts.d.r4_3_symbol_split:job \\
        --exp D-R4-3-symbol-split --rows primordial/ledger/rows/D/D-R4-3-symbol-split.jsonl --ttl-cpu-s S
"""
from __future__ import annotations

import json
import pathlib
import time

import numpy as np

from primordial.cohorts.d.d1c_run import ALPHAS, BETAS, DELTA, EPS, ESC, LAM, OPS, R_ALL, exact_cost
from primordial.lingua import signal as S

EXP = "D-R4-3-symbol-split"
ROOT = pathlib.Path(__file__).resolve().parents[3]
D1C_ROWS = ROOT / "primordial" / "ledger" / "rows" / "D" / "D1c-operator-unbundling.jsonl"
P_SPLIT = 0.5
GENS = 4000
SEEDS = tuple(range(10, 20))
INSTRUMENT = ((0.0, 0.01), (0.1, 0.0))
BITS = np.arange(S.N_R)


def split_move(rng, k, enc, dec, macro: bool):
    """Split one used symbol of each genome on a random input bit (see module doc). Returns (k, enc, dec, did)."""
    k, enc, dec = k.copy(), enc.copy(), dec.copy()
    did = np.zeros(len(k), bool)
    for i in range(len(k)):
        e = enc[i]
        u = e[rng.integers(0, S.N_R)]
        j = int(rng.integers(0, 8))
        grp = e == u
        sub = grp & (((BITS >> j) & 1) == 1)
        n = int(sub.sum())
        if n == 0 or n == int(grp.sum()):
            continue
        used = np.zeros(S.N_R, bool)
        used[e] = True
        width = 1 << int(k[i])
        free = np.nonzero(~used[1:width])[0]
        if len(free):
            s = int(free[0]) + 1
        elif macro and k[i] < 8:
            s, k[i] = width, k[i] + 1
        else:
            continue
        enc[i, sub] = s
        dec[i, s] = int(rng.integers(0, S.N_ACT)) if macro else dec[i, u]
        did[i] = True
    return k, enc, dec, did


def children(rng, k, enc, dec, op):
    K, E, D = np.repeat(k, LAM), np.repeat(enc, LAM, 0), np.repeat(dec, LAM, 0)
    if op in OPS:
        return S.mutate(rng, K, E, D, **OPS[op])
    m = rng.random(LAM) < P_SPLIT
    if m.any():
        K[m], E[m], D[m], _ = split_move(rng, K[m], E[m], D[m], op == "macro")
    if (~m).any():
        K[~m], E[~m], D[~m] = S.mutate(rng, K[~m], E[~m], D[~m], **OPS["single"])
    return K, E, D


def climb(a, b, s, op, gens=GENS) -> dict:
    """D1c.climb with the operator swapped in (identical RNG path for single / frozen)."""
    t0 = time.perf_counter()
    rng = np.random.Generator(np.random.PCG64(7919 * s + 100003))
    k, enc, dec = S.random_genomes(rng, 1)
    pc = start = float(exact_cost(k, enc, dec, a, b)[0])
    best = (pc, k, enc, dec)
    accepts = 0
    for _ in range(gens):
        ck, ce, cd = children(rng, k, enc, dec, op)
        cc = exact_cost(ck, ce, cd, a, b)
        j = LAM - 1 - int(np.argmin(cc[::-1]))
        if cc[j] <= pc + EPS:
            accepts += cc[j] < pc - 1e-12
            k, enc, dec, pc = ck[j:j + 1], ce[j:j + 1], cd[j:j + 1], float(cc[j])
            if pc < best[0]:
                best = (pc, k, enc, dec)
    c, bk, be, bd = best
    m_opt, c_opt = S.analytic_optimum(a, b, DELTA)
    return {"alpha": a, "beta": b, "run_seed": s, "op": op, "gens": gens, "start_cost": start, "cost": c,
            "gap": c - c_opt, "escaped": bool(c - c_opt <= ESC), "opt_m": m_opt, "k": int(bk[0]),
            "entries": int(S.entries(be)[0]), "improving_accepts": int(accepts),
            "yield": float(S.evaluate(bk, be, bd, R_ALL, a, b, DELTA)[1][0]), "wall_s": round(time.perf_counter() - t0, 2)}


def neutral_control(n=512) -> dict:
    rng = np.random.Generator(np.random.PCG64(4459))
    k, enc, dec = S.random_genomes(rng, n)
    k2, e2, d2, did = split_move(rng, k, enc, dec, macro=False)
    y0 = S.evaluate(k, enc, dec, R_ALL, 0.0, 0.0, DELTA)[1]
    y1 = S.evaluate(k2, e2, d2, R_ALL, 0.0, 0.0, DELTA)[1]
    de = S.entries(e2) - S.entries(enc)
    return {"kind": "neutral_control", "n": n, "n_split": int(did.sum()), "yield_identical": bool(np.array_equal(y0, y1)),
            "entries_plus1_iff_split": bool(np.array_equal(de, did.astype(int))), "width_unchanged": bool(np.array_equal(k, k2))}


def d1c_rows() -> dict:
    out = {}
    for line in D1C_ROWS.read_text(encoding="utf-8").splitlines():
        x = json.loads(line)
        if x.get("kind") == "climb" and x.get("gens") == GENS:
            out[(x["alpha"], x["beta"], x["run_seed"], x["op"])] = x
    return out


def plan(seeds=SEEDS, ops=("single", "split", "macro", "frozen")):
    jobs = [("instrument", a, b, s, op) for a, b in INSTRUMENT for s in (0, 1) for op in ("single", "frozen")]
    return jobs + [("run", a, b, s, op) for op in ops for a in ALPHAS for b in BETAS for s in seeds]


def job(ctx, seeds=SEEDS, ops=("single", "split", "macro", "frozen"), gens=GENS, dev=False):
    st = ctx.load_checkpoint() or {"done": {}, "control": None}
    if st["control"] is None:
        st["control"] = neutral_control()
        ctx.emit({**st["control"], "status": "control"})
        ctx.checkpoint(st)
    ref = d1c_rows()
    for n, (what, a, b, s, op) in enumerate(plan(seeds, ops)):
        key = f"{what}|{a}|{b}|{s}|{op}"
        if key in st["done"]:
            continue
        if ctx.should_pause():
            ctx.pause(st)
        r = climb(a, b, s, op, gens)
        if what == "instrument":
            d = ref[(a, b, s, op)]
            r.update(kind="instrument", reproduces_d1c=bool(abs(r["cost"] - d["cost"]) < 1e-12 and r["k"] == d["k"]
                                                          and r["entries"] == d["entries"]), status="control")
        else:
            r.update(kind="climb", status="cheat" if op == "frozen" else ("control" if a == 1.5 else ("dev" if dev else "record")))
        ctx.emit(r)
        st["done"][key] = r
        if n % 8 == 7:
            ctx.checkpoint(st)
    ctx.emit({**verdict(list(st["done"].values()), st["control"], len(seeds)), "status": "dev" if dev else "record"})


TRAPPED = ((0.0, 0.01), (0.1, 0.0), (0.1, 0.01), (0.3, 0.0), (0.3, 0.01), (0.6, 0.01))     # D1c SINGLE 0/10


def verdict(rows, control, n) -> dict:
    """Pre-registered checks (bus predicate D-R4-3)."""
    cl = [x for x in rows if x["kind"] == "climb"]

    def esc(op, a, b):
        return sum(x["escaped"] for x in cl if x["op"] == op and x["alpha"] == a and x["beta"] == b)

    table = {f"a{a}_b{b}": {op: f"{esc(op, a, b)}/{n}" for op in ("single", "split", "macro", "frozen")}
             for a in ALPHAS for b in BETAS}
    gap = {f"a{a}_b{b}": {op: float(np.median([x["gap"] for x in cl if x["op"] == op and x["alpha"] == a
                                               and x["beta"] == b] or [np.nan]))
                          for op in ("single", "split", "macro", "frozen")} for a in ALPHAS for b in BETAS}
    ins = [x for x in rows if x["kind"] == "instrument"]
    return {"kind": "summary", "exp": EXP, "n_seeds": n, "escape_table": table, "median_gap": gap,
            "checks": {
                "I_single_frozen_reproduce_d1c": bool(ins) and all(x["reproduces_d1c"] for x in ins),
                "C_split_is_yield_neutral": control["yield_identical"] and control["entries_plus1_iff_split"]
                                            and control["width_unchanged"] and control["n_split"] > 0,
                "C_frozen_never_escapes": all(esc("frozen", a, b) == 0 for a in ALPHAS for b in BETAS),
                "C_alpha1.5_real_ops_all_escape": all(esc(op, 1.5, b) == n for op in ("single", "split", "macro") for b in BETAS),
                "R_single_replicates_d1c_traps_fresh_seeds": all(esc("single", a, b) <= 0.2 * n for a, b in TRAPPED),
                "P1_split_crosses_no_trapped_cell": all(esc("split", a, b) <= 0.2 * n for a, b in TRAPPED),
                "P2_macro_crosses_every_trapped_cell": all(esc("macro", a, b) >= 0.8 * n for a, b in TRAPPED)}}
