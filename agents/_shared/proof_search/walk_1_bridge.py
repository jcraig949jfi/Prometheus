"""walk_1 record → ProofSearchEngine adapter.

A walk_1 record contains:
  - theorem_full_name (e.g. "Quiver.Path.toList_injective")
  - file_path (mathlib4 file containing the theorem)
  - decomposition: ordered list of steps, each with the winning tactic AND
    counterfactual siblings (failed alternatives)

This module wires a walk_1 record into a candidate pool the engine can search:
at each step, candidates = [winning tactic] + [sibling tactics]. The engine's
job is to rediscover the closing sequence from that pool.

Requires mathlib4 to be built (Gap 1). Until then, runs as a unit-test against
the record's structure only.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Walk1Record:
    """Parsed walk_1 record. One record = one closed theorem with siblings."""
    problem_id: str
    theorem_full_name: str
    file_path: str
    decomposition: list[dict[str, Any]]
    raw: dict[str, Any]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Walk1Record":
        return cls(
            problem_id=d["problem_id"],
            theorem_full_name=d["theorem_full_name"],
            file_path=d["file_path"],
            decomposition=d.get("decomposition", []),
            raw=d,
        )

    @property
    def winning_tactic_sequence(self) -> list[str]:
        return [step["tactic"] for step in self.decomposition]

    def candidates_at_step(self, step_index: int) -> list[str]:
        """All tactics tried at this step: winning + siblings."""
        if step_index >= len(self.decomposition):
            return []
        step = self.decomposition[step_index]
        winning = step["tactic"]
        siblings = [s["sibling_tactic"] for s in step.get("counterfactual_siblings", [])]
        # Deduplicate while preserving order; winning first
        seen = set()
        ordered = []
        for t in [winning] + siblings:
            if t not in seen:
                seen.add(t)
                ordered.append(t)
        return ordered

    @property
    def total_candidate_pool(self) -> list[str]:
        """Union of all candidates across all steps. The engine searches over
        this pool at every node (the search itself decides which to try when)."""
        seen: set[str] = set()
        pool: list[str] = []
        for i in range(len(self.decomposition)):
            for t in self.candidates_at_step(i):
                if t not in seen:
                    seen.add(t)
                    pool.append(t)
        return pool


def load_records(jsonl_path: str | Path) -> list[Walk1Record]:
    """Load all walk_1 records from a JSONL file."""
    records = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            records.append(Walk1Record.from_dict(d))
    return records


def imports_for_theorem(record: Walk1Record) -> list[str]:
    """Lean import lines needed to restate the theorem in a fresh context.

    Heuristic: the file_path (e.g. "Mathlib/Combinatorics/Quiver/Path.lean")
    maps directly to the import (`import Mathlib.Combinatorics.Quiver.Path`).
    """
    # Strip leading "Mathlib/" path, swap separators to dots, strip ".lean"
    p = record.file_path
    if p.endswith(".lean"):
        p = p[:-5]
    module = p.replace("/", ".").replace("\\", ".")
    return [f"import {module}"]


def make_command_for_state_extraction(record: Walk1Record, step_index: int = 0) -> str:
    """Construct a Lean command that re-states the theorem and emits an initial
    proof state for engine search.

    The decomposition[step_index]["counterfactual_siblings"][0]["sibling_state_before"]
    is the *human-readable* form of the goal at that step. For the FIRST step,
    this gives us the initial proof state of the theorem.

    To re-enter that state cleanly inside lean-repl, we need access to:
      - The original theorem's full_name (so its declared type is available)
      - All hypotheses (which are visible inside the `by` block)

    Strategy: import the file, then re-prove the theorem via `by sorry` to get
    a fresh proof_state aligned with the original. This relies on the theorem
    being declared in the imported file.
    """
    imports = "\n".join(imports_for_theorem(record))
    # Restate as `example : <full theorem name>.type := by sorry`
    # NOTE: lean-repl doesn't directly expose theorem types by name; the cleanest
    # approach is to `#check <name>` and parse, OR import the file and rely on
    # the user to provide the theorem statement separately. For now, emit a
    # template the caller can fill in.
    return f"""{imports}

-- Engine search target: {record.theorem_full_name}
-- Original tactic sequence ({len(record.decomposition)} steps): {record.winning_tactic_sequence}
example : True := by sorry  -- placeholder; replace with actual theorem type
""".strip()
