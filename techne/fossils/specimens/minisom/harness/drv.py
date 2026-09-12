import numpy as np
from minisom import MiniSom
np.random.seed(1)
# three separated 2-D clusters
c=[np.random.randn(60,2)*0.3+m for m in ([0,0],[5,5],[0,5])]
X=np.vstack(c)
som=MiniSom(6,6,2,sigma=1.0,learning_rate=0.5,random_seed=1)
q0=som.quantization_error(X); som.train_random(X,1000); q1=som.quantization_error(X)
print("qerr_before %.4f qerr_after %.4f"%(q0,q1))
print("SOM_ORGANIZED" if q1<q0*0.6 else "SOM_WEAK")
