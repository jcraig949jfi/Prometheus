"""Tests for the producer receipt, the three-field verdict and the authority stage (C-004-T013).

Contract: rso/slice001/contract/CONTRACT.md v1.0.0 + AMENDMENT_v1.0.1.md; draft B B2-B4, B7.2.
Every receipt, stage record and verdict here is an in-memory software fixture: never custody evidence
(CONTRACT.md s4; amendment V8). Stdlib only.
"""
import copy
import json
import unittest

from rso.slice001 import receipt as R

H = "ab" * 32          # a 64-hex sha256
H2 = "cd" * 32
C40 = "1" * 40         # a 40-hex commit


def code_ref(path="rso/slice001/world.py", sha=H):
    return {"role": "code:" + path, "sha256": sha, "length": 100, "commit": C40}


def art(role, sha=H):
    return {"role": role, "sha256": sha, "length": 10}


def ref(path="rso/slice001/contract/contract.json"):
    return {"path": path, "blob_sha256": H, "commit": C40}


def gate_outcome(pid="P4", value="PASS", applicable=12, witness=None, reason=None):
    return {"kind": "GATE", "predicate": pid, "value": value,
            "reason": reason or ("PRESERVE held" if value == "PASS" else "FAIL at (h, j)"),
            "witness": witness if value == "FAIL" else None,
            "eligible_count": 4096, "applicable_count": applicable,
            "vacuous": applicable == 0}


def ruler_outcome(value="POSITIVE", successes=12288, trials=12288, statistic="1/1"):
    return {"kind": "RULER", "ruler": "P2", "value": value, "statistic": statistic,
            "successes": successes, "trials": trials,
            "per_boundary": [{"j": 1, "statistic": "1/1"}, {"j": 2, "statistic": "1/1"},
                             {"j": 3, "statistic": "1/1"}],
            "reason": "RETENTION above exact bound 1/2"}


def cell():
    return {"cell_id": "W-S1", "revision": H, "physics": "REG " + H, "world": "STANDARD " + H,
            "boundary": "EPISODE_CONTENT_RESET j=1..3", "search": "NONE", "development": "NONE",
            "resources": H, "measurement": H, "exposure": "ref " + H}


def good_receipt(pid="P4", name="PRESERVE", status="RAN"):
    kind = "RULER" if pid == "P2" else "GATE"
    d = {
        "schema": "rso.slice001.receipt.v1",
        "node_id": "rcpt:REG:%s:STANDARD" % name,
        "registration_ref": ref("rso/slice001/contract/contract.json"),
        "contract_ref": ref(),
        "cell": cell(),
        "subject": {"id": "REG", "code": [code_ref("rso/slice001/fixtures/reg.py")]},
        "observer": None,
        "world": {"variant": "STANDARD", "code": [code_ref()]},
        "predicate": {"id": pid, "kind": kind, "code": [code_ref("rso/slice001/predicates.py")]},
        "code": {"producer": [code_ref("rso/slice001/adapter.py")], "base_sha": C40,
                 "branch": "argus/c004-t013", "worktree_path": "C:/x", "dirty": False},
        "inputs": {"domain": art("domain"), "reset_model_sha256": H},
        "outputs": [art("trace:probe_a"), art("trace:probe_d")],
        "oracle": art("oracle"),
        "expected_answer": {"table": ref("rso/slice001/expected/EXPECTED_ANSWERS.json"),
                            "row_id": "T01.REG." + name},
        "dependencies": ["rcpt:REG:BOUNDS:STANDARD"],
        "execution": {"status": "RAN", "missing": [], "run_id": "run-0001"},
        "outcome": ruler_outcome() if kind == "RULER" else gate_outcome(pid),
        "resources": {"cpu_seconds": 1, "wall_seconds": 1, "launches": 1, "artifact_bytes": 10},
        "limitations": ["draft A A7: not in the model"],
        "created_at_utc": "2026-10-04T02:00:00Z",
    }
    if status == "BLOCKED":
        d["execution"] = {"status": "BLOCKED", "missing": ["runtime inside the registered model"],
                          "run_id": "run-0002"}
        d["outcome"] = None
    return d


def stage_record(instrument="P4", stage="AUTHOR_TESTED", version=None):
    fs = {"date": "2026-10-05", "challenger": {"seat": "Pallas", "model": "claude-fable-5-1"},
          "set_ref": ref("rso/slice001/challenge/s3.json"),
          "sound_cases": {"correct": 5, "total": 5}, "broken_cases": {"correct": 4, "total": 5},
          "edits": {"proposed": 10, "applicable": 10, "duplicate": 0, "executed": 10, "killed": 8,
                    "survived": 1, "equivalent": 0, "error": 1, "timeout": 0},
          "unresolved": 0}
    rec = {"instrument": instrument,
           "version": version or [code_ref("rso/slice001/predicates.py")],
           "stage": stage,
           "fire_test": {"must_accept": ["T01.REG"],
                         "must_reject": [{"case_id": "T05.WIPE", "expected_reason": "FAIL"}],
                         "receipt": ref("ops/campaigns/C-004/tasks/C-004-T013/attempts/A-001/RECEIPT.json")},
           "first_sight": None, "closure": None,
           "recorded_by": "Argus[harry1-91cbacb8]", "recorded_at_utc": "2026-10-04T02:00:00Z"}
    if stage in ("FIRST_SIGHT_CHALLENGED", "CLOSED_AFTER_REPAIR"):
        rec["first_sight"] = fs
    if stage == "CLOSED_AFTER_REPAIR":
        cl = copy.deepcopy(fs)
        cl["date"] = "2026-10-06"
        cl["sound_cases"] = {"correct": 2, "total": 2}
        cl["broken_cases"] = {"correct": 2, "total": 2}
        cl["first_sight_preserved"] = copy.deepcopy(fs)
        rec["closure"] = cl
    return rec


def qualified(stage="AUTHOR_TESTED"):
    return {"status": "QUALIFIED", "stage": stage}


def unqualified(*why):
    return {"status": "UNQUALIFIED", "why": list(why) or ["NO_STAGE_RECORD"]}


class TestCanonicalBytes(unittest.TestCase):
    def test_sorted_compact_utf8(self):
        self.assertEqual(R.canonical_bytes({"b": 1, "a": [True, None, "x"]}),
                         b'{"a":[true,null,"x"],"b":1}')

    def test_floats_refused(self):
        with self.assertRaises(R.ReceiptError):
            R.canonical_bytes({"a": 0.5})
        with self.assertRaises(R.ReceiptError):
            R.canonical_bytes({"a": float("nan")})

    def test_loads_refuses_duplicate_keys_and_floats(self):
        with self.assertRaises(R.ReceiptError):
            R.loads_canonical(b'{"a":1,"a":2}')
        with self.assertRaises(R.ReceiptError):
            R.loads_canonical(b'{"a":1.0}')
        with self.assertRaises(R.ReceiptError):
            R.loads_canonical(b'{"a":NaN}')

    def test_round_trip_and_hash(self):
        r = R.Receipt.from_dict(good_receipt())
        again = R.Receipt.from_bytes(r.canonical_bytes())
        self.assertEqual(r.canonical_bytes(), again.canonical_bytes())
        self.assertEqual(len(r.sha256), 64)


class TestReceiptSchema(unittest.TestCase):
    def assertRefused(self, d, code):
        with self.assertRaises(R.ReceiptError) as cm:
            R.Receipt.from_dict(d)
        self.assertEqual(cm.exception.code, code)

    def test_good_receipts_accepted(self):
        for pid, name in (("P4", "PRESERVE"), ("P2", "RETENTION")):
            r = R.Receipt.from_dict(good_receipt(pid, name))
            self.assertEqual(r.node_id, "rcpt:REG:%s:STANDARD" % name)
        R.Receipt.from_dict(good_receipt(status="BLOCKED"))

    def test_every_missing_field_rejected(self):
        # RED item 1: missing-field rejection, one field at a time, typed reason.
        for f in R.RECEIPT_FIELDS:
            d = good_receipt()
            del d[f]
            self.assertRefused(d, "RECEIPT_SCHEMA:" + f)

    def test_execution_and_outcome_both_required(self):
        d = good_receipt()
        del d["execution"]["status"]
        self.assertRefused(d, "RECEIPT_SCHEMA:execution.status")
        d = good_receipt()
        d["outcome"] = None                      # RAN needs an outcome
        self.assertRefused(d, "RECEIPT_SCHEMA:outcome")
        d = good_receipt(status="BLOCKED")
        d["outcome"] = gate_outcome()            # BLOCKED must not carry one
        self.assertRefused(d, "RECEIPT_SCHEMA:outcome")
        d = good_receipt(status="BLOCKED")
        d["execution"]["missing"] = []           # BLOCKED names what was missing
        self.assertRefused(d, "RECEIPT_SCHEMA:execution.missing")

    def test_unknown_field_rejected(self):
        d = good_receipt()
        d["extra"] = 1
        self.assertRefused(d, "RECEIPT_SCHEMA:extra")

    def test_producer_authority_key_forbidden(self):
        # Cheat control (FD-B1): a producer receipt claiming QUALIFIED is refused whatever the stage.
        d = good_receipt()
        d["authority"] = qualified("AUTHOR_TESTED")
        self.assertRefused(d, "RECEIPT_SCHEMA:authority")

    def test_gate_ruler_vocabularies_kept_apart(self):
        d = good_receipt()
        d["outcome"]["value"] = "POSITIVE"
        self.assertRefused(d, "RECEIPT_SCHEMA:outcome.value")
        d = good_receipt("P2", "RETENTION")
        d["outcome"]["value"] = "PASS"
        self.assertRefused(d, "RECEIPT_SCHEMA:outcome.value")
        d = good_receipt("P2", "RETENTION")
        d["outcome"] = gate_outcome("P2")
        self.assertRefused(d, "RECEIPT_SCHEMA:outcome.kind")

    def test_no_indeterminate_slot(self):
        d = good_receipt()
        d["outcome"]["value"] = "INDETERMINATE"
        self.assertRefused(d, "RECEIPT_SCHEMA:outcome.value")

    def test_witness_and_vacuity_rules(self):
        d = good_receipt()
        d["outcome"]["witness"] = {"h": 1}       # PASS has no witness
        self.assertRefused(d, "RECEIPT_SCHEMA:outcome.witness")
        d = good_receipt()
        d["outcome"] = gate_outcome(value="FAIL", witness=None)
        self.assertRefused(d, "RECEIPT_SCHEMA:outcome.witness")
        d = good_receipt()
        d["outcome"]["applicable_count"] = 0     # vacuous must then be true
        self.assertRefused(d, "RECEIPT_SCHEMA:outcome.vacuous")
        d = good_receipt()
        d["outcome"] = gate_outcome(applicable=0)
        R.Receipt.from_dict(d)
        d = good_receipt()
        d["outcome"]["reason"] = ""
        self.assertRefused(d, "RECEIPT_SCHEMA:outcome.reason")

    def test_ruler_statistic_exact_rational(self):
        d = good_receipt("P2", "RETENTION")
        d["outcome"]["statistic"] = "12288/12288"   # not lowest terms
        self.assertRefused(d, "RECEIPT_SCHEMA:outcome.statistic")
        d = good_receipt("P2", "RETENTION")
        d["outcome"]["statistic"] = "1/2"           # disagrees with successes/trials
        self.assertRefused(d, "RECEIPT_SCHEMA:outcome.statistic")

    def test_node_id_uses_predicate_name(self):
        d = good_receipt()
        d["node_id"] = "rcpt:REG:P4:STANDARD"       # V1: NAME, not id
        self.assertRefused(d, "RECEIPT_SCHEMA:node_id")
        d = good_receipt()
        d["node_id"] = "rcpt:REG:ERASE:STANDARD"    # name of another predicate
        self.assertRefused(d, "RECEIPT_SCHEMA:node_id")
        self.assertEqual(R.make_node_id("REG", "OBSERVER", "STANDARD", observer="O1"),
                         "rcpt:REG:OBSERVER:O1:STANDARD")

    def test_trace_roles_and_dependencies(self):
        d = good_receipt()
        d["outputs"] = [art("trace:bogus")]
        self.assertRefused(d, "RECEIPT_SCHEMA:outputs")
        d = good_receipt()
        d["dependencies"] = ["rcpt:Z:BOUNDS:STANDARD", "rcpt:A:BOUNDS:STANDARD"]
        self.assertRefused(d, "RECEIPT_SCHEMA:dependencies")

    def test_floats_and_bools_not_ints(self):
        d = good_receipt()
        d["resources"]["cpu_seconds"] = 1.5
        self.assertRefused(d, "RECEIPT_SCHEMA:resources.cpu_seconds")
        d = good_receipt()
        d["resources"]["launches"] = True
        self.assertRefused(d, "RECEIPT_SCHEMA:resources.launches")

    def test_observer_only_for_p7(self):
        d = good_receipt()
        d["observer"] = {"id": "O1", "code": [code_ref()]}
        self.assertRefused(d, "RECEIPT_SCHEMA:observer")

    def test_limitations_never_empty(self):
        d = good_receipt()
        d["limitations"] = []
        self.assertRefused(d, "RECEIPT_SCHEMA:limitations")

    def test_receipt_is_immutable(self):
        src = good_receipt()
        r = R.Receipt.from_dict(src)
        before = r.canonical_bytes()
        src["node_id"] = "changed"
        view = r.to_dict()
        view["outcome"]["value"] = "FAIL"
        self.assertEqual(r.canonical_bytes(), before)
        with self.assertRaises(AttributeError):
            r.node_id = "x"


class TestVerdict(unittest.TestCase):
    def test_all_three_fields_required(self):
        # GREEN item: a verdict cannot be constructed without all three fields.
        full = {"node_id": "rcpt:REG:PRESERVE:STANDARD",
                "execution": {"status": "RAN", "missing": [], "run_id": "r1"},
                "authority": qualified(), "outcome": gate_outcome()}
        R.verdict_from_fields(full, required="PASS")
        for f in ("execution", "authority", "outcome"):
            d = copy.deepcopy(full)
            del d[f]
            with self.assertRaises(R.VerdictError) as cm:
                R.verdict_from_fields(d, required="PASS")
            self.assertEqual(cm.exception.code, "VERDICT_FIELD_MISSING:" + f)

    def test_standings(self):
        ran = {"status": "RAN", "missing": [], "run_id": "r1"}
        blk = {"status": "BLOCKED", "missing": ["completed run (Timeout)"], "run_id": "r2"}
        nid = "rcpt:REG:PRESERVE:STANDARD"
        v = R.make_verdict(nid, ran, qualified(), gate_outcome(), "PASS")
        self.assertEqual(v["standing"], "SATISFIED")
        v = R.make_verdict(nid, ran, qualified(), gate_outcome(value="FAIL", witness={"h": 3}), "PASS")
        self.assertEqual(v["standing"], "UNMET")
        v = R.make_verdict(nid, ran, unqualified("PRECONDITION:CALIBRATION"), gate_outcome(), "PASS")
        self.assertEqual(v["standing"], "UNQUALIFIED")
        self.assertEqual(v["reasons"], ["PRECONDITION:CALIBRATION"])
        v = R.make_verdict(nid, blk, unqualified("NO_STAGE_RECORD"), None, "PASS")
        self.assertEqual(v["standing"], "BLOCKED")
        self.assertEqual(v["reasons"], ["completed run (Timeout)"])
        # all three fields are carried, not replaced by the standing
        for k in ("execution", "authority", "outcome"):
            self.assertIn(k, v)

    def test_required_value_must_match_kind(self):
        ran = {"status": "RAN", "missing": [], "run_id": "r1"}
        with self.assertRaises(R.VerdictError):
            R.make_verdict("rcpt:REG:RETENTION:STANDARD", ran, qualified(), ruler_outcome(), "PASS")
        v = R.make_verdict("rcpt:AMN:RETENTION:STANDARD", ran, qualified(),
                           ruler_outcome("NEGATIVE", 6144, 12288, "1/2"), "POSITIVE")
        self.assertEqual(v["standing"], "UNMET")

    def test_eligibility_is_worst(self):
        ran = {"status": "RAN", "missing": [], "run_id": "r1"}
        blk = {"status": "BLOCKED", "missing": ["x"], "run_id": "r2"}
        sat = R.make_verdict("rcpt:A:ERASE:STANDARD", ran, qualified(), gate_outcome("P3"), "PASS")
        unmet = R.make_verdict("rcpt:A:PRESERVE:STANDARD", ran, qualified(),
                               gate_outcome(value="FAIL", witness={"h": 1}), "PASS")
        unq = R.make_verdict("rcpt:A:CHANNEL:STANDARD", ran, unqualified("PRECONDITION:RESTART"),
                             gate_outcome("P5"), "PASS")
        bl = R.make_verdict("rcpt:A:RESTART:STANDARD", blk, unqualified("NO_STAGE_RECORD"), None, "PASS")
        self.assertEqual(R.eligibility([sat])["eligibility"], "ELIGIBLE")
        e = R.eligibility([sat, unmet, unq])
        self.assertEqual((e["eligibility"], e["standing"]), ("NOT_ELIGIBLE", "UNQUALIFIED"))
        self.assertEqual(e["not_satisfied"], ["rcpt:A:CHANNEL:STANDARD", "rcpt:A:PRESERVE:STANDARD"])
        e = R.eligibility([unmet, bl, sat])
        self.assertEqual(e["standing"], "BLOCKED")
        self.assertEqual(len(e["not_satisfied"]), 2)   # the UNMET line is not hidden behind BLOCKED
        with self.assertRaises(R.VerdictError):
            R.eligibility([])


class TestStage(unittest.TestCase):
    def test_stage_records_validate(self):
        for s in R.STAGE_ORDER:
            R.validate_stage_record(stage_record(stage=s))

    def test_stage_record_shape_errors(self):
        rec = stage_record()
        rec["fire_test"]["must_reject"] = []          # a gate that only accepts has no fire test
        with self.assertRaises(R.StageError):
            R.validate_stage_record(rec)
        rec = stage_record(stage="FIRST_SIGHT_CHALLENGED")
        rec["first_sight"] = None
        with self.assertRaises(R.StageError):
            R.validate_stage_record(rec)
        rec = stage_record(stage="CLOSED_AFTER_REPAIR")
        rec["closure"]["first_sight_preserved"]["sound_cases"] = {"correct": 5, "total": 6}
        with self.assertRaises(R.StageError):                # first-sight figures kept unchanged
            R.validate_stage_record(rec)
        rec = stage_record()
        rec["first_sight"] = stage_record(stage="FIRST_SIGHT_CHALLENGED")["first_sight"]
        with self.assertRaises(R.StageError):                # AUTHOR_TESTED carries no challenge
            R.validate_stage_record(rec)

    def test_lowest_stage_inheritance(self):
        # RED item 2: a claim inherits the lowest stage among its prerequisites (gates and rulers).
        self.assertEqual(R.lowest_stage(["CLOSED_AFTER_REPAIR", "AUTHOR_TESTED",
                                         "FIRST_SIGHT_CHALLENGED"]), "AUTHOR_TESTED")
        self.assertEqual(R.lowest_stage(["CLOSED_AFTER_REPAIR", "FIRST_SIGHT_CHALLENGED"]),
                         "FIRST_SIGHT_CHALLENGED")
        ran = {"status": "RAN", "missing": [], "run_id": "r1"}
        vs = [R.make_verdict("rcpt:A:ERASE:STANDARD", ran, qualified("CLOSED_AFTER_REPAIR"),
                             gate_outcome("P3"), "PASS"),
              R.make_verdict("rcpt:A:RETENTION:STANDARD", ran, qualified("FIRST_SIGHT_CHALLENGED"),
                             ruler_outcome(), "POSITIVE")]
        self.assertEqual(R.inherited_authority(vs), qualified("FIRST_SIGHT_CHALLENGED"))
        vs.append(R.make_verdict("rcpt:A:PRESERVE:STANDARD", ran, unqualified("WITHDRAWN:W1"),
                                 gate_outcome(), "PASS"))
        self.assertEqual(R.inherited_authority(vs),
                         {"status": "UNQUALIFIED", "why": ["rcpt:A:PRESERVE:STANDARD: WITHDRAWN:W1"]})
        with self.assertRaises(R.StageError):
            R.lowest_stage([])
        with self.assertRaises(R.StageError):
            R.lowest_stage(["AUTHOR_TESTED", "SOMEWHAT_TESTED"])

    def test_s2_every_claim_author_tested(self):
        ran = {"status": "RAN", "missing": [], "run_id": "r1"}
        vs = [R.make_verdict("rcpt:A:%s:STANDARD" % n, ran, qualified("AUTHOR_TESTED"),
                             gate_outcome(p), "PASS") for p, n in (("P3", "ERASE"), ("P4", "PRESERVE"))]
        self.assertEqual(R.inherited_authority(vs), qualified("AUTHOR_TESTED"))


class TestAuthorityCheatControl(unittest.TestCase):
    """GREEN cheat control: QUALIFIED above what the registered stage record says is refused."""

    def setUp(self):
        self.rcpt = R.Receipt.from_dict(good_receipt())
        self.at = stage_record("P4", "AUTHOR_TESTED")

    def test_qualified_at_registered_stage_accepted(self):
        v = R.verdict_for_receipt(self.rcpt, qualified("AUTHOR_TESTED"), "PASS", [self.at])
        self.assertEqual(v["standing"], "SATISFIED")

    def test_qualified_above_author_tested_refused(self):
        for claimed in ("FIRST_SIGHT_CHALLENGED", "CLOSED_AFTER_REPAIR"):
            with self.assertRaises(R.AuthorityRefused) as cm:
                R.verdict_for_receipt(self.rcpt, qualified(claimed), "PASS", [self.at])
            self.assertEqual(cm.exception.code,
                             "STAGE_EXCEEDS_RECORD:%s>AUTHOR_TESTED" % claimed)

    def test_qualified_without_record_refused(self):
        with self.assertRaises(R.AuthorityRefused) as cm:
            R.verdict_for_receipt(self.rcpt, qualified(), "PASS", [])
        self.assertEqual(cm.exception.code, "NO_STAGE_RECORD")

    def test_record_for_other_version_does_not_count(self):
        other = stage_record("P4", "CLOSED_AFTER_REPAIR",
                             version=[code_ref("rso/slice001/predicates.py", sha=H2)])
        with self.assertRaises(R.AuthorityRefused) as cm:
            R.verdict_for_receipt(self.rcpt, qualified("CLOSED_AFTER_REPAIR"), "PASS", [other])
        self.assertEqual(cm.exception.code, "NO_STAGE_RECORD")

    def test_record_for_other_instrument_does_not_count(self):
        with self.assertRaises(R.AuthorityRefused):
            R.verdict_for_receipt(self.rcpt, qualified(), "PASS", [stage_record("P3")])

    def test_unqualified_needs_no_record(self):
        v = R.verdict_for_receipt(self.rcpt, unqualified("NO_STAGE_RECORD"), "PASS", [])
        self.assertEqual(v["standing"], "UNQUALIFIED")

    def test_highest_registered_record_for_version_bounds_the_claim(self):
        fs = stage_record("P4", "FIRST_SIGHT_CHALLENGED")
        v = R.verdict_for_receipt(self.rcpt, qualified("FIRST_SIGHT_CHALLENGED"), "PASS",
                                  [self.at, fs])
        self.assertEqual(v["authority"], qualified("FIRST_SIGHT_CHALLENGED"))


class TestContractAlignment(unittest.TestCase):
    """The module's vocabularies are the frozen contract's, not a private copy that can drift."""

    def test_vocabularies_match_contract_json(self):
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "contract", "contract.json")
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
        self.assertEqual(c["receipt"]["schema"], R.SCHEMA)
        self.assertEqual(list(c["receipt"]["standing_order"]), list(R.STANDING_ORDER))
        self.assertEqual(list(c["authority_stages"]["order"]), list(R.STAGE_ORDER))
        self.assertEqual(sorted(c["receipt"]["trace_roles"]), sorted(R.TRACE_ROLES))
        self.assertEqual(sorted(c["receipt"]["gate_outcome"]), sorted(R.GATE_VALUES))
        self.assertEqual(sorted(c["receipt"]["ruler_outcome"]), sorted(R.RULER_VALUES))
        names = {g["id"]: g["name"] for g in c["gates"] if g["id"].startswith("P")}
        self.assertEqual(names, dict(R.PREDICATE_NAMES))
        kinds = {g["id"]: g["kind"] for g in c["gates"] if g["id"].startswith("P")}
        self.assertEqual(kinds, {p: R.PREDICATE_KINDS[p] for p in kinds})


if __name__ == "__main__":
    unittest.main()
