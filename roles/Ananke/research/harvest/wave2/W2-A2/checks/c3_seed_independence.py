"""Within-cell and cross-cell world-seed overlap between TRAIN (every gen), FINAL and HELD namespaces,
recomputed exactly from search.py's derivations for every evolve row."""
import os; os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import sys, collections
sys.path.insert(0, __file__.rsplit("checks",1)[0]+"checks")
from rows import rows, ROOT
sys.path.insert(0, str(ROOT))
from prometheus.ananke.rng import H_int
from prometheus.ananke import search
from prometheus.ananke.assays import world_seeds
R=[r for r in rows() if r['kind']=='evolve']
within=0; tr_all=collections.Counter(); he_all=collections.defaultdict(list)
ss=collections.Counter(r['search_seed'] for r in R)
print("evolve rows", len(R), "distinct search seeds", len(ss), "dupes", [(k,v) for k,v in ss.items() if v>1][:5])
for r in R:
    s=r['search_seed']; sp=r['search']
    tr=set()
    for gen in range(sp['gens']):
        tr |= set(world_seeds(H_int(s, search.TRAIN_NS, gen), sp['M']))
    fi=set(world_seeds(H_int(s, search.FINAL_NS), sp['M_final']))
    he=set(world_seeds(H_int(s, search.HELD_NS), sp['M_held']))
    within += len(he & (tr|fi))
    for x in tr|fi: tr_all[x]+=1
    for x in he: he_all[x].append(r['cell_id'])
cross=[(x,he_all[x]) for x in he_all if x in tr_all]
print("within-cell held AND (train OR final):", within)
print("cross-cell held seeds that are some cell's train/final seed:", len(cross), "(expected by 32-bit chance ~", round(len(tr_all)*len(he_all)/2**32,2),")")
dup_held=[x for x,v in he_all.items() if len(v)>1]
print("held seeds shared by >1 evolve cell:", len(dup_held))
