"""TEST-11 (Beta-01): ABSTRACTION-ONLY CANDIDACY under g10 (rung R3; improver-rule change). Spec: T11_ABS_SPEC.md.

DEV-11 diagnosis (D11_DERIVATION_DIAG.json + donor entries): the MEMORISE library (it stores observed programs) wins
g10's net-gain score in T09 seeds 7, 9 and 14 and in T10 seeds 6, 12, 13 and 14. It never transfers. Its validation
savings grow with observation, so observation breadth (T10) fed memorisation as much as abstraction.

g11 = g10 with MEMORISE removed from the candidate set before selection. This is content-free: a rule about candidate
TYPE (non-generalising stored programs), with no family labels. Everything else is identical to T09/T10.
Arms: g11 at O4 (T09 roles), g11 at O10 (T10 roles), NULL11 at O10 (OFF planted under g11: gate).
Baselines (existing rows): g10 O4 = T09 g10; g10 O10 = T10 g10; g0 O4 = T09 g0.
Known answers (checked before freeze):
- K1: seed 3 g11 O4 reproduces T09's g10 row exactly (MEMORISE did not win there);
- K2: seed 13 g11 O10 selects (v - {H}), as predicted by the D11 table (the max net-gain schema once MEMORISE is
  removed).
Stages: known | run [w] | score [w] | report.
"""
import os
os.environ.setdefault("V2B_T51_DIR", "T04_T51")
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402

import r7e as R  # noqa: E402
import t10_observe as T10  # noqa: E402

OUT = R.RUNS / "T11_ABS"
T09 = R.RUNS / "T09_SUBSET"
T10D = R.RUNS / "T10_OBS"
ARMS = [("g11", "O4"), ("g11", "O10"), ("NULL11", "O10")]
BASE_GENOME = {"g11": "g10", "NULL11": "NULL10"}
EXCLUDE = "MEMORISE"


def _install_g11():
    import gtc
    if getattr(gtc._select_subset, "_g11", False):
        return
    orig = gtc._select_subset

    def sel(cands, start, cells):
        return orig({k: v for k, v in cands.items() if k != EXCLUDE}, start, cells)
    sel._g11 = True
    gtc._select_subset = sel


def _job(a):
    genome, obs, d, s, fams, panel = a
    R.T.init_worker()
    _install_g11()
    r = R._donor((d, s, fams, panel, BASE_GENOME[genome]))
    r["genome"], r["obs"] = genome, obs
    return r


def _plan():
    r09 = {x["seed"]: x for x in json.loads((T09 / "T09_ROLES.json").read_text(encoding="utf-8"))}
    r10 = {x["seed"]: x for x in json.loads((T10D / "T10_ROLES.json").read_text(encoding="utf-8"))}
    panel = {s: p for _d, s, _f, p in R.seeds()}
    return r09, r10, panel


def _arm_key(r):
    return "%s_%s" % (r["genome"], r["obs"])


def stage_known():
    OUT.mkdir(parents=True, exist_ok=True)
    r09, r10, panel = _plan()
    jobs = [("g11", "O4", r09[3]["src"], 3, r09[3]["families"], panel[3]),
            ("g11", "O10", r10[13]["src"], 13, r10[13]["families"], panel[13])]
    with ProcessPoolExecutor(max_workers=2, initializer=R.T.init_worker) as ex:
        a, b = list(ex.map(_job, jobs))
    ref = {x["seed"]: x for x in R.rdl(T09 / "T09_DONORS.jsonl") if x["genome"] == "g10"}[3]
    k1 = all(a[k] == ref[k] for k in T10.CONT_KEYS)
    k2 = b["selected_schema"] == "(v - {H})"
    res = {"K1_seed3_O4_reproduces_T09_g10": k1, "K2_seed13_O10_selects_(v - {H})": k2,
           "K2_observed": b["selected_schema"], "pass": k1 and k2}
    (OUT / "T11_KNOWN.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    R.log("T11 known %s" % res)
    return res


def stage_run(w=4):
    OUT.mkdir(parents=True, exist_ok=True)
    r09, r10, panel = _plan()
    done = {(x["seed"], _arm_key(x)) for x in R.rdl(OUT / "T11_DONORS.jsonl")}
    jobs = []
    for g, o in ARMS:
        src = r09 if o == "O4" else r10
        for s in sorted(src):
            if (s, "%s_%s" % (g, o)) not in done:
                jobs.append((g, o, src[s]["src"], s, src[s]["families"], panel[s]))
    R.log("T11 donor jobs %d" % len(jobs))
    with open(OUT / "T11_DONORS.jsonl", "a", encoding="utf-8") as fh, \
            ProcessPoolExecutor(max_workers=w, initializer=R.T.init_worker) as ex:
        for r in ex.map(_job, jobs):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            R.log("seed %d %-11s sel=%s origin=%s" % (r["seed"], _arm_key(r), r["selected_schema"], r["selected_origin"]))


def stage_score(w=4):
    donors = R.rdl(OUT / "T11_DONORS.jsonl")
    have = set()
    for p in (R.RUNS / "T07_R7E" / "R7E_WALKS.jsonl", R.RUNS / "T08_VB" / "T08_WALKS.jsonl", T09 / "T09_WALKS.jsonl",
              T10D / "T10_WALKS.jsonl"):
        have |= {(x["lib"], x["family"], x["cell"]) for x in R.rdl(p)}
    fams_by = {s: [dict(f, seed="LIN%d" % s) for f in fams if f["role"] == "TRANSFER"] for _d, s, fams, _p in R.seeds()}
    index, todo = [], {}
    for x in donors:
        k = hashlib.sha256(json.dumps(x["selected_entries"], sort_keys=True).encode()).hexdigest()[:16]
        for f in fams_by[x["seed"]]:
            for ci in range(2):
                index.append({"seed": x["seed"], "genome": _arm_key(x), "family": f["name"], "cell": ci, "lib": k})
                if (k, f["name"], ci) not in have:
                    todo[(k, f["name"], ci)] = (k, x["selected_entries"], f, ci)
    (OUT / "T11_INDEX.json").write_text(json.dumps({"index": index}), encoding="utf-8")
    R.log("T11 new walks %d" % len(todo))
    with open(OUT / "T11_WALKS.jsonl", "a", encoding="utf-8") as fh, \
            ProcessPoolExecutor(max_workers=w, initializer=R.T.init_worker) as ex:
        for r in ex.map(R._walk, list(todo.values()), chunksize=2):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()


def _cmp(a, b, seeds):
    better = sum(1 for s in seeds if a[s] > b[s])
    worse = sum(1 for s in seeds if a[s] < b[s])
    p = R._sign_p(better, worse)
    return {"better": better, "worse": worse, "tied": len(seeds) - better - worse, "sign_p": round(p, 4),
            "total_a": sum(a[s] for s in seeds), "total_b": sum(b[s] for s in seeds),
            "positive": p < 0.05 and sum(a[s] for s in seeds) > sum(b[s] for s in seeds)}


def stage_report():
    """Frozen rules: T11_ABS_SPEC.md s4."""
    W = {}
    for p in (R.RUNS / "T07_R7E" / "R7E_WALKS.jsonl", R.RUNS / "T08_VB" / "T08_WALKS.jsonl", T09 / "T09_WALKS.jsonl",
              T10D / "T10_WALKS.jsonl", OUT / "T11_WALKS.jsonl"):
        for w in R.rdl(p):
            W[(w["lib"], w["family"], w["cell"])] = w["result"]
    t07idx = json.loads((R.RUNS / "T07_R7E" / "R7E_INDEX.json").read_text())["index"]
    pristine = {(e["seed"], e["family"], e["cell"]): e["lib"] for e in t07idx if e["genome"] == "PRISTINE"}
    i09 = json.loads((T09 / "T09_INDEX.json").read_text())["index"]
    i10 = json.loads((T10D / "T10_INDEX.json").read_text())["index"]
    i11 = json.loads((OUT / "T11_INDEX.json").read_text())["index"]
    seeds = sorted({e["seed"] for e in i11})

    def g(idx, genome):
        h = T10._gains(idx, W, pristine, genome)
        return {s: len(h[s]) for s in seeds}
    gain = {"g0_O4": g(i09, "g0"), "g10_O4": g(i09, "g10"), "g10_O10": g(i10, "g10"),
            "g11_O4": g(i11, "g11_O4"), "g11_O10": g(i11, "g11_O10"), "NULL11_O10": g(i11, "NULL11_O10")}
    tot = {k: sum(v.values()) for k, v in gain.items()}
    d11 = {(x["seed"], _arm_key(x)): x for x in R.rdl(OUT / "T11_DONORS.jsonl")}
    known = json.loads((OUT / "T11_KNOWN.json").read_text())
    null_sel = sum(1 for s in seeds if (d11.get((s, "NULL11_O10"), {}).get("selected_origin") or "").startswith("PLANTED"))
    gate = known["pass"] and null_sel <= 2 and tot["NULL11_O10"] <= tot["g11_O10"] + 2
    primary = _cmp(gain["g11_O10"], gain["g10_O10"], seeds)
    sec_o4 = _cmp(gain["g11_O4"], gain["g10_O4"], seeds)
    cumulative = _cmp(gain["g11_O10"], gain["g0_O4"], seeds)
    memo = {k: sum(1 for s in seeds if [e["name"] for e in d11[(s, k)]["selected_entries"]][:1] == ["memorised"])
            for k in ("g11_O4", "g11_O10", "NULL11_O10")}
    res = {"seeds": seeds, "gain": gain, "totals": tot, "known": known, "NULL11_planted_selected_seeds": null_sel,
           "gate": gate, "memorise_selected_seeds": memo,
           "PRIMARY_g11O10_vs_g10O10": primary, "SECONDARY_g11O4_vs_g10O4": sec_o4,
           "CUMULATIVE_g11O10_vs_g0O4": cumulative,
           "ABSTRACTION_ONLY_POSITIVE": primary["positive"] if gate else None,
           "IMPROVER_CUMULATIVE_POSITIVE": cumulative["positive"] if gate else None,
           "per_seed_selection": {s: {k: d11[(s, k)]["selected_schema"] for k in ("g11_O4", "g11_O10")} for s in seeds},
           "disposition": "MEASURED" if gate else "MEASUREMENT_FAILED"}
    (OUT / "T11_RESULT.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    R.log("T11 %s totals %s primary %s secO4 %s cumulative %s null_sel %d" % (
        res["disposition"], tot, primary, sec_o4, cumulative, null_sel))
    return res


if __name__ == "__main__":
    st = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    {"known": stage_known, "run": lambda: stage_run(w), "score": lambda: stage_score(w), "report": stage_report}[st]()
