"""The membrane tests, written BEFORE the engine (TDD).

They encode the operator's requirements of 2026-09-21 and the frozen
Campaign 1 envelope E1-E4: canonical artifact bytes, hash before and
after transplant, no donor state outside the artifact, one loader path
for every arm, reset integrity, exhaustive boundary receipts, escrow
beneath the improver, determinism, and a positive control proving the
substrate can express a detectable transferable improvement.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import engine as E  # noqa: E402


# ---------------------------------------------------------------- artifact and hashing
def test_artifact_is_canonical_and_order_independent():
    a = E.Artifact.from_modules({"search": "S", "verify": "V"})
    b = E.Artifact.from_modules({"verify": "V", "search": "S"})
    assert a.bytes == b.bytes and a.sha256 == b.sha256
    assert b"\r\n" not in a.bytes
    assert json.loads(a.bytes.decode())["search"] == "S"


def test_artifact_hash_changes_with_any_byte():
    a = E.Artifact.from_modules({"search": "S"})
    b = E.Artifact.from_modules({"search": "S "})
    assert a.sha256 != b.sha256


def test_vault_extraction_is_positional_and_records_generation():
    lin = E.Lineage(seed=1, base=E.base_image())
    lin.evolve(generations=3, escrow=E.Escrow(200))
    art = lin.extract(generation=3)
    assert art.generation == 3 and art.sha256 == E.Artifact.from_bytes(art.bytes).sha256
    with pytest.raises(ValueError):
        lin.extract(generation=2)          # only the frozen extraction point may be taken


# ---------------------------------------------------------------- recipients and the loader
def test_every_arm_uses_one_loader_path():
    base = E.base_image()
    art = E.Artifact.from_modules(dict(base))
    paths = set()
    for arm, payload in (("scratch", None), ("transplant", art), ("sham", art), ("positive", art)):
        r = E.Recipient.fresh(seed=7)
        rec = r.load(payload)
        paths.add(rec["loader_path"])
    assert len(paths) == 1


def test_transplant_hashes_before_and_after_and_rejects_a_mutated_artifact():
    art = E.Artifact.from_modules(dict(E.base_image()))
    r = E.Recipient.fresh(seed=7)
    rec = r.load(art)
    assert rec["hash_at_extraction"] == rec["hash_at_load"] == art.sha256
    bad = E.Artifact(bytes=art.bytes + b" ", generation=art.generation, sha256=art.sha256)  # claimed hash lies
    with pytest.raises(E.BoundaryViolation):
        E.Recipient.fresh(seed=7).load(bad)


def test_reset_destroys_planted_state_markers():
    r = E.Recipient.fresh(seed=7)
    r.plant_markers()                       # memory, cache, temp, process, environment
    assert r.markers_present()
    r2 = E.Recipient.fresh(seed=7)
    assert not r2.markers_present()
    assert r2.reset_receipt()["markers_destroyed"] is True


def test_no_donor_state_crosses_and_the_receipt_enumerates_everything_read():
    lin = E.Lineage(seed=3, base=E.base_image())
    lin.evolve(generations=3, escrow=E.Escrow(200))
    lin.state.remember("SECRET", "donor-only")
    art = lin.extract(generation=3)
    r = E.Recipient.fresh(seed=9)
    rec = r.load(art)
    assert rec["donor_reads"] == [art.sha256]
    assert "SECRET" not in r.dump_state()
    assert set(rec["crossed"]) == {"artifact_bytes"}


def test_a_negative_fixture_extra_state_crossing_is_caught():
    art = E.Artifact.from_modules(dict(E.base_image()))
    r = E.Recipient.fresh(seed=9)
    with pytest.raises(E.BoundaryViolation):
        r.load(art, smuggle={"cache": {"answer": 42}})   # deliberately extra
    assert r.boundary_log()[-1]["violation"] == "extra_payload:cache"


# ---------------------------------------------------------------- compute escrow
def test_escrow_is_enforced_beneath_the_improver_and_is_equal_across_arms():
    esc = E.Escrow(10)
    r = E.Recipient.fresh(seed=1)
    r.load(None)
    out = r.run_tasks(E.tasks(family="arith", n=20, seed=1), esc)
    assert out["evaluated"] <= 10 and esc.spent <= 10 and out["escrow_exhausted"] is True
    with pytest.raises(E.EscrowExhausted):
        esc.charge(1)


def test_improver_cannot_raise_its_own_escrow():
    esc = E.Escrow(5)
    lin = E.Lineage(seed=1, base=E.base_image())
    with pytest.raises(E.EscrowExhausted):
        lin.evolve(generations=99, escrow=esc)
    assert esc.spent <= 5


# ---------------------------------------------------------------- determinism
def test_same_seed_same_result():
    a = E.Lineage(seed=5, base=E.base_image())
    a.evolve(generations=2, escrow=E.Escrow(300))
    b = E.Lineage(seed=5, base=E.base_image())
    b.evolve(generations=2, escrow=E.Escrow(300))
    assert a.extract(2).sha256 == b.extract(2).sha256


# ---------------------------------------------------------------- the substrate can express a transferable improvement
def test_positive_control_transfers_and_memory_only_does_not():
    """The sensitivity gate: a known-good module must lift a fresh recipient on FRESH
    instances, while cached donor answers must not."""
    fresh = E.tasks(family="numtheory", n=40, seed=99)
    scratch = E.Recipient.fresh(seed=2)
    scratch.load(None)
    s = scratch.run_tasks(fresh, E.Escrow(200))["accuracy"]

    pos = E.Recipient.fresh(seed=2)
    pos.load(E.positive_control_artifact())
    p = pos.run_tasks(fresh, E.Escrow(200))["accuracy"]

    seen = E.tasks(family="numtheory", n=40, seed=1234)      # donor's own instances
    mem = E.Recipient.fresh(seed=2)
    mem.load(None, memory=E.memorised_state(seen))
    m_fresh = mem.run_tasks(fresh, E.Escrow(200))["accuracy"]
    m_seen = mem.run_tasks(seen, E.Escrow(200))["accuracy"]

    assert p - s >= 0.30          # machinery transfers to fresh instances
    assert m_fresh - s <= 0.05    # state does not
    assert m_seen - s >= 0.30     # ... although it clearly helps on what it memorised
