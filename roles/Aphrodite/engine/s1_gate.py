"""THE S1 GATE, G-S1.1 .. G-S1.7 (AMENDMENT 12 s6, frozen at 287d208ea). Run 3
under ADDENDUM 2 (18ab82c50): identity over D_TASK_T3_v1 (B1 v3, B2 v3),
conformance over B1 v3 + the boundary battery. Run 2 was
under AMENDMENT 12 ADDENDUM 1 (frozen at d72595bb0): B1 v2, B2 v2 (fresh,
10,000), emitter v2. Run 1's code is at d72595bb0 and its report is
S1_GATE_RUN1_2026-09-23.json.

Identities are computed once per program in a process pool for throughput
only: the evaluator, batteries and decisions are the same as a serial run.
Nothing here grows B1 or edits a fixture in response to a result.
"""
import json
import os
import random
import re
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import basis_v4 as G           # noqa: E402
import conformance as CF       # noqa: E402
import identity as I           # noqa: E402
import s1_fixtures as F        # noqa: E402

SAMPLE_N = 20_000
ARTIFACT_SAMPLE_N = 200
EMITTER = 2
WORKERS = int(os.environ.get("S1_WORKERS", "7"))


def _log(msg):
    print("[s1] " + msg, flush=True)


# ---------------------------------------------------------------- pooled identities
def _ids(item):
    prog, tr = item
    rec = {"b": I.behavior_id(prog, tr), "a": I.audit_id(prog, tr),
           "s": I.structure_id(prog, tr)}
    sp = I.structural_program(prog)
    if tuple(sp) != tuple(prog):
        rec["sp_b"], rec["sp_a"] = I.behavior_id(sp, tr), I.audit_id(sp, tr)
        rec["sp"] = list(sp)
    return item, rec


def _conf(prog):
    """Conformance domain = valid inputs + ceiling/failure edges (ADDENDUM 2)."""
    a = CF.check_whole_program(prog, I.B1, EMITTER)
    b = CF.check_whole_program(prog, I.B1_BOUNDARY, EMITTER)
    return prog, {"checked": a["checked"] + b["checked"],
                  "checked_boundary": b["checked"],
                  "mismatches": a["mismatches"] + b["mismatches"]}


def pooled(fn, items, chunks=16):
    out = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for k, v in ex.map(fn, items, chunksize=chunks):
            out[k] = v
    return out


# ---------------------------------------------------------------- G-S1.1
def gate_collapse(ID):
    rows, fails = [], []
    for fx in F.collapse_pairs():
        tr = fx["trailing"]
        a, b = ID[(tuple(fx["a"]), tr)], ID[(tuple(fx["b"]), tr)]
        neg = I.values(fx["a"], tr, I.b1_neg()) == I.values(fx["b"], tr, I.b1_neg())
        row = {"name": fx["name"], "kind": fx["kind"], "a": list(fx["a"]), "b": list(fx["b"]),
               "same_behavior": a["b"] == b["b"], "same_on_audit": a["a"] == b["a"],
               "same_structure": a["s"] == b["s"], "holds_with_negative_inputs": neg}
        rows.append(row)
        if not row["same_behavior"]:
            fails.append(row)
    dep = sorted({r["name"] for r in rows if r["same_behavior"] and not r["holds_with_negative_inputs"]})
    return {"fixtures": len(rows), "collapsed": sum(r["same_behavior"] for r in rows),
            "general": sum(r["kind"] == "general" for r in rows),
            "historical": sum(r["kind"] == "historical" for r in rows),
            "failures": fails, "PASS": not fails,
            "collapses_that_depend_on_nonnegative_domain": dep,
            "structurally_distinct_but_behaviourally_equal": sum(
                r["same_behavior"] and not r["same_structure"] for r in rows),
            "rows": rows}


# ---------------------------------------------------------------- G-S1.2
def gate_separation(ID):
    hand, fails = [], []
    for nn in F.NEAR_NEIGHBOURS:
        tr = nn["trailing"]
        witness_ok = (G.run_program(nn["a"], list(nn["witness"]), tr)
                      != G.run_program(nn["b"], list(nn["witness"]), tr))
        a, b = ID[(tuple(nn["a"]), tr)], ID[(tuple(nn["b"]), tr)]
        row = {"name": nn["name"], "witness": [str(x) for x in nn["witness"]],
               "witness_really_differs": witness_ok, "separated_by_B1": a["b"] != b["b"],
               "same_structure": a["s"] == b["s"]}
        hand.append(row)
        if not (witness_ok and row["separated_by_B1"]):
            fails.append(row)
    mech = {"mutants": 0, "B2_separates": 0, "B1_separates": 0,
            "B2_separates_but_B1_merges": [], "B1_merges_B2_merges": 0}
    for w in F.catalog_witnesses():
        p, tr = w["program"], w["trailing"]
        wi = ID[(tuple(p), tr)]
        for m in F.mutants(p):
            mi = ID[(tuple(m), tr)]
            mech["mutants"] += 1
            s1, s2 = mi["b"] != wi["b"], (mi["a"] != wi["a"]) or (mi["b"] != wi["b"])
            mech["B1_separates"] += s1
            mech["B2_separates"] += s2
            if s2 and not s1:
                mech["B2_separates_but_B1_merges"].append(
                    {"witness": list(p), "mutant": list(m), "trailing": tr})
            if not s1 and not s2:
                mech["B1_merges_B2_merges"] += 1
    return {"hand_declared": hand, "hand_failures": fails, "mechanical": mech,
            "PASS": not fails and not mech["B2_separates_but_B1_merges"]}


# ---------------------------------------------------------------- G-S1.3 / G-S1.4
def sample_programs():
    rng = random.Random(I._seed("APHRODITE/S1/SAMPLE/v1"))
    return [("fold", rng.choice(G.INIT_SPACE), rng.choice(G.BODY_SPACE),
             rng.choice(G.FINAL_SPACE)) for _ in range(SAMPLE_N)]


def gate_audit_and_refinement(ID):
    by_b, by_s, rewrite_fail, rewritten = {}, {}, [], 0
    for (prog, tr), r in ID.items():
        by_b.setdefault((tr, r["b"]), []).append((prog, r["a"]))
        by_s.setdefault((tr, r["s"]), set()).add(r["b"])
        if "sp" in r:
            rewritten += 1
            if r["sp_b"] != r["b"] or r["sp_a"] != r["a"]:
                rewrite_fail.append({"program": list(prog), "structural": r["sp"]})
    false_merges, merged = [], 0
    for (tr, bid), members in by_b.items():
        if len(members) < 2:
            continue
        merged += len(members)
        auds = {}
        for prog, aid in sorted(members):
            auds.setdefault(aid, []).append(list(prog))
        if len(auds) > 1:
            false_merges.append({"behavior_id": bid, "trailing": tr,
                                 "audit_split": list(auds.values())[:4]})
    refinement_fail = [k for k, v in by_s.items() if len(v) > 1]
    return ({"programs": len(ID), "behavior_classes": len(by_b),
             "members_in_multi_member_classes": merged,
             "false_merges": false_merges[:25], "false_merge_count": len(false_merges),
             "PASS": not false_merges},
            {"structure_classes": len(by_s), "rewritten_programs": rewritten,
             "structure_id_with_two_behaviors": len(refinement_fail),
             "rewrite_changed_behavior": rewrite_fail[:25],
             "PASS": not refinement_fail and not rewrite_fail})


# ---------------------------------------------------------------- G-S1.5
def gate_conformance(programs):
    t0 = time.perf_counter()
    std = CF.check()
    _log("standing conformance part 1 GREEN=%s checked=%d (%.0fs)"
         % (std["GREEN"], std["checked"], time.perf_counter() - t0))
    live = [p for p, tr in programs if p[0] == "fold" and tr]
    excluded = len(programs) - len(live)       # the live emitter is TRAILING-fold only
    res = pooled(_conf, live, chunks=4)
    mism = [m for r in res.values() for m in r["mismatches"]]
    checked = sum(r["checked"] for r in res.values())
    checked_boundary = sum(r["checked_boundary"] for r in res.values())
    return {"standing_gate_part1": {"GREEN": std["GREEN"], "checked": std["checked"],
                                    "mismatches": std["mismatches"][:5]},
            "whole_program_B1_part2": {"emitter": EMITTER, "programs": len(live),
                                       "excluded_non_trailing_or_expr": excluded,
                                       "comparisons": checked, "of_which_boundary_battery": checked_boundary,
                                       "mismatch_count": len(mism),
                                       "mismatches": mism[:25]},
            "PASS": std["GREEN"] and not mism}


# ---------------------------------------------------------------- G-S1.6
FORBIDDEN_IMPORTS = ("tier3b", "tier3c", "meta_tribunal", "improver", "run_", "certify_",
                     "s1_fixtures", "organ_extract")


def gate_no_target():
    src = (HERE / "identity.py").read_text(encoding="utf-8")
    imports = re.findall(r"^\s*(?:import|from)\s+([\w\.]+)", src, re.M)
    bad_imports = [m for m in imports if any(m.startswith(f) for f in FORBIDDEN_IMPORTS)]
    code = re.sub(r'"""[\s\S]*?"""', "", src)          # docstrings are prose, not rules
    literals = {s for w in F.catalog_witnesses() for s in w["program"][1:] if len(s) > 3}
    found = sorted(l for l in literals if l in code)
    fam_found = sorted(w["family"] for w in F.catalog_witnesses() if w["family"] in src)
    schema = "{H}" in src
    return {"imports": imports, "forbidden_imports": bad_imports,
            "catalog_literals_in_code": found, "family_names_in_source": fam_found,
            "schema_hole_in_source": schema,
            "PASS": not bad_imports and not found and not fam_found and not schema}


# ---------------------------------------------------------------- G-S1.7
def gate_old_fixtures():
    py = os.environ.get("S1_PYTEST_PYTHON", sys.executable)
    r = subprocess.run([py, "-m", "pytest", "-q", str(HERE / "tests" / "test_semantics.py")],
                       capture_output=True, text=True, cwd=str(HERE))
    tail = (r.stdout or r.stderr).strip().splitlines()[-1:] or [""]
    return {"returncode": r.returncode, "summary": tail[0], "PASS": r.returncode == 0}


def main(out_name="S1_GATE_RUN3_2026-09-24.json"):
    t0 = time.perf_counter()
    rep = {"amendment": "AMENDMENT_12 @ 287d208ea + ADDENDUM_1 @ d72595bb0 + ADDENDUM_2 @ 18ab82c50",
           "run": 3, "domain": I.DOMAIN, "B1_version": "v3", "B1_boundary_inputs": len(I.B1_BOUNDARY), "B1_inputs": len(I.B1), "B1_sha256": I.B1_SHA,
           "B2_version": "v3", "B2_inputs": len(I.b2()), "emitter": EMITTER, "workers": WORKERS,
           "started_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    rep["G_S1_6_no_target"] = gate_no_target()
    _log("G-S1.6 no target PASS=%s" % rep["G_S1_6_no_target"]["PASS"])

    fixture_programs = []
    for fx in F.collapse_pairs():
        fixture_programs += [(tuple(fx["a"]), fx["trailing"]), (tuple(fx["b"]), fx["trailing"])]
    for nn in F.NEAR_NEIGHBOURS:
        fixture_programs += [(tuple(nn["a"]), nn["trailing"]), (tuple(nn["b"]), nn["trailing"])]
    mutant_programs = [(tuple(m), w["trailing"]) for w in F.catalog_witnesses()
                       for m in F.mutants(w["program"])]
    witnesses = [(tuple(w["program"]), w["trailing"]) for w in F.catalog_witnesses()]
    sample = [(p, True) for p in sample_programs()]
    allp = list(dict.fromkeys(fixture_programs + witnesses + mutant_programs + sample))
    t1 = time.perf_counter()
    ID = pooled(_ids, allp)
    _log("identities for %d programs (%.0fs, %d workers)"
         % (len(ID), time.perf_counter() - t1, WORKERS))

    rep["G_S1_1_collapse"] = gate_collapse(ID)
    _log("G-S1.1 collapse %d/%d PASS=%s" % (rep["G_S1_1_collapse"]["collapsed"],
                                             rep["G_S1_1_collapse"]["fixtures"],
                                             rep["G_S1_1_collapse"]["PASS"]))
    rep["G_S1_2_separation"] = gate_separation(ID)
    _log("G-S1.2 separation PASS=%s mutants=%d B1-merged-but-B2-separated=%d"
         % (rep["G_S1_2_separation"]["PASS"], rep["G_S1_2_separation"]["mechanical"]["mutants"],
            len(rep["G_S1_2_separation"]["mechanical"]["B2_separates_but_B1_merges"])))
    audit, refine = gate_audit_and_refinement(ID)
    rep["G_S1_3_audit"], rep["G_S1_4_refinement"] = audit, refine
    _log("G-S1.3 audit false merges=%d classes=%d PASS=%s"
         % (audit["false_merge_count"], audit["behavior_classes"], audit["PASS"]))
    _log("G-S1.4 refinement PASS=%s" % refine["PASS"])
    rng = random.Random(I._seed("APHRODITE/S1/ARTIFACT-SAMPLE/v1"))
    art_progs = list(dict.fromkeys(fixture_programs)) + rng.sample(sample, ARTIFACT_SAMPLE_N)
    rep["G_S1_5_conformance"] = gate_conformance(art_progs)
    _log("G-S1.5 conformance PASS=%s mismatches=%d"
         % (rep["G_S1_5_conformance"]["PASS"],
            rep["G_S1_5_conformance"]["whole_program_B1_part2"]["mismatch_count"]))
    rep["G_S1_7_old_fixtures"] = gate_old_fixtures()
    _log("G-S1.7 old fixtures PASS=%s %s" % (rep["G_S1_7_old_fixtures"]["PASS"],
                                              rep["G_S1_7_old_fixtures"]["summary"]))
    gates = [k for k in rep if k.startswith("G_S1_")]
    rep["OUTCOME"] = "S1_PASS" if all(rep[k]["PASS"] for k in gates) else "S1_FAIL"
    rep["failed_gates"] = [k for k in gates if not rep[k]["PASS"]]
    rep["seconds"] = round(time.perf_counter() - t0, 1)
    (HERE / out_name).write_text(json.dumps(rep, indent=1, sort_keys=True, default=str) + "\n",
                                 encoding="utf-8")
    _log("OUTCOME %s failed=%s (%.0fs) -> %s" % (rep["OUTCOME"], rep["failed_gates"],
                                                  rep["seconds"], out_name))
    return 0 if rep["OUTCOME"] == "S1_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(*(sys.argv[1:2])))
