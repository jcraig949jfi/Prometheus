"""C-010-T012_1 option 2 (Palamedes, C-010-T013): each bundle's inventory holds only its own launch, so two
launches against ONE cumulative ledger store both pass P-FLAT. Plumbing only (random organisms, tiny seed lists)."""
import os
import unittest

from rso.binding import binding as B
from rso.witness import evaluate as EVW
from rso.witness import run_witness as RW
from rso.witness.tests.test_run_witness import Base, _bundle, _write_config


class TestPerLaunchInventory(Base):
    def test_second_launch_on_a_shared_store_is_flat(self):
        c1 = _write_config(self.d, self.subject, [("S", [101, 102]), ("NULL", [201, 202])], name="c1.json", label="one")
        c2 = _write_config(self.d, self.subject, [("S", [111, 112]), ("NULL", [211, 212])], name="c2.json", label="two")
        out1, r1 = self.launch(c1, out_name="b1")
        out2, r2 = self.launch(c2, out_name="b2")
        self.assertNotEqual(r1["launch_run_id"], r2["launch_run_id"])
        store_rows = self.ledger().inventory()
        self.assertGreater(len([r for r in store_rows if r.get("launch_kind") == B.TOP_LEVEL]), 1)
        for out, res in ((out1, r1), (out2, r2)):
            man, rows, _ = _bundle(out)
            runs = rows[:-1]
            self.assertEqual(rows[-1], {"kind": "TERMINAL", "row_count": len(runs)})
            self.assertTrue(all(r["run_id"] == res["launch_run_id"] or r.get("parent_run_id") == res["launch_run_id"]
                                for r in runs))
            self.assertEqual(EVW.p_flat(runs, man["launch_run_id"]), [])

    def test_helper_drops_foreign_rows_and_recounts(self):
        rows = [{"kind": "RUN", "run_id": "A", "launch_kind": "TOP_LEVEL"},
                {"kind": "RUN", "run_id": "A/n", "parent_run_id": "A", "launch_kind": "RECEIPT"},
                {"kind": "RUN", "run_id": "B", "launch_kind": "TOP_LEVEL"},
                {"kind": "RUN", "run_id": "B/n", "parent_run_id": "B", "launch_kind": "RECEIPT"},
                {"kind": "TERMINAL", "row_count": 4}]
        got = RW.launch_inventory(rows, "A")
        self.assertEqual([r.get("run_id") for r in got[:-1]], ["A", "A/n"])
        self.assertEqual(got[-1], {"kind": "TERMINAL", "row_count": 2})


if __name__ == "__main__":
    unittest.main()
