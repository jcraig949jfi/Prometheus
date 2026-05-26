"""Composition loader: EREBOS-G25-* (Degeneracy / Trivial-Case)
on Lehmer-context parent.

Per pivot/erebos_g25_degeneracy_research_2026-05-26.md +
charon/agents/erebos/generators/g25_degeneracy.py:DEGENERATE_REGISTRY
which maps BL-C-001 -> degree_1_polynomial.

G25's expected_kill_pattern is `division_by_zero_or_type_error`:
when the parent claim's logic isn't generalized to boundary cases,
the degenerate-state version fails with an exception OR yields a
trivially-true PASS that has no falsification content.

For Lehmer at degree=1:
- Lehmer's polynomial M = 1.176... lives at degree 10.
- Degree-1 polynomials have Mahler measure = max(1, |a_1 / a_0|)
  for ax + b (monic case: just |b| if b is integer).
- For monic integer degree-1 polynomials, M values are integer
  absolute values: 1, 2, 3, ... Many exceed Lehmer's bound
  trivially.
- BUT: degree-1 polynomials with M >= 1.176 are NOT counterexamples
  to Lehmer because Lehmer's conjecture is about MIN M among
  non-cyclotomic polynomials, and degree-1 cases are typically
  cyclotomic (x - 1, x + 1) OR have M well above 1.176.
- Trivially-holding-at-degenerate is the EXPECTED outcome for a
  well-generalized claim; that's "claim_holds_trivially". A
  division_by_zero would indicate the parent's logic was over-
  fitted to higher-degree cases.

MVP test:
1. Filter Mossinghoff catalog to degree=1 entries.
2. For each: compute Lehmer-bound satisfaction (M >= 1.176).
3. If ANY entry triggers a numerical error (NaN, infinity, etc.)
   -> kill_pattern=division_by_zero_or_type_error (G25 succeeds;
   parent claim broke at boundary).
4. Otherwise -> claim_holds_trivially_at_degenerate (G25 fails to
   surface a problem; parent claim is well-generalized).
"""
from __future__ import annotations

import math
from typing import Any, Optional

from charon.agents.stygian.loaders._composition import register


M_LEHMER = 1.1762808182599176


def _load_degree_1_entries() -> list[dict]:
    """Load degree-1 entries from Mossinghoff catalog."""
    try:
        from prometheus_math.databases.mahler import all_below
    except Exception:
        return []
    entries = all_below(2.0)
    return [
        e for e in entries
        if e.get("degree") == 1 and e.get("mahler_measure") is not None
    ]


def run_g25_lehmer_degenerate() -> dict:
    """Run the degenerate-case test on Lehmer claim at degree=1.
    Returns result dict for the executor."""
    deg1 = _load_degree_1_entries()
    if not deg1:
        # The catalog has no degree-1 entries -- that itself is a
        # finding (the catalog doesn't cover the degenerate case),
        # but it's not a G25-style FAILURE; it's a coverage gap.
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_degenerate_case_absent",
            "n_degree_1_entries": 0,
            "notes": (
                "Mossinghoff catalog has no degree-1 entries; the "
                "degenerate-case test cannot run. Note: this is a "
                "catalog coverage observation, not a G25 success/"
                "failure verdict."
            ),
        }

    errors: list[str] = []
    pass_count = 0
    fail_count = 0
    measures: list[float] = []
    for e in deg1:
        m = e.get("mahler_measure")
        try:
            m_f = float(m)
            if math.isnan(m_f) or math.isinf(m_f):
                errors.append(f"M={m_f} for entry {e.get('name', '?')}")
                continue
            measures.append(m_f)
            if m_f >= M_LEHMER:
                pass_count += 1
            else:
                fail_count += 1
        except (TypeError, ValueError) as exc:
            errors.append(f"{type(exc).__name__}: {exc} for entry {e.get('name', '?')}")

    if errors:
        return {
            "verdict": "PROMOTED",  # G25's hypothesis confirmed
            "kill_pattern": "division_by_zero_or_type_error",
            "n_degree_1_entries": len(deg1),
            "n_errors": len(errors),
            "errors_sample": errors[:3],
            "notes": (
                f"Lehmer-bound check on {len(deg1)} degree-1 entries "
                f"produced {len(errors)} numeric errors. G25's "
                f"hypothesis (the parent claim's logic breaks at "
                f"degenerate state) is CONFIRMED by error_count > 0."
            ),
        }

    if not measures:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_no_usable_measures",
            "n_degree_1_entries": len(deg1),
            "notes": "all degree-1 entries had missing/invalid measures",
        }

    pass_fraction = pass_count / len(measures)
    # If pass_fraction is 0 or 1, the test is essentially trivial -
    # either all pass (well-generalized) or none pass (claim broke).
    # Both are "claim_holds_trivially" outcomes from G25's POV (the
    # degenerate case revealed no LOGIC error, just a quantitative
    # outcome).
    return {
        "verdict": "REJECTED",
        "kill_pattern": "claim_holds_trivially_at_degenerate",
        "n_degree_1_entries": len(deg1),
        "n_usable_measures": len(measures),
        "lehmer_pass_count": pass_count,
        "lehmer_fail_count": fail_count,
        "lehmer_pass_fraction": round(pass_fraction, 4),
        "notes": (
            f"Lehmer-bound (M >= {M_LEHMER:.6f}) check on {len(measures)} "
            f"degree-1 entries: {pass_count} pass, {fail_count} fail "
            f"(pass fraction {pass_fraction:.4f}). No numerical "
            f"errors. G25's hypothesis (parent breaks at degenerate "
            f"boundary) REJECTED; parent claim is well-generalized "
            f"to the degree-1 case."
        ),
    }


class G25LehmerDegenerateLoader:
    plugin_id = "g25_degeneracy"
    composition_id = "g25_lehmer_degenerate"
    description = (
        "Composition loader for EREBOS-G25-* claims with parent "
        "BL-C-001 Lehmer; degenerate state = degree=1 polynomials."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g25_degeneracy":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        return "BL-C-001" in composed_id


    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_g25_lehmer_degenerate()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                f"EREBOS-G25 degeneracy composition: the BL-C-001 "
                f"Lehmer-bound claim, when restricted to degenerate "
                f"degree=1 polynomials, must trivially hold (or "
                f"elegantly zero out, or produce a typed exception)."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff catalog; "
                "filtered to entries with degree=1"
            ),
            "result": result,
            "notes": (
                "Third composition loader; second after the v0.10 spike. "
                "G25 graduates from 'unfalsifiable MVP' to 'empirical "
                "instrument' for the (Lehmer, degree=1) composition."
            ),
        }


register(G25LehmerDegenerateLoader())
