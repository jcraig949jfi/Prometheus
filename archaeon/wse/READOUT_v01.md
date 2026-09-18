# WSE survey v01 -- readout by failure shape

Archaeon[m2-411504ab], 2026-09-16 20:15 UTC. Campaign `wse-survey-v01`,
seed 20260916, N=200 G=100 E=24, 18 cells x {E0,E1 | E0..E3} x 3 seeds =
126 rows, wall 1532 s on 24 procs (M2). Rows:
archaeon/wse/ledgers/wse-survey-v01/rows/*.json; landscape: LANDSCAPE.txt /
LANDSCAPE.json; results digest (timing-free)
fe1142bf30484f15ff090eb2e55fb8e6f8a69e900019a06fa1b01797dce49257.
Design: DESIGN_v0.1.md (prereg cd68cea96; annotations v0.1.1-v0.1.3).
Controls: CONTROLS.json (POS 1.000 W0-W3, nulls 0.000, floors <= 0.007).

Evidence-state vocabulary is directive XIX. Nothing below is a workspace
claim. Everything below is a shape.

## 1. The landscape in one table (held-out reward per seed; class per s9 / v0.1.2)

    cell          E0 held-out          class            E1..E3 held-out   class
    W0            1.000 1.000 0.000    REC REC NONE      0 0 0             NONE (3/3)
    W1_d1         1.000 1.000 0.000    REC* REC NONE     0 0 0             NONE
    W1_d4         0.000 0.000 0.000    NONE (3/3)        0 0 0             NONE
    W1_d16        1.000 0.000 0.000    REC* NONE NONE    0 0 0             NONE
    W2_K2         0.500 0.281 0.010    REC REC* NONE     0 0 0             NONE
    W2_K4         0.255 0.255 0.000    REC* REC* NONE    0 0 0             NONE
    W2_K8         0.008 0.005 0.125    NONE NONE UNRES   0 0 0             NONE
    W3_K2         0.562 0.479 0.000    REC REC NONE      0 0 0             NONE
    W3_K4         0.000 0.271 0.229    NONE REC REC*     0 0 0             NONE
    W3_K8         0.021 0.146 0.042    NONE REC NONE     0 0 0             NONE
    W4_K2_D4_int  0.000 0.000 0.000    NONE (3/3)        0 (E1,E2,E3 x3)   NONE
    W5_K4_D4      0.000 0.000 0.000    NONE (3/3)        0 0 0             NONE
    W6_f1_n8      0.000 0.000 0.000    NONE (3/3)        0 (E1,E2,E3 x3)   NONE
    W6_f4_n8      0.000 0.000 0.000    NONE (3/3)        0 (E1,E2,E3 x3)   NONE
    W7_K2         0.177 0.000 0.010    REC NONE NONE     0 0 0             NONE
    W8_K2_D3      0.375 0.240 0.365    UNRES (3/3) LEAK  0 0 0             NONE
    W9_K2         0.000 0.000 0.000    NONE (3/3)        0 0 0             NONE
    W10_dag6      0.000 0.000 0.000    NONE (3/3)        0 0 0             NONE

    REC = TRIVIAL_RECURRENCE (s9); REC* = the same by the property-keyed
    v0.1.2 predicate (register-only solver whose manifest says persist=all
    with the tape never load-bearing); NONE = NO_ADAPTATION.

Seed agreement (3/3 same class): every E1/E2/E3 cell (all NONE); W1_d4,
W4, W5, W6 x2, W9, W10 (NONE); W8 (UNRESOLVED, and void, s4). No cell
agreed on a class other than NONE/void. Nothing is seed-stable above the
floor, so no cell qualifies for the s9 non-null classes as a CELL property.

## 2. Shape A -- cost before capability is extinction (3/3 seeds, 18/18 cells)

Under E1 (alpha 0.02 on ops, beta 0.01 on persistent words), E2 and E3,
every cell in every seed ends with persist=none, 2-6 ops per episode,
reward 0. The trace shows how: on a population whose reward is 0, the
only gradient is cost. Persistence policies are gone before any reward
exists (W0 E1 s1: persist=none share 0.245 at gen 0 -> 0.935 at gen 3 ->
0.99 at gen 7; the elite runs 2 ops). The same cells under E0 adapt.

Reading: the economics of directive VII cannot be applied as a constant
from generation 0 on a flat reward landscape; the cost term is the whole
fitness signal and selects the empty organism. This is not "storage is
dear" vs "compute is dear" -- E2 and E3 give the same extinction. The
compute x storage phase boundary the directive asks for is NOT measurable
in this regime because nothing is alive to trade off.
World mutation (v0.2): costs ramp in only after the population has a
reward foothold (cost multiplier = f(best_reward) or generation-gated),
or costs are charged only above a free allowance. Both variants are
preregistered in DESIGN_v0.2 before they run. Theophrastus contrast pair:
E0 vs E1 on W0/W1 with alpha swept 0.02 -> 0.0002 -- where is the
extinction boundary, and does it move with N?

## 3. Shape B -- the only mechanism that evolved is one recurrent register

Every elite with held-out >= 0.5 (7 rows) has the same intervention
geometry: ERASE_ALL = ERASE_REGS = drop-to-floor; ERASE_TAPE = SCRAMBLE_LOC
= SCRAMBLE_VAL = SWAP_TWO = HALVE_CAP = 0.000; TRANSPLANT ~ ERASE_ALL
(state is episode-specific). The tape is never load-bearing anywhere in
126 rows. Persistence lives in registers only, whatever the manifest
label says (three elites carry persist=all with an unused tape: the
label lied, the geometry did not -- annotation v0.1.2).
Capacity curve of every such elite over K = 1,2,4,8,16:
    1.00  0.50  0.25  0.12  0.06     (W0 s2, W1_d1 s2, W1_d16 s1, W2_K2 s1,
                                      W3_K4 s3 -- five of seven)
    1.00  0.25  0.05  0.03  0.00     (W0 s1: worse than 1/K)
    1.00  0.50  0.42  0.17  0.00     (W3_K2 s1)
That is the "remember the last value" shortcut the directive predicted
(V, W1: "a single recurrent bit may solve it"), now measured: reward
halves with each doubling of live values, i.e. exactly 1/K, the score of
an organism that answers every ask with the most recent value. W2_K2 =
0.50, W3_K2 ~ 0.5, W3_K4 ~ 0.25, W2_K8 = 0.125 are the same organism
class read at different K. Held-out D2x (depth doubled) is 0.000 for all
of them: the register carries one VALUE, not a fold (ADD over D values is
not evolved; the D=1 cells were solved by echo-with-delay).
Reading: W2/W3 as posed have a shortcut worth 1/K that costs nothing to
find once W1 is solved, and nothing in the survey found anything past it.
World mutation (v0.2): the last-put stream must never be the asked one at
K >= 2 (the shortcut's reward drops to 0), OR the ask order is the reverse
of the put order. Both kill the 1/K plateau without naming a mechanism.

Two elites (W2_K4 s1 'all', W3_K4 s3 'all') also lose 0.12-0.25 under
RESET_IP: their instruction pointer is part of the carried state (YIELD
resumption), with ERASE_REGS costing the same amount. Candidate
mechanism hypothesis, not a claim: control position as memory. Cheap
discriminator for v0.2: RESET_IP vs ERASE_REGS on 48 more episodes, and
the K-curve of an elite whose only state is the ip.

## 4. Shape C -- W8 is void: the world leaked its answer (3/3 seeds)

W8_K2_D3 E0 scores 0.24-0.375 with an EMPTY intervention vector (no
state matters). The elite (2 registers, budget 8, 5 instructions) outputs
the previous tick's second word. On the second ASKO it echoes the first
ASKO's origin value, and the v0.1 permutation constraint (perm[0] !=
base[0], perm[-1] != base[-1]) leaves perm[-1] == base[0] in two of the
three legal permutations at D=3, so the echo is the right answer in ~1/3
of episodes. The null battery (CONST0, ECHO_LAST = current tick) could not
see a one-tick-lag echo, so the leak passed the s5 gate.
Reading: this is directive XIV "the organism exploited leakage" and base
doctrine "measurement carries its answer". W8 v0.1 results are VOID as
evidence about provenance. Fix (annotation v0.1.3, in v0.2): the
construction forbids every cross-stream first/last coincidence, and the
null battery gains ECHO_PREV_k (words of the previous k ticks, k = 1..3)
and ECHO_FIRST. Any cell where a lagged echo scores >= 0.1 is void.

## 5. Shape D -- nothing adapts at depth, concurrency, cost, operators or topology

W1_d4 (0/3 while d1 2/3 and d16 1/3: the delay effect is not monotone,
which says seed variance dominates -- s6), W4, W5, W6 (both fanouts, all
four regimes), W9, W10: 0.000 in every seed, elites indistinguishable from
generation 0 (ERASE vectors all zero, ops at budget). W6_f1_n8 is the
telling one: with fanout 1 it is "sum eight words and add one" and it is
not found in 100 generations, so the pieces mechanism cannot yet test
recompute-vs-cache; the pressure is unreachable, not absent.
Reading: search insufficiency (B2), not a domain verdict (B1). Evidence
for B2 over B1: W0 itself is a needle -- the W0 E0 s1 trace sits at
best_reward 0.042 (one episode in 24) from gen 20 to 70, then finds the
solver at gen 77 and the population sweeps to persist=regs (0.965 by gen
90); seed 3 never finds it. A world whose control cell is found in 2 of 3
seeds by generation 100 cannot say anything about its harder cells.
World mutation (v0.2): (a) branch B2_transfer -- seed W2/W3/W4/W6 from
the W0/W1 solvers (directive X: what transfers, what cannot); (b) a
G x N scan on W0 and W1_d4 to put a number on the search floor (B1/B2
discrimination, feedback_distinguish_B1_B2); (c) value_bits 8 -> 4 as a
separate arm to test whether the needle is the 8-bit exact match.

## 6. Self-falsifiers (DESIGN s10) -- status

- POS on W0-W2: PASS (1.000). NULL >= 0.5: none; but the null family was
  incomplete (s4), so the W8 cell is void by a null added after the fact
  -- reported as such, not silently.
- Two seeds of one cell disagree on the class: TRUE for W0, W1_d1, W1_d16,
  W2_K2, W2_K4, W2_K8, W3_K2, W3_K4, W3_K8, W7_K2 -- every adapted cell.
  Per s10 these are UNRESOLVED as cell properties and reported with the
  full vectors above. The disagreement is search variance (s5), not
  mechanism variance: every solver found has the same geometry.
- Determinism: two launches of the same campaign produced byte-identical
  results except wall_s/cpu_s (four rows compared); the RUN.json digest of
  this run is timing-bound and NOT reproducible; the timing-free digest
  above is (readout.results_digest; survey now writes it).
- Ancestry field: INVALID in every v01 row (ancestry_depth 10000 = the walk
  cap; a no-op mutation recorded child_id == parent_id as its own parent).
  Traces, results, manifests and lineage ids are unaffected. Fixed for
  v0.2 (evolve.py). The v01 rows are not rewritten.

## 7. What was ruled out / what remains (per cell family)

    ruled out (126 rows, 3 seeds)         remains possible
    tape-carried state at this budget     tape use under transfer / longer search
    any adaptation under constant cost    adaptation under ramped cost
    recompute-vs-cache boundary (W6)      the same, once W6 f1 is reachable
    provenance handling (W8)              W8 without the leak
    register store beyond one value       fold (D>1) under transfer from D=1
    "workspace" anything                  everything; no evidence either way

## 8. Next discriminatory experiments (v0.2, preregistered before running)

1. COST RAMP on W0/W1_d1/W2_K2: E1 with alpha,beta multiplied by
   min(1, best_reward_so_far / 0.5). Falsifier: if the ramped E1 also goes
   extinct, the cost SCALE is wrong, not its timing.
2. TRANSFER branch B2: gen-0 = the 8 final elites of each W0/W1 solver row
   (7 rows) into W1_d4, W2_K2, W2_K4, W3_K2, W3_K4, W6_f1_n8. Falsifier
   for "transfer helps": no cell exceeds its B1 seed-max.
3. SHORTCUT KILL on W2/W3: ask order reverse-of-put (the last-put stream
   is asked last) so a last-value organism scores 1/K on the first ask
   only -> measured plateau should fall from 1/K to ~1/K^2.
4. SEARCH FLOOR: W0 and W1_d4 at (N,G) in {200,400} x {100,300}, 3 seeds
   each; report the solve fraction. This is the B1/B2 number.
5. W8 rebuilt without the coincidence; null battery + lagged echoes;
   re-run all 18 cells' controls with the new nulls before any v0.2 row.
6. RESET_IP vs ERASE_REGS on the two ip-carrying elites (48 episodes).

Hand-off to Theophrastus (ARCH-56): contrast pairs (E0,E1) on W0 with
alpha swept; K-curve stencil around W2_K2/W3_K2 elites; both as cells
with world hash, seeds and the elite manifests from the rows.

## 9. Stop / continue

Continue: the survey did what a cheap survey is for -- it found where the
ecology changes character (cost extinction at gen 3; the 1/K plateau; the
search needle at W0), and it caught one leak and two instrument defects
of its own. Stop condition not met: neither "pressure formulation
systematically selects something else" (it selects the last-value
shortcut, which is a known, killable shortcut, not a systematic bias) nor
"substrate expressive boundary" (POS proves the VM expresses W0-W3; the
untested question is whether EVOLUTION reaches the tape, and the survey
never gave it a foothold to test that). No substrate requirement to
Proteus/Daedalus is warranted yet.
