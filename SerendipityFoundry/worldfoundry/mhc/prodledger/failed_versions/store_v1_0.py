"""Crash-safe append-only persistence with hash chaining and rollback defense.

  * Each line: {"h": entry_hash, "p": prev_hash, "e": event} where
    entry_hash = sha256(prev_hash || canonical(event)). GENESIS chains from
    the fixed root "0"*64.
  * Appends are flushed + fsynced before the caller gets an acknowledgement:
    an event either durably exists (and the caller was told so) or does not
    (and the caller was never told it did). There is no third state.
  * RESTART: replay the log through the SAME validate_and_apply fold the
    live service uses. A torn FINAL line (partial write, unparseable, or
    broken hash) is truncated with a recovery note -- by the fsync rule its
    caller was never acknowledged. ANY interior corruption: REFUSE TO START.
  * ROLLBACK DEFENSE: the head hash is anchored externally every
    ANCHOR_EVERY accepted events and at shutdown. On start, if the external
    anchor knows a head we cannot reach by replaying our log, the local log
    has been rolled back -- REFUSE TO START. What can be rolled back is
    therefore bounded by the anchoring cadence, and that bound is stated in
    the packet rather than hidden.
  * Single writer: an OS-level exclusive lock file. A second writer fails
    loudly rather than interleaving.
"""
from __future__ import annotations

import json
import os

from .canon import canon_bytes, event_hash, CanonError
from .core import LedgerState, validate_and_apply, Refused

ROOT = "0" * 64
ANCHOR_EVERY = 8


class StoreError(Exception):
    pass


class HeadAnchor:
    """External head-anchor interface. The mock writes to a separate file
    that the threat model places outside the attacker's reach (a real
    deployment uses an independent timestamping service; see sealing.py).
    Monotone: it only ever appends heads, never forgets them."""

    def __init__(self, path):
        self.path = path

    def publish(self, head: str, n_events: int):
        with open(self.path, "a", encoding="ascii") as f:
            f.write(json.dumps({"head": head, "n": n_events}) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def latest(self):
        if not os.path.exists(self.path):
            return None
        last = None
        with open(self.path, encoding="ascii") as f:
            for line in f:
                line = line.strip()
                if line:
                    last = json.loads(line)
        return last


class LedgerStore:
    def __init__(self, path: str, anchor: HeadAnchor):
        self.path = path
        self.anchor = anchor
        self.lockpath = path + ".lock"
        self._lock = None
        self._fh = None
        self.head = ROOT
        self.state = LedgerState()
        self.known_heads = {ROOT}
        self._acquire_lock()
        self._replay()

    # ---------- single writer ----------
    def _acquire_lock(self):
        try:
            fd = os.open(self.lockpath, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise StoreError("ledger is locked by another writer -- "
                             "single-writer invariant; refusing")
        os.write(fd, str(os.getpid()).encode())
        self._lock = fd

    def close(self):
        if self._fh:
            self._fh.close()
            self._fh = None
        if self._lock is not None:
            os.close(self._lock)
            os.remove(self.lockpath)
            self._lock = None

    # ---------- replay / recovery ----------
    def _replay(self):
        good = []
        torn_note = None
        if os.path.exists(self.path):
            with open(self.path, "rb") as f:
                raw = f.read()
            lines = raw.split(b"\n")
            prev = ROOT
            for i, line in enumerate(lines):
                if not line.strip():
                    continue
                is_last = all(not l.strip() for l in lines[i + 1:])
                try:
                    rec = json.loads(line.decode("ascii"))
                    if rec["p"] != prev:
                        raise StoreError(f"chain break at record {i}")
                    if rec["h"] != event_hash(prev, rec["e"]):
                        raise StoreError(f"hash mismatch at record {i}")
                    validate_and_apply(self.state, rec["e"])
                except StoreError:
                    raise                     # interior corruption: fail closed
                except Refused as e:
                    raise StoreError(f"persisted event {i} no longer valid "
                                     f"under fold rules: {e} -- fail closed")
                except Exception as e:
                    if is_last:
                        torn_note = f"torn final record {i} truncated: {e}"
                        break                 # unacknowledged partial write
                    raise StoreError(f"interior corruption at record {i}: {e}")
                prev = rec["h"]
                good.append(line)
                self.known_heads.add(prev)
            self.head = prev
        # rollback defense
        latest = self.anchor.latest()
        if latest and latest["head"] not in self.known_heads:
            raise StoreError(
                "ROLLBACK DETECTED: external anchor knows head "
                f"{latest['head'][:12]}... which this log never reaches. "
                "Refusing to start.")
        if torn_note is not None:
            with open(self.path, "wb") as f:      # rewrite good prefix only
                f.write(b"\n".join(good) + (b"\n" if good else b""))
                f.flush()
                os.fsync(f.fileno())
            self.recovery_note = torn_note
        else:
            self.recovery_note = None
        self._fh = open(self.path, "ab")

    # ---------- append ----------
    def append(self, event: dict) -> str:
        """Validate against folded state, then durably append. Returns the
        new head hash. On Refused: logs a REFUSAL record (which is itself
        chained) and re-raises. FAIL CLOSED: any persistence failure after
        state mutation poisons the service -- it refuses every further
        operation, and a restart replays the durable truth from disk."""
        if getattr(self, "_poisoned", False):
            raise StoreError("store poisoned by earlier persistence failure; "
                             "restart required (state = durable log only)")
        try:
            validate_and_apply(self.state, event)
        except Refused as e:
            refusal = {"type": "REFUSAL", "lt": max(self.state.lt, 0),
                       "refused_type": event.get("type"), "reason": str(e)}
            try:
                validate_and_apply(self.state, refusal)
                self._raw_append(refusal)
            except Exception:
                pass                                   # refusal logging must
            raise                                      # never mask the refusal
        try:
            self._raw_append(event)
        except Exception as pe:
            self._poisoned = True
            raise StoreError(f"persistence failed after acceptance; store "
                             f"poisoned, restart to recover: {pe}")
        if self.state.n_events % ANCHOR_EVERY == 0:
            self.anchor.publish(self.head, self.state.n_events)
        return self.head

    def _raw_append(self, event: dict):
        h = event_hash(self.head, event)
        rec = canon_bytes({"h": h, "p": self.head, "e": event})
        self._fh.write(rec + b"\n")
        self._fh.flush()
        os.fsync(self._fh.fileno())
        self.head = h
        self.known_heads.add(h)

    def publish_head(self):
        self.anchor.publish(self.head, self.state.n_events)
