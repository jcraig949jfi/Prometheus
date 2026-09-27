"""The lane reducer must refuse, not guess: missing units, disagreeing
Attempts, wrong units and wrong answers each block the battery."""

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
if _AETHER not in sys.path:
    sys.path.insert(0, _AETHER)

from observatory import aeth03_lane_reduce as LR         # noqa: E402


def _attempt(path, uid, rsha, lsha, violations=0, host="h"):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"unit_id": uid, "result_sha256": rsha, "legacy_sha256": lsha,
                   "host": {"hostname": host, "platform": "p", "numpy": "n"},
                   "resources": {"wall_seconds": 1.0, "peak_rss_mb": 1.0},
                   "locality_violations": violations}, fh)


def _run(tmp_path, tasks, capsys):
    tf = tmp_path / "tasks.json"
    tf.write_text(json.dumps(tasks))
    code = LR.main(["reduce", "--tasks", str(tf), "--results", str(tmp_path)])
    return code, json.loads(capsys.readouterr().out)


def _task(tid, lane="known"):
    return {"task_id": tid, "lane": lane, "unit_id": "U-" + tid,
            "expected_legacy_sha256": "good"}


def test_complete_battery(tmp_path, capsys):
    _attempt(tmp_path / "T-1__A-001__a.json", "U-T-1", "r1", "good")
    _attempt(tmp_path / "T-1__A-002__b.json", "U-T-1", "r1", "good", host="b")
    code, rep = _run(tmp_path, [_task("T-1")], capsys)
    assert code == 0 and rep["battery"] == "COMPLETE"
    assert rep["tasks"][0]["state"] == "MATCH"


def test_missing_unit_blocks_the_battery(tmp_path, capsys):
    _attempt(tmp_path / "T-1__A-001__a.json", "U-T-1", "r1", "good")
    code, rep = _run(tmp_path, [_task("T-1"), _task("T-2")], capsys)
    assert code != 0 and rep["battery"] == "INCOMPLETE"
    assert rep["blocking"] == ["T-2:MISSING"]


def test_disagreeing_duplicates_raise_a_determinism_alarm(tmp_path, capsys):
    _attempt(tmp_path / "T-1__A-001__a.json", "U-T-1", "r1", "good")
    _attempt(tmp_path / "T-1__A-002__b.json", "U-T-1", "r2", "good", host="b")
    code, rep = _run(tmp_path, [_task("T-1")], capsys)
    assert rep["tasks"][0]["state"] == "DETERMINISM_ALARM" and code != 0


def test_wrong_answer_and_wrong_unit_and_void_instrument(tmp_path, capsys):
    _attempt(tmp_path / "T-1__A-001__a.json", "U-T-1", "r1", "bad")
    _attempt(tmp_path / "T-2__A-001__a.json", "U-OTHER", "r1", "good")
    _attempt(tmp_path / "T-3__A-001__a.json", "U-T-3", "r1", "good", violations=2)
    code, rep = _run(tmp_path, [_task("T-1"), _task("T-2"), _task("T-3")], capsys)
    states = {t["task_id"]: t["state"] for t in rep["tasks"]}
    assert states == {"T-1": "MISMATCH", "T-2": "WRONG_UNIT", "T-3": "INSTRUMENT_VOID"}
    assert code != 0


def test_open_lane_counts_done_without_an_expected_answer(tmp_path, capsys):
    _attempt(tmp_path / "T-9__A-001__a.json", "U-T-9", "r9", None)
    code, rep = _run(tmp_path, [_task("T-9", lane="open")], capsys)
    assert code == 0 and rep["tasks"][0]["state"] == "DONE"
