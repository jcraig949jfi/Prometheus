"""The Player Registry: a canonical, machine-readable inventory of frozen specimens.

    THE REGISTRY DESCRIBES SPECIMENS. IT DOES NOT DEFINE PLAYER "TYPES."

There are no player families, no classes, no taxonomy and no quality score anywhere in this
module, and adding one would be a contract violation rather than a feature. A registry entry
makes an organism ADDRESSABLE -- it says what the organism IS structurally and where it came
from, never what it is FOR. What any specimen is good for is for the arena to discover.

INTRINSIC VERSUS EXTRINSIC (integration directive section 4)
------------------------------------------------------------
Two kinds of fact about an organism are kept mechanically separate, not merely by convention:

    INTRINSIC   genome, manifest, runtime identity, lineage, immutable provenance.
                Fixed at generation. Determines organism_id and entry_id.

    EXTRINSIC   world behaviour, encounters, phenotype, scores, failures, novelty,
                discovered capabilities. Owned by Harmonia/Mnemosyne, NOT by Proteus.

`entry_id` is computed over the intrinsic part ONLY. An extrinsic observation therefore cannot
alter an organism's identity even if a consumer writes one into the entry, and a test asserts
exactly that. `phenotype` defaults to the string UNKNOWN and Proteus never writes any other
value: "no presently demonstrated use" is not "garbage", and the registry deliberately has no
generate -> score -> classify -> delete lifecycle.

SOURCE OF TRUTH
---------------
Manifest validity is decided by `proteus.foundry.vm.validate_manifest` and by nothing here.
This module records the validator's verdict; it never re-implements the rules, so there is no
second source of truth to drift.

FAIL CLOSED
-----------
Validation raises `RegistryError` on: a schema version it does not know, a missing required
field, an unknown field in any closed object, an organism_id that does not equal the hash of its
own manifest, or an entry whose recomputed entry_id disagrees with the stored one. Unknown fields
are handled DELIBERATELY: closed objects reject them by name, and exactly one object
(`extrinsic`) is an open namespace, declared as such.
"""
from __future__ import annotations

import json
import os

from proteus.foundry.affordances import AFFORDANCE_HASH
from proteus.foundry.grammar import GRAMMAR_HASH, GRAMMAR_VERSION
from proteus.foundry.identity import RUNTIME_HASH, canonical_json, hash_obj
from proteus.foundry.vm import SCHEMA as MANIFEST_SCHEMA
from proteus.foundry.vm import ManifestError, validate_manifest

REGISTRY_SCHEMA = "proteus.player_registry.v1"
ENTRY_SCHEMA = "proteus.player_registry_entry.v1"

#: The one object in an entry that accepts arbitrary consumer-supplied keys. Everything else is
#: closed and rejects unknown fields by name.
OPEN_NAMESPACES = ("extrinsic",)

ENTRY_REQUIRED = ("schema_version", "organism_id", "lineage_id", "generation", "manifest",
                  "identity", "provenance", "resource_envelope", "validation", "extrinsic",
                  "entry_id")
IDENTITY_REQUIRED = ("manifest_schema_version", "runtime_hash", "grammar_hash",
                     "affordance_hash", "grammar_version")
PROVENANCE_REQUIRED = ("source", "foundry_identity", "population_seed", "index_in_population",
                       "derivation", "generation_manifest_id")
ENVELOPE_REQUIRED = ("n_regs", "tape_words", "genome_words", "genome_instructions",
                     "code_writable", "persist", "tick_budget", "out_cap",
                     "max_state_footprint_words", "persistent_state_words", "max_ops_per_tick",
                     "max_output_values_per_channel_per_tick")
VALIDATION_REQUIRED = ("manifest_valid", "validator", "error")

REGISTRY_REQUIRED = ("schema_version", "registry_id", "source_qualification", "build",
                     "entries")


class RegistryError(ValueError):
    """Any registry contract violation. Always raised; never warned."""


# ------------------------------------------------------------------ qualification

def source_qualification() -> dict:
    """What a consumer must know about where these specimens come from, without reading V0.6.

    Integration directive section 7: a downstream consumer must not need archaeological
    knowledge of V0.6 to know the limitation. This travels with every registry.
    """
    return {
        "deterministic_generation": "QUALIFIED",
        "semantic_quarantine": "QUALIFIED",
        "mutation_neutrality": "NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT",
        "mutation_current_source": "FULL_SPACE_CURRENT_SOURCE_UNRESOLVED",
        "operational_significance": "NOT_YET_ADJUDICATED",
        "permitted_use": "USE_A_FROZEN_SPECIMEN_SOURCE",
        "prohibited_use": "USE_B_NEUTRAL_EVOLUTIONARY_OPERATOR",
        "plain_statement": (
            "These specimens were generated deterministically and are safe to enumerate, "
            "instantiate, run, checkpoint and replay. The MUTATION machinery that would breed "
            "them is measurably NOT reversible: it carries an authored probability current "
            "(entropy production 1.4e-02 nats/step, 11.3% of two-way flux is net imbalance, "
            "reproduced across two independent measurements). Do NOT interpret any population "
            "produced by mutation as unbiased evolution, and do NOT assume structural states "
            "are sampled neutrally. Whether that current matters in practice is NOT YET "
            "ADJUDICATED."),
        "evidence": "roles/Proteus/PROTEUS_V0_6_FINAL_EXTERNAL_REVIEW_PACKET.txt",
    }


# ------------------------------------------------------------------ entry construction

def resource_envelope(manifest: dict) -> dict:
    """Bounds a scheduler needs BEFORE running a player. Structural facts only, never a score.

    Every number here is a hard bound read off the manifest, not an estimate and not a ranking.
    """
    p = manifest["persist"]
    persistent = ((manifest["tape_words"] if p in ("tape", "all") else 0)
                  + (manifest["n_regs"] if p in ("regs", "all") else 0))
    return {
        "n_regs": manifest["n_regs"],
        "tape_words": manifest["tape_words"],
        "genome_words": len(manifest["genome"]),
        "genome_instructions": len(manifest["genome"]) // 4,
        "code_writable": manifest["code_writable"],
        "persist": p,
        "tick_budget": manifest["tick_budget"],
        "out_cap": manifest["out_cap"],
        "max_state_footprint_words": manifest["tape_words"] + manifest["n_regs"],
        "persistent_state_words": persistent,
        "max_ops_per_tick": manifest["tick_budget"],
        "max_output_values_per_channel_per_tick": manifest["out_cap"],
    }


def intrinsic_view(entry: dict) -> dict:
    """The part of an entry that determines identity: everything except extrinsic and entry_id."""
    return {k: v for k, v in entry.items() if k not in ("extrinsic", "entry_id")}


def compute_entry_id(entry: dict) -> str:
    return hash_obj(intrinsic_view(entry))


def build_entry(organism: dict, provenance: dict) -> dict:
    """One registry entry for one organism record from proteus.foundry.generate.

    The manifest is embedded verbatim. organism_id is NOT recomputed here -- it is checked
    against the authoritative rule (sha256 of the canonical manifest) and a mismatch raises.
    """
    manifest = organism["manifest"]
    try:
        validate_manifest(manifest)
        valid, err = True, None
    except ManifestError as e:
        valid, err = False, str(e)
    if hash_obj(manifest) != organism["organism_id"]:
        raise RegistryError("organism_id is not the hash of its manifest")
    entry = {
        "schema_version": ENTRY_SCHEMA,
        "organism_id": organism["organism_id"],
        "lineage_id": organism["lineage_id"],
        "generation": organism["generation"],
        "manifest": manifest,
        "identity": {
            "manifest_schema_version": MANIFEST_SCHEMA,
            "runtime_hash": organism["runtime_hash"],
            "grammar_hash": GRAMMAR_HASH,
            "grammar_version": GRAMMAR_VERSION,
            "affordance_hash": AFFORDANCE_HASH,
        },
        "provenance": dict(provenance),
        "resource_envelope": resource_envelope(manifest),
        "validation": {"manifest_valid": valid,
                       "validator": "proteus.foundry.vm.validate_manifest",
                       "error": err},
        # EXTRINSIC: owned by the consumer, never by Proteus, never part of identity.
        "extrinsic": {
            "phenotype": "UNKNOWN",
            "owner": "not Proteus; Harmonia/Mnemosyne may attach observations here",
            "note": ("UNKNOWN is a permanent, legitimate state. It records that no observation "
                     "has been made, and must not be read as a negative judgement. Nothing "
                     "written into this object changes organism_id or entry_id."),
        },
    }
    entry["entry_id"] = compute_entry_id(entry)
    return entry


def build_registry(entries: list, build: dict) -> dict:
    reg = {
        "schema_version": REGISTRY_SCHEMA,
        "source_qualification": source_qualification(),
        "build": dict(build),
        "entries": list(entries),
    }
    reg["registry_id"] = hash_obj({"schema_version": reg["schema_version"],
                                   "build": reg["build"],
                                   "entry_ids": [e["entry_id"] for e in reg["entries"]]})
    return reg


# ------------------------------------------------------------------ validation, fail closed

def _closed(obj, required, where):
    if not isinstance(obj, dict):
        raise RegistryError(f"{where} must be an object")
    missing = [k for k in required if k not in obj]
    if missing:
        raise RegistryError(f"{where} missing required field(s): {sorted(missing)}")
    unknown = [k for k in obj if k not in required]
    if unknown:
        raise RegistryError(f"{where} has unknown field(s): {sorted(unknown)} "
                            f"(this object is CLOSED; only 'extrinsic' accepts new keys)")


def validate_entry(entry: dict) -> None:
    _closed(entry, ENTRY_REQUIRED, "entry")
    if entry["schema_version"] != ENTRY_SCHEMA:
        raise RegistryError(f"unknown entry schema_version {entry['schema_version']!r}; "
                            f"this build understands {ENTRY_SCHEMA!r}")
    _closed(entry["identity"], IDENTITY_REQUIRED, "entry.identity")
    _closed(entry["provenance"], PROVENANCE_REQUIRED, "entry.provenance")
    _closed(entry["resource_envelope"], ENVELOPE_REQUIRED, "entry.resource_envelope")
    _closed(entry["validation"], VALIDATION_REQUIRED, "entry.validation")
    if not isinstance(entry["extrinsic"], dict):
        raise RegistryError("entry.extrinsic must be an object (it is the one OPEN namespace)")
    # authoritative manifest check, delegated -- never re-implemented here
    validate_manifest(entry["manifest"])
    if hash_obj(entry["manifest"]) != entry["organism_id"]:
        raise RegistryError("organism_id does not equal sha256 of the canonical manifest")
    if compute_entry_id(entry) != entry["entry_id"]:
        raise RegistryError("entry_id does not match the entry's intrinsic content")
    env = resource_envelope(entry["manifest"])
    if env != entry["resource_envelope"]:
        raise RegistryError("resource_envelope disagrees with the manifest it describes")


def validate_registry(reg: dict) -> None:
    _closed(reg, REGISTRY_REQUIRED, "registry")
    if reg["schema_version"] != REGISTRY_SCHEMA:
        raise RegistryError(f"unknown registry schema_version {reg['schema_version']!r}; "
                            f"this build understands {REGISTRY_SCHEMA!r}")
    if not isinstance(reg["entries"], list):
        raise RegistryError("registry.entries must be a list")
    seen = set()
    for e in reg["entries"]:
        validate_entry(e)
        if e["organism_id"] in seen:
            raise RegistryError(f"duplicate organism_id {e['organism_id'][:16]}")
        seen.add(e["organism_id"])
    expect = hash_obj({"schema_version": reg["schema_version"], "build": reg["build"],
                       "entry_ids": [e["entry_id"] for e in reg["entries"]]})
    if expect != reg["registry_id"]:
        raise RegistryError("registry_id does not match its entries")


# ------------------------------------------------------------------ IO and lookup

def save(reg: dict, path: str) -> str:
    validate_registry(reg)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(canonical_json(reg))
        f.write("\n")
    return reg["registry_id"]


def default_path() -> str:
    """Where the committed starter registry lives, so a consumer never hardcodes a path."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "PLAYER_REGISTRY.json")


def load_default() -> dict:
    """Operation A, the one-liner: the committed frozen starter menagerie, validated."""
    return load(default_path())


def load(path: str) -> dict:
    if not os.path.exists(path):
        raise RegistryError(f"no registry at {path}")
    with open(path, encoding="utf-8") as f:
        reg = json.load(f)
    validate_registry(reg)
    return reg


def enumerate_ids(reg: dict) -> list:
    """Operation A: every addressable specimen, in registry order."""
    return [e["organism_id"] for e in reg["entries"]]


def get_entry(reg: dict, organism_id: str) -> dict:
    """Operation J: the whole entry, including provenance and identity."""
    for e in reg["entries"]:
        if e["organism_id"] == organism_id:
            return e
    raise RegistryError(f"unknown organism_id {organism_id!r}")


def get_manifest(reg: dict, organism_id: str) -> dict:
    """Operation B: the immutable player itself."""
    return get_entry(reg, organism_id)["manifest"]


def get_resource_envelope(reg: dict, organism_id: str) -> dict:
    """Operation K: hard bounds, before you schedule anything."""
    return get_entry(reg, organism_id)["resource_envelope"]
