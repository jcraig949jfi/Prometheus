"""Cheat controls for research_check: it must FAIL on each defect it claims to detect."""
import hashlib
from pathlib import Path

from comms.manifest import artifact_hash
from prometheus.cosmos.research_check import check

REAL = Path(__file__).resolve().parents[3] / "roles" / "Cosmos" / "research"

RULE = "genesis|abc|roles/Cosmos/research/THREADS.md|t"
TID = "thr-" + hashlib.sha256(RULE.encode()).hexdigest()[:12]
THREAD = """### T-X1 | A | t
- thread_id: """ + TID + """
- id_rule: """ + RULE + """
- status: OPEN
- zone: Z1
- question: q
- instruments: i
- first_experiment: f
- kill_criterion: k
- depends_on: none
"""
RESULT = """### R-1 | r
- status: {status}
- observation: o
- law: l
- domain: d
- falsifier: {fals}
- baselines: majority .5; definition rung .9
{extra}"""
GRAVE = """### G-1 | C0 | x
- law: l
- campaign: C0
- killed_by: UNRECOVERED -- tbd
- evidence: e
- fragments: f
"""
FREEZE = """### F-1 | a
- kind: file
- target: frozen.txt
- sha256: {h}
- supersedes: -
- review: PENDING
- status: {st1}
{second}"""


def ws(tmp_path, thread=THREAD, result=None, grave=GRAVE, freeze=None, frozen_text="law v1\n"):
    rd = tmp_path / "roles" / "Cosmos" / "research"
    rd.mkdir(parents=True)
    (tmp_path / "frozen.txt").write_text(frozen_text, encoding="utf-8")
    h = artifact_hash(tmp_path / "frozen.txt")
    (rd / "THREADS.md").write_text(thread, encoding="utf-8")
    (rd / "RESULTS.md").write_text(result or RESULT.format(status="PROVISIONAL", fals="x", extra=""),
                                   encoding="utf-8")
    (rd / "GRAVEYARD.md").write_text(grave, encoding="utf-8")
    (rd / "FREEZES.md").write_text(freeze or FREEZE.format(h=h, st1="ACTIVE", second=""),
                                   encoding="utf-8")
    return rd, h


def test_real_workspace_passes():
    errors, s = check(REAL)
    assert errors == [], errors
    assert s["threads"] >= 9


def test_clean_fixture_passes_and_counts_unrecovered(tmp_path):
    rd, _ = ws(tmp_path)
    errors, s = check(rd, tmp_path)
    assert errors == []
    assert s["graves_unrecovered"] == ["G-1"]
    assert s["freezes"] == {"F-1": "VERIFIED"}


def test_catches_missing_kill_criterion(tmp_path):
    rd, _ = ws(tmp_path, thread=THREAD.replace("- kill_criterion: k\n", ""))
    assert any("kill_criterion" in e for e in check(rd, tmp_path)[0])


def test_catches_bad_status_and_zone(tmp_path):
    rd, _ = ws(tmp_path, thread=THREAD.replace("OPEN", "WINNING").replace("Z1", "Z9"))
    errs = check(rd, tmp_path)[0]
    assert any("status" in e for e in errs) and any("zone" in e for e in errs)


def test_catches_collapsed_layers(tmp_path):
    rd, _ = ws(tmp_path, result=RESULT.format(status="PROVISIONAL", fals="o", extra=""))
    assert any("collapsed" in e for e in check(rd, tmp_path)[0])


def test_catches_missing_falsifier(tmp_path):
    rd, _ = ws(tmp_path, result=RESULT.format(status="PROVISIONAL", fals="", extra=""))
    assert any("falsifier" in e for e in check(rd, tmp_path)[0])


def test_catches_killed_result_without_grave(tmp_path):
    rd, _ = ws(tmp_path, result=RESULT.format(status="KILLED", fals="x", extra="- graveyard: G-9\n"))
    assert any("graveyard" in e for e in check(rd, tmp_path)[0])


def test_catches_edited_frozen_file(tmp_path):
    rd, _ = ws(tmp_path)
    (tmp_path / "frozen.txt").write_text("law v1 TUNED\n", encoding="utf-8")
    assert any("was edited" in e for e in check(rd, tmp_path)[0])


def test_crlf_checkout_is_not_an_edit(tmp_path):
    rd, _ = ws(tmp_path)
    (tmp_path / "frozen.txt").write_bytes(b"law v1\r\n")
    assert check(rd, tmp_path)[0] == []


def test_catches_deleted_superseded_freeze(tmp_path):
    rd, h = ws(tmp_path)
    second = "### F-2 | b\n- kind: file\n- target: frozen.txt\n- sha256: %s\n- supersedes: F-1\n" \
             "- review: PENDING\n- status: ACTIVE\n" % h
    (rd / "FREEZES.md").write_text(FREEZE.format(h=h, st1="SUPERSEDED", second=second), encoding="utf-8")
    assert check(rd, tmp_path)[0] == []
    (rd / "FREEZES.md").write_text(second, encoding="utf-8")        # old freeze removed
    assert any("not an EARLIER entry" in e for e in check(rd, tmp_path)[0])


def test_catches_superseded_freeze_left_active(tmp_path):
    rd, h = ws(tmp_path)
    second = "### F-2 | b\n- kind: file\n- target: frozen.txt\n- sha256: %s\n- supersedes: F-1\n" \
             "- review: PENDING\n- status: ACTIVE\n" % h
    (rd / "FREEZES.md").write_text(FREEZE.format(h=h, st1="ACTIVE", second=second), encoding="utf-8")
    assert any("superseded by F-2" in e for e in check(rd, tmp_path)[0])


def test_absent_git_freeze_is_unverifiable_not_error(tmp_path):
    rd, _ = ws(tmp_path, freeze="### F-1 | g\n- kind: git\n- target: " + "ab" * 20 +
               "\n- sha256: -\n- supersedes: -\n- review: N/A\n- status: ACTIVE\n")
    errors, s = check(rd, tmp_path)
    assert errors == [] and s["freezes"] == {"F-1": "UNVERIFIABLE_HERE"}


def test_catches_thread_id_that_does_not_rederive(tmp_path):
    rd, _ = ws(tmp_path, thread=THREAD.replace("THREADS.md|t\n", "THREADS.md|renamed\n"))
    assert any("re-derive" in e for e in check(rd, tmp_path)[0])


def test_catches_results_without_definition_rung(tmp_path):
    r = RESULT.format(status="PROVISIONAL", fals="x", extra="").replace("definition rung .9", "5-NN .8")
    rd, _ = ws(tmp_path, result=r)
    assert any("DEFINITION RUNG" in e for e in check(rd, tmp_path)[0])
