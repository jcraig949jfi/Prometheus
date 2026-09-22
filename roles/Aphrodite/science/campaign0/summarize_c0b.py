"""Campaign 0B verdict from rows only (PREREG_C0B sections 4-5). TIER 2."""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from assay import PLANTED  # noqa: E402
from summarize_c0 import wilson  # noqa: E402

L_DIR = HERE / ("ledgers_quick" if "--quick" in sys.argv else "ledgers")


def main():
    rows = [json.loads(x) for x in (L_DIR / "c0b_rows.jsonl").read_text(encoding="utf-8").splitlines() if x]
    g = defaultdict(list)
    for r in rows:
        g[(r["pathology"], r["world"], r["L"])].append(r)
    out = {"pathologies": {}, "delta_table": {}}
    passed = True
    for p in sorted({r["pathology"] for r in rows}):
        out["pathologies"][p] = {}
        for wk in sorted({r["world"] for r in rows}):
            out["pathologies"][p][wk] = {}
            for L in sorted({r["L"] for r in rows}):
                rs = g[(p, wk, L)]
                n = len(rs)
                rec = sum(r["recovered"] for r in rs)
                fp = sum(bool(set(r["flags"]) - PLANTED[wk]) for r in rs)
                lo, _ = wilson(rec, n)
                reliable = rec / n >= 0.90 and lo >= 0.85
                cell = {"recovery": round(rec / n, 4), "wilson_lo": round(lo, 4), "reliable": reliable,
                        "false_flag_rate": round(fp / n, 4), "fp_wilson_upper": round(wilson(fp, n)[1], 4),
                        "ambiguous": round(sum(r["ambiguous"] for r in rs) / n, 4)}
                out["pathologies"][p][wk][str(L)] = cell
                if L == 64:
                    if wk in ("W6", "W9"):
                        passed &= cell["fp_wilson_upper"] <= 0.10
                    else:
                        passed &= reliable
    # classify failures: calibration (false flags) vs power (missed recovery)
    cal, power = [], []
    for p, ws in out["pathologies"].items():
        for wk, byL in ws.items():
            c = byL.get("64")
            if not c:
                continue
            if c["fp_wilson_upper"] > 0.10:
                cal.append(f"{p}/{wk}: false-flag upper {c['fp_wilson_upper']}")
            elif wk not in ("W6", "W9") and not c["reliable"]:
                power.append(f"{p}/{wk}: recovery {c['recovery']}")
    out["calibration_failures_L64"] = cal
    out["power_losses_L64"] = power
    out["PASS"] = bool(passed)
    drows = [json.loads(x) for x in (L_DIR / "c0b_delta_rows.jsonl").read_text(encoding="utf-8").splitlines() if x]
    dg = defaultdict(list)
    for r in drows:
        dg[(r["kind"], r["world"], r["L"], r["delta"])].append(r)
    for d in sorted({r["delta"] for r in drows}):
        t = {}
        for L in sorted({r["L"] for r in drows}):
            shifts = sorted({r["world"] for r in drows if r["kind"] == "mde"}, key=float)
            curve = {s: round(sum(x["recovered"] for x in dg[("mde", s, L, d)]) / len(dg[("mde", s, L, d)]), 4)
                     for s in shifts}
            mde = next((float(s) for s in shifts if curve[s] >= 0.80), None)
            null = dg[("world", "W6", L, d)]
            w4 = dg[("world", "W4", L, d)]
            t[str(L)] = {"transfer_curve": curve, "mde_logit": mde,
                         "mde_points": None if mde is None else round(
                             1 / (1 + math.exp(-(math.log(0.35 / 0.65) + mde))) - 0.35, 4),
                         "null_shown_equivalent": round(sum(x["d_vault_verdict"] == "EQUIVALENT" for x in null)
                                                        / len(null), 4),
                         "w4_recovery": round(sum(x["recovered"] for x in w4) / len(w4), 4)}
        out["delta_table"][str(d)] = t
    (L_DIR / "C0B_VERDICT.json").write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
    for p, ws in out["pathologies"].items():
        print(p)
        for wk, byL in ws.items():
            print("  ", wk, " ".join(f"L{L}: rec {c['recovery']:.3f}{'*' if c['reliable'] else ''} "
                                     f"falseflag {c['false_flag_rate']:.3f}" for L, c in byL.items()))
    print("CALIBRATION FAILURES @64:", cal)
    print("POWER LOSSES @64:", power)
    print("PASS", out["PASS"])
    for d, t in out["delta_table"].items():
        print("delta", d, {L: (v["mde_logit"], v["mde_points"], v["null_shown_equivalent"], v["w4_recovery"])
                           for L, v in t.items()})


if __name__ == "__main__":
    main()
