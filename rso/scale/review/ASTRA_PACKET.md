+============================================================================+
| ASTRA REVIEW PACKET -- Observatory scaling, compute economy, distributed   |
| execution, checkpointing, extensibility (C-013, Strategic Expansion)       |
| Author: Palamedes (Lead RSO Engineer, coordinator), harry1/M4,             |
|         claude-opus-5-5, instance harry1-679179c6                          |
| Date:   2026-10-10 (prepared; review NOT yet performed)                    |
| For:    Astra (external architecture reviewer), the operator (HITL)        |
| Status: REQUEST FOR REVIEW. Self-contained: no repository access needed.   |
+============================================================================+

0. WHAT WE ASK OF YOU
----------------------
Attack the architecture and the compute economy, not the prose. Five
questions from the operator (s14), restated:
  A1 Can the Observatory support long-duration experiments as designed?
  A2 Are the abstraction boundaries right?
  A3 Is the resource model credible?
  A4 Which architectural decisions are premature?
  A5 Where does distributed execution create hidden SCIENTIFIC problems?
"Not worth building" and "build less" are first-class answers.

1. CONTEXT IN ONE PARAGRAPH
----------------------------
Prometheus asks under what conditions computational systems evolve
increasingly sophisticated sagacity. Its Observatory (RSO) qualifies
evidence about native runtimes. In the last week it ran three campaigns:
a methods slice (C-004, closed INCOMPLETE after two repair rounds), a
first-class execution binding (C-009, closed scoped to flat inventories),
and the first native retained-information witness (C-010, Ares W15:
instrument qualified, both subjects NEGATIVE). A program-wide audit of 25
engines (Hestia) found organisms discover one-part mechanisms but never a
two-part mechanism whose parts are individually worthless. Resources: local
CPU machines, six small Ubuntu nodes (no GPU), two RTX 5060 Ti GPUs, rented
GPUs via RunPod (no spend authorized in this window), strong reasoning
models for design and review. We cannot buy scale; we must spend
intelligently.

2. MEASURED FACTS THE ARCHITECTURE MUST FIT
--------------------------------------------
  compute      C-004 / C-009 / C-010 ledgered 53.1 / 31.8 / 26.2 CPU-min;
               0 GPU-seconds. Two independent tools agree to the decimal.
  wall time    ~3.1 days / 8.0 h / 6.2 h per campaign.
  waiting      69-82% of every work packet's lifetime was WAITING (for a
               seat to claim, or for the coordinator to integrate);
               median work per packet 12-15 min.
  reuse        ~17% of ~9,700 implementation lines is reusable across
               experiments (ledger, binding, canonical receipts, custody
               reads, mutation runner, ruler, driver core).
  challenge    7 of 7 independent adversarial challenges found real
               defects; each costs ~1.5-2.2 reviewer-model hours, one
               repair round, 4-10 h wall.
  fleet        Fabric (Postgres task queue): no standing workers (0 live
               of 61 registered between windows). A sibling campaign
               (C-012) ran bounded workers on two Ubuntu nodes through it
               today: 1,504 benchmark epochs, 12/12 native-world epochs
               validated; ~0.10 s coordination per epoch at 3-60 s epochs;
               1.6% execution wasted under 3 induced worker kills. Its
               owner leans to PARK it: the only native workload is 3-4
               orders of magnitude below its envelope. Lease plane,
               custody registry and blob store verified operational.
               Ubuntu nodes: one smoke-test receipt in their history. RunPod
               launcher: >40 historical receipts, every pod observed
               terminated; its budget check is a client-side estimate, not
               a hard cap; account limits unverified.

3. THE PROPOSED ARCHITECTURE (summary of three committed documents)
--------------------------------------------------------------------
3.1 Multi-fidelity evidence tiers
  E exploratory (no custody; never cited) -> S provisional screen (frozen,
  ledgered) -> A qualified assay (preregistered, bound receipts, custody,
  controls) -> C independent challenge (other model family; set committed
  before outcomes) -> R preserved result. Only R is a finding; an E/S number
  in a claim is a defect. Challenges reserved for promoted claims.
3.2 Escalation ladder
  Stage 0 analytical rejection (expressible / reachable / rewarded /
  credited / detected; known-answer construction; simpler-alternative
  failure; ruler detects a planted positive and rejects a near-miss) ->
  1 local CPU -> 2 local GPU (only if measured beneficial) -> 3 bounded
  cloud pilot (operator cap; termination + recovery + accounting) -> 4
  1x/4x/16x distributed comparison -> 5 long-running adaptive research.
  Promotion needs a REGISTERED observation that more budget could reveal a
  new capability (not more fitness).
3.3 Long-duration execution ("the job owns its state")
  Immutable manifest; seed partitions; one checkpoint chain per partition
  published with expected-parent compare-and-set; append-only event and
  attempt ledger; checkpoint bytes in a sha256-addressed retained store;
  workers interchangeable under leases; resume verifies bytes plus a short
  resume-equivalence replay; final account computed from the event log. An
  agent session appears only to freeze the manifest and read the result.
  DEMONSTRATED on one host this week: a runner survived the loss of its
  worker, its supervisor and the launching agent session; a DIFFERENT
  session resumed it from one command line; final digest equal to the
  uninterrupted control (13/13 criteria; 286 CPU-s). Retention policy and
  an idempotent relaunch entry followed (relaunch tested with a SIMULATED
  scheduler; no OS scheduler installed).
  Missing: cross-host transport (planned: port onto a sibling campaign's
  PostgreSQL epoch publication over the same queue), a live worker plane,
  a large-object store reachable from all nodes, engine save/load pairs
  (only 3 of ~11 runtimes checkpoint today without engine edits).
3.4 Compute economy
  Distinguish cost of discovering a candidate from cost of proving it:
  today proof dominates by orders of magnitude (tens of CPU-minutes vs
  hours of reviewer-model time). Account CPU, GPU, memory, storage,
  transfer, tokens, reviewer and engineering time, operator interventions,
  dollars. The ledger now refuses runs that would exceed GPU-hour or dollar
  caps BEFORE they start. No fleet-wide dollar ledger exists yet.
3.5 Renting compute
  Only when (a) Stages 0-2 passed locally, (b) a registered criterion says
  more budget could reveal a new capability -- a rarity barrier, which
  time crosses, not a composition barrier, which it does not (audit), (c)
  the workload batches well, (d) it checkpoints. Counter-example on file: ~3
  weeks of rented GPU on random soup bought near-trivial dynamics.

4. DECISIONS WE BELIEVE ARE RIGHT -- AND WANT YOU TO TRY TO BREAK
------------------------------------------------------------------
  D1 Build no scheduler; build durable run-records and let any worker or
     seat resume. (Risk: we are re-inventing a scheduler badly.)
  D2 Reuse the sibling campaign's PostgreSQL + queue transport instead of
     a new one. (Risk: coupling the Observatory to one engine's plumbing;
     and, as that campaign's owner argues for itself, building cross-host
     transport ahead of any workload that exceeds one host.)
  D3 Keep Git for manifests, hashes, results and provenance only; raw
     evidence in a retained store. (Risk: a store we do not yet have.)
  D4 Reserve independent challenges for promoted claims. (Risk: defects in
     unpromoted machinery leak into promoted claims later.)
  D5 Next engineering investment: cross-host runner port + a registry of
     qualified components whose qualification stage travels with them.

5. HIDDEN SCIENTIFIC RISKS OF DISTRIBUTION WE ALREADY SEE
---------------------------------------------------------
  - Seed partitions resumed on different hosts: is replay bit-identical
    across CPUs/BLAS/numba builds? (Measured only on one host.)
  - Selection over partial runs: an operator or seat that inspects a
    running job's progress events can bias stopping. (Plateau rules must be
    frozen; is that enough?)
  - Interrupted runs: wasted work is accounted, but does interruption
    correlate with outcomes (e.g. long lineages are the ones killed)?
  - Archive / novelty methods are sensitive to evaluation order; does a
    distributed queue change the science?

6. QUESTIONS FOR THE REVIEWER (written to resist agreement)
------------------------------------------------------------
Q1 Coordination latency (69-82% waiting) is our largest measured cost. Is
   the right fix event-driven dispatch, fewer and larger packets, or fewer
   seats? Argue against our D1.
Q2 Is a "qualified component registry" a real lever or bureaucracy that
   will itself need qualifying?
Q3 Which part of the escalation ladder is theatre for a program our size?
Q4 What would you NOT build in the next quarter that we propose?
Q5 Name one distributed-execution failure that would silently corrupt a
   scientific result in this design.

7. SOURCES (for the operator; the reviewer needs none)
-------------------------------------------------------
rso/scale/RSO_SCALING_ASSESSMENT.md; rso/scale/LONG_DURATION_EXECUTION_
ARCHITECTURE.md; rso/scale/PROMETHEUS_SAGACITY_SCALING_ROADMAP.md; rso/
scale/runner/FIRE_TEST.md; rso/scale/CHECKPOINT_REPLAY_SURVEY.md.

+============================================================================+
| "Build less" and "stop" remain first-class answers.                        |
+============================================================================+
