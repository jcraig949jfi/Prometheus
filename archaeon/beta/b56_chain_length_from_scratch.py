"""B56 -- repair of B55's design: chain-length wiring test with the read opcode REMOVED from generation 0.

B55 (and its preview) found L1/L2 keyed solvers at GENERATION 0: random founders already contain the 1-2 instruction
read, so B55 measured founder probability, not whether search can BUILD the read. B56: identical to B55 except that
every op-2 instruction (OUTK / LDK2 / LDK) in every generation-0 genome is replaced by NOP (0, 0, 0, 0); the read must
then be created by mutation. Same worlds, search, held-out (64 x 4) and keyed criterion (K6 >= .9); 8 seeds per variant.
PREDICTION (before running): L1 >= 6/8 and L2 >= 4/8 BUILT by search (first train >= .9 at gen > 0), L3 <= 1/8.
If L2 also collapses, the 2-link chain is as hard as the 3-link one for search and B55's slope was founder chance.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b55_chain_length import VMS, score_k, train_eps
from archaeon.wse import evolve as EV
from archaeon.wse.evolve import gen0

OUT = Path(__file__).resolve().parent / "results"


def scrubbed_gen0(seed, N):
    pop = gen0(CAMPAIGN_SEED, seed, N, FOUNDRY_C2)
    out = []
    from proteus.foundry import generate as G
    for o in pop:
        g = list(o["manifest"]["genome"])
        for i in range(0, len(g), 4):
            if g[i] % 25 == 2:
                g[i:i + 4] = [0, 0, 0, 0]
        m = dict(o["manifest"], genome=g)
        rec = G.organism_record(m, None, 0); rec["origins"] = ["gen0_scrubbed"]
        out.append(rec)
    return out


def cell(job):
    v = job["variant"]
    EV.Player = VMS[v].Player
    pop = scrubbed_gen0(job["seed"], 200)
    prov = {"fill": "gen0 with op-2 scrubbed", "seed": job["seed"], "n": 200, "verified_common": True}
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=16, branch="b56", foundry=FOUNDRY_C2,
                      init_pop=pop, gen0_provenance=prov)
    first = None
    for g in range(job["G"]):
        row = ev.evaluate_generation(episodes=train_eps(g, job["seed"]), last=(g == job["G"] - 1))
        if first is None and row["best_reward"] >= .9:
            first = g
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    prof = {"K%d" % k: score_k(m, k, v) for k in (2, 3, 6)}
    return {"variant": v, "seed": job["seed"], "profile": prof, "keyed": prof["K6"] >= .9, "first_train_ge_.9": first,
            "built_by_search": prof["K6"] >= .9 and (first or 0) > 0, "elite_manifest": m}


def main(argv):
    G_ = int(argv[0]) if argv else 300
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"variant": v, "seed": 5601 + s, "G": G_}): (v, s) for s in range(8) for v in ("L1", "L2", "L3")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                v, s = futs[f]; r = {"variant": v, "seed": 5601 + s, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B56_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: x for k, x in r.items() if k != "elite_manifest"}) + chr(10))
    summ = {v: {"keyed": sum(r.get("variant") == v and r.get("keyed", False) for r in rows),
                "built": sum(r.get("variant") == v and r.get("built_by_search", False) for r in rows)} for v in ("L1", "L2", "L3")}
    print(json.dumps(summ), flush=True)
    (OUT / "B56_result.json").write_text(json.dumps({"probe": "B56", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
