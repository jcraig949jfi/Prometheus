"""
AETH-01 -- provenance composition rule (EXPERIMENTS.md, S06 repair).

This is NOT physics; it is the pure labeling rule that determines
`instrument_class` for a run's initialization recipe, extracted here as
a single testable function so KILL_GATES_01.md's K6 hand-cases have an
executable check, not only a documentation-level argument. No campaign
runner exists yet; this function only encodes the composition rule
itself.
"""

SEEDED_CONTROL = "SEEDED_CONTROL"
SPONTANEOUS = "SPONTANEOUS"


def instrument_class(seeded_pattern_present: bool) -> str:
    """EXPERIMENTS.md (S06 repair): `instrument_class = SEEDED_CONTROL`
    if ANY hand-authored functional byte pattern (regimes 3-4) is
    present ANYWHERE in the initial lattice content, regardless of
    which overlay (regimes 5-7: resource-rich/poor/heterogeneous) is
    additionally applied. `instrument_class = SPONTANEOUS` only if the
    ENTIRE initial lattice content derives exclusively from
    unstructured generation (regimes 1-2), under ANY overlay. There is
    no configuration in which the same initialization is validly
    labeled both ways -- this function is intentionally total (every
    call returns exactly one of the two labels)."""
    return SEEDED_CONTROL if seeded_pattern_present else SPONTANEOUS
