"""How many evolve rows FORCE multi-hop transport by env placement (some world needs > 1 hop)?
hop range: ring/torus env distance <= radius is one hop (neighbour table = all sites within radius);
graphs/global: BFS distance 1 = one hop. SIGNAL rate split by forced vs not."""
import os; os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import sys, collections, numpy as np
sys.path.insert(0, __file__.rsplit("checks",1)[0]+"checks")
from rows import rows, ROOT
sys.path.insert(0, str(ROOT))
import torch; torch.set_num_threads(2)
from prometheus.ananke import envs, search
from prometheus.ananke.physics import Physics
from prometheus.ananke.assays import world_seeds
from prometheus.ananke.rng import H_int
tab=collections.defaultdict(lambda: collections.Counter())
for r in rows():
    if r['kind']!='evolve': continue
    fam=r['env']['family']
    if fam=='HOLD': continue
    ph=Physics.from_dict(r['physics']); env=envs.EnvSpec(**r['env'])
    ep=envs.build(ph, env, world_seeds(H_int(r['search_seed'], search.HELD_NS), 64))
    M=envs.dist_matrix(ph); si=ep.schedule.sense_idx.numpy(); ri=ep.schedule.read_idx.numpy()[:,0]
    hop = ph.radius if ph.topology in ('ring','torus') else 1
    if fam in ('RELAY','FLIP'): far=M[si[:,0],ri]
    elif fam=='MAJ': far=M[ri[:,None],si].max(1)
    else: far=np.maximum(M[si[:,0],ri], M[si[:,1],ri])
    frac_multi=float(np.mean(far>hop))
    k='multi_all' if frac_multi==1 else ('multi_some' if frac_multi>0 else 'one_hop')
    tab[(fam,k)]['n']+=1; tab[(fam,k)]['SIGNAL']+=r['labels']['SIGNAL']
for k in sorted(tab): print(k, dict(tab[k]))
