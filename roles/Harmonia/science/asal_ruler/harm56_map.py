"""HARM-56 cross-observer map. Implements PREREG_HARM56_OBSERVER_DEPENDENCE_2026-09-19.md, written BEFORE any
native-observer score exists. Input: flax_scores.json (Techne's harm55_flax_score.py --path flax output:
{"identity": {...}, "scores": {"<stage>_<idx>": float}, optional "embeddings": {key: [8 x 512]}, optional
"self_check": {key: torch_score}, optional "static_control": float}).

    python harm56_map.py --flax <flax_scores.json> [--out <dir>]
Outputs: harm56_table.jsonl (one row per rollout, the operator's columns), harm56_map.json (counts, A-F, probes,
verdicts), and prints the compact map. Never a single agreement statistic as the verdict.
"""
import argparse, hashlib, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "out", "run_2026-09-18", "search")
MANIFEST = os.path.join(HERE, "out", "run_2026-09-18", "frames128_manifest.json")
THRESH = {"catalogue": 0.807627, "mean": 0.816686, "2sd": 0.816686 - 2 * 0.008363}
BAND = 0.01
CATALOGUE_CROSSERS = ["S0_212", "S0_138", "S0_215", "S0_9", "S0_8"]
TORCH_BOTTOM10 = ["S2_189", "S2_175", "S2_87", "S2_162", "S2_2", "S2_115", "S2_194", "S2_84", "S2_55", "S2_135"]
SELF_TOL, STATIC_TOL = 1e-6, 1e-3


def state(t_below, f_below):
    return "STABLE_CROSSING" if t_below and f_below else "LOST_CROSSING" if t_below else "GAINED_CROSSING" if f_below else "STABLE_NON_CROSSING"


def d_clip_from(z):
    z = np.asarray(z, dtype=np.float64); z = z / np.linalg.norm(z, axis=-1, keepdims=True)
    return float(np.mean([1.0 - float(z[i + 1] @ z[i]) for i in range(len(z) - 1)]))


def classify(o, alive, th):  # identical to asal_ruler.classify (copied so the map has no import side effects)
    if not alive: return "NOT_ALIVE"
    if o["coh"] >= 0.8 * th["coh_O"] and o["d_pix"] >= 0.5 * th["d_pix_O"] and o["mass_cv"] <= 0.5: return "GENUINE_DYNAMICAL_NOVELTY"
    if o["coh"] < 0.5 * th["coh_O"] and o["d_pix"] >= th["d_pix_O"]: return "METRIC_EXPLOIT"
    if o["d_pix"] < 0.5 * th["d_pix_O"] and o["d_clip"] >= 0.8 * th["d_clip_H"]: return "OBSERVER_EXPLOIT"
    return "UNCLASSIFIED"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--flax", required=True); ap.add_argument("--out", default=os.path.join(HERE, "out", "run_2026-09-18", "harm56"))
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    rows = {f"{r['stage']}_{r['idx']}": r for r in (json.loads(l) for l in open(os.path.join(RUN, "rows.jsonl"))) if r.get("alive") and r.get("score") is not None}
    th = json.load(open(os.path.join(HERE, "out", "run_2026-09-18", "thresholds.json")))
    man = json.load(open(MANIFEST))["rollouts"]
    fx = json.load(open(a.flax)); flax = fx["scores"]; emb = fx.get("embeddings", {}); selfchk = fx.get("self_check", {})
    controls = {}
    # C-SELF, C-STATIC, C-HASH (hash check is the scoring host's; we record what the identity block says)
    if selfchk:
        d = max(abs(float(selfchk[k]) - rows[k]["score"]) for k in selfchk if k in rows); controls["C-SELF"] = {"max_abs_diff": d, "n": len(selfchk), "pass": d <= SELF_TOL}
    else: controls["C-SELF"] = {"pass": None, "note": "no self_check block returned"}
    if "static_control" in fx: controls["C-STATIC"] = {"score": fx["static_control"], "pass": abs(fx["static_control"] - 0.875) < STATIC_TOL}
    else: controls["C-STATIC"] = {"pass": None, "note": "no static_control returned"}
    controls["C-HASH"] = {"scoring_host_verified": fx.get("identity", {}).get("frames_manifest_verified"), "manifest_sha256_here": hashlib.sha256(open(MANIFEST, "rb").read()).hexdigest()}
    keys = [k for k in rows if k in flax]; missing = [k for k in rows if k not in flax]
    t = np.array([rows[k]["score"] for k in keys]); f = np.array([float(flax[k]) for k in keys])
    rt = np.argsort(np.argsort(t)); rf = np.argsort(np.argsort(f))
    table = []
    for i, k in enumerate(keys):
        r = rows[k]; row = {"key": k, "stage": r["stage"], "idx": r["idx"], "ic": r["ic"], "params": r["params"], "alive": r["alive"], "class_torch": r["class"],
                            "score_torch": float(t[i]), "score_flax": float(f[i]), "diff_signed": float(f[i] - t[i]), "diff_abs": float(abs(f[i] - t[i])),
                            "rank_torch": int(rt[i]), "rank_flax": int(rf[i]), "rank_shift": int(rf[i] - rt[i]), "frame_sha256": man.get(k, {}).get("sha256")}
        for nm, thr in THRESH.items():
            row[f"cross_{nm}_torch"] = bool(t[i] < thr); row[f"cross_{nm}_flax"] = bool(f[i] < thr); row[f"state_{nm}"] = state(t[i] < thr, f[i] < thr)
        if k in emb:
            o = {"coh": r["coh"], "d_pix": r["d_pix"], "mass_cv": r["mass_cv"], "d_clip": d_clip_from(emb[k])}
            row["d_clip_flax"] = o["d_clip"]; row["class_flax"] = classify(o, True, th)
            row["classification"] = "CLASSIFICATION_STABLE" if row["class_flax"] == r["class"] else "CLASSIFICATION_DISCORDANT"
        else:
            depends = r["class"] == "OBSERVER_EXPLOIT" or (r["d_pix"] < 0.5 * th["d_pix_O"])
            row["classification"] = "CLASSIFICATION_UNRESOLVED" if depends else "CLASSIFICATION_STABLE"
            row["classification_note"] = "native embeddings absent" + ("; class branch depends on d_clip" if depends else "; class does not depend on d_clip")
        if abs(t[i] - THRESH["mean"]) <= BAND and row["state_mean"] in ("LOST_CROSSING", "GAINED_CROSSING"):
            row["classification"] = "CLASSIFICATION_UNRESOLVED" if row["classification"] == "CLASSIFICATION_STABLE" else row["classification"]
        table.append(row)
    with open(os.path.join(a.out, "harm56_table.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
        for row in table: fh.write(json.dumps(row) + "\n")
    by = {r["key"]: r for r in table}
    def cnt(field):
        c = {}
        for r in table: c[r[field]] = c.get(r[field], 0) + 1
        return c
    res = {"n": len(table), "n_missing_flax": len(missing), "identity": fx.get("identity"), "controls": controls, "thresholds": THRESH,
           "map": {nm: cnt(f"state_{nm}") for nm in THRESH}, "classification": cnt("classification"),
           "discordant_keys": [r["key"] for r in table if r["classification"] == "CLASSIFICATION_DISCORDANT"],
           "unresolved_keys": [r["key"] for r in table if r["classification"] == "CLASSIFICATION_UNRESOLVED"]}
    # A-F
    S0 = [r for r in table if r["stage"] == "S0"]; gen = [r for r in table if r["class_torch"] == "GENUINE_DYNAMICAL_NOVELTY"]; mex = [r for r in table if r["class_torch"] == "METRIC_EXPLOIT"]
    res["A_catalogue_life_still_crosses"] = {"flax_crossers_S0": [(r["key"], r["score_flax"], r["class_torch"]) for r in S0 if r["cross_mean_flax"]],
                                             "torch_crossers_status": {k: (by[k]["state_mean"] if k in by else "absent") for k in CATALOGUE_CROSSERS}}
    res["B_genuine_still_crosses"] = {"S2_135": {k: by["S2_135"][k] for k in ("score_torch", "score_flax", "state_mean", "state_2sd")} if "S2_135" in by else "absent",
                                      "genuine_states_mean": {r["key"]: r["state_mean"] for r in gen}, "genuine_states_2sd": {r["key"]: r["state_2sd"] for r in gen}}
    res["C_deepest_witnesses"] = {k: ({kk: by[k][kk] for kk in ("score_torch", "score_flax", "rank_flax", "state_mean", "state_2sd", "class_torch")} if k in by else "absent") for k in TORCH_BOTTOM10}
    mexc = [r for r in mex if r["cross_mean_torch"]]
    res["D_metric_exploit_preserved"] = {"n_torch_crossers": len(mexc), "still_below_mean_flax": sum(1 for r in mexc if r["cross_mean_flax"]),
                                         "not_preserved": [(r["key"], r["score_torch"], r["score_flax"]) for r in mexc if not r["cross_mean_flax"]]}
    def cls_stats(field):
        out = {}
        for c in ("GENUINE_DYNAMICAL_NOVELTY", "UNCLASSIFIED", "METRIC_EXPLOIT", "OBSERVER_EXPLOIT"):
            v = [r[field] for r in table if r["class_torch"] == c]
            if v: out[c] = {"n": len(v), "median": float(np.median(v)), "q1": float(np.percentile(v, 25)), "q3": float(np.percentile(v, 75))}
        return out
    st, sf = cls_stats("score_torch"), cls_stats("score_flax")
    ot = sorted(st, key=lambda c: st[c]["median"]); of = sorted(sf, key=lambda c: sf[c]["median"])
    res["E_ordering_of_regions"] = {"torch": st, "flax": sf, "order_torch": ot, "order_flax": of, "order_changed": ot != of}
    res["F_classification_observer_dependent"] = {"counts": res["classification"], "discordant": [(r["key"], r["class_torch"], r.get("class_flax"), r.get("d_clip_flax")) for r in table if r["classification"] == "CLASSIFICATION_DISCORDANT"],
                                                   "unresolved": [(r["key"], r["class_torch"], r.get("classification_note")) for r in table if r["classification"] == "CLASSIFICATION_UNRESOLVED"]}
    # probes
    conc = [r for r in table if r["state_mean"] in ("STABLE_CROSSING", "STABLE_NON_CROSSING")]; disc = [r for r in table if r["state_mean"] in ("LOST_CROSSING", "GAINED_CROSSING")]
    def dist(rs, field):
        v = [rows[r["key"]][field] for r in rs]; return {"n": len(v), "median": float(np.median(v)) if v else None, "q1": float(np.percentile(v, 25)) if v else None, "q3": float(np.percentile(v, 75)) if v else None}
    res["probes"] = {"P1_genuine_one_observer_only": [(r["key"], r["state_mean"], r["score_torch"], r["score_flax"]) for r in gen if r["state_mean"] in ("LOST_CROSSING", "GAINED_CROSSING")],
                     "P2_turbulence_one_observer_only": [(r["key"], r["state_mean"], r["score_torch"], r["score_flax"]) for r in mex if r["state_mean"] in ("LOST_CROSSING", "GAINED_CROSSING")],
                     "P3_catalogue_near_boundary": [(r["key"], r["score_torch"], r["score_flax"], r["state_mean"]) for r in S0 if abs(r["score_torch"] - THRESH["mean"]) <= BAND or abs(r["score_flax"] - THRESH["mean"]) <= BAND],
                     "P4_sharp_rank_moves": [(r["key"], r["rank_torch"], r["rank_flax"], r["class_torch"]) for r in table if abs(r["rank_shift"]) >= 40],
                     "P5_regimes_in_discordant_set": {"n_discordant": len(disc), "n_concordant": len(conc),
                                                      **{f: {"discordant": dist(disc, f), "concordant": dist(conc, f)} for f in ("coh", "d_pix", "mass_cv", "d_clip")},
                                                      "ic_kind_discordant": {k: sum(1 for r in disc if r["ic"].split(":")[0] == k) for k in ("IC-CAT", "IC-ORB", "IC-BLOB")},
                                                      "gn_discordant": {g: sum(1 for r in disc if r["params"]["gn"] == g) for g in (1, 2, 3)}}}
    # verdicts (rule A6 vocabulary)
    def verdict(subset_states):
        if not subset_states: return "UNRESOLVED"
        return "OBSERVER_STABLE" if all(s in ("STABLE_CROSSING", "STABLE_NON_CROSSING") for s in subset_states) else "OBSERVER_DEPENDENT"
    vA = verdict([by[k]["state_mean"] for k in CATALOGUE_CROSSERS if k in by]); vB = verdict([r["state_mean"] for r in gen]); vC = verdict([by[k]["state_mean"] for k in TORCH_BOTTOM10 if k in by])
    all_lost = all(r["state_mean"] == "LOST_CROSSING" for r in table if r["cross_mean_torch"]) if any(r["cross_mean_torch"] for r in table) else None
    res["verdicts"] = {"A": vA, "B": vB, "C": vC, "phenomenon_disappears_under_native_observer": all_lost,
                       "replication_authorised": (not all_lost) and all(v in ("OBSERVER_STABLE", "OBSERVER_DEPENDENT") for v in (vA, vB, vC)) and (controls["C-SELF"]["pass"] is not False) and (controls["C-STATIC"]["pass"] is not False)}
    json.dump(res, open(os.path.join(a.out, "harm56_map.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True, default=float)
    print(json.dumps({k: res[k] for k in ("n", "controls", "map", "classification", "verdicts")}, indent=1, default=float))
    print("A", res["A_catalogue_life_still_crosses"]["torch_crossers_status"]); print("B S2_135", res["B_genuine_still_crosses"]["S2_135"]); print("E order", res["E_ordering_of_regions"]["order_torch"], "->", res["E_ordering_of_regions"]["order_flax"])


if __name__ == "__main__":
    main()
