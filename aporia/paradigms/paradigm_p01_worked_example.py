"""PARADIGM-P01 worked example — Algebraic Translation, executed.

The paradigm's move: reframe a problem in a richer algebraic category where
tools are sharper. The canonical executable instance in our data: MODULARITY.
The Diophantine side (point counts of an elliptic curve over F_p — brute
enumeration, no theory) and the automorphic side (Hecke eigenvalues of the
attached newform — fetched from mf_newforms.traces, an entirely independent
data pipeline) must agree: a_p = p + 1 - #E(F_p) = trace(T_p | f).

Curves: 11.a2 (rank 0, the classical 11a1) and 37.a1 (rank 1, first rank-1
conductor). Newforms: 11.2.a.a, 37.2.a.a.

Pre-stated readings (BEFORE run):
  TRANSLATION-EXACT   a_p matches traces[p] for EVERY good prime p <= 500,
                      both curves.
  MISMATCH            instrument-first, in order: (1) ainvs are FLOAT-typed
                      in the mirror ('[0.0,-1.0,...]') — cast to int and
                      verify exactness; (2) traces array is 1-indexed by n
                      (traces[0] = a_1); (3) bad primes (p | N) excluded —
                      a_p at bad primes follows different rules.
"""
from __future__ import annotations
import json
import pathlib
import sys

import psycopg2

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p01_results.json"
sys.path.insert(0, str(HERE.parent / "catalog_attacks"))
from nt_helpers import sieve_primes

PAIRS = [("11.a2", "11.2.a.a", 11), ("37.a1", "37.2.a.a", 37)]

conn = psycopg2.connect(host="localhost", port=5432, dbname="lmfdb", user="postgres")
cur = conn.cursor()
cur.execute("SET statement_timeout='120s'")

res = {}
for ec_label, mf_label, N in PAIRS:
    cur.execute("SELECT ainvs FROM public.ec_curvedata WHERE lmfdb_label=%s", (ec_label,))
    raw = cur.fetchone()[0]
    vals = json.loads(raw) if isinstance(raw, str) else raw
    a1, a2, a3, a4, a6 = (int(v) for v in vals)          # trap 1: float-typed ainvs
    assert all(float(int(v)) == float(v) for v in vals), f"non-integer ainvs {vals}"

    cur.execute("SELECT traces FROM public.mf_newforms WHERE label=%s", (mf_label,))
    raw = cur.fetchone()[0]
    traces = json.loads(raw) if isinstance(raw, str) else raw
    traces = [int(t) for t in traces]                     # trap 2: 1-indexed (traces[0]=a_1)

    rows = []
    mismatches = 0
    for p in (int(q) for q in sieve_primes(500)):
        if N % p == 0:
            continue                                      # trap 3: bad primes excluded
        count = 0                                         # Diophantine side: brute force
        for x in range(p):
            rhs_base = (x * x * x + a2 * x * x + a4 * x + a6) % p
            for y in range(p):
                if (y * y + a1 * x * y + a3 * y - rhs_base) % p == 0:
                    count += 1
        n_points = count + 1                              # affine points + point at infinity
        a_p_diophantine = p + 1 - n_points
        a_p_automorphic = traces[p - 1]                   # a_p = traces[p-1] (1-indexed by n)
        ok = a_p_diophantine == a_p_automorphic
        mismatches += 0 if ok else 1
        rows.append({"p": p, "a_p_pointcount": a_p_diophantine,
                     "a_p_newform": a_p_automorphic, "match": ok})
    n_good = len(rows)
    verdict = "TRANSLATION-EXACT" if mismatches == 0 else "MISMATCH"
    print(f"{ec_label} <-> {mf_label}: {n_good} good primes <=500, "
          f"mismatches={mismatches} -> {verdict}", flush=True)
    res[ec_label] = {"newform": mf_label, "conductor": N, "n_good_primes": n_good,
                     "mismatches": mismatches, "verdict": verdict, "rows": rows}

conn.close()
OUT.write_text(json.dumps({
    "protocol": "brute-force point counts over F_p (no theory on the Diophantine side) vs mf_newforms.traces (independent automorphic pipeline), good p <= 500",
    "results": res}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
