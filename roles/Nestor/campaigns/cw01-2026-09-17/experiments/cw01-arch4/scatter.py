"""The SCATTERED damage ruler (T-R01): each eligible instruction is independently hit with probability f.

mask(n, f, key)           Bernoulli mask from a seed built from `key` (exactly reproducible)
apply(m, mask, mode, key) 'delete' removes hit instructions (at least one instruction is kept);
                          'nop' disables them (opcode := NOP; length and jump topology preserved);
                          'operand' randomises one operand word of each hit instruction
reach_map(m, eps)         HALT-probe: instruction i is REACHED if replacing its opcode by HALT changes
                          the program's answers on eps
telemetry(m, mask, reach) n_eligible, n_hit, fraction_hit, executable hits, persistent-state hits,
                          category distribution of hits
assay(...)                mean loss (D2/D3), displacement, ABSOLUTE reward change, telemetry over draws
sham(...)                 the mask is drawn and nothing is applied; the same evaluation route is taken

Computational scope: integer programs on a bounded VM."""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "P-D01"))
import common as CM            # noqa: E402
from run_PD01 import reduced_class   # noqa: E402
A = CM.A
PERSISTENT_CATS = ("read_write", "indirection")
PROVENANCE = {"intervention_family": "blind structural damage", "geometry": "scattered, per-instruction, independent", "sampling_law": "Bernoulli(f) per eligible instruction",
              "normalisation": "loss = D2/D3 share over draws (binary); dreward = absolute reward_per_ask change", "denominator": "draws (4) per cell; programs paired with themselves",
              "price_assumptions": "none (no price in the evaluation)", "viability_floor": "3/16 on reward_per_ask (D3 below it)",
              "alters_baseline_function": "no: the baseline is the undamaged program; the sham path verifies the route", "qualification": "P-G01 (RESULT.json disposition)"}


def mask(n, f, key):
    rng = A.SplitMix64(A.seed_from("nestor.scatter", A.LOOP_SEED, *key))
    return [rng.unit() < f for _ in range(n)]


def apply(m, msk, mode, key):
    c = json.loads(json.dumps(m))
    g = c["genome"]
    n = len(g) // A.IW
    hit = [i for i in range(n) if msk[i]]
    if mode == "delete":
        if len(hit) >= n:
            hit = hit[:-1]
        keep = [w for i in range(n) if i not in set(hit) for w in g[i * A.IW:(i + 1) * A.IW]]
        c["genome"] = keep if keep else g[:A.IW]
    elif mode == "nop":
        for i in hit:
            g[i * A.IW] = A.NOP
    elif mode == "operand":
        rng = A.SplitMix64(A.seed_from("nestor.scatter.operand", A.LOOP_SEED, *key))
        for i in hit:
            g[i * A.IW + 1 + int(rng.next_u32() % 3)] = int(rng.next_u32())
    else:
        raise ValueError(mode)
    return c


def reach_map(m, eps):
    base = A.C1.answers(m, eps)
    n = len(m["genome"]) // A.IW
    out = []
    for i in range(n):
        c = json.loads(json.dumps(m))
        c["genome"][i * A.IW] = A.HALT
        out.append(A.C1.answers(c, eps) != base)
    return out


def telemetry(m, msk, reach=None):
    g = m["genome"]
    n = len(g) // A.IW
    hits = [i for i in range(n) if msk[i]]
    cats = {}
    for i in hits:
        cat = A.CATEGORY[g[i * A.IW] % A.N_OPCODES]
        cats[cat] = cats.get(cat, 0) + 1
    return {"n_eligible": n, "n_hit": len(hits), "fraction_hit": len(hits) / max(1, n), "executable_hits": (sum(1 for i in hits if reach[i]) if reach else None),
            "persistent_state_hits": sum(1 for i in hits if A.CATEGORY[g[i * A.IW] % A.N_OPCODES] in PERSISTENT_CATS), "categories": cats, "positions": hits}


def assay(pm, env, eps, f, draws, mode, tag, reach=None, pev=None):
    pev = pev or A.eval_all(pm, {env: eps})
    if pev[env]["answered_share"] == 0.0:
        return {"degenerate": True}
    n = len(pm["genome"]) // A.IW
    rows = []
    for d in range(1, draws + 1):
        key = (tag, mode, f, d)
        msk = mask(n, f, key)
        child = apply(pm, msk, mode, key)
        cev = A.eval_all(child, {env: eps})
        disp = A.C1.displacement(cev[env]["_answers"], pev[env]["_answers"])
        D = reduced_class(cev, pev, disp, env)
        t = telemetry(pm, msk, reach)
        rows.append({"draw": d, "D": D, "loss": int(D in ("D2", "D3")), "disp": disp, "dreward": cev[env]["reward_per_ask"] - pev[env]["reward_per_ask"], **{k: v for k, v in t.items() if k != "positions"}})
    return {"degenerate": False, "r0": pev[env]["reward_per_ask"], "n_instr": n, "persistent_words": pev[env]["meter"].get("persistent_state_words", 0),
            "loss": float(np.mean([r["loss"] for r in rows])), "disp": float(np.mean([r["disp"] for r in rows])), "dreward": float(np.mean([r["dreward"] for r in rows])),
            "fraction_hit": float(np.mean([r["fraction_hit"] for r in rows])), "n_hit": float(np.mean([r["n_hit"] for r in rows])),
            "executable_hits": (float(np.mean([r["executable_hits"] for r in rows])) if reach else None), "persistent_state_hits": float(np.mean([r["persistent_state_hits"] for r in rows])), "rows": rows}


def sham(pm, env, eps, f, tag):
    n = len(pm["genome"]) // A.IW
    msk = mask(n, f, (tag, "sham", f, 1))
    child = json.loads(json.dumps(pm))            # drawn, not applied
    pev = A.eval_all(pm, {env: eps})
    cev = A.eval_all(child, {env: eps})
    return {"n_hit_drawn": sum(msk), "disp": A.C1.displacement(cev[env]["_answers"], pev[env]["_answers"]), "reward_equal": cev[env]["reward_per_ask"] == pev[env]["reward_per_ask"]}
