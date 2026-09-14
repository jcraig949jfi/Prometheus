"""erebos_null_instrument_calibration.py -- ONE question:

    The "0 permutation-null survivors" verdict (Phase 3.K, 2026-06-03)
    rests on pair_aware_permutation_null.py reporting observed=2 deltas
    against a null with p95=2 (p=0.105). The real 699-row ledger it ran
    on is gone from this host. Can the INSTRUMENT itself be exercised
    today, and what is its resolution floor on ledgers of that size --
    i.e. is "observed=2, p=0.105" a property of the data or of the
    instrument?

Method: import the committed harness unchanged and monkeypatch only
its `_load_real_rows` with synthetic ledgers of the same size (699 rows)
and comparable cardinality (14 plugins with loaders, ~6 kill patterns
per plugin, ~230 input signatures). Two worlds:
  NULL    -- kill_pattern independent of partner cells (no linkage).
  PLANTED -- for two plugin pairs, the kill pattern of A is fixed by the
             partner cell B on shared signatures (strong linkage).
For each world and several seeds the harness's own p-value, null mean,
null p95 and observed count are recorded, plus the smallest observed
count that would have cleared p<0.05 (null_p95 + 1). This does NOT
re-measure Erebos; it measures the instrument. Deterministic, offline.

Writes erebos_null_instrument_calibration_result.json next to this file.
Pure ASCII. Repo root resolved from __file__ (no drive letters).
"""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
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


def synthetic_rows(seed: int, planted: bool) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    for i in range(N_ROWS):
        plugin = rng.choice(PLUGINS)
        sig = f"sig-{rng.randrange(N_SIGS)}"
        kp = rng.choice(KPS)
        rows.append({"row_id": f"r{i}", "plugin_id": plugin, "kill_pattern": kp,
                     "domain": "mahler", "input_signature": sig})
    if planted:
        # Linkage: whenever g02 shares a signature with g10, g02's kp is
        # forced to boundary_artifact; whenever g23 shares with g24, g23's
        # kp is forced to coverage_gap. Overall g02/g23 majorities differ.
        by_sig: dict[str, list[dict]] = {}
        for r in rows:
            by_sig.setdefault(r["input_signature"], []).append(r)
        for sig, group in by_sig.items():
            plugins_here = {r["plugin_id"] for r in group}
            for r in group:
                if r["plugin_id"] == "g02_contrast" and "g10_boundary" in plugins_here:
                    r["kill_pattern"] = "boundary_artifact"
                if r["plugin_id"] == "g23_asymptotic_limit" and "g24_symmetry_twist" in plugins_here:
                    r["kill_pattern"] = "coverage_gap"
    return rows


def run_world(world: str, seed: int) -> dict:
    rows = synthetic_rows(seed, planted=(world == "PLANTED"))
    H._load_real_rows = lambda include_enriched=True: rows   # instrument unchanged
    t0 = time.time()
    res = H.run_pair_aware_permutation_null()
    d = {k: getattr(res, k) for k in dir(res) if not k.startswith("_")
         and not callable(getattr(res, k))}
    d = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()
         if isinstance(v, (int, float, str, bool)) or v is None}
    d["world"] = world
    d["seed"] = seed
    d["n_rows"] = len(rows)
    p95 = d.get("null_p95")
    d["min_observed_to_clear_p05"] = (p95 + 1) if isinstance(p95, (int, float)) else None
    d["elapsed_s"] = round(time.time() - t0, 1)
    return d


def main() -> int:
    out = {"question": __doc__.strip().splitlines()[0],
           "harness": "charon/agents/erebos/sprint1/phase3/pair_aware_permutation_null.py",
           "harness_constants": {"N_PERMUTATIONS": H.N_PERMUTATIONS, "SEED": H.SEED,
                                 "MIN_COOCCURRENCE": H.MIN_COOCCURRENCE,
                                 "MIN_LIFT": H.MIN_LIFT},
           "historical_quote_phase3K": {"observed_deltas_vs_pair": 2, "null_p95": 2,
                                        "p_value": 0.105, "source":
               "pivot/sprint1/phase3/PHASE3_K_PAIR_AWARE_NULL_VERDICT_2026-06-03.md"},
           "runs": []}
    for world in ("NULL", "PLANTED"):
        for seed in (11, 23, 37):
            r = run_world(world, seed)
            out["runs"].append(r)
            print(world, seed, {k: r.get(k) for k in (
                "observed_deltas_vs_pair", "observed_deltas_vs_plugin", "null_mean", "null_p95", "p_value", "verdict",
                "min_observed_to_clear_p05", "elapsed_s")})
    nulls = [r for r in out["runs"] if r["world"] == "NULL"]
    plants = [r for r in out["runs"] if r["world"] == "PLANTED"]
    out["summary"] = {
        "NULL_p_values": [r.get("p_value") for r in nulls],
        "NULL_null_p95": [r.get("null_p95") for r in nulls],
        "NULL_observed": [r.get("observed_deltas_vs_pair") for r in nulls],
        "NULL_false_positive_at_p05": sum(1 for r in nulls
                                          if (r.get("p_value") or 1) < 0.05),
        "PLANTED_p_values": [r.get("p_value") for r in plants],
        "PLANTED_observed": [r.get("observed_deltas_vs_pair") for r in plants],
        "PLANTED_detected_at_p05": sum(1 for r in plants
                                       if (r.get("p_value") or 1) < 0.05),
        "reading": ("If NULL worlds give null_p95 close to the historical 2, "
                    "then an observed count of 2 sits AT the instrument floor "
                    "on 699-row ledgers regardless of the data; PLANTED shows "
                    "whether strong linkage is detectable at all."),
    }
    (HERE / "erebos_null_instrument_calibration_result.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(out["summary"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
