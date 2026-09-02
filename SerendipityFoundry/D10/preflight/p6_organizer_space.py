"""P6: reachability of non-degenerate organizations.

An organizer is useless in two ways: if every artifact gets the SAME key
(retrieval collapses to the tiebreak hash, i.e. exactly the uniform control)
or if every artifact gets a DISTINCT key with no structure (retrieval is an
arbitrary Hamming neighbourhood of a content hash). A usable organization
lives in between: it must group. This probe measures how much of the
organizer space random initialisation and mutation actually reach, because
an unreachable middle would make a null result a search failure, not a
hypothesis failure.
"""
import json, sys, statistics
sys.path.insert(0, "d10")
from lib.organizer import build_organization, decode
from foundry.engines.gp.stackvm.adapter import StackVMAdapter
from foundry.core.seeds import derive_seed

eng = StackVMAdapter()
N_ART = 300
genos = [eng.create_random(derive_seed(5, "corpus", f"#{i}")) for i in range(N_ART)]
ids = [f"a{i}" for i in range(N_ART)]

def bucket(d):
    if d <= 1: return "collapsed(1)"
    if d < 0.05 * N_ART: return "coarse(2..5%)"
    if d < 0.5 * N_ART: return "middle(5..50%)"
    if d < N_ART: return "fine(50..100%)"
    return "injective(100%)"

# -- random initialisation ------------------------------------------------
from collections import Counter
init = Counter(); dists = []
N_RAND = 600
for i in range(N_RAND):
    g = eng.create_random(derive_seed(77, "orgspace", f"#{i}"))
    o = build_organization(g, ids, genos)
    d = o.stats()["n_distinct_keys"]
    init[bucket(d)] += 1; dists.append(d)

# -- mutational reachability from collapsed seeds -------------------------
walks = Counter(); reached_middle = 0
N_WALK, WALK_LEN = 60, 40
for w in range(N_WALK):
    g = eng.create_random(derive_seed(78, "walk", f"#{w}"))
    hit = False
    for step in range(WALK_LEN):
        g = eng.mutate(g, derive_seed(78, "walkmut", f"#{w}", f"#{step}"))
        d = build_organization(g, ids, genos).stats()["n_distinct_keys"]
        b = bucket(d)
        walks[b] += 1
        if b in ("coarse(2..5%)", "middle(5..50%)"): hit = True
    reached_middle += int(hit)

out = {"n_artifacts": N_ART,
       "random_init_buckets": dict(init),
       "random_init_n": N_RAND,
       "median_distinct_keys": statistics.median(dists),
       "mutation_walk_buckets": dict(walks),
       "walks_reaching_grouping": f"{reached_middle}/{N_WALK}",
       "walk_len": WALK_LEN}
print(json.dumps(out, indent=1))
json.dump(out, open("d10/preflight/p6.json","w"), indent=1)
