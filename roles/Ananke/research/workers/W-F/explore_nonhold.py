"""POST-HOC exploratory (not in PLAN): non-HOLD readable cells only.
Same CV machinery; also JOINT site_acc+chan_acc complementarity."""
import collections, numpy as np
import analyze as A
rows = [r for r in A.load() if r["class"] != "UNREADABLE" and r["family"] != "HOLD"]
y = np.array([r["class"] for r in rows]); cnt = collections.Counter(y)
y = np.array([c if cnt[c] >= 5 else "OTHER" for c in y])
fam = np.array([r["family"] for r in rows])
X8 = np.array([[A.feats(r["physics"])[k] for k in A.P8] for r in rows])
X6 = np.array([[A.feats(r["physics"])[k] for k in A.P6] for r in rows])
F = np.array([[float(f == g) for g in A.FAMS] for f in fam])
cvr, gains, strat = A.cv(X8, X6, F, y, fam)
print("n", len(rows), dict(collections.Counter(y)), "strat", strat)
for k, v in cvr.items(): print(k, round(v["mean"], 3))
print("gain", round(np.mean(gains), 3), np.percentile(gains, [2.5, 97.5]).round(3))
from sklearn.tree import DecisionTreeClassifier, export_text
print(export_text(DecisionTreeClassifier(max_depth=2, random_state=0).fit(X8, y), feature_names=A.P8))
s = [r["mid"]["site_all"]["acc"][0] + r["mid"]["channel_all"]["acc"][0] for r in A.load()
     if r.get("class") == "JOINT"]
print("JOINT site_acc+chan_acc", np.round(s, 2), "mean", round(float(np.mean(s)), 3))
# distinct physics points among non-HOLD readable
pts = collections.Counter(tuple(sorted((k, str(v)) for k, v in r["physics"].items() if k != "topo_seed")) for r in rows)
print("distinct physics points (non-HOLD readable):", len(pts))
