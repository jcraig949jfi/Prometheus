"""S3 (endogenous abstraction) then S4 (abstraction transplant), AMENDMENT 14
(commit 4a6bbf55d), frozen before this was written.

Stages, each writing its own artifact; no stage reads a later one:
  0 preconditions (S1_PASS, S2_PASS) + G1 conformance, both parts
  1 G2 generator qualification of every Tier-3D family; S6 check
  2 sham distribution, hashed BEFORE the donor runs
  3 donor D1-D6 -> S3_ARTIFACT (frozen, hashed); S3 outcome
  4 (only if ENDOGENOUS_ABSTRACTION = YES) S7 difficulty pilot, positive
    witnesses, recipients, the eight-condition criterion -> S4_RESULTS
Recipients run in a process pool for throughput only; each cell is a pure
function of (family, arm library, i).
"""
import hashlib
import json
import math
import os
import random
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import basis_v4 as G          # noqa: E402
import conformance as CF      # noqa: E402
import engine as E            # noqa: E402
import fair as FR             # noqa: E402
import identity as I          # noqa: E402
import meta_tribunal as M     # noqa: E402
import tier3d as T            # noqa: E402
import cert as CT             # noqa: E402

M.use_provider(T)

N = 16
ESCROW = FR.ESCROW
MAX_HITS = 5
R_OBSERVE = 3
R_VALIDATE = 8
EMITTER = 2
WORKERS = int(os.environ.get("S34_WORKERS", "7"))
DATE = "2026-09-23"


def _log(m):
    print("[s3s4] " + m, flush=True)


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write(name, obj):
    (HERE / name).write_text(json.dumps(obj, indent=1, sort_keys=True, default=str) + "\n",
                             encoding="utf-8")


def _sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def entry(name, bodies, inits=None, **meta):
    e = {"name": name, "inits": list(inits or G.H1_SPACE), "bodies": list(bodies),
         "finals": list(G.FINAL_SPACE)}
    e.update(meta)
    return e


def lib_with(entries):
    return FR.KLib(list(entries) + FR.pristine().entries)


# ---------------------------------------------------------------- stage 0
def stage_preconditions():
    s1l = json.loads((HERE / "S1_LOCAL_GATE_2026-09-24.json").read_text(encoding="utf-8"))
    s2 = json.loads((HERE / "S2_GATE_2026-09-23.json").read_text(encoding="utf-8"))
    if s1l.get("CAMPAIGN_RELEVANT_IDENTITY") != "PASS" or s2.get("OUTCOME") != "S2_PASS":
        raise SystemExit("STOP: CAMPAIGN_RELEVANT_IDENTITY=PASS (ADDENDUM 3) and S2_PASS "
                         "are preconditions")
    std = CF.check()
    rng = random.Random(I._seed("APHRODITE/T3D/CONF/v1"))
    progs = [T.witness(f) for f in T.FAMILY_SPEC] + [
        ("fold", rng.choice(G.INIT_SPACE), rng.choice(G.BODY_SPACE), rng.choice(G.FINAL_SPACE))
        for _ in range(40)]
    # conformance domain = valid inputs + ceiling/failure edges (ADDENDUM 2)
    p2 = [CF.check_whole_program(p, bat, EMITTER) for p in progs for bat in (I.B1, I.B1_BOUNDARY)]
    gate = {"part1_GREEN": std["GREEN"], "part1_checked": std["checked"],
            "part2_programs": len(progs), "part2_checked": sum(x["checked"] for x in p2),
            "part2_mismatches": sum(len(x["mismatches"]) for x in p2)}
    gate["GREEN"] = gate["part1_GREEN"] and gate["part2_mismatches"] == 0
    _log("G1 conformance part1=%s (%d) part2 mismatches=%d over %d"
         % (std["GREEN"], std["checked"], gate["part2_mismatches"], gate["part2_checked"]))
    if not gate["GREEN"]:
        raise SystemExit("CONFORMANCE GATE RED -- no run begins")
    return gate


# ---------------------------------------------------------------- stage 1
def _qual(f):
    return f, T.qualify_generator(f)


def stage_qualify():
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        quals = dict(ex.map(_qual, sorted(T.FAMILY_SPEC)))
    for f in sorted(quals):
        _log("[gen-qual] %-32s size=%s QUALIFIED=%s" % (f, quals[f]["qualified_dev_size"],
                                                       quals[f]["QUALIFIED"]))
    obs = [f for f in T.OBSERVE if quals[f]["QUALIFIED"]]
    val = [f for f in T.VALIDATE if quals[f]["QUALIFIED"]]
    s6 = {"observe_qualified": obs, "validate_qualified": val,
          "PASS": len(obs) >= 2 and len(val) >= 3}
    return quals, s6


# ---------------------------------------------------------------- stage 2
def _body_class(b):
    return I.behavior_id(("fold", "0", b, "acc"), True) + I.behavior_id(("fold", "1", b, "acc"), True)


def stage_shams():
    """8 shams: 6 random H2 behavior-class representatives + 1 random
    one-hole schema from the LGG of a random pair of H2 bodies."""
    by_cls = {}
    for b in G.H2_SPACE:
        by_cls.setdefault(_body_class(b), []).append(b)
    reps = sorted(min(v, key=lambda s: (len(s), s)) for v in by_cls.values())
    shams = []
    for k in range(8):
        rng = random.Random(I._seed("APHRODITE/T3D/SHAM/v1/%d" % k))
        bodies = sorted(rng.sample(reps, 6))
        schema = None
        while schema is None:
            a, b = rng.sample(G.H2_SPACE, 2)
            g, table = T.lgg(I.normalise(I.parse(a)), I.normalise(I.parse(b)))
            if len(table) == 1 and not g[0].startswith("hole"):
                schema = T.schema_src(g)
        inst = T.instantiate(schema)
        shams.append({"k": k, "bodies": bodies, "schema": schema,
                      "entries": [entry("sham_%d" % k, sorted(set(bodies + inst)), ["0", "1"],
                                        sham_schema=schema)]})
    for s in shams:
        s["sha256"] = lib_with(s["entries"]).sha256()
    return {"h2_body_classes": len(reps), "shams": shams}


# ---------------------------------------------------------------- stage 3
def _cell_cost(args):
    name, entries, fam, r, size = args
    lib = lib_with(entries) if entries is not None else FR.pristine()
    c = FR.Cell(T, fam, r, size, label="T3D-val")
    return (name, fam, r), c.cost(lib)[0]


def stage_donor(quals, s6):
    t0 = time.perf_counter()
    meta = 0
    base = FR.pristine()
    observed = []                                   # D1
    for fam in s6["observe_qualified"]:
        size = quals[fam]["qualified_dev_size"]
        for r in range(R_OBSERVE):
            c = FR.Cell(T, fam, r, size, label="T3D-obs")
            esc = E.Escrow(ESCROW)
            hits = FR.search_collect(base, c.parsed, esc, ESCROW, c.seed, max_hits=1)
            meta += esc.spent
            if hits:
                observed.append({"family": fam, "r": r, "program": list(hits[0][0]),
                                 "examples": c.examples})
    classes = {}                                    # D2
    for o in observed:
        classes.setdefault(I.behavior_id(tuple(o["program"]), True), []).append(o)
    cls_list, cert_log = [], []
    for bid, obs in sorted(classes.items()):         # D3 + certificates C1-C3 (ADDENDUM 3)
        mem = T.class_members(tuple(obs[0]["program"]), obs[0]["examples"])
        observed_progs = [tuple(o["program"]) for o in obs]
        rec = CT.certify(observed_progs + mem, anchor=observed_progs[0])
        cert_log.append({"provisional_behavior_id": bid, "certificate": rec})
        if rec["PASS"]:
            groups = [(observed_progs, mem)]
        else:                                        # split BEFORE downstream use (s4)
            _log("[cert] SPLIT provisional class %s.. into %d sub-buckets"
                 % (bid[:10], rec["sub_buckets"]))
            sigbat = list(I.B1) + CT.b_cert() + CT.adversarial(observed_progs + mem)
            sub = {}
            for p in dict.fromkeys(observed_progs + mem):
                sub.setdefault(I.values(p, True, sigbat), []).append(p)
            groups = [([p for p in v if p in observed_progs], [p for p in v if p in mem])
                      for v in sub.values() if any(p in observed_progs for p in v)]
        for gobs, gmem in groups:
            fams = sorted({o["family"] for o in obs if tuple(o["program"]) in gobs})
            cls_list.append({"behavior_id": bid, "certified": True, "split_from_provisional":
                             not rec["PASS"], "families": fams,
                             "observed_programs": [list(p) for p in gobs],
                             "members": [list(p) for p in gmem],
                             "member_bodies": sorted({p[2] for p in gmem})})
            _log("[D3] class %s.. from %s: %d members, %d distinct bodies (certified%s)"
                 % (bid[:10], fams, len(gmem), len(cls_list[-1]["member_bodies"]),
                    ", split" if not rec["PASS"] else ""))
    derived = T.derive_schemas([c["member_bodies"] for c in cls_list])     # D4
    _log("[D4] candidate schemas: %s" % [d["schema"] for d in derived])

    memorised = sorted({b for c in cls_list for b in c["member_bodies"]})
    cands = {"UNCHANGED": None,
             "MEMORISE": [entry("memorised", memorised)]}
    for k, d in enumerate(derived):                  # D5
        cands["SCHEMA_%d" % k] = [entry("derived_%d" % k, T.instantiate(d["schema"]),
                                        derived_schema=d["schema"])]
    if len(derived) > 1:
        allb = []
        for d in derived:
            allb += T.instantiate(d["schema"])
        cands["SCHEMA_ALL"] = [entry("derived_all", list(dict.fromkeys(allb)),
                                     derived_schemas=[d["schema"] for d in derived])]
    libs = {n: (lib_with(e) if e is not None else base) for n, e in cands.items()}
    hashes = {n: l.sha256() for n, l in libs.items()}
    bad = {n: l.desugars()[1] for n, l in libs.items() if not l.desugars()[0]}
    if bad:
        raise SystemExit("STOP: a candidate library does not desugar into G4: %s" % bad)

    jobs = [(n, e, f, r, quals[f]["qualified_dev_size"])     # D6
            for n, e in cands.items() for f in s6["validate_qualified"] for r in range(R_VALIDATE)]
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        costs = dict(ex.map(_cell_cost, jobs, chunksize=2))
    meta += sum(costs.values())
    cell_keys = [(f, r) for f in s6["validate_qualified"] for r in range(R_VALIDATE)]
    per = {n: [costs[(n, f, r)] for f, r in cell_keys] for n in cands}
    table = {}
    for n in cands:
        row = FR.paired_summary(per["UNCHANGED"], per[n])
        row.update({"sha256": hashes[n], "size": libs[n].size(), "costs": per[n],
                    "eligible": n != "UNCHANGED" and row["lower95_one_sided"] > 0})
        table[n] = row
        _log("[D6] %-11s mean cost %.0f saving %.0f lower95 %.0f eligible=%s"
             % (n, row["mean_cost"], row["mean_paired_saving"], row["lower95_one_sided"],
                row["eligible"]))
    elig = [n for n in table if table[n]["eligible"]]
    chosen = (min(elig, key=lambda n: (-table[n]["mean_paired_saving"], table[n]["size"],
                                       table[n]["sha256"])) if elig else "UNCHANGED")
    carries_schema = chosen.startswith("SCHEMA")
    pos = set(T.instantiate("(acc + {H})"))
    art = {"written_utc": _now(), "observed": [{k: v for k, v in o.items() if k != "examples"}
                                               for o in observed],
           "classes": cls_list, "class_certificates": cert_log,
           "GLOBAL_BEHAVIOR_IDENTITY": "FAIL (provisional buckets; certificates govern use)",
           "derived_schemas": derived,
           "derived_equal_to_positive_control_instantiations_REPORTED_ONLY": {
               d["schema"]: set(T.instantiate(d["schema"])) == pos for d in derived},
           "candidates": {n: {"entries": cands[n], "sha256": hashes[n]} for n in cands},
           "selection": {"table": table, "cells": cell_keys, "selected": chosen},
           "selected_sha256": hashes[chosen], "selected_entries": cands[chosen],
           "meta_charges": meta, "seconds": round(time.perf_counter() - t0, 1),
           "ENDOGENOUS_ABSTRACTION": "YES" if carries_schema else "NO"}
    return art


# ---------------------------------------------------------------- stage 4
def run_recipient(args):
    fam, arm, entries, i, size, label = args
    lib = lib_with(entries) if entries is not None else FR.pristine()
    c = FR.Cell(T, fam, i, size, label=label)
    esc = E.Escrow(ESCROW)
    hits = FR.search_collect(lib, c.parsed, esc, ESCROW, c.seed, max_hits=MAX_HITS)
    fp, first = 0, None
    for prog, coord, ch in hits:
        art = M.artifact_for(fam, prog, EMITTER)
        trib = M.MetaTribunal.after_freeze(art, fam)
        sc = trib.score(art)
        if trib.qualified(sc):
            first = {"charges": ch, "coordinate": coord, "program": list(prog),
                     "bytes": len(art.bytes), "sha256": art.sha256}
            break
        fp += 1
    row = {"recipient": i, "arm": arm, "family": fam, "label": label, "escrow_spent": esc.spent,
           "hits": len(hits), "qualified": first is not None,
           "charges": first["charges"] if first else None,
           "coordinate": first["coordinate"] if first else None,
           "solution_program": first["program"] if first else None,
           "solution_behavior_id": (I.behavior_id(tuple(first["program"]), True) if first else None),
           "artifact_bytes": first["bytes"] if first else None,
           "artifact_sha256": first["sha256"] if first else None, "false_positives": fp}
    return (fam, arm, label, i), row


def _pool_rows(jobs):
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        return dict(ex.map(run_recipient, jobs, chunksize=1))


def summarise(rows):
    q = [r for r in rows if r["qualified"]]
    hits = sum(r["hits"] for r in rows)
    return {"PRIMARY_censored_effort": round(statistics.mean(
        [r["charges"] if r["qualified"] else ESCROW for r in rows]), 1),
        "qualified": len(q), "n": len(rows),
        "false_positives": sum(r["false_positives"] for r in rows), "hits": hits,
        "fp_fraction_of_hits": round(sum(r["false_positives"] for r in rows) / hits, 4) if hits else 0.0,
        "solution_behavior_ids": sorted({r["solution_behavior_id"] for r in q}),
        "median_artifact_bytes": statistics.median([r["artifact_bytes"] for r in q]) if q else None}


def stage_transfer(quals, shams, art):
    arms = {"DERIVED": art["selected_entries"], "PRISTINE": None,
            "POSITIVE_CONTROL": [entry("positive_control", T.instantiate("(acc + {H})"),
                                       schema="(acc + {H})")],
            "MEMORISE": art["candidates"]["MEMORISE"]["entries"]}
    for s in shams["shams"]:
        arms["SHAM_%d" % s["k"]] = s["entries"]
    libs = {a: (lib_with(e) if e is not None else FR.pristine()) for a, e in arms.items()}
    bad = {a: l.desugars()[1] for a, l in libs.items() if not l.desugars()[0]}
    if bad:
        raise SystemExit("STOP: an arm does not desugar into G4: %s" % bad)
    cand = [f for f in T.TRANSFER if quals[f]["QUALIFIED"]]
    witness_ok = {}
    for f in cand:                                   # positive-control witness
        a = M.artifact_for(f, T.witness(f), EMITTER)
        tr = M.MetaTribunal.after_freeze(a, f)
        witness_ok[f] = tr.qualified(tr.score(a))
    cand = [f for f in cand if witness_ok[f]]
    ctrl = [a for a in arms if a not in ("DERIVED", "MEMORISE")]      # S7: DERIVED excluded
    pilot = _pool_rows([(f, a, arms[a], i, quals[f]["qualified_dev_size"], "T3D-pilot")
                        for f in cand for a in ctrl for i in range(N)])
    solvable = {}
    for f in cand:
        best = {a: sum(pilot[(f, a, "T3D-pilot", i)]["qualified"] for i in range(N)) for a in ctrl}
        solvable[f] = {"pilot_qualified_by_arm": best, "SOLVABLE": max(best.values()) >= 8}
    admitted = [f for f in cand if solvable[f]["SOLVABLE"]]
    unseen = [f for f in admitted if f in T.UNSEEN_BODY]
    _log("[S7] admitted %s (unseen-body %d)" % (admitted, len(unseen)))
    out = {"arms": {a: {"sha256": libs[a].sha256(), "size": libs[a].size()} for a in arms},
           "transfer_qualified": [f for f in T.TRANSFER if quals[f]["QUALIFIED"]],
           "positive_witness": witness_ok, "difficulty_pilot": solvable,
           "admitted": admitted, "unseen_body_admitted": unseen}
    if len(unseen) < 2:
        out["STOP"] = "fewer than two unseen-body families survived S7 -- S4 not tested"
        return out
    rows = _pool_rows([(f, a, arms[a], i, quals[f]["qualified_dev_size"], "T3D-rx")
                       for f in admitted for a in arms for i in range(N)])
    detail = {f: {a: [rows[(f, a, "T3D-rx", i)] for i in range(N)] for a in arms} for f in admitted}
    out["detail"] = detail
    out["per_family"] = {f: {a: summarise(detail[f][a]) for a in arms} for f in admitted}
    out["criterion"] = criterion(out, art, libs)
    return out


def criterion(out, art, libs):
    fams = out["admitted"]
    pf, det = out["per_family"], out["detail"]
    shams = [a for a in pf[fams[0]] if a.startswith("SHAM_")]
    c = {}
    c["1_expressive_equivalence"] = all(l.desugars()[0] for l in libs.values())
    d_all, p_all = [], []
    fam_effect = {}
    for f in fams:
        dr = det[f]["DERIVED"]
        pr = det[f]["PRISTINE"]
        dc = [r["charges"] if r["qualified"] else ESCROW for r in dr]
        pc = [r["charges"] if r["qualified"] else ESCROW for r in pr]
        d_all += dc
        p_all += pc
        s = FR.paired_summary(pc, dc)
        sham_eff = sorted(pf[f][a]["PRIMARY_censored_effort"] for a in shams)
        de = pf[f]["DERIVED"]["PRIMARY_censored_effort"]
        fam_effect[f] = {"paired_vs_pristine": s,
                         "derived_qualified": pf[f]["DERIVED"]["qualified"],
                         "pristine_qualified": pf[f]["PRISTINE"]["qualified"],
                         "beats_every_sham": de < sham_eff[0],
                         "below_sham_median": de < statistics.median(sham_eff),
                         "effect": s["lower95_one_sided"] > 0
                                   and pf[f]["DERIVED"]["qualified"] >= pf[f]["PRISTINE"]["qualified"]}
    pooled = FR.paired_summary(p_all, d_all)
    c["2_improves_vs_pristine"] = (pooled["lower95_one_sided"] > 0 and all(
        fam_effect[f]["derived_qualified"] >= fam_effect[f]["pristine_qualified"] for f in fams))
    eff = [f for f in fams if fam_effect[f]["effect"]]
    c["3_beats_sham_distribution"] = (
        sum(fam_effect[f]["beats_every_sham"] for f in fams) * 2 >= len(fams)
        and all(fam_effect[f]["below_sham_median"] for f in eff))
    c["4_hostile_evaluation"] = True                 # only tribunal-qualified solutions counted
    hits = sum(pf[f]["DERIVED"]["hits"] for f in fams)
    fps = sum(pf[f]["DERIVED"]["false_positives"] for f in fams)
    c["5_false_positive_limit"] = (fps / hits if hits else 0.0) <= 0.25
    c["6_multiple_families"] = len(eff) >= 2
    # C4 (ADDENDUM 3): a solving class counts as OBSERVED only if a certificate
    # confirms it equals an observed class; a differing B1 bucket is a real witness
    # of difference. A bucket match that the certificate refutes was found AFTER the
    # arms ran: condition 7 is then INCONCLUSIVE and the seat returns.
    anchors = {}
    for cl in art["classes"]:
        anchors.setdefault(cl["behavior_id"], []).append(tuple(cl["observed_programs"][0]))
    c4, inconclusive, novel = [], False, []
    for f in eff:
        progs = {tuple(r["solution_program"]) for r in det[f]["DERIVED"] if r["qualified"]}
        fam_novel = True
        for sp in progs:
            bid = I.behavior_id(sp, True)
            for anc in anchors.get(bid, []):
                rec = CT.certify([sp, anc], anchor=anc)
                c4.append({"family": f, "solution": list(sp), "observed": list(anc),
                           "certified_equal": rec["PASS"]})
                if rec["PASS"]:
                    fam_novel = False
                else:
                    inconclusive = True
        if progs and fam_novel:
            novel.append(f)
    c["7_two_unobserved_mechanisms"] = (len(novel) >= 2) if not inconclusive else False
    c["8_no_donor_state"] = True                     # membrane: artifacts carry module bytes only
    return {"conditions": c, "class_certificates_C4": c4,
            "CONDITION_7_INCONCLUSIVE_RETURN_TO_OPERATOR": inconclusive,
            "pooled_paired_vs_pristine": pooled, "per_family": fam_effect,
            "families_with_effect": eff, "novel_mechanism_families": novel,
            "derived_fp_fraction": round(fps / hits, 4) if hits else 0.0,
            "ABSTRACTION_TRANSPLANT": "YES" if all(c.values()) else "NO",
            "failed": [k for k, v in c.items() if not v]}


def main():
    t0 = time.perf_counter()
    gate = stage_preconditions()
    quals, s6 = stage_qualify()
    _write("T3D_QUALIFICATION_%s.json" % DATE, {"quals": quals, "S6": s6})
    if not s6["PASS"]:
        _log("STOP (S6): %s" % s6)
        return 2
    shams = stage_shams()
    _write("T3D_SHAMS_%s.json" % DATE, shams)
    _log("shams hashed: %s" % [s["sha256"][:10] for s in shams["shams"]])
    art = stage_donor(quals, s6)
    art["conformance_gate"] = gate
    _write("S3_ARTIFACT_%s.json" % DATE, art)
    _log("S3 ENDOGENOUS_ABSTRACTION=%s selected=%s sha=%s"
         % (art["ENDOGENOUS_ABSTRACTION"], art["selection"]["selected"], art["selected_sha256"][:12]))
    if art["ENDOGENOUS_ABSTRACTION"] != "YES":
        return 3
    out = stage_transfer(quals, shams, art)
    out["conformance_gate_before"] = gate
    std = CF.check()                                 # G1 re-run with the results
    out["conformance_gate_after"] = {"part1_GREEN": std["GREEN"], "part1_checked": std["checked"]}
    out["total_seconds"] = round(time.perf_counter() - t0, 1)
    _write("S4_RESULTS_%s.json" % DATE, out)
    if "criterion" in out:
        _log("S4 ABSTRACTION_TRANSPLANT=%s failed=%s" % (out["criterion"]["ABSTRACTION_TRANSPLANT"],
                                                          out["criterion"]["failed"]))
    else:
        _log("S4 %s" % out.get("STOP"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
