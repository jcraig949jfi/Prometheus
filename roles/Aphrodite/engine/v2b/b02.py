"""BETA-02 (C-007): IMPROVER REPLICATION -> MECHANISM SPLIT -> R8. Pre-registration: beta02/BETA02_PREREG.md.

E1  Higher-powered fresh-seed replication of T12 (g11 @ O10 vs I_0 @ O4) on W8 LIN 24-47 (never used).
E2  Factorial on the same seeds: selection rule {g0 = I_0, g0x = I_0 minus MEMORISE, g10, g11 = g10 minus MEMORISE}
    x observation width {O4, O10}. Validation breadth is 12 throughout, as in T12.
E3  R8 (executed only if the pre-registered replication gate passes). The donor libraries are E1's g11_O10 and
    g0_O4 selections. They are frozen + hashed and transplanted (entries only) into fresh next-generation improvers on
    UNSEEN W8 LIN seeds 48-71 (pair i: donor 24+i -> next 48+i). Machinery is identical across arms. Endpoint: the
    NEXT generation's improvement over its own inherited library.

Every T12 instrument is unchanged: escrow 30k, cap 1M, T4 v1a tribunal, endpoint, A19 role rule, the T12 extras
seeding strings, R_VAL C1, and gtc genomes (sha e097e1d4).
Stages:
  supply {E|R8} [w]         foundry + roles + extras for the seed block
  known                     pre-freeze known answers K0-K4 (outcome-free)
  e12 run|score [w], e12 report
  r8 run|score [w], r8 report   (refuses unless the E12 result shows REPLICATION_GATE = PASS)
"""
import os
os.environ.setdefault("V2B_T51_DIR", "T04_T51")
import hashlib  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402

import r7e as R  # noqa: E402
import identity as I  # noqa: E402
import t10_observe as T10  # noqa: E402

T = R.T
B02 = R.RUNS.parent.parent / "beta02" / "runs"
W8 = T.W8
SUPPLY_FILE = W8 / "W8_SUPPLIES_B02.json"
SUP = B02 / "SUPPLY"
E12 = B02 / "E12"
R8D = B02 / "R8"
BLOCKS = {"E": list(range(24, 48)), "R8": list(range(48, 72))}
EXTRA_VAL, EXTRA_OBS = 8, 6
EXCLUDE = "MEMORISE"
# rule -> (gtc genome, MEMORISE excluded?)
RULES = {"g0": ("g0", False), "g0x": ("g0", True), "g10": ("g10", False), "g11": ("g10", True),
         "NULL11": ("NULL10", True), "NULL0x": ("NULL", True)}
E12_ARMS = [(r, w) for r in ("g0", "g0x", "g10", "g11") for w in ("O4", "O10")] + [("NULL11", "O10"), ("NULL0x", "O10")]
R8_LIBS = ["L_g11", "L_I0", "L_P"]
R8_MACH = [("g0", "O4"), ("g11", "O10")]          # primary machinery first (I_0), secondary g11
MIN_SEEDS = 20
NULL_MAX = 2


def log(m):
    print("[B02 %s] %s" % (time.strftime("%H:%M:%S", time.gmtime()), m), flush=True)


def wj(p, o):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(o, indent=1, default=str), encoding="utf-8")


def rj(p):
    return json.loads(p.read_text(encoding="utf-8"))


def sha(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()


# ------------------------------------------------------------------ supply (T51 foundry + A19 roles + T12 extras)
def _qual(d):
    return T._qual(d)


def stage_supply(block, w=4):
    seeds = BLOCKS[block]
    sup = rj(SUPPLY_FILE)
    draws = [(n, b, i, f, "LIN:%d" % s) for s in seeds for n, i, b, f in sup["LIN:%d" % s]["families"]]
    fpath = SUP / "FOUNDRY.jsonl"
    SUP.mkdir(parents=True, exist_ok=True)
    done = {x["name"] for x in R.rdl(fpath)}
    todo = [d for d in draws if d[0] not in done]
    log("supply %s: foundry todo %d of %d" % (block, len(todo), len(draws)))
    with open(fpath, "a", encoding="utf-8") as fh, ProcessPoolExecutor(max_workers=w, initializer=T.init_worker) as ex:
        for i, row in enumerate(ex.map(_qual, todo, chunksize=4)):
            fh.write(json.dumps(row, sort_keys=True, default=str) + "\n")
            fh.flush()
            if i % 200 == 0:
                log("foundry %d/%d" % (i, len(todo)))
    rows = R.rdl(fpath)
    panel = T.panel()
    plan = {s: plan_seed(rows, s, panel) for s in seeds}
    wj(SUP / ("PLAN_%s.json" % block), {"seeds": seeds, "panel": panel, "plan": plan,
                                       "supply_sha": sha([sup["LIN:%d" % s] for s in seeds])})
    log("supply %s: usable %d/%d" % (block, sum(p["ok"] for p in plan.values()), len(seeds)))


def plan_seed(rows, s, panel):
    """A19 roles (T.assign: OBSERVE 4, VALIDATE 4, TRANSFER 32) + T12's extras rule (VALIDATE +8, OBSERVE +6)."""
    fams, ok = T.assign(rows, s)
    keep = ("name", "role", "body", "init", "final", "Q2_size", "p_PRISTINE")
    base = [{k: f[k] for k in keep} for f in fams]
    return dict(extras(rows, s, base, "APHRODITE/T12/VAL/%d", "APHRODITE/T12/OBS/%d"), roles_ok=ok,
                ok=ok and True)


def extras(rows, s, base, val_tag, obs_tag):
    keep = ("name", "body", "init", "final", "Q2_size", "p_PRISTINE")
    used = {f["name"] for f in base}
    q = sorted([x for x in rows if x.get("T4_qualified") and x["source"] == "LIN:%d" % s
                and x.get("p_PRISTINE", 0) <= 0.75 and x["name"] not in used], key=lambda x: x["name"])
    rng = random.Random(I._seed(val_tag % s))
    rng.shuffle(q)
    val = [dict({k: x[k] for k in keep}, role="VALIDATE") for x in q[:EXTRA_VAL]]
    used |= {f["name"] for f in val}
    fl = sorted([x for x in rows if x.get("T4_qualified") and x["source"] == "LIN:%d" % s
                 and 0 < x.get("p_PRISTINE", 0) <= 0.75 and x["name"] not in used], key=lambda x: x["name"])
    rng = random.Random(I._seed(obs_tag % s))
    rng.shuffle(fl)
    obs = [dict({k: x[k] for k in keep}, role="OBSERVE") for x in fl[:EXTRA_OBS]]
    ok = len(val) == EXTRA_VAL and len(obs) == EXTRA_OBS
    return {"seed": s, "extras_ok": ok, "O4": base + val, "O10": base + val + obs}


# ------------------------------------------------------------------ donors (per-job selector state; no cross-job leak)
_ORIG = {}


def _set_rule(rule):
    import a17
    import gtc
    if not _ORIG:
        _ORIG["a17"], _ORIG["sub"] = a17.select, gtc._select_subset
    excl = RULES[rule][1]
    if excl:
        oa, os_ = _ORIG["a17"], _ORIG["sub"]
        a17.select = lambda c, st, cells: oa({k: v for k, v in c.items() if k != EXCLUDE}, st, cells)
        gtc._select_subset = lambda c, st, cells: os_({k: v for k, v in c.items() if k != EXCLUDE}, st, cells)
    else:
        a17.select, gtc._select_subset = _ORIG["a17"], _ORIG["sub"]


def _donor(a):
    """a = (tag, rule, width, seed, fams, panel, start_entries or None). Mirrors r7e._donor (+ optional transplant)."""
    tag, rule, width, s, fams, panel, start = a
    T.init_worker()
    import a17
    import a18_c1
    import gtc
    a17.R_VAL = a18_c1.R_VAL_C1
    _set_rule(rule)
    fl = [dict(f, qualified_dev_size=f["Q2_size"]) for f in fams]
    specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in fl}
    args = ("LIN%d" % s, "P", s, fl, specs, panel, True) + ((start,) if start is not None else ())
    r = gtc.donor_g(RULES[rule][0], args)
    _set_rule("g0")
    return {"tag": tag, "rule": rule, "width": width, "seed": s, "selected": r["selected"],
            "selected_schema": r["selected_schema"], "selected_origin": r["selected_origin"],
            "selected_entries": r["selected_entries"], "n_observed": r["n_observed"], "n_derived": r["n_derived"],
            "classes": r["classes"], "seconds": r["seconds"],
            "memorise_selected": r["selected"] == EXCLUDE}


def _pool_donors(jobs, out, w, label):
    done = {(x["tag"], x["seed"]) for x in R.rdl(out)}
    jobs = [j for j in jobs if (j[0], j[3]) not in done]
    log("%s donor jobs %d" % (label, len(jobs)))
    with open(out, "a", encoding="utf-8") as fh, ProcessPoolExecutor(max_workers=w, initializer=T.init_worker) as ex:
        for r in ex.map(_donor, jobs):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            log("seed %d %-10s sel=%s via=%s" % (r["seed"], r["tag"], r["selected_schema"], r["selected"]))


def _pool_walks(todo, out, w, label):
    done = {(x["lib"], x["family"], x["cell"]) for x in R.rdl(out)}
    todo = [v for v in todo if (v[0], v[2]["name"], v[3]) not in done]
    log("%s walks todo %d" % (label, len(todo)))
    with open(out, "a", encoding="utf-8") as fh, ProcessPoolExecutor(max_workers=w, initializer=T.init_worker) as ex:
        for n, r in enumerate(ex.map(R._walk, todo, chunksize=2)):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            if n % 500 == 0:
                log("walks %d/%d" % (n, len(todo)))


def _key(entries, libs):
    k = hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()[:16]
    libs.setdefault(k, entries)
    return k


def _tr(plan_row, s):
    return [dict(f, seed="LIN%d" % s) for f in plan_row["O4"] if f["role"] == "TRANSFER"]


# ------------------------------------------------------------------ exact statistics
def flip_dist(d):
    """Exact sign-flip null distribution of sum(+-|d_i|) over integer d (zeros drop out): {sum: count}."""
    dist = {0: 1}
    for x in (abs(int(v)) for v in d if v != 0):
        nd = {}
        for s, c in dist.items():
            nd[s + x] = nd.get(s + x, 0) + c
            nd[s - x] = nd.get(s - x, 0) + c
        dist = nd
    return dist


def flip_test(d):
    nz = [int(v) for v in d if v != 0]
    obs = sum(nz)
    dist = flip_dist(nz)
    tot = 2 ** len(nz)
    p1 = sum(c for s, c in dist.items() if s >= obs) / tot
    p2 = sum(c for s, c in dist.items() if abs(s) >= abs(obs)) / tot
    return {"n": len(d), "nonzero": len(nz), "sum": obs, "mean": round(sum(d) / len(d), 3) if d else None,
            "median": statistics.median(d) if d else None, "better": sum(v > 0 for v in d),
            "worse": sum(v < 0 for v in d), "tied": sum(v == 0 for v in d), "p_one_sided": round(p1, 6),
            "p_two_sided": round(p2, 6), "attainable_min_p": round(1 / tot, 8), "diffs": list(d)}


def holm(ps, alpha=0.05):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    rej, m = [False] * len(ps), len(ps)
    for k, i in enumerate(order):
        if ps[i] <= alpha / (m - k):
            rej[i] = True
        else:
            break
    return rej


# ------------------------------------------------------------------ E1/E2
def e12_run(w=4):
    P = rj(SUP / "PLAN_E.json")
    seeds = [s for s in P["seeds"] if P["plan"][str(s)]["ok"] and P["plan"][str(s)]["extras_ok"]]
    E12.mkdir(parents=True, exist_ok=True)
    wj(E12 / "E12_SEEDS.json", {"seeds": seeds, "n": len(seeds)})
    jobs = [("%s_%s" % (r, wd), r, wd, s, P["plan"][str(s)][wd], P["panel"], None) for s in seeds for r, wd in E12_ARMS]
    _pool_donors(jobs, E12 / "E12_DONORS.jsonl", w, "E12")


def e12_score(w=4):
    P = rj(SUP / "PLAN_E.json")
    seeds = rj(E12 / "E12_SEEDS.json")["seeds"]
    libs, index, todo = {}, [], {}
    PR = _key(R.FR.pristine().entries, libs)
    for x in R.rdl(E12 / "E12_DONORS.jsonl"):
        k = _key(x["selected_entries"], libs)
        for f in _tr(P["plan"][str(x["seed"])], x["seed"]):
            for ci in range(2):
                index.append({"seed": x["seed"], "genome": x["tag"], "family": f["name"], "cell": ci, "lib": k})
                todo.setdefault((k, f["name"], ci), (k, libs[k], f, ci))
    for s in seeds:
        for f in _tr(P["plan"][str(s)], s):
            for ci in range(2):
                index.append({"seed": s, "genome": "PRISTINE", "family": f["name"], "cell": ci, "lib": PR})
                todo.setdefault((PR, f["name"], ci), (PR, libs[PR], f, ci))
    wj(E12 / "E12_INDEX.json", {"index": index})
    _pool_walks(list(todo.values()), E12 / "E12_WALKS.jsonl", w, "E12")


def _gains(idx, W, ref_genome, genomes, seeds):
    """Per-seed count of families reached (qualified, <= cap, >= 1 of 2 cells) by `genome` where its reference
    library (ref_genome(entry): PRISTINE for E12, the entry's own inherited START for R8) is censored in that cell."""
    ok = lambda r: bool(r) and not r.get("censored", True)  # noqa: E731
    lib_of = {(e["genome"], e["seed"], e["family"], e["cell"]): e["lib"] for e in idx}
    out = {}
    for g in genomes:
        hit = {s: set() for s in seeds}
        for e in idx:
            if e["genome"] != g:
                continue
            r = W.get((e["lib"], e["family"], e["cell"]))
            p = W.get((lib_of[(ref_genome(e), e["seed"], e["family"], e["cell"])], e["family"], e["cell"]))
            if ok(r) and not ok(p):
                hit[e["seed"]].add(e["family"])
        out[g] = {s: len(hit[s]) for s in seeds}
    return out


def e12_report():
    """Frozen rules: BETA02_PREREG.md s3-s4."""
    known = rj(B02 / "KNOWN.json")
    seeds = rj(E12 / "E12_SEEDS.json")["seeds"]
    W = {(x["lib"], x["family"], x["cell"]): x["result"] for x in R.rdl(E12 / "E12_WALKS.jsonl")}
    idx = rj(E12 / "E12_INDEX.json")["index"]
    arms = ["%s_%s" % a for a in E12_ARMS]
    G = _gains(idx, W, lambda e: "PRISTINE", arms, seeds)
    D = {(x["seed"], x["tag"]): x for x in R.rdl(E12 / "E12_DONORS.jsonl")}
    tot = {a: sum(G[a].values()) for a in arms}
    c = lambda a, b: [G[a][s] - G[b][s] for s in seeds]  # noqa: E731

    def planted(tag):
        return sum(1 for s in seeds if (D[(s, tag)].get("selected_origin") or "").startswith("PLANTED"))
    null = {"NULL11_O10": {"planted_selected": planted("NULL11_O10"), "total": tot["NULL11_O10"], "vs": tot["g11_O10"]},
            "NULL0x_O10": {"planted_selected": planted("NULL0x_O10"), "total": tot["NULL0x_O10"], "vs": tot["g0x_O10"]}}
    gate_null = all(v["planted_selected"] <= NULL_MAX and v["total"] <= v["vs"] + 2 for v in null.values())
    supply_ok = len(seeds) >= MIN_SEEDS
    gate = known["pass"] and gate_null
    e1 = flip_test(c("g11_O10", "g0_O4"))
    e1["totals"] = {"g11_O10": tot["g11_O10"], "g0_O4": tot["g0_O4"]}
    e1["positive"] = e1["p_one_sided"] < 0.05 and e1["sum"] > 0
    # E2: g11/g10 family (primary) and g0x/g0 family (robustness); per-seed contrasts
    ex10, ex4 = c("g11_O10", "g10_O10"), c("g11_O4", "g10_O4")
    w11, w10 = c("g11_O10", "g11_O4"), c("g10_O10", "g10_O4")
    excl = [(a + b) / 2 for a, b in zip(ex10, ex4)]
    width = [(a + b) / 2 for a, b in zip(w11, w10)]
    inter = [a - b for a, b in zip(ex10, ex4)]
    x2 = lambda v: [int(round(2 * x)) for x in v]  # noqa: E731   (exact test on 2x the half-sums: same p)
    e2 = {"MEMORISE_EXCLUSION_EFFECT": flip_test(x2(excl)), "OBSERVATION_WIDTH_EFFECT": flip_test(x2(width)),
          "INTERACTION": flip_test(inter)}
    for k, v in e2.items():
        v["note"] = "per-seed contrast; diffs are 2x the averaged contrast" if k != "INTERACTION" else "per-seed contrast"
    rej = holm([e2[k]["p_two_sided"] for k in e2])
    for k, r in zip(e2, rej):
        e2[k]["holm_reject_0.05"] = r
    cells = {"EXCL_at_O10": flip_test(ex10), "EXCL_at_O4": flip_test(ex4), "WIDTH_g11": flip_test(w11),
             "WIDTH_g10": flip_test(w10), "CRITERION_g10_vs_g0_O4": flip_test(c("g10_O4", "g0_O4")),
             "CRITERION_g10_vs_g0_O10": flip_test(c("g10_O10", "g0_O10")),
             "EXCL_I0_at_O4_g0x_vs_g0": flip_test(c("g0x_O4", "g0_O4")),
             "EXCL_I0_at_O10_g0x_vs_g0": flip_test(c("g0x_O10", "g0_O10")),
             "g11_O4_vs_g0_O4": flip_test(c("g11_O4", "g0_O4"))}
    g11_only_at_O10 = (cells["EXCL_at_O10"]["p_one_sided"] < 0.05 and cells["EXCL_at_O10"]["sum"] > 0
                       and not (cells["EXCL_at_O4"]["p_one_sided"] < 0.05 and cells["EXCL_at_O4"]["sum"] > 0))
    memo = {a: [s for s in seeds if D[(s, a)]["memorise_selected"]] for a in arms}
    disp = "SUPPLY_LIMITED" if not supply_ok else ("MEASURED" if gate else "MEASUREMENT_FAILED")
    rgate = disp == "MEASURED" and e1["positive"]
    res = {"seeds": seeds, "n_seeds": len(seeds), "gains": G, "totals": tot, "known": known, "null_gate": null,
           "gate": gate, "E1_IMPROVER_REPLICATED": e1, "E1_POSITIVE": e1["positive"] if disp == "MEASURED" else None,
           "E2": e2, "E2_cells": cells, "G11_ONLY_WORKS_AT_O10": g11_only_at_O10 if disp == "MEASURED" else None,
           "memorise_selected_seeds": memo,
           "selections": {s: {a: D[(s, a)]["selected_schema"] or D[(s, a)]["selected"] for a in arms} for s in seeds},
           "REPLICATION_GATE": "PASS" if rgate else "FAIL", "disposition": disp}
    wj(E12 / "E12_RESULT.json", res)
    log("E12 %s gate=%s E1 %s/%s/%s sum %s p1 %s; REPLICATION_GATE %s" % (
        disp, gate, e1["better"], e1["worse"], e1["tied"], e1["sum"], e1["p_one_sided"], res["REPLICATION_GATE"]))
    return res


# ------------------------------------------------------------------ E3 / R8
def _gate_or_die():
    res = rj(E12 / "E12_RESULT.json")
    if res["REPLICATION_GATE"] != "PASS":
        raise SystemExit("R8 refused: REPLICATION_GATE = %s (pre-registered)" % res["REPLICATION_GATE"])
    return res


def r8_freeze_libraries():
    """Extract ONLY the selected entries of E1's g11_O10 and g0_O4 donors -> hashed library files. No other state."""
    _gate_or_die()
    seeds = rj(E12 / "E12_SEEDS.json")["seeds"]
    D = {(x["seed"], x["tag"]): x for x in R.rdl(E12 / "E12_DONORS.jsonl")}
    libs = {}
    for s in seeds:
        libs[str(s)] = {"L_g11": D[(s, "g11_O10")]["selected_entries"], "L_I0": D[(s, "g0_O4")]["selected_entries"],
                        "L_P": R.FR.pristine().entries}
    rec = {"libraries": libs, "sha256": {s: {k: sha(v) for k, v in d.items()} for s, d in libs.items()}}
    wj(R8D / "R8_LIBRARIES.json", rec)
    log("R8 libraries frozen: %d donor seeds; file sha %s" % (len(libs), sha(rec)[:16]))


def r8_run(w=4):
    _gate_or_die()
    if not (R8D / "R8_LIBRARIES.json").exists():
        r8_freeze_libraries()
    L = rj(R8D / "R8_LIBRARIES.json")
    for s, d in L["libraries"].items():                  # integrity: the hashes must still match
        assert all(sha(d[k]) == L["sha256"][s][k] for k in d), "library hash mismatch"
    P = rj(SUP / "PLAN_R8.json")
    pairs = [(int(s), int(s) + 24) for s in L["libraries"]
             if P["plan"].get(str(int(s) + 24), {}).get("ok") and P["plan"][str(int(s) + 24)]["extras_ok"]]
    wj(R8D / "R8_PAIRS.json", {"pairs": pairs, "n": len(pairs)})
    jobs = []
    for d, n in pairs:
        for lib in R8_LIBS:
            for rule, wd in R8_MACH:
                jobs.append(("%s|%s_%s" % (lib, rule, wd), rule, wd, n, P["plan"][str(n)][wd], P["panel"],
                             L["libraries"][str(d)][lib]))
    _pool_donors(jobs, R8D / "R8_DONORS.jsonl", w, "R8")


def r8_score(w=4):
    P = rj(SUP / "PLAN_R8.json")
    L = rj(R8D / "R8_LIBRARIES.json")
    pairs = rj(R8D / "R8_PAIRS.json")["pairs"]
    nxt = {n: d for d, n in pairs}
    libs, index, todo = {}, [], {}
    for x in R.rdl(R8D / "R8_DONORS.jsonl"):
        n = x["seed"]
        lib = x["tag"].split("|")[0]
        k_sel = _key(x["selected_entries"], libs)
        k_start = _key(L["libraries"][str(nxt[n])][lib], libs)
        for f in _tr(P["plan"][str(n)], n):
            for ci in range(2):
                index.append({"seed": n, "genome": x["tag"], "family": f["name"], "cell": ci, "lib": k_sel,
                              "start": "START|" + lib})
                todo.setdefault((k_sel, f["name"], ci), (k_sel, libs[k_sel], f, ci))
                index.append({"seed": n, "genome": "START|" + lib, "family": f["name"], "cell": ci, "lib": k_start})
                todo.setdefault((k_start, f["name"], ci), (k_start, libs[k_start], f, ci))
    seen, uniq = set(), []
    for e in index:
        t = (e["seed"], e["genome"], e["family"], e["cell"])
        if t not in seen:
            seen.add(t)
            uniq.append(e)
    wj(R8D / "R8_INDEX.json", {"index": uniq})
    _pool_walks(list(todo.values()), R8D / "R8_WALKS.jsonl", w, "R8")


def r8_report():
    """Frozen rules: BETA02_PREREG.md s5."""
    pairs = rj(R8D / "R8_PAIRS.json")["pairs"]
    seeds = [n for _d, n in pairs]
    W = {(x["lib"], x["family"], x["cell"]): x["result"] for x in R.rdl(R8D / "R8_WALKS.jsonl")}
    idx = rj(R8D / "R8_INDEX.json")["index"]
    tags = ["%s|%s_%s" % (lib, r, wd) for lib in R8_LIBS for r, wd in R8_MACH]
    starts = ["START|" + lib for lib in R8_LIBS]
    imp = _gains(idx, W, lambda e: e.get("start", e["genome"]), tags, seeds)   # gain over OWN inherited library
    cap_start = _gains([dict(e, start="START|L_P") for e in idx], W, lambda e: "START|L_P", starts, seeds)
    out = {}
    for rule, wd in R8_MACH:
        m = "%s_%s" % (rule, wd)
        prim = flip_test([imp["L_g11|" + m][s] - imp["L_I0|" + m][s] for s in seeds])
        prim["positive"] = prim["p_one_sided"] < 0.05 and prim["sum"] > 0
        out[m] = {"R8_improvement_L_g11_vs_L_I0": prim,
                  "improvement_L_g11_vs_L_P": flip_test([imp["L_g11|" + m][s] - imp["L_P|" + m][s] for s in seeds]),
                  "improvement_L_I0_vs_L_P": flip_test([imp["L_I0|" + m][s] - imp["L_P|" + m][s] for s in seeds]),
                  "totals": {lib: sum(imp["%s|%s" % (lib, m)].values()) for lib in R8_LIBS}}
    res = {"pairs": pairs, "next_gen_improvement": imp, "inherited_library_capability_vs_pristine": cap_start,
           "by_machinery": out, "R8_PASS": out["g0_O4"]["R8_improvement_L_g11_vs_L_I0"]["positive"],
           "R8_PASS_secondary_g11_machinery": out["g11_O10"]["R8_improvement_L_g11_vs_L_I0"]["positive"]}
    wj(R8D / "R8_RESULT.json", res)
    log("R8 primary %s ; secondary %s" % (out["g0_O4"]["R8_improvement_L_g11_vs_L_I0"],
                                          out["g11_O10"]["R8_improvement_L_g11_vs_L_I0"]["positive"]))
    return res


# ------------------------------------------------------------------ known answers (outcome-free; before freeze)
def stage_known():
    res = {}
    # K0: plan_seed/extras on T12's supply reproduce T12_ROLES (O4 and O10 family lists) exactly
    rows = R.rdl(R.RUNS / "T12_T51" / "T51_FOUNDRY.jsonl")
    t12 = {p["seed"]: p for p in rj(R.RUNS / "T12_REPL" / "T12_ROLES.json")}
    pn = rj(R.RUNS / "T12_T51" / "T51_PLAN.json")["panel"]
    mine = {s: plan_seed(rows, s, pn) for s in t12}
    res["K0_plan_reproduces_T12_roles"] = all(mine[s]["O4"] == t12[s]["O4"] and mine[s]["O10"] == t12[s]["O10"]
                                              for s in t12)
    # K1/K2/K3: one worker, sequence g11 -> g0 -> g0x -> g0 -> transplant(pristine) on T12 seed 17
    T12D = {(x["seed"], "%s_%s" % (x["genome"], x["obs"])): x for x in R.rdl(R.RUNS / "T12_REPL" / "T12_DONORS.jsonl")}
    s = 17
    seq = [("a", "g11", "O10", None), ("b", "g0", "O4", None), ("c", "g0x", "O4", None), ("d", "g0", "O4", None),
           ("e", "g0", "O4", R.FR.pristine().entries)]
    jobs = [(t, r, wd, s, t12[s][wd], pn, st) for t, r, wd, st in seq]
    with ProcessPoolExecutor(max_workers=1, initializer=T.init_worker) as ex:
        out = {r["tag"]: r for r in ex.map(_donor, jobs)}
    keys = ("selected_schema", "selected_origin", "selected_entries", "n_observed", "n_derived", "classes")
    same = lambda a, ref: all(a[k] == ref[k] for k in keys)  # noqa: E731
    res["K1_g11_O10_reproduces_T12"] = same(out["a"], T12D[(s, "g11_O10")])
    res["K1_g0_O4_reproduces_T12"] = same(out["b"], T12D[(s, "g0_O4")])
    res["K2_g0x_excludes_MEMORISE"] = (not out["c"]["memorise_selected"]) and out["b"]["memorise_selected"]
    res["K2_g0_after_g0x_reproduces_T12"] = same(out["d"], T12D[(s, "g0_O4")])
    res["K3_transplant_pristine_equals_plain_P"] = same(out["e"], T12D[(s, "g0_O4")])
    # K4: DP sign-flip == brute force (T12 diffs and 200 random integer vectors)
    def brute(d):
        nz = [x for x in d if x]
        obs = sum(nz)
        return sum(1 for sg in itertools.product((1, -1), repeat=len(nz))
                   if sum(a * abs(x) for a, x in zip(sg, nz)) >= obs) / 2 ** len(nz) if nz else 1.0
    rng = random.Random(7)
    vecs = [[0, 12, 0, 4, 4, 15, 0, 5]] + [[rng.randint(-6, 9) for _ in range(rng.randint(1, 12))] for _ in range(200)]
    res["K4_exact_flip_matches_bruteforce"] = all(abs(flip_test(v)["p_one_sided"] - brute(v)) < 1e-6 for v in vecs)
    # K5: the reducer (_gains) on T12's index + walks reproduces T12_RESULT's per-seed gains
    t12r = rj(R.RUNS / "T12_REPL" / "T12_RESULT.json")
    W12 = {(x["lib"], x["family"], x["cell"]): x["result"] for x in R.rdl(R.RUNS / "T12_REPL" / "T12_WALKS.jsonl")}
    i12 = rj(R.RUNS / "T12_REPL" / "T12_INDEX.json")["index"]
    g12 = _gains(i12, W12, lambda e: "PRISTINE", list(t12r["gain"]), t12r["seeds"])
    res["K5_reducer_reproduces_T12_gains"] = all(g12[a][s] == t12r["gain"][a][str(s)] for a in g12 for s in t12r["seeds"])
    res["pass"] = all(v for k, v in res.items() if k.startswith("K"))
    wj(B02 / "KNOWN.json", res)
    log("known %s" % res)
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    w = int(a[-1]) if a and a[-1].isdigit() else 4
    if a[0] == "supply":
        stage_supply(a[1], w)
    elif a[0] == "known":
        stage_known()
    elif a[0] == "e12":
        {"run": lambda: e12_run(w), "score": lambda: e12_score(w), "report": e12_report}[a[1]]()
    elif a[0] == "r8":
        {"freeze": r8_freeze_libraries, "run": lambda: r8_run(w), "score": lambda: r8_score(w),
         "report": r8_report}[a[1]]()
    else:
        raise SystemExit("unknown stage")
