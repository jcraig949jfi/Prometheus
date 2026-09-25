"""Prove guardproof against REAL production guards, including its own thesis.

A module whose claim is "a guard is not evidence until it has been observed refusing"
would refute itself by shipping unproven. So this exercises the actual guards in
lib/learnability.py and lib/contract.py -- not copies, not stand-ins -- against e05's
real committed verdict contract.

G5 is the one that matters most: prove_refuses must REFUSE a vacuous fixture whose bad
case equals its good case. That is the CW01-D038a antipattern wearing a test's
clothing, and a harness that cannot detect it would reproduce the defect it exists to
catch.
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parent
for p in (str(HERE),):
    if p not in sys.path:
        sys.path.insert(0, p)

import contract as CT          # noqa: E402
import guardproof as GP        # noqa: E402
import learnability as LN      # noqa: E402

CONTRACT_PATH = BASE / "experiments" / "cw01-e05" / "VERDICT_CONTRACT.json"
RESULTS = []


def show(name, v):
    RESULTS.append({"guard": name, **{k: v[k] for k in
                                      ("proven", "distinguishable", "refused_bad",
                                       "admitted_good", "verdict")}})
    print("    %-34s %-7s %s" % (name, "PROVEN" if v["proven"] else "UNPROVEN", v["verdict"][:78]))
    return v["proven"]


def main():
    print("########## guardproof self-test: real production guards ##########")
    led = GP.GuardLedger()

    # G1 -- the guard whose misuse motivated this module (CW01-D038a)
    v = led.prove("learnability.require_controlled", LN.require_controlled,
                  bad_args=({"force_disjunctive": True}, {}, "G1/bad"),
                  good_args=({"force_disjunctive": True}, {"force_disjunctive": True}, "G1/good"),
                  expect=LN.UncontrolledComparison)
    show("learnability.require_controlled", v)

    # G2 -- vacuous comparison (CW01-D034)
    v = led.prove("learnability.require_live", LN.require_live,
                  bad_args=({"info": 0.0, "components_carried": 0}, ("info", "components_carried"), "G2/bad"),
                  good_args=({"info": 228.7, "components_carried": 3}, ("info", "components_carried"), "G2/good"),
                  expect=LN.VacuousCheck)
    show("learnability.require_live", v)

    # G3 -- unlearnable world
    v = led.prove("learnability.require", LN.require,
                  bad_args=({"learnable": False, "verdict": "NOT LEARNABLE - do not spend budget"},),
                  good_args=({"learnable": True, "verdict": "LEARNABLE"},),
                  expect=LN.NotLearnable)
    show("learnability.require", v)

    # G4 -- contract drift, against e05's REAL committed contract
    committed = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))["contract"]
    c = CT.VerdictContract(committed)
    good_path = pathlib.Path(tempfile.mkdtemp()) / "good.json"
    bad_path = pathlib.Path(tempfile.mkdtemp()) / "bad.json"
    c.save(good_path)
    mutated = json.loads(json.dumps(committed))
    mutated["budget_B"] = 4
    CT.VerdictContract(mutated).save(bad_path)
    v = led.prove("contract.require_matches", c.require_matches,
                  bad_args=(bad_path,), good_args=(good_path,),
                  expect=CT.ContractViolation)
    show("contract.require_matches", v)

    # G5 -- THE META CHECK. A fixture whose bad case equals its good case must be
    # refused. This is exactly what require_controlled(dict(kw), dict(kw)) was.
    same = {"force_disjunctive": True}
    vac = GP.prove_refuses(LN.require_controlled,
                           bad_args=(dict(same), dict(same), "G5"),
                           good_args=(dict(same), dict(same), "G5"),
                           expect=LN.UncontrolledComparison, label="G5/vacuous")
    caught = (not vac["proven"]) and (not vac["distinguishable"])
    RESULTS.append({"guard": "prove_refuses REFUSES a vacuous fixture", "proven": caught,
                    "distinguishable": vac["distinguishable"], "refused_bad": vac["refused_bad"],
                    "admitted_good": vac["admitted_good"], "verdict": vac["verdict"]})
    print("    %-34s %-7s %s" % ("meta: vacuous fixture refused",
                                 "PROVEN" if caught else "UNPROVEN", vac["verdict"][:78]))

    raised = False
    try:
        GP.require_proven(vac)
    except GP.VacuousFixture:
        raised = True
    print("    %-34s %-7s require_proven raised VacuousFixture=%s"
          % ("meta: fails closed", "PROVEN" if raised else "UNPROVEN", raised))
    RESULTS.append({"guard": "require_proven fails closed on vacuous", "proven": raised,
                    "verdict": "VacuousFixture raised" if raised else "did not raise"})

    # G6 -- the ledger must refuse to let a driver rely on an unproven guard
    empty = GP.GuardLedger()
    denied = False
    try:
        empty.require("some.guard.with.no.fixture")
    except GP.GuardNotProven:
        denied = True
    print("    %-34s %-7s GuardLedger.require raised GuardNotProven=%s"
          % ("meta: ledger demands proof", "PROVEN" if denied else "UNPROVEN", denied))
    RESULTS.append({"guard": "GuardLedger.require refuses unproven", "proven": denied,
                    "verdict": "GuardNotProven raised" if denied else "did not raise"})

    # the four real guards must all be proven before the ledger will clear
    led.require("learnability.require_controlled", "learnability.require_live",
                "learnability.require", "contract.require_matches")

    n_ok = sum(1 for r in RESULTS if r["proven"])
    print("\n    %d/%d proven" % (n_ok, len(RESULTS)))
    out = {"ledger": led.as_dict(), "checks": RESULTS,
           "all_proven": n_ok == len(RESULTS),
           "_rule": "'guard exists' is not evidence; 'guard observed refusing' is evidence"}
    (BASE / "GUARDPROOF_SELFTEST.json").write_text(json.dumps(out, indent=1, default=str),
                                                   encoding="utf-8")
    return 0 if out["all_proven"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
