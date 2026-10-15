"""Hooked copy of the PTE CPU oracle's run loop (C-019-T040, Argus). READ-ONLY reuse of prometheus/ananke/oracle.py.

Why a copy: oracle.run has no between-tick hook and no zero-communication control, and prometheus/ananke/ is the
owner's lane (no edits). Every helper (hash, topology, LM, execute_program) is IMPORTED from the oracle unchanged; only
the tick loop is copied, with two marked additions (ARGUS-ADD). tests/test_runner.py pins: (1) no hook, no zero_comm
-> every returned array equals oracle.run; (2) the oracle source lines this copy came from are unchanged (sha256).
"""
from __future__ import annotations

import numpy as np

from prometheus.ananke.oracle import (ACC_LIM, DUP, INIT, LAT, LOSS, MUT, NOISE, ROUTE, SAT, WAKE, M32, H,  # noqa: F401
                                      bern, build_topology, clamp, compute_LM, execute_program, p16, sat)

ORACLE_SOURCE = "prometheus/ananke/oracle.py"
ORACLE_RUN_LINES = (277, 511)


def run(phys: dict, genomes, world_seeds, sense, T: int, after_tick=None, zero_comm=False) -> dict:
    """oracle.run (prometheus/ananke/oracle.py:277-511, copied verbatim at the pinned SHA) plus TWO additions,
    each marked ARGUS-ADD: after_tick(t, b, S_b) is called once per world after every tick, AFTER the S0
    readout trace is recorded (the engine's lens.run between-tick hook semantics, lens.py:86-87); zero_comm
    drops every copy at delivery (engine Controls.zero_comm: 'no packet is ever delivered (emission still
    costs)'; the dropped copies are counted under stats['lost']). With neither, the output equals oracle.run
    bit for bit (tests/test_runner.py)."""
    nbr, dist = build_topology(phys)
    is_global = nbr is None
    N = int(phys["n_sites"])
    D = int(phys["state_dim"])
    P = int(phys["payload_width"])
    C = int(phys["channels"])
    F = int(phys["fanout"])
    G = int(phys["rules"])
    L = int(phys["prog_len"])
    R = 0 if is_global else len(nbr[0])
    dest_all = phys["dest_mode"] == "all"
    loss = float(phys["loss"])
    loss_per_hop = int(phys["loss_per_hop"])
    lat_base = int(phys["lat_base"])
    lat_hop = int(phys["lat_hop"])
    jit = int(phys["lat_jitter"])
    dup16 = p16(phys["dup"])
    noise = int(phys["noise"])
    cap = int(phys["cap"])
    collision = phys["collision"]
    decay_shift = int(phys["decay_shift"])
    async_mode = phys["update_mode"] == "async"
    period = int(phys["update_period"])
    wake16 = p16(phys["update_p"])
    plastic = int(phys["plastic_route"])
    adapt = int(phys["adapt_shift"])
    wimm = int(phys["wimm"])
    setrule = int(phys["setrule"])
    mut16 = p16(phys["mut_site"])
    e_income = int(phys["e_income"])
    e_max = int(phys["e_max"])
    c_emit = int(phys["c_emit"])
    c_op = int(phys["c_op"])
    c_mem = int(phys["c_mem"])
    economy = any(v != 0 for v in (c_emit, c_op, c_mem, e_income))

    LM = compute_LM(phys, dist)
    # A16: host survival table by dist
    def survive16(dd: int) -> int:
        s = (1.0 - loss) ** dd if loss_per_hop else (1.0 - loss)
        return int(round(s * 65536))
    surv_tab = {}

    genomes = [[[[int(v) for v in ins] for ins in rule] for rule in world]
               for world in np.asarray(genomes).tolist()]
    Bn = len(world_seeds)
    assert len(genomes) == Bn
    for g in genomes:
        assert len(g) == G and all(len(rule) == L for rule in g)
    sense = np.asarray(sense)

    # s4 state
    S = [[[0] * D for _ in range(N)] for _ in range(Bn)]
    E = [[e_max] * N for _ in range(Bn)]
    rr = [[H(int(world_seeds[b]), INIT, 0, n, 7) % G for n in range(N)]
          for b in range(Bn)]
    w = [[[16] * R for _ in range(N)] for _ in range(Bn)]
    Kp = [[[0] * L for _ in range(N)] for _ in range(Bn)]
    Acc_sum = [[[[0] * P for _ in range(C)] for _ in range(N)] for _ in range(Bn)]
    Acc_cnt = [[[0] * C for _ in range(N)] for _ in range(Bn)]
    Msum = [[[[[0] * P for _ in range(C)] for _ in range(N)] for _ in range(Bn)]
            for _ in range(LM)]
    Mcnt = [[[[0] * C for _ in range(N)] for _ in range(Bn)] for _ in range(LM)]

    stats = {k: [] for k in ("emitted", "dup", "delivered", "lost",
                             "collided", "saturated")}
    S0_trace = np.zeros((T, Bn, N), dtype=np.int64)

    for t in range(T):
        st = dict.fromkeys(stats, 0)
        slot = t % LM
        for b in range(Bn):
            ws = int(world_seeds[b]) & M32
            # ---- 1. DELIVERY
            for n in range(N):
                cnts = Mcnt[slot][b][n]
                sums = Msum[slot][b][n]
                tot = sum(cnts)
                if collision == "aloha" and cap > 0 and tot > cap:
                    st["collided"] += tot
                    dsum = [[0] * P for _ in range(C)]
                    dcnt = [0] * C
                elif collision == "saturate" and cap > 0 and tot > cap:
                    dsum = [[(sums[c][p] * cap) // tot for p in range(P)]
                            for c in range(C)]
                    dcnt = [(cnts[c] * cap) // tot for c in range(C)]
                    st["saturated"] += tot - sum(dcnt)
                else:
                    dsum = [list(row) for row in sums]
                    dcnt = list(cnts)
                for c in range(C):
                    for p in range(P):
                        Acc_sum[b][n][c][p] = clamp(
                            Acc_sum[b][n][c][p] + dsum[c][p], -ACC_LIM, ACC_LIM)
                    Acc_cnt[b][n][c] = clamp(Acc_cnt[b][n][c] + dcnt[c], 0, ACC_LIM)
                Msum[slot][b][n] = [[0] * P for _ in range(C)]
                Mcnt[slot][b][n] = [0] * C

            # per-site outputs of the RUN step
            O = [None] * N
            awake_v = [False] * N
            nonnop_v = [0] * N
            for n in range(N):
                # ---- 2. ENVIRONMENT
                sv = int(sense[t, b, n]) if sense is not None else 0
                # ---- 3. WAKE
                if async_mode:
                    awake = bern(wake16, H(ws, WAKE, t, n, 0))
                else:
                    awake = (t % period == 0)
                awake_v[n] = awake
                if not awake:
                    continue
                # ---- 4. RUN
                in_sum = [clamp(Acc_sum[b][n][c][p], -SAT, SAT)
                          for c in range(C) for p in range(P)]
                in_cnt = [clamp(Acc_cnt[b][n][c], 0, SAT) for c in range(C)]
                Acc_sum[b][n] = [[0] * P for _ in range(C)]
                Acc_cnt[b][n] = [0] * C
                reg, r_next, Kp_next, nonnop = execute_program(
                    genomes[b][rr[b][n]], S[b][n], None, in_sum, in_cnt,
                    sat(sv), min(E[b][n], SAT), Kp[b][n], rr[b][n],
                    D=D, P=P, C=C, G=G, L=L, ws=ws, t=t, n=n,
                    wimm=wimm, setrule=setrule)
                S[b][n] = reg[:D]
                rr[b][n] = r_next
                Kp[b][n] = Kp_next
                O[n] = reg[D + 4: D + 8 + P]
                nonnop_v[n] = nonnop

            for n in range(N):
                awake = awake_v[n]
                o = O[n]
                # ---- 5. ECONOMY
                if is_global or not dest_all:
                    copies = F
                else:
                    copies = R
                want = awake and o[0] > 0
                if economy:
                    emit_cost = c_emit * copies
                    if want and E[b][n] < emit_cost:
                        want = False
                    spend = ((emit_cost if want else 0)
                             + (c_op * nonnop_v[n] if awake else 0)
                             + c_mem * sum(1 for v in S[b][n] if v != 0))
                    E[b][n] = clamp(E[b][n] + e_income - spend, 0, e_max)
                # ---- 6. ROUTING WRITE
                if plastic and awake and o[3] != 0 and not is_global:
                    j = o[2] % R
                    w[b][n][j] = clamp(w[b][n][j] + (o[3] >> adapt), 0, 1023)
                # ---- 7. EMISSION
                if want:
                    c = o[1] % C
                    q = o[4:4 + P]
                    for f in range(copies):
                        if is_global:
                            h = H(ws, ROUTE, t, n, f)
                            rcp, dd = (n + 1 + h % (N - 1)) % N, 1
                        elif dest_all:
                            rcp, dd = nbr[n][f], dist[n][f]
                        else:
                            h = H(ws, ROUTE, t, n, f)
                            W = sum(w[b][n])
                            if W == 0:
                                j = h % R
                            else:
                                u = h % W
                                cs, j = 0, 0
                                for k in range(R):
                                    cs += w[b][n][k]
                                    if cs <= u:
                                        j += 1
                            rcp, dd = nbr[n][j], dist[n][j]
                        if dd not in surv_tab:
                            surv_tab[dd] = survive16(dd)
                        s16 = surv_tab[dd]
                        st["emitted"] += 1
                        lost = (H(ws, LOSS, t, n, f) & 0xFFFF) >= s16
                        delay = clamp(lat_base + lat_hop * dd
                                      + H(ws, LAT, t, n, f) % (jit + 1), 1, LM - 1)
                        if noise > 0:
                            qn = [sat(q[p] + (H(ws, NOISE, t, n, f * 16 + p)
                                              % (2 * noise + 1)) - noise)
                                  for p in range(P)]
                        else:
                            qn = list(q)
                        if lost or zero_comm:  # ARGUS-ADD zero_comm
                            st["lost"] += 1
                        else:
                            sl = (t + delay) % LM
                            for p in range(P):
                                Msum[sl][b][rcp][c][p] += qn[p]
                            Mcnt[sl][b][rcp][c] += 1
                            st["delivered"] += 1
                        if bern(dup16, H(ws, DUP, t, n, f)):
                            st["dup"] += 1
                            lost2 = (H(ws, LOSS, t, n, f + 4096) & 0xFFFF) >= s16
                            delay2 = clamp(delay + 1 + H(ws, DUP, t, n, f + 4096)
                                           % (jit + 1), 1, LM - 1)
                            if lost2 or zero_comm:  # ARGUS-ADD zero_comm
                                st["lost"] += 1
                            else:
                                sl = (t + delay2) % LM
                                for p in range(P):
                                    Msum[sl][b][rcp][c][p] += qn[p]
                                Mcnt[sl][b][rcp][c] += 1
                                st["delivered"] += 1
                # ---- 8. LOCAL MUTATION
                if bern(mut16, H(ws, MUT, t, n, 0)):
                    Kp[b][n][H(ws, MUT, t, n, 1) % L] = (H(ws, MUT, t, n, 2) % 257) - 128
                # ---- 9. DECAY
                if decay_shift > 0:
                    S[b][n] = [v - (v >> decay_shift) for v in S[b][n]]
                # ---- 10. READOUT
                S0_trace[t, b, n] = S[b][n][0]
            if after_tick is not None:  # ARGUS-ADD between-tick hook (after readout)
                after_tick(t, b, S[b])
        for k in stats:
            stats[k].append(st[k])

    i64 = lambda x: np.array(x, dtype=np.int64)
    return {
        "S": i64(S).reshape(Bn, N, D),
        "E": i64(E).reshape(Bn, N),
        "r": i64(rr).reshape(Bn, N),
        "w": i64(w).reshape(Bn, N, R),
        "Kp": i64(Kp).reshape(Bn, N, L),
        "Acc_sum": i64(Acc_sum).reshape(Bn, N, C, P),
        "Acc_cnt": i64(Acc_cnt).reshape(Bn, N, C),
        "Msum": i64(Msum).reshape(LM, Bn, N, C, P),
        "Mcnt": i64(Mcnt).reshape(LM, Bn, N, C),
        "S0_trace": S0_trace,
        "stats": stats,
        "LM": LM,
    }

