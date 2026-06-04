"""A single crawler (a "spider"): a frontier walk over one landscape (or, for
the feral ruleset, over many), emitting typed+provenanced+null-scored edges.

Fitness is multifactor (James's three): don't die, expand connectivity, and
branch near death. This module owns one crawler's life; the population/
evolution logic lives in swarm.py.
"""
from __future__ import annotations

import hashlib
import random
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from agents.arachne.fabric import Fabric, Edge


@dataclass
class Ruleset:
    """The few knobs a crawler has. Editorial freedom is maximal; these govern
    HOW it walks, never WHAT may connect."""
    landscape: str                 # adapter name, or "feral" (hops landscapes)
    max_neighbors: int = 8         # degree budget per expand
    novelty_floor: float = 0.92    # drop edges with null_p above this (too generic)
    hop: bool = False              # feral: pick a random landscape each step
    frontier_mode: str = "bfs"     # "bfs" | "dfs" | "random"
    reseed_every: int = 40         # inject fresh seeds every N steps (anti-starve)
    seed: int = 0

    def mutate(self, rng: random.Random) -> "Ruleset":
        """Produce a child ruleset — the mutation operators that make the
        tree-of-life evolutionary rather than a stamp collection."""
        child = Ruleset(**{**self.__dict__})
        child.seed = rng.randint(1, 10_000_000)
        knob = rng.choice(
            ["max_neighbors", "novelty_floor", "frontier_mode", "hop", "reseed"]
        )
        if knob == "max_neighbors":
            child.max_neighbors = max(2, min(32, self.max_neighbors + rng.choice([-4, -2, 4, 8])))
        elif knob == "novelty_floor":
            # lower floor => accept MORE edges (escape starvation); raise => pickier
            child.novelty_floor = float(min(0.99, max(0.50, self.novelty_floor + rng.choice([-0.15, -0.08, 0.05]))))
        elif knob == "frontier_mode":
            child.frontier_mode = rng.choice(["bfs", "dfs", "random"])
        elif knob == "hop":
            child.hop = not self.hop
        elif knob == "reseed":
            child.reseed_every = max(10, min(120, self.reseed_every + rng.choice([-20, -10, 20])))
        return child


class Crawler:
    DEATH_STALL = 12       # consecutive 0-progress steps => dead (dead-end / loop)
    DEATH_ERRORS = 8       # consecutive errors => dead
    WINDOW = 16            # fitness sliding window

    def __init__(self, cid: str, ruleset: Ruleset, parent: Optional[str] = None,
                 generation: int = 0):
        self.id = cid
        self.ruleset = ruleset
        self.parent = parent
        self.generation = generation
        self.rng = random.Random(ruleset.seed or hash(cid) & 0xffffffff)
        self.frontier: deque[str] = deque()
        self.visited: set[str] = set()
        self.alive = True
        self.death_reason: Optional[str] = None
        self.stall_streak = 0
        self.error_streak = 0
        self.steps = 0
        self.total_edges = 0
        self._progress = deque(maxlen=self.WINDOW)   # (new_edges+new_nodes) per step
        self._nullsum = deque(maxlen=self.WINDOW)    # mean null_p per step
        self._frontier_hashes: deque[str] = deque(maxlen=6)
        self.born_landscape = ruleset.landscape

    # -- fitness --------------------------------------------------------------
    def fitness(self) -> float:
        if not self._progress:
            return 1.0
        prog = sum(self._progress) / len(self._progress)
        nullp = (sum(self._nullsum) / len(self._nullsum)) if self._nullsum else 0.5
        # connectivity expansion discounted by how generic the edges were
        return prog * (1.0 - 0.6 * nullp)

    def _frontier_hash(self) -> str:
        head = list(self.frontier)[:12]
        return hashlib.sha1("|".join(head).encode()).hexdigest()[:10]

    # -- one step -------------------------------------------------------------
    def step(self, fabric: Fabric, landscapes: dict) -> dict:
        """Expand one node. landscapes: name -> adapter instance."""
        self.steps += 1
        now = datetime.now(timezone.utc).isoformat()

        # choose landscape (feral hops)
        if self.ruleset.hop and landscapes:
            ls_name = self.rng.choice(list(landscapes.keys()))
        else:
            ls_name = self.ruleset.landscape
        adapter = landscapes.get(ls_name)
        if adapter is None:
            self.error_streak += 1
            self._after(0, 0, 0.5)
            return {"action": "no_adapter", "landscape": ls_name}

        # reseed if frontier empty or on cadence
        if not self.frontier or self.steps % max(1, self.ruleset.reseed_every) == 0:
            try:
                for s in adapter.seeds(self.rng, k=4):
                    if s not in self.visited:
                        self.frontier.append(s)
            except Exception:
                pass

        if not self.frontier:
            self._after(0, 0, 0.5)
            return {"action": "starved_no_frontier", "landscape": ls_name}

        # pick next node per frontier mode
        if self.ruleset.frontier_mode == "dfs":
            node = self.frontier.pop()
        elif self.ruleset.frontier_mode == "random":
            idx = self.rng.randrange(len(self.frontier))
            self.frontier.rotate(-idx)
            node = self.frontier.popleft()
        else:
            node = self.frontier.popleft()
        self.visited.add(node)

        # expand
        try:
            raw = adapter.expand(node, self.rng, self.ruleset) or []
            self.error_streak = 0
        except Exception as e:
            self.error_streak += 1
            self._after(0, 0, 0.5)
            return {"action": "expand_error", "landscape": ls_name,
                    "error": f"{type(e).__name__}: {e}"[:160]}

        # filter by novelty floor (rule 3 as a gate), build edges
        edges, nulls = [], []
        for (dst, op, null_p) in raw[: max(1, self.ruleset.max_neighbors) * 3]:
            if null_p > self.ruleset.novelty_floor:
                continue
            edges.append(Edge(src=node, dst=dst, op=op, landscape=ls_name,
                              crawler=self.id, born_at=now, null_p=float(null_p)))
            nulls.append(float(null_p))
            if len(edges) >= self.ruleset.max_neighbors:
                break

        delta = fabric.add(edges)
        # push novel destinations onto the frontier
        for e in edges:
            if e.dst not in self.visited:
                self.frontier.append(e.dst)

        new_e, new_n = delta["new_edges"], delta["new_nodes"]
        self.total_edges += new_e
        mean_null = (sum(nulls) / len(nulls)) if nulls else 0.5
        self._after(new_e, new_n, mean_null)

        # loop detection: frontier head repeating
        fh = self._frontier_hash()
        looping = fh in self._frontier_hashes and new_e == 0
        self._frontier_hashes.append(fh)

        return {"action": "expanded", "landscape": ls_name, "node": node,
                "new_edges": new_e, "new_nodes": new_n, "candidates": len(raw),
                "looping": looping, "fitness": round(self.fitness(), 3)}

    def _after(self, new_e: int, new_n: int, mean_null: float) -> None:
        self._progress.append(new_e + new_n)
        self._nullsum.append(mean_null)
        if new_e == 0 and new_n == 0:
            self.stall_streak += 1
        else:
            self.stall_streak = 0
        # death checks
        if self.stall_streak >= self.DEATH_STALL:
            self.alive = False
            self.death_reason = "starved_or_looping"
        elif self.error_streak >= self.DEATH_ERRORS:
            self.alive = False
            self.death_reason = "error_streak"

    def snapshot(self) -> dict:
        return {
            "id": self.id, "parent": self.parent, "generation": self.generation,
            "landscape": self.ruleset.landscape, "born_landscape": self.born_landscape,
            "alive": self.alive, "death_reason": self.death_reason,
            "steps": self.steps, "total_edges": self.total_edges,
            "fitness": round(self.fitness(), 3), "stall_streak": self.stall_streak,
            "frontier": len(self.frontier), "visited": len(self.visited),
            "ruleset": {"max_neighbors": self.ruleset.max_neighbors,
                        "novelty_floor": round(self.ruleset.novelty_floor, 3),
                        "hop": self.ruleset.hop,
                        "frontier_mode": self.ruleset.frontier_mode,
                        "reseed_every": self.ruleset.reseed_every},
        }
