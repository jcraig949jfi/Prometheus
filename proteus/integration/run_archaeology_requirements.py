"""Emit the machine-readable Proteus-side archaeology requirements (pre-T1 hardening, task 10).

    python proteus/integration/run_archaeology_requirements.py

What a future external archaeologist -- someone with the repository and no living memory of this
programme -- must be able to recover, and what must therefore stay stable. Values are READ from
the live artifacts rather than transcribed, so this file cannot drift from what it describes.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry.affordances import AFFORDANCE_HASH  # noqa: E402
from proteus.foundry.grammar import GRAMMAR_HASH, GRAMMAR_VERSION  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH, canonical_json  # noqa: E402
from proteus.integration import registry as R  # noqa: E402

V0_6_PACKET_SHA = "a5b1a7a137022dbaad42894dc8fc289f580ab0fdb59b4ec3654354c3a5906f6d"
READINESS_PACKET_SHA = "5059f44ca83ca91f51773f8b18613cfcb19154ab88e545d32314f3e77379cbf5"


def build():
    reg = R.load_default()
    ids = R.enumerate_ids(reg)
    first = R.get_entry(reg, ids[0])
    return {
        "schema_version": "proteus.archaeology_requirements.v1",
        "generated_for": "Harmonia T1/T2 boundary probes and any later reconstruction",
        "principle": (
            "An archaeologist starting from a single evidence id must be able to reach a "
            "specimen and prove it unaltered, WITHOUT living memory, WITHOUT Proteus internals, "
            "and WITHOUT trusting any write echo. Harmonia's first integration demonstrated the "
            "path end to end; these are the Proteus-side obligations that keep it working."),

        "identities_an_archaeologist_must_recover": [
            {"id": "organism_id",
             "where": "registry entry / PEW fossil player / SFE blob_hash",
             "rule": "sha256 of canonical_json(manifest); the authoritative specimen identity",
             "recoverable_from": "the manifest alone, by re-hashing"},
            {"id": "entry_id", "where": "registry entry",
             "rule": "sha256 of the entry MINUS extrinsic and entry_id",
             "recoverable_from": "the entry, via registry.compute_entry_id"},
            {"id": "registry_id", "where": "registry root",
             "rule": "sha256 over {schema_version, build, [entry_id...]}",
             "recoverable_from": "the registry file"},
            {"id": "lineage_id", "where": "registry entry",
             "rule": "founder organism_id; equals organism_id at generation 0"},
            {"id": "generation_manifest_id", "where": "registry build block",
             "rule": "sha256 of the foundry manifest that produced the population"},
            {"id": "foundry_identity", "where": "registry build and provenance",
             "rule": "sha256 of {foundry_manifest, runtime_hash}"},
            {"id": "population_seed", "where": "registry build",
             "rule": "int(sha256(governing directive)[:16], 16); fixed before any specimen"},
            {"id": "encounter_id", "where": "consumer side",
             "rule": "proteus.foundry.export.encounter_identity(...) is authoritative"},
        ],

        "hashes_that_must_remain_stable": {
            "grammar_hash": GRAMMAR_HASH,
            "grammar_version": GRAMMAR_VERSION,
            "runtime_hash": RUNTIME_HASH,
            "affordance_hash": AFFORDANCE_HASH,
            "registry_id": reg["registry_id"],
            "registry_serialized_sha256":
                hashlib.sha256(canonical_json(reg).encode()).hexdigest(),
            "first_specimen_organism_id": ids[0],
            "first_specimen_entry_id": first["entry_id"],
            "v0_6_final_packet_sha256": V0_6_PACKET_SHA,
            "integration_readiness_packet_sha256": READINESS_PACKET_SHA,
            "stability_rule": (
                "These are published. A change to grammar/runtime/affordance hashes invalidates "
                "every specimen identity derived under them and REQUIRES a new registry version "
                "plus an explicit identity transition, never a silent refresh. Document hashes "
                "are over LF-normalised bytes; proteus/.gitattributes pins eol=lf so a checkout "
                "on any platform reproduces them."),
        },

        "source_qualification_fields_that_must_propagate": {
            "fields": sorted(R.source_qualification().keys()),
            "current_values": R.source_qualification(),
            "rule": (
                "This block travels inside every registry. A consumer must be able to learn the "
                "V0.6 limitation without archaeology. Dropping, flattening or summarising it "
                "downstream is a contract violation: mutation_neutrality is NOT_QUALIFIED and "
                "USE B remains prohibited."),
        },

        "determinism_and_quarantine_metadata_that_must_stay_queryable": [
            {"property": "manifest identity is file-independent",
             "query": "sha256(canonical_json(manifest)) == organism_id",
             "why": "CRLF or transport re-serialisation can never alter a specimen id",
             "verified_by": "proteus/tests/test_integration.py; Harmonia read-back 64/64"},
            {"property": "population rebuild is deterministic",
             "query": "python proteus/integration/run_determinism_check.py",
             "why": "registry_id and serialized sha256 must agree on CPython 3.11 and 3.12"},
            {"property": "replay contract excludes the nondeterministic path",
             "query": "pytest proteus/tests/test_pre_t1_gates.py -k replay_contract"},
            {"property": "known random defect stays inside its measured blast radius",
             "query": "pytest proteus/tests/test_pre_t1_gates.py -k blast_radius",
             "why": "the published bounded-blast-radius statement is only true while it holds"},
            {"property": "no forbidden imports package-wide",
             "query": "pytest proteus/tests/test_package_import_hygiene.py",
             "why": "quarantine.py itself covers proteus/foundry ONLY"},
            {"property": "protected surface carries zero import exemptions",
             "query": "pytest proteus/tests/test_pre_t1_gates.py -k protected_deterministic"},
            {"property": "audit stamp freshness",
             "query": "python proteus/audits/audit_identity.py verify",
             "why": "binds proteus/foundry/*.py + auditor + affordance table ONLY; it does NOT "
                    "cover proteus/integration, which is why the hygiene test exists"},
            {"property": "semantic quarantine",
             "query": "python proteus/audits/quarantine.py"},
            {"property": "no semantic taxonomy in the registry",
             "query": "pytest proteus/tests/test_integration.py -k no_semantic_taxonomy"},
            {"property": "extrinsic observation cannot alter identity",
             "query": "pytest proteus/tests/test_integration.py -k extrinsic_write"},
            {"property": "generated artifacts are not tracked",
             "query": "pytest proteus/tests/test_pre_t1_gates.py -k generated_artifacts"},
            {"property": "consumer document does not deny the registry",
             "query": "pytest proteus/tests/test_pre_t1_gates.py -k deny_the_registry"},
        ],

        "known_defects_carried_forward": [
            {"id": "D3", "file": "proteus/v0_6/equilibrium.py",
             "defect": "imports the stdlib random module, against Proteus policy",
             "blast_radius": ["empirical-occupancy cross-check (non-adjudicated)",
                              "matched-trajectory arm (non-adjudicated)"],
             "not_in": "the numerical replay contract",
             "status": "NOT FIXED BY DESIGN; fixing would alter two published numbers",
             "gate": "test_random_blast_radius_is_exactly_where_it_was_measured"},
        ],
    }


def main():
    out = build()
    p = os.path.join(HERE, "ARCHAEOLOGY_REQUIREMENTS.json")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(canonical_json(out))
        f.write("\n")
    q = out["source_qualification_fields_that_must_propagate"]["fields"]
    print(f"wrote {os.path.relpath(p, ROOT)}")
    print(f"  identities             {len(out['identities_an_archaeologist_must_recover'])}")
    print(f"  stable hashes          {len(out['hashes_that_must_remain_stable']) - 1}")
    print(f"  qualification fields   {len(q)}")
    print("  queryable properties   "
          f"{len(out['determinism_and_quarantine_metadata_that_must_stay_queryable'])}")
    print(f"  known defects carried  {len(out['known_defects_carried_forward'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
