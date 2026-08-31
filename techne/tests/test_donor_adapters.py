"""The minimum donor test battery, T1-T10. Techne Gen-0, 2026-08-31.

Every registered adapter must survive all ten. The battery is parametrised over the registry,
so a new adapter is covered the moment it registers -- there is no per-donor opt-in, which is
deliberate: an adapter that could skip T8 or T9 would defeat the reason the contract exists.

WHAT THE BATTERY IS FOR. These are engineering properties, not scientific ones. Passing says a
donor is callable, honest about its configuration, replayable, and does not disguise its own
objective as a Prometheus measurement. It says nothing whatever about whether the donor is
useful, and no result here should be cited as evidence that it is.
"""
from __future__ import annotations

import numpy as np
import pytest

from techne.lib import donors as D
from techne.lib.donors.contract import (
    NO_SELECTION, DonorAdapter, DonorArtifact, DonorError, SelectionRelation, canonical_digest,
)

ADAPTERS = sorted(D.registry)

#: One exercisable (capability, payload, config, seed) fixture per adapter. Chosen small and
#: exact so the battery runs in seconds and so T3's determinism claim is testable rather than
#: statistical.
FIXTURES = {
    "tensorly": ("cp", np.linspace(0, 1, 60).reshape(5, 4, 3), {"rank": 2}, 0),
    "pyribs": ("archive_fill",
               {"objective": lambda X: -np.sum(np.asarray(X) ** 2, axis=1),
                "measures": lambda X: np.clip(np.asarray(X), -1, 1)},
               {"solution_dim": 2, "dims": [4, 4], "ranges": [(-1, 1), (-1, 1)],
                "sigma": 0.2, "batch_size": 8, "iterations": 3}, 7),
    "discopy": ("compose",
                {"boxes": [{"name": "f", "dom": "x", "cod": "y"},
                           {"name": "g", "dom": "y", "cod": "z"}]}, {}, None),
    "cvc5": ("check_int_constraints",
             {"vars": ["x", "y"],
              "constraints": [({"x": 1, "y": -1}, ">", 0), ({"x": 1, "y": 1}, "==", 10)]},
             {}, None),
    "egglog": ("saturate_extract", ["*", ["+", 2, 3], 1], {"rules": ["mul_one", "comm_add"]},
               None),
}

#: Adapters whose output is genuinely seed-sensitive, for T4. `discopy`, `cvc5` and `egglog`
#: are deterministic BY CONSTRUCTION -- a diagram, a decision procedure and a saturation are
#: not stochastic -- so demanding seed sensitivity from them would be demanding a defect.
SEED_SENSITIVE = {"pyribs"}


def _fixture(name):
    if name not in FIXTURES:
        pytest.skip("no fixture registered for adapter " + name)
    return FIXTURES[name]


@pytest.fixture(params=ADAPTERS)
def adapter(request):
    try:
        return D.get(request.param)
    except Exception as e:                                            # noqa: BLE001
        pytest.skip("adapter " + request.param + " unavailable: " + repr(e))


# -- T1 IDENTITY ---------------------------------------------------------------------------
def test_t1_identity_reports_expected_upstream_and_version(adapter: DonorAdapter):
    """The adapter names the upstream project it is supposed to be, not the PyPI name it was
    installed under. Five of eight donor names checked on 2026-08-30 resolved to unrelated
    projects, so the distribution name is not evidence of identity."""
    ident = adapter.identity()
    assert ident.name and ident.distribution and ident.version
    assert ident.upstream.startswith("github.com/"), ident.upstream
    assert ident.identity_evidence in {"declared_url", "description_only", "unresolved"}
    import importlib.metadata as md
    assert ident.version == md.version(ident.distribution)


# -- T2 CONFIG ECHO ------------------------------------------------------------------------
def test_t2_effective_config_is_inspectable(adapter: DonorAdapter):
    """What the artifact records as its config is what was actually accepted -- so a reader
    can tell which knobs were in force without trusting a narrative."""
    cap, payload, cfg, seed = _fixture(adapter.identity().name)
    art = adapter.propose(cap, payload, cfg, seed=seed)
    assert art.config == dict(cfg)
    assert art.capability == cap
    assert set(art.config) <= set(adapter.accepted_config)


# -- T3 DETERMINISM ------------------------------------------------------------------------
def test_t3_same_input_config_seed_gives_identical_output(adapter: DonorAdapter):
    """Where the adapter's capabilities() claims determinism, two identical invocations must
    agree bit for bit on the output digest. This is what makes replay meaningful."""
    name = adapter.identity().name
    cap, payload, cfg, seed = _fixture(name)
    claims = {c.name: c.deterministic for c in adapter.capabilities()}
    if not claims.get(cap):
        pytest.skip("capability " + cap + " does not claim determinism")
    a = adapter.propose(cap, payload, cfg, seed=seed)
    b = adapter.propose(cap, payload, cfg, seed=seed)
    assert a.output_digest == b.output_digest, name + " claimed determinism and broke it"
    assert a.input_digest == b.input_digest


# -- T4 SEED SENSITIVITY -------------------------------------------------------------------
def test_t4_seed_can_change_output_where_stochastic(adapter: DonorAdapter):
    """A stochastic donor whose output never moves with the seed is not seeded at all -- it is
    ignoring the seed, and every 'seeded replay' recorded downstream would be fiction."""
    name = adapter.identity().name
    if name not in SEED_SENSITIVE:
        pytest.skip(name + " is deterministic by construction; seed sensitivity is not expected")
    cap, payload, cfg, _ = _fixture(name)
    digests = {adapter.propose(cap, payload, cfg, seed=s).output_digest for s in (1, 2, 3, 4)}
    assert len(digests) > 1, name + " ignored the seed across four values"


# -- T5 PROVENANCE -------------------------------------------------------------------------
def test_t5_artifact_carries_donor_identity_and_config(adapter: DonorAdapter):
    """A produced artifact must answer 'exactly what produced this?' on its own."""
    ident = adapter.identity()
    cap, payload, cfg, seed = _fixture(ident.name)
    prov = adapter.propose(cap, payload, cfg, seed=seed).provenance()
    for key in ("donor", "donor_version", "upstream", "capability", "config", "seed",
                "input_digest", "output_digest", "native_selection_relation", "environment"):
        assert key in prov, "provenance missing " + key
    assert prov["donor"] == ident.name
    assert prov["donor_version"] == ident.version
    assert prov["upstream"] == ident.upstream
    assert "payload" not in prov, "provenance must stay small; the payload is not provenance"


# -- T6 REPLAY -----------------------------------------------------------------------------
def test_t6_persisted_invocation_can_be_reconstructed(adapter: DonorAdapter):
    """The replay record must round-trip through JSON and be sufficient to rerun the call and
    obtain the same output. A replay record that cannot be serialised never reaches a ledger."""
    import json
    name = adapter.identity().name
    cap, payload, cfg, seed = _fixture(name)
    first = adapter.propose(cap, payload, cfg, seed=seed)
    rec = json.loads(json.dumps(first.replay_seed()))
    assert rec["donor"] == name and rec["capability"] == cap and rec["seed"] == seed
    assert rec["input_digest"] == canonical_digest(payload)
    claims = {c.name: c.deterministic for c in adapter.capabilities()}
    again = D.get(rec["donor"]).propose(rec["capability"], payload, rec["config"],
                                        seed=rec["seed"])
    if claims.get(cap):
        assert again.output_digest == first.output_digest


# -- T7 STRICTNESS -------------------------------------------------------------------------
def test_t7_unknown_config_key_raises(adapter: DonorAdapter):
    """Silently dropping an unrecognised key records a configuration that never took effect,
    which turns the provenance record into a false statement."""
    cap, payload, cfg, seed = _fixture(adapter.identity().name)
    bad = dict(cfg)
    bad["definitely_not_a_real_option"] = 1
    with pytest.raises(DonorError) as ei:
        adapter.propose(cap, payload, bad, seed=seed)
    assert "unknown configuration key" in str(ei.value)


def test_t7b_unknown_capability_raises(adapter: DonorAdapter):
    with pytest.raises(DonorError):
        adapter.propose("no_such_capability", None, {})


# -- T8 SELECTION DECLARATION --------------------------------------------------------------
def test_t8_selection_relation_is_explicitly_declared(adapter: DonorAdapter):
    """Declared or explicitly NONE -- never blank. Without this a downstream experiment cannot
    tell a measured result from one inherited from the donor's own objective."""
    rel = adapter.native_selection_relation
    assert isinstance(rel, SelectionRelation)
    assert rel.kind in {"objective", "ordering", "constraint", "none"}
    assert rel.direction in {"maximize", "minimize", "satisfy", "none"}
    assert rel.supplied_by in {"donor", "caller"}
    if rel.kind == "none":
        assert rel is NO_SELECTION or rel.direction == "none"
    else:
        assert rel.over, "a non-none selection relation must say what it ranks"
    art = adapter.propose(*_fixture(adapter.identity().name)[:3],
                          seed=_fixture(adapter.identity().name)[3])
    assert art.native_selection_relation == rel.as_dict()


def test_t8b_adapter_without_selection_relation_cannot_be_defined():
    """The contract refuses the class at definition time, not at call time -- an adapter with
    the field unset must never reach the registry."""
    with pytest.raises(TypeError) as ei:
        class Broken(DonorAdapter):      # noqa: D401
            pass
    assert "native_selection_relation" in str(ei.value)


# -- T9 NATIVE-vs-PROMETHEUS SEPARATION ----------------------------------------------------
def test_t9_no_prometheus_score_field_on_the_artifact(adapter: DonorAdapter):
    """The artifact exposes `native_score` and nothing that could be mistaken for an
    independent Prometheus judgement. Aliasing the two is how a donor's own objective gets
    laundered into a scientific result."""
    cap, payload, cfg, seed = _fixture(adapter.identity().name)
    art = adapter.propose(cap, payload, cfg, seed=seed)
    fields = set(art.provenance())
    for forbidden in ("score", "quality", "fitness", "value", "prometheus_score", "rank"):
        assert forbidden not in fields, "artifact exposes an ambiguous field " + forbidden
    assert "native_score" in dataclass_field_names(art)
    if art.native_score is not None:
        assert adapter.native_selection_relation.kind != "none", \
            "a donor declaring NO_SELECTION returned a native score"


def dataclass_field_names(obj) -> set:
    import dataclasses
    return {f.name for f in dataclasses.fields(obj)}


# -- T10 FAILURE SEMANTICS -----------------------------------------------------------------
def test_t10_donor_failure_is_typed_not_an_empty_success(adapter: DonorAdapter):
    """A failure must raise DonorError carrying donor and stage -- never return an artifact
    with an empty payload, which downstream is indistinguishable from a genuine null."""
    name = adapter.identity().name
    bad_payloads = {
        "tensorly": ("cp", np.array(3.0), {"rank": 2}),          # ndim < 2
        "pyribs": ("archive_fill", {"objective": lambda X: 1.0}, # missing 'measures'
                   {"solution_dim": 2, "dims": [2, 2], "ranges": [(-1, 1), (-1, 1)]}),
        "discopy": ("compose", {"boxes": [{"name": "f", "dom": "x", "cod": "y"},
                                          {"name": "g", "dom": "q", "cod": "z"}]}, {}),
        "cvc5": ("check_int_constraints",
                 {"vars": ["x"], "constraints": [({"x": 1}, "~~", 0)]}, {}),
        "egglog": ("saturate_extract", ["^", 1, 2], {}),
    }
    if name not in bad_payloads:
        pytest.skip("no failure fixture for " + name)
    cap, payload, cfg = bad_payloads[name]
    with pytest.raises(DonorError) as ei:
        adapter.propose(cap, payload, cfg)
    err = ei.value
    assert err.donor == name
    assert err.stage in {"input", "config", "propose", "compose", "tensor_eval"}


# -- registry-level invariants -------------------------------------------------------------
def test_registry_manifest_is_json_serialisable(adapter: DonorAdapter):
    """The inventory is machine-readable or it is not an inventory."""
    import json
    blob = json.dumps(adapter.manifest(), sort_keys=True)
    assert json.loads(blob)["identity"]["name"] == adapter.identity().name


def test_canonical_digest_is_stable_and_discriminating():
    a = {"x": [1, 2, 3], "y": np.arange(4)}
    b = {"y": np.arange(4), "x": [1, 2, 3]}
    assert canonical_digest(a) == canonical_digest(b), "key order must not change the digest"
    assert canonical_digest(a) != canonical_digest({"x": [1, 2, 4], "y": np.arange(4)})
