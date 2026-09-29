# Self-location in NPE copiers: transplant tests

Delegate for Nestor, npe-arc3-2026-09-28, 2026-09-28. This is computational artificial life: integer programs
on the z8 VM, nothing biological. The tests only read the corpus and the W1/c9x/z80atlas code. Every file was
written into this directory. At most 2 worker processes were used.

## Answer in brief

- **Nearly every copier gets its position from the environment.**
  - 280 of 280 SELF-independent competent copiers stop copying once the tape position moves by 16 bytes or
    more (T1). No register seeding at the new position brings them back (T3 D32).
  - Their source and destination are absolute tape addresses. These come from immediates and/or the fresh
    zero registers, and the 128-byte wrap folds them onto the right place.
  - The code copies "bytes 0..63 to 64..127", or the reverse, **whoever runs it**. When a blank partner's
    NOP slide runs into the donor's code, the partner copies the donor itself. That is the main reason
    copiers fail with a blank partner (see T4).
- **Where the self-location comes from:**

  | source | what supplies it |
  |---|---|
  | the tape coordinate (base 0 or 64) and the 128-byte fold | environment |
  | the fresh zero registers, for about half of the copiers | environment |
  | the SELF value (base, length), for 52 copiers that call SELF | organism asks, world computes |
  | sense and the partner's own execution | never used: 0 of 332 fail when sense is flipped, 0 of 332 when the partner does not execute |

- **Architecture classes predict little.**
  - The self-location class is **one class** among SELF-independent copiers: TAPE_ANCHORED, 280 of 280.
    So among them it predicts nothing.
  - Among SELF-dependent copiers the three classes map onto roughly three seed groups (lineage caveat
    below).
- **The one useful predictor is the initialization transplant (STATE_FREE):** the copier still works from
  random or constant registers.
  - It predicts state robustness: SELF_POISON in 3 of 179 STATE_FREE copiers vs 74 of 143 others (Fisher
    p = 1.5e-28). At lineage level it is 1 of 28 vs 28 of 46.
  - It does **not** predict SELF-dependence: 27 of 182 vs 25 of 150.
- I stopped cataloguing there.
- **What changes when self-location is internalized.** 2 genomes, both SELF-dependent, both from seed
  16000026, share one motif: SELF, then `LD D,L; LD E,D`, then an in-place LDIR, then an LDDR "copy behind
  me" that smears with period 64. They are the only LOCATORs.
  - They copy at every tested offset, on the other half, on 256- and 192-byte tapes and from random
    registers, and they are never self-poisoned.
  - Internalized location makes **position-free, state-free, geometry-tolerant reproduction** possible. It
    exists in 2 of 332 copiers (1 motif), so it is rare, not typical.

## Declarations, validation, controls

- **Declarations.** `DECLARATIONS.md` was written before any transplant ran. It holds:
  - the per-test ORGANISM-vs-ENVIRONMENT readings;
  - the class rules;
  - the predictive tests;
  - the expectations E1 to E4.
- **Validation** (`validation.json`). GP11 is my generalized P-11 assay: the tape layout, execution order,
  sense, start state, entry point and blank or non-executing partner are all parameters. In the standard
  layout, with p11's own seed tags, it reproduces `p11.assay` in **288 of 288** trials (48 genomes x
  3 seeds x 2 sides, 132 of them passes).
- **Positive controls** (`controls.py`, `controls.json`). Hand-built copiers, padded with NOPs. The expected
  classes were declared in the script's docstring before it ran.
  - C_LOCATOR (SELF, then DE = HL + 64) came out LOCATOR and STATE_FREE, as expected.
  - C_TAPE (all immediates) came out TAPE_ANCHORED and STATE_FREE, as expected.
  - C_ZERO_BOTH (E derived from fresh E) came out STATE_ANCHORED, restored by PTRSHIFT, and not
    STATE_FREE, as expected.
  - **C_ZERO_HL_IMM_E was expected to be TAPE_ANCHORED and came out STATE_ANCHORED.** It passes D32_HL_SELF
    at 0.58. Cause: with a long count and dst - src = 32, the copy smears with period 32, and this control
    genome is 60 of 64 zero bytes, so fidelity is easy to reach. This is an artefact of a sparse control;
    real genomes have a median of 1 zero byte. It shows that the D32 rescue can over-fire on
    low-complexity genomes.
  - All four classes are shown able to fire.

## Methods

- **Sample** (`sample.json`). 355 genomes from `q1_partial.jsonl`:
  - all 55 competent SELF-dependent genomes;
  - the 29 competent SELF-independent first donors;
  - 271 stratified competent SELF-independent genomes. Strata are cell x VM x origin experiment, with a
    water-filling quota of 61 per stratum, seed 20260928.

  332 pass REF at >= 0.5 and are **eligible**: 52 SELF-dependent and 280 SELF-independent. The 23
  ineligible genomes are assay noise near 0.5.
- **REF** is the standard P-11 assay on the genome's home side. Home is side 0 for 277 genomes and side 1
  for 55. Every condition changes one factor from REF.
- **Seeds.** K = 12 seeds per condition, each seed a 3-draw GP11 majority. Victim draws are shared across
  conditions, so comparisons are paired. pass means rate >= 0.5.
- **(a) and (b)** use run_ss.py logic re-implemented in `selfloc.selfstate`, run on the genome's own VM:
  - k = 0, 1, 2 prior blank-partner executions, 10 seeds x 2 sides;
  - scored with `run_nc.copies`, which is predecessor acceptance AND P-11.
- **(c)** comes from q1.
- **Files:**

  | file | content |
  |---|---|
  | `selfloc.py` | sample, validate, run |
  | `analyze.py` | produces `selfloc_results.json`, with every genome's rates, class, flags and self-state rates |
  | `trace_locator.py` | produces `trace_locator.txt` |
  | `diag_blank.py` | produces `diag_blank.json` |
  | `run.log` | the log of the run |

## Per-test results (eligible n = 332: 52 SELF-dependent / 280 SELF-independent; pass counts)

| condition | SELF-dep | SELF-indep | reading |
|---|---|---|---|
| REF | 52 | 280 | |
| STD_OTHER (standard assay, other side) | 6 | **0** | no SELF-free copier works from both sides |
| T1 d = 1 / 4 | 3 / 4 | 173 / 145 | inside the anchor tolerance (a few wrong bytes still pass 90%) |
| T1 d = 8 / 16 / 32 / 48 | 2 / 2 / 1 / 2 | 13 / **0 / 0 / 0** | position is supplied by the tape |
| T1 d = 64 (other half, home order and sense) | 9 | **0** | |
| G256_ADJ (partner at +64 on a 256-byte tape) | 23 | 99 | 210 of 332 need the 128 fold |
| G256_HALF (partner at +128) | 10 | 86 | 77 SELF-indep pass both: the destination is an immediate whose bit 7 the 128 tape ignored |
| G256_HI (donor at 128+h) | 31 | 19 | SELF supplies the high position |
| G192_ADJ (192-byte tape, not a power of two) | 10 | 30 | |
| I_CONST55 / I_CONSTFF / I_RAND | 27 / 29 / 27 | 163 / 165 / 163 | about 55% set every register they use |
| I_HL_PARTNER / I_SELFPTRS | 52 / 52 | 262 / 259 | the initial HL is almost never read |
| D32_HL_SELF / DE_PARTNER / HLDE / PTRSHIFT | 1 / 17 / 18 / 17 | **0 / 0 / 0 / 0** | only SELF-dependent lineage 16000029 is rescued by re-supplying DE |
| P_NOEXEC (partner does not execute) | 52 | 280 | the partner's execution is never needed |
| P_BLANK (blank partner) | 51 | 225 | 56 fail, mostly C5: see below |
| SENSE_FLIP | 52 | 280 | the side cue is never read |
| ORDER_FLIP | 33 | 86 | 213 fail: the random victim's execution scribbles (environmental interference, not a cue) |
| ROT +1 / +4 / +16, entry at base | 48 / 41 / 37 | 164 / 130 / 45 | |
| ROT +1 / +4 / +16, entry follows | 49 / 43 / 41 | 178 / 154 / 78 | |
| ROT -4, entry follows | 0 | 3 | design defect: see Deviations |
| P_SELF (partner = copy of self; descriptive) | stays self in 317 of 332 | | |

**T4, blank partner** (`diag_blank.json`, 56 failures). The failing criteria are:

| failing criteria | genomes |
|---|---|
| C5 only | 25 |
| C4 and C5 | 22 |
| C2, C4 and C5 | 5 |
| C2 and C4 | 4 |

- C5 fails in 52 of 56. That is the donor-disabled control reaching >= 90% fidelity.
- Mechanism: the blank partner is a NOP slide. It runs through its own slot, wraps onto the donor's code
  and executes it, and the tape-anchored program then copies the donor into the partner **under the
  partner's own execution context**.
- This is an executor transplant that happened by accident, and it is the clearest causal evidence here:
  the copy's where and from-where do not depend on who runs it.
- The declared PARTNER_REL flag therefore does not mean "partner-relative". No copier needs the partner
  (P_NOEXEC 332 of 332).

**T5, rotation.**
- A +1 rotation is tolerated by about two thirds of copiers. Tape-anchored copiers still copy the slot, so
  what breaks is the code itself: bytes shifted past the copy, or absolute jumps.
- Larger rotations break most copiers. SELF-dependent copiers are more tolerant: 41 of 52 pass +16
  follow, against 78 of 280 SELF-independent.

## Classes (by transplant only; declared rules)

| class | definition | n (SELF-dep / SELF-indep) | lineages (origin runs) |
|---|---|---|---|
| LOCATOR | pass >= 5 of 6 offsets d in {1..48} | 2 / 0 | 2 (seed 16000026: x_dd_dense_copy and x_dd_establish) |
| PARTIAL | pass d = 32 but not LOCATOR | 0 / 0 | |
| STATE_ANCHORED | fail d = 32; a D32 register seeding rescues | 17 / 0 | 1 (x_dd_dense_copy 16000029) |
| TAPE_ANCHORED | fail d = 32 and all D32 seedings | 33 / 280 | 75 |

**Secondary flags** (eligible 332):
- STATE_FREE: 182 (LOCATOR 2, TAPE 180).
- WRAP_DEPENDENT (fail G256_ADJ): 210.
- SENSE_READ: 0.
- ORDER_DEP: 213.
- "PARTNER_REL": 56. These are the blank-slide cases, not true partner relativity.
- POS_INDEP_CODE: 113. Weakened by the ROT-4 defect.

**Operational reading of the classes:**
- **TAPE_ANCHORED + STATE_FREE (180): "fixed-address copier".** It uses immediates only, and position comes
  from where the world put it.
- **TAPE_ANCHORED, not STATE_FREE (133): "fresh-zero + fixed-address copier".** Position comes from the
  tape and from the zero start state (the Q4 motif: fresh HL = own base 0, E immediate).
- **STATE_ANCHORED (17, SELF-dependent).** SELF supplies HL; the destination DE comes from fresh zeros.
- **LOCATOR (2, SELF-dependent).** SELF supplies the base. DE is derived from it (`LD D,L; LD E,D`, so
  DE mod 128 = base). An LDDR from base + 64 down to base then writes each own byte i to base - 64 + i,
  which is the partner under any tape length that is a multiple of 64, smearing periodically.
  (`trace_locator.txt`: identical register values at bases 0, 32 and 64; partner fidelity 0.98 at all
  three.)
- **No PC-relative locator is possible:** GETPC is disabled by the ops mask 0x2A.

## Does class predict anything? (contingency tables, eligible genomes)

**(a) State robustness** (SELF_POISON if rate_1 < 0.25 rate_0):

| class | SELF_POISON | SELF_OK | unmeasurable |
|---|---|---|---|
| LOCATOR | 0 | 2 | 0 |
| STATE_ANCHORED | 17 | 0 | 0 |
| TAPE_ANCHORED | 60 | 243 | 10 |
| TAPE_ANCHORED, STATE_FREE | 3 | 174 | 3 |
| TAPE_ANCHORED, not STATE_FREE | 57 | 69 | 7 |
| **STATE_FREE (all)** | **3** | **176** | 3 |
| **not STATE_FREE (all)** | **74** | **69** | 7 |

- **STATE_FREE vs poison:** Fisher p = 1.5e-28. Lineage-level majority vote: 1 of 28 STATE_FREE lineages
  are poisoned, against 28 of 46 others.
- **STATE_ANCHORED vs TAPE_ANCHORED, poison:** 17 of 17 vs 60 of 303, p = 7e-12. Restricted to
  non-STATE_FREE genomes: 17 of 17 vs 57 of 126, p = 6e-6.
  - **But STATE_ANCHORED is one lineage (16000029).** Among SELF-independent copiers, where there are no
    STATE_ANCHORED genomes, the class contrast is undefined (p = 1).
- **SELF-dependence vs poison:** 24 of 52 vs 53 of 270, p = 1.3e-4. This is driven by the 16000029
  lineage.

**(b) Competence under reset:** run_nc.copies rate_0 from fresh, both sides pooled.

| | rate_0 >= 0.5 | rate_0 >= 0.25 |
|---|---|---|
| STATE_FREE | 117 of 182 | 177 of 182 |
| not STATE_FREE | 64 of 150 | 130 of 150 |
| LOCATOR | 2 of 2 | 2 of 2 |
| STATE_ANCHORED | 1 of 17 | 15 of 17 |
| TAPE_ANCHORED | 178 of 313 | 290 of 313 |

- At the declared bar (rate_0 >= 0.5) the STATE_FREE contrast has Fisher p = 1.0e-4.
- The declared bar of 0.5 is nearly unattainable for one-sided copiers, because rate_0 pools both sides
  and a one-sided copier scores at most 0.5 (caveat). The rate_0 >= 0.25 column is a post-hoc normalized
  bar, with no Fisher test computed.

**(c) SELF-dependence:**
- By class: LOCATOR 2 of 2, STATE_ANCHORED 17 of 17, TAPE_ANCHORED 33 of 313. This is circular in part,
  since only SELF can give a VM-internal locator. E3 held: every LOCATOR is SELF-dependent.
- By STATE_FREE: 27 of 182 vs 25 of 150, so there is no association.
- Calling SELF does **not** by itself internalize location: 33 of 52 SELF-dependent copiers are still
  TAPE_ANCHORED. SELF supplies the source, but the destination is an absolute immediate.

**Verdict on the expectations:**

| expectation | result |
|---|---|
| E1 | confirmed |
| E2 | confirmed, but it rests on 1 lineage |
| E3 | confirmed |
| E4 | confirmed, far beyond expectation: 313 of 332 |

**Verdict on cataloguing:** the self-location classes add nothing beyond STATE_FREE for (a), and nothing
beyond SELF-dependence and lineage for (c). The predictive content sits in one transplant, initialization.
Cataloguing stopped.

## Conclusions

1. **What the organism supplies.** The bytes, including the choice of which registers to overwrite, and,
   for 52 genomes, the request to SELF.
   **What the environment supplies:**
   - the absolute base address, which fixes the position for 313 of 332;
   - the 128-byte fold, which turns "some address with low 7 bits = 64" into "the partner", for 210 of 332;
   - the fresh zero state, for about 45%;
   - on request, the SELF value.

   Sense and partner execution are never used. Execution order matters only through interference.
2. **Robustness to state follows from STATE_FREE.** Whether the copier overwrites every register it reads
   predicts it. Where the anchor comes from (tape vs state) is secondary and confounded with lineage.
3. **Capabilities unlocked by internalized location.** Seen in 1 motif, 2 genomes, so this is an existence
   proof, not a rate:
   - copying from any tape offset, including the other half (T1 d = 64 at 1.0);
   - copying on tapes of 192 and 256 bytes;
   - copying from random registers;
   - no self-poisoning across repeated executions (self-state rates 0.5, 0.5, 0.5 and 0.5, 0.75, 0.70).

   Tape-anchored copiers can do none of the first two. Any change of placement would kill them: slot
   shuffling, larger tapes, or more than two slots.
4. **Supplied location is not an organism property.** Tape-anchored code copies donor to partner even when
   the partner executes it (the blank-slide C5 failures). In tape-anchored copiers, "self" is a place on
   the tape, not the program.

## Deviations and caveats

- **K and seeds.** K was raised from 8 to 12 and SS seeds from 5 to 10, after a 2-genome timing test and
  before the full run, for statistical power.
- **Added after the declaration.** The positive controls (their expectations were declared in the script
  first), `diag_blank.py` and `trace_locator.py`.
- **ROT-4_FOLLOW** is a design defect. With the entry at base + 60, the program runs 4 bytes and then
  leaves the slot. The same kind of truncation, of r bytes, affects the +r follow rotations. The
  POS_INDEP_CODE flag is weak because of this.
- **PARTNER_REL is mis-specified**, as explained under T4.
- **The D32 rescue can over-fire** on low-complexity genomes (the C_ZERO_HL_IMM_E control).
- **Lineage non-independence.** STATE_ANCHORED is 1 run, and LOCATOR is 2 genomes sharing seed 16000026
  across two experiments (no descent claim is made). The 280 SELF-independent genomes come from 74
  runs. The sample caps each stratum, not each run.
- **Scope.** T1 and T3 displacement was tested at a single displaced offset (32) for rescue. Tapes other
  than 128, 192 and 256 were not tested. G256_HI failures of the natural LOCATORs (0.0) were not traced.
- **Assay noise.** K = 12 at a 0.5 bar leaves genomes near threshold noisy. Classification uses 6 offsets,
  which damps this.
