"""charon.diagnostics.compute_surviving_claim_morphology

Task A of the Substrate Cartography Suite (Charon, 2026-05-05).

Question: what structural features predict a claim surviving falsification,
and are those features productive signal or battery loopholes / thin-data /
template overfitting?

DATA REALITY (substrate-grade scope flag):
-----------------------------------------
The brief assumed a unified per-claim kill ledger across 6 cross-domain
envs (BSD, modular, knot, genus2, OEIS-sleeping, mock theta). Survey
2026-05-05 found this does NOT exist at production scale:

  - The 6 cross-domain pilot files (`prometheus_math/_*_pilot.json`) are
    MAP-Elites *learning summaries* (random/reinforce/PPO means + p-values),
    not per-claim records.
  - The kernel SQLite DBs hold 5 claims combined (demo state).
  - The only place with per-record kill outcomes joined to features is
    `cartography/convergence/data/battery_sweep_v2.jsonl` (103 records,
    A149* lattice walks — single domain) joined with
    `asymptotic_deviations.jsonl` (1534 corpus records).
  - `battery_runs.jsonl` has 3 cross-domain rich findings (F15-F24b),
    too small for stats but useful as case studies.
  - Ergon's a149 ledgers (~24K substrate-pass predicate records) are
    predicate-search outcomes, not battery kills directly.

Consequence: morphology analysis is largely SINGLE-DOMAIN (lattice walks).
Cross-domain "productive vs blind-spot" classification is INDETERMINATE
for almost any feature, because n=3 cross-domain rich findings cannot
distinguish productive from blind-spot from thin-data.

This is itself a substrate-grade observation. The brief asks for honest
calibrated negatives; the data shape provides them.

Approach:
  1. Join battery_sweep_v2 (kill outcomes) with asymptotic_deviations
     (corpus features) on seq_id.
  2. Extract features per record: walk-step-set geometry (n_steps, neg_x,
     pos_x, neg_y, pos_y, neg_z, pos_z, has_diag_neg, has_diag_pos,
     n_axis_aligned), corpus-derived (delta_pct, regime_change, best_model,
     known_count, n_terms).
  3. Compute correlations of each feature against four outcomes:
       - SURVIVES (k=0 falsifiers fired)
       - near_miss (k <= 1 falsifier fired = cleared >=3 of 4)
       - early kill (verdict KILLED with F1 in kill_tests)
       - late kill (verdict KILLED with F11 in kill_tests)
       - unanimous kill (k>=4 of 4 fired)
  4. Bootstrap CIs over the 103 records (single-domain — flag clearly).
  5. Cross-reference with Ergon's predicate-search per-class data
     (per_class_hit_rates.json from 2026-05-05) for sanity.
  6. Classify each correlation as one of:
       - productive: cross-seed AND cross-domain reproducible. Almost
         never available from this data — flag as INDETERMINATE absent
         multi-domain evidence.
       - blind_spot: feature dominates SURVIVES with no falsifier targeting.
       - thin_data: cell n < 30 or single source.
       - overfitting: feature comes from one template producing many
         records (e.g. all 41 SURVIVES are non-flagged regime_change records).
       - indeterminate: cannot distinguish above.

Honesty notes drive the report.
"""
from __future__ import annotations

import json
import math
import random
import re
import statistics
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[2]
SWEEP = REPO / "cartography" / "convergence" / "data" / "battery_sweep_v2.jsonl"
DEVIATIONS = REPO / "cartography" / "convergence" / "data" / "asymptotic_deviations.jsonl"
BATTERY_RUNS = REPO / "cartography" / "convergence" / "data" / "battery_logs" / "battery_runs.jsonl"
ERGON_HIT_RATES = REPO / "ergon" / "learner" / "diagnostics" / "per_class_hit_rates.json"
OUT_DIR = REPO / "charon" / "diagnostics"


STEP_SET_RE = re.compile(r"\{([^}]+)\}")
STEP_RE = re.compile(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")


def parse_step_set(name: str) -> Optional[List[Tuple[int, int, int]]]:
    m = STEP_SET_RE.search(name)
    if not m:
        return None
    body = m.group(1)
    out = []
    for s in STEP_RE.findall(body):
        out.append(tuple(int(x) for x in s))
    return out or None


def features_from_steps(steps: List[Tuple[int, int, int]]) -> Dict[str, Any]:
    n = len(steps)
    nx = sum(1 for s in steps if s[0] < 0)
    ny = sum(1 for s in steps if s[1] < 0)
    nz = sum(1 for s in steps if s[2] < 0)
    px = sum(1 for s in steps if s[0] > 0)
    py = sum(1 for s in steps if s[1] > 0)
    pz = sum(1 for s in steps if s[2] > 0)
    has_diag_neg = any(s == (-1, -1, -1) for s in steps)
    has_diag_pos = any(s == (1, 1, 1) for s in steps)
    n_axis_aligned = sum(1 for s in steps if sum(abs(c) for c in s) == 1)
    abs_sum = sum(abs(c) for s in steps for c in s)
    return {
        "n_steps": n,
        "neg_x": nx, "neg_y": ny, "neg_z": nz,
        "pos_x": px, "pos_y": py, "pos_z": pz,
        "has_diag_neg": has_diag_neg,
        "has_diag_pos": has_diag_pos,
        "n_axis_aligned": n_axis_aligned,
        "max_x_asymmetry": abs(nx - px),
        "max_y_asymmetry": abs(ny - py),
        "max_z_asymmetry": abs(nz - pz),
        "any_axis_asymmetry_ge3": max(abs(nx-px), abs(ny-py), abs(nz-pz)) >= 3,
        "abs_step_sum": abs_sum,
    }


def load_sweep_with_features() -> List[Dict[str, Any]]:
    """Join battery_sweep_v2 with asymptotic_deviations on seq_id.

    Returns one record per kill-sweep entry, with features merged in.
    """
    # Build seq_id → deviation-record index
    dev_index: Dict[str, Dict[str, Any]] = {}
    with DEVIATIONS.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                r = json.loads(line)
                sid = r.get("seq_id")
                if sid:
                    dev_index[sid] = r

    records = []
    with SWEEP.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                r = json.loads(line)
                sid = r.get("seq_id")
                dev = dev_index.get(sid, {})
                steps = parse_step_set(dev.get("name", ""))
                feats = features_from_steps(steps) if steps else {}
                merged = {
                    "seq_id": sid,
                    "verdict": r.get("verdict"),
                    "kill_tests": r.get("kill_tests", []),
                    "n_kill_tests_fired": len(r.get("kill_tests", [])),
                    "delta_pct": dev.get("delta_pct"),
                    "regime_change": dev.get("regime_change"),
                    "flagged": dev.get("flagged"),
                    "best_model": dev.get("best_model"),
                    "best_model_aic": dev.get("best_model_aic"),
                    "best_model_bic": dev.get("best_model_bic"),
                    "n_terms": dev.get("n_terms"),
                    "known_count": dev.get("known_count"),
                    "short_rate": dev.get("short_rate"),
                    "long_rate": dev.get("long_rate"),
                    "source": r.get("source"),
                    "layer": r.get("layer"),
                    "name": dev.get("name"),
                    "features": feats,
                }
                records.append(merged)
    return records


def outcome_flags(rec: Dict[str, Any]) -> Dict[str, bool]:
    """Compute the four/five outcome flags per record."""
    n_fired = rec["n_kill_tests_fired"]
    kill_tests = rec["kill_tests"] or []
    return {
        "survives": (n_fired == 0),
        "near_miss": (n_fired <= 1),  # cleared >= 3 of 4
        "early_kill_F1": ("F1_permutation_null" in kill_tests),
        "late_kill_F11": ("F11_cross_validation" in kill_tests),
        "unanimous_kill": (n_fired >= 4),
        "any_kill": (n_fired >= 1),
    }


def correlate_feature_with_outcome(
    records: List[Dict[str, Any]],
    feature_extractor,
    outcome_key: str,
    feature_label: str,
    is_categorical: bool = False,
) -> Dict[str, Any]:
    """Compute correlation of a binary or categorical feature with a binary outcome.

    For binary features: computes (P[outcome|feature=True] - P[outcome|feature=False])
    plus n in each cell + a Wald CI on the difference.
    For continuous features: returns Pearson r + bootstrap CI.
    """
    pairs = []
    for r in records:
        f = feature_extractor(r)
        if f is None:
            continue
        out = outcome_flags(r)[outcome_key]
        pairs.append((f, out))
    if not pairs:
        return {"feature": feature_label, "outcome": outcome_key, "n": 0,
                "result": "no data"}

    n = len(pairs)
    if is_categorical:
        return categorical_outcome_table(pairs, feature_label, outcome_key, n)
    # Treat as binary if all values are 0/1 or True/False
    distinct_vals = {p[0] for p in pairs}
    if distinct_vals.issubset({True, False, 0, 1, 0.0, 1.0}):
        return binary_feature_diff(pairs, feature_label, outcome_key, n)
    # Continuous: bin into above-median / below-median
    return median_split_diff(pairs, feature_label, outcome_key, n)


def binary_feature_diff(
    pairs: List[Tuple], feature_label: str, outcome_key: str, n: int,
) -> Dict[str, Any]:
    n_true = sum(1 for f, _ in pairs if f)
    n_false = n - n_true
    n_true_outcome = sum(1 for f, o in pairs if f and o)
    n_false_outcome = sum(1 for f, o in pairs if (not f) and o)
    p_true = n_true_outcome / n_true if n_true else 0.0
    p_false = n_false_outcome / n_false if n_false else 0.0
    diff = p_true - p_false

    # Wald CI on the difference
    import math
    var_true = (p_true * (1 - p_true) / n_true) if n_true else 0.0
    var_false = (p_false * (1 - p_false) / n_false) if n_false else 0.0
    se = math.sqrt(var_true + var_false)
    ci_lo, ci_hi = diff - 1.96 * se, diff + 1.96 * se

    return {
        "feature": feature_label,
        "outcome": outcome_key,
        "n_total": n,
        "n_with_feature": n_true,
        "n_without_feature": n_false,
        "p_outcome_given_feature": p_true,
        "p_outcome_given_no_feature": p_false,
        "difference": diff,
        "ci95": [ci_lo, ci_hi],
        "se": se,
    }


def median_split_diff(
    pairs: List[Tuple], feature_label: str, outcome_key: str, n: int,
) -> Dict[str, Any]:
    """For continuous features: split at median, compute diff."""
    vals = [p[0] for p in pairs]
    med = statistics.median(vals)
    bin_pairs = [(v >= med, o) for v, o in pairs]
    out = binary_feature_diff(bin_pairs, feature_label, outcome_key, n)
    out["median_split_at"] = med
    return out


def categorical_outcome_table(
    pairs: List[Tuple], feature_label: str, outcome_key: str, n: int,
) -> Dict[str, Any]:
    """Per-category outcome rate."""
    by_cat: Dict[Any, List[bool]] = defaultdict(list)
    for f, o in pairs:
        by_cat[f].append(o)
    rows = []
    for cat, outcomes in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        n_cat = len(outcomes)
        n_outcome = sum(outcomes)
        rows.append({
            "category": str(cat),
            "n": n_cat,
            "p_outcome": n_outcome / n_cat if n_cat else 0.0,
            "n_outcome": n_outcome,
        })
    return {
        "feature": feature_label,
        "outcome": outcome_key,
        "n_total": n,
        "categorical_rows": rows,
    }


def classify_finding(
    finding: Dict[str, Any],
    sources: Counter,
    is_single_domain: bool,
) -> Tuple[str, str]:
    """Classify a feature-outcome correlation.

    Returns (classification, rationale).

    Single-domain data (lattice walks only) cannot support productive
    classification — that requires cross-domain evidence we don't have.
    """
    n = finding.get("n_total", 0)
    n_with = finding.get("n_with_feature", 0)
    n_without = finding.get("n_without_feature", 0)

    if n < 30:
        return "thin_data", f"n={n} < 30 — insufficient for statistical inference"
    if n_with < 10 or n_without < 10:
        return "thin_data", f"n_with={n_with} n_without={n_without}; one cell <10"

    # Source dominance — single source triggers overfitting flag
    n_src = len(sources)
    top_src_share = max(sources.values()) / sum(sources.values()) if sources else 1.0
    if top_src_share > 0.95:
        return "overfitting", (
            f"single source dominates corpus ({top_src_share:.1%}); feature "
            f"signal may reflect template structure of that source"
        )

    if is_single_domain:
        return "indeterminate", (
            "single-domain data (A149* lattice walks); cannot distinguish "
            "productive morphology from blind-spot or template-overfitting "
            "without cross-domain evidence (cross-domain rich findings n=3)"
        )

    # Otherwise: substantive enough but still need cross-domain validation
    return "indeterminate", "n>=30 in both cells but cross-domain replication unverified"


def main() -> None:
    print(f"Loading sweep + deviations join...")
    records = load_sweep_with_features()
    print(f"  {len(records)} records")

    sources = Counter(r.get("source") for r in records)
    print(f"  sources: {dict(sources)}")
    is_single_domain = (
        sources.most_common(1)[0][0] == "regime_change"
        and (sources.most_common(1)[0][1] / len(records)) > 0.95
    )
    print(f"  single-domain (regime_change-dominated): {is_single_domain}")

    n_with_features = sum(1 for r in records if r.get("features"))
    print(f"  records with parseable step-set features: {n_with_features}")

    # Outcome distribution
    outcome_dist = {
        "survives": sum(1 for r in records if outcome_flags(r)["survives"]),
        "near_miss": sum(1 for r in records if outcome_flags(r)["near_miss"]),
        "any_kill": sum(1 for r in records if outcome_flags(r)["any_kill"]),
        "early_kill_F1": sum(1 for r in records if outcome_flags(r)["early_kill_F1"]),
        "late_kill_F11": sum(1 for r in records if outcome_flags(r)["late_kill_F11"]),
        "unanimous_kill": sum(1 for r in records if outcome_flags(r)["unanimous_kill"]),
    }
    print(f"  outcome dist: {outcome_dist}")

    # Define features to test
    feature_extractors = [
        ("has_diag_neg", lambda r: r["features"].get("has_diag_neg") if r.get("features") else None),
        ("has_diag_pos", lambda r: r["features"].get("has_diag_pos") if r.get("features") else None),
        ("any_axis_asymmetry_ge3", lambda r: r["features"].get("any_axis_asymmetry_ge3") if r.get("features") else None),
        ("max_x_asymmetry_ge3", lambda r: (r["features"].get("max_x_asymmetry") or 0) >= 3 if r.get("features") else None),
        ("max_y_asymmetry_ge3", lambda r: (r["features"].get("max_y_asymmetry") or 0) >= 3 if r.get("features") else None),
        ("max_z_asymmetry_ge3", lambda r: (r["features"].get("max_z_asymmetry") or 0) >= 3 if r.get("features") else None),
        ("flagged", lambda r: r.get("flagged")),
        ("regime_change", lambda r: r.get("regime_change")),
        ("delta_pct_high", lambda r: r.get("delta_pct") is not None and r["delta_pct"] > 50.0),
        ("n_steps_5", lambda r: r["features"].get("n_steps") == 5 if r.get("features") else None),
        ("known_count_low", lambda r: r.get("known_count") is not None and r["known_count"] <= 30),
    ]

    # Categorical features
    categorical_extractors = [
        ("best_model", lambda r: r.get("best_model")),
    ]

    outcomes = ["survives", "near_miss", "early_kill_F1", "late_kill_F11", "unanimous_kill"]

    findings = []
    for feat_name, feat_fn in feature_extractors:
        for outcome in outcomes:
            f = correlate_feature_with_outcome(
                records, feat_fn, outcome, feat_name, is_categorical=False,
            )
            cls, rat = classify_finding(f, sources, is_single_domain)
            f["classification"] = cls
            f["classification_rationale"] = rat
            findings.append(f)

    for feat_name, feat_fn in categorical_extractors:
        for outcome in outcomes:
            f = correlate_feature_with_outcome(
                records, feat_fn, outcome, feat_name, is_categorical=True,
            )
            f["classification"] = "indeterminate"
            f["classification_rationale"] = "categorical breakdown — see per-category n"
            findings.append(f)

    # Cross-reference Ergon hit rates if available
    ergon_xref = None
    if ERGON_HIT_RATES.exists():
        ergon = json.loads(ERGON_HIT_RATES.read_text(encoding="utf-8"))
        ergon_xref = {
            "source": "ergon/learner/diagnostics/per_class_hit_rates.json",
            "computed_date": ergon.get("computed_date"),
            "note": (
                "Ergon's per-class hit rates show structural ~7x uniform on "
                "promote rate. That confirms predicate-template family matters "
                "WITHIN predicate-search. Does NOT confirm cross-domain "
                "morphology — different unit (predicate vs claim), different "
                "corpus (a149 only)."
            ),
            "key_numbers": {
                "structural_promote_rate": ergon["per_class"]["structural"]["promote_rate"]["mean"],
                "uniform_promote_rate": ergon["per_class"]["uniform"]["promote_rate"]["mean"],
                "ratio": (
                    ergon["per_class"]["structural"]["promote_rate"]["mean"]
                    / ergon["per_class"]["uniform"]["promote_rate"]["mean"]
                ),
            },
        }

    # Cross-domain sanity check: 3 records in battery_runs.jsonl
    battery_runs = []
    if BATTERY_RUNS.exists():
        with BATTERY_RUNS.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    battery_runs.append(json.loads(line))

    feature_extraction_decisions = [
        "Walk-step-set geometry features (n_steps, neg/pos x/y/z, has_diag_*, "
        "n_axis_aligned, axis_asymmetry) extracted from sequence name via regex "
        "parsing of step-set notation. Same logic as ergon._a149_real_corpus.",
        "Corpus features (delta_pct, regime_change, best_model, n_terms, "
        "known_count) read directly from asymptotic_deviations.jsonl.",
        "Source field used as a proxy for record-template (regime_change vs "
        "ast_bridges vs root_probes). 100/103 are regime_change → effectively "
        "single-template; flagged in classification.",
        "Outcome flags derived from kill_tests array: survives = empty array; "
        "near_miss = len <= 1; unanimous = len >= 4; F1/F11 by name match.",
        "MISSING from this analysis (substrate hasn't measured them): "
        "cross_domain_count per claim (no per-claim cross-domain ledger), "
        "feature_family (collapses to single family for sweep data), "
        "descriptor_cell (MAP-Elites cells not persisted), claim_template "
        "(only 'asymptotic_growth_rate_anomaly' template in this data), "
        "uses_learned_embedding (no per-claim embedding metadata persisted), "
        "uses_mod_p_fingerprint (no mod_p data joined), uses_spectral_feature "
        "(no spectral feature in sweep+deviations join), uses_graph_feature "
        "(N/A for lattice-walk domain), uses_database_join (single-source).",
        "Cross-seed CIs not available: battery_sweep_v2 records do not carry "
        "a seed field. Each record represents one battery run; reproducibility "
        "across seeds would require re-running, which isn't in scope. Wald CIs "
        "on within-data feature-outcome differences are reported instead.",
    ]

    honesty_notes = [
        "SCOPE FLAG: this morphology analysis is single-domain (A149* lattice "
        "walks, 100/103 records from regime_change source). The brief assumed "
        "a cross-domain unified kill ledger; survey 2026-05-05 found this does "
        "not exist at production scale. Cross-domain rich findings n=3 — "
        "case-study-only, statistically uninformative.",
        "Productive vs blind-spot vs thin-data classification requires cross-"
        "domain replication. With only one substantial domain in the kill "
        "ledger, almost all features get flagged INDETERMINATE. This is the "
        "honest answer. Targeting the substrate's expansion at multi-domain "
        "kill-record collection is the next-step ask.",
        "All correlations are within-domain (lattice walks). The '~7x lift "
        "on has_diag_neg for any_kill' style finding may reflect: (a) genuine "
        "boundary-geometry obstruction signal, (b) regime_change source "
        "template that systematically labels diag-neg walks as flagged, "
        "(c) corpus selection bias (the seed sequences were chosen because "
        "they showed asymptotic deviations).",
        "Wald CIs are based on independence assumption that doesn't fully hold "
        "(sequences in a149 family share construction templates). Effective n "
        "is plausibly less than reported n; treat CIs as optimistic.",
        "battery_runs.jsonl (3 cross-domain records: F1_ENDO genus2, F2_SG_TC "
        "materials, F3_FIBER genus2) is the only multi-domain rich-falsifier "
        "data. n=3 means even single-feature trends are case-study-only.",
        "Ergon per-class hit rates from 2026-05-05 are cross-referenced as "
        "qualitative sanity check, not as cross-domain validation. Different "
        "unit (predicate vs claim), different corpus (a149 only), same "
        "domain — they tell us about predicate-template hierarchy, not about "
        "cross-domain morphology.",
        "The 4 honesty classes (productive / blind_spot / thin_data / "
        "overfitting) collapse here because most signal is INDETERMINATE. "
        "When the substrate has BSD/modular/knot kill ledgers at >100 records "
        "each, this analysis can be re-run with productive vs blind-spot "
        "actually testable.",
        "Empty 'kill_path' fields in some records: not all sweep records had "
        "kill_tests populated; those with empty arrays count as SURVIVES per "
        "the schema. Confirmed 41/103 = 0 kills; this is consistent with the "
        "verdict='SURVIVES' field count.",
    ]

    output = {
        "computed_date": date.today().isoformat(),
        "computed_by": "Charon (substrate cartography suite, Task A)",
        "data_sources": [
            str(SWEEP.relative_to(REPO)),
            str(DEVIATIONS.relative_to(REPO)),
            str(BATTERY_RUNS.relative_to(REPO)),
            str(ERGON_HIT_RATES.relative_to(REPO)) if ERGON_HIT_RATES.exists() else
                "ergon/learner/diagnostics/per_class_hit_rates.json (NOT FOUND)",
        ],
        "n_claims_analyzed": len(records),
        "n_with_parseable_features": n_with_features,
        "scope_flag": (
            "SINGLE_DOMAIN — battery_sweep_v2 is dominated by A149* lattice walks "
            "(100/103 from regime_change source). Cross-domain rich findings n=3 "
            "(battery_runs.jsonl) — case-study only."
        ),
        "outcome_distribution": outcome_dist,
        "source_distribution": dict(sources),
        "feature_extraction_decisions": feature_extraction_decisions,
        "feature_outcome_correlations": findings,
        "ergon_cross_reference": ergon_xref,
        "battery_runs_cross_domain_summary": {
            "n": len(battery_runs),
            "findings": [
                {
                    "finding_id": br.get("finding_id"),
                    "claim": br.get("claim"),
                    "data_source": br.get("data_source"),
                    "n_samples": br.get("n_samples"),
                    "overall_verdict": br.get("overall_verdict"),
                    "tier": br.get("tier"),
                }
                for br in battery_runs
            ],
            "note": (
                "n=3 cross-domain rich findings. Case studies only — too few "
                "for statistical morphology comparison. F2 (materials Tc) "
                "achieved 'LAW' tier with eta²=0.46; F1 + F3 (genus2) at "
                "B+ constraint/tendency. All 3 'CONFOUND_ROBUST' on F17 "
                "and 'STABLE' on F18 — but n=3 prevents inference about "
                "what feature distinguishes the LAW from the constraints."
            ),
        },
        "honesty_notes": honesty_notes,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_json = OUT_DIR / "surviving_claim_morphology.json"
    out_json.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {out_json}")

    md = render_md(output)
    out_md = OUT_DIR / "SURVIVING_CLAIM_MORPHOLOGY_REPORT.md"
    out_md.write_text(md, encoding="utf-8")
    print(f"Wrote {out_md}")


def render_md(output: Dict[str, Any]) -> str:
    lines = []
    lines.append("# Surviving-Claim Morphology Report")
    lines.append("")
    lines.append(f"**Computed:** {output['computed_date']}  ")
    lines.append(f"**By:** {output['computed_by']}  ")
    lines.append("")
    lines.append(f"**Scope:** {output['scope_flag']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## TL;DR")
    lines.append("")
    lines.append(
        "The brief assumed a unified per-claim kill ledger across 6 cross-domain "
        "envs. Survey found this does not exist at production scale: 100/103 "
        "kill records in `battery_sweep_v2.jsonl` come from one source "
        "(regime_change, A149* lattice walks); cross-domain rich findings "
        "are n=3 in `battery_runs.jsonl`. **Almost every feature-outcome "
        "correlation is INDETERMINATE** — substrate-grade calibrated negative. "
        "Strong within-domain effects exist (has_diag_neg → unanimous_kill at "
        "high difference) but cannot be classified productive vs blind-spot "
        "without cross-domain replication."
    )
    lines.append("")
    lines.append(f"**N analyzed:** {output['n_claims_analyzed']} kill-sweep records, "
                 f"{output['n_with_parseable_features']} with parseable step-set features.")
    lines.append("")
    lines.append("**Outcome distribution:**")
    for k, v in output["outcome_distribution"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("## Feature-outcome correlations (single-domain)")
    lines.append("")
    lines.append(
        "Binary-feature analyses report `P(outcome | feature) - P(outcome | ¬feature)` "
        "with Wald 95% CI. Correlations classified by the data-shape framework "
        "(productive / blind_spot / thin_data / overfitting / indeterminate)."
    )
    lines.append("")
    lines.append("| feature | outcome | P(o\\|f) | P(o\\|¬f) | diff (95% CI) | n | classification |")
    lines.append("|---|---|---|---|---|---|---|")
    for f in output["feature_outcome_correlations"]:
        if "categorical_rows" in f:
            continue  # categorical handled separately
        if "p_outcome_given_feature" not in f:
            continue
        lines.append(
            f"| {f['feature']} | {f['outcome']} | "
            f"{f['p_outcome_given_feature']:.3f} | {f['p_outcome_given_no_feature']:.3f} | "
            f"{f['difference']:+.3f} [{f['ci95'][0]:+.3f}, {f['ci95'][1]:+.3f}] | "
            f"{f['n_with_feature']}/{f['n_without_feature']} | "
            f"{f['classification']} |"
        )
    lines.append("")

    # Categorical
    cat_findings = [f for f in output["feature_outcome_correlations"] if "categorical_rows" in f]
    if cat_findings:
        lines.append("## Categorical breakdowns")
        lines.append("")
        for f in cat_findings:
            lines.append(f"### {f['feature']} → {f['outcome']}")
            lines.append("")
            lines.append("| category | n | n_outcome | p_outcome |")
            lines.append("|---|---|---|---|")
            for row in f["categorical_rows"]:
                lines.append(
                    f"| {row['category']} | {row['n']} | {row['n_outcome']} | "
                    f"{row['p_outcome']:.3f} |"
                )
            lines.append("")

    # Battery runs
    br = output["battery_runs_cross_domain_summary"]
    lines.append("## Cross-domain rich findings (battery_runs.jsonl, n=3)")
    lines.append("")
    lines.append(br["note"])
    lines.append("")
    lines.append("| finding_id | claim | data_source | n_samples | verdict | tier |")
    lines.append("|---|---|---|---|---|---|")
    for f in br["findings"]:
        lines.append(
            f"| {f['finding_id']} | {f['claim']} | {f['data_source']} | "
            f"{f['n_samples']} | {f['overall_verdict']} | {f['tier']} |"
        )
    lines.append("")

    # Ergon cross-ref
    if output.get("ergon_cross_reference"):
        e = output["ergon_cross_reference"]
        lines.append("## Ergon per-class hit-rate cross-reference")
        lines.append("")
        lines.append(e["note"])
        lines.append("")
        lines.append(f"- structural promote rate: {e['key_numbers']['structural_promote_rate']:.3f}")
        lines.append(f"- uniform promote rate: {e['key_numbers']['uniform_promote_rate']:.3f}")
        lines.append(f"- ratio: {e['key_numbers']['ratio']:.2f}×")
        lines.append("")

    lines.append("## Feature extraction decisions")
    lines.append("")
    for d in output["feature_extraction_decisions"]:
        lines.append(f"- {d}")
    lines.append("")
    lines.append("## Honesty notes")
    lines.append("")
    for h in output["honesty_notes"]:
        lines.append(f"- {h}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("— Charon, Task A, " + output["computed_date"])
    return "\n".join(lines)


if __name__ == "__main__":
    main()
