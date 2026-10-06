"""D3 fault-injection matrix (moonshot/epoch/CONTRACT.md s10), written RED before the implementation.

Every case runs four ways: PER_CHAIN and SINGLE_REF, each with leases on and with leases DISABLED
(case 10 = the two lease-free variants of cases 1-9). Real git; real bare remotes in a temp directory;
faults are injected at the contract's named points (s11). Workers that must race past a lease are built
with respect_leases=False: a worker that ignores leases must still be harmless (leases grant nothing)."""
import os
import subprocess
import sys
import time
import unittest

from moonshot.epoch import model, runtime
from moonshot.epoch import store as S
from moonshot.epoch import validate as V
from moonshot.epoch import worker as W
from moonshot.epoch.tests.harness import APPROVED_SHA, REPO_ROOT, CountingRunner, Harness, planted_runner

O = W.Outcome


class D3Matrix:
    LAYOUT = None
    LEASES = True

    def setUp(self):
        self.h = Harness(self.LAYOUT, leases=self.LEASES)
        self.addCleanup(self.h.cleanup)

    # ------------------------------------------------------------------------------------------------ helpers

    def head_index(self, chain_id="C1"):
        return self.h.coordinator.chain_view(chain_id).head_index

    def assert_matches_reference(self, genesis, upto):
        """The published chain equals an uninterrupted, transport-free replay: digests AND bytes."""
        cid = genesis.chain_id
        lin = self.h.coordinator.lineage(cid)
        self.assertEqual([e.epoch_index for e in lin], list(range(1, upto + 1)))
        ref = model.replay_chain(genesis, upto)
        self.assertEqual([e.epoch_digest for e in lin], [r.epoch_digest for r in ref])
        for e, r in zip(lin, ref):
            files = self.h.coordinator.epoch_bytes(e.commit)
            self.assertEqual((files["trace"], files["checkpoint"]), (r.trace, r.checkpoint))
            self.assertEqual(model.verify_epoch(files), [])

    def receipts_for(self, *workers):
        for w in workers:
            w.flush_receipts()
        return self.h.coordinator.read_receipts()

    def refs_matching(self, fragment):
        return [r for r in self.h.remote_refs() if fragment in r]

    # ------------------------------------------------------------------------------------------------ case 1

    def test_case01_duplicate_execution_one_published(self):
        g = self.h.chain(epochs=1)
        b = self.h.worker("bravo", respect_leases=False)
        box = {}

        def b_runs_first(worker, ctx):
            box["b"] = b.run_attempt("C1")

        a = self.h.worker("alpha", faults=W.FaultPlan({"after_execute": b_runs_first}))
        ra = a.run_attempt("C1")
        rb = box["b"]
        self.assertEqual((rb.outcome, ra.outcome), (O.PUBLISHED, O.DUPLICATE))
        self.assertEqual((ra.work_id, ra.epoch_digest), (rb.work_id, rb.epoch_digest))
        self.assertEqual(len(self.h.coordinator.lineage("C1")), 1)
        self.assertIsNone(self.h.coordinator.contest("C1"))
        self.assertEqual(self.refs_matching("/quarantine/"), [])
        got = {r["attempt_id"]: r["outcome"] for r in self.receipts_for(a, b)}
        self.assertEqual(got, {ra.attempt_id: "DUPLICATE", rb.attempt_id: "PUBLISHED"})
        self.assert_matches_reference(g, 1)

    # ------------------------------------------------------------------------------------------------ case 2

    def test_case02_worker_death_before_staging_reexecutes(self):
        for point in ("after_lease", "mid_execute", "after_execute"):
            with self.subTest(point=point):
                cid = "D" + str(len(point)) + point[6:9]
                g = self.h.chain(cid, epochs=1)
                a = self.h.worker("dead-" + point, faults=W.FaultPlan({point: W.CRASH}))
                with self.assertRaises(W.InjectedCrash):
                    a.run_attempt(cid)
                self.assertEqual(self.head_index(cid), 0)
                self.h.clock.advance(61)
                rb = self.h.worker("next-" + point).run_attempt(cid)
                self.assertEqual(rb.outcome, O.PUBLISHED)
                rec = self.h.restart(a).recover()
                self.assertEqual([r.outcome for r in rec], [O.ABANDONED_RECOVERED])
                self.assertIn("crashed", rec[0].flags)
                self.assertEqual(len(self.h.coordinator.lineage(cid)), 1)
                self.assert_matches_reference(g, 1)

    def test_case02_crash_after_stage_then_restart_publishes(self):
        g = self.h.chain(epochs=1)
        a = self.h.worker("alpha", faults=W.FaultPlan({"after_stage": W.CRASH}))
        with self.assertRaises(W.InjectedCrash):
            a.run_attempt("C1")
        self.assertEqual(self.head_index(), 0)                     # staged is not published
        rec = self.h.restart(a).recover()
        self.assertEqual([r.outcome for r in rec], [O.PUBLISHED])
        self.assertIn("recovered", rec[0].flags)
        self.assert_matches_reference(g, 1)

    def test_case02_crash_after_stage_then_other_publishes(self):
        g = self.h.chain(epochs=1)
        a = self.h.worker("alpha", faults=W.FaultPlan({"after_stage": W.CRASH}))
        with self.assertRaises(W.InjectedCrash):
            a.run_attempt("C1")
        self.h.clock.advance(61)
        self.assertEqual(self.h.worker("bravo").run_attempt("C1").outcome, O.PUBLISHED)
        rec = self.h.restart(a).recover()
        self.assertEqual([r.outcome for r in rec], [O.DUPLICATE])
        self.assertEqual(len(self.h.coordinator.lineage("C1")), 1)
        self.assert_matches_reference(g, 1)

    def test_case02_crash_after_cas_counts_once(self):
        g = self.h.chain(epochs=1)
        a = self.h.worker("alpha", faults=W.FaultPlan({"after_cas": W.CRASH}))
        with self.assertRaises(W.InjectedCrash):
            a.run_attempt("C1")
        self.assertEqual(self.head_index(), 1)
        a2 = self.h.restart(a)
        rec = a2.recover()
        self.assertEqual([r.outcome for r in rec], [O.PUBLISHED])
        mine = [r for r in self.receipts_for(a2) if r["attempt_id"] == rec[0].attempt_id]
        self.assertEqual([r["outcome"] for r in mine], ["PUBLISHED"])
        self.assert_matches_reference(g, 1)

    def test_case02_real_process_kill_mid_epoch(self):
        if self.LAYOUT != S.PER_CHAIN:
            self.skipTest("process death is layout-independent; run once per lease mode")
        g = self.h.chain(epochs=1, iterations=2_000_000)
        spool = os.path.join(self.h.dir, "spool-killed")
        cmd = [sys.executable, "-m", "moonshot.epoch", "work", "--remote", self.h.remote, "--namespace", self.h.ns,
               "--layout", self.LAYOUT, "--local-dir", os.path.join(self.h.dir, "local-killed"),
               "--spool-dir", spool, "--worker-id", "killed", "--code-sha", APPROVED_SHA,
               "--approve", APPROVED_SHA, "--chain", "C1", "--max-attempts", "1"]
        if not self.LEASES:
            cmd.append("--no-leases")
        p = subprocess.Popen(cmd, cwd=REPO_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        self.addCleanup(lambda: p.poll() is None and p.kill())
        deadline = time.time() + 60
        while time.time() < deadline and not _spool_state(spool, "EXECUTING"):
            if p.poll() is not None:
                self.fail("worker exited before executing: " + p.stderr.read().decode(errors="replace")[-800:])
            time.sleep(0.01)
        self.assertTrue(_spool_state(spool, "EXECUTING"), "worker never reached EXECUTING")
        p.kill()
        p.wait(timeout=30)
        self.assertEqual(self.head_index(), 0)
        rb = self.h.worker("bravo", clock=lambda: time.time() + 3600).run_attempt("C1")
        self.assertEqual(rb.outcome, O.PUBLISHED)
        killed = W.Worker(self.h.store("killed"), "killed", code_sha=APPROVED_SHA, approved={APPROVED_SHA},
                          spool_dir=spool, leases=self.LEASES)
        rec = killed.recover()
        self.assertEqual([r.outcome for r in rec], [O.ABANDONED_RECOVERED])
        self.assert_matches_reference(g, 1)

    # ------------------------------------------------------------------------------------------------ case 3

    def test_case03_lease_expiry_reclaim_and_late_duplicate(self):
        for pause in ("after_execute", "after_stage"):
            with self.subTest(pause=pause):
                cid = "L" + pause[6:9]
                g = self.h.chain(cid, epochs=3)
                box = {}

                def others_advance(worker, ctx, cid=cid, box=box, pause=pause):
                    self.h.clock.advance(61)                       # the holder's lease has expired
                    box["b"] = self.h.worker("bravo-" + pause).run_attempt(cid)
                    box["c"] = self.h.worker("charlie-" + pause).run_attempt(cid)   # a descendant exists too

                a = self.h.worker("alpha-" + pause, faults=W.FaultPlan({pause: others_advance}))
                ra = a.run_attempt(cid)
                self.assertEqual((box["b"].outcome, box["c"].outcome), (O.PUBLISHED, O.PUBLISHED))
                self.assertEqual(ra.outcome, O.DUPLICATE)
                self.assertIn("late", ra.flags)
                self.assertEqual(self.head_index(cid), 2)
                self.h.worker("delta-" + pause).run_chain(cid)
                self.assert_matches_reference(g, 3)

    # ------------------------------------------------------------------------------------------------ case 4

    def test_case04_cas_collision_one_published_one_duplicate(self):
        g = self.h.chain(epochs=1)
        a = self.h.worker("alpha", respect_leases=False)
        box = {}

        def a_publishes_first(worker, ctx):
            box["a"] = a.run_attempt("C1")

        b = self.h.worker("bravo", respect_leases=False, faults=W.FaultPlan({"after_stage": a_publishes_first}))
        rb = b.run_attempt("C1")
        self.assertEqual((box["a"].outcome, rb.outcome), (O.PUBLISHED, O.DUPLICATE))
        self.assertEqual(len(self.h.coordinator.lineage("C1")), 1)
        self.assert_matches_reference(g, 1)

    def test_case04_different_chains_contend_only_on_single_ref(self):
        self.h.chain("X", epochs=1)
        self.h.chain("Y", epochs=1)
        b = self.h.worker("bravo")
        box = {}

        def b_publishes_y(worker, ctx):
            box["b"] = b.run_attempt("Y")

        a = self.h.worker("alpha", faults=W.FaultPlan({"after_stage": b_publishes_y}))
        ra = a.run_attempt("X")
        self.assertEqual((ra.outcome, box["b"].outcome), (O.PUBLISHED, O.PUBLISHED))
        if self.LAYOUT == S.SINGLE_REF:
            self.assertGreaterEqual(ra.receipt["contention_retries"], 1)
        else:
            self.assertEqual(ra.receipt["contention_retries"], 0)

    # ------------------------------------------------------------------------------------------------ case 5

    def test_case05_remote_outage_bounded_spool_no_publication(self):
        g = self.h.chain(epochs=2)
        runner = CountingRunner()

        def outage(worker, ctx):
            self.h.take_remote_offline()

        a = self.h.worker("alpha", runner=runner, faults=W.FaultPlan({"after_execute": outage}))
        r1 = a.run_attempt("C1")
        self.assertEqual(r1.outcome, O.REMOTE_UNAVAILABLE)
        self.assertEqual(runner.calls, 1)
        a.faults = W.FaultPlan()
        r2 = a.run_attempt("C1")                                   # still offline: no second epoch executes
        self.assertEqual(r2.outcome, O.REMOTE_UNAVAILABLE)
        self.assertEqual(runner.calls, 1)
        self.h.bring_remote_online()
        self.assertEqual(self.head_index(), 0)                     # nothing was published while offline
        rec = a.recover()
        self.assertEqual([r.outcome for r in rec], [O.PUBLISHED])
        self.assertIn("outage", rec[0].flags)
        self.assertEqual(rec[0].attempt_id, r1.attempt_id)         # the same attempt, charged once
        self.h.assert_remote_consistent(self)
        a.run_chain("C1")
        self.assert_matches_reference(g, 2)

    def test_case05_outage_while_another_publishes_resolves_duplicate(self):
        g = self.h.chain(epochs=1)

        def go_offline(worker, ctx):
            worker.store.remote_url = self.h.dead_url

        a = self.h.worker("alpha", respect_leases=False, faults=W.FaultPlan({"after_execute": go_offline}))
        self.assertEqual(a.run_attempt("C1").outcome, O.REMOTE_UNAVAILABLE)
        self.assertEqual(self.h.worker("bravo", respect_leases=False).run_attempt("C1").outcome, O.PUBLISHED)
        a.store.remote_url = self.h.remote
        self.assertEqual([r.outcome for r in a.recover()], [O.DUPLICATE])
        self.assert_matches_reference(g, 1)

    # ------------------------------------------------------------------------------------------------ case 6

    def test_case06_messy_schedule_equals_uninterrupted_replay(self):
        g = self.h.chain(epochs=3)
        a = self.h.worker("alpha", faults=W.FaultPlan({"after_stage": W.CRASH}))
        with self.assertRaises(W.InjectedCrash):
            a.run_attempt("C1")
        self.h.clock.advance(61)
        b = self.h.worker("bravo")
        self.assertEqual(b.run_attempt("C1").outcome, O.PUBLISHED)          # epoch 1, re-executed
        box = {}

        def dup(worker, ctx):
            box["c"] = self.h.worker("charlie", respect_leases=False).run_attempt("C1")

        b.faults = W.FaultPlan({"after_execute": dup})
        self.assertEqual(b.run_attempt("C1").outcome, O.DUPLICATE)          # epoch 2, executed twice
        self.assertEqual(box["c"].outcome, O.PUBLISHED)
        b.faults = W.FaultPlan()
        self.h.restart(a).recover()
        self.h.worker("delta").run_chain("C1")
        self.assert_matches_reference(g, 3)

    def test_case06_retried_trace_is_byte_identical(self):
        self.h.chain(epochs=1)
        a = self.h.worker("alpha", faults=W.FaultPlan({"after_stage": W.CRASH}))
        with self.assertRaises(W.InjectedCrash):
            a.run_attempt("C1")
        staged = self.refs_matching("/staging/")
        self.assertEqual(len(staged), 1)
        first = {n: self.h.read_remote_blob(staged[0], n) for n in ("MANIFEST.json", "SPEC.json", "TRACE",
                                                                     "CHECKPOINT")}
        self.h.clock.advance(61)
        self.h.worker("bravo").run_attempt("C1")
        files = self.h.coordinator.epoch_bytes(self.h.coordinator.lineage("C1")[0].commit)
        self.assertEqual((files["manifest"], files["spec"], files["trace"], files["checkpoint"]),
                         (first["MANIFEST.json"], first["SPEC.json"], first["TRACE"], first["CHECKPOINT"]))

    # ------------------------------------------------------------------------------------------------ case 7

    def test_case07_host_metadata_never_reaches_canonical_bytes(self):
        self.h.chain(epochs=1)
        b = self.h.worker("worker-bravo", host_label="SPECTREX5-windows", respect_leases=False)
        box = {}

        def b_first(worker, ctx):
            box["b"] = b.run_attempt("C1")

        a = self.h.worker("worker-alpha", host_label="ubu001-linux", respect_leases=False,
                          faults=W.FaultPlan({"after_execute": b_first}))
        ra = a.run_attempt("C1")
        self.assertEqual(ra.epoch_digest, box["b"].epoch_digest)
        files = self.h.coordinator.epoch_bytes(self.h.coordinator.lineage("C1")[0].commit)
        for blob in files.values():
            for marker in (b"SPECTREX5", b"ubu001", b"worker-alpha", b"worker-bravo", ra.attempt_id.encode(),
                           box["b"].attempt_id.encode()):
                self.assertNotIn(marker, blob)
        self.assertEqual((ra.receipt["host"], box["b"].receipt["host"]), ("ubu001-linux", "SPECTREX5-windows"))

    # ------------------------------------------------------------------------------------------------ case 8

    def test_case08_ambiguous_push_applied_resolves_published_once(self):
        g = self.h.chain(epochs=1)
        a = self.h.worker("alpha", faults=W.FaultPlan({"cas_ambiguous": W.APPLY_THEN_LOSE_ACK}))
        r = a.run_attempt("C1")
        self.assertEqual(r.outcome, O.PUBLISHED)
        self.assertIn("ambiguous", r.flags)
        mine = [x for x in self.receipts_for(a) if x["attempt_id"] == r.attempt_id]
        self.assertEqual([x["outcome"] for x in mine], ["PUBLISHED"])
        self.assert_matches_reference(g, 1)

    def test_case08_ambiguous_push_not_applied_retries_cas(self):
        g = self.h.chain(epochs=1)
        a = self.h.worker("alpha", faults=W.FaultPlan({"cas_ambiguous": W.LOSE_BEFORE_APPLY}))
        r = a.run_attempt("C1")
        self.assertEqual(r.outcome, O.PUBLISHED)
        self.assertIn("ambiguous", r.flags)
        self.assertGreaterEqual(r.receipt["push_attempts_cas"], 2)
        self.assert_matches_reference(g, 1)

    def test_case08_ambiguous_then_unreachable_stays_pending(self):
        g = self.h.chain(epochs=1)

        def apply_then_vanish(worker, ctx):
            ctx["push"]()
            self.h.take_remote_offline()
            raise W.AmbiguousPush("acknowledgement lost and remote gone")

        a = self.h.worker("alpha", faults=W.FaultPlan({"cas_ambiguous": apply_then_vanish}))
        r = a.run_attempt("C1")
        self.assertEqual(r.outcome, O.AMBIGUOUS)                   # never counted as published while unresolved
        self.h.bring_remote_online()
        rec = a.recover()
        self.assertEqual([x.outcome for x in rec], [O.PUBLISHED])
        self.assertEqual(rec[0].attempt_id, r.attempt_id)
        mine = [x for x in self.receipts_for(a) if x["attempt_id"] == r.attempt_id]
        self.assertEqual([x["outcome"] for x in mine], ["PUBLISHED"])
        self.assert_matches_reference(g, 1)

    def test_case08_ambiguous_applied_then_descendant_is_still_published(self):
        g = self.h.chain(epochs=2)

        def apply_then_extend(worker, ctx):
            ctx["push"]()
            self.h.worker("bravo", respect_leases=False).run_attempt("C1")      # builds epoch 2 on top
            raise W.AmbiguousPush("acknowledgement lost")

        a = self.h.worker("alpha", faults=W.FaultPlan({"cas_ambiguous": apply_then_extend}))
        r = a.run_attempt("C1")
        self.assertEqual(r.outcome, O.PUBLISHED)
        self.assertEqual(self.head_index(), 2)
        self.assert_matches_reference(g, 2)

    # ------------------------------------------------------------------------------------------------ case 9

    def test_case09_disagreement_at_head_quarantines_halts_and_replay_overturns(self):
        g = self.h.chain(epochs=2)
        bad = self.h.worker("bad", runner=planted_runner(), respect_leases=False)
        box = {}

        def bad_publishes_first(worker, ctx):
            box["bad"] = bad.run_attempt("C1")

        good = self.h.worker("good", faults=W.FaultPlan({"after_stage": bad_publishes_first}))
        rg = good.run_attempt("C1")
        self.assertEqual(box["bad"].outcome, O.PUBLISHED)          # a push grants no authority ...
        self.assertEqual(rg.outcome, O.DISAGREEMENT)               # ... and the first writer does not win silently
        self.assertEqual(rg.work_id, box["bad"].work_id)
        self.assertNotEqual(rg.epoch_digest, box["bad"].epoch_digest)
        self.assertEqual(len(self.refs_matching("/quarantine/C1/1/")), 1)
        c = self.h.coordinator.contest("C1")
        self.assertEqual((c["state"], c["epoch_index"]), ("CONTESTED", 1))
        self.assertEqual(V.chain_status(self.h.coordinator, "C1"), "CONTESTED")
        runner = CountingRunner()
        self.assertEqual(self.h.worker("late", runner=runner).run_attempt("C1").outcome, O.HALTED)
        self.assertEqual(runner.calls, 0)
        self.assertEqual(V.resolve(self.h.resolver(), "C1", runners=[runtime.run_synthetic_v1]),
                         V.Resolution.OVERTURNED)
        self.assertEqual(self.head_index(), 0)                     # rewound past the rejected epoch
        self.assertTrue(self.refs_matching("/rejected/C1/1"))
        self.h.worker("good2").run_chain("C1")
        self.assert_matches_reference(g, 2)

    def test_case09_faulty_challenger_is_upheld(self):
        g = self.h.chain(epochs=2)
        good = self.h.worker("good")
        box = {}

        def good_publishes_first(worker, ctx):
            box["good"] = good.run_attempt("C1")

        bad = self.h.worker("bad", runner=planted_runner(), respect_leases=False,
                            faults=W.FaultPlan({"after_stage": good_publishes_first}))
        self.assertEqual(bad.run_attempt("C1").outcome, O.DISAGREEMENT)
        self.assertEqual(box["good"].outcome, O.PUBLISHED)
        self.assertEqual(V.chain_status(self.h.coordinator, "C1"), "CONTESTED")
        self.assertEqual(V.resolve(self.h.resolver(), "C1", runners=[runtime.run_synthetic_v1]),
                         V.Resolution.UPHELD)
        self.assertEqual((self.head_index(), V.chain_status(self.h.coordinator, "C1")), (1, "OPEN"))
        self.assertEqual(len(self.refs_matching("/quarantine/C1/1/")), 1)   # the evidence stays
        self.h.worker("good2").run_chain("C1")
        self.assert_matches_reference(g, 2)

    def test_case09_audit_finds_bad_epoch_with_descendants_taints_then_overturns(self):
        g = self.h.chain(epochs=3)
        self.assertEqual(self.h.worker("good1").run_attempt("C1").outcome, O.PUBLISHED)
        self.assertEqual(self.h.worker("bad", runner=planted_runner()).run_attempt("C1").outcome, O.PUBLISHED)
        self.assertEqual(self.h.worker("good3").run_attempt("C1").outcome, O.PUBLISHED)   # built on bad bytes
        a = V.audit(self.h.validator(), "C1", 2, runner=runtime.run_synthetic_v1, auditor_id="auditor")
        self.assertEqual(a["result"], "MISMATCH")
        c = self.h.coordinator.contest("C1")
        self.assertEqual((c["state"], c["taint_root"]), ("TAINTED", 2))
        self.assertEqual(V.chain_status(self.h.coordinator, "C1"), "TAINTED")
        self.assertEqual(self.h.worker("any", runner=CountingRunner()).run_attempt("C1").outcome, O.HALTED)
        self.assertEqual(V.resolve(self.h.resolver(), "C1", runners=[runtime.run_synthetic_v1]),
                         V.Resolution.OVERTURNED)
        self.assertEqual(self.head_index(), 1)
        self.h.worker("good4").run_chain("C1")
        self.assert_matches_reference(g, 3)

    def test_case09_faulty_audit_with_descendants_is_upheld(self):
        g = self.h.chain(epochs=3)
        self.h.worker("good").run_chain("C1")
        a = V.audit(self.h.validator(), "C1", 2, runner=planted_runner(), auditor_id="faulty-auditor")
        self.assertEqual(a["result"], "MISMATCH")
        self.assertEqual(V.chain_status(self.h.coordinator, "C1"), "TAINTED")
        self.assertEqual(V.resolve(self.h.resolver(), "C1", runners=[runtime.run_synthetic_v1]),
                         V.Resolution.UPHELD)
        self.assertEqual(V.chain_status(self.h.coordinator, "C1"), "COMPLETE")
        self.assert_matches_reference(g, 3)

    def test_case09_late_worker_disagreement_taints_descendants(self):
        g = self.h.chain(epochs=3)

        def honest_advance(worker, ctx):
            self.h.clock.advance(61)
            self.h.worker("h1").run_attempt("C1")
            self.h.worker("h2").run_attempt("C1")

        a = self.h.worker("bad", runner=planted_runner(), faults=W.FaultPlan({"after_stage": honest_advance}))
        ra = a.run_attempt("C1")
        self.assertEqual(ra.outcome, O.DISAGREEMENT)
        self.assertIn("late", ra.flags)
        c = self.h.coordinator.contest("C1")
        self.assertEqual((c["state"], c["taint_root"]), ("TAINTED", 1))
        self.assertEqual(V.resolve(self.h.resolver(), "C1", runners=[runtime.run_synthetic_v1]),
                         V.Resolution.UPHELD)
        self.h.worker("h3").run_chain("C1")
        self.assert_matches_reference(g, 3)

    def test_case09_unresolvable_stays_halted(self):
        self.h.chain(epochs=2)
        self.h.worker("good").run_attempt("C1")
        V.audit(self.h.validator(), "C1", 1, runner=planted_runner(0), auditor_id="faulty-auditor")
        self.assertEqual(V.resolve(self.h.resolver(), "C1", runners=[planted_runner(1)]), V.Resolution.UNRESOLVED)
        self.assertEqual(V.chain_status(self.h.coordinator, "C1"), "UNRESOLVED")
        self.assertEqual(self.h.worker("any").run_attempt("C1").outcome, O.HALTED)

    def test_case09_corrupt_published_bytes_halt_the_chain(self):
        self.h.chain(epochs=2)
        self.h.worker("good").run_attempt("C1")
        self.h.tamper_head("C1")
        runner = CountingRunner()
        self.assertEqual(self.h.worker("next", runner=runner).run_attempt("C1").outcome, O.HALTED)
        self.assertEqual(runner.calls, 0)
        self.assertIn(V.chain_status(self.h.coordinator, "C1"), ("CONTESTED", "TAINTED"))

    # ------------------------------------------------------------------------------------------------ case 11

    def test_case11_unapproved_code_refused_everywhere(self):
        self.h.chain("Usha", epochs=1, approved="bad" + "0" * 37)
        self.h.chain("Urt", epochs=1, runtime_={"name": "moonshot.synthetic", "version": 99})
        self.h.chain("OK", epochs=1)
        for cid, kw in (("Usha", {}), ("Urt", {}), ("OK", {"code_sha": "d" * 40})):
            with self.subTest(chain=cid):
                runner = CountingRunner()
                w = self.h.worker("w-" + cid, runner=runner, **kw)
                r = w.run_attempt(cid)
                self.assertEqual(r.outcome, O.REFUSED_UNAPPROVED)
                self.assertEqual(runner.calls, 0)
                self.assertEqual(self.head_index(cid), 0)
                self.assertEqual([x["outcome"] for x in self.receipts_for(w) if x["attempt_id"] == r.attempt_id],
                                 ["REFUSED_UNAPPROVED"])

    # ------------------------------------------------------------------------------------------------ case 12

    def test_case12_clock_ahead_steals_early_but_one_publication(self):
        g = self.h.chain(epochs=1)
        box = {}

        def ahead_runs(worker, ctx):
            box["ahead"] = self.h.worker("ahead", clock_offset=3600).run_attempt("C1")

        a = self.h.worker("alpha", faults=W.FaultPlan({"after_execute": ahead_runs}))
        ra = a.run_attempt("C1")
        self.assertEqual((box["ahead"].outcome, ra.outcome), (O.PUBLISHED, O.DUPLICATE))
        self.assertEqual(len(self.h.coordinator.lineage("C1")), 1)
        self.assert_matches_reference(g, 1)

    def test_case12_clock_behind_only_waits(self):
        if not self.LEASES:
            self.skipTest("leases disabled: no clock is consulted")
        g = self.h.chain(epochs=1)
        box = {}

        def others(worker, ctx):
            self.h.clock.advance(120)                              # the holder's lease is expired for true time
            box["behind"] = self.h.worker("behind", clock_offset=-3600).run_attempt("C1")
            box["true"] = self.h.worker("true").run_attempt("C1")

        a = self.h.worker("alpha", faults=W.FaultPlan({"after_execute": others}))
        ra = a.run_attempt("C1")
        self.assertEqual((box["behind"].outcome, box["true"].outcome, ra.outcome),
                         (O.BUSY, O.PUBLISHED, O.DUPLICATE))
        self.assert_matches_reference(g, 1)

    # ------------------------------------------------------------------------------------------------ structure

    def test_publication_is_not_validation(self):
        g = self.h.chain(epochs=2)
        self.h.worker("alpha").run_chain("C1")
        self.assertIsNone(self.h.coordinator.validation("C1"))     # PUBLISHED is not VALIDATED
        rep = V.validate_chain(self.h.validator(), "C1", replay_indices=(2,))
        self.assertEqual([e["state"] for e in rep["epochs"]], ["VALIDATED", "VALIDATED"])
        self.assertEqual([e["checks"] for e in rep["epochs"]], [["BYTES"], ["BYTES", "REPLAY"]])
        self.assertEqual(self.h.coordinator.validation("C1")["head_epoch_index"], 2)
        self.assert_matches_reference(g, 2)

    def test_roles_workers_cannot_create_validate_or_resolve(self):
        self.h.chain(epochs=1)
        w = self.h.store("plain-worker")
        with self.assertRaises(PermissionError):
            w.create_chain(model.make_genesis("Z", epochs=1, params={"work_iterations": 1, "trace_every": 1,
                                                                     "checkpoint_bytes": 1},
                                              approved_code_sha=APPROVED_SHA, initial_checkpoint=b"z"))
        with self.assertRaises(PermissionError):
            V.validate_chain(w, "C1")
        with self.assertRaises(PermissionError):
            V.resolve(w, "C1", runners=[runtime.run_synthetic_v1])

    def test_only_moonshot_refs_on_the_remote(self):
        self.h.chain(epochs=2)
        a = self.h.worker("alpha")
        a.run_chain("C1")
        a.flush_receipts()
        V.validate_chain(self.h.validator(), "C1")
        refs = self.h.remote_refs()
        self.assertTrue(refs)
        self.h.assert_remote_consistent(self)

    def test_every_attempt_has_exactly_one_receipt(self):
        self.h.chain(epochs=3)
        ws = [self.h.worker(n, respect_leases=False) for n in ("r1", "r2", "r3")]
        reports = []
        for _ in range(3):
            for w in ws:
                reports.append(w.run_attempt("C1"))
        attempts = [r for r in reports if r.outcome not in (O.BUSY, O.COMPLETE)]
        got = [r["attempt_id"] for r in self.receipts_for(*ws)]
        self.assertEqual(sorted(got), sorted(r.attempt_id for r in attempts))
        self.assertEqual(sum(r.outcome == O.PUBLISHED for r in attempts), 3)


def _spool_state(spool_dir, state):
    d = os.path.join(spool_dir, "attempts")
    if not os.path.isdir(d):
        return False
    for name in os.listdir(d):
        try:
            with open(os.path.join(d, name), "rb") as f:
                if ('"state":"{}"'.format(state)).encode() in f.read():
                    return True
        except OSError:
            pass
    return False


class TestD3PerChain(D3Matrix, unittest.TestCase):
    LAYOUT, LEASES = S.PER_CHAIN, True


class TestD3SingleRef(D3Matrix, unittest.TestCase):
    LAYOUT, LEASES = S.SINGLE_REF, True


class TestD3PerChainNoLeases(D3Matrix, unittest.TestCase):          # case 10
    LAYOUT, LEASES = S.PER_CHAIN, False


class TestD3SingleRefNoLeases(D3Matrix, unittest.TestCase):         # case 10
    LAYOUT, LEASES = S.SINGLE_REF, False


if __name__ == "__main__":
    unittest.main()
