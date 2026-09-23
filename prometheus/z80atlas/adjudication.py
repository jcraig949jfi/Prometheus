"""v2 detectors (added 2026-09-23 by the post-campaign forensics; roles/Bellerophon/forensics_2026-09-23/).

The frozen v1 triggers in observatory.py stay byte-for-byte (their hash is part of the historical campaign); they are
NOT fit for adjudication (ISSUE_AND_REPAIR_LEDGER.md). These predicates read only the repaired summary fields:
  task_reached       a verified exact solver of the CONFIGURED task is alive at the end, and the world is not extinct
  self_replication   >= 1 SELF_REPLICATION birth (own bytes, own code, pre- and post-execution fidelity >= 0.9)
  sustained          a SELF_REPLICATION chain of depth >= min_depth
  spontaneous        self_replication from a fresh start: init RANDOM, no init_tapes, first self-replicator unseeded
They are predicates on ONE run. Comparisons between arms are made by the preregistered analysis (GROUNDING_PREREG.md)
with a declared experimental unit, never by any() over unequal run sets."""
from __future__ import annotations

from typing import Dict, Optional

from prometheus.z80atlas.tasks import Task, verify_tape as _verify
from prometheus.z80atlas.world import Config


def task_reached(s: Dict) -> bool:
    return (not s.get("extinct")) and (s.get("verified") or {}).get("exact_solvers_final", 0) >= 1


def self_replication(s: Dict) -> bool:
    return (s.get("self_rep_births") or 0) > 0


def sustained(s: Dict, min_depth: int = 3) -> bool:
    return (s.get("sr_max_depth") or 0) >= min_depth


def spontaneous(s: Dict, vec: Dict[str, str], has_init_tapes: bool) -> bool:
    fsr = s.get("first_self_replication") or {}
    return vec.get("init") == "RANDOM" and not has_init_tapes and bool(fsr) and not fsr.get("seeded")


def verify_tape(tape: bytes, cfg: Config, task: Optional[Task] = None) -> Dict:
    task = task or Task(cfg.task)
    return _verify(tape, cfg.L, task, cfg.read_gate, cfg.budget, cfg.layout, cfg.allow_copyall)
