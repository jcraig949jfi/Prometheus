"""The scoreboard is investigations and their yields, not supported/failed rows (operator directive 2026-09-19 s9).
It counts ACTIVE (non-superseded) packets; the headline is mechanisms_that_survived_transplant, not supported clauses;
a falsified prediction is productive output, so predictions_falsified is reported, never hidden."""
from nyx.atlas.build import build


def test_scoreboard_is_s9_investigation_shaped():
    sb = build()["scoreboard"]
    assert sb["schema"].startswith("nyx.scoreboard/2")
    # the s9 vocabulary is present and the old row-counting keys are gone
    for k in ("packets_issued", "packets_adjudicated", "predictions_tested", "predictions_falsified",
              "cuts_technically_supported", "mechanisms_isolated", "observer_stable_mechanisms",
              "successful_independent_transplants", "unresolved_anomalies", "mechanisms_that_survived_transplant"):
        assert k in sb, k
    assert "verdicts_returned" not in sb and "supported" not in sb


def test_scoreboard_counts_are_internally_consistent():
    sb = build()["scoreboard"]
    # an isolated mechanism is a superset of the observer-stable and the transplanted ones
    assert sb["observer_stable_mechanisms"] <= sb["mechanisms_isolated"]
    assert sb["successful_independent_transplants"] <= sb["mechanisms_isolated"]
    # the headline equals the transplant count (a mechanism survives transplant iff its transplant is SUPPORTED)
    assert sb["mechanisms_that_survived_transplant"] == sb["successful_independent_transplants"]
    # falsified never exceeds tested
    assert sb["predictions_falsified"] <= sb["predictions_tested"]
