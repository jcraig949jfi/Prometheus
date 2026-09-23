"""THE S1 GATE, G-S1.1 .. G-S1.7 (AMENDMENT 12 s6, frozen at 287d208ea).

Writes S1_GATE_<date>.json. Outcome is S1_PASS only if every sub-gate holds.
Nothing here grows B1 or edits a fixture in response to a result.
"""
import json
import random
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import basis_v4 as G           # noqa: E402
import conformance as CF       # noqa: E402
import engine as E             # noqa: E402
import identity as I           # noqa: E402
import meta_tribunal as M      # noqa: E402
import s1_fixtures as F        # noqa: E402

SAMPLE_N = 20_000
ARTIFACT_SAMPLE_N = 200


def _log(msg):
    print("[s1] " + msg, flush=True)


def _differs_at(a, b, inp, trailing):
    return G.run_program(a, list(inp), trailing) != G.run_program(b, list(inp), trailing)


# ---------------------------------------------------------------- G-S1.1
def gate_collapse():
    rows, fails = [], []
    for fx in F.collapse_pairs():
        tr = fx["trailing"]
        same = I.same_behavior(fx["a"], fx["b"], tr)
        audit = I.audit_id(fx["a"], tr) == I.audit_id(fx["b"], tr)
        neg = I.values(fx["a"], tr, I.b1_neg()) == I.values(fx["b"], tr, I.b1_neg())
        row = {"name": fx["name"], "kind": fx["kind"], "a": list(fx["a"]), "b": list(fx["b"]),
               "same_behavior": same, "same_on_audit": audit,
               "same_structure": I.structure_id(fx["a"], tr) == I.structure_id(fx["b"], tr),
               "holds_with_negative_inputs": neg}
        rows.append(row)
        if not same:
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
def gate_separation():
    hand, fails = [], []
    for nn in F.NEAR_NEIGHBOURS:
        tr = nn["trailing"]
        witness_ok = _differs_at(nn["a"], nn["b"], nn["witness"], tr)
        sep = not I.same_behavior(nn["a"], nn["b"], tr)
        row = {"name": nn["name"], "witness": [str(x) for x in nn["witness"]],
               "witness_really_differs": witness_ok, "separated_by_B1": sep,
               "same_structure": I.structure_id(nn["a"], tr) == I.structure_id(nn["b"], tr)}
        hand.append(row)
        if not (witness_ok and sep):
            fails.append(row)
    mech = {"mutants": 0, "B2_separates": 0, "B1_separates": 0,
            "B2_separates_but_B1_merges": [], "B1_merges_B2_merges": 0}
    mutant_programs = []
    for w in F.catalog_witnesses():
        p, tr = w["program"], w["trailing"]
        wb, wa = I.behavior_id(p, tr), I.audit_id(p, tr)
        for m in F.mutants(p):
            mutant_programs.append((m, tr))
            mech["mutants"] += 1
            mb, ma = I.behavior_id(m, tr), I.audit_id(m, tr)
            s1, s2 = mb != wb, (ma != wa) or (mb != wb)
            mech["B1_separates"] += s1
            mech["B2_separates"] += s2
            if s2 and not s1:
                mech["B2_separates_but_B1_merges"].append(
                    {"witness": list(p), "mutant": list(m), "trailing": tr})
            if not s1 and not s2:
                mech["B1_merges_B2_merges"] += 1
    ok = not fails and not mech["B2_separates_but_B1_merges"]
    return {"hand_declared": hand, "hand_failures": fails, "mechanical": mech,
            "PASS": ok}, mutant_programs


# ---------------------------------------------------------------- G-S1.3 / G-S1.4
def sample_programs():
    rng = random.Random(I._seed("APHRODITE/S1/SAMPLE/v1"))
    return [("fold", rng.choice(G.INIT_SPACE), rng.choice(G.BODY_SPACE),
             rng.choice(G.FINAL_SPACE)) for _ in range(SAMPLE_N)]


def gate_audit_and_refinement(programs):
    """programs: list of (prog, trailing). Every B1 merge must agree on B2;
    every structure_id collision must share a behavior_id; every structural
    rewrite must preserve behaviour on B1 and B2."""
    by_b, by_s, rewrite_fail = {}, {}, []
    rewritten = 0
    for prog, tr in programs:
        bid, sid = I.behavior_id(prog, tr), I.structure_id(prog, tr)
        by_b.setdefault((tr, bid), set()).add(tuple(prog))
        by_s.setdefault((tr, sid), set()).add(bid)
        sp = I.structural_program(prog)
        if tuple(sp) != tuple(prog):
            rewritten += 1
            if (I.behavior_id(sp, tr) != bid
                    or I.audit_id(sp, tr) != I.audit_id(prog, tr)):
                rewrite_fail.append({"program": list(prog), "structural": list(sp)})
    false_merges, merged_members = [], 0
    for (tr, bid), members in by_b.items():
        if len(members) < 2:
            continue
        merged_members += len(members)
        auds = {}
        for m in sorted(members):
            auds.setdefault(I.audit_id(m, tr), []).append(list(m))
        if len(auds) > 1:
            false_merges.append({"behavior_id": bid, "trailing": tr,
                                 "audit_split": list(auds.values())[:4]})
    refinement_fail = [k for k, v in by_s.items() if len(v) > 1]
    return ({"programs": len(programs), "behavior_classes": len(by_b),
             "members_in_multi_member_classes": merged_members,
             "false_merges": false_merges[:25], "false_merge_count": len(false_merges),
             "PASS": not false_merges},
            {"structure_classes": len(by_s), "rewritten_programs": rewritten,
             "structure_id_with_two_behaviors": len(refinement_fail),
             "rewrite_changed_behavior": rewrite_fail[:25],
             "PASS": not refinement_fail and not rewrite_fail})


# ---------------------------------------------------------------- G-S1.5
def _artifact_values(prog, battery):
    art = M.artifact_for("gate", prog)
    r = E.Recipient.fresh(seed=1)
    r.load(art)
    out = []
    for inp in battery:
        if len(inp) < 2:
            continue
        prompt = "Family gate over: " + ", ".join(map(str, inp[:-1])) + " with %d." % inp[-1]
        out.append(r.answer(prompt, "gate"))
    return out


def gate_conformance(programs):
    t0 = time.perf_counter()
    std = CF.check()
    _log("standing conformance gate GREEN=%s checked=%d (%.0fs)"
         % (std["GREEN"], std["checked"], time.perf_counter() - t0))
    mism, checked, excluded = [], 0, 0
    for prog, tr in programs:
        if prog[0] != "fold" or not tr:
            excluded += 1          # the live emitter is TRAILING-fold only
            continue
        want = I.values(prog, tr, I.B1)
        got = _artifact_values(prog, I.B1)
        for inp, a, b in zip(I.B1, want, got):
            checked += 1
            if not (a == b or (a == I.FAIL and b in ("overflow", None))):
                mism.append({"program": list(prog), "input_len": len(inp),
                             "input_max_digits": max(len(str(x)) for x in inp),
                             "search": a, "artifact": b})
    return {"standing_gate": {"GREEN": std["GREEN"], "checked": std["checked"],
                              "mismatches": std["mismatches"][:5]},
            "whole_program_B1": {"programs": len(programs) - excluded,
                                 "excluded_non_trailing_or_expr": excluded,
                                 "comparisons": checked, "mismatch_count": len(mism),
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
    literals = set()
    for w in F.catalog_witnesses():
        for s in w["program"][1:]:
            if len(s) > 3:
                literals.add(s)
    found = sorted(l for l in literals if l in code)
    fam_names = [w["family"] for w in F.catalog_witnesses()]
    fam_found = sorted(f for f in fam_names if f in src)
    schema = "{H}" in src or "acc + {H}" in src
    ok = not bad_imports and not found and not fam_found and not schema
    return {"imports": imports, "forbidden_imports": bad_imports,
            "catalog_literals_in_code": found, "family_names_in_source": fam_found,
            "schema_hole_in_source": schema, "PASS": ok}


# ---------------------------------------------------------------- G-S1.7
def gate_old_fixtures():
    py = Path(sys.executable)
    venv = Path(__import__("os").environ.get("S1_PYTEST_PYTHON", str(py)))
    r = subprocess.run([str(venv), "-m", "pytest", "-q", str(HERE / "tests" / "test_semantics.py")],
                       capture_output=True, text=True, cwd=str(HERE))
    tail = (r.stdout or r.stderr).strip().splitlines()[-1:] or [""]
    return {"returncode": r.returncode, "summary": tail[0], "PASS": r.returncode == 0}


def main(out_name=None):
    t0 = time.perf_counter()
    rep = {"amendment": "AMENDMENT_12_2026-09-23.md @ 287d208ea",
           "domain": I.DOMAIN, "B1_inputs": len(I.B1), "B1_sha256": I.B1_SHA,
           "B2_inputs": len(I.b2()), "started_utc": datetime.now(timezone.utc)
           .strftime("%Y-%m-%dT%H:%M:%SZ")}
    rep["G_S1_6_no_target"] = gate_no_target()
    _log("G-S1.6 no target PASS=%s" % rep["G_S1_6_no_target"]["PASS"])
    rep["G_S1_1_collapse"] = gate_collapse()
    _log("G-S1.1 collapse %d/%d PASS=%s" % (rep["G_S1_1_collapse"]["collapsed"],
                                             rep["G_S1_1_collapse"]["fixtures"],
                                             rep["G_S1_1_collapse"]["PASS"]))
    sep, mutant_programs = gate_separation()
    rep["G_S1_2_separation"] = sep
    _log("G-S1.2 separation PASS=%s mutants=%d" % (sep["PASS"], sep["mechanical"]["mutants"]))
    fixture_programs = []
    for fx in F.collapse_pairs():
        fixture_programs += [(tuple(fx["a"]), fx["trailing"]), (tuple(fx["b"]), fx["trailing"])]
    for nn in F.NEAR_NEIGHBOURS:
        fixture_programs += [(tuple(nn["a"]), nn["trailing"]), (tuple(nn["b"]), nn["trailing"])]
    sample = [(p, True) for p in sample_programs()]
    allp = list(dict.fromkeys(fixture_programs + mutant_programs + sample))
    t1 = time.perf_counter()
    audit, refine = gate_audit_and_refinement(allp)
    rep["G_S1_3_audit"], rep["G_S1_4_refinement"] = audit, refine
    _log("G-S1.3 audit false merges=%d classes=%d PASS=%s (%.0fs)"
         % (audit["false_merge_count"], audit["behavior_classes"], audit["PASS"],
            time.perf_counter() - t1))
    _log("G-S1.4 refinement PASS=%s" % refine["PASS"])
    rng = __import__("random").Random(I._seed("APHRODITE/S1/ARTIFACT-SAMPLE/v1"))
    art_progs = list(dict.fromkeys(fixture_programs)) + rng.sample(sample, ARTIFACT_SAMPLE_N)
    rep["G_S1_5_conformance"] = gate_conformance(art_progs)
    _log("G-S1.5 conformance PASS=%s" % rep["G_S1_5_conformance"]["PASS"])
    rep["G_S1_7_old_fixtures"] = gate_old_fixtures()
    _log("G-S1.7 old fixtures PASS=%s %s" % (rep["G_S1_7_old_fixtures"]["PASS"],
                                              rep["G_S1_7_old_fixtures"]["summary"]))
    gates = [k for k in rep if k.startswith("G_S1_")]
    rep["OUTCOME"] = "S1_PASS" if all(rep[k]["PASS"] for k in gates) else "S1_FAIL"
    rep["failed_gates"] = [k for k in gates if not rep[k]["PASS"]]
    rep["seconds"] = round(time.perf_counter() - t0, 1)
    name = out_name or "S1_GATE_%s.json" % datetime.now(timezone.utc).strftime("%Y-%m-%d")
    (HERE / name).write_text(json.dumps(rep, indent=1, sort_keys=True, default=str) + "\n",
                             encoding="utf-8")
    _log("OUTCOME %s failed=%s (%.0fs) -> %s" % (rep["OUTCOME"], rep["failed_gates"],
                                                  rep["seconds"], name))
    return 0 if rep["OUTCOME"] == "S1_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(*(sys.argv[1:2])))
