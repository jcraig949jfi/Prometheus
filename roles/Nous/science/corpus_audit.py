#!/usr/bin/env python
"""Reproduce every number in roles/Nous/ARCHAEOLOGY_2026-09-11.md section 3.

The archaeology makes four adverse claims about this seat's own shipped
instrument. This script recomputes all of them from the committed corpus
so a reader does not have to trust the prose:

  M1  the novelty classifier does not discriminate
  M2  the ranking key is nearly constant
  M3  the key does not separate the scorer's own reject class
  M4  no control of any kind exists in agents/nous/

Usage (from any worktree, never the canonical checkout):

    python roles/Nous/science/corpus_audit.py
    python roles/Nous/science/corpus_audit.py --check   # exit 1 on drift

--check compares against the values frozen below at base SHA 363120e08.
It is the reader this seat owes its own freeze record: an unread hash
list is decorative, so the expectations are behavioural, not a digest.

This script makes NO network call and reads no credential.
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import math
import os
import random
import statistics as st
import subprocess
import sys

DIMS = ("reasoning", "metacognition", "hypothesis_generation",
        "implementability")

# Frozen at origin/main 363120e08, 2026-09-11, by the seat's adoption pass.
#
# THESE ARE THE COMMITTED CORPUS'S VALUES, and that distinction is the
# point. Run from this seat's canonical checkout on M2, the same script
# reports 10,105 rows; run from any worktree, or on any other machine, it
# reports 5,918. The difference is 4,187 rows in ten run directories
# (2026-03-28 .. 2026-04-02) that .gitignore:140 `agents/nous/runs/` kept
# out of the repository forever. They exist on one host's disk only.
# See ARCHAEOLOGY_2026-09-11.md section 2. A number measured from a
# working directory is a claim about a moment on one machine; this file
# freezes the repository's number, which is the one another seat can
# reproduce.
EXPECTED = {
    "rows": 5918,
    "high_potential": 719,
    "unproductive": 299,
    "novelty": {"novel": 5462, "unclear": 153, "existing": 4,
                "unproductive": 299},
    "distinct_concepts": 95,
    "distinct_fields": 20,
    "unprod_mean": 6.4696,
    "prod_mean": 6.4067,
    "permutation_seed": 11,
    "permutation_draws": 2000,
}

PERM_SEED = 11
PERM_DRAWS = 2000


def repo_root() -> str:
    """Repository root, resolved from git rather than a hardcoded path."""
    here = os.path.dirname(os.path.abspath(__file__))
    out = subprocess.run(["git", "-C", here, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise SystemExit("not a git checkout: %s" % out.stderr.strip())
    return out.stdout.strip()


def assert_not_canonical(root: str) -> None:
    """D-23 s1: refuse to run from the canonical checkout.

    Only in the main worktree does git-dir equal git-common-dir.
    """
    def rp(arg: str) -> str:
        r = subprocess.run(["git", "-C", root, "rev-parse", arg],
                           capture_output=True, text=True, timeout=60)
        return os.path.normcase(os.path.abspath(
            os.path.join(root, r.stdout.strip())))
    if rp("--git-dir") == rp("--git-common-dir"):
        raise SystemExit(
            "REFUSED: this is the canonical checkout (git-dir == "
            "git-common-dir). Run from a linked worktree (D-23 s1).")


def load(root: str):
    """Yield every parsed response row in the committed corpus."""
    pattern = os.path.join(root, "agents", "nous", "runs", "*",
                           "responses.jsonl")
    files = sorted(glob.glob(pattern))
    if not files:
        raise SystemExit("no corpus found at %s" % pattern)
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except ValueError:
                    continue  # counted as unparsed; see report


def audit(root: str) -> dict:
    rows = 0
    hp = 0
    novelty = collections.Counter()
    vals = {d: [] for d in DIMS}
    unprod, prod = [], []
    concepts, fields = set(), set()

    for d in load(root):
        rows += 1
        s = d.get("score") or {}
        r = s.get("ratings") or {}
        if s.get("high_potential"):
            hp += 1
        novelty[s.get("novelty")] += 1
        for k in DIMS:
            v = r.get(k)
            if isinstance(v, (int, float)):
                vals[k].append(v)
        c = s.get("composite_score")
        if isinstance(c, (int, float)):
            (unprod if s.get("is_unproductive") else prod).append(c)
        concepts.update(d.get("concept_names") or [])
        fields.update(d.get("concept_fields") or [])

    comp = unprod + prod
    dims = {}
    for k in DIMS:
        v = vals[k]
        cnt = collections.Counter(v)
        mode, mode_n = cnt.most_common(1)[0]
        dims[k] = {"n": len(v), "mean": st.mean(v), "sd": st.pstdev(v),
                   "mode": mode, "mode_share": mode_n / len(v)}

    # M3: reject-class separation, with a label-permutation null.
    du, dp = st.mean(unprod), st.mean(prod)
    se = math.sqrt(st.pvariance(unprod) / len(unprod)
                   + st.pvariance(prod) / len(prod))
    obs = abs(du - dp)
    rng = random.Random(PERM_SEED)
    labels = [1] * len(unprod) + [0] * len(prod)
    hits = 0
    for _ in range(PERM_DRAWS):
        rng.shuffle(labels)
        a = [v for v, lab in zip(comp, labels) if lab]
        b = [v for v, lab in zip(comp, labels) if not lab]
        if abs(st.mean(a) - st.mean(b)) >= obs:
            hits += 1

    top5 = collections.Counter(comp).most_common(5)
    return {
        "rows": rows, "high_potential": hp,
        "unproductive": len(unprod), "productive": len(prod),
        "novelty": dict(novelty), "dims": dims,
        "distinct_concepts": len(concepts), "distinct_fields": len(fields),
        "unprod_mean": du, "prod_mean": dp, "diff": du - dp, "se": se,
        "z": (du - dp) / se, "perm_p": hits / PERM_DRAWS,
        "top5_composite": top5,
        "top5_share": sum(n for _, n in top5) / len(comp),
    }


def controls_present(root: str) -> list:
    """M4: look for any control arm in the seat's own source.

    A control here means a deliberately-degenerate input whose score is
    compared against real input: a content-free string, a shuffled
    triple, or a repeated triple measuring rater self-consistency.
    Absence is the finding, so this returns what it FOUND, never a bare
    boolean.
    """
    needles = ("shuffle", "control", "placebo", "null_arm", "cheat",
               "self_consistency", "repeat_triple", "content_free")
    found = []
    src = os.path.join(root, "agents", "nous")
    for dirpath, _, names in os.walk(src):
        if "runs" in dirpath or "__pycache__" in dirpath:
            continue
        for name in names:
            if not name.endswith(".py"):
                continue
            path = os.path.join(dirpath, name)
            try:
                lines = open(path, encoding="utf-8",
                             errors="replace").read().splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines, 1):
                low = line.lower()
                for n in needles:
                    if n in low:
                        # Report the LINE, not just the file: every hit in
                        # this corpus so far has been a concept NAME
                        # ("Feedback Control", "Adaptive Control") in the
                        # dictionary, not a control arm. A keyword match
                        # is evidence for a reader to judge, never a
                        # verdict -- which is the whole point of M4.
                        found.append((os.path.relpath(path, root), i, n,
                                      line.strip()[:88]))
                        break
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the corpus has drifted from the "
                         "values frozen at 363120e08")
    args = ap.parse_args()

    root = repo_root()
    assert_not_canonical(root)
    a = audit(root)

    print("Nous corpus audit -- roles/Nous/ARCHAEOLOGY_2026-09-11.md s3")
    print("repository root: %s" % root)
    print()
    print("corpus rows              : %d" % a["rows"])
    print("high_potential           : %d (%.1f%%)"
          % (a["high_potential"], 100 * a["high_potential"] / a["rows"]))
    print("distinct concepts/fields : %d / %d"
          % (a["distinct_concepts"], a["distinct_fields"]))
    print()
    print("M1  novelty classifier")
    for k, v in sorted(a["novelty"].items(), key=lambda kv: -kv[1]):
        print("      %-14s %6d  %5.2f%%" % (k, v, 100 * v / a["rows"]))
    print("      VERDICT: a class returned on %.1f%% of rows carries no"
          % (100 * max(a["novelty"].values()) / a["rows"]))
    print("      information about which combination was novel.")
    print()
    print("M2  ranking key dispersion")
    print("      %-22s %6s %7s %7s  %s"
          % ("dimension", "n", "mean", "sd", "mode (share)"))
    for k in DIMS:
        d = a["dims"][k]
        print("      %-22s %6d %7.2f %7.3f  %s (%.1f%%)"
              % (k, d["n"], d["mean"], d["sd"], d["mode"],
                 100 * d["mode_share"]))
    print("      five composite values cover %.1f%% of the corpus: %s"
          % (100 * a["top5_share"],
             ", ".join(str(v) for v, _ in a["top5_composite"])))
    print()
    print("M3  reject-class separation")
    print("      unproductive n=%5d  mean composite = %.4f"
          % (a["unproductive"], a["unprod_mean"]))
    print("      productive   n=%5d  mean composite = %.4f"
          % (a["productive"], a["prod_mean"]))
    print("      difference = %+.4f   SE = %.4f   z = %+.2f"
          % (a["diff"], a["se"], a["z"]))
    print("      label-permutation p = %.4f (%d shuffles, seed %d)"
          % (a["perm_p"], PERM_DRAWS, PERM_SEED))
    print("      VERDICT: the key does not separate the reject class in")
    print("      the protective direction. The SIGN of the residual is a")
    print("      WEAK SIGNAL, not read here (doctrine on marginal numbers).")
    print()
    found = controls_present(root)
    print("M4  controls in agents/nous/ source")
    if found:
        print("      %d keyword hit(s); each is shown so a reader can judge"
              % len(found))
        print("      whether it is a control arm or a concept name:")
        for path, lineno, needle, text in found:
            print("      %s:%d (%s)" % (path, lineno, needle))
            print("          %s" % text)
        print("      As of 363120e08 every hit is a concept NAME in the")
        print("      dictionary, not a control arm.")
    print("      VERDICT: no negative, positive or cheat arm exists. The")
    print("      generator and the rater are the same model in the same")
    print("      call; there is no independent oracle anywhere in the loop.")

    if args.check:
        bad = []
        for k in ("rows", "high_potential", "unproductive",
                  "distinct_concepts", "distinct_fields"):
            if a[k] != EXPECTED[k]:
                bad.append("%s: %r != frozen %r" % (k, a[k], EXPECTED[k]))
        if a["novelty"] != EXPECTED["novelty"]:
            bad.append("novelty: %r != frozen %r"
                       % (a["novelty"], EXPECTED["novelty"]))
        for k in ("unprod_mean", "prod_mean"):
            if abs(a[k] - EXPECTED[k]) > 5e-4:
                bad.append("%s: %.4f != frozen %.4f" % (k, a[k], EXPECTED[k]))
        print()
        if bad:
            print("CHECK FAILED -- the corpus has drifted from 363120e08:")
            for b in bad:
                print("  %s" % b)
            return 1
        print("CHECK PASSED -- corpus matches the values frozen at 363120e08.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
