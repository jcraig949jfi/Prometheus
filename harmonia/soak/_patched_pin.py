"""P54's pin plus exactly two lines — the proposed patch, as a real file.

ADDED vs P54: json.dumps(None) and {"examinee": "a"}. Everything else, including
the counted-skip assertion, is P54's. Proposal only; Aporia's file is untouched.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.abspath("harmonia/experiments"))
from run_zoo_matrix import Checkpoint  # noqa: E402


def _mk(lines):
    p = Path(tempfile.mkdtemp()) / "ck.jsonl"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def test_shapes():
    p = _mk([json.dumps({"examinee": "a", "probe_id": "p1"}),
             '{"truncat',
             json.dumps({"wrong": "shape"}),
             json.dumps({}),
             json.dumps({"unrelated": 1, "keys": 2}),
             json.dumps([1, 2, 3]),
             json.dumps("just a string"),
             json.dumps(None),                    # ADDED: the only shape that tests isinstance
             json.dumps({"examinee": "a"}),       # ADDED: the only shape that tests the probe_id check
             json.dumps({"examinee": "b", "probe_id": "p2"})])
    ck = Checkpoint(p)
    assert len(ck.records) == 2, ck.records
    assert ck.done == {("a", "p1"), ("b", "p2")}
    assert getattr(ck, "n_skipped_malformed", 0) == 7


if __name__ == "__main__":
    test_shapes()
    print("patched pin: OK")
