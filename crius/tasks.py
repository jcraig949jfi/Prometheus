"""Task generation: TaskSpec, frozen composition partitions, lifetimes per suite.

A TaskSpec carries hidden fields (composition, stage, family) for receipts;
the Player-facing observation exposes only start, target and budgets
(see crius/player.py Observation).
"""

from __future__ import annotations

import hashlib
import itertools
import json
import random
from dataclasses import dataclass, asdict

from . import world

STAGE_ORDER = ("A", "B", "C", "D", "E")


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    start: tuple
    target: tuple
    interaction_budget: int
    step_budget: int
    # hidden from Players; present for receipts and reports
    composition: tuple
    depth: int
    stage: str
    family: str
    world_id: str = "c0"
    perm: tuple = ()

    def public(self) -> dict:
        return {
            "start": self.start,
            "target": self.target,
            "interaction_budget": self.interaction_budget,
            "step_budget": self.step_budget,
        }

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------- partitions


def build_partitions(cfg: dict) -> dict:
    """Deterministic three-way split of compositions over ops {0..4}.

    search_cd: used in stages C/D of search lifetimes.
    search_e:  used in stage E of search lifetimes (transfer within search).
    qual:      never used in any search lifetime.
    Compositions containing op5 and depth-4 compositions are generated only
    in the qualification suite (families absent_op5_*, depth4).
    """
    p = cfg["partitions"]
    rng = random.Random(p["seed"])
    known = list(range(world.NUM_OPS - 1))  # ops 0..4; op5 is the absent family
    pairs = list(itertools.product(known, repeat=2))
    triples = list(itertools.product(known, repeat=3))
    rng.shuffle(pairs)
    rng.shuffle(triples)
    a, b, c = p["pair_split"]
    assert a + b + c == len(pairs), "pair_split must cover %d pairs" % len(pairs)
    pa, pb, pc = pairs[:a], pairs[a : a + b], pairs[a + b :]
    a, b, c = p["triple_split"]
    assert a + b + c == len(triples), "triple_split must cover %d triples" % len(triples)
    ta, tb, tc = triples[:a], triples[a : a + b], triples[a + b :]
    search_pairs = set(pa)
    search_triples = set(ta) | set(tb)
    reversed_pairs = [q for q in pc if (q[1], q[0]) in search_pairs]
    other_qual_pairs = [q for q in pc if q not in reversed_pairs]
    new_combos = [
        t for t in tc if (t[0], t[1]) in search_pairs and (t[1], t[2]) in search_pairs
    ]
    other_qual_triples = [t for t in tc if t not in new_combos]
    return {
        "search_cd_pairs": pa,
        "search_e_pairs": pb,
        "qual_pairs": pc,
        "search_cd_triples": ta,
        "search_e_triples": tb,
        "qual_triples": tc,
        "reversed_pairs": reversed_pairs,
        "heldout_pairs": other_qual_pairs,
        "new_combination_triples": new_combos,
        "heldout_triples": other_qual_triples,
    }


def partitions_fingerprint(parts: dict) -> str:
    payload = json.dumps({k: sorted(v) for k, v in parts.items()}, sort_keys=True)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()[:16]


# ---------------------------------------------------------------- instances


def _random_object(rng: random.Random) -> tuple:
    return tuple(rng.randrange(world.B) for _ in range(world.L))


def make_task(cfg: dict, rng: random.Random, composition, stage: str, family: str, index: int) -> TaskSpec:
    depth = len(composition)
    budget = cfg["budgets"]["interactions_by_depth"][str(depth)]
    steps = cfg["budgets"]["steps_per_task"]
    for _ in range(1000):
        start = _random_object(rng)
        target = world.apply_sequence(composition, start)
        if target != start:
            break
    else:
        raise RuntimeError("could not sample a task with target != start for %r" % (composition,))
    tid = hashlib.sha256(
        json.dumps([start, target, composition, stage, family, index]).encode("ascii")
    ).hexdigest()[:12]
    return TaskSpec(
        task_id=tid,
        start=start,
        target=target,
        interaction_budget=budget,
        step_budget=steps,
        composition=tuple(composition),
        depth=depth,
        stage=stage,
        family=family,
    )


def _pick(rng: random.Random, pool, n: int):
    pool = list(pool)
    if not pool:
        return []
    if n <= len(pool):
        return rng.sample(pool, n)
    out = list(pool)
    rng.shuffle(out)
    while len(out) < n:
        out.append(rng.choice(pool))
    return out


def make_lifetime(cfg: dict, seed: int, suite: str) -> list:
    """The task sequence one Player instance meets. Deterministic in (cfg, seed, suite)."""
    parts = build_partitions(cfg)
    sizes = cfg["lifetime"]["stages"]
    rng = random.Random(("lifetime", suite, seed, cfg["partitions"]["seed"]).__repr__())
    all_ops = list(range(world.NUM_OPS))
    stages = []
    # Stage A: every primitive appears at least once.
    a_comps = [(op,) for op in all_ops]
    while len(a_comps) < sizes["A"]:
        a_comps.append((rng.choice(all_ops),))
    stages.append(("A", [(c, "primitive") for c in a_comps[: sizes["A"]]]))
    stages.append(("B", [((rng.choice(all_ops),), "primitive") for _ in range(sizes["B"])]))
    if suite == "search":
        stages.append(("C", [(c, "search_pair") for c in _pick(rng, parts["search_cd_pairs"], sizes["C"])]))
        stages.append(("D", [(c, "search_triple") for c in _pick(rng, parts["search_cd_triples"], sizes["D"])]))
        ne = sizes["E"]
        e = [(c, "transfer_pair") for c in _pick(rng, parts["search_e_pairs"], ne // 2)]
        e += [(c, "transfer_triple") for c in _pick(rng, parts["search_e_triples"], ne - ne // 2)]
        stages.append(("E", e))
    elif suite == "heldout_v1":
        nc = sizes["C"]
        c = [(q, "reversed_pair") for q in _pick(rng, parts["reversed_pairs"], nc // 2)]
        c += [(q, "heldout_pair") for q in _pick(rng, parts["heldout_pairs"], nc - nc // 2)]
        stages.append(("C", c))
        nd = sizes["D"]
        d = [(t, "heldout_triple") for t in _pick(rng, parts["heldout_triples"], nd // 2)]
        d += [(t, "new_combination") for t in _pick(rng, parts["new_combination_triples"], nd - nd // 2)]
        stages.append(("D", d))
        ne = sizes["E"]
        known = list(range(world.NUM_OPS - 1))
        e = []
        n_d2 = ne // 2
        n_d3 = (ne - n_d2) // 2 + ((ne - n_d2) % 2)
        n_d4 = ne - n_d2 - n_d3
        for _ in range(n_d2):
            other = rng.choice(known)
            comp = (5, other) if rng.random() < 0.5 else (other, 5)
            e.append((comp, "absent_op5_d2"))
        for _ in range(n_d3):
            comp = [rng.choice(known), rng.choice(known)]
            comp.insert(rng.randrange(3), 5)
            e.append((tuple(comp), "absent_op5_d3"))
        for _ in range(n_d4):
            e.append((tuple(rng.choice(known) for _ in range(4)), "depth4"))
        stages.append(("E", e))
    else:
        raise ValueError("unknown suite %r" % suite)
    tasks = []
    index = 0
    for stage, items in stages:
        items = list(items)
        rng.shuffle(items)  # order within a stage varies by seed
        for comp, family in items:
            tasks.append(make_task(cfg, rng, comp, stage, family, index))
            index += 1
    assert len(tasks) == cfg["lifetime"]["tasks_per_lifetime"], (
        "stage sizes must sum to tasks_per_lifetime"
    )
    return tasks


def task_sequence_hash(tasks) -> str:
    payload = json.dumps([[t.start, t.target, t.interaction_budget, t.step_budget] for t in tasks])
    return hashlib.sha256(payload.encode("ascii")).hexdigest()[:16]


def stage_first_indices(tasks) -> dict:
    out = {}
    for i, t in enumerate(tasks):
        out.setdefault(t.stage, i)
    return out
