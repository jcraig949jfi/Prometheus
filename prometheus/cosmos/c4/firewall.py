"""DISCOVERY / CONFIRMATION firewall for C4 law search (R-STAT A5).

Rules enforced in code:
1. World sets are disjoint by construction: each split draws its world seeds from its own namespace
   (DISCOVERY, CONFIRMATION, EXTERNAL), so no world can be in two splits.
2. Law search, coordinate selection and complexity choice see DISCOVERY only.
3. CONFIRMATION labels never leave the vault. The vault scores a predictor and returns only the verdict
   statistics.
4. A candidate is scored only if it was FROZEN first: its spec hash is appended to the freeze log before
   the vault is opened, and the vault refuses an unfrozen spec.
5. A confirmation batch is SPENT by its first scoring, pass or fail. A revised law gets a new id and needs
   a fresh batch. Every scoring, including failures, is appended to the ledger, so the number of
   candidates that touched confirmation is always visible.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable, Dict, Optional

import numpy as np

from prometheus.cosmos.hashing import h

SPLITS = ("DISCOVERY", "CONFIRMATION", "EXTERNAL")


def split_seed(split: str, batch: int, i: int) -> int:
    """World seed for world i of a batch of a split. Distinct namespaces => disjoint world sets."""
    if split not in SPLITS:
        raise ValueError(split)
    return int(h(["C4-WORLD", split, int(batch), int(i)])[:15], 16)


class FirewallError(RuntimeError):
    pass


class Vault:
    """Holds CONFIRMATION labels for numbered batches in a directory; scores frozen candidates once per batch."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.freeze_log = self.root / "FREEZE_LOG.jsonl"
        self.ledger = self.root / "SCORE_LEDGER.jsonl"

    # -- batches ------------------------------------------------------------------------------------
    def deposit(self, batch: int, world_ids, labels, meta: Optional[dict] = None) -> str:
        p = self.root / f"batch_{batch:03d}.json"
        if p.exists():
            raise FirewallError(f"batch {batch} already deposited")
        rec = {"batch": batch, "world_ids": list(map(str, world_ids)), "labels": list(map(int, labels)),
               "meta": meta or {}}
        p.write_text(json.dumps(rec))
        return h(rec)

    def _batch(self, batch: int) -> dict:
        p = self.root / f"batch_{batch:03d}.json"
        if not p.exists():
            raise FirewallError(f"no batch {batch}")
        return json.loads(p.read_text())

    def spent(self, batch: int) -> bool:
        return any(r["batch"] == batch for r in self._read(self.ledger))

    # -- freezing -----------------------------------------------------------------------------------
    def freeze(self, candidate_id: str, spec: dict) -> str:
        if any(r["candidate_id"] == candidate_id for r in self._read(self.freeze_log)):
            raise FirewallError(f"{candidate_id} already frozen; a revision needs a new id")
        sh = h(spec)
        self._append(self.freeze_log, {"candidate_id": candidate_id, "spec_sha256": sh,
                                       "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        return sh

    # -- scoring ------------------------------------------------------------------------------------
    def score(self, candidate_id: str, spec: dict, batch: int,
              predict: Callable[[list], np.ndarray], verdict: Callable[[np.ndarray, np.ndarray], Dict]) -> Dict:
        fr = [r for r in self._read(self.freeze_log) if r["candidate_id"] == candidate_id]
        if not fr:
            raise FirewallError(f"{candidate_id} is not frozen")
        if fr[0]["spec_sha256"] != h(spec):
            raise FirewallError(f"{candidate_id} spec differs from its freeze")
        if self.spent(batch):
            raise FirewallError(f"confirmation batch {batch} is spent")
        b = self._batch(batch)
        pred = np.asarray(predict(b["world_ids"]))
        out = verdict(np.asarray(b["labels"]), pred)
        safe = {k: v for k, v in out.items() if k not in ("labels", "y")}
        self._append(self.ledger, {"candidate_id": candidate_id, "spec_sha256": fr[0]["spec_sha256"],
                                   "batch": batch, "result": safe,
                                   "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        return safe

    def n_scored(self) -> int:
        return len(self._read(self.ledger))

    # -- io -----------------------------------------------------------------------------------------
    @staticmethod
    def _read(p: Path):
        if not p.exists():
            return []
        return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]

    @staticmethod
    def _append(p: Path, rec: dict):
        with open(p, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
