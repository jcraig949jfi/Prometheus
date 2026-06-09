"""Graded-QD harness with a pluggable mutation operator — the "1 and 2 together"
build (Harmonia C, proposal `pivot/harmonia_C_higher_success_engine_2026-05-27.md`).

ARM 1 (LLM-mutation vs random, head to head) and ARM 2 (a real positive-test
domain) in one reusable apparatus:

  * Generic MAP-Elites core: (init, mutate, descriptor, fitness, behavior axes).
  * Domain = LABS (low-autocorrelation binary sequences): merit factor
    F = n^2 / (2E) — a DENSE continuous gradient (no cliff), O(n^2) mechanical
    check, cypari-free. PRIOR-LEAK CONTROL by HARDNESS: at moderate length n no
    optimal sequence is catalogued/memorizable, so an LLM improvement is search,
    not recitation. (Contrast: Salem deg-10 = the negative control, where optima
    ARE memorizable.)
  * Pluggable operator: `random` (bit-flips) vs `llm` (Claude Haiku proposes a
    bold structural mutation), with prior-leak / hallucination instrumentation.

The honest comparison: at EQUAL eval budget, does the LLM arm reach higher merit
factor / more niche coverage than random? And does it beat the random FRONTIER?
"""
from __future__ import annotations
import argparse, json, math, os, re, time
import numpy as np

# --------------------------- LABS domain -----------------------------------
def autocorr_energy(s):
    n = len(s); E = 0
    for k in range(1, n):
        c = int(np.dot(s[:n - k], s[k:]))
        E += c * c
    return E

def merit_factor(s):
    n = len(s); E = autocorr_energy(s)
    return (n * n) / (2.0 * E) if E > 0 else float("inf")

def peak_sidelobe(s):
    n = len(s)
    return max(abs(int(np.dot(s[:n - k], s[k:]))) for k in range(1, n)) / n

def skew_defect(s):
    n = len(s)
    if n % 2 == 0:
        return float("nan")
    m = (n - 1) // 2
    bad = tot = 0
    for i in range(1, m + 1):
        tot += 1
        if s[m + i] != ((-1) ** i) * s[m - i]:
            bad += 1
    return bad / tot if tot else 0.0

def run_entropy(s):
    runs, cur = [], 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            cur += 1
        else:
            runs.append(cur); cur = 1
    runs.append(cur)
    vals, cnts = np.unique(runs, return_counts=True)
    p = cnts / cnts.sum()
    return float(-np.sum(p * np.log(p)))

def labs_descriptor(s):
    return {
        "merit_factor": merit_factor(s),
        "skew_defect": skew_defect(s),
        "run_entropy": run_entropy(s),
        "balance": abs(int(s.sum())) / len(s),
        "peak_sidelobe": peak_sidelobe(s),
    }

LABS_AXES = ["merit_factor", "skew_defect", "run_entropy", "balance", "peak_sidelobe"]

# calibration anchor: Barker-13 merit factor ~ 14.08
BARKER13 = np.array([1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1])
_f = merit_factor(BARKER13)
assert 13.0 < _f < 15.0, f"LABS merit-factor instrument off-anchor (Barker-13): {_f}"

# ----------------------------- operators -----------------------------------
def random_seq(n, rng):
    return rng.choice(np.array([-1, 1]), size=n)

def random_mutate(s, rng):
    c = s.copy()
    for _ in range(int(rng.integers(1, 3))):
        c[int(rng.integers(len(c)))] *= -1
    return c

class LLMMutator:
    """Claude-Haiku mutation operator. Records validity / hallucination stats
    (the prior-leak instrumentation: at moderate n there is no memorizable
    answer, so improvements are search)."""
    def __init__(self, model="claude-haiku-4-5-20251001", temperature=1.0):
        import keys, anthropic
        self.c = anthropic.Anthropic(api_key=keys.get_key("CLAUDE"))
        self.model, self.temperature = model, temperature
        self.calls = self.valid = self.noop = self.malformed = 0

    def __call__(self, s, rng):
        n = len(s)
        parent = "".join("+" if v > 0 else "-" for v in s)
        F = merit_factor(s)
        prompt = (
            f"Mutate a +/- binary sequence to MAXIMIZE its merit factor "
            f"(F = n^2/(2E), E = sum of squared aperiodic autocorrelations; "
            f"higher F = lower sidelobes = better). Length n={n}. "
            f"Current sequence (F={F:.3f}): {parent}\n"
            f"Propose ONE new sequence of EXACTLY {n} characters, each '+' or '-', "
            f"with a HIGHER merit factor. Make a bold structural change. "
            f"Output ONLY the {n}-character +/- string, nothing else."
        )
        self.calls += 1
        try:
            r = self.c.messages.create(
                model=self.model, max_tokens=n + 64, temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}])
            txt = r.content[0].text
        except Exception:
            self.malformed += 1
            return random_mutate(s, rng)          # fall back; counts as malformed
        chars = re.findall(r"[+\-]", txt)
        if len(chars) != n:
            self.malformed += 1
            return random_mutate(s, rng)
        cand = np.array([1 if ch == "+" else -1 for ch in chars])
        self.valid += 1
        if np.array_equal(cand, s):
            self.noop += 1
        return cand

# --------------------------- MAP-Elites core -------------------------------
def map_elites(n, mutate, fitness, descriptor, axes, rng, n_evals,
               grid=(20, 20), warmup=200, init=None):
    bx, by = axes
    warm = []
    for _ in range(max(warmup, 50)):
        s = init(n, rng); warm.append([descriptor(s)[bx], descriptor(s)[by]])
    warm = np.array(warm)
    lo = np.nanmin(warm, axis=0); hi = np.nanmax(warm, axis=0)
    hi = np.where(hi > lo, hi, lo + 1.0)
    def cell(d):
        u = (np.array([d[bx], d[by]]) - lo) / (hi - lo)
        ix = np.clip((np.nan_to_num(u) * np.array(grid)).astype(int), 0, np.array(grid) - 1)
        return (int(ix[0]), int(ix[1]))
    archive, trace = {}, []
    def consider(s):
        d = descriptor(s); f = fitness(s); k = cell(d)
        if k not in archive or f > archive[k][0]:
            archive[k] = (f, s.copy(), d)
        return f
    best = -1e9
    for i in range(n_evals):
        if archive and rng.random() < 0.7:
            keys_ = list(archive.keys())
            parent = archive[keys_[int(rng.integers(len(keys_)))]][1]
            s = mutate(parent, rng)
        else:
            s = init(n, rng)
        f = consider(s)
        best = max(best, f)
        trace.append(best)
    fits = np.array([v[0] for v in archive.values()])
    elite = max(archive.values(), key=lambda v: v[0])
    return {
        "n_evals": n_evals, "cells_filled": len(archive),
        "total_cells": grid[0] * grid[1], "coverage": len(archive) / (grid[0] * grid[1]),
        "best_fitness": float(fits.max()), "median_fitness": float(np.median(fits)),
        "best_merit_factor": float(elite[2]["merit_factor"]),
        "best_seq": "".join("+" if v > 0 else "-" for v in elite[1]),
        "frontier_trace_tail": [round(x, 4) for x in trace[-1:]],
    }

# ------------------------------- driver ------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=37)
    ap.add_argument("--llm_budget", type=int, default=250)
    ap.add_argument("--frontier_budget", type=int, default=40000)
    ap.add_argument("--seed", type=int, default=20260529)
    a = ap.parse_args()
    n, B = a.n, a.llm_budget
    out = {"domain": "LABS", "n": n, "calibration": {"barker13_F": round(_f, 4)}}
    print(f"=== LABS positive-test domain, n={n} (Barker-13 anchor F={_f:.3f}) ===")

    # Phase 1: descriptor orthogonality audit
    rng = np.random.default_rng(a.seed)
    rows = [[labs_descriptor(random_seq(n, rng))[ax] for ax in LABS_AXES] for _ in range(8000)]
    X = np.array(rows); std = np.nanstd(X, axis=0)
    live = [i for i in range(len(LABS_AXES)) if std[i] > 1e-9]
    C = np.corrcoef(X[:, live], rowvar=False)
    names = [LABS_AXES[i] for i in live]
    print("Phase 1 — descriptor correlation (live axes):", names)
    print("        " + " ".join(f"{m[:9]:>10s}" for m in names))
    for i, m in enumerate(names):
        print(f"{m[:9]:>9s} " + " ".join(f"{C[i, j]:10.3f}" for j in range(len(names))))
    collin = [(names[i], names[j], round(C[i, j], 3))
              for i in range(len(names)) for j in range(i + 1, len(names)) if abs(C[i, j]) > 0.9]
    print("collinear pairs (|corr|>0.9):", collin or "none")
    out["phase1_corr"] = {"axes": names, "matrix": C.tolist(), "collinear": collin}

    AX = ("skew_defect", "run_entropy")   # structural behavior axes (decorrelated from F)
    common = dict(fitness=merit_factor, descriptor=labs_descriptor, axes=AX, init=random_seq)

    # Phase 2: random arm at EQUAL (LLM) budget
    print(f"\nPhase 2 — random arm @ equal budget ({B} evals)")
    r_eq = map_elites(n, random_mutate, rng=np.random.default_rng(a.seed + 1), n_evals=B, **common)
    print("   ", {k: r_eq[k] for k in ("coverage", "best_merit_factor", "best_fitness")})
    out["random_equal_budget"] = r_eq

    # Phase 3: random arm at FRONTIER budget
    print(f"\nPhase 3 — random arm @ frontier ({a.frontier_budget} evals)")
    r_fr = map_elites(n, random_mutate, rng=np.random.default_rng(a.seed + 2),
                      n_evals=a.frontier_budget, **common)
    print("   ", {k: r_fr[k] for k in ("coverage", "best_merit_factor", "best_fitness")})
    out["random_frontier"] = r_fr

    # Phase 4: LLM arm at equal budget
    print(f"\nPhase 4 — LLM (Haiku) arm @ {B} evals  [each eval = 1 API call]")
    t0 = time.time()
    llm = LLMMutator()
    r_llm = map_elites(n, llm, rng=np.random.default_rng(a.seed + 3), n_evals=B, **common)
    r_llm["llm_stats"] = {"calls": llm.calls, "valid": llm.valid, "noop": llm.noop,
                          "malformed": llm.malformed,
                          "valid_rate": round(llm.valid / max(llm.calls, 1), 3),
                          "wall_sec": round(time.time() - t0, 1)}
    print("   ", {k: r_llm[k] for k in ("coverage", "best_merit_factor", "best_fitness")})
    print("    llm_stats:", r_llm["llm_stats"])
    out["llm_equal_budget"] = r_llm

    # verdict (failure-shape, not verdict-line)
    print("\n=== HEAD-TO-HEAD (equal budget) ===")
    print(f"  best merit factor:  random={r_eq['best_merit_factor']:.3f}  "
          f"llm={r_llm['best_merit_factor']:.3f}  (random frontier={r_fr['best_merit_factor']:.3f})")
    print(f"  niche coverage:     random={r_eq['coverage']:.3f}  "
          f"llm={r_llm['coverage']:.3f}  (random frontier={r_fr['coverage']:.3f})")
    print("  PRIOR-LEAK NOTE: n is moderate -> no catalogued optimum to recite; "
          "any LLM merit-factor gain over random@equal-budget is search, not recall.")

    OUT = rf"D:\Prometheus\harmonia\tmp\_labs_qd_arms_n{n}.json"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {OUT}")

if __name__ == "__main__":
    main()
