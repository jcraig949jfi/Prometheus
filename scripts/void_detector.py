"""CLI for the mutation-lattice void detector (SelfImprovingDaemon v2d).

Usage:
    python scripts/void_detector.py list                  # all voids, ranked
    python scripts/void_detector.py list --json           # raw JSON
    python scripts/void_detector.py for-agent <name>      # voids targeting an agent
    python scripts/void_detector.py summary               # one-line health
    python scripts/void_detector.py demo                  # seed synthetic registry,
                                                          # run detection, then revert
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_THIS = Path(__file__).resolve()
REPO_ROOT = _THIS.parents[1]
sys.path.insert(0, str(REPO_ROOT))

from agents._shared.void_detector import (
    detect_voids, voids_for_agent, summary, Void,
)
from agents._shared.mutation_registry import (
    record_kept_mutation, query_borrowable_mutations, registry_stats,
    DEFAULT_REGISTRY_PATH,
)
from dataclasses import asdict


def _print_void_table(voids: list[Void]) -> None:
    if not voids:
        print("(no voids detected — registry may be empty or no compatible neighbors found)")
        return
    print(f"{'#':>3} {'conf':>5} {'pred d':>7} {'adaptation':<28} {'target shape':<60}")
    print("-" * 110)
    for i, v in enumerate(voids[:50], 1):
        shape = f"traits={v.target_agent_traits[:3]}{'...' if len(v.target_agent_traits) > 3 else ''} "
        shape += f"failures={v.target_failure_modes[:2]}{'...' if len(v.target_failure_modes) > 2 else ''}"
        print(f"{i:>3} {v.confidence:>5.2f} {v.predicted_delta_composite:>+7.2f} "
              f"{v.adaptation_name[:28]:<28} {shape[:60]:<60}")
        print(f"    {v.rationale}")


def cmd_list(args):
    voids = detect_voids(min_confidence=args.min_confidence,
                         max_voids=args.limit)
    if args.json:
        print(json.dumps([asdict(v) for v in voids], indent=2))
    else:
        _print_void_table(voids)


def cmd_for_agent(args):
    if not args.traits:
        print("error: --traits is required (comma-separated list)", file=sys.stderr)
        return 1
    traits = [t.strip() for t in args.traits.split(",") if t.strip()]
    failures = [f.strip() for f in (args.failures or "").split(",") if f.strip()]
    voids = voids_for_agent(agent_traits=traits, current_failure_modes=failures,
                            min_confidence=args.min_confidence)
    print(f"Voids targeting agent='{args.agent_name}' "
          f"(traits={traits}, failures={failures}): {len(voids)}")
    _print_void_table(voids)


def cmd_summary(args):
    s = summary()
    print(json.dumps(s, indent=2))


def cmd_demo(args):
    """Seed synthetic registry entries, run detection, print results, revert."""
    snapshot_path = None
    if DEFAULT_REGISTRY_PATH.exists():
        snapshot_path = DEFAULT_REGISTRY_PATH.with_suffix(".jsonl.demo_backup")
        DEFAULT_REGISTRY_PATH.rename(snapshot_path)
    try:
        now = datetime.now(timezone.utc).isoformat()
        seeds = [
            dict(agent_name="AgentA",
                 adaptation_name="DROP_MTIME_CACHE",
                 applied_at=now + "-A1",
                 baseline_composite=0.20, post_composite=0.50,
                 delta_per_axis={"null_rate": -0.30, "diversity": 0.10},
                 agent_traits=["daemon", "scour_based", "mtime_cached"],
                 addresses_failure_modes=["high_null_rate"],
                 stagnation_signature={}, module_source="demo:AgentA",
                 cost="one_tick", reversibility="manual_via_revert"),
            dict(agent_name="AgentB",
                 adaptation_name="DROP_MTIME_CACHE",
                 applied_at=now + "-B1",
                 baseline_composite=0.25, post_composite=0.45,
                 delta_per_axis={"null_rate": -0.25, "diversity": 0.05},
                 agent_traits=["daemon", "scour_based", "mtime_cached", "http_fetcher"],
                 addresses_failure_modes=["high_null_rate"],
                 stagnation_signature={}, module_source="demo:AgentB",
                 cost="one_tick", reversibility="manual_via_revert"),
            dict(agent_name="AgentA",
                 adaptation_name="EXPAND_PATHS",
                 applied_at=now + "-A2",
                 baseline_composite=0.30, post_composite=0.60,
                 delta_per_axis={"null_rate": -0.20, "diversity": 0.20},
                 agent_traits=["daemon", "scour_based", "mtime_cached"],
                 addresses_failure_modes=["high_null_rate"],
                 stagnation_signature={}, module_source="demo:AgentA",
                 cost="one_tick", reversibility="manual_via_revert"),
            dict(agent_name="AgentC",
                 adaptation_name="SPAWN_SIBLING",
                 applied_at=now + "-C1",
                 baseline_composite=0.20, post_composite=0.55,
                 delta_per_axis={"diversity": 0.20, "novelty": 0.15},
                 agent_traits=["daemon", "queue_consumer"],
                 addresses_failure_modes=["recursive_drift"],
                 stagnation_signature={}, module_source="demo:AgentC",
                 cost="high", reversibility="manual_via_revert"),
        ]
        for s in seeds:
            record_kept_mutation(**s)

        print("=== Seeded registry ===")
        print(json.dumps(registry_stats(), indent=2))
        print()
        print("=== All voids detected (Type A: interpolation) ===")
        voids = detect_voids()
        _print_void_table(voids)
        print()
        print("=== Voids targeting a hypothetical 'AgentBPrime' "
              "(traits = AgentB + extra; failures = high_null_rate) ===")
        agent_voids = voids_for_agent(
            agent_traits=["daemon", "scour_based", "mtime_cached", "http_fetcher", "json_emitter"],
            current_failure_modes=["high_null_rate"],
        )
        _print_void_table(agent_voids)
    finally:
        if DEFAULT_REGISTRY_PATH.exists():
            DEFAULT_REGISTRY_PATH.unlink()
        if snapshot_path and snapshot_path.exists():
            snapshot_path.rename(DEFAULT_REGISTRY_PATH)


def main():
    ap = argparse.ArgumentParser(description="Mutation-lattice void detector (v2d)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="list all voids ranked by evidence")
    p_list.add_argument("--limit", type=int, default=50)
    p_list.add_argument("--min-confidence", type=float, default=0.0)
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_agent = sub.add_parser("for-agent", help="voids targeting a specific agent")
    p_agent.add_argument("agent_name")
    p_agent.add_argument("--traits", required=True, help="comma-separated trait list")
    p_agent.add_argument("--failures", default="", help="comma-separated failure-mode list")
    p_agent.add_argument("--min-confidence", type=float, default=0.0)
    p_agent.set_defaults(func=cmd_for_agent)

    p_sum = sub.add_parser("summary", help="one-line lattice summary")
    p_sum.set_defaults(func=cmd_summary)

    p_demo = sub.add_parser("demo", help="seed synthetic registry, detect, revert")
    p_demo.set_defaults(func=cmd_demo)

    args = ap.parse_args()
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main() or 0)
