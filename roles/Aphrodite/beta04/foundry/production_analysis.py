"""Post-hoc analysis of the E1 v2 PRODUCTION run (E1_V2_RULES Addendum D). READ-ONLY with respect to the frozen
pipeline: it reads production/ outputs and the frozen modules; it changes no gate, rule, feature or config.

    python production_analysis.py [--out production]

Writes production/E1_ADDENDUM_D.json and production/E1_ADDENDUM_D.md:
  1. Addendum D evaluation: per-world gate (>= 1 admitted R2 AND >= 1 admitted R3), pooled rule 7 over admitted
     R3/R4 (mechanism-kind pairings after near-duplicate merging and the motif cap, which FINAL.jsonl already
     applies), full pooled rejection histogram.
  2. Hindsight-regression DESCRIPTIVE diagnostic (Addendum D item 3; not a gate): would ANY dev-consistent model
     structure of the regression classes solve test? Hindsight is over model STRUCTURE: class key (E, S, W, P),
     keep rule (F), list statistic (P), recurrence constant (W). Inside one structure the fit is the same
     fewest-parameter fit the rung uses (per-class minimal subsets; W's feature set minimal), so this is a LOWER
     bound on full hindsight. 45 CPU-s cap per family (timeout reported; compute cap).
  3. Per-family headroom for admitted families: hitting cost of the known-positive route (R2: sealed oracle; R3/R4:
     acquired-library chain) vs the budgets, CRN rank and order-free expected rank; base 1e6 walk with
     dev-consistent counts.
"""
import argparse
import json
import os
import time
from collections import Counter

import numpy as np

import generator as G
import regress as R

HERE = os.path.dirname(os.path.abspath(__file__))


def read_jsonl(p):
    if not os.path.exists(p):
        return []
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


# ---------------------------------------------------------------- hindsight regression (descriptive)
def _ok(pred, test):
    for xs, y in test:
        try:
            p = pred(xs)
        except (OverflowError, ZeroDivisionError, TypeError):
            return False
        if p is None or p != y or type(p) is not type(y):
            return False
    return True


def hindsight_regression(dev, test, budget_s=45.0):
    B = R.derive_banks(G.CONFIG)
    pc = R.PhiCache(B["phi"])
    t0 = time.process_time()
    tried = Counter()

    def timeout():
        return time.process_time() - t0 > budget_s

    # E
    if all(type(y) is list and len(y) == len(x) for x, y in dev):
        xv = [v for x, _y in dev for v in x]
        yv = [w for _x, y in dev for w in y]
        for ncl, name, kf in R._data_keys(xv, B["keys"]):
            if timeout():
                return {"solved": None, "timeout": True, "tried": dict(tried)}
            r = R._keyed_fit(xv, yv, kf, pc)
            tried["E"] += 1
            if r is None or r[0] >= len(yv):
                continue
            model = r[1]

            def pred(xs, model=model, kf=kf):
                out = [R._keyed_pred(model, kf, v, pc) for v in xs]
                return None if any(o is None for o in out) else out
            if _ok(pred, test):
                return {"solved": True, "by": "E key=%s" % name, "tried": dict(tried)}
    # F
    if all(type(y) is list for _x, y in dev):
        preds = R._keep_preds(B)
        cands = [(n, p) for n, p, _k in preds]
        for i, (n1, p1, k1) in enumerate(preds):
            for n2, p2, k2 in preds[i + 1:]:
                if k1 != k2:
                    cands.append(("%s&%s" % (n1, n2), (lambda p1, p2: lambda v: p1(v) and p2(v))(p1, p2)))
        nrows = sum(len(x) for x, _y in dev)
        for n, p in cands:
            if timeout():
                return {"solved": None, "timeout": True, "tried": dict(tried)}
            kept = []
            for x, y in dev:
                kx = [v for v in x if p(v)]
                if len(kx) != len(y):
                    kept = None
                    break
                kept.append((kx, y))
            if kept is None:
                continue
            xv = [v for kx, _y in kept for v in kx]
            yv = [w for _kx, y in kept for w in y]
            keys = R._data_keys(xv, B["keys"]) if yv else [(1, "none", lambda v: 0)]
            for ncl, kname, kf in keys:
                if yv:
                    r = R._keyed_fit(xv, yv, kf, pc)
                    tried["F"] += 1
                    if r is None or r[0] >= nrows:
                        continue
                    model = r[1]
                else:
                    model = {}

                def pred(xs, model=model, kf=kf, p=p):
                    out = [R._keyed_pred(model, kf, v, pc) for v in xs if p(v)]
                    return None if any(o is None for o in out) else out
                if _ok(pred, test):
                    return {"solved": True, "by": "F keep=%s key=%s" % (n, kname), "tried": dict(tried)}
    # S, P, W: reuse the rung's fitters with restricted key lists (one structure at a time)
    for cname, fitter, keyfield in (("S", R.fit_S, "single_keys"), ("W", R.fit_W, "single_keys")):
        for name, kf in B[keyfield]:
            if timeout():
                return {"solved": None, "timeout": True, "tried": dict(tried)}
            B1 = dict(B, single_keys=[(name, kf)], consts=B["consts"])
            for c in (B["consts"] if cname == "W" else [None]):
                if c is not None:
                    B1 = dict(B1, consts=[c])
                m = fitter(dev, B1, pc)
                tried[cname] += 1
                if m is not None and _ok(m["pred"], test):
                    return {"solved": True, "by": m["desc"], "tried": dict(tried)}
    if all(type(y) is int for _x, y in dev):
        for st in B["stats"]:
            for name, kf in [("none", lambda v: 0)] + list(B["keys"]):
                if timeout():
                    return {"solved": None, "timeout": True, "tried": dict(tried)}
                B1 = dict(B, stats=[st], keys=[(name, kf)])
                m = R.fit_P(dev, B1, pc)
                tried["P"] += 1
                if m is not None and _ok(m["pred"], test):
                    return {"solved": True, "by": m["desc"], "tried": dict(tried)}
    return {"solved": False, "tried": dict(tried)}


# ---------------------------------------------------------------- main analysis
def analyse(out):
    with open(os.path.join(out, "WORLD_MANIFEST.json")) as f:
        man = json.load(f)
    worlds = sorted(man["worlds"], key=lambda w: man["worlds"][w]["commitment_index"])
    res = {"addendum": "E1_V2_RULES.md ADDENDUM D", "config_sha": man["config_sha"],
           "qual_config_sha": man["qual_config_sha"], "regression_bank": man["regression_bank"]["sha256"],
           "worlds": {}, "admitted": []}
    pooled_hist = {}
    pairings = set()
    gate_pass = []
    for wid in worlds:
        wd = os.path.join(out, wid)
        with open(os.path.join(wd, "WORLD_SEALED.json")) as f:
            world = json.load(f)
        recs = {r["family_id"]: r for r in world["families"]}
        finals = read_jsonl(os.path.join(wd, "FINAL.jsonl"))
        adm = {}
        for q in finals:
            r = recs[q["family_id"]]
            pooled_hist.setdefault(r["rung"], Counter())[q["class"]] += 1
            if q["status"] == "ADMITTED":
                adm.setdefault(r["rung"], []).append((q, r))
        gate = bool(adm.get("R2")) and bool(adm.get("R3"))
        if gate:
            gate_pass.append(wid)
        res["worlds"][wid] = {"commitment_index": man["worlds"][wid]["commitment_index"],
                              "world_seed_sha256": man["worlds"][wid]["world_seed_sha256"],
                              "admitted_by_rung": {k: len(v) for k, v in sorted(adm.items())},
                              "gate": "PASS" if gate else "FAIL",
                              "mechanisms": [m["name"] for m in world["mechanisms"]],
                              "unfilled": world["mechanism_screen"]["unfilled_slots"]}
        for rung, lst in sorted(adm.items()):
            for q, r in lst:
                if rung in ("R3", "R4"):
                    pairings.add(q["kind_pair"])
                item = {"world": wid, "family_id": q["family_id"], "rung": rung, "skeleton": r["skeleton"],
                        "kind_pair": q.get("kind_pair"), "fused_key": q["fused_key"],
                        "witness_promoted": r["witness_promoted"], "witness_esize": r["witness_esize"],
                        "promoted_esize": r["promoted_esize"], "capture": q["capture"],
                        "regression_selected_best_test_acc": q["regression"]["best_selected_test_acc"],
                        "base1e6": {"walk_charge": q["base1e6"]["walk_charge"],
                                    "n_dev_consistent": q["base1e6"]["n_dev_consistent"],
                                    "complete_size": q["base1e6"]["complete_size"]}}
                route = q["kp"] if rung == "R2" else q["chain_d"]
                item["headroom"] = {"route": "sealed-oracle KP" if rung == "R2" else "acquired-library chain (d)",
                                    "found": route.get("found"), "found_esize": route.get("found_esize"),
                                    "crn_rank": route.get("charge"),
                                    "order_free_rank": route.get("order_free_rank"),
                                    "order_free_estimated": route.get("order_free_rank_estimated"),
                                    "budget": 1_000_000, "B_small": 100_000,
                                    "crn_within_B_small": (route.get("charge") or 10 ** 9) <= 100_000,
                                    "order_free_within_budget": (route.get("order_free_rank") or 10 ** 12) <= 1_000_000,
                                    "complete_size": route.get("complete_size")}
                if rung != "R2":
                    item["acquired_used"] = route.get("acquired_used")
                    item["kp_capacity"] = q.get("kp", {}).get("status")
                t0 = time.process_time()
                item["hindsight_regression"] = hindsight_regression(r["dev"], r["test"])
                item["hindsight_regression"]["cpu_s"] = round(time.process_time() - t0, 1)
                res["admitted"].append(item)
                print(q["family_id"], item["hindsight_regression"].get("solved"), flush=True)
    r3 = sum(1 for a in res["admitted"] if a["rung"] == "R3")
    kp = sorted(pairings)
    e1 = "WORLD_DEMAND_QUALIFIED" if (gate_pass and len(kp) >= 3) else "WORLD_DEMAND_NOT_QUALIFIED"
    res["pooled"] = {
        "worlds": len(worlds), "worlds_passing_gate": len(gate_pass), "gate_pass_worlds": gate_pass,
        "admitted_by_rung": dict(sorted(Counter(a["rung"] for a in res["admitted"]).items())),
        "r3r4_kind_pairings": kp, "n_kind_pairings": len(kp),
        "rejection_histogram": {k: dict(sorted(v.items())) for k, v in sorted(pooled_hist.items())},
        "hindsight_regression_solves_admitted": sum(1 for a in res["admitted"]
                                                    if a["hindsight_regression"].get("solved")),
        "hindsight_regression_timeouts": sum(1 for a in res["admitted"]
                                             if a["hindsight_regression"].get("solved") is None),
        "r3_admitted": r3, "r5_admitted": sum(1 for a in res["admitted"] if a["rung"] == "R5"),
        "E1": "%s (gate PASS %d/%d worlds; %d mechanism-kind pairings among admitted R3/R4)" % (
            e1, len(gate_pass), len(worlds), len(kp)),
        "E1_label": e1}
    with open(os.path.join(out, "E1_ADDENDUM_D.json"), "w") as f:
        json.dump(res, f, sort_keys=True, indent=1)
    with open(os.path.join(out, "E1_ADDENDUM_D.md"), "w", encoding="utf-8") as f:
        f.write(render(res))
    print(res["pooled"]["E1"])
    return res


def render(res):
    p = res["pooled"]
    L = ["# E1 v2 PRODUCTION: Addendum D evaluation", "",
         "Frozen v2 code and config: generator `%s`, qualification `%s`, regression `%s`." % (
             res["config_sha"][:8], res["qual_config_sha"][:8], res["regression_bank"][:8]), "",
         "## E1 outcome", "", "**%s**" % p["E1"], "",
         "* Per-world gate (>= 1 admitted R2 AND >= 1 admitted R3): **%d / %d** worlds pass." % (
             p["worlds_passing_gate"], p["worlds"]),
         "* Pooled rule 7: mechanism-kind pairings among admitted R3/R4, after merging and caps: **%d** (%s); "
         "required >= 3." % (p["n_kind_pairings"], ", ".join(p["r3r4_kind_pairings"]) or "none"),
         "* Admitted by rung (pooled): %s. R5 admitted: %d." % (p["admitted_by_rung"], p["r5_admitted"]),
         "* Hindsight-regression diagnostic (descriptive, NOT a gate): it solves **%d** of %d admitted families "
         "(%d timeouts)." % (p["hindsight_regression_solves_admitted"], len(res["admitted"]),
                             p["hindsight_regression_timeouts"]), "",
         "## Per world", "", "| idx | world | mechanisms (unfilled) | admitted by rung | gate |", "|---|---|---|---|---|"]
    for wid, w in sorted(res["worlds"].items(), key=lambda kv: kv[1]["commitment_index"]):
        L.append("| %d | %s | %s (%s) | %s | %s |" % (w["commitment_index"], wid, ", ".join(w["mechanisms"]),
                                                       ", ".join(w["unfilled"]) or "-",
                                                       w["admitted_by_rung"] or "-", w["gate"]))
    L += ["", "## Pooled rejection histogram (gen-screen rejects included)", "", "| rung | class counts |",
          "|---|---|"]
    for rung, h in p["rejection_histogram"].items():
        L.append("| %s | %s |" % (rung, "; ".join("%s %d" % kv for kv in h.items())))
    L += ["", "## Admitted families: headroom and diagnostic", "",
          "| world | family | rung | kind pair | promoted witness | route solution | CRN rank | order-free rank | "
          "base 1e6 dev-consistent | hindsight regression |", "|---|---|---|---|---|---|---|---|---|---|"]
    for a in res["admitted"]:
        h = a["headroom"]
        hr = a["hindsight_regression"]
        L.append("| %s | %s | %s | %s | `%s` | `%s` | %s | %s%s | %s | %s |" % (
            a["world"], a["family_id"], a["rung"], a["kind_pair"] or "-", a["witness_promoted"], h["found"],
            h["crn_rank"], h["order_free_rank"], " (est.)" if h["order_free_estimated"] else "",
            a["base1e6"]["n_dev_consistent"],
            "SOLVED (%s)" % hr.get("by") if hr.get("solved") else ("timeout" if hr.get("solved") is None else "no")))
    L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "production"))
    a = ap.parse_args()
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    analyse(a.out)
