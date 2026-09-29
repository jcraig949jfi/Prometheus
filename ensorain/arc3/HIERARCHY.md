# Ensorain work mapped to the MWO-0001 common hierarchy (Thread > Campaign > Experiment > Task > Attempt)

Adopted 2026-09-29 under MWO-0001 s4. History is not renamed; this file adds aliases.

## Threads (enduring questions)

| id | question | existing aliases |
|---|---|---|
| thr-ens-lossless-memorizer | Can exact retention reach the generalization of bounded coarse-grained state under accounted resources? | WTP-LM01 directive; ARC3 T01 |
| thr-ens-locus-of-compression | Where does compression occur (stored records / learned hypothesis / query readout), and what does each buy? | ARC3 T02, T09, T10; PKG-S1 three-loci decomposition |
| thr-ens-causal-selectivity | Does discarding particular distinctions CAUSE better generalization? | ARC3 T04, T06, T07; PKG-F |
| thr-ens-sufficiency-ladder | Does each memory strategy retain what is provably sufficient, in answer-keyed worlds? | ARC3 T17-T21, T25; PKG-S1 |

## Campaigns

| id | envelope | threads |
|---|---|---|
| C-ENS-ARC3 | Operator ARC3 directive 2026-09-28 (roles/Ensorain/prompts/2026-09-28_arc3_directive/). Dev compute below the lease threshold; LM01 is its only gated experiment | all four |

## Experiments

| id | status | notes |
|---|---|---|
| E-ENS-LM01 | FROZEN v0.3.2 ee8cbe0c8, NOT LAUNCHED (queue item Q1). HOLD on the launch authorization; carrier defect DEF-ENS-001 | ~10 h at 8 workers; Fabric lease at launch (MWO-0001 s3) |
| E-ENS-S1-PILOT | DONE (dev, answer-keyed, not preregistered): ensorain/arc3/suff/RESULTS_S1_PILOT.md. C1-C4 independently REPLICATED (Fabric tsk-ba120344aa29; suff/replication/) | thr-ens-sufficiency-ladder, thr-ens-locus-of-compression |
| E-ENS-PKGF-PROBE | DONE (dev prerequisite probe v1+v2): ensorain/arc3/RESULTS_PKGF_PROBE.md | thr-ens-causal-selectivity |
| E-ENS-PKGF | DESIGN (ensorain/arc3/packages/PKG_F_CAUSAL_SELECTIVITY.md). Not before the LM01 integration | thr-ens-causal-selectivity |
| E-ENS-LM02 | DESIGN (ensorain/arc3/packages/PKG_LM02_DESIGN.md). After the LM01 rows | thr-ens-lossless-memorizer, thr-ens-locus-of-compression |

## Tasks / Attempts

None yet. Candidate Fabric Tasks (bounded, portable, no WTP-M2 locality needed):
- DONE: tsk-ba120344aa29, PKG-S1 replication (lesson: the claude executor cannot run code; use claude-writes then script-runs);
- an independent review of PKG-F design v0.1;
- a CSSR causal-state learner build (T25).
