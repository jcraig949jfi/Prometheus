"""FREEZE cw01-e08: copy the qualification proposal into WORLD.json and hash the verdict contract.

Refuses if QUALIFY.json is not QUALIFIED, if any pressure parameter is still null after the copy, or
if the production seed component appears among the qualification seed components. After this
script runs and its outputs are committed, no criterion, coefficient, schedule, seed, exclusion
rule, or statistic may change under attempt_id cw01-e08-a01 (lib/contract freeze rule).
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent


def _bootstrap_lib():
    for cand in [HERE] + list(HERE.parents):
        if (cand / "lib" / "repopath.py").exists():
            sys.path.insert(0, str(cand / "lib"))
            return cand / "lib"
    raise RuntimeError("cannot locate lib/repopath.py walking up from %s" % HERE)


_bootstrap_lib()
import contract as CT          # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    q = json.loads((HERE / "QUALIFY.json").read_text(encoding="utf-8"))
    if q["verdict"] != "QUALIFIED":
        raise SystemExit("QUALIFY.json verdict is %s; nothing to freeze" % q["verdict"])
    cfg = json.loads((HERE / "WORLD.json").read_text(encoding="utf-8"))
    prop = q["proposal"]
    if any(prop[k] is None for k in ("lambda", "generations", "g_amp")):
        raise SystemExit("proposal incomplete: %s" % prop)
    if q["production_seed_component"] in q["seed_components_used"]:
        raise SystemExit("production seed component overlaps qualification seeds")

    cfg["evolution"]["generations"] = int(prop["generations"])
    cfg["evolution"]["g_amp"] = int(prop["g_amp"])
    cfg["tax"]["lambda"] = float(prop["lambda"])
    cfg["tax"]["lambda_fraction_of_max"] = float(prop["lambda_fraction"])
    cfg["tax"]["weights"] = [float(w) for w in prop["weights"]]
    cfg["_frozen_from"] = "QUALIFY.json %s" % q["ts"]
    (HERE / "WORLD.json").write_text(json.dumps(cfg, indent=1, ensure_ascii=True), encoding="utf-8")

    spec = {
        "experiment_id": cfg["experiment_id"],
        "attempt_id": cfg["attempt_id"],
        "world_schema_version": cfg["world_schema_version"],
        "statistic_name": "capability_adjusted_scalar_burden_tax_contrast",
        "statistic_formula": "scalar(B)_l = a + b*C_l + c_tax*[TAX] + c_amp*[AMP]; c_tax is the primary contrast; "
                             "interaction c_int from the full model with + c_int*[TAX*AMP]",
        "normalisation": "scalar(B) = sum_j w_j * B_j / B_j_max over (bond, params, flops, bits); C_l = mean held64 "
                         "(per-seed mean summed clipped final charge on seeds 30000..30063) over COMPETENT representatives",
        "intervention_control_relationship": "2x2 factorial; arms differ ONLY in sel = fit - lambda*scalar(B) (TAX) and in "
                                             "whether the scheduled structural operator truncates (AMP) or shams; same world, "
                                             "seeds, horizon, population, mutation, selection, instrumentation",
        "null_construction": "randomisation of TAX labels within each AMP stratum, n_perm draws, seeded from "
                             "seeds(attempt_id, 'perm')",
        "effect_clearing_rule": "COMPLETE requires c_tax < p05 of its randomisation null with common support and "
                                "minimum counts; c_int must lie inside its null for pooling, else the pooled contrast "
                                "is NOT_VERIFIED and per-stratum contrasts are reported",
        "set_selection_procedure": "representatives = top 8 of each lineage's final population by RECORDED tax-free "
                                   "train fitness (one rule for all arms); competent = held64 > competence floor; "
                                   "lineage competent iff >= 4 competent representatives",
        "disposition_rules": {
            "COMPLETE": "Q1-Q7 QUALIFIED; c_tax < p05; overlap >= 4 each way; >= 6 competent lineages per TAX level; "
                        "non-competent lineage count in TAX arms exceeds no-TAX by at most 2 per level; no fixture WRONG",
            "NULL": "question posed (overlap, counts, excess) and c_tax not below p05",
            "INCONCLUSIVE": "any predicate failed; or a required contrast NOT_VERIFIED; or non-competent excess > 2 per level",
            "INVALID": "contract mismatch, seed overlap, arm label reaching the assay, recount disagreement in production rows, "
                       "or any post-freeze integrity failure",
        },
        "world": {"gen_seed": cfg["world"]["gen_seed"], "wid": q["world"]["wid"], "A": cfg["world"]["A"],
                  "train_seeds": cfg["world"]["train_seeds"], "held_seeds": cfg["world"]["held_seeds"]},
        "organism": {"R_max": cfg["organism"]["R_max"], "init_G_noise": cfg["organism"]["init_G_noise"],
                     "record_nbytes": q["world"]["record_nbytes"]},
        "evolution": {k: cfg["evolution"][k] for k in ("n_org", "tournament", "elite", "mut_rate", "mut_sigma",
                                                        "p_rank", "grow_sigma", "generations", "g_amp")},
        "tax": {"lambda": cfg["tax"]["lambda"], "weights": cfg["tax"]["weights"],
                "lambda_fraction_of_max": cfg["tax"]["lambda_fraction_of_max"], "coordinates": cfg["tax"]["_coordinates"]},
        "arms": cfg["arms"], "lineages_per_arm": cfg["lineages_per_arm"],
        "production_seed_component": "evo",
        "qualification_seed_components": q["seed_components_used"],
        "assay": {"top_k": cfg["assay"]["top_k"], "s_amp": cfg["assay"]["s_amp"],
                  "competence_floor_held64": cfg["assay"]["competence_floor_held64"]},
        "stats": cfg["stats"],
        "freeze_rule": "once the first production organism is evaluated under this attempt_id, no metric, coefficient, "
                       "schedule, seed, exclusion rule, threshold or verdict criterion may change; a defect voids the "
                       "verdict and opens a new attempt_id",
    }
    c = CT.VerdictContract(spec).freeze()
    h = c.save(HERE / "VERDICT_CONTRACT.json")
    RS.require_ascii_safe(HERE / "VERDICT_CONTRACT.json")
    RS.require_ascii_safe(HERE / "WORLD.json")
    print("FROZEN %s | contract sha256 %s | lambda %.4f (x%.4f) G %d g_amp %d" % (
        time.strftime("%Y-%m-%d %H:%M:%S"), h, cfg["tax"]["lambda"], cfg["tax"]["lambda_fraction_of_max"],
        cfg["evolution"]["generations"], cfg["evolution"]["g_amp"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
