"""cw01-e05 independent replication lane: additional attempt seeds.

This file belongs to the REPLICATION lane, not to the frozen experiment. It adds
NOTHING to the contract and changes nothing in it. It imports the committed driver
and calls its own `one_replicate()` with new `attempt_id` values, exactly as
REPLICA_BRIEF.md R4 permits:

  * same world (WORLD.json, unmodified)
  * same budget B, same statistic, same normalisation
  * same set-selection procedure (exhaustive enumeration inside one_replicate)
  * same null construction and same eligibility rule
  * same contract hash, bound and frozen by the committed bind_contract()

The replicate COUNT is not a field of the hashed contract, and more replicates make
the COMPLETE bar harder rather than easier, because the contract requires every
condition to hold in EVERY replicate.

`execute_e05.py` is NOT edited and NOT executed as __main__ here; only its module
functions are called. `ctx` is passed as None, which the committed `one_replicate`
already supports (it guards `if ctx is not None` before emitting lineage rows), so
no rows are written and no RowWriter is opened by this script.

Usage (from this directory):
    H:\\Python312\\python.exe extra_seeds_replica.py [attempt_id ...]
Default seeds: cw01-e05-r05 .. cw01-e05-r12
"""
from __future__ import annotations

import json
import pathlib
import platform
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import execute_e05 as X  # noqa: E402  (the COMMITTED driver, imported not edited)

DEFAULT_SEEDS = ["cw01-e05-r%02d" % i for i in range(5, 13)]
OUT = HERE / "extra_seeds_replica.json"

# Fields the replication lane reports per replicate.
REPORT_FIELDS = (
    "attempt_id", "budget_B", "did_points",
    "law_effect_best_points", "law_effect_worst_points",
    "superadditivity_mean_pct", "superadditivity_clears_null",
    "null_p05", "null_p95",
    "ablation_targeted", "ablation_random_sham", "ablation_all_load_bearing",
    "n_load_bearing", "n_carried",
    "mixture_score", "best_single_score", "beats_best_single",
    "arms_match", "ancestor_relative_pct",
)


def _jsonable(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError("not JSON serialisable: %r" % type(o))


def main(argv):
    seeds = argv[1:] or list(DEFAULT_SEEDS)

    contract = X.bind_contract()          # refuses on ANY drift from the committed file
    if contract.hash != "c80b5bfd348f7b87418166061f39c1446bd45c6e74ff060f9c5927e24b2c5619":
        raise SystemExit("contract hash is not the frozen one: %s" % contract.hash)

    print("########## cw01-e05 replication lane: extra attempt seeds ##########")
    print("    contract %s (frozen, unchanged)" % contract.hash[:16])
    print("    budget_B %s" % contract.get("budget_B"))
    print("    seeds    %s" % ", ".join(seeds))

    reps, failures = [], []
    for aid in seeds:
        t0 = time.time()
        try:
            r = X.one_replicate(aid, contract, ctx=None)
        except Exception as e:                                   # noqa: BLE001
            failures.append({"attempt_id": aid, "error": "%s: %s" % (type(e).__name__, e)})
            print("    %-14s FAILED  %s: %s" % (aid, type(e).__name__, str(e)[:120]))
            _dump(reps, failures, seeds, contract)
            continue
        r["wall_s"] = round(time.time() - t0, 1)
        reps.append(r)
        print("    %-14s did %+.6f pp | sa %.6f%% clears=%s | beats=%s | load_bearing=%s | %.1fs"
              % (aid, r["did_points"], r["superadditivity_mean_pct"],
                 r["superadditivity_clears_null"], r["beats_best_single"],
                 r["ablation_all_load_bearing"], r["wall_s"]))
        _dump(reps, failures, seeds, contract)   # partial results survive an interruption

    n = len(reps)
    if n:
        print("\n    %d/%d extra seeds completed" % (n, len(seeds)))
        print("    beats_best_single           %d/%d" % (sum(r["beats_best_single"] for r in reps), n))
        print("    superadditivity_clears_null %d/%d" % (sum(r["superadditivity_clears_null"] for r in reps), n))
        print("    ablation_all_load_bearing   %d/%d" % (sum(r["ablation_all_load_bearing"] for r in reps), n))
        print("    did_points > 0              %d/%d" % (sum(r["did_points"] > 0 for r in reps), n))
    print("    wrote %s" % OUT)
    return 0 if not failures else 1


def _dump(reps, failures, seeds, contract):
    payload = {
        "lane": "independent_replication",
        "campaign_id": "cw01-2026-09-17", "experiment_id": "cw01-e05",
        "note": "additional attempt seeds under the UNCHANGED frozen contract; "
                "the committed driver was imported, not modified",
        "verdict_contract_sha256": contract.hash,
        "budget_B": contract.get("budget_B"),
        "seeds_requested": list(seeds),
        "n_completed": len(reps),
        "environment": {"os": platform.platform(), "python": sys.version.split()[0],
                        "numpy": np.__version__, "executable": sys.executable},
        "summary": ({
            "beats_best_single": "%d/%d" % (sum(r["beats_best_single"] for r in reps), len(reps)),
            "superadditivity_clears_null": "%d/%d" % (sum(r["superadditivity_clears_null"] for r in reps), len(reps)),
            "ablation_all_load_bearing": "%d/%d" % (sum(r["ablation_all_load_bearing"] for r in reps), len(reps)),
            "m3_interaction_positive": "%d/%d" % (sum(r["did_points"] > 0 for r in reps), len(reps)),
            "did_points_mean": float(np.mean([r["did_points"] for r in reps])),
            "superadditivity_mean_pct": float(np.mean([r["superadditivity_mean_pct"] for r in reps])),
        } if reps else {}),
        "reported_fields": list(REPORT_FIELDS),
        "replicates": reps,
        "failures": failures,
    }
    OUT.write_text(json.dumps(payload, indent=1, default=_jsonable), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
