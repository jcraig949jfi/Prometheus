# Review 1 -- Archaeon's adjudication (2026-09-28)

**Record:**
- claims: REVIEW_1_CLAIMS.md at 6ff584d14;
- review: review1/REVIEW_1.md;
- counter-examples: review1/cx_*.py (verbatim from the reviewer; transcript at
  C:/Prometheus-data/evidence/attribution_v0_2026-09-28/rev1/).

**Reviewer:** an isolated Claude worker on ubu002 with an empty config and no Archaeon memory, pinned to claude-opus-5-5, working
from Git only. Wall time 10 min, 10:09:53Z-10:20:17Z. Asked to invalidate the claims; told not to reuse Archaeon's coined terms.

**Summary:** the review is right on almost every point. It found:
- one defect that invalidated a headline result (the assay's BEE/NPE material was not descent);
- one that invalidated a claimed finding (D7's uniqueness);
- a validator that certified the conflation it exists to prevent.

All three are accepted and fixed or withdrawn. Nothing below edits the original claims file.

| claim | reviewer | Archaeon's ruling | what changed |
|---|---|---|---|
| R1-1 representation | FAILS as stated | **ACCEPTED** | See details below. |
| R1-2 TH-014 | STANDS WITH CORRECTION | **ACCEPTED** | See details below. |
| R1-3 boundary | FAILS | **ACCEPTED; the claim is WITHDRAWN** | See details below. |
| R1-4 regression | STANDS WITH CORRECTION | **ACCEPTED** | See details below. |
| R1-5 assay | FAILS for (a), (b), (c) on NPE and BEE r016299 | **ACCEPTED, and extended to BEE r038751 too** | See details below. |
| R1-6 retraction | STANDS WITH CORRECTION | **ACCEPTED** | See details below. |

## R1-1 representation
- "Cannot" was argued, not tested.
- The field split is the directive's own list. It is not a finding.
- The one surviving addition is keeping STATE (IBS) separate, plus the rules that stop fields standing in for one another.
- "Axis" vs "qualifier" is a naming choice; the claim is dropped.
- A1 is now token-based and recursive. It rejects template / ancestor / parent keys (CX-1a) and accepts `apparent_fidelity`
  (CX-1b).
- `native` still carries engine fields verbatim. No derived quantity reads parent-like native fields.

## R1-2 TH-014
- The classifier maps recorded channels to classes. It does not detect a mis-logged channel from bytes.
- New rule A16: material provenance from harness_log / operator_log requires an infrastructure process. This rejects the realistic
  leak (CX-2a/2b: process and carrier both mis-logged), now included as fixture `+MISLOGGED_CHANNEL`.
- A14: a convention cannot put a reproduction label on an infrastructure channel (CX-2c).
- Remaining limit: if the engine lost the infrastructure log as well, nothing in the record can reveal the leak. The TH-014
  requirement is now stated as "the instrument must RECORD the channel evidence", not "the classifier detects leaks".

## R1-3 reproduction boundary (WITHDRAWN)
- On the directive's own cases four definitions tie: D5, D5T, D7, D7_STRICT.
- D7's lead came from two cases I authored.
- The reviewer's cases break D7:
  * CX-3a, a universal copier and junk: fixed by removing the RELATIONAL pass. A Tierra parasite HAS local machinery; the fixture
    was wrong.
  * CX-3b, von Neumann's constructor + description: D7 fails it; there is no fix.
- Adding the reviewer's cases, the only survivor is D5T (capable donors supply >= theta of the material, plus a capable child).
  That is the same case-set game, so no winner is claimed. The case x definition matrix is the result, and
  test_the_winner_depends_on_the_case_set records how the survivor set changes with the case set.
- Machinery claims now need knockout dependence entries (A17, CX-3c).
- Donor capability must be an executed claim about the donor, not a native field.
- D6 (heredity) no longer rides on D5.

## R1-4 regression
- The E-002 self-cross was a PTE genetic-algorithm crossover, not an Archaeon organism event. Re-encoded (pte_ga_self_cross:
  OPERATOR_RECOMBINATION, one donor).
- P-11 is no longer filed as a capability; it is a dependence test, and the case's capability is "untested".
- Each historical label must now be rejected by the rule that names its error, not by any rule.
- Accepted: this shows only that the validator rejects a label contradicting correctly recorded fields. It does not show that v0
  would have caught the historical errors from the data available then.

## R1-5 assay
- BEE material was a source-address reading (CX-5a, real traced VM). NPE material was value match plus code provenance (CX-5e).
- The BEE performer was hard-coded (CX-5b).
- Count resolution disabled tiling (CX-5c/5d).
- All are fixed: ASSAY.md v2.
- The headline changed. Descent is identifiable only in Archaeon's preserved record. For BEE and NPE the directive's quantitative
  questions need a material-taint replay.
- r038751 was wrong in the same way (the reviewer tested r016299 explicitly).

## R1-6 retraction
- Added to the retraction note: the lineage was failing (18 births, 6 exact, dead by epoch 14,072) and was rescued by host
  execution. Inert arrival 446,966 began running the near-copier's own code at epoch 14,001. It was about 800 epochs old when
  measured, and background mutation also replaces material ids.
- The "no exact self-copy" test is isolated-VM; the "6 exact" count is in situ. Both are true.

## Where I disagree (partially)
- R1-1 point 3: CONTRAST and AGGREGATION being required top-level keys is not a contradiction of "qualifier". A required qualifier
  is still a qualifier. But the axis count has no testable consequence, so the claim is dropped anyway.
- R1-5 (d): "later is_sr in situ" is labelled `replayed`. It is an in-world event, not an isolated test, and is recorded with
  conditions {neighbour: in_situ_partner, scaffold: world}. I keep it, qualified; the reviewer's circularity point about the
  writer's donor_capabilities is accepted, and that field is removed.

## Process finding (for directive item 11)
- A context-free reviewer with primary-evidence pointers, told to invalidate, found in 10 minutes what my own tests (44 green)
  could not. My tests encoded my assumptions: the verdicts, the adapters' `via` values, the fixtures' channels.
- The most useful move was the reviewer running Bellerophon's own traced VM on hand-built memories to produce ground truth. That is
  an executing reviewer, not a reading one.
- Recommendation: every future Archaeon synthesis ships with one such review before promotion (as here), and review prompts should
  ask for executed counter-examples.
