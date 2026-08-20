"""knockout_ablation.py — mechanism-knockout ablation of the composed engine.

WHY THIS FILE EXISTS. The forge's one surviving capability claim — "+11pp R3 from the
Probabilistic-Fallacy engine, +32pp R4 from Temporal-Computation" — is cited in
`roles/Hephaestus/ROLE.md` §2/§6, `agents/hephaestus/STATUS.md` §3, the program dossier and
the 08-12 meta-assessment as the only demonstrated metabolization in the program. As of
2026-08-19 it had **no computation anywhere in the repository**: `failure_mining_results.json`
holds the 80 mined scraps that were the INPUT to building those engines, not the measured
output, and no ablation script existed. The number lived only as prose.

That is the exact defect the forge's own doctrine names — a tier claim shipped without an
ablation showing the novel mechanism is load-bearing (ROLE.md §8). Applied to itself, late.

WHAT THIS DOES. Mechanism-knockout, the forge's own Gate-6 protocol: run the composed tool
with the full engine set, then re-run with ONE engine removed, and report the per-tier delta.
An engine whose removal costs nothing was decorative in that tier, whatever its label says.

Deterministic, local, zero API cost. Battery and seed are pinned; re-running reproduces.

    python agents/hephaestus/src/knockout_ablation.py                 # default: all engines
    python agents/hephaestus/src/knockout_ablation.py --engines prob_fallacy,temporal
    python agents/hephaestus/src/knockout_ablation.py --n-per-category 2 --seed 42

CAVEAT ON THE RULER, stated up front because it is the point of the exercise: these tiers are
the TRAP BATTERY's `CATEGORY_TIER` vocabulary (the 2026-05-15 ladder), NOT Harmonia's testable
ladder used by `grading_oracle`. They are different rulers and this file does not translate
between them. A number produced here is "R3 on the forge's own ruler" and must be quoted that
way. See `roles/Hephaestus/TICKET_category_tier_remap_2026-08-17.md`.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import defaultdict
from datetime import datetime, timezone

SRC = pathlib.Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from composer import ComposedReasoningTool                      # noqa: E402
from test_harness import _run_battery, CATEGORY_TIER            # noqa: E402
from trap_generator_extended import generate_full_battery       # noqa: E402

OUT_DIR = SRC.parent / "ablation"


class _AblatedTool(ComposedReasoningTool):
    """The composed tool with one named engine removed. Weights are NOT renormalised —
    the aggregator already divides by the weight of engines that fired, so removal is a
    clean knockout rather than a reweighting of the survivors."""

    def __init__(self, drop: str | None = None):
        super().__init__()
        self.dropped = drop
        if drop is not None:
            names = {n for _, n, _ in self.engines}
            if drop not in names:
                raise ValueError(f"unknown engine {drop!r}; have {sorted(names)}")
            self.engines = [(w, n, e) for (w, n, e) in self.engines if n != drop]


def _by_tier(results: dict, battery: list[dict]) -> dict[str, tuple[int, int]]:
    """Per-tier (correct, total) using the trap battery's own CATEGORY_TIER map."""
    acc: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for res, trap in zip(results["trap_results"], battery):
        tier = CATEGORY_TIER.get(trap.get("category"), "unknown")
        acc[tier][1] += 1
        if res.get("is_correct"):
            acc[tier][0] += 1
    return {t: (c, n) for t, (c, n) in acc.items()}


def run(engines: list[str], n_per_category: int, seed: int) -> dict:
    battery = generate_full_battery(n_per_category=n_per_category, seed=seed)

    full = _run_battery(ComposedReasoningTool(), battery)
    full_tiers = _by_tier(full, battery)

    report: dict = {
        "instrument": "knockout_ablation@v1",
        "protocol": "mechanism-knockout (ROLE.md §8 Gate 6): full minus one engine, per-tier delta",
        "ruler": "trap-battery CATEGORY_TIER (2026-05-15 vocabulary) — NOT Harmonia's testable ladder",
        "battery": {"n": len(battery), "n_per_category": n_per_category, "seed": seed},
        "executor": "hephaestus", "host": "M3/GANDALF",
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "full": {
            "accuracy": full["accuracy"],
            "by_tier": {t: {"correct": c, "n": n, "acc": (c / n if n else None)}
                        for t, (c, n) in sorted(full_tiers.items())},
        },
        "knockouts": {},
    }

    for name in engines:
        abl = _run_battery(_AblatedTool(drop=name), battery)
        abl_tiers = _by_tier(abl, battery)
        deltas = {}
        for tier, (fc, fn) in sorted(full_tiers.items()):
            ac, an = abl_tiers.get(tier, (0, 0))
            if fn == 0 or an == 0:
                continue
            deltas[tier] = {
                "n": fn,
                "full_acc": fc / fn,
                "ablated_acc": ac / an,
                "delta_pp": round((fc / fn - ac / an) * 100, 1),   # +ve => engine helps
            }
        report["knockouts"][name] = {
            "overall_full": full["accuracy"],
            "overall_ablated": abl["accuracy"],
            "overall_delta_pp": round((full["accuracy"] - abl["accuracy"]) * 100, 1),
            "by_tier": deltas,
        }
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--engines", default="prob_fallacy,temporal,causal",
                    help="comma-separated engine names to knock out "
                         "(causal is included as a control: doctrine says it is decorative)")
    ap.add_argument("--n-per-category", type=int, default=2)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    names = [s.strip() for s in args.engines.split(",") if s.strip()]
    rep = run(names, args.n_per_category, args.seed)

    print(f"[knockout] battery n={rep['battery']['n']} seed={rep['battery']['seed']} "
          f"ruler={rep['ruler'].split(' —')[0]}")
    print(f"[knockout] full composed accuracy: {rep['full']['accuracy']:.1%}")
    for tier, d in rep["full"]["by_tier"].items():
        if d["acc"] is not None:
            print(f"             {tier}: {d['correct']}/{d['n']} = {d['acc']:.1%}")
    for name, k in rep["knockouts"].items():
        print(f"\n[knockout] DROP {name}: overall {k['overall_full']:.1%} -> "
              f"{k['overall_ablated']:.1%} ({k['overall_delta_pp']:+.1f}pp)")
        for tier, d in k["by_tier"].items():
            print(f"             {tier}: {d['full_acc']:.1%} -> {d['ablated_acc']:.1%} "
                  f"({d['delta_pp']:+.1f}pp, n={d['n']})")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = pathlib.Path(args.out) if args.out else (
        OUT_DIR / f"knockout_{datetime.now(timezone.utc):%Y-%m-%d}.json")
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    tmp.replace(out)                                   # atomic: no half-written ledgers
    print(f"\n[knockout] written {out}")


if __name__ == "__main__":
    main()
