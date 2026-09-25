"""Measure the ACTUAL mutational topology of a genotype, never its semantic task difficulty.

For a tape, sample single-byte substitutions and evaluate each neighbour in ISOLATION (own tape, an empty neighbour
window, fresh inputs): does it still replicate (writes the window as the reproduction physics requires), does it
score higher / the same / lower on the current task, and does it score on the matched HARDER task (the next rung of
the task family)? The densities are the response geometry of that genotype: beneficial-neighbour density, neutral
fraction, replication-lethal fraction, and moat density (neighbours that already touch the next task).

Damage cliffs: k random byte damages (k = 1, 2, 4, 8, 16), the fraction of damaged copies that still replicate / still
solve -- the Atlas "damage cliff" and "length-mediated robustness" rulers on this substrate.

Everything is seeded and bounded (a few hundred VM executions per specimen)."""
from __future__ import annotations

import random
from typing import Dict, List, Optional

from prometheus.z80atlas import vm
from prometheus.z80atlas.tasks import Task, score as task_score
from prometheus.z80atlas.world import Config

NEXT_TASK = {"ECHO": "INC", "INC": "COND_ONE", "COND_ONE": "COND_MULTI", "CONST": "ECHO", "SUM2": None, "COND_MULTI": None}


def _eval(tape: bytes, cfg: Config, task: Task, rng: random.Random, n_inputs: int = 3) -> Dict:
    L = cfg.L; scores = []; rep = 0
    tape = bytes(tape[:L]) + bytes(max(0, L - len(tape)))   # a short witness is zero-padded: slice-assigning fewer bytes would SHRINK the memory
    for _ in range(n_inputs):
        mem = bytearray(256); mem[:L] = tape
        inputs = task.inputs(rng)
        for k, v in enumerate(inputs):
            mem[vm.IN_BASE + k] = v
        if cfg.layout == "SEPARATED":
            tr = vm.execute(mem, L, 0, cfg.budget // 2, inputs, region=(0, L // 2), allow_copyall=cfg.allow_copyall)
            tr2 = vm.execute(mem, L, L // 2, cfg.budget // 2, inputs, region=(L // 2, L), allow_copyall=cfg.allow_copyall)
            outs = tr.outputs + tr2.outputs; fi = tr.first_in_step if tr.first_in_step is not None else tr2.first_in_step
            fo = tr.first_out_step if tr.first_out_step is not None else tr2.first_out_step
            written = {a for a in list(tr.writes) + list(tr2.writes) if L <= a < 2 * L}
        else:
            tr = vm.execute(mem, L, 0, cfg.budget, inputs, allow_copyall=cfg.allow_copyall)
            outs = tr.outputs; fi = tr.first_in_step; fo = tr.first_out_step
            written = {a for a in tr.writes if L <= a < 2 * L}
        need = {"ENDOGENOUS_COPY": L, "ENDOGENOUS_PARTIAL": 1, "OVERWRITE": L // 2, "CONSTRUCTIVE": L // 2, "PAIR_EXECUTION": L // 2}.get(cfg.reproduction, L // 2)
        if len(written) >= need:
            child = bytes(mem[L:2 * L])
            fid = 1.0 - sum(1 for x, y in zip(child, tape[:L]) if x != y) / L
            if fid >= 0.9:
                rep += 1
        scores.append(task_score(task, outs, task.expected(inputs), "ATOMIC" if cfg.scoring == "NEUTRAL" else cfg.scoring, cfg.read_gate, fo, fi))
    return {"score": sum(scores) / len(scores), "replicates": rep == n_inputs}


def _pad(tape: bytes, L: int) -> bytes:
    return bytes(tape[:L]) + bytes(max(0, L - len(tape)))


def scan(tape: bytes, cfg: Config, task: Task, seed: int, n: int = 48) -> Dict:
    rng = random.Random(seed)
    L = cfg.L; tape = _pad(tape, L)
    base = _eval(tape, cfg, task, rng)
    nxt = Task(NEXT_TASK[task.kind], k=task.k) if NEXT_TASK.get(task.kind) else None
    base_next = _eval(tape, cfg, nxt, rng)["score"] if nxt else None
    better = same = worse = lethal = 0; moat = 0
    for _ in range(n):
        t = bytearray(tape[:L]); p = rng.randrange(L); t[p] = (t[p] + rng.randrange(1, 256)) & 0xFF
        e = _eval(bytes(t), cfg, task, rng)
        if base["replicates"] and not e["replicates"]:
            lethal += 1
        if e["score"] > base["score"] + 1e-9:
            better += 1
        elif abs(e["score"] - base["score"]) < 1e-9:
            same += 1
        else:
            worse += 1
        if nxt is not None:
            en = _eval(bytes(t), cfg, nxt, rng)["score"]
            if en > (base_next or 0.0) + 1e-9:
                moat += 1
    return {"n": n, "base_score": round(base["score"], 3), "base_replicates": base["replicates"],
            "beneficial_density": round(better / n, 3), "neutral_fraction": round(same / n, 3), "deleterious_fraction": round(worse / n, 3),
            "replication_lethal_fraction": round(lethal / n, 3) if base["replicates"] else None,
            "next_task": nxt.kind if nxt else None, "base_next_score": None if base_next is None else round(base_next, 3),
            "moat_density": round(moat / n, 3) if nxt else None}


def damage_cliff(tape: bytes, cfg: Config, task: Task, seed: int, trials: int = 12) -> Dict:
    rng = random.Random(seed); L = cfg.L; tape = _pad(tape, L)
    out = {}
    base = _eval(tape, cfg, task, rng)
    for k in (1, 2, 4, 8, 16):
        rep = solve = 0
        for _ in range(trials):
            t = bytearray(tape[:L])
            for p in rng.sample(range(L), min(k, L)):
                t[p] = rng.randrange(256)
            e = _eval(bytes(t), cfg, task, rng)
            rep += e["replicates"]; solve += e["score"] >= 0.999
        out["k%d" % k] = {"replicates": round(rep / trials, 3), "solves": round(solve / trials, 3)}
    return {"base_replicates": base["replicates"], "base_solves": base["score"] >= 0.999, "cliff": out}
