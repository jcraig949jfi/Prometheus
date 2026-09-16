"""PR-ID identity for CA rule tables and the join to Herakles's derivation records.

Controls: POSITIVE (two routes to one child give one organism_ref and two derivation ids; the
join round-trips), NEGATIVE (a different table gives a different ref; a parent-equal child is
flagged identity and never a new mechanism), CHEAT (a record whose child hex was swapped for a
plausible one passes the structural read but is REFUSED by the semantic owner's re-derivation,
so the structural read is never presented as verification).
"""
from __future__ import annotations

import pytest

from proteus.eval import rule_table_identity as R
from proteus.eval.identity import organism_ref

herakles_derive = pytest.importorskip("herakles.evca.derive")

GKL_LIKE = "005f005f005f005f005fff5f005fff5f"          # any 32-hex table; the value is not a claim
OTHER = "0123456789abcdef0123456789abcdef"


def test_canonical_hex_and_the_two_content_ids_agree_with_herakles():
    for h in (GKL_LIKE, OTHER, GKL_LIKE.upper(), OTHER[:16] + "_" + OTHER[16:]):
        assert R.canonical_rule_hex(h) == herakles_derive.canonical_hex(h)
        assert R.evca_player_id(h) == herakles_derive.player_id(h)
        assert R.rule_hex_of_evca_player(R.evca_player_id(h)) == R.canonical_rule_hex(h)
    # and the two owners REFUSE the same spellings: a 0x prefix is not a table for either
    with pytest.raises(R.RuleTableIdentityError):
        R.canonical_rule_hex("0x" + OTHER)
    with pytest.raises(Exception):
        herakles_derive.canonical_hex("0x" + OTHER)


def test_organism_ref_is_pr_id_over_the_canonical_body_only():
    ref = R.organism_ref_of_rule(GKL_LIKE)
    assert ref.startswith("sha256:") and len(ref) == 7 + 64
    assert ref == R.organism_ref_of_rule(GKL_LIKE.upper())          # spelling is not identity
    assert ref == organism_ref(R.rule_table_manifest(GKL_LIKE))
    assert ref != R.organism_ref_of_rule(OTHER)                      # negative
    assert ref != R.organism_ref_of_rule(GKL_LIKE, semantic_version="herakles.evca.core.v2")


def test_join_is_a_bijection_on_tables():
    pid = R.evca_player_id(GKL_LIKE)
    assert R.organism_ref_of_evca_player(pid) == R.organism_ref_of_rule(GKL_LIKE)
    with pytest.raises(R.RuleTableIdentityError):
        R.rule_hex_of_evca_player("sha256:" + "0" * 64)
    with pytest.raises(R.RuleTableIdentityError):
        R.canonical_rule_hex("zz" * 16)
    with pytest.raises(R.RuleTableIdentityError):
        R.canonical_rule_hex(OTHER + "00")


def test_positive_two_routes_one_child_one_ref_two_derivations():
    # route 1: edit two entries at once; route 2: the same two edits, one then the other
    edits = [(3, 1), (77, 0)]
    r1 = herakles_derive.derive_edit(GKL_LIKE, edits)
    mid = herakles_derive.derive_edit(GKL_LIKE, [edits[0]])
    r2 = herakles_derive.derive_edit(mid["child_rule_hex"], [edits[1]])
    a, b = R.verified_refs(r1), R.verified_refs(r2)
    assert a["child_organism_ref"] == b["child_organism_ref"]
    assert a["child_player_id"] == b["child_player_id"]
    assert a["derivation_id"] != b["derivation_id"]
    assert a["verified_by_semantic_owner"] and b["verified_by_semantic_owner"]
    assert a["parent_organism_refs"] == [R.organism_ref_of_rule(GKL_LIKE)]
    assert b["parent_organism_refs"] == [R.organism_ref_of_rule(mid["child_rule_hex"])]


def test_crossover_record_carries_both_parents_in_order():
    mask = herakles_derive.crossover_mask_one_point(64)
    rec = herakles_derive.derive_crossover(GKL_LIKE, OTHER, mask)
    refs = R.verified_refs(rec)
    assert refs["parent_organism_refs"] == [R.organism_ref_of_rule(GKL_LIKE),
                                            R.organism_ref_of_rule(OTHER)]
    assert refs["operator"] == "crossover_mask"
    assert refs["child_organism_ref"] not in refs["parent_organism_refs"]


def test_negative_identity_child_is_flagged_not_presented_as_new():
    # a no-op edit: set entry 0 to its current value
    cur = herakles_derive.decode_table(GKL_LIKE)[0]
    rec = herakles_derive.derive_edit(GKL_LIKE, [(0, int(cur))])
    refs = R.verified_refs(rec)
    assert refs["identity"] is True
    assert refs["child_organism_ref"] == refs["parent_organism_refs"][0]


def test_cheat_swapped_child_hex_passes_the_structural_read_and_fails_verification():
    rec = herakles_derive.derive_edit(GKL_LIKE, [(5, 1)])
    forged = dict(rec)
    forged["child_rule_hex"] = OTHER
    forged["child_player_id"] = R.evca_player_id(OTHER)
    forged["identity"] = False
    # structurally consistent: ids spell hexes, flag agrees -- the structural read cannot tell
    structural = R.refs_for_derivation(forged)
    assert structural["verified_by_semantic_owner"] is False
    assert structural["child_organism_ref"] == R.organism_ref_of_rule(OTHER)
    # the semantic owner's re-derivation refuses it
    with pytest.raises(Exception):
        R.verified_refs(forged)


def test_structural_read_fails_closed_on_inconsistent_records():
    rec = herakles_derive.derive_edit(GKL_LIKE, [(5, 1)])
    bad = dict(rec)
    bad["child_player_id"] = R.evca_player_id(OTHER)               # id does not spell the hex
    with pytest.raises(R.RuleTableIdentityError):
        R.refs_for_derivation(bad)
    bad = dict(rec)
    bad["identity"] = True                                          # flag disagrees with hexes
    with pytest.raises(R.RuleTableIdentityError):
        R.refs_for_derivation(bad)
    with pytest.raises(R.RuleTableIdentityError):
        R.refs_for_derivation({"kind": "something_else"})
