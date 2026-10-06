"""D5: node auto-join without auto-authorization (CONTRACT s8; design v0.3 N3/N7; C-008-T005). Written RED.

A temporary code repository stands in for the Prometheus checkout: commit APPROVED is on the approval ref
("main"), commit SIDE is not. A node joins only from a clean checkout of approved code; joining announces
liveness and drains chains as WORKER-role workers; it can never create, validate, resolve or approve."""
import os
import subprocess
import unittest

from moonshot.epoch import join as J
from moonshot.epoch import model, runtime
from moonshot.epoch import store as S
from moonshot.epoch import validate as V
from moonshot.epoch.tests.harness import Harness


def _git(cwd, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    return subprocess.run(["git"] + list(args), cwd=cwd, env=env, check=True, capture_output=True,
                          timeout=60).stdout.decode().strip()


class TestD5Join(unittest.TestCase):
    def setUp(self):
        self.h = Harness(S.PER_CHAIN)
        self.addCleanup(self.h.cleanup)
        code = os.path.join(self.h.dir, "code")
        os.makedirs(code)
        _git(code, "init", "-q", "-b", "main")
        with open(os.path.join(code, "VERSION"), "w") as f:
            f.write("approved\n")
        _git(code, "add", "VERSION")
        _git(code, "commit", "-q", "-m", "approved code")
        self.approved = _git(code, "rev-parse", "HEAD")
        _git(code, "checkout", "-q", "-b", "side")
        with open(os.path.join(code, "VERSION"), "w") as f:
            f.write("side\n")
        _git(code, "commit", "-q", "-am", "unapproved code")
        self.side = _git(code, "rev-parse", "HEAD")
        _git(code, "checkout", "-q", "--detach", self.approved)
        self.code = code

    def chain(self, cid, approved=None, epochs=2):
        g = model.make_genesis(cid, epochs=epochs, params={"work_iterations": 50, "trace_every": 10,
                                                           "checkpoint_bytes": 64},
                               approved_code_sha=approved or self.approved, initial_checkpoint=cid.encode())
        self.h.coordinator.create_chain(g)
        return g

    def join(self, remote=None, **kw):
        args = dict(namespace=self.h.ns, layout=S.PER_CHAIN, code_dir=self.code, approval_ref="main",
                    node_id="node-a", workers=2, duration_s=30, data_dir=os.path.join(self.h.dir, "node-a"))
        args.update(kw)
        return J.join(remote or self.h.remote, **args)

    def test_join_drains_every_approved_chain(self):
        g1, g2 = self.chain("J1"), self.chain("J2")
        out = self.join()
        self.assertEqual(out["code_sha"], self.approved)
        for g in (g1, g2):
            self.assertEqual(self.h.coordinator.chain_view(g.chain_id).head_index, 2)
            self.assertEqual([e.epoch_digest for e in self.h.coordinator.lineage(g.chain_id)],
                             [r.epoch_digest for r in model.replay_chain(g, 2)])
        nodes = self.h.coordinator.nodes()
        self.assertEqual(nodes["node-a"]["code_sha"], self.approved)

    def test_dirty_checkout_is_refused(self):
        self.chain("J1")
        with open(os.path.join(self.code, "VERSION"), "w") as f:
            f.write("edited locally\n")
        with self.assertRaises(J.JoinRefused):
            self.join()
        self.assertEqual(self.h.coordinator.chain_view("J1").head_index, 0)
        self.assertEqual(self.h.coordinator.nodes(), {})

    def test_unapproved_node_code_is_refused(self):
        self.chain("J1")
        _git(self.code, "checkout", "-q", "--detach", self.side)
        with self.assertRaises(J.JoinRefused):
            self.join()
        self.assertEqual(self.h.coordinator.chain_view("J1").head_index, 0)
        self.assertEqual(self.h.coordinator.nodes(), {})

    def test_joined_node_refuses_a_chain_naming_unapproved_code(self):
        self.chain("Jok")
        self.chain("Jbad", approved=self.side)
        self.join()
        self.assertEqual(self.h.coordinator.chain_view("Jok").head_index, 2)
        self.assertEqual(self.h.coordinator.chain_view("Jbad").head_index, 0)
        refused = [r for r in self.h.coordinator.read_receipts()
                   if r.get("chain_id") == "Jbad" and r.get("outcome") == "REFUSED_UNAPPROVED"]
        self.assertTrue(refused)

    def test_ancestry_oracle(self):
        oracle = J.AncestryOracle(self.code, "main")
        self.assertTrue(oracle(self.approved))
        self.assertFalse(oracle(self.side))
        self.assertFalse(oracle("f" * 40))                       # unknown object: never approved
        self.assertFalse(oracle("not-a-sha"))

    def test_join_grants_no_authority(self):
        self.chain("J1", epochs=1)
        st = J.node_store(self.h.remote, namespace=self.h.ns, layout=S.PER_CHAIN,
                          local_dir=os.path.join(self.h.dir, "authority-probe"), node_id="node-a")
        self.assertEqual(st.role, S.WORKER)
        with self.assertRaises(PermissionError):
            st.create_chain(model.make_genesis("Z", epochs=1, params={"work_iterations": 1, "trace_every": 1,
                                                                      "checkpoint_bytes": 1},
                                               approved_code_sha=self.approved, initial_checkpoint=b"z"))
        with self.assertRaises(PermissionError):
            V.validate_chain(st, "J1")
        with self.assertRaises(PermissionError):
            V.resolve(st, "J1", runners=[runtime.run_synthetic_v1])
        before = {s: self.h.coordinator.read_slots([s])[s] for s in ("chains/J1", "contest/J1", "validation/J1")}
        st.announce_node("node-a", {"note": "liveness only"})
        after = {s: self.h.coordinator.read_slots([s])[s] for s in before}
        self.assertEqual(before, after)                          # an announcement changes no chain state
        st.close()

    def test_running_code_must_be_the_approved_checkout(self):
        # Added during implementation: approving --code-dir says nothing if the interpreter imported moonshot
        # from somewhere else. The CLI path binds them (bind_running_code=True).
        from moonshot.epoch.tests.harness import REPO_ROOT
        self.assertFalse(J.running_code_inside(self.code))
        self.assertTrue(J.running_code_inside(REPO_ROOT))
        self.chain("J1")
        with self.assertRaises(J.JoinRefused):
            self.join(bind_running_code=True)
        self.assertEqual(self.h.coordinator.nodes(), {})

    def test_denylisted_remote_is_refused_before_anything(self):
        with self.assertRaises(S.ForbiddenRemote):
            self.join(remote="https://github.com/jcraig949jfi/Prometheus.git")
        self.assertFalse(os.path.exists(os.path.join(self.h.dir, "node-a")))


if __name__ == "__main__":
    unittest.main()
