+=====================================================================+
|  WORKSPACE / SERENDIPITY ECOLOGY (WSE)                              |
|  ARCHITECTURE + THREE CAMPAIGNS OF INSTRUMENT WORK                  |
|  An external review packet, written before any decision to scale up |
|                                                                     |
|  Author: Archaeon (autonomous seat m2-411504ab, machine M2)         |
|  Date:   2026-09-17                                                 |
|  For:    HITL (James) + external reviewers with no repo access      |
|  Status: OPEN QUESTION -- should this be scaled, redesigned, or     |
|          stopped? The packet is written so that "stop" is reachable.|
|                                                                     |
|  Self-contained: every load-bearing number is inline. Nothing here  |
|  requires reading code, logs or prior packets.                      |
+=====================================================================+

CONTENTS

  1.  What the system is trying to do
  2.  The architecture, bottom to top
  3.  What a single experiment costs and produces
  4.  The instrument stack built to keep the answers honest
  5.  Campaign 1 and 2 in one page each (why campaign 3 looked like it did)
  6.  Campaign 3: ten discriminating experiments
  7.  The five findings that would survive an adversarial read
  8.  Everything campaign 3 killed
  9.  What this does NOT establish
  10. The scaling question, stated as a decision
  11. Questions for the reviewer, written to resist agreement
  12. Artifacts, commits, and how to attack this

-----------------------------------------------------------------------
1. WHAT THE SYSTEM IS TRYING TO DO
-----------------------------------------------------------------------

The programme's thesis is that capability should be DISCOVERED by a
population under ecological pressure, not written down by a designer and
not distilled from a language model. No language model is in any loop
described here. Nothing in the substrate names a cognitive function.

WSE is the test bed for one specific question: under what ecological
conditions does a population of tiny programs acquire something that
looks like WORKING MEMORY -- holding a value across interference and
producing it on demand -- and can the conditions that produce it be
measured rather than asserted?

The deliberate design commitment, and the thing most worth attacking: the
world emits integers and expects integers. It never names a register, a
store, a memory or a strategy. If "memory" appears, it has to appear as
behaviour under a readout that could equally have scored something else.

-----------------------------------------------------------------------
2. THE ARCHITECTURE, BOTTOM TO TOP
-----------------------------------------------------------------------

2.1 THE ORGANISM (Proteus player VM)

An organism is a MANIFEST, which is data, content-addressed by hash:

  genome        a list of 32-bit words, length a multiple of 4,
                bounded [4, 4096] words
  n_regs        registers, bounded [2, 16]
  tape_words    bounded [16, 4096], multiple of 4
  tick_budget   bounded [8, 65536]
  out_cap       output words per tick, bounded [1, 256]
  persist       one of none | regs | tape | all  (what survives a tick)
  code_writable whether stores may overwrite the genome region

Execution: the genome is copied to the front of the tape and run IN
PLACE, so a program and its data share one address space and a
self-modifying organism is possible but not privileged. An instruction is
four consecutive words (op, a, b, c). The opcode word is taken MODULO the
opcode count, so every word sequence is a legal program and mutation can
never produce an illegal instruction. That single decision is what makes
the search space navigable at all.

The affordance table is 25 opcodes in 9 categories, published and hashed:

  halt_yield    NOP HALT YIELD
  read_write    LDC MOV
  indirection   LD ST                (tape addressed by register contents)
  arithmetic    ADD SUB MUL
  logical       AND OR XOR NOT SHL SHR
  comparison    EQ LT
  control       JMP JZ JNZ
  opaque_io     IN INQ OUT           (channels are integer-indexed)
  randomness    RND

There is no memory opcode, no store-value opcode and no cost opcode. LD
and ST address a bounded tape by register content; whether that becomes
memory is the experimental question, not a given.

2.2 THE MUTATION GRAMMAR

Twelve operators with FROZEN masses, hashed as part of the runtime
identity (grammar v0.4). Masses, exactly as the code renormalises them:

  operand_perturbation  0.1979    replacement           0.1250
  deletion              0.1146    insertion             0.0833
  movement              0.0833    reference_redirection 0.0833
  config_perturbation   0.0833    region_swap           0.0625
  splice                0.0521    duplication           0.0417
  randomization         0.0417    unreachable_removal   0.0312

Deletion mass deliberately exceeds insertion mass so growth is not the
default direction. A thirteenth operator (zeroing) was removed in an
earlier version and the remaining twelve were renormalised MECHANICALLY
in code, so the change is auditable rather than transcribed. Operators
manipulate representation only; none of them "adds a capability".

2.3 THE WORLD

A WORLD is a point in a knob space, not a hand-written task. An EPISODE
is a list of ticks; each tick is the list of words the organism reads on
input channel 0. Some ticks carry an expected answer: the first word the
organism writes on output channel 0 that tick. The event grammar:

  PUT   [1, tag, v]        stream `tag` updates its state with v
  ASK   [2, tag]           expect the current state of `tag`
  ASKX  [3, tag, y, ...]   expect state combined with a fresh operand
  ASK2  [4, tagA, tagB, c] expect a combination of TWO streams' states
  ASKO  [5, v0]            expect the last value of the stream whose
                           FIRST value was v0
  SETOP [6, tag, a, b, c]  redefine the stream's update rule
  DEF   [7, node, ...]     a dataflow node (graph topology worlds)
  NOISE [8, r, r]          never referenced

Knobs include: K (streams live at once), D (events per stream), delay
(noise ticks between the last PUT and the asks), ask_mode (all | one),
ask_kind, value_bits, interleaving, distractor streams, retirement,
noise rate, and a train/held-out TAG VOCABULARY SPLIT so no held-out
episode reuses a training identity. Every identity -- tags, values,
operator parameters, arrival order, which stream is asked -- is drawn
fresh per episode from a seed.

Cells used in this packet:
  W0       K=1, delay 0.  The simplest: one stream, ask at the end.
  W1_dN    K=1, delay N.  Interference before the ask.
  W2_K2    K=2, ask BOTH streams. The two-value cell.
  W3_K2    K=2, ask ONE of the two.
  W7_K2    K=2, ASK2: combine two streams' states.

With 4-bit values, chance is 1/16 = 0.0625.

2.4 THE POPULATION LOOP

  N = 200 organisms, E = 16 episodes per generation battery,
  elitism 4, tournament size 4, one mutation per child by default.

Generation 0 is drawn from a FOUNDRY (a named sampling distribution,
part of the run key). Fitness is a declared cost VECTOR, never an
expected mechanism:

  fitness = reward - alpha*ops/1000 - beta*persistent_words/64
                   - gamma*(io per episode)/100

Regime E0 sets every cost to zero (reward alone); other regimes price
computation, storage and I/O. Reward is the fraction of ask events
answered EXACTLY.

Common random numbers are the default: two arms of the same experiment
see the same generation 0 and the same episode batteries, so a
difference between arms is a difference in treatment.

2.5 THE ENGINE (Serendipity Foundry)

A separate service, maintained by a different seat, that holds the
experimental record: worlds with isolation policies, artifacts with
content hashes, experiments, observations, failures. It is not a compute
service; it is the thing that makes a claim CITABLE. It enforces rules
the experimenter would otherwise be trusted to follow:

  - an artifact that can seed a population must carry a MATURITY block
    (did the source solve its own cell?), or publication is refused;
  - an ISOLATED world cannot import from another world -- or from
    itself (a real 403 we hit and worked with, not around);
  - every post carries an idempotency key, so a resumed attempt cannot
    silently double-record.

Pinned instance for this work: eng_906356f7fb1da180131f9290, schema 8,
pinned 2026-09-16 by the engine's owner seat.

-----------------------------------------------------------------------
3. WHAT A SINGLE EXPERIMENT COSTS AND PRODUCES
-----------------------------------------------------------------------

Concretely, from campaign 3's own receipts (12-core box, one machine):

  smallest slot    24 genome x seed probes            39 s
  typical slot     60 runs x 100 generations at N=200 680-920 s
  largest slot     228 runs x 60 generations           1512 s
  whole campaign   ten slots, attempts of record       ~6.1 h compute

Each experiment produces, mechanically:

  PREREG.json/.md   a SEALED preregistration (15 fields, digest checked
                    at close; changing it after sealing is an error the
                    machine records)
  attempts/aNN/     one directory per attempt, receipt written after
                    EVERY step, never renamed
  rows.json         one row per run, all telemetry
  RECEIPT.json      worlds, artifacts, records, timings, typed states
  RECORD.md         regenerated from the above plus a written addendum;
                    the generated sections are never hand-edited
  ledger entries    defects, landscape facts, machinery moves
  table rows        appended to the persistent reachability and
                    corridor tables

The preregistration fields include, besides the question: WHY THIS SLOT
IS STILL WORTH SPENDING, ASSAY CAPABILITY REQUIREMENT, POSITIVE CONTROL,
CLAIM CEILING, KILL CONDITION, TYPED FAILURE CONDITIONS and REPLACEMENT
CONDITION. The last one matters: an experiment must say in advance what
would make it not worth running.

-----------------------------------------------------------------------
4. THE INSTRUMENT STACK BUILT TO KEEP THE ANSWERS HONEST
-----------------------------------------------------------------------

This is the part that took most of three campaigns, and it is the part
most relevant to a scaling decision.

4.1 THE REACHABILITY TABLE (1,265 rows, append-only)

One row per run: cell, value bits, N, G, E, regime, generation-0
foundry, plus run identity so common random numbers cannot double-count
the same run. It answers "is this cell reachable at this budget?"
BEFORE an experiment is designed on it. Classes are Wilson-banded:
COMMON, REACHABLE, RARE, OBSERVED_UNREACHABLE_AT_BUDGET, UNESTABLISHED.

Three levels of reach, added in campaign 3:

  FLOOR   best training reward < 0.45
  SHELF   0.45 <= best < 0.90        (on a two-stream cell: half credit)
  SUMMIT  best >= 0.90 AND confirmed on 48 held-out episodes

The held-out confirmation exists because a training-only 0.9375 was
found to read 0.53 on held-out episodes: a lucky 16-episode battery. A
summit that is not confirmed is recorded as a CANDIDATE, not a summit.

Runs stopped early on success are right-censored rather than pooled
naively, and budget lookups pool monotonically.

4.2 THE CORRIDOR TABLE (155 rows)

A second instrument beside reachability, answering a different question:
given a MATURE solution of cell A, what does it already contain on cell
B (direct reuse, no search), and what does a search on B reach when
seeded with it? Edge kinds: direct, init, ladder. Mature sources only:
if a source never solved its own cell, the row records why it is not
admissible.

4.3 TYPED STATES AND A DISPOSITION LADDER

Before any result is read, the machine computes which declared
preconditions FAILED, from measurements:

  ENGINE_FAILURE, INSTRUMENT_FAILURE, INTERVENTION_NOT_APPLIED,
  RESIDUE_BELOW_FLOOR, IMMATURE_ARTIFACT, STREAM_BELOW_THRESHOLD,
  TARGET_UNREACHABLE, READOUT_CANNOT_EXPRESS, POSITIVE_CONTROL_FAILED,
  UNDERPOWERED

and then a disposition candidate:

  INCONCLUSIVE < CAPABLE_NEGATIVE < WEAK_POSITIVE < SUPPORTED_POSITIVE

SUPPORTED_POSITIVE requires n >= 10 AND every declared falsification
attack to have been run and survived. Across three campaigns, nothing
has ever reached it. The agent writing the record may argue with the
machine's candidate but must quote it; in campaign 3 the agent's
disposition was STRICTER than the machine's once, and never looser.

4.4 ATTEMPTS, RESUMES AND RECEIPTS

Every run of a harness is a numbered attempt with its own sealed
preregistration and receipt. Steps are keyed by a hash of (experiment,
preregistration digest, step name, parts), so a resumed attempt replays
only steps belonging to the same design. This was added after a resume
replayed a DIFFERENT design's engine steps in campaign 2.

4.5 WHAT THE INSTRUMENT STACK HAS CAUGHT

Not hypothetical. Each of these changed a result:

  - a reachability table pooling two different generation-0 foundries;
  - the same run counted twice under common random numbers;
  - a resume replaying another design's steps;
  - dry-run rows entering a persistent table;
  - a training-only summit that held-out at 0.53;
  - a fixed curriculum rung releasing a ladder before the population had
    climbed it (7 of 12 seeds);
  - a search threshold reached by 9 of 390,625 genotypes, censoring 44
    of 48 rows;
  - a rank correlation pooled over two strata of different difficulty,
    which produced a textbook-looking replication that was a two-point
    correlation;
  - a falsification attack coded with an absolute floor, so it passed
    exactly when it should have failed;
  - a shared disposition routine that crashed on rows lacking the
    primary metric, where the tempting fix (treat missing as zero) would
    have inflated the treatment effect.

-----------------------------------------------------------------------
5. CAMPAIGN 1 AND 2 IN ONE PAGE EACH
-----------------------------------------------------------------------

CAMPAIGN 1 (ten slots, n=3 per arm). Five weak positives, two capable
negatives, three assays that could not pose their question at all. All
three incapable assays had the SAME cause: a cell chosen from prior 0/3
rows with no pooled reachability estimate. That is what the reachability
table was built to prevent. Four instrument failures were found and
fixed inside their timebox; none became a disposition.

CAMPAIGN 2 (ten slots, n=6 to 52). Seven capable negatives, three weak
positives, zero supported positives, zero engine errors across 13 live
attempts. Two of campaign 1's five weak positives were taken to n >= 10
and DIED (residue components +0.009 at n=12; failed-genotype transfer
+0.002 at n=10). The headline landscape facts campaign 3 inherited:

  - on the two-stream cell, populations reliably reach a HALF-CREDIT
    SHELF and stop there;
  - a delay curriculum with a revisit share removes a forgetting cliff;
  - a basin-share geometry statistic correlated with search efficiency
    (rho -0.59) in one evaluator family;
  - substituted material TAKES OVER the population even when the
    treatment being tested is harmful.

That last one was logged as a recurring defect twice, and is what
campaign 3 turned into an experiment.

-----------------------------------------------------------------------
6. CAMPAIGN 3: TEN DISCRIMINATING EXPERIMENTS
-----------------------------------------------------------------------

The instruction was: DO NOT IMPROVE THE STORY, IMPROVE THE MACHINE, and
DO NOT PRESERVE AN EXPERIMENTAL LINE MERELY BECAUSE IT HAS A NUMBER.
Four lines were retired before the campaign began; a fifth was replaced
mid-campaign when its parent evidence voided its outcome variable.

 slot  question                              n    disposition
 ----  ------------------------------------  ---  -----------------
 01    shelf-to-summit budget scan (G300)    24   CAPABLE_NEGATIVE
 02    anatomy of the shelf                  18   CAPABLE_NEGATIVE
 03    delay corridor ladder, powered        12   WEAK_POSITIVE
 04    corridor map, mature sources only     66   WEAK_POSITIVE
 05    retention economics break-even        60   CAPABLE_NEGATIVE
 06    basin share out of family             48   INCONCLUSIVE
 07    basin geometry as a causal target     60   CAPABLE_NEGATIVE
 08    (replacement) partial-credit removal  24   CAPABLE_NEGATIVE
 09    CA mechanism, not usefulness          24   CAPABLE_NEGATIVE
 10    import dose ecology                   228  CAPABLE_NEGATIVE

  10 of 10 attempted. 0 engine errors on attempts of record. 0 retired
  lines reopened. 2 slots failed their own positive control on first
  execution, were repaired at the machine level, re-preregistered and
  re-run. 41 ledger entries. 1 resume replaying 29 verified steps.

-----------------------------------------------------------------------
7. THE FIVE FINDINGS THAT WOULD SURVIVE AN ADVERSARIAL READ
-----------------------------------------------------------------------

7.1 THE TWO-STREAM CELL HAS A CEILING, AND IT IS NOT BUDGET OR REWARD

Zero confirmed summits in 60 runs, across three independent attacks:

  fresh search, 300 generations, n=12             0 summits, 0 candidates
  seeded with preserved shelf organisms, n=12     0 summits
  all-or-nothing payoff, 300 generations, n=12    0 summits
  corridor map, 3 two-stream cells, 54 runs       0 summits

Best training excursion ever observed: 0.875 (28 of 32 asks), which read
0.60 on held-out episodes. The table now classes this summit
OBSERVED_UNREACHABLE_AT_BUDGET at every ladder point through 300
generations (95% upper band 0.22 at n=14 baseline runs).

7.2 THE SHELF IS A ONE-VALUE MEMORY, AND PARTIAL CREDIT BUILDS IT

Direct measurement, 12 shelf elites, 400 grammar children each:

  improving children                    1 in 4,800
  neutral / destructive                 0.64 / 0.36
  second-stream gains                   58
  gains that KEEP the first stream      0 of 58
  greedy 3-step paths reaching 0.90     0 of 480
  strategy: answer every ask with the first PUT value  6 of 12
            answer every ask with the last PUT value   4 of 12

The organism remembers ONE value and answers with it, which is correct
about half the time because half the asks concern that stream. Every
edit that raises the other stream's credit does so by switching WHICH
value is remembered.

The causal half: selecting on COMPLETE EPISODES instead of per-ask
credit cut shelf arrivals from 11/12 to 8/12, doubled time below the
shelf, and produced a different organism -- five runs whose held-out
episode credit EQUALS their per-ask credit (0.438-0.646), i.e. they
answer both asks or neither. That is the right kind of creature, at the
wrong reliability, and still no summit. The payoff selects the plateau
and the creature; it does not set the ceiling.

7.3 THE DELAY LADDER BUILDS INVARIANCE, NOT A SOLVER

A curriculum over delays 0 -> 1 -> 2 -> 4, with rung 0 held until the
population actually climbs it:

  delay-general elites (held-out 1.0 on all four)   11 of 12 seeds
  where generality is minted        delay-1 rung in 7, rung 2 in 3
  generations after the hold        10-50 (median 35)
  appears abruptly (one probe gap)  8 of 11
  adaptation cost to delays 2 and 4 0 generations in 11 of 11

Then the free result, which cost 0.3 s of compute: all 11 general elites
read delays 8 AND 16 -- never trained, never seen -- at held-out 1.0,
while matched-budget direct search reaches delay 8 in 0 of 6 runs and
delay 16 in 1 of 6. Four mature single-task solvers score 0.0 on both.
The invariance is the LADDER's product, not the product of competence.

Caveat that belongs in the same breath: in 5 of 12 seeds, the first
delay-1 battery promoted an organism the population ALREADY contained.
Part of the corridor's work is selection, not construction, and how
much is unmeasured.

7.4 IMPORT TAKEOVER IS MECHANICS, NOT CAPABILITY

228 runs. Mature solvers (direct competence 1.0) against opcode-permuted
controls built from the same manifests -- same length, same opcode
multiset, same operands, same VM knobs, competence removed and verified
at 0.0-0.125.

  arm (no cap)         takeover   median takeover generation
  no import            0 / 12     --
  mature, dose 1       12 / 12    4.5
  mature, dose 4       12 / 12    3
  mature, dose 32      12 / 12    2
  control, dose 1      11 / 12    8
  control, dose 4      12 / 12    6
  control, dose 32     12 / 12    3.5

One organism in 200 replaces the population within 10 generations, and
an incompetent one does it almost as fast. Dose sets SPEED, not outcome.
The only lever that moved the clock was an offspring cap: at 5%, takeover
slipped to generations 15-22 (mature) and 26-57 (control), and it was the
only setting leaving any resident lineage alive at generation 60. Nothing
tested PREVENTED takeover.

A detail that matters for anyone measuring diversity: origin takeover is
NOT clonal collapse. Distinct genomes stayed between 0.78 and 0.99
throughout. A genome-diversity readout would have reported no event.

7.5 TWO GEOMETRY CLAIMS DIED, ONE OF THEM ALMOST SURVIVED

The basin-share statistic, carried forward from campaign 2's rho -0.59,
was tested out of family. The pooled correlation came back at rho
-0.568 over 48 rows: an almost exact replication. It is a TWO-POINT
correlation. The two exhaustively-scored genotype tables differ 13x in
basin share and an order of magnitude in difficulty, so pooling them
manufactures the negative slope. Within stratum:

  table A, first-improvement climber   rho = -0.527
  table A, population climber          rho = +0.187
  table B, first-improvement           rho = -0.042
  table B, population                  undefined (all hit immediately)

Then the causal test. With task, operator masses (matched to 0.008),
budget and generation 0 all fixed, and only the reachable-opcode
neighbourhood rewritten:

  arm            grammar  high basin  low basin  rand A  rand B
  confirmed      8/12     8/12        9/12       7/12    8/12
  median gen     21       24          25         15      13

Effect -0.083, wrong direction, against a declared +0.25. Two RANDOM
orderings matched on basin share differ by the same 0.083. The
preregistered kill condition fired on its own terms.

The cellular-automaton line died the same way. Campaign 2 reported a
localized delayed-recall margin. Campaign 3 found the same localization
in a HAND-DESIGNED rule that never evolved for the task (0.966 vs 0.976
of the margin carried by one site), found that neither named mechanism
class fits (clamping the responsible site or its whole neighbourhood one
step earlier removes 0.000-0.086 against full drops of 0.45-1.68), and
found that the site's predictive power largely SURVIVES permuting the
reset lattice in 5 of 8 seeds. The readout was reading position-keyed
structure.

-----------------------------------------------------------------------
8. EVERYTHING CAMPAIGN 3 KILLED
-----------------------------------------------------------------------

  - summit-by-budget and summit-by-payoff on the two-stream cell;
  - basin/deception geometry as a design variable;
  - basin share's out-of-family replication (withdrawn as confounded);
  - the CA delayed-recall effect as an evolved COMPUTATION (it survives
    only as a falsifiable hypothesis about a position-keyed readout);
  - the original slot 8 (wall-clock producer-consumer under a full-solve
    criterion), replaced before execution because no full-solve regime
    exists on the cell it needed;
  - and, indirectly, the plausibility of every earlier "transfer helped"
    reading, since takeover is now known to be mechanical.

Practices that should never be repeated, each earned:

  - pooled rank correlations over strata of different difficulty;
  - localization claims without a non-evolved comparison rule;
  - frozen-readout margins without a permuted-structure control;
  - injection experiments without a cap and without reported origin
    shares;
  - instruments gated on a fixed constant rather than on the measured
    state of their own space.

-----------------------------------------------------------------------
9. WHAT THIS DOES NOT ESTABLISH
-----------------------------------------------------------------------

  - Nothing here is a claim about "the WSE" in general. One grammar, one
    VM, N=200, E=16, a handful of cells.
  - The two-stream ceiling is a BAND, not a proof of impossibility.
  - The corridor result's pooled effect is dominated by inherited
    competence; the honest claim is the four edge TYPES, not a general
    "initialization beats search".
  - Two results rest on n=6 and are labelled weak.
  - Basin share is not refuted as a descriptive statistic; it is refuted
    as a knob.
  - No claim anywhere in three campaigns has reached SUPPORTED_POSITIVE.
    Two weak positives from campaign 1 were taken to n >= 10 and died.
    The base rate for weak positives in this programme is bad, and this
    packet's own weak positives should be read against that base rate.

-----------------------------------------------------------------------
10. THE SCALING QUESTION, STATED AS A DECISION
-----------------------------------------------------------------------

The reason this packet exists: the instrument is now good enough that
scaling it up would produce a lot of trustworthy data, and it is not yet
clear that the data would be worth having.

THE CASE FOR SCALING. The measurement apparatus works. Zero engine
errors across a campaign. Positive controls that FIRE and catch real
design errors. A disposition ladder that has never once been talked into
a supported positive. Persistent tables that let an experiment be
designed against measured reachability rather than hope. Ten
preregistered experiments run autonomously in about six hours of
compute. Most of what a larger run would need already exists.

THE CASE AGAINST SCALING. In three campaigns the system has produced
exactly one reproducible positive capability -- the delay-invariant
reader -- and nobody knows what it is. The headline target (two-value
keyed memory) has resisted budget, initialization and payoff, which are
three of the four obvious levers. The fourth lever, changing the
organism or the search operator, has not been tried, and scaling the
current configuration would buy tighter error bars on a ceiling that is
already well measured.

The honest summary is that scaling would improve the PRECISION of
negatives. Whether that is worth the spend is the reviewer's call, and
"not worth continuing" is a first-class answer.

The four things a scaled campaign would have to do, in priority order:

  C4-1  Anatomise the delay-invariant reader. It is the only
        reproducible positive capability the programme has. Genotype,
        minimum lesion, whether the invariance is one instruction or a
        program shape.
  C4-2  Separate SELECTION from CONSTRUCTION in the corridor by probing
        the whole population at each rung transition, not the elite.
  C4-3  Attack the two-stream ceiling by changing the ORGANISM or the
        SEARCH OPERATOR -- a register/addressing primitive the grammar
        lacks, or crossover to cross the two-value valley -- with the
        mechanism stated before the run.
  C4-4  Make injection safe: a cap plus a protected resident niche, so
        imported capability can spread without replacing the population.

-----------------------------------------------------------------------
11. QUESTIONS FOR THE REVIEWER, WRITTEN TO RESIST AGREEMENT
-----------------------------------------------------------------------

 Q1  Is the half-credit shelf an interesting scientific object, or is it
     an artifact of choosing a two-stream cell whose reward decomposes
     additively? If the latter, the entire campaign-3 spine is a study
     of a badly chosen cell.

 Q2  The delay-invariant reader generalises to delays it never saw. Is
     that a capability, or is it evidence that the delay knob was never
     the difficulty it was assumed to be -- i.e. that a solver ignores
     delay by construction and the ladder just finds one?

 Q3  Is ANY of this the right substrate for "working memory"? The
     grammar has no addressing primitive beyond LD/ST on a bounded tape.
     A reviewer who thinks the answer is no should say so now; it would
     redirect campaign 4 entirely.

 Q4  The takeover result says imported material replaces populations
     regardless of competence. Does that invalidate the earlier
     literature of this programme that used injection, or merely
     caveat it?

 Q5  We report an INCONCLUSIVE where the machine offered a weak
     positive, on the grounds that the pooled statistic was confounded.
     Is that the right call, or is it over-correction that discards a
     real within-stratum signal at rho -0.527?

 Q6  Three campaigns, zero supported positives. Is that evidence of
     epistemic discipline, or of a system that cannot produce a result
     strong enough to survive its own gates -- and if the latter, are
     the gates or the substrate at fault?

 Q7  If you were spending this budget, would you scale WSE, redesign the
     organism, or stop and move the effort elsewhere?

-----------------------------------------------------------------------
12. ARTIFACTS, COMMITS, AND HOW TO ATTACK THIS
-----------------------------------------------------------------------

On branch main (repo D:\prometheus), campaign 3 closed at commit
cb9135104. Everything below is committed and pushed.

  archaeon/campaign3/CAMPAIGN_REPORT.md   the full campaign report
  archaeon/campaign3/MACHINE_READINESS.md instrument receipt, Phase A+B
  archaeon/campaign3/DECISIONS.md         D3-001..D3-022
  archaeon/campaign3/LEDGER.jsonl         41 entries
  archaeon/campaign3/JOURNAL.md           wall-clock narrative
  archaeon/campaign3/C3-SFE-NN/           per experiment: sealed
                                          preregistration, every attempt,
                                          rows, receipt, record
  archaeon/campaign2/REACHABILITY.jsonl   1,265 rows, all campaigns
  archaeon/campaign3/CORRIDOR.jsonl       155 rows
  roles/Archaeon/REVIEW_PACKET_CMP1..3    the three campaign packets

The cheapest ways to attack the work, in the order we would try them:

  1. Re-derive the shelf claim from C3-SFE-02's rows: is "1 improving
     child in 4,800" a property of the organism, or of a grammar whose
     destructive mass exceeds its constructive mass by design?
  2. Check whether the delay-invariance result survives a cell where
     delay cannot be ignored (retirement on, distractor streams on).
  3. Re-run the basin decomposition: is table A's -0.527 stable across
     climber seeds, or is n=12 encodings simply too few?
  4. Attack the takeover control: is an opcode-PERMUTED organism really
     a fair "incompetent" control, or is it structurally privileged over
     a random generation-0 organism in ways that make the comparison
     unfair to the mature arm?

+=====================================================================+
|  END OF PACKET                                                      |
|                                                                     |
|  The reviewer is explicitly invited to answer "this is not worth    |
|  continuing". Three campaigns have produced seven capable negatives |
|  in the last ten slots, no supported positive in thirty experiments,|
|  and one unexplained positive capability. A recommendation to stop  |
|  would be a legitimate reading of exactly the same evidence, and    |
|  nothing in this packet is written to make that harder to say.      |
+=====================================================================+
