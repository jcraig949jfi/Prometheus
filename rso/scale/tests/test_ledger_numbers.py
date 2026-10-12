"""Known-answer fixture for rso/scale/ledger_numbers.py (C-013-T020)."""
import json
import os
import tempfile
import unittest

from rso.scale import ledger_numbers as N

ROWS = [
    {"kind": "START", "launch_kind": "TOP_LEVEL", "run_id": "a", "node_id": "n", "start_utc": "2026-10-07T00:00:00Z"},
    {"kind": "START", "launch_kind": "RECEIPT", "run_id": "a/r1", "parent_run_id": "a", "node_id": "n",
     "start_utc": "2026-10-07T00:00:01Z"},
    {"kind": "END", "run_id": "a/r1", "status": "COMPLETED", "cpu_s": 2.5, "artifact_bytes": 100,
     "end_utc": "2026-10-07T00:01:40Z"},
    # TOP_LEVEL "a" has no END of its own: wall falls back to its latest child END (100 s)
    {"kind": "START", "launch_kind": "TOP_LEVEL", "run_id": "b", "node_id": "n", "start_utc": "2026-10-07T01:00:00Z"},
    {"kind": "END", "run_id": "b", "status": "FAILED", "cpu_s": 1.0, "artifact_bytes": 0,
     "end_utc": "2026-10-07T01:00:10Z"},
    {"kind": "START", "launch_kind": "MUTATION_CHILD", "run_id": "b/c1", "parent_run_id": "b", "node_id": "n",
     "start_utc": "2026-10-07T01:00:02Z"},
    {"kind": "REFUSED", "run_id": "c", "cap": "launches", "used": 2, "limit": 2, "at_utc": "2026-10-07T02:00:00Z"},
]


class TestNumbers(unittest.TestCase):
    def test_known_answer(self):
        n = N.numbers(ROWS)
        self.assertEqual(n["top_level_launches"], 2)
        self.assertEqual(n["starts_by_launch_kind"], {"MUTATION_CHILD": 1, "RECEIPT": 1, "TOP_LEVEL": 2})
        self.assertEqual(n["end_status"], {"COMPLETED": 1, "FAILED": 1, "INTERRUPTED": 2})
        self.assertEqual(n["interrupted"], 2)  # "a" (no own END) and "b/c1"
        self.assertEqual(n["refused"], 1)
        self.assertEqual(n["cpu_s_total"], 3.5)
        self.assertEqual(n["artifact_bytes"], 100)
        self.assertEqual(n["top_level_wall_s"], {"n": 2, "sum": 110.0, "median": 55.0, "max": 100.0})

    def test_torn_tail_tolerated_but_mid_corruption_fails(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "L.jsonl")
        with open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps(ROWS[0]) + "\n" + '{"kind": "EN')
        self.assertEqual(len(N.read_rows(p)), 1)
        with open(p, "w", encoding="utf-8") as f:
            f.write('{"kind": "EN\n' + json.dumps(ROWS[0]) + "\n")
        with self.assertRaises(ValueError):
            N.read_rows(p)


if __name__ == "__main__":
    unittest.main()
