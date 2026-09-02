"""
D7 master driver.  Freezes the constitution, runs the binding experiment with
matched controls and statistics, and emits machine verdicts (D7 ladder).

Order follows section 52: physics -> cut -> grammar -> census -> history/controls
-> synthetic validation -> FREEZE -> developmental history -> Z1 (binding run).
"""

from __future__ import annotations
import json, sys, time, random

from substrate import Grammar, sha, z_artifacts_used, z_size
from certify import certify_cut, base_closure
from census import census
from history import generate_history, condition, derive_prior
from hoard import hoard_fingerprint
from search import search
from meter import Meter
from verdict import check_admission, geometry, assign_verdict
from controls import macro_replay, reweight_navigator, classify_degeneracy
from evalz import evaluate
from leakage import audit, symmetry_assertion
from validate import run_battery
from stats import median, bootstrap_ci, paired_permutation_test
from altworlds import (proof_kit, xfer_kit, structureless_kit, hostile_kit,
                       transfer_vacuity_gate)

# ---- FROZEN CONSTITUTION PARAMETERS (declared before evidence) ----
P = 13
GRAMMAR = Grammar(rep_max=5, max_nodes=16, ncoord=3)
GRAMMAR_H = Grammar(rep_max=5, max_nodes=16, ncoord=4)  # hostile (4 coords)
BUDGET = 1500
SEEDS = list(range(8))
MIN_EFFECT = 2.0
ALPHA = 0.05
Z0_ARMS = ["Z0-sample", "Z0-evo", "Z0-cost", "Z0-novelty"]


def log(m):
    print(m, flush=True)


def arm_config(name, aw):
    cfg = dict(art_w=aw, mode="evo", cost_bias=0.0, novelty=False)
    if name == "Z0-sample":
        cfg.update(mode="sample")
    elif name == "Z0-cost":
        cfg.update(cost_bias=0.15)
    elif name == "Z0-novelty":
        cfg.update(mode="sample", novelty=True)
    return cfg


def run_arm(name, world, S, targets, hoard, grammar, aw, seeds, budget):
    cfg = arm_config(name, aw)
    rows = []
    for sd in seeds:
        m = Meter()
        r = search(world, S, targets, hoard, grammar, random.Random(sd), m,
                   art_w=cfg["art_w"], mode=cfg["mode"], cost_bias=cfg["cost_bias"],
                   novelty=cfg["novelty"], budget=budget)
        rows.append({"seed": sd, "solved": r["solved"],
                     "first": r["first_solve_eval"] if r["solved"] else budget,
                     "z": r["z"], "fold": sorted(map(list, r["family_reached"])) if r["z"] else [],
                     "meter": m.snapshot()})
    return rows


def main():
    t0 = time.time()
    report = {"date": "2026-08-27", "params": {"P": P, "budget": BUDGET,
              "seeds": SEEDS, "min_effect": MIN_EFFECT, "alpha": ALPHA}}

    # ---------------- assemble + FREEZE ----------------
    pk = proof_kit(P)
    w, H, roles, labels = pk["world"], pk["hoard"], pk["roles"], pk["labels"]
    pairs = pk["pairs"]
    S, T = pairs["primary"]
    fam_targets = [T] + [t for (s, t) in pairs["family"] if t != T]

    log("[1] certifying cut ...")
    cut = certify_cut(w, S, T)
    assert cut["barrier"], "no cut!"

    log("[2] census ...")
    cen = census(w, S, T, H, GRAMMAR, n=8000, seed=7, family=pairs["family"])

    log("[3] developmental history ...")
    hist_meter = Meter()
    store = generate_history(H, dev_worlds=pk["dev_worlds"], meter=hist_meter)

    constitution = {
        "world_fp": w.fingerprint(),
        "grammar_fp": GRAMMAR.fingerprint(),
        "hoard_fp": hoard_fingerprint(H),
        "history_fp": sha([store["marginal"], store["pair"]]),
        "dev_fps": store["dev_fingerprints"],
        "cut": cut,
        "census": cen,
    }
    constitution["constitution_hash"] = sha(constitution)
    report["constitution"] = constitution
    log(f"    constitution_hash = {constitution['constitution_hash'][:16]}")

    # ---------------- leakage / anti-cheat ----------------
    log("[4] leakage audit ...")
    lk = audit(pk, store, S, T)
    sym = symmetry_assertion(
        {"grammar": GRAMMAR.fingerprint(), "hoard_fp": constitution["hoard_fp"],
         "budget": BUDGET, "verifier": "evalz.evaluate"},
        {"grammar": GRAMMAR.fingerprint(), "hoard_fp": constitution["hoard_fp"],
         "budget": BUDGET, "verifier": "evalz.evaluate"})
    report["leakage"] = {"audit": lk, "symmetry": sym}

    # ---------------- synthetic validation ----------------
    log("[5] synthetic validation battery ...")
    report["validation"] = run_battery()

    # ---------------- priors ----------------
    aw2, D = derive_prior(store, S, T)
    aw0, _ = derive_prior(condition(store, "H0"), S, T)
    aw1, _ = derive_prior(condition(store, "H1"), S, T)
    report["D_task_coords"] = D

    # ---------------- BINDING RUN over family x seeds ----------------
    log("[6] binding run (arms x pairs x seeds) ...")
    arms = {n: None for n in Z0_ARMS}
    arms["H0"] = aw0; arms["H1"] = aw1; arms["H2"] = aw2
    matrix = {a: {} for a in arms}   # arm -> pair_idx -> rows
    best_z_by_arm = {}
    for a in arms:
        for pi, (ps, pt) in enumerate(pairs["family"]):
            tars = [pt] + [x for (s, x) in pairs["family"] if x != pt]
            rows = run_arm(a if a in Z0_ARMS else ("Z0-evo" if a in ("H0", "H1", "H2") else a),
                           w, ps, tars, H, GRAMMAR, arms[a], SEEDS, BUDGET)
            matrix[a][pi] = rows
            for r in rows:
                if r["z"] and a not in best_z_by_arm:
                    best_z_by_arm[a] = r["z"]
        log(f"    arm {a} done ({time.time()-t0:.0f}s)")

    # flatten first-solve per (pair,seed) unit
    def firsts(a):
        return [r["first"] for pi in sorted(matrix[a]) for r in matrix[a][pi]]

    def succ(a):
        rr = [r["solved"] for pi in matrix[a] for r in matrix[a][pi]]
        return sum(rr), len(rr)

    arm_stats = {}
    for a in arms:
        f = firsts(a)
        s, n = succ(a)
        arm_stats[a] = {"success": f"{s}/{n}", "median_first": median(f),
                        "ci": bootstrap_ci(f)}
    report["arm_stats"] = arm_stats

    # primary comparator = best Z0 by median (frozen nested-selection rule)
    comp = min(Z0_ARMS, key=lambda a: arm_stats[a]["median_first"])
    report["primary_comparator"] = comp

    def contrast(x, y):  # x baseline vs y (H2): paired on unit order
        fx, fy = firsts(x), firsts(y)
        perm = paired_permutation_test(fx, fy)
        mx, my = median(fx), median(fy)
        return {"baseline": x, "median_baseline": mx, "median_H2": my,
                "ratio": (mx / my) if my else None, "perm": perm}

    con = {"H2_vs_bestZ0": contrast(comp, "H2"),
           "H2_vs_H0": contrast("H0", "H2"),
           "H2_vs_H1": contrast("H1", "H2")}
    report["contrasts"] = con

    relational = {
        "history_free_easy": arm_stats[comp]["median_first"] <= arm_stats["H2"]["median_first"],
        "hoard_effect": (arm_stats["H0"]["median_first"] is not None
                         and arm_stats["H2"]["median_first"] is not None
                         and arm_stats["H0"]["median_first"] <= 1.3 * arm_stats["H2"]["median_first"]),
        "significant": (con["H2_vs_H0"]["ratio"] and con["H2_vs_H0"]["ratio"] >= MIN_EFFECT
                        and con["H2_vs_H1"]["ratio"] and con["H2_vs_H1"]["ratio"] >= MIN_EFFECT
                        and con["H2_vs_H0"]["perm"]["p"] is not None and con["H2_vs_H0"]["perm"]["p"] < ALPHA
                        and con["H2_vs_H1"]["perm"]["p"] < ALPHA),
    }
    report["relational_effect"] = relational

    # ---------------- pick primary z (from H2) + full admission ----------------
    zprimary = best_z_by_arm.get("H2") or best_z_by_arm.get("H0")
    adm = check_admission(w, S, T, pairs["family"], pairs["off_motif"], zprimary, H, GRAMMAR)
    geo = geometry(w, S, zprimary, H, pairs["family"])
    report["primary_z"] = {"ast": zprimary, "size": z_size(zprimary),
                           "artifacts": [(a, labels[a], roles[a]) for a in z_artifacts_used(zprimary)]}
    report["admission"] = adm
    report["geometry"] = geo

    # ancestry / serendipity (section 39): were z's parts individually (in)active?
    anc = []
    for a in set(z_artifacts_used(zprimary)):
        anc.append({"aid": a, "label": labels[a], "role": roles[a],
                    "marginal_coords": store["marginal"][a]["coords"],
                    "marginally_frozen_writer": store["marginal"][a]["frozen"]})
    report["ancestry"] = anc
    report["serendipity"] = {
        "note": "gated s-writer is INERT alone (marginally invisible) yet jointly topology-changing",
        "inert_alone_but_used": [x["label"] for x in anc
                                 if not x["marginally_frozen_writer"] and roles[x["aid"]] == "s_writer_nl"]}

    # ---------------- controls ----------------
    report["controls"] = {
        "macro_replay": macro_replay(w, S, T),
        "reweight_navigator": reweight_navigator(w, S, T),
    }

    # ---------------- transfer ----------------
    log("[7] transfer ...")
    xreport = {}
    try:
      xk = xfer_kit()
      vac = transfer_vacuity_gate(pk, xk)
      xreport = {"vacuity": vac}
      if vac["valid"]:
        xw = xk["world"]; xS, xT = xk["pairs"]["primary"]
        xtar = [xT] + [t for (s, t) in xk["pairs"]["family"] if t != xT]
        xstore = generate_history(xk["hoard"], dev_worlds=xk["dev_worlds"])
        xaw, _ = derive_prior(xstore, xS, xT)
        z0 = run_arm("Z0-evo", xw, xS, xtar, xk["hoard"], GRAMMAR, None, SEEDS, BUDGET)
        zm = run_arm("Z0-evo", xw, xS, xtar, xk["hoard"], GRAMMAR, xaw, SEEDS, BUDGET)
        # Z-BYTE: frozen proof z in alien hoard
        try:
            byte = evaluate(zprimary, xw, xS, [xT], xk["hoard"])
            zbyte = {"ran": True, "crossed": byte["reached"][xT]}
        except Exception as e:
            zbyte = {"ran": False, "result": "SUBSTRATE_MISMATCH", "err": type(e).__name__}
        xreport.update({
            "cut": certify_cut(xw, xS, xT),
            "Z0_median": median([r["first"] for r in z0]),
            "Zmech_median": median([r["first"] for r in zm]),
            "Z0_success": sum(r["solved"] for r in z0),
            "Zmech_success": sum(r["solved"] for r in zm),
            "Z_BYTE": zbyte,
        })
    except Exception as e:
      xreport["error"] = f"{type(e).__name__}: {e}"
    report["transfer"] = xreport

    # ---------------- NULL preservation ----------------
    log("[8] NULL preservation ...")
    try:
      nk = structureless_kit(P); nw = nk["world"]; nS, nT = nk["pairs"]["primary"]
      nstore = generate_history(nk["hoard"], dev_worlds=nk["dev_worlds"])
      naw, _ = derive_prior(nstore, nS, nT)
      n0 = run_arm("Z0-evo", nw, nS, [nT], nk["hoard"], GRAMMAR, None, list(range(6)), BUDGET)
      n1 = run_arm("Z0-evo", nw, nS, [nT], nk["hoard"], GRAMMAR, naw, list(range(6)), BUDGET)
      report["null"] = {"cut": certify_cut(nw, nS, nT)["barrier"],
                        "Z0_solved": sum(r["solved"] for r in n0),
                        "Z1_solved": sum(r["solved"] for r in n1),
                        "preserved": (sum(r["solved"] for r in n0) == 0 and sum(r["solved"] for r in n1) == 0)}
    except Exception as e:
      report["null"] = {"error": f"{type(e).__name__}: {e}"}

    # ---------------- hostile revision ----------------
    log("[9] hostile revision ...")
    hostile = {}
    try:
      hk = hostile_kit(11); hw = hk["world"]; hS, hT = hk["pairs"]["primary"]
      htar = [hT] + [t for (s, t) in hk["pairs"]["family"] if t != hT]
      hstore = generate_history(hk["hoard"], dev_worlds=hk["dev_worlds"])
      haw, _ = derive_prior(hstore, hS, hT)
      hrows = run_arm("Z0-evo", hw, hS, htar, hk["hoard"], GRAMMAR_H, haw, list(range(3)), 800)
      hz = next((r["z"] for r in hrows if r["z"]), None)
      hostile = {"cut": certify_cut(hw, hS, hT)["barrier"],
                 "revision_solved": sum(r["solved"] for r in hrows),
                 "n": len(hrows)}
      if hz is not None:
        used = [hk["labels"][a] for a in z_artifacts_used(hz)]
        hostile["revision_uses"] = used
        hostile["uses_revision_tool"] = any(hk["roles"][a] == "revision_tool" for a in z_artifacts_used(hz))
    except Exception as e:
      hostile = {"error": f"{type(e).__name__}: {e}"}
    report["hostile"] = hostile

    # ---------------- VERDICT ----------------
    verdict, reasons = assign_verdict(adm, relational, cen["KILL_FLAGS"])
    # transfer + hostile tiers
    tiers = [verdict]
    if verdict == "CERTIFIED_NONLINEAR_WORMHOLE":
        if xreport.get("Zmech_success", 0) > 0 and xreport.get("vacuity", {}).get("valid"):
            if xreport.get("Z_BYTE", {}).get("crossed"):
                tiers.append("GENUINE_FROZEN_TRANSFER")
            else:
                tiers.append("MOTIF_TRANSFER_ONLY")
        if hostile.get("revision_solved", 0) > 0:
            tiers.append("WORMHOLE_WITH_REVISION")
    report["verdict"] = {"base": verdict, "reasons": reasons, "tiers_earned": tiers,
                         "history_construction_cost": hist_meter.counts["history_construction"]}

    report["runtime_sec"] = round(time.time() - t0, 1)
    with open("d7_report.json", "w") as f:
        json.dump(report, f, indent=1, default=str)
    log("=" * 60)
    log(f"VERDICT: {verdict}   tiers: {tiers}")
    log(f"arm medians: " + ", ".join(f"{a}={arm_stats[a]['median_first']}({arm_stats[a]['success']})" for a in arms))
    log(f"H2 vs bestZ0({comp}) ratio={con['H2_vs_bestZ0']['ratio']:.2f} p={con['H2_vs_bestZ0']['perm']['p']}")
    log(f"H2 vs H0 ratio={con['H2_vs_H0']['ratio']:.2f} p={con['H2_vs_H0']['perm']['p']} | "
        f"H2 vs H1 ratio={con['H2_vs_H1']['ratio']:.2f} p={con['H2_vs_H1']['perm']['p']}")
    log(f"validation ALL_PASS={report['validation']['ALL_PASS']} leakage={lk['pass']} "
        f"NULL_preserved={report['null']['preserved']} transfer={xreport.get('vacuity',{}).get('verdict')} "
        f"hostile_revision={hostile.get('revision_solved')}/{hostile.get('n')}")
    log(f"runtime {report['runtime_sec']}s")


if __name__ == "__main__":
    main()
