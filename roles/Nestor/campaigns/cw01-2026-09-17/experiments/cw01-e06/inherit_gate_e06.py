"""ENGINEERING TARGET for cw01-e06: prove the inherited stack before QUALIFY.

e06 is the first experiment built relocatable from inception and the first to inherit
the full e05 infrastructure. Before any science budget is spent, each inherited gate
must be demonstrated BY OBSERVED REFUSAL - not merely imported, not merely present:

  G1  repopath      repository discovery from >= 2 different directory depths
  G2  recordsafety  refuses a deliberately unsafe (non-ascii) record
  G3  recordsafety  tally agreement refuses deliberately drifted state
  G4  guardproof    refuses a vacuous proof whose bad case equals its good case
  G5  writerlock    refuses a git write while a live RowWriter exists

"Guard exists" is not evidence. "Guard observed refusing" is evidence. Every gate here
also carries a POSITIVE CONTROL, because a guard that refuses unconditionally is as
useless as one that never fires.

If any inherited gate fails, the shared mechanism is repaired before e06 science
proceeds - the whole point of promoting them was that they transfer.

CW01-D046: roots discovered by marker, never by counting parents.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent


def _bootstrap_lib():
    for cand in [HERE] + list(HERE.parents):
        if (cand / "lib" / "repopath.py").exists():
            sys.path.insert(0, str(cand / "lib"))
            return cand / "lib"
    raise RuntimeError("cannot locate lib/repopath.py walking up from %s" % HERE)


LIB = _bootstrap_lib()
import repopath as RP          # noqa: E402
import recordsafety as RS      # noqa: E402
import guardproof as GP        # noqa: E402
import writerlock as WL        # noqa: E402
import learnability as LN      # noqa: E402

CAMPAIGN = RP.find_campaign_root(HERE)
REPO = RP.find_root(HERE)
CHECKS = []


def record(gid, name, passed, detail):
    CHECKS.append({"id": gid, "gate": name, "passed": bool(passed), "detail": detail})
    print("   %-4s %-14s %-6s %s" % (gid, name, "PASS" if passed else "FAIL", detail[:74]))
    return passed


def g1_repopath():
    """Discovery must agree from at least two DIFFERENT directory depths."""
    shallow = LIB                                   # .../campaigns/<id>/lib
    deep = HERE                                     # .../campaigns/<id>/experiments/cw01-e06
    d_shallow = len(shallow.parts)
    d_deep = len(deep.parts)
    same_repo = RP.find_root(shallow) == RP.find_root(deep) == REPO
    same_camp = RP.find_campaign_root(shallow) == RP.find_campaign_root(deep) == CAMPAIGN
    differing = d_shallow != d_deep
    refused = False
    try:
        RP.find_root(pathlib.Path(tempfile.mkdtemp()), marker=".no_such_marker")
    except RP.RepoRootNotFound:
        refused = True
    return record("G1", "repopath", same_repo and same_camp and differing and refused,
                  "same root from depths %d and %d; unmarked tree refused"
                  % (d_shallow, d_deep))


def g2_recordsafety_ascii():
    tmp = pathlib.Path(tempfile.mkdtemp())
    bad = tmp / "bad.json"
    bad.write_text(json.dumps({"n": "x每 y"}, ensure_ascii=False), encoding="utf-8")
    good = tmp / "good.json"
    good.write_text(json.dumps({"n": "x每 y"}, ensure_ascii=True), encoding="utf-8")
    refused = RS.scan(bad)["outcome"] == "FAIL"
    raised = False
    try:
        RS.require_ascii_safe(bad)
    except RS.UnsafeRecord:
        raised = True
    admits = RS.scan(good)["outcome"] == "PASS"
    live = RS.check_records([CAMPAIGN / "CAMPAIGN_STATE.json", CAMPAIGN / "DEFECTS.jsonl"])
    return record("G2", "recordsafety", refused and raised and admits and live["safe"],
                  "refused non-ascii, admitted escaped, live records %s" % live["verdict"])


def g3_tally_agreement():
    tmp = pathlib.Path(tempfile.mkdtemp())
    led = tmp / "L.jsonl"
    led.write_text("".join(json.dumps({"id": "X%d" % i, "experiment_id": "cw01-e01"}) + "\n"
                           for i in range(3)), encoding="utf-8")

    def st(total, per):
        p = tmp / ("S%d.json" % total)
        p.write_text(json.dumps({"campaign_totals": {"defects_logged": total,
                                                     "defects_per_experiment": per}}),
                     encoding="utf-8")
        return p

    refused = RS.check_tally(st(2, {"e01": 2}), led)["outcome"] == "FAIL"
    raised = False
    try:
        RS.require_tally_consistent(st(2, {"e01": 2}), led)
    except RS.TallyDrift:
        raised = True
    admits = RS.check_tally(st(3, {"e01": 3}), led)["outcome"] == "PASS"
    live = RS.check_tally(CAMPAIGN / "CAMPAIGN_STATE.json", CAMPAIGN / "DEFECTS.jsonl")
    return record("G3", "tally", refused and raised and admits and live["outcome"] == "PASS",
                  "refused drift, admitted agreement, live tally %s" % live["outcome"])


def g4_guardproof_vacuous():
    same = {"force": True}
    vac = GP.prove_refuses(LN.require_controlled,
                           bad_args=(dict(same), dict(same), "g4"),
                           good_args=(dict(same), dict(same), "g4"),
                           expect=LN.UncontrolledComparison, label="G4/vacuous")
    caught = (not vac["proven"]) and (not vac["distinguishable"])
    raised = False
    try:
        GP.require_proven(vac)
    except GP.VacuousFixture:
        raised = True
    real = GP.prove_refuses(LN.require_controlled,
                            bad_args=({"force": True}, {}, "g4"),
                            good_args=({"force": True}, {"force": True}, "g4"),
                            expect=LN.UncontrolledComparison, label="G4/real")
    denied = False
    try:
        GP.GuardLedger().require("nonexistent.guard")
    except GP.GuardNotProven:
        denied = True
    return record("G4", "guardproof", caught and raised and real["proven"] and denied,
                  "vacuous fixture refused; a real refusal still proves; ledger demands proof")


def g5_writerlock():
    os.environ.setdefault("PM_TAG", "m1-cw01e06g")
    quiet = WL.check(REPO)["outcome"] == "PASS"
    rows = WL._rows_module(REPO)
    probe = HERE / "rows" / ".inherit_gate_probe.jsonl"
    w = rows.RowWriter(str(probe), "CW01-E06-INHERIT")     # zero rows -> close cannot commit
    try:
        refused = WL.check(REPO)["outcome"] == "FAIL"
        raised = False
        try:
            WL.require_quiet(REPO)
        except WL.LiveRowWriter:
            raised = True
    finally:
        w.close()
        probe.unlink(missing_ok=True)
    after = WL.check(REPO)["outcome"] == "PASS"
    nv = WL.check(pathlib.Path(tempfile.mkdtemp()))["outcome"] == "NOT_VERIFIED"
    return record("G5", "writerlock", quiet and refused and raised and after and nv,
                  "refused while live, admitted when reaped, non-worktree is NOT_VERIFIED")


def main():
    print("########## cw01-e06 ENGINEERING TARGET - inherited stack ##########")
    print("   campaign %s | repo %s\n" % (CAMPAIGN.name, REPO.name))
    g1_repopath()
    g2_recordsafety_ascii()
    g3_tally_agreement()
    g4_guardproof_vacuous()
    g5_writerlock()
    n = sum(1 for c in CHECKS if c["passed"])
    print("\n   %d/%d inherited gates proven by observed refusal" % (n, len(CHECKS)))
    ok = n == len(CHECKS)
    print("   %s" % ("e06 science may proceed to QUALIFY" if ok else
                     "REPAIR THE SHARED MECHANISM before e06 science proceeds"))
    (HERE / "INHERIT_GATE.json").write_text(json.dumps(
        {"campaign_id": "cw01-2026-09-17", "experiment_id": "cw01-e06",
         "campaign_root": str(CAMPAIGN), "repo_root": str(REPO),
         "checks": CHECKS, "n_passed": n, "n_total": len(CHECKS), "all_proven": ok,
         "_rule": "an inherited gate is not evidence until observed refusing in THIS experiment"},
        indent=1), encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
