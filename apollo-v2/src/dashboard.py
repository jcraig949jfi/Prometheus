"""
dashboard.py — Quick population health readout for Apollo v2.

Usage: python dashboard.py
       watch -n 60 python dashboard.py   (auto-refresh every 60s)
"""

import json
import sys
from pathlib import Path


def read_latest(path: str, n: int = 5) -> list[dict]:
    """Read last N lines from a JSONL file."""
    p = Path(path)
    if not p.exists():
        return []
    lines = p.read_text(encoding='utf-8').strip().split('\n')
    return [json.loads(line) for line in lines[-n:] if line.strip()]


def dashboard():
    base = Path(__file__).parent.parent

    # Dashboard status
    status_path = base / "dashboard" / "status_v2.jsonl"
    entries = read_latest(str(status_path), 10)

    if not entries:
        print("No dashboard data yet. Apollo v2 has not started or hasn't logged.")
        return

    latest = entries[-1]
    gen = latest.get('generation', 0)
    pop = latest.get('population_size', 0)
    ts = latest.get('timestamp', '?')

    print("=" * 65)
    print(f" APOLLO v2 — Generation {gen}  |  {ts}")
    print("=" * 65)
    print(f"  Population:     {pop}")
    print(f"  Compile rate:   {latest.get('compilation_survival_pct', 0):.0%}")
    print(f"  NCD decay:      {latest.get('ncd_decay_weight', 1.0):.1f}")
    print()

    print("  ACCURACY")
    print(f"    Best margin:  {latest.get('best_accuracy_margin', 0):+.4f}")
    print(f"    Median:       {latest.get('median_accuracy_margin', 0):+.4f}")
    print()

    print("  ABLATION (bypass detection)")
    print(f"    Best delta:   {latest.get('best_ablation_delta', 0):.4f}")
    print(f"    All-LB count: {latest.get('n_all_load_bearing', 0)}")
    print()

    print(f"  GENERALIZATION")
    print(f"    Best held-out:{latest.get('best_generalization', 0):+.4f}")
    print()

    print(f"  DIVERSITY")
    print(f"    Archive size: {latest.get('novelty_archive_size', 0)}")
    print(f"    Med. prims:   {latest.get('median_primitive_count', 0):.1f}")
    print()

    # Trend (last 5 entries)
    if len(entries) >= 2:
        print("  TREND (last entries):")
        print(f"  {'Gen':>6s} {'BestAcc':>8s} {'MedAcc':>8s} {'BestAbl':>8s} {'#LB':>4s} {'Arch':>5s}")
        for e in entries[-5:]:
            print(f"  {e.get('generation', 0):6d} "
                  f"{e.get('best_accuracy_margin', 0):+8.4f} "
                  f"{e.get('median_accuracy_margin', 0):+8.4f} "
                  f"{e.get('best_ablation_delta', 0):8.4f} "
                  f"{e.get('n_all_load_bearing', 0):4d} "
                  f"{e.get('novelty_archive_size', 0):5d}")
    print()

    # Graveyard stats
    graveyard_path = base / "graveyard" / "graveyard_v2.jsonl"
    if graveyard_path.exists():
        lines = graveyard_path.read_text(encoding='utf-8').strip().split('\n')
        deaths = [json.loads(l) for l in lines if l.strip()]
        causes = {}
        for d in deaths:
            c = d.get('cause', 'unknown')
            causes[c] = causes.get(c, 0) + 1
        print(f"  GRAVEYARD ({len(deaths)} total deaths):")
        for cause, count in sorted(causes.items(), key=lambda x: -x[1]):
            print(f"    {cause}: {count}")
    print()

    # Lineage peek
    lineage_path = base / "lineage" / "lineage_v2.jsonl"
    if lineage_path.exists():
        recent = read_latest(str(lineage_path), 3)
        if recent:
            print("  RECENT ELITES:")
            for r in recent:
                prims = r.get('primitive_names', [])
                acc = r.get('fitness', {}).get('accuracy_margin', 0)
                abl = r.get('fitness', {}).get('ablation_delta', 0)
                mut = r.get('mutations_applied', [])
                print(f"    {r.get('genome_id', '?'):12s} | acc={acc:+.3f} abl={abl:.2f} | "
                      f"{len(prims)} prims | {mut}")

    print("=" * 65)


if __name__ == '__main__':
    dashboard()
