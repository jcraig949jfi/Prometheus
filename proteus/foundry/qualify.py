"""Foundry-local qualification: can this candidate exist as a player at all? Cheap death, recorded.

This is NOT selection and NOT a world. The only questions asked are mechanical: is the manifest
within the published bounds, was it generated under this runtime, and does it execute the frozen
probe ensemble without the runtime raising. An organism that emits nothing, halts at once, or
spins its whole budget PASSES qualification -- those are phenotypes, and judging them is the
neutral operator's job in a world. Deaths are appended to a hash-chained ledger with their cost.
"""
from __future__ import annotations

import time

from .identity import RUNTIME_HASH, hash_obj
from .probes import run_ensemble
from .vm import ManifestError, validate_manifest


class FailureLedger:
    """Append-only, hash-chained. Rows are never edited; interpretation lives elsewhere."""

    def __init__(self):
        self.rows = []

    def append(self, organism_index: int, organism_id: str | None, failure_class: str,
               detail: str, cost: dict) -> dict:
        prev = self.rows[-1]["row_hash"] if self.rows else "0" * 64
        row = {"seq": len(self.rows), "organism_index": organism_index, "organism_id": organism_id,
               "failure_class": failure_class, "detail": detail, "cost": cost,
               "runtime_hash": RUNTIME_HASH, "prev_hash": prev}
        row["row_hash"] = hash_obj(row)
        self.rows.append(row)
        return row


def qualify(population: list, probes: list, cfg: dict, ledger: FailureLedger) -> list:
    alive = []
    for i, o in enumerate(population):
        t0 = time.perf_counter()
        oid = o.get("organism_id")
        if o.get("runtime_hash") != RUNTIME_HASH:
            ledger.append(i, oid, "RUNTIME_MISMATCH", "organism stamped with a different runtime",
                          {"wall_s": time.perf_counter() - t0, "ops": 0})
            continue
        try:
            validate_manifest(o["manifest"])
        except ManifestError as e:
            ledger.append(i, oid, "MANIFEST_INVALID", str(e), {"wall_s": time.perf_counter() - t0, "ops": 0})
            continue
        try:
            run_ensemble(o["manifest"], probes, cfg)
        except Exception as e:  # the runtime must be total; if it is not, that is a runtime defect
            ledger.append(i, oid, "RUNTIME_RAISED", repr(e), {"wall_s": time.perf_counter() - t0, "ops": None})
            continue
        alive.append(o)
    return alive
