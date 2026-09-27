import os
import subprocess

import pytest

from ensorain.lm01.launch_gate import (is_operator_launch, negative_control_texts, campaign_seeds, replication_seeds,
                                       _seed, CAMPAIGN_BASE, REPLICATION_BASE, SPAN, REPO)

SHA = "3fc37e0c7" + "a" * 31


def test_positive_full_and_prefix():
    assert is_operator_launch(f"LAUNCH WTP-LM01 using frozen prereg {SHA}", SHA)
    assert is_operator_launch(f"please: LAUNCH WTP-LM01 using frozen prereg {SHA[:9]}.", SHA)


def test_negative_controls_all_rejected():
    neg = negative_control_texts(SHA)
    assert neg["operator_rulings_2026-09-26"], "the operator's ruling text must be present as a control"
    for name, text in neg.items():
        assert not is_operator_launch(text, SHA), name


def test_freeze_commit_must_be_full_sha():
    assert not is_operator_launch(f"LAUNCH WTP-LM01 using frozen prereg {SHA[:12]}", SHA[:12])


def test_campaign_seeds_refuse_uncommitted_or_bad_directive(tmp_path):
    p = tmp_path / "01_OPERATOR_LAUNCH_verbatim.md"
    p.write_text(f"LAUNCH WTP-LM01 using frozen prereg {SHA}\n", encoding="utf-8")
    with pytest.raises(Exception):
        campaign_seeds(str(p), SHA, ["s"], 2)


def test_seed_ranges_disjoint():
    c = _seed("LM01-campaign", SHA, "s", 0, CAMPAIGN_BASE)
    assert CAMPAIGN_BASE <= c < CAMPAIGN_BASE + SPAN
    assert all(REPLICATION_BASE <= r < REPLICATION_BASE + SPAN for r in replication_seeds(SHA, "s", 5))


def test_committed_verified_file_without_matching_hash_is_refused():
    """Full path on a real committed, MANIFEST-verified file: the operator's ruling text must NOT open the gate."""
    p = os.path.join(REPO, "roles", "Ensorain", "prompts", "2026-09-26_lm01_operator_rulings",
                     "01_OPERATOR_LM01_RULINGS_verbatim.md")
    with pytest.raises(PermissionError, match="lacks"):
        campaign_seeds(p, SHA, ["s"], 2)
