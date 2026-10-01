# BUILDER EVALUATION PROTOCOL

Seat: Aphrodite (inference harvest 2026-09-30). Tier 1-3: a prereg-ready design. Nothing here is running, and nothing
here authorises a Builder lane. Lane status is set by Aporia/CWO: on 2026-09-30, BUILDER-OBSERVABILITY = STARTED
(`ops/fleet/fleet_status.py`); BUILDER-FABRIC and BUILDER-EXPERIMENT = SUSPENDED (CWO-B s7).

Builders are defined in `ops/fleet/CWO_2026-09-30_FLEET_ACTIVATION.md` s2: "make the ecosystem better while the
scientists use it", with no scientific authority. Their output is infrastructure, so their value is only visible
DOWNSTREAM. That is the whole design problem.

---------------------------------------------------------------------------------------------------------------------

## 0. Principles (binding on every endpoint below)

P1. **The primary endpoint is downstream payoff on work the Builder was NOT commissioned for.** A Builder that fixes
    the experiment that motivated it has done a repair. It has not improved the lab (causal model, rung L2).
P2. **Builders never compute their own endpoints.** The Observatory computes them from raw receipts, and a
    non-Builder seat audits a sample.
P3. **Every "more is better" metric is paired with a "cost or false" metric.** Neither half is reported alone.
P4. **Planted batteries are sealed.** Canary tasks, planted defects and planted staleness are generated, hashed and
    held under holdout custody. The Builder never sees them, and neither does any seat whose output they score.
P5. **Mandate voiding.** A metric that a work order MANDATES (heartbeats, push cadence, receipts) cannot count as
    evidence of improvement in the window where the mandate takes effect. The mandate moved it, not the Builder.
P6. **Endpoint definitions are frozen before the lane runs** (the same prereg discipline as science). Each Builder lane
    gets an evaluation manifest with a hash, recorded in the Observatory.
P7. **(rev 2) Lab-level causal attribution of a Builder is NOT available at this scale. Say so; do not fake it.**
    Rev 1 proposed a seat-level stepped wedge. Critic 2 (E1/E3) showed it is infeasible:
    - Builders patch SHARED infrastructure on main, so their fixes cannot be withheld per seat.
    - Withholding a fix from control seats conflicts with MWO-0004.
    - With 4 seats x 72h x about 25 verdicts, power is about 10-15%.
    Rev 2 evaluates each Builder at three levels, each labelled with what it can and cannot show:
    (i)  **instrument level (causal, cheap):** planted batteries and canaries (FAB-1b, EXP-4, OBS-1). These show the
         instrument works. They do not show the lab improved.
    (ii) **mechanism level (causal, in a sandbox):** AGENT_SCIENCE E3 (primitives) and E5 (Builder generalisation) on
         HML. These show the KIND of Builder output helps agents on unseen tasks.
    (iii) **lab level (descriptive only):** an interrupted time series of LBS and secondaries around each Builder
         release.
         - Releases are STAGGERED: at most one fleet-visible infrastructure change per 5 working days, logged in the
           Observatory (findings_A2 item 15). Where releases overlap, the window is labelled CONFOUNDED.
         - Lab-level claims are reported as "consistent with / not consistent with", never as "caused".

---------------------------------------------------------------------------------------------------------------------

## 1. BUILDER-FABRIC

Scope: the execution layer, i.e. leases, workers, sandboxing, receipts and recovery (CWO s2).

### Primary endpoint
**FAB-1 Manual interventions per 100 completed Fabric tasks**, at a fixed canary workload.
- Definition: any human (operator) or seat action that is not a task submission or a result read, and that was needed to
  get a task to a terminal state. Examples: restarting a worker, clearing a disk, re-submitting after a silent drop,
  hand-editing a lease.
- Source: a Fabric receipt flag `manual=true`, cross-checked automatically against comms (messages naming a task id plus
  a repair verb) and against git (commits touching fabric/ state within 30 min of a task failure).
- Paired with: **FAB-1b canary success rate.** Canaries are drawn from a sealed generator, not a fixed set of 10 (critic
  2, D4). The generator randomises requirements, sizes and submit times, and draws its shapes from the real task
  distribution, so that canaries are not recognisable. Their expected outputs are hashed. If interventions fall but canaries also fail silently more often, the Builder has hidden
  failures, not removed them.

### Secondary endpoints

| ID | Endpoint | Auto? | Gameable how | Cheat control |
|---|---|---|---|---|
| FAB-2 | infra-attributable failure fraction | yes | relabel infra failures as "science"; OR (critic 2, H5) rerun a nondeterministic science task until it passes and file the failure as INFRA | **(rev 2)** the retry rule applies ONLY to tasks declared deterministic at submission (fixed seeds; output hash expected identical) AND whose retry reproduces the declared hash. Nondeterministic failures are never auto-INFRA. EVERY retry of a science task is listed in that experiment's evidence packet. A blind auditor labels a 10% sample |
| FAB-3 | submit-to-start latency, p50 / p95, and its variance | yes | prioritise canaries; drop slow jobs | canaries are indistinguishable from ordinary jobs (P4); dropped jobs count as infinite latency |
| FAB-4 | recurrence of a "fixed" failure class within 14 days | yes | re-signature the same failure | failure signatures frozen in the manifest (normalised exit code + stack-frame cluster); new signatures are clustered against old ones by an auditor |
| FAB-5 | silent-acceptance rate (accepted tasks with no eligible worker; #916/#953) | yes via canaries | refuse everything | paired with FAB-1b and a false-refusal audit |
| FAB-6 | reproducibility: bit-identical or within-tolerance rerun of a 2% random sample of completed tasks | yes | exclude nondeterministic tasks | the sample is drawn by the Observatory, not the Builder |

### Downstream (P1) test (rev 2)
- Descriptive interrupted time series (P7 iii) of Fabric-using seats' INFRA-attributed INVALID/UNTESTABLE rate and
  time-to-verdict.
- Odysseus is the commissioning customer, so Odysseus's tasks are EXCLUDED from the primary series and reported
  separately.

---------------------------------------------------------------------------------------------------------------------

## 2. BUILDER-EXPERIMENT

Scope: reusable experimental primitives, i.e. prereg manifest, frozen config, seeds, baseline/positive-control
declarations, falsifier hooks, run receipts and evidence packets (CWO s2).

### Primary endpoint
**EXP-1 Post-run INVALID + UNTESTABLE fraction on experiments run by seats OTHER than the primitives' commissioning
seat(s)** (descriptive at lab level; causal reading via AGENT_SCIENCE E3; P7).
- Rationale: in the history, the dominant expensive failure modes are design and supply failures discovered AFTER the
  run (Aphrodite A20-A22: UNTESTABLE, INVALID_DESIGN_DEFECT, UNTESTABLE). A primitive that moves these failures
  before the run, or removes them, has real value.
- Paired with: **EXP-1b false-kill rate.** Pre-run kills are audited by running a random 20% of killed designs anyway at
  their DESIGNED scale. At minimum scale, a false kill would be "confirmed" by underpowering (critic 2, H4). Each kill
  states its avoided cost, and the kill is credited only up to that cost (critic 2, K2).
- (rev 2) EXP-1 at lab level is DESCRIPTIVE (P7 iii). The causal reading of EXP-1 is AGENT_SCIENCE E3.

### Secondary endpoints

| ID | Endpoint | Auto? | Gameable how | Cheat control |
|---|---|---|---|---|
| EXP-2 | setup effort: tokens and wall-clock from frozen hypothesis text to sealed launch | yes (manifest timestamps, token meters) | freeze later (do design work before the clock starts) | the clock starts at the FIRST commit or message naming the hypothesis id, not at the manifest |
| EXP-3 | pre-run kill fraction by declared controls (positive control fails, supply screen fails) | yes | controls that always fail | paired with EXP-1b |
| EXP-4 | **planted-defect catch rate** before run | semi | learn the battery; "fight the last war" (critic 2, D6) | (rev 2) at least 40% of items come from defect classes ABSENT from the historical catalog, authored by a DIFFERENT model family or by the operator (D2). Difficulty is anchored by repeating 5 items each rotation. The sealed battery (P4) of preregs is seeded with historical defect classes: constant-True gate (TH-021), missing equal-expressivity sham, holdout leakage, supply quota unreachable, ruler false positive. New battery items are drawn each quarter. Item classes come from the real defect catalog (`evidence/`) |
| EXP-5 | provenance completeness: can a FRESH-context agent regenerate the result table from receipts alone? | yes (scheduled agent) | over-document trivial runs | random sample; pass/fail on exact table reproduction |
| EXP-6 | non-trivial cross-seat reuse of primitives | semi | trivial imports to inflate reuse | count a use only if the primitive's output enters a sealed run's receipt (its hash is in the receipt) |
| EXP-7 | time to falsification: freeze to first decisive evidence against the hypothesis | yes | pick hypotheses that die fast | a difficulty forecast is recorded at freeze (P6); compared at matched forecast |
| EXP-8 | method transfer to a new engine: hours to bring a new engine under primitives, so that its first experiment passes EXP-4 | manual | choose easy engines | the engine is chosen by a third party; the comparison arm uses an engine that is not onboarded |

### Downstream (P1) test (rev 2)
- Causal reading: AGENT_SCIENCE E3 (primitives vs sham library vs docs-only, on HML).
- Lab reading: a descriptive time series (P7 iii), excluding the commissioning seat(s).
- The rev-1 stepped wedge is withdrawn: it was infeasible and had about 10-15% power (critic 2, E1/E3).

---------------------------------------------------------------------------------------------------------------------

## 3. BUILDER-OBSERVABILITY

Scope: fleet legibility, i.e. work-order adoption, queues, last receipt, blockers, stale state (CWO s2). It is seeded by
`ops/fleet/fleet_status.py` (STALE_MWO / STALE_UPDATE / NO_QUEUE / IDLE_HOLD / IDLE_WORKERS).

### Primary endpoint
**OBS-1 Detection recall and latency on planted staleness**, at a bounded false-alarm rate.
- (rev 2) A SYNTHETIC canary seat only. Using real seats is excluded, because it is not blind and it can mislead the
  seats that read their state (critic 2, D5). The canary seat is made stale on a randomised schedule unknown to the
  Builder. Examples: WORK_STATE claims RUNNING with no process; MWO id behind; a blocker older than 24h with no comms;
  heartbeat timestamps fresh but the content frozen.
- Recall = flagged / planted. Latency = flag time minus plant time.
- Paired with: **OBS-1b false-alarm rate** on unplanted seat-hours, audited against ground truth. Ground truth is a
  periodic independent audit of processes, git and comms, as in Artemis's CWO role.

### Secondary endpoints

| ID | Endpoint | Auto? | Gameable how | Cheat control |
|---|---|---|---|---|
| OBS-2 | stale-state incidence: seat-hours where WORK_STATE disagrees with audited ground truth | semi | **update timestamps without changing content** (the main cheat) | compare CONTENT against ground truth, not timestamps; a fresh timestamp with a stale claim counts as stale |
| OBS-3 | operator minutes on status discovery | partial | the operator stops asking (fatigue) | measured by the operator's own logged time, plus operator status-question messages; reported with operator availability as a covariate |
| OBS-4 | dependency lead time: hours between a predicted blocker being surfaced and its stall | yes | predict everything | Brier score on blocker predictions |
| OBS-5 | stale-authority incidents (a seat acts on a superseded order; cf. Artemis about 2h15m, CWO-C s11) | semi | — | counted from comms and git: an action after the adoption deadline citing a superseded order id |

Note on P5: CWO-B and CWO-C MANDATE heartbeats, so heartbeat counts and "fresh WORK_STATE" are void as Builder evidence
for 2026-09-30 to 10-07. OBS-1 (planted) is immune to this, because a mandate cannot make a detector find a plant.

---------------------------------------------------------------------------------------------------------------------

## 4. Cross-Builder endpoints (lab level)

| ID | Endpoint | Purpose |
|---|---|---|
| LAB-1 | (rev 2) LBS: load-bearing survival under an external audit (causal model s1.1), as an interrupted time series around staggered releases | the only endpoint tied to the North Star; descriptive at lab level |
| LAB-2 | the proportion of all failures that are infrastructure-attributed (FAB-2 rule) | separates C7 from C6/C11 |
| LAB-3 | operator-minutes per VIU | X2 control; the denominator the North Star actually cares about |
| LAB-4 | Builder cost: inference + compute + operator review minutes | Builders are not free; payoff must exceed cost |

Break-even rule (rev 2): a Builder lane is CONTINUE if BOTH of the following hold:
1. its instrument-level battery passes (level i);
2. the sandbox mechanism test (level ii), where one exists, shows a payoff exceeding LAB-4 cost.
Lab-level LBS (level iii) can veto a lane, through a clear adverse trend, but cannot by itself justify one.
Otherwise it is PARK. This mirrors the S4 break-even logic (41.2 < 64).

---------------------------------------------------------------------------------------------------------------------

## 5. Gameability summary (the honest table)

| Endpoint | Gameability | Why | Residual risk after controls |
|---|---|---|---|
| raw message, commit, packet or heartbeat counts | **total** | mandated or free to produce | excluded entirely |
| reuse counts (imports) | high | trivial imports | medium: receipt-hash rule helps |
| pre-run kill fraction | high | kill everything | low with the false-kill audit |
| time-to-result | high | easier questions; clock games | medium: difficulty forecast + first-mention clock |
| infra-failure fraction | medium | relabeling | low with the retry rule + blind audit |
| planted-battery catch rates (FAB-1b, EXP-4, OBS-1) | **medium** (rev 2, K3) | sealed, but same-model authors and the custody limits on shared hosts (#1128) leak style | rotate; author 40%+ outside the model family; anchor items |
| downstream eta on non-commissioning work | low | requires real VIUs | the VIU review itself can be gamed (see the Observatory reviewer-independence rule) |
| operator-minutes | medium | the operator under-reports or fatigues | needs the operator's own log; accept noise |

---------------------------------------------------------------------------------------------------------------------

## 6. Minimum viable instrumentation (implement now, cheaply)

These seven items need no new science and no privileged installs. They make the rest computable later.

1. `p_pred` and `difficulty_forecast` fields in every prereg manifest (one line each). These are the basis of VIU
   surprisal and the difficulty control.
2. A `manual=true|false` plus `actor` field on Fabric receipts.
3. An `origin` field on every infrastructure/process commit: OPERATOR / SEAT / BUILDER / EXTERNAL. This could be a
   commit trailer (`Improvement-Origin:`).
4. A `consumes:` list in WORK_STATE `next_actions` and in packets, naming the VIU ids that a decision relied on. This is
   the consumption edge.
5. A canary submitter: a sealed set of 10 Fabric tasks, scheduled.
6. A planted-staleness generator for OBS-1, run by a seat that is not a Builder.
7. Verdict-class normalisation across seats: POSITIVE / NULL / KILLED / UNTESTABLE / INVALID / PARKED. Today these
   strings are seat-local.

Items 1-4 are additive fields with no migration cost. Items 5-6 are small scripts. Item 7 is a mapping table.
