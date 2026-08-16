"""Control C — zero-API static leakage probe on REAL stripped D0 packets.

Owner: Harmonia B (meter integrity). Companion to control C in `ergon/probe/r3_controls.py`.

WHY THIS EXISTS. Control C as preregistered (§4.5) spends a solver batch asking whether gold
is recoverable from a verdict-stripped D0 packet with the problem text redacted. Verdict-token
redaction removes the literal `true`/`false`. It does NOT remove the trace's *semantic*
conclusion — a coprimality trace that says "their greatest common divisor is 1" has stated
the answer in domain language with no verdict token present.

So before spending the live batch, run the same question through a **blinded bag-of-words
classifier** (the R7 layer-(b) technique, pointed at gold instead of at arm identity). It is
deterministic, costs nothing, and gives a LOWER BOUND: whatever a unigram model can recover,
a frontier solver can recover at least as much.

READING THE RESULT
  clearly above chance  -> control C is predicted to FAIL live; fix the rendering first
                           rather than paying for the batch to tell you so.
  at chance             -> NOT a pass. A unigram model is weak; only the live batch can
                           pass control C. This probe can fail the packets, never clear them.

That asymmetry is deliberate and is the whole point: a cheap test that can only ever say
"broken", never "fine", cannot be used to wave the expensive test through.

Run:
    cd D:\\prometheus
    PYTHONPATH=. PYTHONIOENCODING=utf-8 python harmonia/probe/c_static_leakage_probe.py
"""
from __future__ import annotations

import json
import pathlib
import re
from collections import defaultdict

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.naive_bayes import MultinomialNB

from ergon.probe.assemble import (
    assemble_retrieved,
    leaks_verdict,
    load_prepass,
    select_residue,
    tau_from_records,
)
from ergon.probe.r3_controls import exact_binom_p_upper, C_MAX_P, C_MAX_POINT

LEDGER = pathlib.Path("ergon/probe/ledgers/probe_prepass.jsonl")
MANIFEST = pathlib.Path("ergon/probe/manifests/manifest_L1_n126.jsonl")


#: The provenance head line rendered into every ResidueRecord body:
#:   [probe_prepass:ood_coprime-L1-00000#r1 probe_prepass#65]
#: It carries the record's uid, and the uid's trailing index turns out to encode gold
#: (see `uid_index_oracle`). Stripping it separates the two leak channels.
_HEAD_LINE = re.compile(r"^\[[^\]]*\]\s*$", re.MULTILINE)
_UID_LIKE = re.compile(r"\b[a-z_]+-L\d-\d+(?:#r\d)?\b")
_LONGNUM = re.compile(r"\b\d{4,}\b")


def strip_identifiers(text: str) -> str:
    """Remove provenance identifiers, leaving only the residue prose + sparsity block."""
    t = _HEAD_LINE.sub("", text)
    t = _UID_LIKE.sub(" ", t)
    return t


def uid_index_oracle() -> dict:
    """Is gold recoverable from the uid alone? (manifest-generator property, not a
    packet property — but the packet ships the uid, so it becomes one.)"""
    man = [json.loads(l) for l in MANIFEST.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = []
    for d in man:
        m = re.search(r"-(\d+)$", d["uid"])
        rows.append((int(m.group(1)), bool(d["gold_bool"]), d["domain"]))
    # the trivial rule a reader would find: low index => True
    k = sum(1 for i, g, _ in rows if (i < 9) == g)
    per_dom = {}
    for _i, _g, dom in rows:
        per_dom.setdefault(dom, [0, 0])
    for i, g, dom in rows:
        per_dom[dom][1] += 1
        per_dom[dom][0] += int((i < 9) == g)
    return {"k": k, "n": len(rows), "acc": k / len(rows),
            "p": exact_binom_p_upper(k, len(rows)),
            "per_domain": {d: v[0] / v[1] for d, v in per_dom.items()}}


def build() -> tuple[list[str], list[int], list[str]]:
    man = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            man[d["uid"]] = d
    recs = load_prepass(LEDGER)
    tau = tau_from_records(recs)
    texts, gold, doms = [], [], []
    for uid in sorted({r.uid for r in recs}):
        sel = select_residue(recs, stratum="D0", target_uid=uid)
        if not sel or uid not in man:
            continue
        pk = assemble_retrieved(task_uid=uid, stratum="D0", records=sel, tau=tau)
        assert not leaks_verdict(pk.body), f"verdict token survived in {uid}"
        texts.append(pk.body)
        gold.append(int(bool(man[uid]["gold_bool"])))
        doms.append(man[uid]["domain"])
    return texts, gold, doms


def evaluate(texts, gold, label: str, ngram=(1, 1)):
    vec = CountVectorizer(ngram_range=ngram, min_df=2, lowercase=True)
    X = vec.fit_transform(texts)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=20260816)
    out = {}
    for name, clf in (("naive-bayes", MultinomialNB()),
                      ("logistic", LogisticRegression(max_iter=2000, C=1.0))):
        pred = cross_val_predict(clf, X, gold, cv=cv)
        k = int(sum(int(p == g) for p, g in zip(pred, gold)))
        n = len(gold)
        acc = k / n
        p = exact_binom_p_upper(k, n)
        verdict = "LEAK" if (p <= C_MAX_P or acc > C_MAX_POINT) else "no-unigram-leak"
        out[name] = (k, n, acc, p, verdict)
        print(f"  {label:<26s} {name:<12s} {k:3d}/{n:3d} = {acc:.4f}   "
              f"p(>=k|0.5)={p:.4g}   {verdict}")
    return out


def top_features(texts, gold, k=12):
    vec = CountVectorizer(min_df=3, lowercase=True)
    X = vec.fit_transform(texts)
    clf = LogisticRegression(max_iter=2000).fit(X, gold)
    names = vec.get_feature_names_out()
    coefs = clf.coef_[0]
    order = coefs.argsort()
    print("\n  tokens most predictive of gold=False:",
          ", ".join(names[i] for i in order[:k]))
    print("  tokens most predictive of gold=True :",
          ", ".join(names[i] for i in order[-k:][::-1]))


def main() -> int:
    texts, gold, doms = build()
    print("=" * 78)
    print("CONTROL C — static (zero-API) leakage probe on REAL stripped D0 packets")
    print("=" * 78)
    print(f"\npackets: {len(texts)}   gold True/False: {sum(gold)}/{len(gold)-sum(gold)}")
    print(f"domains: {len(set(doms))}   (chance = 0.50 by construction, 50/50 per domain)")
    print(f"\npass condition mirrors prereg §4.5: p > {C_MAX_P} AND point <= {C_MAX_POINT}\n")

    ora = uid_index_oracle()
    print("CHANNEL 0 — the uid itself (manifest-generator property):")
    print(f"  rule 'index < 9 => gold True' recovers {ora['k']}/{ora['n']} = "
          f"{ora['acc']:.4f}  p={ora['p']:.3g}")
    print("  per-domain: " + "  ".join(f"{d.replace('ood_','')}={v:.2f}"
                                       for d, v in sorted(ora["per_domain"].items())))
    print("  The generator lays gold out in BLOCKS by index (T*9 then F*9 in 6 of 7")
    print("  domains). Every D0 packet renders the record's uid into its body, so the")
    print("  packet ships this oracle whether or not the trace says anything.\n")

    print("CHANNEL 1+0 — full packet body, as it would be shipped (5-fold CV):")
    uni = evaluate(texts, gold, "as-shipped")
    bi = evaluate(texts, gold, "as-shipped uni+bi", ngram=(1, 2))

    stripped = [strip_identifiers(t) for t in texts]
    print("\nCHANNEL 1 ONLY — identifiers stripped, residue prose only:")
    uni_s = evaluate(stripped, gold, "prose-only")
    bi_s = evaluate(stripped, gold, "prose-only uni+bi", ngram=(1, 2))

    top_features(stripped, gold)

    worst = max(v[2] for v in list(uni_s.values()) + list(bi_s.values()))
    worst_p = min(v[3] for v in list(uni_s.values()) + list(bi_s.values()))
    shipped_worst = max(v[2] for v in list(uni.values()) + list(bi.values()))
    leaked = worst_p <= C_MAX_P or worst > C_MAX_POINT
    print(f"\n  as-shipped best {shipped_worst:.3f}   prose-only best {worst:.3f}   "
          f"uid-oracle {ora['acc']:.3f}")

    print("\n" + "-" * 78)
    if leaked:
        print(f"PREDICTED FAIL: a bag-of-words model recovers gold at {worst:.3f} "
              f"(p={worst_p:.3g}) from packets that carry NO verdict token.")
        print("Verdict-token redaction is not answer redaction — the trace restates its")
        print("conclusion in domain language ('gcd is 1', 'divisible by 7'). Control C")
        print("should be expected to fail live; fix the rendering before paying for it.")
    else:
        print(f"NO UNIGRAM LEAK DETECTED (best {worst:.3f}, p={worst_p:.3g}).")
        print("This does NOT clear control C. A unigram model is a weak reader; only the")
        print("live batch can pass it. This probe can fail the packets, never clear them.")
    print("-" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
