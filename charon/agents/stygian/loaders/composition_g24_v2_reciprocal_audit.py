"""Composition loader v2: EREBOS-G24-* with reciprocal-polynomial
symmetry audit.

Companion to composition_g24_lehmer_x_flip. The original G24 loader
audits the x -> -x symmetry; v2 audits the RECIPROCAL substitution
x -> 1/x. For monic integer polynomials with constant term +/- 1
(which all degree-minimum Mossinghoff entries are), the reciprocal
polynomial has the same Mahler measure: M(P(x)) = M(P*(x)) where
P*(x) = x^deg(P) * P(1/x) = reversed coefficient vector.

Audit: for each entry, reverse the coefficients vector and
recompute Mahler. Compare to stored value. Mismatches indicate
catalog corruption.

For palindromic polynomials, reversal is the identity (coefficients
equal their reversal), so the test is degenerate. For non-palindromic
entries, the test is informative — but we already saw in ITER-19
G11 v4 that 99% of the catalog is palindromic. So this audit will
mostly verify identities trivially; the interesting cases are the
~89 non-palindromic entries.
"""
from __future__ import annotations

from typing import Optional

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    load_non_cyclotomic_mahler_entries,
)


SAMPLE_SIZE = 200
TOLERANCE = 1e-6


def _reciprocal(coeffs: list[int]) -> list[int]:
    """Reciprocal polynomial: reverse the coefficient vector."""
    return list(reversed(coeffs))


def _is_palindromic(coeffs: list[int]) -> bool:
    return list(coeffs) == list(reversed(coeffs))


def run_g24_v2_reciprocal_audit() -> dict:
    """Audit a sample of catalog entries under the x -> 1/x
    (reciprocal) symmetry. Returns result dict for the executor.

    Trivial case (palindromic) is reported separately from
    informative case (non-palindromic)."""
    try:
        from techne.lib.mahler_measure import mahler_measure
    except Exception as e:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": f"techne.lib.mahler_measure import failed: {e}",
        }

    entries = load_non_cyclotomic_mahler_entries()
    if not entries:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": "Mossinghoff catalog load returned no entries",
        }

    # Stratify the sample: include all non-palindromic entries first
    # (the informative ones), then top up with palindromic entries
    # from smallest M up.
    non_palindromic = [
        e for e in entries
        if e.get("coeffs") and not _is_palindromic(list(e["coeffs"]))
    ]
    palindromic_sorted = sorted(
        [e for e in entries if e.get("coeffs")
         and _is_palindromic(list(e["coeffs"]))],
        key=lambda e: float(e["mahler_measure"]),
    )
    sample = non_palindromic[:SAMPLE_SIZE]
    if len(sample) < SAMPLE_SIZE:
        sample += palindromic_sorted[:SAMPLE_SIZE - len(sample)]

    audited_pal = 0
    audited_nonpal = 0
    mismatches: list[dict] = []
    for e in sample:
        coeffs = e.get("coeffs")
        if not coeffs:
            continue
        M_orig = float(e["mahler_measure"])
        is_pal = _is_palindromic(list(coeffs))
        rev = _reciprocal(list(coeffs))
        try:
            M_rev = float(mahler_measure(rev))
        except Exception as ex:
            mismatches.append({
                "degree": e.get("degree"),
                "coeffs": list(coeffs),
                "M_orig": M_orig,
                "is_palindromic": is_pal,
                "error": f"reciprocal_Mahler_compute_failed: {ex}",
            })
            continue
        if is_pal:
            audited_pal += 1
        else:
            audited_nonpal += 1
        if abs(M_orig - M_rev) > TOLERANCE:
            mismatches.append({
                "degree": e.get("degree"),
                "coeffs": list(coeffs),
                "M_orig": M_orig,
                "M_reciprocal": M_rev,
                "delta": abs(M_orig - M_rev),
                "is_palindromic": is_pal,
            })

    audited = audited_pal + audited_nonpal
    if audited == 0:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_insufficient_sample",
            "n_sample": 0,
            "notes": "no entries with usable coeffs field",
        }

    if mismatches:
        verdict = "REJECTED"
        kp = "symmetry_breaking"
        notes = (
            f"Reciprocal audit detected {len(mismatches)}/{audited} "
            f"mismatches beyond tolerance {TOLERANCE}. Catalog or "
            f"compute pipeline bug; M(P) should equal M(P*) where "
            f"P*(x) = x^deg(P) * P(1/x) for monic integer polys with "
            f"constant term +/-1."
        )
    else:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"Reciprocal audit: all {audited}/{audited} sampled "
            f"entries pass within tolerance {TOLERANCE}. Catalog "
            f"is consistent under x -> 1/x. Audited {audited_pal} "
            f"palindromic (trivial cases) + {audited_nonpal} non-"
            f"palindromic (informative cases) entries."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "n_sample": audited,
        "n_palindromic": audited_pal,
        "n_non_palindromic": audited_nonpal,
        "n_mismatches": len(mismatches),
        "tolerance": TOLERANCE,
        "mismatches_head": mismatches[:5],
        "notes": notes,
    }


class G24V2ReciprocalAuditLoader:
    plugin_id = "g24_symmetry_twist"
    composition_id = "g24_v2_reciprocal_audit"
    description = (
        "Composition loader v2 for EREBOS-G24-* claims in Mahler "
        "context. Audits the x -> 1/x reciprocal substitution; "
        "complementary to v1 (x -> -x). Informative on non-palindromic "
        "entries; trivial on palindromic."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g24_symmetry_twist":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        if not ("BL-C-001" in composed_id or "lehmer" in composed_id.lower()
                or "mahler" in composed_id.lower() or "salem" in composed_id.lower()):
            return False
        return "v2" in composed_id.lower() or "reciprocal" in composed_id.lower()

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_g24_v2_reciprocal_audit()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                "EREBOS-G24 v2 reciprocal-symmetry composition: audit "
                "x -> 1/x substitution; complementary to v1's x -> -x."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff "
                "catalog; techne.lib.mahler_measure on reversed "
                "coefficient vector."
            ),
            "result": result,
            "notes": (
                "G24 v2 complements v1; together they audit the two "
                "natural unit-circle-preserving symmetries on monic "
                "integer polynomials."
            ),
        }


register(G24V2ReciprocalAuditLoader())
