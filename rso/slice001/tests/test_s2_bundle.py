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
# The E05 cases that write keeper rows (they hash the real inventory; fixed by C-004-T025, cpu_us).
KEEPER_ROW_CASES = ("E05.KEEPER", "E05.LATE_REG", "E05.FAB_REGISTERED")


class TestBuild(unittest.TestCase):
    def test_node_set_is_b9_g0(self):
        self.assertEqual(sorted(g0().dicts), sorted(F.g0_dicts()))
        self.assertEqual(len(g0().dicts), 25)

    def test_receipts_validate_and_are_real(self):
        for nid, d in g0().dicts.items():
            rc = R.Receipt.from_dict(d)
            self.assertEqual(rc.node_id, nid)
            self.assertEqual(d["execution"], {"status": "RAN", "missing": [], "run_id": "g0-test/" + nid})
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

    def test_one_launch_and_one_receipt_row_per_receipt(self):
        # C-004-T026 (escalation C-004-T024_1, option 2): 1 TOP_LEVEL build row + 25 RECEIPT rows (V7).
        inv = g0().inventory
        runs, term = inv[:-1], inv[-1]
        self.assertEqual(term, {"kind": "TERMINAL", "row_count": 26})
        self.assertEqual([(r["node_id"], r["launch_kind"]) for r in runs if r["launch_kind"] == "TOP_LEVEL"],
                         [("G0", "TOP_LEVEL")])
        rec = {r["node_id"]: r for r in runs if r["launch_kind"] == "RECEIPT"}
        self.assertEqual(sorted(rec), sorted(g0().dicts))
        for nid, d in g0().dicts.items():
            self.assertEqual((rec[nid]["run_id"], rec[nid]["status"]), (d["execution"]["run_id"], "COMPLETED"))
        self.assertTrue(all(isinstance(r["cpu_us"], int) for r in runs))   # C-004-T025: integer microseconds
        self.assertEqual(_G0["usage"]["launches"], 1)
        self.assertTrue(EV.inventory_terminal(inv))

    def test_unknown_rows_mode_is_refused(self):
        with self.assertRaises(ValueError):
            SB.build_g0("0" * 40, _NullLedger(), rows="per_node")


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

    def test_missing_g_inv_run_unreported(self):
        # V7 / X06 on the real G0 (C-004-T026): the omitted PRESERVE receipt's own RECEIPT row is reported
        # COMPLETED, so G-INV attributes it to CL-RET(REG).
        run = g0().dicts["rcpt:REG:PRESERVE:STANDARD"]["execution"]["run_id"]
        self.assertEqual(gates(F.case_for("E02.MISSING", base()), "CL-RET(REG)")["G-INV"],
                         ("FAIL", "RUN_UNREPORTED:%s" % run))
        self.assertEqual(gates(F.case_for("E02.MISSING", base()), "CL-RET(PKTD)")["G-INV"], PASS)   # V7

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


class _NullLedger(object):
    def begin(self, *a, **k):
        raise AssertionError("no ledger row may be written for a refused build")


# --------------------------------------------------------------------------------------------------------
# build_bundle over subjects outside G0 (C-004-T026): WIPE (sound in the model, fails PRESERVE: T05) and
# OVERDELAY (leaves the model: K = 3 exceeded).

_B = {}


def wipe_overdelay(rows="per_receipt"):
    if rows not in _B:
        d = tempfile.mkdtemp(prefix="rso-bundle-")
        try:
            led = L.Ledger.from_contract(os.path.join(d, "ledger.jsonl"))
            _B[rows] = SB.build_bundle(_commit(), led, ["WIPE", "OVERDELAY"], run_id="b-test", rows=rows,
                                       created_at_utc="2026-10-04T00:00:00Z")
        finally:
            shutil.rmtree(d, ignore_errors=True)
    return _B[rows]


def _commit():
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=SB.REPO_ROOT, capture_output=True,
                          text=True).stdout.strip()


def committed_stage_records():
    """The committed T023A/T023B stage records and their fire-receipt blobs, as a registered fixture store."""
    import glob
    import json
    recs, blobs = [], {}
    for p in sorted(glob.glob(os.path.join(SB.REPO_ROOT, "rso", "slice001", "stages", "*.json"))):
        with open(p, encoding="utf-8") as f:
            r = json.load(f)
        if isinstance(r, dict) and "instrument" in r and "fire_test" in r:
            recs.append(r)
            path = r["fire_test"]["receipt"]["path"]
            with open(os.path.join(SB.REPO_ROOT, *path.split("/")), "rb") as f:
                blobs[path] = f.read().replace(b"\r\n", b"\n")
    return recs, blobs


def decide(bundle_g, subject, observers=("NULL",)):
    recs, blobs = committed_stage_records()
    bundle = EV.Bundle({n: R.Receipt.from_dict(d).canonical_bytes() for n, d in bundle_g.dicts.items()},
                       bundle_g.traces, bundle_g.inventory, stage_records=recs, blobs=blobs)
    store = EV.FixtureStore([F.row("STAGE_RECORD", EV.record_blob(r)) for r in recs])
    anchors = EV.Anchors(bundle_g.manifest, "keeper")
    some = next(iter(bundle_g.dicts.values()))
    gate_versions = {r["instrument"]: r["version"] for r in recs if r["instrument"] in C.GATES}
    consumer = C.Consumer(bundle, anchors, store, EV.Config(some["cell"]["revision"]), gate_versions,
                          F.FIRST_CHECK)
    cell = dict(bundle_g.dicts[R.make_node_id(subject, "BOUNDS", "STANDARD")]["cell"])
    del cell["measurement"]
    return consumer.decide(EV.make_claim("CL-RET", subject, observers=observers, cell=cell))


class TestBuildBundle(unittest.TestCase):
    def test_subjects_outside_g0_get_the_g0_receipt_set(self):
        b = wipe_overdelay()
        want = {"rcpt:WORLD:CALIBRATION:STANDARD"}
        for m in ("WIPE", "OVERDELAY"):
            want |= {R.make_node_id(m, n, "STANDARD") for n in SB.SUBJECT_NAMES}
            want.add(R.make_node_id(m, "OBSERVER", "STANDARD", observer="NULL"))
        self.assertEqual(sorted(b.dicts), sorted(want))

    def test_overdelay_is_blocked_not_raised(self):
        b = wipe_overdelay()
        bounds = b.dicts["rcpt:OVERDELAY:BOUNDS:STANDARD"]
        self.assertEqual((bounds["execution"]["status"], bounds["outcome"]["value"]), ("RAN", "FAIL"))
        for nid, d in b.dicts.items():
            if nid.startswith("rcpt:OVERDELAY:") and nid != "rcpt:OVERDELAY:BOUNDS:STANDARD":
                self.assertEqual(d["execution"]["status"], "BLOCKED", nid)
                self.assertEqual(d["execution"]["missing"], ["BOUNDS_VIOLATION:DELAY_RANGE"], nid)
                self.assertIsNone(d["outcome"], nid)

    def test_wipe_fails_preserve_t05(self):
        d = wipe_overdelay().dicts["rcpt:WIPE:PRESERVE:STANDARD"]
        self.assertEqual(d["outcome"]["value"], "FAIL")

    def test_consumer_decisions(self):
        b = wipe_overdelay()
        self.assertEqual(decide(b, "WIPE")["eligibility"], "NOT_ELIGIBLE")
        self.assertEqual(decide(b, "OVERDELAY")["standing"], "BLOCKED")

    def test_one_launch_rows_attribute_every_receipt(self):
        inv = wipe_overdelay().inventory
        self.assertEqual(sum(1 for r in inv[:-1] if r["launch_kind"] == "TOP_LEVEL"), 1)
        self.assertEqual(sorted(r["node_id"] for r in inv[:-1] if r["launch_kind"] == "RECEIPT"),
                         sorted(wipe_overdelay().dicts))

    def test_rows_mode_changes_only_run_ids_and_inventory(self):
        a, b = wipe_overdelay("per_receipt"), wipe_overdelay("build")
        self.assertEqual(sorted(a.dicts), sorted(b.dicts))
        for nid in a.dicts:
            x, y = dict(a.dicts[nid]), dict(b.dicts[nid])
            x["execution"], y["execution"] = dict(x["execution"], run_id=""), dict(y["execution"], run_id="")
            x["resources"], y["resources"] = None, None              # measured CPU differs run to run
            self.assertEqual(R.canonical_bytes(x), R.canonical_bytes(y), nid)
            self.assertEqual(a.traces[nid], b.traces[nid], nid)
        self.assertEqual(b.dicts["rcpt:WIPE:ERASE:STANDARD"]["execution"]["run_id"], "b-test")
        self.assertEqual([r["launch_kind"] for r in b.inventory[:-1]], ["TOP_LEVEL"])

    def test_two_twins_for_one_subject_are_refused(self):
        with self.assertRaises(SB.BuildError):
            SB.build_bundle("0" * 40, _NullLedger(), ["REG"], twins=[("REG", "REG_FLAT"), ("REG", "LOSSY")])


if __name__ == "__main__":
    unittest.main()
