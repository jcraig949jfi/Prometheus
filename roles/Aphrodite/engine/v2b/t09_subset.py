"""TEST-9 (Beta-01): SUBSET-BENEFIT SELECTION CRITERION (R7) on the endogenous route. Spec: T09_SUBSET_SPEC.md.

T07/T08 locate the natural-supply limit at the selection CRITERION. I_0's paired lower95 > 0 over all validation
cells rejects abstractions that help a SUBSET of heterogeneous natural families. g10 (gtc.py) is a content-free rule:
accept a candidate if it saves >= 1000 charges on some validation family AND its total losses do not exceed its
total gains; choose by net gain.

Validation is a FRESH breadth-12 draw: the original 4 VALIDATE families + 8 extras, seeded `APHRODITE/T09/VAL/<seed>`.
The extras come from each seed's qualified head and EXCLUDE every family in T51/T06 roles AND T08's exposed extras.
OBSERVE 4 and TRANSFER 32 are unchanged; escrow 30k; PRISTINE start (kind P).
Arms: g0 (I_0), g10, ORACLE10 (planted G1 under g10: diagnostic), NULL10 (planted OFF under g10: gate).
Endpoint: gain over PRISTINE on the 32 TRANSFER families (T07 cells; PRISTINE walks reused).
"""
import os
os.environ.setdefault("V2B_T51_DIR", "T04_T51")
import hashlib  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402

import r7e as R  # noqa: E402
import identity as I  # noqa: E402

OUT = R.RUNS / "T09_SUBSET"
EXTRA = 8
GEN = ["g0", "g10", "ORACLE10", "NULL10"]
VALIDATION_LIMITED = [4, 9, 12, 13, 14]


def roles_fresh():
    t08 = {r["seed"]: {f["name"] for f in r["families"]} for r in
           json.loads((R.RUNS / "T08_VB" / "T08_ROLES.json").read_text(encoding="utf-8"))}
    out = []
    for d, s, fams, panel in R.seeds():
        rows = R.rdl(R.RUNS / d / "T51_FOUNDRY.jsonl")
        used = {f["name"] for f in fams} | t08.get(s, set())
        q = sorted([r for r in rows if r.get("T4_qualified") and r["source"] == "LIN:%d" % s
                    and r.get("p_PRISTINE", 0) <= 0.75 and r["name"] not in used], key=lambda r: r["name"])
        rng = random.Random(I._seed("APHRODITE/T09/VAL/%d" % s))
        rng.shuffle(q)
        keep = [{k: f[k] for k in ("name", "role", "body", "init", "final", "Q2_size", "p_PRISTINE")} for f in fams]
        add = [{k: r[k] for k in ("name", "body", "init", "final", "Q2_size", "p_PRISTINE")} for r in q[:EXTRA]]
        for a in add:
            a["role"] = "VALIDATE"
        out.append((d, s, keep + add, panel, len(add)))
    return out


def stage_run(w=4):
    OUT.mkdir(parents=True, exist_ok=True)
    plan = roles_fresh()
    (OUT / "T09_ROLES.json").write_text(json.dumps([{"src": d, "seed": s, "families": f, "extra": n}
                                                    for d, s, f, _p, n in plan]), encoding="utf-8")
    done = {(x["seed"], x["genome"]) for x in R.rdl(OUT / "T09_DONORS.jsonl")}
    jobs = [(d, s, f, p, g) for d, s, f, p, n in plan if n == EXTRA for g in GEN if (s, g) not in done]
    R.log("T09 donor jobs %d" % len(jobs))
    with open(OUT / "T09_DONORS.jsonl", "a", encoding="utf-8") as fh, \
            ProcessPoolExecutor(max_workers=w, initializer=R.T.init_worker) as ex:
        for r in ex.map(R._donor, jobs):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            R.log("seed %d %-8s sel=%s origin=%s" % (r["seed"], r["genome"], r["selected_schema"], r["selected_origin"]))


def stage_score(w=4):
    donors = R.rdl(OUT / "T09_DONORS.jsonl")
    have = {(x["lib"], x["family"], x["cell"]) for x in R.rdl(R.RUNS / "T07_R7E" / "R7E_WALKS.jsonl")}
    have |= {(x["lib"], x["family"], x["cell"]) for x in R.rdl(R.RUNS / "T08_VB" / "T08_WALKS.jsonl")}
    fams_by = {s: [dict(f, seed="LIN%d" % s) for f in fams if f["role"] == "TRANSFER"] for _d, s, fams, _p in R.seeds()}
    index, todo = [], {}
    for x in donors:
        k = hashlib.sha256(json.dumps(x["selected_entries"], sort_keys=True).encode()).hexdigest()[:16]
        for f in fams_by[x["seed"]]:
            for ci in range(2):
                index.append({"seed": x["seed"], "genome": x["genome"], "family": f["name"], "cell": ci, "lib": k})
                if (k, f["name"], ci) not in have:
                    todo[(k, f["name"], ci)] = (k, x["selected_entries"], f, ci)
    (OUT / "T09_INDEX.json").write_text(json.dumps({"index": index}), encoding="utf-8")
    R.log("T09 new walks %d" % len(todo))
    with open(OUT / "T09_WALKS.jsonl", "a", encoding="utf-8") as fh, \
            ProcessPoolExecutor(max_workers=w, initializer=R.T.init_worker) as ex:
        for r in ex.map(R._walk, list(todo.values()), chunksize=2):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()


def stage_report():
    """Frozen rules: T09_SUBSET_SPEC.md s4."""
    from collections import defaultdict
    W = {}
    for p in (R.RUNS / "T07_R7E" / "R7E_WALKS.jsonl", R.RUNS / "T08_VB" / "T08_WALKS.jsonl", OUT / "T09_WALKS.jsonl"):
        for w in R.rdl(p):
            W[(w["lib"], w["family"], w["cell"])] = w["result"]
    t07idx = json.loads((R.RUNS / "T07_R7E" / "R7E_INDEX.json").read_text())["index"]
    pristine = {(e["seed"], e["family"], e["cell"]): e["lib"] for e in t07idx if e["genome"] == "PRISTINE"}
    ok = lambda r: bool(r) and not r.get("censored", True)  # noqa: E731
    idx = json.loads((OUT / "T09_INDEX.json").read_text())["index"]
    hit = defaultdict(set)
    for e in idx:
        r = W.get((e["lib"], e["family"], e["cell"]))
        p = W.get((pristine[(e["seed"], e["family"], e["cell"])], e["family"], e["cell"]))
        if ok(r) and not ok(p):
            hit[(e["genome"], e["seed"])].add(e["family"])
    seeds = sorted({e["seed"] for e in idx})
    gain = {g: {s: len(hit[(g, s)]) for s in seeds} for g in GEN}
    tot = {g: sum(gain[g].values()) for g in GEN}
    donors = {(x["seed"], x["genome"]): x for x in R.rdl(OUT / "T09_DONORS.jsonl")}
    null_sel = sum(1 for s in seeds if (donors.get((s, "NULL10"), {}).get("selected_origin") or "").startswith("PLANTED"))
    gate_null = null_sel <= 2 and tot["NULL10"] <= tot["g10"] + 2
    a = sum(1 for s in seeds if gain["g10"][s] > gain["g0"][s])
    b = sum(1 for s in seeds if gain["g10"][s] < gain["g0"][s])
    p = R._sign_p(a, b)
    oracle_acc = sum(1 for s in seeds if (donors.get((s, "ORACLE10"), {}).get("selected_origin") or "").startswith("PLANTED"))
    t07 = json.loads((R.RUNS / "T07_R7E" / "R7E_RESULT.json").read_text())
    res = {"seeds": seeds, "gain": gain, "totals": tot, "g10_vs_g0": {"better": a, "worse": b, "sign_p": round(p, 4)},
           "NULL10_planted_selected_seeds": null_sel, "gate_null": gate_null,
           "ORACLE10_planted_accepted_seeds": oracle_acc,
           "validation_limited_rescued_g10": [s for s in VALIDATION_LIMITED if gain["g10"].get(s, 0) > 0],
           "descriptive_vs_T07_g0_B4_total": t07["totals"]["g0"],
           "R7_SUBSET_POSITIVE": (p < 0.05 and tot["g10"] > tot["g0"]) if gate_null else None,
           "disposition": "MEASURED" if gate_null else "MEASUREMENT_FAILED"}
    (OUT / "T09_RESULT.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    R.log("T09 %s totals %s g10vs g0 %s null_sel %d oracle_acc %d rescued %s" % (
        res["disposition"], tot, res["g10_vs_g0"], null_sel, oracle_acc, res["validation_limited_rescued_g10"]))
    return res


if __name__ == "__main__":
    st = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    {"run": lambda: stage_run(w), "score": lambda: stage_score(w), "report": stage_report}[st]()
