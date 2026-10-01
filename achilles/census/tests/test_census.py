"""Controls for the Achilles fleet census (base role s2: positive, negative and CHEAT controls).

The cheat controls inject the signals that have historically lied in this program -- a fresh
registration, an 'online' Agora heartbeat, a WORKING label, a heartbeat message -- with no
substantive work behind them, and assert the census does NOT report the seat as active/working.
"""
import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from achilles.census import classify as C  # noqa: E402
from achilles.census import render as R  # noqa: E402
from achilles.census import sources as S  # noqa: E402

ROSTER = C.Roster(["Theseus", "Nestor", "Harmonia", "Aporia", "Techne", "Aphrodite"], {"Pythia": "Aporia"})


def no_owner(_f):
    return None


def owner_by_roles(f):
    parts = f.split("/")
    return parts[1] if len(parts) > 2 and parts[0] == "roles" and parts[1] in ROSTER.canon.values() else None


# ---------------------------------------------------------------- attribution

def test_positive_subject_prefix_with_instance_gives_seat_and_host():
    a = C.attribute_commit("Theseus[desktop-ruapvai-01f15f15]: charter ADOPTED", "", [], "James Craig", ROSTER, no_owner)
    assert a["seat"] == "Theseus" and a["basis"] == "subject-prefix" and a["host"] == "DESKTOP-RUAPVAI"


def test_positive_lane_and_trailer_attribution():
    assert C.attribute_commit("Nestor-B[m1-53677235]: rows", "", [], "", ROSTER, no_owner)["seat"] == "Nestor"
    a = C.attribute_commit("G[m1-d1dd222e]: rows 12-40", "Nestor-Instance: G m1-d1dd222e\n", [], "", ROSTER, no_owner)
    assert a["seat"] == "Nestor" and a["basis"] == "instance-trailer" and a["host"] == "M1"


def test_positive_case_insensitive_and_word_prefix():
    assert C.attribute_commit("TECHNE: arsenal", "", [], "", ROSTER, no_owner)["seat"] == "Techne"
    assert C.attribute_commit("Aporia journal 2026-09-30: x", "", [], "", ROSTER, no_owner)["seat"] == "Aporia"


def test_positive_path_majority():
    a = C.attribute_commit("W1: C-STATELESS CONFIRMED", "", ["roles/Nestor/a", "roles/Nestor/b", "README.md"], "", ROSTER, owner_by_roles)
    assert a["seat"] == "Nestor" and a["basis"] == "path-majority"


def test_negative_unattributable_commit_is_not_guessed():
    a = C.attribute_commit("WIP: misc", "", ["scripts/x.py", "docs/y.md"], "James Craig", ROSTER, owner_by_roles)
    assert a["seat"] is None and a["basis"] == "unattributed"


def test_negative_split_paths_do_not_attribute():
    a = C.attribute_commit("sweep", "", ["roles/Nestor/a", "roles/Aporia/b"], "", ROSTER, owner_by_roles)
    assert a["seat"] is None


def test_system_commits_are_not_seat_work():
    assert C.attribute_commit("auto: portfolio update 2026-09-30", "", ["docs/state.json"], "", ROSTER, no_owner)["seat"] == "SYSTEM"


# ---------------------------------------------------------------- experiment vocabulary

def test_positive_result_and_prereg_detection():
    assert C.commit_category("Theseus v0 RESULT: H1 hard test FAIL -- deep descendants", ["theseus/synth/x"]) == "experiment_result"
    assert C.verdict_token("Theseus v0 RESULT: H1 hard test FAIL") == "RESULT"
    assert C.commit_category("Theseus v0 PREREGISTRATION + machinery", ["roles/Theseus/prereg/x"]) == "experiment_start"
    assert C.commit_category("X-P2-SHAM CLEAN_NULL", []) == "experiment_result"


def test_negative_tests_heartbeats_and_dashboards_are_not_experiments():
    assert C.commit_category("Achilles: heartbeat to Aporia #1197", ["roles/Achilles/STATUS.md"]) == "status"
    assert C.commit_category("run pytest self-test after merge", ["archaeon/tests/x.py"]) == "work"
    assert C.commit_category("Theseus: state READY under CWO-2026-09-30B", ["roles/Theseus/WORK_STATE.json"]) == "status"
    assert C.commit_category("journal: notes", ["roles/Nyx/journal/2026-09-30.md"]) == "status"


def test_lowercase_prose_pass_is_not_a_verdict():
    # 'pass' in prose ('adoption pass') must not read as a PASS verdict; capitals do
    assert C.commit_category("Agora: adoption pass, queue classified", ["roles/Agora/x.md"]) != "experiment_result"
    assert C.commit_category("Lexis G1: PASS on the frozen bar", ["roles/Lexis/x.md"]) == "experiment_result"


# ---------------------------------------------------------------- state rules

def decl(state, age, source="WORK_STATE"):
    return {"state": state, "source": source, "time": None, "age_h": age}


def test_positive_declared_working_with_fresh_work_is_working_high():
    r = C.classify_seat("SEAT", [decl("WORKING", 1)], {"substantive_age_h": 0.5, "status_age_h": 0.2, "presence_age_h": 0.1}, {})
    assert r["state"] == "WORKING" and r["active"] == "Yes" and r["confidence"] == "HIGH"


def test_cheat_label_registration_and_heartbeat_without_work_is_not_active():
    """CHEAT: a fresh WORKING label + fresh presence + fresh heartbeat, but no substantive work."""
    r = C.classify_seat("SEAT", [decl("WORKING", 0.5)], {"substantive_age_h": None, "status_age_h": 0.3, "presence_age_h": 0.0}, {})
    assert r["state"] != "WORKING"
    assert r["active"] != "Yes"
    assert "ACTIVE_NO_WORK_48H" in r["flags"]


def test_cheat_presence_only_seat_with_no_declaration_is_dormant_not_active():
    """CHEAT: an 'online' legacy heartbeat (the Agora failure mode) and nothing else."""
    r = C.classify_seat("SEAT", [], {"substantive_age_h": 24 * 30, "status_age_h": None, "presence_age_h": 0.01}, {})
    assert r["state"] == "DORMANT" and r["active"] == "Uncertain"


def test_negative_retired_marker_without_activity():
    r = C.classify_seat("SEAT", [], {"substantive_age_h": 24 * 20}, {"state": "RETIRED", "source": "STATUS.md:7"})
    assert r["state"] == "RETIRED" and r["active"] == "No"


def test_parked_but_active_is_flagged_not_hidden():
    r = C.classify_seat("SEAT", [decl("PARKED", 2)], {"substantive_age_h": 1}, {})
    assert r["state"] == "PARKED" and "PARKED_BUT_ACTIVE" in r["flags"] and r["confidence"] == "LOW"


def test_conflicting_declarations_lower_confidence():
    r = C.classify_seat("SEAT", [decl("READY", 1, "WORK_STATE"), decl("BLOCKED", 2, "STATUS.md")], {"substantive_age_h": 1}, {})
    assert "CONFLICTING_STATES" in r["flags"] and r["confidence"] != "HIGH"


def test_no_evidence_is_unknown():
    r = C.classify_seat("SEAT", [], {}, {})
    assert r["state"] == "UNKNOWN" and r["confidence"] == "LOW"


def test_normalise_free_text_state():
    assert C.normalise_state("BLOCKED (promexec, operator); P0 CLOSED") == "BLOCKED"
    assert C.normalise_state("READY -> assigned C4 R-STAT (#1137)") == "READY"
    assert C.status_md_state("x\nseat state: RETIRED 2026-09-11 by the operator\n")[0] == "RETIRED"
    assert C.status_md_state("## Seat state: ACTIVE\n")[0] == "ACTIVE"


def test_host_mapping():
    assert C.host_from_instance("elsa-c0ac1245") == "ELSA"
    assert C.host_from_instance("gandalf-4c0c7e64") == "M3"
    assert C.host_from_machine("SPECTREX5") == "M2"
    assert C.host_from_instance("not-an-instance") is None


# ---------------------------------------------------------------- publication safety

def test_redaction_removes_email_addresses():
    assert "@" not in S.redact("sent 'x' to someone.name+tag@example.com (body=1)")


def _snap(status="SUCCESS"):
    seat = {"kind": "SEAT", "short_role": "r", "role_description": {"value": "d"}, "observed_role": None, "state": "WORKING",
            "active": "Yes", "last_active": {"value": "2026-09-30T00:00:00Z"}, "activity_age": "1h", "last_activity": "commit x",
            "task": {"value": "t", "source": "s", "candidates": []}, "last_experiment": None, "experiment_result": None,
            "last_commit": None, "engines": [], "branch_worktree": None, "host": {"value": "M1"}, "blocker": None,
            "confidence": "HIGH", "domain": "science", "flags": [], "current_work": "t",
            "state_detail": {"rule": "S3-working", "why": [], "declared": [], "activity": {"substantive_age_h": 1.0}},
            "recent_commits": [], "recent_messages": [], "recent_experiments": [], "evidence": [], "monitors": []}
    return {"generated_at_utc": "2026-09-30T00:00:00Z", "base_sha": "abc", "current_mwo": "MWO-0004", "latest_cwo": "x",
            "run": {"status": status, "last_successful_utc": "2026-09-30T00:00:00Z", "last_attempted_utc": "2026-09-30T00:00:00Z"},
            "summary": {"seats_total": 1, "entities_total": 1, "counts_by_state": {"WORKING": 1}, "active_6h": 1, "active_24h": 1,
                        "active_72h": 1, "experiments_24h": 0, "commits_24h": 0, "non_seat_entities": 0},
            "seats": {"Nestor": seat}, "engines": {}, "anomalies": [], "delta": {"note": "first run"}, "sources_status": {}, "mailer": {}}


def test_page_carries_client_side_staleness_check():
    page = R.render_html(_snap())
    assert "STALE OR FAILED CENSUS" in page and "run_status.json" in page and "Last successful census" in page


def test_email_block_contains_the_table_in_the_body():
    blk = R.email_block(_snap())
    for col in ("Agent", "Role", "State", "Last active", "Last experiment", "Current / last task", "Engine / system", "Last commit"):
        assert col in blk["markdown"] and col in blk["html"]
    assert "Nestor" in blk["markdown"] and blk["rows"] == 1


def _mailer():
    spec = importlib.util.spec_from_file_location("send_brief_email", ROOT / "scripts" / "send_brief_email.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_mailer_includes_fresh_census_and_tags_receipt(tmp_path):
    m = _mailer()
    blk = R.email_block(_snap())
    p = tmp_path / "email_census.json"
    p.write_text(json.dumps(blk), encoding="utf-8")
    now = dt.datetime(2026, 9, 30, 2, 0, tzinfo=dt.timezone.utc)
    md, html, tag = m.build_fleet_census(p, now)
    assert "Fleet census" in md and "Nestor" in html and tag.startswith("census=2026-09-30T00:00:00Z")
    assert "STALE" not in md


def test_mailer_says_stale_loudly(tmp_path):
    m = _mailer()
    p = tmp_path / "email_census.json"
    p.write_text(json.dumps(R.email_block(_snap())), encoding="utf-8")
    md, html, tag = m.build_fleet_census(p, dt.datetime(2026, 10, 2, tzinfo=dt.timezone.utc))
    assert "STALE FLEET CENSUS" in md and "STALE FLEET CENSUS" in html


def test_mailer_says_missing_loudly(tmp_path):
    m = _mailer()
    md, html, tag = m.build_fleet_census(tmp_path / "absent.json")
    assert "UNAVAILABLE" in md and tag == "census=UNAVAILABLE"


def test_negative_file_names_and_bookkeeping_packets_are_not_experiments():
    assert C.commit_category("Odysseus: remove legacy ARC3 lease detection (logged in FREEZE.md)", ["fabric/x.py"]) == "work"
    assert C.commit_category("Techne[gandalf-4c0c7e64]: review packet for the 2026-09-30 boot pass", ["roles/Techne/r.txt"]) == "work"
