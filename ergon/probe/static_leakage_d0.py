"""Static D0 leakage check on REAL packets (Harmonia B's technique, numeric family).

Builds every D0 packet from the M30 pre-pass ledger, strips problem text, and asks: can a
blinded bag-of-words classifier recover the gold COUNT from the packet alone? Chance is ~0.25
on the balanced answer range {1,2,3,4}. Zero API cost. This is the pre-verification for
control C — HB ruling 4(ii): re-run the static probe first, only spend the live batch when
the static channel is at chance.
"""
import json, pathlib, re, sys
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ergon.probe.assemble import assemble_retrieved, load_prepass, select_residue  # noqa: E402

LEDGER = ROOT / "ergon/probe/ledgers/nearmiss_mix-M30_prepass.jsonl"
MANIFEST = ROOT / "ergon/probe/manifests/nearmiss_mix-M30_manifest_n200.jsonl"

rows = [json.loads(l) for l in MANIFEST.read_text(encoding="utf-8").splitlines()]
gold = {r["uid"]: r["gold_int"] for r in rows}
pool = load_prepass(LEDGER)
tau = {"nearmiss_mix-M30_prepass": 10_000}

texts, labels = [], []
leaks = 0
for r in rows:
    recs = select_residue(pool, stratum="D0", target_uid=r["uid"])
    if not recs:
        continue
    pkt = assemble_retrieved(task_uid=r["uid"], stratum="D0", records=recs, tau=tau)
    from ergon.probe.extract import leaks_numeric_answer
    if leaks_numeric_answer(pkt.body):
        leaks += 1
    texts.append(pkt.body)
    labels.append(gold[r["uid"]])

print(f"packets built: {len(texts)}  |  bodies still leaking an answer form: {leaks}")

# blinded bag-of-words, 5-fold CV, most-common-class baseline
tok = re.compile(r"[a-z]{3,}")
def feats(t): return Counter(tok.findall(t.lower()))
n = len(texts)
folds = [list(range(i, n, 5)) for i in range(5)]
correct = 0
for f in folds:
    train = [i for i in range(n) if i not in f]
    # per-class token log-odds (naive bayes-ish, add-1)
    cls_tok, cls_n = defaultdict(Counter), Counter()
    for i in train:
        cls_tok[labels[i]].update(feats(texts[i])); cls_n[labels[i]] += 1
    vocab = set()
    for c in cls_tok: vocab |= set(cls_tok[c])
    import math
    for i in f:
        ft = feats(texts[i])
        best, bs = None, -1e18
        for c in cls_tok:
            tot = sum(cls_tok[c].values()) + len(vocab)
            s = math.log(cls_n[c] / len(train))
            for w, k in ft.items():
                s += k * math.log((cls_tok[c][w] + 1) / tot)
            if s > bs: bs, best = s, c
        correct += (best == labels[i])
base = max(Counter(labels).values()) / n
acc = correct / n
import math as m
# exact binomial vs chance 0.25
pv = sum(m.comb(n, i) * 0.25**i * 0.75**(n-i) for i in range(correct, n+1))
print(f"recovery {acc:.3f} (n={n})  majority-baseline {base:.3f}  chance 0.25")
print(f"one-sided exact binomial vs 0.25: p = {pv:.4f}")
verdict = "PASS" if (pv > 0.05 and acc <= 0.35) else "FAIL"
print(f"STATIC-LEAKAGE: {verdict}  (rule: p>0.05 vs chance AND point <= 0.35)")
