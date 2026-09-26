"""ENVGATE-01 instrument tests (directive 2026-09-24): pairing, transforms, RNG isolation, memo/ruler exactness, chamber isolation,
physics identity with the frozen z80atlas engine, and the frozen decision logic."""
from __future__ import annotations

import itertools

import pytest

from proteus.foundry.prng import SplitMix64, seed_from
from archaeon.z80atlas import vm
from archaeon.z80atlas.census import copier_census as C
from archaeon.envgate import mechanism as M, engine as EG, ruler as R, analyze as A, preflight as PF
from archaeon.envgate.block import run_block

SMALL = {"K_chambers": 32, "dwell": 4, "refills": 3}


def test_paired_arms_receive_byte_identical_inflow_sequences():
    r = run_block(3, SMALL)
    assert len(set(r["pairing_sha256"].values())) == 1 and r["arrivals"] == 96


def test_inflow_sequence_does_not_depend_on_which_arms_run():
    a = run_block(3, SMALL, arms=["U"])["pairing_sha256"]["U"]; b = run_block(3, SMALL, arms=["BAND_BLOCK"])["pairing_sha256"]["BAND_BLOCK"]
    c = run_block(3, SMALL)["pairing_sha256"]["RESCUE_128"]; d = run_block(4, SMALL, arms=["U"])["pairing_sha256"]["U"]
    assert a == b == c and a != d


def test_transforms_block_exactly_and_pass_everything_else_unchanged():
    r = SplitMix64(seed_from("test.transforms", 1))
    for _ in range(200000):
        u, v = r.next_u32(), r.next_u32(); base = u >> 24
        for arm in M.ARMS.values():
            x = M.transform(arm, u, v)
            assert x not in arm["_bset"]
            if base not in arm["_bset"]: assert x == base
        assert (M.transform(M.ARMS["RESCUE_128"], u, v) != M.transform(M.ARMS["BAND_BLOCK"], u, v)) == (base == 128)


def test_inflow_and_environment_never_touch_world_or_mutation_rng():
    assert PF.check_rng_isolation()["PASS"]


def test_memo_is_exact():
    r = SplitMix64(seed_from("test.memo", 2)); memo = EG.Memo(cap=500)
    for _ in range(3000):
        t = bytes(r.randbelow(256) for _ in range(32)); n = bytes(r.randbelow(256) for _ in range(32)) if r.randbelow(2) else EG.ZERO; x = (r.randbelow(256),)
        got = memo.run(t, n, x); want = vm.execute(t, n, x, EG.STEP_CAP, True, -1.0)
        assert got == want
        got2 = memo.run(t, n, ((x[0] + 7) % 256,)); assert got2 == vm.execute(t, n, ((x[0] + 7) % 256,), EG.STEP_CAP, True, -1.0)


def test_arrival_ruler_equals_the_frozen_census_ruler():
    import json
    hits = json.loads(PF.CENSUS_HITS.read_text(encoding="utf-8"))["hits"]["vmcopy32"][:40]
    tapes = [bytes.fromhex(h["tape"]) for h in hits] + list(C.stream_tapes("TEST-ENVGATE-RULER", 0, 300, 32))
    for t in tapes:
        assert R.measure(t)["class"] == C.classify(C.sweep(t, True), 32)
    for h in hits:
        assert R.measure(bytes.fromhex(h["tape"])).get("exact_inputs", []) == h["exact_inputs"]


def test_chambers_are_write_protected_and_arrivals_are_tested_unchanged():
    tape = bytes.fromhex(C.SPECIMEN)
    r = run_block(20_001, {"K_chambers": 8, "dwell": 64, "refills": 2}, tapes=itertools.repeat(tape))
    for s in r["arms"].values():
        assert s["refused_into_chamber"] == 0 and s["n_established"] == 0          # control-origin founders are never scored
    w = EG.World("U", 5, 8); env = EG.EnvStream(5); memo = EG.Memo(); w.arrive(EG.N, tape, 0, 0)
    for e in range(64): w.step(e, env, memo)
    assert w.genomes[EG.N] == tape                                             # no mutation or death in the chamber during dwell


def test_physics_identity_with_frozen_engine():
    assert PF.check_physics_identity(seeds=(7,))["PASS"]


def _blk(b, est, pairing_ok=True):
    arms = {}
    for a in M.ARM_ORDER:
        arms[a] = {"refused_into_chamber": 0, "n_established": len(est.get(a, [])), "established_arrivals": est.get(a, []),
                   "lineages": [{"established": True, "origin": "random_inflow", "arrival": x} for x in est.get(a, [])]}
    return {"block": b, "arrivals": 100, "ruler_counts": {}, "hits": {}, "pairing_sha256": {a: ("x" if pairing_ok or a != "U" else "y") for a in M.ARM_ORDER}, "arms": arms}


def test_decision_logic_supported_partial_and_failure():
    est = {"U": list(range(8)), "SHAM_BLOCK": list(range(8)), "RESCUE_128": list(range(7)), "BLOCK_128": [0], "BAND_BLOCK": []}
    assert A.analyze([_blk(0, est)], 1)["verdict"] == "GATING_CAUSALLY_SUPPORTED"
    est2 = dict(est, RESCUE_128=[])
    assert A.analyze([_blk(0, est2)], 1)["verdict"] == "GATING_PARTIALLY_SUPPORTED"
    same = {a: list(range(8)) for a in M.ARM_ORDER}
    res = A.analyze([_blk(0, same)], 1); assert res["verdict"] == "GATING_NOT_SUPPORTED" and res["falsifiers"]["F1_BAND_as_U"]
    assert A.analyze([_blk(0, {})], 1)["verdict"] == "NO_ESTABLISHMENT_AT_TESTED_EXPOSURE"
    assert A.analyze([_blk(0, est, pairing_ok=False)], 1)["verdict"] == "DESIGN_OR_INSTRUMENT_FAILURE"
    assert A.analyze([_blk(0, est)], 2)["verdict"] == "DESIGN_OR_INSTRUMENT_FAILURE"      # a missing block
