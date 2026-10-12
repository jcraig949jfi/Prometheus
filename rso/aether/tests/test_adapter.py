"""C-018-T030 tests (unittest; harry1 has no pytest). From the repo root:
    python -m unittest rso.aether.tests.test_adapter -v
RED FIRST: committed before rso/aether/{adapter,evaluate,confirm}.py existed (red/RED_OUTPUT.txt).
Synthetic records exercise every decision line of the evaluator; small fixture runs (Aether's own V1 law_step, 48^2,
<= 24 ticks) exercise the recorder end to end. No confirmatory seed is executed here."""
import copy
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
        self.assertTrue(any("B" in p for p in E.tree_check(dict(m, B=m["origin"] + 2), a)))
        self.assertTrue(any("N" in p for p in E.tree_check(dict(m, N=m["origin"] + 6), a)))

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
        d = {"n_units": 40, "confirmed_r2": 8, "content_excess_cond": 0.0, "content_excess_all": 0.0, "null_excess": 0.0}
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


if __name__ == "__main__":
    unittest.main()
