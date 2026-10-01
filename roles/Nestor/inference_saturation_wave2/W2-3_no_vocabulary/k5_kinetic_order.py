"""K5 (frame D, chemistry / mass action): kinetic order of the causal-set growth in X-TICKET.

Existing data only: c9x x_ticket/results/*.json (128 single-implant 7ae3 runs, BASE, splice off),
traj[t] = (live members of the implant's causal set [by site label], anc0 sites, cumulative causal
births) for epochs 1..300.
Three readings of the per-epoch birth count B(t+1):
  first order (constant kernel, the GW/IPS reading):   E[B] = b * n
  second order (cooperative autocatalysis, Allee):      E[B] = b * n + c * n^2   (c > 0)
  age-structured (site/content frame: a site's content is eroded after it is written, so only
  recently written sites still act):                    E[B] = a * young + b_old * old,
  young = causal births in the previous K epochs (capped at n), old = n - young.
Poisson MLE; compare log-likelihoods. Epochs t < TMAX, n >= 1, n/N small (n <= 40).
"""
import json
import math

import common as C

K = 5
TMAX = 300


def load():
    rows = []
    for f in (C.CAMP / "c9x-explore-2026-09-24" / "x_ticket" / "results").glob("*.json"):
        tr = json.loads(f.read_text())["traj"]
        prev = [(1, 1, 0)] + tr
        for t in range(1, min(len(tr), TMAX)):
            n, _a, cb = prev[t]
            if n < 1 or n > 40:
                continue
            nb = tr[t][2] - cb
            young = min(n, cb - prev[max(0, t - K)][2])
            rows.append((n, young, n - young, nb))
    return rows


def poisson_fit(X, y, iters=200):
    """Poisson MLE with identity link, nonneg coefficients, by multiplicative EM-style updates."""
    p = len(X[0])
    beta = [0.05] * p
    for _ in range(iters):
        mu = [max(1e-12, sum(b * x for b, x in zip(beta, row))) for row in X]
        num = [sum(row[j] * yi / m for row, yi, m in zip(X, y, mu)) for j in range(p)]
        den = [sum(row[j] for row in X) for j in range(p)]
        beta = [b * nu / d if d > 0 else 0.0 for b, nu, d in zip(beta, num, den)]
    mu = [max(1e-12, sum(b * x for b, x in zip(beta, row))) for row in X]
    ll = sum(yi * math.log(m) - m - math.lgamma(yi + 1) for yi, m in zip(y, mu))
    return beta, ll


def main():
    rows = load()
    y = [r[3] for r in rows]
    out = {"n_obs": len(rows), "K": K}
    b1, l1 = poisson_fit([[r[0]] for r in rows], y)
    b2, l2 = poisson_fit([[r[0], r[0] ** 2] for r in rows], y)
    b3, l3 = poisson_fit([[r[1], r[2]] for r in rows], y)
    b4, l4 = poisson_fit([[r[1], r[2], r[0] ** 2] for r in rows], y)
    out["first_order"] = {"b": b1, "ll": round(l1, 1), "aic": round(2 - 2 * l1, 1)}
    out["second_order"] = {"b,c": b2, "ll": round(l2, 1), "aic": round(4 - 2 * l2, 1)}
    out["age_structured"] = {"a_young,b_old": b3, "ll": round(l3, 1), "aic": round(4 - 2 * l3, 1)}
    out["age_plus_n2"] = {"a,b,c": b4, "ll": round(l4, 1), "aic": round(6 - 2 * l4, 1)}
    # per-capita birth rate by n bin (descriptive)
    bins = [(1, 1), (2, 2), (3, 4), (5, 8), (9, 16), (17, 40)]
    out["per_capita_by_n"] = {}
    for lo, hi in bins:
        rs = [r for r in rows if lo <= r[0] <= hi]
        if rs:
            out["per_capita_by_n"]["%d-%d" % (lo, hi)] = {"member_epochs": sum(r[0] for r in rs),
                                                         "births_per_member_epoch": round(sum(r[3] for r in rs) / sum(r[0] for r in rs), 4),
                                                         "young_share": round(sum(r[1] for r in rs) / sum(r[0] for r in rs), 3)}
    (C.HERE / "k5_kinetic_order.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
