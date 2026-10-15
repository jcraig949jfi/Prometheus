"""End-to-end conformance to the owner's committed numbers (worlds + oracle + ruler), and the committed evidence.

One admission check is re-run live (~50 s): RELAY1H relay_flood at FLIP-0000 must reproduce admission_R4.json's
mean and lo99 to 1e-9. The full table (108 checks) is runs/ka/ + qual/KA_TABLE.json; its reduce must PASS."""
import json
import os
import unittest

import numpy as np

from rso.gen5.ananke.eval import evaluate as E
from rso.gen5.ananke.eval import ka_table as KT
from rso.gen5.ananke.eval import mechanics_run as MR
from rso.gen5.ananke.eval import owner, ruler, worlds

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Conformance(unittest.TestCase):
    def test_relay1h_admission_exact(self):
        cells, adm = owner.cells(), owner.admission()
        c = cells[0]
        rec = adm[f"{c['cell_id']}|RELAY1H"]["plant"]
        ph = worlds.rep_physics(c["physics"], "R4"); env = worlds.task_env(c["env"], "RELAY1H")
        pt, ep = E.eval_programs(ph, env, E.admission_seeds("RELAY1H", c["cell_key"]),
                                 [adm[f"{c['cell_id']}|RELAY1H"]["plant_genome"]])
        r = ruler.competence("RELAY-mh", pt[0], ep)
        for comp in ("all", "late"):
            for k in ("mean", "lo99"):
                self.assertAlmostEqual(r[comp][k], rec[comp][k], delta=1e-9)
        self.assertEqual(r["status"], rec["status"])


class CommittedEvidence(unittest.TestCase):
    def test_ka_rows_reduce_pass(self):
        d = os.path.join(HERE, "runs", "ka")
        if not os.path.isdir(d):
            self.skipTest("no committed KA rows")
        res = KT.reduce_rows(KT.load_rows(d), owner.cells(), owner.admission(), owner.library(), owner.dlib(), replay_k=0)
        self.assertEqual(res["problems"], [])
        self.assertEqual(res["rows"], res["planned"])

    def test_ka_table_json_matches_rows(self):
        p = os.path.join(HERE, "qual", "KA_TABLE.json")
        if not os.path.exists(p):
            self.skipTest("no KA_TABLE.json")
        t = json.load(open(p))
        self.assertEqual(t["verdict"], "PASS")
        rows = {r["check_id"]: r for r in KT.load_rows(os.path.join(HERE, "runs", "ka"))}
        for e in t["table"]:
            self.assertEqual(e["pt_sha"], rows[e["check_id"]]["pt_sha"])

    def test_mechanics_reduce_pass(self):
        d = os.path.join(HERE, "runs", "mech")
        if not os.path.isdir(d):
            self.skipTest("no committed mechanics rows")
        out = os.path.join(d, "_tmp_reduce.json")
        try:
            self.assertEqual(MR.reduce(d, out), 0)
        finally:
            if os.path.exists(out):
                os.remove(out)


if __name__ == "__main__":
    unittest.main()
