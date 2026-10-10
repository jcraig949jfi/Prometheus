"""Idempotent host-relaunch entry and the simulated scheduler (C-013-T025; roadmap P-3).

No OS scheduler task is installed anywhere: the timer here is rso.scale.runner.sched_sim, a harness that invokes the
entry (as a subprocess, the way Task Scheduler / systemd would) every interval_s seconds."""
import os
import sys
import threading
import time
import unittest

from rso.scale.runner import account as A
from rso.scale.runner import control as CTL
from rso.scale.runner import relaunch as RL
from rso.scale.runner import run as RUN
from rso.scale.runner import sched_sim as SIM
from rso.scale.runner import store as S
from rso.scale.runner import supervisor as SUP
from rso.scale.runner import worker as W
from rso.scale.runner.tests._util import TempRun, toy_params

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


class Spawn:
    """Stands in for launch_detached: records the call and plays a supervisor that is live afterwards."""

    def __init__(self, run_dir, delay=0.0):
        self.run_dir, self.calls, self.delay = run_dir, 0, delay

    def __call__(self, run_dir, code_root):
        self.calls += 1
        time.sleep(self.delay)
        tok = SUP.acquire_supervisor(self.run_dir)
        return {"supervisor_pid": os.getpid(), "token": tok}


class TestDecision(unittest.TestCase):
    def setUp(self):
        self.t = TempRun(epochs=2, partitions=2)
        self.rd = self.t.run_dir
        self.chains = RUN.chain_ids(self.t.manifest)

    def tearDown(self):
        self.t.cleanup()

    def test_incomplete_and_nothing_running_launches_once(self):
        sp = Spawn(self.rd)
        r = RL.relaunch(self.rd, spawn=sp)
        self.assertEqual((r["action"], sp.calls), ("LAUNCHED", 1))
        r = RL.relaunch(self.rd, spawn=sp)                          # the supervisor is live now: fire again, noop
        self.assertEqual((r["action"], sp.calls), ("RUNNING", 1))

    def test_complete_run_is_a_noop(self):
        for c in self.chains:
            W.work(self.rd, c)
        sp = Spawn(self.rd)
        self.assertEqual(RL.relaunch(self.rd, spawn=sp)["action"], "COMPLETE")
        self.assertEqual(sp.calls, 0)

    def test_halted_chain_is_not_relaunched(self):
        RUN.halt(self.rd, self.chains[0], {"kind": "DISAGREEMENT", "epoch_index": 1})
        sp = Spawn(self.rd)
        r = RL.relaunch(self.rd, spawn=sp)
        self.assertEqual((r["action"], sp.calls), ("HALTED", 0))
        self.assertEqual(RL.EXIT["HALTED"], 4)

    def test_blocked_supervisor_is_not_relaunched_until_an_explicit_launch(self):
        SUP.sup_event(self.rd, {"kind": "SUPERVISOR_START"})
        SUP.sup_event(self.rd, {"kind": "SUPERVISOR_END", "state": "BLOCKED", "reason": "resume INVALID"})
        sp = Spawn(self.rd)
        self.assertEqual(RL.relaunch(self.rd, spawn=sp)["action"], "BLOCKED")
        self.assertEqual(sp.calls, 0)
        SUP.sup_event(self.rd, {"kind": "SUPERVISOR_START"})        # an operator's explicit launch re-arms the run
        self.assertEqual(RL.relaunch(self.rd, spawn=sp)["action"], "LAUNCHED")

    def test_dead_supervisor_record_is_replaced(self):
        tok = SUP.acquire_supervisor(self.rd)
        cur = S.read_json(SUP._path(self.rd))
        cur["pid"], cur["create_time"] = 2 ** 31 - 3, 0.0           # a killed supervisor's record
        S.atomic_write_json(SUP._path(self.rd), cur)
        sp = Spawn(self.rd)
        self.assertEqual(RL.relaunch(self.rd, spawn=sp)["action"], "LAUNCHED")
        self.assertEqual(sp.calls, 1)

    def test_concurrent_fires_spawn_one_supervisor(self):
        sp = Spawn(self.rd, delay=0.3)
        out, errs = [], []

        def fire():
            try:
                out.append(RL.relaunch(self.rd, spawn=sp)["action"])
            except Exception as e:                                  # surfaced below, not lost in the thread
                errs.append(repr(e))
        ths = [threading.Thread(target=fire) for _ in range(4)]
        [t.start() for t in ths]
        [t.join(60) for t in ths]
        self.assertEqual(errs, [])
        self.assertEqual(sp.calls, 1)
        self.assertEqual(sorted(out), ["LAUNCHED", "RUNNING", "RUNNING", "RUNNING"])

    def test_every_fire_is_logged(self):
        sp = Spawn(self.rd)
        RL.relaunch(self.rd, spawn=sp)
        RL.relaunch(self.rd, spawn=sp)
        rows, _ = S.read_jsonl(os.path.join(SUP.sdir(self.rd), "relaunch.jsonl"))
        self.assertEqual([r["action"] for r in rows], ["LAUNCHED", "RUNNING"])

    def test_refuses_the_canonical_checkout(self):
        with self.assertRaises(SystemExit):
            RL.relaunch(self.rd, code_root="C:/Prometheus", spawn=Spawn(self.rd))


class TestSimulatedSchedulerFire(unittest.TestCase):
    """Kill everything, no session acts, the simulated scheduler fires, the job resumes, digest == control."""

    def setUp(self):
        self.t = TempRun(params=toy_params(ticks_per_epoch=40, trace_every=5, work_per_tick=6000), partitions=2,
                         epochs=3)
        self.rd = self.t.run_dir

    def tearDown(self):
        self.t.cleanup()

    def test_kill_everything_then_scheduler_resumes_the_job(self):
        result = SIM.fire_test(self.rd, code_root=REPO, interval_s=2.0, timeout_s=420)
        self.assertEqual(result["failed"], [], result)
        acct = A.final_account(self.rd)
        self.assertEqual(acct["state"], "COMPLETE")
        self.assertEqual(acct["run_digest"], CTL.control(self.rd)["run_digest"])
        self.assertGreaterEqual(acct["wasted"]["interrupted_attempts"], 1)


if __name__ == "__main__":
    unittest.main()
