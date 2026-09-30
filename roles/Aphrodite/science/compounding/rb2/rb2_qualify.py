"""RB-2 stage 2 -- Q2, extensional G1 test, solvability, aggregation
(forensic, not a disposition). Reads RB2_CENSUS_ROWS.json, writes
RB2_AUDIT.json. Checkpoints to RB2_Q2.json / RB2_SOLVE.jsonl (resumable).

Per variant x stratum:
  admissible            the variant's structural preconditions + its non-degeneracy
  non_additive          admissible and body class not ADDITIVE / ACC_FREE
                        (task-grounded: b(acc,v,f,l) - acc depends on acc on a
                        non-negative grid)
  Q2                    exact a17.qualify (cached form, validated here on a sample)
  non_G1_extensional    Q2-passing non-additive survivors NOT extensionally equal
                        to any G1-coverage program (K7 test, widened inits)
  solvability           K2 cells (4 per arm, escrow 250k): dev-consistent hit;
                        for T4-world rows also the T4-qualified solve, for V0 rows
                        also the OLD-tribunal-qualified solve
  window                share of solved-tested survivors with PRISTINE 1..3 of 4
  junk                  T4 profile reasons among the admitted, plus V4 wrap
"""
import json
import random
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rb2_common as C   # noqa: E402

HERE = C.HERE
ALL_V = list(C.VARIANTS) + list(C.T4_VARIANTS)
ADD_SAMPLE = 12        # additive Q2-passing programs per variant x stratum sent to solvability


def init_of(v):
    return C.VARIANTS[v]["inits"] if v in C.VARIANTS else C.T4_VARIANTS[v]


def admitted(r, v):
    if v in C.VARIANTS:
        return r[v]["admissible"]
    return r["profile_" + init_of(v)]["admissible"]


def prog(r, v):
    return (r["init_" + init_of(v)], r["body"], r["final"])


def genuinely_non_additive(r):
    return r["body_class"] not in ("ADDITIVE", "ACC_FREE")


def _q2(p):
    return list(p), C.qualify_cached(*p)


def _q2ref(p):
    return list(p), C.qualify_reference(*p)


def _g1(p):
    return list(p), C.g1_equivalent(*p)


def _solve(args):
    p, size, tribs = args
    name = C.letter_name("rbs", list(p))
    out = {"prog": list(p), "size": size}
    res = C.solve_cells(p[0], p[1], p[2], size, name, tribunal="T4" if "T4" in tribs else None)
    out.update(res)
    if "OLD" in tribs:
        o = C.solve_cells(p[0], p[1], p[2], size, name, tribunal="OLD")
        for arm in ("PRISTINE", "L1"):
            out[arm]["qualified_OLD"] = o[arm]["qualified"]
    if "T4" in tribs:
        for arm in ("PRISTINE", "L1"):
            out[arm]["qualified_T4"] = out[arm].pop("qualified")
    return out


def pmap(fn, items, chunks=4):
    with ProcessPoolExecutor(C.WORKERS, initializer=C.worker_init) as ex:
        return list(ex.map(fn, items, chunksize=chunks))


if __name__ == "__main__":
    t0 = time.time()
    cen = json.loads((HERE / "RB2_CENSUS_ROWS.json").read_text())
    rows = cen["rows"]
    adm_progs = {}
    for r in rows:
        for v in ALL_V:
            if admitted(r, v):
                adm_progs[prog(r, v)] = 1
    print("admissible programs (union):", len(adm_progs), flush=True)
    # ---- Q2 (cached exact) + validation against a17.qualify on a sample
    qf = HERE / "RB2_Q2.json"
    q2 = {}
    if qf.exists():
        q2 = {tuple(json.loads(k)): v for k, v in json.loads(qf.read_text())["q2"].items()}
    todo = [p for p in adm_progs if p not in q2]
    for p, s in pmap(_q2, todo, 20):
        q2[tuple(p)] = s
    val = json.loads(qf.read_text()).get("validation") if qf.exists() else None
    if val is None:
        rs = sorted(adm_progs)
        random.Random(C.SEED_LABEL + "/q2val").shuffle(rs)
        vs = rs[:40]
        ref = dict((tuple(p), s) for p, s in pmap(_q2ref, vs, 1))
        val = {"n": len(vs), "agree": sum(ref[p] == q2[p] for p in vs),
               "disagreements": [[list(p), q2[p], ref[p]] for p in vs if ref[p] != q2[p]]}
    qf.write_text(json.dumps({"validation": val, "q2": {json.dumps(list(k)): v for k, v in q2.items()}}))
    print("Q2 done; validation", val["agree"], "/", val["n"], "(%.0fs)" % (time.time() - t0), flush=True)
    # ---- extensional G1 test on Q2-passing, genuinely non-additive admissible programs
    bodycls = {r["body"]: r["body_class"] for r in rows}
    surv = [p for p in adm_progs if q2[p] is not None and bodycls[p[1]] not in ("ADDITIVE", "ACC_FREE")]
    gf = HERE / "RB2_G1EXT.json"
    g1 = {}
    if gf.exists():
        g1 = {tuple(json.loads(k)): v for k, v in json.loads(gf.read_text()).items()}
    for p, eq in pmap(_g1, [p for p in surv if p not in g1], 4):
        g1[tuple(p)] = eq
    gf.write_text(json.dumps({json.dumps(list(k)): v for k, v in g1.items()}))
    print("G1-extensional tests:", len(surv), "(%.0fs)" % (time.time() - t0), flush=True)
    # ---- solvability set: all non-additive survivors + a sample of additive ones
    tribs = defaultdict(set)
    for r in rows:
        for v in ALL_V:
            if admitted(r, v):
                p = prog(r, v)
                if v.startswith("V7") or v.startswith("V8"):
                    tribs[p].add("T4")
                if v == "V0":
                    tribs[p].add("OLD")
    solve_set = {p: 1 for p in surv}
    for v in ALL_V:
        for op in C.STRATA:
            adds = sorted({prog(r, v) for r in rows if r["op"] == op and admitted(r, v)
                           and q2[prog(r, v)] is not None and not genuinely_non_additive(r)})
            random.Random("%s/add/%s/%s" % (C.SEED_LABEL, v, op)).shuffle(adds)
            for p in adds[:ADD_SAMPLE]:
                solve_set[p] = 1
    sf = HERE / "RB2_SOLVE.jsonl"
    solved = {}
    if sf.exists():
        for line in sf.read_text().splitlines():
            o = json.loads(line)
            solved[tuple(o["prog"])] = o
    todo = [(p, q2[p], sorted(tribs[p])) for p in solve_set if p not in solved]
    print("solvability programs:", len(solve_set), "todo", len(todo), flush=True)
    with ProcessPoolExecutor(C.WORKERS, initializer=C.worker_init) as ex, open(sf, "a") as fh:
        for i, o in enumerate(ex.map(_solve, todo, chunksize=1)):
            solved[tuple(o["prog"])] = o
            fh.write(json.dumps(o) + "\n")
            fh.flush()
            if i % 100 == 0:
                print("  solved %d/%d (%.0fs)" % (i, len(todo), time.time() - t0), flush=True)
    print("solvability done (%.0fs)" % (time.time() - t0), flush=True)
    # ---- behavior ids for family counting (successor world survivors)
    beh = {}
    for p in solve_set:
        beh[p] = C.I.behavior_id(("fold",) + tuple(p), True)
    # ---- aggregate
    table = {}
    fam_members = {}
    for v in ALL_V:
        table[v] = {}
        for op in C.STRATA + ["ALL"]:
            rs = [r for r in rows if (op == "ALL" or r["op"] == op)]
            A = [r for r in rs if admitted(r, v)]
            NA = [r for r in A if genuinely_non_additive(r)]
            Aq = [r for r in A if q2[prog(r, v)] is not None]
            NAq = [r for r in NA if q2[prog(r, v)] is not None]
            NAq_ng = [r for r in NAq if g1.get(prog(r, v)) is None]
            tested = [r for r in Aq if prog(r, v) in solved]
            tested_na = [r for r in NAq if prog(r, v) in solved]

            def solv(lst, arm, key="solved"):
                return sum(solved[prog(r, v)][arm].get(key, 0) > 0 for r in lst)

            def window(lst, key="solved"):
                return sum(0 < solved[prog(r, v)]["PRISTINE"].get(key, 0) < 4 for r in lst)
            junk = Counter()
            for r in A:
                for rs_ in r["profile_" + init_of(v)]["reasons"]:
                    junk[rs_] += 1
                if v in C.VARIANTS and r[v]["wrap_probes"] > 0:
                    junk["WRAP_DEPENDENT(overflow artifact)"] += 1
                if r["body_class"] == "ACC_FREE":
                    junk["BODY_IGNORES_ACC"] += 1
            junk["ANY_T4_REASON"] = sum(bool(r["profile_" + init_of(v)]["reasons"]) for r in A)
            cell = {
                "draws": len(rs), "admissible": len(A), "genuinely_non_additive": len(NA),
                "Q2_pass_admissible": len(Aq),
                "Q2_pass_rate": round(len(Aq) / len(A), 3) if A else None,
                "non_additive_Q2_pass": len(NAq),
                "non_additive_Q2_pass_non_G1_extensional": len(NAq_ng),
                "distinct_non_additive_Q2_bodies": len({r["body"] for r in NAq}),
                "solvability_tested": len(tested),
                "solvability_tested_non_additive": len(tested_na),
                "non_additive_PRISTINE_any": solv(tested_na, "PRISTINE"),
                "non_additive_L1_any": solv(tested_na, "L1"),
                "non_additive_either": sum(solved[prog(r, v)]["PRISTINE"]["solved"] + solved[prog(r, v)]["L1"]["solved"] > 0
                                           for r in tested_na),
                "non_additive_L1_only": sum(solved[prog(r, v)]["L1"]["solved"] > 0 and solved[prog(r, v)]["PRISTINE"]["solved"] == 0
                                            for r in tested_na),
                "window_PRISTINE_1to3_of_4": window(tested),
                "window_fraction": round(window(tested) / len(tested), 3) if tested else None,
                "window_fraction_non_additive": round(window(tested_na) / len(tested_na), 3) if tested_na else None,
                "junk_among_admissible": dict(junk),
            }
            if v.startswith("V7") or v.startswith("V8"):
                cell["non_additive_T4_qualified_PRISTINE_any"] = solv(tested_na, "PRISTINE", "qualified_T4")
                cell["non_additive_T4_qualified_L1_any"] = solv(tested_na, "L1", "qualified_T4")
                cell["non_additive_T4_qualified_either"] = sum(
                    solved[prog(r, v)]["PRISTINE"].get("qualified_T4", 0) + solved[prog(r, v)]["L1"].get("qualified_T4", 0) > 0
                    for r in tested_na)
                cell["window_T4_qualified_non_additive"] = window(tested_na, "qualified_T4")
            if v == "V0":
                cell["non_additive_OLD_qualified_either"] = sum(
                    solved[prog(r, v)]["PRISTINE"].get("qualified_OLD", 0) + solved[prog(r, v)]["L1"].get("qualified_OLD", 0) > 0
                    for r in tested_na)
            # per 1000 draws yield of genuinely non-additive, Q2-qualified, solvable
            ys = sum(solved[prog(r, v)]["PRISTINE"]["solved"] + solved[prog(r, v)]["L1"]["solved"] > 0 for r in tested_na)
            cell["yield_per_1000_nonadd_Q2_solvable"] = round(1000 * ys / len(rs), 2)
            cell["yield_per_1000_nonadd_Q2_solvable_nonG1ext"] = round(1000 * sum(
                solved[prog(r, v)]["PRISTINE"]["solved"] + solved[prog(r, v)]["L1"]["solved"] > 0
                and g1.get(prog(r, v)) is None for r in tested_na) / len(rs), 2)
            table[v][op] = cell
        # schema families among non-additive, Q2-pass, solvable survivors
        fams = defaultdict(set)
        fams_ng = defaultdict(set)
        fams_t4 = defaultdict(set)
        for r in rows:
            if not admitted(r, v) or not genuinely_non_additive(r):
                continue
            p = prog(r, v)
            if q2[p] is None or p not in solved:
                continue
            s = solved[p]
            if s["PRISTINE"]["solved"] + s["L1"]["solved"] > 0:
                fams[r["body_class"]].add(beh[p])
                if g1.get(p) is None:
                    fams_ng[r["body_class"]].add(beh[p])
            if s["PRISTINE"].get("qualified_T4", 0) + s["L1"].get("qualified_T4", 0) > 0:
                fams_t4[r["body_class"]].add(beh[p])
        fam_members[v] = {
            "solvable_by_family_distinct_behaviors": {k: len(x) for k, x in sorted(fams.items())},
            "families_with_ge2": sorted(k for k, x in fams.items() if len(x) >= 2),
            "nonG1ext_solvable_by_family": {k: len(x) for k, x in sorted(fams_ng.items())},
            "nonG1ext_families_with_ge2": sorted(k for k, x in fams_ng.items() if len(x) >= 2),
            "T4_qualified_solvable_by_family": {k: len(x) for k, x in sorted(fams_t4.items())},
            "T4_qualified_families_with_ge2": sorted(k for k, x in fams_t4.items() if len(x) >= 2),
        }
    # examples of non-G1 survivors in the successor world
    ex = defaultdict(list)
    for r in rows:
        v = "V7_T4_WIDE"
        p = prog(r, v)
        if admitted(r, v) and genuinely_non_additive(r) and q2[p] is not None and g1.get(p) is None \
                and p in solved and len(ex[r["body_class"]]) < 6:
            s = solved[p]
            ex[r["body_class"]].append({"prog": list(p), "Q2": q2[p], "L_max": r["profile_WIDE"]["L_max"],
                                        "PRISTINE": s["PRISTINE"]["solved"], "L1": s["L1"]["solved"],
                                        "T4q_P": s["PRISTINE"].get("qualified_T4"), "T4q_L1": s["L1"].get("qualified_T4")})
    body_classes = {v: dict(Counter(r["body_class"] for r in rows if admitted(r, v))) for v in ALL_V}
    out = {"forensic": "not a disposition; nothing here is Campaign 1 evidence",
           "seed_label": C.SEED_LABEL, "N_per_stratum": cen["N_per_stratum"],
           "k1_reproduction": cen["k1_reproduction"],
           "variants": {v: (C.VARIANTS.get(v) or {"tribunal": "T4 family_profile", "inits": C.T4_VARIANTS[v]})
                        for v in ALL_V},
           "q2_cached_validation": val,
           "table": table, "schema_families": fam_members, "body_classes_admitted": body_classes,
           "successor_nonG1_examples": ex,
           "seconds": round(time.time() - t0)}
    (HERE / "RB2_AUDIT.json").write_text(json.dumps(out, indent=1, default=list))
    for v in ALL_V:
        c = table[v]["ALL"]
        print(v, {k: c[k] for k in ("admissible", "genuinely_non_additive", "Q2_pass_rate", "non_additive_Q2_pass",
                                    "non_additive_Q2_pass_non_G1_extensional", "non_additive_either",
                                    "window_fraction", "yield_per_1000_nonadd_Q2_solvable")})
        print("   families>=2:", fam_members[v]["families_with_ge2"], "nonG1:", fam_members[v]["nonG1ext_families_with_ge2"])
