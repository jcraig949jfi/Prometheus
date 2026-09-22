"""AETH-01 tier-1 observatory: measurement only, no interpretation.

Implements the "Measurable quantities" of `Aether/AETH-01/HABITABILITY.md`
that are cheap enough to sample during a long run. It computes numbers
about a lattice. It does NOT label a world, decide whether something is
an assembly, or claim anything fired.

WHAT IS DELIBERATELY NOT HERE
  - `component_track` and `perturbation_divergence`. The first needs
    torus-aware connected components with frame-to-frame matching, the
    second needs a second run of the same world with one bit flipped.
    Both are deepen-tier (HABITABILITY.md), and a cheap wrong version
    of either is worse than none, because it would produce numbers that
    look like structure tracking.
  - Every detector in the claim ladder (`scientific_aeth01.py`
    CLAIM_TIERS). Nothing here reports construction, transmission or
    heredity, and no output of this module may be read as evidence for
    any of them.

WHAT THE OBSERVATORY MUST NOT BE ABLE TO DO
  It is outside the universe (AETHER_CONCEPT.md): it only reads the
  five lattice fields and never writes them. Every function here takes
  arrays and returns scalars or small summaries; none returns a lattice
  and none is given one to modify. `read_only_guard` in the tests
  checks the arrays are unchanged after a full measurement pass.

BACKEND
  `xp` is numpy or cupy. Reductions return host floats/ints so a caller
  never accidentally keeps a device array per tick for 5,000 ticks.
"""

import hashlib
import zlib

import numpy as np

OPCODE, ARG0, ARG1, PAYLOAD, ENERGY = 0, 1, 2, 3, 4
FIELD_NAMES = ("opcode", "arg0", "arg1", "payload", "energy")
WRITE_OPCODE = 0x01


def _host(value):
    """Device scalar -> host float, without importing cupy."""
    return float(getattr(value, "get", lambda: value)())


def _host_int(value):
    return int(getattr(value, "get", lambda: value)())


def histogram256(xp, field):
    """Exact 256-bin value histogram of one uint8 field, as host ints.

    Every distribution statistic below is derived from this rather than
    from the lattice, so an H*W reduction happens once per field per
    sample instead of once per statistic.
    """
    counts = xp.bincount(field.ravel(), minlength=256)
    return np.asarray(getattr(counts, "get", lambda: counts)(), dtype=np.int64)


def entropy_bits(counts):
    """Shannon entropy of an empirical byte distribution, in bits.

    0.0 means one byte value covers the lattice (HABITABILITY.md's
    HOMOGENIZED signature); 8.0 means uniform over all 256 values.
    """
    total = counts.sum()
    if total <= 0:
        return 0.0
    p = counts[counts > 0].astype(np.float64) / float(total)
    return float(-(p * np.log2(p)).sum())


def gini_from_counts(counts):
    """Exact Gini coefficient from a 256-bin histogram.

    Energy is uint8, so the full pairwise mean absolute difference is a
    256x256 sum rather than an O(n log n) sort of H*W values -- exact,
    and cheap enough to sample often. Returns 0.0 for an all-zero
    lattice (no concentration is definable when there is nothing to
    concentrate), which is reported alongside energy_total so the two
    cases are distinguishable.
    """
    total = counts.sum()
    if total <= 0:
        return 0.0
    values = np.arange(256, dtype=np.float64)
    mean = float((counts * values).sum()) / float(total)
    if mean <= 0:
        return 0.0
    diff = np.abs(values[:, None] - values[None, :])
    pair_sum = float((counts[:, None] * counts[None, :] * diff).sum())
    return pair_sum / (2.0 * float(total) * float(total) * mean)


def spatial_autocorr(xp, field):
    """Mean Pearson correlation between a site and its 4 neighbours.

    Uses `xp.roll`, the same toroidal permutation the kernel gathers
    with, so the wrap is the lattice's real topology and not an edge
    artifact. Returns 0.0 for a constant field, where correlation is
    undefined rather than perfect -- reported next to the field's
    entropy, which is what says "constant".
    """
    x = field.astype(xp.float64)
    n = x.size
    mean = x.sum() / n
    centered = x - mean
    var = _host((centered * centered).sum()) / n
    if var <= 0.0:
        return 0.0
    total = 0.0
    for shift, axis in ((1, 0), (-1, 0), (1, 1), (-1, 1)):
        rolled = xp.roll(centered, shift, axis=axis)
        total += _host((centered * rolled).sum()) / n
    return total / (4.0 * var)


def compression_ratio(fields):
    """zlib size of the lattice bytes over zlib size of random bytes.

    HABITABILITY.md's cheap structure proxy. Near 1.0 means "as
    incompressible as noise"; well below 1.0 means repeated structure.
    The random baseline is computed at the same byte length with a
    fixed seed, so the ratio is comparable across samples and worlds.
    Host-side: the arrays are brought over by the caller.
    """
    raw = b"".join(np.ascontiguousarray(f).tobytes() for f in fields)
    if not raw:
        return 0.0
    packed = len(zlib.compress(raw, 6))
    baseline = _random_baseline_size(len(raw))
    return float(packed) / float(baseline) if baseline else 0.0


_BASELINE_CACHE = {}


def _random_baseline_size(n):
    """Compressed size of n iid random bytes, memoised.

    Deterministic in n, and n is the same on every sample of a given
    lattice, so recomputing it per sample would regenerate and compress
    tens of megabytes of noise for an answer already known.
    """
    if n not in _BASELINE_CACHE:
        noise = np.random.default_rng(0xA37E).integers(
            0, 256, size=n, dtype=np.uint8).tobytes()
        _BASELINE_CACHE[n] = len(zlib.compress(noise, 6))
    return _BASELINE_CACHE[n]


def state_digest(fields):
    """sha256 over the five fields, for exact-recurrence detection.

    A standard hash over the real bytes rather than a cheap invented
    fingerprint, because a fingerprint collision would look exactly like
    a recurrence. HABITABILITY.md's PERIODIC label additionally requires
    forward-trajectory agreement, since Mu and Rho hash the tick: equal
    lattices at different ticks do NOT imply equal successors. A digest
    match here is therefore a CANDIDATE, never a confirmed period.
    """
    h = hashlib.sha256()
    for f in fields:
        h.update(np.ascontiguousarray(f).tobytes())
    return h.hexdigest()[:32]


def coarse_map(xp, field, blocks=128):
    """Block-mean downsample to blocks x blocks, as a float32 host array.

    Keeps spatial organization observable across a whole run at ~64 KB
    per sample instead of ~84 MB, so gradients, seams, patches and
    fronts survive in the record even where full snapshots cannot.
    Returns None when the lattice does not divide evenly, rather than
    silently cropping.
    """
    h, w = field.shape
    if h % blocks or w % blocks:
        return None
    bh, bw = h // blocks, w // blocks
    reduced = field.astype(xp.float32).reshape(blocks, bh, blocks, bw).mean(axis=(1, 3))
    return np.asarray(getattr(reduced, "get", lambda: reduced)(), dtype=np.float32)


def cheap_counters(xp, fields, write_cost):
    """Per-tick scalars cheap enough for every single tick.

    activity_density here is recomputed rather than taken from the
    kernel's own counters dict, so the observatory does not depend on
    the thing it observes reporting on itself.
    """
    opcode, energy = fields[OPCODE], fields[ENERGY]
    n = float(opcode.size)
    is_write = opcode == WRITE_OPCODE
    write_sites = _host_int(is_write.sum())
    starved = _host_int((is_write & (energy.astype(xp.int64) < write_cost)).sum())
    return {
        "write_density": write_sites / n,
        "starved_density": starved / n,
        "activity_density": (write_sites - starved) / n,
        "energy_total": _host_int(energy.astype(xp.int64).sum()),
    }


def change_rate(xp, before, after):
    """Fraction of (site, field) pairs whose stored bits changed.

    HABITABILITY.md defines this over the required per-event trace. No
    trace exists, and a consecutive-state difference is EXACTLY
    equivalent for it: each (site, field) has at most one winning write
    per tick, so "the stored bits changed" and "the value differs from
    last tick" are the same predicate. A same-value write is therefore
    correctly NOT counted as a change by either definition. What this
    proxy cannot see, and the trace could, is HOW MANY proposals lost.
    """
    changed = 0
    per_field = {}
    for i, (b, a) in enumerate(zip(before, after)):
        c = _host_int((b != a).sum())
        per_field[FIELD_NAMES[i]] = c / float(b.size)
        changed += c
    return changed / float(before[0].size * len(before)), per_field


def sample(xp, fields, write_cost, want_compression=False,
           want_maps=False, map_blocks=128):
    """One full observatory sample. Returns plain JSON-able values.

    Nothing here is a verdict. Every key is a measured quantity, and
    the labels in HABITABILITY.md are applied later, by a human reading
    these numbers, not by this function.
    """
    opcode, payload, energy = fields[OPCODE], fields[PAYLOAD], fields[ENERGY]
    hist_opcode = histogram256(xp, opcode)
    hist_payload = histogram256(xp, payload)
    hist_energy = histogram256(xp, energy)

    out = dict(cheap_counters(xp, fields, write_cost))
    out.update({
        "entropy_opcode_bits": entropy_bits(hist_opcode),
        "entropy_payload_bits": entropy_bits(hist_payload),
        "entropy_energy_bits": entropy_bits(hist_energy),
        "energy_gini": gini_from_counts(hist_energy),
        "energy_zero_fraction": float(hist_energy[0]) / float(energy.size),
        "energy_saturated_fraction": float(hist_energy[255]) / float(energy.size),
        "energy_mean": float((hist_energy * np.arange(256)).sum()) / float(energy.size),
        "opcode_modal_fraction": float(hist_opcode.max()) / float(opcode.size),
        "distinct_opcodes": int((hist_opcode > 0).sum()),
        "autocorr_opcode": spatial_autocorr(xp, opcode),
        "autocorr_payload": spatial_autocorr(xp, payload),
        "autocorr_energy": spatial_autocorr(xp, energy),
    })
    if want_compression or want_maps:
        host_fields = [np.asarray(getattr(f, "get", lambda: f)()) for f in fields]
        if want_compression:
            out["compression_ratio"] = compression_ratio(host_fields)
            out["state_digest"] = state_digest(host_fields)
    if want_maps:
        out["_maps"] = {
            "energy": coarse_map(xp, energy, blocks=map_blocks),
            "write": coarse_map(xp, (opcode == WRITE_OPCODE).astype(xp.uint8) * 255,
                                blocks=map_blocks),
        }
    return out
