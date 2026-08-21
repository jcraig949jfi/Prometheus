"""PARADIGM-P04 worked example — Spectral Analysis, executed.

The paradigm's move: study the spectrum of an associated operator instead of
the object. Executable instance: Montgomery-Odlyzko — the zeta zeros behave
like eigenvalues of a GUE random matrix. We compute the first 1,000 zeta
zeros (mpmath, anchored against the archive's stored 20), unfold by the local
density, and compare nearest-neighbor spacings to the Wigner GUE surmise.

Pre-stated readings (BEFORE run):
  GUE-CONSISTENT   KS statistic vs Wigner-GUE surmise < KS vs Poisson AND
                   KS vs Wigner < 0.08 at n=999 spacings (low zeros carry
                   known finite-height deviations; the bar is discrimination,
                   not perfection — both KS values reported raw).
  GUE-INCONSISTENT otherwise — instrument-first: unfolding density, zero
                   indexing, mpmath dps.
Anchor gate: first 20 computed zeros must match the archive row
(charon_duckdb.dirichlet_zeros conductor=1) to 1e-9 or halt.
"""
from __future__ import annotations
import json
import math
import pathlib

import mpmath as mp
import numpy as np
import psycopg2

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p04_results.json"
N = 1000
mp.mp.dps = 20

conn = psycopg2.connect(host="localhost", port=5432, dbname="prometheus_fire", user="postgres")
cur = conn.cursor()
cur.execute("SELECT zeros_vector FROM charon_duckdb.dirichlet_zeros WHERE conductor=1")
raw = cur.fetchone()[0]
archive = json.loads(raw) if isinstance(raw, str) else raw
conn.close()

zeros = np.array([float(mp.zetazero(k).imag) for k in range(1, N + 1)])
anchor_drift = max(abs(zeros[i] - archive[i]) for i in range(min(20, len(archive))))
assert anchor_drift < 1e-9, f"anchor gate FAILS: drift {anchor_drift}"
print(f"anchor gate: 20/20 archive zeros matched, max drift {anchor_drift:.2e}", flush=True)

# unfold via the Riemann counting function N(T) ~ (T/2pi)log(T/2pi) - T/2pi + 7/8.
# INSTRUMENT-FIRST CATCH (first run, exactly the pre-stated branch): using only
# the density term t*log(t/2pi)/(2pi) — i.e. dropping the -T/2pi term — gave
# mean spacing 1.2239 and KS 0.39 vs BOTH ensembles; the mean-spacing gate
# (should be ~1) localized the fault to the unfolding before any GUE reading.
tt = zeros / (2 * math.pi)
unfolded = tt * np.log(tt) - tt + 7.0 / 8.0
s = np.diff(unfolded)
print(f"spacings: n={len(s)} mean={s.mean():.4f} (unfolded mean should be ~1) "
      f"min={s.min():.4f} max={s.max():.4f}", flush=True)

def ks_stat(sample, cdf):
    x = np.sort(sample)
    n = len(x)
    emp_hi = np.arange(1, n + 1) / n
    emp_lo = np.arange(0, n) / n
    c = cdf(x)
    return float(max(np.max(np.abs(emp_hi - c)), np.max(np.abs(emp_lo - c))))

# SECOND INSTRUMENT-FIRST CATCH: the first comparator was 1-exp(-4x^2/pi) — a
# Rayleigh-type CDF, NOT the GUE surmise (it is not even the integral of the
# stated density). Derived properly: integrating P(s)=(32/pi^2)s^2 e^{-4s^2/pi}
# gives CDF(s) = erf(2s/sqrt(pi)) - (4s/pi) e^{-4s^2/pi}. The wrong comparator
# produced KS 0.24 against a CORRECTLY unfolded sample — a broken yardstick
# reads a straight rod as bent.
_erf = np.vectorize(math.erf)
wigner_cdf = lambda x: _erf(2.0 * x / math.sqrt(math.pi)) - (4.0 * x / math.pi) * np.exp(-4.0 * x * x / math.pi)
poisson_cdf = lambda x: 1.0 - np.exp(-x)
ks_w = ks_stat(s, wigner_cdf)
ks_p = ks_stat(s, poisson_cdf)
verdict = "GUE-CONSISTENT" if (ks_w < ks_p and ks_w < 0.08) else "GUE-INCONSISTENT"
print(f"KS vs Wigner-GUE: {ks_w:.4f}   KS vs Poisson: {ks_p:.4f}  -> {verdict}", flush=True)

hist, edges = np.histogram(s, bins=np.arange(0, 3.2, 0.2), density=True)
OUT.write_text(json.dumps({
    "protocol": "first 1000 zeta zeros (mpmath dps=20, 20-zero archive anchor gate), density unfolding, NN spacings vs Wigner GUE surmise and Poisson, KS discrimination",
    "n_zeros": N, "anchor_max_drift": anchor_drift,
    "mean_unfolded_spacing": float(s.mean()),
    "ks_wigner": ks_w, "ks_poisson": ks_p, "verdict": verdict,
    "spacing_hist_density": {"edges": [round(float(e), 2) for e in edges],
                             "density": [round(float(h), 4) for h in hist]}},
    indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
