"""PARADIGM-P16 worked example — Modular / Arithmetic Statistics, executed.

The paradigm's move: lift mod-p local data to global conclusions via
distributions. Executable instance: SATO-TATE AT DATA SCALE with a detector
leg. For weight-2 newforms the normalized Frobenius traces a_p/(2*sqrt(p))
follow the semicircle law — IF the form is non-CM (Clozel-Harris-Taylor
class). CM forms VIOLATE it structurally (half the primes are supersingular:
a_p = 0). The instrument must both CONFIRM (non-CM) and DECLINE (CM) — the
tier's certificates-that-can-decline rule.

Comparator DERIVED (P82 rule): integrating the ST density (2/pi)sqrt(1-t^2)
gives F(x) = 1/2 + (x*sqrt(1-x^2) + asin(x))/pi; endpoint gates F(-1)=0,
F(1)=1 asserted before use.

Data: mf_newforms.traces (a_n, 1-indexed, n<=1000 -> 168 odd-good primes per
form), DISTINCT ON unnecessary for single-label fetches but bad primes (p|N)
excluded, and the Hasse gate |a_p| <= 2*sqrt(p) asserted on EVERY prime (a
violation is a data-integrity event, not statistics).

Pre-stated readings (BEFORE run):
  ST-DISCRIMINATES  non-CM forms (11.2.a.a, 37.2.a.a): KS vs semicircle <
                    KS vs uniform[-1,1] AND < 0.15 at n~167; CM forms
                    (32.2.a.a, 27.2.a.a): zero-fraction > 0.4 AND KS vs
                    semicircle > 0.2 (the detector DECLINES).
  ST-CONFUSED       any leg fails — instrument-first: normalization 2*sqrt(p),
                    1-indexed traces, bad-prime exclusion, Hasse gate.
"""
from __future__ import annotations
import json
import math
import pathlib
import sys

import numpy as np
import psycopg2

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p16_results.json"
sys.path.insert(0, str(HERE.parent / "catalog_attacks"))
from nt_helpers import sieve_primes

# --- derived comparator with endpoint gates ----------------------------------
def st_cdf(x):
    x = np.clip(x, -1.0, 1.0)
    return 0.5 + (x * np.sqrt(1 - x * x) + np.arcsin(x)) / math.pi

assert abs(st_cdf(np.array([-1.0]))[0]) < 1e-12 and abs(st_cdf(np.array([1.0]))[0] - 1) < 1e-12, \
    "comparator endpoint gate FAILS"
uni_cdf = lambda x: (np.clip(x, -1, 1) + 1) / 2.0

def ks_stat(sample, cdf):
    x = np.sort(sample)
    n = len(x)
    c = cdf(x)
    return float(max(np.max(np.abs(np.arange(1, n + 1) / n - c)),
                     np.max(np.abs(np.arange(0, n) / n - c))))

conn = psycopg2.connect(host="localhost", port=5432, dbname="lmfdb", user="postgres")
cur = conn.cursor()
cur.execute("SET statement_timeout='120s'")
primes = [int(p) for p in sieve_primes(1000)]

FORMS = [("11.2.a.a", 11, "non-CM"), ("37.2.a.a", 37, "non-CM"),
         ("32.2.a.a", 32, "CM"), ("27.2.a.a", 27, "CM")]
res = []
all_ok = True
for label, N, kind in FORMS:
    cur.execute("SELECT traces, is_cm::text FROM public.mf_newforms WHERE label=%s", (label,))
    raw, is_cm = cur.fetchone()
    traces = json.loads(raw) if isinstance(raw, str) else raw
    xs = []
    zero_ct = 0
    for p in primes:
        if N % p == 0:
            continue
        a_p = int(traces[p - 1])
        assert a_p * a_p <= 4 * p, f"HASSE VIOLATION at {label}, p={p}: a_p={a_p}"
        xs.append(a_p / (2 * math.sqrt(p)))
        zero_ct += (a_p == 0)
    xs = np.array(xs)
    ks_st = ks_stat(xs, st_cdf)
    ks_un = ks_stat(xs, uni_cdf)
    zf = zero_ct / len(xs)
    if kind == "non-CM":
        ok = ks_st < ks_un and ks_st < 0.15
    else:
        ok = zf > 0.4 and ks_st > 0.2
    all_ok &= ok
    print(f"{label} ({kind}, mirror is_cm={is_cm}): n={len(xs)} zero-frac={zf:.3f} "
          f"KS_semicircle={ks_st:.4f} KS_uniform={ks_un:.4f} -> "
          f"{'CONFIRMS' if kind == 'non-CM' and ok else 'DECLINES (correct)' if ok else 'FAIL'}",
          flush=True)
    res.append({"label": label, "kind": kind, "mirror_is_cm": is_cm, "n_primes": len(xs),
                "zero_fraction": round(zf, 4), "ks_semicircle": round(ks_st, 4),
                "ks_uniform": round(ks_un, 4), "ok": bool(ok)})
conn.close()

verdict = "ST-DISCRIMINATES" if all_ok else "ST-CONFUSED"
print(f"-> {verdict}", flush=True)
OUT.write_text(json.dumps({
    "protocol": "normalized Frobenius traces a_p/(2 sqrt p) from mf_newforms.traces (p<=1000, bad primes excluded, Hasse gate per prime) vs DERIVED semicircle CDF with endpoint gates; two non-CM confirm, two CM decline",
    "results": res, "verdict": verdict}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
