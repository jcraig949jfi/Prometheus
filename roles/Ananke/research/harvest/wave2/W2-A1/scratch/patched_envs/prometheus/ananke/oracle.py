"""PTE v1 independent CPU correctness oracle (pure Python + NumPy).

Written ONLY from roles/Ananke/pte/DESIGN.md (sections 2-6), without
reading the GPU engine. Clarity over speed: explicit loops over worlds,
sites, instructions and packet copies. All arithmetic uses Python ints
(arbitrary precision) and explicit masks/clamps. `>>` is arithmetic
(floor) shift, `%` is floor mod, `//` is floor division.

Public API
----------
    hash32(x), H(*keys)                       DESIGN.md s2
    p16(p)                                    round(p * 65536)
    build_topology(phys) -> (nbr, dist)       s3; (None, None) for global
    compute_LM(phys, dist)                    s6 last line
    run(phys, genomes, world_seeds, sense, T) s4-s6

AMBIGUITIES
-----------
A1  (DESIGN.md L252) LM formula `1 + clamp(lat_base + lat_hop*maxdist +
    lat_jitter + lat_jitter + 1)` gives clamp() no bounds. Implemented:
    LM = 1 + max(1, lat_base + lat_hop*maxdist + 2*lat_jitter + 1), i.e.
    lower bound 1 only (so LM >= 2 and the delay range [1, LM-1] is never
    empty). The 2*jitter+1 term is included even when dup == 0. maxdist =
    max of the dist table (ring/torus: r in practice; random/smallworld/
    global: 1).
A2  (L218, L131-132) dest_mode=all with topology=global: R is undefined
    (no table). Implemented: global always uses copies = F with the
    hashed recipient (the global rule is listed under dest_mode=sample at
    L231-232), regardless of dest_mode.
A3  (L218, L227-228) `copies` for dest_mode=all is R (the full table,
    including duplicate/parallel/self entries); copy f goes to nbr[n][f]
    with dist[n][f]. For sample, copies = F.
A4  (L227-228) Emission payload/channel are the O registers as left at
    the END of the program (step 4), read in step 7; the routing write
    (step 6) happens BEFORE sampling, so a site's own rval changes the
    weights its same-tick emission samples from.
A5  (L242-245) The duplicate draw is taken regardless of whether the
    primary copy was lost; the duplicate goes to the same recipient and
    channel, uses the same noisy payload q', its own loss draw
    H(ws,LOSS,t,n,f+4096) against the same survive16 (same dist), and
    delay2 is computed from the already-clamped primary delay.
A6  (L217-223) Economy on: E is updated for ALL sites (asleep sites also
    get e_income and pay c_mem*count(S!=0)); c_mem counts S after the
    write-back of step 4 (and before decay). The `E < emit_cost` test uses
    E before this tick's update. Economy off (all four of c_emit, c_op,
    c_mem, e_income zero): E stays at e_max, no affordability test.
    e_max is used even if economy is off (ENERGY = min(e_max, 32767)).
A7  (L205-206) Saturate mode: sum := (sum*cap)//tot uses Python floor
    division, so negative sums round toward -inf (e.g. -5*1//2 = -3).
    Applied per (c, p) and per c for counts. `collided` counts only aloha
    discards (tot packets); saturate events are counted separately in
    stats['saturated'] (number of packets removed = tot - sum of scaled
    counts) and are NOT added to `collided`.
A8  (L208-209) Accumulator clamps are inclusive +-2^20 (= +-1048576) for
    Acc_sum and [0, 2^20] for Acc_cnt, applied after each delivery add.
    Mailbox Msum/Mcnt themselves are never clamped (unbounded ints).
A9  (L189-194) WIMM writes go to Kp_next (a copy of Kp at program start)
    in instruction order, later writes to the same slot win; the I value
    of later instructions in the SAME run still uses the start-of-run Kp.
    Likewise SETRULE writes r_next (init = r), last one wins, applied
    after the program; the program executed is the start-of-tick r.
A10 (L248) Decay applies to all sites (awake or asleep); no extra
    saturation is needed (S - (S >> k) stays in range). Note -1 >> k = -1
    so S = -1 decays to 0.
A11 (L142) Rule init r = H(ws, INIT, 0, n, 7) mod G, using the WORLD seed
    ws (the topology uses topo_seed with the same (INIT, 0, n, j) key
    layout, a different stream only by seed).
A12 (L161, L15-17) SENSE is not given a clamp in the register table; C1
    says every register is saturated to +-32767. Implemented: SENSE is
    saturated to +-32767 when placed in the register file (identical to
    the literal reading whenever |SENSE| <= 32767).
A13 (L174-190) Ops without an explicit sat() (MOV, GT, SEL, MAX, SHR,
    MOD, RAND) write the raw result; given A12 all such results are in
    range anyway. Genome fields are used raw (not re-range-checked):
    op mod 16, dst mod NW, a/b mod NR with Python floor mod; bf = raw b;
    imm raw. CONST computes sat(I * 2**(bf & 7)).
A14 (L123-124) Torus enumeration is nested: outer loop dy = -r..r, inner
    dx = -r..r, keeping 1 <= |dx|+|dy| <= r. On small tori, wrapped
    entries may repeat or hit the site itself; they are kept (as for
    random-topology parallel edges). Ring likewise keeps wrapped repeats.
A15 (L65, L128-130) k_random is documented as "extra edges" for
    smallworld too, but s3 defines smallworld as rewired radius-1 torus
    only (R = 4). Implemented per s3: no extra edges.
A16 (L233-235) survive16 is computed on the host with Python floats:
    round(((1-loss)**dist if loss_per_hop else (1-loss)) * 65536). loss=0
    gives 65536 (never lost), loss=1 gives 0 (always lost).
A17 stats (not in spec): per tick, 'emitted' = primary copies attempted
    (wanting sites x copies), 'dup' = duplicate copies attempted,
    'delivered' = copies (primary + duplicate) written into a mailbox,
    'lost' = primary + duplicate copies lost. Invariant:
    emitted + dup == delivered + lost. 'collided' = packets discarded by
    aloha at delivery; 'saturated' see A7.
A18 (L246-247) Local mutation runs for all sites (awake or not), after
    step 4 has applied Kp_next. Written value lies in [-128, 128].
A19 (L213-215) Clamped Acc views are built into the register file BEFORE
    Acc is zeroed; only awake sites zero Acc.
"""
from __future__ import annotations

import math

import numpy as np

M32 = 0xFFFFFFFF
SAT = 32767
ACC_LIM = 1 << 20

WAKE, ROUTE, LOSS, LAT, DUP, NOISE, RANDOP, MUT, INIT, ENV, CTRL = range(1, 12)

OP_NAMES = ["NOP", "MOV", "ADD", "SUB", "MULQ", "ADDI", "CONST", "GT", "SEL",
            "MAX", "SHR", "XOR", "MOD", "RAND", "SETRULE", "WIMM"]


# --------------------------------------------------------------------- s2
def hash32(x: int) -> int:
    x = int(x) & M32
    x ^= x >> 16
    x = (x * 0x7FEB352D) & M32
    x ^= x >> 15
    x = (x * 0x846CA68B) & M32
    x ^= x >> 16
    return x


def H(*keys) -> int:
    h = 0x811C9DC5
    for k in keys:
        h = hash32(h ^ (int(k) & M32))
    return h


def p16(p: float) -> int:
    return int(round(float(p) * 65536))


def bern(p16v: int, h: int) -> bool:
    return (h & 0xFFFF) < p16v


def clamp(x: int, lo: int, hi: int) -> int:
    return lo if x < lo else (hi if x > hi else x)


def sat(x: int) -> int:
    return clamp(x, -SAT, SAT)


# --------------------------------------------------------------------- s3
def _side(n_sites: int) -> int:
    s = math.isqrt(n_sites)
    if s * s != n_sites:
        raise ValueError(f"torus n_sites={n_sites} is not a perfect square")
    return s


def _torus(N: int, r: int):
    s = _side(N)
    nbr, dist = [], []
    for n in range(N):
        y, x = divmod(n, s)
        row, drow = [], []
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                m = abs(dx) + abs(dy)
                if 1 <= m <= r:
                    row.append(((y + dy) % s) * s + ((x + dx) % s))
                    drow.append(m)
        nbr.append(row)
        dist.append(drow)
    return nbr, dist


def build_topology(phys: dict):
    topo = phys["topology"]
    N = int(phys["n_sites"])
    ts = int(phys["topo_seed"])
    if topo == "global":
        return None, None
    if topo == "ring":
        r = int(phys["radius"])
        offs = list(range(-r, 0)) + list(range(1, r + 1))
        nbr = [[(n + o) % N for o in offs] for n in range(N)]
        dist = [[abs(o) for o in offs] for n in range(N)]
        return nbr, dist
    if topo == "torus":
        return _torus(N, int(phys["radius"]))
    if topo == "random":
        k = int(phys["k_random"])
        nbr = [[(n + 1 + H(ts, INIT, 0, n, j) % (N - 1)) % N for j in range(k)]
               for n in range(N)]
        dist = [[1] * k for _ in range(N)]
        return nbr, dist
    if topo == "smallworld":
        nbr, dist = _torus(N, 1)
        rew = int(phys["rewire"])
        for n in range(N):
            for j in range(len(nbr[n])):
                if H(ts, INIT, 1, n, j) % 1000 < rew:
                    nbr[n][j] = (n + 1 + H(ts, INIT, 2, n, j) % (N - 1)) % N
                    dist[n][j] = 1
        return nbr, dist
    raise ValueError(f"unknown topology {topo!r}")


def compute_LM(phys: dict, dist) -> int:
    maxdist = 1 if dist is None else max((max(row) for row in dist if row), default=1)
    inner = (int(phys["lat_base"]) + int(phys["lat_hop"]) * maxdist
             + int(phys["lat_jitter"]) + int(phys["lat_jitter"]) + 1)
    return 1 + max(1, inner)          # A1


# ------------------------------------------------------------------ s5
def execute_program(prog, S, T_unused, in_sum, in_cnt, sense, energy, Kp, r,
                    *, D, P, C, G, L, ws, t, n, wimm, setrule):
    """Run one site's program. Returns (reg, r_next, Kp_next, nonnop).

    prog: list of L (op, dst, a, b, imm). S: list D. in_sum: C*P list
    (already clamped). in_cnt: C list (clamped). Kp: list L.
    """
    NW = D + 8 + P
    reg = list(S) + [0] * 4 + [0] * (4 + P) + list(in_sum) + list(in_cnt) \
        + [sense, energy, 0]
    NR = NW + C * P + C + 3
    assert len(reg) == NR
    r_next = r
    Kp_next = list(Kp)
    nonnop = 0
    for i in range(L):
        op, dst, a, b, imm = (int(v) for v in prog[i])
        opp = op % 16
        d = dst % NW
        A = reg[a % NR]
        B = reg[b % NR]
        bf = b
        I = clamp(imm + Kp[i], -SAT, SAT)
        if opp != 0:
            nonnop += 1
        if opp == 0:
            pass
        elif opp == 1:
            reg[d] = A
        elif opp == 2:
            reg[d] = sat(A + B)
        elif opp == 3:
            reg[d] = sat(A - B)
        elif opp == 4:
            reg[d] = sat((A * B) >> 8)
        elif opp == 5:
            reg[d] = sat(A + I)
        elif opp == 6:
            reg[d] = sat(I * (1 << (bf & 7)))
        elif opp == 7:
            reg[d] = 256 if A > B else 0
        elif opp == 8:
            reg[d] = A if reg[d] > 0 else B
        elif opp == 9:
            reg[d] = max(A, B)
        elif opp == 10:
            reg[d] = A >> (bf & 15)
        elif opp == 11:
            reg[d] = sat(A ^ B)
        elif opp == 12:
            reg[d] = A % (abs(B) + 1)
        elif opp == 13:
            m = abs(A)
            reg[d] = (H(ws, RANDOP, t, n, i) % (2 * m + 1)) - m
        elif opp == 14:
            if setrule and G > 1:
                r_next = A % G
        elif opp == 15:
            if wimm:
                Kp_next[A % L] = sat(B)
    return reg, r_next, Kp_next, nonnop


# ------------------------------------------------------------------ s6
def run(phys: dict, genomes, world_seeds, sense, T: int) -> dict:
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
                        if lost:
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
                            if lost2:
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
