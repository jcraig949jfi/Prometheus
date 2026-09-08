"""PR-ID (D-7) acceptance tests: PR-ID-a, PR-ID-b, PR-ID-c, plus the WP-X8 identity fixture."""
from __future__ import annotations

import json
import os

import pytest

from proteus.eval import fixtures as F
from proteus.eval.identity import (ARTIFACT_SCHEMA, FAMILY_GENOME, FAMILY_PROGRAM,
                                   FAMILY_RULE_TABLE, IDENTITY_BEARING, IdentityError,
                                   REPR_PLAYER_MANIFEST_V0, artifact_manifest, evaluation_ref,
                                   hashed_document, legacy_organism_id, observation_ref,
                                   organism_ref)
from proteus.eval.library import LIBRARY_VERSION, evaluate
from proteus.foundry.affordances import AFFORDANCE_HASH
from proteus.foundry.identity import RUNTIME_HASH, hash_obj

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTRY = os.path.join(ROOT, "proteus", "integration", "PLAYER_REGISTRY.json")
X8 = os.path.join(ROOT, "proteus", "eval", "X8_IDENTITY_FIXTURE.json")


def prog_artifact(manifest):
    return artifact_manifest(FAMILY_PROGRAM, manifest, REPR_PLAYER_MANIFEST_V0,
                             "proteus.vm.v0.4")


def rule_artifact(body, rep="ca.rule_table.v0", sem="ca.elementary.v0"):
    return artifact_manifest(FAMILY_RULE_TABLE, body, rep, sem)


# =============================================================== PR-ID-a

def test_prid_a_key_order_and_serialization_do_not_change_identity():
    """Canonical JSON sorts keys, so a differently-ordered dict is the same artifact."""
    m1 = dict(F.ECHO)
    m2 = {k: F.ECHO[k] for k in reversed(list(F.ECHO.keys()))}
    assert list(m1.keys()) != list(m2.keys())
    assert organism_ref(prog_artifact(m1)) == organism_ref(prog_artifact(m2))


def test_prid_a_non_identity_metadata_does_not_change_identity():
    a = prog_artifact(F.ECHO)
    b = artifact_manifest(FAMILY_PROGRAM, F.ECHO, REPR_PLAYER_MANIFEST_V0, "proteus.vm.v0.4",
                          meta={"label": "the echo one", "notes": "found on a Tuesday"})
    assert organism_ref(a) == organism_ref(b)


def test_prid_a_a_semantic_instruction_change_alters_identity():
    """One opcode word different -> different artifact."""
    edited = dict(F.ECHO)
    edited["genome"] = list(F.ECHO["genome"])
    edited["genome"][0] = F.OUT                      # was IN
    assert organism_ref(prog_artifact(edited)) != organism_ref(prog_artifact(F.ECHO))


def test_prid_a_a_rule_bit_change_alters_identity():
    a = rule_artifact({"k": 2, "bits": [0, 1, 1, 0]})
    b = rule_artifact({"k": 2, "bits": [0, 1, 1, 1]})
    assert organism_ref(a) != organism_ref(b)


def test_prid_a_representation_and_semantic_versions_are_identity_bearing():
    base = rule_artifact({"k": 1, "bits": [0, 1]})
    rep = rule_artifact({"k": 1, "bits": [0, 1]}, rep="ca.rule_table.v1")
    sem = rule_artifact({"k": 1, "bits": [0, 1]}, sem="ca.totalistic.v0")
    assert organism_ref(base) != organism_ref(rep)
    assert organism_ref(base) != organism_ref(sem)
    assert organism_ref(rep) != organism_ref(sem)


def test_prid_a_identity_bearing_set_is_declared_and_enforced():
    assert IDENTITY_BEARING == ("family", "representation_version", "semantic_version", "body")
    with pytest.raises(IdentityError, match="identity-bearing"):
        artifact_manifest(FAMILY_GENOME, [1, 2], "g.v0", "g.v0", meta={"family": "sneaky"})
    with pytest.raises(IdentityError, match="identity-bearing"):
        artifact_manifest(FAMILY_GENOME, [1, 2], "g.v0", "g.v0", meta={"body": "sneaky"})
    with pytest.raises(IdentityError):
        artifact_manifest(FAMILY_GENOME, [1, 2], "g.v0", "g.v0", meta="not a dict")


def test_prid_a_alias_relabelling_is_a_different_artifact_not_normalised_away():
    """Aliases are excluded only where semantics permit -- and here they do not.

    w and w+25 are instruction-identical but the genome is copied into the tape, so they are
    different DATA. Normalising them would merge artifacts that can behave differently.
    """
    from proteus.eval.library import relabel_opcode_aliases
    alt = relabel_opcode_aliases(F.ECHO, 1)
    assert organism_ref(prog_artifact(alt)) != organism_ref(prog_artifact(F.ECHO))


# =============================================================== PR-ID-b

def test_prid_b_same_artifact_two_worlds_keeps_organism_ref_gains_observation_refs():
    art = prog_artifact(F.ECHO)
    oref = organism_ref(art)
    spec = F.echo_spec((1,))
    eref = evaluation_ref(oref, RUNTIME_HASH, AFFORDANCE_HASH, LIBRARY_VERSION,
                          spec["spec_id"], 0, 4, "budget_status_only")
    o1 = observation_ref(eref, "wld_aaaaaaaa")
    o2 = observation_ref(eref, "wld_bbbbbbbb")
    assert organism_ref(art) == oref            # unchanged by being observed anywhere
    assert o1 != o2                             # separate observation references
    assert o1 != eref and o2 != eref


def test_prid_b_identity_is_separate_from_the_evaluation_environment():
    """organism_ref must not move when the environment does; evaluation_ref must."""
    oref = organism_ref(prog_artifact(F.ECHO))
    spec = F.echo_spec((1,))
    a = evaluation_ref(oref, RUNTIME_HASH, AFFORDANCE_HASH, LIBRARY_VERSION,
                       spec["spec_id"], 0, 4, "budget_status_only")
    b = evaluation_ref(oref, "0" * 64, AFFORDANCE_HASH, LIBRARY_VERSION,
                       spec["spec_id"], 0, 4, "budget_status_only")
    c = evaluation_ref(oref, RUNTIME_HASH, AFFORDANCE_HASH, LIBRARY_VERSION,
                       spec["spec_id"], 1, 4, "budget_status_only")
    d = evaluation_ref(oref, RUNTIME_HASH, AFFORDANCE_HASH, LIBRARY_VERSION,
                       spec["spec_id"], 0, 4, "budget_is_counterexample")
    assert len({a, b, c, d}) == 4, "runtime, seed and policy must each move evaluation_ref"


def test_prid_b_equal_identity_is_not_a_behaviour_equivalence_claim():
    """Two artifacts with the same ref are the same bytes. Behaviour needs evaluation_ref."""
    a, b = prog_artifact(F.ECHO), prog_artifact(dict(F.ECHO))
    assert organism_ref(a) == organism_ref(b)
    # ...but the same artifact under a different budget is a different EVALUATION
    s1, s2 = F.echo_spec((1,)), F.echo_spec((1, 2))
    e1 = evaluation_ref(organism_ref(a), RUNTIME_HASH, AFFORDANCE_HASH, LIBRARY_VERSION,
                        s1["spec_id"], 0, 4, "budget_status_only")
    e2 = evaluation_ref(organism_ref(a), RUNTIME_HASH, AFFORDANCE_HASH, LIBRARY_VERSION,
                        s2["spec_id"], 0, 4, "budget_status_only")
    assert e1 != e2


# =============================================================== PR-ID-c

def test_prid_c_families_cannot_collide_even_with_an_identical_body():
    """The adversarial case: a rule table whose body IS a player manifest."""
    a = prog_artifact(F.ECHO)
    b = rule_artifact(F.ECHO)                       # same body, different family
    assert organism_ref(a) != organism_ref(b)


def test_prid_c_encoding_is_unambiguous_by_key_set():
    """Program docs carry the 8 manifest keys; wrapped docs carry exactly 4. Never equal."""
    prog_doc = hashed_document(prog_artifact(F.ECHO))
    rule_doc = hashed_document(rule_artifact({"bits": [1]}))
    assert set(prog_doc) == set(F.ECHO)
    assert set(rule_doc) == set(IDENTITY_BEARING)
    assert set(prog_doc) != set(rule_doc)


def test_prid_c_genome_and_rule_table_with_equal_bodies_differ():
    body = [0, 1, 1, 0]
    g = artifact_manifest(FAMILY_GENOME, body, "g.bitstring.v0", "g.v0")
    r = artifact_manifest(FAMILY_RULE_TABLE, body, "g.bitstring.v0", "g.v0")
    assert organism_ref(g) != organism_ref(r)


def test_prid_c_matching_identity_is_not_independent_replication():
    """Recomputing a ref from the same bytes is arithmetic, not a second observation."""
    art = prog_artifact(F.ECHO)
    assert organism_ref(art) == organism_ref(art)
    spec = F.echo_spec((1,))
    e = evaluation_ref(organism_ref(art), RUNTIME_HASH, AFFORDANCE_HASH, LIBRARY_VERSION,
                       spec["spec_id"], 0, 4, "budget_status_only")
    # two observations of the SAME evaluation in the same world are distinguished only by an
    # explicit occurrence marker; without one they are the same reference, by design.
    assert observation_ref(e, "wld_x") == observation_ref(e, "wld_x")
    assert observation_ref(e, "wld_x", occurrence=1) != observation_ref(e, "wld_x", occurrence=2)


def test_prid_c_malformed_artifacts_fail_closed():
    with pytest.raises(IdentityError):
        artifact_manifest("not_a_family", {}, "r", "s")
    with pytest.raises(IdentityError):
        artifact_manifest(FAMILY_PROGRAM, {"schema_version": "x"}, REPR_PLAYER_MANIFEST_V0, "s")
    with pytest.raises(IdentityError):
        organism_ref({"schema_version": "wrong", "family": "program"})
    with pytest.raises(IdentityError):
        organism_ref(dict(prog_artifact(F.ECHO), surprise=1))


# =============================================================== legacy continuity

def test_program_ref_reduces_exactly_to_the_legacy_organism_id():
    """Sixty-four fossils depend on this. organism_ref MUST NOT mint a second id for a program."""
    with open(REGISTRY, encoding="utf-8") as f:
        entries = json.load(f)["entries"]
    for e in entries[:12]:
        art = prog_artifact(e["manifest"])
        assert legacy_organism_id(art) == e["organism_id"]
        assert organism_ref(art) == "sha256:" + e["organism_id"]
        assert hash_obj(e["manifest"]) == e["organism_id"]


def test_legacy_id_is_refused_for_non_program_families():
    with pytest.raises(IdentityError):
        legacy_organism_id(rule_artifact({"bits": [1]}))


# =============================================================== WP-X8 fixture

def test_x8_fixture_is_equal_score_and_behaviourally_different():
    """X8-a needs exactly this: same score, different observable behaviour, distinct identities."""
    pair = F.x8_equal_score_pair()
    ra = evaluate(pair["a"], pair["spec"])
    rb = evaluate(pair["b"], pair["spec"])
    assert ra["cases_passed"] == rb["cases_passed"] == 0          # EQUAL SCORE
    assert ra["status_counts"] != rb["status_counts"]             # DIFFERENT BEHAVIOUR
    assert ra["ops_total"] != rb["ops_total"]
    assert organism_ref(prog_artifact(pair["a"])) != organism_ref(prog_artifact(pair["b"]))


def test_x8_fixture_file_matches_the_code():
    """The shipped fixture must not drift from the fixtures module it was generated from."""
    assert os.path.exists(X8), "run proteus/eval/emit_x8_fixture.py"
    with open(X8, encoding="utf-8") as f:
        doc = json.load(f)
    pair = F.x8_equal_score_pair()
    assert doc["artifacts"]["a"]["organism_ref"] == organism_ref(prog_artifact(pair["a"]))
    assert doc["artifacts"]["b"]["organism_ref"] == organism_ref(prog_artifact(pair["b"]))
    assert doc["equal_score"] is True
    assert doc["behaviour_differs"] is True
