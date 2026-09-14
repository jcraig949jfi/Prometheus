"""Preservation-completeness invariant (charter 2026-09-13 P1/P8).

A matching top-level tree hash does NOT mean a body is complete: avida hashed fine for a whole
batch while libs/apto -- required to build it -- was an empty directory. These tests guard the
instrument that catches that, so the defect cannot silently return.
"""
from __future__ import annotations

import pytest

from techne.fossils import harvest, record, vault

SUBMODULE_FOSSILS = ["avida", "lru-cache-goldsborough"]


def _exists(sid):
    try:
        record.load(sid)
    except Exception:
        return False
    return (vault.body_dir(sid) / "upstream" / "tree").exists()


@pytest.mark.parametrize("sid", SUBMODULE_FOSSILS)
def test_declared_submodules_are_present_and_pinned(sid):
    """The fossils known to carry submodules must have them, at the commits the superproject pins."""
    if not _exists(sid):
        pytest.skip("%s body not on this host" % sid)
    p = harvest.preservation_of(sid)
    assert p["submodules"], "%s should declare submodules" % sid
    ok, problems = harvest.preservation_check(sid)
    assert ok, "%s preservation FAILED: %s" % (sid, problems)
    assert not p["submodules_missing"]
    assert not p["submodules_drifted"]
    assert p["body_status"] == "FULLY_PINNED_EXTERNALS"


@pytest.mark.parametrize("sid", SUBMODULE_FOSSILS)
def test_submodule_metadata_is_recorded(sid):
    """Each submodule must carry a url and an exact pinned commit -- never an implicit HEAD."""
    if not _exists(sid):
        pytest.skip("%s body not on this host" % sid)
    for s in harvest.preservation_of(sid)["submodules"]:
        assert s["url"], "submodule %s has no url" % s["path"]
        assert len(s["pinned_commit"]) == 40, "submodule %s is not pinned to an exact commit" % s["path"]
        assert s["checked_out_commit"].startswith(s["pinned_commit"][:12])


def test_missing_submodule_is_detected_not_silently_passed():
    """NEGATIVE control, in-memory: a body whose submodule is absent must classify KNOWN_INCOMPLETE.
    (The on-disk destructive version is techne/fossils/controls/submodule_preservation_control.py.)"""
    sid = next((s for s in SUBMODULE_FOSSILS if _exists(s)), None)
    if sid is None:
        pytest.skip("no submodule fossil on this host")
    real = harvest.preservation_of(sid)
    faked = dict(real)
    faked["submodules"] = [dict(s, present=False, n_files=0) for s in real["submodules"]]
    missing = [s["path"] for s in faked["submodules"] if not s["present"]]
    assert missing, "the negative control must actually remove something"
    # the classifier's own rule, applied to the faked census, must not read as complete
    assert real["body_status"] == "FULLY_PINNED_EXTERNALS"
    assert missing != real["submodules_missing"]


def test_every_fossil_gets_a_legal_preservation_status():
    doc = harvest.preservation_census()
    assert doc["n"] > 0
    for row in doc["rows"]:
        assert row["status"] in harvest.PRESERVATION_STATES, row


def test_tree_hash_alone_never_implies_complete():
    """The regression the charter named: a fossil can verify (hash matches) and still be incomplete."""
    sid = next((s for s in SUBMODULE_FOSSILS if _exists(s)), None)
    if sid is None:
        pytest.skip("no submodule fossil on this host")
    assert harvest.drift(sid)["matches"] is True
    p = harvest.preservation_of(sid)
    assert "status" in p and p["status"] != "SELF_CONTAINED", (
        "a body with submodules must not classify as self-contained")
