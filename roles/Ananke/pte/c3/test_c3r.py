"""Representation-v2 known-answer tests (CPU). Run: python -m pytest roles/Ananke/pte/c3/test_c3r.py -q -p no:cacheprovider"""
import dataclasses
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

import c3r_common as R  # noqa: E402
C = R.C; B = R.B
from prometheus.ananke import envs, search  # noqa: E402
from prometheus.ananke.search import HELD_NS  # noqa: E402

PH = C.Physics.from_dict(dict(C.Physics().to_dict(), prog_len=16, rules=1, state_dim=2, payload_width=1,
                              channels=1, decay_shift=0)).validate()
ENV = envs.EnvSpec(family="FLIP", d=1, delta=4, trials=8, block=4)
SP = search.SearchSpec(pop=12, M=2, gens=4, M_final=2, elite=2)


def test_r0_loop_equals_c2b_ga():
    import run_c2b
    hs = C.assays.world_seeds(C.H_int(7, HELD_NS), 8)
    a = run_c2b.evolve_c2b(PH, ENV, 4242, SP, "cpu", ckpts=(), held=hs, role="FLIP")
    b = R.evolve_staged(R.rep_physics(PH, "R0"), ENV, 4242, SP, "cpu", "R0", gens_to=SP.gens - 1)
    # c2b returns the population evaluated at the last generation (produced after gen gens-2)
    assert np.array_equal(a["pop"], b["pop"])


def test_continuation_equals_straight_run():
    ph = R.rep_physics(PH, "R4")
    s1 = R.evolve_staged(ph, ENV, 99, SP, "cpu", "R4", gens_to=2)
    s2 = R.evolve_staged(ph, ENV, 99, SP, "cpu", "R4", gens_to=5, state=s1)
    d = R.evolve_staged(ph, ENV, 99, SP, "cpu", "R4", gens_to=5)
    assert np.array_equal(s2["pop"], d["pop"]) and np.array_equal(s2["dup"], d["dup"])


def test_free_lines_are_nop_at_init():
    ph = R.rep_physics(PH, "R1")
    pop = R.init_population(np.random.default_rng(1), 20, ph, 8)
    assert (pop[:, :, 16:, 0] == 0).all() and (pop[:, :, :16, 0] != 0).any()


def test_duplicate_into_free_capacity_and_marks():
    ph = R.rep_physics(PH, "R3")
    g0 = R.init_population(np.random.default_rng(2), 1, ph, 8)[0]
    t = np.ones(g0.shape[:2], bool); d = np.zeros(g0.shape[:2], bool)
    for s in range(50):
        c, tt, dd, (r, b, src, pos, had_free) = R.duplicate(np.random.default_rng(s), g0, t, d)
        assert had_free and (g0[r, pos:pos + b, 0] % 16 == 0).all()     # destination was entirely free (NOP)
        assert np.array_equal(c[r, pos:pos + b], g0[r, src:src + b]) and dd[r, pos:pos + b].all()
        assert dd.sum() == b


def test_plant_reencodes_for_every_rep():
    for rep in R.REPS:
        ph = R.rep_physics(PH, rep)
        g = R.rep_plant(ph)
        assert g.shape[1] == R.REPS[rep]["prog_len"]
        assert ((g[..., 4] >= -128) & (g[..., 4] <= 127)).all()
        if R.REPS[rep]["free_lines"]:
            assert (g[:, 16:, 0] == 0).all()


def test_golden_v1_unchanged():
    import subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    r = subprocess.run([sys.executable, os.path.join(here, "golden.py"), "check", os.path.join(here, "golden_v1.json")],
                       capture_output=True, text=True, cwd=here)
    assert r.returncode == 0, r.stdout[-500:]
