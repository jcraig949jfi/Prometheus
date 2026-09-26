"""AETH-03 candidate physics: `aeth01.v1` with exactly one assumption changed.

SCOUT KERNELS, NOT FROZEN SEMANTICS. Each variant is a counterfactual
law used only by the cheap CPU scouts in `aeth03_scouts.py`. None of
them is `aeth01.v1`, and none may be reported under that id: every
variant carries its own `SEMANTICS_ID`. `aeth01.v1` itself is untouched
(`Aether/test/reference/gpu_aeth01.py` is imported, never edited), and
the `v1` variant here is asserted bit-identical to it in
`test_aeth03_variants.py`, so a difference between a variant and the
baseline cannot come from a transcription error in the shared parts.

One change per variant, stated against the v1 phase it replaces
(`AETH01_REPAIRED_FREEZE_CANDIDATE.md` s3):

  v1   baseline, unchanged
  add  COMMIT (phase 4): fields 0-3 store (old + payload) mod 256
       instead of payload. A write combines with the target's prior
       value rather than replacing it.
  hys  ARBITRATE (phase 3), fields 0-3 only: a contender whose value
       equals the target's current value in that field outranks every
       contender whose value differs; ties inside each group are broken
       by the unmodified v1 priority. The field's current value is the
       only memory used; no state is added.
  chg  SETTLE (phase 5a): an emitting site is debited WRITE_COST only if
       its proposal would change the target, i.e. payload differs from
       the target's current value in the selected field 0-3. Energy
       proposals (field 4) always pay. Decode is unchanged, so a site
       below WRITE_COST is still starved.
  cnd  DECODE/EMIT (phases 1-2): a second active opcode, 0x02, emits
       exactly like WRITE but its proposal is valid only where the
       target field's low two bits equal bits 2-3 of the emitter's arg0.
       It pays WRITE_COST whether or not the condition holds. Direction
       uses arg0 mod 4 as in v1, so bits 2-3 are otherwise unused.
  str  EMIT (phase 2): direction = (arg0 + (energy >> 6)) mod 4, so the
       emitter's current resource level, a record of its history,
       rotates which neighbour it acts on.

Ladder 2 (PHYSICS_DESIGN_01 s8, targeting propagation):

  mov  COMMIT (phase 4): a source whose template proposal (fields 0-3)
       wins has its own payload cleared to 0 after the tick -- the byte
       moves instead of being copied -- unless the source itself received
       a winning payload write this tick, which then stands.
  rcv  DECODE (phase 1): a site that received a winning template write on
       the previous tick is active this tick even if its opcode is not
       WRITE (it still needs energy >= WRITE_COST and pays it). DEVIATION
       FROM s8, stated: s8 says ladder 2 adds no state, but "received last
       tick" is one bit per site carried across ticks. The kernel takes it
       as `received=` and returns the next one in counters["received"].
  m4   EMIT (phase 2): target field = (arg1 >> 3) mod 5 instead of
       arg1 mod 5, so flips of arg1's low three bits leave the field
       unchanged (s8 asked for "some single-bit flips" to be neutral).
       Chosen over s8's example "arg1 mod 8 folded onto five fields"
       because any 8-to-5 fold gives three fields double weight; this
       one spreads 32 values 7/7/6/6/6.

Everything else -- arbitration hash, Mu, energy transfer settlement,
maintenance, replenishment -- is the v1 text.
"""

import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REF = os.path.join(os.path.dirname(_HERE), "test", "reference")
if _REF not in sys.path:
    sys.path.insert(0, _REF)

import gpu_aeth01 as K                                   # noqa: E402

VARIANTS = ("v1", "add", "hys", "chg", "cnd", "str", "mov", "rcv", "m4")
# `v1g` is v1 routed through this module's shared code path rather than
# delegated to gpu_step. It exists only so the differential test can
# prove the shared path IS v1 before any variant's single change is
# layered on it.
_ALL = VARIANTS + ("v1g",)
SEMANTICS_ID = {
    "v1": "aeth01.v1",
    "add": "aeth03.add.scout0",
    "hys": "aeth03.hys.scout0",
    "chg": "aeth03.chg.scout0",
    "cnd": "aeth03.cnd.scout0",
    "str": "aeth03.str.scout0",
    "mov": "aeth03.mov.scout0",
    "rcv": "aeth03.rcv.scout0",
    "m4": "aeth03.m4.scout0",
    "v1g": "aeth01.v1",
}
COND_OPCODE = 0x02
ENERGY = K.ENERGY
_SLOTS = K._NEIGHBOR_SLOTS
# Offset from a site to the neighbour it targets, indexed by direction
# (N, E, S, W), as implied by _NEIGHBOR_SLOTS' required directions.
_DIR_OFFSET = {K.NORTH: (-1, 0), K.EAST: (0, 1), K.SOUTH: (1, 0), K.WEST: (0, -1)}


def _target_value(field_arrays, direction, target_field):
    """For each emitter, the current value of the field it targets."""
    out = np.zeros(direction.shape, dtype=np.int16)
    for d, (dr, dc) in _DIR_OFFSET.items():
        for f in range(4):
            there = np.roll(field_arrays[f], (-dr, -dc), axis=(0, 1))
            m = (direction == d) & (target_field == f)
            out = np.where(m, there.astype(np.int16), out)
    return out


def step(variant, H, W, seed, tick, write_cost, maintenance_cost,
         replenish_numer, replenish_amount, mut_numer, opcode, arg0, arg1,
         payload, energy, observer=None, received=None):
    """One tick of the named variant. Same signature/returns as gpu_step.

    `received` is used only by `rcv`: a bool (H, W) array, True where the
    site received a winning template write on the PREVIOUS tick. The next
    tick's array is returned as counters["received"]. It is the one bit of
    per-site state `rcv` needs (see the module docstring).
    """
    if variant not in _ALL:
        raise ValueError("unknown variant %r" % (variant,))
    if variant == "v1":
        return K.gpu_step(H=H, W=W, seed=seed, tick=tick, write_cost=write_cost,
                          maintenance_cost=maintenance_cost,
                          replenish_numer=replenish_numer,
                          replenish_amount=replenish_amount,
                          mut_numer=mut_numer, opcode=opcode, arg0=arg0,
                          arg1=arg1, payload=payload, energy=energy,
                          observer=observer)
    packed = K.pack_coords_vec(np.arange(H).reshape(H, 1),
                               np.arange(W).reshape(1, W))
    energy_i = energy.astype(np.int64)
    starved = energy_i < write_cost
    is_emitter = opcode == K.WRITE_OPCODE
    if variant == "cnd":
        is_emitter = is_emitter | (opcode == COND_OPCODE)
    if variant == "rcv" and received is not None:
        is_emitter = is_emitter | received
    active = is_emitter & (~starved)
    if variant == "str":
        direction = ((arg0.astype(np.int64) + (energy_i >> 6)) % 4).astype(np.uint8)
    else:
        direction = (arg0 % 4).astype(np.uint8)
    if variant == "m4":
        target_field = ((arg1 >> 3) % 5).astype(np.uint8)
    else:
        target_field = (arg1 % 5).astype(np.uint8)
    transfer_amt = np.minimum(payload.astype(np.int16),
                              (energy_i - write_cost).astype(np.int16))
    value = np.where(target_field == ENERGY, transfer_amt,
                     payload.astype(np.int16))
    cond_key = ((arg0 >> 2) & 3).astype(np.int16)
    is_cond = opcode == COND_OPCODE

    template = [opcode.astype(np.int16), arg0.astype(np.int16),
                arg1.astype(np.int16), payload.astype(np.int16)]
    current = [t.copy() for t in template] + [energy_i.astype(np.int16)]
    winner4_has, winner4_val = None, None
    won_src = np.zeros((H, W), dtype=bool)        # mov: a source's template proposal won
    received_next = np.zeros((H, W), dtype=bool)  # rcv: site got a winning template write

    for f in range(5):
        best_has = np.zeros((H, W), dtype=bool)
        best_priority = np.zeros((H, W), dtype=np.uint64)
        best_value = np.zeros((H, W), dtype=np.int16)
        watched = observer is not None
        best_slot = np.full((H, W), 255, dtype=np.uint8) if watched else None
        contenders = np.zeros((H, W), dtype=np.uint8) if watched else None
        n_differ = np.zeros((H, W), dtype=np.uint8) if watched else None
        here = current[f]
        for slot, (dr, dc, required_dir) in enumerate(_SLOTS):
            shift = (-dr, -dc)
            n_active = np.roll(active, shift, axis=(0, 1))
            n_dir = np.roll(direction, shift, axis=(0, 1))
            n_field = np.roll(target_field, shift, axis=(0, 1))
            n_value = np.roll(value, shift, axis=(0, 1))
            slot_valid = n_active & (n_dir == required_dir) & (n_field == f)
            if variant == "cnd":
                n_cond = np.roll(is_cond, shift, axis=(0, 1))
                n_key = np.roll(cond_key, shift, axis=(0, 1))
                slot_valid = slot_valid & (~n_cond | ((here & 3) == n_key))
            prio = K.arbitration_priority_vec(
                seed, tick, packed, f, np.roll(packed, shift, axis=(0, 1)))
            if variant == "hys" and f != ENERGY:
                match = (n_value == here).astype(np.uint64)
                prio = (prio >> np.uint64(1)) | (match << np.uint64(63))
            cond = slot_valid & (~best_has | (prio > best_priority))
            best_priority = np.where(cond, prio, best_priority)
            best_value = np.where(cond, n_value, best_value)
            if variant == "mov" and f != ENERGY:
                # track the winning slot per target without the observer
                if slot == 0:
                    win_slot = np.full((H, W), 255, dtype=np.uint8)
                win_slot = np.where(cond, np.uint8(slot), win_slot)
            if watched:
                best_slot = np.where(cond, np.uint8(slot), best_slot)
                contenders = contenders + slot_valid.astype(np.uint8)
                n_differ = n_differ + (slot_valid & (n_value != here)).astype(np.uint8)
            best_has = best_has | slot_valid
        if watched:
            observer.append((best_slot, contenders, n_differ))
        if f == ENERGY:
            winner4_has, winner4_val = best_has, best_value
        else:
            received_next |= best_has
            if f == K.PAYLOAD:
                payload_winner = best_has
            if variant == "mov":
                for slot, (dr, dc, _rd) in enumerate(_SLOTS):
                    # target (r, c) won from the source at (r + dr, c + dc)
                    won_src |= np.roll(win_slot == slot, (dr, dc), axis=(0, 1))
            commit = best_value
            if variant == "add":
                commit = (template[f] + best_value) & 0xFF
            trig, bit_idx = K.mu_vec(seed, tick, packed, f, mut_numer)
            stored = np.where(trig, commit ^ (np.int16(1) << bit_idx), commit)
            template[f] = np.where(best_has, stored, template[f])

    next_opcode, next_arg0, next_arg1, next_payload = template
    if variant == "mov":
        # The winning source's payload moved to its target: clear it,
        # unless the source itself received a winning payload write this
        # tick, which then stands (the incoming byte arrives after the
        # outgoing one leaves).
        next_payload = np.where(won_src & ~payload_winner, 0, next_payload)

    e = energy_i.copy()
    if variant == "chg":
        there = _target_value(current, direction, target_field)
        pays = active & ((target_field == ENERGY) | (payload.astype(np.int16) != there))
    elif variant == "cnd":
        pays = active
    else:
        pays = active
    e -= np.where(pays, write_cost, 0)
    is_transfer_source = active & (target_field == ENERGY)
    e -= np.where(is_transfer_source, value, 0)
    headroom = 255 - e
    delta = np.where(winner4_has, np.minimum(winner4_val, headroom), 0)
    e += delta
    e -= np.minimum(maintenance_cost, e)
    triggered = K.rho_vec(seed, tick, packed, replenish_numer)
    headroom2 = 255 - e
    e += np.where(triggered, np.minimum(replenish_amount, headroom2), 0)

    counters = {
        "activity_density": float(np.count_nonzero(active)) / (H * W),
        "total_energy": int(e.sum()),
    }
    if variant == "rcv":
        counters["received"] = received_next
    return (
        next_opcode.astype(np.uint8), next_arg0.astype(np.uint8),
        next_arg1.astype(np.uint8), next_payload.astype(np.uint8),
        e.astype(np.uint8), counters,
    )
