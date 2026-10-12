"""B80 -- does latch QUALITY (not genome identity or length) decide conversion to RESET? (follow-up to B79)

B79 used one latch per arm: 16-instr .120 -> 4/6, 32-instr .098 -> 6/6, 46-instr .053 -> 0/6.
Here there are FOUR evolved plain-pulse register latches per quality band, and the LOW band includes three
16-instruction latches, so length is crossed with quality:
  HIGH (plain-pulse reward >= .09): B69d CONC 6923 (16, .120); B69c CONC 6911 (16, .123); B69c CONC 6913 (16, .139);
                                    B69d SOLO 6929 (32, .098)
  LOW  (~.05):                      B69c CONC 6916 (16, .051); B69c SOLO 6913 (16, .057); B69d CONC 6931 (16, .059);
                                    B69d CONC 6932 (28, .052)
Gen 0 = 200 copies of the latch. Relocating pulse, SOLO, G=300, 3 seeds per latch (8001-8003) = 24 cells.
Readout = B77 parity; a population converts if it has >= 5 RESET-like genomes.
PREDICTION (committed before running), quality hypothesis:
- HIGH band converts in >= 8/12 populations, LOW band in <= 3/12;
- among the three 16-instruction LOW latches, <= 2/9 convert (length does not rescue low quality).
KNOWN CONFOUND (found at staging, before running): persist mode. All HIGH latches persist 'regs'; three of the four
LOW latches persist 'all' (L_6932 persists 'regs'). Report L_6932 separately; a persist-matched follow-up is needed
if the bands differ.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G

from archaeon.beta.b25_noclock_world import NoClock, load as load24
from archaeon.beta.b68_pulse_state_controls import group_pulse
import archaeon.beta.b75_reset_evolution as B75
import archaeon.beta.b76_reset_from_latch as B76
from archaeon.beta.b79_evolved_latch_start import parity

RES = Path(__file__).resolve().parent / "results"
OUT = RES / "B80_latch_quality"
LATCHES = {
    "H_6923": ("HIGH", "B69d_pulse", "CONC", 6923), "H_6911": ("HIGH", "B69c_pulse", "CONC", 6911),
    "H_6913": ("HIGH", "B69c_pulse", "CONC", 6913), "H_6929": ("HIGH", "B69d_pulse", "SOLO", 6929),
    "L_6916": ("LOW", "B69c_pulse", "CONC", 6916), "L_S6913": ("LOW", "B69c_pulse", "SOLO", 6913),
    "L_6931": ("LOW", "B69d_pulse", "CONC", 6931), "L_6932": ("LOW", "B69d_pulse", "CONC", 6932)}


def latch_genome(key):
    _, d, a, sd = LATCHES[key]
    w0, s, _ = load24(); w = NoClock(w0)
    sc = lambda m: sum(group_pulse([m], w, s + 1000 + k, 16, 4)[0] for k in range(4)) / 4
    pop = json.loads((RES / d / ("B62_pop_%s_%d.json" % (a, sd))).read_text(encoding="utf-8"))
    best = max(({json.dumps(m["genome"]): m for m in pop}).values(), key=sc)
    return best, round(sc(best), 4)


def cell(job):
    m0, q = latch_genome(job["latch"])

    def gen0():
        rec = G.organism_record(copy.deepcopy(m0), None, 0); rec["origins"] = ["gen0_" + job["latch"]]
        return [copy.deepcopy(rec) for _ in range(200)]

    B76.latch_gen0 = gen0; B76.OUT = OUT / job["latch"]; B76.OUT.mkdir(parents=True, exist_ok=True)
    r = B76.cell(job)
    pop = json.loads((B76.OUT / ("pop_%d.json" % job["seed"])).read_text(encoding="utf-8"))
    r["parity_reset_like"], r["parity_best"] = parity(pop)
    r.update({"latch": job["latch"], "band": LATCHES[job["latch"]][0], "latch_len": len(m0["genome"]) // 4, "latch_quality": q})
    return r


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    refs = B75.refs_(); rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"latch": k, "seed": 8001 + i, "G": int(argv[0]) if argv else 300, "refs": refs}): (k, i) for k in LATCHES for i in range(3)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                k, i = futs[f]; r = {"latch": k, "band": LATCHES[k][0], "seed": 8001 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B80_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    conv = lambda r: r.get("parity_reset_like", 0) >= 5
    summ = {"HIGH": sum(conv(r) for r in rows if r["band"] == "HIGH"), "LOW": sum(conv(r) for r in rows if r["band"] == "LOW"),
            "LOW_16instr": sum(conv(r) for r in rows if r["band"] == "LOW" and r.get("latch_len") == 16)}
    print(json.dumps(summ))
    (OUT / "B80_result.json").write_text(json.dumps({"probe": "B80", "refs": refs, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
