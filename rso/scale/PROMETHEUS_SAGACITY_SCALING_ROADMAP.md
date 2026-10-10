# Prometheus Sagacity Scaling Roadmap -- v1 (C-013-T031, Workstream D)

Palamedes[harry1-679179c6], 2026-10-10. A map of decisions, not a backlog and not a schedule. Sources:
roles/Palamedes/notes/2026-10-10_strategic_sources/ (Hestia Audit 1 + Oct-8 response M1-M7; Atlas G1-G6 + Nyx's
attack; ASTRA-6.0, FABLE-5.1, v0.4 synthesis, wind-tunnel reviews; execution inventory), rso/scale/
RSO_SCALING_ASSESSMENT.md, and C-004/C-009/C-010 results. Status: v1 -- LONG_DURATION_EXECUTION_ARCHITECTURE.md,
CHECKPOINT_REPLAY_SURVEY.md and the session-independent runner (fire test 13/13) are folded in; the D1 result is
pending (challenge in progress); external Astra/Fable reviews and Hestia's review are PENDING (none has occurred).

## 0. The position in one paragraph

Across 25 engines the organisms find one-part mechanisms and none finds "the first mechanism made of two parts that
are individually worthless" (Hestia W1, measured 7 times). Per amendment M1 this is "a strong prior for the tested
representations; not a proof for population search with recombination, neutrality, spatial structure or lifetime
learning". Per Hestia's Oct-8 answers: longer runs will not help ("time crosses rarity; it does not cross
composition"), world demand must start now (M3), and lifetime plasticity is "the cheapest lever we have not pulled".
The Observatory itself can now qualify a native result in hours for tens of CPU-minutes (C-010); its throughput is
limited by bespoke qualification, coordination latency and the scarcity of discriminating targets, not by compute
(RSO_SCALING_ASSESSMENT.md). Prometheus's advantage must therefore come from choosing and structuring experiments, not
from running more of them.

## 1. North-star distinction applied to every decision

An experiment is in scope for scaling only if its estimand concerns acquiring NEW capabilities (a 2-part mechanism
reached; reuse lowering a later acquisition cost; a learning procedure making a desert crossable), not optimising an
existing one (higher fitness on a mechanism already found). Fitness, activity and genome growth never earn budget
(s12). Every claim carries Hestia's cognitive accounting (M5): what the organism computed vs. what inherited
architecture, development, the world, search infrastructure and the evaluator supplied.

## 2. The decision ladder for any proposed experiment (escalation stages 0-5, s4)

  Stage 0  analytical rejection. Answer the five questions of reachability cartography for the target (expressible /
           reachable / rewarded / credited / detected -- Hestia M2; rso/reach/REACHABILITY_CARTOGRAPHY_V0.md) with
           enumeration, constructed organisms and cheap controls. Required before any search: a known-answer
           construction that works; a demonstration that a specified simpler alternative does NOT solve the world
           (World-Demand admission, M3); a ruler shown to detect a planted positive and reject a planted near-miss.
  Stage 1  local CPU discovery at the smallest budget that can move (screen at 8 seeds; Hestia RESPONSE plan).
           Measure evaluations/s, memory/candidate, hitting-time distribution, frontier movement, instrumentation
           overhead, mechanism survival.
  Stage 2  local GPU qualification only where the workload is batched and measured to benefit (M1/M2 RTX 5060 Ti).
  Stage 3  bounded cloud pilot: only after local qualification; every run states question, workload, hardware,
           duration, MAXIMUM AUTHORISED SPEND (operator-approved; client-side estimates are not caps), throughput,
           checkpoint cadence, termination and recovery, and the observation that would justify more scale.
  Stage 4  extended distributed run at 1x / 4x / 16x budgets as a preregistered comparison.
  Stage 5  long-running adaptive research with checkpoint/restart, leases, provenance, plateau detection and frozen
           stopping and escalation criteria (LONG_DURATION_EXECUTION_ARCHITECTURE.md).
  Promotion rule between stages: a registered observation that more budget could reveal a NEW capability (not more
  fitness) -- e.g. a hitting-time distribution with mass near the budget edge, a stepping stone preserved and
  extended, a later acquisition getting cheaper. Registered before the extra outcomes are seen.
  Stopping rules: instrument failure; absence of world demand (a reflex or register baseline solves it); discovery
  rate plateau; repeated rediscovery of one trivial mechanism; complexity growth without capability growth.

## 3. Multi-fidelity evidence (scaling the scientific process, s8; Hestia M6 "cheap exploration, expensive proof")

  tier E  exploratory evaluation: no custody, no challenge; labelled EXPLORATORY and never cited as evidence.
  tier S  provisional screen: frozen config, ledgered, seeds partitioned; a candidate list, not a claim.
  tier A  qualified mechanism assay: preregistered, bound receipts (rso/binding), custody, controls incl. the M5 set
          (archive disabled at final evaluation; shuffled history; random library).
  tier C  independent challenge (Q3, other model; committed before outcomes).
  tier R  preserved result (bounded class, costs, known escapes).
  Transitions are explicit records. Only tier R is a scientific finding; a tier-E or tier-S number that appears in a
  claim is a defect. Challenge (tier C) is reserved for promoted claims: 7 of 7 challenges found real defects, so it is
  worth its cost, and at ~1.5-2.2 Q3 hours per path it is the stage that must not be spent on every candidate.

## 4. Horizon I -- about one month (qualification, cheap, reproducible)

  Most important uncertainty: are the composition deserts crossable by SEARCH-STRUCTURE interventions at a fixed
    budget (retention, neutral acceptance, novelty selection, worse-candidate admission, structured credit), or do
    they need representation or developmental change?
  Resolving experiment: C-013 D1 on the FABLE-5.1 p1_slice reach world (known 8-instruction construction; chain
    baseline 1/24), then the SAME frozen cartography protocol on one audited desert with a known construction --
    routed to its owner, never run over another seat's charter: Ananke FLIP (16-line plant; 0/290; Hestia's "single
    most informative next run") or SFE W2_K2 (12-instruction witness; 0/395; CREDIT).
  Prerequisites: cartography protocol + certification wrapper (C-013-T010); owner agreement for the second desert.
  Resource class: local CPU, single-digit core-hours each.
  Success: a preregistered contrast moves (an arm certified-reaches the target where chain does not, Holm-adjusted),
    AND the mechanism the hits use is the construction's or a qualified alternative -- not a seeded control.
  Failure: no arm moves with budget-relative upper bounds stated -> search structure alone is not the lever at
    these budgets; Horizon II tests representation/development.
  Pivot if: the behaviour descriptor cannot separate meaningful intermediates from arbitrary genomes (then no archive
    result is interpretable -- fix the descriptor first, per Nyx A4), or the target turns out REWARD/CREDIT-bound.
  Also in Horizon I (platform): a qualified-component registry so the next native runtime pays only for its adapter
    (assessment B1); a durable run-record + local runner so a job survives its session (assessment B2); one
    World-Demand admission ladder (reference solver succeeds; reflex/register/memoryless baselines fail) on a world
    from the existing Ensorain N0-N6 / Ludus / Cosmos parts, owned where Hestia's M3 places it. In flight elsewhere,
    to be reused not duplicated: Aphrodite's Beta-04 (C-015: typed list-program foundry R0-R4 with a null ladder and a
    known-positive gate, adopting D1's arms and descriptor test) and Ensorain's C-014/WTP-05 (0.2-0.8 admission band).

## 5. Horizon II -- about one quarter (developmental and evolutionary exploration)

  Most important uncertainty: does lifetime plasticity or developmental promotion make a two-part mechanism reachable
    that blind search does not reach -- without the machinery itself supplying the solution?
  Resolving experiment: on the one desert Horizon I characterised as REACH-bound, a preregistered 2x2: promotion
    (a generic, reversible developmental promotion operator, ChatGPT review 2 via Hestia) on/off x lifetime plasticity
    on/off, at 1x and 4x budgets; cognitive accounting per M5; archive disabled at final evaluation; shuffled-history
    and random-library controls; a conventional learner baseline (stronger ordinary competitor, ASTRA D3).
  Prerequisites: Horizon I characterisation; a promotion operator that is substrate-generic (checked by applying it to
    a second substrate); durable execution for multi-day runs; Q3 challenge on the frozen assay.
  Resource class: local CPU fleet, days; GPU only if Stage 2 measures a benefit.
  Success: the target is reached at >= 5/32 seeds at 4x (Hestia's ladder readout) only in the promotion and/or
    plasticity arms, certified by rulers not fitness, with the accounting showing the organism -- not the operator --
    did the composing.
  Failure: 0/32 in every arm with bounds -> the representation, not the search or development, is the barrier; pivot
    to a representation change or to an unfamiliar-substrate lane (portfolio F).
  Pivot if: promotion only works when it encodes the target (designed reasoning with extra steps -- Hestia's open
    question 4), or the conventional learner wins outright (then that is the finding: ASTRA's thesis exit).

## 6. Horizon III -- about one year (sustained search for cumulative capability)

  Most important uncertainty: do discoveries lower the acquisition cost of LATER discoveries -- does Hestia's R4
    ("reuse of a unit") appear and compound, and does the system's capacity to learn improve?
  Resolving experiment: a curriculum of admitted World-Demand worlds R0 -> R4 (memory bit, composition, lifetime
    learning, reuse of an earlier discovery, revision after a rule change -- the five distinct demands of s6),
    measuring acquisition-cost curves against a conventional learner and against the same system with reuse disabled;
    co-development of world demand only after a seed exists (M5).
  Prerequisites: a Horizon II success; durable multi-week execution; a mechanism library with provenance; the
    qualified-component registry; a cost ledger (assessment s5: no fleet dollar ledger exists today).
  Resource class: fleet weeks; bounded cloud only at Stage 3-4 with operator-approved caps.
  Success: acquisition cost of the k-th capability falls with k beyond the reuse-disabled control and the
    conventional baseline, with qualified mechanisms at each rung.
  Failure: flat acquisition cost -> the system optimises, it does not accumulate; publish the bounded negative.
  Pivot if: gains vanish under "archive off at final evaluation" (the search infrastructure did the work) or under
    shuffled history (no real reuse).

## 7. The portfolio (s11) as discriminating experiments with dependencies

  D reachability archives      Horizon I (D1, then one audited desert)             first; cheapest; informs B, A
  C structured credit           Horizon I on a CREDIT-bound desert (SFE, Crius)     after D's protocol exists
  B lifetime plasticity         Horizon II arm                                      after D/C characterise a target
  A developmental modularity    Horizon II arm                                      same assay as B (2x2)
  E world-organism co-dev       Horizon III, only after a seed (M5)                 depends on the Foundry
  F unfamiliar substrates       reserved lane, ~15-20% of compute (ChatGPT 1; Hestia maps membership differently --
                                disagreement preserved)                             independent of A-D
  No substrate keeps resources because of past investment; a conventional baseline may win; a negative may close a
  line (M4: retire for a NAMED bottleneck only).

## 8. Compute economy (s10)

  Cost of discovering a candidate vs cost of proving it: today a qualified evidence path costs ~10-30 ledgered
  CPU-minutes but ~1.5-2.2 Q3 reviewer-hours, one repair round and 4-10 hours of wall time (assessment s1, s4) --
  proof dominates by orders of magnitude. Cheap exploration (Ananke: 3,456 evaluations per search) is affordable in
  bulk; challenges are not. Policy: spend tier C only on promoted claims; measure cost per qualified finding, never
  per evaluation alone. Account: CPU core-h, GPU-h, peak/avg memory, storage, transfer, inference tokens, reviewer and
  engineering time, operator interventions, dollars (the last has no fleet ledger yet -- a Horizon I gap).

## 9. When renting compute would actually help (s17 Q6)

  Only when (a) an experiment has passed Stages 0-2 locally, (b) its registered promotion criterion says more budget
  could reveal a new capability (a rarity barrier, which time crosses -- RELAY-multihop crossed at 4x/8x/16x -- not a
  composition barrier, which it does not), (c) the workload is measured to batch well, and (d) it checkpoints so
  interruption costs bounded work. Aether's ~3 weeks of RunPod GPU on random soup is the counter-example: GPU scale
  without a demanded mechanism bought 1.6e12 site-ticks of near-triviality ("NOT more GPU scale"). Paid runs need the
  operator's explicit cap; the client-side estimate in Aether/runpod is not a hard limit.

## 10. Honesty at scale (s17 Q7)

  tiered evidence with explicit transitions (s3); preregistered promotion and stopping rules (s2); bound receipts and
  custody for tier A and above; independent Q3 challenge before tier R; cognitive accounting and the M5 controls on
  every claim of organism capability; budget-relative upper bounds instead of "impossible"; exploratory numbers that
  leak into claims treated as defects; counts of challenges and survivors published beside results.

## 11. A seven-day experiment without a live agent session (s17 Q5)

  The job owns its state: immutable manifest + seed partitions + append-only progress events + periodic checkpoint
  records with hashes, written to a retained store; any seat (or an operator command) resumes from the last verified
  checkpoint; a lease prevents double execution; final accounting is computed from the event log
  (LONG_DURATION_EXECUTION_ARCHITECTURE.md s3). DEMONSTRATED on one host in this window: rso/scale/runner/ survived
  worker, supervisor and session loss and a different session resumed it to the control's digest (FIRE_TEST.md, 13/13);
  checkpoint retention (T024) bounds storage; an idempotent relaunch entry (T025) removes the "someone must run launch"
  dependency once the operator chooses to install a host scheduler task (documented, deliberately not installed).
  Missing for seven days on the fleet: cross-host transport (P-4: port onto Themis's C-012 NF transport; depends on its
  large-object fetch path), a standing worker plane (Fabric
  carries work only inside its owner's windows -- C-012 published 1,504 benchmark and 12 native-world epochs through it
  on 2026-10-10 -- and is otherwise idle, 0 live of 61 at 12:40Z), and an engine save/load pair -- only Aether's
  kernel, z80atlas (pickle) and Proteus checkpoint today without engine edits (CHECKPOINT_REPLAY_SURVEY.md).

## 12. Open disagreements (preserved, not synthesised away)

  - Archive value: Gemini "required"; ChatGPT 2 and Hestia: only with certificate-keyed descriptors; Nyx: S4 is
    MAP-Elites with count selection and "Go-Explore" must not describe genome copying. This roadmap sides with Nyx and
    Hestia pending D1.
  - Whether promotion is "designed reasoning with extra steps" (Hestia open question) -- Horizon II's pivot rule.
  - Alien-lane share and membership (ChatGPT 1 vs Hestia).
  - Whether W1 is near-theorem or representation-specific (M1 chose the latter; literature unverified).
  - ASTRA's planning caps (0 GPU, local CPU only) vs this directive's exploration of RunPod escalation: not resolved
    here; Stage 3 stays operator-gated.

## 13. The next decisions (to be finalised in RECOMMENDATION.md at closeout)

  next engineering investment (provisional): port the now-demonstrated session-independent runner onto Themis's C-012
    NF transport (cross-host, P-4) TOGETHER WITH a qualified-component registry -- relieves assessment B2 across hosts
    and B1, is small relative to the alternatives, and every later horizon depends on it. Evidence since v1: C-012's
    owner reports N2 and N5 exist, N4 measured (~0.10 s coordination per epoch; 1.6% wasted work under induced kills),
    N1 (out-of-database checkpoint refs) and N3 (run_tag) not built but small (comms #2043/#2044). Themis's C-012
    review packet (moonshot/pivot/C012_NF2_REVIEW_2026-10-10.md s7) lists option D -- offer that path to the
    Observatory -- but LEANS A (park: "the only native workload sits three to four orders of magnitude below the
    envelope; building more now would be engineering ahead of demand"). The same argument bears on P-4 here and is
    NOT answered yet: this program's measured workloads are tens of CPU-minutes per campaign (s5 of the assessment),
    D1 is ~3 core-hours on one host, and B2's waiting is between SEATS, not between hosts. If nothing in Horizon I
    needs a second host, the cheaper investment that attacks B2 directly is the qualified-component registry plus
    event-driven dispatch of READY packets, with P-4 deferred until a registered workload exceeds one host. To be
    decided in RECOMMENDATION.md with D1's measured cost in hand; recorded here as an open disagreement with my own
    v1 provisional choice.
  next scientific experiment (provisional): D1, then the same frozen cartography on one audited desert (Ananke FLIP),
    routed to its owner.
