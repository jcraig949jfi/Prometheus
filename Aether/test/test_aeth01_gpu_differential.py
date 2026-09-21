"""
AETH-01 -- preregistered CPU (`oracle_aeth01.py`) vs GPU-shaped
(`gpu_aeth01.py`) differential test corpus.

Preregistered categories (fixed BEFORE running, per GPU_RUNPOD.md
"Verify" tier and ADVERSARIAL_ANALYSIS.md #9's closure requirement):
(1) the 6 K1 hand-worked accounting cases, run on both implementations;
(2) all four seeded K3 fixtures, including distributed two-source
    construction and recursive activation of preconfigured machinery,
    with per-source/content/control/scaffold interventions and rescues;
(3) explicit H,W in {1,2} toroidal self-aliasing dimension cases;
(4) >=500 randomized small worlds (Hypothesis), single tick;
(5) multi-tick trajectories (5 chained steps) on randomized worlds,
    comparing state at EVERY intermediate tick, not just the final one.

A mismatch anywhere means the GPU-SHAPED implementation disagrees with
the CPU oracle; per REQUIREMENTS.md R12, this gate must pass before any
GPU trajectory is used for a scientific claim. This is a local,
GPU-hardware-free run of the "GPU" side (no CuPy/GPU available in this
workspace); it verifies the ALGORITHM the RunPod canary would port, not
actual GPU execution.
"""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from reference import oracle_aeth01 as ok1
from reference.gpu_aeth01 import gpu_step
from reference.scientific_aeth01 import k3_intervention_cases

MAX_DIM = 4


def _to_arrays(grid, H, W):
    arr = np.array(grid, dtype=np.uint8)  # shape (H, W, 5)
    return [arr[:, :, f] for f in range(5)]


def _from_arrays(arrays, H, W):
    stacked = np.stack(arrays, axis=-1)
    return [[tuple(int(v) for v in stacked[r, c]) for c in range(W)] for r in range(H)]


def _gpu_step_on_grid(world):
    opcode, arg0, arg1, payload, energy = _to_arrays(world.grid, world.H, world.W)
    no_, na0, na1, npl, ne, counters = gpu_step(
        world.H, world.W, world.seed, world.tick, world.write_cost,
        world.maintenance_cost, world.replenish_numer, world.replenish_amount,
        world.mut_numer, opcode, arg0, arg1, payload, energy,
    )
    return _from_arrays([no_, na0, na1, npl, ne], world.H, world.W), counters


def _assert_cpu_gpu_agree(world, msg=""):
    trace = []
    cpu_next = world.step(trace=trace)
    gpu_grid, counters = _gpu_step_on_grid(world)
    assert gpu_grid == cpu_next.grid, f"CPU/GPU mismatch {msg}: cpu={cpu_next.grid} gpu={gpu_grid}"
    emitted = sum(event[0] == "proposal_emitted" for event in trace)
    assert counters["activity_density"] == emitted / (world.H * world.W), msg
    assert counters["total_energy"] == sum(cell[ok1.ENERGY] for row in cpu_next.grid for cell in row), msg
    return cpu_next


def _world(H, W, seed, write_cost=0, maintenance_cost=0, replenish_numer=0,
           replenish_amount=0, mut_numer=0, tick=0, grid=None):
    return ok1.Aeth01World(H, W, seed, write_cost, maintenance_cost,
                            replenish_numer, replenish_amount, mut_numer,
                            tick=tick, grid=grid)


# --- (1) K1 hand-worked cases -----------------------------------------

def test_gpu_matches_cpu_k1_cases():
    cases = [
        _world(1, 2, seed=1, write_cost=5, grid=[[(1, 1, 0, 7, 100), (0, 0, 0, 0, 0)]]),
        _world(1, 3, seed=5, write_cost=5, grid=[[(1, 1, 4, 30, 50), (0, 0, 0, 0, 0), (1, 3, 4, 40, 80)]]),
        _world(1, 2, seed=7, write_cost=2, grid=[[(1, 1, 4, 250, 200), (0, 0, 0, 0, 100)]]),
        _world(1, 1, seed=2, write_cost=3, grid=[[(1, 0, 4, 100, 50)]]),
        _world(1, 1, seed=3, maintenance_cost=5, grid=[[(0, 0, 0, 0, 2)]]),
        _world(1, 1, seed=4, replenish_numer=2**32, replenish_amount=20, grid=[[(0, 0, 0, 0, 250)]]),
    ]
    for i, w in enumerate(cases):
        _assert_cpu_gpu_agree(w, msg=f"K1 case {i+1}")


# --- (2) Shared K3 input corpus; independent transition implementations --

@pytest.mark.parametrize("name,world", tuple(k3_intervention_cases()))
def test_gpu_matches_cpu_k3_interventions(name, world):
    for tick in range(4):
        world = _assert_cpu_gpu_agree(world, msg=f"K3 {name} tick={tick}")


@pytest.mark.parametrize("energy,write_cost,maintenance_cost,pulses", [
    (0, 3, 2, 0), (2, 3, 2, 0), (3, 3, 2, 1), (4, 3, 2, 1),
    (20, 3, 2, 4), (22, 3, 2, 4), (23, 3, 2, 5), (24, 3, 2, 5),
    (7, 3, 0, 2), (255, 255, 255, 1), (255, 1, 255, 1),
    (0, 0, 0, 8), (0, 0, 2, 8), (5, 0, 2, 8), (255, 0, 255, 8),
])
def test_gpu_matches_cpu_pulse_budget_boundary(energy, write_cost, maintenance_cost, pulses):
    world = _world(1, 2, seed=41, write_cost=write_cost, maintenance_cost=maintenance_cost,
                   grid=[[(1, 1, 3, 7, energy), (0, 0, 0, 0, 0)]])
    observed = 0
    for tick in range(8):
        # Cross-checked against GPU activity_density inside the step helper,
        # even when a final same-value write leaves no visible template delta.
        trace = []
        world.step(trace=trace)
        observed += sum(event[0] == "proposal_emitted" for event in trace)
        world = _assert_cpu_gpu_agree(world, msg=f"pulse boundary tick={tick}")
    assert observed == pulses


# --- (3) explicit H,W in {1,2} self-aliasing dimensions -----------------

def test_gpu_matches_cpu_small_torus_self_aliasing_dimensions():
    for H, W in [(1, 1), (1, 2), (2, 1), (2, 2)]:
        grid = [
            [(1, r * W + c, (r + c) % 5, (r * 7 + c * 3) % 256, 80) for c in range(W)]
            for r in range(H)
        ]
        w = _world(H, W, seed=99, write_cost=4, maintenance_cost=1,
                    replenish_numer=1 << 20, replenish_amount=10, mut_numer=1 << 20,
                    grid=grid)
        _assert_cpu_gpu_agree(w, msg=f"dims H={H} W={W}")


# --- (4)/(5) randomized worlds, single-tick and multi-tick trajectories -

_cell_strategy = st.one_of(
    st.tuples(st.just(ok1.WRITE_OPCODE), st.integers(0, 255), st.integers(0, 255),
              st.integers(0, 255), st.integers(0, 255)),
    st.tuples(st.integers(0, 255).filter(lambda o: o != ok1.WRITE_OPCODE),
              st.integers(0, 4), st.integers(0, 4), st.integers(0, 4), st.integers(0, 255)),
)


@st.composite
def worlds(draw, max_dim=MAX_DIM):
    H = draw(st.integers(min_value=1, max_value=max_dim))
    W = draw(st.integers(min_value=1, max_value=max_dim))
    seed = draw(st.integers(min_value=0, max_value=(1 << 64) - 1))
    tick = draw(st.integers(min_value=0, max_value=(1 << 64) - 6))
    write_cost = draw(st.integers(min_value=0, max_value=255))
    maintenance_cost = draw(st.integers(min_value=0, max_value=255))
    replenish_numer = draw(st.sampled_from([0, 1, 1 << 16, 1 << 31, 1 << 32]))
    replenish_amount = draw(st.integers(min_value=0, max_value=255))
    mut_numer = draw(st.sampled_from([0, 1, 1 << 16, 1 << 31, 1 << 32]))
    grid = draw(st.lists(st.lists(_cell_strategy, min_size=W, max_size=W), min_size=H, max_size=H))
    return _world(H, W, seed, write_cost, maintenance_cost, replenish_numer,
                  replenish_amount, mut_numer, tick=tick, grid=grid)


@settings(max_examples=500, deadline=None)
@given(world=worlds())
def test_gpu_matches_cpu_randomized_single_tick(world):
    _assert_cpu_gpu_agree(world)


@settings(max_examples=100, deadline=None)
@given(world=worlds())
def test_gpu_matches_cpu_randomized_multi_tick_trajectory(world):
    w = world
    for t in range(5):
        w = _assert_cpu_gpu_agree(w, msg=f"trajectory tick {t}")
