"""P-B05 (serendipity): e02's ratchet world under e07-style weather.

Parent T-E02. Delta: during evolution a uniform random fraction of T4-bound region entries
is deleted between steps (blind selector; sham consumes the same draws). Arms STATIC /
WEATHER / SHAMWEATHER, 4 replicates each, e02's 80 generations. Rulers: e02's own
fixation order (p_norm vs p_factor at 75% travel) and neutral drift floor; gap =
fix(p_factor) - fix(p_norm). Descriptive (serendipity), with the exact relabelling band on
the gap. Unchanged: e02 economics, 9-gene organism, selection, detector procedure.
"""
from __future__ import annotations

import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402
import lineage as LG           # noqa: E402

W1 = L.import_world("cw01-e01", "world_e01")
W2 = L.import_world("cw01-e02", "world_e02")
PID, TID, AID = "P-B05", "T-E02", "cw01-loop1-PB05"
ARMS, N_REP, SWEEP = ("STATIC", "WEATHER", "SHAMWEATHER"), 4, (0.1, 0.2, 0.3)


class WeatherRegion(W1.Region):
    mode, rng = "STATIC", None

    def hold_tick(self):
        if WeatherRegion.mode != "STATIC" and WeatherRegion.rng is not None:
            r = WeatherRegion.rng
            f = float(r.choice(SWEEP))
            keys = sorted(self._all().keys())
            k = int(round(f * len(keys)))
            if k > 0:
                pick = r.choice(len(keys), size=k, replace=False)
                if WeatherRegion.mode == "WEATHER":
                    for i in pick:
                        self.drop(keys[int(i)])
        return super().hold_tick()


_orig = W2.run_episode


def run_episode_w(genome, cfg, arm, stream_seed, policy_seed=None, intervention=None, **kw):
    WeatherRegion.rng = np.random.Generator(np.random.PCG64(S.seed(str(stream_seed), "weather")))
    return _orig(genome, cfg, arm, stream_seed, policy_seed, intervention, **kw)


W2.Region = WeatherRegion
W2.run_episode = run_episode_w


def main():
    t0 = time.time()
    G = 80
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "serendipity-descriptive",
                         "delta": "blind deletion of a fraction of bound region entries between steps during evolution (WEATHER) with a draw-matched sham",
                         "unchanged": "e02 economics, organism, selection (elite 0.25, sigma 0.12), 80 generations, fixation ruler",
                         "attacks": "whether disruption is a pressure that changes which gene fixes first (foundation-first?) or the neutral drift floor",
                         "arms": ARMS, "replicates": N_REP, "sweep": SWEEP,
                         "statistic": "per replicate: fixation generation of p_norm and p_factor (75% travel), gap = fix_factor - fix_norm, neutral drift max_abs; arm contrast on gap by exact relabelling (C(8,4)=70)",
                         "decision": "descriptive; a change of ORDER (foundation-first majority under WEATHER but not STATIC) is recorded as material"})
    out = {a: [] for a in ARMS}
    for arm in ARMS:
        for rep in range(N_REP):
            WeatherRegion.mode = arm
            cfg = L.load_cfg("cw01-e02", AID + "|r%d" % rep)
            ev = W2.evolve(cfg, "treatment", G, cfg["population"]["organisms"], S.seed)
            fo = LG.fixation_order(ev["history"], "p_norm", "p_factor", W2.NEUTRAL_GENES)
            rec = {"rep": rep, "fix_norm": fo["fix_a"], "fix_factor": fo["fix_b"], "verdict": fo["verdict"],
                   "gap": (None if (fo["fix_a"] is None or fo["fix_b"] is None) else fo["fix_b"] - fo["fix_a"]),
                   "neutral_drift_max": fo["neutral_drift"]["max_abs"], "final_mean": ev["history"][-1]["mean"],
                   "ancestor_relative_pct": 100 * ev["history"][-1]["ancestor_relative"] / max(ev["ancestor_mean"], 1e-9),
                   "mean_ordered": ev["history"][-1]["mean_ordered"], "mean_binds": ev["history"][-1]["mean_binds"]}
            out[arm].append(rec)
            print("   %-11s r%d  norm@%s factor@%s  %s  gap %s  drift %.3f  anc-rel %+.1f%%  binds %.1f"
                  % (arm, rep, fo["fix_a"], fo["fix_b"], fo["verdict"], rec["gap"], rec["neutral_drift_max"],
                     rec["ancestor_relative_pct"], rec["mean_binds"]), flush=True)

    def gaps(a):
        return [x["gap"] for x in out[a] if x["gap"] is not None]

    contrast = L.relabel_diff(gaps("STATIC"), gaps("WEATHER")) if len(gaps("STATIC")) >= 2 and len(gaps("WEATHER")) >= 2 else None
    ff = {a: sum(1 for x in out[a] if x["verdict"] == "p_norm FIRST") for a in ARMS}
    order_changed = ff["WEATHER"] >= 3 and ff["STATIC"] <= 1
    res = {"perturbation_id": PID, "parent": TID, "foundation_first_count": ff, "gap_contrast_weather_minus_static": contrast,
           "neutral_drift_mean": {a: float(np.mean([x["neutral_drift_max"] for x in out[a]])) for a in ARMS},
           "ancestor_relative_mean_pct": {a: float(np.mean([x["ancestor_relative_pct"] for x in out[a]])) for a in ARMS},
           "runs": out, "elapsed_s": round(time.time() - t0, 1),
           "reading": "order changed under weather" if order_changed else "order unchanged (p_factor first remains the rule)"}
    L.result(HERE, res, ph)
    L.append_evidence(TID, PID, "e02 under weather: foundation-first %s; gap contrast %s" % (ff, contrast and round(contrast["effect"], 2)),
                      order_changed, detail={"gap_contrast": contrast, "drift": res["neutral_drift_mean"]})
    L.append_evidence("T-X01", PID, "neutral drift under STATIC/WEATHER/SHAM in e02: %s" % res["neutral_drift_mean"], False)
    print("DONE %s (%.0f s)" % (res["reading"], time.time() - t0))


if __name__ == "__main__":
    main()
