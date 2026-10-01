"""TECHNE-126: the recipe axis must not report a clean scan where there was nothing to scan.

Controls:
  negative  a recipe with no network fetch reads NO_NETWORK_FETCH_DETECTED (the scan ran, clean)
  positive  a recipe that clones / pip-installs reads NETWORK_DEPENDENT and names the fetch
  cheat     NO recipe at all must NOT read as a clean scan (the defect: it used to)
  migration byte-exact one-line relabel, refuses ambiguity, keeps records that do have a recipe,
            idempotent, dry run writes nothing
  tree      no tracked record says NO_NETWORK_FETCH_DETECTED without a recipe.json beside it
"""
import json
import pathlib

import pytest

from techne.fossils import harvest, vault
from techne.fossils import migrate_recipe_status_20260930 as mig

SPECIMENS = vault.specimen_dir("_").parent


@pytest.fixture
def fake_specimens(tmp_path, monkeypatch):
    root = tmp_path / "specimens"
    root.mkdir()
    monkeypatch.setattr(vault, "specimen_dir", lambda sid: root / sid)
    return root


def _mk(root, sid, recipe=None):
    d = root / sid
    d.mkdir()
    if recipe is not None:
        (d / "recipe.json").write_text(json.dumps(recipe), encoding="utf-8")
    return d


def test_negative_control_recipe_without_fetch_is_a_clean_scan(fake_specimens):
    _mk(fake_specimens, "clean", {"build": ["make -C src"], "run": ["./a.out"]})
    assert harvest.recipe_status_of("clean") == "NO_NETWORK_FETCH_DETECTED"


def test_positive_control_recipe_with_fetch_is_network_dependent(fake_specimens):
    _mk(fake_specimens, "net", {"build": ["git clone https://github.com/openai/baselines.git", "pip install -e ."]})
    assert harvest.recipe_status_of("net") == "NETWORK_DEPENDENT"
    deps = harvest._recipe_network_deps("net")
    assert "git clone" in deps and "pip install" in deps


def test_cheat_control_no_recipe_is_not_a_clean_scan(fake_specimens):
    """The defect: with no recipe.json the old code returned NO_NETWORK_FETCH_DETECTED."""
    _mk(fake_specimens, "bare")
    assert harvest._recipe_network_deps("bare") == []          # nothing fired ...
    assert harvest.recipe_status_of("bare") == "NO_RECIPE"     # ... because nothing could have
    assert harvest.recipe_status_of("bare") != "NO_NETWORK_FETCH_DETECTED"


def test_recipe_states_vocabulary_is_closed():
    assert set(harvest.RECIPE_STATES) == {"NETWORK_DEPENDENT", "NO_NETWORK_FETCH_DETECTED", "NO_RECIPE"}


def _record_bytes(recipe_status, indent=2, eol="\n", extra=None):
    doc = {"specimen_id": "x", "preservation": {"status": "SELF_CONTAINED", "recipe_status": recipe_status,
                                               "note": "n"}, "seat": "Techne"}
    if extra:
        doc.update(extra)
    return (json.dumps(doc, indent=indent) + "\n").replace("\n", eol).encode("utf-8")


def test_relabel_changes_exactly_one_value_and_no_other_byte():
    for eol in ("\n", "\r\n"):
        raw = _record_bytes(mig.OLD, eol=eol)
        new, status = mig.relabel_bytes(raw)
        assert status == "RELABELED"
        assert new == raw.replace(mig.OLD_TEXT, mig.NEW_TEXT)
        assert len(raw) - len(new) == len(mig.OLD) - len(mig.NEW)
        assert json.loads(new)["preservation"]["recipe_status"] == "NO_RECIPE"
        assert (b"\r\n" in new) == (eol == "\r\n")            # line endings untouched


def test_relabel_refuses_ambiguity():
    # the old text appears twice (once outside preservation): a human decides, not this script
    raw = _record_bytes(mig.OLD, extra={"history": {"recipe_status": mig.OLD}})
    new, status = mig.relabel_bytes(raw)
    assert status == "AMBIGUOUS" and new == raw


def test_relabel_not_applicable_when_already_new_or_absent():
    for raw in (_record_bytes(mig.NEW), _record_bytes("NETWORK_DEPENDENT"),
                (json.dumps({"specimen_id": "y"}) + "\n").encode()):
        new, status = mig.relabel_bytes(raw)
        assert status == "NOT_APPLICABLE" and new == raw


def test_migration_on_a_fixture_tree(tmp_path):
    root = tmp_path / "specimens"
    root.mkdir()
    bare = root / "bare"; bare.mkdir(); (bare / "record.json").write_bytes(_record_bytes(mig.OLD))
    withr = root / "withrecipe"; withr.mkdir(); (withr / "record.json").write_bytes(_record_bytes(mig.OLD))
    (withr / "recipe.json").write_text("{}", encoding="utf-8")
    none = root / "nopres"; none.mkdir(); (none / "record.json").write_text('{"specimen_id": "n"}\n', encoding="utf-8")
    before = {p: p.read_bytes() for p in root.rglob("record.json")}

    dry = mig.migrate(root, write=False)
    assert dry["by_status"] == {"WOULD_RELABEL": 1, "HAS_RECIPE_KEPT": 1, "NOT_APPLICABLE": 1}
    assert {p: p.read_bytes() for p in root.rglob("record.json")} == before          # dry run writes nothing

    real = mig.migrate(root, write=True)
    assert real["by_status"] == {"RELABELED": 1, "HAS_RECIPE_KEPT": 1, "NOT_APPLICABLE": 1}
    assert json.loads((bare / "record.json").read_bytes())["preservation"]["recipe_status"] == "NO_RECIPE"
    assert (withr / "record.json").read_bytes() == before[withr / "record.json"]     # a scanned recipe keeps its label
    assert (none / "record.json").read_bytes() == before[none / "record.json"]

    again = mig.migrate(root, write=True)
    assert again["by_status"].get("RELABELED", 0) == 0                               # idempotent


def test_tracked_tree_has_no_clean_scan_label_without_a_recipe():
    bad = []
    for d in sorted(SPECIMENS.iterdir()):
        rp = d / "record.json"
        if not rp.exists():
            continue
        rs = (json.loads(rp.read_text(encoding="utf-8")).get("preservation") or {}).get("recipe_status")
        if rs is None:
            continue
        assert rs in harvest.RECIPE_STATES, (d.name, rs)
        if rs == "NO_NETWORK_FETCH_DETECTED" and not (d / "recipe.json").exists():
            bad.append(d.name)
    assert not bad, "clean-scan label with no recipe to scan: %s" % bad[:5]


def test_stored_label_equals_recomputed_label():
    """Every stored recipe_status is what the instrument would say now (needs no body)."""
    diff = []
    for d in sorted(SPECIMENS.iterdir()):
        rp = d / "record.json"
        if not rp.exists():
            continue
        rs = (json.loads(rp.read_text(encoding="utf-8")).get("preservation") or {}).get("recipe_status")
        if rs is not None and rs != harvest.recipe_status_of(d.name):
            diff.append((d.name, rs, harvest.recipe_status_of(d.name)))
    assert not diff, diff[:5]
