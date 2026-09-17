"""Score the C5 record run against its pre-run hypothesis (bus 1789391624761-0).

usage: python -m primordial.brain.c5_score <record.jsonl>
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

ROWS = pathlib.Path(__file__).resolve().parents[1] / "ledger" / "rows" / "C"
EXP_ID = "C5-fast-population-forward"


def main(argv):
    src = pathlib.Path(argv[0])
    rows = [json.loads(line) for line in open(src, encoding="utf-8")]
    W = [r for r in rows if r["kind"] == "world"]
    per = {r["gen_seed"]: {k: r[k] for k in ("speedup_fast_par", "speedup_fast_ser", "brain_share_numpy",
                                             "micro_forward_speedup", "amdahl_predicted",
                                             "amdahl_ratio_measured_over_predicted", "row_agreement",
                                             "row_mismatches", "clear_row_mismatches", "live_rows",
                                             "fitness_equal_genomes_par", "cheat_wrong_frac")} for r in W}
    h1 = sum(v["speedup_fast_par"] >= 3.0 for v in per.values())
    h1_held = h1 >= 4 and len(per) == 5
    h2_held = all(v["row_agreement"] >= 0.999 and v["clear_row_mismatches"] == 0 for v in per.values())
    h3_held = all(0.7 <= v["amdahl_ratio_measured_over_predicted"] <= 1.3 for v in per.values())
    control_ok = all(v["cheat_wrong_frac"] >= 0.30 for v in per.values())
    status = "KILL" if not h1_held else ("PASS" if (h2_held and control_ok) else "FAIL")
    out = {"exp_id": EXP_ID, "source": src.name, "git": rows[0]["git"], "per_world": per,
           "H1_worlds_ge_3x": h1, "H1_held": h1_held, "H2_held": h2_held, "H3_held": h3_held,
           "control_ok": control_ok, "status_by_posted_rule": status}
    ROWS.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, ROWS / f"{EXP_ID}.jsonl")
    with open(ROWS / f"{EXP_ID}.summary.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
