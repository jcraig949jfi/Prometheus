"""Exports toward SFE and PEW. One direction only: nothing here is ever read by a player.

SFE payloads (contracts/SFE_INTEGRATION.md): a population is stored as content-addressed
artifacts with info_kind "artifact"; encounters are the operator's committed experiments; this
module only SHAPES the payloads, it never talks to the Engine (no client, no token, no network
import -- the quarantine audit enforces that for the whole package).

PEW records (contracts/PEW_EXPORT.md): JSONL rows keyed by immutable identities so that the
Evidence Wiki can later attach interpretation to organisms, lineages, classes and encounters
without any of it flowing back.
"""
from __future__ import annotations

import base64
import json

from .identity import RUNTIME_HASH, canonical_json, hash_obj
from .grammar import GRAMMAR_HASH
from .affordances import AFFORDANCE_HASH


def sfe_artifact_payload(organism: dict) -> dict:
    """Shape for POST /v2/worlds/{wid}/artifacts. The operator supplies the world."""
    blob = canonical_json(organism["manifest"]).encode("utf-8")
    return {
        "name": f"proteus:{organism['organism_id'][:16]}",
        "data_b64": base64.b64encode(blob).decode("ascii"),
        "meta": {
            "info_kind": "artifact",
            "proteus": {
                "organism_id": organism["organism_id"],
                "lineage_id": organism["lineage_id"],
                "generation": organism["generation"],
                "runtime_hash": organism["runtime_hash"],
                "manifest_schema": organism["manifest"]["schema_version"],
            },
        },
    }


def encounter_identity(organism_ids: list, world_binding_id: str, seed: int, checkpoint_ids: list | None) -> str:
    """The id SFE-side observations bind to (A9). Proteus mints nothing else about an encounter."""
    return hash_obj({"organisms": sorted(organism_ids), "world_binding": world_binding_id,
                     "seed": seed, "checkpoints": sorted(checkpoint_ids or []),
                     "runtime_hash": RUNTIME_HASH})


def pew_rows(organisms: list, lineage_records: list, signature_rows: list | None = None,
             degeneracy: list | None = None, packet_ref: str | None = None, git_commit: str | None = None):
    """Yield PEW-bound JSONL rows. Statuses are for Mnemosyne's client; content is identity-keyed."""
    prov = {"runtime_hash": RUNTIME_HASH, "grammar_hash": GRAMMAR_HASH, "affordance_hash": AFFORDANCE_HASH,
            "packet_ref": packet_ref, "git_commit": git_commit}
    for o in organisms:
        yield {"kind": "proteus.organism", "organism_id": o["organism_id"], "lineage_id": o["lineage_id"],
               "generation": o["generation"], "manifest_hash": o["organism_id"],
               "genome_instr": len(o["manifest"]["genome"]) // 4,
               "bounds": {k: o["manifest"][k] for k in ("n_regs", "tape_words", "tick_budget", "out_cap")},
               "code_writable": o["manifest"]["code_writable"], "persist": o["manifest"]["persist"],
               "provenance": prov}
    for r in lineage_records:
        yield {"kind": "proteus.descent", "record_id": r["record_id"], "organism_id": r["organism_id"],
               "parent_ids": r["parent_ids"], "operators": [op["operator"] for op in r["operators"]],
               "mutation_seed": r["mutation_seed"], "provenance": prov}
    for s in signature_rows or []:
        yield {"kind": "proteus.signature", "organism_id": s["organism_id"],
               "transcript_class": s["transcript_class"], "knockout_vector": s["knockout_vector"],
               "resources": s.get("resources"), "provenance": prov}
    for d in degeneracy or []:
        yield {"kind": "proteus.transcript_class", "class_id": d["class_id"], "n_genomes": d["n_genomes"],
               "n_lineages": d["n_lineages"], "parent_child_pairs": d["parent_child_pairs_within_class"],
               "knockout_vector_distribution": d["knockout_vector_distribution"], "provenance": prov}


def write_jsonl(path: str, rows) -> int:
    n = 0
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
            n += 1
    return n
