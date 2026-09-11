"""Emit the TECHNE-12 shrink-target fixture with exactly enumerated ground truth.

    python proteus/eval/emit_shrink_fixture.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from proteus.eval import boolean as B  # noqa: E402
from proteus.eval import shrink as S  # noqa: E402
from proteus.foundry.identity import canonical_json, sha256_hex  # noqa: E402

I, C, Not, And, Or, Xor = B.I, B.C, B.Not, B.And, B.Or, B.Xor
OUT = os.path.join(HERE, "SHRINK_TARGET_FIXTURE.json")

XOR3 = Xor(Xor(I(0), I(1)), I(2))
AND01 = And(I(0), I(1))
START_XOR3 = Xor(Xor(Xor(I(0), I(1)), I(2)), Xor(I(0), I(0)))
START_AND01 = And(And(I(0), I(1)), Or(I(1), I(1)))


def row(name, target, start, predicate, max_size):
    gt = S.minimal_by_enumeration(target, predicate, max_size=max_size)
    return {
        "name": name,
        "target": S.canonical(target),
        "target_truth_table": "".join(map(str, B.truth_table(target))),
        "predicate": predicate,
        "start_program": S.canonical(start),
        "start_size": S.program_size(start),
        "start_satisfies_predicate": S.PREDICATES[predicate](start, target),
        "enumerated_to_size": max_size,
        "ground_truth": {"canonical": gt["canonical"], "size": gt["size"],
                         "depth": gt["depth"]},
    }


def main():
    doc = {
        "schema": "proteus.shrink_target_fixture/1",
        "interface_version": B.INTERFACE_VERSION,
        "shrink_contract": S.SHRINK_CONTRACT,
        "declared_size_order": (
            "(node_count, depth, canonical_string). Node count is primary because it is the cost "
            "the kind charges and the quantity a component library is claimed to reduce. Depth "
            "breaks ties toward flatter programs. The canonical string is ONLY to make the order "
            "total; it carries no simplicity claim."),
        "post_conditions": {
            "still_a_counterexample": (
                "a shrunk program must still DISAGREE with the target under Proteus's evaluator; "
                "budget exhaustion is a status and NOT a witness, so a starved program does not "
                "satisfy this"),
            "still_solves": (
                "a shrunk program must still pass EVERY declared case with full coverage; "
                "no-witness alone is never solved"),
        },
        "measured_triviality": (
            "still_a_counterexample has minimum node count 1 for ALL 256 three-input targets: the "
            "five leaves have five distinct truth tables, so at least four disagree with any "
            "target. Enumeration is exact and cheaper. This is the same honest limit Techne found "
            "for assignments. still_solves is the non-trivial target."),
        "known_answers": [
            row("xor3", XOR3, START_XOR3, "still_solves", 5),
            row("and01", AND01, START_AND01, "still_solves", 5),
            row("xor3_counterexample", XOR3, C(0), "still_a_counterexample", 2),
        ],
        "observed_hypothesis_behaviour": {
            "note": ("RECORDED, NOT ASSERTED. Hypothesis shrinks toward its own notion of "
                     "simplicity. These are observations from hypothesis 6.165.10 via "
                     "hypothesis.find; Techne should re-measure rather than treat them as fixed."),
            "xor3": {"reached": "(xor x0 (xor x1 x2))", "size": 5,
                     "agrees_on_size": True, "agrees_on_expression": False,
                     "comment": "same size and depth as the minimum; a different member of the "
                                "tie class, separated only by our canonical tie-break"},
            "and01": {"reached": "(not (not (and x0 x1)))", "size": 5,
                      "agrees_on_size": False, "agrees_on_expression": False,
                      "comment": "true minimum is 3; Hypothesis left a semantically inert double "
                                 "negation, so it did NOT minimise node count"},
        },
        "what_this_does_NOT_establish": (
            "That Hypothesis is useful here. It is SOUND under both post-conditions -- whatever "
            "it returns still satisfies the predicate -- but on and01 it returned 5 nodes against "
            "an exhaustive minimum of 3. Soundness is not minimality, and minimality under "
            "Proteus's order is what the experiment charges for."),
    }
    doc["fixture_id"] = "sha256:" + sha256_hex(canonical_json(doc))
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"wrote {os.path.relpath(OUT, ROOT)}")
    print(f"  fixture_id {doc['fixture_id']}")
    for r in doc["known_answers"]:
        print(f"  {r['name']:<20} start {r['start_program']} (size {r['start_size']}) "
              f"-> MIN {r['ground_truth']['canonical']} (size {r['ground_truth']['size']})")
    return 0


if __name__ == "__main__":
    from proteus.workspace import assert_not_canonical
    assert_not_canonical("run emit_shrink_fixture.py")
    sys.exit(main())
