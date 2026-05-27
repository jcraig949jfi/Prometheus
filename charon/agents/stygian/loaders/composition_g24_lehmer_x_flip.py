"""Composition loader: EREBOS-G24-* (Symmetry/Twist) on Lehmer-context
parents.

Per the G24 plugin spec: the substitution x -> -x is a known
mathematical symmetry that PRESERVES Mahler measure exactly
(because P(-x) has roots equal to -roots of P, which have the
same absolute values). The conjecture under test is: "Mahler
measure is conserved under x -> -x for all entries in the
Mossinghoff non-cyclotomic catalog."

If this conjecture holds (the expected mathematical truth), G24's
falsification fails -> verdict = PROMOTED (the symmetry holds, the
catalog implementation is consistent with the mathematics).

If ANY entry's twisted Mahler measure differs from the original
beyond numerical tolerance, kill_pattern = symmetry_breaking — and
the meta-finding is that the CATALOG or the COMPUTATION has a bug,
NOT that the mathematics is wrong. This makes G24 a substrate-grade
catalog auditor.

Concrete test (v0.15 MVP):
- Sample SAMPLE_SIZE catalog entries with ascending M (deterministic).
- For each: read entry['coeffs'], apply x -> -x flip, recompute
  Mahler measure via techne.lib.mahler_measure.mahler_measure.
- Tolerance: TOLERANCE = 1e-6 absolute on M itself.
- If any |M_original - M_twisted| > TOLERANCE:
    -> REJECTED, kill_pattern = symmetry_breaking (catalog audit fail).
- If all match within tolerance:
    -> PROMOTED (symmetry confirmed end-to-end; catalog passes the
       x -> -x audit).
"""
from __future__ import annotations

from typing import Optional

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    load_non_cyclotomic_mahler_entries,
)


# Number of catalog entries to audit per run (capped to keep loader cheap)
SAMPLE_SIZE = 200
TOLERANCE = 1e-6


def _x_flip_local(coeffs: list[int]) -> list[int]:
    """x -> -x substitution: negate every odd-indexed coefficient
    (ascending convention). Local mirror of mahler._x_flip to avoid
    private-API coupling."""
    return [c if (i % 2 == 0) else -c for i, c in enumerate(coeffs)]


def run_g24_lehmer_x_flip_audit() -> dict:
    """Audit SAMPLE_SIZE entries under the x -> -x symmetry. Returns
    the result dict the executor consumes."""
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

    # Deterministic sample: first SAMPLE_SIZE by ascending M (the
    # densest, most-tested band).
    entries_sorted = sorted(entries, key=lambda e: float(e["mahler_measure"]))
    sample = entries_sorted[:SAMPLE_SIZE]

    mismatches: list[dict] = []
    audited = 0
    for e in sample:
        coeffs = e.get("coeffs")
        if not coeffs or not isinstance(coeffs, (list, tuple)):
            continue
        M_orig = float(e["mahler_measure"])
        twisted = _x_flip_local(list(coeffs))
        try:
            M_twisted = float(mahler_measure(twisted))
        except Exception as ex:
            mismatches.append({
                "degree": e.get("degree"),
                "coeffs": list(coeffs),
                "M_orig": M_orig,
                "error": f"twisted_Mahler_compute_failed: {ex}",
            })
            audited += 1
            continue
        audited += 1
        if abs(M_orig - M_twisted) > TOLERANCE:
            mismatches.append({
                "degree": e.get("degree"),
                "coeffs": list(coeffs),
                "M_orig": M_orig,
                "M_twisted": M_twisted,
                "delta": abs(M_orig - M_twisted),
            })

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
            f"x -> -x audit detected {len(mismatches)}/{audited} "
            f"catalog entries whose twisted Mahler measure differs "
            f"from the stored value beyond tolerance {TOLERANCE}. "
            f"This is a CATALOG / IMPLEMENTATION audit failure -- "
            f"the mathematics says M(P(x)) = M(P(-x)) exactly. "
            f"Substrate-grade meta-finding: the data or the compute "
            f"pipeline has a bug worth investigating."
        )
    else:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"x -> -x audit: all {audited}/{audited} sampled catalog "
            f"entries have twisted Mahler measure within tolerance "
            f"{TOLERANCE} of the stored value. The Mossinghoff catalog "
            f"passes the x -> -x symmetry audit. G24's conjecture "
            f"that Mahler measure is conserved under sign-flip is "
            f"empirically confirmed on this sample."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "n_sample": audited,
        "n_mismatches": len(mismatches),
        "tolerance": TOLERANCE,
        "mismatches_head": mismatches[:5],  # first few for triage
        "notes": notes,
    }


class G24LehmerXFlipLoader:
    plugin_id = "g24_symmetry_twist"
    composition_id = "g24_lehmer_x_flip"
    description = (
        "Composition loader for EREBOS-G24-* claims in Mahler context. "
        "Audits a sample of Mossinghoff catalog entries under the "
        "x -> -x symmetry; PROMOTED if catalog passes, REJECTED with "
        "symmetry_breaking if any entry's twisted Mahler differs."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g24_symmetry_twist":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        rationale = (queue_payload.get("rationale") or "").lower()
        return (
            "BL-C-001" in composed_id
            or "BL-C-003" in composed_id
            or "BL-C-004" in composed_id
            or "lehmer" in composed_id.lower()
            or "mahler" in composed_id.lower()
            or "salem" in composed_id.lower()
            or "lehmer" in rationale
            or "mahler" in rationale
        )

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_g24_lehmer_x_flip_audit()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                f"EREBOS-G24 symmetry composition: x -> -x preserves "
                f"Mahler measure; audited on {SAMPLE_SIZE} smallest-M "
                f"Mossinghoff entries to detect catalog/implementation "
                f"bugs."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff "
                "non-cyclotomic catalog; techne.lib.mahler_measure for "
                "twisted-poly recomputation."
            ),
            "result": result,
            "notes": (
                "G24 graduates to empirical instrument for Mahler-"
                "context emissions. The mathematical truth is known "
                "(M is conserved under x -> -x); the loader audits "
                "whether the catalog implements this correctly."
            ),
        }


register(G24LehmerXFlipLoader())
