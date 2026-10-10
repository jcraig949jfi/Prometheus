"""C-012-T002: PostgreSQL epoch publication -- written RED, before the schema exists (OP-NF2 s3).

Runs against the canonical cluster in a THROWAWAY schema with throwaway NOLOGIN roles (dropped at teardown), the
pattern fabric's own tests use. Privilege tests are real: they SET ROLE to non-superuser roles before acting.
Requires EW_DB_HOST (or running on M1); otherwise every test is skipped with that reason, loudly."""
import os
import secrets
import subprocess
import sys
import threading
import time
import unittest

from moonshot.epoch import model
from moonshot.epoch.tests.harness import planted_runner

PG = bool(os.environ.get("EW_DB_HOST"))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
APPROVED = "c0de" * 10
O_PUB, O_DUP, O_DIS, O_STALE, O_INV, O_REF, O_HALT = ("PUBLISHED", "DUPLICATE", "DISAGREEMENT", "STALE", "INVALID",
                                                      "REFUSED_UNAPPROVED", "HALTED")


def genesis(cid="C1", epochs=4):
    return model.make_genesis(cid, epochs=epochs, params={"work_iterations": 60, "trace_every": 20,
                                                          "checkpoint_bytes": 64},
                              approved_code_sha=APPROVED, initial_checkpoint=b"pg genesis " + cid.encode())


@unittest.skipUnless(PG, "EW_DB_HOST is not set: PostgreSQL publication tests need the canonical cluster")
class PgCase(unittest.TestCase):
    """A throwaway schema per test; helpers to act under each role."""

    def setUp(self):
        from moonshot.nf import pg
        self.pg = pg
        self.schema = "moonshot_t_" + secrets.token_hex(4)
        self.admin = pg.connect()
        pg.init_schema(self.admin, self.schema)
        self.addCleanup(self._drop)
        self.coord = self.handle("coordinator")
        self.pub = self.handle("publisher")
        self.g = genesis()
        self.coord.create_chain(self.g, namespace="test", approved_code_sha=APPROVED)
        self._n = 0

    def _drop(self):
        for h in getattr(self, "_handles", []):
            try:
                h.close()
            except Exception:
                pass
        self.pg.drop_schema(self.admin, self.schema)
        self.admin.close()

    def handle(self, role):
        h = self.pg.Moonshot(self.pg.connect(), self.schema, role=role, actor="test-" + role)
        self.__dict__.setdefault("_handles", []).append(h)
        return h

    def epoch(self, k, input_ckpt, runner=None, g=None):
        return model.execute((g or self.g).obj, k, input_ckpt, runner)

    def attempt(self):
        self._n += 1
        return "att-test{:06d}".format(self._n)

    def publish(self, h, k, result, expected_parent, expected_generation, chain="C1", attempt=None, **kw):
        return h.publish(attempt or self.attempt(), "tsk-test", chain, k, expected_parent, expected_generation,
                         result.files(), **kw)

    def run_chain_to(self, upto, runner=None):
        """Publish epochs 1..upto honestly (or with `runner`); returns the EpochResults."""
        out, inp, parent = [], self.g.initial_checkpoint, None
        for k in range(1, upto + 1):
            r = self.epoch(k, inp, runner)
            res = self.publish(self.pub, k, r, parent, k - 1)
            self.assertEqual(res["outcome"], O_PUB, res)
            out.append(r)
            inp, parent = r.checkpoint, r.epoch_digest
        return out


class TestSchemaAndIdentity(PgCase):
    def test_schema_version_and_genesis_head(self):
        h = self.handle("reader")
        self.assertEqual(h.schema_version(), self.pg.SCHEMA_VERSION)
        head = h.head("C1")
        self.assertEqual((head["head_index"], head["head_epoch_digest"], head["generation"], head["state"]),
                         (0, None, 0, "OPEN"))
        self.assertEqual(head["head_checkpoint_sha256"], self.g.obj["initial_checkpoint_sha256"])

    def test_published_digest_is_the_c008_semantic_identity(self):
        r = self.epoch(1, self.g.initial_checkpoint)
        res = self.publish(self.pub, 1, r, None, 0)
        self.assertEqual(res["outcome"], O_PUB)
        lin = self.handle("reader").lineage("C1")
        self.assertEqual([(p["epoch_index"], p["epoch_digest"], p["work_id"]) for p in lin],
                         [(1, r.epoch_digest, r.work_id)])
        files = self.handle("reader").epoch_files("C1", 1)
        self.assertEqual(files, r.files())
        self.assertEqual(model.verify_epoch(files, self.g.obj["initial_checkpoint_sha256"]), [])

    def test_objects_are_content_addressed_by_the_database(self):
        cur = self.admin.cursor()
        with self.assertRaises(Exception):
            cur.execute("INSERT INTO {}.objects (sha256, size_bytes, content) VALUES (%s, 3, %s)".format(self.schema),
                        ("0" * 64, b"abc"))
        self.admin.rollback()

    def test_immutable_tables_refuse_rewrites_even_by_superuser(self):
        self.run_chain_to(1)
        cur = self.admin.cursor()
        for sql in ("UPDATE {s}.objects SET created_at = now()", "DELETE FROM {s}.results",
                    "UPDATE {s}.publications SET epoch_digest = 'x'", "DELETE FROM {s}.attempts"):
            with self.subTest(sql=sql):
                with self.assertRaises(Exception):
                    cur.execute(sql.format(s=self.schema))
                self.admin.rollback()


class TestGuardedPublication(PgCase):
    def test_identical_repeat_is_idempotent_duplicate(self):
        r = self.epoch(1, self.g.initial_checkpoint)
        self.assertEqual(self.publish(self.pub, 1, r, None, 0)["outcome"], O_PUB)
        self.assertEqual(self.publish(self.pub, 1, r, None, 0)["outcome"], O_DUP)
        h = self.handle("reader")
        self.assertEqual(len(h.lineage("C1")), 1)
        self.assertEqual(h.head("C1")["generation"], 1)

    def test_same_attempt_twice_returns_the_recorded_outcome(self):
        # the lost-acknowledgement path: the retry of one attempt is answered from the record, never re-classified
        r = self.epoch(1, self.g.initial_checkpoint)
        a = self.attempt()
        first = self.publish(self.pub, 1, r, None, 0, attempt=a)
        again = self.publish(self.pub, 1, r, None, 0, attempt=a)
        self.assertEqual((first["outcome"], first["replayed"]), (O_PUB, False))
        self.assertEqual((again["outcome"], again["replayed"], again["publication_id"]),
                         (O_PUB, True, first["publication_id"]))
        self.assertEqual(self.handle("reader").attempt_count("C1"), 1)

    def test_conflicting_result_is_preserved_and_fails_closed(self):
        good = self.epoch(1, self.g.initial_checkpoint)
        bad = self.epoch(1, self.g.initial_checkpoint, planted_runner())
        self.assertEqual(good.work_id, bad.work_id)
        self.assertEqual(self.publish(self.pub, 1, good, None, 0)["outcome"], O_PUB)
        res = self.publish(self.pub, 1, bad, None, 0)
        self.assertEqual(res["outcome"], O_DIS)
        h = self.handle("reader")
        c = h.open_contest("C1")
        self.assertEqual((c["state"], c["epoch_index"], c["published_epoch_digest"], c["challenger_epoch_digest"]),
                         ("CONTESTED", 1, good.epoch_digest, bad.epoch_digest))
        self.assertEqual(h.head("C1")["state"], "HALTED")
        self.assertEqual(sorted(h.results_for_work(good.work_id)), sorted([good.epoch_digest, bad.epoch_digest]))
        # a halted chain advances for nobody
        nxt = self.epoch(2, good.checkpoint)
        self.assertEqual(self.publish(self.pub, 2, nxt, good.epoch_digest, 1)["outcome"], O_HALT)

    def test_late_disagreement_with_descendants_taints(self):
        rs = self.run_chain_to(3)
        bad = self.epoch(2, rs[0].checkpoint, planted_runner())
        self.assertEqual(self.publish(self.pub, 2, bad, rs[0].epoch_digest, 1)["outcome"], O_DIS)
        c = self.handle("reader").open_contest("C1")
        self.assertEqual((c["state"], c["epoch_index"]), ("TAINTED", 2))

    def test_stale_worker_cannot_advance(self):
        rs = self.run_chain_to(2)
        # a late identical epoch 1 is a DUPLICATE, never a second advance
        self.assertEqual(self.publish(self.pub, 1, rs[0], None, 0)["outcome"], O_DUP)
        # the right parent but a wrong generation: refused (strict guard), and nothing moves
        r3 = self.epoch(3, rs[1].checkpoint)
        self.assertEqual(self.publish(self.pub, 3, r3, rs[1].epoch_digest, 7)["outcome"], O_STALE)
        head = self.handle("reader").head("C1")
        self.assertEqual((head["head_index"], head["generation"]), (2, 2))
        # work for a parent that is not on the lineage (expected parent from elsewhere)
        other = self.epoch(3, b"not the lineage")
        self.assertEqual(self.publish(self.pub, 3, other, "f" * 64, 2)["outcome"], O_STALE)

    def test_bytes_that_disagree_with_their_manifest_are_invalid(self):
        r = self.epoch(1, self.g.initial_checkpoint)
        files = dict(r.files(), trace=r.trace + b"tampered\n")
        res = self.pub.publish(self.attempt(), "tsk-test", "C1", 1, None, 0, files)
        self.assertEqual(res["outcome"], O_INV)
        self.assertEqual(self.handle("reader").head("C1")["head_index"], 0)

    def test_database_checks_hashes_even_when_the_client_skips_verification(self):
        r = self.epoch(1, self.g.initial_checkpoint)
        files = dict(r.files(), checkpoint=r.checkpoint[:-1] + b"\x00")
        res = self.pub.publish(self.attempt(), "tsk-test", "C1", 1, None, 0, files, verify=False)
        self.assertEqual(res["outcome"], O_INV)
        self.assertEqual(self.handle("reader").head("C1")["head_index"], 0)

    def test_unapproved_code_is_refused_without_publication(self):
        r = self.epoch(1, self.g.initial_checkpoint)
        res = self.pub.publish(self.attempt(), "tsk-test", "C1", 1, None, 0, r.files(), approved=False)
        self.assertEqual(res["outcome"], O_REF)
        self.assertEqual(self.handle("reader").head("C1")["head_index"], 0)

    def test_completion(self):
        self.run_chain_to(4)
        self.assertEqual(self.handle("reader").head("C1")["state"], "COMPLETE")


class TestConcurrency(PgCase):
    def _race(self, results):
        """Publish every result for epoch 1 at once, each on its own connection; returns the outcomes."""
        out, errors = [], []
        barrier = threading.Barrier(len(results))

        def go(r):
            h = self.handle("publisher")
            try:
                barrier.wait()
                out.append(self.publish(h, 1, r, None, 0)["outcome"])
            except Exception as e:  # pragma: no cover - reported below
                errors.append(repr(e))

        ts = [threading.Thread(target=go, args=(r,)) for r in results]
        for t in ts:
            t.start()
        for t in ts:
            t.join(60)
        self.assertEqual(errors, [])
        return out

    def test_eight_identical_racers_one_publication(self):
        r = self.epoch(1, self.g.initial_checkpoint)
        out = self._race([r] * 8)
        self.assertEqual((out.count(O_PUB), out.count(O_DUP)), (1, 7))
        self.assertEqual(len(self.handle("reader").lineage("C1")), 1)

    def test_mixed_racers_one_publication_one_contest(self):
        good = self.epoch(1, self.g.initial_checkpoint)
        bad = self.epoch(1, self.g.initial_checkpoint, planted_runner())
        out = self._race([good, bad] * 4)
        self.assertEqual((out.count(O_PUB), out.count(O_DIS)), (1, 1))
        self.assertEqual(out.count(O_PUB) + out.count(O_DUP) + out.count(O_DIS) + out.count(O_HALT), 8)
        h = self.handle("reader")
        self.assertEqual(len(h.lineage("C1")), 1)
        self.assertEqual(h.head("C1")["state"], "HALTED")
        self.assertEqual(sorted(h.results_for_work(good.work_id)), sorted([good.epoch_digest, bad.epoch_digest]))


class TestCrashAndRollback(PgCase):
    def _child(self, mode, attempt):
        """A separate publisher process (killable); mode chooses where it stops."""
        code = ("import sys,time; from moonshot.nf import pg; from moonshot.nf.tests import test_pg_publication as T\n"
                "h = pg.Moonshot(pg.connect(), sys.argv[1], role='publisher', actor='child')\n"
                "r = T.model.execute(T.genesis().obj, 1, T.genesis().initial_checkpoint)\n"
                "res = h.publish(sys.argv[2], 'tsk-child', 'C1', 1, None, 0, r.files(), _hold_before_commit_s=float(sys.argv[3]))\n"
                "print(res['outcome'], flush=True)\n")
        hold = {"before_commit": "8", "commit": "0"}[mode]
        env = dict(os.environ, PYTHONPATH=REPO)
        return subprocess.Popen([sys.executable, "-c", code, self.schema, attempt, hold], cwd=REPO, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_killed_inside_the_transaction_leaves_nothing(self):
        a = self.attempt()
        p = self._child("before_commit", a)
        h = self.handle("reader")
        deadline = time.time() + 60
        while time.time() < deadline and not h.publisher_waiting(self.schema):
            time.sleep(0.2)
        self.assertTrue(h.publisher_waiting(self.schema), "child never reached its hold point")
        p.kill()
        p.wait(30)
        time.sleep(1.0)
        self.assertEqual((h.head("C1")["head_index"], h.attempt_count("C1")), (0, 0))
        r = self.epoch(1, self.g.initial_checkpoint)
        res = self.publish(self.pub, 1, r, None, 0, attempt=a)        # the restarted publisher
        self.assertEqual((res["outcome"], res["replayed"]), (O_PUB, False))

    def test_lost_ack_after_commit_resolves_by_replay(self):
        a = self.attempt()
        p = self._child("commit", a)
        out, err = p.communicate(timeout=120)
        self.assertEqual(out.decode().strip(), O_PUB, err.decode()[-500:])
        # the parent never saw that answer (as if the acknowledgement were lost): it retries the same attempt
        r = self.epoch(1, self.g.initial_checkpoint)
        res = self.publish(self.pub, 1, r, None, 0, attempt=a)
        self.assertEqual((res["outcome"], res["replayed"]), (O_PUB, True))
        self.assertEqual(len(self.handle("reader").lineage("C1")), 1)

    def test_error_mid_transaction_rolls_back(self):
        r = self.epoch(1, self.g.initial_checkpoint)
        with self.assertRaises(Exception):
            self.pub.publish(self.attempt(), "tsk-test", "C1", 1, None, 0, r.files(), _raise_before_commit=True)
        h = self.handle("reader")
        self.assertEqual((h.head("C1")["head_index"], h.attempt_count("C1"), h.object_count()), (0, 0, 2))


class TestValidationAndContests(PgCase):
    def test_publication_starts_unvalidated_and_only_a_validator_validates(self):
        rs = self.run_chain_to(1)
        h = self.handle("reader")
        self.assertEqual(h.validation_state("C1", 1), "UNVALIDATED")
        with self.assertRaises(Exception):
            self.pub.record_validation("C1", 1, "VALIDATED", ["BYTES"], rs[0].epoch_digest, "test")
        v = self.handle("validator")
        v.record_validation("C1", 1, "VALIDATED", ["BYTES", "REPLAY"], rs[0].epoch_digest, "M2")
        self.assertEqual(h.validation_state("C1", 1), "VALIDATED")

    def test_validation_mismatch_with_descendants_taints_and_halts(self):
        rs = self.run_chain_to(3)
        v = self.handle("validator")
        v.record_validation("C1", 2, "MISMATCH", ["BYTES", "REPLAY"], "e" * 64, "M2")
        h = self.handle("reader")
        c = h.open_contest("C1")
        self.assertEqual((c["state"], c["epoch_index"], c["reason"]), ("TAINTED", 2, "AUDIT_MISMATCH"))
        self.assertEqual(h.head("C1")["state"], "HALTED")

    def test_resolution_upheld(self):
        good = self.epoch(1, self.g.initial_checkpoint)
        bad = self.epoch(1, self.g.initial_checkpoint, planted_runner())
        self.publish(self.pub, 1, good, None, 0)
        self.publish(self.pub, 1, bad, None, 0)
        cid = self.handle("reader").open_contest("C1")["contest_id"]
        with self.assertRaises(Exception):
            self.pub.resolve_contest(cid, [good.epoch_digest])
        verdict = self.handle("resolver").resolve_contest(cid, [good.epoch_digest, good.epoch_digest])
        self.assertEqual(verdict, "UPHELD")
        h = self.handle("reader")
        self.assertIsNone(h.open_contest("C1"))
        self.assertEqual((h.head("C1")["state"], h.head("C1")["head_index"]), ("OPEN", 1))

    def test_resolution_overturned_rewinds_and_stale_follows(self):
        bad = self.epoch(1, self.g.initial_checkpoint, planted_runner())
        good = self.epoch(1, self.g.initial_checkpoint)
        self.publish(self.pub, 1, bad, None, 0)                        # the faulty result got there first
        bad2 = self.epoch(2, bad.checkpoint)
        self.assertEqual(self.publish(self.pub, 2, bad2, bad.epoch_digest, 1)["outcome"], O_PUB)
        self.assertEqual(self.publish(self.pub, 1, good, None, 0)["outcome"], O_DIS)   # TAINTED (a descendant)
        cid = self.handle("reader").open_contest("C1")["contest_id"]
        self.assertEqual(self.handle("resolver").resolve_contest(cid, [good.epoch_digest]), "OVERTURNED")
        h = self.handle("reader")
        head = h.head("C1")
        self.assertEqual((head["head_index"], head["state"], head["generation"]), (0, "OPEN", 3))
        self.assertEqual(h.rejected_epochs("C1"), [(1, bad.epoch_digest), (2, bad2.epoch_digest)])
        # work built on the rejected branch can no longer advance anything
        bad3 = self.epoch(3, bad2.checkpoint)
        self.assertEqual(self.publish(self.pub, 3, bad3, bad2.epoch_digest, 2)["outcome"], O_STALE)
        # the honest epoch re-publishes on the rewound lineage
        self.assertEqual(self.publish(self.pub, 1, good, None, 3)["outcome"], O_PUB)

    def test_resolution_unresolved_stays_halted(self):
        good = self.epoch(1, self.g.initial_checkpoint)
        bad = self.epoch(1, self.g.initial_checkpoint, planted_runner())
        self.publish(self.pub, 1, good, None, 0)
        self.publish(self.pub, 1, bad, None, 0)
        cid = self.handle("reader").open_contest("C1")["contest_id"]
        self.assertEqual(self.handle("resolver").resolve_contest(cid, [good.epoch_digest, bad.epoch_digest]),
                         "UNRESOLVED")
        self.assertEqual(self.handle("reader").head("C1")["state"], "HALTED")


class TestAuthority(PgCase):
    def test_roles_cannot_exceed_their_function(self):
        r = self.epoch(1, self.g.initial_checkpoint)
        for role in ("reader", "validator", "resolver", "coordinator"):
            with self.subTest(role=role):
                with self.assertRaises(Exception):
                    self.publish(self.handle(role), 1, r, None, 0)
        with self.assertRaises(Exception):
            self.pub.create_chain(genesis("C2"), namespace="test", approved_code_sha=APPROVED)

    def test_no_role_writes_tables_directly(self):
        for role in ("reader", "publisher", "validator", "resolver", "coordinator"):
            with self.subTest(role=role):
                h = self.handle(role)
                with self.assertRaises(Exception):
                    h.raw("UPDATE {}.chains SET head_index = 3".format(self.schema))

    def test_public_has_nothing(self):
        self.assertEqual(self.handle("reader").public_privileges(self.schema), [])


if __name__ == "__main__":
    unittest.main()
