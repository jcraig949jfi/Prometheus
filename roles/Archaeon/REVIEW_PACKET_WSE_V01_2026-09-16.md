+==========================================================================+
|  REVIEW PACKET -- WSE SURVEY v01                                         |
|  Computational Workspace Ecology: the cheap survey (worlds W0-W10)       |
|  Author: Archaeon (seat, instance m2-411504ab, machine M2 / SPECTREX5)   |
|  Date: 2026-09-16                                                        |
|  For: the operator (HITL) and external reviewers                        |
|  Status: SURVEY COMPLETE; three failure shapes; one world VOID; v0.2     |
|          not yet preregistered                                           |
|  Self-contained: every load-bearing number is inline; no repo access     |
|  is needed to critique this packet.                                      |
+==========================================================================+

-----------------------------------------------------------------------
0. SUMMARY, MANDATE, VERDICT
-----------------------------------------------------------------------

Mandate (operator, 2026-09-16, verbatim directive on file): build worlds
and pressures under which organisms MAY evolve machinery for keeping
unfinished computation persistent, addressable, resumable, shareable and
recombinable. Never reward "having a workspace"; never name an affordance
after the hoped-for mechanism; behavioural success licenses nothing
without intervention evidence; begin with a cheap survey and find where
the ecology changes character.

What was done today: an event-stream world grammar in which every
pressure of the directive (W0-W10) is a knob setting; four fitness
regimes; a selection loop over an existing, unmodified organism VM; hand-
written positive and null controls; nine state interventions; a
preregistered design; a survey of 18 cells x 2-4 regimes x 3 seeds = 126
evolutionary runs (N=200, G=100, 24 episodes/generation), 1532 s wall on
24 cores; a readout by failure shape.

Verdict (evidence-state vocabulary of the directive, section XIX):
  - pressure created, world validated: W0-W3 (positive controls 1.000,
    nulls 0.000, generation-0 floor <= 0.007).
  - adaptation observed, intervention-sensitive: seven elites, all the
    SAME mechanism -- one recurrent register, tape never load-bearing.
  - mechanism hypothesis (weak): instruction pointer as carried state in
    two elites.
  - VOID: W8 (provenance) -- the world leaked its answer to a one-tick-
    lag echo.
  - unresolved everywhere else: nothing adapted at depth, concurrency,
    shared intermediates, operators-as-data, or random topology, and the
    control cell itself is found in only 2 of 3 seeds, so the harder
    cells are search-limited, not domain-limited.
  - NO workspace claim of any kind. None was expected from a survey.

Lean: CONTINUE, with the world mutated (not the organisms) along four
named axes, each preregistered before it runs. "Stop" is defensible only
if the reviewer judges the search-needle result (section 6D) to mean the
substrate cannot give evolution a foothold at all; section 7 argues it
does not.

-----------------------------------------------------------------------
1. WHAT WAS BUILT (and what was committed before any measurement)
-----------------------------------------------------------------------

Substrate REUSED, untouched: the Proteus player VM (Prometheus's existing
organism runtime). 25 opcodes (NOP HALT YIELD LDC MOV LD ST ADD SUB MUL
AND OR XOR NOT SHL SHR EQ LT JMP JZ JNZ IN INQ OUT RND); state = registers
(2-16), a tape (16-4096 words; the genome sits at its front), an
instruction pointer; per-tick input/output channels of 32-bit words. The
manifest fields are EVOLVABLE by the existing mutation grammar (12
operators incl. a splice crossover and a "config perturbation" that steps
n_regs, tape_words, tick_budget, code_writable and the PERSIST policy in
{none, regs, tape, all} = what survives across ticks). YIELD ends a tick
keeping the instruction pointer; HALT resets it. Nothing was added to the
VM. No affordance is named after a computational interpretation.

Built (archaeon/wse/, ~1100 lines, 25 tests):
  worlds.py        one event grammar. Per tick the organism receives the
                   words of ONE event on input channel 0; some ticks
                   expect an answer (first output word).
                     PUT [1,tag,v]            stream tag: s := s (op) v
                     PUT [1,tag,p1..pn]       "expensive": v = sum(p_i)
                     ASK [2,tag]              expect s_tag
                     ASKX [3,tag,y,(pieces)]  expect s_tag (op) y
                     ASK2 [4,tagA,tagB,c]     expect combine_c(s_A,s_B)
                     ASKO [5,v0]              expect LAST value of the
                                              stream whose FIRST was v0
                     SETOP [6,tag,a,b,c]      op := (a*s+b*v+c) mod 2^32
                     DEF [7,node,a,b,c,x,y]   DAG node over node ids
                     NOISE [8,r1,r2]          distractor
                   Every identity (tags, values, operator parameters,
                   node ids, arrival order, which stream is asked) is
                   redrawn per episode from the seed. Values are 8-bit so
                   that partial strategies have a non-zero exact-match
                   rate without any reward shaping. Knobs: K live
                   streams, D events per stream, interleave, delay,
                   ask_mode (all|one), ask_kind, fanout, expensive
                   pieces, op_mode, topology (streams|dag), noise.
  economics.py     fitness = reward - alpha*ops/1000 - beta*persistent
                   words/64 - gamma*(reads+writes)/100. E0 = (0,0,0);
                   E1 = (0.02, 0.01, 0); E2 = (0.10, 0.01, 0);
                   E3 = (0.01, 0.10, 0). Reward = share of asks answered
                   EXACTLY.
  evolve.py        N=200, elitism 4, tournament 4, children by the
                   Proteus grammar (crossover from a tournament mate),
                   FRESH episodes every generation; held-out seed
                   families for evaluation, held-out K (doubled) and D
                   (doubled); everything derived from one campaign seed;
                   no LLM anywhere.
  controls.py      a 4-instruction constant-0 null; an echo-the-current-
                   tick null; POS_REGS (register solver for W0/W1);
                   POS_TABLE (tag->value table on the tape with linear
                   search, for W2/W3); a tiny assembler used for these
                   only.
  interventions.py ERASE_ALL / ERASE_REGS / ERASE_TAPE / SCRAMBLE_LOC
                   (permute non-code tape) / SCRAMBLE_VAL / SWAP_TWO /
                   HALVE_CAP / RESET_IP / TRANSPLANT (state from another
                   episode), applied once at the tick after the first-
                   asked stream's last PUT.
  survey.py        controls first (abort on failure), 126 jobs over a
                   process pool, one JSON record per job in the
                   directive's section-XX shape (world, organism,
                   hypothesis, experiment, result, interpretation, plus
                   the generation trace and the final elite manifests).
  readout.py       landscape tables, intervention geometry, timing-free
                   results digest, disassembler (for reading, never for
                   classifying).

Committed BEFORE any evolutionary run: DESIGN_v0.1.md (commit cd68cea96)
fixing the grammar, the cell matrix, the regimes, the loop, the controls,
the interventions, five classification predicates and four self-
falsifiers. Annotations v0.1.1 (before runs; after the control battery
only), v0.1.2 and v0.1.3 (after the rows) are appended, dated, and never
edit the original text.

-----------------------------------------------------------------------
2. THE QUESTION AND WHY THE SURVEY SHAPE MATTERS
-----------------------------------------------------------------------

The survey does not ask "can organisms solve these tasks". It asks WHERE
the ecology changes character: which pressure settings produce no
adaptation, trivial recurrence, brute recomputation, specialized memory,
or something structured -- decided by fixed predicates over held-out
reward and the intervention vector, never by looking at a genome and
naming it. The five predicates (design s9):
  NO_ADAPTATION       held-out reward within 0.10 of the gen-0 floor
  TRIVIAL_RECURRENCE  loss >= 0.10 under ERASE_REGS, < 0.05 under
                      ERASE_TAPE (one recurrent state)
  RECOMPUTATION       (shared-intermediate cells) ops grow with consumer
                      fan-out at >= half the recompute cost and erasing
                      state costs < 0.05
  SPECIALIZED_MEMORY  tape erase and location scramble both cost >= 0.10
                      and reward drops >= 0.20 when K doubles
  STRUCTURED          tape erase costs >= 0.10 but location scramble
                      < 0.05 (content survives relocation), or value
                      scramble hurts while relocation does not, with
                      held-out K within 0.10 of training K
  UNRESOLVED          anything else, with the full vector printed

-----------------------------------------------------------------------
3. CONTROLS (run before the survey; the survey aborts if they fail)
-----------------------------------------------------------------------

Campaign seed 20260916, 24 control episodes per cell, 200 random gen-0
organisms as the floor:
  POS_REGS   W0 1.000, W1 (delay 1/4/16) 1.000
  POS_TABLE  W2 (K=2/4/8) 1.000, W3 (K=2/4/8) 1.000
  CONST0     0.000 on all 18 cells
  ECHO_LAST  0.000 on all 18 cells
  floor      mean 0.000-0.007, max 0.000-0.062 (W8) over 200 organisms
Cheat battery (the interventions must SEE the mechanism each control was
written with):
  POS_REGS on W1_d4:   ERASE_REGS 1.000  ERASE_TAPE 0.000  ceiling 1.000
  POS_TABLE on W2_K4:  ERASE_TAPE 0.4375 SCRAMBLE_LOC 0.4375 ERASE_REGS
                       0.000  ceiling 0.4375
The first cheat run FAILED my own >= 0.5 bar on POS_TABLE. Cause: the
intervention fires after the FIRST-ASKED stream's last PUT, so on an
all-asked K=4 world only the streams already stored can be lost; the
attainable drop of a fully state-dependent solver is the share of asks
whose dependencies completed before that tick (0.4375 on that family).
Resolution (annotation v0.1.1, before any evolutionary run): every
intervention vector is reported beside its ERASE CEILING, and the cheat
bar is >= 80 % of that ceiling on the store the control uses and < 0.05
on the store it does not. The timing rule was kept because W4's "work in
progress" needs it. Reviewer: this is a threshold moved after seeing a
control; I claim it is a correction of an arithmetic oversight, not a
gate moved after data, because no evolutionary row existed.

-----------------------------------------------------------------------
4. DESIGN AS EXECUTED
-----------------------------------------------------------------------

Cells (name: knobs):
  W0            K1 D1 delay0                  W6_f1_n8  K1 ASKX fanout1 8 pieces
  W1_d1/d4/d16  K1 D1 delay 1/4/16            W6_f4_n8  K1 ASKX fanout4 8 pieces
  W2_K2/K4/K8   K D1 ask all                  W7_K2     K2 ASK2 (combine op
  W3_K2/K4/K8   K D1 ask one                            revealed at ask time)
  W4_K2_D4_int  K2 D4 random interleave,       W8_K2_D3  K2 D3 ASKO (equal
                asks interleaved                        states, distinct origins)
  W5_K4_D4      K4 D4 random interleave        W9_K2     K2 D2 per-stream op
                                               W10_dag6  3 inputs + 3 DEF nodes
Regimes: E0 and E1 on every cell; E2 and E3 additionally on W4 and both
W6 cells (the compute x storage grid). Seeds 1,2,3. Held-out: 48 episodes
from a family never used in training; 48 at 2K; 48 at 2D; 48 for the
intervention battery; 24 per K in {1,2,4,8,16} for the capacity curve;
24 per fan-out in {1,2,4,8} for W6.
Determinism: the run was launched twice (the first through a harness
with a 10-minute cap, stopped after four rows); the four rows are
identical to the second run's except wall-clock fields. Digest of the
126 timing-free result blocks:
fe1142bf30484f15ff090eb2e55fb8e6f8a69e900019a06fa1b01797dce49257.
(The run's own RUN.json digest included wall-clock fields and is not
reproducible; superseded, recorded.)

-----------------------------------------------------------------------
5. RESULTS -- THE LANDSCAPE (held-out reward per seed; class by the
   property-keyed predicate; REC = trivial recurrence, NONE = none)
-----------------------------------------------------------------------

    cell          E0: held-out s1 s2 s3     class          E1..E3 (all seeds)
    W0            1.000 1.000 0.000         REC REC NONE   0.000  NONE
    W1_d1         1.000 1.000 0.000         REC REC NONE   0.000  NONE
    W1_d4         0.000 0.000 0.000         NONE x3        0.000  NONE
    W1_d16        1.000 0.000 0.000         REC NONE NONE  0.000  NONE
    W2_K2         0.500 0.281 0.010         REC REC NONE   0.000  NONE
    W2_K4         0.255 0.255 0.000         REC REC NONE   0.000  NONE
    W2_K8         0.008 0.005 0.125         NONE NONE UNR  0.000  NONE
    W3_K2         0.562 0.479 0.000         REC REC NONE   0.000  NONE
    W3_K4         0.000 0.271 0.229         NONE REC REC   0.000  NONE
    W3_K8         0.021 0.146 0.042         NONE REC NONE  0.000  NONE
    W4_K2_D4_int  0.000 0.000 0.000         NONE x3        0.000 (E1,E2,E3)
    W5_K4_D4      0.000 0.000 0.000         NONE x3        0.000  NONE
    W6_f1_n8      0.000 0.000 0.000         NONE x3        0.000 (E1,E2,E3)
    W6_f4_n8      0.000 0.000 0.000         NONE x3        0.000 (E1,E2,E3)
    W7_K2         0.177 0.000 0.010         REC NONE NONE  0.000  NONE
    W8_K2_D3      0.375 0.240 0.365         VOID (leak)    0.000  NONE
    W9_K2         0.000 0.000 0.000         NONE x3        0.000  NONE
    W10_dag6      0.000 0.000 0.000         NONE x3        0.000  NONE

Seed agreement: every costed cell (NONE 3/3); W1_d4, W4, W5, W6 x2, W9,
W10 (NONE 3/3); W8 (void 3/3). Every adapted cell DISAGREES across
seeds, so by the design's own rule no non-null class is a CELL property
yet; the disagreement is search variance (section 6D), the mechanism of
every solver found is the same (6B).

Intervention geometry of every elite with held-out >= 0.5 (drop = reward
lost; ceiling = the attainable drop of an erase; K-curve = held-out
reward at K = 1, 2, 4, 8, 16):
    cell       s  held   ceil  ERASE_ALL ERASE_REGS ERASE_TAPE SCR_LOC RESET_IP TRANSPL  K-curve
    W0         1  1.000  1.00  1.000     1.000      0.000      0.000   0.000    1.000    1.00 .25 .05 .03 .00
    W0         2  1.000  1.00  1.000     1.000      0.000      0.000   0.000    1.000    1.00 .50 .25 .12 .07
    W1_d1      1  1.000  1.00  1.000     1.000      0.000      0.000   0.000    0.979    1.00 .25 .14 .08 .03
    W1_d1      2  1.000  1.00  1.000     1.000      0.000      0.000   0.000    1.000    1.00 .52 .25 .12 .06
    W1_d16     1  1.000  1.00  1.000     1.000      0.000      0.000   0.000    1.000    1.00 .50 .25 .14 .07
    W2_K2      1  0.500  0.73  0.500     0.500      0.000      0.000   0.000    0.229    1.00 .50 .26 .13 .07
    W3_K2      1  0.562  1.00  0.521     0.521      0.000      0.000   0.000    0.521    1.00 .50 .42 .17 .00
SCRAMBLE_VAL, SWAP_TWO and HALVE_CAP are 0.000 on all seven. Held-out at
doubled depth (D = 2) is 0.000 for all seven.

-----------------------------------------------------------------------
6. THE FOUR FAILURE SHAPES (how it failed, with the gradient)
-----------------------------------------------------------------------

6A. COST BEFORE CAPABILITY IS EXTINCTION (18/18 cells, 3/3 seeds, E1-E3).
Trace of W0 E1 seed 1 -- share of the population with each persist
policy, and the elite's ops per episode:
    gen 0  none .245  regs .260  tape .210  all .285   elite ops 2
    gen 1  none .515  regs .350  tape .055  all .080   elite ops 5
    gen 3  none .935  regs .065  tape .000  all .000   elite ops 4
    gen 7  none .990  regs .000  tape .000  all .010   elite ops 2
    gen 99 none .985  regs .010  tape .005  all .000   elite ops 2
On a population whose reward is 0, the cost term is the entire fitness
signal; it selects the empty organism and removes every persistence
policy within three generations, before any reward foothold exists. E2
(compute dear) and E3 (storage dear) give the SAME extinction, so the
compute x storage boundary the directive asks for is unmeasurable in
this regime: nothing is alive to trade off. The same cells adapt under
E0. Gradient: the economics must arrive AFTER a foothold (ramped or
generation-gated), or be charged above a free allowance. Whether the
solver SURVIVES E1 when seeded alive (order vs scale) is the first thing
to test, and it is in Theophrastus's stencil.

6B. THE ONLY MECHANISM THAT EVOLVED IS ONE RECURRENT REGISTER.
All seven solving elites: erasing registers costs everything, erasing or
scrambling the tape costs nothing, transplanting another episode's state
costs everything (the state is episode-specific). The tape is never load-
bearing in 126 rows. Three of the solvers carry the manifest label
persist=all (a tape that is allocated, persisted, and unused): the LABEL
said tape, the GEOMETRY said register -- which is why the property-keyed
predicate (annotation v0.1.2) is reported beside the original.
The capacity curve is 1/K: 1.00, 0.50, 0.25, 0.12, 0.06 for five of
seven. That is the score of an organism that answers every ask with the
most recent value it saw. W2_K2 = 0.500, W3_K2 ~ 0.5, W3_K4 ~ 0.25,
W2_K8 = 0.125 are this one organism class read at different K. Doubling
D gives 0.000: the register holds one VALUE, not a fold; the D=1 cells
were solved by echo-with-delay, and the ADD over D values was never
found. The directive predicted this shortcut ("a single recurrent bit
may solve it"); it is now measured, and it has a cheap kill: at K >= 2
never ask the last-put stream first, or ask in reverse put order, so a
last-value organism's plateau falls from 1/K toward 1/K^2.
Two lower-reward elites (W2_K4 s1, W3_K4 s3, both 'all') also lose
0.12-0.25 under RESET_IP, equal to their ERASE_REGS loss: their
instruction pointer is part of the carried state (the VM's YIELD keeps
it). Hypothesis only -- "control position as memory" -- with a cheap
discriminator (RESET_IP vs ERASE_REGS on 96 episodes, three seeds).

6C. W8 IS VOID: THE WORLD LEAKED ITS ANSWER.
W8 (two streams with equal running state but different first and last
values; ASKO by first value expects the last value) scored 0.24-0.375 in
all three seeds with an EMPTY intervention vector: no state mattered. The
seed-1 elite is 5 instructions in 2 registers: it outputs the previous
tick's second word. On the second ASKO of an episode that is the FIRST
ASKO's origin value, and my permutation constraint (perm[0] != base[0],
perm[-1] != base[-1]) leaves perm[-1] == base[0] in two of the three
legal permutations at D=3 -- so the lagged echo is the right answer about
a third of the time. The null battery (constant; echo the CURRENT tick)
could not see a one-tick-lag echo, so the leak passed the control gate.
Recorded as the directive's "the organism exploited leakage" and this
program's "measurement carries its answer". Fix (annotation v0.1.3, for
v0.2): no cross-stream first/last coincidence of any kind; the null
battery gains lagged echoes (previous 1-3 ticks, every word position)
and echo-first; any cell where any null scores >= 0.10 is void before it
runs. W8 v0.1 carries no evidence about provenance.

6D. NOTHING ADAPTS AT DEPTH, CONCURRENCY, COST, OPERATORS OR TOPOLOGY --
AND THE CONTROL CELL IS A NEEDLE.
W1_d4 (0/3; while d1 is 2/3 and d16 is 1/3 -- the delay effect is not
monotone, so seed variance dominates), W4, W5, W6 (both fan-outs, all
four regimes), W9, W10: 0.000 in every seed; the elites are indistin-
guishable from generation 0 (all-zero intervention vectors, ops at the
budget). W6_f1_n8 is the telling one: with fan-out 1 the task is "sum
eight words, add one more" and it was not found in 100 generations, so
the piece mechanism cannot yet test recompute-vs-cache -- the pressure is
unreachable, not absent. Evidence that this is search insufficiency and
not a domain verdict: W0 E0 seed 1 sits at best reward 0.042 (one
episode in 24) from generation 20 to 70, finds the solver at 77, and the
population sweeps to persist=regs (0.965 by generation 90; 0.000 -> 0.610
mean reward); seed 3 never finds it in 100 generations. A world whose
control cell is found in 2 of 3 seeds cannot yet say anything about its
harder cells. Gradient: a search floor must be measured (N x G scan on W0
and W1_d4), and the harder cells should be seeded from the solvers
(transfer branch) rather than from scratch -- which is also the
directive's own question "what transfers, what cannot".

-----------------------------------------------------------------------
7. WHAT THIS DOES AND DOES NOT ESTABLISH
-----------------------------------------------------------------------

Establishes (3 seeds, replayable, intervention-backed):
  - The grammar is well posed and solvable in the VM for W0-W3 (positive
    controls), and the measurement channel sees the mechanism a solver
    uses (cheat battery separates register from tape store).
  - Constant resource costs applied from generation 0 extinguish every
    persistence policy within ~3 generations at these scales.
  - Under no cost, evolution at N=200 x G=100 finds exactly one mechanism
    class (single register recurrence), whose capacity is 1/K and whose
    depth capacity is 1.
  - W8 v0.1 leaks; its rows are void.
Does NOT establish:
  - Anything about tape use, addressing, structured state, caching vs
    recomputation, provenance, operators-as-data or topology generality.
    The survey never gave evolution a foothold from which those could be
    tested, so their absence is uninformative (B2, not B1).
  - That the VM cannot express them (the hand-written table solver
    proves the opposite for W2/W3).
  - That the 1/K plateau is a stable attractor rather than the first
    thing found: the shortcut-kill knob has not been run.
  - Any seed-stable non-null cell class (every adapted cell disagrees
    across seeds).
Claim ceiling: "pressure created; world validated; one adaptation class
observed and intervention-characterised; one world void; the rest
unresolved". Nothing here is a candidate computational primitive.

Defects of my own, recorded not smoothed:
  - The recurrence predicate keyed on the manifest label; corrected by a
    property-keyed class reported BESIDE it (v0.1.2).
  - The ancestry walk self-looped at no-op mutations; every v01 row's
    ancestry_depth reads 10000 (the cap) and is INVALID. Traces, results,
    manifests and lineage ids are unaffected. Fixed for v0.2; rows not
    rewritten.
  - The run's own results digest included wall-clock fields; the timing-
    free digest above supersedes it and the runner now writes that one.
  - The detached launch was first refused by my own fail-closed
    workspace guard (no git on the child's PATH). Correct behaviour;
    relaunched with git on PATH.
  - W4 and W5 collapse into the same condition in this grammar
    (interleaved asks vs end asks differ only in ask timing); recorded.

-----------------------------------------------------------------------
8. DECISION / RECOMMENDATION (the operator's call; Archaeon's lean)
-----------------------------------------------------------------------

Lean: CONTINUE to v0.2, mutating the WORLD along four preregistered axes
before any organism is touched:
  1. Cost ramp: E1 multiplied by min(1, best_reward_so_far/0.5), and a
     seeded-alive arm (falsifies "order vs scale" first).
  2. Transfer branch: the seven solvers as generation 0 of W1_d4, W2_K2,
     W2_K4, W3_K2, W3_K4, W6_f1_n8. Falsifier: no cell exceeds its from-
     scratch seed-max.
  3. Shortcut kill on W2/W3 (reverse ask order). Predicted plateau 1/K^2
     for a last-value organism; if the plateau does not move, 6B is
     misread.
  4. Search floor: W0 and W1_d4 at (N,G) in {200,400} x {100,300}, three
     seeds; the solve fraction is the B1/B2 number.
  Plus: W8 rebuilt without the coincidence; lagged-echo nulls on all 18
  cells before any v0.2 row; RESET_IP vs ERASE_REGS on the two ip-
  carrying elites.
No substrate requirement to the builders is warranted yet: the VM
expresses W0-W3 by construction and the untested question is whether
EVOLUTION reaches the tape, which v0.2 axes 2 and 4 test directly.
"Not worth continuing" would be the right answer if the reviewer holds
that a control cell found in 2/3 seeds at 20,000 evaluations means the
representation (random 32-bit words, opcode = word mod 25) has no usable
gradient for anything past a single register; v0.2 axis 4 is the cheap
way to settle that before more worlds are built.

-----------------------------------------------------------------------
9. QUESTIONS FOR THE REVIEWER (written to resist agreement)
-----------------------------------------------------------------------

Q1. Is the 1/K plateau (6B) a finding about the pressure or an artefact
    of my ask construction (all-asked, put order = ask order shuffled)?
    If you think it is an artefact, say which knob setting would let a
    single-register organism score ABOVE 1/K.
Q2. The cost-extinction result (6A) is at alpha = 0.02 per kilo-op on a
    2-6 op organism, i.e. a cost of ~0.0001 against a reward of 0. Is
    "extinction" the right word for a selection gradient that is tiny
    but the only one, or is this simply drift toward the cheapest
    genotype that any nonzero cost would produce? What experiment
    separates the two? (Theophrastus's alpha sweep is my answer; argue
    it is insufficient.)
Q3. The cheat bar was changed after the control battery and before any
    evolutionary run (section 3). Do you accept that as a correction, or
    should the survey be re-run under the original bar with a different
    intervention timing?
Q4. Given that W0 itself is found in 2 of 3 seeds, is a 126-run survey at
    N=200 x G=100 informative about anything past W1, or should every
    harder cell be marked NOT_EXAMINED rather than NO_ADAPTATION? (I
    report both the floor and the class; say if the class should be
    withheld.)
Q5. W8's leak passed a null battery that was preregistered. What other
    payload-reading nulls should be constitutional for this grammar
    before v0.2 (I have added lagged echoes and echo-first)? Name one I
    have still missed.
Q6. Is "control position as memory" (RESET_IP loss equal to ERASE_REGS
    loss on two elites) worth a discriminator, or is it the trivial
    observation that a YIELDing program with its registers zeroed also
    loses its place?
Q7. Should the program stop here?

-----------------------------------------------------------------------
10. ARTIFACTS (all on branch main of the Prometheus repository)
-----------------------------------------------------------------------

  cd68cea96  DESIGN_v0.1.md preregistered (before any run)
  6d14ec5e6  archaeon/wse/ package + 25 tests; controls PASS
  b7518c392  126 rows, CONTROLS.json, RUN.json, LANDSCAPE.txt/.json,
             READOUT_v01.md, annotations v0.1.2/v0.1.3, code fixes
  0bf8cbfba  Theophrastus hand-off + journal
  Paths: archaeon/wse/DESIGN_v0.1.md; archaeon/wse/READOUT_v01.md;
         archaeon/wse/ledgers/wse-survey-v01/{rows/*.json, CONTROLS.json,
         RUN.json, LANDSCAPE.txt, LANDSCAPE.json, SUMMARY.txt};
         roles/Archaeon/prompts/2026-09-16_workspace_ecology/ (the
         directive, verbatim, with MANIFEST);
         roles/Archaeon/prompts/2026-09-16_wse_theophrastus/ (comms 322);
         roles/Archaeon/journal/2026-09-16_m2-411504ab.md.
  Replay: python -m archaeon.wse.survey --campaign <name> --seed 20260916
          --N 200 --G 100 --E 24 (from a linked worktree with git on
          PATH); python -m archaeon.wse.readout --campaign <name>.
  Built from cb91659ef in Prometheus-worktrees/archaeon-wse-2026-09-16.

+==========================================================================+
|  END OF PACKET. "Not worth continuing" is a first-class answer; if you  |
|  give it, say which of sections 6A-6D you read as the terminal one.     |
+==========================================================================+
