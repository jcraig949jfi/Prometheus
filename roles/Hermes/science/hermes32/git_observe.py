"""Workspace attestation for a git invocation: facts, never a judgement.

Hermes, 2026-09-11, HERMES-32. Prototype under Hermes science; the
production home, if any, is Archaeon's (archaeon/workspace.py already has
is_main_worktree) and the change is routed rather than made.

WHAT THIS EMITS, and why each field is a fact rather than a diagnosis:

  command         the git subcommand as invoked. What was run.
  repo_id         `git rev-list --max-parents=0 HEAD`, the root-commit SHA.
                  Identical in every clone of a repository, different for a
                  different repository, independent of path, host, drive
                  letter and remote URL. The git analogue of a Postgres
                  system_identifier, and chosen for the same reason: the
                  name of a thing is not its identity.
  workspace_role  "main_worktree" when `git rev-parse --git-dir` resolves
                  to the same directory as `--git-common-dir`, else
                  "linked_worktree". A property of the process's cwd.
  exit_code       what git returned.
  stdout_head     the first line of stdout, which is what an observer
                  would have quoted anyway.

WHAT IT DOES NOT DO, each a constraint from the assignment:

  * it does not know any rule. There is no branch on a subcommand name,
    no list of mutating operations, no mention of which places are
    allowed. A test asserts the module's executable lines contain no git
    subcommand literal.
  * it does not raise. Every execution returns an observation; none
    becomes an error. Turning ordinary calls into failures was explicitly
    excluded.
  * it does not read the incident corpus, a seat name, a model, an
    embedding or a fuzzy matcher.
  * it adds no uniqueness of its own: two different processes running the
    same command in the same place produce the SAME observation. That is
    the point; an instrument that stamped the observer would force
    uniqueness and destroy convergence.

The judgement -- whether a (command, place) pair is permitted -- lives in
a rule, and the rule is deliberately not here. That separation is what
the experiment is testing: can facts alone make the distinction
observable?
"""
from __future__ import annotations

import os
import subprocess
from typing import Any, Dict, List, Optional

#: Generous by contract: WORKING_CONTRACT s3 forbids short timeouts on git
#: operations over a large tree. Measured here -- `git status --short` on the
#: 39k-file canonical checkout exceeded 120 s on a cold index.
TIMEOUT = 600


def _git(args: List[str], cwd: Optional[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True,
                          timeout=TIMEOUT)


def workspace_facts(cwd: Optional[str] = None) -> Dict[str, Any]:
    """Measure the two identity facts. No side effects, no judgement."""
    out: Dict[str, Any] = {"repo_id": None, "workspace_role": None}
    # One invocation for both paths: git prints them on successive lines.
    r = _git(["rev-parse", "--git-dir", "--git-common-dir"], cwd)
    lines = r.stdout.strip().splitlines()
    if r.returncode == 0 and len(lines) >= 2:
        base = cwd or os.getcwd()
        a = os.path.abspath(os.path.join(base, lines[0].strip()))
        b = os.path.abspath(os.path.join(base, lines[1].strip()))
        out["workspace_role"] = "main_worktree" if a == b else "linked_worktree"
    root = _git(["rev-list", "--max-parents=0", "HEAD"], cwd)
    if root.returncode == 0 and root.stdout.strip():
        out["repo_id"] = root.stdout.strip().splitlines()[-1]
    return out


def observe(argv: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
    """Run `git <argv>` and return the observation: what was run, where it
    ran, and what came back. The caller decides what, if anything, that
    means."""
    p = _git(list(argv), cwd)
    obs: Dict[str, Any] = {
        "command": argv[0] if argv else "",
        "exit_code": p.returncode,
        "stdout_head": (p.stdout.strip().splitlines() or [""])[0],
        "exit_state": "success" if p.returncode == 0 else "raised",
        "message": (p.stdout.strip().splitlines() or [""])[0] or
                   (p.stderr.strip().splitlines() or [""])[0],
        "exception_type": "NoError" if p.returncode == 0 else "GitError",
    }
    obs.update(workspace_facts(cwd))
    return obs


def attest(argv: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
    """Facts about an invocation WITHOUT running it -- for reconstructing a
    historical observation, where the command already ran long ago."""
    obs = {"command": argv[0] if argv else ""}
    obs.update(workspace_facts(cwd))
    return obs
