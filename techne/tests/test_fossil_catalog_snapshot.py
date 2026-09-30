"""TECHNE-125: the tracked techne/fossils/CATALOG.json is a HOST-NEUTRAL snapshot that cannot go
stale silently.

The 2026-09-13 snapshot sat on main for 16 days at 121 rows while the records grew to 168, and it
carried M1 drive paths and a body count that was only true on M1. Nothing failed, because nothing
compared the snapshot with the records.

Controls:
  staleness   the snapshot names exactly the tracked records, with each record's current tree hash
  neutrality  no cell depends on the writing host (no body check, no vault path, no drive letter)
  cheat       a catalog written WITH a body check is detected as host-dependent by the same detector;
              a snapshot with one row removed / one hash altered is detected as stale
"""
import copy
import json
import re

from techne.fossils import catalog, vault

SNAPSHOT = vault.REPO / "techne" / "fossils" / "CATALOG.json"
_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")


def host_dependent_cells(doc: dict) -> list:
    """Every cell of a catalog document that depends on the machine that wrote it."""
    bad = []
    if doc.get("host_neutral") is not True:
        bad.append("host_neutral is not true")
    if doc.get("vault_root_on_this_host") is not None:
        bad.append("vault_root_on_this_host")
    if doc.get("bodies_present_on_this_host") is not None:
        bad.append("bodies_present_on_this_host")
    rr = doc.get("records_root")
    if not isinstance(rr, str) or _DRIVE.match(rr) or rr.startswith("/"):
        bad.append("records_root is not repository-relative: %r" % (rr,))
    for r in doc.get("rows", []):
        for k in ("body_present_on_this_host", "body_path", "mirror_available"):
            if r.get(k) is not None:
                bad.append("%s.%s" % (r.get("fossil_id"), k))
        for k in ("record_path", "recipe_path"):
            v = r.get(k)
            if isinstance(v, str) and (_DRIVE.match(v) or v.startswith("/")):
                bad.append("%s.%s is absolute" % (r.get("fossil_id"), k))
    return bad


def staleness(doc: dict) -> list:
    """How the snapshot differs from the tracked records: missing ids, extra ids, changed tree hashes."""
    live = {r["fossil_id"]: r["tree_sha256"] for r in catalog.enumerate_fossils(check_bodies=False)}
    snap = {r["fossil_id"]: r["tree_sha256"] for r in doc.get("rows", [])}
    out = ["missing from snapshot: %s" % s for s in sorted(set(live) - set(snap))]
    out += ["in snapshot but no record: %s" % s for s in sorted(set(snap) - set(live))]
    out += ["tree hash differs: %s" % s for s in sorted(set(live) & set(snap)) if live[s] != snap[s]]
    if doc.get("fossils") != len(doc.get("rows", [])):
        out.append("fossils count %r != %d rows" % (doc.get("fossils"), len(doc.get("rows", []))))
    return out


def _snapshot():
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def test_tracked_snapshot_is_host_neutral():
    bad = host_dependent_cells(_snapshot())
    assert not bad, "host-dependent cells in the tracked snapshot: %s" % bad[:5]


def test_tracked_snapshot_is_not_stale():
    diff = staleness(_snapshot())
    assert not diff, ("CATALOG.json is stale; regenerate with `python -m techne.fossils.catalog "
                      "--no-body-check --out techne/fossils/CATALOG.json`: %s" % diff[:5])


def test_live_host_neutral_catalog_passes_both_detectors():
    doc = catalog.catalog(check_bodies=False)
    assert host_dependent_cells(doc) == []
    assert staleness(doc) == []


def test_cheat_control_body_checked_catalog_is_detected_as_host_dependent():
    doc = catalog.catalog(check_bodies=True)
    bad = host_dependent_cells(doc)
    assert "vault_root_on_this_host" in bad and "bodies_present_on_this_host" in bad
    assert any(b.endswith(".body_path") for b in bad)


def test_cheat_control_stale_snapshots_are_detected():
    doc = catalog.catalog(check_bodies=False)
    dropped = copy.deepcopy(doc)
    gone = dropped["rows"].pop()["fossil_id"]
    dropped["fossils"] -= 1
    assert staleness(dropped) == ["missing from snapshot: %s" % gone]
    altered = copy.deepcopy(doc)
    altered["rows"][0]["tree_sha256"] = "0" * 64
    assert staleness(altered) == ["tree hash differs: %s" % altered["rows"][0]["fossil_id"]]
    extra = copy.deepcopy(doc)
    extra["rows"].append(dict(extra["rows"][0], fossil_id="no-such-fossil"))
    extra["fossils"] += 1
    assert "in snapshot but no record: no-such-fossil" in staleness(extra)
