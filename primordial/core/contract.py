"""The Primordial Machine swarm contract v0 (owner: lane A).

Everything a lane builds plugs into these four shapes so the pieces compose
into one chimera without a meeting. Changing this file is a lane-A commit
announced on the bus (kind=contract); lanes code against the version tag.

HOT-PATH RULE: no str on the hot path. Observations, actions, messages and
symbols are integer arrays or packed bytes. Strings exist only in receipts.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np

CONTRACT_VERSION = "pm-contract-v0"
LANES = ("A", "B", "C", "D", "E",          # conductor + round 2 cohorts
         "F", "G", "H",                    # round 3 builders (fabric, metric, measurement)
         "P", "Q", "W", "T", "U",          # round 6 MVP builders (precision, nsight, warp, tensornet, cudagraph)
         "R")                              # round 5 PREDICTOR (sealed anti-prior ledger; SWARM_R5 O5) -- not P


@runtime_checkable
class World(Protocol):
    """Batched world: n_envs independent episodes stepped in lock-step.

    obs      uint16  [n_envs, n_slots, obs_dim]
    actions  int32   [n_envs, n_slots, act_dim]
    charge   int32   [n_envs, n_slots]   (economy; <= 0 means absorbed)
    done     bool    [n_envs]
    """
    n_envs: int
    n_slots: int
    obs_dim: int
    act_dim: int

    def reset(self, seeds: np.ndarray) -> np.ndarray: ...
    def step(self, actions: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]: ...
    def trace_hashes(self) -> list[bytes]:
        """Per-env digest of the full trajectory; the semantic oracle that lets
        a Python, Lua, GraphBLAS or GPU implementation prove it is the SAME world."""
        ...


@runtime_checkable
class Brain(Protocol):
    """An organism controller. Plasticity lives in adapt(); cost() is what the
    representation ecology charges (params, flops, bytes of state)."""

    def act(self, obs: np.ndarray, msg_in: np.ndarray | None) -> tuple[np.ndarray, np.ndarray | None]: ...
    def adapt(self, signal: np.ndarray) -> None: ...
    def cost(self) -> dict: ...


@runtime_checkable
class Channel(Protocol):
    """Metered channel. send() returns the exact bits charged; the charge is
    settled atomically where the channel lives (e.g. a Lua script)."""

    def send(self, src: int, dst: int, payload: bytes) -> int: ...
    def recv(self, dst: int) -> list[bytes]: ...


@runtime_checkable
class Genome(Protocol):
    def to_bytes(self) -> bytes: ...
    def descriptor(self) -> np.ndarray:
        """QD behaviour/feature descriptor (float32 [k])."""
        ...


# ---------------------------------------------------------------- receipts

STATUSES = ("PASS", "FAIL", "KILL", "NULL", "INDETERMINATE")
REQUIRED = ("lane", "exp_id", "claim", "status", "engineering", "science",
            "controls", "rows", "git")


class ReceiptError(ValueError):
    pass


def validate_receipt(rec: dict) -> dict:
    """A receipt is the unit of competition. Two ledgers stay separate:
    `engineering` (events/s, steps/s, bytes, latency...) and `science`
    (branch points, kills, transfers, consequential symbols...).

    Board eligibility: status PASS or KILL, a cheat control that was RUN
    (controls.cheat is a non-empty result string), and rows committed at a path.
    """
    missing = [k for k in REQUIRED if k not in rec]
    if missing:
        raise ReceiptError(f"receipt missing {missing}")
    if rec["lane"] not in LANES:
        raise ReceiptError(f"unknown lane {rec['lane']!r}")
    if rec["status"] not in STATUSES:
        raise ReceiptError(f"status must be one of {STATUSES}")
    if not isinstance(rec["engineering"], dict) or not isinstance(rec["science"], dict):
        raise ReceiptError("engineering and science must be separate dicts")
    overlap = set(rec["engineering"]) & set(rec["science"])
    if overlap:
        raise ReceiptError(f"metric in both ledgers: {sorted(overlap)}")
    if not str(rec["claim"]).strip():
        raise ReceiptError("claim (written before the run) is empty")
    return rec


def board_eligible(rec: dict) -> bool:
    c = rec.get("controls") or {}
    return (rec.get("status") in ("PASS", "KILL")
            and bool(str(c.get("cheat") or "").strip())
            and bool(str(rec.get("rows") or "").strip()))
