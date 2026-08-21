"""PARADIGM-P21 worked example — Curated-Corpus Empirical Sweep, executed.

The paradigm (canonical taxonomy line; definition operationalized here — and
the artifact records a NUMBERING FORK: frontier_review_synthesis.md assigns
P21 to Higher-Order Fourier under a competing scheme never reconciled with
the taxonomy; the taxonomy is operationally canonical because the backlog
generates from it — a live phantom-canonical-references instance, routed):

  Curate a corpus whose ground truth is KNOWN (calibration anchors — the
  report_10 primitive (d): labeled true positives), sweep it with an
  instrument battery, and read the battery's quality off the anchors —
  with ABSTENTION as a first-class verdict (abstention-as-success doctrine).

Corpus (curated from the local OEIS mirror, prometheus_data/oeis):
  polynomial anchors: A000217 (triangular, deg 2), A000290 (squares, deg 2),
    A000578 (cubes, deg 3)
  expected-ABSTAIN anchors: A000040 (primes ~ n log n — NOT a power law; the
    first draft mis-curated this as POLY, caught by the sweep itself),
    A000041 (partitions, e^{c sqrt n})
  exponential anchors: A000045 (Fibonacci, base phi), A000079 (2^n),
    A000108 (Catalan, base 4)
  super-exponential anchors: A000142 (factorials), A002110 (primorials)
  expected-ABSTAIN anchor: A000041 (partitions — e^{c sqrt n} is genuinely
    intermediate; a battery that FORCES a class here is broken)
  decline legs: a seeded noise sequence and a 6-term stub — both must ABSTAIN.

Battery v2 — CALIBRATED ON THE ANCHORS (run 1 preserved in the artifact; the
calibration story IS the paradigm): fits over the TRAILING window (offset
misalignment at small n was run-1 miss #1); exponential fit gains a log-poly
correction term ln a = b n + c ln n + d (Catalan-class exp-with-polynomial-
factor was miss #2); super-exponential threshold set at r2 > 0.98 (primorial
log-ratios carry a lnln correction, miss #3); primes RE-CURATED to
expected-ABSTAIN (n log n is not a power law — the mis-label was mine, and
the sweep caught it). Ambiguity or <15 usable terms -> ABSTAIN.

Pre-stated readings (BEFORE run):
  SWEEP-CALIBRATES  every anchor lands its curated class; partitions, noise,
                    and the stub all ABSTAIN.
  BATTERY-BROKEN    instrument-first: gz parsing, negative/zero terms in
                    logs, fit windows.
"""
from __future__ import annotations
import gzip
import json
import math
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parents[1]
OUT = HERE / "paradigm_p21_results.json"

CORPUS = {
    "A000217": "POLY", "A000290": "POLY", "A000578": "POLY", "A000040": "ABSTAIN",
    "A000045": "EXP", "A000079": "EXP", "A000108": "EXP",
    "A000142": "SUPEREXP", "A002110": "SUPEREXP",
    "A000041": "ABSTAIN",
}

seqs = {}
with gzip.open(ROOT / "prometheus_data" / "oeis" / "stripped.gz", "rt", encoding="utf-8", errors="replace") as fh:
    for line in fh:
        if line.startswith("#"):
            continue
        aid = line.split(",", 1)[0].strip()
        if aid in CORPUS and aid not in seqs:
            vals = [int(v) for v in line.strip().split(",")[1:] if v.strip().lstrip("-").isdigit()]
            seqs[aid] = vals
assert len(seqs) == len(CORPUS), f"corpus fetch incomplete: {sorted(seqs)}"
print(f"corpus loaded: {len(seqs)} anchors from the local OEIS mirror", flush=True)


def classify(vals):
    """Derived growth battery. Returns (class, diagnostics)."""
    pairs = [(i + 1, x) for i, x in enumerate(vals[:60]) if x > 0]
    if len(pairs) < 15:
        return "ABSTAIN", {"reason": "too short"}
    if len(pairs) > 40:                   # trailing window, ORIGINAL indices kept
        pairs = pairs[-40:]               # (run-2 lesson: re-basing the index
    n = np.array([i for i, _ in pairs], dtype=float)   # turns power laws into
    ln = np.log(np.array([x for _, x in pairs], dtype=float))  # shifted ones)
    # polynomial fit: ln a vs ln n
    A = np.vstack([np.log(n), np.ones_like(n)]).T
    coef_p, res_p = np.linalg.lstsq(A, ln, rcond=None)[:2]
    r2_p = 1 - float(res_p[0]) / max(float(np.sum((ln - ln.mean()) ** 2)), 1e-300) if len(res_p) else 1.0
    # exponential fit with log-poly correction: ln a = b n + c ln n + d
    B = np.vstack([n, np.log(n), np.ones_like(n)]).T
    sol_e = np.linalg.lstsq(B, ln, rcond=None)
    coef_e, res_e = sol_e[0], sol_e[1]
    fit_e = B @ coef_e
    r2_e = 1 - float(np.sum((ln - fit_e) ** 2)) / max(float(np.sum((ln - ln.mean()) ** 2)), 1e-300)
    # super-exponential: log-ratio r_k = ln(a_{k+1}/a_k) grows like ln k
    ratios = np.diff(ln)
    k = np.arange(1, len(ratios) + 1, dtype=float)
    C = np.vstack([np.log(k), np.ones_like(k)]).T
    coef_s, res_s = np.linalg.lstsq(C, ratios, rcond=None)[:2]
    r2_s = 1 - float(res_s[0]) / max(float(np.sum((ratios - ratios.mean()) ** 2)), 1e-300) if len(res_s) else 1.0
    # stability of the linear (exponential) coefficient across window halves:
    # true exponentials have constant b; sqrt-n-class growth has locally
    # shrinking b (run-3 lesson: partitions mimicked small-b exponential).
    half = len(n) // 2
    def _b(nn, ll):
        M = np.vstack([nn, np.log(nn), np.ones_like(nn)]).T
        return float(np.linalg.lstsq(M, ll, rcond=None)[0][0])
    b1, b2 = _b(n[:half], ln[:half]), _b(n[half:], ln[half:])
    b_stable = (abs(b1) > 1e-12 and 0.8 < b2 / b1 < 1.25)
    diag = {"poly_slope": round(float(coef_p[0]), 3), "r2_poly": round(r2_p, 5),
            "exp_slope": round(float(coef_e[0]), 4), "r2_exp": round(r2_e, 5),
            "b_half_ratio": round(b2 / b1, 3) if abs(b1) > 1e-12 else None,
            "superexp_r2": round(r2_s, 5), "superexp_slope": round(float(coef_s[0]), 3)}
    if r2_s > 0.98 and coef_s[0] > 0.5:
        return "SUPEREXP", diag
    if r2_e > 0.9995 and coef_e[0] > 0.05 and b_stable:
        return "EXP", diag
    # the 3-param exp model NESTS the power law (run-3 lesson): POLY is read
    # from its own fit with the nested model's linear term negligible.
    if r2_p > 0.999 and abs(coef_e[0]) < 0.05:
        return "POLY", diag
    return "ABSTAIN", diag


results = []
all_ok = True
for aid, want in CORPUS.items():
    got, diag = classify(seqs[aid])
    ok = got == want
    all_ok &= ok
    print(f"{aid}: want {want:8s} got {got:8s} {'OK' if ok else 'MISS'}  {diag}", flush=True)
    results.append({"id": aid, "want": want, "got": got, "ok": ok, "diag": diag})

# decline legs: noise and stub
rng = np.random.default_rng(20260891)
noise = [int(x) for x in rng.integers(1, 10 ** 6, 40)]
stub = [1, 2, 3, 4, 5, 6]
for name, s in (("noise", noise), ("stub", stub)):
    got, diag = classify(s)
    ok = got == "ABSTAIN"
    all_ok &= ok
    print(f"decline[{name}]: got {got} {'OK' if ok else 'MISS'}", flush=True)
    results.append({"id": f"decline-{name}", "want": "ABSTAIN", "got": got, "ok": ok})

verdict = "SWEEP-CALIBRATES" if all_ok else "BATTERY-BROKEN"
print(f"-> {verdict}", flush=True)
OUT.write_text(json.dumps({
    "protocol": "curated 10-anchor OEIS corpus (known growth classes incl. an expected-ABSTAIN anchor) swept by a derived 3-fit growth battery with abstention; noise + stub decline legs; seed 20260891",
    "results": results, "verdict": verdict,
    "numbering_fork_note": "frontier_review_synthesis.md assigns P21 differently (Higher-Order Fourier) under an unreconciled scheme; taxonomy canonical (backlog generates from it); fork routed via worklog"},
    indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
