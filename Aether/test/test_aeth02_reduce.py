"""The AETH-02 report's headline figures, asserted against the evidence.

A report whose numbers cannot be regenerated from committed bytes is a
report nobody can check. These tests run `aeth02_reduce` over the
committed trajectory log and assert the figures quoted in
`AETH-01/NATIVE_CIRCUITRY_01_2026-09-24.md`. A change to the reduction
that would silently alter the report fails here instead of leaving a
stale document behind.

Tolerances are tight on purpose: these are deterministic reductions of a
fixed file, not estimates, so anything other than an exact match means
the reduction changed.
"""

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "observatory"))

import aeth02_reduce as reduce_mod                      # noqa: E402

LOG = os.path.join(ROOT, "AETH-01", "evidence",
                   "2026-09-24_aeth02_trajectories", "circuitry.log")
REPORT = os.path.join(ROOT, "AETH-01",
                      "NATIVE_CIRCUITRY_01_2026-09-24.md")

pytestmark = pytest.mark.skipif(
    not os.path.exists(LOG),
    reason="trajectory evidence not present in this checkout")


@pytest.fixture(scope="module")
def summary():
    return reduce_mod.summarise(LOG)


def test_the_log_parses_with_no_damaged_records():
    """`load` raises on an unparseable telemetry line that is not the tail,
    so this also asserts the committed evidence is intact."""
    records, control = reduce_mod.load(LOG)
    assert len(records) == 612
    assert "AETH02_GATE canary status=PASS" in control


def test_the_out_degree_invariant_held_everywhere(summary):
    """Out-degree 1 is what makes the write graph a partial function. If
    this were ever 2 the graph claims in the report would all be void."""
    assert summary["max_outdegree_observed"] == [1]


def test_three_phases_two_complete_one_truncated(summary):
    phases = summary["phases"]
    assert sorted(phases) == [0, 1, 2]
    assert phases[0]["completed"] and phases[1]["completed"]
    assert not phases[2]["completed"]
    assert phases[0]["last_tick"] == phases[1]["last_tick"] == 50000
    assert phases[2]["last_tick"] == 46751


def test_the_three_seeds_agree_to_four_decimal_places(summary):
    """The round's strongest result. Three independent initial states reach
    the same stationary statistics."""
    for key, places in (("write_density", 3), ("change_rate", 4),
                        ("energy_gini", 3), ("activity_density", 3)):
        values = [summary["phases"][p]["stationary"][key] for p in (0, 1, 2)]
        spread = max(values) - min(values)
        assert spread < 10.0 ** -places, (key, values, spread)


def test_the_four_way_classification_matches_the_report(summary):
    """72% same-value uncontested, 27% state-changing, contests under 1%."""
    for phase in (0, 1, 2):
        fr = summary["phases"][phase]["classes_pooled"]["fractions"]
        assert 0.270 < fr["STATE_CHANGING"] < 0.273
        assert 0.721 < fr["SAME_VALUE_UNCONTESTED"] < 0.723
        contested = (fr["SAME_VALUE_CONTESTED_ALTERNATIVE_CHANGE"]
                     + fr["SAME_VALUE_CONTESTED_NO_ALTERNATIVE_CHANGE"])
        assert 0.0060 < contested < 0.0070
        total = sum(fr[c] for c in reduce_mod.CLASSES)
        assert abs(total - 1.0) < 1e-9, "the four classes must partition"


def test_most_landed_writes_are_redundant_and_perturbation_supplies_the_change(
        summary):
    """86% of landed template writes propose a value already present, and
    ~38% of all template-field change is perturbation acting through that
    redundant channel."""
    for phase in (0, 1, 2):
        entry = summary["phases"][phase]
        assert 0.858 < entry["redundant_proposal_fraction"] < 0.862
        assert 0.375 < entry["perturbation_share_of_change"] < 0.385


def test_an_unbroken_cohort_exists_and_is_about_one_percent(summary):
    """~1.2% of template edges have been present since tick 1; the rest
    turn over with a mean run of 45-54 ticks."""
    for phase in (0, 1, 2):
        unbroken = summary["phases"][phase]["unbroken"]
        for field in ("arg0", "arg1", "payload"):
            assert 0.012 < unbroken[field]["fraction"] < 0.014
            assert 49.0 < unbroken[field]["turnover_mean"] < 54.0
        assert 0.008 < unbroken["opcode"]["fraction"] < 0.009
        # Energy routing is the control that makes the claim mean something:
        # if persistence were a general property it would appear here too.
        assert unbroken["energy"]["fraction"] < 0.0002
        assert unbroken["energy"]["count"] < 10
        assert unbroken["energy"]["turnover_mean"] < 3.0


def test_run_max_reaches_the_end_of_the_trajectory(summary):
    for phase, last in ((0, 50000), (1, 50000), (2, 46751)):
        for field in reduce_mod.TEMPLATE:
            assert summary["phases"][phase]["persistence"][field][
                "run_max"] == last


def test_persistence_and_contest_never_co_occur(summary):
    """The decisive observation: an edge that is contested does not persist.

    Zero contested among 1,754 sampled persistent edges, against a
    whole-window contested rate near 1.7%. If persistence and contest were
    independent the expectation would be about 29.
    """
    windows = summary["windows"]
    assert len(windows) == 10
    total = sum(w["persistent"] for w in windows)
    contested = sum(w["persistent_contested"] for w in windows)
    assert total == 1754
    assert contested == 0
    rates = [w["control_contested"] for w in windows]
    assert 0.012 < min(rates) and max(rates) < 0.023
    expected = total * (sum(rates) / len(rates))
    assert expected > 25, ("the comparison is only meaningful if the "
                           "expectation is well above zero", expected)


def test_cycles_are_stable_and_never_empty(summary):
    """1.45% of nodes on a cycle, 22% membership retention over 500 ticks.

    `retention_zero_count == 0` matters: a single zero would mean the cycle
    set had been completely replaced, which would support a very different
    reading of the same aggregate count.
    """
    for phase in (0, 1, 2):
        cycles = summary["phases"][phase]["cycles"]
        assert 0.0143 < cycles["share_last"] < 0.0149
        assert 0.215 < cycles["retention_mean"] < 0.222
        assert cycles["retention_zero_count"] == 0
        assert cycles["measurements"] >= 94


def test_cost_matches_what_the_report_quotes(summary):
    for phase in (0, 1):
        cost = summary["phases"][phase]["cost"]
        assert 0.886 < cost["phase_usd"] < 0.889
        assert abs(cost["usd_per_1e9_site_ticks"] - 0.004039) < 1e-6
        assert 3.36e7 < cost["sites_per_sec"] < 3.38e7


def test_the_report_does_not_claim_billing_reconciliation():
    """$2.608 is wall time at a quoted rate. The report must say so."""
    with open(REPORT, encoding="utf-8") as fh:
        text = fh.read()
    assert "billing reconciliation" in text.lower()
    assert "NOT performed" in text
    assert "wall time at a quoted rate" in text


def test_the_report_records_that_no_intervention_was_run():
    """Track 4 was conditional and did not happen. A reader must not have
    to infer that from the absence of a section."""
    with open(REPORT, encoding="utf-8") as fh:
        text = fh.read()
    assert "## 3. INTERVENTION RESULTS" in text
    assert "None. No intervention was performed this round." in text


def test_the_render_path_works(summary):
    text = reduce_mod.render(summary)
    assert "max out-degree observed: [1]" in text
    assert "pooled: 0 of 1754 persistent edges were contested" in text
