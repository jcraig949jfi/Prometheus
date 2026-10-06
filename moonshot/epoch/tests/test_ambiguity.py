"""Lost acknowledgements on EVERY write path, not only the chain CAS (added 2026-10-06 after the D5 field run:
a Windows git:// push applied its ref and never returned). Written RED: D3 case 8 injected ambiguity only at
the chain CAS, so slot writes, staging, receipts and node announcements could still kill a worker.

Each write that meets a lost acknowledgement must resolve by re-reading, exactly like the chain CAS: applied
-> done once; not applied -> sent again; someone else's value -> an ordinary CAS rejection."""
import os
import unittest

from moonshot.epoch import model
from moonshot.epoch import store as S
from moonshot.epoch import worker as W
from moonshot.epoch.gitio import AmbiguousPush
from moonshot.epoch.tests.harness import APPROVED_SHA, Harness, OffsetClock

O = W.Outcome


class OneShot:
    """A push hook that loses the acknowledgement of the next push touching `fragment`, once."""

    def __init__(self, fragment, applied):
        self.fragment, self.applied, self.armed, self.fired = fragment, applied, False, 0

    def __call__(self, push, url, updates):
        if self.armed and any(self.fragment in dst for _, dst, _ in updates):
            self.armed = False
            self.fired += 1
            if self.applied:
                push(url, updates)
            raise AmbiguousPush("injected: acknowledgement lost ({})".format("applied" if self.applied else "not applied"))
        return push(url, updates)


class AmbiguityEverywhere:
    LAYOUT = None

    def setUp(self):
        self.h = Harness(self.LAYOUT)
        self.addCleanup(self.h.cleanup)

    def frag(self, slot_fragment):
        return slot_fragment if self.LAYOUT == S.PER_CHAIN else "/index"

    def worker_with(self, hook, wid="alpha"):
        st = self.h.store(wid, push_hook=hook)
        return W.Worker(st, wid, code_sha=APPROVED_SHA, approved={APPROVED_SHA},
                        spool_dir=os.path.join(self.h.dir, "spool-" + wid), clock=OffsetClock(self.h.clock, 0))

    def test_create_chain_resolves_a_lost_ack(self):
        for applied in (True, False):
            with self.subTest(applied=applied):
                hook = OneShot(self.frag("/chains/"), applied)
                coord = self.h.store("coord-%s" % applied, role=S.COORDINATOR, push_hook=hook)
                g = model.make_genesis("G%d" % applied, epochs=1, params={"work_iterations": 10, "trace_every": 5,
                                                                         "checkpoint_bytes": 8},
                                       approved_code_sha=APPROVED_SHA, initial_checkpoint=b"g")
                hook.armed = True
                coord.create_chain(g)
                self.assertEqual(hook.fired, 1)
                self.assertEqual(self.h.coordinator.chain_view(g.chain_id).head_index, 0)

    def test_lease_stage_and_receipt_writes_resolve_lost_acks(self):
        g = self.h.chain(epochs=4)                       # one epoch per sub-case below
        for fragment, applied in (("/leases/", True), ("/staging/", True), ("/leases/", False), ("/staging/", False)):
            with self.subTest(fragment=fragment, applied=applied):
                hook = OneShot(fragment if fragment == "/staging/" else self.frag(fragment), applied)
                w = self.worker_with(hook, "w%d%s" % (applied, fragment.strip("/")[:3]))
                hook.armed = True
                r = w.run_attempt("C1")
                self.assertEqual(r.outcome, O.PUBLISHED)
                self.assertEqual(hook.fired, 1)
                self.h.clock.advance(1)
        self.assertEqual([e.epoch_digest for e in self.h.coordinator.lineage("C1")],
                         [x.epoch_digest for x in model.replay_chain(g, 4)])

    def test_receipt_flush_resolves_a_lost_ack_without_duplicates(self):
        self.h.chain(epochs=2)
        for applied in (True, False):
            with self.subTest(applied=applied):
                hook = OneShot(self.frag("/receipts/"), applied)
                w = self.worker_with(hook, "rcpt%d" % applied)
                r = w.run_attempt("C1")
                hook.armed = True
                self.assertEqual(w.flush_receipts(), 1)
                self.assertEqual(hook.fired, 1)
                mine = [x for x in self.h.coordinator.read_receipts() if x["attempt_id"] == r.attempt_id]
                self.assertEqual(len(mine), 1)

    def test_node_announcement_resolves_a_lost_ack(self):
        for applied in (True, False):
            with self.subTest(applied=applied):
                hook = OneShot("/nodes/", applied)
                st = self.h.store("node%d" % applied, push_hook=hook)
                hook.armed = True
                st.announce_node("n%d" % applied, {"note": "liveness"})
                self.assertEqual(hook.fired, 1)
                self.assertIn("n%d" % applied, self.h.coordinator.nodes())


class TestAmbiguityPerChain(AmbiguityEverywhere, unittest.TestCase):
    LAYOUT = S.PER_CHAIN


class TestAmbiguitySingleRef(AmbiguityEverywhere, unittest.TestCase):
    LAYOUT = S.SINGLE_REF


if __name__ == "__main__":
    unittest.main()
