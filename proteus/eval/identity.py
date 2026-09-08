"""PR-ID (D-7) -- one artifact identity across families: programs, rule tables, genomes.

`organism_ref` generalises the existing Proteus rule `organism_id = sha256(canonical manifest)`
so that a CA rule table and a population genome can sit beside a program in the retention archive
and in PEW `fossil_players`, under one convention.

----------------------------------------------------------------------------------------------
THE COMPATIBILITY DECISION, AND WHY IT IS NOT A FUDGE
----------------------------------------------------------------------------------------------
For family `program` at representation `proteus.player_manifest.v0`, `organism_ref` is EXACTLY
`"sha256:" + sha256(canonical_json(manifest))` -- the legacy rule, unchanged.

That is deliberate. Sixty-four specimens are already fossilised under it, and the SFE seam holds
because `blob_hash == "sha256:" + organism_id`. Minting a second identity for the same artifact
would have made every existing fossil ambiguous, which is a far worse defect than a slightly
irregular encoding rule.

Every OTHER family is wrapped:

    {"family", "representation_version", "semantic_version", "body"}

CROSS-FAMILY COLLISION IS STRUCTURALLY IMPOSSIBLE, not merely unlikely (PR-ID-c). A validated
player manifest has exactly the eight keys the schema requires; a wrapped artifact has exactly
the four keys above. Canonical JSON sorts and emits keys, so the two byte strings can never be
equal, and a rule table whose `body` happens to BE a player manifest still hashes differently.
There is a test that constructs exactly that adversarial case.

----------------------------------------------------------------------------------------------
THREE REFERENCES, KEPT SEPARATE ON PURPOSE
----------------------------------------------------------------------------------------------
    organism_ref     WHAT the artifact is. Bytes plus declared semantics. Carries NO evaluation
                     environment. Stable across worlds, machines and runs.
    evaluation_ref   HOW it was executed: organism_ref + runtime/affordance/library versions +
                     spec + seed + budget + policy. This is the REPLAYABLE identity.
    observation_ref  WHERE a particular observation happened: evaluation_ref + a world binding.

This separation is the point of D-7, and it encodes something Proteus measured rather than
assumed: `organism_ref` pins BYTES, not EXECUTION. A 25 -> 26 opcode-table amendment re-decoded
94.87% of instructions with `organism_id` UNCHANGED. So an artifact reference alone is not
sufficient to reproduce behaviour -- `evaluation_ref` is. Anyone treating a matching
`organism_ref` as proof of identical behaviour has made an error this module exists to prevent.

NONE OF THESE IS A BEHAVIOUR-EQUIVALENCE CLAIM. Equal `organism_ref` means equal bytes under
equal declared semantics. It does not mean equal behaviour, and equal behaviour does not imply
equal `organism_ref`.

----------------------------------------------------------------------------------------------
IDENTITY-BEARING METADATA, DECLARED
----------------------------------------------------------------------------------------------
HASHED:      family, representation_version, semantic_version, body
NOT HASHED:  label, notes, provenance, timestamps, discovery history, any observation, any score

ALIASES ARE NOT NORMALISED AWAY FOR PROGRAMS, and the reason is measured. `op = word mod
N_OPCODES`, so `w` and `w + N_OPCODES` are instruction-identical -- but the genome is copied into
the tape, so they are DIFFERENT DATA. Normalising them would merge artifacts that can behave
differently. Aliases are excluded only where semantics permit, and here they do not.
"""
from __future__ import annotations

from proteus.foundry.identity import canonical_json, sha256_hex
from proteus.foundry.vm import SCHEMA as PLAYER_MANIFEST_SCHEMA
from proteus.foundry.vm import ManifestError, validate_manifest

ARTIFACT_SCHEMA = "proteus.artifact_manifest.v1"

FAMILY_PROGRAM = "program"
FAMILY_RULE_TABLE = "rule_table"
FAMILY_GENOME = "genome"
FAMILIES = (FAMILY_PROGRAM, FAMILY_RULE_TABLE, FAMILY_GENOME)

#: The one representation that reduces to the legacy organism_id rule.
REPR_PLAYER_MANIFEST_V0 = PLAYER_MANIFEST_SCHEMA          # "proteus.player_manifest.v0"

IDENTITY_BEARING = ("family", "representation_version", "semantic_version", "body")
NOT_IDENTITY_BEARING = ("label", "notes", "provenance", "created", "observations", "score",
                        "phenotype", "descriptor")


class IdentityError(ValueError):
    """Malformed artifact manifest. Fails closed."""


def artifact_manifest(family, body, representation_version, semantic_version, meta=None):
    """Build a canonical artifact manifest. Non-identity metadata is carried but never hashed.

    `meta` is an explicit DICT rather than **kwargs. With **kwargs the four identity-bearing
    names are also the four positional parameter names, so Python would raise TypeError before
    the guard below could ever run -- the guard was unreachable, i.e. dead defensive code that
    looked like protection. As a dict the guard is reachable and actually enforces the rule.
    """
    if family not in FAMILIES:
        raise IdentityError(f"unknown family {family!r}; known: {list(FAMILIES)}")
    if not isinstance(representation_version, str) or not representation_version:
        raise IdentityError("representation_version must be a non-empty string")
    if not isinstance(semantic_version, str) or not semantic_version:
        raise IdentityError("semantic_version must be a non-empty string")
    if body is None:
        raise IdentityError("body is required")
    if family == FAMILY_PROGRAM and representation_version == REPR_PLAYER_MANIFEST_V0:
        try:
            validate_manifest(body)
        except ManifestError as e:
            raise IdentityError(f"program body is not a valid player manifest: {e}") from e
    if meta is not None:
        if not isinstance(meta, dict):
            raise IdentityError("meta must be a dict of non-identity-bearing fields")
        for k in meta:
            if k in IDENTITY_BEARING:
                raise IdentityError(
                    f"{k!r} is identity-bearing and cannot be smuggled in as metadata")
    man = {"schema_version": ARTIFACT_SCHEMA, "family": family,
           "representation_version": representation_version,
           "semantic_version": semantic_version, "body": body}
    if meta:
        man["meta"] = dict(meta)
    return man


def hashed_document(manifest):
    """EXACTLY the bytes that determine identity. Everything else is excluded here."""
    _check(manifest)
    if (manifest["family"] == FAMILY_PROGRAM
            and manifest["representation_version"] == REPR_PLAYER_MANIFEST_V0):
        # legacy-compatible: the player manifest itself, nothing wrapped around it
        return manifest["body"]
    return {k: manifest[k] for k in IDENTITY_BEARING}


def organism_ref(manifest):
    """WHAT the artifact is. Environment-free. Not a behaviour claim."""
    return "sha256:" + sha256_hex(canonical_json(hashed_document(manifest)))


def legacy_organism_id(manifest):
    """The bare hex organism_id for program artifacts, for continuity with existing fossils."""
    if (manifest["family"] != FAMILY_PROGRAM
            or manifest["representation_version"] != REPR_PLAYER_MANIFEST_V0):
        raise IdentityError("legacy organism_id is defined only for player-manifest programs")
    return organism_ref(manifest).split(":", 1)[1]


def evaluation_ref(org_ref, runtime_hash, affordance_hash, library_version,
                   spec_id, seed, step_budget, budget_policy):
    """HOW it was executed. The REPLAYABLE identity; organism_ref alone is not."""
    return "sha256:" + sha256_hex(canonical_json({
        "organism_ref": org_ref, "runtime_hash": runtime_hash,
        "affordance_hash": affordance_hash, "library_version": library_version,
        "spec_id": spec_id, "seed": seed, "step_budget": step_budget,
        "budget_policy": budget_policy}))


def observation_ref(eval_ref, world_binding_id, occurrence=None):
    """WHERE an observation happened. Same artifact in two worlds -> two observation refs."""
    doc = {"evaluation_ref": eval_ref, "world_binding_id": world_binding_id}
    if occurrence is not None:
        doc["occurrence"] = occurrence
    return "sha256:" + sha256_hex(canonical_json(doc))


def _check(manifest):
    if not isinstance(manifest, dict):
        raise IdentityError("artifact manifest must be an object")
    if manifest.get("schema_version") != ARTIFACT_SCHEMA:
        raise IdentityError(f"expected schema_version {ARTIFACT_SCHEMA!r}")
    missing = [k for k in IDENTITY_BEARING if k not in manifest]
    if missing:
        raise IdentityError(f"missing identity-bearing field(s): {missing}")
    if manifest["family"] not in FAMILIES:
        raise IdentityError(f"unknown family {manifest['family']!r}")
    unknown = set(manifest) - set(IDENTITY_BEARING) - {"schema_version", "meta"}
    if unknown:
        raise IdentityError(f"unknown top-level field(s): {sorted(unknown)}")
