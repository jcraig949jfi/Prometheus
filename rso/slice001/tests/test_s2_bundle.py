"""The real S2 reference bundle G0 and the E01-E05 edits applied to it (C-004-T024).

G0 is built once per test run from real executions at HEAD (s2_bundle.build_g0, about 55 CPU-s) against a
temporary ledger. Expected results are the contract's (draft A A6 outcomes; draft B B6.3/B6.4 reasons), never
read back from the consumer. Every custody QUALIFIED here is fixture-store logic, never custody evidence (V8).
Stdlib only; uses git.
"""
import os
import shutil
import subprocess
import tempfile
import unittest

from rso.slice001 import checker as C
from rso.slice001 import evidence as EV
from rso.slice001 import ledger as L
from rso.slice001 import receipt as R
from rso.slice001 import s2_bundle as SB
from rso.slice001.fixtures import evidence_cases as F

_G0 = {}


def g0():
    if "g0" not in _G0:
        d = tempfile.mkdtemp(prefix="rso-g0-")
        try:
            led = L.Ledger.from_contract(os.path.join(d, "ledger.jsonl"))
            commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=SB.REPO_ROOT, capture_output=True,
                                    text=True).stdout.strip()
            _G0["g0"] = SB.build_g0(commit, led, run_id="g0-test", created_at_utc="2026-10-04T00:00:00Z")
            _G0["usage"] = led.usage()
            _G0["commit"] = commit
        finally:
            shutil.rmtree(d, ignore_errors=True)
    return _G0["g0"]


def base():
    if "base" not in _G0:
        _G0["base"] = F.real_base(g0())
    return _G0["base"]


def vr(g):
    if g["execution"]["status"] == "BLOCKED":
        return "BLOCKED", g["execution"]["missing"][0]
    o = g["outcome"]
    return o["value"], (o["reason"] if o["value"] == "FAIL" else None)


def gates(case, claim_id):
    cl = case.claims[claim_id]
    return {"G-BIND": vr(EV.g_bind(cl, case.bundle, case.anchors, case.config)),
            "G-INV": vr(EV.g_inv(cl, case.bundle, case.anchors)),
            "G-RECOMP": vr(C.g_recomp(cl, case.bundle, case.anchors))}


PASS = ("PASS", None)
# Escalation C-004-T024_2: the ledger's float cpu_s makes the RUN_INVENTORY custody blob uncomputable on a real
# inventory, so the keeper-row cases raise on the real base. They are expectedFailure until that is fixed (an
# unexpected success then turns the suite red, which is the signal to remove the marker).
KEEPER_ROW_CASES = ("E05.KEEPER", "E05.LATE_REG", "E05.FAB_REGISTERED")


class TestBuild(unittest.TestCase):
    def test_node_set_is_b9_g0(self):
        self.assertEqual(sorted(g0().dicts), sorted(F.g0_dicts()))
        self.assertEqual(len(g0().dicts), 25)

    def test_receipts_validate_and_are_real(self):
        for nid, d in g0().dicts.items():
            rc = R.Receipt.from_dict(d)
            self.assertEqual(rc.node_id, nid)
            self.assertEqual(d["execution"], {"status": "RAN", "missing": [], "run_id": "g0-test"})
            for out in d["outputs"]:
                b = g0().traces[nid][out["role"]]
                self.assertEqual((len(b), EV._sha(b)), (out["length"], out["sha256"]))

    def test_outcomes_are_the_contracts(self):
        # A6: every gate PASS and RETENTION POSITIVE for REG, PKTD, LAGD; ERASE(LAGD) FAIL (T04); TWIN PASS.
        for nid, d in g0().dicts.items():
            name = EV.parse_node_id(nid)[1]
            want = "POSITIVE" if name == "RETENTION" else ("FAIL" if nid == "rcpt:LAGD:ERASE:STANDARD" else "PASS")
            self.assertEqual(d["outcome"]["value"], want, nid)
        self.assertEqual(g0().dicts["rcpt:LAGD:ERASE:STANDARD"]["outcome"]["witness"],
                         {"history": 64, "partner": 0, "j": 3, "episode": 4, "tick": "PROBE_A"})

    def test_versions_are_import_closures_at_the_commit(self):
        for nid, d in g0().dicts.items():
            name = EV.parse_node_id(nid)[1]
            paths = sorted(c["role"][len("code:"):] for c in d["predicate"]["code"])
            self.assertEqual(paths, sorted(SB.slice_imports(SB.ENTRY[name])), nid)
            self.assertTrue(all(c["commit"] == _G0["commit"] for c in d["predicate"]["code"]), nid)

    def test_versions_match_committed_stage_records_when_present(self):
        # T023A / T023B records name versions at their own pin; same files => same blobs.
        import glob
        import json
        recs = {}
        for p in glob.glob(os.path.join(SB.REPO_ROOT, "rso", "slice001", "stages", "*.json")):
            with open(p, encoding="utf-8") as f:
                r = json.load(f)
            if isinstance(r, dict) and "instrument" in r and "version" in r:
                recs[r["instrument"]] = r["version"]
        if not recs:
            self.skipTest("no stage records on this tree")
        for nid, d in g0().dicts.items():
            pid = d["predicate"]["id"]
            if pid in recs:
                mine = sorted((c["role"], c["sha256"]) for c in d["predicate"]["code"])
                self.assertEqual(mine, sorted((c["role"], c["sha256"]) for c in recs[pid]), nid)

    def test_one_charged_top_level_build_row(self):
        inv = g0().inventory
        self.assertEqual([r["kind"] for r in inv], ["RUN", "TERMINAL"])
        self.assertEqual((inv[0]["node_id"], inv[0]["launch_kind"], inv[0]["status"]), ("G0", "TOP_LEVEL", "COMPLETED"))
        self.assertGreater(inv[0]["cpu_us"], 0)                   # C-004-T025: canonical-safe integer microseconds
        self.assertEqual(_G0["usage"]["launches"], 1)
        self.assertTrue(EV.inventory_terminal(inv))

    def test_per_receipt_rows_await_the_escalation(self):
        with self.assertRaises(NotImplementedError):
            SB.build_g0("0" * 40, None, rows="per_receipt")


class TestConsumerOnRealG0(unittest.TestCase):
    def test_g0_consistent_under_the_gates(self):
        case = F.g0(base())
        for cid in ("CL-RET(REG)", "CL-RET(PKTD)", "CL-RET(LAGD)", "CL-CAL(STANDARD)"):
            self.assertEqual(gates(case, cid), {"G-BIND": PASS, "G-INV": PASS, "G-RECOMP": PASS}, cid)
        for cid in ("TWIN(REG)", "CL-CUST(G0)"):
            g = gates(case, cid)
            self.assertEqual((g["G-BIND"], g["G-INV"]), (PASS, PASS), cid)

    def test_claim_cells_come_from_the_receipts(self):
        c = F.claims(base())
        cell = dict(g0().dicts["rcpt:REG:BOUNDS:STANDARD"]["cell"])
        del cell["measurement"]
        self.assertEqual(c["CL-RET(REG)"]["cell"], cell)
        self.assertEqual(F.claims(F.synthetic_base()), F.claims())


class TestEditsOnRealG0(unittest.TestCase):
    """Each B9 edit is a function of the base; on the real G0 it produces that E-case's bundle."""

    def test_every_registered_case_builds_on_the_real_base(self):
        for cid in sorted(set(F.CASES) - set(KEEPER_ROW_CASES)):
            case = F.case_for(cid, base())
            self.assertIsInstance(case, F.Case, cid)
            self.assertEqual(case.config.contract_revision, base().revision, cid)

    def test_e02_e03_typed_reasons(self):
        want = {"E03.BYTEFLIP": ("FAIL", "BYTES_MISMATCH:trace:probe_a"),
                "E03.STRIP": ("FAIL", "DEPENDENCY_MISMATCH:rcpt:REG:RETENTION:STANDARD->"
                                      "rcpt:WORLD:CALIBRATION:STANDARD"),
                "E02.MALFORMED": ("FAIL", "SCOPE_MALFORMED:boundary"),
                "E02.RELABEL": ("FAIL", "SCOPE_MISMATCH:physics"),
                "E02.MISSING": ("BLOCKED", "EVIDENCE_MISSING:rcpt:REG:PRESERVE:STANDARD")}
        for cid, w in sorted(want.items()):
            self.assertEqual(gates(F.case_for(cid, base()), "CL-RET(REG)")["G-BIND"], w, cid)
        self.assertEqual(gates(F.case_for("E03.BYTEFLIP", base()), "CL-RET(REG)")["G-RECOMP"],
                         ("FAIL", "BYTES_MISMATCH:trace:probe_a"))

    def test_missing_g_inv_with_a_build_row(self):
        # Escalation C-004-T024_1, option 1: one build row carries no per-node attribution, so the omitted
        # PRESERVE run is not RUN_UNREPORTED on the real G0 (the synthetic G0's X06 FAIL needs per-node rows).
        self.assertEqual(gates(F.case_for("E02.MISSING", base()), "CL-RET(REG)")["G-INV"], PASS)

    def test_e01_outcome_edit_caught_by_recomputation_on_real_traces(self):
        g = gates(F.case_for("E01.OUTCOME_EDIT", base()), "CL-RET(LAGD)")
        self.assertEqual(g["G-BIND"], PASS)                       # producer anchors re-made: binding passes
        self.assertEqual(g["G-RECOMP"], ("FAIL", "OUTCOME_MISMATCH:value"))

    def test_e01_fab_consistent_passes_the_gates(self):
        # B5.4 stated limit: another runtime's consistent bytes under REG's receipts are not detected.
        g = gates(F.case_for("E01.FAB_CONSISTENT", base()), "CL-RET(REG)")
        self.assertEqual(g, {"G-BIND": PASS, "G-INV": PASS, "G-RECOMP": PASS})

    def test_e03_reanchor_is_never_a_pass(self):
        g = gates(F.case_for("E03.REANCHOR", base()), "CL-RET(REG)")
        self.assertEqual(g["G-BIND"], PASS)
        self.assertEqual(g["G-RECOMP"][0], "FAIL")

    # expectedFailure removed by Palamedes at C-004-T025 integration: T024_2 fixed (cpu_us)
    def test_e05_fab_anchors_custody(self):
        fab = F.case_for("E05.FAB_ANCHORS", base())
        self.assertIn("ANCHORS_FROM_PRODUCER", EV.custody(fab.bundle, fab.anchors, fab.store, fab.first_check)["why"])

    # expectedFailure removed by Palamedes at C-004-T025 integration: T024_2 fixed (cpu_us)
    def test_e05_keeper_row_cases_on_the_real_base(self):
        for cid in KEEPER_ROW_CASES:
            F.case_for(cid, base())

    # expectedFailure removed by Palamedes at C-004-T025 integration: T024_2 fixed (cpu_us)
    def test_e05_custody_logic(self):
        k = F.case_for("E05.KEEPER", base())
        self.assertEqual(EV.custody(k.bundle, k.anchors, k.store, k.first_check)["status"], "QUALIFIED")
        late = F.case_for("E05.LATE_REG", base())
        self.assertEqual(EV.custody(late.bundle, late.anchors, late.store, late.first_check),
                         {"status": "UNQUALIFIED", "why": ["REGISTERED_AFTER_CHECK"]})

    def test_e04_withdrawals_target_real_nodes(self):
        w = F.case_for("E04.W_RESTART", base()).bundle.withdrawals[0]
        code = g0().dicts["rcpt:REG:RESTART:STANDARD"]["predicate"]["code"]
        self.assertEqual(w["target"], EV.stage_node_id("P6", EV.predicate_version(code)))
        self.assertEqual(F.case_for("E04.W_OBS", base()).bundle.withdrawals[0]["target"],
                         "rcpt:REG:OBSERVER:BOOKKEEP:STANDARD")

    def test_base_is_never_mutated(self):
        before = R.canonical_bytes(sorted(base()._dicts.items()))
        for cid in sorted(set(F.CASES) - set(KEEPER_ROW_CASES)):
            F.case_for(cid, base())
        self.assertEqual(R.canonical_bytes(sorted(base()._dicts.items())), before)


if __name__ == "__main__":
    unittest.main()
