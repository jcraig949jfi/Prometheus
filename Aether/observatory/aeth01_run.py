"""Build an AETH-01 initial lattice and run a world under observation.

One implementation, used by both the local CPU scout and the A40
first-light runner, so a scout result and a pod result cannot come from
two subtly different worlds.

PROVENANCE IS THE POINT, not a formality. EXPERIMENTS.md item 5
requires that the exact recipe for every initial state be logged, not
described in prose, so a contamination investigation can reconstruct
precisely what ran. `build_initial` therefore returns the lattice AND a
recipe dict that contains every input it consumed plus a digest of what
it produced, and `verify_recipe` rebuilds the lattice from the recipe
alone and checks the digest.

INSTRUMENT CLASS. EXPERIMENTS.md: `SPONTANEOUS` only if the entire
initial content comes from unstructured generation (regimes 1-2);
`SEEDED_CONTROL` if any hand-authored functional pattern is present
anywhere. This module can only build regimes 1-2, so it only ever emits
`SPONTANEOUS`, and it says so in the recipe rather than leaving the
field for a caller to fill in optimistically. Nothing here can produce
a seeded control, by construction.

The class tag lives only in run metadata. It is never written into the
lattice bytes and no site can read it (R1, R10).
"""

import hashlib
import time

import numpy as np

from observatory import aeth01_observatory as obs

WRITE_OPCODE = 0x01

# EXPERIMENTS.md regimes 1 and 2. Both are unstructured generation.
RANDOM_SOUP = "random_soup"          # regime 1
SPARSE_SOUP = "sparse_soup"          # regime 2

# Regime 5/6 overlays: initial energy content only. These are overlays,
# not origins -- they carry no instrument_class of their own.
ENERGY_UNIFORM = "uniform"           # 0..255
ENERGY_RICH = "rich"                 # regime 5
ENERGY_POOR = "poor"                 # regime 6


def build_initial(regime, h, w, rng_seed, write_density=None,
                  energy_mode=ENERGY_UNIFORM):
    """Return (fields, recipe). Deterministic in (regime, h, w, rng_seed, ...)."""
    rng = np.random.default_rng(rng_seed)

    if regime == RANDOM_SOUP:
        # Every field iid uniform over its full byte range: WRITE lands
        # at ~1/256 by construction, not by choice.
        opcode = rng.integers(0, 256, size=(h, w), dtype=np.uint8)
        effective_density = None
    elif regime == SPARSE_SOUP:
        if write_density is None:
            raise ValueError("sparse_soup needs an explicit write_density")
        # Non-WRITE background drawn from the non-WRITE bytes, so the
        # background is still unstructured rather than a constant that
        # would itself be a hand-authored pattern.
        background = rng.integers(0, 255, size=(h, w), dtype=np.uint8)
        background = np.where(background >= WRITE_OPCODE,
                              background + np.uint8(1), background).astype(np.uint8)
        is_write = rng.random((h, w)) < write_density
        opcode = np.where(is_write, np.uint8(WRITE_OPCODE), background).astype(np.uint8)
        effective_density = float(is_write.mean())
    else:
        raise ValueError("unknown regime %r (this module builds only the "
                         "unstructured regimes 1-2)" % (regime,))

    arg0 = rng.integers(0, 256, size=(h, w), dtype=np.uint8)
    arg1 = rng.integers(0, 256, size=(h, w), dtype=np.uint8)
    payload = rng.integers(0, 256, size=(h, w), dtype=np.uint8)

    if energy_mode == ENERGY_UNIFORM:
        energy = rng.integers(0, 256, size=(h, w), dtype=np.uint8)
    elif energy_mode == ENERGY_RICH:
        energy = rng.integers(224, 256, size=(h, w), dtype=np.uint8)
    elif energy_mode == ENERGY_POOR:
        energy = rng.integers(0, 32, size=(h, w), dtype=np.uint8)
    else:
        raise ValueError("unknown energy_mode %r" % (energy_mode,))

    fields = [opcode, arg0, arg1, payload, energy]
    recipe = {
        "regime": regime,
        "h": h, "w": w,
        "rng_seed": int(rng_seed),
        "write_density_requested": write_density,
        "write_density_realized": effective_density,
        "energy_mode": energy_mode,
        "generator": "numpy.random.default_rng",
        "generator_call_order": ["opcode", "arg0", "arg1", "payload", "energy"],
        "instrument_class": "SPONTANEOUS",
        "initial_state_digest": obs.state_digest(fields),
        "initial_write_sites": int((opcode == WRITE_OPCODE).sum()),
    }
    return fields, recipe


def verify_recipe(recipe):
    """Rebuild from the recipe alone; return True if the digest matches.

    A recipe that cannot reproduce its own lattice is not provenance,
    it is a description. Run before trusting any run's origin claim.
    """
    fields, rebuilt = build_initial(
        recipe["regime"], recipe["h"], recipe["w"], recipe["rng_seed"],
        write_density=recipe.get("write_density_requested"),
        energy_mode=recipe.get("energy_mode", ENERGY_UNIFORM))
    return rebuilt["initial_state_digest"] == recipe["initial_state_digest"]


def run_world(xp, gpu_step, fields, params, ticks,
              sample_every=10, deep_every=100, map_every=100,
              tick0=0, progress=None):
    """Run one world, sampling the observatory as it goes.

    `params` is the five run parameters plus the physics seed. Cheap
    counters are taken every tick; the fuller sample every
    `sample_every`; compression and the exact state digest every
    `deep_every`; coarse spatial maps every `map_every`.

    Returns (final_fields, series, maps, meta). `series` is a list of
    per-sample dicts, always carrying `tick`, so a gap in sampling is
    visible as a gap rather than being interpolated away.
    """
    device = [xp.asarray(f) for f in fields]
    write_cost = params["write_cost"]
    series, maps = [], []
    prev = [f.copy() for f in device]
    started = time.time()

    for step in range(ticks):
        tick = tick0 + step
        result = gpu_step(params["h"], params["w"], params["seed"], tick,
                          write_cost, params["maintenance_cost"],
                          params["replenish_numer"], params["replenish_amount"],
                          params["mut_numer"], *device)
        device = list(result[:5])

        want_full = (step % sample_every == 0) or (step == ticks - 1)
        if not want_full:
            continue
        want_deep = (step % deep_every == 0) or (step == ticks - 1)
        want_maps = (step % map_every == 0) or (step == ticks - 1)
        row = obs.sample(xp, device, write_cost,
                         want_compression=want_deep, want_maps=want_maps)
        rate, per_field = obs.change_rate(xp, prev, device)
        row["change_rate"] = rate
        row["change_rate_by_field"] = per_field
        row["tick"] = tick + 1
        captured = row.pop("_maps", None)
        if captured is not None and captured.get("energy") is not None:
            maps.append({"tick": tick + 1,
                         "energy": captured["energy"],
                         "write": captured["write"]})
        series.append(row)
        prev = [f.copy() for f in device]
        if progress is not None:
            progress(tick + 1, row)

    host = [np.asarray(getattr(f, "get", lambda: f)()) for f in device]
    meta = {
        "ticks_run": ticks,
        "tick0": tick0,
        "wall_seconds": time.time() - started,
        "final_state_digest": obs.state_digest(host),
        "samples": len(series),
    }
    return host, series, maps, meta
