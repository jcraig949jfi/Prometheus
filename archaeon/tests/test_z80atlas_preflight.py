"""Operator ruling 4 (2026-09-23): sampler starvation fix + support/identifiability preflight before any adaptive launch."""
from __future__ import annotations

import pytest

from archaeon.z80atlas import grammar as GR, preflight as PF, scheduler as S

DRAWS = 8000


@pytest.fixture(scope="module")
def fixed():
    return PF.run(GR, draws=DRAWS)


@pytest.fixture(scope="module")
def campaign():
    return PF.run(GR, draws=DRAWS, step=PF.campaign_sampler_step())


def test_regression_campaign_sampler_fails_the_topology_contrast(campaign):
    """The 72-hour campaign's own sampler (c7610ea19) must be caught: no bare-niches world is ever drawn."""
    c = campaign["contrasts"]["topology_alone_niches_vs_well_mixed"]
    assert c["arm_support"][0] == 0 and c["status"] == "UNSUPPORTED"
    assert campaign["verdict"] == "FAIL"
    m = campaign["contrasts"]["migration_within_niches"]          # niches draws pick migration=none far below the design rate
    assert m["arm_support"][0] < 0.5 * m["arm_expected_under_design"][0]


def test_fixed_sampler_supports_every_declared_contrast(fixed):
    assert fixed["undeclared_coupling"] == [] and fixed["reference_rejections"] == 0
    assert fixed["sampler_starved"] == {}
    for name, c in fixed["contrasts"].items():
        assert c["status"] in ("OK", "RESTRICTED"), (name, c)
    topo = fixed["contrasts"]["topology_alone_niches_vs_well_mixed"]
    assert topo["arm_support"][0] >= PF.MIN_SUPPORT and not any(topo["arm_starved"])


def test_matched_control_confound_is_reported_not_hidden(fixed):
    """grammar.matched_controls drops recombination / explicit_fitness when it flips EXTERNAL -> endogenous."""
    c = fixed["contrasts"]["reproduction_physics_via_matched_control"]
    assert c["status"] == "RESTRICTED" and c["control_changes_other_factors"].get("pressure", 0) > 0
    assert fixed["verdict"] == "PASS_WITH_RESTRICTIONS"


def test_undeclared_coupling_is_detected(monkeypatch):
    ctx = dict(GR.CONTEXT); ctx.pop("representation.layout")
    monkeypatch.setattr(GR, "CONTEXT", ctx)
    zeros = PF.structural_zeros(GR)
    linked = {frozenset((a, p)) for a, p in GR.CONTEXT.items()}
    assert "representation.layout|task" in [k for k in zeros if frozenset(k.split("|")) not in linked]


def test_context_matches_the_constraints():
    """Every constraint-induced structural zero is between axes CONTEXT links (so the sampler conditions on it)."""
    zeros = PF.structural_zeros(GR); linked = {frozenset((a, p)) for a, p in GR.CONTEXT.items()}
    assert zeros and all(frozenset(k.split("|")) in linked for k in zeros)


def test_launch_gate_refuses_fail_and_unaccepted_restrictions(monkeypatch):
    for verdict, accept, ok in [("FAIL", "any reason", False), ("PASS_WITH_RESTRICTIONS", None, False),
                                ("PASS_WITH_RESTRICTIONS", "reproduction read only on the clean subset", True), ("PASS", None, True)]:
        monkeypatch.setattr(PF, "run", lambda G, verdict=verdict: {"verdict": verdict, "undeclared_coupling": [], "contrasts": {}})
        got, p = S.preflight_gate(accept)
        assert got is ok, (verdict, accept)


def test_eligible_levels_follow_constraints():
    assert [l for l in GR.AXES["world.migration"] if GR.eligible("world.migration", l, {"world.topology": "well_mixed"})] == ["none"]
    assert set(l for l in GR.AXES["world.env_dynamics"] if GR.eligible("world.env_dynamics", l, {"world.topology": "grid_vn"})) == {"fixed", "nonstationary", "env_mutate"}
    assert not GR.eligible("pressure", "recombination", {"reproduction": "ENDOGENOUS_COPY"}) and GR.eligible("pressure", "recombination", {"reproduction": "EXTERNAL"})
    assert not GR.eligible("representation.layout", "separated", {"task": "none"})
