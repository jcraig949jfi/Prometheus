"""Ablation harness. RESTORED 2026-08-22. Operates on artifact stores; no model.

A2 memo-only        drop the rules, keep the recorded outcomes
A3 rules-only       drop the recorded outcomes, keep the rules
A4 artifact shuffle run universe X's store against universe Y's queries
A5 top-k deletion   remove the k most-used rules and everything in the memo that
                    depended on them, compared against removing k RANDOM and k
                    LEAST-USED rules — because "deleting things hurts" is not
                    evidence; deleting the load-bearing things specifically is
A7 wrong artifacts  measured live inside substrate_arm

  python ablations.py
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List

from baselines import substrate_arm
from config import ArmConfig
from substrate import ArtifactStore, SubstratePredictor
from universe import EvalSet, Universe, UniverseSpec

HERE = Path(__file__).resolve().parent


def score(store: ArtifactStore, ev: EvalSet):
    preds, cov = SubstratePredictor(store).predict_all(ev.queries)
    acc, _ = ev.score(preds)
    return acc, cov


def strip_rules(store: ArtifactStore) -> ArtifactStore:
    s = store.clone()
    for r in s.rules.values():
        r.status = "rejected"          # memo deliberately left intact
    return s


def strip_memo(store: ArtifactStore) -> ArtifactStore:
    s = store.clone()
    s.memo = {}
    return s


def delete_rules(store: ArtifactStore, rids: List[str]) -> ArtifactStore:
    s = store.clone()
    for rid in rids:
        s.demote(rid)                  # purges dependent memo entries too
    return s


def run(seeds: List[int], rounds: int, mode: str) -> Dict:
    stores, evs = {}, {}
    for seed in seeds:
        uni = Universe(UniverseSpec(seed=seed))
        ev = EvalSet(uni)
        _, store = substrate_arm(uni, ev, seed, ArmConfig(), rounds, mode)
        # tally use so "most-used" is defined by held-out normalisation
        SubstratePredictor(store).predict_all(ev.queries, tally=True)
        stores[seed], evs[seed] = store, ev

    rows = []
    for seed in seeds:
        st, ev = stores[seed], evs[seed]
        base_acc, base_cov = score(st, ev)
        a2_acc, a2_cov = score(strip_rules(st), ev)
        a3_acc, a3_cov = score(strip_memo(st), ev)
        other = seeds[(seeds.index(seed) + 1) % len(seeds)]
        a4_acc, a4_cov = score(stores[other], ev)

        active = [r for r in st.rules.values() if r.status == "active"]
        ranked = sorted(active, key=lambda r: (-r.uses, r.rid))
        K = max(1, len(active) // 5)
        top = [r.rid for r in ranked[:K]]
        bottom = [r.rid for r in ranked[-K:]]
        rng = random.Random(seed)
        rand = [score(delete_rules(st, rng.sample([r.rid for r in active],
                                                  min(K, len(active)))), ev)[0]
                for _ in range(5)]
        rows.append({
            "seed": seed, "n_rules": len(active), "k_deleted": K,
            "base_acc": base_acc, "base_cov": base_cov,
            "A2_memo_only_acc": a2_acc, "A2_cov": a2_cov,
            "A3_rules_only_acc": a3_acc, "A3_cov": a3_cov,
            "A4_shuffle_acc": a4_acc, "A4_cov": a4_cov,
            "A5_del_top_acc": score(delete_rules(st, top), ev)[0],
            "A5_del_random_acc": sum(rand) / len(rand),
            "A5_del_bottom_acc": score(delete_rules(st, bottom), ev)[0],
            "A5_restored_acc": score(st.clone(), ev)[0],
        })

    mean = lambda f: sum(r[f] for r in rows) / len(rows)
    out = {"mode": mode, "seeds": seeds, "per_seed": rows,
           "mean": {f: round(mean(f), 4) for f in rows[0] if f != "seed"}}
    print(f"\nablations over {len(seeds)} universes ({mode})\n")
    print(f"  intact store                   acc={mean('base_acc'):.3f} "
          f"cov={mean('base_cov'):.3f}")
    print(f"  A2 memo only, rules removed    acc={mean('A2_memo_only_acc'):.3f} "
          f"cov={mean('A2_cov'):.3f}")
    print(f"  A3 rules only, memo removed    acc={mean('A3_rules_only_acc'):.3f} "
          f"cov={mean('A3_cov'):.3f}")
    print(f"  A4 store from another universe acc={mean('A4_shuffle_acc'):.3f} "
          f"cov={mean('A4_cov'):.3f}")
    print(f"\n  A5 causal specificity (delete {mean('k_deleted'):.0f} of "
          f"{mean('n_rules'):.0f}):")
    print(f"     most-used   acc={mean('A5_del_top_acc'):.3f}")
    print(f"     random      acc={mean('A5_del_random_acc'):.3f}")
    print(f"     least-used  acc={mean('A5_del_bottom_acc'):.3f}")
    print(f"     restored    acc={mean('A5_restored_acc'):.3f}")
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", type=int, default=20)
    p.add_argument("--rounds", type=int, default=6)
    p.add_argument("--mode", default="datadriven")
    p.add_argument("--out", default="runs/ablations.json")
    a = p.parse_args()
    res = run(list(range(1, a.seeds + 1)), a.rounds, a.mode)
    (HERE / a.out).write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(f"\n  -> {a.out}")
