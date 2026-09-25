"""WTP-03 genome generation: the WTP-02 grammar (candidate/normalize/mutate, unchanged) plus one
declared grammar change (PREREG_WTP03 s5): every world has an INFORMATION MARKET. A genome drawn
with query_every = 0 gets query_every redrawn from 3-40 (query_reward and tol keep their draws),
because a query market is the one causally meaningful payoff for predicting unseen cells."""
import numpy as np

from ensorain.wtp2.genome2 import candidate as candidate2, normalize, mutate  # noqa: F401


def market(g, rng):
    if not g["resource"].get("query_every"):
        g["resource"]["query_every"] = int(rng.integers(3, 41))
        g["resource"]["market_redrawn"] = True
    for k in ("calibrated", "calibrated3", "kappa"):
        g["resource"].pop(k, None)
    g["memory"].pop("carrier", None)
    return g


def candidate(rng, archive, admitted):
    return market(candidate2(rng, archive, admitted), rng)
