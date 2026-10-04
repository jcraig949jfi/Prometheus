"""TEST-7 (Beta-01): R7E -- improver-RULE changes on the ENDOGENOUS route (rung R7). Spec: T07_R7E_SPEC.md.

The pristine-start donor (no inherited library) derives the base class on natural lineage supply in about half the seeds
(T51 5/8, T06 3/7). Its failures are observation starvation (3/15) and selection failure (4/15). Question: does a
CONTENT-FREE change to the improver's RULES, carried into fresh supply with NO library, raise what it derives and
reuses? Each genome runs on the same seeds (common random numbers) with PRISTINE start. That isolates the improver
from inherited content (W4 P-C).

Seeds: T51 roles (LIN 0-7) and T06 roles (LIN 8-15; seed 11 unfillable) = 15 seeds. Escrow 30k (T51 instruments).
Genomes (gtc.py): g0 (continuity: must reproduce T51/T06's P selections), g8 (selection: mean saving > 0), g9 (derive
also from VALIDATE hits), ORACLE (G1 entry planted: positive control), NULL (OFF entry planted: negative control).
Endpoint: gain = number of the seed's 32 TRANSFER families where the selected library reaches a T4-v1a-qualified
program at <= 1M in >= 1 of 2 cells AND PRISTINE is censored in that cell.
Stages: run [w] | score [w] | report.
"""
import os
os.environ.setdefault("V2B_T51_DIR", "T04_T51")
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402

import t51_natural as T  # noqa: E402
import gtc  # noqa: E402
import a17  # noqa: E402
from a18 import FR  # noqa: E402
import instruments as INS  # noqa: E402
import walk  # noqa: E402

RUNS = T.paths.ROOT / "beta01" / "runs"
OUT = RUNS / os.environ.get("V2B_R7E_DIR", "T07_R7E")
SRC = {"T04_T51": list(range(8)), "T06_T51C": [8, 9, 10, 12, 13, 14, 15]}
GEN = ["g0", "g8", "g9", "ORACLE", "NULL"]
CAP = int(os.environ.get("V2B_R7E_CAP", 1_000_000))


def log(m):
    print("[R7E %s] %s" % (time.strftime("%H:%M:%S", time.gmtime()), m), flush=True)


def rdj(p):
    return json.loads(p.read_text(encoding="utf-8"))


def rdl(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def seeds():
    out = []
    for d, ss in SRC.items():
        roles = rdj(RUNS / d / "T51_ROLES.json")
        panel = rdj(RUNS / d / "T51_PLAN.json")["panel"]
        for s in ss:
            if roles["LIN:%d" % s]["ok"]:
                out.append((d, s, roles["LIN:%d" % s]["families"], panel))
    return out


def _donor(a):
    T.init_worker()
    import a18_c1
    a17.R_VAL = a18_c1.R_VAL_C1          # as a18_c1._donor_job (T51/T06 donors)
    d, s, fams, panel, genome = a
    fl = [dict(f, qualified_dev_size=f["Q2_size"]) for f in fams]
    specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in fl}
    r = gtc.donor_g(genome, ("LIN%d" % s, "P", s, fl, specs, panel, True))
    return {"src": d, "seed": s, "genome": genome, "selected_schema": r["selected_schema"],
            "selected_origin": r["selected_origin"], "selected_entries": r["selected_entries"],
            "n_observed": r["n_observed"], "n_derived": r["n_derived"], "classes": r["classes"], "seconds": r["seconds"]}


def stage_run(w=4):
    OUT.mkdir(parents=True, exist_ok=True)
    done = {(x["seed"], x["genome"]) for x in rdl(OUT / "R7E_DONORS.jsonl")}
    jobs = [(d, s, f, p, g) for d, s, f, p in seeds() for g in GEN if (s, g) not in done]
    log("donor jobs %d" % len(jobs))
    with open(OUT / "R7E_DONORS.jsonl", "a", encoding="utf-8") as fh, \
            ProcessPoolExecutor(max_workers=w, initializer=T.init_worker) as ex:
        for r in ex.map(_donor, jobs):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            log("seed %d %-6s sel=%s obs=%d der=%d" % (r["seed"], r["genome"], r["selected_schema"], r["n_observed"],
                                                      r["n_derived"]))


def _walk(a):
    T.init_worker()
    key, entries, f, ci = a
    prov = a17.Prov({f["name"]: (f["body"], f["final"], f["init"])})
    a17.M.use_provider(prov)
    c = FR.Cell(prov, f["name"], ci, f["Q2_size"], label="T51-%s-rx" % f["seed"])   # T51's transfer cell seeds
    r = walk.first_qualified(FR.KLib(entries), c, CAP, INS.qualifier(prov, f["name"], "v1a", "BOTH"))
    return {"lib": key, "family": f["name"], "cell": ci, "result": r}


def stage_score(w=4):
    donors = rdl(OUT / "R7E_DONORS.jsonl")
    libs, jobs, index = {}, [], []

    def key(e):
        k = hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest()[:16]
        libs.setdefault(k, e)
        return k
    P = key(FR.pristine().entries)
    fams_by = {s: [dict(f, seed="LIN%d" % s) for f in fams if f["role"] == "TRANSFER"] for _d, s, fams, _p in seeds()}
    for x in donors:
        k = key(x["selected_entries"])
        for f in fams_by[x["seed"]]:
            for ci in range(2):
                index.append({"seed": x["seed"], "genome": x["genome"], "family": f["name"], "cell": ci, "lib": k})
                jobs.append((k, f, ci))
    for s, fs in fams_by.items():
        for f in fs:
            for ci in range(2):
                index.append({"seed": s, "genome": "PRISTINE", "family": f["name"], "cell": ci, "lib": P})
                jobs.append((P, f, ci))
    (OUT / "R7E_INDEX.json").write_text(json.dumps({"index": index}), encoding="utf-8")
    done = {(x["lib"], x["family"], x["cell"]) for x in rdl(OUT / "R7E_WALKS.jsonl")}
    uniq = {}
    for k, f, ci in jobs:
        uniq.setdefault((k, f["name"], ci), (k, libs[k], f, ci))
    todo = [v for kk, v in sorted(uniq.items()) if kk not in done]
    log("walks %d todo %d" % (len(uniq), len(todo)))
    with open(OUT / "R7E_WALKS.jsonl", "a", encoding="utf-8") as fh, \
            ProcessPoolExecutor(max_workers=w, initializer=T.init_worker) as ex:
        for r in ex.map(_walk, todo, chunksize=2):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
    log("score done")


def _sign_p(a, b):
    n = a + b
    return sum(math.comb(n, k) for k in range(a, n + 1)) / 2 ** n if n else 1.0


def stage_report():
    """Frozen rules: T07_R7E_SPEC.md s4."""
    idx = rdj(OUT / "R7E_INDEX.json")["index"]
    W = {(w["lib"], w["family"], w["cell"]): w["result"] for w in rdl(OUT / "R7E_WALKS.jsonl")}
    ok = lambda r: bool(r) and not r.get("censored", True)  # noqa: E731
    from collections import defaultdict
    by = defaultdict(dict)
    for e in idx:
        by[(e["seed"], e["family"], e["cell"])][e["genome"]] = W.get((e["lib"], e["family"], e["cell"]))
    gain = defaultdict(lambda: defaultdict(int))
    fams = defaultdict(set)
    for (s, f, ci) in by:
        fams[s].add(f)
    for s, fs in fams.items():
        for g in GEN:
            for f in fs:
                if any(ok(by[(s, f, ci)].get(g)) and not ok(by[(s, f, ci)].get("PRISTINE")) for ci in range(2)):
                    gain[g][s] += 1
    S = sorted(fams)
    tot = {g: sum(gain[g][s] for s in S) for g in GEN}
    donors = {(x["seed"], x["genome"]): x for x in rdl(OUT / "R7E_DONORS.jsonl")}
    prev = {}
    for d in SRC:
        for x in rdl(RUNS / d / "T51_DONORS.jsonl"):
            if x["arm"] == "P":
                prev[int(x["catalog"][3:])] = x["selected_schema"]
    cont = sum(1 for s in S if donors.get((s, "g0"), {}).get("selected_schema") == prev.get(s))
    inherited = 0
    for d in SRC:
        r = rdj(RUNS / d / ("T06_RESULT.json" if d == "T06_T51C" else "T51_EXPLORATORY_VS_PRISTINE.json"))
        if d == "T06_T51C":
            inherited += sum(r["G1_START_gain"].values())
        else:
            inherited += r["absolute_family_gains_vs_PRISTINE"]["G1"]["START_vs_PRISTINE"]
    gates = {"continuity_g0": cont == len(S), "oracle_upper": tot["ORACLE"] >= 0.9 * inherited,
             "null_lower": tot["NULL"] <= tot["g0"] + 2}
    out = {"seeds": S, "gain": {g: dict(gain[g]) for g in GEN}, "totals": tot, "inherited_reference": inherited,
           "continuity_g0": "%d/%d" % (cont, len(S)), "gates": gates, "tests": {}}
    for g in ("g8", "g9"):
        a = sum(1 for s in S if gain[g][s] > gain["g0"][s])
        b = sum(1 for s in S if gain[g][s] < gain["g0"][s])
        out["tests"][g] = {"better_seeds": a, "worse_seeds": b, "sign_p": round(_sign_p(a, b), 4),
                           "total_delta": tot[g] - tot["g0"],
                           "R7E_POSITIVE": _sign_p(a, b) < 0.05 and tot[g] > tot["g0"],
                           "derivation_success_seeds": sum(1 for s in S if donors.get((s, g), {}).get("selected_schema"))}
    out["disposition"] = "MEASURED" if all(gates.values()) else "MEASUREMENT_FAILED"
    (OUT / "R7E_RESULT.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    log("disposition %s gates %s totals %s tests %s" % (out["disposition"], gates, tot,
                                                       {g: (v["R7E_POSITIVE"], v["sign_p"]) for g, v in out["tests"].items()}))
    return out


if __name__ == "__main__":
    st = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    {"run": lambda: stage_run(w), "score": lambda: stage_score(w), "report": stage_report}[st]()
