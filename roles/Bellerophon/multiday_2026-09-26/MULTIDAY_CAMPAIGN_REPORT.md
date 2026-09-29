# MULTI-DAY CAMPAIGN REPORT -- Bellerophon E-BEL-MD (C-BEL-MULTIDAY), physics v3: acquisition, protection, repair

Written 2026-09-29 after the frozen analysis point. Prereg: MULTIDAY_PREREG.md (frozen 12ce26e23, code a3086cece, no
amendments). Analysis: tools/md_analysis.py, byte-identical to the frozen blob (sha256 73b1e918...), run
2026-09-29 03:06-05:05Z on the pinned code and inputs, --replay 0.03 --workers 12, under Fabric lease
lse-a0185f56ea0c (spectrex5:cpu12; released). Output: receipts/MD_RESULTS.json (committed with this report).

## 0. Header

- Runtime: 47.1 h active in ONE segment (2026-09-26T16:40:28Z -> 2026-09-28T15:48:37Z); cap 60 h; estimate was ~27 h.
- Runs: 4,160 / 4,160 complete; NOT_RUN 0.
- Failures / voids: 0 voids, 0 ledger imbalances, 0 empty yokes, 0 supervisor relaunches, 0 tail repairs.
- Reproducibility: seeded 3% replay 114 / 114 byte-identical (every field except wall_s).
- instrument_ok: TRUE (prereg s9). Hypotheses may be interpreted.

## 1. Primary dispositions (frozen rules, s7; Holm across 5)

| primary | result | numbers |
|---|---|---|
| Q1_LADDER1: ECHO copiers acquire INC | **HOLDS** | acquired ON 58/320 (18.1%) vs OFF 0/320, SHUFFLED 1/320, YOKED 0/320. Pairs ON>c: 58-0, 58-1, 58-0. p_holm 1.0e-15. Margin met |
| Q1_COPIER: pure copiers acquire ECHO | **HOLDS** | ON 36/240 (15.0%) vs OFF 4, SHUFFLED 2, YOKED 2 (of 240). p_holm 1.6e-8. K16 ON 6/120; K40 ON 30/120 |
| Q1_LADDER2: INC copiers acquire COND_ONE | **FAILS** | 0/240 in EVERY arm, both K. No discordant pair (p = 1) |
| Q2: task robustness rises within ON runs | **HOLDS** (small) | n = 134 runs with >= 2 eligible checkpoints; up 72, down 41; mean change +0.0115 [0.0055, 0.0183]; p_holm 0.009. Reported beside it: OFF copy-robustness drift +0.004 [-0.0014, 0.0093] (n = 238) |
| Q3: repair becomes common | **FAILS** (baseline clause) | ON 15/320 = 4.7% vs OFF 0, YOKED 0 (p_holm 1.8e-4, direction met). The frozen extra clause needs ON > 4/60 = 6.7% (the 500-tick rate): NOT met |

Disposition tags (s10): **LADDER_CLIMBED** (Q1_LADDER1) and **PROTECTION_EVOLVED** (Q2). REPAIR_COMMON: no.
NO_ESCALATION: no.

## 2. What the numbers mean (and do not)

1. **One rung, not a ladder.**
   - With computation paid, copiers carrying ECHO code acquired INC in 18% of worlds; unpaid, shuffled-paid and
     supply-matched controls: essentially never.
   - COND_ONE (a conditional: several edits from INC in the measured task family) was never acquired, in any of the 960 LADDER2 runs.
   - The supported claim: coupling carries a population across a one-edit gap. It has not been shown to cross a
     multi-edit gap within 20,000 ticks.
2. **The ECHO acquisition replicates at 40x the horizon.**
   - K40: 30/120 ON vs 1-2 in controls. The coupling campaign had 29/150 at 500 ticks.
   - K16 stays weak (6/120). The effect lives where base income keeps copiers alive.
3. **Protection is real but small.** Robustness of the dominant competent tape rose by about 1.2 percentage points of
   mutants that stay competent. The OFF-arm copy-robustness drift is a different trait and its CI includes 0. The two
   are not a matched contrast, so "task-specific" protection is suggested, not established.
4. **Repair did not become common.** A long horizon did not raise the E2-type repair rate (4.7% vs 6.7% at 500
   ticks). Where repair happens it is coupling-dependent (0 in both controls).
5. **Previous-rung retention** (descriptive): at the end of LADDER1 ON runs 2.7% of the living remain ECHO-competent.
   Acquiring INC replaces ECHO; it does not add to it.

## 3. Post-hoc label audit (labelled; NOT an endpoint; written after the frozen analysis)

The endpoint `acquired` reads the lineage label sr_depth > 0 (a birth event), which can include tapes that do not copy
themselves (Odysseus #748/#804; DEF-BEL-003). tools/label_audit.py -> receipts/LABEL_AUDIT_POSTHOC.json reads the frozen
per-run arch descriptor of each acquired run's dominant competent SR tape:
- **ON arms:** 108/109 are isolated self-copiers with task accuracy 1.0. LADDER1 58/58, COPIER 35/36, REPAIR 15/15.
- **Controls:** 6/9 are label-carriers that do NOT self-copy (COPIER OFF 3/4, SHUFFLED 2/2; LADDER1 SHUFFLED 1/1).
- **Founders:** 0 acquired dominants equal a founder/fixture tape.
- **Reading:** label noise sits in the controls, as Odysseus found for the coupling campaign. Counting only real
  copiers, every Q1 contrast becomes stronger, not weaker (LADDER1 58 vs 0; COPIER 35 vs <= 2).

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
- A next step (e.g. an intermediate rung between INC and COND_ONE, or a longer horizon for the multi-edit gap) would
  be a new, separately authorised experiment.
