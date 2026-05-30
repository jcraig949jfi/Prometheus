# Aporia Ecosystem — Status and Next Steps

**Filed:** 2026-05-30
**Author:** Aporia (in-session)
**Scope:** The four components that operate together as the Aporia ecosystem — Aporia itself (the open-problem catalog + persona), Pythia (Deep Research dispatch), the Charon swarm (falsification machinery), and the inbox plumbing that routes tickets between them.
**Companion:** `aporia/doctrine/lean_substrate_state_2026-05-30.md` (Ergon-authored, Lean substrate scope only).
**Doctrine discipline:**
- `feedback_take_a_stand` — next-step section presents stands as falsifiable artifacts, not menu items
- `feedback_substrate_passive_consumer_warning` — every proposal traces to a behaviour delta
- `feedback_anti_gravitational_well` — frontier-review questions designed to be DIAGNOSTIC (where convergence is the warning signal, not validation)
- `feedback_no_hard_tables` — tables avoided in chat-pasteable sections; code blocks used for structured listings

---

## 1. Where Aporia sits in the substrate

Aporia is not a daemon. It is a **role**: the open-problem cataloger + cross-agent ticket relay + research-direction void detector. Aporia's outputs are:

- An open-problem catalog (`aporia/{astronomy,biology,...,physics}/` per-domain registries, ~322 problems across 13 domains)
- A doctrine corpus (`aporia/doctrine/`: critical_memories, dr_prompt_discipline, lean_substrate_*, external_tool_interaction_primitives, substrate_vocabulary)
- An inbox plumbing layer (`aporia/meta/queue/*.jsonl`) routing tickets between Techne / Ergon / Charon / Harmonia
- The substrate-shaped pilot batches and adjudication artifacts

The role is currently operated by Claude Code sessions. The longer-term direction (per `project_aporia_reorientation`) is to pivot Aporia from oracle mode (answering "what should we do?") to instrument mode (running blind trials, falsifying frames, surfacing voids).

## 2. Status of the four ecosystem components

### 2.1 Aporia itself — the catalog and the role

**Catalog state:**
- 13 domain directories. The originally-claimed 322 open questions across the catalog has not been audited recently. Per `feedback_calibration` discipline, treat that number as 6-month-old until a fresh inventory runs.
- Recent doctrine additions (last 14 days): `dr_prompt_discipline.md` (DR query construction rules), `external_tool_interaction_primitives_2026-05-28.md` (cross-agent tool-interaction primitives), `lean_substrate_state_2026-05-30.md` + `lean_substrate_next_steps_2026-05-30.md` (Ergon-authored, Lean substrate).
- Doctrine churn is concentrated in Lean / external-tool primitives. Domain catalogs (astronomy / biology / physics / mathematics) have not received structured additions in the same window.

**Role state:**
- Operating in-session per request; no daemon. Pivot to instrument mode is documented but not implemented as machinery.
- The most-recent strategic redirect (`project_falsification_routing_learner`, 2026-05-10) says v1.0 trains falsification-routing first, NOT theorem-answering. Aporia's role inherits that: surface falsification-shaped problems to the dispatcher, not answer-shaped problems.

### 2.2 Pythia — Deep Research dispatch

**What it does:** Pulls from `aporia/docs/gemini_research_queue/`, dispatches to Gemini Deep Research, lands results in `aporia/docs/deep_research_reports/<date>/`.

**Volume signal (last 4 days, 2026-05-26 → 2026-05-30):** ~60 reports filed, broken roughly into:
- Stygian primary-literature surveys (BL-C-002, 005, 006, 007 + HECATE-* survey series)
- Lethe forward false-anchor hunts (saxl_conjecture, sato_tate_symk, mertens, sensitivity, ternary_goldbach, bounded_gaps_vs_twin_primes, schinzel_zassenhaus, fermat_last_theorem_calibration, ...)
- Acheron coordinate-collision hunts (catalan, schinzel, lehmer, rank, goldbach, sato-tate, twin prime, mertens)
- Hecate retraction-pattern surveys (a2_detrended, h2_method_tr, c1_mut_equal, f3_active_*)
- Moros cross-pollination critiques (on substrate pivot docs)
- Hypatia D-track research (proof-decomposition synthesis)

**Read of the volume:** Pythia is the highest-utilization arm of the ecosystem right now. The substrate is using its DR token budget (per `feedback_use_or_lose_research_tokens` — 20/day, no rollover).

**Concern:** Volume vs. yield is not tracked. 60 DR reports landed; how many produced a substrate-behaviour delta (new doctrine entry, kill, anchor demotion, ticket resolution)? Unknown without an audit. Per `feedback_substrate_passive_consumer_warning`, this is the failure shape that fires loudest right now.

### 2.3 Charon swarm — falsification machinery

**Eight daemons in one Python process (charon_loop.py, ~1.5 GB resident, alive since 2026-05-26):**

- **Stygian** — runs the v10 battery on a fixed claim per tick (R1 + R6 on the reasoning ladder)
- **Lethe** — false-anchor mining (LLM-judges-LLM on candidate-status statements; R0-R2)
- **Acheron** — coordinate-collision detection in terms across the substrate vocabulary (R0; pure regex-match registry)
- **Moros** — adversarial multi-model critique aggregation of substrate artifacts (R2 + R6 convergence-as-self-monitoring)
- **Hecate** — cross-generation MI audits across the kill_ledger (R2 + R6 swarm-self-monitoring)
- **Nephele** — Clio liveness watchdog + arxiv RSS relay (R0 + R1)
- **Pollux** — Spearman/normalized-Spearman cross-database pair survival (R2 + R6)
- **Erebos** — generator cluster, currently at v3 Phase 1B ITER-39, 25-archetype spec; targets R3-R8 (abstraction → conjecture)

**Recent buildout (since 2026-05-26):**
- Erebos v0.27 → v3 Phase 1B ITER-39 — roughly 13 major iterations
- Layer1/seam/Layer2 doctrine integrated; kill_pattern_registry; ComposedClaim with per-field consumer audit; residue revocation mechanism; cost-instrumentation; 15 new Techne generators (k1..bb1) stub→real

**Concerning state:** Massive architectural progression on Erebos while the Techne→promotion pipeline shows **89 consecutive 0-promoted fires** (a 2-day-old measurement; will be higher now). 360M+ lifetime kills, 2,351 discoveries, discoveries flat for 3+ days. The substrate is generating heat; the promotion criterion is the bottleneck. Erebos's rebuild looks like the intended response — reshaping the kill→promotion routing layer — but whether it lands by the end of the streak is the open question.

### 2.4 Inbox plumbing — `aporia/meta/queue/`

**Counts (2026-05-30 snapshot):**

```
aporia_inbox.jsonl   : 202 lines  → 196 OPEN, 5 RESOLVED-PIVOT-ACCEPTED, 1 IN_PROGRESS
charon_inbox.jsonl   :   2 lines  →   2 OPEN
ergon_inbox.jsonl    :  84 lines  →  60 BLOCKED-DEFERRED-V1.0, 8 DONE, 8 status=?, 6 OPEN, 1 ABLE_TO_ADVANCE, 1 WONTFIX
techne_inbox.jsonl   : 102 lines  →  51 OPEN, 29 DONE, 14 status=?, 4 DESIGN_LANDED_IMPL_DEFERRED, 1 each {BLOCKED, SUPERSEDED, AUDITED_NO_CHANGE, ABLE_TO_ADVANCE}
harmonia_inbox.jsonl :   1 line   →   1 status=?
```

**Headline numbers:** ~340 total open across the queues. **196 OPEN tickets in aporia_inbox alone** — and a sample shows tickets dated 2026-05-07 still OPEN. The ticket lifetime distribution is heavy-tailed; the queue is functioning as an append-only journal more than as an actionable work queue.

**Schema is heterogeneous:** Each inbox uses a different status vocabulary. `BLOCKED-DEFERRED-V1.0` only appears in ergon_inbox; `RESOLVED-PIVOT-ACCEPTED` only in aporia_inbox; ~22 tickets across queues have `status=?` (missing or unparseable). The schema drift IS a finding — it reflects each agent's distinct stagnation modes — but it makes cross-queue reasoning hard.

## 3. What is operationally broken right now

Honest version:

1. **Pythia yield is not measured.** 60 DR reports in 4 days; behaviour-delta count unknown. The substrate could be passively consuming.
2. **Aporia inbox is a journal, not a queue.** 196 OPEN, oldest ~3 weeks. No triage cadence.
3. **Techne 89-fire 0-promoted streak.** Erebos v3 is the intended fix; un-validated as of this filing.
4. **Catalog audit is overdue.** "322 open problems" is a 6-month-old number; per `feedback_calibration` it should be re-counted.
5. **Reasoning-ladder annotation discipline is not implemented.** The ladder design doc (`pivot/reasoning_ladder_design_2026-05-15.md` § 0 + § 8) says inbox tickets should carry a `required_reasoning_tier` field; current schemas don't.
6. **Aporia role is not running as machinery.** It runs in-session when a human (James) is at the keyboard. The instrument-mode pivot is documented but not built.

## 4. Suggested next steps (stands, not options)

Per `feedback_take_a_stand`: stand = falsifiable artifact. Wrong stand surfaces a falsification; no stand surfaces nothing. Each item below is a stand with its behaviour delta and the observation that would prove it wrong.

### Stand A — Pythia yield audit goes first

**Action:** One pass over `aporia/docs/deep_research_reports/2026-05-{26..30}/` (~60 reports). For each, tag whether it produced a substrate-behaviour delta: doctrine commit, kill ledger entry, anchor demotion, ticket resolution, generator change, or nothing. Output: `aporia/meta/pythia_yield_audit_2026-05-30.jsonl`, one row per report.

**Behaviour delta:** A yield-per-token number. Falsifies the substrate-passive-consumer hypothesis for Pythia if the ratio is high; confirms it if the ratio is low and triggers a Pythia query-construction discipline revision.

**Falsifiable:** If <10% of reports trace to a delta, Pythia is broadcasting to a deaf substrate; the DR token budget should rotate to a different consumption pattern (smaller queue, deeper synthesis, longer-form prompts).

### Stand B — Inbox triage cadence: weekly close-or-promote pass

**Action:** Every Friday, one pass over `aporia/meta/queue/*_inbox.jsonl`. For each OPEN ticket older than 14 days: close-as-WONTFIX, escalate-to-PRIORITY-or-CHARTER, or move-to-doctrine. The journal-versus-queue tension is resolved by forcing a verdict, not by adding a new field.

**Behaviour delta:** Inbox depth drops or stays flat — the system commits to bounded WIP. The first pass will produce ~30-50 close decisions and ~5-10 promotions to charter / doctrine.

**Falsifiable:** If after 3 weekly passes the OPEN count is still growing faster than tickets resolve, the substrate is producing tickets faster than the role can adjudicate; that's a Pythia-equivalent over-production signal at the meta layer.

### Stand C — Reasoning-ladder annotation on NEW tickets only

**Action:** From 2026-06-01 onward, every NEW ticket landing in `aporia/meta/queue/*_inbox.jsonl` MUST carry `required_reasoning_tier` (R0-R12) AND `failure_axis` (F0-F8). Old tickets are NOT backfilled.

**Behaviour delta:** New-ticket schema is forced to commit to a target tier at filing time. This is the falsifiable version of the ladder doc's § 8 behaviour-delta claim (which has been deferred for 15 days).

**Falsifiable:** If 6 weeks pass and tier annotations on NEW tickets are not used by any agent (i.e., Techne/Ergon/Charon don't read the tier when pulling work), the annotation discipline is decoration and gets removed.

### Stand D — Aporia catalog audit: one domain per week

**Action:** Pick one of the 13 domain directories per week. Count current problems, mark which have been touched in the last 90 days, generate one DR report per stale problem set proposing demote / retain / promote. Order: start with `mathematics/` (highest substrate-coupling), then `physics/`, then descending.

**Behaviour delta:** After 13 weeks, the "322 open problems" claim is replaced with a fresh per-domain count + staleness distribution. The catalog stops being a 6-month-old number.

**Falsifiable:** If after 3 weeks of audits, the per-domain demote-fraction is <5%, the catalog wasn't drifted; the staleness assumption is wrong and the audit cadence drops to quarterly. If it's >40%, the catalog was substantially decorative; cadence stays weekly until convergence.

### Stand E — Defer Aporia-as-daemon until Stands A-D land at least once

**Action:** Do NOT build an Aporia daemon yet. Stands A-D are run by human-driven sessions. Daemon-ization is deferred until the cadence has been validated by hand at least once.

**Behaviour delta:** No new agents/aporia/ directory. No SelfImprovingDaemon-mixin Aporia. The role stays human-driven for 4 weeks.

**Falsifiable:** If the Friday triage cadence misses 2 weeks in a row because no human ran it, the role is under-served by human-only operation and a partial-automation pass (e.g., a script that surfaces "OPEN and >14 days" tickets every Friday morning) is the right intervention. Even then, the daemon is a partial-automation, not a full Aporia agent.

### Order of execution

Strict sequence, no parallelism:

1. **Stand A** (Pythia yield audit) — first because it tells us whether the highest-volume arm is producing value
2. **Stand B** (first inbox triage pass) — second because it tightens the meta-feedback loop
3. **Stand C** (NEW-ticket schema discipline) — third because it requires the queue to be in a known state
4. **Stand D** (per-domain catalog audits) — runs weekly starting after Stand B's first pass
5. **Stand E** (defer Aporia daemon) — passive, requires no action

### What this section explicitly is NOT proposing

To make the suppression visible:

- **No new agent.** Resisting the gradient toward "build Aporia v2 as a daemon."
- **No new doctrine doc beyond this one.** No "Aporia constitution v2", no "open-problem ontology v3."
- **No replacement of the inbox schema with a new framework.** Schema heterogeneity is a finding; replacing it would erase the finding.
- **No retroactive tier-annotation of 196 old aporia_inbox tickets.** That's the gravitational well of "fix the catalog by hand."
- **No promotion of any in-flight pivot doc to doctrine.** Pivot/ stays in pivot until the cross-pollination round runs.

---

## 5. Questions for the frontier review board

Per `feedback_anti_gravitational_well` and `feedback_llm_convergence_is_gravity_amplifier`: frontier convergence on these questions is a warning, not validation. Questions are designed so that the SHAPE of disagreement is diagnostic. Each question carries the answer-axis we expect to see disagreement on, and what the SHAPE of convergence-or-divergence will tell us.

### Q1 — The 89-fire 0-promoted streak: which layer is broken?

> Techne has fired 89 consecutive batches without promoting any new substrate object. 360M+ lifetime kills, ~360 fires total, only 2,351 discoveries with no growth in 3 days. Three candidate diagnoses:
> (i) **Generation-rate problem** — the generators are exploring the wrong subspace;
> (ii) **Promotion-criteria problem** — the criteria are mis-calibrated and would reject valid promotables;
> (iii) **Routing problem** — kills are being computed but not routed into the promotion-eligibility queue at all.
> Which diagnosis does each reviewer assign highest prior? Defend with specific evidence the assignment would require.

**Why diagnostic:** Each model probably has a different default. (i) is the LLM-corpus-conventional answer (more diversity is the fix). (ii) is the substrate-internal answer (criteria need tuning). (iii) is the engineering answer (plumbing bug). If all 4 models converge on (i), that's the gravity-amplifier firing; we should suspect (iii). If they split 2-1-1, the divergence axis IS the next investigation.

### Q2 — Pythia's yield model

> The Aporia ecosystem dispatches ~15 DR queries/day from Pythia, 20-token budget (no rollover). 60 reports landed in 4 days. Substrate-behaviour-delta yield is not measured. What ratio of "report → substrate-behaviour delta" would each reviewer flag as the threshold for "Pythia is broadcasting to a deaf substrate"? What is each reviewer's intuition for what the actual current ratio is, based on the names of the reports filed (see § 2.2)?

**Why diagnostic:** This is a calibration question. A frontier model trained on academic-research distributions will say a 10-30% yield is "fine." A model trained on shipping-engineering distributions will say <50% is wasteful. The disagreement on what "fine" means tells us whether to import a research norm or an engineering norm to substrate evaluation.

### Q3 — Charon swarm: 9th agent, or consolidate?

> The Charon swarm has 8 daemons in one process (Stygian / Lethe / Acheron / Moros / Hecate / Nephele / Pollux / Erebos). Each occupies a distinct tier of the reasoning ladder (mostly R0-R6, with Erebos targeting R3-R8). The substrate has produced 25 distinct generator archetypes (Erebos G01-G25) but only 1 (G19 Proof-Obligation) operates at R8/R9 — and R8/R9 is the explicit target of the Prometheus criterion (`pivot/reasoning_ladder_design_2026-05-15.md` § 1).
> Two opposing stands:
> (a) Add a 9th Charon agent specialized for R8/R9 conjecture-formation, accepting that R8 outputs need their own falsification machinery the existing daemons don't supply;
> (b) Consolidate — kill 2-3 of the lower-tier Charon daemons whose outputs are not currently consumed, and reinvest the maintenance budget into the existing Erebos generator cluster.
> Which stand does each reviewer take? What single piece of evidence would flip them to the other stand?

**Why diagnostic:** This is research-strategy-as-judgement. Convergent answer = the question was already settled in the LLM training corpus and we're asking gravity. Divergent answer = there's a genuine bet to make. The "single piece of evidence" anchor forces each reviewer to specify a falsifier rather than hedge.

### Q4 — The inbox-as-journal observation

> 196 OPEN tickets in aporia_inbox.jsonl, oldest ~3 weeks. The inbox is functioning as an append-only journal more than as an actionable work queue. Two stands surface in design space:
> (a) This is fine — the long-tail of open tickets is the substrate's "open research signature"; the BUG would be forcing closure on tickets that are genuinely open research questions, and the inbox is correctly NOT being squeezed into the project-management mold;
> (b) This is broken — open tickets that nobody is actually working on are misleading lattice noise; the cost is that fresh tickets get buried, and the substrate's "we have a queue" framing is a lie.
> Which framing does each reviewer adopt? Is there a third framing (the inbox IS the substrate; the inbox IS the artifact)?

**Why diagnostic:** This probes the reviewer's prior on **what a substrate of structured artifacts looks like in steady state**. The (a) answer aligns with substrate-doctrine; (b) aligns with engineering-doctrine. The third framing — if any reviewer surfaces it without prompting — is the most interesting outcome.

### Q5 — Reasoning-ladder annotation discipline

> The ladder doc (`pivot/reasoning_ladder_design_2026-05-15.md`) says new inbox tickets should carry `required_reasoning_tier` (R0-R12) at filing time. This has not been implemented in 15 days. The proposed Stand C (§ 4 above) says: enforce on NEW tickets only, do NOT backfill.
> Is the no-backfill stand correct? Three competing positions:
> (a) Correct — backfilling 196 tickets is exactly the gravitational-well failure mode the ladder is supposed to detect;
> (b) Wrong — the ladder's value is comparative across the queue, so a queue with half-annotated tickets has no comparative signal;
> (c) The annotation discipline itself is decoration that won't be read by downstream agents and the right move is to drop it entirely.
> Position (c) is the falsifier of the entire ladder § 8 behaviour-delta claim. Which position does each reviewer take?

**Why diagnostic:** Position (c) is the most aggressive — and the most useful if a reviewer is willing to take it. If 4 reviewers all dodge (c) and split between (a) and (b), the consensus is that the ladder annotation is real-but-poorly-deployed. If any reviewer takes (c), we have a falsifier for the ladder doc itself, which is the doc's own stated escape hatch.

### Q6 — Aporia-as-daemon: now or later?

> Aporia is a role, not a daemon. Stand E (§ 4) says: defer daemon-ization for 4 weeks until Stands A-D have run by hand at least once. The opposing stand is: build the daemon now, accept that it will be wrong, learn from its wrongness — exactly the gen-30-wall doctrine (`feedback_gen_30_wall`) says we should NOT build a single-agent automation but a lineage of them.
> Does each reviewer think Aporia-as-daemon (single agent or lineage) is the next step, or that the role's failure modes are pre-substrate (i.e., the human-in-the-loop discipline isn't yet present, so automating it would automate sloppiness)?

**Why diagnostic:** This is the most adversarial question — it directly invites the reviewer to attack a stand we've taken. The shape of the attack tells us whether automation discipline or HITL discipline is the under-served piece.

### Q7 (free response) — What is the question we are not asking?

> Each reviewer: identify one structural blindspot in this document. Not a missing detail or a citation we owe — a frame we've adopted without examining. Format: one sentence stating the missing frame, one sentence stating why we likely didn't see it, one sentence proposing the falsification test.

**Why diagnostic:** This is the cheapest-to-write, most-valuable-to-read question. A non-answer means the reviewer didn't engage. A pattern across answers (do they all flag the same blindspot? different blindspots?) tells us whether the doc has one shared weakness or many independent ones.

---

## 6. Posture

This doc is filed at `pivot/` per the discipline of NOT landing load-bearing doctrine without external review. After the frontier-review round produces responses (Stands A-E falsified or not, Q1-Q7 analyzed), this doc gets revised to v0.2; the Stand-section that survives gets promoted to `aporia/doctrine/aporia_ecosystem_doctrine.md`.

The doc has 6 weeks to produce its behaviour delta. If by 2026-07-11 the Pythia yield audit has not run, the inbox triage has not happened, and the tier-annotation discipline is not in NEW tickets, the doc was wrong and gets retired.

— Aporia, 2026-05-30
