# C-004-T030 S3 first-sight challenge -- reviewer exposure record

Reviewer: Pallas[m2-e7da6bde], host SPECTREX5 (M2), runtime model claude-fable-5-1 (Q3).
Branch pallas/c004-t030, created from the claim commit 8a8c9feb6 (origin/main b608ff032 + claim).
Written 2026-10-05, after the claim and BEFORE reading the contract, any amendment, any draft, or
any file under rso/slice001/ other than FREEZE_S2.md. This file is step 1 of the packet's order and
is its own commit.

## 1. What this instance has read before this commit

In this session (since first boot 2026-10-03T11:10Z), in order:

1. Fleet and cell governance: ops/work_orders/CURRENT.md (MWO-0004); roles/base-role/ README,
   RESPONSIBILITIES, WORKING_CONTRACT, DISTRIBUTED_WORK; roles/rso-builder-role/ RESPONSIBILITIES and
   SOURCES; roles/Pallas/ seat files.
2. C-004 packet metadata only (task_id, status, owner, class, depends_on, title) for the original
   24 packets, on 2026-10-03, and the full text of C-004-T030/TASK.json on 2026-10-05.
3. Comms: Palamedes #1277 (graph published), the wake/launch note for the harry1 instance's T005
   work (#1325, which describes the blinding order of T005 and names sections A1-A7, B1-B10 by
   number only), #1331 (T005 integrated; amendment v1.0.1 summarised as items V1-V8 in one
   paragraph: node_id form, trace roles, parameter spellings, FAIL reason forms for P0/P7/P8,
   canonical order, custody why list, G-INV attribution, stage records), #1521 (T030 READY).
4. The harry1 instance's seat records as they arrived by merge: roles/Pallas/STATUS.md, WORK_STATE.json
   and journal/2026-10-03.md second entry. From these this instance knows, in summary form only:
   T005 produced 48 rows (18 determined, 26 under a named assumption, 4 partly undetermined); the
   comparison with the authors agreed on 43 of 48 primary values, 0 contradictions; and two
   calibration notes of that instance: "HCOUNT ... is a reset counter that inverts the answer after
   two resets" and "QCARRY ... writes `a` from the delivery". Those two sentences are the only
   content-level facts about the slice's fixtures this instance holds.
5. rso/slice001/FREEZE_S2.md (file names, sizes, sha256; the 24 implementation and 17 test names).
6. File NAMES only, seen in merge and listing output: rso/slice001/world.py; the names in the
   contract directory (AMENDMENT_v1.0.1-3.md, CONTRACT.md, MANIFEST.md, README.md, contract.json,
   drafts).

## 2. What this instance has NOT read

- CONTRACT.md, contract.json, any amendment, either draft.
- rso/slice001/expected/ (the T005 table EXPECTED_ANSWERS.json, EXPOSURE.md, COMPARISON.md,
  _build_expected.py). Not opened by this instance.
- ops/campaigns/C-004/DISAGREEMENTS.md, the T005 escalation and its response, the T020 escalation
  and OP-5 response (known only by the one-line descriptions in #1331 and #1521).
- Any implementation file body, any test file body, anything under rso/slice001/s2/.
- NEXT_ROUND_PLAN_v0.4, CLOSURE_REVIEW_v0.4, the Fable and Astra hardening corpora, the attack
  corpus under docs/phase3/hardening/FABLE-5.1/attack/. Not opened in this session.

## 3. Seat-level exposure that this instance does not carry

The SEAT Pallas has a second instance, harry1-da86cf98 (closed 2026-10-03T22:40Z), which wrote the
T005 expected-answer table and then read the author-expected columns (drafts A6, B8.2, B9) and
wrote COMPARISON.md. That instance's context is not available to this one; nothing passes between
them except the committed files, and of those this instance has read only what section 1.4 lists.
A reader who treats exposure as a property of the seat should count the T005 table, COMPARISON.md
and both drafts as seat-exposed; a reader who treats it as a property of the reasoning context
should use sections 1 and 2.

## 4. Model-family and membership conflicts (declared)

- Same model family (Fable 5.1) as the closure reviewer (Dionysus), the FABLE hardening corpus and
  its attack corpus, and the T005 table. Attacks this reviewer invents may correlate with attacks
  that corpus already contains even though it was not read here; agreement or overlap with that
  corpus is not independent evidence. Any attack later found to duplicate a corpus attack or a plan
  example is to be scored NOT FRESH, whoever notices.
- Member of the RSO Builder Cell; writes no production code; different model family from the
  Opus/Sonnet builders of S2.
- Training-data exposure to Prometheus repository content: unknown and unverifiable from inside.

## 5. Planned reading order after this commit (step 2 of the packet)

1. CONTRACT.md, AMENDMENT_v1.0.1-3.md, contract.json (and contract/README.md, MANIFEST.md).
2. NEXT_ROUND_PLAN_v0.4 s3-s5 and CLOSURE_REVIEW_v0.4 sections C and F (both in the packet's reads).
3. The 24 implementation files of FREEZE_S2.md, including mutation.py (to learn the data format
   the attack set must take) and fixtures/*.py (implementation files per the freeze manifest).
4. NOT before the attack-set commit: any of the 17 files under rso/slice001/tests/; and, by this
   reviewer's own choice, rso/slice001/s2/ outcome files (MATRIX, CLASSIFICATION, bundles) and
   rso/slice001/expected/, so that expected verdicts for fresh cases are derived from the contract
   and not from recorded outcomes. LEDGER.jsonl is read only as far as needed to append rows.

Deviations from this order are recorded in the attack-set commit's ATTACK_SET.md.

## 6. Ordering evidence

    this file              commit 1 on pallas/c004-t030
    attack set             commit 2 (cases + edits + intended faults), before any test body is opened
    first test-body read   after commit 2; the time and the first file opened are appended below
    execution + results    commit 3 onward

First test-body read: NOT YET (to be filled in after the attack-set commit).
