"""Greedy corpus builder — orchestrates all source adapters into a
training-ready corpus + a held-out gold true/false eval set + a manifest.

Usage:
    python -m ergon.learner.greedy.build_corpus --out-dir ergon/learner/greedy/corpus

Discipline:
- Held-out gold eval is uid-disjoint from train and stratified by
  (gold label, source). It is NEVER written into the train file.
- Per-source caps prevent any single source re-creating the monoculture.
- Nemesis is not a source here (eval-only by design); not imported.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

from .serializers import Example
from .sources import ALL_SOURCES, SourceStats

# Per-source caps: greedy on variety, sampled on count.
DEFAULT_CAPS = {
    "theseus": 14000,     # the spine; stratified across generators+verdicts
    "pollux": 4000,
    "erebos": 4000,
    "hephaestus": 5000,
    "charon_md": 2500,    # tier 2
    "harmonia": 500,      # tier 2
}


def collect(caps: Dict[str, int], seed: int = 42, values_shown: bool = False):
    examples: List[Example] = []
    stats: Dict[str, SourceStats] = {}
    for name, fn in ALL_SOURCES.items():
        cap = caps.get(name, 0)
        if cap <= 0:
            continue
        st = SourceStats(name=name)
        if name == "theseus":
            it = fn(cap, st, values_shown=values_shown)
        else:
            it = fn(cap, st)
        for ex in it:
            examples.append(ex)
        stats[name] = st
    # dedup by uid (stable: keep first)
    seen = set()
    deduped: List[Example] = []
    for ex in examples:
        if ex.uid in seen:
            continue
        seen.add(ex.uid)
        deduped.append(ex)
    return deduped, stats


def reserve_gold_eval(examples: List[Example], n_eval: int, seed: int = 7):
    """Split a uid-disjoint, label+source-stratified gold eval set out of
    the examples that carry a gold_bool. Returns (train, eval)."""
    rng = random.Random(seed)
    gold = [e for e in examples if e.gold_bool is not None]
    nongold = [e for e in examples if e.gold_bool is None]

    # stratify by (gold_bool, source)
    strata: Dict[tuple, List[Example]] = defaultdict(list)
    for e in gold:
        strata[(e.gold_bool, e.source)].append(e)
    for k in strata:
        rng.shuffle(strata[k])

    # proportional draw toward n_eval, balanced across True/False
    eval_set: List[Example] = []
    # aim for ~50/50 true/false in eval
    want_true = n_eval // 2
    want_false = n_eval - want_true
    def drain(target_bool, want):
        picked = []
        keys = [k for k in strata if k[0] == target_bool]
        rng.shuffle(keys)
        i = 0
        while want > 0 and any(strata[k] for k in keys):
            k = keys[i % len(keys)]
            if strata[k]:
                picked.append(strata[k].pop())
                want -= 1
            i += 1
        return picked
    eval_set += drain(True, want_true)
    eval_set += drain(False, want_false)

    eval_uids = {e.uid for e in eval_set}
    train = [e for e in examples if e.uid not in eval_uids]
    return train, eval_set


def entity_disjoint_split(examples: List[Example], n_eval: int,
                          eval_entity_frac: float = 0.30, seed: int = 11):
    """Split so that NO entity (underlying knot/EC/etc. object) in the eval
    set ever appears in any training example. This kills value-memorization
    as an explanation for eval accuracy: the model has never seen these
    objects' invariant values during training.

    - eval-eligible: gold-labeled AND every entity in the held-out pool
    - train-eligible: no entity in the held-out pool
    - mixed (some held-out, some not): DROPPED (would leak an eval entity)
    - no-entity examples: train (they reference no held-out object)
    """
    rng = random.Random(seed)
    all_entities = sorted({e for ex in examples for e in ex.entities})
    rng.shuffle(all_entities)
    n_hold = int(len(all_entities) * eval_entity_frac)
    eval_pool = set(all_entities[:n_hold])

    train: List[Example] = []
    eval_cand: List[Example] = []
    dropped_mixed = 0
    for ex in examples:
        ents = set(ex.entities)
        if not ents:
            train.append(ex)
            continue
        if ents <= eval_pool:
            if ex.gold_bool is not None:
                eval_cand.append(ex)
            else:
                dropped_mixed += 1
        elif ents.isdisjoint(eval_pool):
            train.append(ex)
        else:
            dropped_mixed += 1

    # balance eval 50/50 true/false, cap at n_eval
    rng.shuffle(eval_cand)
    pos = [e for e in eval_cand if e.gold_bool is True]
    neg = [e for e in eval_cand if e.gold_bool is False]
    k = min(len(pos), len(neg), n_eval // 2)
    eval_set = pos[:k] + neg[:k]
    rng.shuffle(eval_set)

    # any eval_cand not chosen must NOT leak into train (they touch eval pool) -> drop
    stats = {"n_entities": len(all_entities), "held_out_entities": len(eval_pool),
             "dropped_mixed_or_unused": dropped_mixed + (len(eval_cand) - len(eval_set))}
    return train, eval_set, stats


def write_jsonl(path: Path, rows: List[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def summarize(examples: List[Example]) -> dict:
    return {
        "n": len(examples),
        "by_source": dict(Counter(e.source for e in examples)),
        "by_tier": dict(Counter(e.tier for e in examples)),
        "by_outcome": dict(Counter(e.outcome for e in examples)),
        "by_domain_top": dict(Counter(e.domain for e in examples).most_common(15)),
        "failure_fraction": round(sum(e.is_failure for e in examples) / max(1, len(examples)), 4),
        "gold_labeled": sum(e.gold_bool is not None for e in examples),
        "gold_true": sum(e.gold_bool is True for e in examples),
        "gold_false": sum(e.gold_bool is False for e in examples),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="F:/Prometheus/ergon/learner/greedy/corpus")
    ap.add_argument("--n-eval", type=int, default=1200)
    ap.add_argument("--theseus-cap", type=int, default=DEFAULT_CAPS["theseus"])
    ap.add_argument("--tag", default="v1")
    ap.add_argument("--entity-split", action="store_true",
                    help="entity-disjoint train/eval split (no shared underlying objects)")
    ap.add_argument("--values-shown", action="store_true",
                    help="embed invariant values in the prompt (reasoning task, not recall)")
    args = ap.parse_args()

    caps = dict(DEFAULT_CAPS)
    caps["theseus"] = args.theseus_cap

    print(f"[greedy] collecting (values_shown={args.values_shown}) from:", list(caps.keys()))
    examples, stats = collect(caps, values_shown=args.values_shown)
    print(f"[greedy] collected {len(examples)} deduped examples")

    split_stats = {}
    if args.entity_split:
        train, gold_eval, split_stats = entity_disjoint_split(examples, n_eval=args.n_eval)
        print(f"[greedy] ENTITY-DISJOINT split: train={len(train)} gold_eval={len(gold_eval)} {split_stats}")
    else:
        train, gold_eval = reserve_gold_eval(examples, n_eval=args.n_eval)
        print(f"[greedy] random split: train={len(train)}  gold_eval={len(gold_eval)}")

    out = Path(args.out_dir)
    write_jsonl(out / f"train_{args.tag}.jsonl", [e.to_row() for e in train])
    write_jsonl(out / f"gold_eval_{args.tag}.jsonl", [e.to_row() for e in gold_eval])

    manifest = {
        "tag": args.tag,
        "caps": caps,
        "entity_split": args.entity_split,
        "values_shown": args.values_shown,
        "split_stats": split_stats,
        "n_eval_requested": args.n_eval,
        "source_stats": {k: {"yielded": v.yielded, "skipped": v.skipped,
                              "by_outcome": v.by_outcome} for k, v in stats.items()},
        "train_summary": summarize(train),
        "gold_eval_summary": summarize(gold_eval),
    }
    (out / f"manifest_{args.tag}.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print("[greedy] wrote corpus + manifest to", out)
    print(json.dumps(manifest["train_summary"], indent=2))
    print("GOLD EVAL:", json.dumps(manifest["gold_eval_summary"], indent=2))


if __name__ == "__main__":
    main()
