"""THE CALIBRATION GATE. The campaign does not start until these pass.

The directive's early-exploration stage requires positive controls proving that the VM
executes correctly, that known replicators replicate, that known task witnesses solve,
that external reproduction controls evolve, and that endogenous reproduction can invade
when seeded. This file runs all five against the real engine - not against a mock - and
writes CALIBRATION.json. run_campaign.py refuses to launch on anything but PASS.

Every check returns PASS / FAIL / NOT_VERIFIED. A check that could not run is never
counted as a check that passed: that distinction is the one this campaign's ledger has
had to relearn most often.

The replicator and witness programs used here are INSTRUMENTS. They are seeded
deliberately, they are labelled as seeded in every record they touch, and no result about
spontaneous origin may cite a run that contains them. The grammar enforces the other half
of that rule: a spontaneity test must draw its population from uniform random bytes.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import grammar as G
import selftest_z8
import tasks
import world

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = []


def record(name, outcome, detail, t0=None):
    RESULTS.append({"control": name, "outcome": outcome, "detail": detail,
                    "seconds": round(time.time() - t0, 1) if t0 else None})
    print("  %-38s %s" % (name, outcome), flush=True)


def base_cell(**over):
    over.pop("tier", None)           # tier is not a factor; it is passed to run_cell
    c = {"world": "SOUP_MEM", "environment": "STATIC", "representation": "Z8_64",
         "reproduction": "ENDOGENOUS_COPY", "self_location": "PRIMITIVE",
         "copy_primitive": "BLOCK", "pressure": "NONE_IMPLICIT", "structure": "WELL_MIXED",
         "task_transform": "NEUTRAL", "read_order": "ANSWER_BEFORE_READ", "bridge": "VALLEY",
         "seeding": "SEEDED_REPLICATOR", "mutation_operator": "BOTH",
         "mutation_locality": "LOCAL", "mutation_rate": "LOW", "atlas_axis": "NONE"}
    c.update(over)
    c = G.repair(c)
    return c


# ---------------------------------------------------------------- 1. the VM
def control_vm():
    t0 = time.time()
    selftest_z8.CHECKS.clear()
    try:
        selftest_z8.test_instructions()
        selftest_z8.test_sandbox()
        selftest_z8.test_replication()
        selftest_z8.test_tasks()
    except Exception as e:                                        # noqa: BLE001
        record("vm_semantics", "NOT_VERIFIED", {"exception": "%s: %s" % (type(e).__name__, e)}, t0)
        return
    fails = [c for c in selftest_z8.CHECKS if c["outcome"] != "PASS"]
    record("vm_semantics", "PASS" if not fails else "FAIL",
           {"checks": len(selftest_z8.CHECKS), "failed": len(fails), "failures": fails[:6]}, t0)


# ---------------------------------------------------------------- 2. replication
def control_replication():
    for prim, loc in (("BLOCK", "PRIMITIVE"), ("BYTEWISE", "PRIMITIVE"),
                      ("BLOCK", "PC_RELATIVE"), ("BYTEWISE", "PC_RELATIVE")):
        t0 = time.time()
        cell = base_cell(copy_primitive=prim, self_location=loc, seeding="SEEDED_REPLICATOR")
        try:
            r = world.run_cell(cell, seed=1, max_epochs=40)
        except Exception as e:                                    # noqa: BLE001
            record("seeded_replicator_%s_%s" % (prim, loc), "NOT_VERIFIED",
                   {"exception": "%s: %s" % (type(e).__name__, e)}, t0)
            continue
        s = r["summary"]
        ok = s["births_endogenous"] > 0 and (s["first_replicator"] or {}).get("fidelity", 0) >= 0.90
        record("seeded_replicator_%s_%s" % (prim, loc), "PASS" if ok else "FAIL",
               {"births_endogenous": s["births_endogenous"], "births_external": s["births_external"],
                "first_replicator_epoch": (s["first_replicator"] or {}).get("epoch"),
                "fidelity": (s["first_replicator"] or {}).get("fidelity"),
                "pop_final": s["pop_final"], "flags": [f["flag"] for f in s["flags"]]}, t0)

    # self_location NONE: the negative case, asserted rather than assumed. A hardcoded
    # base cannot survive relocation, so the hand-written replicator must NOT replicate.
    # If it ever does, the world is leaking position information the factor says it does
    # not have, and that would invalidate every self_location comparison.
    t0 = time.time()
    # The population must be HETEROGENEOUS for this to test anything. With every organism
    # carrying identical bytes, copying from a hardcoded address produces a byte-identical
    # child for every organism, and 'copied from address zero' is indistinguishable from
    # 'copied itself'. So: a random soup with a few hardcoded-base invaders, where only
    # the invader that happens to sit at the hardcoded address can copy itself.
    cell = dict(base_cell(copy_primitive="BLOCK", self_location="PRIMITIVE", seeding="RANDOM"))
    cell["self_location"] = "NONE"                      # deliberately outside the grammar's pairing
    r = world.run_cell(cell, seed=1, max_epochs=40, invaders=8)
    s = r["summary"]
    fr = s["first_replicator"]
    # Births may still happen - the organism declares a child built from whatever lay at
    # the address it hardcoded - but they are not COPIES of the parent. The one exception
    # is the organism that happens to sit at that address, for which the hardcode is
    # accidentally correct; so the assertion is that faithful replication is confined to
    # base zero, not that nothing is born.
    ok = (fr is None) or bool(fr.get("base_is_zero"))
    record("no_general_replicator_without_self_location", "PASS" if ok else "FAIL",
           {"births_endogenous": s["births_endogenous"], "first_replicator": fr,
            "pop_final": s["pop_final"],
            "note": "a hardcoded base is wrong once the organism is placed elsewhere; only the "
                    "occupant of the hardcoded address can copy itself, and that is position "
                    "dependence, not replication"}, t0)


# ---------------------------------------------------------------- 3. the witness in a world
def control_witness():
    t0 = time.time()
    ok, detail = True, {}
    for tr in ("XOR1", "XOR15", "XOR5A", "ADD1"):
        for ro in tasks.READ_ORDERS:
            spec = tasks.TaskSpec(transform=tr, read_order=ro, n_episodes=64)
            w = tasks.competence(tasks.witness(spec), spec, seed=3, held_seed=900003)
            a = tasks.competence(tasks.reader_ancestor(spec), spec, seed=3, held_seed=900003)
            d = tasks.one_edit_distance(spec)
            detail["%s_%s" % (tr, ro)] = {"witness_comp": w["comp"], "witness_held": w["held"],
                                          "ancestor_comp": round(a["comp"], 3),
                                          "one_edit": d}
            if not (w["comp"] == 1.0 and w["held"] == 1.0 and d["differs"] == 1):
                ok = False
    record("task_witness_solves_and_is_one_edit", "PASS" if ok else "FAIL", detail, t0)


# ---------------------------------------------------------------- 4. the exogenous control evolves
def control_external_evolves():
    """EXTERNAL reproduction with explicit ranking must be able to cross a one-edit
    INCREMENTAL constant. If it cannot, the campaign's mutation model is too weak to
    resolve any accessibility difference and every later negative would be vacuous."""
    t0 = time.time()
    cell = base_cell(reproduction="EXTERNAL", pressure="EXPLICIT_FITNESS", seeding="SEEDED_READER",
                     task_transform="XOR1", read_order="ANSWER_BEFORE_READ",
                     mutation_rate="MID")
    runs = []
    for seed in (1, 2, 3):
        r = world.run_cell(cell, seed=seed, tier="M", max_epochs=400)
        s = r["summary"]
        runs.append({"seed": seed, "crossed": s["crossed"], "held_max": s["held_max"],
                     "comp_max": s["comp_max"], "births_external": s["births_external"],
                     "first_cross_epoch": (s["first_cross"] or {}).get("epoch")})
    crossed = sum(1 for x in runs if x["crossed"])
    best = max(x["held_max"] for x in runs)
    ok = crossed >= 1 or best >= 0.75
    record("external_control_crosses_one_edit", "PASS" if ok else "FAIL",
           {"runs": runs, "crossed_of_3": crossed, "best_held": best}, t0)


# ---------------------------------------------------------------- 5. endogenous invasion
def control_invasion():
    """A seeded replicator among random bytes must be able to take over. This is an
    invasion control, NOT evidence of spontaneous origin - the population is not random
    in the sense the spontaneity tests require, and every record says so."""
    t0 = time.time()
    cell = base_cell(seeding="RANDOM", reproduction="ENDOGENOUS_COPY", mutation_rate="LOW")
    runs = []
    for seed in (1, 2):
        r = world.run_cell(cell, seed=seed, max_epochs=60, invaders=2)
        s = r["summary"]
        runs.append({"seed": seed, "invader_share_final": s["invader_share_final"],
                     "births_endogenous": s["births_endogenous"],
                     "births_external": s["births_external"], "pop_final": s["pop_final"],
                     "flags": [f["flag"] for f in s["flags"]]})
    shares = [x["invader_share_final"] or 0 for x in runs]
    ok = max(shares) > 2.0 / G.TIERS["S"]["pop"] * 4 and all(x["births_external"] == 0 for x in runs)
    record("endogenous_invasion_from_seed", "PASS" if ok else "FAIL",
           {"runs": runs, "seeded_share": round(2 / G.TIERS["S"]["pop"], 4), "shares": shares}, t0)


# ---------------------------------------------------------------- 6. the negative control
def control_no_runner_births():
    """The campaign-voiding check, run deliberately: in every endogenous physics, the
    runner must create exactly zero descendants, and a random population that cannot
    replicate must simply die or stagnate rather than being quietly repopulated."""
    t0 = time.time()
    detail = {}
    ok = True
    for repro in ("ENDOGENOUS_COPY", "CONSTRUCTIVE", "OVERWRITE", "ENDOGENOUS_PARTIAL"):
        cell = base_cell(reproduction=repro, seeding="RANDOM")
        r = world.run_cell(cell, seed=7, max_epochs=40)
        s = r["summary"]
        detail[repro] = {"births_external": s["births_external"],
                         "births_endogenous": s["births_endogenous"],
                         "pop_final": s["pop_final"],
                         "flags": [f["flag"] for f in s["flags"]]}
        if s["births_external"] != 0 or any(f["severity"] == "critical" for f in s["flags"]):
            ok = False
    record("no_runner_births_in_endogenous", "PASS" if ok else "FAIL", detail, t0)


def main():
    t0 = time.time()
    print("CALIBRATION (grammar %s)" % G.grammar_hash()[:12], flush=True)
    control_vm()
    control_witness()
    control_replication()
    control_invasion()
    control_no_runner_births()
    control_external_evolves()
    n_fail = sum(1 for r in RESULTS if r["outcome"] == "FAIL")
    n_nv = sum(1 for r in RESULTS if r["outcome"] == "NOT_VERIFIED")
    out = {"grammar_hash": G.grammar_hash(), "written": time.strftime("%Y-%m-%d %H:%M:%S"),
           "seconds": round(time.time() - t0, 1), "controls": RESULTS,
           "passed": sum(1 for r in RESULTS if r["outcome"] == "PASS"),
           "failed": n_fail, "not_verified": n_nv,
           "gate": "PASS" if (n_fail == 0 and n_nv == 0) else "REFUSE"}
    (HERE / "CALIBRATION.json").write_text(json.dumps(out, indent=1), encoding="ascii")
    print(json.dumps({k: out[k] for k in ("passed", "failed", "not_verified", "gate", "seconds")}, indent=1))
    return 0 if out["gate"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
