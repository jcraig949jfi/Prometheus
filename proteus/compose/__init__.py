"""Structural composition over frozen Proteus specimens.

Deliberately OUTSIDE `proteus/foundry`: nothing here changes how a player executes, so the
runtime identity (`identity.RUNTIME_SOURCE_FILES` = affordances.py + vm.py) and the V0.6 audit
tree digest are both untouched by this package's existence. A composition is a CONSTRUCTOR that
emits an ordinary manifest which the frozen runtime interprets exactly as it interprets any other.
"""
from .segments import (SEGMENT_SCHEMA, COMPOSITION_SCHEMA, Segment, segment_from_instructions,
                       segment_id, composition_id, compose, ablate, ablation_report,
                       activation_evidence, decompose, NOP_ALIASES)

__all__ = ["SEGMENT_SCHEMA", "COMPOSITION_SCHEMA", "Segment", "segment_from_instructions",
           "segment_id", "composition_id", "compose", "ablate", "ablation_report",
           "activation_evidence", "decompose", "NOP_ALIASES"]
