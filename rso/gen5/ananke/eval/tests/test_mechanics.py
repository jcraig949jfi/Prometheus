"""Rung-4 attribution mechanics: genome-level contracts (fast) and small oracle fire tests. Written before
mechanics.py. Full-size plant outcomes are in MECHANICS_KA.json (mechanics_run.py)."""
import unittest

import numpy as np

from rso.gen5.ananke.eval import evaluate as E
from rso.gen5.ananke.eval import mechanics as K
from rso.gen5.ananke.eval import owner, worlds

CELLS = owner.cells()
ADM = owner.admission()
C0 = CELLS[0]
PH = worlds.rep_physics(C0["physics"], "R4")
GATE = np.asarray(ADM[f"{C0['cell_id']}|GATE"]["plant_genome"], dtype=np.int64)
CTX, CUE = [11, 12, 13], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14]
L = E.register_layout(PH)


class GenomeContracts(unittest.TestCase):
    def test_lines_nop(self):
        g = K.lines_nop(GATE, CTX)
        self.assertTrue((g[:, CTX] == 0).all())
        self.assertTrue(np.array_equal(np.delete(g, CTX, 1), np.delete(GATE, CTX, 1)))
        self.assertTrue(np.array_equal(GATE, np.asarray(ADM[f"{C0['cell_id']}|GATE"]["plant_genome"])))  # no aliasing

    def test_use_disabled_keeps_bytes_but_dst(self):
        g, rep = K.use_disabled(GATE, CTX, PH)
        for i in CTX:
            self.assertEqual(int(g[0, i, 1]) % L["NW"], L["CHAN"])
            self.assertTrue(np.array_equal(g[0, i, [0, 2, 3, 4]], GATE[0, i, [0, 2, 3, 4]]))   # op, a, b, imm kept
            self.assertEqual(int(g[0, i, 1]) - int(g[0, i, 1]) % L["NW"],
                             int(GATE[0, i, 1]) - int(GATE[0, i, 1]) % L["NW"])               # raw high part kept
        others = [i for i in range(GATE.shape[1]) if i not in CTX]
        self.assertTrue(np.array_equal(g[:, others], GATE[:, others]))
        self.assertEqual(rep["bytes_changed"], sum(int(GATE[0, i, 1]) % L["NW"] != L["CHAN"] for i in CTX))
        self.assertEqual(rep["lines_executed_nonnop"], 3)

    def test_use_disabled_refuses_when_sink_is_read(self):
        g = GATE.copy()
        g[0, 20] = [1, 3, L["CHAN"], 0, 0]           # MOV T0 <- CHAN outside the module: the sink is not dead
        with self.assertRaises(K.UnsupportedIntervention):
            K.use_disabled(g, CTX, PH)
        ph2 = dict(PH, channels=2)
        with self.assertRaises(K.UnsupportedIntervention):
            K.use_disabled(GATE, CTX, ph2)

    def test_rename_identity_and_involution(self):
        rows = GATE[0, :15]
        self.assertTrue(np.array_equal(K.rename_state(rows, PH, [0, 1, 2]), rows))
        p = [0, 2, 1]
        self.assertTrue(np.array_equal(K.rename_state(K.rename_state(rows, PH, p), PH, p), rows))

    def test_transplant_places_and_renames(self):
        g = K.transplant(GATE[0, :15], PH, start=9)
        self.assertTrue(np.array_equal(g[0, 9:24], GATE[0, :15])); self.assertTrue((g[0, :9] == 0).all())
        with self.assertRaises(ValueError):
            K.transplant(GATE[0, :15], PH, start=10)

    def test_substitute_size_matched(self):
        donor = np.arange(15).reshape(3, 5)
        g = K.substitute(GATE, CTX, donor)
        self.assertTrue(np.array_equal(g[0, CTX], donor))
        with self.assertRaises(ValueError):
            K.substitute(GATE, CTX, donor[:2])

    def test_lesion_reads_zero(self):
        les = K.lesion_input(GATE[0, CTX], PH, L["SENSE"])
        self.assertFalse(np.any([(int(r[2]) % L["NR"] == L["SENSE"]) or (int(r[3]) % L["NR"] == L["SENSE"] and int(r[0]) % 16 in K.B_IS_REGISTER) for r in les]))


class OracleFireTests(unittest.TestCase):
    """Small-world (8 worlds) dynamics checks of the mechanics; outcome-level known answers are in the full run."""

    @classmethod
    def setUpClass(cls):
        cls.env = worlds.task_env(C0["env"], "GATE")
        cls.seeds = E.own_seeds(0xF17E, C0["cell_key"], 8)
        cls.pt, _ = E.eval_programs(PH, cls.env, cls.seeds, [GATE])

    def test_dead_line_use_disabled_is_identity(self):
        g = GATE.copy(); g[0, 20] = [2, L["T0"] + 1, L["T0"] + 1, L["T0"] + 1, 0]   # ADD T1 T1 T1 after the readout: dead
        gd, _ = K.use_disabled(g, [20], PH)
        pt, _ = E.eval_programs(PH, self.env, self.seeds, [g, gd])
        self.assertTrue(np.array_equal(pt[0], self.pt[0])); self.assertTrue(np.array_equal(pt[1], self.pt[0]))

    def test_transplant_offset_and_consistent_rename_identical(self):
        g9 = K.transplant(GATE[0, :15], PH, start=9)
        gr = K.transplant(K.rename_state(GATE[0, :15], PH, [0, 2, 1]), PH, start=0)
        pt, _ = E.eval_programs(PH, self.env, self.seeds, [g9, gr])
        self.assertTrue(np.array_equal(pt[0], self.pt[0])); self.assertTrue(np.array_equal(pt[1], self.pt[0]))

    def test_reg_zero_hook_after_readout(self):
        # zeroing S2 after every tick: the context latch never persists -> readout 0 on every trial whose readout tick
        # follows a tick without a context arrival; it must differ from the plant
        pt, _ = E.eval_programs(PH, self.env, self.seeds, [GATE], after_tick=K.reg_zero(2))
        self.assertFalse(np.array_equal(pt[0], self.pt[0]))

    def test_zero_comm_gives_exact_chance_pairs(self):
        pt, ep = E.eval_programs(PH, self.env, self.seeds, [GATE], zero_comm=True)
        pair = pt[0].reshape(-1, 2, pt.shape[2]).mean((1, 2))
        self.assertTrue(np.allclose(pair, 0.5))


if __name__ == "__main__":
    unittest.main()
