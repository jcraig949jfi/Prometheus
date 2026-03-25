"""MAP-Elites grid for adversarial task quality-diversity.

The grid is the core data structure of Nemesis. Each cell represents a
region of the (logical_complexity × linguistic_obfuscation) space. The
occupant of each cell is the adversarial task that maximizes tool
disagreement for that difficulty region.

This ensures the adversarial set covers the ENTIRE behavioral boundary
of the tool library, not just a few hard clusters.
"""

import json
import logging
import zlib
from pathlib import Path

import numpy as np

log = logging.getLogger("nemesis.grid")

GRID_SIZE = 10  # 10x10 = 100 cells


class AdversarialTask:
    """A single adversarial task with metadata."""

    __slots__ = (
        "prompt", "candidates", "correct", "category",
        "mr_chain", "complexity", "obfuscation",
        "disagreement", "tools_broken", "blind_spot",
        "parent_id", "lineage_depth", "source_trap",
        "tool_results",
    )

    def __init__(self, prompt: str, candidates: list[str], correct: str,
                 category: str = "", mr_chain: list[str] | None = None,
                 complexity: int = 1, obfuscation: int = 1,
                 source_trap: str = ""):
        self.prompt = prompt
        self.candidates = candidates
        self.correct = correct
        self.category = category
        self.mr_chain = mr_chain or []
        self.complexity = max(1, min(GRID_SIZE, complexity))
        self.obfuscation = max(1, min(GRID_SIZE, obfuscation))
        self.disagreement = 0.0
        self.tools_broken = 0
        self.blind_spot = False
        self.parent_id = ""
        self.lineage_depth = 0
        self.source_trap = source_trap
        self.tool_results = {}

    @property
    def cell(self) -> tuple[int, int]:
        """Grid cell (row=complexity, col=obfuscation), 0-indexed."""
        return (self.complexity - 1, self.obfuscation - 1)

    @property
    def fitness(self) -> float:
        """Fitness for MAP-Elites placement. Higher = better adversarial task."""
        # Primary: tool disagreement (how many tools give different answers)
        # Secondary: lineage depth (multi-generation breaks are more valuable)
        # Tertiary: blind spot bonus (all tools wrong = very valuable)
        score = self.disagreement * 10.0
        score += self.lineage_depth * 2.0
        if self.blind_spot:
            score += 50.0
        return score

    def to_dict(self) -> dict:
        return {
            "prompt": self.prompt,
            "candidates": self.candidates,
            "correct": self.correct,
            "category": self.category,
            "mr_chain": self.mr_chain,
            "complexity": self.complexity,
            "obfuscation": self.obfuscation,
            "disagreement": self.disagreement,
            "tools_broken": self.tools_broken,
            "blind_spot": self.blind_spot,
            "parent_id": self.parent_id,
            "lineage_depth": self.lineage_depth,
            "source_trap": self.source_trap,
            "tool_results": self.tool_results,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AdversarialTask":
        t = cls(
            prompt=d["prompt"],
            candidates=d["candidates"],
            correct=d["correct"],
            category=d.get("category", ""),
            mr_chain=d.get("mr_chain", []),
            complexity=d.get("complexity", 1),
            obfuscation=d.get("obfuscation", 1),
            source_trap=d.get("source_trap", ""),
        )
        t.disagreement = d.get("disagreement", 0)
        t.tools_broken = d.get("tools_broken", 0)
        t.blind_spot = d.get("blind_spot", False)
        t.parent_id = d.get("parent_id", "")
        t.lineage_depth = d.get("lineage_depth", 0)
        t.tool_results = d.get("tool_results", {})
        return t


class MAPElitesGrid:
    """10x10 quality-diversity grid for adversarial tasks.

    Axes:
        Row (Y): Logical complexity (1-10)
        Col (X): Linguistic obfuscation (1-10)

    Each cell holds at most one task — the one with highest fitness
    (tool disagreement + lineage depth + blind spot bonus) for that
    region of difficulty space.
    """

    def __init__(self):
        self._grid: list[list[AdversarialTask | None]] = [
            [None] * GRID_SIZE for _ in range(GRID_SIZE)
        ]
        self._generation = 0

    @property
    def n_filled(self) -> int:
        return sum(
            1 for row in self._grid for cell in row if cell is not None
        )

    @property
    def n_empty(self) -> int:
        return GRID_SIZE * GRID_SIZE - self.n_filled

    @property
    def tasks(self) -> list[AdversarialTask]:
        """All tasks currently in the grid."""
        return [cell for row in self._grid for cell in row if cell is not None]

    def get(self, row: int, col: int) -> AdversarialTask | None:
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            return self._grid[row][col]
        return None

    def place(self, task: AdversarialTask) -> bool:
        """Try to place a task in the grid.

        Returns True if the task was placed (new cell or beat incumbent).
        """
        row, col = task.cell
        current = self._grid[row][col]

        if current is None:
            self._grid[row][col] = task
            log.debug("Placed new task at (%d,%d): disagreement=%.2f",
                      row, col, task.disagreement)
            return True

        if task.fitness > current.fitness:
            log.debug("Replaced task at (%d,%d): %.2f > %.2f",
                      row, col, task.fitness, current.fitness)
            self._grid[row][col] = task
            return True

        return False

    def empty_cells(self) -> list[tuple[int, int]]:
        """Return list of (row, col) pairs for empty cells."""
        return [
            (r, c)
            for r in range(GRID_SIZE)
            for c in range(GRID_SIZE)
            if self._grid[r][c] is None
        ]

    def density_map(self) -> np.ndarray:
        """Return GRID_SIZE x GRID_SIZE array: 1 where filled, 0 where empty."""
        m = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self._grid[r][c] is not None:
                    m[r, c] = 1.0
        return m

    def disagreement_map(self) -> np.ndarray:
        """Return GRID_SIZE x GRID_SIZE array of disagreement scores."""
        m = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self._grid[r][c] is not None:
                    m[r, c] = self._grid[r][c].disagreement
        return m

    def blind_spots(self) -> list[AdversarialTask]:
        """Return all tasks that are blind spots (all tools wrong)."""
        return [t for t in self.tasks if t.blind_spot]

    def weakest_cells(self, n: int = 10) -> list[tuple[int, int]]:
        """Return n filled cells with lowest fitness (replacement candidates)."""
        filled = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self._grid[r][c] is not None:
                    filled.append((self._grid[r][c].fitness, r, c))
        filled.sort()
        return [(r, c) for _, r, c in filled[:n]]

    def novelty_check(self, task: AdversarialTask,
                      threshold: float = 0.15) -> bool:
        """Check if a task is sufficiently novel (NCD distance from all existing tasks).

        Returns True if the task is novel enough to be placed.
        Uses NCD (compression distance) to avoid neural dependencies.
        """
        prompt_bytes = task.prompt.encode("utf-8")
        c_new = len(zlib.compress(prompt_bytes))

        for existing in self.tasks:
            ex_bytes = existing.prompt.encode("utf-8")
            c_ex = len(zlib.compress(ex_bytes))
            c_both = len(zlib.compress(prompt_bytes + b" " + ex_bytes))
            ncd = (c_both - min(c_new, c_ex)) / max(c_new, c_ex, 1)
            if ncd < threshold:
                return False  # too similar to an existing task

        return True

    def save(self, path: Path):
        """Serialize grid to JSON."""
        data = {
            "grid_size": GRID_SIZE,
            "generation": self._generation,
            "n_filled": self.n_filled,
            "cells": [],
        }
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                cell = self._grid[r][c]
                if cell is not None:
                    data["cells"].append({
                        "row": r, "col": c,
                        "task": cell.to_dict(),
                    })
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        log.info("Grid saved: %d/%d cells filled", self.n_filled, GRID_SIZE**2)

    def load(self, path: Path):
        """Load grid from JSON."""
        data = json.loads(path.read_text(encoding="utf-8"))
        self._generation = data.get("generation", 0)
        for cell_data in data.get("cells", []):
            r, c = cell_data["row"], cell_data["col"]
            task = AdversarialTask.from_dict(cell_data["task"])
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                self._grid[r][c] = task
        log.info("Grid loaded: %d/%d cells filled", self.n_filled, GRID_SIZE**2)

    def export_adversarial_set(self) -> list[dict]:
        """Export all grid tasks as trap-battery-compatible dicts."""
        return [
            {
                "prompt": t.prompt,
                "candidates": t.candidates,
                "correct": t.correct,
            }
            for t in self.tasks
        ]

    def summary(self) -> str:
        """Human-readable grid summary."""
        lines = [
            f"MAP-Elites Grid: {self.n_filled}/{GRID_SIZE**2} cells filled "
            f"({self.n_empty} empty)",
            f"Generation: {self._generation}",
            f"Blind spots: {len(self.blind_spots())}",
            "",
            "Density (filled=X, empty=.):",
        ]
        for r in range(GRID_SIZE):
            row_str = ""
            for c in range(GRID_SIZE):
                cell = self._grid[r][c]
                if cell is None:
                    row_str += ". "
                elif cell.blind_spot:
                    row_str += "B "
                else:
                    row_str += "X "
            lines.append(f"  {r+1:2d} |{row_str}|")

        lines.append(f"     {''.join(f'{c+1:2d}' for c in range(GRID_SIZE))}")
        lines.append(f"      {'Linguistic Obfuscation →':>20s}")
        return "\n".join(lines)
