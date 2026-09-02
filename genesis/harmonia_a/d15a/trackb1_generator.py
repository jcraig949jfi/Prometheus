#!/usr/bin/env python
"""D15-A Track B.1 -- construct the missing middle (R-A: Z_8 x Z_8).
E1/E2/E3, probe semantics, construction, acceptance filters: copied
VERBATIM from generator_v2.py (frozen); the ONLY substrate change is
M=8. Additions are MEASUREMENTS required by D15A_TRACKB1_FREEZE.md:
paired cost distribution, gradient/magic-probe metrics, 4-cell probe
factorial with per-probe dH/goal bits, difficulty features + matched
cross-rung support, substrate-confound provenance of the active
advantage. Oracle-side only; nothing here reaches a discovery path."""

import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).parent
M = 8                     # <-- THE one change (was 6)
DIM = 2
NST = M ** DIM            # 64


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


def bfs_dist(op_perms, x0, targets):
    """shortest #ops from x0 to any state in targets; 99 if unreachable."""
    if x0 in targets:
        return 0
    seen = {x0}
    fr = {x0}
    d = 0
    while fr:
        d += 1
        nx = set()
        for s in fr:
            for p in op_perms:
                t = p[s]
                if t in targets:
                    return d
                if t not in seen:
                    seen.add(t); nx.add(t)
        fr = nx
    return 99


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


def make_variant(base, agree_states, rng, differ_k=3):
    q = list(base)
    movable = [s for s in range(NST) if s not in agree_states]
    rng.shuffle(movable)
    for i in range(0, min(differ_k * 2, len(movable) - 1), 2):
        a, b = movable[i], movable[i + 1]
        q[a], q[b] = q[b], q[a]
    return tuple(q)


def _one_step_to_G(T, G, N):
    pre = set()
    for s in N:
        for p in T:
            if p[s] in G:
                pre.add(s)
    return pre | set(G)


def construct_world(seed, rung):
    rng = np.random.default_rng(np.random.SeedSequence([7, seed,
                                                        hash(rung) & 0xffff]))
    keys = list(BASE)
    rng.shuffle(keys)
    T = [BASE[k] for k in keys[:3]]
    x0 = int(rng.integers(NST))
    N = reach(T, {x0})
    hk = keys[3]
    h = BASE[hk]
    reach_h = reach(T + [h], {x0})
    outside = list(reach_h - N)
    if len(outside) < 1:
        return None
    G = frozenset({int(rng.choice(outside))})
    tb_pool = [s for s in range(NST) if s not in reach_h and s not in G]
    if len(tb_pool) < 3:
        return None
    Tb = frozenset(rng.choice(tb_pool, size=3, replace=False).tolist())
    O = set(range(NST))
    R = [h]
    for _ in range(4):
        R.append(make_variant(h, reach_h, rng, differ_k=3))
    n_distract = {"I0": 2, "I1": 2, "I2": 3, "I3": 2, "I4": 1,
                  "I5": 0}[rung]
    distinguishers = []
    for di in range(n_distract):
        alt = None
        for cand_k in keys[4:]:
            cand = BASE[cand_k]
            if G <= reach(T + [cand], {x0}):
                alt = cand; break
        if alt is None:
            for cand_k in keys:
                comp = tuple(BASE[cand_k][h[s]] for s in range(NST))
                if G <= reach(T + [comp], {x0}) and reach(T + [comp],
                                                          {x0}) & Tb == set():
                    alt = comp; break
        if alt is None:
            continue
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
    # cache E2 class per useful repair (pure speed; identical semantics)
    cls = {i: e2_class(q, T, x0, G, Tb) for i, q in enumerate(U)}

    def vsize(probes):
        return len({cls[i] for i, q in enumerate(U)
                    if all(q[s] == h[s] for s in probes)})

    V0n = vsize(frozenset())
    VOn = vsize(frozenset(O))
    # per-probe dH + goal bit (frozen factorial)
    goalset = set()
    one_step = _one_step_to_G(T, G, N)
    for s in N:
        if any(p[s] in one_step for p in T):
            goalset.add(s)
    probe_rows = []
    for s in O:
        v1 = vsize(frozenset({s}))
        dH = (np.log2(V0n) - np.log2(v1)) if V0n > 0 and v1 > 0 else 0.0
        probe_rows.append((s, float(dH), 1 if s in goalset else 0))
    gains = [r[1] for r in probe_rows]
    disc = [r for r in probe_rows if r[1] > 0]
    cells = dict(
        INFORMATION_ONLY=sum(1 for _, d, g in probe_rows
                             if d > 0 and g == 0),
        GOAL_ONLY=sum(1 for _, d, g in probe_rows if d == 0 and g == 1),
        MIXED=sum(1 for _, d, g in probe_rows if d > 0 and g == 1),
        NULL=sum(1 for _, d, g in probe_rows if d == 0 and g == 0))

    def greedy_cost(probe_pool):
        P = set()
        first = None
        if vsize(frozenset(P)) <= 1:
            return 0, None
        for _ in range(8):
            best_s, best_v = None, vsize(frozenset(P))
            for s in probe_pool:
                if s in P:
                    continue
                nv = vsize(frozenset(P | {s}))
                if nv < best_v:
                    best_v, best_s = nv, s
            if best_s is None:
                return 99, first
            if first is None:
                first = best_s
            P.add(best_s)
            if vsize(frozenset(P)) <= 1:
                return len(P), first
        return 99, first

    passive_cost, first_p = greedy_cost(N)
    active_cost, first_a = greedy_cost(O)
    base_cost = bfs_dist(T + [h], x0, set(G))
    info_states = [r[0] for r in disc]
    return dict(
        seed=seed, rung=rung, x0=x0,
        nav_reach=len(N), obs_universe=len(O),
        R_size=len(R), U_size=len(U),
        E1_useful=len({tuple(q) for q in U}),
        E2_classes_V0=V0n,
        E2_classes_after_full_probe=VOn,
        H0=float(np.log2(V0n)) if V0n > 0 else 0.0,
        n_informative_probes=len(disc),
        info_only=len([s for s in info_states if s not in N]),
        best_gain=float(max(gains)) if gains else 0.0,
        median_gain=float(np.median(gains)) if gains else 0.0,
        n_distinct_gains=len({round(r[1], 6) for r in disc}),
        magic_probe=bool(any(
            vsize(frozenset({r[0]})) == 1 for r in disc)) if V0n > 1
        else False,
        cells=cells,
        passive_cost=passive_cost, active_cost=active_cost,
        first_active_outside_N=bool(first_a is not None
                                    and first_a not in N),
        disc_in_N=len([s for s in info_states if s in N]),
        disc_out_N=len([s for s in info_states if s not in N]),
        baseline_search_cost=base_cost,
        reach_frac=len(N) / NST,
        solver_density=len(U) / max(len(R), 1),
        target_burden=len(G),
        goal_states=len(goalset),
        h=h)


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


def greedy_match(A, B):
    """1-1 matched pairs under frozen difficulty bands."""
    used = set()
    pairs = 0
    for wa in A:
        for j, wb in enumerate(B):
            if j in used:
                continue
            if (abs(wa["reach_frac"] - wb["reach_frac"]) <= 0.10
                    and abs(wa["baseline_search_cost"]
                            - wb["baseline_search_cost"]) <= 1
                    and abs(wa["solver_density"]
                            - wb["solver_density"]) <= 0.15
                    and wa["target_burden"] == wb["target_burden"]):
                used.add(j)
                pairs += 1
                break
    return pairs


def main():
    RUNGS = ("I0", "I1", "I2", "I3", "I4", "I5")
    worlds = []
    per_target = 80
    SEED_CAP = 12000
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
        print(f"[gen] {rung}: {got} worlds from {seed} seeds", flush=True)

    by = {}
    for w in worlds:
        by.setdefault(w["rung"], []).append(w)

    # ---------- verdict 1: I2 ----------
    i2 = by.get("I2", [])
    paired = [dict(C_passive=w["passive_cost"], C_active=w["active_cost"],
                   dC=w["passive_cost"] - w["active_cost"]) for w in i2]
    dCs = [p["dC"] for p in paired]
    magic_frac = float(np.mean([w["magic_probe"] for w in i2])) if i2 else 1.0
    gradient_frac = float(np.mean(
        [w["n_informative_probes"] >= 3 and w["n_distinct_gains"] >= 2
         for w in i2])) if i2 else 0.0
    i2_checks = dict(
        n=len(i2), n_ok=len(i2) >= 40,
        median_dC=float(np.median(dCs)) if dCs else 0.0,
        median_dC_ok=bool(dCs and np.median(dCs) >= 1),
        magic_probe_frac=magic_frac, magic_ok=magic_frac <= 0.5,
        gradient_frac=gradient_frac, gradient_ok=gradient_frac >= 0.5)
    V_I2 = ("READY" if (i2_checks["n_ok"] and i2_checks["median_dC_ok"]
                        and i2_checks["magic_ok"]
                        and i2_checks["gradient_ok"]) else "NOT_READY")

    # ---------- verdict 2: orthogonality ----------
    mid = [w for r in ("I2", "I3", "I4") for w in by.get(r, [])]
    io_frac = float(np.mean([w["cells"]["INFORMATION_ONLY"] > 0
                             for w in mid])) if mid else 0.0
    go_frac = float(np.mean([w["cells"]["GOAL_ONLY"] > 0
                             for w in mid])) if mid else 0.0
    cell_table = {r: {k: float(np.median([w["cells"][k]
                                          for w in by.get(r, [])]))
                      for k in ("INFORMATION_ONLY", "GOAL_ONLY",
                                "MIXED", "NULL")}
                  for r in RUNGS if r in by}
    orth_checks = dict(info_only_world_frac=io_frac,
                       goal_only_world_frac=go_frac,
                       io_ok=io_frac >= 0.5, go_ok=go_frac >= 0.5,
                       cells_median_by_rung=cell_table)
    V_ORTH = "READY" if (io_frac >= 0.5 and go_frac >= 0.5) else "NOT_READY"

    # ---------- verdict 3: difficulty match ----------
    contrasts = {}
    for a, b in (("I0", "I5"), ("I2", "I3"), ("I1", "I3")):
        contrasts[f"{a}_vs_{b}"] = greedy_match(by.get(a, []),
                                                by.get(b, []))
    V_DIFF = ("READY" if all(v >= 30 for v in contrasts.values())
              else "NOT_READY")

    # ---------- substrate-confound attack ----------
    conf = dict(
        first_active_outside_N_frac=float(np.mean(
            [w["first_active_outside_N"] for w in i2])) if i2 else 0.0,
        disc_out_N_median=float(np.median(
            [w["disc_out_N"] for w in i2])) if i2 else 0.0,
        disc_in_N_median=float(np.median(
            [w["disc_in_N"] for w in i2])) if i2 else 0.0,
        I3_equality_persists=bool(by.get("I3") and all(
            w["passive_cost"] == w["active_cost"] for w in by["I3"])))
    conf["info_advantage_ok"] = conf["first_active_outside_N_frac"] >= 0.8

    # ---------- verdict 4: full generator (anchors) ----------
    from collections import Counter

    def frac(r, fn):
        ws = by.get(r, [])
        return float(np.mean([fn(w) for w in ws])) if ws else 0.0
    anchors = dict(
        all_rungs_40=all(len(by.get(r, [])) >= 40 for r in RUNGS),
        I0_zero_info=frac("I0", lambda w:
                          w["E2_classes_after_full_probe"]
                          == w["E2_classes_V0"]
                          and w["E2_classes_V0"] > 1),
        I1_separation=frac("I1", lambda w: w["passive_cost"] >= 99
                           and w["active_cost"] < 99),
        I5_identified=frac("I5", lambda w: w["E2_classes_V0"] == 1),
        E1_E2_median_all=float(np.median(
            [w["E1_useful"] / max(w["E2_classes_V0"], 1)
             for w in worlds])) if worlds else 0.0,
        master_key_top=(max(Counter(tuple(w["h"]) for w in worlds)
                            .values()) / len(worlds)) if worlds else 1.0)
    anchors_ok = (anchors["all_rungs_40"]
                  and anchors["I0_zero_info"] >= 0.5
                  and anchors["I1_separation"] >= 0.99
                  and anchors["I5_identified"] >= 0.8
                  and anchors["E1_E2_median_all"] >= 3.0
                  and anchors["master_key_top"] <= 0.15)
    V_GEN = ("READY" if (anchors_ok and V_I2 == "READY"
                         and conf["I3_equality_persists"])
             else "NOT_READY")

    # ---------- verdict 5: instrument ----------
    V_INST = ("READY" if (V_GEN == "READY" and V_ORTH == "READY"
                          and V_DIFF == "READY"
                          and conf["info_advantage_ok"])
              else "NOT_READY")

    out = dict(substrate=f"Z_{M}xZ_{M} ({NST} states)",
               verdicts=dict(D15A_TRACKB1_I2=V_I2,
                             D15A_TRACKB1_ORTHOGONALITY=V_ORTH,
                             D15A_TRACKB1_DIFFICULTY_MATCH=V_DIFF,
                             D15A_TRACKB1_FULL_GENERATOR=V_GEN,
                             D15A_TRACKB1_INSTRUMENT=V_INST),
               i2=i2_checks, i2_paired_distribution=paired,
               orthogonality=orth_checks,
               difficulty_match=dict(pairs=contrasts,
                                     band=">=30 per contrast"),
               substrate_confound=conf, anchors=anchors,
               per_rung={r: dict(
                   n=len(by.get(r, [])),
                   E2_V0_median=float(np.median(
                       [w["E2_classes_V0"] for w in by[r]]))
                   if r in by else None,
                   H0_median=float(np.median([w["H0"] for w in by[r]]))
                   if r in by else None,
                   pc_median=float(np.median(
                       [min(w["passive_cost"], 9) for w in by[r]]))
                   if r in by else None,
                   ac_median=float(np.median(
                       [min(w["active_cost"], 9) for w in by[r]]))
                   if r in by else None)
                   for r in RUNGS})
    json.dump(out, open(OUT / "D15A_TRACKB1_CENSUS.json", "w"),
              indent=1, default=str)
    print(json.dumps(out["verdicts"], indent=1))
    print("i2:", json.dumps(i2_checks))
    print("orth:", io_frac, go_frac)
    print("diff pairs:", contrasts)
    print("confound:", json.dumps(conf))
    print("anchors:", json.dumps(anchors))


if __name__ == "__main__":
    main()
