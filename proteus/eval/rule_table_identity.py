"""PR-ID identity for radius-3 CA rule tables, and the join to Herakles's derivation records.

THEO-REQ-003 / -005 (comms #241, #247) asked for a provenance-carrying composition and
table-level intervention "minted where organisms are minted, so that the child is a player with
lineage and not a producer-local string". The LIBRARY half exists and is Herakles's:
`herakles.evca.derive` (dbc41fd2f, 2026-09-16) returns an `evca_derived_rule_v1` record with the
child table, both parents, the operator and its parameters, a CONTENT-derived player id
(`evca:r3:<32 hex>`) and a ROUTE-derived derivation id. This module does not re-implement any of
that. It is the one piece that is Proteus's: the artifact IDENTITY under PR-ID
(`proteus.eval.identity`, one identity across families) and its join to Herakles's ids.

TWO CONTENT IDS, ONE BIJECTION. `evca:r3:<hex>` and PR-ID's `organism_ref` are both pure
functions of the canonical 32-hex table. Neither is minted; both are derived. `organism_ref`
exists so a rule-table player sits in the same identity space as every program and genome
Proteus has ever registered (cross-family collision is structurally impossible, PR-ID-c);
`evca:r3:` exists so Herakles's records need no Proteus import. The functions below convert in
both directions and a test asserts the round trip over the whole record.

WHAT THIS MODULE REFUSES TO DO. It does not verify that a child really is the operator applied
to its parents -- that is `herakles.evca.derive.verify_record`, the semantic owner's check, and
`verified_refs` calls it lazily so this module stays stdlib-only. It does not write a PEW row:
`fossil_players` is Mnemosyne's write path (T5). It does not force a rule table into
`proteus.lineage_record.v0`, whose required `resource_budget` (tick_budget, tape_words, n_regs,
out_cap) and `runtime_hash` are VM facts a rule table does not have; the derivation record IS the
lineage record for this family, and a cross-family descent record is backlog PROTEUS-26.

NOTHING HERE SCORES, SELECTS OR NAMES A RULE INTERESTING.
"""
from __future__ import annotations

from proteus.eval.identity import FAMILY_RULE_TABLE, artifact_manifest, organism_ref

#: The representation Herakles's records carry: 128 entries as 32 lowercase hex digits,
#: radius 3, entry index = neighbourhood pattern under herakles.evca.core's declared bit order.
REPR_EVCA_RULE_HEX_R3_V1 = "herakles.evca.rule_hex.r3.v1"
#: Semantic version: the evca core that interprets the table. Bumped by Herakles, never here.
SEM_EVCA_CORE_V1 = "herakles.evca.core.v1"
EVCA_PLAYER_PREFIX = "evca:r3:"
RECORD_KIND = "evca_derived_rule_v1"
TABLE_HEX_LEN = 32


class RuleTableIdentityError(ValueError):
    """Malformed table or record. Fails closed."""


def canonical_rule_hex(rule_hex):
    """Lowercase, no separators, exactly 32 hex digits. Same spelling Herakles canonicalises to."""
    if not isinstance(rule_hex, str):
        raise RuleTableIdentityError(f"rule_hex must be a string, got {type(rule_hex).__name__}")
    # the SAME normalisation as herakles.evca.core.decode_table: spaces and underscores dropped,
    # lowercased, nothing else (no 0x prefix), so the two owners never disagree on a spelling
    h = rule_hex.replace(" ", "").replace("_", "").lower()
    if len(h) != TABLE_HEX_LEN or any(c not in "0123456789abcdef" for c in h):
        raise RuleTableIdentityError(f"rule_hex must be {TABLE_HEX_LEN} hex digits, got {rule_hex!r}")
    return h


def rule_table_manifest(rule_hex, semantic_version=SEM_EVCA_CORE_V1, meta=None):
    """The PR-ID artifact manifest of a rule table. Body is the canonical hex and nothing else."""
    return artifact_manifest(FAMILY_RULE_TABLE, {"rule_hex": canonical_rule_hex(rule_hex)},
                             REPR_EVCA_RULE_HEX_R3_V1, semantic_version, meta=meta)


def organism_ref_of_rule(rule_hex, semantic_version=SEM_EVCA_CORE_V1):
    """sha256:<64 hex> -- PR-ID's WHAT-it-is for a rule table. Environment-free."""
    return organism_ref(rule_table_manifest(rule_hex, semantic_version))


def evca_player_id(rule_hex):
    """Herakles's content id for the same table. Pure; matches herakles.evca.derive.player_id."""
    return EVCA_PLAYER_PREFIX + canonical_rule_hex(rule_hex)


def rule_hex_of_evca_player(pid):
    if not isinstance(pid, str) or not pid.startswith(EVCA_PLAYER_PREFIX):
        raise RuleTableIdentityError(f"not an {EVCA_PLAYER_PREFIX}<hex> player id: {pid!r}")
    return canonical_rule_hex(pid[len(EVCA_PLAYER_PREFIX):])


def organism_ref_of_evca_player(pid, semantic_version=SEM_EVCA_CORE_V1):
    """The join: Herakles's id -> PR-ID ref. Total on well-formed ids; a bijection on tables."""
    return organism_ref_of_rule(rule_hex_of_evca_player(pid), semantic_version)


def refs_for_derivation(rec, semantic_version=SEM_EVCA_CORE_V1):
    """PR-ID refs for every table a Herakles derivation record names. STRUCTURAL only: it reads
    the record's ids and hexes and checks they agree with each other; it does not re-derive the
    child (see `verified_refs`)."""
    if not isinstance(rec, dict) or rec.get("kind") != RECORD_KIND:
        raise RuleTableIdentityError(f"not an {RECORD_KIND} record")
    for k in ("operator", "operator_params", "parents", "parent_rule_hexes", "child_rule_hex",
              "child_player_id", "derivation_id", "identity"):
        if k not in rec:
            raise RuleTableIdentityError(f"record lacks {k!r}")
    parents = list(rec["parents"])
    if not 1 <= len(parents) <= 2 or len(rec["parent_rule_hexes"]) != len(parents):
        raise RuleTableIdentityError("a derivation has one or two parents, listed twice over")
    for pid, h in zip(parents, rec["parent_rule_hexes"]):
        if rule_hex_of_evca_player(pid) != canonical_rule_hex(h):
            raise RuleTableIdentityError(f"parent id {pid} does not spell parent hex {h}")
    child_hex = canonical_rule_hex(rec["child_rule_hex"])
    if rule_hex_of_evca_player(rec["child_player_id"]) != child_hex:
        raise RuleTableIdentityError("child_player_id does not spell child_rule_hex")
    if bool(rec["identity"]) != (child_hex in [canonical_rule_hex(h) for h in rec["parent_rule_hexes"]]):
        raise RuleTableIdentityError("identity flag disagrees with the hexes")
    return {
        "schema_version": "proteus.rule_table_refs.v1",
        "representation_version": REPR_EVCA_RULE_HEX_R3_V1,
        "semantic_version": semantic_version,
        "child_organism_ref": organism_ref_of_rule(child_hex, semantic_version),
        "child_player_id": rec["child_player_id"],
        "parent_organism_refs": [organism_ref_of_rule(h, semantic_version)
                                 for h in rec["parent_rule_hexes"]],
        "parent_player_ids": parents,
        "operator": rec["operator"],
        "operator_params": rec["operator_params"],
        "derivation_id": rec["derivation_id"],
        "identity": bool(rec["identity"]),
        "verified_by_semantic_owner": False,
    }


def verified_refs(rec, semantic_version=SEM_EVCA_CORE_V1):
    """`refs_for_derivation` AFTER Herakles's own `verify_record` has re-derived the child.
    Imports herakles lazily; refuses (never guesses) if the library is absent."""
    try:
        from herakles.evca.derive import verify_record  # noqa: WPS433 (lazy on purpose)
    except ImportError as e:                            # pragma: no cover - environment-dependent
        raise RuleTableIdentityError("herakles.evca.derive is not importable here; the record "
                                     "cannot be verified and is NOT presented as verified") from e
    verify_record(rec)                                  # raises EvcaError on any mismatch
    out = refs_for_derivation(rec, semantic_version)
    out["verified_by_semantic_owner"] = True
    return out
