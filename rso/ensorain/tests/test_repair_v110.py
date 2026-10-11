"""C-016-T041 behavioural pins for the v1.1.0 repair (PREREGISTRATION.md v1.1.0; rso/ensorain/challenge/REPORT.md
s4.4). Each test named in rso/ensorain/repair_v110/RED_EDITS.json is RED on its mutant applied verbatim (Pallas's
E1 E2 E3 E4 E6 from challenge/edits.json, plus this round's own repairs). Development seeds only.

    python -B -m unittest rso.ensorain.tests.test_repair_v110 -v
"""
import copy
import unittest

import numpy as np

from rso.ensorain import analysis, assay, subjects
from rso.ensorain.challenge import subjects_c as C

DEV = [16_300_401 + i for i in range(40)]           # development lives not used by DEV_QUALIFICATION / DEV_CHECK


def _row(subject, arm, seed, pre=True, late=False, r5=True):
    """A synthetic row: role 1 correct before the switch iff `pre`, in the late window iff `late`."""
    return dict(subject=subject, arm=arm, seed=seed, sw=6, c_pre=10 if pre else 0, n_pre=10, c_early=0, n_early=10,
                c_late=10 if late else 0, n_late=10, c5=10 if r5 else 0, n5=10, c5_post=10 if r5 else 0, n5_post=10,
                memory_ok=True, recompute_ok=True)


def _subject(name, n, full, frozen, noise, shuffle, pre_full=None, r5=None):
    """Rows of one subject; full / frozen / noise / shuffle are the per-life `revised` outcomes (lists of bools)."""
    rows = []
    for i in range(n):
        p = True if pre_full is None else pre_full[i]
        k = True if r5 is None else r5[i]
        rows.append(_row(name, "full", i, pre=p, late=full[i], r5=k))
        for arm, rv in (("frozen", frozen), ("noise", noise), ("shuffle", shuffle)):
            rows.append(_row(name, arm, i, pre=rv[i] or arm != "frozen", late=rv[i]))
        rows += [_row(name, "newlife", i), _row(name, "noswitch", i, late=True)]
    return rows


def _v(rows, n):
    return analysis.verdicts(rows, n_required=n)


class Inference(unittest.TestCase):
    def test_holm_decides_not_the_raw_p(self):                     # E1 (W1: 26:14 of 40, raw .0403, Holm .0807)
        n = 40
        full = [i < 26 for i in range(n)]
        ctrl = [i >= 26 for i in range(n)]
        v = _v(_subject("s", n, full, ctrl, ctrl, full), n)["s"]
        self.assertEqual((v["K1"]["wins"], v["K1"]["losses"]), (26, 14))
        self.assertLess(float(v["K1"]["p"]), 0.05)
        self.assertGreater(v["holm"]["K1"], 0.05)
        self.assertEqual(v["verdict"], "REVISION_NOT_SHOWN")

    def test_k1_is_against_frozen_and_k2_against_shuffle(self):     # E4
        n = 40
        yes, no = [True] * n, [False] * n
        v = _v(_subject("s", n, yes, no, no, yes), n)["s"]
        self.assertEqual(v["verdict"], "REVISION_NOT_HISTORY_DEPENDENT")
        v = _v(_subject("s", n, yes, yes, no, no), n)["s"]            # frozen revises: K1 must fail
        self.assertEqual(v["verdict"], "REVISION_NOT_SHOWN")

    def test_k1_needs_the_noise_matched_arm_too(self):              # jitter's class: frozen 0, noise = full
        n = 40
        full = [i < 19 for i in range(n)]
        v = _v(_subject("s", n, full, [False] * n, full, full), n)["s"]
        self.assertEqual((v["K1_noise"]["wins"], v["K1_noise"]["losses"]), (0, 0))
        self.assertEqual(v["verdict"], "REVISION_NOT_SHOWN")

    def test_endpoint_is_the_whole_life(self):
        r = _row("s", "full", 0, pre=False, late=True)              # the Smuggler's life: late-perfect, never pre
        self.assertFalse(analysis.revised(r))
        self.assertTrue(analysis.revised(_row("s", "full", 0, pre=True, late=True)))


class Gates(unittest.TestCase):
    def test_gpre_counts_the_full_arm(self):                        # E2 (W2: learns_pre's frozen arm is -s)
        n = 40
        yes, no = [True] * n, [False] * n
        rows = _subject("s", n, yes, no, no, no)
        for r in rows:
            if r["arm"] == "frozen":
                r["c_pre"] = 0
        v = _v(rows, n)["s"]
        self.assertTrue(v["G_PRE"])
        self.assertEqual(v["verdict"], "REVISION_HISTORY_DEPENDENT")

    def test_gpre_threshold_is_the_exact_binomial_not_a_majority(self):   # E6 (W5: 205 of 400)
        n = 400
        yes, no = [True] * n, [False] * n
        v = _v(_subject("s", n, yes, no, no, no, pre_full=[i < 205 for i in range(n)]), n)["s"]
        self.assertEqual(v["pre_competent_lives"], 205)
        self.assertEqual(v["verdict"], "REFUSED_FIXED_PRIOR")

    def test_gr5_has_a_competence_bound(self):                      # B3: 180 of 400 lives at zero role 5
        n = 400
        yes, no = [True] * n, [False] * n
        v = _v(_subject("s", n, yes, no, no, no, r5=[i >= 180 for i in range(n)]), n)["s"]
        self.assertEqual(v["role5_retained_lives"], 220)
        self.assertFalse(v["G_R5"])
        self.assertEqual(v["verdict"], "REVISION_WITHOUT_RETAINED_COMPETENCE")


class Instrument(unittest.TestCase):
    def test_late_window_starts_three_blocks_after_the_switch(self):    # E3
        sw, log, _ = assay._one(subjects.reference(), DEV[0], True, False)
        row = assay.life(subjects.reference(), "full", DEV[0])
        n1 = [int((x["ep"]["role"] == 1).sum()) for x in log]
        self.assertEqual(row["n_early"], sum(n1[sw:sw + 3]))
        self.assertEqual(row["n_late"], sum(n1[sw + 3:]))

    def test_nan_plastic_value_is_flagged(self):                    # P1
        g = subjects.reference()
        h = copy.deepcopy(g)
        h["nodes"][4]["v"] = h["nodes"][4]["v"] * np.nan
        self.assertFalse(assay.memory_check(g, h, True)[0])

    def test_noise_arm_shares_the_full_arms_draws(self):
        g = C.jitter()                                              # eta = 1e-9 already: noise arm = full arm
        a, b = assay.life(g, "full", DEV[1]), assay.life(g, "noise", DEV[1])
        self.assertEqual({k: v for k, v in a.items() if k != "arm"}, {k: v for k, v in b.items() if k != "arm"})
        ref = subjects.reference()
        self.assertEqual(assay.noise_matched(ref)["eta"], assay.ETA_NOISE)
        self.assertEqual(ref["eta"], 1.0)

    def test_noswitch_arm_never_flips_the_law(self):
        g = subjects.memoryless(+1)
        a, b = assay.life(g, "full", DEV[2]), assay.life(g, "noswitch", DEV[2])
        self.assertEqual(a["sw"], b["sw"])
        self.assertEqual((a["c_late"], b["c_late"]), (0, b["n_late"]))


class Registered(unittest.TestCase):
    def test_family_s_is_declared_from_genome_structure(self):
        subs = subjects.load_searched("rso/ensorain/SUBJECTS.json")
        self.assertEqual(assay.family_s(subs), ["searched_16310006", "searched_16310007", "searched_16310008"])

    def test_untested_subjects_are_reported_not_tested(self):
        n = 40
        yes, no = [True] * n, [False] * n
        rows = _subject("reference", n, yes, no, no, no) + _subject("searched_a", n, yes, no, no, no) + \
            _subject("searched_b", n, yes, no, no, no)
        v = analysis.report(rows, n, searched=["searched_a", "searched_b"], tested=["searched_a"])
        self.assertEqual(v["searched_b"]["verdict"], "NOT_TESTED_PARAMETER_FREE")
        self.assertEqual(v["searched_a"]["family"], "S")

    def test_qd_jitter_and_qe_learns_pre_on_dev(self):              # the two new qualification controls
        c = assay.controls()
        rows = assay.run({"jitter": c["jitter"], "learns_pre": c["learns_pre"]}, analysis.ARMS, DEV)
        v = _v(rows, len(DEV))
        self.assertNotIn(v["jitter"]["verdict"], analysis.REVISIONS)
        self.assertIn(v["learns_pre"]["verdict"], analysis.REVISIONS)


if __name__ == "__main__":
    unittest.main()
