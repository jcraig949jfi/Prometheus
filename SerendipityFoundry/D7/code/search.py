"""
Shared synthesis engine.  Every arm (Z0-random, Z0-cost, Z0-novelty, Z0-evo, Z1)
uses THIS code with THE SAME evaluation, verification, budget, and shaping signal.
Arms differ ONLY in the proposal prior `art_w` (and, for variants, the selection
rule) -- never in the grammar, hoard, verifier, or fitness.

Shaping fitness = -min field-distance to the primary target over the Gz closure.
This target-aware signal is identical across arms (it does not encode history).
A run "solves" when the primary target enters the Gz closure (exact verification).
"""

from __future__ import annotations
from substrate import z_size
from synthlang import random_program, mutate, crossover
from evalz import evaluate


def _fitness(res, size, cost_bias=0.0):
    f = -float(res["best_dist"])
    if cost_bias:
        f -= cost_bias * size
    return f


def search(world, S, targets, hoard, grammar, rng, meter,
           art_w=None, node_w=None, budget=1500, mode="evo",
           pop=48, tournament=3, elite=4, fresh_frac=0.25,
           cost_bias=0.0, novelty=False, seed_progs=None):
    """
    Returns dict: solved(bool), first_solve_eval(int|None), evals(int),
                  best(ast), best_fit, family_reached(set), z(ast|None).
    """
    ids = sorted(hoard.keys())
    art_w = art_w or {}
    node_w = node_w or {}
    evals = [0]
    first_solve = [None]
    archive = set()  # novelty behavior signatures
    primary = targets[0]

    def ev(ast):
        res = evaluate(ast, world, S, targets, hoard, meter=meter)
        evals[0] += 1
        meter.tick("synthesis_proposal", 1)
        if first_solve[0] is None and res["reached"][primary]:
            first_solve[0] = evals[0]
        return res

    def nov_key(res):
        # coarse behavior signature: closure size + which targets reached
        return (res["closure_size"], tuple(sorted(k for k, v in res["reached"].items() if v)))

    best = None
    best_fit = -1e9
    best_res = None

    def consider(ast, res):
        nonlocal best, best_fit, best_res
        f = _fitness(res, z_size(ast), cost_bias)
        if novelty:
            k = nov_key(res)
            if k not in archive:
                f += 5.0
                archive.add(k)
        if f > best_fit:
            best_fit, best, best_res = f, ast, res
        return f

    # -------- pure sampling mode (Z0-random / Z0-cost / Z0-novelty) --------
    if mode == "sample":
        while evals[0] < budget:
            ast = random_program(rng, ids, grammar, node_w=node_w, art_w=art_w)
            res = ev(ast)
            consider(ast, res)
            if res["reached"][primary] and not novelty:
                break
        fam = set(k for k, v in (best_res or {"reached": {}})["reached"].items() if v) if best_res else set()
        solved = first_solve[0] is not None
        zbest = best if solved else None
        return {"solved": solved, "first_solve_eval": first_solve[0], "evals": evals[0],
                "best": best, "best_fit": best_fit, "family_reached": fam,
                "z": zbest, "z_res": best_res}

    # -------- evolutionary mode (Z0-evo / Z1) --------
    population = []
    seeds = list(seed_progs or [])
    for i in range(pop):
        if i < len(seeds):
            ast = seeds[i]
        else:
            ast = random_program(rng, ids, grammar, node_w=node_w, art_w=art_w)
        res = ev(ast)
        consider(ast, res)
        population.append((ast, res))
        if res["reached"][primary]:
            break

    while evals[0] < budget and first_solve[0] is None:
        scored = [(consider(a, r), a, r) for (a, r) in population]
        scored.sort(key=lambda x: x[0], reverse=True)
        nxt = [(a, r) for (_, a, r) in scored[:elite]]
        while len(nxt) < pop and evals[0] < budget:
            if rng.random() < fresh_frac:
                child = random_program(rng, ids, grammar, node_w=node_w, art_w=art_w)
            else:
                # tournament parents
                def pick():
                    cand = [scored[rng.randrange(len(scored))] for _ in range(tournament)]
                    cand.sort(key=lambda x: x[0], reverse=True)
                    return cand[0][1]
                pa, pb = pick(), pick()
                if rng.random() < 0.5:
                    child = crossover(rng, pa, pb, grammar)
                else:
                    child = mutate(rng, pa, ids, grammar, node_w=node_w, art_w=art_w)
            meter.tick("recombination", 1)
            res = ev(child)
            consider(child, res)
            nxt.append((child, res))
            if res["reached"][primary]:
                break
        population = nxt

    fam = set(k for k, v in (best_res or {"reached": {}})["reached"].items() if v) if best_res else set()
    solved = first_solve[0] is not None
    zbest = best if solved else None
    return {"solved": solved, "first_solve_eval": first_solve[0], "evals": evals[0],
            "best": best, "best_fit": best_fit, "family_reached": fam,
            "z": zbest, "z_res": best_res}
