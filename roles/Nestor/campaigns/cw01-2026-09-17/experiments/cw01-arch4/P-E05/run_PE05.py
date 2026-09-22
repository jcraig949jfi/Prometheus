"""P-E05 [deformation C x A; T-ARCH4/S1 stasis escape]: DEPTH 64 under the no-growth rule, and the
damage surface of what each rule produces.

Cells: rule {orig, no_growth} x proposals {frozen, delheavy}, trap-NOP; 2 walkers x viable parents;
depth 64 archived at 16/32/64. Per archived depth: exaptation (D6 rule on the other environments),
length delta, structural diversity, connected share. P-D01 damage cells (delete k=4 at 1 and 4
sites, operand k=4; modulo; 4 draws) on the depth-16 and depth-64 finals. Computational scope:
integer programs on a bounded VM.
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
sys.path.insert(0, str(HERE.parent / "P-D03"))
sys.path.insert(0, str(HERE.parent / "P-D01"))
from run_PD03 import weights     # noqa: E402
from run_PD01 import damage, windows, reduced_class   # noqa: E402

PID, TID = "P-E05", "T-ARCH4/S1"
RULES, PROPS, TRAP = ("orig", "no_growth"), ("frozen", "delheavy"), "nop"
DEPTH, ARCH, WALKERS, MAXP = 64, (16, 32, 64), 2, 32
BAND = A.C1.BAND
CELLS = [("delete", 4, 1), ("delete", 4, 4), ("operand", 4, 1)]


def walk(parent, org, w, env_eps, rule, prop):
    names, cum = weights(prop)
    rng = A.SplitMix64(A.seed_from("c4.05.walk", A.CAMPAIGN_SEED, org, "walk", w))
    r0 = A.evaluate(parent, env_eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
    cur = json.loads(json.dumps(parent))
    d, steps, props_total, archived = 0, [], 0, {}
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
            child, _ = A.trap(child, TRAP)
            tries += 1
            r = A.evaluate(child, env_eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
            ok = abs(r - r0) <= BAND and (rule == "orig" or CM.n_instr(child) <= CM.n_instr(cur))
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
        if d in ARCH:
            archived[d] = json.loads(json.dumps(cur))
    return {"depth": d, "proposals": props_total, "ops": steps, "archived": archived, "final": cur}


def assay(pm, env, eps, tag):
    pev = A.eval_all(pm, {env: eps[env]})
    n = CM.n_instr(pm)
    rows = []
    for kind, k, s in CELLS:
        if k >= n:
            continue
        for dr in range(1, 5):
            rng = A.SplitMix64(A.seed_from("nestor.pe05.assay", A.LOOP_SEED, tag, kind, k, s, dr))
            child = damage(pm, kind, windows(n, k, s, "even", rng), rng, "modulo")
            cev = A.eval_all(child, {env: eps[env]})
            disp = A.C1.displacement(cev[env]["_answers"], pev[env]["_answers"])
            rows.append(int(reduced_class(cev, pev, disp, env) in ("D2", "D3")))
    return float(np.mean(rows)) if rows else None


def job(j):
    p, rule, prop = j["parent"], j["rule"], j["prop"]
    env = p["env"]
    eps = {k: A.episodes(k) for k in A.ENVS}
    pm = A.canonical(p["manifest"])
    pev = A.eval_all(pm, eps)
    others = [o for o in A.OTHER_ENVS if o != env]
    len0 = CM.n_instr(pm)
    out = []
    for w in range(1, WALKERS + 1):
        wk = walk(pm, p["organism_id"], w, eps[env], rule, prop)
        per_depth = {}
        for dd in ARCH:
            m = wk["archived"].get(dd)
            if m is None:
                continue
            fev = A.eval_all(m, eps)
            ex = [o for o in others if fev[o]["reward_per_ask"] >= pev[o]["reward_per_ask"] + BAND and fev[o]["reward_per_ask"] >= A.C1.FLOOR]
            per_depth[dd] = {"exaptive": bool(ex), "len_delta": CM.n_instr(m) - len0, "manifest": m,
                             "loss": assay(m, env, eps, "%s-%s-%s-%d-%d" % (p["organism_id"], rule, prop, w, dd)) if dd in (16, 64) else None}
        out.append({"walker": w, "depth": wk["depth"], "acceptance": wk["depth"] / wk["proposals"] if wk["proposals"] else None, "ops": Counter(wk["ops"]), "per_depth": per_depth})
    return {"pid": p["organism_id"], "rule": rule, "prop": prop, "walkers": out}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (float(c - h), float(c + h))


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "C", "escapes_stasis": "S1 froze depth because deeper walks under the original rule only accumulate length; P-D03 removed the accumulation under no_growth; depth is re-posed under that rule",
                         "scope": CM.SCOPE, "claim_type": "stasis-escape-cross", "grid": {"rule": RULES, "prop": PROPS, "trap": TRAP}, "depth": DEPTH, "archive": ARCH, "walkers": WALKERS,
                         "measures": "per archived depth: exaptation (D6 rule), length delta, connected share, structural diversity; damage loss (delete k4 s1, delete k4 s4, operand k4; modulo; 4 draws) at depth 16 and 64",
                         "material_rule": "exaptation Wilson 95% bands at depth 64 vs 16 disjoint in any cell; OR paired sign-flip of loss(64) - loss(16) outside its band in any cell; OR paired sign-flip of loss under no_growth minus orig (same parent, walker, depth) outside its band",
                         "continuation": ["depth 128", "lencost rule", "band width x depth"], "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    jobs = [{"parent": p, "rule": r, "prop": q} for p in parents for r in RULES for q in PROPS]
    with A.pool(8) as ex:
        res = list(ex.map(job, jobs))
    table = {}
    for r in res:
        key = "%s|%s" % (r["rule"], r["prop"])
        c = table.setdefault(key, {dd: {"ex": [], "len": [], "loss": [], "mani": []} for dd in ARCH} | {"reached": [], "acc": []})
        for w in r["walkers"]:
            c["reached"].append(w["depth"])
            c["acc"].append(w["acceptance"] if w["acceptance"] is not None else np.nan)
            for dd, v in w["per_depth"].items():
                c[dd]["ex"].append(1.0 if v["exaptive"] else 0.0)
                c[dd]["len"].append(v["len_delta"])
                if v["loss"] is not None:
                    c[dd]["loss"].append(v["loss"])
                c[dd]["mani"].append(v["manifest"])
    summ = {}
    for key, c in table.items():
        summ[key] = {"n_walks": len(c["reached"]), "connected_64": float(np.mean([d == DEPTH for d in c["reached"]])), "depth_mean": float(np.mean(c["reached"])), "acceptance": float(np.nanmean(c["acc"]))}
        for dd in ARCH:
            n = len(c[dd]["ex"])
            summ[key][str(dd)] = {"n": n, "exaptation": float(np.mean(c[dd]["ex"])) if n else None, "wilson": wilson(int(sum(c[dd]["ex"])), n),
                                  "len_delta": float(np.mean(c[dd]["len"])) if n else None, "loss": float(np.mean(c[dd]["loss"])) if c[dd]["loss"] else None,
                                  "structural_diversity": CM.struct_div(c[dd]["mani"][:60]) if n >= 2 else None}
    # paired contrasts
    sf_depth, sf_rule = {}, {}
    for key in summ:
        pairs = []
        for r in res:
            if "%s|%s" % (r["rule"], r["prop"]) != key:
                continue
            for w in r["walkers"]:
                a, b = w["per_depth"].get(16), w["per_depth"].get(64)
                if a and b and a["loss"] is not None and b["loss"] is not None:
                    pairs.append(b["loss"] - a["loss"])
        sf_depth[key] = CM.paired_signflip(pairs)
    for prop in PROPS:
        for dd in (16, 64):
            byk = {}
            for r in res:
                if r["prop"] != prop:
                    continue
                for w in r["walkers"]:
                    v = w["per_depth"].get(dd)
                    if v and v["loss"] is not None:
                        byk.setdefault((r["pid"], w["walker"]), {})[r["rule"]] = v["loss"]
            sf_rule["%s|%d" % (prop, dd)] = CM.paired_signflip([v["no_growth"] - v["orig"] for v in byk.values() if "no_growth" in v and "orig" in v])
    disjoint = any(summ[k]["64"]["n"] and (summ[k]["64"]["wilson"][0] > summ[k]["16"]["wilson"][1] or summ[k]["64"]["wilson"][1] < summ[k]["16"]["wilson"][0]) for k in summ)
    material = bool(disjoint or any(v and (v["above_p95"] or v["below_p05"]) for v in list(sf_depth.values()) + list(sf_rule.values())))
    out = {"perturbation_id": PID, "parent": TID, "summary": summ, "loss_64_minus_16": sf_depth, "loss_no_growth_minus_orig": sf_rule, "exaptation_bands_disjoint": disjoint, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "depth 64 under rules: %s; loss(64)-loss(16) %s; loss no_growth-orig %s"
                      % ({k: {dd: (round(v[str(dd)]["exaptation"], 3) if v[str(dd)]["exaptation"] is not None else None, round(v[str(dd)]["len_delta"], 1) if v[str(dd)]["len_delta"] is not None else None, round(v[str(dd)]["loss"], 3) if v[str(dd)]["loss"] is not None else None) for dd in ARCH} | {"conn64": round(v["connected_64"], 2)} for k, v in summ.items()},
                         {k: (round(v["mean_diff"], 3), v["above_p95"], v["below_p05"]) if v else None for k, v in sf_depth.items()},
                         {k: (round(v["mean_diff"], 3), v["above_p95"], v["below_p05"]) if v else None for k, v in sf_rule.items()}),
                      material, detail={"summary": summ, "depth": sf_depth, "rule": sf_rule},
                      state="ACTIVE" if material else None, state_reason="the recorded escape (a different acceptance rule) made depth informative" if material else None)
    L.append_evidence("T-ARCH4/M1", PID, "cross A x C: damage loss of no_growth vs orig products %s" % {k: (round(v["mean_diff"], 3), v["above_p95"], v["below_p05"]) if v else None for k, v in sf_rule.items()}, material)
    print("DONE material=%s (%.0f s) %s" % (material, time.time() - t0, json.dumps({k: {dd: summ[k][str(dd)]["exaptation"] for dd in ARCH} for k in summ})))


if __name__ == "__main__":
    main()
