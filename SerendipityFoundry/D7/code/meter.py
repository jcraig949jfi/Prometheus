"""
Metering (D7 section 48).  Separate lanes; oracle/proof lane is never learner-visible.
"""

from __future__ import annotations
from dataclasses import dataclass, field


LANES = [
    "history_construction",
    "relational_indexing",
    "synthesis_proposal",
    "transform_execution",
    "exact_verification",
    "graph_analysis",
    "artifact_retrieval",
    "compression_lookup",
    "recombination",
    "confirmation",
    "ORACLE_proof",          # separate lane; not part of learner budget
]


@dataclass
class Meter:
    counts: dict = field(default_factory=lambda: {k: 0 for k in LANES})

    def tick(self, lane, n=1):
        self.counts[lane] += n

    def learner_total(self):
        return sum(v for k, v in self.counts.items() if k != "ORACLE_proof")

    def snapshot(self):
        return dict(self.counts)

    def reset(self):
        for k in self.counts:
            self.counts[k] = 0
