"""The hooked runner equals the unmodified CPU oracle, and the oracle lines it copies are pinned."""
import hashlib
import os
import unittest

import numpy as np

from prometheus.ananke import oracle
from rso.gen5.ananke.eval import evaluate as E
from rso.gen5.ananke.eval import owner, runner, worlds

ROOT = owner.ROOT
RUN_SHA256 = "a5c5be65a187b5b13af41a39b5bd8eb23851fde318551cc499c184ad6cd63774"   # oracle.py:277-511, LF


class RunnerPin(unittest.TestCase):
    def test_oracle_source_unchanged(self):
        lines = open(os.path.join(ROOT, runner.ORACLE_SOURCE), "rb").read().replace(b"\r\n", b"\n").split(b"\n")
        a, b = runner.ORACLE_RUN_LINES
        blob = b"\n".join(lines[a - 1:b]) + b"\n"
        self.assertEqual(hashlib.sha256(blob).hexdigest(), RUN_SHA256)

    def test_equals_oracle_without_hooks(self):
        cells, adm = owner.cells(), owner.admission()
        c = cells[0]
        ph = worlds.rep_physics(c["physics"], "R4")
        env = worlds.task_env(c["env"], "GATE")
        seeds = E.own_seeds(0x7E57, c["cell_key"], 2)
        ep = worlds.build(ph, env, seeds)
        g = np.asarray(adm[f"{c['cell_id']}|GATE"]["plant_genome"])
        a = oracle.run(ph, [g, g], seeds, ep.sense(), env.T())
        b = runner.run(ph, [g, g], seeds, ep.sense(), env.T())
        for k in ("S", "E", "r", "w", "Kp", "Acc_sum", "Acc_cnt", "Msum", "Mcnt", "S0_trace"):
            self.assertTrue(np.array_equal(a[k], b[k]), k)
        self.assertEqual(a["stats"], b["stats"])
        self.assertGreater(sum(a["stats"]["delivered"]), 0)          # the plant actually communicates here

    def test_hook_sees_every_tick_after_readout(self):
        cells, adm = owner.cells(), owner.admission()
        c = cells[0]
        ph = worlds.rep_physics(c["physics"], "R4")
        env = worlds.task_env(c["env"], "GATE")
        seeds = E.own_seeds(0x7E58, c["cell_key"], 2)
        ep = worlds.build(ph, env, seeds)
        g = np.asarray(adm[f"{c['cell_id']}|GATE"]["plant_genome"])
        calls = []
        r = runner.run(ph, [g, g], seeds, ep.sense(), env.T(), after_tick=lambda t, b, S: calls.append((t, b)))
        self.assertEqual(len(calls), 2 * env.T())
        z = runner.run(ph, [g, g], seeds, ep.sense(), env.T(), zero_comm=True)
        self.assertEqual(sum(z["stats"]["delivered"]), 0)
        self.assertTrue(np.array_equal(r["S0_trace"], oracle.run(ph, [g, g], seeds, ep.sense(), env.T())["S0_trace"]))


if __name__ == "__main__":
    unittest.main()
