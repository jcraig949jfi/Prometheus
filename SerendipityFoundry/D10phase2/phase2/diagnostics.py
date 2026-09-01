"""Phase 2 section 14 -- POST-FREEZE diagnostics only.

The primary gate result is already written and hashed. Nothing here can
change the verdict; a failed Hamming PP2 is NOT rescued by an alternative
comparison. Two things are checked:

  (a) bit-permutation invariance -- a shared permutation of the 64 bit
      positions must leave Hamming retrieval identical. Failure would mean
      an implementation problem, not a scientific result.
  (b) descriptive reinterpretation of the IDENTICAL PP2 keys under two
      alternative supplied comparisons, reported for information only.
"""
import sys, json, random
import numpy as np
sys.path.insert(0, "d10")
from lib import organizer as og, pp2 as PP
from foundry.tasks.base import ExactTask
from foundry.core.seeds import derive_seed

D = json.load(open("d10/phase2/dataset.json"))
corpus = [bytes.fromhex(h) for h in D["corpus_hex"]]
ids = [f"a{i}" for i in range(len(corpus))]
gate = [(d["family"],
         ExactTask(train_cases=[(list(a), b) for a, b in d["train"]],
                   test_cases=[(list(a), b) for a, b in d["test"]]))
        for d in D["gate_tasks"]]
sel = json.load(open("d10/phase2/pp2_selection.json"))
KA = getattr(PP, sel["ka_fn"])(*sel["ka_args"])
KQ = getattr(PP, sel["kq_fn"])(*sel["kq_args"])
GEN = PP.make_genome(KA, KQ)
org = og.build_organization(GEN, ids, corpus)
qkeys = [og.query_key(GEN, t.evidence()) for _, t in gate]
K = 4

# ---- (a) bit-permutation invariance ----
rng = random.Random(4242)
perm = list(range(64)); rng.shuffle(perm)


def permute(k):
    out = 0
    for src, dst in enumerate(perm):
        if (k >> src) & 1:
            out |= 1 << dst
    return out


porg = og.Organization(org.artifact_ids, tuple(permute(k) for k in org.keys),
                       org.genome_addr, org.build_steps)
same = 0
for j in range(len(gate)):
    s = derive_seed(9302, "gateret", str(j))
    a = [x for x, _ in og.retrieve(org, qkeys[j], K, s)]
    b = [x for x, _ in og.retrieve(porg, permute(qkeys[j]), K, s)]
    same += int(a == b)
inv = {"tasks_with_identical_topk": same, "n_tasks": len(gate),
       "invariant": same == len(gate)}

# ---- (b) alternative supplied comparisons, descriptive only ----
keys = np.array(org.keys, dtype=object)


def topk_by(scorefn, qk):
    sc = [(scorefn(int(k), qk), i) for i, k in enumerate(org.keys)]
    sc.sort()
    return [ids[i] for _, i in sc[:K]]


def numeric(k, q):
    return abs(k - q)


def prefix(k, q):
    x = k ^ q
    return -(64 - x.bit_length())


overlap = {"numeric": [], "prefix": []}
for j in range(len(gate)):
    s = derive_seed(9302, "gateret", str(j))
    ham = [x for x, _ in og.retrieve(org, qkeys[j], K, s)]
    overlap["numeric"].append(
        len(set(ham) & set(topk_by(numeric, qkeys[j]))) / K)
    overlap["prefix"].append(
        len(set(ham) & set(topk_by(prefix, qkeys[j]))) / K)

res = {"bit_permutation_invariance": inv,
       "mean_topk_overlap_with_hamming": {
           "unsigned_numeric_distance": round(float(np.mean(overlap["numeric"])), 4),
           "common_prefix_length": round(float(np.mean(overlap["prefix"])), 4)},
       "note": ("Descriptive only. PP2 failed the frozen Hamming gate; these "
                "comparisons are NOT used to revisit that verdict.")}
print(json.dumps(res, indent=1))
json.dump(res, open("d10/phase2/diagnostics.json", "w"), indent=1)
