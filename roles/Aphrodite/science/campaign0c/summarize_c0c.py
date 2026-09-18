"""Campaign 0C verdict from rows only (PREREG_C0C s4). TIER 2."""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
L_DIR = HERE / ("ledgers_quick" if "--quick" in sys.argv else "ledgers")


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main():
    rows = [json.loads(x) for x in (L_DIR / "c0c_rows.jsonl").read_text(encoding="utf-8").splitlines() if x]
    g = defaultdict(list)
    for r in rows:
        g[(r["world"], r["L"])].append(r)
    out = {"cells": {}}
    for (w, L), rs in sorted(g.items()):
        n = len(rs)
        disc = sum(r["discovery"] for r in rs)
        lo, hi = wilson(disc, n)
        conf = sum(r["n_confirmed"] for r in rs)
        conf_true = sum(r["n_confirmed_true"] for r in rs)
        nom_bias = [x for r in rs for x, c in zip(r["nominated_screen_minus_true"], r["nominated_true_carrier"]) if c]
        est_err = [e[0] - t for r in rs for e, t in zip(r["confirmed_est"], r["confirmed_true"])]
        cover = [e[1] <= t <= e[2] for r in rs for e, t in zip(r["confirmed_est"], r["confirmed_true"])]
        Lr = rs[0]["L"]
        out["cells"][f"{w}|L{L}"] = {
            "world": w, "L": L, "pi": rs[0]["pi"], "J": rs[0]["J"], "n": n,
            "p_discovery": round(disc / n, 4), "wilson": [round(lo, 4), round(hi, 4)],
            "p_discovery_nmin1": round(sum(r["discovery_nmin1"] for r in rs) / n, 4),
            "mean_true_carriers": round(sum(r["n_true_carriers"] for r in rs) / n, 3),
            "q_screen": round(sum(r["n_qualified"] for r in rs) / (n * Lr), 4),
            "q_nominated": round(sum(r["n_nominated"] for r in rs) / (n * Lr), 4),
            "q_confirm": round(conf / (n * Lr), 4),
            "true_carrier_rate": round(sum(r["n_true_carriers"] for r in rs) / (n * Lr), 4),
            "confirmed": conf, "confirmed_true": conf_true,
            "precision": None if conf == 0 else round(conf_true / conf, 4),
            "screen_winners_curse_mean": None if not nom_bias else round(sum(nom_bias) / len(nom_bias), 4),
            "estimate_bias_mean": None if not est_err else round(sum(est_err) / len(est_err), 4),
            "estimate_coverage": None if not cover else round(sum(cover) / len(cover), 4),
        }
    C = out["cells"]
    g1 = all(C[f"{w}|L{L}"]["wilson"][1] <= 0.10 for w in ("N0", "AS", "WC") for L in (32, 64))
    c64 = [c for c in C.values() if c["L"] == 64]
    ct, cn = sum(c["confirmed_true"] for c in c64), sum(c["confirmed"] for c in c64)
    g2 = cn > 0 and ct / cn >= 0.90
    g3 = all(C[f"G_pi{pi}_J{J}|L64"]["p_discovery"] >= 0.80 and C[f"G_pi{pi}_J{J}|L64"]["wilson"][0] >= 0.75
             for pi in (0.1, 0.2) for J in (1.0, 2.0))
    errs, covs = [], []
    for r in (json.loads(x) for x in (L_DIR / "c0c_rows.jsonl").read_text(encoding="utf-8").splitlines() if x):
        if r["L"] == 64:
            errs += [e[0] - t for e, t in zip(r["confirmed_est"], r["confirmed_true"])]
            covs += [e[1] <= t <= e[2] for e, t in zip(r["confirmed_est"], r["confirmed_true"])]
    bias = sum(errs) / len(errs) if errs else float("nan")
    cov = sum(covs) / len(covs) if covs else float("nan")
    g4 = abs(bias) <= 0.01 and cov >= 0.90
    out["gates"] = {"G1_calibration": g1, "G2_precision": {"pass": g2, "value": round(ct / cn, 4) if cn else None},
                    "G3_power": g3, "G4_estimation": {"pass": g4, "bias": round(bias, 5), "coverage": round(cov, 4),
                                                      "n_confirmed_L64": len(errs)}}
    out["PASS"] = bool(g1 and g2 and g3 and g4)
    (L_DIR / "C0C_VERDICT.json").write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
    for key, c in C.items():
        print(f"{key:24s} P(DISC) {c['p_discovery']:.3f} [{c['wilson'][0]:.2f},{c['wilson'][1]:.2f}] "
              f"q_scr {c['q_screen']:.3f} q_conf {c['q_confirm']:.4f} true {c['true_carrier_rate']:.4f} "
              f"prec {c['precision']} scrWC {c['screen_winners_curse_mean']} estBias {c['estimate_bias_mean']} "
              f"cov {c['estimate_coverage']}")
    print("GATES", json.dumps(out["gates"]))
    print("PASS", out["PASS"])


if __name__ == "__main__":
    main()
