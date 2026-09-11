"""Emit the boolean3 interface/population artifact and the declared correctness scope.

    python proteus/eval/emit_boolean3.py

Writes BOOLEAN3_POPULATION.json. The frozen USE_A registry is not read for membership and is
never written.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from proteus.eval import boolean as B  # noqa: E402
from proteus.eval import boolean_population as P  # noqa: E402
from proteus.eval.genome_read import genome_read_report  # noqa: E402
from proteus.foundry.affordances import AFFORDANCE_HASH  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH, canonical_json, sha256_hex  # noqa: E402

OUT = os.path.join(HERE, "BOOLEAN3_POPULATION.json")


def main():
    pop = P.population()
    for m in pop["members"]:
        spec = B.boolean_spec(B.I(m["sensitive_to_input"])) if m["role"] == "positive_control" \
            else B.boolean_spec(B.I(0))
        gr = genome_read_report(m["manifest"], spec)
        m["genome_read"] = {"detected": gr["detected"], "bound": "lower"}
    doc = {
        "schema_version": "proteus.boolean3_interface.v1",
        "population": pop,
        "correctness_scope": B.correctness_scope(),
        "environment": {"runtime_hash": RUNTIME_HASH, "affordance_hash": AFFORDANCE_HASH},
        "channel_verdict": ("The EXISTING input channel expresses the declared Boolean subset. "
                            "No new player interface was required; a named population and "
                            "interface version were still created so no old specimen is "
                            "redefined."),
    }
    doc["artifact_id"] = "sha256:" + sha256_hex(canonical_json(doc))
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"wrote {os.path.relpath(OUT, ROOT)}")
    print(f"  artifact_id {doc['artifact_id']}")
    for m in pop["members"]:
        print(f"  {m['name']:<6} {m['role']:<17} {m['organism_ref']}")
    return 0


if __name__ == "__main__":
    from proteus.workspace import assert_not_canonical
    assert_not_canonical("run emit_boolean3.py")
    sys.exit(main())
