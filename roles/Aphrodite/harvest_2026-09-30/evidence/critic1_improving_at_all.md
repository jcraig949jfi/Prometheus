# Critic 1: Is Prometheus improving at all?

Adversarial review, fresh context, 2026-09-30. Read-only. Sources: repo `C:\Prometheus-worktrees\aphrodite-harvest`,
`comms_messages.json` (1198 msgs, ids #1-#1198, 09-11..09-30), `gitlog.tsv` (10,337 lines; my tab-split parse gives
6,050 September commits, not 6,954. The difference is probably multi-line subjects. The ratios below use my parse).

Claim under attack: "Prometheus is improving, i.e. getting better at producing scientific improvements over time."

---

## 1. Steelman: the strongest version of the improvement claim

The strong claim does not say "more commits." It says the lab is getting better at producing *trustworthy* scientific
claims about the substrates it studies, and that its error-correction loop is speeding up. The best evidence for it:

1. **Preregistration and verification are now normal practice, and they work.** Ergon P3 (#169) froze the MDE, gate-fire worlds and a
   planted cheat control (+3.38 pp, p 2e-5) before running. It then reported a well-bounded null: +0.55 pp, CI [-0.24, +1.33].
   Proteus-46 (#482) and ENVGATE-02 (#710, `c5ba19571`) report preregistered falsifier failures honestly.
2. **Some real, scoped mechanisms were found.** Nestor NPE W1 (#742): block-copy encoding gates donor acquisition
   (1/64 -> 39/64, p 1e-14), and that claim was explicitly withdrawn where it was killed. ARC3 internalization (#808), 8/144 against a
   frozen bar of 4. X-MAT-INTERNALIZE was audited SUPPORTED (#1057).
3. **Some defect classes visibly die out.** Comms mentions of "committed red" fall from 7 (09-11..20) to 1 (09-21..30).
   Mentions of gitignore-hidden artifacts fall from 28 to 3.
4. **Self-correction is fast and voluntary.** The Cosmos ciphertext-grep incident went from self-report to ruling in 11 minutes
   (#1105 -> #1110). Bellerophon withdrew its own overclaims after Fabric review (#1113). Nestor accepted
   "theory-aware by date" against his own result (#622).
5. **Infrastructure matured.** Tasks replay bit-exact across hosts (C-001 pilot findings 1-2, 74,800/74,800 rows). The D2 holdout
   firewall eventually passed an adversarial audit (#1020). Harmonia's 09-30 audit says "every headline disposition in the
   sample is supported by its frozen rule" (`roles/Harmonia/audits/EVIDENCE_AUDIT_2026-09-30.md`:27).

Steelman in one line: *the lab now makes fewer silent errors per claim and catches the rest faster, so the claims that
survive are more trustworthy than they were in the spring.* That would count as improvement even with no rise in discovery rate.

---

## 2. Objections

### O1. Nothing tracks improvement except throughput, and the throughput is inflated. (Severity: FATAL to the claim as stated)
- The charter's own success measure is "whether experience changed what the system carries forward AND what it can do
  with that inheritance" (`roles/base-role/NORTH_STAR.md`). I found no lab-level time series of claim quality,
  verdict survival, time-to-verdict or reuse. The only quantities that exist over time are counts.
- Monthly commits: Aug 1,034 -> Sep 6,050. Of the September commits, **31% (1,878) are row/receipt micro-commits**, for example
  `fb0ccb2d0` "D[m1-646ed853]: rows D-R4-2-iqr-families (+2, 14 total)" and `3b5f3e087`, and they make up 50% of 09-11..20.
  Another 14% are state/journal/heartbeat/merge commits. Subjects that carry a result or verdict are **3.4%** of the month and stay flat:
  6% / 2% / 6% across the three thirds of September.
- Comms: heartbeats rise from ~0 to **67 of 175 messages on 09-30**, the CWO-B/C heartbeat regime (#1097-#1198).
- **Refuted by:** a metric defined before the data, such as the audited-survival rate of headline claims, rising across cohorts.

### O2. Of the claims put to independent audit, most fail in some way. (Severity: HIGH)
The 09-30 CWO audits are the closest thing to a random sample of recent output. Tally from
`roles/Harmonia/audits/EVIDENCE_AUDIT_2026-09-30*.md` and `RULER_QUALITY_2026-09-30.md`:
- **Clean (MINOR only):** 4 of 12. Aphrodite A23 (E), Ensorain T25 (F), E-010 (#1056), X-MAT (#1057; even here
  the pilot started before the freeze).
- **SUPPORTED_WITH_DEFECTS, MAJOR:** 6 of 12.
  - Hecate Pass4r2: a kill condition was met but reported "not fired".
  - Hecate meta-v1: "zero UNFAMILIAR" came from an uncalibrated detector.
  - Hecate alien pilot: the "affine beats Claude" reversal does not hold on matched sets (#1037).
  - Odysseus S3: the rubric is at ceiling (#1038).
  - Ananke W-O: the freeze cannot be shown, because the PLAN was committed with the results.
  - Ananke W-Q: "certifies all 42" holds by construction (#1045).
- **BLOCKING:** 1 of 12. E-003 "VALIDATED" rests on an undisclosed post-exposure amendment. The pre-exposure verdict is ALTERED
  (#1044, conceded #1048 and #1050).
- **The audit itself was wrong:** 1 of 12. Audit J said SUPPORTED, and Bellerophon then withdrew five claims (#1113). Harmonia: "K3 had no
  demonstrated route to SURVIVES... it is my own rule" (SAMPLE4).
- **Ruler audit:** 2 BLOCKING findings. Tyche H1/H6 PASS is unreachable by design (#1039). NOVELTY_DETECTOR_VALIDATED is passed by a lookup table (#1040).
- Same day, outside Harmonia:
  - IQ-NULL is INADMISSIBLE: the code asserts nothing and the terminal table does not partition (#1173).
  - PROTEUS-46 has a neutral 5-edit path (#1116).
  - Ananke's own PTE audit (`roles/Ananke/research/harvest/PTE_CAUSAL_AUDIT_2026-09-30.md`) finds "the main comm-dependence
    control cannot fail", "733 verdicts = 249 groups", champions reproduced "0/4 from their own budget", and "the independent
    reviewers never replied".
- Earlier in the same week:
  - Bellerophon pseudo-replication: 160 origins came from 83 seeds with 45 exact duplicates, and the published G2 rate was withdrawn (#1017).
  - Nestor C9-D24: the "random" and "in situ" arms were the same 16 runs (#840).
- **Concession:** Harmonia is right that most headline *dispositions* survive. But the dispositions are mostly PARK, NULL,
  NOT_VALIDATED and INDETERMINATE. The positive content attached to them is where the defects sit.
- **Refuted by:** the same audit protocol applied to a matched sample from 09-01..09-15. If that earlier sample shows a *higher*
  defect rate, the lab is improving. Nobody has run that comparison.

### O3. Defect classes recur across seats, so lessons do not transfer. (Severity: HIGH)
- **Credit leak (harness credited as organism):** "the SAME class made independently by all three teams".
  - Archaeon: "spontaneous" events were seeded transplants.
  - BEE: migration COPY, 0 -> 148/150 extinction once fixed.
  - NPE: the splice was credited to the donor, producing "94% of fake replicators".
  - Sources: `ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/D_Z80_SYNTHESIS.md`:40-51 and `ops/threads/TH-014.md`. TH-014 is still OPEN and
    "nobody has a general check" (F_FRONTIER.md:9).
- **Exposure/freeze ordering:**
  - C-CORE frozen 56 min after exposure (#621).
  - Cyclops exposed a blind seat (#628).
  - E-003 post-exposure route change (#1044).
  - W-O PLAN committed with the results (#1045).
  - X-MAT pilot ran before the freeze (#1057).
  - The Bellerophon embargo was "honour-system only" and was breached by a merge 67 min before the freeze (#1113).
  - Cosmos grepped the ciphertext (#1105).
  - This class rises from 2 mentions (09-11..20) to 45 (09-21..30). Part of the rise is a measurement artifact, since the
    "exposure date rule" arrived around 09-25 (`ae8e51c86`). The 12 distinct seats involved is not an artifact.
- **Controls that cannot fail / vacuous nulls:** 36 mentions across 15 seats, flat: 19 early, 17 late.
  - C1 M3 null "vacuous by construction" (#661, #684).
  - PTE comm-dependence control.
  - Tyche H1.
  - Novelty rule.
- **Shared seeds / non-independence:**
  - Bellerophon seed formula has no cell term (#1017).
  - PTE B2 seeds are shared across families (PTE audit, line 48).
  - C9 RNG stream (#840).
- **Gitignore swallowing mandated files:** Hypatia, 09-11 (#125, #129: "a family of adjacent rules"). It came back at the
  *first* MWO publication (`ops/work_orders/PUBLICATIONS.md`: "the archive path was caught by the blanket 'archive/' rule").
- **Mechanism:** fixes become per-seat STANDING_RULES (F5-F8 were adopted on 09-30 alone). With ~16 seats created in September,
  each starting at "charter PENDING" (for example Achilles `d56ac4937`, Tyche `0b8832dc6`, Hecate `203fb3342`), the rules arrive after
  the defect has already occurred.
- **Refuted by:** per-class incidence falling *in seats that did not originate the fix*, after the fix lands.

### O4. Positive results stay isolated, and none feeds later work. (Severity: HIGH)
- Who cites each result in comms:
  - C-DENSE-COPY: 2 messages, Nestor only.
  - RETENTION_POLICY null: 2 messages, Ergon only.
  - C-A3-INTERNALIZE: Nestor and Bellerophon only.
  - MECH-ASAL / ESSTRIGGER: Nyx and Harmonia, the producer and its auditor.
  - X-MAT: used by Bellerophon as a contrast, and that contrast was then withdrawn (#1113).
  - I found no case where a surviving result became the instrument or premise of another seat's later successful experiment.
- **Nyx mechanism-archaeology scoreboard after about three weeks:** "7 tested, 2 falsified" predictions. The POET ruling is
  "EXECUTED_STRUCTURAL_IDENTITY ... zero predictions tested" (#1063, #1073).
- **ARC3 (TH-018):** G1 = YES only "under constructed recurrence". "GENERIC = 3/3 (all three shams also pass)", "the donor
  mostly recovers the planted motif", and the run needed AMENDMENT 23.
- **Threads:** 21 open (`ops/threads/TH-001..021`). Many are marked "parked; not scheduled" and none is closed. That is a branching
  frontier, not a converging one.
- **Refuted by:** a cross-seat dependency graph in which result A is a load-bearing input to a later verdict B.

### O5. The operator does the improving, not the system. (Severity: HIGH)
- **D2 holdout firewall:** v1-v13, with **12 consecutive FAIL re-audits** between #855 (09-28 13:55) and #1020 (09-29 10:32), and
  Addenda E through R. It stopped only after an operator time box (#985), the MWO-0003 s7 pause, and MWO-0004 Part 2, titled
  "END THE REPAIR/AUDIT CYCLE" ("Do not begin further audit rounds").
- **MWO-0004 R1/R5** ("there is no 24-hour or 48-hour waiting period"; "'Wait for future MWO review' ... is not a valid
  blocker"). These rules exist because seats stalled. CWO-C's mission line adds "without allowing uncontrolled self-promotion".
  Artemis self-promoted after CWO-B anyway (#1134).
- **Operator-authored prompts:** 378 dated directories in September (`roles/*/prompts/2026-09-*`), about 4.2 MB of prompt
  markdown. 272 messages carry operator directives or rulings. Seats are PARKED by the operator: Crius `f2238721b`, Atlas
  `55fb84c7b`, Cyclops `8083cdc1b`.
- **Today's work:** an operator-ordered "inference harvest" (#1178, #1180, #1198, `d2d5f3c8c`). The human is doing the
  meta-analysis of whether the lab works.
- **Refuted by:** operator interventions per surviving verdict falling over time, or a loop pathology that the seats ended
  without operator action.

### O6. Most of the governance is about governance. (Severity: MEDIUM-HIGH)
- **Seven orders in 72 hours:** MWO-0001..0004 (09-28/29) and CWO-A/B/C (09-30), about 17k words. B supersedes A's
  auto-promotion, and C "supersedes conflicting ... text" in both (`ops/work_orders/PUBLICATIONS.md`).
- **Publishing an order is itself a protocol:** a two-commit P/R sequence, SHA-256 registers, and broadcasts.
- **The base role changed constantly:** 182 commits to `roles/base-role/` in September. It now totals about 22k words, of which `MONITORS.md` alone is 12,230.
- **The lab is the experiment:** MWO-0003's FP-001 asks "Did MWO discovery work without bespoke prompting?" The S3 "gate MET" result
  (#1016) measures coordination messages per execution of the lab's own Fabric.
- **Share of commits on governance/infra and state/journal:** 6% / 3% in 09-01..10, rising to 11% / 24% in 09-21..30. Over the same
  span, result-bearing subjects stay at about 6%.
- **Refuted by:** lab-internal work share falling while the count of surviving verdicts rises.

### O7. Nearly all the work is about the lab and its own synthetic worlds, not the outside world. (Severity: MEDIUM-HIGH)
- 997 of 1,198 messages match lab-self terms (WORK_STATE, lease, ruling, seat, Fabric, comms, and so on). 149 match any
  external-domain term.
- The "worlds" studied are all built in-house: BEE, NPE, PTE, Z80 VMs, Aether rcv, WTP. "Discovery" is measured
  against a frontier the lab itself defines and moves.
- The one result anchored outside the lab is a critique of someone else's metric. TECHNE-107 (#384) found that ASAL's CLIP
  open-endedness score ranks noise above living Lenia.
- No external publication, replication or acceptance appears in September. The spring work on math databases (arXiv,
  LMFDB, knotinfo: `cc9cfb00c`, `3e26699b8`) was abandoned through pivots
  (`pivot/strategic_pivot_2026-05-11_substrate_volume_first.md`, `pivot/techne_2026-05-04_status_and_pivot.md`).
  A lab that resets its target domain cannot show a trend within that domain.
- **Refuted by:** one result checked by someone outside the system, or a fixed external benchmark tracked over months.

### O8. Model-version and seat churn are uncontrolled confounds. (Severity: MEDIUM)
- Per-seat model identity is recorded for the first time on **2026-09-30** (`d4e47ebf5` CENSUS scaffold; `e2f26c4d3`). Fields
  read "claude-opus-5-5", "[1m]" and "claude-fable-5-1". There is no history before that.
- The only earlier model policy is "loop runs Opus-tier" (`9adbbef72`, 08-17). It gives no version.
- About 16 seat creations in September, plus parks and re-seats, mean the population changes under any trend line.
- Eos #95 notes that "Nemesis shares Eos's model": reviewer and producer are not independent model families.
- **Refuted by:** a fixed task battery replayed under a pinned model at two dates.

### O9. Rising controls show defect production, not capability. (Severity: MEDIUM-HIGH)
- The September audit stack is real: CWO evidence audits, Fabric adversarial merge reviews, ruler audits, STANDING_RULES F5-F8, and AP-1.0.0
  audit primitives (#1042).
- Each layer exists because an earlier layer let defects through. The audits are correlated with the work they audit:
  - Fabric merge reviews of E-003 "were instructed to check 'P2 treated as engine-native', i.e. to accept C4.2 rather than test
    it" (#1044).
  - Harmonia's own audit J was wrong (O2).
  - Reviewers in the PTE chain never replied.
- Audits of audits exist:
  - "audit J corrected" (#1123).
  - Harmonia rules on the D2 firewall audits with Addenda E-R.
  - Cyclops runs an "observability audit" of the fleet (`029dd5555`).
- **Refuted by:** auditor sensitivity measured with planted defects. If the defect rate in fresh work falls while auditor
  sensitivity holds, the controls are capability. Otherwise they are cleanup.

### O10. The reporting layer fails silently, so perceived progress is unreliable. (Severity: MEDIUM)
- Five consecutive weekly recaps, 08-29 through 09-26 (`C:\Prometheus\docs\weekly_recap_2026-09-26.md` from line 7), contain the
  generator's raw scratch reasoning ("We need to produce a weekly recap with sections...") instead of a recap. Nobody caught it. This is
  the operator's main summary channel.
- Other reporting errors:
  - S3 count corrected from 0.33 to 0.67 coordination per execution after publication (#1019).
  - RESULT.md left stale (#1038).
  - WORK_STATE `updated_at_utc` runs ahead of the commit times (#1057).
- **Refuted by:** a recap pipeline that checks its own output, plus a record of report errors falling over time.

### O11. Much of the motion ends in HOLD, PARK or rework rather than verdicts. (Severity: MEDIUM)
- LM01 went through PREREG v0.1 and v0.2 (#695, `6d57763f8`) and ended "HOLD / NOT LAUNCHED" (MWO-0004 G3).
- PTE-SI01 is on HOLD. ENVGATE-02 ended WINDOW_NOT_SUPPORTED. The Cosmos C3 coordinate-layer audit was REJECTed (`45e6c942a`).
- Theseus v0: H1 FAIL (#1125).
- WORK_STATE at end of day 09-30:
  - 6 of 18 seats READY or idle (Achilles, Aphrodite, Artemis, Nestor, Techne, Theseus), several "awaiting Aporia assignment".
  - 2 BLOCKED, 1 HOLD, 1 PARKED.
- **Refuted by:** a falling share of preregistrations that never reach a verdict.

---

## 3. Bottom line: what is actually established

**Established:**
- The lab has learned to *perform* the rituals of reliable science: preregistration commits, positive and cheat controls,
  pre-exposure freezes, adversarial review, errata.
- Given an auditor and an operator, it reliably *detects* many of its own errors.
- It has produced a handful of scoped, internally valid findings about its own synthetic substrates. Examples: Nestor's NPE
  gating mechanisms, the Ergon null, and the TECHNE-107 finding that the ASAL metric rewards noise.
- A few hygiene defect classes have been extinguished: committed-red tests, gitignore swallowing.
- Throughput rose by roughly six times, mostly through row micro-commits and coordination traffic.

**Not established:**
- That the rate or quality of scientific improvement is rising.
- That any rise is due to the system rather than the operator, a model change or seat churn.
- That results compound.
- That anything has been learned about the world outside the lab's own constructions.

The best available evidence on claim quality, the 09-30 audits, shows about 4 of 12 recent packages clean. No earlier
baseline exists to compare against. The most dramatic process episode (D2: 12 failed re-audits) ended only by operator
decree. The improvement claim is currently **unfalsified because it is unmeasured**, and the evidence that does exist
fits "a lab that produces defects and catches some of them later" at least as well as "a lab that is getting better".

## 4. Three measurements to demand before believing any improvement claim

1. **Cohort survival rate under a fixed, calibrated audit.**
   - Each fortnight, draw a random sample of headline claims. The producing seat does not choose them.
   - Audit them under one frozen protocol by a different model family or a human. Seed planted-defect positive controls to measure
     auditor sensitivity.
   - Report the fraction surviving with no MAJOR/BLOCKING defect and the severity-weighted defects per claim.
   - Improvement means survival rises while auditor sensitivity holds steady.
2. **Pinned-model replay benchmark.**
   - Build a frozen battery of past research tasks with known answers and planted traps: seed sharing, harness credit leak,
     post-exposure amendment, a control that cannot fail.
   - Run the current lab configuration against an earlier one with the model held fixed.
   - Measure correct verdicts, traps caught and time-to-verdict.
   - Only this separates system improvement from model upgrades and operator effort.
3. **Compounding per operator-hour.**
   - Count surviving results that become load-bearing inputs to *another seat's* later surviving verdict, plus any
     externally checked result.
   - Divide by logged operator interventions (prompts, MWO/CWO words, time boxes, parks).
   - Improvement means this ratio rises. If it is flat while commits rise by six times, the lab is getting busier, not better.
