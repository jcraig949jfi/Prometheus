"""Run the OEIS prefix-extension hunt and write results to
``OEIS_PREFIX_EXTENSION_RESULTS.md``.

Pulls A152*, A153*, A154*, A155* (50 each = 200 total), applies the
calibrated surrogate battery, runs the brute-force signature
enumerator per prefix, and runs REINFORCE (3 seeds × 1000 episodes
each) on the union of the curated A148+A149 corpus + lattice-walk
entries from the new prefixes.

Only the curated A148+A149 corpus actually contains parseable 3-D
walks; for A152-A155 the hunt is on the general (non-lattice)
SurrogateRecord schema.
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List

import numpy as np

from prometheus_math._obstruction_corpus_extended import load_extended_corpus
from prometheus_math._oeis_prefix_extension import (
    DEFAULT_NEW_PREFIXES,
    enumerate_signatures,
    extend_corpus_with_surrogate,
    extended_pipeline_summary,
    signatures_per_prefix,
    _general_feature_dict,
)


def main() -> Dict[str, Any]:
    print("=" * 72)
    print("OEIS PREFIX EXTENSION — A152-A155 SURROGATE HUNT")
    print("=" * 72)
    t0 = time.perf_counter()

    # Step 1 — pull and surrogate.
    print(f"\n[1] Pulling {DEFAULT_NEW_PREFIXES}, 50 each")
    corpus = extend_corpus_with_surrogate(
        prefixes=list(DEFAULT_NEW_PREFIXES), max_per_prefix=50
    )
    pull_summary = extended_pipeline_summary(corpus)
    print(json.dumps(pull_summary, indent=2))

    # Step 2 — brute-force per-prefix signatures.
    print("\n[2] Brute-force signature search per prefix")
    per_prefix = signatures_per_prefix(
        corpus, max_complexity=3, top_k=5, min_match_size=3
    )
    for prefix, sigs in per_prefix.items():
        print(f"\n  {prefix}: {len(sigs)} signatures")
        for pred, lift, n in sigs:
            print(f"    lift={lift:>8.2f} n_match={n:>3} pred={pred}")

    # Step 3 — aggregate signatures across prefixes.
    print("\n[3] Aggregate signatures (across all prefixes)")
    all_general = [
        (
            (
                rec.features
                if rec.parseable_step_set and rec.features
                else _general_feature_dict(rec)
            ),
            rec.kill_verdict,
        )
        for rec in corpus.entries_general
    ]
    agg_sigs = enumerate_signatures(
        all_general, max_complexity=3, min_match_size=5
    )
    top_agg = agg_sigs[:5]
    for pred, lift, n in top_agg:
        print(f"    lift={lift:>8.2f} n_match={n:>3} pred={pred}")

    # Step 4 — REINFORCE on the curated A148+A149 + lattice extension
    # (which is empty for A152-A155). The point of this step is to
    # confirm the pipeline runs end-to-end on a hybrid corpus.
    print("\n[4] REINFORCE on A148+A149 (curated; A152-A155 contributes 0 lattice rows)")
    curated = load_extended_corpus(
        prefixes=["A148", "A149"], mode="surrogate"
    )
    combined = list(curated) + list(corpus.entries_lattice)
    print(f"    combined corpus size: {len(combined)} (lattice schema)")
    reinforce_results: List[Dict[str, Any]] = []
    try:
        from prometheus_math.demo_obstruction import (
            train_reinforce_obstruction,
        )
        from prometheus_math.obstruction_env import ObstructionEnv
    except Exception as e:
        print(f"    (REINFORCE deps unavailable: {e})")
    else:
        for seed in (101, 102, 103):
            env = ObstructionEnv(
                corpus=combined,
                seed=seed,
                max_predicate_complexity=4,
                held_out_fraction=0.3,
            )
            env.reset()
            out = train_reinforce_obstruction(
                env, n_episodes=1000, seed=seed
            )
            disc = out.get("discoveries", [])
            print(
                f"    seed={seed}: rediscoveries={len(out['rediscoveries'])}, "
                f"discoveries={len(disc)}, mean_reward={float(np.mean(out['rewards'])):.3f}"
            )
            reinforce_results.append(
                {
                    "seed": seed,
                    "n_rediscoveries": len(out["rediscoveries"]),
                    "n_discoveries": len(disc),
                    "mean_reward": float(np.mean(out["rewards"])),
                    "obstruction_first_episode": out.get(
                        "obstruction_first_episode"
                    ),
                }
            )

    elapsed = time.perf_counter() - t0
    print(f"\nElapsed: {elapsed:.1f} s")
    return {
        "pull_summary": pull_summary,
        "per_prefix_signatures": {
            p: [(dict(d), float(l), int(n)) for d, l, n in ss]
            for p, ss in per_prefix.items()
        },
        "aggregate_top": [
            (dict(d), float(l), int(n)) for d, l, n in top_agg
        ],
        "reinforce": reinforce_results,
        "elapsed_sec": elapsed,
    }


if __name__ == "__main__":
    out = main()
    out_path = "prometheus_math/_oeis_prefix_extension_run.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nWrote {out_path}")
