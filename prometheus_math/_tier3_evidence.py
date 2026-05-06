"""prometheus_math._tier3_evidence -- shared KillVector v2 + EvidenceField
emission helper for the 6 cross-domain envs (substrate v2.3 §9 Tier 3).

Wires the existing per-step ``elapsed_seconds`` + ``oracle_calls``
telemetry (Pre-Tier-0 step 0b) into a typed evidence ontology:

* ``KillVector`` (kill_vector.py) -- one component per falsifier the env
  ran. For these prediction-style envs the "falsifier" is just
  "prediction_correct"; ``triggered = not correct``.
* ``EvidenceField`` (evidence_field.py) -- 6 factual axes derived from
  the KillVector + telemetry. ``exclusion_distance`` is NULL for these
  domains since no ``CoordinateChart`` is registered yet (only Lehmer
  has one); the ``reason_unpopulated`` field carries the explanation.

Reported as "observed policy table", NOT "manifold chart" per ChatGPT
drift warning -- coordinate_chart_id is ``"provisional:<domain>"``.
The cross-domain envs use ``provisional:`` to flag that no real chart
exists yet (blocked on Charon coord per joint sprint T11).

Single-component KillVector convention
--------------------------------------
For envs that just compare predicted vs ground truth, one component
suffices:

    KillComponent(
        falsifier_name="prediction_correct",
        triggered=not correct,
        margin=None if correct else 1.0,
        margin_unit="boolean",
        method="kernel_bind_eval",
        convergence_status="exact",
    )

Richer-falsifier envs can build their own KillVector and pass it as
``kill_vector_override``.

Serialisation
-------------
``info["kill_vector"]`` is a ``dict`` (KillVector.to_dict() shape).
``info["evidence_field"]`` is a ``dict`` produced by
``dataclasses.asdict()`` on the ``EvidenceField`` -- this guarantees
JSON-serialisability and a stable shape across consumers (downstream
ledger writers, dashboards, the Learner). Six top-level keys: the six
axis names. ``axis_confidence`` ships as a 7th key.
"""
from __future__ import annotations

import hashlib
from dataclasses import asdict
from typing import Any, Dict, Mapping, Optional, Sequence

from .kill_vector import KillComponent, KillVector
from .evidence_field import EvidenceField, build_evidence_field


# Default method string for the BIND/EVAL substrate-call path used by
# every cross-domain env. Single canonical name so downstream
# correlation tooling sees a uniform method label.
DEFAULT_METHOD: str = "kernel_bind_eval"

# Falsifier name for the binary "did the prediction match ground truth"
# check. Documented here so test fixtures and the Learner agree.
PREDICTION_FALSIFIER: str = "prediction_correct"


def _hash_candidate(*parts: Any) -> str:
    """SHA-256 hex digest over the string-rendered ``parts``. Used to
    bind a KillVector to the specific (env, episode-key) being scored
    so the Learner can dedupe across runs."""
    h = hashlib.sha256()
    for p in parts:
        h.update(str(p).encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def build_prediction_kill_vector(
    *,
    correct: bool,
    operator_class: str,
    candidate_hash: str,
    region_meta: Optional[Mapping[str, Any]] = None,
    method: str = DEFAULT_METHOD,
) -> KillVector:
    """Single-component KillVector for prediction-style envs.

    ``triggered = not correct`` per substrate convention: triggered
    means "this falsifier kicked in" = "the prediction was wrong".
    ``margin`` is binary (None when correct, 1.0 when wrong);
    ``margin_unit="boolean"`` documents the convention.
    """
    component = KillComponent(
        falsifier_name=PREDICTION_FALSIFIER,
        triggered=not correct,
        margin=None if correct else 1.0,
        margin_unit="boolean",
        method=str(method),
        convergence_status="exact",
    )
    return KillVector(
        components=(component,),
        candidate_hash=str(candidate_hash),
        operator_class=str(operator_class),
        region_meta=dict(region_meta or {}),
    )


def build_step_evidence(
    *,
    correct: bool,
    domain: str,
    env_name: str,
    elapsed_seconds: float,
    oracle_calls: int,
    region_meta: Optional[Mapping[str, Any]] = None,
    candidate_parts: Sequence[Any] = (),
    method: str = DEFAULT_METHOD,
    kill_vector_override: Optional[KillVector] = None,
) -> Dict[str, Any]:
    """Build the ``{"kill_vector": ..., "evidence_field": ...}`` payload
    that each Tier-3 env adds to its ``info`` dict.

    Parameters
    ----------
    correct : bool
        Did the prediction match the ground truth?
    domain : str
        Domain string used in ``RAW_INVARIANTS_PER_DOMAIN``
        (e.g. ``"bsd_rank"``, ``"modular_form"``,
        ``"knot_trace_field"``, ``"genus2"``, ``"oeis_sleeping"``,
        ``"mock_theta"``). Used to build
        ``coordinate_chart_id="provisional:<domain>"``.
    env_name : str
        Friendly env identifier used as the KillVector
        ``operator_class`` (versioned ``<env_name>_v1``).
    elapsed_seconds, oracle_calls : float, int
        Per-step telemetry from the env's existing instrumentation.
    region_meta : mapping, optional
        Per-step region metadata for the KillVector
        ``region_meta`` field (e.g. ``{"split": ..., "label": ...}``).
    candidate_parts : sequence, optional
        Parts to concatenate for the candidate hash. Defaults to a
        deterministic but uninformative hash if empty.
    method : str
        Method string for the KillComponent + EvidenceField
        ``methods_used``. Defaults to ``"kernel_bind_eval"``.
    kill_vector_override : KillVector, optional
        For envs with richer falsifier logic (none today; reserved for
        future Tier-3 expansion). When supplied, bypasses the default
        single-component KillVector.

    Returns
    -------
    dict
        ``{"kill_vector": <KillVector.to_dict()>,
           "evidence_field": <asdict(EvidenceField)>}``
    """
    if kill_vector_override is not None:
        kv = kill_vector_override
    else:
        candidate_hash = _hash_candidate(env_name, *candidate_parts)
        kv = build_prediction_kill_vector(
            correct=correct,
            operator_class=f"{env_name}_v1",
            candidate_hash=candidate_hash,
            region_meta=region_meta,
            method=method,
        )

    ef = build_evidence_field(
        kill_vector=kv,
        elapsed_seconds=float(elapsed_seconds),
        oracle_calls=int(oracle_calls),
        coordinate_chart_id=f"provisional:{domain}",
        methods_used=(method,),
    )

    return {
        "kill_vector": kv.to_dict(),
        "evidence_field": asdict(ef),
    }


__all__ = [
    "DEFAULT_METHOD",
    "PREDICTION_FALSIFIER",
    "build_prediction_kill_vector",
    "build_step_evidence",
]
