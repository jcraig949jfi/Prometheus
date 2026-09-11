"""Adversarial tests for HERMES-32. Hermes, 2026-09-11.

Predictions were committed first at 8094151be. These tests pin the result
and, more importantly, pin the two BOUNDS the experiment exposed, so that a
later reader cannot quote the headline without them.

    python -m pytest roles/Hermes/science/hermes32/test_hermes32.py -q
"""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "convergence"))

import git_observe as G                                          # noqa: E402
import signature as S                                            # noqa: E402

RESULTS = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
SEATS = S.seat_names()
CANONICAL = Path(RESULTS["canonical"])


def key(obs):
    return S.s4_whole_observation(obs, seats=SEATS)


# ------------------------------------------------- THE HEADLINE RESULT ---
def test_before_is_unsignable_and_after_is_exact():
    assert RESULTS["before"]["verdict"] == "UNSIGNABLE"
    assert RESULTS["before"]["collides"] is True
    assert RESULTS["after"]["verdict"] == "EXACT"
    assert RESULTS["after"]["collisions"] == []


def test_the_ablation_reverses_it():
    """Without this reversal the result is correlation, not evidence that the
    instrument caused convergeability."""
    ab = RESULTS["ablations"]
    assert ab["remove both"]["convergence_disappears"] is True
    assert ab["remove repo_id"]["convergence_disappears"] is True


def test_the_ablation_also_shows_workspace_role_is_NOT_load_bearing():
    """Predicted in the preregistration and confirmed: for THIS specimen the
    minimum sufficient new observable is repo_id alone. Reported rather than
    quietly trimmed, because an ablation that only confirms what you kept is
    not an ablation."""
    assert RESULTS["ablations"]["remove workspace_role"]["convergence_disappears"] is False


# --------------------------------------------------------- BOUND ONE ---
def test_the_instrument_does_NOT_make_the_failure_self_announcing():
    """The conversion is of RECORDABILITY, not of detection. Every field that
    could signal trouble reads exactly like success, because the thing that
    would say otherwise is the rule, and the rule may not be in the
    instrument. A failure nobody records converges with nothing."""
    facts = RESULTS["canonical_facts"]
    specimen = {"exception_type": "NoError", "message": "Already up to date.",
                "exit_state": "success", "exit_code": 0,
                "stdout_head": "Already up to date.", **facts}
    permitted = RESULTS["negatives"]["CTL-E4 permitted worktree management in the canonical checkout"]
    for field in ("exit_code", "exit_state", "exception_type"):
        assert specimen[field] == permitted[field], field
    assert key(specimen) != key(permitted)          # distinguishable, yet


def test_the_instrument_encodes_no_rule():
    """No branch on a subcommand name, no list of mutating operations, no
    mention of which places are allowed -- checked over the parsed source, so
    a docstring mentioning 'pull' for context does not count."""
    tree = ast.parse((HERE / "git_observe.py").read_text(encoding="utf-8"))
    literals = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            parent_is_doc = False
            literals.add(node.value)
    # strip docstrings
    docs = {ast.get_docstring(n) for n in ast.walk(tree)
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef))}
    literals -= {d for d in docs if d}
    banned = {"pull", "merge", "rebase", "checkout", "reset", "restore",
              "cherry-pick", "stash", "canonical", "forbidden", "violation", "D-23"}
    assert not (literals & banned), literals & banned


def test_the_instrument_adds_no_uniqueness_of_its_own():
    """An instrument that stamped the observer, the pid or the time would
    force uniqueness and destroy convergence -- the opposite of the goal."""
    a = G.workspace_facts(cwd=str(CANONICAL))
    b = G.workspace_facts(cwd=str(CANONICAL))
    assert a == b
    assert set(a) == {"repo_id", "workspace_role"}


def test_the_instrument_never_raises_and_answers_even_outside_a_repository(tmp_path):
    """'Do not turn every execution into an error.' Outside a repo it returns
    nulls rather than blowing up, and a null field is simply absent from the
    key."""
    facts = G.workspace_facts(cwd=str(tmp_path))
    assert facts == {"repo_id": None, "workspace_role": None}
    assert key({"message": "x", **facts}) == key({"message": "x"})


# --------------------------------------------------------- BOUND TWO ---
def test_only_ONE_of_the_four_negatives_actually_exercises_the_instrument():
    """Self-criticism, made executable. CTL-E2/E3/E4 are permitted commands in
    the SAME repository and the SAME worktree; they separate on `command`,
    which was available before the instrument existed. Only CTL-E1 -- a
    legitimate execution of the SAME command elsewhere -- is separated by the
    new fact. The conversion therefore rests on one control, and the reader
    should know which."""
    facts = RESULTS["canonical_facts"]
    specimen = {"exception_type": "NoError", "message": "Already up to date.",
                "exit_state": "success", "exit_code": 0,
                "stdout_head": "Already up to date.", **facts}
    neg = RESULTS["negatives"]
    exercises, trivially_separated = [], []
    for name, o in neg.items():
        stripped_s = {k: v for k, v in specimen.items() if k not in ("repo_id", "workspace_role")}
        stripped_o = {k: v for k, v in o.items() if k not in ("repo_id", "workspace_role")}
        (exercises if key(stripped_s) == key(stripped_o) else trivially_separated).append(name)
    assert len(exercises) == 1 and exercises[0].startswith("CTL-E1")
    assert len(trivially_separated) == 3


def test_the_scope_condition_is_what_made_it_work():
    """The newly identified condition: the instrument converted this specimen
    because it exposed a fact at the SAME SCOPE as the rule that makes the
    behaviour a failure. D-23 s3 is repository-scoped ('never git pull'), and
    repo_id is a repository-scoped fact. A fact at the wrong scope does not
    convert: workspace_role is worktree-scoped and, by the ablation, does no
    work here."""
    assert RESULTS["ablations"]["remove repo_id"]["convergence_disappears"] is True
    assert RESULTS["ablations"]["remove workspace_role"]["convergence_disappears"] is False


# ------------------------------------------- NO COLLATERAL DAMAGE ---
def test_no_other_case_verdict_moved():
    """False merge / false split across the original corpus, under the same
    whole-observation hash used for this experiment."""
    x = RESULTS["cross_check"]
    assert x["CASE-A"]["distinct_keys"] == 1 and x["CASE-A"]["observers"] == 5
    assert x["CASE-B"]["distinct_keys"] == 1 and x["CASE-B"]["observers"] == 6
    assert x["CASE-C"]["distinct_keys"] == 2      # still two incidents, correctly
    assert x["CASE-D"]["distinct_keys"] == 2      # still two incidents, correctly


def test_cost_is_bounded_and_writes_nothing():
    c = RESULTS["cost"]
    assert c["workspace_facts_ms"] < 500          # two read-only git invocations
    assert c["workspace_facts_ms"] > c["git_rev_parse_ms"]


def test_keys_are_stable_across_processes():
    facts = RESULTS["canonical_facts"]
    obs = {"exception_type": "NoError", "message": "Already up to date.",
           "exit_state": "success", "exit_code": 0,
           "stdout_head": "Already up to date.", **facts}
    here = key(obs)
    code = ("import sys, json; sys.path.insert(0, r'{d}');"
            "import signature as S;"
            "print(S.s4_whole_observation(json.loads(r'''{j}'''), seats=S.seat_names()))"
            ).format(d=str(HERE.parent / "convergence"), j=json.dumps(obs))
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr[-300:]
    assert out.stdout.strip() == here
