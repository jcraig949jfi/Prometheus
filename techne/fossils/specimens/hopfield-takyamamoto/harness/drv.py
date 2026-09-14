import os; os.environ.setdefault('MPLBACKEND','Agg')
import numpy as np
from network import HopfieldNetwork        # the repo's own class (imports matplotlib/tqdm)
np.random.seed(1)
N=25
P=[np.where(np.random.rand(N)>0.5,1,-1).astype(float),
   np.where(np.random.rand(N)>0.5,1,-1).astype(float)]
net=HopfieldNetwork(); net.train_weights(P)          # Hebbian store, the repo's code
cue=P[0].copy(); idx=np.random.choice(N,3,replace=False); cue[idx]*=-1   # corrupt 3 bits
out=np.asarray(net.predict([cue], num_iter=30, threshold=0, asyn=False)[0])
ok = np.array_equal(out,P[0]) or np.array_equal(out,-P[0])
print("N=%d stored=2 corrupted=3 recovered=%s"%(N,bool(ok)))
print("HOPFIELD_OK" if ok else "HOPFIELD_SPURIOUS")
