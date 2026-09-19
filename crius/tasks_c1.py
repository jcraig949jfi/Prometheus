"""Campaign 1 stream generator: (namespace, seed) -> permutation, library, 50-task lifetime.

Frozen procedural generator (DESIGN_C1 s1-s2). The qualification namespace
"qual" is sealed: search uses namespace "search" only, and the namespace
is part of the generator key.
"""

from __future__ import annotations

import hashlib
import json
import random

from . import world_c1 as w
from .tasks import TaskSpec

NAMESPACES = ("search", "qual", "gate")


def _rng(cfg: dict, namespace: str, seed: int) -> random.Random:
    key = "c1:%s:%s:%d:%s" % (cfg["generator"]["version"], namespace, seed, w.WORLD_VERSION)
    return random.Random(key)


def _task(cfg, rng, perm, library, chain, stage, family, index) -> TaskSpec:
    depth = len(chain)
    budget = cfg["budgets"]["interactions_by_depth"][str(depth)]
    steps = cfg["budgets"]["steps_per_task"]
    for _ in range(50):
        start = tuple(rng.randrange(w.B) for _ in range(w.L))
        target = w.apply_chain([(library[t], a) for t, a in chain], start)
        if target != start:
            break
    else:
        return None  # the chain is (near-)identity; the caller redraws it
    tid = hashlib.sha256(json.dumps([start, target, chain, stage, family, index]).encode("ascii")).hexdigest()[:12]
    return TaskSpec(
        task_id=tid, start=start, target=target, interaction_budget=budget, step_budget=steps,
        composition=tuple(chain), depth=depth, stage=stage, family=family, world_id="c1", perm=perm,
    )


def _distinct_chain(rng, k, d):
    ts = rng.sample(range(k), d)
    return [(t, rng.randrange(w.L)) for t in ts]


def _repeat_chain(rng, k, d):
    while True:
        ts = [rng.randrange(k) for _ in range(d)]
        if len(set(ts)) < d:
            return [(t, rng.randrange(w.L)) for t in ts]


def make_stream(cfg: dict, namespace: str, seed: int) -> dict:
    assert namespace in NAMESPACES, namespace
    g = cfg["generator"]
    rng = _rng(cfg, namespace, seed)
    perm = w.draw_perm(rng)
    library = w.draw_library(rng, g["templates"], g["min_steps"], g["max_steps"])
    k = len(library)
    sizes = cfg["lifetime"]["stages"]
    stages = []
    a = [[(t, rng.randrange(w.L))] for t in range(k) for _ in range(3)]
    while len(a) < sizes["A"]:
        a.append([(rng.randrange(k), rng.randrange(w.L))])
    stages.append(("A", [(c, "single") for c in a[: sizes["A"]]]))
    stages.append(("B", [([(rng.randrange(k), rng.randrange(w.L))], "single_new_arg") for _ in range(sizes["B"])]))
    stages.append(("C", [(_distinct_chain(rng, k, 2), "chain2") for _ in range(sizes["C"])]))
    stages.append(("D", [(_distinct_chain(rng, k, 3), "chain3") for _ in range(sizes["D"])]))
    ne = sizes["E"]
    if namespace == "qual":
        e = [(_repeat_chain(rng, k, 3), "chain_repeat3") for _ in range(ne // 2)]
        e += [(_repeat_chain(rng, k, 4) if rng.random() < 0.5 else _distinct_chain(rng, k, min(4, k)) + [(rng.randrange(k), rng.randrange(w.L))],
                "chain4") for _ in range(ne - ne // 2)]
    else:
        e = [(_repeat_chain(rng, k, 2), "chain_repeat2") for _ in range(ne // 2)]
        e += [(_repeat_chain(rng, k, 3), "chain_repeat3") for _ in range(ne - ne // 2)]
    stages.append(("E", e))
    tasks = []
    index = 0
    redraw = {"single": lambda: [(rng.randrange(k), rng.randrange(w.L))],
              "single_new_arg": lambda: [(rng.randrange(k), rng.randrange(w.L))],
              "chain2": lambda: _distinct_chain(rng, k, 2), "chain3": lambda: _distinct_chain(rng, k, 3),
              "chain_repeat2": lambda: _repeat_chain(rng, k, 2), "chain_repeat3": lambda: _repeat_chain(rng, k, 3),
              "chain4": lambda: _repeat_chain(rng, k, 4)}
    for stage, items in stages:
        items = list(items)
        rng.shuffle(items)
        for chain, family in items:
            task = _task(cfg, rng, perm, library, chain, stage, family, index)
            while task is None:
                task = _task(cfg, rng, perm, library, redraw[family](), stage, family, index)
            tasks.append(task)
            index += 1
    assert len(tasks) == cfg["lifetime"]["tasks_per_lifetime"]
    return {"namespace": namespace, "seed": seed, "perm": perm, "library": library, "tasks": tasks}


def generator_fingerprint(cfg: dict) -> str:
    """Hash of a reference stream: any change to the generator or world changes it."""
    s = make_stream(cfg, "gate", 0)
    payload = json.dumps({"perm": s["perm"], "library": s["library"],
                          "tasks": [[t.start, t.target, t.composition] for t in s["tasks"]]})
    return hashlib.sha256(payload.encode("ascii")).hexdigest()[:16]
