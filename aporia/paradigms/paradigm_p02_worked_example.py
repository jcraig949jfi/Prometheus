"""PARADIGM-P02 worked example — Cohomological Obstruction, executed.

The paradigm's move: detect global impossibility via local-to-global failure
classes. Executable instances in our substrate, three legs:

  A. THE OBSTRUCTION MADE COUNTABLE (g2c_curves): the 2x2 census of
     (locally_solvable, globally_solvable). The cell (true, false) is the
     paradigm incarnate — everywhere-locally-solvable curves with no rational
     point; nothing OTHER than a cohomological obstruction class can explain
     membership in that cell.
  B. THE EXEMPLAR VERIFIED (ec_curvedata): Cassels' pairing forces |Sha| to be
     a perfect square for elliptic curves — check EVERY non-null sha value.
  C. THE REFINEMENT WITNESSED (g2c_curves): Poonen-Stoll — for genus-2
     Jacobians |Sha| can be twice a square; has_square_sha=false instances
     are the data-level witnesses that the obstruction theory REFINES with
     the category (the same lesson as P01, seen from the obstruction side).

Pre-stated readings (BEFORE run):
  A: OBSTRUCTION-PRESENT (cell (t,f) nonzero — expected; counts recorded per
     cell, nulls counted FIRST per the cardinality rule) / cell (f,t) MUST be
     empty (globally solvable implies locally solvable — any row there is an
     instrument or data fault, halt and inspect).
  B: ALL-SQUARE (every non-null EC sha is a perfect square; integer sqrt
     check, float-cast trap noted) / NON-SQUARE-FOUND (instrument-first:
     text/float casts, 0/null semantics, THEN a data-integrity event).
  C: NONSQUARE-PRESENT (has_square_sha=false count > 0 — Poonen-Stoll
     witnesses exist) with counts; all-square would be a surprising absence
     worth its own record, not a failure.
"""
from __future__ import annotations
import json
import math
import pathlib

import psycopg2

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p02_results.json"

conn = psycopg2.connect(host="localhost", port=5432, dbname="lmfdb", user="postgres")
cur = conn.cursor()
cur.execute("SET statement_timeout='300s'")
res = {}

# --- A: local-global census ---------------------------------------------------
cur.execute("""
  SELECT locally_solvable::text, globally_solvable::text, count(*)
  FROM public.g2c_curves GROUP BY 1, 2 ORDER BY 1, 2""")
# ENCODING TRAP (caught P80 first run): globally_solvable is an INTEGER
# (-1 unknown / 0 proven-no / 1 yes), not a boolean — the first draft keyed on
# 'True'/'False' strings and silently tallied obstructed=0 while the raw census
# printed 1051. Typed-value assumptions are verified by reading the raw census,
# never by the write succeeding (the P72 lesson, data-side).
cells = {}
obstructed = impossible = unknown = 0
for a, b, n in cur.fetchall():
    loc = a in ("True", "true", "t", "1")
    glo = int(float(b))
    cells[f"local={loc} global={glo}"] = int(n)
    if loc and glo == 0:
        obstructed += int(n)          # the paradigm's cell: local yes, global proven-no
    if (not loc) and glo == 1:
        impossible += int(n)          # logically impossible cell
    if loc and glo == -1:
        unknown += int(n)
print("A. local/global census:", cells, flush=True)
assert impossible == 0, f"HALT: {impossible} rows globally-but-not-locally solvable"
res["local_global_census"] = {"cells": cells, "obstructed_count": obstructed,
                              "undecided_count": unknown, "impossible_cell": impossible,
                              "encoding": "globally_solvable int: -1 unknown / 0 no / 1 yes"}

# --- B: EC Cassels square check ----------------------------------------------
cur.execute("""
  SELECT sha::text, count(*) FROM public.ec_curvedata
  WHERE sha IS NOT NULL GROUP BY 1""")
sha_counts = cur.fetchall()
n_vals = 0
non_square = []
for s, n in sha_counts:
    v = float(s)
    assert v == int(v), f"non-integer sha {s}"
    v = int(v)
    n_vals += int(n)
    if v > 0:
        r = math.isqrt(v)
        if r * r != v:
            non_square.append((v, int(n)))
print(f"B. EC sha: {n_vals:,} non-null values across {len(sha_counts)} distinct; "
      f"non-squares: {non_square if non_square else 'NONE'}", flush=True)
res["ec_cassels_square"] = {"n_nonnull": n_vals, "n_distinct": len(sha_counts),
                            "non_square_values": non_square,
                            "verdict": "ALL-SQUARE" if not non_square else "NON-SQUARE-FOUND"}

# --- C: genus-2 Poonen-Stoll witnesses ---------------------------------------
cur.execute("""
  SELECT has_square_sha::text, count(*) FROM public.g2c_curves GROUP BY 1""")
hs = {str(a): int(n) for a, n in cur.fetchall()}
print("C. g2c has_square_sha:", hs, flush=True)
# sample 5 witnesses with their analytic_sha for the artifact
cur.execute("""
  SELECT label, analytic_sha::text FROM public.g2c_curves
  WHERE NOT has_square_sha::boolean ORDER BY label LIMIT 5""")
witnesses = cur.fetchall()
print("   witnesses:", witnesses, flush=True)
res["g2c_poonen_stoll"] = {"distribution": hs, "sample_witnesses":
                           [{"label": l, "analytic_sha": s} for l, s in witnesses]}
conn.close()

OUT.write_text(json.dumps({
    "protocol": "three-leg obstruction census: g2c local/global 2x2 (impossible-cell assert), EC sha integer-sqrt check on all non-null values, g2c has_square_sha distribution with witnesses",
    "results": res}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
