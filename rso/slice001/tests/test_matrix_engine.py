"""Tests for the S2 comparison engine (rso/slice001/matrix.py), prepared ahead of C-004-T020.

These test the comparator only, on synthetic rows plus the real independent table's shape. The T020 matrix run
itself (implementation rows for all registered cases) is tests/test_matrix.py, written at T020.
"""
import copy
import unittest

from rso.slice001 import matrix as M


def row(cid="T99.X", outcome="PASS", reason="ok", **kw):
    r = {"id": cid, "primary": {"predicate": "ERASE", "scope": "REG", "execution": "RAN",
                                "authority": "QUALIFIED@AUTHOR_TESTED", "outcome": outcome, "reason": reason},
         "other_verdicts": [], "claims": []}
    r["primary"].update(kw)
    return r


class TestFieldRules(unittest.TestCase):
    def test_identical_rows_agree(self):
        e = row()
        self.assertEqual(M.compare_row(e, copy.deepcopy(e))["status"], M.AGREE)

    def test_outcome_difference_is_a_mismatch(self):
        r = M.compare_row(row(outcome="FAIL"), row(outcome="PASS"))
        self.assertEqual(r["status"], M.DISAGREE)
        self.assertIn("outcome", [f["field"] for f in r["fields"] if f["status"] == M.MISMATCH])

    def test_undetermined_is_never_a_match(self):
        r = M.compare_row(row(outcome="UNDETERMINED (G04)"), row(outcome="POSITIVE"))
        f = [x for x in r["fields"] if x["field"] == "outcome"][0]
        self.assertEqual(f["status"], M.NOT_COMPARED)
        self.assertNotEqual(r["status"], M.AGREE)

    def test_placeholder_reason_is_a_pattern(self):
        e = row(outcome="FAIL", reason="forbidden influence across boundary 1, first visible at <episode, tick>")
        good = row(outcome="FAIL", reason="forbidden influence across boundary 1, first visible at (2, PROBE_A)")
        bad = row(outcome="FAIL", reason="forbidden influence across boundary 2, first visible at (3, PROBE_A)")
        self.assertEqual(M.compare_row(e, good)["status"], M.AGREE)
        self.assertEqual(M.compare_row(e, bad)["status"], M.DISAGREE)

    def test_pass_reason_wording_is_not_compared(self):
        e = row(outcome="PASS", reason="no forbidden influence across boundaries 1-3 within H = 3")
        a = row(outcome="PASS", reason="no forbidden influence across boundaries 1-3 within the horizon")
        r = M.compare_row(e, a)
        f = [x for x in r["fields"] if x["field"] == "reason"][0]
        self.assertEqual(f["status"], M.NOT_APPLICABLE)
        self.assertEqual(r["status"], M.AGREE)

    def test_fail_reason_still_compared(self):
        e = row(outcome="FAIL", reason="forbidden influence across boundary 1, first visible at <episode, tick>")
        a = row(outcome="FAIL", reason="forbidden influence across boundary 3, first visible at (4, PROBE_A)")
        self.assertEqual(M.compare_row(e, a)["status"], M.DISAGREE)

    def test_undetermined_among_alternatives(self):
        e = row(outcome="FAIL", reason="UNDETERMINED among SCOPE_MISMATCH:physics | IDENTITY_UNKNOWN:<node_id> (G08)")
        st, note = M.reason_matches(e["primary"]["reason"], "IDENTITY_UNKNOWN:rcpt:REG2:BOUNDS:STANDARD")
        self.assertEqual(st, M.NOT_COMPARED)
        self.assertIn("IDENTITY_UNKNOWN", note)
        st, _ = M.reason_matches(e["primary"]["reason"], "BYTES_MISMATCH:receipt")
        self.assertEqual(st, M.MISMATCH)

    def test_counts_and_claims_compared(self):
        e = row(statistic="1/2", successes=6144, trials=12288)
        e["claims"] = [{"claim": "CL-RET(AMNESIAC)", "eligibility": "NOT_ELIGIBLE", "standing": "UNMET"}]
        a = copy.deepcopy(e)
        a["primary"]["successes"] = 6145
        a["claims"][0]["standing"] = "UNQUALIFIED"
        bad = {(f["where"], f["field"]) for f in M.compare_row(e, a)["fields"] if f["status"] == M.MISMATCH}
        self.assertEqual(bad, {("primary", "successes"), ("claim:CL-RET(AMNESIAC)", "standing")})


class TestMatrix(unittest.TestCase):
    def setUp(self):
        self.exp = {"T01.A": row("T01.A"), "T02.B": row("T02.B", outcome="NEGATIVE"),
                    "E06.C": row("E06.C")}
        self.exit = {"T01.A": True, "T02.B": True, "E06.C": False}

    def test_missing_case_fails_never_passes(self):
        rep = M.compare(self.exp, {"T01.A": row("T01.A"), "E06.C": row("E06.C")}, self.exit)
        self.assertIn("T02.B", rep["unresolved_gating"])
        self.assertFalse(rep["exit_ok"])

    def test_non_exit_case_is_reported_not_gating(self):
        act = {"T01.A": row("T01.A"), "T02.B": row("T02.B", outcome="NEGATIVE"), "E06.C": row("E06.C", outcome="FAIL")}
        rep = M.compare(self.exp, act, self.exit)
        self.assertTrue(rep["exit_ok"])
        self.assertEqual([r["status"] for r in rep["results"] if r["id"] == "E06.C"], [M.DISAGREE])

    def test_extra_row_blocks_exit(self):
        act = {k: copy.deepcopy(v) for k, v in self.exp.items()}
        act["T77.UNREGISTERED"] = row("T77.UNREGISTERED")
        rep = M.compare(self.exp, act, self.exit)
        self.assertEqual(rep["extra"], ["T77.UNREGISTERED"])
        self.assertFalse(rep["exit_ok"])

    def test_cheat_control_always_match_comparator_is_caught(self):
        # if compare_row were replaced by one that says AGREE for everything, a real outcome flip must still
        # surface somewhere: this asserts the genuine comparator reports it.
        act = {k: copy.deepcopy(v) for k, v in self.exp.items()}
        act["T02.B"]["primary"]["outcome"] = "POSITIVE"
        rep = M.compare(self.exp, act, self.exit)
        self.assertEqual(rep["unresolved_gating"], ["T02.B"])
        self.assertEqual(rep["classification"], {"T02.B": "UNCLASSIFIED"})

    def test_cheat_control_undetermined_everywhere_does_not_pass(self):
        act = {}
        for k, v in self.exp.items():
            a = copy.deepcopy(v)
            for f in ("execution", "authority", "outcome", "reason"):
                a["primary"][f] = "UNDETERMINED"
            act[k] = a
        rep = M.compare(self.exp, act, self.exit)
        self.assertFalse(rep["exit_ok"])
        self.assertEqual(sorted(rep["unresolved_gating"]), ["T01.A", "T02.B"])

    def test_render_is_ascii(self):
        rep = M.compare(self.exp, {}, self.exit)
        txt = M.render(rep)
        txt.encode("ascii")
        self.assertIn("exit: NOT OK", txt)


class TestRealTableShape(unittest.TestCase):
    def test_every_registered_case_has_one_table_row(self):
        exp = M.load_expected()
        flags = M.exit_flags()
        self.assertEqual(set(exp), set(flags))
        self.assertEqual(len(exp), 48)
        self.assertEqual(sorted(k for k, v in flags.items() if not v), ["E06.LOSSY", "E06.REG_FLAT", "E06.REG_ONEHOT"])

    def test_table_against_itself_never_disagrees(self):
        exp = M.load_expected()
        rep = M.compare(exp, copy.deepcopy(exp), M.exit_flags())
        self.assertEqual(rep["unresolved_gating"], [])
        self.assertNotIn(M.DISAGREE, rep["counts"])

    def test_register_items_name_real_cases(self):
        exp = M.load_expected()
        for cid in M.REGISTER:
            self.assertIn(cid, exp)


if __name__ == "__main__":
    unittest.main()
