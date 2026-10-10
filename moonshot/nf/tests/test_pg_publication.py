"""C-012-T002: PostgreSQL epoch publication -- written RED, before the schema exists (OP-NF2 s3).

Runs against the canonical cluster in a THROWAWAY schema with throwaway NOLOGIN roles (dropped at teardown), the
pattern fabric's own tests use. Privilege tests are real: they SET ROLE to non-superuser roles before acting.
Requires EW_DB_HOST (or running on M1); otherwise every test is skipped with that reason, loudly."""
import os
import re
import secrets
import subprocess
import sys
import threading
import time
import unittest

from moonshot.epoch import canonical as C
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
        self.admin = self._bounded(pg.connect())
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

    @staticmethod
    def _bounded(conn):
        """A test session never waits on a lock for more than a minute: a wedge becomes a failure."""
        conn.cursor().execute("SET lock_timeout = '60s'")
        conn.commit()
        return conn

    def handle(self, role):
        h = self.pg.Moonshot(self._bounded(self.pg.connect()), self.schema, role=role, actor="test-" + role)
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

    def refused(self, sql, message):
        """`sql`, run by the superuser, must be refused by the moonshot guard that `message` names -- not by a
        foreign key that happens to block the same statement (a BEFORE trigger answers first)."""
        cur = self.admin.cursor()
        with self.subTest(sql=sql):
            try:
                with self.assertRaisesRegex(Exception, re.escape(message)):
                    cur.execute(sql.format(s=self.schema))
            finally:
                # always: a statement that wrongly SUCCEEDED holds its locks until rolled back (a missing contest
                # guard once wedged the whole suite on the resolver's row lock)
                self.admin.rollback()

    def terminate(self, pid):
        """Kill a server backend, as a network fault or a DBA would, and wait until it is gone."""
        cur = self.admin.cursor()
        cur.execute("SELECT pg_terminate_backend(%s)", (pid,))
        self.admin.commit()
        deadline = time.time() + 30
        while time.time() < deadline:
            cur.execute("SELECT count(*) FROM pg_stat_activity WHERE pid = %s", (pid,))
            gone = cur.fetchone()[0] == 0
            self.admin.commit()
            if gone:
                return pid
            time.sleep(0.1)
        self.fail("backend {} survived pg_terminate_backend".format(pid))


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
        # Guards against accidental rewrites, not a boundary against a superuser (who can disable triggers).
        # Mutation PM07 survived the first version of this test: its DELETE hit a referenced row, so a foreign key
        # refused it and the results guard could vanish unnoticed. Each refusal now names its guard.
        rs = self.run_chain_to(1)
        self.handle("validator").record_validation("C1", 1, rs[0].epoch_digest, "VALIDATED", ["REPLAY"],
                                                   rs[0].epoch_digest, "test")
        s = self.schema
        for table, col in (("objects", "created_at"), ("results", "first_seen_at"), ("attempts", "classified_at"),
                           ("validations", "validated_at"), ("events", "at")):
            self.refused("UPDATE {s}." + table + " SET " + col + " = now()",
                         "moonshot: UPDATE on {}.{} is forbidden".format(s, table))
            self.refused("DELETE FROM {s}." + table, "moonshot: DELETE on {}.{} is forbidden".format(s, table))
        self.refused("UPDATE {s}.publications SET published_by = 'x'", "moonshot: a publication's content is immutable")
        self.refused("DELETE FROM {s}.publications", "moonshot: publications are never deleted")
        for table in ("objects", "chains", "results", "publications", "attempts", "contests", "validations", "events"):
            self.refused("TRUNCATE {s}." + table + " CASCADE", "moonshot: TRUNCATE on {}.{} is forbidden".format(s, table))

    def test_the_database_admits_one_live_publication_per_position(self):
        # The chain lock and guard already prevent a second live row through the API; this is the index beneath
        # them, tested directly (a superuser INSERT), so it cannot vanish unnoticed.
        rs = self.run_chain_to(1)
        self.refused("INSERT INTO {s}.publications (chain_id, epoch_index, work_id, epoch_digest, generation, "
                     "attempt_id, published_by) VALUES ('C1', 1, '" + rs[0].work_id + "', '" + rs[0].epoch_digest +
                     "', 99, 'att-x', 'x')", "publications_one_live")

    def test_chain_identity_is_immutable_and_its_generation_only_grows(self):
        self.run_chain_to(2)
        self.refused("UPDATE {s}.chains SET approved_code_sha = repeat('d', 40)", "moonshot: a chain's identity is immutable")
        self.refused("UPDATE {s}.chains SET generation = generation - 1", "moonshot: a chain's generation never decreases")
        self.refused("UPDATE {s}.chains SET head_index = 1, head_epoch_digest = 'x'",
                     "moonshot: a head move must advance the generation")
        self.refused("DELETE FROM {s}.chains", "moonshot: chains are never deleted")


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

    def test_the_claimed_parent_must_be_the_head(self):
        # Generation and input checkpoint both match; only the claimed parent is wrong. Publishing would write a
        # false parent_epoch_digest into the lineage (mutation PM02 survived the first suite).
        rs = self.run_chain_to(1)
        r2 = self.epoch(2, rs[0].checkpoint)
        self.assertEqual(self.publish(self.pub, 2, r2, "a" * 64, 1)["outcome"], O_STALE)
        self.assertEqual(self.handle("reader").head("C1")["head_index"], 1)

    def test_an_epoch_from_another_input_never_extends_the_lineage(self):
        # the right parent and generation, computed from a checkpoint that is not the head's output
        rs = self.run_chain_to(2)
        off = self.epoch(3, rs[0].checkpoint)
        self.assertEqual(self.publish(self.pub, 3, off, rs[1].epoch_digest, 2)["outcome"], O_STALE)
        self.assertEqual(self.handle("reader").head("C1")["head_index"], 2)

    def test_the_database_checks_every_manifest_claim(self):
        # verify=False: the publisher's checks are off, so each refusal below is the database's own
        r = self.epoch(1, self.g.initial_checkpoint)

        def manifest(**change):
            m = dict(r.manifest, **change)
            return C.canonical_bytes({k: v for k, v in m.items() if v is not None})

        flip = lambda b: bytes([b[0] ^ 1]) + b[1:]  # noqa: E731 -- same length, different hash
        cases = [("spec_sha256", dict(spec=b"{}")),
                 ("trace_sha256", dict(trace=flip(r.trace))),
                 ("output_checkpoint_sha256", dict(checkpoint=flip(r.checkpoint))),
                 ("trace_bytes", dict(manifest=manifest(trace_bytes=len(r.trace) + 1))),
                 ("output_checkpoint_bytes", dict(manifest=manifest(output_checkpoint_bytes=len(r.checkpoint) + 1))),
                 ("position", dict(manifest=manifest(epoch_index=2))),
                 ("position", dict(manifest=manifest(chain_id="C9"))),
                 ("identity fields", dict(manifest=manifest(work_id=None))),
                 ("manifest unreadable", dict(manifest=b"\xff not a manifest"))]
        reader = self.handle("reader")
        for error, change in cases:
            with self.subTest(error=error, change=sorted(change)):
                a = self.attempt()
                res = self.pub.publish(a, "tsk-test", "C1", 1, None, 0, dict(r.files(), **change), verify=False)
                self.assertEqual(res["outcome"], O_INV)
                errs = reader.attempt(a)["detail"]["errors"]
                self.assertTrue(any(e.startswith(error) for e in errs), errs)
        self.assertEqual(reader.head("C1")["head_index"], 0)

    def test_the_publisher_refuses_a_forged_identity(self):
        # Every byte hash is consistent, so the database alone would accept it: only the publisher's
        # recomputation of the C-008 identity catches the forgery (mutation PM12 survived the first suite).
        r = self.epoch(1, self.g.initial_checkpoint)
        forged = dict(r.files(), manifest=C.canonical_bytes(dict(r.manifest, epoch_digest="b" * 64)))
        a = self.attempt()
        self.assertEqual(self.pub.publish(a, "tsk-test", "C1", 1, None, 0, forged)["outcome"], O_INV)
        h = self.handle("reader")
        self.assertIn("epoch_digest does not recompute", h.attempt(a)["detail"]["errors"])
        self.assertEqual(h.head("C1")["head_index"], 0)

    def test_the_publisher_refuses_a_spec_this_chain_did_not_derive(self):
        # a self-consistent epoch of a look-alike chain (same id and input, other parameters)
        other = model.make_genesis("C1", epochs=4, params={"work_iterations": 61, "trace_every": 20,
                                                           "checkpoint_bytes": 64},
                                   approved_code_sha=APPROVED, initial_checkpoint=b"pg genesis C1")
        r = self.epoch(1, self.g.initial_checkpoint, g=other)
        a = self.attempt()
        self.assertEqual(self.pub.publish(a, "tsk-test", "C1", 1, None, 0, r.files())["outcome"], O_INV)
        h = self.handle("reader")
        self.assertIn("SPEC is not the derived spec", h.attempt(a)["detail"]["errors"])
        self.assertEqual(h.head("C1")["head_index"], 0)

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
        env = dict(os.environ, PYTHONPATH=os.pathsep.join(p for p in (REPO, os.environ.get("PYTHONPATH")) if p))
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

    # The three tests below exercise the reconnect path for real (mutation PM13 survived the first suite: no test
    # ever lost a connection inside the publishing process).

    def test_a_dead_connection_is_replaced_before_publishing(self):
        pid = self.terminate(self.pub.conn.get_backend_pid())
        r = self.epoch(1, self.g.initial_checkpoint)
        res = self.publish(self.pub, 1, r, None, 0)
        self.assertEqual((res["outcome"], res["replayed"]), (O_PUB, False))
        self.assertNotEqual(self.pub.conn.get_backend_pid(), pid)
        self.assertEqual(self.handle("reader").attempt_count("C1"), 1)

    def test_a_connection_killed_inside_the_transaction_is_retried_cleanly(self):
        r = self.epoch(1, self.g.initial_checkpoint)
        pid, out = self.pub.conn.get_backend_pid(), {}

        def go():
            try:
                out["res"] = self.publish(self.pub, 1, r, None, 0, _hold_before_commit_s=8)
            except Exception as e:  # pragma: no cover - reported below
                out["err"] = repr(e)

        t = threading.Thread(target=go)
        t.start()
        h = self.handle("reader")
        deadline = time.time() + 60
        while time.time() < deadline and not h.publisher_waiting(self.schema):
            time.sleep(0.1)
        self.assertTrue(h.publisher_waiting(self.schema), "the publisher never reached its hold point")
        self.terminate(pid)                   # the server rolls the open transaction back
        t.join(60)
        self.assertNotIn("err", out)
        self.assertEqual((out["res"]["outcome"], out["res"]["replayed"]), (O_PUB, False))
        self.assertEqual((len(h.lineage("C1")), h.attempt_count("C1")), (1, 1))

    def test_a_lost_acknowledgement_in_process_reconnects_and_gets_the_record(self):
        # the server commits, the connection dies before the client hears it (injected after COMMIT returns)
        r = self.epoch(1, self.g.initial_checkpoint)
        pid = self.pub.conn.get_backend_pid()
        res = self.publish(self.pub, 1, r, None, 0, _lose_acks=1)
        self.assertEqual((res["outcome"], res["replayed"]), (O_PUB, True))
        self.assertNotEqual(self.pub.conn.get_backend_pid(), pid)
        h = self.handle("reader")
        self.assertEqual((len(h.lineage("C1")), h.attempt_count("C1")), (1, 1))


class TestValidationAndContests(PgCase):
    def test_publication_starts_unvalidated_and_only_a_validator_validates(self):
        rs = self.run_chain_to(1)
        h = self.handle("reader")
        self.assertEqual(h.validation_state("C1", 1), "UNVALIDATED")
        with self.assertRaises(Exception):
            self.pub.record_validation("C1", 1, rs[0].epoch_digest, "VALIDATED", ["BYTES"], rs[0].epoch_digest, "test")
        v = self.handle("validator")
        v.record_validation("C1", 1, rs[0].epoch_digest, "VALIDATED", ["BYTES", "REPLAY"], rs[0].epoch_digest, "M2")
        self.assertEqual(h.validation_state("C1", 1), "VALIDATED")

    def test_a_validation_names_the_bytes_it_validated(self):
        # A validation is about one digest. One that names a digest no longer live (the epoch was overturned and
        # re-published meanwhile) is stale and refused, never attributed to whatever is live now.
        rs = self.run_chain_to(1)
        v = self.handle("validator")
        with self.assertRaisesRegex(Exception, "stale validation"):
            v.record_validation("C1", 1, "f" * 64, "VALIDATED", ["REPLAY"], "f" * 64, "M2")
        with self.assertRaisesRegex(Exception, "a replay that disagrees is a MISMATCH"):
            v.record_validation("C1", 1, rs[0].epoch_digest, "VALIDATED", ["REPLAY"], "e" * 64, "M2")
        with self.assertRaisesRegex(Exception, "a MISMATCH needs a disagreeing replay digest"):
            v.record_validation("C1", 1, rs[0].epoch_digest, "MISMATCH", ["REPLAY"], rs[0].epoch_digest, "M2")
        with self.assertRaisesRegex(Exception, "a REPLAY check needs its replay digest"):
            v.record_validation("C1", 1, rs[0].epoch_digest, "VALIDATED", ["REPLAY"], None, "M2")
        self.assertEqual(self.handle("reader").validation_state("C1", 1), "UNVALIDATED")

    def test_validation_mismatch_with_descendants_taints_and_halts(self):
        rs = self.run_chain_to(3)
        v = self.handle("validator")
        v.record_validation("C1", 2, rs[1].epoch_digest, "MISMATCH", ["BYTES", "REPLAY"], "e" * 64, "M2")
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
        # an unresolved contest stays open: a later unanimous replay still resolves it
        self.assertEqual(self.handle("resolver").resolve_contest(cid, [good.epoch_digest] * 3), "UPHELD")
        self.assertEqual(self.handle("reader").head("C1")["state"], "OPEN")

    def test_overturn_at_a_later_epoch_rewinds_to_its_parent(self):
        rs = self.run_chain_to(1)
        bad2 = self.epoch(2, rs[0].checkpoint, planted_runner())
        good2 = self.epoch(2, rs[0].checkpoint)
        self.assertEqual(self.publish(self.pub, 2, bad2, rs[0].epoch_digest, 1)["outcome"], O_PUB)
        bad3 = self.epoch(3, bad2.checkpoint)
        self.assertEqual(self.publish(self.pub, 3, bad3, bad2.epoch_digest, 2)["outcome"], O_PUB)
        self.assertEqual(self.publish(self.pub, 2, good2, rs[0].epoch_digest, 1)["outcome"], O_DIS)
        cid = self.handle("reader").open_contest("C1")["contest_id"]
        self.assertEqual(self.handle("resolver").resolve_contest(cid, [good2.epoch_digest] * 2), "OVERTURNED")
        h = self.handle("reader")
        head = h.head("C1")
        self.assertEqual((head["head_index"], head["head_epoch_digest"], head["head_checkpoint_sha256"],
                          head["generation"], head["state"]),
                         (1, rs[0].epoch_digest, rs[0].manifest["output_checkpoint_sha256"], 4, "OPEN"))
        self.assertEqual(h.rejected_epochs("C1"), [(2, bad2.epoch_digest), (3, bad3.epoch_digest)])
        self.assertEqual(self.publish(self.pub, 2, good2, rs[0].epoch_digest, 4)["outcome"], O_PUB)
        self.assertEqual([p["epoch_digest"] for p in h.lineage("C1")], [rs[0].epoch_digest, good2.epoch_digest])

    def test_bytes_that_fail_validation_open_a_contest_and_can_be_overturned(self):
        rs = self.run_chain_to(2)
        self.handle("validator").record_validation("C1", 2, rs[1].epoch_digest, "INVALID", ["BYTES"], None, "M2")
        h = self.handle("reader")
        c = h.open_contest("C1")
        self.assertEqual((c["reason"], c["state"], c["epoch_index"]), ("CORRUPT_BYTES", "CONTESTED", 2))
        self.assertEqual(h.head("C1")["state"], "HALTED")
        verdict = self.handle("resolver").resolve_contest(c["contest_id"], [rs[1].epoch_digest],
                                                          published_bytes_ok=False)
        self.assertEqual(verdict, "OVERTURNED")
        self.assertEqual((h.head("C1")["head_index"], h.head("C1")["state"]), (1, "OPEN"))

    def test_an_adverse_validation_during_an_open_contest_is_not_dropped(self):
        # Fail closed. A MISMATCH recorded while another contest is open cannot open a second one; resolving the
        # first must not reopen the chain over it (found reviewing the GREEN tree: it did).
        rs = self.run_chain_to(3)
        bad1 = self.epoch(1, self.g.initial_checkpoint, planted_runner())
        self.assertEqual(self.publish(self.pub, 1, bad1, None, 0)["outcome"], O_DIS)      # TAINTED at epoch 1
        first = self.handle("reader").open_contest("C1")
        self.handle("validator").record_validation("C1", 3, rs[2].epoch_digest, "MISMATCH", ["REPLAY"], "e" * 64,
                                                   "M2")
        self.assertEqual(self.handle("reader").open_contest("C1")["contest_id"], first["contest_id"])
        self.assertEqual(self.handle("resolver").resolve_contest(first["contest_id"], [rs[0].epoch_digest] * 2),
                         "UPHELD")
        h = self.handle("reader")
        nxt = h.open_contest("C1")
        self.assertIsNotNone(nxt, "the pending MISMATCH was dropped: the chain reopened over it")
        self.assertEqual((nxt["epoch_index"], nxt["reason"], nxt["state"]), (3, "AUDIT_MISMATCH", "CONTESTED"))
        self.assertEqual(h.head("C1")["state"], "HALTED")

    def test_contest_grounds_are_immutable_and_a_resolution_is_final(self):
        good = self.epoch(1, self.g.initial_checkpoint)
        bad = self.epoch(1, self.g.initial_checkpoint, planted_runner())
        self.publish(self.pub, 1, good, None, 0)
        self.publish(self.pub, 1, bad, None, 0)
        cid = self.handle("reader").open_contest("C1")["contest_id"]
        self.refused("UPDATE {s}.contests SET challenger_epoch_digest = 'x'", "moonshot: a contest's grounds are immutable")
        self.refused("DELETE FROM {s}.contests", "moonshot: contests are never deleted")
        self.handle("resolver").resolve_contest(cid, [good.epoch_digest])
        self.refused("UPDATE {s}.contests SET state = 'CONTESTED'", "moonshot: a resolved contest stays resolved")


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
