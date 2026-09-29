# S3 workload -- DRAFT for the principal (NOT FROZEN)

Drafted by Artemis on ubu002, 2026-09-29, for the Artemis principal session
that the operator ruling places on ubu001 (Odysseus #923;
roles/Odysseus/prompts/2026-09-28_fabric/06_*). That session reviews
this draft, pastes the table into S3_PROTOCOL.md s3, and freezes it by
commit before the one submission. Nothing here was submitted.

## How the 10 packages were chosen (no ranking, no rewriting; MWO-0001)

- Built by build_s3_draft.py from origin/main 742243972 (committed content only).
- Eligible: backlog state RAW; host class L (repo-only); not used in the
  2026-09-28 self-test cohorts; cluster not D (memory, SI-adjacent), H
  (holdouts/custody) or Z (answered); no blind-lane guard term in the title.
  56 eligible, 77 excluded (reasons per thread in draft/DRAW.json).
- Draw: random.Random(sha256(S3_PROTOCOL.md)).sample(eligible sorted by id, 10);
  seed 2bb850283794920e... The protocol text is Odysseus's, so the seed is not Artemis's choice.
- Each package is built the same way as the self-test's raw (B) cohort packages: title,
  relations and verbatim harvest entries, with curator names redacted, plus the S3 deliverables
  paragraph. This matches the control class the protocol compares against.
- Body guard scan: 'selective' (Q9: an arbiter as an unmodelled selective force) and 'retaining'/
  'retention' (Q6: QD archive policies) are not SI material, and the recipients are generic Fabric
  workers and fresh scorers, not seats. Left as drawn.
- Uniform budget: 90 min (--wall-s 5400) for every package, so there is no per-package judgement.
  Replication: --replicas 1 (the protocol default).

## Table for S3_PROTOCOL.md s3

| id | question (as a principal would pose it) | budget (min) | required artifacts beyond REPORT.md | quality criterion specific to it |
|---|---|---|---|---|
| Q1 | package draft/Q1.package.md (harvested question, verbatim; source thread FR-028, cluster C) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q2 | package draft/Q2.package.md (harvested question, verbatim; source thread FR-075, cluster K) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q3 | package draft/Q3.package.md (harvested question, verbatim; source thread FR-053, cluster F) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q4 | package draft/Q4.package.md (harvested question, verbatim; source thread FR-099, cluster N) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q5 | package draft/Q5.package.md (harvested question, verbatim; source thread FR-115, cluster M) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q6 | package draft/Q6.package.md (harvested question, verbatim; source thread FR-102, cluster M) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q7 | package draft/Q7.package.md (harvested question, verbatim; source thread FR-119, cluster L) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q8 | package draft/Q8.package.md (harvested question, verbatim; source thread FR-022, cluster B) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q9 | package draft/Q9.package.md (harvested question, verbatim; source thread FR-077, cluster K) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q10 | package draft/Q10.package.md (harvested question, verbatim; source thread FR-055, cluster F) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |

## Open points for the principal session

- The two identity probe packages (protocol s1) are Odysseus's to supply or to specify.
- Claude workers cannot run code, so packages that need computation return out/analysis.py.
  Running it is a counted code-stage coordination action.
