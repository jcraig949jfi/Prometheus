"""Transcribe Table 2 of Andre, Bennett, Koza 1996 (GP-96 pp. 3-11) from the
text layer, lines 315-328 of derived/gp1996gkl_text.txt: GKL 1978, Davis
1995, Das (1995), and the GP rule, "in truth table order from 0000000 to
1111111". GKL transcribed must equal GKL derived (calibration) or nothing is
written. Then every table is compared with Juille and Pollack 1998's
reprint, which was transcribed and calibrated independently.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
from herakles import evca                                # noqa: E402
from herakles.evca import genomes as G                    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TEXT = os.path.join(HERE, "gp1996gkl_text.txt")
OUT = os.path.join(HERE, "abk_1996_rule_tables.json")
JP = os.path.join(HERE, "..", "..", "spec-juille-pollack-1998", "derived",
                  "juille_pollack_1998_rule_tables.json")

LINES = {"gkl": (315, 316, 317), "davis1995": (318, 319, 320),
         "das1995": (321, 322, 323), "abk_gp": (326, 327, 328)}
# Table 1 (lines 93-106): out-of-sample accuracy at N = 149, 600 steps,
# iid Bernoulli(0.5) ICs, over 10^6 or 10^7 cases.
PUBLISHED = {"gkl": {"acc": 0.816, "cases": 1e6},
             "davis1995": {"acc": 0.818, "cases": 1e6},
             "das1995": {"acc": 0.82178, "cases": 1e7},
             "abk_gp": {"acc": 0.82326, "cases": 1e7},
             "das1994_ga_best": {"acc": 0.769, "cases": 1e6}}


def main():
    L = open(TEXT, encoding="utf-8").read().split("\n")
    tables = {}
    for name, idx in LINES.items():
        bits = "".join("".join(re.findall(r"[01]{8}", L[i])) for i in idx)
        assert len(bits) == 128, (name, len(bits))
        tables[name] = {"bits": bits, "hex": "%032x" % int(bits, 2),
                        "text_lines": list(idx),
                        "published": PUBLISHED[name]}
    derived = evca.encode_table(evca.gkl_rule_table())
    q1 = tables["gkl"]["hex"] == derived
    print("GKL transcribed == derived:", q1)
    if not q1:
        print("STOP"); return 1
    jp = json.load(open(JP, encoding="utf-8"))["tables"]
    cross = {"abk_gp == JP abk": tables["abk_gp"]["hex"] == jp["abk"]["hex"],
             "das1995 == JP das": tables["das1995"]["hex"] == jp["das"]["hex"],
             "gkl == JP gkl": tables["gkl"]["hex"] == jp["gkl"]["hex"]}
    held = {n: G.rule_hex(n) for n in G.NAMES}
    ident = {n: [h for h, hx in held.items() if hx == t["hex"]]
             for n, t in tables.items()}
    print("cross-check against Juille-Pollack reprint:", cross)
    print("identity against held genomes:", ident)
    out = {"source": "gp1996gkl.pdf Table 2 (lines 315-328 of "
                     "gp1996gkl_text.txt); truth-table order 0000000..1111111",
           "gkl_calibration": q1, "cross_check_juille_pollack": cross,
           "identity_against_held": ident,
           "published_table1_note": "Table 1 also lists the best 1994 GA rule "
                                    "of Das, Mitchell, Crutchfield at 76.9% "
                                    "over 10^6 cases; no table printed for it",
           "tables": tables}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
