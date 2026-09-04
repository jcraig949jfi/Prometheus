#!/usr/bin/env python3
"""Validator for sfe.issue_disposition.v1.

A disposition ledger that cites tests which do not exist, or commits which are
not in the repo, is a claim about a moment rather than a record. This checks the
citations resolve, so the ledger cannot quietly drift from the tree it describes.

    python roles/Daedalus/sprint_20260904/validate_disposition.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LEDGER = os.path.join(HERE, "issue_disposition.json")
TESTDIR = os.path.join(REPO, "SerendipityFoundry", "SerendipityFoundryEngine",
                       "tests")

VOCAB_KEYS = ("implementation", "deployment", "qualification", "disposition")
REQUIRED = ("id", "original_claim", "disposition", "reproduction",
            "corrected_claim", "implementation", "deployment", "qualification")

errors, warnings = [], []


def main():
    with open(LEDGER, encoding="utf-8") as fh:
        led = json.load(fh)
    vocab = led["status_vocabulary"]

    # every test name declared anywhere in the engine test tree
    known_tests = set()
    for fn in os.listdir(TESTDIR):
        if not fn.endswith(".py"):
            continue
        with open(os.path.join(TESTDIR, fn), encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("def test_"):
                    known_tests.add(line[4:].split("(")[0].strip())

    seen = set()
    for iss in led["issues"]:
        i = iss.get("id", "<no id>")
        for k in REQUIRED:
            if k not in iss:
                errors.append("%s: missing required field %r" % (i, k))
        if i in seen:
            errors.append("%s: duplicate id" % i)
        seen.add(i)

        for k in VOCAB_KEYS:
            v = iss.get(k)
            if v is not None and v not in vocab[k]:
                errors.append("%s: %s=%r not in vocabulary %s"
                              % (i, k, v, vocab[k]))

        # A confirmed-and-fixed issue must cite at least one test.
        if iss.get("implementation") == "FIXED_TESTED" and not iss.get("tests"):
            errors.append("%s: FIXED_TESTED but cites no tests" % i)

        # Cited tests must exist. Free-text citations (a script, not a pytest)
        # are allowed but flagged so they stay visible.
        for t in iss.get("tests", []):
            name = t.split()[0]
            if name.startswith("test_"):
                if name not in known_tests:
                    errors.append("%s: cites test %r which does not exist"
                                  % (i, name))
            else:
                warnings.append("%s: non-pytest evidence citation: %s"
                                % (i, t[:60]))

        # Cited commits must resolve in this repo.
        c = iss.get("commit")
        if c:
            p = subprocess.run(["git", "-C", REPO, "cat-file", "-e",
                                "%s^{commit}" % c],
                               capture_output=True, text=True)
            if p.returncode != 0:
                errors.append("%s: cites commit %s which does not resolve"
                              % (i, c))

        # A refuted issue must not carry a constraint -- that is the whole
        # point of CT-SFE-6: a false finding must not become a live guard.
        if iss.get("disposition") == "REFUTED" and iss.get("constraint"):
            errors.append("%s: REFUTED but still carries constraint %r"
                          % (i, iss["constraint"]))

        # Nothing may claim live qualification while undeployed.
        if (iss.get("qualification") == "LIVE_QUALIFIED"
                and iss.get("deployment") == "NOT_DEPLOYED"):
            errors.append("%s: claims LIVE_QUALIFIED while NOT_DEPLOYED" % i)

    print("issues: %d" % len(led["issues"]))
    print("known engine tests: %d" % len(known_tests))
    for w in warnings:
        print("  WARN  %s" % w)
    for e in errors:
        print("  ERROR %s" % e)
    print("\n%s" % ("VALID" if not errors else "INVALID (%d errors)"
                    % len(errors)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
