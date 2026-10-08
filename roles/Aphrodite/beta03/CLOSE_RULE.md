# BETA-03 CLOSE RULE (frozen; amendment A1 of the close-decision table)

Supersedes the decision table in beta03/MIGRATION_DESIGN_DRAFT.md s5, following the red team
(beta03/reviews/REDTEAM_MIGRATION_DECISION.md: B1-B3, M1-M3, M5, m4, m5).
- **Frozen before any E1, E2 or E5-N outcome was read.** The E1 recipient rows existing at freeze time are ledgered by
  line count and sha256; they were not read.
- **Own file, own sha:** design edits to the migration draft do NOT amend this rule.

## Fixed input
**E5-H (structured-world R8) = INSTRUMENT_UNVALIDATED.**
- The known-positive oracle depth-two control fails under the frozen W5P observation rule.
- The single pre-registered cheap repair (O1) failed its frozen criterion, 0/3.

## Rule (first match wins; exhaustive)
Inputs are the E5-N label after E6 (beta03/windows/E5N_PREREG.md + A1) and E6's status.

| # | Condition | Recommendation |
|---|---|---|
| 1 | E5-N R8_UNDER_PROMOTION = **YES** (E6 confirmed) | **CONTINUE_CURRENT_ENGINE** |
| 2 | E5-N = **YES_PENDING_E6** and E6 not completed by the hard stop | **CONTINUE_CURRENT_ENGINE (PROVISIONAL: E6 pending)** |
| 3 | E5-N = **MEASUREMENT_FAILED**, OR NO_AFTER_ATTACK where the ONLY failed E6 component is the label-scramble invariance (c) | **INSTRUMENT_REPAIR_REQUIRED** |
| 4 | Every other case | **MIGRATE_SUBSTRATE** |

"Every other case" in row 4 includes:
- NO, with any channel qualifier;
- INSTRUMENT_UNVALIDATED (natural-world positive control fails);
- NO_AFTER_ATTACK on any other component;
- NOT_RUN (time or compute).

## Mandatory fields with MIGRATE_SUBSTRATE (red team B3)
- `BASIS = OUTCOME_C_APPARATUS_LIMIT`. This is the operator's closing-note Outcome C: a W5P instrument failure whose
  one cheap repair failed, so stop rather than coerce the one-hole grammar.
- `S10_KILL_CRITERION = NOT_MET`. Directive s10's retirement precondition ("W5P instrument qualified, second-level
  mechanisms independently attainable") is NOT satisfied, because the known-positive control failed.
- `KILL_CRITERION_HESTIA_PROXY = <E5-N field>`. It is a proxy: g11 acceptance (not MDL), one inheritance step, and the
  structured instrument is not validated.
- **Qualifiers:**
  - E5-N P1 significance and sign;
  - channel status;
  - attributed depth-2 fraction;
  - NOT_RUN where applicable;
  - E1 labels;
  - E2 labels.
- **Banned wordings:** "no second rung exists", "recursion refuted", "R8 disproved". **Q5 and Q6 must be answered
  "not established in this engine"**, unless row 1 applies.

## Separation (red team M1, M3)
- **E1 and E2 outcomes never change the recommendation.**
- They set qualifiers and TFS-1 design obligations only. For example:
  - E1 SATURATION means the R8 endpoint must use common-residual opportunity sets on any substrate;
  - E2 g12 YES/NO decides whether MDL/reach acceptance is the default comparator.
- **Only s13 labels are emitted,** plus qualifiers.
