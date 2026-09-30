"""Evaluate HT-a9e2ba7618 / W4 from rows.jsonl only; writes OUTCOME.json."""
import json
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")
OUT = os.path.join(HERE, "OUTCOME.json")

W0, WH = "0.0", "0.4"
PC_THRESH = 0.98


def success_pred(T, C, N):
    """Spec success_criterion, thresholds unchanged. T,C,N: dict w->mean acc."""
    return bool(T[WH] >= 0.9 and (T[W0] - T[WH]) <= 0.05
                and (C[W0] - C[WH]) >= 0.3 and (N[W0] - N[WH]) >= 0.3)


def null_same_invariance(N):
    return bool(N[WH] >= 0.9 and (N[W0] - N[WH]) <= 0.05)


def failure_pred(T, N):
    return bool((T[W0] - T[WH]) > 0.1 or null_same_invariance(N))


def main():
    rows = [json.loads(l) for l in open(ROWS, encoding="utf-8") if l.strip()]
    by = {}
    for r in rows:
        by.setdefault(r["arm"], []).append(r)

    def arm_mean(arm, key="acc_by_w"):
        rs = by[arm]
        ws = rs[0][key].keys()
        return ({w: float(np.mean([r[key][w] for r in rs])) for w in ws},
                {w: float(np.std([r[key][w] for r in rs], ddof=1)) for w in ws}, len(rs))

    T, Tsd, nT = arm_mean("TREATMENT")
    C, Csd, nC = arm_mean("CONTROL")
    N, Nsd, nN = arm_mean("NULL_TWIN")
    cross, _, _ = arm_mean("TREATMENT", "frac_boundary_crossed_by_w")
    pc = by["POSITIVE_CONTROL"]
    pc_car = float(np.mean([r["acc_carrier"] for r in pc]))
    pc_clk = float(np.mean([r["acc_clock"] for r in pc]))
    pc_det = bool(pc_car >= PC_THRESH and pc_clk >= PC_THRESH)
    chT, _, _ = arm_mean("CHEAT", "acc_T_by_w")
    chC, _, _ = arm_mean("CHEAT", "acc_C_by_w")
    chN, _, _ = arm_mean("CHEAT", "acc_N_by_w")
    cheat_det = success_pred(chT, chC, chN) and not failure_pred(chT, chN)

    succ = success_pred(T, C, N)
    fail = failure_pred(T, N)
    null_meets = null_same_invariance(N)
    if not (pc_det and cheat_det):
        outcome = "INSTRUMENT_FAIL"
    elif null_meets:
        outcome = "CONFOUNDED"
    elif succ and not fail:
        outcome = "SIGNAL"
    else:
        outcome = "NULL"

    anomalies = []
    if T[W0] < PC_THRESH:
        anomalies.append(f"treatment carrier accuracy at w=0 is {T[W0]:.4f} < 0.98")
    if N[W0] < PC_THRESH:
        anomalies.append(f"null-twin carrier accuracy at w=0 is {N[W0]:.4f} < 0.98 (carrier identical to treatment at w=0 up to noise)")
    for arm, d in (("TREATMENT", T), ("CONTROL", C), ("NULL_TWIN", N)):
        vals = [d[w] for w in sorted(d, key=float)]
        if any(b > a + 0.01 for a, b in zip(vals, vals[1:])):
            anomalies.append(f"{arm} accuracy not monotone non-increasing in w: {vals}")

    cpu = max(r.get("cpu_seconds_cumulative", 0.0) for r in rows)
    attempts = max(r["params"]["ATTEMPT"] for r in rows)
    out = {
        "triplicateId": "HT-a9e2ba7618", "world": "W4", "outcome": outcome,
        "statistics": {
            "statistic": "mean over seeds of per-seed symbol decoding accuracy (4000 symbols per seed per w)",
            "TREATMENT_carrier_phase_cowarped": {"mean_by_w": T, "sd_by_w": Tsd, "n_seeds": nT,
                                                 "drop_0_to_0.4": T[W0] - T[WH]},
            "CONTROL_clock_time": {"mean_by_w": C, "sd_by_w": Csd, "n_seeds": nC,
                                   "drop_0_to_0.4": C[W0] - C[WH]},
            "NULL_TWIN_carrier_phase_unwarped_carrier": {"mean_by_w": N, "sd_by_w": Nsd, "n_seeds": nN,
                                                         "drop_0_to_0.4": N[W0] - N[WH]},
            "POSITIVE_CONTROL_w0": {"carrier": pc_car, "clock": pc_clk, "n_seeds": len(pc)},
            "CHEAT": {"T": chT, "C": chC, "N": chN, "n_seeds": len(by["CHEAT"])},
            "frac_symbols_crossing_clock_slot_boundary_by_w": cross,
        },
        "criterion_as_applied": ("SUCCESS iff mean acc_T(0.4) >= 0.9 AND acc_T(0)-acc_T(0.4) <= 0.05 AND "
                                 "acc_C(0)-acc_C(0.4) >= 0.3 AND acc_N(0)-acc_N(0.4) >= 0.3; FAILURE iff "
                                 "acc_T(0)-acc_T(0.4) > 0.1 OR (acc_N(0.4) >= 0.9 AND acc_N(0)-acc_N(0.4) <= 0.05). "
                                 f"success={succ}, failure={fail}. PC detected iff both decoders mean >= 0.98 at w=0 "
                                 "(separate seeds). CHEAT detected iff success and not failure on injected values."),
        "positive_control_detected": pc_det, "cheat_detected": bool(cheat_det),
        "null_twin_meets_success": null_meets,
        "stupid_explanations_status": [
            {"text": "monotone warps preserve order so any order decoder is invariant",
             "addressed_by_this_run": True,
             "how": ("one symbol per cycle, so within-cycle order carries no slot information; the null twin keeps "
                     f"pulse order and timing identical yet its drop is {N[W0]-N[WH]:.3f} vs treatment {T[W0]-T[WH]:.3f}")},
            {"text": "warps too weak to move symbols across slot boundaries",
             "addressed_by_this_run": True,
             "how": f"fraction of symbols whose elapsed time crosses a clock slot boundary at w=0.4: {cross[WH]:.3f}"},
            {"text": "adaptive-scale decoder overfits the warp family",
             "addressed_by_this_run": False,
             "how": "only one warp family (piecewise-linear, slopes 1+w*U[-1,1]) was run"},
        ],
        "anomalies": anomalies, "core_minutes": cpu / 60.0, "attempts": attempts,
        "notes": (f"Carrier-phase decoding with a co-warped carrier: accuracy {T[W0]:.3f} at w=0 and {T[WH]:.3f} at w=0.4. "
                  f"Clock-time decoder with oracle cycle onsets: {C[W0]:.3f} -> {C[WH]:.3f}. Same carrier-phase decoder "
                  f"with the carrier left unwarped (null twin): {N[W0]:.3f} -> {N[WH]:.3f}. Positive control "
                  f"(w=0, separate seeds) carrier {pc_car:.3f}, clock {pc_clk:.3f}. Outcome {outcome} by the PREREG "
                  "class rules applied in code. The run does not test other warp families or a non-oscillatory "
                  "co-warped clock (the spec's alternative explanation)."),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: out[k] for k in ("outcome", "positive_control_detected", "cheat_detected",
                                          "null_twin_meets_success", "core_minutes")}))


if __name__ == "__main__":
    main()
