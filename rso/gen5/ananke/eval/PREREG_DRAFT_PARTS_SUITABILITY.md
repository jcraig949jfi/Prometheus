# DRAFT -- REQUIRES OWNER SIGN-OFF -- NOT FROZEN

# Parts-suitability ladder on Ananke PTE: does a search-acquired A make GATE more accessible?

**Status: DRAFT.** Written by the Observatory (Argus, C-019-T040, 2026-10-15) as the Observatory's half of a jointly
specified experiment. It is a proposal to the owner (Ananke), not a preregistration.
- The Observatory never freezes it. Only the owner can sign it off, amend it or reject it.
- Nothing native runs under it until the owner consents (directive 2026-10-15 s2A; comms #2083, #2249).
- The worlds, search, operators, representation and budgets named here are the owner's lane. Where this text names
  one, it is a requirement or a question for the owner, never a design the Observatory imposes.

**Pins.** Owner records: `origin/ananke/p2b-2026-10-05` @ `f58362c5e` (PREREG_PTE_C4.md, RESULT_PTE_C4.md,
PREREG_PTE_C5T.md, DLIB_C4.json, admission_R4.json, LIBRARY_C4.json). Engine: `prometheus/ananke/` at main
`0546be826` (unchanged on the owner's branch). Observatory instrument: `rso/gen5/ananke/eval/` on branch
`argus/c019-t040` (see README.md for the qualification evidence).

**Not used, by design.** The owner's champion populations (pops_C4T.tar, pops_C4D.tar) and any C5T output. Owner
consent is pending; this draft is written without them.

## 1. Question and why this design

The directive's precursor question (s3) is: does an acquired mechanism reduce the cost of acquiring a second capability
under matched search and compute?

C4 already answered one version of it, for one library:
- the search-acquired RELAY/HOLD modules gave 0/32 for GATE;
- no library gave 0/32;
- the owner's DESIGNED GATE halves gave 2/32 (CP95 .008-.208).

The owner's own reading is that the evolved one-stage modules were the WRONG parts (RESULT_PTE_C4.md s5). This draft
tests the RIGHT parts, acquired by search rather than inserted:
- **A** = GATE's own two halves: a context latch, and a cue relay x context product. They are acquired by the owner's
  native search on owner-authored one-stage worlds.
- **B** = GATE at the C4 cells.

A positive result would separate "the evolved modules were the wrong parts" from "search cannot assemble any parts".
It is the directive's s13 example, almost exactly.

## 2. The six claims, kept separate (directive s3)

| # | claim | what this design can show | what it cannot |
|---|---|---|---|
| 1 | Expressibility | already shown: gate_plant TRUE at 4 cells; DLIB halves reassembled TRUE (owner; reproduced independently in T040 KA_TABLE) | -- |
| 2 | World demand | GATE rewards B: plant TRUE, null / relay_flood / hold_latch FALSE (reproduced) | that the half-task worlds demand ONLY their half (Rung-1 leakage checks, s4) |
| 3 | Accessibility | P(B within budget) per arm, with exact CIs and right-censored hitting times | anything about budgets not run |
| 4 | Reuse | REUSE vs CONTROL, paired on (cell, idx) | reuse at power below the calibration gate (s6.3) |
| 5 | Attribution | Rung-4 battery on every competent REUSE champion: library lines NOP, USE-DISABLED (bytes kept), substitute, transplant, register zero, zero communication | attribution for champions that were never competent |
| 6 | Discovery | A was acquired by the declared search on declared worlds, recorded per module (source search, generation, worlds) | that the half-task WORLDS were not themselves designed with GATE in mind: they are. Report this as "discovery of parts on designed curricula", not open-ended discovery |

**Claim 6 is narrowed by construction.** Designed half-task worlds make the parts' DEMAND designed, even though their
ACQUISITION is searched. The result may qualify claims 1-5 while claim 6 stays at this narrower form. The report must
say so in its first paragraph.

## 3. Division of labour (directive s2A)

| Owner (Ananke) | Observatory |
|---|---|
| the half-task worlds (CTX-LATCH, CUE-x-CTX); native search, operators, representation (R4, OPD / OPDL), budgets, seeds; the library builder; running every native search | independent evaluation on the CPU oracle (T040 evaluator, conformance pinned to the owner's admission numbers); Rung-4 attribution; accessibility statistics; completeness manifest and custody; the adversarial kit; scientific interpretation of the joint result |

The Observatory supplies no solution to any evolving organism. It never writes in `prometheus/ananke/` or
`roles/Ananke/`.

## 4. Ladder

**Rung 0 (DONE, Observatory, T040).** Known answers re-checked independently on the CPU oracle at the owner's world
seeds (qual/KA_TABLE.json):
- 40 admission readings, with mean and lo99 matched to 1e-9;
- the DLIB live lines, and the halves reassembled and alone;
- 56 module-alone checks;
- hold_latch FALSE on GATE (new).

**Rung 1 (OWNER).** Acquire A by native search on two owner-authored one-stage worlds. **Requirements** (the Observatory
checks them before any target search; each is a known-answer row):
- (a) The CTX-LATCH world admits the D-LIB CONTEXT half, placed at its own lines, as a positive control. It rejects
  the null genome, and it rejects the CUE half alone.
- (b) The CUE-x-CTX world admits the CUE half under the world's own context supply, and rejects the CONTEXT half
  alone.
- (c) Neither world contains a GATE trial. gate_plant is scored on both worlds and the score is reported: LEAKAGE is
  the case where the composed solution is the cheapest solution of a half-world.
- (d) The budget, the number of independent searches and the success frequency are recorded; so are evaluations to
  first success, the information the search could use, and mechanism diversity (live-line multiset per competent
  champion).
- (e) If a half is NOT acquired within the registered budget, that result is preserved. A designed half is NOT
  substituted silently. The run then degrades to "constructed-A accessibility calibration", labelled as such
  (directive s4 Rung 1).

**Rung 2 (OWNER builds, OBSERVATORY verifies).** The library is the live lines of the lowest-idx competent champion per
(cell, half), as in `build_library.py`. It is frozen with hashes. The Observatory verifies:
- each module ALONE is TRUE on its half-world and FALSE on GATE;
- the two modules re-assembled are reported on GATE (descriptive; the arm decides, not this check);
- module bytes equal the frozen library (custody, `owner.py`-style blob pins).

**Rung 3 (OWNER runs; arms frozen by the owner).** GATE at the 4 admitted cells, idx 0..n-1, R4. All arms of one
(cell, idx) share the gen-0 population and the training worlds (C4 seed rule), so (cell, idx) is the paired unit.

| arm | library | budget | purpose |
|---|---|---|---|
| CONTROL | none (C4 arm B: R4 / OPD) | G | the baseline accessibility |
| REUSE | the search-acquired halves (R4 / OPDL, P_LIB .15, renaming as C4) | G | the claim |
| SHAM-MISMATCH | the C4 RELAY/HOLD library (LIBRARY_C4.json) | G | a library of real but wrong parts (C4: 0/32 at G = 36) |
| SHAM-SCRAMBLED | the REUSE modules, size-matched, line order permuted and register fields deranged (the deterministic permutation is in the freeze) | G | same bytes budget, no function; the Observatory verifies FALSE alone on each half-world before use, and a sham that is still functional is refused |
| COMPUTE-MATCHED | none | G + G_L | the extra search effort REUSE received. G_L = the L-stage generations spent acquiring the halves, amortised per REUSE search; the unamortised value is reported as a sensitivity |
| CONSTRUCTED-POSITIVE | the D-LIB designed halves (C4 arm D) | G | calibration: can the instrument see an advantage at all? |

**Rung 4 (OBSERVATORY, on the oracle; no search).** Every competent champion of every arm gets the battery of
`mechanics.py`, on 256 fresh worlds from the Observatory's namespace:
- library lines NOP;
- **USE-DISABLED**: library bytes kept and executed, writes redirected to the dead O.chan;
- library lines substituted by lesioned twins;
- transplant of the library lines into fresh genomes;
- register zero S0/S1/S2;
- zero communication;
- context off.

The owner's 12-generation transplant GA is optional and native.

## 5. Endpoints and analysis (frozen at sign-off, before any target row)

- **Primary.** P(B within budget G), REUSE vs CONTROL.
  - Test: exact one-sided McNemar on the (cell, idx) pairs (`access.paired_binary`), alpha .05.
  - B = the frozen GATE ruler (RELAY-mh) on the search's held worlds. It is re-read independently by the Observatory
    on the oracle.
- **Secondary.**
  - Generations to first B, as right-censored data. The native monitor reads the ruler on 64 monitor worlds every 6
    generations, so times are interval-censored at that cadence.
  - The Kaplan-Meier curve, P(B by g) and the restricted mean (never an infinite hitting time).
  - Pooled Fisher one-sided; log-rank (descriptive); the paired first-to-B count (`access.paired_times`).
- **Contrasts**, each paired on (cell, idx), each a separate row in the report:
  - REUSE vs CONTROL;
  - REUSE vs COMPUTE-MATCHED;
  - REUSE vs SHAM-MISMATCH;
  - REUSE vs SHAM-SCRAMBLED;
  - CONSTRUCTED-POSITIVE vs CONTROL (calibration).
  - Holm over the four REUSE contrasts.
- **Attribution endpoint.** Among competent REUSE champions, the fraction whose competence is lost under BOTH library
  NOP and USE-DISABLED. Possession is not use: a champion that keeps competence under USE-DISABLED does not count as
  reuse.
- **Labels (proposed; the owner may change them before sign-off).**
  - **REUSE_IMPROVES_ACCESSIBILITY** requires all of:
    - all four contrasts significant after Holm;
    - the calibration gate met (s6.3);
    - attribution >= 1/2 of competent REUSE champions, with at least 4 competent REUSE champions across >= 2 cells.
  - **REUSE_ADVANTAGE_UNATTRIBUTED**: the contrasts hold but attribution does not.
  - **NO_REUSE_EFFECT_AT_BUDGET**: the calibration gate is met and the primary contrast is not significant. This is a
    budget-relative null, stated with its CP95.
  - **UNDERPOWERED_BY_CALIBRATION**: the calibration gate is not met. No reuse claim either way.
- **Stopping rule.** The run stops only when every planned (arm, cell, idx) has run to G. There is no interim look at
  REUSE vs CONTROL.
  - A wall-clock deadline censors whole idx rounds of every arm equally (C4 rule).
  - Searches that never started are excluded and counted (`access.validate_searches`).
  - The completeness manifest decides whether the set is COMPLETE before any label is read.

## 6. Resources and power (directive s11)

**6.1 Measured throughput.**
- **Observatory, harry1 CPU (no torch).** The oracle runs 15,000-19,700 site-ticks per second per process, with two
  processes running concurrently (the harry1 limit). Measured over the 14,464 world-episodes of the T040 known-answer
  run; 6.5 CPU-h in total; qual/KA_TABLE.json `throughput`.

  | cell | GATE / FLIP episode length | world-episodes per second per process |
  |---|---|---|
  | FLIP-0000 / FLIP-0004 (N = 64) | 208 ticks | 1.1-1.8 |
  | FLIP-0167 (N = 100) | 336 ticks | 0.46 |
  | FLIP-0099 (N = 144) | 336 ticks | 0.31 |

- **Rung-4 battery cost.** One competent champion's battery is 12 interventions x 256 worlds = 3,072
  world-episodes. That is about 30-45 min of one process at N = 64, and about 2.8 h at N = 144.
- **What follows.** The Observatory re-evaluates and attributes competent champions plus a sample. It cannot
  re-evaluate whole populations per generation; per-generation readings must come from the native monitor.
- **Owner, M1 GPU.** About 14.7 searches per hour at 36 generations, population 96, 3 workers
  (PREREG_PTE_C5T.md s0).

**6.2 Counts.**
- 6 arms x 4 cells x n idx searches at budget G, plus the Rung-1 stage of 2 half-worlds x 4 cells x n_L searches.
- At G = 36 and n = 32 (8 per cell), the target stage is 192 searches, about 13 GPU-h.
- Rung 1 at n_L = 8 per (cell, half) is 64 searches, about 4.4 GPU-h. The unknown is whether a half is acquired
  within 36 generations; the L-stage C4 RELAY1H / HOLD acquisition rate was 2-5 of 6.

**6.3 Power: the binding constraint.** Exact one-sided Fisher, alpha .05, power .8; computed with `access.power_fisher`
and `access.min_detectable`.

| p_CONTROL | n = 32 | 48 | 64 | 96 | 128 |
|---|---|---|---|---|---|
| 0 | .203 | .138 | .105 | .070 | .053 |
| 1/32 | .274 | .206 | .171 | .139 | .119 |
| 2/32 | .330 | .263 | .225 | .188 | .168 |
| .10 | .385 | .320 | .283 | .245 | .220 |

(Entries are the smallest detectable p_REUSE.)

- **Calibration gate.** The constructed positive must be detectable against CONTROL; otherwise a REUSE null cannot be
  read.
- At the C4 rates (CONSTRUCTED-POSITIVE 2/32 = .0625 vs CONTROL 0/32), the power to detect the positive is:

  | n per arm | power |
  |---|---|
  | 32 | .05 |
  | 64 | .37 |
  | 96 | .72 |
  | 128 | .91 |

- 80% power needs **107 searches per arm** at 36 generations: 6 arms x 107 = 642 searches, about 44 GPU-h.
- Alternatively, the positive's rate must rise with budget. To detect .15 vs 0 at 80% needs 44 per arm; .20 vs 0
  needs 33 per arm.
- **Therefore the first decision is a budget-calibration stage, not the full comparison.** Run the
  CONSTRUCTED-POSITIVE and CONTROL arms only, at 1-2 larger budgets (for example 72 and 144 generations, the latter
  the C5T budget). Read the positive's rate. Then choose (G, n) from the table above. The C5T outcome (still unreported)
  bears directly on this: it is arm C at 144 generations.

**6.4 Checkpoint / restart.**
- The owner's runner is job-resumable: one job per (arm, cell, idx), with a deadline file and censored rounds.
- The Observatory's evaluation is resumable JSONL keyed by check id (ka_table / mechanics_run pattern), with one row
  per evaluated champion carrying its per-trial arrays.
- A restart never re-runs a finished row. A duplicated row is refused at reduce.

**6.5 Why a longer run could change the conclusion.**
- **The rate is budget-dependent.** C4's D arm reached 2/32 at 36 generations; C5T (4x) is the owner's test of
  whether rates rise. A comparison at a budget where both arms sit at the floor cannot distinguish "reuse does not
  help" from "nothing is reachable yet". Hitting-time curves over a longer budget do distinguish them, via
  Kaplan-Meier separation before the floor lifts.
- **What a longer run cannot change.** A longer run does NOT rescue a design that fails the calibration gate at every
  affordable budget. It also cannot convert designed half-worlds into open-ended discovery (s2, claim 6).

## 7. Falsifiability table (rso/qualify/FALSIFIABILITY.md; one row per claim-critical control)

| control | 1 alternative it stands for | 2 pass observation if the alternative is true | 3 fail observation if false | 4 impossible by construction? | 5 privileged access? | 6 registered near-miss / counterfeit |
|---|---|---|---|---|---|---|
| CONTROL (no library) | the search reaches GATE anyway; the library adds nothing | CONTROL rate ~ REUSE rate | REUSE > CONTROL on paired units | no: CONTROL can reach GATE (the plant is in the genome space: canonical form, admission) | none: same gen-0 population and worlds as REUSE | CONSTRUCTED-POSITIVE vs CONTROL (must separate at the calibration gate) |
| SHAM-MISMATCH (C4 library) | ANY inserted material helps: extra lines, register traffic, operator noise | SHAM ~ REUSE | REUSE > SHAM | no: C4 measured 0/32 for this sham at 36 generations, so it CAN differ | none | KA: every C4 module alone is FALSE on GATE (56/56 reproduced) |
| SHAM-SCRAMBLED | the specific bytes or op multiset of the REUSE modules help, regardless of their function | SHAM ~ REUSE | REUSE > SHAM | must be checked: the sham is refused if it is functional alone on a half-world | the permutation is drawn from a frozen seed; its output is verified FALSE before use | the KA-style "alone" rows on both half-worlds |
| COMPUTE-MATCHED | REUSE's advantage is just the generations spent acquiring A | CM ~ REUSE | REUSE > CM | no | none | G_L is reported amortised and unamortised; the label requires the amortised contrast |
| CONSTRUCTED-POSITIVE | the instrument cannot see an advantage even when the right parts are inserted | CP ~ CONTROL (the calibration gate fails: no reuse reading allowed) | CP > CONTROL | no: C4 arm D reached 2/32 vs 0/32 | CP's parts are designed (calibration, never discovery) | -- |
| Rung-4 USE-DISABLED | possession, not use: the library bytes help by being there (spacing, sinks, inert lines) | competence kept with the bytes present but their writes dead | competence lost | no: fire-tested both ways on plants (a dead line use-disabled gives IDENTICAL output; the plant halves use-disabled read FALSE at 2 cells, all of P_FLIP reads FALSE; MECHANICS_KA.json 32/32 KNOWN) | none: it acts on bytes only | dead-line identity control (test_mechanics) |
| Rung-4 TRANSPLANT / any line move | moving or re-inserting lines is semantically neutral | identical output after a move | output changes | **cell-dependent**: at FLIP-0004 (mut_site .001, wimm 1) in-lifetime Kp mutation hits a hashed INSTRUCTION INDEX, so a pure offset move changed the per-trial output (status still TRUE). Library insertion therefore changes the dynamics of the moved lines there, independent of their function | none | MECHANICS_KA_first_reduce_FAIL.json (the T040 expectation that was wrong) |
| Rung-4 library NOP | the library lines are inert and something else carries B | competence kept | competence lost | no (plant halves NOP: FALSE; a NOP line NOP: identical) | none | as above |
| Ruler (RELAY-mh on GATE) | a cue-only, context-only or once-per-episode policy is read as GATE | relay_flood / hold_latch / null read TRUE | FALSE | no: all three are FALSE at 4 cells (KA) | none | relay_flood (cue without context), hold_latch (context without cue), latch-once (late half) |
| Accessibility table | a missing, duplicated or rewritten search changes the rate | analysis reads a verdict | `validate_searches` refuses it | no (adversary target ananke_access: DROP, DUPLICATE, REWRITE, SCRUB all REJECTED) | `hit`/`time` are recomputed from the checkpoint statuses, never read | the kit's four variants |

**Executable checks to run at sign-off** (rso/qualify/falsifiable.py), each on development data:
- `constant_passes` and `oracle_fails` on the label rule;
- `trusts_derived` on the reduce (tamper the checkpoint statuses and keep `hit`);
- `cannot_emit` on every sham (it must be able to reach B).

## 8. Completeness manifest (template)

The template is `qual/MANIFEST_TEMPLATE_parts_suitability.json`, in the rso.completeness format:
- arms = the six arms; `row_key_fields` = [arm, cell]; `seed_field` = idx;
- one shard per (arm, cell) with its idx list;
- digests "TO_BE_FILLED_AT_FREEZE".

The owner fills in n, G and the source hashes at sign-off and seals it. The Observatory pins its sha256 before reading
any target row.

## 9. Decisions only the owner can make (the Observatory does not presume them)

1. The two half-task worlds: definitions, parameters, and whether CUE-x-CTX supplies the context as SENSE at the
   actuator (GATE's channel) or otherwise.
2. G, n, n_L; whether to run the budget-calibration stage first (recommended, s6.3).
3. Whether SHAM-MISMATCH reuses the C4 0/32 rows (same seeds and budget only) or is re-run at G.
4. The label thresholds in s5.
5. Consent for the Observatory to re-evaluate the C4 / C5T champions (pops_C4T/C4D) on the oracle. This is separate
   from this draft: that is the "instrument would not recognise" question for C4 (COORDINATION.md s3 item 1).
