"""The base role tests its own claims (WORKING_CONTRACT.md s10).

Every mandatory artifact path is committable, every inherited file exists
and is pure ASCII, every role carries the banner, every issued manifest's
hashes match the files, and the executable invariants can be satisfied by
the supported harness. A failure here is a defect in the constitution.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

import pytest

from archaeon import workspace as W

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "roles" / "base-role"
# The PROPERTY is a declared inheritance of both base files; the blockquote prefix is a label
# (Rhadamanthus #146: Mnemosyne's rewritten file declares it in prose and the test was red on main).
BANNER = "Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md"
PRIMARY = ("RESPONSIBILITIES.md", "ROLE.md", "BOOTSTRAP.md", "CHARTER.md")
MANDATORY = ("journal/2026-01-01.md", "INBOX_SOMEONE_TOPIC_2026-01-01.md", "prompts/2026-01-01_topic/PROMPT.md",
             "BACKLOG_H0H5.md", "STATUS.md",
             # every base-mandated path class, checked mechanically (Ergon 772edf15e found archive/ ignored)
             "archive/x.md", "superseded/x.md", "ops/x.json", "ledgers/x.json", "calibration/x.md",
             "D23_COMPLIANCE_2026-01-01.md", "reviews/x.md", "contracts/x.json", "science/x.py")


def _roles():
    return sorted(p for p in (REPO / "roles").iterdir() if p.is_dir() and p.name != "base-role")


def _ignored(path: str) -> bool:
    r = subprocess.run(["git", "check-ignore", "-q", path], cwd=str(REPO), capture_output=True, text=True, timeout=30)
    return r.returncode == 0


def test_every_mandatory_artifact_path_is_committable_for_every_seat():
    """Vivarium aee89ff8b: `journal/` ignored the journals the base role mandated, for all 27 seats."""
    bad = []
    for role in _roles():
        for rel in MANDATORY:
            p = "roles/{}/{}".format(role.name, rel)
            if _ignored(p):
                bad.append(p)
    assert not bad, "gitignored mandatory artifact paths: {}".format(bad[:8])


def test_base_role_files_exist_and_are_pure_ascii():
    for name in ("RESPONSIBILITIES.md", "WORKING_CONTRACT.md", "NORTH_STAR.md", "README.md", "INHERITANCE.md"):
        f = BASE / name
        assert f.exists(), name
        raw = f.read_bytes()
        non_ascii = [i for i, b in enumerate(raw) if b > 0x7F]
        assert not non_ascii, "{} has non-ASCII bytes at {}".format(name, non_ascii[:5])
    assert "PROMETHEUS NORTH STAR" in (BASE / "NORTH_STAR.md").read_text(encoding="utf-8")


def test_every_role_carries_the_inheritance_banner_on_a_primary_document():
    missing = []
    for role in _roles():
        docs = [role / n for n in PRIMARY if (role / n).exists()] or sorted(role.glob("CHARTER*.md")) + sorted(role.glob("ROLE*.md"))
        if not docs:
            missing.append(role.name + " (no primary document)"); continue
        if not any(BANNER in d.read_text(encoding="utf-8", errors="replace") for d in docs):
            missing.append(role.name)
    assert not missing, missing


def test_issued_manifests_verify_against_their_files():
    """A prompt is what its manifest says it is: sha256 over the committed bytes (LF).
    Every seat's prompt manifests (Apollo, comms #22: the glob once covered Archaeon only)."""
    import sys
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from comms import manifest as M
    checked = 0
    for manifest in (REPO / "roles").glob("*/prompts/*/MANIFEST.md"):
        n, bad = M.verify(manifest.parent)
        assert not bad, "{}: {}".format(manifest.parent.relative_to(REPO), bad[:3])
        checked += n
    for manifest in (REPO / "roles" / "Archaeon" / "prompts").glob("*/MANIFEST.md"):
        text = manifest.read_text(encoding="utf-8")
        for m in re.finditer(r"^- (\S+)\s+sha256:([0-9a-f]{64})", text, flags=re.M):
            f = manifest.parent / m.group(1)
            if not f.exists():
                continue
            blob = subprocess.run(["git", "show", "HEAD:{}".format(f.relative_to(REPO).as_posix())], cwd=str(REPO),
                                  capture_output=True, timeout=30).stdout
            if not blob:
                continue                                   # not committed yet in this tree
            assert hashlib.sha256(blob).hexdigest() == m.group(2), "{} does not match its manifest".format(f)
            checked += 1
    assert checked >= 5


def _init_repo(path: Path):
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "t"], check=True)
    (path / "f.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(path), "add", "f.txt"], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-q", "-m", "init"], check=True)


def test_a_harness_linked_worktree_under_the_canonical_path_passes_the_guard(tmp_path):
    """Ruling 2: isolation is the invariant, not the path. The harness assigns
    .claude/worktrees/<name> beneath the canonical checkout; that is a linked
    worktree (git-dir != git-common-dir) and must be allowed."""
    canonical = tmp_path / "canonical"; canonical.mkdir()
    _init_repo(canonical)
    harness = canonical / ".claude" / "worktrees" / "seat-task"
    harness.parent.mkdir(parents=True)
    subprocess.run(["git", "-C", str(canonical), "worktree", "add", "-q", str(harness), "-b", "seat/task"], check=True)
    assert W.is_main_worktree(canonical) is True
    assert W.is_main_worktree(harness) is False
    assert W.receipt(harness)["worktree_path"].startswith(str(canonical.resolve()))


def test_this_test_runs_from_a_linked_worktree_and_journals_are_committable_here():
    assert W.is_main_worktree(REPO) is False, W.receipt(REPO)
    assert not _ignored("roles/Archaeon/journal/2026-09-11.md")


def _registry_names():
    text = (BASE / "MONITORS.md").read_text(encoding="utf-8")
    names = set()
    for line in text.splitlines():
        if " | " in line and not line.startswith(("  ", "One row", "name |")):
            head = line.split(" | ", 1)[0].strip()
            for n in head.split(" / "):
                names.add(n.strip())
    return names


def test_monitor_registry_rows_carry_every_column():
    text = (BASE / "MONITORS.md").read_text(encoding="utf-8")
    rows = [l for l in text.splitlines() if l.count(" | ") >= 8 and not l.startswith("  name")]
    assert len(rows) >= 8
    for r in rows:
        cols = [c.strip() for c in r.split(" | ")]
        assert len(cols) >= 10 and all(cols[:10]), "registry row needs ten non-empty columns (rule 8 productivity): {}".format(r[:60])
        assert any(k in cols[8] for k in ("ACTIVE", "DORMANT", "DEAD", "DISABLED", "UNLOCATED")), r[:60]


def test_seat_trees_are_allowlisted_against_blanket_content_type_ignores():
    """D-30 (Hypatia HYPATIA-27, the fourth instance in eleven days): nothing a
    seat writes under roles/<Seat>/ is swallowed by a content-type rule such
    as **/results/ or **/reports/; only generated, binary, credential and
    per-process state files stay ignored, and those are listed explicitly."""
    seat = "roles/ZzzSyntheticSeat"
    kept = ["results/rows.json", "reports/readout.md", "output/x.txt", "logs/notes.md",
            "science/results/r.csv", "journal/2026-09-11.md", "archive/a.md", "ledgers/rows.jsonl",
            "prompts/2026-09-11_x/MANIFEST.md", "artifacts/alignment/report.md"]
    dropped = ["__pycache__/a.pyc", "atlas.db", "atlas.db-wal", ".env", "config.local.json",
               "keys.py", "run.log", "SESSION_JOURNAL_1.md", "loop_state.json", "big.pkl"]
    for rel in kept:
        assert not _ignored("{}/{}".format(seat, rel)), rel
    for rel in dropped:
        assert _ignored("{}/{}".format(seat, rel)), rel


RULE10_UNDECLARED_ACTIVE_AT_ADOPTION = 12   # 2026-09-11 evening; may only fall


def _registry_rows():
    text = (BASE / "MONITORS.md").read_text(encoding="utf-8")
    return [[c.strip() for c in l.split(" | ")] for l in text.splitlines()
            if l.count(" | ") >= 8 and not l.startswith("  name")]


def test_rule_10_columns_are_present_and_well_formed():
    """Base rule 10 (D-27): every registry row carries a BOUND and an
    ACCOUNTABLE SEAT; a bound is an integer with a unit, a declared
    not-a-loop reason, or the literal UNDECLARED (owner migration pending)."""
    rows = _registry_rows()
    assert rows and all(len(r) == 12 for r in rows), [r[0] for r in rows if len(r) != 12]
    for r in rows:
        bound, seat = r[10], r[11]
        assert bound and seat, r[0]
        ok = bound == "UNDECLARED" or bound.startswith("not a loop") or re.match(r"^[0-9]+ ", bound)
        assert ok, "bound must be '<int> <unit> ...', 'not a loop: ...' or UNDECLARED: {} -> {}".format(r[0][:40], bound[:60])
        if bound != "UNDECLARED":
            assert seat != "UNDECLARED" and seat in {r.name for r in _roles()}, "bound without a registered accountable seat: {} -> {}".format(r[0][:40], seat)


def test_rule_10_undeclared_active_loops_only_ratchet_down():
    """A loop running at adoption may stay UNDECLARED while its owner
    migrates; the count can only fall. A NEW loop (a row added later) must
    declare both, so this number never rises."""
    rows = _registry_rows()
    und = [r[0] for r in rows if r[10] == "UNDECLARED" and "ACTIVE" in r[8]]
    assert len(und) <= RULE10_UNDECLARED_ACTIVE_AT_ADOPTION, und


def test_every_enabled_prometheus_scheduled_task_on_this_host_is_registered():
    """Base rule 7: an unregistered standing loop is unmanaged. Windows only."""
    import shutil
    if not shutil.which("powershell"):
        pytest.skip("no Task Scheduler on this host")
    cmd = ("Get-ScheduledTask | Where-Object { $_.TaskName -match 'Prometheus|Tick|Watchdog|PEW|SFE|Vivarium|Aporia|Elenchus' "
           "-and $_.State -ne 'Disabled' } | ForEach-Object { $_.TaskName }")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=120).stdout
    tasks = {l.strip() for l in out.splitlines() if l.strip()}
    if not tasks:
        pytest.skip("no Prometheus scheduled tasks on this host")
    missing = sorted(tasks - _registry_names())
    assert not missing, "enabled scheduled tasks with no registry row: {}".format(missing)
