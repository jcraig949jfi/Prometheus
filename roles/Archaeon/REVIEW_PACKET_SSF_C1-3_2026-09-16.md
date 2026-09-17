+==========================================================================+
|  REVIEW PACKET -- SELECTIVE STATE FORMATION, CYCLES 1-3                  |
|  Three world mutations on one stream world under ramped economics        |
|  Author: Archaeon (seat, instance m2-411504ab, machine M2 / SPECTREX5)   |
|  Date: 2026-09-16                                                        |
|  For: the operator (HITL) and external reviewers                        |
|  Status: THREE CYCLES COMPLETE; no selective state evolved; two world    |
|          hacks closed; one economic adaptation (halting) evolved; the    |
|          search floor measured; a substrate requirement drafted          |
|  Self-contained: every load-bearing number is inline; no repo access     |
|  is needed to critique this packet.                                      |
+==========================================================================+

-----------------------------------------------------------------------
0. MANDATE AND VERDICT
-----------------------------------------------------------------------

Mandate (operator, 2026-09-16, verbatim on file): build and iterate a
world whose economics make selective state formation advantageous and
eventually necessary; never implement or reward a known architecture;
expose both boundaries (too much memory, too much forgetting); track
learning curves, cost and transfer; ablate before naming; do not stop
to ask. The same organism substrate as the morning's survey (a 25-opcode
register+tape VM with an evolvable persistence policy, unmodified).

Verdict, in the directive's own terms:
  - The boundary map exists and exposes both boundaries on 7 of 8 cells,
    computed before evolution with three hand-written organisms.
  - Inside the region where selectivity pays, evolution produced ONE
    economically driven adaptation: a transferred one-register lineage
    evolved its tick budget from 256 to 16 and its cost from ~6,300 to
    ~120 ops per episode while holding competence (it learned when not
    to compute). Intervention-backed, replayable, and not selective
    state.
  - No lineage ever held more than one value. Selective state,
    compression, forgetting and interference mechanisms were never
    reached, so the cells built for them were RUN, not TESTED.
  - Two world hacks found and closed (a noise-triggered cost ramp; a
    constant-answer forget world). One instrument defect in my own
    control set found and closed (the selective control could not fold).
  - The binding constraint is search: de-novo footholds 0/60 at 256 x
    120, 2/9 at 512 x 200 on the easiest cell.

Lean: STOP mutating the world and file one substrate requirement
(section 8) before another cycle; the economics have nothing to shape
until the sampler produces organisms that can be shaped.

-----------------------------------------------------------------------
1. THE WORLD (one grammar; each cycle changed one or two things)
-----------------------------------------------------------------------

An episode is a stream of one event per tick. K TRACKED entities (each
asked once) and Kd DISTRACTOR entities (never asked) receive D PUT events
[1, tag, v] in random interleaving; the tracked tag's ASK [2, tag]
arrives a random delay after its last event (delay drawn per tag per
episode from a set, so query timing is never fixed); RETIRE [9, tag]
marks an entity as finished. Values are 4-bit (chance 1/16). Tags are
drawn per episode from 2^15 ids; a held-out family uses a disjoint
range. Cells:
  A_remember   K1 D1 Kd8 delays {4,16,64}   (remember + distract + timescale)
  B_update     K1 D4 Kd4 delays {4,16}      (update: keep the LAST value)
  C_forget     K1 D2 Kd4 retire 0.5         (forget; cycle 1: expect 0 after
                                             RETIRE; cycles 2-3: the tag is
                                             recycled on a fold)
  D_bind2 / E_bind4   K2 / K4, D2, Kd8      (bind + distract)
  F_compose    K2 D2 fold, ASK2             (NOT EXAMINED: no positive control)
  G_interfere  K2 D2 Kd8, distractor tags share 12 of 16 bits with tracked
  H_timescale  K2 D1 Kd8 delays {4,64}
Economics: fitness = reward - m_g x (alpha x ops/1000 + beta x
persistent_words/64 + gamma x (reads+writes)/100).
  S1  (0.02, 0.05, 0.02)   S2 (0.02, 0.20, 0.02)   S3 (0.10, 0.05, 0.02)
  S1p (0.002, 0.05, 0.02)  S0 = no cost
m_g is a RAMP: cycle 1 = min(1, best_train_reward/0.30); cycles 2-3 =
clip((population mean reward - chance)/0.20, 0, 1).
Selection: N organisms, elitism 4, tournament 4, children by the
existing 12-operator grammar (incl. crossover and manifest-limit steps),
fresh episodes every generation; held-out seed families for every
measurement; every organism's held-out competence sampled every 10
generations against cumulative experience (learning curve). No LLM.

-----------------------------------------------------------------------
2. THE BOUNDARY MAP (critical control; computed before any evolution)
-----------------------------------------------------------------------

Three hand-written organisms on 32 control episodes per cell:
  FULL_LOG   appends every (tag, value) it sees; on ASK scans the log
             backwards for the tag. 2062 persistent words.
  SELECTIVE  one (tag, last value) slot per entity; PUT overwrites,
             RETIRE zeroes. 526 words (of which ~230 are its own code:
             the VM counts the whole tape, so this footprint is
             pessimistic). A fold variant for the recycled forget cell.
  TRIVIAL    the last value seen, in a register. 8 words.
Reward on cycle-1 cells (A/B/C/D/E/G/H): FULL_LOG 1.000, SELECTIVE 1.000
(0.859 before its tape was widened -- a defect of mine, fixed before any
run), TRIVIAL 0.125-0.312. Ops per episode: FULL_LOG 374-1052,
SELECTIVE 569-2030, TRIVIAL 159-514.
Fitness winner by regime (7 cells, identical pattern):
  S0   FULL_LOG ties SELECTIVE          -> too little cost
  S1   SELECTIVE by >= 0.10 over both   -> selectivity pays
  S2   TRIVIAL                          -> too much cost (beta 0.20 x 526/64)
  S3   SELECTIVE by >= 0.10 over both   -> selectivity pays
Stateless nulls (constant 0; echo of any word of the current tick) sit
at chance (0.00-0.16 against 0.0625 + 0.10) on every cell; stateful
shortcut floors (echo of the previous 1-3 ticks; the episode's first
word) are reported, not voids (0.06-0.22). Only S1 and S3 pairs (and S1p
in cycle 3) were allowed to evolve.

-----------------------------------------------------------------------
3. CYCLE 1 (v0.2): 36 rows, N=256 G=120 E=16, 601 s
-----------------------------------------------------------------------

FAILURE SHAPE C1-A -- the ramp trigger was a noise statistic. With 256
organisms scored on 16 asks at chance 1/16, one organism scores 2/16 in
generation 0 by luck; m_g = min(1, 0.125/0.30) = 0.42 at generation 1
while the population mean is 0.02; the cost gradient is the only
gradient and it selects the empty organism. Persist=none share on
A_remember S1 s1: 0.238 (gen 0) -> 0.723 (gen 3) -> 0.910 (gen 4) ->
0.996 (gen 10). 36/36 rows. This was the s2 falsifier of the
preregistration, firing as written.
FAILURE SHAPE C1-B -- "forget = expect 0" is a constant-answer hack.
C_forget's elites in 3/3 seeds: no persistent state, ~37 ops, competence
0.583-0.604 = the retire floor (CONST0 0.59); intervention vector all
0.000. The world offered a constant that answers half its asks.
Survivors: two A_remember transfer rows (14-15 persistent words,
0.125 / 0.167 = the last-value register from the morning's survey).
World mutations for cycle 2: ramp on the population MEAN above chance;
RETIRE recycles the tag on a fold (the ask expects the NEW fold only;
CONST0 on the new cell: 0.00).

-----------------------------------------------------------------------
4. CYCLE 2 (v0.3): 39 rows, N=256 G=120 E=16, 1063 s
-----------------------------------------------------------------------

FAILURE SHAPE C2-A -- the trigger works; the compute coefficient kills.
B_update S1 transfer s1: m_g = 0 for generations 0-4 while the
transferred register solvers lift the mean to 0.128; m_g 0.33 at
generation 5. Those solvers burn their whole tick budget every tick
(elite 13,600 ops/episode at gen 3), so alpha alone costs 0.02 x 13.6 x
0.33 = 0.09 against a reward edge of ~0.12. Do-nothing organisms (2-50
ops) take over by generation 20; the mean falls to 0.004; m_g returns to
0; nothing is left to select. On A_remember the SAME lineage runs
228-516 ops/episode, takes over the population (persist=regs share 0.99
by generation 20-40) and survives m_g up to 0.78 in 2 of 3 seeds
(held-out 0.229 / 0.146; held-out vocabulary 0.104 / 0.208; ERASE_REGS
= ERASE_ALL = the whole drop; tape never load-bearing). The lineage
lives or dies by its ops; the storage term decided nothing.
FAILURE SHAPE C2-B -- no de-novo foothold even at zero cost. C_forget S0
naive (no cost, 120 generations): NO_ADAPTATION 3/3; every naive row of
cycles 1-2 (57) at chance.
Learning curves of the survivors oscillate 0.08-0.29 (24-episode
resolution) with slope ~0 over 120 generations.
World mutation for cycle 3: separate search from economics.

-----------------------------------------------------------------------
5. CYCLE 3 (v0.4): 18 rows, two arms on A/B/D, 6631 s
-----------------------------------------------------------------------

Predictions were committed before the rows (DESIGN_v0.4).
  ARM 1  search floor: naive, no cost, N=512 G=200.
         Prediction "foothold in >= 1 of 9": WON, 2/9, both on the
         easiest cell (A_remember s2 0.188, first >= 0.15 at generation
         120; s3 0.125), both one-register last-value (ERASE_REGS =
         ERASE_ALL = 0.104). B_update 0/3, D_bind2 0/3.
  ARM 2  transferred lineage under S1p (alpha 0.002), N=256 G=200.
         Prediction "persistence survives in >= 2 of 3 rows per cell":
         LOST (A 1/3, B 1/3, D 0/3).
         Prediction "ops fall >= 50 % in at least one cell": WON, by
         98 %: B_update s3 6,319 -> 122 ops/episode, tick_budget evolved
         256 -> 16, persist=regs, 15 words, held-out 0.333, held-out
         vocabulary 0.333, m_g ~1.0 from generation 25 (full cost paid
         and survived). A_remember s2 9,090 -> 203 ops, 0.167.
         Prediction "anything above the last-value plateau": NO. The
         0.333 IS the plateau at Kd=4: curve over Kd 1.00 / 0.33 / 0.21 /
         0.04 / 0.17 (Kd = 0/4/8/16/32); K-curve 0.25 / 0.17 / 0.09 /
         0.07; delay curve 0.33 / 0.25 / 0.21 / 0.21. One value, no tag.
Learning slopes over the last three curve points: -0.008 to +0.027 per
10k episodes; competence per 10k episodes 0.001-0.004; no
discontinuity of the directive's listed kinds anywhere.

-----------------------------------------------------------------------
6. THE ADAPTATION THAT DID EVOLVE, STATED THE WAY THE DIRECTIVE ASKS
-----------------------------------------------------------------------

Under pressure combination {update x distract x cheap compute x dear
storage, ramped after a mean foothold}, the transferred lineage on the
update cell evolved a 98 % reduction in ops per episode by lowering its
tick budget (a manifest field the grammar steps) and halting, while
holding one persistent register. Erasing registers destroys its
competence (drop 0.31 of 0.33); erasing the tape, scrambling locations
or values, halving capacity and resetting the instruction pointer do
nothing (0.000); transplanting another episode's state destroys it
(0.33). The effect transfers unchanged to the unseen tag vocabulary
(0.333) because the register carries no tag. It does NOT transfer to
more distractors (0.04 at Kd=16) or more entities (0.09 at K=4). This is
"learning when not to compute", not "learning what deserves to become
state". It is harvestable only as a negative: the economics can shape
cost before they can shape selectivity, and did.

-----------------------------------------------------------------------
7. WHAT THIS DOES AND DOES NOT ESTABLISH; DEFECTS
-----------------------------------------------------------------------

Establishes (replayable; timing-free digests in each RUN/LANDSCAPE):
  - both economic boundaries on 7 cells, by construction, before
    evolution;
  - a best-of-population ramp trigger is a noise statistic at these
    sizes; a mean-above-chance trigger is not;
  - the compute coefficient at 0.02/kop extinguishes any founder that
    burns its budget before halting can evolve; at 0.002 the same
    founder survives and halts;
  - the de-novo search floor on the stream world is above 256 x 120 and
    around 512 x 200 on the easiest cell; bind and update cells have no
    de-novo route at 512 x 200;
  - no evolved organism in 93 SSF rows (or 126 survey rows) holds more
    than one value in persistent state.
Does NOT establish: anything about selective state, interference,
timescale or forgetting mechanisms in evolved organisms; whether the
storage coefficient would discriminate one slot from many (nothing had
many); whether the last-value plateau is stable under a shortcut-kill
ask order (not run here).
Defects of mine, recorded: the cycle-1 ramp (prereg falsifier fired);
the forget world's constant answer (nulls did not include it because
CONST0 was exempted on retire cells -- I exempted the very null that
caught it, then read it by hand); SELECTIVE's slot table overflow at 256
words (fixed before any run); the selective control could not fold
(cycle-2 map first voided the forget cell; fixed with a fold variant);
FULL_LOG does not fold, so the forget cell's "FULL_LOG loses" is not a
fair comparison; W4 and W5 of the morning's survey collapse into one
condition in this grammar; the launch-time line in my journal was wrong
by 40 minutes and is annotated.

-----------------------------------------------------------------------
8. DECISION / RECOMMENDATION (operator's call; Archaeon's lean)
-----------------------------------------------------------------------

Lean: do not run a fourth world mutation yet. Two things first.
  1. Economics: charge ops above a free allowance tied to episode
     length (e.g. 4 ops per tick) so compute shapes rather than kills;
     keep beta as the discriminating term; keep the mean-keyed ramp.
  2. Substrate requirement to Proteus, stated as a requirement and not
     a mechanism: "we need generation-0 organisms for which the joint
     event {read an input word; branch on it; copy a later word to a
     location that persists} has non-negligible probability, because the
     economics cannot select what the sampler never produces." How
     (word-to-opcode map, seeded grammar, anything else) is Proteus's.
     Evidence: 0/60 de-novo footholds at 256 x 120; 2/9 at 512 x 200 on
     the easiest cell; the morning's W0 needle (2/3 seeds at 200 x 100).
"Not worth continuing" is defensible if the reviewer holds that a
substrate whose sampler cannot reach a two-instruction store-and-recall
in 60,000 evaluations is not the substrate for this question; my answer
is that the requirement in (2) is exactly the falsifiable form of that
objection, and it is cheap to test.

-----------------------------------------------------------------------
9. QUESTIONS FOR THE REVIEWER (written to resist agreement)
-----------------------------------------------------------------------

Q1. The boundary map uses hand-written organisms whose footprint is
    dominated by code (SELECTIVE 526 words, ~230 of them program). Is
    the "selectivity pays" region an artefact of my control organisms'
    verbosity rather than of the economics? What would a fair minimal
    selective organism cost?
Q2. The 98 % ops reduction is real and intervention-backed. Is it an
    adaptation in the directive's sense (a mechanism), or merely the
    removal of a wasteful loop a hand-written founder would never have
    had? Say what would distinguish the two.
Q3. I exempted CONST0 on retire cells and thereby exempted the null that
    would have caught the constant-answer hack. What rule should replace
    "exempt the floor on cells where it is structural"?
Q4. Is "search floor" the right reading of 0/60 and 2/9, or is it that
    the 4-bit exact-match reward has no gradient at all and any success
    is a lottery? What experiment separates gradient-free from
    rare-but-climbable?
Q5. Should the substrate requirement (section 8.2) go to Proteus now, or
    is a shortcut-kill ask order plus a free-allowance compute cost worth
    one more cycle first?
Q6. Stop here?

-----------------------------------------------------------------------
10. ARTIFACTS (branch main of the Prometheus repository)
-----------------------------------------------------------------------

  21bd43cc8  the directive, verbatim, with MANIFEST
  6d98c190e  DESIGN_v0.2 (cycle 1 prereg)     1c0e39ccf  v0.2 code + map
  806907ab8  cycle 1 rows (ledgers/ssf-c1)
  6e6adda60  DESIGN_v0.3 (cycle 2 prereg)     f6e18b5c7  v0.3 code + map
  190ab0756  cycle 2 rows (ledgers/ssf-c2)
  876f53acc  DESIGN_v0.4 (cycle 3 prereg)     cc9565185  v0.4 code
  204b031c4  cycle 3 rows (ledgers/ssf-c3)
  archaeon/wse/READOUT_ssf.md (the readout by failure shape);
  archaeon/wse/{worlds,economics,evolve,controls,interventions,ssf,
  ssf_readout,readout}.py; tests archaeon/tests/test_wse.py (25).
  Replay: python -m archaeon.wse.ssf --campaign <name> --seed <s>
  [--cycle3]; python -m archaeon.wse.ssf_readout --campaign <name>.
  Timing-free digests: c1 237d9b93..., c2 (in RUN.json), c3 7d8ec619...
  Built from cb91659ef in Prometheus-worktrees/archaeon-wse-2026-09-16.

+==========================================================================+
|  END OF PACKET. "Not worth continuing" is a first-class answer; if you  |
|  give it, say whether it is the world, the economics or the substrate.  |
+==========================================================================+
