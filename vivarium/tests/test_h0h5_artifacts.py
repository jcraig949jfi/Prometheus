"""H0-H5 iteration 1: the artifact slot's contract, offline.

What is tested HERE is arithmetic and algebra -- exact keys, canonical bytes,
digest binding, closure, limits, sealed identity, admission. What is tested
against a real engine, a real database and a real PEW namespace is in
tests/test_h0h5_slice.py: everything that turns on authority, on the queue's
state machine, or on a fossil actually landing. The split is deliberate and the
order's "each a real execution, not a mock" applies to the second file.
"""
from __future__ import annotations

import json

import pytest

from artifact_fixtures import LocalResolver, input_set, probe_spec
from conftest import make_spec
from viv import artifacts as _a
from viv import executors as _ex
from viv import kinds as _kinds
from viv import preflight as _pf
from viv import queue as _q
from viv import spec as _spec
from viv.request import ExecutionRequest

ITEMS = [[0, 0, 1], [1, 1, 0], [1, 0, 1]]


def _loaded(items=ITEMS, **kw):
    """Hydrate one artifact through the full preflight and return everything."""
    _obj, raw, slot = input_set(items, **kw)
    res = LocalResolver({slot["digest"]: (raw, "w-src", "art-1")})
    pf = _pf.Preflight(resolver=res,
                       locators={slot["digest"]: {"source_world": "w-src",
                                                  "source_artifact": "art-1"}})
    inputs, receipt = pf.hydrate({"failure_inputs": slot})
    return slot, raw, inputs, receipt, res


# ===========================================================================
# 1. THE SLOT CONTRACT -- exact keys, resolved values, no placeholders
# ===========================================================================

def test_a_well_formed_slot_passes():
    _obj, _raw, slot = input_set(ITEMS)
    assert _a.check_slot("failure_inputs", slot) == []


def test_the_slot_field_set_is_exactly_the_designs():
    assert _a.SLOT_FIELDS == ("digest", "artifact_type", "schema_version",
                              "codec", "expected_bytes", "interface_id")


@pytest.mark.parametrize("drop", list(_a.SLOT_FIELDS))
def test_every_slot_field_is_required(drop):
    _obj, _raw, slot = input_set(ITEMS)
    slot.pop(drop)
    reasons = _a.check_slot("failure_inputs", slot)
    assert any(drop in r for r in reasons), reasons


def test_an_extra_slot_key_is_refused_not_ignored():
    """The same rule the payload contract already applies, one level down."""
    _obj, _raw, slot = input_set(ITEMS)
    slot["source_world"] = "w-src"      # a locator leaking INTO the seal
    reasons = _a.check_slot("failure_inputs", slot)
    assert any("unknown key" in r for r in reasons), reasons


def test_a_slot_declaring_an_unreadable_schema_version_is_refused():
    _obj, _raw, slot = input_set(ITEMS)
    slot["schema_version"] = "99"
    assert _a.check_slot("failure_inputs", slot)


def test_an_interface_belonging_to_another_type_is_refused():
    _obj, _raw, slot = input_set(ITEMS)
    slot["artifact_type"] = "failure_input_set"
    slot["interface_id"] = "boolean-inputs-v1"
    assert _a.check_slot("failure_inputs", slot) == []
    slot["artifact_type"] = "program_component"      # unknown type
    assert _a.check_slot("failure_inputs", slot)


def test_a_digest_that_is_not_a_digest_is_refused():
    _obj, _raw, slot = input_set(ITEMS)
    for bad in ("sha256:xyz", "deadbeef", "sha256:" + "A" * 64, ""):
        slot["digest"] = bad
        assert _a.check_slot("failure_inputs", slot), bad


# ===========================================================================
# 2. THE LOCATOR -- immutable addresses only
# ===========================================================================

@pytest.mark.parametrize("bad", [
    {"source_world": "w-latest", "source_artifact": "a1"},
    {"source_world": "w1", "source_artifact": "art-*"},
    {"source_world": "https://example/w1", "source_artifact": "a1"},
    {"source_world": "w1", "source_artifact": "../a1"},
    {"source_world": "w1", "source_artifact": "HEAD"},
])
def test_a_mutable_lookup_is_refused_by_syntax(bad):
    """C1 forbids latest/glob/mutable URL. The only way to keep that promise
    is to refuse the syntax, not to hope no producer writes it."""
    reasons = _a.check_locator("failure_inputs", bad)
    assert any("MUTABLE" in r for r in reasons), reasons


def test_a_locator_with_an_extra_key_is_refused():
    assert _a.check_locator("s", {"source_world": "w1", "source_artifact": "a",
                                  "note": "hello"})


# ===========================================================================
# 3. THE CODEC -- canonical, or nothing
# ===========================================================================

def test_non_canonical_json_is_refused_even_though_it_parses():
    """Two byte strings denoting one object would be two digests for one
    input, which is the ambiguity content-addressing exists to remove."""
    obj = {"artifact_type": "failure_input_set", "schema_version": "1",
           "interface_id": "boolean-inputs-v1", "n_bits": 1, "items": [[1]]}
    pretty = json.dumps(obj, indent=2).encode()      # parses, not canonical
    with pytest.raises(_a.PreflightRejected) as e:
        _a.CODECS["canonical-json-v1"](pretty)
    assert e.value.rejection_class == _a.MALFORMED
    assert "CANONICAL" in str(e.value)


def test_bytes_that_are_not_json_are_malformed():
    with pytest.raises(_a.PreflightRejected) as e:
        _a.CODECS["canonical-json-v1"](b"\x00\x01not json")
    assert e.value.rejection_class == _a.MALFORMED


def test_booleans_are_refused_in_bit_rows():
    """true/false round-trip as different bytes than 1/0, so admitting them
    would let two encodings of one input set exist."""
    obj = {"artifact_type": "failure_input_set", "schema_version": "1",
           "interface_id": "boolean-inputs-v1", "n_bits": 1,
           "items": [[True]]}
    raw = _a.canonical_bytes(obj)
    with pytest.raises(_a.PreflightRejected) as e:
        _a.INTERFACES["boolean-inputs-v1"][1](json.loads(raw), _a.ALPHA)
    assert e.value.rejection_class == _a.MALFORMED


# ===========================================================================
# 4. PREFLIGHT -- the ten steps, each refusing
# ===========================================================================

def test_a_clean_load_produces_a_receipt_with_what_was_verified():
    slot, raw, inputs, receipt, res = _loaded()
    assert receipt["loaded"] is True
    assert receipt["bytes_loaded"] == len(raw)
    assert receipt["closure_manifest"] == [slot["digest"]]
    assert set(receipt["verified"]) >= {"digest", "size", "codec_canonical",
                                        "artifact_type", "interface_id"}
    assert inputs["failure_inputs"].shape["item_count"] == len(ITEMS)


def test_wrong_digest_is_refused_and_names_both_hashes():
    _obj, raw, slot = input_set(ITEMS)
    other, _raw2, _s2 = input_set([[1, 1, 1]])
    wrong = _a.canonical_bytes(other)
    res = LocalResolver({slot["digest"]: (wrong, "w-src", "art-1")})
    pf = _pf.Preflight(resolver=res,
                       locators={slot["digest"]: {"source_world": "w-src",
                                                  "source_artifact": "art-1"}})
    with pytest.raises(_a.PreflightRejected) as e:
        pf.hydrate({"failure_inputs": slot})
    assert e.value.rejection_class in (_a.SIZE_MISMATCH, _a.DIGEST_MISMATCH)


def test_a_digest_mismatch_at_equal_size_is_caught_by_the_hash():
    """Same byte count, different bytes: only the digest can see this."""
    a_items = [[0, 0, 1], [1, 1, 0], [1, 0, 1]]
    b_items = [[0, 0, 1], [1, 1, 0], [1, 1, 1]]
    _o1, _r1, slot = input_set(a_items)
    _o2, raw2, slot2 = input_set(b_items)
    assert slot["expected_bytes"] == slot2["expected_bytes"]
    assert slot["digest"] != slot2["digest"]
    res = LocalResolver({slot["digest"]: (raw2, "w-src", "art-1")})
    pf = _pf.Preflight(resolver=res,
                       locators={slot["digest"]: {"source_world": "w-src",
                                                  "source_artifact": "art-1"}})
    with pytest.raises(_a.PreflightRejected) as e:
        pf.hydrate({"failure_inputs": slot})
    assert e.value.rejection_class == _a.DIGEST_MISMATCH


def test_an_absent_artifact_is_refused():
    _obj, _raw, slot = input_set(ITEMS)
    pf = _pf.Preflight(resolver=LocalResolver({}),
                       locators={slot["digest"]: {"source_world": "w-src",
                                                  "source_artifact": "nope"}})
    with pytest.raises(_a.PreflightRejected) as e:
        pf.hydrate({"failure_inputs": slot})
    assert e.value.rejection_class == _a.ABSENT


def test_an_unauthorized_world_is_refused():
    _obj, raw, slot = input_set(ITEMS)
    res = LocalResolver({slot["digest"]: (raw, "w-theirs", "art-1")},
                        authorized={"w-mine"})
    pf = _pf.Preflight(resolver=res,
                       locators={slot["digest"]: {"source_world": "w-theirs",
                                                  "source_artifact": "art-1"}})
    with pytest.raises(_a.PreflightRejected) as e:
        pf.hydrate({"failure_inputs": slot})
    assert e.value.rejection_class == _a.UNAUTHORIZED


def test_a_missing_locator_is_refused_before_any_fetch():
    _obj, _raw, slot = input_set(ITEMS)
    res = LocalResolver({})
    pf = _pf.Preflight(resolver=res, locators={})
    with pytest.raises(_a.PreflightRejected) as e:
        pf.hydrate({"failure_inputs": slot})
    assert e.value.rejection_class == _a.LOCATOR_MISSING
    assert res.calls == 0


def test_wrong_type_in_the_content_is_refused_even_with_the_right_digest():
    """The bytes are exactly what the spec sealed and they are still not this
    input: the content's own header says it is something else."""
    obj = {"artifact_type": "decoder", "schema_version": "1",
           "interface_id": "boolean-inputs-v1", "n_bits": 1, "items": [[1]]}
    raw = _a.canonical_bytes(obj)
    slot = {"digest": _a.digest_of(raw), "artifact_type": "failure_input_set",
            "schema_version": "1", "codec": "canonical-json-v1",
            "expected_bytes": len(raw), "interface_id": "boolean-inputs-v1"}
    res = LocalResolver({slot["digest"]: (raw, "w-src", "a")})
    pf = _pf.Preflight(resolver=res,
                       locators={slot["digest"]: {"source_world": "w-src",
                                                  "source_artifact": "a"}})
    with pytest.raises(_a.PreflightRejected) as e:
        pf.hydrate({"failure_inputs": slot})
    assert e.value.rejection_class == _a.WRONG_TYPE


def test_an_incompatible_interface_is_refused():
    obj = {"artifact_type": "failure_input_set", "schema_version": "1",
           "interface_id": "boolean-inputs-v2", "n_bits": 1, "items": [[1]]}
    raw = _a.canonical_bytes(obj)
    slot = {"digest": _a.digest_of(raw), "artifact_type": "failure_input_set",
            "schema_version": "1", "codec": "canonical-json-v1",
            "expected_bytes": len(raw), "interface_id": "boolean-inputs-v1"}
    res = LocalResolver({slot["digest"]: (raw, "w-src", "a")})
    pf = _pf.Preflight(resolver=res,
                       locators={slot["digest"]: {"source_world": "w-src",
                                                  "source_artifact": "a"}})
    with pytest.raises(_a.PreflightRejected) as e:
        pf.hydrate({"failure_inputs": slot})
    assert e.value.rejection_class == _a.INCOMPATIBLE_INTERFACE


def test_an_oversize_declaration_is_refused_before_the_fetch():
    """A size limit that only fires after the download is a measurement."""
    _obj, raw, slot = input_set(ITEMS)
    slot["expected_bytes"] = 99_000_000
    res = LocalResolver({slot["digest"]: (raw, "w-src", "a")})
    pf = _pf.Preflight(resolver=res, limits=_a.Limits(per_artifact_bytes=1024),
                       locators={slot["digest"]: {"source_world": "w-src",
                                                  "source_artifact": "a"}})
    with pytest.raises(_a.PreflightRejected) as e:
        pf.hydrate({"failure_inputs": slot})
    assert e.value.rejection_class == _a.OVERSIZE
    assert res.calls == 0, "the fetch happened before the limit was applied"


def test_too_many_items_is_refused_against_the_declared_limit():
    big = [[0, 0, 1]] * 50
    _obj, raw, slot = input_set(big)
    res = LocalResolver({slot["digest"]: (raw, "w-src", "a")})
    pf = _pf.Preflight(resolver=res, limits=_a.Limits(max_items=10),
                       locators={slot["digest"]: {"source_world": "w-src",
                                                  "source_artifact": "a"}})
    with pytest.raises(_a.PreflightRejected) as e:
        pf.hydrate({"failure_inputs": slot})
    assert e.value.rejection_class == _a.LIMIT_EXCEEDED


# ===========================================================================
# 5. CLOSURE
# ===========================================================================

def _with_dependency():
    _dobj, draw, dslot = input_set([[1, 1, 1], [0, 0, 0]])
    _obj, raw, slot = input_set(ITEMS, dependencies=[dslot])
    store = {dslot["digest"]: (draw, "w-src", "dep-1"),
             slot["digest"]: (raw, "w-src", "root-1")}
    locators = {dslot["digest"]: {"source_world": "w-src",
                                  "source_artifact": "dep-1"},
                slot["digest"]: {"source_world": "w-src",
                                 "source_artifact": "root-1"}}
    return slot, dslot, store, locators


def test_a_dependency_is_resolved_verified_and_manifested():
    slot, dslot, store, locators = _with_dependency()
    pf = _pf.Preflight(resolver=LocalResolver(store), locators=locators)
    inputs, receipt = pf.hydrate({"failure_inputs": slot})
    assert receipt["closure_size"] == 2
    assert set(receipt["closure_manifest"]) == {slot["digest"], dslot["digest"]}
    # The dependency's rows are consumed, in declared order after the root's.
    assert inputs["failure_inputs"].all_items() == (
        (0, 0, 1), (1, 1, 0), (1, 0, 1), (1, 1, 1), (0, 0, 0))


def test_a_dependency_without_a_locator_is_a_missing_dependency():
    slot, dslot, store, locators = _with_dependency()
    locators.pop(dslot["digest"])
    pf = _pf.Preflight(resolver=LocalResolver(store), locators=locators)
    with pytest.raises(_a.PreflightRejected) as e:
        pf.hydrate({"failure_inputs": slot})
    assert e.value.rejection_class == _a.MISSING_DEPENDENCY


def test_a_content_addressed_cycle_cannot_be_CONSTRUCTED_at_all():
    """The stronger fact, established rather than assumed.

    C1 says alpha forbids dependency cycles, and preflight refuses one. But
    under honest content addressing a cycle cannot be built: A can name B only
    if A's bytes contain sha256(B), and B can name A only if B's bytes contain
    sha256(A) -- each hash is required as an input to the other's preimage.
    Nothing here can produce that pair, which is why the test below reaches
    past the fetch to exercise the guard directly instead of pretending to
    construct one.

    The guard therefore protects against a resolver that serves bytes not
    matching their digest -- and the digest check already refuses that, so it
    is defence in depth, and saying which is better than implying it is
    load-bearing.
    """
    a_obj = {"artifact_type": "failure_input_set", "schema_version": "1",
             "interface_id": "boolean-inputs-v1", "n_bits": 3,
             "items": [[1, 0, 0]], "dependencies": []}
    a_raw = _a.canonical_bytes(a_obj)
    a_digest = _a.digest_of(a_raw)
    # To make A name itself, A's bytes must contain A's own hash.
    a_obj["dependencies"] = [{"digest": a_digest,
                              "artifact_type": "failure_input_set",
                              "schema_version": "1",
                              "codec": "canonical-json-v1",
                              "expected_bytes": len(a_raw),
                              "interface_id": "boolean-inputs-v1"}]
    cyclic_raw = _a.canonical_bytes(a_obj)
    assert _a.digest_of(cyclic_raw) != a_digest, (
        "a self-naming artifact would be a sha256 fixed point")


def test_the_cycle_guard_refuses_a_repeat_in_the_chain():
    """Exercised at the guard, since the fetch path cannot reach it."""
    _obj, raw, slot = input_set(ITEMS)
    pf = _pf.Preflight(resolver=LocalResolver({slot["digest"]: (raw, "w", "a")}),
                       locators={slot["digest"]: {"source_world": "w",
                                                  "source_artifact": "a"}})
    with pytest.raises(_a.PreflightRejected) as e:
        pf.load("failure_inputs", slot, depth=1, chain=(slot["digest"],))
    assert e.value.rejection_class == _a.DEPENDENCY_CYCLE


def test_a_dependency_chain_two_deep_resolves_in_order():
    """The closure is a real recursion, not one hard-coded level."""
    _o3, r3, s3 = input_set([[1, 1, 1]])
    _o2, r2, s2 = input_set([[0, 1, 0]], dependencies=[s3])
    _o1, r1, s1 = input_set(ITEMS, dependencies=[s2])
    store = {s1["digest"]: (r1, "w", "a1"), s2["digest"]: (r2, "w", "a2"),
             s3["digest"]: (r3, "w", "a3")}
    loc = {d: {"source_world": "w", "source_artifact": a}
           for d, (_b, _w, a) in store.items()}
    pf = _pf.Preflight(resolver=LocalResolver(store), locators=loc)
    inputs, receipt = pf.hydrate({"failure_inputs": s1})
    assert receipt["closure_size"] == 3
    # Depth-first, children recorded before their parent.
    assert receipt["closure_manifest"] == [s3["digest"], s2["digest"],
                                           s1["digest"]]
    assert inputs["failure_inputs"].all_items() == (
        (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 0), (1, 1, 1))


def test_closure_depth_is_bounded():
    slot, dslot, store, locators = _with_dependency()
    pf = _pf.Preflight(resolver=LocalResolver(store), locators=locators,
                       limits=_a.Limits(max_depth=0))
    with pytest.raises(_a.PreflightRejected) as e:
        pf.hydrate({"failure_inputs": slot})
    assert e.value.rejection_class == _a.LIMIT_EXCEEDED


def test_an_address_the_closure_never_consumed_is_refused():
    """An unread entry travelling beside a sealed spec is a channel."""
    _obj, raw, slot = input_set(ITEMS)
    _o2, raw2, spare = input_set([[1, 1, 1]])
    store = {slot["digest"]: (raw, "w", "a"), spare["digest"]: (raw2, "w", "b")}
    locators = {slot["digest"]: {"source_world": "w", "source_artifact": "a"},
                spare["digest"]: {"source_world": "w", "source_artifact": "b"}}
    pf = _pf.Preflight(resolver=LocalResolver(store), locators=locators)
    with pytest.raises(_a.PreflightRejected) as e:
        pf.hydrate({"failure_inputs": slot})
    assert e.value.rejection_class == _a.CONTRACT_INVALID
    assert "channel" in str(e.value)


# ===========================================================================
# 6. THE CACHE -- authorization, not a dictionary
# ===========================================================================

def test_the_cache_refuses_a_hit_for_a_principal_it_never_authorized():
    """The obvious digest -> bytes cache is a permission bypass. This one
    records WHO was authorized, so an unauthorized caller misses and is sent
    back to the engine to be refused there."""
    cache = _a.LoaderCache()
    cache.put("sha256:" + "a" * 64, b"secret", ("client-a", "w-a"))
    assert cache.get("sha256:" + "a" * 64, ("client-a", "w-a")) == b"secret"
    assert cache.get("sha256:" + "a" * 64, ("client-b", "w-b")) is None
    assert cache.stats()["refused_hits"] == 1


def test_a_second_slot_over_one_digest_is_fetched_once():
    """Load-once, for the principal actually authorized."""
    _obj, raw, slot = input_set(ITEMS)
    res = LocalResolver({slot["digest"]: (raw, "w", "a")})
    loc = {slot["digest"]: {"source_world": "w", "source_artifact": "a"}}
    pf = _pf.Preflight(resolver=res, locators=loc)
    pf.hydrate({"failure_inputs": slot})
    assert res.calls == 1
    assert pf.cache.stats()["distinct_artifacts"] == 1


# ===========================================================================
# 7. IMMUTABILITY AND THE KIND'S ISOLATION
# ===========================================================================

def test_the_hydrated_input_cannot_be_mutated():
    _slot, _raw, inputs, _receipt, _res = _loaded()
    data = inputs["failure_inputs"].data
    with pytest.raises(TypeError):
        data["items"] = ()
    with pytest.raises(TypeError):
        data["items"][0][0] = 9


def test_the_kind_reports_that_its_input_refused_mutation():
    slot, _raw, inputs, _receipt, _res = _loaded()
    out = _ex.run(probe_spec(slot), seed=1, inputs=inputs)
    assert out["inputs_immutable"] is True


def test_a_kind_with_slots_called_without_hydration_is_refused():
    """Reaching the executor with no inputs means preflight was bypassed."""
    _obj, _raw, slot = input_set(ITEMS)
    with pytest.raises(_ex.ExecutorUnavailable) as e:
        _ex.run(probe_spec(slot), seed=1, inputs=None)
    assert "bypassed" in str(e.value)


def test_a_kind_without_slots_handed_inputs_is_refused():
    """An undeclared input is an undeclared channel."""
    with pytest.raises(_ex.ExecutorUnavailable) as e:
        _ex.run(make_spec(), seed=1, inputs={"failure_inputs": object()})
    assert "undeclared" in str(e.value)


# ===========================================================================
# 8. SEALED IDENTITY -- the property the whole design turns on
# ===========================================================================

def test_changing_a_consumed_digest_changes_the_sealed_identity():
    _o1, _r1, slot_a = input_set(ITEMS)
    _o2, _r2, slot_b = input_set(ITEMS + [[1, 1, 1]])
    assert (_spec.spec_hash(probe_spec(slot_a))
            != _spec.spec_hash(probe_spec(slot_b)))


def test_changing_provenance_does_not_change_the_sealed_identity(conn, schema):
    """Two rows, opposite provenance, one hash. That is what makes an arm
    comparison a comparison."""
    _obj, raw, slot = input_set(ITEMS)
    spec = probe_spec(slot)
    loc = {slot["digest"]: {"source_world": "w-1", "source_artifact": "a-1"}}
    a = _q.enqueue(conn, created_by="archaeon:policy-A",
                   source_reason="selected by the frozen policy",
                   experiment_spec=spec, artifact_locators=loc,
                   family_id="F", arm_id="treatment", schema=schema)
    b = _q.enqueue(conn, created_by="human:jim",
                   source_reason="hand-issued control",
                   experiment_spec=spec, artifact_locators=loc,
                   family_id="F", arm_id="control", schema=schema)
    conn.commit()
    assert (_q.get(conn, a, schema=schema)["spec_hash"]
            == _q.get(conn, b, schema=schema)["spec_hash"])


def test_changing_only_the_locator_does_not_change_the_sealed_identity(
        conn, schema):
    """The address is not the input. Two copies of byte-identical artifacts in
    two different worlds are the same experiment."""
    _obj, raw, slot = input_set(ITEMS)
    spec = probe_spec(slot)
    a = _q.enqueue(conn, created_by="t", source_reason="copy in world 1",
                   experiment_spec=spec, schema=schema,
                   artifact_locators={slot["digest"]: {
                       "source_world": "w-1", "source_artifact": "a-1"}})
    b = _q.enqueue(conn, created_by="t", source_reason="copy in world 2",
                   experiment_spec=spec, schema=schema,
                   artifact_locators={slot["digest"]: {
                       "source_world": "w-2", "source_artifact": "a-2"}})
    conn.commit()
    assert (_q.get(conn, a, schema=schema)["spec_hash"]
            == _q.get(conn, b, schema=schema)["spec_hash"])


def test_two_different_locators_over_identical_bytes_execute_identically():
    """THE claim that justifies widening ExecutionRequest to four fields: a
    locator can decide WHETHER a run happens, never WHAT it computes."""
    _obj, raw, slot = input_set(ITEMS)
    spec = probe_spec(slot)
    outs = []
    for world, aid in (("w-north", "art-A"), ("w-south", "art-B")):
        res = LocalResolver({slot["digest"]: (raw, world, aid)})
        pf = _pf.Preflight(resolver=res, locators={
            slot["digest"]: {"source_world": world, "source_artifact": aid}})
        inputs, receipt = pf.hydrate({"failure_inputs": slot})
        outs.append((_ex.run(spec, seed=1, inputs=inputs),
                     receipt["closure_manifest_hash"]))
    assert outs[0][0] == outs[1][0], "the locator changed the RESULT"
    assert outs[0][1] == outs[1][1], "the locator changed the manifest"


def test_an_old_no_artifact_spec_keeps_its_identity_and_behaviour():
    """Nothing about the loader touched the kinds that existed before it."""
    old = make_spec()
    assert _spec.spec_hash(old) == _spec.spec_hash(make_spec())
    assert _kinds.get("noop_v0").artifact_slots == frozenset()
    assert _pf.slots_of(old) == {}
    assert _ex.run(old, seed=1)["executed"] is True


# ===========================================================================
# 9. ADMISSION
# ===========================================================================

def test_a_spec_whose_slot_is_malformed_is_refused_at_admission(conn, schema):
    """Placeholders never enter a queue."""
    _obj, _raw, slot = input_set(ITEMS)
    slot["digest"] = "TBD"
    with pytest.raises(Exception) as e:
        _q.enqueue(conn, created_by="t", source_reason="t",
                   experiment_spec=probe_spec(slot), schema=schema,
                   artifact_locators={}, )
    assert "digest" in str(e.value) or "slot" in str(e.value)


def test_a_spec_with_no_locator_for_its_own_slot_is_refused(conn, schema):
    _obj, _raw, slot = input_set(ITEMS)
    with pytest.raises(ValueError) as e:
        _q.enqueue(conn, created_by="t", source_reason="t",
                   experiment_spec=probe_spec(slot), schema=schema)
    assert "no locator" in str(e.value)


def test_a_mutable_locator_is_refused_at_admission(conn, schema):
    _obj, _raw, slot = input_set(ITEMS)
    with pytest.raises(ValueError) as e:
        _q.enqueue(conn, created_by="t", source_reason="t",
                   experiment_spec=probe_spec(slot), schema=schema,
                   artifact_locators={slot["digest"]: {
                       "source_world": "w-latest", "source_artifact": "a"}})
    assert "MUTABLE" in str(e.value)


def test_the_address_book_reaches_the_request_and_provenance_does_not(
        conn, schema):
    _obj, _raw, slot = input_set(ITEMS)
    loc = {slot["digest"]: {"source_world": "w-1", "source_artifact": "a-1"}}
    eid = _q.enqueue(conn, created_by="archaeon:C_frozen_S17",
                     source_reason="weak_signal-lookalike",
                     source_evidence={"detector": "D1"},
                     experiment_spec=probe_spec(slot), family_id="F1",
                     arm_id="C_frozen_S17", artifact_locators=loc,
                     schema=schema)
    conn.commit()
    req = ExecutionRequest.from_queue_row(_q.get(conn, eid, schema=schema))
    assert req.artifact_locators == loc
    blob = json.dumps({"loc": req.artifact_locators, "spec": req.spec})
    for leaked in ("archaeon", "C_frozen_S17", "D1", "F1", "weak_signal"):
        assert leaked not in blob


def test_the_address_book_is_frozen_after_admission(conn, schema):
    """Re-addressing a row would make it a record of two resolutions wearing
    one identity."""
    _obj, _raw, slot = input_set(ITEMS)
    eid = _q.enqueue(conn, created_by="t", source_reason="t",
                     experiment_spec=probe_spec(slot), schema=schema,
                     artifact_locators={slot["digest"]: {
                         "source_world": "w-1", "source_artifact": "a-1"}})
    conn.commit()
    import psycopg2
    with pytest.raises(psycopg2.errors.RaiseException) as e:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE %s.research_experiment_queue SET artifact_locators="
                "'{}'::jsonb WHERE experiment_id=%%s" % schema, (eid,))
    conn.rollback()
    assert "address book" in str(e.value)


# ===========================================================================
# 10. RESOURCES
# ===========================================================================

def test_unavailable_is_never_reported_as_zero():
    from viv import resources as _r
    v = _r.Meter().start().vector()
    assert v["gpu_seconds"]["enforcement"] == _r.UNAVAILABLE
    assert v["gpu_seconds"]["quantity"] is None


def test_the_enforcement_summary_separates_enforceable_from_measured():
    from viv import resources as _r
    m = _r.Meter().start()
    m.count("artifact_bytes", 100)
    v = m.vector(artifact_bytes_limit=1024, wall_limit=60)
    s = _r.enforcement_summary(v)
    assert "artifact_bytes" in s[_r.ENFORCEABLE]
    assert "wall_seconds" in s[_r.ENFORCEABLE]
    assert "cpu_seconds" in s[_r.MEASURED]
    assert "gpu_seconds" in s[_r.UNAVAILABLE]


def test_a_limitless_run_reports_wall_seconds_as_measured_not_enforceable():
    from viv import resources as _r
    v = _r.Meter().start().vector()
    assert v["wall_seconds"]["enforcement"] == _r.MEASURED


def test_peak_memory_is_marked_never_additive_and_bytes_are():
    """C4: sum additive work quantities; never sum peak-memory samples."""
    from viv import resources as _r
    m = _r.Meter().start()
    m.count("artifact_bytes", 10)
    v = m.vector()
    assert v["peak_memory_bytes"]["additive"] is False
    assert v["artifact_bytes"]["additive"] is True


def test_the_budget_is_debited_before_the_fetch_not_after():
    """A debit taken afterwards is an accounting entry, not a limit."""
    _obj, raw, slot = input_set(ITEMS)
    order = []
    res = LocalResolver({slot["digest"]: (raw, "w", "a")})
    real = res.resolve

    def watched(digest, locator):
        order.append("fetch")
        return real(digest, locator)

    res.resolve = watched
    pf = _pf.Preflight(resolver=res,
                       locators={slot["digest"]: {"source_world": "w",
                                                  "source_artifact": "a"}},
                       debit=lambda r, n: order.append("debit"))
    pf.hydrate({"failure_inputs": slot})
    assert order == ["debit", "fetch"]


def test_a_refused_budget_stops_the_fetch_entirely():
    _obj, raw, slot = input_set(ITEMS)
    res = LocalResolver({slot["digest"]: (raw, "w", "a")})

    def broke(resource, amount):
        raise _pf.BudgetExhausted("no allowance for %s bytes" % amount)

    pf = _pf.Preflight(resolver=res, debit=broke,
                       locators={slot["digest"]: {"source_world": "w",
                                                  "source_artifact": "a"}})
    with pytest.raises(_pf.BudgetExhausted):
        pf.hydrate({"failure_inputs": slot})
    assert res.calls == 0


def test_peak_memory_is_measured_where_the_host_keeps_a_peak_counter():
    """It was reported `unavailable` on this host until the ctypes signature
    was declared -- an untyped GetCurrentProcess truncates the pseudo-handle
    and the call silently fails. `unavailable` is the honest reading of a
    failed call, which is exactly why it must not be allowed to stand for a
    counter that does work."""
    import os as _os

    from viv import resources as _r
    v = _r.Meter().start().vector()
    peak = v["peak_memory_bytes"]
    if _os.name == "nt":
        assert peak["enforcement"] == _r.MEASURED, peak["method"]
        assert peak["quantity"] > 0
        assert peak["scope"] == "process"
    else:
        assert peak["enforcement"] in (_r.MEASURED, _r.UNAVAILABLE)
        assert (peak["quantity"] is None) == (peak["enforcement"]
                                              == _r.UNAVAILABLE)
