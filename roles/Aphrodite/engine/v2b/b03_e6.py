"""BETA-03 E6: the PRE-REGISTERED attack runner for E5-N (beta03/windows/E5N_PREREG.md s6 + AMENDMENT A1 items 3, 6).

Reads ONLY E5-N / E1 receipts (beta03/runs/E5N/*, beta03/runs/E1/*, beta03/runs/SUPPLY/PLAN_B.json); never edits them.
Every new output goes to beta03/runs/E6/. Machinery is imported unchanged (b02 walks, r7e._walk, b03_e5._w5p_run,
engine/w5p/promote.instantiate, w8_lin.py). Which branch runs is decided by E5N_RESULT.json's label, mechanically:

  label NO                -> NEGATIVE branch: first-broken-link diagnosis on the recorded rows. Pure read, no compute.
  label YES_PENDING_E6    -> POSITIVE branch (A1 item 6):
     (a) PLAIN control   arm D's selected library minus every body outside G5 (a17.g5_bodies); empty entries dropped;
     (b) SHAM swap       inherited primitive id(s) in arm D's promoted-form (depth-2) entries replaced by the id of
                         promote(the pair's L_SHAM schema); schemas re-instantiated with w5p.promote.instantiate;
         both re-walk the SAME transfer cells (r7e._walk via b02._pool_walks, cap 1M, T4 v1a) on the pair's common
         residual families. DROP = strictly fewer acquired common-residual families than arm D.
         DEPENDENCY_CONFIRMED iff DROP under (a) AND (b) in >= 2/3 of the SECOND-LEVEL pairs.
     (c) label scramble  entry `name` fields renamed to seeded random strings on 2 pairs (the first two SECOND-LEVEL
                         pairs in seed order); every walk result must equal arm D's recorded result (invariance).
     (d) unseen lineages W8 LIN 120-127 (unchanged w8_lin.py -> NEW file W8_SUPPLIES_B03E6.json; T51 foundry, A19
                         roles + T12 extras exactly as b02.stage_supply/plan_seed); E1 block-A donor libraries
                         72..79 in order -> 120..127; arms C (L_P) and D (L_g11), promotable (b03_e5._w5p_run);
                         common residual from the L_P / L_g11 START walks (frozen + hashed before any recipient);
                         PASS iff sum(D - C) > 0 AND at most 1 pair has D < C.
     R8_UNDER_PROMOTION = YES iff YES_PENDING_E6 AND DEPENDENCY_CONFIRMED AND (c) AND (d); else NO_AFTER_ATTACK with
     the failed component(s) named.
  any other label (MEASUREMENT_FAILED / INSTRUMENT_UNVALIDATED) -> the negative-branch diagnosis is still written
     (it reports the MEASUREMENT / SUPPLY link); no attack is run.

Declared engineering choices (decided before any E5-N outcome; none reads an outcome):
  - E6 walks are run only on the pair's COMMON-RESIDUAL families (the only families the acquisition measure counts),
    both cells, on the identical r7e._walk cells (label "T51-LIN<n>-rx", cell index 0/1) used by E5-N scoring.
  - A pair with no L_SHAM (b03_e5 E5N-3 rule) cannot be swapped: it counts as NO DROP under (b) (conservative
    against YES) and is listed as SHAM_UNAVAILABLE.
  - (b) re-instantiates EVERY schema of a promoted-form entry (an entry whose schema/schemas contains a promoted
    node) under the swapped registry; entries without a promoted node (the inherited START entries) are unchanged,
    so the base-grammar expressivity and the inherited plain abstraction are kept.
  - (d) common residual and recipient walks cover all 32 TRANSFER families for the starts (needed to define the
    residual) and only the common-residual families for the recipients.
Stages: diagnose | positive {build|walk|report} [w] | unseen {gen|supply|freeze|starts|recip|score|report} [w] |
        report | known
"""
import os
os.environ.setdefault("V2B_T51_DIR", "T04_T51")
import copy  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from collections import defaultdict  # noqa: E402
from pathlib import Path  # noqa: E402

import b03  # noqa: E402   (imports b02 first: the a18.TAG import-order guard)
import b03_e5  # noqa: E402
import b02  # noqa: E402

R = b02.R
log, wj, rj, sha = b02.log, b02.wj, b02.rj, b02.sha
TAG_D = "L_g11|" + b03_e5.MACH5
TAG_C = "L_P|" + b03_e5.MACH5
TAG_F = "L_SHAM|" + b03_e5.MACH5
UNSEEN = list(range(120, 128))
UNSEEN_DONORS = list(range(72, 80))
SUPPLY_FILE_E6 = "W8_SUPPLIES_B03E6.json"
W8_N_FAMILIES = 144                         # as W8_SUPPLIES_B03.json (every LIN supply holds 144 admitted families)
BARE = re.compile(r"P_[0-9a-f]{12}\(\{H\}\)")
PID = re.compile(r"P_[0-9a-f]{12}")
LINKS = ["CANDIDACY", "SELECTION", "TRANSFER", "SEARCH_BUDGET"]


class Ctx:
    """All receipt paths in one place, so the runner can be pointed at synthetic / exposed fixtures in tests."""

    def __init__(self, e1d=None, e5d=None, e6d=None, plan=None, cap=None, sup=None):
        self.e1d = Path(e1d or b03.E1D)
        self.e5d = Path(e5d or b03_e5.E5D)
        self.e6d = Path(e6d or (b03.B03 / "E6"))
        self.plan = Path(plan or (b02.SUP / "PLAN_B.json"))
        self.sup = Path(sup or (b03.B03 / "SUPPLY"))      # block-A plan (panel) for the unseen stage
        self.cap = int(cap or R.CAP)


# ================================================================== receipts (read-only)
def _rdl(p):
    return R.rdl(Path(p))


def libraries(ctx):
    """E1 libraries (hash-checked, as b03._libs_checked) + E5-N sham libraries (hash-checked, as b03_e5._libs)."""
    L = rj(ctx.e1d / "E1_LIBRARIES.json")
    for d, ls in L["libraries"].items():
        assert all(sha(ls[k]) == L["sha256"][d][k] for k in ls), "E1 library hash mismatch"
    S = rj(ctx.e5d / "E5N_SHAM_LIBRARIES.json")
    assert sha({"sham": S["sham"]}) == S["sha256"], "sham library hash mismatch"
    return L, S["sham"]


def walks(ctx):
    W = {}
    for p in (ctx.e1d / "E1_START_WALKS.jsonl", ctx.e1d / "E1_RECIP_WALKS.jsonl",
              ctx.e5d / "E5N_SHAM_START_WALKS.jsonl", ctx.e5d / "E5N_RECIP_WALKS.jsonl"):
        for x in _rdl(p):
            W[(x["lib"], x["family"], x["cell"])] = x["result"]
    return W


def index(ctx):
    out = []
    for p in (ctx.e1d / "E1_START_INDEX.json", ctx.e1d / "E1_RECIP_INDEX.json", ctx.e5d / "E5N_SHAM_START_INDEX.json",
              ctx.e5d / "E5N_RECIP_INDEX.json"):
        if p.exists():
            out += rj(p)["index"]
    return out


def recip_rows(ctx):
    return {(x["seed"], x["tag"]): x for x in _rdl(ctx.e5d / "E5N_RECIP.jsonl")}


def common_residual(ctx):
    C = rj(ctx.e1d / "E1_COMMON_RESIDUAL.json")
    rec = {k: v for k, v in C.items() if k != "sha256"}
    assert sha(rec) == C["sha256"], "common residual hash mismatch"
    return C["common_residual"]


def _ok(r):
    return bool(r) and not r.get("censored", True)


def acquired(idx, W, C, tag, n):
    """Common-residual families of pair n that `tag`'s library reaches in >= 1 cell (b03.acq_common_from, one cell)."""
    return b03.acq_common_from(idx, W, C, [tag], [n])[tag][n]


def nontrivial_depth2(row):
    return b03_e5._nontrivial_depth2(row)


def _is_promoted_entry(e):
    return any(s and PID.search(s) for s in [e.get("schema")] + list(e.get("schemas") or []))


# ================================================================== library transforms (the attacks)
def plain_library(entries):
    """(a) every body outside G5 removed; entries left with no body (explicit or schema-expanded) dropped."""
    import a17
    import fair as FR
    g5 = set(a17.g5_bodies())
    out = []
    for e in entries:
        e2 = copy.deepcopy(e)
        e2["bodies"] = [b for b in e.get("bodies") or [] if b in g5]
        if FR.entry_bodies(e2):
            out.append(e2)
    return out


def sham_primitive(sham_entries):
    """promote(pair's L_SHAM schema) with the frozen W5P machinery (w5p.donor.promote_start on the sham START)."""
    from w5p import donor as WD
    reg = WD.promote_start(sham_entries)
    assert len(reg) == 1, "an L_SHAM start must carry exactly one schema (got %d)" % len(reg)
    return next(iter(reg.values()))


def swap_schema(schema, inherited_ids, sham_id):
    return PID.sub(lambda m: sham_id if m.group(0) in inherited_ids else m.group(0), schema)


def sham_library(entries, inherited_ids, sham_entries):
    """(b) in every promoted-form entry, inherited primitive id(s) -> the sham primitive's id; every schema of the
    entry re-instantiated under the swapped registry (promote.instantiate). Other entries unchanged."""
    from w5p import promote as W
    sp = sham_primitive(sham_entries)
    reg = {sp.id: sp}
    inh = set(inherited_ids)
    out, swapped = [], []
    for e in entries:
        if not _is_promoted_entry(e):
            out.append(copy.deepcopy(e))
            continue
        e2 = copy.deepcopy(e)
        sch = ([e["schema"]] if e.get("schema") else []) + list(e.get("schemas") or [])
        new = [swap_schema(s, inh, sp.id) for s in sch]
        left = sorted({p for s in new for p in PID.findall(s)} - set(reg))
        assert not left, "swapped schema references a primitive outside the sham registry: %s" % left
        bodies = []
        for s in new:
            bodies += W.instantiate(s, reg)
        e2["bodies"] = list(dict.fromkeys(bodies))
        if e.get("schema"):
            e2["schema"] = new[0]
            e2["schema_expansion"] = W.expand(new[0], reg)
        if e.get("schemas"):
            e2["schemas"] = new[1:] if e.get("schema") else new
        e2["promoted"] = W.lineage_records(reg, [sp.id])
        swapped.append({"from": sch, "to": new, "n_bodies": len(e2["bodies"])})
        out.append(e2)
    return out, {"sham_id": sp.id, "sham_schema": sp.schema, "swapped": swapped}


def scramble_library(entries, n):
    """(c) entry `name` fields renamed to seeded random strings (APHRODITE/B03/E6/SCRAMBLE/<n>)."""
    rng = random.Random(b02.I._seed("APHRODITE/B03/E6/SCRAMBLE/%d" % n))
    out = copy.deepcopy(entries)
    for e in out:
        e["name"] = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(12))
    return out


def _span_to_promoted(entries):
    """Candidates walked before the LAST promoted-form entry is exhausted (keyed walk order = entry order)."""
    import fair as FR
    lib = FR.KLib(entries)
    tot, end = 0, 0
    for e, bodies in zip(lib.entries, lib._bodies):
        tot += len(e["inits"]) * len(bodies) * len(e["finals"])
        if _is_promoted_entry(e):
            end = tot
    return end


# ================================================================== NEGATIVE branch: first broken link (pure read)
def _schema_index_bounds(n_derived, promoted_sorted, s):
    """donor derived list = sorted(all derived schema strings); only the promoted subset is recorded. The index of s
    lies in [rank among promoted, rank + (#plain)]."""
    lo = sum(1 for x in promoted_sorted if x < s)
    return lo, lo + (n_derived - len(promoted_sorted))


def selection_detail(row):
    """For a pair whose arm-D donor derived promoted schemas but selected no non-trivial depth-2 schema: were the
    non-trivial promoted candidates eligible in the recorded selection_table? Exact if the row carries the full
    derived list ('derived_schemas'); otherwise resolved by index bounds where possible."""
    w = row["w5p"]
    tab = row.get("selection_table") or {}
    n_der = row.get("n_derived", 0)
    dp = list(w.get("derived_with_promoted") or [])
    nt = [s for s in dp if not BARE.fullmatch(s)]
    elig = {k for k, v in tab.items() if v.get("eligible")}
    out = {"nontrivial_promoted_derived": nt, "eligible_candidates": sorted(elig),
           "SCHEMA_ALL_eligible": "SCHEMA_ALL" in elig, "per_schema": {}}
    full = row.get("derived_schemas")
    for s in nt:
        if full:
            k = full.index(s)
            out["per_schema"][s] = "ELIGIBLE" if ("SCHEMA_%d" % k) in elig else "INELIGIBLE"
            continue
        lo, hi = _schema_index_bounds(n_der, sorted(dp), s)
        names = ["SCHEMA_%d" % k for k in range(lo, hi + 1)]
        if all(x in elig for x in names):
            out["per_schema"][s] = "ELIGIBLE"
        elif not any(x in elig for x in names):
            out["per_schema"][s] = "INELIGIBLE"
        else:
            out["per_schema"][s] = "UNRESOLVED"
    vals = set(out["per_schema"].values())
    out["kind"] = ("ELIGIBLE_REJECTED" if "ELIGIBLE" in vals else
                   ("NONE_ELIGIBLE" if vals == {"INELIGIBLE"} else
                    ("ONLY_BARE_REEXPRESSIONS" if not nt else "UNRESOLVED_FROM_RECEIPTS")))
    out["exact"] = bool(full)
    return out


def pair_link(row, n, C, idx, W, cap, G5):
    """First broken link of one arm-D pair: CANDIDACY / SELECTION / TRANSFER / SEARCH_BUDGET / NONE (attributed)."""
    w = row["w5p"]
    ev = {"pair": n, "promoted_in_ids": w.get("promoted_in_ids", []), "n_derived": row.get("n_derived"),
          "n_derived_with_promoted": w.get("n_derived_with_promoted", 0),
          "derived_with_promoted": w.get("derived_with_promoted", []), "selected": row.get("selected"),
          "selected_schema": row.get("selected_schema"), "dag_depth_selected": w.get("dag_depth_selected"),
          "cost_total": (w.get("cost") or {}).get("total")}
    nt_der = [s for s in ev["derived_with_promoted"] if not BARE.fullmatch(s)]
    if not w.get("promoted_in_ids"):
        ev.update(link="CANDIDACY", reason="REPRESENTATION_NOTHING_PROMOTED (inherited library carries no schema)")
        return ev
    if ev["n_derived_with_promoted"] == 0:
        ev.update(link="CANDIDACY", reason="NO_PROMOTED_SCHEMA_DERIVED (D1 observation)")
        return ev
    d2 = nontrivial_depth2(row)
    if not d2:
        ev["selection"] = selection_detail(row)
        ev.update(link="SELECTION", reason=("ONLY_BARE_REEXPRESSIONS_DERIVED" if not nt_der else
                                            "DERIVED_NOT_SELECTED:" + ev["selection"]["kind"]))
        return ev
    ev["selected_depth2"] = [{k: p.get(k) for k in ("id", "schema", "expansion", "depth")} for p in d2]
    sel = row["selected_entries"]
    pbodies = set()
    for e in sel:
        if _is_promoted_entry(e):
            pbodies |= set(e.get("bodies") or [])
    idx_by = {(e["genome"], e["seed"], e["family"], e["cell"]): e["lib"] for e in idx}
    fams, ext = [], []
    for f in C[str(n)]:
        cells = []
        for ci in (0, 1):
            k = idx_by.get((TAG_D, n, f, ci))
            r = W.get((k, f, ci)) if k else None
            cells.append({"cell": ci, "walked": r is not None, "censored": (r or {}).get("censored"),
                          "charge": (r or {}).get("charge"), "stopped": (r or {}).get("stopped"),
                          "in_G5": (r["program"][2] in G5) if _ok(r) and r.get("program") else None,
                          "in_promoted_entry": (r["program"][2] in pbodies) if _ok(r) and r.get("program") else None})
        fams.append({"family": f, "cells": cells})
        first = next((c for c in cells if c["walked"] and c["censored"] is False), None)
        if first and first["in_G5"] is False and first["in_promoted_entry"]:
            ext.append(f)
    span = _span_to_promoted(sel)
    cens = sum(1 for x in fams for c in x["cells"] if c["censored"])
    ev.update(common_residual_walks=fams, extend_acquired=ext, promoted_span_end=span, cap=cap,
              censored_walks=cens, acquired=sum(1 for x in fams if any(c["censored"] is False for c in x["cells"])))
    if ext:
        ev.update(link="NONE", reason="ATTRIBUTED_SECOND_LEVEL")
    elif span > cap and cens > 0:
        ev.update(link="SEARCH_BUDGET", reason="promoted-form entries end at candidate %d > cap %d; %d censored walks"
                  % (span, cap, cens))
    else:
        ev.update(link="TRANSFER", reason="promoted-form entries fully inside the cap (end %d <= %d) or no censored "
                                          "walk; no EXTEND acquisition from them" % (span, cap))
    return ev


def diagnose(ctx=None, write=True):
    """Negative-branch diagnosis on the recorded rows (E5N_PREREG s6 'If NO', A1 item 3 channel status)."""
    ctx = ctx or Ctx()
    res5 = rj(ctx.e5d / "E5N_RESULT.json")
    L, _sham = libraries(ctx)
    pairs = L["pairs"]
    C = common_residual(ctx)
    W, idx, D5 = walks(ctx), index(ctx), recip_rows(ctx)
    import a17
    G5 = set(a17.g5_bodies())
    per = []
    for _d, n in pairs:
        row = D5.get((n, TAG_D))
        if row is None:
            per.append({"pair": n, "link": "MISSING_ROW"})
            continue
        per.append(pair_link(row, n, C, idx, W, ctx.cap, G5))
    hist = defaultdict(int)
    for p in per:
        hist[p["link"]] += 1
    have = [p for p in per if p["link"] != "MISSING_ROW"]
    order = {"CANDIDACY": 0, "SELECTION": 1, "TRANSFER": 2, "SEARCH_BUDGET": 2, "NONE": 3}

    def passed(stage):
        return [p for p in have if order[p["link"]] > order[stage]]
    if not res5.get("noop_ok", False):
        first = "MEASUREMENT"
    elif not res5.get("positive_control", False):
        first = "SUPPLY"
    elif not passed("CANDIDACY"):
        first = "CANDIDACY"
    elif not passed("SELECTION"):
        first = "SELECTION"
    elif not [p for p in have if p["link"] == "NONE"]:
        tb = [p["link"] for p in have if p["link"] in ("TRANSFER", "SEARCH_BUDGET")]
        first = ("SEARCH_BUDGET" if tb.count("SEARCH_BUDGET") > tb.count("TRANSFER") else
                 ("TRANSFER" if tb.count("TRANSFER") > tb.count("SEARCH_BUDGET") else "TRANSFER_OR_SEARCH_BUDGET"))
    else:
        failed = []
        P1 = res5.get("P1_enabling_L_g11_vs_L_P_promotable_CONFIRMATORY", {})
        if not (P1.get("p_one_sided", 1) < 0.05 and P1.get("sum", 0) > 0):
            failed.append("P1_ENABLING")
        if len(res5.get("depth2_pairs_with_acquisition", [])) < b03_e5.MIN_DEPTH2_PAIRS:
            failed.append("SECOND_LEVEL_COUNT")
        SH = res5.get("SHAM_L_g11_vs_L_SHAM_promotable_residual_minus_sham_start", {})
        if not (SH.get("p_one_sided", 1) < 0.05 and SH.get("sum", 0) > 0):
            failed.append("SHAM")
        first = "STATISTICAL:" + "+".join(failed or ["NONE"])
    chan = res5.get("label_qualifiers", {}).get("channel_status")
    expect = {"CANDIDACY": "CLOSED_CANDIDACY", "SELECTION": "CLOSED_SELECTION"}
    consistent = (first not in expect or chan == expect[first])
    out = {"label_E5N": res5.get("R8_UNDER_PROMOTION_natural"), "first_broken_link": first,
           "pair_link_histogram": dict(hist), "channel_status_E5N": chan, "consistent_with_E5N_channel": consistent,
           "noop_ok": res5.get("noop_ok"), "positive_control": res5.get("positive_control"),
           "per_pair": per, "cap": ctx.cap,
           "note": "pure read of E5-N/E1 receipts; SELECTION eligibility is exact only when rows carry derived_schemas"}
    if write:
        wj(ctx.e6d / "E6_NEGATIVE_DIAGNOSIS.json", out)
    log("E6 negative: first broken link %s; pairs %s" % (first, dict(hist)))
    return out


# ================================================================== POSITIVE branch
def second_level_pairs(res5):
    return sorted(x["pair"] for x in res5.get("attributed_second_level_pairs", []))


def positive_build(ctx=None):
    """Build + hash the attack libraries (a) PLAIN, (b) SHAM, (c) SCRAMBLE for the SECOND-LEVEL pairs."""
    ctx = ctx or Ctx()
    res5 = rj(ctx.e5d / "E5N_RESULT.json")
    assert res5["R8_UNDER_PROMOTION_natural"] == "YES_PENDING_E6", "positive branch runs only on YES_PENDING_E6"
    L, sham = libraries(ctx)
    donor_of = {n: d for d, n in L["pairs"]}
    D5 = recip_rows(ctx)
    sl = second_level_pairs(res5)
    libs = {}
    for k, n in enumerate(sl):
        row = D5[(n, TAG_D)]
        sel = row["selected_entries"]
        rec = {"D": sel, "PLAIN": plain_library(sel)}
        sh = sham.get(str(donor_of[n]), {})
        if sh.get("entries"):
            rec["SHAM"], rec["sham_detail"] = sham_library(sel, row["w5p"]["promoted_in_ids"], sh["entries"])
        else:
            rec["SHAM"], rec["sham_detail"] = None, {"SHAM_UNAVAILABLE": True}
        if k < 2:
            rec["SCRAMBLE"] = scramble_library(sel, n)
        libs[str(n)] = rec
    out = {"second_level_pairs": sl, "libraries": libs,
           "sha256": {n: {a: sha(v) for a, v in r.items() if a in ("D", "PLAIN", "SHAM", "SCRAMBLE") and v is not None}
                      for n, r in libs.items()}}
    wj(ctx.e6d / "E6_ATTACK_LIBRARIES.json", out)
    log("E6 attack libraries: %d pairs; sha %s" % (len(sl), sha(out)[:16]))
    return out


def _tr_common(plan, n, C):
    keep = set(C[str(n)])
    return [f for f in b02._tr(plan["plan"][str(n)], n) if f["name"] in keep]


def positive_walk(ctx=None, w=2):
    ctx = ctx or Ctx()
    A = rj(ctx.e6d / "E6_ATTACK_LIBRARIES.json")
    for n, r in A["libraries"].items():
        for a, h in A["sha256"][n].items():
            assert sha(r[a]) == h, "attack library hash mismatch"
    plan = rj(ctx.plan)
    C = common_residual(ctx)
    keys, index_, todo = {}, [], {}
    for n_s, r in A["libraries"].items():
        n = int(n_s)
        for arm in ("PLAIN", "SHAM", "SCRAMBLE"):
            if r.get(arm) is None:
                continue
            k = b02._key(r[arm], keys)
            for f in _tr_common(plan, n, C):
                for ci in range(2):
                    index_.append({"seed": n, "genome": "E6_%s" % arm, "family": f["name"], "cell": ci, "lib": k})
                    todo.setdefault((k, f["name"], ci), (k, keys[k], f, ci))
    wj(ctx.e6d / "E6_ATTACK_INDEX.json", {"index": index_})
    have = {(x["lib"], x["family"], x["cell"]) for x in _rdl(ctx.e6d / "E6_ATTACK_WALKS.jsonl")}
    b02._pool_walks([v for kk, v in todo.items() if kk not in have], ctx.e6d / "E6_ATTACK_WALKS.jsonl", w, "E6-attack")


def dependency_confirmed(drops_a, drops_b):
    """A1 item 6: DROP under BOTH (a) and (b) in >= 2/3 of the SECOND-LEVEL pairs."""
    n = len(drops_a)
    both = sum(1 for a, b in zip(drops_a, drops_b) if a and b)
    return n > 0 and 3 * both >= 2 * n, both


def unseen_pass(diffs):
    """A1 item 6(d): sum(D - C) > 0 AND at most 1 pair worse."""
    return sum(diffs) > 0 and sum(1 for x in diffs if x < 0) <= 1


def positive_report(ctx=None):
    ctx = ctx or Ctx()
    res5 = rj(ctx.e5d / "E5N_RESULT.json")
    A = rj(ctx.e6d / "E6_ATTACK_LIBRARIES.json")
    C = common_residual(ctx)
    W = walks(ctx)
    for x in _rdl(ctx.e6d / "E6_ATTACK_WALKS.jsonl"):
        W[(x["lib"], x["family"], x["cell"])] = x["result"]
    idx = index(ctx) + rj(ctx.e6d / "E6_ATTACK_INDEX.json")["index"]
    idx_by = {(e["genome"], e["seed"], e["family"], e["cell"]): e["lib"] for e in idx}
    sl = A["second_level_pairs"]
    rows, da, db, scr = [], [], [], []
    for n in sl:
        r = A["libraries"][str(n)]
        aD = acquired(idx, W, C, TAG_D, n)
        aA = acquired(idx, W, C, "E6_PLAIN", n)
        aB = acquired(idx, W, C, "E6_SHAM", n) if r.get("SHAM") is not None else None
        da.append(aA < aD)
        db.append(aB is not None and aB < aD)
        row = {"pair": n, "acq_D": aD, "acq_PLAIN": aA, "acq_SHAM": aB, "drop_PLAIN": da[-1], "drop_SHAM": db[-1],
               "sham_detail": r.get("sham_detail")}
        if r.get("SCRAMBLE") is not None:
            mism = []
            for f in C[str(n)]:
                for ci in (0, 1):
                    a = W.get((idx_by.get((TAG_D, n, f, ci)), f, ci))
                    b = W.get((idx_by.get(("E6_SCRAMBLE", n, f, ci)), f, ci))
                    if a != b:
                        mism.append([f, ci])
            row["scramble_mismatches"] = mism
            scr.append(not mism)
        rows.append(row)
    dep, both = dependency_confirmed(da, db)
    scramble_ok = len(scr) == min(2, len(sl)) and all(scr)
    U = rj(ctx.e6d / "E6_UNSEEN_RESULT.json") if (ctx.e6d / "E6_UNSEEN_RESULT.json").exists() else None
    unseen_ok = bool(U and U.get("PASS"))
    pending = res5.get("R8_UNDER_PROMOTION_natural") == "YES_PENDING_E6"
    failed = [k for k, v in (("YES_PENDING_E6", pending), ("DEPENDENCY_CONFIRMED", dep),
                             ("LABEL_SCRAMBLE_INVARIANCE", scramble_ok), ("UNSEEN_LINEAGES", unseen_ok)) if not v]
    label = "YES" if not failed else "NO_AFTER_ATTACK"
    out = {"second_level_pairs": sl, "per_pair": rows, "drops_both": both, "DEPENDENCY_CONFIRMED": dep,
           "LABEL_SCRAMBLE_INVARIANCE": scramble_ok, "UNSEEN_LINEAGES": U, "UNSEEN_PASS": unseen_ok,
           "R8_UNDER_PROMOTION": label, "failed_components": failed,
           "unseen_note": None if U else "E6_UNSEEN_RESULT.json absent: (d) not yet run -> counted as not passed"}
    wj(ctx.e6d / "E6_RESULT.json", out)
    log("E6 %s dep=%s (%d/%d) scramble=%s unseen=%s" % (label, dep, both, len(sl), scramble_ok, unseen_ok))
    return out


# ================================================================== (d) unseen lineages LIN 120-127
def unseen_dirs(ctx):
    return ctx.e6d / "UNSEEN", ctx.e6d / "UNSEEN" / "SUPPLY"


def unseen_gen(ctx=None, seeds=None, out_file=None):
    """Unchanged w8_lin.py into a NEW supply file (never W8_SUPPLIES_B03.json). 2-process pool (W8_NPROC=2)."""
    gen = b02.W8 / "w8_lin.py"
    out_file = out_file or (b02.W8 / SUPPLY_FILE_E6)
    seeds = seeds or UNSEEN
    env = dict(os.environ, W8_SUPPLY_FILE=str(out_file), W8_NPROC="2", OMP_NUM_THREADS="1")
    spec = "LIN:%d-%d" % (min(seeds), max(seeds)) if len(seeds) > 1 else "LIN:%d" % seeds[0]
    subprocess.run([sys.executable, str(gen), "gen", str(W8_N_FAMILIES), spec], check=True, env=env)
    return out_file


def plan_from_rows(rows, seeds, panel):
    """b02.stage_supply's plan step, verbatim logic (b02.plan_seed per seed)."""
    return {s: b02.plan_seed(rows, s, panel) for s in seeds}


def unseen_supply(ctx=None, w=2):
    ctx = ctx or Ctx()
    _ud, sd = unseen_dirs(ctx)
    sup = rj(b02.W8 / SUPPLY_FILE_E6)
    draws = [(nm, b, i, f, "LIN:%d" % s) for s in UNSEEN for nm, i, b, f in sup["LIN:%d" % s]["families"]]
    fpath = sd / "FOUNDRY.jsonl"
    sd.mkdir(parents=True, exist_ok=True)
    done = {x["name"] for x in _rdl(fpath)}
    todo = [d for d in draws if d[0] not in done]
    log("E6 unseen foundry todo %d of %d" % (len(todo), len(draws)))
    from concurrent.futures import ProcessPoolExecutor
    with open(fpath, "a", encoding="utf-8") as fh, ProcessPoolExecutor(max_workers=w, initializer=R.T.init_worker) as ex:
        for i, row in enumerate(ex.map(b02._qual, todo, chunksize=4)):
            fh.write(json.dumps(row, sort_keys=True, default=str) + "\n")
            fh.flush()
    rows = _rdl(fpath)
    panel = R.T.panel()
    plan = plan_from_rows(rows, UNSEEN, panel)
    wj(sd / "PLAN_U.json", {"seeds": UNSEEN, "panel": panel, "plan": plan,
                            "supply_sha": sha([sup["LIN:%d" % s] for s in UNSEEN])})
    log("E6 unseen supply: usable %d/%d" % (sum(p["ok"] and p["extras_ok"] for p in plan.values()), len(UNSEEN)))


def unseen_pairs(ctx):
    L, _ = libraries(ctx)
    P = rj(unseen_dirs(ctx)[1] / "PLAN_U.json")
    ok = lambda s: P["plan"].get(str(s), {}).get("ok") and P["plan"][str(s)].get("extras_ok")  # noqa: E731
    return [(d, n) for d, n in zip(UNSEEN_DONORS, UNSEEN) if str(d) in L["libraries"] and ok(n)], L, P


def unseen_starts(ctx=None, w=2):
    """Walk the L_P / L_g11 START libraries on every TRANSFER family of 120..127; freeze + hash the common residual
    BEFORE any recipient runs."""
    ctx = ctx or Ctx()
    ud, _sd = unseen_dirs(ctx)
    pairs, L, P = unseen_pairs(ctx)
    keys, idx_, todo = {}, [], {}
    for d, n in pairs:
        for lb in ("L_P", "L_g11"):
            k = b02._key(L["libraries"][str(d)][lb], keys)
            for f in b02._tr(P["plan"][str(n)], n):
                for ci in range(2):
                    idx_.append({"seed": n, "genome": "START|" + lb, "family": f["name"], "cell": ci, "lib": k})
                    todo.setdefault((k, f["name"], ci), (k, keys[k], f, ci))
    wj(ud / "U_START_INDEX.json", {"index": idx_})
    b02._pool_walks(list(todo.values()), ud / "U_START_WALKS.jsonl", w, "E6-unseen-start")
    W = {(x["lib"], x["family"], x["cell"]): x["result"] for x in _rdl(ud / "U_START_WALKS.jsonl")}
    reach = defaultdict(bool)
    for e in idx_:
        reach[(e["genome"], e["seed"], e["family"])] |= _ok(W.get((e["lib"], e["family"], e["cell"])))
    common = {str(n): sorted(f["name"] for f in b02._tr(P["plan"][str(n)], n)
                             if not any(reach[("START|" + lb, n, f["name"])] for lb in ("L_P", "L_g11")))
              for _d, n in pairs}
    rec = {"rule": "TRANSFER families of the unseen recipient that neither START library (L_P, L_g11) reaches in "
                   "either cell at cap 1M; start walks only; frozen before any recipient", "pairs": pairs,
           "common_residual": common}
    rec["sha256"] = sha(rec)
    wj(ud / "U_COMMON_RESIDUAL.json", rec)
    log("E6 unseen common residual: %d slots; sha %s" % (sum(len(v) for v in common.values()), rec["sha256"][:16]))


def unseen_recip(ctx=None, w=2):
    from concurrent.futures import ProcessPoolExecutor
    ctx = ctx or Ctx()
    ud, _sd = unseen_dirs(ctx)
    assert (ud / "U_COMMON_RESIDUAL.json").exists(), "unseen common residual must be frozen first"
    pairs, L, P = unseen_pairs(ctx)
    out = ud / "U_RECIP.jsonl"
    done = {(x["tag"], x["seed"]) for x in _rdl(out)}
    jobs = [("%s|%s" % (lb, b03_e5.MACH5), "g11", "O10", n, P["plan"][str(n)]["O10"], P["panel"],
             L["libraries"][str(d)][lb]) for d, n in pairs for lb in ("L_P", "L_g11")
            if ("%s|%s" % (lb, b03_e5.MACH5), n) not in done]
    log("E6 unseen recipient jobs %d" % len(jobs))
    with open(out, "a", encoding="utf-8") as fh, ProcessPoolExecutor(max_workers=w, initializer=b03_e5._init) as ex:
        for r in ex.map(b03_e5._w5p_run, jobs):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()


def unseen_score(ctx=None, w=2):
    ctx = ctx or Ctx()
    ud, _sd = unseen_dirs(ctx)
    pairs, _L, P = unseen_pairs(ctx)
    C = rj(ud / "U_COMMON_RESIDUAL.json")["common_residual"]
    keys, idx_, todo = {}, [], {}
    for x in _rdl(ud / "U_RECIP.jsonl"):
        n = x["seed"]
        k = b02._key(x["selected_entries"], keys)
        for f in _tr_common(P, n, C):
            for ci in range(2):
                idx_.append({"seed": n, "genome": x["tag"], "family": f["name"], "cell": ci, "lib": k})
                todo.setdefault((k, f["name"], ci), (k, keys[k], f, ci))
    wj(ud / "U_RECIP_INDEX.json", {"index": idx_})
    have = {(x["lib"], x["family"], x["cell"]) for x in _rdl(ud / "U_START_WALKS.jsonl")}
    have |= {(x["lib"], x["family"], x["cell"]) for x in _rdl(ud / "U_RECIP_WALKS.jsonl")}
    b02._pool_walks([v for kk, v in todo.items() if kk not in have], ud / "U_RECIP_WALKS.jsonl", w, "E6-unseen")


def unseen_report(ctx=None):
    ctx = ctx or Ctx()
    ud, _sd = unseen_dirs(ctx)
    Crec = rj(ud / "U_COMMON_RESIDUAL.json")
    assert sha({k: v for k, v in Crec.items() if k != "sha256"}) == Crec["sha256"], "unseen residual hash mismatch"
    C = Crec["common_residual"]
    pairs = [tuple(p) for p in Crec["pairs"]]
    seeds = [n for _d, n in pairs]
    W = {}
    for p in (ud / "U_START_WALKS.jsonl", ud / "U_RECIP_WALKS.jsonl"):
        for x in _rdl(p):
            W[(x["lib"], x["family"], x["cell"])] = x["result"]
    idx_ = rj(ud / "U_START_INDEX.json")["index"] + rj(ud / "U_RECIP_INDEX.json")["index"]
    acq = b03.acq_common_from(idx_, W, C, [TAG_C, TAG_D], seeds)
    diffs = [acq[TAG_D][n] - acq[TAG_C][n] for n in seeds]
    out = {"pairs": pairs, "acq_D": acq[TAG_D], "acq_C": acq[TAG_C], "diffs_D_minus_C": diffs, "sum": sum(diffs),
           "pairs_worse": sum(1 for x in diffs if x < 0), "PASS": unseen_pass(diffs) if seeds else False,
           "flip_test_descriptive": b02.flip_test(diffs) if seeds else None}
    wj(ctx.e6d / "E6_UNSEEN_RESULT.json", out)
    log("E6 unseen: sum(D-C)=%s worse=%d PASS=%s" % (out["sum"], out["pairs_worse"], out["PASS"]))
    return out


# ================================================================== dispatcher
def report(ctx=None):
    """Mechanical branch choice from the E5-N label."""
    ctx = ctx or Ctx()
    label = rj(ctx.e5d / "E5N_RESULT.json")["R8_UNDER_PROMOTION_natural"]
    if label == "YES_PENDING_E6":
        return positive_report(ctx)
    return diagnose(ctx)


if __name__ == "__main__":
    a = sys.argv[1:]
    w = int(a[-1]) if a and a[-1].isdigit() else 2
    w = min(w, 2)
    if a[0] == "diagnose":
        diagnose()
    elif a[0] == "positive":
        {"build": positive_build, "walk": lambda: positive_walk(w=w), "report": positive_report}[a[1]]()
    elif a[0] == "unseen":
        {"gen": unseen_gen, "supply": lambda: unseen_supply(w=w), "starts": lambda: unseen_starts(w=w),
         "recip": lambda: unseen_recip(w=w), "score": lambda: unseen_score(w=w), "report": unseen_report}[a[1]]()
    elif a[0] == "report":
        report()
    elif a[0] == "known":
        import b03_e6_known
        b03_e6_known.main()
    else:
        raise SystemExit("unknown stage")
