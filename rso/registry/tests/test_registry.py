import copy
import os
import tempfile
import unittest

from rso.registry import registry as R
from rso.registry.entries import ENTRIES


def _tree(files):
    root = tempfile.mkdtemp()
    for p, data in files.items():
        os.makedirs(os.path.dirname(os.path.join(root, p)), exist_ok=True)
        with open(os.path.join(root, p), "wb") as f:
            f.write(data)
    return root


def _entry(name, files, deps=()):
    e = {k: [] for k in R.REQUIRED}
    e.update(name=name, version="v", owner="o", files=list(files), interface="i", stage="AUTHOR_TESTED",
             qualified_scope="s", dependencies=list(deps))
    return e


class TestRegistry(unittest.TestCase):
    def test_committed_entries_are_well_formed(self):
        self.assertEqual(R.problems(ENTRIES), [])
        self.assertTrue(all(e["qualified_scope"] and e["not_qualified_for"] for e in ENTRIES))

    def test_nothing_is_globally_qualified(self):
        self.assertNotIn("QUALIFIED", {e["stage"] for e in ENTRIES})
        e = _entry("a", [])
        e["stage"] = "QUALIFIED"
        self.assertTrue(any("stage" in p for p in R.problems([e])))

    def test_unchanged_bytes_are_current_and_crlf_does_not_count(self):
        root = _tree({"m/a.py": b"x = 1\n"})
        reg = R.build([_entry("a", ["m/a.py"])], "c0", root)
        with open(os.path.join(root, "m/a.py"), "wb") as f:
            f.write(b"x = 1\r\n")
        self.assertEqual(R.status(reg, root)["a"], ("CURRENT", []))

    def test_a_changed_byte_requires_requalification(self):
        root = _tree({"m/a.py": b"x = 1\n"})
        reg = R.build([_entry("a", ["m/a.py"])], "c0", root)
        with open(os.path.join(root, "m/a.py"), "wb") as f:
            f.write(b"x = 2\n")
        self.assertEqual(R.status(reg, root)["a"], ("REQUALIFY_REQUIRED", ["m/a.py"]))

    def test_requalification_propagates_to_dependents(self):
        root = _tree({"m/a.py": b"a\n", "m/b.py": b"b\n", "m/c.py": b"c\n"})
        reg = R.build([_entry("c", ["m/c.py"], ["b"]), _entry("b", ["m/b.py"], ["a"]), _entry("a", ["m/a.py"])],
                      "c0", root)
        with open(os.path.join(root, "m/a.py"), "wb") as f:
            f.write(b"A\n")
        st = R.status(reg, root)
        self.assertEqual([st[n][0] for n in "abc"], ["REQUALIFY_REQUIRED"] * 3)
        self.assertEqual(st["c"][1], ["dependency b"])

    def test_missing_field_unknown_dependency_and_missing_file_refuse_build(self):
        root = _tree({"m/a.py": b"a\n"})
        e = _entry("a", ["m/a.py", "m/gone.py"], ["nope"])
        del e["counterexamples"]
        with self.assertRaises(ValueError) as cm:
            R.build([e], "c0", root)
        msg = str(cm.exception)
        for part in ("missing counterexamples", "unknown dependency nope", "file missing m/gone.py"):
            self.assertIn(part, msg)

    def test_a_deleted_pinned_file_is_malformed_not_current(self):
        root = _tree({"m/a.py": b"a\n"})
        reg = R.build([_entry("a", ["m/a.py"])], "c0", root)
        os.remove(os.path.join(root, "m/a.py"))
        self.assertEqual(R.status(reg, root)["a"][0], "MALFORMED")

    def test_committed_registry_matches_entries(self):
        reg = R._load()
        pinned = [{k: v for k, v in e.items() if k != "source"} for e in reg["entries"]]
        self.assertEqual(pinned, copy.deepcopy(ENTRIES))


if __name__ == "__main__":
    unittest.main()
