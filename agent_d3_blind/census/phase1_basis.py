"""Phase 1 driver for one basis: census -> graph -> targets -> witnesses -> M0.

Run: python census/phase1_basis.py --basis S1 [--scale 1.0]

--scale is a *smoke-test only* knob used to verify the code runs end to end on a
throwaway copy.  The recorded Phase 1 run uses scale 1.0 and the preregistered
constants; the scale used is written into the ledger.
"""
import argparse
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from substrates import common, registry            # noqa: E402
from probes import battery                          # noqa: E402
from mutation import mutators                       # noqa: E402
from classifiers import families                    # noqa: E402
from m0 import harness, baselines                   # noqa: E402
from reachability import witnesses                  # noqa: E402

G = json.load(open(os.path.join(ROOT, "prereg", "gates.json")))
C = G["constants"]
VP = battery.VALUE_PROBES
LP = battery.LIVENESS_PROBES
EXTP = battery.EXT_PROBES


def build_order(basis, order):
    perms = registry.set_order(basis, order)
    sub = registry.get(basis)
    rng = random.Random(C["SEED_RNG"] + 31 * order)
    seeds, tries = [], 0
    while len(seeds) < C["N_SEEDS"] and tries < C["SEED_TRIES"]:
        tries += 1
        p = sub.random_program(rng, rng.randrange(4, 16))
        if not sub.is_valid(p):
            continue
        if common.sem_profile(sub, p, VP)["live"] and p not in seeds:
            seeds.append(p)
    aprobes, atries = battery.make_artifact_probes(sub, common)
    donors = mutators.make_donors(sub)
    return sub, seeds, aprobes, donors, perms, tries, atries


def radius_census(basis, sub, seeds, aprobes, donors, order, nmut, rows_out):
    rng = random.Random(777000 + 13 * order + 7 * ord(basis[1]))
    agg = {r: {"n": 0, "valid": 0, "semdiff": 0, "identity": 0, "destructive": 0,
               "live_consumer": 0, "nontrivial": 0} for r in C["RADII"]}
    fam = {}
    fam_all = {}
    opfam = {}
    classes = set()
    structs = set()
    outs_art = set()
    seedprof = [common.sem_profile(sub, s, VP) for s in seeds]
    for si, s in enumerate(seeds):
        pfp = seedprof[si]["fp"]
        for r in C["RADII"]:
            for _ in range(nmut):
                cand, kinds = mutators.mutate(basis, sub, s, rng, r, donors)
                a = agg[r]
                a["n"] += 1
                valid = sub.is_valid(cand)
                fmly = families.classify(s, cand)
                fam_all[fmly] = fam_all.get(fmly, 0) + 1
                row = {"basis": basis, "order": order, "seed": si, "r": r,
                       "valid": int(valid), "family": fmly,
                       "size": len(cand), "cand_h": common.h16(cand)}
                if not valid:
                    row["sem_fp"] = "INVALID"
                    row["destructive"] = 1
                    a["destructive"] += 1
                    rows_out.append(row)
                    continue
                a["valid"] += 1
                if cand != s:
                    outs_art.add(cand)
                pr = common.sem_profile(sub, cand, VP)
                sp = common.struct_profile(sub, cand, aprobes, LP)
                classes.add(pr["fp"])
                structs.add(sp["fp"])
                ident = (pr["fp"] == pfp)
                dest = not pr["live"]
                if not ident:
                    a["semdiff"] += 1
                    fam[fmly] = fam.get(fmly, 0) + 1
                    of = families.op_family(basis, sub, s, cand)
                    opfam[of] = opfam.get(of, 0) + 1
                if ident:
                    a["identity"] += 1
                if dest:
                    a["destructive"] += 1
                if (not ident) and (not dest):
                    a["nontrivial"] += 1
                if sp["live_consumer"]:
                    a["live_consumer"] += 1
                row.update({"sem_fp": pr["fp"], "struct_fp": sp["fp"],
                            "identity": int(ident), "destructive": int(dest),
                            "live_consumer": int(sp["live_consumer"]),
                            "nvalid_out": sp["n_valid_out"]})
                rows_out.append(row)
    return {"agg": {str(k): v for k, v in agg.items()}, "fam_semdiff": fam,
            "fam_all": fam_all, "opfam": opfam,
            "n_classes": len(classes), "n_structs": len(structs),
            "n_distinct_out_artifacts": len(outs_art),
            "classes": classes, "structs": structs}


def chain_census(basis, sub, seeds, aprobes, donors):
    rng = random.Random(31337 + ord(basis[1]))
    edges = set()
    first_depth = {}
    classes = set()
    steps_valid = 0
    steps_total = 0
    reps = {}
    for si, s in enumerate(seeds):
        p0 = common.sem_profile(sub, s, VP)
        first_depth.setdefault(p0["fp"], 0)
        reps.setdefault(p0["fp"], s)
        classes.add(p0["fp"])
        for _w in range(C["CHAIN_WALKS"]):
            cur, curfp = s, p0["fp"]
            for step in range(1, C["CHAIN_STEPS"] + 1):
                steps_total += 1
                cand, _k = mutators.mutate(basis, sub, cur, rng, 1, donors)
                if not sub.is_valid(cand):
                    continue
                steps_valid += 1
                pr = common.sem_profile(sub, cand, VP)
                classes.add(pr["fp"])
                if pr["fp"] not in first_depth or first_depth[pr["fp"]] > step:
                    first_depth[pr["fp"]] = step
                    reps[pr["fp"]] = cand
                if pr["fp"] != curfp:
                    edges.add((curfp, pr["fp"]))
                cur, curfp = cand, pr["fp"]
    return {"edges": edges, "first_depth": first_depth, "classes": classes,
            "reps": reps, "steps_valid": steps_valid, "steps_total": steps_total}


def giant_component(edges):
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    for a, b in edges:
        union(a, b)
    if not parent:
        return 0.0, 0, 0
    sizes = {}
    for x in parent:
        r = find(x)
        sizes[r] = sizes.get(r, 0) + 1
    n = len(parent)
    return max(sizes.values()) / n, max(sizes.values()), n


def probe_stability(basis, sub, seeds, donors, nsub):
    rng = random.Random(9091 + ord(basis[1]))
    allp = VP + EXTP
    outs = []
    n = 0
    while n < nsub:
        s = seeds[rng.randrange(len(seeds))]
        cand, _k = mutators.mutate(basis, sub, s, rng,
                                   rng.choice(C["RADII"]), donors)
        if not sub.is_valid(cand):
            continue
        o = []
        for x in allp:
            y, st = sub.run(cand, x)
            o.append(y if st == "ok" else st)
        outs.append(o)
        n += 1
    res = {}
    for k in (4, 8, 12, 16):
        res[k] = len({common.h16(o[:k]) for o in outs})
    delta = abs(res[16] - res[12]) / max(1, res[12])
    return {"counts": res, "rel_delta_12_16": delta,
            "stable": delta <= C["PROBE_STABILITY_TOL"], "n": n}


def fresh_pool(basis, sub, n):
    rng = random.Random(20261 + ord(basis[1]))
    ws = [(s, 2.0 ** (-s / 8.0)) for s in range(1, 33)]
    tot = sum(w for _s, w in ws)
    cum, acc = [], 0.0
    for s, w in ws:
        acc += w / tot
        cum.append((acc, s))

    def pick():
        r = rng.random()
        for a, s in cum:
            if r <= a:
                return s
        return 32
    reps, live = {}, 0
    for _ in range(n):
        p = sub.random_program(rng, pick())
        if not sub.is_valid(p):
            continue
        pr = common.sem_profile(sub, p, VP)
        if pr["live"]:
            live += 1
        reps.setdefault(pr["fp"], p)
    return reps, live


def build_targets(chain, fresh_reps):
    rng = random.Random(C["TARGET_RNG"])
    depth = dict(chain["first_depth"])
    pool = {}
    for fp, d in depth.items():
        if d == 0:
            continue
        pool[fp] = d
    for fp in fresh_reps:
        if fp not in pool:
            pool[fp] = 99
    near = sorted([f for f, d in pool.items() if d <= 2])
    mid = sorted([f for f, d in pool.items() if 3 <= d <= 5])
    far = sorted([f for f, d in pool.items() if d >= 6])
    out = []
    for name, lst in (("near", near), ("mid", mid), ("far", far)):
        rng.shuffle(lst)
        for fp in lst[:C["N_TARGETS_PER_STRATUM"]]:
            out.append({"fp": fp, "stratum": name, "depth": pool[fp]})
    return out, {"near": len(near), "mid": len(mid), "far": len(far)}


def witness_search(basis, sub, aprobes, donors, budget, name):
    rng = random.Random(60600 + ord(basis[1]) + sum(ord(c) for c in name))
    start = common.meter()
    best, bestp = -1.0, None
    cur, curf = None, -1.0
    self_fp = {a: common.sem_profile(sub, a, VP)["fp"] for a in aprobes} \
        if name == "W4_UNIVERSAL" else {}
    target = float(len(VP)) if name != "W4_UNIVERSAL" else float(len(aprobes))
    steps, restarts = 0, 0
    while common.meter() - start < budget:
        if cur is None or steps % 400 == 0:
            for _ in range(40):
                cand = sub.random_program(rng, rng.randrange(3, 20))
                if sub.is_valid(cand):
                    break
            cur, curf = cand, -1.0
            restarts += 1
        child, _k = mutators.mutate(basis, sub, cur, rng, rng.choice([1, 1, 2, 3]), donors)
        steps += 1
        if not sub.is_valid(child):
            continue
        if name == "W4_UNIVERSAL":
            f = witnesses.w4_fitness(sub, common, child, aprobes, self_fp)
        else:
            pr = common.sem_profile(sub, child, VP)
            f = witnesses.value_fitness(name, pr["outs"])
        if f >= curf:
            cur, curf = child, f
        if f > best:
            best, bestp = f, child
        if best >= target:
            break
    return {"witness": name, "best_fitness": best, "target": target,
            "constructed": bool(best >= target),
            "cost_runs": common.meter() - start, "steps": steps,
            "restarts": restarts,
            "prog": list(bestp) if bestp is not None else None,
            "prog_size": len(bestp) if bestp is not None else None}


def run_m0(basis, sub, seeds, donors, budget, targets, witness_fps, aprobes):
    tgt_by_fp = {t["fp"]: t for t in targets}
    out = {}
    for vi, v in enumerate(baselines.VARIANTS):
        ctx = harness.Ctx(basis, sub, seeds, donors, budget,
                          rng_seed=880000 + 97 * vi + ord(basis[1]))
        t0 = time.time()
        meta = baselines.RUNNERS[v](ctx)
        hits = {"near": 0, "mid": 0, "far": 0}
        hit_costs = []
        for fp, (prog, cost) in ctx.found.items():
            t = tgt_by_fp.get(fp)
            if t:
                hits[t["stratum"]] += 1
                hit_costs.append(cost)
        wreach = [w for w, fp in witness_fps.items() if fp and fp in ctx.found]
        # W4 is a structural witness: audited on the harness side, outside the
        # M0 budget, over the representatives M0 actually emitted.
        w4 = False
        selffp = {a: common.sem_profile(sub, a, VP)["fp"] for a in aprobes}
        for fp, (prog, cost) in list(ctx.found.items())[:4000]:
            if witnesses.w4_fitness(sub, common, prog, aprobes, selffp) >= len(aprobes):
                w4 = True
                break
        if w4:
            wreach.append("W4_UNIVERSAL")
        n_t = len(targets)
        out[v] = {"meta": meta, "spent": ctx.spent(), "budget": budget,
                  "n_eval": ctx.calls, "n_valid": ctx.n_valid,
                  "n_classes": len(ctx.found), "hits": hits,
                  "coverage": sum(hits.values()) / max(1, n_t),
                  "far_coverage": hits["far"] / max(1, sum(
                      1 for t in targets if t["stratum"] == "far")),
                  "median_hit_cost": sorted(hit_costs)[len(hit_costs) // 2] if hit_costs else None,
                  "witnesses_reached": wreach,
                  "trace": ctx.trace[-40:], "secs": round(time.time() - t0, 1)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--basis", required=True)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    b = a.basis
    sc = a.scale
    t_start = time.time()
    led = {"basis": b, "scale": sc, "prereg_version": G["prereg_version"],
           "probe_hash": battery.probe_hash(VP),
           "ext_probe_hash": battery.probe_hash(EXTP), "orders": {}}
    rows = []
    per_order = {}
    order0 = None
    for order in C["ORDERS"]:
        sub, seeds, aprobes, donors, perms, tries, atries = build_order(b, order)
        nmut = int((C["N_MUT_ORDER0"] if order == 0 else C["N_MUT_OTHER_ORDERS"]) * sc)
        nmut = max(2, nmut)
        rc = radius_census(b, sub, seeds, aprobes, donors, order, nmut, rows)
        o = {"n_seeds": len(seeds), "seed_tries": tries,
             "artifact_probe_tries": atries,
             "n_artifact_probes": len(aprobes),
             "min_seed_size": min((len(s) for s in seeds), default=None),
             "agg": rc["agg"], "fam_semdiff": rc["fam_semdiff"],
             "fam_all": rc["fam_all"], "opfam": rc["opfam"],
             "n_classes_radius": rc["n_classes"],
             "n_structs_radius": rc["n_structs"],
             "n_distinct_out_artifacts": rc["n_distinct_out_artifacts"],
             "seeds": [list(s) for s in seeds],
             "artifact_probes": [list(p) for p in aprobes]}
        per_order[order] = o
        led["orders"][str(order)] = o
        if order == 0:
            order0 = (sub, seeds, aprobes, donors, rc)
    # ---- order-0 deep pass ----
    sub, seeds, aprobes, donors, rc = order0
    registry.set_order(b, 0)
    ch = chain_census(b, sub, seeds, aprobes, donors)
    allclasses = set(rc["classes"]) | set(ch["classes"])
    edges = set(ch["edges"])
    # radius-1 edges from the radius census
    seedfps = [common.sem_profile(sub, s, VP)["fp"] for s in seeds]
    for r in rows:
        if r["order"] == 0 and r["r"] == 1 and r.get("sem_fp", "INVALID") != "INVALID":
            sf = seedfps[r["seed"]]
            if sf != r["sem_fp"]:
                edges.add((sf, r["sem_fp"]))
    gc_frac, gc_size, gc_n = giant_component(edges)
    stab = probe_stability(b, sub, seeds, donors, int(C["PROBE_STABILITY_SUBSAMPLE"] * sc))
    freps, fresh_live = fresh_pool(b, sub, int(C["FRESH_SAMPLE_N"] * sc))
    targets, pool_sizes = build_targets(ch, freps)
    wit = []
    wbud = int(C["WITNESS_BUDGET_RUNS"] * sc)
    for wn in witnesses.NAMES:
        wit.append(witness_search(b, sub, aprobes, donors, wbud, wn))
    wfps = {n: (witnesses.oracle_fp(n) if n in witnesses.ORACLES else None)
            for n in witnesses.NAMES}
    m0 = run_m0(b, sub, seeds, donors, int(C["M0_BUDGET_RUNS"] * sc),
                targets, wfps, aprobes)

    led["order0"] = {
        "n_semantic_classes_total": len(allclasses),
        "n_classes_chain": len(ch["classes"]),
        "chain_steps_valid": ch["steps_valid"], "chain_steps_total": ch["steps_total"],
        "giant_component_frac": gc_frac, "giant_component_size": gc_size,
        "graph_nodes": gc_n, "graph_edges": len(edges),
        "probe_stability": stab,
        "fresh_pool_classes": len(freps), "fresh_pool_live": fresh_live,
        "target_pool_sizes": pool_sizes,
        "targets": targets,
        "witnesses": wit, "witness_fps": wfps,
        "m0": m0,
    }
    with open(os.path.join(ROOT, "ledgers", "graph_%s.json" % b), "w") as f:
        json.dump({"basis": b, "nodes": sorted({x for e in edges for x in e}),
                   "edges": sorted(edges),
                   "first_depth": ch["first_depth"],
                   "giant_component_frac": gc_frac,
                   "giant_component_size": gc_size}, f)
    led["secs"] = round(time.time() - t_start, 1)
    led["total_meter_runs"] = common.meter()
    out = a.out or os.path.join(ROOT, "ledgers", "basis_%s.json" % b)
    with open(out, "w") as f:
        json.dump(led, f, indent=1, default=str)
    with open(os.path.join(ROOT, "ledgers", "census_rows_%s.jsonl" % b), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print("[%s] done in %ss, meter=%d, classes=%d, gc=%.3f" %
          (b, led["secs"], common.meter(), len(allclasses), gc_frac))


if __name__ == "__main__":
    main()
