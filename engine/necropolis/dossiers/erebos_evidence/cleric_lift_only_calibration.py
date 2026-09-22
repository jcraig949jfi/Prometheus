"""cleric_lift_only_calibration.py -- ONE question (Cleric attack on the
MEASUREMENT layer of erebos.dossier.json):

    The Necromancer's calibration planted a PARTNER-CONDITIONED kill
    pattern (A's kp fixed whenever A shares a signature with B).  Both the
    pair-aware counter and the lift substrate capture that class, so the
    substrate-vs-pair-aware delta count is zero BY CONSTRUCTION, not by
    lack of power.  The dossier itself lists "a lift-only signal class was
    not tried" as a scope limit.  This script tries it.

Method: import the committed harness unchanged (same monkeypatch as the
Necromancer's script: only `_load_real_rows` is replaced) and plant a
LIFT-ONLY signal, i.e. the class of structure the Phase 3.E claim was
actually about: on signatures shared with partner B, plugin A emits a
GLOBALLY RARE kp a minority of the time and its GLOBALLY COMMON kp the
majority of the time.  A count-max counter recommends the common kp; a
lift-max substrate recommends the rare kp.  Each planted pair therefore
yields exactly one substrate-vs-pair-aware delta if the instrument can
see it.  Worlds: NULL (no plant), LIFT2 (two planted pairs), LIFT3
(three planted pairs).  Same 699 rows, 14 plugins, 6 kill patterns,
230 signatures as the Necromancer's script.  Deterministic, offline.

If LIFT2/LIFT3 clear p<0.05 the statistic has resolution at N=699 for
the class it was built to test, and the historical observed=2 (p=0.105)
is a weak negative about the data, not an instrument floor.  If they do
not, the Necromancer's "no resolution in this regime" generalises.

Writes cleric_lift_only_calibration_result.json next to this file, from
Python, flushed per run.  Pure ASCII.  Repo root resolved from __file__
(no drive letters; EREBOS_REPO env var overrides for scratch runs).
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ["EREBOS_REPO"]) if os.environ.get("EREBOS_REPO") else HERE.parents[3]
sys.path.insert(0, str(REPO))

import charon.agents.erebos.sprint1.phase3.pair_aware_permutation_null as H  # noqa: E402

PLUGINS = ["g02_contrast", "g03_failure_neighborhood", "g04_survivor_tightening",
           "g09_projection_collapse", "g10_boundary", "g11_exception_miner",
           "g15_cross_gen_mi", "g16_anti_anchor", "g17_causal_intervention",
           "g18_minimal_counterexample", "g19_proof_obligation",
           "g23_asymptotic_limit", "g24_symmetry_twist", "g25_degeneracy"]
KPS = ["permutation_null", "residual_survival", "threshold_artifact",
       "coverage_gap", None, "boundary_artifact"]
N_ROWS = 699
N_SIGS = 230
N_SHARED = 12          # shared signatures per planted pair
RARE_ON_SHARED = 5     # of the 12 shared, A emits the rare kp this many times
COMMON_ELSEWHERE = 0.85

# (A, B, A_common_kp, A_rare_kp, B_fixed_kp)
PLANTS = [
    ("g02_contrast", "g10_boundary", "threshold_artifact", "boundary_artifact", "permutation_null"),
    ("g23_asymptotic_limit", "g24_symmetry_twist", "residual_survival", "coverage_gap", "threshold_artifact"),
    ("g15_cross_gen_mi", "g16_anti_anchor", "permutation_null", "residual_survival", "coverage_gap"),
]


def synthetic_rows(seed: int, n_plants: int) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    for i in range(N_ROWS):
        rows.append({"row_id": f"r{i}", "plugin_id": rng.choice(PLUGINS),
                     "kill_pattern": rng.choice(KPS), "domain": "mahler",
                     "input_signature": f"sig-{rng.randrange(N_SIGS)}"})
    for k, (a, b, common, rare, b_kp) in enumerate(PLANTS[:n_plants]):
        a_rows = [r for r in rows if r["plugin_id"] == a]
        b_rows = [r for r in rows if r["plugin_id"] == b]
        for r in b_rows:
            r["kill_pattern"] = b_kp
        for r in a_rows:
            r["kill_pattern"] = common if rng.random() < COMMON_ELSEWHERE else rng.choice(KPS)
        rng.shuffle(a_rows)
        rng.shuffle(b_rows)
        n = min(N_SHARED, len(a_rows), len(b_rows))
        for j in range(n):
            sig = f"plant{k}-{j}"
            a_rows[j]["input_signature"] = sig
            b_rows[j]["input_signature"] = sig
            a_rows[j]["kill_pattern"] = rare if j < RARE_ON_SHARED else common
    return rows


def run_world(world: str, n_plants: int, seed: int) -> dict:
    rows = synthetic_rows(seed, n_plants)
    H._load_real_rows = lambda include_enriched=True: rows   # instrument unchanged
    # Direct read of the two recommendation maps on the unshuffled rows,
    # so the reader can see WHICH cells disagree (not just how many).
    sub = H._substrate_recs(rows)
    pair = H.pair_aware_counter_recommendations(rows)
    disagreements = sorted(
        f"{plugin} | given {partner} : substrate={kp} pair_counter={pair.get((plugin, partner))}"
        for (plugin, partner), kp in sub.items()
        if pair.get((plugin, partner)) != kp)
    t0 = time.time()
    res = H.run_pair_aware_permutation_null()
    d = {k: getattr(res, k) for k in dir(res) if not k.startswith("_")
         and not callable(getattr(res, k))}
    d = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()
         if isinstance(v, (int, float, str, bool)) or v is None}
    d.update({"world": world, "n_plants": n_plants, "seed": seed, "n_rows": len(rows),
              "n_substrate_recs": len(sub), "n_pair_recs": len(pair),
              "unshuffled_disagreements": disagreements,
              "elapsed_s": round(time.time() - t0, 1)})
    p95 = d.get("null_p95")
    d["min_observed_to_clear_p05"] = (p95 + 1) if isinstance(p95, (int, float)) else None
    return d


def main() -> int:
    out_path = HERE / "cleric_lift_only_calibration_result.json"
    out = {"question": __doc__.strip().splitlines()[0],
           "harness": "charon/agents/erebos/sprint1/phase3/pair_aware_permutation_null.py",
           "harness_constants": {"N_PERMUTATIONS": H.N_PERMUTATIONS, "SEED": H.SEED,
                                 "MIN_COOCCURRENCE": H.MIN_COOCCURRENCE,
                                 "MIN_LIFT": H.MIN_LIFT},
           "plant_design": {"n_shared_sigs_per_pair": N_SHARED,
                            "rare_kp_on_shared": RARE_ON_SHARED,
                            "common_kp_prob_elsewhere": COMMON_ELSEWHERE,
                            "pairs": PLANTS},
           "historical_quote_phase3K": {"observed_deltas_vs_pair": 2, "null_p95": 2,
                                        "p_value": 0.105, "source":
               "pivot/sprint1/phase3/PHASE3_K_PAIR_AWARE_NULL_VERDICT_2026-06-03.md"},
           "runs": []}

    def flush() -> None:
        out_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="ascii")

    flush()
    for world, n_plants in (("NULL", 0), ("LIFT2", 2), ("LIFT3", 3)):
        for seed in (11, 23, 37):
            r = run_world(world, n_plants, seed)
            out["runs"].append(r)
            flush()
            print(world, seed, {k: r.get(k) for k in (
                "observed_deltas_vs_pair", "observed_deltas_vs_plugin", "null_mean",
                "null_p95", "p_value", "verdict", "min_observed_to_clear_p05")})
            for line in r["unshuffled_disagreements"]:
                print("    ", line)
    summ = {}
    for world in ("NULL", "LIFT2", "LIFT3"):
        rs = [r for r in out["runs"] if r["world"] == world]
        summ[world] = {"observed": [r.get("observed_deltas_vs_pair") for r in rs],
                       "null_p95": [r.get("null_p95") for r in rs],
                       "null_mean": [r.get("null_mean") for r in rs],
                       "p_values": [r.get("p_value") for r in rs],
                       "detected_at_p05": sum(1 for r in rs if (r.get("p_value") or 1) < 0.05)}
    summ["reading"] = ("If LIFT2 and LIFT3 are detected at p<0.05 while NULL is not, the "
                       "committed statistic HAS resolution at N=699 for the lift-vs-count class "
                       "the Phase 3.E claim named, and the historical observed=2 / p=0.105 is a "
                       "weak negative about the data rather than an instrument floor.")
    out["summary"] = summ
    flush()
    print(json.dumps(summ, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
