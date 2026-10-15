"""C-019-T021 ladder probe (directive s3-s4), seconds of CPU, NO search. Evaluates Crius's own committed PARTS (hand-built
bytecode, crius/parts_c2.py) on the frozen rung-C config (crius/configs/c2c.json, suite 'gate', seeds 19_020_001..005):
what Capability A / Capability B look like as native programs and what each is worth by construction.
    python -B -m rso.gen5.crius.ladder_probe rso/gen5/crius/results/ladder_probe.json
"""
import json
import sys

from crius import baselines_c1 as bl, evaluate, receipts, streams
from rso.gen5.crius import adapt

SEEDS = (19020001, 19020002, 19020003, 19020004, 19020005)
NAMES = ("ENUMERATE_VM_C1", "P_BASE", "P_REC", "P_INV", "P_REC_INV", "P_PLAN", "P_REC_INV_PLAN")


def main(out):
    cfg = receipts.load_config("crius/configs/c2c.json")
    rows = {}
    for s in SEEDS:
        tasks = streams.lifetime(cfg, s, "gate")
        for n in NAMES:
            r = {}
            for cond in ("ACCUMULATED", "FRESH"):
                m = evaluate.run_lifetime(bl.make_baseline(n), tasks, cfg, cond, seed=s)["metrics"]
                r[cond] = m["successes"]
            rows["%s/%d" % (n, s)] = r
            print(n, s, r, flush=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"schema": "prometheus.rso.gen5.crius.ladder_probe.v1", "config": "crius/configs/c2c.json", "rows": rows}, f, indent=1, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main(sys.argv[1])
