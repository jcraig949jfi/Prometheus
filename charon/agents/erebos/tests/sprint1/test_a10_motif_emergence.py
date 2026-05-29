"""Tests for Sprint-1 A10 motif emergence harness."""
from __future__ import annotations

from charon.agents.erebos.sprint1 import SprintResult
from charon.agents.erebos.sprint1.a10_motif_emergence import (
    CLASSES,
    N_PER_CLASS,
    PASS_THRESHOLD_PURITY,
    _generate_classified_ledger,
    run_a10,
)


def test_ledger_has_balanced_classes():
    rows = _generate_classified_ledger()
    from collections import Counter
    c = Counter(r["_class"] for r in rows)
    for cls in CLASSES:
        assert c[cls] == N_PER_CLASS


def test_motif_extractor_does_not_see_class_field():
    """The motif extractor should compute over plugin_id +
    kill_pattern only; the _class field is invisible."""
    from charon.agents.erebos._motif_extraction import (
        extract_plugin_kp_motifs,
    )
    rows = _generate_classified_ledger()
    result = extract_plugin_kp_motifs(rows, min_count=2)
    # Motif keys are (plugin_id, kp_or_PROMOTED) tuples
    for m in result.motifs:
        assert len(m.key) == 2


def test_run_a10_returns_sprint_result():
    r = run_a10()
    assert isinstance(r, SprintResult)
    assert r.experiment_id == "A10"
    assert r.metric_name == "motif_to_class_purity"
    assert r.pass_threshold == PASS_THRESHOLD_PURITY
    assert 0.0 <= r.metric_value <= 1.0


def test_run_a10_is_deterministic():
    r1 = run_a10()
    r2 = run_a10()
    assert r1.metric_value == r2.metric_value
