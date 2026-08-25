"""End-to-end dry-run of the campaign state machine against a mocked transport.

Why this exists: P2-P5 shipped without ever executing a line. A dry-run against a fake
solver found three defects in one pass — (a) P2 requested its F0 leg twice and doubled its
task list, burning 468 free-lane calls to write rows it already had; (b) the HOLD before P4
never fired, because a duplicate-inflated coverage denominator made P2 look incomplete and
returned early; (c) the ledger shape was unreadable by `r10_recompute.py`, which would have
blocked the independent recomputation at the END of a weeks-long campaign.

FIXTURE DISCIPLINE: mocked responses are transport fixtures, never data. The temp DIR is
asserted to be outside the real ledger tree, and no artifact this test writes is admissible
as a result.
"""
import json
import random
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


class _Resp:
    def __init__(self, text):
        self.status, self.error_type, self.text = "ok", None, text
        self.latency_s, self.ts_utc = 1.0, "2026-08-21T00:00:00+00:00"
        self.host, self.executor = "TESTHOST", "dryrun"
        self.prompt_tokens, self.completion_tokens, self.usd = 50, 900, 0.0


def _harness(tmp, signoff, waive_r13=True):
    """Run the campaign once against a mock tuned to land the band read IN band."""
    import ergon.probe.campaign as C

    rng = random.Random(11)
    gold_by_nums = {}

    def fake_call(_name, prompt, **_kw):
        if "Say OK" in prompt:
            return _Resp("OK")
        g = gold_by_nums.get(tuple(re.findall(r"\b\d{5,}\b", prompt)))
        if g is not None and rng.random() < 0.37:
            return _Resp(f"Reasoning...\n\nANSWER: {g}")
        return _Resp(f"Reasoning...\n\nANSWER: {rng.randint(0, 5)}")

    C.call = fake_call
    C.CALL_SPACING_S = 0.0
    C.DIR = tmp
    C.HOLD_FILE = tmp / "RE_REVIEW_SIGNOFF"
    C.MANIFEST_N = 200          # below this a LEVELED read is arithmetically unreachable
    C.BATCH_CAP = 10 ** 6
    for r in C.manifest():
        gold_by_nums[tuple(re.findall(r"\b\d{5,}\b", r["prompt"]))] = r["gold_int"]
    if signoff:
        C.HOLD_FILE.write_text("dryrun", encoding="utf-8")
    if waive_r13:
        # the dry-run manifest is deliberately small; this is a STATE-MACHINE test, so the
        # power floor is waived explicitly here rather than silently lowered in the code.
        C._r13_waiver().write_text("dryrun: state-machine test", encoding="utf-8")
    C.main()
    return [json.loads(l) for l in
            (tmp / "campaign_log.jsonl").read_text(encoding="utf-8").splitlines()]


@pytest.fixture()
def tmpdir_outside_ledgers():
    tmp = Path(tempfile.mkdtemp(prefix="campaign_dry_"))
    assert "ledgers" not in str(tmp), "dry-run must never write into the real ledger tree"

    # A test once wrote an R13 waiver into the LIVE campaign directory because the gate path
    # was bound at import instead of resolved from DIR. A stray waiver silently disables a
    # power floor on a real run, so the fixture proves the live tree is untouched.
    #
    # PREDICATE CORRECTED 2026-08-25 (Harmonia B, exit review #3). This asserted ABSOLUTE
    # ABSENCE, which cannot distinguish "a test leaked a gate file" from "the independent seat
    # legitimately signed off". The moment a real RE_REVIEW_SIGNOFF existed the suite went red,
    # leaving two bad options: run red for the whole authorized campaign, or delete a real
    # signoff to green the suite — silently revoking a gate to satisfy a test. The guard's
    # actual intent is "no TEST may create these", so it now snapshots before and compares
    # after. Strictly stronger: it still catches creation, and additionally catches a test
    # MUTATING a signoff that already exists.
    live = ROOT / "ergon/probe/ledgers/campaign"
    guarded = ("R13_POWER_FLOOR_WAIVED", "RE_REVIEW_SIGNOFF")
    before = {f: (live / f).read_bytes() if (live / f).exists() else None for f in guarded}

    yield tmp

    for stray in guarded:
        after = (live / stray).read_bytes() if (live / stray).exists() else None
        if before[stray] is None:
            assert after is None, (
                f"a test CREATED {stray} in the LIVE ledger tree — this disables a real gate")
        else:
            assert after == before[stray], (
                f"a test MUTATED the live {stray} — a real gate was altered by a test run")


def test_campaign_holds_before_p4_then_completes(tmpdir_outside_ledgers):
    tmp = tmpdir_outside_ledgers

    log = _harness(tmp, signoff=False)
    phases = [e.get("phase") for e in log if e.get("phase")]
    events = [e.get("event") for e in log if e.get("event")]

    # P1-P3 run; P4 must NOT, and the hold must be recorded rather than silent.
    assert "P1" in phases and "P2" in phases and "P3" in phases
    assert "P4" not in phases, "P4 fired without a re-review sign-off"
    assert "holding" in events

    # every phase reached full coverage of its UNIQUE work set
    for e in log:
        if e.get("coverage"):
            done, want = e["coverage"].split("/")
            assert done == want, f"{e.get('phase')} incomplete: {e['coverage']}"

    # no phase may send more calls than it has unique rows to fill: duplicate pairs are
    # wasted free-lane quota AND duplicate ledger rows that R10 refuses.
    for e in log:
        if e.get("sent") is not None and e.get("coverage"):
            want = int(e["coverage"].split("/")[1])
            assert e["sent"] <= want, (
                f"{e.get('phase')} sent {e['sent']} calls for {want} rows — duplicate dispatch")

    log2 = _harness(tmp, signoff=True)
    assert "P4" in [e.get("phase") for e in log2 if e.get("phase")]
    assert "campaign_complete" in [e.get("event") for e in log2 if e.get("event")]


def test_band_read_is_three_valued_and_carries_scope(tmpdir_outside_ledgers):
    tmp = tmpdir_outside_ledgers
    _harness(tmp, signoff=True)
    read = json.loads((tmp / "p1_bandread.json").read_text(encoding="utf-8"))

    assert read["leveling_verdict"] in {
        "LEVELED", "NOT-LEVELED", "NOT-LEVELED-DISPERSION",
        "UNDECIDED-UNDERPOWERED", "UNDECIDED-RESOLVES-TO-FAILURE"}
    # §3.1 ruling 3: manifest-level primary, Wilson reported beside it
    assert read["manifest_interval_95"] and read["wilson_interval_95"]
    # an in-band point whose interval straddles an edge is never silently LEVELED
    lo, hi = read["manifest_interval_95"]
    if (lo < 0.35 < hi) or (lo < 0.60 < hi):
        assert read["leveling_verdict"].startswith("UNDECIDED")
    assert read["n_required_for_decidability"] is not None
    assert "scope_caveat" in read and "D0" in read["scope_caveat"]      # C6 travels on artifacts


def test_r10_reads_the_campaign_arms_ledger(tmpdir_outside_ledgers):
    """The independent recomputation must work on what the campaign actually writes."""
    tmp = tmpdir_outside_ledgers
    _harness(tmp, signoff=True)
    sys.path.insert(0, str(ROOT / "ergon" / "probe"))
    import importlib
    r10 = importlib.import_module("ergon.probe.r10_recompute")
    # the campaign now loads a PINNED manifest (Ruling 2 re-pin) rather than generating one
    import ergon.probe.campaign as C
    manifest_path = ROOT / C.PINNED_MANIFEST
    if not manifest_path.exists():
        manifest_path = tmp / f"campaign_manifest_{C.RUNG}_n{C.MANIFEST_N}.jsonl"
    rows = r10.load(str(tmp / "p4_arms.jsonl"), str(manifest_path))
    assert rows and all("arm" in r and "uid" in r and "correct" in r for r in rows)
    arms = {r["arm"] for r in rows}
    assert {"F0", "F-null", "F-prom-retrieved"} <= arms


def test_r13_power_floor_halts_before_any_arm(tmpdir_outside_ledgers):
    """R13: 'replenish before any arm runs.' A run below the floor must spend nothing on arms.

    This guards the failure this rule exists to prevent: ~2,750 free-lane calls collected into
    an INCONCLUSIVE-UNDERPOWERED verdict class that, per §6.3, never routes Path gamma.
    """
    tmp = tmpdir_outside_ledgers
    log = _harness(tmp, signoff=True, waive_r13=False)
    phases = [e.get("phase") for e in log if e.get("phase")]
    assert "P1" in phases, "the band read must still run — it is what measures the floor"
    for arm_phase in ("P2", "P3", "P4", "P5"):
        assert arm_phase not in phases, f"{arm_phase} ran below the R13 power floor"
    ends = [e for e in log if e.get("verdict") == "R13-POWER-FLOOR-UNMET"]
    assert ends, "the halt must be recorded, not silent"
    assert ends[0]["n_post_screen"] < ends[0]["floor"]
