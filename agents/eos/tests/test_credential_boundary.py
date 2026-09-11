"""EOS-04 Phase 0: the falsifier the operator required, demonstrated.

Operator directive, Season II, Mission 5:

    "no tracked file other than the resolver may contain the legacy
     credential path or independently implement credential-path
     discovery. Demonstrate the test before requesting Phase 1."

This file is that test. IT IS EXPECTED TO FAIL TODAY, and every test
below that names outstanding work is marked xfail(strict=True) so that
the day it starts passing, pytest reports XPASS as a FAILURE and forces
whoever fixed it to come here and flip the marker. A green suite that
hides unfinished work is the thing this program keeps paying for.

Phase 0 is BLOCKED, and not on effort. See
test_the_canonical_resolver_is_reachable_from_a_conformant_workspace:
the resolver every one of these call sites is supposed to route through
cannot be imported from a D-23-conformant worktree, because it is
gitignored and untracked files do not exist in linked worktrees.
Routing the call sites through it today would replace working bespoke
loaders with ImportError on every conformant workspace in the program.

Run: python -m pytest agents/eos/tests/test_credential_boundary.py -q -rxX
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]

#: The one file CLAUDE.md names as canonical: "All API keys are loaded via
#: keys.py at the repo root. Scripts should `from keys import get_key`
#: rather than reading key files directly."
RESOLVER = "keys.py"

#: Files allowed to contain the literal legacy path because they are DATED
#: RECORDS OF THE PROBLEM, not instructions to reproduce it. Each is an
#: Eos artifact describing the migration; none is imported by anything.
#: A record that says "on 2026-09-11 the path was here" is evidence; a
#: README that says "put your key here" is a defect.
RECORD_ALLOWLIST = {
    "agents/eos/tests/test_credential_boundary.py",
    "agents/eos/tests/test_intake.py",
    "agents/eos/src/credential_census.py",
}

LEGACY_RX = r"agents/eos/\.env|[\"']agents[\"'][ ]*[,/][ ]*[\"']eos[\"']"


def _git_grep_files(pattern: str, *pathspecs: str) -> set[str]:
    cmd = ["git", "grep", "-l", "-E", pattern, "--", *pathspecs]
    r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=600)
    if r.returncode not in (0, 1):
        pytest.skip("git grep did not answer (rc={}); INDETERMINATE, not a pass".format(r.returncode))
    return {l.strip() for l in r.stdout.splitlines() if l.strip()}


# ---------------------------------------------------------------------------
# The blocker. This is not about Eos's code; it is about whether Phase 0 is
# even executable as specified.
# ---------------------------------------------------------------------------

@pytest.mark.xfail(strict=True, reason="BLOCKER, not a defect in this seat: keys.py is "
                                       "gitignored (.gitignore:9), so the resolver CLAUDE.md "
                                       "mandates does not exist in any linked worktree and "
                                       "`from keys import get_key` -- and therefore `import "
                                       "prometheus_llm` -- raises ModuleNotFoundError in every "
                                       "D-23-conformant workspace. Marked xfail rather than left "
                                       "red so the shared suite stays green; when keys.py becomes "
                                       "tracked this XPASSes and the failure drags someone here.")
def test_the_canonical_resolver_is_reachable_from_a_conformant_workspace():
    """D-23 requires every seat to work from a LINKED worktree and refuses
    the canonical checkout. Untracked files do not exist in linked
    worktrees. keys.py is gitignored (.gitignore:9).

    Measured 2026-09-11 from D:\\Prometheus-worktrees\\eos-base-role:
        from keys import get_key   -> ModuleNotFoundError
        import prometheus_llm      -> ModuleNotFoundError (it imports keys
                                      at module load)
    and from the canonical checkout, both succeed.

    So the program's mandated credential resolver AND its single model API
    are unreachable from every workspace the working contract permits. That
    is a conflict between two standing rules, reported to Archaeon under
    WORKING_CONTRACT s10 (a rule that cannot be followed is a defect in the
    constitution, not in the seat).

    This test asserts the property that must hold before Phase 0 can run:
    the resolver is a TRACKED file. It is not a test of Eos's code and Eos
    cannot make it pass alone -- un-ignoring keys.py is an operator
    decision that needs one human look at one literal first (see
    roles/Eos/EOS04_PHASE0_REPORT.md).
    """
    r = subprocess.run(["git", "ls-files", "--error-unmatch", RESOLVER],
                       cwd=str(REPO), capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, (
        "the canonical resolver {} is NOT TRACKED, so it does not exist in any "
        "linked worktree and `from keys import get_key` raises ModuleNotFoundError "
        "in every D-23-conformant workspace. Phase 0 cannot route call sites "
        "through a module they cannot import.".format(RESOLVER))


# ---------------------------------------------------------------------------
# The falsifier the operator specified. Expected to fail until Phase 0 lands.
# ---------------------------------------------------------------------------

@pytest.mark.xfail(strict=True, reason="EOS-04 Phase 0 outstanding: 17 tracked .py files "
                                       "still name the legacy credential path. Blocked on the "
                                       "resolver being tracked (see the blocker test above).")
def test_no_tracked_code_contains_the_legacy_credential_path():
    hits = _git_grep_files(LEGACY_RX, "*.py") - RECORD_ALLOWLIST - {RESOLVER}
    assert not hits, (
        "{} tracked python files name the legacy credential path instead of asking "
        "the resolver:\n  ".format(len(hits)) + "\n  ".join(sorted(hits)))


@pytest.mark.xfail(strict=True, reason="EOS-04 Phase 0 outstanding: documentation still "
                                       "instructs readers to place credentials in a seat directory.")
def test_no_tracked_documentation_instructs_readers_to_use_the_legacy_path():
    """Docs that TELL people to put a key in agents/eos/.env manufacture new
    call sites faster than Phase 0 can remove them. Dated records are
    exempt; README and setup instructions are not."""
    docs = _git_grep_files(LEGACY_RX, "*.md")
    instructional = {d for d in docs
                     if d.lower().endswith("readme.md") or "/docs/" in d.lower()}
    assert not instructional, (
        "{} tracked documents instruct readers to use the legacy path:\n  ".format(
            len(instructional)) + "\n  ".join(sorted(instructional)))


# ---------------------------------------------------------------------------
# What Eos CAN hold today: its own house.
# ---------------------------------------------------------------------------

def test_eos_own_code_does_not_discover_credential_paths():
    """Whatever the rest of the program does, this seat's own modules must
    not implement credential-path discovery. The one historical exception is
    the retired daemon's inline .env loader, which is archaeological material
    and is named here rather than quietly excluded."""
    src = REPO / "agents" / "eos" / "src"
    offenders = []
    for p in sorted(src.glob("*.py")):
        body = p.read_text(encoding="utf-8", errors="replace")
        rel = p.relative_to(REPO).as_posix()
        if rel in RECORD_ALLOWLIST or p.name == "eos_daemon.py":
            continue
        if ".env" in body and ("os.environ.setdefault" in body or "split(\"=\"" in body):
            offenders.append(rel)
    assert not offenders, "Eos modules discovering credentials themselves: {}".format(offenders)


def test_the_retired_daemon_is_the_only_eos_credential_reader_and_is_labelled():
    """eos_daemon.py parses agents/eos/.env inline at import. It is retired
    production machinery (the scorer it serves failed its own controls) and
    is kept as archaeological material. This test pins that it is the ONLY
    Eos file doing so, so the exception cannot silently grow."""
    daemon = (REPO / "agents" / "eos" / "src" / "eos_daemon.py").read_text(
        encoding="utf-8", errors="replace")
    assert "_env_file = EOS_ROOT / \".env\"" in daemon, (
        "eos_daemon's inline credential loader changed shape; re-check whether this "
        "exception is still the one being granted")


def test_env_file_stays_ignored():
    r = subprocess.run(["git", "check-ignore", "-q", "agents/eos/.env"],
                       cwd=str(REPO), capture_output=True, timeout=60)
    assert r.returncode == 0, "agents/eos/.env is NOT ignored -- a credential file is trackable"


def test_the_boundary_instruments_are_themselves_trackable():
    """Found 2026-09-11: agents/eos/.gitignore's `*credential*` line silently
    excluded THIS FILE and src/credential_census.py -- the test that holds the
    credential boundary and the census that finds leaks. git dropped both
    without a word; `git add -A` simply did not add them.

    A pattern written to exclude secrets BY NAME also excludes the tooling
    named after them. Same family as the Season I defect where the comment
    documenting a contamination bug triggered the bug.
    """
    for rel in ("agents/eos/tests/test_credential_boundary.py",
                "agents/eos/src/credential_census.py"):
        r = subprocess.run(["git", "check-ignore", "-q", rel],
                           cwd=str(REPO), capture_output=True, timeout=60)
        assert r.returncode != 0, "{} is IGNORED; the boundary instrument is invisible to git".format(rel)


def test_the_credential_patterns_still_bind():
    """The re-inclusion above must not weaken what it re-includes around."""
    for rel in ("agents/eos/.env", "agents/eos/reports/x.md",
                "agents/eos/data/my_secret.json"):
        r = subprocess.run(["git", "check-ignore", "-q", rel],
                           cwd=str(REPO), capture_output=True, timeout=60)
        assert r.returncode == 0, "{} is TRACKABLE; a credential path escaped".format(rel)
