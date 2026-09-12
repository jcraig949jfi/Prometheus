import numpy as np
from py_vollib.black_scholes import black_scholes as bs
from py_vollib.black_scholes.implied_volatility import implied_volatility as iv
S, r = 100.0, 0.01
worst = 0.0; worst_p = 0.0; n = 0; ill = 0
for K in (40, 70, 90, 100, 110, 130, 200, 300):
    for t in (0.02, 0.25, 1.0, 3.0):
        for sigma in (0.05, 0.2, 0.6, 1.5):
            for flag in ("c", "p"):
                p = bs(flag, S, K, t, r, sigma)
                try:
                    s2 = iv(p, S, K, t, r, flag)
                except Exception as e:
                    print("K=%s t=%s sigma=%s %s -> %s (price %.3e)" % (K, t, sigma, flag, type(e).__name__, p)); continue
                p2 = bs(flag, S, K, t, r, s2)
                perr = abs(p2 - p) / S; worst_p = max(worst_p, perr)
                # sigma is identifiable only where the price moves with it: vega ~ S*sqrt(t)*phi(d1)
                d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
                vega = S * np.sqrt(t) * np.exp(-0.5 * d1 ** 2) / np.sqrt(2 * np.pi)
                if vega > 1e-6:
                    err = abs(s2 - sigma); worst = max(worst, err); n += 1
                else:
                    ill += 1
print("well-conditioned points (vega > 1e-6): %d  worst |sigma_iv - sigma| = %.3e" % (n, worst))
print("ill-conditioned points (vega <= 1e-6, sigma not identifiable): %d" % ill)
print("all points: worst price round-trip error / S = %.3e" % worst_p)
print("RESULT", "OK" if (worst < 1e-9 and worst_p < 1e-12 and n >= 150) else "FAIL")
