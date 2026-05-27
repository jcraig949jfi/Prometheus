"""Composition loader: EREBOS-G18-* (Minimal-Counterexample) on
Lehmer-context parents.

Per the G18 plugin spec: predicts that the minimal counterexample
to a parent conjecture lives in Region R (the modal kill_pattern
region in Erebos's kill-density landscape). The Tier B-MVP path
here: for Lehmer-context parents, define Region R as the degree-
band above the parent's stated degree (or, by default, degrees
>= DEGREE_BAND_FLOOR). Search the Mossinghoff non-cyclotomic
catalog for any entry in that band whose M < M_Lehmer (a literal
counterexample to Lehmer's conjecture).

Expected outcome: Lehmer's conjecture is unbroken historically,
so the catalog should contain ZERO such counterexamples in any
degree band. The loader's verdict shape:

- Counterexample found in the region: PROMOTED (G18's gradient-
  field prediction succeeded; this would be a substrate-grade
  historical break to Lehmer).
- No counterexample found: REJECTED with kill_pattern =
  region_R_exhausted_without_counterexample (G18's prediction
  was wrong — the region is exhausted; the parent conjecture
  holds in this region empirically).

This matches the G18 plugin's `expected_kill_pattern` exactly,
which is the design intent: G18 against an unbroken conjecture
should return its expected kill pattern, validating both the
plugin's framing and the catalog's historical state.

Loader is intentionally NOT a falsification of Lehmer itself; it's
a falsification of G18's gradient-field hypothesis about where the
counterexample lives. If anyone breaks Lehmer, this loader will
catch it.
"""
from __future__ import annotations

from typing import Optional

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    M_LEHMER,
    load_non_cyclotomic_mahler_entries,
)


# Default region floor when the parent doesn't specify a degree.
# Most Lehmer-conjecture work focuses on degree >= 10 (Lehmer's
# polynomial itself is degree 10). Pick a floor that gives a
# substantive search space.
DEGREE_BAND_FLOOR = 10
DEGREE_BAND_CEILING = 36  # Mossinghoff catalog cap

# Epsilon tolerance for the strict-less-than comparison. Without
# this, floating-point rounding flags Lehmer-equivalents (e.g.,
# Lehmer x cyclotomic, which has identical M but is stored with a
# different last-bit rounding from a different compute path) as
# false-positive counterexamples. 1e-9 is way below the smallest
# known gap between distinct M classes (~1e-3) but well above
# double-precision ULP noise (~1e-15).
M_COMPARISON_EPSILON = 1e-9


def _find_counterexamples_in_band(
    degree_floor: int,
    degree_ceiling: int,
    M_threshold: float,
    epsilon: float = M_COMPARISON_EPSILON,
) -> list[dict]:
    """Return Mossinghoff non-cyclotomic entries with degree in
    [floor, ceiling] AND M strictly less than threshold by more than
    `epsilon` (numerical-precision-aware). These would be genuine
    counterexamples to a 'M >= threshold' parent conjecture."""
    entries = load_non_cyclotomic_mahler_entries()
    out: list[dict] = []
    for e in entries:
        deg = e.get("degree")
        m = float(e.get("mahler_measure", 0.0))
        if deg is None or not (degree_floor <= deg <= degree_ceiling):
            continue
        if m < M_threshold - epsilon:
            out.append({
                "degree": deg,
                "mahler_measure": m,
                "coeffs": e.get("coeffs"),
                "name": e.get("name"),
            })
    return out


def run_g18_lehmer_degree_band(
    degree_floor: int = DEGREE_BAND_FLOOR,
    degree_ceiling: int = DEGREE_BAND_CEILING,
) -> dict:
    """Search the Mossinghoff catalog for Lehmer counterexamples in
    the predicted degree band. Returns result dict."""
    entries = load_non_cyclotomic_mahler_entries()
    if not entries:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": "Mossinghoff catalog load returned no entries",
        }
    # Count entries in the band (any M)
    in_band = [
        e for e in entries
        if (deg := e.get("degree")) is not None
        and degree_floor <= deg <= degree_ceiling
    ]
    n_band = len(in_band)

    # Find counterexamples to Lehmer in the band (M < M_Lehmer,
    # non-cyclotomic since load_non_cyclotomic excludes M ~ 1.0)
    counterexamples = _find_counterexamples_in_band(
        degree_floor=degree_floor,
        degree_ceiling=degree_ceiling,
        M_threshold=M_LEHMER,
    )

    if counterexamples:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"G18's gradient-field hypothesis SUCCEEDED: found "
            f"{len(counterexamples)} catalog entries in degree band "
            f"[{degree_floor}, {degree_ceiling}] with M < M_Lehmer = "
            f"{M_LEHMER:.6f}. This is a substrate-grade historical "
            f"break to Lehmer's conjecture in the predicted region. "
            f"Triage immediately."
        )
    else:
        verdict = "REJECTED"
        kp = "region_R_exhausted_without_counterexample"
        notes = (
            f"G18's gradient-field hypothesis FAILED: no catalog "
            f"entries in degree band [{degree_floor}, {degree_ceiling}] "
            f"(n={n_band} entries searched) have M < M_Lehmer. "
            f"The region is exhausted; Lehmer's conjecture holds "
            f"empirically in this band. G18's prediction that the "
            f"counterexample lives here was wrong (matches plugin's "
            f"expected_kill_pattern)."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "degree_band_floor": degree_floor,
        "degree_band_ceiling": degree_ceiling,
        "n_entries_in_band": n_band,
        "M_threshold": M_LEHMER,
        "n_counterexamples": len(counterexamples),
        "counterexamples_head": counterexamples[:5],
        "notes": notes,
    }


class G18LehmerDegreeBandLoader:
    plugin_id = "g18_minimal_counterexample"
    composition_id = "g18_lehmer_degree_band"
    description = (
        "Composition loader for EREBOS-G18-* claims in Lehmer context. "
        "Searches degree band [10, 36] of Mossinghoff catalog for "
        "counterexamples to Lehmer's bound. PROMOTED if any found "
        "(historic break); REJECTED with "
        "region_R_exhausted_without_counterexample if none."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g18_minimal_counterexample":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        rationale = (queue_payload.get("rationale") or "").lower()
        return (
            "BL-C-001" in composed_id
            or "lehmer" in composed_id.lower()
            or "mahler" in composed_id.lower()
            or "lehmer" in rationale
            or "mahler" in rationale
        )

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_g18_lehmer_degree_band()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                f"EREBOS-G18 minimal-counterexample composition: "
                f"search Mossinghoff catalog degree-band "
                f"[{DEGREE_BAND_FLOOR}, {DEGREE_BAND_CEILING}] for "
                f"entries with M < M_Lehmer. Region exhaustion is "
                f"the expected outcome on Lehmer's (historically "
                f"unbroken) conjecture."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff "
                "non-cyclotomic catalog; degree-band restriction; "
                "M < M_Lehmer search."
            ),
            "result": result,
            "notes": (
                "G18 graduates to empirical instrument for Lehmer-"
                "context emissions via the catalog-search degree-band "
                "loader. Validates plugin's expected_kill_pattern "
                "against an unbroken conjecture."
            ),
        }


register(G18LehmerDegreeBandLoader())
