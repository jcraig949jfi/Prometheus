"""Minting derived rule tables (Archaeon ruling #268): the mint record, its refusals, the
append-only hash-chained ledger.

Controls: POSITIVE (a verified crossover mints; two routes to one child are two mints with one
player_id), NEGATIVE (an identity child is refused; a duplicate append is refused; the frozen
USE_A registry is untouched), CHEAT (a forged record cannot be minted under require_verified;
an edited ledger row breaks every later mint_id and further appends are refused).
"""
from __future__ import annotations

import json
import os

import pytest

from proteus.eval import rule_table_identity as RI
from proteus.eval import rule_table_mint as M

herakles_derive = pytest.importorskip("herakles.evca.derive")

A = "005f005f005f005f005fff5f005fff5f"
B = "0123456789abcdef0123456789abcdef"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTRY = os.path.join(ROOT, "proteus", "integration", "PLAYER_REGISTRY.json")


def _crossover():
    return herakles_derive.derive_crossover(A, B, herakles_derive.crossover_mask_one_point(64))


def _flip(hex_, idx):
    """An edit that CHANGES entry idx (an edit to the current value is an identity derivation)."""
    cur = int(herakles_derive.decode_table(hex_)[idx])
    return herakles_derive.derive_edit(hex_, [(idx, 1 - cur)])


def test_positive_verified_crossover_mints_with_both_parents_and_the_route():
    rec = M.mint(_crossover())
    assert rec["schema_version"] == M.MINT_SCHEMA and rec["minter"] == "Proteus"
    assert rec["player_id"] == RI.evca_player_id(rec["rule_hex"])
    assert rec["organism_ref"] == RI.organism_ref_of_rule(rec["rule_hex"])
    assert rec["parent_player"] == RI.evca_player_id(A) and rec["mate_player"] == RI.evca_player_id(B)
    assert rec["mutation_ref"].startswith("sha256:") and rec["operator"] == "crossover_mask"
    assert rec["verified_by_semantic_owner"] is True
    assert rec["prev_mint_id"] == M.GENESIS_PREV
    assert rec["mint_id"] == M._mint_id(rec)


def test_negative_identity_child_is_refused():
    cur = herakles_derive.decode_table(A)[0]
    rec = herakles_derive.derive_edit(A, [(0, int(cur))])
    with pytest.raises(M.MintRefused):
        M.mint(rec)


def test_cheat_forged_record_cannot_be_minted_verified():
    rec = herakles_derive.derive_edit(A, [(5, 1)])
    forged = dict(rec)
    forged["child_rule_hex"] = B
    forged["child_player_id"] = RI.evca_player_id(B)
    forged["identity"] = False
    with pytest.raises(Exception):
        M.mint(forged)                                   # verify_record refuses
    unverified = M.mint(forged, require_verified=False)  # the escape hatch says so on its face
    assert unverified["verified_by_semantic_owner"] is False


def test_ledger_chains_refuses_duplicates_and_keeps_two_routes(tmp_path):
    path = str(tmp_path / "L.jsonl")
    r1 = M.append_mint(_crossover(), path)
    edits = [(3, 1), (77, 0)]
    e1 = herakles_derive.derive_edit(A, edits)
    mid = herakles_derive.derive_edit(A, [edits[0]])
    e2 = herakles_derive.derive_edit(mid["child_rule_hex"], [edits[1]])
    r2 = M.append_mint(e1, path)
    r3 = M.append_mint(e2, path)
    assert r2["player_id"] == r3["player_id"] and r2["mutation_ref"] != r3["mutation_ref"]
    assert r2["prev_mint_id"] == r1["mint_id"] and r3["prev_mint_id"] == r2["mint_id"]
    ok, n, bad = M.verify_ledger(path)
    assert ok and n == 3 and bad is None
    with pytest.raises(M.MintRefused):
        M.append_mint(e1, path)                          # same player via the same route
    assert M.verify_ledger(path)[1] == 3                 # nothing was written by the refusal


def test_cheat_an_edited_ledger_row_breaks_the_chain_and_blocks_appends(tmp_path):
    path = str(tmp_path / "L.jsonl")
    M.append_mint(_crossover(), path)
    M.append_mint(_flip(A, 9), path)
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    rows[0]["operator_params"] = {"mask_hex": "00" * 16}   # tamper with the FIRST row
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n")
    ok, n, bad = M.verify_ledger(path)
    assert not ok and bad == 0
    with pytest.raises(M.MintRefused):
        M.append_mint(_flip(A, 10), path)


def test_the_frozen_registry_is_untouched_by_minting():
    with open(REGISTRY, encoding="utf-8") as f:
        reg = json.load(f)
    assert reg["registry_id"].startswith("b15e0a7f5f2dcb99")
    assert len(reg["entries"]) == 64
    rec = M.mint(_crossover())
    assert rec["organism_ref"].split(":")[1] not in {e["organism_id"] for e in reg["entries"]}


def test_committed_ledger_verifies_if_present():
    ok, n, bad = M.verify_ledger()
    assert ok, (n, bad)
