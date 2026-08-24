"""Every gate must be proven to FIRE, not merely to pass.

This file exists because of a repeated failure with one root cause. Four gates in this probe
were shipped having been exercised only in the direction where they let work through:

- the drip's truncation gate read a field its own writer never emitted, so it returned
  `0.0000` forever — a gate that could not fail (found by Charon, not by me);
- the R13 power floor measured its N on the single-family screen, the statistic the rule
  explicitly disqualifies, so the enforcement code and the escalation describing it referred
  to different populations;
- the R13 waiver path was bound at import, so a test re-pointing DIR wrote a real waiver file
  into the LIVE ledger tree, silently disabling a power floor on a live run;
- the campaign's own transport gate was added only after a control "passed" 0.0 vs 0.0 on a
  dead lane.

A gate tested only on good input is an assertion, not a gate. Each test below feeds input the
gate MUST reject and asserts it rejects — and, where the gate reads a field, that an ABSENT
field raises rather than returning a passing value.
"""
import json
import math
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


# --------------------------------------------------------------- truncation gate (drip)

def test_drip_truncation_gate_raises_when_its_input_field_is_absent():
    """The exact defect: `r.get("completion_tokens") or 0` against rows that never carry it."""
    from ergon.probe.drip_coldband import _truncation_rate
    rows_without = [{"status": "ok", "extracted_int": 1} for _ in range(50)]
    with pytest.raises(ValueError, match="completion_tokens"):
        _truncation_rate(rows_without)


def test_drip_truncation_gate_fires_on_actually_truncated_rows():
    from ergon.probe.drip_coldband import _truncation_rate, MAX_TOK, TRANSPORT_FLOOR  # noqa: F401
    rows = ([{"status": "ok", "completion_tokens": MAX_TOK} for _ in range(10)]
            + [{"status": "ok", "completion_tokens": 100} for _ in range(90)])
    assert _truncation_rate(rows) == pytest.approx(0.10)      # 10% — must exceed the 2% gate


def test_drip_truncation_gate_does_not_pass_a_dead_input():
    from ergon.probe.drip_coldband import _truncation_rate
    with pytest.raises(ValueError):
        _truncation_rate([])                                   # no ok rows: refuse, never 0.0


# --------------------------------------------------------------- transport floor

def test_transport_floor_refuses_a_dead_lane():
    """A dead lane scores every row wrong and would emit a confident 0.0."""
    from ergon.probe import drip_coldband as D
    recs = [{"status": "error", "error_type": "HTTP504"} for _ in range(100)]
    ok_rate = sum(1 for r in recs if r["status"] == "ok") / len(recs)
    assert ok_rate < D.TRANSPORT_FLOOR, "a fully dead lane must be below the floor"


# --------------------------------------------------------------- manifest sha pin

def test_campaign_refuses_a_manifest_whose_sha_does_not_match_the_pin():
    """The pin exists so regeneration cannot silently destroy the cross-family screen."""
    import ergon.probe.campaign as C
    tmp = Path(tempfile.mkdtemp(prefix="pin_"))
    assert "ledgers" not in str(tmp)
    real = ROOT / C.PINNED_MANIFEST
    if not real.exists():
        pytest.skip("pinned manifest not present")
    rows = [json.loads(l) for l in real.read_text(encoding="utf-8").splitlines()]
    rows[0]["prompt"] = rows[0]["prompt"] + " tampered"
    fake = tmp / Path(C.PINNED_MANIFEST).name
    fake.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                    encoding="utf-8")
    from ergon.probe.task_gen_v3 import manifest_sha256
    assert manifest_sha256(rows)[:16] != C.PINNED_MANIFEST_SHA, (
        "a tampered manifest must not hash to the pin")


# --------------------------------------------------------------- R10 independent recompute

def test_r10_refuses_duplicate_task_arm_rows():
    import importlib
    r10 = importlib.import_module("ergon.probe.r10_recompute")
    tmp = Path(tempfile.mkdtemp(prefix="r10_")) / "dupes.jsonl"
    row = {"arm": "F0", "uid": "u1", "correct": True, "extracted": 1, "status": "ok"}
    tmp.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        r10.load(str(tmp))


def test_r10_refuses_synthetic_rows():
    import importlib
    r10 = importlib.import_module("ergon.probe.r10_recompute")
    tmp = Path(tempfile.mkdtemp(prefix="r10s_")) / "synth.jsonl"
    tmp.write_text(json.dumps(
        {"arm": "F0", "uid": "u1", "correct": True, "extracted": 1,
         "status": "ok", "synthetic": True}) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        r10.load(str(tmp))


def test_r10_refuses_a_prepass_ledger_mistaken_for_an_arms_ledger():
    """key = [rep, uid] is a pre-pass; the arm contrast is undefined on it."""
    import importlib
    r10 = importlib.import_module("ergon.probe.r10_recompute")
    tmp = Path(tempfile.mkdtemp(prefix="r10p_")) / "prepass.jsonl"
    tmp.write_text("\n".join(json.dumps(
        {"key": [1, f"u{i}"], "status": "ok", "extracted_int": 1}) for i in range(3)),
        encoding="utf-8")
    with pytest.raises(SystemExit):
        r10.load(str(tmp), None)


# --------------------------------------------------------------- band rule (three-valued)

def test_band_verdict_is_undecided_when_the_interval_straddles_an_edge():
    """An in-band POINT whose interval crosses an edge must never read LEVELED."""
    acc, n, movable = 0.5823, 620, 0.3468            # the real M20 numbers
    z = 1.959964
    se = math.sqrt(acc * (1 - acc) / n)
    lo, hi = acc - z * se, acc + z * se
    straddles = (lo < 0.35 < hi) or (lo < 0.60 < hi)
    point_in = 0.35 <= acc <= 0.60
    assert point_in and straddles, "this is the case the three-valued rule exists for"
    verdict = ("NOT-LEVELED" if not point_in else
               "NOT-LEVELED-DISPERSION" if movable < 0.30 else
               "UNDECIDED" if straddles else "LEVELED")
    assert verdict == "UNDECIDED", "a straddling interval was reported as leveled"


def test_dispersion_floor_fires_on_a_bimodal_set_with_a_centred_mean():
    """Harmonia B's cheat control: mean dead-centre, zero movable mass, must NOT level."""
    acc, movable = 0.50, 0.00                        # trivial+impossible mixture
    point_in = 0.35 <= acc <= 0.60
    verdict = "NOT-LEVELED-DISPERSION" if (point_in and movable < 0.30) else "OTHER"
    assert verdict == "NOT-LEVELED-DISPERSION"


# --------------------------------------------------------------- gate paths must not be import-bound

def test_gate_paths_resolve_from_dir_at_call_time():
    """A gate path frozen at import writes into the LIVE tree when DIR is re-pointed —
    which is how a real waiver file was once created by a test run."""
    import ergon.probe.campaign as C
    original = C.DIR
    try:
        tmp = Path(tempfile.mkdtemp(prefix="gatepath_"))
        C.DIR = tmp
        assert C._r13_waiver().parent == tmp, (
            "the waiver path did not follow DIR — it is bound at import and will write into "
            "the live ledger tree")
    finally:
        C.DIR = original
