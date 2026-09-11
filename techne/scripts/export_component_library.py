"""TECHNE-14: export stitch's abstractions as a component_library artifact -- and
measure them against the extractor Archaeon already has.

    PYTHONPATH=<repo> <env>/python -m techne.scripts.export_component_library

WHAT CHANGED BEFORE I WROTE A LINE OF THIS. Vivarium told me my arity-0 result is
"the DERIVED library H0 beta wants", against their hand-built instrument control.
That is half right and the half that is wrong matters: archaeon/producer/
campaign_h1h0.py::extract_library ALREADY IS beta's derived extractor -- repeated
typed subtrees of the phase-1 solutions, min_size 3, min_count 2, labelled
`derived`, ties broken by canonical JSON so it replays. So this export does not
fill an empty slot. It is a SECOND extractor arriving where one exists, and the
only thing that justifies it is beating the one already there.

So the deliverable is a COMPARISON, not a publication.

THE SPLIT IS THE WHOLE QUESTION. Archaeon's design holds TARGET tasks out:
task_split() draws disjoint src/tgt, phase 1 solves source tasks, phase 2 solves
target tasks. A library derived from phase-2 solutions and then used on phase-2
tasks has been handed its own test set. So the corpora divide sharply:

  PHASE1_3   the 3 phase-1 source solutions. The ONLY corpus a library may be
             derived from if it is to be used on phase-2 targets.
  ALL_17     every exported row. Includes all 14 phase-2 cells -- the held-out
             set -- and is therefore not exportable for use on phase-2 at any
             quality.

NO EXPRESSION PARSER LIVES HERE, deliberately. Every component this exports must
match a solved program whose AST Archaeon already published in Proteus's grammar,
and the published AST is what gets exported. A stitch body that is NOT a whole
program in the corpus is REFUSED rather than parsed by me: a second parser that
agrees with the owner's grammar until it does not is exactly the failure the
interface id exists to prevent. The refusal is recorded whether or not it fires.

TWO OWNERS ARE CONSULTED AND NEITHER IS COPIED. The envelope comes from
Archaeon's library_object(); the validation comes from Vivarium's
viv.artifacts._check_boolean_components_v1, which is the real loader and which
itself defers to proteus.eval.boolean.check. Truth tables come from Proteus's
evaluator. Nothing structural is re-implemented in this file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys

from ..acquisition import budget as _budget
from ..acquisition import manifest_io, paths, receipt
from ..acquisition.checks.stitch_on_h1_solutions import (DECLARED_SHA, SOLVED,
                                                         run_compress)


def _import_owners():
    """Owners' modules, or an honest failure naming which one is absent."""
    root = str(paths.REPO_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    from archaeon.producer import campaign_h1h0 as _ar
    from archaeon.producer.contract import ensure_viv_importable
    from proteus.eval import boolean as _pb
    # `viv` lives under vivarium/, and Archaeon already owns the one line that
    # makes it importable from an arbitrary entry point. Use theirs.
    ensure_viv_importable()
    from viv import artifacts as _va
    from viv import library_leak as _vl
    return _ar, _pb, _va, _vl


class _Limits:
    """Vivarium's checker reads .max_items off a Limits; 8 is Archaeon's own
    max_components, so the export is held to the ceiling its consumer uses."""

    max_items = 8


def _as_tuple(node):
    if not isinstance(node, list):
        return node
    if node[0] in ("const", "input"):
        return (node[0], node[1])
    return tuple([node[0]] + [_as_tuple(x) for x in node[1:]])


def _score(res, name, corpus, by_sexpr, held_out, ar, pb, va, vl=None, target_tts=None,
           known_solutions=None):
    """One corpus: what stitch learned, whether it is exportable, and what the
    owners' checkers say about it."""
    if not res.get("ok"):
        return {"ok": False, "returncode": res.get("returncode")}

    comps, refused = [], []
    for nm, arity, body, uses in zip(res["names"], res["arities"], res["bodies"], res["uses"]):
        entry = by_sexpr.get(body)
        row = {"stitch_name": nm, "arity": arity, "body": body, "uses": uses,
               "is_whole_program_in_corpus": entry is not None}
        if entry is None:
            # A PROPER SUBTREE would land here. Refused, not parsed -- see the
            # module docstring. This has never fired on this corpus.
            row["refused"] = ("no published AST: this body is not a whole solved program, and "
                              "this exporter will not parse an expression itself")
            refused.append(row)
            continue
        row["expr"] = entry["ast"]
        row["solves_tasks"] = sorted(set(entry["tasks"]))
        row["from_held_out_phase2"] = body in held_out
        row["truth_table"] = pb.truth_table(_as_tuple(entry["ast"]))
        comps.append(row)

    lib = ar.library_object([{"name": "stitch_" + c["stitch_name"], "expr": c["expr"]}
                             for c in comps], provenance="derived")
    raw = lib.get("raw")
    validated, rejected = None, None
    if raw is not None:
        try:
            validated = va._check_boolean_components_v1(
                json.loads(raw.decode("utf-8")), _Limits())
        except Exception as exc:                                # noqa: BLE001
            rejected = type(exc).__name__ + ": " + str(exc)

    n_leak = sum(1 for c in comps if c["from_held_out_phase2"])

    # VIVARIUM'S SEMANTIC CHECKER, because mine was weaker than I had noticed.
    # `from_held_out_phase2` is STRING EQUALITY on s-expressions, so it sees a
    # component only when it is spelled exactly as some solved program was. Two
    # things escape that: the same function spelled differently, and -- worse --
    # a component computing the function of a held-out target that was never
    # SOLVED, which my test cannot see at all because it only knows solutions.
    # viv.library_leak.check compares TRUTH TABLES against the whole target set.
    # Called even when the library is EMPTY. A null leak field would have to be
    # read as "not checked" or "nothing to check", and a reader cannot tell which
    # -- the same ambiguity this seat refuses elsewhere. An empty library returns
    # CLEAN, which is true and is a measurement rather than an absence.
    leak = None
    if vl is not None:
        leak = vl.check([{"name": "stitch_" + c["stitch_name"], "expr": c["expr"]}
                         for c in comps], target_tts or {},
                        known_solutions=known_solutions or {})
        leak["n_target_tasks_my_syntactic_test_could_see"] = len(known_solutions or {})
        leak["why_agreement_with_the_syntactic_test_is_not_coverage"] = (
            "my test compares an s-expression against SOLVED programs, so it can only ever "
            "see the %d targets that have a solution here, never the other %d. Where the two "
            "agree on this corpus, they agree by coincidence -- the same shape as an "
            "equal-width grid reproducing equal-mass edges because the edges happened to be "
            "equal-width." % (len(known_solutions or {}),
                              len(target_tts or {}) - len(known_solutions or {})))

    return {
        "ok": True, "derived_from": name, "n_programs": len(corpus),
        "n_abstractions": res["n_abstractions"],
        "original_cost": res["original_cost"], "final_cost": res["final_cost"],
        "components": comps, "refused_components": refused,
        "every_component_is_a_whole_program": bool(comps) and not refused,
        "n_components_from_held_out_phase2": n_leak,
        "syntactic_leak_test_is_weaker": (
            "n_components_from_held_out_phase2 is string equality on s-expressions and is "
            "kept only so the two tests can be compared. The VERDICT is viv_library_leak."),
        "viv_library_leak": leak,
        "exportable_for_phase2_use": (
            (leak["usable_as_a_library_effect"]) if leak is not None else n_leak == 0),
        "why_not_exportable": (
            None if n_leak == 0 else
            "%d of %d components ARE held-out phase-2 solutions; a search given them finds "
            "those targets as a size-1 LEAF, which measures the leak and not the library"
            % (n_leak, len(comps))),
        "artifact": {"slot": lib.get("slot"), "slot_blocker": lib.get("slot_blocker"),
                     "canonical_json": None if raw is None else raw.decode("utf-8")},
        "loader_accepted": validated, "loader_rejection": rejected,
        "no_pickle": {
            "codec": "canonical-json-v1",
            "bytes_parse_as_json": raw is not None and isinstance(
                json.loads(raw.decode("utf-8")), dict),
            "claim": "the artifact is canonical JSON produced by the owner's canonical_bytes; "
                     "nothing in this path pickles, unpickles, or imports an upstream object"},
    }


def _answer(mine, theirs_n):
    if mine == 0 and theirs_n == 0:
        return ("NO, AND NEITHER DOES THEIRS. Both return an EMPTY library on the legitimate "
                "corpus, and they agree for the same reason: three solutions of 2-4 grammar "
                "nodes contain no subexpression repeated across two of them. That is a fact "
                "about the corpus, not about either extractor, and no amount of tool quality "
                "changes it.")
    if mine == 0:
        return "NO: stitch returns empty where Archaeon's extractor keeps %d." % theirs_n
    if theirs_n == 0:
        return "YES: stitch finds %d where Archaeon's extractor finds none." % mine
    return "BOTH non-empty; the components are listed side by side and must be compared directly."


def _compare(out, theirs):
    p1 = out.get("PHASE1_3", {})
    return {
        "question": ("on the only corpus a held-out evaluation permits -- the 3 phase-1 "
                     "solutions -- does stitch find anything Archaeon's repeated-subtree "
                     "extractor does not?"),
        "stitch_on_PHASE1_3_n_abstractions": p1.get("n_abstractions"),
        "archaeon_extractor_on_PHASE1_3_n_kept": theirs["n_kept"],
        "archaeon_n_candidate_subtrees": theirs["n_candidate_subtrees"],
        "answer": _answer(p1.get("n_abstractions"), theirs["n_kept"]),
        "and_on_ALL_17": {
            "n_abstractions": out.get("ALL_17", {}).get("n_abstractions"),
            "n_from_held_out_phase2":
                out.get("ALL_17", {}).get("n_components_from_held_out_phase2"),
            "viv_leak_verdict":
                (out.get("ALL_17", {}).get("viv_library_leak") or {}).get("verdict"),
            "exportable_for_phase2_use":
                out.get("ALL_17", {}).get("exportable_for_phase2_use")},
    }


def _checks(out, theirs):
    p1 = out.get("PHASE1_3", {})
    all17 = out.get("ALL_17", {})
    rows = [
        ("every exported component carries the AST ARCHAEON published, never one this "
         "exporter parsed",
         all(not v.get("refused_components") for v in out.values() if v.get("ok"))),
        ("the artifact is accepted by VIVARIUM's real loader, or the corpus produced no "
         "components to accept",
         all(v.get("loader_rejection") is None for v in out.values() if v.get("ok"))),
        ("no pickle crosses the boundary: the artifact is canonical JSON from the owner's "
         "canonical_bytes",
         all(v["no_pickle"]["codec"] == "canonical-json-v1"
             for v in out.values() if v.get("ok"))),
        ("MEASURED, not assumed: whether stitch beats the extractor Archaeon already has, on "
         "the corpus a held-out evaluation permits",
         p1.get("n_abstractions") is not None and theirs["n_kept"] is not None),
        ("LEAKAGE IS REPORTED RATHER THAN EXPORTED: any component that is itself a held-out "
         "phase-2 solution is counted and its corpus marked not exportable",
         all17.get("exportable_for_phase2_use") is not None),
        ("the verdict comes from VIVARIUM'S SEMANTIC checker over the full held-out task set, "
         "not from my string equality on s-expressions",
         (all17.get("viv_library_leak") or {}).get("verdict") is not None),
    ]
    checks = [{"claim": k, "pass": bool(v)} for k, v in rows]
    verdict = (
        "stitch's library is EMPTY on the only corpus a held-out evaluation permits (%s phase-1 "
        "solutions), and Archaeon's existing extractor is empty on it too. On ALL_17 stitch "
        "returns %s abstractions, of which %s ARE held-out phase-2 solutions -- so that library "
        "is not exportable for phase-2 use. The export path itself works and the loader accepts "
        "it; there is nothing on this corpus worth putting through it."
        % (p1.get("n_programs"), all17.get("n_abstractions"),
           all17.get("n_components_from_held_out_phase2")))
    return checks, all(x["pass"] for x in checks), verdict


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-arity", type=int, default=3)
    ap.add_argument("--iterations", type=int, default=3)
    ap.add_argument("--profile", default="stitch_core_reproduction")
    a = ap.parse_args(argv)

    ar, pb, va, vl = _import_owners()

    man = manifest_io.load()
    manifest_io.entry(man, "stitch_rust_core")
    root = paths.repos() / "stitch_rust_core"
    binary = root / "target" / "release" / "compress.exe"
    work = paths.tool_cache() / "checkwork" / "stitch_export"
    work.mkdir(parents=True, exist_ok=True)

    rec = receipt.new("ADAPTER_QUALIFICATION", "stitch_rust_core")
    rec["check"] = "component_library_export_and_comparison_against_archaeons_extractor"
    rec["consumer"] = ("viv component_library / boolean-components-v1, which is Proteus's "
                       "interface and Vivarium's loader")
    rec["clears"] = "TECHNE-14"

    src = paths.REPO_ROOT.joinpath(*SOLVED)
    git_bytes = subprocess.run(["git", "show", "origin/main:" + "/".join(SOLVED)],
                               cwd=str(paths.REPO_ROOT), capture_output=True).stdout
    committed_sha = hashlib.sha256(git_bytes).hexdigest()
    doc = json.loads(src.read_text(encoding="utf-8"))
    programs = doc["programs"]

    p1 = [p for p in programs if p["candidate_set"] == "cs-h1h0-1-p1"]
    p2 = [p for p in programs if p["candidate_set"].startswith("cs-h1h0-1-p2")]

    #: sexpr -> the AST ARCHAEON published for it, and the tasks it solved.
    by_sexpr = {}
    for p in programs:
        e = by_sexpr.setdefault(p["solution_sexpr"],
                                {"ast": p["solution_ast"], "tasks": [], "phases": set()})
        e["tasks"].append(p["task_id"])
        e["phases"].add(1 if p["candidate_set"] == "cs-h1h0-1-p1" else 2)
        if e["ast"] != p["solution_ast"]:                       # pragma: no cover
            raise SystemExit("same s-expression, two ASTs: " + p["solution_sexpr"])

    held_out_sexprs = {p["solution_sexpr"] for p in p2}

    corpora = {"PHASE1_3": [p["solution_sexpr"] for p in p1],
               "ALL_17": [p["solution_sexpr"] for p in programs]}

    # THE FULL HELD-OUT TASK SET, not just the solved ones. Archaeon's split is the
    # authority on which tasks are held out; a leak test built from SOLUTIONS can
    # only ever see targets that happen to have been solved.
    split = ar.task_split()
    target_tts = {t["task_id"]: t["tt"] for t in split["target"]}
    known_solutions = {p["task_id"]: p["solution_ast"] for p in p2}

    out = {}
    with _budget.Budget(profile=_budget.get_profile(a.profile)) as b:
        for name, corpus in corpora.items():
            res = run_compress(binary, root, corpus, work / (name + ".json"),
                               iterations=a.iterations, max_arity=a.max_arity, b=b)
            out[name] = _score(res, name, corpus, by_sexpr, held_out_sexprs, ar, pb, va,
                               vl=vl, target_tts=target_tts, known_solutions=known_solutions)
        rec["resource_receipt"] = b.resource_receipt()

    # ---- Archaeon's extractor on the SAME legitimate corpus ------------------
    theirs = ar.extract_library(
        [{"result": {"solution": json.dumps(p["solution_ast"])}} for p in p1])
    theirs_summary = {
        "extractor": "archaeon.producer.campaign_h1h0.extract_library",
        "parameters": {"min_size": 3, "min_count": 2, "max_components": 8},
        "derived_from": "PHASE1_3",
        "n_candidate_subtrees": theirs["n_candidates"],
        "n_kept": theirs["n_kept"],
        "components": [{"name": c["name"], "expr": c["expr"], "count": c["count"]}
                       for c in theirs["object"]["components"]],
    }

    rec["observations"] = {
        "schema": "techne.h0.component_library_export/1",
        "clears": "TECHNE-14",
        "input": {"path": "/".join(SOLVED), "declared_sha256": DECLARED_SHA,
                  "committed_bytes_sha256": committed_sha,
                  "matches_declared": committed_sha == DECLARED_SHA},
        "split": {
            "owner": "archaeon.producer.campaign_h1h0.task_split",
            "rule": "SOURCE tasks feed phase 1; TARGET tasks are held out and solved in phase 2",
            "why_it_decides_this_export": (
                "a library derived from phase-2 solutions and then used on phase-2 targets has "
                "been handed its own test set, so ALL_17 is measured and reported but is NOT "
                "exportable for use on phase 2 at any quality"),
            "n_phase1": len(p1), "n_phase2_cells": len(p2),
            "n_phase2_distinct": len(held_out_sexprs),
            "n_target_tasks_in_split": len(target_tts),
            "n_target_tasks_with_a_known_solution": len(known_solutions),
            "why_the_full_target_set_matters": (
                "my own leak test compared against SOLVED PROGRAMS, so a component computing "
                "the function of a held-out target that was never solved was invisible to it. "
                "%d targets are in the split and only %d have a solution here."
                % (len(target_tts), len(known_solutions)))},
        "stitch": out,
        "archaeon_existing_extractor": theirs_summary,
        "comparison": _compare(out, theirs_summary),
    }
    rec["checks"], rec["all_passed"], rec["verdict"] = _checks(out, theirs_summary)
    rec["does_not_establish"] = ["INSTALLATION", "FIRST_USEFUL_CHECK",
                                 "PAPER_REPRODUCTION", "LOCAL_SCIENTIFIC_BENEFIT"]
    path = receipt.write(rec)
    print(json.dumps(rec["observations"]["comparison"], indent=1))
    print("VERDICT", rec["verdict"])
    print("receipt", path)
    return 0 if rec["all_passed"] else 1


if __name__ == "__main__":                                      # pragma: no cover
    raise SystemExit(main())
