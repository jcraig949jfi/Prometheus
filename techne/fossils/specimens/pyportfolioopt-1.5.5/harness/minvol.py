import numpy as np, pandas as pd, glob
from pypfopt import EfficientFrontier, expected_returns, risk_models
paths = glob.glob("tests/resources/stock_prices.csv") + glob.glob("**/stock_prices.csv", recursive=True)
if paths:
    df = pd.read_csv(paths[0], parse_dates=True, index_col="date"); print("data:", paths[0])
else:
    # the PyPI sdist ships no tests/resources: a seeded synthetic 3-factor market, 20 assets, 750 days
    rng = np.random.default_rng(7); n_assets, n_days = 20, 750
    load = rng.normal(0, 1, (n_assets, 3)); fac = rng.normal(0, 0.01, (n_days, 3)); idio = rng.normal(0, 0.008, (n_days, n_assets)) * rng.uniform(0.5, 2.0, n_assets)
    rets = fac @ load.T * 0.6 + idio + 0.0003
    df = pd.DataFrame(100 * np.cumprod(1 + rets, axis=0), columns=["A%02d" % i for i in range(n_assets)], index=pd.bdate_range("2020-01-01", periods=n_days))
    print("data: SYNTHETIC seeded factor market (sdist has no tests/resources)")
mu = expected_returns.mean_historical_return(df); S = risk_models.sample_cov(df)
ef = EfficientFrontier(mu, S); w = ef.min_volatility(); w = ef.clean_weights()
wv = np.array([w[k] for k in df.columns]); var_min = float(wv @ S.values @ wv)
we = np.ones(len(df.columns)) / len(df.columns); var_eq = float(we @ S.values @ we)
print("assets=%d sum(w)=%.6f min(w)=%.6f nonzero=%d" % (len(wv), wv.sum(), wv.min(), int((wv > 1e-6).sum())))
print("annual variance: min-vol=%.6f equal-weight=%.6f" % (var_min, var_eq))
ok = abs(wv.sum() - 1) < 1e-4 and wv.min() > -1e-6 and var_min < var_eq
print("RESULT", "OK" if ok else "FAIL")
