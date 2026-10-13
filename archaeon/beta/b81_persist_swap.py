"""B81 -- does the PERSIST MODE (not latch quality) decide conversion to RESET? Persist-swap test (follow-up to B80).

B80: persist-'regs' latches converted in 5/15 runs and persist-'all' latches in 0/8 (Fisher one-sided p ~ .08). But
every 'all' latch is also LOW quality, so the two are confounded.
Pre-check (B81pre_persist_swap.json): forcing persist 'regs' <-> 'all' leaves gen-0 behaviour IDENTICAL in both the
plain and the relocating pulse world (same rewards to 4 decimals) for 7/8 latches; H_6911 breaks under 'all' and is
excluded. So a swap changes only the EVOLVABLE substrate (whether the tape persists across ticks), not the starting
behaviour.
Arms (gen 0 = 200 copies of the latch, persist FORCED; relocating pulse, SOLO, G=300, seeds 8001-8003, B77 parity):
  LOW->regs   L_6916, L_S6913, L_6931 (originally 'all'; 0/8 converted in B80)
  HIGH->all   H_6923, H_6913 (originally 'regs'; 3/6 converted in B80)
PREDICTION (committed before running), persist hypothesis:
- LOW->regs converts >= 3/9;
- HIGH->all converts <= 1/6.
If LOW->regs stays <= 1/9 and HIGH->all stays >= 3/6, persist is NOT the variable and quality / genome identity is.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G

import archaeon.beta.b75_reset_evolution as B75
import archaeon.beta.b76_reset_from_latch as B76
from archaeon.beta.b79_evolved_latch_start import parity
from archaeon.beta.b80_latch_quality import latch_genome

OUT = Path(__file__).resolve().parent / "results" / "B81_persist_swap"
ARMS = {"L_6916": "regs", "L_S6913": "regs", "L_6931": "regs", "H_6923": "all", "H_6913": "all"}


def cell(job):
    m0, q = latch_genome(job["latch"]); m0 = copy.deepcopy(m0); orig = m0["persist"]; m0["persist"] = ARMS[job["latch"]]

    def gen0():
        rec = G.organism_record(copy.deepcopy(m0), None, 0); rec["origins"] = ["gen0_%s_%s" % (job["latch"], m0["persist"])]
        return [copy.deepcopy(rec) for _ in range(200)]

    B76.latch_gen0 = gen0; B76.OUT = OUT / job["latch"]; B76.OUT.mkdir(parents=True, exist_ok=True)
    r = B76.cell(job)
    pop = json.loads((B76.OUT / ("pop_%d.json" % job["seed"])).read_text(encoding="utf-8"))
    r["parity_reset_like"], r["parity_best"] = parity(pop)
    r.update({"latch": job["latch"], "persist_forced": m0["persist"], "persist_orig": orig, "arm": "LOW->regs" if job["latch"].startswith("L") else "HIGH->all"})
    return r


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    refs = B75.refs_(); rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"latch": k, "seed": 8001 + i, "G": int(argv[0]) if argv else 300, "refs": refs}): (k, i) for k in ARMS for i in range(3)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                k, i = futs[f]; r = {"latch": k, "seed": 8001 + i, "arm": "LOW->regs" if k.startswith("L") else "HIGH->all", "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B81_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("parity_reset_like", 0) >= 5 for r in rows if r["arm"] == a) for a in ("LOW->regs", "HIGH->all")}
    print(json.dumps(summ))
    (OUT / "B81_result.json").write_text(json.dumps({"probe": "B81", "refs": refs, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
