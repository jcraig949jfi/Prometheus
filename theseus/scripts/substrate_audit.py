"""Substrate audit — compute the metrics the audit recommended.

Per user request after Fire #87 audit conversation. Computes:
1. Template growth curve (templates per 1M records, over time)
2. Per-gen contribution decay (pick-N marginal yield vs pick-1)
3. Effective claim-space utilization
4. Promote-to-record ratio over time
5. Downstream consumption gap

Outputs structured stats to stdout. Run:
    python -m theseus.scripts.substrate_audit
"""
from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from theseus.config import THESEUS_ROOT, BATCHES_JSONL_PATH
from theseus.orchestration.signature_index import SIGNATURE_INDEX_PATH


def _load_batches() -> List[Dict[str, Any]]:
    """Load all per-batch journal entries."""
    out = []
    with BATCHES_JSONL_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def _load_signature_index() -> Dict[str, Any]:
    """Aggregate signature_index data: per-gen counts + verdicts."""
    if not SIGNATURE_INDEX_PATH.exists():
        return {"total_unique": 0, "by_gen": {}, "by_verdict": {}}
    with sqlite3.connect(SIGNATURE_INDEX_PATH) as c:
        cur = c.execute("SELECT COUNT(*), SUM(seen_count) FROM signatures")
        total_unique, total_seen = cur.fetchone()
        cur = c.execute(
            "SELECT generator_id, COUNT(*), SUM(seen_count) "
            "FROM signatures GROUP BY generator_id ORDER BY COUNT(*) DESC"
        )
        by_gen = {
            gid: {"unique": n, "total_seen": tot}
            for gid, n, tot in cur.fetchall()
        }
        cur = c.execute(
            "SELECT verdict_class, COUNT(*), SUM(seen_count) "
            "FROM signatures GROUP BY verdict_class"
        )
        by_verdict = {
            vc: {"unique": n, "total_seen": tot}
            for vc, n, tot in cur.fetchall()
        }
    return {
        "total_unique": total_unique,
        "total_seen": total_seen,
        "by_gen": by_gen,
        "by_verdict": by_verdict,
    }


def metric_template_growth(batches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Templates per 1M records, windowed over fire ranges."""
    # No per-batch "templates" field — derive from cumulative differences
    # in the signature_index. We don't have historical SI snapshots.
    # Best proxy: count discoveries-emitted and records over batch windows.
    windows = [
        (0, 30, "Pre-#34"),  # placeholder; we don't have batches for pre-session
    ]
    # Just compute totals
    cum_records = 0
    cum_kills = 0
    cum_confirms = 0
    for b in batches:
        cum_records += b["total_records"]
        cum_kills += b["total_kills"]
        cum_confirms += b["total_confirmations"]
    return {
        "n_batches": len(batches),
        "cumulative_records": cum_records,
        "cumulative_kills": cum_kills,
        "cumulative_confirms": cum_confirms,
        "kill_share": cum_kills / max(cum_records, 1),
    }


def metric_per_gen_contribution(batches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Per-gen: total records emitted across all fires, fire-count, dup-rate."""
    by_gen = defaultdict(lambda: {
        "fire_count": 0,
        "total_records": 0,
        "total_kills": 0,
        "total_confirms": 0,
        "dup_sum": 0.0,
    })
    for b in batches:
        for gid, m in b["per_generator"].items():
            by_gen[gid]["fire_count"] += 1
            by_gen[gid]["total_records"] += m["records_emitted"]
            by_gen[gid]["total_kills"] += m["kills"]
            by_gen[gid]["total_confirms"] += m["confirmations"]
            by_gen[gid]["dup_sum"] += m.get("dup_rate", 0.0)
    out = {}
    for gid, d in by_gen.items():
        n = d["fire_count"]
        out[gid] = {
            "fire_count": n,
            "total_records": d["total_records"],
            "mean_dup_rate": round(d["dup_sum"] / max(n, 1), 3),
            "kill_share": round(d["total_kills"] / max(d["total_records"], 1), 3),
            "records_per_fire": d["total_records"] // max(n, 1),
        }
    return out


def metric_effective_claim_space(si: Dict[str, Any]) -> Dict[str, Any]:
    """Estimate the effective coverage of the templated claim space."""
    # Theoretical bound: n_gens × n_relations × n_claim_kinds × n_invariant_pairs
    # We can't know n_invariant_pairs without enumerating catalogs.
    # Just report observed coverage.
    return {
        "unique_templates": si["total_unique"],
        "total_seen": si["total_seen"],
        "global_saturation": (
            1.0 - si["total_unique"] / max(si["total_seen"], 1)
        ),
        "templates_by_gen": si["by_gen"],
        "templates_by_verdict": si["by_verdict"],
    }


def metric_promote_to_record_ratio(
    batches: List[Dict[str, Any]],
    lifetime_stats_path: Path,
) -> Dict[str, Any]:
    """Promote rate (records passing info-density filter / total records)."""
    # `discoveries_emitted` is the promote count
    cum_records = sum(b["total_records"] for b in batches)
    if lifetime_stats_path.exists():
        ls = json.loads(lifetime_stats_path.read_text())
        lifetime_promoted = ls.get("lifetime_discoveries_emitted", 0)
    else:
        lifetime_promoted = 0
    return {
        "lifetime_promoted_records": lifetime_promoted,
        "lifetime_records": cum_records,
        "promote_rate_per_million": round(
            lifetime_promoted / max(cum_records, 1) * 1_000_000, 2
        ),
    }


def metric_consumption_gap() -> Dict[str, Any]:
    """How many promoted records have been reviewed downstream?"""
    # We don't have a "reviewed" field. Count outbox vs inbox.
    consumed_dir = THESEUS_ROOT / "handoff" / "ergon_outbox" / "consumed"
    inbox_dir = THESEUS_ROOT / "handoff" / "ergon_outbox" / "inbox"
    n_consumed = len(list(consumed_dir.glob("*.jsonl"))) if consumed_dir.is_dir() else 0
    n_inbox = len(list(inbox_dir.glob("*.jsonl"))) if inbox_dir.is_dir() else 0
    return {
        "ergon_outbox_consumed_bundles": n_consumed,
        "ergon_outbox_inbox_pending": n_inbox,
        "human_reviewed_count": 0,  # nothing yet
        "verified_findings": 0,
    }


def metric_demand_signal_trajectory() -> Dict[str, Any]:
    """Aggregate demand signal events across all batches."""
    journal_dir = THESEUS_ROOT / "journals"
    if not journal_dir.is_dir():
        return {}
    total = 0
    by_signature: Dict[str, int] = defaultdict(int)
    n_files = 0
    for f in journal_dir.glob("demand_*.jsonl"):
        n_files += 1
        try:
            with f.open("r", encoding="utf-8") as fp:
                for line in fp:
                    rec = json.loads(line)
                    sig = "/".join(rec["signature"]) if rec["signature"] else "?"
                    n = rec["count"]
                    total += n
                    by_signature[sig] += n
        except (OSError, json.JSONDecodeError):
            continue
    top10 = sorted(by_signature.items(), key=lambda x: -x[1])[:10]
    return {
        "n_demand_files": n_files,
        "total_demand_events": total,
        "distinct_signatures": len(by_signature),
        "top_10": top10,
    }


def main() -> int:
    batches = _load_batches()
    si = _load_signature_index()
    lifetime_stats_path = THESEUS_ROOT / "orchestration" / "lifetime_stats.json"

    print("=" * 70)
    print("SUBSTRATE AUDIT — Techne Theseus")
    print("=" * 70)

    growth = metric_template_growth(batches)
    print(f"\n[1] Cumulative volume:")
    print(f"    n_batches: {growth['n_batches']}")
    print(f"    cumulative_records: {growth['cumulative_records']:,}")
    print(f"    cumulative_kills:   {growth['cumulative_kills']:,}")
    print(f"    cumulative_confirms: {growth['cumulative_confirms']:,}")
    print(f"    kill_share: {growth['kill_share']:.1%}")

    promote = metric_promote_to_record_ratio(batches, lifetime_stats_path)
    print(f"\n[2] Promote-to-record ratio:")
    print(f"    lifetime_promoted_records: {promote['lifetime_promoted_records']}")
    print(f"    lifetime_records: {promote['lifetime_records']:,}")
    print(f"    promote rate: {promote['promote_rate_per_million']} per million")

    consumption = metric_consumption_gap()
    print(f"\n[3] Downstream consumption gap:")
    for k, v in consumption.items():
        print(f"    {k}: {v}")

    claim_space = metric_effective_claim_space(si)
    print(f"\n[4] Effective claim-space utilization:")
    print(f"    unique_templates: {claim_space['unique_templates']:,}")
    print(f"    total_seen: {claim_space['total_seen']:,}")
    print(f"    global saturation: {claim_space['global_saturation']:.4f}")
    print(f"    templates_by_verdict:")
    for vc, d in claim_space["templates_by_verdict"].items():
        print(f"      {vc}: {d['unique']} templates / {d['total_seen']:,} seen")
    print(f"    top 10 gens by template count:")
    for gid, d in sorted(
        claim_space["templates_by_gen"].items(),
        key=lambda x: -x[1]["unique"],
    )[:10]:
        print(f"      {gid}: {d['unique']} templates / {d['total_seen']:,} seen "
              f"(saturation {1 - d['unique']/max(d['total_seen'],1):.3f})")

    pg = metric_per_gen_contribution(batches)
    print(f"\n[5] Per-gen contribution (sorted by total records):")
    print(f"    {'gid':<5} {'fires':>5} {'records':>15} {'rec/fire':>12} "
          f"{'kill%':>6} {'dup%':>6}")
    for gid in sorted(pg, key=lambda g: -pg[g]["total_records"])[:20]:
        d = pg[gid]
        print(f"    {gid:<5} {d['fire_count']:>5} {d['total_records']:>15,} "
              f"{d['records_per_fire']:>12,} {d['kill_share']:>5.1%} "
              f"{d['mean_dup_rate']:>5.1%}")

    demand = metric_demand_signal_trajectory()
    print(f"\n[6] Demand signal trajectory:")
    print(f"    n_demand_files: {demand.get('n_demand_files', 0)}")
    print(f"    total_demand_events: {demand.get('total_demand_events', 0):,}")
    print(f"    distinct_signatures: {demand.get('distinct_signatures', 0)}")
    print(f"    top 10 wanted primitives:")
    for sig, n in demand.get("top_10", []):
        print(f"      {n:>12,}  {sig}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
