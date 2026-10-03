"""Tests for the S2 scaffolding CI command (C-004-T003). Stdlib only."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def run_ci(*args):
    return subprocess.run(
        [sys.executable, "-B", "-m", "rso.slice001.ci"] + list(args),
        cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True)


class TestSkeleton(unittest.TestCase):
    def test_package_importable(self):
        import rso.slice001  # noqa: F401
        from rso.slice001 import ci
        self.assertTrue(callable(ci.main))


class TestRunRecord(unittest.TestCase):
    def test_record_fields_on_passing_dir(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "test_ok.py"), "w") as f:
                f.write("import unittest\nclass T(unittest.TestCase):\n"
                        "    def test_a(self): self.assertTrue(True)\n")
            r = run_ci("--tests-dir", d, "--contract", os.path.join(d, "none.json"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rec = json.loads(r.stdout)
        for k in ("tests_run", "passed", "failed", "errored", "start_utc", "end_utc",
                  "git_sha", "dirty", "wall_s", "cpu_s", "contract", "status"):
            self.assertIn(k, rec)
        self.assertEqual((rec["tests_run"], rec["passed"], rec["failed"], rec["errored"]), (1, 1, 0, 0))
        self.assertEqual(rec["contract"]["state"], "ABSENT")
        self.assertEqual(rec["status"], "PASSED")


class TestCheatControl(unittest.TestCase):
    def test_failing_test_is_observed(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "test_bad.py"), "w") as f:
                f.write("import unittest\nclass T(unittest.TestCase):\n"
                        "    def test_a(self): self.assertTrue(False)\n"
                        "    def test_b(self): raise RuntimeError('x')\n")
            r = run_ci("--tests-dir", d, "--contract", os.path.join(d, "none.json"))
        self.assertNotEqual(r.returncode, 0)
        rec = json.loads(r.stdout)
        self.assertEqual(rec["status"], "FAILED")
        self.assertEqual((rec["failed"], rec["errored"], rec["passed"]), (1, 1, 0))


class TestContractShape(unittest.TestCase):
    KEYS = ["version", "frozen", "claim", "world", "reset_model", "receipt", "render",
            "authority_stages", "custody", "gates", "cases", "challenge", "caps", "files"]

    def _check(self, obj):
        from rso.slice001 import ci
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "contract.json")
            with open(p, "w") as f:
                json.dump(obj, f)
            return ci.validate_contract(p)

    def _good(self):
        o = {k: {} for k in self.KEYS}
        o["version"] = "1"
        o["frozen"] = False
        return o

    def test_valid(self):
        self.assertEqual(self._check(self._good())["state"], "OK")

    def test_missing_key_reported(self):
        o = self._good()
        del o["gates"]
        res = self._check(o)
        self.assertEqual(res["state"], "INVALID")
        self.assertIn("gates", " ".join(res["problems"]))

    def test_wrong_type_reported(self):
        o = self._good()
        o["frozen"] = "yes"
        self.assertEqual(self._check(o)["state"], "INVALID")

    def test_non_object_and_bad_json(self):
        self.assertEqual(self._check([1])["state"], "INVALID")
        from rso.slice001 import ci
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "c.json")
            with open(p, "w") as f:
                f.write("{not json")
            self.assertEqual(ci.validate_contract(p)["state"], "INVALID")

    def test_absent(self):
        from rso.slice001 import ci
        self.assertEqual(ci.validate_contract(os.path.join(tempfile.gettempdir(), "nope-xyz.json"))["state"], "ABSENT")

    def test_invalid_contract_fails_command(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "test_ok.py"), "w") as f:
                f.write("import unittest\nclass T(unittest.TestCase):\n    def test_a(self): pass\n")
            p = os.path.join(d, "contract.json")
            with open(p, "w") as f:
                f.write("{}")
            r = run_ci("--tests-dir", d, "--contract", p)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout)["contract"]["state"], "INVALID")


if __name__ == "__main__":
    unittest.main()
