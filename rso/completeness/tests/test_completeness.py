"""C-018-T011 tests (unittest; harry1 has no pytest). Run from the repo root:
    python -m unittest rso.completeness.tests.test_completeness -v
RED FIRST: these were committed before rso/completeness/{manifest,verify,z80}.py existed (rso/completeness/README.md, s RED).
Part 1 is engine-agnostic (a synthetic three-shard experiment); part 2 is the known-answer fixture: the committed C-017 Z80
confirmatory shards (rso/z80/runs/CONFIRM.{0..5}-6.*), read only."""
import copy
import json
import os
import unittest

from rso.completeness import manifest as M, verify as V

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------- part 1: engine-agnostic
def native(rows):
    return M.digest(rows)


def synth_shard(i):
    rows = [{"arm": a, "seed": 1000 * i + 10 * j + k, "v": k} for j, a in enumerate("AB") for k in (1, 2)]
    return {"id": "S.%d-3" % i, "rows": rows, "meta": {"shard": [i, 3], "rows": len(rows), "rows_sha256": native(rows), "mode": "t"}}


def synth_manifest(early_stop=None, n=3):
    shards = [synth_shard(i) for i in range(3)]
    specs = [{"id": s["id"], "seeds": sorted({r["seed"] for r in s["rows"]}), "arm_counts": {"A": 2, "B": 2}, "rows": 4,
              "rows_sha256": M.digest(s["rows"]), "meta_sha256": M.digest(s["meta"])} for s in shards[:n]]
    m = M.build("synthetic", arms=["A", "B"], shards=specs, sources={"src.py": "ab" * 32}, row_key_fields=["arm"], early_stop=early_stop)
    return m, shards


class Core(unittest.TestCase):
    def setUp(self):
        self.m, self.shards = synth_manifest()
        self.src = {"src.py": "ab" * 32}

    def v(self, shards, m=None, **kw):
        return V.verify(m or self.m, shards, sources=kw.pop("sources", self.src), native_digest=native, **kw)

    def test_complete(self):
        r = self.v(self.shards)
        self.assertEqual((r.status, r.missing, r.findings), (V.COMPLETE, [], []))

    def test_order_is_irrelevant(self):
        self.assertEqual(self.v(list(reversed(self.shards))).status, V.COMPLETE)

    def test_missing_shard_is_incomplete_never_complete(self):
        r = self.v(self.shards[:2])
        self.assertEqual((r.status, r.missing), (V.INCOMPLETE, ["S.2-3"]))

    def test_no_shards_at_all_is_incomplete(self):
        self.assertEqual(self.v([]).status, V.INCOMPLETE)

    def test_duplicate_identical_is_refused(self):
        r = self.v(self.shards + [copy.deepcopy(self.shards[1])])
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.DUPLICATE, r.kinds())

    def test_duplicate_that_differs_is_conflicting(self):
        twin = copy.deepcopy(self.shards[1])
        twin["rows"][0]["v"] = 9
        r = self.v(self.shards + [twin])
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.CONFLICTING, r.kinds())

    def test_unexpected_shard_is_refused(self):
        extra = synth_shard(7)
        r = self.v(self.shards + [extra])
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.UNEXPECTED, r.kinds())

    def test_substituted_consistent_but_different_rows(self):
        s = copy.deepcopy(self.shards[0])
        s["rows"][0]["v"] = 7
        s["meta"]["rows_sha256"] = native(s["rows"])           # a re-run: internally consistent, not the frozen bytes
        r = self.v([s] + self.shards[1:])
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.SUBSTITUTED, r.kinds())

    def test_altered_row_without_meta_update(self):
        s = copy.deepcopy(self.shards[0])
        s["rows"][0]["v"] = 7
        r = self.v([s] + self.shards[1:])
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.ALTERED, r.kinds())

    def test_altered_meta_field(self):
        s = copy.deepcopy(self.shards[0])
        s["meta"]["mode"] = "dev"
        r = self.v([s] + self.shards[1:])
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.ALTERED, r.kinds())

    def test_other_seed_partition_is_named(self):
        s = copy.deepcopy(self.shards[0])
        for row in s["rows"]:
            row["seed"] += 5000
        s["meta"]["rows_sha256"] = native(s["rows"])
        r = self.v([s] + self.shards[1:])
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.SEED_PARTITION, r.kinds())

    def test_row_count_mismatch_is_named(self):
        s = copy.deepcopy(self.shards[0])
        s["rows"].append(dict(s["rows"][0]))
        s["meta"]["rows_sha256"] = native(s["rows"])
        r = self.v([s] + self.shards[1:])
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.COUNT_MISMATCH, r.kinds())

    def test_refusal_outranks_incomplete(self):
        s = copy.deepcopy(self.shards[0])
        s["rows"][0]["v"] = 7
        r = self.v([s])
        self.assertEqual(r.status, V.REFUSED)
        self.assertEqual(r.missing, ["S.1-3", "S.2-3"])        # what is missing is still listed

    def test_source_hash_mismatch_is_refused(self):
        r = self.v(self.shards, sources={"src.py": "cd" * 32})
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.SOURCE_MISMATCH, r.kinds())

    def test_sources_not_supplied_is_incomplete_not_complete(self):
        r = V.verify(self.m, self.shards, sources=None, native_digest=native)
        self.assertEqual(r.status, V.INCOMPLETE)
        self.assertIn("source:src.py", r.missing)

    def test_manifest_edited_after_sealing_is_refused(self):
        m = copy.deepcopy(self.m)
        m["shards"].pop()                                     # shrink the experiment on paper
        r = self.v(self.shards[:2], m=m)
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.MANIFEST_ALTERED, r.kinds())

    def test_pinned_manifest_hash_catches_a_resealed_manifest(self):
        small, _ = synth_manifest(n=2)                        # a smaller experiment, validly sealed
        r = self.v(self.shards[:2], m=small, pinned_manifest_sha256=self.m["manifest_sha256"])
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.MANIFEST_ALTERED, r.kinds())

    # ---- preregistered early stop vs unplanned absence.  Two shards present carry 2 rows each with arm A and v == 2.
    def stop(self, at_least):
        return {"rule_id": "ES-1", "preregistered_in": "synthetic prereg s9", "skippable": ["S.2-3"],
                "trigger": {"where": {"arm": "A", "v": 2}, "at_least": at_least}}

    def test_declared_early_stop_with_trigger_met(self):
        m, sh = synth_manifest(self.stop(2))
        r = V.verify(m, sh[:2], sources=self.src, native_digest=native)
        self.assertEqual(r.status, V.COMPLETE_EARLY_STOP)
        self.assertEqual((r.early_stop["rule_id"], r.early_stop["skipped"], r.early_stop["observed"]), ("ES-1", ["S.2-3"], 2))
        self.assertEqual(r.missing, [])

    def test_declared_early_stop_without_its_trigger_is_unplanned_absence(self):
        m, sh = synth_manifest(self.stop(3))
        r = V.verify(m, sh[:2], sources=self.src, native_digest=native)
        self.assertEqual((r.status, r.missing), (V.INCOMPLETE, ["S.2-3"]))
        self.assertEqual(r.early_stop["trigger_met"], False)

    def test_early_stop_does_not_excuse_a_non_skippable_shard(self):
        m, sh = synth_manifest(self.stop(2))
        r = V.verify(m, [sh[0], sh[2]], sources=self.src, native_digest=native)
        self.assertEqual((r.status, r.missing), (V.INCOMPLETE, ["S.1-3"]))

    def test_early_stop_cannot_excuse_a_corrupted_shard(self):
        m, sh = synth_manifest(self.stop(2))
        bad = copy.deepcopy(sh[0])
        bad["rows"][0]["v"] = 7
        r = V.verify(m, [bad, sh[1]], sources=self.src, native_digest=native)
        self.assertEqual(r.status, V.REFUSED)

    def test_trigger_is_not_credited_from_unverified_rows(self):
        m, sh = synth_manifest(self.stop(3))
        forged = copy.deepcopy(sh[1])
        forged["rows"] += [{"arm": "A", "seed": 1030, "v": 2}] * 5       # extra triggering rows in a shard that is not the frozen one
        forged["meta"]["rows_sha256"] = native(forged["rows"])
        r = V.verify(m, [sh[0], forged], sources=self.src, native_digest=native)
        self.assertEqual(r.status, V.REFUSED)

    def test_early_stop_added_after_the_fact_is_a_different_manifest(self):
        m, sh = synth_manifest()
        m2, _ = synth_manifest(self.stop(2))
        self.assertNotEqual(m["manifest_sha256"], m2["manifest_sha256"])
        r = V.verify(m2, sh[:2], sources=self.src, native_digest=native, pinned_manifest_sha256=m["manifest_sha256"])
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.MANIFEST_ALTERED, r.kinds())


# ---------------------------------------------------------------- part 2: Z80 six-shard known-answer fixture
class Z80Fixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from rso.completeness import z80 as Z
        cls.Z = Z
        cls.paths = Z.shard_paths()
        cls.shards = Z.load_shards(cls.paths)
        cls.manifest = Z.committed_manifest()
        cls.sources = Z.current_sources(cls.manifest)

    def v(self, shards, **kw):
        return self.Z.verify_set(kw.pop("manifest", self.manifest), shards, sources=kw.pop("sources", self.sources))

    def test_manifest_is_derived_from_the_preregistration_not_copied_from_the_data(self):
        self.assertEqual(self.Z.build_manifest(), self.manifest)

    def test_manifest_shape(self):
        m = self.manifest
        self.assertEqual(len(m["shards"]), 6)
        self.assertEqual([s["rows"] for s in m["shards"]], [58, 58, 61, 62, 61, 60])
        self.assertEqual(len(m["arms"]), 11)

    def test_complete_set_is_complete(self):
        r = self.v(self.shards)
        self.assertEqual((r.status, r.missing, r.findings), (V.COMPLETE, [], []))

    def test_complete_set_reproduces_the_frozen_analysis_exactly(self):
        out = self.Z.analyse(self.paths)
        want = json.load(open(os.path.join(ROOT, "rso", "z80", "runs", "CONFIRM.analysis.json"), encoding="utf-8"))
        self.assertEqual(out["completeness"]["status"], V.COMPLETE)
        self.assertEqual(json.loads(json.dumps(out["analysis"], default=str)), want)

    def test_each_single_shard_removed_is_incomplete(self):
        for i in range(6):
            r = self.v([s for j, s in enumerate(self.shards) if j != i])
            self.assertEqual((r.status, r.missing), (V.INCOMPLETE, ["CONFIRM.%d-6" % i]), i)

    def test_missing_shard_gives_no_verdict(self):
        out = self.Z.analyse(self.paths[:5])
        self.assertEqual(out["completeness"]["status"], V.INCOMPLETE)
        self.assertNotIn("analysis", out)                     # the frozen analyzer is never asked about a smaller experiment

    def test_each_single_shard_duplicated_is_refused(self):
        for i in range(6):
            r = self.v(self.shards + [copy.deepcopy(self.shards[i])])
            self.assertEqual(r.status, V.REFUSED, i)
            self.assertIn(V.DUPLICATE, r.kinds())

    def test_dev_rows_under_a_confirm_identity_are_refused(self):
        s = copy.deepcopy(self.shards[2])
        for row in s["rows"]:
            row["seed"] -= (17_080_000 - 17_060_000) if row["seed"] >= 17_080_000 else (17_050_000 - 17_030_000)
        s["meta"]["mode"] = "dev"
        s["meta"]["rows_sha256"] = self.Z.native_digest(s["rows"])
        r = self.v(self.shards[:2] + [s] + self.shards[3:])
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.SUBSTITUTED, r.kinds())
        self.assertIn(V.SEED_PARTITION, r.kinds())

    def test_rerun_with_a_different_rows_sha_is_substituted(self):
        s = copy.deepcopy(self.shards[4])
        s["rows"][0]["cls"] = "OTHER"
        s["meta"]["rows_sha256"] = self.Z.native_digest(s["rows"])
        r = self.v(self.shards[:4] + [s] + self.shards[5:])
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.SUBSTITUTED, r.kinds())

    def test_one_altered_row_is_refused(self):
        for i in range(6):
            s = copy.deepcopy(self.shards[i])
            s["rows"][0]["cls"] = "OTHER" if s["rows"][0]["cls"] != "OTHER" else "ENDO"
            r = self.v([x if j != i else s for j, x in enumerate(self.shards)])
            self.assertEqual(r.status, V.REFUSED, i)
            self.assertIn(V.ALTERED, r.kinds())

    def test_one_altered_meta_field_is_refused(self):
        for field, val in (("cleared_by", "someone else"), ("frozen_json_sha256", "0" * 64), ("mode", "dev"), ("wall_s", 1)):
            s = copy.deepcopy(self.shards[1])
            s["meta"][field] = val
            r = self.v([self.shards[0], s] + self.shards[2:])
            self.assertEqual(r.status, V.REFUSED, field)
            self.assertIn(V.ALTERED, r.kinds())

    def test_a_dropped_row_is_refused(self):
        s = copy.deepcopy(self.shards[3])
        s["rows"].pop()
        r = self.v(self.shards[:3] + [s] + self.shards[4:])
        self.assertEqual(r.status, V.REFUSED)

    def test_shard_from_another_partition_with_a_new_identity_is_unexpected(self):
        s = copy.deepcopy(self.shards[0])
        s["id"] = "CHALLENGE.0-6"
        r = self.v(self.shards[1:] + [s])
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.UNEXPECTED, r.kinds())

    def test_frozen_source_changed_is_refused(self):
        src = dict(self.sources)
        src[sorted(src)[0]] = "0" * 64
        r = self.v(self.shards, sources=src)
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.SOURCE_MISMATCH, r.kinds())

    def test_wrapper_pins_the_committed_manifest(self):
        m = copy.deepcopy(self.manifest)
        m["shards"] = m["shards"][:5]
        m = M.seal(m)                                           # a validly sealed, smaller experiment
        r = self.v(self.shards[:5], manifest=m)
        self.assertEqual(r.status, V.REFUSED)
        self.assertIn(V.MANIFEST_ALTERED, r.kinds())

    def test_early_stop_in_a_z80_manifest_needs_its_trigger(self):
        def with_stop(at_least):
            stop = {"rule_id": "ES-Z", "preregistered_in": "test only", "skippable": ["CONFIRM.5-6"],
                    "trigger": {"where": {"arm": "NH_ENDO_SHORT", "forgery": ""}, "at_least": at_least}}
            return M.seal(dict(copy.deepcopy(self.manifest), early_stop=stop))
        kw = dict(sources=self.sources, native_digest=self.Z.native_digest)
        self.assertEqual(V.verify(with_stop(10 ** 6), self.shards[:5], **kw).status, V.INCOMPLETE)
        self.assertEqual(V.verify(with_stop(1), self.shards[:5], **kw).status, V.COMPLETE_EARLY_STOP)

    def test_frozen_c017_files_are_untouched(self):
        from rso.z80 import freeze
        self.assertEqual(freeze.mismatches(), [])


if __name__ == "__main__":
    unittest.main()
