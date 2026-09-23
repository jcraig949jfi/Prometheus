"""P-D01 [deformation A]: LOCALITY DOSE SURFACE.

Parent T-ARCH4/M1. Damage of k instructions (k in 2,4,8) spread over s windows (s in 1,2,4,8;
s <= k; window width k/s) placed EVENLY around the genome or at RANDOM distinct positions; kind
in {delete, opcode (opcode word := random uint32), operand (one operand word := random uint32),
move (each window swapped with a random non-overlapping window of equal width: displacement
without deletion)}; decode in {modulo, trap-NOP}; genotype sets: viable parents, walker-16
descendants (walker 1), C4-08 ordinary top-32 (seed 1); 4 draws per cell; scored on the parent
environment (loss, displacement, D-class without the exaptation branch) and on the held-out
world W2_K2d1 (reward change). A per-cell regression of loss on log2 k, log2 s, kind, placement,
decode, genotype set says which quantity controls damage. Computational scope: integer programs
on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from collections import Counter

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
A, L = CM.A, CM.L

PID, TID = "P-D01", "T-ARCH4/M1"
KS, KINDS, PLACES, DECODES, DRAWS = (2, 4, 8), ("delete", "opcode", "operand", "move"), ("even", "random"), ("modulo", "nop"), 4
HELD = A.with_knobs(A.WorldSpec("W2_K2", K=2, value_bits=4), name="W2_K2d1", delay=1)


def c408_tops(seed=1, n=32):
    p = A.ARCH / "archaeon" / "campaign4" / "C4-08" / "attempts" / "a01" / "final_tops.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    for e in d:
        if e["arm"] == "ordinary" and e["seed"] == seed:
            out = []
            for i, x in enumerate(e["final_top"][:n]):
                m = x["manifest"] if isinstance(x, dict) and "manifest" in x else x
                out.append({"organism_id": "c408-s%d-%d" % (seed, i), "stratum": "c408_ordinary", "manifest": m, "env": "W2_K2"})
            return out
    return []


def windows(n, k, s, place, rng):
    w = max(1, k // s)
    if place == "even" or s == 1:
        off = int(rng.next_u32() % n)
        starts = [(off + int(round(i * n / s))) % n for i in range(s)]
    else:
        # BOUNDED rejection sampling (run 1 hung for 3 h in two workers on an unbounded loop, CW01-D075):
        # windows must not overlap, measured on the ring; after 500 rejections fall back to even placement.
        starts, tries = [], 0
        while len(starts) < s and tries < 500:
            tries += 1
            c = int(rng.next_u32() % n)
            if all(min(abs(c - t), n - abs(c - t)) >= w for t in starts):
                starts.append(c)
        if len(starts) < s:
            off = int(rng.next_u32() % n)
            starts = [(off + int(round(i * n / s))) % n for i in range(s)]
    return [[(st + j) % n for j in range(w)] for st in starts]


def damage(m, kind, wins, rng, decode):
    c = json.loads(json.dumps(m))
    g = c["genome"]
    n = len(g) // A.IW
    if kind == "delete":
        idx = {i for w in wins for i in w}
        keep = [x for i, x in enumerate(g) if (i // A.IW) not in idx]
        c["genome"] = keep if len(keep) >= A.IW else g[:A.IW]
    elif kind == "opcode":
        for w in wins:
            for i in w:
                g[i * A.IW] = int(rng.next_u32())
    elif kind == "operand":
        for w in wins:
            for i in w:
                g[i * A.IW + 1 + int(rng.next_u32() % 3)] = int(rng.next_u32())
    else:
        for w in wins:
            wd = len(w)
            for _try in range(8):
                st = int(rng.next_u32() % n)
                other = [(st + j) % n for j in range(wd)]
                if not set(other) & set(w):
                    for a, b in zip(w, other):
                        ia, ib = a * A.IW, b * A.IW
                        g[ia:ia + A.IW], g[ib:ib + A.IW] = g[ib:ib + A.IW], g[ia:ia + A.IW]
                    break
    c, _ = A.trap(c, decode)
    return c


def reduced_class(child_ev, parent_ev, disp, env):
    c, p = child_ev[env], parent_ev[env]
    r, rp = c["reward_per_ask"], p["reward_per_ask"]
    if c["answered_share"] == 0.0 or c.get("_constant_answer"):
        return "D2"
    if r > rp + A.C1.BAND:
        return "D7"
    if abs(r - rp) <= A.C1.BAND:
        return "D5"
    if r >= A.C1.FLOOR:
        return "D4"
    return "D3"


def job(j):
    p = j["program"]
    env = p["env"]
    eps = {env: A.episodes(env), "HELD": A.episodes_for(HELD, A.CAMPAIGN_SEED, "train", 1, A.C1.E)}
    pm = A.canonical(p["manifest"])
    pev = A.eval_all(pm, eps)
    n = CM.n_instr(pm)
    rows = []
    for k in KS:
        for s in (1, 2, 4, 8):
            if s > k or k // s < 1 or k >= n:
                continue
            for place in PLACES:
                if s == 1 and place == "random":
                    continue
                for kind in KINDS:
                    for dec in DECODES:
                        for d in range(1, DRAWS + 1):
                            rng = A.SplitMix64(A.seed_from("nestor.pd01", A.LOOP_SEED, p["organism_id"], k, s, place, kind, dec, d))
                            wins = windows(n, k, s, place, rng)
                            child = damage(pm, kind, wins, rng, dec)
                            cev = A.eval_all(child, eps)
                            disp = A.C1.displacement(cev[env]["_answers"], pev[env]["_answers"])
                            D = reduced_class(cev, pev, disp, env)
                            rows.append({"pid": p["organism_id"], "set": p["stratum"], "k": k, "s": s, "place": place, "kind": kind, "decode": dec, "draw": d,
                                         "D": D, "loss": int(D in ("D2", "D3")), "disp": disp, "held_delta": cev["HELD"]["reward_per_ask"] - pev["HELD"]["reward_per_ask"],
                                         "held_exapt": int(cev["HELD"]["reward_per_ask"] >= pev["HELD"]["reward_per_ask"] + A.C1.BAND and cev["HELD"]["reward_per_ask"] >= A.C1.FLOOR)})
    return rows


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "A", "scope": CM.SCOPE, "claim_type": "parameterized-dose-surface",
                         "factors": {"k": KS, "s": [1, 2, 4, 8], "placement": PLACES, "kind": KINDS, "decode": DECODES, "draws": DRAWS,
                                     "genotype_sets": ["viable parents", "walker16 (walker 1)", "C4-08 ordinary top-32 seed 1"], "held_out": "W2_K2d1"},
                         "held_fixed": "classification constants, episodes (CRN), programs' behaviour (canonicalised)",
                         "attacks": "what controls damage at equal count: sites, placement, word kind, decode, genotype set (P-C04/P-C15 saw two points)",
                         "analysis": "cell means; least-squares of loss on log2 k, log2 s, kind, placement, decode, set; paired sign-flips s=8 vs s=1 at k=8 and k=8 vs k=2 at s=1",
                         "continuation": ["window width 1/2/4/8 at fixed k", "gap as a continuous variable", "opcode category of hit instructions", "pairwise site epistasis", "other held-out families", "C5 representation B"],
                         "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    programs = [dict(p, stratum="parent") for p in parents]
    for p in parents:
        wk = A.C5.walk(p["manifest"], p["organism_id"], 1, A.episodes(p["env"]), 16, 32)
        programs.append({"organism_id": p["organism_id"] + "/w1", "stratum": "walker16", "manifest": wk["archived"].get(wk["depth"]), "env": p["env"]})
    programs += c408_tops()
    with A.pool(8) as ex:
        rows = [r for rs in ex.map(job, [{"program": p} for p in programs]) for r in rs]
    # cell means
    cells = {}
    for r in rows:
        key = (r["set"], r["k"], r["s"], r["place"], r["kind"], r["decode"])
        c = cells.setdefault(key, {"n": 0, "loss": 0.0, "disp": 0.0, "held_exapt": 0.0, "D7": 0})
        c["n"] += 1
        c["loss"] += r["loss"]
        c["disp"] += r["disp"]
        c["held_exapt"] += r["held_exapt"]
        c["D7"] += int(r["D"] == "D7")
    table = [{"set": k[0], "k": k[1], "s": k[2], "place": k[3], "kind": k[4], "decode": k[5], "n": v["n"], "loss": v["loss"] / v["n"],
              "disp": v["disp"] / v["n"], "held_exapt": v["held_exapt"] / v["n"], "D7": v["D7"]} for k, v in cells.items()]
    # regression on rows
    kinds, places, decs, sets = list(KINDS), list(PLACES), list(DECODES), sorted({r["set"] for r in rows})
    X, y = [], []
    for r in rows:
        x = [1.0, np.log2(r["k"]), np.log2(r["s"])]
        x += [1.0 if r["kind"] == kd else 0.0 for kd in kinds[1:]]
        x += [1.0 if r["place"] == "random" else 0.0, 1.0 if r["decode"] == "nop" else 0.0]
        x += [1.0 if r["set"] == st else 0.0 for st in sets[1:]]
        X.append(x)
        y.append(r["loss"])
    X, y = np.array(X), np.array(y)
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    names = ["intercept", "log2_k", "log2_s"] + ["kind=" + kd for kd in kinds[1:]] + ["place=random", "decode=nop"] + ["set=" + st for st in sets[1:]]
    coef = dict(zip(names, [float(b) for b in beta]))

    def per_prog(filter_fn):
        out = {}
        for r in rows:
            if filter_fn(r):
                out.setdefault(r["pid"], []).append(r["loss"])
        return {k: float(np.mean(v)) for k, v in out.items()}
    a = per_prog(lambda r: r["k"] == 8 and r["s"] == 8 and r["kind"] == "delete" and r["decode"] == "modulo")
    b = per_prog(lambda r: r["k"] == 8 and r["s"] == 1 and r["kind"] == "delete" and r["decode"] == "modulo")
    c = per_prog(lambda r: r["k"] == 8 and r["s"] == 1 and r["kind"] == "delete" and r["decode"] == "modulo")
    d = per_prog(lambda r: r["k"] == 2 and r["s"] == 1 and r["kind"] == "delete" and r["decode"] == "modulo")
    contrasts = {"sites_8_minus_1_at_k8_delete": CM.paired_signflip([a[p] - b[p] for p in a if p in b]),
                 "k_8_minus_2_at_s1_delete": CM.paired_signflip([c[p] - d[p] for p in c if p in d])}
    kind_loss = {kd: float(np.mean([r["loss"] for r in rows if r["kind"] == kd])) for kd in KINDS}
    dec_loss = {dc: float(np.mean([r["loss"] for r in rows if r["decode"] == dc])) for dc in DECODES}
    s_loss = {s: float(np.mean([r["loss"] for r in rows if r["s"] == s and r["k"] == 8])) for s in (1, 2, 4, 8)}
    k_loss = {k: float(np.mean([r["loss"] for r in rows if r["k"] == k and r["s"] == 1])) for k in KS}
    place_loss = {pl: float(np.mean([r["loss"] for r in rows if r["place"] == pl and r["s"] > 1])) for pl in PLACES}
    material = bool(abs(coef["log2_s"]) > 0.02 or abs(coef["decode=nop"]) > 0.05 or contrasts["sites_8_minus_1_at_k8_delete"] and contrasts["sites_8_minus_1_at_k8_delete"]["above_p95"])
    out = {"perturbation_id": PID, "parent": TID, "n_programs": len(programs), "n_rows": len(rows), "cells": len(table),
           "regression_loss": coef, "marginals": {"kind": kind_loss, "decode": dec_loss, "sites_at_k8": s_loss, "k_at_s1": k_loss, "placement": place_loss},
           "contrasts": contrasts, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "cells.json").write_text(json.dumps(table, ensure_ascii=True, default=CM.js), encoding="utf-8")
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "locality dose surface: loss coefficients log2_s %+.3f, log2_k %+.3f, decode=nop %+.3f, place=random %+.3f; sites at k=8 %s; kinds %s"
                      % (coef["log2_s"], coef["log2_k"], coef["decode=nop"], coef["place=random"], {k: round(v, 3) for k, v in s_loss.items()}, {k: round(v, 3) for k, v in kind_loss.items()}),
                      material, detail={"regression": coef, "marginals": out["marginals"], "contrasts": contrasts})
    print("DONE material=%s %s (%.0f s)" % (material, json.dumps({"coef": {k: round(v, 3) for k, v in coef.items()}, "sites_k8": {k: round(v, 3) for k, v in s_loss.items()}, "k_s1": {k: round(v, 3) for k, v in k_loss.items()}, "kind": {k: round(v, 3) for k, v in kind_loss.items()}, "decode": {k: round(v, 3) for k, v in dec_loss.items()}}), time.time() - t0))


if __name__ == "__main__":
    main()
