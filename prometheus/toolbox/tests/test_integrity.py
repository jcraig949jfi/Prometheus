"""Forensic integrity of the receipt file itself (overnight C10): truncation, corruption and edits must be
DETECTED and COUNTED, never silently dropped; a strict read refuses, a scan reports."""
from __future__ import annotations

import json

import pytest

from prometheus.toolbox import receipt as R
from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.ref.players import random_statemachine
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.backends.local import execute, lower

REG = default_registry()


def _write(tmp_path, n_seeds=3):
    e = Experiment(family="integ", world=ref("world.integer.v1", world_seed=1), substrate=ref("substrate.flat.v1"), players=[random_statemachine(1).manifest()],
                   seed_policy={"base": 1, "n_seeds": n_seeds}, budget={"episodes": 1, "horizon": 8})
    execute(lower(e, REG).job, tmp_path / "r.jsonl", REG)
    return tmp_path / "r.jsonl"


def test_truncated_last_line_is_reported_not_dropped(tmp_path):
    p = _write(tmp_path); raw = p.read_bytes()
    p.write_bytes(raw[:-40])                                   # mid-record truncation (a crash during the last flush)
    with pytest.raises(R.ReceiptError):
        R.read_all(p)
    scan = R.scan(p)
    assert scan["valid"] == 3 and scan["defects"] == [{"line": 4, "defect": "TRUNCATED_OR_MALFORMED_JSON"}]


def test_edited_record_in_the_middle_is_named_by_line(tmp_path):
    p = _write(tmp_path); lines = p.read_text(encoding="utf-8").splitlines()
    rec = json.loads(lines[1]); rec["seed"] = 999; lines[1] = json.dumps(rec, sort_keys=True, separators=(",", ":"))
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    scan = R.scan(p)
    assert scan["valid"] == 3 and scan["defects"][0]["line"] == 2 and scan["defects"][0]["defect"].startswith("RECEIPT_ID_MISMATCH")


def test_duplicate_receipt_ids_are_reported(tmp_path):
    p = _write(tmp_path); lines = p.read_text(encoding="utf-8").splitlines()
    p.write_text("\n".join(lines + [lines[0]]) + "\n", encoding="utf-8")
    scan = R.scan(p)
    assert any(d["defect"] == "DUPLICATE_RECEIPT_ID" for d in scan["defects"]) and scan["valid"] == 4


def test_scan_of_a_clean_file_has_no_defects(tmp_path):
    p = _write(tmp_path)
    assert R.scan(p) == {"path": str(p), "lines": 4, "valid": 4, "defects": [], "receipt_ids": R.scan(p)["receipt_ids"]}
