"""
Icarus kill-path clustering.

Per the 2026-05-28 review point #3: a cycle is too local a unit of memory;
wisdom.md is too mushy. The right unit is the kill-path CLUSTER -- a group of
cycles that failed (or promoted-with-debt) under the same failure signature.

Borrows the idea from Harmonia's nulls/ + retraction registry. Mines the
training_stream.jsonl (one typed training object per cycle) and groups by
(failure_class, failure_subclass). Emits KILL_CLUSTER objects:

  KILL_CLUSTER: contract_alignment_loss
  Observed cycles: 14, 22, 31
  Trigger: batch filtering or skipping
  Symptom: output no longer positionally corresponds to input
  Survives: single-problem tests, unordered aggregate tests
  Killed by: cardinality preservation, trace alignment
  Recommended next move: explicit ResultEnvelope per input item

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

STREAM = Path(r"D:\Prometheus\agents\icarus\state\training_stream.jsonl")
CLUSTERS_OUT = Path(r"D:\Prometheus\agents\icarus\state\kill_clusters.json")
CLUSTERS_MD = Path(r"D:\Prometheus\agents\icarus\wisdom\kill_clusters.md")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_stream() -> list[dict]:
    if not STREAM.exists():
        return []
    rows = []
    for line in STREAM.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def build_clusters() -> dict:
    """Group training objects by (failure_class, failure_subclass). Only
    non-'none' failure classes form clusters. Returns a summary dict and
    writes kill_clusters.json + kill_clusters.md."""
    rows = _load_stream()
    groups: dict[tuple, list[dict]] = defaultdict(list)

    for r in rows:
        fc = r.get("failure_class", "none")
        if fc in ("none",):
            continue
        fsc = r.get("failure_subclass", "none")
        groups[(fc, fsc)].append(r)

    clusters = []
    for (fc, fsc), members in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        cycles = sorted({m.get("cycle") for m in members if m.get("cycle") is not None})
        # Aggregate the enriched survivor / next-move hints across members
        survivors = [m.get("nearby_survivor") for m in members if m.get("nearby_survivor")]
        repr_hints = [m.get("representation_change_hint") for m in members
                      if m.get("representation_change_hint")]
        regression_tests = [m.get("regression_test_to_write") for m in members
                            if m.get("regression_test_to_write")]
        tier_risks = sorted({t for m in members for t in (m.get("future_tier_risk") or [])})
        proposal_types = sorted({m.get("proposal_type") for m in members if m.get("proposal_type")})
        detected_by = sorted({m.get("detected_by") for m in members if m.get("detected_by")})

        clusters.append({
            "cluster_id": f"{fc}/{fsc}",
            "failure_class": fc,
            "failure_subclass": fsc,
            "count": len(members),
            "observed_cycles": cycles,
            "detected_by": detected_by,
            "proposal_types": proposal_types,
            "future_tier_risk": tier_risks,
            "nearby_survivors": _dedupe(survivors)[:5],
            "representation_change_hints": _dedupe(repr_hints)[:5],
            "recommended_regression_tests": _dedupe(regression_tests)[:5],
            "updated_at": _now_iso(),
        })

    summary = {
        "total_clusters": len(clusters),
        "total_failures_analyzed": sum(c["count"] for c in clusters),
        "clusters": clusters,
        "generated_at": _now_iso(),
    }

    try:
        CLUSTERS_OUT.parent.mkdir(parents=True, exist_ok=True)
        CLUSTERS_OUT.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    except Exception:
        pass

    _write_markdown(clusters)
    return summary


def _dedupe(items: list) -> list:
    seen = set()
    out = []
    for x in items:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _write_markdown(clusters: list[dict]) -> None:
    lines = [
        "# Icarus Kill-Path Clusters",
        "",
        f"Generated: {_now_iso()}",
        f"Clusters: {len(clusters)}",
        "",
        "The unit of failure memory: groups of cycles that failed under the "
        "same signature. Consult before proposing a change adjacent to a "
        "listed cluster.",
        "",
    ]
    for c in clusters:
        lines.append(f"## KILL_CLUSTER: {c['cluster_id']}")
        lines.append("")
        lines.append(f"- **Count**: {c['count']}")
        lines.append(f"- **Observed cycles**: {c['observed_cycles']}")
        lines.append(f"- **Detected by**: {', '.join(c['detected_by']) or 'unknown'}")
        lines.append(f"- **Proposal types**: {', '.join(c['proposal_types']) or 'unknown'}")
        lines.append(f"- **Future tier risk**: {', '.join(c['future_tier_risk']) or 'none recorded'}")
        if c["nearby_survivors"]:
            lines.append(f"- **Nearby survivors** (what would have worked):")
            for s in c["nearby_survivors"]:
                lines.append(f"    - {s}")
        if c["recommended_regression_tests"]:
            lines.append(f"- **Recommended regression tests**:")
            for t in c["recommended_regression_tests"]:
                lines.append(f"    - {t}")
        if c["representation_change_hints"]:
            lines.append(f"- **Representation change hints**:")
            for h in c["representation_change_hints"]:
                lines.append(f"    - {h}")
        lines.append("")
    try:
        CLUSTERS_MD.parent.mkdir(parents=True, exist_ok=True)
        CLUSTERS_MD.write_text("\n".join(lines), encoding="utf-8")
    except Exception:
        pass


if __name__ == "__main__":
    s = build_clusters()
    print(json.dumps({"total_clusters": s["total_clusters"],
                      "total_failures": s["total_failures_analyzed"]}, indent=2))
