"""Pinned regression for the HARMA-P18 Checkpoint defect (fixed P44, fault-injected
and verified by HARMA-P28, PINNED here per its finding that effectiveness without a
committed red-able test is the P38 greenness lesson again).

Pins: truncated line tolerated; well-formed-but-wrong shapes (missing keys, empty
object, unrelated keys, non-object JSON) SKIPPED with n_skipped_malformed counted;
valid records still resume. Run: python -m pytest harmonia/experiments/test_checkpoint_robustness.py -q
"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_zoo_matrix import Checkpoint  # noqa: E402


def _mk(lines):
    d = Path(tempfile.mkdtemp())
    p = d / "ck.jsonl"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def test_all_harma_p18_shapes_survive_and_are_counted():
    p = _mk([json.dumps({"examinee": "a", "probe_id": "p1"}),
             '{"truncat',                        # half-written line from a kill
             json.dumps({"wrong": "shape"}),     # well-formed, missing keys
             json.dumps({}),                     # empty object
             json.dumps({"unrelated": 1, "keys": 2}),
             json.dumps([1, 2, 3]),              # non-object JSON
             json.dumps("just a string"),
             json.dumps({"examinee": "b", "probe_id": "p2"})])
    ck = Checkpoint(p)
    assert len(ck.records) == 2, ck.records
    assert ck.done == {("a", "p1"), ("b", "p2")}
    assert getattr(ck, "n_skipped_malformed", 0) == 5


def test_clean_checkpoint_unchanged():
    p = _mk([json.dumps({"examinee": "a", "probe_id": "p1"})])
    ck = Checkpoint(p)
    assert len(ck.records) == 1 and getattr(ck, "n_skipped_malformed", 0) == 0


if __name__ == "__main__":
    test_all_harma_p18_shapes_survive_and_are_counted()
    test_clean_checkpoint_unchanged()
    print("2/2 checkpoint pins pass")
