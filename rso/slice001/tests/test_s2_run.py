"""Driver checks for the T020 matrix run (rso/slice001/s2_run.py) that need no bundle build."""
import unittest

from rso.slice001 import matrix as M
from rso.slice001 import s2_run as S


class TestNoSeeding(unittest.TestCase):
    def test_silent_consumer_never_agrees(self):
        # cheat control for the seeding bug: with no consumer lines at all, every resolvable field is absent,
        # so a row can only DISAGREE (or be MISSING) -- never AGREE by echoing the expected row.
        exp = M.load_expected()
        rows = {}
        for cid in ("T01.REG", "T04.LAGD", "E01.G0", "T07.BOOKKEEP"):
            e = exp[cid]
            rows[cid] = {"id": cid,
                         "primary": S._actual(e["primary"], {}, {"status": None, "why": []}, ["REG"]),
                         "other_verdicts": [S._actual(v, {}, {"status": None, "why": []}, ["REG"])
                                            for v in e.get("other_verdicts", [])],
                         "claims": [S.claim_row(c["claim"], {}) for c in e.get("claims", [])]}
            r = M.compare_row(e, rows[cid])
            self.assertEqual(r["status"], M.DISAGREE, cid)

    def test_actual_carries_only_consumer_fields(self):
        e = {"predicate": "ERASE", "scope": "REG", "outcome": "PASS", "statistic": "1/1", "reason": "x"}
        a = S._actual(e, {}, {"status": None, "why": []}, ["REG"])
        self.assertEqual(a, {"predicate": "ERASE", "scope": "REG"})

    def test_reported_twin_eligibility_not_applicable(self):
        e = {"id": "X", "primary": {"predicate": "TWIN_EQ", "outcome": "PASS"}, "other_verdicts": [],
             "claims": [{"claim": "TWIN(REG, REG-ONEHOT)", "eligibility": "REPORTED", "standing": "SATISFIED"}]}
        a = {"id": "X", "primary": {"predicate": "TWIN_EQ", "outcome": "PASS"}, "other_verdicts": [],
             "claims": [{"claim": "TWIN(REG, REG-ONEHOT)", "eligibility": "ELIGIBLE", "standing": "SATISFIED"}]}
        self.assertEqual(M.compare_row(e, a)["status"], M.AGREE)


class TestProduceContract(unittest.TestCase):
    def test_contract_option_reaches_produce_and_defaults_to_the_slice_contract(self):
        from unittest import mock
        with mock.patch.object(S, "produce", return_value={}) as p:
            S.main(["produce", "--commit", "c", "--ledger", "l.jsonl", "--contract", "k.json"])
            p.assert_called_once_with("c", "l.jsonl", contract="k.json")
        with mock.patch.object(S, "produce", return_value={}) as p:
            S.main(["produce", "--commit", "c", "--ledger", "l.jsonl"])
            p.assert_called_once_with("c", "l.jsonl", contract=S.L.DEFAULT_CONTRACT)

    def test_produce_charges_the_ledger_under_the_given_contract(self):
        from unittest import mock
        with mock.patch.object(S.L.Ledger, "from_contract", side_effect=RuntimeError("stop")) as fc:
            with self.assertRaises(RuntimeError):
                S.produce("c", "l.jsonl", contract="k.json")
            fc.assert_called_once_with("l.jsonl", "k.json")


class TestProductionRunJson(unittest.TestCase):
    """C-009-T031 R3 (B1.PROBE.PRODUCTION_RUNJSON): s2_run.consumer_for passes run_id = g.run_id, so the production
    consume path and the fixture path agree on a run.json that names another launch (LAUNCH_UNBOUND on both)."""

    def test_paths_agree(self):
        from rso.binding.challenge.B1 import cases as B1C
        from rso.slice001 import s2_run as SR
        from rso.slice001.fixtures import evidence_cases as F
        from rso.slice001.tests.test_evidence import r1_g0
        recs, blobs = SR.stage_records()
        dec_a, _cust_a, rid_a, dec_b, _cust_b = B1C.probe_production_runjson(r1_g0(), recs, blobs, F.FIRST_CHECK)
        self.assertEqual(rid_a, B1C.SUBSTITUTE)
        for claim in ("CL-RET(REG)", "CL-CAL(STANDARD)"):
            line = [ln for ln in dec_a[claim]["prerequisites"] if ln.get("predicate") == "G-INV"]
            self.assertTrue(line, claim)
            self.assertEqual(line[0]["verdict"]["outcome"]["reason"], "LAUNCH_UNBOUND", claim)
            self.assertEqual(dec_a[claim], dec_b[claim], claim)


if __name__ == "__main__":
    unittest.main()
