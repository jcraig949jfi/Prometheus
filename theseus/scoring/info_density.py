"""Info-density scoring.

A record is high-info if:
- triggered a kill with a specific (non-generic) failure mode
- survived 4-fold falsification at high precision
- triangulated INCONCLUSIVE → H5_CONFIRMED-local-lemma

A record is low-info if:
- trivially falsifiable (e.g. catalog miss on a known catalog entry)
- repetitive (canonical_claim_text appears verbatim in recent emissions)
- UNVERIFIED with no precision metadata

This is v0.1 heuristic. Calibration against real training_value
deferred until Ergon resumes.
"""
from __future__ import annotations

from theseus.emit.record_schema import TheseusRecord, Verdict


# Kill patterns that count as "specific failure mode" rather than
# generic catalog/syntax miss. Extend as the substrate grows.
SPECIFIC_KILL_PATTERNS = {
    "F1_triggered", "F6_triggered", "F9_triggered", "F11_triggered",
    "operator_falsifier", "irreducibility_violated",
    "reciprocity_violated", "near_miss_band",
}


def info_density_score(record: TheseusRecord) -> float:
    """Return 0..1 info-density score for a record."""
    v = record.verdict

    if v == Verdict.REJECTED.value:
        # Kill — value depends on specificity
        if record.kill_pattern is None:
            return 0.4  # generic kill, still useful
        for sk in SPECIFIC_KILL_PATTERNS:
            if sk in (record.kill_pattern or ""):
                # Specific kill — high value, boost if precision high
                base = 0.8
                if record.precision_dps and record.precision_dps >= 50:
                    base += 0.1
                return min(base, 1.0)
        return 0.5  # named but non-canonical kill pattern

    if v == Verdict.PROMOTED.value:
        # Very rare; high info
        return 0.95

    if v == Verdict.SHADOW_CATALOG.value:
        # Survived battery, not catalog-verified
        # Precision matters a lot here
        if record.precision_dps and record.precision_dps >= 60:
            return 0.75
        return 0.6

    if v == Verdict.INCONCLUSIVE.value:
        # Triangulation seed — moderate value
        return 0.55

    # UNVERIFIED — generator emitted but didn't route through sigma
    # Lowest info value; useful only as raw claim pool
    return 0.2
