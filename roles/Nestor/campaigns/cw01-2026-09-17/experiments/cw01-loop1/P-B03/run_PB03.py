"""P-B03: e07's damage family transplanted into e01's world (where state use DID evolve).

Parent T-E07 (x T-E01). Delta: between steps, a uniform random fraction f of the organism's
STORED region entries is deleted (selector sees keys only, never contents or importance);
the sham consumes the same draws and deletes nothing. Arms STATIC / WEATHER / SHAMWEATHER,
6 lineages each. After evolution every lineage's top-8 (by intact score on selection
streams) is assayed on matched test streams: intact, damaged at f=0.2, and a floor (the same
genome with p_write=0). Retention r = (S_dmg - F) / (S_int - F) as a ratio of means per
lineage. Primary: c in r_l = a + b*S_l + c*[WEATHER] over the 12 STATIC+WEATHER lineages,
exact relabelling (924). Unchanged: e01 economics, organism, episode structure, e01's
truncation selection (elite hardcoded n//4), lineage as unit.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402

W1 = L.import_world("cw01-e01", "world_e01")
PID, TID = "P-B03", "T-E07"
AID = "cw01-loop1-PB03"
ARMS = ("STATIC", "WEATHER", "SHAMWEATHER")
N_LIN, GENS, N_ORG = 6, 40, 64
SWEEP, F_TEST, TOP_K, N_SEL, N_TEST = (0.1, 0.2, 0.3), 0.2, 8, 8, 16
DELTA = 0.0005          # usefulness: intact minus floor per-episode score (e01 effects are ~0.003)


class WeatherRegion(W1.Region):
    """e01's Region with e07's representation-blind deletion between steps."""
    mode = "STATIC"
    frac = None            # None -> draw from SWEEP per episode
    rng = None

    def hold_tick(self):
        if WeatherRegion.mode != "STATIC" and WeatherRegion.rng is not None:
            r = WeatherRegion.rng
            f = WeatherRegion.frac if WeatherRegion.frac is not None else float(r.choice(SWEEP))
            keys = sorted(self._all().keys())
            k = int(round(f * len(keys)))
            if k > 0:
                pick = r.choice(len(keys), size=k, replace=False)      # keys only: blind
                if WeatherRegion.mode == "WEATHER":
                    for i in pick:
                        self.drop(keys[int(i)])
        return super().hold_tick()


_orig_run = W1.run_episode


def run_episode_w(genome, cfg, arm, stream_seed, policy_seed=None, intervention=None, **kw):
    WeatherRegion.rng = np.random.Generator(np.random.PCG64(S.seed(str(stream_seed), "weather")))
    return _orig_run(genome, cfg, arm, stream_seed, policy_seed, intervention, **kw)


W1.Region = WeatherRegion
W1.run_episode = run_episode_w


def score_pop(pop, cfg, streams, mode, frac):
    WeatherRegion.mode, WeatherRegion.frac = mode, frac
    out = np.zeros((len(pop), len(streams)))
    for i, g in enumerate(pop):
        for j, s in enumerate(streams):
            out[i, j] = W1.run_episode(g, cfg, "treatment", s, policy_seed=S.seed(AID, "policy|assay", j))["score"]
    return out


def main():
    t0 = time.time()
    cfg = L.load_cfg("cw01-e01", AID)
    ph = L.prereg(HERE, {
        "perturbation_id": PID, "parent": TID, "also": "T-E01", "attempt_id": AID, "claim_type": "confirmatory-transplant",
        "delta": "e07 damage family (blind deletion of a fraction of stored region entries between steps) + bit-matched sham inside e01's world; STATIC/WEATHER/SHAMWEATHER during evolution",
        "unchanged": "e01 economics, 5-gene organism, episode structure, e01 selection, arm-independent streams",
        "attacks": "e07 D059 (state use never evolved) and e01 I4 gap",
        "arms": ARMS, "lineages_per_arm": N_LIN, "generations": GENS, "n_org": N_ORG, "sweep": SWEEP, "f_test": F_TEST,
        "representatives": "top %d by intact score on %d selection streams (one rule for all arms)" % (TOP_K, N_SEL),
        "assay": "%d matched test streams: intact, damaged f=%.1f, floor = same genome with p_write=0" % (N_TEST, F_TEST),
        "statistic": "r_l = (sum S_dmg - sum F)/(sum S_int - sum F) over useful reps; c in r_l = a + b S_l + c[WEATHER], exact relabelling over 12 lineages",
        "decision": {"damage_fires": "mean r over STATIC lineages < 0.95, else INCONCLUSIVE (damage inert)",
                     "sham_inert": "SHAMWEATHER vs STATIC c inside [p05,p95], else CONTAMINATED",
                     "POSITIVE": "c_weather > p95 with the two checks above",
                     "NEGATIVE": "c_weather < p05", "NULL": "otherwise"},
        "seeds": "attempt id %s, per-lineage seed suffix; no prior production seed" % AID})

    lineages = []
    for arm in ARMS:
        for li in range(N_LIN):
            WeatherRegion.mode, WeatherRegion.frac = arm, None
            mk = lambda a, c, i, li=li: S.seed(a + "|L%d" % li, c, i)     # noqa: E731
            ev = W1.evolve(cfg, "treatment", GENS, N_ORG, mkseed=mk)
            pop = ev["final_pop"]
            sel = [S.seed(AID, "sel", j) for j in range(N_SEL)]
            s_sel = score_pop(pop, cfg, sel, "STATIC", None).mean(1)
            reps = [pop[i] for i in np.argsort(-s_sel)[:TOP_K]]
            test = [S.seed(AID, "test", j) for j in range(N_TEST)]
            s_int = score_pop(reps, cfg, test, "STATIC", None)
            s_dmg = score_pop(reps, cfg, test, "WEATHER", F_TEST)
            s_sham = score_pop(reps, cfg, test, "SHAMWEATHER", F_TEST)
            floor_pop = [dict(g, p_write=0.0) for g in reps]
            s_fl = score_pop(floor_pop, cfg, test, "STATIC", None)
            useful = (s_int.mean(1) - s_fl.mean(1)) >= DELTA
            if useful.sum() >= 1:
                num = (s_dmg[useful] - s_fl[useful]).sum()
                den = (s_int[useful] - s_fl[useful]).sum()
                r = float(num / den) if den > 0 else float("nan")
            else:
                r = float("nan")
            rec = {"arm": arm, "lineage": li, "S_int": float(s_int.mean()), "S_floor": float(s_fl.mean()),
                   "S_dmg": float(s_dmg.mean()), "sham_dev": float(np.abs(s_sham - s_int).max()),
                   "n_useful": int(useful.sum()), "r": r,
                   "gene_means": {g: float(np.mean([p[g] for p in reps])) for g in W1.GENE_NAMES},
                   "hist_last": ev["history"][-1]}
            lineages.append(rec)
            print("   %-11s L%d  S_int %.5f floor %.5f dmg %.5f  r %.3f  useful %d  sham_dev %.1e  p_write %.2f persist %.1f"
                  % (arm, li, rec["S_int"], rec["S_floor"], rec["S_dmg"], r, useful.sum(), rec["sham_dev"],
                     rec["gene_means"]["p_write"], rec["gene_means"]["persist_steps"]), flush=True)

    def arm_of(a):
        return [x for x in lineages if x["arm"] == a and np.isfinite(x["r"])]

    st, we, sh = arm_of("STATIC"), arm_of("WEATHER"), arm_of("SHAMWEATHER")
    damage_fires = bool(np.mean([x["r"] for x in st]) < 0.95) if st else False
    c_w = L.relabel_ancova([x["r"] for x in st], [x["S_int"] for x in st], [x["r"] for x in we], [x["S_int"] for x in we])
    c_s = L.relabel_ancova([x["r"] for x in st], [x["S_int"] for x in st], [x["r"] for x in sh], [x["S_int"] for x in sh])
    dI = L.relabel_diff([x["S_int"] for x in st], [x["S_int"] for x in we])
    sham_inert = bool(c_s["p05"] <= c_s["c"] <= c_s["p95"])
    if not damage_fires:
        disp = "INCONCLUSIVE (damage inert on STATIC lineages)"
    elif not sham_inert:
        disp = "CONTAMINATED (sham arm differs from static)"
    elif c_w["above_p95"]:
        disp = "POSITIVE (weather lineages retain more at matched intact score)"
    elif c_w["below_p05"]:
        disp = "NEGATIVE (weather lineages retain less)"
    else:
        disp = "NULL"
    res = {"perturbation_id": PID, "parent": TID, "disposition": disp,
           "damage_fires": damage_fires, "sham_inert": sham_inert, "c_weather": c_w, "c_sham": c_s,
           "intact_cost_weather_minus_static": dI,
           "arm_means": {a: {"r": float(np.mean([x["r"] for x in arm_of(a)])), "S_int": float(np.mean([x["S_int"] for x in arm_of(a)])),
                             "n": len(arm_of(a))} for a in ARMS},
           "lineages": lineages, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, res, ph)
    material = damage_fires   # if damage bites on an EVOLVED organism, e07's boundary was substrate-specific
    L.append_evidence(TID, PID, "e07's damage family posed in e01's world: %s; STATIC r %.3f, WEATHER r %.3f, c %.3f [%.3f, %.3f]"
                      % (disp, res["arm_means"]["STATIC"]["r"], res["arm_means"]["WEATHER"]["r"], c_w["c"], c_w["p05"], c_w["p95"]),
                      material, detail={"c_weather": c_w, "dI": dI}, state="ACTIVE",
                      state_reason="the question is posable in this world; next: severity dose and I2-style scramble")
    L.append_evidence("T-E01", PID, "e01 organisms under blind state deletion: retention r %.3f at f=0.2 (STATIC lineages)"
                      % res["arm_means"]["STATIC"]["r"], damage_fires, detail={"arm_means": res["arm_means"]})
    print("DISPOSITION %s  (%.0f s)" % (disp, time.time() - t0))


if __name__ == "__main__":
    main()
