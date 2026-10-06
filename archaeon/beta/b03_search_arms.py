"""B03 -- which generic SEARCH change lifts the W2_K2 0/60 summit record? (Phase 2-B Beta)

B01/B02: the organism can solve W2_K2 (16-20 instructions); the shelf -> summit gap is a SILENT PLATEAU of ~5
coordinated edits. Observation while designing B03: no length-changing operator in grammar v0.4 fixes up relative
jump offsets (insertion/deletion/duplication/movement/splice), so growing code inside a program silently retargets
every jump that spans the edit point.

Arms, equal compute (N=200, E=16, G=300, E0, FOUNDRY_C2, fresh gen 0 = the CMP3 cell population), 24 cell seeds:
  BASE   descend() unchanged (the CMP3 search).
  HEAVY  n_ops per child = 1 + Geometric(1/2), capped at 8 (mean ~2): more coordinated edits per child.
  RELOC  with prob .30 the child gets ONE relocation-aware structural edit (insert a random instruction, duplicate
         a block of 1-4, or delete one instruction), with every relative jump that spans the edit re-targeted;
         otherwise descend() unchanged. The ONLY difference from BASE is edit semantics.
Readout: summit = train best >= .90 AND held-out (48 episodes) >= .90; first summit generation; shelf reached.

PREDICTIONS (before running): BASE <= 1/24; HEAVY <= 3/24; RELOC >= 3/24 and > BASE (one-sided Fisher p < .10).
If RELOC does not beat BASE, jump fix-up is not the binding constraint and the next suspect is selection
(E=16 noise / elitism) rather than variation.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from math import comb
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.lineage import descend
from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, SUMMIT, TARGET
from archaeon.wse.evolve import Evolution, evaluate
from archaeon.wse.worlds import episodes_for

OUT = Path(__file__).resolve().parent / "results"
JUMPS = (18, 19, 20)
N_OPC = 25
M32 = 0xFFFFFFFF


def _off(w):
    return w - (1 << 32) if w >= (1 << 31) else w


def relocate(genome, pos, k):
    """Insert k instructions at instruction index pos (k<0 deletes -k at pos): fix every relative jump spanning it.
    Returns the fixed-up list of instructions (each a 4-word list) WITHOUT the inserted block."""
    ins = [genome[i:i + 4] for i in range(0, len(genome), 4)]
    out = []
    for i, w in enumerate(ins):
        w = list(w)
        if w[0] % N_OPC in JUMPS:
            tgt = i + _off(w[2])
            if k > 0:
                ni = i + (k if i >= pos else 0)
                nt = tgt + (k if tgt >= pos else 0)
            else:
                d = -k
                ni = i - (d if i >= pos + d else 0)
                nt = tgt - (d if tgt >= pos + d else 0)
            w[2] = (nt - ni) & M32
        out.append(w)
    return out


def reloc_child(parent, seed):
    rng = SplitMix64(seed_from("archaeon.beta.reloc", seed, parent["organism_id"]))
    m = dict(parent["manifest"]); g = list(m["genome"]); n = len(g) // 4
    kind = ("insert", "duplicate", "delete")[rng.randbelow(3)]
    if kind == "delete" and n <= 1:
        kind = "insert"
    if kind == "insert":
        pos = rng.randbelow(n + 1)
        block = [[rng.next_u32() for _ in range(4)]]
    elif kind == "duplicate":
        k = 1 + rng.randbelow(min(4, n)); src = rng.randbelow(n - k + 1); pos = rng.randbelow(n + 1)
        block = [g[(src + j) * 4:(src + j) * 4 + 4] for j in range(k)]
    if kind == "delete":
        pos = rng.randbelow(n)
        fixed = relocate(g, pos, -1)
        new = fixed[:pos] + fixed[pos + 1:]
    else:
        fixed = relocate(g, pos, len(block))
        new = fixed[:pos] + [list(b) for b in block] + fixed[pos:]
    words = [w for ins in new for w in ins]
    if not 4 <= len(words) <= min(4096, m["tape_words"]):
        return descend(parent, seed)
    m["genome"] = words
    child = G.organism_record(m, parent["lineage_id"], parent["generation"] + 1)
    rec = {"organism_id": child["organism_id"], "parent_ids": [parent["organism_id"]], "mutation_seed": seed,
           "operators": [{"operator": "reloc_" + kind}], "pre_hash": parent["organism_id"], "post_hash": child["organism_id"]}
    return child, rec


def make_descend(arm):
    if arm == "BASE":
        return None
    if arm == "HEAVY":
        def d(parent, seed, mate=None):
            r = SplitMix64(seed_from("archaeon.beta.heavy", seed)); k = 1
            while k < 8 and r.randbelow(2):
                k += 1
            return descend(parent, seed, mate=mate, n_ops=k)
        return d
    if arm == "RELOC":
        def d(parent, seed, mate=None):
            if SplitMix64(seed_from("archaeon.beta.relocgate", seed)).unit() < .30:
                return reloc_child(parent, seed)
            return descend(parent, seed, mate=mate)
        return d
    raise ValueError(arm)


def cell(job):
    arm, seed, G_ = job["arm"], job["seed"], job["G"]
    t0 = time.time()
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=16, branch="b03",
                   foundry=FOUNDRY_C2, descend_fn=make_descend(arm))
    eps = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", seed, 48)
    first = shelf = None; best = []
    for g in range(G_):
        row = ev.evaluate_generation(last=(g == G_ - 1))
        best.append(round(row["best_reward"], 4))
        if shelf is None and row["best_reward"] >= .45:
            shelf = g
        if row["best_reward"] >= SUMMIT and evaluate(ev.scored[0][1]["manifest"], eps, rng_seed=7)["reward"] >= SUMMIT:
            first = g
            elite = ev.scored[0][1]
            return {"arm": arm, "seed": seed, "first_summit_gen": first, "first_shelf_gen": shelf, "trace_best": best,
                    "summit_manifest": elite["manifest"], "summit_ancestry_ops": [o.get("operator") for a in ev.ancestry(elite["organism_id"]) for o in a.get("operators", [])],
                    "wall_s": round(time.time() - t0, 1)}
        if g < G_ - 1:
            ev.reproduce()
    elite = ev.scored[0][1]
    return {"arm": arm, "seed": seed, "first_summit_gen": None, "first_shelf_gen": shelf, "trace_best": best,
            "final_heldout": round(evaluate(elite["manifest"], eps, rng_seed=7)["reward"], 4),
            "final_manifest": elite["manifest"], "wall_s": round(time.time() - t0, 1)}


def fisher_one_sided(a, n1, b, n2):
    """P(X >= a) for X ~ hypergeometric: successes a of n1 in arm 1 vs b of n2 in arm 2 (arm 1 better)."""
    K, N = a + b, n1 + n2
    return sum(comb(K, x) * comb(N - K, n1 - x) for x in range(a, min(K, n1) + 1)) / comb(N, n1)


def main(argv):
    OUT.mkdir(exist_ok=True)
    seeds = list(range(301, 325))
    jobs = [{"arm": a, "seed": s, "G": 300} for s in seeds for a in ("BASE", "HEAVY", "RELOC")]
    rows = []
    with ProcessPoolExecutor(max_workers=24) as ex:
        for r in ex.map(cell, jobs):
            rows.append(r)
            print(json.dumps({k: r.get(k) for k in ("arm", "seed", "first_summit_gen", "first_shelf_gen", "final_heldout", "wall_s")}), flush=True)
    summ = {}
    for a in ("BASE", "HEAVY", "RELOC"):
        rr = [r for r in rows if r["arm"] == a]
        summ[a] = {"n": len(rr), "summits": sum(r["first_summit_gen"] is not None for r in rr),
                   "summit_gens": sorted(r["first_summit_gen"] for r in rr if r["first_summit_gen"] is not None),
                   "shelf": sum(r["first_shelf_gen"] is not None for r in rr)}
    for a in ("HEAVY", "RELOC"):
        summ[a]["fisher_vs_BASE_one_sided"] = fisher_one_sided(summ[a]["summits"], summ[a]["n"], summ["BASE"]["summits"], summ["BASE"]["n"])
    print(json.dumps(summ), flush=True)
    (OUT / "B03_result.json").write_text(json.dumps({"probe": "B03", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
