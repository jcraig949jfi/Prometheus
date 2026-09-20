"""
Aether AETH-01 (candidate semantics_id aeth01.v1) -- GPU canary kernel.

Backend-agnostic port of `test/reference/gpu_aeth01.py`: identical body,
only the import at the top differs (CuPy if importable -- i.e. actual
GPU hardware + CUDA -- else NumPy, so this exact file can also be
smoke-tested locally before ever touching a pod). Any change to the
PHYSICS below that is not also made in `gpu_aeth01.py` invalidates the
local differential-test evidence this canary is meant to extend onto
real hardware; keep the two in sync by hand (no build step copies one
into the other).
"""

try:
    import cupy as np  # noqa: N811 -- intentional alias, see module docstring.
    BACKEND = "cupy"
except ImportError:  # pragma: no cover -- exercised only off a GPU pod.
    import numpy as np  # noqa: N811
    BACKEND = "numpy_fallback"

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

_NEIGHBOR_SLOTS = ((-1, 0, SOUTH), (1, 0, NORTH), (0, 1, WEST), (0, -1, EAST))

np.seterr(over="ignore")


def mix64_vec(x):
    x = x.astype(np.uint64)
    u = (x ^ (x >> U64(30))) * MIX_MUL_1
    v = (u ^ (u >> U64(27))) * MIX_MUL_2
    return v ^ (v >> U64(31))


def pack_coords_vec(row, col):
    return (row.astype(np.uint64) << U64(32)) | col.astype(np.uint64)


def arbitration_priority_vec(seed, tick, tr, tc, field, sr, sc):
    h0 = mix64_vec(np.uint64(seed) ^ ARBITRATION_SEED_XOR)
    h1 = mix64_vec(h0 ^ np.uint64(tick))
    h2 = mix64_vec(h1 ^ pack_coords_vec(tr, tc))
    h3 = mix64_vec(h2 ^ np.uint64(field))
    return mix64_vec(h3 ^ pack_coords_vec(sr, sc))


def mu_vec(seed, tick, row, col, field, mut_numer):
    g0 = mix64_vec(np.uint64(seed) ^ MUT_DOMAIN_CONST)
    g1 = mix64_vec(g0 ^ np.uint64(tick))
    g2 = mix64_vec(g1 ^ pack_coords_vec(row, col))
    key = mix64_vec(g2 ^ np.uint64(field))
    triggered = (key >> U64(32)) < np.uint64(mut_numer)
    bit_index = (key & U64(0b111)).astype(np.int64)
    return triggered, bit_index


def rho_vec(seed, tick, row, col, replenish_numer):
    r0 = mix64_vec(np.uint64(seed) ^ REPLENISH_DOMAIN_CONST)
    r1 = mix64_vec(r0 ^ np.uint64(tick))
    key = mix64_vec(r1 ^ pack_coords_vec(row, col))
    return (key >> U64(32)) < np.uint64(replenish_numer)


def gpu_step(
    H, W, seed, tick, write_cost, maintenance_cost, replenish_numer,
    replenish_amount, mut_numer, opcode, arg0, arg1, payload, energy,
):
    """One tick, whole-grid vectorized. See `gpu_aeth01.py` for full
    phase-by-phase commentary (identical algorithm)."""
    row_idx, col_idx = np.meshgrid(np.arange(H), np.arange(W), indexing="ij")
    energy_i = energy.astype(np.int64)
    starved = energy_i < write_cost
    active = (opcode == WRITE_OPCODE) & (~starved)
    direction = arg0.astype(np.int64) % 4
    target_field = arg1.astype(np.int64) % 5
    transfer_amt = np.minimum(payload.astype(np.int64), energy_i - write_cost)
    value = np.where(target_field == ENERGY, transfer_amt, payload.astype(np.int64))

    template = [opcode.astype(np.int64).copy(), arg0.astype(np.int64).copy(),
                arg1.astype(np.int64).copy(), payload.astype(np.int64).copy()]
    winner4_has, winner4_val = None, None

    for f in range(5):
        best_has = np.zeros((H, W), dtype=bool)
        best_priority = np.zeros((H, W), dtype=np.uint64)
        best_value = np.zeros((H, W), dtype=np.int64)
        for dr, dc, required_dir in _NEIGHBOR_SLOTS:
            n_row, n_col = (row_idx + dr) % H, (col_idx + dc) % W
            n_active = active[n_row, n_col]
            n_dir = direction[n_row, n_col]
            n_field = target_field[n_row, n_col]
            n_value = value[n_row, n_col]
            slot_valid = n_active & (n_dir == required_dir) & (n_field == f)
            prio = arbitration_priority_vec(seed, tick, row_idx, col_idx, f, n_row, n_col)
            cond = slot_valid & (~best_has | (prio > best_priority))
            best_priority = np.where(cond, prio, best_priority)
            best_value = np.where(cond, n_value, best_value)
            best_has = best_has | slot_valid
        if f == ENERGY:
            winner4_has, winner4_val = best_has, best_value
        else:
            trig, bit_idx = mu_vec(seed, tick, row_idx, col_idx, f, mut_numer)
            stored = np.where(trig, best_value ^ (np.int64(1) << bit_idx), best_value)
            template[f] = np.where(best_has, stored, template[f])

    next_opcode, next_arg0, next_arg1, next_payload = template

    e = energy_i.copy()
    e -= np.where(active, write_cost, 0)
    is_transfer_source = active & (target_field == ENERGY)
    e -= np.where(is_transfer_source, value, 0)
    headroom = 255 - e
    delta = np.where(winner4_has, np.minimum(winner4_val, headroom), 0)
    e += delta
    e -= np.minimum(maintenance_cost, e)
    triggered = rho_vec(seed, tick, row_idx, col_idx, replenish_numer)
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
