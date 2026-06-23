"""validate_ec_rich_diagonal.py — paired validator for EC_RICH_DIAGONAL_2026-06-15.md.

Per feedback_validators_ship_with_docs: the results doc makes structured claims
(cell/void counts, the D_JOINT partition, survivor=0, three laws at 1000/1000);
this script re-derives each from the shipped JSON artifact and a live catalog
recount, and checks the doc text against them.

Run:  python harmonia/experiments/validate_ec_rich_diagonal.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from theseus.generators.a1_catalog_cross_product import _load_catalog, _get_int  # noqa: E402
from theseus.config import BSD_RICH_DB_PATH                                       # noqa: E402

EXP = REPO / "harmonia" / "experiments"
DOC = REPO / "harmonia" / "proposals" / "2026-06-09" / "EC_RICH_DIAGONAL_2026-06-15.md"

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name} :: {detail}")


def main():
    o = json.loads((EXP / "ec_rich_diagonal_results.json").read_text(encoding="utf-8"))
    text = DOC.read_text(encoding="utf-8")

    check("artifact + doc exist", (EXP / "ec_rich_diagonal_results.json").exists()
          and DOC.exists())

    # --- lattice geometry: 9 invariants, 10368 cells -----------------------
    check("9 integer invariants", len(o["meta"]["invariants"]) == 9
          and set(o["meta"]["invariants"]) >= {"sha_an", "num_bad_primes", "cm",
                                                "signD", "conductor_radical"})
    check("cell count 10,368 == 9·8·6·6·4",
          o["n_cells"] == 10368 == 72 * 6 * 6 * 4 // 6 * 6, str(o["n_cells"]))
    # (the //6*6 keeps the literal honest: 72 ordered pairs × 36 op-pairs × 4 rel)
    check("cell count exactly 72*36*4", o["n_cells"] == 72 * 36 * 4)

    # --- void partition ----------------------------------------------------
    bj = o["by_joint_class"]
    check("void split 503 D_MARGINAL / 98 D_THEOREM / 176 D_JOINT == artifact",
          o["n_voids"] == 777 and bj.get("D_MARGINAL") == 503
          and bj.get("D_THEOREM") == 98 and bj.get("D_JOINT") == 176, str(bj))
    check("doc cites the same split",
          all(s in text for s in ("503", "98", "176", "777")))

    # --- D_JOINT tag partition is COMPLETE (no untagged survivors) ---------
    tags = Counter((c["known_math"].split(":")[0] if c["known_math"] else "UNTAGGED")
                   for c in o["joint_candidates"])
    check("176 D_JOINT candidates recorded", len(o["joint_candidates"]) == 176)
    check("D_JOINT partition: 41 DEFINITIONAL / 9 LITERATURE / 107 DEGENERATE "
          "/ 19 LOW-INFO / 0 UNTAGGED",
          tags.get("DEFINITIONAL") == 41
          and tags.get("LITERATURE (Lorenzini 2011)") == 9
          and tags.get("DEGENERATE") == 107
          and tags.get("LOW-INFO") == 19
          and tags.get("UNTAGGED", 0) == 0, str(dict(tags)))
    check("survivors == 0 (clean kill: no novel within-object law)",
          o["survivors"] == [] and "Novel within-object laws found = 0" in text,
          str(o["survivors"]))

    # --- every DEFINITIONAL/LITERATURE tag is a conductor/radical or
    #     torsion/tamagawa cell (the tagger is not hand-waving) -------------
    fam = {frozenset((c["inv_a"], c["inv_b"]))
           for c in o["joint_candidates"]
           if c["known_math"].startswith(("DEFINITIONAL", "LITERATURE"))}
    check("tagged-known families are exactly {conductor,radical} and "
          "{torsion,tamagawa}",
          fam == {frozenset(("conductor", "conductor_radical")),
                  frozenset(("torsion", "tamagawa_product"))}, str(fam))

    # --- perm-null cleanly separates the two real law-families from the
    #     degenerate columns: maximal signal (perm 0) <=> tagged-known law ----
    perm0 = [c for c in o["joint_candidates"] if c["perm_null_void_rate"] == 0.0]
    known = [c for c in o["joint_candidates"]
             if c["known_math"].startswith(("DEFINITIONAL", "LITERATURE"))]
    check("exactly 50 D_JOINT have perm_null 0, and they ARE the 50 "
          "DEFINITIONAL+LITERATURE cells (the real laws have maximal signal)",
          len(perm0) == 50 and len(known) == 50
          and {c["f"] + c["g"] + c["inv_a"] + c["inv_b"] + c["rel"] for c in perm0}
          == {c["f"] + c["g"] + c["inv_a"] + c["inv_b"] + c["rel"] for c in known})
    check("every perm_null>0 D_JOINT is DEGENERATE/LOW-INFO (cm/signD/sha_an) "
          "— the column-shuffle null correctly demotes the near-constant fields",
          all(c["known_math"].startswith(("DEGENERATE", "LOW-INFO"))
              for c in o["joint_candidates"] if c["perm_null_void_rate"] > 0.0))

    # --- live recount of the three laws (independent of the sweep) ---------
    ecs = _load_catalog(BSD_RICH_DB_PATH)
    rad = sum(1 for e in ecs
              if _get_int(e, "conductor") % _get_int(e, "conductor_radical") == 0)
    par = sum(1 for e in ecs
              if _get_int(e, "conductor") % 2 == _get_int(e, "conductor_radical") % 2)
    tor = sum(1 for e in ecs
              if _get_int(e, "tamagawa_product") % _get_int(e, "torsion") == 0)
    check("rad(N) | N holds 1000/1000 (live)", rad == 1000, str(rad))
    check("N == rad(N) (mod 2) holds 1000/1000 (live)", par == 1000, str(par))
    check("torsion | tamagawa_product holds 1000/1000 (live)", tor == 1000, str(tor))

    # --- the committed Proposal B diagonal artifact is UNTOUCHED -----------
    prior = json.loads((EXP / "diagonal_void_results.json").read_text(encoding="utf-8"))
    check("committed diagonal_void_results.json still 51 voids / 9 joint "
          "(this exploration did not overwrite it)",
          prior["ec"]["n_voids"] == 51 and prior["ec"]["n_joint"] == 9)

    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
