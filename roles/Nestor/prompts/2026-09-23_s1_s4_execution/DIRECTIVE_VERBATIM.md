# Operator directive, 2026-09-23 -- Nestor S1 through S4 execution

Captured VERBATIM. Nothing below the rule is edited, reflowed, corrected or
summarised. This file is authoritative and wins over any later summary,
including `STRATEGY_POST_RESET.md`. Issued in the session started 2026-09-23
07:10 EDT, in answer to the post-reset bootstrap report.

---

Proceed with S1 through S4.

DO NOT freeze Cycle 9, write final hashes, create the production observatory, or launch anything. Return for operator review after S4.

S1 — predecessor forensics

Do not modify the frozen 72-hour evidence.

Produce three products.

S1-A — replication failure funnel

First compute the deepest funnel possible from the frozen record for every RANDOM-start non-PAIR_EXECUTION run. Missing transitions must be explicitly labelled NOT_MEASURED, never inferred.

Then create a separate forensic-replay directory and add telemetry sufficient to measure:

self-location executed
-> allocation attempted
-> allocation succeeded
-> target writes occurred
-> BIRTH/SPLIT attempted
-> birth accepted
-> fidelity >= 0.90
-> offspring itself produced an evidence-backed child

Replay 64 frozen RANDOM-start runs from each of:

* ENDOGENOUS_COPY
* ENDOGENOUS_PARTIAL
* CONSTRUCTIVE
* OVERWRITE

Target 256 total.

Selection must be deterministic from the frozen record, using run-id hashing and stratifying as evenly as feasible over self_location and copy_primitive. Preserve each selected run’s original cell, seed, tier and physics. The only change is added telemetry.

These replays are a new forensic assay, NOT retroactive 72-hour evidence.

Report the transition probabilities and absolute losses at each funnel step separately for each reproduction physics.

S1-B — H4 extinction autopsy

For 64dea50f417efb02-s1203-tL-a0 and its exact matched control, reconstruct:

* population size over time;
* endogenous/external births;
* deaths by cause;
* validation epochs;
* held-out trajectory;
* first-cross timing;
* extinction time, if any;
* compute actually consumed before termination.

Determine whether the 4x runtime difference is principally early extinction, population-size difference, validation frequency, or another cause.

Do not change H4 yet. Produce the diagnosis first.

S1-C — PAIR_EXECUTION deep mining

Do NOT inspect the 1,031 cases until P-11 below is specified, tested and committed.

After P-11 is frozen prospectively, re-adjudicate all 1,031 through it and report:

* number surviving;
* number failing each causal criterion;
* causal replication-depth distribution;
* structure/representation/pressure distribution among survivors;
* whether the previous depth-1 dominance remains.

S2 — P-11 PAIR_EXECUTION causal-copy criterion

Before examining Product C, commit the P-11 specification and tests.

Retain the predecessor phenotype threshold:

final fidelity to donor >= 0.90

Do not choose a new threshold from the 1,031 cases.

A causal pair-copy event additionally requires a matched randomized-victim assay:

1. victim half is randomized before interaction and its initial donor fidelity is recorded;
2. final victim fidelity to donor reaches >= 0.90;
3. consider positions where the initial victim byte differed from the corresponding donor byte and the final victim byte equals the donor byte;
4. at least 90% of those donor-directed changes must have been last-written by the donor during the interaction;
5. matched donor-write-disabled control must remain below 0.90 donor fidelity.

Instrument per-position last-writer provenance. Do not substitute total writes_other.

Tests must include:

* genuine block copier: PASS;
* genuine bytewise copier: PASS;
* already-similar halves with no copying: FAIL;
* donor writes many unrelated bytes: FAIL;
* partial overwrite plus pre-existing similarity: FAIL;
* randomized victim rebuilt by donor: PASS;
* donor-write-disabled version of that same case: FAIL.

Every negative control must be demonstrated capable of catching the predecessor detector.

Only after this spec and test receipt are committed may S1-C inspect the 1,031 predecessor candidates.

P-11 does not rewrite the frozen predecessor result. Report both:

* predecessor criterion: 1,031 admissible;
* P-11 stricter causal reassay: N surviving.

S3 — small engineering fixes

Fix:

1. adjudicate() generator consumption / len(list(rows));
2. CROSS/MARGIN and any other load-bearing adjudication thresholds so bundle and adjudicator read one immutable, hash-covered constants object.

Add defect-injection tests for both.

S4 — candidate Cycle-9 manifest

Do this only after S1-C and S1-B are complete.

Rebuild the H2 specimen panel from P-11 survivors. Do NOT assume the old 16 specimens remain eligible.

Enlarge power unevenly:

* H1: keep approximately current size unless S1 reveals a specific validity reason to change it.
* H2: increase seeds substantially only for P-11-surviving specimens; primary endpoint remains causal replication depth.
* H3: increase shared-seed exposure moderately.
* H4: target 32 seed-pairs per block, unless the extinction autopsy shows the assay itself needs redesign first.

Aim for an evidence-efficient campaign, approximately 5–8 projected wall-hours. Do not pad work to consume 24 hours.

Produce a new candidate manifest, timings, power/information rationale and proposed hashes.

STOP after S4.

Return:

* S1 frozen-record funnel;
* forensic-replay funnel and selected run IDs;
* H4 extinction autopsy;
* P-11 spec/commit/test receipt;
* old 1,031 -> P-11 survivor disposition;
* S3 repair receipt;
* revised H2 panel;
* candidate enlarged manifest and projected runtime;
* every new anomaly or defect found.

No freeze and no launch until operator review.
