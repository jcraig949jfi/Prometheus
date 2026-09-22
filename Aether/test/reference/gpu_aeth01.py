"""
Aether AETH-01 (candidate semantics_id aeth01.v1) -- GPU-SHAPED CPU
implementation, exact-integer, no floating point anywhere.

This is the "gather" (per-target-site, no atomics, embarrassingly
parallel) shape GPU_RUNPOD.md and PHYSICS_CANDIDATES.md's R12
feasibility argument describe, following AETH-00's own
`Aether/production/aeth00.py` gather precedent, generalized to the
5-field / 7-phase repaired law. It uses NumPy's array API (vectorized
whole-grid operations, no per-site Python loop) because no GPU library
(CuPy/Numba-CUDA/PyTorch) is installed in this workspace and no GPU
hardware is available locally, and installing one is a dependency
decision requiring explicit sign-off (not taken here). NumPy's
element-wise/broadcast operations are the same SHAPE of computation a
CUDA kernel would perform per-thread (gather from up to 4 neighbors,
compute a value, write once, no shared mutable state) -- porting this
module to CuPy is intended to be a near-mechanical `import cupy as np`
substitution, not a redesign, BUT THIS HAS NOT BEEN DONE OR TESTED ON
REAL GPU HARDWARE; R12 remains open until it is (REQUIREMENTS.md).

Independence: does not import `oracle_aeth01.py`; every formula is
restated from `AETH01_REPAIRED_FREEZE_CANDIDATE.md` directly, so a
CPU/GPU-shape differential test (`test_aeth01_gpu_differential.py`) is
comparing two structurally different implementations of the same text,
not one importing the other.
"""

import numpy as np

MASK64 = np.uint64((1 << 64) - 1)
U64 = np.uint64

WRITE_OPCODE = 0x01
OPCODE, ARG0, ARG1, PAYLOAD, ENERGY = 0, 1, 2, 3, 4
NORTH, EAST, SOUTH, WEST = 0, 1, 2, 3

ARBITRATION_SEED_XOR = U64(0x9E3779B97F4A7C15)
MIX_MUL_1 = U64(0xBF58476D1CE4E5B9)
MIX_MUL_2 = U64(0x94D049BB133111EB)
MUT_DOMAIN_CONST = U64(0xD1B54A32D192ED03)
REPLENISH_DOMAIN_CONST = U64(0x2545F4914F6CDD1D)

# Same 4 gather slots as Aether/production/aeth00.py's `_NEIGHBOR_SLOTS`:
# (row_offset, col_offset, required_direction_of_that_neighbor).
_NEIGHBOR_SLOTS = ((-1, 0, SOUTH), (1, 0, NORTH), (0, 1, WEST), (0, -1, EAST))

np.seterr(over="ignore")  # uint64 wraparound is the intended semantic (matches & MASK64).


def mix64_vec(x: np.ndarray) -> np.ndarray:
    x = x.astype(np.uint64)
    x ^= x >> U64(30)
    x *= MIX_MUL_1
    x ^= x >> U64(27)
    x *= MIX_MUL_2
    x ^= x >> U64(31)
    return x


def pack_coords_vec(row: np.ndarray, col: np.ndarray) -> np.ndarray:
    return (row.astype(np.uint64) << U64(32)) | col.astype(np.uint64)


def arbitration_priority_vec(
    seed, tick, target_packed, field, source_packed
) -> np.ndarray:
    h0 = mix64_vec(np.uint64(seed) ^ ARBITRATION_SEED_XOR)
    h1 = mix64_vec(h0 ^ np.uint64(tick))
    h2 = mix64_vec(h1 ^ target_packed)
    h3 = mix64_vec(h2 ^ np.uint64(field))
    return mix64_vec(h3 ^ source_packed)


def mu_vec(seed, tick, packed, field, mut_numer):
    g0 = mix64_vec(np.uint64(seed) ^ MUT_DOMAIN_CONST)
    g1 = mix64_vec(g0 ^ np.uint64(tick))
    g2 = mix64_vec(g1 ^ packed)
    key = mix64_vec(g2 ^ np.uint64(field))
    triggered = (key >> U64(32)) < np.uint64(mut_numer)
    bit_index = (key & U64(0b111)).astype(np.int16)
    return triggered, bit_index


def rho_vec(seed, tick, packed, replenish_numer):
    r0 = mix64_vec(np.uint64(seed) ^ REPLENISH_DOMAIN_CONST)
    r1 = mix64_vec(r0 ^ np.uint64(tick))
    key = mix64_vec(r1 ^ packed)
    return (key >> U64(32)) < np.uint64(replenish_numer)



def gpu_step(
    H, W, seed, tick, write_cost, maintenance_cost, replenish_numer,
    replenish_amount, mut_numer, opcode, arg0, arg1, payload, energy,
):
    """One tick, whole-grid vectorized, no per-site Python loop (the
    GPU-shaped computation). Inputs/outputs are H x W uint8 arrays.
    Returns (next_opcode, next_arg0, next_arg1, next_payload,
    next_energy, counters) -- `counters` is a small tier-1-style dict
    (GPU_RUNPOD.md), not a per-event trace (a real GPU kernel does not
    emit one row per micro-event; K7's event-ledger cross-check is
    performed against the CPU oracle's trace, not this module)."""
    packed = pack_coords_vec(np.arange(H).reshape(H, 1), np.arange(W).reshape(1, W))
    energy_i = energy.astype(np.int64)
    starved = energy_i < write_cost
    active = (opcode == WRITE_OPCODE) & (~starved)
    direction = (arg0 % 4).astype(np.uint8)
    target_field = (arg1 % 5).astype(np.uint8)
    transfer_amt = np.minimum(payload.astype(np.int16),
                              (energy_i - write_cost).astype(np.int16))
    value = np.where(target_field == ENERGY, transfer_amt, payload.astype(np.int16))

    template = [opcode.astype(np.int16), arg0.astype(np.int16),
                arg1.astype(np.int16), payload.astype(np.int16)]
    winner4_has, winner4_val = None, None

    for f in range(5):
        best_has = np.zeros((H, W), dtype=bool)
        best_priority = np.zeros((H, W), dtype=np.uint64)
        best_value = np.zeros((H, W), dtype=np.int16)
        for dr, dc, required_dir in _NEIGHBOR_SLOTS:
            shift = (-dr, -dc)
            n_active = np.roll(active, shift, axis=(0, 1))
            n_dir = np.roll(direction, shift, axis=(0, 1))
            n_field = np.roll(target_field, shift, axis=(0, 1))
            n_value = np.roll(value, shift, axis=(0, 1))
            slot_valid = n_active & (n_dir == required_dir) & (n_field == f)
            prio = arbitration_priority_vec(
                seed, tick, packed, f, np.roll(packed, shift, axis=(0, 1)))
            cond = slot_valid & (~best_has | (prio > best_priority))
            best_priority = np.where(cond, prio, best_priority)
            best_value = np.where(cond, n_value, best_value)
            best_has = best_has | slot_valid
        if f == ENERGY:
            winner4_has, winner4_val = best_has, best_value
        else:
            trig, bit_idx = mu_vec(seed, tick, packed, f, mut_numer)
            stored = np.where(trig, best_value ^ (np.int16(1) << bit_idx), best_value)
            template[f] = np.where(best_has, stored, template[f])

    next_opcode, next_arg0, next_arg1, next_payload = template

    # Phase 5: energy settlement.
    e = energy_i.copy()
    e -= np.where(active, write_cost, 0)
    is_transfer_source = active & (target_field == ENERGY)
    e -= np.where(is_transfer_source, value, 0)
    headroom = 255 - e
    delta = np.where(winner4_has, np.minimum(winner4_val, headroom), 0)
    e += delta
    # Phase 6: maintenance decay, floored at 0.
    e -= np.minimum(maintenance_cost, e)
    # Phase 7: independent per-site replenishment, saturating at 255.
    triggered = rho_vec(seed, tick, packed, replenish_numer)
    headroom2 = 255 - e
    e += np.where(triggered, np.minimum(replenish_amount, headroom2), 0)

    counters = {
        "activity_density": float(np.count_nonzero(active)) / (H * W),
        "total_energy": int(e.sum()),
    }
    return (
        next_opcode.astype(np.uint8), next_arg0.astype(np.uint8),
        next_arg1.astype(np.uint8), next_payload.astype(np.uint8),
        e.astype(np.uint8), counters,
    )
