"""Emit the shared WP-X8 identity fixture: two EQUAL-SCORE artifacts with DIFFERENT behaviour.

    python proteus/eval/emit_x8_fixture.py

Requested by the third amendment so X8-a can run against the Proteus identity convention. The
archive's capacities are enforced on pointers keyed by `organism_ref`, and equal-score artifacts
with different observable behaviour must remain eligible for retention. This fixture is the
minimal object that makes that testable: if retention were keyed on score alone, these two would
be indistinguishable, and one of them would be evicted for no reason.

Nothing here is called better, interesting, or a solution. Both artifacts score ZERO.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from proteus.eval import fixtures as F  # noqa: E402
from proteus.eval.identity import (FAMILY_PROGRAM, REPR_PLAYER_MANIFEST_V0,  # noqa: E402
                                   artifact_manifest, evaluation_ref, organism_ref)
from proteus.eval.library import LIBRARY_VERSION, evaluate  # noqa: E402
from proteus.foundry.affordances import AFFORDANCE_HASH  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH, canonical_json, sha256_hex  # noqa: E402

OUT = os.path.join(HERE, "X8_IDENTITY_FIXTURE.json")


def main():
    pair = F.x8_equal_score_pair()
    spec = pair["spec"]
    rows = {}
    for key, label in (("a", "halts immediately"), ("b", "never halts; exhausts its op budget")):
        man = pair[key]
        art = artifact_manifest(FAMILY_PROGRAM, man, REPR_PLAYER_MANIFEST_V0, "proteus.vm.v0.4")
        oref = organism_ref(art)
        r = evaluate(man, spec)
        rows[key] = {
            "label": label,
            "manifest": man,
            "organism_ref": oref,
            "evaluation_ref": evaluation_ref(oref, RUNTIME_HASH, AFFORDANCE_HASH,
                                             LIBRARY_VERSION, spec["spec_id"], 0,
                                             spec["ticks"], r["budget_policy"]),
            "observed": {"cases_passed": r["cases_passed"],
                         "cases_with_expectation": r["cases_with_expectation"],
                         "status_counts": r["status_counts"],
                         "steps_total": r["steps_total"], "ops_total": r["ops_total"],
                         "has_witness": r["has_witness"],
                         "witness_case_index": (r["witness"] or {}).get("case_index")},
        }

    a, b = rows["a"]["observed"], rows["b"]["observed"]
    doc = {
        "schema_version": "proteus.x8_identity_fixture.v1",
        "purpose": ("two artifacts that a score-only view cannot tell apart and an execution view "
                    "trivially can; for WP-X8's retention capacities keyed on organism_ref"),
        "identity_convention": "PR-ID (D-7); see proteus/eval/identity.py",
        "environment": {"runtime_hash": RUNTIME_HASH, "affordance_hash": AFFORDANCE_HASH,
                        "library_version": LIBRARY_VERSION, "spec_id": spec["spec_id"],
                        "budget_policy": "budget_status_only"},
        "specification": spec,
        "artifacts": rows,
        "equal_score": a["cases_passed"] == b["cases_passed"],
        "score": a["cases_passed"],
        "behaviour_differs": (a["status_counts"] != b["status_counts"]
                              or a["ops_total"] != b["ops_total"]),
        "distinct_identity": rows["a"]["organism_ref"] != rows["b"]["organism_ref"],
        "claim_boundary": ("Both artifacts score zero. Neither is called better, interesting or a "
                           "solution. The fixture demonstrates only that equal score does not "
                           "imply equal observable behaviour, so retention keyed on score alone "
                           "would discard a real distinction."),
    }
    doc["fixture_id"] = "sha256:" + sha256_hex(canonical_json(
        {k: v for k, v in doc.items() if k != "purpose"}))
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"wrote {os.path.relpath(OUT, ROOT)}")
    print(f"  fixture_id     {doc['fixture_id']}")
    for k in ("a", "b"):
        o = rows[k]
        print(f"  {k}: {o['organism_ref']}  score={o['observed']['cases_passed']} "
              f"status={o['observed']['status_counts']} ops={o['observed']['ops_total']}")
    print(f"  equal_score={doc['equal_score']} behaviour_differs={doc['behaviour_differs']} "
          f"distinct_identity={doc['distinct_identity']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
