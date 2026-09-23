"""cw01-e08 QUALIFICATION: Q1-Q7 with broken fixtures, on DISJOINT seeds; freezes nothing itself.

Every numerical pressure parameter (lambda, G, g_amp) is DERIVED here by the rule written in
PREREGISTRATION.md section 6 after its attainable range is measured, and written to
QUALIFY.json as a proposal. freeze_e08.py then copies the proposal into WORLD.json and hashes
the verdict contract. If any predicate fails, exit 1 and e08 is INCONCLUSIVE.

Seed policy: every draw here uses seed components 'pilot', 'q3', 'q7' under the attempt_id;
production lineages use 'evo'. No overlap by construction; recorded in QUALIFY.json.
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
import seeds as S              # noqa: E402
import world_e08 as W          # noqa: E402


def ck(res, name, passed, detail):
    res[name] = {"passed": bool(passed), "detail": detail}
    print("   %-38s %s" % (name, "PASS" if passed else "FAIL"))
    return bool(passed)


def js(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.bool_):
        return bool(o)
    return str(o)


# ----------------------------------------------------------------- helpers

def held(cfg, spec, pop):
    hs = W.held_seeds(cfg)
    ro = W.rollout(spec, pop, hs)
    return ro["fit"] / len(hs), ro["live_ticks"]


def truncated(pop, cfg, spec, n):
    q = W.copy_pop(pop)
    for _ in range(n):
        W.amputate(q, cfg, spec, sham=False)
    return q


def all_single_truncations(pop, p, cfg, spec):
    """Every eligible single-bond truncation of organism p (one per bond with r_k > 1)."""
    one = W.take(pop, [p])
    outs = []
    for k in range(one["rk"].shape[1]):
        if one["rk"][0, k] > 1:
            q = W.copy_pop(one)
            q["rk"][0, k] -= 1
            W.enforce_pad(q, cfg, spec)
            outs.append(q)
    return outs


def cat_all(pops):
    out = pops[0]
    for q in pops[1:]:
        out = W.concat(out, q)
    return out


# ----------------------------------------------------------------- main

def main():
    t0 = time.time()
    cfg = json.loads((HERE / "WORLD.json").read_text(encoding="utf-8"))
    aid = cfg["attempt_id"]
    spec = W.world_spec(cfg)
    gc, tc, ac = cfg["gate"], cfg["tax"], cfg["assay"]
    floor_h = ac["competence_floor_held64"]
    res, fixtures = {}, {}
    ok = True
    print("########## cw01-e08 QUALIFICATION (disjoint seeds) ##########")

    # ---- Q1 (i): floors --------------------------------------------------------
    ftr = W.trivial_floors(spec, W.train_seeds(cfg))
    fhe = W.trivial_floors(spec, W.held_seeds(cfg))
    print("   train floors %s | held64 floors %s" % (ftr["per_seed"], fhe["per_seed"]))
    best_trivial_train = ftr["best_constant"]

    # ---- pilot: 4 CONTROL lineages, own seed component ----------------------------
    print("\n-- pilot: %d CONTROL lineages x %d generations --" % (gc["pilot_lineages"], gc["pilot_generations"]))
    pilots = []
    for j in range(gc["pilot_lineages"]):
        t1 = time.time()
        ev = W.evolve(cfg, spec, aid, "CONTROL", j, gc["pilot_generations"], lam=0.0, g_amp=None,
                      seed_component="pilot", history_every=5)
        pilots.append(ev)
        print("   pilot %d: %.1f s  fit max %d  scalar mean %.3f" % (j, time.time() - t1, ev["fit"].max(),
                                                                    ev["history"][-1]["scalar_mean"]))
    # generation at which the MEDIAN (over pilots) top fitness first clears best trivial train fit
    gens = [h["gen"] for h in pilots[0]["history"]]
    med_top = [float(np.median([p["history"][i]["fit_max"] for p in pilots])) for i in range(len(gens))]
    first = next((g for g, m in zip(gens, med_top) if m > best_trivial_train), None)
    if first is None:
        G_prop = None
    else:
        G_prop = int(min(800, max(200, int(np.ceil(2 * max(first, 1) / 50.0)) * 50)))
    g_amp_prop = (max(5, G_prop // 40) if G_prop else None)
    print("   median top fitness first clears %d at generation %s -> G %s, g_amp %s"
          % (best_trivial_train, first, G_prop, g_amp_prop))

    # representatives + held64
    reps, rep_lineage = [], []
    for j, ev in enumerate(pilots):
        r, _ = W.representatives(ev["pop"], ev["fit"], gc["pilot_top_k"])
        reps.append(r)
        rep_lineage += [j] * gc["pilot_top_k"]
    elites = cat_all(reps)
    rep_lineage = np.array(rep_lineage)
    h_el, lt_el = held(cfg, spec, elites)
    B_el = W.burden(elites, cfg, spec)
    sb_el = W.scalar_burden(B_el, cfg, spec)
    comp_el = h_el > floor_h
    print("   pilot elites: held64 min/med/max %.1f/%.1f/%.1f | competent %d/%d | scalar %.2f..%.2f"
          % (h_el.min(), np.median(h_el), h_el.max(), comp_el.sum(), len(h_el), sb_el.min(), sb_el.max()))
    ok &= ck(res, "Q1_computation_exists", comp_el.any(),
             {"floors_train": ftr, "floors_held64": fhe, "n_competent_elites": int(comp_el.sum()),
              "held64_max": float(h_el.max()), "competence_floor": floor_h})

    # ---- Q2: burden has range among competent organisms -----------------------------
    cal = [elites]
    cal_tag = [np.zeros(len(h_el), int)]
    for n in gc["calibration_truncations"]:
        cal.append(truncated(elites, cfg, spec, n))
        cal_tag.append(np.full(len(h_el), n))
    calpop = cat_all(cal)
    cal_tag = np.concatenate(cal_tag)
    h_cal, lt_cal = held(cfg, spec, calpop)
    B_cal = W.burden(calpop, cfg, spec)
    sb_cal = W.scalar_burden(B_cal, cfg, spec)
    comp_cal = h_cal > floor_h
    if comp_cal.sum() >= 2:
        rng_factor = float(sb_cal[comp_cal].max() / max(sb_cal[comp_cal].min(), 1e-9))
    else:
        rng_factor = 0.0
    ok &= ck(res, "Q2_burden_has_range", rng_factor >= gc["q2_range_factor_min"],
             {"range_factor": rng_factor, "required": gc["q2_range_factor_min"],
              "n_competent": int(comp_cal.sum()), "n_total": int(len(h_cal)),
              "competent_by_truncation": {int(n): int(comp_cal[cal_tag == n].sum()) for n in np.unique(cal_tag)},
              "scalar_competent_min_max": [float(sb_cal[comp_cal].min()), float(sb_cal[comp_cal].max())]
              if comp_cal.any() else None})

    # ---- Q3: tax attainability curve on the train seeds ---------------------------
    ro_cal = W.rollout(spec, calpop, W.train_seeds(cfg))
    fit_cal = ro_cal["fit"].astype(float)
    comp_train = comp_cal                       # competence defined on held64 (tax-free assay)
    H = float(np.median(fit_cal[comp_train]) - best_trivial_train) if comp_train.any() else 0.0
    Bmax_scalar = float(sum(tc["weights"]))
    lam_max = H / Bmax_scalar if H > 0 else 0.0
    # the inactive organism at MINIMAL burden: the worst case for "inactivity is optimal"
    d, R, A, Wd = W.dims(cfg, spec)
    sb_min = float(W.scalar_burden({"bond": np.array([d + 1]), "params": np.array([1 + 16 * d + A]),
                                    "flops": np.array([d + A]), "bits": np.array([0])}, cfg, spec)[0])
    sd0 = float(fit_cal[comp_train].std()) if comp_train.sum() > 1 else 0.0
    curve = []
    chosen = None
    for frac in tc["sweep_fractions"]:
        lam = frac * lam_max
        sel = fit_cal - lam * sb_cal
        selc = sel[comp_train]
        rho = W.spearman(selc, sb_cal[comp_train]) if comp_train.sum() > 2 else 0.0
        sel_abst = ftr["abstain"] - lam * sb_min
        a_ok = rho <= -tc["q3_gradient_min"]
        b_ok = bool(selc.max() > sel_abst) if comp_train.any() else False
        c_inactive_optimal = not b_ok
        dyn = float(selc.std() / sd0) if sd0 > 0 else 0.0
        d_ok = dyn >= tc["q3_dynamic_range_min"]
        row = {"fraction": frac, "lambda": lam, "spearman_sel_vs_scalar": rho, "gradient_ok": bool(a_ok),
               "best_competent_sel": float(selc.max()) if comp_train.any() else None,
               "abstain_min_burden_sel": sel_abst, "competence_attainable": b_ok,
               "inactivity_optimal": bool(c_inactive_optimal), "dynamic_range": dyn, "dynamic_ok": bool(d_ok),
               "qualifies": bool(a_ok and b_ok and (not c_inactive_optimal) and d_ok)}
        curve.append(row)
        if row["qualifies"]:
            chosen = row
        print("   lambda %.4f (x%.4f): rho %+.3f | best sel %.1f vs abstain %.1f | dyn %.2f | %s"
              % (lam, frac, rho, row["best_competent_sel"] or 0, sel_abst, dyn, "OK" if row["qualifies"] else "-"))
    ok &= ck(res, "Q3_tax_fires_without_killing", chosen is not None,
             {"headroom_H": H, "lambda_max": lam_max, "scalar_min_burden": sb_min, "curve": curve,
              "chosen": chosen})

    # ---- Q4: accessibility ----------------------------------------------------------
    comp_idx = np.where(comp_el)[0]
    ret = []
    for p in comp_idx:
        variants = all_single_truncations(elites, int(p), cfg, spec)
        if not variants:
            continue
        hv, _ = held(cfg, spec, cat_all(variants))
        ret.append(float(np.mean(hv > floor_h)))
    local_ret = float(np.mean(ret)) if ret else 0.0
    per_lineage_comp = [bool(comp_el[rep_lineage == j].any()) for j in range(gc["pilot_lineages"])]
    q4a = local_ret >= gc["q4_local_retention_min"]
    q4b = sum(per_lineage_comp) >= gc["q4_pilot_competent_min"]
    ok &= ck(res, "Q4_evolution_reaches_ridge", (q4a or q4b) and G_prop is not None,
             {"A_local_retention": local_ret, "A_required": gc["q4_local_retention_min"], "A_ok": bool(q4a),
              "B_pilot_lineages_competent": per_lineage_comp, "B_ok": bool(q4b),
              "first_clear_generation": first, "G_proposed": G_prop, "g_amp_proposed": g_amp_prop,
              "median_top_fitness_trajectory": dict(zip(map(str, gens), med_top))})

    # ---- Q5: sham inert, intervention not ---------------------------------------------
    base = pilots[0]["pop"]
    sh = W.copy_pop(base)
    W.amputate(sh, cfg, spec, sham=True)
    sham_identical = all(np.array_equal(sh[k], base[k]) for k in base)
    am = W.copy_pop(base)
    info = W.amputate(am, cfg, spec, sham=False)
    amp_changes = int(sum((not np.array_equal(am[k], base[k])) for k in ("G", "rk", "al", "Wo")))
    ok &= ck(res, "Q5_sham_inert_intervention_not", sham_identical and info["n_changed"] > 0,
             {"sham_identical": sham_identical, "amputation_changed_organisms": info["n_changed"],
              "arrays_changed": amp_changes})
    # broken fixture: a leaky sham
    leaky = W.copy_pop(base)
    W.amputate(leaky, cfg, spec, sham=True)
    leaky["rk"][0, W.widest_bond(leaky["rk"])[0]] -= 1
    W.enforce_pad(leaky, cfg, spec)
    fixtures["Q5_leaky_sham"] = {"detected": not all(np.array_equal(leaky[k], base[k]) for k in base)}

    # ---- Q6: accounting fixtures -------------------------------------------------------
    def one_org(rk_fill, mk_fill, C_fill):
        q = W.init_population(cfg, spec, np.random.default_rng(99), 1)
        q["rk"][:] = rk_fill
        q["mk"][:] = mk_fill
        q["C"][:] = C_fill
        q["C"][:, 0] = 0
        return W.enforce_pad(q, cfg, spec)

    # 1 always-abstain
    q1 = one_org(3, True, 0)
    h1, lt1 = held(cfg, spec, q1)
    B1 = W.burden(q1, cfg, spec)
    fixtures["Q6_1_always_abstain"] = {"held64": float(h1[0]), "abstain_floor": fhe["per_seed"]["abstain"],
                                       "scalar_charged": float(W.scalar_burden(B1, cfg, spec)[0]),
                                       "outcome": "CHARGED_NONCOMPETENT" if (h1[0] <= floor_h and
                                                                            W.scalar_burden(B1, cfg, spec)[0] > 0) else "WRONG"}
    # 2 reduced participation: an organism that ALWAYS acts 7 (the costliest action) dies at ~tick 25 of 32
    # (measured: constant action 7 gives 25.6 live ticks, final charge 0). First fixture build let the TT
    # pick the abstain row often enough to survive (QUALIFY run 1); repaired so the forward cannot abstain:
    # all cores masked -> the contraction is a fixed vector v; Wo makes index 1 win for that v.
    q2 = one_org(3, False, 15)
    rk2 = q2["rk"][0]
    v = q2["al"][0, :rk2[0]].astype(np.float64)
    for c in range(d):
        v = v @ q2["G"][0, c, 0, :rk2[c], :rk2[c + 1]].astype(np.float64)
        v /= max(np.abs(v).max(), 1e-300)
    q2["Wo"][:] = 0.0
    q2["Wo"][0, :rk2[d], :] = -v[:, None]
    q2["Wo"][0, :rk2[d], 1] = v
    W.enforce_pad(q2, cfg, spec)
    probe_obs = np.random.default_rng(3).integers(0, 65536, size=(64, spec.D))
    always_acts = bool((W.forward(W.take(q2, [0] * 64), probe_obs, np.arange(64), spec) == 1).all())
    h2, lt2 = held(cfg, spec, q2)
    B2 = W.burden(q2, cfg, spec)
    twin = W.copy_pop(q2)                       # the SAME genome, abstaining: its own static-burden reference
    twin["C"][:] = 0
    B2t = W.burden(twin, cfg, spec)
    _, lt2t = held(cfg, spec, twin)
    same_static = all(B2[c][0] == B2t[c][0] for c in W.COORDS)
    fixtures["Q6_2_reduced_participation"] = {
        "always_acts_7": always_acts,
        "live_ticks": float(lt2[0]), "full_ticks_of_abstaining_twin": float(lt2t[0]), "held64": float(h2[0]),
        "static_burden_equal_to_own_abstaining_twin": same_static,
        "outcome": "CHARGED_LOWER_WORK_VISIBLE" if (lt2[0] < lt2t[0] and same_static and h2[0] <= floor_h)
        else "WRONG"}
    # 3 deferred work impossible: statelessness -> per-row actions independent of row order
    rng = np.random.default_rng(7)
    obs = rng.integers(0, 65536, size=(256, spec.D))
    sub = W.take(elites, [0] * 256)
    a1 = W.forward(sub, obs, np.arange(256), spec)
    perm = rng.permutation(256)
    a2 = W.forward(sub, obs[perm], np.arange(256), spec)
    stateless = bool(np.array_equal(a1[perm], a2))
    fixtures["Q6_3_deferred_work"] = {"stateless_by_construction": stateless,
                                      "outcome": "IMPOSSIBLE_VERIFIED" if stateless else "WRONG"}
    # 4 hidden memory: extra bytes refused by the loader
    rec = W.pack(elites, cfg, spec)
    rt = W.unpack(rec, cfg, spec)
    roundtrip = all(np.array_equal(rt[k], elites[k]) for k in elites)
    extra = np.concatenate([rec, np.zeros((rec.shape[0], 8), np.uint8)], axis=1)
    try:
        W.unpack(extra, cfg, spec)
        refused = False
    except W.GenomeRefused:
        refused = True
    fixtures["Q6_4_hidden_memory"] = {"roundtrip_exact": roundtrip, "extra_bytes_refused": refused,
                                      "outcome": "REFUSED" if (refused and roundtrip) else "WRONG"}
    # 5 recomputation for storage: rank 1, all bits
    q5 = one_org(1, True, 0)
    B5 = {c: float(v[0]) for c, v in W.burden(q5, cfg, spec).items()}
    # 6 storage for contractions: R_max, no bits
    q6 = one_org(R, False, 0)
    B6 = {c: float(v[0]) for c, v in W.burden(q6, cfg, spec).items()}
    fixtures["Q6_5_recompute_for_storage"] = {"vector": B5, "scalar": float(W.scalar_burden(W.burden(q5, cfg, spec), cfg, spec)[0]),
                                              "outcome": "CHARGED_SHIFT_VISIBLE" if (B5["bits"] == 4 * d and B5["params"] < B6["params"]
                                                                                    and W.scalar_burden(W.burden(q5, cfg, spec), cfg, spec)[0] > 0) else "WRONG"}
    fixtures["Q6_6_storage_for_contractions"] = {"vector": B6, "scalar": float(W.scalar_burden(W.burden(q6, cfg, spec), cfg, spec)[0]),
                                                 "outcome": "CHARGED_SHIFT_VISIBLE" if (B6["bits"] == 0 and B6["flops"] > B5["flops"]) else "WRONG"}
    # 7 counter bypass
    q7 = W.take(elites, [0])
    r0 = int(q7["rk"][0, 0])
    if r0 < R:
        q7["al"][0, r0] = 1.0
    else:
        q7["rk"][0, 0] = R - 1
    try:
        W.burden(q7, cfg, spec)
        bypass_refused = False
    except W.BurdenRefused:
        bypass_refused = True
    fixtures["Q6_7_counter_bypass"] = {"outcome": "REFUSED" if bypass_refused else "WRONG"}
    # 8 structural deletion must not change evaluation opportunity
    sig_before = (spec.T, spec.S, spec.W, spec.wid, tuple(W.held_seeds(cfg).tolist()))
    abst = one_org(3, True, 0)
    ro_a = W.rollout(spec, abst, W.held_seeds(cfg)[:8], hash_obs=True)
    W.amputate(abst, cfg, spec, sham=False)
    ro_b = W.rollout(spec, abst, W.held_seeds(cfg)[:8], hash_obs=True)
    sig_after = (spec.T, spec.S, spec.W, spec.wid, tuple(W.held_seeds(cfg).tolist()))

    def bad_amputate(pop, spec_):
        W.amputate(pop, cfg, spec_, sham=False)
        spec_.T -= 1                                     # the broken operator shortens the horizon
    spec_copy = W.world_spec(cfg)
    bad_amputate(W.copy_pop(abst), spec_copy)
    bad_detected = (spec_copy.T, spec_copy.S, spec_copy.W, spec_copy.wid) != sig_before[:4]
    fixtures["Q6_8_opportunity_invariant"] = {
        "spec_unchanged_by_amputation": sig_before == sig_after,
        "obs_stream_unchanged_for_fixed_actions": ro_a["obs_hash"] == ro_b["obs_hash"],
        "broken_operator_detected": bool(bad_detected),
        "outcome": "INVARIANT_HELD_AND_BROKEN_DETECTED" if (sig_before == sig_after and ro_a["obs_hash"] == ro_b["obs_hash"]
                                                            and bad_detected) else "WRONG"}
    q6_all = all(v["outcome"] != "WRONG" for k, v in fixtures.items() if k.startswith("Q6_"))
    ok &= ck(res, "Q6_accounting_fixtures", q6_all, {k: v["outcome"] for k, v in fixtures.items() if k.startswith("Q6_")})

    # ---- Q7: determinism / blindness --------------------------------------------------
    a = W.evolve(cfg, spec, aid, "TAX+AMP", 0, 30, lam=lam_max * 0.5, g_amp=5, seed_component="q7", history_every=0)
    b = W.evolve(cfg, spec, aid, "TAX+AMP", 0, 30, lam=lam_max * 0.5, g_amp=5, seed_component="q7", history_every=0)
    det = all(np.array_equal(a["pop"][k], b["pop"][k]) for k in a["pop"]) and np.array_equal(a["fit"], b["fit"])
    # broken fixture: a clock-seeded run
    import inspect
    c1 = W.evolve(cfg, spec, "clock-%f" % time.time(), "TAX+AMP", 0, 5, lam=0.0, g_amp=None, seed_component="q7x", history_every=0)
    c2 = W.evolve(cfg, spec, "clock-%f" % time.time(), "TAX+AMP", 0, 5, lam=0.0, g_amp=None, seed_component="q7x", history_every=0)
    clock_detected = not all(np.array_equal(c1["pop"][k], c2["pop"][k]) for k in c1["pop"])
    fixtures["Q7_clock_seeded"] = {"detected": clock_detected}
    blind = "arm" not in inspect.signature(W.assay).parameters
    ok &= ck(res, "Q7_determinism_blindness", det and blind,
             {"lineage_replay_identical": det, "assay_signature_has_no_arm": blind,
              "assay_params": list(inspect.signature(W.assay).parameters)})

    fixtures_ok = all(v.get("detected", True) for v in fixtures.values()) and q6_all
    # ---- lineage count / MDE from the disjoint pilot ------------------------------------
    lin_scalar = [float(sb_el[rep_lineage == j].mean()) for j in range(gc["pilot_lineages"])]
    sd_l = float(np.std(lin_scalar, ddof=1))
    n_per_level = 2 * cfg["lineages_per_arm"]
    mde = 2.5 * sd_l * np.sqrt(2.0 / n_per_level)
    power = {"pilot_lineage_scalar_means": lin_scalar, "between_lineage_sd": sd_l,
             "n_per_tax_level": n_per_level, "mde_scalar_burden_approx": float(mde),
             "_rule": "MDE ~ 2.5 * SD * sqrt(2/n) at alpha 0.05 one-sided, power 0.8; lineage count is NOT changed after outcomes"}

    proposal = {"lambda": (chosen["lambda"] if chosen else None),
                "lambda_fraction": (chosen["fraction"] if chosen else None),
                "weights": tc["weights"], "generations": G_prop, "g_amp": g_amp_prop,
                "s_amp": ac["s_amp"], "lineages_per_arm": cfg["lineages_per_arm"]}
    verdict = "QUALIFIED" if (ok and fixtures_ok) else "REFUSED"
    out = {"campaign_id": cfg["campaign_id"], "experiment_id": cfg["experiment_id"], "attempt_id": aid,
           "phase": "QUALIFY", "ts": time.strftime("%Y-%m-%d %H:%M:%S"), "elapsed_s": round(time.time() - t0, 1),
           "world": {"gen_seed": cfg["world"]["gen_seed"], "wid": spec.wid, "T": spec.T, "S": spec.S, "W": spec.W,
                     "D": spec.D, "d": spec.d, "R_max": R, "record_nbytes": W.record_nbytes(cfg, spec)},
           "seed_components_used": ["pilot", "q7", "q7x"], "production_seed_component": "evo",
           "predicates": res, "fixtures": fixtures, "fixtures_all_detected": fixtures_ok,
           "power": power, "proposal": proposal, "verdict": verdict,
           "_rule": "predicates are never relaxed after observing a failure"}
    (HERE / "QUALIFY.json").write_text(json.dumps(out, indent=1, ensure_ascii=True, default=js), encoding="utf-8")
    print("\n== %s (%.0f s) == proposal %s" % (verdict, time.time() - t0, proposal))
    return 0 if verdict == "QUALIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
