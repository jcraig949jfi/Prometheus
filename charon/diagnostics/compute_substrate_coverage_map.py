"""charon.diagnostics.compute_substrate_coverage_map

Task C of the Substrate Cartography Suite (Charon, 2026-05-05).

Question: which cells (domain × object_type × invariant_family × feature_family
× source_dataset) are dense / moderate / thin / void / misleading_dense?

Scope (per brief): BSD / modular / knot triple. Genus2 / mock_theta /
oeis_sleeping deferred to follow-up.

LOAD-BEARING OUTPUT: misleading_dense flag — cells with many records but
low invariant diversity, high missingness, duplicated source structure,
or one dominant feature family.
"""
from __future__ import annotations

import gzip
import json
import statistics
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[2]
DB = REPO / "prometheus_math" / "databases"
BRIDGES = REPO / "cartography" / "convergence" / "data" / "bridges.jsonl"
OUT_DIR = REPO / "charon" / "diagnostics"


def load_corpus(name: str) -> List[Dict[str, Any]]:
    path = DB / f"{name}.json.gz"
    with gzip.open(path, "rt", encoding="utf-8") as f:
        d = json.load(f)
    return d["entries"]


def compute_feature_distribution(
    records: List[Dict[str, Any]], feature_name: str,
    extractor=None,
) -> Dict[str, Any]:
    """Compute distribution stats for a feature across records.

    Returns: n_with, n_missing, distinct_values, top_value_share, dominant.
    """
    if extractor is None:
        extractor = lambda r: r.get(feature_name)
    vals = []
    n_missing = 0
    for r in records:
        v = extractor(r)
        if v is None:
            n_missing += 1
        else:
            try:
                vals.append(v)
            except (TypeError, ValueError):
                n_missing += 1

    n = len(records)
    if not vals:
        return {
            "feature": feature_name, "n": n, "n_with": 0, "n_missing": n_missing,
            "missingness_rate": 1.0, "n_distinct": 0, "top_value_share": 0.0,
            "dominant": None,
        }
    # For discrete features, count
    is_discrete = all(
        isinstance(v, (int, str, bool)) for v in vals[:100]
    )
    if is_discrete:
        cnt = Counter(vals)
        top_val, top_count = cnt.most_common(1)[0]
        return {
            "feature": feature_name, "n": n, "n_with": len(vals),
            "n_missing": n_missing, "missingness_rate": n_missing / n,
            "n_distinct": len(cnt), "top_value_share": top_count / len(vals),
            "dominant": str(top_val),
            "value_distribution": dict(cnt.most_common(8)),
        }
    # Continuous — report range + diversity proxy
    return {
        "feature": feature_name, "n": n, "n_with": len(vals),
        "n_missing": n_missing, "missingness_rate": n_missing / n,
        "n_distinct": len(set(vals)),
        "top_value_share": None,
        "dominant": None,
        "min": min(vals), "max": max(vals),
        "median": statistics.median(vals) if vals else None,
    }


def classify_coverage(
    n_objects: int, missingness: float, top_share: float, distinct: int,
    n_invariants_present: int,
) -> Tuple[str, List[str]]:
    """Apply the coverage tagging rubric."""
    flags = []
    if n_objects == 0:
        return "void", ["no records"]
    if n_objects < 30:
        flags.append("low_n")
        if n_objects < 10:
            return "thin", flags + [f"n={n_objects} < 10"]
        return "thin", flags + [f"n={n_objects} < 30"]
    # Misleading-dense triggers
    if missingness > 0.20:
        flags.append(f"high_missingness ({missingness:.0%})")
    if top_share is not None and top_share > 0.80:
        flags.append(f"dominant_value_share ({top_share:.0%})")
    if n_invariants_present < 3:
        flags.append(f"low_invariant_diversity ({n_invariants_present} invariants)")
    if distinct < 5 and n_objects > 30:
        flags.append(f"low_diversity (distinct={distinct} on n={n_objects})")
    if flags:
        return "misleading_dense", flags
    if n_objects >= 200:
        return "dense", []
    return "moderate", []


def analyze_bsd(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """BSD: elliptic curves with rich data."""
    cells: Dict[str, Any] = {}

    # Cell 1: arithmetic invariants
    rank_dist = compute_feature_distribution(
        records, "rank",
        extractor=lambda r: r.get("base", {}).get("rank"),
    )
    conductor_dist = compute_feature_distribution(
        records, "conductor",
        extractor=lambda r: r.get("base", {}).get("conductor"),
    )

    n_inv_arith = sum(
        1 for f in [rank_dist, conductor_dist] if f["n_with"] > 0
    )
    cells["BSD::elliptic_curve::arithmetic::cremona"] = {
        "n_objects": len(records),
        "n_claims_generated": "INCONCLUSIVE_DATA (no per-claim ledger)",
        "n_kills": "INCONCLUSIVE_DATA",
        "n_promotes": "INCONCLUSIVE_DATA",
        "n_near_misses": "INCONCLUSIVE_DATA",
        "feature_completeness": {
            "rank": rank_dist, "conductor": conductor_dist,
        },
        "missingness_rate": min(rank_dist["missingness_rate"],
                                conductor_dist["missingness_rate"]),
        "cross_domain_link_count": "see bridges.jsonl summary",
        "battery_applicable": True,
        "notes": (
            "Cremona dataset, full ainvs + a_p available. F1+F6+F9+F11 all "
            "applicable. Rank distribution: " +
            ", ".join(f"r={k}:n={v}" for k, v in rank_dist["value_distribution"].items())
        ),
    }
    tag, flags = classify_coverage(
        len(records),
        cells["BSD::elliptic_curve::arithmetic::cremona"]["missingness_rate"],
        rank_dist["top_value_share"],
        rank_dist["n_distinct"],
        n_inv_arith,
    )
    cells["BSD::elliptic_curve::arithmetic::cremona"]["coverage_tag"] = tag
    cells["BSD::elliptic_curve::arithmetic::cremona"]["coverage_flags"] = flags

    # Cell 2: L-function invariants (regulator, L1)
    regulator_dist = compute_feature_distribution(
        records, "regulator",
        extractor=lambda r: r.get("rich", {}).get("regulator"),
    )
    l1_dist = compute_feature_distribution(
        records, "L1",
        extractor=lambda r: r.get("rich", {}).get("L1"),
    )
    real_period_dist = compute_feature_distribution(
        records, "real_period",
        extractor=lambda r: r.get("rich", {}).get("real_period"),
    )
    n_inv_lfun = sum(
        1 for f in [regulator_dist, l1_dist, real_period_dist] if f["n_with"] > 0
    )
    cells["BSD::elliptic_curve::L_function::cremona"] = {
        "n_objects": len(records),
        "n_claims_generated": "INCONCLUSIVE_DATA",
        "n_kills": "INCONCLUSIVE_DATA",
        "feature_completeness": {
            "regulator": regulator_dist, "L1": l1_dist, "real_period": real_period_dist,
        },
        "missingness_rate": max(
            regulator_dist["missingness_rate"],
            l1_dist["missingness_rate"],
            real_period_dist["missingness_rate"],
        ),
        "battery_applicable": True,
        "notes": "Regulator, L1, real_period — full BSD-formula inputs",
    }
    tag, flags = classify_coverage(
        len(records),
        cells["BSD::elliptic_curve::L_function::cremona"]["missingness_rate"],
        None,
        regulator_dist["n_distinct"],
        n_inv_lfun,
    )
    cells["BSD::elliptic_curve::L_function::cremona"]["coverage_tag"] = tag
    cells["BSD::elliptic_curve::L_function::cremona"]["coverage_flags"] = flags

    return cells


def analyze_modular(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    cells: Dict[str, Any] = {}

    weight_dist = compute_feature_distribution(records, "weight")
    level_dist = compute_feature_distribution(records, "level")
    char_order_dist = compute_feature_distribution(records, "char_order")

    cells["modular::newform::level_weight::lmfdb"] = {
        "n_objects": len(records),
        "n_claims_generated": "INCONCLUSIVE_DATA",
        "feature_completeness": {
            "weight": weight_dist, "level": level_dist, "char_order": char_order_dist,
        },
        "missingness_rate": max(
            weight_dist["missingness_rate"], level_dist["missingness_rate"],
            char_order_dist["missingness_rate"],
        ),
        "battery_applicable": True,
        "notes": (
            "weight distribution: top values "
            f"{dict(list(weight_dist.get('value_distribution', {}).items())[:5])}"
        ),
    }
    tag, flags = classify_coverage(
        len(records),
        cells["modular::newform::level_weight::lmfdb"]["missingness_rate"],
        weight_dist["top_value_share"],
        weight_dist["n_distinct"],
        3,
    )
    cells["modular::newform::level_weight::lmfdb"]["coverage_tag"] = tag
    cells["modular::newform::level_weight::lmfdb"]["coverage_flags"] = flags

    # Coefficient features
    a_p_dist = compute_feature_distribution(
        records, "a_p_length",
        extractor=lambda r: len(r.get("a_p", [])) if r.get("a_p") else None,
    )
    cells["modular::newform::coefficients::lmfdb"] = {
        "n_objects": len(records),
        "n_claims_generated": "INCONCLUSIVE_DATA",
        "feature_completeness": {"a_p_length": a_p_dist},
        "missingness_rate": a_p_dist["missingness_rate"],
        "battery_applicable": True,
        "notes": (
            f"a_p length distribution: median={a_p_dist.get('median')}, "
            f"min={a_p_dist.get('min')}, max={a_p_dist.get('max')}"
        ),
    }
    tag, flags = classify_coverage(
        len(records), a_p_dist["missingness_rate"],
        None, a_p_dist["n_distinct"], 1,
    )
    if a_p_dist["n_distinct"] < 3:
        flags.append("uniform a_p length — likely fixed cap")
        tag = "misleading_dense"
    cells["modular::newform::coefficients::lmfdb"]["coverage_tag"] = tag
    cells["modular::newform::coefficients::lmfdb"]["coverage_flags"] = flags

    return cells


def analyze_knot(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    cells: Dict[str, Any] = {}

    crossing_dist = compute_feature_distribution(records, "crossing_number")
    sig_dist = compute_feature_distribution(records, "signature")
    genus_dist = compute_feature_distribution(records, "three_genus")
    hyp_dist = compute_feature_distribution(records, "hyperbolic_volume")
    cells["knot::hyperbolic_knot::topological::knotinfo"] = {
        "n_objects": len(records),
        "n_claims_generated": "INCONCLUSIVE_DATA",
        "feature_completeness": {
            "crossing_number": crossing_dist, "signature": sig_dist,
            "three_genus": genus_dist, "hyperbolic_volume": hyp_dist,
        },
        "missingness_rate": max(
            crossing_dist["missingness_rate"], sig_dist["missingness_rate"],
            genus_dist["missingness_rate"], hyp_dist["missingness_rate"],
        ),
        "battery_applicable": True,
        "notes": (
            f"crossing range [{crossing_dist.get('min')}, {crossing_dist.get('max')}], "
            f"hyperbolic_volume range [{hyp_dist.get('min'):.2f}, "
            f"{hyp_dist.get('max'):.2f}]"
            if hyp_dist.get('min') is not None else
            f"crossing range [{crossing_dist.get('min')}, {crossing_dist.get('max')}]"
        ),
    }
    tag, flags = classify_coverage(
        len(records),
        cells["knot::hyperbolic_knot::topological::knotinfo"]["missingness_rate"],
        crossing_dist["top_value_share"],
        crossing_dist["n_distinct"],
        4,
    )
    cells["knot::hyperbolic_knot::topological::knotinfo"]["coverage_tag"] = tag
    cells["knot::hyperbolic_knot::topological::knotinfo"]["coverage_flags"] = flags

    # Trace field / number-field
    nf_disc_dist = compute_feature_distribution(
        records, "nf_discriminant",
        extractor=lambda r: r.get("nf_discriminant"),
    )
    nf_class_dist = compute_feature_distribution(
        records, "nf_class_number",
        extractor=lambda r: r.get("nf_class_number"),
    )
    tf_class_dist = compute_feature_distribution(
        records, "trace_field_class",
        extractor=lambda r: r.get("trace_field_class"),
    )
    cells["knot::hyperbolic_knot::trace_field::knotinfo"] = {
        "n_objects": len(records),
        "n_claims_generated": "INCONCLUSIVE_DATA",
        "feature_completeness": {
            "nf_discriminant": nf_disc_dist,
            "nf_class_number": nf_class_dist,
            "trace_field_class": tf_class_dist,
        },
        "missingness_rate": max(
            nf_disc_dist["missingness_rate"],
            nf_class_dist["missingness_rate"],
            tf_class_dist["missingness_rate"],
        ),
        "battery_applicable": True,
        "notes": (
            f"trace_field_class top values: "
            f"{dict(list(tf_class_dist.get('value_distribution', {}).items())[:5])}"
        ),
    }
    tag, flags = classify_coverage(
        len(records),
        cells["knot::hyperbolic_knot::trace_field::knotinfo"]["missingness_rate"],
        tf_class_dist["top_value_share"],
        tf_class_dist["n_distinct"],
        3,
    )
    cells["knot::hyperbolic_knot::trace_field::knotinfo"]["coverage_tag"] = tag
    cells["knot::hyperbolic_knot::trace_field::knotinfo"]["coverage_flags"] = flags

    return cells


def load_bridges_summary() -> Dict[str, Any]:
    """Summarize bridges.jsonl — cross-dataset concept-keyed bridges."""
    if not BRIDGES.exists():
        return {"error": "not found"}
    with BRIDGES.open(encoding="utf-8") as f:
        bridges = [json.loads(l) for l in f if l.strip()]

    by_dataset = Counter()
    by_n_datasets = Counter()
    for b in bridges:
        for ds in b.get("datasets", {}):
            by_dataset[ds] += 1
        by_n_datasets[b.get("n_datasets", 0)] += 1

    return {
        "n_bridges": len(bridges),
        "by_dataset_freq": dict(by_dataset.most_common(15)),
        "by_n_datasets_distribution": dict(by_n_datasets),
        "note": (
            "bridges.jsonl is concept-keyed cross-dataset coverage. Dataset "
            "name → number of bridge-concepts referencing that dataset."
        ),
    }


def main() -> None:
    print("Loading BSD corpus...")
    bsd = load_corpus("bsd_rich")
    print(f"  {len(bsd)} records")

    print("Loading modular_forms corpus...")
    modular = load_corpus("modular_forms")
    print(f"  {len(modular)} records")

    print("Loading knots corpus...")
    knot = load_corpus("knots")
    print(f"  {len(knot)} records")

    print("Computing per-domain coverage cells...")
    cells = {}
    cells.update(analyze_bsd(bsd))
    cells.update(analyze_modular(modular))
    cells.update(analyze_knot(knot))

    bridges_summary = load_bridges_summary()

    # Charon-specific per-cell checks
    charon_checks: Dict[str, Dict[str, Any]] = {}
    for cell_id, cell in cells.items():
        domain, obj_type, inv_family, source = cell_id.split("::")
        n = cell["n_objects"]
        miss = cell.get("missingness_rate", 0.0)
        tag = cell.get("coverage_tag", "")
        flags = cell.get("coverage_flags", [])

        charon_checks[cell_id] = {
            "battery_applicable": cell["battery_applicable"],
            "battery_kill_data_available": (
                # Only A149 lattice-walks have battery_sweep_v2 kill outcomes
                "false (battery_sweep_v2 is single-domain A149*)"
            ),
            "real_failures_vs_missing_data": (
                f"missingness={miss:.1%} on key invariants — "
                + ("treat kills as conflated with missingness"
                   if miss > 0.20 else
                   "missingness low; failures interpretable")
            ),
            "cross_domain_links_via_shared_invariant": (
                "modular forms + BSD share L-function structure (a_p, level); "
                "knot + BSD share number-field invariants (nf_discriminant). "
                "Cross-domain bridges are not 1:1 — they project through "
                "shared invariants. Apparent bridges may be artifacts of "
                "which invariants are mutually populated."
            ),
            "single_dataset_dominated": (
                source in {"cremona", "lmfdb", "knotinfo"}
                and (n > 0)
            ),
            "safe_for_ergon": (
                tag in ("dense", "moderate") and
                cell["battery_applicable"] and
                miss < 0.20 and
                n >= 100
            ),
            "low_confidence_reasons": flags,
        }

    honesty_notes = [
        "SCOPE: BSD/modular/knot triple per brief. Genus2/mock_theta/"
        "oeis_sleeping coverage cells deferred — pilots have corpus stats "
        "but not richer feature-level analysis. Quick-survey extension is "
        "feasible (~1h additional).",
        "INCONCLUSIVE_DATA fields (n_claims_generated, n_kills, n_promotes, "
        "n_near_misses) reflect Task A's finding: there is no unified per-"
        "claim ledger across these 6 envs. The cell counts in the brief "
        "schema cannot be populated from persisted data. Coverage map is "
        "structural-side only (corpus available + features present); "
        "kill-side coverage is INCONCLUSIVE.",
        "Coverage tags computed at corpus level: dense (n>=200, no flags), "
        "moderate (30 <= n < 200), thin (n<30), void (n=0), "
        "misleading_dense (n>=30 with one or more of: missingness>20%, "
        "top_value_share>80%, low invariant diversity, low distinct values).",
        "knot corpus has 52 records — borderline thin. Below the 100-record "
        "threshold for 'safe_for_ergon'. Hyperbolic-volume coverage range is "
        "broad but n is dominated by degree_5_plus trace fields per pilot "
        "stats.",
        "modular_forms DB has 7875 records but pilot uses 1000 (12.7% "
        "sample). The pilot's coverage report applies to the sample, not "
        "the full corpus. Coverage scaling is feasible: re-run with the "
        "full DB for stronger coverage claims.",
        "The 'cross_domain_link_count' cell field collapses to an "
        "INCONCLUSIVE proxy: bridges.jsonl gives concept-keyed cross-dataset "
        "links but not per-record cross-domain claim counts. Per-record "
        "cross-domain provenance is not persisted.",
        "Battery applicability is qualitative — based on which standard "
        "invariants exist for each domain (BSD has rank+L1, modular has "
        "weight+a_p, knot has crossing+hyperbolic_volume). The per-falsifier "
        "applicability matrix (does F1 work on knots? does F11 work on "
        "modular? etc.) is NOT in this report — that's a separate task "
        "requiring battery code-walking.",
        "'Safe for Ergon' = (tag ∈ {dense, moderate}) AND battery_applicable "
        "AND missingness<20% AND n>=100. This is a coarse threshold; "
        "Ergon's actual training-grade requirement may differ.",
    ]

    output = {
        "computed_date": date.today().isoformat(),
        "computed_by": "Charon (substrate cartography suite, Task C)",
        "scope": "BSD / modular / knot triple per brief",
        "data_sources": [
            "prometheus_math/databases/bsd_rich.json.gz",
            "prometheus_math/databases/modular_forms.json.gz",
            "prometheus_math/databases/knots.json.gz",
            "cartography/convergence/data/bridges.jsonl",
        ],
        "n_total_objects": len(bsd) + len(modular) + len(knot),
        "cells": cells,
        "charon_per_cell_checks": charon_checks,
        "bridges_cross_dataset_summary": bridges_summary,
        "honesty_notes": honesty_notes,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_json = OUT_DIR / "substrate_coverage_map.json"
    out_json.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {out_json}")

    md = render_md(output)
    out_md = OUT_DIR / "SUBSTRATE_COVERAGE_MAP_REPORT.md"
    out_md.write_text(md, encoding="utf-8")
    print(f"Wrote {out_md}")


def render_md(output: Dict[str, Any]) -> str:
    lines = []
    lines.append("# Substrate Coverage Map (BSD / modular / knot)")
    lines.append("")
    lines.append(f"**Computed:** {output['computed_date']}  ")
    lines.append(f"**By:** {output['computed_by']}  ")
    lines.append(f"**Scope:** {output['scope']}  ")
    lines.append(f"**Total objects analyzed:** {output['n_total_objects']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Coverage cells")
    lines.append("")
    lines.append("| cell | n | tag | flags | missingness | battery_applicable | safe_for_ergon |")
    lines.append("|---|---|---|---|---|---|---|")
    for cell_id, cell in output["cells"].items():
        chk = output["charon_per_cell_checks"][cell_id]
        flags = ", ".join(cell.get("coverage_flags", [])) or "—"
        miss = f"{cell.get('missingness_rate', 0.0):.1%}"
        lines.append(
            f"| {cell_id} | {cell['n_objects']} | "
            f"**{cell.get('coverage_tag', '?')}** | {flags} | "
            f"{miss} | {chk['battery_applicable']} | "
            f"{'✓' if chk['safe_for_ergon'] else '✗'} |"
        )
    lines.append("")

    # Per-cell detail
    lines.append("## Per-cell detail")
    lines.append("")
    for cell_id, cell in output["cells"].items():
        lines.append(f"### {cell_id}")
        lines.append("")
        lines.append(
            f"- n_objects: {cell['n_objects']}, "
            f"tag: **{cell.get('coverage_tag')}**"
        )
        lines.append(f"- missingness: {cell.get('missingness_rate', 0):.1%}")
        if cell.get("coverage_flags"):
            lines.append(f"- flags: {', '.join(cell['coverage_flags'])}")
        lines.append(f"- notes: {cell.get('notes', '')}")
        lines.append("")
        lines.append("Feature completeness:")
        lines.append("")
        lines.append("| feature | n_with | n_missing | distinct | top_share | dominant |")
        lines.append("|---|---|---|---|---|---|")
        for fname, fd in cell.get("feature_completeness", {}).items():
            top = f"{fd.get('top_value_share', 0):.0%}" if fd.get('top_value_share') is not None else "—"
            lines.append(
                f"| {fname} | {fd['n_with']} | {fd['n_missing']} | "
                f"{fd['n_distinct']} | {top} | "
                f"{fd.get('dominant') or '—'} |"
            )
        lines.append("")
        chk = output["charon_per_cell_checks"][cell_id]
        lines.append("Charon checks:")
        for k, v in chk.items():
            if isinstance(v, list):
                v = ", ".join(v) if v else "(none)"
            lines.append(f"- **{k}**: {v}")
        lines.append("")

    # Bridges
    bs = output["bridges_cross_dataset_summary"]
    if "n_bridges" in bs:
        lines.append("## Cross-dataset bridges (from bridges.jsonl)")
        lines.append("")
        lines.append(f"Total bridges: **{bs['n_bridges']}**")
        lines.append("")
        lines.append("Top datasets by bridge-frequency:")
        lines.append("")
        lines.append("| dataset | n_bridges referencing |")
        lines.append("|---|---|")
        for ds, n in bs["by_dataset_freq"].items():
            lines.append(f"| {ds} | {n} |")
        lines.append("")
        lines.append(bs.get("note", ""))
        lines.append("")

    # Honesty
    lines.append("## Honesty notes")
    lines.append("")
    for h in output["honesty_notes"]:
        lines.append(f"- {h}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("— Charon, Task C, " + output["computed_date"])
    return "\n".join(lines)


if __name__ == "__main__":
    main()
