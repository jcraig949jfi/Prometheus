"""EvCA density classification: a pure library.

Extracted from `herakles/specimens/spec-evca-density/derived/verify_rule_tables.py`
under WP-C1. The specimen directory keeps the immutable originals and the
recovery record; this module is the executable form, with nothing in it that
runs, reads, writes or seeds anything at import time.

PURITY CONTRACT
  - No top-level execution. Importing this module evaluates constants only.
  - No file I/O anywhere, at import or at call time. The six genomes are
    embedded in `genomes.py`; a test asserts they still match the specimen
    JSON, so drift is caught rather than silently tolerated.
  - No global RNG. Every stochastic entry point takes an explicit integer
    seed and builds its own `numpy.random.Generator`.
  - No mutation of caller arrays. Every function returns new arrays.

PINNED CONVENTIONS. Each is a decision that changes results, so each is
stated here, enforced in code, and covered by a test. Where the source did
not state a convention, that is said explicitly.

  RING BOUNDARY
      Periodic. Cell 0's left neighbour is cell N-1. Implemented with
      `numpy.roll`, which wraps. Stated in the specimen record.

  NEIGHBOURHOOD BIT ORDER
      Seven cells, i-3 .. i+3. The LEFTMOST neighbour (i-3) is the MOST
      SIGNIFICANT bit of the neighbourhood index:
          idx = sum over j in 0..6 of cell[i-3+j] << (6-j)
      NOT stated in either source. Determined empirically during recovery and
      re-confirmed here by deriving `maj` and `GKL` from their definitions and
      matching all 32 published hex digits. `test_msb_convention_is_forced`
      re-runs that derivation, so the convention is re-earned on every test
      run rather than trusted.

  RULE ENCODING
      32 hexadecimal digits, 128 bits. Bit k of the string, counting from the
      LEFT, is the output for neighbourhood index k. Stated verbatim in the
      EvCA review Table 1 caption. `decode_table` and `encode_table` are exact
      inverses and a test asserts the round trip on all six genomes.

  SUPPORTED RADIUS
      r = 3 ONLY. This module refuses any other radius. A general decoder is
      not implemented, and silently generalising an r=3-only decoder is the
      specific failure the work package names. `RADIUS` is a module constant
      and `require_radius` raises on anything else.

  UPDATE COUNT
      No default. `steps` is a required argument everywhere it is used.
      The literature convention is a maximum of roughly 2N updates; the
      recovery verifier used 300 for N = 149. That is a CONVENTION, not a
      property of the rules, and it is one of the named suspects for any
      discrepancy against published numbers, so the caller must state it.

  MAJORITY AND TIES
      N must be ODD, and `require_lattice` raises on even N. With N odd the
      density is never exactly one half, so no tie rule is needed and none is
      invented here. Refusing even N is preferred to choosing a convention
      the source never had to state.

  ACCURACY
      The fraction of initial conditions for which the lattice is in the
      uniform configuration matching the IC's majority AFTER `steps` updates.

      This is "the state at T", not "was ever reached by T". The two agree
      only if the uniform configurations are fixed points of the rule, which
      is a property of table entries 0 and 127. `fixes_uniform_states` reports
      it and `accuracy` records it in its result, so a rule for which the two
      definitions differ is visible rather than silently mis-scored.

  WITNESS
      The indices of misclassified initial conditions, ascending, truncated to
      a declared bound. The result always carries `witness_truncated` and the
      full `n_incorrect`, so a truncated witness can never be mistaken for a
      complete one.

  SYMMETRY
      Reflection and complement are exact semantics-preserving moves. Both
      transform the RULE AND THE REALISED INITIAL CONDITION; complement also
      flips the majority target. Comparisons are made on NORMALISED
      trajectories, never on raw hashes of differently oriented arrays.
"""
from __future__ import annotations

import hashlib
from typing import Dict, List, Optional

import numpy as np

#: The only radius this module implements. See PINNED CONVENTIONS.
RADIUS = 3
#: Neighbourhood width, 2 * RADIUS + 1.
WIDTH = 2 * RADIUS + 1
#: Number of distinct neighbourhoods, hence rule-table length.
TABLE_BITS = 1 << WIDTH          # 128
#: Hex digits in an encoded table.
TABLE_HEX = TABLE_BITS // 4      # 32
#: Default cap on the returned witness. Callers may raise or lower it.
WITNESS_LIMIT = 64


class EvcaError(ValueError):
    """Any violation of a pinned convention. Always raised, never warned."""


# ---------------------------------------------------------------------------
# Guards. Each refuses rather than coerces.
# ---------------------------------------------------------------------------

def require_radius(r: int) -> int:
    if r != RADIUS:
        raise EvcaError(
            "radius %r is not supported: this module implements r = %d only, "
            "and the rule-table decoder is specific to a %d-cell "
            "neighbourhood. Generalising it silently would change what every "
            "recovered genome means." % (r, RADIUS, WIDTH))
    return r


def require_lattice(n_cells: int) -> int:
    if not isinstance(n_cells, (int, np.integer)) or isinstance(n_cells, bool):
        raise EvcaError("lattice size must be an integer, got %r" % (n_cells,))
    if n_cells < WIDTH:
        raise EvcaError(
            "lattice size %d is smaller than the %d-cell neighbourhood; the "
            "ring would wrap onto itself and a cell would be its own "
            "neighbour more than once" % (n_cells, WIDTH))
    if n_cells % 2 == 0:
        raise EvcaError(
            "lattice size %d is even. The density-classification task is "
            "defined for ODD N so that no initial condition is exactly at "
            "density one half. No tie-breaking convention is assumed here "
            "because the sources never needed one." % n_cells)
    return int(n_cells)


def require_steps(steps: int) -> int:
    if not isinstance(steps, (int, np.integer)) or isinstance(steps, bool):
        raise EvcaError("steps must be an integer, got %r" % (steps,))
    if steps < 0:
        raise EvcaError("steps must be non-negative, got %d" % steps)
    return int(steps)


def require_density(density: float) -> float:
    if not isinstance(density, (int, float, np.floating)) or \
            isinstance(density, bool):
        raise EvcaError("density must be a number, got %r" % (density,))
    if not (0.0 <= float(density) <= 1.0):
        raise EvcaError("density %r is outside [0, 1]" % (density,))
    return float(density)


def require_table(table: np.ndarray) -> np.ndarray:
    t = np.asarray(table)
    if t.shape != (TABLE_BITS,):
        raise EvcaError(
            "rule table must have shape (%d,), got %r" % (TABLE_BITS, t.shape))
    if not np.isin(t, (0, 1)).all():
        raise EvcaError("rule table must contain only 0 and 1")
    return t.astype(np.uint8)


# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------

def decode_table(hex_string: str) -> np.ndarray:
    """32 hex digits -> a (128,) uint8 table. Bit k from the LEFT is index k."""
    if not isinstance(hex_string, str):
        raise EvcaError("rule must be a hex string, got %r" % (hex_string,))
    h = hex_string.replace(" ", "").replace("_", "").lower()
    if len(h) != TABLE_HEX:
        raise EvcaError(
            "rule must be exactly %d hex digits (%d bits), got %d: %r"
            % (TABLE_HEX, TABLE_BITS, len(h), hex_string))
    if any(c not in "0123456789abcdef" for c in h):
        raise EvcaError("rule contains a non-hexadecimal character: %r"
                        % (hex_string,))
    bits = bin(int(h, 16))[2:].zfill(TABLE_BITS)
    return np.array([int(b) for b in bits], dtype=np.uint8)


def encode_table(table: np.ndarray) -> str:
    """Exact inverse of `decode_table`."""
    t = require_table(table)
    return "%0*x" % (TABLE_HEX, int("".join(str(int(b)) for b in t), 2))


# ---------------------------------------------------------------------------
# Dynamics
# ---------------------------------------------------------------------------

def neighbourhood_index(states: np.ndarray) -> np.ndarray:
    """(n, N) states -> (n, N) neighbourhood indices under the pinned order."""
    s = np.asarray(states)
    if s.ndim != 2:
        raise EvcaError("states must be 2-D (n_ics, n_cells), got shape %r"
                        % (s.shape,))
    require_lattice(s.shape[1])
    idx = np.zeros(s.shape, dtype=np.int32)
    for j, off in enumerate(range(-RADIUS, RADIUS + 1)):
        # np.roll(s, -off) brings cell (i + off) to position i.
        idx |= np.roll(s, -off, axis=1).astype(np.int32) << (WIDTH - 1 - j)
    return idx


def step(states: np.ndarray, table: np.ndarray) -> np.ndarray:
    """One synchronous update of every cell. Returns a NEW array."""
    t = require_table(table)
    return t[neighbourhood_index(states)]


def evolve(states: np.ndarray, table: np.ndarray, steps: int,
           record: bool = False) -> np.ndarray:
    """Advance `steps` updates.

    record=False returns the final (n, N) state.
    record=True returns the full (steps + 1, n, N) space-time trajectory,
    including the initial condition at index 0.
    """
    require_steps(steps)
    t = require_table(table)
    cur = np.asarray(states).astype(np.uint8)
    if not record:
        for _ in range(steps):
            cur = step(cur, t)
        return cur
    frames = np.empty((steps + 1,) + cur.shape, dtype=np.uint8)
    frames[0] = cur
    for k in range(steps):
        cur = step(cur, t)
        frames[k + 1] = cur
    return frames


def fixes_uniform_states(table: np.ndarray) -> Dict[str, bool]:
    """Are the two uniform configurations fixed points of this rule?

    Entry 0 is the all-zeros neighbourhood and entry 127 the all-ones one, so
    these two bits decide it. It matters because `accuracy` reads the state AT
    `steps`; if a uniform configuration is not a fixed point, "in the correct
    uniform state at T" and "reached the correct uniform state by T" are
    different measurements.
    """
    t = require_table(table)
    return {"all_zeros_fixed": bool(t[0] == 0),
            "all_ones_fixed": bool(t[TABLE_BITS - 1] == 1)}


# ---------------------------------------------------------------------------
# Initial conditions
# ---------------------------------------------------------------------------

def require_count(exact_count: int, n_cells: int) -> int:
    """An exact number of ones for a lattice of `n_cells`. Refuses, never clips."""
    if not isinstance(exact_count, (int, np.integer)) \
            or isinstance(exact_count, bool):
        raise EvcaError("exact_count must be an integer, got %r"
                        % (exact_count,))
    if not (0 <= exact_count <= n_cells):
        raise EvcaError("exact_count %d is outside [0, %d]"
                        % (exact_count, n_cells))
    return int(exact_count)


def make_ics(n_ics: int, n_cells: int, seed: int,
             density: Optional[float] = None,
             exact_count: Optional[int] = None) -> np.ndarray:
    """Seeded initial conditions. No global RNG is touched.

    density=None draws each cell iid uniform, which is the unbiased ensemble
    the published performance figures are defined over. A float instead draws
    each cell iid Bernoulli(density), which is a DIFFERENT ensemble and must
    not be compared with published numbers.

    exact_count=k (2026-09-16, THEO-REQ-006) draws each initial condition as
    a uniformly random arrangement of EXACTLY k ones among `n_cells` cells (a
    seeded permutation of a fixed-count vector), so the realised density is
    k / n_cells on every row and the majority target is fixed by k alone.
    This is a THIRD ensemble: it is not the Bernoulli one (whose realised
    count has sd sqrt(p (1 - p) / N)) and it must not be compared with
    published numbers either. `density` and `exact_count` are mutually
    exclusive; passing both is refused rather than resolved.

    The three ensembles do not share a random stream: exact_count=k under a
    seed is unrelated to density=k/N under the same seed. Nothing here
    claims otherwise.
    """
    if not isinstance(n_ics, (int, np.integer)) or isinstance(n_ics, bool) \
            or n_ics < 1:
        raise EvcaError("n_ics must be a positive integer, got %r" % (n_ics,))
    n = require_lattice(n_cells)
    if not isinstance(seed, (int, np.integer)) or isinstance(seed, bool):
        raise EvcaError("seed must be an integer, got %r" % (seed,))
    if density is not None and exact_count is not None:
        raise EvcaError(
            "density and exact_count are two different ensembles; pass one")
    rng = np.random.default_rng(int(seed))
    if exact_count is not None:
        k = require_count(exact_count, n)
        base = np.zeros(n, dtype=np.uint8)
        base[:k] = 1
        rows = np.empty((int(n_ics), n), dtype=np.uint8)
        for i in range(int(n_ics)):
            rows[i] = base[rng.permutation(n)]
        return rows
    p = 0.5 if density is None else require_density(density)
    return (rng.random((int(n_ics), n)) < p).astype(np.uint8)


def majority_target(states: np.ndarray) -> np.ndarray:
    """1 where the IC has more ones than zeros, else 0. Requires odd N."""
    s = np.asarray(states)
    n_cells = require_lattice(s.shape[1])
    return (s.sum(axis=1) * 2 > n_cells).astype(np.uint8)


# ---------------------------------------------------------------------------
# The measurement
# ---------------------------------------------------------------------------

def classify(table: np.ndarray, ics: np.ndarray, steps: int,
             witness_limit: int = WITNESS_LIMIT) -> Dict[str, object]:
    """Run the task and report accuracy with a bounded witness.

    Every field a caller needs in order NOT to over-read the number is in the
    result: the witness bound and whether it bit, the uniform-fixed-point
    facts, and the exact accuracy denominator.
    """
    t = require_table(table)
    require_steps(steps)
    s = np.asarray(ics).astype(np.uint8)
    if s.ndim != 2:
        raise EvcaError("ics must be 2-D (n_ics, n_cells), got %r" % (s.shape,))
    n_cells = require_lattice(s.shape[1])
    if witness_limit < 0:
        raise EvcaError("witness_limit must be non-negative")

    target = majority_target(s)
    final = evolve(s, t, steps)
    ones = final.sum(axis=1)
    reached_all_ones = ones == n_cells
    reached_all_zeros = ones == 0
    correct = np.where(target == 1, reached_all_ones, reached_all_zeros)

    wrong = np.flatnonzero(~correct)
    witness = wrong[:witness_limit].tolist()
    return {
        "accuracy": float(correct.mean()),
        "n_ics": int(s.shape[0]),
        "n_cells": n_cells,
        "steps": int(steps),
        "n_correct": int(correct.sum()),
        "n_incorrect": int(wrong.size),
        "witness": [int(i) for i in witness],
        "witness_limit": int(witness_limit),
        # `witness_truncated` means "the witness OMITS at least one index".
        # A witness of length exactly `witness_limit` with this False is a
        # COMPLETE vector, and n_incorrect == len(witness) says so. The bound
        # is `>` deliberately and stays `>` (THEO-REQ-004, 2026-09-16): a
        # validator that wants to tell a full vector from a cut one compares
        # len(witness) with n_incorrect, which is always present.
        "witness_truncated": bool(wrong.size > witness_limit),
        "uniform_fixed_points": fixes_uniform_states(t),
        "correct_mask_digest": mask_digest(correct),
        # The whole per-IC outcome, not a bounded witness of it, so a reader
        # never has to re-execute to learn which ICs succeeded above the
        # witness bound (THEO-REQ-004 capability half).
        "correct_mask_hex": pack_mask_hex(correct),
    }


def mask_digest(mask: np.ndarray) -> str:
    """Digest of a boolean per-IC mask. Orientation-free by construction."""
    m = np.asarray(mask).astype(np.uint8).ravel()
    return "sha256:" + hashlib.sha256(m.tobytes()).hexdigest()[:32]


def pack_mask_hex(mask: np.ndarray) -> str:
    """A boolean per-IC mask as hex. IC i is bit (7 - i % 8) of byte i // 8.

    `numpy.packbits` big-endian order; the last byte is zero-padded on the
    right. The mask's length is NOT recoverable from the string alone, so
    `unpack_mask_hex` takes it, and every result that carries this field
    carries `n_ics` beside it.
    """
    m = np.asarray(mask).astype(np.uint8).ravel()
    if m.size and not np.isin(m, (0, 1)).all():
        raise EvcaError("mask must contain only 0 and 1")
    return np.packbits(m, bitorder="big").tobytes().hex()


def unpack_mask_hex(hex_string: str, n_ics: int) -> np.ndarray:
    """Exact inverse of `pack_mask_hex` given the mask length."""
    if not isinstance(n_ics, (int, np.integer)) or isinstance(n_ics, bool) \
            or n_ics < 0:
        raise EvcaError("n_ics must be a non-negative integer, got %r"
                        % (n_ics,))
    if not isinstance(hex_string, str) or len(hex_string) % 2:
        raise EvcaError("mask hex must be a string of whole bytes")
    raw = np.frombuffer(bytes.fromhex(hex_string), dtype=np.uint8)
    if raw.size != (int(n_ics) + 7) // 8:
        raise EvcaError("mask hex holds %d byte(s); %d IC(s) need %d"
                        % (raw.size, n_ics, (int(n_ics) + 7) // 8))
    bits = np.unpackbits(raw, bitorder="big")[:int(n_ics)]
    if bits.size < raw.size * 8 and np.unpackbits(raw, bitorder="big")[
            int(n_ics):].any():
        raise EvcaError("mask hex has non-zero padding bits")
    return bits.astype(bool)


# ---------------------------------------------------------------------------
# Exact symmetries
# ---------------------------------------------------------------------------

def reverse_bits(idx: int) -> int:
    """Reverse the WIDTH bits of a neighbourhood index."""
    out = 0
    for j in range(WIDTH):
        if idx & (1 << j):
            out |= 1 << (WIDTH - 1 - j)
    return out


def reflect_table(table: np.ndarray) -> np.ndarray:
    """The rule that acts on a left-right mirrored lattice.

    If s'[i] = s[-i] then the neighbourhood of i in s' is the reverse of the
    neighbourhood of -i in s, so the reflected rule must answer the reversed
    index with the original rule's answer.
    """
    t = require_table(table)
    out = np.empty_like(t)
    for idx in range(TABLE_BITS):
        out[reverse_bits(idx)] = t[idx]
    return out


def complement_table(table: np.ndarray) -> np.ndarray:
    """The rule that acts on a 0-1 exchanged lattice.

    If s'[i] = 1 - s[i] then the neighbourhood index becomes idx ^ 127 and the
    output must be inverted, so out[j] = 1 - t[j ^ 127].
    """
    t = require_table(table)
    out = np.empty_like(t)
    for idx in range(TABLE_BITS):
        out[idx] = 1 - t[idx ^ (TABLE_BITS - 1)]
    return out


def reflect_states(states: np.ndarray) -> np.ndarray:
    """Mirror the ring. Cell i becomes cell -i, so index 0 is held fixed."""
    s = np.asarray(states)
    return np.roll(s[:, ::-1], 1, axis=1)


def complement_states(states: np.ndarray) -> np.ndarray:
    return (1 - np.asarray(states).astype(np.uint8)).astype(np.uint8)


def normalise_trajectory(frames: np.ndarray, reflected: bool = False,
                         complemented: bool = False) -> np.ndarray:
    """Undo a declared orientation so two trajectories are comparable.

    Comparing raw arrays from differently oriented runs is the mistake this
    exists to prevent: two identical dynamics under a mirror produce different
    bytes, and a hash of those bytes would report a broken symmetry.
    """
    out = np.asarray(frames).astype(np.uint8)
    if complemented:
        out = (1 - out).astype(np.uint8)
    if reflected:
        out = np.roll(out[..., ::-1], 1, axis=-1)
    return out


def trajectory_digest(frames: np.ndarray) -> str:
    """Digest of a NORMALISED trajectory. Callers normalise first."""
    a = np.ascontiguousarray(np.asarray(frames).astype(np.uint8))
    h = hashlib.sha256()
    h.update(str(a.shape).encode("ascii"))
    h.update(a.tobytes())
    return "sha256:" + h.hexdigest()


def selected_trajectory(rule_hex: str, n_cells: int, steps: int, seed: int,
                        ic_index: int = 0) -> Dict[str, object]:
    """One declared, fully specified space-time diagram and its digest.

    This is the family's raster and its replay check. Every input that can
    change the bytes is an argument; nothing is defaulted.
    """
    table = decode_table(rule_hex)
    ics = make_ics(ic_index + 1, n_cells, seed)
    frames = evolve(ics[ic_index:ic_index + 1], table, steps, record=True)
    frames = frames[:, 0, :]
    return {"rule_hex": rule_hex, "n_cells": require_lattice(n_cells),
            "steps": require_steps(steps), "seed": int(seed),
            "ic_index": int(ic_index),
            "shape": list(frames.shape),
            "digest": trajectory_digest(frames),
            "frames": frames}


# ---------------------------------------------------------------------------
# The two rules that are derivable from their definitions.
# These are the calibration anchors: they let the bit-order convention be
# re-earned on every test run instead of trusted.
# ---------------------------------------------------------------------------

def majority_rule_table() -> np.ndarray:
    """Simple majority: output 1 iff at least 4 of the 7 cells are 1."""
    out = np.zeros(TABLE_BITS, dtype=np.uint8)
    for idx in range(TABLE_BITS):
        nb = [(idx >> (WIDTH - 1 - j)) & 1 for j in range(WIDTH)]
        out[idx] = 1 if sum(nb) >= (WIDTH + 1) // 2 else 0
    return out


def gkl_rule_table() -> np.ndarray:
    """Gacs-Kurdyumov-Levin, from its definition.

    If the cell is 0 its next state is the majority of cells i, i-1, i-3.
    If the cell is 1 it is the majority of cells i, i+1, i+3.
    """
    out = np.zeros(TABLE_BITS, dtype=np.uint8)
    for idx in range(TABLE_BITS):
        nb = [(idx >> (WIDTH - 1 - j)) & 1 for j in range(WIDTH)]
        centre = nb[RADIUS]
        if centre == 0:
            trio = [nb[RADIUS], nb[RADIUS - 1], nb[0]]
        else:
            trio = [nb[RADIUS], nb[RADIUS + 1], nb[WIDTH - 1]]
        out[idx] = 1 if sum(trio) >= 2 else 0
    return out


# ---------------------------------------------------------------------------
# A third criterion, added 2026-09-10 under operator instruction.
#
# WHY. `stable` and `at_T` are all-or-nothing: the lattice either is in the
# correct uniform configuration or it is not. Measured on the live cs-c3-2
# corpus, 40 of 40 random 128-entry tables scored 0.0 under BOTH, and `maj`
# scored 0.0 under both as well. A criterion whose attainable range for random
# tables is the single point {0} cannot rank a random table, cannot separate
# `maj` from noise, and cannot show a gate to be reachable before it is frozen.
#
# `cellwise_majority_match` is per-cell rather than per-lattice: the fraction
# of cells that agree with the IC's majority target after `steps` updates.
#
# THIS IS NOT COMPARABLE TO THE PUBLISHED FIGURES. The published P values are
# the fraction of INITIAL CONDITIONS classified correctly, all-or-nothing,
# which is `at_T`. Quoting a cell-match number against a published P would be
# comparing two different quantities. The identity in the next paragraph says
# exactly when they coincide and it is the only case where they may be
# compared.
#
# EXACT IDENTITY. For a rule that always reaches a uniform configuration by
# `steps`, every per-IC value is 0 or 1, so the mean cell-match EQUALS the
# at_T accuracy. `maj` is the counterexample: it reaches uniform in 23 of 200
# undriven samples, so its per-IC values are strictly interior and its mean is
# a genuinely different number from its at_T accuracy of 0.0.
# ---------------------------------------------------------------------------

def cellwise_majority_match(table: np.ndarray, ics: np.ndarray, steps: int
                            ) -> Dict[str, object]:
    """Mean fraction of cells matching the IC's majority target at `steps`.

    Returns the mean, the dispersion ACROSS initial conditions, and the mass
    at the two extremes. The dispersion is not decoration: the mean alone
    cannot separate a constant rule from a random one, and the dispersion can.
    See `ATTAINABLE` below.

    ATTAINABLE RANGE. Per initial condition the value lies in [0, 1]. For a
    RANDOM table the mean is centred on 0.5, because a balanced random rule
    drives the lattice to density about one half and each cell then agrees
    with a fixed target with probability about one half. The sampling spread
    of that mean is approximately sqrt(0.25 / n_cells / n_ics); at n_cells 149
    and n_ics 100 that is about 0.004. So the attainable range for random
    tables is an interval around 0.5, not a point, which is the property this
    function exists to provide.

    ANALYTIC EXPECTATIONS, stated before measurement:
        random balanced table   mean about 0.500, small dispersion
        constant-zero rule      mean = P(target = 0) = 0.5 exactly,
                                dispersion = 0.5 exactly, values only 0 or 1
        constant-one rule       the same by symmetry
        perfect classifier      mean 1.0
        perfect anti-classifier mean 0.0

    TWO DISPERSIONS, AND THEY ANSWER DIFFERENT QUESTIONS. `sd_across_ics` is
    the IC-to-IC spread WITHIN one table: about 0.50 for a constant rule and
    about 0.10 for a random one. The spread of the MEAN across many different
    random tables is a separate and much smaller number, about 0.005 at these
    sizes, and it is that second one which makes the attainable range narrow.
    Confusing them is easy; the first version of the test for this function
    did exactly that.

    The two constants land on the SAME MEAN as a random table and are told
    apart only by dispersion. Any ranking built on the mean alone inherits
    that blind spot, and it is stated here rather than discovered later.
    """
    t = require_table(table)
    require_steps(steps)
    s = np.asarray(ics).astype(np.uint8)
    if s.ndim != 2:
        raise EvcaError("ics must be 2-D (n_ics, n_cells), got %r" % (s.shape,))
    n_cells = require_lattice(s.shape[1])
    target = majority_target(s)
    final = evolve(s, t, steps)
    per_ic = (final == target[:, None]).mean(axis=1)
    return {
        "mean_cell_match": float(per_ic.mean()),
        "sd_across_ics": float(per_ic.std()),
        "min_cell_match": float(per_ic.min()),
        "max_cell_match": float(per_ic.max()),
        "fraction_all_cells_match": float((per_ic == 1.0).mean()),
        "fraction_no_cells_match": float((per_ic == 0.0).mean()),
        "n_ics": int(s.shape[0]), "n_cells": n_cells, "steps": int(steps),
        "criterion": "cellwise_majority_match",
        "comparable_to_published_P": False,
        "note": ("equals at_T accuracy ONLY for a rule that always reaches a "
                 "uniform configuration by `steps`"),
    }


def random_table(seed: int) -> np.ndarray:
    """A uniformly random 128-entry table. Seeded; no global RNG."""
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
        raise EvcaError("seed must be an integer, got %r" % (seed,))
    rng = np.random.default_rng(int(seed))
    return rng.integers(0, 2, size=TABLE_BITS).astype(np.uint8)
# ---------------------------------------------------------------------------
# The SYNCHRONISATION task (2026-09-10). A second target for the collider.
#
# PUBLISHED CONVENTION. Density classification asks the lattice to settle into
# the FIXED uniform configuration matching the initial majority. Synchronisation
# asks something different and incompatible: reach a globally synchronous
# period-2 oscillation, every cell alternating in phase, all-zeros then
# all-ones then all-zeros. The task is studied in the same EvCA line
# (Das, Crutchfield, Mitchell and Hanson 1995; Sipper's and later
# Jimenez-Morales, Crutchfield and Mitchell 2001 work on synchronisation).
# Those attributions are RECALLED, not fetched, and are leads.
#
# Unlike density there is no per-IC "correct answer" to compute: every initial
# condition has the same target, a synchronous blink. So the score is the
# fraction of initial conditions that reach it, and there is no majority and
# no tie question.
#
# ANALYTIC EXPECTATIONS, stated before measurement:
#   constant-zero rule   lattice becomes all zeros and STAYS. A fixed point is
#                        not an oscillation, so the score is exactly 0.
#   constant-one rule    the same, exactly 0.
#   random table         reaching a globally synchronous blink by chance is
#                        vanishingly unlikely; expect 0 or near it.
#   the six genomes      these are DENSITY classifiers. They drive the lattice
#                        to a FIXED uniform state, which is the opposite of
#                        oscillating, so expect 0. If any scores above 0 that
#                        is a finding about that rule, not about the task.
# ---------------------------------------------------------------------------

def synchronisation_score(table: np.ndarray, ics: np.ndarray, steps: int
                          ) -> Dict[str, object]:
    """Fraction of initial conditions reaching a synchronous period-2 blink.

    A run SUCCEEDS if the lattice at `steps` and at `steps + 1` are each
    uniform AND differ from each other, so the lattice is alternating in
    phase across the whole ring.

    Checking two consecutive frames is what distinguishes an oscillation from
    a fixed point. A rule that reaches all-zeros and stays there is uniform at
    both frames and identical across them, so it correctly scores 0.
    """
    t = require_table(table)
    require_steps(steps)
    s = np.asarray(ics).astype(np.uint8)
    if s.ndim != 2:
        raise EvcaError("ics must be 2-D (n_ics, n_cells), got %r" % (s.shape,))
    n_cells = require_lattice(s.shape[1])
    a = evolve(s, t, steps)
    b = step(a, t)
    ones_a, ones_b = a.sum(axis=1), b.sum(axis=1)
    uni_a = (ones_a == 0) | (ones_a == n_cells)
    uni_b = (ones_b == 0) | (ones_b == n_cells)
    alternating = uni_a & uni_b & (ones_a != ones_b)
    frozen = uni_a & uni_b & (ones_a == ones_b)
    return {
        "criterion": "synchronisation",
        "score": float(alternating.mean()),
        "fraction_frozen_uniform": float(frozen.mean()),
        "fraction_non_uniform": float((~(uni_a & uni_b)).mean()),
        "n_ics": int(s.shape[0]), "n_cells": n_cells, "steps": int(steps),
        "comparable_to_published_P": False,
        "note": ("a DIFFERENT task from density classification; a density "
                 "classifier drives to a FIXED uniform state and is expected "
                 "to score 0 here"),
    }


def blinker_rule_table() -> np.ndarray:
    """INSTRUMENT-POSITIVE CONTROL for `synchronisation_score`.

    Output = NOT centre. From a UNIFORM initial condition the whole lattice
    alternates in phase forever, which is exactly the synchronous blink the
    task asks for, so the detector must return 1.0 on it.

    This is not a rule that SOLVES synchronisation. Solving it means reaching
    the blink from an ARBITRARY initial condition, and this rule does not: from
    a non-uniform start it just inverts the same non-uniform pattern. It exists
    so that a score of 0.0 everywhere else can be read as a hard task rather
    than a broken measurement.
    """
    t = np.zeros(TABLE_BITS, dtype=np.uint8)
    for idx in range(TABLE_BITS):
        centre = (idx >> (RADIUS)) & 1
        t[idx] = 1 - centre
    return t


# ---------------------------------------------------------------------------
# The synchronisation analogue of `cellwise_majority_match` (2026-09-16,
# Archaeon prompt of 2026-09-11 item 4, backlog L-7 / C-2).
#
# WHY. `synchronisation_score` is all-or-nothing per initial condition, and
# every organism held scores exactly 0.0 on it (CRITERIA.md). Like `at_T` it
# gives a random table the single point {0}, so no gate on it can be shown
# reachable from noise and a 0.0 cannot be separated from an unreachable
# target. This criterion is per CELL, so a random table lands on an interval
# and a rule that is PARTLY synchronising is separable from one that is not.
#
# DEFINITION. Two consecutive frames, a at `steps` and b at `steps + 1`. The
# ring's PHASE at `steps` is the majority state of a (odd N, never a tie). A
# cell is COUNTED if it flips between a and b (locally period 2) AND its state
# in a equals the phase (it is blinking in step with the majority). The per-IC
# value is the fraction of counted cells; the criterion reports its mean and
# dispersion across initial conditions, and the two components separately.
#
# EXACT IDENTITY. A per-IC value of 1.0 holds iff every cell flips and every
# cell equals the phase at `steps`, i.e. iff a is uniform, b is uniform and
# a != b, which is precisely `synchronisation_score`'s success predicate. So
# `fraction_all_cells_sync` EQUALS `synchronisation_score["score"]` exactly,
# on the same ICs and steps, and a test asserts it.
#
# ANALYTIC EXPECTATIONS, stated before any measurement (committed before the
# floor is measured; the measured floor goes in CRITERIA.md in a later commit):
#   constant rules        uniform and fixed at T, so no cell flips: 0.0 EXACTLY,
#                         dispersion 0.
#   blinker, uniform ICs  every cell flips in phase: 1.0 EXACTLY.
#   blinker, k ones of N  every cell flips; the in-phase share is the majority
#                         share, so the per-IC value is max(k, N-k)/N EXACTLY.
#                         This is the CHEAT control: an injected success level
#                         the channel must read to the digit.
#   blinker, random ICs   flip 1.0; mean about 0.5 + sqrt(1/(2 pi N)), which
#                         is the expected majority share (0.533 at N = 149).
#   random table          flip about 0.5, in-phase about the majority share,
#                         roughly independent: mean about 0.27 at N = 149, in a
#                         narrow interval (spread of the mean about 0.005 at
#                         100 ICs). THE FLOOR IS NOT 0 AND NOT 0.5.
#                         [MEASURED 2026-09-16, sync_floor_2026-09-16.json,
#                         20 tables: mean of means 0.227, range [0.057,
#                         0.307], sd of means 0.049. TWO PARTS OF THE LINE
#                         ABOVE WERE WRONG and stay visible: the interval is
#                         ten times wider than predicted, because the flip
#                         fraction is a RULE property (0.11 to 0.57 across
#                         tables, correlation 0.99 with the mean), and the
#                         mean sits 3.5 SE below the independence value
#                         0.266, because flip and in-phase are anticorrelated
#                         (r = -0.79 across tables). The floor is a BAND,
#                         not a point, and an organism is quoted against
#                         its top, 0.31 at this geometry.]
#   density classifiers   the five that reach a fixed uniform state: 0.0
#                         exactly; maj never reaches uniform and its flip
#                         fraction is unknown before measurement.
# ---------------------------------------------------------------------------

def cellwise_synchronisation_match(table: np.ndarray, ics: np.ndarray,
                                   steps: int) -> Dict[str, object]:
    """Mean fraction of cells blinking in phase with the ring at `steps`.

    See the block comment above for the definition, the exact identity with
    `synchronisation_score`, and the expectations stated before measurement.
    NOT comparable to any published figure; `synchronisation_score` is the
    all-or-nothing form and no published P is held for it either (L-7).
    """
    t = require_table(table)
    require_steps(steps)
    s = np.asarray(ics).astype(np.uint8)
    if s.ndim != 2:
        raise EvcaError("ics must be 2-D (n_ics, n_cells), got %r" % (s.shape,))
    n_cells = require_lattice(s.shape[1])
    a = evolve(s, t, steps)
    b = step(a, t)
    phase = majority_target(a)                     # (n,) majority state of a
    flips = a != b                                 # locally period 2
    in_phase = a == phase[:, None]                 # in step with the ring
    counted = flips & in_phase
    per_ic = counted.mean(axis=1)
    return {
        "criterion": "cellwise_synchronisation_match",
        "mean_sync_match": float(per_ic.mean()),
        "sd_across_ics": float(per_ic.std()),
        "min_sync_match": float(per_ic.min()),
        "max_sync_match": float(per_ic.max()),
        "fraction_all_cells_sync": float((per_ic == 1.0).mean()),
        "fraction_no_cells_sync": float((per_ic == 0.0).mean()),
        "mean_flip_fraction": float(flips.mean(axis=1).mean()),
        "mean_phase_match": float(in_phase.mean(axis=1).mean()),
        "n_ics": int(s.shape[0]), "n_cells": n_cells, "steps": int(steps),
        "comparable_to_published_P": False,
        "note": ("per-cell form of the synchronisation task; "
                 "fraction_all_cells_sync equals synchronisation_score "
                 "exactly on the same ICs and steps"),
    }
