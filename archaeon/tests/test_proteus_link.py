"""Proteus player identity, its coordinate axes, and the neutrality guard."""
from __future__ import annotations

import pytest

from archaeon import config as cfg
from archaeon import fossils, provenance
from archaeon.detectors import run_all, eligibility_census

px = pytest.importorskip("archaeon.proteus_link")


@pytest.fixture(scope="module")
def reg():
    try:
        return px.load_registry()
    except px.ProteusUnavailable as exc:            # pragma: no cover
        pytest.skip(str(exc))


# --------------------------------------------------------------------------
# The registry
# --------------------------------------------------------------------------
def test_registry_loads_and_is_the_frozen_menagerie(reg):
    assert reg["schema_version"] == "proteus.player_registry.v1"
    assert len(reg["entries"]) == 64


def test_every_specimen_is_generation_zero(reg):
    """The starter menagerie is USE A: frozen specimens, nothing bred.

    If this ever fails, bred organisms have entered the registry and the
    neutrality guard becomes load-bearing rather than precautionary.
    """
    assert {e["generation"] for e in reg["entries"]} == {0}


def test_lineage_id_is_not_a_family_key_here(reg):
    """All 64 lineages have size 1, so lineage_id groups nothing.

    Recorded as a test because it is easy to assume otherwise: lineage_id IS a
    family key in general (it is the founder's organism_id), but in the starter
    menagerie every specimen is its own founder. A detector that used it as a
    family baseline would get a baseline of one.
    """
    lineages = [e["lineage_id"] for e in reg["entries"]]
    assert len(set(lineages)) == len(lineages) == 64


def test_envelope_axes_are_numeric_and_have_real_spread(reg):
    """These are the coordinates that replace the hash-like spec.candidate."""
    ids = [e["organism_id"] for e in reg["entries"]]
    for axis in ("tape_words", "n_regs", "genome_instructions", "tick_budget"):
        vals = [px.envelope_coords(o).get(axis) for o in ids]
        assert all(isinstance(v, float) for v in vals), axis
        assert len(set(vals)) > 1, "{} is degenerate".format(axis)
    # tape_words spans 16..1024: a real ordered axis, unlike a hash
    tw = [px.envelope_coords(o)["tape_words"] for o in ids]
    assert min(tw) == 16 and max(tw) == 1024


def test_archaeon_reads_coordinates_not_taxonomy():
    """Proteus supplies no player types/families/tags by design and tests that
    the vocabulary never appears. Archaeon must read only measured bounds."""
    for axis in px.ENVELOPE_AXES:
        for banned in ("family", "type", "class", "tag", "score", "rank",
                       "quality"):
            assert banned not in axis.lower(), \
                "{} looks like a taxonomy field, not a measured bound".format(axis)


# --------------------------------------------------------------------------
# The neutrality guard
# --------------------------------------------------------------------------
def test_frozen_specimens_pass_the_use_a_guard(reg):
    ids = [e["organism_id"] for e in reg["entries"]][:8]
    audit = px.assert_use_a_only(ids)
    assert audit["bred_organisms"] == 0
    assert audit["registered_generation_0"] == 8
    assert audit["permitted_use"] == px.USE_A


def test_bred_organism_is_refused(monkeypatch, reg):
    """A population comparison over bred organisms must raise, not warn.

    Proteus reports mutation_neutrality =
    NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT. A baseline built from a
    biased population is wrong in a way that leaves NO trace in the
    arithmetic, so a warning would be routinely ignored and the bias would
    reach a proposal silently.
    """
    real = px.entries_by_id()
    oid = next(iter(real))
    faked = dict(real)
    faked[oid] = dict(faked[oid], generation=3)
    monkeypatch.setattr(px, "entries_by_id", lambda: faked)
    with pytest.raises(px.NeutralityNotEstablished) as ei:
        px.assert_use_a_only([oid])
    assert "NONEQUILIBRIUM" in str(ei.value)


def test_unregistered_organism_is_unknown_provenance_not_a_violation():
    """Absence from the registry does not make an organism a mutant.

    Treating it as one would be its own fabricated claim -- the same class of
    error the charter forbids in the other direction.
    """
    audit = px.assert_use_a_only(["not-a-proteus-organism-id"])
    assert audit["bred_organisms"] == 0
    assert audit["unregistered_provenance_unknown"] == 1


# --------------------------------------------------------------------------
# The chart and the artifact join
# --------------------------------------------------------------------------
def test_proteus_chart_is_registered():
    c = cfg.CHARTS["sfe.proteus_player.v0"]
    assert c.player_field == "proteus.organism_id"
    assert c.source == "sfe_proteus"
    assert "tape_words" in c.coord_fields


def test_artifact_join_reports_its_own_reach():
    """The reader must say how far the join got, whatever it found.

    A corpus that comes back empty because no world has run an experiment is
    a DIFFERENT fact from one that comes back empty because no Proteus player
    ever crossed into SFE, and the window has to distinguish them.
    """
    c = fossils.read_sfe_proteus()
    w = c.window
    if "error" in w:
        pytest.skip(w["error"])
    for k in ("join", "worlds_with_proteus_artifact",
              "worlds_with_unique_player", "worlds_ambiguous_excluded",
              "returned"):
        assert k in w, "corpus window is missing {}".format(k)
    assert w["worlds_with_unique_player"] + w["worlds_ambiguous_excluded"] \
        == w["worlds_with_proteus_artifact"]


def test_empty_proteus_corpus_is_not_reported_as_missing_player_identity():
    """The distinction that matters.

    On this corpus today the chart HAS player identity and there is simply no
    data. Reporting that as 'no player identity' would be a false statement
    about the instrument -- and would hide that the binding now works.
    """
    c = fossils.read_sfe_proteus()
    if c.rows:
        pytest.skip("corpus is non-empty; this test covers the empty case")
    census = eligibility_census(run_all(c, cfg.DEFAULT.detectors))
    for name in ("REPEATED_SMALL_DEVIATION", "SIGN_INSTABILITY",
                 "PLAYER_ORDER_REVERSAL"):
        e = census["per_detector"][name]
        assert e["detail"].get("cause") == "EMPTY_CORPUS"
        assert "absence of data" in e["blocked_reason"]


def test_provenance_carries_proteus_qualification():
    """Any proposal built on Proteus players must carry what was NOT
    established about them."""
    c = fossils.read_sfe_proteus()
    if "error" in c.window:
        pytest.skip(c.window["error"])
    block = provenance._proteus_block(c, [])
    assert block is not None
    q = block["source_qualification"]
    assert q["permitted_use"] == px.USE_A
    assert q["mutation_neutrality"].startswith("NOT_QUALIFIED")


def test_sfe_chart_still_reports_structural_absence():
    """The default SFE chart genuinely has no player field; that must still
    read as NO_PLAYER_FIELD rather than as an absence of data."""
    c = fossils.read_sfe()
    census = eligibility_census(run_all(c, cfg.DEFAULT.detectors))
    e = census["per_detector"]["PLAYER_ORDER_REVERSAL"]
    assert e["detail"].get("cause") == "NO_PLAYER_FIELD"
