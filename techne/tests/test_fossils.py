"""The fossil vault's own invariants (the harvest tooling, not the specimens)."""
from __future__ import annotations

import pathlib

import pytest

from techne.fossils import record, vault

SPECIMENS = sorted(p.name for p in vault.SPECIMENS.iterdir() if (p / "record.json").exists()) \
    if vault.SPECIMENS.exists() else []


def test_vault_root_is_derivable_and_absolute():
    r = vault.vault_root()
    assert r.is_absolute()
    assert vault.canonical_root().is_absolute()


def test_to_wsl_maps_drive_letters():
    assert vault.to_wsl(pathlib.Path("F:/a/b")).startswith("/mnt/f/")


def test_tree_hash_is_order_independent_of_walk():
    rows = [("b.txt", "22", 1), ("a.txt", "11", 2)]
    # tree_hash_of hashes the rows as given; hash_tree sorts, so the vault always feeds sorted
    assert vault.tree_hash_of(sorted(rows)) == vault.tree_hash_of(sorted(reversed(rows)))


@pytest.mark.skipif(not SPECIMENS, reason="no specimens on this tree")
@pytest.mark.parametrize("sid", SPECIMENS)
def test_every_specimen_record_is_valid_and_has_a_capability_summary(sid):
    rec = record.load(sid)
    assert not record.validate(rec), record.validate(rec)
    for k in ("built_to", "pressure", "success_means"):
        assert rec["human_capability_summary"][k]
    # the handoff must NOT name organs or functions -- it is context only. We cannot test
    # semantics, but we can assert the five context fields exist and none is a decomposition key.
    h = rec["nyx_handoff"]
    assert set(h) == {"here_is_the_machine", "where_it_came_from", "how_to_run_it",
                      "how_we_know_it_runs", "what_humans_used_it_for"}


#: A specimen legitimately has no recipe/receipt only when it is deliberately not run.
_NO_RUN = {"SOURCE_ONLY", "BINARY_ONLY", "BLOCKED_DEPENDENCY", "BLOCKED_PLATFORM",
           "BROKEN_UPSTREAM", "LEGAL_RESTRICTION", "NOT_ATTEMPTED"}


@pytest.mark.skipif(not SPECIMENS, reason="no specimens on this tree")
@pytest.mark.parametrize("sid", SPECIMENS)
def test_every_specimen_has_a_hash_list_and_a_recipe_unless_source_only(sid):
    d = vault.specimen_dir(sid)
    assert (d / "UPSTREAM_HASHES.txt").exists()
    assert "TREE_SHA256" in (d / "UPSTREAM_HASHES.txt").read_text(encoding="utf-8")
    if record.load(sid)["run_classification"] not in _NO_RUN:
        assert (d / "recipe.json").exists(), "%s is not SOURCE_ONLY but has no recipe" % sid


@pytest.mark.skipif(not SPECIMENS, reason="no specimens on this tree")
def test_every_run_specimen_has_a_receipt():
    ran = [s for s in SPECIMENS if record.load(s)["run_classification"] not in _NO_RUN]
    assert ran, "no specimen has been run"
    for s in ran:
        rd = vault.specimen_dir(s) / "receipts"
        assert rd.exists() and any(rd.glob("*.json")), s


@pytest.mark.skipif(not SPECIMENS, reason="no specimens on this tree")
@pytest.mark.parametrize("sid", SPECIMENS)
def test_observability_and_lineage_fields_present(sid):
    r = record.load(sid)
    assert set(r["observability"]) >= set(record.OBSERVABILITY_DIMS)
    for e in r.get("lineage_relations", []):
        assert e["relation"] in record.LINEAGE_RELATIONS, e
