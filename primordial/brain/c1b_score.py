"""Score the C1b record run against its pre-run hypothesis (bus 1789389161904-0 claim + note).

usage: python -m primordial.brain.c1b_score <record.jsonl>
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

ROWS = pathlib.Path(__file__).resolve().parents[1] / "ledger" / "rows" / "C"
EXP_ID = "C1b-load-sensitivity"


def main(argv):
    src = pathlib.Path(argv[0])
    rows = [json.loads(line) for line in open(src, encoding="utf-8")]
    s = next(r for r in rows if r["kind"] == "summary")
    ratio, cross, host = s["ratio_vs_idle"], s["crossover"], s["host_cpu_median_by_load"]
    key = "d64_r64_B4096/{}/burn8"
    p1 = {i: ratio.get(key.format(i)) for i in ("numba_par", "nb_bucket_c3", "numba_par_c3", "numba_1", "np_bucket")}
    p1_held = (p1["numba_par"] is not None and p1["numba_par"] <= 0.70
               and p1["nb_bucket_c3"] >= 0.85 and p1["numba_par_c3"] >= 0.85)
    graph = {k: v for k, v in ratio.items() if "/torch_gpu_graph_e2e/burn8" in k}
    p2_held = all(v >= 0.85 for v in graph.values())
    grid = [256, 1024, 4096, 16384]
    xi = cross["d16_r16/torch_gpu_e2e/idle"]["crossover_B_in_tested"]
    xb = cross["d16_r16/torch_gpu_e2e/burn8"]["crossover_B_in_tested"]
    step = None if xi is None or xb is None else abs(grid.index(xi) - grid.index(xb))
    g_over = cross["d64_r64/torch_gpu_e2e/idle"]["gpu_over_best_cpu"].get("4096")
    p3_held = step is not None and step <= 1 and g_over is not None and g_over <= 1.3
    sham = {k: v for k, v in ratio.items() if k.endswith("/sham8") and "cheat" not in k}
    controls = {"sham_host_ok": host["sham8"] <= host["idle"] + 10,
                "sham_within_15pct": all(0.85 <= v <= 1.15 for v in sham.values()),
                "sham_outside_15pct": {k: v for k, v in sham.items() if not 0.85 <= v <= 1.15},
                "burn8_host_ok": host["burn8"] >= host["idle"] + 35,
                "honest_valid": s["honest_invalid"] == 0,
                "skip_half_caught": s["skip_half_invalid_ge64"][0] == s["skip_half_invalid_ge64"][1]}
    controls_ok = all(v for k, v in controls.items() if k != "sham_outside_15pct")
    status = "KILL" if not p1_held else ("PASS" if controls_ok else "FAIL")
    out = {"exp_id": EXP_ID, "source": src.name, "git": rows[0]["git"],
           "p1_burn8_ratio_d64r64_B4096": p1, "p1_held": p1_held,
           "p2_graph_burn8_ratios": graph, "p2_held": p2_held,
           "p3_crossover_d16r16_idle_burn8": [xi, xb], "p3_d64r64_B4096_gpu_over_best_cpu_idle": g_over,
           "p3_held": p3_held, "controls": controls, "controls_ok": controls_ok,
           "host_cpu_median_by_load": host, "status_by_posted_rule": status,
           "crossover": cross, "ratio_vs_idle": ratio}
    ROWS.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, ROWS / f"{EXP_ID}.jsonl")
    with open(ROWS / f"{EXP_ID}.summary.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in out.items() if k not in ("crossover", "ratio_vs_idle")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
