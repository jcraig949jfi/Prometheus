"""Seeded draw of the ONE representative BEE run for the ancestry replay (prereg v3 s5; Review 4 s5.1: the earlier choice of r038751
was made after its properties were known).

Eligible population, declared BEFORE the draw:
- traced runs in Bellerophon's preserved births directory (845 runs, z80atlas campaign 2026-09-19);
- reproduction == ENDOGENOUS_COPY (the family r038751 belongs to);
- >= 1 is_sr birth (column 11), so that Q4/Q5 are defined.
The draw: sort the eligible run ids; index = int(sha256(SEED), 16) % n. It is deterministic and re-runnable from these files.
    python -m archaeon.attribution.bee_run_draw [--births DIR] [--runs DIR]
"""
import gzip
import hashlib
import json
import os
import sys

SEED = "attribution-arc 2026-09-28 prereg v3 BEE representative run"
BIRTHS = "C:/Users/James/z80atlas_forensics_2026-09-23_local/births"
RUNS = "C:/Users/James/z80atlas_campaign_2026-09-19/runs"


def main(births, runs):
    elig = []; stats = {"traced": 0, "endogenous": 0, "with_sr": 0}
    for f in sorted(os.listdir(births)):
        if not f.endswith(".jsonl.gz"): continue
        rid = f.split(".")[0]; stats["traced"] += 1
        cfg = json.load(open(os.path.join(runs, rid, "config.json")))["config"]
        if cfg.get("reproduction") != "ENDOGENOUS_COPY": continue
        stats["endogenous"] += 1
        n = sr = 0
        with gzip.open(os.path.join(births, f), "rt") as fh:
            for line in fh:
                row = json.loads(line); n += 1
                if isinstance(row, list) and len(row) > 11 and row[11]: sr += 1
        if sr: elig.append((rid, n, sr)); stats["with_sr"] += 1
    elig.sort()
    i = int(hashlib.sha256(SEED.encode()).hexdigest(), 16) % len(elig)
    out = {"seed": SEED, "stats": stats, "n_eligible": len(elig), "index": i, "drawn": elig[i], "eligible": elig}
    print(json.dumps({k: v for k, v in out.items() if k != "eligible"}))
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    o = main(a[a.index("--births") + 1] if "--births" in a else BIRTHS, a[a.index("--runs") + 1] if "--runs" in a else RUNS)
    json.dump(o, open("bee_run_draw.json", "w"), indent=0)
