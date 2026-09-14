"""A6 -- attest what the ledger cannot record.

The ledger is written through SQLite's write lock. When that lock is what
failed, nothing can be written to the ledger about the failure: the hash chain
is silent exactly when the engine is the thing that broke (2026-09-11, thirteen
rows of cs-h5-1, roles/Daedalus/DESIGN_A6_ATTESTATION_2026-09-11.md). So the
record has to live somewhere the lock cannot block.

This module is that somewhere: an APPEND-ONLY INTENT JOURNAL, plain files
outside SQLite, written at three points --

    intent(...)     BEFORE the ledger lock is touched, for every mutating request
    effected(...)   after the effect, i.e. after the ledger's own COMMIT returned
    refused(...)    on a refusal (a lock timeout, a 5xx, an exception)

-- and a reconciler that turns a request id into exactly one of four verdicts:

    CONFIRMED_EFFECT        intent + effected line          took_effect True
    CONFIRMED_NO_EFFECT     intent + refused line           took_effect False
    UNKNOWN_RECONCILABLE    intent, no outcome line, and the ledger CAN settle it
    UNKNOWN_UNRECONCILABLE  intent, no outcome line, and the ledger cannot

The epistemic rule (operator, 2026-09-12): AN UNKNOWN OUTCOME STAYS UNKNOWN
UNTIL INDEPENDENTLY RECONCILED. The request path itself can only ever produce
`intent`, `effected` (written strictly after the ledger COMMIT returned, so it
is the ledger's answer relayed, never a guess) and `refused`. A journal that
holds `intent` alone yields UNKNOWN, never a CONFIRMED verdict and never
"failed"; the caller's own error (a timeout) is not evidence either way -- rule
146 committed and its caller saw a timeout. CONFIRMED is reached from UNKNOWN
only by `attest(rid, ledger_has_effect=True|False)`, whose argument comes from
a separate reader of the ledger (deploy/reconcile_attestations.py joins the
journal to the ledger by idempotency key), never from this module's own
inference.

Fails OPEN: if the journal directory cannot be written, requests are still
served and `degraded` is True. An attestation mechanism that can take the
engine down would have made availability worse in exchange for evidence.

No route, no schema change, no dependency. Files: one JSON object per line,
rotated daily by name (incidents/YYYY-MM-DD.jsonl), fsync per line is NOT done
-- the journal is written on the same volume as the ledger and its purpose is
to outlive a lock failure, not a power failure; the ledger's own durability is
SQLite's.
"""
from __future__ import annotations

import json
import os
import secrets
import threading
import time
from typing import Any, Dict, Optional

VERDICTS = ("CONFIRMED_EFFECT", "CONFIRMED_NO_EFFECT",
            "UNKNOWN_RECONCILABLE", "UNKNOWN_UNRECONCILABLE")


def _now() -> float:
    return time.time()


class Journal:
    """Append-only intent journal. One instance per process; thread-safe."""

    def __init__(self, directory: str):
        self.directory = str(directory)
        self._lock = threading.Lock()
        self._mem: Dict[str, Dict[str, Any]] = {}     # rid -> {intent, outcome}
        self.degraded = False
        self.degraded_reason: Optional[str] = None
        self.counts = {"intent": 0, "effected": 0, "refused": 0, "write_failures": 0}
        try:
            # ONE level only: the default is <db dir>/incidents, whose parent
            # exists by construction. A missing parent means a misconfigured
            # path, and creating a tree there would be a journal nobody finds
            # (the first test run turned a POSIX path into a tree at the drive root).
            if not os.path.isdir(self.directory):
                os.mkdir(self.directory)
            probe = os.path.join(self.directory, ".writable")
            with open(probe, "a", encoding="ascii"):
                pass
        except OSError as e:                          # fail OPEN
            self.degraded = True
            self.degraded_reason = "%s: %s" % (type(e).__name__, e)

    # -- writing ----------------------------------------------------------
    def _path(self) -> str:
        return os.path.join(self.directory,
                            time.strftime("%Y-%m-%d", time.gmtime()) + ".jsonl")

    def _append(self, rec: Dict[str, Any]) -> None:
        line = json.dumps(rec, sort_keys=True, separators=(",", ":"))
        with self._lock:
            rid = rec["rid"]
            slot = self._mem.setdefault(rid, {})
            if rec["kind"] == "intent":
                slot["intent"] = rec
            else:
                slot["outcome"] = rec
            self.counts[rec["kind"]] = self.counts.get(rec["kind"], 0) + 1
            if self.degraded:
                return
            try:
                with open(self._path(), "a", encoding="ascii") as fh:
                    fh.write(line + "\n")
            except OSError as e:
                self.degraded = True
                self.degraded_reason = "%s: %s" % (type(e).__name__, e)
                self.counts["write_failures"] += 1

    def intent(self, *, route: str, client: Optional[str] = None,
               idem_key: Optional[str] = None, rid: Optional[str] = None) -> str:
        rid = rid or ("req_" + secrets.token_hex(12))
        self._append({"kind": "intent", "rid": rid, "ts": _now(), "route": route,
                      "client": client, "idem_key": idem_key})
        return rid

    def effected(self, rid: str, *, kind: str, ref: Optional[str] = None) -> None:
        """Only after the ledger's COMMIT returned. Relays, never infers."""
        self._append({"kind": "effected", "rid": rid, "ts": _now(),
                      "effect_kind": kind, "ref": ref})

    def refused(self, rid: str, *, reason: str) -> None:
        self._append({"kind": "refused", "rid": rid, "ts": _now(), "reason": reason})

    # -- reading ----------------------------------------------------------
    def lookup(self, rid: str) -> Dict[str, Any]:
        with self._lock:
            slot = self._mem.get(rid)
        if slot is not None:
            return dict(slot)
        return self._scan(rid)

    def _scan(self, rid: str) -> Dict[str, Any]:
        """Cold path: read the files (another process wrote them, or we
        restarted). Newest file first."""
        found: Dict[str, Any] = {}
        try:
            names = sorted(n for n in os.listdir(self.directory) if n.endswith(".jsonl"))
        except OSError:
            return found
        for n in reversed(names):
            try:
                with open(os.path.join(self.directory, n), encoding="ascii") as fh:
                    for line in fh:
                        try:
                            rec = json.loads(line)
                        except ValueError:
                            continue
                        if rec.get("rid") != rid:
                            continue
                        if rec.get("kind") == "intent":
                            found["intent"] = rec
                        else:
                            found["outcome"] = rec
            except OSError:
                continue
            if found:
                break
        return found

    def open_intents(self, *, older_than_s: float = 0.0) -> list:
        """Intents with no outcome line, in memory (this process's lifetime)."""
        cutoff = _now() - older_than_s
        with self._lock:
            return [dict(s["intent"]) for s in self._mem.values()
                    if "intent" in s and "outcome" not in s and s["intent"]["ts"] <= cutoff]

    def attest(self, rid: str, *, ledger_has_effect: Optional[bool] = None) -> Dict[str, Any]:
        """The verdict for one request id.

        ledger_has_effect is the INDEPENDENT reconciliation: True/False from a
        reader that looked the effect up in the ledger by the intent's
        idempotency key or ref; None when nobody has looked yet or the intent
        carries nothing a reader could look up.
        """
        slot = self.lookup(rid)
        intent = slot.get("intent")
        outcome = slot.get("outcome")
        base = {"rid": rid, "reached_engine": intent is not None,
                "route": intent.get("route") if intent else None,
                "idem_key": intent.get("idem_key") if intent else None,
                "intent_ts": intent.get("ts") if intent else None}
        if intent is None:
            return dict(base, state="UNKNOWN_UNRECONCILABLE", took_effect=None,
                        why="no intent record: the request never reached the journal")
        if outcome is not None and outcome["kind"] == "effected":
            return dict(base, state="CONFIRMED_EFFECT", took_effect=True,
                        ref=outcome.get("ref"), effect_kind=outcome.get("effect_kind"),
                        why="effected line written after the ledger COMMIT returned")
        if outcome is not None and outcome["kind"] == "refused":
            if ledger_has_effect is True:
                # the ledger contradicts the refusal: the ledger wins, and the
                # contradiction is reported rather than hidden
                return dict(base, state="CONFIRMED_EFFECT", took_effect=True,
                            why="ledger shows the effect despite a refused line; ledger wins",
                            contradiction=True, refused_reason=outcome.get("reason"))
            return dict(base, state="CONFIRMED_NO_EFFECT", took_effect=False,
                        refused_reason=outcome.get("reason"),
                        why="refused line; a refusal writes nothing to the ledger")
        # intent only: the outcome is UNKNOWN until the ledger is consulted
        if ledger_has_effect is True:
            return dict(base, state="CONFIRMED_EFFECT", took_effect=True,
                        why="reconciled: the ledger holds the effect")
        if ledger_has_effect is False:
            return dict(base, state="CONFIRMED_NO_EFFECT", took_effect=False,
                        why="reconciled: the ledger holds no effect for this intent")
        reconcilable = bool(intent.get("idem_key"))
        return dict(base,
                    state="UNKNOWN_RECONCILABLE" if reconcilable else "UNKNOWN_UNRECONCILABLE",
                    took_effect=None,
                    why=("no outcome line; reconcile against the ledger by idempotency key"
                         if reconcilable else
                         "no outcome line and no idempotency key: nothing to look up"))


def route_is_mutating(method: str) -> bool:
    return method.upper() in ("POST", "PUT", "PATCH", "DELETE")
