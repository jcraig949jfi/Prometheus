"""Phase 2A temporal dynamics: occurrence RATE per fixed 6-hour window (by run completion time), never cumulative
counts. Lanes: FIXED (exploration runs: allocation independent of promotion) vs PROMOTED (promoted + verification +
intervention: allocation driven by earlier triggers). A rising rate in FIXED would be a genuine change in what the
substrate produces per run; a rising rate only in PROMOTED is allocation (exposure) feedback.
Trend statistic: Cochran-Armitage style z for a linear trend in proportions across windows.
Writes receipts/TEMPORAL.json."""
from __future__ import annotations

import collections
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import load as Ld  # noqa: E402
from rates import outcomes  # noqa: E402

W = 6 * 3600


def trend_z(ks, ns):
    xs = list(range(len(ns)))
    N = sum(ns); K = sum(ks)
    if N == 0 or K == 0 or K == N:
        return None
    p = K / N
    xbar = sum(x * n for x, n in zip(xs, ns)) / N
    T = sum(x * (k - n * p) for x, k, n in zip(xs, ks, ns))
    V = p * (1 - p) * sum(n * (x - xbar) ** 2 for x, n in zip(xs, ns))
    return round(T / math.sqrt(V), 2) if V > 0 else None


def main() -> None:
    R = [r for r in Ld.runs() if r["kind"] != "positive_control"]
    S = Ld.state_small(); t0 = S["start_ts"]
    FL = Ld.flags(); flag_runs = collections.defaultdict(set)
    for f in FL:
        if f.get("run"):
            flag_runs[f["flag"]].add(f["run"])
    win = {}
    for r in R:
        try:
            win[r["id"]] = int((os.stat(Ld.WD / "runs" / r["id"] / "summary.json").st_mtime - t0) // W)
        except OSError:
            pass
    lanes = {"FIXED": lambda r: r["kind"] == "exploration", "PROMOTED": lambda r: r["kind"] in ("promoted", "verification", "intervention")}
    out = {"window_hours": 6, "definition": __doc__, "lanes": {}}
    for lane, sel in lanes.items():
        rows = [(r, outcomes(r)) for r in R if sel(r)]
        L = {}
        for key in ("exact_solve", "hifi_repro", "spont", "extinct", "persistent"):
            ks = [0] * 12; ns = [0] * 12
            for r, o in rows:
                if o[key] is None or r["id"] not in win:
                    continue
                w = min(11, win[r["id"]]); ns[w] += 1; ks[w] += int(o[key])
            L[key] = {"k": ks, "n": ns, "rate": [round(k / n, 4) if n else None for k, n in zip(ks, ns)], "trend_z": trend_z(ks, ns)}
        for fname, runs_ in flag_runs.items():
            ks = [0] * 12; ns = [0] * 12
            for r, _ in rows:
                if r["id"] not in win:
                    continue
                w = min(11, win[r["id"]]); ns[w] += 1; ks[w] += int(r["id"] in runs_)
            L["FLAG:" + fname] = {"k": ks, "n": ns, "rate": [round(k / n, 4) if n else None for k, n in zip(ks, ns)], "trend_z": trend_z(ks, ns)}
        out["lanes"][lane] = L
    p = Ld.write("TEMPORAL.json", out)
    print(p)
    for lane, L in out["lanes"].items():
        print("==", lane)
        for k, v in L.items():
            print("  %-58s z=%-6s n=%s" % (k, v["trend_z"], v["n"][:12]))
            print("  %-58s rate=%s" % ("", v["rate"]))


if __name__ == "__main__":
    main()
