"""
Aether AETH-01 (candidate semantics_id aeth01.v1) -- GPU canary kernel.

Backend-agnostic port of `test/reference/gpu_aeth01.py`: identical physics
bodies and constants, with abbreviated docs and omitted array annotations.
The backend/warning shim selects CuPy if importable (not proof of working
GPU hardware), else NumPy for local smoke tests. Any change to the
PHYSICS below that is not also made in `gpu_aeth01.py` invalidates the
local differential-test evidence this canary is meant to extend onto
real hardware; keep the two in sync by hand (no build step copies one
into the other).
"""

try:
    import cupy as np  # noqa: N811 -- intentional alias, see module docstring.
    BACKEND = "cupy"
except ImportError:
    import numpy as np  # noqa: N811
    BACKEND = "numpy_fallback"
    # Intended uint64 wraparound; CuPy does not implement numpy.seterr.
    np.seterr(over="ignore")

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


def mix64_vec(x):
    x = x.astype(np.uint64)
    x ^= x >> U64(30)
    x *= MIX_MUL_1
    x ^= x >> U64(27)
    x *= MIX_MUL_2
    x ^= x >> U64(31)
    return x
def mix64_scalar(x):
    """Same splitmix64 finalizer as `mix64_vec`, on one host scalar.

    Exists because NumPy reports integer overflow for scalar operations
    and not for array ones, so feeding a scalar to the vectorized mixer
    emits `overflow encountered in scalar multiply` on a wraparound that
    is the intended semantic. Python ints are unbounded and the mask is
    explicit, so this path cannot overflow rather than overflowing
    quietly. Constants are reused from the vectorized mixer, not
    restated, and equality with it is asserted over a randomized 64-bit
    corpus in test_aeth01_mix64_scalar.py."""
    mask = int(MASK64)
    x = int(x) & mask
    x ^= x >> 30
    x = (x * int(MIX_MUL_1)) & mask
    x ^= x >> 27
    x = (x * int(MIX_MUL_2)) & mask
    x ^= x >> 31
    return np.uint64(x)


def pack_coords_vec(row, col):
    return (row.astype(np.uint64) << U64(32)) | col.astype(np.uint64)


def arbitration_priority_vec(
    seed, tick, target_packed, field, source_packed
):
    h0 = mix64_scalar(np.uint64(seed) ^ ARBITRATION_SEED_XOR)
    h1 = mix64_scalar(h0 ^ np.uint64(tick))
    h2 = mix64_vec(h1 ^ target_packed)
    h3 = mix64_vec(h2 ^ np.uint64(field))
    return mix64_vec(h3 ^ source_packed)


def mu_vec(seed, tick, packed, field, mut_numer):
    g0 = mix64_scalar(np.uint64(seed) ^ MUT_DOMAIN_CONST)
    g1 = mix64_scalar(g0 ^ np.uint64(tick))
    g2 = mix64_vec(g1 ^ packed)
    key = mix64_vec(g2 ^ np.uint64(field))
    triggered = (key >> U64(32)) < np.uint64(mut_numer)
    bit_index = (key & U64(0b111)).astype(np.int16)
    return triggered, bit_index


def rho_vec(seed, tick, packed, replenish_numer):
    r0 = mix64_scalar(np.uint64(seed) ^ REPLENISH_DOMAIN_CONST)
    r1 = mix64_scalar(r0 ^ np.uint64(tick))
    key = mix64_vec(r1 ^ packed)
    return (key >> U64(32)) < np.uint64(replenish_numer)


def gpu_step(
    H, W, seed, tick, write_cost, maintenance_cost, replenish_numer,
    replenish_amount, mut_numer, opcode, arg0, arg1, payload, energy,
    observer=None,
):
    """One tick, whole-grid vectorized. See `gpu_aeth01.py` for full
    phase-by-phase commentary (identical algorithm)."""
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
        watched = observer is not None
        best_slot = np.full((H, W), 255, dtype=np.uint8) if watched else None
        contenders = np.zeros((H, W), dtype=np.uint8) if watched else None
        for slot, (dr, dc, required_dir) in enumerate(_NEIGHBOR_SLOTS):
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
            if watched:
                best_slot = np.where(cond, np.uint8(slot), best_slot)
                contenders = contenders + slot_valid.astype(np.uint8)
            best_has = best_has | slot_valid
        if watched:
            observer.append((best_slot, contenders))
        if f == ENERGY:
            winner4_has, winner4_val = best_has, best_value
        else:
            trig, bit_idx = mu_vec(seed, tick, packed, f, mut_numer)
            stored = np.where(trig, best_value ^ (np.int16(1) << bit_idx), best_value)
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
