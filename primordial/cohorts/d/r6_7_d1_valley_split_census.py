"""D-R6-7 (ANOM-1789451432892-0): why do D1's valleys (0.3, 0), (0.3, 0.01), (0.6, 0.01) keep the same gap under the
single move, the neutral split and the split + re-point macro (D-R4-3)?

The anomaly's post hoc mechanism: a split on ONE input bit moves about half of a symbol's R mass, while the optimal code
gives one bucket (R >> 5, 1/8 of the mass) its own symbol, so a one-bit split pays more bits than it gains; a
target-blind THREE-bit split (1/8 mass) would pay. Zero search here: an exact 1-step census of every split from every
trapped code.

Trapped codes: D-R4-3's climbs are deterministic (its instrument reproduced D1c exactly), so each trapped code is
re-derived by replaying r4_3_symbol_split.climb with the best genome kept, and must reproduce the committed row.

Census, per trapped genome (k, enc, dec) at exact cost c (lingua.signal.evaluate over all 256 R):
  for every used symbol u and every subset of its R group
    one_bit   R with bit j == p                          (j in 0..7, p in {0, 1}; 16 subsets)
    three_bit R with bits (j1, j2, j3) == pattern v      (56 bit triples x 8 patterns; includes the bucket bits 5, 6, 7)
  (empty or whole-group subsets skipped), the subset moves to a new symbol s (the smallest unused symbol below 1 << k,
  else s = 1 << k and k + 1 when k < 8, else no move), and dec[s] takes each of the 8 actions (dec[s] == dec[u] is the
  neutral split, any other value the split + re-point). improving = cost < c - 1e-12.

Rule (fixed before reading). T = trapped genomes = D-R4-3 record climbs in the three cells, ops single / split /
macro, escaped False.
  I1  every replayed climb reproduces its committed row (cost to 1e-12, k, entries, escaped); the hand code for each
      cell's analytic optimum m* costs exactly c_opt -- else INDETERMINATE.
  f1 = fraction of T with >= 1 improving one_bit move; f3 = fraction with >= 1 improving three_bit move.
  MASS_BARRIER    f1 <= 0.2 and f3 >= 0.8
  DEEPER_VALLEY   f1 <= 0.2 and f3 <= 0.2
  SAMPLING_MISS   f1 >= 0.8   (single-move escapes exist; the climbers did not draw them)
  MIXED           otherwise
Controls per cell: optimum_has_no_improving_move (hand_code(m*) census: 0 improving in both families -- no code costs
below c_opt); planted_one_symbol_short (hand_code(m* - 1), when m* >= 2: >= 1 improving three_bit move).
"""
from __future__ import annotations

import itertools
import json
import pathlib
import time

import numpy as np

from primordial.cohorts.d import r4_3_symbol_split as R43
from primordial.cohorts.d.d1c_run import DELTA, EPS, ESC, LAM, R_ALL, exact_cost
from primordial.lingua import signal as S

EXP = "D-R6-7-d1-valley-split-census"
PREDICATE_ID = EXP
ANOMALY = "1789451432892-0"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
SRC_ROWS = "primordial/ledger/rows/D/D-R4-3-symbol-split.jsonl"
CELLS = ((0.3, 0.0), (0.3, 0.01), (0.6, 0.01))
OPS3 = ("single", "split", "macro")
TRIPLES = list(itertools.combinations(range(8), 3))
CHUNK = 8192


def replay(a, b, s, op, gens=R43.GENS):
    """r4_3_symbol_split.climb, identical RNG path, returning the best genome as well."""
    rng = np.random.Generator(np.random.PCG64(7919 * s + 100003))
    k, enc, dec = S.random_genomes(rng, 1)
    pc = float(exact_cost(k, enc, dec, a, b)[0])
    best = (pc, k, enc, dec)
    for _ in range(gens):
        ck, ce, cd = R43.children(rng, k, enc, dec, op)
        cc = exact_cost(ck, ce, cd, a, b)
        j = LAM - 1 - int(np.argmin(cc[::-1]))
        if cc[j] <= pc + EPS:
            k, enc, dec, pc = ck[j:j + 1], ce[j:j + 1], cd[j:j + 1], float(cc[j])
            if pc < best[0]:
                best = (pc, k, enc, dec)
    c, bk, be, bd = best
    m_opt, c_opt = S.analytic_optimum(a, b, DELTA)
    return {"cost": c, "k": int(bk[0]), "entries": int(S.entries(be)[0]), "escaped": bool(c - c_opt <= ESC),
            "gap": c - c_opt}, (int(bk[0]), be[0].copy(), bd[0].copy())


def subsets(enc_row: np.ndarray) -> list[tuple[str, int, np.ndarray]]:
    """[(family, u, mask [256])] for every used symbol u: one_bit and three_bit subsets, not empty, not the whole group."""
    R = np.arange(S.N_R)
    out = []
    for u in np.unique(enc_row):
        grp = enc_row == u
        n = int(grp.sum())
        for j in range(8):
            for p in (0, 1):
                m = grp & (((R >> j) & 1) == p)
                if 0 < m.sum() < n:
                    out.append(("one_bit", int(u), m))
        for t in TRIPLES:
            code = ((R >> t[0]) & 1) | (((R >> t[1]) & 1) << 1) | (((R >> t[2]) & 1) << 2)
            for v in range(8):
                m = grp & (code == v)
                if 0 < m.sum() < n:
                    out.append(("three_bit", int(u), m))
    return out


def census(k: int, enc_row: np.ndarray, dec_row: np.ndarray, a: float, b: float) -> dict:
    c0 = float(exact_cost(np.array([k]), enc_row[None], dec_row[None], a, b)[0])
    used = np.zeros(S.N_R, bool)
    used[enc_row] = True
    width = 1 << k
    free = np.nonzero(~used[1:width])[0]
    if len(free):
        s, k2 = int(free[0]) + 1, k
    elif k < 8:
        s, k2 = width, k + 1
    else:
        return {"cost": c0, "moves": 0, "one_bit": {"n": 0, "improving": 0, "best_delta": None},
                "three_bit": {"n": 0, "improving": 0, "best_delta": None}, "new_symbol": None}
    subs = subsets(enc_row)
    fam = np.array([f for f, _, _ in subs])
    us = np.array([u for _, u, _ in subs])
    masks = np.stack([m for _, _, m in subs]) if subs else np.zeros((0, S.N_R), bool)
    out = {"cost": c0, "new_symbol": s, "k_after": k2, "moves": int(len(subs) * S.N_ACT)}
    deltas = np.empty((len(subs), S.N_ACT))
    for d in range(S.N_ACT):
        for i0 in range(0, len(subs), CHUNK):
            M = masks[i0:i0 + CHUNK]
            E = np.where(M, s, enc_row[None, :])
            D = np.repeat(dec_row[None, :], len(M), 0)
            D[:, s] = d
            K = np.full(len(M), k2)
            deltas[i0:i0 + CHUNK, d] = exact_cost(K, E, D, a, b) - c0
    neutral = deltas[np.arange(len(subs)), dec_row[us]] if len(subs) else np.zeros(0)
    for f in ("one_bit", "three_bit"):
        sel = fam == f
        dd = deltas[sel]
        out[f] = {"n": int(dd.size), "improving": int((dd < -1e-12).sum()),
                  "best_delta": float(dd.min()) if dd.size else None,
                  "neutral_improving": int((neutral[sel] < -1e-12).sum()) if sel.any() else 0}
    return out


def decide(i1: bool, controls_ok: bool, f1: float, f3: float) -> str:
    if not (i1 and controls_ok):
        return "INDETERMINATE"
    if f1 >= 0.8:
        return "SAMPLING_MISS"
    if f1 <= 0.2 and f3 >= 0.8:
        return "MASS_BARRIER"
    if f1 <= 0.2 and f3 <= 0.2:
        return "DEEPER_VALLEY"
    return "MIXED"


def committed(text: str) -> dict:
    out = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        x = json.loads(line)
        if x.get("kind") == "climb" and x.get("status") == "record" and (x["alpha"], x["beta"]) in CELLS and x["op"] in OPS3:
            out[(x["alpha"], x["beta"], x["run_seed"], x["op"])] = x
    return out


def job(ctx, status="record"):
    t0 = time.perf_counter()
    text = (ROOT / SRC_ROWS).read_text(encoding="utf-8")
    ref = committed(text)
    trapped, repro = [], []
    for (a, b, s, op), x in sorted(ref.items()):
        got, (k, e, d) = replay(a, b, s, op)
        ok = (abs(got["cost"] - x["cost"]) < 1e-12 and got["k"] == x["k"] and got["entries"] == x["entries"]
              and got["escaped"] == x["escaped"])
        repro.append(ok)
        if not x["escaped"]:
            cen = census(k, e, d, a, b)
            trapped.append({"alpha": a, "beta": b, "run_seed": s, "op": op, "k": k, "entries": got["entries"],
                            "gap": got["gap"], "cost": cen["cost"], "new_symbol": cen["new_symbol"], "moves": cen["moves"],
                            "one_bit": cen["one_bit"], "three_bit": cen["three_bit"]})
    controls, hand_ok = {}, True
    for a, b in CELLS:
        m, c_opt = S.analytic_optimum(a, b, DELTA)
        hk, he, hd = S.hand_code(m)
        hc = float(exact_cost(np.array([hk]), he[None], hd[None], a, b)[0])
        hand_ok &= abs(hc - c_opt) < 1e-12
        opt = census(hk, he, hd, a, b)
        ctl = {"m_opt": m, "c_opt": c_opt, "hand_cost": hc,
               "optimum_improving": opt["one_bit"]["improving"] + opt["three_bit"]["improving"]}
        if m >= 2:
            sk, se, sd = S.hand_code(m - 1)
            short = census(sk, se, sd, a, b)
            ctl["short_three_bit_improving"] = short["three_bit"]["improving"]
            ctl["short_one_bit_improving"] = short["one_bit"]["improving"]
        controls[f"a{a}_b{b}"] = ctl
    ctl_ok = all(v["optimum_improving"] == 0 and v.get("short_three_bit_improving", 1) >= 1 for v in controls.values())
    n = len(trapped)
    f1 = sum(t["one_bit"]["improving"] >= 1 for t in trapped) / n if n else 0.0
    f3 = sum(t["three_bit"]["improving"] >= 1 for t in trapped) / n if n else 0.0
    i1 = {"replay_reproduces_committed": bool(repro) and all(repro), "n_replayed": len(repro),
          "hand_code_costs_c_opt": bool(hand_ok), "trapped_nonempty": n > 0}
    decision = decide(all(v for k_, v in i1.items() if k_ != "n_replayed"), ctl_ok, f1, f3)
    per_cell = {}
    for a, b in CELLS:
        tt = [t for t in trapped if (t["alpha"], t["beta"]) == (a, b)]
        per_cell[f"a{a}_b{b}"] = {"trapped": len(tt), "one_bit_any": sum(t["one_bit"]["improving"] >= 1 for t in tt),
                                  "three_bit_any": sum(t["three_bit"]["improving"] >= 1 for t in tt)}
    ctx.emit({"kind": "summary", "exp": EXP, "predicate_id": PREDICATE_ID, "anomaly": ANOMALY, "status": status,
              "ts": round(time.time(), 3), "source_rows": SRC_ROWS, "qd_runs": 0, "climb_replays": len(repro),
              "checks": {"I1": i1, "controls_ok": bool(ctl_ok)}, "controls": controls,
              "n_trapped": n, "f1_one_bit_improving": f1, "f3_three_bit_improving": f3, "per_cell": per_cell,
              "trapped": trapped, "decision": decision, "wall_s": round(time.perf_counter() - t0, 3)})
