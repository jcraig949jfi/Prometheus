"""K5b: robustness of K5. (i) age profile of per-site writing: births per member by age class, where
age classes are counted from cumulative causal births in windows (1, 2-3, 4-7, 8-15, 16-31, >=32 epochs);
(ii) the same first-order vs age-structured comparison INSIDE the 10 winning runs only (depth >= 5),
so run-level heterogeneity cannot produce the age effect; (iii) K sensitivity."""
import json
import math

import common as C
from k5_kinetic_order import poisson_fit

EDGES = [1, 3, 7, 15, 31]


def load(winners_only=False, K=5):
    rows, prof = [], []
    for f in (C.CAMP / "c9x-explore-2026-09-24" / "x_ticket" / "results").glob("*.json"):
        d = json.loads(f.read_text())
        if winners_only and d["depth"] < 5:
            continue
        tr = d["traj"]
        prev = [(1, 1, 0)] + tr
        for t in range(1, min(len(tr), 300)):
            n, _a, cb = prev[t]
            if n < 1 or n > 40:
                continue
            nb = tr[t][2] - cb
            young = min(n, cb - prev[max(0, t - K)][2])
            rows.append((n, young, n - young, nb))
            # age classes: births within (t-e_hi, t-e_lo]
            cls, lo_cb, rem = [], cb, n
            for e in EDGES:
                c_e = cb - prev[max(0, t - e)][2]
                k = min(rem, c_e - (cb - lo_cb))
                cls.append(max(0, k))
                rem -= max(0, k)
                lo_cb = prev[max(0, t - e)][2]
            cls.append(max(0, rem))
            prof.append((cls, nb))
    return rows, prof


def main():
    out = {}
    rows, prof = load()
    X = [c for c, _ in prof]
    y = [b for _, b in prof]
    beta, ll = poisson_fit(X, y, 400)
    out["age_profile_per_member_epoch"] = dict(zip(["age<=1", "2-3", "4-7", "8-15", "16-31", ">=32"], [round(b, 5) for b in beta]))
    out["age_profile_member_epochs"] = dict(zip(["age<=1", "2-3", "4-7", "8-15", "16-31", ">=32"], [sum(c[j] for c in X) for j in range(6)]))
    for K in (2, 3, 5, 10):
        r, _ = load(False, K)
        y = [q[3] for q in r]
        _, l1 = poisson_fit([[q[0]] for q in r], y)
        b3, l3 = poisson_fit([[q[1], q[2]] for q in r], y)
        out["K=%d_all" % K] = {"dAIC_first_minus_age": round((2 - 2 * l1) - (4 - 2 * l3), 1), "young,old": [round(v, 5) for v in b3]}
    r, _ = load(True, 5)
    y = [q[3] for q in r]
    _, l1 = poisson_fit([[q[0]] for q in r], y)
    _, l2 = poisson_fit([[q[0], q[0] ** 2] for q in r], y)
    b3, l3 = poisson_fit([[q[1], q[2]] for q in r], y)
    out["winners_only_K5"] = {"n_obs": len(r), "aic_first": round(2 - 2 * l1, 1), "aic_second": round(4 - 2 * l2, 1),
                              "aic_age": round(4 - 2 * l3, 1), "young,old": [round(v, 5) for v in b3]}
    (C.HERE / "k5b_age_profile.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
