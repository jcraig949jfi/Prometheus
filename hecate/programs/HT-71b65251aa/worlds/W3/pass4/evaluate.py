"""Evaluator for HT-71b65251aa / W3 Pass 4. Reads rows.jsonl; writes PASS4_OUTCOME.json.

Order: controls for every arm set are computed and printed FIRST; treatment
statistics only if all are detected. Predicate from PREREG rules, in code.
"""
import json
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
THETA = "0.6"
# round-1 rule (R)
R_ACC_TOL, R_DEPTH_MAX, R_RHO_MIN = 0.01, 0.7 * 2, 0.4
# ORIG
ORIG_ACC_TOL = 0.005
# ALT
ALT_ELIG_GAP, ALT_ACC_TOL, ALT_DEPTH_FRAC, ALT_RHO_MIN = 0.02, 0.01, 0.8, 0.5
ATTEMPTS = 1  # every run of attack.py counts; update with a described reason only


def mean(xs):
    xs = list(xs)
    if any(x is None for x in xs):
        return None
    return float(np.mean(xs))


def arm(rows, attack, variant, name):
    return sorted([r for r in rows if r["attack"] == attack and r["variant"] == variant and r["arm"] == name],
                  key=lambda r: r["seed"])


def r_rule(acc, depth, rho, acc_l2):
    return [acc >= acc_l2 - R_ACC_TOL, depth <= R_DEPTH_MAX, rho is not None and rho >= R_RHO_MIN]


def alt_rule(acc, depth, rho, acc_l2, depth_l2):
    return [acc >= acc_l2 - ALT_ACC_TOL, depth <= ALT_DEPTH_FRAC * depth_l2, rho is not None and rho >= ALT_RHO_MIN]


def controls(rows, attack, variant, rule):
    P = arm(rows, attack, variant, "POSITIVE_CONTROL")
    thetas = list(P[0]["by_theta"].keys())
    pos = all(all(r["by_theta"][th]["all_depth0"] and r["by_theta"][th]["all_correct"]
                  and r["by_theta"][th]["n_unique"] >= 1 for r in P) for th in thetas)
    C = arm(rows, attack, variant, "CONTROL")
    acc_l2 = mean(r["fixed"]["L2"]["accuracy"] for r in C)
    dep_l2 = mean(r["fixed"]["L2"]["mean_depth"] for r in C)
    CH = arm(rows, attack, variant, "CHEAT")
    ch = {s: mean(r["injected"][s] for r in CH) for s in
          ("accuracy", "mean_depth", "spearman_depth_ambiguity", "spearman_depth_uncertainty")}
    cheat = all(rule(ch, acc_l2, dep_l2))
    return dict(positive_detected=bool(pos), cheat_detected=bool(cheat), n_seeds=len(P),
                min_unique_per_seed=min(r["by_theta"][thetas[0]]["n_unique"] for r in P), cheat_stats=ch)


def seedmeans(rows, attack, variant):
    C = arm(rows, attack, variant, "CONTROL")
    fixed = {k: {s: mean(r["fixed"][k][s] for r in C) for s in ("accuracy", "mean_depth")}
             for k in ("L0", "L1", "L2", "L3")}
    diag = {k: mean(r["diagnostics"][k] for r in C) for k in C[0]["diagnostics"]}
    keys = ("accuracy", "mean_depth", "spearman_depth_ambiguity", "spearman_depth_uncertainty", "spearman_depth_unc1")
    T = {th: {s: mean(r["by_theta"][th][s] for r in arm(rows, attack, variant, "TREATMENT")) for s in keys}
         for th in arm(rows, attack, variant, "TREATMENT")[0]["by_theta"]}
    for th in T:
        T[th]["depth_hist_total"] = np.sum([r["by_theta"][th]["depth_hist"]
                                            for r in arm(rows, attack, variant, "TREATMENT")], 0).tolist()
        for s in ("spearman_within_size3", "spearman_within_size4"):
            T[th][s] = mean(r["by_theta"][th][s] for r in arm(rows, attack, variant, "TREATMENT"))
    N = {th: {s: mean(r["by_theta"][th][s] for r in arm(rows, attack, variant, "NULL_TWIN")) for s in keys}
         for th in T}
    return fixed, diag, T, N


def main():
    t0 = time.process_time()
    rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8")]
    meta = json.load(open(os.path.join(HERE, "attack_meta.json"), encoding="utf-8"))
    alt_variants = meta["alt_variants_tried"]

    # ---- 1. controls first -------------------------------------------------
    r_rule_ch = lambda ch, a2, d2: r_rule(ch["accuracy"], ch["mean_depth"], ch["spearman_depth_ambiguity"], a2)
    alt_rule_ch = lambda ch, a2, d2: alt_rule(ch["accuracy"], ch["mean_depth"], ch["spearman_depth_uncertainty"], a2, d2)
    ctl = {"R/ORIGINAL": controls(rows, "R", "ORIGINAL", r_rule_ch)}
    for v in alt_variants:
        ctl[f"ALT/{v}"] = controls(rows, "ALT", v, alt_rule_ch)
    pos_all = all(c["positive_detected"] for c in ctl.values())
    cheat_all = all(c["cheat_detected"] for c in ctl.values())
    print("CONTROLS:", json.dumps({k: {kk: v[kk] for kk in ("positive_detected", "cheat_detected",
                                                             "min_unique_per_seed")} for k, v in ctl.items()}))

    out = {"triplicateId": "HT-71b65251aa", "world": "W3",
           "R": {"reproduced": False, "stats": {}}, "ORIG": {"fired": False, "stats": {}},
           "ALT": {"status": "NOT_ELIGIBLE", "stats": {}},
           "controls": {"positive_detected": pos_all, "cheat_detected": cheat_all, "by_arm_set": ctl},
           "predicate": "PARK", "anomalies": [], "core_minutes": None, "attempts": ATTEMPTS, "notes": ""}

    if not (pos_all and cheat_all):
        out["notes"] = "Controls not detected in every arm set; no treatment statistic computed. PARK."
    else:
        # ---- 2. R -----------------------------------------------------------
        fixed, diag, T, N = seedmeans(rows, "R", "ORIGINAL")
        a2 = fixed["L2"]["accuracy"]
        tr = r_rule(T[THETA]["accuracy"], T[THETA]["mean_depth"], T[THETA]["spearman_depth_ambiguity"], a2)
        tw = r_rule(N[THETA]["accuracy"], N[THETA]["mean_depth"], N[THETA]["spearman_depth_ambiguity"], a2)
        confound = [th for th in N if all(r_rule(N[th]["accuracy"], N[th]["mean_depth"],
                                                 N[th]["spearman_depth_ambiguity"], a2))]
        reproduced = all(tr) and not tw[0] and not confound
        out["R"] = {"reproduced": bool(reproduced), "stats": dict(
            seeds=sorted({r["seed"] for r in rows if r["attack"] == "R"}), theta=THETA, fixed=fixed,
            treatment_by_theta=T, twin_by_theta=N, diagnostics=diag,
            clauses_acc_depth_rho_theta06=tr, twin_clauses_theta06=tw, confound_thetas=confound)}

        # ---- 3. ORIG --------------------------------------------------------
        L1 = arm(rows, "ORIG", "ORIGINAL", "FIXED_L1"); AD = arm(rows, "ORIG", "ORIGINAL", "ADAPTIVE")
        l1a = mean(r["accuracy"] for r in L1); l1d = mean(r["mean_depth"] for r in L1)
        ada = {th: {s: mean(r["by_theta"][th][s] for r in AD) for s in ("accuracy", "mean_depth")}
               for th in AD[0]["by_theta"]}
        c_acc = l1a >= ada[THETA]["accuracy"] - ORIG_ACC_TOL
        c_dep = l1d <= ada[THETA]["mean_depth"]
        out["ORIG"] = {"fired": bool(c_acc and c_dep), "stats": dict(
            theta=THETA, fixed_L1_accuracy=l1a, fixed_L1_mean_depth=l1d, adaptive_by_theta=ada,
            clause_acc=bool(c_acc), clause_depth=bool(c_dep),
            fires_at_other_thetas={th: bool(l1a >= v["accuracy"] - ORIG_ACC_TOL and l1d <= v["mean_depth"])
                                   for th, v in ada.items()})}

        # ---- 4. ALT ---------------------------------------------------------
        alt_stats, status = {}, "NOT_ELIGIBLE"
        for v in alt_variants:
            f, dg, Ta, Na = seedmeans(rows, "ALT", v)
            gap = f["L2"]["accuracy"] - f["L1"]["accuracy"]
            elig = gap >= ALT_ELIG_GAP
            s = dict(eligible=bool(elig), gap_L2_minus_L1=gap, fixed=f, diagnostics=dg)
            if elig:
                cl = alt_rule(Ta[THETA]["accuracy"], Ta[THETA]["mean_depth"],
                              Ta[THETA]["spearman_depth_uncertainty"], f["L2"]["accuracy"], f["L2"]["mean_depth"])
                s.update(theta=THETA, clauses_acc_depth_rho=cl, treatment_by_theta=Ta, twin_by_theta=Na,
                         other_thetas_pass={th: all(alt_rule(Ta[th]["accuracy"], Ta[th]["mean_depth"],
                                                             Ta[th]["spearman_depth_uncertainty"],
                                                             f["L2"]["accuracy"], f["L2"]["mean_depth"]))
                                            for th in Ta})
                status = "PASS" if all(cl) else "FAIL"
            else:
                s.update(treatment_by_theta=Ta)
            alt_stats[v] = s
        out["ALT"] = {"status": status, "stats": dict(variants_tried=alt_variants, by_variant=alt_stats)}

        # ---- 5. predicate ---------------------------------------------------
        if out["ORIG"]["fired"] and status == "PASS":
            pred = "ORIG_FOSSIL_ALT_PASS"
        elif reproduced and status == "PASS" and not out["ORIG"]["fired"]:
            pred = "SURVIVES"
        else:
            pred = "PARK"
        out["predicate"] = pred

        an = []
        if abs(fixed["L2"]["accuracy"] - fixed["L3"]["accuracy"]) < 1e-9:
            an.append("R world: fixed L2 and L3 accuracies identical")
        if abs(fixed["L1"]["accuracy"] - a2) < 0.001:
            an.append(f"R world: fixed L1 within 0.001 of L2 ({fixed['L1']['accuracy']:.5f} vs {a2:.5f})")
        for v, s in alt_stats.items():
            if not s["eligible"]:
                an.append(f"{v}: not eligible, L2-L1 gap {s['gap_L2_minus_L1']:.5f} < 0.02")
            else:
                if s["twin_by_theta"][THETA]["accuracy"] >= s["fixed"]["L2"]["accuracy"] - ALT_ACC_TOL:
                    an.append(f"{v}: random-depth twin also within 0.01 of L2 at theta 0.6")
                if s["fixed"]["L3"]["accuracy"] > s["fixed"]["L2"]["accuracy"] + 1e-9:
                    an.append(f"{v}: fixed L3 beats L2 ({s['fixed']['L3']['accuracy']:.4f})")
        out["anomalies"] = an

        parts = [f"Predicate {pred}.",
                 f"R (seeds 100-109, theta 0.6): acc {T[THETA]['accuracy']:.4f} vs L2 {a2:.4f}, depth "
                 f"{T[THETA]['mean_depth']:.3f}, rho {T[THETA]['spearman_depth_ambiguity']:.3f}; twin acc "
                 f"{N[THETA]['accuracy']:.4f}; reproduced={reproduced}.",
                 f"ORIG: L1 acc {l1a:.5f} depth {l1d:.1f} vs adaptive acc {ada[THETA]['accuracy']:.5f} depth "
                 f"{ada[THETA]['mean_depth']:.3f}; fired={out['ORIG']['fired']}."]
        for v, s in alt_stats.items():
            p = f"ALT {v}: L1 {s['fixed']['L1']['accuracy']:.4f}, L2 {s['fixed']['L2']['accuracy']:.4f}, gap {s['gap_L2_minus_L1']:.4f}, eligible={s['eligible']}"
            if s["eligible"]:
                t = s["treatment_by_theta"][THETA]
                p += (f"; adaptive acc {t['accuracy']:.4f}, depth {t['mean_depth']:.3f} (max {0.8 * s['fixed']['L2']['mean_depth']:.2f}), "
                      f"rho(depth,H(L0)) {t['spearman_depth_uncertainty']}; clauses {s['clauses_acc_depth_rho']}")
            parts.append(p + ".")
        parts.append(f"ALT status {status}.")
        out["notes"] = " ".join(parts)

    out["core_minutes"] = round((meta["cpu_seconds"] + time.process_time() - t0) / 60.0, 4)
    with open(os.path.join(HERE, "PASS4_OUTCOME.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: out[k] for k in ("predicate", "anomalies", "core_minutes", "attempts", "notes")}, indent=1))


if __name__ == "__main__":
    main()
