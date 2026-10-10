# NPE-48h functional heredity: findings log (append-only; numbers from runs/<EXP>/REDUCED.json)

## F1. X-LOSS-AUTOPSY: why transmitted function is transient (EXPLORE, runs/X-LOSS-GATE, 54 runs)

All arms below are pooled over established runs. The physics is the same in every arm per interaction.

**Transmission works.**
- P(competent child | competent P-11 donor) = 0.89-0.91 per causal generation (n = 3,421-9,514 births per arm).
- The copy itself (tape, before the world's post-copy mutation) is competent in 0.94: block-copy errors cost about
  6%, and post-copy mutation about 4%.
- LABEL births transmit at 0.82-0.85.

**Losses are mostly replacement, not decay.**

| loss class | share of competence losses |
|---|---|
| LOST_OVERWRITE (a competent organism is overwritten by a NON-competent copier) | 0.81-0.87 |
| LOST_INPLACE (ATOMIC in-place mutation) | 0.12-0.17 |
| copy error or mutation at birth | 0.01-0.02 |

**The copy race is neutral; transmission leaks.**
- After the peak, competent-over-non-competent wins / non-competent-over-competent wins = 0.90-0.92 in every arm.
- That equals the transmission fidelity: competence is a NEUTRAL passenger in the exchange among copiers.
- The one-way mutational leak (competent -> non-competent copier; the reverse is about 0) drains it.

**The hazard is constant per interaction.** Loss per competent-half interaction is 0.20-0.27 in all arms. So
persistence time is set by interactions per epoch, not by any selective force.

**Where it breaks.**
- A changed byte in the task routine (bytes 7-38) destroys competence with probability 0.63-0.67, against
  0.08-0.12 for the copier (bytes 0-6).
- Statically, the routine's single-byte robustness is 0.38, against 0.98 for the copier.
- The routine is structurally independent of the copier: no shared bytes, and the copier runs first and halts
  nowhere near the routine.

**Failure funnel:**
1. The copier spreads CT_UA into the random soup; CS peaks at 0.23-0.48.
2. Per interaction, about 3.5% of competent halves become non-competent copiers: in-place mutation about 3.2%,
   copy-born about 0.4%.
3. Neutral copy exchange then lets the non-competent copiers replace competent ones as often as the reverse.
4. Competence is extinct after about 50-100 interactions per organism.

**Barrier moved:** functional transmission is PRESENT. Functional persistence FAILS because selection on function is
ABSENT: the copy race does not see the task.

## F2. X-GATE-HARM: HARMFUL (declared rule; EXPLORE, same runs)

| arm | median last epoch with CS > 0 (established) | interactions per epoch, competent halves | per non-competent half |
|---|---|---|---|
| TG | 70 (range 60-160) | 0.998 | 0.159 |
| SHUF | 220 (10-350) | 0.41 | 0.17 |
| C015 (competence-blind floor) | 400 (0 or 220-900) | 0.15 | 0.15 |
| C100 | 50 (30-80) | 1.0 | 1.0 |

- The TG gate gives competent organisms about 6.6x more interactions per epoch and no exchange advantage. Since the
  hazard per interaction is unchanged, it only speeds up neutral drift to extinction.
- **"Selection" by meeting frequency is not selection when the encounter is symmetric.**
- **Next (as the directive prescribes):** change the DIRECTION of copying, not its rate (X-DIR-QUAL).

## Defects found and repaired

**DEF-FH-1 (harness, tests and assays only):** fh's ledger wrapper called the class `_mutate` and deleted any
instance-level override. An assay that disabled mutation on an instance therefore silently kept world mutation on;
about 9% of "mutation-free" CT_UA copies differed by one byte.
- Repaired: the wrapper chains to the bound `_mutate` and restores it.
- Regression: HK-1. The old behavior is the failing case (the 9% diffs reproduced before the fix).
- Production runs never override `_mutate`, so they are unaffected; EQ-1 still matches frozen XTG-v2 bit for bit.
  The X-LOSS-GATE batch straddled the fix, and its runs are behaviorally identical under both versions.

## F3. X-DIR-QUAL: SIGNAL. Selection on copy DIRECTION maintains transmitted function (EXPLORE, 60 runs)

**Setup:** order = DIR (q = 1: the higher-u organism runs first, i.e. is the would-be donor), with interaction rate
fixed and competence-blind (CONST p).

**Maintenance** (final CS >= 0.10, established runs):

| arm | maintained | final CS |
|---|---|---|
| DIR015 (2000 epochs) | 12/12 | 0.91-0.95 |
| DIR100 (300 epochs, matched about 300 interactions per organism) | 12/12 | 0.88-0.94 |
| RND015 | 0/9 | -- |
| RND100 | 0/12 | -- |
| CT_U under DIR | 0/5 | CS = 0 at every snapshot |
| COPY_ONLY under DIR | 0/5 | CS = 0 at every snapshot |

- Both negatives established their copiers and runaway, yet never showed competence.
- DIR also raised CT_UA establishment: 12/12, against 9/12 under RND015.

**Mechanism (ledger):**
- Side 0 wins the copy race in 93-98% of conversions in every arm. DIR therefore converts "first mover wins" into
  "function wins".
- The exchange becomes 50,420 competent-over-non-competent conversions against 815 the reverse (RND: 5,524 against
  4,925).
- Losses shift from OVERWRITE (0.89 under RND) to the mutational leak:

  | loss class (DIR) | share |
  |---|---|
  | in-place | 0.43 |
  | copy error | 0.29 |
  | post-copy mutation | 0.26 |
  | overwrite | 0.02 |

- Hazard per competent-half interaction: 0.058 (RND: 0.26-0.28).
- Transmission per generation is unchanged at 0.92. The function is held at a mutation-selection balance of
  CS about 0.92.

**Architecture after about 300 interactions per organism (arch_mine DIR015, 12 runs):**
- A quasispecies: 100-122 competent genome families per run; the dominant family has a share of 0.03-0.09 and a
  Hamming distance of 14-24 from CT_UA.
- Conservation against CT_UA: copier 0.97, routine 0.80, padding 0.43. The planted routine SURVIVES; drift is in the
  padding and in some neutral routine positions.
- Single-byte robustness of the dominant genome: all 0.69-0.72 (CT_UA 0.69); routine 0.38-0.45 (CT_UA 0.38). There
  is no clear robustness gain; 3 of 12 are at 0.43 or above (weak; not yet tested).
- Copier function is intact: P-11 conversion 0.95-1.0, task kept in 0.90-0.95 of copies.
- **No architectural integration** at this horizon. The task is cargo held by selection, not fused with the copier.

**Barrier moved:** functional persistence and selection on function are now PRESENT, under an external directional
coupling. Architectural integration is NOT observed. Endogenous re-discovery has not yet been tested.

**Scope caution:** DIR is a world rule that reads the task ruler, so selection on function is designed in. What is
discovered is that DIRECTION (copy priority), not RATE (meeting frequency), is the coordinate that makes function
heritable-and-selected on this pair tape.

## F4. Mining X-DIR-QUAL DIR015: maintained function, rewired architecture (descriptive; final competent genomes, 12 runs)

**Neutral positions** (CT_UA single-byte robustness 1.0) drift freely:
- IN/OUT port operands (bytes 8, 11, 14, 33, 37): conservation 0.34-0.81.
- The trailing HALTs (34, 38).
- The ANSWER_BEFORE_READ branch (35-38), which is near-dead under STATIC FORCED_READ: it is taken only when key = 1.

**FRAGILE positions also vary**, through COMPENSATED multi-byte rewrites, all with u = 1.0:

| CT_UA position | robustness in CT_UA | conservation among maintained genomes |
|---|---|---|
| 16 | 0.15 | 0.83 |
| 19 | 0.15 | 0.80 |
| 29 | 0.23 | 0.82 |

Variants seen:
- The vestigial read-order detector (`LD A,C; CP 2; JRC abr`) is rewritten or neutralized:
  - `LD L,C; LD D,D; nop`: the jump is kept, but the compared value is gone;
  - `CP 3; LD L,0E`: the jump is removed;
  - `CP 45; SUB 0E`;
  - `JRC` becomes `JRZ`;
  - `OR A; INC A`.
- The regime-0 exit is re-routed: the JRZ offset becomes +6 or +3, so the base answer is emitted through the formerly
  dead ABR branch's `OUT` (byte 36). Dead code is reused.

**Reading:** where the function is maintained, the planted routine is not frozen. The population sheds a structure the
static world makes vestigial, and repurposes dead code, while the essential conditional is conserved at 1.00: IN and
LD at 7-15; XOR, branch and ADD 37 at 21-31.

**Open:** whether this is neutral drift or robustness selection. The dominant genomes' routine robustness is
0.38-0.45, against 0.38 for CT_UA. X-DIR-LONG tests it.

## C1. C-DIR-MAINTAIN: CONFIRMED (CONFIRM lane; fresh seeds; protocol frozen at 27c5271b4)

| arm | maintained (established runs) | final CS |
|---|---|---|
| DIR015 | 12/12 | 0.887-0.953 |
| RND015 | 0/12 | 0 |
| CT_U under DIR | 0/6 | 0 |
| COPY_ONLY under DIR | 0/6 | 0 |

- **PROMOTED mechanism:** on the ffa6 pair tape, coupling task competence to copy DIRECTION (who runs first) turns a
  transmitted function into a maintained one. Coupling competence to interaction RATE does not (F2).

## ATLAS PACKET A1 (cross-pollination)

| field | value |
|---|---|
| barrier before | functional transmission yes (P-11 child keeps the task 0.90 per generation); functional persistence no (the task is a neutral passenger in the copy race; a one-way mutational leak of about 3.5% per interaction erases it in about 50-100 interactions per organism) |
| intervention | competence decides copy priority (who executes first on the pair tape), with the interaction rate held competence-blind |
| barrier after | persistence and selection on function present (CS about 0.92 at mutation-selection balance; confirmed 12/12 vs 0/12); architectural integration not yet; endogenous re-discovery being tested |
| primitive / mechanism | first-mover-wins copy race (side 0 wins 93-98% of conversions); "selection" must act on the asymmetry of heredity, not on encounter frequency. A symmetric rate gate is HARMFUL (it accelerates neutral drift to loss). |
| generalizes? | the encounter-symmetric vs direction-asymmetric distinction should hold for any engine whose replication is a pairwise race; untested outside ffa6 |
| open neighbors | the q x mutation boundary (X-DIR-SURFACE); re-discovery distance (X-REDISCOVER); de novo emergence (X-RANDOM-DIR); integration over long horizons (X-DIR-LONG) |

**Barrier map:**

| transition | status |
|---|---|
| copy-capable material | PRESENT |
| causal heredity | PRESENT |
| functional transmission | PRESENT |
| functional persistence | PRESENT only under directional coupling |
| selection on function | PRESENT only under directional coupling |
| architectural integration | not observed; neutral rewiring of vestigial code seen (F4) |
| endogenous re-discovery | testing |

## Defects (continued)

**DEF-FH-2 (instrument; it crashed a whole experiment):** `summarize` stored the run cfg verbatim. A plant given as
raw bytes, as X-REDISCOVER's variants are, made the row write fail with a TypeError, so every X-REDISCOVER job
failed. No row was written and no result was lost; the orphan detail files were deleted.
- Repaired: `_jsonable` writes bytes as {"hex": ...}.
- Regression: JS-1. The production TypeError is the failing case.
- X-REDISCOVER is re-queued unchanged.

**Queue tooling:**
- `runqueue.py` was first named `queue.py`, which shadowed the stdlib `queue` that multiprocessing imports. It failed
  at once, with no runs.
- Its `--after` wait line had a broken string literal; the process died before waiting.
- Both were caught before any run and fixed.

## F5. X-RANDOM-DIR: CLEAN_NULL (structural)

**Result:** from random populations at CONST 0.15, 2000 epochs:
- no copier regime: 0/12 runs reached depth >= 20, max depth 3;
- no competence root in either arm.

**DIR and RND rows are identical by construction**, which is not a defect:
- with u = 0 everywhere, DIR never reorders and never draws its private RNG;
- so the identical-arms signature, normally a defect flag, is the expected reading here.

**What it bounds:** de novo functional heredity in this world is blocked at the FIRST rung (copy-capable material).
The task rung is never reached.

**Retired:** the earlier C-A3 runaways (25/72) came under QD pressure and are a different regime. Re-discovery is
tested instead from copier backgrounds (X-REDISCOVER).

## F6. X-DIR-SURFACE: SIGNAL. A monotone maintenance boundary in directional strength q x mutation k (66 runs + X-DIR-QUAL q = 1, k = 1)

**Maintained runs / established runs** (median final CS in brackets; CONST 0.15, 2000 epochs, CT_UA):

| q | k = 1 | k = 4 | k = 16 |
|---|---|---|---|
| 0.10 | 3/6 (0.10, at the boundary) | 0/5 | -- (1/6 established) |
| 0.25 | 6/6 (0.65) | 0/5 | -- (1/6 established) |
| 0.50 | 6/6 (0.86) | 4/6 (0.24) | -- (0/6 established) |
| 1.00 | 6/6 (0.93) | 4/6 (0.63) | -- (1/6 established) |

**The boundary:**
- About q = 0.10 at k = 1, and between 0.25 and 0.5 at k = 4.
- So the directional advantage needed scales with the mutational leak, consistent with F1 (leak about 0.035 x k per
  interaction).
- At k = 4 even q = 1 maintains in only 4/6 runs: k = 4 is near the edge for this routine.

**Two error thresholds, ordered:**
- At k = 16 (about 2 copy errors per copy) the COPIER regime itself fails to establish, in 1/6 or fewer per cell.
  Heredity collapses before function can be tested.
- The function threshold (k about 4-8 at q = 1) sits below the copier threshold (k < 16). This matches the routine
  being about 6x more mutationally fragile per byte than the copier (F1).

**Weak signal (not chased yet):** q = 0.10, k = 1 splits 3/6 with final CS 0.10-0.12 among the maintained runs. This
cell is AT the boundary, the place to measure the critical selection coefficient. It is not chased now; more seeds
alone would not discriminate it.

## F7. X-REDISCOVER: WEAK_SIGNAL. Re-discovery is supply-limited at distance 1 and absent at distance >= 2 (48 runs)

**Setup:** copier-backgrounds whose routine is d operand-steps from use (CT_UA with byte 31 changed); all
established; CONST 0.15; 2000 epochs.

| distance | runs with a competence-creation root (DIR / RANDOM) | runs ending competent, final CS >= 0.10 (DIR / RANDOM) |
|---|---|---|
| d = 1 (0x24) | 2/6 / 4/6 | 1/6 (CS 0.95) / 0/6 |
| d = 2, 3, 4 | 0 / 0 | 0 / 0 |

- The swept d = 1 rediscovery restored byte 31 to 0x25: the SAME solution as CT_UA.

**Reading:**
- At d = 1 the creating mutation arises only 0-1 times per run (about 77k organism-interactions). Under DIR a new
  competent mutant can sweep (1 of 2); under RANDOM it never persists.
- From d >= 2 no creation occurs. The use ruler gives intermediates no credit (the ADD constant is ATOMIC), so a
  two-step path needs neutral drift and a second rare event.
- **Endogenous re-discovery is bounded by mutational SUPPLY across a valley, not by selection.**

**Child:** X-REDISCOVER-SUPPLY (a supply x7 test, below).

## F8. X-ONTAPE: SIGNAL. Endogenous on-tape priority maintains function; and function can become PAIR-DISTRIBUTED (EXPLORE, 36 runs + 1 replay)

**Setup:** copy priority is earned only from the organism's own answers on the pair tape. The episode is fed to IN
during the copying execution; the score is an EWMA of the first OUT's correctness; it resets on conversion. No
offline scorer sits in the loop.

**Maintenance:**

| arm | maintained by the offline use ruler | final CS | on-tape correct share |
|---|---|---|---|
| ONTAPE | 10/10 established | 0.76-0.86 (one at 0.11) | 0.70 |
| ONTAPE_RND | 0/10 | -- | 0.04 |
| CT_U under ONTAPE | 0/5 use-competent | -- | 0.37 (partial credit maintains read-but-ignore behavior; never creates use) |
| COPY_ONLY under ONTAPE | 0/4 | -- | 0.00 |

**Ledger:**
- The exchange advantage is only about 2:1 (62,759 against 30,313), against 60:1 under DIR.
- Overwrite is still 0.50 of losses.
- A noisy endogenous priority signal suffices.

**Lower causal depth (37-62, against 95-138 under ONTAPE_RND):** consistent with reputation being age-structured.
The score resets on conversion, so long-scored elders out-prioritize their own fresh copies. This is a hypothesis
only; it was not separately tested.

**Anomaly mined: run 44900007 collapsed from CS about 0.78 to 0.11 between epochs 1500 and 2000** (a deterministic
replay, `mine_ontape7.py`).
- The genomes that displaced competence are offline-INCOMPETENT (u = 0) with the HIGHEST on-tape scores (EWMA
  0.71-0.87).
- **Mechanism:** a single change of the JRZ offset (byte 29: 0x02 -> 0x42, +66) sends the regime-0 path out of the
  genome:
  - offline (alone in a scratch arena) it never answers r = 0, so u = 0;
  - on the 128-byte pair tape the jump wraps into the PARTNER's half at byte 32, an OUT instruction in this population.
    The invader emits its regime-0 answer by executing its partner's code;
  - its own byte 32 is also OUT, so it works with copies of itself: on-tape homotypic use = 1.0.
- **The function has become pair-distributed:** it is not contained in any one genome, yet it is stable in the
  population.
- At the same time some offline-competent genomes fail on the tape. For example `ED 02` at byte 17 is harmless
  offline (ops disabled) but acts on the tape.
- **Offline competence and in-context function DIVERGE once selection reads in-context behavior.**

**New ruler (readout only):** tape_self = on-tape homotypic cue-flip use (fh `_tape_self`; the independent
`arch.tape_use` agrees, test TR-1).

| genome | tape_self |
|---|---|
| CT_UA | 1.0 |
| CT_U | 0 |
| COPY_ONLY | 0 |
| the invader | 1.0 |

- Against a copier partner every genome scores about 0.5: as side 1 it is overwritten before running.

**Reading:**
- The decisive ruler must match where selection acts. Under ONTAPE, the offline CS UNDERSTATES maintained function.
  The 0.11 run is a transition to a distributed architecture, not a loss.
- This is the first observed ARCHITECTURAL change that is not mere drift: function re-implemented across the
  pair-tape ecology, using the partner's code.

**Children:**
- C-ONTAPE-MAINTAIN (CONFIRM, both rulers).
- X-ONTAPE-LONG: does the distributed form spread?

## F9. X-VETO: SIGNAL. Any competence-coupled asymmetry of copy DIRECTION suffices; offense (DIR) and defense (VETO) are equivalent (EXPLORE, 36 runs)

**Maintenance** (CONST 0.15, 2000 epochs, CT_UA):

| arm | maintained (established runs) | final CS |
|---|---|---|
| VETO015 (random order; a pair whose first mover is less competent is skipped) | 12/12 | 0.82-0.89 |
| DIR015 | 12/12 | 0.90-0.95 |
| RND015 | 0/11 | -- |

**Ledger (VETO vs DIR):**

| quantity | VETO | DIR |
|---|---|---|
| competent-over-non-competent : reverse | 41,620 : 699 | 50,704 : 829 |
| loss shares (in-place / copy error / copy mutation / overwrite) | 0.42 / 0.30 / 0.26 / 0.018 | the same |
| hazard per competent interaction | 0.058 | 0.059 |

**Reading:**
- Removing the LOSING direction of exchange (defense) is mechanistically equivalent to granting the WINNING direction
  (offense).
- VETO's slightly lower equilibrium comes from the interactions it forgoes.
- **Unifying principle (EXPLORE level; DIR confirmed, VETO not yet):** function is maintained iff competence biases
  the DIRECTION of the copy exchange. Interaction-rate coupling fails because it is direction-symmetric (F2).
- This holds whether the bias is imposed by an offline ruler (DIR / VETO) or earned on the tape (ONTAPE, F8).

## F10. X-ARCH-COMPETE: SIGNAL. Selection on function also selects the more ROBUST implementation (EXPLORE, 24 runs)

**Setup:** CT_UA (routine 32 bytes, single-byte robustness 0.69; its copies keep the task 0.90 of the time) and CT_W
(routine 24 bytes, robustness 0.75, copies keep the task 1.0), planted together under DIR. Both have u = 1, so DIR
ties them; only their mutational leak differs. The plant slot alternates by seed.

**CT_W-family share of final competent organisms:**

| k | runs where CT_W holds the majority | median CT_W share | final competence |
|---|---|---|---|
| 1 | 11/12 | 1.0 | 12/12 maintained |
| 4 | 12/12 | 1.0 in every run | 12/12 maintained |

- Under k = 4, CT_UA alone maintained in only 4/6 runs (F6).
- There is no slot effect: CT_W wins from either planting slot.

**Reading:**
- Once function is under directional selection, competition between functional architectures is decided by
  mutational robustness (leak).
- The selection is stronger at higher mutation, as declared.
- This is architecture-level selection by SUBSTITUTION between existing forms. Whether compression or robustness can
  arise DE NOVO within a lineage is X-DIR-LONG's question.
- **Caveat:** CT_W differs from CT_UA in more than robustness. It lacks the read-order detector and has a shorter
  routine, so "robustness" here means a smaller destructive mutational target, not a separately measured property.

**Child:** C-ARCH-COMPETE (fresh seeds, frozen).

## Defects (continued)

**DEF-FH-3 (instrument; it invalidated a declared horizon):** world.Runner applies
`t["epochs"] = min(t["epochs"], max_epochs)`, so `epochs` above the tier's 2000 was silently capped.
- X-DIR-LONG (declared 8000 epochs) ran its first 5 jobs at 2000 epochs. They were caught from the row timings
  (about 270-440 s, against an expected 1000-2000 s).
- Queue 2 and its workers were stopped. The 5 rows are quarantined in runs/X-DIR-LONG_INVALID_DEF-FH-3/ and are not
  used.
- Repaired: fh extends `r.t["epochs"]` explicitly. Regression: LE-1. The old behavior is the failing case, as the
  production rows show.
- X-DIR-LONG is re-queued unchanged.
- X-ONTAPE-LONG (6000) had not started; it will run with the fix.
- No completed 2000-epoch experiment is affected: their declared horizon equals the cap.

## C2. C-ONTAPE-MAINTAIN: CONFIRMED (CONFIRM lane; fresh seeds 45_200_000+; protocol frozen at 9bfe58eab; primary ruler TCS)

| arm | function maintained (final TCS >= 0.10, established runs) | final TCS | final offline CS |
|---|---|---|---|
| ONTAPE | 12/12 | 0.70-0.81 | 0.66-0.86 |
| ONTAPE_RND | 0/12 | -- | -- |
| CT_U under ONTAPE | 0/6 on both rulers | -- | -- |
| COPY_ONLY under ONTAPE | 0/6 on both rulers | -- | -- |

- **Pair-distributed (tape-only) genomes recur:** present at the end in 8/12 ONTAPE runs, at 0.4-7.8% of the
  population. They are not a one-run curiosity.
- **PROMOTED mechanism:** copy priority EARNED from the organism's own in-context answers (no offline scorer in the
  loop) maintains a transmitted function on the pair tape.

## ATLAS PACKET A2 (cross-pollination)

| field | value |
|---|---|
| barrier before | persistence required an external ruler deciding copy direction (A1) |
| intervention | the world feeds task inputs to the pair-tape execution in which copying happens; copy priority is an EWMA of the organism's own on-tape answers (no offline scorer) |
| barrier after | persistence and selection on function hold ENDOGENOUSLY (confirmed 12/12 vs 0/12) |
| new phenomenon | in-context selection lets function become PAIR-DISTRIBUTED. A genome can answer by jumping into its partner's code (byte-29 JRZ +66 -> the partner's OUT). It is competent on the tape and incompetent alone. Offline and in-context function diverge, so rulers must match where selection acts. |
| primitive / mechanism | (1) direction-biased copy exchange (offense DIR = defense VETO, F9); (2) robust architectures out-compete fragile ones under function selection (F10); (3) shared-tape execution makes the partner's code part of one's phenotype |
| generalizes? | 7ae3 scope test queued; direction-vs-rate should transfer to any pairwise-race replicator |
| open neighbors | does the distributed form spread over long horizons (X-ONTAPE-LONG, running)? is it cooperative or parasitic (frequency dependence)? does any genome-level compression arise de novo (X-DIR-LONG)? |

**Barrier map (updated):**

| transition | status |
|---|---|
| copy-capable material | PRESENT (planted); de novo blocked (F5) |
| causal heredity | PRESENT |
| functional transmission | PRESENT (0.90-0.92 per generation) |
| functional persistence | PRESENT under direction coupling (external C1, endogenous C2) |
| selection on function | PRESENT; also selects robust architectures (F10) |
| architectural integration | FIRST SIGNS: pair-distributed function (F8, C2); neutral rewiring of vestigial code (F4) |
| endogenous re-discovery | 1-step only, supply-limited (F7) |

## F11. X-ONTAPE-LONG: WEAK_SIGNAL, provisional. Function holds for 6000 epochs; pair-distributed forms are a recurring minority (6 runs)

**Function:** maintained in 6/6 runs to epoch 6000.
- Final offline CS: 0.77-0.81.
- Corrected final TCS (lower bound): 0.75-0.79.

**Tape-only (pair-distributed) forms** (trajectory measured with the defective ruler, below):
- They exceed 5% of the population at some snapshot in 5/6 runs, peaking at 26%. They never exceed 50%.
- Corrected final shares are 0-3% in every run.

**Reading:** the distributed form is a recurring, transient MINORITY, not a takeover. X-DISTRIB-GAME tests whether
it has any selective edge.

**Provisional:** the trajectory waves cannot be re-scored, because intermediate non-dominant genomes were not saved.

## Defects (continued)

**DEF-FH-4 (ruler; it biased a readout, not a verdict):** the on-tape ruler (`fh._tape_self`, `arch.tape_answer`)
fed the episode to the scored side only. The partner ran without inputs, so IN returned 0 and it took the
answer-before-read branch. In the ONTAPE world BOTH sides get episodes.
- **Found in X-ONTAPE-LONG seed 45300004.** "TCS 0.25 vs offline CS 0.79". The dominant genomes carry a mutated
  answer-before-read branch (byte 35 = DF). Executed by an input-less first mover, it wrecks the second half before
  that half can answer.
- **Repaired:** both contexts get the episode. Regression TR-2: this genome scores 0.5 under the old ruler and >= 0.75
  under the corrected one; the controls are unchanged; the invader INV scores 1.0 under both.
- **Post-hoc rescoring** (`rescore_tape.py`; saved genomes only, so corrected TCS is a lower bound):
  - C-ONTAPE-MAINTAIN ONTAPE runs: corrected TCS >= 0.69-0.85 (was 0.70-0.81). ONTAPE_RND and the negatives stay at 0.
    The frozen verdict CONFIRMED stands and is unaffected.
  - X-ONTAPE-LONG seed 45300004: corrected TCS >= 0.77. Its "collapse" was the artifact.

**Correction to F4 ("vestigial" read-order detector):** the answer-before-read branch is dead only under the offline
scorer, where key >= 1 makes it rare. On the pair TAPE, in every world without task inputs (DIR / VETO / RND: IN
returns 0), it is the path executed on EVERY interaction. Its mutations therefore change tape behavior. "Vestigial"
applies to the offline task only.

## C3. C-ARCH-COMPETE: NOT_CONFIRMED (CONFIRM lane; fresh seeds 45_400_000+; frozen at fb072bba5)

**Result:**
- 9 of 10 runs ended with competence. The CT_W family held the majority in 7; the rule needed 8.
- **Verdict: NOT_CONFIRMED. The rule is not re-cut.**

**Post-verdict mining** (descriptive only; dominant-family series):
- In both CT_UA-won runs, CT_UA was dominant from epoch 10 on, and CT_W ended at 0%. CT_W's single founder lineage
  was lost before it could compete.
- In the CT_W-won runs, CT_UA leads early and CT_W takes over between epochs 100 and 500.

**Reading:**
- Robust-architecture substitution occurs when both founders establish. Single-founder establishment is a lottery
  that the frozen rule did not condition on.
- F10 therefore stays EXPLORE-level, and the mechanism is NOT promoted.
- A better confirm design would plant several copies of each architecture, so that establishment is not a lottery.
  It is not run here, to avoid adaptive re-testing in the same window.

## F12. X-DIR-7AE3: SIGNAL. The direction-vs-rate result generalizes to a second world (scope test, 36 runs)

**The 7ae3 cell:** Z8_64 representation, where OPERAND mutation hits real operand bytes only, so the world never
mutates opcodes; WELL_MIXED. Otherwise STATIC ADD37, CONST 0.15, 2000 epochs, as in ffa6.

| arm | maintained (established runs) | final CS | median last epoch with CS > 0 |
|---|---|---|---|
| DIR015 | 12/12 | 0.95-0.99 | 2000 |
| RND015 | 0/9 | -- | 900 (ffa6: about 400) |
| CT_U under DIR | 0/4 | 0 | -- |
| COPY_ONLY under DIR | 0/4 | 0 | -- |

- **The leak model predicts both shifts.** Opcode-sparing mutation shrinks the routine's destructive target, which
  gives a higher maintained equilibrium (0.95-0.99, against 0.91-0.95 in ffa6) and slower neutral loss without
  selection (900 against 400).
- **Scope:** the principle (function persists iff competence biases copy-exchange DIRECTION) holds across two pair-tape
  worlds with different mutation geometry and structure. It is untested outside pair-tape replication.

## F13. X-DISTRIB-GAME: CLEAN_NULL. The pair-distributed form (INV) is a NEUTRAL alternative implementation (24 runs)

**Setup:** ONTAPE, CONST 0.15, 2000 epochs; 6 seeds paired across arms. 8 rare vs about 191 common planted.
- INV share is inferred from offline CS: INV has u = 0 offline, and the on-tape readout was off in this experiment, so
  its genomes were not saved.
- The marker share is read directly (byte 60) among competent genomes.

| arm | outcome by epoch 2000 |
|---|---|
| INV rare | lost like the rare marker: final CS 0.69-0.88 (NEU_RARE 0.74-0.84); the CS dip at epoch 200 is the same in both arms |
| MARK rare | lost (about 0% of competents in 6/6) |
| INV common | holds: offline CS stays about 0 in 5/6 (the INV family keeps the population); in 1/6 competence returned late (0.60 at epoch 2000) |
| MARK common | holds (97-100% of competents) |

**Reading:**
- No edge from rare and no disadvantage when common: INV behaves as a neutral variant of CT_UA under on-tape
  selection.
- A population whose function is entirely PAIR-DISTRIBUTED (each genome answers through its partner's code) persists
  for 2000 epochs. This is inferred from the population staying INV-dominated under ONTAPE selection; TCS was not
  measured in this experiment.
- The distributed architecture is an alternative stable state reached by drift, not a selected improvement.
- **Killed:** "pair-distributed function spreads because it is advantaged" (together with the counter-copy kill).

## F14. X-REPUTATION: SIGNAL. Reputation reset explains ONTAPE's shallow genealogies (24 runs, paired; corrected tape ruler)

| arm | median causal depth | INHERIT deeper (paired seeds) | on-tape function maintained (TCS >= 0.10) | final TCS |
|---|---|---|---|---|
| RESET (default) | 42.5 | -- | 9/9 established | 0.73-0.83 |
| INHERIT (a converted half takes its donor's score) | 116.5 | 9/9 established pairs (3 seeds established in neither arm) | 9/9 established | 0.82-0.89 |

- **The age-structured-reputation hypothesis (F8) is supported.** Resetting the score on conversion lets long-scored
  elders out-prioritize their own fresh copies. Copying concentrates in old donors, and genealogies stay short.
- **Exchange advantage:** median 2.0 (RESET) against 1.7 (INHERIT).

**Secondary (descriptive, not a declared classification):** heritable reputation strongly increases PAIR-DISTRIBUTED
function.

| arm | final tape-only share | maximum over the run | runs exceeding 0.5 |
|---|---|---|---|
| RESET | <= 0.12 | 0.26 | 0/9 |
| INHERIT | up to 0.70 | 0.70 | 4/9 |

- Offline CS therefore swings widely under INHERIT (0.17-0.89) while TCS stays high.
- This is consistent with F13 (the distributed form is neutral): deeper genealogies mean larger neutral sweeps.
- **Weak signal, not chased.** A confirm would need a frozen design with tape-only share as its endpoint.
