"""
Sigma-substrate kernel — MVP v0.1

Mechanically enforces:
  - Append-only substrate (SQLite UNIQUE on (name, version))
  - Linear capability tokens (frozen Capability + persisted spent_caps)
  - Three-valued GATE (CLEAR / WARN / BLOCK)
  - Falsification-first PROMOTE (verdict required + checked at PROMOTE time)
  - Content-addressed provenance (sha256, integrity-checked on RESOLVE)

Six opcodes: RESOLVE, CLAIM, FALSIFY, GATE, PROMOTE, TRACE.
"""

from __future__ import annotations

import enum
import hashlib
import json
import sqlite3
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Verdict(enum.Enum):
    CLEAR = "CLEAR"
    WARN = "WARN"
    BLOCK = "BLOCK"


class Tier(enum.Enum):
    Conjecture = "Conjecture"
    Possible = "Possible"
    Probable = "Probable"
    WorkingTheory = "WorkingTheory"
    Validated = "Validated"


# ---------------------------------------------------------------------------
# Value types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Symbol:
    name: str
    version: int
    def_hash: str
    def_blob: str
    provenance: list[str]
    tier: Tier

    @property
    def ref(self) -> str:
        return f"{self.name}@v{self.version}"


@dataclass(frozen=True)
class VerdictResult:
    status: Verdict
    rationale: str
    input_hash: str
    seed: int
    runtime_ms: int


@dataclass
class Claim:
    id: str
    target_name: str
    hypothesis: str
    evidence: str
    kill_path: str
    target_tier: Tier
    status: str = "pending"
    verdict: VerdictResult | None = None


@dataclass(frozen=True)
class Capability:
    """
    Linear capability token. Construct fresh; consume returns a new
    Capability(consumed=True). Re-presenting a consumed token to PROMOTE
    is rejected by the persisted spent_caps table — linearity holds across
    process boundaries.
    """
    cap_id: str
    cap_type: str = "PromoteCap"
    consumed: bool = False

    def consume(self) -> "Capability":
        if self.consumed:
            raise CapabilityError(f"capability {self.cap_id} already consumed (in-process)")
        return Capability(self.cap_id, self.cap_type, True)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class BlockedError(RuntimeError):
    """Raised by GATE on a BLOCK verdict."""


class CapabilityError(RuntimeError):
    """Raised on capability misuse (double-spend, missing, wrong type)."""


class ImmutabilityError(RuntimeError):
    """Raised on attempted overwrite of a promoted symbol."""


class FalsificationError(RuntimeError):
    """Raised when PROMOTE is called on a claim without a non-BLOCK verdict."""


class IntegrityError(RuntimeError):
    """Raised when a content-addressed read finds a hash mismatch."""


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS symbols (
    name        TEXT NOT NULL,
    version     INTEGER NOT NULL,
    def_hash    TEXT NOT NULL,
    def_blob    TEXT NOT NULL,
    provenance  TEXT NOT NULL,
    tier        TEXT NOT NULL,
    created_at  REAL NOT NULL,
    PRIMARY KEY(name, version)
);

CREATE INDEX IF NOT EXISTS idx_symbols_def_hash ON symbols(def_hash);

CREATE TABLE IF NOT EXISTS claims (
    id                  TEXT PRIMARY KEY,
    target_name         TEXT NOT NULL,
    hypothesis          TEXT NOT NULL,
    evidence            TEXT NOT NULL,
    kill_path           TEXT NOT NULL,
    target_tier         TEXT NOT NULL,
    status              TEXT NOT NULL DEFAULT 'pending',
    verdict_status      TEXT,
    verdict_rationale   TEXT,
    verdict_input_hash  TEXT,
    verdict_seed        INTEGER,
    verdict_runtime_ms  INTEGER
);

CREATE TABLE IF NOT EXISTS capabilities (
    cap_id      TEXT PRIMARY KEY,
    cap_type    TEXT NOT NULL,
    consumed    INTEGER NOT NULL DEFAULT 0
);
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


# ---------------------------------------------------------------------------
# The kernel
# ---------------------------------------------------------------------------

class SigmaKernel:
    """
    The substrate kernel. Wraps a SQLite connection.

    Five real opcodes (RESOLVE, CLAIM, FALSIFY, GATE, PROMOTE) plus TRACE
    as a read-only provenance walk. mint_capability and bootstrap_symbol
    are MVP scaffolding — flagged as such, not opcodes.
    """

    ORACLE_PATH = Path(__file__).parent / "omega_oracle.py"

    def __init__(self, db_path: str | Path = ":memory:"):
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # ------------------------------------------------------------------
    # MVP scaffolding (not opcodes; flagged for the eventual GENESIS spec)
    # ------------------------------------------------------------------

    def bootstrap_symbol(
        self,
        name: str,
        version: int,
        def_obj: dict,
        tier: Tier = Tier.WorkingTheory,
        provenance: list[str] | None = None,
    ) -> Symbol:
        """
        STUB: hardcoded substrate seeding for the MVP. In the eventual
        architecture this would be the GENESIS protocol with anchor-suite
        calibration. Here we just append directly.
        """
        def_blob = json.dumps(def_obj, sort_keys=True)
        def_hash = _sha256(def_blob)
        prov = provenance or []
        try:
            self.conn.execute(
                "INSERT INTO symbols VALUES (?,?,?,?,?,?,?)",
                (name, version, def_hash, def_blob, json.dumps(prov), tier.value, time.time()),
            )
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            raise ImmutabilityError(f"{name}@v{version} already in substrate") from e
        return Symbol(name, version, def_hash, def_blob, prov, tier)

    def mint_capability(self, cap_type: str = "PromoteCap") -> Capability:
        """
        STUB: in the eventual architecture capabilities are issued by
        role assignment + quorum. Here the demo mints them directly.
        """
        cap_id = _new_id("cap")
        self.conn.execute(
            "INSERT INTO capabilities VALUES (?,?,0)",
            (cap_id, cap_type),
        )
        self.conn.commit()
        return Capability(cap_id, cap_type)

    # ------------------------------------------------------------------
    # OPCODE 1 — RESOLVE
    # ------------------------------------------------------------------

    def RESOLVE(self, name: str, version: int) -> Symbol:
        """Fetch by (name, version). Verify content hash. Reject on miss or mismatch."""
        row = self.conn.execute(
            "SELECT name, version, def_hash, def_blob, provenance, tier "
            "FROM symbols WHERE name=? AND version=?",
            (name, version),
        ).fetchone()
        if row is None:
            raise KeyError(f"{name}@v{version} not in substrate")

        sym = Symbol(
            name=row[0],
            version=row[1],
            def_hash=row[2],
            def_blob=row[3],
            provenance=json.loads(row[4]),
            tier=Tier(row[5]),
        )

        # Hash integrity: recompute and reject on mismatch.
        computed = _sha256(sym.def_blob)
        if computed != sym.def_hash:
            raise IntegrityError(
                f"hash mismatch on {sym.ref}: stored={sym.def_hash[:12]} computed={computed[:12]}"
            )
        return sym

    # ------------------------------------------------------------------
    # OPCODE 2 — CLAIM
    # ------------------------------------------------------------------

    def CLAIM(
        self,
        target_name: str,
        hypothesis: str,
        evidence: dict,
        kill_path: str,
        target_tier: Tier = Tier.Conjecture,
    ) -> Claim:
        """Allocate a provisional claim. Born at lowest tier unless overridden."""
        cid = _new_id("claim")
        evidence_str = json.dumps(evidence, sort_keys=True)
        claim = Claim(
            id=cid,
            target_name=target_name,
            hypothesis=hypothesis,
            evidence=evidence_str,
            kill_path=kill_path,
            target_tier=target_tier,
        )
        self.conn.execute(
            "INSERT INTO claims VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                cid, target_name, hypothesis, evidence_str, kill_path,
                target_tier.value, "pending",
                None, None, None, None, None,
            ),
        )
        self.conn.commit()
        return claim

    # ------------------------------------------------------------------
    # OPCODE 3 — FALSIFY
    # ------------------------------------------------------------------

    def FALSIFY(self, claim: Claim, seed: int = 42) -> VerdictResult:
        """
        Dispatch the claim + kill_path to the Ω oracle subprocess.
        Bind the verdict to the claim. Return the verdict.

        The oracle is a separate process — control plane / data plane split.
        Fails closed: any oracle error becomes a BLOCK with the error rationale.
        """
        oracle_input = {
            "claim_id": claim.id,
            "hypothesis": claim.hypothesis,
            "evidence": claim.evidence,
            "kill_path": claim.kill_path,
            "seed": seed,
        }

        t0 = time.time()
        try:
            proc = subprocess.run(
                [sys.executable, str(self.ORACLE_PATH)],
                input=json.dumps(oracle_input).encode("utf-8"),
                capture_output=True,
                timeout=10,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            verdict = VerdictResult(
                status=Verdict.BLOCK,
                rationale=f"oracle subprocess failed: {e.stderr.decode('utf-8', errors='replace')[:200]}",
                input_hash="",
                seed=seed,
                runtime_ms=int((time.time() - t0) * 1000),
            )
        except subprocess.TimeoutExpired:
            verdict = VerdictResult(
                status=Verdict.BLOCK,
                rationale="oracle subprocess timed out",
                input_hash="",
                seed=seed,
                runtime_ms=int((time.time() - t0) * 1000),
            )
        else:
            try:
                out = json.loads(proc.stdout.decode("utf-8"))
                verdict = VerdictResult(
                    status=Verdict(out["verdict"]),
                    rationale=out.get("rationale", ""),
                    input_hash=out.get("input_hash", ""),
                    seed=out.get("seed", seed),
                    runtime_ms=int(out.get("runtime_ms", (time.time() - t0) * 1000)),
                )
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                verdict = VerdictResult(
                    status=Verdict.BLOCK,
                    rationale=f"oracle response malformed: {e}",
                    input_hash="",
                    seed=seed,
                    runtime_ms=int((time.time() - t0) * 1000),
                )

        # Bind to claim (in-memory and persisted).
        claim.verdict = verdict
        claim.status = "falsified"
        self.conn.execute(
            "UPDATE claims SET status='falsified', verdict_status=?, verdict_rationale=?, "
            "verdict_input_hash=?, verdict_seed=?, verdict_runtime_ms=? WHERE id=?",
            (
                verdict.status.value, verdict.rationale, verdict.input_hash,
                verdict.seed, verdict.runtime_ms, claim.id,
            ),
        )
        self.conn.commit()
        return verdict

    # ------------------------------------------------------------------
    # OPCODE 4 — GATE
    # ------------------------------------------------------------------

    def GATE(self, verdict: VerdictResult) -> str:
        """
        Three-valued epistemic branch:
          BLOCK → raise BlockedError (caller's path dies)
          WARN  → bubble rationale; caller may proceed but the warning is
                  permanently attached to any value derived downstream
          CLEAR → continue
        """
        if verdict.status == Verdict.BLOCK:
            raise BlockedError(verdict.rationale)
        if verdict.status == Verdict.WARN:
            # The caller's responsibility is to record the warning in any
            # downstream provenance. The MVP just prints it.
            print(f"  [GATE WARN] {verdict.rationale}")
            return "WARN"
        return "CLEAR"

    # ------------------------------------------------------------------
    # OPCODE 5 — PROMOTE
    # ------------------------------------------------------------------

    def PROMOTE(self, claim: Claim, cap: Capability) -> Symbol:
        """
        Append a new immutable symbol. Requires:
          1. cap exists and is unconsumed (rejected by spent_caps table)
          2. cap is consumed atomically with the promote (linear discipline)
          3. claim has a non-BLOCK verdict bound (defense-in-depth even if
             caller bypassed GATE)
          4. (name, version) does not already exist (rejected by PRIMARY KEY)
        """
        # 1. Verify capability exists and is unconsumed.
        cap_row = self.conn.execute(
            "SELECT consumed FROM capabilities WHERE cap_id=? AND cap_type='PromoteCap'",
            (cap.cap_id,),
        ).fetchone()
        if cap_row is None:
            raise CapabilityError(f"capability {cap.cap_id} not registered (mint via mint_capability)")
        if cap_row[0]:
            raise CapabilityError(f"capability {cap.cap_id} already consumed (double-spend rejected)")

        # 2. Defense-in-depth verdict check (caller may have skipped GATE).
        if claim.verdict is None:
            raise FalsificationError(f"claim {claim.id} has no verdict; FALSIFY first")
        if claim.verdict.status == Verdict.BLOCK:
            raise FalsificationError(f"claim {claim.id} has BLOCK verdict; cannot promote")

        # 3. Compute the new symbol.
        target_name = claim.target_name
        max_ver = self.conn.execute(
            "SELECT COALESCE(MAX(version), 0) FROM symbols WHERE name=?",
            (target_name,),
        ).fetchone()[0]
        new_version = max_ver + 1

        # Provenance: dataset+null hashes from evidence, plus the verdict's input hash.
        ev = json.loads(claim.evidence)
        provenance: list[str] = []
        for key in sorted(ev.keys()):
            v = ev[key]
            if isinstance(v, str) and len(v) == 64:  # looks like a sha256
                provenance.append(v)
        if claim.verdict.input_hash:
            provenance.append(claim.verdict.input_hash)

        def_blob = json.dumps(
            {
                "hypothesis": claim.hypothesis,
                "evidence": ev,
                "kill_path": claim.kill_path,
                "verdict": claim.verdict.status.value,
                "verdict_rationale": claim.verdict.rationale,
            },
            sort_keys=True,
        )
        def_hash = _sha256(def_blob)

        # 4. Atomic: consume cap + insert symbol.
        try:
            self.conn.execute("BEGIN")
            self.conn.execute(
                "UPDATE capabilities SET consumed=1 WHERE cap_id=?",
                (cap.cap_id,),
            )
            self.conn.execute(
                "INSERT INTO symbols VALUES (?,?,?,?,?,?,?)",
                (
                    target_name, new_version, def_hash, def_blob,
                    json.dumps(provenance), claim.target_tier.value, time.time(),
                ),
            )
            self.conn.execute(
                "UPDATE claims SET status='promoted' WHERE id=?",
                (claim.id,),
            )
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            raise ImmutabilityError(
                f"{target_name}@v{new_version} collision: {e}"
            ) from e
        except Exception:
            self.conn.rollback()
            raise

        return Symbol(
            name=target_name,
            version=new_version,
            def_hash=def_hash,
            def_blob=def_blob,
            provenance=provenance,
            tier=claim.target_tier,
        )

    # ------------------------------------------------------------------
    # OPCODE 6 -- ERRATA
    # ------------------------------------------------------------------

    def ERRATA(
        self,
        prior_name: str,
        prior_version: int,
        corrected_def: dict,
        fault_description: str,
        cap: Capability,
    ) -> Symbol:
        """
        Promote a corrected v(N+1) of an existing symbol with an
        errata_correcting backref. The prior version remains immutable
        in the substrate as historical record of what was pushed and why
        it was wrong.

        Append-only is preserved: we ADD a new edge (the errata pointer
        embedded in the new symbol's def_blob), we never mutate the prior.
        """
        # 1. Verify the prior version exists.
        prior = self.RESOLVE(prior_name, prior_version)

        # 2. Verify and consume capability.
        cap_row = self.conn.execute(
            "SELECT consumed FROM capabilities WHERE cap_id=? AND cap_type='PromoteCap'",
            (cap.cap_id,),
        ).fetchone()
        if cap_row is None:
            raise CapabilityError(f"capability {cap.cap_id} not registered")
        if cap_row[0]:
            raise CapabilityError(f"capability {cap.cap_id} already consumed")

        new_version = prior.version + 1
        # Defensive: handle the rare case where v(N+1) was already promoted.
        existing = self.conn.execute(
            "SELECT 1 FROM symbols WHERE name=? AND version=?",
            (prior_name, new_version),
        ).fetchone()
        if existing:
            raise ImmutabilityError(
                f"{prior_name}@v{new_version} already exists; cannot errata over it"
            )

        # 3. Build the corrected symbol with the backref.
        def_obj = {
            "corrected_def": corrected_def,
            "errata_correcting": f"{prior_name}@v{prior_version}",
            "fault_description": fault_description,
            "prior_def_hash": prior.def_hash,
        }
        def_blob = json.dumps(def_obj, sort_keys=True)
        def_hash = _sha256(def_blob)

        # Provenance: include the prior's def_hash so TRACE walks the lineage.
        provenance = [prior.def_hash]

        try:
            self.conn.execute("BEGIN")
            self.conn.execute(
                "UPDATE capabilities SET consumed=1 WHERE cap_id=?",
                (cap.cap_id,),
            )
            self.conn.execute(
                "INSERT INTO symbols VALUES (?,?,?,?,?,?,?)",
                (
                    prior_name, new_version, def_hash, def_blob,
                    json.dumps(provenance), prior.tier.value, time.time(),
                ),
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

        return Symbol(
            name=prior_name,
            version=new_version,
            def_hash=def_hash,
            def_blob=def_blob,
            provenance=provenance,
            tier=prior.tier,
        )

    # ------------------------------------------------------------------
    # OPCODE 7 -- TRACE
    # ------------------------------------------------------------------

    def TRACE(self, symbol: Symbol) -> dict[str, Any]:
        """
        Recursive provenance walk from `symbol` outward through dependency hashes.
        Cycle-safe via a visited set. Hashes that don't resolve to a substrate
        symbol are tagged 'external' (e.g. verdict_input_hash, bootstrap roots).
        """
        visited: set[str] = set()

        def walk(def_hash: str) -> dict[str, Any]:
            if def_hash in visited:
                return {"hash": def_hash[:12], "type": "cycle"}
            visited.add(def_hash)

            row = self.conn.execute(
                "SELECT name, version, provenance FROM symbols WHERE def_hash=?",
                (def_hash,),
            ).fetchone()
            if row is None:
                return {"hash": def_hash[:12], "type": "external"}

            children = []
            for child_hash in json.loads(row[2]):
                children.append(walk(child_hash))

            return {
                "ref": f"{row[0]}@v{row[1]}",
                "hash": def_hash[:12],
                "children": children,
            }

        return walk(symbol.def_hash)

    # ------------------------------------------------------------------
    # Inspection helpers (not opcodes)
    # ------------------------------------------------------------------

    def list_symbols(self) -> list[tuple[str, int, str, str]]:
        rows = self.conn.execute(
            "SELECT name, version, substr(def_hash,1,12), tier FROM symbols ORDER BY name, version"
        ).fetchall()
        return rows

    def close(self):
        self.conn.close()
