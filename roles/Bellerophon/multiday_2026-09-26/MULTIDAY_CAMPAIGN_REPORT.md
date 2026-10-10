# MULTI-DAY CAMPAIGN REPORT -- Bellerophon E-BEL-MD (C-BEL-MULTIDAY), physics v3: acquisition, protection, repair

Written 2026-09-29 after the frozen analysis point. Prereg: MULTIDAY_PREREG.md (frozen 12ce26e23, code a3086cece, no
amendments). Analysis: tools/md_analysis.py, byte-identical to the frozen blob (sha256 73b1e918...), run
2026-09-29 03:06-05:05Z on the pinned code and inputs, --replay 0.03 --workers 12, under Fabric lease
lse-a0185f56ea0c (spectrex5:cpu12; released). Output: receipts/MD_RESULTS.json (committed with this report).

## 0. Header

- Runtime: 47.1 h active in ONE segment (2026-09-26T16:40:28Z -> 2026-09-28T15:48:37Z); cap 60 h; estimate was ~27 h.
- Runs: 4,160 / 4,160 complete; NOT_RUN 0.
- Failures / voids: 0 voids, 0 ledger imbalances, 0 empty yokes, 0 supervisor relaunches; tail repairs: none recorded
  (STATUS field null).
- Reproducibility: seeded 3% replay 114 / 114 byte-identical (every field except wall_s).
- instrument_ok: TRUE (prereg s9). Hypotheses may be interpreted.
- Pin: the code ran from a `git archive` copy (CRLF bytes); equality with the freeze record was checked on
  LF-normalised sha256 for all files.

## 1. Primary dispositions (frozen rules, s7; Holm across 5)

| primary | result | numbers |
|---|---|---|
| Q1_LADDER1: ECHO copiers acquire INC | **HOLDS** | acquired ON 58/320 (18.1%) vs OFF 0/320, SHUFFLED 1/320, YOKED 0/320. Pairs ON>c: 58-0, 58-1, 58-0. Paired difference vs OFF +0.181 [0.141, 0.225]. p_holm 1.0e-15. Margin met |
| Q1_COPIER: pure copiers acquire ECHO | **HOLDS** | ON 36/240 (15.0%) vs OFF 4, SHUFFLED 2, YOKED 2 (of 240). Paired difference vs OFF +0.133 [0.092, 0.179], vs YOKED +0.142 [0.100, 0.188]. p_holm 1.6e-8. K16 ON 6/120; K40 ON 30/120 |
| Q1_LADDER2: INC copiers acquire COND_ONE | **FAILS** | 0/240 in EVERY arm, both K. No discordant pair (p = 1) |
| Q2: task robustness rises within ON runs | **HOLDS** (small) | n = 134 runs with >= 2 eligible checkpoints; up 72, down 41; mean change +0.0115 [0.0055, 0.0183]; p_holm 0.009. Reported beside it: OFF copy-robustness drift +0.004 [-0.0014, 0.0093] (n = 238) |
| Q3: repair becomes common | **FAILS** (baseline clause) | ON 15/320 = 4.7% vs OFF 0, YOKED 0; paired difference +0.047 [0.025, 0.072] (p_holm 1.8e-4, direction met). The frozen extra clause needs ON > 4/60 = 6.7% (the coupling campaign's K16 500-tick rate): NOT met |

Disposition tags (s10): **LADDER_CLIMBED** (Q1_LADDER1) and **PROTECTION_EVOLVED** (Q2). REPAIR_COMMON: no.
NO_ESCALATION: no.

## 2. What the numbers mean (and do not)

Revised 2026-09-29 after two independent Fabric merge reviews (tsk-bc42e48a52be, tsk-def7523bd2f2; both
MERGE_WITH_FIXES). The first-draft wording they found wrong is listed in s7.

1. **One rung acquired, the next not.**
   - With computation paid, copiers carrying ECHO code acquired INC in 18% of worlds. Unpaid, shuffled-paid and
     supply-matched controls: essentially never.
   - COND_ONE was never acquired in any of the 960 LADDER2 runs, in any arm.
   - The frozen task family describes COND_ONE as ONE conditional edit away from INC. This campaign measured no edit
     distance, so the null is NOT attributed to gap size.
   - Candidate explanation (descriptive, prereg s8): LADDER2's non-competent-earner share is 1.0. Every paid correct
     output came from tapes that are not COND_ONE-exact. INC founders and ECHO tapes answer COND_ONE correctly on about
     half of all inputs, so ON pays them, and there may be little or no selective gradient toward the exact
     conditional. Shares in the other lanes: COPIER 0.024, LADDER1 0.037, REPAIR 0.031.
2. **The ECHO acquisition replicates at 40x the horizon.**
   - K40: 30/120 ON vs 1-2 in controls. The coupling campaign had 29/150 at 500 ticks.
   - K16 stays weak (6/120 ON vs 2/1/0).
   - HYPOTHESIS, not tested here: the effect needs a base income that keeps pure copiers alive.
3. **A small within-run rise in the dominant competent tape's task robustness.**
   - About +1.2 percentage points of single-byte mutants stay competent.
   - The measure compares the dominant tape at the first and last eligible checkpoints; these can be different
     lineages. It covers only runs with >= 2 eligible checkpoints (survivor selection).
   - The OFF-arm copy-robustness drift is a different trait and its CI includes 0; it is not a matched control.
     "Task-specific protection" is suggested, not established.
4. **Repair did not become more common.**
   - Like-for-like, the pooled rate is 4.7% at 20,000 ticks vs 5/120 = 4.2% at 500 ticks (coupling campaign E2, K16 and
     K40): no detectable change.
   - Per K (POST-HOC secondary, receipts/POSTHOC_SECONDARIES.json; prereg s8 names it but the frozen script omitted
     it): K16 ON 10/160 = 6.25% vs 4/60 at 500 ticks; K40 ON 5/160 = 3.1% vs 1/60. Controls 0/160 each.
   - The frozen clause fails as written (4.7% is not > 6.7%). The 4/60 baseline has a wide CI (about 2-16%), so the
     gap is NOT evidence of a decline.
   - Where repair happens it is coupling-dependent (0 in both controls).
5. **Previous-rung retention** (descriptive): the frozen figure (2.7%) is a mean over ALL LADDER1 ON runs, not
   conditioned on acquisition. Controls: 0.09-0.11%.
   - POST-HOC split (receipts/POSTHOC_SECONDARIES.json): acquired runs 4.1% ECHO-competent at the last checkpoint
     (n = 58); non-acquired 1.3% (n = 55).
   - A single tape cannot be both ECHO-exact and INC-exact, so no claim is made that acquisition "replaces" ECHO.

## 3. Post-hoc label audit (labelled; NOT an endpoint; written after the frozen analysis)

The endpoint `acquired` reads the lineage label sr_depth > 0 (a birth event), which can include tapes that do not copy
themselves (Odysseus #748/#804; DEF-BEL-003). tools/label_audit.py -> receipts/LABEL_AUDIT_POSTHOC.json reads the frozen
per-run arch descriptor of each acquired run's dominant competent SR tape:
- **ON arms:** 108/109 are isolated self-copiers with task accuracy 1.0. LADDER1 58/58, COPIER 35/36, REPAIR 15/15.
- **Controls:** 6/9 are label-carriers that do NOT self-copy (COPIER OFF 3/4, SHUFFLED 2/2; LADDER1 SHUFFLED 1/1).
- **Founders:** 0 acquired dominants equal a founder/fixture tape. This is informative only for LADDER1 and REPAIR;
  COPIER has no init tapes, so the check is vacuous there.
- **Reading:** label noise sits in the controls, as Odysseus found for the coupling campaign. Counting only real
  copiers, no Q1 contrast reverses.
  * Control rates fall: COPIER OFF 4 -> 1, SHUFFLED 2 -> 0; LADDER1 SHUFFLED 1 -> 0.
  * COPIER ON vs YOKED gets slightly weaker (36 vs 2 -> 35 vs 2, since both YOKED acquisitions are real copiers).
- **Verifiability:** these counts come from host-local results.jsonl. MD_RESULTS.descriptive.acquired_arch_ON is capped
  at 30 per lane, so 58/58 and 35/36 cannot be re-derived from Git alone (see s4).

## 4. Defects and limits (recorded, not smoothed)

- **DEF-BEL-002** (Artemis R-08): md_analysis.py sets `holds` without conditioning on instrument_ok. The prereg s9 rule
  governs, and instrument_ok is TRUE here, so no disposition changes. The frozen script is not edited.
- **DEF-BEL-003:** the SR label is a birth event, not a capability (s3 audit above).
- **Cost model wrong:**
  * the pilots (max 34 min/run, 1.0 GB/worker) underestimated the production tails: max run 6,764 s, max worker
    2,223 MB, max tree 12.5 GB;
  * active runtime was 47.1 h against the ~27 h estimate. The 60 h cap held; the 4 GB reserve was never touched
    (min free 7.7 GB).
  * Pilots with 8 pairs do not sample the long-survivor tail.
- **Reproducibility from Git:** results.jsonl (129 MB; 24.7 MB gzip), STATUS.json, supervisor.jsonl and memory.jsonl are
  host-local on M2, recorded by sha256 (s5). Committed receipts: MD_RESULTS.json, LABEL_AUDIT_POSTHOC.json,
  POSTHOC_SECONDARIES.json (ops + secondaries).
  * Claims NOT recomputable from Git alone: the label-audit counts, the post-hoc per-K and retention splits, and the ops
    figures.
  * Re-deriving MD_RESULTS needs about 561 CPU-h; the 114/114 replay shows such a re-run is byte-identical.
  * A durable archive of results.jsonl by hash is recommended; it has not been done.
- **Scope:** one ladder family (ECHO -> INC -> COND_ONE), one physics (v3), 20,000 ticks, one host. Q2 is a
  single-checkpoint-pair measure (first vs last eligible).

## 5. Operations accounting

| item | value |
|---|---|
| wall = active | 47.14 h, one segment, no suspension |
| workers | 12 throughout (valve never fired), recycled every 2 runs |
| per-run wall | mean 486 s, max 6,764 s, sum 561.2 CPU-h |
| memory | 5,656 samples; min free 7.71 GB; max tree 12,470 MB; max worker 2,223 MB |
| co-running heavy jobs | none recorded. Ensorain WTP-LM01 queued itself behind this campaign (#778) and did not run |
| supervisor | 1 start, 0 relaunches, campaign_stopped rc 0 at 2026-09-28T15:49:03Z |
| analysis | 2026-09-29 03:06-05:05Z, lease lse-a0185f56ea0c (acquired 03:06Z, released 05:05Z) |

Runtime evidence (host-local, not committed; M2 C:/Users/James/md_campaign_2026-09-26), sha256:
results.jsonl d7edf11aa04306416d596b361ac1297a0b6548cfdc3be7d67bbc5f05126d67cc;
STATUS.json de8bc81fa1a76a876b5345e7d276c32c309d5f2c7828b668c5b33116b83b51ff;
supervisor.jsonl 1cc5fe2eca55029d2912f4a7d6a45c4e993a1eabbefe494ec243e14d981e41c8;
memory.jsonl 0a4bd500ee76925132170e2c4da218efd9152dc05aea7f143a7b2737c4549723.

## 6. What this does not authorise

- No new multi-day campaign (MWO-0001, BELLEROPHON section).
- A next step (e.g. a COND_ONE lane in which non-competent partial solvers are not paid, or a measured edit distance) would
  be a new, separately authorised experiment.

## 7. Review record

- Reviews: two independent Fabric replicas (tsk-bc42e48a52be, tsk-def7523bd2f2) on base bcab1d5ff. Both found freeze
  integrity PASS, every s0-s1 number matching MD_RESULTS.json, and every HOLDS/FAILS recomputed correctly. Both returned
  MERGE_WITH_FIXES: prose overclaims, no frozen verdict affected.
- First-draft wording corrected here:
  * "COND_ONE ... several edits from INC" and the one-edit / multi-edit mechanism (contradicted by the frozen tasks.py;
    no distance measured);
  * "Acquiring INC replaces ECHO" (unconditioned metric);
  * "4.7% vs 6.7%" as a horizon effect (not like-for-like);
  * "every Q1 contrast becomes stronger" (false for COPIER vs YOKED);
  * "the effect lives where base income ..." (untested);
  * "0 tail repairs" (the field is null);
  * the vacuous COPIER founder check.
- Added: the LADDER2 non-competent-earner confound (prereg s8 descriptive), the per-K Q3 rates, effect-size CIs,
  reproducibility limits, the CRLF pin disclosure, and receipts/POSTHOC_SECONDARIES.json with its failure ledger
  (FAILURE_LEDGER.md).

---
## SEED-INDEPENDENCE AUDIT (2026-10-10T10:26:19Z, Bellerophon, BEL-RD-72 s XI) -- no correction needed; original figures unchanged

The plan was regenerated from the committed code and inputs and every seed checked: seeds are shared ONLY across the
arms of one block (ON / OFF / SHUFFLED / YOKED of the same lane, block and K) -- the intended seed pairing, analysed with
seed-pair tests -- and by no two blocks, K levels, tasks or lanes (0 seeds span more than one (lane, block, K)). Coupling:
11,372 Phase-1 runs on 3,151 distinct populations; multi-day: 4,160 runs on 1,120. Per-arm denominators in this report
are counts of distinct populations already. (The grounding round's design differed: see its correction record.)
