# CRITIC RECONCILIATION -- inference harvest, 2026-09-30

Two fresh-context Opus critics. Neither saw Aphrodite's reasoning or preferred conclusion.
- Critic 1 attacked "Prometheus is improving at all" (`critic1_improving_at_all.md`). It saw no drafts.
- Critic 2 attacked the rev-1 measurement system for Goodhart and gameability (`critic2_goodhart.md`). It found
  16 BLOCKING, 31 MAJOR and about 13 MINOR objections.

Abbreviations: CM = causal model, RB = RSI boundary, BP = Builder protocol, AS = agent-science experiments,
OB = Observatory design.

Dispositions: FIXED means the text was changed (location given). PARTIAL means it was mitigated, with the residual
disclosed. ACCEPTED means no fix exists at this scale; it is disclosed. REJECTED means the objection was disagreed with,
for the reason given.

## Critic 2 -- BLOCKING (16)

| ID | Objection (short) | Disposition | Where / how |
|---|---|---|---|
| A1 | surprisal against the lab's own improving forecasts PENALISES learning | FIXED | CM s1.2 S1: forecast skill against a FIXED reference forecaster becomes a positive secondary endpoint; surprisal demoted to exploratory, with a fixed reference |
| A2 | seats choose the outcome set, which inflates surprisal | FIXED | CM s1.2/s1.3: one canonical binary outcome from the frozen primary decision rule |
| A3 | surprisal rewards underpowered NULLs and false positives; no retraction penalty | FIXED | CM s1.3: NULL needs power >= 0.8; retraction reverses credit and credits the finder |
| A7 | consumption manufactured by citation or self-consumption | FIXED | CM s1.1 step 3, OB s2.10: LOAD-BEARING only = a DIFFERENT seat's FROZEN design uses it, that design survives the audit, and the external auditor judges |
| B1 | the seat's own difficulty forecast is the matched-difficulty control | FIXED | CM s1.2 (reference forecaster); OB O-6: seat forecasts are SEAT_ASSERTED and never the control. L1 is measured by frozen-battery replay (RB L1a), which needs no difficulty forecast |
| C3 | operator-minutes fall by decree (MWO-0004 R1) or by seats not escalating | FIXED | CM s1.2 S4: VOID under escalation-reducing policies; always paired with the late-defect rate S3 |
| D1 | E4 traps map one-to-one onto the lessons pack, which makes it a naming test | FIXED | AS E4 rev 2: primary on HELD-OUT trap classes authored outside the model family; named traps are a manipulation check |
| E1 | Builders patch shared infra, so per-seat wedging is impossible and conflicts with MWO-0004 | FIXED (by withdrawal) | BP P7 rev 2: the wedge is withdrawn. Three levels instead: instrument (planted), mechanism (sandbox AS E3/E5), lab (descriptive ITS) |
| E3 | wedge power about 10-15%; an underpowered NULL is uninterpretable | FIXED | as E1. All power claims are now simulated, with tables in CM s1.1 and AS E4. Rev 1's own power claim (0.8 at 0.45->0.75) was WRONG: simulation gives 0.56 |
| F1 | the origin audit cannot see operator prompts typed into sessions | PARTIAL | OB s2.12: roles/*/prompts (about 378 dirs in Sep) are coded; default = OPERATOR when unclear. Residual: prompts not saved to disk are invisible |
| G1 | log(payoff/cost) undefined for zero or negative payoff, which causes survivorship | FIXED | RB L4, CM s5: net payoff, with all events included |
| G2 | overlapping fleet changes make single-improvement payoff unidentifiable | PARTIAL | RB L4: estimable only under STAGGERED releases (>= 5 working days apart); otherwise UNTESTABLE. This needs operator/Aporia scheduling discipline |
| G5 | L5 unidentifiable with one operator; quiet windows are chosen, and queues are written under orders | PARTIAL | RB L5: requires a full operator-input log AND randomised quiet windows from a pre-published seed; nodes autonomous only if designed after the window opened. Otherwise UNTESTABLE |
| G6 | L6 knockouts and sham lineages cannot be run at lab scale | ACCEPTED | RB L6: declared UNTESTABLE BY DESIGN at lab scale; testable only at engine scale or in sandbox populations |
| H1 | about 40 metrics read by a motivated reader | FIXED | CM s1.1-1.3, OB s5: ONE primary (LBS), 4 gatekept secondaries, everything else descriptive or exploratory; fixed fortnightly cadence; all rows always shown |
| H5 | FAB-2 retry rule launders science failures as INFRA | FIXED | BP FAB-2: only declared-deterministic tasks with a reproduced hash; every science retry listed in the packet |
| I1 | no external validity: the whole apparatus is one model family | PARTIAL | the LBS auditor is outside the model family (the operator's Council, or human); planted batteries are 40%+ authored outside it; OB O-7 reports world-facing share and outside-auditor share. Residual: Council use costs operator time |

## Critic 2 -- MAJOR (31)

| ID | Disposition | Note |
|---|---|---|
| A4 salami slicing | FIXED | CM s1.3: one run = one unit |
| A5 isotonic per seat on about 10 points | FIXED | removed; fixed reference forecaster instead |
| A6 reviewer recall unmeasured; independence rule undefined | FIXED | LBS planted recall >= 3/4 per round, else the round is void |
| A8 consumption right-censored, visibility-biased | PARTIAL | fixed 60-day follow-up; quiet-seat bias disclosed |
| A9 prereg count becomes the activity metric | FIXED | prereg counts appear nowhere as endpoints (CM s1) |
| C1 a cost vector lets readers pick a component | FIXED | primary is LBS per fortnight; per-component cost exploratory only |
| C2 cost shifts to unmetered resources | ACCEPTED | disclosed; token metering via harness usage is an Observatory adapter (OB s4) |
| D2 same-model batteries | PARTIAL | 40%+ outside the model family (BP EXP-4) |
| D3 sealed custody unenforceable on shared hosts (#1128) | ACCEPTED | disclosed; batteries rotate |
| D4 recognisable canaries | FIXED | BP FAB-1b: randomised canary generator |
| D5 planted staleness in a real seat | FIXED | BP OBS-1: synthetic canary seat only |
| D6 fighting the last war | FIXED | BP EXP-4: 40%+ novel classes |
| E2 interference between wedge arms | MOOT | wedge withdrawn |
| E4 calendar confound; arm awareness | MOOT for the wedge | the ITS is labelled descriptive |
| E5 no-op sham detectable and erodes trust | FIXED | dropped at lab scale; sandbox only (RB L2, BP) |
| E7 Builders build their own scorers; Aphrodite scores her own T49 | FIXED / DISCLOSED | Builders never compute endpoints (BP P2); the E4 lessons pack is curated by another seat; this conflict of interest is disclosed in the handoff |
| F2 origin trailer self-declared; CWO authorship ambiguous | FIXED | OB: OPERATOR_RELAYED_BY_SEAT class; trailer is SEAT_ASSERTED |
| F3 rewarding autonomy invites withholding operator input | PARTIAL | autonomy is not an endpoint at all below L5; operator input is never penalised in LBS. Disclosed |
| G3 generation inflation via cited parents | FIXED | RB L4: a parent counts only if the child's frozen design uses its output |
| G4 diminishing-returns null unconstrained at N = 3-5 | ACCEPTED | L4 is UNTESTABLE at current N without staggered releases |
| G7 L4-L6 outlast a model version | ACCEPTED | disclosed in RB L6; model-switch event study for L4 |
| G8 no fixed task family in real research | FIXED | RB L1(a): a frozen battery replay under a pinned model |
| G9 better rulers punished | FIXED | RB L2: a ruler validated on the planted battery that wins is itself an L2 event |
| H2 seats on one model are non-independent; pseudo-replication | FIXED | AS E4: item is the unit; replicates averaged |
| H3 E4 run count inconsistent | FIXED | AS E4: 16 x 4 x 3 = 192 runs; power simulated (0.93 at 2 held-out traps per item) |
| H4 minimum-scale kill audit confirms false kills | FIXED | BP EXP-1b: designed scale |
| H6 model-coded fields steerable by phrasing | PARTIAL | primary uses no model-coded fields; secondaries require 2-coder agreement >= 0.8; disclosed |
| H7 first-mention clock discourages early communication | PARTIAL | EXP-2 is a descriptive secondary only; disclosed |
| I2 VIU excludes questions, instruments, retractions, diagnosed-UNTESTABLE | PARTIAL | LBS samples include diagnosed-UNTESTABLE; retractions credit the finder; instruments are credited as L2 events. New questions remain uncredited (disclosed) |
| I3 better selection subtracted | FIXED | CM s4: selection is credited as portfolio improvement, labelled |
| I4 North Star conflated with RSI | FIXED | CM s4: HITL improvement is legitimate; X2/C8 only block the word "recursive" |

MINOR K1-K6 are FIXED where they are textual. K6 (lane authority): CWO-2026-09-30C is the current operator order and
names Aporia as dispatcher, so the authority field on episodes uses the CWO id, not the seat.

## Critic 1 -- disposition of its findings

Critic 1's findings are evidence, not design objections. They are adopted into the handoff (s2) as retrospective
evidence, cross-checked against the independent analysts A1-A4.

Its three demanded measurements are all adopted:
- (a) a fixed fortnightly audit of randomly sampled claims, by an outsider, with planted defects = LBS steps 1-2;
- (b) a frozen battery replayed under a pinned model = RB L1(a);
- (c) results that become load-bearing inputs to another seat's later surviving verdict, per operator-hour = LBS
  step 3.

One correction to critic 1's own numbers: it counted 6,050 September commits. The brief's figure of 6,954 was an
artefact of multi-line subjects and UTC/local date bucketing, and A2 independently found 6,050. Critic 1's figure
stands.

## What the reconciliation did NOT change

- The ladder's structure (L0-L7) and the causal decomposition (C1-C12, X1-X2). Neither critic disputed them. Critic 2
  disputed their measurability, which is now stated per rung.
- The verdict that no rung above L0 is established at lab scale. Both critics independently support it.
