"""Consumer-side integration smoke harness. Uses ONLY the generic ABI and the registry.

    python proteus/integration/run_smoke.py

It answers exactly one question:

    CAN HARMONIA RELIABLY OPERATE THESE ORGANISMS?

It does NOT answer, and must never be extended to answer, "which organisms are good?" There is
no ranking, no scoring, no winner and no interpretation of behaviour anywhere in this file.

THE INPUTS ARE A FIXTURE, NOT A WORLD. The synthetic channels below carry arbitrary constants
with no semantics, no task, no reward and no state that persists between specimens. If this
fixture ever acquires rules, objectives or a name like "World 0", that is a contract violation:
worlds belong to Harmonia and bind to the generic ABI from the other side.

SPECIMENS ARE CHOSEN STRUCTURALLY, NEVER BEHAVIOURALLY. The harness walks the registry and picks
specimens that differ in (tape_words, persist, code_writable, tick_budget) so that the plumbing
is exercised across shapes. It never looks at what a player did in order to decide whether to
test it.

Covers directive section 5 operations A-K and the section 8 error paths.
"""
from __future__ import annotations

import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry.identity import RUNTIME_HASH, canonical_json  # noqa: E402
from proteus.foundry.lineage import checkpoint, restore  # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from  # noqa: E402
from proteus.foundry.vm import ManifestError, Meter, Player, validate_manifest  # noqa: E402
from proteus.integration import registry as R  # noqa: E402

REGISTRY_PATH = os.path.join(HERE, "PLAYER_REGISTRY.json")
FIXTURE_INPUTS = [[3, 5, 8], [13, 21]]      # arbitrary constants. no meaning. not a world.
FIXTURE_N_OUT = 2
FIXTURE_SEED = 0x5C09E
TICKS = 5


def _rng(organism_id):
    """The external RNG contract: the CALLER seeds it, the player can never touch it."""
    return SplitMix64(seed_from("proteus.integration.smoke", FIXTURE_SEED, organism_id))


def _encounter(manifest, organism_id, ticks=TICKS, budget=None):
    """Run a whole deterministic encounter from a fresh state. Returns outputs and statuses."""
    p = Player(manifest)
    st = p.fresh_state()
    rng = _rng(organism_id)
    m = Meter()
    outs, sts = [], []
    for _ in range(ticks):
        o, s = p.run_tick(st, FIXTURE_INPUTS, FIXTURE_N_OUT, rng, meter=m, budget=budget)
        outs.append([list(c) for c in o])
        sts.append(s)
    return outs, sts, st, m


def pick_structurally_diverse(reg, k=8):
    """Distinct structural shapes. Behaviour is never consulted."""
    seen, chosen = set(), []
    for e in reg["entries"]:
        env = e["resource_envelope"]
        key = (env["tape_words"], env["persist"], env["code_writable"], env["tick_budget"])
        if key not in seen:
            seen.add(key)
            chosen.append(e)
        if len(chosen) >= k:
            break
    return chosen


def main():
    results = {"schema_version": "proteus.integration_smoke.v1",
               "question": "Can Harmonia reliably operate these organisms?",
               "explicitly_not": "Which organisms are good?",
               "fixture": {"inputs": FIXTURE_INPUTS, "n_out": FIXTURE_N_OUT,
                           "seed": FIXTURE_SEED, "ticks": TICKS,
                           "not_a_world": "arbitrary constants, no semantics, no task, no reward"},
               "operations": {}, "specimens": [], "error_paths": {}}
    ok = True

    # ---- A. enumerate
    reg = R.load(REGISTRY_PATH)
    ids = R.enumerate_ids(reg)
    results["operations"]["A_enumerate"] = {"passed": len(ids) > 0, "n": len(ids),
                                            "registry_id": reg["registry_id"]}
    print(f"A enumerate            {len(ids)} specimens, registry {reg['registry_id'][:16]}")

    chosen = pick_structurally_diverse(reg)
    print(f"  chose {len(chosen)} structurally distinct specimens "
          f"(by shape, never by behaviour)")

    for e in chosen:
        oid = e["organism_id"]
        rec = {"organism_id": oid, "shape": {k: e["resource_envelope"][k] for k in
                                             ("tape_words", "persist", "code_writable",
                                              "tick_budget", "genome_instructions")}}
        # ---- B. manifest by id     ---- C. validate     ---- D/E. instantiate + fresh state
        manifest = R.get_manifest(reg, oid)
        validate_manifest(manifest)
        p = Player(manifest)
        st0 = p.fresh_state()
        rec["B_manifest_by_id"] = True
        rec["C_validate"] = True
        rec["D_instantiate"] = True
        rec["E_fresh_state"] = (len(st0["tape"]) == manifest["tape_words"]
                                and len(st0["regs"]) == manifest["n_regs"]
                                and st0["ip"] == 0 and st0["ticks"] == 0)

        # ---- F. run ticks, and ---- I. replay the identical encounter
        o1, s1, stA, m1 = _encounter(manifest, oid)
        o2, s2, stB, m2 = _encounter(manifest, oid)
        rec["F_run_tick"] = True
        rec["I_replay_identical"] = (o1 == o2 and s1 == s2 and stA == stB
                                     and m1.ops == m2.ops)
        rec["statuses"] = s1

        # ---- G. checkpoint  ---- H. restore, then continue and compare against an unbroken run
        p3 = Player(manifest)
        st3 = p3.fresh_state()
        rng3 = _rng(oid)
        pre = []
        for _ in range(2):
            o, s = p3.run_tick(st3, FIXTURE_INPUTS, FIXTURE_N_OUT, rng3)
            pre.append(([list(c) for c in o], s))
        snap = checkpoint(oid, st3, "smoke-encounter", 2)
        rng_state_after = rng3.state
        st4 = restore(snap)
        rec["G_checkpoint"] = ("checkpoint_id" in snap and snap["organism_id"] == oid)
        rec["H_restore_state_equal"] = (st4 == st3)
        # continuing from the restored state, with the RNG at the same point, must match the
        # unbroken run's remaining ticks exactly
        rng4 = SplitMix64(0)
        rng4.state = rng_state_after
        post_restore = []
        for _ in range(TICKS - 2):
            o, s = p3.run_tick(st4, FIXTURE_INPUTS, FIXTURE_N_OUT, rng4)
            post_restore.append(([list(c) for c in o], s))
        unbroken = list(zip(o1[2:], s1[2:]))
        rec["H_continuation_matches_unbroken"] = (
            [(o, s) for o, s in post_restore] == [(o, s) for o, s in unbroken])

        # ---- J. provenance and identity
        full = R.get_entry(reg, oid)
        rec["J_provenance"] = (full["provenance"]["source"].endswith("generate")
                               and full["identity"]["runtime_hash"] == RUNTIME_HASH
                               and full["entry_id"] == R.compute_entry_id(full))

        # ---- K. resource limits, and that they actually bind
        env = R.get_resource_envelope(reg, oid)
        within_out_cap = all(len(c) <= env["out_cap"] for tick in o1 for c in tick)
        _o, _s, _st, m5 = _encounter(manifest, oid, ticks=1, budget=10 ** 9)
        rec["K_resource_envelope"] = True
        rec["K_out_cap_respected"] = within_out_cap
        rec["K_budget_cannot_be_raised"] = m5.ops <= env["tick_budget"]

        passed = all(v for k, v in rec.items()
                     if k.startswith(("B_", "C_", "D_", "E_", "F_", "G_", "H_", "I_", "J_", "K_")))
        rec["passed"] = passed
        ok = ok and passed
        results["specimens"].append(rec)
        print(f"  {oid[:12]} tape {rec['shape']['tape_words']:>5} "
              f"persist {rec['shape']['persist']:<5} "
              f"cw {str(rec['shape']['code_writable']):<5} "
              f"budget {rec['shape']['tick_budget']:>5} -> "
              f"{'PASS' if passed else 'FAIL'}  statuses {','.join(s1[:3])}")

    # ---------------------------------------------------------------- error paths, fail closed
    def expect_raise(name, fn):
        try:
            fn()
        except Exception as exc:                                   # noqa: BLE001 - that is the test
            results["error_paths"][name] = {"raised": True, "type": type(exc).__name__,
                                            "message": str(exc)[:160]}
            print(f"  {name:<34} RAISED {type(exc).__name__}")
            return True
        results["error_paths"][name] = {"raised": False}
        print(f"  {name:<34} DID NOT RAISE  <-- FAIL")
        return False

    print("error paths (all must fail closed)")
    good = R.get_manifest(reg, ids[0])
    e_ok = True
    e_ok &= expect_raise("malformed_manifest_missing_field",
                         lambda: validate_manifest({k: v for k, v in good.items()
                                                    if k != "n_regs"}))
    e_ok &= expect_raise("malformed_manifest_out_of_bounds",
                         lambda: validate_manifest(dict(good, n_regs=999)))
    e_ok &= expect_raise("malformed_manifest_genome_not_multiple_of_4",
                         lambda: validate_manifest(dict(good, genome=good["genome"][:-1])))
    e_ok &= expect_raise("player_rejects_bad_manifest",
                         lambda: Player(dict(good, tape_words=7)))
    e_ok &= expect_raise("unknown_organism_id",
                         lambda: R.get_manifest(reg, "0" * 64))
    e_ok &= expect_raise("stale_runtime_identity_on_restore",
                         lambda: restore({"runtime_hash": "0" * 64,
                                          "state": {"tape": [], "regs": [], "ip": 0,
                                                    "ticks": 0}}))
    e_ok &= expect_raise("invalid_checkpoint_missing_state",
                         lambda: restore({"runtime_hash": RUNTIME_HASH}))
    e_ok &= expect_raise("registry_entry_tampered_manifest",
                         lambda: R.validate_entry(dict(reg["entries"][0],
                                                       manifest=dict(good, tick_budget=32))))
    e_ok &= expect_raise("registry_unknown_field_rejected",
                         lambda: R.validate_entry(dict(reg["entries"][0], surprise=1)))
    e_ok &= expect_raise("registry_unknown_schema_version_rejected",
                         lambda: R.validate_registry(dict(reg, schema_version="proteus.v999")))
    e_ok &= expect_raise("registry_tampered_registry_id",
                         lambda: R.validate_registry(dict(reg, registry_id="0" * 64)))

    # extrinsic writes must NOT change identity -- the architectural guarantee of section 4
    tampered = json.loads(json.dumps(reg["entries"][0]))
    tampered["extrinsic"]["phenotype"] = "explorer"
    tampered["extrinsic"]["score"] = 0.97
    identity_held = (R.compute_entry_id(tampered) == reg["entries"][0]["entry_id"])
    R.validate_entry(tampered)                       # must still validate: extrinsic is OPEN
    results["extrinsic_cannot_change_identity"] = identity_held
    print(f"  {'extrinsic_write_keeps_identity':<34} "
          f"{'HELD' if identity_held else 'BROKEN  <-- FAIL'}")

    results["passed"] = bool(ok and e_ok and identity_held)
    with open(os.path.join(HERE, "RESULT_SMOKE.json"), "w", encoding="utf-8",
              newline="\n") as f:
        f.write(canonical_json(results))
        f.write("\n")
    print(f"\nSMOKE {'PASSED' if results['passed'] else 'FAILED'} "
          f"({len(results['specimens'])} specimens, "
          f"{len(results['error_paths'])} error paths)")
    return 0 if results["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
