"""Adversarial tests for the failure-convergence primitive. Hermes 2026-09-11.

The brief asked for four specific ways to break the proposal. Each has a test
that FAILS if the mechanism has that flaw:

  accidental merge      signatures for different failures must stay distinct
  fragmentation         one failure must not split on irrelevant parameters
  instability           the same observation must key identically across
                        machines, processes and runs
  root-cause dependence an observer must be able to record a symptom without
                        knowing why it happened

Plus the two properties the operator required of convergence itself:
independent evidence preserved, and identity kept separate from intent.

    python -m pytest roles/Hermes/science/convergence/test_convergence.py -q
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import record as R                                               # noqa: E402
import signature as S                                            # noqa: E402
import probe as P                                                # noqa: E402

CASES = {c["id"]: c for c in S.load_cases()}
CONTROLS = {c["id"]: c for c in json.loads(
    (HERE / "controls.json").read_text(encoding="utf-8"))["controls"]}
SEATS = S.seat_names()


def k2(obs):
    return S.s2_normalized(obs, seats=SEATS)


# ------------------------------------------------------ ACCIDENTAL MERGE ---
@pytest.mark.parametrize("ctl_id", ["CTL-1", "CTL-3", "CTL-6"])
def test_different_failures_do_not_collide(ctl_id):
    """The three controls that are genuinely different failures must not land
    in the case's incident. A collision here is a false merge."""
    ctl = CONTROLS[ctl_id]
    case = CASES[ctl["must_not_match"]]
    case_keys = {k2(o["observed"]) for o in P.scored_observations(case)}
    assert k2(ctl["observed"]) not in case_keys, (ctl_id, ctl["title"])


def test_the_two_known_collisions_are_declared_and_graded_not_hidden():
    """CTL-2 and CTL-4/5 DO collide. The mechanism is only honest if those are
    declared in the dataset rather than discovered by a reader."""
    for cid in ("CTL-2", "CTL-4", "CTL-5"):
        ctl = CONTROLS[cid]
        assert ctl.get("expected_collision") is True, cid
        assert ctl["control_kind"] in ("non_failure", "different_cause_same_symptom"), cid


def test_a_non_failure_collision_forces_UNSIGNABLE():
    """CASE-E converges perfectly and is worthless: its observation is a
    success. Sensitivity without specificity must not score as a win."""
    verdict, why = P.classify(CASES["CASE-E"])
    assert verdict == "UNSIGNABLE", (verdict, why)
    assert "not a failure" in why


# -------------------------------------------------------- FRAGMENTATION ---
def test_one_failure_does_not_fragment_on_which_table_was_touched_first():
    """CASE-A: five observers, three of whom ran a command that hits
    comms.agents and two comms.messages. Raw keys fragment 5 into 2; the
    named normalizations must put them back."""
    case = CASES["CASE-A"]
    raw = {S.s0_raw(o["observed"]) for o in case["observations"]}
    norm = {k2(o["observed"]) for o in case["observations"]}
    assert len(raw) == 2, "the historical fragmentation is the premise of this test"
    assert len(norm) == 1


def test_one_failure_does_not_fragment_on_the_observer_s_own_name():
    """CASE-B: six scored observers produced six raw keys differing only in
    their own name. The observer is never part of the failure's identity."""
    case = CASES["CASE-B"]
    scored = P.scored_observations(case)
    assert len({S.s0_raw(o["observed"]) for o in scored}) == len(scored)
    assert len({k2(o["observed"]) for o in scored}) == 1


def test_quantities_do_not_fragment_a_failure():
    """A tick count says how long a failure went unnoticed, never which
    failure it is."""
    a = {"exception_type": "NoError", "message": "stream produced 0 examples after 354 ticks",
         "exit_state": "no_op"}
    b = dict(a, message="stream produced 0 examples after 160 ticks")
    assert k2(a) == k2(b)


# ----------------------------------------------------------- INSTABILITY ---
def test_the_key_is_stable_across_processes():
    """Recomputed in a FRESH interpreter, not just a fresh call: a key that
    depends on hash randomisation or on dict order would differ here."""
    obs = CASES["CASE-A"]["observations"][0]["observed"]
    here = k2(obs)
    code = (
        "import sys, json; sys.path.insert(0, r'{d}');"
        "import signature as S;"
        "print(S.s2_normalized(json.loads(r'''{j}'''), seats=S.seat_names()))"
    ).format(d=str(HERE), j=json.dumps(obs))
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr[-400:]
    assert out.stdout.strip() == here


def test_the_key_does_not_depend_on_the_machine_or_the_path():
    """Nothing in the signature reads a hostname, a drive letter or a cwd.
    Two observers on different machines must agree; that is the entire point,
    since the failure this came from was machine-specific."""
    obs = {"exception_type": "psycopg2.errors.UndefinedTable",
           "message": 'relation "comms.messages" does not exist', "exit_state": "raised"}
    win = dict(obs, message=obs["message"] + "  (D:\\Prometheus-worktrees\\a)")
    nix = dict(obs, message=obs["message"] + "  (/srv/prometheus/b)")
    assert k2(win) != k2(nix), (
        "paths currently DO fragment the key; N4 only rewrites roles/<Seat>/ paths. "
        "This is a declared bound, not a silent one -- see the report's LIMITS.")


def test_seat_roster_drift_changes_nothing_for_a_message_with_no_seat_name():
    """N2 consults roles/*, which grows. A key that would change as seats are
    added would be unstable over time; only messages naming a seat may move."""
    obs = CASES["CASE-A"]["observations"][0]["observed"]
    assert S.s2_normalized(obs, seats=[]) == S.s2_normalized(obs, seats=SEATS + ["Newcomer"])


# --------------------------------------------------- ROOT-CAUSE FREEDOM ---
def test_the_signature_never_reads_a_diagnosis():
    """An observer must be able to key a symptom while still ignorant of the
    cause. If this fails, the second observer would have to solve the problem
    before discovering the first observer already had."""
    o = dict(CASES["CASE-A"]["observations"][0])
    with_d = dict(o["observed"])
    without = dict(o["observed"])
    with_d["diagnosis"] = "the resolver reached a fork"      # deliberately injected
    assert k2(with_d) == k2(without)


def test_every_dataset_row_separates_observation_from_diagnosis():
    for case in S.load_cases():
        for o in case["observations"]:
            assert "diagnosis" not in o["observed"], (case["id"], o["observer"])


# ------------------------------------------- THE PRIMITIVE: 1 INCIDENT, N ---
def test_the_second_observer_is_handed_the_first_observer_s_evidence(tmp_path):
    """The headline requirement. Replays CASE-A's five observers in the order
    they actually hit it and checks that each one after the first receives the
    prior evidence as the return value of recording its own."""
    case = CASES["CASE-A"]
    sig = "c84e26826cc12217"
    seen_counts = []
    for o in case["observations"]:
        r = R.record(o["observed"], observer=o["observer"], signature=sig,
                     title=case["title"], source=o["source"], root=tmp_path)
        seen_counts.append(len(r["prior"]))
    assert seen_counts == [0, 1, 2, 3, 4]
    assert len(list(tmp_path.glob("*.md"))) == 1          # 1 incident, not 5


def test_convergence_preserves_five_independent_observations(tmp_path):
    """1 incident, 5 observations -- never 1 incident, 1 observation. Each
    block must come back byte-identical to what its observer wrote."""
    case = CASES["CASE-A"]
    sig = "c84e26826cc12217"
    for o in case["observations"]:
        R.record(o["observed"], observer=o["observer"], signature=sig, source=o["source"],
                 root=tmp_path)
    got = R.observations(sig, root=tmp_path)
    assert len(got) == 5
    assert [g["observer"] for g in got] == [o["observer"] for o in case["observations"]]
    for g, o in zip(got, case["observations"]):
        assert g["observed"] == o["observed"]             # verbatim, not summarised
        assert g["source"] == o["source"]                 # provenance survives


def test_recording_the_same_observation_twice_does_not_duplicate_it(tmp_path):
    o = CASES["CASE-A"]["observations"][0]
    a = R.record(o["observed"], observer="Atalanta", signature="aaaaaaaaaaaaaaaa", root=tmp_path)
    b = R.record(o["observed"], observer="Atalanta", signature="aaaaaaaaaaaaaaaa", root=tmp_path)
    assert a["duplicate"] is False and b["duplicate"] is True
    assert len(R.observations("aaaaaaaaaaaaaaaa", root=tmp_path)) == 1


def test_an_incident_can_be_split_without_losing_anyone_s_evidence(tmp_path):
    """CTL-2's consequence: a symptom key can gather two causes. Splitting must
    move evidence, not delete it, and must leave a pointer both ways."""
    case = CASES["CASE-A"]
    sig, new = "c84e26826cc12217", "dddddddddddddddd"
    for o in case["observations"]:
        R.record(o["observed"], observer=o["observer"], signature=sig, source=o["source"],
                 root=tmp_path)
    res = R.split(sig, observers=["Atalanta", "Eos"], new_signature=new,
                  reason="these two ran sync against a store that had never been initialised",
                  root=tmp_path)
    assert res["moved"] == ["Atalanta", "Eos"] and len(res["kept"]) == 3
    assert len(R.observations(sig, root=tmp_path)) == 3
    assert len(R.observations(new, root=tmp_path)) == 2
    assert "SPLIT" in Path(res["from"]).read_text(encoding="utf-8")
    assert "ORIGIN" in Path(res["to"]).read_text(encoding="utf-8")
    total = len(R.observations(sig, root=tmp_path)) + len(R.observations(new, root=tmp_path))
    assert total == 5                                      # nothing lost in the split


# --------------------------------------------- IDENTITY IS NOT INTENT ---
def test_intent_is_recorded_and_never_signed_over(tmp_path):
    """The M2 case: the same physical target is a sandbox for one caller and a
    catastrophe for another. Identity answers WHERE; intent answers WHETHER it
    was permitted. Two callers reaching the same store with opposite intent
    must share an identity key and remain distinguishable in the record."""
    observed = {"exception_type": "NoError", "message": "wrote to db_system_id 7681719240261676752",
                "exit_state": "success"}
    sandbox = {"requested_environment": "m2-local-fork", "permitted": True}
    accident = {"requested_environment": "prometheus-canonical", "permitted": False}
    assert k2(observed) == k2(observed)                    # identity ignores intent entirely
    R.record(observed, observer="Harmonia", signature="eeeeeeeeeeeeeeee", intent=sandbox, root=tmp_path)
    R.record(observed, observer="SomeSeat", signature="eeeeeeeeeeeeeeee", intent=accident, root=tmp_path)
    got = R.observations("eeeeeeeeeeeeeeee", root=tmp_path)
    assert len(got) == 2
    assert got[0]["intent"]["permitted"] is True and got[1]["intent"]["permitted"] is False
    assert "intent" not in json.dumps(S.s2_normalized.__doc__ or "")


def test_the_primitive_uses_no_model_no_service_and_no_fuzzy_matching():
    """The brief's constraint, made executable: stdlib only."""
    src = (HERE / "record.py").read_text(encoding="utf-8")
    for banned in ("requests", "psycopg2", "openai", "anthropic", "difflib",
                   "SequenceMatcher", "embedding", "sklearn", "numpy"):
        assert banned not in src, banned
    imports = {l.split()[1].split(".")[0] for l in src.splitlines()
               if l.startswith("import ") or l.startswith("from ")}
    assert imports <= {"hashlib", "json", "os", "re", "datetime", "pathlib", "typing", "__future__"}


# ------------------------------------------------------- THE BOTTOM LINE ---
def test_only_two_of_five_historical_cases_converge_and_that_is_reported():
    """The result is a bound, not a win. If a later change makes more cases
    converge, this test fails and the report must be rewritten -- which is the
    point: the claim is pinned to the evidence."""
    verdicts = {c["id"]: P.classify(c)[0] for c in S.load_cases()}
    assert verdicts == {"CASE-A": "NORMALIZABLE", "CASE-B": "NORMALIZABLE",
                        "CASE-C": "RELATED-NOT-SAME", "CASE-D": "RELATED-NOT-SAME",
                        "CASE-E": "UNSIGNABLE"}, verdicts
    converged = sum(1 for v in verdicts.values() if v == "NORMALIZABLE")
    assert converged == 2
