"""B51 -- a MUTATION lever for the memory law: insert a coupled write/read pair in ONE step.

Memory law: update-on-condition / keyed state is not reached across VM (B49), world (B40/B45/B47), incentive
(B22/B22b) and selection (B50). Its structure (B20/B22): a write ST [rA], v and a read LD x, [rA] through the SAME
address register are each silent alone, so the pair needs two coordinated silent edits.
Operator PAIR (generic structural prior, not task-specific): with probability .25 per child, pick a register rA among
those the parent already uses, insert ST [rA], rB at one random point and LD rC, [rA] at another (rB, rC also drawn
from used registers), with relative jumps re-targeted (B03 relocate); otherwise grammar v0.4 descend.
Arms (jittered-wide L4_order and L6_w2k2, CMP3 search via archaeon.wse.evolve, N=200, E=16, G=300, FOUNDRY_BIG gen 0
so tag addresses fit; 4 seeds per arm x world): PAIR vs BASE. Held-out 64 x 4 (B45 standard).
PREDICTION (before running): PAIR >= 1/4 on L6 (W2_K2) or L4; BASE 0/4 each.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.lineage import descend
from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, REGIMES, TARGET
from archaeon.beta.b03_search_arms import relocate
from archaeon.beta.b08_primitive_ladder import eps_for as plain_eps
from archaeon.beta.b08k_wide_jitter_rescore import wide
from archaeon.beta.b19_hidden_config_gate import FOUNDRY_BIG
from archaeon.beta.b21_operand_locality import used_registers
from archaeon.wse.evolve import Evolution, evaluate

OUT = Path(__file__).resolve().parent / "results"
LD, ST = 5, 6


def eps(rung, family, index, n):
    return wide(plain_eps(rung, family, index, n), ("b51", rung, family, index))


def insert_at(genome, pos, ins):
    fixed = relocate(genome, pos, 1)
    new = fixed[:pos] + [list(ins)] + fixed[pos:]
    return [w for i in new for w in i]


def pair_descend(parent, seed, mate=None):
    rng = SplitMix64(seed_from("archaeon.beta.b51", seed, parent["organism_id"]))
    if rng.unit() >= .25:
        return descend(parent, seed, mate=mate)
    m = dict(parent["manifest"]); g = list(m["genome"]); nr = m["n_regs"]
    used = used_registers(g, nr) or list(range(nr))
    ra, rb, rc = (used[rng.randbelow(len(used))] for _ in range(3))
    n = len(g) // 4
    p1 = rng.randbelow(n + 1)
    g = insert_at(g, p1, (ST, ra, rb, 0))
    p2 = rng.randbelow(len(g) // 4 + 1)
    g = insert_at(g, p2, (LD, rc, ra, 0))
    if len(g) > m["tape_words"] or len(g) > 4096:
        return descend(parent, seed, mate=mate)
    m["genome"] = g
    child = G.organism_record(m, parent["lineage_id"], parent["generation"] + 1)
    return child, {"organism_id": child["organism_id"], "parent_ids": [parent["organism_id"]], "mutation_seed": seed,
                   "operators": [{"operator": "coupled_pair"}], "pre_hash": parent["organism_id"], "post_hash": child["organism_id"]}


def heldout(m, rung):
    return sum(evaluate(m, eps(rung, "heldout", 7 + k, 64), rng_seed=7)["reward"] for k in range(4)) / 4


def cell(job):
    arm, rung, seed, G_ = job["arm"], job["rung"], job["seed"], job["G"]
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=16, branch="b51", foundry=FOUNDRY_BIG,
                   descend_fn=pair_descend if arm == "PAIR" else None)
    solved = None; best = []
    for g in range(G_):
        row = ev.evaluate_generation(episodes=eps(rung, "train", g * 100003 + seed, 16), last=(g == G_ - 1))
        best.append(round(row["best_reward"], 4))
        if row["best_reward"] >= .9 and heldout(ev.scored[0][1]["manifest"], rung) >= .9:
            solved = g
            break
        if g < G_ - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    g_ = m["genome"]
    return {"arm": arm, "rung": rung, "seed": seed, "solved_gen": solved, "heldout": round(heldout(m, rung), 4),
            "max_train": max(best), "elite_LD": sum(1 for i in range(0, len(g_), 4) if g_[i] % 25 == LD),
            "elite_ST": sum(1 for i in range(0, len(g_), 4) if g_[i] % 25 == ST), "elite_manifest": m}


def main(argv):
    G_ = int(argv[0]) if argv else 300
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "rung": r, "seed": 5101 + s, "G": G_}): (a, r, s)
                for s in range(4) for r in ("L4_order", "L6_w2k2") for a in ("PAIR", "BASE")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, rr, s = futs[f]; r = {"arm": a, "rung": rr, "seed": 5101 + s, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B51_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    summ = {"%s/%s" % (a, r): sum(x.get("arm") == a and x.get("rung") == r and x.get("solved_gen") is not None for x in rows)
            for a in ("PAIR", "BASE") for r in ("L4_order", "L6_w2k2")}
    print(json.dumps(summ), flush=True)
    (OUT / "B51_result.json").write_text(json.dumps({"probe": "B51", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
