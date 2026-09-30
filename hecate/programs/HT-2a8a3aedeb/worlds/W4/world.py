"""HT-2a8a3aedeb / W4 world. See IMPLEMENTATION_NOTES.md (written first)."""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")

PARAMS = dict(
    n_modes=3, levels=5, K=2, n_train=10, n_in=5, n_orth=5, n_pc=5,
    seeds=list(range(10)), pe=0.1, stay=0.5, bias_lo=0.2, bias_hi=0.8,
    q_offset=1.0, q_amp=0.9, z_floor_rel=1e-12,
)
ATTEMPT = int(sys.argv[1]) if len(sys.argv) > 1 else 2
L, K, PE = PARAMS["levels"], PARAMS["K"], PARAMS["pe"]


def walk(r):
    P = np.zeros((L, L))
    for i in range(L):
        P[i, i] += PARAMS["stay"]
        if i + 1 < L:
            P[i, i + 1] += 0.5 * r
        else:
            P[i, i] += 0.5 * r
        if i - 1 >= 0:
            P[i, i - 1] += 0.5 * (1 - r)
        else:
            P[i, i] += 0.5 * (1 - r)
    return P


def orth_factors(rng):
    one = np.ones((L, 1)) / np.sqrt(L)
    M = np.hstack([one, rng.standard_normal((L, L - 1))])
    Q, _ = np.linalg.qr(M)
    Q = Q * np.sign(Q[0, 0] * one[0, 0])  # keep first column = +const
    # attempt 2 repair: shared span = {constant, one direction} (K dims); O = 2 dims of complement
    return Q[:, 0:K], Q[:, K:2 * K]  # F (shared), O (orthogonal)


def goal_cost(rng, V):
    core = rng.standard_normal((K, K, K))
    g = np.einsum("abc,ia,jb,kc->ijk", core, V[0], V[1], V[2]).ravel()
    g = g / np.max(np.abs(g))
    return PARAMS["q_offset"] + PARAMS["q_amp"] * g


def lin_system(P, q):
    e = np.exp(-q)
    A = np.eye(len(q)) - (e[:, None] * (1 - PE)) * P
    b = PE * e
    return A, b


def solve_z(P, q):
    A, b = lin_system(P, q)
    return np.linalg.solve(A, b)


def policy_cost(P, q, z):
    """Exact J for policy u(s'|s) ~ (1-pe)P(s'|s) z(s'), u(exit) ~ pe."""
    w_int = (1 - PE) * P * z[None, :]
    w_exit = PE * np.ones(len(q))
    tot = w_int.sum(1) + w_exit
    u_int = w_int / tot[:, None]
    u_exit = w_exit / tot
    p_int = (1 - PE) * P
    with np.errstate(divide="ignore", invalid="ignore"):
        kl_int = np.where(u_int > 0, u_int * np.log(u_int / p_int), 0.0)
    kl = kl_int.sum(1) + u_exit * np.log(u_exit / PE)
    v = np.linalg.solve(np.eye(len(q)) - u_int, q + kl)
    return float(v.mean())


def galerkin_regret(P, q, B, Jstar):
    A, b = lin_system(P, q)
    c = np.linalg.solve(B.T @ A @ B, B.T @ b)
    zh = B @ c
    mx = zh.max()
    if mx <= 0:
        zh = np.ones_like(zh)
        nfloor = len(zh)
    else:
        fl = PARAMS["z_floor_rel"] * mx
        nfloor = int((zh < fl).sum())
        zh = np.maximum(zh, fl)
    J = policy_cost(P, q, zh)
    return (J - Jstar) / Jstar, nfloor


def hosvd_factors(T):
    Us = []
    for m in range(3):
        X = np.moveaxis(T, m + 1, 0).reshape(L, -1)
        U, _, _ = np.linalg.svd(X, full_matrices=False)
        Us.append(U[:, :K])
    return Us


def eig_factors(Pm):
    w, V = np.linalg.eig(Pm)
    idx = np.argsort(-w.real)[:K]
    Q, _ = np.linalg.qr(V[:, idx].real)
    return Q, np.sort(w.real)[::-1]


def kron3(Us):
    return np.kron(np.kron(Us[0], Us[1]), Us[2])


def evaluate_goals(P, goals, Bs):
    out = {k: [] for k in Bs}
    floors = {k: 0 for k in Bs}
    Jstars = []
    opt_check = []
    for q in goals:
        z = solve_z(P, q)
        Jstar = float((-np.log(z)).mean())
        opt_check.append(abs(policy_cost(P, q, z) - Jstar) / Jstar)
        Jstars.append(Jstar)
        for k, B in Bs.items():
            r, nf = galerkin_regret(P, q, B, Jstar)
            out[k].append(float(r))
            floors[k] += nf
    return out, floors, Jstars, max(opt_check)


def main():
    t0 = time.process_time()
    fh = open(ROWS, "a", encoding="utf-8")
    for seed in PARAMS["seeds"]:
        ss = np.random.SeedSequence(seed)
        r_dyn, r_fac, r_goal, r_rand, r_perm = [np.random.default_rng(s) for s in ss.spawn(5)]
        biases = r_dyn.uniform(PARAMS["bias_lo"], PARAMS["bias_hi"], 3)
        Pms = [walk(r) for r in biases]
        P = np.kron(np.kron(Pms[0], Pms[1]), Pms[2])
        FO = [orth_factors(r_fac) for _ in range(3)]
        F = [f for f, _ in FO]
        O = [o for _, o in FO]
        train = [goal_cost(r_goal, F) for _ in range(PARAMS["n_train"])]
        test_in = [goal_cost(r_goal, F) for _ in range(PARAMS["n_in"])]
        test_orth = [goal_cost(r_goal, O) for _ in range(PARAMS["n_orth"])]
        test_pc = train[:PARAMS["n_pc"]]

        Z = np.stack([solve_z(P, q).reshape(L, L, L) for q in train])
        Ua = hosvd_factors(Z)
        eigs = [eig_factors(Pm) for Pm in Pms]
        Ub = [e[0] for e in eigs]
        second_eig = [float(e[1][1]) for e in eigs]
        Uc = [np.linalg.qr(r_rand.standard_normal((L, K)))[0] for _ in range(3)]
        Zp = Z.copy()
        for g in range(Z.shape[0]):
            for m in range(3):
                Zp[g] = np.take(Zp[g], r_perm.permutation(L), axis=m)
        Un = hosvd_factors(Zp)
        Bs = {"a": kron3(Ua), "b": kron3(Ub), "c": kron3(Uc), "null": kron3(Un)}

        reg_in, fl_in, J_in, oc1 = evaluate_goals(P, test_in, Bs)
        reg_orth, fl_orth, J_orth, oc2 = evaluate_goals(P, test_orth, Bs)
        reg_pc, fl_pc, J_pc, oc3 = evaluate_goals(P, test_pc, {"a": Bs["a"], "b": Bs["b"]})

        # diagnostics: alignment of (b) and (a) with shared/orthogonal factors
        def overlap(U, V):
            return [float(np.linalg.norm(U[m].T @ V[m]) ** 2 / K) for m in range(3)]

        common = dict(
            triplicateId="HT-2a8a3aedeb", world="W4", attempt=ATTEMPT, seed=seed,
            params=PARAMS, biases=biases.tolist(), second_eig_per_mode=second_eig,
            regret_in={k: reg_in[k] for k in ("a", "b", "c")},
            regret_orth={k: reg_orth[k] for k in ("a", "b", "c")},
            Jstar_in=J_in, Jstar_orth=J_orth,
            floored_entries={"in": fl_in, "orth": fl_orth},
            optimal_policy_check_max_relerr=max(oc1, oc2, oc3),
            overlap_b_with_F=overlap(Ub, F), overlap_b_with_O=overlap(Ub, O),
            overlap_a_with_F=overlap(Ua, F), overlap_a_with_O=overlap(Ua, O),
        )
        arms = {
            "TREATMENT": dict(candidate="a", cand_in=reg_in["a"], cand_orth=reg_orth["a"]),
            "CONTROL": dict(candidate="c", cand_in=reg_in["c"], cand_orth=reg_orth["c"]),
            "NULL_TWIN": dict(candidate="null", cand_in=reg_in["null"], cand_orth=reg_orth["null"]),
            "POSITIVE_CONTROL": dict(candidate="a", pc_goal_indices=list(range(PARAMS["n_pc"])),
                                     regret_pc_a=reg_pc["a"], regret_pc_b=reg_pc["b"]),
            "CHEAT": dict(candidate="cheat",
                          cand_in=[rb / 10 for rb in reg_in["b"]],
                          cand_orth=[rb * 10 for rb in reg_orth["b"]]),
        }
        for arm, extra in arms.items():
            row = dict(arm=arm, **common, **extra)
            row["cpu_seconds_cumulative"] = time.process_time() - t0
            fh.write(json.dumps(row) + "\n")
            fh.flush()
    fh.close()


if __name__ == "__main__":
    main()
