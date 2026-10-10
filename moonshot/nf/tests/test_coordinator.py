"""C-012-T003: the Moonshot coordinator over Fabric -- dispatch (fabric.store.submit), publish (Fabric artifacts ->
moonshot.publish), validate and resolve by replay, durable receipts.

Runs against a THROWAWAY Fabric schema (FABRIC_SCHEMA, the pattern fabric's own tests use) and a THROWAWAY Moonshot
schema on the canonical cluster. The worker is simulated in-process with Fabric's own calls (claim -> run the
executor as the script executor does -> add_artifact -> finish_attempt) because fabric.worker needs fcntl (POSIX);
the real worker runs in the two-node demonstration. Requires EW_DB_HOST."""
import json
import os
import secrets
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from moonshot.epoch import canonical as C
from moonshot.epoch import model

PG = bool(os.environ.get("EW_DB_HOST"))
REPO = Path(__file__).resolve().parents[3]
APPROVED = "c0de" * 10
OTHER_SHA = "beef" * 10
CAPS = ["fabric.runtime==0.2", "moonshot.epoch.v1", "python.stdlib"]
FILES = {"manifest": "MANIFEST.json", "spec": "SPEC.json", "trace": "TRACE", "checkpoint": "CHECKPOINT"}


def genesis(cid="Q1", epochs=3):
    return model.make_genesis(cid, epochs=epochs, params={"work_iterations": 60, "trace_every": 20,
                                                          "checkpoint_bytes": 64},
                              approved_code_sha=APPROVED, initial_checkpoint=b"coordinator " + cid.encode())


class SimWorker:
    """One claim -> one execution -> artifacts -> finish, through fabric.store exactly as fabric.worker does,
    except that the 'pinned checkout' is this checkout (it reports the task's base_sha as its worktree head)."""

    def __init__(self, fab, host, faults_dir, *, agent=None, fail=False):
        from fabric import store as S
        self.S, self.fab, self.host, self.faults, self.fail = S, fab, host, faults_dir, fail
        self.agent = agent or "worker.{}.moonshot".format(host)
        self.instance = "{}-{}".format(host, secrets.token_hex(3))

    def run_one(self):
        S = self.S
        got = S.claim(self.fab, self.agent, self.instance, self.host, CAPS, ["script"], ttl_s=120)
        if got is None:
            return None
        task, aid = got["task"], got["attempt_id"]
        params = task["params"] if isinstance(task["params"], dict) else json.loads(task["params"])
        with tempfile.TemporaryDirectory(prefix="sim-") as d:
            out = Path(d) / "out"
            out.mkdir()
            env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8", "HOME": d,
                   "FABRIC_OUT_DIR": str(out), "MOONSHOT_FAULT_DIR": str(self.faults)}
            if os.name == "nt":
                env.update({k: os.environ[k] for k in ("SYSTEMROOT", "TEMP", "TMP") if k in os.environ})
            cmd = [sys.executable, "-E", "-s", "-m", params["module"]] + list(params.get("args") or [])
            if self.fail:
                cmd = [sys.executable, "-c", "import sys; sys.exit(3)"]
            r = subprocess.run(cmd, cwd=str(REPO), env=env, capture_output=True, timeout=120)
            S.add_artifact(self.fab, task["task_id"], aid, "stdout", "stdout", r.stdout, actor=self.agent)
            S.add_artifact(self.fab, task["task_id"], aid, "stderr", "stderr", r.stderr, actor=self.agent)
            for f in sorted(out.iterdir()):
                S.add_artifact(self.fab, task["task_id"], aid, f.name, "file", f.read_bytes(),
                               media_type="application/octet-stream", actor=self.agent)
        receipt = {"host": self.host, "agent": self.agent, "instance": self.instance, "base_sha": task.get("base_sha"),
                   "worktree_head": task.get("base_sha"), "exit_code": r.returncode}
        S.finish_attempt(self.fab, aid, "succeeded" if r.returncode == 0 else "failed", self.agent,
                         exit_code=r.returncode, env_receipt=receipt)
        return {"task_id": task["task_id"], "attempt_id": aid, "exit_code": r.returncode}


@unittest.skipUnless(PG, "EW_DB_HOST is not set: coordinator tests need the canonical cluster")
class CoordCase(unittest.TestCase):
    def setUp(self):
        from fabric import store as S
        from moonshot.nf import coordinator as K
        from moonshot.nf import pg
        self.S, self.K, self.pg = S, K, pg
        tag = secrets.token_hex(4)
        self.fschema, self.schema = "fabric_t_" + tag, "moonshot_t_" + tag
        old = os.environ.get("FABRIC_SCHEMA")
        os.environ["FABRIC_SCHEMA"] = self.fschema
        self.addCleanup(lambda: os.environ.__setitem__("FABRIC_SCHEMA", old) if old else
                        os.environ.pop("FABRIC_SCHEMA", None))
        self.fab = S.connect(require_schema=False)
        S.init_schema(self.fab)
        self.admin = pg.connect()
        pg.init_schema(self.admin, self.schema)
        self.addCleanup(self._drop)
        self.tmp = tempfile.TemporaryDirectory(prefix="co-")
        self.addCleanup(self.tmp.cleanup)
        self.faults = Path(self.tmp.name)
        self.co = K.Coordinator(self.schema, principal="Themis-test", campaign="C-012-test", actor="test-coordinator")
        self.g = genesis()
        self.co.create_chain(self.g, namespace="qual")

    def _drop(self):
        try:
            self.co.close()
        except Exception:
            pass
        self.pg.drop_schema(self.admin, self.schema)
        self.admin.close()
        cur = self.fab.cursor()
        cur.execute("DROP SCHEMA IF EXISTS {} CASCADE".format(self.fschema))
        self.fab.commit()
        self.fab.close()

    def worker(self, host, **kw):
        d = self.faults / host                    # node-local: each simulated host has its own fault directory
        d.mkdir(exist_ok=True)
        return SimWorker(self.fab, host, d, **kw)

    def fault(self, host, **spec):
        d = self.faults / host
        d.mkdir(exist_ok=True)
        (d / "qual.json").write_text(json.dumps([dict(spec, chain_id=spec.get("chain_id", "Q1"))]), encoding="utf-8")

    def clear_fault(self, host):
        (self.faults / host / "qual.json").unlink()

    def reader(self):
        return self.co.reader

    def step(self, chain="Q1", host="hostA"):
        """Dispatch the next epoch, run it, publish it; returns the publish result."""
        self.co.dispatch(chain)
        self.assertIsNotNone(self.worker(host).run_one())
        out = self.co.publish_ready()
        self.assertEqual(len(out), 1, out)
        return out[0]


class TestHappyPath(CoordCase):
    def test_one_chain_end_to_end_is_the_c008_identity(self):
        for k in (1, 2, 3):
            res = self.step()
            self.assertEqual((res["outcome"], res["epoch_index"]), ("PUBLISHED", k), res)
        ref = model.replay_chain(self.g, 3)
        lin = self.reader().lineage("Q1")
        self.assertEqual([p["epoch_digest"] for p in lin], [r.epoch_digest for r in ref])
        self.assertEqual(self.reader().head("Q1")["state"], "COMPLETE")

    def test_validation_moves_unvalidated_to_validated(self):
        self.step()
        self.assertEqual(self.reader().validation_state("Q1", 1), "UNVALIDATED")
        self.assertEqual(self.co.validate("Q1"), [(1, "VALIDATED")])
        self.assertEqual(self.reader().validation_state("Q1", 1), "VALIDATED")
        self.assertEqual(self.co.validate("Q1"), [])                       # nothing left to validate

    def test_the_receipt_is_durable_canonical_and_complete(self):
        for _ in range(3):
            self.step()
        self.co.validate("Q1")
        rec = self.co.receipt("Q1")
        body = self.reader().object(rec["sha256"])
        self.assertEqual(body, C.canonical_bytes(rec["receipt"]))          # stored, content-addressed, canonical
        r = rec["receipt"]
        self.assertEqual((r["chain_id"], r["head"]["state"], len(r["lineage"])), ("Q1", "COMPLETE", 3))
        self.assertTrue(all(e["validation"] == "VALIDATED" for e in r["lineage"]))
        self.assertTrue(all(e["fabric_task_id"] and e["fabric_attempt_id"] and e["host"] == "hostA"
                            for e in r["lineage"]))

    def test_dispatch_is_idempotent_per_head(self):
        a = self.co.dispatch("Q1")
        b = self.co.dispatch("Q1")
        self.assertEqual([t["task_id"] for t in a], [t["task_id"] for t in b])
        self.assertEqual([t["created"] for t in b], [False])

    def test_publish_ready_classifies_each_attempt_once(self):
        self.step()
        self.assertEqual(self.co.publish_ready(), [])

    def test_accounting_lives_outside_the_trace(self):
        res = self.step()
        a = self.reader().attempt(res["attempt_id"])
        acct = a["detail"]["fabric"]
        self.assertEqual((acct["task_id"], acct["host"], acct["base_sha"]), (res["task_id"], "hostA", APPROVED))
        files = self.reader().epoch_files("Q1", 1)
        for needle in (res["task_id"], res["attempt_id"], "hostA"):
            for blob in files.values():
                self.assertNotIn(needle.encode(), blob)

    def test_a_failed_execution_is_left_to_fabric_and_retried(self):
        self.co.dispatch("Q1")
        self.assertEqual(self.worker("hostA", fail=True).run_one()["exit_code"], 3)
        self.assertEqual(self.co.publish_ready(), [])                      # nothing to classify
        self.assertIsNotNone(self.worker("hostB").run_one())               # Fabric's retry, another host
        out = self.co.publish_ready()
        self.assertEqual([(o["outcome"], o["host"]) for o in out], [("PUBLISHED", "hostB")])

    def test_dispatch_refuses_a_halted_or_complete_chain(self):
        for _ in range(3):
            self.step()
        with self.assertRaises(self.K.CoordinatorError):
            self.co.dispatch("Q1")


class TestRaces(CoordCase):
    def test_identical_racers_one_published_one_duplicate(self):
        self.co.dispatch("Q1", replicas=2, hosts=["hostA", "hostB"])
        self.worker("hostA").run_one()
        self.worker("hostB").run_one()
        out = self.co.publish_ready(parallel=2)
        self.assertEqual(sorted(o["outcome"] for o in out), ["DUPLICATE", "PUBLISHED"])
        self.assertEqual(len(self.reader().lineage("Q1")), 1)

    def test_conflicting_racers_contest_and_resolution_by_replay(self):
        self.fault("hostB", epochs=[1], mode="flip_checkpoint")         # hostB is the faulty host
        self.co.dispatch("Q1", replicas=2, hosts=["hostA", "hostB"])
        self.worker("hostA").run_one()
        self.worker("hostB").run_one()
        out = self.co.publish_ready(parallel=2)
        self.assertEqual(sorted(o["outcome"] for o in out), ["DISAGREEMENT", "PUBLISHED"])
        self.assertEqual(self.reader().head("Q1")["state"], "HALTED")
        honest_won = self.reader().lineage("Q1")[0]["epoch_digest"] == model.replay_chain(self.g, 1)[0].epoch_digest
        verdict = self.co.resolve("Q1")
        self.assertEqual(verdict, "UPHELD" if honest_won else "OVERTURNED")
        self.assertEqual(self.reader().head("Q1")["state"], "OPEN")


class TestRefusals(CoordCase):
    def test_bytes_that_disagree_with_their_manifest_are_invalid(self):
        self.fault("hostA", epochs=[1], mode="corrupt_trace")
        self.co.dispatch("Q1")
        self.worker("hostA").run_one()
        self.assertEqual([o["outcome"] for o in self.co.publish_ready()], ["INVALID"])
        self.assertEqual(self.reader().head("Q1")["head_index"], 0)

    def test_unapproved_code_is_refused(self):
        self.co.dispatch("Q1", base_sha=OTHER_SHA)       # a task pinned to code the chain did not approve
        self.worker("hostA").run_one()
        out = self.co.publish_ready()
        self.assertEqual([o["outcome"] for o in out], ["REFUSED_UNAPPROVED"])
        self.assertIn("base_sha", self.reader().attempt(out[0]["attempt_id"])["detail"]["refused"])

    def test_another_module_is_refused_even_when_its_bytes_are_right(self):
        # provenance, not just bytes: a different module of the approved commit that emits a perfectly valid epoch
        t = self.co.dispatch("Q1")[0]
        task = self.S.get_task(self.fab, t["task_id"])
        params = dict(task["params"], module="moonshot.nf.tests.fake_exec")
        self.S.cancel(self.fab, t["task_id"], "test")
        self.S.submit(self.fab, "Themis-test", "forged", "script", required_caps=CAPS[:2], base_sha=APPROVED,
                      params=params, idempotency_key="forged-module", metadata=task["metadata"],
                      campaign_id="C-012-test")
        self.assertEqual(self.worker("hostA").run_one()["exit_code"], 0)
        out = self.co.publish_ready()
        self.assertEqual([o["outcome"] for o in out], ["REFUSED_UNAPPROVED"])
        self.assertIn("module", self.reader().attempt(out[0]["attempt_id"])["detail"]["refused"])
        self.assertEqual(self.reader().head("Q1")["head_index"], 0)

    def test_a_test_namespace_task_cannot_publish_into_another_namespace(self):
        prod = genesis("P1")
        self.co.create_chain(prod, namespace="prod")
        t = self.co.dispatch("P1")[0]
        task = self.S.get_task(self.fab, t["task_id"])
        args = list(task["params"]["args"])
        args[args.index("--namespace") + 1] = "qual"                     # would let a node-local fault apply
        self.S.cancel(self.fab, t["task_id"], "test")
        self.S.submit(self.fab, "Themis-test", "forged", "script", required_caps=CAPS[:2], base_sha=APPROVED,
                      params=dict(task["params"], args=args), idempotency_key="forged-ns", metadata=task["metadata"],
                      campaign_id="C-012-test")
        self.worker("hostA").run_one()
        out = self.co.publish_ready()
        self.assertEqual([o["outcome"] for o in out], ["REFUSED_UNAPPROVED"])
        self.assertIn("namespace", self.reader().attempt(out[0]["attempt_id"])["detail"]["refused"])


class TestPublisherFaults(CoordCase):
    def test_a_publisher_process_killed_mid_transaction_leaves_the_attempt_unclassified(self):
        import time
        self.co.dispatch("Q1")
        aid = self.worker("hostA").run_one()["attempt_id"]
        env = dict(os.environ, PYTHONPATH=os.pathsep.join(p for p in (str(REPO), os.environ.get("PYTHONPATH")) if p))
        child = subprocess.Popen([sys.executable, "-m", "moonshot.nf.coordinator", "publish", "--schema", self.schema,
                                  "--principal", "Themis-test", "--campaign", "C-012-test",
                                  "--hold-before-commit-s", "8"], cwd=str(REPO), env=env,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        deadline = time.time() + 60
        while time.time() < deadline and not self.reader().publisher_waiting(self.schema):
            time.sleep(0.2)
        self.assertTrue(self.reader().publisher_waiting(self.schema), child.stderr.read1(2000) if child.poll() else "")
        child.kill()
        child.wait(30)
        time.sleep(1.0)
        self.assertIsNone(self.reader().attempt(aid))                      # the server rolled it back
        out = self.co.publish_ready()
        self.assertEqual([(o["attempt_id"], o["outcome"], o["replayed"]) for o in out], [(aid, "PUBLISHED", False)])

    def test_a_lost_acknowledgement_gets_the_recorded_answer(self):
        self.co.dispatch("Q1")
        self.worker("hostA").run_one()
        out = self.co.publish_ready(_lose_acks=1)
        self.assertEqual([(o["outcome"], o["replayed"]) for o in out], [("PUBLISHED", True)])
        self.assertEqual(self.reader().attempt_count("Q1"), 1)

    def test_the_publisher_cli_classifies_ready_attempts(self):
        self.co.dispatch("Q1")
        aid = self.worker("hostA").run_one()["attempt_id"]
        env = dict(os.environ, PYTHONPATH=os.pathsep.join(p for p in (str(REPO), os.environ.get("PYTHONPATH")) if p))
        r = subprocess.run([sys.executable, "-m", "moonshot.nf.coordinator", "publish", "--schema", self.schema,
                            "--principal", "Themis-test", "--campaign", "C-012-test"], cwd=str(REPO), env=env,
                           capture_output=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr.decode()[-800:])
        lines = [json.loads(x) for x in r.stdout.decode().splitlines() if x.strip()]
        self.assertEqual([(x["attempt_id"], x["outcome"]) for x in lines], [(aid, "PUBLISHED")])


class TestDefenceInDepth(CoordCase):
    def test_a_publication_that_slipped_past_verification_is_caught_and_overturned(self):
        # A publisher bug (verification skipped) lets a self-consistent forged identity in -- the database alone
        # cannot recompute canonical identities. Replay validation catches it (INVALID -> CORRUPT_BYTES), and the
        # resolver overturns it because the published bytes do not verify (mutation TM15 survived without this).
        r = model.execute(self.g.obj, 1, self.g.initial_checkpoint)
        forged = dict(r.files(), manifest=C.canonical_bytes(dict(r.manifest, epoch_digest="b" * 64)))
        res = self.co._h("publisher").publish("att-forged", "tsk-forged", "Q1", 1, None, 0, forged, verify=False)
        self.assertEqual(res["outcome"], "PUBLISHED")
        self.assertEqual(self.co.validate("Q1"), [(1, "INVALID")])
        c = self.reader().open_contest("Q1")
        self.assertEqual((c["reason"], c["state"]), ("CORRUPT_BYTES", "CONTESTED"))
        self.assertEqual(self.co.resolve("Q1"), "OVERTURNED")
        self.assertEqual(self.step()["outcome"], "PUBLISHED")              # the honest epoch, on the rewound chain
        self.assertEqual(self.reader().lineage("Q1")[0]["epoch_digest"], r.epoch_digest)


class TestStraggler(CoordCase):
    def test_work_from_an_overturned_lineage_is_stale(self):
        # a faulty host publishes epoch 1; epoch 2 is computed on it; replay validation catches epoch 1;
        # the resolver overturns; the late epoch-2 result from the rejected lineage is STALE
        self.fault("hostB", epochs=[1], mode="flip_checkpoint")
        self.co.dispatch("Q1")
        self.worker("hostB").run_one()
        self.assertEqual([o["outcome"] for o in self.co.publish_ready()], ["PUBLISHED"])
        self.co.dispatch("Q1")
        self.worker("hostA").run_one()                                     # epoch 2, not yet published
        self.assertEqual(self.co.validate("Q1", epochs=[1]), [(1, "MISMATCH")])
        self.assertEqual(self.reader().head("Q1")["state"], "HALTED")
        self.assertEqual(self.co.resolve("Q1"), "OVERTURNED")
        out = self.co.publish_ready()
        self.assertEqual([(o["epoch_index"], o["outcome"]) for o in out], [(2, "STALE")])
        for _ in range(3):                                                 # the honest chain completes
            self.step()
        self.assertEqual(self.reader().head("Q1")["state"], "COMPLETE")


if __name__ == "__main__":
    unittest.main()
