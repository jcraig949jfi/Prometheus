"""Shared roles and fresh-seat discovery (roles/base-role/INHERITANCE.md "Shared roles", 2026-10-03).

A roles/<name>-role/ directory is an inherited layer, not a seat. These tests check the property a fresh
session depends on: from the repository alone it can find its entry file and resolve its whole chain.
"""
import re
from pathlib import Path

from comms import api as comms_api

REPO = Path(__file__).resolve().parents[2]
ROLES = REPO / "roles"
INH = (ROLES / "base-role" / "INHERITANCE.md").read_text(encoding="utf-8")
BASE_BANNER = "Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md"
SHARED_DECL = re.compile(r"Inherits roles/([A-Za-z0-9_.-]+-role)/RESPONSIBILITIES\.md")


def _shared_roles():
    return sorted(p.name for p in ROLES.iterdir() if p.is_dir() and p.name.endswith("-role") and p.name != "base-role")


def _seats():
    return sorted(p.name for p in ROLES.iterdir() if p.is_dir() and not p.name.endswith("-role"))


def _entry_rows():
    sec = INH[INH.index("## Entry files"):INH.index("## Who adds a row")]
    rows = {}
    for m in re.finditer(r"^\| ([A-Za-z0-9_.-]+) \| ([A-Z_]+\.md)", sec, re.M):
        rows.setdefault(m.group(1), m.group(2))
    return rows


def _shared_table():
    sec = INH[INH.index("## Shared roles"):INH.index("## Who adds a row")]
    out = {}
    for m in re.finditer(r"^\| ([A-Za-z0-9_.-]+-role) \| ([^|]*) \| ([^|]*) \|", sec, re.M):
        out[m.group(1)] = sorted(s.strip() for s in m.group(3).split(",") if s.strip())
    return out


def test_shared_roles_are_not_seats_anywhere():
    roster = comms_api.roster()
    for name in ["base-role"] + _shared_roles():
        assert name not in roster, name
    assert set(roster) == set(_seats())


def test_every_shared_role_is_registered_and_inherits_the_base():
    table = _shared_table()
    for name in _shared_roles():
        entry = ROLES / name / "RESPONSIBILITIES.md"
        assert entry.exists(), name + " has no RESPONSIBILITIES.md"
        assert BASE_BANNER in entry.read_text(encoding="utf-8"), name + " lacks the base banner"
        assert name in table, name + " missing from INHERITANCE.md Shared roles"
    assert set(table) <= set(_shared_roles()), "registered shared roles with no directory"


def test_every_declared_shared_role_exists_and_lists_its_seat():
    table = _shared_table()
    entries = _entry_rows()
    for seat in _seats():
        f = entries.get(seat)
        if not f or not (ROLES / seat / f).exists():
            continue
        declared = set(SHARED_DECL.findall((ROLES / seat / f).read_text(encoding="utf-8", errors="replace")))
        for name in declared - {"base-role"}:
            assert (ROLES / name).is_dir(), "{} declares missing shared role {}".format(seat, name)
            assert seat in table.get(name, []), "{} not listed under {} in INHERITANCE.md".format(seat, name)
    for name, seats in table.items():
        for seat in seats:
            f = entries.get(seat)
            assert f, "{} (under {}) has no entry-file row".format(seat, name)
            text = (ROLES / seat / f).read_text(encoding="utf-8")
            assert BASE_BANNER in text and "Inherits roles/{}/RESPONSIBILITIES.md".format(name) in text, seat


def test_every_entry_file_row_resolves_for_the_seats_that_have_one():
    entries = _entry_rows()
    missing = [s for s in _seats() if s in entries and not (ROLES / s / entries[s]).exists()
               and not (ROLES / s / "BOOTSTRAP.md").exists()]
    assert not missing, missing


def test_fresh_session_pointers_exist():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert "Starting a seat session" in readme and "roles/base-role/WAKE_DIRECTIVE.md" in readme
    wake = (ROLES / "base-role" / "WAKE_DIRECTIVE.md").read_text(encoding="utf-8")
    assert "You are <Seat>. Bootstrap from Prometheus." in wake


# --- the RSO Builder Cell (operator directive 2026-10-03) ---------------------------------------------------
CELL = ("Palamedes", "Pallas", "Argus", "Cadmus", "Eupalamus")


def test_the_rso_builder_cell_is_discoverable_from_the_repository_alone():
    import json
    roster = comms_api.roster()
    table = _shared_table()
    entries = _entry_rows()
    assert table.get("rso-builder-role") == sorted(CELL)
    for seat in CELL:
        assert seat in roster, seat + " not addressable on comms"
        assert entries.get(seat) == "RESPONSIBILITIES.md", seat + " has no entry-file row"
        text = (ROLES / seat / "RESPONSIBILITIES.md").read_text(encoding="utf-8")
        assert BASE_BANNER in text and "Inherits roles/rso-builder-role/RESPONSIBILITIES.md" in text, seat
        wake = (ROLES / seat / "WAKE.md").read_text(encoding="utf-8")
        assert "You're @roles/{} Bootstrap.".format(seat) in wake and "workgraph ready " + seat in wake, seat
        ws = json.loads((ROLES / seat / "WORK_STATE.json").read_text(encoding="utf-8"))
        assert ws["seat"] == seat and ws.get("state"), seat
    assert (ROLES / "rso-builder-role" / "SOURCES.md").exists()


def test_the_cell_campaign_names_real_seats_and_one_ready_seed_for_the_coordinator():
    from workgraph import core
    camps = core.load_campaigns()
    _, c = camps["C-004"]
    assert c["coordinator_role"] == "Palamedes" and set(c["members"]) == set(CELL)
    assert all((ROLES / m).is_dir() for m in c["members"])
    assert {"Q1", "Q2", "Q3"} <= set(c["quality_classes"])
    tasks = core.load_tasks()
    assert tasks["C-004-T000"][1]["owner_role"] == "Palamedes"
