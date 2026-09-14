"""Techne harness (batch 06, phase 5): particle marginal Metropolis-Hastings (Andrieu, Doucet,
Holenstein 2010) as shipped in particles.mcmc.PMMH, on the package's own stochastic volatility
model. An OLD fossil made more useful: the specimen already held the bootstrap filter; PMMH wraps
it inside an MCMC over the model parameters. Parameter recovery is NOT asserted at this chain
length; the chain's movement is, and the posterior means are recorded as data."""
import numpy as np, particles
from particles import state_space_models as ssms, distributions as dists, mcmc
np.random.seed(3)
true = {"mu": -1.0, "rho": 0.9, "sigma": 0.3}
ssm = ssms.StochVol(**true); x, y = ssm.simulate(150)
prior = dists.StructDist({"mu": dists.Normal(scale=2.0), "rho": dists.Uniform(a=-1.0, b=1.0), "sigma": dists.Gamma(a=2.0, b=2.0)})
pmmh = mcmc.PMMH(ssm_cls=ssms.StochVol, prior=prior, data=y, Nx=100, niter=400, verbose=0)
pmmh.run()
th = pmmh.chain.theta
burn = 100
acc = float(np.mean(th["rho"][1:] != th["rho"][:-1]))
means = {k: float(np.mean(th[k][burn:])) for k in ("mu", "rho", "sigma")}
print("T=150 Nx=100 niter=400 burn=100; acceptance ~ %.3f" % acc)
print("true      :", true)
print("post. mean:", {k: round(v, 3) for k, v in means.items()})
ok = 0.02 < acc < 0.95
print("RESULT", "RUN: the PMMH chain moves (acceptance in (0.02, 0.95)); parameter recovery NOT asserted at 400 iterations / 100 particles" if ok else "FAIL (chain did not move)")
