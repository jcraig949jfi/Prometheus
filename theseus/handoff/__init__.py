"""Theseus handoff — substrate→consumer export pipelines.

Ergon handoff: converts top-N high-training-weight Theseus records into
training_anchor substrate_blocks that Ergon's parse_substrate_blocks.py
+ validate_substrate_blocks.py + ingest_training_anchors.py pipeline
can consume directly.
"""
from theseus.handoff.ergon_handoff import (
    export_for_ergon,
    DEFAULT_WEIGHT_THRESHOLD,
)

__all__ = ["export_for_ergon", "DEFAULT_WEIGHT_THRESHOLD"]
