#!/usr/bin/env python3
"""Can a text-only reader find the planted defect without doing mathematics?

The hand-written tell list in `epoch/defenses.py` only measures the signatures
someone already noticed. This is the stronger test: train a classifier on step
prose alone and ask it to point at the planted step in derivations it has never
seen. It will find tells nobody thought of, which is the point.

Task: given a derivation, rank its steps by P(planted) and take the top one.
Chance is 1 / (number of steps). If the classifier beats chance, the prose
carries a signature and a live falsifier could exploit it instead of reasoning.

The most discriminative tokens are printed so the residue can be judged. Some
signal is legitimate — a case split that lists four branches instead of five is
genuinely visible in the mathematics, and a reader *should* notice. What must
not survive is a stylistic tic of the mutation operator.

  python fingerprint_audit.py --items 240
  python fingerprint_audit.py --items 240 --generator-dir <old checkout>
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent

# legacy tells, kept so the old measurement stays runnable and comparable
LEGACY_TELLS = ["CONVERSE:", "Cancelling the factor", "the same estimate is taken",
                "treats only", "expanding by", "carried over to modulo",
                "holds modulo each factor", "lies outside the stated range",
                "is anchored by checking", "by transitivity", "satisfies n^2 >"]


def tokens(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z_]+|\d+|[<>=^+*/%-]+", text.lower())
    return words + [f"{a}|{b}" for a, b in zip(words, words[1:])]


def build_items(n: int, seed: int, gen_dir: Path) -> list[dict]:
    sys.path.insert(0, str(gen_dir))
    for m in ("templates", "mutations", "generate", "derivation", "exprlang",
              "oracle", "render"):
        sys.modules.pop(m, None)
    import generate as GEN
    import mutations as MUT
    import templates as T

    rng = random.Random(seed)
    fams = MUT.PLAY_FAMILIES + MUT.HOLDOUT_FAMILIES
    tids = ["t1_integer_sum_identity", "t2_modular_power_cycle",
            "t4_linear_recurrence", "t5_collatz_stopping_time"]
    budget = GEN.budget_search_size()
    out, tries = [], 0
    while len(out) < n and tries < n * 20:
        tries += 1
        fam = fams[len(out) % len(fams)]
        got = GEN.build_one(rng.choice(tids), T.TRUE_INVALID, [fam], rng, budget)
        if not got:
            continue
        item, mut = got
        out.append({"family": mut["family"], "target": mut["target"],
                    "steps": [{"id": s["id"], "text": s["text"]}
                              for s in item.steps]})
    return out


def train_nb(items: list[dict]):
    pos, neg = Counter(), Counter()
    npos = nneg = 0
    for it in items:
        for s in it["steps"]:
            bag = pos if s["id"] == it["target"] else neg
            bag.update(tokens(s["text"]))
            if s["id"] == it["target"]:
                npos += 1
            else:
                nneg += 1
    vocab = set(pos) | set(neg)
    tp, tn = sum(pos.values()), sum(neg.values())
    lp = {w: math.log((pos[w] + 1) / (tp + len(vocab))) for w in vocab}
    ln = {w: math.log((neg[w] + 1) / (tn + len(vocab))) for w in vocab}
    prior = math.log(npos / max(1, nneg))
    return lp, ln, prior, vocab


def score(step_text, lp, ln, prior, vocab) -> float:
    s = prior
    for w in tokens(step_text):
        if w in vocab:
            s += lp[w] - ln[w]
    return s


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--items", type=int, default=240)
    p.add_argument("--seed", type=int, default=17)
    p.add_argument("--generator-dir", default=str(HERE))
    p.add_argument("--label", default="current")
    args = p.parse_args()

    items = build_items(args.items, args.seed, Path(args.generator_dir).resolve())
    rng = random.Random(args.seed)
    rng.shuffle(items)
    cut = int(len(items) * 0.6)
    train, test = items[:cut], items[cut:]

    lp, ln, prior, vocab = train_nb(train)

    hits, chance, per_family = 0, 0.0, defaultdict(lambda: [0, 0])
    for it in test:
        ranked = max(it["steps"],
                     key=lambda s: score(s["text"], lp, ln, prior, vocab))
        ok = ranked["id"] == it["target"]
        hits += ok
        chance += 1 / len(it["steps"])
        per_family[it["family"]][0] += ok
        per_family[it["family"]][1] += 1

    n = len(test)
    acc, ch = hits / n, chance / n

    legacy = sum(1 for it in items
                 if any(t in s["text"] for t in LEGACY_TELLS
                        for s in it["steps"] if s["id"] == it["target"]))

    L = []
    L.append(f"FINGERPRINT AUDIT — {args.label}")
    L.append("=" * 62)
    L.append(f"items {len(items)} (train {len(train)} / held-out {len(test)})")
    L.append("")
    L.append("Hand-written tell list (the old, weak measure)")
    L.append(f"  planted steps matched by a grep: {legacy}/{len(items)} "
             f"= {legacy/len(items):.0%}")
    L.append("")
    L.append("Learned text-only classifier (the strong measure)")
    L.append(f"  top-1 identification of the planted step : {acc:.1%}")
    L.append(f"  chance for these derivations             : {ch:.1%}")
    L.append(f"  lift over chance                         : {acc - ch:+.1%}")
    L.append("")
    L.append("  by family (held-out):")
    for fam, (h, t) in sorted(per_family.items()):
        if t:
            L.append(f"    {fam.split('_')[0]:<4s} {h}/{t}")
    L.append("")

    disc = sorted(vocab, key=lambda w: lp[w] - ln[w], reverse=True)[:12]
    L.append("  most planted-indicative tokens (judge these by hand):")
    L.append("    " + ", ".join(repr(w) for w in disc))
    L.append("")
    if acc - ch < 0.10:
        L.append("VERDICT: prose carries no usable signature. A falsifier cannot")
        L.append("skip the mathematics by reading style.")
    else:
        L.append("VERDICT: the prose still leaks. Inspect the tokens above and")
        L.append("decide whether the residue is mathematical content a reader")
        L.append("should legitimately see, or a tic of the mutation operator.")

    text = "\n".join(L)
    print(text)
    out = HERE / f"FINGERPRINT_{args.label}.json"
    out.write_text(json.dumps({
        "label": args.label, "items": len(items), "held_out": n,
        "legacy_grep_rate": legacy / len(items),
        "classifier_top1": acc, "chance": ch, "lift": acc - ch,
        "by_family": {k: v for k, v in per_family.items()},
        "top_tokens": disc,
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
