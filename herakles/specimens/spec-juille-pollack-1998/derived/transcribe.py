"""Transcribe Table 2 of Juille and Pollack 1998 from the text layer.

Lines 782-791 of derived/gp98_text.txt (0-based) hold five rules, two
lines each, 8 groups of 8 binary digits per line, digits separated by "/".
Q1 of PROTOCOL.md (GKL transcribed == GKL derived) is checked here and the
script refuses to write the table file if it fails.
"""
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
from herakles import evca                                # noqa: E402
from herakles.evca import genomes as G                    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TEXT = os.path.join(HERE, "gp98_text.txt")
OUT = os.path.join(HERE, "juille_pollack_1998_rule_tables.json")

LINES = {"coev1": (782, 783), "coev2": (784, 785), "das": (786, 787),
         "abk": (788, 789), "gkl": (790, 791)}
PUBLISHED_P = {  # Table 1, lines 449-453, "+/- 0.001"
    "coev1": {149: 0.851, 599: 0.810, 999: 0.795},
    "coev2": {149: 0.860, 599: 0.802, 999: 0.785},
    "das":   {149: 0.823, 599: 0.778, 999: 0.764},
    "abk":   {149: 0.824, 599: 0.764, 999: 0.730},
    "gkl":   {149: 0.815, 599: 0.773, 999: 0.759},
}


def digits(line):
    # keep only the 8-digit groups; the label ("Das rule") precedes them
    groups = re.findall(r'(?:/[01]){8}', line)
    return "".join(g.replace("/", "") for g in groups)


def main():
    text = open(TEXT, encoding="utf-8").read().split("\n")
    tables = {}
    for name, (a, b) in LINES.items():
        bits = digits(text[a]) + digits(text[b])
        assert len(bits) == 128, (name, len(bits))
        hexs = "%032x" % int(bits, 2)
        tables[name] = {"bits": bits, "hex": hexs, "text_lines": [a, b],
                        "published_P": PUBLISHED_P[name]}
    # Q1: GKL calibration
    derived = evca.encode_table(evca.gkl_rule_table())
    q1 = tables["gkl"]["hex"] == derived
    print("Q1 GKL transcribed == derived:", q1, tables["gkl"]["hex"], derived)
    if not q1:
        diff = [i for i in range(128) if tables["gkl"]["bits"][i]
                != bin(int(derived, 16))[2:].zfill(128)[i]]
        print("STOP: differing bit positions", diff)
        return 1
    # Q2: Das rule identity against held genomes
    held = {n: G.rule_hex(n) for n in G.NAMES}
    matches = {n: [h for h, hx in held.items() if hx == t["hex"]]
               for n, t in tables.items()}
    print("identity against held genomes:", matches)
    out = {"source": "gp98.pdf Table 2 (lines 782-791 of gp98_text.txt), "
                     "bit order: leftmost = input 0000000",
           "q1_gkl_calibration": q1,
           "identity_against_held": matches,
           "tables": tables}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
