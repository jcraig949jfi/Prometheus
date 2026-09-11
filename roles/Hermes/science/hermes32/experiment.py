"""HERMES-32: does instrumentation make a silent failure convergeable?

    python roles/Hermes/science/hermes32/experiment.py

Runs BEFORE, AFTER, three ABLATIONS, the preserved negatives, the
false-merge/false-split cross-check and the cost measurement, and writes
results.json. Predictions were committed first, at 8094151be
(FREEZE_AND_PREREGISTRATION.md).

HONESTY NOTE ON RECONSTRUCTION. The specimen's own invocation --
`git pull` in the canonical checkout -- is NOT re-run here. Repeating the
violation to measure it would be absurd. Instead the two historical
observations keep their FROZEN message and exit code and are joined to the
workspace facts measured with attest(), which runs no mutating command.
Those facts (root commit, worktree role) are stable properties of where
Atalanta and Hermes stood, were as true that morning as now, and were
genuinely available to both observers. Everything else in this experiment
-- every negative control -- is a command actually executed.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "convergence"))

import git_observe as G                                          # noqa: E402
import signature as S                                            # noqa: E402
import probe as P                                                # noqa: E402

SEATS = S.seat_names()
REPO_ROOT = HERE.parents[3]
CANONICAL = Path(os.environ.get("HERMES32_CANONICAL", str(REPO_ROOT.parents[0] / "Prometheus")))


def key(obs):
    return S.s4_whole_observation(obs, seats=SEATS)


def drop(obs, *fields):
    return {k: v for k, v in obs.items() if k not in fields}


# ---------------------------------------------------------------- BEFORE ---
# The frozen historical observation. `stdout_head` carries the same string as
# `message` because that is literally what both observers quoted; it is present
# so the reconstructed specimen has the SAME FIELD SET as an observe() result.
# Without that, specimen and control differ in SHAPE and can never collide,
# which silently voids the ablation -- the first run of this experiment had
# exactly that bug and the preregistered prediction ("remove both -> convergence
# DISAPPEARS") is what exposed it.
FROZEN = {"exception_type": "NoError", "message": "Already up to date.",
          "exit_state": "success", "exit_code": 0,
          "stdout_head": "Already up to date."}

BEFORE = {
    "Atalanta": dict(FROZEN),          # roles/Atalanta/calibration/LEDGER.md:79
    "Hermes": dict(FROZEN),            # roles/Hermes/calibration/CALIBRATION.md row 8
}


def build_negatives(scratch: Path):
    """Measured, not constructed. Two permitted commands really run in the
    canonical checkout (D-23 s1 allows fetch, inspection and worktree
    management there) and a legitimate pull really runs in another repo."""
    bare, work = scratch / "other.git", scratch / "other"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    subprocess.run(["git", "clone", "-q", str(bare), str(work)], check=True)
    for k, v in (("user.email", "t@t"), ("user.name", "t")):
        subprocess.run(["git", "-C", str(work), "config", k, v], check=True)
    (work / "f.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(work), "add", "f.txt"], check=True)
    subprocess.run(["git", "-C", str(work), "commit", "-q", "-m", "init"], check=True)
    subprocess.run(["git", "-C", str(work), "push", "-q", "origin", "HEAD:refs/heads/main"], check=True)
    subprocess.run(["git", "-C", str(work), "branch", "--set-upstream-to=origin/main"],
                   check=True, capture_output=True)
    neg = {}
    neg["CTL-E1 legitimate pull, different repository"] = G.observe(["pull"], cwd=str(work))
    neg["CTL-E2 permitted fetch in the canonical checkout"] = G.observe(["fetch", "origin"], cwd=str(CANONICAL))
    neg["CTL-E3 permitted inspection in the canonical checkout"] = G.observe(["status", "--short"], cwd=str(CANONICAL))
    neg["CTL-E4 permitted worktree management in the canonical checkout"] = G.observe(
        ["worktree", "list"], cwd=str(CANONICAL))
    return neg


def main():
    scratch = Path(tempfile.mkdtemp(prefix="hermes32_"))
    out = {"preregistered_at": "8094151be", "canonical": str(CANONICAL)}
    try:
        print("HERMES-32 -- instrumenting one silent failure")
        print("=" * 74)

        # ---- the instrument's facts for the place the specimen happened ----
        facts = G.attest(["pull"], cwd=str(CANONICAL))
        print("\nINSTRUMENT facts for the canonical checkout (no command run):")
        print("  repo_id        {}".format(facts["repo_id"]))
        print("  workspace_role {}".format(facts["workspace_role"]))
        out["canonical_facts"] = facts

        neg = build_negatives(scratch)
        print("\nNEGATIVE CONTROLS, measured by actually running them:")
        for name, o in neg.items():
            print("  {:<58} exit={} stdout={!r}".format(name[:58], o["exit_code"], o["stdout_head"][:38]))
        out["negatives"] = neg

        # ------------------------------------------------------- BEFORE ----
        print("\nBEFORE  (observation = what the observers actually recorded)")
        b_keys = {k: key(v) for k, v in BEFORE.items()}
        ctl1_before = key(drop(neg["CTL-E1 legitimate pull, different repository"],
                               "repo_id", "workspace_role", "command"))
        print("  Atalanta {}\n  Hermes   {}".format(b_keys["Atalanta"], b_keys["Hermes"]))
        print("  CTL-E1   {}   <- a LEGITIMATE execution".format(ctl1_before))
        before_converges = len(set(b_keys.values())) == 1
        before_collides = ctl1_before in set(b_keys.values())
        before_verdict = "UNSIGNABLE" if before_collides else ("EXACT" if before_converges else "SPLIT")
        print("  converge={}  collides_with_legitimate={}  ->  {}".format(
            before_converges, before_collides, before_verdict))
        out["before"] = {"keys": b_keys, "ctl_e1_key": ctl1_before,
                         "converges": before_converges, "collides": before_collides,
                         "verdict": before_verdict}

        # -------------------------------------------------------- AFTER ----
        print("\nAFTER   (same observation + the instrument's two facts)")
        after = {k: dict(v, **facts) for k, v in BEFORE.items()}   # facts already carries command
        a_keys = {k: key(v) for k, v in after.items()}
        n_keys = {n: key(o) for n, o in neg.items()}
        for k, v in a_keys.items():
            print("  {:<9}{}".format(k, v))
        for n, v in n_keys.items():
            print("  {:<58} {}".format(n[:58], v))
        after_converges = len(set(a_keys.values())) == 1
        after_collides = [n for n, v in n_keys.items() if v in set(a_keys.values())]
        after_verdict = "UNSIGNABLE" if after_collides else ("EXACT" if after_converges else "SPLIT")
        print("  converge={}  collisions={}  ->  {}".format(
            after_converges, after_collides or "none", after_verdict))
        out["after"] = {"keys": a_keys, "negative_keys": n_keys, "converges": after_converges,
                        "collisions": after_collides, "verdict": after_verdict}

        # ----------------------------------------------------- ABLATION ----
        print("\nABLATION  (remove the new observation, change nothing else)")
        out["ablations"] = {}
        for label, fields in (("remove repo_id", ("repo_id",)),
                              ("remove workspace_role", ("workspace_role",)),
                              ("remove both", ("repo_id", "workspace_role"))):
            ab = {k: drop(v, *fields) for k, v in after.items()}
            abn = {n: drop(o, *fields) for n, o in neg.items()}
            ak = {k: key(v) for k, v in ab.items()}
            an = {n: key(v) for n, v in abn.items()}
            conv = len(set(ak.values())) == 1
            coll = [n for n, v in an.items() if v in set(ak.values())]
            verdict = "UNSIGNABLE" if coll else ("EXACT" if conv else "SPLIT")
            gone = verdict != "EXACT"
            print("  {:<24} converge={:<5} collisions={:<40} -> {:<11} convergence {}".format(
                label, str(conv), str(coll or "none")[:40], verdict,
                "DISAPPEARS" if gone else "SURVIVES"))
            out["ablations"][label] = {"converges": conv, "collisions": coll,
                                       "verdict": verdict, "convergence_disappears": gone}

        # ------------------------------- FALSE MERGE / FALSE SPLIT --------
        print("\nFALSE MERGE / FALSE SPLIT  (s4 over the five original cases)")
        cross = {}
        for c in S.load_cases():
            scored = P.scored_observations(c)
            ks = {key(o["observed"]) for o in scored}
            cross[c["id"]] = {"observers": len(scored), "distinct_keys": len(ks),
                              "s2_verdict": P.classify(c)[0]}
            print("  {:<9} observers={} s4_keys={} s2_verdict={}".format(
                c["id"], len(scored), len(ks), cross[c["id"]]["s2_verdict"]))
        out["cross_check"] = cross

        # ------------------------------------------------------- COST -----
        print("\nCOST imposed on an ordinary caller")
        t0 = time.time()
        for _ in range(10):
            G.workspace_facts(cwd=str(CANONICAL))
        per_call = (time.time() - t0) / 10
        t1 = time.time()
        for _ in range(10):
            subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(CANONICAL),
                           capture_output=True, text=True, timeout=600)
        baseline = (time.time() - t1) / 10
        print("  workspace_facts()      {:.1f} ms per call (2 read-only git invocations)".format(
            per_call * 1000))
        print("  git rev-parse HEAD     {:.1f} ms per call, for scale".format(baseline * 1000))
        print("  writes: none. raises: none. every execution returns an observation.")
        out["cost"] = {"workspace_facts_ms": round(per_call * 1000, 1),
                       "git_rev_parse_ms": round(baseline * 1000, 1)}

        (HERE / "results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
        print("\nrows written to roles/Hermes/science/hermes32/results.json")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    main()
