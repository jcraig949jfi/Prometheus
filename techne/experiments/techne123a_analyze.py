"""TECHNE-123A analysis on M3: reads a run's result.json (always retrieved; it carries the pairwise
divergence curves computed on the pod) and, when present, trajectories.npz (the large artifact), and
writes TECHNE123A_ANALYSIS_<run_id>.json plus a fixed-width text table.

Statistics, as preregistered (TECHNE123A_PREREG_2026-10-05.md s1):
  D_same(t)   mean latent MSE over SAME_ACTION_DIFF_SEED pairs (FWD_si vs FWD_sj)
  E_fam(t)    mean over seeds of D_cf(t) - D_same(t) for COUNTERFACTUAL_<fam>, with a bootstrap over
              the pairs (2000 draws) giving a 95% interval
  P(t)        the same for INTERVENE at t >= 32; h* = last t whose interval excludes 0
  replicates  latent MSE of X vs X_rep per frame; DETERMINISTIC if all zero

Usage: python techne/experiments/techne123a_analyze.py <receipt_dir_or_result.json> [--npz PATH] [--out DIR]
Pure numpy. Nothing here touches the network or any credential.
"""
import argparse
import json
import os
import sys

import numpy as np


def _curves(result, kind):
    return [np.array(p["latent_mse"], dtype="float64") for p in result["pairs"].values() if p["kind"] == kind]


def _curves_px(result, kind):
    return [np.array(p["pixel_mae"], dtype="float64") for p in result["pairs"].values() if p["kind"] == kind]


def bootstrap_diff(cf, same, draws=2000, seed=0):
    """E(t) = mean(cf) - mean(same) per frame, with a percentile bootstrap over pair resampling."""
    rng = np.random.default_rng(seed)
    cf = np.stack(cf); same = np.stack(same)
    T = min(cf.shape[1], same.shape[1])
    cf, same = cf[:, :T], same[:, :T]
    point = cf.mean(0) - same.mean(0)
    bs = np.empty((draws, T))
    for d in range(draws):
        a = cf[rng.integers(0, len(cf), len(cf))].mean(0)
        b = same[rng.integers(0, len(same), len(same))].mean(0)
        bs[d] = a - b
    lo, hi = np.percentile(bs, [2.5, 97.5], axis=0)
    return point, lo, hi


def read(result, npz=None):
    out = {"run_id": result.get("run_id"), "plan": result.get("plan"), "T": result.get("T"), "device": result.get("device"),
           "n_trajectories": len(result["trajectories"]), "readings": {}, "curves": {}}
    # Q1 replicates
    reps = [(k, np.array(p["latent_mse"])) for k, p in result["pairs"].items() if p["kind"] == "REPLICATE"]
    same = _curves(result, "SAME_ACTION_DIFF_SEED")
    if reps:
        mx = max(float(c.max()) for _, c in reps)
        if mx == 0.0:
            q1 = "DETERMINISTIC"
        elif same and all((c[1:] < np.stack(same)[:, 1:].min(0)).all() for _, c in reps):
            q1 = "BOUNDED"
        elif same:
            q1 = "UNCONTROLLED_OR_AT_SEED_BAND"
        else:
            q1 = "REPLICATE_NONZERO_NO_SEED_BAND_TO_COMPARE"
        out["readings"]["Q1_replay"] = {"reading": q1, "replicate_max_latent_mse": mx,
                                        "replicate_pairs": [k for k, _ in reps]}
        out["curves"]["replicate_latent_mse"] = {k: c.tolist() for k, c in reps}
    if same:
        S = np.stack(same)
        out["curves"]["same_action_diff_seed_latent_mse_mean"] = S.mean(0).tolist()
        out["curves"]["same_action_diff_seed_latent_mse_min"] = S.min(0).tolist()
        out["curves"]["same_action_diff_seed_latent_mse_max"] = S.max(0).tolist()
        out["readings"]["stochastic_spread"] = {"n_pairs": len(same), "latent_mse_at_last_frame_mean": float(S[:, -1].mean())}
    # Q2 / Q3
    for fam in ("TURN", "NOOP", "INTERVENE", "BACK"):
        cf = _curves(result, "COUNTERFACTUAL_" + fam)
        if not cf or not same:
            out["readings"]["Q2_" + fam] = {"reading": "NOT_COMPUTABLE", "n_cf_pairs": len(cf), "n_same_pairs": len(same)}
            continue
        point, lo, hi = bootstrap_diff(cf, same)
        cfp = _curves_px(result, "COUNTERFACTUAL_" + fam); samep = _curves_px(result, "SAME_ACTION_DIFF_SEED")
        ppoint, plo, phi = bootstrap_diff(cfp, samep)
        T = len(point)
        out["curves"]["E_%s_latent" % fam] = {"point": point.tolist(), "lo": lo.tolist(), "hi": hi.tolist()}
        out["curves"]["E_%s_pixel" % fam] = {"point": ppoint.tolist(), "lo": plo.tolist(), "hi": phi.tolist()}
        if fam == "INTERVENE":
            idx = [t for t in range(32, T)]
            excl = [t for t in idx if lo[t] > 0]
            if idx and excl and excl[-1] == idx[-1]:
                r = "PERSISTENT_TO_END"
            elif excl:
                r = "DECAYING"
            else:
                r = "NO_EFFECT"
            peak = float(max(point[24:40])) if T >= 40 else float(max(point[24:T]))
            out["readings"]["Q3_persistence"] = {"reading": r, "h_star_last_frame_excluding_zero": (excl[-1] if excl else None),
                                                 "P_peak_frames_24_39": peak, "P_at_last_frame": float(point[-1]),
                                                 "decay_ratio_end_over_peak": (float(point[-1]) / peak if peak > 0 else None),
                                                 "frames_after_intervention_evaluated": len(idx), "n_cf_pairs": len(cf), "n_same_pairs": len(same),
                                                 "sign_agreement_pixel": bool(all((ppoint[t] > 0) == (point[t] > 0) for t in idx)) if idx else None}
        else:
            idx = [t for t in range(4, T)]
            frac = (sum(1 for t in idx if lo[t] > 0) / len(idx)) if idx else 0.0
            pfrac = (sum(1 for t in idx if plo[t] > 0) / len(idx)) if idx else 0.0
            reading = "CAUSAL" if frac >= 0.75 else "NOT_DETECTED"
            if (frac >= 0.75) != (pfrac >= 0.75):
                reading = "INDETERMINATE_RULERS_DISAGREE"
            out["readings"]["Q2_" + fam] = {"reading": reading, "fraction_horizons_latent_excluding_zero": round(frac, 3),
                                            "fraction_horizons_pixel_excluding_zero": round(pfrac, 3),
                                            "n_cf_pairs": len(cf), "n_same_pairs": len(same), "E_latent_at_last_frame": float(point[-1])}
    # secondary estimate with the BACK baseline (Amendment A): TURN vs BACK against BACK_si vs BACK_sj
    same_b = _curves(result, "SAME_ACTION_DIFF_SEED_BACK")
    cf_b = _curves(result, "COUNTERFACTUAL_TURN_VS_BACK")
    if same_b and cf_b:
        point, lo, hi = bootstrap_diff(cf_b, same_b)
        idx = [t for t in range(4, len(point))]
        frac = sum(1 for t in idx if lo[t] > 0) / len(idx)
        out["readings"]["Q2_TURN_secondary_BACK_baseline"] = {"reading": "CAUSAL" if frac >= 0.75 else "NOT_DETECTED",
                                                              "fraction_horizons_latent_excluding_zero": round(frac, 3), "n_cf_pairs": len(cf_b), "n_same_pairs": len(same_b),
                                                              "E_latent_at_last_frame": float(point[-1])}
        out["curves"]["E_TURN_vs_BACK_latent"] = {"point": point.tolist(), "lo": lo.tolist(), "hi": hi.tolist()}
        S = np.stack(same_b)
        out["curves"]["same_action_diff_seed_BACK_latent_mse_mean"] = S.mean(0).tolist()
    # descriptive, from the npz when present: drift from the prompt, frame-to-frame change, stall
    if npz is not None:
        desc = {}
        for k in npz.files:
            if not k.startswith("lat_"):
                continue
            L = npz[k].astype("float32"); T = L.shape[0]
            drift = [float(np.mean((L[t] - L[0]) ** 2)) for t in range(T)]
            step = [0.0] + [float(np.mean((L[t] - L[t - 1]) ** 2)) for t in range(1, T)]
            desc[k[4:]] = {"drift_from_prompt_t8_16_32_48_last": [round(drift[t], 4) for t in (8, 16, 32, 48, T - 1) if t < T],
                           "step_change_t8_32_last": [round(step[t], 4) for t in (8, 32, T - 1) if t < T],
                           "stalled_last8": bool(all(x < 0.01 for x in step[-8:]))}
        out["descriptive"] = desc
        out["readings"]["stall_count"] = {"stalled": sum(1 for v in desc.values() if v["stalled_last8"]), "of": len(desc),
                                          "stalled_labels": sorted(k for k, v in desc.items() if v["stalled_last8"])}
    # timing
    tr = result["trajectories"]
    pf = [s for v in tr.values() for s in v["per_frame_s"]]
    out["timing"] = {"frames_generated": len(pf), "s_per_frame_mean": float(np.mean(pf)) if pf else None,
                     "s_per_frame_max": float(np.max(pf)) if pf else None, "weights_s": result["timing_s"].get("weights"),
                     "load_models_s": result["timing_s"].get("load_models"), "all_trajectories_s": result["timing_s"].get("all_trajectories"),
                     "gpu_mem_peak_mib": result.get("gpu_mem_peak_mib")}
    out["weights_verified"] = {k: v.get("verified") for k, v in result["weights"].items() if isinstance(v, dict) and "verified" in v}
    if npz is not None:
        out["npz"] = {"keys": sorted(npz.files), "latent_shapes": {k: list(npz[k].shape) for k in npz.files if k.startswith("lat_")}}
    return out


def table(a):
    lines = ["TECHNE-123A analysis  run %s  plan %s  T %s  device %s" % (a["run_id"], a["plan"], a["T"], a["device"]),
             "trajectories %d  frames %s  s/frame mean %s  max %s  weights %s s  load %s s" % (
                 a["n_trajectories"], a["timing"]["frames_generated"],
                 None if a["timing"]["s_per_frame_mean"] is None else round(a["timing"]["s_per_frame_mean"], 3),
                 None if a["timing"]["s_per_frame_max"] is None else round(a["timing"]["s_per_frame_max"], 3),
                 a["timing"]["weights_s"], a["timing"]["load_models_s"]),
             "weights verified against official sha256: %s" % a["weights_verified"], ""]
    for k, v in a["readings"].items():
        lines.append("%-18s %s" % (k, json.dumps(v)))
    lines.append("")
    for name in ("E_TURN_latent", "E_NOOP_latent", "E_INTERVENE_latent", "E_BACK_latent", "E_TURN_vs_BACK_latent"):
        c = a["curves"].get(name)
        if not c:
            continue
        lines.append(name + "  (t: point [lo, hi])")
        pts = c["point"]
        for t in range(0, len(pts), max(1, len(pts) // 8)):
            lines.append("  t=%3d  %+.5f  [%+.5f, %+.5f]" % (t, pts[t], c["lo"][t], c["hi"][t]))
        lines.append("  t=%3d  %+.5f  [%+.5f, %+.5f]" % (len(pts) - 1, pts[-1], c["lo"][-1], c["hi"][-1]))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="receipt evidence dir (containing result.json) or a result.json path")
    ap.add_argument("--npz", default=None)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__))))
    a = ap.parse_args()
    src = a.source if a.source.endswith(".json") else os.path.join(a.source, "result.json")
    result = json.load(open(src, encoding="utf-8"))
    npz = np.load(a.npz) if a.npz and os.path.exists(a.npz) else None
    an = read(result, npz)
    an["source"] = src.replace("\\", "/")
    out_json = os.path.join(a.out, "TECHNE123A_ANALYSIS_%s.json" % an["run_id"])
    with open(out_json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(an, fh, indent=1)
    txt = table(an)
    with open(out_json[:-5] + ".txt", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt + "\n")
    print(txt)
    print("\nwrote", out_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
