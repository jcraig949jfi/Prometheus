"""Selection-to-ruler coupling, CPU. For a fixed sample of non-SIGNAL evolve cells (first 6 per comm
family by cell_id order), compare the RECORDED champion twin readings (REACH_BEYOND_HOP inputs,
persist, div_frac_readout) with 16 RANDOM genomes (search.random_genomes) at the same physics/env on
the same 16 held-out worlds. Also replay the champion twin on CPU and check it equals the record."""
import os; os.environ["CUDA_VISIBLE_DEVICES"]="-1"; os.environ["OMP_NUM_THREADS"]="2"
import sys, time, numpy as np, json
sys.path.insert(0, __file__.rsplit("checks",1)[0]+"checks")
from rows import rows, ROOT
sys.path.insert(0, str(ROOT))
import torch; torch.set_num_threads(2); assert not torch.cuda.is_available()
from prometheus.ananke import assays, envs, search
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
t0=time.time()
R=sorted([r for r in rows() if r['kind']=='evolve' and r['wave']=='A' and not r['labels']['SIGNAL']], key=lambda r:r['cell_id'])
out=[]
for fam in ("RELAY","MAJ","FLIP","XOR"):
    for r in [x for x in R if x['env']['family']==fam][:6]:
        ph=Physics.from_dict(r['physics']); env=envs.EnvSpec(**r['env'])
        hs=assays.world_seeds(H_int(r['search_seed'], search.HELD_NS), 64)[:16]
        champ=np.asarray(r['result']['champion'])
        tw=assays.twin_assay(ph, champ[None], env, hs, device="cpu")
        rep={k: float(v[0]) for k,v in tw.items() if k in r['result']['twin']}
        replay_ok = all(abs(rep[k]-r['result']['twin'][k])<1e-9 for k in rep)
        G=search.random_genomes(np.random.default_rng(H_int(r['search_seed'],0x5A5A)), 16, ph)
        tr=assays.twin_assay(ph, G, env, hs, device="cpu")
        o={"cell":r['cell_id'][:8],"fam":fam,"topo":ph.topology,"held":r['result']['held']['acc'],"replay_ok":replay_ok,
           "champ_beyond_hop":r['result']['twin']['beyond_hop'],"champ_persist":r['result']['twin']['persist'],
           "champ_divro":r['result']['twin']['div_frac_readout'],
           "rand_beyond_hop":float(tr['beyond_hop'].mean()),"rand_persist":float(tr['persist'].mean()),
           "rand_divro":float(tr['div_frac_readout'].mean()),"rand_any_div":float((tr['reach']>0).mean())}
        out.append(o); print(o, flush=True)
f=lambda k: np.mean([o[k] for o in out])
print("MEANS champ beyond_hop %.3f persist %.2f divro %.3f | random beyond_hop %.3f persist %.2f divro %.3f | replay_ok %d/%d | wall %.0fs"%(
    f('champ_beyond_hop'),f('champ_persist'),f('champ_divro'),f('rand_beyond_hop'),f('rand_persist'),f('rand_divro'),
    sum(o['replay_ok'] for o in out),len(out),time.time()-t0))
json.dump(out, open(__file__.rsplit("checks",1)[0]+"checks/c8_out.json","w"), indent=1)
