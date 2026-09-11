# Diomedes -- CALIBRATION ledger

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11 (seeded on the base-role adoption pass). Kept because it
is unflattering. ROLE.md S9.6 gives the totals: ELEVEN substantive predictions
wrong or overstated, FIVE right, four of the five right ones on experiments an
external reviewer specified rather than ones this seat designed. The rows
below are the individually documented items; the mapping of every row to the
11/5 partition with a file-and-line reference is DIOM-08 and is NOT claimed
complete here. Where the source counts one item that decomposes into two
incidents, both incidents are rows.

Columns: id | date | what was predicted or claimed | what was measured |
failure mode | source

## Wrong or overstated

    C-01 | 2026-08-24 | cycle 002 prediction, four clauses | 3 of 4 wrong | prediction | BOOTSTRAP.md S6; CYCLE_002_RESULT_relational_coordinates.md
    C-02 | 2026-08-24 | cycle 003: direction of the effect | direction right, magnitude UNDER-estimated | prediction | BOOTSTRAP.md S6; CYCLE_003_RESULT_split_discriminator.md
    C-03 | 2026-08-25 | cycle 004: ordering of arms; "fits both passably" read as "transfers" | ordering wrong | conflation | BOOTSTRAP.md S6; CYCLE_004_RESULT_relation_type_confound.md
    C-04 | 2026-08-25 | synthesis 001: "75% of the information" | a span ratio of ranking accuracies; AUC does not decompose | claim inflation (variance attribution) | BOOTSTRAP.md S3, S6; SYNTHESIS_001_cycles_001_004.md; feedback_three_claim_inflations
    C-05 | 2026-08-25 | cycle 005 planning: c4 recommended as the replication target | c4 VACUOUS, every outcome field single-valued | preflight omitted a property | BOOTSTRAP.md S6 trap 3; cycle005_preflight.json
    C-06 | 2026-08-25 | finding 1 (state-only residue action-insufficient) as stated before review | KEEP, narrowed: proves action-insufficiency by construction, not Z(x,a) adequacy | overstatement | BOOTSTRAP.md S2, S6; REVIEW_RESPONSE_RESULT_2026-08-25.md
    C-07 | 2026-08-25 | finding 3 (locality / anti-transfer) as stated before review | PROVISIONAL: failure of the tested representation and model family, chart mismatch unexcluded | overstatement | BOOTSTRAP.md S2, S6; REVIEW_RESPONSE_RESULT_2026-08-25.md
    C-08 | 2026-08-25 | a recovery ceiling computed on cycle 004's B cell | quoted as a property of all 552 ordered pairs | wrong-population statistic | ROLE.md S9.6 item 1; REVIEW_ROUND2_CORRECTIONS_2026-08-25.md
    C-09 | 2026-08-25 | one transport aggregate | averaged 288 objective-changing transfers with 264 coordinate-changing ones | wrong-population statistic | ROLE.md S9.6 item 1; REVIEW_ROUND2_CORRECTIONS_2026-08-25.md
    C-10 | 2026-08-25 | a gate on the LOCO margin (0.57 vs 0.5646, err 0.0275) | gate closer to the observed value than its own error; not a gate | gate below measurement error | ROLE.md S9.6 item 2; coordinate_census.py self-test line "LOCO margin 0.0054"
    C-11 | 2026-08-25 | a Spearman gate with bands 0.3 apart on 24 clusters (SE 0.21), written two hours after correcting C-10 | the band that fired was declined | gate below measurement error, repeated | ROLE.md S9.6 item 2; REVIEW_ROUND2_CORRECTIONS_2026-08-25.md
    C-12 | 2026-08-25 | "127 SE below the gate" from a seed-level SE over five re-splits of 24 cells | cell-clustered interval 52x wider and included zero | SE on the wrong unit | ROLE.md S9.6 item 3; REVIEW_RESPONSE_RESULT_2026-08-25.md; feedback_se_on_the_wrong_unit
    C-13 | 2026-08-25 | model failure written as structural impossibility | model failure | claim inflation (modality) | ROLE.md S9.6 item 4; feedback_three_claim_inflations
    C-14 | 2026-08-25 | non-firing prereg branches written as a fired branch | did not fire | claim inflation (branch) | ROLE.md S9.6 item 4; feedback_three_claim_inflations
    C-15 | 2026-08-25 | cycle 005 Arm A: b2 pre-flighted on class balance and oracle form | conditional headroom 0.0265, never checked; the arm was wasted | preflight omitted a property, third firing | BOOTSTRAP.md S4 step 1, S6 trap 3; CYCLE_005_ARMA_RESULT.md
    C-16 | 2026-08-25 | another seat's .git/index.lock judged stale and removed | it belonged to a live seat whose commit landed minutes later | operational, not a prediction; counted here because it was a confident wrong call | ROLE.md S9.8

## Right (partial; DIOM-08 completes the five)

    R-01 | 2026-08-24 | cycle 003 direction | right | BOOTSTRAP.md S6
    R-02 | 2026-08-25 | T1 transport ceiling computed analytically before running: max recovery 10.4% | Arm B best transport 6.03%, inside the ceiling | BOOTSTRAP.md S2; CYCLE_005_RESULT_armB_transport.md
    R-03 | 2026-08-24 | Lane N h1 test: pre-committed KILL on a T0 null, positive expected | strong positive at T0, 0.7392 local vs 0.6254 state-independent ceiling | ROLE.md S7 third bullet; CYCLE_001_RESULT_h1_counterfactual_hunt.md
    R-04 | 2026-08-25 | "both cycle-005 predictions flatter the thread", declared in the prereg | they did; both arms PARK | BOOTSTRAP.md S2; CYCLE_005_PREREG_terminal.md

## Standing rules derived from this ledger (all now base doctrine or seat rule)

    - measure conditional headroom before adopting any population for a
      conditional-structure question; below ~0.05 disqualifies (BOOTSTRAP S6,
      adopted 2026-08-25; enforced by coordinate_census.py)
    - compute the SE before choosing the gate; report the CI beside the verdict
    - the unit that varies is the unit of the SE
    - verdict in {ADEQUATE, INADEQUATE, VACUOUS}, enforced by the module
    - pre-flight EVERY property, not some (three firings)

## 2026-09-11 (this pass)

    No prediction made. One instrument change (planted controls) whose
    expected values were written into the assertions before the run and hit
    exactly: 0.5, 0.0, 0.0, None. That is a test, not a calibration event.
