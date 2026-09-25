"""P-D03 [deformation C]: breaking the ACCEPTANCE-FILTER mechanism for length growth.

Parent T-ARCH4/M1. A Nestor walk (same band, proposals and archive as C4-05, acceptance made
pluggable) over a grid: acceptance rule in {orig: |r-r0| <= band; no_growth: orig AND len <=
len_prev; lennorm: |r-r0| <= band*len0/len; lencost: orig AND len <= len0+1; symdel: orig with a
deletion/splice proposal retried up to 4 times before it counts as a proposal} x trap semantics in
{modulo, nop, halt} x proposal distribution in {frozen, balanced (insert+dup mass = delete+splice
mass), delheavy (delete+splice mass x3)}; 2 walkers x viable parents x depth 16; per cell length
delta, acceptance, exaptation, structural diversity, and the share of accepted steps by operator
(does growth disappear, reverse, relocate to duplication/config, or become another accumulation?).
Computational scope: integer programs on a bounded VM.
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

PID, TID = "P-D03", "T-ARCH4/M1"
RULES, TRAPS, PROPS = ("orig", "no_growth", "lennorm", "lencost", "symdel"), ("modulo", "nop", "halt"), ("frozen", "balanced", "delheavy")
DEPTH, WALKERS, MAXP = 16, 2, 32
BAND = A.C1.BAND


def weights(kind):
    names, w = list(A.GR.NAMES), list(A.GR.WEIGHTS)
    if kind == "balanced":
        grow = sum(w[names.index(x)] for x in ("insertion", "duplication"))
        shrink = sum(w[names.index(x)] for x in ("deletion", "splice"))
        t = 0.5 * (grow + shrink)
        for x in ("insertion", "duplication"):
            w[names.index(x)] *= t / grow
        for x in ("deletion", "splice"):
            w[names.index(x)] *= t / shrink
    elif kind == "delheavy":
        for x in ("deletion", "splice"):
            w[names.index(x)] *= 3.0
    s = sum(w)
    return names, np.cumsum([v / s for v in w])


def walk(parent, org, w, env_eps, rule, trapmode, prop):
    names, cum = weights(prop)
    rng = A.SplitMix64(A.seed_from("c4.05.walk", A.CAMPAIGN_SEED, org, "walk", w))
    r0 = A.evaluate(parent, env_eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
    len0 = CM.n_instr(parent)
    cur = json.loads(json.dumps(parent))
    d, steps, props_total = 0, [], 0
    while d < DEPTH:
        accepted, tries = None, 0
        while tries < MAXP:
            name = None if prop == "frozen" else names[int(np.searchsorted(cum, (rng.next_u32() % 1_000_000) / 1_000_000.0))]
            try:
                child, rec = A.GR.mutate(cur, rng, mate=None, name=name)
            except A.ManifestError:
                tries += 1
                continue
            if "noop" in (rec.get("args") or {}):
                continue
            child, _ = A.trap(child, trapmode)
            tries += 1
            r = A.evaluate(child, env_eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
            ln, lp = CM.n_instr(child), CM.n_instr(cur)
            if rule == "orig":
                ok = abs(r - r0) <= BAND
            elif rule == "no_growth":
                ok = abs(r - r0) <= BAND and ln <= lp
            elif rule == "lennorm":
                ok = abs(r - r0) <= BAND * len0 / max(ln, 1)
            elif rule == "lencost":
                ok = abs(r - r0) <= BAND and ln <= len0 + 1
            else:                                                     # symdel
                ok = abs(r - r0) <= BAND
                if not ok and rec["operator"] in ("deletion", "splice"):
                    for _retry in range(3):
                        try:
                            c2, rec2 = A.GR.mutate(cur, rng, mate=None, name=rec["operator"])
                        except A.ManifestError:
                            continue
                        if "noop" in (rec2.get("args") or {}):
                            continue
                        c2, _ = A.trap(c2, trapmode)
                        r2 = A.evaluate(c2, env_eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
                        if abs(r2 - r0) <= BAND:
                            child, rec, r, ok = c2, rec2, r2, True
                            break
            if ok:
                accepted = (child, rec, r)
                break
        props_total += tries
        if accepted is None:
            break
        child, rec, r = accepted
        d += 1
        steps.append(rec["operator"])
        cur = child
    return {"depth": d, "proposals": props_total, "final": cur, "ops": steps, "len_delta": CM.n_instr(cur) - len0}


def job(j):
    p, rule, trapmode, prop = j["parent"], j["rule"], j["trap"], j["prop"]
    env = p["env"]
    eps = {k: A.episodes(k) for k in A.ENVS}
    pm = A.canonical(p["manifest"])
    pev = A.eval_all(pm, eps)
    others = [o for o in A.OTHER_ENVS if o != env]
    out = []
    for w in range(1, WALKERS + 1):
        wk = walk(pm, p["organism_id"], w, eps[env], rule, trapmode, prop)
        fev = A.eval_all(wk["final"], eps)
        ex = [o for o in others if fev[o]["reward_per_ask"] >= pev[o]["reward_per_ask"] + BAND and fev[o]["reward_per_ask"] >= A.C1.FLOOR]
        out.append({"walker": w, "depth": wk["depth"], "acceptance": wk["depth"] / wk["proposals"] if wk["proposals"] else None,
                    "len_delta": wk["len_delta"], "exaptive": bool(ex), "ops": wk["ops"], "manifest": wk["final"]})
    return {"pid": p["organism_id"], "rule": rule, "trap": trapmode, "prop": prop, "walkers": out}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "C", "scope": CM.SCOPE, "claim_type": "parameterized-mechanism-break",
                         "grid": {"rule": RULES, "trap": TRAPS, "prop": PROPS}, "depth": DEPTH, "walkers": WALKERS, "max_proposals": MAXP,
                         "held_fixed": "band width, seeds, parents' behaviour (canonicalised), environments",
                         "attacks": "P-C16's stated mechanism: growth = accepted NOP-trapped insertions + rejected live deletions",
                         "measures": "length delta, acceptance, exaptation, structural diversity, accepted-operator shares, per cell",
                         "continuation": ["band width", "depth 32/64 under the winning rule", "explicit per-instruction cost sweep", "C5 representation B"],
                         "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    jobs = [{"parent": p, "rule": r, "trap": t, "prop": q} for p in parents for r in RULES for t in TRAPS for q in PROPS]
    with A.pool(8) as ex:
        res = list(ex.map(job, jobs))
    cells = {}
    for r in res:
        key = (r["rule"], r["trap"], r["prop"])
        c = cells.setdefault(key, {"len": [], "acc": [], "ex": [], "depth": [], "ops": Counter(), "mani": []})
        for w in r["walkers"]:
            c["len"].append(w["len_delta"])
            c["acc"].append(w["acceptance"] if w["acceptance"] is not None else np.nan)
            c["ex"].append(1.0 if w["exaptive"] else 0.0)
            c["depth"].append(w["depth"])
            c["ops"].update(w["ops"])
            c["mani"].append(w["manifest"])
    table = []
    for (rule, tr, pr), c in cells.items():
        tot = sum(c["ops"].values()) or 1
        table.append({"rule": rule, "trap": tr, "prop": pr, "n": len(c["len"]), "len_delta": float(np.mean(c["len"])), "connected_16": float(np.mean([d == DEPTH for d in c["depth"]])),
                      "acceptance": float(np.nanmean(c["acc"])), "exaptation": float(np.mean(c["ex"])), "structural_diversity": CM.struct_div(c["mani"][:60]),
                      "op_share": {k: round(v / tot, 3) for k, v in c["ops"].most_common(6)}})
    base = next(x for x in table if (x["rule"], x["trap"], x["prop"]) == ("orig", "nop", "frozen"))
    by_rule = {r: float(np.mean([x["len_delta"] for x in table if x["rule"] == r and x["trap"] == "nop"])) for r in RULES}
    by_trap = {t: float(np.mean([x["len_delta"] for x in table if x["trap"] == t and x["rule"] == "orig"])) for t in TRAPS}
    by_prop = {q: float(np.mean([x["len_delta"] for x in table if x["prop"] == q and x["trap"] == "nop" and x["rule"] == "orig"])) for q in PROPS}
    growth_broken = [x for x in table if x["trap"] == "nop" and x["len_delta"] <= 0.25 * base["len_delta"]]
    material = bool(growth_broken)
    out = {"perturbation_id": PID, "parent": TID, "table": table, "baseline_orig_nop_frozen": base, "len_by_rule_under_nop": by_rule,
           "len_by_trap_under_orig": by_trap, "len_by_prop_under_orig_nop": by_prop,
           "cells_where_growth_breaks_under_nop": [(x["rule"], x["prop"], round(x["len_delta"], 2), round(x["exaptation"], 3), x["op_share"]) for x in growth_broken],
           "material": material, "n_parents": len(parents), "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "acceptance-filter grid: length by rule under trap-NOP %s; by trap %s; by proposal %s; growth breaks in %d/%d nop cells"
                      % ({k: round(v, 2) for k, v in by_rule.items()}, {k: round(v, 2) for k, v in by_trap.items()}, {k: round(v, 2) for k, v in by_prop.items()}, len(growth_broken), sum(1 for x in table if x["trap"] == "nop")),
                      material, detail={"by_rule": by_rule, "by_trap": by_trap, "by_prop": by_prop, "broken": out["cells_where_growth_breaks_under_nop"]})
    print("DONE material=%s (%.0f s) rule %s | trap %s | prop %s" % (material, time.time() - t0, {k: round(v, 2) for k, v in by_rule.items()}, {k: round(v, 2) for k, v in by_trap.items()}, {k: round(v, 2) for k, v in by_prop.items()}))


if __name__ == "__main__":
    main()
