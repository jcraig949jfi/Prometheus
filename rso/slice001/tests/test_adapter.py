"""Tests for the producer adapter: world runs -> producer receipts (C-004-T016).

The round trip is world.run_life (T010) -> adapter traces and receipts -> checker.g_recomp (T015). The runtimes
below are draft A A6's REG, PKTD and LAGD realised on world.Runtime; the outcomes handed to the adapter are the
contract's expected outcomes (A4-A6 eligible counts, the hand-derived LAGD ERASE witness of T015's tests and
EXPECTED_ANSWERS.json rows T01.REG / T04.LAGD), never checker output, so a PASS of G-RECOMP shows that the
world's traces in the checker's byte layout recompute to what the contract says. No custody is involved.
Python >= 3.8, standard library only.
"""
import copy
import json
import os
import unittest

from rso.slice001 import adapter as A
from rso.slice001 import checker as C
from rso.slice001 import evidence as EV
from rso.slice001 import receipt as R
from rso.slice001 import world as W

COMMIT = "c004" + "0" * 36
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --------------------------------------------------------------------------------------------------------
# Draft A A6 runtimes on the world's runtime interface.

class Reg(W.Runtime):
    """REG: a := u and d := f at CUE; reset d := 0 and flush the channel."""

    def on_cue(self, u, f):
        self.a, self.d = u, f

    def on_deliver(self, bits):
        pass

    def reset(self):
        self.d, self.chan, self.log_n = 0, [], self.log_n + 1


class Pktd(Reg):
    """PKTD: the display goes through the channel: sends (f, 0); d := the delivered bit."""

    def on_cue(self, u, f):
        self.a = u
        self.send(f, 0)

    def on_deliver(self, bits):
        if bits:
            self.d = bits[0]


class Lagd(Reg):
    """LAGD: d := f and sends (f, 1); on delivery d := bit; reset sets d := 0 only (channel kept)."""

    def on_cue(self, u, f):
        self.a, self.d = u, f
        self.send(f, 1)

    def on_deliver(self, bits):
        if bits:
            self.d = bits[0]

    def reset(self):
        self.d, self.log_n = 0, self.log_n + 1


class Spam(Reg):
    """Leaves the registered model: three sends in one CUE (S = 2)."""

    def on_cue(self, u, f):
        for _ in range(3):
            self.send(f, 1)


RUNTIMES = {"REG": Reg, "PKTD": Pktd, "LAGD": Lagd}

# --------------------------------------------------------------------------------------------------------
# Expected outcomes from the contract (A4-A6), stated here, never computed by the checker.


def gate(pid, value, eligible, witness=None, applicable=None, reason="expected (contract A6)"):
    return {"kind": "GATE", "predicate": pid, "value": value, "reason": reason, "witness": witness,
            "eligible_count": eligible, "applicable_count": applicable, "vacuous": applicable == 0}


RET_POS = {"kind": "RULER", "ruler": "P2", "value": "POSITIVE", "statistic": "1/1", "successes": 12288,
           "trials": 12288, "per_boundary": [{"j": j, "statistic": "1/1"} for j in (1, 2, 3)],
           "reason": "expected (contract A6)"}
EXPECTED = {"CALIBRATION": gate("P1", "PASS", 98304), "RETENTION": RET_POS, "ERASE": gate("P3", "PASS", 9600),
            "PRESERVE": gate("P4", "PASS", 6144, applicable=6144), "CHANNEL": gate("P5", "PASS", 24576)}
LAGD_ERASE = gate("P3", "FAIL", 9600, {"history": 64, "partner": 0, "j": 3, "episode": 4, "tick": "PROBE_A"})


def expected(subject, name):
    if (subject, name) == ("LAGD", "ERASE"):
        return copy.deepcopy(LAGD_ERASE)
    return copy.deepcopy(EXPECTED[name])


def ref(path):
    return A.file_code_ref(path, COMMIT, root=os.path.dirname(os.path.dirname(HERE)))


def identity(subject):
    return A.Identity(
        registration_ref={"path": "rso/slice001/contract/contract.json", "blob_sha256": "a" * 64, "commit": COMMIT},
        contract_ref={"path": "rso/slice001/contract/contract.json", "blob_sha256": "a" * 64, "commit": COMMIT},
        cell={"cell_id": "W-S1", "revision": "b" * 64, "physics": "%s fixture" % subject,
              "world": "STANDARD", "boundary": "EPISODE_CONTENT_RESET j=1..3", "search": "NONE",
              "development": "NONE", "resources": "OP-1 caps", "exposure": "EXPOSURE fixture"},
        subject={"id": subject, "code": [ref("rso/slice001/tests/test_adapter.py")]},
        world_code=[ref("rso/slice001/world.py")],
        producer_code=[ref("rso/slice001/adapter.py")],
        code_state={"base_sha": COMMIT, "branch": "test", "worktree_path": "test", "dirty": False},
        expected_table={"path": "rso/slice001/expected/EXPECTED_ANSWERS.json", "blob_sha256": "c" * 64,
                        "commit": COMMIT})


PRED_CODE = [{"role": "code:rso/slice001/rulers.py", "sha256": "d" * 64, "length": 1, "commit": COMMIT}]
_RUNS = {}


def runs_of(subject):
    if subject not in _RUNS:
        _RUNS[subject] = A.world_runs(RUNTIMES[subject])
    return _RUNS[subject]


def produce(subject, name, outcome=None, runs=None):
    """A receipt + traces for one recompute-set node, from the world runs, with the contract outcome."""
    world_subject = EV.WORLD_SUBJECT if name == "CALIBRATION" else subject
    out = expected(subject, name) if outcome is None else outcome
    return A.make_receipt(identity(world_subject), name, lambda runs: out, PRED_CODE,
                          runs=runs_of(subject) if runs is None else runs, run_id="run-%s-%s" % (subject, name))


def bundle_for(subject, **override):
    receipts, traces = {}, {}
    for name in C.RECOMPUTE_SET:
        rc, tr = override.get(name) or produce(subject, name)
        receipts[rc.node_id] = rc.canonical_bytes()
        traces[rc.node_id] = tr
    return EV.Bundle(receipts, traces, inventory=[])


def g_recomp(subject, bundle):
    claim = EV.make_claim("CL-RET", subject=subject)
    return C.g_recomp(claim, bundle, None)


def value(g):
    o = g["outcome"]
    return (o["value"], o["reason"] if o["value"] == "FAIL" else None)


# --------------------------------------------------------------------------------------------------------

class TestWorldTraces(unittest.TestCase):
    def test_layout_is_the_checkers(self):
        tr = A.world_traces(Reg)
        self.assertEqual(sorted(tr), sorted(C.TRACE_LAYOUT))
        for role, data in tr.items():
            self.assertEqual(C.parse_trace(role, data), runs_of("REG")[role])

    def test_runs_follow_the_world(self):
        # Spot values from A2/A6. PROBE_A precedes CUE, so at episode e REG answers a = u_{e-1} (0 in episode
        # 1) and displays d = 0 (cleared by every reset; 0 initially).
        pa = runs_of("REG")["trace:probe_a"]["RESET"]
        h = 0b101101011010
        for e in range(1, W.EPISODES + 1):
            y = W.u_of(h, e - 1) if e > 1 else 0
            self.assertEqual(pa[h * 12 + (e - 1) * 2:h * 12 + e * 2], "%d0" % y)
        sends = runs_of("PKTD")["trace:sends"]["RESET"]
        self.assertEqual(sends[h * 24:h * 24 + 4], "%d0--" % W.f_of(h, 1))
        g = 1 << (2 * (W.EPISODES - 1))                             # f_1 = 1: slot order <bit><k> is visible
        self.assertEqual(sends[g * 24:g * 24 + 4], "10--")
        self.assertEqual(runs_of("LAGD")["trace:sends"]["RESET"][4:8], "01--")       # h = 0, episode 2: f_2 = 0, k = 1
        self.assertEqual(runs_of("REG")["trace:sends"]["RESET"][:24], "--" * 12)
        cl = runs_of("REG")["trace:clamp"]["CLAMP"]
        self.assertEqual(cl[h * 6:h * 6 + 6], "010101")              # y_A follows the clamp v at j = 1..3

    def test_skip_runs_differ_only_by_the_skipped_reset(self):
        # REG's reset clears only d: skipping it leaves every answer y_A (a is ALLOWED) unchanged and changes
        # the PROBE_A display of episode j+1 (d = f_j instead of 0) whenever f_j = 1.
        r = runs_of("REG")["trace:probe_a"]
        for j in W.BOUNDARIES:
            self.assertEqual(r["SKIP%d" % j][0::2], r["RESET"][0::2])
            self.assertNotEqual(r["SKIP%d" % j][1::2], r["RESET"][1::2])
            h = 1 << (2 * (W.EPISODES - j))                         # f_j = 1, every other input 0
            self.assertEqual(r["SKIP%d" % j][h * 12 + j * 2 + 1], "1")
            self.assertEqual(r["RESET"][h * 12 + j * 2 + 1], "0")

    def test_out_of_model_runtime_is_blocked_not_traced(self):
        rc, tr = A.make_receipt(identity("SPAM"), "ERASE", lambda runs: self.fail("no outcome may be asked"),
                                PRED_CODE, make=Spam, run_id="run-spam")
        d = rc.to_dict()
        self.assertEqual(d["execution"]["status"], "BLOCKED")
        self.assertEqual(d["execution"]["missing"], ["BOUNDS_VIOLATION:SENDS_PER_CUE"])
        self.assertIsNone(d["outcome"])
        self.assertEqual((d["outputs"], tr), ([], {}))


class TestReceipt(unittest.TestCase):
    def test_receipt_records_identities_and_never_its_own_outcome(self):
        out = expected("REG", "ERASE")
        rc, tr = produce("REG", "ERASE", outcome=out)
        d = rc.to_dict()
        self.assertEqual(d["outcome"], out)                         # exactly what the gate returned
        self.assertNotIn("authority", d)
        self.assertEqual(d["node_id"], "rcpt:REG:ERASE:STANDARD")
        self.assertEqual(sorted(a["role"] for a in d["outputs"]), sorted(C.RECOMPUTE_ROLES["ERASE"]))
        for a in d["outputs"]:
            self.assertEqual((a["length"], a["sha256"]), (len(tr[a["role"]]), EV._sha(tr[a["role"]])))
        self.assertEqual(d["cell"]["measurement"], EV.predicate_version(PRED_CODE))
        self.assertEqual(d["dependencies"], sorted(EV.required_deps("rcpt:REG:ERASE:STANDARD")))
        self.assertEqual(d["execution"], {"status": "RAN", "missing": [], "run_id": "run-REG-ERASE"})
        self.assertEqual(d["predicate"], {"id": "P3", "kind": "GATE", "code": PRED_CODE})
        self.assertGreater(d["resources"]["artifact_bytes"], 0)

    def test_outcome_with_authority_is_refused(self):
        bad = dict(expected("REG", "ERASE"), authority="QUALIFIED")
        with self.assertRaises(R.ReceiptError):
            produce("REG", "ERASE", outcome=bad)

    def test_wrong_kind_outcome_is_refused(self):
        with self.assertRaises(R.ReceiptError):
            produce("REG", "ERASE", outcome=copy.deepcopy(RET_POS))

    def test_file_code_ref_hashes_lf_bytes(self):
        r = ref("rso/slice001/world.py")
        with open(os.path.join(HERE, "world.py"), "rb") as f:
            data = f.read().replace(b"\r\n", b"\n")
        self.assertEqual((r["role"], r["length"], r["sha256"]), ("code:rso/slice001/world.py", len(data),
                                                                EV._sha(data)))


class TestRoundTrip(unittest.TestCase):
    """world run -> adapter -> checker.g_recomp, on the contract's expected outcomes."""

    def test_reg_round_trip_passes(self):
        self.assertEqual(value(g_recomp("REG", bundle_for("REG"))), ("PASS", None))

    def test_pktd_round_trip_passes(self):
        self.assertEqual(value(g_recomp("PKTD", bundle_for("PKTD"))), ("PASS", None))

    def test_lagd_round_trip_passes_with_the_erase_failure(self):
        g = g_recomp("LAGD", bundle_for("LAGD"))
        self.assertEqual(value(g), ("PASS", None))
        self.assertIn("ERASE", g["outcome"]["reason"])

    def test_expected_table_agrees_on_t01_and_t04(self):
        with open(os.path.join(HERE, "expected", "EXPECTED_ANSWERS.json"), encoding="utf-8") as f:
            rows = {r["id"]: r for r in json.load(f)["rows"]}
        p = rows["T01.REG"]["primary"]
        self.assertEqual((p["successes"], p["trials"], p["statistic"]), (12288, 12288, "1/1"))
        self.assertEqual(rows["T04.LAGD"]["outcome"], "FAIL")


class TestCheatControls(unittest.TestCase):
    def test_outputs_differing_from_supplied_bytes_are_refused(self):
        # Cheat: REG's receipt with LAGD's probe_a bytes supplied (same answers, different displays). The
        # consumer must not recompute from bytes the receipt does not bind.
        rc, tr = produce("REG", "RETENTION")
        other = A.traces_from_runs({"trace:probe_a": runs_of("LAGD")["trace:probe_a"]})["trace:probe_a"]
        self.assertNotEqual(other, tr["trace:probe_a"])
        swapped = dict(tr, **{"trace:probe_a": other})
        g = g_recomp("REG", bundle_for("REG", RETENTION=(rc, swapped)))
        self.assertEqual(value(g), ("FAIL", "BYTES_MISMATCH:trace:probe_a"))

    def test_one_flipped_byte_is_refused(self):
        rc, tr = produce("REG", "ERASE")
        b = bytearray(tr["trace:sends"])
        b[-10] = ord("0") if b[-10] != ord("0") else ord("1")
        g = g_recomp("REG", bundle_for("REG", ERASE=(rc, dict(tr, **{"trace:sends": bytes(b)}))))
        self.assertEqual(value(g), ("FAIL", "BYTES_MISMATCH:trace:sends"))

    def test_wrong_outcome_on_true_traces_is_refused(self):
        # A producer claiming ERASE PASS for LAGD over LAGD's real traces: recomputation disagrees.
        bad = produce("LAGD", "ERASE", outcome=expected("REG", "ERASE"))
        g = g_recomp("LAGD", bundle_for("LAGD", ERASE=bad))
        self.assertEqual(value(g), ("FAIL", "OUTCOME_MISMATCH:value"))


class Invert(W.Runtime):
    """S3_INVERT-like (C-004-T042, F1): the reset complements a and sets a flag the capture omits; the answer
    un-complements while the flag is set. The clamp is meaningful only on the SAME instance."""

    def __init__(self):
        W.Runtime.__init__(self)
        self.flipped = False

    def on_cue(self, u, f):
        self.a, self.d, self.flipped = u, f, False

    def answer(self):
        return self.a ^ 1 if self.flipped else self.a

    def reset(self):
        self.a ^= 1
        self.flipped = True


class TestF1ClampSameInstance(unittest.TestCase):
    """F1 (S3.BROKEN.INVERT): the bound trace:clamp must be the trace the registered CHANNEL instrument
    (reset.clamp_answers: capture, a := v, restore into the SAME runtime) computes its outcome from."""

    def test_clamp_trace_equals_the_instruments_clamp_answers(self):
        from rso.slice001 import reset as RS
        run = A.world_runs(Invert)["trace:clamp"]["CLAMP"]
        for h in (0, 1, 64, 1365, 4095):
            self.assertEqual(run[h * 6:h * 6 + 6], "".join("%d" % y for y in RS.clamp_answers(Invert, h)), h)

    def test_honest_channel_receipt_recomputes_equal(self):
        from rso.slice001 import reset as RS
        runs = A.world_runs(Invert)
        out = {k: v for k, v in RS.channel(Invert).items() if k != "execution"}
        self.assertEqual(out["value"], "FAIL")                       # the in-place reading: v is not followed
        rc, tr = A.make_receipt(identity("INVERT"), "CHANNEL", lambda r: out, PRED_CODE, run_id="r", runs=runs)
        self.assertIsNone(C.first_mismatch("CHANNEL", rc.to_dict()["outcome"],
                                           C.recompute("CHANNEL", "STANDARD", {k: C.parse_trace(k, b) for k, b in tr.items()})))


if __name__ == "__main__":
    unittest.main()
