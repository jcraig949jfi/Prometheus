"""The scoreboard counts investigations and their yields, not supported/failed rows (directive 2026-09-19 s9),
and MECHANISM counts are over UNIQUE mechanism_ids from the mechanism ledger, not packets (directive 2026-09-19b s2).
A falsified prediction is productive output, so predictions_falsified is reported, never hidden."""
from nyx.atlas import mechanisms as mech
from nyx.atlas.build import build


def test_scoreboard_is_investigation_shaped():
    sb = build()["scoreboard"]
    assert sb["schema"].startswith("nyx.scoreboard/3")
    for k in ("packets_issued", "packets_adjudicated", "predictions_tested", "predictions_falsified",
              "cuts_technically_supported", "mechanisms_registered", "mechanisms_isolated",
              "observer_stable_mechanisms", "successful_independent_transplants",
              "unresolved_anomalies", "mechanisms_that_survived_transplant"):
        assert k in sb, k
    # the old row-counting vocabulary is gone
    assert "verdicts_returned" not in sb and "supported" not in sb


def test_scoreboard_counts_are_internally_consistent():
    sb = build()["scoreboard"]
    assert sb["observer_stable_mechanisms"] <= sb["mechanisms_isolated"] <= sb["mechanisms_registered"]
    assert sb["mechanisms_that_survived_transplant"] <= sb["successful_independent_transplants"] or \
        sb["successful_independent_transplants"] == 0
    assert sb["predictions_falsified"] <= sb["predictions_tested"]


def test_mechanism_count_is_decoupled_from_packet_count():
    """The whole point of s2: one packet can carry several mechanisms, so the counts must not track."""
    sb = build()["scoreboard"]
    led = mech.load()
    ids = [m["mechanism_id"] for m in led["mechanisms"]]
    assert len(ids) == len(set(ids)), "mechanism_ids must be unique -- identity is the point"
    assert sb["mechanisms_registered"] == len(set(ids))
    # ASAL contributes two distinct mechanisms from ONE packet; so mechanisms != packets here
    asal = [m for m in led["mechanisms"] if m["minimal_executable_organ"]["cut_id"] == "asal-sakana-2024"]
    assert len(asal) >= 2
    assert {p["packet_id"] for m in asal for p in m["evidence_packets"]} == {"MECH-ASAL-LEGIT-SEARCH-001"}


def test_ledger_validates_and_every_mechanism_has_a_falsifier():
    led = mech.load()
    assert mech.validate(led) == []
    for m in led["mechanisms"]:
        assert m["falsifier"].strip(), m["mechanism_id"]
        assert m["minimal_executable_organ"]["boundary"], m["mechanism_id"]


def test_survived_transplant_requires_a_supported_transplant_row():
    """The headline count cannot be claimed without a receipt."""
    led = {"schema": mech.SCHEMA, "mechanisms": [{
        "mechanism_id": "M-X", "source_lineage": "t", "proposed_behavior": "b",
        "minimal_executable_organ": {"cut_id": "c", "boundary": "f.py:1-2"},
        "predicted_intervention": "i", "falsifier": "f", "evidence_packets": [],
        "counterevidence_packets": [], "observer_dependence": "UNKNOWN",
        "transplant_history": [], "current_disposition": "SURVIVED_TRANSPLANT"}]}
    assert any("no SUPPORTED transplant row" in b for b in mech.validate(led))
    assert mech.counts(led)["mechanisms_that_survived_transplant"] == 0
