"""Analysis path for the Metabolization Probe — prereg §6.

Everything here is preregistered and must exist, tested, BEFORE the first real call:

  primary endpoint  paired task-level F-prom-retrieved - F-null on the pooled manifest,
                    unit = TASK (never task x solver: solvers on one task are correlated,
                    and counting them separately is pseudo-replication), tested by a
                    two-sided paired bootstrap, 10,000 resamples, seed 0.
  secondary         per-solver McNemar exact; per-D-stratum profiles; the §2 decomposition;
                    harm_rate. All labeled exploratory, BH-FDR within family.
  guards            parse-failure spread >10pp across arms  -> INADMISSIBLE-FORMAT-CONFOUNDED
                    timeout spread       > 2pp across arms  -> flagged
  verdict           §6.3 classes, including INCONCLUSIVE-UNDERPOWERED, which is NOT a row of
                    the diagnostic matrix and can never route to Path gamma.
"""
from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Optional

import numpy as np

from .schema import ProbeRecord, assert_no_synthetic, INSTRUMENTATION_ONLY

# Preregistered constants (prereg §6.2, §6.3) — changing these after data exists is an amendment.
BOOTSTRAP_N = 10_000
BOOTSTRAP_SEED = 0
ALPHA = 0.05
TARGET_EFFECT = 0.08        # delta*, the design is powered for this
MIN_PRACTICAL_EFFECT = 0.05  # MPE: below this a result is detectable but strategically inert
PARSE_FAIL_SPREAD_LIMIT = 0.10
TIMEOUT_SPREAD_LIMIT = 0.02
MIN_STRATUM_RECORDS = 40     # below this a stratum is NOT-RUN-FOR-LACK-OF-RESIDUE

# Spec §4.6 states the standard by example: "a substrate that fixes 8 and breaks 7 is not
# navigation" — a harm/gain ratio of 0.875. Calibrated here to 0.75, which fails that example
# with margin while still admitting a genuine effect carrying ordinary per-item noise. (My
# first draft used 0.5 and rejected a cleanly-planted +12pp effect as merely WEAK; caught by
# the acceptance suite, which is the entire reason it exists.)
HARM_GAIN_RATIO_LIMIT = 0.75

# --- §6.3 as amended by the co-sign round (Charon §3, Harmonia B §1.1), 2026-08-16 ----------
# These are the binding classes. Code that disagrees with the binding document is a defect in
# the code, so they are implemented here rather than described.
#
#   CARRY-STRONG           Δ ≥ +8pp, CI LB > 0, harm/gain within limit
#   CARRY-STRONG-BUT-HARMFUL  Δ ≥ +8pp, CI LB > 0, harm condition FAILS   [Charon 3.1]
#                          -> routes to the negative-transfer row; never quotable as carry
#                             without harm_rate in the same sentence; does not license Path α
#   CARRY-WEAK             CI LB > 0 and +5pp ≤ Δ < +8pp                  [Charon 3.2]
#   DETECTABLE-BUT-INERT   CI LB > 0 and Δ < +5pp                         [Charon 3.2]
#                          -> NOT a matrix row; routes to no program direction
#   BOUNDED-NULL           CI LB ≤ 0 and CI UB < +5pp
#   INCONCLUSIVE-UNDERPOWERED  CI LB ≤ 0 and CI UB ≥ +5pp -> not a matrix row
#
# Charon 3.3: verdict classes apply to the POOLED PRIMARY ENDPOINT ONLY. Strata, decomposition
# quantities, and per-source breakdowns carry point estimates with intervals and never a class
# label — reading a 0.40-power stratum as "bounded null" is the inference his own doctrine
# forbids. Enforced by `classify_pooled_only`, not by convention.
NON_ROUTING_CLASSES = ("DETECTABLE-BUT-INERT", "INCONCLUSIVE-UNDERPOWERED", "NOT-RUN")

# Harmonia B §1.1 (BC-8): matrix ROW SELECTION gets the same underpowered escape the verdict
# classes have. Rows 2 and 3 ("recorded residue lacks usable information" -> provenance
# engineering) vs ("retrieval failure, residue vindicated" -> build the retriever) are
# different quarters of work; a CI that spans both readings chooses neither.
UNROUTED = "UNROUTED-UNDERPOWERED"


@dataclass
class ArmDiagnostics:
    arm: str
    n: int
    parse_fail_rate: float
    timeout_rate: float
    accuracy: float


@dataclass
class Comparison:
    label: str
    n_tasks: int
    delta: float
    ci_lo: float
    ci_hi: float
    p_value: float
    exploratory: bool = False


@dataclass
class AnalysisResult:
    admissible: bool
    admissibility_notes: list[str] = field(default_factory=list)
    diagnostics: list[ArmDiagnostics] = field(default_factory=list)
    primary: Optional[Comparison] = None
    per_solver_mcnemar: dict[str, float] = field(default_factory=dict)
    strata: list[Comparison] = field(default_factory=list)
    decomposition: dict[str, float] = field(default_factory=dict)
    harm_rate: float = float("nan")
    gain_rate: float = float("nan")
    verdict: str = "NOT-RUN"
    verdict_reason: str = ""


# --------------------------------------------------------------------------------------
# shaping
# --------------------------------------------------------------------------------------

def _by_task_arm_solver(records: Iterable[ProbeRecord]) -> dict:
    """(task, arm, solver) -> success in {0,1}. Unparseable/failed = 0 (prereg §1)."""
    out: dict[tuple[str, str, str], int] = {}
    for r in records:
        out[(r.task_uid, r.arm, r.solver)] = int(r.scored)
    return out


def _task_level_series(cube: dict, arm: str, tasks: list[str], solvers: list[str]) -> np.ndarray:
    """Per-task mean success across solvers — the preregistered unit of analysis."""
    vals = []
    for t in tasks:
        per_solver = [cube.get((t, arm, s)) for s in solvers]
        present = [v for v in per_solver if v is not None]
        vals.append(float(np.mean(present)) if present else np.nan)
    return np.asarray(vals, dtype=float)


def paired_bootstrap(delta: np.ndarray, n_boot: int = BOOTSTRAP_N,
                     seed: int = BOOTSTRAP_SEED) -> tuple[float, float, float, float]:
    """Two-sided paired bootstrap. Returns (mean, ci_lo, ci_hi, p)."""
    d = delta[~np.isnan(delta)]
    if d.size == 0:
        return float("nan"), float("nan"), float("nan"), float("nan")
    rng = np.random.RandomState(seed)
    idx = rng.randint(0, d.size, (n_boot, d.size))
    means = d[idx].mean(axis=1)
    obs = float(d.mean())
    lo, hi = np.percentile(means, [100 * ALPHA / 2, 100 * (1 - ALPHA / 2)])
    # two-sided p: proportion of resamples on the far side of zero, doubled
    p = 2.0 * min((means <= 0).mean(), (means >= 0).mean())
    return obs, float(lo), float(hi), float(min(1.0, p))


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar on discordant pairs (binomial, no scipy)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return float(min(1.0, 2 * tail))


def benjamini_hochberg(pvals: list[float], q: float = 0.05) -> list[bool]:
    """Returns per-test rejection flags at FDR q."""
    m = len(pvals)
    if m == 0:
        return []
    order = np.argsort(pvals)
    thresh = [(i + 1) / m * q for i in range(m)]
    sorted_p = [pvals[i] for i in order]
    keep = [p <= t for p, t in zip(sorted_p, thresh)]
    cut = max([i for i, k in enumerate(keep) if k], default=-1)
    out = [False] * m
    for rank, i in enumerate(order):
        if rank <= cut:
            out[i] = True
    return out


# --------------------------------------------------------------------------------------
# guards
# --------------------------------------------------------------------------------------

def arm_diagnostics(records: list[ProbeRecord]) -> list[ArmDiagnostics]:
    by_arm: dict[str, list[ProbeRecord]] = defaultdict(list)
    for r in records:
        by_arm[r.arm].append(r)
    out = []
    for arm, rs in sorted(by_arm.items()):
        n = len(rs)
        pf = sum(1 for r in rs if r.parsed_verdict is None) / n
        to = sum(1 for r in rs if r.status == "timeout") / n
        acc = sum(1 for r in rs if r.scored) / n
        out.append(ArmDiagnostics(arm, n, pf, to, acc))
    return out


def check_admissibility(diags: list[ArmDiagnostics]) -> tuple[bool, list[str]]:
    """Prereg §1 format-confound guard + the soak-derived timeout guard."""
    notes: list[str] = []
    ok = True
    comparable = [d for d in diags if d.arm not in INSTRUMENTATION_ONLY]
    if len(comparable) < 2:
        return True, ["fewer than two comparable arms — guards not applicable"]

    pf = [d.parse_fail_rate for d in comparable]
    spread = max(pf) - min(pf)
    if spread > PARSE_FAIL_SPREAD_LIMIT:
        ok = False
        hi = max(comparable, key=lambda d: d.parse_fail_rate)
        lo = min(comparable, key=lambda d: d.parse_fail_rate)
        notes.append(
            f"INADMISSIBLE-FORMAT-CONFOUNDED: parse-failure spread {spread:.1%} exceeds "
            f"{PARSE_FAIL_SPREAD_LIMIT:.0%} ({hi.arm} {hi.parse_fail_rate:.1%} vs "
            f"{lo.arm} {lo.parse_fail_rate:.1%})"
        )

    to = [d.timeout_rate for d in comparable]
    to_spread = max(to) - min(to)
    if to_spread > TIMEOUT_SPREAD_LIMIT:
        notes.append(
            f"FLAG: timeout spread {to_spread:.1%} exceeds {TIMEOUT_SPREAD_LIMIT:.0%} — "
            "long-latency calls track longer packets, so this risks arm-correlated missing data"
        )
    return ok, notes


# --------------------------------------------------------------------------------------
# verdict
# --------------------------------------------------------------------------------------

def classify(delta: float, ci_lo: float, ci_hi: float,
             harm_rate: float, gain_rate: float) -> tuple[str, str]:
    """Prereg §6.3. INCONCLUSIVE-UNDERPOWERED is not a matrix row and never routes to Path gamma."""
    if math.isnan(delta):
        return "NOT-RUN", "no data"
    if ci_lo > 0:
        # Charon 3.4: the ratio is degenerate at gain_rate == 0. Report raw counts and treat
        # it as undefined rather than as satisfied or failed. (Cannot co-occur with STRONG:
        # Δ ≥ +8pp forces gain > 0.)
        ratio_defined = not (math.isnan(harm_rate) or math.isnan(gain_rate) or gain_rate == 0)
        churn_ok = (not ratio_defined) or harm_rate <= HARM_GAIN_RATIO_LIMIT * gain_rate
        ratio_txt = (f"harm {harm_rate:.1%} vs gain {gain_rate:.1%} "
                     f"(ratio {harm_rate / gain_rate:.2f})" if ratio_defined
                     else f"harm {harm_rate:.1%}, gain {gain_rate:.1%} — ratio UNDEFINED")

        if delta >= TARGET_EFFECT:
            if churn_ok:
                return "CARRY-STRONG", (
                    f"delta {delta:+.1%} >= {TARGET_EFFECT:.0%}, CI lower bound {ci_lo:+.1%} > 0, "
                    f"{ratio_txt} within the {HARM_GAIN_RATIO_LIMIT} limit")
            # [Charon 3.1] the gap: strong Δ with failing harm previously matched no class.
            return "CARRY-STRONG-BUT-HARMFUL", (
                f"delta {delta:+.1%} clears {TARGET_EFFECT:.0%} with CI lower bound "
                f"{ci_lo:+.1%} > 0, BUT churn fails: {ratio_txt} > {HARM_GAIN_RATIO_LIMIT}. "
                "Routes to the negative-transfer row. Never quotable as carry without "
                "harm_rate in the same sentence; does not license Path alpha.")
        if delta >= MIN_PRACTICAL_EFFECT:
            return "CARRY-WEAK", (
                f"CI lower bound {ci_lo:+.1%} > 0 and delta {delta:+.1%} sits in "
                f"[{MIN_PRACTICAL_EFFECT:.0%}, {TARGET_EFFECT:.0%}) — real but below the "
                f"strong threshold; {ratio_txt}")
        # [Charon 3.2] statistically present, practically absent. Routes nowhere.
        return "DETECTABLE-BUT-INERT", (
            f"CI lower bound {ci_lo:+.1%} > 0 but delta {delta:+.1%} is below the "
            f"{MIN_PRACTICAL_EFFECT:.0%} practical floor. NOT a diagnostic-matrix row and "
            "routes to no program direction — statistically present, strategically inert.")
    if ci_hi < MIN_PRACTICAL_EFFECT:
        return "BOUNDED-NULL", (
            f"CI [{ci_lo:+.1%}, {ci_hi:+.1%}] excludes a practically meaningful effect. "
            "Bounded to the tested models, tasks, packetization and context budgets — "
            "never 'at any capacity'.")
    return "INCONCLUSIVE-UNDERPOWERED", (
        f"CI [{ci_lo:+.1%}, {ci_hi:+.1%}] spans zero AND reaches the "
        f"{MIN_PRACTICAL_EFFECT:.0%} practical floor. Not a diagnostic-matrix row; "
        "routes to replenish-and-rerun.")


def classify_pooled_only(comparison: "Comparison", harm_rate: float,
                         gain_rate: float) -> tuple[str, str]:
    """[Charon 3.3] Verdict classes attach to the POOLED PRIMARY ENDPOINT and nothing else.

    Raises on any attempt to label a stratum, a decomposition quantity, or a per-source
    breakdown. Enforced mechanically because "D3: bounded null" from a 0.40-power stratum is
    exactly the evidence-of-absence inference the kill authority's own doctrine forbids.
    """
    if comparison.exploratory:
        raise ValueError(
            f"refusing to attach a verdict class to an exploratory comparison "
            f"({comparison.label!r}); §6.3 classes are pooled-primary-endpoint only")
    return classify(comparison.delta, comparison.ci_lo, comparison.ci_hi, harm_rate, gain_rate)


def route_matrix_row(whole_minus_null: Optional["Comparison"],
                     retrieved_minus_null: Optional["Comparison"],
                     *, exploratory_only: bool) -> tuple[str, str]:
    """[BC-8 / Harmonia B §1.1] Row 2 vs row 3 selection, with an underpowered escape.

    Row 2 = recorded residue lacks usable information -> provenance engineering.
    Row 3 = information exists, retrieval failed -> build the retriever (M2).
    The discriminator is `F-prom-whole - F-null`. If its CI spans both readings — or if the
    decomposition is flagged EXPLORATORY-ONLY — no row is chosen and the next-move column of
    the verdict document stays empty.
    """
    if exploratory_only:
        return UNROUTED, ("whole-vs-retrieved decomposition is EXPLORATORY-ONLY (BC-1); "
                          "it may not route matrix rows 2/3 regardless of its point estimate")
    if whole_minus_null is None or math.isnan(whole_minus_null.delta):
        return UNROUTED, "F-prom-whole did not run; rows 2/3 are not separable"
    w = whole_minus_null
    if w.ci_lo > 0 and (retrieved_minus_null is not None and retrieved_minus_null.ci_lo <= 0):
        return "ROW-3-RETRIEVAL-FAILURE", (
            f"whole beats null ({w.delta:+.1%}, CI [{w.ci_lo:+.1%}, {w.ci_hi:+.1%}]) while "
            "retrieved does not: the information exists and Prometheus cannot find it")
    if w.ci_hi < MIN_PRACTICAL_EFFECT:
        return "ROW-2-RESIDUE-LACKS-INFORMATION", (
            f"whole-arm CI [{w.ci_lo:+.1%}, {w.ci_hi:+.1%}] excludes a practically meaningful "
            "effect even with maximum available residue in context — bounded to the tested "
            "regime, never 'at any capacity'")
    return UNROUTED, (
        f"whole-arm CI [{w.ci_lo:+.1%}, {w.ci_hi:+.1%}] spans both readings — it cannot "
        "separate 'residue lacks information' from 'retrieval failed'. Two different quarters "
        "of work; a thin number chooses neither.")


def harm_gain_by_gold(records: list[ProbeRecord], arm: str,
                      baseline: str = "F0") -> dict[str, dict[str, float]]:
    """[BC-6 / Charon C6] harm and gain split by gold label, not only pooled.

    This is the detector for the polarity confound Charon measured: D3 packets run ~26:1
    negative against a 50/50 task set, so a negative prime trades errors rather than shifting
    mean accuracy — it surfaces in harm, and only when harm is split by label.
    """
    cube = _by_task_arm_solver(records)
    gold_of = {r.task_uid: r.gold_bool for r in records if r.gold_bool is not None}
    solvers = sorted({r.solver for r in records})
    out: dict[str, dict[str, float]] = {}
    for label, want in (("gold_true", True), ("gold_false", False), ("pooled", None)):
        tasks = [t for t, g in gold_of.items() if want is None or g is want]
        a = _task_level_series(cube, arm, tasks, solvers)
        b = _task_level_series(cube, baseline, tasks, solvers)
        both = ~np.isnan(a) & ~np.isnan(b)
        if not both.any():
            out[label] = {"n": 0, "harm_rate": float("nan"), "gain_rate": float("nan")}
            continue
        av, bv = a[both], b[both]
        out[label] = {
            "n": int(both.sum()),
            "harm_rate": float(np.mean(bv > av)),   # baseline right, arm wrong
            "gain_rate": float(np.mean(av > bv)),
            "solved_to_unsolved": float(np.sum(bv > av)),
            "unsolved_to_solved": float(np.sum(av > bv)),
        }
    return out


def strict_screen_reanalysis(records: list[ProbeRecord],
                             strict_excluded_uids: set[str]) -> Optional["Comparison"]:
    """[BC-3 / Charon C1] The primary endpoint, recomputed on the strict-screened subset.

    Zero API cost — a second pass over a results file already collected. It converts the
    contamination-leniency design choice from an assumption into a measurement: if lenient and
    strict agree, the leniency is demonstrated harmless rather than argued harmless.
    """
    kept = [r for r in records if r.task_uid not in strict_excluded_uids]
    if not kept:
        return None
    cube = _by_task_arm_solver(kept)
    tasks = sorted({r.task_uid for r in kept})
    solvers = sorted({r.solver for r in kept})
    d = (_task_level_series(cube, "F-prom-retrieved", tasks, solvers)
         - _task_level_series(cube, "F-null", tasks, solvers))
    delta, lo, hi, p = paired_bootstrap(d)
    return Comparison("PRIMARY (strict-screened subset) [BC-3]",
                      int((~np.isnan(d)).sum()), delta, lo, hi, p)


def detect_topic_conditioning(acc: dict[str, float]) -> Optional[str]:
    """The matrix row the spec lacked: any on-topic text primes the solver."""
    need = ("F0", "F-null", "F-generic", "F-prom-retrieved")
    if not all(a in acc for a in need):
        return None
    packeted = [acc["F-null"], acc["F-generic"], acc["F-prom-retrieved"]]
    if max(packeted) - min(packeted) <= 0.02 and min(packeted) - acc["F0"] >= TARGET_EFFECT:
        return ("TOPIC-CONDITIONING: F-prom ~ F-null ~ F-generic, all well above F0. "
                "The lift belongs to prompting, not to residue; no retrieval work is justified.")
    return None


# --------------------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------------------

def analyze(records: list[ProbeRecord]) -> AnalysisResult:
    assert_no_synthetic(records)  # structural, not a matter of discipline

    res = AnalysisResult(admissible=True)
    res.diagnostics = arm_diagnostics(records)
    res.admissible, res.admissibility_notes = check_admissibility(res.diagnostics)

    cube = _by_task_arm_solver(records)
    tasks = sorted({r.task_uid for r in records})
    solvers = sorted({r.solver for r in records})
    acc = {d.arm: d.accuracy for d in res.diagnostics}

    prom = _task_level_series(cube, "F-prom-retrieved", tasks, solvers)
    null = _task_level_series(cube, "F-null", tasks, solvers)
    paired = prom - null
    valid = ~np.isnan(paired)

    delta, lo, hi, p = paired_bootstrap(paired)
    res.primary = Comparison("F-prom-retrieved - F-null (pooled)", int(valid.sum()),
                             delta, lo, hi, p)

    # negative transfer: does the arm break things F0 got right?
    f0 = _task_level_series(cube, "F0", tasks, solvers)
    both = ~np.isnan(f0) & ~np.isnan(prom)
    if both.any():
        f0b, prb = f0[both], prom[both]
        res.harm_rate = float(np.mean((f0b > prb)))
        res.gain_rate = float(np.mean((prb > f0b)))

    # per-solver McNemar (secondary)
    for s in solvers:
        b = c = 0
        for t in tasks:
            pv, nv = cube.get((t, "F-prom-retrieved", s)), cube.get((t, "F-null", s))
            if pv is None or nv is None:
                continue
            b += int(pv == 1 and nv == 0)
            c += int(pv == 0 and nv == 1)
        res.per_solver_mcnemar[s] = mcnemar_exact(b, c)

    # per-stratum (exploratory by construction — underpowered at ~N/4, prereg §6.2)
    strat_p = []
    for d in ("D0", "D1", "D2", "D3"):
        d_tasks = sorted({r.task_uid for r in records if r.d_stratum == d})
        n_records = sum(1 for r in records if r.d_stratum == d)
        if n_records < MIN_STRATUM_RECORDS:
            res.strata.append(Comparison(f"{d} NOT-RUN-FOR-LACK-OF-RESIDUE", n_records,
                                         float("nan"), float("nan"), float("nan"),
                                         float("nan"), exploratory=True))
            continue
        dp = _task_level_series(cube, "F-prom-retrieved", d_tasks, solvers)
        dn = _task_level_series(cube, "F-null", d_tasks, solvers)
        dd, dlo, dhi, dpv = paired_bootstrap(dp - dn)
        res.strata.append(Comparison(d, len(d_tasks), dd, dlo, dhi, dpv, exploratory=True))
        strat_p.append(dpv)

    # the §2 decomposition
    def a(name):
        return acc.get(name, float("nan"))

    res.decomposition = {
        "residue_existence  (whole - null)": a("F-prom-whole") - a("F-null"),
        "retrieval_efficiency (retrieved - null)": a("F-prom-retrieved") - a("F-null"),
        "retrieval_loss     (whole - retrieved)": a("F-prom-whole") - a("F-prom-retrieved"),
        "oracle_gap         (oracle - whole)": a("F-oracle") - a("F-prom-whole"),
        "specificity_margin (retrieved - generic)": a("F-prom-retrieved") - a("F-generic"),
    }

    if not res.admissible:
        res.verdict = "INADMISSIBLE-FORMAT-CONFOUNDED"
        res.verdict_reason = "; ".join(res.admissibility_notes)
        return res

    topic = detect_topic_conditioning(acc)
    if topic:
        res.verdict, res.verdict_reason = "TOPIC-CONDITIONING", topic
        return res

    res.verdict, res.verdict_reason = classify(delta, lo, hi, res.harm_rate, res.gain_rate)
    return res


def format_report(res: AnalysisResult) -> str:
    L = ["=== Metabolization Probe -- analysis ===", ""]
    L.append("arm diagnostics (accuracy | parse-fail | timeout):")
    for d in res.diagnostics:
        L.append(f"  {d.arm:20s} n={d.n:5d}  acc {d.accuracy:6.1%}  "
                 f"pf {d.parse_fail_rate:5.1%}  to {d.timeout_rate:5.1%}")
    for n in res.admissibility_notes:
        L.append(f"  ! {n}")
    if res.primary:
        p = res.primary
        L += ["", f"PRIMARY  {p.label}",
              f"  n_tasks={p.n_tasks}  delta {p.delta:+.1%}  "
              f"CI [{p.ci_lo:+.1%}, {p.ci_hi:+.1%}]  p={p.p_value:.4f}"]
    L += ["", f"harm_rate {res.harm_rate:.1%}   gain_rate {res.gain_rate:.1%}", "",
          "decomposition:"]
    for k, v in res.decomposition.items():
        L.append(f"  {k:42s} {v:+.1%}")
    L += ["", "per-distance (EXPLORATORY -- underpowered by construction):"]
    for s in res.strata:
        if math.isnan(s.delta):
            L.append(f"  {s.label:38s} n={s.n_tasks}")
        else:
            L.append(f"  {s.label:6s} n={s.n_tasks:4d}  delta {s.delta:+.1%}  "
                     f"CI [{s.ci_lo:+.1%}, {s.ci_hi:+.1%}]")
    L += ["", f"VERDICT: {res.verdict}", f"  {res.verdict_reason}"]
    return "\n".join(L)
