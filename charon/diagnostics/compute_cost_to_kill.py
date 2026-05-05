"""charon.diagnostics.compute_cost_to_kill

Task B of the Substrate Cartography Suite (Charon, 2026-05-05).

Question: empirical wall-clock + oracle-call distribution per (operator class,
domain), with tar-pit identification.

DATA REALITY (substrate-grade):
-------------------------------
Survey 2026-05-05 found:
  - The 6 cross-domain pilot files (BSD, modular, knot, genus2, mock_theta,
    oeis_sleeping) have ZERO `elapsed_seconds` telemetry. n_episodes is set
    but no timing is persisted.
  - The Σ-kernel SQLite DBs have 5 demo claims, all with verdict_runtime_ms=0.
  - Ergon a149 trial JSONs have `elapsed_s` per (config, seed) — but at
    the trial level, not per operator-class call.
  - Lehmer/discovery_v2 pipeline persists per-(arm, seed) `elapsed_seconds`
    + `operator_call_counts`.
  - Several special-purpose pilots (v2_anti_elitist, v3_root_space,
    native_kill_vector, catalog_seeded) have some `elapsed_s`.
  - `oracle_calls` is NEVER persisted in any of the JSON files surveyed.
    `arsenal_meta.py` declares theoretical max_oracle_calls per callable;
    actual oracle calls fired at runtime are not logged.

The brief's "per_cell" schema (structural__BSD with cpu_seconds + io_seconds
+ oracle_calls percentiles + tar_pits) is INCONCLUSIVE_DATA for almost every
cell. The honest output is:
  - Where timing exists: amortized per-episode cost at the available
    granularity (per arm-config or per-trial).
  - Where it doesn't: INCONCLUSIVE_DATA flag. This is itself the substrate-
    grade finding.

What's measurable and what isn't:
  - Per-class wall-clock cost-to-kill: NOT MEASURABLE from persisted data.
    Ergon's per-seed elapsed_s is per-(config, seed), not per-call.
  - Per-domain wall-clock-per-episode: PARTIALLY MEASURABLE for Lehmer
    + a149 (Ergon). Not measurable for any of the 6 cross-domain envs.
  - IO vs CPU breakdown: NOT MEASURABLE. No timing source separates them.
  - Oracle-call counts: NOT MEASURABLE. Not persisted anywhere.
  - Tar pits: identifiable as outliers in Ergon a149 elapsed_s; not
    identifiable for cross-domain envs.

The substrate's instrumentation gap is the load-bearing observation here.
"""
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[2]
PMATH = REPO / "prometheus_math"
ETRIALS = REPO / "ergon" / "learner" / "trials"
OUT_DIR = REPO / "charon" / "diagnostics"

# Pilots and their domain/pipeline attribution
PIPELINE_FILES = {
    # Cross-domain learning pilots — NO timing
    "bsd_rank__cross_domain_pilot": {
        "path": PMATH / "_bsd_rank_pilot_run.json",
        "domain": "BSD", "operator_vocab": "random/reinforce/majority",
        "expects_timing": False,
    },
    "modular_form__cross_domain_pilot": {
        "path": PMATH / "_modular_form_pilot.json",
        "domain": "modular", "operator_vocab": "random/reinforce/ppo",
        "expects_timing": False,
    },
    "knot__cross_domain_pilot": {
        "path": PMATH / "_knot_pilot.json",
        "domain": "knot", "operator_vocab": "random/reinforce/ppo",
        "expects_timing": False,
    },
    "genus2__cross_domain_pilot": {
        "path": PMATH / "_genus2_pilot.json",
        "domain": "genus2", "operator_vocab": "random/reinforce",
        "expects_timing": False,
    },
    "mock_theta__cross_domain_pilot": {
        "path": PMATH / "_mock_theta_pilot.json",
        "domain": "mock_theta", "operator_vocab": "random/reinforce/ppo",
        "expects_timing": False,
    },
    "oeis_sleeping__cross_domain_pilot": {
        "path": PMATH / "_oeis_sleeping_pilot.json",
        "domain": "oeis_sleeping", "operator_vocab": "random/growth",
        "expects_timing": False,
    },
    # Lehmer/discovery_v2 pipeline — has timing
    "lehmer__discovery_v2": {
        "path": PMATH / "_discovery_v2_pilot.json",
        "domain": "lehmer", "operator_vocab": "coefficient_mutators_x7",
        "expects_timing": True,
    },
    # Special-purpose pilots
    "lehmer__v2_anti_elitist": {
        "path": PMATH / "_v2_anti_elitist_pilot.json",
        "domain": "lehmer", "operator_vocab": "strategy_arms",
        "expects_timing": True,
    },
    "lehmer__v3_root_space": {
        "path": PMATH / "_v3_root_space_pilot.json",
        "domain": "lehmer", "operator_vocab": "root_space",
        "expects_timing": True,
    },
}

# Ergon a149 trial JSONs (per-config, per-seed elapsed_s)
ERGON_TRIALS = [
    "trial_3_iter28_a149_results.json",
    "trial_3_iter31_a149_results.json",
    "trial_3_iter18_results.json",  # synthetic obstruction
    "trial_3_iter25_results.json",
    "trial_3_iter26_results.json",
    "trial_3_iter27_results.json",
]


def extract_timing(pipeline_name: str, info: Dict[str, Any]) -> Dict[str, Any]:
    """Extract timing telemetry from a pilot file. Returns INCONCLUSIVE if none."""
    path = info["path"]
    if not path.exists():
        return {
            "pipeline": pipeline_name,
            "data_quality": "INCONCLUSIVE_DATA",
            "reason": f"file not found: {path}",
            "domain": info["domain"],
        }
    try:
        d = json.load(path.open(encoding="utf-8"))
    except Exception as e:
        return {
            "pipeline": pipeline_name,
            "data_quality": "INCONCLUSIVE_DATA",
            "reason": f"unable to parse: {e}",
            "domain": info["domain"],
        }

    elapsed_records = []
    n_episodes_records = []

    # discovery_v2 shape
    if "results" in d and isinstance(d["results"], list):
        for r in d["results"]:
            if "elapsed_seconds" in r:
                elapsed_records.append({
                    "elapsed_s": r["elapsed_seconds"],
                    "n_episodes": r.get("n_episodes"),
                    "arm": r.get("arm"),
                    "seed": r.get("seed"),
                    "operator_call_counts": r.get("operator_call_counts", {}),
                })

    # cells/total_elapsed_s shape (v2_anti_elitist, v3_root_space)
    if "total_elapsed_s" in d:
        total = d["total_elapsed_s"]
        n_eps = d.get("total_episodes") or d.get("n_samples_per_seed")
        if "cells" in d and isinstance(d["cells"], dict):
            for cell_id, cell in d["cells"].items():
                cell_n = cell.get("n_episodes") or cell.get("n_samples")
                cell_elapsed = cell.get("elapsed_s")
                if cell_elapsed is not None:
                    elapsed_records.append({
                        "elapsed_s": cell_elapsed,
                        "n_episodes": cell_n,
                        "arm": cell_id,
                        "seed": None,
                        "operator_call_counts": {},
                    })

    # cross-domain pilot shape (no timing)
    if not elapsed_records:
        n_eps = d.get("n_episodes")
        if n_eps:
            return {
                "pipeline": pipeline_name,
                "data_quality": "INCONCLUSIVE_DATA",
                "reason": (
                    f"no elapsed_seconds telemetry; n_episodes={n_eps} runs "
                    f"completed but timing was not persisted"
                ),
                "domain": info["domain"],
                "n_episodes_run_aggregate": n_eps,
            }
        return {
            "pipeline": pipeline_name,
            "data_quality": "INCONCLUSIVE_DATA",
            "reason": "no parseable telemetry",
            "domain": info["domain"],
        }

    # Compute amortized seconds-per-episode
    per_arm = defaultdict(list)
    for r in elapsed_records:
        if r["n_episodes"]:
            sec_per_ep = r["elapsed_s"] / r["n_episodes"]
            per_arm[r["arm"]].append({"sec_per_ep": sec_per_ep, **r})

    arm_summaries = {}
    for arm, recs in per_arm.items():
        secs = [r["sec_per_ep"] for r in recs]
        if not secs:
            continue
        arm_summaries[arm] = {
            "n": len(secs),
            "median_sec_per_ep": statistics.median(secs),
            "p95_sec_per_ep": _percentile(secs, 0.95) if len(secs) >= 5 else None,
            "min_sec_per_ep": min(secs),
            "max_sec_per_ep": max(secs),
            "raw_records": recs,
        }

    return {
        "pipeline": pipeline_name,
        "data_quality": "high" if len(elapsed_records) >= 9 else (
            "medium" if len(elapsed_records) >= 4 else "low"
        ),
        "n_observations": len(elapsed_records),
        "domain": info["domain"],
        "operator_vocab": info["operator_vocab"],
        "per_arm": arm_summaries,
        "raw": elapsed_records,
    }


def _percentile(vals: List[float], p: float) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    k = int(len(s) * p)
    return s[min(k, len(s) - 1)]


def extract_ergon_trials() -> Dict[str, Any]:
    """Extract per-config elapsed_s from Ergon a149 trial results."""
    out: Dict[str, Any] = {}
    for fname in ERGON_TRIALS:
        path = ETRIALS / fname
        if not path.exists():
            continue
        try:
            d = json.load(path.open(encoding="utf-8"))
        except Exception as e:
            continue
        # The iter28/iter31 a149 results are dict[config_name -> List[seed_records]]
        # iter25/iter26/iter27 may have different shape — try both
        if isinstance(d, dict) and any(
            isinstance(v, list) for v in d.values()
        ):
            for config_name, seed_records in d.items():
                if not isinstance(seed_records, list):
                    continue
                secs = []
                neps_list = []
                for sr in seed_records:
                    if isinstance(sr, dict) and "elapsed_s" in sr:
                        secs.append(sr["elapsed_s"])
                        neps_list.append(sr.get("n_episodes"))
                if secs:
                    sec_per_ep = [
                        s / n for s, n in zip(secs, neps_list) if n
                    ]
                    out[f"{path.stem}::{config_name}"] = {
                        "trial": path.stem,
                        "config": config_name,
                        "n_seeds": len(secs),
                        "elapsed_s_per_seed": secs,
                        "n_episodes_per_seed": neps_list,
                        "sec_per_ep_per_seed": sec_per_ep,
                        "median_sec_per_ep": (
                            statistics.median(sec_per_ep) if sec_per_ep else None
                        ),
                        "max_sec_per_ep": (
                            max(sec_per_ep) if sec_per_ep else None
                        ),
                    }
    return out


def load_arsenal_theoretical_bounds() -> Dict[str, Any]:
    """Pull theoretical max_seconds / max_oracle_calls from arsenal_meta."""
    try:
        from prometheus_math.arsenal_meta import ARSENAL_REGISTRY
    except Exception as e:
        return {"error": f"arsenal_meta import failed: {e}"}
    by_category = defaultdict(list)
    untagged = []
    for ref, meta in ARSENAL_REGISTRY.items():
        if not meta.cost:
            continue
        secs = meta.cost.get("max_seconds")
        oracles = meta.cost.get("max_oracle_calls")
        item = {
            "ref": ref,
            "max_seconds": secs,
            "max_oracle_calls": oracles,
            "category": meta.category,
            "equivalence_class": meta.equivalence_class,
        }
        if meta.category:
            by_category[meta.category].append(item)
        else:
            untagged.append(item)

    summary = {}
    for cat, items in by_category.items():
        secs = [i["max_seconds"] for i in items if i["max_seconds"]]
        oracles = [i["max_oracle_calls"] for i in items if i["max_oracle_calls"]]
        summary[cat] = {
            "n_callables": len(items),
            "max_seconds_distribution": {
                "min": min(secs) if secs else None,
                "median": statistics.median(secs) if secs else None,
                "max": max(secs) if secs else None,
            },
            "max_oracle_calls_distribution": {
                "min": min(oracles) if oracles else None,
                "median": statistics.median(oracles) if oracles else None,
                "max": max(oracles) if oracles else None,
            },
        }
    return {
        "n_callables_with_cost_metadata": sum(
            len(items) for items in by_category.values()
        ) + len(untagged),
        "by_category": summary,
        "n_untagged": len(untagged),
        "note": (
            "These are THEORETICAL upper bounds declared via @arsenal_op decorator. "
            "Actual runtime cost is not logged at the arsenal-callable granularity. "
            "Useful for budget-based gating but NOT for empirical cost-to-kill."
        ),
    }


def main() -> None:
    print("Extracting pilot telemetry...")
    pipelines = {}
    for pname, info in PIPELINE_FILES.items():
        pipelines[pname] = extract_timing(pname, info)

    print("Extracting Ergon a149 trial timing...")
    ergon = extract_ergon_trials()

    print("Loading arsenal theoretical bounds...")
    arsenal = load_arsenal_theoretical_bounds()

    # Telemetry completeness summary
    completeness = {
        "n_pilots_with_timing": sum(
            1 for p in pipelines.values() if p.get("data_quality") not in
            ("INCONCLUSIVE_DATA", None)
        ),
        "n_pilots_inconclusive": sum(
            1 for p in pipelines.values() if p.get("data_quality") == "INCONCLUSIVE_DATA"
        ),
        "n_ergon_configs_with_timing": len(ergon),
        "domains_with_no_timing": sorted({
            p["domain"] for p in pipelines.values()
            if p.get("data_quality") == "INCONCLUSIVE_DATA"
        }),
        "domains_with_some_timing": sorted({
            p["domain"] for p in pipelines.values()
            if p.get("data_quality") not in ("INCONCLUSIVE_DATA", None)
        }),
        "oracle_calls_persisted_anywhere": False,  # confirmed by survey
        "io_vs_cpu_breakdown_persisted_anywhere": False,
    }

    # Tar pits — Ergon a149 max_sec_per_ep where it spikes
    tar_pits = []
    for k, v in ergon.items():
        if v.get("max_sec_per_ep") and v.get("median_sec_per_ep"):
            ratio = v["max_sec_per_ep"] / v["median_sec_per_ep"]
            if ratio > 1.5:
                tar_pits.append({
                    "config": k,
                    "median_sec_per_ep": v["median_sec_per_ep"],
                    "max_sec_per_ep": v["max_sec_per_ep"],
                    "ratio": ratio,
                    "note": "max/median > 1.5 — possible tar-pit seed",
                })

    honesty_notes = [
        "DATA REALITY: the substrate persists wall-clock telemetry for "
        "a149/Lehmer pipelines but NOT for the 6 cross-domain envs (BSD, "
        "modular, knot, genus2, mock_theta, oeis_sleeping). For those, "
        "n_episodes is recorded but elapsed_seconds is not. INCONCLUSIVE "
        "flagged per-domain.",
        "Per-class cost (structural / symbolic / etc.) is NOT directly "
        "measurable: Ergon's elapsed_s is at the (config, seed) level, "
        "not per-call. Amortized per-class cost would assume uniform "
        "per-call cost across classes within a config — false (different "
        "classes do different work). Reporting per-config amortized-per-"
        "episode cost is the granularity available; class breakdown is "
        "INCONCLUSIVE without instrumentation work.",
        "IO-bound vs CPU-bound separation: NOT MEASURABLE. No timing "
        "source in the surveyed data separates them. The brief's "
        "io_seconds field is INCONCLUSIVE everywhere.",
        "Oracle-call counts: NOT PERSISTED ANYWHERE. arsenal_meta.py "
        "declares theoretical max_oracle_calls per callable but actual "
        "fired-counts at runtime are not logged. INCONCLUSIVE for all "
        "cells.",
        "99th-percentile cost-to-kill: requires n>>30 per cell. "
        "Available data: max ~12 obs per Ergon config (3 seeds × 4 "
        "configs); Lehmer discovery_v2 has 6 records. None reach n>=30 "
        "for stable p99.",
        "Tar-pit identification scoped to Ergon a149 timing where "
        "max/median > 1.5. Cross-domain tar-pit detection INCONCLUSIVE.",
        "arsenal_meta theoretical bounds are useful for budget-based "
        "gating in the kernel but should not be conflated with empirical "
        "cost — they are designer-declared upper bounds, not measurements.",
        "The substrate-grade implication: Ergon's scheduler cannot make "
        "data-driven cost-aware compute allocation across the 6 cross-"
        "domain envs without first instrumenting elapsed_seconds (and "
        "oracle_calls) into the pilot run loop. ~1 day of engineering "
        "to add `time.perf_counter()` brackets and `oracle_calls` "
        "counter in each run script. Until then: cost-aware scheduling "
        "is structurally aspirational, not empirically grounded.",
    ]

    output = {
        "computed_date": date.today().isoformat(),
        "computed_by": "Charon (substrate cartography suite, Task B)",
        "data_sources": [
            "prometheus_math/_*pilot*.json (10 surveyed)",
            "ergon/learner/trials/*results*.json (6 surveyed)",
            "prometheus_math/arsenal_meta.py (theoretical bounds)",
            "sigma_kernel/*.db (5 demo claims, runtime_ms=0)",
        ],
        "telemetry_completeness": completeness,
        "per_pipeline": pipelines,
        "ergon_a149_per_config": ergon,
        "arsenal_theoretical_bounds": arsenal,
        "tar_pits": tar_pits,
        "honesty_notes": honesty_notes,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_json = OUT_DIR / "cost_to_kill_distribution.json"
    out_json.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {out_json}")

    md = render_md(output)
    out_md = OUT_DIR / "COST_TO_KILL_REPORT.md"
    out_md.write_text(md, encoding="utf-8")
    print(f"Wrote {out_md}")


def render_md(output: Dict[str, Any]) -> str:
    lines = []
    lines.append("# Cost-to-Kill Cartography")
    lines.append("")
    lines.append(f"**Computed:** {output['computed_date']}  ")
    lines.append(f"**By:** {output['computed_by']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## TL;DR")
    lines.append("")
    c = output["telemetry_completeness"]
    lines.append(
        f"- {c['n_pilots_inconclusive']} of {c['n_pilots_with_timing'] + c['n_pilots_inconclusive']} "
        f"surveyed pilots have ZERO `elapsed_seconds` telemetry."
    )
    lines.append(
        f"- Domains with no timing data persisted: "
        f"`{c['domains_with_no_timing']}`"
    )
    lines.append(
        f"- Domains with at least some timing: "
        f"`{c['domains_with_some_timing']}`"
    )
    lines.append(
        f"- Oracle-call counts persisted anywhere: "
        f"**{c['oracle_calls_persisted_anywhere']}**"
    )
    lines.append(
        f"- IO-bound vs CPU-bound separation persisted anywhere: "
        f"**{c['io_vs_cpu_breakdown_persisted_anywhere']}**"
    )
    lines.append("")
    lines.append(
        "**Substrate-grade negative**: Ergon's scheduler cannot do data-driven "
        "cost-aware allocation across the 6 cross-domain envs without first "
        "instrumenting `elapsed_seconds` + `oracle_calls` in the pilot run "
        "loops. The `per_cell` schema in the brief (cpu_seconds, io_seconds, "
        "oracle_calls percentiles, tar_pits per (operator, domain)) is "
        "INCONCLUSIVE_DATA for almost every cell. The honest output is the "
        "instrumentation gap itself."
    )
    lines.append("")

    # Per-pipeline summary
    lines.append("## Per-pipeline telemetry")
    lines.append("")
    lines.append("| pipeline | domain | data_quality | n_obs | median sec/ep | reason |")
    lines.append("|---|---|---|---|---|---|")
    for pname, p in output["per_pipeline"].items():
        if p.get("data_quality") == "INCONCLUSIVE_DATA":
            lines.append(
                f"| {pname} | {p.get('domain')} | INCONCLUSIVE_DATA | 0 | — | "
                f"{p.get('reason', '')} |"
            )
        else:
            # find median across arms
            med = None
            arm_meds = [a["median_sec_per_ep"] for a in p.get("per_arm", {}).values()
                        if a.get("median_sec_per_ep")]
            if arm_meds:
                med = statistics.median(arm_meds)
            lines.append(
                f"| {pname} | {p.get('domain')} | {p['data_quality']} | "
                f"{p.get('n_observations', 0)} | "
                f"{med:.4f} | per-arm in JSON |"
            )
    lines.append("")

    # Per-arm detail for pipelines with data
    lines.append("## Per-arm detail (where timing exists)")
    lines.append("")
    for pname, p in output["per_pipeline"].items():
        if p.get("data_quality") == "INCONCLUSIVE_DATA":
            continue
        if not p.get("per_arm"):
            continue
        lines.append(f"### {pname} ({p.get('domain')})")
        lines.append("")
        lines.append(f"Operator vocab: `{p.get('operator_vocab')}`")
        lines.append("")
        lines.append("| arm | n | median sec/ep | min | max | p95 |")
        lines.append("|---|---|---|---|---|---|")
        for arm, a in p["per_arm"].items():
            p95 = f"{a['p95_sec_per_ep']:.4f}" if a.get("p95_sec_per_ep") else "n<5"
            lines.append(
                f"| {arm} | {a['n']} | {a['median_sec_per_ep']:.4f} | "
                f"{a['min_sec_per_ep']:.4f} | {a['max_sec_per_ep']:.4f} | {p95} |"
            )
        lines.append("")

    # Ergon
    lines.append("## Ergon a149 trials — per-config wall-clock")
    lines.append("")
    if not output["ergon_a149_per_config"]:
        lines.append("(no Ergon trial timing extracted)")
    else:
        lines.append("| config | n_seeds | median sec/ep | max sec/ep | tar-pit ratio |")
        lines.append("|---|---|---|---|---|")
        for k, v in output["ergon_a149_per_config"].items():
            if v.get("median_sec_per_ep") is None:
                continue
            ratio = (
                v["max_sec_per_ep"] / v["median_sec_per_ep"]
                if v["median_sec_per_ep"] else None
            )
            ratio_s = f"{ratio:.2f}×" if ratio else "—"
            lines.append(
                f"| {k} | {v['n_seeds']} | "
                f"{v['median_sec_per_ep']:.4f} | "
                f"{v['max_sec_per_ep']:.4f} | {ratio_s} |"
            )
    lines.append("")

    # Tar pits
    lines.append("## Tar pits")
    lines.append("")
    if output["tar_pits"]:
        lines.append("Configs with max/median > 1.5× — candidate tar-pit seeds:")
        lines.append("")
        for tp in output["tar_pits"]:
            lines.append(
                f"- {tp['config']}: median={tp['median_sec_per_ep']:.4f}s, "
                f"max={tp['max_sec_per_ep']:.4f}s, ratio={tp['ratio']:.2f}×"
            )
    else:
        lines.append("(none flagged at 1.5× threshold)")
    lines.append("")

    # Arsenal bounds
    lines.append("## Arsenal theoretical bounds (from `arsenal_meta.py`)")
    lines.append("")
    arsenal = output["arsenal_theoretical_bounds"]
    if "error" in arsenal:
        lines.append(f"(error: {arsenal['error']})")
    else:
        lines.append(
            f"- {arsenal['n_callables_with_cost_metadata']} arsenal callables "
            f"have cost metadata declared."
        )
        lines.append("")
        lines.append("| category | n callables | median max_sec | median max_oracle |")
        lines.append("|---|---|---|---|")
        for cat, info in arsenal["by_category"].items():
            sec_med = info["max_seconds_distribution"].get("median")
            ora_med = info["max_oracle_calls_distribution"].get("median")
            sec_s = f"{sec_med:.3f}s" if sec_med is not None else "—"
            ora_s = f"{ora_med}" if ora_med is not None else "—"
            lines.append(f"| {cat} | {info['n_callables']} | {sec_s} | {ora_s} |")
        lines.append("")
        lines.append(arsenal.get("note", ""))
    lines.append("")

    lines.append("## Honesty notes")
    lines.append("")
    for h in output["honesty_notes"]:
        lines.append(f"- {h}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("— Charon, Task B, " + output["computed_date"])
    return "\n".join(lines)


if __name__ == "__main__":
    main()
