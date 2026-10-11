"""E3-R analysis (windows/E3R_PREREG.md + AMENDMENT E3R-A1 = red team reviews/REDTEAM_E3R_PREFREEZE.md s3 A1-A12, s4
rulings, s5 claim limits). Pure functions over the E3-KP-format caches written by e3_known_positive.py (one
KPA1_<world>.json per world in the E3-R output dir, seeded from the frozen E3-KP cache). The driver is e3r_run.py.

CELLS (seed s): off_frozen = Config(seed=s) (s = 0: the FROZEN E3-KP primary, re-used, asserted = the frozen pooled
file); on_frozen = Config(oe=True, seed=s); off_xabs = Config(extract="xabs", seed=s); on_xabs = Config(oe=True,
extract="xabs", seed=s). Seeds 0, 1, 2 for on_frozen, on_xabs, off_xabs (A3); off_frozen seeds 1 / 2 are the frozen
E3-KP seed rows. Priority 2 (A8): on_xabs with fallback OFF, seed 0 ("on_xabs_fb0").

SCRATCH CONTROL (A1). The PRIMARY control of an OE cell is the OE scratch (seed 0, cap 3,600 CPU-s, one extension to
14,400); of an off cell the non-OE scratch (seed 0). Seeds 1 / 2 RE-USE the seed-0 scratch of their enumerator
(declared deviation from the E3-KP s4B item 10 convention, for compute; A3). A scratch is FAILED (no qualified
program), SOLVED, CENSORED (cap reached: a THIRD state) or NOT_RUN (lazy). Bounds per cell: LO = CENSORED / NOT_RUN
counted as NOT failed; HI = counted as failed. A cell COUNTS at a bound iff its chains are complete, 5q >= 4n and
5 * scratch_fails(bound) >= 4n; TRIVIALISED at a bound iff 5q >= 4n but the scratch condition fails;
COUNTS_CONDITIONAL iff the bounds disagree. The frozen non-OE scratch is reported beside every OE cell as a weaker
SECONDARY control only.

LABEL per seed (prereg table): EITHER (on_frozen AND off_xabs count) / SEARCH (on_frozen only) / DEVELOPMENTAL
(off_xabs only) / BOTH_REQUIRED (only on_xabs) / NONE; INCOMPLETE if any cell's chains are incomplete. Computed at LO
and at HI; if they agree, that is the label; else "<HI label> (CONDITIONAL: ...)" and the UNCONDITIONAL (LO) label
is the one the recommendation may use. Stability over seeds 0 / 1 / 2: STABLE (3/3), MAJORITY (2/3: the majority
label is reported), SEED_UNSTABLE (the seed-0 label is reported, tagged). Computed on the unconditional labels.

READINGS (A4, A5, A7, A12; fixed text in INTERPRETATION): reading cell for NONE = on_xabs (seed 0); dominant link =
strict majority of its not-qualified families among HORIZON (HORIZON_R1 + COMPOSITION_HORIZON) / UD-R1 / UD-EXTRACT;
otherwise MIXED. UD split: UD-R1 = an R1 first dev-consistent program failed test + tribunal (dev gap; WORLD);
UD-EXTRACT = a qualified R1 program whose stone disagrees with the sealed mechanism on probes, with a post-hoc
global-equivalence check of that R1 program vs the sealed R1 witness (GLOBAL_EQ_LISTS); UD-OTHER = the anomaly.
"""
import hashlib
import json
import random
import time
from pathlib import Path
from typing import Dict, List, Optional

from tfs1 import core as C
from tfs1.e3 import worlds as WD
from tfs1.e3 import e3_known_positive as KP

CELLS = ("off_frozen", "on_frozen", "off_xabs", "on_xabs")
SEEDS = (0, 1, 2)
READING_CELL = "on_xabs"
OE_SCRATCH_CAP_S = 3600.0
OE_SCRATCH_EXTENSION_S = 14400.0
OE_SCRATCH_ENVELOPE_S = 16 * 3600.0
HARD_STOP_UTC = "2026-10-13T09:27:00Z"
NOT_BEFORE_UTC = "2026-10-11T11:30:00Z"
GLOBAL_EQ_SEED = "TFS1/E3R/GLOBALEQ/v0"

SCOPE = ("E3-R discriminates repair class WITHIN TFS-1. It does NOT discriminate CHANGE vs MIGRATE; that decision "
         "rests on AR-1 and the synthesis. Every label is conditional on the readout fallback (A1-C; see the "
         "fallback-off row).")
INTERPRETATION = {
    "SEARCH": "repair class SEARCH within TFS-1: pre-registered OE pruning alone qualifies the known-positive chain",
    "BOTH_REQUIRED": "repair class BOTH_REQUIRED within TFS-1: OE + post-hoc patch (X-ABS, a post-hoc single-motif "
                     "extraction patch)",
    "DEVELOPMENTAL": "repair class DEVELOPMENTAL within TFS-1 (X-ABS, a post-hoc single-motif extraction patch, alone); "
                     "NOTE: pre-registered as unattainable at seed 0 (off_xabs = 9/15 known)",
    "EITHER": "repair class EITHER within TFS-1 (OE alone, or the post-hoc X-ABS patch alone); NOTE: pre-registered as "
              "unattainable at seed 0 (off_xabs = 9/15 known)",
    "NONE/HORIZON": "no repair class identified at 1e6; the horizon remains binding (consistent with CHANGE_SEARCH -- "
                    "a bigger search change -- or MIGRATE; NOT a CHANGE_SEARCH finding)",
    "NONE/UD-R1": "no repair class identified; UD-R1 dominated (R1 dev gaps): points to WORLD (foundry "
                  "identifiability); not, alone, to MIGRATE",
    "NONE/UD-EXTRACT": "no repair class identified; UD-EXTRACT dominated in on_xabs: points to DEVELOPMENTAL "
                       "coverage (extraction); not, alone, to MIGRATE",
    "NONE/MIXED": "no repair class identified; the residual links are listed",
    "INCOMPLETE": "REPAIR_CLASS = INCOMPLETE (required items not complete); bounds reported",
}
CLAIM_LIMITS = {
    "may_claim": "On 15 foundry-selected families, with oracle decomposition and certifier-guided R1 acquisition, and "
                 "with the readout fallback ON, at seed(s) S: pre-registered OE pruning [plus a post-hoc single-motif "
                 "extraction patch] qualifies the known-positive chain at >= 12/15; the repair class is <label> "
                 "(<stability>).",
    "may_not_claim": [
        "TFS1_INSTRUMENT_QUALIFIED = YES, or any relabel of E3-KP (still NO)",
        "an open E3 lifetime gate (needs TFS1_INSTRUMENT_QUALIFIED = YES)",
        "that E3-R is the counterfactual A1-A.5 repair (the trigger did not fire): not 'TFS-1 would have qualified'",
        "COMPOSITIONAL_DISCOVERY",
        "generality of X-ABS beyond the hoisted-reducer motif",
        "'developmental machinery is fine' (under SEARCH with X-ABS firing in the OE cells)",
        "evidence for CHANGE over MIGRATE"],
    "standing_limits": ["oracle decomposition (sealed-indexed R1 tasks)", "certifier-guided R1 retry",
                        "15 foundry-selected families (regression to the mean, F5)",
                        "judged on the same test + tribunal as foundry admission (no fresh tribunal, F11 / M6)",
                        "seeds 1 / 2 re-use the seed-0 scratch (declared deviation)"],
}


def cell_cfg(cell: str, seed: int = 0, budget: int = KP.BUDGET, fallback: bool = True) -> KP.Config:
    oe = cell.startswith("on_")
    ex = "xabs" if cell.endswith("xabs") else "frozen"
    return KP.Config(fallback=fallback, oe=oe, extract=ex, seed=seed, budget=budget)


def utc_now() -> str:
    return KP.utc_now()


# ================================================================ scratch states
def scratch_key(fid, oe, budget) -> str:
    return KP.search_key(fid, None, KP.Config(oe=oe, budget=budget))          # always seed 0 (A3 deviation)


def scratch_state(d: Dict, fid: str, oe: bool, budget: int) -> Dict:
    k = scratch_key(fid, oe, budget)
    r = d.get("searches", {}).get(k)
    if r is not None:
        q = bool(r.get("hit") and r.get("verdict", {}).get("qualified"))
        return {"state": "SOLVED" if q else "FAILED", "cpu_s": r.get("cpu_s", 0.0)}
    c = d.get("censored_searches", {}).get(k)
    if c is not None:
        return {"state": "CENSORED", "cpu_s": c["row"].get("cpu_s", 0.0), "cap_s": c["cap_s"]}
    return {"state": "NOT_RUN", "cpu_s": 0.0}


# ================================================================ UD split + global equivalence
def global_eq_lists() -> List[List[int]]:
    """The reviewer's F2 list set, fixed: the empty list, every singleton in [-200, 200], 20,000 lists of length 1-16
    with elements in [-60, 60] (seed GLOBAL_EQ_SEED)."""
    rng = random.Random(GLOBAL_EQ_SEED)
    out = [[]] + [[v] for v in range(-200, 201)]
    out += [[rng.randint(-60, 60) for _ in range(rng.randint(1, 16))] for _ in range(20000)]
    return out


_GEQ = {}


def global_equivalence(program: str, witness: str) -> Dict:
    """POST-HOC scoring only: does the R1 program equal the sealed R1 witness (value-or-FAIL) on GLOBAL_EQ_LISTS?"""
    k = (program, witness)
    if k not in _GEQ:
        lists = global_eq_lists()
        a = C.compile_term(C.parse(program), None, None, swap=False)
        b = C.compile_term(C.parse(witness), None, None, swap=False)
        diff = 0
        for inp in lists:
            if not C.same_value(C.run(a, list(inp)), C.run(b, list(inp))):
                diff += 1
        _GEQ[k] = {"n_lists": len(lists), "n_differ": diff, "globally_equivalent": diff == 0}
    return _GEQ[k]


def ud_split(kp: KP.KP, units: Dict, link_info: Dict) -> Dict:
    det = link_info.get("detail")
    if det == "R1_FIRST_DEV_CONSISTENT_FAILS_TEST":
        return {"ud": "UD-R1", "unit": link_info.get("unit")}
    if det == "STONE_DISAGREES_SEALED_PROBES":
        out = {"ud": "UD-EXTRACT", "units": {}}
        for m in link_info.get("units", []):
            u = units[m]
            prog = next((a["found"] for a in u.get("attempts", []) if a["family_id"] == u.get("from")), None)
            g = (global_equivalence(prog, kp.fams[u["from"]]["witness"]) if prog and u.get("from") in kp.fams
                 else None)
            out["units"][m] = {"r1_program": prog, "from": u.get("from"), "stone": u.get("lambda"),
                               "global_equivalence_vs_sealed_r1_witness": g}
        return out
    return {"ud": "UD-OTHER", "detail": det}


# ================================================================ collection
def _families(kp: KP.KP, d: Dict, cfg: KP.Config, scratch_oe: bool, budget: int) -> List[Dict]:
    row = d.get("rows", {}).get(cfg.key(), {})
    units, chain = row.get("units", {}), row.get("chain", {})
    out = []
    for fid in kp.admitted():
        ch = chain.get(fid)
        li = kp.family_link(fid, units, ch)
        rec = {"world": kp.world, "family_id": fid, "rung": kp.fams[fid]["rung"],
               "output_type": kp.task(fid)["output_type"], "chain_status": ch["status"] if ch else None,
               "complete": ch is not None and all(m in units for m in kp.constituents(fid)),
               "qualified": bool(ch and ch["status"] == "SOLVED"), "link": li["link"], "detail": li["detail"],
               "scratch": scratch_state(d, fid, scratch_oe, budget)["state"],
               "scratch_secondary_non_oe": scratch_state(d, fid, False, budget)["state"] if scratch_oe else None}
        if li["link"] == "UNDERDETERMINED_STONE":
            rec["ud"] = ud_split(kp, units, li)
        out.append(rec)
    return out


def _units(kp: KP.KP, d: Dict, cfg: KP.Config) -> Dict[str, Dict]:
    row = d.get("rows", {}).get(cfg.key(), {})
    return {"%s/%s" % (kp.world, m): u for m, u in row.get("units", {}).items()}


def collect(root, worlds: List[str], out_dir, budget=KP.BUDGET, seeds=SEEDS, with_fb0=True) -> Dict:
    data = {"families": {}, "units": {}}
    kps = {w: KP.KP(root, w) for w in worlds}
    ds = {w: KP._load(out_dir, w) for w in worlds}
    specs = [(c, s, True) for s in seeds for c in CELLS] + ([("on_xabs_fb0", 0, False)] if with_fb0 else [])
    for cell, s, fb in specs:
        base = cell.replace("_fb0", "")
        cfg = cell_cfg(base, s, budget, fallback=fb)
        fams, units = [], {}
        for w in worlds:
            fams += _families(kps[w], ds[w], cfg, base.startswith("on_"), budget)
            units.update(_units(kps[w], ds[w], cfg))
        data["families"][(cell, s)] = fams
        data["units"][(cell, s)] = units
    data["_kps"], data["_ds"] = kps, ds
    return data


# ================================================================ bounds, labels
def cell_summary(fams: List[Dict], units: Dict, kps=None) -> Dict:
    n = len(fams)
    q = sum(f["qualified"] for f in fams)
    complete = n > 0 and all(f["complete"] for f in fams)
    st = [f["scratch"] for f in fams]
    fail, cen, nr, sol = (st.count("FAILED"), st.count("CENSORED"), st.count("NOT_RUN"), st.count("SOLVED"))
    sf_lo, sf_hi = fail, fail + cen + nr
    hi_chain = complete and 5 * q >= 4 * n
    lo = hi_chain and 5 * sf_lo >= 4 * n
    hi = hi_chain and 5 * sf_hi >= 4 * n
    links = {}
    ud = {"UD-R1": 0, "UD-EXTRACT": 0, "UD-OTHER": 0}
    for f in fams:
        if not f["qualified"] and f["link"]:
            links[f["link"]] = links.get(f["link"], 0) + 1
            if f.get("ud"):
                ud[f["ud"]["ud"]] += 1
    fired = sorted(k for k, u in units.items() if u.get("extraction") == "xabs_absorbed")
    agree = {}
    for k in fired:
        u = units[k]
        prog = next((a["found"] for a in u.get("attempts", []) if a["family_id"] == u.get("from")), None)
        if kps is not None and prog:
            w, m = k.split("/")
            fr = KP.extract_mechanism(prog, kps[w].mech[m]["kind"])
            agree[k] = {"before_frozen_stone": C.to_str(fr[0]) if fr else None,
                        "before_agreement": kps[w].agree_sealed(m, C.to_str(fr[0])) if fr else None,
                        "after_xabs_stone": u.get("lambda"),
                        "after_agreement": u.get("agrees_with_sealed_on_probe")}
    sec = [f["scratch_secondary_non_oe"] for f in fams if f.get("scratch_secondary_non_oe") is not None]
    return {"n": n, "chain_qualified": q, "complete": complete,
            "scratch": {"FAILED": fail, "CENSORED": cen, "NOT_RUN": nr, "SOLVED": sol},
            "scratch_fails_LO": sf_lo, "scratch_fails_HI": sf_hi, "chain_ge_80pct": hi_chain,
            "counts_LO": lo, "counts_HI": hi, "COUNTS_CONDITIONAL": lo != hi,
            "trivialised_LO": hi_chain and not lo, "trivialised_HI": hi_chain and not hi,
            "n_censored": cen, "n_not_run": nr, "first_failing_link_counts": links, "ud_sublabels": ud,
            "xabs_firings": len(fired), "xabs_fired_units": fired, "stone_agreement_before_after": agree,
            "certifier_assisted_retries": sum(bool(u.get("certifier_assisted_retry")) for u in units.values()),
            "secondary_non_oe_scratch_fails": (sec.count("FAILED") if sec else None)}


def label_of(counts: Dict[str, bool], complete: Dict[str, bool]) -> str:
    if not all(complete.get(c) for c in CELLS):
        return "INCOMPLETE"
    if counts["on_frozen"] and counts["off_xabs"]:
        return "EITHER"
    if counts["on_frozen"]:
        return "SEARCH"
    if counts["off_xabs"]:
        return "DEVELOPMENTAL"
    if counts["on_xabs"]:
        return "BOTH_REQUIRED"
    return "NONE"


def seed_label(cells: Dict[str, Dict]) -> Dict:
    comp = {c: cells[c]["complete"] for c in CELLS}
    lo = label_of({c: cells[c]["counts_LO"] for c in CELLS}, comp)
    hi = label_of({c: cells[c]["counts_HI"] for c in CELLS}, comp)
    k_cen = max(cells[c]["n_censored"] for c in ("on_frozen", "on_xabs"))
    k_nr = max(cells[c]["n_not_run"] for c in ("on_frozen", "on_xabs"))
    if lo == hi:
        rep = lo
    else:
        rep = "%s (CONDITIONAL: %d OE scratches censored at 3,600 CPU-s%s; unconditional: %s)" % (
            hi, k_cen, (", %d not run" % k_nr) if k_nr else "", lo)
    return {"label_LO": lo, "label_HI": hi, "determined": lo == hi, "reported": rep, "unconditional": lo}


def stability(labels: List[str]) -> Dict:
    """labels for seeds 0, 1, 2 (unconditional)."""
    cnt = {}
    for l in labels:
        cnt[l] = cnt.get(l, 0) + 1
    top = max(cnt, key=lambda l: (cnt[l], l == labels[0]))
    if cnt[top] == len(labels):
        return {"label": top, "stability": "STABLE", "per_seed": labels}
    if cnt[top] * 2 > len(labels):
        return {"label": top, "stability": "MAJORITY", "per_seed": labels}
    return {"label": labels[0], "stability": "SEED_UNSTABLE", "per_seed": labels}


def dominant(fams: List[Dict]) -> Dict:
    nq = [f for f in fams if not f["qualified"]]
    cls = {"HORIZON": 0, "UD-R1": 0, "UD-EXTRACT": 0, "OTHER": 0}
    resid = {}
    for f in nq:
        if f["link"] in KP.HORIZON_LINKS:
            c = "HORIZON"
        elif f.get("ud") and f["ud"]["ud"] in ("UD-R1", "UD-EXTRACT"):
            c = f["ud"]["ud"]
        else:
            c = "OTHER"
        cls[c] += 1
        key = "%s%s" % (f["link"], ("/" + f["ud"]["ud"]) if f.get("ud") else "")
        resid[key] = resid.get(key, 0) + 1
    dom = next((c for c in ("HORIZON", "UD-R1", "UD-EXTRACT") if 2 * cls[c] > len(nq)), "MIXED") if nq else None
    return {"dominant": dom, "classes": cls, "residual_links": resid, "n_not_qualified": len(nq)}


def attribution(fams_by_cell: Dict[str, List[Dict]]) -> Dict:
    """Per-family attribution over the off_frozen failures (A3 PRIMARY output)."""
    idx = {c: {(f["world"], f["family_id"]): f for f in fams_by_cell[c]} for c in CELLS}
    rows, tally = [], {"OE-only": 0, "X-ABS-only": 0, "both-only": 0, "either": 0, "neither": 0}
    for key, f0 in sorted(idx["off_frozen"].items()):
        if f0["qualified"]:
            continue
        oe, xa, bo = (idx["on_frozen"][key]["qualified"], idx["off_xabs"][key]["qualified"],
                      idx["on_xabs"][key]["qualified"])
        cat = ("either" if oe and xa else "OE-only" if oe else "X-ABS-only" if xa else "both-only" if bo
               else "neither")
        tally[cat] += 1
        r = {"world": key[0], "family_id": key[1], "category": cat, "off_frozen_link": f0["link"],
             "on_frozen": oe, "off_xabs": xa, "on_xabs": bo}
        if cat == "neither":
            fx = idx["on_xabs"][key]
            r["residual_link"] = fx["link"]
            r["residual_detail"] = fx["detail"]
            r["residual_ud"] = fx.get("ud", {}).get("ud")
        if (oe or xa) and not bo:
            r["note"] = "fixed by a single factor but NOT in on_xabs (interaction)"
        rows.append(r)
    return {"families": rows, "tally": tally}


def effects(cs: Dict[str, Dict]) -> Dict:
    q = {c: cs[c]["chain_qualified"] for c in CELLS}
    return {"chain_qualified": q,
            "OE_main_effect": (q["on_frozen"] + q["on_xabs"] - q["off_frozen"] - q["off_xabs"]) / 2,
            "XABS_main_effect": (q["off_xabs"] + q["on_xabs"] - q["off_frozen"] - q["on_frozen"]) / 2,
            "interaction": q["on_xabs"] - q["on_frozen"] - q["off_xabs"] + q["off_frozen"]}


def masking(units_on_frozen: Dict, units_on_xabs: Dict) -> Dict:
    changed = sorted(k for k in units_on_xabs if units_on_xabs[k].get("lambda") != units_on_frozen.get(k, {})
                     .get("lambda") or units_on_xabs[k].get("status") != units_on_frozen.get(k, {}).get("status"))
    fired = sorted(k for k, u in units_on_xabs.items() if u.get("extraction") == "xabs_absorbed")
    return {"xabs_changed_any_stone_in_OE_cells": bool(changed or fired), "units_changed": changed,
            "units_xabs_fired": fired}


# ================================================================ the result
def analyse(root, worlds: List[str], out_dir, budget=KP.BUDGET, frozen_dir=None, expect_off_frozen=None,
            expect_off_xabs=None, utc_start=None, ledger=None) -> Dict:
    data = collect(root, worlds, out_dir, budget)
    kps = data["_kps"]
    per_seed = {}
    for s in SEEDS:
        cs = {c: cell_summary(data["families"][(c, s)], data["units"][(c, s)], kps) for c in CELLS}
        if s != 0:            # off_frozen at seeds 1/2 has no own scratch here: its scratch = seed-0 non-OE (A3)
            pass
        per_seed[s] = {"cells": cs, "label": seed_label(cs), "effects": effects(cs),
                       "attribution": attribution({c: data["families"][(c, s)] for c in CELLS}),
                       "masking": masking(data["units"][("on_frozen", s)], data["units"][("on_xabs", s)]),
                       "reading_cell": READING_CELL,
                       "reading_cell_dominant": dominant(data["families"][(READING_CELL, s)])}
    lab_unc = [per_seed[s]["label"]["unconditional"] for s in SEEDS]
    lab_hi = [per_seed[s]["label"]["label_HI"] for s in SEEDS]
    st = stability(lab_unc)
    st_hi = stability(lab_hi)
    s0 = per_seed[0]
    final = st["label"]
    conditional = any(not per_seed[s]["label"]["determined"] for s in SEEDS)
    reported = final if not conditional or st_hi["label"] == final else "%s (CONDITIONAL: HI bound %s)" % (
        final, st_hi["label"])
    dom = s0["reading_cell_dominant"]
    if final in ("SEARCH", "BOTH_REQUIRED", "DEVELOPMENTAL", "EITHER"):
        reading = INTERPRETATION[final]
        if final == "SEARCH" and s0["masking"]["xabs_changed_any_stone_in_OE_cells"]:
            reading += "; MASKING: X-ABS changed stones in the OE cells (%s)" % ", ".join(
                s0["masking"]["units_changed"] or s0["masking"]["units_xabs_fired"])
    elif final == "NONE":
        reading = INTERPRETATION["NONE/" + (dom["dominant"] or "MIXED")]
        if dom["dominant"] == "MIXED":
            reading += ": %s" % json.dumps(dom["residual_links"], sort_keys=True)
    else:
        reading = INTERPRETATION["INCOMPLETE"]
    # A8 fallback-off row (priority 2)
    fb0 = data["families"].get(("on_xabs_fb0", 0), [])
    fb = None
    if fb0 and all(f["complete"] for f in fb0):
        c0 = cell_summary(fb0, data["units"][("on_xabs_fb0", 0)], kps)
        alt = dict(s0["cells"], on_xabs=c0)
        lab_alt = seed_label(alt)
        fb = {"cell": c0, "label_if_substituted": lab_alt,
              "agrees_with_fallback_on": lab_alt["unconditional"] == s0["label"]["unconditional"],
              "A1_C": ("recommendation names the fallback-off row" if lab_alt["unconditional"] !=
                       s0["label"]["unconditional"] else "both rows agree (state both)")}
    checks = reproduction_checks(s0["cells"], data, frozen_dir, worlds, expect_off_frozen, expect_off_xabs, budget)
    return {"label": KP._label(root), "root": str(root), "worlds": worlds, "budget": budget,
            "utc_start": utc_start, "utc_end": utc_now(),
            "REPAIR_CLASS": reported, "REPAIR_CLASS_unconditional": final, "stability": st["stability"],
            "per_seed_labels": {s: per_seed[s]["label"] for s in SEEDS}, "stability_HI": st_hi,
            "reading": reading, "scope": SCOPE, "claim_limits": CLAIM_LIMITS,
            "PRIMARY_attribution_seed0": s0["attribution"], "per_seed": per_seed,
            "fallback_off_on_xabs": fb, "reproduction_checks": checks, "compute_ledger": ledger,
            "rules": {"cell_counts": "complete AND 5q >= 4n AND 5*scratch_fails >= 4n (LO: CENSORED/NOT_RUN = not "
                                     "failed; HI: = failed)",
                      "labels": "EITHER / SEARCH / DEVELOPMENTAL / BOTH_REQUIRED / NONE (prereg table); INCOMPLETE",
                      "stability": "STABLE 3/3, MAJORITY 2/3 (majority label), SEED_UNSTABLE (seed-0 label)",
                      "reading_cell": READING_CELL, "scratch_cap_s": OE_SCRATCH_CAP_S,
                      "extension_s": OE_SCRATCH_EXTENSION_S, "oe_scratch_envelope_s": OE_SCRATCH_ENVELOPE_S}}


def reproduction_checks(cs0, data, frozen_dir, worlds, expect_off_frozen, expect_off_xabs,
                        budget=KP.BUDGET) -> Dict:
    out = {}
    of = cs0["off_frozen"]
    if frozen_dir is not None:
        p = Path(frozen_dir) / ("KPA1_POOLED_%s.json" % KP.Config(budget=budget).key())
        if p.exists():
            fv = json.loads(p.read_text())["verdict"]
            links = {k: v for k, v in fv["first_failing_link_counts"].items() if v and k in KP.LINKS}
            out["off_frozen_equals_frozen_pooled"] = (fv["chain_qualified"] == of["chain_qualified"]
                                                      and fv["scratch_fails"] == of["scratch_fails_LO"]
                                                      and links == of["first_failing_link_counts"])
            out["frozen_pooled"] = {"chain_qualified": fv["chain_qualified"], "scratch_fails": fv["scratch_fails"],
                                    "links": links}
    if expect_off_frozen is not None:
        out["off_frozen_assert"] = {"expected": expect_off_frozen, "got": of["chain_qualified"],
                                    "pass": of["chain_qualified"] == expect_off_frozen}
    if expect_off_xabs is not None:          # EXPECTED, pending reproduction: REPORTED, never asserted (review v2)
        ox = cs0["off_xabs"]
        out["off_xabs_expected_pending_reproduction"] = {
            "expected": expect_off_xabs, "got": ox["chain_qualified"], "complete": ox["complete"],
            "status": ("REPRODUCED" if ox["complete"] and ox["chain_qualified"] == expect_off_xabs else
                       "NOT_REPRODUCED (reported, not asserted)" if ox["complete"] else "INCOMPLETE")}
    return out
