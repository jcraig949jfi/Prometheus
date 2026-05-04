"""Trial 3 iter-31 — 15K-episode deeper search on real a149 corpus.

Per Iter 28 finding: Ergon found Charon's anchors + A149499 + a 7-record
A149086+ cluster at 5K eps. Scale to 15K eps to see if longer combinatorial
search reveals more substrate-grade clusters.

Multi-restart at uniform=5% (deep assembly) AND uniform=30% (broad coverage).
"""
from __future__ import annotations

import json
from pathlib import Path

from ergon.learner.promotion_ledger import PromotionLedger
from ergon.learner.trials._a149_real_corpus import (
    corpus_summary, load_a149_real_corpus,
)
from ergon.learner.trials.trial_3_iter28_a149_real import run_one_seed_on_a149


if __name__ == "__main__":
    out_dir = Path(__file__).parent
    ledger_dir = out_dir / "ledgers"
    ledger_dir.mkdir(parents=True, exist_ok=True)

    print("Loading real a149 corpus...")
    corpus = load_a149_real_corpus()
    summary = corpus_summary(corpus)
    print(f"  {summary['n_total']} records, {summary['n_kill_any']} killed")
    print()

    seeds = [42, 100, 1234]
    n_episodes = 15000

    weight_configs = {
        "u05_15k": {
            "structural": 0.65, "symbolic": 0.15, "uniform": 0.05,
            "structured_null": 0.05, "anti_prior": 0.10,
        },
        "u30_15k": {
            "structural": 0.40, "symbolic": 0.15, "uniform": 0.30,
            "structured_null": 0.05, "anti_prior": 0.10,
        },
    }

    all_results = {}
    for cfg_name, weights in weight_configs.items():
        ledger_path = ledger_dir / f"trial_3_iter31_a149_{cfg_name}_ledger.jsonl"
        if ledger_path.exists():
            ledger_path.unlink()
        manifest = {
            "weights": weights, "exploration_rate": 0.15,
            "n_episodes": n_episodes, "n_seeds": len(seeds),
            "evaluator": "in-process_predicate_eval",
            "corpus_id": "a149_real_v1",
            "lift_threshold": 2.0, "min_match_size": 3,
        }
        ledger = PromotionLedger(
            path=ledger_path,
            trial_name=f"trial_3_iter31_a149_{cfg_name}",
            regime_manifest=manifest,
        )
        print(f"Config: {cfg_name}")
        per_seed = []
        for seed in seeds:
            print(f"  Seed {seed}...", end=" ", flush=True)
            r = run_one_seed_on_a149(
                seed, n_episodes, corpus, weights, ledger,
                "ergon_a149_real_corpus_eval",
            )
            print(
                f"ch_disc={r['charon_disc']} a149499_cap={r['a149499_capture']} "
                f"pass={r['substrate_passed']} hl={r['n_high_lift']} "
                f"({r['elapsed_s']:.1f}s)"
            )
            per_seed.append(r)
        all_results[cfg_name] = per_seed

    (out_dir / "trial_3_iter31_a149_results.json").write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8"
    )

    # Find unique high-lift predicates (lift>=10, match>=3, kr=1.0) across all configs
    print()
    print("=" * 78)
    print("HIGH-LIFT UNIQUE PREDICATES (lift >= 10, match >= 3, kill_rate = 1.0)")
    print("=" * 78)
    seen_preds = set()
    discoveries = []
    for cfg_name, per_seed in all_results.items():
        for s in per_seed:
            for h in s["top_high_lift"]:
                if (h["lift"] >= 10.0 and h["match_size"] >= 3
                        and h["matched_kill_rate"] >= 0.999):
                    key = tuple(sorted(h["predicate"].items()))
                    if key not in seen_preds:
                        seen_preds.add(key)
                        discoveries.append({**h, "from_config": cfg_name})

    discoveries.sort(key=lambda x: -x["lift"])
    for d in discoveries:
        print(
            f"  lift={d['lift']:>6.2f} match={d['match_size']:>2d} "
            f"kr={d['matched_kill_rate']:.3f} from={d['from_config']:>10s}  "
            f"predicate={d['predicate']}"
        )
    print()
    print(f"Total unique high-confidence discoveries: {len(discoveries)}")
