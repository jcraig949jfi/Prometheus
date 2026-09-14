import numpy as np, emcee
np.random.seed(2)
ndim, nwalkers = 5, 32
A = np.random.rand(ndim, ndim); cov = 0.5 - np.random.rand(ndim ** 2).reshape((ndim, ndim)); cov = np.triu(cov); cov += cov.T - np.diag(cov.diagonal()); cov = np.dot(cov, cov)
icov = np.linalg.inv(cov); mu = np.arange(ndim) * 0.5
def log_prob(x):
    d = x - mu
    return -0.5 * d @ icov @ d
p0 = mu + 0.1 * np.random.randn(nwalkers, ndim)
s = emcee.EnsembleSampler(nwalkers, ndim, log_prob)
s.run_mcmc(p0, 6000, progress=False)
chain = s.get_chain(discard=1000, flat=True)
m = chain.mean(axis=0); c = np.cov(chain.T)
mean_err = float(np.abs(m - mu).max()); cov_rel = float(np.abs(c - cov).max() / np.abs(cov).max())
af = float(np.mean(s.acceptance_fraction))
try:
    tau = s.get_autocorr_time(quiet=True); tau_max = float(np.max(tau))
except Exception as e:
    tau_max = float("nan")
print("samples=%d mean_err=%.3f cov_rel_err=%.3f acceptance=%.3f tau_max=%.1f" % (len(chain), mean_err, cov_rel, af, tau_max))
print("RESULT", "OK" if (mean_err < 0.1 and cov_rel < 0.15 and 0.15 < af < 0.7) else "FAIL")
