"""Free local CPU scout: where is aeth01.v1 dynamically alive at all?

HABITABILITY.md asks this question before any question about
organization, and answers it with the scout -> qualify -> deepen funnel
(GPU_RUNPOD.md). This is the scout tier, run on CPU at small size for
no money, so that a paid A40 run is aimed at parameters that are known
not to be trivially dead rather than at a guess.

It sweeps the three ECONOMICS.md resource regimes against initial WRITE
density and perturbation rate, and prints the measured quantities. It
does NOT assign a HABITABILITY.md label: labels are applied by a person
reading these numbers, and `UNKNOWN` is a first-class outcome.

    python Aether/observatory/aeth01_scout.py <repo-root> [out.jsonl]
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
sys.path.insert(0, str(ROOT / "Aether"))

from observatory import aeth01_run as runner            # noqa: E402
from observatory import aeth01_observatory as obs       # noqa: E402

sys.path.insert(0, str(ROOT / "Aether" / "test"))
from reference.gpu_aeth01 import gpu_step               # noqa: E402

SIZE = 128
TICKS = 1500
SAMPLE_EVERY = 10
DEEP_EVERY = 250
PHYSICS_SEED = 0x5C0117

P32 = 1 << 32  # REPLENISH_NUMER / 2**32 and MUT_NUMER / 2**32 are probabilities.


def prob(p):
    return int(round(p * P32))


# ---------------------------------------------------------------- round 1
# ECONOMICS.md's three resource regimes exactly as written there, against
# EXPERIMENTS.md regimes 1-2. Result: all 18 configs freeze or starve.
ROUND1_REGIMES = {
    "A_execution_only": dict(write_cost=1, maintenance_cost=0,
                             replenish_numer=0, replenish_amount=0),
    "B_maintenance": dict(write_cost=1, maintenance_cost=1,
                          replenish_numer=prob(0.001), replenish_amount=8),
    "C_free_compute": dict(write_cost=0, maintenance_cost=0,
                           replenish_numer=0, replenish_amount=0),
}
ROUND1_INITS = [
    ("regime1_random_soup", runner.RANDOM_SOUP, None),
    ("regime2_sparse_2pct", runner.SPARSE_SOUP, 0.02),
    ("regime2_sparse_10pct", runner.SPARSE_SOUP, 0.10),
]
ROUND1_MUTATION = [("mut_off", 0), ("mut_1e-3", prob(0.001))]

# ---------------------------------------------------------------- round 2
# Round 1 found two scale-invariant reasons nothing happens:
#   (a) regime A starves -- writers exhaust their OWN energy in ~E/w ticks
#       while 99.65% of the world's energy is locked in non-WRITE sites
#       that can never spend or transfer it;
#   (b) regime C freezes at a fixed point -- a writer's output is a
#       constant function of its own unchanging bytes, so every target
#       reaches its value in one tick and 1,585 active writers produce
#       2.0 changed site-field pairs per tick.
# Round 2 attacks both: keep writers solvent, and sweep the ONE mechanism
# that continuously injects new values into the write stream. Round 1
# swept perturbation only to 1e-3; the physics allows up to 1.0.
ROUND2_REGIMES = {
    # No energy constraint at all: isolates the fixed-point question
    # from the starvation question.
    "C_free_compute": dict(write_cost=0, maintenance_cost=0,
                           replenish_numer=0, replenish_amount=0),
    # Writers stay solvent: cost to act, no decay, steady rain.
    "A_fed": dict(write_cost=1, maintenance_cost=0,
                  replenish_numer=prob(0.01), replenish_amount=4),
    # ECONOMICS.md regime B with inflow actually balanced against
    # outflow: MAINTENANCE_COST=1 drains 1.0/site/tick, so the rain must
    # deliver ~1.0/site/tick. Its own example (0.001 x 8 = 0.008) is
    # 125x short, which is why round 1's regime B collapsed to 0.03% of
    # its initial energy.
    "B_balanced": dict(write_cost=1, maintenance_cost=1,
                       replenish_numer=prob(0.125), replenish_amount=8),
}
ROUND2_INITS = [
    ("regime2_sparse_10pct", runner.SPARSE_SOUP, 0.10),
    ("regime2_sparse_50pct", runner.SPARSE_SOUP, 0.50),
]
ROUND2_MUTATION = [("mut_1e-2", prob(0.01)), ("mut_1e-1", prob(0.1)),
                   ("mut_5e-1", prob(0.5))]

ROUNDS = {
    "1": (ROUND1_REGIMES, ROUND1_INITS, ROUND1_MUTATION),
    "2": (ROUND2_REGIMES, ROUND2_INITS, ROUND2_MUTATION),
}


def summarize(series):
    """Trailing-window behaviour, as measured. No labels."""
    tail = series[len(series) // 2:] or series
    first, last = series[0], series[-1]

    def col(key):
        return [row[key] for row in tail if key in row]

    activity = col("activity_density")
    change = col("change_rate")
    digests = [row["state_digest"] for row in series if "state_digest" in row]
    return {
        "activity_first": first["activity_density"],
        "activity_last": last["activity_density"],
        "activity_tail_mean": float(np.mean(activity)) if activity else 0.0,
        "activity_tail_max": float(np.max(activity)) if activity else 0.0,
        "change_tail_mean": float(np.mean(change)) if change else 0.0,
        "change_tail_max": float(np.max(change)) if change else 0.0,
        "entropy_opcode_first": first["entropy_opcode_bits"],
        "entropy_opcode_last": last["entropy_opcode_bits"],
        "opcode_modal_last": last["opcode_modal_fraction"],
        "distinct_opcodes_last": last["distinct_opcodes"],
        "energy_total_first": first["energy_total"],
        "energy_total_last": last["energy_total"],
        "energy_gini_last": last["energy_gini"],
        "energy_zero_frac_last": last["energy_zero_fraction"],
        "autocorr_opcode_last": last["autocorr_opcode"],
        "compression_last": last.get("compression_ratio"),
        "repeated_state_digest": len(digests) != len(set(digests)),
        "write_density_last": last["write_density"],
        "starved_density_last": last["starved_density"],
    }


def main():
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("scout.jsonl")
    round_id = sys.argv[3] if len(sys.argv) > 3 else "1"
    regimes, inits, mutation = ROUNDS[round_id]
    rows = []
    configs = [(rn, rp, inm, ini, dens, mn, mv)
               for rn, rp in regimes.items()
               for inm, ini, dens in inits
               for mn, mv in mutation]
    print("scout round %s: %d configs, %d^2 lattice, %d ticks each"
          % (round_id, len(configs), SIZE, TICKS), flush=True)
    t_all = time.time()

    with out_path.open("w", encoding="utf-8") as fh:
        for i, (rname, rparams, iname, iregime, density, mname, mval) in enumerate(configs, 1):
            fields, recipe = runner.build_initial(
                iregime, SIZE, SIZE, rng_seed=0xA37E, write_density=density)
            assert runner.verify_recipe(recipe), "recipe does not rebuild its own lattice"
            params = dict(rparams)
            params.update(h=SIZE, w=SIZE, seed=PHYSICS_SEED, mut_numer=mval)
            t0 = time.time()
            _final, series, _maps, meta = runner.run_world(
                np, gpu_step, fields, params, TICKS,
                sample_every=SAMPLE_EVERY, deep_every=DEEP_EVERY,
                map_every=TICKS + 1)
            row = {
                "config": "%s | %s | %s" % (rname, iname, mname),
                "round": round_id,
                "regime": rname, "init": iname, "mutation": mname,
                "params": {k: v for k, v in params.items()},
                "recipe": recipe,
                "meta": meta,
                "summary": summarize(series),
            }
            rows.append(row)
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            s = row["summary"]
            print("[%2d/%2d] %-46s act %.5f->%.5f tail %.5f  chg %.6f  "
                  "Hop %.2f->%.2f  E %d->%d  %.0fs"
                  % (i, len(configs), row["config"], s["activity_first"],
                     s["activity_last"], s["activity_tail_mean"],
                     s["change_tail_mean"], s["entropy_opcode_first"],
                     s["entropy_opcode_last"], s["energy_total_first"],
                     s["energy_total_last"], time.time() - t0), flush=True)

    print("\ntotal %.0fs -> %s" % (time.time() - t_all, out_path), flush=True)


if __name__ == "__main__":
    main()
