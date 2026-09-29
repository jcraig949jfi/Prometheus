"""E-003 analysis: classes, identification, questions, predictions, gates and the verdict COMPUTED IN CODE (C4.7), plus the
attribution-v0 round-trip. Every number written goes to one output JSON (traceable, C4.7).

Readings of the prereg this seat applies (declared here, before production):
- R1 identification: data label (E, X, j) AND flip not FAILED AND 0 value changes over the R1 draws (groups outside
  {X} | performer; draws where both the write and the birth occur).
  * A locus with NO eligible draw (every such draw suppressed, or no group outside) is "dep-vacuous". It is identified on
    the dependence clause, and the count is reported.
  * The flip clause is observed on the sample only. For births outside it, IDENTIFIED = MOVE + dependence, and the
    sample's per-class flip-FAILED rate is reported as the correction (v4 s2.1, "applied as a correction with a CI").
- Class key (R1): the majority performer entity over written loci (self = W, other = P, none = no ENTITY performer).
  NO_MATERIAL = <= 10% of written loci carry an ENTITY data label. TRANSMISSION (R5) = the majority of written loci are
  IDENTIFIED with data entity W.
- Donor of a locus = its data-label entity. Majority donor = plurality over ENTITY loci; TIED / NONE are counted apart.
- New material = non-ENTITY data labels (INPUT / CONST / COMPUTED / COMPUTED_FROM) at birth. In this world a child is
  never mutated at birth; background mutation is recorded on the persisted vectors (MUT origins).
- Q8c per locus = changes / draws over R2's groups (write-occurring draws), for written ENTITY-MOVE loci with >= 1 draw.
  The estimand is the mean over those loci, with a birth-clustered bootstrap (2,000 resamples, seed 1).
- Painting guard (C4.6): per-birth source diversity = distinct (entity, source locus) / ENTITY loci. P1 and Q8c are
  also reported excluding births with diversity < 0.5.
- B-P1 (Archaeon ruling #956): the whole analysis runs under reading (A) (performer = the frozen tracer's entity bases of
  the store opcode label) and reading (B) (no performer when that label is not ENTITY). Class counts, per-class gates,
  class-keyed Qs and the verdict are reported for both; a verdict that differs is READING-DEPENDENT. The s4 sample and
  the Q4 host pool are drawn under reading (A) only (declared).
- Flip-coverage denominator (Archaeon ruling #951, pre-production): the sampled written loci meeting R1 conditions 1
  AND 3 (ENTITY-MOVE, 0 dependence changes); the condition-1-only variant is a diagnostic. A birth-clustered CI is
  reported, and MARGINAL is a mark only (C4.4). The class key returns TIED on a tie; TIED is gated if it occurs.
- Gated classes are self / other / none (+ TIED). NO_MATERIAL is reported, not gated (R1). CORRECTION 2026-09-29, pre-freeze,
  made AFTER the dry run on r022153: the dry analysis had gated NO_MATERIAL (flip coverage 1/3 over 3 loci). Disclosed
  in the E-003 README.
- Q5: the founder (ORIG) share of capable children's loci is reported. The drift-only null is NOT built (descriptive;
  stated in the report).
- Q8r post-dominator scope: NOT implemented (secondary, non-gating; stated). The whole-execution rule-IMPLICIT share is
  reported.
    python e003_analysis.py --make-sample --export E --q4 Q --out sample.json
    python e003_analysis.py --export E --q4 Q --arms A --flip F --compl C --sample S --out results.json [--v0-schema path]
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import importlib.util
import json
import pathlib
import random
import statistics as st

L = 64
SAMPLE_N = 200
SAMPLE_SEED = 20260929
COMPL_SEED = 20260930
COMPL_FRAC = 0.20


def rows(p):
    return [json.loads(l) for l in gzip.open(p, "rt", encoding="utf-8")]


def is_ent(d):
    return isinstance(d, str) and d[0] in "WP"


def perf_ents(x, reading="A"):
    """B-P1 (Archaeon ruling #956): (A) the frozen tracer's ENTITY bases of the store opcode label; (B) no entity when that
    label is not itself ENTITY (perf_kind != "E")."""
    e = {p[0] for p in x["performer"]}
    return e if (reading == "A" or x.get("perf_kind") == "E") else set()


def perf_class(r, reading="A"):
    W = [x for x in r["loci"] if x["written"]]
    c = collections.Counter()
    for x in W:
        ents = perf_ents(x, reading)
        if not ents:
            c["none"] += 1
        for e in ents:
            c[e] += 1
    if not c:
        return "none"
    mc = c.most_common(2)
    if len(mc) > 1 and mc[0][1] == mc[1][1]:
        return "TIED"                                   # Archaeon ruling #951: TIED is gated if it occurs
    return {"W": "self", "P": "other"}.get(mc[0][0], "none")


def no_material(r):
    W = [x for x in r["loci"] if x["written"]]
    return not W or sum(is_ent(x["data"]) for x in W) <= 0.10 * len(W)


def boot(values_by_birth, n=2000, seed=1):
    """birth-clustered bootstrap of the mean over loci. values_by_birth: list of lists (one per birth)."""
    groups = [g for g in values_by_birth if g]
    if not groups:
        return None, None
    tot = sum(sum(g) for g in groups); cnt = sum(len(g) for g in groups)
    rng = random.Random(seed); ms = []
    for _ in range(n):
        s = c = 0
        for _ in groups:
            g = groups[rng.randrange(len(groups))]; s += sum(g); c += len(g)
        ms.append(s / c)
    ms.sort()
    return round(tot / cnt, 6), [round(ms[int(0.025 * n)], 6), round(ms[int(0.975 * n) - 1], 6)]


def prop_boot(flags_by_birth, n=2000, seed=1):
    """share of births with a True flag, bootstrap over births"""
    xs = [int(x) for x in flags_by_birth if x is not None]
    if not xs:
        return None, None, 0
    rng = random.Random(seed); ms = sorted(sum(xs[rng.randrange(len(xs))] for _ in xs) / len(xs) for _ in range(n))
    return round(sum(xs) / len(xs), 6), [round(ms[int(0.025 * n)], 6), round(ms[int(0.975 * n) - 1], 6)], len(xs)


def make_sample(E, Q4):
    cap = {q["tape"]: q["isolated"]["capable"] for q in Q4}
    strata = collections.defaultdict(list)
    for r in E:
        cls = "NO_MATERIAL" if no_material(r) else perf_class(r)
        strata[(cls, bool(cap.get(r["child_tape"])))].append(r["birth_index"])
    keys = sorted(strata, key=str)
    if sum(len(v) for v in strata.values()) <= SAMPLE_N:
        chosen = sorted(b for v in strata.values() for b in v)
    else:
        base = SAMPLE_N // len(keys); take = {k: min(base, len(strata[k])) for k in keys}
        left = SAMPLE_N - sum(take.values())
        rest = {k: len(strata[k]) - take[k] for k in keys}
        tot = sum(rest.values())
        for k in keys:                                         # remainder proportional to what is left, floor, then by size
            add = min(rest[k], (left * rest[k]) // tot if tot else 0); take[k] += add
        left = SAMPLE_N - sum(take.values())
        for k in sorted(keys, key=lambda k: -(len(strata[k]) - take[k])):
            if left <= 0: break
            if take[k] < len(strata[k]): take[k] += 1; left -= 1
        rng = random.Random(SAMPLE_SEED); chosen = []
        for k in keys:
            chosen += rng.sample(sorted(strata[k]), take[k])
        chosen.sort()
    rng2 = random.Random(COMPL_SEED)
    sub = sorted(rng2.sample(chosen, max(1, round(COMPL_FRAC * len(chosen)))))
    return {"rule": "strata = (class, Q4 isolated capable); equal share per stratum capped at size, remainder proportional; "
                    "random.Random(%d); completeness subset random.Random(%d) 20%%" % (SAMPLE_SEED, COMPL_SEED),
            "strata_sizes": {str(k): len(v) for k, v in strata.items()}, "sample": chosen, "completeness_subset": sub}


def analyse(E, Q4, A, F, C, S, schema_mod, reading="A"):
    sfx = "" if reading == "A" else "_B"
    q4 = {q["tape"]: q for q in Q4}
    arms = {a["birth_index"]: a for a in A}
    flips = {f["birth_index"]: {int(k): v for k, v in f["flip"].items()} for f in F}
    comp = {c["birth_index"]: {int(k): v for k, v in c["completeness"].items()} for c in C}
    sample = set(S["sample"])
    B = []
    for r in E:
        bi = r["birth_index"]; ar = arms[bi]["loci"]; fl = flips.get(bi, {})
        W = [i for i in range(L) if r["loci"][i]["written"]]
        loci = []
        for i in W:
            x = r["loci"][i]; a = ar[i]; d = x["data"]
            move = is_ent(d)
            dep_ok = a["dep_changes" + sfx] == 0
            fv = fl.get(i, {}).get("prefix") if bi in sample else None
            ident = move and dep_ok and fv != "FAILED"
            src = (d[0], int(d[1:])) if move else None
            perf = perf_ents(x, reading)
            implicit = move and any(b[0] in "WPI" and (b[0] == "I" or b[0] not in ({d[0]} | perf)) for b in x["ctrl"])
            loci.append({"i": i, "move": move, "ident": ident, "dep_ok": dep_ok, "dep_vacuous": move and a["dep_draws" + sfx] == 0, "flip": fv, "src": src,
                         "perf": perf, "q8c": (a["q8c_changes" + sfx] / a["q8c_draws" + sfx]) if (move and a["q8c_draws" + sfx]) else None,
                         "qin": (a["qin_changes"] / a["qin_draws"]) if a["qin_draws"] else None,
                         "nonmove": (a["nonmove_changes"] / a["nonmove_draws"]) if ((not move) and a["nonmove_draws"]) else None,
                         "kind": d if isinstance(d, str) else list(d)[0], "implicit": implicit,
                         "exec_ents": {b[0] for b in x["exec"] if b[0] in "WPI"}})
        cls = "NO_MATERIAL" if no_material(r) else perf_class(r, reading)
        n_id = sum(l["ident"] for l in loci)
        ent = [l for l in loci if l["move"]]
        srcs = {(l["src"][0], l["src"][1]) for l in ent}
        div = (len(srcs) / len(ent)) if ent else None
        donors = collections.Counter(l["src"][0] for l in ent if l["ident"])
        donors_all = collections.Counter(l["src"][0] for l in ent)
        maj = (lambda c: "NONE" if not c else ("TIED" if len(c) > 1 and c.most_common(2)[0][1] == c.most_common(2)[1][1] else c.most_common(1)[0][0]))
        perf_maj = collections.Counter(e for l in loci for e in l["perf"])
        q = q4.get(r["child_tape"], {})
        B.append({"bi": bi, "tick": r["tick"], "cls": cls, "n_written": len(loci), "n_ident": n_id,
                  "identifiable": bool(loci) and n_id >= 0.9 * len(loci),
                  "transmission": bool(loci) and sum(1 for l in loci if l["ident"] and l["src"][0] == "W") > 0.5 * len(loci),
                  "div": div, "maj_donor_ident": maj(donors), "maj_donor_all": maj(donors_all),
                  "performer_maj": perf_maj.most_common(1)[0][0] if perf_maj else "none",
                  "native_material": r["native_row"][6], "new_share": sum(1 for l in loci if not l["move"]) / len(loci) if loci else 0.0,
                  "donor_shares": {k: v / len(loci) for k, v in donors_all.items()} if loci else {},
                  "cap_iso": (q.get("isolated") or {}).get("capable"), "cap_host": (q.get("host") or {}).get("capable"),
                  "whether": arms[bi]["whether"], "loci": loci, "orig": [tuple(x["orig"]) for x in r["loci"]],
                  "in_sample": bi in sample})
    out = {"reading": reading, "births": len(B), "classes": dict(collections.Counter(b["cls"] for b in B))}
    nonNM = [b for b in B if b["cls"] != "NO_MATERIAL"]
    TX = [b for b in B if b["transmission"]]
    out["identifiable_share_nonNM"] = prop_boot([b["identifiable"] for b in nonNM])
    out["transmission_births"] = len(TX)
    out["dep_vacuous_loci"] = sum(l["dep_vacuous"] for b in B for l in b["loci"])
    # flip coverage and failure (sample), per class
    fc = {}                                              # ruling #951: denominator = loci meeting R1 conditions 1 AND 3
    for cls in sorted({b["cls"] for b in B}):
        sel = [b for b in B if b["in_sample"] and b["cls"] == cls]
        per_birth = [[int(l["flip"] in ("CONFIRMED", "FAILED")) for l in b["loci"] if l["move"] and l["dep_ok"] and l["flip"] is not None] for b in sel]
        ls = [l for b in sel for l in b["loci"] if l["move"] and l["dep_ok"] and l["flip"] is not None]
        ls1 = [l for b in sel for l in b["loci"] if l["move"] and l["flip"] is not None]
        conf = sum(l["flip"] == "CONFIRMED" for l in ls); fail = sum(l["flip"] == "FAILED" for l in ls); n = len(ls)
        cov_pt, cov_ci = boot(per_birth)
        fc[cls] = {"move_dep_loci": n, "confirmed": conf, "failed": fail, "coverage": round((conf + fail) / n, 6) if n else None,
                   "coverage_ci95": cov_ci, "failed_rate": round(fail / (conf + fail), 6) if conf + fail else None,
                   "diagnostic_cond1_only": {"move_loci": len(ls1), "coverage": round(sum(l["flip"] in ("CONFIRMED", "FAILED") for l in ls1) / len(ls1), 6) if ls1 else None}}
    out["flip_by_class"] = fc
    # completeness (R5) per class
    cc = {}
    for b in B:
        if b["bi"] not in comp: continue
        k = cc.setdefault(b["cls"], {"unnamed": 0, "leaks": 0, "named": 0, "named_effective": 0})
        for v in comp[b["bi"]].values():
            for f in k: k[f] += v[f]
    for v in cc.values():
        v["leak_rate"] = round(v["leaks"] / v["unnamed"], 6) if v["unnamed"] else None
        v["precision"] = round(v["named_effective"] / v["named"], 6) if v["named"] else None
    out["completeness_by_class"] = cc
    # Q8c (R2) overall, per class, transmission (P5), painting guard
    def q8c(sel):
        return boot([[l["q8c"] for l in b["loci"] if l["q8c"] is not None] for b in sel])
    out["Q8c_all"] = q8c(B); out["Q8c_by_class"] = {c: q8c([b for b in B if b["cls"] == c]) for c in out["classes"]}
    out["Q8c_transmission"] = q8c(TX)
    out["Q8c_transmission_div_ge_0.5"] = q8c([b for b in TX if (b["div"] or 0) >= 0.5])
    out["Q_input"] = boot([[l["qin"] for l in b["loci"] if l["qin"] is not None] for b in B])
    out["Q8c_nonmove"] = boot([[l["nonmove"] for l in b["loci"] if l["nonmove"] is not None] for b in B])
    # Q8c-whether (C4.1): per group, birth suppression rate, overall and by class
    def whether(sel):
        o = {}
        for g in ("W", "P", "INPUT"):
            xs = [b["whether"][g]["suppressed"] / b["whether"][g]["draws"] for b in sel if g in b["whether"]]
            o[g] = {"births": len(xs), "mean_suppression": round(st.mean(xs), 6) if xs else None}
        return o
    out["Q8c_whether"] = whether(B); out["Q8c_whether_by_class"] = {c: whether([b for b in B if b["cls"] == c]) for c in out["classes"]}
    # P1 Q-homology on the transmission class (identified W loci)
    def homology(sel):
        return boot([[int(l["src"][1] == l["i"]) for l in b["loci"] if l["ident"] and l["src"][0] == "W"] for b in sel])
    out["P1_homology_transmission"] = homology(TX)
    out["P1_homology_transmission_div_ge_0.5"] = homology([b for b in TX if (b["div"] or 0) >= 0.5])
    out["Q_homology_all_ident"] = boot([[int(l["src"][1] == l["i"]) for l in b["loci"] if l["ident"]] for b in B])
    # P2 native "target" label vs copy-descent majority (C3/C4.3: all identifiable births with native target; also all W/P-majority)
    def p2(sel):
        return prop_boot([(b["maj_donor_ident"] != "P") for b in sel if b["native_material"] == "target" and b["maj_donor_ident"] in ("W", "P")])
    out["P2_native_target_disagrees_identifiable"] = p2([b for b in B if b["identifiable"]])
    out["P2_native_target_disagrees_WPmajority"] = prop_boot([(b["maj_donor_all"] != "P") for b in B if b["native_material"] == "target" and b["maj_donor_all"] in ("W", "P")])
    # Q1, Q3, Q4, Q6, Q7, Q8r
    out["Q1_performer_ne_majority_donor"] = prop_boot([(b["performer_maj"] != b["maj_donor_all"]) for b in B if b["maj_donor_all"] in ("W", "P")])
    out["Q3_departure_uniparental"] = prop_boot([(sorted(b["donor_shares"].values(), reverse=True)[1:2] or [0])[0] >= 0.10 or b["new_share"] >= 0.10
                                                 or (b["maj_donor_all"] in ("W", "P") and b["performer_maj"] != b["maj_donor_all"]) for b in B])
    out["Q4_isolated_capable_children"] = prop_boot([b["cap_iso"] for b in B])
    out["Q4_host_assisted_capable_children"] = prop_boot([b["cap_host"] for b in B])
    out["Q4_material_without_capability_transmission"] = prop_boot([not b["cap_iso"] for b in TX])
    out["Q4_incapable_isolated_but_host_capable"] = prop_boot([(not b["cap_iso"]) and bool(b["cap_host"]) for b in B])
    out["Q6_exec_contains"] = {e: prop_boot([any(e in l["exec_ents"] for l in b["loci"]) for b in B]) for e in ("W", "P", "I")}
    out["Q7_source_diversity_mean"] = round(st.mean([b["div"] for b in B if b["div"] is not None]), 6)
    out["Q7_computed_share"] = boot([[int((not l["move"]) and l["kind"] in ("COMPUTED", "COMPUTED_FROM")) for l in b["loci"]] for b in B])
    out["Q8r_rule_implicit_share_whole_execution"] = boot([[int(l["implicit"]) for l in b["loci"] if l["move"]] for b in B])
    out["Q8r_pdom_scope"] = "NOT_COMPUTED (secondary, non-gating; not implemented)"
    cap_loci = [o for b in B if b["cap_iso"] for o in b["orig"]]
    out["Q5_descriptive_founder_share_of_capable_children_loci"] = round(sum(1 for o in cap_loci if o[0] == "ORIG") / len(cap_loci), 6) if cap_loci else None
    out["Q5_drift_null"] = "NOT_COMPUTED (descriptive only)"
    # ---- gates and verdict (R3, C4.4 point estimate vs floor, CI reported) ------------------------------------------------
    gates = {}
    GATED = ("self", "other", "none", "TIED")            # R1: NO_MATERIAL reported, not gated; TIED gated if it occurs (#951)
    gates["flip_failed_le_1pct"] = {c: (v["failed_rate"] is None or v["failed_rate"] <= 0.01) for c, v in fc.items() if c in GATED}
    gates["flip_coverage_ge_50pct"] = {c: (v["coverage"] is None or v["move_dep_loci"] == 0 or v["coverage"] >= 0.50) for c, v in fc.items() if c in GATED}
    gates["flip_coverage_marginal"] = {c: bool(v["coverage_ci95"] and v["coverage_ci95"][0] < 0.50 <= v["coverage_ci95"][1]) for c, v in fc.items() if c in GATED}
    gates["completeness_leak_le_5pct"] = {c: (v["leak_rate"] is None or v["leak_rate"] <= 0.05) for c, v in cc.items() if c in GATED}
    gates["marginal_ci_note"] = "C4.4: point estimates gate; bootstrap CIs are in the per-class blocks"
    gates["identifiable_ge_80pct_nonNM"] = (out["identifiable_share_nonNM"][0] or 0) >= 0.80
    gates["transmission_ge_30"] = len(TX) >= 30
    out["gates"] = gates
    q_lo, q_hi = (out["Q8c_transmission"][1] or [None, None]) if out["Q8c_transmission"][1] else (None, None)
    p1, p1ci = out["P1_homology_transmission"]
    preds = {"P1": ("HOLDS" if p1ci and p1ci[0] >= 0.90 else ("LOSES" if p1ci and p1ci[1] < 0.90 else "INCONCLUSIVE")),
             "P5": ("HOLDS" if q_hi is not None and q_hi < 0.05 else ("LOSES" if q_lo is not None and q_lo >= 0.05 else "INCONCLUSIVE"))}
    p2v = out["P2_native_target_disagrees_identifiable"]
    preds["P2_engine_native"] = ("HOLDS" if p2v[1] and p2v[1][0] >= 0.10 else ("CERTIFIED" if p2v[1] and p2v[1][1] < 0.10 else "INCONCLUSIVE"))
    out["predictions"] = preds
    # round trip
    rt = roundtrip(B, schema_mod) if schema_mod else {"status": "NOT_RUN (schema not supplied)"}
    out["roundtrip"] = rt
    verdict, why = "VALIDATED", []
    if not all(gates["flip_failed_le_1pct"].values()) or not all(gates["completeness_leak_le_5pct"].values()):
        verdict = "SPEC_DEFECT"; why.append("s4 threshold failed (flip FAILED > 1% or completeness leak > 5%) -- needs named-channel review (BROKEN only with a fixture)")
    elif not gates["identifiable_ge_80pct_nonNM"] or not gates["transmission_ge_30"] or not all(gates["flip_coverage_ge_50pct"].values()):
        verdict = "INCONCLUSIVE"; why.append("identifiability < 80% or transmission < 30 births or flip coverage < 50%")
    else:
        lo = out["Q8c_transmission"][1][0] if out["Q8c_transmission"][1] else None
        if lo is not None and lo > 0.50:
            verdict = "ALTERED"; why.append("DOMINANT: Q8c lower bound > 50% -> v0 weighted dependence field")
        elif lo is not None and lo >= 0.05:
            verdict = "ALTERED"; why.append("WEIGHTED: Q8c lower bound >= 5% -> v0 weighted dependence field")
        elif preds["P1"] == "LOSES":
            verdict = "ALTERED"; why.append("P1 loses -> v0 positional-homology field required")
        elif preds["P5"] == "LOSES":
            verdict = "ALTERED"; why.append("P5 loses -> v0 weighted dependence field")
        elif not (q_hi is not None and q_hi < 0.05) or rt.get("status") != "PASS":
            verdict = "INCONCLUSIVE"; why.append("VALIDATED needs Q8c upper < 5% AND round-trip PASS")
    out["verdict"] = {"verdict": verdict, "why": why, "note": "INSTRUMENT_FAILED is decided by the three-way tracer agreement (s4.3), not here"}
    return out


def roundtrip(B, S):
    """each birth -> attribution-v0 record; schema.check must pass; Q1/Q3/Q4/Q7/homology recomputed from v0 must match"""
    bad = 0; mism = collections.Counter(); n = 0
    for b in B:
        segs = []; loci = {l["i"]: l for l in b["loci"]}
        for i in range(L):
            l = loci.get(i)
            if l is None:
                segs.append(S.seg(i, i + 1, kind="new_unspecified", via="replay_taint")); continue
            if l["move"]:
                segs.append(S.seg(i, i + 1, kind="entity", entity="org:" + l["src"][0], src_lo=l["src"][1], via="replay_taint"))
            else:
                kind = "new_input" if isinstance(l["kind"], str) and l["kind"].startswith("I") else (
                    "new_constant" if isinstance(l["kind"], str) and l["kind"].startswith("C:") else "new_computed")
                segs.append(S.seg(i, i + 1, kind=kind, via="replay_taint"))
        perfs = [{"kind": "organism_code" if e == "W" else "neighbour_organism", "id": "org:" + e, "role": "performer"}
                 for e in sorted({e for l in b["loci"] for e in l["perf"]})] or [{"kind": "organism_code", "id": "org:W", "role": "performer"}]
        dep = [{"intervention": "randomise %s bytes (K=8, single interaction)" % g, "outcome": "birth occurs",
                "result": ("ceases" if v["suppressed"] == v["draws"] else ("persists" if v["suppressed"] == 0 else "altered")),
                "target": {"W": "material", "P": "other", "INPUT": "input"}[g], "contrast": "unmodified replay",
                "rate": v["suppressed"] / v["draws"]} for g, v in b["whether"].items()]
        cap = []
        for c, key in (("exact_self_copy", "cap_iso"), ("host_assisted_copy", "cap_host")):
            if b[key] is not None:
                cap.append({"capability": c, "method": "executed", "ruler": "q4.py 320 trials >= 50%", "result": bool(b[key]),
                            "conditions": {"neighbour": "random" if c == "exact_self_copy" else "run_self_performed_children"}})
        rec = S.record("r022153:b%d" % b["bi"], "BEE", "org:child", production={"process": "executed_write", "evidence": "shadow tracer"},
                       carrier={"performers": perfs, "exec_where": S.NI, "exec_what": S.NI},
                       material={"unit": "byte", "n_units": L, "resolution": "per_locus", "segments": segs},
                       dependence=dep, capability=cap, contrast={"baseline": "unmodified single-interaction replay", "kind": "counterfactual"})
        v = S.check(rec); n += 1
        if v:
            bad += 1; mism["check:" + v[0][:40]] += 1; continue
        d = S.donors(rec)
        maj = max(d, key=d.get)[4:] if d else "NONE"
        if d and len(d) > 1 and sorted(d.values())[-1] == sorted(d.values())[-2]:
            maj = "TIED"
        if maj != b["maj_donor_all"]: mism["majority_donor"] += 1
        if abs(S.new_share(rec) - b["new_share"]) > 1e-9: mism["new_share"] += 1
        sd = S.source_diversity(rec)
        if (sd is None) != (b["div"] is None) or (sd is not None and abs(sd - b["div"]) > 1e-6): mism["source_diversity"] += 1
        if S.capability_of(rec, "exact_self_copy") != (None if b["cap_iso"] is None else bool(b["cap_iso"])): mism["q4"] += 1
    return {"status": "PASS" if not bad and not mism else "FAIL", "records": n, "check_failures": bad, "mismatches": dict(mism)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", required=True); ap.add_argument("--q4", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--make-sample", action="store_true")
    ap.add_argument("--arms"); ap.add_argument("--flip"); ap.add_argument("--compl"); ap.add_argument("--sample")
    ap.add_argument("--v0-schema", default=None)
    a = ap.parse_args()
    E = rows(a.export); Q4 = rows(a.q4)
    if a.make_sample:
        res = make_sample(E, Q4)
    else:
        S = json.loads(pathlib.Path(a.sample).read_text(encoding="utf-8"))
        mod = None
        if a.v0_schema:
            spec = importlib.util.spec_from_file_location("attr_schema", a.v0_schema); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        A_, F_, C_ = rows(a.arms), rows(a.flip), rows(a.compl)
        rA = analyse(E, Q4, A_, F_, C_, S, mod, "A")
        rB = analyse(E, Q4, A_, F_, C_, S, mod, "B")
        dep = [k for k in ("classes", "gates", "predictions", "verdict", "flip_by_class", "completeness_by_class", "Q8c_by_class",
                           "Q8c_whether_by_class", "Q1_performer_ne_majority_donor", "Q3_departure_uniparental")
               if json.dumps(rA.get(k), sort_keys=True, default=str) != json.dumps(rB.get(k), sort_keys=True, default=str)]
        res = {"reading_A": rA, "reading_B": rB, "reading_dependent_fields": dep,
               "verdict": {"A": rA["verdict"]["verdict"], "B": rB["verdict"]["verdict"],
                           "READING_DEPENDENT": rA["verdict"]["verdict"] != rB["verdict"]["verdict"]},
               "gates": {"A": rA["gates"], "B": rB["gates"]}, "predictions": {"A": rA["predictions"], "B": rB["predictions"]}}
        res["inputs_sha256"] = {k: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() for k, p in
                                (("export", a.export), ("q4", a.q4), ("arms", a.arms), ("flip", a.flip), ("compl", a.compl), ("sample", a.sample))}
    pathlib.Path(a.out).write_text(json.dumps(res, indent=1, default=str, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("verdict", "gates", "predictions") if k in res} or {"sample": len(res.get("sample", []))}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
