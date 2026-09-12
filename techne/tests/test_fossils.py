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


@pytest.mark.skipif(not SPECIMENS, reason="no specimens on this tree")
@pytest.mark.parametrize("sid", SPECIMENS)
def test_every_specimen_has_a_recipe_and_a_hash_list(sid):
    d = vault.specimen_dir(sid)
    assert (d / "recipe.json").exists()
    assert (d / "UPSTREAM_HASHES.txt").exists()
    txt = (d / "UPSTREAM_HASHES.txt").read_text(encoding="utf-8")
    assert "TREE_SHA256" in txt


@pytest.mark.skipif(not SPECIMENS, reason="no specimens on this tree")
def test_at_least_one_receipt_per_specimen_that_was_run():
    ran = [s for s in SPECIMENS if record.load(s)["run_classification"] != "NOT_ATTEMPTED"]
    assert ran, "no specimen has been run"
    for s in ran:
        assert (vault.specimen_dir(s) / "receipts").exists() and \
               any((vault.specimen_dir(s) / "receipts").glob("*.json")), s
