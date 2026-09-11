"""Controls for the Eos intake gate.

Base role s2: every change ships with a POSITIVE control and a CHEAT control
where the change is measured; a NEGATIVE control is welcome but does not
substitute. They answer different questions:

    NEGATIVE  I do not hallucinate an admission where there is nothing
    POSITIVE  I can detect a real link into the program
    CHEAT     the measurement channel can actually observe what I claim to
              measure -- and, here, it cannot fully: test_cheat_* LOCKS IN a
              known hole so that closing it breaks this test loudly instead
              of quietly improving behind everyone's back.

Run: python -m pytest agents/eos/tests/test_intake.py -q
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SRC))

from intake import (Claim, Item, INDETERMINATE, PENDING, SELF_PATHS, classify,  # noqa: E402
                    check_capability_absent, check_rationale_admissible, summarise)

FALSIFIER = ("If the named object's measured behaviour is unchanged after this item is read, "
             "the anchor was useless and the row is deleted with its reason.")
CLEAN = "Proposed as an anchor against a named object in the repository."


def _item(iid="t-1", title="A method for handing off populations between search operators",
          abstract="A method.") -> Item:
    return Item(id=iid, title=title, source="test", url="https://example.invalid/" + iid,
                abstract=abstract, fetched_at="2026-09-11T00:00:00+00:00", provenance="unit test")


def _anchor(referent: str, rationale: str = CLEAN) -> Claim:
    return Claim(sought="ANCHOR", rationale=rationale, referent=referent,
                 falsifier=FALSIFIER, proposed_by="test")


# --- NEGATIVE -------------------------------------------------------------

def test_negative_no_referent_is_refused():
    """Nothing in, nothing admitted."""
    v = classify(_item(), _anchor("research/frontier/does_not_exist.md#relevance"))
    assert v.state == "REFUSED"
    assert "no such file" in v.reason


def test_negative_real_file_wrong_token_is_refused():
    v = classify(_item(), _anchor("roles/base-role/RESPONSIBILITIES.md#ZZ_NOT_IN_THIS_FILE_ZZ"))
    assert v.state == "REFUSED"
    assert "does not occur" in v.reason


def test_negative_referent_escaping_the_repo_is_refused():
    v = classify(_item(), _anchor("../../../etc/passwd#root"))
    assert v.state == "REFUSED"


# --- POSITIVE -------------------------------------------------------------

def test_positive_real_referent_reaches_pending(tmp_path):
    """The gate can detect a real link: a real file and a token really in it."""
    v = classify(_item(), _anchor("roles/base-role/RESPONSIBILITIES.md#No LLM adjudicates"))
    assert v.state == PENDING, v.reason
    assert all(c.passed for c in v.checks)


def test_positive_resource_from_our_own_measurement_terminates():
    now = datetime.now(timezone.utc)
    c = Claim(sought="RESOURCE", rationale="Called today; status and latency recorded.",
              observation={"endpoint": "https://export.arxiv.org/api/query", "status": 200,
                           "observed_at": now.isoformat(), "observed_by": "eos-intake",
                           "latency_ms": 431})
    assert classify(_item("r-1"), c).state == "RESOURCE"


# --- CHEAT ----------------------------------------------------------------

def test_cheat_a_real_but_unrelated_referent_still_passes():
    """THE KNOWN HOLE, locked in deliberately.

    The gate verifies that a referent EXISTS, not that it is the RIGHT one.
    A bait item paired with a genuine file and a genuine token passes. This
    was predicted before it was run (roles/Eos/intake/PREREGISTRATION_
    2026-09-11.md, Test 4) and it happened.

    If a future change closes the hole, THIS TEST FAILS -- which is the
    point. The seat must then update the test, the calibration ledger and
    the module docstring together, rather than silently inheriting a
    reputation the mechanism has not earned.
    """
    bait = _item("bait", title="Compressed Coordinate Systems for Cross-Domain Structure Discovery",
                 abstract="We learn compressing coordinate systems under which structure becomes detectable.")
    v = classify(bait, _anchor("roles/base-role/RESPONSIBILITIES.md#No LLM adjudicates"))
    assert v.state == PENDING, (
        "the gate now refuses an unrelated-but-real referent -- the hole may be closed; "
        "update this test, CALIBRATION.md and the intake.py docstring together. Reason: " + v.reason)


def test_cheat_documented_free_tier_is_not_a_resource():
    """A provider's pricing page is a label, not a measurement."""
    c = Claim(sought="RESOURCE", rationale="The registry row records free_tier true.",
              observation={"endpoint": "https://example-provider/v1", "status": "documented",
                           "observed_at": datetime.now(timezone.utc).isoformat(),
                           "observed_by": "provider-documentation"})
    v = classify(_item("r-2"), c)
    assert v.state == "REFUSED" and "observed_by" in v.reason


def test_cheat_stale_measurement_is_refused():
    old = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
    c = Claim(sought="RESOURCE", rationale="Measured once.",
              observation={"endpoint": "https://x.invalid", "status": 200,
                           "observed_at": old, "observed_by": "eos-intake"})
    assert classify(_item("r-3"), c).state == "REFUSED"


def test_cheat_future_measurement_is_refused():
    ahead = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    c = Claim(sought="RESOURCE", rationale="Measured.",
              observation={"endpoint": "https://x.invalid", "status": 200,
                           "observed_at": ahead, "observed_by": "eos-intake"})
    assert classify(_item("r-4"), c).state == "REFUSED"


# --- the rules the operator ruled ----------------------------------------

def test_gate_never_admits():
    """ANCHOR and ACQUIRE are human acts. The gate may not emit them."""
    states = set()
    for ref in ("roles/base-role/RESPONSIBILITIES.md#No LLM adjudicates",
                "research/frontier/nope.md#x"):
        states.add(classify(_item(), _anchor(ref)).state)
    assert "ANCHOR" not in states and "ACQUIRE" not in states


@pytest.mark.parametrize("word", ["interesting", "relevant", "promising", "state-of-the-art", "novel"])
def test_inadmissible_rationale_is_rejected(word):
    c = _anchor("roles/base-role/RESPONSIBILITIES.md#No LLM adjudicates",
                rationale="This work is highly {} for our substrate.".format(word))
    assert classify(_item(), c).state == "REFUSED"


def test_missing_falsifier_is_refused():
    c = Claim(sought="ANCHOR", rationale=CLEAN,
              referent="roles/base-role/RESPONSIBILITIES.md#No LLM adjudicates",
              falsifier="", proposed_by="test")
    assert classify(_item(), c).state == "REFUSED"


def test_item_without_provenance_is_refused():
    it = Item(id="p-0", title="t", source="", url="", abstract="", fetched_at="", provenance="")
    assert classify(it, _anchor("roles/base-role/RESPONSIBILITIES.md#No LLM adjudicates")).state == "REFUSED"


# --- instrument error is not evidence ------------------------------------

def test_indeterminate_is_not_a_refusal():
    """A check that DID NOT ANSWER must not be banked as a fact about the
    item. The first season produced exactly one of these (a dedup search that
    exceeded its budget) and it would otherwise have read as a refusal."""
    import intake as m
    original = m._git_grep_count
    m._git_grep_count = lambda marker, timeout=None: -1
    try:
        c = Claim(sought="ACQUIRE", rationale="An engine the program may lack.",
                  destination="vivarium/specs/x.json", capability_markers=["ZZZ"],
                  consumer="roles/Vivarium/CHARTER.md", proposed_by="test")
        v = classify(_item("i-1"), c)
        assert v.state == INDETERMINATE
        assert v.state != "REFUSED"
        assert any(ch.indeterminate for ch in v.checks)
    finally:
        m._git_grep_count = original


def test_dedup_search_excludes_everything_this_seat_writes():
    """The instrument asks what THE PROGRAM has. Eos is not the program: its
    records, its archive and its own source are excluded, or every item it
    writes down becomes 'already present' on the next pass. Both halves of
    this were found by running it, one level apart."""
    assert ":(exclude)roles/Eos/" in SELF_PATHS
    assert ":(exclude)agents/eos/" in SELF_PATHS


def test_summarise_counts_every_state():
    keys = set(summarise([]))
    assert {"ANCHOR", "ACQUIRE", "RESOURCE", "REFUSED", PENDING, INDETERMINATE} <= keys


# --- workspace and credential hygiene ------------------------------------

@pytest.mark.parametrize("entry", ["eos_daemon.py", "library_scanner.py", "probe.py"])
def test_d23_guard_present_at_every_entry_point(entry):
    """EOS-19. A scan that can run from the canonical checkout is the defect
    D-23 exists to prevent."""
    body = (SRC / entry).read_text(encoding="utf-8")
    assert "assert_not_canonical" in body, entry


def test_env_file_stays_ignored():
    """The program's keyring lives at agents/eos/.env until EOS-04 moves it.
    Re-including agents/eos/ in .gitignore must never re-include that file."""
    r = subprocess.run(["git", "check-ignore", "-q", "agents/eos/.env"],
                       cwd=str(REPO), capture_output=True, timeout=60)
    assert r.returncode == 0, "agents/eos/.env is NOT ignored -- a credential file is trackable"


def test_reports_dir_stays_ignored():
    r = subprocess.run(["git", "check-ignore", "-q", "agents/eos/reports/x.md"],
                       cwd=str(REPO), capture_output=True, timeout=60)
    assert r.returncode == 0
