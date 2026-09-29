"""Step 1 + instrument checks.
(a) rebuild the C4-01 census children of the 19 shelf parents from their seeds, re-score on
    W2_K2 with the fast scorer, compare with the committed rows AND with evaluate();
(b) S3 outcome table on the 1,568 eligible;
(c) hand-written summit and planted control scores (train and held-out)."""
import collections as C
import gzip
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r4lib as L
from archaeon.wse.evolve import evaluate

t0 = time.time()
rows = json.loads(gzip.open(os.path.join(L.REPO, "archaeon/campaign4/C4-01/attempts/a02/children.json.gz")).read())
pop = json.load(open(os.path.join(L.REPO, "archaeon/campaign4/STARTING_POPULATION.json")))
shelf = {o["organism_id"]: o["manifest"] for o in pop["organisms"] if o["class"] == "shelf"}
eps = L.episodes()
exp = L.expected_vector(eps)

out = {"n_shelf": len(shelf)}
mism_rows = mism_eval = checked_eval = 0
oc = C.Counter()
n_elig = 0
for x in rows:
    if x["parent_id"] not in shelf or x["operator"].startswith("control_"):
        continue
    pm = shelf[x["parent_id"]]
    rng = L.SplitMix64(L.seed_from("c4.01.edit", L.CAMPAIGN_SEED, x["parent_id"], x["operator"], x["draw"]))
    try:
        child, rec = L.GR.mutate(pm, rng, mate=None, name=x["operator"])
    except L.ManifestError:
        continue
    if not x["applied"]:
        continue
    a = L.answers(child, eps)
    r = L.score(a, exp)
    if abs(r - x["evals"]["W2_K2"]["reward_per_ask"]) > 1e-12:
        mism_rows += 1
    if checked_eval < 600:
        ev = evaluate(child, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
        checked_eval += 1
        if abs(ev - r) > 1e-12:
            mism_eval += 1
    pr = x["parent_reward"]
    n_elig += 1
    vals = [v for v in a if v is not None]
    degenerate = (not vals) or (len(set(vals)) == 1 and len(vals) == len(a))
    if r > pr + L.BAND + L.EPS:
        oc["improved"] += 1
    elif degenerate or r <= L.EPS:
        oc["lethal"] += 1
    elif abs(r - pr) <= L.BAND + L.EPS:
        oc["neutral"] += 1
    else:
        oc["deleterious"] += 1
out["eligible_rebuilt"] = n_elig
out["outcomes"] = dict(oc)
out["mismatch_vs_committed_rows"] = mism_rows
out["fast_vs_evaluate_checked"] = checked_eval
out["fast_vs_evaluate_mismatch"] = mism_eval
out["s3_table_reproduced"] = (n_elig == 1568 and oc == C.Counter(improved=0, neutral=967, deleterious=74, lethal=527)) or dict(oc)

held = L.episodes("train", 2, 64)
hexp = L.expected_vector(held)
for name, g in (("summit", L.summit_genome(0)), ("planted_1clobber", L.summit_genome(1)), ("planted_2clobber", L.summit_genome(2))):
    m = L.manifest_of(g)
    a = L.answers(m, eps)
    out[name] = {"train": L.score(a, exp), "train_evaluate": evaluate(m, eps, rng_seed=0)["reward_per_ask"],
                 "heldout64": L.score(L.answers(m, held), hexp), "instr": len(g) // 4,
                 "episode_all_correct": L.episode_score(a, exp)}
for pid, pm in shelf.items():
    a = L.answers(pm, eps)
    out.setdefault("shelf_parents", {})[pid[:12]] = {"train": L.score(a, exp), "heldout64": L.score(L.answers(pm, held), hexp),
                                                     "episode_all_correct": L.episode_score(a, exp),
                                                     "lev_to_summit": L.levenshtein_instr(pm["genome"], L.summit_genome(0))}
out["wall_s"] = round(time.time() - t0, 1)
json.dump(out, open(os.path.join(L.HERE, "step1_result.json"), "w"), indent=1, sort_keys=True)
print(json.dumps(out, indent=1, sort_keys=True))
