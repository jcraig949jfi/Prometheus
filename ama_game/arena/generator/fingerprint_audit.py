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


def ablate(text: str, mode: str, rng: random.Random) -> str:
    """Representations that keep surface form and destroy mathematical content.

    The decisive question is not whether the planted step is predictable — a
    domain-widening step SHOULD attract scrutiny, and legitimate mathematics
    predicts where mistakes live. The question is whether it can be identified
    WITHOUT checking the mathematics. These ablations answer it:

      full             the step as written
      digits_masked    every numeral -> '#'. Arithmetic relations destroyed,
                       syntax, kind, length and word choice preserved.
      digits_shuffled  every numeral -> a random numeral of the same width.
                       Numbers still present, relations between them gone.
      skeleton         numerals masked AND every identifier collapsed. Only the
                       grammatical frame of the step survives.

    If the lift survives digit masking, something identifies the planted step
    without arithmetic, and that is leakage. If the lift disappears and returns
    only when real digits return, the residue is mathematics.
    """
    if mode == "full":
        return text
    if mode == "digits_masked":
        return re.sub(r"\d+", "#", text)
    if mode == "digits_shuffled":
        return re.sub(r"\d+",
                      lambda m: "".join(str(rng.randint(0, 9)) for _ in m.group()),
                      text)
    if mode == "skeleton":
        t = re.sub(r"\d+", "#", text)
        return re.sub(r"[a-zA-Z_]{1,3}", "V", t)
    raise ValueError(mode)


def tokens(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z_]+|\d+|[<>=^+*/%-]+", text.lower())
    return words + [f"{a}|{b}" for a, b in zip(words, words[1:])]


def build_items(n: int, seed: int, gen_dir: Path, fast: bool = False) -> list[dict]:
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
            "t4_linear_recurrence"]
    if not fast:
        tids.append("t5_collatz_stopping_time")   # exhaustive sweeps: slow
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


def train_nb(items: list[dict], mode="full", rng=None):
    pos, neg = Counter(), Counter()
    npos = nneg = 0
    for it in items:
        for s in it["steps"]:
            bag = pos if s["id"] == it["target"] else neg
            bag.update(tokens(ablate(s["text"], mode, rng)))
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
    p.add_argument("--fast", action="store_true",
                   help="skip the iterated-map template, whose exhaustive "
                        "sweeps dominate build time and carry no extra prose")
    args = p.parse_args()

    items = build_items(args.items, args.seed, Path(args.generator_dir).resolve(),
                        args.fast)
    rng = random.Random(args.seed)
    rng.shuffle(items)
    cut = int(len(items) * 0.6)
    train, test = items[:cut], items[cut:]

    ablations = {}
    for mode in ("full", "digits_masked", "digits_shuffled", "skeleton"):
        arng = random.Random(99)
        lp, ln, prior, vocab = train_nb(train, mode, arng)
        arng = random.Random(99)
        hits, chance, per_family = 0, 0.0, defaultdict(lambda: [0, 0])
        for it in test:
            shuffled = list(it["steps"])
            arng.shuffle(shuffled)          # break score ties at random, not by
            ranked = max(shuffled,          # position: argmax on equal scores
                         key=lambda s: score(ablate(s["text"], mode, arng),
                                             lp, ln, prior, vocab))
            ok = ranked["id"] == it["target"]
            hits += ok
            chance += 1 / len(it["steps"])
            per_family[it["family"]][0] += ok
            per_family[it["family"]][1] += 1
        ablations[mode] = {"top1": hits / len(test), "chance": chance / len(test),
                           "by_family": dict(per_family)}
        if mode == "full":
            full_family = per_family

    lp, ln, prior, vocab = train_nb(train, "full", random.Random(99))
    per_family = full_family
    n = len(test)
    acc, ch = ablations["full"]["top1"], ablations["full"]["chance"]

    # positional baseline: index alone, no text whatsoever
    pos_counts, pos_tot = Counter(), Counter()
    for it in train:
        for i, st in enumerate(it["steps"]):
            pos_tot[i] += 1
            if st["id"] == it["target"]:
                pos_counts[i] += 1
    prng2 = random.Random(5)
    phits, pch = 0, 0.0
    for it in test:
        idx = list(range(len(it["steps"])))
        prng2.shuffle(idx)
        best = max(idx, key=lambda i: (pos_counts[i] + 1) / (pos_tot[i] + 2))
        phits += it["steps"][best]["id"] == it["target"]
        pch += 1 / len(it["steps"])
    ablations["position_only"] = {"top1": phits / len(test),
                                  "chance": pch / len(test), "by_family": {}}

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
    L.append("NEGATIVE CONTROL — is the residue mathematics, or leakage?")
    L.append("  Same classifier on representations that keep surface form and")
    L.append("  destroy mathematical content. Leakage survives digit masking;")
    L.append("  mathematics does not.")
    L.append("")
    L.append(f"    {'representation':<18s} {'top-1':>8s} {'chance':>8s} {'lift':>8s}")
    for mode, r in ablations.items():
        L.append(f"    {mode:<18s} {r['top1']:>7.1%} {r['chance']:>8.1%} "
                 f"{r['top1'] - r['chance']:>+8.1%}")
    L.append("")
    sk = ablations["skeleton"]["by_family"]
    if sk:
        L.append("  which families are identifiable with ALL content destroyed:")
        for fam, (h, t) in sorted(sk.items(), key=lambda kv: -kv[1][0] / max(1, kv[1][1])):
            if t:
                L.append(f"    {fam.split('_')[0]:<4s} {h}/{t}  "
                         f"{h/t:>5.0%}")
        L.append("")

    masked_lift = ablations["digits_masked"]["top1"] - ablations["digits_masked"]["chance"]
    skel_lift = ablations["skeleton"]["top1"] - ablations["skeleton"]["chance"]
    full_lift = acc - ch
    content_dependent = full_lift - max(masked_lift, skel_lift)

    L.append(f"  lift that requires real digits: {content_dependent:+.1%}")
    L.append(f"  lift surviving content removal: {max(masked_lift, skel_lift):+.1%}")
    L.append("")
    if max(masked_lift, skel_lift) < 0.04:
        L.append("VERDICT: PASS. The residual signal disappears once arithmetic")
        L.append("content is destroyed and returns only when real digits return.")
        L.append("The planted step cannot be found without checking the")
        L.append("mathematics, which is the standard that matters. Above-chance")
        L.append("predictability from content is not leakage - legitimate")
        L.append("mathematics predicts where mistakes live.")
    elif max(masked_lift, skel_lift) < 0.10:
        L.append("VERDICT: UNRESOLVED. Some signal survives content removal, but")
        L.append("weakly. Neither a clean pass nor a demonstrated fingerprint.")
        L.append("Do not report this as fixed.")
    else:
        L.append("VERDICT: FAIL. The planted step is identifiable with the")
        L.append("arithmetic destroyed, so a falsifier can skip the mathematics.")

    text = "\n".join(L)
    print(text)
    out = HERE / f"FINGERPRINT_{args.label}.json"
    out.write_text(json.dumps({
        "label": args.label, "items": len(items), "held_out": n,
        "legacy_grep_rate": legacy / len(items),
        "classifier_top1": acc, "chance": ch, "lift": acc - ch,
        "by_family": {k: v for k, v in per_family.items()},
        "top_tokens": disc, "ablations": ablations,
        "lift_requiring_digits": content_dependent,
        "lift_surviving_content_removal": max(masked_lift, skel_lift),
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
