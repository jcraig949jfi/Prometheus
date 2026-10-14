"""B85 -- does the hand-latch route to RESET need RECOMBINATION between the two latch variants? (follow-up to B84)

B76 seeded gen 0 with 100 x LATCH_1 + 100 x LATCH_2 (pool-1 and pool-2 specialists) and converted 6/6.
B83: LATCH_1 has zero improving one-step mutants.
B84: 12 neutral walks of 15 steps from LATCH_1 never find RESET.
The route evolution takes therefore needs something a single lineage lacks. The candidate is crossover between the
two different latch genomes (CMP3's descend takes a mate).
Arms (relocating pulse, SOLO, G=300, seeds 8501-8506, B77 parity; a population converts with >= 5 RESET-like genomes):
  SINGLE  gen 0 = 200 x LATCH_1 (one genome: crossover only among its own drifted copies)
  PAIR    gen 0 = 100 x LATCH_1 + 100 x LATCH_2 (the B76 condition; replication on new seeds)
PREDICTION (committed before running), recombination hypothesis: PAIR >= 4/6 AND SINGLE <= 2/6.
If SINGLE >= 4/6, recombination between the two latches is not required.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G

from archaeon.beta.b68_pulse_state_controls import latch, man
import archaeon.beta.b75_reset_evolution as B75
import archaeon.beta.b76_reset_from_latch as B76
from archaeon.beta.b79_evolved_latch_start import parity

OUT = Path(__file__).resolve().parent / "results" / "B85_single_latch"


def gen0_for(arm):
    def mk(i, n):
        rec = G.organism_record(man(latch(i), "regs"), None, 0); rec["origins"] = ["gen0_latch%d" % i]
        return [copy.deepcopy(rec) for _ in range(n)]
    return (lambda: mk(1, 200)) if arm == "SINGLE" else (lambda: mk(1, 100) + mk(2, 100))


def cell(job):
    B76.latch_gen0 = gen0_for(job["arm"]); B76.OUT = OUT / job["arm"]; B76.OUT.mkdir(parents=True, exist_ok=True)
    r = B76.cell(job)
    pop = json.loads((B76.OUT / ("pop_%d.json" % job["seed"])).read_text(encoding="utf-8"))
    r["parity_reset_like"], r["parity_best"] = parity(pop); r["arm"] = job["arm"]
    return r


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    refs = B75.refs_(); rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 8501 + i, "G": int(argv[0]) if argv else 300, "refs": refs}): (a, i) for a in ("SINGLE", "PAIR") for i in range(6)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[f]; r = {"arm": a, "seed": 8501 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B85_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("parity_reset_like", 0) >= 5 for r in rows if r.get("arm") == a) for a in ("SINGLE", "PAIR")}
    print(json.dumps(summ))
    (OUT / "B85_result.json").write_text(json.dumps({"probe": "B85", "refs": refs, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
