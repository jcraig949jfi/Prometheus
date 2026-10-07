"""B10 -- is the selection wall a fact about the INSTRUCTION SET? A branch-free SEL primitive (Phase 2-B Beta)

B08/B09/B07: two stored values + a data cue -> answer from the right one is unreachable for the CMP3 GA (0/8, 0/8,
0/36), while a two-slot fixed-order queue is reachable (4/8). In this VM, selection needs a conditional JUMP whose
relative offset must land between two OUT/HALT blocks. Organism change (one opcode, nothing else):

  SEL   op 24 (was RND):  regs[a] = regs[b] if regs[a] != 0 else regs[c]      -- a straight-line multiplexer

The variant VM is built from proteus/foundry/vm.py's OWN source with only the op-24 branch replaced (asserted), so
every other semantic is byte-identical. It is installed in archaeon.wse.evolve for SEL arms only.

Cells (CMP3 search: N=200, E=16, E0, FOUNDRY_C2, G=200, 8 seeds):  {stock, sel} x {L5_hint3, L6_w2k2}.
Controls: hand programs (stock branch dispatcher; SEL hint dispatcher; SEL tag solver) on both worlds and both VMs.

PREDICTIONS (before running): stock replicates 0/8 on both; SEL L5_hint3 >= 3/8; SEL L6_w2k2 >= 1/8.
If SEL L5 stays 0/8, the wall is not the jump structure but reading/holding the cue at all.
"""
from __future__ import annotations

import inspect
import json
import sys
import time
import types
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import proteus.foundry.vm as stockvm

from archaeon.beta.b01_w2k2_existence import (CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, SOLVER, TARGET, EQ, HALT, IN, JNZ, JZ,
                                              LDC, MOV, OUT_, _prog, manifest)
from archaeon.beta.b08_primitive_ladder import HINT_DISPATCH
from archaeon.beta.b09_dispatch_wall import eps_for as b09_eps
from archaeon.wse import evolve as EV
from archaeon.wse.worlds import episodes_for

OUT = Path(__file__).resolve().parent / "results"
SOLVED = 0.90
SEL = 24
OLD = "            elif op == 24:\n                regs[a] = rng.next_u32()\n                rnd_draws += 1\n"
NEW = ("            elif op == 24:\n                if regs[a] != 0:\n                    regs[a] = regs[bw % nr]\n"
       "                else:\n                    regs[a] = regs[cw % nr]\n")


def build_sel_vm():
    src = inspect.getsource(stockvm)
    assert src.count(OLD) == 1, "op-24 branch not found exactly once; the stock VM changed"
    src = src.replace(OLD, NEW).replace("from .affordances import", "from proteus.foundry.affordances import") \
             .replace("from .prng import", "from proteus.foundry.prng import")
    mod = types.ModuleType("archaeon_beta_selvm")
    exec(compile(src, "archaeon_beta_selvm", "exec"), mod.__dict__)
    return mod


SELVM = build_sel_vm()


def use_vm(kind):
    EV.Player = SELVM.Player if kind == "sel" else stockvm.Player


def world_eps(world, family, index, n):
    if world == "L6_w2k2":
        return episodes_for(TARGET, CAMPAIGN_SEED, family, index, n)
    return b09_eps("L5_hint3", family, index, n)


HEAD = [(IN, 1, 0), (LDC, 2, 1), (EQ, 3, 1, 2), (JZ, 3, 10), (IN, 4, 0), (IN, 5, 0), (JNZ, 6, 4), (MOV, 6, 4),
        (MOV, 7, 5), (HALT,), (MOV, 8, 4), (MOV, 9, 5), (HALT,)]
SEL_HINT = _prog(HEAD + [(IN, 4, 0), (IN, 3, 0), (SEL, 3, 9, 7), (OUT_, 3, 0), (HALT,)])        # h ? slotB : slotA
SEL_TAG = _prog(HEAD + [(IN, 4, 0), (EQ, 3, 4, 6), (SEL, 3, 7, 9), (OUT_, 3, 0), (HALT,)])      # tag==A ? A : B


def controls():
    out = {}
    for vm in ("stock", "sel"):
        use_vm(vm)
        for name, g in (("branch_hint_dispatch", HINT_DISPATCH), ("branch_tag_solver", SOLVER), ("sel_hint", SEL_HINT), ("sel_tag", SEL_TAG)):
            out["%s/%s" % (vm, name)] = {w: round(EV.evaluate(manifest(g), world_eps(w, "heldout", 7, 48), rng_seed=7)["reward"], 4)
                                         for w in ("L5_hint3", "L6_w2k2")}
    use_vm("stock")
    return out


def cell(job):
    vm, world, seed, G_ = job["vm"], job["world"], job["seed"], job["G"]
    use_vm(vm)
    t0 = time.time()
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=16, branch="b10", foundry=FOUNDRY_C2)
    ho = world_eps(world, "heldout", seed, 48)
    solved = None; best = []
    for g in range(G_):
        row = ev.evaluate_generation(episodes=world_eps(world, "train", g * 100003 + seed, 16), last=(g == G_ - 1))
        best.append(round(row["best_reward"], 4))
        if row["best_reward"] >= SOLVED and EV.evaluate(ev.scored[0][1]["manifest"], ho, rng_seed=7)["reward"] >= SOLVED:
            solved = g
            break
        if g < G_ - 1:
            ev.reproduce()
    elite = ev.scored[0][1]["manifest"]
    sel_used = sum(1 for i in range(0, len(elite["genome"]), 4) if elite["genome"][i] % 25 == SEL)
    return {"vm": vm, "world": world, "seed": seed, "solved_gen": solved, "max_train": max(best),
            "final_heldout": round(EV.evaluate(elite, ho, rng_seed=7)["reward"], 4), "elite_sel_instrs": sel_used,
            "elite_manifest": elite, "wall_s": round(time.time() - t0, 1)}


def main(argv):
    OUT.mkdir(exist_ok=True)
    G_ = int(argv[0]) if argv else 200
    ctl = controls(); print("controls", json.dumps(ctl), flush=True)
    jobs = [{"vm": v, "world": w, "seed": s, "G": G_} for s in range(1001, 1009) for v in ("sel", "stock") for w in ("L5_hint3", "L6_w2k2")]
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 24) as ex:
        for f in as_completed([ex.submit(cell, j) for j in jobs]):
            r = f.result(); rows.append(r)
            print(json.dumps({k: r[k] for k in ("vm", "world", "seed", "solved_gen", "final_heldout", "max_train", "elite_sel_instrs", "wall_s")}), flush=True)
    summ = {"%s/%s" % (v, w): sum(r["vm"] == v and r["world"] == w and r["solved_gen"] is not None for r in rows)
            for v in ("sel", "stock") for w in ("L5_hint3", "L6_w2k2")}
    print(json.dumps(summ), flush=True)
    (OUT / "B10_result.json").write_text(json.dumps({"probe": "B10", "G": G_, "controls": ctl, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
