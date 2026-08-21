"""PARADIGM-P03 worked example — Symmetry Exploitation, executed.

The paradigm's move: use group actions / involutions to collapse the search
space. Executable instance: the Fricke involution W_N on weight-2 trivial-
character newforms fixes the functional-equation sign, which LOCKS the parity
of the analytic rank — a symmetry consequence that halves the rank search
space before any L-value is computed.

Convention discipline (assume-wrong): the orientation (which Fricke sign forces
which parity) is DERIVED from the contingency table, not asserted from memory.
The claim under test is that the table is PERFECTLY DIAGONAL — a deterministic
one-to-one lock — whichever orientation the data shows.

Pre-stated readings (BEFORE run):
  PARITY-LOCKED      zero off-diagonal cells in the (fricke, rank mod 2)
                     contingency table over all qualifying rows; orientation
                     reported as derived.
  PARITY-VIOLATIONS  any off-diagonal count > 0 — instrument-first, in order:
                     (1) weight or character filter leak, (2) fricke null
                     semantics, (3) analytic_rank text-cast fault; only after
                     those pass is a violation a data-integrity event.
Cardinality FIRST: the qualifying subset (non-null fricke AND rank) is counted
against the full weight-2 trivial-character population; nullity is reported,
not hidden.
"""
from __future__ import annotations
import json
import pathlib

import psycopg2

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p03_results.json"

conn = psycopg2.connect(host="localhost", port=5432, dbname="lmfdb", user="postgres")
cur = conn.cursor()
cur.execute("SET statement_timeout='300s'")

cur.execute("SELECT count(*) FROM public.mf_newforms WHERE weight::int=2 AND char_order::int=1")
population = cur.fetchone()[0]
cur.execute("""
  SELECT fricke_eigenval::text, mod(analytic_rank::int, 2), count(*)
  FROM public.mf_newforms
  WHERE weight::int=2 AND char_order::int=1
        AND fricke_eigenval IS NOT NULL AND analytic_rank IS NOT NULL
  GROUP BY 1, 2 ORDER BY 1, 2""")
cells = [(w, int(p), int(n)) for w, p, n in cur.fetchall()]
print("raw contingency (fricke, parity, count):", cells, flush=True)
qualifying = sum(n for _, _, n in cells)

# derive the orientation from the dominant cell per fricke sign
by_sign = {}
for w, p, n in cells:
    by_sign.setdefault(w, {})[p] = n
orientation = {w: max(d, key=d.get) for w, d in by_sign.items()}
off_diagonal = sum(n for w, p, n in cells if p != orientation[w])
verdict = "PARITY-LOCKED" if off_diagonal == 0 else "PARITY-VIOLATIONS"
print(f"population={population:,} qualifying={qualifying:,} "
      f"orientation={orientation} off_diagonal={off_diagonal} -> {verdict}", flush=True)

# max rank per sign — the symmetry also bounds what ranks OCCUR per class
cur.execute("""
  SELECT fricke_eigenval::text, analytic_rank::int, count(*)
  FROM public.mf_newforms
  WHERE weight::int=2 AND char_order::int=1
        AND fricke_eigenval IS NOT NULL AND analytic_rank IS NOT NULL
  GROUP BY 1, 2 ORDER BY 1, 2""")
rank_dist = [(w, int(r), int(n)) for w, r, n in cur.fetchall()]
print("rank distribution per sign:", rank_dist, flush=True)
conn.close()

OUT.write_text(json.dumps({
    "protocol": "contingency of (fricke_eigenval, analytic_rank mod 2) over weight-2 trivial-character newforms; orientation DERIVED not asserted; nullity reported",
    "population_weight2_trivchar": int(population),
    "qualifying_nonnull": int(qualifying),
    "cells": cells, "derived_orientation": orientation,
    "off_diagonal": int(off_diagonal), "verdict": verdict,
    "rank_distribution_per_sign": rank_dist}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
