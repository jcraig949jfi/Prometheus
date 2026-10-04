"""Tests for the semantic mutation runner (C-004-T017). Plan s5 outcome classes; stdlib only.

The toy module and its frozen suite are written to a temporary directory, never under rso/slice001.
The fire test is the four control edits of the packet: a killing edit, a surviving edit, a syntax-error
edit and a timeout edit. Every launch here is a mutation child and is charged to the CPU cap (OP-1).
"""
import hashlib
import json
import os
import shutil
import tempfile
import unittest

from rso.slice001 import mutation as M

HERE = os.path.dirname(os.path.abspath(__file__))
SLICE = os.path.dirname(HERE)

TOY = '''"""Toy module for the mutation fire test."""


def add(a, b):
    return a + b


def scale(x):
    return x * 2


def double_abs(x):
    if x < 0:
        x = -x
    return x + x
'''

TOY_TESTS = '''import unittest
from toypkg import arith


class T(unittest.TestCase):
    def test_add(self):
        self.assertEqual(arith.add(2, 3), 5)

    def test_double_abs(self):
        self.assertEqual(arith.double_abs(-3), 6)
        self.assertEqual(arith.double_abs(4), 8)
'''

TIMEOUT_S = 3


def edit(eid, find, replace, fault="toy fault", witness=None, **kw):
    e = {"edit_id": eid, "path": "toypkg/arith.py", "module": "toypkg.arith", "find": find,
         "replace": replace, "intended_fault": fault}
    if witness is not None:
        e["witness"] = {"expr": witness}
    e.update(kw)
    return e


KILL = edit("C1-KILL", "return a + b", "return a - b", "add subtracts")
SURVIVE = edit("C2-SURVIVE", "return x * 2", "return x * 3", "scale untested", witness="m.scale(1)")
SYNTAX = edit("C3-SYNTAX", "return a + b", "return a +", "syntax error")
TIMEOUT = edit("C4-TIMEOUT", "    return a + b",
               "    import time\n    time.sleep(%d)\n    return a + b" % (TIMEOUT_S * 20), "hangs")


def tree_hashes(root):
    out = {}
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x != "__pycache__"]
        for f in files:
            p = os.path.join(d, f)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, root)] = hashlib.sha256(fh.read()).hexdigest()
    return out


class ToyCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="argus_t017_")
        pkg = os.path.join(self.tmp, "toypkg")
        os.mkdir(pkg)
        for name, text in (("__init__.py", ""), ("arith.py", TOY), ("test_arith.py", TOY_TESTS)):
            with open(os.path.join(pkg, name), "w", encoding="utf-8", newline="\n") as f:
                f.write(text)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write_edits(self, edits, name="edits.json"):
        p = os.path.join(self.tmp, name)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"schema": M.EDITS_SCHEMA, "edits": edits}, f)
        return p

    def run_edits(self, edits, **kw):
        rows_path = os.path.join(self.tmp, "rows_%d.jsonl" % len(os.listdir(self.tmp)))
        kw.setdefault("timeout_s", TIMEOUT_S)
        kw.setdefault("require_committed", False)
        result = M.run(self.write_edits(edits), root=self.tmp, suite=["toypkg.test_arith"],
                       rows_path=rows_path, **kw)
        return result, M.load_rows(rows_path)

    @staticmethod
    def by_id(rows):
        return {r["edit_id"]: r for r in rows if r["row"] == "edit"}


class TestFireControls(ToyCase):
    """The packet's RED/fire test: each control edit gets its expected class."""

    def test_four_controls_and_tree_unchanged(self):
        before_slice = tree_hashes(SLICE)
        before_toy = tree_hashes(self.tmp)
        result, rows = self.run_edits([KILL, SURVIVE, SYNTAX, TIMEOUT])
        got = {k: v["status"] for k, v in self.by_id(rows).items()}
        self.assertEqual(got, {"C1-KILL": "KILLED", "C2-SURVIVE": "SURVIVED",
                               "C3-SYNTAX": "SYNTAX_ERROR", "C4-TIMEOUT": "TIMEOUT"})
        s = result["summary"]
        self.assertEqual((s["proposed"], s["applicable"], s["duplicate"], s["executed"], s["killed"],
                          s["survived"], s["equivalent"], s["error"], s["timeout"]),
                         (4, 4, 0, 3, 1, 1, 0, 1, 1))
        # no file under rso/slice001 modified, and the target module on disk untouched (in-memory edits)
        self.assertEqual(tree_hashes(SLICE), before_slice)
        after_toy = tree_hashes(self.tmp)
        for k, v in before_toy.items():
            self.assertEqual(after_toy[k], v, k)

    def test_baseline_row_first_and_terminal_row_last(self):
        _, rows = self.run_edits([KILL])
        self.assertEqual([r["row"] for r in rows], ["header", "baseline", "edit", "terminal"])
        self.assertEqual(rows[1]["status"], "PASSED")
        self.assertEqual(rows[-1]["edit_rows"], 1)


class TestClasses(ToyCase):
    def test_errors_are_not_kills(self):
        imp = edit("E-IMPORT", "def add(a, b):", "raise RuntimeError('boom')\n\n\ndef add(a, b):",
                   "module fails at import")
        terr = edit("E-TESTERR", "return a + b", "return undefined_name", "NameError in test run")
        result, rows = self.run_edits([imp, terr])
        got = self.by_id(rows)
        self.assertEqual(got["E-IMPORT"]["status"], "IMPORT_ERROR")
        self.assertEqual(got["E-TESTERR"]["status"], "TEST_ERROR")
        s = result["summary"]
        self.assertEqual((s["killed"], s["error"], s["executed"]), (0, 2, 2))

    def test_not_applicable_and_duplicate(self):
        na = edit("N1", "return a * b", "return a / b")
        noop = edit("N2", "return a + b", "return a + b")
        dup = edit("D1", "return a + b", "return a - b")
        result, rows = self.run_edits([KILL, na, noop, dup])
        got = self.by_id(rows)
        self.assertEqual(got["N1"]["status"], "NOT_APPLICABLE")
        self.assertEqual(got["N2"]["status"], "NOT_APPLICABLE")
        self.assertEqual(got["D1"]["status"], "DUPLICATE")
        self.assertEqual(got["D1"]["duplicate_of"], "C1-KILL")
        s = result["summary"]
        self.assertEqual((s["proposed"], s["applicable"], s["duplicate"], s["executed"]), (4, 2, 1, 1))

    def test_ambiguous_find_is_not_applicable_without_occurrence(self):
        amb = edit("A1", "x", "y")
        result, rows = self.run_edits([amb])
        self.assertEqual(self.by_id(rows)["A1"]["status"], "NOT_APPLICABLE")
        occ = edit("A2", "return x + x", "return x + x + 0", occurrence=1)
        result, rows = self.run_edits([occ])
        self.assertEqual(self.by_id(rows)["A2"]["status"], "SURVIVED")


class TestSurvivorsAndEquivalence(ToyCase):
    def test_survivor_with_witness_differs_is_resolved_non_equivalent(self):
        result, rows = self.run_edits([SURVIVE])
        r = self.by_id(rows)["C2-SURVIVE"]
        self.assertEqual(r["witness"]["result"], "DIFFERS")
        self.assertEqual((r["witness"]["original"], r["witness"]["mutant"]), ("2", "3"))
        self.assertEqual(r["equivalence"], "NOT_EQUIVALENT_WITNESSED")
        self.assertEqual(result["summary"]["unresolved_survivors"], 0)

    def test_no_observed_difference_is_unresolved_not_equivalent(self):
        same = edit("S2", "return x + x", "return 2 * x", "equivalent rewrite?", witness="m.double_abs(5)")
        bare = edit("S3", "return x * 2", "return x * 4", "no witness supplied")
        result, rows = self.run_edits([same, bare])
        got = self.by_id(rows)
        self.assertEqual(got["S2"]["status"], "SURVIVED")
        self.assertEqual(got["S2"]["witness"]["result"], "NO_DIFFERENCE_OBSERVED")
        self.assertEqual(got["S2"]["equivalence"], "UNRESOLVED")
        self.assertIsNone(got["S3"]["witness"])
        self.assertEqual(got["S3"]["equivalence"], "UNRESOLVED")
        s = result["summary"]
        self.assertEqual((s["survived"], s["equivalent"], s["unresolved_survivors"]), (2, 0, 2))

    def test_equivalence_only_by_adjudication(self):
        same = edit("S2", "return x + x", "return 2 * x", "equivalent rewrite?")
        _, rows = self.run_edits([same, SURVIVE])
        s = M.summarize(rows, adjudications={"S2": "EQUIVALENT"})
        self.assertEqual((s["equivalent"], s["unresolved_survivors"]), (1, 0))
        with self.assertRaises(M.MutationError):          # a witnessed difference cannot be equivalent
            M.summarize(rows, adjudications={"C2-SURVIVE": "EQUIVALENT"})
        with self.assertRaises(M.MutationError):          # only survivors are adjudicated
            M.summarize(rows, adjudications={"NOPE": "EQUIVALENT"})


class TestProtocol(ToyCase):
    def test_baseline_failure_executes_nothing(self):
        with open(os.path.join(self.tmp, "toypkg", "arith.py"), "w", encoding="utf-8") as f:
            f.write(TOY.replace("return a + b", "return a - b"))
        result, rows = self.run_edits([KILL])
        self.assertEqual(rows[1]["status"], "FAILED")
        self.assertEqual(self.by_id(rows)["C1-KILL"]["status"], "NOT_RUN_BASELINE")
        self.assertEqual(result["summary"]["executed"], 0)
        self.assertEqual(result["summary"]["killed"], 0)

    def test_rows_file_never_overwritten(self):
        p = os.path.join(self.tmp, "rows.jsonl")
        with open(p, "w") as f:
            f.write("{}\n")
        with self.assertRaises(M.MutationError):
            M.run(self.write_edits([KILL]), root=self.tmp, suite=["toypkg.test_arith"], rows_path=p,
                  timeout_s=TIMEOUT_S, require_committed=False)

    def test_cpu_cap_stops_and_keeps_partial(self):
        result, rows = self.run_edits([KILL, SURVIVE], max_child_seconds=0)
        got = self.by_id(rows)
        self.assertEqual(got["C1-KILL"]["status"], "NOT_RUN_CAP")
        self.assertEqual(got["C2-SURVIVE"]["status"], "NOT_RUN_CAP")
        self.assertEqual(rows[-1]["row"], "terminal")
        self.assertTrue(result["summary"]["cap_exhausted"])

    def test_edits_schema(self):
        for bad in ([dict(KILL, extra=1)], [dict(KILL, find="")], [KILL, KILL],
                    [dict(KILL, module="toypkg.other")], [dict(KILL, intended_fault="")]):
            with self.assertRaises(M.MutationError):
                M.load_edits(self.write_edits(bad))

    def test_uncommitted_edits_file_refused(self):
        with self.assertRaises(M.MutationError):
            M.run(self.write_edits([KILL]), root=self.tmp, suite=["toypkg.test_arith"],
                  rows_path=os.path.join(self.tmp, "r.jsonl"), timeout_s=TIMEOUT_S)

    def test_edit_counts_vocabulary(self):
        # the stage record's edits object (draft B B4.1) uses exactly these keys
        self.assertEqual(M.EDIT_COUNTS, ("proposed", "applicable", "duplicate", "executed", "killed",
                                         "survived", "equivalent", "error", "timeout"))


if __name__ == "__main__":
    unittest.main()
