"""Phase 2 section 5: artifact-side reconstruction audit.

After the D1 repair, enumerate exactly what KA may observe, then try to
RECONSTRUCT nuisance variables from those admissible observations. The
question is not "is the forbidden field present" but "can the forbidden
quantity be recovered from what remains".

Two categories are reported separately and must not be conflated:
  SUPPLIED     an experimenter-authored channel that hands over the
               quantity (disqualifying);
  INTRINSIC    a genuine correlation between a genotype's own syntax and
               its origin, which the substrate and history create
               (legitimate, but it must be measured and controlled).

Reconstruction is given its BEST SHOT: rich offline features (full byte
histogram, opcode histogram, length, word statistics) and a real
classifier, none of which KA could compute within KEY_MAX_STEPS. An upper
bound on reconstructibility is what we want here.
"""
import sys, json, collections
import numpy as np
sys.path.insert(0, "d10")
from lib import organizer as og
from foundry.engines.gp.stackvm import vm
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import cross_val_score, cross_val_predict

D = json.load(open("d10/phase2/dataset.json"))
corpus = [bytes.fromhex(h) for h in D["corpus_hex"]]
prov = D["corpus_prov"]
print(f"corpus={len(corpus)}")


def admissible_words(g):
    """EXACTLY what KA receives after the D1 repair."""
    return og.artifact_words(g)


def rich_features(g):
    """Offline upper-bound featurisation of the admissible observation.

    Everything here is a function of the 24 content words KA receives (i.e.
    the first 192 genotype bytes) plus the number of those words. Nothing
    oracle-side enters.
    """
    w = admissible_words(g)
    vis = g[:og.MAX_ARTIFACT_WORDS * 8]          # the bytes KA can see
    arr = (np.frombuffer(vis, dtype=np.uint8) if vis
           else np.zeros(0, dtype=np.uint8))
    bh = np.bincount(arr, minlength=256).astype(float)
    oh = np.bincount(np.array([b % vm.N_OPCODES for b in vis], dtype=int)
                     if vis else np.zeros(0, dtype=int),
                     minlength=vm.N_OPCODES).astype(float)
    trail = 0                                     # trailing zero bytes of last word
    if vis:
        last = vis[(len(vis) - 1) // 8 * 8:]
        trail = 8 - len(last)
    return np.concatenate([
        bh, oh,
        [float(len(w)),                           # number of words (INTRINSIC)
         float(trail),                            # len mod 8 padding (SUPPLIED artifact)
         float(arr.mean()) if arr.size else 0.0,
         float(arr.std()) if arr.size else 0.0],
    ])


X = np.stack([rich_features(g) for g in corpus])
Lens = np.array([len(g) for g in corpus])
print(f"feature dim={X.shape[1]}")

targets = {}
targets["source_family"] = np.array([p["family"] for p in prov])
targets["source_hist_task"] = np.array([p["hist_task"] for p in prov])
targets["restart_phase"] = np.array([p["restart"] for p in prov])
targets["corpus_admission_source"] = np.array(
    [{"solver": 0, "final_population": 1, "subsample": 2}[p["source"]]
     for p in prov])
targets["is_solver"] = np.array([int(p["source"] == "solver") for p in prov])

# multiplicity: how many times the genotype appeared in the raw history
# (corpus is content-deduped, so this is a property we recorded, not one
# the corpus retains)
res = {"n_corpus": len(corpus), "feature_dim": int(X.shape[1])}

# ---- genotype length: regression, since it is continuous ----
rf = RandomForestRegressor(n_estimators=60, random_state=0, n_jobs=-1)
pred = cross_val_predict(rf, X, Lens, cv=4)
ss_res = float(np.sum((Lens - pred) ** 2))
ss_tot = float(np.sum((Lens - Lens.mean()) ** 2))
res["genotype_length"] = {
    "kind": "regression", "r2": round(1 - ss_res / ss_tot, 4),
    "baseline_r2": 0.0,
    "note": "INTRINSIC after D1: word COUNT and zero-padding remain",
}

for name, y in targets.items():
    mask = y >= 0
    yy, XX = y[mask], X[mask]
    if len(set(yy.tolist())) < 2:
        res[name] = {"skipped": "single class"}
        continue
    maj = collections.Counter(yy.tolist()).most_common(1)[0][1] / len(yy)
    clf = RandomForestClassifier(n_estimators=60, random_state=0, n_jobs=-1)
    acc = float(np.mean(cross_val_score(clf, XX, yy, cv=4, n_jobs=-1)))
    res[name] = {"kind": "classification", "n": int(len(yy)),
                 "n_classes": int(len(set(yy.tolist()))),
                 "accuracy": round(acc, 4),
                 "majority_baseline": round(maj, 4),
                 "lift_over_baseline": round(acc - maj, 4)}
    print(f"{name:26s} acc={acc:.4f} maj={maj:.4f} lift={acc-maj:+.4f}",
          flush=True)

# ---- how much of the family signal is carried by LENGTH ALONE? ----
fam = targets["source_family"]
m = fam >= 0
clf = RandomForestClassifier(n_estimators=60, random_state=0, n_jobs=-1)
acc_len = float(np.mean(cross_val_score(clf, Lens[m].reshape(-1, 1), fam[m],
                                        cv=4, n_jobs=-1)))
res["source_family_from_length_only"] = round(acc_len, 4)
print(f"source_family from LENGTH ONLY: acc={acc_len:.4f}")

print(json.dumps(res, indent=1))
json.dump(res, open("d10/phase2/reconstruct_audit.json", "w"), indent=1)
