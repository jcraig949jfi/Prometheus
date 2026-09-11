"""Generate the C1-b golden fixture. Run deliberately, never in CI.

These values are REGRESSION anchors for this implementation. They are not a
claim about the published figures and they are not a tolerance. Regenerating
them silently would destroy the only thing they are for, so this script
refuses to overwrite an existing fixture unless --force is given, and it
records the reason it was regenerated.

    python -m herakles.evca.tools.make_golden --reason "<why>"
"""
from __future__ import annotations

from herakles.workspace import assert_not_canonical

import argparse
import io
import json
import os
import sys

from herakles import evca
from herakles.evca import genomes as G

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURE = os.path.join(HERE, "..", "tests", "golden_c1b.json")

CONFIG = {"n_ics": 64, "n_cells": 21, "steps": 42, "seed": 20260908}
SELECTED = {"rule_hex": G.GENOMES["par"]["hex"], "n_cells": 21, "steps": 42,
            "seed": 20260908, "ic_index": 0}


def build():
    ics = evca.make_ics(CONFIG["n_ics"], CONFIG["n_cells"], CONFIG["seed"])
    rules = {}
    for name in G.NAMES:
        r = evca.classify(evca.decode_table(G.rule_hex(name)), ics,
                          CONFIG["steps"], witness_limit=evca.WITNESS_LIMIT)
        rules[name] = {
            "hex": G.rule_hex(name),
            "accuracy": r["accuracy"],
            "n_correct": r["n_correct"],
            "n_incorrect": r["n_incorrect"],
            "witness": r["witness"],
            "witness_truncated": r["witness_truncated"],
            "correct_mask_digest": r["correct_mask_digest"],
            "uniform_fixed_points": r["uniform_fixed_points"],
        }
    sel = evca.selected_trajectory(**SELECTED)
    return {
        "note": ("Regression anchors for herakles.evca on a small fixed "
                 "configuration. NOT a claim about published performance and "
                 "NOT a tolerance; the historical comparison is C1-e."),
        "config": CONFIG,
        "rules": rules,
        "selected_trajectory": {"inputs": SELECTED, "digest": sel["digest"],
                                "shape": sel["shape"]},
    }


def main(argv=None):
    # D-23: refuse to run from the canonical checkout.
    _ws = assert_not_canonical("regenerate the golden fixture")
    ap = argparse.ArgumentParser()
    ap.add_argument("--reason", required=True,
                    help="why this fixture is being regenerated")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    path = os.path.abspath(FIXTURE)
    if os.path.exists(path) and not args.force:
        print("refusing to overwrite %s without --force" % path)
        return 2
    data = build()
    data["generated_reason"] = args.reason
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(data, indent=1, sort_keys=True) + "\n")
    print("wrote %s" % path)
    for name, r in data["rules"].items():
        print("  %-10s accuracy=%.6f  incorrect=%3d  %s"
              % (name, r["accuracy"], r["n_incorrect"],
                 r["correct_mask_digest"][:24]))
    print("  selected trajectory %s shape=%s"
          % (data["selected_trajectory"]["digest"][:24],
             data["selected_trajectory"]["shape"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
