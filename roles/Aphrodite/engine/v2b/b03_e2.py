"""BETA-03 E2: g12 ENDPOINT-ALIGNED SELECTOR -- fresh-seed confirmation. Pre-registration: beta03/windows/E2_PREREG.md.

Seeds: block A (W8 LIN 72-95, Beta-03 supply; never used in Beta-01/02). Width O10, validation breadth 12, PRISTINE start.
Arms:
  I_0 @ O10   b02._donor rule g0           (new rows, this runner)
  g11 @ O10   b02._donor rule g11          (REUSED from E1 donors: identical job, same seeds/roles/code)
  g12 @ O10   g12.donor12 mode 'g12'       one job per seed scores every candidate once; the arms
              g12 / NULL12 (OFF plant) / MEMO12 (memorised plant) / NEAR12 (near-miss plant) are picks over that table
Endpoint: Beta-02 E1 endpoint (held-out TRANSFER families reached at <= 1M, >= 1 of 2 cells, PRISTINE censored).
Stages: run [w] | score [w] | report
"""
import os
os.environ.setdefault("V2B_T51_DIR", "T04_T51")
import json  # noqa: E402
import sys  # noqa: E402

import b03  # noqa: E402   (imports b02 first: a18.TAG import-order guard)
import b02  # noqa: E402
import g12  # noqa: E402

R = b02.R
E2D = b03.B03 / "E2"
E1D = b03.E1D
G12_ARMS = ["g12", "NULL12", "MEMO12", "NEAR12"]
TRAP_MAX = 2
NONINF_RATIO = 0.9
log, wj, rj = b02.log, b02.wj, b02.rj


def _seeds():
    P = rj(b02.SUP / "PLAN_A.json")
    return P, [s for s in P["seeds"] if P["plan"][str(s)]["ok"] and P["plan"][str(s)]["extras_ok"]]


def run(w=4):
    from concurrent.futures import ProcessPoolExecutor
    P, seeds = _seeds()
    E2D.mkdir(parents=True, exist_ok=True)
    out = E2D / "E2_DONORS.jsonl"
    done = {(x["tag"], x["seed"]) for x in R.rdl(out)}
    jobs = []
    for s in seeds:
        fams = P["plan"][str(s)]["O10"]
        if ("g12_job", s) not in done:
            jobs.append(("g12", ("g12_job", "g12", "O10", s, fams, P["panel"], None)))
        if ("g0_O10", s) not in done:
            jobs.append(("b02", ("g0_O10", "g0", "O10", s, fams, P["panel"], None)))
    log("E2 donor jobs %d" % len(jobs))
    with open(out, "a", encoding="utf-8") as fh, ProcessPoolExecutor(max_workers=w, initializer=R.T.init_worker) as ex:
        for r in ex.map(g12.run_job, jobs):
            if r.get("g12"):
                r["g12"].pop("walks", None)          # keep receipts compact; tables + arm entries retained
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            log("seed %d %s sel=%s arms=%s" % (r["seed"], r["tag"], r["selected_schema"],
                                               {a: v["chosen"] for a, v in r.get("g12", {}).get("arms", {}).items()}))


def _arm_libs():
    """seed -> arm -> entries. g11 rows come from E1 donors (identical job)."""
    D = {(x["seed"], x["tag"]): x for x in R.rdl(E2D / "E2_DONORS.jsonl")}
    E1 = {(x["seed"], x["tag"]): x for x in R.rdl(E1D / "E1_DONORS.jsonl")}
    _P, seeds = _seeds()
    libs = {}
    for s in seeds:
        if (s, "g12_job") not in D or (s, "g0_O10") not in D or (s, "g11_O10") not in E1:
            continue
        g = D[(s, "g12_job")]["g12"]
        libs[s] = {"I0_O10": D[(s, "g0_O10")]["selected_entries"], "g11_O10": E1[(s, "g11_O10")]["selected_entries"]}
        for a in G12_ARMS:
            libs[s][a] = g["arm_entries"][a]
    return libs


def score(w=4):
    P, _seeds_ = _seeds()
    libs = _arm_libs()
    keys, index, todo = {}, [], {}
    PR = b02._key(R.FR.pristine().entries, keys)
    for s, arms in libs.items():
        for f in b02._tr(P["plan"][str(s)], s):
            for ci in range(2):
                index.append({"seed": s, "genome": "PRISTINE", "family": f["name"], "cell": ci, "lib": PR})
                todo.setdefault((PR, f["name"], ci), (PR, keys[PR], f, ci))
                for a, ent in arms.items():
                    k = b02._key(ent, keys)
                    index.append({"seed": s, "genome": a, "family": f["name"], "cell": ci, "lib": k})
                    todo.setdefault((k, f["name"], ci), (k, keys[k], f, ci))
    wj(E2D / "E2_INDEX.json", {"index": index})
    b02._pool_walks(list(todo.values()), E2D / "E2_WALKS.jsonl", w, "E2")


def report():
    """Frozen rules: beta03/windows/E2_PREREG.md s5."""
    libs = _arm_libs()
    seeds = sorted(libs)
    W = {(x["lib"], x["family"], x["cell"]): x["result"] for x in R.rdl(E2D / "E2_WALKS.jsonl")}
    idx = rj(E2D / "E2_INDEX.json")["index"]
    arms = ["I0_O10", "g11_O10"] + G12_ARMS
    G = b02._gains(idx, W, lambda e: "PRISTINE", arms, seeds)
    tot = {a: sum(G[a].values()) for a in arms}
    D = {(x["seed"], x["tag"]): x for x in R.rdl(E2D / "E2_DONORS.jsonl")}
    E1 = {(x["seed"], x["tag"]): x for x in R.rdl(E1D / "E1_DONORS.jsonl")}
    g = {s: D[(s, "g12_job")]["g12"] for s in seeds}
    chosen = {s: {a: g[s]["arms"][a]["chosen"] for a in G12_ARMS} for s in seeds}
    plant = {a: sum(1 for s in seeds if g[s]["arms"][a]["plant_selected"]) for a in ("NULL12", "MEMO12", "NEAR12")}
    natural_memo = sum(1 for s in seeds if chosen[s]["g12"] == "MEMORISE")
    g12_nonref = sum(1 for s in seeds if chosen[s]["g12"] != g12.REF)
    g11_nonref = sum(1 for s in seeds if E1[(s, "g11_O10")]["selected"] != "INHERITED")
    # near-miss attractiveness (descriptive): eligible under the recorded I_0 diagnostic table, if present
    near_attr = sum(1 for s in seeds if (g[s].get("i0_diag") or {}).get("table", {}).get("PLANT_NEAR", {})
                    .get("eligible"))
    c = lambda a, b: [G[a][s] - G[b][s] for s in seeds]  # noqa: E731
    vs_i0 = b02.flip_test(c("g12", "I0_O10"))
    vs_g11 = b02.flip_test(c("g12", "g11_O10"))
    g11_gt = b02.flip_test(c("g11_O10", "g12"))["p_one_sided"]
    holm = b02.holm([vs_i0["p_one_sided"], min(vs_g11["p_one_sided"], g11_gt)])
    traps_ok = all(v <= TRAP_MAX for v in plant.values()) and natural_memo <= TRAP_MAX
    non_elim = g12_nonref >= 0.5 * g11_nonref
    transfer_pos = vs_i0["p_one_sided"] < 0.05 and vs_i0["sum"] > 0
    if transfer_pos and traps_ok and non_elim:
        general = "YES"
    elif (vs_i0["sum"] <= 0) or not traps_ok or not non_elim:
        general = "NO"
    else:
        general = "INCONCLUSIVE"
    if vs_g11["p_one_sided"] < 0.05 and vs_g11["sum"] > 0:
        rel = "SUPERIOR"
    elif g11_gt < 0.05 and vs_g11["sum"] < 0:
        rel = "INFERIOR"
    elif tot["g12"] >= NONINF_RATIO * tot["g11_O10"]:
        rel = "NONINFERIOR"
    else:
        rel = "INCONCLUSIVE"
    supply_ok = len(seeds) >= b03.MIN_PAIRS
    res = {"seeds": seeds, "n": len(seeds), "gains": G, "totals": tot, "g12_choices": chosen,
           "traps": {"plant_selected_seeds": plant, "natural_MEMORISE_selected_by_g12": natural_memo,
                     "near_miss_attractive_under_I0_diag": near_attr, "pass": traps_ok},
           "non_eliminating": {"g12_nonINHERITED": g12_nonref, "g11_nonINHERITED": g11_nonref, "pass": non_elim},
           "g12_vs_I0_O10": vs_i0, "g12_vs_g11_O10": vs_g11, "g11_gt_g12_p_one_sided": g11_gt,
           "holm_[vsI0,vsg11]": holm, "G12_GENERAL_RULE": general if supply_ok else "SUPPLY_LIMITED",
           "G12_VS_G11": rel if supply_ok else "SUPPLY_LIMITED", "params": g12.params()}
    wj(E2D / "E2_RESULT.json", res)
    log("E2 G12_GENERAL_RULE %s G12_VS_G11 %s totals %s" % (res["G12_GENERAL_RULE"], res["G12_VS_G11"], tot))
    return res


def known():
    """K4 (outcome-free on confirmation supply): via THIS runner's import path, a g12 job on EXPOSED Beta-02 seed 26
    (PLAN_E roles, O10) reproduces the selector lead's smoke receipt: arm choices and the S/eligible table."""
    from concurrent.futures import ProcessPoolExecutor
    PE = rj(b03.ROOT / "beta02" / "runs" / "SUPPLY" / "PLAN_E.json")
    ref = [json.loads(x) for x in open(os.path.join(os.path.dirname(__file__), "receipts",
                                                    "G12_DEV_SMOKE_EXPOSED_2026-10-08.jsonl")) if x.strip()]
    ref = {r["seed"]: r for r in ref}[26]
    job = ("g12", ("g12_job", "g12", "O10", 26, PE["plan"]["26"]["O10"], PE["panel"], None))
    with ProcessPoolExecutor(max_workers=1, initializer=R.T.init_worker) as ex:
        r = list(ex.map(g12.run_job, [job]))[0]
    arms_ok = {a: v["chosen"] for a, v in r["g12"]["arms"].items()} == {a: v["chosen"] for a, v in ref["g12"]["arms"].items()}
    tab_ok = all(r["g12"]["table"][k]["S"] == ref["g12"]["table"][k]["S"] and
                 r["g12"]["table"][k]["eligible"] == ref["g12"]["table"][k]["eligible"] for k in ref["g12"]["table"])
    res = {"K4_g12_reproduces_smoke_seed26_arms": arms_ok, "K4_g12_reproduces_smoke_seed26_table": tab_ok,
           "pass": arms_ok and tab_ok}
    wj(E2D / "E2_KNOWN.json", res)
    log("E2 known %s" % res)
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    w = int(a[-1]) if a and a[-1].isdigit() else 4
    {"run": lambda: run(w), "score": lambda: score(w), "report": report, "known": known}[a[0]]()
