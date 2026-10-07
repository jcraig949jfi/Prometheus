"""B21 -- operand-locality mutation: does biasing register operands toward registers the program already uses make
the coupled write/read pair reachable? (Phase 2-B Beta, generic search change)

B20: the indexed solver is an isolated peak behind a coupled write/read pair (ST [r_tag] and LD [r_tag] must name
the SAME register the tag was read into). Under grammar v0.4 a new instruction's register fields are uniform over
n_regs (2-16), so two independent edits agreeing on one register is ~1/n_regs^2 per pair of edits.
Operator change (generic, not task-specific): after descend(), find the first instruction that differs from the
parent; if its opcode reads/writes registers (not LDC's immediate, not a jump offset), with probability .5 redraw
each register field uniformly from the registers ALREADY referenced elsewhere in the parent program.

Cells: jittered L4_order and L6_w2k2 (B08J instrument), CMP3 search (N=200, E=16, E0, FOUNDRY_C2), G=300, 4 seeds
each; comparison B08J (L4 0/8, L6 0/8). Light rule: 2 procs.
PREDICTION (before running): L4 >= 1/4 or L6 >= 1/4. If both 0/4, operand agreement is not the binding piece and
the silent-pair plateau needs a world-level stepping stone (next: B22).
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.lineage import descend
from proteus.foundry.prng import SplitMix64, seed_from

import archaeon.beta.b08_primitive_ladder as B
from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET
from archaeon.beta.b08j_jittered_ladder import jittered
from archaeon.wse.evolve import Evolution, evaluate

OUT = Path(__file__).resolve().parent / "results"
SOLVED = 0.90
NO_REGS = {0, 1, 2}                      # NOP HALT YIELD
B_IS_IMM = {3, 18}                       # LDC imm; JMP offset
JUMP_B = {19, 20}                        # JZ/JNZ: a is a register, b is an offset


def used_registers(g, nr):
    used = set()
    for i in range(0, len(g), 4):
        op = g[i] % 25
        if op in NO_REGS:
            continue
        used.add(g[i + 1] % nr)
        if op not in B_IS_IMM and op not in JUMP_B:
            used.add(g[i + 2] % nr)
            if op >= 7 and op <= 17:
                used.add(g[i + 3] % nr)
    return sorted(used)


def local_descend(parent, seed, mate=None):
    child, rec = descend(parent, seed, mate=mate)
    rng = SplitMix64(seed_from("archaeon.beta.b21", seed, parent["organism_id"]))
    if rng.unit() >= .5:
        return child, rec
    pg, cg = parent["manifest"]["genome"], list(child["manifest"]["genome"])
    nr = child["manifest"]["n_regs"]
    idx = next((i for i in range(0, min(len(pg), len(cg)), 4) if pg[i:i + 4] != cg[i:i + 4]),
               (min(len(pg), len(cg)) // 4) * 4 if len(cg) > len(pg) else None)
    if idx is None or idx + 4 > len(cg):
        return child, rec
    used = used_registers(pg, nr)
    op = cg[idx] % 25
    if not used or op in NO_REGS:
        return child, rec
    fields = [1] + ([] if op in B_IS_IMM or op in JUMP_B else [2]) + ([3] if 7 <= op <= 17 else [])
    for f in fields:
        cg[idx + f] = used[rng.randbelow(len(used))]
    m = dict(child["manifest"]); m["genome"] = cg
    new = G.organism_record(m, parent["lineage_id"], parent["generation"] + 1)
    rec = dict(rec, organism_id=new["organism_id"], post_hash=new["organism_id"],
               operators=list(rec.get("operators", [])) + [{"operator": "operand_locality", "index": idx // 4}])
    return new, rec


def cell(job):
    B.eps_for = jittered
    rung, seed, G_ = job["rung"], job["seed"], job["G"]
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=16, branch="b21", foundry=FOUNDRY_C2,
                   descend_fn=local_descend)
    ho = B.eps_for(rung, "heldout", seed, 48)
    solved, best = None, []
    for g in range(G_):
        row = ev.evaluate_generation(episodes=B.eps_for(rung, "train", g * 100003 + seed, 16), last=(g == G_ - 1))
        best.append(round(row["best_reward"], 4))
        if row["best_reward"] >= SOLVED and evaluate(ev.scored[0][1]["manifest"], ho, rng_seed=7)["reward"] >= SOLVED:
            solved = g
            break
        if g < G_ - 1:
            ev.reproduce()
    elite = ev.scored[0][1]["manifest"]
    return {"rung": rung, "seed": seed, "solved_gen": solved, "max_train": max(best),
            "final_heldout": round(evaluate(elite, ho, rng_seed=7)["reward"], 4), "elite_manifest": elite}


def main(argv):
    OUT.mkdir(exist_ok=True)
    G_ = int(argv[0]) if argv else 300
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 2) as ex:
        futs = {ex.submit(cell, {"rung": r, "seed": 2101 + s, "G": G_}): (r, s) for s in range(4) for r in ("L4_order", "L6_w2k2")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                rr, s = futs[f]; r = {"rung": rr, "seed": 2101 + s, "solved_gen": None, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B21_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    summ = {r: sum(x["rung"] == r and x["solved_gen"] is not None for x in rows) for r in ("L4_order", "L6_w2k2")}
    print(json.dumps(summ), flush=True)
    (OUT / "B21_result.json").write_text(json.dumps({"probe": "B21", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
