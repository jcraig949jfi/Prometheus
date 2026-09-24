# PTE v1 -- Packet-Tensor Engine: substrate specification

Currency: 2026-09-24. Status: DESIGN (stage 4 of the mission). This file
is the normative semantics. The GPU engine (prometheus/ananke/) and the
independent CPU oracle (prometheus/ananke/oracle.py) are both written
FROM THIS FILE; conformance = bit-identical state digests. Any
disagreement between code and this file is a defect in one of them,
resolved by a dated annotation here, never a silent edit.

Primitive-set version: PTE-OPS-1. Substrate version: PTE-SUB-1.

## 0. Design choices and why (recorded, per mission s18 "make a
## defensible choice, record it, continue")

C1. ALL-INTEGER SUBSTRATE. Every register, packet payload, routing
    weight and energy value is an integer held in int32 and saturated to
    [-32767, 32767] (routing/energy have their own ranges). Reasons:
    (a) bit-exact determinism on any GPU and against a CPU oracle, so
    replay is exact on RunPod hardware too (mission s15); (b) integer
    scatter-add is order-independent, so packet superposition is
    deterministic without torch deterministic-algorithm flags; (c)
    bitwise/modular/threshold primitives are native, which keeps the
    vocabulary away from float "neuron" idioms (mission s1, s3).
    Saturation (not wrap) on every write; MOD is the explicit wrap
    primitive. Products of two saturated values fit in int32
    (32767^2 < 2^31), so no intermediate overflows.
C2. COUNTER-BASED HASH RANDOMNESS. No stateful RNG. Every random draw
    is a pure function H(world_seed, stream, tick, site, j). Streams are
    named and disjoint (Ensorain rule: separate rng streams), so a
    control that changes one stream (e.g. loss) does not shift any other
    stream's draws, and a transplant never desynchronises the world.
C3. PACKETS SUPERPOSE. A packet is (channel, payload[P]). Arrivals at
    one site on one channel in one tick ADD (sum) and are COUNTED.
    Receivers see per-channel sums and counts, not individual packets.
    This is the cheapest physically meaningful arrival law and makes
    collisions, interference and bandwidth genuine physics. Source
    identity is ABSENT in v1 (mission: "optionally absent").
C4. PROGRAMS, NOT LAYERS. The local update law is a short straight-line
    program (L instructions, 5 integer fields each) over a register
    file. Programs are world genomes with G rule variants; each site runs
    the variant its rule register selects. Field values are reduced
    modulo the current register-space sizes at execution, so ANY
    genome is valid under ANY dials -- which is what makes transplants
    across physics defined.
C5. THE OUTER SEARCH IS DECLARED. Update laws are found by a plain
    mutation + truncation-selection loop over world genomes (the search,
    not the substrate). Resemblance recorded: this is a genetic
    algorithm over linear register programs (linear GP). The substrate
    never sees a gradient.
C6. NO CPU PROTOTYPE. The oracle exists only as a correctness witness
    on tiny configs (mission s2).

## 1. Shapes and dials

A BATCH is B independent worlds sharing one PHYSICS (all dials except
seeds and genomes). Each world has N sites.

Physics dials (all recorded in every receipt; names are the receipt
keys):

    topology        ring | torus | random | smallworld | global
    n_sites         N (torus: side*side)
    radius          r  (ring/torus neighbourhood, Manhattan)
    k_random        out-degree for random/smallworld extra edges
    rewire          smallworld rewire fraction (per mille)
    state_dim       D   persistent registers per site (>=1; S0 = actuator)
    payload_width   P   (>=1)
    channels        C   (>=1; C=1 means "channel field absent")
    fanout          F   copies per emission (dest_mode=sample)
    dest_mode       sample | all
    loss            packet loss probability (per copy), 0..1
    loss_per_hop    0|1: survival = (1-loss)^dist
    lat_base, lat_hop, lat_jitter   latency = base + hop*dist + U{0..jitter}
    dup             duplicate probability per copy
    noise           payload additive noise amplitude sigma (integer)
    cap             receiver bandwidth: max packets per site per tick
                    (0 = unlimited)
    collision       none | aloha | saturate
    decay_shift     0 (none) or k: S -= S >> k each tick
    update_mode     sync | async
    update_period   sync: sites run when t % period == 0
    update_p        async: wake probability per tick
    rules           G rule variants per genome (>=1)
    prog_len        L instructions per rule
    plastic_route   0|1  routing-table writes honoured
    adapt_shift     routing write scaling (w += rval >> adapt_shift)
    wimm            0|1  WIMM (writable immediates) honoured
    setrule         0|1  SETRULE honoured
    mut_site        in-lifetime per-site parameter mutation prob per tick
    e_income, e_max, c_emit, c_op, c_mem   energy economy (all 0 = off)

Environment dials (per family, s6): spatial scale d, temporal scale,
change rate, cue amplitude, distractor amplitude.

## 2. Hash randomness (normative)

    M32 = 0xFFFFFFFF
    hash32(x):  x &= M32
                x ^= x >> 16; x = (x * 0x7FEB352D) & M32
                x ^= x >> 15; x = (x * 0x846CA68B) & M32
                x ^= x >> 16; return x
    H(k1, ..., kn):  h = 0x811C9DC5
                     for k in (k1..kn): h = hash32(h ^ (k & M32))
                     return h

Inputs are non-negative Python ints or integer arrays (broadcast).
Implementations use 64-bit integer containers; the masked low 32 bits
of the product are exact under two's-complement wrap.

Stream ids: WAKE=1 ROUTE=2 LOSS=3 LAT=4 DUP=5 NOISE=6 RANDOP=7 MUT=8
INIT=9 ENV=10 CTRL=11. A draw is H(ws, stream, t, n, j) with ws the
world seed (uint32), t the tick, n the site, j a sub-index.

Probability test: bern(p16, h) = (h & 0xFFFF) < p16, where
p16 = round(p * 65536) computed once on the host (Python round).

## 3. Topology

Neighbour table nbr[N, R] (site indices) and dist[N, R] (hops):

- ring: offsets -r..-1, 1..r in that order; dist = |offset|. R = 2r.
- torus (side s, N=s*s, site n = y*s + x): all (dx, dy) with
  1 <= |dx|+|dy| <= r, enumerated dy from -r to r, then dx from -r to r;
  neighbour ((y+dy) mod s)*s + ((x+dx) mod s); dist = |dx|+|dy|.
- random: for each site n, k_random targets drawn as
  (n + 1 + H(topo_seed, INIT, 0, n, j) mod (N-1)) mod N, j=0..k-1;
  dist = 1. (Duplicates allowed; they are real parallel edges.)
- smallworld: torus radius 1 (R=4), then each entry independently
  rewired if (H(topo_seed, INIT, 1, n, j) mod 1000) < rewire, to
  (n + 1 + H(topo_seed, INIT, 2, n, j) mod (N-1)) mod N; rewired dist = 1.
- global: no table. Each copy's recipient is
  (n + 1 + h mod (N-1)) mod N; dist = 1. Routing weights unused.

topo_seed is a physics-level seed (shared by the batch).

## 4. Site state

Per world b, site n:

    S[D]      persistent registers, int32 saturated; init 0
    E         energy, init e_max (economy off: fixed at e_max)
    r         rule index in [0, G); init H(ws, INIT, 0, n, 7) mod G
    w[R]      routing weights in [0, 1023]; init 16
    Kp[L]     writable immediate offsets in [-32767, 32767]; init 0
    Acc_sum[C, P], Acc_cnt[C]   inbox accumulators; init 0

Mailbox ring (in-flight packets): Msum[LM, C, P], Mcnt[LM, C] per site,
LM = 1 + max possible delay.

## 5. Register file and instruction semantics (PTE-OPS-1)

Register file for an executing site (index order is normative):

    [0, D)                 S           persistent (read/write)
    [D, D+4)               T0..T3      temporaries, zeroed each run
    [D+4, D+8+P)           O: emit, chan, rport, rval, pay0..pay{P-1}
                           zeroed each run
    --- write space ends here: NW = D + 8 + P ---
    [NW, NW+C*P)           IN_sum[c*P + p]   clamp(Acc_sum, +-32767)
    [.., + C)              IN_cnt[c]         clamp(Acc_cnt, 0, 32767)
    next                   SENSE
    next                   ENERGY = min(E, 32767)
    next                   ZERO   (always 0)
    --- read space size NR = NW + C*P + C + 3 ---

Instruction fields (op, dst, a, b, imm), stored as ints; op in [0,256),
dst/a/b in [0,256), imm in [-128,127]. At execution:

    op' = op mod 16; d = dst mod NW; A = reg[a mod NR]; B = reg[b mod NR]
    bf = b (raw field, used as a small constant by some ops)
    I = clamp(imm + Kp[i], -32767, 32767)      i = instruction index
    sat(x) = clamp(x, -32767, 32767)

    0  NOP
    1  MOV     reg[d] = A
    2  ADD     reg[d] = sat(A + B)
    3  SUB     reg[d] = sat(A - B)
    4  MULQ    reg[d] = sat((A * B) >> 8)            arithmetic shift
    5  ADDI    reg[d] = sat(A + I)
    6  CONST   reg[d] = sat(I << (bf & 7))           I*2^(bf&7)
    7  GT      reg[d] = 256 if A > B else 0
    8  SEL     reg[d] = A if reg[d] > 0 else B       gated write
    9  MAX     reg[d] = max(A, B)
    10 SHR     reg[d] = A >> (bf & 15)               arithmetic
    11 XOR     reg[d] = sat(A ^ B)
    12 MOD     reg[d] = A mod (|B| + 1)              floor mod, >= 0
    13 RAND    m = |A|; reg[d] = (H(ws,RANDOP,t,n,i) mod (2m+1)) - m
    14 SETRULE if setrule and G > 1: r_next = A mod G   (last one wins)
    15 WIMM    if wimm: Kp_next[A mod L] = sat(B)       (in order; later
               writes to the same slot win); reg unchanged

Instructions execute sequentially i = 0..L-1; each reads the register
file as left by instruction i-1. SETRULE and WIMM take effect after the
program (r := r_next; Kp := Kp_next). A site executes rule
genome[b, r, :, :] where r is its rule index at the START of the tick.
nonnop = count of instructions with op' != 0.

## 6. The tick (normative order), for t = 0, 1, ..., T-1

1. DELIVERY. slot = t mod LM. For each site: cnt_c = Mcnt[slot, c],
   tot = sum_c cnt_c.
   - collision=aloha and cap>0 and tot > cap: the slot's contents are
     discarded (counted as `collided`).
   - collision=saturate and cap>0 and tot > cap: sums and counts are
     scaled: sum := (sum * cap) // tot (floor division toward -inf),
     cnt := (cnt * cap) // tot   (superposed energy is capped).
   - otherwise delivered unchanged.
   Acc_sum += delivered sums (then clamp +-2^20); Acc_cnt += counts
   (clamp 0..2^20). Slot zeroed.
2. ENVIRONMENT. SENSE[n] := env input for (b, t, n) (0 if none).
3. WAKE. sync: awake = (t mod update_period == 0).
   async: awake = bern(update_p16, H(ws, WAKE, t, n, 0)).
4. RUN (awake sites only). Build the register file from S, zeros for
   T and O, clamped Acc views, SENSE, ENERGY, ZERO. Then Acc := 0 for
   awake sites (asleep sites keep accumulating). Execute the program
   (s5). Write back S. Apply r_next and Kp_next.
5. ECONOMY (only if any of c_emit, c_op, c_mem, e_income is non-zero).
   want = awake and O.emit > 0. copies = F (sample) or R (all).
   emit_cost = c_emit * copies. If want and E < emit_cost: want = 0.
   spend = (emit_cost if want) + (c_op * nonnop if awake)
           + c_mem * count(S != 0).
   E := clamp(E + e_income - spend, 0, e_max).
   Economy off: want = awake and O.emit > 0; E unchanged.
6. ROUTING WRITE. If plastic_route and awake and O.rval != 0 and the
   topology has a table: j = O.rport mod R;
   w[j] := clamp(w[j] + (O.rval >> adapt_shift), 0, 1023).
7. EMISSION. For each wanting site, channel c = O.chan mod C, payload
   q[p] = O.pay[p]. For copy f = 0..copies-1:
   - recipient: dest_mode=all -> table entry f. dest_mode=sample ->
     h = H(ws, ROUTE, t, n, f); W = sum(w); if W == 0: j = h mod R,
     else u = h mod W, j = number of k with cumsum(w)[k] <= u.
     global topology: recipient = (n + 1 + h mod (N-1)) mod N, dist 1.
   - loss: survive16 = round(((1-loss)^dist if loss_per_hop else
     (1-loss)) * 65536) (host table by dist); lost if
     (H(ws, LOSS, t, n, f) & 0xFFFF) >= survive16.
   - latency: delay = clamp(lat_base + lat_hop*dist
     + H(ws, LAT, t, n, f) mod (lat_jitter+1), 1, LM-1).
   - noise: q'[p] = sat(q[p] + (H(ws, NOISE, t, n, f*16+p) mod
     (2*noise+1)) - noise) if noise > 0 else q[p].
   - deliver (if not lost): Msum[(t+delay) mod LM, c, :] += q' at the
     recipient; Mcnt[..., c] += 1.
   - duplicate: if bern(dup16, H(ws, DUP, t, n, f)): a second copy with
     its own loss draw H(ws, LOSS, t, n, f+4096), delay2 = clamp(delay
     + 1 + H(ws, DUP, t, n, f+4096) mod (lat_jitter+1), 1, LM-1), same
     noisy payload q'.
8. LOCAL MUTATION. If bern(mut_site16, H(ws, MUT, t, n, 0)):
   Kp[H(ws, MUT, t, n, 1) mod L] := (H(ws, MUT, t, n, 2) mod 257) - 128.
9. DECAY. If decay_shift > 0: S := S - (S >> decay_shift), all sites.
10. READOUT. The environment reads S0 of its actuator sites for
    scoring after this step.

LM = 1 + clamp(lat_base + lat_hop*maxdist + lat_jitter + lat_jitter + 1).

## 7. Environment families (v1)

Common: sensors and actuators are sites chosen per episode from the ENV
stream at a preregistered spatial scale d (graph distance). Targets
y in {-1, +1} are EXACTLY balanced within an episode (half each,
order from the ENV stream), so every constant policy scores exactly
0.5. A readout scores 1 if sign(S0) == y, 0.5 if S0 == 0, else 0.
Cue input: SENSE = A*x for the cue window (A = 256 default).

- RELAY  (temporal prediction + transport). Sensor s, actuator a at
  distance d. Each trial: cue x on s for c ticks; readout at a at
  trial_start + delta. y = x.
- XOR    (spatially separated evidence). Sensors s1, s2 at distance >= d
  from each other and from a; cues x1, x2; y = x1*x2. Each sensor alone
  carries zero information about y (exact, by construction).
- MAJ    (distributed evidence). k=5 sensors; each receives x flipped
  with probability 0.3 (independently); y = x; actuator at distance d
  from all sensors' centroid (nearest site).
- FLIP   (changing mappings). Sensor s, actuator a, teacher site f.
  y = m*x; after each readout the teacher site receives SENSE = A*y for
  c ticks (the correct answer, delivered AFTER the readout). m flips
  every `block` trials; the total number of trials under m=+1 and m=-1
  is equal. Scored on trials that are not the first of their block.
- HOLD   (delayed intervention / memory). Sensor = actuator site. Cue at
  trial start; then `gap` ticks of distractors (SENSE = +-A_dist, A_dist
  < A, random signs); readout after the gap. y = the cue.

Env dials: d (spatial scale), delta / gap (temporal scale), block
(change rate), A, A_dist.

## 8. What is NOT in v1 (deliberate)

Source identity, per-packet TTL/multi-hop auto-forwarding (relay is only
by site programs; distance-dependent latency and per-hop loss stand in
for diffusion), packet-carried code, reproduction of sites. Each is a
candidate dial for v2 if the census shows v1 cannot reach a question.

## 9. Rulings on the oracle author's ambiguity list (2026-09-24)

The independent oracle (prometheus/ananke/oracle.py, written from this
file without reading the engine) listed 19 ambiguities A1-A19 in its
module docstring. Ruling: ALL NINETEEN of its literal readings are
adopted as normative, verbatim as written there. Notes:
- A1: LM = 1 + max(1, lat_base + lat_hop*maxdist + 2*lat_jitter + 1),
  maxdist = max of the dist table (1 for random/smallworld/global).
- A2: global topology requires dest_mode=sample (Physics.validate
  refuses the other); copies = F.
- A12: SENSE is saturated to +-32767 in the register file. The engine
  did NOT do this in its first draft (found by this list, fixed before
  any conformance run; irrelevant for |SENSE| <= 256 but it was a
  divergence).
- A7/A17: stats vocabulary differs between implementations (the oracle
  also counts `saturated`); conformance compares state, traces and the
  attempted/delivered/lost/collided counters only.
