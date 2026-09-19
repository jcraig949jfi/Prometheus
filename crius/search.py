"""Outer search: (mu + lambda) mutation-and-selection over Player programs.

The search is scaffolding (charter s7). Fitness is the frozen C0_EFFICIENCY
averaged over the configured search seeds, ACCUMULATED condition. Every
evaluated candidate gets a CandidateReceipt (candidate_id, parent_id,
modification, iteration, fitness components) appended to candidates.jsonl,
so the whole ancestry is reconstructible.

Arms (DESIGN_C0.md C1):
  random  initial population of random programs
  seeded  initial population = the bytecode ENUMERATE seed plus its mutants

CLI: python -m crius.search --config crius/configs/c0.json --iterations 150 --seed 1 --arm seeded
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time
from multiprocessing import Pool

from . import evaluate, receipts, streams, tasks as tasks_mod, vm
from .player import VMPlayer

MUTATIONS = ("replace", "arg", "const", "insert", "delete", "swap", "duplicate")


# ---------------------------------------------------------------- program generation


def random_arg(rng: random.Random, kind: str, length: int) -> int:
    if kind == "R":
        return rng.randrange(vm.NREG)
    if kind == "I":
        return rng.randint(*vm.IMM_RANGE)
    if kind == "A":
        return rng.randrange(max(1, length))
    if kind == "F":
        return rng.randrange(len(vm.INPUT_FIELDS))
    return 0


_OPSET = [None]


def set_opset(cfg: dict) -> None:
    _OPSET[0] = vm.opcode_names(cfg.get("substrate", {}))


def random_instruction(rng: random.Random, length: int) -> tuple:
    name = rng.choice(_OPSET[0] or vm.opcode_names({}))
    kinds = vm.OPSPEC[name]
    return (vm.OP[name],) + tuple(random_arg(rng, k, length) for k in kinds)


def random_program(rng: random.Random, cfg: dict) -> list:
    lo, hi = cfg["search"]["init_len"]
    n = rng.randint(lo, hi)
    return [random_instruction(rng, n) for _ in range(n)]


def _shift_targets(program: list, pos: int, delta: int) -> list:
    out = []
    for ins in program:
        name = vm.OPNAMES[ins[0]]
        kinds = vm.OPSPEC[name]
        vals = list(ins[1:])
        for i, k in enumerate(kinds):
            if k == "A" and vals[i] >= pos:
                vals[i] = max(0, vals[i] + delta)
        out.append((ins[0],) + tuple(vals))
    return out


def mutate(program: list, rng: random.Random, cfg: dict) -> tuple:
    """One mutation. Returns (new_program, description)."""
    prog = list(program)
    n = len(prog)
    maxlen = cfg["vm"]["max_program_len"]
    op = rng.choice(MUTATIONS)
    if n == 0:
        op = "insert"
    if op == "replace":
        i = rng.randrange(n)
        prog[i] = random_instruction(rng, n)
        return prog, "replace@%d" % i
    if op == "arg":
        i = rng.randrange(n)
        name = vm.OPNAMES[prog[i][0]]
        kinds = [k for k in vm.OPSPEC[name] if k != "N"]
        if not kinds:
            return mutate(program, rng, cfg)
        j = rng.randrange(len(kinds))
        vals = list(prog[i][1:])
        vals[j] = random_arg(rng, kinds[j], n)
        prog[i] = (prog[i][0],) + tuple(vals)
        return prog, "arg@%d.%d" % (i, j)
    if op == "const":
        consts = [i for i, ins in enumerate(prog) if vm.OPNAMES[ins[0]] in ("CONST", "ACTI")]
        if not consts:
            return mutate(program, rng, cfg)
        i = rng.choice(consts)
        vals = list(prog[i][1:])
        slot = 1 if vm.OPNAMES[prog[i][0]] == "CONST" else 0
        vals[slot] = vals[slot] + rng.choice((-2, -1, 1, 2))
        prog[i] = (prog[i][0],) + tuple(vals)
        return prog, "const@%d" % i
    if op == "insert":
        if n >= maxlen:
            return mutate(program, rng, cfg)
        i = rng.randrange(n + 1)
        prog = _shift_targets(prog, i, 1)
        prog.insert(i, random_instruction(rng, n + 1))
        return prog, "insert@%d" % i
    if op == "delete":
        if n <= 1:
            return mutate(program, rng, cfg)
        i = rng.randrange(n)
        del prog[i]
        prog = _shift_targets(prog, i + 1, -1)
        return prog, "delete@%d" % i
    if op == "swap":
        if n < 2:
            return mutate(program, rng, cfg)
        i, j = rng.sample(range(n), 2)
        prog[i], prog[j] = prog[j], prog[i]
        return prog, "swap@%d,%d" % (i, j)
    if op == "duplicate":
        if n >= maxlen or n == 0:
            return mutate(program, rng, cfg)
        a = rng.randrange(n)
        ln = rng.randint(1, min(6, n - a, maxlen - n))
        seg = prog[a : a + ln]
        i = rng.randrange(n + 1)
        prog = _shift_targets(prog, i, ln)
        prog[i:i] = seg
        return prog, "duplicate@%d+%d->%d" % (a, ln, i)
    raise AssertionError(op)


def make_child(program: list, rng: random.Random, cfg: dict) -> tuple:
    lo, hi = cfg["search"]["mutations_per_child"]
    k = rng.randint(lo, hi)
    mods = []
    prog = program
    for _ in range(k):
        prog, m = mutate(prog, rng, cfg)
        mods.append(m)
    return prog, "+".join(mods)


# ---------------------------------------------------------------- evaluation


_WORKER = {}


def _init_worker(cfg: dict):
    _WORKER["cfg"] = cfg
    vm.set_substrate(cfg.get("substrate", {}))
    _WORKER["tasks"] = {s: streams.lifetime(cfg, s, "search") for s in cfg["seeds"]["search"]}


def _set_streams(seeds):
    """Rotating streams: (re)build the worker's task streams for these seeds."""
    cfg = _WORKER["cfg"]
    _WORKER["tasks"] = {s: streams.lifetime(cfg, s, "search") for s in seeds}


def evaluate_program(payload) -> dict:
    prog_json, seeds = payload
    cfg = _WORKER["cfg"]
    if set(seeds) != set(_WORKER["tasks"]):
        _set_streams(seeds)
    player = VMPlayer(vm.program_from_json(prog_json))
    per_seed = {}
    for seed, tasks in _WORKER["tasks"].items():
        life = evaluate.run_lifetime(player, tasks, cfg, "ACCUMULATED", seed=seed)
        m = life["metrics"]
        per_seed[str(seed)] = {
            "fitness": m["fitness"],
            "C1_FITNESS": m["C1_FITNESS"],
            "charged_cost_total": m["charged_cost_total"],
            "invalid_actions_total": m["invalid_actions_total"],
            "store_trace": _sum_traces(life["task_results"]),
            "C0_EFFICIENCY": m["C0_EFFICIENCY"],
            "competence_gained": m["competence_gained"],
            "experience": m["experience"],
            "compute": m["compute"],
            "retained_state": m["retained_state"],
            "successes": m["successes"],
            "interactions_total": m["interactions_total"],
            "vm_steps_total": m["vm_steps_total"],
            "ws_cost_total": m["ws_cost_total"],
            "blocks_created_total": m["blocks_created_total"],
            "artifacts_invoked_total": m["artifacts_invoked_total"],
            "workspace_bytes_final": life["workspace_history"][-1]["bytes"],
            "late_early_ratio_by_depth": m["late_early_ratio_by_depth"],
            "by_stage": {k: (v["mean_cost"], v["success_rate"]) for k, v in m["by_stage"].items()},
            "adaptation_curve": m["adaptation_curve"],
            "replay_hash": life["replay_hash"],
        }
    fit = sum(v["fitness"] for v in per_seed.values()) / len(per_seed)
    return {"fitness": round(fit, 5), "per_seed": per_seed, "length": len(prog_json), "stream_seeds": list(seeds)}


def _sum_traces(task_results):
    out = {}
    for r in task_results:
        for k, v in r.get("store_trace", {}).items():
            out[k] = out.get(k, 0) + v
    return out


def _eval_many(pool, progs, seeds):
    payload = [(vm.program_to_json(p), list(seeds)) for p in progs]
    if pool is None:
        return [evaluate_program(p) for p in payload]
    return pool.map(evaluate_program, payload, chunksize=1)


def splice(child: list, donor: list, rng: random.Random, cfg: dict) -> tuple:
    """Generic segment splice (DESIGN_C1 s5): copy a contiguous segment of the donor into the child."""
    maxlen = cfg["vm"]["max_program_len"]
    if not donor or len(child) >= maxlen:
        return child, "splice:none"
    lo, hi = cfg["search"].get("splice_len", [1, 8])
    ln = rng.randint(lo, min(hi, len(donor), maxlen - len(child)))
    a = rng.randrange(len(donor) - ln + 1)
    seg = donor[a : a + ln]
    i = rng.randrange(len(child) + 1)
    out = _shift_targets(child, i, ln)
    out[i:i] = seg
    return out, "splice@%d<-donor[%d:%d]" % (i, a, a + ln)


# ---------------------------------------------------------------- the loop


def run_search(cfg: dict, config_path: str, iterations: int, seed: int, arm: str, workers: int,
               run_id: str, mu: int = None, lam: int = None, out_root: str = None) -> str:
    mu = mu or cfg["search"]["mu"]
    lam = lam or cfg["search"]["lambda"]
    set_opset(cfg)
    vm.set_substrate(cfg.get("substrate", {}))
    paired = int(cfg.get("streams", {}).get("paired", 1))
    takeover = bool(cfg.get("streams", {}).get("takeover_check", False))
    donors = []
    for pname in cfg["search"].get("parts_donors", []):
        from . import parts_c2
        donors.append((pname, parts_c2.program(pname)))
    out = os.path.join(out_root or os.path.join("crius", "runs"), run_id)
    os.makedirs(out, exist_ok=True)
    meta = receipts.run_meta(cfg, config_path)
    meta.update({"run_id": run_id, "arm": arm, "iterations": iterations, "search_seed": seed, "mu": mu, "lambda": lam})
    receipts.write_json(os.path.join(out, "RUN_META.json"), meta)
    take_f = open(os.path.join(out, "takeovers.jsonl"), "w", encoding="ascii", newline="\n")
    rng = random.Random("search:%s:%d" % (arm, seed))
    cand_f = open(os.path.join(out, "candidates.jsonl"), "w", encoding="ascii", newline="\n")
    iter_f = open(os.path.join(out, "iterations.jsonl"), "w", encoding="ascii", newline="\n")

    def emit(rec):
        cand_f.write(json.dumps(rec, sort_keys=True) + "\n")
        cand_f.flush()

    # initial population
    rotate = cfg.get("streams", {}).get("rotate", False)

    def seeds_for(it):
        if not rotate:
            return list(cfg["seeds"]["search"])
        base = streams.search_stream_seed(cfg, it, seed)
        return [base * 10 + k for k in range(paired)]  # paired common-random streams (DESIGN_C2 s3)

    def check_seed(it):
        return streams.search_stream_seed(cfg, it, seed) * 10 + 9
    if arm in ("seeded", "recombination"):
        seedprog = vm.enumerate_program()
        init = [(seedprog, None, "seed:ENUMERATE_VM")]
        while len(init) < mu:
            child, mod = make_child(seedprog, rng, cfg)
            init.append((child, vm.program_hash(seedprog), mod))
    elif arm == "random":
        init = [(random_program(rng, cfg), None, "random_init") for _ in range(mu)]
    else:
        raise ValueError(arm)
    pool = Pool(workers, initializer=_init_worker, initargs=(cfg,)) if workers > 1 else None
    if pool is None:
        _init_worker(cfg)
    t0 = time.time()
    evals = _eval_many(pool, [p for p, _, _ in init], seeds_for(0))
    population = []
    for (prog, parent, mod), ev in zip(init, evals):
        cid = vm.program_hash(prog)
        rec = {"candidate_id": cid, "parent_id": parent, "modification": mod, "iteration": 0,
               "program": vm.program_to_json(prog), **ev}
        emit(rec)
        population.append((ev["fitness"], len(prog), cid, prog, rec))
    population.sort(key=lambda x: (-x[0], x[1], x[2]))
    population = population[:mu]
    seen = {p[2] for p in population}
    best_ever = population[0]
    for it in range(1, iterations + 1):
        children = []
        while len(children) < lam:
            _, _, pcid, pprog, _ = rng.choice(population)
            child, mod = make_child(pprog, rng, cfg)
            if arm == "recombination" and rng.random() < cfg["search"].get("splice_fraction", 0.3):
                pool = [(p[2], p[3]) for p in population] + [("PART:" + n, prog) for n, prog in donors]
                dcid, dprog = rng.choice(pool)
                child, m2 = splice(child, dprog, rng, cfg)
                mod = mod + "+" + m2 + ":" + dcid
            ccid = vm.program_hash(child)
            if ccid in seen or not child:
                continue
            seen.add(ccid)
            children.append((child, pcid, mod, ccid))
        cur_seeds = seeds_for(it)
        if rotate:
            # common random numbers within the comparison: parents are re-evaluated on this iteration's stream
            pevals = _eval_many(pool, [p[3] for p in population], cur_seeds)
            population = [(ev["fitness"], p[1], p[2], p[3], {**p[4], "reeval": ev}) for p, ev in zip(population, pevals)]
        evals = _eval_many(pool, [c[0] for c in children], cur_seeds)
        elite_ids = {p[2] for p in population}
        newcomers = []
        for (child, pcid, mod, ccid), ev in zip(children, evals):
            rec = {"candidate_id": ccid, "parent_id": pcid, "modification": mod, "iteration": it,
                   "program": vm.program_to_json(child), **ev}
            emit(rec)
            newcomers.append((ev["fitness"], len(child), ccid, child, rec))
        merged = sorted(population + newcomers, key=lambda x: (-x[0], x[1], x[2]))
        if takeover and rotate:
            # DESIGN_C2 s3: a child may displace an elite member only if it also wins on an independent check stream
            proposed = merged[:mu]
            displaced = [p for p in population if p[2] not in {q[2] for q in proposed}]
            entering = [q for q in proposed if q[2] not in elite_ids]
            if entering and displaced:
                cs = [check_seed(it)]
                cev = _eval_many(pool, [q[3] for q in entering] + [p[3] for p in displaced], cs)
                ent_check = {q[2]: e["fitness"] for q, e in zip(entering, cev[: len(entering)])}
                dis_check = sorted(((e["fitness"], p) for p, e in zip(displaced, cev[len(entering):])), key=lambda x: x[0])
                keep_out = set()
                for q in sorted(entering, key=lambda q: q[0]):  # weakest entrant against the strongest displaced
                    if not dis_check:
                        break
                    dfit, dp = dis_check[-1]
                    rec_t = {"iteration": it, "child": q[2], "child_paired": q[0], "child_check": ent_check[q[2]],
                             "displaced": dp[2], "displaced_paired": dp[0], "displaced_check": dfit}
                    if ent_check[q[2]] >= dfit:
                        rec_t["outcome"] = "takeover"
                        dis_check.pop()
                    else:
                        rec_t["outcome"] = "blocked"
                        keep_out.add(q[2])
                        dis_check.pop()
                        merged = [m for m in merged if m[2] != q[2]] + [dp]
                    take_f.write(json.dumps(rec_t) + "\n")
                take_f.flush()
                merged = sorted({m[2]: m for m in merged}.values(), key=lambda x: (-x[0], x[1], x[2]))
        population = merged
        population = population[:mu]
        if population[0][0] > best_ever[0]:
            best_ever = population[0]
        fits = [p[0] for p in population]
        row = {"iteration": it, "best": population[0][0], "best_id": population[0][2],
               "mean_pop": round(sum(fits) / len(fits), 5), "best_ever": best_ever[0],
               "best_len": population[0][1], "elapsed_s": round(time.time() - t0, 1),
               "children_mean": round(sum(e["fitness"] for e in evals) / len(evals), 5)}
        iter_f.write(json.dumps(row) + "\n")
        iter_f.flush()
        if it % 10 == 0 or it == 1:
            print("it %4d  best %.4f (len %d)  pop mean %.4f  children mean %.4f  %.0fs" % (
                it, row["best"], row["best_len"], row["mean_pop"], row["children_mean"], row["elapsed_s"]), flush=True)
    if pool is not None:
        pool.close()
        pool.join()
    cand_f.close()
    iter_f.close()
    take_f.close()
    final = {
        "run_id": run_id, "arm": arm, "iterations": iterations,
        "best": {"candidate_id": best_ever[2], "fitness": best_ever[0], "program": vm.program_to_json(best_ever[3]),
                 "listing": vm.disassemble(best_ever[3]), "receipt": best_ever[4]},
        "final_population": [{"candidate_id": p[2], "fitness": p[0], "length": p[1]} for p in population],
        "elapsed_s": round(time.time() - t0, 1),
    }
    receipts.write_json(os.path.join(out, "best.json"), final)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--iterations", type=int, default=150)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--arm", choices=("random", "seeded", "recombination"), default="seeded")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--mu", type=int, default=None)
    ap.add_argument("--lambda", dest="lam", type=int, default=None)
    args = ap.parse_args(argv)
    cfg = receipts.load_config(args.config)
    run_id = args.run_id or "search_%s_s%d_%s" % (args.arm, args.seed, time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
    out = run_search(cfg, args.config, args.iterations, args.seed, args.arm, args.workers, run_id, args.mu, args.lam)
    print("run:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
