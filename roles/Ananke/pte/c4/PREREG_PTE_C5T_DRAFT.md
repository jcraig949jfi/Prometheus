# PTE-C5T preregistration (DRAFT): terminal composition assay

Status: DRAFT, written 2026-10-08 while C4-T runs and before any C4-T row was read. It is finalised (FREEZE_C5T.json)
only if the C4 route rule sends the C5 slot here, and its numbers change only for the reasons listed in s6.

**Authority:** the 72h order, s10 (roles/Ananke/prompts/2026-10-07_72h_c3_c4_c5/, 8c48ebfdf).

## 1. When this runs

It runs if C3R and C4 produce no replicated two-stage competence:
- C3R: NO_REPRESENTATION_EFFECT (f2c8351af);
- C4-T: neither COMPOSITION_REACHED nor REUSE_IMPROVES_COMPOSITION for GATE or FLIP.

If C4-T reaches replicated composition, the C5 slot is the turbulence campaign (order s9) instead, and this draft is
withdrawn.

## 2. Question

With the best generic compositional representation and a frozen library of solved one-stage modules, does PTE's search
reach two-stage competence (GATE or FLIP) at a budget 4x that of C4-T?
- If not, the current PTE search architecture is classified as exhausted for richer cognition.
- The physics and instruments are preserved (order s10).

## 3. Design

**Representation and operator:** C4 arm C, i.e. R4 with OPDL. That is duplication-and-divergence plus insertion of
library modules, instantiated with uniform state-register renaming. It is the most compositional GENERIC machinery
built in C4. The designed D-LIB halves are NOT used: they are a diagnostic, not a generic representation.

**Library:** the frozen C4 library LIBRARY_C4.json: 8 modules from solved RELAY1H and HOLD searches. No new library is
built.

**Tasks:** GATE at the 4 admitted cells and FLIP at the 3 admitted cells. The admission is admission_R4.json.

**Seeds:** fresh, so no C4 trajectory is reused: search_seed = H(C5T_NS = 0xC5001007, task id, cell_key, idx),
idx 0..7.

**Budget:** 144 generations (4x C4-T), M32, otherwise the C4 search spec. That gives 56 searches: 32 GATE and 24 FLIP.

**Order:** rounds by idx, cells interleaved, GATE before FLIP within a round. A wall therefore censors whole rounds.

**Projected cost:** about 15 min of GPU throughput per search with 3 workers, so about 14 h. Deadline: launch + 16 h,
read from the freeze file.

**Paired control:** none is run. The 36-generation arms A/B/C of C4-T are the lower-budget reference. This assay asks
an absolute question (any competence?), not a contrast.

## 4. Frozen interpretation

**Competent:** the task ruler is TRUE on the search's held worlds: FLIP uses the B ruler; GATE uses RELAY-mh, i.e.
SIGNAL plus late-half.

**Every competent champion is assayed**, with the same assays as C4:
- fresh held worlds (256);
- swap_v2 on S0, S1, S2 and payload;
- each state register zeroed;
- library-line ablation;
- teacher_off;
- zero_comm.

A champion counts toward a POSITIVE label only if all three hold:
- it is competent on the fresh worlds;
- it loses competence under zero_comm;
- for GATE, it loses competence when the context register is zeroed; for FLIP, when its swap-localised mapping
  carrier is zeroed.

So competence must be shown to use the two stages, not merely be achieved.

**Labels (per task, then overall):**

| label | rule |
|---|---|
| COMPOSITION_REACHED_UNDER_REUSE | >= 4 assay-confirmed competent searches across >= 2 cells, for either task |
| SPARSE_COMPOSITION | 1-3 assay-confirmed competent searches, or all in one cell |
| NO_COMPOSITION | 0 assay-confirmed competent searches |

**Kill rule (order s10).** PTE_SEARCH_ARCHITECTURE_EXHAUSTED_FOR_COMPOSITION if all three hold:
- the library is available: all 8 modules frozen;
- both tasks are NO_COMPOSITION, or at most 1 assay-confirmed competent search in total, among n >= 40 completed
  searches;
- the C4-T arm-C reuse diagnostics show modules present in the champions. MODULE_PRESENT >= .5 rules out the escape
  "the library was never used".

**If MODULE_PRESENT < .5,** the label is instead LIBRARY_NOT_TAKEN_UP, and the kill is NOT issued: the architecture was
not given a fair test of reuse.

**What the kill excludes and what it does not:**
- It excludes, at 95%, a per-search two-stage success rate above about 7% (CP upper bound for 0-1 of 56) at 4x, for this
  representation, operator, library and these cells.
- It does not exclude other search architectures (lifetime learning, archives, curricula), other task families, or
  other physics.

## 5. Threats

- **One library.** Its modules come from one search stage at one physics per cell.
- **Renaming is uniform.** Correct assembly needs compatible register assignments; with 3 registers the chance per
  insertion pair is about 1/9.
- **GATE is a designed rung.**
- **Same author.** Review is requested and is not a gate.

## 6. Allowed changes before the freeze (and only these)

- Withdrawal, if C4 routes to C5 turbulence.
- The deadline, if the C4-T measured throughput differs from the flight by more than 25%. The number of searches
  stays at 56.
- Code defects found by tests, recorded in the freeze.
