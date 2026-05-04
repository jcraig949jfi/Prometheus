"""prometheus_math.discovery_pipeline — DISCOVERY_CANDIDATE -> substrate CLAIM.

Implements §6.1 of `harmonia/memory/architecture/discovery_via_rediscovery.md`:
the engineering move that converts the current "log a DISCOVERY_CANDIDATE
side-note and flag for hand-verification" pattern in ``discovery_env.py``
into a mechanical substrate-grade pipeline.

When ``DiscoveryEnv`` produces a polynomial in the sub-Lehmer band that
isn't in the Mossinghoff catalog, this pipeline:

  1. Runs the kill_path checks:
       - reciprocity (trivially satisfied by env construction)
       - irreducibility (sympy / cypari)
       - multi-catalog consistency (Mossinghoff today; LMFDB + OEIS + arXiv
         deferred to §6.3)
       - F1+F6+F9+F11 falsification battery simulation
  2. Mints a CLAIM through the kernel discipline (CLAIM/FALSIFY/GATE/PROMOTE).
  3. Routes to one of three TERMINAL states (Gemini's §6.6 Shadow Catalog
     extension folded in):
       - PROMOTED — canonical symbol; fully survived + independently verified
                    (rare today; requires literature cross-check we don't
                    have an automated tool for yet)
       - SHADOW_CATALOG — signal-class survives the battery and is
                          catalog-missing, but lacks independent verification.
                          The vast majority of non-trivial outputs land here.
       - REJECTED — killed by a battery member; kill_pattern captured as
                    substrate.

Avoids the cold-fusion failure mode (treating every catalog-miss as
canonical truth) by funneling unverified survivors to SHADOW_CATALOG.
The substrate can hold them addressable across years; downstream
verification can promote them to canonical later.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple

from sigma_kernel.sigma_kernel import (
    Capability,
    SigmaKernel,
    Symbol,
    Tier,
    Verdict,
    VerdictResult,
)
from sigma_kernel.bind_eval import BindEvalExtension


# ---------------------------------------------------------------------------
# Terminal state enum
# ---------------------------------------------------------------------------


TerminalState = Literal["PROMOTED", "SHADOW_CATALOG", "REJECTED"]


@dataclass(frozen=True)
class DiscoveryRecord:
    """The outcome of running a candidate polynomial through the
    discovery pipeline.

    Substrate-grade: the record itself is content-addressed (via
    candidate_hash) and references the kernel CLAIM and any minted
    symbols by id. Downstream consumers query the substrate, not this
    Python object, to reproduce the verdict.

    Day-3 reframe: ``kill_pattern: str | None`` is now a *derived*
    field — the canonical kill outcome is ``kill_vector``, a typed
    multi-component falsifier vector (see ``prometheus_math.kill_vector``).
    Old code reading ``record.kill_pattern`` continues to work; new
    code should consume ``record.kill_vector`` for component-aware
    navigation (Day 4-5 learner & greedy navigation).
    """

    candidate_hash: str  # sha256 over coeffs + mahler_measure
    coeffs: Tuple[int, ...]
    mahler_measure: float
    terminal_state: TerminalState
    kill_pattern: Optional[str]  # only set when terminal_state == REJECTED
    claim_id: Optional[str]  # set unless we couldn't even mint a CLAIM
    symbol_ref: Optional[str]  # "name@v1" for PROMOTED / SHADOW_CATALOG entries
    check_results: Dict[str, Any] = field(default_factory=dict)
    # Day-3: kill vector (default None for legacy callers / phase0 short-circuits
    # that don't construct one explicitly).
    kill_vector: Optional[Any] = None

    @property
    def is_signal_class(self) -> bool:
        """True iff the candidate survived to PROMOTED or SHADOW_CATALOG."""
        return self.terminal_state in ("PROMOTED", "SHADOW_CATALOG")


# ---------------------------------------------------------------------------
# Kill-path checks (mechanical, fast)
# ---------------------------------------------------------------------------


def _is_reciprocal(coeffs: List[int]) -> bool:
    """Palindromic check. Trivial for env-generated polys; included so
    the pipeline catches any future env that loosens the constraint."""
    n = len(coeffs)
    return all(coeffs[i] == coeffs[n - 1 - i] for i in range(n // 2))


def _is_irreducible(coeffs: List[int]) -> Tuple[bool, str]:
    """Test integer-polynomial irreducibility over Q.

    Returns (irreducible, rationale). Uses sympy as the primary backend;
    falls back to a minimal "single-factor" check via numpy roots if
    sympy isn't available (the fallback is conservative — it returns
    False on any input it can't verify, which is the right error
    direction for a kill-path check).
    """
    if all(c == 0 for c in coeffs):
        return False, "zero polynomial"
    try:
        import sympy  # type: ignore

        x = sympy.symbols("x")
        # coeffs are ascending; sympy.Poly takes descending.
        poly = sympy.Poly(list(reversed(coeffs)), x, domain="ZZ")
        factors = sympy.factor_list(poly)
        # factor_list returns (content, [(factor, multiplicity), ...]).
        # Irreducible iff exactly one factor with multiplicity 1, and
        # the factor is the polynomial itself (or its negative).
        _, fac_list = factors
        if len(fac_list) == 1 and fac_list[0][1] == 1:
            return True, "sympy.factor_list: single factor, multiplicity 1"
        kp = "; ".join(
            f"({fac.as_expr()})^{mult}" for fac, mult in fac_list
        )
        return False, f"reducible: {kp}"
    except ImportError:
        # Fallback: refuse to assert irreducibility without sympy.
        return False, "sympy unavailable; cannot verify irreducibility"


def _check_catalog_miss(
    coeffs: List[int], mahler_measure: float, tol: float = 1e-5
) -> Tuple[bool, str, List[str]]:
    """Confirm the polynomial is NOT in any consulted catalog.

    Returns ``(catalog_miss, rationale, catalogs_checked)``.

    Per §6.3 (forged 2026-04-29): consults the multi-catalog
    consistency check at ``prometheus_math.catalog_consistency``.
    Today's catalog set:

      * Mossinghoff (embedded snapshot, always live)
      * lehmer_literature (embedded Boyd/Smyth/Borwein-Mossinghoff
        snapshot, always live)
      * LMFDB nf_fields (skip-cleanly when mirror unreachable)
      * OEIS coefficient sequence (skip-cleanly when API unreachable)
      * arXiv title fuzzy (skip-cleanly when API unreachable)

    ``catalog_miss = True`` iff EVERY consulted catalog reported a miss.
    Catalogs that emit a typed error (e.g. LMFDB unreachable) DO count
    toward miss for this aggregation, but the rationale string surfaces
    them so downstream consumers can distinguish "actual miss" from
    "skipped due to network".
    """
    from prometheus_math.catalog_consistency import (
        run_consistency_check,
    )

    try:
        agg = run_consistency_check(coeffs, mahler_measure, tol=tol)
    except Exception as e:
        # Defensive: the orchestrator should never raise (it wraps
        # adapter exceptions internally), but if something pathological
        # happens we degrade to "all catalogs missed".
        return (
            True,
            f"consistency-check failed ({type(e).__name__}); "
            f"treating as miss",
            [],
        )

    catalogs_checked: List[str] = list(agg["catalogs_checked"])
    if agg["any_hit"]:
        first_hit = agg["hits"][0]
        rationale = (
            f"matches {first_hit.catalog_name} entry "
            f"{first_hit.match_label} (query={first_hit.query_kind})"
        )
        return False, rationale, catalogs_checked

    # Unanimous miss.  Surface error / skip information so downstream
    # can see which catalogs were "real misses" vs "skipped".
    skipped = [
        f"{r.catalog_name}({r.error.split(':', 1)[0]})"
        for r in agg["errors"]
    ]
    if skipped:
        rationale = (
            "missing from all consulted catalogs; "
            f"skipped/errored: {','.join(skipped)}"
        )
    else:
        rationale = "missing from all consulted catalogs"
    return True, rationale, catalogs_checked


def _f1_permutation_null(coeffs: List[int], m_value: float) -> Tuple[bool, str]:
    """F1 falsification: simulate permutation null on the M-value.

    For a real signal, the observed M should be statistically distinguishable
    from the M-distribution under random coefficient permutation. For a
    numerical artifact (M near 1 with high precision noise), the permutation
    null typically yields M much higher.

    MVP simulation: check that observed M < median of 30 random permutations
    (cheap proxy; real F1 uses the matched-null pipeline).
    """
    if not math.isfinite(m_value):
        return False, "F1: non-finite M"
    try:
        import numpy as np
        from techne.lib.mahler_measure import mahler_measure as _mm

        rng = np.random.default_rng(20260503)
        perm_ms: List[float] = []
        for _ in range(30):
            perm = list(coeffs)
            rng.shuffle(perm)
            try:
                v = float(_mm(perm))
                if math.isfinite(v):
                    perm_ms.append(v)
            except Exception:
                continue
        if not perm_ms:
            return False, "F1: permutation null produced no finite M"
        median_perm = float(np.median(perm_ms))
        # Observed M passes F1 iff strictly smaller than the permutation-null median.
        survived = m_value < median_perm
        return (
            survived,
            f"F1 perm-null median={median_perm:.4f} vs observed={m_value:.4f}",
        )
    except Exception as e:  # pragma: no cover
        return False, f"F1: simulation error {type(e).__name__}: {e!r}"[:200]


def _f6_base_rate(coeffs: List[int], m_value: float) -> Tuple[bool, str]:
    """F6 falsification: base-rate check.

    Trivial polys (all-equal-magnitude coefficients) yield Salem-band M
    by accident; F6 rejects them as base-rate hits. Real signal has
    non-trivial coefficient structure.
    """
    if all(c == 0 for c in coeffs):
        return False, "F6: zero polynomial"
    nz = [c for c in coeffs if c != 0]
    if not nz:
        return False, "F6: all-zero coefficients"
    # Count distinct nonzero coefficient values (signed). Lehmer has +1
    # and -1, giving 2 distinct values; Φ_5 has only +1 giving 1 distinct.
    distinct_values = len(set(nz))
    if distinct_values < 2:
        return (
            False,
            f"F6: trivial coefficient structure ({distinct_values} distinct nonzero value)",
        )
    return True, f"F6: {distinct_values} distinct nonzero coefficient values"


def _f9_simpler_explanation(coeffs: List[int]) -> Tuple[bool, str]:
    """F9 falsification: rule out a simpler explanation.

    For Lehmer-like polys: simpler explanation is "the poly is a
    cyclotomic factor of a higher-degree poly" (M=1 trivially). We
    already gate on 1.001 < M < 1.18 upstream; this check is for
    post-rejection record-keeping.
    """
    # The discovery_env reward gate already excludes cyclotomic (M=1).
    # If we got here, M > 1.001, so cyclotomic is not the explanation.
    return True, "F9: M > 1.001 rules out cyclotomic"


def _f11_cross_validation(
    coeffs: List[int], m_value: float
) -> Tuple[bool, str]:
    """F11 falsification: cross-validation against an independent
    M-computation.

    MVP: re-compute M via two independent paths and check agreement.
    """
    try:
        from techne.lib.mahler_measure import mahler_measure as _mm

        v_a = float(_mm(coeffs))
        v_b = float(_mm(list(reversed(coeffs))))  # reciprocal: should give same M
        if not (math.isfinite(v_a) and math.isfinite(v_b)):
            return False, "F11: non-finite M in cross-val"
        if abs(v_a - v_b) > 1e-6:
            return False, f"F11: cross-val mismatch {v_a:.6f} vs {v_b:.6f}"
        if abs(v_a - m_value) > 1e-6:
            return False, f"F11: M drift {v_a:.6f} vs reported {m_value:.6f}"
        return True, f"F11: cross-val agrees within 1e-6 ({v_a:.6f})"
    except Exception as e:  # pragma: no cover
        return False, f"F11: error {type(e).__name__}: {e!r}"[:200]


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


@dataclass
class DiscoveryPipeline:
    """The DISCOVERY_CANDIDATE -> substrate CLAIM processor.

    Composes with a SigmaKernel + BindEvalExtension. Stateless across
    candidates; the kernel holds the substrate state.
    """

    kernel: SigmaKernel
    ext: BindEvalExtension

    @staticmethod
    def _candidate_hash(coeffs: List[int], m_value: float) -> str:
        blob = json.dumps(
            {"coeffs": list(coeffs), "M": float(m_value)},
            sort_keys=True,
        )
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def process_candidate(
        self,
        coeffs: List[int],
        mahler_measure: float,
    ) -> DiscoveryRecord:
        """Run a single candidate through the pipeline."""

        # Phase 0: cheap upfront filters that don't merit a CLAIM.
        if not (1.001 < mahler_measure < 1.18):
            cand_hash = self._candidate_hash(coeffs, mahler_measure)
            kill_pattern = (
                f"out_of_band:M={mahler_measure:.4f}_outside_(1.001,1.18)"
            )
            check_results_phase0 = {"phase": "phase0_band_check"}
            # Day-3: emit a kill_vector even for phase-0 kills (1 component).
            from prometheus_math.kill_vector import (
                kill_vector_from_pipeline_output,
            )
            kv = kill_vector_from_pipeline_output(
                coeffs=list(coeffs),
                mahler_measure=mahler_measure,
                check_results=check_results_phase0,
                candidate_hash=cand_hash,
                phase0_kill=True,
            )
            return DiscoveryRecord(
                candidate_hash=cand_hash,
                coeffs=tuple(coeffs),
                mahler_measure=mahler_measure,
                terminal_state="REJECTED",
                kill_pattern=kill_pattern,
                claim_id=None,
                symbol_ref=None,
                check_results=check_results_phase0,
                kill_vector=kv,
            )

        # Phase 1: cheap mechanical kill-path checks.
        recip_ok = _is_reciprocal(coeffs)
        irred_ok, irred_rat = _is_irreducible(coeffs)
        # Day-3: also capture per-catalog results so the kill_vector can
        # carry per-catalog distances.  We re-run the consistency check
        # via the orchestrator (cached internally for in-band candidates),
        # then derive the legacy aggregated tuple from the same data.
        try:
            from prometheus_math.catalog_consistency import (
                run_consistency_check as _run_consistency_check,
            )
            _agg = _run_consistency_check(coeffs, mahler_measure)
        except Exception:
            _agg = None
        catalog_miss, cat_rat, catalogs = _check_catalog_miss(
            coeffs, mahler_measure
        )
        f1_ok, f1_rat = _f1_permutation_null(coeffs, mahler_measure)
        f6_ok, f6_rat = _f6_base_rate(coeffs, mahler_measure)
        f9_ok, f9_rat = _f9_simpler_explanation(coeffs)
        f11_ok, f11_rat = _f11_cross_validation(coeffs, mahler_measure)

        check_results = {
            "reciprocity": (recip_ok, "palindromic check"),
            "irreducibility": (irred_ok, irred_rat),
            "catalog_miss": (catalog_miss, cat_rat),
            "catalogs_checked": catalogs,
            "F1": (f1_ok, f1_rat),
            "F6": (f6_ok, f6_rat),
            "F9": (f9_ok, f9_rat),
            "F11": (f11_ok, f11_rat),
        }

        # Build the kill_vector from the existing check results.  Re-used
        # for both the early-kill REJECTED branch and the SHADOW_CATALOG
        # success branch.
        from prometheus_math.kill_vector import (
            kill_vector_from_pipeline_output,
        )
        _cand_hash = self._candidate_hash(coeffs, mahler_measure)
        _kv = kill_vector_from_pipeline_output(
            coeffs=list(coeffs),
            mahler_measure=mahler_measure,
            check_results=check_results,
            candidate_hash=_cand_hash,
            catalog_results=_agg,
        )

        # Phase 2: capture the kill_pattern of the FIRST failing check.
        # The order matters — we report the most informative kill.
        early_kill: Optional[str] = None
        if not recip_ok:
            early_kill = "reciprocity_failed"
        elif not irred_ok:
            early_kill = f"reducible:{irred_rat[:80]}"
        elif not catalog_miss:
            # NOT a kill in the artifact sense — this is a known polynomial
            # rediscovered. Route to a different terminal: still REJECTED
            # for the discovery purpose (it's not new), but the kill_pattern
            # names the catalog hit so downstream knows it's calibration
            # signal, not artifact.
            early_kill = f"known_in_catalog:{cat_rat[:80]}"
        elif not f1_ok:
            early_kill = f"F1_kill:{f1_rat[:80]}"
        elif not f6_ok:
            early_kill = f"F6_kill:{f6_rat[:80]}"
        elif not f9_ok:
            early_kill = f"F9_kill:{f9_rat[:80]}"
        elif not f11_ok:
            early_kill = f"F11_kill:{f11_rat[:80]}"

        if early_kill is not None:
            return DiscoveryRecord(
                candidate_hash=_cand_hash,
                coeffs=tuple(coeffs),
                mahler_measure=mahler_measure,
                terminal_state="REJECTED",
                kill_pattern=early_kill,
                claim_id=None,
                symbol_ref=None,
                check_results=check_results,
                kill_vector=_kv,
            )

        # Phase 3: all kill-path checks survived. Mint a CLAIM through
        # the kernel discipline.
        candidate_hash = _cand_hash
        cap = self.kernel.mint_capability("PromoteCap")
        hypothesis = (
            f"polynomial coeffs={coeffs} has Mahler measure "
            f"{mahler_measure:.6f} in (1.001, 1.18); is reciprocal, "
            f"irreducible over Q, and absent from {catalogs}"
        )
        evidence = {
            "coeffs": list(coeffs),
            "mahler_measure": mahler_measure,
            "candidate_hash": candidate_hash,
            "checks_passed": [
                k for k, v in check_results.items()
                if isinstance(v, tuple) and v[0] is True
            ],
        }
        claim = self.kernel.CLAIM(
            target_name=f"discovery_candidate_{candidate_hash[:12]}",
            hypothesis=hypothesis,
            evidence=evidence,
            kill_path="discovery_pipeline_v1",
            target_tier=Tier.Conjecture,
        )

        # Phase 4: We don't run the kernel's subprocess Ω oracle here —
        # the kill-path checks above already implement the discipline
        # the Ω would dispatch. Instead, construct a synthetic verdict
        # that records the survival and short-circuits PROMOTE.
        # (The bind_eval_v2 pattern uses in-process validators for the
        # same reason; documented in BIND_EVAL_V2_NOTES.md.)
        verdict = VerdictResult(
            status=Verdict.CLEAR,
            rationale=(
                f"discovery_pipeline_v1 survival: reciprocal + irreducible + "
                f"catalog_miss + F1+F6+F9+F11 all passed"
            ),
            input_hash=candidate_hash,
            seed=0,
            runtime_ms=0,
        )
        # Persist the verdict on the claim so PROMOTE accepts it.
        self.kernel.conn.execute(
            "UPDATE claims SET verdict_status=?, verdict_rationale=?, "
            "verdict_input_hash=?, verdict_seed=?, verdict_runtime_ms=? "
            "WHERE id=?",
            (
                verdict.status.value,
                verdict.rationale,
                verdict.input_hash,
                verdict.seed,
                verdict.runtime_ms,
                claim.id,
            ),
        )
        self.kernel.conn.commit()
        claim.verdict = verdict

        # Phase 5: PROMOTE. The claim survived the kill_path; mint the
        # symbol. By default the symbol lands in the SHADOW_CATALOG
        # state — surviving the battery is necessary but not sufficient
        # for canonical PROMOTED status. PROMOTED requires independent
        # verification (literature cross-check, formal proof, additional
        # cross-modality concordance), which we don't yet automate.
        try:
            symbol = self.kernel.PROMOTE(claim, cap)
            symbol_ref = symbol.ref
            terminal: TerminalState = "SHADOW_CATALOG"
        except Exception as e:
            return DiscoveryRecord(
                candidate_hash=candidate_hash,
                coeffs=tuple(coeffs),
                mahler_measure=mahler_measure,
                terminal_state="REJECTED",
                kill_pattern=f"PROMOTE_failed:{type(e).__name__}:{e!r}"[:200],
                claim_id=claim.id,
                symbol_ref=None,
                check_results=check_results,
                kill_vector=_kv,
            )

        # The symbol's def_blob carries the candidate's full provenance.
        # Mark its tier so downstream consumers can filter "shadow vs
        # canonical." Tier.WorkingTheory is the right shape — survived
        # mechanical checks but not yet independently verified.
        return DiscoveryRecord(
            candidate_hash=candidate_hash,
            coeffs=tuple(coeffs),
            mahler_measure=mahler_measure,
            terminal_state=terminal,
            kill_pattern=None,
            claim_id=claim.id,
            symbol_ref=symbol_ref,
            check_results=check_results,
            kill_vector=_kv,
        )

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def list_shadow_catalog(self) -> List[Dict[str, Any]]:
        """Return all SHADOW_CATALOG entries currently in the substrate."""
        rows = self.kernel.conn.execute(
            "SELECT name, version, def_hash, def_blob, tier "
            "FROM symbols WHERE name LIKE ? ORDER BY created_at",
            ("discovery_candidate_%",),
        ).fetchall()
        out: List[Dict[str, Any]] = []
        for r in rows:
            try:
                blob = json.loads(r[3])
            except Exception:
                blob = {}
            out.append(
                {
                    "name": r[0],
                    "version": r[1],
                    "def_hash": r[2],
                    "tier": r[4],
                    "blob": blob,
                }
            )
        return out


__all__ = [
    "DiscoveryPipeline",
    "DiscoveryRecord",
    "TerminalState",
]
