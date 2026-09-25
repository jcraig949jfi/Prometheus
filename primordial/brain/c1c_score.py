"""Score the C1c record run against its pre-run hypothesis (bus 1789390684100-0).

usage: python -m primordial.brain.c1c_score <record.jsonl>
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

ROWS = pathlib.Path(__file__).resolve().parents[1] / "ledger" / "rows" / "C"
EXP_ID = "C1c-gpu-no-gather"


def main(argv):
    src = pathlib.Path(argv[0])
    rows = [json.loads(line) for line in open(src, encoding="utf-8")]
    s = next(r for r in rows if r["kind"] == "summary")
    pc = s["per_config"]
    g = lambda cfg, key, B: pc[cfg][key].get(str(B), pc[cfg][key].get(B))

    h1 = {"bucket_over_gather": g("d64_r64", "bucket_over_gather", 262144),
          "gather_over_bucket_peak_mem": g("d64_r64", "gather_over_bucket_peak_mem", 262144)}
    h1["held"] = bool(h1["bucket_over_gather"] and h1["bucket_over_gather"] >= 8
                      and h1["gather_over_bucket_peak_mem"] and h1["gather_over_bucket_peak_mem"] >= 8)
    h2 = {cfg: pc[cfg]["tp_1M_over_262k"] for cfg in ("d64_r64", "d16_r16")}
    h2_held = all(v["bucket"] is not None and v["bucket"] >= 1.3 and v["gather"] is not None and v["gather"] <= 1.1
                  for v in h2.values())
    x = {cfg: pc[cfg]["crossover_bucket_beats_gather_from_B"] for cfg in pc}
    h3_held = (all(x[c] is not None and x[c] <= 16384 for c in ("d16_r64", "d64_r64"))
               and all(x[c] is not None and x[c] <= 65536 for c in ("d16_r16", "d64_r16"))
               and all(x[c] is None or x[c] >= 262144 for c in ("d16_r4", "d64_r4")))
    h4 = g("d64_r64", "bucket_over_best_cpu", 262144)
    h4_held = bool(h4 and h4 >= 15)
    controls_ok = s["honest_invalid"] == 0 and s["cheat_invalid_ge64"][0] == s["cheat_invalid_ge64"][1] > 0
    status = "KILL" if not h1["held"] else ("PASS" if controls_ok else "FAIL")
    out = {"exp_id": EXP_ID, "source": src.name, "git": rows[0]["git"], "H1": h1, "H2": {"held": h2_held, "values": h2},
           "H3": {"held": h3_held, "crossover_from_B": x}, "H4": {"held": h4_held, "bucket_over_best_cpu": h4},
           "controls": {"honest_invalid": s["honest_invalid"], "honest_cells": s["honest_cells"],
                        "cheat_invalid_ge64": s["cheat_invalid_ge64"]},
           "controls_ok": controls_ok, "status_by_posted_rule": status, "per_config": pc}
    ROWS.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, ROWS / f"{EXP_ID}.jsonl")
    with open(ROWS / f"{EXP_ID}.summary.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
