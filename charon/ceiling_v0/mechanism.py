"""Why does P3d reach 0.647 when P3c reaches 0.364?

This has been the largest open question since iteration 9 and two explanations
have already been proposed and withdrawn:

  iteration 9  "static relevance to raw query patterns"  -> refuted, gives 0.374
  iteration 10 "dynamic relevance to normalised words"   -> refuted, gives 0.414
               and the perfect-proposer comparison was confounded by generator
               saturation, so its headline was void

Both explanations were about WHICH RULES get proposed. This file tests a different
hypothesis, at the level of the group rather than the rule list:

  The substrate answers a query only when normalisation lands it on a canonical
  form the memo already holds. So accuracy is not really about rule truth or rule
  firing at all — it is about whether the rules COLLAPSE the query population onto
  a small set of forms that observation has already covered.

That predicts a specific arithmetic:

  accuracy  ~  coverage  +  (1 - coverage) * fallback_accuracy

which is checkable, and it predicts that the difference between arms lives in the
number of DISTINCT canonical forms the held-out queries reduce to.

Everything here is measured against the hidden group directly.

  python mechanism.py
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List

from baselines import substrate_arm
from config import ArmConfig
from substrate import ArtifactStore, SubstratePredictor, normalize
from universe import EvalSet, Universe, UniverseSpec

SEEDS = list(range(1, 21))
ROUNDS = 6


def profile(store: ArtifactStore, uni: Universe, ev: EvalSet) -> Dict:
    rules = list(store.rules.values())
    pred = SubstratePredictor(store)

    forms, hits, lens = [], 0, []
    elems = set()
    for q in ev.queries:
        canon, _ = normalize(q.word, rules)
        key = ArtifactStore.memo_key(q.tag, canon)
        forms.append((q.tag, tuple(canon)))
        lens.append(len(canon))
        elems.add(uni.true_word_element(canon))
        if key in store.memo:
            hits += 1

    preds, cov = pred.predict_all(ev.queries)
    acc, _ = ev.score(preds)

    # how concentrated is the query population after rewriting?
    distinct = len(set(forms))
    counts = Counter(forms)
    top_share = counts.most_common(1)[0][1] / len(ev.queries) if counts else 0.0

    # fallback accuracy: how often the fallback symbol happens to be right
    fb = pred.fallback
    fb_acc = sum(1 for a in ev.answers if a == fb) / len(ev.answers)

    predicted = cov * 1.0 + (1 - cov) * fb_acc
    return {
        "acc": acc, "coverage": cov,
        "distinct_forms": distinct,
        "distinct_elements": len(elems),
        "mean_canon_len": sum(lens) / len(lens),
        "top_form_share": top_share,
        "fallback_acc": fb_acc,
        "predicted_acc": predicted,
        "residual": acc - predicted,
        "n_rules": len(store.active_rules()),
        "n_memo": len(store.memo),
    }


def run() -> None:
    modes = ("random", "datadriven", "relevance")
    agg: Dict[str, List[Dict]] = {m: [] for m in modes}
    for seed in SEEDS:
        uni = Universe(UniverseSpec(seed=seed))
        ev = EvalSet(uni)
        for m in modes:
            _, store = substrate_arm(uni, ev, seed, ArmConfig(), ROUNDS, m)
            agg[m].append(profile(store, uni, ev))

    def mean(m, f):
        v = [r[f] for r in agg[m]]
        return sum(v) / len(v)

    print("=" * 76)
    print("MECHANISM — what actually separates the substrate arms")
    print("=" * 76)
    print(f"\n  {'arm':<14}{'acc':>7}{'cov':>7}{'rules':>7}{'memo':>7}"
          f"{'canon len':>11}{'distinct':>10}{'top share':>11}")
    for m in modes:
        print(f"  {m:<14}{mean(m,'acc'):>7.3f}{mean(m,'coverage'):>7.3f}"
              f"{mean(m,'n_rules'):>7.1f}{mean(m,'n_memo'):>7.0f}"
              f"{mean(m,'mean_canon_len'):>11.2f}{mean(m,'distinct_forms'):>10.1f}"
              f"{mean(m,'top_form_share'):>11.3f}")

    print(f"\n  does  acc ~ cov + (1-cov)*fallback  hold?\n")
    print(f"  {'arm':<14}{'measured':>10}{'predicted':>11}{'residual':>10}"
          f"{'fallback':>10}")
    for m in modes:
        print(f"  {m:<14}{mean(m,'acc'):>10.3f}{mean(m,'predicted_acc'):>11.3f}"
              f"{mean(m,'residual'):>10.3f}{mean(m,'fallback_acc'):>10.3f}")

    print(f"\n  40 held-out queries reduce to this many distinct (tag, form) pairs:")
    for m in modes:
        print(f"    {m:<14}{mean(m,'distinct_forms'):>6.1f}   "
              f"covering {mean(m,'distinct_elements'):.1f} distinct group elements "
              f"of 27")


if __name__ == "__main__":
    run()
