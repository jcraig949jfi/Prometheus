"""The substrate contract: the minimum a family must expose to join CWE.

No common microscopic state. A family owns its physics, its mechanisms and its
meters. It exposes:

  name, version, lineage          identity; lineage = the family's own source files
  space()                         native knob lattice {knob: [levels]}
  coords(params, cmap)            DECLARED dimensionless coordinates computed from
                                  the spec alone (never from running the world)
  units(params)                   native exchange metadata {"reward_per_success": R}
  run(params, mech, seed, E)      native observations for one mechanism:
                                  {"reward": float[E], "cost": float[E], ...native meters}
  deform(params)                  single-knob neighbours [(knob, params')]
  coord_preserving(params, rng)   microscopically different params, same declared coords
  sham(params)                    the SHAM twin: the ask no longer depends on the cue

Mechanisms every family must ship (reference players, hand-written, no search):
  SEL   retains only the relevant past observation
  LOG   retains every past observation
  LAST  retains nothing beyond the current observation (memoryless)

The shared functional demand (identical across families; mechanisms differ):
  an observation (the cue, one of V symbols) occurs, disappears, K irrelevant
  observations arrive during a horizon, and at the ask the system is rewarded
  iff it emits the cue.

This module holds signatures only. It carries no physics, so importing it does
not make two families share an evaluator (independence audit: independence.py).
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

MECHANISMS = ("SEL", "LOG", "LAST")
COORD_MAPS = ("v1", "v2")

# Declared coordinate vocabulary (dimensionless). Every family must provide all four.
#   C  maintenance cost of retaining ONE cue for the full horizon / reward per success
#   N  expected native corruption events hitting one retained cue over the horizon
#      v1: raw event count on the physical carrier; v2: effective hazard after any
#      native repair (a family without repair declares v2 == v1)
#   K  number of irrelevant observations during the horizon
#   G  1 - 1/V  (the most a memory can add over a memoryless guess)
COORDS = ("C", "N", "K", "G")


class Family:
    name: str = "?"
    version: str = "0"
    lineage: Tuple[str, ...] = ()

    def space(self) -> Dict[str, List[Any]]:
        raise NotImplementedError

    def coords(self, params: Dict[str, Any], cmap: str = "v1") -> Dict[str, float]:
        raise NotImplementedError

    def units(self, params: Dict[str, Any]) -> Dict[str, float]:
        raise NotImplementedError

    def run(self, params: Dict[str, Any], mech: str, seed: int, episodes: int) -> Dict[str, Any]:
        raise NotImplementedError

    def deform(self, params: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
        sp = self.space()
        out = []
        for k, levels in sp.items():
            if k not in params or params[k] not in levels:
                continue
            i = levels.index(params[k])
            for j in (i - 1, i + 1):
                if 0 <= j < len(levels):
                    q = dict(params)
                    q[k] = levels[j]
                    out.append((k, q))
        return out

    def coord_preserving(self, params: Dict[str, Any], rng) -> List[Dict[str, Any]]:
        return []

    def sham(self, params: Dict[str, Any]) -> Dict[str, Any]:
        q = dict(params)
        q["sham"] = True
        return q
