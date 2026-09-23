"""ANALYSE cw01-e08 from the committed rows under the frozen contract -> RESULT.json.

Reads rows/cw01-e08-a01.jsonl only. Lineage is the unit. Applies exactly the preregistered
rules: competence floor, lineage competence (>= 4 competent representatives), capability-adjusted
scalar burden with TAX-label randomisation within AMP strata, interaction check for pooling,
common support, minimum counts, non-competent excess; then the disposition through
lib/lineage.decide so no branch can fire on a test that did not run.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent


def _bootstrap_lib():
    for cand in [HERE] + list(HERE.parents):
        if (cand / "lib" / "repopath.py").exists():
            sys.path.insert(0, str(cand / "lib"))
            return cand / "lib"
    raise RuntimeError("cannot locate lib/repopath.py walking up from %s" % HERE)


_bootstrap_lib()
sys.path.insert(0, str(HERE))
import contract as CT          # noqa: E402
import lineage as LG           # noqa: E402
import seeds as S              # noqa: E402
import world_e08 as W          # noqa: E402


def js(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.bool_):
        return bool(o)
    return str(o)


def main():
    cfg = json.loads((HERE / "WORLD.json").read_text(encoding="utf-8"))
    c = CT.VerdictContract.load(HERE / "VERDICT_CONTRACT.json").freeze()
    aid = cfg["attempt_id"]
    rows_path = HERE / "rows" / "cw01-e08-a01.jsonl"
    rows = [json.loads(l) for l in rows_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    bad = [r for r in rows if r.get("verdict_contract_sha256") != c.hash]
    if bad:
        raise CT.ContractViolation("%d rows carry a different contract hash" % len(bad))
    assays = [r for r in rows if r.get("kind") == "assay"]
    lin_rows = [r for r in rows if r.get("kind") == "lineage"]
    floor = cfg["assay"]["competence_floor_held64"]
    st = cfg["stats"]
    log = LG.TestLog()

    # ---- lineage-level quantities over COMPETENT representatives -----------------------
    L = {}
    for r in assays:
        key = (r["arm"], r["lineage"])
        L.setdefault(key, []).append(r)
    lineages = []
    for (arm, lin), rs in sorted(L.items()):
        comp = [r for r in rs if r["held64"] > floor]
        rec = {"arm": arm, "lineage": lin, "tax": W.is_tax(arm), "amp": W.is_amp(arm),
               "n_reps": len(rs), "n_competent": len(comp), "competent": len(comp) >= st.get("min_competent_reps", 4)}
        src = comp if rec["competent"] else rs
        rec["C"] = float(np.mean([r["held64"] for r in src]))
        rec["scalar"] = float(np.mean([r["scalar"] for r in src]))
        for cname in W.COORDS:
            rec["b_" + cname] = float(np.mean([r["b_" + cname] for r in src]))
        rec["retention"] = float(np.mean([(r["held64_after_amp"] - 159.0) / max(r["held64"] - 159.0, 1e-9)
                                          for r in src]))
        rec["live_ticks"] = float(np.mean([r["live_ticks"] for r in src]))
        rec["work"] = float(np.mean([r["work"] for r in src]))
        rec["raw_C_all_reps"] = float(np.mean([r["held64"] for r in rs]))
        rec["raw_scalar_all_reps"] = float(np.mean([r["scalar"] for r in rs]))
        lineages.append(rec)
    log.record("rows_present", True, len(assays) > 0, "%d assay rows, %d lineages" % (len(assays), len(lineages)))

    per_arm = {}
    for arm in cfg["arms"]:
        ls = [x for x in lineages if x["arm"] == arm]
        per_arm[arm] = {"n": len(ls), "n_competent_lineages": sum(x["competent"] for x in ls),
                        "n_noncompetent_lineages": sum(not x["competent"] for x in ls),
                        "C_mean_all": float(np.mean([x["raw_C_all_reps"] for x in ls])),
                        "scalar_mean_all": float(np.mean([x["raw_scalar_all_reps"] for x in ls])),
                        "live_ticks_mean": float(np.mean([x["live_ticks"] for x in ls])),
                        "work_mean": float(np.mean([x["work"] for x in ls]))}
        for cname in W.COORDS:
            per_arm[arm]["b_" + cname + "_mean_all"] = float(np.mean([x["b_" + cname] for x in ls]))
        if per_arm[arm]["n_competent_lineages"]:
            cs = [x for x in ls if x["competent"]]
            per_arm[arm]["C_mean_competent"] = float(np.mean([x["C"] for x in cs]))
            per_arm[arm]["scalar_mean_competent"] = float(np.mean([x["scalar"] for x in cs]))
            per_arm[arm]["retention_mean_competent"] = float(np.mean([x["retention"] for x in cs]))

    # ---- non-competent excess (TAX minus no-TAX, per AMP level) ---------------------------
    excess = {}
    for amp in (False, True):
        tax_arm = "TAX+AMP" if amp else "TAX"
        ctl_arm = "AMP" if amp else "CONTROL"
        excess["amp" if amp else "sham"] = (per_arm[tax_arm]["n_noncompetent_lineages"]
                                            - per_arm[ctl_arm]["n_noncompetent_lineages"])
    excess_ok = all(v <= st["noncompetent_excess_max"] for v in excess.values())
    log.record("noncompetent_excess", True, excess_ok, "TAX minus no-TAX non-competent lineages per level: %s (max %d)"
               % (excess, st["noncompetent_excess_max"]), value=excess)

    # ---- competent lineages only: counts, overlap, contrast ---------------------------------
    comp = [x for x in lineages if x["competent"]]
    n_tax = sum(x["tax"] for x in comp)
    n_notax = sum(not x["tax"] for x in comp)
    counts_ok = n_tax >= st["min_competent_lineages"] and n_notax >= st["min_competent_lineages"]
    log.record("min_counts", True, counts_ok, "competent lineages TAX %d / no-TAX %d (min %d each)"
               % (n_tax, n_notax, st["min_competent_lineages"]), value={"tax": n_tax, "notax": n_notax})

    if n_tax >= 1 and n_notax >= 1:
        ov = W.overlap(np.array([x["C"] for x in comp if not x["tax"]]),
                       np.array([x["C"] for x in comp if x["tax"]]), st["overlap_min"])
        log.record("common_support", True, ov["ok"], json.dumps(ov), value=ov)
    else:
        ov = None
        log.record("common_support", False, None, "not enough competent lineages to assess")

    contrast = None
    if counts_ok and ov and ov["ok"]:
        rng = S.rng(aid, "perm")
        contrast = W.stratified_contrast([x["scalar"] for x in comp], [x["C"] for x in comp],
                                         [x["tax"] for x in comp], [x["amp"] for x in comp],
                                         st["n_perm"], rng)
        log.record("interaction_inside_null", True, contrast["c_int_inside"],
                   "c_int %.4f in [%.4f, %.4f]" % (contrast["c_int"], contrast["c_int_p05"], contrast["c_int_p95"]),
                   value=contrast["c_int"])
        log.record("primary_contrast", contrast["c_int_inside"], contrast["c_tax_below_p05"],
                   "c_tax %.4f vs p05 %.4f (p95 %.4f)" % (contrast["c_tax"], contrast["c_tax_p05"], contrast["c_tax_p95"]),
                   value=contrast["c_tax"])
        # per-stratum contrasts, always reported
        strata = {}
        for amp in (False, True):
            sub = [x for x in comp if x["amp"] == amp]
            if sum(x["tax"] for x in sub) >= 2 and sum(not x["tax"] for x in sub) >= 2:
                rng_s = S.rng(aid, "perm|stratum", int(amp))
                strata["amp" if amp else "sham"] = W.stratified_contrast(
                    [x["scalar"] for x in sub], [x["C"] for x in sub], [x["tax"] for x in sub],
                    [False] * len(sub), st["n_perm"] // 4, rng_s)
        contrast["per_stratum"] = strata
        # secondary: each coordinate and retention, same machinery
        secondary = {}
        for cname in W.COORDS:
            rng_c = S.rng(aid, "perm|coord|" + cname)
            secondary[cname] = W.stratified_contrast([x["b_" + cname] for x in comp], [x["C"] for x in comp],
                                                     [x["tax"] for x in comp], [x["amp"] for x in comp],
                                                     st["n_perm"] // 4, rng_c)
        rng_r = S.rng(aid, "perm|retention")
        secondary["retention"] = W.stratified_contrast([x["retention"] for x in comp], [x["C"] for x in comp],
                                                       [x["tax"] for x in comp], [x["amp"] for x in comp],
                                                       st["n_perm"] // 4, rng_r)
        rng_d = S.rng(aid, "perm|deltaC")
        secondary["delta_C_tax_minus_notax"] = W.stratified_contrast([x["C"] for x in comp], [0.0] * len(comp),
                                                                     [x["tax"] for x in comp], [x["amp"] for x in comp],
                                                                     st["n_perm"] // 4, rng_d)
        contrast["secondary"] = secondary
    else:
        log.record("interaction_inside_null", False, None, "contrast not computed")
        log.record("primary_contrast", False, None, "contrast not computed (counts or overlap failed)")

    rules = [
        ("INCONCLUSIVE", "the tax removed computation rather than compressing it: non-competent excess > max",
         ["noncompetent_excess"], lambda lg: not lg.passed("noncompetent_excess")),
        ("INCONCLUSIVE", "a required contrast is NOT_VERIFIED (counts or common support)",
         ["min_counts", "common_support"], lambda lg: not (lg.passed("min_counts") and lg.passed("common_support"))),
        ("INCONCLUSIVE", "interaction outside its null: pooled contrast NOT_VERIFIED; per-stratum contrasts reported",
         ["interaction_inside_null"], lambda lg: not lg.passed("interaction_inside_null")),
        ("COMPLETE", "pooled c_tax below p05 of its randomisation null with support, counts and excess satisfied",
         ["primary_contrast", "noncompetent_excess", "min_counts", "common_support"],
         lambda lg: lg.passed("primary_contrast")),
        ("NULL", "question posed; c_tax not below p05",
         ["primary_contrast", "noncompetent_excess", "min_counts", "common_support"],
         lambda lg: not lg.passed("primary_contrast")),
    ]
    disp, reason, trace = LG.decide(rules, log)

    out = c.stamp({
        "campaign_id": cfg["campaign_id"], "experiment_id": cfg["experiment_id"], "attempt_id": aid,
        "phase": "CLOSE_SCIENCE", "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "disposition": disp, "disposition_reason": reason, "decision_trace": trace,
        "tests": log.as_dict(), "per_arm": per_arm, "noncompetent_excess": excess,
        "contrast": contrast, "overlap": ov, "lineages": lineages,
        "rows": {"path": str(rows_path.relative_to(HERE)), "n_rows": len(rows), "n_assay": len(assays),
                 "n_lineage_rows": len(lin_rows)},
        "_reading": "c_tax < 0 means TAX lineages carry LESS scalar burden at matched capability; the full "
                    "burden vector per coordinate is in contrast.secondary so migration is visible",
    })
    (HERE / "RESULT.json").write_text(json.dumps(out, indent=1, ensure_ascii=True, default=js), encoding="utf-8")
    print("DISPOSITION %s - %s" % (disp, reason))
    for arm, v in per_arm.items():
        print("   %-8s competent lineages %d/%d | C all %.1f | scalar all %.3f | bits %.1f params %.0f"
              % (arm, v["n_competent_lineages"], v["n"], v["C_mean_all"], v["scalar_mean_all"],
                 v["b_bits_mean_all"], v["b_params_mean_all"]))
    if contrast:
        print("   c_tax %.4f  null [%.4f, %.4f]  below_p05=%s | c_int %.4f inside=%s"
              % (contrast["c_tax"], contrast["c_tax_p05"], contrast["c_tax_p95"], contrast["c_tax_below_p05"],
                 contrast["c_int"], contrast["c_int_inside"]))
    print("   excess %s | counts tax %d notax %d | overlap %s" % (excess, n_tax, n_notax, ov and ov["ok"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
