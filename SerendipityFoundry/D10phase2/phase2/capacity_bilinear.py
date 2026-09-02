"""Phase 2, decisive information-level upper bound (DEV ONLY).

Any KA/KQ + Hamming scheme computes
    score(a,t) = -popcount(KA(a) XOR KQ(t))
which is a bilinear form in the +/-1 bit embeddings of the two sides:
    -popcount(x XOR y) = (x.y - 64)/2   for x,y in {-1,+1}^64.
So a general fitted BILINEAR model over rich admissible features is a
STRICT SUPERSET of what the declared interface can express -- it is not
limited to 64 bits, not limited to the VM step cap, and not limited to
programs a human can write.

If that superset cannot capture the conditional relevance signal on
held-out families, then no admissible KA/KQ pair can either, and the
failure is INFORMATIONAL rather than a failure of human ingenuity or of
VM expressivity.

Reported both in-sample and leave-one-family-out, because the difference
separates "the functional form cannot express it" from "it exists but does
not generalise across families".
"""
import sys, json
import numpy as np
sys.path.insert(0, "d10")
from lib import organizer as og
from foundry.engines.gp.stackvm import vm
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge

K = 4
D = json.load(open("d10/phase2/dataset.json"))
corpus = [bytes.fromhex(h) for h in D["corpus_hex"]]
dev = [(d["family"], d["train"]) for d in D["dev_tasks"]]
R = np.load("d10/phase2/relevance_dev.npy")
fams = np.array([f for f, _ in dev])
VIS = og.MAX_ARTIFACT_WORDS * 8
print(f"corpus={len(corpus)} dev={len(dev)} R={R.shape}", flush=True)


def artifact_feat(g):
    vis = g[:VIS]
    a = np.frombuffer(vis, dtype=np.uint8) if vis else np.zeros(0, np.uint8)
    bh = np.bincount(a, minlength=256).astype(float)
    oh = np.bincount((a % vm.N_OPCODES) if a.size else np.zeros(0, int),
                     minlength=vm.N_OPCODES).astype(float)
    n = max(len(vis), 1)
    return np.concatenate([bh / n, oh / n,
                           [len(og.artifact_words(g)), np.log1p(len(g))]])


def query_feat(train):
    outs = np.array([o for _, o in train], float)
    ins = np.array([v for i, _ in train for v in i], float)
    oh = np.bincount((outs.astype(int) % 256), minlength=256).astype(float)
    ih = np.bincount((ins.astype(int) % 256), minlength=256).astype(float)
    return np.concatenate([
        oh / len(outs), ih / max(len(ins), 1),
        [outs.mean(), outs.std(), outs.min(), outs.max(),
         len(set(outs.tolist())), ins.mean(), ins.std()]])


FA = np.stack([artifact_feat(g) for g in corpus])
GT = np.stack([query_feat(t) for _, t in dev])
FA = (FA - FA.mean(0)) / (FA.std(0) + 1e-9)
GT = (GT - GT.mean(0)) / (GT.std(0) + 1e-9)
da = min(40, FA.shape[0], FA.shape[1])
dt = min(12, GT.shape[0] - 1, GT.shape[1])
FA = PCA(n_components=da, random_state=0).fit_transform(FA)
GT = PCA(n_components=dt, random_state=0).fit_transform(GT)
FA = np.hstack([FA, np.ones((FA.shape[0], 1))])
GT = np.hstack([GT, np.ones((GT.shape[0], 1))])
print(f"artifact dims={FA.shape[1]} query dims={GT.shape[1]} "
      f"-> bilinear params={FA.shape[1]*GT.shape[1]}", flush=True)

glob = np.argsort(-R.mean(axis=1), kind="stable")[:K]
ref_global = float(np.mean([R[glob, j].mean() for j in range(R.shape[1])]))
ref_oracle = float(np.mean([np.sort(R[:, j])[-K:].mean()
                            for j in range(R.shape[1])]))
ref_unif = float(R.mean())
span = ref_oracle - ref_global


def build(js):
    X, y = [], []
    for j in js:
        X.append((FA[:, :, None] * GT[j][None, None, :]).reshape(len(corpus), -1))
        y.append(R[:, j])
    return np.vstack(X), np.concatenate(y)


def topk_rel(scores, j):
    return float(R[np.argsort(-scores, kind="stable")[:K], j].mean())


def evaluate(train_js, test_js, alpha=10.0):
    X, y = build(train_js)
    m = Ridge(alpha=alpha).fit(X, y)
    out = []
    for j in test_js:
        Xj = (FA[:, :, None] * GT[j][None, None, :]).reshape(len(corpus), -1)
        out.append(topk_rel(m.predict(Xj), j))
    return float(np.mean(out))


alljs = list(range(len(dev)))
insample = evaluate(alljs, alljs)
lofo = []
for held in sorted(set(fams.tolist())):
    te = [j for j in alljs if fams[j] == held]
    tr = [j for j in alljs if fams[j] != held]
    if te and tr:
        lofo.append(evaluate(tr, te))
lofo_m = float(np.mean(lofo))

res = {"uniform": round(ref_unif, 5), "global_best": round(ref_global, 5),
       "cond_oracle": round(ref_oracle, 5), "conditional_span": round(span, 5),
       "bilinear_in_sample": {
           "mean_topk_relevance": round(insample, 5),
           "capture_of_conditional_span": round((insample - ref_global) / span, 4)},
       "bilinear_leave_one_family_out": {
           "mean_topk_relevance": round(lofo_m, 5),
           "capture_of_conditional_span": round((lofo_m - ref_global) / span, 4),
           "per_family": [round(x, 5) for x in lofo]}}
print(json.dumps(res, indent=1))
json.dump(res, open("d10/phase2/capacity_bilinear.json", "w"), indent=1)
