"""prometheus_math.kill_vector — kill_path as a vector, not a category.

Day 3 of the Day 1-5 plan.  Replaces the categorical
``kill_path: str`` field of ``DiscoveryRecord`` with a typed
``KillVector`` whose components are ``(triggered, margin)`` pairs across
the falsifier battery.

Why
---
Yesterday's empirical archaeology over the kernel ledger showed
0.725-bit MI between operators and the binary categorical kill_path —
i.e. there's already detectable structure in "this falsifier killed
it / it didn't".  ChatGPT's reframe (echoed in the Day 1-5 plan): each
candidate's outcome is naturally a *vector*

    k = (k_F1, k_F6, k_F9, k_F11, k_recip, k_irreduce, k_catalog, k_band)

with one component per falsifier, each carrying

  * ``triggered`` — bool, "did this falsifier kill the candidate?"
  * ``margin``    — float | None, continuous "margin to failure" so
                    near-misses are distinguishable from comfortable
                    survivors.  None when the margin would require
                    re-running the falsifier (i.e. wasn't captured at
                    pipeline-time).

The vector is the substrate for Days 4-5: a learner consumes
``E[k | operator]`` to estimate per-operator "directional derivatives"
in kill-space, and greedy navigation searches for the zero vector.

Backwards compatibility
-----------------------
Old code reading ``record.kill_path: str`` continues to work.  The
``KillVector`` is the new field; the legacy categorical kill_path is
*derived* via ``kill_vector.to_legacy_kill_path()``.  Backfill from
existing pilot JSON / kernel ledger records is supported via
``kill_vector_from_legacy(record)``.

Margin units & combination
--------------------------
The unit-combination question is genuinely hard: F1's margin is a
``1 - p_value`` (in [0, 1]); F6's margin is a signed z-score (R); a
catalog Hamming distance is in N.  We tag each component with a
``margin_unit`` and offer two reduction strategies:

  * ``magnitude(unit_aware=True)`` (default): each margin is mapped to
    [0, 1] via a unit-specific squash before L2-summing.  Robust;
    treats "F1 marginal kill at p=0.04" comparably to "catalog distance
    1 from a known entry".
  * ``magnitude(unit_aware=False)``: raw L2 over numeric margins.
    Documented but discouraged — useful only when comparing within a
    single falsifier's regime.

See KILL_VECTOR_SPEC.md for the full rationale, including a discussion
of when this choice will matter (multi-falsifier near-misses) and when
it won't (single-falsifier dominant kills).
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Margin-unit registry
# ---------------------------------------------------------------------------


# Recognised margin units.  Each maps to a [0, 1] "saturated kill-strength"
# via ``_squash_margin``; this is what makes magnitudes comparable across
# units.
MARGIN_UNITS: Tuple[str, ...] = (
    "p_value",      # F1: margin = 1 - p_value, in [0, 1]; bigger = stronger kill
    "z_score",      # F6: signed z-score; |z| / (|z| + Z_CHAR) into [0, 1]
    "hamming",      # catalog: integer distance to nearest entry; 1/(1+d) into (0, 1]
    "absolute",     # generic numeric distance; |x| / (|x| + 1) into [0, 1)
    "log_distance", # log10(distance); exp(-x) into (0, 1]
    "boolean",      # raw 0/1 flag; identity into {0, 1}
)


# Characteristic z-score for the squash; |z|=2 ≈ 0.5 saturated kill-strength.
_Z_CHARACTERISTIC = 2.0


def _squash_margin(margin: Optional[float], unit: Optional[str]) -> float:
    """Map a (margin, unit) pair into [0, 1] saturated kill-strength.

    Returns 0.0 when ``margin`` is None or unit is unknown — i.e.
    "no information about how strongly this killed".  Used by
    ``magnitude(unit_aware=True)``.
    """
    if margin is None or unit is None:
        return 0.0
    try:
        m = float(margin)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(m):
        # +inf catalog distance = "no near match" = strong miss-signal,
        # which for kill-strength purposes saturates at 1.
        if math.isinf(m) and m > 0 and unit == "hamming":
            return 1.0
        return 0.0

    if unit == "p_value":
        # margin already mapped to [0, 1] by the convention 1 - p_value.
        return max(0.0, min(1.0, m))
    if unit == "z_score":
        # |z| / (|z| + Z_CHARACTERISTIC); signed z folded by abs.
        a = abs(m)
        return a / (a + _Z_CHARACTERISTIC)
    if unit == "hamming":
        # 0 = exact match (no kill); larger = farther = stronger miss.
        # Saturate via 1 - 1/(1+d) so 0 -> 0, 1 -> 0.5, +inf -> 1.
        if m < 0:
            m = 0.0
        return 1.0 - 1.0 / (1.0 + m)
    if unit == "absolute":
        a = abs(m)
        return a / (a + 1.0)
    if unit == "log_distance":
        # exp(-max(0, m)) so log_distance=0 → 1, large positive → 0.
        return math.exp(-max(0.0, m))
    if unit == "boolean":
        return 1.0 if m else 0.0
    return 0.0


# ---------------------------------------------------------------------------
# KillComponent / KillVector
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KillComponent:
    """One coordinate of the kill vector.

    Attributes
    ----------
    falsifier_name : str
        Canonical falsifier identifier.  Currently:
          * "out_of_band"       — Phase 0 band check (1.001 < M < 1.18)
          * "reciprocity"       — palindromic check
          * "irreducibility"    — sympy.factor_list factorisation
          * "F1_permutation_null"
          * "F6_base_rate"
          * "F9_simpler_explanation"
          * "F11_cross_validation"
          * "catalog:Mossinghoff"
          * "catalog:lehmer_literature"
          * "catalog:LMFDB"
          * "catalog:OEIS"
          * "catalog:arXiv"
        Catalog hits use the ``catalog:<name>`` prefix so downstream
        consumers can splat.  New falsifiers can be added without
        breaking existing code (the consuming code iterates components,
        keyed by name).
    triggered : bool
        Did this falsifier *kill* the candidate?  By convention:
          * For falsifiers (F1/F6/F9/F11/reciprocity/irreducibility):
            triggered = True iff the falsifier failed (the candidate
            was killed).
          * For catalog adapters: triggered = True iff the catalog
            *hit* (i.e. the polynomial was already known there, which
            kills the discovery claim).
          * For out_of_band: triggered = True iff M is outside the
            (1.001, 1.18) Salem-band.
    margin : float | None
        Continuous "margin to failure".  Sign convention: bigger
        positive margin = stronger kill / weaker survivor.  None when
        the margin wasn't captured (deferred — see KILL_VECTOR_SPEC).
    margin_unit : str | None
        One of MARGIN_UNITS, or None when margin is None.  Required for
        unit-aware magnitude reduction.
    metadata : dict
        Falsifier-specific extras (e.g. catalog match label, witness
        seed for F1, irreducibility factor count).  Free-form; consumers
        may rely on it being JSON-serialisable.
    """

    falsifier_name: str
    triggered: bool
    margin: Optional[float] = None
    margin_unit: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:  # type: ignore[override]
        # Frozen dataclass — bypass setattr for sanity-check side-effects.
        if self.margin is not None and self.margin_unit is None:
            object.__setattr__(self, "margin_unit", "absolute")
        if self.margin_unit is not None and self.margin_unit not in MARGIN_UNITS:
            raise ValueError(
                f"unknown margin_unit {self.margin_unit!r}; "
                f"must be one of {MARGIN_UNITS}"
            )

    def squashed(self) -> float:
        """[0, 1] saturated kill-strength for this component."""
        return _squash_margin(self.margin, self.margin_unit)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "falsifier_name": self.falsifier_name,
            "triggered": bool(self.triggered),
            "margin": (
                None if self.margin is None else float(self.margin)
            ),
            "margin_unit": self.margin_unit,
            "metadata": dict(self.metadata or {}),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "KillComponent":
        return cls(
            falsifier_name=str(d["falsifier_name"]),
            triggered=bool(d.get("triggered", False)),
            margin=(
                None if d.get("margin") is None else float(d["margin"])
            ),
            margin_unit=d.get("margin_unit"),
            metadata=dict(d.get("metadata") or {}),
        )


@dataclass(frozen=True)
class KillVector:
    """Vectorised falsifier outcome for one DISCOVERY_CANDIDATE.

    Attributes
    ----------
    components : tuple[KillComponent, ...]
        Ordered by falsifier-call order in the pipeline (band → cheap
        mechanical checks → catalog → F1/F6/F9/F11).  The order is the
        *navigation order*: when the learner consumes
        ``E[kill_vector | operator]``, the leftmost components are the
        cheapest to evaluate during greedy navigation.
    candidate_hash : str
        SHA-256 hash of (coeffs, M).  Ties this kill_vector back to a
        specific CLAIM in the kernel ledger.
    operator_class : str
        Identifier of the operator that produced the candidate (e.g.
        "DiscoveryEnv@degree=10/seed=0", "Lehmer-fuzz@v3").  Used by
        the Day-4 learner to bin candidates by operator for the
        directional-derivative estimator.
    region_meta : dict
        Region-level metadata: ``{"degree": 10, "alphabet": [-1,0,1],
        "env": "DiscoveryEnv", "reward_shape": "tier-3", "seed": 0,
        "episode_idx": 142}`` and similar.  Free-form so the substrate
        can grow extra coordinates over time.
    timestamp : float
        Unix epoch seconds at construction time.  Useful for
        chronological analysis when a single operator's behaviour
        changes mid-run.
    """

    components: Tuple[KillComponent, ...]
    candidate_hash: str
    operator_class: str = ""
    region_meta: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: time.time())

    # ------------------------------------------------------------------
    # Derived properties for backwards-compat & navigation
    # ------------------------------------------------------------------

    @property
    def first_triggered(self) -> Optional[KillComponent]:
        """First component whose ``triggered`` is True, in component
        order.  Equivalent to the old categorical kill_path: the
        pipeline's "first-failing" semantics is preserved."""
        for c in self.components:
            if c.triggered:
                return c
        return None

    def to_legacy_kill_path(self) -> Optional[str]:
        """Render the kill_vector to the legacy ``kill_path: str``
        format used by older pipeline records.  Returns None if no
        component triggered (i.e. the candidate would PROMOTE)."""
        c = self.first_triggered
        if c is None:
            return None
        # Reproduce the kill_pattern strings from discovery_pipeline._
        # process_candidate's Phase 2 ladder.
        name = c.falsifier_name
        meta = c.metadata or {}
        if name == "out_of_band":
            m = meta.get("M") or meta.get("mahler_measure") or "?"
            return f"out_of_band:M={m}_outside_(1.001,1.18)"
        if name == "reciprocity":
            return "reciprocity_failed"
        if name == "irreducibility":
            rat = str(meta.get("rationale", "reducible"))[:80]
            return f"reducible:{rat}"
        if name.startswith("catalog:"):
            cat = name.split(":", 1)[1]
            label = meta.get("match_label", "?")
            return f"known_in_catalog:matches {cat} entry {label}"
        if name == "F1_permutation_null":
            rat = str(meta.get("rationale", ""))[:80]
            return f"F1_kill:{rat}"
        if name == "F6_base_rate":
            rat = str(meta.get("rationale", ""))[:80]
            return f"F6_kill:{rat}"
        if name == "F9_simpler_explanation":
            rat = str(meta.get("rationale", ""))[:80]
            return f"F9_kill:{rat}"
        if name == "F11_cross_validation":
            rat = str(meta.get("rationale", ""))[:80]
            return f"F11_kill:{rat}"
        return f"{name}_kill"

    # ------------------------------------------------------------------
    # Magnitude (the scalar projection used by legacy code)
    # ------------------------------------------------------------------

    def magnitude(self, unit_aware: bool = True) -> float:
        """L2 norm over triggered components' margins.

        Parameters
        ----------
        unit_aware : bool, default True
            If True (recommended): each component's margin is squashed
            to [0, 1] before summing, making the magnitude unit-free
            and comparable across falsifiers.
            If False: raw L2 over numeric margins.  Mixes p_value and
            z_score scales — use only when components share a unit.

        Returns
        -------
        float
            Non-negative.  0.0 iff no component triggered (a would-be
            PROMOTE) OR every triggered component has no margin.
        """
        acc = 0.0
        for c in self.components:
            if not c.triggered:
                continue
            if unit_aware:
                v = c.squashed()
            else:
                if c.margin is None:
                    continue
                try:
                    v = float(c.margin)
                except (TypeError, ValueError):
                    continue
                if not math.isfinite(v):
                    # Skip non-finite margins for raw L2 (don't poison
                    # the norm with +inf).
                    continue
            acc += v * v
        return math.sqrt(acc)

    @property
    def triggered_count(self) -> int:
        return sum(1 for c in self.components if c.triggered)

    def get(self, name: str) -> Optional[KillComponent]:
        """Return the component named ``name``, or None if absent."""
        for c in self.components:
            if c.falsifier_name == name:
                return c
        return None

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "components": [c.to_dict() for c in self.components],
            "candidate_hash": self.candidate_hash,
            "operator_class": self.operator_class,
            "region_meta": dict(self.region_meta),
            "timestamp": float(self.timestamp),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "KillVector":
        comps = tuple(
            KillComponent.from_dict(c) for c in (d.get("components") or [])
        )
        return cls(
            components=comps,
            candidate_hash=str(d.get("candidate_hash", "")),
            operator_class=str(d.get("operator_class", "")),
            region_meta=dict(d.get("region_meta") or {}),
            timestamp=float(d.get("timestamp", 0.0) or 0.0),
        )

    @classmethod
    def from_json(cls, s: str) -> "KillVector":
        return cls.from_dict(json.loads(s))


# ---------------------------------------------------------------------------
# Margin-extraction helpers
# ---------------------------------------------------------------------------
#
# Each helper maps the pipeline's existing falsifier output (the
# (ok, rationale) tuple from discovery_pipeline._fX) into a KillComponent.
# Where the margin is "deferred" — i.e. would require re-running the
# falsifier with extra instrumentation to obtain — we set margin=None
# and document the deferral in KILL_VECTOR_SPEC.md.
#
# Cheap (computable from pipeline output without re-run):
#   * out_of_band               — margin = M - 1.18 (signed)
#   * reciprocity               — margin = max |c_i - c_{n-1-i}|
#   * irreducibility            — margin = factor count above degree 0
#                                  (parsed from rationale)
#   * F6_base_rate              — margin = #distinct_nonzero_values
#                                  (parsed from rationale, signed
#                                  vs threshold 2)
#   * F9_simpler_explanation    — margin = M - 1.001 (cyclotomic gap)
#   * F11_cross_validation      — margin = |M_a - M_b| from rationale
#                                  when present, else None
#   * catalog:*                 — margin = match_distance from
#                                  CatalogResult (if available)
#
# Deferred (requires pipeline re-run with extra instrumentation):
#   * F1_permutation_null margin = 1 - p_value
#       Today's ``_f1_permutation_null`` returns survived := observed_M
#       < median_perm_M.  The proper p-value would be the rank of the
#       observed M against the null distribution; computing it requires
#       larger N (≥ 1000 perms) than the MVP runs (30) and isn't surfaced
#       as a numeric in the rationale.  Deferred.
#
# All extractors are pure functions of the pipeline's existing output;
# adding them does NOT require changing discovery_pipeline.py's
# falsifier internals (only the wrapper that emits the KillVector).


def _coeff_reciprocity_margin(coeffs: List[int]) -> float:
    """Max |c_i - c_{n-1-i}| over coefficient pairs.  0 = palindromic."""
    n = len(coeffs)
    if n == 0:
        return 0.0
    return float(max(abs(coeffs[i] - coeffs[n - 1 - i]) for i in range(n // 2)))


def _f6_distinct_count_margin(rationale: str) -> Tuple[Optional[float], str]:
    """Parse the F6 rationale to extract the #distinct count.  The
    rationale strings are:

      * "F6: zero polynomial"
      * "F6: all-zero coefficients"
      * "F6: trivial coefficient structure (N distinct nonzero value)"
      * "F6: N distinct nonzero coefficient values"

    Returns ``(margin, unit)`` where margin is the signed gap to the
    threshold of 2 (positive = above threshold = passes; negative =
    below = killed).  None if we can't parse.
    """
    import re

    m = re.search(r"\((\d+) distinct nonzero value\)", rationale)
    if m:
        n = int(m.group(1))
        # margin = n - 2 (threshold).  Negative = trivial = killed.
        return float(n - 2), "z_score"
    m = re.search(r": (\d+) distinct nonzero coefficient values", rationale)
    if m:
        n = int(m.group(1))
        return float(n - 2), "z_score"
    return None, "z_score"


def _f11_drift_margin(rationale: str) -> Optional[float]:
    """Parse F11 rationale for either drift or cross-val numerics.

    Rationale shapes:
      * "F11: cross-val agrees within 1e-6 (V)"   — survived
      * "F11: cross-val mismatch A vs B"          — killed by mismatch
      * "F11: M drift A vs reported B"            — killed by drift
      * "F11: non-finite M in cross-val"          — killed
    """
    import re

    m = re.search(r"mismatch ([\d\.eE\-\+]+) vs ([\d\.eE\-\+]+)", rationale)
    if m:
        try:
            return abs(float(m.group(1)) - float(m.group(2)))
        except ValueError:
            return None
    m = re.search(r"drift ([\d\.eE\-\+]+) vs reported ([\d\.eE\-\+]+)", rationale)
    if m:
        try:
            return abs(float(m.group(1)) - float(m.group(2)))
        except ValueError:
            return None
    return None


def _irreducibility_factor_count(rationale: str) -> int:
    """Parse irreducibility rationale to count factors >= degree 1.

    Rationale shapes:
      * "sympy.factor_list: single factor, multiplicity 1"   — irreducible
      * "reducible: (f1)^a; (f2)^b; ..."                       — count factors
      * "zero polynomial"                                       — 0
      * "sympy unavailable; cannot verify irreducibility"       — 0
    """
    if "single factor" in rationale:
        return 0
    if rationale.startswith("reducible:"):
        body = rationale.split(":", 1)[1]
        return len([f for f in body.split(";") if f.strip()])
    return 0


# ---------------------------------------------------------------------------
# Build a KillVector from pipeline output
# ---------------------------------------------------------------------------


def kill_vector_from_pipeline_output(
    coeffs: List[int],
    mahler_measure: float,
    check_results: Dict[str, Any],
    candidate_hash: str,
    operator_class: str = "",
    region_meta: Optional[Dict[str, Any]] = None,
    catalog_results: Optional[Dict[str, Any]] = None,
    phase0_kill: bool = False,
) -> KillVector:
    """Construct a KillVector from a single ``DiscoveryPipeline.process_candidate`` call.

    Parameters
    ----------
    coeffs, mahler_measure : the candidate
    check_results : dict
        The ``DiscoveryRecord.check_results`` dict, as currently emitted
        by ``DiscoveryPipeline.process_candidate``.  Expected keys:
        "reciprocity", "irreducibility", "catalog_miss",
        "catalogs_checked", "F1", "F6", "F9", "F11" (each a (ok,
        rationale) tuple).  When phase0 fired, the dict has only a
        "phase" key; we emit a single out_of_band component.
    candidate_hash : str
        The candidate's hash (matches the kernel CLAIM).
    operator_class, region_meta : optional pass-through metadata.
    catalog_results : dict, optional
        If provided, the per-catalog ``CatalogResult`` results from
        ``run_consistency_check``.  When absent we still emit a single
        ``catalog:_aggregate`` component from check_results.
    phase0_kill : bool
        True iff the candidate was killed by the band check.  In that
        case check_results may have only ``{"phase": "phase0_band_check"}``.

    Returns
    -------
    KillVector
    """
    components: List[KillComponent] = []
    region_meta = dict(region_meta or {})

    # Component 1: out_of_band (phase 0 band check).
    in_band = 1.001 < mahler_measure < 1.18
    band_margin = 0.0
    if math.isfinite(mahler_measure):
        # Signed: positive margin = above 1.18; negative margin = below 1.001.
        if mahler_measure > 1.18:
            band_margin = mahler_measure - 1.18
        elif mahler_measure < 1.001:
            band_margin = mahler_measure - 1.001  # negative
        else:
            band_margin = 0.0
    else:
        band_margin = float("nan")
    components.append(KillComponent(
        falsifier_name="out_of_band",
        triggered=not in_band,
        margin=(
            None if not math.isfinite(band_margin) else float(band_margin)
        ),
        margin_unit="absolute",
        metadata={"M": mahler_measure},
    ))

    # If phase 0 killed, we don't have any further check_results entries;
    # short-circuit.
    if phase0_kill or "phase" in (check_results or {}):
        return KillVector(
            components=tuple(components),
            candidate_hash=candidate_hash,
            operator_class=operator_class,
            region_meta=region_meta,
        )

    # Component 2: reciprocity.
    recip_pair = check_results.get("reciprocity", (True, ""))
    recip_ok = bool(recip_pair[0]) if isinstance(recip_pair, tuple) else bool(recip_pair)
    components.append(KillComponent(
        falsifier_name="reciprocity",
        triggered=not recip_ok,
        margin=_coeff_reciprocity_margin(list(coeffs)),
        margin_unit="absolute",
        metadata={"rationale": str(recip_pair[1]) if isinstance(recip_pair, tuple) else ""},
    ))

    # Component 3: irreducibility.
    irred_pair = check_results.get("irreducibility", (True, ""))
    irred_ok = bool(irred_pair[0]) if isinstance(irred_pair, tuple) else bool(irred_pair)
    irred_rat = irred_pair[1] if isinstance(irred_pair, tuple) else ""
    components.append(KillComponent(
        falsifier_name="irreducibility",
        triggered=not irred_ok,
        margin=float(_irreducibility_factor_count(irred_rat)),
        margin_unit="absolute",
        metadata={"rationale": str(irred_rat)[:200]},
    ))

    # Components 4..8: catalog adapters.
    if catalog_results is not None:
        # Use the by_catalog dict from run_consistency_check.
        by_catalog = catalog_results.get("by_catalog") or {}
        for cat_name, result in by_catalog.items():
            # CatalogResult or dict
            if hasattr(result, "hit"):
                hit = bool(result.hit)
                dist = getattr(result, "match_distance", None)
                label = getattr(result, "match_label", None)
                err = getattr(result, "error", None)
            else:
                hit = bool(result.get("hit"))
                dist = result.get("match_distance")
                label = result.get("match_label")
                err = result.get("error")
            # margin: hit means distance ≈ 0 (kill is tight); miss means
            # the distance to the nearest entry, which we use as a
            # "how far from being known" proxy.  When the adapter
            # errored, mark margin None.
            if err is not None:
                margin: Optional[float] = None
            elif dist is not None:
                try:
                    margin = float(dist)
                except (TypeError, ValueError):
                    margin = None
            elif not hit:
                # miss without a numeric distance — set +inf so the
                # "very far from any entry" semantics is captured.
                margin = float("inf")
            else:
                margin = 0.0
            components.append(KillComponent(
                falsifier_name=f"catalog:{cat_name}",
                triggered=hit,
                margin=margin,
                margin_unit="hamming",
                metadata={
                    "match_label": label,
                    "error": err,
                },
            ))
    else:
        # Aggregated fallback: only emit one catalog component from
        # check_results["catalog_miss"].
        catmiss_pair = check_results.get("catalog_miss", (True, ""))
        catmiss = bool(catmiss_pair[0]) if isinstance(catmiss_pair, tuple) else True
        catmiss_rat = catmiss_pair[1] if isinstance(catmiss_pair, tuple) else ""
        components.append(KillComponent(
            falsifier_name="catalog:_aggregate",
            triggered=not catmiss,
            margin=(0.0 if not catmiss else float("inf")),
            margin_unit="hamming",
            metadata={"rationale": str(catmiss_rat)[:200]},
        ))

    # Component 9: F1_permutation_null.  Margin deferred — see module docstring.
    f1_pair = check_results.get("F1", (True, ""))
    f1_ok = bool(f1_pair[0]) if isinstance(f1_pair, tuple) else bool(f1_pair)
    f1_rat = f1_pair[1] if isinstance(f1_pair, tuple) else ""
    components.append(KillComponent(
        falsifier_name="F1_permutation_null",
        triggered=not f1_ok,
        margin=None,                       # DEFERRED
        margin_unit=None,
        metadata={"rationale": str(f1_rat)[:200], "deferred": True},
    ))

    # Component 10: F6_base_rate.
    f6_pair = check_results.get("F6", (True, ""))
    f6_ok = bool(f6_pair[0]) if isinstance(f6_pair, tuple) else bool(f6_pair)
    f6_rat = f6_pair[1] if isinstance(f6_pair, tuple) else ""
    f6_margin, f6_unit = _f6_distinct_count_margin(f6_rat)
    components.append(KillComponent(
        falsifier_name="F6_base_rate",
        triggered=not f6_ok,
        margin=f6_margin,
        margin_unit=(f6_unit if f6_margin is not None else None),
        metadata={"rationale": str(f6_rat)[:200]},
    ))

    # Component 11: F9_simpler_explanation.
    f9_pair = check_results.get("F9", (True, ""))
    f9_ok = bool(f9_pair[0]) if isinstance(f9_pair, tuple) else bool(f9_pair)
    f9_rat = f9_pair[1] if isinstance(f9_pair, tuple) else ""
    # Margin = M - 1.001 (cyclotomic gap; positive = comfortably non-cyclotomic).
    f9_margin: Optional[float] = None
    if math.isfinite(mahler_measure):
        f9_margin = float(mahler_measure - 1.001)
    components.append(KillComponent(
        falsifier_name="F9_simpler_explanation",
        triggered=not f9_ok,
        margin=f9_margin,
        margin_unit=("absolute" if f9_margin is not None else None),
        metadata={"rationale": str(f9_rat)[:200]},
    ))

    # Component 12: F11_cross_validation.
    f11_pair = check_results.get("F11", (True, ""))
    f11_ok = bool(f11_pair[0]) if isinstance(f11_pair, tuple) else bool(f11_pair)
    f11_rat = f11_pair[1] if isinstance(f11_pair, tuple) else ""
    f11_margin = _f11_drift_margin(f11_rat)
    components.append(KillComponent(
        falsifier_name="F11_cross_validation",
        triggered=not f11_ok,
        margin=f11_margin,
        margin_unit=("absolute" if f11_margin is not None else None),
        metadata={"rationale": str(f11_rat)[:200]},
    ))

    return KillVector(
        components=tuple(components),
        candidate_hash=candidate_hash,
        operator_class=operator_class,
        region_meta=region_meta,
    )


# ---------------------------------------------------------------------------
# Backfill: legacy DiscoveryRecord -> KillVector
# ---------------------------------------------------------------------------


def kill_vector_from_legacy(
    record: Dict[str, Any],
    operator_class: str = "",
    region_meta: Optional[Dict[str, Any]] = None,
) -> KillVector:
    """Reconstruct as much of a KillVector as possible from a legacy
    DiscoveryRecord-shaped dict (or a JSON record from the existing
    pilot logs).

    Expected keys in ``record``:

      * "candidate_hash" : str
      * "coeffs"         : list[int]
      * "mahler_measure" : float
      * "kill_pattern"   : str | None    (legacy categorical kill_path)
      * "check_results"  : dict          (optional; if present we use it)

    Where margins aren't computable from saved data we set
    ``margin=None`` rather than fabricating a value.  The returned
    KillVector is "lossy but consistent" with the legacy data: its
    ``to_legacy_kill_path()`` reproduces the original kill_pattern
    when no check_results dict is present.
    """
    coeffs = list(record.get("coeffs") or [])
    m = float(record.get("mahler_measure") or float("nan"))
    candidate_hash = str(record.get("candidate_hash") or "")
    kill_pattern: Optional[str] = record.get("kill_pattern")
    check_results = record.get("check_results")

    # Path 1: full check_results dict survived in the legacy record.
    if isinstance(check_results, dict) and check_results:
        return kill_vector_from_pipeline_output(
            coeffs=coeffs,
            mahler_measure=m,
            check_results=check_results,
            candidate_hash=candidate_hash,
            operator_class=operator_class,
            region_meta=region_meta,
            phase0_kill=("phase" in check_results),
        )

    # Path 2: only the legacy kill_pattern string is available.
    # Synthesise a minimal vector that at least round-trips to
    # to_legacy_kill_path().
    components: List[KillComponent] = []

    in_band = math.isfinite(m) and (1.001 < m < 1.18)
    band_margin = float("nan")
    if math.isfinite(m):
        if m > 1.18:
            band_margin = m - 1.18
        elif m < 1.001:
            band_margin = m - 1.001
        else:
            band_margin = 0.0
    components.append(KillComponent(
        falsifier_name="out_of_band",
        triggered=not in_band,
        margin=(None if not math.isfinite(band_margin) else float(band_margin)),
        margin_unit="absolute",
        metadata={"M": m},
    ))

    if kill_pattern:
        # Identify the kill from the pattern string.
        kp = kill_pattern
        if kp.startswith("out_of_band"):
            # Already captured above.
            pass
        elif kp.startswith("reciprocity"):
            components.append(KillComponent(
                falsifier_name="reciprocity",
                triggered=True,
                margin=_coeff_reciprocity_margin(coeffs),
                margin_unit="absolute",
                metadata={"legacy_kill_pattern": kp},
            ))
        elif kp.startswith("reducible"):
            components.append(KillComponent(
                falsifier_name="irreducibility",
                triggered=True,
                margin=None,
                margin_unit=None,
                metadata={"legacy_kill_pattern": kp},
            ))
        elif kp.startswith("known_in_catalog"):
            # Try to extract the catalog name from the pattern.
            cat = "_aggregate"
            for cat_candidate in (
                "Mossinghoff", "lehmer_literature", "LMFDB", "OEIS", "arXiv"
            ):
                if cat_candidate in kp:
                    cat = cat_candidate
                    break
            components.append(KillComponent(
                falsifier_name=f"catalog:{cat}",
                triggered=True,
                margin=0.0,
                margin_unit="hamming",
                metadata={"legacy_kill_pattern": kp},
            ))
        elif kp.startswith("F1_kill"):
            components.append(KillComponent(
                falsifier_name="F1_permutation_null",
                triggered=True,
                margin=None,
                margin_unit=None,
                metadata={"legacy_kill_pattern": kp, "deferred": True},
            ))
        elif kp.startswith("F6_kill"):
            components.append(KillComponent(
                falsifier_name="F6_base_rate",
                triggered=True,
                margin=None,
                margin_unit=None,
                metadata={"legacy_kill_pattern": kp},
            ))
        elif kp.startswith("F9_kill"):
            components.append(KillComponent(
                falsifier_name="F9_simpler_explanation",
                triggered=True,
                margin=None,
                margin_unit=None,
                metadata={"legacy_kill_pattern": kp},
            ))
        elif kp.startswith("F11_kill"):
            components.append(KillComponent(
                falsifier_name="F11_cross_validation",
                triggered=True,
                margin=None,
                margin_unit=None,
                metadata={"legacy_kill_pattern": kp},
            ))
        else:
            # Unknown pattern — emit a generic untyped killer so
            # to_legacy_kill_path round-trips.
            components.append(KillComponent(
                falsifier_name="legacy_unknown",
                triggered=True,
                margin=None,
                margin_unit=None,
                metadata={"legacy_kill_pattern": kp},
            ))

    return KillVector(
        components=tuple(components),
        candidate_hash=candidate_hash,
        operator_class=operator_class,
        region_meta=dict(region_meta or {}),
    )


# ---------------------------------------------------------------------------
# Aggregation (used by Day-4 learner inputs)
# ---------------------------------------------------------------------------


def aggregate_by_operator(
    vectors: List[KillVector],
) -> Dict[str, Dict[str, float]]:
    """Compute ``E[k_i | operator]`` over a corpus of KillVectors.

    Returns a nested dict::

        {
            operator_class: {
                falsifier_name: P(triggered=True | operator),
                ...,
                f"{falsifier_name}__mean_squashed": E[squashed_margin],
                f"__count": N,
            },
            ...
        }

    This is the directional-derivative input the Day-4 learner consumes.
    Implementation is intentionally simple (one pass, dict math) so it
    can run inside the kernel's read-path without dragging numpy in.
    """
    by_op: Dict[str, Dict[str, List[float]]] = {}
    counts: Dict[str, int] = {}

    for v in vectors:
        op = v.operator_class or "_unknown"
        bucket = by_op.setdefault(op, {})
        counts[op] = counts.get(op, 0) + 1
        for c in v.components:
            tk = bucket.setdefault(c.falsifier_name, [])
            tk.append(1.0 if c.triggered else 0.0)
            sk = bucket.setdefault(f"{c.falsifier_name}__squashed", [])
            sk.append(c.squashed())

    out: Dict[str, Dict[str, float]] = {}
    for op, bucket in by_op.items():
        d: Dict[str, float] = {"__count": float(counts.get(op, 0))}
        for k, vs in bucket.items():
            if vs:
                d[k] = sum(vs) / len(vs)
        out[op] = d
    return out


__all__ = [
    "KillComponent",
    "KillVector",
    "MARGIN_UNITS",
    "kill_vector_from_pipeline_output",
    "kill_vector_from_legacy",
    "aggregate_by_operator",
]
