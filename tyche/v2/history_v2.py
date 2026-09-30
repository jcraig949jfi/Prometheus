"""Causal natural history of every sense a v2 run produced (directive v2).

A slot is SOLVED when an admitted lens there is replicated (Pass D) and its
test gain reaches >= 50% of the oracle deficit at admission. For the best
such lens, answer (answer key used here only):

  first_carrier[i]    first ancestor whose outputs FUNCTIONALLY carry
                      hidden precursor i (MI above a permutation null on the
                      train split; soft / partial carriers count)
  zero_utility_gens   generations the carrier line existed while its home
                      val z < 2 (no significant home value)
  why_survived        for carrier-line members in those generations: how
                      they persisted -- elite, parent choice decided by a
                      SIGNIFICANT case (z >= 2) or by a NOISE-level case,
                      reserve (novelty / random / age_or_credit), drift
  valued_elsewhere    worlds other than home where a carrier had a
                      significant case
  arrivals            first-carrier generation per precursor
  gradient            home val gain along the best ancestral path
  transition          the parent -> child edge with the largest home-gain
                      jump: operator, gains, and the donor's valued worlds
  strict_survivable   fraction of path ancestors that ever held a
                      significant case (would survive STRICT gating)
  assembly            MUTATION | GRAFT | COMPOSE | COALITION | DRIFT, plus
                      EXAPTATION when the transition's donor/parent was
                      significantly valued on another world

Usage: python -m tyche.v2.history_v2 <run_dir> [--workers N]
"""

from __future__ import annotations

import argparse
import collections
import json
import os
from multiprocessing import Pool

import numpy as np

from . import eco_v2 as E2
from . import worlds_v2 as W2
from .run_v2 import world_set


def jl(p):
    return [json.loads(x) for x in open(p, encoding="ascii") if x.strip()] if os.path.exists(p) else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    cfg = json.load(open(os.path.join(a.run, "CONFIG.json")))
    _, known = world_set(cfg["args"]["worlds"])
    by = {s["id"]: s for s in known}
    gene = {}
    for r in jl(os.path.join(a.run, "GENEALOGY.jsonl")):
        gene.setdefault(r["id"], r)
    ev = collections.defaultdict(dict)   # id -> slot -> list of (epoch, phase, best (g, z))
    for r in jl(os.path.join(a.run, "EVALS.jsonl")):
        for slot, cs in r["cases"].items():
            g, z = max(cs.values(), key=lambda v: v[0])
            ev[r["id"]].setdefault(slot, []).append((r["epoch"], r["phase"], g, z))
    sel = jl(os.path.join(a.run, "SELECTION.jsonl"))
    pops = {r["gen"]: set(r["pop"]) | set(r["reserve"]) for r in jl(os.path.join(a.run, "POP.jsonl"))}
    defs = {(d["tag"], d["slot"]): d for d in jl(os.path.join(a.run, "DEFICITS.jsonl"))}
    rows = json.load(open(os.path.join(a.run, "PASS_D.json")))
    pool = Pool(a.workers, initializer=E2._init, initargs=(known,))

    def home_val(i, slot):
        v = ev.get(i, {}).get(slot, [])
        return (max(x[2] for x in v), max(x[3] for x in v)) if v else (None, None)

    def sig_elsewhere(i, slot):
        return sorted({s for s, v in ev.get(i, {}).items() if s != slot and any(x[2] > 0 and x[3] >= 2 for x in v)})

    def ever_sig(i):
        return any(x[2] > 0 and x[3] >= 2 for v in ev.get(i, {}).values() for x in v)

    out = []
    for r in rows:
        spec = by[r["spec"]]
        law = spec["law"]
        if law["comb"] == "prf" or spec.get("kind") == "tsd":
            continue
        tag = f"epoch{r['admission']['epoch']}_end"
        d0 = defs.get(("eco0", r["slot"]), {})
        best_def = max([v for k, v in d0.items() if k.endswith("deficit") and v is not None], default=None)
        if "@L2" in r["spec"]:
            sw = [v for (t, s), v in defs.items() if s == r["slot"] and t.startswith("switch")]
            best_def = max([v for k, v in sw[0].items() if k.endswith("deficit") and v is not None], default=None) if sw else best_def
        solved = r["replicated"] and best_def and r["home_test"][0] >= 0.5 * best_def
        if not solved:
            continue
        # ancestry DAG (fused members + parents)
        anc, stack = {}, [(r["id"], 0)]
        while stack:
            i, k = stack.pop()
            if i in anc or i not in gene:
                continue
            anc[i] = k
            stack += [(p, k + 1) for p in gene[i]["parents"]]
        ids = sorted(anc)
        _, carr = pool.apply(E2.task_carriers, ((r["spec"], law, [gene[i]["genome"] for i in ids]),))
        car = {i: c for i, c in zip(ids, carr)}
        k = len(law["prec"])
        first, arrivals = {}, {}
        for p in range(k):
            cs = [i for i in ids if car[i][p] > 0.005]
            if cs:
                f = min(cs, key=lambda i: (gene[i]["birth_gen"] if gene[i]["birth_gen"] >= 0 else 10 ** 6))
                first[p] = f
                arrivals[p] = gene[f]["birth_gen"]
        # carrier line: ancestors carrying precursor p; zero-utility persistence and why
        why = collections.Counter()
        zero_gens = {}
        slot = r["slot"]
        for p, f in first.items():
            line = [i for i in ids if car[i][p] > 0.005]
            gens = sorted(g for g, members in pops.items() if any(i in members for i in line))
            zg = [g for g in gens if all((home_val(i, slot)[1] or 0) < 2 for i in line if i in pops[g])]
            zero_gens[p] = len(zg)
            for s in sel:
                if s["gen"] not in zg:
                    continue
                for pe in s["parents"]:
                    if pe["p"] in line:
                        why["parent_significant" if pe["z"] >= 2 and pe["gain"] > 0 else "parent_noise_level"] += 1
                for e in s["elites"]:
                    if e[0] in line:
                        why["elite"] += 1
                for i, reason in s["reserve"].items():
                    if i in line:
                        why[f"reserve_{reason}"] += 1
                for i in line:
                    if i in pops.get(s["gen"], set()) and gene[i]["ops"][:1] == ["drift"]:
                        why["drift_born"] += 1
        # best ancestral path by home value, and the transition edge
        path, cur = [], r["id"]
        while cur in gene:
            hv = home_val(cur, slot)[0]
            path.append({"id": cur, "gen": gene[cur]["birth_gen"], "ops": gene[cur]["ops"], "home_gain": hv})
            ps = [p for p in gene[cur]["parents"] if p in gene]
            if not ps:
                break
            cur = max(ps, key=lambda p: (home_val(p, slot)[0] if home_val(p, slot)[0] is not None else -9))
        path = path[::-1]
        jumps = [(path[j + 1]["home_gain"] or 0) - (path[j]["home_gain"] or 0) for j in range(len(path) - 1)]
        trans = None
        if jumps:
            j = int(np.argmax(jumps))
            child = path[j + 1]["id"]
            donors = [p for p in gene[child]["parents"] if p != path[j]["id"]]
            trans = {"parent": path[j]["id"], "child": child, "ops": gene[child]["ops"], "jump": round(jumps[j], 4),
                     "parent_gain": path[j]["home_gain"], "child_gain": path[j + 1]["home_gain"],
                     "gen": gene[child]["birth_gen"],
                     "parent_valued_elsewhere": sig_elsewhere(path[j]["id"], slot),
                     "donors": [{"id": dd, "valued_elsewhere": sig_elsewhere(dd, slot)} for dd in donors]}
        op = (trans["ops"][0] if trans else (gene[r["id"]]["ops"][0]))
        mode = {"fuse": "COALITION", "graft": "GRAFT", "compose": "COMPOSE", "drift": "DRIFT",
                "immigrant": "IMMIGRANT", "init": "INITIAL"}.get(op, "MUTATION")
        if r["kind"] == "coalition":
            mode = "COALITION"
        exapt = bool(trans and (trans["parent_valued_elsewhere"] or any(dd["valued_elsewhere"] for dd in trans["donors"])))
        out.append({
            "slot": slot, "spec": r["spec"], "lens": r["id"], "kind": r["kind"], "test": r["home_test"][0],
            "oracle_deficit": best_def, "n_ancestors": len(anc),
            "first_carrier": {str(p): {"id": f, "gen": arrivals[p], "ops": gene[f]["ops"],
                                       "valued_elsewhere": sig_elsewhere(f, slot),
                                       "home_val": home_val(f, slot)} for p, f in first.items()},
            "precursors_never_carried": [p for p in range(k) if p not in first],
            "zero_utility_gens": {str(p): v for p, v in zero_gens.items()},
            "why_survived": dict(why),
            "gradient": [(x["gen"], None if x["home_gain"] is None else round(x["home_gain"], 4)) for x in path],
            "transition": trans,
            "strict_survivable_frac": round(float(np.mean([ever_sig(x["id"]) for x in path])), 3) if path else None,
            "assembly": mode + ("+EXAPTATION" if exapt else ""),
        })
    pool.close()
    json.dump(out, open(os.path.join(a.run, "HISTORIES.json"), "w"), indent=1, sort_keys=True)
    print(f"{len(out)} histories")


if __name__ == "__main__":
    main()
