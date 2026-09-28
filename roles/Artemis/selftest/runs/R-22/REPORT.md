# REPORT

## 1. WHAT I SET OUT TO TEST

In the Workspace/Serendipity Ecology (WSE) corridor ladder (W0 -> delay 1 -> delay 2 -> delay 4,
K=1 stream, 4-bit values, Proteus bytecode organisms), campaign 3 reported one positive capability:
elites that score 1.0 at delays 8 and 16, which they never trained on. The report did not say what
these organisms do. I asked four linked questions. (a) What is the genotype, and what is the smallest
lesion that removes the delay competence? (b) Is this a real memory capability, or is the delay knob
easy in a way nobody noticed? I tested (b) with hand-built programs and with probes that change where
the PUT sits and what the noise contains. (c) At the delay-1 transition, does the ladder select organisms
that the population already contained, or does it build new ones? This needs whole-population probes,
which were never run. (d) Is the half-credit shelf on the two-stream cell a real object, or an artefact
of per-ask (additive) reward? The fourth question in the package, an adaptive difficulty schedule with a
working down-rule, was not attempted (see 4).

## 2. WHAT I DID

All inputs were committed at cb91351046c78592c455a0e090e29dd7f78a03ba (cb9135104). I exported code with
`git archive cb9135104 archaeon/wse archaeon/campaign2 archaeon/campaign3 archaeon/__init__.py
archaeon/workspace.py archaeon/provenance.py archaeon/config.py archaeon/clock.py proteus` into
<scratch>/src and ran everything there under `env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE`.
The runs used no engine, database or service.

Data (committed rows @cb9135104):
- archaeon/campaign3/C3-SFE-03/rows.json: the 12 ladder elites (elite_manifest), 11 of them delay-general.
- archaeon/campaign3/C3-SFE-01/rows.json: the 24 final elites on the two-stream cell W2_K2 (the shelf).
- archaeon/campaign3/C3-SFE-08/rows.json: the all-or-nothing reward arm (traces, used to check reproduction).

Scripts (all in <scratch>):
- dissect.py: disassembles each ladder elite. It scores the elite at delays 0/1/2/4/8/16/32 on 48
  episodes per delay. It then applies every single-instruction knockout (op -> NOP, operands kept; this is
  the program's own knockout rule) and scores each knockout at every delay.
  Outputs: out_dissect.txt/json, out_lesion_summary.txt.
- probes.py, probes2.py: adversarial noise probes, using the world grammar exactly except for the noise
  ticks. Noise words were drawn small (<16), shaped like a PUT, given kind codes 0/1/2/3..17/2^31+1/2^32-1
  or random, or given lengths 0/1/2/4. I also varied value width (8/16/32 bits) and ran delay 64. Four
  hand-built constructions were scored alongside the elites: ungated W0 solver (5 instr), first-tick latch
  (6 instr), kind==PUT gate (9 instr), magnitude gate (9 instr).
- probes3.py: moves the PUT away from tick 0 by adding 1, 2 or 4 noise ticks before it (pre-noise), at
  delays 0/2/4.
- shelf.py, shelf2.py, order.py: on W2_K2, checks which PUT value each organism answers with (first or
  last). It also checks whether two-value organisms depend on the ask order: asks in PUT order versus
  reversed, with distinct values so ties earn no credit.
- poprun.py, popsum.py: re-runs the committed ladder (ladder.run_ladder, same seeds, N=200, E=16,
  p=0.1, rung0_max=100) with a hook that probes the WHOLE population. Probes run every 5 generations and
  at every generation from T1-3 to T1+15, where T1 is the first delay-1 generation. Each organism gets 12
  episodes each of d0, d4 and pre-noise+d4, and is classified as W0-only, general-latch or general-gated.
  Each run stops 30 generations after T1. Seeds run: 1, 2, 6, 7, 8, 9, 10, 11, 12. T1 matched the
  committed transitions in 9/9 seeds.
- sfe08.py: re-runs the all-or-nothing (episode-credit) arm on W2_K2 for seed 4, 300 generations. The
  elite's episode-reward trace matched the committed trace for all 300 generations, and the final
  held-out score matched the committed 0.500/0.500. I then applied the ask-order test to the elite.

## 3. RESULT

(a) What the reader is. All 11 delay-general elites score 1.0 at every delay tested (0 to 64). Under noise
that shares the PUT's position they are robust to almost every content change: small noise words, wrong
kind codes, noise shaped like a PUT, a distractor PUT to another tag, ticks of length 0-4, and 8-32-bit
values (>= 0.94 everywhere). One exception: seed 4 fails when the noise's first word is 1, 9 or 2^31+1.
The decisive probe was one noise tick BEFORE the PUT, with delay 0. Under it, 10/11 elites fall from 1.0
to 0.00, and the same holds with 1, 2 or 4 pre-noise ticks at delays 0-4. The hand-built 6-instruction
first-tick latch reproduces this pattern exactly. The one non-general ladder elite, a plain W0 solver,
scores 1.0 on the same probe. So 10 of the 11 "delay-invariant readers" are FIRST-TICK LATCHES. They
store whatever arrives on the episode's first tick and never overwrite it. They read neither the delay,
nor the kind word, nor the tag. The world always puts the only PUT at tick 0, so this solves every delay
trivially. Only seed 4 is a content-gated reader: it stores on the kind word, and its gate is imperfect.
On W2_K2 the 10 latches answer every ask with the FIRST PUT's value (100% of asks), and seed 4 answers with
the LAST PUT's value (100%). Both score per-ask 0.526 and episode 0.052.

Genotype and minimum lesion: 8-27 instructions. In 6/11 elites, one to four single instructions are
"delay-only". Knocking out any one of them leaves a perfect W0 solver that scores 0 at every delay >= 1:
seed 5: 1 instruction, seed 6: 3, seed 7: 4, seed 8: 2, seed 11: 2, seed 12: 3. Seed 11 is the cleanest
case. `EQ r2,r0,r0` sets a flag on the first tick, and `JNZ r2` then skips the read/store path on every
later tick. Removing either instruction gives an ungated W0 solver. In the other 5/11 (seeds 1, 2, 3, 4, 9),
no single lesion separates delay competence from W0 competence, because the latch is part of the W0 mechanism itself.
Of 188 single lesions, exactly one had a delay-LENGTH-dependent effect (seed 6, instr 2: d1 0.94, d>=2
0.00). The invariance is one flag and a branch, not a program shape that scales with delay.

(b) Construction null: the delay knob was never hard as a memory-duration knob. Registers persist and do
not decay, so for these organisms delay 1 and delay 64 are the same problem: do not overwrite the stored
value on a non-PUT tick. The ungated W0 solver scores 1.0 at d0 and 0.00 at every d >= 1. The latch and the
kind gate each score 1.0 at every delay. The magnitude gate also scores 1.0 at every delay on standard
noise, but fails once the noise words are small. The committed direct-search rates fit a difficulty that
does not depend on delay: d4 1/14, d8 0/6, d16 1/6. The ladder's "free" transfer to d8/d16 therefore says
nothing about working memory. The held-out batteries cannot tell a latch from a reader, because they never
move the PUT off tick 0.

(c) Select or construct. Whole-population counts of delay-general organisms at the last probe before the
delay-1 transition:
seed 2 73/200, seed 11 19/200, seed 7 6/200, and 0/200 in seeds 1, 6, 8, 9 and 12. Seed 8 had 5/200 earlier
in W0 but lost them. Seed 10 never became general. So the ladder SELECTED standing variation in 3/8
general seeds and CONSTRUCTED generality after the transition in 5/8. When constructed, the first general
organism in the population appeared 3-14 generations after T1. In both routes the organisms are latches.
The gated class appeared only transiently (max 4/200, seed 6). Latches also spread under pure W0 selection
(seed 2: 98/200 before any delay rung), because W0 cannot tell a latch from an ungated solver: this is
neutral drift. What the ladder "constructs" is a one-bit latch flag.

(d) The half-credit shelf. The one-value shelf elites are mostly the same latch. Among one-value shelf
elites in the committed W2_K2 runs, 6/9 (fresh arm) and 7/12 (shelf arm) score 0 under one pre-noise
tick. Asks are shuffled independently of PUT order. Any one-value memory therefore earns exactly 1/2 per
ask (0.526 with ties) and about 1/16 per episode, so the 0.5 per-ask level is arithmetic of additive
credit. Under all-or-nothing credit the one-value shelf does not persist: those organisms score 0.052.
But a 0.5 level does persist. I re-ran the committed all-or-nothing arm (seed 4), and it reproduced exactly.
Its "both-or-neither two-value" elite is a tag-blind FIFO queue: episode 1.0 when the asks come in PUT
order and 0.0 when they are reversed. Two fresh-arm W2_K2 elites (seeds 3 and 11) are the same FIFO
(1.0/0.0). Under both credit rules, then, the ~0.5 shelf is occupied by organisms that ignore the tag word.
Its level comes from P(ask order = PUT order) = 1/2, or from 1 of 2 asks. The campaign's reading of the
all-or-nothing organisms as ones that "hold both values keyed" is wrong for the case I could check.

## 4. DID IT RESOLVE THE QUESTION

Mostly yes for (a) and (b). The reader's mechanism is identified in 11/11 elites: 10 latches and 1 kind
gate. I found the minimum lesions and showed that the knob is not a memory-duration difficulty. This
rests on single lesions only; I did not search pairwise lesions for the five entangled genomes.

Partly for (c): 9 of 12 seeds were re-run. Seeds 3, 4 and 5 were dropped for CPU budget, and each run
stopped 30 generations after T1.

Partly for (d). The shelf question was not posed quite right: the 0.5 level is set by tag-blindness plus
random ask order, not by additive reward alone. The FIFO reading of the all-or-nothing organisms rests on
1 re-run seed plus 2 committed elites; the other four "two-value" episode-arm seeds were not re-run.

The adaptive difficulty schedule with a working down-rule was not attempted.

## 5. CONSEQUENCES

- Instrument/harness defect, and a false premise. The WSE stream episodes always place the only PUT (K=1)
  at tick 0, and the held-out batteries keep that position fixed. "Reads unseen delays d8/d16" is
  therefore satisfied by a first-tick latch that reads nothing. Every WSE working-memory or
  delay-generality claim should be re-read with this in mind: the campaign-3 "only reproducible positive
  capability", the "free" corridor edges to W1_d8/W1_d16, and the "delay-invariant on arrival" findings.
  The fix is cheap: add pre-PUT noise or jitter to the PUT position, and add an ask-order control for
  K=2, to training and held-out batteries. The same position-keyed pattern was already suspected in the
  campaign-3 CA readout ("reading position-keyed reset structure"); this is a second, independent case.
- The half-credit shelf and the "two-value" organisms are tag-blind: latch, last-value or FIFO. On W2_K2
  the summit needs the tag word to be used, and no organism I examined uses it. This supports "change the
  organism or the search" for W2_K2, with a sharper target: tag binding. It also refutes the "keyed"
  description of the all-or-nothing organisms for the seed checked.
- Selection vs construction: both occur, 3/8 vs 5/8. Latches also drift neutrally under W0, so
  "standing variation" of generality here is a by-product of an invisible equivalence, not pre-adaptation.
- Who should know: the WSE/corridor owner (Archaeon seat) and whoever keeps the reachability and
  corridor tables. The W1_d8/d16 and ladder-route rows and the WSE world generator's position invariants
  need a caveat. Anyone citing the campaign-3 summary items on delay invariance and the shelf should also know.
- Reproduction: the ladder transitions and the all-or-nothing arm reproduced bit-for-bit from committed code.

## 6. COST

About 2 hours of my own time. CPU was about 63 CPU-minutes, slightly over the 1 CPU-hour cap, with at
most 2 processes. Most of it went to the population re-runs (~41 min, including about 13 min on an
aborted seed-3 run and a partially run seed 5) and the 300-generation re-run (~15 min). Memory stayed
well under 1 GB, with no GPU, no services and no database.

Not done: population probes for seeds 3, 4 and 5; pairwise lesions; re-runs of the other four all-or-nothing
seeds; the adaptive down-rule schedule.
