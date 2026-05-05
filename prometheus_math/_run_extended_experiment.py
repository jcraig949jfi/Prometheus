"""One-shot experiment runner — produces the numbers for
OBSTRUCTION_EXTENDED_RESULTS.md.

Run::

    python -m prometheus_math._run_extended_experiment

Outputs JSON to stdout + a small dict for the results doc.
"""
from __future__ import annotations

import json
import math
import time
from typing import Any, Dict, List

import numpy as np

from prometheus_math._obstruction_corpus_extended import (
    extended_corpus_summary,
    load_extended_corpus,
)
from prometheus_math._obstruction_corpus_live import (
    obstruction_signature_lift_on_live,
)
from prometheus_math.demo_obstruction import (
    train_random_obstruction,
    train_reinforce_obstruction,
)
from prometheus_math.obstruction_env import (
    REDISCOVERED_OBSTRUCTION_SHAPE_TAG,
    REDISCOVERED_SECONDARY_TAG,
    ObstructionEnv,
)


OBSTRUCTION_SHAPE: Dict[str, Any] = {
    "n_steps": 5,
    "neg_x": 4,
    "pos_x": 1,
    "has_diag_neg": True,
}

ANCHOR_SEQ_IDS = {"A149074", "A149081", "A149082", "A149089", "A149090"}


def _signature_lift_per_prefix(corpus, prefix):
    sub = [e for e in corpus if e.sequence_id.startswith(prefix)]
    if not sub:
        return None
    return obstruction_signature_lift_on_live(sub, OBSTRUCTION_SHAPE)


def main() -> Dict[str, Any]:
    out: Dict[str, Any] = {}

    # Layer 1: data audit (live mode)
    live = load_extended_corpus(
        prefixes=["A148", "A149", "A150", "A151"], mode="live"
    )
    live_summary = extended_corpus_summary(live)
    out["live_summary"] = {
        "n_total": live_summary["n_total"],
        "n_killed": live_summary["n_killed"],
        "kill_rate": live_summary["kill_rate"],
        "by_prefix_total": live_summary["per_prefix_total"],
        "by_prefix_kill_rate": live_summary["per_prefix_kill_rate"],
    }

    # Layer 2: surrogate mode
    surr = load_extended_corpus(
        prefixes=["A148", "A149", "A150", "A151"], mode="surrogate"
    )
    surr_summary = extended_corpus_summary(surr)
    out["surrogate_summary"] = {
        "n_total": surr_summary["n_total"],
        "n_killed": surr_summary["n_killed"],
        "kill_rate": surr_summary["kill_rate"],
        "by_prefix_total": surr_summary["per_prefix_total"],
        "by_prefix_kill_rate": surr_summary["per_prefix_kill_rate"],
    }
    surr_killed_ids = sorted({e.sequence_id for e in surr if e.kill_verdict})
    out["surrogate_killed_ids"] = surr_killed_ids

    # Layer 3: OBSTRUCTION_SHAPE lift on live, per slice
    out["obstruction_shape_lift"] = {}
    for label, prefixes in (
        ("A148_A149_only", ["A148", "A149"]),
        ("A148_A149_A150_A151", ["A148", "A149", "A150", "A151"]),
        ("A150_A151_only", ["A150", "A151"]),
    ):
        try:
            sub = load_extended_corpus(prefixes=prefixes, mode="live")
            r = obstruction_signature_lift_on_live(sub, OBSTRUCTION_SHAPE)
            out["obstruction_shape_lift"][label] = {
                "lift": r["lift"],
                "n_match": r["n_match"],
                "n_total": r["n_total"],
                "match_kill_rate": r["match_kill_rate"],
                "non_match_kill_rate": r["non_match_kill_rate"],
                "match_sequence_ids": r["match_sequence_ids"],
            }
        except Exception as e:
            out["obstruction_shape_lift"][label] = {"error": str(e)}

    # Same on surrogate corpus
    out["obstruction_shape_lift_surrogate"] = {}
    for label, prefixes in (
        ("A148_A149_only", ["A148", "A149"]),
        ("A148_A149_A150_A151", ["A148", "A149", "A150", "A151"]),
        ("A150_A151_only", ["A150", "A151"]),
    ):
        try:
            sub = load_extended_corpus(prefixes=prefixes, mode="surrogate")
            r = obstruction_signature_lift_on_live(sub, OBSTRUCTION_SHAPE)
            out["obstruction_shape_lift_surrogate"][label] = {
                "lift": r["lift"],
                "n_match": r["n_match"],
                "n_total": r["n_total"],
                "match_kill_rate": r["match_kill_rate"],
                "non_match_kill_rate": r["non_match_kill_rate"],
            }
        except Exception as e:
            out["obstruction_shape_lift_surrogate"][label] = {"error": str(e)}

    # Layer 4: REINFORCE vs random on the extended live corpus
    n_episodes = 1000
    seeds = [101, 102, 103]
    print(f"[run] REINFORCE x {n_episodes} eps x {len(seeds)} seeds (live)...", flush=True)

    reinforce_results = []
    random_results = []
    for s in seeds:
        env_rein = ObstructionEnv(
            corpus=live, seed=s,
            max_predicate_complexity=4, held_out_fraction=0.3,
        )
        env_rein.reset()
        t0 = time.time()
        rein = train_reinforce_obstruction(env_rein, n_episodes, seed=s)
        t1 = time.time()
        env_rand = ObstructionEnv(
            corpus=live, seed=s + 1000,
            max_predicate_complexity=4, held_out_fraction=0.3,
        )
        env_rand.reset()
        rand = train_random_obstruction(env_rand, n_episodes, seed=s + 1000)
        t2 = time.time()
        reinforce_results.append({
            "seed": s,
            "mean_reward": float(np.mean(rein["rewards"])),
            "max_reward": float(np.max(rein["rewards"])),
            "n_obstruction_tags": sum(
                1 for _, t in rein["rediscoveries"]
                if t == REDISCOVERED_OBSTRUCTION_SHAPE_TAG
            ),
            "n_secondary_tags": sum(
                1 for _, t in rein["rediscoveries"]
                if t == REDISCOVERED_SECONDARY_TAG
            ),
            "first_obstruction_episode": rein["obstruction_first_episode"],
            "duration_sec": round(t1 - t0, 2),
        })
        random_results.append({
            "seed": s + 1000,
            "mean_reward": float(np.mean(rand["rewards"])),
            "max_reward": float(np.max(rand["rewards"])),
            "n_obstruction_tags": sum(
                1 for _, t in rand["rediscoveries"]
                if t == REDISCOVERED_OBSTRUCTION_SHAPE_TAG
            ),
            "duration_sec": round(t2 - t1, 2),
        })

    # Aggregate
    rein_means = [r["mean_reward"] for r in reinforce_results]
    rand_means = [r["mean_reward"] for r in random_results]
    rein_avg = float(np.mean(rein_means))
    rand_avg = float(np.mean(rand_means))

    out["reinforce_vs_random_live"] = {
        "n_episodes": n_episodes,
        "seeds": seeds,
        "reinforce_per_seed": reinforce_results,
        "random_per_seed": random_results,
        "reinforce_mean_of_means": rein_avg,
        "random_mean_of_means": rand_avg,
        "lift_reinforce_over_random": (
            rein_avg / rand_avg if rand_avg > 1e-12 else float("inf") if rein_avg > 0 else 0.0
        ),
    }

    # Layer 5: REINFORCE on surrogate corpus too
    print("[run] REINFORCE on surrogate corpus...", flush=True)
    sur_rein_results = []
    sur_rand_results = []
    for s in seeds:
        env_rein = ObstructionEnv(
            corpus=surr, seed=s,
            max_predicate_complexity=4, held_out_fraction=0.3,
        )
        env_rein.reset()
        rein = train_reinforce_obstruction(env_rein, n_episodes, seed=s)
        env_rand = ObstructionEnv(
            corpus=surr, seed=s + 2000,
            max_predicate_complexity=4, held_out_fraction=0.3,
        )
        env_rand.reset()
        rand = train_random_obstruction(env_rand, n_episodes, seed=s + 2000)
        sur_rein_results.append({
            "seed": s,
            "mean_reward": float(np.mean(rein["rewards"])),
            "max_reward": float(np.max(rein["rewards"])),
            "n_obstruction_tags": sum(
                1 for _, t in rein["rediscoveries"]
                if t == REDISCOVERED_OBSTRUCTION_SHAPE_TAG
            ),
            "first_obstruction_episode": rein["obstruction_first_episode"],
        })
        sur_rand_results.append({
            "seed": s + 2000,
            "mean_reward": float(np.mean(rand["rewards"])),
            "max_reward": float(np.max(rand["rewards"])),
            "n_obstruction_tags": sum(
                1 for _, t in rand["rediscoveries"]
                if t == REDISCOVERED_OBSTRUCTION_SHAPE_TAG
            ),
        })
    sur_rein_avg = float(np.mean([r["mean_reward"] for r in sur_rein_results]))
    sur_rand_avg = float(np.mean([r["mean_reward"] for r in sur_rand_results]))
    out["reinforce_vs_random_surrogate"] = {
        "n_episodes": n_episodes,
        "seeds": seeds,
        "reinforce_per_seed": sur_rein_results,
        "random_per_seed": sur_rand_results,
        "reinforce_mean_of_means": sur_rein_avg,
        "random_mean_of_means": sur_rand_avg,
        "lift_reinforce_over_random": (
            sur_rein_avg / sur_rand_avg if sur_rand_avg > 1e-12
            else float("inf") if sur_rein_avg > 0 else 0.0
        ),
    }

    print(json.dumps(out, indent=2, default=str), flush=True)
    return out


if __name__ == "__main__":
    main()
