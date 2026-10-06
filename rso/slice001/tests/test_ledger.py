"""Tests for the attempted-run inventory and caps ledger (C-004-T019). Stdlib only.

The ledger counts and refuses; it decides nothing scientific. Controls:
  RED / fire test   the 13th launch under a 12-launch cap is refused (and the refusal is inventoried)
  cheat control     a run that crashes, or is killed before it can report, still leaves a row
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from rso.slice001 import evidence as E
from rso.slice001 import ledger as L
from rso.slice001 import receipt as R

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

CAPS = {"cpu_minutes": 30, "new_artifact_mb": 100, "top_level_validation_launches": 12}
CONTRACT_KEYS = ("version", "frozen", "claim", "world", "reset_model", "receipt", "render",
                 "authority_stages", "custody", "gates", "cases", "challenge", "files")


def caps(**over):
    d = dict(CAPS)
    d.update(over)
    return L.Caps.from_dict(d)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = os.path.join(self._tmp.name, "attempted_runs.jsonl")

    def ledger(self, **over):
        return L.Ledger(self.path, caps(**over))

    def lines(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return [json.loads(x) for x in f.read().splitlines() if x.strip()]


class TestCaps(Base):
    def test_caps_read_from_the_real_contract(self):
        c = L.Ledger.from_contract(self.path).caps
        self.assertEqual(c.launches, 20)                         # contract v1.0.4, OP-7 (was 12)
        self.assertEqual(c.cpu_s, 120 * 60)                      # contract v1.0.3, OP-4 (was 30 * 60)
        self.assertEqual(c.artifact_bytes, 100 * 1000 * 1000)

    def test_contract_v104_launch_cap_amendment_is_exact(self):
        # AMENDMENT_v1.0.4 X1 (12 -> 20) and X2 (launch_accounting text, verbatim) and the amendments entry.
        path = os.path.join(REPO, "rso", "slice001", "contract", "contract.json")
        with open(path, "r", encoding="utf-8") as f:
            doc = json.load(f)
        self.assertEqual(doc["version"], "1.0.4")
        self.assertEqual(doc["caps"]["top_level_validation_launches"], 20)
        self.assertEqual(
            doc["caps"]["launch_accounting"],
            "S2/S3 window under the original cap of 12: 8 launches used (S2 produce 5: G0, EXTRA, HEAL, FLAT, "
            "LOSSY; S3 3: unchanged suite, cases, mutation driver), closed at the S3 integration (bddb3c71d), 4 "
            "unused. Post-S3 repair-round window (OP-7): launches 9-20, i.e. 12 more, for the S4 regression rerun "
            "of all five S2 bundles on the repaired code and the S4 closure set; the ledger counts both windows "
            "cumulatively against 20.")
        self.assertEqual(doc["caps"]["cpu_minutes"], 120)         # every other cap unchanged by v1.0.4
        self.assertEqual(doc["caps"]["new_artifact_mb"], 100)
        self.assertEqual(doc["amendments"][-1]["version"], "1.0.4")
        self.assertEqual(doc["amendments"][-1]["path"], "rso/slice001/contract/AMENDMENT_v1.0.4.md")

    def test_missing_or_bad_caps_fail_closed(self):
        for bad in ({}, {"cpu_minutes": 30}, dict(CAPS, cpu_minutes="x"), dict(CAPS, top_level_validation_launches=-1),
                    dict(CAPS, new_artifact_mb=True)):
            with self.assertRaises(L.LedgerError, msg=repr(bad)):
                L.Caps.from_dict(bad)

    def test_contract_without_caps_fails_closed(self):
        p = os.path.join(self._tmp.name, "c.json")
        with open(p, "w") as f:
            json.dump({"version": 1}, f)
        with self.assertRaises(L.LedgerError):
            L.Ledger.from_contract(self.path, p)


class TestLaunchCap(Base):
    def run_one(self, led, i, **kw):
        a = led.begin("run-%02d" % i, "node-%d" % i, **kw)
        a.finish("COMPLETED", cpu_s=0.1)

    def test_13th_launch_under_12_cap_is_refused(self):
        led = self.ledger()
        for i in range(12):
            self.run_one(led, i)
        with self.assertRaises(L.CapExhausted) as cm:
            led.begin("run-12", "node-12")
        self.assertEqual(cm.exception.cap, "top_level_validation_launches")
        self.assertEqual((cm.exception.used, cm.exception.limit), (12, 12))
        rows = led.inventory()
        self.assertEqual(rows[-2]["status"], "REFUSED")        # the refusal is itself inventoried
        self.assertEqual(rows[-2]["run_id"], "run-12")

    def test_refusal_does_not_consume_a_launch(self):
        led = self.ledger(top_level_validation_launches=1)
        self.run_one(led, 0)
        for i in (1, 2, 3):
            with self.assertRaises(L.CapExhausted):
                led.begin("run-%02d" % i, "n")
        self.assertEqual(led.usage()["launches"], 1)

    def test_children_do_not_count_as_launches(self):
        led = self.ledger(top_level_validation_launches=1)
        self.run_one(led, 0)
        for i in range(1, 4):
            self.run_one(led, i, launch_kind="MUTATION_CHILD")
        self.assertEqual(led.usage()["launches"], 1)
        with self.assertRaises(L.CapExhausted):
            led.begin("top", "n")

    def test_failures_and_retries_are_charged(self):
        led = self.ledger(top_level_validation_launches=2)
        led.begin("a", "n").finish("FAILED")
        led.begin("a-retry", "n").finish("COMPLETED")
        with self.assertRaises(L.CapExhausted):
            led.begin("a-retry-2", "n")


class TestResourceCaps(Base):
    def test_cpu_cap_stops_everything_including_children(self):
        led = self.ledger(cpu_minutes=1)
        led.begin("a", "n").finish("COMPLETED", cpu_s=60)
        for kind in ("TOP_LEVEL", "MUTATION_CHILD"):
            with self.assertRaises(L.CapExhausted) as cm:
                led.begin("b-" + kind, "n", launch_kind=kind)
            self.assertEqual(cm.exception.cap, "cpu_minutes")

    def test_mutation_children_are_charged_cpu(self):
        led = self.ledger(cpu_minutes=1)
        led.begin("c1", "n", launch_kind="MUTATION_CHILD").finish("COMPLETED", cpu_s=40)
        led.begin("c2", "n", launch_kind="MUTATION_CHILD").finish("COMPLETED", cpu_s=20)
        self.assertEqual(led.usage()["cpu_s"], 60)
        with self.assertRaises(L.CapExhausted):
            led.begin("c3", "n")

    def test_artifact_bytes_cap(self):
        led = self.ledger(new_artifact_mb=1)
        led.begin("a", "n").finish("COMPLETED", artifact_bytes=1000 * 1000)
        with self.assertRaises(L.CapExhausted) as cm:
            led.begin("b", "n")
        self.assertEqual(cm.exception.cap, "new_artifact_mb")

    def test_under_cap_is_not_refused(self):
        led = self.ledger(cpu_minutes=1)
        led.begin("a", "n").finish("COMPLETED", cpu_s=59.9)
        led.begin("b", "n").finish("COMPLETED", cpu_s=0.0)


def _floats(obj, path="$"):
    """Paths of every float anywhere in a JSON-like value."""
    if isinstance(obj, float):
        return [path]
    if isinstance(obj, dict):
        return [p for k, v in sorted(obj.items()) for p in _floats(v, "%s.%s" % (path, k))]
    if isinstance(obj, (list, tuple)):
        return [p for i, v in enumerate(obj) for p in _floats(v, "%s[%d]" % (path, i))]
    return []


class TestCanonicalSafeInventory(Base):
    """C-004-T025 / escalation C-004-T024_2: receipt.canonical_bytes refuses floats (draft B B2), so the
    inventory the custody layer hashes must carry integer microseconds, never a float cpu_s."""

    def doc(self, led):
        return {"schema": E.INVENTORY_SCHEMA, "rows": led.inventory()}

    def test_inventory_hashes_with_receipt_canonical_bytes(self):
        led = self.ledger()
        led.begin("a", "node-a").finish("COMPLETED", cpu_s=52.1734567, artifact_bytes=10)
        led.begin("b", "node-b").finish("FAILED", cpu_s=0.0000004)
        led.begin("dead", "node-c")                              # INTERRUPTED: cpu_us None
        R.canonical_bytes(self.doc(led))                         # raises ReceiptError on any float
        self.assertEqual(_floats(self.doc(led)), [])

    def test_refused_rows_are_canonical_safe_too(self):
        led = self.ledger(top_level_validation_launches=1)
        led.begin("a", "n").finish("COMPLETED", cpu_s=1.25)
        with self.assertRaises(L.CapExhausted):
            led.begin("b", "n")
        R.canonical_bytes(self.doc(led))
        self.assertEqual([r["status"] for r in led.inventory()[:-1]], ["COMPLETED", "REFUSED"])

    def test_cpu_us_is_the_rounded_integer_microseconds(self):
        led = self.ledger()
        for i, s in enumerate((52.17, 0.0, 1.0000004, 1.0000006, 2.5, 0.0000004)):
            led.begin("r%d" % i, "n").finish("COMPLETED", cpu_s=s)
        got = [r["cpu_us"] for r in led.inventory()[:-1]]
        self.assertEqual(got, [52170000, 0, 1000000, 1000001, 2500000, 0])
        self.assertTrue(all(type(v) is int for v in got))

    def test_no_float_cpu_s_field_in_rows(self):
        led = self.ledger()
        led.begin("a", "n").finish("COMPLETED", cpu_s=3.0)
        self.assertNotIn("cpu_s", led.inventory()[0])

    def test_store_keeps_the_float_and_usage_still_sums_seconds(self):
        led = self.ledger()
        led.begin("a", "n").finish("COMPLETED", cpu_s=0.25)
        led.begin("b", "n").finish("COMPLETED", cpu_s=0.5)
        self.assertEqual(self.lines()[1]["cpu_s"], 0.25)         # the JSONL store is unchanged
        self.assertEqual(led.usage()["cpu_s"], 0.75)

    def test_written_inventory_file_is_canonical_safe(self):
        led = self.ledger()
        led.begin("a", "n").finish("COMPLETED", cpu_s=7.7)
        out = os.path.join(self._tmp.name, "inv.jsonl")
        led.write_inventory(out)
        with open(out, "r", encoding="utf-8") as f:
            rows = [json.loads(x) for x in f.read().splitlines()]
        self.assertEqual(_floats(rows), [])


class TestReceiptRowKind(Base):
    """A RECEIPT row charges CPU and bytes but not a top-level launch; it carries a node_id (V7)."""

    def test_25_receipt_rows_charge_one_launch_and_their_summed_cpu(self):
        led = self.ledger()
        led.begin("build", "G0", launch_kind=L.TOP_LEVEL).finish("COMPLETED", cpu_s=1.0)
        for i in range(25):
            led.begin("rcpt-%02d" % i, "rcpt:node-%02d" % i, launch_kind=L.RECEIPT).finish(
                "COMPLETED", cpu_s=2.0, artifact_bytes=100)
        u = led.usage()
        self.assertEqual(u["launches"], 1)
        self.assertEqual(u["cpu_s"], 51.0)
        self.assertEqual(u["artifact_bytes"], 2500)

    def test_receipt_rows_leave_the_other_eleven_launches_available(self):
        led = self.ledger()                                      # cap 12
        led.begin("build", "G0").finish("COMPLETED")
        for i in range(25):
            led.begin("rcpt-%02d" % i, "n-%d" % i, launch_kind=L.RECEIPT).finish("COMPLETED")
        for i in range(11):
            led.begin("run-%02d" % i, "n").finish("COMPLETED")
        with self.assertRaises(L.CapExhausted) as cm:
            led.begin("run-11", "n")
        self.assertEqual(cm.exception.cap, "top_level_validation_launches")

    def test_receipt_rows_carry_kind_and_node_id_in_the_inventory(self):
        led = self.ledger()
        led.begin("build", "G0").finish("COMPLETED")
        led.begin("r1", "rcpt:REG:BOUNDS:STANDARD", launch_kind=L.RECEIPT).finish("COMPLETED")
        rows = led.inventory()
        self.assertEqual([(r["run_id"], r["node_id"], r["launch_kind"]) for r in rows[:-1]],
                         [("build", "G0", "TOP_LEVEL"), ("r1", "rcpt:REG:BOUNDS:STANDARD", "RECEIPT")])
        self.assertTrue(E.inventory_terminal(rows))

    def test_receipt_row_is_still_refused_when_cpu_is_exhausted(self):
        led = self.ledger(cpu_minutes=1)
        led.begin("a", "n").finish("COMPLETED", cpu_s=60)
        with self.assertRaises(L.CapExhausted) as cm:
            led.begin("r", "n", launch_kind=L.RECEIPT)
        self.assertEqual(cm.exception.cap, "cpu_minutes")
        self.assertEqual(led.inventory()[-2]["status"], "REFUSED")

    def test_receipt_row_is_refused_when_bytes_are_exhausted(self):
        led = self.ledger(new_artifact_mb=1)
        led.begin("a", "n").finish("COMPLETED", artifact_bytes=1000 * 1000)
        with self.assertRaises(L.CapExhausted) as cm:
            led.begin("r", "n", launch_kind=L.RECEIPT)
        self.assertEqual(cm.exception.cap, "new_artifact_mb")

    def test_receipt_row_is_not_blocked_by_an_exhausted_launch_cap(self):
        led = self.ledger(top_level_validation_launches=1)
        led.begin("build", "G0").finish("COMPLETED")
        led.begin("r1", "n", launch_kind=L.RECEIPT).finish("COMPLETED")   # does not raise
        with self.assertRaises(L.CapExhausted):
            led.begin("top2", "n")

    def test_an_interrupted_receipt_row_is_not_a_launch(self):
        led = self.ledger(top_level_validation_launches=1)
        led.begin("build", "G0").finish("COMPLETED")
        led.begin("dead", "n", launch_kind=L.RECEIPT)                      # never finished
        self.assertEqual(led.usage()["launches"], 1)

    def test_unknown_launch_kind_is_still_an_error(self):
        with self.assertRaises(L.LedgerError):
            self.ledger().begin("r", "n", launch_kind="SIDECAR")


class TestCrashRowsCheat(Base):
    def test_exception_in_context_leaves_a_failed_row_and_propagates(self):
        led = self.ledger()
        with self.assertRaises(RuntimeError):
            with led.run("boom", "n"):
                raise RuntimeError("crash")
        row = led.inventory()[0]
        self.assertEqual((row["run_id"], row["status"]), ("boom", "FAILED"))

    def test_context_measures_cpu(self):
        # process_time() can tick as coarsely as ~15.6 ms on Windows, so a fixed workload can finish inside
        # one tick and measure exactly 0.0 (C-004-T022). Spin, bounded by wall time, until it advances.
        led = self.ledger()
        with led.run("spin", "n"):
            t0, deadline = time.process_time(), time.perf_counter() + 5.0
            while time.process_time() <= t0:
                if time.perf_counter() > deadline:
                    self.fail("process_time() did not advance in 5 s of spinning")
        self.assertGreater(led.inventory()[0]["cpu_us"], 0)

    def test_context_records_exactly_the_measured_cpu_delta(self):
        # deterministic cheat control: with a fake clock the recorded value must be the delta, not 0.0
        led = self.ledger()
        with mock.patch.object(L.time, "process_time", side_effect=[10.0, 12.5]):
            with led.run("fake-clock", "n"):
                pass
        row = led.inventory()[0]
        self.assertEqual((row["status"], row["cpu_us"]), ("COMPLETED", 2500000))

    def test_hard_killed_process_still_leaves_a_row(self):
        # cheat control: the child dies without running any cleanup; only the START line exists.
        code = ("import sys; from rso.slice001 import ledger as L\n"
                "led = L.Ledger(sys.argv[1], L.Caps.from_dict(%r))\n"
                "led.begin('killed', 'node-k')\n"
                "import os; os._exit(9)\n" % (CAPS,))
        r = subprocess.run([sys.executable, "-B", "-c", code, self.path], cwd=REPO,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(r.returncode, 9, r.stderr)
        row = self.ledger().inventory()[0]
        self.assertEqual((row["run_id"], row["node_id"], row["status"]), ("killed", "node-k", "INTERRUPTED"))
        self.assertIsNone(row["cpu_us"])                         # unmetered, never zero

    def test_interrupted_run_still_counts_as_a_launch(self):
        led = self.ledger(top_level_validation_launches=1)
        led.begin("dead", "n")                                   # never finished
        with self.assertRaises(L.CapExhausted):
            self.ledger(top_level_validation_launches=1).begin("next", "n")


class TestInventoryShape(Base):
    def test_rows_match_the_g_inv_interface(self):
        led = self.ledger()
        led.begin("r1", "node-a").finish("COMPLETED", cpu_s=1)
        led.begin("r2", "node-b").finish("FAILED")
        rows = led.inventory()
        self.assertTrue(E.inventory_terminal(rows))
        for r in rows[:-1]:
            self.assertEqual(r["kind"], "RUN")
            for k in ("run_id", "node_id", "status"):
                self.assertIn(k, r)
        self.assertEqual(rows[-1], {"kind": "TERMINAL", "row_count": 2})

    def test_empty_ledger_has_a_terminal_row(self):
        rows = self.ledger().inventory()
        self.assertEqual(rows, [{"kind": "TERMINAL", "row_count": 0}])
        self.assertTrue(E.inventory_terminal(rows))

    def test_node_id_is_recorded_per_row(self):
        led = self.ledger()
        led.begin("r1", "node-a").finish("COMPLETED")
        self.assertEqual(led.inventory()[0]["node_id"], "node-a")

    def test_write_inventory_round_trips(self):
        led = self.ledger()
        led.begin("r1", "node-a").finish("COMPLETED")
        out = os.path.join(self._tmp.name, "inv.jsonl")
        led.write_inventory(out)
        with open(out, "r", encoding="utf-8") as f:
            rows = [json.loads(x) for x in f.read().splitlines()]
        self.assertEqual(rows, led.inventory())


class TestAppendOnlyStore(Base):
    def test_every_record_is_flushed_before_begin_returns(self):
        led = self.ledger()
        led.begin("r1", "n")
        self.assertEqual([r["kind"] for r in self.lines()], ["START"])

    def test_a_second_ledger_instance_sees_prior_state(self):
        a = self.ledger(top_level_validation_launches=1)
        a.begin("r1", "n").finish("COMPLETED")
        with self.assertRaises(L.CapExhausted):
            self.ledger(top_level_validation_launches=1).begin("r2", "n")

    def test_duplicate_run_id_is_refused(self):
        led = self.ledger()
        led.begin("dup", "n").finish("COMPLETED")
        with self.assertRaises(L.LedgerError):
            led.begin("dup", "n")

    def test_finish_twice_is_an_error(self):
        a = self.ledger().begin("r1", "n")
        a.finish("COMPLETED")
        with self.assertRaises(L.LedgerError):
            a.finish("FAILED")

    def test_bad_status_is_an_error(self):
        a = self.ledger().begin("r1", "n")
        with self.assertRaises(L.LedgerError):
            a.finish("GREAT")

    def test_torn_last_line_is_tolerated_and_reported(self):
        led = self.ledger()
        led.begin("r1", "n").finish("COMPLETED")
        with open(self.path, "a", encoding="utf-8") as f:
            f.write('{"kind": "START", "run_id": "r2"')            # torn write, no newline
        fresh = self.ledger()
        self.assertEqual([r["run_id"] for r in fresh.inventory()[:-1]], ["r1"])
        self.assertTrue(fresh.torn_tail)

    def test_corrupt_middle_line_fails_closed(self):
        led = self.ledger()
        led.begin("r1", "n").finish("COMPLETED")
        with open(self.path, "r", encoding="utf-8") as f:
            ls = f.read().splitlines()
        ls.insert(1, "not json")
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("\n".join(ls) + "\n")
        with self.assertRaises(L.LedgerError):
            self.ledger().inventory()


class TestCiIntegration(Base):
    def setUp(self):
        Base.setUp(self)
        self.tests = os.path.join(self._tmp.name, "t")
        os.mkdir(self.tests)
        self.contract = os.path.join(self._tmp.name, "contract.json")
        c = {k: 1 for k in CONTRACT_KEYS}
        c.update({"frozen": True, "caps": dict(CAPS, top_level_validation_launches=2)})
        with open(self.contract, "w") as f:
            json.dump(c, f)

    def ci(self, *extra):
        return subprocess.run(
            [sys.executable, "-B", "-m", "rso.slice001.ci", "--tests-dir", self.tests,
             "--contract", self.contract] + list(extra),
            cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    def write_test(self, ok=True):
        with open(os.path.join(self.tests, "test_x.py"), "w") as f:
            f.write("import unittest\nclass T(unittest.TestCase):\n"
                    "    def test_a(self): self.assertTrue(%s)\n" % ok)

    def test_no_ledger_flag_writes_nothing(self):
        self.write_test()
        r = self.ci()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(os.path.exists(self.path))

    def test_ledgered_launch_appends_a_row_with_node_id(self):
        self.write_test()
        r = self.ci("--ledger", self.path, "--node-id", "node-ci")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rows = self.ledger().inventory()
        self.assertEqual((rows[0]["node_id"], rows[0]["status"], rows[0]["launch_kind"]),
                         ("node-ci", "COMPLETED", "TOP_LEVEL"))
        self.assertIn("ledger", json.loads(r.stdout))

    def test_failing_launch_is_still_inventoried(self):
        self.write_test(ok=False)
        r = self.ci("--ledger", self.path, "--node-id", "node-ci")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.ledger().inventory()[0]["status"], "FAILED")

    def test_third_launch_under_a_2_cap_is_refused_before_running_tests(self):
        self.write_test()
        for _ in range(2):
            self.assertEqual(self.ci("--ledger", self.path, "--node-id", "n").returncode, 0)
        r = self.ci("--ledger", self.path, "--node-id", "n")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("top_level_validation_launches", r.stderr)
        self.assertEqual(r.stdout.strip(), "")                   # no run record: nothing was run
        self.assertEqual(self.ledger().inventory()[-2]["status"], "REFUSED")

    def test_ledger_flag_requires_node_id(self):
        self.write_test()
        r = self.ci("--ledger", self.path)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(self.path))


if __name__ == "__main__":
    unittest.main()
