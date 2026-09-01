"""Build the Lexis handoff artifacts, deterministically, from the committed G7 rows.

Writes (into --out-dir, default this directory):
    interface_pair_manifest.json     the frozen pair: provenance, contract, evidence
    state_injection_fixture.json     42 Charon tasks with recognition, outcomes, dE/dS,
                                     robustness columns, and the ORACLE semantic states a
                                     state-injection experiment needs, per injection level
    consumer_utility_result.json     CORRECT/ABSTAIN/WRONG accounting of the bundle under
                                     several loss functions, both batteries, both placements

Evidence sources (all committed, none recomputed here except what is cheap and local):
    roles/Lexis/notes/g7_charon_result.json          the G7 arms, robust sets, dE/dS
    roles/Charon/apollo_e9/charon_battery_E9*.json   the battery and its sidecar
    roles/Lexis/instruments/candidate_primitives.py  the frozen pair (hash-pinned)

ORACLE STATES. For each task the fixture gives up to two injection levels:
    inject_parsed   the slots Apollo's PARSER layer is responsible for (numbers, names,
                    relations, quantities, question_target). If a task solves from here,
                    the failure was SURFACE (A).
    inject_derived  the slots the COMPUTE layer is responsible for (counts, ordered,
                    max_value, comparison, extreme_number). If a task fails at parsed level
                    but solves from here, the failure was CAPABILITY (B). If it fails even
                    here, the failure is READOUT (C).
Each level names `then_run` -- the EXISTING clean-pool operators that must run after the
injection. `then_run == []` means no existing operator consumes the injected slots: that
level is a B-gap by construction and is not run. NO_SLOT means the substrate has no slot
that can carry the needed state at that level. `readout_only` marks derived-level
injections that are one string match away from the answer (comparison=True/False for
yes/no candidates): they measure the readout and nothing else.

The oracle states are authored from Charon's GOLD and from the candidate strings. They
are the INPUT to Apollo's preregistered oracle arm, not a parser and not a solver. The
injected relation direction and the question_target word encode the question's polarity
in the substrate's own index vocabulary (select_nth understands first/second/third/
smallest but NOT 'last'); the arm therefore tests op_build_ordering + select_nth, not
polarity resolution. That is stated per task in `oracle_encodes`.

FIXTURE SELF-CHECK. For every level with a non-empty `then_run`, the injected state is
built, the named operators are run, and `verified` records whether the gold came out.
This is a mechanics check that the fixture is consumable -- it is NOT the experiment. The
experiment is the preregistered comparison of arms (raw / oracle / corrupted) and belongs
to the consumer.

Read-only on apollo/. Deterministic: no timestamps, no randomness.
"""
from __future__ import annotations

import argparse
import collections
import copy
import json
import os
import subprocess
import sys
from pathlib import Path

# HIDDEN DEPENDENCY (found 2026-09-01 while verifying byte-identity): the home battery's
# `synth` subset (30 of 120 tasks) is generated through a set and therefore changes with
# PYTHONHASHSEED. Every per-task home number depends on the draw. Pin it here so the
# artifacts are byte-reproducible; report the spread over other seeds below.
HASHSEED = "0"
if os.environ.get("PYTHONHASHSEED") != HASHSEED:
    os.environ["PYTHONHASHSEED"] = HASHSEED
    os.execv(sys.executable, [sys.executable] + sys.argv)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INSTR = HERE.parent / "instruments"
NOTES = HERE.parent / "notes"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(INSTR))
sys.path.insert(0, str(ROOT / "apollo" / "src"))
sys.path.insert(0, str(ROOT / "apollo" / "scripts"))
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))

import blackboard_evolve as be                        # noqa: E402
from blackboard import BlackboardState, run_pipeline  # noqa: E402
from o1_enumerate import KNOWN_0833                   # noqa: E402
from _answer_slice import D as _SLICE                 # noqa: E402
from bundle_test import skey, table                   # noqa: E402
import lexis_pair                                     # noqa: E402
import consumer_utility as cu                         # noqa: E402

CHARON = ROOT / "roles" / "Charon" / "apollo_e9"
G7 = NOTES / "g7_charon_result.json"

PARSED_SLOTS = ("numbers", "names", "relations", "quantities", "question_target")
DERIVED_SLOTS = ("counts", "ordered", "max_value", "comparison", "extreme_number",
                 "rules", "facts", "derived_facts")


def git(*args):
    try:
        return subprocess.check_output(["git", *args], cwd=str(ROOT), text=True).strip()
    except Exception:                                   # noqa: BLE001
        return None


# ── oracle semantic states, keyed by Charon's ORIGINAL file index ─────────────────
# (winner, loser) pairs mean "winner dominates loser" for op_build_ordering; select_nth
# indexes `ordered` by question_target: first=0, second=1, third=2, smallest=-1.
NO = "NO_SLOT"
ORACLE = {
    # numeric_comparison -- Charon's candidates are ENTITY NAMES, Apollo's home readout for
    # this category (score_by_comparison__g) selects yes/no. The only clean readout that
    # can select a name is select_nth__g over `ordered`.
    0:  {"parsed": {"quantities": {"the cargo drone": 47.5, "the survey drone": 47.05},
                    "question_target": "first"}, "parsed_run": [],
         "derived": {"relations": [["the cargo drone", "the survey drone"]],
                     "question_target": "first"},
         "derived_run": ["op_build_ordering", "select_nth__g"],
         "encodes": "relation direction = 'more'; readout by entity phrase"},
    1:  {"parsed": {"quantities": {"station A": -12, "station B": -3},
                    "question_target": "first"}, "parsed_run": [],
         "derived": {"relations": [["station A", "station B"]], "question_target": "first"},
         "derived_run": ["op_build_ordering", "select_nth__g"],
         "encodes": "relation direction = 'colder' (min); readout by entity phrase"},
    2:  {"parsed": {"quantities": {"the reservoir at 3/8": 0.375, "the reservoir at 0.4": 0.4},
                    "question_target": "first"}, "parsed_run": [],
         "derived": {"relations": [["the reservoir at 0.4", "the reservoir at 3/8"]],
                     "question_target": "first"},
         "derived_run": ["op_build_ordering", "select_nth__g"],
         "encodes": "fraction/decimal already compared; readout by entity phrase"},
    3:  {"parsed": {"quantities": {"ledger A": 1204000, "ledger B": 1240000},
                    "question_target": "first"}, "parsed_run": [],
         "derived": {"relations": [["ledger B", "ledger A"]], "question_target": "first"},
         "derived_run": ["op_build_ordering", "select_nth__g"],
         "encodes": "thousands separators already parsed; readout by entity phrase"},
    4:  {"parsed": {"quantities": {"machine A": 2.25, "machine B": 2.2},
                    "question_target": "first"}, "parsed_run": [],
         "derived": {"relations": [["machine A", "machine B"]], "question_target": "first"},
         "derived_run": ["op_build_ordering", "select_nth__g"],
         "encodes": "rates 9/4 vs 11/5 already computed; readout by entity phrase"},
    5:  {"parsed": {"quantities": {"the beam": 1.25, "the rod": 1.25}}, "parsed_run": [],
         "derived": NO, "derived_run": [],
         "encodes": "EQUALITY: no slot represents a tie and no readout selects it"},
    # numeric_stated_premise -- Charon's tasks are PRODUCTS; the home category of the same
    # name is 'which number is larger' (parse_which_extreme -> score_by_extreme_number__g).
    # Same label, different verb. No clean operator multiplies.
    6:  {"parsed": {"numbers": [18, 7]}, "parsed_run": [],
         "derived": {"counts": {"bolts": {"count": 126}}},
         "derived_run": ["op_aggregate_quantities", "score_by_aggregate__g"],
         "encodes": "the product; parse_box_items would have written this for 'boxes with'"},
    7:  {"parsed": {"numbers": [250, 6]}, "parsed_run": [],
         "derived": {"counts": {"stock": {"count": 1500}}},
         "derived_run": ["op_aggregate_quantities", "score_by_aggregate__g"],
         "encodes": "the product"},
    8:  {"parsed": {"numbers": [3.5, 8]}, "parsed_run": [],
         "derived": {"counts": {"litres": {"count": 28}}},
         "derived_run": ["op_aggregate_quantities", "score_by_aggregate__g"],
         "encodes": "the product"},
    9:  {"parsed": {"numbers": [42, 15]}, "parsed_run": [],
         "derived": {"counts": {"lines": {"count": 630}}},
         "derived_run": ["op_aggregate_quantities", "score_by_aggregate__g"],
         "encodes": "the product"},
    10: {"parsed": {"numbers": [23, 14]}, "parsed_run": [],
         "derived": {"counts": {"credits": {"count": 322}}},
         "derived_run": ["op_aggregate_quantities", "score_by_aggregate__g"],
         "encodes": "the product"},
    11: {"parsed": {"numbers": [240, 45]}, "parsed_run": [],
         "derived": {"counts": {"samples": {"count": 180}}},
         "derived_run": ["op_aggregate_quantities", "score_by_aggregate__g"],
         "encodes": "the product after a unit conversion (per minute -> 45 s)"},
    # transitivity -- home path parse_ordinal -> parse_names_and_relations ->
    # op_build_ordering -> select_nth__g. Parsed level IS the home path's input.
    12: {"parsed": {"names": ["Ana", "Bruno", "Chen"],
                    "relations": [["Ana", "Bruno"], ["Bruno", "Chen"]],
                    "question_target": "first"},
         "parsed_run": ["op_build_ordering", "select_nth__g"],
         "derived": {"ordered": ["Ana", "Bruno", "Chen"], "question_target": "first"},
         "derived_run": ["select_nth__g"], "encodes": "taller = dominates"},
    13: {"parsed": {"names": ["crate W", "crate X", "crate Y", "crate Z"],
                    "relations": [["crate W", "crate X"], ["crate X", "crate Y"],
                                  ["crate Y", "crate Z"]],
                    "question_target": "smallest"},
         "parsed_run": ["op_build_ordering", "select_nth__g"],
         "derived": {"ordered": ["crate W", "crate X", "crate Y", "crate Z"],
                     "question_target": "smallest"},
         "derived_run": ["select_nth__g"],
         "encodes": "'lightest' -> index -1, spelled 'smallest' (select_nth has no 'last')"},
    14: {"parsed": {"names": ["Mira", "Noor", "Omar"],
                    "relations": [["Mira", "Noor"], ["Noor", "Omar"]],
                    "question_target": "smallest"},
         "parsed_run": ["op_build_ordering", "select_nth__g"],
         "derived": {"ordered": ["Mira", "Noor", "Omar"], "question_target": "smallest"},
         "derived_run": ["select_nth__g"],
         "encodes": "'finished last' -> index -1, spelled 'smallest'"},
    15: {"parsed": {"names": ["Kai", "Lena", "Mateo"],
                    "relations": [["Kai", "Lena"], ["Mateo", "Lena"]],
                    "question_target": "first"}, "parsed_run": [],
         "derived": NO, "derived_run": [],
         "encodes": "UNDERDETERMINED: `ordered` cannot represent 'cannot be determined'; "
                    "op_build_ordering breaks the Kai/Mateo tie arbitrarily"},
    16: {"parsed": {"names": ["item R", "item S", "item T", "item U"],
                    "relations": [["item R", "item S"], ["item S", "item T"],
                                  ["item T", "item U"]]}, "parsed_run": [],
         "derived": {"comparison": True}, "derived_run": ["score_by_comparison__g"],
         "encodes": "yes/no question over a chain; no op derives `comparison` from "
                    "`relations`", "readout_only": True},
    17: {"parsed": {"names": ["village D", "village E", "village F"],
                    "relations": [["village F", "village E"], ["village E", "village D"]],
                    "question_target": "first"},
         "parsed_run": ["op_build_ordering", "select_nth__g"],
         "derived": {"ordered": ["village F", "village E", "village D"],
                     "question_target": "first"},
         "derived_run": ["select_nth__g"], "encodes": "north = dominates"},
    # all_but_n -- parse_numbers fires; nothing in the clean pool subtracts; the only clean
    # reader of max_value (score_by_aggregate__g) is guarded on `counts`, not max_value.
    18: {"parsed": {"numbers": [60, 14]}, "parsed_run": [],
         "derived": {"counts": {"sealed": {"count": 46}}},
         "derived_run": ["op_aggregate_quantities", "score_by_aggregate__g"],
         "encodes": "N - K"},
    19: {"parsed": {"numbers": [33, 8]}, "parsed_run": [],
         "derived": {"counts": {"hardback": {"count": 25}}},
         "derived_run": ["op_aggregate_quantities", "score_by_aggregate__g"],
         "encodes": "N - K"},
    20: {"parsed": {"numbers": [120, 27]}, "parsed_run": [],
         "derived": {"counts": {"occupied": {"count": 93}}},
         "derived_run": ["op_aggregate_quantities", "score_by_aggregate__g"],
         "encodes": "N - K"},
    21: {"parsed": {"numbers": [5, 19]}, "parsed_run": [],
         "derived": {"counts": {"reported": {"count": 14}}},
         "derived_run": ["op_aggregate_quantities", "score_by_aggregate__g"],
         "encodes": "N - K with the numbers in reversed prompt order"},
    22: {"parsed": {"numbers": [250, 36]}, "parsed_run": [],
         "derived": {"counts": {"failed": {"count": 36}}},
         "derived_run": ["op_aggregate_quantities", "score_by_aggregate__g"],
         "encodes": "the COMPLEMENT K, not N - K (the frozen pair answers 214 here)"},
    23: {"parsed": {"numbers": [84, 11]}, "parsed_run": [],
         "derived": {"counts": {"invalid": {"count": 11}}},
         "derived_run": ["op_aggregate_quantities", "score_by_aggregate__g"],
         "encodes": "the COMPLEMENT K, not N - K (the frozen pair answers 73 here)"},
    # temporal_ordering -- no home path (home 0/5). Nearest existing derivation: relations
    # (earlier dominates later) -> op_build_ordering -> select_nth__g.
    24: {"parsed": {"relations": [["the alarm sounded", "the door opened"],
                                  ["the door opened", "the lights came on"]],
                    "question_target": "smallest"},
         "parsed_run": ["op_build_ordering", "select_nth__g"],
         "derived": {"ordered": ["the alarm sounded", "the door opened", "the lights came on"],
                     "question_target": "smallest"},
         "derived_run": ["select_nth__g"],
         "encodes": "earlier = dominates; 'last' -> index -1 spelled 'smallest'"},
    25: {"parsed": {"relations": [["the site was cleared", "the permit was issued"],
                                  ["the permit was issued", "the survey was filed"]],
                    "question_target": "first"},
         "parsed_run": ["op_build_ordering", "select_nth__g"],
         "derived": {"ordered": ["the site was cleared", "the permit was issued",
                                 "the survey was filed"], "question_target": "first"},
         "derived_run": ["select_nth__g"],
         "encodes": "'after' inverted to earlier = dominates"},
    26: {"parsed": {"relations": [["packet A", "packet B"], ["packet B", "packet C"],
                                  ["packet C", "packet D"]], "question_target": "third"},
         "parsed_run": ["op_build_ordering", "select_nth__g"],
         "derived": {"ordered": ["packet A", "packet B", "packet C", "packet D"],
                     "question_target": "third"},
         "derived_run": ["select_nth__g"], "encodes": "earlier = dominates; 'third' -> 2"},
    27: {"parsed": {"relations": [["event Y", "event X"], ["event X", "event Z"]],
                    "question_target": "second"},
         "parsed_run": ["op_build_ordering", "select_nth__g"],
         "derived": {"ordered": ["event Y", "event X", "event Z"],
                     "question_target": "second"},
         "derived_run": ["select_nth__g"], "encodes": "'after' inverted; 'second' -> 1"},
    28: {"parsed": {"relations": [["the contract was signed", "the invoice was paid"],
                                  ["the invoice was paid", "the audit began"],
                                  ["the audit began", "the report was signed"]],
                    "question_target": "first"},
         "parsed_run": ["op_build_ordering", "select_nth__g"],
         "derived": {"ordered": ["the contract was signed", "the invoice was paid",
                                 "the audit began", "the report was signed"],
                     "question_target": "first"},
         "derived_run": ["select_nth__g"], "encodes": "'after' inverted; earliest -> 0"},
    29: {"parsed": {"relations": [["task P", "task Q"], ["task R", "task Q"]],
                    "question_target": "first"}, "parsed_run": [],
         "derived": NO, "derived_run": [],
         "encodes": "UNDERDETERMINED: `ordered` cannot represent it"},
    # vacuous_truth -- no slot carries a quantifier over a domain. The only reachable
    # readout is score_by_comparison__g on a boolean, which is one string match from the
    # answer: derived-level injection here measures the readout and nothing else.
    30: {"parsed": NO, "parsed_run": [], "derived": {"comparison": True},
         "derived_run": ["score_by_comparison__g"], "readout_only": True,
         "encodes": "universal over an empty domain -> true"},
    31: {"parsed": NO, "parsed_run": [], "derived": {"comparison": True},
         "derived_run": ["score_by_comparison__g"], "readout_only": True,
         "encodes": "universal over an empty domain -> true"},
    32: {"parsed": NO, "parsed_run": [], "derived": {"comparison": False},
         "derived_run": ["score_by_comparison__g"], "readout_only": True,
         "encodes": "universal over a non-empty domain with a counterexample -> false"},
    33: {"parsed": NO, "parsed_run": [], "derived": {"comparison": False},
         "derived_run": ["score_by_comparison__g"], "readout_only": True,
         "encodes": "existential over an empty domain -> false"},
    34: {"parsed": NO, "parsed_run": [], "derived": {"comparison": True},
         "derived_run": ["score_by_comparison__g"], "readout_only": True,
         "encodes": "conditional with unsatisfiable antecedent -> true"},
    35: {"parsed": NO, "parsed_run": [], "derived": {"comparison": True},
         "derived_run": ["score_by_comparison__g"], "readout_only": True,
         "encodes": "universal over an empty domain -> true"},
    # consistency_check -- 36 is an order cycle (relations exist; no cycle-detection op in
    # the clean pool; the unadmitted G5 candidate lexis_op_order_consistent is the nearest
    # object). 37-41 are constraint systems with no slot at all.
    36: {"parsed": {"names": ["P", "Q", "R"],
                    "relations": [["P", "Q"], ["Q", "R"], ["R", "P"]]}, "parsed_run": [],
         "derived": {"comparison": False}, "derived_run": ["score_by_comparison__g"],
         "readout_only": True, "encodes": "cycle -> inconsistent -> 'no'"},
    37: {"parsed": NO, "parsed_run": [], "derived": {"comparison": True},
         "derived_run": ["score_by_comparison__g"], "readout_only": True,
         "encodes": "consistent scheduling statements"},
    38: {"parsed": NO, "parsed_run": [], "derived": {"comparison": False},
         "derived_run": ["score_by_comparison__g"], "readout_only": True,
         "encodes": "linear system with x=7 contradicts x+y=10, x-y=2 (x=6)"},
    39: {"parsed": NO, "parsed_run": [], "derived": {"comparison": True},
         "derived_run": ["score_by_comparison__g"], "readout_only": True,
         "encodes": "a satisfying day assignment exists"},
    40: {"parsed": NO, "parsed_run": [], "derived": {"comparison": True},
         "derived_run": ["score_by_comparison__g"], "readout_only": True,
         "encodes": "25 + 12 <= 40"},
    41: {"parsed": NO, "parsed_run": [], "derived": {"comparison": False},
         "derived_run": ["score_by_comparison__g"], "readout_only": True,
         "encodes": "syllogism: technician -> certified -> not nights, Sam works nights"},
}


def inject_and_run(task, slots, run_names):
    s = BlackboardState(problem_text=task["prompt"], candidates=list(task["candidates"]))
    for k, v in slots.items():
        if k == "relations":
            v = [tuple(p) for p in v]
        setattr(s, k, copy.deepcopy(v))
    for n in run_names:
        s = be.REGISTRY[n][0](s)
    return s.selected_answer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(HERE))
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw = json.loads((CHARON / "charon_battery_E9.json").read_text(encoding="utf-8"))
    meta = json.loads((CHARON / "charon_battery_E9_metadata.json").read_text(encoding="utf-8"))
    meta_by_idx = {m["index"]: m for m in meta["per_task"]}
    g7 = json.loads(G7.read_text(encoding="utf-8"))

    # G7 rows are in sorted-category order; map back to Charon's original index by prompt.
    sorted_tasks = [t for c in sorted({t["category"] for t in raw})
                    for t in raw if t["category"] == c]
    sorted_pos = {t["prompt"]: i for i, t in enumerate(sorted_tasks)}
    base_arm = g7["arms"]["baseline C"]
    pair_arm = g7["arms"]["C + compute + readout"]
    base_reach, base_rob = set(base_arm["reach_tasks"]), set(base_arm["robust"])
    pair_reach, pair_rob = set(pair_arm["reach_tasks"]), set(pair_arm["robust"])
    dS_set, dE_set = set(g7["dS_bound"]), set(g7["dE_bound"])
    abn_trace = {r["prompt"]: r for r in g7["all_but_n_pair_trace"]}

    base_names = [n for n in sorted(be.REGISTRY)
                  if (be.role_of(n) == "transformer" or n in be.GUARDED_SCORERS)
                  and set(be.REGISTRY[n][0].writes) & set(_SLICE)]
    base_ops = [be.REGISTRY[n][0] for n in base_names]
    known_ops = [be.REGISTRY[n][0] for n in KNOWN_0833]
    _, bundle_ops = lexis_pair.augmented_program("readout_last", verify=False)

    rows, selfcheck = [], collections.Counter()
    for i, t in enumerate(raw):
        s0 = BlackboardState(problem_text=t["prompt"], candidates=list(t["candidates"]))
        k0 = skey(s0)
        fired = []
        for nm, op in zip(base_names, base_ops):
            try:
                s2 = op(copy.deepcopy(s0))
            except Exception:                            # noqa: BLE001
                s2 = s0
            if skey(s2) != k0:
                fired.append(nm)
        delta, ok = table(t["prompt"], t["candidates"], t["correct"], base_ops)
        sp = sorted_pos[t["prompt"]]
        base_sel = cu.run_program(known_ops, [t])[0]
        bundle_sel = cu.run_program(bundle_ops, [t])[0]
        m = meta_by_idx[i]
        o = ORACLE[i]

        levels = {}
        for lvl in ("parsed", "derived"):
            slots = o[lvl]
            run = o[lvl + "_run"]
            entry = {"slots": slots, "then_run": run}
            if slots == NO:
                entry["status"] = "NO_SLOT"
                entry["verified"] = None
            elif not run:
                entry["status"] = "NO_CONSUMER_OP (B-gap by construction)"
                entry["verified"] = None
            else:
                got = inject_and_run(t, slots, run)
                entry["status"] = "PATH_EXISTS"
                entry["verified"] = (got == t["correct"])
                entry["selected"] = got
                selfcheck[(lvl, entry["verified"])] += 1
            if lvl == "derived" and o.get("readout_only"):
                entry["readout_only"] = True
            levels[lvl] = entry
        # which of A/B/C the fixture can discriminate for this task
        p, d = levels["parsed"], levels["derived"]
        if p["status"] == "PATH_EXISTS":
            disc = "A vs (B or C): parsed-level path exists"
        elif d["status"] == "PATH_EXISTS" and not d.get("readout_only"):
            disc = "B vs C: parsed level has no consumer; derived-level path exists"
        elif d["status"] == "PATH_EXISTS":
            disc = "C only: derived injection is one string match from the answer"
        else:
            disc = "NONE: no slot can carry the needed state at either level"

        rows.append({
            "charon_index": i, "g7_sorted_index": sp, "category": t["category"],
            "prompt": t["prompt"], "candidates": list(t["candidates"]),
            "correct": t["correct"], "correct_slot": m["correct_slot"],
            "candidate_lens": m["candidate_lens"],
            "correct_is_longest": m["correct_is_longest"],
            "correct_is_strictly_longest": m["correct_is_strictly_longest"],
            "correct_is_shortest": m["correct_is_shortest"],
            "correct_is_strictly_shortest": m["correct_is_strictly_shortest"],
            "recognition": {
                "fired_at_initial_state": fired,
                "closure_size_under_C": len(delta),
                "unrecognised": len(delta) == 1,
                "number_extraction_only": fired == ["parse_numbers"],
                "reaches_meaningful_representation": not (len(delta) == 1
                                                           or fired == ["parse_numbers"]),
            },
            "baseline": {
                "organism": "KNOWN_0833",
                "outcome": base_sel["outcome"], "selected": base_sel["selected"],
                "correct_reachable_under_C": sp in base_reach,
                "robust_under_C_all_24_permutations": sp in base_rob,
                "positional_fallback": (base_sel["outcome"] == "CORRECT"
                                        and sp not in base_rob),
                "class": ("solved" if base_sel["outcome"] == "CORRECT"
                          else "dS_bound" if sp in dS_set else "dE_bound"),
            },
            "frozen_pair": {
                "reachable_with_pair": sp in pair_reach,
                "robust_with_pair": sp in pair_rob,
                "bundle_readout_last_outcome": bundle_sel["outcome"],
                "bundle_readout_last_selected": bundle_sel["selected"],
                "trace": abn_trace.get(t["prompt"]),
            },
            "injection": levels,
            "oracle_encodes": o["encodes"],
            "discriminates": disc,
        })

    n = len(rows)
    summary = {
        "n_tasks": n,
        "unrecognised": sum(r["recognition"]["unrecognised"] for r in rows),
        "number_extraction_only": sum(r["recognition"]["number_extraction_only"] for r in rows),
        "fail_before_capability_layer": sum(
            not r["recognition"]["reaches_meaningful_representation"] for r in rows),
        "baseline_outcomes": cu.counts([r["baseline"]["outcome"] for r in rows]),
        "class_counts": dict(collections.Counter(r["baseline"]["class"] for r in rows)),
        "parsed_level": dict(collections.Counter(r["injection"]["parsed"]["status"] for r in rows)),
        "derived_level": dict(collections.Counter(r["injection"]["derived"]["status"] for r in rows)),
        "derived_readout_only": sum(bool(r["injection"]["derived"].get("readout_only")) for r in rows),
        "selfcheck_paths": {"%s_%s" % (l, v): c for (l, v), c in sorted(selfcheck.items(),
                                                                       key=lambda kv: str(kv[0]))},
        "discriminates": dict(collections.Counter(r["discriminates"] for r in rows)),
    }
    fixture = {
        "fixture": "lexis_g7_state_injection_fixture",
        "version": 1,
        "battery": "roles/Charon/apollo_e9/charon_battery_E9.json",
        "battery_commit": "5097b0c8f",
        "evidence": "roles/Lexis/notes/g7_charon_result.json",
        "clean_pool_C": base_names,
        "production_organism": KNOWN_0833,
        "slot_groups": {"parsed": list(PARSED_SLOTS), "derived": list(DERIVED_SLOTS)},
        "experiment": {
            "question": "If the surface layer is bypassed and the correct semantic state is "
                        "injected, can the existing substrate solve the task?",
            "arms": {
                "A_raw": "KNOWN_0833 on the raw prompt (= E9; 2/42, 40 abstain)",
                "B_oracle_parsed": "inject `injection.parsed.slots`, run `then_run`, score",
                "B_oracle_derived": "inject `injection.derived.slots`, run `then_run`, score",
                "C_corrupted": "consumer-owned: inject a plausible-but-wrong state of the same "
                               "shape (e.g. swapped relation direction, off-by-one count) and "
                               "confirm the gold does NOT come out; a level whose corrupted arm "
                               "also scores is an answer leak, not a capability",
            },
            "readings": {
                "A_surface": "raw fails, parsed-level oracle solves",
                "B_capability": "parsed-level has no consumer or fails; derived-level solves",
                "C_readout": "derived-level path fails, or exists only as readout_only",
                "score_readout_only_separately": "rows with injection.derived.readout_only "
                                                 "must be reported apart from the rest; they "
                                                 "carry no capability content",
            },
            "not_run_here": "the fixture self-check runs each oracle path once to prove the "
                            "fixture is consumable; the arm comparison and the corrupted "
                            "control are the consumer's experiment",
        },
        "summary": summary,
        "tasks": rows,
    }
    (out_dir / "state_injection_fixture.json").write_text(
        json.dumps(fixture, indent=1), encoding="utf-8")

    # ── manifest ─────────────────────────────────────────────────────────────────
    src = INSTR / "candidate_primitives.py"
    src_text = src.read_text(encoding="utf-8")

    def func_src(name):
        start = src_text.index("@blackboard_op(", src_text.index('name="%s"' % name) - 400)
        end = src_text.index("\n\n\n", start)
        return src_text[start:end]

    pair = lexis_pair.load(verify=False)
    home_pair = json.loads((NOTES / "bundle_test_result.json").read_text(encoding="utf-8"))
    manifest = {
        "artifact": "lexis_interface_pair",
        "version": 1,
        "status": "QUARANTINED_CANDIDATE",
        "status_meaning": "frozen, hash-pinned, importable, NOT admitted, NOT promoted, NOT "
                          "registered in apollo/. Admission is the consumer's decision.",
        "claim_ceiling": "MEASURED ACROSS TWO AUTHORS / ONE INDEPENDENT AUTHORSHIP CHANGE. "
                         "Not 'generally transferable', not 'generally useful'.",
        "source": {
            "file": "roles/Lexis/instruments/candidate_primitives.py",
            "sha256": pair["sha256"],
            "git_blob": git("rev-parse", "HEAD:roles/Lexis/instruments/candidate_primitives.py"),
            "commits": {
                "compute_added": {"sha": "043dc92ac", "when": "2026-08-25 02:20:49 -0400"},
                "readout_added": {"sha": "30b96a91e", "when": "2026-08-25 06:49:52 -0400"},
                "blind_battery_entered_repo": {"sha": "5097b0c8f",
                                               "when": "2026-08-25 09:36:44 -0400"},
                "lexis_first_read_battery": "2026-08-27",
            },
            "loader": "roles/Lexis/handoff/lexis_pair.py",
        },
        "primitives": {
            "compute": {
                "name": lexis_pair.COMPUTE, "reads": ["numbers"], "writes": ["max_value"],
                "precondition": "len(state.numbers) >= 2",
                "semantics": "max_value := (largest parsed number) - (second largest)",
                "required_upstream": "parse_numbers (Apollo registry; NOT in KNOWN_0833)",
                "alone": {"home_dE": 0, "home_dS": 0, "home_dROBUST": 0,
                          "charon_dE": 0, "charon_dS": 0, "charon_dROBUST": 0,
                          "why": "the only clean-pool reader of max_value, "
                                 "score_by_aggregate__g, is guarded on len(counts) > 0, "
                                 "which this primitive does not write"},
                "source": func_src(lexis_pair.COMPUTE),
            },
            "readout": {
                "name": lexis_pair.READOUT, "reads": ["candidates", "max_value"],
                "writes": ["selected_answer"],
                "precondition": "max_value is not None and candidates non-empty",
                "semantics": "select the candidate whose LEADING integer equals "
                             "round(max_value); content match, hence permutation-equivariant",
                "alone": {"home_dE": 0, "home_dS": 0, "home_dROBUST": 0,
                          "charon_dE": 0, "charon_dS": 0, "charon_dROBUST": 0,
                          "why": "nothing in the clean pool writes max_value on these tasks"},
                "source": func_src(lexis_pair.READOUT),
            },
            "complementarity": "each alone moves nothing on either battery; together "
                               "+5/5 (home all_but_n) and +4/6 (Charon all_but_n), both "
                               "permutation-robust. A wrong value cannot be rescued by a "
                               "reader, so the pair rules out dead computation.",
        },
        "evidence": {
            "home_T_home_120": {"pair_dE": home_pair["C + compute + readout"]["dE"],
                                "pair_dS": home_pair["C + compute + readout"]["dS"],
                                "pair_dROBUST": home_pair["C + compute + readout"]["dROBUST"],
                                "source": "roles/Lexis/notes/bundle_test_result.json"},
            "charon_T_charon_42": {"pair_dE": pair_arm["dE"], "pair_dS": pair_arm["dS"],
                                   "pair_dROBUST": pair_arm["dROBUST"],
                                   "all_but_n_correct": 4, "all_but_n_wrong_guess": 2,
                                   "wrong_guess_tasks_all_but_n": [22, 23],
                                   "wrong_guess_mechanism": "prompts ask for the COMPLEMENT "
                                   "('how many failed?'); the pair answers N-K and the "
                                   "distractor set contains it; the organism ABSTAINED here",
                                   "organism_level_whole_battery": {
                                       "ABSTAIN_to_CORRECT": 4, "ABSTAIN_to_WRONG": 3,
                                       "third_wrong_task": 11,
                                       "third_wrong_mechanism": "numeric_stated_premise "
                                       "'240 per minute, 45 seconds': 240-45=195 and Charon "
                                       "placed 195 among the distractors; the pair fires on "
                                       "ANY two-number prompt whose difference is a candidate",
                                       "break_even_wrong_penalty": "4/3 -- helps under "
                                       "(1,0,-1), hurts under (1,0,-2) and fail-closed"},
                                   "source": "roles/Lexis/notes/g7_charon_result.json and "
                                             "roles/Lexis/handoff/consumer_utility_result.json"},
            "home_organism_level_regression": {
                "finding": "inserted into the production organism AFTER its transformers "
                           "(readout_last / readout_first), the COMPUTE primitive alone flips "
                           "9 home synth two_stage_count tasks CORRECT->WRONG on the seed-0 "
                           "draw (range over 5 hash-seed draws in consumer_utility_result.json)",
                "mechanism": "write-write hazard on the REUSED slot max_value: "
                             "op_aggregate_quantities writes the box total, the compute "
                             "primitive overwrites it with (max - second max), and "
                             "score_by_aggregate__g (guarded on counts) routes the wrong value. "
                             "The primitive's own docstring says it 'deliberately reuses an "
                             "existing slot'; that reuse is the defect.",
                "placement_that_avoids_it": "compute_first (parse_numbers, compute, T..., S..., "
                                            "readout): +5 CORRECT, 0 WRONG on the seed-0 draw; "
                                            "op_aggregate_quantities then overwrites the "
                                            "compute value on box tasks. The hazard is not "
                                            "removed, it is ordered around. Placement is the "
                                            "consumer's decision and must be re-measured on "
                                            "the consumer's organism.",
                "why_the_ceiling_did_not_show_it": "the joint BFS reports the best program in "
                                                    "the closure, which orders around the "
                                                    "hazard; a fixed organism does not",
                "source": "roles/Lexis/handoff/consumer_utility_result.json"},
            "permutation_robustness": "all 24 orderings of the 4 candidates (G6); passing "
                                      "proves equivariance, NOT reasoning",
            "gates_cleared": ["G5 NEW=1 (not representable by existing vocabulary)",
                              "G6 all-24-permutation on every credited dE",
                              "G7 authorship independence, by git timestamp",
                              "congruence audit (no aliasing / hidden state)"],
            "gates_NOT_cleared": ["consumer trial under the consumer's loss function",
                                  "admission", "post-admission monitoring"],
        },
        "failure_modes": [
            "asks for the complement / a quantity other than (max - second max): answers "
            "WRONG, does not abstain (Charon 22, 23)",
            "any two-number prompt whose (max - second max) appears among the candidates: "
            "answers WRONG (Charon 11: 240-45=195)",
            "WRITE-WRITE HAZARD on max_value with op_aggregate_quantities when placed after it "
            "in a pipeline that carries parse_box_items: 9 home regressions on the seed-0 "
            "draw; see evidence.home_organism_level_regression",
            "the home battery's synth subset depends on PYTHONHASHSEED: any per-task home "
            "number is a property of a draw; artifacts here pin seed 0 and report a sweep",
            "three or more numbers in the prompt: subtracts the two largest regardless of "
            "role (untested outside 2-number prompts)",
            "candidates that do not begin with an integer: readout abstains",
            "max_value written by another operator (op_aggregate_quantities) before the "
            "readout: the readout will route THAT value (placement-dependent; measured in "
            "consumer_utility_result.json)",
        ],
        "prohibitions": [
            "do not describe as admitted, promoted, transferable, or generally useful",
            "do not modify or re-tune against Charon's battery (spent for Lexis 2026-09-01)",
            "do not register in apollo/ without a consumer trial and an operator decision",
        ],
        "consumer_acceptance": "roles/Lexis/handoff/consumer_utility.py -- CORRECT / "
                               "ABSTAIN / WRONG under the consumer's own payoffs",
        "spent_for": [{"seat": "Lexis", "battery": "roles/Charon/apollo_e9/charon_battery_E9.json",
                       "read": "2026-08-27", "measured": "2026-09-01"}],
        "trial": [], "decision": [], "monitoring": [],
        "protocol": "roles/Lexis/handoff/ADMISSION_PROTOCOL.md (stage 3 of 6)",
    }
    (out_dir / "interface_pair_manifest.json").write_text(
        json.dumps(manifest, indent=1), encoding="utf-8")

    # ── consumer utility, both batteries, all arms ───────────────────────────────
    from o1_enumerate import build_battery               # noqa: E402
    from g7_remeasure import load_charon                 # noqa: E402
    batteries = {"home": build_battery()[0], "charon": load_charon()[0]}
    ag = lambda pl, c=True, r=True: lexis_pair.augmented_program(pl, c, r, verify=False)  # noqa: E731
    arms = {
        "+parse_numbers only": ag("readout_last", False, False),
        "+parse_numbers +compute": ag("readout_last", True, False),
        "+parse_numbers +readout": ag("readout_last", False, True),
        "+bundle readout_last": ag("readout_last"),
        "+bundle readout_first": ag("readout_first"),
        "+bundle compute_first": ag("compute_first"),
    }
    util = {"losses": {k: list(v) for k, v in cu.LOSSES.items()}, "batteries": {}}
    for bname, tasks in batteries.items():
        base = cu.run_program(known_ops, tasks)
        util["batteries"][bname] = {"baseline_counts": cu.counts(base), "arms": {}}
        for aname, (names, ops) in arms.items():
            cand = cu.run_program(ops, tasks)
            cmp = cu.compare(base, cand)
            cmp["program"] = names
            cmp["changed_tasks"] = [{"i": i, "base": b["outcome"], "cand": c["outcome"],
                                     "selected": c["selected"]}
                                    for i, (b, c) in enumerate(zip(base, cand))
                                    if b["outcome"] != c["outcome"]]
            util["batteries"][bname]["arms"][aname] = cmp
    # home-battery spread over PYTHONHASHSEED draws (the synth subset is redrawn per seed)
    sweep = {}
    for seed in ("0", "1", "2", "3", "4"):
        env = dict(os.environ, PYTHONHASHSEED=seed)
        outp = out_dir / ("_sweep_%s.json" % seed)
        subprocess.run([sys.executable, str(HERE / "consumer_utility.py"), "--battery", "home",
                        "--out", str(outp)], env=env, check=True, capture_output=True)
        r = json.loads(outp.read_text(encoding="utf-8"))["batteries"]["home"]["arms"]
        outp.unlink()
        sweep[seed] = {a: {"delta": r[a]["delta"], "transitions": r[a]["transitions"]}
                       for a in ("+parse_numbers +compute", "+bundle readout_last",
                                 "+bundle compute_first")}
    util["home_hashseed_sweep"] = {
        "note": "the home synth subset (tasks 50-79) is redrawn with PYTHONHASHSEED; "
                "each seed is a different draw of 30 tasks; the artifacts above use seed 0",
        "seeds": sweep,
        "compute_only_CORRECT_to_WRONG_range": sorted({
            v["+parse_numbers +compute"]["transitions"].get("CORRECT->WRONG", 0)
            for v in sweep.values()}),
        "compute_first_WRONG_range": sorted({v["+bundle compute_first"]["delta"]["WRONG"]
                                             for v in sweep.values()}),
        "compute_first_CORRECT_range": sorted({v["+bundle compute_first"]["delta"]["CORRECT"]
                                               for v in sweep.values()}),
    }
    (out_dir / "consumer_utility_result.json").write_text(
        json.dumps(util, indent=1), encoding="utf-8")

    print("fixture summary:", json.dumps(summary, indent=1))
    for bname in util["batteries"]:
        for aname in ("+parse_numbers +compute", "+bundle readout_last", "+bundle compute_first"):
            print(cu.fmt_report("%s / %s" % (bname, aname),
                                util["batteries"][bname]["arms"][aname]))
            print()
    print("wrote 3 artifacts to %s" % out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
