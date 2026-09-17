"""Build the C1 committed rows + receipt from hot runs.

The full sweep's d64 r4 and d64 r64 blocks ran while lane B burst 16 producer
processes (13 cells host_cpu > 60%), so those blocks are replaced by a clean
rerun. Every row keeps `source` = the hot file it came from.

usage: python -m primordial.brain.c1_build_receipt <full.jsonl> <rerun.jsonl> <git_sha>
"""
from __future__ import annotations

import json
import pathlib
import sys

from primordial.brain.c1_crossover import EXP_ID, analyse

ROWS = pathlib.Path(__file__).resolve().parents[1] / "ledger" / "rows" / "C"


def load(path):
    rows = [json.loads(line) for line in open(path, encoding="utf-8")]
    for r in rows:
        r["source"] = pathlib.Path(path).name
    return rows


def main(argv):
    full, rerun = load(argv[0]), load(argv[1])
    sha = argv[2]
    redone = {(r["obs_dim"], r["r"]) for r in rerun if r["kind"] in ("cell", "logit_check")}
    keep = [r for r in full if r["kind"] not in ("summary",)
            and not (r["kind"] in ("cell", "logit_check") and (r["obs_dim"], r["r"]) in redone)]
    merged = keep + [r for r in rerun if r["kind"] in ("header", "cell", "logit_check")]
    summary = analyse(merged)
    pos = [r for r in full if r["kind"] == "positive_control"]
    summary["positive_control_exact_honest"] = all(r["exact"] for r in pos if "cheat" not in r["impl"])
    summary["positive_control_cheat_skip_half_exact"] = any(r["exact"] for r in pos if r["impl"] == "cheat_skip_half")
    cells = [r for r in merged if r["kind"] == "cell" and "skipped" not in r]
    res = {(c["d"], c["r"], c["B"]): c for c in cells if c["impl"] == "torch_gpu_resident"}
    big = [(c["obs_per_s_wall"] / res[k]["obs_per_s_wall"], c["obs_per_s_timer"] / res[k]["obs_per_s_wall"])
           for c in cells if c["impl"] == "cheat_gpu_nosync" and (k := (c["d"], c["r"], c["B"]))[2] >= 16384]
    summary["nosync_B_ge_16384_max_wall_ratio_vs_resident"] = max(w for w, _ in big)
    summary["nosync_B_ge_16384_max_timer_ratio_vs_resident"] = max(t for _, t in big)
    ROWS.mkdir(parents=True, exist_ok=True)
    rows_path = ROWS / f"{EXP_ID}.jsonl"
    with open(rows_path, "w", encoding="utf-8", newline="\n") as fh:
        for r in merged:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    with open(ROWS / f"{EXP_ID}.summary.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
    print(json.dumps(summary, indent=1, sort_keys=True))
    print("rows", rows_path, len(merged), "contended cells", summary["controls"]["contended_cells"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
