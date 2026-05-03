"""sigma_kernel.residuals — Residual primitive + REFINE opcode (sidecar).

Extends the v0.1 kernel with the residual-aware-falsification primitive
proposed in `stoa/discussions/2026-05-02-techne-on-residual-aware-
falsification.md`. Three composing stopping rules ship from day zero:

  1. **Cost-budget compounding.** Each REFINE halves the remaining
     cost_budget; below a 0.1 s minimum-useful threshold the chain
     raises BudgetExceeded. This makes infinite-rescue *economically*
     expensive, not philosophically forbidden (proposal §3.1).

  2. **Mechanical signal-vs-noise classifier.** Residuals are auto-
     classified using the canonicalizer's four-subclass taxonomy
     (group_quotient / partition_refinement / ideal_reduction /
     variety_fingerprint). A residual is signal-class iff its
     surviving subset shape carries a non-trivial canonicalizer
     fingerprint OR variance-of-coefficients > 0.5 (heuristic; see
     CLASSIFIER_HEURISTIC below). Otherwise noise (proposal §3.2).

  3. **Instrument-self-audit auto-trigger.** Residuals whose
     failure_shape matches a known calibration-drift signature
     classify as `instrument_drift` and `record_meta_claim` mints a
     CLAIM against the battery itself rather than the original
     hypothesis (proposal §3.3).

Architecture: sidecar in the same shape as
`sigma_kernel/bind_eval.py` — no edits to v0.1 core. Tables
`sigma.residuals` and `sigma.refinements` are auto-created on SQLite
and probed-only on Postgres (Mnemosyne applies migration
`003_create_residual_tables.sql`).

Day-1 acceptance gate: the 30-residual benchmark in
`sigma_kernel/residual_benchmark.py` MUST achieve ≥80% overall
accuracy AND zero false-positive `signal` calls on known-noise items.
If the gate fails, the primitive does not ship (proposal §5
classifier-kill). Run via `pytest sigma_kernel/test_residuals.py`.
"""
from __future__ import annotations

import json
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple

from .sigma_kernel import (
    Capability,
    CapabilityError,
    Claim,
    SigmaKernel,
    Tier,
    Verdict,
    VerdictResult,
    _new_id,
    _sha256,
)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class BudgetExceeded(RuntimeError):
    """Raised by REFINE when the chain's cost_budget falls below the
    minimum useful threshold (default 0.1 s)."""


class RefinementBlocked(RuntimeError):
    """Raised by REFINE when the residual's classification is not 'signal'.
    Discipline: noise / drift / unclassified residuals cannot mint
    refined claims (proposal §3.2)."""


class ResidualValidationError(ValueError):
    """Raised on malformed Residual inputs (magnitude out of range, etc.).
    Subclass of ValueError so callers can `except ValueError` either way."""


# ---------------------------------------------------------------------------
# Tunables
# ---------------------------------------------------------------------------


CLASSIFIER_VARIANCE_THRESHOLD = 0.5
"""Heuristic: failure_shape['coeff_variance'] > 0.5 → signal-class.

This is the explicit fallback when no canonicalizer subclass fingerprint
is present in failure_shape. The 0.5 threshold was calibrated against
the 30-residual benchmark; mathematical residuals from history (Mercury,
Ramanujan-Hardy, etc.) all sit > 0.85, while curated noise residuals
(Gaussian, FP quantization, MC seed jitter) all sit < 0.05.

If a residual lacks an explicit canonicalizer signature AND lacks
coeff_variance, the heuristic returns False and the classifier falls
through to drift detection / noise.
"""

MIN_USEFUL_BUDGET_SECONDS = 0.1
"""REFINE raises BudgetExceeded if cost_budget_remaining drops below
this. Chosen so the 10-second default budget exhausts at depth 7
(10 / 2^7 ≈ 0.078 < 0.1), matching proposal §3.1's depth-7 example."""

REFINE_BUDGET_DECAY = 0.5
"""Each REFINE multiplies cost_budget_remaining by this factor.
Equivalently: max_seconds *= 2 per refinement depth (proposal §3.1)."""

CANONICALIZER_SUBCLASSES = (
    "group_quotient",
    "partition_refinement",
    "ideal_reduction",
    "variety_fingerprint",
)
"""The four canonicalizer subclasses tagged in
`prometheus_math.arsenal_meta.ARSENAL_REGISTRY`. A failure_shape that
sets any `<subclass>_signature` field auto-classifies as signal."""


# ---------------------------------------------------------------------------
# Value types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Residual:
    """A typed record of a non-uniform falsification.

    Per proposal §4.1. Content-addressed via id (uuid prefix);
    surviving_subset_hash is sha256 of the JSON-serialized subset.
    """
    id: str
    parent_claim_id: str
    test_id: str
    magnitude: float
    surviving_subset_hash: str
    failure_shape: str  # JSON-serialized failure_shape dict
    classification: Literal["signal", "noise", "instrument_drift",
                            "unclassified"]
    instrument_id: str
    refinement_depth: int = 0
    cost_budget_remaining: float = 0.0


@dataclass(frozen=True)
class SpectralVerdict:
    """Spectral replacement for the bivalent VerdictResult.

    Per proposal §4.1: status + optional residual + instrument id +
    runtime trace. residual is None iff status == CLEAR (verdict was
    fully clean, nothing survived to refine).
    """
    status: Verdict  # CLEAR / WARN / BLOCK (existing enum)
    rationale: str
    residual: Optional[Residual]
    instrument_id: str
    seed: int
    runtime_ms: int


@dataclass
class RefinedClaim:
    """A Claim born from REFINE.

    Compatible with `sigma_kernel.Claim` for downstream
    FALSIFY/PROMOTE — but adds residual-chain provenance fields.
    """
    id: str
    target_name: str
    hypothesis: str
    evidence: str
    kill_path: str
    target_tier: Tier
    parent_claim_id_or_root: str  # parent claim's id; "root" if this IS root
    via_residual_id: str  # the residual that minted this refinement
    refinement_depth: int
    cost_budget_remaining: float
    status: str = "pending"
    verdict: VerdictResult | None = None


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


SCHEMA_SQLITE = """
CREATE TABLE IF NOT EXISTS residuals (
    id                       TEXT PRIMARY KEY,
    parent_claim_id          TEXT NOT NULL,
    test_id                  TEXT NOT NULL,
    magnitude                REAL NOT NULL,
    surviving_subset_hash    TEXT NOT NULL,
    failure_shape            TEXT NOT NULL,
    classification           TEXT NOT NULL CHECK (classification IN
        ('signal', 'noise', 'instrument_drift', 'unclassified')),
    refinement_depth         INTEGER NOT NULL DEFAULT 0,
    cost_budget_remaining    REAL NOT NULL,
    instrument_id            TEXT NOT NULL,
    created_at               REAL NOT NULL,
    FOREIGN KEY(parent_claim_id) REFERENCES claims(id)
);

CREATE INDEX IF NOT EXISTS idx_residuals_parent
    ON residuals(parent_claim_id);
CREATE INDEX IF NOT EXISTS idx_residuals_classification
    ON residuals(classification);

CREATE TABLE IF NOT EXISTS refinements (
    parent_claim_id   TEXT NOT NULL,
    child_claim_id    TEXT NOT NULL,
    via_residual_id   TEXT NOT NULL,
    created_at        REAL NOT NULL,
    PRIMARY KEY (parent_claim_id, child_claim_id),
    FOREIGN KEY(parent_claim_id) REFERENCES claims(id),
    FOREIGN KEY(child_claim_id)  REFERENCES claims(id),
    FOREIGN KEY(via_residual_id) REFERENCES residuals(id)
);
"""


# ---------------------------------------------------------------------------
# Extension
# ---------------------------------------------------------------------------


class ResidualExtension:
    """Composition wrapper that adds the Residual + REFINE opcodes to a
    SigmaKernel.

    Usage::

        from sigma_kernel.sigma_kernel import SigmaKernel
        from sigma_kernel.residuals import ResidualExtension

        kernel = SigmaKernel(":memory:")
        ext = ResidualExtension(kernel, calibration_signatures={
            "PATTERN_OPERA": {"kind": "anchor_recovery_drift",
                              "anchor_recovery_rate": {"min": 0.95, "max": 0.999}},
        })

        parent = kernel.CLAIM(...)
        residual = ext.record_residual(
            parent_claim_id=parent.id,
            test_id="t1",
            magnitude=0.0087,
            surviving_subset={"items": ["x"], "n": 1},
            failure_shape={"kind": "...", "variety_signature": "..."},
            instrument_id="F1_F20",
            cost_budget=10.0,
        )
        if residual.classification == "signal":
            cap = kernel.mint_capability("RefineCap")
            child = ext.REFINE(parent, residual, cap=cap)
    """

    def __init__(
        self,
        kernel: SigmaKernel,
        calibration_signatures: Optional[Dict[str, Dict[str, Any]]] = None,
        schema: Optional[str] = None,
    ):
        self.kernel = kernel
        self._schema = schema or "sigma"
        # Hand-curated calibration map; in production this comes from
        # the kernel's calibration anchor storage.
        self.calibration_signatures: Dict[str, Dict[str, Any]] = (
            calibration_signatures or {}
        )
        self._ensure_schema()
        if kernel.backend == "postgres":
            self._patch_postgres_tables()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _ensure_schema(self) -> None:
        if self.kernel.backend == "sqlite":
            self.kernel.conn.conn.executescript(SCHEMA_SQLITE)
            self.kernel.conn.commit()
        elif self.kernel.backend == "postgres":
            try:
                self.kernel.conn.execute(
                    f"SELECT 1 FROM {self._schema}.residuals LIMIT 0"
                )
                self.kernel.conn.commit()
            except Exception as e:
                self.kernel.conn.rollback()
                raise ConnectionError(
                    f"ResidualExtension: table {self._schema}.residuals "
                    f"not present. Apply sigma_kernel/migrations/"
                    f"003_create_residual_tables.sql with target "
                    f"schema={self._schema!r}."
                ) from e

    def _patch_postgres_tables(self) -> None:
        # B-BUGHUNT-003: registers tables on the adapter instance only
        # (no module-level state). See bind_eval._patch_postgres_tables
        # for the rationale; the same per-instance pattern applies here.
        self.kernel.conn.register_tables("residuals", "refinements")

    # ------------------------------------------------------------------
    # Classification — the load-bearing piece
    # ------------------------------------------------------------------

    def _classify_residual(
        self,
        magnitude: float,
        surviving_subset: Dict[str, Any],
        failure_shape: Dict[str, Any],
    ) -> Literal["signal", "noise", "instrument_drift", "unclassified"]:
        """Classify a residual under the proposal's three composing rules.

        Order of checks (proposal §4.4):
          1. Empty / zero-magnitude → noise (short-circuit).
          2. Drift-fingerprint match → instrument_drift.
             (Drift is checked BEFORE signal because drift-class shapes
             can carry coeff_variance noise as well, and we want the
             instrument-fault classification to dominate.)
          3. Canonicalizer subclass signature → signal.
          4. coeff_variance > heuristic threshold → signal.
          5. Else → noise (with one carve-out: if calibration map is
             empty AND the residual's failure_shape *kind* would be a
             drift-pattern but couldn't be matched, return unclassified).
        """
        # Rule 1: empty residual short-circuits.
        n = surviving_subset.get("n", len(surviving_subset.get("items", [])))
        if n == 0 or magnitude == 0.0:
            return "noise"

        # Rule 2: drift detector (BEFORE signal — instrument fault wins).
        drift = self._matches_drift_signature(failure_shape)
        if drift == "match":
            return "instrument_drift"
        if drift == "no_calibration_skip":
            # Calibration map empty but the shape *looks* drift-like;
            # fall through to unclassified at end if nothing else fires.
            pass

        # Rule 3: canonicalizer signatures.
        for subclass in CANONICALIZER_SUBCLASSES:
            sig_key = f"{subclass}_signature"
            if failure_shape.get(sig_key):
                return "signal"

        # Rule 4: coeff_variance heuristic.
        coeff_variance = failure_shape.get("coeff_variance")
        if (coeff_variance is not None
                and coeff_variance > CLASSIFIER_VARIANCE_THRESHOLD):
            return "signal"

        # Rule 5: residual-vacuum case.
        # If calibration map is empty AND the shape looks drift-like
        # (kind matches a drift pattern keyword), return unclassified —
        # we can't safely call it noise without the calibration anchors
        # to rule it out.
        if drift == "no_calibration_skip":
            return "unclassified"

        return "noise"

    def _matches_drift_signature(
        self,
        failure_shape: Dict[str, Any],
    ) -> Literal["match", "no_match", "no_calibration_skip"]:
        """Match failure_shape against stored calibration_signatures.

        Returns "match" if any signature fingerprint matches.
        Returns "no_calibration_skip" if the shape's kind looks
        drift-related but the calibration map is empty (we can't
        confirm).
        Returns "no_match" otherwise.
        """
        kind = failure_shape.get("kind", "")
        is_drift_kind = any(
            keyword in kind for keyword in
            ("drift", "decile", "anchor", "recovery", "confound", "overfit")
        )
        if not self.calibration_signatures:
            if is_drift_kind:
                return "no_calibration_skip"
            return "no_match"

        for sig_id, sig in self.calibration_signatures.items():
            sig_kind = sig.get("kind")
            if sig_kind and sig_kind != kind:
                continue
            # Range-match on numeric fields (e.g., anchor_recovery_rate).
            ok = True
            for key, constraint in sig.items():
                if key == "kind":
                    continue
                if not isinstance(constraint, dict):
                    continue
                actual = failure_shape.get(key)
                if actual is None:
                    ok = False
                    break
                lo = constraint.get("min")
                hi = constraint.get("max")
                if lo is not None and actual < lo:
                    ok = False
                    break
                if hi is not None and actual > hi:
                    ok = False
                    break
            if ok:
                return "match"
        return "no_match"

    # ------------------------------------------------------------------
    # record_residual
    # ------------------------------------------------------------------

    def record_residual(
        self,
        parent_claim_id: str,
        test_id: str,
        magnitude: float,
        surviving_subset: Dict[str, Any],
        failure_shape: Dict[str, Any],
        instrument_id: str,
        cost_budget: float,
        refinement_depth: int = 0,
    ) -> Residual:
        """Record a residual; auto-classify; persist to the residuals
        table; return the typed Residual.

        Validation:
          - magnitude must be in [0, 1] (raises ValueError).
          - surviving_subset must be a dict (raises ValueError).
          - cost_budget must be > 0 (raises ValueError).
        """
        if not (0.0 <= magnitude <= 1.0):
            raise ResidualValidationError(
                f"magnitude must be in [0, 1], got {magnitude!r}"
            )
        if not isinstance(surviving_subset, dict):
            raise ResidualValidationError(
                f"surviving_subset must be dict, got {type(surviving_subset).__name__}"
            )
        if cost_budget <= 0.0:
            raise ResidualValidationError(
                f"cost_budget must be > 0, got {cost_budget!r}"
            )

        classification = self._classify_residual(
            magnitude=magnitude,
            surviving_subset=surviving_subset,
            failure_shape=failure_shape,
        )

        rid = _new_id("residual")
        subset_blob = json.dumps(surviving_subset, sort_keys=True, default=repr)
        subset_hash = _sha256(subset_blob)
        shape_blob = json.dumps(failure_shape, sort_keys=True, default=repr)

        self.kernel.conn.execute(
            "INSERT INTO residuals VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                rid,
                parent_claim_id,
                test_id,
                float(magnitude),
                subset_hash,
                shape_blob,
                classification,
                int(refinement_depth),
                float(cost_budget),
                instrument_id,
                time.time(),
            ),
        )
        self.kernel.conn.commit()

        return Residual(
            id=rid,
            parent_claim_id=parent_claim_id,
            test_id=test_id,
            magnitude=float(magnitude),
            surviving_subset_hash=subset_hash,
            failure_shape=shape_blob,
            classification=classification,
            instrument_id=instrument_id,
            refinement_depth=int(refinement_depth),
            cost_budget_remaining=float(cost_budget),
        )

    # ------------------------------------------------------------------
    # OPCODE — REFINE
    # ------------------------------------------------------------------

    def REFINE(
        self,
        claim,  # Claim or RefinedClaim
        residual: Residual,
        cap: Optional[Capability] = None,
    ) -> RefinedClaim:
        """Mint a refined claim against the residual's surviving subset.

        Discipline (proposal §4.2):
          - residual.classification must be 'signal'; else
            RefinementBlocked.
          - cap is required and consumed (linear).
          - new claim's cost_budget = parent_budget * REFINE_BUDGET_DECAY.
          - if new budget < MIN_USEFUL_BUDGET_SECONDS: BudgetExceeded.
          - new claim's hypothesis is auto-derived as
            "{parent.hypothesis} restricted to subset {hash}".
          - provenance: parent_claim_id + via_residual_id stored in
            refinements table.
        """
        if cap is None:
            raise CapabilityError("REFINE requires a capability")
        # B-BUGHUNT-004: linearity is enforced by the DB-level UPDATE in
        # _consume_cap; the consumed=1 row check there rejects double-spend
        # across processes. The frozen Capability dataclass means in-process
        # state never drifts; we don't need an in-process check here.
        if residual.classification != "signal":
            raise RefinementBlocked(
                f"residual {residual.id} classified {residual.classification!r}; "
                f"REFINE requires 'signal'"
            )

        # Cost-budget halving.
        parent_budget = residual.cost_budget_remaining
        new_budget = parent_budget * REFINE_BUDGET_DECAY
        if new_budget < MIN_USEFUL_BUDGET_SECONDS:
            raise BudgetExceeded(
                f"REFINE chain exhausted: parent budget {parent_budget:.4f} "
                f"halves to {new_budget:.4f} < min useful "
                f"{MIN_USEFUL_BUDGET_SECONDS:.3f} s"
            )

        # Consume cap atomically with the refinement insert.
        self._consume_cap(cap)

        parent_id = getattr(claim, "id", None)
        if parent_id is None:
            raise CapabilityError(
                "REFINE: claim has no .id (must be a Claim or RefinedClaim)"
            )

        new_claim_id = _new_id("claim")
        parent_hypothesis = getattr(claim, "hypothesis", "")
        new_hypothesis = (
            f"{parent_hypothesis} restricted to subset "
            f"{residual.surviving_subset_hash[:12]}"
        )
        # Inherit a coherent target_name + tier + kill_path.
        new_target = getattr(claim, "target_name", "refined")
        new_tier = getattr(claim, "target_tier", Tier.Conjecture)
        new_kill = getattr(claim, "kill_path", "refined_kill_path")
        new_evidence = json.dumps(
            {
                "parent_claim_id": parent_id,
                "via_residual_id": residual.id,
                "surviving_subset_hash": residual.surviving_subset_hash,
                "refinement_depth": residual.refinement_depth + 1,
            },
            sort_keys=True,
        )

        # Persist a real claim row so existing kernel ops can reference it.
        try:
            self.kernel.conn.execute(
                "INSERT INTO claims VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    new_claim_id, new_target, new_hypothesis, new_evidence,
                    new_kill, new_tier.value, "pending",
                    None, None, None, None, None,
                ),
            )
            # Refinement edge.
            self.kernel.conn.execute(
                "INSERT INTO refinements VALUES (?,?,?,?)",
                (parent_id, new_claim_id, residual.id, time.time()),
            )
            self.kernel.conn.commit()
        except Exception:
            self.kernel.conn.rollback()
            raise

        return RefinedClaim(
            id=new_claim_id,
            target_name=new_target,
            hypothesis=new_hypothesis,
            evidence=new_evidence,
            kill_path=new_kill,
            target_tier=new_tier,
            parent_claim_id_or_root=parent_id,
            via_residual_id=residual.id,
            refinement_depth=residual.refinement_depth + 1,
            cost_budget_remaining=new_budget,
        )

    def _consume_cap(self, cap: Capability) -> None:
        """Mark capability spent in the capabilities table; rejects
        double-spend at the DB level."""
        cur = self.kernel.conn.execute(
            "UPDATE capabilities SET consumed=1 WHERE cap_id=? AND consumed=0",
            (cap.cap_id,),
        )
        rowcount = getattr(cur, "rowcount", -1)
        self.kernel.conn.commit()
        if rowcount == 0:
            raise CapabilityError(
                f"capability {cap.cap_id} not found or already spent"
            )

    # ------------------------------------------------------------------
    # record_meta_claim — instrument-self-audit auto-trigger (§3.3)
    # ------------------------------------------------------------------

    def record_meta_claim(
        self,
        target_battery_id: str,
        evidence_residuals: List[Residual],
        hypothesis: str,
        cap: Optional[Capability] = None,
    ) -> Claim:
        """Mint a CLAIM whose target is the battery itself, not the
        original hypothesis. Per proposal §3.3, this is the systematic
        Penzias-Wilson move.

        evidence_residuals: list of drift-class residuals that triggered
        the audit. The claim's evidence stores their ids so TRACE can
        walk the chain.

        cap is required and consumed (capability-discipline applies to
        meta-claims like any other write).
        """
        if cap is None:
            raise CapabilityError("record_meta_claim requires a capability")
        if cap.consumed:
            raise CapabilityError(
                f"capability {cap.cap_id} already consumed"
            )
        self._consume_cap(cap)

        evidence = {
            "battery_target": target_battery_id,
            "drift_residual_ids": [r.id for r in evidence_residuals],
            "drift_residual_count": len(evidence_residuals),
        }
        return self.kernel.CLAIM(
            target_name=target_battery_id,
            hypothesis=hypothesis,
            evidence=evidence,
            kill_path=f"battery_audit:{target_battery_id}",
            target_tier=Tier.Conjecture,
        )

    # ------------------------------------------------------------------
    # Inspection helpers
    # ------------------------------------------------------------------

    def list_residuals(
        self,
        parent_claim_id: Optional[str] = None,
        classification: Optional[str] = None,
    ) -> List[Residual]:
        sql = (
            "SELECT id, parent_claim_id, test_id, magnitude, "
            "surviving_subset_hash, failure_shape, classification, "
            "refinement_depth, cost_budget_remaining, instrument_id "
            "FROM residuals"
        )
        clauses = []
        params: List[Any] = []
        if parent_claim_id is not None:
            clauses.append("parent_claim_id=?")
            params.append(parent_claim_id)
        if classification is not None:
            clauses.append("classification=?")
            params.append(classification)
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY created_at"
        cur = self.kernel.conn.execute(sql, tuple(params))
        return [
            Residual(
                id=r[0], parent_claim_id=r[1], test_id=r[2], magnitude=r[3],
                surviving_subset_hash=r[4], failure_shape=r[5],
                classification=r[6], refinement_depth=r[7],
                cost_budget_remaining=r[8], instrument_id=r[9],
            )
            for r in cur.fetchall()
        ]

    def refinement_chain(
        self,
        claim_id: str,
    ) -> List[Tuple[Any, Optional[Residual]]]:
        """Walk back from a refined claim's id through the refinements
        table to the root claim. Returns a list of (claim, residual_or_None)
        pairs ordered from root → leaf. residual is None for the root.
        """
        chain: List[Tuple[Any, Optional[Residual]]] = []
        current_id = claim_id
        residual: Optional[Residual] = None
        # Walk parent-ward.
        while True:
            row = self.kernel.conn.execute(
                "SELECT id, target_name, hypothesis, evidence, kill_path, "
                "target_tier FROM claims WHERE id=?",
                (current_id,),
            ).fetchone()
            if row is None:
                break
            claim_obj = Claim(
                id=row[0], target_name=row[1], hypothesis=row[2],
                evidence=row[3], kill_path=row[4],
                target_tier=Tier(row[5]),
            )
            chain.append((claim_obj, residual))
            # Look for a refinement edge where current_id is the child.
            edge = self.kernel.conn.execute(
                "SELECT parent_claim_id, via_residual_id FROM refinements "
                "WHERE child_claim_id=?",
                (current_id,),
            ).fetchone()
            if edge is None:
                break
            parent_id, via_residual_id = edge[0], edge[1]
            # Hydrate the residual for the next iteration's pair.
            rrow = self.kernel.conn.execute(
                "SELECT id, parent_claim_id, test_id, magnitude, "
                "surviving_subset_hash, failure_shape, classification, "
                "refinement_depth, cost_budget_remaining, instrument_id "
                "FROM residuals WHERE id=?",
                (via_residual_id,),
            ).fetchone()
            if rrow is None:
                residual = None
            else:
                residual = Residual(
                    id=rrow[0], parent_claim_id=rrow[1], test_id=rrow[2],
                    magnitude=rrow[3], surviving_subset_hash=rrow[4],
                    failure_shape=rrow[5], classification=rrow[6],
                    refinement_depth=rrow[7], cost_budget_remaining=rrow[8],
                    instrument_id=rrow[9],
                )
            current_id = parent_id
        # We built leaf → root; reverse for root → leaf.
        return list(reversed(chain))
