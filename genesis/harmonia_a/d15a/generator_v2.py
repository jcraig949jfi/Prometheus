#!/usr/bin/env python
"""D15-A Track B — constructive generator v2 + exhaustive census.
Finite worlds over Z_6xZ_6 (36 states). Every relation (E1/E2, version
space, probe factorial) is computed exactly. Repairs are CONSTRUCTED to
instantiate each rung, then the census VERIFIES. No oracle info reaches
any discovery path (this module is evaluation-side only)."""

import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).parent
M = 6
DIM = 2
NST = M ** DIM            # 36


def enc(a, b):
    return a * M + b


def dec(s):
    return s // M, s % M


def perm_from(fn):
    return tuple(fn(*dec(s)) for s in range(NST))


def reach(op_perms, x0set):
    seen = set(x0set)
    fr = set(x0set)
    while fr:
        nx = set()
        for s in fr:
            for p in op_perms:
                t = p[s]
                if t not in seen:
                    seen.add(t); nx.add(t)
        fr = nx
    return seen


# ---- base operator library (permutations of the 36-grid) -------------
def base_ops():
    ops = {}
    for k in (1, 2, 3):
        ops[f"ra{k}"] = perm_from(lambda a, b, k=k: enc((a + k) % M, b))
        ops[f"rb{k}"] = perm_from(lambda a, b, k=k: enc(a, (b + k) % M))
    ops["swap"] = perm_from(lambda a, b: enc(b, a))
    ops["refa"] = perm_from(lambda a, b: enc((-a) % M, b))
    ops["refb"] = perm_from(lambda a, b: enc(a, (-b) % M))
    ops["diag"] = perm_from(lambda a, b: enc((a + b) % M, b))
    ops["diag2"] = perm_from(lambda a, b: enc(a, (a + b) % M))
    # compositions broaden the hidden-op family (fixes master-key)
    keys0 = list(ops)
    for i in range(len(keys0)):
        for j in range(i + 1, len(keys0)):
            k1, k2 = keys0[i], keys0[j]
            p = tuple(ops[k2][ops[k1][s]] for s in range(NST))
            nm = f"{k1}+{k2}"
            if p not in set(ops.values()) and len(ops) < 26:
                ops[nm] = p
    return ops


BASE = base_ops()


def e2_class(q, T, x0, G, Tb):
    rc = reach(list(T) + [q], {x0})
    return (frozenset(rc & G), bool(rc & Tb) is False)


def useful(R, T, x0, G, Tb):
    return [q for q in R if G <= reach(list(T) + [q], {x0})]


def version_space(U, T, x0, G, Tb, h, probes):
    """E2 classes still consistent with observed h(s) for s in probes."""
    classes = set()
    for q in U:
        if all(q[s] == h[s] for s in probes):
            classes.add(e2_class(q, T, x0, G, Tb))
    return classes


def make_variant(base, agree_states, rng, differ_k=3):
    """A permutation equal to `base` on agree_states, a small transposition
    elsewhere (keeps it a permutation)."""
    q = list(base)
    movable = [s for s in range(NST) if s not in agree_states]
    rng.shuffle(movable)
    for i in range(0, min(differ_k * 2, len(movable) - 1), 2):
        a, b = movable[i], movable[i + 1]
        q[a], q[b] = q[b], q[a]
    return tuple(q)


def construct_world(seed, rung):
    rng = np.random.default_rng(np.random.SeedSequence([7, seed,
                                                        hash(rung) & 0xffff]))
    keys = list(BASE)
    rng.shuffle(keys)
    T = [BASE[k] for k in keys[:3]]
    x0 = int(rng.integers(NST))
    N = reach(T, {x0})
    # target OUTSIDE navigation reach (dynamics failure), reachable via h
    hk = keys[3]
    h = BASE[hk]
    reach_h = reach(T + [h], {x0})
    outside = list(reach_h - N)
    if len(outside) < 1:
        return None
    G = frozenset({int(rng.choice(outside))})
    # taboo chosen from OUTSIDE reach_h so h is sound BY CONSTRUCTION
    tb_pool = [s for s in range(NST) if s not in reach_h and s not in G]
    if len(tb_pool) < 3:
        return None
    Tb = frozenset(rng.choice(tb_pool, size=3, replace=False).tolist())
    O = set(range(NST))                      # observable universe
    R = [h]                                  # true repair always in pool
    # EQUIV members: agree with h on reach_h (E2-equal to h by construction)
    for _ in range(4):
        R.append(make_variant(h, reach_h, rng, differ_k=3))
    # distractor E2 classes: repairs that ALSO solve G but via a different
    # target-relevant structure, agreeing with h only on a controlled set.
    n_distract = {"I0": 2, "I1": 2, "I2": 3, "I3": 2, "I4": 1,
                  "I5": 0}[rung]
    distinguishers = []                      # states that split classes
    for di in range(n_distract):
        # pick an alternate op that also reaches G
        alt = None
        for cand_k in keys[4:]:
            cand = BASE[cand_k]
            if G <= reach(T + [cand], {x0}):
                alt = cand; break
        if alt is None:
            # synthesize: h composed with a base op, retried for solving
            for cand_k in keys:
                comp = tuple(BASE[cand_k][h[s]] for s in range(NST))
                if G <= reach(T + [comp], {x0}) and reach(T + [comp],
                                                          {x0}) & Tb == set():
                    alt = comp; break
        if alt is None:
            continue
        # where does alt disagree with h? that's the distinguishing set
        dset = [s for s in range(NST) if alt[s] != h[s]]
        if not dset:
            continue
        if rung == "I0":
            O -= set(dset)
        elif rung == "I1":
            altl = list(alt)
            for s in list(dset):
                if s in N:
                    altl[s] = h[s]
            alt = tuple(altl)
            if not (G <= reach(T + [alt], {x0})):
                continue
            dset = [s for s in range(NST) if alt[s] != h[s]]
        distinguishers.extend(dset)
        R.append(alt)
    U = useful(R, T, x0, G, Tb)
    V0 = version_space(U, T, x0, G, Tb, h, frozenset())
    VO = version_space(U, T, x0, G, Tb, h,
                       frozenset(s for s in O))
    # informative probes at V0
    info_states = []
    for s in O:
        vp = version_space(U, T, x0, G, Tb, h, frozenset({s}))
        if len(vp) < len(V0):
            info_states.append(s)

    def greedy_cost(probe_pool):
        """min probes to drive |V| to 1 by greedy max-split; cap 8."""
        P = set()
        V = version_space(U, T, x0, G, Tb, h, frozenset(P))
        if len(V) <= 1:
            return 0
        for _ in range(8):
            best_s, best_v = None, len(V)
            for s in probe_pool:
                if s in P:
                    continue
                nv = len(version_space(U, T, x0, G, Tb, h,
                                       frozenset(P | {s})))
                if nv < best_v:
                    best_v, best_s = nv, s
            if best_s is None:
                return 99          # cannot identify from this pool
            P.add(best_s)
            V = version_space(U, T, x0, G, Tb, h, frozenset(P))
            if len(V) <= 1:
                return len(P)
        return 99
    passive_cost = greedy_cost(N)          # navigation-reachable only
    active_cost = greedy_cost(O)           # any observable (teleport)
    # goal states: on a T-step toward G frontier
    goal_states = [s for s in N if any(p[s] in
                   reach(T, {x0}) and p[s] in _one_step_to_G(T, G, N)
                   for p in T)]
    return dict(
        seed=seed, rung=rung, x0=x0, G=sorted(G), Tb=sorted(Tb),
        n_T=len(T), nav_reach=len(N), obs_universe=len(O),
        R_size=len(R), U_size=len(U),
        E1_useful=len({tuple(q) for q in U}),
        E2_classes_V0=len(V0),
        E2_classes_after_full_probe=len(VO),
        n_informative_probes=len(info_states),
        info_only=len([s for s in info_states if s not in N]),
        passive_cost=passive_cost, active_cost=active_cost,
        active_advantage=int(passive_cost - active_cost),
        goal_states=len(goal_states),
        h=h, T=T, x0_=x0, G_=G, Tb_=Tb, O_=sorted(O), U_=U,
        distinguishers=sorted(set(distinguishers)))


def _one_step_to_G(T, G, N):
    pre = set()
    for s in N:
        for p in T:
            if p[s] in G:
                pre.add(s)
    return pre | set(G)


def census(worlds):
    from collections import Counter
    by_rung = {}
    for w in worlds:
        by_rung.setdefault(w["rung"], []).append(w)
    rep = {}
    for rung, ws in sorted(by_rung.items()):
        v0 = [w["E2_classes_V0"] for w in ws]
        vfull = [w["E2_classes_after_full_probe"] for w in ws]
        e1 = [w["E1_useful"] for w in ws]
        e2 = [w["E2_classes_V0"] for w in ws]
        rep[rung] = dict(
            n=len(ws),
            E2_V0_min=int(min(v0)), E2_V0_max=int(max(v0)),
            E2_V0_median=float(np.median(v0)),
            E2_after_full_probe_median=float(np.median(vfull)),
            E1_vs_E2_ratio_median=float(np.median(
                [a / max(b, 1) for a, b in zip(e1, e2)])),
            zero_info_frac=float(np.mean(
                [w["E2_classes_after_full_probe"] == w["E2_classes_V0"]
                 and w["E2_classes_V0"] > 1 for w in ws])),
            identified_frac=float(np.mean(
                [w["E2_classes_V0"] == 1 for w in ws])),
            has_info_only_probe_frac=float(np.mean(
                [w["info_only"] > 0 for w in ws])),
            passive_cost_median=float(np.median(
                [min(w["passive_cost"], 9) for w in ws])),
            active_cost_median=float(np.median(
                [min(w["active_cost"], 9) for w in ws])),
            active_advantage_frac=float(np.mean(
                [w["passive_cost"] > w["active_cost"] for w in ws])))
    return rep


def main():
    RUNGS = ("I0", "I1", "I2", "I3", "I4", "I5")
    worlds = []
    per_target = 80
    SEED_CAP = 12000
    def accepts(w):
        r = w["rung"]
        pc, ac, v0 = w["passive_cost"], w["active_cost"], w["E2_classes_V0"]
        if r == "I0":
            return w["E2_classes_after_full_probe"] > 1
        if r == "I1":
            return pc >= 99 and ac < 99
        if r == "I2":
            return ac < 99 and pc < 99 and ac < pc
        if r == "I3":
            return ac < 99 and ac == pc and v0 > 1
        if r == "I4":
            return ac == 1 and v0 == 2
        if r == "I5":
            return v0 == 1
        return True
    for rung in RUNGS:
        got = 0
        seed = 0
        while got < per_target and seed < SEED_CAP:
            w = construct_world(seed, rung)
            seed += 1
            if w is None or not accepts(w):
                continue
            worlds.append(w)
            got += 1
    rep = census(worlds)

    # ---- census acceptance criteria (frozen) ----
    checks = {}
    checks["all_rungs_populated"] = all(rep.get(r, {}).get("n", 0) >= 40
                                        for r in RUNGS)
    # E2 ladder monotone-ish in V0 median
    med = {r: rep[r]["E2_V0_median"] for r in RUNGS if r in rep}
    checks["ladder_ordering"] = (med.get("I0", 0) >= med.get("I3", 99)
                                 and med.get("I5", 99) <= 1.0
                                 and med.get("I0", 0) > med.get("I5", 99))
    checks["equiv_rung_collapses"] = (
        rep.get("I5", {}).get("E1_vs_E2_ratio_median", 0) >= 3.0)
    checks["I0_zero_info"] = rep.get("I0", {}).get("zero_info_frac", 0) >= 0.5
    checks["I5_identified"] = rep.get("I5", {}).get("identified_frac", 0) >= 0.8
    # master-key: no single hidden op dominant
    from collections import Counter
    hk = Counter(tuple(w["h"]) for w in worlds)
    checks["no_master_key"] = (max(hk.values()) / len(worlds)) <= 0.15
    # probe factorial: info-only probes exist in ACTIVE rungs
    checks["info_only_exists"] = (
        rep.get("I2", {}).get("has_info_only_probe_frac", 0) >= 0.3)

    verdict_gen = ("GENERATOR_READY" if
                   (checks["all_rungs_populated"]
                    and checks["ladder_ordering"]
                    and checks["equiv_rung_collapses"]
                    and checks["no_master_key"])
                   else "GENERATOR_NOT_READY")
    checks["I1_active_advantage"] = (
        rep.get("I1", {}).get("active_advantage_frac", 0) >= 0.4)
    checks["I2_active_fast"] = (
        rep.get("I2", {}).get("active_cost_median", 9) <= 3.0)
    checks["poles_vs_middle"] = (
        rep.get("I0", {}).get("active_cost_median", 0) >
        rep.get("I5", {}).get("active_cost_median", 9))
    verdict_inst = ("INSTRUMENT_READY" if
                    (verdict_gen == "GENERATOR_READY"
                     and checks["I0_zero_info"]
                     and checks["I5_identified"]
                     and checks["info_only_exists"]
                     and checks["I1_active_advantage"]
                     and checks["poles_vs_middle"])
                    else "INSTRUMENT_NOT_READY")

    json.dump(dict(census=rep, checks=checks,
                   verdict_generator=verdict_gen,
                   verdict_instrument=verdict_inst,
                   n_worlds=len(worlds)),
              open(OUT / "D15A_GENERATOR_CENSUS_V2.json", "w"), indent=1,
              default=str)
    ladder = {r: dict(n=rep[r]["n"], E2_V0_median=rep[r]["E2_V0_median"],
                      E2_V0_range=[rep[r]["E2_V0_min"],
                                   rep[r]["E2_V0_max"]],
                      E1_E2_ratio=rep[r]["E1_vs_E2_ratio_median"])
              for r in RUNGS if r in rep}
    json.dump(ladder, open(OUT / "D15A_IDENTIFIABILITY_LADDER_V2.json",
                           "w"), indent=1)
    # probe orthogonality summary
    ortho = {}
    for r in RUNGS:
        ws = [w for w in worlds if w["rung"] == r]
        if not ws:
            continue
        ortho[r] = dict(
            median_informative=float(np.median(
                [w["n_informative_probes"] for w in ws])),
            frac_with_info_only=float(np.mean(
                [w["info_only"] > 0 for w in ws])),
            median_goal_states=float(np.median(
                [w["goal_states"] for w in ws])))
    json.dump(ortho, open(OUT / "D15A_PROBE_ORTHOGONALITY.json", "w"),
              indent=1)

    print(json.dumps(checks, indent=1, default=str))
    print("GENERATOR:", verdict_gen, "| INSTRUMENT:", verdict_inst)
    for r in RUNGS:
        if r in rep:
            print(f"  {r}: n={rep[r]['n']} E2_V0_med={rep[r]['E2_V0_median']}"
                  f" E1/E2={rep[r]['E1_vs_E2_ratio_median']:.1f}"
                  f" zeroinfo={rep[r]['zero_info_frac']:.2f}"
                  f" ident={rep[r]['identified_frac']:.2f}")


if __name__ == "__main__":
    main()
