"""Tests for the Era-2 heartbeat wiring (PRON-03).

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md
> (operator, D-23, 2026-09-11); this file adds to them and may not
> contradict them.

test_productive_liveness.py proves the SEMANTICS are right. This file
proves the WIRING is right: that scripts/intelligence_loop.py actually
feeds those semantics from real events, and -- the part that matters --
that it cannot be made to claim success without one.

Run:  python -m pytest roles/Pronoia/science/test_heartbeat_wiring.py -q
"""

from __future__ import annotations

import importlib.util
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCIENCE = REPO_ROOT / "roles" / "Pronoia" / "science"
sys.path.insert(0, str(SCIENCE))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from productive_liveness import Health, WorkEvidence, derive_health  # noqa: E402


def _load_loop():
    """Import scripts/intelligence_loop.py without running main().

    Module import does touch the filesystem (it makes its log directory), so
    it is skipped rather than failed if the environment will not allow it --
    a test that cannot run must say so, not pass quietly.
    """
    path = REPO_ROOT / "scripts" / "intelligence_loop.py"
    spec = importlib.util.spec_from_file_location("intelligence_loop_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:  # pragma: no cover
        pytest.skip("intelligence_loop not importable here: %s" % e)
    return mod


LOOP = _load_loop()


# ---------------------------------------------------------------------------
# The state dict actually carries work fields now
# ---------------------------------------------------------------------------

def test_state_declares_work_fields_and_they_start_empty():
    st = LOOP.PRONOIA_STATE
    for k in ("last_work_attempt_at", "last_work_success_at", "work_cadence_sec"):
        assert k in st, "PRONOIA_STATE is missing %s" % k
    # They must start as NO EVIDENCE, not as an optimistic default.
    assert st["last_work_attempt_at"] is None
    assert st["last_work_success_at"] is None


def test_a_fresh_process_reads_booting_not_productive():
    """Wiring the fields in must not accidentally make startup look good."""
    started = datetime.now(timezone.utc)
    ev = WorkEvidence(started_at=started, last_heartbeat_at=started,
                      last_attempt_at=None, last_success_at=None)
    assert derive_health(started, ev, cadence_sec=3600) == Health.BOOTING


# ---------------------------------------------------------------------------
# _parse_iso: malformed evidence reads as NO evidence, never as a wrong time
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad", [None, "", "not-a-date", "2026-13-45T99:99", [], {}])
def test_parse_iso_returns_none_for_anything_unusable(bad):
    assert LOOP._parse_iso(bad) is None


def test_parse_iso_roundtrips_and_forces_tz_awareness():
    now = datetime.now(timezone.utc)
    assert LOOP._parse_iso(now.isoformat()) == now
    naive = datetime(2026, 9, 11, 12, 0, 0)
    got = LOOP._parse_iso(naive.isoformat())
    assert got is not None and got.tzinfo is not None, (
        "a naive stored timestamp must be made explicit, not compared raw")


# ---------------------------------------------------------------------------
# _cycle_left_evidence: the artifact check that makes exit-0 mean something
# ---------------------------------------------------------------------------

def test_cycle_left_evidence_false_when_nothing_was_written(tmp_path, monkeypatch):
    """NEGATIVE CONTROL for the artifact check."""
    monkeypatch.setattr(LOOP, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(LOOP, "DASHBOARD_FILES", ["docs/state.json"])
    (tmp_path / "docs").mkdir()
    assert LOOP._cycle_left_evidence(datetime.now(timezone.utc)) is False


def test_cycle_left_evidence_true_when_an_artifact_was_written(tmp_path, monkeypatch):
    """POSITIVE CONTROL: the check can detect a real write."""
    monkeypatch.setattr(LOOP, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(LOOP, "DASHBOARD_FILES", ["docs/state.json"])
    (tmp_path / "docs").mkdir()
    since = datetime.now(timezone.utc)
    time.sleep(0.02)
    (tmp_path / "docs" / "state.json").write_text("{}")
    assert LOOP._cycle_left_evidence(since) is True


def test_cycle_left_evidence_false_for_a_STALE_artifact(tmp_path, monkeypatch):
    """THE ONE THAT MATTERS. A file that already existed is not evidence that
    THIS cycle did anything. 'artifact exists -> artifact is fresh' is one of
    the named inference errors this seat hunts."""
    monkeypatch.setattr(LOOP, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(LOOP, "DASHBOARD_FILES", ["docs/state.json"])
    (tmp_path / "docs").mkdir()
    art = tmp_path / "docs" / "state.json"
    art.write_text("{}")
    old = time.time() - 86400
    os.utime(art, (old, old))          # written yesterday
    since = datetime.now(timezone.utc)  # cycle starts now
    assert LOOP._cycle_left_evidence(since) is False


def test_cycle_left_evidence_fails_closed_on_an_unreadable_path(tmp_path, monkeypatch):
    """An error is not a success. Failing closed costs a false STALLED, which
    is the cheap direction to be wrong in."""
    monkeypatch.setattr(LOOP, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(LOOP, "DASHBOARD_FILES", ["docs/\x00bad"])
    assert LOOP._cycle_left_evidence(datetime.now(timezone.utc)) is False


# ---------------------------------------------------------------------------
# The success rule, stated as the loop applies it
# ---------------------------------------------------------------------------

def _success_rule(cycle_ok: bool, evidence: bool) -> bool:
    """Mirror of the condition in the loop body. Kept beside the tests so a
    change to the rule that is not reflected here shows up as a failure."""
    return bool(cycle_ok and evidence)


@pytest.mark.parametrize("cycle_ok,evidence,expected", [
    (True,  True,  True),    # exit 0 AND a consequence -> success
    (True,  False, False),   # exit 0, nothing written  -> NOT success
    (False, True,  False),   # something written but a child failed
    (False, False, False),
])
def test_success_requires_both_exit_zero_and_a_consequence(cycle_ok, evidence, expected):
    assert _success_rule(cycle_ok, evidence) is expected


def test_the_loop_body_really_uses_that_conjunction():
    """Read the source and assert the rule is the one tested above. Cheap,
    and it catches the case where someone relaxes the condition in the loop
    and leaves these tests passing against a mirror that no longer mirrors."""
    src = (REPO_ROOT / "scripts" / "intelligence_loop.py").read_text(encoding="utf-8")
    assert "if cycle_ok and cycle_left_evidence:" in src, (
        "the success boundary in intelligence_loop.py no longer matches the "
        "rule these tests verify")
    # and it must be the ONLY place the success field is assigned
    assigns = src.count('PRONOIA_STATE["last_work_success_at"] =')
    assert assigns == 1, (
        "last_work_success_at is assigned in %d places; it must have exactly "
        "one writer or the boundary is not enforceable" % assigns)


def test_heartbeat_thread_never_writes_the_work_fields():
    """CHEAT CONTROL, at the architectural level. If the heartbeat thread
    could set its own work timestamps it could keep itself green forever --
    which is precisely what Era 2 did with status='online'. Assert the
    heartbeat function body contains no assignment to either field."""
    src = (REPO_ROOT / "scripts" / "intelligence_loop.py").read_text(encoding="utf-8")
    start = src.index("def _start_pronoia_pg_heartbeat")
    end = src.index("GIT_AUTHOR =")
    body = src[start:end]
    for field in ("last_work_attempt_at", "last_work_success_at"):
        assert 'PRONOIA_STATE["%s"] =' % field not in body, (
            "the heartbeat thread assigns %s -- it must only READ work state" % field)


def test_health_is_passed_to_the_writer_not_hardcoded():
    src = (REPO_ROOT / "scripts" / "intelligence_loop.py").read_text(encoding="utf-8")
    assert "health=health," in src, "health must be forwarded to write_heartbeat"
    assert "derive_health(" in src, "health must be DERIVED, not asserted"


# ---------------------------------------------------------------------------
# The persistence layer stayed backward compatible
# ---------------------------------------------------------------------------

def test_write_heartbeat_gained_only_optional_arguments():
    import inspect
    import agora_persist
    sig = inspect.signature(agora_persist.write_heartbeat)
    required = [n for n, p in sig.parameters.items()
                if p.default is inspect.Parameter.empty]
    assert required == ["agent_name", "machine"], (
        "write_heartbeat gained a required parameter; every existing caller "
        "in the fleet would break")
    for n in ("last_work_attempt_at", "last_work_success_at", "health"):
        assert n in sig.parameters and sig.parameters[n].default is None


def test_write_heartbeat_coalesces_work_state_so_it_cannot_be_erased():
    """A caller that never passes work state must not WIPE work state written
    by something that does. Verified against the SQL text because the
    alternative is a live database write, which this test will not do."""
    import agora_persist
    src = Path(inspect_file(agora_persist)).read_text(encoding="utf-8")
    for col in ("last_work_attempt_at", "last_work_success_at", "health"):
        assert "%s = COALESCE(EXCLUDED.%s" % (col, col) in src, (
            "%s is not COALESCEd on update; a legacy caller would null it" % col)


def inspect_file(mod) -> str:
    import inspect as _i
    return _i.getsourcefile(mod)
