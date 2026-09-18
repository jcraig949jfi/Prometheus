"""Foundry profile for the graph substrate -- the same proteus.foundry_profile.v1 record shape, a
different runtime/grammar/regime, so a graph regime can never alias a v0 regime (different
runtime_hash and affordance_hash by construction). The C4-frozen v0 catalog
(proteus/eval/FOUNDRY_PROFILE_CATALOG.json) is not touched; graph profiles live in
proteus/graph/GRAPH_PROFILE_CATALOG.json.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from proteus.eval.foundry_profile import ID_HEX, ID_PREFIX, PROFILE_SCHEMA, grammar_identity  # noqa: E402
from proteus.graph import affordances as A  # noqa: E402
from proteus.graph import grammar as GR  # noqa: E402
from proteus.graph.generate import DEFAULT_FOUNDRY_MANIFEST, validate_foundry_manifest  # noqa: E402
from proteus.graph.identity import RUNTIME_HASH, RUNTIME_VERSION, canonical_json, hash_obj  # noqa: E402

CATALOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GRAPH_PROFILE_CATALOG.json")

KERNEL_QUALIFICATION = {
    "grammar": GR.GRAMMAR_VERSION,
    "mutation_neutrality": "R4_NODE_COUNT_DRIFT_WITHIN_0.02_PER_STEP_NO_SELECTION (measured 2026-09-18, 3 seeds; "
                           "test_graph_grammar.py pins the band)",
    "mutation_current_source": "NOT_MEASURED (V0.5 detailed-balance instrument admitted as DETECTOR only, Harmonia #412; "
                               "no absence claim)",
    "operational_significance": "NOT_YET_ADJUDICATED",
    "permitted_use": "USE_A_FROZEN_SPECIMEN_SOURCE and selection-driven search CONDITIONAL on this kernel",
    "prohibited_use": "USE_B_NEUTRAL_EVOLUTIONARY_OPERATOR (no neutral-variation, drift or operator-independent claims)",
}


def regime_of(fm: dict) -> dict:
    r = {k: v for k, v in fm.items() if k not in ("seed", "n")}
    validate_foundry_manifest(dict(r, seed=0, n=0))
    return json.loads(canonical_json(r))


def build_graph_profile(fm: dict) -> dict:
    body = {
        "schema_version": PROFILE_SCHEMA,
        "substrate": "graph",
        "runtime_version": RUNTIME_VERSION,
        "regime": regime_of(fm),
        "runtime_hash": RUNTIME_HASH,
        "affordance_hash": A.AFFORDANCE_HASH,
        "grammar": grammar_identity(version=GR.GRAMMAR_VERSION, ghash=GR.GRAMMAR_HASH, names=GR.NAMES, weights=GR.WEIGHTS),
        "kernel_qualification": KERNEL_QUALIFICATION,
    }
    full = hash_obj(body)
    return {**body, "profile_id": ID_PREFIX + full[:ID_HEX], "profile_sha256": full,
            "archaeon_regime_id": None, "archaeon_regime_scheme": None,
            "note": "Archaeon's instr<lo>-<hi> rule is defined over v0 foundry manifests only; a graph regime has none"}


def verify_graph_profile(p: dict) -> None:
    body = {k: p[k] for k in ("schema_version", "substrate", "runtime_version", "regime", "runtime_hash",
                              "affordance_hash", "grammar", "kernel_qualification")}
    full = hash_obj(body)
    if p["profile_sha256"] != full or p["profile_id"] != ID_PREFIX + full[:ID_HEX]:
        raise ValueError("graph profile id does not recompute")
    validate_foundry_manifest(dict(p["regime"], seed=0, n=0))


def build_catalog() -> dict:
    rows = [{"name": "graph_default_v1", "ran_in": ["nothing yet: opened 2026-09-18, no world has run it"],
             **build_graph_profile(dict(DEFAULT_FOUNDRY_MANIFEST, seed=0, n=0))}]
    doc = {"schema_version": "proteus.foundry_profile_catalog.v1", "substrate": "graph", "currency": "2026-09-18",
           "runtime_hash": RUNTIME_HASH, "affordance_hash": A.AFFORDANCE_HASH,
           "grammar": grammar_identity(version=GR.GRAMMAR_VERSION, ghash=GR.GRAMMAR_HASH, names=GR.NAMES, weights=GR.WEIGHTS),
           "kernel_qualification": KERNEL_QUALIFICATION,
           "note": "Graph-substrate profiles. The v0 catalog proteus/eval/FOUNDRY_PROFILE_CATALOG.json is frozen for "
                   "Campaign 4 and unchanged; a graph profile cannot alias a v0 profile (different runtime_hash).",
           "profiles": rows}
    doc["catalog_id"] = hash_obj({k: v for k, v in doc.items() if k != "catalog_id"})
    return doc


def main() -> int:
    from proteus.workspace import assert_not_canonical
    assert_not_canonical("run graph profile catalog")
    doc = build_catalog()
    with open(CATALOG_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    print(CATALOG_PATH)
    for r in doc["profiles"]:
        print(" ", r["name"], r["profile_id"], "| runtime", r["runtime_hash"][:12], "| grammar", r["grammar"]["grammar_hash"][:12])
    return 0


if __name__ == "__main__":
    sys.exit(main())
