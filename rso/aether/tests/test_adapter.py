"""C-018-T030 tests (unittest; harry1 has no pytest). From the repo root:
    python -m unittest rso.aether.tests.test_adapter -v
RED FIRST: committed before rso/aether/{adapter,evaluate,confirm}.py existed (red/RED_OUTPUT.txt).
Synthetic records exercise every decision line of the evaluator; small fixture runs (Aether's own V1 law_step, 48^2,
<= 24 ticks) exercise the recorder end to end. No confirmatory seed is executed here.
v1.1.0 (C-018-T041): classes NonAncestorWindow, TreeStructure, Evaluable, Reporting, AnalyserGuards pin the repair round;
every one is RED on its mutant (red/run_red.py rows 21+, and Pallas's challenge/edits.json E1 E2 E3 E5 applied verbatim)."""
import copy
import json
import os
import shutil
import tempfile
import unittest

import numpy as np

from rso.aether import adapter as A, confirm as C, evaluate as E
from rso.completeness import manifest as M

N = 16


def blank_arrays(n=N, origin=(8, 3)):
    snap = np.zeros((5, n, n), np.uint8)
    imp = snap.copy()
    imp[3][origin] ^= 1
    ft = {w: np.full(n * n, -1, np.int16) for w in ("impulse", "cutB", "cutN")}
    return {"snap": snap, "imp": imp, "ftick_impulse": ft["impulse"], "ftick_cutB": ft["cutB"], "ftick_cutN": ft["cutN"]}


def chain(n=N, origin=(8, 3), length=7):
    """A synthetic east chain origin..origin+length-1, first-divergence tick = distance (a perfect relay).
    B = origin+2 removes everything downstream; N = origin+6 (terminal, a non-ancestor of origin+3..+5) removes only itself."""
    a = blank_arrays(n, origin)
    sites = [origin[0] * n + origin[1] + c for c in range(length)]
    for c, s in enumerate(sites):
        a["ftick_impulse"][s] = c
        a["ftick_cutB"][s] = c if c < 2 else -1
        a["ftick_cutN"][s] = c if c != 6 else -1
    meta = {"kind": "fixture", "n": n, "origin": sites[0], "B": sites[2], "N": sites[6], "targets": sites[3:6]}
    return meta, a


def tree_of(a, parent):
    """Attributed tree record in Aether's prop01 shape from the impulse first ticks and a parent map."""
    sites = sorted(int(s) for s in np.flatnonzero(a["ftick_impulse"] >= 0))
    gen = {}
    for s in sites:
        g, p = 0, parent.get(s, -1)
        while p >= 0:
            g, p = g + 1, parent.get(p, -1)
        gen[s] = g
    return {"site": sites, "gen": [gen[s] for s in sites], "parent": [parent.get(s, -1) for s in sites],
            "ftick": [int(a["ftick_impulse"][s]) for s in sites], "type": [2] * len(sites)}


class T0AndLightCone(unittest.TestCase):
    def test_single_site_impulse(self):
        meta, a = chain()
        self.assertEqual(E.t0_sites(a), [meta["origin"]])

    def test_multi_site_impulse_is_multi_source(self):
        meta, a = chain()
        a["imp"][3][(8, 9)] ^= 7
        self.assertEqual(len(E.t0_sites(a)), 2)
        self.assertEqual(E.ancestry(meta, a)["cls"], "MULTI_SOURCE")

    def test_light_cone_ok_and_violation(self):
        meta, a = chain()
        self.assertTrue(E.light_cone(meta, a)[0])
        a["ftick_impulse"][2 * N + 12] = 1                # Chebyshev radius 9 at tick 1
        ok, ratio = E.light_cone(meta, a)
        self.assertFalse(ok)
        self.assertGreater(ratio, 1)


class Ancestry(unittest.TestCase):
    def test_confirmed(self):
        meta, a = chain()
        r = E.ancestry(meta, a)
        self.assertEqual(r["cls"], "CONFIRMED")
        self.assertEqual((r["removed_B"], r["removed_N"]), (1.0, 0.0))
        self.assertEqual(r["r_int"], 5)               # origin+3..+5 interventional; +6 is removed by the N clamp too
        self.assertEqual(r["agreement"], 1.0)

    def test_nonspecific(self):
        meta, a = chain()
        a["ftick_cutN"][meta["targets"]] = -1
        self.assertEqual(E.ancestry(meta, a)["cls"], "NONSPECIFIC")

    def test_not_interventional(self):
        meta, a = chain()
        a["ftick_cutB"][:] = a["ftick_impulse"]
        a["ftick_cutB"][meta["B"]] = -1
        r = E.ancestry(meta, a)
        self.assertEqual(r["cls"], "NOT_INTERVENTIONAL")
        self.assertEqual(r["agreement"], 0.0)

    def test_insufficient(self):
        meta, a = chain()
        meta["targets"] = meta["targets"][:2]
        self.assertEqual(E.ancestry(meta, a)["cls"], "INSUFFICIENT")

    def test_non_divergent_targets_do_not_count(self):
        meta, a = chain()
        a["ftick_impulse"][meta["targets"][0]] = -1
        self.assertEqual(E.ancestry(meta, a)["cls"], "INSUFFICIENT")

    def test_vacuous_nonancestor_clamp(self):
        """C3 cannot fail when its site never diverges: clamping it to CONTROL is the identity (the T020 fixture's (-2,0) site)."""
        meta, a = chain()
        meta["N"] = 2 * N + 3
        self.assertEqual(E.ancestry(meta, a)["cls"], "CONTROL_VACUOUS")

    def test_no_nonancestor(self):
        meta, a = chain()
        meta["N"] = None
        self.assertEqual(E.ancestry(meta, a)["cls"], "CONTROL_VACUOUS")

    def test_threshold_edges(self):
        meta, a = chain()
        o = meta["origin"]
        s = o - N                                       # a divergent sibling as N; targets origin+3..+6 (4 sites)
        a["ftick_impulse"][s], a["ftick_cutB"][s], a["ftick_cutN"][s] = 1, 1, -1
        a["ftick_cutN"][o + 6] = 6
        meta.update(N=s, targets=[o + 3, o + 4, o + 5, o + 6])
        a["ftick_cutB"][o + 6] = 6                        # 3 of 4 removed = 0.75 < 0.8
        self.assertEqual(E.ancestry(meta, a)["cls"], "NOT_INTERVENTIONAL")
        a["ftick_cutB"][o + 6] = -1                       # 4 of 4
        self.assertEqual(E.ancestry(meta, a)["cls"], "CONFIRMED")
        a["ftick_cutN"][o + 6] = -1                       # N removes 1 of 4 = 0.25 > 0.2
        self.assertEqual(E.ancestry(meta, a)["cls"], "NONSPECIFIC")


class NativeTree(unittest.TestCase):
    def native(self):
        meta, a = chain()
        o = meta["origin"]
        # O -> o+1 (generation 1 with a CARRY child: B by Aether's rule) -> o+2 ...; sibling S = o-N, generation 1, no child
        s = o - N
        a["ftick_impulse"][s], a["ftick_cutB"][s], a["ftick_cutN"][s] = 1, 1, -1
        a["ftick_cutB"][o + 1] = -1
        a["ftick_cutN"][o + 6] = 6
        parent = {o + c: o + c - 1 for c in range(1, 7)}
        parent[s] = o
        tree = tree_of(a, parent)
        tree["ftick"][tree["site"].index(s)] = 1
        tree["type"][tree["site"].index(s)] = 3
        m = {"kind": "native", "n": N, "origin": o, "tree": tree, "B": o + 1, "N": s}
        return m, a

    def test_choose_nonancestor_rule(self):
        m, a = self.native()
        self.assertEqual(A.choose_nonancestor(m["tree"], m["B"], m["origin"], N), m["N"])

    def test_nonancestor_prefers_matched_then_earliest(self):
        m, a = self.native()
        t = copy.deepcopy(m["tree"])
        o = m["origin"]
        for s, g, p, ft in ((o + N, 1, o, 2), (o - 3 * N, 3, m["N"], 3)):   # a later sibling; a farther non-ancestor
            t["site"].append(s), t["gen"].append(g), t["parent"].append(p), t["ftick"].append(ft), t["type"].append(1)
        self.assertEqual(A.choose_nonancestor(t, m["B"], o, N), m["N"])

    def test_nonancestor_excludes_unattributed(self):
        m, a = self.native()
        t = copy.deepcopy(m["tree"])
        i = t["site"].index(m["N"])
        t["gen"][i], t["parent"][i] = -1, -2          # unattributed: not an ATTRIBUTED non-ancestor
        self.assertIsNone(A.choose_nonancestor(t, m["B"], m["origin"], N))

    def test_native_targets_are_aether_descendants(self):
        m, a = self.native()
        r = E.ancestry(m, a)
        self.assertEqual(sorted(r["targets"]), [m["origin"] + c for c in range(2, 7)])
        self.assertEqual(r["cls"], "CONFIRMED")

    def test_recorded_B_or_N_not_trusted(self):
        m, a = self.native()
        self.assertEqual(E.tree_check(m, a), [])
        self.assertTrue(any("recorded B" in p for p in E.tree_check(dict(m, B=m["origin"] + 2), a)))
        self.assertTrue(any("recorded N" in p for p in E.tree_check(dict(m, N=m["origin"] + 6), a)))

    def test_tree_must_match_observed_divergence(self):
        m, a = self.native()
        t = copy.deepcopy(m["tree"])
        for k in ("site", "gen", "parent", "ftick", "type"):
            del t[k][-1]
        self.assertTrue(E.tree_check(dict(m, tree=t), a))
        t = copy.deepcopy(m["tree"])
        t["ftick"][0] += 1
        self.assertTrue(E.tree_check(dict(m, tree=t), a))

    def test_producer_fields_ignored(self):
        """The evaluator recomputes from the arrays; a producer-written verdict is ignored (trusts_derived must be False)."""
        m, a = self.native()
        m["producer_cls"] = "CONFIRMED"
        before = E.ancestry(m, a)["cls"]
        a2 = dict(a, ftick_cutB=a["ftick_impulse"].copy())
        self.assertNotEqual(E.ancestry(m, a2)["cls"], before)


class Binding(unittest.TestCase):
    def test_arrays_sha_binds_record(self):
        meta, a = chain()
        meta["arrays_sha256"] = A.arrays_sha256(a)
        self.assertEqual(E.binding_problems(meta, a), [])
        a["ftick_cutB"][meta["targets"][0]] = 3
        self.assertTrue(E.binding_problems(meta, a))


class Content(unittest.TestCase):
    def test_conditioned_excess(self):
        acc = {0: np.full((4, 6), 0.125), 1: np.full((4, 6), 0.625)}
        acc[0][:, 3:] = 0.625                                              # seed 0 recovers content only at r >= 4
        self.assertAlmostEqual(E.conditioned_excess(acc, 3), 0.25)         # radii 2..3: seed 0 at chance, seed 1 at +0.5
        self.assertAlmostEqual(E.conditioned_excess(acc, 6), (0.5 * 3 / 5 + 0.5) / 2)
        self.assertIsNone(E.conditioned_excess(acc, 1))

    def test_reach_band(self):
        rows = [{"cls": "CONFIRMED", "r_int": r} for r in (1, 2, 3, 3, 4)] + [{"cls": "NOT_INTERVENTIONAL", "r_int": 6}] * 5
        self.assertEqual(E.reach_band(rows), 3)                            # need max(3, ceil(1.0)) = 3 units with r_int >= r
        self.assertEqual(E.reach_band(rows[:2] + rows[5:]), 0)

    def test_graded_labels(self):
        L0 = A.graded_labels(0, 12, 0.0)
        L1 = A.graded_labels(0, 12, 1.0)
        self.assertEqual(L0.shape, (8, 12))
        self.assertTrue((L1 == np.arange(8)[:, None]).all())
        La, Lb = A.graded_labels(0, 12, 0.1), A.graded_labels(0, 12, 0.3)

        def hit(L):
            return L == np.arange(8)[:, None]
        self.assertTrue((hit(Lb) | ~hit(La)).all())                        # common random numbers: monotone in p


class Disposition(unittest.TestCase):
    def law(self, **kw):
        d = {"n_units": 40, "evaluable": 40, "need": 4, "confirmed_r2": 8, "content_excess_cond": 0.0,
             "content_excess_all": 0.0, "null_excess": 0.0}
        d.update(kw)
        return d

    def base(self, **kw):
        s = {"completeness": "COMPLETE", "qualified": True, "records_ok": True, "law": self.law()}
        s.update(kw)
        return s

    def test_outcomes(self):
        self.assertEqual(E.disposition(self.base()), "CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT")
        self.assertEqual(E.disposition(self.base(law=self.law(content_excess_cond=0.06))), "ANCESTRY_WITH_CONTENT")
        self.assertEqual(E.disposition(self.base(law=self.law(confirmed_r2=3))), "NEITHER")
        self.assertEqual(E.disposition(self.base(law=self.law(confirmed_r2=4, content_excess_all=0.07))),
                         "CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT")
        self.assertEqual(E.disposition(self.base(law=self.law(confirmed_r2=0, content_excess_all=0.07))),
                         "CONTENT_WITHOUT_INTERVENTIONAL_ANCESTRY")

    def test_refusals_outrank(self):
        self.assertEqual(E.disposition(self.base(completeness="INCOMPLETE")), "INCOMPLETE")
        self.assertEqual(E.disposition(self.base(completeness="REFUSED")), "REFUSED")
        self.assertEqual(E.disposition(self.base(qualified=False)), "DETECTION_UNQUALIFIED")
        self.assertEqual(E.disposition(self.base(records_ok=False)), "REFUSED_RECORD_INCONSISTENT")
        self.assertEqual(E.disposition(self.base(law=self.law(null_excess=0.04))), "DETECTION_UNQUALIFIED")

    def test_agreement_category(self):
        self.assertEqual(E.agreement_category(0.85), "AGREE")
        self.assertEqual(E.agreement_category(0.5), "DISAGREE")
        self.assertEqual(E.agreement_category(0.6), "MIXED")
        self.assertIsNone(E.agreement_category(None))


class Seeds(unittest.TestCase):
    def test_disjoint(self):
        conf = {k for law in C.ARMS for k in C.seeds(law)}
        self.assertFalse(conf & set(A.DEV_K))
        self.assertFalse(conf & set(C.BURNED))
        bases = list(A.SEEDS.values())
        for b in bases:                                 # Cadmus 0xC18A..0xC18E and Aether 0xE2010000 / 0xE2011000 / 0x1A9F
            self.assertNotIn(b >> 16, (0xC18A, 0xC18B, 0xC18C, 0xC18D, 0xC18E, 0xE201))
            self.assertNotEqual(b, 0x1A9F)
        self.assertEqual(len(set(bases)), len(bases))


class Completeness(unittest.TestCase):
    SRC = {"x.py": "a" * 64}

    def shards(self):
        out = []
        for sid, (law, ks) in C.shard_plan().items():
            rows = [{"law": law, "seed": k, "arrays_sha256": "%064x" % k} for k in ks]
            out.append(C.make_shard(sid, rows))
        return out

    def test_design_pending_then_complete(self):
        d = C.design_manifest(sources=self.SRC)
        self.assertTrue(M.is_sealed(d))
        r = C.verify_presented(d, self.shards(), sources=self.SRC, pinned_design_sha256=d["manifest_sha256"])
        self.assertEqual(r.status, "COMPLETE")

    def test_missing_duplicate_altered_seed_source(self):
        d = C.design_manifest(sources=self.SRC)
        sh = self.shards()
        self.assertEqual(C.verify_presented(d, sh[1:], sources=self.SRC).status, "INCOMPLETE")
        self.assertEqual(C.verify_presented(d, sh + [sh[0]], sources=self.SRC).status, "REFUSED")
        bad = copy.deepcopy(sh)
        bad[0]["rows"][0]["arrays_sha256"] = "f" * 64
        self.assertIn("ALTERED", C.verify_presented(d, bad, sources=self.SRC).kinds())
        bad = copy.deepcopy(sh)
        bad[0]["rows"][0]["seed"] = 7
        bad[0] = C.make_shard(bad[0]["id"], bad[0]["rows"])
        self.assertIn("SEED_PARTITION", C.verify_presented(d, bad, sources=self.SRC).kinds())
        self.assertIn("SOURCE_MISMATCH", C.verify_presented(d, sh, sources={"x.py": "b" * 64}).kinds())

    def test_smaller_design_refused_by_pin(self):
        d = C.design_manifest(sources={})
        small = M.seal(dict(d, shards=d["shards"][:-1]))
        r = C.verify_presented(small, self.shards()[:-1], sources={}, pinned_design_sha256=d["manifest_sha256"])
        self.assertEqual(r.status, "REFUSED")

    def test_run_guard(self):
        self.assertEqual(C.main(["run", "RX.0"]), 2)                     # no --cleared-by: refused before any execution
        self.assertEqual(C.main(["run", "RX.0", "--cleared-by", "not-a-release"]), 2)   # a flag alone is not a release


class FixtureEndToEnd(unittest.TestCase):
    def test_relay_small(self):
        meta, a = A.fixture_unit("A", 0, n=48, horizon=24)
        meta["arrays_sha256"] = A.arrays_sha256(a)
        self.assertEqual(E.binding_problems(meta, a), [])
        self.assertEqual(E.ancestry(meta, a)["cls"], "CONFIRMED")
        self.assertTrue(E.light_cone(meta, a)[0])

    def test_wrong_B_and_misattributed_N(self):
        o = A.FIX_ORIGIN
        meta, a = A.fixture_unit("A", 0, n=48, horizon=24, B=(o[0] - 2, o[1]))
        self.assertEqual(E.ancestry(meta, a)["cls"], "NOT_INTERVENTIONAL")
        meta, a = A.fixture_unit("A", 0, n=48, horizon=24, N=(o[0], o[1] + 1))
        self.assertEqual(E.ancestry(meta, a)["cls"], "NONSPECIFIC")

    def test_teleport_flagged(self):
        meta, a = A.fixture_unit("A", 0, n=48, horizon=12, law="TELEPORT")
        self.assertFalse(E.light_cone(meta, a)[0])


def native_shape(n=N, origin=(8, 3), ticks_up=1, ticks_m=5, extra=()):
    """Pallas's 0x3004 / 0x3005 shape (REPORT s4.2): B = O+(0,1) first diverges at tick 4 with a CARRY chain of targets at
    ticks 6..8; U = O-(1,0), a generation-1 sibling that diverged at tick `ticks_up` (BEFORE B: a possible unattributed
    upstream contributor); M = O+(1,0), a generation-1 sibling at tick `ticks_m`. Both are at B's distance from O."""
    o = origin[0] * n + origin[1]
    rows = [(o, 0, -1, 0, 0), (o + 1, 1, o, 4, 1), (o + 2, 2, o + 1, 6, 2), (o + 3, 3, o + 2, 7, 2), (o + 4, 4, o + 3, 8, 2),
            (o - n, 1, o, ticks_up, 1), (o + n, 1, o, ticks_m, 1)] + list(extra)
    return {k: [r[i] for r in rows] for i, k in enumerate(("site", "gen", "parent", "ftick", "type"))}, o


class NonAncestorWindow(unittest.TestCase):
    """B8 / B4: N must satisfy ftick(B) <= ftick(N) < min ftick(targets)."""
    def test_upstream_sibling_is_not_the_control(self):
        tree, o = native_shape()
        self.assertEqual(A.nonancestor_candidates(tree, o + 1, o, N)[0][2], o - N)     # v1.0.0's N: the upstream sibling
        self.assertEqual(A.nonancestor_window(tree, o + 1), (4, 6))
        self.assertEqual(A.choose_nonancestor(tree, o + 1, o, N), o + N)               # v1.1.0: the matched sibling

    def test_window_edges(self):
        tree, o = native_shape(ticks_m=4)                                               # ftick(N) == ftick(B): allowed
        self.assertEqual(A.choose_nonancestor(tree, o + 1, o, N), o + N)
        tree, o = native_shape(ticks_m=6)                                               # == first target tick: excluded
        self.assertIsNone(A.choose_nonancestor(tree, o + 1, o, N))
        tree, o = native_shape(ticks_up=7, ticks_m=9)                                   # both after the targets began
        self.assertIsNone(A.choose_nonancestor(tree, o + 1, o, N))

    def test_ranking_inside_window(self):
        far = (8 * N + 3 + 2 * N, 2, 8 * N + 3 + N, 5, 1)                                # distance 2 from O, tick 5
        tree, o = native_shape(ticks_m=5, extra=[far])
        self.assertEqual(A.choose_nonancestor(tree, o + 1, o, N), o + N)               # matched distance first

    def test_no_window_control_means_vacuous_not_interventional_stands(self):
        meta, a = chain()
        meta["N"] = None
        self.assertEqual(E.ancestry(meta, a)["cls"], "CONTROL_VACUOUS")                 # B clamp removes: N needed
        a["ftick_cutB"][:] = a["ftick_impulse"]
        a["ftick_cutB"][meta["B"]] = -1
        self.assertEqual(E.ancestry(meta, a)["cls"], "NOT_INTERVENTIONAL")              # B clamp fails: no N needed


class TreeStructure(unittest.TestCase):
    """B1: native tree invariants and clamp-world fidelity in tree_check; the roots line (Pallas E2)."""
    def setUp(self):
        self.m, self.a = NativeTree().native()

    def test_native_shape_is_clean(self):
        self.assertEqual(E.tree_check(self.m, self.a), [])
        tree, _ = native_shape()
        self.assertEqual(E.tree_invariants(tree, N), [])

    def test_invariants(self):
        tree, o = native_shape()
        t = copy.deepcopy(tree)
        t["parent"][4] = o + 2                                    # o+4 re-parented two sites away, gen kept
        p = E.tree_invariants(t, N)
        self.assertTrue(any("4-adjacent" in x for x in p) and any("gen != parent" in x for x in p))
        t = copy.deepcopy(tree)
        t["ftick"][2] = 9                                         # o+2 after its child o+3
        self.assertTrue(any("not earlier" in x for x in E.tree_invariants(t, N)))
        t = copy.deepcopy(tree)
        t["gen"][3] = 5
        self.assertEqual(E.tree_invariants(t, N), ["tree invariant: gen != parent gen + 1 at 2 sites"])
        t = copy.deepcopy(tree)
        t["parent"][3] = 0
        self.assertTrue(any("not in tree" in x for x in E.tree_invariants(t, N)))

    def test_tree_check_runs_invariants(self):
        t = copy.deepcopy(self.m["tree"])
        o = self.m["origin"]
        i = t["site"].index(o + 4)
        t["parent"][i] = o + 2
        self.assertTrue(any("4-adjacent" in x for x in E.tree_check(dict(self.m, tree=t), self.a)))

    def test_clamp_world_must_be_a_clamp(self):
        a = dict(self.a, ftick_cutB=np.full(N * N, -1, np.int16))     # no CUT_B world was run (Pallas's type-flip form)
        self.assertTrue(any("cutB array is not a clamp" in x for x in E.tree_check(self.m, a)))
        a = dict(self.a, ftick_cutN=self.a["ftick_impulse"].copy())   # N diverges in its own clamp world
        self.assertTrue(any("cutN array is not a clamp" in x for x in E.tree_check(self.m, a)))

    def test_origin_line(self):
        m = dict(self.m, origin=self.m["origin"] + 1)                 # recorded origin is not the root / t0 site
        self.assertTrue(any(x.startswith("origin:") for x in E.tree_check(m, self.a)))


def summary_rows():
    r = {"cls": "NO_CUT", "r_int": 0, "agreement": None, "n_targets": 0, "light_cone_ok": True, "ftick_B": None,
         "ftick_N": None, "targets_ftick": None}
    conf = [dict(r, cls="CONFIRMED", r_int=3, agreement=1.0, n_targets=4, ftick_B=1, ftick_N=2,
                 targets_ftick=E.tick_profile([5, 6, 250, 320]), seed=s) for s in range(3)]
    ni = [dict(r, cls="NOT_INTERVENTIONAL", agreement=0.0, n_targets=4, ftick_B=1, ftick_N=2, seed=3 + s) for s in range(5)]
    return conf + ni + [dict(r, seed=8 + s) for s in range(40)]


class Evaluable(unittest.TestCase):
    """B2: `need` over EVALUABLE units; fewer than EVALUABLE_MIN -> ANCESTRY_UNEVALUABLE; label carries the count."""
    def law(self, **kw):
        return Disposition().law(**kw)

    def base(self, L):
        return {"completeness": "COMPLETE", "qualified": True, "records_ok": True, "law": L}

    def test_unevaluable_population(self):
        self.assertEqual(E.EVALUABLE_MIN, 8)
        for ev in (0, 7):
            L = self.law(n_units=48, evaluable=ev, confirmed_r2=min(ev, 3), content_excess_all=0.07)
            self.assertEqual(E.disposition(self.base(L)), "ANCESTRY_UNEVALUABLE")
        L = self.law(n_units=48, evaluable=8, confirmed_r2=3)
        self.assertEqual(E.disposition(self.base(L)), "CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT")

    def test_need_counts_evaluable_units_only(self):
        self.assertEqual([E.need(x) for x in (0, 8, 30, 31, 48)], [3, 3, 3, 4, 5])
        L = self.law(n_units=48, evaluable=10, confirmed_r2=3)          # v1.0.0: need 5 over 48 units -> NEITHER
        self.assertEqual(E.disposition(self.base(L)), "CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT")
        rows = summary_rows()                                            # 3 CONFIRMED r 3 of 8 evaluable; 40 NO_CUT
        self.assertEqual(E.reach_band(rows), 3)
        self.assertEqual(E.evaluable(rows), 8)

    def test_label(self):
        L = self.law(n_units=48, evaluable=10, need=3)
        self.assertEqual(E.label("NEITHER", L), "NEITHER [evaluable 10 of 48 units; minimum 8; need 3 CONFIRMED at r >= 2]")


class Reporting(unittest.TestCase):
    """B3 / B7: content over the CONFIRMED units' own seeds and the targets' first-tick profile, beside the registered."""
    def test_confirmed_seed_content_and_tick_profile(self):
        rows = summary_rows()
        acc = {r["seed"]: np.full((4, 6), 0.125 if r["cls"] == "CONFIRMED" else 1.0) for r in rows}
        L = E.law_summary(rows, acc, {s: np.full((4, 6), 0.125) for s in acc})
        self.assertGreater(L["content_excess_cond"], 0.7)                 # registered: radius band over every seed
        self.assertEqual(L["content_excess_cond_confirmed_seeds"], 0.0)  # the CONFIRMED units' own features: chance
        self.assertEqual((L["evaluable"], L["need"], L["reach_band"]), (8, 3, 3))
        self.assertEqual(L["confirmed_targets_ftick"]["0"], {"n": 4, "min_q1_med_q3_max": [5.0, 5.8, 128.0, 267.5, 320.0],
                                                             "after_200": 2, "after_300": 1})
        self.assertEqual(L["nonspecific_N_before_B"], 0)
        rows[3] = dict(rows[3], cls="NONSPECIFIC", ftick_B=4, ftick_N=1)
        rows[4] = dict(rows[4], cls="NONSPECIFIC", ftick_B=4, ftick_N=4)        # same tick: inside the window, not upstream
        self.assertEqual(E.law_summary(rows, acc, acc)["nonspecific_N_before_B"], 1)
        self.assertIsNone(E.tick_profile([]))

    def test_unit_row_carries_ticks(self):
        m, a = NativeTree().native()
        r = E.evaluate_unit(dict(m, seed=0), a)
        self.assertEqual((r["ftick_B"], r["ftick_N"], r["targets_ftick"]["n"]), (1, 1, 5))


class AnalyserGuards(unittest.TestCase):
    """confirm.analyse on a two-shard fixture with stubbed replay / snapshot / freeze check (the shape of Pallas's
    forge.e3 / e5). Each guard has a test that is RED on its mutant: E5 completeness stop, E3 unit-file binding, E1 replay
    sample (challenge/edits.json verbatim), B6 freeze check, B5 duplicate refusal and per-unit snapshot binding, B1 replayed
    tree, P1 nothing verdict-bearing on refusal."""
    SEEDS = {"RX.0": [1, 2], "RX.1": [3, 4]}

    def unit(self, k):
        m, a = NativeTree().native()
        a = {x: v.copy() for x, v in a.items()}
        a["snap"][0][0, k] = k                                    # a seed-specific t0 state (single-site impulse kept)
        a["imp"][0][0, k] = k
        a["H"] = np.zeros((8, 1, 1, 6, 4, 256), np.uint8)
        a["D"] = np.zeros((8, 1, 1, 6), np.float32)
        m = dict(m, schema="prometheus.rso.aether.unit.v1", law="RX", seed=k, warm=1, H=1, B_tick=1,
                 aether={"warm_digest": A.P.digest(list(a["snap"]))})
        return m, a

    def setUp(self):
        self.d = tempfile.mkdtemp()
        specs = []
        for sid, ks in self.SEEDS.items():
            os.makedirs(os.path.join(self.d, sid))
            rows = []
            for k in ks:
                meta = A.save_unit(os.path.join(self.d, sid, "native_RX_%d" % k), *self.unit(k))
                rows.append({"law": "RX", "seed": k, "arrays_sha256": meta["arrays_sha256"], "meta_sha256": M.digest(meta)})
            self.write_shard(sid, rows)
            specs.append({"id": sid, "seeds": ks, "arm_counts": {"RX": 2}, "rows": 2, "rows_sha256": "PENDING",
                          "meta_sha256": "PENDING"})
        self.design = M.build("T041 guard fixture", arms=["RX"], shards=specs, sources={}, row_key_fields=["law"],
                              seed_field="seed", early_stop=None)
        self.dp = os.path.join(self.d, "design.json")
        with open(self.dp, "w", encoding="utf-8") as f:
            json.dump(self.design, f)

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def write_shard(self, sid, rows):
        with open(os.path.join(self.d, sid + ".shard.json"), "w", encoding="utf-8") as f:
            json.dump(C.make_shard(sid, rows), f)

    def stored(self, law, k, *_a, **_k):
        return A.load_unit(os.path.join(self.d, "RX.%d" % ((k - 1) // 2), "native_%s_%d" % (law, k)))

    def genuine_snapshot(self, law, k, n, warm):
        _, a = self.unit(k)
        return list(a["snap"]), 0, NativeTree().native()[0]["origin"]

    def genuine_tree(self, law, k, n, warm, H):
        m, _ = self.stored(law, k)
        return {"tree": m["tree"], "origin": m["origin"], "warm_digest": m["aether"]["warm_digest"]}

    def run_analyse(self, **kw):
        got = []
        kw.setdefault("replay", self.stored)
        kw.setdefault("tree_replay", self.genuine_tree)
        kw.setdefault("snapshot", self.genuine_snapshot)
        kw.setdefault("freeze_check", lambda: [])
        rc = C.analyse(runs=self.d, design_path=self.dp, pin=self.design["manifest_sha256"], emit=got.append, **kw)
        return rc, got[0]

    def assert_refused(self, rc, out, needle):
        self.assertEqual(rc, 4)
        self.assertTrue(any(needle in p for p in out["problems"]), out.get("problems"))
        self.assertNotIn("laws", out)                                 # P1: nothing verdict-bearing
        self.assertNotIn("classes", json.dumps(out))

    def test_clean_fixture_reports_evidence(self):
        rc, out = self.run_analyse()
        self.assertEqual(rc, 0, out.get("problems"))
        self.assertEqual(out["evidence"], {"freeze_check": "OK", "rows": 4, "distinct_arrays_sha256": 4, "snapshot_bound": 4,
                                           "tree_replayed": 4, "full_replay_verified": 2, "replay_sample": C.REPLAY})
        self.assertEqual(out["laws"]["RX"]["disposition"], "ANCESTRY_UNEVALUABLE")
        self.assertIn("evaluable 4 of 4 units", out["laws"]["RX"]["label"])

    def test_E5_incomplete_stops_before_units(self):
        os.remove(os.path.join(self.d, "RX.1.shard.json"))
        rc, out = self.run_analyse()
        self.assertEqual(rc, 3)
        self.assertNotIn("laws", out)
        self.assertNotIn("problems", out)

    def test_E3_unit_files_bound_to_row(self):
        p = os.path.join(self.d, "RX.1.shard.json")
        with open(p, encoding="utf-8") as f:
            sh = json.load(f)
        sh["rows"][1]["arrays_sha256"] = "f" * 64
        self.write_shard("RX.1", sh["rows"])
        self.assert_refused(*self.run_analyse(), "unit files differ from the shard row")

    def test_E1_replay_sample(self):
        def replay(law, k):
            m, a = self.stored(law, k)
            return m, dict(a, ftick_cutN=a["ftick_cutN"][::-1].copy())
        self.assert_refused(*self.run_analyse(replay=replay), "native replay differs")

    def test_B1_replayed_tree(self):
        def replay(law, k):
            m, a = self.stored(law, k)
            t = copy.deepcopy(m["tree"])
            t["type"][-1] = 3
            return dict(m, tree=t), a
        self.assert_refused(*self.run_analyse(replay=replay), "replayed ['tree'] differs")

    def test_B1_every_unit_tree_replayed(self):
        def tree_replay(law, k, n, warm, H):                      # seed 4 is not in the full-replay sample
            u = self.genuine_tree(law, k, n, warm, H)
            if k == 4:
                u["tree"] = dict(u["tree"], type=u["tree"]["type"][:-1] + [3 - u["tree"]["type"][-1]])
            return u
        rc, out = self.run_analyse(tree_replay=tree_replay)
        self.assert_refused(rc, out, "RX.1 seed 4: replayed Aether tree / origin is not the unit's")
        self.assertEqual(out["evidence"]["tree_replayed"], 3)

    def test_B1_tree_replay_checks_origin_and_warm_digest(self):
        for field, value in (("origin", -7), ("warm_digest", "0" * 32)):
            with self.subTest(field=field):
                def tree_replay(law, k, n, warm, H):
                    u = self.genuine_tree(law, k, n, warm, H)
                    return dict(u, **{field: value}) if k == 4 else u
                self.assert_refused(*self.run_analyse(tree_replay=tree_replay), "replayed Aether tree / origin is not")

    def test_B6_freeze_check_first(self):
        rc, out = self.run_analyse(freeze_check=lambda: ["design manifest differs from the frozen one"])
        self.assertEqual((rc, out["disposition"]), (4, "REFUSED_FREEZE_MISMATCH"))
        self.assertNotIn("completeness", out)

    def copy_as(self, k_src, k_dst, relabel=True):
        m, a = A.load_unit(os.path.join(self.d, "RX.1", "native_RX_%d" % k_src))
        m = A.save_unit(os.path.join(self.d, "RX.1", "native_RX_%d" % k_dst), dict(m, seed=k_dst if relabel else k_src), a)
        rows = [json.load(open(os.path.join(self.d, "RX.1.shard.json"), encoding="utf-8"))["rows"][0],
                {"law": "RX", "seed": k_dst, "arrays_sha256": m["arrays_sha256"], "meta_sha256": M.digest(m)}]
        self.write_shard("RX.1", rows)

    def test_B5_duplicate_arrays_refused(self):
        self.copy_as(3, 4)
        self.assert_refused(*self.run_analyse(snapshot=lambda law, k, n, w: self.genuine_snapshot(law, 3, n, w)),
                            "rows share an arrays_sha256")

    def test_B5_every_unit_snapshot_bound(self):
        self.copy_as(3, 4)
        self.assert_refused(*self.run_analyse(), "warm snapshot / origin is not seed 4's")

    def test_meta_names_its_row(self):
        self.copy_as(3, 4, relabel=False)
        self.assert_refused(*self.run_analyse(snapshot=lambda law, k, n, w: self.genuine_snapshot(law, 3, n, w)),
                            "unit meta names RX seed 3")

    def test_B5_warm_digest_is_the_seeds(self):
        p = os.path.join(self.d, "RX.1", "native_RX_4")
        m, a = A.load_unit(p)
        m = A.save_unit(p, dict(m, aether={"warm_digest": "0" * 32}), a)     # stored snap genuine, Aether digest not
        rows = json.load(open(os.path.join(self.d, "RX.1.shard.json"), encoding="utf-8"))["rows"]
        rows[1]["meta_sha256"] = M.digest(m)
        self.write_shard("RX.1", rows)
        self.assert_refused(*self.run_analyse(), "warm snapshot / origin is not seed 4's")


if __name__ == "__main__":
    unittest.main()
