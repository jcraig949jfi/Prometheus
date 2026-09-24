"""P-E06 (T-E06; co-parents T-X14, T-X04, T-X01, T-E07): ONE COUPLED ECOLOGY.

Recombination rate {.5,.6,.7,.8,.9,1.0} x seeded TREE frequency {.1,.5,.9} x damage {none, sham,
tape, tree, both} (f = .1 of body units per generation, blind) x 3 attempt ids, 160 generations,
tournament 3. Damage draws come from a SEPARATE rng keyed (attempt, generation) so the sham is
draw-matched by construction; none == sham on every trajectory is a fail-closed harness check
(CW01-D076). Full trajectories are kept (runs.json). Read as a coupled system: direction map of
final TREE over (rate, f0) per regime, the crossing rate per f0, coexistence at 80 and 160,
extinction generation, body-size response, lineage collapse.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402

W6 = L.import_world("cw01-e06", "world_e06")
PID, TID, F = "P-E06", "T-E06", 0.1
RATES, F0S, DAMAGE, IDS, GENS = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0), (0.1, 0.5, 0.9), ("none", "sham", "tape", "tree", "both"), ["cw01-loop3-PE06-%d" % i for i in range(3)], 160
MODE = {"arm": "none", "aid": None, "gen": 0}
_orig_gen = W6.generation


def contract_tree(node, target, counter):
    if node[0] == "in":
        return node
    if counter[0] == target:
        counter[0] += 1
        return node[1]
    counter[0] += 1
    return (node[0], contract_tree(node[1], target, counter), contract_tree(node[2], target, counter))


def damage_pop(pop, r, arm):
    """Draws are made for EVERY body in every damaging arm (sham included); application depends on the arm."""
    out = []
    for g in pop:
        h = dict(g)
        if g["substrate"] == "TAPE":
            prog = list(g["body"])
            k = int(round(F * len(prog)))
            picks = r.choice(len(prog), size=min(k, max(0, len(prog) - 1)), replace=False) if len(prog) > 1 else []
            if arm in ("tape", "both") and len(picks):
                h["body"] = [ins for i, ins in enumerate(prog) if i not in set(int(x) for x in picks)]
        else:
            n_int = W6.tree_nodes(g["body"]) - (W6.tree_nodes(g["body"]) + 1) // 2
            k = int(round(F * max(n_int, 0)))
            picks = r.choice(max(n_int, 1), size=min(k, max(n_int, 0)), replace=False) if n_int > 0 else []
            if arm in ("tree", "both"):
                body = g["body"]
                for t in sorted((int(x) for x in picks), reverse=True):
                    body = contract_tree(body, t, [0])
                h["body"] = body
        out.append(h)
    return out


def generation_w(pop, cfg, items, cross_ok, r, elite_frac):
    if MODE["arm"] != "none":
        drng = np.random.Generator(np.random.PCG64(S.seed(MODE["aid"], "damage|%d" % MODE["gen"], 0)))
        pop = damage_pop(pop, drng, MODE["arm"])
    MODE["gen"] += 1
    return _orig_gen(pop, cfg, items, cross_ok, r, elite_frac)


W6.generation = generation_w
KEEP = ("freq_TREE", "structural_units_TREE", "structural_units_TAPE", "live_registers_TAPE", "lineages_TREE", "lineages_TAPE", "score_TREE", "score_TAPE", "recomb_yield_TREE", "recomb_yield_TAPE")


def job(j):
    aid, rate, f0, arm = j["aid"], j["rate"], j["f0"], j["arm"]
    MODE.update({"arm": arm, "aid": aid, "gen": 0})
    cfg = L.load_cfg("cw01-e06", aid)
    cfg["ecology"]["recombination_rate"] = rate
    targets = [t for t in W6.attempt_target(cfg, S.seed) if t.get("graph") is not None]
    # the evolution stream is keyed WITHOUT the damage arm, so none/sham/tape/tree/both share every draw
    run = W6.evolve(cfg, "mixed_assortative", GENS, 96, S.seed, "%s|r%.1f|f%.1f" % (aid, rate, f0), freq_first=f0, target=targets)
    h = run["history"]
    return {"aid": aid, "rate": rate, "f0": f0, "arm": arm, "traj": {k: [round(float(x.get(k, 0.0)), 5) for x in h] for k in KEEP},
            "final80": h[79]["freq_TREE"], "final160": h[-1]["freq_TREE"], "coexist80": all(h[79].get("freq_" + lab, 0) > 0.05 for lab in run["labels"]), "coexist160": W6.coexisting(run),
            "extinct": run["extinction_generation"], "units_TREE": h[-1].get("structural_units_TREE"), "units_TAPE": h[-1].get("structural_units_TAPE"), "lineage_survival": run["lineage_survival"]}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    hh = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (float(c - hh), float(c + hh))


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-X14", "T-X04", "T-X01", "T-E07"], "claim_type": "integrated-factorial",
                         "factors": {"rate": RATES, "f0": F0S, "damage": DAMAGE, "attempt_ids": IDS, "generations": GENS, "f": F, "tournament": 3, "n_org": 96},
                         "unchanged": "e06 world, sharing, prices, item streams, mutation, graph targets",
                         "harness_check": "none == sham on every freq_TREE trajectory (separate damage rng); a violation voids the run as INVALID",
                         "readouts": ["direction map sign(final160 - f0) per (rate, f0, regime)", "crossing rate per f0 per regime: first consecutive-rate sign change of mean(final160 - f0)", "coexistence at 80 and 160 (counts of 3, Wilson)", "extinction generation", "final units by label", "lineage collapse (generation when lineages_TREE + lineages_TAPE <= 2)"],
                         "material_rule": "any of: a sign change across rate at f0 .1 or .9 in the 'none' regime; a damage regime moves a crossing by >= .2 in rate; coexistence-at-160 totals differ between regimes with disjoint Wilson bands; a regime has >= 3 cells with 2/3 or 3/3 coexistence at 160",
                         "continuation": ["target geometry x rate", "damage dose f", "240 generations at the crossing", "tournament 2"]})
    jobs = [{"aid": a, "rate": r, "f0": f, "arm": d} for a in IDS for r in RATES for f in F0S for d in DAMAGE]
    with ProcessPoolExecutor(max_workers=8) as ex:
        rows = list(ex.map(job, jobs, chunksize=4))
    by = {(r["aid"], r["rate"], r["f0"], r["arm"]): r for r in rows}
    sham_ok = all(by[(a, r, f, "none")]["traj"]["freq_TREE"] == by[(a, r, f, "sham")]["traj"]["freq_TREE"] for a in IDS for r in RATES for f in F0S)
    regimes = {}
    for d in DAMAGE:
        cells = {}
        for r in RATES:
            for f in F0S:
                rs = [by[(a, r, f, d)] for a in IDS]
                cells["%.1f|%.1f" % (r, f)] = {"final160": float(np.mean([x["final160"] for x in rs])), "final80": float(np.mean([x["final80"] for x in rs])),
                                                "direction": int(np.sign(np.mean([x["final160"] for x in rs]) - f)), "coexist80": sum(x["coexist80"] for x in rs), "coexist160": sum(x["coexist160"] for x in rs),
                                                "extinct_TREE": [x["extinct"].get("TREE") for x in rs], "extinct_TAPE": [x["extinct"].get("TAPE") for x in rs],
                                                "units_TREE": float(np.mean([x["units_TREE"] or 0 for x in rs])), "units_TAPE": float(np.mean([x["units_TAPE"] or 0 for x in rs])),
                                                "per_id_final160": [round(x["final160"], 3) for x in rs]}
        crossing = {}
        for f in F0S:
            signs = [cells["%.1f|%.1f" % (r, f)]["direction"] for r in RATES]
            cr = [(RATES[i], RATES[i + 1]) for i in range(len(RATES) - 1) if signs[i] != signs[i + 1] and signs[i] != 0 and signs[i + 1] != 0]
            crossing["%.1f" % f] = {"signs": signs, "first_crossing": cr[0] if cr else None, "n_crossings": len(cr)}
        co160 = sum(c["coexist160"] for c in cells.values())
        n_cells = len(cells) * len(IDS)
        regimes[d] = {"cells": cells, "crossing": crossing, "coexist160_total": co160, "coexist160_wilson": wilson(co160, n_cells), "coexist80_total": sum(c["coexist80"] for c in cells.values()),
                      "cells_with_majority_coexistence": sum(1 for c in cells.values() if c["coexist160"] >= 2), "mean_final160": float(np.mean([c["final160"] for c in cells.values()]))}
    # lineage collapse
    collapse = {}
    for d in DAMAGE:
        g = []
        for r in rows:
            if r["arm"] != d:
                continue
            tot = [a + b for a, b in zip(r["traj"]["lineages_TREE"], r["traj"]["lineages_TAPE"])]
            gg = next((i for i, v in enumerate(tot) if v <= 2), None)
            g.append(gg if gg is not None else GENS)
        collapse[d] = float(np.mean(g))
    none_sign_change = any(regimes["none"]["crossing"][k]["n_crossings"] > 0 for k in ("0.1", "0.9"))

    def cr_val(d, f):
        c = regimes[d]["crossing"][f]["first_crossing"]
        return None if c is None else 0.5 * (c[0] + c[1])
    moved = any(cr_val("none", f) is not None and cr_val(d, f) is not None and abs(cr_val("none", f) - cr_val(d, f)) >= 0.2 for d in ("tape", "tree", "both") for f in ("0.1", "0.5", "0.9"))
    moved = moved or any((cr_val("none", f) is None) != (cr_val(d, f) is None) for d in ("tape", "tree", "both") for f in ("0.1", "0.5", "0.9"))
    disjoint = any(regimes[a]["coexist160_wilson"][1] < regimes[b]["coexist160_wilson"][0] or regimes[b]["coexist160_wilson"][1] < regimes[a]["coexist160_wilson"][0] for a in DAMAGE for b in DAMAGE if a < b)
    region = any(regimes[d]["cells_with_majority_coexistence"] >= 3 for d in DAMAGE)
    material = bool(sham_ok and (none_sign_change or moved or disjoint or region))
    out = {"perturbation_id": PID, "parent": TID, "harness_none_equals_sham": sham_ok, "disposition": "RAN" if sham_ok else "INVALID_HARNESS", "regimes": regimes, "lineage_collapse_gen": collapse,
           "flags": {"none_sign_change_across_rate": none_sign_change, "damage_moves_crossing": moved, "coexistence_bands_disjoint": disjoint, "coexistence_region": region},
           "n_runs": len(rows), "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "runs.json").write_text(json.dumps(rows, ensure_ascii=True, default=L.js), encoding="utf-8")
    L.append_evidence(TID, PID, "coupled ecology (none==sham %s): direction signs by f0 %s; crossings %s; coexist160 totals %s; majority-coexistence cells %s; mean final TREE %s; lineage collapse gen %s; flags %s"
                      % (sham_ok, {d: {f: regimes[d]["crossing"][f]["signs"] for f in ("0.1", "0.5", "0.9")} for d in ("none", "tape", "tree", "both")},
                         {d: {f: regimes[d]["crossing"][f]["first_crossing"] for f in ("0.1", "0.5", "0.9")} for d in DAMAGE if d != "sham"},
                         {d: regimes[d]["coexist160_total"] for d in DAMAGE}, {d: regimes[d]["cells_with_majority_coexistence"] for d in DAMAGE}, {d: round(regimes[d]["mean_final160"], 3) for d in DAMAGE},
                         {d: round(v, 1) for d, v in collapse.items()}, out["flags"]), material, detail={"flags": out["flags"], "coexist": {d: regimes[d]["coexist160_total"] for d in DAMAGE}, "crossing": {d: regimes[d]["crossing"] for d in DAMAGE}})
    for tid in ("T-X14", "T-X04", "T-X01"):
        L.append_evidence(tid, PID, "cross (see T-E06): crossings %s; lineage collapse %s" % ({d: regimes[d]["crossing"]["0.1"]["first_crossing"] for d in ("none", "both")}, {d: round(v, 1) for d, v in collapse.items()}), material)
    print("DONE material=%s sham_ok=%s (%.0f s) flags %s | coexist160 %s" % (material, sham_ok, time.time() - t0, out["flags"], {d: regimes[d]["coexist160_total"] for d in DAMAGE}))


if __name__ == "__main__":
    main()
