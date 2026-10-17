"""ROBUST01 physics: aeth01.op_xor_fold (combine-all-contenders). ONE contest-semantics change against the frozen XOR law.

FROZEN XOR LAW (aeth01.op_xor, REACH01 R2): when several valid writers target the same (site, template field) in a
tick, the kernel keeps ONE, chosen by the coordinate- and seed-keyed arbitration hash, and the site stores
existing ^ winner.
THIS LAW: for a TEMPLATE field (opcode, arg0, arg1, payload) the site stores existing ^ v1 ^ v2 ^ ... over EVERY valid
incoming write (the XOR-fold of all contenders). XOR is commutative and associative, so no order and no arbitration is
needed. With at most one contender the two laws are identical.
UNCHANGED (declared, not tuned):
- the ENERGY field (arg1 % 5 == 4) still has a single hash-chosen winner, and every active transfer source still pays
  its transfer whether or not it wins. This is the only coordinate- or seed-keyed path left in the execution-only
  regime (mutation 0, no rain).
- energy settlement, write cost, starvation, the gather neighbourhood (4 slots, torus) and the tick order.
- two writers carrying the same byte cancel (v ^ v = 0): destructive interference is part of the law.

Implemented as a wrapper, like express01.step: the frozen kernel runs untouched (P0), then each template field is
replaced by existing ^ fold at sites with >= 1 valid contender. The fold is gathered from PRE-tick state, as the
kernel's own contest is.

install() makes op "XOR" mean this law inside the current process, so the frozen REACH01 search, certifier and reducer
code (which hard-codes or passes op "XOR") runs byte-identical under the new semantics. Any other op raises. The patch
reaches every caller that looks the step up as express01.step (r3_frontier, r3_certify, r4_accum, r4_reduce); it does
NOT reach express01.py run as a script (its own module-level step), so r01_run refuses that script.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REACH01 = os.path.abspath(os.path.join(HERE, "..", "REACH01"))
for _p in (os.path.join(REACH01, "R2"), os.path.join(REACH01, "R3"), os.path.join(REACH01, "R4")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import express01 as X  # noqa: E402

SEMANTICS_ID = "aeth01.op_xor_fold"
CONTROL_SEMANTICS_ID = "aeth01.op_xor"
WRITE_OPCODE = 1
ENERGY_FIELD = 4
# (row offset, col offset, direction the neighbour must aim to hit this site): the kernel's _NEIGHBOR_SLOTS.
SLOTS = ((-1, 0, X.S), (1, 0, X.N), (0, 1, X.W), (0, -1, X.E))

_CONTEST_STEP = None
STEP_CALLS = 0   # fold ticks executed in this process (r01_run stamps it: proof the law was exercised)


def gather(xp, s, write_cost):
    """Per template field: (XOR-fold of every valid incoming payload, number of valid contenders); plus the number of
    valid contenders for the energy field. All from pre-tick state s = [opcode, arg0, arg1, payload, energy]."""
    opcode, arg0, arg1, payload, energy = s
    active = (opcode == WRITE_OPCODE) & (energy.astype(xp.int64) >= write_cost)
    direction = arg0 % 4
    field = arg1 % 5
    zero = xp.zeros(opcode.shape, xp.uint8)
    folds = [zero.copy() for _ in range(4)]
    counts = [zero.copy() for _ in range(5)]
    for dr, dc, req in SLOTS:
        sh = (-dr, -dc)
        n_act = xp.roll(active, sh, axis=(0, 1)) & (xp.roll(direction, sh, axis=(0, 1)) == req)
        n_field = xp.roll(field, sh, axis=(0, 1))
        n_val = xp.roll(payload, sh, axis=(0, 1))
        for f in range(5):
            valid = n_act & (n_field == f)
            counts[f] = counts[f] + valid.astype(xp.uint8)
            if f < 4:
                folds[f] = folds[f] ^ xp.where(valid, n_val, zero)
    return folds, counts


def step_fold(xp, K, n, seed, tick, s, energy, observer=None):
    """One tick of aeth01.op_xor_fold. Same signature and return shape as express01.step (minus op)."""
    global STEP_CALLS
    STEP_CALLS += 1
    if observer is not None:
        raise NotImplementedError("aeth01.op_xor_fold has no single winner per site; the contest observer is undefined")
    out = K.gpu_step(n, n, seed, tick, energy["write_cost"], energy["maintenance_cost"],
                     energy["replenish_numer"], energy["replenish_amount"], 0, *s)
    nxt = list(out[:5])
    folds, counts = gather(xp, s, energy["write_cost"])
    for f in range(4):
        nxt[f] = xp.where(counts[f] > 0, s[f] ^ folds[f], nxt[f])
    return nxt, []


def contest_step(*a, **kw):
    """The frozen express01.step, whether or not install() has run (for controls and tests)."""
    return (_CONTEST_STEP or X.step)(*a, **kw)


def install():
    """Inside this process, op "XOR" = aeth01.op_xor_fold. Idempotent. Returns the semantics id."""
    global _CONTEST_STEP
    if _CONTEST_STEP is None:
        _CONTEST_STEP = X.step

        def step(xp, K, op, n, seed, tick, s, energy, observer=None):
            if op != "XOR":
                raise ValueError("ROBUST01 process: only op XOR (= %s) is defined, got %r" % (SEMANTICS_ID, op))
            return step_fold(xp, K, n, seed, tick, s, energy, observer)
        step.semantics_id = SEMANTICS_ID
        X.step = step
    return SEMANTICS_ID


def installed():
    return _CONTEST_STEP is not None


def uninstall():
    """Tests only: restore the frozen contest step."""
    global _CONTEST_STEP
    if _CONTEST_STEP is not None:
        X.step = _CONTEST_STEP
        _CONTEST_STEP = None
