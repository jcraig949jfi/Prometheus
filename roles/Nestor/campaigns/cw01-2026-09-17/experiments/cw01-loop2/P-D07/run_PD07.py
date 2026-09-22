"""P-D07: P-B03 re-posed with the ABSOLUTE retained score and a severity dose.

Parent T-E07 (x T-E01). Same world, organism, damage family and sham as P-B03 (blind deletion
of a fraction of stored region entries between steps; STATIC / WEATHER / SHAMWEATHER during
evolution). Changes: 8 lineages per arm; the test severity is a dose f in {.1, .2, .3, .45}; the
ruler is the ABSOLUTE retained score above the floor A_f = mean(S_dmg,f - F) per lineage (the
ratio is reported beside it, never as the verdict; CW01-D071); contrast c_f in A_f = a + b S_int +
c[WEATHER] by exact relabelling over the 16 STATIC+WEATHER lineages at each f, plus the raw
difference of means with its relabelling band.
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
PID, TID, AID = "P-D07", "T-E07", "cw01-loop2-PD07"
ARMS, N_LIN, GENS, N_ORG = ("STATIC", "WEATHER", "SHAMWEATHER"), 8, 40, 64
SWEEP, DOSE, TOP_K, N_SEL, N_TEST = (0.1, 0.2, 0.3), (0.1, 0.2, 0.3, 0.45), 8, 8, 16


class WeatherRegion(W1.Region):
    mode, frac, rng = "STATIC", None, None

    def hold_tick(self):
        if WeatherRegion.mode != "STATIC" and WeatherRegion.rng is not None:
            r = WeatherRegion.rng
            f = WeatherRegion.frac if WeatherRegion.frac is not None else float(r.choice(SWEEP))
            keys = sorted(self._all().keys())
            k = int(round(f * len(keys)))
            if k > 0:
                pick = r.choice(len(keys), size=k, replace=False)
                if WeatherRegion.mode == "WEATHER":
                    for i in pick:
                        self.drop(keys[int(i)])
        return super().hold_tick()


_orig = W1.run_episode


def run_episode_w(genome, cfg, arm, stream_seed, policy_seed=None, intervention=None, **kw):
    WeatherRegion.rng = np.random.Generator(np.random.PCG64(S.seed(str(stream_seed), "weather")))
    return _orig(genome, cfg, arm, stream_seed, policy_seed, intervention, **kw)


W1.Region, W1.run_episode = WeatherRegion, run_episode_w


def score_pop(pop, cfg, streams, mode, frac):
    WeatherRegion.mode, WeatherRegion.frac = mode, frac
    return np.array([[W1.run_episode(g, cfg, "treatment", s, policy_seed=S.seed(AID, "policy|assay", j))["score"] for j, s in enumerate(streams)] for g in pop])


def main():
    t0 = time.time()
    cfg = L.load_cfg("cw01-e01", AID)
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "also": "T-E01", "claim_type": "reposed-confirmatory",
                         "delta": "absolute retained score above floor as ruler; severity dose at test; 8 lineages per arm",
                         "unchanged": "e01 world/organism/selection; e07 damage family and sham; training sweep %s" % (SWEEP,),
                         "attacks": "D071 (ill-conditioned ratio) and the dose dependence of the weather effect", "dose": DOSE, "lineages_per_arm": N_LIN,
                         "statistic": "A_f = mean over top-%d reps and %d test streams of (S_dmg - F); c_f in A_f = a + b S_int + c[WEATHER], exact relabelling (C(16,8)); sham arm must sit inside its band" % (TOP_K, N_TEST),
                         "decision": {"POSITIVE_at_f": "c_f > p95 and sham inside", "NEGATIVE_at_f": "c_f < p05", "NULL_at_f": "otherwise", "damage_fires": "STATIC A_f < S_int - F by > 5% at f=.2"},
                         "continuation": ["training severity sweep", "scramble instead of deletion", "damage timing relative to recurrence", "usefulness margin scaled to effect size"]})
    lineages = []
    for arm in ARMS:
        for li in range(N_LIN):
            WeatherRegion.mode, WeatherRegion.frac = arm, None
            mk = lambda a, c, i, li=li: S.seed(a + "|L%d" % li, c, i)     # noqa: E731
            ev = W1.evolve(cfg, "treatment", GENS, N_ORG, mkseed=mk)
            pop = ev["final_pop"]
            sel = [S.seed(AID, "sel", j) for j in range(N_SEL)]
            reps = [pop[i] for i in np.argsort(-score_pop(pop, cfg, sel, "STATIC", None).mean(1))[:TOP_K]]
            test = [S.seed(AID, "test", j) for j in range(N_TEST)]
            s_int = score_pop(reps, cfg, test, "STATIC", None)
            s_fl = score_pop([dict(g, p_write=0.0) for g in reps], cfg, test, "STATIC", None)
            rec = {"arm": arm, "lineage": li, "S_int": float(s_int.mean()), "F": float(s_fl.mean()), "margin": float((s_int - s_fl).mean()), "A": {}, "ratio": {}}
            for f in DOSE:
                s_d = score_pop(reps, cfg, test, "WEATHER", f)
                rec["A"][str(f)] = float((s_d - s_fl).mean())
                den = (s_int - s_fl).sum()
                rec["ratio"][str(f)] = float((s_d - s_fl).sum() / den) if den > 0 else float("nan")
            s_sh = score_pop(reps, cfg, test, "SHAMWEATHER", 0.2)
            rec["sham_dev"] = float(np.abs(s_sh - s_int).max())
            lineages.append(rec)
            print("   %-11s L%d S_int %.5f margin %.5f A %s" % (arm, li, rec["S_int"], rec["margin"], {k: round(v, 5) for k, v in rec["A"].items()}), flush=True)

    def arm(a):
        return [x for x in lineages if x["arm"] == a]
    st, we, sh = arm("STATIC"), arm("WEATHER"), arm("SHAMWEATHER")
    results = {}
    for f in DOSE:
        k = str(f)
        c_w = L.relabel_ancova([x["A"][k] for x in st], [x["S_int"] for x in st], [x["A"][k] for x in we], [x["S_int"] for x in we])
        c_s = L.relabel_ancova([x["A"][k] for x in st], [x["S_int"] for x in st], [x["A"][k] for x in sh], [x["S_int"] for x in sh])
        raw = L.relabel_diff([x["A"][k] for x in st], [x["A"][k] for x in we])
        sham_ok = c_s["p05"] <= c_s["c"] <= c_s["p95"]
        disp = ("POSITIVE" if (c_w["above_p95"] and sham_ok) else "NEGATIVE" if c_w["below_p05"] else "NULL") if sham_ok else "CONTAMINATED"
        results[k] = {"c_weather": c_w, "c_sham": c_s, "raw": raw, "disposition": disp,
                      "A_mean": {a: float(np.mean([x["A"][k] for x in arm(a)])) for a in ARMS}, "ratio_mean": {a: float(np.nanmean([x["ratio"][k] for x in arm(a)])) for a in ARMS}}
    fires = float(np.mean([x["A"]["0.2"] for x in st])) < 0.95 * float(np.mean([x["margin"] for x in st]))
    dI = L.relabel_diff([x["S_int"] for x in st], [x["S_int"] for x in we])
    out = {"perturbation_id": PID, "parent": TID, "damage_fires": fires, "by_dose": results, "intact_cost": dI,
           "margin_mean": {a: float(np.mean([x["margin"] for x in arm(a)])) for a in ARMS}, "lineages": lineages, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    summary = {k: (v["disposition"], round(v["A_mean"]["STATIC"], 5), round(v["A_mean"]["WEATHER"], 5)) for k, v in results.items()}
    material = any(v["disposition"] in ("POSITIVE", "NEGATIVE") for v in results.values())
    L.append_evidence(TID, PID, "absolute-retention dose: %s; intact cost %.5f [%.5f, %.5f]; damage fires %s" % (summary, dI["effect"], dI["p05"], dI["p95"], fires), material, detail={"by_dose": {k: {"disp": v["disposition"], "c": v["c_weather"]} for k, v in results.items()}})
    print("DONE %s (%.0f s)" % (summary, time.time() - t0))


if __name__ == "__main__":
    main()
