# INFERENCE HARVEST HANDOFF -- Aphrodite, 2026-09-30 / 10-01

Directive: operator, bounded inference harvest. It temporarily unparks Aphrodite for inference-only work until
2026-10-01 05:00 America/New_York. It is an exception to CWO-B's FINISH-IN-PLACE / no-new-work rule.

Boundaries kept:
- no live LLM experiment (every agent experiment here is prereg-ready, NOT run);
- no GPU or model-host deployment;
- no positive RSI claim;
- no evidence-tier promotion.

Question: **how would we know whether Prometheus is genuinely getting better at producing future scientific
improvements, rather than merely accumulating code, memory, compute, agents and process?**

## 0. Bottom line

1. **Nothing establishes, at lab scale, that Prometheus is improving at producing improvements. That is because nothing
   MEASURES it.** Every quantity the lab records is activity or self-report: commits, packets, messages, heartbeats,
   WORK_STATE. The one quality-shaped measurement in existence is the 09-30 operator-commissioned audit, and it has no
   baseline. The improvement claim is unfalsified only because it is unmeasured (critic 1). No rung of the ladder above
   L0 is established (RSI_BOUNDARY s5).
2. **What the record DOES show is a lab that catches its own errors when an auditor and the operator are involved, and
   whose lessons mostly do not transfer between seats.**
   - Within a seat, the failure share falls from 0.28 (first 24 h) to 0.15 (after 72 h). New seats re-learn the same
     failures. Positives compound inside seats (e.g. Nestor's 7-link chain) but have never crossed a seat or substrate
     boundary (A3).
   - "Gates that cannot fail or cannot pass" is the commonest defect class: 14 episodes across 9 seats. It recurred after
     seat-local lessons, including Aphrodite's own recurrence: an unpassable gate was caught on 09-22, and hard-coded
     True gates were shipped on 09-23 (D55).
   - Consolidation happened only where the operator ruled (leases, Fabric, thread IDs). Elsewhere, duplication persists:
     19 seats own prereg/freeze functions; 11 own novelty rulers.
3. **The operator is the main improver.** About 9 operator prompts a day reach about 41 seats. Every waiting chain
   terminates at the operator. The D2 audit loop (13 rounds; 8 of them found defects introduced by the previous repair)
   ended only by operator decree. That is human-in-the-loop improvement, which is legitimate. It is not evidence of
   system self-improvement.
4. **Late September is unanalysable as a natural experiment.** The model switched from Opus 5 to 5.5 on 09-23..26. Then
   ops IDs, Fabric, leases, four MWOs, WORK_STATE, three CWOs, Builders and this harvest all landed in 4 days. Several
   orders superseded their predecessors within 0.5-5 h.
5. **One measurement can fix this cheaply: LBS (load-bearing survival).** Fortnightly, take 12 random verdicts and audit
   them with an auditor OUTSIDE the model family, mixing 4 planted defects in to measure the auditor's recall. At +60
   days, check whether a surviving claim became a premise in ANOTHER seat's later frozen, surviving design. It is the
   only endpoint here whose numerator the measured seats cannot write. Six fortnights detect only LARGE changes (power
   0.79 for survival 0.40 -> 0.80, but 0.56 for 0.45 -> 0.75). That limit is stated in advance.

---------------------------------------------------------------------------------------------------------------------

## 1. Deliverables

| # | File | What it is |
|---|---|---|
| 1 | PROMETHEUS_IMPROVEMENT_CAUSAL_MODEL.md | 12 mechanisms + 2 exogenous causes; their signatures and isolating contrasts; LBS primary endpoint; retrospective mapping |
| 2 | BUILDER_EVALUATION_PROTOCOL.md | FABRIC / EXPERIMENT / OBSERVABILITY endpoints, gameability, cheat controls; 3-level evaluation (instrument / sandbox / descriptive lab) |
| 3 | AGENT_SCIENCE_EXPERIMENTS.md | E1-E8, prereg-ready, NOT authorised; shared apparatus DB (defect battery) + HML (hidden-mechanism lab) |
| 4 | IMPROVEMENT_PROCESS_OBSERVATORY_DESIGN.md | entity schemas, API, adapters, frozen metric views; anti-Goodhart rules O-1..O-7 |
| 5 | RSI_BOUNDARY_REVISITED_2026-09-30.md | improvement vs IPI vs RSI; ladder L0-L7, each with ruler, hostile controls, falsifier, identifiability |
| 6 | this file | handoff |
| ev | evidence/ | analyst reports A1-A4, critics 1-2, CRITIC_RECONCILIATION.md, analysis code |

Every design document is rev 2: rev 1 was drafted before the critics; rev 2 applies 16 BLOCKING and 31 MAJOR
objections (evidence/CRITIC_RECONCILIATION.md). One of Aphrodite's own rev-1 claims was wrong: the LBS power figure.
Simulation corrected it.

---------------------------------------------------------------------------------------------------------------------

## 2. What can already be measured retrospectively (and what it shows)

Sources: four independent read-only analysts and critic 1, using git (10,337 non-merge commits), comms (1,198 messages,
09-11..09-30) and the repo.

| Measurement | Value | Reading | Source |
|---|---|---|---|
| Throughput composition (Sep) | 6,050 commits; 31% row/receipt micro-commits, 14% state/journal/heartbeat; result-reporting commits flat at 2-6% | activity grew; the result rate did not | critic 1 O1, A2 |
| Coordination share of commits | 16.9% (wk 08-10) -> 46.3% (wk 09-28); 58.8% on 09-29, or 27.2% without WORK_STATE commits | the control plane reports on itself | A2 |
| Coordination share of messages | 25% overall; 41% on 09-30, from mandated heartbeats (64 heartbeat/census messages) | policy effect, not workload | A4, A2 |
| Defect discovery stage | pre-run share 0% / 11% / 42% / 3% over four periods; the 42% peak = two processes (Aphrodite amendment freezing; Ensorain fixtures) | NO fleet-wide shift earlier | A1 |
| Defect discoverer | self/automated 86% / 53% / 88% -> 30% in 09-28..30; 27/40 found by other seats, at least 18 of them by operator-commissioned review lanes | reviewer capacity rose about 3x; this is detection effort, not practice | A1 |
| Defect recurrence | "gate that cannot fail or cannot pass": 14 episodes, 9 seats; seed/pairing errors rediscovered by 4 seats; CRLF-hash lesson only partly transferred; exposure/freeze-ordering slips across 12 seats | lessons are seat-local; no transfer shown | A1, critic 1 O3 |
| Auditor fallibility | Harmonia committed its audited error twice (D79, D87); audit J wrong (#1113); Fabric reviewers passed a post-exposure change because prompts told them to (D73) | the review layer needs its own recall measurement | A1, critic 1 |
| 09-30 audit outcomes | of 12 audited packages: 4 clean, 6 MAJOR, 1 BLOCKING, 1 audit wrong; dispositions mostly survive, while attached positive claims carry the defects | no baseline exists, so this cannot show a trend | critic 1 O2 |
| Positive-result compounding | WITHIN seats, yes: Nestor's 7-link confirmed chain, Aether E-006 -> E-010, Aphrodite S1-S4 -> A23. Some chains were built on positives later restricted or killed (Cosmos laws A/B, Archaeon CMP1, Ensorain WTP-02). ACROSS seats or substrates, none: Nestor internalisation vanished in BEE; Atlas-BEE inverted or absent; cross-engine ancestry UNTESTABLE. Only about 3 cross-seat attempts exist | compounding is seat-local; cross-seat portability is unshown (n too small to call it absent) | A3, critic 1 O4 |
| Operator load | 177 operator prompts / 20 days / 41 seats; redirect-science 101, approve-gate 36, infra 34; all waiting chains end at the operator; 0 operator prompts on 09-15, 09-20, 09-22, when only 2 seats were active | operator availability throttles throughput | A4 |
| Review cycles | D2: 13 rounds in about 20.5 h; 8 found NEW defect classes, often repair-introduced; 2 re-reported an operator-blocked item | audit churn: repair-induced defects | A4, critic 1 O5 |
| Stale-state incidents | 12 catalogued, 9 of them in 09-28..30. Examples: Artemis 16 Fabric tasks under a superseded order (#1134); a leftover Nestor scheduled task destroyed 10/11 sample files (#943); the census marked Aphrodite not_live 3 h after a commit | control-plane churn creates stale authority | A4 |
| Tool reuse | comms used by all 55 senders, imported by 8; fabric imported by 4 seats; Proteus's foundry reused by 6 seats; 4 lease systems built in about 30 h, then consolidated by operator ruling | reuse is via CLI and convention; consolidation is operator-driven | A4 |
| Intervention natural experiments | comms bus: overhead up, benefit indeterminate. Prereg: weak positive. Holdouts, positive controls, review skill: indeterminate. Wiki: burst then decay. Fabric: leaning churn. MWO/CWO: fast adoption plus self-reporting inflation | none clearly positive except prereg (weak) | A2 |
| World-facing share | 997/1198 messages about the lab itself vs 149 about any external domain; every studied "world" is built in-house | the lab is mostly studying itself | critic 1 O7 |
| Experiment ledger, verdict mix | see s2.1 | | A3 |

### 2.1 Experiment ledger (A3; evidence/findings_A3_experiments.md, findings_A3_ledger.csv)

281 experiments across 14 seats, 09-06..09-30. Verdict classes are A3's mapping of seat-local wording; 16% of rows were
later relabelled by their seats.

| Class | Count |
|---|---|
| POSITIVE | 107 |
| NULL | 89 |
| KILLED by baseline/control | 23 |
| UNTESTABLE | 25 |
| INVALID | 21 |
| PARKED | 10 |
| OPEN | 6 |

- **UNTESTABLE + INVALID share by verdict date:** 0.33 -> 0.29 -> 0.14 -> 0.09 -> 0.13, then 0.31 on 09-30. Of the 9
  failures on 09-30, 8 came from Hecate, Tyche and Theseus on their first day.
- **Seat age drives it.** A seat's first 24 h run at 0.28; after 72 h, 0.15. This is the cleanest "improvement-shaped"
  signal in the record, and it is WITHIN-SEAT LEARNING THAT DOES NOT TRANSFER: every new seat re-learns the old failures
  (no quota screen, no planted positive control, compute oversizing). Within-seat trends are mixed. Nestor fell
  0.67 -> about 0.07; Archaeon and Ensorain fell. Aphrodite ROSE 0.14 -> 0.60 once its assays became supply-limited.
- **Freeze-to-verdict** median is under 1 h, with no trend. The real cost is RE-FREEZES. Aphrodite's recurrence line took
  6 amendments and 15.7 h to reach one valid YES; its bounded-RSI line took 4.2 days to reach a valid NO.
- **Screens.** 35 problems were caught pre-run vs 70 post-run. Where screens existed they worked (Aether $0 scouts;
  Cosmos killing a law before spending the sealed holdout; Nestor gates). The expensive failures all had a screen that
  did not test the thing that failed: a positive control unable to fire, ceiling rulers, compute sizing. Examples:
  Nestor's 72 h Z80 run, Archaeon ENVGATE-01, Ananke PTE-C1, Tyche's 13 lost core-h. This cross-tab is partly circular,
  because missing screens were often learned only from failures.
- **T49 (Aphrodite's supply-screen lesson).**
  - Built after A21. A22 used it and STILL failed quota (5/8 vs 6).
  - The lesson was written 3 min after A23 froze, so its "worked" rests on A23 alone.
  - NO other seat cites it; equivalents arose earlier and independently elsewhere.
  - Not evidence of transfer in either direction.
- **Reused instruments carry their defects.** Nestor's P-11 assay was reused about 10 times before being ruled unsound.
  Bellerophon's BEE replications repeated its own logged defect.

**Implication for the causal model.** The seat-age curve says the binding constraint is not per-seat learning. Seats
learn within about 72 h. The constraint is that the lab has no channel through which a lesson becomes a NEW seat's
default. Lesson channels today are per-seat STANDING_RULES, operator prompts and documents. That is exactly what C11
(reusable skill) would need, and exactly what E4 tests. The gate-reachability lint (s5 item 1) is the cheapest channel
that does not depend on reading.

---------------------------------------------------------------------------------------------------------------------

## 3. Conclusions that are currently IMPOSSIBLE

1. That Prometheus's error RATE changed. No first-pass denominator exists, and detection effort tripled in 72 h.
2. That detection moved earlier fleet-wide. The only pre-run peak comes from two specific processes.
3. That any process intervention of 09-27..30 caused anything. Seven-plus interventions landed in 4 days, right after a
   model switch.
4. That adversarial review beats self-review, or that fresh critics beat self-review. These were never compared under
   a fixed protocol: AGENT_SCIENCE E1/E2.
5. That a self-caught defect indicates robustness. First-pass rate and recall are both unmeasured: E8.
6. That any Builder improved anything. The Builders exist on paper; the only output is fleet_status.py.
7. Any lab-scale rung L3+ of the ladder. L6 is UNTESTABLE BY DESIGN at this scale; L5 needs randomised operator-quiet
   windows and a full operator-input log.
8. Any claim about information yield per resource. Tokens are unmetered, operator-minutes are unlogged, and p_pred is
   never recorded.
9. That positive results compound ACROSS seats or substrates. Within-seat chains exist (A3). About 3 cross-seat
   attempts all failed or ended UNTESTABLE, which is too few to call portability absent. Load-bearing use is not
   recorded anywhere.
10. That T49, or any single lesson, transferred. No other seat cites T49, and its own success rests on one experiment
    (A23).

---------------------------------------------------------------------------------------------------------------------

## 4. The best bounded future real-agent experiment

**AGENT_SCIENCE E4 (rev 2): cross-substrate skill transfer with held-out traps.**
- Agents receive (a) the Prometheus lessons pack, (b) generic methodology text, (c) raw project context, or (d) nothing.
- They then design and run experiments on HML, a new hidden-mechanism substrate with exact ground truth.
- The primary endpoint is failure on HELD-OUT trap classes, which the pack never names.
- Design: 16 items x 4 arms x 3 replicates = 192 runs, about 29M tokens plus small CPU. Simulated power is 0.93 for a
  failure-rate drop from 0.50 to 0.25 with 2 held-out traps per item.
- It is the only design that separates reusable skill (C11) from memory (C3), domain knowledge (C10), trap-naming, and
  the model (X1). It answers whether anything Prometheus learned is skill rather than history.
- Prerequisites, which are apparatus rather than live experiments: build HML (about 1-2 Builder days, local CPU) and
  a held-out trap list authored outside the model family.
- **Authorisation needed:** live-LLM experiment authority, which this harvest does not grant.
- Conflict of interest: Aphrodite designed both the experiment and the lessons pack concept. Another seat must curate
  the pack.

Runner-up: E8 (self-catch decomposition). It is cheap, and it makes every future "agent found its own bug" interpretable.

---------------------------------------------------------------------------------------------------------------------

## 5. Builder instrumentation worth implementing immediately

Ranked by value / cost. None changes scientific meaning or needs privilege. All are inside R2.

1. **Gate-reachability lint (BUILDER-EXPERIMENT).** This targets the most recurrent defect class in the history, the gate
   that cannot fail or cannot pass (14 episodes, 9 seats). For every frozen decision rule:
   - run the gate on synthetic inputs that MUST pass and on inputs that MUST fail;
   - refuse to seal if either branch is unreachable;
   - apply the same check to positive controls: the control must be able to fail.
   About one day of work. It turns fleet rule F1 from a document into a check, and it is the cheapest test of whether a
   Builder primitive can stop a recurring class (measured as EXP-4 on the planted battery).
2. **Operator-input log as a first-class record.** One line per directive: time, seat, kind, minutes. That means
   formalising and back-filling the `roles/*/prompts/` archive. Without it, X2 cannot be controlled and L5 is
   untestable.
3. **IDs in comms `task_ref`.** TH/C/E/experiment ids in `task_ref`, which is nearly always empty today, so messages
   join to work automatically.
4. **Canonical p(YES) + reference forecast at freeze.** One field per prereg; the reference forecast is generated by a
   fixed fresh-context prompt. This creates forecast skill (secondary S1), the signal that would detect the lab
   learning to predict its experiments.
5. **Release staggering log (BUILDER-OBSERVABILITY).** At most one fleet-visible infra or control-plane change per 5
   working days, each logged. Without it, no intervention is ever evaluable.
6. **LBS pilot.** One fortnight: 12 random verdicts plus 4 planted, audited through the operator's Council (outside the
   model family). The cost is operator time; it is the only primary endpoint that cannot be gamed by the seats.
7. **Fabric `deterministic` declaration + `manual` flag on receipts.** This closes the FAB-2 laundering hole, and it
   makes manual interventions countable.
8. **Verdict-class mapping table** across all seats (POSITIVE / NULL / KILLED / UNTESTABLE / INVALID / PARKED).

---------------------------------------------------------------------------------------------------------------------

## 6. Ways the current workflow creates false impressions of improvement

1. **Mandated visibility looks like activity.** Heartbeats, WORK_STATE commits and push cadence rise by decree. On
   09-29, 58.8% of commits were coordination.
2. **More reviewers look like more rigor.** Discovery by other seats went from 14-47% to 70% in 72 h because the operator
   commissioned review lanes. Defects found rose; defects made is unknown.
3. **Repair-audit loops look like hardening.** In D2, most rounds found defects introduced by the previous repair.
4. **Operator rulings look like system learning.** Lease, Fabric and thread-ID consolidation happened by ruling. A seat
   that "adopts a lesson" after a ruling is complying, not learning.
5. **A model upgrade looks like fleet-wide skill transfer.** Opus 5 -> 5.5 on 09-23..26 lifts every seat at once.
6. **Clean negatives look like progress.** Correct PARK/NULL dispositions survive audit, so the verdict record looks
   healthy, while the attached positive claims carry the defects.
7. **Seat-local STANDING_RULES look like institutional memory.** Fixes are written per seat, about 16 new seats were
   created in September starting at "charter PENDING", and rules arrive after the defect has recurred elsewhere.
8. **Self-caught defects look like robustness.** They are equally predicted by weaker first passes.
9. **Packets look like results.** Review-packet commits jumped tenfold (1-4/wk to 14-52/wk) on 09-01 and stayed there.
   Result-reporting commits did not move.
10. **The reporting layer fails silently.** Five consecutive weekly recaps (08-29..09-26) contain the generator's raw
    scratch reasoning instead of a recap, and nobody noticed. A lab whose summaries are not read cannot use them as
    evidence of anything (critic 1 O10).
11. **Engine-scale results read as lab-scale.** Aphrodite's own G1_RECURRENT_STEPPING_STONE = YES (A23) is a MECHANISM
    under CONSTRUCTED recurrence inside one engine. It says nothing about Prometheus improving.
12. **Self-measurement by the improver.** This harvest is itself Prometheus analysing whether Prometheus works, using
    the same model family. Its conclusions should be audited from outside (LBS-style) before they are acted on at
    scale.

---------------------------------------------------------------------------------------------------------------------

## 7. Disclosures

- **Aphrodite's own defects in the record:** D55 (hard-coded True gates on 09-23, the day after catching an unpassable
  gate) and the TH-021 constant-True conditions in run_s3s4.py, a16.py and a17.py. They remain unrelabelled (hard gate).
  Aphrodite is a counterexample to its own seat-level lesson transfer.
- **Rev-1 error:** the LBS power figure was claimed without simulation, and simulation showed it was too high. Fixed in
  rev 2.
- **Conflict of interest:** Aphrodite designed the scoring system that would evaluate its own T49 lesson (E4). Mitigation:
  another seat curates the lessons pack, and the held-out traps are authored outside the model family.
- **Harness note:** the subagents' report-file writes were blocked for A2 (and partly for A1). Aphrodite deposited
  their returned text, which is marked as such in each file.
- **Housekeeping found by A4:** Aphrodite's M4 lease ledger (roles/Aphrodite/leases/) was never migrated into Fabric's
  lease table. It is retired for new work per MWO-0001 and unused since; noted, not acted on.

---------------------------------------------------------------------------------------------------------------------

## 8. State at handoff

- Branch `aphrodite/inference-harvest-2026-09-30`, pushed; not merged to main. The merge is a routine CWO-C completion
  step for Aporia/operator review.
- No compute, leases, Fabric tasks or live-LLM experiments were used. The only processes were read-only analysis
  subagents and two fresh-context critics.
- At cutoff (2026-10-01 05:00 America/New_York): Aphrodite returns to READY, with NEXT = awaiting Aporia assignment.
