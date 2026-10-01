# A3: Experiment ledger and verdict dynamics across seats (2026-09-06 .. 2026-09-30)

Read-only analysis. Repo: `C:\Prometheus-worktrees\aphrodite-harvest` (origin/main) plus the comms and gitlog datasets. Nothing in the repo was modified.

Companion CSV: `findings_A3_ledger.csv` (same directory). The full CSV is also embedded at the end of this file.

## 0. Method and how far to trust it

**Sources**
- `roles/*/WORK_STATE.json` experiments arrays.
- `ops/campaigns/C-001..C-003`, `ops/threads/TH-*`.
- Aphrodite `STATUS.md`, `engine/AMENDMENT_*` and `science/**`.
- Nestor `EXPERIMENT_GRAPH.jsonl` and `campaigns/`.
- Cosmos `c3/`, `c4/` and `campaigns/`.
- Ensorain `ensorain/*_VERDICT.md`, `arc3/**`, and the remote branch `origin/ensorain/base-role-adopt-2026-09-23` for 09-29/30 material that is not on main.
- Aether `AETH-0x` and C-002.
- Hecate `hecate/**`; Tyche `tyche/runs/**`; Theseus `theseus/**`.
- Archaeon `archaeon/**` and `CALIBRATION_LEDGER.md`.
- Bellerophon, Ananke `research/workers/W-*`, Artemis, Nyx `nyx/atlas/predictions` and Odysseus.
- Harmonia rulings and audits (`roles/Harmonia/rulings/`, `audits/EVIDENCE_AUDIT_2026-09-30.md`).
- Git subjects for FREEZE/PREREG/RESULT/verdict.

**Collection.** The Aphrodite rows were built directly from git (each `AMENDMENT_n` add-commit and its verdict commit). The other seats were swept by three parallel read-only sub-searches, then normalised by hand into one schema.

**Times.** All times are UTC, written MM-DD HH:MM in 2026. Git author times are -04:00 and were converted.
- **"Freeze"** is the commit that first added the prereg or amendment.
- **"Verdict"** is the commit or file that first recorded the result.
- **"Launch"** is often not recorded. `=frz` means the run started in the freeze commit's window.

**Unit of analysis.** One row is one adjudicated hypothesis test.
- A campaign is split into rows where its arms got different verdict classes. Examples: Aphrodite A17 has rows E1, E2/E3 and E4; Archaeon CMP1 has POS, NEG and INC rows.
- Nestor's exploratory `X-*` nodes are each one row. They are cheap, and there are 105 Nestor rows in all, so they dominate the raw counts. Section 1 therefore also reports figures with them excluded.

**Verdict classes**

| Class | Meaning |
|---|---|
| POSITIVE | The frozen bar was met. This includes instrument-qualification passes. |
| NULL | A valid null or negative, including WEAK_SIGNAL below the bar. |
| KILLED | Killed by a baseline, sham, control, attacker or cheap screen. |
| UNTESTABLE | Supply, quota, power, reachability or a positive control failed, so the question could not be asked. |
| INVALID | A design or instrument defect voided the run. |
| PARKED | Frozen but not run, or stopped by the operator. |
| OPEN | Running, or awaiting adjudication. |

**Flags**
- `screen_pre`: whether a pre-run screen or positive control existed.
- `failure_found`: PRE means a cheap check caught the problem before the expensive run. POST means it was found after the run, by the run itself, a reviewer or an audit.
- `relabel`: the verdict was later changed by an operator, Harmonia or a peer.
- `builds_on_pos`: the experiment was explicitly motivated by an earlier POSITIVE.

**Size.** 281 rows across 14 seats. Class mix: POSITIVE 107, NULL 89, UNTESTABLE 25, KILLED 23, INVALID 21, PARKED 10, OPEN 6.

**Reliability caveats**
- **The classes are mine**, mapped from each seat's own vocabulary. That vocabulary includes CUT_SUPPORTED, CAPABLE_NEGATIVE, WEAK_SIGNAL, INDETERMINATE, HORIZON_DEPENDENT and STEERING_REQUIRED. Boundary cases are flagged in the CSV `verdict_recorded` column so they can be re-mapped.
- **`screen_pre` = N is partly circular.** I often learned that a screen was missing *because* the run failed. Treat the screen x class cross-tab (section 3) as suggestive only.
- **Times marked `~` or `?` are approximate or unknown.** Cosmos C3-LAW, Nyx POET (frozen 09-19, run 09-30) and Archaeon CMP1/CMP3 have known discrepancies between reported and committed times.

## 1. Verdict-class mix over time and per seat

**Per seat.** U+I is UNTESTABLE + INVALID as a share of rows that reached a verdict.

| seat | rows | POS | NULL | KILLED | UNTEST | INVALID | PARKED | OPEN | U+I share |
|---|---|---|---|---|---|---|---|---|---|
| Nestor | 105 | 41 | 44 | 5 | 5 | 6 | 3 | 1 | 0.11 |
| Archaeon | 33 | 9 | 12 | 2 | 4 | 4 | 2 | 0 | 0.26 |
| Aphrodite | 30 | 11 | 6 | 2 | 6 | 3 | 2 | 0 | 0.32 |
| Ananke | 30 | 17 | 9 | 0 | 2 | 1 | 0 | 1 | 0.10 |
| Ensorain | 19 | 6 | 6 | 3 | 2 | 0 | 2 | 0 | 0.12 |
| Cosmos | 14 | 4 | 3 | 4 | 0 | 2 | 0 | 1 | 0.15 |
| Aether | 12 | 5 | 4 | 2 | 0 | 0 | 0 | 1 | 0.00 |
| Hecate | 9 | 3 | 1 | 2 | 2 | 1 | 0 | 0 | 0.33 |
| Bellerophon | 8 | 4 | 0 | 1 | 1 | 1 | 0 | 1 | 0.29 |
| Nyx | 7 | 3 | 0 | 0 | 1 | 1 | 1 | 1 | 0.40 |
| Artemis | 5 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0.00 |
| Tyche | 4 | 0 | 2 | 0 | 1 | 1 | 0 | 0 | 0.50 |
| Odysseus | 3 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0.00 |
| Theseus | 2 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 1.00 |

**Over time.** Buckets are by verdict date. PARKED and OPEN are excluded.

| verdict window | n | POS | NULL | KILLED | UNTEST | INVALID | U+I share | POS share |
|---|---|---|---|---|---|---|---|---|
| up to 09-17 | 24 | 6 | 8 | 2 | 5 | 3 | **0.33** | 0.25 |
| 09-18..21 | 17 | 6 | 4 | 2 | 4 | 1 | **0.29** | 0.35 |
| 09-22..24 | 78 | 27 | 33 | 7 | 4 | 7 | **0.14** | 0.35 |
| 09-25..27 | 58 | 27 | 22 | 4 | 2 | 3 | **0.09** | 0.47 |
| 09-28..29 | 53 | 30 | 11 | 5 | 4 | 3 | **0.13** | 0.57 |
| 09-30 | 29 | 9 | 8 | 3 | 6 | 3 | **0.31** | 0.31 |

Excluding the Nestor X-* nodes and the Ananke W-* workers, the U+I series is 0.33, 0.29, 0.15, 0.12, 0.19, 0.35. The shape is the same.

**Seat age.** This is hours since the seat's first recorded verdict.

| seat age | n | U+I share | POS share |
|---|---|---|---|
| first 24 h | 60 | **0.28** | 0.32 |
| 24-72 h | 6 | 0.00 | 0.67 |
| over 72 h | 193 | **0.15** | 0.42 |

**Reading**
1. **The fleet-wide U+I share fell from about 0.3 to about 0.1 between 09-17 and 09-27, then rebounded to 0.31 on 09-30.** The rebound is almost entirely composition. Eight of the 9 U+I verdicts on 09-30 come from Hecate, Tyche and Theseus, which were all in their first day, plus one each from Bellerophon REPL-02 and Ananke W-Y. A new seat's first-day failure rate (0.28) is about twice a mature seat's (0.15).
   - So the fleet curve tracks *how many seats are in their first day*, not a fleet-level process improvement.
2. **Within mature seats the trend is mixed. "Better design-before-run" is not a fleet-wide fact.**
   - **Falling:**
     - Nestor: 0.67 (cw01 09-18, mostly DESIGN UNREACHABLE gate kills), then 0.10, 0.05, 0.09.
     - Archaeon: 0.33 (H0H5/S-series 09-10..13), then about 0 to 0.2.
     - Ensorain: 0.22 (E0/D2), then 0, 0.
     - Aether: 0 throughout.
   - **Rising: Aphrodite.** By bucket it went 0.14, 0.25, 0.50, 0.60. In verdict order, windows of 6 run 1/6, 1/6, 1/6, 3/6, then 3/4. It is the only mature seat whose defect rate *rose*, and it said so itself: T49, "3 of the last 4 assays failed on design or supply".
   - The rise coincides with Aphrodite's move from engine-capability questions (A3-A14) to supply-bound recurrence assays (A15-A22). Those need a foundry to produce a quota of qualified task families before any arm can run. **The failures are supply failures, not biology.**
3. **The POSITIVE share rose from 0.25 to 0.57 through 09-28/29.** Section 6 explains why this should not be read as better science. Much of it is cheap confirm-after-explore chains (Nestor C-*), instrument qualifications (Ananke swap-statistics workers) and replications inside one substrate.

## 2. Time from freeze to a valid verdict

A valid verdict here means POSITIVE, NULL or KILLED.

**Median hours by seat**

| seat | median h | n |
|---|---|---|
| Hecate | 0.10 | 6 |
| Artemis | 0.17 | 4 |
| Ensorain | 0.38 | 14 |
| Cosmos | 0.51 | 10 |
| Aphrodite | 0.60 | 19 |
| Nestor | 0.71 | 86 |
| Odysseus | 0.8 | 2 |
| Tyche | 1.1 | 2 |
| Aether | 1.25 | 10 |
| Archaeon | 2.4 | 15 |
| Bellerophon | 4.1 | 5 |
| Nyx | 6.7 | 3 |
| Ananke | 7.1 | 6 |

The longest runs: Nestor Z80A-72H took 78.7 h, Bellerophon MD 60 h, Ananke PTE-C1 59 h including the hold, and Nyx POET 265 h, of which 11 days was the queue.

**Median hours by verdict window**

| window | median h | p75 h |
|---|---|---|
| up to 09-17 | 2.4 | 2.5 |
| 09-18..21 | 0.36 | 0.48 |
| 09-22..24 | 0.52 | 1.17 |
| 09-25..27 | 1.14 | 1.80 |
| 09-28..29 | 1.83 | 3.98 |
| 09-30 | 0.68 | 1.25 |

UNTESTABLE and INVALID rows took a median 0.58 h from freeze to verdict, about the same as valid ones. A defect is typically discovered *during* the run, not after a long wait.

**Reading**
- **The freeze-to-verdict cycle is very short: median under 1 h.** Most "experiments" are minutes-to-hours CPU runs. Cycle time is not the bottleneck.
- **No improving trend.** The cycle got longer from 09-22 to 09-29 because seats moved to larger, multi-day or Fabric-dispatched runs: Bellerophon MD, Ananke workers, Aether Fabric, E-003.
- **The useful clock is hypothesis to first valid verdict across re-freezes.** Aphrodite's chains show it:
  - **Recurrence-assay line (C1, C2, C3, C3R, C3R2, C3R2C).** A18 froze 09-27 22:49. The only valid verdicts were A19's NO at 09-28 01:20 and A23's YES at 09-28 14:31. That is **15.7 h and 6 amendments, of which 4 were UNTESTABLE/INVALID**, for one valid positive.
  - **Bounded-RSI line (A9, A10, A11, A15, A16, A17).** A9 froze 09-22 08:30. A17-E1 gave a valid NO on 09-26 14:09, **4.2 days and 6 amendments later**. Three intermediate verdicts were INVALID/UNTESTABLE, and the line was never answered positively.
  - **S1 identity (A12 plus 3 addenda).** 09-23 20:29 to 09-24 14:20, **17.9 h and 3 failed runs** before the global FAIL and local PASS.
  - **Other seats show the same "re-freeze until testable" pattern:**
    - Cosmos certificate v1, v2, v3 (minutes).
    - Ensorain E0, E1, E1.5 (positive control fixed by E1.5, about 10 h).
    - Hecate probe rounds R1, R2, R3 (generator repaired in about 1 h).
    - Tyche v0 to v1 (about 4 h).
    - The E-003 ancestry prereg, v1 to v5 (about 1 day, with 4 versions judged UNSOUND by review).

## 3. Cheap kills before the expensive run vs failures found afterwards

**Counts.** `failure_found` was set on 105 of 281 rows: **PRE 35, POST 70**. By class:

| class | PRE | POST |
|---|---|---|
| INVALID | 3 | 18 |
| UNTESTABLE | 7 | 18 |
| KILLED | 6 | 9 |
| POSITIVE (defect found later) | 6 | 11 |
| NULL | 6 | 13 |

**POST outnumbers PRE in every verdict window except 09-18..21.** That window is the Nestor cw01 and Archaeon CMP2-5 gate era, when QUALIFY and world-screen gates killed designs before evolution.

| window | PRE | POST |
|---|---|---|
| up to 09-17 | 6 | 7 |
| 09-18..21 | 7 | 4 |
| 09-22..24 | 3 | 25 |
| 09-25..27 | 4 | 11 |
| 09-28..29 | 5 | 10 |
| 09-30 | 3 | 13 |

### 3a. Cheap kills (exemplary)

| Seat | What the cheap check caught |
|---|---|
| Aether | AETH-03 PD01/PD02: $0 128^2 CPU scouts killed 6 of 7 one-change physics laws before any GPU spend. The platform also refused flights without a scout bundle ($0). |
| Cosmos | The C3 law was killed by a two-review, roughly 5-minute coordinate audit **before** sealed holdout D2 was spent (Harmonia Addendum Q: "correct pre-holdout kill"). Smoke runs also caught certificate v1/v2 defects before any law work. |
| Nestor | cw01 QUALIFY/RECONCILE gates closed e06, e07, e09 as DESIGN UNREACHABLE at about 0 compute. The cw01-e01 smoke run caught 6 defects, 4 of which would have faked the effect. C9-D14 was caught at reading time, before the 1,200-run C9. The D2 firewall failed 12 audits before PASS, with no science exposed. |
| Archaeon | The CMP5 world screen left 9/25 worlds eligible. CMP3 slots that failed their own positive control were repaired before data. CMP2 at n>=10 with common random numbers killed most CMP1 weak positives cheaply. The H1H0 degeneracy row stopped a replicate that would have been identical by construction. |
| Ananke | W-E: the positive control predicted the power-limited NO in advance. W-Y: the known-answer plant failed, so it stopped at 0.25 core-h. PTE-C1b: eligibility was checked pre-data. |
| Hecate | The round-2 control-first pilot flagged 6/13 specs as unattainable; generator v2 then had 0 instrument failures. |
| Tyche | v1: reachability was measured pre-freeze and R2 removed. |
| Nyx | particles-001: the positive control fired the stop. |
| Aphrodite | A4: the reachability gate (seconds). A22/A23: a supply feasibility screen. |

### 3b. Failures found after the expensive run (the costly ones)

| Seat | What was found after the run |
|---|---|
| Nestor | **Z80A-72H** (72 wall-h, 23,471 runs): after the run, defects D04/D05 showed 910/1031 "replicators" were splice artifacts. **C9-H1** (part of 40.4 CPU-h, 1,200 runs): the intervention never reached the task (C9-D16). **X-PAIR-NORECOMB**: relabelled INVALID 4 days later (no positive arm). **P-11 assay**: UNSOUND per Artemis; its results were reused across about 10 experiments before that. |
| Archaeon | **ENVGATE-01** (about 9.3 h): relabelled PARTIALLY. **Deep block** "0.0 founder material": retracted. |
| Ananke | **PTE-C1** (12 h): the packet-ablation window and frozen-routing null were vacuous (errata). |
| Bellerophon | **Grounding** (3 h 51 m x 18 workers): G6a 160/160 became 103/160, found 6 days later. **REPL-02** (750 runs): the positive control was 0/50 only after the run. **E-003 BEE**: VALIDATED became ALTERED/OPEN after audit. |
| Tyche | v0 attempt 1: 13 core-h lost to BLAS oversubscription. v0: H1/H6 UNREACHABLE_BY_DESIGN, knowable pre-run per Harmonia. |
| Aether | **AETH-01 First Light** ($2.02): the $0 scout had already predicted the null; run anyway. **AETH-02**: stale observer, truncated trajectory. |
| Ensorain | **E1**: the positive-control failure cause was "identified before the run", but it ran anyway. **WTP-02/03**: the constant learner and the N6 baseline surfaced only post-data. |
| Aphrodite | A15, A16, A17-E2/E3, A18, A20, A21, A22: the supply/quota or design defect was discovered **by running the frozen assay**. These were cheap ($0, minutes to about 2 h on M4), so cost was in sequence time and amendment count, not compute. |

**Net.**
- Cheap pre-run screens exist and work where they are used.
- Every seat that had a costly post-run failure (Nestor, Archaeon, Ananke, Bellerophon, Aether, Tyche) had a screen in place. The screen did not test the failure that occurred:
  - a positive control that cannot fire;
  - a negative control with zero cases;
  - ceiling rulers;
  - compute and memory sizing;
  - quota or supply.
- Harmonia's 09-30 evidence audit names the same pattern, "uncalibrated negative claims" and "ceiling rulers", and proposes "a detector's absence claim needs a positive control for that class".

## 4. Did methods transfer? (the T49 test case and equivalents)

**The T49 lesson, within Aphrodite**
- The lesson is in `roles/Aphrodite/science/compounding/BACKLOG_COMPOUNDING.md:514`, `science/arc3/ARC3_SYNTHESIS_2026-09-28.md:99,217`, `ops/threads/TH-021.md:23` and `ops/campaigns/C-003/CAMPAIGN.md:37`.
- The supply screen (`science/arc3/c3r2_feasibility/genuine_motifs.py`) was built *after* A21, at commit 29453b20c, 09-28 07:40Z. A22 was frozen 5 minutes later (684fcf392) with a "supply-screened panel".
- **A22 nonetheless failed its quota.** It filled 5/8 against n>=6, short on OTHER-motif spares, which the screen did not cover.
- A23 doubled the spares and lowered k proportionally, then filled 10/12 and returned the first clean verdict.
- The lesson was codified as T49 at 09-28 10:10Z (commit "backlog T47-T50", -04:00 06:10). That is 3 minutes after A23 was frozen and before its result. A23 is the only run that followed the screen, and the "countermeasure worked" verdict on T49 rests on that single run (`BACKLOG_COMPOUNDING.md:528`).
- **Aphrodite has run nothing since.** Its state is HOLD/READY. NEXT_SESSION and its 09-30 heartbeat (comms #1193) state the order "T49 supply screen, then a frozen AMENDMENT, then a Fabric lease" for T51.
- **Whether it is obeyed when it matters cannot be observed yet.**

**Cross-seat adoption of T49**
- In the comms dataset, "supply screen"/T49 appears **only in Aphrodite's own messages**: 1 message, #1193.
- In the repo, the phrase appears only in Aphrodite files and its own C-003/TH-021.
- **No seat cites T49. No seat adopted it from Aphrodite.**

**Equivalent screens other seats used.** All of these were adopted independently, and most of them earlier:

| Seat | Screen | When |
|---|---|---|
| Nestor | QUALIFY gates, smoke-before-budget, "fail-on-old-code" self-tests, replay-match gates | from 09-17 |
| Archaeon | WORLD_SCREEN eligibility before prereg (CMP5) | 09-18 |
| Archaeon | reachability tables (lesson from CMP1's 3 "assay incapable" slots) | — |
| Ensorain | LM01 dev margin sweep (29/75 strata TESTABLE) | before freeze, 09-25/26 |
| Ensorain | LM02 REF_HOLD instrument-OK gate | — |
| Hecate | Pass 3 v2 attainability check before spec freeze | — |
| Tyche | v1 reachability measured pre-freeze | — |
| Aether | $0 scout tier | — |
| Ananke | known-answer plants (W-K fixtures, then the H-PLANT gate) | — |
| Ananke | "positive control FIRED" definition (Aporia ruling #675) | 09-25 |

The Ananke and Ensorain LM01 design norms (per-cell positive controls, replication power >=80% "else UNTESTABLE") came from **Aporia/Cyclops joint stewardship** on 09-25/26: comms #592-#699, about 15 "concur -> JOINT" rulings. On 09-26 the operator removed that stewardship ("experiments no longer managed via Aporia or Cyclops"). From then on, design norms propagated by *audit* (Harmonia 09-30, Artemis challenges) rather than by a shared pre-freeze checklist.

**Did reusing instruments avoid earlier failure modes? Mostly not across seats; often yes within a seat.**
- **Not avoided:**
  - **Nestor P-11:** reused in about 10 experiments before Artemis showed it certifies construction, not heredity.
  - **Bellerophon REPL-01:** rebuilt Nestor's C-A3-INTERNALIZE in BEE. It repeated the "no demonstrated SURVIVES path" defect already logged on 09-29 for E-003 Q4 (DEF-BEL-004). REPL-02 then repeated it again (positive control M6 0/50).
  - **TH-014:** the same credit-leak error was made independently by Archaeon, BEE and NPE.
  - **Cosmos:** the "zero-parameter definition rung" failure that Artemis R-14 found in C0 recurred in C3. It was caught pre-holdout the second time, which is a partial avoidance.
  - **Tyche v2:** repeated v0's memory stop.
  - **Ensorain E1:** inherited E0's positive-control constants and failed the same way.
- **Avoided:**
  - Ensorain E1.5 (own constants, positive control passed).
  - Nestor X-TASK-GATE (guesser lesson from C9-H1R built into the design).
  - Aether E-010..E-012 (regression hash gates reuse E-009).
  - Hecate generator v2.
  - Ananke swap-statistics chain W-M, W-N, W-Q, W-U, W-W, W-X (instrument promoted only after known-answer and must-fail checks).
- **New seats re-learn rather than inherit.**
  - Hecate's alien B/C runs had no quota screen and hit free-tier quota and truncation.
  - Theseus had no planted positive control. Its packet says to add one next.
  - Tyche lost 13 core-h to BLAS oversubscription.
  - This is the strongest evidence that lessons stay seat-local.

## 5. Do positives compound?

**Positives that compound inside one seat and one substrate**
- **Nestor NPE chain** (each step a confirmed C-* on fresh seeds):
  - C-SELFLOC and C-ENERGY (09-24)
  - then X-DENSE-OPS-R, C-DENSE and C-ABLATE
  - then (09-26) C-DENSE-COPY
  - then C-STATELESS-FFA6, then (09-28) C-ZERO-SPECIFIC
  - then C-A3-INTERNALIZE, then (09-30) X-MAT-INTERNALIZE (ENDOGENOUS 8/8)
  - X-TASK-GATE is frozen on top of it.
  - This is the longest compounding chain in the ledger: about 7 confirmed links over 6 days.
  - **Caveats:**
    - Several links were later re-described or narrowed: C-STATELESS-FFA6, C-CORE (operator withdrew the SI framing), C-CRITICAL-MASS (post-hoc superadditivity killed by X-DOSE-CURVE).
    - The substrate changed under the chain several times: repaired VM, dense VM, DENSE_COPY VM, ATOMIC runner, register-reset worlds.
    - The P-11 ruler beneath early links was later ruled UNSOUND.
- **Aether C-002:**
  - E-006 (rcv_add/rcv_str NEW_BEHAVIOUR)
  - then E-008 (horizon falsifier did not weaken it)
  - then E-009 (REPLICATED on fresh seeds)
  - then E-010 (STEERING_REQUIRED, Harmonia SUPPORTED)
  - then E-011 (PARTIAL)
  - E-012 is frozen.
  - This is the cleanest compounding chain: each link is a preregistered lesion or replication of the previous positive, guarded by hash-identity regression gates.
- **Aphrodite:**
  - S1-local PASS, S2 PASS and S3 YES fed **S4 ABSTRACTION_TRANSPLANT YES** (09-24) and A17-E4 S1_NECESSITY SUPPORTED.
  - The next six attempts to build on S4 (A15-A22) yielded 1 valid NO and 5 UNTESTABLE/INVALID.
  - A23 YES (09-28) is scoped to "mechanism under constructed recurrence ... NOT retroactive RSI evidence". Its successor T51 (natural recurrence) has not run.
  - So Aphrodite's positives compounded once (S1 to S4), then stalled on supply.
- **Ananke:** the swap-verdict instrument chain (REL2, REL3, REL4, REL5, then promoted) compounds as an *instrument*. Mechanism-side positives (W-A law, W-I trajectories) were narrowed by later workers rather than extended.
- **Bellerophon:** coupling (READY_FOR_MULTIDAY) fed MD (LADDER_CLIMBED, PROTECTION_EVOLVED) — two links, partial.

**Positives that did NOT survive being built on**
- **Cosmos:** law A gave C0b, C0e and C0m PASSes, and law B gave C2. Both were **RESTRICTED on 09-29** (no margin over the zero-parameter rung). The "compounding" was on a positive that was itself not above baseline.
- **Archaeon:** CMP1 weak positives were retested in CMP2 at n>=10 and 7 of 10 died (CAPABLE_NEGATIVE).
- **Ensorain:** WTP-02's mechanical "EXPAND" was built on by WTP-03, and both were killed by trivial baselines.
- **Cross-seat transfer of a positive: 0 clean successes in the ledger.**
  - Nestor C-A3-INTERNALIZE was rebuilt in BEE (Bellerophon REPL-01): **DISAPPEARS (K3)**, descent UNRESOLVED, and REPL-02 residue NOT_REPLICATED.
  - NPE/SFE positives were transplanted into BEE (Atlas-BEE a1-a6): a1 INVERTED, a2/a3 CHANGED, a4/a5 ABSENT, only a6 PRESERVED.
  - ENVGATE-01 R2 survived into C-001 E-001, but as a re-reading rather than a replication.
  - The E-003 cross-engine ancestry tracer ended UNTESTABLE (NPE flip coverage) and OPEN (BEE).

**Bottom line.** Compounding is real **within a seat on its own substrate** (Nestor, Aether, partly Aphrodite and Ananke). Positives have **not** been shown to carry across seats or substrates; every cross-substrate attempt in the ledger weakened or erased the effect. By the stated criterion (compounding positives are the key signal), the evidence is seat-local compounding with no demonstrated portability.

## 6. Confounds

1. **Seat entry and turnover.**
   - Three seats (Hecate, Tyche, Theseus) were born and produced verdicts on 09-29/30. Aphrodite was created 09-17. Archaeon's early record is H0H5/SFE work from before comms existed (09-06..13).
   - Fleet-level shares are dominated by which seats are in their first day (section 1). Any "trend" must be read within a seat.
2. **Unequal recording granularity.**
   - Nestor records every exploratory node in a graph (105 rows). Aether, Cosmos and Bellerophon record campaigns. Archaeon's ten-slot campaigns are collapsed to 1-3 rows here.
   - Ananke WORK_STATE lists only its latest 14 workers. Earlier workers (W-A..L) come from reports.
   - Raw class shares therefore weight Nestor's cheap explore-confirm loop heavily, which inflates both POSITIVE and NULL.
3. **Selection of what is recorded.**
   - WORK_STATE arrays are curated and truncated: Cosmos shows 1 string, Nestor 2.
   - 09-29/30 Ensorain work exists only on an unmerged branch.
   - Aphrodite's 09-17/18 toy studies (RSI toys, swarm) are visible only in git subjects.
   - Several Nyx/Harmonia packets never ran (GZIP-003).
   - Failures that a seat abandoned without a commit are invisible. The ledger is biased toward experiments that produced a committed artifact, which probably *under-counts* early-stage UNTESTABLE outcomes.
4. **Operator and peer rulings that relabel.** 44 of 281 rows (16%) carry a later relabel.
   - **Operator relabels:**
     - ENVGATE-01 (CAUSALLY to PARTIALLY);
     - Ensorain E1.5 (CLOSE to INTRIGUING/PARKED);
     - WTP-02 (EXPAND to PARK/REDESIGN);
     - E0 ("useful negative");
     - Nestor C-CORE/SI framing withdrawn;
     - Aphrodite S4 accepted with "BOUNDED_RSI not yet established";
     - CMP5 slot to POST-HOC.
   - **Harmonia relabels:**
     - Tyche H1/H6 to UNREACHABLE_BY_DESIGN;
     - Hecate W6 to KNOWN_ANALOGUE_FOUND;
     - Nyx POET to not confirmatory;
     - E-003 BEE VALIDATED to ALTERED/OPEN;
     - Odysseus S3 coordination recoded 0.33 to 0.67.
   - **Peer relabels:**
     - Artemis on X-PAIR-NORECOMB (to INVALID), P-11 (UNSOUND) and C0 laws (RESTRICTED);
     - Artemis #871 on A23 gate defects (labels not changed).
   - I classified rows by their **current** label. Relabels move rows mostly from POSITIVE to KILLED/NULL/INVALID, so the *as-first-recorded* POSITIVE share is higher than shown. The operator's 09-30 Ensorain ruling ("low power must never mean unchanged", which became QUARANTINED) changes gate semantics prospectively.
5. **Changing substrates.** Almost every chain changed substrate mid-stream:
   - Nestor: 4+ VM variants.
   - Cosmos: coordinates v1 to v4, certificates v1 to v3.
   - Aether: A40 GPU, CPU, RunPod pods, Fabric, BUCKKEEP.
   - Archaeon: SFE schema 7/8/9, then WSE, then vmcopy32, then taint VM.
   - Aphrodite: engine v1, extended grammar, W5 depth-3 world, T4 tribunal, ruler v2.
   - A positive at step n and a null at step n+1 are often not on the same substrate.
6. **Model versions.**
   - Seats ran claude-opus-5 (Nestor 09-14) and later claude-opus-5-5[1m] (Nestor 09-30). Most seats ran opus-5-5.
   - Sub-workers sometimes defaulted to claude-sonnet-5: C-001 deep-block W1-W3, and Hecate's meta generator.
   - Hecate's alien assay used gpt-oss-120b and gemini-3.6-flash, with output budgets changed mid-run.
   - Seat sessions also reset: Aphrodite's 09-25 and 09-30 reset checkpoints, and instance tags like m2-475d761f.
   - Model and session identity are not recorded per experiment in most ledgers, so I cannot separate a "learning" effect from a model or session change.
7. **Governance changes.**
   - Aporia/Cyclops stewardship was in force 09-25/26 and then revoked.
   - CWO-2026-09-30B froze auto-promotion; Artemis D003/D004 were submitted in violation and D005 was cancelled.
   - CWO-C made Aporia the dispatcher again on 09-30.
   - The rules for what counts as a "valid" run changed during the window.
8. **Cheapness distorts the PRE/POST comparison.** Many POST failures (all of Aphrodite's) cost minutes of free CPU. So "found after the run" is often the *rational* screen when the run is cheaper than a separate screen. Only rows with recorded large compute (section 3b) are true expensive failures.

## 7. Cannot conclude

- **Whether T49 is obeyed.** Aphrodite has run no experiment since writing it. T51 is authorised but undispatched.
- **Whether any seat adopted T49.** No citation was found in comms or the repo. Independent equivalents exist but predate it, and there is no evidence that they derived from it.
- **A fleet-level decline in UNTESTABLE/INVALID that is not confounded by seat age.** Within-seat declines are visible for Nestor, Archaeon and Ensorain. Aphrodite's share rose. The new 09-30 seats reset the fleet curve.
- **Whether higher late POSITIVE shares mean better science.** They coincide with cheap confirm chains, instrument workers and post-hoc relabels that later removed positives. The as-first-recorded vs current-label difference was not computed row by row.
- **True compute per experiment.** Compute is recorded for under half the rows, in mixed units (lives, runs, core-h, dollars, wall-h). No cost-weighted PRE/POST comparison is possible.
- **Launch timestamps** for most rows (only freeze/verdict commits are reliable). Freeze-to-launch latency is not measurable.
- **Cross-substrate portability of any positive.** No successful case exists, but there are also few attempts: REPL-01/02, Atlas-BEE, E-003. Absence of success is not yet evidence of non-portability.
- **The effect of model version or session resets** on design quality. Per-experiment model identity is not recorded.
- **Completeness.** Seats outside the requested list were not swept, and experiments with no committed artifact are invisible. Examples: Harmonia's own studies, Vivarium, Atlas, Crius, Hypatia, Herakles, Proteus. Branch-only material other than Ensorain's was not systematically read.

## 8. Ledger table (compact)

All rows. The full columns (hypothesis, launch, compute, relabel, builds_on_pos) are in the CSV.

Column key:
- **scr**: pre-run screen or positive control existed.
- **found**: PRE or POST failure detection.
- **rel**: relabelled.
- **bop**: builds on an earlier positive.

| id | seat | substrate | freeze | verdict | recorded verdict | class | scr | found | rel | bop | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| APH-RSI-TOYS | Aphrodite | python toys | 09-18 01:01 | 09-18 01:30 | 9 SUPPORTED/3 REFUTED/3 INDETERMINATE | POSITIVE | Y | - | N | N | git 07fcc2509 |
| APH-SWARM | Aphrodite | python toys | 09-18 04:47 | 09-18 04:57 | results; toys stopped after external review | PARKED | Y | - | N | N | git acc40e902, 7bb8ff982 |
| APH-C0 | Aphrodite | C0 generative worlds | 09-18 05:38 | 09-18 05:47 | PASS (operator ACCEPTED) | POSITIVE | Y | - | N | N | roles/Aphrodite/science/campaign0/RESULTS_C0_2026-09-18.md |
| APH-C0B | Aphrodite | C0 pathology generator | 09-18 12:12 | 09-18 12:17 | FAIL on power, calibration intact | NULL | Y | - | N | Y | roles/Aphrodite/science/campaign0/RESULTS_C0B_2026-09-18.md |
| APH-C0C | Aphrodite | C0 quadrature-truth generator | 09-18 16:26 | 09-18 16:30 | PASS | POSITIVE | Y | - | N | Y | roles/Aphrodite/science/campaign0c/RESULTS_C0C_2026-09-18.md |
| APH-C1 | Aphrodite | Campaign 1 (no eligible substrate) | 09-19 09:50 | - | FROZEN and UNRUN (blocked on other seats' contracts) | PARKED | Y | - | N | Y | roles/Aphrodite/science/campaign1/PREREG_C1_TRANSPLANT_2026-09-19.md |
| APH-ENGINE-V1 | Aphrodite | local engine v1 | 09-21 12:21 | 09-21 12:27 | discovery WORKS; coprime shortcut; clone lineages | POSITIVE | Y | POST | N | N | roles/Aphrodite/engine/README.md |
| APH-A3-2B | Aphrodite | local engine | 09-21 13:01 | 09-21 13:09 | yield 0/16, validity scar | INVALID | N | POST | N | Y | git 8a1fee278, 92f013c85 |
| APH-A4-2C-GATE | Aphrodite | local engine | 09-21 ~16:00 | 09-21 16:28 | STOPPED at reachability gate | KILLED | Y | PRE | N | Y | git aeaadcfaf |
| APH-A5A6-2C | Aphrodite | local engine (ext. grammar) | 09-21 18:23 | 09-22 01:32 | load-bearing mechanism discovered, extrapolates | POSITIVE | Y | - | N | Y | git 48e17a7d1 |
| APH-A7-S3LICE | Aphrodite | local engine | 09-22 05:05 | 09-22 05:12 | DIRECT_COMPETENCE_REUSE = NO (scratch control vacuous) | NULL | Y | POST | N | Y | git 173c08649 |
| APH-A8-SLICE4 | Aphrodite | local engine | 09-22 07:42 | 09-22 08:08 | STRUCTURAL_SEARCH_LEVERAGE = YES | POSITIVE | Y | - | N | Y | git 74f857091 |
| APH-A9-T3A | Aphrodite | local engine | 09-22 08:30 | 09-22 08:38 | BRSI NO; sham contained answer; INCONCLUSIVE_CONTROL_INVALID | INVALID | Y | POST | N | Y | git ba88978c0 |
| APH-A10-T3B | Aphrodite | local engine | 09-22 08:45 | 09-22 17:21 | BRSI NO; search leverage YES_LOCAL 47x | NULL | Y | - | N | Y | git 4d87b0bd4 |
| APH-A11-T3C | Aphrodite | local engine | 09-22 23:16 | 09-23 00:02 | BRSI NO; donor none, two SHAMS did | KILLED | Y | - | N | Y | git 4469736ca |
| APH-A12-S1 | Aphrodite | local engine | 09-23 20:29 | 09-24 14:20 | runs 1-3 FAIL; GLOBAL FAIL; campaign-local PASS | NULL | Y | POST | N | N | roles/Aphrodite/engine/AMENDMENT_12_ADDENDUM_3_2026-09-24.md |
| APH-A13-S2 | Aphrodite | local engine | 09-23 21:16 | 09-24 14:49 | S2_PASS | POSITIVE | Y | - | N | Y | git 52dad4db7 |
| APH-A14-S3 | Aphrodite | local engine | 09-23 21:16 | 09-24 14:49 | ENDOGENOUS_ABSTRACTION = YES | POSITIVE | Y | - | N | Y | git 52dad4db7 |
| APH-A14-S4 | Aphrodite | local engine | 09-23 21:16 | 09-24 15:11 | YES all 8 conditions; operator: BRSI not yet established | POSITIVE | Y | - | Y | Y | roles/Aphrodite/engine/S4_RESULTS_2026-09-23.json |
| APH-A15-G2 | Aphrodite | local engine | 09-24 16:19 | 09-24 16:39 | STOP at catalog 2/7<3; UNTESTABLE catalog | UNTESTABLE | N | POST | N | Y | git a9a64c7d9 |
| APH-A16 | Aphrodite | local engine | 09-24 18:36 | 09-24 19:51 | foundry 6%; E1/E2 untestable; E4 INCONCLUSIVE | UNTESTABLE | N | POST | N | Y | git bb47c233c |
| APH-A17-E1 | Aphrodite | local engine | 09-26 13:33 | 09-26 14:09 | E1 BRSI NO (valid novelty failure) | NULL | Y | - | N | Y | pivot/APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-26.md |
| APH-A17-E2E3 | Aphrodite | local engine | 09-26 13:33 | 09-26 14:09 | E2 UNTESTABLE (catalog); E3 UNTESTABLE | UNTESTABLE | N | POST | N | Y | same |
| APH-A17-E4 | Aphrodite | local engine | 09-26 13:33 | 09-26 13:39 | S1_NECESSITY SUPPORTED 3/3 vs 0/3 | POSITIVE | Y | - | N | Y | git fb5628435 |
| APH-A18-C1 | Aphrodite | local engine W5 + T4 | 09-27 22:49 | 09-27 23:28 | UNTESTABLE (supply 0/12; seat's supply-screen flaw) | UNTESTABLE | N | POST | N | Y | roles/Aphrodite/engine/A18_C1_RESULT_2026-09-27.json |
| APH-A19-C2 | Aphrodite | local engine W5 | 09-27 23:28 | 09-28 01:20 | G1_STEPPING_STONE NO; GENERIC 0/2; S-NAT UNTESTABLE | NULL | Y | - | N | Y | roles/Aphrodite/engine/A19_C2/ |
| APH-A20-C3 | Aphrodite | local engine W5 | 09-28 05:36 | 09-28 06:49 | UNTESTABLE (observe floor vs escrow cliff) | UNTESTABLE | N | POST | N | Y | roles/Aphrodite/engine/A20_C3/A20_C3_RESULT_2026-09-28.json |
| APH-A21-C3R | Aphrodite | local engine W5 | 09-28 06:49 | 09-28 07:40 | INVALID_DESIGN_DEFECT (inert motifs) | INVALID | N | POST | N | Y | git 29453b20c |
| APH-A22-C3R2 | Aphrodite | local engine W5 | 09-28 07:45 | 09-28 10:06 | UNTESTABLE (5/8 fillable <6) | UNTESTABLE | Y | POST | N | Y | git 8d47bbf9d |
| APH-A23-C3R2C | Aphrodite | local engine W5 | 09-28 10:07 | 09-28 14:31 | YES; GENERIC 3/3; p=0.0078; constructed recurrence | POSITIVE | Y | POST(minor, Artemis #871) | N | Y | roles/Aphrodite/engine/A23_C3R2C/A23_C3R2C_RESULT_2026-09-28.json |
| NES-cw01-e01 | Nestor | cw01 policy world | 09-17 20:54 | 09-17 21:25 | COMPLETE 5/5 | POSITIVE | Y | PRE | N | N | roles/Nestor/campaigns/cw01-2026-09-17/experiments/cw01-e01/RESULT.json |
| NES-cw01-e02 | Nestor | cw01 | 09-17 21:27 | 09-17 21:57 | NULL | NULL | Y | - | N | N | .../cw01-e02/RESULT.json |
| NES-cw01-e03 | Nestor | cw01 | ? | 09-17 22:13 | COMPLETE | POSITIVE | Y | - | N | N | .../cw01-e03/RESULT.json |
| NES-cw01-e04 | Nestor | cw01 | ? | 09-18 00:16 | INCONCLUSIVE (noise floor measured post-run) | KILLED | N | POST | Y | N | .../cw01-e04/RESULT.json |
| NES-cw01-e05 | Nestor | cw01 | 09-18 07:24 | 09-18 08:07 | NULL | NULL | Y | PRE | N | N | .../cw01-e05/RESULT.json |
| NES-cw01-e06 | Nestor | cw01 | ? | 09-18 11:23 | DESIGN UNREACHABLE (gate Q16) | UNTESTABLE | Y | PRE | N | N | roles/Nestor/campaigns/cw01-2026-09-17/CAMPAIGN_STATE.json |
| NES-cw01-e07 | Nestor | cw01 | 09-18 12:13 | 09-18 12:30 | DESIGN UNREACHABLE (gate refused) | UNTESTABLE | Y | PRE | N | N | same |
| NES-cw01-e08 | Nestor | tensor-train organism | 09-18 14:01 | 09-18 14:12 | INCONCLUSIVE (contrast NOT_VERIFIED) | UNTESTABLE | Y | POST | N | N | .../cw01-e08/RESULT.json |
| NES-cw01-e09 | Nestor | algorithmic soup | - | 09-18 14:23 | DESIGN UNREACHABLE (reconcile) | UNTESTABLE | Y | PRE | N | N | CAMPAIGN_STATE.json |
| NES-cw01-e10 | Nestor | mutable graph physics | - | - | PENDING | PARKED | - | - | N | N | CAMPAIGN_STATE.json |
| NES-Z80A-72H | Nestor | Z80 x Atlas grammar | 09-19 14:49 | 09-22 21:30 | WEAK_SIGNAL; narrowed 3x; 910/1031 splice artifacts | NULL | Y | POST | Y | N | roles/Nestor/FINDINGS.md s.A |
| NES-S2-P11 | Nestor | P-11 causal-copy assay | 09-23 13:22 | 09-23 13:22 | INSTRUMENT 14/14 (later UNSOUND per Artemis) | POSITIVE | Y | POST | Y | N | roles/Nestor/campaigns/z80atlas-verify-2026-09-22/P11_SPEC.md |
| NES-S1B-H4 | Nestor | replays | 09-23 | 09-23 13:36 | INVALID: control crossed first; withdrawn | KILLED | Y | - | N | Y | .../H4_AUTOPSY.md |
| NES-S1C-P11 | Nestor | P-11 | 09-23 13:38 | 09-24 04:32 | WEAK_SIGNAL 57 survive | NULL | - | - | Y | Y | .../S1C_P11_REASSAY.md |
| NES-C9-H3RULER | Nestor | C9 | 09-24 10:48 | 09-24 11:06 | R3 9/9 after D14 caught pre-freeze | POSITIVE | Y | PRE | N | N | .../H3_RULER_TOURNAMENT.json |
| NES-C9-H1 | Nestor | repaired Z80 VM | 09-24 11:06 | 09-24 17:52 | INVALID (C9-D16 wiring) after 1,200 runs | INVALID | Y | POST | Y | N | roles/Nestor/campaigns/z80atlas-verify-2026-09-22/observatory/C9_OUTCOME_AND_ADDENDUM.md |
| NES-C9-H2 | Nestor | repaired Z80 VM | 09-24 11:06 | 09-24 17:52 | REPLICATION_EVENTS_WITHOUT_PROPAGATION (WS) | NULL | Y | - | N | N | same |
| NES-C9-H3 | Nestor | repaired Z80 VM | 09-24 11:06 | 09-24 17:52 | NOT_DEMONSTRATED / CLEAN_NULL | NULL | Y | - | N | N | same |
| NES-X-NONPAIR-SEARCH | Nestor | FREE non-pair physics | 09-24 11:07 | 09-24 11:44 | WEAK_SIGNAL | NULL | - | - | N | N | roles/Nestor/campaigns/c9x-explore-2026-09-24/x_nonpair_search/ |
| NES-X-NONPAIR-FIDELITY | Nestor | replays | 09-24 11:44 | 09-24 12:01 | WEAK_SIGNAL | NULL | - | - | N | N | .../x_nonpair_fidelity/ |
| NES-X-SELFLOC-FREE | Nestor | FREE+BLOCK | 09-24 12:01 | 09-24 12:25 | CLEAN_NULL | NULL | - | - | N | N | .../x_selfloc_free/ |
| NES-X-SELFLOC-SEEDED | Nestor | implanted copier | 09-24 12:25 | 09-24 12:49 | SIGNAL 15/23 vs 0/23 | POSITIVE | Y | - | N | N | .../x_selfloc_seeded/ |
| NES-C-SELFLOC | Nestor | fresh cells | 09-24 12:49 | 09-24 13:20 | CONFIRMED 13/36 vs 0/36 | POSITIVE | Y | - | N | Y | .../c_selfloc_confirm/VERDICT.json |
| NES-X-ERROR-THRESHOLD | Nestor | seeded | 09-24 12:49 | 09-24 14:11 | CLEAN_NULL | NULL | - | - | N | Y | .../x_error_threshold/ |
| NES-X-ENERGY-INHERIT | Nestor | energy cells | 09-24 14:11 | 09-24 14:31 | SIGNAL 7/19 vs 1/19 | POSITIVE | - | - | N | Y | .../x_energy_inherit/ |
| NES-C-ENERGY | Nestor | 40 fresh cells | 09-24 14:31 | 09-24 15:12 | CONFIRMED 20/40 vs 4/40 | POSITIVE | Y | - | N | Y | .../c_energy_confirm/VERDICT.json |
| NES-X-LOCAL-ALLOC | Nestor | GRID/GRAPH | 09-24 15:13 | 09-24 15:17 | WEAK_SIGNAL (found C9-D15 artifact) | NULL | - | - | N | Y | .../x_local_alloc/ |
| NES-X-SPONTANEOUS | Nestor | permissive FREE | 09-24 15:17 | 09-24 15:39 | CLEAN_NULL | NULL | - | - | N | Y | .../x_spontaneous/ |
| NES-X-NEARMISS | Nestor | replays | 09-24 15:39 | 09-24 15:43 | WEAK_SIGNAL | NULL | - | - | N | Y | .../x_nearmiss/ |
| NES-X-DENSE-OPS | Nestor | 1-byte op VM | 09-24 15:43 | 09-24 16:24 | INVALID (VM leaked across workers) | INVALID | Y | POST | N | Y | .../x_dense_ops/ |
| NES-X-DENSE-OPS-R | Nestor | dense VM repaired | 09-24 16:24 | 09-24 17:06 | SIGNAL 23/47 vs 0/47 | POSITIVE | Y | - | N | Y | .../x_dense_ops/SUMMARY_R.json |
| NES-C-DENSE | Nestor | dense VM 40 fresh | 09-24 17:06 | 09-24 17:41 | CONFIRMED 13/40 vs 0/40 | POSITIVE | Y | - | N | Y | .../c_dense_confirm/VERDICT.json |
| NES-X-DENSE-ABLATE | Nestor | dense VM | 09-24 17:07 | 09-24 18:54 | SIGNAL | POSITIVE | - | - | N | Y | .../x_dense_ablate/ |
| NES-C-ABLATE | Nestor | 40 fresh | 09-24 18:54 | 09-24 19:46 | LOC+SEARCH CONFIRMED; ENERGY NOT | POSITIVE | Y | - | N | Y | .../c_ablate_confirm/VERDICT.json |
| NES-C9-H1R | Nestor | C9 H1 rewired | 09-24 17:53 | 09-24 18:02 | COST_INTERACTION_ONLY | POSITIVE | Y | PRE | N | N | .../c9_h1r/VERDICT.json |
| NES-X-H2-7AE3 | Nestor | specimen 7ae3 | 09-24 18:03 | 09-24 18:20 | WEAK_SIGNAL (C9-D17) | NULL | - | POST | N | N | .../x_h2_7ae3/ |
| NES-C9-H3-NULL | Nestor | H3 flow | 09-24 17:52 | 09-24 18:29 | CLEAN_NULL | NULL | - | - | N | N | .../x_h3_flow/ |
| NES-X-H2-TERMINATION | Nestor | 7ae3 | 09-24 18:20 | 09-24 18:44 | WEAK_SIGNAL | NULL | - | - | N | N | .../x_h2_termination/ |
| NES-X-H3-EASIER | Nestor | niche 0 | 09-24 18:29 | 09-24 18:35 | CLEAN_NULL; H3 RETIRED | NULL | Y | - | N | N | .../x_h3_easier/ |
| NES-X-H2-NORECOMB | Nestor | splice off | 09-24 18:44 | 09-24 19:10 | WEAK_SIGNAL | NULL | - | - | N | N | .../x_h2_norecomb/ |
| NES-C-NORECOMB | Nestor | 2 specimens x 24 | 09-24 19:10 | 09-24 20:03 | NOT_CONFIRMED 5/48 vs 5/48 | NULL | Y | - | N | N | .../c_norecomb_confirm/VERDICT.json |
| NES-X-PAIR-NORECOMB | Nestor | random pair tape | 09-24 19:47 | 09-24 20:08 | CLEAN_NULL -> INVALID 09-28 (no positive arm) | INVALID | N | POST | Y | N | .../x_pair_norecomb/ |
| NES-X-RUNAWAY | Nestor | 7ae3 splice off | 09-24 20:03 | 09-24 20:30 | SIGNAL (descriptive) | POSITIVE | - | - | N | N | .../x_runaway/ |
| NES-X-H1-TRANSPLANT | Nestor | 4 task transforms | 09-24 20:09 | 09-24 20:24 | SIGNAL 4/4 | POSITIVE | Y | - | N | Y | .../x_h1_transplant/ |
| NES-X-H1-GRADIENT | Nestor | probe | 09-24 20:25 | 09-24 20:28 | WEAK_SIGNAL | NULL | - | - | N | Y | .../x_h1_gradient/ |
| NES-C-RUNAWAY | Nestor | 7ae3 150/arm | 09-24 20:30 | 09-24 22:03 | CONFIRMED 7/150 vs 0/150 | POSITIVE | Y | - | N | Y | .../c_runaway_confirm/VERDICT.json |
| NES-X-RUNAWAY-TRANSPLANT | Nestor | other specimens | 09-24 22:03 | 09-24 22:45 | CLEAN_NULL (specimen-specific) | NULL | Y | - | N | Y | .../x_runaway_transplant/ |
| NES-X-POSITION | Nestor | P-11 | 09-24 22:45 | 09-24 22:50 | WITHDRAWN (assay sabotage) | INVALID | N | POST | N | Y | .../x_position/ |
| NES-X-STATE | Nestor | runaway | 09-24 22:46 | 09-24 22:50 | WEAK_SIGNAL | NULL | - | - | N | Y | .../x_state/ |
| NES-X-SUFFICIENCY | Nestor | runaway vs stall | 09-24 22:47 | 09-24 22:50 | CLEAN_NULL | NULL | - | - | N | Y | .../x_sufficiency/ |
| NES-X-CRITICAL-MASS | Nestor | 7ae3 k=1 vs 4 | 09-24 22:50 | 09-24 23:43 | WEAK_SIGNAL 9/64 | NULL | - | - | N | Y | .../x_critical_mass/ |
| NES-C-CRITICAL-MASS | Nestor | 80/arm | 09-24 23:43 | 09-25 00:53 | CONFIRMED 41/80 vs 5/80 (post-hoc superadditivity later killed) | POSITIVE | Y | - | N | Y | .../c_critical_mass/VERDICT.json |
| NES-X-DOSE-CURVE | Nestor | k in 1..8 | 09-25 00:53 | 09-25 03:02 | CLEAN_NULL (independent tickets) | KILLED | - | - | N | Y | .../x_dose_curve/ |
| NES-X-TICKET | Nestor | 7ae3 | 09-25 03:07 | 09-25 03:54 | WEAK_SIGNAL | NULL | - | - | N | Y | .../x_ticket/ |
| NES-X-DECAY | Nestor | dose f | 09-25 03:54 | 09-25 05:01 | WEAK_SIGNAL | NULL | - | - | N | Y | .../x_decay/ |
| NES-X-STALL | Nestor | replays | 09-25 05:01 | 09-25 05:18 | SIGNAL GENOME 177/192 | POSITIVE | Y | - | N | Y | .../x_stall/ |
| NES-X-STERILE | Nestor | g in 1,0 | 09-25 05:18 | 09-25 06:13 | CLEAN_NULL | NULL | - | - | N | Y | .../x_sterile/ |
| NES-X-STALL-F0 | Nestor | f=0 | 09-25 06:13 | 09-25 06:23 | SIGNAL write-back 25x | POSITIVE | Y | - | N | Y | .../x_stall_f0/ |
| NES-X-ATOMIC | Nestor | ATOMIC write-back | 09-25 06:23 | 09-25 08:03 | SIGNAL 36/64 vs 3/64 | POSITIVE | - | - | N | Y | .../x_atomic/ |
| NES-C-ATOMIC-C1 | Nestor | 7ae3 80/arm | 09-25 08:03 | 09-25 10:22 | CONFIRMED 46/80 vs 1/80 | POSITIVE | Y | - | N | Y | .../c_atomic/VERDICT.json |
| NES-C-ATOMIC-C2 | Nestor | 15 specimens | 09-25 08:03 | 09-25 11:02 | NOT_CONFIRMED | NULL | Y | - | N | Y | same |
| NES-X-DONOR-RATE | Nestor | assay | 09-25 11:02 | 09-25 11:03 | SIGNAL | POSITIVE | - | - | N | Y | .../x_donor_rate/ |
| NES-X-DONOR-SWAP | Nestor | 7ae3 in 11 cells | 09-25 11:03 | 09-25 12:48 | WEAK_SIGNAL 3/11 | NULL | Y | - | N | Y | .../x_donor_swap/ |
| NES-X-SWAP-ORIGIN | Nestor | replays | 09-25 12:50 | 09-25 13:18 | CLEAN_NULL (label later corrected) | NULL | Y | - | Y | Y | .../x_swap_origin/ |
| NES-X-ROOT-AUDIT | Nestor | C-ATOMIC rows | 09-25 13:18 | 09-25 15:03 | WEAK_SIGNAL 12/80 vs 0/80 | NULL | Y | - | N | Y | .../x_root_audit/ |
| NES-X-ATOMIC-RANDOM | Nestor | random implant | 09-25 15:03 | 09-25 15:46 | SIGNAL 0/80 vs 46/80 | POSITIVE | Y | - | N | Y | .../x_atomic_random/ |
| NES-X-SWAP-ANCESTRY | Nestor | replays | 09-25 15:46 | 09-25 16:08 | SIGNAL | POSITIVE | Y | - | N | Y | .../x_swap_ancestry/ |
| NES-C-SWAP-ACQUIRE | Nestor | 240/arm | 09-25 16:08 | 09-25 18:52 | NOT_CONFIRMED 9/240 vs 0 (bar 10; power ~0.45) | NULL | N | POST | N | Y | .../c_swap_acquire/VERDICT.json |
| NES-X-ACQUIRE | Nestor | assay | 09-25 16:08 | 09-25 18:56 | WEAK_SIGNAL | NULL | Y | - | N | Y | .../x_acquire/ |
| NES-X-CONTENT | Nestor | z8taint | 09-25 18:56 | 09-25 19:30 | WEAK_SIGNAL | NULL | Y | - | N | Y | .../x_content/ |
| NES-X-CORE | Nestor | z8taint | 09-25 19:30 | 09-25 19:53 | WEAK_SIGNAL | NULL | - | - | N | Y | .../x_core/ |
| NES-C-CORE | Nestor | 64 fresh | 09-25 19:53 | 09-25 21:04 | CONFIRMED 17/27 (scope limited by Aporia #621; SI framing withdrawn by operator) | POSITIVE | Y | - | Y | Y | .../c_core/VERDICT.json |
| NES-X-CORE-TIME | Nestor | trajectories | 09-25 21:04 | 09-25 21:31 | SIGNAL | POSITIVE | Y | - | Y | Y | .../x_core_time/ |
| NES-X-CERT-BREAK | Nestor | P-11 | 09-25 21:31 | 09-25 21:55 | WEAK_SIGNAL | NULL | - | - | N | Y | .../x_cert_break/ |
| NES-X-DONOR-DISCOVERY | Nestor | 7ae3/ffa6 ATOMIC | 09-26 13:37 | 09-26 14:19 | SIGNAL 1/96 | POSITIVE | Y | PRE | N | Y | roles/Nestor/campaigns/npe-w1-donor-discovery-2026-09-26/x_donor_discovery/ |
| NES-X-DD-DENSE-COPY | Nestor | DENSE_COPY VM | 09-26 14:19 | 09-26 15:51 | SIGNAL 0/96 -> 49/96 | POSITIVE | Y | - | N | Y | .../x_dd_dense_copy/ |
| NES-C-DENSE-COPY | Nestor | 64/arm | 09-26 15:51 | 09-26 16:48 | CONFIRMED 1/64 vs 39/64 | POSITIVE | Y | - | N | Y | .../c_dense_copy/VERDICT.json |
| NES-X-DD-ESTABLISH | Nestor | replays | 09-26 16:49 | 09-26 18:12 | SIGNAL NO_COPY 80% | POSITIVE | Y | - | N | Y | .../x_dd_establish/ |
| NES-X-DD-NOCOPY-CONTEXT | Nestor | probe | 09-26 18:12 | 09-26 18:25 | WEAK_SIGNAL (withdrawn) | NULL | - | - | N | Y | .../x_dd_nocopy_context/ |
| NES-X-DD-STATE-RESET | Nestor | reset on genome change | 09-26 18:25 | 09-26 20:13 | CLEAN_NULL | NULL | Y | - | N | Y | .../x_dd_state_reset/ |
| NES-X-DD-SELFSTATE | Nestor | probe | 09-26 20:13 | 09-26 20:14 | WEAK_SIGNAL; ruler later INVALID | INVALID | N | POST | Y | Y | .../x_dd_selfstate/ |
| NES-X-DD-STATELESS | Nestor | stateless exec | 09-26 20:14 | 09-26 22:01 | SIGNAL .38 -> .90 | POSITIVE | Y | - | N | Y | .../x_dd_stateless/ |
| NES-C-STATELESS | Nestor | 24/cell/arm | 09-26 22:01 | 09-26 23:19 | NOT_CONFIRMED | NULL | Y | - | N | Y | .../c_stateless/VERDICT.json |
| NES-C-STATELESS-FFA6 | Nestor | ffa6 48/arm | 09-26 23:19 | 09-27 00:44 | CONFIRMED 11/33 vs 34/42 (re-described later) | POSITIVE | Y | - | Y | Y | .../c_stateless_ffa6/VERDICT.json |
| NES-X-P2-BRIDGE | Nestor | 16 W1 donors | 09-27 21:01 | 09-27 21:41 | CLEAN_NULL (withdrew W1 ffa6 reading) | NULL | Y | - | N | Y | roles/Nestor/campaigns/npe-p2-endogenous-heredity-2026-09-27/x_p2_bridge/ |
| NES-X-P2-ENDOSTATE | Nestor | lineages | 09-27 21:17 | 09-27 21:18 | CLEAN_NULL -> ruler defect | INVALID | N | POST | Y | Y | .../x_p2_endostate/ |
| NES-X-P2-ATTRIB | Nestor | stock vs dense VM | 09-27 21:21 | 09-27 21:22 | SIGNAL 372/372 (negative control not exercised) | POSITIVE | N | POST | N | Y | .../x_p2_attrib/ |
| NES-X-P2-PLANT | Nestor | stock VM planted | 09-27 21:23 | 09-28 01:16 | SIGNAL 32/96 | POSITIVE | - | - | N | Y | .../x_p2_plant/ |
| NES-X-P2-REGSTATE | Nestor | reset variants | 09-27 21:23 | 09-27 22:14 | SIGNAL ZERO_SPECIFIC | POSITIVE | Y | - | N | Y | .../x_p2_regstate/ |
| NES-X-P2-LINEAGE | Nestor | replays | 09-27 21:23 | 09-27 22:59 | WEAK_SIGNAL 4/13 | NULL | Y | - | N | Y | .../x_p2_lineage/ |
| NES-X-P2-SHAM | Nestor | sham dense VM | 09-27 21:23 | 09-28 01:16 | CLEAN_NULL 0/96 (rival killed) | KILLED | Y | - | N | Y | .../x_p2_sham/ |
| NES-C-ZERO-SPECIFIC | Nestor | ffa6 fresh panel | 09-27 22:14 | 09-28 01:31 | CONFIRMED 26/48 vs 2/48 | POSITIVE | Y | - | N | Y | .../c_zero_specific/VERDICT.json |
| NES-X-P2-D0CHECK | Nestor | replays | 09-27 22:59 | 09-27 23:06 | CLEAN_NULL | NULL | Y | - | N | Y | .../x_p2_d0check/ |
| NES-X-A3-FAIR | Nestor | treatment-blind ruler | 09-28 05:20 | 09-28 09:19 | SIGNAL ZERO_LITERAL | POSITIVE | Y | - | N | Y | roles/Nestor/campaigns/npe-arc3-2026-09-28/x_a3_fair/ |
| NES-X-A3-AUTOPSY | Nestor | autopsy | 09-28 05:23 | 09-28 09:28 | SIGNAL | POSITIVE | - | - | N | Y | .../x_a3_autopsy/ |
| NES-X-A3-WITHDRAW | Nestor | scaffold withdrawal | 09-28 05:31 | 09-28 14:12 | CLEAN_NULL | NULL | Y | - | N | Y | .../x_a3_withdraw/ |
| NES-X-A3-FORENSIC | Nestor | delegate forensic | 09-28 | 09-28 06:26 | KILLED (knock-in 0/5, revert 0/8) | KILLED | Y | - | N | Y | .../delegates/forensic_16000006/ |
| NES-X-A3-ENDOSTATE-R | Nestor | cycle-aware ruler | 09-28 06:28 | 09-28 06:30 | WEAK_SIGNAL | NULL | Y | - | N | Y | .../x_a3_endostate_r/ |
| NES-X-A3-SFLINEAGE | Nestor | replays | 09-28 06:31 | 09-28 08:18 | SIGNAL 3/5 | POSITIVE | Y | - | N | Y | .../x_a3_sflineage/ |
| NES-C-A3-INTERNALIZE | Nestor | dense VM 144 fresh | 09-28 08:18 | 09-28 11:32 | CONFIRMED 8 events (bar 4) | POSITIVE | Y | - | N | Y | .../c_a3_internalize/VERDICT.json |
| NES-ANCESTRY-REPLAY | Nestor | T-003 + Z8 tracer | 09-28 23:17 | 09-29 05:26 | run1 INVALIDATED; v2.2 flip coverage FAIL -> INCONCLUSIVE | UNTESTABLE | Y | POST | N | N | roles/Nestor/campaigns/ancestry-replay-2026-09-28/ |
| NES-X-MAT-INTERNALIZE | Nestor | dense_taint | 09-30 08:41 | 09-30 10:02 | ENDOGENOUS 8/8 (no planted-transplant PC, Harmonia #1057) | POSITIVE | Y | POST | Y | Y | roles/Nestor/campaigns/npe-frontier-2026-09-30/x_mat_internalize/RESULT.md |
| NES-X-TASK-GATE | Nestor | ffa6 TASK_GATED | 09-30 18:04 | - | FROZEN, NOT executed | OPEN | Y | - | N | Y | .../x_task_gate/PREREG.md |
| NES-C3-HOLDOUT-D | Nestor | 128 hidden worlds | 09-25 19:00 | 09-28 | EXPOSED by merge; never used blind | PARKED | Y | - | Y | N | roles/Nestor/C3_HOLDOUT_D_REPORT.md |
| NES-C3-HOLDOUT-D2 | Nestor | AES-sealed 128 worlds | 09-28 09:34 | 09-29 14:34 (audit PASS) | SEALED/UNREAD/UNSPENT | PARKED | Y | PRE | N | N | roles/Nestor/WORK_STATE.json |
| COS-C0 | Cosmos | visible worlds + sealed D | 09-23 11:41 | 09-23 12:28 | no surviving invariant | NULL | Y | POST(run1 crash) | N | N | roles/Cosmos/campaigns/c0/RESULT_run2.md |
| COS-C0b | Cosmos | v3 coords, sealed D | 09-23 12:39 | 09-23 12:53 | SURVIVED .983 -> RESTRICTED 09-29 (no margin over zero-param rung) | KILLED | Y | POST | Y | Y | roles/Cosmos/research/RESULTS.md R-0001 |
| COS-C0e | Cosmos | sealed E | 09-23 12:57 | 09-23 12:58 | PASS .972 (later planted-invariant recovery) | POSITIVE | Y | - | Y | Y | roles/Cosmos/campaigns/c0e/ |
| COS-C0m | Cosmos | repetition code | 09-23 13:00 | 09-23 13:01 | M1/M2 PASS; M3 lost by .005 | POSITIVE | - | - | N | Y | roles/Cosmos/campaigns/c0m/ |
| COS-C0s | Cosmos | stress | 09-23 13:01 | 09-23 13:04 | S2 INVALID ladder defect -> S2b +0.045 9/9 | INVALID | Y | POST | N | Y | roles/Cosmos/campaigns/c0s/ |
| COS-C1 | Cosmos | v4 coords | 09-23 13:24 | 09-23 14:30 | no survivor (location gate) | NULL | - | POST(MemoryError) | N | Y | roles/Cosmos/campaigns/c1/ |
| COS-C2 | Cosmos | sealed F | 09-23 14:30 | 09-23 15:24 | F A .930, B .955, B>A n.s.; RESTRICTED 09-29 | KILLED | Y | POST | Y | Y | roles/Cosmos/campaigns/c2/F_adjudication.json |
| COS-ETA2 | Cosmos | cost-line vs random | 09-23 15:25 | 09-23 15:35 | NOT earned .767 vs .946 | KILLED | Y | - | N | Y | roles/Cosmos/campaigns/eta2/ |
| COS-C2X | Cosmos | attribution arms | 09-23 15:36 | 09-23 16:46 | attribution UNRESOLVED | NULL | Y | - | Y | Y | roles/Cosmos/campaigns/c2x/PREREG.md |
| COS-C3-S1-GATE-v2 | Cosmos | 6 planted systems | 09-24 ~07:10 | 09-24 07:13 | FAIL (instrument) | INVALID | Y | PRE | N | N | roles/Cosmos/c3/runs/GATE_v2_FAIL.json |
| COS-C3-S1-GATE-v3 | Cosmos | seeds 6-10 | 09-24 ~07:15 | 09-24 07:19 | PASS | POSITIVE | Y | - | N | N | roles/Cosmos/c3/runs/GATE_v3_PASS_seeds6to10.json |
| COS-C3-LAW | Cosmos | 120 visible worlds | 09-24 (withheld F-0000) | 09-29 12:21 | REJECT: zero-param rule 104/120; KILLED BEFORE HOLDOUT | KILLED | Y | PRE | Y | Y | roles/Cosmos/research/reviews/COORD_AUDIT_C3_2026-09-29.md |
| COS-T-I1 | Cosmos | graveyard atoms | 09-29 02:54 | 09-29 03:59 | v1/v2 defects; v3 11/15 | POSITIVE | Y | PRE | N | Y | roles/Cosmos/research/GRAVEYARD.md |
| COS-C4 | Cosmos | C4 design v0.2 | 09-30 13:47 | - | DESIGNED; R-STAT interim BLOCKING | OPEN | Y | PRE | N | Y | roles/Cosmos/c4/DESIGN_C4.md |
| ENS-E0 | Ensorain | e0 TT/ALS learners | 09-23 11:05 | 09-23 12:10 | INDETERMINATE (planted PC R^2 .007); frozen as useful negative | UNTESTABLE | Y | POST | Y | N | ensorain/E0_VERDICT.md |
| ENS-E1 | Ensorain | e1 TT vs baselines | 09-23 14:15 | 09-23 14:30 | INDETERMINATE; rank-1 LOWRANK beats TT | KILLED | Y | POST | N | N | ensorain/E1_VERDICT.md |
| ENS-E1.5 | Ensorain | e1p5 caps | 09-23 21:31 | 09-23 21:44 | CLOSE(B) -> operator INTRIGUING; PARKED | PARKED | Y | - | Y | N | ensorain/E1P5_VERDICT.md |
| ENS-E2 | Ensorain | e2 structure discovery | 09-23 21:57 | 09-23 22:09 | INDETERMINATE (control 2.7-SE chance) | NULL | Y | - | N | N | ensorain/E2_VERDICT.md |
| ENS-D1 | Ensorain | d1 random dials | 09-24 06:45 | 09-24 07:11 | 14 pairs nominated; T2/T3 not supported | NULL | Y | - | N | N | ensorain/D1_ROUND1.md |
| ENS-D2 | Ensorain | d1 confirm grids | 09-24 07:11 | 09-24 07:23 | INSTRUMENT CONTROLS FAIL | UNTESTABLE | Y | POST | N | N | ensorain/D2_ROUND2.md |
| ENS-D3 | Ensorain | d1 local | 09-24 07:23 | 09-24 07:39 | CONTROLS PASS; nominations | POSITIVE | Y | - | N | N | ensorain/D3_ROUND3.md |
| ENS-D4 | Ensorain | fresh seeds | 09-24 07:23 | 09-24 07:44 | M1 REPLICATED | POSITIVE | Y | - | N | Y | ensorain/DIALS_SYNTHESIS.md |
| ENS-WTP01 | Ensorain | wtp foundry | 09-24 08:18 | 09-24 08:43 | SEARCH SPACE MOSTLY DEGENERATE (metric artifact) | NULL | Y | POST | N | N | ensorain/ENSORAIN_WTP01_REPORT.md |
| ENS-WTP02 | Ensorain | wtp2 | 09-24 08:53 | 09-24 09:52 | EXPAND -> operator PARK/REDESIGN (one-float constant) | KILLED | Y | POST | Y | N | ensorain/WTP02_OPERATOR_RULING.md |
| ENS-WTP03 | Ensorain | wtp3 + N0-N5 | 09-24 22:12 | 09-25 09:07 | CANDIDATE PHYSICS -> seat KNOWN PHYSICS (N6 beats all) | KILLED | Y | POST | Y | Y | ensorain/ENSORAIN_WTP03_REPORT.md |
| ENS-LM01 | Ensorain | lm01 on WTP generators | 09-28 09:35 (v0.3.2) | - | FROZEN_NOT_LAUNCHED; HOLD | PARKED | Y | PRE | N | N | ensorain/PREREG_WTP_LM01.md |
| ENS-S1-PILOT | Ensorain | exact-oracle ladder | 09-28 06:32 | 09-28 06:36 | LOCUS IRRELEVANT; replicated 09-29 | POSITIVE | Y | - | N | N | ensorain/arc3/suff/RESULTS_S1_PILOT.md |
| ENS-PKGF-PROBE | Ensorain | LM01 SELECTIVE | none | 09-28 06:54 | harm vanishes under recency readout | POSITIVE | Y | - | N | N | ensorain/arc3/RESULTS_PKGF_PROBE.md |
| ENS-T25 | Ensorain | CSSR + Fabric | 09-29 04:00 | 09-29 11:35 | G1-G3 survive, G4 refuted | POSITIVE | Y | - | N | Y | branch ensorain: reviews/T25_CSSR_REVIEW_2026-09-29.md |
| ENS-CRYPT | Ensorain | learned crypticity | 09-29 12:55 | 09-29 14:03 | K1 refuted; one-sided bound | NULL | Y | - | N | Y | branch ensorain: arc3/suff/CRYPT_LEARNED.md |
| ENS-PKGF-CHAIN | Ensorain | PKG-F detectors | 09-29 14:36 | 09-30 03:48 | mixed; several refutations | NULL | Y | - | N | Y | branch ensorain commits 860a861fa..f7656908f |
| ENS-PKGF-OBS | Ensorain | pkgf_obs gate | 09-30 14:01 | 09-30 14:06 | OB1 survives; OB2 refuted | POSITIVE | Y | - | Y | Y | branch ensorain fe6393297 |
| ENS-LM02 | Ensorain | lm02 88 worlds | 09-30 14:33 | 09-30 14:51 | WINDOW_NOT_SUPPORTED; INSTRUMENT OK | NULL | Y | - | N | Y | branch ensorain: arc3/lm02/RESULTS_LM02_ASSAY.md |
| AET-AETH01-FL | Aether | aeth01.v1 4096^2 A40 | none | 09-23 00:26 | no endogenous organization (scout predicted null) | NULL | Y(ignored) | - | N | N | Aether/AETH-01/FIRST_LIGHT_01_2026-09-22.md |
| AET-AETH02 | Aether | aeth01.v1 2048^2 A40 | 09-23 21:45 | 09-24 12:40 | no (observer 250 ticks stale; 3rd traj truncated) | NULL | Y | POST | Y | N | Aether/AETH-01/NATIVE_CIRCUITRY_01_2026-09-24.md |
| AET-AETH03-PD01 | Aether | 128^2 CPU scouts | 09-26 06:53 | 09-26 07:52 | KILLED K-b x4; no scale-up | KILLED | Y | PRE | N | N | Aether/AETH-03/PHYSICS_DESIGN_01_2026-09-26.md |
| AET-AETH03-PD02 | Aether | mov/rcv/m4 | 09-26 14:20 | 09-26 16:47 | mov, m4 KILLED; rcv UNRESOLVED | KILLED | Y | PRE | N | N | Aether/AETH-03/PHYSICS_DESIGN_02_2026-09-26.md |
| AET-E003 | Aether | assay audit | 09-27 15:16 | 09-27 15:45 | exact after repair; one claim withdrawn | POSITIVE | Y | - | N | N | ops/campaigns/C-002/E-003/RESULT.md |
| AET-E005 | Aether | 8 units 10k ticks | 09-27 15:16 | 09-27 16:09 | horizon-robust | NULL | Y | - | N | N | ops/campaigns/C-002/E-005/RESULT.md |
| AET-E006 | Aether | 72 units A5000 pod | 09-27 15:16 | 09-27 18:03 | rcv_add, rcv_str NEW_BEHAVIOUR; fwd PC FAILED; falsifier 2 lost | POSITIVE | Y | POST | Y | N | ops/campaigns/C-002/E-006/RESULT.md |
| AET-E008 | Aether | 4 Fabric tasks | 09-27 15:16 | 09-29 04:08 | HORIZON-DEPENDENT clause iii only | POSITIVE | Y | - | N | Y | ops/campaigns/C-002/E-008/RESULT.md |
| AET-E009 | Aether | seeds 4-7 | 09-29 12:12 | 09-29 13:43 | REPLICATED both | POSITIVE | Y | - | N | Y | ops/campaigns/C-002/E-009/RESULT.md |
| AET-E010 | Aether | rcv_sfx lesion | 09-30 08:54 | 09-30 09:29 | STEERING_REQUIRED (Harmonia SUPPORTED) | POSITIVE | Y | - | N | Y | ops/campaigns/C-002/E-010/RESULT.md |
| AET-E011 | Aether | rcv_adr lesion | 09-30 09:35 | 09-30 10:21 | PARTIAL (lesion leaky) | NULL | Y | - | N | Y | ops/campaigns/C-002/E-011/RESULT.md |
| AET-E012 | Aether | rcv_sfz lesion | 09-30 10:25 | - | prereg only | OPEN | Y | - | N | Y | ops/campaigns/C-002/E-012/EXPERIMENT.md |
| HEC-PROBE-R1 | Hecate | opus-5-5 implementers, 16 worlds | 09-30 02:10 | 09-30 02:35 | 3 SIGNAL, 6 NULL, 1 CONF, 3 INSTR_FAIL, 3 NOT_BUILT | POSITIVE | Y | POST | N | N | hecate/programs/PROBE_ROUND1_REPORT.json |
| HEC-PASS4-R1 | Hecate | attacker | 09-30 02:36 | 09-30 02:41 | 2 PARK, 1 known mechanism | KILLED | Y | - | N | Y | hecate/programs/PASS4_ROUND1_REPORT.json |
| HEC-PROBE-R2 | Hecate | 13 worlds | 09-30 02:37 | 09-30 02:48 | 0 SIGNAL; 6 SPEC_UNATTAINABLE | UNTESTABLE | Y | PRE | N | N | hecate/programs/PROBE_ROUND2_REPORT.json |
| HEC-PROBE-R3 | Hecate | generator v2, 8 worlds | 09-30 03:13 | 09-30 03:18 | 2 SIGNAL, 6 NULL, 0 instrument fail | POSITIVE | Y | - | N | N | hecate/programs/PROBE_ROUND3_REPORT.json |
| HEC-PASS4-R2 | Hecate | attacker | 09-30 03:19 | 09-30 03:26 | both PARK (Harmonia: ORIG kill met but not reported) | KILLED | Y | POST | Y | Y | hecate/programs/PASS4_ROUND2_REPORT.json |
| HEC-META-V1 | Hecate | sonnet-5 gen / opus-5-5 detector | 09-30 02:44 | 09-30 03:08 | M1 INDETERMINATE; zero UNFAMILIAR (uncalibrated) | INVALID | N | POST | Y | N | hecate/meta/REPORT_v1.md |
| HEC-ALIEN-A | Hecate | opus-5-5, 100 systems | 09-30 05:40 | 09-30 07:51 | INDETERMINATE / NOT_SUPPORTED; detector NOT_VALIDATED | NULL | Y | POST | Y | N | hecate/alien/REPORT_pilot.md |
| HEC-ALIEN-BC | Hecate | gpt-oss-120b, gemini-3.6-flash | 09-30 05:40 | 09-30 08:28 | incomplete (quota, truncation) | UNTESTABLE | N | POST | N | N | hecate/alien/DEVIATION_01.md |
| HEC-AUTOPSY | Hecate | meta v1 detector | 09-30 08:21 | 09-30 08:25 | DETECTOR_CANNOT_REACH_UNFAMILIAR | POSITIVE | - | - | N | N | hecate/autopsy/AUTOPSY.md |
| TYC-V0-ATT1 | Tyche | lens evolution | 09-30 06:30 | 09-30 07:05 | stopped: BLAS oversubscription | INVALID | Y | POST | N | N | tyche/runs/v0_2026-09-30_ABORTED |
| TYC-V0 | Tyche | lens evolution, 32 worlds | 09-30 06:30 | 09-30 09:18 | H2,H5 PASS; H3,H4 FAIL; H1,H6 INDET -> UNREACHABLE_BY_DESIGN | UNTESTABLE | Y | POST | Y | Y | tyche/runs/v0_2026-09-30/REPORT.md |
| TYC-V1 | Tyche | V0/DE/DENR arms | 09-30 10:17 | 09-30 10:53 | GATE 6 FAIL | NULL | Y | PRE | N | N | tyche/runs/v1_2026-09-30/REPORT_v1.md |
| TYC-V2-BLOCKR | Tyche | STRICT/LEX/RES | 09-30 13:11 | 09-30 14:50 | RH1-RH4 FALSE; OV censored | NULL | Y | POST(memory) | N | N | tyche/runs/v2_blockR/REPORT_BLOCK_R.md |
| THE-V0 | Theseus | synth concepts | 09-30 13:09 | 09-30 14:00 | H1 FAIL (lens leak, hash nondeterminism) | INVALID | N | POST | N | N | theseus/runs/v0_2026-09-30/REPORT.json |
| THE-V0_1 | Theseus | same, fixed | 09-30 14:01 | 09-30 14:42 | H1 INDETERMINATE (n=51 underpowered) | UNTESTABLE | N | POST | N | N | roles/Theseus/REVIEW_PACKET_v0_2026-09-30.txt |
| ARC-STAGE0 | Archaeon | SFE fossils | ? | 09-06 02:34 | KILL under tenancy; 0 eligible units | KILLED | Y | PRE | N | N | archaeon/docs/STAGE0_RESULT.md |
| ARC-C3-1 | Archaeon | SFE ca_density | ? | 09-10 11:58 | producer error, 126 rows cancelled | INVALID | N | POST | N | N | roles/Archaeon/H0H5_STATUS.md |
| ARC-C3-2 | Archaeon | SFE 150 rows | 09-10 | 09-10 17:56 | H2 STRUCTURALLY_VOID | UNTESTABLE | Y | POST | Y | N | archaeon/docs/h0h5/C3_2_READOUT.md |
| ARC-H1H0-P2 | Archaeon | SFE cegis | 09-10 | 09-10 23:16 | FAIR and INERT; fresh==S00 by construction | UNTESTABLE | Y | POST | Y | N | archaeon/docs/h0h5/H1H0_PHASE2_READOUT.md |
| ARC-C3-3 | Archaeon | SFE cellwise | 09-11 00:25 | - | never issued | PARKED | Y | PRE | N | N | archaeon/docs/h0h5/C3_3_DESIGN.md |
| ARC-H5-1 | Archaeon | SFE eca rules | 09-10 23:31 | 09-11 22:10 | analytic bounds; calibration only | POSITIVE | Y | - | Y | N | archaeon/docs/h0h5/H5_1_READOUT_2026-09-11.md |
| ARC-H3-DEADSTREAM | Archaeon | h3_replay | 09-11 | 09-11 20:10 | task-level reuse separates | POSITIVE | Y | - | N | N | archaeon/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md |
| ARC-S1-FOSSIL | Archaeon | SFE | 09-12 16:55 | 09-12 16:59 | NO_DETECTABLE_ADVANTAGE | NULL | Y | - | N | N | git 8fc994e1f |
| ARC-S3-INFO | Archaeon | synthetic 120 worlds | 09-12 19:27 | 09-12 19:40 | NO_ADVANTAGE (saturated endpoint) | UNTESTABLE | N | POST | N | N | git log |
| ARC-S4-PRODUCERS | Archaeon | synthetic 240 worlds | 09-12 20:26 | 09-12 22:49 | NO_SEPARATION | NULL | ? | - | N | N | git log |
| ARC-S5 | Archaeon | exact DP producer | 09-13 04:34 | 09-13 06:01 | INSTRUMENT_FAILURE both runs | INVALID | N | POST | N | N | roles/Archaeon/CALIBRATION_LEDGER.md |
| ARC-S7 | Archaeon | same | 09-13 13:47 | 09-13 22:30 | GATE_FAILS_TO_ISOLATE | NULL | Y | POST | N | N | roles/Archaeon/CALIBRATION_LEDGER.md |
| ARC-WSE-V01 | Archaeon | WSE over Proteus VM | 09-16 19:10 | 09-16 19:53 | three failure shapes | NULL | Y | - | N | N | archaeon/wse/READOUT_v01.md |
| ARC-SSF | Archaeon | WSE stream world | 09-16 20:16 | 09-16 22:47 | no selective state | NULL | Y | - | N | N | archaeon/wse/READOUT_ssf.md |
| ARC-CMP1-POS | Archaeon | SFE v2 + WSE | 09-17 | 09-17 01:03 | WEAK POSITIVE (SFE-01, -07 later killed) | POSITIVE | Y | - | N | N | archaeon/campaign1/CAMPAIGN_REPORT.md |
| ARC-CMP1-NEG | Archaeon | same | 09-17 | 09-17 01:03 | NEGATIVE, assay capable | NULL | Y | - | N | N | same |
| ARC-CMP1-INC | Archaeon | same | 09-17 | 09-17 01:03 | INCONCLUSIVE (assay incapable) | UNTESTABLE | N | POST | N | N | same |
| ARC-CMP2 | Archaeon | SFE v2 CRN | 09-17 02:56 | 09-17 04:21 | 7 CAPABLE_NEGATIVE / 3 WEAK_POSITIVE | KILLED | Y | PRE | N | Y | archaeon/campaign2/CAMPAIGN_REPORT.md |
| ARC-CMP3 | Archaeon | WSE | 09-17 05:23 | 09-17 07:54 | 7 NEG, 2 WEAK_POS, 1 INCONCL | NULL | Y | PRE | N | N | archaeon/campaign3/CAMPAIGN_REPORT.md |
| ARC-CMP4 | Archaeon | engine 9.0.1 | 09-18 | 09-18 06:46 | NO_CONDITION_SELECTED | NULL | Y | PRE | N | N | archaeon/campaign4/CAMPAIGN_REPORT.md |
| ARC-CMP5 | Archaeon | representation B | 09-18 14:16 | 09-18 15:08 | BOUNDARY_CREATED_NO_DISCOVERY_GAIN | NULL | Y | PRE | Y | N | archaeon/campaign5/CAMPAIGN_REPORT.md |
| ARC-CMP6 | Archaeon | graph organisms | 09-18 20:08 | - | no science rows | PARKED | Y | - | N | N | archaeon/campaign6/DECISIONS.md |
| ARC-MOAT-CENSUS | Archaeon | Z80 atlas vmcopy32 | 09-24 00:54 | 09-24 02:03 | 828 QUALIFIED; LOTTERY_CONSISTENT | POSITIVE | Y | - | N | N | roles/Archaeon/journal/2026-09-23_m2-db608f52.md |
| ARC-ENVGATE-01 | Archaeon | vmcopy32 | 09-24 06:39 | 09-24 16:05 | CAUSALLY -> PARTIALLY SUPPORTED (operator R1) | POSITIVE | Y | POST | Y | N | archaeon/envgate/ADJUDICATION_ADDENDUM_2026-09-24.md |
| ARC-ENVGATE-02 | Archaeon | vmcopy32 | 09-24 | 09-26 07:48 | WINDOW_NOT_SUPPORTED | NULL | Y | POST(KeyError) | N | Y | archaeon/envgate2/VERDICT_2026-09-26.md |
| ARC-PORTABILITY-01 | Archaeon | taint VM, BEE, NPE, PTE | 09-26 13:03 | 09-27 00:25 | PORTABLE_WITH_DOMAIN_LIMITS | POSITIVE | Y | - | N | N | archaeon/causal_lens/PORTABILITY01_REPORT.md |
| ARC-E001 | Archaeon | BEE, NPE, Archaeon | 09-27 11:26 | 09-27 13:58 | yes in all three engines | POSITIVE | Y | - | N | Y | ops/campaigns/C-001/E-001/RESULT.md |
| ARC-E002 | Archaeon (Artemis exec) | PTE | 09-27 | 09-27 18:30 | RULE INADEQUATE stands | NULL | Y | - | N | N | ops/campaigns/C-001/E-002/RESULT.md |
| ARC-DEEPBLOCK | Archaeon | taint VM block 13 | 09-27 17:43 | 09-27 18:52 | 0.0 founder material RETRACTED | INVALID | N | POST | Y | N | ops/threads/TH-013.md |
| ARC-ATTRIB-V0 | Archaeon | BEE, NPE, Archaeon | 09-28 10:04 | 09-28 10:27 | v1 withdrawn; identifiable 1 of 3 | INVALID | N | POST | N | Y | ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28/ASSAY.md |
| ARC-TH013 | Archaeon | block 13 to epoch 20k | 09-28 09:51 | 09-28 11:27 | machinery relocates; exactness claim withdrawn | POSITIVE | N | - | N | Y | .../TH013_RESULT.md |
| ARC-TH015 | Archaeon | 24 member tapes | 09-28 10:12 | 09-28 11:29 | EXECUTED_ONLY .891; MACHINERY .028 | POSITIVE | Y | - | N | Y | .../TH015_RESULT.md |
| ARC-ITEM8 | Archaeon | block 13 | 09-28 11:24 | 09-28 | 72% dead on arrival; prior 377/400 VOID | NULL | N | - | N | Y | .../ITEM8_RESULT.md |
| BEL-EXP001 | Bellerophon | BEE toolbox | 09-19 02:55 | 09-19 | rows wrong, caught before report | INVALID | Y | PRE | N | N | roles/Bellerophon/calibration/LEDGER.md |
| BEL-ATLAS-BEE | Bellerophon | BEE | 09-19 12:42 | 09-19 13:42 | a1 INVERTED, a2/a3 CHANGED, a4/a5 ABSENT, a6 PRESERVED | POSITIVE | Y | - | N | Y | roles/Bellerophon/atlas_bee/REVIEW_PACKET_2026-09-19.md |
| BEL-GROUNDING | Bellerophon | Z80_64 copier worlds | 09-23 12:55 | 09-23 17:02 | mixed; G6a 160/160 -> 103/160 (errata 09-29) | POSITIVE | Y | POST | Y | N | roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md |
| BEL-COUPLING | Bellerophon | BEE physics v3 | 09-24 20:07 | 09-25 19:42 | READY_FOR_MULTIDAY; P5 FAILS ceiling | POSITIVE | Y | - | N | N | roles/Bellerophon/coupling_2026-09-24/COUPLING_CAMPAIGN_REPORT.md |
| BEL-MD | Bellerophon | BEE physics v3 20k ticks | 09-26 16:40 | 09-29 05:06 | LADDER_CLIMBED, PROTECTION_EVOLVED; LADDER2 FAILS; Q3 FAILS | POSITIVE | Y | - | N | Y | roles/Bellerophon/multiday_2026-09-26/MULTIDAY_CAMPAIGN_REPORT.md |
| BEL-E003-BEE | Bellerophon (Archaeon owner) | BEE r022153 | 09-29 07:30 | 09-29 09:38 | VALIDATED -> ALTERED; verdict of record OPEN | OPEN | Y | POST | Y | N | roles/Bellerophon/e003_2026-09-29/ERRATA_2026-09-30.md |
| BEL-REPL-01 | Bellerophon | BEE register world | 09-30 11:20 | 09-30 12:32 | DISAPPEARS (K3); descent UNRESOLVED | KILLED | Y | POST | Y | Y | roles/Bellerophon/repl_2026-09-30/RESULT.md |
| BEL-REPL-02 | Bellerophon | BEE register world | 09-30 13:08 | 09-30 15:03 | RESIDUE_NOT_REPLICATED; M6 PC 0/50 | UNTESTABLE | Y | POST | N | Y | roles/Bellerophon/repl_2026-09-30/RESULT_02.md |
| ANA-PTE-C1 | Ananke | PTE | 09-24 12:01 | 09-25 00:10 | COMM_DEPENDENT, REPRODUCED (errata later) | POSITIVE | N | POST | Y | N | roles/Ananke/pte/C1_REPORT.md |
| ANA-PTE-C1B | Ananke | PTE | 09-26 00:25 | 09-26 13:41 | M3 = transport on readout tick; C1 null vacuous | POSITIVE | Y | PRE | N | Y | roles/Ananke/pte/c1b/REVIEW_PACKET_PTE_C1b.txt |
| ANA-PTE-SI01 | Ananke | PTE | 09-25 20:06 | 09-28 06:52 | CLOSED for current champions | NULL | Y | PRE | N | Y | roles/Ananke/research/SYNTHESIS_2026-09-28_ARC3.md |
| ANA-W-A | Ananke | PTE M2 | 09-27 22:32 | 09-28 00:40 | same three-line law | POSITIVE | Y | - | N | Y | roles/Ananke/research/workers/W-A/REPORT.md |
| ANA-W-B | Ananke | PTE | 09-28 | 09-28 00:40 | bootstrap account holds, narrower | POSITIVE | ? | - | N | Y | .../W-B/REPORT.md |
| ANA-W-C | Ananke | PTE vs Aether | 09-28 | 09-28 00:40 | CONTRAST DOES NOT HOLD (design confound) | INVALID | N | POST | N | N | .../W-C/REPORT.md |
| ANA-W-D | Ananke | records | 09-28 | 09-27 22:38 | case table (audit) | POSITIVE | - | - | N | N | .../W-D/REPORT.md |
| ANA-W-E | Ananke | PTE | 09-28 | 09-28 00:40 | NO, power limit predicted by C-POS | UNTESTABLE | Y | PRE | N | N | .../W-E/REPORT.md |
| ANA-W-F | Ananke | PTE 166 cells | 09-28 | 09-28 00:40 | census table | POSITIVE | Y | - | N | N | .../W-F/REPORT.md |
| ANA-W-G | Ananke | PTE | 09-28 | 09-28 06:52 | NO (replicated; controls valid) | NULL | Y | - | N | Y | .../W-G/REPORT.md |
| ANA-W-H | Ananke | PTE | 09-28 | 09-28 06:16 | COMPRESSES not EXPANDS | NULL | Y | - | N | Y | .../W-H/REPORT.md |
| ANA-W-I | Ananke | PTE 33 cells | 09-28 | 09-28 | carriers are trajectories | POSITIVE | Y | - | N | Y | .../W-I/REPORT.md |
| ANA-W-J | Ananke | PTE | 09-28 | 09-28 | conditionally, gain ~0.02 | POSITIVE | Y | - | N | N | .../W-J/REPORT.md |
| ANA-W-K | Ananke | PTE fixtures | 09-28 | 09-28 05:48 | no universal check; K2 J .70 | POSITIVE | Y | - | N | Y | .../W-K/REPORT.md |
| ANA-W-L | Ananke | PTE M2 | 09-28 | 09-28 07:43 | reachable as INTEGRATION; lag-2 unreached | POSITIVE | Y | - | N | Y | .../W-L/REPORT.md |
| ANA-W-M | Ananke | PTE | 09-29 | 09-29 04:51 | single-trial swap census replaces sum test | POSITIVE | Y | - | N | Y | .../W-M/REPORT.md |
| ANA-W-N | Ananke | PTE | 09-29 | 09-29 06:47 | sample-size effect | POSITIVE | Y | - | N | Y | .../W-N/REPORT.md |
| ANA-W-O | Ananke | PTE 733 verdicts | 09-29 | 09-29 09:17 | 84% stay CHANCE; frozen proportions missed | NULL | ? | - | N | Y | .../W-O/REPORT.md |
| ANA-W-P | Ananke | PTE | 09-29 | 09-29 10:52 | no support; joint carrier instead | NULL | Y | - | N | Y | .../W-P/REPORT.md |
| ANA-W-Q | Ananke | stats | 09-29 | 09-29 11:46 | certifies 42 transfers; not promoted | POSITIVE | Y | - | N | Y | .../W-Q/REPORT.md |
| ANA-W-R | Ananke | PTE sync | 09-29 | 09-29 12:58 | indexed by update-clock phase | POSITIVE | Y | - | N | Y | .../W-R/REPORT.md |
| ANA-W-S | Ananke | PTE | 09-29 | 09-29 13:43 | H1 NOT SUPPORTED | NULL | Y | - | N | Y | .../W-S/REPORT.md |
| ANA-W-T | Ananke | PTE | 09-29 | 09-29 14:27 | exact but reaches no new cell | NULL | Y | - | N | Y | .../W-T/REPORT.md |
| ANA-W-U | Ananke | stats | 09-29 | 09-29 16:20 | bootstrap holds to 32 pairs | POSITIVE | Y | - | N | Y | .../W-U/REPORT.md |
| ANA-W-V | Ananke | PTE MAJ | 09-30 | 09-30 07:15 | DISTRIBUTED-NONMAJ | NULL | Y | - | N | N | .../W-V/REPORT.md |
| ANA-W-W | Ananke | stats | 09-30 09:19 | 09-30 10:34 | promotable; held for check | POSITIVE | Y | - | N | Y | .../W-W/REPORT.md |
| ANA-W-X | Ananke | stats | 09-30 | 09-30 10:48 | passes frozen rule; promoted | POSITIVE | Y | - | N | Y | .../W-X/REPORT.md |
| ANA-W-Y | Ananke | PTE | 09-30 11:09 | 09-30 11:28 | known-answer Plant A failed | UNTESTABLE | Y | PRE | N | N | .../W-Y/REPORT.md |
| ANA-W-Z | Ananke | PTE 124 groups | 09-30 11:49 | 09-30 12:51 | 92.7% < 95% bar | NULL | Y | - | N | Y | .../W-Z/REPORT.md |
| ANA-H-PLANT | Ananke | PTE plants | 09-30 23:46 | - | running | OPEN | Y | - | N | N | roles/Ananke/research/plans/H-PLANT_PLAN.md |
| ART-P11-FALSIF | Artemis | NPE z8 + toy ISA | 09-28 09:08 | 09-28 09:21 | P-11 certifies construction, not heredity (UNSOUND) | KILLED | Y | - | N | N | roles/Artemis/challenge/p11/RESULT.md |
| ART-SI-MODEL | Artemis | register-machine sim | 09-28 09:06 | 09-28 10:01 | broad N, narrow U | POSITIVE | Y | - | N | N | roles/Artemis/challenge/si/RESULT.md |
| ART-FR101 | Artemis | Archaeon C3-SFE-09 code | 09-28 09:04 | 09-28 09:11 | shift rules each score 1.000 | KILLED | N | POST | N | N | roles/Artemis/challenge/experiments/FR-101/RESULT.md |
| ART-SELFTEST | Artemis | fresh Claude workers | 09-28 13:37 | 09-29 | not shown | NULL | Y | - | N | N | roles/Artemis/selftest/RESULT.md |
| ART-CVTR-NESTOR | Artemis | NPE genomes | 09-28 19:38 | 09-28 19:40 | (c) 8/8 accepted; 19 P-11-certified fail | POSITIVE | Y | - | N | N | roles/Artemis/challenge/cvtr_nestor/RESULT.md |
| ODY-ART-S3 | Odysseus+Artemis | Fabric v0.2 | 09-29 12:29 | 09-29 13:58 | gate MET; 0.33 -> 0.67 recoded; ceiling ruler (Harmonia MAJOR) | POSITIVE | Y | POST | Y | N | roles/Odysseus/fabric_pilot/s3/RESULT.md |
| ODY-S2 | Odysseus | Fabric 18 verifiers | 09-28 21:07 | 09-28 21:14 | MET 0.28/exec | POSITIVE | Y | - | N | N | roles/Odysseus/fabric_pilot/s2/RESULT.md |
| ODY-EXPEDITION1 | Odysseus | BEE, Z80, NI | 09-28 17:14 | 09-28 | NI RETIRED; WSE reader FAILED | NULL | - | - | N | N | roles/Odysseus/expedition/EXPEDITION_1_REPORT.md |
| NYX-GZIP-001-002 | Nyx | gzip 1.2.4 fossil | 09-16 17:23 | 09-16 18:33 | Harmonia CHALLENGE: line 672 not 667 | INVALID | Y | PRE | N | N | nyx/atlas/predictions/ |
| NYX-GZIP-003 | Nyx | gzip | 09-16 18:33 | - | never run | PARKED | - | - | N | N | roles/Harmonia/journal/2026-09-17_m2-038758c6.md |
| NYX-PARTICLES-001 | Nyx | particle filter fossil | 09-17 15:22 | 09-17 15:33 | INDETERMINATE (PC out of band) | UNTESTABLE | Y | PRE | N | N | roles/Harmonia/rulings/RULING_PARTICLES_ESSTRIGGER_001_2026-09-17.md |
| NYX-PARTICLES-002 | Nyx | particle filter, 2 worlds | 09-17 15:48 | 09-17 22:29 | CUT_SUPPORTED boundary; (c) FAILED | POSITIVE | Y | - | N | Y | roles/Harmonia/rulings/RULING_PARTICLES_ESSTRIGGER_002_2026-09-17.md |
| NYX-ASAL-001 | Nyx | ASAL Lenia + CLIP | 09-18 06:13 | 09-18 06:28 | CUT_SUPPORTED; narrowed by operator | POSITIVE | Y | - | Y | N | roles/Harmonia/rulings/RULING_ASAL_LEGIT_SEARCH_001_2026-09-18.md |
| NYX-POET-001 | Nyx | POET fossil | 09-19 ~10:09 | 09-30 10:43 | CUT_SUPPORTED, NOT confirmatory | POSITIVE | Y | - | Y | N | roles/Harmonia/rulings/RULING_MECH_POET_NOVELTY_ESTIMATOR_001_2026-09-30.md |
| NYX-AVIDA-001 | Nyx | Avida ancestry | 09-30 11:13 | - | awaiting adjudication | OPEN | Y | - | N | N | nyx/atlas/predictions/MECH-AVIDA-ANCESTRY-RETENTION-001.json |

## 9. Full CSV (also saved as findings_A3_ledger.csv)

```csv
id,seat,substrate,hypothesis,freeze_utc,launch_utc,verdict_utc,verdict_recorded,class,screen_pre,failure_found,relabel,builds_on_pos,compute,evidence
APH-RSI-TOYS,Aphrodite,python toys,RSI toy mechanisms E1-E4,09-18 01:01,09-18 01:06,09-18 01:30,9 SUPPORTED/3 REFUTED/3 INDETERMINATE,POSITIVE,Y,-,N,N,minutes,git 07fcc2509
APH-SWARM,Aphrodite,python toys,swarm damage boundaries S1-S4,09-18 04:47,09-18 04:50,09-18 04:57,results; toys stopped after external review,PARKED,Y,-,N,N,minutes,"git acc40e902, 7bb8ff982"
APH-C0,Aphrodite,C0 generative worlds,RSI assay qualifies (tier 2),09-18 05:38,09-18 05:41,09-18 05:47,PASS (operator ACCEPTED),POSITIVE,Y,-,N,N,minutes,roles/Aphrodite/science/campaign0/RESULTS_C0_2026-09-18.md
APH-C0B,Aphrodite,C0 pathology generator,assay survives stress pathologies,09-18 12:12,09-18 12:14,09-18 12:17,"FAIL on power, calibration intact",NULL,Y,-,N,Y,minutes,roles/Aphrodite/science/campaign0/RESULTS_C0B_2026-09-18.md
APH-C0C,Aphrodite,C0 quadrature-truth generator,secondary endpoint qualifies,09-18 16:26,09-18 16:28,09-18 16:30,PASS,POSITIVE,Y,-,N,Y,minutes,roles/Aphrodite/science/campaign0c/RESULTS_C0C_2026-09-18.md
APH-C1,Aphrodite,Campaign 1 (no eligible substrate),mechanism transplantation raises D_VAULT,09-19 09:50,-,-,FROZEN and UNRUN (blocked on other seats' contracts),PARKED,Y,-,N,Y,0,roles/Aphrodite/science/campaign1/PREREG_C1_TRANSPLANT_2026-09-19.md
APH-ENGINE-V1,Aphrodite,local engine v1,endogenous discovery transfers to fresh recipient,09-21 12:21,=frz,09-21 12:27,discovery WORKS; coprime shortcut; clone lineages,POSITIVE,Y,POST,N,N,71 s,roles/Aphrodite/engine/README.md
APH-A3-2B,Aphrodite,local engine,slice 2B discovery yield,09-21 13:01,=frz,09-21 13:09,"yield 0/16, validity scar",INVALID,N,POST,N,Y,minutes,"git 8a1fee278, 92f013c85"
APH-A4-2C-GATE,Aphrodite,local engine,load-bearing structure reachable in grammar,09-21 ~16:00,-,09-21 16:28,STOPPED at reachability gate,KILLED,Y,PRE,N,Y,seconds,git aeaadcfaf
APH-A5A6-2C,Aphrodite,local engine (ext. grammar),variable-length accumulation discovered,09-21 18:23,=frz,09-22 01:32,"load-bearing mechanism discovered, extrapolates",POSITIVE,Y,-,N,Y,hours,git 48e17a7d1
APH-A7-S3LICE,Aphrodite,local engine,extracted organ guides search,09-22 05:05,09-22 05:07,09-22 05:12,DIRECT_COMPETENCE_REUSE = NO (scratch control vacuous),NULL,Y,POST,N,Y,minutes,git 173c08649
APH-A8-SLICE4,Aphrodite,local engine,search leverage at equal expressivity,09-22 07:42,=frz,09-22 08:08,STRUCTURAL_SEARCH_LEVERAGE = YES,POSITIVE,Y,-,N,Y,minutes,git 74f857091
APH-A9-T3A,Aphrodite,local engine,bounded RSI (meta-dev transplant),09-22 08:30,09-22 08:34,09-22 08:38,BRSI NO; sham contained answer; INCONCLUSIVE_CONTROL_INVALID,INVALID,Y,POST,N,Y,minutes,git ba88978c0
APH-A10-T3B,Aphrodite,local engine,bounded RSI w/ semantic identity + shams,09-22 08:45,09-22 08:58,09-22 17:21,BRSI NO; search leverage YES_LOCAL 47x,NULL,Y,-,N,Y,hours,git 4d87b0bd4
APH-A11-T3C,Aphrodite,local engine,donor forms abstraction,09-22 23:16,=frz,09-23 00:02,"BRSI NO; donor none, two SHAMS did",KILLED,Y,-,N,Y,minutes,git 4469736ca
APH-A12-S1,Aphrodite,local engine,whole-program behaviour identity,09-23 20:29,09-23 ~20:45,09-24 14:20,runs 1-3 FAIL; GLOBAL FAIL; campaign-local PASS,NULL,Y,POST,N,N,hours,roles/Aphrodite/engine/AMENDMENT_12_ADDENDUM_3_2026-09-24.md
APH-A13-S2,Aphrodite,local engine,fair meta-selection,09-23 21:16,09-24 14:22,09-24 14:49,S2_PASS,POSITIVE,Y,-,N,Y,minutes,git 52dad4db7
APH-A14-S3,Aphrodite,local engine,endogenous abstraction derived + selected,09-23 21:16,09-24 14:22,09-24 14:49,ENDOGENOUS_ABSTRACTION = YES,POSITIVE,Y,-,N,Y,minutes,git 52dad4db7
APH-A14-S4,Aphrodite,local engine,abstraction transplants to unseen bodies,09-23 21:16,09-24 14:49,09-24 15:11,YES all 8 conditions; operator: BRSI not yet established,POSITIVE,Y,-,Y,Y,<1 h,roles/Aphrodite/engine/S4_RESULTS_2026-09-23.json
APH-A15-G2,Aphrodite,local engine,G1->G2 bounded recursion,09-24 16:19,09-24 16:21,09-24 16:39,STOP at catalog 2/7<3; UNTESTABLE catalog,UNTESTABLE,N,POST,N,Y,minutes,git a9a64c7d9
APH-A16,Aphrodite,local engine,4-h recursion campaign,09-24 18:36,09-24 18:42,09-24 19:51,foundry 6%; E1/E2 untestable; E4 INCONCLUSIVE,UNTESTABLE,N,POST,N,Y,"<4 h, $0",git bb47c233c
APH-A17-E1,Aphrodite,local engine,bounded RSI E1,09-26 13:33,09-26 13:36,09-26 14:09,E1 BRSI NO (valid novelty failure),NULL,Y,-,N,Y,48 min (A17 total),pivot/APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-26.md
APH-A17-E2E3,Aphrodite,local engine,E2 replication / G4 ceiling,09-26 13:33,09-26 13:36,09-26 14:09,E2 UNTESTABLE (catalog); E3 UNTESTABLE,UNTESTABLE,N,POST,N,Y,in 48 min,same
APH-A17-E4,Aphrodite,local engine,S1 necessity,09-26 13:33,09-26 13:36,09-26 13:39,S1_NECESSITY SUPPORTED 3/3 vs 0/3,POSITIVE,Y,-,N,Y,in 48 min,git fb5628435
APH-A18-C1,Aphrodite,local engine W5 + T4,abstraction compounding C1,09-27 22:49,09-27 ~23:00,09-27 23:28,UNTESTABLE (supply 0/12; seat's supply-screen flaw),UNTESTABLE,N,POST,N,Y,<1 h,roles/Aphrodite/engine/A18_C1_RESULT_2026-09-27.json
APH-A19-C2,Aphrodite,local engine W5,G1 is a stepping stone,09-27 23:28,09-28 00:46,09-28 01:20,G1_STEPPING_STONE NO; GENERIC 0/2; S-NAT UNTESTABLE,NULL,Y,-,N,Y,~2 h,roles/Aphrodite/engine/A19_C2/
APH-A20-C3,Aphrodite,local engine W5,recurrence-controlled stepping stone,09-28 05:36,09-28 ~05:54,09-28 06:49,UNTESTABLE (observe floor vs escrow cliff),UNTESTABLE,N,POST,N,Y,~1 h,roles/Aphrodite/engine/A20_C3/A20_C3_RESULT_2026-09-28.json
APH-A21-C3R,Aphrodite,local engine W5,C3R no observe floor,09-28 06:49,09-28 ~07:00,09-28 07:40,INVALID_DESIGN_DEFECT (inert motifs),INVALID,N,POST,N,Y,<1 h,git 29453b20c
APH-A22-C3R2,Aphrodite,local engine W5,"genuine motifs, supply-screened panel",09-28 07:45,09-28 ~08:00,09-28 10:06,UNTESTABLE (5/8 fillable <6),UNTESTABLE,Y,POST,N,Y,~2 h,git 8d47bbf9d
APH-A23-C3R2C,Aphrodite,local engine W5,G1 recurrent stepping stone n=12,09-28 10:07,09-28 ~10:10,09-28 14:31,YES; GENERIC 3/3; p=0.0078; constructed recurrence,POSITIVE,Y,"POST(minor, Artemis #871)",N,Y,~4 h,roles/Aphrodite/engine/A23_C3R2C/A23_C3R2C_RESULT_2026-09-28.json
NES-cw01-e01,Nestor,cw01 policy world,retention selected under necessity,09-17 20:54,=frz,09-17 21:25,COMPLETE 5/5,POSITIVE,Y,PRE,N,N,30.6 min,roles/Nestor/campaigns/cw01-2026-09-17/experiments/cw01-e01/RESULT.json
NES-cw01-e02,Nestor,cw01,ancestral efficiency ratchet,09-17 21:27,=frz,09-17 21:57,NULL,NULL,Y,-,N,N,29 s,.../cw01-e02/RESULT.json
NES-cw01-e03,Nestor,cw01,input-conditional coalitions,?,?,09-17 22:13,COMPLETE,POSITIVE,Y,-,N,N,74 s,.../cw01-e03/RESULT.json
NES-cw01-e04,Nestor,cw01,queue/TTL triage ecology,?,?,09-18 00:16,INCONCLUSIVE (noise floor measured post-run),KILLED,N,POST,Y,N,55 s,.../cw01-e04/RESULT.json
NES-cw01-e05,Nestor,cw01,superadditive mixtures,09-18 07:24,=frz,09-18 08:07,NULL,NULL,Y,PRE,N,N,30 s,.../cw01-e05/RESULT.json
NES-cw01-e06,Nestor,cw01,representation ecology,?,-,09-18 11:23,DESIGN UNREACHABLE (gate Q16),UNTESTABLE,Y,PRE,N,N,~0,roles/Nestor/campaigns/cw01-2026-09-17/CAMPAIGN_STATE.json
NES-cw01-e07,Nestor,cw01,computational weather,09-18 12:13,-,09-18 12:30,DESIGN UNREACHABLE (gate refused),UNTESTABLE,Y,PRE,N,N,~0,same
NES-cw01-e08,Nestor,tensor-train organism,rank-tax burden,09-18 14:01,=frz,09-18 14:12,INCONCLUSIVE (contrast NOT_VERIFIED),UNTESTABLE,Y,POST,N,N,~10 min,.../cw01-e08/RESULT.json
NES-cw01-e09,Nestor,algorithmic soup,composition/reuse,-,-,09-18 14:23,DESIGN UNREACHABLE (reconcile),UNTESTABLE,Y,PRE,N,N,0,CAMPAIGN_STATE.json
NES-cw01-e10,Nestor,mutable graph physics,-,-,-,-,PENDING,PARKED,-,-,N,N,-,CAMPAIGN_STATE.json
NES-Z80A-72H,Nestor,Z80 x Atlas grammar,what replicates spontaneously,09-19 14:49,=frz,09-22 21:30,WEAK_SIGNAL; narrowed 3x; 910/1031 splice artifacts,NULL,Y,POST,Y,N,"72 wall-h, 23,471 runs",roles/Nestor/FINDINGS.md s.A
NES-S2-P11,Nestor,P-11 causal-copy assay,pair-tape copying causal,09-23 13:22,=frz,09-23 13:22,INSTRUMENT 14/14 (later UNSOUND per Artemis),POSITIVE,Y,POST,Y,N,-,roles/Nestor/campaigns/z80atlas-verify-2026-09-22/P11_SPEC.md
NES-S1B-H4,Nestor,replays,A-4 accessibility vs extinction,09-23,-,09-23 13:36,INVALID: control crossed first; withdrawn,KILLED,Y,-,N,Y,-,.../H4_AUTOPSY.md
NES-S1C-P11,Nestor,P-11,how many of 1031 survive,09-23 13:38,-,09-24 04:32,WEAK_SIGNAL 57 survive,NULL,-,-,Y,Y,-,.../S1C_P11_REASSAY.md
NES-C9-H3RULER,Nestor,C9,H3 ruler tracks material,09-24 10:48,=frz,09-24 11:06,R3 9/9 after D14 caught pre-freeze,POSITIVE,Y,PRE,N,N,4 wall-h,.../H3_RULER_TOURNAMENT.json
NES-C9-H1,Nestor,repaired Z80 VM,H1 cue gating,09-24 11:06,=frz,09-24 17:52,"INVALID (C9-D16 wiring) after 1,200 runs",INVALID,Y,POST,Y,N,40.4 CPU-h (C9 total),roles/Nestor/campaigns/z80atlas-verify-2026-09-22/observatory/C9_OUTCOME_AND_ADDENDUM.md
NES-C9-H2,Nestor,repaired Z80 VM,H2 propagation,09-24 11:06,=frz,09-24 17:52,REPLICATION_EVENTS_WITHOUT_PROPAGATION (WS),NULL,Y,-,N,N,(C9),same
NES-C9-H3,Nestor,repaired Z80 VM,H3 easy-niche reservoir,09-24 11:06,=frz,09-24 17:52,NOT_DEMONSTRATED / CLEAN_NULL,NULL,Y,-,N,N,(C9),same
NES-X-NONPAIR-SEARCH,Nestor,FREE non-pair physics,in-place search makes births,09-24 11:07,=frz,09-24 11:44,WEAK_SIGNAL,NULL,-,-,N,N,96 runs,roles/Nestor/campaigns/c9x-explore-2026-09-24/x_nonpair_search/
NES-X-NONPAIR-FIDELITY,Nestor,replays,no copying vs imperfect copying,09-24 11:44,=frz,09-24 12:01,WEAK_SIGNAL,NULL,-,-,N,N,~25 replays,.../x_nonpair_fidelity/
NES-X-SELFLOC-FREE,Nestor,FREE+BLOCK,self-location barrier,09-24 12:01,=frz,09-24 12:25,CLEAN_NULL,NULL,-,-,N,N,?,.../x_selfloc_free/
NES-X-SELFLOC-SEEDED,Nestor,implanted copier,physics supports implanted copier,09-24 12:25,=frz,09-24 12:49,SIGNAL 15/23 vs 0/23,POSITIVE,Y,-,N,N,?,.../x_selfloc_seeded/
NES-C-SELFLOC,Nestor,fresh cells,self-location gates heredity (confirm),09-24 12:49,=frz,09-24 13:20,CONFIRMED 13/36 vs 0/36,POSITIVE,Y,-,N,Y,72 runs,.../c_selfloc_confirm/VERDICT.json
NES-X-ERROR-THRESHOLD,Nestor,seeded,mutation window,09-24 12:49,=frz,09-24 14:11,CLEAN_NULL,NULL,-,-,N,Y,115 runs,.../x_error_threshold/
NES-X-ENERGY-INHERIT,Nestor,energy cells,newborn energy wall,09-24 14:11,=frz,09-24 14:31,SIGNAL 7/19 vs 1/19,POSITIVE,-,-,N,Y,?,.../x_energy_inherit/
NES-C-ENERGY,Nestor,40 fresh cells,energy inheritance (confirm),09-24 14:31,=frz,09-24 15:12,CONFIRMED 20/40 vs 4/40,POSITIVE,Y,-,N,Y,80 runs,.../c_energy_confirm/VERDICT.json
NES-X-LOCAL-ALLOC,Nestor,GRID/GRAPH,local ALLOC exhaustion,09-24 15:13,=frz,09-24 15:17,WEAK_SIGNAL (found C9-D15 artifact),NULL,-,-,N,Y,?,.../x_local_alloc/
NES-X-SPONTANEOUS,Nestor,permissive FREE,"spontaneous heredity, barriers relieved",09-24 15:17,=frz,09-24 15:39,CLEAN_NULL,NULL,-,-,N,Y,47 worlds,.../x_spontaneous/
NES-X-NEARMISS,Nestor,replays,near-miss behaviour,09-24 15:39,=frz,09-24 15:43,WEAK_SIGNAL,NULL,-,-,N,Y,-,.../x_nearmiss/
NES-X-DENSE-OPS,Nestor,1-byte op VM,encoding length barrier,09-24 15:43,=frz,09-24 16:24,INVALID (VM leaked across workers),INVALID,Y,POST,N,Y,?,.../x_dense_ops/
NES-X-DENSE-OPS-R,Nestor,dense VM repaired,same,09-24 16:24,=frz,09-24 17:06,SIGNAL 23/47 vs 0/47,POSITIVE,Y,-,N,Y,?,.../x_dense_ops/SUMMARY_R.json
NES-C-DENSE,Nestor,dense VM 40 fresh,confirm dense,09-24 17:06,=frz,09-24 17:41,CONFIRMED 13/40 vs 0/40,POSITIVE,Y,-,N,Y,80 runs,.../c_dense_confirm/VERDICT.json
NES-X-DENSE-ABLATE,Nestor,dense VM,necessary barriers,09-24 17:07,=frz,09-24 18:54,SIGNAL,POSITIVE,-,-,N,Y,?,.../x_dense_ablate/
NES-C-ABLATE,Nestor,40 fresh,confirm ablation,09-24 18:54,=frz,09-24 19:46,LOC+SEARCH CONFIRMED; ENERGY NOT,POSITIVE,Y,-,N,Y,160 runs,.../c_ablate_confirm/VERDICT.json
NES-C9-H1R,Nestor,C9 H1 rewired,H1 rerun,09-24 17:53,=frz,09-24 18:02,COST_INTERACTION_ONLY,POSITIVE,Y,PRE,N,N,240 runs,.../c9_h1r/VERDICT.json
NES-X-H2-7AE3,Nestor,specimen 7ae3,establishment lottery,09-24 18:03,=frz,09-24 18:20,WEAK_SIGNAL (C9-D17),NULL,-,POST,N,N,?,.../x_h2_7ae3/
NES-C9-H3-NULL,Nestor,H3 flow,easy material reaches hard niches,09-24 17:52,=frz,09-24 18:29,CLEAN_NULL,NULL,-,-,N,N,?,.../x_h3_flow/
NES-X-H2-TERMINATION,Nestor,7ae3,why lineages end,09-24 18:20,=frz,09-24 18:44,WEAK_SIGNAL,NULL,-,-,N,N,?,.../x_h2_termination/
NES-X-H3-EASIER,Nestor,niche 0,easy niche competent,09-24 18:29,=frz,09-24 18:35,CLEAN_NULL; H3 RETIRED,NULL,Y,-,N,N,?,.../x_h3_easier/
NES-X-H2-NORECOMB,Nestor,splice off,splice causes depth ceiling,09-24 18:44,=frz,09-24 19:10,WEAK_SIGNAL,NULL,-,-,N,N,?,.../x_h2_norecomb/
NES-C-NORECOMB,Nestor,2 specimens x 24,confirm norecomb,09-24 19:10,=frz,09-24 20:03,NOT_CONFIRMED 5/48 vs 5/48,NULL,Y,-,N,N,?,.../c_norecomb_confirm/VERDICT.json
NES-X-PAIR-NORECOMB,Nestor,random pair tape,splice suppresses heredity,09-24 19:47,=frz,09-24 20:08,CLEAN_NULL -> INVALID 09-28 (no positive arm),INVALID,N,POST,Y,N,?,.../x_pair_norecomb/
NES-X-RUNAWAY,Nestor,7ae3 splice off,runaway anatomy,09-24 20:03,=frz,09-24 20:30,SIGNAL (descriptive),POSITIVE,-,-,N,N,?,.../x_runaway/
NES-X-H1-TRANSPLANT,Nestor,4 task transforms,H1 interaction transplants,09-24 20:09,=frz,09-24 20:24,SIGNAL 4/4,POSITIVE,Y,-,N,Y,?,.../x_h1_transplant/
NES-X-H1-GRADIENT,Nestor,probe,gate removes guessers,09-24 20:25,=frz,09-24 20:28,WEAK_SIGNAL,NULL,-,-,N,Y,?,.../x_h1_gradient/
NES-C-RUNAWAY,Nestor,7ae3 150/arm,splice prevents runaway,09-24 20:30,=frz,09-24 22:03,CONFIRMED 7/150 vs 0/150,POSITIVE,Y,-,N,Y,300 runs,.../c_runaway_confirm/VERDICT.json
NES-X-RUNAWAY-TRANSPLANT,Nestor,other specimens,runaway generalizes,09-24 22:03,=frz,09-24 22:45,CLEAN_NULL (specimen-specific),NULL,Y,-,N,Y,?,.../x_runaway_transplant/
NES-X-POSITION,Nestor,P-11,copier position-independent,09-24 22:45,=frz,09-24 22:50,WITHDRAWN (assay sabotage),INVALID,N,POST,N,Y,?,.../x_position/
NES-X-STATE,Nestor,runaway,copies depend on register state,09-24 22:46,=frz,09-24 22:50,WEAK_SIGNAL,NULL,-,-,N,Y,?,.../x_state/
NES-X-SUFFICIENCY,Nestor,runaway vs stall,sufficiency separates,09-24 22:47,=frz,09-24 22:50,CLEAN_NULL,NULL,-,-,N,Y,?,.../x_sufficiency/
NES-X-CRITICAL-MASS,Nestor,7ae3 k=1 vs 4,critical mass,09-24 22:50,=frz,09-24 23:43,WEAK_SIGNAL 9/64,NULL,-,-,N,Y,?,.../x_critical_mass/
NES-C-CRITICAL-MASS,Nestor,80/arm,critical mass (confirm),09-24 23:43,=frz,09-25 00:53,CONFIRMED 41/80 vs 5/80 (post-hoc superadditivity later killed),POSITIVE,Y,-,N,Y,160 runs,.../c_critical_mass/VERDICT.json
NES-X-DOSE-CURVE,Nestor,k in 1..8,superadditive establishment,09-25 00:53,=frz,09-25 03:02,CLEAN_NULL (independent tickets),KILLED,-,-,N,Y,?,.../x_dose_curve/
NES-X-TICKET,Nestor,7ae3,losing tickets,09-25 03:07,=frz,09-25 03:54,WEAK_SIGNAL,NULL,-,-,N,Y,128 runs,.../x_ticket/
NES-X-DECAY,Nestor,dose f,mutation stops copying,09-25 03:54,=frz,09-25 05:01,WEAK_SIGNAL,NULL,-,-,N,Y,192 runs,.../x_decay/
NES-X-STALL,Nestor,replays,STATE/GENOME/CONTEXT,09-25 05:01,=frz,09-25 05:18,SIGNAL GENOME 177/192,POSITIVE,Y,-,N,Y,-,.../x_stall/
NES-X-STERILE,Nestor,"g in 1,0",children sterile,09-25 05:18,=frz,09-25 06:13,CLEAN_NULL,NULL,-,-,N,Y,?,.../x_sterile/
NES-X-STALL-F0,Nestor,f=0,erosion attribution,09-25 06:13,=frz,09-25 06:23,SIGNAL write-back 25x,POSITIVE,Y,-,N,Y,-,.../x_stall_f0/
NES-X-ATOMIC,Nestor,ATOMIC write-back,removing erosion sustains heredity,09-25 06:23,=frz,09-25 08:03,SIGNAL 36/64 vs 3/64,POSITIVE,-,-,N,Y,128 runs,.../x_atomic/
NES-C-ATOMIC-C1,Nestor,7ae3 80/arm,confirm atomic,09-25 08:03,=frz,09-25 10:22,CONFIRMED 46/80 vs 1/80,POSITIVE,Y,-,N,Y,160 runs,.../c_atomic/VERDICT.json
NES-C-ATOMIC-C2,Nestor,15 specimens,atomic generalizes,09-25 08:03,=frz,09-25 11:02,NOT_CONFIRMED,NULL,Y,-,N,Y,240 runs,same
NES-X-DONOR-RATE,Nestor,assay,donor competence first barrier,09-25 11:02,=frz,09-25 11:03,SIGNAL,POSITIVE,-,-,N,Y,-,.../x_donor_rate/
NES-X-DONOR-SWAP,Nestor,7ae3 in 11 cells,cells permit runaway,09-25 11:03,=frz,09-25 12:48,WEAK_SIGNAL 3/11,NULL,Y,-,N,Y,96 runs,.../x_donor_swap/
NES-X-SWAP-ORIGIN,Nestor,replays,foreign runaways founder-rooted,09-25 12:50,=frz,09-25 13:18,CLEAN_NULL (label later corrected),NULL,Y,-,Y,Y,?,.../x_swap_origin/
NES-X-ROOT-AUDIT,Nestor,C-ATOMIC rows,C1 survives founder-rooted endpoint,09-25 13:18,=frz,09-25 15:03,WEAK_SIGNAL 12/80 vs 0/80,NULL,Y,-,N,Y,?,.../x_root_audit/
NES-X-ATOMIC-RANDOM,Nestor,random implant,effect needs 7ae3 genome (missing null),09-25 15:03,=frz,09-25 15:46,SIGNAL 0/80 vs 46/80,POSITIVE,Y,-,N,Y,80 runs,.../x_atomic_random/
NES-X-SWAP-ANCESTRY,Nestor,replays,foreign runaways founder-descended,09-25 15:46,=frz,09-25 16:08,SIGNAL,POSITIVE,Y,-,N,Y,-,.../x_swap_ancestry/
NES-C-SWAP-ACQUIRE,Nestor,240/arm,founder lineage acquires runaway,09-25 16:08,=frz,09-25 18:52,NOT_CONFIRMED 9/240 vs 0 (bar 10; power ~0.45),NULL,N,POST,N,Y,480 runs,.../c_swap_acquire/VERDICT.json
NES-X-ACQUIRE,Nestor,assay,descendants acquired competence,09-25 16:08,09-25 16:24,09-25 18:56,WEAK_SIGNAL,NULL,Y,-,N,Y,?,.../x_acquire/
NES-X-CONTENT,Nestor,z8taint,runaways carry founder bytes,09-25 18:56,=frz,09-25 19:30,WEAK_SIGNAL,NULL,Y,-,N,Y,-,.../x_content/
NES-X-CORE,Nestor,z8taint,conserved core,09-25 19:30,=frz,09-25 19:53,WEAK_SIGNAL,NULL,-,-,N,Y,-,.../x_core/
NES-C-CORE,Nestor,64 fresh,SELF+LDIR conserved,09-25 19:53,=frz,09-25 21:04,CONFIRMED 17/27 (scope limited by Aporia #621; SI framing withdrawn by operator),POSITIVE,Y,-,Y,Y,64 runs,.../c_core/VERDICT.json
NES-X-CORE-TIME,Nestor,trajectories,core held vs re-fixed,09-25 21:04,=frz,09-25 21:31,SIGNAL,POSITIVE,Y,-,Y,Y,-,.../x_core_time/
NES-X-CERT-BREAK,Nestor,P-11,uncertified events,09-25 21:31,=frz,09-25 21:55,WEAK_SIGNAL,NULL,-,-,N,Y,-,.../x_cert_break/
NES-X-DONOR-DISCOVERY,Nestor,7ae3/ffa6 ATOMIC,donor acquisition limit,09-26 13:37,=frz,09-26 14:19,SIGNAL 1/96,POSITIVE,Y,PRE,N,Y,96 runs,roles/Nestor/campaigns/npe-w1-donor-discovery-2026-09-26/x_donor_discovery/
NES-X-DD-DENSE-COPY,Nestor,DENSE_COPY VM,encoding accessibility,09-26 14:19,=frz,09-26 15:51,SIGNAL 0/96 -> 49/96,POSITIVE,Y,-,N,Y,192 runs,.../x_dd_dense_copy/
NES-C-DENSE-COPY,Nestor,64/arm,confirm dense copy,09-26 15:51,=frz,09-26 16:48,CONFIRMED 1/64 vs 39/64,POSITIVE,Y,-,N,Y,128 runs,.../c_dense_copy/VERDICT.json
NES-X-DD-ESTABLISH,Nestor,replays,where establishment fails,09-26 16:49,=frz,09-26 18:12,SIGNAL NO_COPY 80%,POSITIVE,Y,-,N,Y,-,.../x_dd_establish/
NES-X-DD-NOCOPY-CONTEXT,Nestor,probe,context blocks copying,09-26 18:12,=frz,09-26 18:25,WEAK_SIGNAL (withdrawn),NULL,-,-,N,Y,-,.../x_dd_nocopy_context/
NES-X-DD-STATE-RESET,Nestor,reset on genome change,rescues establishment,09-26 18:25,=frz,09-26 20:13,CLEAN_NULL,NULL,Y,-,N,Y,?,.../x_dd_state_reset/
NES-X-DD-SELFSTATE,Nestor,probe,self-poisoning,09-26 20:13,=frz,09-26 20:14,WEAK_SIGNAL; ruler later INVALID,INVALID,N,POST,Y,Y,-,.../x_dd_selfstate/
NES-X-DD-STATELESS,Nestor,stateless exec,state persistence barrier,09-26 20:14,=frz,09-26 22:01,SIGNAL .38 -> .90,POSITIVE,Y,-,N,Y,?,.../x_dd_stateless/
NES-C-STATELESS,Nestor,24/cell/arm,confirm stateless,09-26 22:01,=frz,09-26 23:19,NOT_CONFIRMED,NULL,Y,-,N,Y,?,.../c_stateless/VERDICT.json
NES-C-STATELESS-FFA6,Nestor,ffa6 48/arm,confirm in ffa6,09-26 23:19,=frz,09-27 00:44,CONFIRMED 11/33 vs 34/42 (re-described later),POSITIVE,Y,-,Y,Y,96 runs,.../c_stateless_ffa6/VERDICT.json
NES-X-P2-BRIDGE,Nestor,16 W1 donors,cell axis makes state a barrier,09-27 21:01,=frz,09-27 21:41,CLEAN_NULL (withdrew W1 ffa6 reading),NULL,Y,-,N,Y,32 runs/arm,roles/Nestor/campaigns/npe-p2-endogenous-heredity-2026-09-27/x_p2_bridge/
NES-X-P2-ENDOSTATE,Nestor,lineages,endogenous state robustness,09-27 21:17,=frz,09-27 21:18,CLEAN_NULL -> ruler defect,INVALID,N,POST,Y,Y,-,.../x_p2_endostate/
NES-X-P2-ATTRIB,Nestor,stock vs dense VM,competence via alias,09-27 21:21,=frz,09-27 21:22,SIGNAL 372/372 (negative control not exercised),POSITIVE,N,POST,N,Y,-,.../x_p2_attrib/
NES-X-P2-PLANT,Nestor,stock VM planted,presence suffices,09-27 21:23,=frz,09-28 01:16,SIGNAL 32/96,POSITIVE,-,-,N,Y,96 runs,.../x_p2_plant/
NES-X-P2-REGSTATE,Nestor,reset variants,what rescues,09-27 21:23,=frz,09-27 22:14,SIGNAL ZERO_SPECIFIC,POSITIVE,Y,-,N,Y,32 runs/arm,.../x_p2_regstate/
NES-X-P2-LINEAGE,Nestor,replays,late genomes descend from D0,09-27 21:23,=frz,09-27 22:59,WEAK_SIGNAL 4/13,NULL,Y,-,N,Y,-,.../x_p2_lineage/
NES-X-P2-SHAM,Nestor,sham dense VM,block-write density rival,09-27 21:23,=frz,09-28 01:16,CLEAN_NULL 0/96 (rival killed),KILLED,Y,-,N,Y,96 runs,.../x_p2_sham/
NES-C-ZERO-SPECIFIC,Nestor,ffa6 fresh panel,rescue is ZERO-specific,09-27 22:14,=frz,09-28 01:31,CONFIRMED 26/48 vs 2/48,POSITIVE,Y,-,N,Y,192 runs,.../c_zero_specific/VERDICT.json
NES-X-P2-D0CHECK,Nestor,replays,D0 already robust,09-27 22:59,=frz,09-27 23:06,CLEAN_NULL,NULL,Y,-,N,Y,-,.../x_p2_d0check/
NES-X-A3-FAIR,Nestor,treatment-blind ruler,zero specialization not artifact,09-28 05:20,=frz,09-28 09:19,SIGNAL ZERO_LITERAL,POSITIVE,Y,-,N,Y,?,roles/Nestor/campaigns/npe-arc3-2026-09-28/x_a3_fair/
NES-X-A3-AUTOPSY,Nestor,autopsy,where reproduction fails,09-28 05:23,=frz,09-28 09:28,SIGNAL,POSITIVE,-,-,N,Y,?,.../x_a3_autopsy/
NES-X-A3-WITHDRAW,Nestor,scaffold withdrawal,gradual withdrawal matters,09-28 05:31,=frz,09-28 14:12,CLEAN_NULL,NULL,Y,-,N,Y,?,.../x_a3_withdraw/
NES-X-A3-FORENSIC,Nestor,delegate forensic,single heritable change,09-28,-,09-28 06:26,"KILLED (knock-in 0/5, revert 0/8)",KILLED,Y,-,N,Y,-,.../delegates/forensic_16000006/
NES-X-A3-ENDOSTATE-R,Nestor,cycle-aware ruler,re-measure endostate,09-28 06:28,=frz,09-28 06:30,WEAK_SIGNAL,NULL,Y,-,N,Y,-,.../x_a3_endostate_r/
NES-X-A3-SFLINEAGE,Nestor,replays,within-lineage internalization,09-28 06:31,=frz,09-28 08:18,SIGNAL 3/5,POSITIVE,Y,-,N,Y,-,.../x_a3_sflineage/
NES-C-A3-INTERNALIZE,Nestor,dense VM 144 fresh,recurrent endogenous internalization,09-28 08:18,=frz,09-28 11:32,CONFIRMED 8 events (bar 4),POSITIVE,Y,-,N,Y,144 runs,.../c_a3_internalize/VERDICT.json
NES-ANCESTRY-REPLAY,Nestor,T-003 + Z8 tracer,who built which bytes (NPE leg of E-003),09-28 23:17,09-29 00:29,09-29 05:26,run1 INVALIDATED; v2.2 flip coverage FAIL -> INCONCLUSIVE,UNTESTABLE,Y,POST,N,N,?,roles/Nestor/campaigns/ancestry-replay-2026-09-28/
NES-X-MAT-INTERNALIZE,Nestor,dense_taint,internalization is material,09-30 08:41,09-30 ~08:30 (pilot pre-freeze),09-30 10:02,"ENDOGENOUS 8/8 (no planted-transplant PC, Harmonia #1057)",POSITIVE,Y,POST,Y,Y,7.8 core-h,roles/Nestor/campaigns/npe-frontier-2026-09-30/x_mat_internalize/RESULT.md
NES-X-TASK-GATE,Nestor,ffa6 TASK_GATED,task competence spreads by replication,09-30 18:04,-,-,"FROZEN, NOT executed",OPEN,Y,-,N,Y,-,.../x_task_gate/PREREG.md
NES-C3-HOLDOUT-D,Nestor,128 hidden worlds,blind holdout for Cosmos,09-25 19:00,-,09-28,EXPOSED by merge; never used blind,PARKED,Y,-,Y,N,-,roles/Nestor/C3_HOLDOUT_D_REPORT.md
NES-C3-HOLDOUT-D2,Nestor,AES-sealed 128 worlds,successor holdout,09-28 09:34,-,09-29 14:34 (audit PASS),SEALED/UNREAD/UNSPENT,PARKED,Y,PRE,N,N,-,roles/Nestor/WORK_STATE.json
COS-C0,Cosmos,visible worlds + sealed D,compact phase-boundary law,09-23 11:41,09-23 11:54,09-23 12:28,no surviving invariant,NULL,Y,POST(run1 crash),N,N,"1,957 s",roles/Cosmos/campaigns/c0/RESULT_run2.md
COS-C0b,Cosmos,"v3 coords, sealed D",law A survives D,09-23 12:39,=frz,09-23 12:53,SURVIVED .983 -> RESTRICTED 09-29 (no margin over zero-param rung),KILLED,Y,POST,Y,Y,-,roles/Cosmos/research/RESULTS.md R-0001
COS-C0e,Cosmos,sealed E,law A transfers,09-23 12:57,=frz,09-23 12:58,PASS .972 (later planted-invariant recovery),POSITIVE,Y,-,Y,Y,-,roles/Cosmos/campaigns/c0e/
COS-C0m,Cosmos,repetition code,law on new mechanism,09-23 13:00,=frz,09-23 13:01,M1/M2 PASS; M3 lost by .005,POSITIVE,-,-,N,Y,-,roles/Cosmos/campaigns/c0m/
COS-C0s,Cosmos,stress,ceiling bias,09-23 13:01,=frz,09-23 13:04,S2 INVALID ladder defect -> S2b +0.045 9/9,INVALID,Y,POST,N,Y,-,roles/Cosmos/campaigns/c0s/
COS-C1,Cosmos,v4 coords,improved law,09-23 13:24,09-23 13:29,09-23 14:30,no survivor (location gate),NULL,-,POST(MemoryError),N,Y,-,roles/Cosmos/campaigns/c1/
COS-C2,Cosmos,sealed F,law B,09-23 14:30,=frz,09-23 15:24,"F A .930, B .955, B>A n.s.; RESTRICTED 09-29",KILLED,Y,POST,Y,Y,-,roles/Cosmos/campaigns/c2/F_adjudication.json
COS-ETA2,Cosmos,cost-line vs random,cost lines help,09-23 15:25,=frz,09-23 15:35,NOT earned .767 vs .946,KILLED,Y,-,N,Y,-,roles/Cosmos/campaigns/eta2/
COS-C2X,Cosmos,attribution arms,selection/cost lines needed,09-23 15:36,=frz,09-23 16:46,attribution UNRESOLVED,NULL,Y,-,Y,Y,-,roles/Cosmos/campaigns/c2x/PREREG.md
COS-C3-S1-GATE-v2,Cosmos,6 planted systems,certificate classifies,09-24 ~07:10,09-24 07:13,09-24 07:13,FAIL (instrument),INVALID,Y,PRE,N,N,-,roles/Cosmos/c3/runs/GATE_v2_FAIL.json
COS-C3-S1-GATE-v3,Cosmos,seeds 6-10,certificate classifies,09-24 ~07:15,=frz,09-24 07:19,PASS,POSITIVE,Y,-,N,N,-,roles/Cosmos/c3/runs/GATE_v3_PASS_seeds6to10.json
COS-C3-LAW,Cosmos,120 visible worlds,candidate invariant,09-24 (withheld F-0000),09-24,09-29 12:21,REJECT: zero-param rule 104/120; KILLED BEFORE HOLDOUT,KILLED,Y,PRE,Y,Y,2 x 5-min reviews,roles/Cosmos/research/reviews/COORD_AUDIT_C3_2026-09-29.md
COS-T-I1,Cosmos,graveyard atoms,atoms re-express definition rung,09-29 02:54,=frz,09-29 03:59,v1/v2 defects; v3 11/15,POSITIVE,Y,PRE,N,Y,-,roles/Cosmos/research/GRAVEYARD.md
COS-C4,Cosmos,C4 design v0.2,uplift where shortcut fails,09-30 13:47,-,-,DESIGNED; R-STAT interim BLOCKING,OPEN,Y,PRE,N,Y,synthetic,roles/Cosmos/c4/DESIGN_C4.md
ENS-E0,Ensorain,e0 TT/ALS learners,evolved TT memory beats non-TT,09-23 11:05,?,09-23 12:10,INDETERMINATE (planted PC R^2 .007); frozen as useful negative,UNTESTABLE,Y,POST,Y,N,"15,760 lives",ensorain/E0_VERDICT.md
ENS-E1,Ensorain,e1 TT vs baselines,TT beats non-TT per parameter,09-23 14:15,?,09-23 14:30,INDETERMINATE; rank-1 LOWRANK beats TT,KILLED,Y,POST,N,N,"10,081 lives",ensorain/E1_VERDICT.md
ENS-E1.5,Ensorain,e1p5 caps,compression-headroom transition,09-23 21:31,?,09-23 21:44,CLOSE(B) -> operator INTRIGUING; PARKED,PARKED,Y,-,Y,N,"12,960 lives",ensorain/E1P5_VERDICT.md
ENS-E2,Ensorain,e2 structure discovery,in-life factorization discovery,09-23 21:57,?,09-23 22:09,INDETERMINATE (control 2.7-SE chance),NULL,Y,-,N,N,"4,800 lives",ensorain/E2_VERDICT.md
ENS-D1,Ensorain,d1 random dials,nominate couplings,09-24 06:45,?,09-24 07:11,14 pairs nominated; T2/T3 not supported,NULL,Y,-,N,N,"4,800 lives",ensorain/D1_ROUND1.md
ENS-D2,Ensorain,d1 confirm grids,confirm R1 nominations,09-24 07:11,?,09-24 07:23,INSTRUMENT CONTROLS FAIL,UNTESTABLE,Y,POST,N,N,"3,192 lives",ensorain/D2_ROUND2.md
ENS-D3,Ensorain,d1 local,intrinsic couplings,09-24 07:23,?,09-24 07:39,CONTROLS PASS; nominations,POSITIVE,Y,-,N,N,"4,800 lives",ensorain/D3_ROUND3.md
ENS-D4,Ensorain,fresh seeds,replicate D3,09-24 07:23,?,09-24 07:44,M1 REPLICATED,POSITIVE,Y,-,N,Y,"1,536 lives",ensorain/DIALS_SYNTHESIS.md
ENS-WTP01,Ensorain,wtp foundry,replicated competence anomalies,09-24 08:18,?,09-24 08:43,SEARCH SPACE MOSTLY DEGENERATE (metric artifact),NULL,Y,POST,N,N,~30 min,ensorain/ENSORAIN_WTP01_REPORT.md
ENS-WTP02,Ensorain,wtp2,candidate intelligence physics,09-24 08:53,?,09-24 09:52,EXPAND -> operator PARK/REDESIGN (one-float constant),KILLED,Y,POST,Y,N,?,ensorain/WTP02_OPERATOR_RULING.md
ENS-WTP03,Ensorain,wtp3 + N0-N5,physics beyond completion,09-24 22:12,?,09-25 09:07,CANDIDATE PHYSICS -> seat KNOWN PHYSICS (N6 beats all),KILLED,Y,POST,Y,Y,?,ensorain/ENSORAIN_WTP03_REPORT.md
ENS-LM01,Ensorain,lm01 on WTP generators,lossless state does not reach bounded-repr competence,09-28 09:35 (v0.3.2),-,-,FROZEN_NOT_LAUNCHED; HOLD,PARKED,Y,PRE,N,N,"planned 1,968 worlds",ensorain/PREREG_WTP_LM01.md
ENS-S1-PILOT,Ensorain,exact-oracle ladder,compression locus vs sufficient statistic,09-28 06:32,=frz,09-28 06:36,LOCUS IRRELEVANT; replicated 09-29,POSITIVE,Y,-,N,N,93 s,ensorain/arc3/suff/RESULTS_S1_PILOT.md
ENS-PKGF-PROBE,Ensorain,LM01 SELECTIVE,restoring distinctions helps/hurts,none,09-28,09-28 06:54,harm vanishes under recency readout,POSITIVE,Y,-,N,N,53 s,ensorain/arc3/RESULTS_PKGF_PROBE.md
ENS-T25,Ensorain,CSSR + Fabric,window sufficiency,09-29 04:00,09-29 09:15,09-29 11:35,"G1-G3 survive, G4 refuted",POSITIVE,Y,-,N,Y,3 Fabric tasks,branch ensorain: reviews/T25_CSSR_REVIEW_2026-09-29.md
ENS-CRYPT,Ensorain,learned crypticity,crypticity tracks truth,09-29 12:55,=frz,09-29 14:03,K1 refuted; one-sided bound,NULL,Y,-,N,Y,small,branch ensorain: arc3/suff/CRYPT_LEARNED.md
ENS-PKGF-CHAIN,Ensorain,PKG-F detectors,regime detector gating,09-29 14:36,=frz,09-30 03:48,mixed; several refutations,NULL,Y,-,N,Y,small,branch ensorain commits 860a861fa..f7656908f
ENS-PKGF-OBS,Ensorain,pkgf_obs gate,low-power cells don't leak stale records,09-30 14:01,09-30 14:02,09-30 14:06,OB1 survives; OB2 refuted,POSITIVE,Y,-,Y,Y,48 worlds,branch ensorain fe6393297
ENS-LM02,Ensorain,lm02 88 worlds,finite window preserves competence,09-30 14:33,09-30 14:34,09-30 14:51,WINDOW_NOT_SUPPORTED; INSTRUMENT OK,NULL,Y,-,N,Y,8 workers,branch ensorain: arc3/lm02/RESULTS_LM02_ASSAY.md
AET-AETH01-FL,Aether,aeth01.v1 4096^2 A40,endogenous organization at scale,none,09-22 20:13,09-23 00:26,no endogenous organization (scout predicted null),NULL,Y(ignored),-,N,N,"$2.02, 4.1 A40-h",Aether/AETH-01/FIRST_LIGHT_01_2026-09-22.md
AET-AETH02,Aether,aeth01.v1 2048^2 A40,spontaneous functional circuitry,09-23 21:45,09-24 07:04,09-24 12:40,no (observer 250 ticks stale; 3rd traj truncated),NULL,Y,POST,Y,N,~$2.82,Aether/AETH-01/NATIVE_CIRCUITRY_01_2026-09-24.md
AET-AETH03-PD01,Aether,128^2 CPU scouts,one-change physics propagates,09-26 06:53,09-26,09-26 07:52,KILLED K-b x4; no scale-up,KILLED,Y,PRE,N,N,$0,Aether/AETH-03/PHYSICS_DESIGN_01_2026-09-26.md
AET-AETH03-PD02,Aether,mov/rcv/m4,propagation candidate earns scale-up,09-26 14:20,09-26,09-26 16:47,"mov, m4 KILLED; rcv UNRESOLVED",KILLED,Y,PRE,N,N,$0,Aether/AETH-03/PHYSICS_DESIGN_02_2026-09-26.md
AET-E003,Aether,assay audit,causal generation exact,09-27 15:16,09-27,09-27 15:45,exact after repair; one claim withdrawn,POSITIVE,Y,-,N,N,CPU,ops/campaigns/C-002/E-003/RESULT.md
AET-E005,Aether,8 units 10k ticks,locality horizon-robust,09-27 15:16,09-27 15:58,09-27 16:09,horizon-robust,NULL,Y,-,N,N,"pod, 426 s max",ops/campaigns/C-002/E-005/RESULT.md
AET-E006,Aether,72 units A5000 pod,combinations super-additive,09-27 15:16,09-27 16:55,09-27 18:03,"rcv_add, rcv_str NEW_BEHAVIOUR; fwd PC FAILED; falsifier 2 lost",POSITIVE,Y,POST,Y,N,pod,ops/campaigns/C-002/E-006/RESULT.md
AET-E008,Aether,4 Fabric tasks,Block D is transient,09-27 15:16,09-29 03:00,09-29 04:08,HORIZON-DEPENDENT clause iii only,POSITIVE,Y,-,N,Y,~13 min/unit,ops/campaigns/C-002/E-008/RESULT.md
AET-E009,Aether,seeds 4-7,Block D replicates,09-29 12:12,09-29 12:46,09-29 13:43,REPLICATED both,POSITIVE,Y,-,N,Y,~2 CPU-h,ops/campaigns/C-002/E-009/RESULT.md
AET-E010,Aether,rcv_sfx lesion,steering required,09-30 08:54,09-30 09:00,09-30 09:29,STEERING_REQUIRED (Harmonia SUPPORTED),POSITIVE,Y,-,N,Y,<1 CPU-h,ops/campaigns/C-002/E-010/RESULT.md
AET-E011,Aether,rcv_adr lesion,trace compounding required,09-30 09:35,09-30 09:40,09-30 10:21,PARTIAL (lesion leaky),NULL,Y,-,N,Y,<1 CPU-h,ops/campaigns/C-002/E-011/RESULT.md
AET-E012,Aether,rcv_sfz lesion,dynamic vs static coupling,09-30 10:25,-,-,prereg only,OPEN,Y,-,N,Y,-,ops/campaigns/C-002/E-012/EXPERIMENT.md
HEC-PROBE-R1,Hecate,"opus-5-5 implementers, 16 worlds",triplicate mechanisms show SIGNAL,09-30 02:10,09-30 02:18,09-30 02:35,"3 SIGNAL, 6 NULL, 1 CONF, 3 INSTR_FAIL, 3 NOT_BUILT",POSITIVE,Y,POST,N,N,16.9 core-min,hecate/programs/PROBE_ROUND1_REPORT.json
HEC-PASS4-R1,Hecate,attacker,round-1 signals survive,09-30 02:36,09-30 02:37,09-30 02:41,"2 PARK, 1 known mechanism",KILLED,Y,-,N,Y,0.3 core-min,hecate/programs/PASS4_ROUND1_REPORT.json
HEC-PROBE-R2,Hecate,13 worlds,next worlds SIGNAL,09-30 02:37,?,09-30 02:48,0 SIGNAL; 6 SPEC_UNATTAINABLE,UNTESTABLE,Y,PRE,N,N,10.8 core-min,hecate/programs/PROBE_ROUND2_REPORT.json
HEC-PROBE-R3,Hecate,"generator v2, 8 worlds",repaired generator testable,09-30 03:13,09-30 03:13,09-30 03:18,"2 SIGNAL, 6 NULL, 0 instrument fail",POSITIVE,Y,-,N,N,3.8 core-min,hecate/programs/PROBE_ROUND3_REPORT.json
HEC-PASS4-R2,Hecate,attacker,round-3 signals survive,09-30 03:19,09-30 03:20,09-30 03:26,both PARK (Harmonia: ORIG kill met but not reported),KILLED,Y,POST,Y,Y,0.7 core-min,hecate/programs/PASS4_ROUND2_REPORT.json
HEC-META-V1,Hecate,sonnet-5 gen / opus-5-5 detector,triplicates beat pairs/singles,09-30 02:44,09-30 02:44,09-30 03:08,M1 INDETERMINATE; zero UNFAMILIAR (uncalibrated),INVALID,N,POST,Y,N,model calls,hecate/meta/REPORT_v1.md
HEC-ALIEN-A,Hecate,"opus-5-5, 100 systems",LLM calls lawful-alien noise,09-30 05:40,09-30 05:41,09-30 07:51,INDETERMINATE / NOT_SUPPORTED; detector NOT_VALIDATED,NULL,Y,POST,Y,N,-,hecate/alien/REPORT_pilot.md
HEC-ALIEN-BC,Hecate,"gpt-oss-120b, gemini-3.6-flash",same,09-30 05:40,09-30,09-30 08:28,"incomplete (quota, truncation)",UNTESTABLE,N,POST,N,N,free tier,hecate/alien/DEVIATION_01.md
HEC-AUTOPSY,Hecate,meta v1 detector,zero-UNFAMILIAR is detector limit,09-30 08:21,09-30 08:22,09-30 08:25,DETECTOR_CANNOT_REACH_UNFAMILIAR,POSITIVE,-,-,N,N,small,hecate/autopsy/AUTOPSY.md
TYC-V0-ATT1,Tyche,lens evolution,(v0),09-30 06:30,09-30 10:3x,09-30 07:05,stopped: BLAS oversubscription,INVALID,Y,POST,N,N,13.0 core-h,tyche/runs/v0_2026-09-30_ABORTED
TYC-V0,Tyche,"lens evolution, 32 worlds",lenses solve planted zero-access controls,09-30 06:30,09-30 07:05,09-30 09:18,"H2,H5 PASS; H3,H4 FAIL; H1,H6 INDET -> UNREACHABLE_BY_DESIGN",UNTESTABLE,Y,POST,Y,Y,<=15.4 core-h,tyche/runs/v0_2026-09-30/REPORT.md
TYC-V1,Tyche,V0/DE/DENR arms,zero-marginal precursors only via DE,09-30 10:17,09-30 10:20,09-30 10:53,GATE 6 FAIL,NULL,Y,PRE,N,N,~2 core-h,tyche/runs/v1_2026-09-30/REPORT_v1.md
TYC-V2-BLOCKR,Tyche,STRICT/LEX/RES,reserve > lexicase > strict,09-30 13:11,09-30 13:24,09-30 14:50,RH1-RH4 FALSE; OV censored,NULL,Y,POST(memory),N,N,<=12 core-h,tyche/runs/v2_blockR/REPORT_BLOCK_R.md
THE-V0,Theseus,synth concepts,deep descendants occupy new niches,09-30 13:09,09-30 13:10,09-30 14:00,"H1 FAIL (lens leak, hash nondeterminism)",INVALID,N,POST,N,N,"9,049 CPU-s",theseus/runs/v0_2026-09-30/REPORT.json
THE-V0_1,Theseus,"same, fixed",same,09-30 14:01,09-30 14:05,09-30 14:42,H1 INDETERMINATE (n=51 underpowered),UNTESTABLE,N,POST,N,N,"~7,100 CPU-s",roles/Theseus/REVIEW_PACKET_v0_2026-09-30.txt
ARC-STAGE0,Archaeon,SFE fossils,fossil corpus supports two-arm claim,?,?,09-06 02:34,KILL under tenancy; 0 eligible units,KILLED,Y,PRE,N,N,?,archaeon/docs/STAGE0_RESULT.md
ARC-C3-1,Archaeon,SFE ca_density,criterion corpus,?,09-10,09-10 11:58,"producer error, 126 rows cancelled",INVALID,N,POST,N,N,?,roles/Archaeon/H0H5_STATUS.md
ARC-C3-2,Archaeon,SFE 150 rows,arms answer G1/H1/Q2/H2,09-10,09-10,09-10 17:56,H2 STRUCTURALLY_VOID,UNTESTABLE,Y,POST,Y,N,?,archaeon/docs/h0h5/C3_2_READOUT.md
ARC-H1H0-P2,Archaeon,SFE cegis,libraries speed CEGIS,09-10,09-10 16:31,09-10 23:16,FAIR and INERT; fresh==S00 by construction,UNTESTABLE,Y,POST,Y,N,?,archaeon/docs/h0h5/H1H0_PHASE2_READOUT.md
ARC-C3-3,Archaeon,SFE cellwise,H2 via X1 variance ratio,09-11 00:25,-,-,never issued,PARKED,Y,PRE,N,N,-,archaeon/docs/h0h5/C3_3_DESIGN.md
ARC-H5-1,Archaeon,SFE eca rules,decoder evolvability,09-10 23:31,=frz,09-11 22:10,analytic bounds; calibration only,POSITIVE,Y,-,Y,N,~3 min/row,archaeon/docs/h0h5/H5_1_READOUT_2026-09-11.md
ARC-H3-DEADSTREAM,Archaeon,h3_replay,coverage separates live from dead,09-11,09-11,09-11 20:10,task-level reuse separates,POSITIVE,Y,-,N,N,?,archaeon/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md
ARC-S1-FOSSIL,Archaeon,SFE,fossil draws beat uniform,09-12 16:55,09-12,09-12 16:59,NO_DETECTABLE_ADVANTAGE,NULL,Y,-,N,N,24 rows,git 8fc994e1f
ARC-S3-INFO,Archaeon,synthetic 120 worlds,info-seeking beats uniform,09-12 19:27,09-12,09-12 19:40,NO_ADVANTAGE (saturated endpoint),UNTESTABLE,N,POST,N,N,?,git log
ARC-S4-PRODUCERS,Archaeon,synthetic 240 worlds,producers separate,09-12 20:26,09-13,09-12 22:49,NO_SEPARATION,NULL,?,-,N,N,?,git log
ARC-S5,Archaeon,exact DP producer,work-budgeted selection,09-13 04:34,09-13 05:04,09-13 06:01,INSTRUMENT_FAILURE both runs,INVALID,N,POST,N,N,?,roles/Archaeon/CALIBRATION_LEDGER.md
ARC-S7,Archaeon,same,GATED_V2W isolates,09-13 13:47,09-13,09-13 22:30,GATE_FAILS_TO_ISOLATE,NULL,Y,POST,N,N,?,roles/Archaeon/CALIBRATION_LEDGER.md
ARC-WSE-V01,Archaeon,WSE over Proteus VM,workspace ecology map,09-16 19:10,09-16 19:23,09-16 19:53,three failure shapes,NULL,Y,-,N,N,"1,532 s",archaeon/wse/READOUT_v01.md
ARC-SSF,Archaeon,WSE stream world,selective state under cost ramp,09-16 20:16,09-16 20:25,09-16 22:47,no selective state,NULL,Y,-,N,N,"7,232 s",archaeon/wse/READOUT_ssf.md
ARC-CMP1-POS,Archaeon,SFE v2 + WSE,transfer helps (SFE-01/04-07),09-17,09-17 00:12,09-17 01:03,"WEAK POSITIVE (SFE-01, -07 later killed)",POSITIVE,Y,-,N,N,591 s,archaeon/campaign1/CAMPAIGN_REPORT.md
ARC-CMP1-NEG,Archaeon,same,SFE-08/-10,09-17,09-17 00:12,09-17 01:03,"NEGATIVE, assay capable",NULL,Y,-,N,N,same,same
ARC-CMP1-INC,Archaeon,same,SFE-02/03/09,09-17,09-17 00:12,09-17 01:03,INCONCLUSIVE (assay incapable),UNTESTABLE,N,POST,N,N,same,same
ARC-CMP2,Archaeon,SFE v2 CRN,retest CMP1 at n>=10,09-17 02:56,09-17,09-17 04:21,7 CAPABLE_NEGATIVE / 3 WEAK_POSITIVE,KILLED,Y,PRE,N,Y,"1,821 s",archaeon/campaign2/CAMPAIGN_REPORT.md
ARC-CMP3,Archaeon,WSE,shelf to summit,09-17 05:23,09-17,09-17 07:54,"7 NEG, 2 WEAK_POS, 1 INCONCL",NULL,Y,PRE,N,N,?,archaeon/campaign3/CAMPAIGN_REPORT.md
ARC-CMP4,Archaeon,engine 9.0.1,damage boundary helps discovery,09-18,09-18 05:54,09-18 06:46,NO_CONDITION_SELECTED,NULL,Y,PRE,N,N,~22 min,archaeon/campaign4/CAMPAIGN_REPORT.md
ARC-CMP5,Archaeon,representation B,failure boundary improves discovery,09-18 14:16,=frz,09-18 15:08,BOUNDARY_CREATED_NO_DISCOVERY_GAIN,NULL,Y,PRE,Y,N,~51 min,archaeon/campaign5/CAMPAIGN_REPORT.md
ARC-CMP6,Archaeon,graph organisms,observatory stress,09-18 20:08,-,-,no science rows,PARKED,Y,-,N,N,-,archaeon/campaign6/DECISIONS.md
ARC-MOAT-CENSUS,Archaeon,Z80 atlas vmcopy32,moat advantage real; copiers lottery,09-24 00:54,-,09-24 02:03,828 QUALIFIED; LOTTERY_CONSISTENT,POSITIVE,Y,-,N,N,?,roles/Archaeon/journal/2026-09-23_m2-db608f52.md
ARC-ENVGATE-01,Archaeon,vmcopy32,byte 128 gates establishment,09-24 06:39,09-24 06:40,09-24 16:05,CAUSALLY -> PARTIALLY SUPPORTED (operator R1),POSITIVE,Y,POST,Y,N,~9.3 h,archaeon/envgate/ADJUDICATION_ADDENDUM_2026-09-24.md
ARC-ENVGATE-02,Archaeon,vmcopy32,window 120..135 is causal key,09-24,09-24 21:22,09-26 07:48,WINDOW_NOT_SUPPORTED,NULL,Y,POST(KeyError),N,Y,"29,973 s",archaeon/envgate2/VERDICT_2026-09-26.md
ARC-PORTABILITY-01,Archaeon,"taint VM, BEE, NPE, PTE",causal lens ports across engines,09-26 13:03,09-26 13:11,09-27 00:25,PORTABLE_WITH_DOMAIN_LIMITS,POSITIVE,Y,-,N,N,845 BEE runs,archaeon/causal_lens/PORTABILITY01_REPORT.md
ARC-E001,Archaeon,"BEE, NPE, Archaeon",who/where/what separable,09-27 11:26,09-27 11:27,09-27 13:58,yes in all three engines,POSITIVE,Y,-,N,Y,51-932 s,ops/campaigns/C-001/E-001/RESULT.md
ARC-E002,Archaeon (Artemis exec),PTE,C-OP continuity rule,09-27,09-27 14:16,09-27 18:30,RULE INADEQUATE stands,NULL,Y,-,N,N,?,ops/campaigns/C-001/E-002/RESULT.md
ARC-DEEPBLOCK,Archaeon,taint VM block 13,founder-material turnover,09-27 17:43,09-27,09-27 18:52,0.0 founder material RETRACTED,INVALID,N,POST,Y,N,?,ops/threads/TH-013.md
ARC-ATTRIB-V0,Archaeon,"BEE, NPE, Archaeon",descent identifiable cross-engine,09-28 10:04,09-28,09-28 10:27,v1 withdrawn; identifiable 1 of 3,INVALID,N,POST,N,Y,10 min review,ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28/ASSAY.md
ARC-TH013,Archaeon,block 13 to epoch 20k,function vs material over time,09-28 09:51,09-28,09-28 11:27,machinery relocates; exactness claim withdrawn,POSITIVE,N,-,N,Y,"4,429 s",.../TH013_RESULT.md
ARC-TH015,Archaeon,24 member tapes,what must cross a generation,09-28 10:12,09-28 10:05,09-28 11:29,EXECUTED_ONLY .891; MACHINERY .028,POSITIVE,Y,-,N,Y,185 s,.../TH015_RESULT.md
ARC-ITEM8,Archaeon,block 13,material without capacity heritable,09-28 11:24,09-28,09-28,72% dead on arrival; prior 377/400 VOID,NULL,N,-,N,Y,"5,302 s",.../ITEM8_RESULT.md
BEL-EXP001,Bellerophon,BEE toolbox,reference experiment,09-19 02:55,09-19,09-19,"rows wrong, caught before report",INVALID,Y,PRE,N,N,?,roles/Bellerophon/calibration/LEDGER.md
BEL-ATLAS-BEE,Bellerophon,BEE,NPE/SFE results reproduce in BEE,09-19 12:42,09-19,09-19 13:42,"a1 INVERTED, a2/a3 CHANGED, a4/a5 ABSENT, a6 PRESERVED",POSITIVE,Y,-,N,Y,?,roles/Bellerophon/atlas_bee/REVIEW_PACKET_2026-09-19.md
BEL-GROUNDING,Bellerophon,Z80_64 copier worlds,G1-G8 predictions,09-23 12:55,=frz,09-23 17:02,mixed; G6a 160/160 -> 103/160 (errata 09-29),POSITIVE,Y,POST,Y,N,3 h 51 m x 18 workers,roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md
BEL-COUPLING,Bellerophon,BEE physics v3,computation feeds reproduction,09-24 20:07,=frz,09-25 19:42,READY_FOR_MULTIDAY; P5 FAILS ceiling,POSITIVE,Y,-,N,N,8.6 h,roles/Bellerophon/coupling_2026-09-24/COUPLING_CAMPAIGN_REPORT.md
BEL-MD,Bellerophon,BEE physics v3 20k ticks,"ladder, protection, repair",09-26 16:40,=frz,09-29 05:06,"LADDER_CLIMBED, PROTECTION_EVOLVED; LADDER2 FAILS; Q3 FAILS",POSITIVE,Y,-,N,Y,"47.1 h active, 4,160 runs",roles/Bellerophon/multiday_2026-09-26/MULTIDAY_CAMPAIGN_REPORT.md
BEL-E003-BEE,Bellerophon (Archaeon owner),BEE r022153,v0 representation of BEE births,09-29 07:30,09-29 08:02,09-29 09:38,VALIDATED -> ALTERED; verdict of record OPEN,OPEN,Y,POST,Y,N,?,roles/Bellerophon/e003_2026-09-29/ERRATA_2026-09-30.md
BEL-REPL-01,Bellerophon,BEE register world,C-A3-INTERNALIZE reproduces in BEE,09-30 11:20,=frz,09-30 12:32,DISAPPEARS (K3); descent UNRESOLVED,KILLED,Y,POST,Y,Y,300 runs,roles/Bellerophon/repl_2026-09-30/RESULT.md
BEL-REPL-02,Bellerophon,BEE register world,REPL-01 residue survives transforms,09-30 13:08,09-30 13:29,09-30 15:03,RESIDUE_NOT_REPLICATED; M6 PC 0/50,UNTESTABLE,Y,POST,N,Y,750 runs,roles/Bellerophon/repl_2026-09-30/RESULT_02.md
ANA-PTE-C1,Ananke,PTE,comm-dependent machinery evolves,09-24 12:01,09-24 12:04,09-25 00:10,"COMM_DEPENDENT, REPRODUCED (errata later)",POSITIVE,N,POST,Y,N,12 h,roles/Ananke/pte/C1_REPORT.md
ANA-PTE-C1B,Ananke,PTE,C1 mechanisms under corrected instruments,09-26 00:25,09-26 13:12,09-26 13:41,M3 = transport on readout tick; C1 null vacuous,POSITIVE,Y,PRE,N,Y,27 cells,roles/Ananke/pte/c1b/REVIEW_PACKET_PTE_C1b.txt
ANA-PTE-SI01,Ananke,PTE,semantic internalisation,09-25 20:06,HOLD,09-28 06:52,CLOSED for current champions,NULL,Y,PRE,N,Y,-,roles/Ananke/research/SYNTHESIS_2026-09-28_ARC3.md
ANA-W-A,Ananke,PTE M2,HOLD delay law,09-27 22:32,=frz,09-28 00:40,same three-line law,POSITIVE,Y,-,N,Y,~5 min,roles/Ananke/research/workers/W-A/REPORT.md
ANA-W-B,Ananke,PTE,SETRULE contribution,09-28,09-28,09-28 00:40,"bootstrap account holds, narrower",POSITIVE,?,-,N,Y,GPU lease,.../W-B/REPORT.md
ANA-W-C,Ananke,PTE vs Aether,timing vs content contrast,09-28,09-28,09-28 00:40,CONTRAST DOES NOT HOLD (design confound),INVALID,N,POST,N,N,4 threads,.../W-C/REPORT.md
ANA-W-D,Ananke,records,which interventions could not fire,09-28,09-28,09-27 22:38,case table (audit),POSITIVE,-,-,N,N,0 runs,.../W-D/REPORT.md
ANA-W-E,Ananke,PTE,retention regime exists,09-28,09-28,09-28 00:40,"NO, power limit predicted by C-POS",UNTESTABLE,Y,PRE,N,N,cpu8,.../W-E/REPORT.md
ANA-W-F,Ananke,PTE 166 cells,carrier census,09-28,09-28,09-28 00:40,census table,POSITIVE,Y,-,N,N,~80 min GPU,.../W-F/REPORT.md
ANA-W-G,Ananke,PTE,nontrivial retention,09-28,09-28,09-28 06:52,NO (replicated; controls valid),NULL,Y,-,N,Y,?,.../W-G/REPORT.md
ANA-W-H,Ananke,PTE,switching expands capacity,09-28,09-28 05:00,09-28 06:16,COMPRESSES not EXPANDS,NULL,Y,-,N,Y,~1.25 GPU-h,.../W-H/REPORT.md
ANA-W-I,Ananke,PTE 33 cells,carriers are places,09-28,09-28,09-28,carriers are trajectories,POSITIVE,Y,-,N,Y,cpu8,.../W-I/REPORT.md
ANA-W-J,Ananke,PTE,receiver operator shapes mechanisms,09-28,09-28,09-28,"conditionally, gain ~0.02",POSITIVE,Y,-,N,N,2 GPU leases,.../W-J/REPORT.md
ANA-W-K,Ananke,PTE fixtures,minimum reach evidence,09-28,09-28,09-28 05:48,no universal check; K2 J .70,POSITIVE,Y,-,N,Y,~25 min,.../W-K/REPORT.md
ANA-W-L,Ananke,PTE M2,retention reachable when rewarded,09-28,09-28,09-28 07:43,reachable as INTEGRATION; lag-2 unreached,POSITIVE,Y,-,N,Y,GPU,.../W-L/REPORT.md
ANA-W-M,Ananke,PTE,sum test detects mixture,09-29,09-29 03:35,09-29 04:51,single-trial swap census replaces sum test,POSITIVE,Y,-,N,Y,CPU,.../W-M/REPORT.md
ANA-W-N,Ananke,PTE,low-acc CHANCE is artifact,09-29,09-29 05:17,09-29 06:47,sample-size effect,POSITIVE,Y,-,N,Y,CPU,.../W-N/REPORT.md
ANA-W-O,Ananke,PTE 733 verdicts,recorded CHANCE verdicts hold,09-29,09-29 06:49,09-29 09:17,84% stay CHANCE; frozen proportions missed,NULL,?,-,N,Y,~2 h,.../W-O/REPORT.md
ANA-W-P,Ananke,PTE,N fraction is state gate,09-29,09-29 09:49,09-29 10:52,no support; joint carrier instead,NULL,Y,-,N,Y,~12 min,.../W-P/REPORT.md
ANA-W-Q,Ananke,stats,per-verdict attainability,09-29,09-29 11:13,09-29 11:46,certifies 42 transfers; not promoted,POSITIVE,Y,-,N,Y,CPU,.../W-Q/REPORT.md
ANA-W-R,Ananke,PTE sync,phase stratification matters,09-29,09-29 12:17,09-29 12:58,indexed by update-clock phase,POSITIVE,Y,-,N,Y,3 core-h,.../W-R/REPORT.md
ANA-W-S,Ananke,PTE,H1 state predictor,09-29,09-29 13:20,09-29 13:43,H1 NOT SUPPORTED,NULL,Y,-,N,Y,?,.../W-S/REPORT.md
ANA-W-T,Ananke,PTE,latency rule generalises,09-29,09-29 14:05,09-29 14:27,exact but reaches no new cell,NULL,Y,-,N,Y,0.9 core-h,.../W-T/REPORT.md
ANA-W-U,Ananke,stats,interval holds 1% FC,09-29,09-29 14:59,09-29 16:20,bootstrap holds to 32 pairs,POSITIVE,Y,-,N,Y,?,.../W-U/REPORT.md
ANA-W-V,Ananke,PTE MAJ,readout is majority,09-30,09-30 06:51,09-30 07:15,DISTRIBUTED-NONMAJ,NULL,Y,-,N,N,0.6 core-h,.../W-V/REPORT.md
ANA-W-W,Ananke,stats,hybrid interval promotable,09-30 09:19,09-30 09:22,09-30 10:34,promotable; held for check,POSITIVE,Y,-,N,Y,4.3 core-h,.../W-W/REPORT.md
ANA-W-X,Ananke,stats,H2 FC <= 1%,09-30,09-30 10:35,09-30 10:48,passes frozen rule; promoted,POSITIVE,Y,-,N,Y,0.17 core-h,.../W-X/REPORT.md
ANA-W-Y,Ananke,PTE,Kp[7] carries readout,09-30 11:09,09-30 11:14,09-30 11:28,known-answer Plant A failed,UNTESTABLE,Y,PRE,N,N,0.25 core-h,.../W-Y/REPORT.md
ANA-W-Z,Ananke,PTE 124 groups,swap_rel consistency >= 95%,09-30 11:49,09-30 11:52,09-30 12:51,92.7% < 95% bar,NULL,Y,-,N,Y,7.3 core-h,.../W-Z/REPORT.md
ANA-H-PLANT,Ananke,PTE plants,NULLs are physics vs search,09-30 23:46,09-30 23:48,-,running,OPEN,Y,-,N,N,cap 2 core-h,roles/Ananke/research/plans/H-PLANT_PLAN.md
ART-P11-FALSIF,Artemis,NPE z8 + toy ISA,P-11 certifies heredity,09-28 09:08,09-28,09-28 09:21,"P-11 certifies construction, not heredity (UNSOUND)",KILLED,Y,-,N,N,~70 s,roles/Artemis/challenge/p11/RESULT.md
ART-SI-MODEL,Artemis,register-machine sim,SI resource bounds,09-28 09:06,09-28 09:24,09-28 10:01,"broad N, narrow U",POSITIVE,Y,-,N,N,"4,445 CPU-s",roles/Artemis/challenge/si/RESULT.md
ART-FR101,Artemis,Archaeon C3-SFE-09 code,particle2 beats generic rules,09-28 09:04,09-28,09-28 09:11,shift rules each score 1.000,KILLED,N,POST,N,N,small,roles/Artemis/challenge/experiments/FR-101/RESULT.md
ART-SELFTEST,Artemis,fresh Claude workers,sharpening raises yield,09-28 13:37,09-28,09-29,not shown,NULL,Y,-,N,N,36 runs,roles/Artemis/selftest/RESULT.md
ART-CVTR-NESTOR,Artemis,NPE genomes,CVT-R on 3 donor sets,09-28 19:38,=frz,09-28 19:40,(c) 8/8 accepted; 19 P-11-certified fail,POSITIVE,Y,-,N,N,161 CPU-s,roles/Artemis/challenge/cvtr_nestor/RESULT.md
ODY-ART-S3,Odysseus+Artemis,Fabric v0.2,Fabric adoption gate,09-29 12:29,09-29 12:52,09-29 13:58,gate MET; 0.33 -> 0.67 recoded; ceiling ruler (Harmonia MAJOR),POSITIVE,Y,POST,Y,N,37 min,roles/Odysseus/fabric_pilot/s3/RESULT.md
ODY-S2,Odysseus,Fabric 18 verifiers,<=1 coordination action per exec,09-28 21:07,09-28 21:08,09-28 21:14,MET 0.28/exec,POSITIVE,Y,-,N,N,362 s,roles/Odysseus/fabric_pilot/s2/RESULT.md
ODY-EXPEDITION1,Odysseus,"BEE, Z80, NI",exploratory changes of mind,09-28 17:14,09-28 09:56,09-28,NI RETIRED; WSE reader FAILED,NULL,-,-,N,N,?,roles/Odysseus/expedition/EXPEDITION_1_REPORT.md
NYX-GZIP-001-002,Nyx,gzip 1.2.4 fossil,fast/lazy switch mechanism,09-16 17:23,-,09-16 18:33,Harmonia CHALLENGE: line 672 not 667,INVALID,Y,PRE,N,N,-,nyx/atlas/predictions/
NYX-GZIP-003,Nyx,gzip,"same, corrected",09-16 18:33,-,-,never run,PARKED,-,-,N,N,-,roles/Harmonia/journal/2026-09-17_m2-038758c6.md
NYX-PARTICLES-001,Nyx,particle filter fossil,ESS trigger boundary,09-17 15:22,09-17 15:28,09-17 15:33,INDETERMINATE (PC out of band),UNTESTABLE,Y,PRE,N,N,small,roles/Harmonia/rulings/RULING_PARTICLES_ESSTRIGGER_001_2026-09-17.md
NYX-PARTICLES-002,Nyx,"particle filter, 2 worlds",boundary + scheme ordering,09-17 15:48,09-17 22:22,09-17 22:29,CUT_SUPPORTED boundary; (c) FAILED,POSITIVE,Y,-,N,Y,?,roles/Harmonia/rulings/RULING_PARTICLES_ESSTRIGGER_002_2026-09-17.md
NYX-ASAL-001,Nyx,ASAL Lenia + CLIP,best crosser is metric exploit,09-18 06:13,09-18 06:18,09-18 06:28,CUT_SUPPORTED; narrowed by operator,POSITIVE,Y,-,Y,N,"1,045 rollouts",roles/Harmonia/rulings/RULING_ASAL_LEGIT_SEARCH_001_2026-09-18.md
NYX-POET-001,Nyx,POET fossil,estimator rows,09-19 ~10:09,09-30 10:42,09-30 10:43,"CUT_SUPPORTED, NOT confirmatory",POSITIVE,Y,-,Y,N,small,roles/Harmonia/rulings/RULING_MECH_POET_NOVELTY_ESTIMATOR_001_2026-09-30.md
NYX-AVIDA-001,Nyx,Avida ancestry,ancestry retention,09-30 11:13,-,-,awaiting adjudication,OPEN,Y,-,N,N,-,nyx/atlas/predictions/MECH-AVIDA-ANCESTRY-RETENTION-001.json
```
