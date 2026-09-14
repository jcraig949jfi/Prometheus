"""C9 evidence: the committed run files carry the numbers the ruling cites,
and the harness classifies outcomes the way the ruling reads them.

Controls:
  positive   the three committed runs exist, are the same build + load, and
             the C: runs are clean while the F: run carries the stall
  ruling     the exact figures quoted in FINDING.md are what the files say
             (burst wall time, producer p95/max, WAL max, slow-call count)
  H1 kill    the pinned arm is not separable from asdeployed on C: (both
             clean) and the WAL never exceeds ~1 MB anywhere
  cheat      the harness's outcome classifier maps an EngineError 500 to
             http_500, a socket timeout to timeout, and a success to ok --
             so a run reporting 'errors: {}' has actually looked
  secrets    no token material in any evidence file
"""
from __future__ import annotations

import json
import os
import socket
import sys

_ENGINE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ENGINE_ROOT not in sys.path:
    sys.path.insert(0, _ENGINE_ROOT)
sys.path.insert(0, os.path.join(_ENGINE_ROOT, "deploy"))
sys.path.insert(0, os.path.join(os.path.dirname(_ENGINE_ROOT), "SerendipityFoundryClient"))

EVID = os.path.join(_ENGINE_ROOT, "deploy", "C9_BURST_STALL_2026-09-11")
RUNS = ("run1_C_asdeployed", "run1_C_pinned", "run2_F_asdeployed")


def _load(name):
    with open(os.path.join(EVID, name + ".json"), encoding="ascii") as fh:
        return json.load(fh)


def test_positive_three_runs_same_build_same_load():
    runs = {n: _load(n) for n in RUNS}
    builds = {r["engine"]["engine_source_hash"] for r in runs.values()}
    assert builds == {"sha256:5380cb90f42dc83b4c6bd4710566e92c3ca2a3d154eacca1069cbc40d187876e"}
    for r in runs.values():
        assert (r["burst"], r["serial_rows"], r["quiet_rows"]) == (600, 12, 8)
        assert r["summary"]["burst/producer"]["n"] == 1200
        assert all(v["errors"] == {} for v in r["summary"].values())


def test_ruling_numbers_are_what_the_files_say():
    c = _load("run1_C_asdeployed")
    p = _load("run1_C_pinned")
    f = _load("run2_F_asdeployed")
    assert c["t_burst_s"] == 20.6 and p["t_burst_s"] == 26.0 and f["t_burst_s"] == 633.8
    assert c["summary"]["burst/producer"]["p95_s"] == 0.033
    assert f["summary"]["burst/producer"]["p95_s"] == 2.674
    assert f["summary"]["burst/producer"]["max_s"] == 15.154
    assert f["summary"]["burst/reader"]["max_s"] == 14.977
    assert len(f["slow_calls"]) == 53 and len(c["slow_calls"]) == 0 and len(p["slow_calls"]) == 0
    assert f["t_burst_s"] / c["t_burst_s"] > 30


def test_h1_kill_pinned_arm_not_separable_and_wal_stays_small():
    c = _load("run1_C_asdeployed")
    p = _load("run1_C_pinned")
    for r in (c, p):
        assert r["summary"]["burst/producer"]["over_10s"] == 0
        assert r["summary"]["burst/producer"]["p95_s"] < 0.05
    assert abs(c["t_burst_s"] - p["t_burst_s"]) < 10
    for n in RUNS:
        assert _load(n)["wal_max_bytes"] < 2 * 1024 * 1024


def test_f_run_stall_shape_is_paired_freezes_of_producer_and_reader():
    f = _load("run2_F_asdeployed")
    slow = [s for s in f["slow_calls"] if s["dt_s"] >= 5]
    who = {s["who"] for s in slow}
    assert {"producer", "reader"} <= who
    # freezes come in producer+reader pairs within 1 s of each other
    prod = sorted(s["at_s"] for s in slow if s["who"] == "producer")
    read = sorted(s["at_s"] for s in slow if s["who"] == "reader")
    paired = sum(1 for a in prod if any(abs(a - b) <= 1.0 for b in read))
    assert paired >= len(prod) // 2


def test_cheat_control_outcome_classifier():
    from c9_burst_stall import Rec
    from sfclient.client import EngineError
    rec = Rec()
    rec.phase = "t"
    _, ok = rec.call("x", "op", lambda: 1)
    def boom():
        raise EngineError(500, {"error": "internal_error"})
    _, e500 = rec.call("x", "op", boom)
    def slow():
        raise socket.timeout("timed out")
    _, to = rec.call("x", "op", slow)
    assert (ok, e500, to) == ("ok", "http_500", "timeout")
    assert len(rec.calls) == 3


def test_no_credential_material_in_evidence():
    for n in RUNS:
        text = open(os.path.join(EVID, n + ".json"), encoding="ascii").read().lower()
        assert "gen2_" not in text and "bearer" not in text and "token" not in text


# -- after the move (2026-09-12): the acceptance criterion as a test ---------
AFTER = "run3_D_asdeployed_after_move"


def test_acceptance_after_move_no_paired_freezes_and_nvme_regime():
    """Operator's criterion 2026-09-12: no paired multi-second freeze
    pattern; zero or bounded calls over 5 s; producer and reader latency
    back in the NVMe-class regime measured in C9 run1."""
    before = _load("run2_F_asdeployed")
    after = _load(AFTER)
    ref = _load("run1_C_asdeployed")
    assert after["engine"]["engine_source_hash"] == before["engine"]["engine_source_hash"]
    assert after["copy_from"].lower().startswith("d:/")
    assert len([s for s in after["slow_calls"] if s["dt_s"] >= 5]) == 0
    assert sum(v["over_10s"] for v in after["summary"].values()) == 0
    for who in ("burst/producer", "burst/reader"):
        assert after["summary"][who]["p95_s"] <= 2 * ref["summary"][who]["p95_s"] + 0.02
        assert after["summary"][who]["max_s"] < 1.0
    assert after["t_burst_s"] < before["t_burst_s"] / 20
    assert after["wal_max_bytes"] < 2 * 1024 * 1024
