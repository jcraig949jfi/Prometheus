"""Scientific naming/attribution regressions, not evidence of a mechanism.

Read only an explicit Aether scientific-doc allowlist: no RunPod package,
receipts, external reviews or other ecosystems are part of this contract.
"""

from pathlib import Path
import re

import pytest

from reference.scientific_aeth01 import CLAIM_TIERS

DOCS = Path(__file__).resolve().parents[1] / "AETH-01"
ACTIVE_SCIENTIFIC_DOCS = (
    "ADVERSARIAL_ANALYSIS.md", "AETH01_REPAIRED_FREEZE_CANDIDATE.md",
    "DECISIONS.md", "ECONOMICS.md", "EXPERIMENTS.md", "HABITABILITY.md",
    "HEREDITY_REQUIREMENTS.md", "KILL_GATES_01.md", "OBSERVATORY.md",
    "PHYSICS_CANDIDATES.md", "PHYSICS_SPEC_DRAFT.md", "REPAIR_LEDGER_01.md",
    "REQUIREMENTS.md", "GPU_RUNPOD.md",
)
LADDER_SUMMARIES = (
    "AETH01_REPAIRED_FREEZE_CANDIDATE.md", "DECISIONS.md",
    "HEREDITY_REQUIREMENTS.md", "KILL_GATES_01.md", "OBSERVATORY.md",
    "REQUIREMENTS.md",
)


def _text(name):
    return (DOCS / name).read_text(encoding="utf-8")


def test_canonical_claim_ladder_has_exactly_five_named_tiers():
    tiers = re.findall(r"^([1-5])\. \*\*([A-Z_]+)\*\*", _text("HEREDITY_REQUIREMENTS.md"), re.MULTILINE)
    assert tiers == [(str(i), name) for i, name in enumerate(CLAIM_TIERS, 1)]


@pytest.mark.parametrize("name", ACTIVE_SCIENTIFIC_DOCS)
def test_active_scientific_docs_do_not_restore_stale_ladder(name):
    text = _text(name)
    assert "HERITABLE_VARIATION" not in text, name
    # Historical references to the originally reviewed four-tier scheme
    # remain legitimate; these patterns catch it being called current.
    assert not re.search(r"repaired\s+4-tier|Hidden prior: the four-tier", text, re.IGNORECASE), name


@pytest.mark.parametrize("name", LADDER_SUMMARIES)
def test_active_ladder_summaries_include_all_five_names(name):
    text = _text(name)
    assert all(tier in text for tier in CLAIM_TIERS), name


@pytest.mark.parametrize("name", ["HEREDITY_REQUIREMENTS.md", "KILL_GATES_01.md"])
def test_fixture_reports_separate_attribution_mechanism_and_tier(name):
    text = _text(name)
    assert "A_opcode" in text and "A_arg0" in text
    assert "DISTRIBUTED_CONSTRUCTION" in text
    assert "RECURSIVE_ACTIVATION_OF_PRECONFIGURED_MACHINERY" in text
    assert "configuration construction" in text
    assert "scaffold" in text
    assert "SEEDED_CONTROL" in text


@pytest.mark.parametrize("name", ["ECONOMICS.md", "KILL_GATES_01.md"])
def test_pulse_budget_docs_preserve_final_pulse_and_zero_cost_limits(name):
    text = _text(name)
    assert "1 + floor((E-w)/(w+m))" in text
    assert "E<w" in text and "w=0" in text
    assert "E=23,w=3,m=2" in text