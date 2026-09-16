"""MINTING derived CA rule tables as Proteus organisms (Archaeon ruling #268, 2026-09-16).

The ruling: "Minting a derived CA mechanism with parent provenance is PROTEUS's; the composition
operator's SEMANTICS are HERAKLES's." Herakles's `herakles.evca.derive` produces the child and
the derivation record; `proteus.eval.rule_table_identity` gives it PR-ID identity; THIS module
turns a verified derivation into a MINT RECORD and appends it to an append-only ledger. The mint
record is what a PEW `fossil_players` row needs (player_id, genome_hash = organism_ref,
parent_player, mutation_ref) and what Theophrastus's stencil needs to label a cell MINTED.

WHAT A MINT IS. A statement, by the organism-side seat, that a specific table entered the
population by a specific route from specific parents, verified by the semantic owner. It is NOT
a claim that the table is interesting, viable or novel. Two routes to one table are two mints
with one player_id and two mutation_refs; the ledger keeps both, and a reader who wants "the"
player joins on player_id.

WHAT A MINT REFUSES. An unverified record (Herakles's `verify_record` must have re-derived the
child; `require_verified=False` exists only for tests and is written into the record). An
IDENTITY child (child == a parent): there is nothing to mint, and minting it would present a
parent as its own offspring. A malformed record.

THE LEDGER (R5, immutable experience). `proteus/mint/RULE_TABLE_MINTS.jsonl`, one canonical
JSON record per line, each carrying `prev_mint_id` so the file is a hash chain: an edit or a
deletion anywhere breaks every later `mint_id`. Appending the same mint twice is refused
(idempotent by mint_id); nothing is ever rewritten. `verify_ledger` walks the chain.

WHAT THIS DOES NOT DO. Write a PEW row (Mnemosyne's write path; the prompt naming the columns
is roles/Proteus/prompts/2026-09-16_replies/PROMPT_MNEMOSYNE_fossil_players_rule_tables.md).
Touch the frozen USE_A registry (`proteus/integration/PLAYER_REGISTRY.json`), which stays
byte-identical. Score, select, or rank anything.
"""
from __future__ import annotations

import os

from proteus.eval import rule_table_identity as RI
from proteus.foundry.identity import canonical_json, sha256_hex

MINT_SCHEMA = "proteus.rule_table_mint.v1"
MINTER = "Proteus"
GENESIS_PREV = "sha256:" + "0" * 64
DEFAULT_LEDGER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "mint", "RULE_TABLE_MINTS.jsonl")


class MintRefused(ValueError):
    """The derivation cannot be minted. The reason is the message; nothing is written."""


def mint(record, semantic_version=RI.SEM_EVCA_CORE_V1, require_verified=True, prev_mint_id=None):
    """Build a mint record from a Herakles derivation record. Pure; writes nothing.

    `prev_mint_id` chains the record into a ledger; `append_mint` fills it in. A record built
    with one prev and appended after another would break the chain, and `append_mint` rebuilds
    the id rather than trusting the caller's.
    """
    if require_verified:
        refs = RI.verified_refs(record, semantic_version)      # raises on any mismatch
    else:
        refs = RI.refs_for_derivation(record, semantic_version)
    if refs["identity"]:
        raise MintRefused("child equals a parent (identity derivation); nothing to mint, and a "
                          "parent must never be presented as its own offspring")
    parents = [{"player_id": pid, "organism_ref": ref}
               for pid, ref in zip(refs["parent_player_ids"], refs["parent_organism_refs"])]
    body = {
        "schema_version": MINT_SCHEMA,
        "minter": MINTER,
        "family": "rule_table",
        "representation_version": refs["representation_version"],
        "semantic_version": refs["semantic_version"],
        "player_id": refs["child_player_id"],
        "organism_ref": refs["child_organism_ref"],
        "rule_hex": RI.rule_hex_of_evca_player(refs["child_player_id"]),
        "parents": parents,
        "parent_player": parents[0]["player_id"],
        "mate_player": parents[1]["player_id"] if len(parents) == 2 else None,
        "mutation_ref": refs["derivation_id"],
        "operator": refs["operator"],
        "operator_params": refs["operator_params"],
        "verified_by_semantic_owner": bool(refs["verified_by_semantic_owner"]),
        "prev_mint_id": prev_mint_id or GENESIS_PREV,
    }
    body["mint_id"] = _mint_id(body)
    return body


def _mint_id(body):
    doc = {k: v for k, v in body.items() if k != "mint_id"}
    return "sha256:" + sha256_hex(canonical_json(doc))


def read_ledger(path=DEFAULT_LEDGER):
    if not os.path.exists(path):
        return []
    import json
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def verify_ledger(path=DEFAULT_LEDGER):
    """Walk the chain. Returns (ok, n_rows, first_bad_index_or_None)."""
    rows = read_ledger(path)
    prev = GENESIS_PREV
    for i, row in enumerate(rows):
        if row.get("prev_mint_id") != prev or _mint_id(row) != row.get("mint_id"):
            return False, len(rows), i
        prev = row["mint_id"]
    return True, len(rows), None


def append_mint(record, path=DEFAULT_LEDGER, semantic_version=RI.SEM_EVCA_CORE_V1,
                require_verified=True):
    """Mint and append, chaining onto the ledger's last row. Refuses a duplicate mint_id and
    refuses to touch a ledger whose chain does not verify. Returns the appended record."""
    ok, n, bad = verify_ledger(path)
    if not ok:
        raise MintRefused(f"ledger {path} does not verify at row {bad}; nothing appended")
    rows = read_ledger(path)
    prev = rows[-1]["mint_id"] if rows else GENESIS_PREV
    rec = mint(record, semantic_version, require_verified, prev_mint_id=prev)
    # a duplicate is the same (player_id, mutation_ref) reaching the ledger twice; its mint_id
    # would differ only by prev, so the check is on the pair, not the id
    for row in rows:
        if row["player_id"] == rec["player_id"] and row["mutation_ref"] == rec["mutation_ref"]:
            raise MintRefused(f"already minted: {rec['player_id']} via {rec['mutation_ref']} "
                              f"(mint {row['mint_id']})")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(canonical_json(rec) + "\n")
        f.flush()
    return rec
