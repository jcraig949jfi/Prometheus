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


if __name__ == "__main__":
    unittest.main()
