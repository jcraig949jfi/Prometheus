"""BETA-03 E5-N: R8 UNDER REPRESENTATION PROMOTION, natural world (W8 LIN). Pre-registration: beta03/windows/E5N_PREREG.md.

Recipients: E1's block-B pairs (LIN 96-119) and E1's FROZEN common residual set (built from start walks only).
Donor libraries: E1's frozen, hashed libraries (L_g11, L_I0, L_P) + L_SHAM (a W8 panel sham schema, frequency-matched
to G1, drawn per pair by a seeded rule; never read from any outcome).
Machinery: the W5P donor (engine/w5p, branch aphrodite/b03-w5p @1e169a577) with rule g11 @ O10, promotion ON:
inherited schemas are promoted to primitives P(x) := S[H := x] and may be constituents of newly derived schemas.
Ordinary-representation arms A (L_P) and B (L_g11) are E1's recipients (identical machinery minus promotion).
Arms (promotable): C = L_P, D = L_g11, E = L_I0, F = L_SHAM.
Stages: sham | recip [w] | score [w] | report
"""
import os
os.environ.setdefault("V2B_T51_DIR", "T04_T51")
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
from collections import defaultdict  # noqa: E402

import b03  # noqa: E402   (imports b02 first: a18.TAG guard)
import b02  # noqa: E402

R = b02.R
E1D = b03.E1D
E5D = b03.B03 / "E5N"
LIBS5 = ["L_P", "L_g11", "L_I0", "L_SHAM"]
MACH5 = "w5p_g11_O10"
SHAM_KEYS = ["PA", "PB", "PC", "PD"]
MIN_DEPTH2_PAIRS = 3
log, wj, rj, sha = b02.log, b02.wj, b02.rj, b02.sha


def _w5p_run(job):
    """harness.run + selection_table and derived counts (red-team E5N-5). Same computation as harness.run."""
    sys.path.insert(0, str(b03.ROOT / "engine"))
    from w5p import harness
    from w5p import donor as WD
    from w5p import promote as WP
    keep = {}
    orig = WD.donor_w5p
    od = WP.derive_schemas

    def spy_derive(*a, **k):                   # amendment A2: record the FULL derived list (receipts only)
        out = od(*a, **k)
        keep["derived_schemas"] = [str(d.get("schema") if isinstance(d, dict) else d) for d in out]
        return out
    WP.derive_schemas = spy_derive
    # amendment A3 (technical rerun 1): output-promotion BOOKKEEPING of a selected schema whose hole occurs more than
    # once (not a unary-linear primitive under the W5P contract) records an UNPROMOTABLE stand-in carrying its
    # dependency depth instead of crashing. Selection, entries and transfer are computed before this step: unaffected.
    ofs = WP.Promoted.from_schema
    keep["unpromotable_selected"] = []

    class _Stand:
        def __init__(self, schema, reg):
            import hashlib as _h
            deps = sorted(set(WP.prims_in(WP.parse(schema))))
            self.schema, self.deps = schema, deps
            self.depth = 1 + max((reg[d].depth for d in deps if d in reg), default=0)
            self.lineage = sorted(set(deps) | {x for d in deps if d in reg for x in reg[d].lineage})
            self.id = "U_" + _h.sha256(schema.encode()).hexdigest()[:12]

        def to_json(self):
            return {"id": self.id, "schema": self.schema, "deps": self.deps, "depth": self.depth,
                    "lineage": self.lineage, "unpromotable": "hole occurs more than once"}

    def safe_from_schema(schema, reg, sha_, kind="selected_entry"):
        try:
            return ofs(schema, reg, sha_, kind)
        except ValueError as ex:
            if kind == "selected_entry" and "exactly one hole" in str(ex):
                st = _Stand(schema, reg)
                keep["unpromotable_selected"].append(st.to_json())
                return st
            raise
    WP.Promoted.from_schema = safe_from_schema

    def spy(*a, **k):
        r = orig(*a, **k)
        keep["selection_table"] = r.get("selection_table")
        keep["n_derived"] = r.get("n_derived")
        return r
    WD.donor_w5p = spy
    harness.D.donor_w5p = spy
    try:
        row = harness.run(job)
    finally:
        WD.donor_w5p = orig
        harness.D.donor_w5p = orig
        WP.derive_schemas = od
        WP.Promoted.from_schema = ofs
    row["selection_table"] = keep.get("selection_table")
    row["derived_schemas"] = keep.get("derived_schemas")
    row["unpromotable_selected"] = keep.get("unpromotable_selected", [])
    return row


def _init():
    sys.path.insert(0, str(b03.ROOT / "engine"))
    from w5p import harness
    harness.init_worker()


def sham_libraries():
    """L_SHAM per pair: start library of a W8 panel sham (PA..PD, frequency-matched to G1 on U supply; W8_PANEL),
    chosen by a seeded draw keyed on the donor seed only."""
    import a18
    L = b03._libs_checked()
    panel = rj(b02.SUP / "PLAN_B.json")["panel"]
    out = {}
    for d, _n in L["pairs"]:
        order = list(SHAM_KEYS)
        random.Random(b02.I._seed("APHRODITE/B03/E5N/SHAM/%d" % d)).shuffle(order)
        learned = set(b03.templates(L["libraries"][str(d)]["L_g11"]) + b03.templates(L["libraries"][str(d)]["L_I0"]))
        pick = next((k for k in order if panel[k] not in learned), None)      # red-team E5N-3
        out[str(d)] = ({"panel_key": pick, "schema": panel[pick], "entries": a18.start_library(pick, panel)[0]}
                       if pick else {"panel_key": None, "entries": None})
    rec = {"sham": out}
    rec["sha256"] = sha(rec)
    wj(E5D / "E5N_SHAM_LIBRARIES.json", rec)
    log("E5N sham libraries: %d; sha %s" % (len(out), rec["sha256"][:16]))
    return rec


def _libs():
    L = b03._libs_checked()
    S = rj(E5D / "E5N_SHAM_LIBRARIES.json")
    assert sha({"sham": S["sham"]}) == S["sha256"], "sham library hash mismatch"
    return {d: dict(ls, L_SHAM=S["sham"][d]["entries"]) for d, ls in L["libraries"].items()}, L["pairs"]


def stage_sham(w=4):
    """Freeze sham libraries and walk their START on block-B transfer cells (inherited capability, report-only)."""
    E5D.mkdir(parents=True, exist_ok=True)
    if not (E5D / "E5N_SHAM_LIBRARIES.json").exists():
        sham_libraries()
    libs, pairs = _libs()
    PB = rj(b02.SUP / "PLAN_B.json")
    keys, index, todo = {}, [], {}
    for d, n in pairs:
        if libs[str(d)]["L_SHAM"] is None:
            continue
        k = b02._key(libs[str(d)]["L_SHAM"], keys)
        for f in b02._tr(PB["plan"][str(n)], n):
            for ci in range(2):
                index.append({"seed": n, "genome": "START|L_SHAM", "family": f["name"], "cell": ci, "lib": k})
                todo.setdefault((k, f["name"], ci), (k, keys[k], f, ci))
    wj(E5D / "E5N_SHAM_START_INDEX.json", {"index": index})
    b02._pool_walks(list(todo.values()), E5D / "E5N_SHAM_START_WALKS.jsonl", w, "E5N-sham")


def stage_recip(w=4):
    from concurrent.futures import ProcessPoolExecutor
    assert (E1D / "E1_COMMON_RESIDUAL.json").exists(), "E1 common residual must be frozen first"
    libs, pairs = _libs()
    PB = rj(b02.SUP / "PLAN_B.json")
    out = E5D / "E5N_RECIP.jsonl"
    done = {(x["tag"], x["seed"]) for x in R.rdl(out)}
    jobs = [("%s|%s" % (lb, MACH5), "g11", "O10", n, PB["plan"][str(n)]["O10"], PB["panel"], libs[str(d)][lb])
            for d, n in pairs for lb in LIBS5 if ("%s|%s" % (lb, MACH5), n) not in done
            and libs[str(d)][lb] is not None]
    log("E5N recipient jobs %d" % len(jobs))
    with open(out, "a", encoding="utf-8") as fh, ProcessPoolExecutor(max_workers=w, initializer=_init) as ex:
        for r in ex.map(_w5p_run, jobs):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            log("seed %d %-18s sel=%s depth=%s usesP=%s" % (r["seed"], r["tag"], r["selected_schema"],
                                                            r["w5p"]["dag_depth_selected"],
                                                            r["w5p"]["selected_uses_promoted"]))


def stage_score(w=4):
    libs, pairs = _libs()
    PB = rj(b02.SUP / "PLAN_B.json")
    keys, index, todo = {}, [], {}
    for x in R.rdl(E5D / "E5N_RECIP.jsonl"):
        n = x["seed"]
        k = b02._key(x["selected_entries"], keys)
        for f in b02._tr(PB["plan"][str(n)], n):
            for ci in range(2):
                index.append({"seed": n, "genome": x["tag"], "family": f["name"], "cell": ci, "lib": k,
                              "start": "START|" + x["tag"].split("|")[0]})
                todo.setdefault((k, f["name"], ci), (k, keys[k], f, ci))
    wj(E5D / "E5N_RECIP_INDEX.json", {"index": index})
    have = set()
    for p in (E1D / "E1_START_WALKS.jsonl", E1D / "E1_RECIP_WALKS.jsonl", E5D / "E5N_SHAM_START_WALKS.jsonl"):
        have |= {(x["lib"], x["family"], x["cell"]) for x in R.rdl(p)}
    b02._pool_walks([v for kk, v in todo.items() if kk not in have], E5D / "E5N_RECIP_WALKS.jsonl", w, "E5N")


def _nontrivial_depth2(row):
    """Selected promoted-dependent schemas that are not a bare re-expression P({H}) of an inherited primitive."""
    w = row.get("w5p") or {}
    if w.get("dag_depth_selected", 0) < 2 or not w.get("selected_uses_promoted"):
        return []
    import re
    bare = re.compile(r"P_[0-9a-f]+\(\{H\}\)")
    return [p for p in w.get("selected_promoted", []) if p.get("depth", 0) >= 2
            and not bare.fullmatch(str(p.get("schema", "")).strip())]


def _g5():
    import a17
    return set(a17.g5_bodies())


def _first_program(W, idx_by, tag, n, f):
    for ci in (0, 1):
        k = idx_by.get((tag, n, f, ci))
        r = W.get((k, f, ci)) if k else None
        if r and not r.get("censored", True):
            return r.get("program")
    return None


def report():
    """Frozen rules: beta03/windows/E5N_PREREG.md s5 (as amended A1, pre-data)."""
    libs, pairs = _libs()
    seeds = [n for _d, n in pairs]
    C = rj(E1D / "E1_COMMON_RESIDUAL.json")["common_residual"]
    W = {}
    for p in (E1D / "E1_START_WALKS.jsonl", E1D / "E1_RECIP_WALKS.jsonl", E5D / "E5N_SHAM_START_WALKS.jsonl",
              E5D / "E5N_RECIP_WALKS.jsonl"):
        for x in R.rdl(p):
            W[(x["lib"], x["family"], x["cell"])] = x["result"]
    idx = (rj(E1D / "E1_START_INDEX.json")["index"] + rj(E1D / "E1_RECIP_INDEX.json")["index"]
           + rj(E5D / "E5N_SHAM_START_INDEX.json")["index"] + rj(E5D / "E5N_RECIP_INDEX.json")["index"])
    tags = ["L_P|g11_O10", "L_g11|g11_O10"] + ["%s|%s" % (lb, MACH5) for lb in LIBS5]
    acq = b03.acq_common_from(idx, W, C, tags, seeds)
    own = b02._gains(idx, W, lambda e: e.get("start", e["genome"]), tags, seeds)
    D5 = {(x["seed"], x["tag"]): x for x in R.rdl(E5D / "E5N_RECIP.jsonl")}
    E1R = {(x["seed"], x["tag"]): x for x in R.rdl(E1D / "E1_RECIP.jsonl")}
    c = lambda a, b: [acq[a][n] - acq[b][n] for n in seeds]  # noqa: E731
    P1 = b02.flip_test(c("L_g11|" + MACH5, "L_P|" + MACH5))           # enabling under promotion (SOLE confirmatory)
    P2 = b02.flip_test(c("L_g11|" + MACH5, "L_g11|g11_O10"))           # descriptive (red-team E5N-4)
    # SHAM on the residual minus what the sham START reaches (red-team E5N-3); pairs without a sham excluded
    reach = defaultdict(bool)
    for e in idx:
        reach[(e["genome"], e["seed"], e["family"])] |= b03._ok(W.get((e["lib"], e["family"], e["cell"])))
    sh_pairs = [n for d, n in pairs if libs[str(d)]["L_SHAM"] is not None]
    C_sh = {str(n): [f for f in C[str(n)] if not reach[("START|L_SHAM", n, f)]] for n in sh_pairs}
    acq_sh = b03.acq_common_from(idx, W, C_sh, ["L_g11|" + MACH5, "L_SHAM|" + MACH5], sh_pairs)
    SH = b02.flip_test([acq_sh["L_g11|" + MACH5][n] - acq_sh["L_SHAM|" + MACH5][n] for n in sh_pairs])
    # measurement gate: W5P with a PRISTINE start must equal the ordinary recipient (no-op continuity), all pairs
    keys = ("selected_schema", "selected_entries", "n_observed", "n_derived", "classes")
    noop = [n for n in seeds if all(D5[(n, "L_P|" + MACH5)][k] == E1R[(n, "L_P|g11_O10")][k] for k in keys)]
    noop_ok = len(noop) == len(seeds)
    best = max([t for t in tags if not t.startswith("L_SHAM")], key=lambda t: sum(acq[t].values()))
    pc = sum(acq[best].values()) >= b03.PC_MIN_FAMILIES and sum(1 for n in seeds if acq[best][n] > 0) >= b03.PC_MIN_PAIRS
    d2 = {n: _nontrivial_depth2(D5[(n, "L_g11|" + MACH5)]) for n in seeds}
    d2_pairs = [n for n in seeds if d2[n]]
    # attribution (red-team E5N-1): an acquisition is EXTEND iff its first qualified program's body lies OUTSIDE G5
    # (it exists only through promotion); REORDER otherwise. A pair is SECOND-LEVEL iff it has a non-trivial selected
    # depth-2 schema AND >= 1 acquired common-residual family whose body is outside G5 and belongs to a
    # promoted-form entry of the selected library.
    G5 = _g5()
    idx_by = {(e["genome"], e["seed"], e["family"], e["cell"]): e["lib"] for e in idx}
    split = {t: {"REORDER": 0, "EXTEND": 0} for t in tags}
    attributed = []
    for n in seeds:
        for t in tags:
            for f in C[str(n)]:
                prog = _first_program(W, idx_by, t, n, f)
                if prog:
                    split[t]["EXTEND" if prog[2] not in G5 else "REORDER"] += 1
        if n in d2_pairs:
            sel = D5[(n, "L_g11|" + MACH5)]["selected_entries"]
            pbodies = set()
            for e in sel:
                sch = [e.get("schema")] + list(e.get("schemas") or [])
                if any(s and "P_" in s for s in sch):
                    pbodies |= set(e.get("bodies") or [])
            ext = [f for f in C[str(n)] if (lambda pr: pr and pr[2] not in G5 and pr[2] in pbodies)(
                _first_program(W, idx_by, "L_g11|" + MACH5, n, f))]
            if ext:
                attributed.append({"pair": n, "extend_families": ext})
    d2_acq_pairs = [x["pair"] for x in attributed]
    depth_any = {t: sum(1 for n in seeds if D5[(n, t)]["w5p"]["dag_depth_selected"] >= 2)
                 for t in ["%s|%s" % (lb, MACH5) for lb in LIBS5]}
    max_depth = max((D5[(n, t)]["w5p"]["dag_depth"] for n in seeds for t in ["%s|%s" % (lb, MACH5) for lb in LIBS5]),
                    default=0)
    cost = {t: {"search_charges_sum": sum((D5[(n, t)]["w5p"].get("cost") or {}).get("total", {}).get("search_charges", 0)
                                          for n in seeds),
                "expanded_sum": sum((D5[(n, t)]["w5p"].get("cost") or {}).get("total", {}).get("expanded_exec_units", 0)
                                    for n in seeds),
                "promoted_units_sum": sum((D5[(n, t)]["w5p"].get("cost") or {}).get("total", {})
                                          .get("promoted_exec_units", 0) for n in seeds)}
            for t in ["%s|%s" % (lb, MACH5) for lb in LIBS5]}
    gate = noop_ok and pc
    enabling = P1["p_one_sided"] < 0.05 and P1["sum"] > 0
    second = len(d2_acq_pairs) >= MIN_DEPTH2_PAIRS
    sham_ok = SH["p_one_sided"] < 0.05 and SH["sum"] > 0
    derived_any = sum(1 for n in seeds if D5[(n, "L_g11|" + MACH5)]["w5p"]["n_derived_with_promoted"] > 0)
    channel = ("CLOSED_CANDIDACY" if derived_any == 0 else
               ("CLOSED_SELECTION" if not d2_pairs else
                ("OPEN_NO_EXTEND_ACQUISITION" if not attributed else "OPEN")))
    attainable = P1["attainable_min_p"] < 0.05
    if not noop_ok:
        label = "MEASUREMENT_FAILED"
    elif not pc:
        label = "INSTRUMENT_UNVALIDATED"
    elif enabling and second and sham_ok:
        label = "YES_PENDING_E6"          # provisional until the pre-registered E6 dependency attack confirms
    else:
        label = "NO"
    qualifiers = {"P1_attainable_at_0.05": attainable, "P1_nonzero_pairs": P1["nonzero"], "channel_status": channel,
                  "pairs_deriving_promoted_schemas": derived_any,
                  "caveat": "a natural-world NO does not by itself trigger retirement without the structured-world "
                            "(E5-H) known-positive control (red-team E5N-4)"}
    frac_attr = len(attributed) / len(seeds) if seeds else 0.0
    kill = ("NOT_EVALUABLE_N_LT_20" if len(seeds) < 20 else
            ("FIRES" if not enabling and frac_attr < 0.10 else "DOES_NOT_FIRE"))
    res = {"pairs": pairs, "n_pairs": len(pairs), "acq_common": {t: sum(v.values()) for t, v in acq.items()},
           "acq_common_per_pair": acq, "own_start_improvement": {t: sum(v.values()) for t, v in own.items()},
           "amendment": "A1 (pre-data, red-team REDTEAM_E5N_PREFREEZE.md)",
           "P1_enabling_L_g11_vs_L_P_promotable_CONFIRMATORY": P1, "P2_promotion_effect_L_g11_descriptive": P2,
           "SHAM_L_g11_vs_L_SHAM_promotable_residual_minus_sham_start": SH, "sham_pairs": len(sh_pairs),
           "reorder_extend_split_common_acquisitions": split, "attributed_second_level_pairs": attributed,
           "label_qualifiers": qualifiers, "KILL_CRITERION_HESTIA": kill, "attributed_depth2_fraction": frac_attr,
           "noop_continuity_pairs": len(noop), "noop_ok": noop_ok, "positive_control_arm": best, "positive_control": pc,
           "depth2_nontrivial_selected_pairs": d2_pairs, "depth2_pairs_with_acquisition": d2_acq_pairs,
           "depth2_detail": {n: d2[n] for n in d2_pairs},
           "dag_depth_selected_ge2_by_arm": depth_any, "max_dag_depth_observed": max_depth,
           "cost_ledgers": cost, "R8_UNDER_PROMOTION_natural": label}
    wj(E5D / "E5N_RESULT.json", res)
    log("E5N %s P1 %s/%s/%s p1 %s depth2 pairs %d (acq %d) sham p %s" % (
        label, P1["better"], P1["worse"], P1["tied"], P1["p_one_sided"], len(d2_pairs), len(d2_acq_pairs),
        SH["p_one_sided"]))
    return res


def known():
    """Outcome-free known answers on EXPOSED Beta-02 data (one worker, sequential: also exercises per-job state):
    K5a W5P (promotion ON) with a PRISTINE start reproduces Beta-02 E12 seed 25 g11_O10 (no-op continuity);
    K5b W5P with promotion OFF and an inherited start (Beta-02 R8 L_g11, pair 25->49) reproduces the Beta-02 R8
        recipient row L_g11|g11_O10 for seed 49 (transplant continuity);
    K5c the same job with promotion ON returns a well-formed w5p block (promoted_in = the inherited schema(s))."""
    from concurrent.futures import ProcessPoolExecutor
    B02R = b03.ROOT / "beta02" / "runs"
    PE, PR = rj(B02R / "SUPPLY" / "PLAN_E.json"), rj(B02R / "SUPPLY" / "PLAN_R8.json")
    E12 = {(x["seed"], x["tag"]): x for x in R.rdl(B02R / "E12" / "E12_DONORS.jsonl")}
    R8 = {(x["seed"], x["tag"]): x for x in R.rdl(B02R / "R8" / "R8_DONORS.jsonl")}
    lib = rj(B02R / "R8" / "R8_LIBRARIES.json")["libraries"]["25"]["L_g11"]
    jobs = [("k5a", "g11", "O10", 25, PE["plan"]["25"]["O10"], PE["panel"], None),
            ("k5b", "g11", "O10", 49, PR["plan"]["49"]["O10"], PR["panel"], lib, {"promote": False}),
            ("k5c", "g11", "O10", 49, PR["plan"]["49"]["O10"], PR["panel"], lib)]
    with ProcessPoolExecutor(max_workers=1, initializer=_init) as ex:
        a, b, c = list(ex.map(_w5p_run, jobs))
    keys = ("selected_schema", "selected_entries", "n_observed", "n_derived", "classes")
    res = {"K5a_pristine_noop_equals_E12_seed25": all(a[k] == E12[(25, "g11_O10")][k] for k in keys),
           "K5b_promote_off_equals_R8_seed49": all(b[k] == R8[(49, "L_g11|g11_O10")][k] for k in keys),
           "K5c_promote_on_wellformed": bool(c["w5p"]["promotion_enabled"] and c["w5p"]["promoted_in_ids"]
                                             and c["w5p"]["cost"]),
           "K5d_selection_table_recorded": all(x.get("selection_table") for x in (a, b, c)),
           "K5e_derived_schemas_recorded": all(isinstance(x.get("derived_schemas"), list) for x in (a, b, c))}
    res["pass"] = all(res.values())
    res["k5c_summary"] = {"selected": c["selected_schema"], "dag_depth": c["w5p"]["dag_depth"],
                          "derived_with_promoted": c["w5p"]["n_derived_with_promoted"]}
    E5D.mkdir(parents=True, exist_ok=True)
    wj(E5D / "E5N_KNOWN.json", res)
    log("E5N known %s" % res)
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    w = int(a[-1]) if a and a[-1].isdigit() else 4
    {"sham": lambda: stage_sham(w), "recip": lambda: stage_recip(w), "score": lambda: stage_score(w),
     "report": report, "known": known}[a[0]]()
