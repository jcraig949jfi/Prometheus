"""B79 -- why did the natural curriculum (B78) mostly fail? Seed gen 0 with an EVOLVED latch.

B76: 200 x the compact HAND latch (16 instructions) -> RESET-like in 6/6 populations (median ~102 genomes).
B78: populations that EVOLVED a latch in the plain pulse world -> RESET in 1/12. Their best genomes were 16-95
instructions and diverse.
Hypothesis (B78): compactness/uniformity of the latch genome is what makes it a stepping stone.
Three arms. Gen 0 = 200 copies of one EVOLVED plain-pulse register latch (B69 populations, never exposed to
relocation):
  COMPACT_HIGH  B69d CONC 6923 best: 16 instructions, plain-pulse reward .120
  LONG_HIGH     B69d SOLO 6929 best: 32 instructions, .098
  LONG_LOW      B69d SOLO 6924 best: 46 instructions, .053
Relocating pulse world (48 ticks, P=4, Q=16), SOLO, G=300, seeds 7901-7906 per arm. Readout = B77 parity (every
unique genome above the hand LATCH; RESET-like = full dependence >= .02 AND re-find >= .31). A population counts if it
has >= 5 RESET-like genomes.
PREDICTION (committed before running), compactness hypothesis:
- COMPACT_HIGH >= 4/6;
- LONG_HIGH <= 2/6 and LONG_LOW <= 2/6.
If all three arms are >= 4/6, uniform seeding (not compactness) is what B78 lacked.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G

from archaeon.beta.b25_noclock_world import NoClock, load as load24
from archaeon.beta.b68_pulse_state_controls import group_pulse
from archaeon.beta.b74_relocating_pulse_ladder import group_reloc
import archaeon.beta.b75_reset_evolution as B75
import archaeon.beta.b76_reset_from_latch as B76

RES = Path(__file__).resolve().parent / "results"
OUT = RES / "B79_evolved_latch"
ARMS = {"COMPACT_HIGH": ("B69d_pulse", "CONC", 6923), "LONG_HIGH": ("B69d_pulse", "SOLO", 6929), "LONG_LOW": ("B69d_pulse", "SOLO", 6924)}


def evolved_latch(arm):
    d, a, sd = ARMS[arm]
    w0, s, _ = load24(); w = NoClock(w0)
    sc = lambda m: sum(group_pulse([m], w, s + 1000 + k, 16, 4)[0] for k in range(4)) / 4
    pop = json.loads((RES / d / ("B62_pop_%s_%d.json" % (a, sd))).read_text(encoding="utf-8"))
    return max(({json.dumps(m["genome"]): m for m in pop}).values(), key=sc)


def parity(pop):
    world, s, _ = B75.load(); w = NoClock(world)
    sc = lambda m: sum(group_reloc([m], w, s + 1000 + k, 16, P=4, Q=16, mode="random")[0] for k in range(4)) / 4
    n = 0; best = 0.0
    for m in {json.dumps(m["genome"]): m for m in pop}.values():
        r = sc(m); best = max(best, r)
        if r <= .040:
            continue
        lk = copy.deepcopy(m); lk["code_writable"] = False; lk["persist"] = "none"
        if r - sc(lk) >= .02:
            rf = B75.refind(m, w, s, world.R); n += bool(rf is not None and rf >= .31)
    return n, round(best, 4)


def cell(job):
    m0 = evolved_latch(job["arm"])

    def gen0():
        rec = G.organism_record(copy.deepcopy(m0), None, 0); rec["origins"] = ["gen0_" + job["arm"]]
        return [copy.deepcopy(rec) for _ in range(200)]

    B76.latch_gen0 = gen0; B76.OUT = OUT / job["arm"]; B76.OUT.mkdir(parents=True, exist_ok=True)
    r = B76.cell(job)
    pop = json.loads((B76.OUT / ("pop_%d.json" % job["seed"])).read_text(encoding="utf-8"))
    r["parity_reset_like"], r["parity_best"] = parity(pop)
    r["arm"] = job["arm"]; r["gen0_len"] = len(m0["genome"]) // 4
    return r


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    refs = B75.refs_(); rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 7901 + i, "G": int(argv[0]) if argv else 300, "refs": refs}): (a, i) for a in ARMS for i in range(6)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[f]; r = {"arm": a, "seed": 7901 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B79_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {a: sum(r.get("parity_reset_like", 0) >= 5 for r in rows if r["arm"] == a) for a in ARMS}
    print(json.dumps(summ))
    (OUT / "B79_result.json").write_text(json.dumps({"probe": "B79", "refs": refs, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
