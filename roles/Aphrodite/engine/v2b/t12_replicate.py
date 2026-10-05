"""TEST-12 (Beta-01): FRESH-SEED REPLICATION of the cumulative improver change. Spec: T12_REPL_SPEC.md.

T09-T11 built, on 15 exposed seeds, an improver that differs from I_0 by three content-free rule changes:
- the g10 subset criterion;
- OBSERVE breadth 10;
- abstraction-only candidacy (g11 = g10 minus MEMORISE).
T11: 123 vs I_0's 93 (6/2/7), not positive under the frozen sign test. T12 asks the same question on UNEXPOSED supply:
W8 LIN seeds 16-23. They were never used in any role, and W8 supplies and X_S are already committed.

Supply (stage `supply`, which is the T51 pipeline unchanged): plan -> foundry (Q2 + T4 v1 + PRISTINE pilots, escrow
30k) -> roles (A19 NAT: OBSERVE 4, VALIDATE 4, TRANSFER 32; seeded APHRODITE/T51/ROLES/<s>).
Extras per seed, mirroring T09/T10:
- VALIDATE +8 from the head (p_PRISTINE <= .75), seeded APHRODITE/T12/VAL/<s>;
- OBSERVE +6 from the floor (0 < p <= .75), seeded APHRODITE/T12/OBS/<s>.
Both exclude the roles and each other.
Arms:
- g0_O4: I_0 with breadth-12 validation, as T09 g0;
- g10_O10;
- g11_O10;
- NULL11_O10: OFF planted under g11, the gate.
Endpoint (as T07): PRISTINE-censored transfer families reached by a T4-v1a-qualified program at <= 1M. PRISTINE is
walked here on the same cells.
Known answer K1: the runner reproduces T11's g11_O10 row for exposed seed 3.
Stages: supply [w] | known | run [w] | score [w] | report.
"""
import os
os.environ["V2B_T51_DIR"] = "T12_T51"
os.environ["V2B_T51_SEEDS"] = "16,17,18,19,20,21,22,23"
os.environ["V2B_T51_ARMS"] = "P"
import hashlib  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402

import r7e as R  # noqa: E402
import identity as I  # noqa: E402
import t10_observe as T10  # noqa: E402
import t11_absonly as T11  # noqa: E402

T = R.T
SUP = R.RUNS / "T12_T51"
OUT = R.RUNS / "T12_REPL"
SEEDS = T.SEEDS
EXTRA_VAL, EXTRA_OBS = 8, 6
ARMS = [("g0", "O4"), ("g10", "O10"), ("g11", "O10"), ("NULL11", "O10")]
MIN_SEEDS = 6


def stage_supply(w=4):
    SUP.mkdir(parents=True, exist_ok=True)
    if not (SUP / "T51_PLAN.json").exists():
        T.stage_plan()
    T.stage_foundry(w)
    T.stage_roles()


def plan_t12():
    roles = json.loads((SUP / "T51_ROLES.json").read_text(encoding="utf-8"))
    panel = json.loads((SUP / "T51_PLAN.json").read_text(encoding="utf-8"))["panel"]
    rows = R.rdl(SUP / "T51_FOUNDRY.jsonl")
    keep = ("name", "body", "init", "final", "Q2_size", "p_PRISTINE")
    out = []
    for s in SEEDS:
        r = roles["LIN:%d" % s]
        if not r["ok"]:
            continue
        base = r["families"]
        used = {f["name"] for f in base}
        q = sorted([x for x in rows if x.get("T4_qualified") and x["source"] == "LIN:%d" % s
                    and x.get("p_PRISTINE", 0) <= 0.75 and x["name"] not in used], key=lambda x: x["name"])
        rng = random.Random(I._seed("APHRODITE/T12/VAL/%d" % s))
        rng.shuffle(q)
        val = [dict({k: x[k] for k in keep}, role="VALIDATE") for x in q[:EXTRA_VAL]]
        used |= {f["name"] for f in val}
        fl = sorted([x for x in rows if x.get("T4_qualified") and x["source"] == "LIN:%d" % s
                     and 0 < x.get("p_PRISTINE", 0) <= 0.75 and x["name"] not in used], key=lambda x: x["name"])
        rng = random.Random(I._seed("APHRODITE/T12/OBS/%d" % s))
        rng.shuffle(fl)
        obs = [dict({k: x[k] for k in keep}, role="OBSERVE") for x in fl[:EXTRA_OBS]]
        ok = len(val) == EXTRA_VAL and len(obs) == EXTRA_OBS
        out.append({"seed": s, "ok": ok, "O4": base + val, "O10": base + val + obs, "panel": panel})
    return out


_ORIG_SELECT = []


def _set_selector(no_memorise):
    """Per-job selector: the pristine gtc._select_subset (g10) or the g11 wrapper (MEMORISE removed)."""
    import gtc
    if not _ORIG_SELECT:
        _ORIG_SELECT.append(gtc._select_subset)
    orig = _ORIG_SELECT[0]
    if no_memorise:
        def sel(cands, start, cells):
            return orig({k: v for k, v in cands.items() if k != T11.EXCLUDE}, start, cells)
        gtc._select_subset = sel
    else:
        gtc._select_subset = orig


def _job(a):
    genome, obs, s, fams, panel = a
    R.T.init_worker()
    _set_selector(genome in ("g11", "NULL11"))
    base = {"g0": "g0", "g10": "g10", "g11": "g10", "NULL11": "NULL10"}[genome]
    r = R._donor(("T12", s, fams, panel, base))
    r["genome"], r["obs"] = genome, obs
    return r


def stage_known():
    OUT.mkdir(parents=True, exist_ok=True)
    r10 = {x["seed"]: x for x in json.loads((R.RUNS / "T10_OBS" / "T10_ROLES.json").read_text(encoding="utf-8"))}
    panel = {s: p for _d, s, _f, p in R.seeds()}
    with ProcessPoolExecutor(max_workers=1, initializer=R.T.init_worker) as ex:   # one worker: g11 then g10
        a, b = list(ex.map(_job, [("g11", "O10", 3, r10[3]["families"], panel[3]),
                                  ("g10", "O10", 13, r10[13]["families"], panel[13])]))
    ref = {x["seed"]: x for x in R.rdl(R.RUNS / "T11_ABS" / "T11_DONORS.jsonl")
           if x["genome"] == "g11" and x["obs"] == "O10"}[3]
    ref10 = {x["seed"]: x for x in R.rdl(R.RUNS / "T10_OBS" / "T10_DONORS.jsonl") if x["genome"] == "g10"}[13]
    k1 = all(a[k] == ref[k] for k in T10.CONT_KEYS)
    k2 = all(b[k] == ref10[k] for k in T10.CONT_KEYS)   # g10 after g11 in the same worker: MEMORISE still chosen
    res = {"K1_seed3_g11_O10_reproduces_T11": k1, "K2_seed13_g10_O10_after_g11_reproduces_T10": k2,
           "pass": k1 and k2}
    (OUT / "T12_KNOWN.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    R.log("T12 known %s" % res)
    return res


def stage_run(w=4):
    OUT.mkdir(parents=True, exist_ok=True)
    plan = plan_t12()
    (OUT / "T12_ROLES.json").write_text(json.dumps(plan), encoding="utf-8")
    done = {(x["seed"], T11._arm_key(x)) for x in R.rdl(OUT / "T12_DONORS.jsonl")}
    jobs = [(g, o, p["seed"], p[o], p["panel"]) for p in plan if p["ok"] for g, o in ARMS
            if (p["seed"], "%s_%s" % (g, o)) not in done]
    R.log("T12 donor jobs %d (seeds ok %d/%d)" % (len(jobs), sum(p["ok"] for p in plan), len(SEEDS)))
    with open(OUT / "T12_DONORS.jsonl", "a", encoding="utf-8") as fh, \
            ProcessPoolExecutor(max_workers=w, initializer=R.T.init_worker) as ex:
        for r in ex.map(_job, jobs):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            R.log("seed %d %-11s sel=%s origin=%s" % (r["seed"], T11._arm_key(r), r["selected_schema"],
                                                      r["selected_origin"]))


def stage_score(w=4):
    donors = R.rdl(OUT / "T12_DONORS.jsonl")
    plan = {p["seed"]: p for p in json.loads((OUT / "T12_ROLES.json").read_text(encoding="utf-8"))}
    libs, index, jobs = {}, [], []

    def key(e):
        k = hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest()[:16]
        libs.setdefault(k, e)
        return k
    P = key(R.FR.pristine().entries)
    tr = {s: [dict(f, seed="LIN%d" % s) for f in p["O4"] if f["role"] == "TRANSFER"] for s, p in plan.items() if p["ok"]}
    for x in donors:
        k = key(x["selected_entries"])
        for f in tr[x["seed"]]:
            for ci in range(2):
                index.append({"seed": x["seed"], "genome": T11._arm_key(x), "family": f["name"], "cell": ci, "lib": k})
                jobs.append((k, f, ci))
    for s, fs in tr.items():
        for f in fs:
            for ci in range(2):
                index.append({"seed": s, "genome": "PRISTINE", "family": f["name"], "cell": ci, "lib": P})
                jobs.append((P, f, ci))
    (OUT / "T12_INDEX.json").write_text(json.dumps({"index": index}), encoding="utf-8")
    done = {(x["lib"], x["family"], x["cell"]) for x in R.rdl(OUT / "T12_WALKS.jsonl")}
    uniq = {}
    for k, f, ci in jobs:
        uniq.setdefault((k, f["name"], ci), (k, libs[k], f, ci))
    todo = [v for kk, v in sorted(uniq.items()) if kk not in done]
    R.log("T12 walks %d todo %d" % (len(uniq), len(todo)))
    with open(OUT / "T12_WALKS.jsonl", "a", encoding="utf-8") as fh, \
            ProcessPoolExecutor(max_workers=w, initializer=R.T.init_worker) as ex:
        for r in ex.map(R._walk, todo, chunksize=2):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()


def flip_p(d):
    """Exact one-sided sign-flip permutation p for sum(d) >= observed (zeros contribute nothing)."""
    nz = [x for x in d if x != 0]
    obs = sum(nz)
    if not nz:
        return 1.0, 1.0
    hits = sum(1 for signs in itertools.product((1, -1), repeat=len(nz))
               if sum(s * abs(x) for s, x in zip(signs, nz)) >= obs)
    return hits / 2 ** len(nz), 1 / 2 ** len(nz)


def _cmp(a, b, seeds):
    d = [a[s] - b[s] for s in seeds]
    p, pmin = flip_p(d)
    better, worse = sum(x > 0 for x in d), sum(x < 0 for x in d)
    return {"diffs": d, "better": better, "worse": worse, "tied": len(d) - better - worse, "flip_p": round(p, 4),
            "attainable_min_p": round(pmin, 4), "sign_p": round(R._sign_p(better, worse), 4),
            "total_a": sum(a[s] for s in seeds), "total_b": sum(b[s] for s in seeds),
            "positive": p < 0.05 and sum(d) > 0}


def stage_report():
    """Frozen rules: T12_REPL_SPEC.md s4."""
    W = {}
    for w in R.rdl(OUT / "T12_WALKS.jsonl"):
        W[(w["lib"], w["family"], w["cell"])] = w["result"]
    idx = json.loads((OUT / "T12_INDEX.json").read_text())["index"]
    pristine = {(e["seed"], e["family"], e["cell"]): e["lib"] for e in idx if e["genome"] == "PRISTINE"}
    seeds = sorted({e["seed"] for e in idx if e["genome"] != "PRISTINE"})
    gain = {}
    for g, o in ARMS:
        k = "%s_%s" % (g, o)
        h = T10._gains(idx, W, pristine, k)
        gain[k] = {s: len(h[s]) for s in seeds}
    tot = {k: sum(v.values()) for k, v in gain.items()}
    d = {(x["seed"], T11._arm_key(x)): x for x in R.rdl(OUT / "T12_DONORS.jsonl")}
    known = json.loads((OUT / "T12_KNOWN.json").read_text())
    null_sel = sum(1 for s in seeds if (d[(s, "NULL11_O10")].get("selected_origin") or "").startswith("PLANTED"))
    memo = {k: [s for s in seeds if [e["name"] for e in d[(s, k)]["selected_entries"]][:1] == ["memorised"]]
            for k in ("g0_O4", "g10_O10", "g11_O10")}
    supply_ok = len(seeds) >= MIN_SEEDS
    gate = known["pass"] and null_sel <= 2 and tot["NULL11_O10"] <= tot["g11_O10"] + 2
    prim = _cmp(gain["g11_O10"], gain["g0_O4"], seeds)
    sec = _cmp(gain["g11_O10"], gain["g10_O10"], seeds)
    t11 = json.loads((R.RUNS / "T11_ABS" / "T11_RESULT.json").read_text())["gain"]
    pooled_d = [t11["g11_O10"][k] - t11["g0_O4"][k] for k in t11["g11_O10"]] + prim["diffs"]
    pp, _ = flip_p(pooled_d)
    pooled = {"n_seeds": len(pooled_d), "sum_diff": sum(pooled_d), "flip_p": round(pp, 5), "label": "EXPOSED+FRESH"}
    disp = "SUPPLY_LIMITED" if not supply_ok else ("MEASURED" if gate else "MEASUREMENT_FAILED")
    res = {"seeds": seeds, "gain": gain, "totals": tot, "known": known, "NULL11_planted_selected_seeds": null_sel,
           "gate": gate, "memorise_selected": memo,
           "PRIMARY_g11O10_vs_g0O4": prim, "SECONDARY_g11O10_vs_g10O10": sec, "POOLED_descriptive": pooled,
           "IMPROVER_REPLICATED_POSITIVE": prim["positive"] if disp == "MEASURED" else None,
           "ABSTRACTION_ONLY_REPLICATED_POSITIVE": sec["positive"] if disp == "MEASURED" else None,
           "per_seed_selection": {s: {k: d[(s, k)]["selected_schema"] for k in gain} for s in seeds},
           "disposition": disp}
    (OUT / "T12_RESULT.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    R.log("T12 %s totals %s primary %s secondary %s null_sel %d memo %s" % (disp, tot, prim, sec, null_sel, memo))
    return res


if __name__ == "__main__":
    st = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    {"supply": lambda: stage_supply(w), "known": stage_known, "run": lambda: stage_run(w),
     "score": lambda: stage_score(w), "report": stage_report}[st]()
