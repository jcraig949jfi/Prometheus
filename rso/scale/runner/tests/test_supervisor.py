"""Out of process: worker subprocesses under a supervisor, a worker killed mid-epoch (C-013-T022)."""
import os
import subprocess
import sys
import time
import unittest

from rso.scale.runner import account as A
from rso.scale.runner import control as CTL
from rso.scale.runner import run as RUN
from rso.scale.runner import supervisor as SUP
from rso.scale.runner.tests._util import TempRun, toy_params

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


class TestSupervisor(unittest.TestCase):
    def setUp(self):
        # a few hundred ms per epoch on one core, so a kill can land mid-epoch
        self.t = TempRun(params=toy_params(ticks_per_epoch=40, trace_every=5, work_per_tick=6000), partitions=2,
                         epochs=3)
        self.rd = self.t.run_dir

    def tearDown(self):
        self.t.cleanup()

    def test_worker_killed_mid_epoch_supervisor_recovers(self):
        c = RUN.chain_ids(RUN.load_manifest(self.rd)[0])[0]
        p = subprocess.Popen([sys.executable, "-m", "rso.scale.runner", "work", self.rd, c], cwd=REPO,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.time() + 60
        while time.time() < deadline:
            prog = RUN.latest_progress(self.rd, c)
            if prog and prog["epoch_index"] >= 2 and 0 < prog["ticks_done"] < 40:
                break
            time.sleep(0.01)
        else:
            p.kill()
            self.fail("worker never reached mid-epoch 2")
        p.kill()                                                    # TerminateProcess / SIGKILL: no cleanup runs
        p.wait(30)
        st = SUP.supervise(self.rd, poll_s=0.05)
        self.assertEqual(st["state"], "COMPLETE", st)
        acct = A.final_account(self.rd)
        self.assertEqual(acct["run_digest"], CTL.control(self.rd)["run_digest"])
        self.assertEqual(acct["wasted"]["interrupted_attempts"], 1)
        self.assertGreater(acct["wasted"]["ticks_lower_bound"], 0)
        self.assertTrue(os.path.exists(os.path.join(self.rd, "FINAL_ACCOUNT.json")))

    def test_single_supervisor(self):
        lock = SUP.acquire_supervisor(self.rd)
        self.assertIsNotNone(lock)
        self.assertIsNone(SUP.acquire_supervisor(self.rd))         # a second live supervisor is refused
        SUP.release_supervisor(self.rd, lock)
        self.assertIsNotNone(SUP.acquire_supervisor(self.rd))


if __name__ == "__main__":
    unittest.main()
