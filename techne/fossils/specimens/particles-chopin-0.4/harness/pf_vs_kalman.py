import numpy as np
import particles
from particles import state_space_models as ssms
from particles import kalman
from particles.collectors import Moments
np.random.seed(1)
ssm = kalman.LinearGauss(rho=0.9, sigmaX=1.0, sigmaY=0.5)
x, y = ssm.simulate(200)
kf = kalman.Kalman(ssm=ssm, data=y); kf.filter()
kmeans = np.array([m.mean.item() for m in kf.filt])
fk = ssms.Bootstrap(ssm=ssm, data=y)
pf = particles.SMC(fk=fk, N=5000, resampling="systematic", collect=[Moments()], verbose=False)
pf.run()
pmeans = np.array([m["mean"] for m in pf.summaries.moments])
rmse = float(np.sqrt(np.mean((pmeans - kmeans) ** 2)))
print("T=%d N=5000 rmse(PF mean, Kalman mean)=%.4f  final ESS-ish logLt=%.2f" % (len(y), rmse, pf.summaries.logLts[-1]))
print("first 5 Kalman means:", np.round(kmeans[:5], 3))
print("first 5 PF     means:", np.round(pmeans[:5], 3))
print("RESULT", "OK" if rmse < 0.1 else "FAIL")
