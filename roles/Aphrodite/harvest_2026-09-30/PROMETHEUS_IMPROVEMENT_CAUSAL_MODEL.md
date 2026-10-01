# PROMETHEUS IMPROVEMENT -- A CAUSAL MODEL

Seat: Aphrodite. Operator directive: bounded inference harvest, 2026-09-30 to 2026-10-01 05:00 America/New_York.
Evidence tier: Tier 1-3 (analysis, design, synthesis). This document makes NO positive RSI claim and promotes no
evidence tier. Retrospective numbers are in s7 and come from the history analyses in `evidence/`.

Question: how would we know whether Prometheus is genuinely getting better at producing FUTURE scientific improvements,
rather than accumulating code, memory, compute, agents and process?

Prometheus itself is treated as the candidate improvement process. This puts it in the same position as the engines that
Aphrodite has tested since 2026-09-17: the stance is the same, and so are the hostile controls and the rule that
throughput is never the ruler.

---------------------------------------------------------------------------------------------------------------------

## 1. The unit of output

Commits, packets, messages, experiments run and agents live are not output. They are activity.

**Definition (VIU -- validated information update).** A VIU is a preregistered claim with all four of the following:
1. a frozen decision rule;
2. a verdict of any sign (POSITIVE, NULL or KILLED counts; UNTESTABLE and INVALID do not);
3. survival of one independent adversarial review that was free to find an invalidating defect;
4. **consumption**: a later decision (a design, a kill, a scope change, a ruling) that names it and would have gone
   differently without it.

A VIU is weighted by its **information value** (s1.1). Raw VIU counts are an intermediate quantity, not the endpoint.

### 1.1 Information value (operationalisable today)

At freeze, the seat records `p_pred`, a probability for each preregistered outcome. This is one field in the prereg
manifest. At verdict, the information value is the surprisal under a **pooled, calibrated** prior. The seat's own prior is
not used for this, because a seat can inflate surprisal by registering a miscalibrated prior.

    info(v) = -log2 q(outcome)        q = calibrated forecast from the pooled forecast record (isotonic per seat)

Calibration is scored separately (Brier score per seat). A seat whose forecasts are systematically wrong gets more
"surprise" credit, but it also gets a worse calibration score. Both are reported, never netted (Goodhart control G-4 in
`BUILDER_EVALUATION_PROTOCOL.md`).

Why surprisal and not "positive results": a lab that only confirms what it already believed is not learning, and a lab
that only reports positives is not measuring. A clean, decision-changing NULL is worth as much as a positive of the same
surprisal. A NULL that everyone predicted at p = 0.95 is worth 0.07 bits. That is correct.

### 1.2 Yield and its derivatives

For a window w and resource vector r(w) = (inference tokens, CPU core-h, GPU-h, operator-minutes, wall-clock):

    Y(w)      = sum of info(v) over VIUs v verdicted in w
    eta(w)    = Y(w) / cost(r(w))                   -- yield per resource, the first-order "improvement" quantity
    eta'(w)   = d eta / d w, at fixed task difficulty -- improvement
    eta''     = whether the RATE at which eta rises is itself produced by the system and is rising -- see s5

`cost` is reported per component and never collapsed into one scalar for headline claims. Operator-minutes are a
first-class resource. A lab whose eta rises because James works harder has not improved.

---------------------------------------------------------------------------------------------------------------------

## 2. Candidate causes of apparent improvement

Twelve mechanisms can raise observed output. Each is defined as an intervention-able node.

| # | Mechanism | Stock or flow | What changes | Example in Prometheus |
|---|---|---|---|---|
| C1 | additional inference | flow | more tokens per question | Opus 5.5 sessions, worker subagents |
| C2 | additional compute | flow | more core-h / GPU-h | Fabric workers, RunPod/Azure (capped) |
| C3 | memory accumulation | stock | more stored artifacts | journals, WORK_STATE, evidence packets, MEMORY.md |
| C4 | better retrieval | stock->flow | the same memory becomes findable | evidence_wiki, ops/threads, NEXT_SESSION boot order |
| C5 | better tools | stock | per-task setup and execution cost falls | fabric lease, comms, cert.py, tribunal T4, fleet_status.py |
| C6 | evaluator/ruler improvement | stock | the validity of verdicts | ruler v2, positive controls, sham arms, pre-freeze supply screens |
| C7 | infrastructure reliability | stock | the fraction of failures that are not science | disk-full fixes, Windows Fabric CLI repair |
| C8 | selection of agents/tasks | policy | WHICH questions are asked and by whom | Aporia dispatch, MWO portfolio, kills |
| C9 | parallelism | flow | more seats at once | 20+ seats, 4 hosts |
| C10 | domain knowledge | stock | facts about a substrate | "the tribunal certifies only commutative bounded folds" |
| C11 | reusable experimental skill | stock | domain-independent procedure | "screen supply before freezing", "sham with equal expressivity" |
| C12 | improvement-process improvement | meta | the rate at which C4-C11 are PRODUCED | a Builder that makes later Builders/rulers cheaper |

Two exogenous causes are NOT part of the system, and every claim must control for them:

| # | Exogenous cause | Why it is dangerous |
|---|---|---|
| X1 | model-version change (e.g. a new Opus) | a step change in every seat at once; it looks like fleet-wide skill transfer |
| X2 | operator attention and skill | James is the highest-bandwidth corrector in the system; his effort is unmetered |

X3 (the time trend of task difficulty) is a hidden moderator: seats move toward easier or harder questions, and yield moves
with them.

### 2.1 Causal graph (directed, simplified)

    X1 model ---------------------------------------------------------------+
    X2 operator ---> C8 selection ---> task mix ---+                        |
         |                                         v                        v
         +--------> C6 rulers ---> verdict validity ---> VIU ---> consumption ---> C10 / C11 stocks
                         ^                         ^                              |
    C12 ---> C5 tools ---+---> setup cost ---------+                              |
     ^        C7 infra ---> failure attribution ---+                              |
     |        C3 memory ---> C4 retrieval ---> duplicate avoidance / reuse --------+
     |        C1, C2, C9 ---> attempts per window ---> raw activity (NOT VIU)
     +---------------- produced by: seats' own outputs?  or by operator?  <-- the RSI question (s5)

The arrow that matters most, and is least observed today, is the one INTO C12: who produced the improvement to the
improvement process.

---------------------------------------------------------------------------------------------------------------------

## 3. Observable signatures that separate the causes

The method: every mechanism predicts a different pattern under some contrast that the lab can actually run, retrospectively or prospectively. A
mechanism is "supported" only if its own signature appears AND the signatures of its rivals do not explain the
same data.

| Cause | Signature if it is the driver | Contrast that isolates it | Rival it is most confused with |
|---|---|---|---|
| C1 inference | yield scales with tokens; eta (per token) flat | budget-equalised replay: same question, capped tokens | C11 (skill looks like "the model thinks better") |
| C2 compute | yield scales with core-h; eta per core-h flat; gains concentrate in brute-force search | equal-compute arms (Aphrodite's 'charge' accounting) | C5 (faster tools look like more compute) |
| C3 memory | gains only on questions that OVERLAP stored content; no change on novel substrates; artifact count rises much faster than VIU | memory ablation: fresh context with the same task | C4, C10 |
| C4 retrieval | fewer duplicate experiments ("has this been tested?" hits); faster boot-to-first-useful-action; same memory size | retrieval ablation: memory present, index removed (raw git only) | C3 |
| C5 tools | setup effort falls ONLY for tasks that use the tool; zero effect on tool-free tasks | tool-access ablation within one seat; tool-users vs non-users at matched tasks | C11 |
| C6 rulers | the verdict mix SHIFTS: fewer post-report retractions, more pre-run kills; raw positive rate can FALL; false positives on planted cases fall | planted-defect and planted-effect batteries scored by old vs new ruler | C11, C8 |
| C7 infra | the infra-attributable failure fraction falls; time-to-result VARIANCE falls; the science-failure rate is unchanged | failure attribution audit; before/after at fixed science | C5 |
| C8 selection | per-agent and per-task-type yield FLAT, aggregate rises (composition effect) | within-unit vs between-unit decomposition (Oaxaca/Simpson split) | everything; the default confound |
| C9 parallelism | aggregate throughput ~ seats; per-seat flat or falling; coordination overhead superlinear | per-seat normalisation; overhead share vs seat count | C1 |
| C10 domain knowledge | in-domain gains; zero transfer to an unseen substrate | transfer test to a substrate with no project history | C11 |
| C11 reusable skill | a procedure learned on substrate A reduces INVALID/UNTESTABLE on substrate B, with no B history and no B-specific tool | cross-substrate transfer with the procedure ablated (prompt/packet without the lesson) | C10, X1 |
| C12 IPI | the RATE at which C4-C11 improvements are produced rises per unit resource, and those improvements are produced by system outputs, not by operator directive or a model upgrade | generation-indexed production function (s5); operator-authorship audit | X2, X1 |
| X1 model | a simultaneous step in many seats at a known date; no lag structure; no dependency on which tools a seat used | event study on model-switch dates (comms boot model strings) | C11, C12 |
| X2 operator | gains co-move with operator message volume and rulings; gains vanish in operator-absent windows | operator-quiet windows (nights, 05:00 cutoffs) vs active windows | C12 |

### 3.1 The three most diagnostic contrasts

1. **Cross-substrate transfer with lesson ablation (C11 vs C10/C3).** The only clean evidence of reusable skill is a
   lesson from engine A that pays on engine B, together with a matched control where the lesson is removed. Everything
   else is consistent with domain knowledge or memory.
2. **Within/between decomposition (C8).** If aggregate yield rises but per-seat yield at matched task type does not,
   the lab has improved its portfolio, not its capability. That is real and useful. It is not "Prometheus got better
   at science". It is "Prometheus (mostly James) got better at choosing".
3. **Authorship of process changes (C12 vs X2).** For every change to tools, rulers or control plane, record who
   originated it: an operator directive (MWO/CWO text), a seat's own proposal, or a seat's output consumed without
   human edit. IPI that is all operator-originated is improvement BY James OF Prometheus. It is not improvement by
   Prometheus of itself.

---------------------------------------------------------------------------------------------------------------------

## 4. What "better at producing future improvements" must mean

Four statements of increasing strength. Each is falsifiable and none uses artifact counts.

- **S-a (it improves).** eta rises over windows at matched task difficulty after controlling X1 and X2.
  Falsifier: eta flat or falling within seats at matched task type; the aggregate rise is fully explained by C8, C9, C1, C2.
- **S-b (it improves its instruments).** C5, C6 and C7 stocks rise, and each improvement is followed by a measurable eta gain
  on LATER work that was not the motivating case. Falsifier: tool/ruler adoption with no downstream eta change, or a
  gain only on the work that commissioned the tool ("built for its own experiment", AGENT_SCIENCE E5).
- **S-c (it improves how it improves).** The production of S-b improvements becomes cheaper or more effective per
  resource: time from "friction observed" to "friction removed", per unit operator-minute, falls across generations of
  improvement. Falsifier: flat improvement-production cost, or a falling cost fully attributable to operator effort or a
  model upgrade.
- **S-d (recursive).** S-c, where the improvements to the improvement process were themselves produced by the system's
  prior outputs (not operator-originated, not a model upgrade), and this holds for at least two successive generations with
  non-decreasing per-generation gain and bounded operator input. Falsifier: see `RSI_BOUNDARY_REVISITED_2026-09-30.md` rungs L4-L6.

Throughput is excluded by construction. More commits, more packets, more agents, more messages and more experiments
appear only in the denominator (cost) or as covariates, never in the numerator.

---------------------------------------------------------------------------------------------------------------------

## 5. The generation-indexed production function (how S-c and S-d become measurable)

Index every process improvement (tool, ruler, control-plane change, Builder output) as an **improvement event** e with:
- `origin`: OPERATOR / SEAT-PROPOSED-OPERATOR-APPROVED / SEAT-AUTONOMOUS / BUILDER / EXTERNAL-MODEL
- `parents`: the earlier improvement events whose outputs were used to produce e (the lineage)
- `generation g(e)` = 1 + max g(parents); a root has g = 1
- `cost(e)`: inference, compute, operator-minutes and wall-clock to produce e
- `payoff(e)`: the change in eta on downstream work NOT used to motivate e, measured over a fixed horizon against a
  matched comparison stream that did not use e

Then:
- improvement      = some payoff(e) > 0 (S-b);
- IPI              = cost-normalised payoff rising with g (S-c);
- recursive        = IPI along lineages whose internal nodes are non-OPERATOR, for g >= 3, with operator-minutes per
                     generation non-increasing (S-d).

This is the lab-scale analogue of Aphrodite's engine-scale R1-R5 (AMENDMENT 15 s7). R1 G1-dependence becomes "the
generation-g output depends on generation-(g-1) outputs". R2 G2>G1 becomes "payoff rises with g". R3 attribution becomes
lineage. R4 hostile controls become matched non-using streams and sham improvements. R5 no leakage becomes no operator
hand-edit inside the lineage.

---------------------------------------------------------------------------------------------------------------------

## 6. Confounding structure: why naive readings mislead

1. **Detection-effort confound.** More reviewers, more auditors and more critics find more defects. A rising defect-discovery
   count says nothing about the defect PRODUCTION rate. You need the rate per unit of first-pass work AND the stage at which
   defects are found, under a fixed detection protocol (a planted-defect battery).
2. **Survivorship and recording drift.** Records improved over time (WORK_STATE schema, ops/threads, IDs from MWO-0001).
   Early episodes are under-recorded, so trends in "recorded X" are partly trends in recording.
3. **Simultaneous interventions.** Comms (09-11), Fabric, MWOs (09-28..29), CWOs (3 on 09-30) and the Builders all land within
   about 3 weeks, and several land on a single day. Before/after contrasts cannot separate them.
4. **Model change (X1)** affects all seats at once and mimics fleet-wide skill transfer.
5. **Operator as mediator (X2).** Nearly every governance improvement originates in operator text. The operator is also
   the main source of the corrections that seats then "learn". Self-correction that follows an operator ruling is
   compliance, not self-correction.
6. **Goodhart on governance.** The CWO mandates heartbeats, pushes and receipts, so visibility metrics rise BY DECREE.
   Any metric that a CWO mandates is void as evidence of improvement for the window in which it was mandated.
7. **Task-difficulty drift.** Seats that hit walls get parked; the survivors work on tractable questions. Yield per
   live seat rises with no capability change (C8 again).
8. **Window length.** The comms record covers 20 days. Most "trends" are 1-3 episode-long. Regression to the mean after a
   crisis (e.g. after the ruler failures that preceded A23) is indistinguishable from learning at this N.

---------------------------------------------------------------------------------------------------------------------

## 7. Retrospective evidence (summary; details in INFERENCE_HARVEST_HANDOFF.md and evidence/)

See s7 of the handoff. It is filled in from four independent history analyses (defects, interventions, the experiment
ledger, human load and reuse) and one adversarial critic.

---------------------------------------------------------------------------------------------------------------------

## 8. What this model forbids saying

- "Prometheus is recursively self-improving" -- not unless S-d holds (RSI_BOUNDARY L5+). No current evidence reaches L4.
- "Prometheus is improving because it produced N more experiments/packets/commits" -- throughput is not a ruler.
- "Seats are getting better at finding their own bugs" -- not without a fixed-protocol planted-defect battery; a
  rising self-catch rate is equally explained by worse first passes (AGENT_SCIENCE E8).
- "Builders improved science" -- not without downstream eta on work they were not built for (BUILDER protocol B-T3).
