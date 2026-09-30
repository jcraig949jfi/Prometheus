"""EXPLORATORY (not preregistered): how did a Z-world solver's precursors
survive before they met? For each admitted lens on a Z world, walk its
genealogy and find, for each planted precursor (a `delay` of the planted
channel by the planted lag; any virtual channel mapping to it), the
ancestors that carried it, the generation it first appeared, and where
those carriers were being valued (their best individual val gain per
world, from EVALS). Uses the answer key only for this analysis.

Usage: python -m tyche.v1.trace_precursors <run_dir>
"""

from __future__ import annotations

import collections
import json
import os
import sys

from .. import lens as Lm


def jl(p):
    return [json.loads(x) for x in open(p, encoding="ascii") if x.strip()]


def carries(g, ch, lag, d):
    """Does g compute delay(raw channel ch, lag) in an output cone?"""
    need = set(Lm.cone(g, g["out"]))
    for i in need:
        op, args, p = g["ins"][i]
        if op == "delay" and p == lag and args[0] < Lm.NIN and args[0] % d == ch:
            return True
    return False


def main(run):
    specs = {s["id"]: s for s in json.load(open(os.path.join(run, "WORLDS.json")))}
    gene = {}
    for r in jl(os.path.join(run, "GENEALOGY.jsonl")):
        gene.setdefault(r["id"], r)
    best = collections.defaultdict(dict)
    for r in jl(os.path.join(run, "EVALS.jsonl")):
        for w, cs in r["cases"].items():
            best[r["id"]][w] = max(best[r["id"]].get(w, -1), max(cs.values()))
    rows = json.load(open(os.path.join(run, "PASS_D.json")))
    out = []
    for r in rows:
        s = specs[r["home"]]
        if s["cls"] != "Z" or s["law"]["kind"] != "xor2":
            continue
        L, d = s["law"], s["d"]
        prec = {"A": (L["a"], L["da"]), "B": (L["b"], L["db"])}
        # ancestors with depth
        anc, frontier = {}, [(r["id"], 0)]
        while frontier:
            i, k = frontier.pop()
            if i in anc or i not in gene:
                continue
            anc[i] = k
            frontier += [(p, k + 1) for p in gene[i]["parents"]]
        rec = {"lens": r["id"], "home": r["home"], "kind": r["kind"], "test": r["home_test"][0],
               "replicated": r["replicated"], "n_ancestors": len(anc)}
        for nm, (ch, lag) in prec.items():
            car = [i for i in anc if carries(gene[i]["genome"], ch, lag, d)]
            first = min(car, key=lambda i: gene[i]["birth_gen"]) if car else None
            vals = [(w, round(v, 3)) for w, v in sorted(best.get(first, {}).items(), key=lambda x: -x[1])[:3]] if first else []
            rec[f"precursor_{nm}"] = {"channel": ch, "lag": lag, "n_carriers": len(car),
                                      "first_carrier": first,
                                      "first_birth_gen": gene[first]["birth_gen"] if first else None,
                                      "first_carrier_ops": gene[first]["ops"] if first else None,
                                      "first_carrier_best_worlds": vals,
                                      "first_carrier_home_gain": round(best.get(first, {}).get(r["home"], float("nan")), 3) if first else None}
        # the ramp: home-world individual val gain along the first-parent line
        line, cur = [], r["id"]
        while cur in gene:
            line.append({"id": cur, "gen": gene[cur]["birth_gen"], "ops": gene[cur]["ops"],
                         "home_gain": round(best.get(cur, {}).get(r["home"], float("nan")), 3)})
            ps = gene[cur]["parents"]
            cur = ps[0] if ps else None
        rec["first_parent_line"] = line[::-1]
        both = [i for i in anc if all(carries(gene[i]["genome"], *prec[k], d) for k in "AB")]
        firstb = min(both, key=lambda i: gene[i]["birth_gen"]) if both else None
        rec["first_with_both"] = {"id": firstb, "birth_gen": gene[firstb]["birth_gen"] if firstb else None,
                                  "ops": gene[firstb]["ops"] if firstb else None,
                                  "parents": gene[firstb]["parents"] if firstb else None}
        out.append(rec)
    json.dump(out, open(os.path.join(run, "TRACE_PRECURSORS.json"), "w"), indent=1, sort_keys=True)
    for x in out:
        print(json.dumps(x, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1])
