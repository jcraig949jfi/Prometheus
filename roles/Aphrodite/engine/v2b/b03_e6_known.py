"""Known answers for the E6 attack runner (b03_e6.py). Outcome-free: SYNTHETIC fixtures + EXPOSED Beta-02 data only.
No E5-N or E1 outcome is read (none exists). <= 2 workers. Writes beta03/runs/E6/E6_KNOWN.json.

K6a  PLAIN filter is the identity on every exposed Beta-02 R8 library (G5-only; 20 pairs x 3) and removes exactly the
     non-G5 bodies of a synthetic W5P depth-2 entry.
K6b  SHAM swap mechanics: inherited id replaced by promote(sham schema) id everywhere in promoted-form entries;
     bodies == promote.instantiate(swapped schema); expansion == original expansion with the inherited schema
     replaced by the sham schema; non-promoted entries unchanged; SCHEMA_ALL-style multi-schema entry handled.
K6c  acquisition reducer used by E6 reproduces the W01 common-residual totals on exposed Beta-02 R8 data.
K6d  (d) supply plan step reproduces Beta-02 PLAN_R8 roles/extras for every R8 seed from the Beta-02 FOUNDRY rows.
K6e  (d) generator path: unchanged w8_lin.py into a scratch file reproduces W8_SUPPLIES_B03 LIN:72 exactly.
K6f  decision functions: DEPENDENCY_CONFIRMED (>= 2/3 BOTH) and unseen PASS rule truth tables.
K6g  NEGATIVE branch on synthetic receipts: every pre-registered link (CANDIDACY incl. REPRESENTATION, SELECTION with
     exact and bound-resolved eligibility, SEARCH_BUDGET, TRANSFER, NONE) and the global first broken link
     (MEASUREMENT, SUPPLY, CANDIDACY, SELECTION, SEARCH_BUDGET, STATISTICAL) + channel consistency.
K6h  label-scramble invariance on one EXPOSED pair: Beta-02 R8 L_g11|g11_O10 recipient library of seed 49, entry names
     scrambled, re-walked (cap 1M) on 4 family-cells: identical to the recorded R8 walk results.
K6i  POSITIVE branch end-to-end on a synthetic YES_PENDING_E6 fixture built on exposed R8 pair 25->49 (cap 30k):
     build -> walk -> report runs; attack libraries hash-checked; scramble invariance holds; decision computed.
K6j  unseen_report on synthetic receipts: PASS / FAIL as the rule says.
"""
import os
os.environ.setdefault("V2B_T51_DIR", "T04_T51")
import json  # noqa: E402
import shutil  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import b03_e6 as X  # noqa: E402   (imports b03 -> b02 first)

b02, b03, R = X.b02, X.b03, X.R
rj, wj, sha, rdl = b02.rj, b02.wj, b02.sha, R.rdl
B02R = b03.ROOT / "beta02" / "runs"
RES = {}


def _init():
    R.T.init_worker()
    import a18
    a18.use_world("W5")


def _w5p():
    import sys
    sys.path.insert(0, str(b03.ROOT / "engine"))
    from w5p import promote as W
    from w5p import donor as WD
    return W, WD


def _depth2_entry(inherited_entries, tmpl="(%s((v * {H})) - first)"):
    """A synthetic arm-D depth-2 selected entry built with the frozen W5P machinery (bookkeeping only)."""
    W, WD = _w5p()
    reg = WD.promote_start(inherited_entries)
    pid = sorted(reg)[0]
    s = tmpl % pid
    e = WD.schema_entry("g2_new", s, reg)
    p = W.Promoted.from_schema(s, reg, WD.entry_sha(e), "selected_entry")
    return e, reg, pid, p


# ------------------------------------------------------------------ K6a
def k6a():
    import a17
    g5 = set(a17.g5_bodies())
    L = rj(B02R / "R8" / "R8_LIBRARIES.json")["libraries"]
    ident = all(X.plain_library(v) == v for d in L.values() for v in d.values())
    inh = L["25"]["L_g11"]
    e, _reg, _pid, _p = _depth2_entry(inh)
    lib = [e] + inh
    out = X.plain_library(lib)
    nong5 = [b for b in e["bodies"] if b not in g5]
    ok = (out[1:] == inh and (not out or out[0]["bodies"] == [b for b in e["bodies"] if b in g5] or
                              not [b for b in e["bodies"] if b in g5]))
    RES["K6a_plain_identity_on_R8_libraries"] = ident
    RES["K6a_plain_removes_nonG5"] = ok and bool(nong5)
    RES["K6a_detail"] = {"synthetic_entry_bodies": len(e["bodies"]), "outside_G5": len(nong5)}


# ------------------------------------------------------------------ K6b
def k6b():
    W, WD = _w5p()
    P = rj(B02R / "SUPPLY" / "PLAN_R8.json")
    import a18
    sham_entries = a18.start_library("PA", P["panel"])[0]
    inh = rj(B02R / "R8" / "R8_LIBRARIES.json")["libraries"]["25"]["L_g11"]
    e, reg, pid, _p = _depth2_entry(inh)
    multi = {"name": "g2_new", "inits": e["inits"], "finals": e["finals"], "bodies": list(e["bodies"]),
             "schemas": ["(acc * {H})", "(first + %s({H}))" % pid]}
    lib = [e, multi] + inh
    out, det = X.sham_library(lib, [pid], sham_entries)
    sp = X.sham_primitive(sham_entries)
    s_new = out[0]["schema"]
    # expansion check by substitution at the term level: orig schema with P_inh -> P_sham, expanded, equals
    # orig expansion with the inherited schema text replaced by the sham schema text at the promoted node
    ref = W.to_src(W.expand_term(W.parse(e["schema"].replace(pid, sp.id)), {sp.id: sp}))
    exp_ok = W.expand(s_new, {sp.id: sp}) == ref and pid not in json.dumps(out[:2])
    b_ok = out[0]["bodies"] == W.instantiate(s_new, {sp.id: sp})
    m_ok = (out[1]["schemas"][0] == "(acc * {H})" and sp.id in out[1]["schemas"][1]
            and out[1]["bodies"] == list(dict.fromkeys(W.instantiate("(acc * {H})", {sp.id: sp})
                                                       + W.instantiate(out[1]["schemas"][1], {sp.id: sp}))))
    RES["K6b_sham_swap"] = bool(exp_ok and b_ok and m_ok and out[2:] == inh and sp.schema == "({H} + v)")
    RES["K6b_detail"] = {"inherited": pid, "sham": sp.id, "from": e["schema"], "to": s_new,
                         "bodies_before": len(e["bodies"]), "bodies_after": len(out[0]["bodies"])}


# ------------------------------------------------------------------ K6c
def k6c():
    diag = rj(b03.B03 / "W01_R8_COMMON_RESIDUAL_DIAG.json")
    rr = rj(B02R / "R8" / "R8_RESULT.json")
    seeds = [n for _d, n in rr["pairs"]]
    W = {(x["lib"], x["family"], x["cell"]): x["result"] for x in rdl(B02R / "R8" / "R8_WALKS.jsonl")}
    idx = rj(B02R / "R8" / "R8_INDEX.json")["index"]
    C = {str(k): v for k, v in diag["common_residual"].items()}
    ok = True
    for t in ("L_g11|g11_O10", "L_I0|g11_O10", "L_P|g11_O10"):
        ok &= sum(X.acquired(idx, W, C, t, n) for n in seeds) == diag["summary"]["acq_on_common_totals"][t]
    RES["K6c_reducer_reproduces_W01"] = bool(ok)


# ------------------------------------------------------------------ K6d / K6e
def k6d():
    rows = rdl(B02R / "SUPPLY" / "FOUNDRY.jsonl")
    P = rj(B02R / "SUPPLY" / "PLAN_R8.json")
    seeds = [int(s) for s in P["plan"]]
    mine = X.plan_from_rows(rows, seeds, P["panel"])
    RES["K6d_plan_reproduces_PLAN_R8"] = all(json.loads(json.dumps(mine[s])) == P["plan"][str(s)] for s in seeds)
    RES["K6d_seeds"] = len(seeds)


def k6e(tmp):
    out = Path(tmp) / "W8_GEN_CHECK.json"
    t0 = time.process_time()
    X.unseen_gen(seeds=[72], out_file=out)
    ref = rj(b02.W8 / "W8_SUPPLIES_B03.json")["LIN:72"]["families"]
    RES["K6e_generator_reproduces_LIN72"] = rj(out)["LIN:72"]["families"] == ref
    RES["K6e_cpu_note"] = "subprocess (2-proc pool) wall-timed by caller; parent cpu %.1fs" % (time.process_time() - t0)


# ------------------------------------------------------------------ K6f
def k6f():
    dc = X.dependency_confirmed
    up = X.unseen_pass
    RES["K6f_rules"] = (dc([True, True, False], [True, True, True])[0] and not dc([True, False, False], [True] * 3)[0]
                        and dc([True] * 3, [True] * 3)[0] and not dc([True, True, True], [False, True, False])[0]
                        and not dc([], [])[0]
                        and up([2, 0, 0, -1]) and not up([1, 0, 0, -1]) and not up([1, -1, -1, 2]) and not up([0, 0]) and up([3, -1, 0])
                        and not up([-1, 0, 1]))


# ------------------------------------------------------------------ fixtures
def _fixture(root, pairs, rows, walks_rows, idx_rows, common, res5, plan=None, sham_entries=None, start_libs=None):
    """Write synthetic E1/E5N receipt dirs under root; return a Ctx pointing at them."""
    e1d, e5d, e6d = Path(root) / "E1", Path(root) / "E5N", Path(root) / "E6"
    for d in (e1d, e5d, e6d):
        d.mkdir(parents=True, exist_ok=True)
    libs = {str(d): start_libs[d] for d, _n in pairs}
    wj(e1d / "E1_LIBRARIES.json", {"pairs": pairs, "libraries": libs,
                                   "sha256": {d: {k: sha(v) for k, v in L.items()} for d, L in libs.items()}})
    rec = {"rule": "synthetic", "common_residual": common}
    rec["sha256"] = sha(rec)
    wj(e1d / "E1_COMMON_RESIDUAL.json", rec)
    sh = {"sham": {str(d): ({"panel_key": "PA", "schema": "({H} + v)", "entries": sham_entries}
                            if sham_entries else {"panel_key": None, "entries": None}) for d, _n in pairs}}
    sh["sha256"] = sha({"sham": sh["sham"]})
    wj(e5d / "E5N_SHAM_LIBRARIES.json", sh)
    with open(e5d / "E5N_RECIP.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    with open(e5d / "E5N_RECIP_WALKS.jsonl", "w", encoding="utf-8") as fh:
        for r in walks_rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    wj(e5d / "E5N_RECIP_INDEX.json", {"index": idx_rows})
    wj(e5d / "E5N_RESULT.json", res5)
    return e1d, e5d, e6d


def _row(n, sel_entries, promoted_in, dwp, n_derived, selected="INHERITED", selected_schema=None, sel_prom=None,
         depth_sel=0, table=None, derived_full=None):
    r = {"seed": n, "tag": X.TAG_D, "selected": selected, "selected_schema": selected_schema,
         "selected_entries": sel_entries, "n_derived": n_derived, "n_observed": 5, "classes": 3,
         "selection_table": table or {"INHERITED": {"eligible": False, "mean_paired_saving": 0,
                                                    "lower95_one_sided": 0}},
         "w5p": {"promoted_in_ids": promoted_in, "n_derived_with_promoted": len(dwp), "derived_with_promoted": dwp,
                 "dag_depth_selected": depth_sel, "selected_uses_promoted": bool(sel_prom),
                 "selected_promoted": sel_prom or [], "cost": None}}
    if derived_full is not None:
        r["derived_schemas"] = derived_full
    return r


def _res5(label="NO", noop=True, pc=True, chan="OPEN", attributed=()):
    return {"R8_UNDER_PROMOTION_natural": label, "noop_ok": noop, "positive_control": pc,
            "label_qualifiers": {"channel_status": chan},
            "P1_enabling_L_g11_vs_L_P_promotable_CONFIRMATORY": {"p_one_sided": 0.4, "sum": 1},
            "SHAM_L_g11_vs_L_SHAM_promotable_residual_minus_sham_start": {"p_one_sided": 0.5, "sum": 0},
            "depth2_pairs_with_acquisition": [a["pair"] for a in attributed],
            "attributed_second_level_pairs": list(attributed)}


# ------------------------------------------------------------------ K6g
def k6g(tmp):
    import a17
    g5 = set(a17.g5_bodies())
    inh = rj(B02R / "R8" / "R8_LIBRARIES.json")["libraries"]["25"]["L_g11"]
    pri = rj(B02R / "R8" / "R8_LIBRARIES.json")["libraries"]["25"]["L_P"]
    e, _reg, pid, p = _depth2_entry(inh)
    sel = [e] + inh
    outside = next(b for b in e["bodies"] if b not in g5)
    d2 = {k: p.to_json()[k] for k in ("id", "schema", "expansion", "depth")}
    nt = "%s((last - {H}))" % pid
    bare = "%s({H})" % pid
    dwp = sorted([nt, bare])
    full = sorted(["(acc * {H})", nt, bare, "math.gcd(abs(acc), abs({H}))"])
    tab_b = {"INHERITED": {"eligible": False}, "SCHEMA_0": {"eligible": True}, "SCHEMA_1": {"eligible": True},
             "SCHEMA_2": {"eligible": True}, "SCHEMA_3": {"eligible": False}}
    tab_x = {"INHERITED": {"eligible": False}, "SCHEMA_0": {"eligible": True}, "SCHEMA_1": {"eligible": False},
             "SCHEMA_2": {"eligible": False}, "SCHEMA_3": {"eligible": False}}
    pairs = [[1, 101], [2, 102], [3, 103], [4, 104], [5, 105], [6, 106]]
    common = {str(n): ["fa", "fb"] for _d, n in pairs}
    rows = [_row(101, pri, [], [], 2),                                              # CANDIDACY (representation)
            _row(102, sel, [pid], [], 3),                                           # CANDIDACY
            _row(103, sel, [pid], dwp, 4, table=tab_b),                             # SELECTION, bound-resolved ELIGIBLE
            _row(104, sel, [pid], dwp, 4, table=tab_x, derived_full=full),          # SELECTION exact (nt at idx 1)
            _row(105, sel, [pid], dwp, 4, "SCHEMA_9", e["schema"], [d2], 2),        # SEARCH_BUDGET (cap small)
            _row(106, sel, [pid], dwp, 4, "SCHEMA_9", e["schema"], [d2], 2)]        # NONE (attributed)
    idx, wl = [], []
    for n, res in ((105, {"censored": True, "charge": 500, "program": None}),
                   (106, {"censored": False, "charge": 37, "program": ["fold", "0", outside, "acc"]})):
        for f in ("fa", "fb"):
            for ci in (0, 1):
                idx.append({"seed": n, "genome": X.TAG_D, "family": f, "cell": ci, "lib": "L%d" % n})
                wl.append({"lib": "L%d" % n, "family": f, "cell": ci,
                           "result": res if (f == "fa" or n == 105) else {"censored": True, "charge": 500}})
    starts = {d: {"L_g11": inh, "L_I0": inh, "L_P": pri} for d, _n in pairs}
    a106 = [{"pair": 106, "extend_families": ["fa"]}]
    out = {}
    for name, r5, cap in (("STAT", _res5(attributed=a106), 500), ("MEAS", _res5(noop=False), 500),
                          ("SUP", _res5(pc=False), 500)):
        root = Path(tmp) / ("neg_" + name)
        e1d, e5d, e6d = _fixture(root, pairs, rows, wl, idx, common, r5, start_libs=starts)
        out[name] = X.diagnose(X.Ctx(e1d, e5d, e6d, cap=cap), write=False)
    links = {p["pair"]: p["link"] for p in out["STAT"]["per_pair"]}
    reasons = {p["pair"]: p.get("reason") for p in out["STAT"]["per_pair"]}
    sel = {p["pair"]: p.get("selection", {}).get("kind") for p in out["STAT"]["per_pair"]}
    # global-link variants: drop pairs progressively
    variants = {}
    for name, keep, chan in (("SB", [101, 102, 103, 104, 105], "OPEN_NO_EXTEND_ACQUISITION"),
                             ("SEL", [101, 102, 103, 104], "CLOSED_SELECTION"),
                             ("CAND", [101, 102], "CLOSED_CANDIDACY")):
        pp = [p for p in pairs if p[1] in keep]
        root = Path(tmp) / ("neg_" + name)
        e1d, e5d, e6d = _fixture(root, pp, [r for r in rows if r["seed"] in keep], wl, idx,
                                 {k: v for k, v in common.items() if int(k) in keep}, _res5(chan=chan),
                                 start_libs=starts)
        variants[name] = X.diagnose(X.Ctx(e1d, e5d, e6d, cap=500), write=False)
    ok = (links == {101: "CANDIDACY", 102: "CANDIDACY", 103: "SELECTION", 104: "SELECTION", 105: "SEARCH_BUDGET",
                    106: "NONE"}
          and reasons[101].startswith("REPRESENTATION") and sel[103] == "ELIGIBLE_REJECTED"
          and sel[104] == "NONE_ELIGIBLE"
          and out["STAT"]["first_broken_link"].startswith("STATISTICAL:P1_ENABLING")
          and out["MEAS"]["first_broken_link"] == "MEASUREMENT" and out["SUP"]["first_broken_link"] == "SUPPLY"
          and variants["SB"]["first_broken_link"] == "SEARCH_BUDGET"
          and variants["SEL"]["first_broken_link"] == "SELECTION" and variants["SEL"]["consistent_with_E5N_channel"]
          and variants["CAND"]["first_broken_link"] == "CANDIDACY" and variants["CAND"]["consistent_with_E5N_channel"])
    # TRANSFER: same SB fixture with a cap above the promoted span
    root = Path(tmp) / "neg_TR"
    pp = [p for p in pairs if p[1] == 105]
    e1d, e5d, e6d = _fixture(root, pp, [r for r in rows if r["seed"] == 105], wl, idx, {"105": ["fa", "fb"]},
                             _res5(), start_libs=starts)
    tr = X.diagnose(X.Ctx(e1d, e5d, e6d, cap=10 ** 9), write=False)
    ok = ok and tr["first_broken_link"] == "TRANSFER"
    RES["K6g_negative_branch"] = bool(ok)
    RES["K6g_detail"] = {"links": links, "selection_kinds": sel,
                         "first": {k: v["first_broken_link"] for k, v in dict(out, **variants, TR=tr).items()}}


# ------------------------------------------------------------------ K6h
def k6h(tmp, w=2):
    idx = rj(B02R / "R8" / "R8_INDEX.json")["index"]
    W = {(x["lib"], x["family"], x["cell"]): x["result"] for x in rdl(B02R / "R8" / "R8_WALKS.jsonl")}
    D = {(x["seed"], x["tag"]): x for x in rdl(B02R / "R8" / "R8_DONORS.jsonl")}
    P = rj(B02R / "SUPPLY" / "PLAN_R8.json")
    n, tag = 49, "L_g11|g11_O10"
    lib = D[(n, tag)]["selected_entries"]
    k_rec = next(e["lib"] for e in idx if e["seed"] == n and e["genome"] == tag)
    fam = {f["name"]: f for f in b02._tr(P["plan"][str(n)], n)}
    rec = [(e["family"], e["cell"], W[(k_rec, e["family"], e["cell"])]) for e in idx
           if e["seed"] == n and e["genome"] == tag and (k_rec, e["family"], e["cell"]) in W]
    # cost control (declared): 3 qualified family-cells with the smallest recorded charge + 1 censored (full cap)
    qual = sorted([r for r in rec if not r[2]["censored"]], key=lambda r: r[2]["charge"])[:3]
    cens = [r for r in rec if r[2]["censored"]][:1]
    pick = qual + cens
    scr = X.scramble_library(lib, n)
    names_changed = all(a["name"] != b["name"] for a, b in zip(lib, scr))
    k = "SCR%d" % n
    out = Path(tmp) / "K6h_WALKS.jsonl"
    b02._pool_walks([(k, scr, fam[f], ci) for f, ci, _r in pick], out, w, "E6-known-scramble")
    got = {(x["family"], x["cell"]): x["result"] for x in rdl(out)}
    same = all(got.get((f, ci)) == r for f, ci, r in pick)
    RES["K6h_scramble_invariance_exposed_R8_49"] = bool(names_changed and same and len(pick) == 4)
    RES["K6h_detail"] = {"family_cells": [[f, ci, r["charge"], r["censored"]] for f, ci, r in pick]}


# ------------------------------------------------------------------ K6i
def k6i(tmp, w=2, cap=30_000):
    old = os.environ.get("V2B_R7E_CAP")
    os.environ["V2B_R7E_CAP"] = str(cap)            # walk workers read r7e.CAP from the environment at import
    try:
        _k6i(tmp, w, cap)
    finally:
        if old is None:
            os.environ.pop("V2B_R7E_CAP", None)
        else:
            os.environ["V2B_R7E_CAP"] = old


def _k6i(tmp, w, cap):
    import a18
    P = rj(B02R / "SUPPLY" / "PLAN_R8.json")
    L8 = rj(B02R / "R8" / "R8_LIBRARIES.json")["libraries"]["25"]
    diag = rj(b03.B03 / "W01_R8_COMMON_RESIDUAL_DIAG.json")
    n, d = 49, 25
    e, _reg, pid, p = _depth2_entry(L8["L_g11"])
    selD = [e] + L8["L_g11"]
    common = {str(n): sorted(diag["common_residual"][str(n)])[:3]}
    sham_entries = a18.start_library("PA", P["panel"])[0]
    row = _row(n, selD, [pid], [e["schema"]], 3, "SCHEMA_0", e["schema"],
               [{k: p.to_json()[k] for k in ("id", "schema", "expansion", "depth")}], 2)
    root = Path(tmp) / "pos"
    att = [{"pair": n, "extend_families": []}]
    e1d, e5d, e6d = _fixture(root, [[d, n]], [row], [], [], common, _res5("YES_PENDING_E6", attributed=att),
                             sham_entries=sham_entries, start_libs={d: L8})
    ctx = X.Ctx(e1d, e5d, e6d, plan=B02R / "SUPPLY" / "PLAN_R8.json", cap=cap)
    # "recorded" arm-D walks for the fixture (in E5-N these come from E5N_RECIP_WALKS)
    keys = {}
    kD = b02._key(selD, keys)
    fams = X._tr_common(P, n, common)
    idx = [{"seed": n, "genome": X.TAG_D, "family": f["name"], "cell": ci, "lib": kD} for f in fams for ci in (0, 1)]
    wj(e5d / "E5N_RECIP_INDEX.json", {"index": idx})
    b02._pool_walks([(kD, selD, f, ci) for f in fams for ci in (0, 1)], e5d / "E5N_RECIP_WALKS.jsonl", w, "E6-K6i-D")
    A = X.positive_build(ctx)
    X.positive_walk(ctx, w)
    out = X.positive_report(ctx)
    RES["K6i_positive_end_to_end"] = bool(out["LABEL_SCRAMBLE_INVARIANCE"] and len(out["per_pair"]) == 1
                                          and out["R8_UNDER_PROMOTION"] == "NO_AFTER_ATTACK"
                                          and "UNSEEN_LINEAGES" in out["failed_components"]
                                          and A["sha256"][str(n)]["D"] == sha(selD))
    RES["K6i_detail"] = {"per_pair": [{k: v for k, v in r.items() if k != "sham_detail"} for r in out["per_pair"]],
                         "failed_components": out["failed_components"], "cap": cap,
                         "sham": A["libraries"][str(n)]["sham_detail"]["sham_schema"]}


# ------------------------------------------------------------------ K6j
def k6j(tmp):
    ok = True
    for diffs, want in (([1, 0, 0, -1, 2, 0, 0, 0], True), ([1, -1, -1, 2, 0, 0, 0, 0], False),
                        ([0] * 8, False)):
        root = Path(tmp) / ("unseen_%s" % "_".join(map(str, diffs)))
        ud = root / "E6" / "UNSEEN"
        ud.mkdir(parents=True, exist_ok=True)
        seeds = list(range(120, 128))
        common = {str(s): ["f%d" % i for i in range(3)] for s in seeds}
        rec = {"rule": "synthetic", "pairs": [[d, s] for d, s in zip(range(72, 80), seeds)], "common_residual": common}
        rec["sha256"] = sha(rec)
        wj(ud / "U_COMMON_RESIDUAL.json", rec)
        idx, wl = [], []
        for s, dd in zip(seeds, diffs):
            aD, aC = (max(dd, 0), max(-dd, 0))
            for tag, a in ((X.TAG_D, aD), (X.TAG_C, aC)):
                for i in range(3):
                    idx.append({"seed": s, "genome": tag, "family": "f%d" % i, "cell": 0, "lib": "%s%d" % (tag, s)})
                    wl.append({"lib": "%s%d" % (tag, s), "family": "f%d" % i, "cell": 0,
                               "result": {"censored": i >= a, "charge": 1}})
        wj(ud / "U_START_INDEX.json", {"index": []})
        wj(ud / "U_RECIP_INDEX.json", {"index": idx})
        (ud / "U_START_WALKS.jsonl").write_text("", encoding="utf-8")
        (ud / "U_RECIP_WALKS.jsonl").write_text("".join(json.dumps(x) + "\n" for x in wl), encoding="utf-8")
        r = X.unseen_report(X.Ctx(e6d=root / "E6"))
        ok = ok and r["PASS"] == want and r["diffs_D_minus_C"] == diffs
    RES["K6j_unseen_report"] = bool(ok)


def main(w=2):
    t0, c0 = time.time(), time.process_time()
    tmp = tempfile.mkdtemp(prefix="b03e6_known_")
    _init()
    steps = [("K6a", k6a), ("K6b", k6b), ("K6c", k6c), ("K6d", k6d), ("K6e", lambda: k6e(tmp)), ("K6f", k6f),
             ("K6g", lambda: k6g(tmp)), ("K6j", lambda: k6j(tmp)), ("K6h", lambda: k6h(tmp, w)),
             ("K6i", lambda: k6i(tmp, w))]
    timing = {}
    for name, fn in steps:
        a, b = time.time(), time.process_time()
        try:
            fn()
        except Exception as ex:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            RES[name + "_ERROR"] = repr(ex)
        timing[name] = {"wall_s": round(time.time() - a, 1), "parent_cpu_s": round(time.process_time() - b, 1)}
        b02.log("%s done %s" % (name, timing[name]))
    keys = [k for k in RES if k.startswith("K6") and not k.endswith(("_detail", "_note", "_seeds"))]
    RES["pass"] = all(RES[k] is True for k in keys) and not any(k.endswith("_ERROR") for k in RES)
    RES["timing"] = timing
    RES["wall_s"] = round(time.time() - t0, 1)
    RES["parent_cpu_s"] = round(time.process_time() - c0, 1)
    wj(b03.B03 / "E6" / "E6_KNOWN.json", RES)
    shutil.rmtree(tmp, ignore_errors=True)
    b02.log("E6 known pass=%s %s" % (RES["pass"], {k: RES[k] for k in keys}))
    return RES


if __name__ == "__main__":
    main()
