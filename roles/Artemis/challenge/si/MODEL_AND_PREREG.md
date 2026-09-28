# SI challenge, Phase 1 -- smallest resource model + preregistered simulation design

Seat: Artemis, 2026-09-28. Pure ASCII. PHASE 1 ONLY: no simulation has been run. The only computation
behind this file is the pen-and-paper derivation below plus tiny closed-form arithmetic (entropies of a
2-state source, section 3.7), done in a scratch script outside the repository. The freeze is the commit
that adds this file (made by whoever commits it; Artemis made no commit). Any later edit is an
amendment, dated, below the END line.

Worktree read: /home/jcraig/Prometheus-worktrees/artemis-base-role at HEAD a9d5f5f23.

Operator question, as this file operationalises it: under bounded memory, compute, latency and
environmental interaction, when does keeping a useful abstraction force an unavoidable resource cost,
and is that cost irreversibility or just a position on a frontier? Reversible computation is treated as
a serious countermodel. The phrase is not protected.

-----------------------------------------------------------------------------------------------------
## 1. The claim under attack, quoted from the sources

S1 (the candidate law; directive s1; path
roles/Cyclops/prompts/2026-09-25_selective_irreversibility/01_OPERATOR_DIRECTIVE_verbatim.md @ 608b672d5,
sha256 f0dd0599cbf6...; s1 = lines 18-43, section sha256 d5d14cdc8e03fc76... per HYPOTHESIS.md @ e2097951d):

    "In a bounded, reusable system that must predict, control, and generalize across changing
     environments, intelligence requires the selective elimination of distinctions from its
     accessible causal state while preferentially preserving distinctions relevant to future
     prediction and control."

THE "REQUIRES" CLAUSE: "intelligence requires the selective elimination of distinctions from its
accessible causal state". It has three parts: ELIMINATION (from ACCESSIBLE causal state), SELECTIVITY
(the distinctions preserved are the ones relevant to the future), and REQUIREMENT (intelligence cannot
avoid it).

S2 (scope; directive s2, same file): "Can a bounded, indefinitely reusable, generalizing adaptive
system avoid relevance-selective loss of accessible distinctions anywhere in the complete
agent/environment/resource cycle?" It adds: "A purported reversible counterexample does not count if it
merely exports an ever-growing history tape, accumulates unpriced memory, hides resets elsewhere, or
pushes irreversibility outside the accounting boundary." Section s4A asks for a reversible system with
bounded memory, "history is not hidden in an unbounded external store", and cyclic operation. Section s9
asks for logical and thermodynamic accounting to be kept distinguishable.

S3 (the elimination half, steward memo 11a; programs/selective_irreversibility/memo/
PORTFOLIO_MEMO_2026-09-25.md @ d50103524, sha256 9ab428c49859a634):

    "THE ELIMINATION HALF IS A THEOREM ... s1 concerns ACCESSIBLE causal state, and exporting is
     elimination from it. So any bounded system with fresh input eliminates distinctions. Only
     SELECTIVITY and REQUIREMENT are empirical."

It holds, per the pending-Cyclops rider, "when the input's entropy rate is positive". Cyclops's co-sign
(same file) adds that export INTO THE ENVIRONMENT counts as export.

S4 (Q1, the reading, still open; RULINGS.md @ 4f5d9bac8, 13:05Z entry): "Q1 the reading (now
load-bearing: does transient query-time contraction count? FALSIFIERS 12:40Z)". FALSIFIERS.md
@ 61e09d32f, 12:40Z entry:

    "'does transient, query-time contraction count as the contraction the law requires?' is
     LOAD-BEARING. If it counts, B cannot falsify the law on generalization tasks at all, which is an
     unfalsifiability region for s4B."

S5 (the WTP-LM01 reading; ensorain/PREREG_WTP_LM01.md @ 768ea8ce9, sha256 f2da31954d3e9da0, s1): LM01
tests the PERSISTENT-STATE reading. "A contraction done transiently at readout and then discarded (L-R)
is not persistent contraction. An L-R win is labelled LOSSLESS_TRANSIENT_CONTRACTION." Steward ruling
R1a (ensorain/lm01/STEWARD_RULINGS.md @ a71666665, sha256 018409900da6cdae): "An L-R win damages the
persistent-state law. It says nothing about a computation-inclusive law."

S6 (the "accessible" reading; DISAGREEMENTS.md @ 9478d54da, 20:25Z/20:40Z): accessible means
accessible TO THE ACTING SYSTEM. Support needs a MERGED certificate. Falsification needs demonstrated
use.

S7 (the prior-art constraint; roles/Artemis/backlog/prior_art/PA_memory_and_sagacity.md @ 4ea12f6a9,
W05): "with time unpriced, a bounded reversible agent CAN avoid elimination in principle. The law is
only non-trivial as a TIME-SPACE (throughput/latency) frontier claim."

-----------------------------------------------------------------------------------------------------
## 2. The smallest formal resource model

### 2.1 Task: online prediction of a known unifilar source

The source is a stationary, finite, minimal unifilar HMM (an epsilon-machine) G = (S, X, T, f, s0):
- causal states S;
- alphabet X;
- emission law T(x|s);
- deterministic update s' = f(s, x).

At every step t the system must output a predictive distribution P_t(.) for x_{t+1}.

PREDICTIVE SUFFICIENCY is exact and measurable, because the causal state S_t is the unique minimal
sufficient statistic of the past for the future (Shalizi & Crutchfield 2001). Define the excess
log-loss

    D = (1/T) sum_t [ -log2 P_t(x_{t+1}) + log2 T(x_{t+1} | S_t) ]   (bits/step, >= 0 in expectation)

D = 0 exactly iff the learner's predictions equal the oracle's. This is checked bitwise, not
statistically.

The model is KNOWN to every learner. The learners differ only in how they keep, or recover, the
information needed to know S_t. This isolates the state-maintenance question the law is about from
model learning. Model learning is a declared Phase-2 extension (section 7).

Source quantities (stationary, unifilar; derivation in 3.1):

    h   = H(X_t | S_{t-1})                        entropy rate (bits/step)
    C   = H(S_t)                                  statistical complexity (C_mu)
    g   = H(S_{t-1} | S_t, X_t)                   MERGE ENTROPY: the prior state lost by the update,
                                                  even given the symbol
    e   = H(X_t | S_t)                            INPUT RESIDUE: the symbol's information that the
                                                  new state does not keep
    identity:  h = g + e                          (3.1)
    r(W) = H(S_{t-1} | S_t, X_{t-W+1:t})          merge entropy NOT recoverable from a retained
                                                  window of W symbols (r(1) = g; non-increasing in W)
    m*(w) = H(S_t | X_{t-w+1:t})                  state entropy not recoverable from the last w symbols

### 2.2 Environment interaction: the retention horizon W (the axis the law has been missing)

The environment delivers x_t. W is the number of most recent symbols the ENVIRONMENT keeps readable,
current symbol included, at replay price rho per symbol read.
- W = 0, TRANSFER: x_t is moved into the agent's input register and the environment keeps no copy. The
  agent must dispose of it.
- W = 1, READ-ONCE: x_t is readable during step t only. The agent can copy it in and un-copy it
  (CNOT twice), so it never has to absorb it.
- 1 < W < inf, FINITE REPLAY: x_{t-W+1..t} is readable.
- W = inf, FULL REPLAY: the whole past is readable (a dataset, a persistent world, a reset-able
  simulator).

Writes into the environment (Cyclops's 11a addition) are EXPORTS, priced as in 2.4.

### 2.3 Learner classes

All learners run on one register machine.
- Its primitive ops are bijections on registers: XOR-copy/CNOT, swap, increment/decrement mod 2^k,
  table-permutation, controlled versions, and READ(env, j), which XORs x_j into a register.
- One IRREVERSIBLE primitive, ERASE(reg), sets a register to 0 and is counted.
- One EXPORT primitive, EXPORT(reg), swaps a register onto the append-only export tape and is counted.

A learner is REVERSIBLE iff it never ERASEs and passes the backward-run certificate (5.4).

    I      Irreversible minimal tracker. Holds s in ceil(log2|S|) bits; s <- f(s, x) in place. It
           ERASEs the merged predecessor (and, at W = 0, the input register). O(1) ops, O(1) latency.
    IW     Irreversible window-k: holds the last k symbols (FIFO; ERASEs the oldest) and decodes S_t
           if the window synchronises, else uses the belief from the window. Recency-selective,
           relevance-blind.
    IH     Irreversible random hash: an m-bit state updated by a fixed random many-to-one map of
           (state, x). Relevance-blind; merge rate matched to I (the s4C control).
    RH     Reversible history keeper (W = 0): appends every x_t to an agent-held store and updates s
           reversibly, because s is a function of the store. Memory grows; O(1) ops and latency.
    RX     Reversible exporter (W = 0): computes s' = f(s, x) into a fresh register, then EXPORTs the
           garbage (s, x | s'), about h bits/step. Agent memory is C; the export tape grows.
    RG-W   Reversible garbage keeper (W >= 1): never absorbs x. At a merge it first tries to
           recompute S_{t-1} from (S_t, retained window) and XOR it out. If that fails, it pushes the
           unrecoverable garbage onto an agent-held stack. Memory grows at the rate of unrecoverable
           merges (<= ceil(log2|S|) bits per such event; entropy rate r(W)).
    RU-W   Reversible uncomputer (W >= 1): as RG-W, but recomputes S_{t-1} from the retained window
           by an explicit reversible sub-computation (compute, copy/XOR, uncompute; Bennett 1973).
           Variants by workspace:
             RU-W/B    naive Bennett: workspace O(D log|S|) bits, O(D) ops, D = recompute depth;
             RU-W/LMT  Lange-McKenzie-Tapp: workspace O(log D + log|S|) bits, ops O(D |S|^2)
                       (Euler tour of the configuration tree; 3.4).
           For group-structured segments (parity) no garbage arises and the cost is O(D).
    RQ-W   Reversible lazy query-time recomputer (the L-R analog; the Q1 object). No persistent
           causal state, only a position pointer. At each query it recomputes S_t from the retained
           window, copies P_t out, then uncomputes. Latency = recompute depth. At W = 0 it is RH + RQ
           (an agent-held store plus a transient refit: exactly LM01's L-R shape).
    HK     Hybrid checkpointer: I plus K exact checkpoints of s (Bennett pebbles), used by RU when
           the window is too short. Pebble memory is counted.
    R-min  For co-unifilar sources (every f(., x) injective on reachable states): the machine itself
           run as a permutation automaton. ceil(log2|S|) bits, O(1), zero erasure (at W >= 1).

### 2.4 Cost vector (Pareto; no exchange rate, as in LM01 s5)

    M_agent   peak register width held by the agent (bits), worst case over the run; also the
              entropy estimate
    M_export  bits on the export tape (external memory the agent wrote)
    M_env     W * log2|X| bits the environment retains for the agent (counted only under boundary B3)
    C_step    primitive ops per step: amortised mean, and max
    C_query   ops per query
    LAT       ops on the query's critical path (for sequential programs, C_query of the answering path)
    REPLAY    env reads per step and per query (price rho per read)
    ERASE     logically erased bits per step (thermodynamic conversion reported separately: >= kT ln2
              per bit, Landauer; optional)
    D         excess log-loss (2.1); SYNC = fraction of steps with decoded state = S_t

Accounting boundaries (each reading is tagged with one):
- B1: agent only.
- B2: agent + export tape.
- B3: agent + export tape + environment-retained window. B3 is the directive's "complete
  agent/environment/resource cycle" reading.

### 2.5 Sources (small enough to simulate exactly)

    RP(q,a)   RESET-PARITY, the primary family.
              X = {0, 1, R}, S = {0, 1} (parity since the last R).
              From state p: emit R w.p. q; otherwise emit 1 w.p. b_p and 0 w.p. 1-b_p, with
              b_0 = a, b_1 = 1-a.
              Updates: 1 flips p, 0 keeps p, R sets p = 0.
              Unifilar and minimal for a != 1/2. q is the MERGE RATE, and 1/q the mean merge LOOKBACK.
              q = 0 is noisy parity, a co-unifilar (permutation) automaton.
    GM        Golden mean (A-0->A, A-1->B, B-0->A). It merges (g > 0) but has Markov order 1.
    EVEN      Even process (A-0->A, A-1->B, B-1->A). It has infinite Markov order but is CO-UNIFILAR
              (g = 0).
    RU(k,X)   Random unifilar machines: |S| = 2^k, k in {1,2,3,4,6}, |X| in {2,4}; f uniformly random;
              emissions Dirichlet(1). Kept only if strongly connected, minimal and synchronising.
              8 machines per (k, |X|).

-----------------------------------------------------------------------------------------------------
## 3. Analytic results (derived; each lists the resource assumptions it needs)

### 3.1 Conservation identity (exact, any unifilar source)

Because S_t = f(S_{t-1}, X_t) is a function, H(S_{t-1}, X_t) = H(S_t) + H(S_{t-1}, X_t | S_t).
Stationarity gives H(S_{t-1}) = H(S_t). So the information that one step of minimal tracking destroys is

    H(S_{t-1}, X_t | S_t) = H(X_t | S_{t-1}) = h
                          = H(S_{t-1} | S_t, X_t) + H(X_t | S_t) = g + e.

Sanity arithmetic, RP(q, a = .25):

    q      h      g      e      C      mean lookback
    0     .811   .000   .811   .811        inf
    .01   .884   .008   .876   .807        100
    .03   .981   .024   .957   .799         33
    .1   1.199   .077  1.122   .769         10
    .3   1.449   .201  1.248   .669        3.3

(Closed forms: pi_1 = (1-q)a; h = H2(q) + (1-q)H2(a); g = q H2(pi_1); e was computed directly and
matches h - g.)

### 3.2 T1 -- the elimination half is a theorem, but only at W = 0 or under B3

Assumptions: W = 0 (transfer), h > 0, agent memory <= m bits, lifetime T.

Statement. Any agent, competent or not, must dispose of at least h*T - m bits over T steps: the entropy
of what it received is h*T (+ O(1)) and it holds at most m.
- An irreversible agent ERASEs them (Landauer >= (hT - m) kT ln2 if heat is priced).
- A reversible agent EXPORTs them (RX), so M_export grows at h per step.

Under B2/B3 with bounded total memory, erasure is UNAVOIDABLE for T > m/h.

What it does NOT say. It does not link erasure to intelligence. A zero-competence agent at W = 0 erases
at the same rate. It is memo 11a/G1, with the conditions made explicit.

At W >= 1 (READ-ONCE or replay) T1 does not bind the agent at all. An agent that never absorbs x has
nothing to dispose of. The environment's own forgetting of x_{t-W} does the elimination, outside B1/B2.

So 11a's "any bounded system with fresh input eliminates distinctions" is true of the agent+window
composite (B3). It is false of the agent alone whenever W >= 1. Positive entropy rate (the 11a rider)
is necessary but not sufficient.

### 3.3 T2 -- co-unifilar worlds need no irreversibility at any competence (W >= 1)

Assumptions: W >= 1; every f(., x) is injective on reachable states (co-unifilar), e.g. EVEN, RP(q = 0).

Statement. R-min tracks S_t exactly with the same ceil(log2|S|) bits as I, O(1) ops, O(1) latency,
ZERO erasure and no export. Its step (s, x) -> (f(s, x), x) is a bijection, and x is left in the
environment.

Consequence. A countermodel-A instance exists with a ZERO premium on every axis. The EVEN process has
infinite Markov order, so the need for long memory does not create a need for irreversibility. The
source's MERGE structure does.

### 3.4 T3 -- full replay: reversible matches exactly, at a small compute premium (the LMT question)

Assumptions: W = inf (or W >= the maximum merge lookback in the run); replay reads priced at rho;
boundary B1 or B2.

Statement. RU-inf reproduces I's predictions bitwise (D = 0), with zero ERASE and zero export.
- Memory: M_agent <= ceil(log2|S|) + O(log T) (position pointer) + recompute workspace.
- Ops/step, amortised: 1 + O(sum over merge steps of the lookback L_t)/T.
- For RP each merge at an R recomputes the parity of the segment since the previous R. Segments
  partition time, so the recompute costs about 2 ops/step amortised, whatever q is. Parity is a
  group computation, so it leaves no Bennett garbage.
- Query latency is O(1): the state is maintained, and recomputes happen off the query's critical path.

For general (non-group) segments the recompute is itself irreversible and must be made reversible.
- Bennett (naive): O(D log|S|) workspace, O(D) ops.
- Bennett pebbling: O(log D log|S|) workspace, O(D^{log2 3}) ops.
- Lange-McKenzie-Tapp: O(log D + log|S|) workspace, O(D |S|^2) ops. The configuration graph of "run f
  over the segment" has D|S| nodes, and each predecessor check scans |S| states.

The LMT blow-up is exponential in the workspace, 2^{O(log D + log|S|)} = poly(D |S|). It is therefore
exponential in the state's BIT-width k = log2|S| (factor ~ 4^k) and polynomial in the lookback.
- For small causal state spaces, equal-memory reversibility is polynomially cheap.
- For k of order 30+, it is astronomically expensive, and the realistic reversible options move to
  more memory (Bennett) or more garbage.

That is the memory x compute trade, stated exactly. Buhrman-Tromp-Vitanyi give the intermediate
time/space curve between the LMT and Bennett endpoints.

RQ-inf (no persistent state; Q1 object): LAT = recompute depth (mean 1/q for RP, unbounded for
q -> 0). It is dominated by RU-inf whenever RU-inf exists. Its only role is to show that transient
query-time contraction can be done with zero erasure (compute-copy-uncompute).

Caveat, s2/s4A. At W = inf the environment is holding an ever-growing history tape. Under B3 that tape
is charged (M_env = T log2|X|), and T3 collapses into the W = 0 memory frontier: it becomes RH with the
store relocated. So T3 KILLS irreversibility only under B1/B2. Whether the environment's self-held
past is "the system's" memory is an accounting-boundary decision, not a fact the experiment can
discover.

### 3.5 T4 -- finite retention, unbounded life: the narrow survivor

Assumptions: 1 <= W < inf; agent memory bounded by m under B2 (exports count); lifetime T -> inf; exact
sufficiency (D = 0); a source with r(W) > 0.

(a) PROVEN for RP(q > 0) at W = 1, worst case. Let the reversible tracker be a permutation automaton on
    finite state set Q with decoder psi(M, x_t) = p_t. Define cls(M) = psi(pi_0(M), 0). This is
    well-defined and equals p_t, because a 0 keeps p and follows any history with positive probability.
    Then:
    - pi_R(Q_t) lies in class 0;
    - pi_1(Q_t & class0) lies in class 1;
    - the two sets are disjoint;
    - |pi_R(Q_t)| = |Q_t| because pi_R is a permutation.
    Hence |Q_{t+1}| >= |Q_t| + |Q_{t-1}|. The reachable register set grows like Fibonacci, so
    M_agent >= t log2(phi) - O(1) = 0.694 t bits. No bounded reversible exact tracker exists. The
    irreversible tracker I needs 1 bit.

(b) CONSTRUCTED upper bound, any W: RG-W needs agent-memory growth <= (rate of merges whose predecessor
    is not a function of (S_t, retained window)) * ceil(log2|S|) bits/step, entropy r(W).
    For RP: r(W) = q * H(p_{t-1} | x_{t-W+1..t-1}). Event rate q(1-q)^{W-1}.

    Tiny arithmetic, q = .1, a = .25:

        m*(w) = H(S_t | last w symbols) for w = 0..8:
            .769 .572 .427 .321 .242 .183 .138 .105 .080 bits
        r(W) = q * m*(W-1):
            W = 1: .077    W = 5: .024    W = 9: .008 bits/step

    The event rate at W = 64 is .1 * .9^63 = 1.3e-4/step. So a reversible agent with a 64-bit garbage
    budget runs exactly and erasure-free for about 5 x 10^5 steps. Lifetime per bit of memory grows
    EXPONENTIALLY in W for light-tailed lookback.

(c) CONJECTURE C1 (lower bound, general W): any bounded-register reversible exact tracker has register
    growth rate >= r'(W), the rate of unrecoverable merges. C1 is not proven for W > 1. The simulation
    probes it with an exact backtracking search (5.6); that probe is a check, not a proof.

(d) The eliminated information is automatically SELECTIVE. The Markov property gives
    future _|_ S_{t-1} | S_t. So whatever an exact tracker erases (the merge garbage) carries zero
    information about the future given what it keeps. At exact competence, "selective" is a theorem.
    Selectivity is an empirical question only in the LOSSY regime (m < C, or eviction under a byte cap)
    and in LEARNING (the partition is unknown).

### 3.6 T5 -- the memory x latency floor (reversible and irreversible alike)

Assumptions: persistent memory M, query latency budget LAT, replay window w = min(W, LAT/rho).

At query time S_t must be a function of (M_t, X_{t-w+1:t}). Hence

    H(M_t) >= m*(w) = H(S_t | X_{t-w+1:t})

whatever the learner's reversibility. For RP(.1, .25) this is the curve in 3.5(b). It is the part of the
law that is invariant across reversible and irreversible learners.

### 3.7 Where irreversible erasure is UNAVOIDABLE (summary)

    regime                                  agent must erase/export?          needs
    W = 0 (transfer), bounded M (B2)        YES, >= h - m/T bits/step, for    h > 0. Not competence-
                                            ANY agent (T1)                    specific.
    W >= 1, co-unifilar source              NO, at any competence (T2)        -
    W >= 1, Markov order <= W               NO (stateless decode)             -
    W = inf, B1/B2                          NO; compute premium ~2-3x ops,    replay priced, env past
                                            LAT O(1); LMT premium 4^k if      not charged
                                            memory must be equal (T3)
    W = inf, B3                             collapses to the W = 0 row        env past charged
    1 <= W < inf, merging source with       YES as T -> inf: rate >= r(W)     bounded M, unbounded T,
    unbounded lookback, exact tracking      (proven W = 1 for RP; C1 else);   exact sufficiency.
                                            a finite T is survivable at       Competence-specific:
                                            M >= r'(W) T, i.e. a finite       an agent that does not
                                            premium (T4)                      track erases nothing.
    heat priced (Landauer)                  rows above x kT ln2; heat is      a physical substrate
                                            owed exactly where erasure is

### 3.8 What this implies about "irreversibility" versus a frontier

The invariants of the model are:
1. the conservation identity (3.1), which says where h bits/step must go;
2. the sufficiency floor m*(w) (3.6);
3. the merge-recovery rate r(W) (3.5), a property of the SOURCE's reverse-time structure relative to the
   ENVIRONMENT's retention. It is related to causal irreversibility and crypticity in computational
   mechanics.

Irreversibility of the AGENT is forced only in one cell: finite retention (1 <= W < inf), an unbounded
lifetime, and bounded memory, for sources with r(W) > 0. Everywhere else the "cost" is a position on a
memory x compute x latency x retention(W) frontier. Reversible learners reach that frontier at the same
predictive sufficiency. At W = 0, erasure is forced for everyone and is not about intelligence.

-----------------------------------------------------------------------------------------------------
## 4. Candidate verdicts, fixed before any simulation

Two claims are judged separately.
- CLAIM-BROAD: "irreversible elimination is required for useful abstraction" (the s1 requires-clause
  read as an irreversibility law).
- CLAIM-NARROW (N*, below).

(K) LAW KILLED. Any predictive sufficiency achieved irreversibly is achieved reversibly at equal agent
    memory with a finite compute/latency/replay premium. The invariant is the frontier (3.6-3.8), not
    irreversibility. Scope: B1/B2 with W >= 1 and either co-unifilar sources, W >= lookback, or finite
    T with memory margin r'(W)T.

(N) NARROWER LAW SURVIVES:

    N*: For a bounded agent (all exports counted) that reads but does not consume its input, over an
    unbounded lifetime, in an environment that retains only a finite window W of its past, exact
    predictive tracking of a source with r(W) > 0 requires logically irreversible elimination at
    average rate >= r(W) bits/step. That rate lies between 0 and g, and g <= h. The eliminated
    information is conditionally independent of the future given the retained state.

    INVARIANT: r(W), a property of (source merge structure, environment retention). It is 0 for
    co-unifilar sources, 0 for Markov order <= W, and -> 0 as W -> inf for light-tailed lookback.

    RESOURCE ASSUMPTIONS, all required:
    - bounded M under B2;
    - finite W, with the environment's past not charged to the agent (B1/B2);
    - T -> inf (or T > M/r'(W));
    - exact (or near-exact) sufficiency.

    Unlike T1, N* is competence-specific: a non-tracking agent needs no erasure at W >= 1.

(U) UNDECIDABLE IN THIS MODEL. The boundary depends on an accounting choice the model cannot make.
    Under B3, every reversible success at W > 0 is re-priced as memory and T1 governs. Or C1 fails to
    close for W > 1 within the probe's cap.

EXPECTED (Artemis forecast, stated before any run; to be scored):
- CLAIM-BROAD: K, probability .85. T2 (EVEN, parity) and T3 are constructions, not hypotheses. The
  simulation can only fail to confirm them through an instrument defect.
- CLAIM-NARROW: N*, .75 at W = 1 (proven for RP; the simulation is a consistency check). .55 for C1 at
  W in {2, 3} (the rest is U).
- Programme-level: "N survives but it is not an irreversibility law about intelligence in general. It
  is a merge-recovery bound conditional on finite environmental retention."

-----------------------------------------------------------------------------------------------------
## 5. Simulation preregistration (Phase 2; NOT RUN)

### 5.1 Code and environment

- Python 3 stdlib + numpy only.
- A new directory, roles/Artemis/challenge/si/sim/, created only in Phase 2, holding:
  - regmachine.py: the register machine, reversible primitives with exact inverses, ERASE, EXPORT, and
    per-op counters (ops, reads, erase bits, export bits, register-width high-water mark);
  - sources.py;
  - learners.py (every learner in 2.3 as a register program);
  - run.py;
  - search_c1.py.
- Randomness: numpy PCG64. Learners never see the seeds.
- Seed for (family, cell, i) = int(sha256("SI-ART-P2|" + FREEZE_SHA + "|" + family + "|" + cell + "|"
  + str(i))[:8], 16), where FREEZE_SHA is the commit that adds this file.

### 5.2 Grid

    F1  RP(q, a = .25): q in {0, .01, .03, .1, .3};
        W in {0, 1, 2, 4, 8, 16, 64, inf};
        T = 8192; 8 seeds.
        Learners, where applicable:
            I, IW-k (k in {2, 8, 32}), IH (m = 8), RH, RX (W = 0), R-min (q = 0),
            RG-W, RU-W/B, RQ-W, HK (K in {1, 4}).
        Budgets for RG/HK: garbage-stack cap m in {8, 64, inf} bits. On overflow the learner switches
        to non-merging mode (no ERASE; loses sync); that switch is a declared behaviour.
    F2  GM, EVEN: W in {0, 1, 2, inf}; T = 8192; 8 seeds; learners I, R-min (EVEN), RG-W, RU-W, RQ-W.
    F3  RU(k, X): 80 machines; W in {1, 2, 4, 8, 16, inf}; T = 4096; 4 seeds.
        Learners: I, IH, RG-W, RU-W/B, RQ-W.
        The LMT sub-study is RU-W/LMT for k <= 4, W in {8, 32}, T = 512, 2 seeds, to measure the
        ops blow-up against |S|.
    F4  C1 probe (search_c1.py): exact backtracking search for permutation-automaton trackers of RP
        (q in {.1, .3}). Grid:
            W in {1, 2, 3};
            n (register states) in {2..32};
            all positive-probability histories up to depth d in {8, 10, 12}.
        A tracker must decode p_t exactly on all of them. Report n_min(d, W) or NOT_FOUND. The search
        cap is 10 CPU-min per (W, d); a capped cell reads U.

### 5.3 Metrics (per run; aggregated as median and max over seeds)

- D (excess log-loss, bits/step); SYNC.
- M_agent peak width, and its growth slope (bits/step, OLS over the second half of the run).
- M_export; M_env (B3).
- C_step (mean, max); C_query and LAT (mean, p99, max).
- REPLAY/step, REPLAY/query; ERASE bits/step.

Analytic companions, computed exactly (enumeration or closed form) and reported beside each cell:
h, g, e, C, r(W), m*(w).

### 5.4 Instrument fixtures (must PASS before any reading; a failure = INSTRUMENT_FAILURE, stop, no verdict)

- FX1 REVERSIBILITY CERTIFICATE. For every R* run: ERASE = 0, and running the inverse program backward
  (with the harness supplying the environment's past, and the export tape) returns the initial register
  file bitwise. For every I run: ERASE > 0, and the backward run fails.
- FX2 ORACLE. I's predictions equal T(.|S_t) bitwise (D = 0). Mean realised log-loss is within 3 SE of
  h.
- FX3 POSITIVE CONTROL (the boundary is detectable). RP(.1, .25), W = 1, garbage cap 8: RG-1 overflows
  at t within [0.5, 2] x 8/r'(1). After that, D > .05 bits/step. For RP(.1) at W = 1,
  r'(1) = q = .1 events/step.
- FX4 NEGATIVE CONTROL. RP(0, .25) and EVEN at W = 1: R-min has ERASE = 0, D = 0, and constant M_agent.
- FX5 BLIND CONTROL. IH at matched merge rate has D > 0 on every source with C > 0.1 bit. If it does
  not, the metric cannot tell selective from blind contraction.

### 5.5 Readings per cell (source, W, budget)

- REV_MATCH: some reversible learner has D = 0 (bitwise), M_agent <= budget, and a finite, bounded
  C_step and LAT. Its premium ratios against I are reported.
- REV_GAP: every reversible learner at that budget has either D > 0 or M_agent slope > 0, while I has
  D = 0 and bounded memory.
- SLOPE_CHECK: the measured M_agent slope of RG-W is within [0.5, 1.5] x r'(W)*ceil(log2|S|). This
  compares the prediction against the construction, not against optimality.

### 5.6 STOP RULES (outcome -> verdict; applied mechanically, in order)

- S0 Any FX1-FX5 FAIL -> INSTRUMENT_FAILURE. Fix, re-run the fixtures, and record the fix as an
     amendment. No verdict.
- S1 CLAIM-BROAD = K if ALL of the following hold:
     (i)   REV_MATCH in every W = inf cell of F1-F3 (B1/B2), with C_step <= 4 x I's mean (RU/B) and
           LAT <= I's + 2 ops. LMT is exempt from the 4x rule; its measured blow-up is reported
           against |S|^2 instead.
     (ii)  REV_MATCH with ZERO premium in every co-unifilar cell at W >= 1.
     (iii) REV_MATCH in every W >= Markov-order cell (GM at W >= 1).
     If (i) fails in some W = inf cell without an instrument cause, CLAIM-BROAD = N for that cell's
     source class, and the failure is reported as a counter-finding to T3.
- S2 CLAIM-NARROW = N* SURVIVES if:
     (i)   REV_GAP in RP(q > 0) at W = 1 for every bounded cap (the T4a theorem shows it);
     (ii)  SLOPE_CHECK passes in >= 80% of finite-W merging cells;
     (iii) F4 finds n_min(d, 1) >= Fib(d) (matches T4a) and NOT_FOUND or n_min growing in d at
           W in {2, 3}.
     If (iii) finds a BOUNDED n at W >= 2 for all d up to 12 (n_min constant over the last 2 depths),
     C1 is FALSIFIED at that W. N* then narrows to W = 1 only, and the finite-W row of 3.7 is
     restated.
- S3 CLAIM-NARROW = U if F4 hits its cap at W >= 2, or if the SLOPE_CHECK fraction is below 80% with no
     instrument cause.
- S4 BOUNDARY-DEPENDENCE flag, always reported. Every S1 reading is re-computed under B3. If K under
     B1/B2 turns to REV_GAP under B3 (expected in all W > 0 replay cells), the report states: "the
     verdict depends on whether the environment's retained past is charged to the agent (U by
     accounting choice)". The report never picks a boundary after seeing rows.
- S5 NO READING FROM ABSENCE. An RU/RG failure caused by our implementation, not by a theorem, is not
     REV_GAP. REV_GAP counts only where T1 or T4a applies, or where F4 has certified that no
     permutation tracker exists within n <= 32.

### 5.7 Runtime and resources

Estimate (from op counts, not measured):
- F1: about 2,000 valid runs x about 0.2 s;
- F2: about 300 x 0.2 s;
- F3: about 8,000 x 0.1 s;
- F4: at most 60 min, capped at 10 min per cell, and only the cells needed.

Hard budget: 1 CPU-hour total, 4 threads, 2 GB RAM, laptop.

BUDGET STOP: if the first 10% of jobs (in a fixed shuffled order) projects > 60 CPU-min, reduce in this
preregistered order:
1. F3 seeds 4 -> 2;
2. F1 T 8192 -> 4096;
3. F4 depth 12 -> 10.

Each reduction is disclosed. Memory is dominated by the history stores: RH at T = 8192 holds 8192 x 2
bits, which is negligible.

-----------------------------------------------------------------------------------------------------
## 6. Implications

### 6.1 Q1 (does transient query-time contraction count?)

The model resolves what Q1 hides. RQ performs ALL of its contraction transiently and with ZERO erasure
(Bennett compute-copy-uncompute).
- If Q1 = COUNTS: the requires-clause is satisfied by fully reversible systems. "Contraction" then means
  only "computes a many-to-one function of the past at query time", which every predictor with fewer
  outputs than histories does. It has no irreversibility content (a tautology region, as FALSIFIERS
  12:40Z feared).
- If Q1 = DOES NOT COUNT (persistent-state reading): RU/RQ at W = inf (B1/B2) and R-min at W >= 1 are
  persistent-state countermodels.

Either way, Q1 is not the load-bearing variable. W and the accounting boundary are. Artemis recommends
that the operator answer Q1 AND fix W and the boundary together.

### 6.2 WTP-LM01 (exact versus coarse retention; ensorain)

LM01's worlds deliver experience once to the learner. That is the W = 0 regime, with the store held by
the agent:
- L-K is RH;
- L-R is RH + RQ, exactly the transient-contraction object;
- the bounded arms are I-like.

In this regime T1 makes the bounded arms' elimination a theorem. With a known model, an exact store is
a superset of every statistic and so can never lose on information, only on compute and optimisation.
So:

(a) An LM01 "EXACT_RETENTION_PAYS" or "BOUNDED_SUFFICES" is a position on a memory x compute(x latency)
    Pareto frontier. It is evidence about sufficiency (the m*-type floor, in a LEARNING setting), and
    about optimiser and inductive-bias match (ANOMALIES 01:29Z and 02:49Z already found this). It is
    NOT evidence for or against irreversibility.
(b) LM01 has no ERASE meter and no reversibility certificate, so no LM01 label should use the word
    "irreversible". This is a reading recommendation. The frozen prereg is untouched.
(c) The part of LM01 that bears on the programme's empirical residue is F-C (selective versus random
    eviction at matched B). That is the LOSSY regime, where selectivity is not a theorem (3.5d).
(d) LOSSLESS_TRANSIENT_CONTRACTION stays correctly labelled. By 6.1 it cannot support an irreversibility
    law under either Q1 answer.

### 6.3 Harmonia's s12 freeze

The freeze should hold, BEFORE any reversible or LM01 row:
1. the accounting boundary (B1/B2/B3), explicitly including whether the environment's self-retained
   past is charged;
2. the environment retention horizon W of each experiment;
3. the lifetime (finite T or asymptotic);
4. exact versus approximate sufficiency;
5. a logical ERASE meter distinct from "loss of accessibility";
6. the Q1 answer.

Without items 1-2 the law is movable in exactly the way s12 forbids: by 3.4 and S4, the same reversible
run is a counterexample under B1/B2 and a non-counterexample under B3.

### 6.4 Rename and restate?

Yes, if the stop rules land as forecast. What survives is not "selective irreversibility" as a property
of intelligence. It is:
- (i) the bounded predictive-sufficiency frontier: m*(w), plus the memory x compute x latency x
  retention trade, which reversible and irreversible learners share;
- (ii) a narrow merge-recovery bound N* (irreversible elimination at rate >= r(W), forced only with
  finite environmental retention, an unbounded life, bounded memory and a merging source);
- (iii) the theorem that erasure by an exact tracker is automatically selective.

Suggested name: "bounded predictive sufficiency", with N* as its thermodynamic corollary. The empirical
residue for the fleet is the LOSSY and LEARNING regimes: which distinctions a system keeps when m < C,
and whether it finds the partition at all. That is where the s4C and LM01 F-C controls belong.

-----------------------------------------------------------------------------------------------------
## 7. Limitations (written before any run)

- The model is known; there is no learning. Generalization here means exact predictive sufficiency. The
  learning extension (count statistics are reversible to maintain, but absorbing x is not) is Phase 2b.
- C1 is unproven for W > 1. F4 is a bounded search, not a proof.
- Worst-case register width versus entropy: T4a bounds the register count, and r(W) is an entropy. Both
  are reported and neither is substituted for the other.
- The PRNG is deterministic. If the "environment" is a seeded simulator, its true entropy rate is 0, and
  an agent that knew the seed would need nothing. This is excluded by construction (the seed is hidden),
  and the exclusion is disclosed.
- Only unifilar sources are used. Non-unifilar HMMs have infinite causal-state sets; they are out of
  scope.
- Control and transfer (s1 "control ... generalize across changing environments") are not modelled.
  Switching regimes are only partially covered by RP's resets.

## 8. References

- Lange, McKenzie, Tapp (2000), JCSS 60:354.
  https://www.sciencedirect.com/science/article/pii/S0022000099916720 [web-checked in PA W05]
- Bennett (1973), "Logical reversibility of computation", IBM J. Res. Dev. 17:525 (UNVERIFIED).
- Bennett (1989), "Time/space trade-offs for reversible computation", SIAM J. Comput. 18:766
  (UNVERIFIED).
- Buhrman, Tromp, Vitanyi (2001), "Time and space bounds for reversible simulation", J. Phys. A 34:6821.
  https://arxiv.org/abs/quant-ph/0101133 [web-checked 2026-09-28: LMT and Bennett are the endpoints of
  the pebble-game trade-off]
- Landauer (1961), IBM J. Res. Dev. 5:183 (UNVERIFIED).
- Still, Sivak, Bell, Crooks (2012), PRL 109:120604. https://arxiv.org/abs/1203.3271 [web-checked in
  PA W03]
- Shalizi, Crutchfield (2001), J. Stat. Phys. 104:817. https://arxiv.org/abs/cond-mat/9907176
  (UNVERIFIED)
- Crutchfield, Ellison, Mahoney (2009), "Time's barbed arrow: irreversibility, crypticity, and stored
  information", PRL 103:094101. https://arxiv.org/abs/0902.1209 [web-checked 2026-09-28; the link from
  r(W) to its causal irreversibility is Artemis's, UNVERIFIED]
- Garner, Thompson, Vedral, Gu (2017), "Thermodynamics of complexity and pattern manipulation", PRE
  95:042140. https://arxiv.org/abs/1510.00010 [web-checked 2026-09-28: least dissipation from the
  minimal-memory devices]
- Tishby, Pereira, Bialek (1999), information bottleneck. https://arxiv.org/abs/physics/0004057
  (UNVERIFIED)

END
