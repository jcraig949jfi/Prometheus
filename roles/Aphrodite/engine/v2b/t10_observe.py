"""TEST-10 (Beta-01): OBSERVE BREADTH as the CANDIDACY discriminator (rung R2, fed by observation supply).
Spec: T10_OBS_SPEC.md.

T09 localised the remaining endogenous-route failures to candidacy. In seeds 0, 7 and 12 the improver derives nothing:
its 4 OBSERVE families yield 0-3 observations at escrow 30k. In seed 9 it derives the wrong class. ORACLE10 shows that
g10 would accept the base class in all four. Question: does OBSERVING more families (4 -> 10) let the pristine
improver generate the candidate it is missing?

Held fixed from T09: the g10 rule, the T09 roles (OBSERVE 4 + fresh breadth-12 VALIDATE + TRANSFER 32), escrow 30k,
PRISTINE start, and the endpoint. Added: 6 fresh OBSERVE families per seed, drawn from the A19 OBSERVE floor
(0 < p_PRISTINE <= .75), seeded `APHRODITE/T10/OBS/<seed>`. They exclude every family used in T51/T06 roles, T08
extras and T09 roles.
Arms: g10 at O10 (treatment), NULL10 at O10 (gate). The baseline is T09's g10 rows (O4). CONT = g10 at O4 for seeds
0 and 3, which must reproduce T09's rows exactly.
Stages: cont | run [w] | score [w] | report.
"""
import os
os.environ.setdefault("V2B_T51_DIR", "T04_T51")
import hashlib  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
from collections import defaultdict  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402

import r7e as R  # noqa: E402
import identity as I  # noqa: E402

OUT = R.RUNS / "T10_OBS"
T09 = R.RUNS / "T09_SUBSET"
EXTRA_OBS = 6
GEN = ["g10", "NULL10"]
CONT_SEEDS = [0, 3]
STARVED = [0, 7, 12]
CONT_KEYS = ("selected_schema", "selected_origin", "selected_entries", "n_observed", "n_derived", "classes")


def t09_roles():
    return {r["seed"]: r for r in json.loads((T09 / "T09_ROLES.json").read_text(encoding="utf-8"))}


def roles_t10():
    t08 = {r["seed"]: {f["name"] for f in r["families"]} for r in
           json.loads((R.RUNS / "T08_VB" / "T08_ROLES.json").read_text(encoding="utf-8"))}
    r09 = t09_roles()
    out = []
    for d, s, fams, panel in R.seeds():
        rows = R.rdl(R.RUNS / d / "T51_FOUNDRY.jsonl")
        base = r09[s]["families"]
        used = {f["name"] for f in fams} | t08.get(s, set()) | {f["name"] for f in base}
        q = sorted([r for r in rows if r.get("T4_qualified") and r["source"] == "LIN:%d" % s
                    and 0 < r.get("p_PRISTINE", 0) <= 0.75 and r["name"] not in used], key=lambda r: r["name"])
        rng = random.Random(I._seed("APHRODITE/T10/OBS/%d" % s))
        rng.shuffle(q)
        add = [{k: r[k] for k in ("name", "body", "init", "final", "Q2_size", "p_PRISTINE")} for r in q[:EXTRA_OBS]]
        for a in add:
            a["role"] = "OBSERVE"
        out.append((d, s, base, base + add, panel, len(add)))
    return out


def _job(a):
    arm, d, s, fams, panel, genome = a
    r = R._donor((d, s, fams, panel, genome))
    r["arm"] = arm
    return r


def stage_cont():
    """Known-answer continuity: g10 on T09's own roles (O4) must reproduce T09's g10 rows exactly."""
    OUT.mkdir(parents=True, exist_ok=True)
    t09 = {(x["seed"], x["genome"]): x for x in R.rdl(T09 / "T09_DONORS.jsonl")}
    plan = {s: (d, base, p) for d, s, base, _f, p, _n in roles_t10()}
    rows = []
    with ProcessPoolExecutor(max_workers=len(CONT_SEEDS), initializer=R.T.init_worker) as ex:
        for r in ex.map(_job, [("CONT", plan[s][0], s, plan[s][1], plan[s][2], "g10") for s in CONT_SEEDS]):
            ref = t09[(r["seed"], "g10")]
            rows.append({"seed": r["seed"], "equal": all(r[k] == ref[k] for k in CONT_KEYS),
                         "diff": [k for k in CONT_KEYS if r[k] != ref[k]]})
    res = {"continuity": rows, "pass": all(x["equal"] for x in rows)}
    (OUT / "T10_CONTINUITY.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    R.log("T10 continuity %s" % res)
    return res


def stage_run(w=4):
    OUT.mkdir(parents=True, exist_ok=True)
    plan = roles_t10()
    (OUT / "T10_ROLES.json").write_text(json.dumps([{"src": d, "seed": s, "families": f, "extra_obs": n}
                                                    for d, s, _b, f, _p, n in plan]), encoding="utf-8")
    done = {(x["seed"], x["genome"]) for x in R.rdl(OUT / "T10_DONORS.jsonl")}
    jobs = [("O10", d, s, f, p, g) for d, s, _b, f, p, n in plan if n == EXTRA_OBS for g in GEN if (s, g) not in done]
    R.log("T10 donor jobs %d" % len(jobs))
    with open(OUT / "T10_DONORS.jsonl", "a", encoding="utf-8") as fh, \
            ProcessPoolExecutor(max_workers=w, initializer=R.T.init_worker) as ex:
        for r in ex.map(_job, jobs):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            R.log("seed %d %-6s sel=%s origin=%s obs=%d der=%d" % (r["seed"], r["genome"], r["selected_schema"],
                                                                   r["selected_origin"], r["n_observed"], r["n_derived"]))


def stage_score(w=4):
    donors = R.rdl(OUT / "T10_DONORS.jsonl")
    have = set()
    for p in (R.RUNS / "T07_R7E" / "R7E_WALKS.jsonl", R.RUNS / "T08_VB" / "T08_WALKS.jsonl", T09 / "T09_WALKS.jsonl"):
        have |= {(x["lib"], x["family"], x["cell"]) for x in R.rdl(p)}
    fams_by = {s: [dict(f, seed="LIN%d" % s) for f in fams if f["role"] == "TRANSFER"] for _d, s, fams, _p in R.seeds()}
    index, todo = [], {}
    for x in donors:
        k = hashlib.sha256(json.dumps(x["selected_entries"], sort_keys=True).encode()).hexdigest()[:16]
        for f in fams_by[x["seed"]]:
            for ci in range(2):
                index.append({"seed": x["seed"], "genome": x["genome"], "family": f["name"], "cell": ci, "lib": k})
                if (k, f["name"], ci) not in have:
                    todo[(k, f["name"], ci)] = (k, x["selected_entries"], f, ci)
    (OUT / "T10_INDEX.json").write_text(json.dumps({"index": index}), encoding="utf-8")
    R.log("T10 new walks %d" % len(todo))
    with open(OUT / "T10_WALKS.jsonl", "a", encoding="utf-8") as fh, \
            ProcessPoolExecutor(max_workers=w, initializer=R.T.init_worker) as ex:
        for r in ex.map(R._walk, list(todo.values()), chunksize=2):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()


def _gains(idx, W, pristine, genome):
    ok = lambda r: bool(r) and not r.get("censored", True)  # noqa: E731
    hit = defaultdict(set)
    for e in idx:
        if e["genome"] != genome:
            continue
        r = W.get((e["lib"], e["family"], e["cell"]))
        p = W.get((pristine[(e["seed"], e["family"], e["cell"])], e["family"], e["cell"]))
        if ok(r) and not ok(p):
            hit[e["seed"]].add(e["family"])
    return hit


def stage_report():
    """Frozen rules: T10_OBS_SPEC.md s4."""
    W = {}
    for p in (R.RUNS / "T07_R7E" / "R7E_WALKS.jsonl", R.RUNS / "T08_VB" / "T08_WALKS.jsonl", T09 / "T09_WALKS.jsonl",
              OUT / "T10_WALKS.jsonl"):
        for w in R.rdl(p):
            W[(w["lib"], w["family"], w["cell"])] = w["result"]
    t07idx = json.loads((R.RUNS / "T07_R7E" / "R7E_INDEX.json").read_text())["index"]
    pristine = {(e["seed"], e["family"], e["cell"]): e["lib"] for e in t07idx if e["genome"] == "PRISTINE"}
    i09 = json.loads((T09 / "T09_INDEX.json").read_text())["index"]
    i10 = json.loads((OUT / "T10_INDEX.json").read_text())["index"]
    seeds = sorted({e["seed"] for e in i10})
    h_o4 = _gains(i09, W, pristine, "g10")
    h_o10 = _gains(i10, W, pristine, "g10")
    h_null = _gains(i10, W, pristine, "NULL10")
    gain = {"g10_O4": {s: len(h_o4[s]) for s in seeds}, "g10_O10": {s: len(h_o10[s]) for s in seeds},
            "NULL10_O10": {s: len(h_null[s]) for s in seeds}}
    tot = {k: sum(v.values()) for k, v in gain.items()}
    d09 = {(x["seed"], x["genome"]): x for x in R.rdl(T09 / "T09_DONORS.jsonl")}
    d10 = {(x["seed"], x["genome"]): x for x in R.rdl(OUT / "T10_DONORS.jsonl")}
    cont = json.loads((OUT / "T10_CONTINUITY.json").read_text())
    null_sel = sum(1 for s in seeds if (d10.get((s, "NULL10"), {}).get("selected_origin") or "").startswith("PLANTED"))
    gate = cont["pass"] and null_sel <= 2 and tot["NULL10_O10"] <= tot["g10_O10"] + 2
    a = sum(1 for s in seeds if gain["g10_O10"][s] > gain["g10_O4"][s])
    b = sum(1 for s in seeds if gain["g10_O10"][s] < gain["g10_O4"][s])
    p = R._sign_p(a, b)
    per_seed = {s: {"O4": {k: d09[(s, "g10")][k] for k in ("selected_schema", "n_observed", "n_derived")},
                    "O10": {k: d10[(s, "g10")][k] for k in ("selected_schema", "n_observed", "n_derived")}}
                for s in seeds}
    rescued = [s for s in STARVED if gain["g10_O10"].get(s, 0) > 0]
    res = {"seeds": seeds, "gain": gain, "totals": tot,
           "O10_vs_O4": {"better": a, "worse": b, "tied": len(seeds) - a - b, "sign_p": round(p, 4)},
           "continuity_pass": cont["pass"], "NULL10_planted_selected_seeds": null_sel, "gate": gate,
           "starved_rescued": rescued, "per_seed": per_seed,
           "CANDIDACY_POSITIVE": (p < 0.05 and tot["g10_O10"] > tot["g10_O4"]) if gate else None,
           "STARVATION_RESCUE": (len(rescued) >= 2) if gate else None,
           "disposition": "MEASURED" if gate else "MEASUREMENT_FAILED"}
    (OUT / "T10_RESULT.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    R.log("T10 %s totals %s O10vsO4 %s null_sel %d rescued %s" % (res["disposition"], tot, res["O10_vs_O4"],
                                                                 null_sel, rescued))
    return res


if __name__ == "__main__":
    st = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    {"cont": stage_cont, "run": lambda: stage_run(w), "score": lambda: stage_score(w), "report": stage_report}[st]()
