"""B13 -- is the two-value wall a MEMORY-AFFORDANCE fact? A queue primitive (Phase 2-B Beta, organism lane)

B08J (2026-10-07, timing jitter removes delay lines): one stored value is reachable (L1 7/8, L3 8/8), a write-once
guard is reachable (L2 5/8), but TWO stored values in fixed order are not (L4 0/8, max held-out .65), nor anything
above. The pieces exist separately (guard, overwrite-store); their composition -- "store here unless full, else
there" -- does not. Organism change: give storage an AUTO-ADVANCING location so multi-item memory needs no composed
control flow.

  PUSH a  (op 24, was RND):   tape[glen + h % (n-glen-2)] = r_a ; h += 1     with h = tape[n-1]
  POPF a  (op 2,  was YIELD): r_a = tape[glen + t % (n-glen-2)] ; t += 1     with t = tape[n-2]
Head/tail live in the last two tape words, so they persist exactly when the tape persists (persist tape/all) and are
visible to the organism. Built from proteus/foundry/vm.py's own source with only those two branches replaced
(asserted). Every other semantic is byte-identical.

Cells: {stock, queue} x {L4_order, L6_w2k2}, both JITTERED in training and held-out (B08J's repaired instrument),
CMP3 search (N=200, E=16, E0, FOUNDRY_C2), fresh gen 0, G=300, 8 seeds.
Controls: hand queue program (PUT: IN tag; IN v; PUSH v. ASK: POPF r; OUT r) on both worlds and both VMs; the B01
slot solver on both VMs.

PREDICTIONS (before running): stock replicates L4 0/8, L6 0/8; queue L4 >= 5/8 (the composition wall disappears);
queue L6 0/8 (a FIFO answers in put order, W2_K2 asks in random order: content addressing is still missing).
"""
from __future__ import annotations

import inspect
import json
import sys
import types
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import proteus.foundry.vm as stockvm

import archaeon.beta.b08_primitive_ladder as B
from archaeon.beta.b01_w2k2_existence import SOLVER, HALT, IN, JZ, LDC, EQ, OUT_, _prog, manifest
from archaeon.beta.b08j_jittered_ladder import jittered
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results"
OLD24 = "            elif op == 24:\n                regs[a] = rng.next_u32()\n                rnd_draws += 1\n"
NEW24 = ("            elif op == 24:\n                _h = tape[n - 1]\n                tape[glen + _h % (n - glen - 2)] = regs[a]\n"
         "                tape[n - 1] = (_h + 1) & MASK32\n")
OLD2 = "            elif op == 2:\n                status = \"yield\"\n                ip = nip\n                break\n"
NEW2 = ("            elif op == 2:\n                _t = tape[n - 2]\n                regs[a] = tape[glen + _t % (n - glen - 2)]\n"
        "                tape[n - 2] = (_t + 1) & MASK32\n")


def build_queue_vm():
    src = inspect.getsource(stockvm)
    assert src.count(OLD24) == 1 and src.count(OLD2) == 1, "stock VM changed"
    src = src.replace(OLD24, NEW24).replace(OLD2, NEW2)
    src = src.replace("from .affordances import", "from proteus.foundry.affordances import").replace("from .prng import", "from proteus.foundry.prng import")
    mod = types.ModuleType("archaeon_beta_queuevm")
    exec(compile(src, "archaeon_beta_queuevm", "exec"), mod.__dict__)
    return mod


QVM = build_queue_vm()
PUSH, POPF = 24, 2
# PUT -> push value; ASK (kind 2 only: NOISE ticks must not pop) -> pop and output
QUEUE_PROG = _prog([(IN, 1, 0), (LDC, 2, 1), (EQ, 3, 1, 2), (JZ, 3, 5), (IN, 4, 0), (IN, 5, 0), (PUSH, 5), (HALT,),
                    (LDC, 2, 2), (EQ, 3, 1, 2), (JZ, 3, 3), (POPF, 6), (OUT_, 6, 0), (HALT,)])
WORLDS = ("L4_order", "L6_w2k2")


def use_vm(kind):
    EV.Player = QVM.Player if kind == "queue" else stockvm.Player


def controls():
    B.eps_for = jittered
    out = {}
    for vm in ("stock", "queue"):
        use_vm(vm)
        for name, g in (("queue_prog", QUEUE_PROG), ("slot_solver", SOLVER)):
            out["%s/%s" % (vm, name)] = {w: round(EV.evaluate(manifest(g), B.eps_for(w, "heldout", 7, 48), rng_seed=7)["reward"], 4)
                                         for w in WORLDS}
    use_vm("stock")
    return out


def cell(job):
    B.eps_for = jittered
    use_vm(job["vm"])
    r = B.cell({"rung": job["world"], "seed": job["seed"], "G": job["G"]})
    r["vm"] = job["vm"]
    g = r["elite_manifest"]["genome"]
    r["elite_push"] = sum(1 for i in range(0, len(g), 4) if g[i] % 25 == PUSH)
    r["elite_popf"] = sum(1 for i in range(0, len(g), 4) if g[i] % 25 == POPF)
    return r


def main(argv):
    OUT.mkdir(exist_ok=True)
    G_ = int(argv[0]) if argv else 300
    ctl = controls(); print("controls", json.dumps(ctl), flush=True)
    jobs = [{"vm": v, "world": w, "seed": s, "G": G_} for s in range(1301, 1309) for v in ("queue", "stock") for w in WORLDS]
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 20) as ex:
        for f in as_completed([ex.submit(cell, j) for j in jobs]):
            r = f.result(); rows.append(r)
            print(json.dumps({k: r.get(k) for k in ("vm", "rung", "seed", "solved_gen", "final_heldout", "max_train", "elite_push", "elite_popf", "wall_s")}), flush=True)
    summ = {"%s/%s" % (v, w): {"solved": sum(r["vm"] == v and r["rung"] == w and r["solved_gen"] is not None for r in rows),
                                "gens": sorted(r["solved_gen"] for r in rows if r["vm"] == v and r["rung"] == w and r["solved_gen"] is not None)}
            for v in ("queue", "stock") for w in WORLDS}
    print(json.dumps(summ), flush=True)
    (OUT / "B13_result.json").write_text(json.dumps({"probe": "B13", "G": G_, "controls": ctl, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
