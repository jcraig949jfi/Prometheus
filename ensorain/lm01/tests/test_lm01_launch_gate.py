from datetime import datetime, timezone

from ensorain.lm01.launch_gate import is_release, TOKEN, replication_seeds, _seed, CAMPAIGN_BASE, SPAN, REPLICATION_BASE

SHA = "a" * 40
FT = datetime(2026, 9, 26, tzinfo=timezone.utc)
GOOD = dict(sender="Cyclops[m2-e8056938]", recipients=["Ensorain"], kind="ruling", subject=TOKEN + " go",
            body=f"freeze {SHA}", created_at=datetime(2026, 9, 27, tzinfo=timezone.utc))


def test_positive_and_each_single_violation():
    assert is_release(GOOD, SHA, FT)
    for k, v in (("subject", "Re: " + TOKEN), ("kind", "report"), ("sender", "Aporia[m1]"), ("recipients", ["Aporia"]),
                 ("body", "no sha"), ("created_at", datetime(2026, 9, 25, tzinfo=timezone.utc))):
        assert not is_release(dict(GOOD, **{k: v}), SHA, FT), k


def test_seed_ranges_disjoint():
    c = _seed("LM01-campaign", SHA, "s", 0, CAMPAIGN_BASE)
    assert CAMPAIGN_BASE <= c < CAMPAIGN_BASE + SPAN
    assert all(REPLICATION_BASE <= r < REPLICATION_BASE + SPAN for r in replication_seeds(SHA, "s", 5))
