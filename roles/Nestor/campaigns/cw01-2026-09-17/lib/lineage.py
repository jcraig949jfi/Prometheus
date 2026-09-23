"""Lineage analysis and honest dispositions — extracted from e02's failures.

Four things live here, each earned by a specific defect:

  TestLog / decide       CW01-D024. e02's driver announced "gains occur but are
                         ADDITIVE: reverting the earlier gain costs no more than
                         that gain was worth" -- about a knockout that NEVER RAN.
                         A disposition branch must name the tests it rests on and
                         be UNREACHABLE unless those tests actually executed.

  detect_gains           CW01-D025. The original could not evaluate generations
                         before its baseline window, which is exactly where all
                         the improvement was (+203.2% within gens 0-9). Seeding
                         the baseline from the ANCESTOR makes early steps visible.

  emit_generations       CW01-D026. e02 emitted 6 rows against e01's 128; the
                         per-generation trajectories that ARE the evidence had to
                         be recovered by re-running evolution. Evidence that must
                         be regenerated to be inspected is not durable.

  fixation_order         The instrument that actually worked. Score-step detection
                         failed on e02's trajectory; measuring WHEN each gene moves
                         answered the ordering question directly. Reports the
                         neutral-drift floor alongside, per CW01-D027.
"""
from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------- dispositions

class TestLog:
    """Which tests ran, and what they found.

    The point is `ran` vs `passed`. A test that did not run cannot support ANY
    conclusion, in either direction -- that is the D024 failure.
    """

    def __init__(self):
        self._t = {}

    def record(self, name, ran, passed=None, detail="", value=None):
        self._t[name] = {"ran": bool(ran), "passed": passed, "detail": detail, "value": value}
        return self

    def ran(self, name):
        return self._t.get(name, {}).get("ran", False)

    def passed(self, name):
        return bool(self._t.get(name, {}).get("passed"))

    def missing(self, names):
        return [n for n in names if not self.ran(n)]

    def as_dict(self):
        return dict(self._t)


def decide(rules, log, fallback=("INCONCLUSIVE", "no rule was reachable")):
    """Evaluate ordered rules, skipping any whose required tests did not RUN.

    rules: list of (disposition, reason, required_test_names, predicate_callable)

    A rule whose required tests did not all run is SKIPPED and the skip is
    reported, rather than being silently treated as False -- which is how a
    never-executed knockout became a confident claim about additivity.
    """
    trace = []
    for disp, reason, required, pred in rules:
        miss = log.missing(required)
        if miss:
            trace.append({"disposition": disp, "skipped": True,
                          "because": f"required test(s) never ran: {miss}"})
            continue
        try:
            hit = bool(pred(log))
        except Exception as e:
            trace.append({"disposition": disp, "skipped": True,
                          "because": f"predicate raised {type(e).__name__}: {e}"})
            continue
        trace.append({"disposition": disp, "skipped": False, "matched": hit})
        if hit:
            return disp, reason, trace
    return fallback[0], fallback[1], trace


# ------------------------------------------------------------- gain detection

def detect_gains(history, effect_size_min_pct, persistence_generations,
                 baseline_window=5, min_sd_separation=3.0, ancestor_mean=None,
                 key="mean"):
    """A gain is a step up that STAYS up and clears the local noise floor.

    ancestor_mean seeds the baseline so generations 0..baseline_window-1 are
    evaluable. Without it the detector is blind precisely where a fast-converging
    population does all its work (CW01-D025).

    NOTE ON CALIBRATION: thresholds must be calibrated against planted steps at the
    START of a series, not only mid-series. e02's Q11 calibration used mid-series
    steps and therefore never exercised this blind spot.
    """
    means = [h[key] for h in history]
    if ancestor_mean is not None:
        means = [float(ancestor_mean)] * baseline_window + means
        shift = baseline_window
    else:
        shift = 0

    gains = []
    for g in range(baseline_window, len(means) - persistence_generations):
        before = means[max(0, g - baseline_window):g]
        after = means[g:g + persistence_generations]
        base = float(np.mean(before))
        if base <= 0:
            continue
        lift = 100.0 * (float(np.mean(after)) - base) / base
        pooled = float(np.std(list(before) + list(after), ddof=1))
        sep = (float(np.mean(after)) - base) / pooled if pooled > 0 else 0.0
        if lift >= effect_size_min_pct and min(after) > base and sep >= min_sd_separation:
            gen = g - shift
            if gains and gen - gains[-1]["gen"] < persistence_generations:
                continue
            gains.append({"gen": gen, "lift_pct": lift, "baseline": base,
                          "level": float(np.mean(after)), "sd_separation": sep})
    return gains


# ------------------------------------------------------------ fixation order

def fixation_generation(history, gene, frac=0.75, tail=5):
    """First generation at which a gene reaches `frac` of its start->end travel.

    Returns (generation | None, start, end). None means the gene did not travel.
    """
    v = np.array([h["gene_" + gene] for h in history], dtype=float)
    lo, hi = float(v[0]), float(v[-tail:].mean())
    if abs(hi - lo) < 1e-12:
        return None, lo, hi
    target = lo + frac * (hi - lo)
    idx = np.where(v >= target)[0] if hi > lo else np.where(v <= target)[0]
    return (int(idx[0]) if len(idx) else None), lo, hi


def neutral_drift_floor(history, neutral_genes, tail=5):
    """How far do genes with NO phenotype travel? That is the drift floor.

    e02: neutral_a travelled up to -0.399 under elite copying despite being verified
    inert. An ordering claim finer than this floor is not resolvable (CW01-D027).
    """
    travel = {}
    for g in neutral_genes:
        v = np.array([h["gene_" + g] for h in history], dtype=float)
        travel[g] = float(v[-tail:].mean() - v[0])
    return {"per_gene": travel,
            "max_abs": max((abs(t) for t in travel.values()), default=0.0)}


def fixation_order(history, gene_a, gene_b, neutral_genes=(), frac=0.75):
    """Does gene_a fix before gene_b? Reported WITH the drift floor, never without.

    This is the direct test of temporal ordering. In e02 it succeeded where
    score-step detection failed: p_factor fixed before p_norm in 6/6 runs across
    three selection strengths, which settled the disposition.
    """
    fa, a0, a1 = fixation_generation(history, gene_a, frac)
    fb, b0, b1 = fixation_generation(history, gene_b, frac)
    drift = neutral_drift_floor(history, neutral_genes) if neutral_genes else None

    if fa is None or fb is None:
        verdict = "indeterminate (a gene did not travel)"
    elif fa < fb:
        verdict = f"{gene_a} FIRST"
    elif fa > fb:
        verdict = f"{gene_b} FIRST"
    else:
        verdict = "SIMULTANEOUS"

    return {"gene_a": gene_a, "gene_b": gene_b, "fix_a": fa, "fix_b": fb,
            "separation": (None if (fa is None or fb is None) else abs(fa - fb)),
            "travel_a": a1 - a0, "travel_b": b1 - b0,
            "verdict": verdict, "neutral_drift": drift,
            "_caveat": "separation must exceed the drift timescale to be resolvable"}


# ------------------------------------------------------------ durable rows

def emit_generations(ctx, history, arm, replicate=None, status="record", extra=None):
    """Emit ONE ROW PER GENERATION. The trajectory is the evidence (CW01-D026)."""
    n = 0
    for rec in history:
        row = {"status": status, "kind": "generation", "arm": arm}
        if replicate is not None:
            row["replicate"] = replicate
        row.update({k: v for k, v in rec.items() if isinstance(v, (int, float, str, bool))})
        if extra:
            row.update(extra)
        ctx.emit(row)
        n += 1
    return n
