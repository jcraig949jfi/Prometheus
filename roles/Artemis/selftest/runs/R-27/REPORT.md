# Reversal catalogue pilot: ruler defects vs substrate facts in the engine seats (2026-09-14..27)

## 1. WHAT I SET OUT TO TEST

The program holds, at high confidence, that measurement defects rather than substrate facts explain a large share
of its reversed claims. That confidence rests on a count of defects, which are a different unit from reversals.
I tried to count the right unit. I built a catalogue of reversals from committed records in the engine seats
over 2026-09-14..27. A reversal here is a claim committed as a result and later withdrawn, narrowed by 2x or more,
flipped, or demoted to void/unresolved. For each one I asked whether the thing that changed was the ruler
(comparator, threshold, detector, window, selector, generator/author, harness, control, sampling, referent) or
the world (a new measurement with the same instrument). I also asked whether the failure class had already been
documented in a different seat, or in Harmonia's Failure-Primitive Atlas, before the claim was made (the
rediscovery rate). Finally, I checked whether the class definitions can be coded reliably, using a blind second
coder and Cohen's kappa.

## 2. WHAT I DID

Inputs (read-only clone, nothing executed from the repo, no compute beyond a few seconds of python stdlib):
- Engine-seat calibration ledgers. For each seat I took the longest version on any branch:
  Aether roles/Aether/calibration/LEDGER.md@77b11cef5; Ananke @c34cbb463; Aphrodite @50782371c;
  Archaeon roles/Archaeon/CALIBRATION_LEDGER.md@7c89a7199; Ares @1dde117f7; Bellerophon @3753d668b;
  Cosmos @940b486f2; Crius @8a2abb596; Ensorain @a65d27ced; Nestor @0100d36cd (empty). That gives 119 dated rows.
- roles/Nestor/FINDINGS.md@fdc73636f (last commit inside the window, on nestor/s1-forensics-2026-09-23), and
  roles/Nestor/campaigns/npe-p2-endogenous-heredity-2026-09-27/SYNTHESIS.md@fdc73636f section 13.
- Erratum/correction sections found by a heading search (WITHDRAWN|RETRACT|ERRAT|CORRECTION|NARROWED|REVERSED...)
  restricted to engine seats and to the window:
  Aether/AETH-01/AETH-02_CLOSE_2026-09-24.md@0e63a3d52 s5;
  Aether/AETH-01/MIX64_SCALAR_REPAIR_2026-09-22.md@66c55243f; roles/Aether/journal/2026-09-22.md;
  roles/Ananke/pte/C1_ERRATA.md@cc98596dd; roles/Ananke/pte/c1b/CORRECTIONS_2026-09-27.md@c34cbb463;
  roles/Ananke/research/C1B_REVIEW_AND_MECHANISMS.md@95f354c3c (addendum);
  ares/ARES_CYCLE2_REPORT.md@3f68be2b9 s5-6; roles/Nyx/reports/ARES_W4_READING_2026-09-25.md@bf5073a91 s0;
  roles/Crius/REVIEW_PACKET_C2_TERMINAL_2026-09-23.md@7069c0ce6 s1;
  ensorain/E1_VERDICT.md@2caf43ff3; ensorain/ENSORAIN_WTP03_REPORT.md@a65d27ced;
  roles/Bellerophon/forensics_2026-09-23/POST_CAMPAIGN_FORENSICS.md@ff8c8519c against the campaign packet
  archaeon/z80atlas/pivot/Z80ATLAS_REVIEW_2026-09-22.md@d50f5710a;
  roles/Nestor/sidequests/graphworld/journal/B.md@2224c31d4 and C.md@d9d005713;
  archaeon/causal_lens/FALSE_FRIENDS.md@949b9ba4d (FF-1, FF-32, FF-33) with archaeon/envgate2/VERDICT_2026-09-26.md.
- Baseline for prior documentation: harmonia/memory/architecture/failure_primitive_atlas.md@acad16c47 (FP-001..004),
  plus dated rows or lessons in other seats' committed files. I dated Nestor's standing lessons with git log -S.

Steps:
1. I froze the codebook before coding: CODEBOOK.md, which copies the protocol's unit, fields, LOCUS classes and
   decision rule. Its sha256 is 3e64900a...f6a4, recorded with a timestamp in CODEBOOK.sha256. I could not commit
   it because the clone is read-only.
2. Candidate listing: scripts/list_candidates.py parses the ledger rows. scripts/extra.py holds 52 non-ledger
   candidates with near-verbatim text. Total: 171 candidates (candidates_all.json).
3. Coding: scripts/codings.py, one record per candidate. Output is in CODED_RECORDS.json and REVERSALS.tsv
   (incl, loci with weights, caught_by, t1/t2, latency, domain, mechanism class, prior_doc, source, note).
   I added a mechanism class (e.g. VACUOUS, COPY_REFERENT, CODE_BUG, SUMMARY_SOURCE) to measure recurrence.
   I made one post-sampling recode, before seeing the second coder's output. Ensorain's WTP-01 anomalies went
   from REV to PREV, because the git history shows the anomalies and their artefact diagnosis were first
   committed together.
4. Reliability: scripts/sample.py drew 30 of the 163 in-window candidates (random.Random(27)). A fresh agent
   session coded them blind from the codebook plus the item text only, with no repo access
   (blind/BLIND_ITEMS.json -> coder2_output.json). scripts/kappa.py computes kappa.
5. Statistics: scripts/stats.py and scripts/sens.py.

## 3. RESULT

Candidates: 171. Of these, 62 are reversals, 46 are lost predictions or hypotheses (excluded, counted
separately), 33 are defects caught before any result was stated, 22 are other (ops and process incidents,
design choices, minor corrections) and 8 fall outside the date window. That is 62 reversals in the pilot frame,
inside the 40-80 estimate. They are concentrated in Nestor (26; its FINDINGS ledger is unusually explicit),
then Ananke 10, Ensorain 5, Aether 4, Cosmos 4, Ares 4, Aphrodite 3, Archaeon 3, Crius 2, Bellerophon 1.
In the ledgers, only 22 of the 111 in-window rows are reversals. Most rows are lost predictions, pre-result
catches, or process incidents.

Ruler vs substrate (weighted, mixed cases 0.5/0.5):
- All reversals (n=62): ruler side 0.92, substrate 0.08. The narrow ruler set (comparator, threshold, detector,
  window, selector, generator/author, harness) is 0.76. Control, sampling and referent make up 0.16.
- Science claims only (n=53; excludes engineering-cost, literature and framing reversals): ruler 0.91, substrate 0.09.
- Sensitivity: excluding Nestor 0.90; ledger rows only 0.96; non-ledger only 0.90; counting every mixed case as
  fully substrate 0.90.
- Locus mass: detector/guard 16.5, harness 11, generator/author 9.5, substrate 5, comparator 4.5, referent 4,
  window 3.5, sampling 3.5, control 2.5, threshold 2.
- Caught by: own forensics 54, other seat 4, operator 2, external review 2. Latency t2-t1: median 0 days,
  mean 0.6, maximum 4. 37 of 62 were reversed the same day.

Rediscovery (a prior document in a different seat, dated before t1, naming the same locus and mechanism):
- 15/62 = 0.24 with the atlas and cross-seat documents; 0.33 excluding Nestor.
- Atlas alone, as the protocol specifies: 6/62 = 0.10 (4 via FP-004 degenerate/pinned field, 2 via FP-001
  baseline costume).
- Cross-seat documents alone: 13/62 = 0.21.
- The recurrent examples are vacuous-by-construction nulls and interventions, recorded in Archaeon (09-05),
  Aphrodite (09-17) and Nestor (09-23/24) and then reappearing in Ananke (09-25/26). The others are
  constant-baseline gates, from Cosmos (09-23) to Ensorain (09-24), and identity-vs-heredity, from Nestor
  (09-24) to Archaeon's ENVGATE labels and FF-32.
- By mechanism class, 13 of 14 classes appear in two or more seats. A failure class usually recurs, but only
  about a quarter of reversals had a findable prior write-up that predates them.

Reliability (30 blind items, coder 2 = fresh agent session):
- Inclusion, reversal vs not: agreement 0.83, kappa 0.65. With my pre-recode code for the one recoded item:
  0.87, kappa 0.72.
- Five-way category: agreement 0.80, kappa 0.71.
- Primary locus, among the 9 items both coders called reversals: agreement 0.78, kappa 0.71. Ruler vs substrate
  agreement on those items: 9/9.
- Primary locus wherever both coders gave one (n=22): kappa 0.67.
- Disagreements cluster on one boundary: whether a defect found while reading a result counts as caught before
  the result was stated (PREV) or as a reversal. They also cluster on harness vs detector for an instrument that
  did not reach the quantity.

Plain conclusion: among detected reversals in this frame, about 9 in 10 trace to the ruler, not to a substrate
fact. The loci codes cleared the preset 0.6 kappa bar, though with a small n. The ruler share clears 0.7 under
every sensitivity split I ran. The rediscovery rate is between the two decision thresholds (0.10-0.33
depending on baseline). It supports neither "documentation is not transmitting" (>= 0.5) nor "classes are
mostly new each time" (< 0.2).

## 4. DID IT RESOLVE THE QUESTION

Partly.

The ruler share is resolved for this frame and this unit. The result is robust to how mixed cases are split and
to dropping the dominant seat, and locus coding was reliable enough (kappa about 0.7 on 9 jointly-included
items; about 0.67 on 22).

Four limits:
(a) Survivorship. Only written-down reversals are visible. A substrate reversal usually reads as "new result",
    not as an error. The lost-prediction pile (46), which the second coder mostly coded as substrate facts, is
    where substrate surprises live, and it is excluded by definition.
(b) The inclusion boundary depends on commit granularity. A defect caught in the same commit as its result is
    PREV, one commit later it is REV. This moved one sampled item and is the main source of kappa loss.
(c) The kappa sample is 30 items, with only 9 jointly-included reversals for locus. The second coder was a
    model session, not a human, and coded from text excerpts I wrote.
(d) Rediscovery depends on which prior documents I found. I did not search every seat's journals, so it is a
    lower bound on "was documented somewhere" and an upper bound on "was documented where the next seat would
    look".

Not done: program-wide extension beyond the ten engine seats and window, the forward test on future launches,
and a human second coder.

## 5. CONSEQUENCES

- The standing proposition, that measurement defects explain a large share of reversals, is now supported on
  the right unit (reversals rather than indexed defects), for engine seats in this window: ruler share about
  0.9, locus kappa about 0.7. Owner of that proposition (Atlas): change the cited basis from the 218-defect index
  to this count. Also add the survivorship caveat: substrate surprises are recorded as lost predictions, not
  reversals.
- Reversals are overwhelmingly self-caught and fast (median same day, maximum 4 days). The binding constraint
  is not detection latency. It is that the same classes recur across seats, for example:
  - vacuous-by-construction nulls and interventions, in 4 seats;
  - similarity or label read as copying/heredity/content, in 4 seats;
  - partial carrier census, in 3 seats;
  - summary-sourced numbers, in 3 seats.
  Rediscovery at 0.10-0.33 is below the "build a pre-launch sheet" threshold, but classes recur across seats
  far more often than prior write-ups exist. A short pre-launch checklist of these 4-5 classes is cheap and
  worth a blind forward test.
- Harness/atlas owners (Harmonia): the Failure-Primitive Atlas, stalled since 2026-06-15, matched only 6 of 62
  engine-era reversals. At least three engine-era classes are good atlas candidates with cross-seat anchors:
  - vacuous guard/intervention (Archaeon, Aphrodite, Nestor, Ananke);
  - identity/label vs heredity/content (Nestor, Archaeon, Bellerophon);
  - selection on the reported set / best-of-N (Ares; caught pre-result).
- Instrument defect in the protocol itself: the reversal/PREV boundary needs a rule based on the artifact, not
  the commit (e.g. "stated in any committed doc outside the file that corrects it"). The LOCUS list has no class
  for interpretation or novelty overclaims, which I coded as generator/author. The decision rule codes
  unmeasured mechanism assertions refuted by a first measurement as SUBSTRATE-FACT. That is literal but arguably
  wrong, and it is one of only 5 substrate units. Fix these before a second pass.
- Premise correction: the ledgers are not about 40% reversals. Here, 22/111 in-window ledger rows qualified.
  Most reversals live in findings files and errata sections, not in calibration ledgers. The package's example
  of the Ares best-of-N gate C flip was caught before the report, so under the codebook it is a pre-result
  catch, not a reversal.
- Who should know: Atlas (proposition basis), Harmonia (atlas growth), the engine seats (the recurrent-class
  checklist), and whoever runs the typed catch-time record proposal. This catalogue is a ready seed for it.

## 6. COST

About 2.5 hours of agent time. CPU: under 1 minute total (python stdlib parsing, git reads). The second coder
used about 1 agent-minute. No GPU, no services, no holdouts touched, nothing written to the repository.

Not done:
- a committed codebook freeze (the repo is read-only; I used a hash plus timestamp instead);
- a revise-and-recode round (not triggered, since kappa >= 0.6);
- a human coder;
- the frame extension to non-engine seats;
- an exhaustive prior-doc search.

Files in the scratch directory: CODEBOOK.md, CODEBOOK.sha256, candidates_all.json, CODED_RECORDS.json,
REVERSALS.tsv, kappa_key.json, blind/, coder2_output.json, scripts/, frame/.
