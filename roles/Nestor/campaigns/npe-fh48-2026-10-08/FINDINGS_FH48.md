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
