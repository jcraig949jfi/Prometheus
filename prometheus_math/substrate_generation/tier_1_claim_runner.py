"""Tier-1 claim-stack runner — routes substrate-grade CLAIMs through
the kernel's CLAIM/FALSIFY/PROMOTE lifecycle and emits LearnerRecord
output.

Per pivot/claim_stack_design_2026-05-11.md + Aporia adjudication
2026-05-12. Day-1 baseline: schema + verifier dispatch wrapper + all
seven verifier slots stubbed (returning verifier_permanent_failure
with not_yet_implemented flag). Day 2 wires the four highest-leverage
verifiers (citation_audit, catalog_lookup, mpmath_compute,
substrate_self_check). Day 3 seed-author example claims.

The runner is INPUT-AGNOSTIC and PRODUCER-AGNOSTIC:
- Input: a JSONL file OR an in-memory list of claim payloads.
- Producer: hand-authored (Aporia) and mined (extractor) claims share
  the same shape; provenance lives descriptively in source_report.

Verifier dispatch wrapper (per Aporia Mod 2):
- Catches transient exceptions (network errors, timeouts, urlopen 503)
  → retries once → if still transient, returns verifier_transient_failure.
- Catches permanent exceptions (KeyError, ValueError, schema validation)
  → returns verifier_permanent_failure immediately.
- Verifier itself returns one of:
    decisive_verified | decisive_contradicted | decisive_inconclusive

Output: LearnerRecord per emitted opcode (1-3 records per claim
depending on whether PROMOTE fires), enriched with claim-specific
extension fields (claim_id, claim_category, expected_verdict,
actual_verdict, verifier_outcome_class).

CLI
---
::

    python -m prometheus_math.substrate_generation.tier_1_claim_runner \\
        --claim-batch path/to/claim_batch.jsonl \\
        --out-jsonl path/to/learner_records.jsonl \\
        --out-summary path/to/run_summary.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Verifier types + transient/permanent exception classification
# ---------------------------------------------------------------------------


# Per Aporia Mod Q4 + claim_stack_design §2: seven verifier slots.
KNOWN_VERIFIERS: Tuple[str, ...] = (
    "citation_audit",
    "catalog_lookup",
    "mpmath_compute",
    "sympy_factor",
    "triangulation",
    "substrate_self_check",
    "manual_review",
)


# Verdict the verifier returns. Distinct from the kernel's three-verdict
# vocabulary (verified/contradicted/inconclusive) and from the
# verifier_outcome_class enum on LearnerRecord. The runner translates
# decisive_* -> kernel verdict, and reports verifier_outcome_class
# directly to the LearnerRecord.
VERIFIER_DECISIVE_OUTCOMES: Tuple[str, ...] = (
    "decisive_verified",
    "decisive_contradicted",
    "decisive_inconclusive",
)


# Kernel verdict translation (per Aporia Mod Q3).
_DECISIVE_TO_KERNEL_VERDICT = {
    "decisive_verified": "verified",
    "decisive_contradicted": "contradicted",
    "decisive_inconclusive": "inconclusive",
}


@dataclass(frozen=True)
class VerifierResult:
    """Structured result returned by every verifier function."""
    outcome_class: str            # one of VERIFIER_OUTCOME_CLASSES
    evidence_blob: Optional[dict] = None
    runtime_ms: int = 0
    method_used: Optional[str] = None
    precision_dps: Optional[int] = None
    caveats: Optional[str] = None
    error_text: Optional[str] = None


# Exception classification. Network / I/O / 503-style failures retry once;
# everything else fails permanently. Conservative classification — when in
# doubt, treat as permanent (don't loop forever on a buggy verifier).
_TRANSIENT_EXC_TYPES: Tuple[type, ...] = (
    TimeoutError,
    ConnectionError,
    urllib.error.URLError,
    urllib.error.HTTPError,  # status checked separately for 5xx
    OSError,
)


def _classify_exception(exc: BaseException) -> str:
    """Returns 'transient' or 'permanent'. Per Aporia Mod 2: HTTP 5xx is
    transient (server side); 4xx is permanent (request shape problem).
    Network timeout / connection-reset is transient. Everything else
    permanent."""
    if isinstance(exc, urllib.error.HTTPError):
        # 5xx server side -> transient; 4xx client side -> permanent
        if 500 <= exc.code < 600:
            return "transient"
        return "permanent"
    if isinstance(exc, _TRANSIENT_EXC_TYPES):
        return "transient"
    return "permanent"


# ---------------------------------------------------------------------------
# Verifier dispatch wrapper
# ---------------------------------------------------------------------------


VerifierFn = Callable[[dict], VerifierResult]


def _dispatch_verifier(
    verifier_fn: VerifierFn,
    claim_payload: dict,
    *,
    transient_retry_count: int = 1,
) -> VerifierResult:
    """Wrap a verifier function with the transient-vs-permanent retry
    discipline (Aporia Mod 2). Default retries once on transient
    failure; permanent failures are decisive immediately.

    Verifier functions themselves should:
    - Return VerifierResult with one of the three decisive_* outcomes
      when execution completes cleanly.
    - Raise an exception if execution cannot complete; the wrapper
      classifies + retries.

    Verifier functions should NOT return verifier_transient_failure /
    verifier_permanent_failure themselves — those are the wrapper's job.
    """
    attempts_remaining = 1 + transient_retry_count
    last_exception: Optional[BaseException] = None
    while attempts_remaining > 0:
        attempts_remaining -= 1
        t_start = time.perf_counter()
        try:
            result = verifier_fn(claim_payload)
            if not isinstance(result, VerifierResult):
                # Defensive: verifier must return our typed result
                return VerifierResult(
                    outcome_class="verifier_permanent_failure",
                    runtime_ms=int((time.perf_counter() - t_start) * 1000),
                    error_text=(
                        f"verifier returned {type(result).__name__}, "
                        f"expected VerifierResult"
                    ),
                )
            if result.outcome_class not in VERIFIER_DECISIVE_OUTCOMES:
                return VerifierResult(
                    outcome_class="verifier_permanent_failure",
                    runtime_ms=int((time.perf_counter() - t_start) * 1000),
                    error_text=(
                        f"verifier returned outcome_class "
                        f"{result.outcome_class!r}; verifiers must return one "
                        f"of {VERIFIER_DECISIVE_OUTCOMES}"
                    ),
                )
            return result
        except BaseException as exc:  # noqa: BLE001
            last_exception = exc
            kind = _classify_exception(exc)
            if kind == "transient" and attempts_remaining > 0:
                # Brief backoff between attempts (polite-bot)
                time.sleep(0.5)
                continue
            elapsed_ms = int((time.perf_counter() - t_start) * 1000)
            outcome = (
                "verifier_transient_failure" if kind == "transient"
                else "verifier_permanent_failure"
            )
            return VerifierResult(
                outcome_class=outcome,
                runtime_ms=elapsed_ms,
                error_text=f"{type(exc).__name__}: {str(exc)[:240]}",
            )
    # Unreachable; the loop always returns
    return VerifierResult(
        outcome_class="verifier_permanent_failure",
        runtime_ms=0,
        error_text=f"dispatch loop exited without result; last exc: {last_exception!r}",
    )


# ---------------------------------------------------------------------------
# Verifier stubs (Day 1) — all return verifier_permanent_failure
# ---------------------------------------------------------------------------


def _verifier_stub_factory(name: str) -> VerifierFn:
    """Build a stub verifier that returns verifier_permanent_failure
    with not_yet_implemented flag. Day 2 replaces these with real
    verifier implementations for the four highest-leverage slots
    (citation_audit, catalog_lookup, mpmath_compute,
    substrate_self_check); Day 2+ replaces the rest."""
    def _stub(claim_payload: dict) -> VerifierResult:
        return VerifierResult(
            outcome_class="verifier_permanent_failure",
            evidence_blob={
                "verifier": name,
                "flag": "not_yet_implemented",
                "claim_id": claim_payload.get("id"),
            },
            runtime_ms=0,
            method_used=name,
            error_text=f"verifier {name!r} not yet implemented (Day 1 stub)",
        )
    _stub.__name__ = f"verifier_stub_{name}"
    return _stub


# ---------------------------------------------------------------------------
# citation_audit verifier (Track 2 Verifier 1, 2026-05-13)
# ---------------------------------------------------------------------------


# Permissive arXiv-ID extractor: finds arXiv:NNNN.NNNNN anywhere in the
# ground_truth_source string, so claims like "arXiv:1604.06431 (BIP 2019 J.
# AMS)" with parenthetical context after the ID still dispatch correctly.
_ARXIV_EXTRACT_RE = re.compile(r"\barXiv:(\d{4}\.\d{4,5})\b")
_ARXIV_ABS_URL = "https://arxiv.org/abs/{arxiv_id}"
_ARXIV_TIMEOUT_S = 12


def _verifier_citation_audit(claim_payload: dict) -> VerifierResult:
    """Citation-audit verifier.

    Strategy:
      1. Extract arXiv ID from ``ground_truth_source`` via permissive regex.
      2. HEAD-check the abstract page. Non-200 → decisive_contradicted.
      3. GET the abstract body. If 'withdrawn' or 'retracted' appears →
         decisive_contradicted. Otherwise decisive_verified.
      4. For DOI / free-form / non-arXiv citations: returns
         decisive_inconclusive so the dispatch wrapper can try a fallback
         verifier (catalog_lookup, manual_review).

    Network errors propagate as exceptions; the dispatch wrapper classifies
    them as transient and retries once.
    """
    gts = claim_payload.get("ground_truth_source", "")
    if not isinstance(gts, str) or not gts:
        return VerifierResult(
            outcome_class="decisive_inconclusive",
            method_used="citation_audit",
            evidence_blob={"reason": "no_ground_truth_source"},
            caveats="ground_truth_source missing or non-string; verifier cannot dispatch",
        )
    m = _ARXIV_EXTRACT_RE.search(gts)
    if not m:
        return VerifierResult(
            outcome_class="decisive_inconclusive",
            method_used="citation_audit",
            evidence_blob={
                "reason": "no_arxiv_id_extractable",
                "ground_truth_source_preview": gts[:120],
            },
            caveats=(
                "No arXiv ID found in ground_truth_source. citation_audit "
                "cannot verify DOI / free-form citations; fallback verifier "
                "(catalog_lookup or manual_review) should handle this."
            ),
        )
    arxiv_id = m.group(1)
    url = _ARXIV_ABS_URL.format(arxiv_id=arxiv_id)

    import urllib.request
    t_start = time.perf_counter()

    # 1. HEAD check
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=_ARXIV_TIMEOUT_S) as resp:
        head_code = resp.getcode()
    if head_code != 200:
        return VerifierResult(
            outcome_class="decisive_contradicted",
            method_used="citation_audit",
            evidence_blob={
                "arxiv_id": arxiv_id,
                "head_code": head_code,
                "reason": "arxiv_head_nonexistent",
            },
            runtime_ms=int((time.perf_counter() - t_start) * 1000),
            caveats=(
                f"arXiv:{arxiv_id} returned HTTP {head_code} (not 200). "
                "Citation does not resolve; expected_verifier author cited "
                "a hallucinated or removed paper."
            ),
        )

    # 2. Abstract-body withdrawal check
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=_ARXIV_TIMEOUT_S) as resp:
        body = resp.read().decode("utf-8", errors="replace").lower()
    runtime_ms = int((time.perf_counter() - t_start) * 1000)
    is_withdrawn = ("withdrawn" in body) or ("retracted" in body)
    if is_withdrawn:
        return VerifierResult(
            outcome_class="decisive_contradicted",
            method_used="citation_audit",
            evidence_blob={
                "arxiv_id": arxiv_id,
                "head_code": 200,
                "reason": "arxiv_withdrawn_or_retracted",
            },
            runtime_ms=runtime_ms,
            caveats=(
                f"arXiv:{arxiv_id} abstract contains withdrawn/retracted marker. "
                "Citation is not active; substrate falsifies any claim treating "
                "it as authoritative."
            ),
        )
    return VerifierResult(
        outcome_class="decisive_verified",
        method_used="citation_audit",
        evidence_blob={
            "arxiv_id": arxiv_id,
            "head_code": 200,
            "active": True,
        },
        runtime_ms=runtime_ms,
    )


# ---------------------------------------------------------------------------
# catalog_lookup verifier (Track 2 Verifier 2, 2026-05-13)
# ---------------------------------------------------------------------------


# T#NN catalog ID extractor — matches the claim_id pattern
# "CLAIM-boundary-T<N>-NNNNN" used by Aporia's boundary claims.
_BOUNDARY_T_ENTRY_RE = re.compile(r"^CLAIM-boundary-T(\d+)-\d{4,5}$")

# tensor_open_problems_v1.md catalog path + entry regex (mirrors
# validate_substrate_blocks.py's loader).
_TENSOR_CATALOG_PATH = Path("aporia/mathematics/tensor_open_problems_v1.md")
_T_ENTRY_RE = re.compile(r"^### (\d+)\.\s", re.MULTILINE)


def _load_tensor_catalog_entries() -> Dict[str, str]:
    """Parse tensor_open_problems_v1.md once. Returns {T#NN -> entry body}.

    Entry body is the markdown text from the entry's header to the next
    entry's header (or end of section). Caches per-process via a
    module-level singleton dict; the catalog file rarely changes within
    a single runner invocation.
    """
    if not _TENSOR_CATALOG_PATH.exists():
        return {}
    text = _TENSOR_CATALOG_PATH.read_text(encoding="utf-8")
    entries: Dict[str, str] = {}
    matches = list(_T_ENTRY_RE.finditer(text))
    for i, m in enumerate(matches):
        n = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        entries[f"T#{n}"] = text[start:end]
    return entries


_TENSOR_CATALOG_CACHE: Optional[Dict[str, str]] = None


def _get_tensor_catalog() -> Dict[str, str]:
    """Lazy-cached accessor; returns empty dict if the catalog file
    is unavailable."""
    global _TENSOR_CATALOG_CACHE
    if _TENSOR_CATALOG_CACHE is None:
        _TENSOR_CATALOG_CACHE = _load_tensor_catalog_entries()
    return _TENSOR_CATALOG_CACHE


def _extract_t_entry_id(claim_payload: dict) -> Optional[str]:
    """Determine the T#NN catalog entry ID this claim targets.

    Strategy:
      1. Explicit verifier_args.entry_id (e.g. {"entry_id": "T#4"})
      2. Derived from claim id pattern (CLAIM-boundary-T4-NNNNN -> T#4)
      3. None if neither applies — non-T# catalog dispatch
    """
    args = claim_payload.get("verifier_args", {}) or {}
    explicit = args.get("entry_id")
    if isinstance(explicit, str) and explicit.startswith("T#"):
        return explicit
    claim_id = claim_payload.get("id", "")
    m = _BOUNDARY_T_ENTRY_RE.match(claim_id)
    if m:
        return f"T#{m.group(1)}"
    return None


def _verifier_catalog_lookup(claim_payload: dict) -> VerifierResult:
    """Catalog-lookup verifier.

    Current scope (MVP, 2026-05-13):
      - Tensor catalog (aporia/mathematics/tensor_open_problems_v1.md):
        verifies the T#NN entry exists. If the claim targets a T#NN
        derived from claim_id or verifier_args.entry_id, looks up the
        catalog entry.
        - Entry missing -> decisive_contradicted (catalog miss; the claim
          references a catalog entry that doesn't exist)
        - Entry exists -> decisive_inconclusive (entry confirmed but
          numeric bound comparison is not yet wired; dispatch to fallback
          verifier or manual_review for the bound check)
      - Non-T# catalog dispatch (LMFDB, OEIS, Mossinghoff): returns
        decisive_inconclusive with a not_yet_wired flag. The dispatch
        wrapper can try a fallback verifier (citation_audit, manual_review).

    Network-free verifier — reads local catalog files only. No exceptions
    expected unless the catalog file is unreadable (permanent failure).
    """
    t_start = time.perf_counter()
    entry_id = _extract_t_entry_id(claim_payload)
    if entry_id is None:
        return VerifierResult(
            outcome_class="decisive_inconclusive",
            method_used="catalog_lookup",
            evidence_blob={
                "reason": "no_t_entry_id_extractable",
                "claim_id": claim_payload.get("id"),
                "note": (
                    "Non-tensor-catalog claims (LMFDB EC, OEIS, Mossinghoff) "
                    "need adapter wiring; falling back to inconclusive."
                ),
            },
            runtime_ms=int((time.perf_counter() - t_start) * 1000),
            caveats=(
                "catalog_lookup MVP only covers the tensor_open_problems "
                "catalog (T#NN entries). Non-T# claims should set "
                "expected_verifier_fallback to citation_audit or manual_review."
            ),
        )
    catalog = _get_tensor_catalog()
    if not catalog:
        return VerifierResult(
            outcome_class="verifier_permanent_failure",
            method_used="catalog_lookup",
            evidence_blob={
                "reason": "tensor_catalog_unavailable",
                "path": str(_TENSOR_CATALOG_PATH),
            },
            runtime_ms=int((time.perf_counter() - t_start) * 1000),
            error_text=(
                f"tensor catalog file not readable at "
                f"{_TENSOR_CATALOG_PATH} (cwd: {Path.cwd()})"
            ),
        )
    runtime_ms = int((time.perf_counter() - t_start) * 1000)
    if entry_id not in catalog:
        return VerifierResult(
            outcome_class="decisive_contradicted",
            method_used="catalog_lookup",
            evidence_blob={
                "entry_id": entry_id,
                "reason": "catalog_entry_missing",
                "catalog_size": len(catalog),
            },
            runtime_ms=runtime_ms,
            caveats=(
                f"{entry_id} not present in tensor_open_problems_v1.md. "
                "Claim references a catalog entry that doesn't exist."
            ),
        )
    entry_text = catalog[entry_id]
    return VerifierResult(
        outcome_class="decisive_inconclusive",
        method_used="catalog_lookup",
        evidence_blob={
            "entry_id": entry_id,
            "entry_body_chars": len(entry_text),
            "entry_preview": entry_text[:240],
            "reason": "entry_confirmed_but_bound_comparison_not_wired",
        },
        runtime_ms=runtime_ms,
        caveats=(
            f"{entry_id} catalog entry exists. MVP does not yet do "
            "numeric bound extraction + comparison; dispatch fallback "
            "verifier (citation_audit or manual_review) for the "
            "specific claim assertion."
        ),
    )


# ---------------------------------------------------------------------------
# mpmath_compute verifier (Track 2 Verifier 3, 2026-05-13)
# ---------------------------------------------------------------------------


# Calibration table: claim_id -> (coeffs_descending, expected_value, default_dps)
# Pre-registered numeric calibration anchors. MVP scope: Mahler-measure
# family. Future entries (Galois-group invariants, L-function special
# values, etc.) follow the same shape. Tolerance comes from
# verifier_args.tolerance per claim; default 1e-25 if absent.
_MPMATH_CALIBRATION_TABLE: Dict[str, Tuple[List[int], str, int]] = {
    # Lehmer's polynomial L(x) = x^10 + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1.
    # M(L) = 1.17628081825991750185... — the smallest known Mahler measure
    # greater than 1 of a monic integer polynomial. Lehmer 1933;
    # Mossinghoff polynomial database.
    "CLAIM-calibration-mahler-00001": (
        [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1],  # descending: x^10, x^9, ..., x^0
        "1.176280818259917506544070338474",       # M(L) at dps>=30
        30,
    ),
}


def _compute_mahler_measure(
    coeffs_descending: List[int], dps: int,
) -> Any:
    """Compute Mahler measure M(P) at the requested mpmath precision.

    M(P) = |a_n| * prod(max(1, |alpha_i|)) where alpha_i are the roots
    of P(x) and a_n is the leading coefficient. Returns an mpmath.mpf.
    """
    import mpmath as mp
    saved_dps = mp.mp.dps
    mp.mp.dps = dps + 5  # small headroom for cumulative rounding
    try:
        mp_coeffs = [mp.mpf(int(c)) for c in coeffs_descending]
        roots = mp.polyroots(mp_coeffs, maxsteps=300, extraprec=4 * dps)
        leading = abs(mp_coeffs[0])
        product = leading
        for r in roots:
            ar = abs(r)
            if ar > 1:
                product *= ar
        return +product  # force re-evaluation at saved precision
    finally:
        mp.mp.dps = saved_dps


def _verifier_mpmath_compute(claim_payload: dict) -> VerifierResult:
    """mpmath_compute verifier.

    MVP (2026-05-13): supports the Mahler-measure family via a small
    calibration table keyed by claim_id. The verifier:

      1. Looks up the claim_id in _MPMATH_CALIBRATION_TABLE. If absent,
         returns decisive_inconclusive (unsupported claim shape).
      2. Reads dps + tolerance from verifier_args (defaults: 30, 1e-25).
      3. Computes the calibration value at dps precision.
      4. Compares to the table's stored expected_value within tolerance.
         |computed - expected| <= tolerance -> decisive_verified;
         otherwise decisive_contradicted with the numeric discrepancy.

    Future extension: accept polynomial coefficients via verifier_args
    when the claim is parametric. For now the table covers the smoke
    target (CLAIM-calibration-mahler-00001) and similar pre-registered
    anchors; new anchors are added by Techne as substrate_self claims.
    """
    t_start = time.perf_counter()
    claim_id = claim_payload.get("id", "")
    if claim_id not in _MPMATH_CALIBRATION_TABLE:
        return VerifierResult(
            outcome_class="decisive_inconclusive",
            method_used="mpmath_compute",
            evidence_blob={
                "claim_id": claim_id,
                "reason": "no_calibration_entry",
                "supported_claim_ids": sorted(_MPMATH_CALIBRATION_TABLE.keys()),
            },
            runtime_ms=int((time.perf_counter() - t_start) * 1000),
            caveats=(
                "mpmath_compute MVP only handles pre-registered calibration "
                "anchors. Future versions will accept polynomial coefficients "
                "via verifier_args.coeffs."
            ),
        )
    coeffs, expected_str, default_dps = _MPMATH_CALIBRATION_TABLE[claim_id]
    args = claim_payload.get("verifier_args", {}) or {}
    dps = int(args.get("dps", default_dps))
    # tolerance may arrive as float or string ('1e-25'); coerce defensively
    tol_raw = args.get("tolerance", "1e-25")
    try:
        tolerance = float(tol_raw)
    except (TypeError, ValueError):
        return VerifierResult(
            outcome_class="verifier_permanent_failure",
            method_used="mpmath_compute",
            runtime_ms=int((time.perf_counter() - t_start) * 1000),
            error_text=f"verifier_args.tolerance not coercible to float: {tol_raw!r}",
        )

    import mpmath as mp
    saved_dps = mp.mp.dps
    mp.mp.dps = dps + 5
    try:
        computed = _compute_mahler_measure(coeffs, dps)
        expected = mp.mpf(expected_str)
        diff = abs(computed - expected)
        within = diff <= mp.mpf(tolerance)
    finally:
        mp.mp.dps = saved_dps
    runtime_ms = int((time.perf_counter() - t_start) * 1000)
    if within:
        return VerifierResult(
            outcome_class="decisive_verified",
            method_used="mpmath_compute",
            evidence_blob={
                "claim_id": claim_id,
                "computed": mp.nstr(computed, dps),
                "expected": expected_str,
                "diff": mp.nstr(diff, max(3, dps - 25)),
                "tolerance": str(tolerance),
                "dps": dps,
            },
            runtime_ms=runtime_ms,
            precision_dps=dps,
        )
    return VerifierResult(
        outcome_class="decisive_contradicted",
        method_used="mpmath_compute",
        evidence_blob={
            "claim_id": claim_id,
            "computed": mp.nstr(computed, dps),
            "expected": expected_str,
            "diff": mp.nstr(diff, dps),
            "tolerance": str(tolerance),
            "dps": dps,
            "reason": "computed_value_outside_tolerance",
        },
        runtime_ms=runtime_ms,
        precision_dps=dps,
        caveats=(
            f"Computed M = {mp.nstr(computed, dps)} differs from catalog "
            f"value by {mp.nstr(diff, dps)}, exceeding tolerance {tolerance}."
        ),
    )


# ---------------------------------------------------------------------------
# substrate_self_check verifier (Track 2 Verifier 4, 2026-05-13)
# ---------------------------------------------------------------------------


# Registry of substrate-self invariants. Each entry maps a short
# invariant_name -> a zero-arg callable returning True (invariant holds)
# or False (contradicted). Exceptions raised by the callable propagate
# as verifier_permanent_failure via the dispatch wrapper.
#
# Per claim_stack_design Q5 / adjudication 2026-05-12: substrate_self
# claims are Techne's authoring territory. Aporia's starter batch
# intentionally has none. This registry is the substrate's own
# self-falsification surface.
def _build_substrate_self_invariants() -> Dict[str, Callable[[], bool]]:
    """Construct the invariants dict. Built lazily to avoid import-time
    coupling — the invariants reference module-level constants whose
    imports cycle if defined at top-of-file."""
    from prometheus_math.substrate_generation.learner_enrichment import (
        VERIFIER_OUTCOME_CLASSES,
        EPISODE_PHASES,
        derive_kill_signature,
    )
    return {
        "verifier_outcome_classes_size_5": (
            lambda: len(VERIFIER_OUTCOME_CLASSES) == 5
        ),
        "episode_phases_size_5": (
            lambda: len(EPISODE_PHASES) == 5
        ),
        "kill_signature_survived_for_none": (
            lambda: derive_kill_signature(None) == ("survived",)
        ),
        "kill_signature_survived_for_empty_string": (
            lambda: derive_kill_signature("") == ("survived",)
        ),
        "known_verifiers_size_7": (
            lambda: len(KNOWN_VERIFIERS) == 7
        ),
        "decisive_outcomes_size_3": (
            lambda: len(VERIFIER_DECISIVE_OUTCOMES) == 3
        ),
    }


_SUBSTRATE_SELF_INVARIANTS_CACHE: Optional[Dict[str, Callable[[], bool]]] = None


def _get_substrate_self_invariants() -> Dict[str, Callable[[], bool]]:
    global _SUBSTRATE_SELF_INVARIANTS_CACHE
    if _SUBSTRATE_SELF_INVARIANTS_CACHE is None:
        _SUBSTRATE_SELF_INVARIANTS_CACHE = _build_substrate_self_invariants()
    return _SUBSTRATE_SELF_INVARIANTS_CACHE


def _verifier_substrate_self_check(claim_payload: dict) -> VerifierResult:
    """substrate_self_check verifier.

    Dispatches via ``verifier_args.invariant_name`` — claim selects a
    named invariant from the registry. Callable returning True is
    decisive_verified; False is decisive_contradicted (the substrate
    is falsifying its own asserted invariant — a real substrate-grade
    catch). Exceptions raised by the callable propagate so the dispatch
    wrapper classifies them as transient/permanent.

    Claims without verifier_args.invariant_name return
    decisive_inconclusive (unable to dispatch).

    Network-free.
    """
    t_start = time.perf_counter()
    args = claim_payload.get("verifier_args", {}) or {}
    invariant_name = args.get("invariant_name")
    invariants = _get_substrate_self_invariants()
    if not isinstance(invariant_name, str) or not invariant_name:
        return VerifierResult(
            outcome_class="decisive_inconclusive",
            method_used="substrate_self_check",
            evidence_blob={
                "reason": "no_invariant_name",
                "available_invariants": sorted(invariants.keys()),
            },
            runtime_ms=int((time.perf_counter() - t_start) * 1000),
            caveats=(
                "substrate_self_check requires verifier_args.invariant_name. "
                "Available invariants are in evidence_blob.available_invariants."
            ),
        )
    if invariant_name not in invariants:
        return VerifierResult(
            outcome_class="decisive_inconclusive",
            method_used="substrate_self_check",
            evidence_blob={
                "reason": "unknown_invariant_name",
                "invariant_name": invariant_name,
                "available_invariants": sorted(invariants.keys()),
            },
            runtime_ms=int((time.perf_counter() - t_start) * 1000),
            caveats=(
                f"Invariant {invariant_name!r} not in substrate-self registry. "
                "Register it via _build_substrate_self_invariants or fix the "
                "claim's verifier_args."
            ),
        )
    holds = invariants[invariant_name]()  # may raise -> dispatch wrapper
    runtime_ms = int((time.perf_counter() - t_start) * 1000)
    if not isinstance(holds, bool):
        return VerifierResult(
            outcome_class="verifier_permanent_failure",
            method_used="substrate_self_check",
            runtime_ms=runtime_ms,
            error_text=(
                f"invariant {invariant_name!r} returned non-bool "
                f"{type(holds).__name__}: {holds!r}"
            ),
        )
    if holds:
        return VerifierResult(
            outcome_class="decisive_verified",
            method_used="substrate_self_check",
            evidence_blob={
                "invariant_name": invariant_name,
                "holds": True,
            },
            runtime_ms=runtime_ms,
        )
    return VerifierResult(
        outcome_class="decisive_contradicted",
        method_used="substrate_self_check",
        evidence_blob={
            "invariant_name": invariant_name,
            "holds": False,
            "reason": "substrate_self_invariant_violated",
        },
        runtime_ms=runtime_ms,
        caveats=(
            f"Substrate-self invariant {invariant_name!r} returned False. "
            "The substrate is falsifying its own asserted invariant — "
            "this is a real substrate-grade catch and requires investigation."
        ),
    )


VERIFIER_REGISTRY: Dict[str, VerifierFn] = {
    name: _verifier_stub_factory(name) for name in KNOWN_VERIFIERS
}
VERIFIER_REGISTRY["citation_audit"] = _verifier_citation_audit
VERIFIER_REGISTRY["catalog_lookup"] = _verifier_catalog_lookup
VERIFIER_REGISTRY["mpmath_compute"] = _verifier_mpmath_compute
VERIFIER_REGISTRY["substrate_self_check"] = _verifier_substrate_self_check


def get_verifier(name: str) -> VerifierFn:
    """Look up the verifier function for a given name. Raises ValueError
    on unknown verifier names (substrate-grade typed-error discipline)."""
    if name not in VERIFIER_REGISTRY:
        raise ValueError(
            f"unknown verifier {name!r}; must be one of {KNOWN_VERIFIERS}"
        )
    return VERIFIER_REGISTRY[name]


# ---------------------------------------------------------------------------
# DiscoveryRecord-shaped lite struct for enrich() compatibility
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _ClaimRecordForEnrich:
    """Duck-typed object passed to learner_enrichment.enrich(). enrich()
    reads candidate_hash + terminal_state + kill_pattern via getattr; we
    construct one of these per claim/phase to feed it."""
    candidate_hash: str
    terminal_state: str
    kill_pattern: Optional[str]


# Mapping from VerifierResult.outcome_class to LearnerRecord
# terminal_state (the existing OUTCOME_CLASSES vocabulary). The kernel
# verdict translation is separate (handled when emitting kernel.FALSIFY).
_VERIFIER_OUTCOME_TO_TERMINAL_STATE = {
    "decisive_verified": "PROMOTED",
    "decisive_contradicted": "REJECTED",
    "decisive_inconclusive": "SURVIVED",  # genuine inconclusive — Learner sees as "alive" claim
    "verifier_transient_failure": "ERROR",
    "verifier_permanent_failure": "ERROR",
}


# ---------------------------------------------------------------------------
# Top-level run loop
# ---------------------------------------------------------------------------


@dataclass
class ClaimRunResult:
    """Per-claim execution summary."""
    claim_id: str
    claim_category: str
    expected_verdict: str
    actual_verdict: str           # the verifier's verdict (decisive_* or verifier_*_failure)
    verifier_used: str            # primary or fallback name
    runtime_ms: int
    learner_records_emitted: int  # 1-3 per claim (CLAIM, FALSIFY, optionally PROMOTE)
    expected_actual_match: bool   # expected_verdict == actual_verdict mapping
    error_text: Optional[str] = None


def _verdict_match(expected: str, actual_outcome_class: str) -> bool:
    """Does the verifier's outcome_class match the author's expected_verdict?
    Per claim_stack_design + Aporia Mod 2: expected 'survived' matches
    decisive_verified; 'falsified' matches decisive_contradicted; 'open'
    matches decisive_inconclusive; 'conditional' matches decisive_inconclusive
    (with caveats). Failures (transient or permanent) never match — they're
    missing data."""
    mapping = {
        "survived": "decisive_verified",
        "falsified": "decisive_contradicted",
        "open": "decisive_inconclusive",
        "conditional": "decisive_inconclusive",
    }
    return mapping.get(expected) == actual_outcome_class


def run_claim(
    claim_payload: dict,
    *,
    kernel: Optional[Any] = None,
    chart_registry: Optional[Any] = None,
    emit_kernel_opcodes: bool = True,
) -> Tuple[ClaimRunResult, List[Any]]:
    """Run one claim through the verifier dispatch + (optionally) emit
    kernel opcodes + return the LearnerRecord(s) generated.

    Parameters
    ----------
    claim_payload : dict
        Validated claim block (per claim_v1.json schema).
    kernel : SigmaKernel | None
        Substrate kernel handle for CLAIM/FALSIFY/PROMOTE emissions.
        When None, opcode emission is skipped (test mode); only the
        verifier dispatch + LearnerRecord enrichment runs.
    chart_registry : ChartRegistry | None
        Passed through to learner_enrichment.enrich().
    emit_kernel_opcodes : bool
        Toggle for opcode emission. Default True; tests pass False.

    Returns (ClaimRunResult, List[LearnerRecord]).
    """
    # Lazy import — keep the runner standalone-importable
    from prometheus_math.substrate_generation.learner_enrichment import enrich

    primary_name = claim_payload["expected_verifier_primary"]
    fallback_name = claim_payload.get("expected_verifier_fallback")
    expected_verdict = claim_payload["expected_verdict"]
    claim_id = claim_payload["id"]
    claim_category = claim_payload["claim_category"]

    t_start = time.perf_counter()

    # 1. Try primary verifier
    primary_result = _dispatch_verifier(get_verifier(primary_name), claim_payload)
    chosen_verifier_name = primary_name
    chosen_result = primary_result

    # 2. If primary returned inconclusive / transient_failure, try fallback (if any)
    if (
        fallback_name
        and primary_result.outcome_class in ("decisive_inconclusive", "verifier_transient_failure")
    ):
        fallback_result = _dispatch_verifier(get_verifier(fallback_name), claim_payload)
        # Use fallback only if it's MORE decisive than primary
        # (decisive_* > verifier_*_failure; among decisive, prefer non-inconclusive)
        if (
            fallback_result.outcome_class in ("decisive_verified", "decisive_contradicted")
            or (
                primary_result.outcome_class == "verifier_transient_failure"
                and fallback_result.outcome_class.startswith("decisive_")
            )
        ):
            chosen_verifier_name = fallback_name
            chosen_result = fallback_result

    elapsed_ms = int((time.perf_counter() - t_start) * 1000)

    # 3. Translate verifier outcome to terminal_state for the
    # DiscoveryRecord-shaped lite struct that enrich() consumes
    terminal_state = _VERIFIER_OUTCOME_TO_TERMINAL_STATE.get(
        chosen_result.outcome_class, "ERROR",
    )
    # kill_pattern: derive from outcome + claim provenance so the
    # existing derive_kill_signature() can produce a useful tuple. For
    # claims, use the claim_id as the kill_pattern body so the signature
    # tuple is anti-leakage by construction (claim IDs are categorical,
    # not literal coefficient data).
    if chosen_result.outcome_class == "decisive_contradicted":
        kill_pattern = f"claim_falsified:{claim_category}"
    elif chosen_result.outcome_class == "decisive_inconclusive":
        kill_pattern = f"claim_inconclusive:{claim_category}"
    elif chosen_result.outcome_class.endswith("_failure"):
        kill_pattern = f"claim_verifier_failure:{chosen_result.outcome_class}"
    else:
        kill_pattern = None  # decisive_verified -> no kill

    # 4. Build LearnerRecord(s) — one per emitted opcode phase
    # Day-1 baseline emits one LearnerRecord per claim with phase=
    # "evaluate" (single-phase). Tier-2+ enhancement emits separate
    # records for claim / falsify / promote phases when kernel opcodes
    # are wired through.
    lite_record = _ClaimRecordForEnrich(
        candidate_hash=claim_id,
        terminal_state=terminal_state,
        kill_pattern=kill_pattern,
    )
    verifier_outcome_class = chosen_result.outcome_class
    learner_record = enrich(
        lite_record,
        chart_id=None,  # claim-stack records don't have a chart yet
        chart_registry=chart_registry,
        decoy_kind=None,
        episode_phase="evaluate",
        verifier_outcome_class=verifier_outcome_class,
        claim_id=claim_id,
        claim_category=claim_category,
        actual_verdict=chosen_result.outcome_class,
    )

    # 5. Optionally emit kernel opcodes (Day 2 enhancement; Day 1 stub)
    if emit_kernel_opcodes and kernel is not None:
        _emit_kernel_opcodes_for_claim(
            kernel, claim_payload, chosen_result, terminal_state,
        )

    result = ClaimRunResult(
        claim_id=claim_id,
        claim_category=claim_category,
        expected_verdict=expected_verdict,
        actual_verdict=chosen_result.outcome_class,
        verifier_used=chosen_verifier_name,
        runtime_ms=elapsed_ms,
        learner_records_emitted=1,  # Day-1 baseline; Tier-2 may emit 3
        expected_actual_match=_verdict_match(expected_verdict, chosen_result.outcome_class),
        error_text=chosen_result.error_text,
    )
    return result, [learner_record]


def _emit_kernel_opcodes_for_claim(
    kernel: Any, claim_payload: dict, verifier_result: VerifierResult,
    terminal_state: str,
) -> None:
    """Emit kernel.CLAIM / .FALSIFY / .PROMOTE opcodes for this claim.

    Day-1 stub: not implemented. Day 2+: wires through. Kept as a
    stand-alone function so the run_claim flow is testable without
    kernel side-effects.
    """
    # TODO(Day 2): wire kernel.CLAIM with target_name, hypothesis,
    # evidence dict, kill_path. Translate verifier_result.outcome_class
    # to kernel verdict via _DECISIVE_TO_KERNEL_VERDICT for FALSIFY.
    # PROMOTE only on decisive_verified.
    return


# ---------------------------------------------------------------------------
# Batch loader + quality-discipline enforcement (Rules A/B/C)
# ---------------------------------------------------------------------------


def load_claim_batch(
    batch_path: Path,
    *,
    enforce_quality_rules: bool = True,
) -> List[dict]:
    """Load a JSONL batch of claim payloads. Optionally enforce the
    quality-discipline rules (claim_stack_design §5 Rules A/B/C):
      - A: per-batch diversity (>=3 categories OR <10 claims)
      - B: per-batch verdict mix (40/25/25/10 ratio guidance; loose check)
      - C: per-batch trust-tier balance (ml_predicted <= 10%;
           analytically_proven + numerically_certified >= 70%)

    Rule A is strict for batches >= 10 claims (smaller batches are
    allowed to be uniform).
    Rule B is GUIDANCE not enforcement (loose threshold: at least one
    distinct verdict value).
    Rule C is strict (anti-murmuration discipline).
    """
    if not batch_path.exists():
        raise FileNotFoundError(f"claim batch not found: {batch_path}")
    payloads: List[dict] = []
    for line in batch_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payloads.append(json.loads(line))
    if enforce_quality_rules:
        _enforce_quality_rules(payloads)
    return payloads


def _enforce_quality_rules(payloads: List[dict]) -> None:
    """Validate quality rules on the batch. Raises ValueError on
    violation with a reason message identifying which rule and which
    claims violated."""
    n = len(payloads)
    if n == 0:
        raise ValueError("batch is empty")
    # Rule A — diversity
    categories = {p.get("claim_category") for p in payloads}
    if n >= 10 and len(categories - {None}) < 3:
        raise ValueError(
            f"Rule A violation: batch of {n} claims spans only "
            f"{len(categories)} categories ({sorted(categories)!s}); need >=3 "
            f"per claim_stack_design §5 Rule A"
        )
    # Rule B — verdict diversity (loose: at least 2 distinct verdicts)
    verdicts = {p.get("expected_verdict") for p in payloads}
    if n >= 10 and len(verdicts - {None}) < 2:
        raise ValueError(
            f"Rule B violation: batch of {n} claims has only "
            f"{len(verdicts)} distinct expected_verdicts ({sorted(verdicts)!s}); "
            f"need >=2 per claim_stack_design §5 Rule B"
        )
    # Rule C — trust-tier balance (strict)
    trust_counts: Dict[str, int] = {}
    for p in payloads:
        t = p.get("trust_tier", "unverified")
        trust_counts[t] = trust_counts.get(t, 0) + 1
    ml_count = trust_counts.get("ml_predicted", 0)
    if n > 0 and (ml_count / n) > 0.10:
        raise ValueError(
            f"Rule C violation: ml_predicted claims are {ml_count}/{n} "
            f"({100*ml_count/n:.1f}%); must be <=10% per Rule C "
            f"(anti-murmuration discipline)"
        )
    proven_count = (
        trust_counts.get("analytically_proven", 0)
        + trust_counts.get("numerically_certified", 0)
    )
    if n >= 10 and (proven_count / n) < 0.70:
        raise ValueError(
            f"Rule C violation: analytically_proven + numerically_certified "
            f"claims are {proven_count}/{n} ({100*proven_count/n:.1f}%); "
            f"must be >=70% per Rule C"
        )


# ---------------------------------------------------------------------------
# Top-level batch run
# ---------------------------------------------------------------------------


def run_claim_batch(
    batch_path: Path,
    *,
    out_jsonl: Optional[Path] = None,
    out_summary: Optional[Path] = None,
    kernel: Optional[Any] = None,
    enforce_quality_rules: bool = True,
) -> Dict[str, Any]:
    """Run a full batch of claims; emit LearnerRecord JSONL + run summary."""
    payloads = load_claim_batch(batch_path, enforce_quality_rules=enforce_quality_rules)
    results: List[ClaimRunResult] = []
    learner_records: List[Any] = []
    t_start = time.perf_counter()
    for payload in payloads:
        result, records = run_claim(
            payload, kernel=kernel,
            emit_kernel_opcodes=(kernel is not None),
        )
        results.append(result)
        learner_records.extend(records)
    elapsed_total_s = time.perf_counter() - t_start

    # Emit JSONL of LearnerRecords
    if out_jsonl:
        out_jsonl.parent.mkdir(parents=True, exist_ok=True)
        with open(out_jsonl, "w", encoding="utf-8") as f:
            for r in learner_records:
                f.write(json.dumps(_learner_record_to_dict(r)) + "\n")

    # Compute summary stats
    outcome_counts: Dict[str, int] = {}
    expected_counts: Dict[str, int] = {}
    actual_counts: Dict[str, int] = {}
    match_count = 0
    for r in results:
        expected_counts[r.expected_verdict] = expected_counts.get(r.expected_verdict, 0) + 1
        actual_counts[r.actual_verdict] = actual_counts.get(r.actual_verdict, 0) + 1
        outcome_counts[r.actual_verdict] = outcome_counts.get(r.actual_verdict, 0) + 1
        if r.expected_actual_match:
            match_count += 1

    summary = {
        "batch_path": str(batch_path).replace("\\", "/"),
        "n_claims": len(payloads),
        "n_learner_records": len(learner_records),
        "elapsed_total_s": round(elapsed_total_s, 3),
        "expected_verdict_distribution": expected_counts,
        "actual_verdict_distribution": actual_counts,
        "expected_actual_match_count": match_count,
        "expected_actual_match_rate": (
            round(match_count / max(1, len(results)), 4)
        ),
        "verifier_outcome_distribution": outcome_counts,
        "transient_failure_count": outcome_counts.get("verifier_transient_failure", 0),
        "permanent_failure_count": outcome_counts.get("verifier_permanent_failure", 0),
        # Per Aporia Mod 2 + Q7: separate health flags
        "health_flag_any_inconclusive_over_20pct": (
            (outcome_counts.get("decisive_inconclusive", 0)
             + outcome_counts.get("verifier_transient_failure", 0)
             + outcome_counts.get("verifier_permanent_failure", 0)) / max(1, len(results))
            > 0.20
        ),
        "health_flag_transient_failure_over_10pct": (
            outcome_counts.get("verifier_transient_failure", 0) / max(1, len(results))
            > 0.10
        ),
    }
    if out_summary:
        out_summary.parent.mkdir(parents=True, exist_ok=True)
        out_summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _learner_record_to_dict(r: Any) -> Dict[str, Any]:
    return {
        "underlying_record_hash": r.underlying_record_hash,
        "episode_id": r.episode_id,
        "episode_phase": r.episode_phase,
        "verification_tier": r.verification_tier,
        "chart_id": r.chart_id,
        "decoy_kind": r.decoy_kind,
        "kill_signature": list(r.kill_signature),
        "outcome_class": r.outcome_class,
        "verifier_outcome_class": r.verifier_outcome_class,
        "claim_id": r.claim_id,
        "claim_category": r.claim_category,
        "actual_verdict": r.actual_verdict,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="tier_1_claim_runner",
        description=(
            "Run a JSONL batch of substrate-grade claims through the "
            "claim_v1 schema's verifier dispatch + emit LearnerRecord output. "
            "Day-1 baseline: all 7 verifiers stubbed (return "
            "verifier_permanent_failure). Day 2+ wires real verifiers."
        ),
    )
    p.add_argument("--claim-batch", required=True, type=Path,
                   help="Input JSONL batch of validated claim payloads")
    p.add_argument("--out-jsonl", type=Path, default=None,
                   help="Output LearnerRecord JSONL (one record per line)")
    p.add_argument("--out-summary", type=Path, default=None,
                   help="Output run summary JSON")
    p.add_argument("--no-quality-rules", action="store_true",
                   help="Skip Rules A/B/C enforcement (smoke / debug mode)")
    args = p.parse_args(argv)

    summary = run_claim_batch(
        args.claim_batch,
        out_jsonl=args.out_jsonl,
        out_summary=args.out_summary,
        kernel=None,  # Day-1: no kernel emission
        enforce_quality_rules=(not args.no_quality_rules),
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
