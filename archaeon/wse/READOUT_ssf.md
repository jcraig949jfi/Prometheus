# SSF -- Selective State Formation: readout of cycles 1-3 (2026-09-16)

Archaeon[m2-411504ab]. Directive: roles/Archaeon/prompts/2026-09-16_selective_state/.
Designs: DESIGN_v0.2.md (cycle 1), DESIGN_v0.3.md (cycle 2), DESIGN_v0.4.md
(cycle 3), each committed before its rows. Ledgers: ledgers/ssf-c1/,
ssf-c2/, ssf-c3/ (rows, BOUNDARY_MAP.json, LANDSCAPE.txt, RUN.json).
Evidence states are the directive's; nothing below names a mechanism.

## 0. The one-paragraph result

Three cycles of world mutation on a stream world (tracked and distractor
entities, replace/fold updates, retirement, random ask delays,
interference, held-out tag vocabularies) with a ramped cost on compute,
persistent words and reads/writes. The boundary map -- three hand-written
organisms (log everything / one slot per entity / last value only) scored
under the economics BEFORE any evolution -- exposed both boundaries the
directive asked for: under no cost the logger ties the selective organism
(too little cost); under beta 0.20 the last-value organism wins (too much
cost); under S1 (alpha 0.02, beta 0.05, gamma 0.02) and S3 the selective
organism beats both by >= 0.10 on 7/7 runnable cells. Evolution inside
that region produced NO selective state: de-novo lineages never found a
foothold (0/60 naive rows across cycles 1-2, including 3 rows at zero
cost), and the only lineages that lived were the last-value register
solvers transferred from the v01 survey, which the compute term killed
wherever they burned their tick budget and which otherwise sat at the
last-value plateau (competence ~1/(Kd+1) + chance) with a learning slope
of zero. Cycle 3 separates the two constraints: search floor vs
economics on a live lineage.

## 1. Cycle 1 (v0.2; 36 rows; ramp keyed on best-of-population)

FAILURE SHAPE C1-A -- the ramp trigger was a noise statistic. m_g =
min(1, best_train_reward/0.30) fired at generation 1 on a lucky 2/16
(0.125) from one of 256 organisms; costs at 0.42 against a population
mean of 0.02 extinguished every persistence policy by generation 4-10 in
36/36 rows (A_remember S1 s1: persist=none share 0.238 -> 0.910 by gen
4). This was the preregistered s2 falsifier of DESIGN_v0.2, firing as
written. World mutation: ramp on the population MEAN above chance.
FAILURE SHAPE C1-B -- "forget = expect 0" is a constant-answer hack.
C_forget (retire_rate 0.5, ASK after RETIRE expects 0): the elites in 3/3
seeds are state-free constant emitters scoring 0.58-0.60 = the retire
floor (CONST0 0.59); the whole intervention vector is 0.000. World
mutation: RETIRE recycles the tag on a fold; the ask expects the new fold
only; CONST0 on the new cell sits at 0.00.
Survivors: two A_remember B2_transfer rows kept a register (14-15
persistent words, competence 0.125 / 0.167). Everything else: persist
none, 30-400 ops/episode, competence at the 4-bit chance level.

## 2. Cycle 2 (v0.3; 39 rows; ramp on mean; RETIRE recycles)

FAILURE SHAPE C2-A (W3) -- the trigger works; the compute coefficient is
the killer. B_update S1 B2_transfer s1: m_g = 0 for generations 0-4 while
the transferred register solvers lifted the mean to 0.128; m_g 0.33 at
generation 5; the solvers burn their whole tick budget every tick (elite
13,600 ops/episode at gen 3), so alpha alone cost 0.09 against a reward
edge of ~0.12; cheap do-nothing organisms (2-50 ops) took over by
generation 20, the mean fell to 0.004, m_g returned to 0 and nothing was
left to select. On A_remember the same lineage runs 228-516 ops/episode:
it took over the population (persist=regs share 0.99 by generation
20-40) and SURVIVED m_g up to 0.78 in two of three seeds (competence
0.229 / 0.146 held-out; 0.104 / 0.208 on the held-out vocabulary; ERASE_
REGS = ERASE_ALL = the whole drop; tape never load-bearing). So the same
lineage lives or dies by its ops, i.e. the compute term punishes
wasteful looping before evolution can learn to HALT. The storage term
never decided anything.
FAILURE SHAPE C2-B (W4) -- no de-novo foothold, even at zero cost.
C_forget S0 B1_naive (no cost, 120 generations): NO_ADAPTATION in 3/3;
every naive row of cycles 1-2 (57 rows) is NO_ADAPTATION or an
UNRESOLVED at chance. The stream world (kind dispatch + tag
discrimination + distractors) is a harder needle than v01's W0, which
was itself found in 2/3 seeds. Search, not economics, binds de-novo
lineages on this substrate.
Learning curves: every survivor oscillates between 0.08 and 0.29 on the
24-episode curve family (1/24 resolution) with slope ~0 over 120
generations; competence per 10k episodes 0.003-0.005; no discontinuity
of the kind the directive lists (less experience needed, larger
distractor load tolerated, longer delay without state growth).

## 3. Cycle 3 (v0.4; 18 rows; two arms; 6631 s)

Predictions (DESIGN_v0.4, written before the rows) and how they fared:
  P1  ARM 1 finds a de-novo foothold in >= 1 of 9 rows  -- WON (2/9):
      A_remember S0 s2 held-out 0.188 (persist=all, tape allocated and
      unused, ERASE_REGS = ERASE_ALL = 0.104; a register), first >= 0.15
      on the curve at generation 120 of 200; A_remember S0 s3 0.125.
      B_update 0/3, D_bind2 0/3. So the de-novo route exists on the
      easiest cell at 4x cycle-1's evaluations and finds the same
      last-value register v01 found; it does not exist at this budget on
      bind or update.
  P2  ARM 2 keeps persistence in >= 2 of 3 rows per cell  -- LOST
      (A 1/3, B 1/3, D 0/3). Under S1p the transferred lineage still
      collapses to persist=none in 7/9 rows; where it survives it
      survives at full cost (m_g ~1.0 from generation 25).
  P3  ops/episode falls >= 50 % in at least one cell  -- WON, and by more:
      B_update S1p s3 6,319 -> 122 ops (tick_budget evolved 256 -> 16;
      persist=regs; 15 words), A_remember S1p s2 9,090 -> 203. The
      lineage LEARNED WHEN NOT TO COMPUTE, the cheapest adaptation the
      economics offered; competence held (0.333 / 0.167).
  P4  anything above the last-value plateau  -- NO. B_update s3's 0.333
      is the plateau at Kd=4 (curve over Kd: 1.00 / 0.33 / 0.21 / 0.04 /
      0.17 for Kd = 0/4/8/16/32; K-curve 0.25 / 0.17 / 0.09 / 0.07);
      held-out vocabulary 0.333 (the register carries no tag); delay
      curve flat (0.33 / 0.25 / 0.21 / 0.21). One value, one slot.
Learning-curve slopes over the last three points: -0.008 to +0.027 per
10k episodes; the two rows with +0.027 are A_remember S1p s2 and
B_update S1p s2, the latter at competence 0.000 (noise). Competence per
10k episodes: 0.001-0.004. No discontinuity of the directive's kinds.

Reading: the compute term, once cheap enough not to kill, shaped the one
living lineage toward halting -- an economically driven adaptation that
is real, intervention-backed (ERASE_REGS = ERASE_ALL = 0.31; TRANSPLANT
0.33; RESET_IP 0), replayable, and NOT selective state: it is the same
one-register store with its wasteful loop removed. The storage term
(beta) never shaped anything, because nothing ever held more than one
value. The search floor for de novo lineages is above 256 x 120 and at
or above 512 x 200 on the easiest cell.

## 3b. What the world should become next (not run; the next cycle's prereg)

- The compute term must not be a killer before it is a shaper: charge
  ops above a free allowance (e.g. 4 x the number of ticks) so a
  budget-burning founder is not extinct before HALT can be found; keep
  beta as the term that discriminates one slot from many.
- The search floor is the program's binding constraint, twice measured
  (v01 W0 needle; here 2/9 at 512 x 200 on the easiest cell). Before
  more worlds: a substrate question to Proteus, stated as a requirement,
  never as a mechanism -- "we need generation-0 organisms whose chance
  of dispatching on an input word and copying a later word to a
  persistent location is not ~0, because the economics cannot select
  what the sampler never produces". Whether that is a different word ->
  opcode map, a seeded grammar, or something else is Proteus's call.
- Selective state (more than one slot, keyed by tag) has never been
  reached, so the interference, bind and timescale cells have not been
  TESTED, only run. They stay NOT_EXAMINED for economics.

## 4. What this establishes and does not

Establishes: the boundary map (both boundaries, seven cells, computed);
the ramp-trigger defect and its fix; the constant-answer hack in the
first forget world; the compute term as the operative killer of the one
living lineage; the absence of any de-novo foothold at 256 x 120 on the
stream world; the last-value plateau as the ceiling of the transferred
lineage.
Does NOT establish: anything about selective state, compression,
forgetting or timescale mechanisms in evolved organisms -- none evolved.
"Selectivity pays" is true of the economics (the map) and untested by
evolution because evolution never reached the region where the map
applies. Claim ceiling: pressure created; world validated; economics
mapped; no adaptation beyond one recurrent register; two world hacks
found and closed.

## 5. Guards the directive named, and how each stood

  fixed query timing            random per-tag delay from a set; held
  future-relevance leaks        stateless nulls at chance on every cell;
                                the first-value stateful floor reported
  seed memorisation             fresh episodes every generation; held-out
                                seed families; held-out vocabulary
  world lookup tables           tags redrawn per episode from 2^15 ids
  state hidden in topology      persistent words counted from the
                                manifest; ops counted by the VM
  free storage as computation   the instruction pointer IS carried by
                                YIELD; RESET_IP is in the battery
  size-only fitness             the boundary map's TRIVIAL organism is
                                the smallest and loses under S1/S3
  memory-free tasks             TRIVIAL and the nulls score at chance
  remember-everything optimal   FULL_LOG loses under S1/S3 by >= 0.10
  architecture-similarity       no mechanism named anywhere
