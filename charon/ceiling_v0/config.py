"""Shared run configuration. RESTORED 2026-08-22.

Structural change made during restoration and flagged as such: `ArmConfig`
previously lived in `arms.py`, which forced `baselines.py` to import the whole
LLM-arm module just to read a budget. It now lives here, so the deterministic
half of the experiment no longer depends on the model half at import time. That
is why the deterministic suite can be restored and verified before any of the
model-facing code exists.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ArmConfig:
    budget_per_round: int = 100
    turns: int = 4
    runs_per_turn_p01: int = 25
    runs_per_turn_p2: int = 12
    claims_per_turn: int = 3
    rule_contexts: int = 3
    eval_chunk: int = 20
