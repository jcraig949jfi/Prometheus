# Harmonia auto-promotion targets

**Status:** DRAFT v0.2 — post-review, open for further external review
**Date:** 2026-05-22
**Scope:** Auto-promotion pipeline design for the five Harmonia child-agents (Phylax, Sophia, Iris, Argos, Telos) in Project Prometheus
**Authors:** Harmonia (Claude Code agent), with James Craig
**Reviewers (v0.1 → v0.2):** External review 2026-05-22 (10 substantive changes incorporated; see §13)
**Related:** `D:\Prometheus\harmonia\agents\ROADMAP.md` (cross-cutting upgrades), per-agent `README.md` files

---

## TL;DR

The Harmonia swarm produces ~440 well-formed artifacts per agent per ~54-hour cycle (~2200 artifacts total, zero errors). Of those, approximately **one** has been read and acted on by a downstream actor. The remaining ~2199 sit on disk as "production" but practically as noise. This document proposes an auto-promotion pipeline that converts a graded subset of those artifacts into formal substrate-state changes (anti-anchor candidates, symbol candidates, lens catalogs, calibrated scorer candidates, specimen attention-state changes) automatically, with explicit reversibility AND taint tracking for every promotion.

The pipeline is **five typed micro-pipelines sharing a scoring primitive, a yield log with taint paths, and a doctrine-versioning gate**, not a single generic consolidator. Each micro-pipeline has its own scoring function, auto-promotion threshold, kill-path, taint-path, and target weekly throughput. Anti-capture safeguards are stronger here than for human-curated promotion, not weaker, because the F043-class failure mode (a definitionally-tautological correlation promoted as a finding) becomes more dangerous at machine speed.

**Reframing from v0.1**: the design question is no longer "Can we safely auto-promote?" but **"Can we compress machine production into high-value, reversible, taint-tracked substrate updates without poisoning future routing?"** The shift acknowledges that reversibility ≠ low epistemic blast radius — reverting a bad promotion restores file state, but it does not fully restore downstream attention, scorer labels, learned priors, or recency caches that consumed the bad state.

Empirical first deliverable: the **Iris → CANDIDATES.md** pipeline as proof-of-concept (lowest blast-radius — note: this is the candidates file, not a real symbol promotion, which still requires human review). Validated by a 2-week observation window with attention-compression metrics: ≥10 of 50 auto-promotions judged worth-keeping, ≥1 clears to a real symbol, ≤2 template artifacts, ≤60 minutes total human review time, ≤5% auto-promote false-positive rate.

---

## 1. Background

### 1.1 Project Prometheus in one paragraph

Prometheus is a falsification-first reasoning substrate for automated mathematical discovery. The core thesis is that generative variance (what users call hallucinations) becomes the engine of evolutionary search when paired with ruthless mechanistic selection. Hypotheses are forced through a deterministic battery of tests that produce structured `KillVector` records describing exactly how each claim broke. Survivors `PROMOTE` to substrate state; the kill-pattern geometry over the ~314K logged kills becomes a navigable gradient field over discovery space. The full thesis lives at `D:\Prometheus\README.md`.

### 1.2 The Harmonia swarm in one paragraph

Harmonia owns substrate architecture and Σ-language grammar within Prometheus. The Harmonia swarm is five autonomous child-agents running under a single rotation orchestrator (`D:\Prometheus\scripts\harmonia_loop.py`), each with a tightly-scoped charter. They tick at 90-second intervals via a Windows-detached daemon launcher. Each agent reads from substrate state (files, the Agora Redis-backed message bus, the Postgres-backed Aporia research queue) and writes proposal artifacts to a per-agent `artifacts/` directory. The five agents are: **Phylax** (pre-promotion gate + retraction-adjacency sentinel), **Sophia** (coordinate-system scout), **Iris** (prose-to-symbol compressor), **Argos** (lens-catalog expander), **Telos** (stalled-specimen reviver). Per-agent details in `D:\Prometheus\harmonia\agents\<name>\README.md`.

### 1.3 The substrate vocabulary (what auto-promotion targets)

The current Prometheus substrate vocabulary (per `D:\Prometheus\aporia\doctrine\substrate_vocabulary\`, v0.1.0) is a 5-layer typed action space:

| Layer | Content | Current count | Storage |
|---|---|---|---|
| Primitives | Witnesses, certificates, invariants, networks (Tier-A++ through Tier-E) | 22 specs | `aporia/doctrine/substrate_vocabulary/primitives/` |
| Attacks | Paradigms P00–P32+ with sub-tactics | ~20 | `aporia/doctrine/substrate_vocabulary/attacks/` |
| Patterns | Failure-mode detectors | 5 mandated + 3 candidates | `harmonia/memory/pattern_library.md` |
| Anti-anchors | Pinned false claims with primary-source refutations | 12 entries | `techne/registry/anti_anchors.jsonl` |
| Composition rules | Cross-tier grammar | 2 confirmed + 5 candidates | `aporia/doctrine/substrate_vocabulary/composition_rules/` |

Additionally, Harmonia maintains:

- 24 promoted symbols (operators, shapes, constants, datasets, signatures, patterns) at `harmonia/memory/symbols/`
- A retraction registry of 9 entries + 4 cross-cutting failure-mode patterns at `harmonia/memory/retraction_registry.md`
- A coordinate-system / methodology toolkit shelf of 10 operators at `harmonia/memory/methodology_toolkit.md`
- Per-problem lens catalogs (Lehmer 28 lenses, Collatz 18 lenses, P-vs-NP 12-lens sketch) at `harmonia/memory/catalogs/`
- A frontier specimen state index (~14 active F-IDs, ~30 killed F-IDs) at `harmonia/memory/frontier_specimen_state.md`

Auto-promotion writes into these structures (with the safety stratification described in §5 — most pipelines write to a `_candidates.jsonl` shadow before any move to the canonical registry).

### 1.4 The F043 anchor lesson

On 2026-04-19, a finding labeled F043 ("BSD-Sha anticorrelation") was promoted to `live_specimen` tier based on a correlation observation across an elliptic-curve ensemble. Within 24 hours, cross-checking against the `PATTERN_BSD_TAUTOLOGY` precondition revealed that the "anticorrelation" was a definitional consequence of how the BSD ingredients are defined (an algebraic identity, not an empirical regularity). F043 was retracted, re-classified as Pattern-30 Level 4 (IDENTITY), and the finding became the load-bearing anchor case for the graded algebraic-identity coupling discipline now codified at `harmonia/memory/symbols/PATTERN_30.md`.

The F043 retraction cost approximately 12 person-hours of substrate state revertal plus the credibility cost of having promoted a tautology. **Auto-promotion at machine speed cannot afford even one F043-class event per week**, which is why the design weights anti-capture safeguards more heavily than human-curated promotion does. **Crucially (v0.2 strengthening):** the F043 retraction was cheap because Harmonia caught it within 24 hours, before downstream agents had reasoned about it. Auto-promotion at scale can leak bad state into yield-log training labels, scorer priors, recency caches, and downstream agent prompts faster than the kill-path can retract. The taint-path mechanism (§6.4) addresses this.

### 1.5 The Aporia DR-prompt discipline

A doctrine document (`aporia/doctrine/dr_prompt_discipline.md` as of 2026-05-19; not yet pushed to the main repo as of this writing) governs how swarm agents enqueue Pythia Deep Research requests. The five compliance requirements are:

1. Requester named explicitly in prompt body (not just via `requested_by` field)
2. Substrate type tagged (A = falsification data, B/C/D = attack-angles / paradigm refinements / step-decompositions)
3. Verification criterion stated (citation requirements, recency cutoff, distinguish-X-from-Y)
4. Landing path declared (which catalog or registry the finding goes into)
5. Recency-collision check (no re-fire on a topic DR'd in the last 7 days)

Both Argos and Phylax already comply with this discipline. Auto-promotion piggybacks on this existing infrastructure. **v0.2 adds:** doctrine version is a required field in every yield row for DR-dependent pipelines (§4.4) — if Aporia changes the doctrine, the pipeline refuses promotion until reconciled.

---

## 2. Motivation: the empirical consumption gap

After ~54 hours of continuous operation (2026-05-19 22:21 EDT → 2026-05-22 ~04:30 EDT), the swarm has produced:

| Agent | Artifacts | Daily rate | Of those, acted on |
|---|---|---|---|
| Phylax | 456 | ~200/day | 0 (1 if you count smoke-test DR 243) |
| Sophia | 438 | ~200/day | 0 |
| Iris | 438 | ~200/day | 0 |
| Argos | 438 | ~200/day | 1 (DR 243 happens to be from Argos's pipeline via Phylax) |
| Telos | 440 | ~200/day | 0 |

Aggregate downstream-action rate: **0.045%** of produced artifacts have been read and acted on by a non-Harmonia downstream consumer within their TTL.

**The diagnosis:** production is solved (the agents work). Consumption is the bottleneck. Scaling production further without solving consumption produces N× more unread artifacts. The right move is to close the production→promotion loop at current production rate first, then scale.

**The reframing (v0.2):** the goal is not "more promotions per week" but "**higher marginal-substrate-value per conductor minute**." A doubling of promotion count with zero value-per-promotion is a regression, not progress. The system must compress production into value, not into volume (§6.6).

---

## 3. Goals and non-goals

### Goals

1. **Convert raw agent artifacts into substrate-state changes automatically**, with measurable weekly throughput against quantified targets (§5.1).
2. **Reduce the human-review burden** from "30+ min/day of manual artifact triage" to "≤10 min/week of audit-log review," and equip the human reviewer with tight tooling (Phase 0.5, §7).
3. **Maintain reversibility AND taint tracking** for every auto-promotion via explicit kill-path AND taint-scope artifacts written at promote-time (§6.1, §6.4).
4. **Generate the yield-log substrate** that future learned scorers train against — with seven distinct label classes that distinguish active acceptance from passive TTL survival (§4.2, §6.5).
5. **Validate the pattern at small scale** (one agent, two-week observation window, attention-compression metrics) before extending to all five.
6. **Track marginal substrate value** for every promotion on a 0-5 ordinal scale (§6.6) so the system cannot Goodhart toward cheap promotions.

### Non-goals

1. **Not** generating more artifacts per tick. Production rate stays at current 90s-interval baseline.
2. **Not** replacing human review of substrate-grade scientific claims. Promotions to `Validated` tier (the highest precision tier in `harmonia/memory/feedback_precision_standard.md`) remain human-only. Anti-anchor and AXIS_CLASS promotions are split into candidate-tier (auto) and registry-tier (human-gated) per §5.2 and §5.5.
3. **Not** scaling backlog size yet. The "heat-death-scale backlogs" thesis from prior session notes is the next horizon, contingent on this consumption layer working AND on the yield log demonstrating that auto-promotion improves Prometheus's epistemic state, not merely making the filesystem look more alive.
4. **Not** auto-modifying any file under `aporia/doctrine/substrate_vocabulary/` (those are versioned externally and require explicit human review).
5. **Not** sharing scoring state with Charon's swarm in v0.2. (But cross-swarm taint propagation IS acknowledged at §6.4 — if Phylax's auto-promoted candidate is consumed by Charon's Stygian, the taint scope must record that consumer even though no Charon code lives in this proposal.)

---

## 4. Design overview

The auto-promotion pipeline has four components in v0.2 (one new since v0.1):

### 4.1 The scoring primitive (`harmonia/agents/_scorer.py`)

A shared three-tier ranking pipeline used by all five agents:

```
Tier 0  Cheap hard-filter pre-filter
        Hand-crafted rules kill obvious noise. ~99% of candidates die here.
        Implementation: per-pipeline regex / type-check / recency-collision
        against the recent yield-log AND TEMPLATE-SUPPRESSION GATES (§5.3).
        VETO POWER: Tier 0 always overrides Tier 1 + Tier 2 recommendations.

Tier 1  Transparent hand-scored rank (Phase 1) → learned model (Phase 3+)
        Per-pipeline deterministic scoring rule in Phase 1; no learned
        model until labels demonstrate stability (Phase 2 gate).
        Outputs a numeric score per candidate.

Tier 2  Epsilon-greedy / UCB1 bandit allocation (active from Phase 1
        with high-explore configuration; risk-coded per below)
        The bandit recommends which Tier 1 survivor to promote first
        when multiple clear the threshold in the same tick. Recommendation
        is VETO-ABLE by Tier 0 — bandit cannot override hard filters.
```

**v0.2 post-review (James direction):** rather than disabling Tier 2 in Phase 1, the bandit stays active from day 1 with explicit risk-mitigation coding. The reviewer's correct concern (bandits optimize toward reward; reward might be miscalibrated) is addressed by *coding for those risks*, not by avoiding the tool:

**Bandit risk-mitigation code (mandatory from Phase 1):**

1. **High initial explore rate.** `epsilon` starts at **0.50** (50% of arm-pulls are random exploration) for the first 50 promotions per pipeline. Drops to 0.30 at 100, 0.20 at 200, 0.10 at 500. Hard floor of 0.10 — the bandit never goes below 10% exploration.

2. **Multi-objective reward signal.** Reward is not raw promotion count. It is:
   ```
   reward = marginal_substrate_value
          - taint_cost_penalty
          - retraction_penalty_if_subsequently_retracted
   ```
   where `taint_cost_penalty` is proportional to the cardinality of `taint_scope.readable_by_agents` × `taint_scope.downstream_slots` (a wider blast radius costs more reward). This means a low-value promotion with wide taint blast pays negative reward even if it isn't retracted.

3. **Per-pipeline isolation.** No cross-pipeline reward sharing in Phases 1-3. Each pipeline has its own bandit instance, its own reward distribution, its own confidence intervals. Cross-pipeline reward sharing is a Phase 4+ option contingent on `marginal_substrate_value` calibration being stable across at least two pipelines independently.

4. **Forced exploration of underrepresented arms.** If a pipeline's arm has not been pulled in 14 days, the next tick force-pulls it (overrides epsilon-greedy). Prevents lock-in on a local optimum when the reward signal is noisy.

5. **Calibration anchor pull-in (daily).** Once per day, the bandit runs against a fixed set of known-good and known-bad past promotions (the calibration set from §6.6). If the bandit would promote a known-bad case OR demote a known-good case incorrectly, an alert event fires (`scorer_self_quiesce`) and the pipeline pauses promotion until the conductor reviews.

6. **Confidence bound exposure.** Every bandit recommendation emits an event including the arm's reward estimate, confidence interval, and pull-count. High-uncertainty arms (low pull-count or wide CI) get a UCB1-style boost rather than a "play it safe" demotion — so uncertain arms get attention sooner, not later.

7. **Tier 0 veto.** Bandit may rank arm A above arm B, but if A fails any Tier 0 hard filter (template-suppression, doctrine-version mismatch, recency collision), B promotes instead. Bandit never overrides hard safety filters.

**Why bandit-from-day-1 is the right move:** the reviewer's framing ("bandits optimize toward reward; your doctrine prevents reward-capture") is too sweeping. A bandit can optimize for ANY reward signal — including `marginal_substrate_value - taint_cost`, which is exactly the signal we want to maximize. The danger is not the tool; it is the reward signal. We code defensively around the reward signal (multi-objective, calibration-checked, taint-penalized) rather than refusing the tool. This also makes the system produce richer training signal earlier — every bandit pull is a labeled experiment, even when the label is "explored randomly and got value 0."

### 4.5 Structured logging requirements (NEW IN v0.2, post-review)

Every tool in the Harmonia auto-promotion pipeline — current and future — emits structured events to a swarm-wide log channel. This is a forward-going requirement: any future tool we add (consolidator, yield-tracker, triage, auto-promoter, cross-swarm bridge) inherits this contract.

**Why:** wins, losses, and tool maturation must be visible without manually opening artifact files. Structured logging is the orchestration substrate; analysis and reporting consume it as a stream.

**Channel:** `D:\Prometheus\harmonia\agents\_logs\events.jsonl` (append-only JSONL on disk) AND `agora:harmonia_events` Redis stream (for real-time consumers like Aletheia's dashboard).

**Event row schema (all fields required):**

```json
{
  "ts": "2026-05-22T13:45:11.234567+00:00",
  "agent": "iris",
  "event_class": "autopromote_committed",
  "event_data": { ... per event_class ... },
  "correlation_ids": {
    "tick_id": "550e8400-e29b-41d4-a716-446655440000",
    "artifact_id": "candidate_block_shuffle_null_replay_20260522T134402Z",
    "yield_id": "yields-row-1234"
  },
  "schema_version": "events.v1"
}
```

**Event classes (initial v0.2 set; extensible):**

| Class | Volume | Meaning |
|---|---|---|
| `tick_start` | per tick | Agent began its run_tick |
| `tick_complete` | per tick | Agent finished; carries stats |
| `tier0_reject` | per candidate | Tier 0 hard filter killed the candidate; carries which rule fired |
| `tier1_scored` | per candidate | Tier 1 produced a numeric score |
| `bandit_arm_pulled` | per pick | Bandit selected an arm; carries reward estimate + CI + pull-count |
| `autopromote_proposed` | per promotion | Pipeline proposed a promotion (pre-commit) |
| `autopromote_committed` | per promotion | Promotion written to substrate slot |
| `autopromote_aborted` | per failed promotion | Pre-commit check failed (no kill-path constructible, taint-scope incomplete, etc.); carries reason |
| `kill_path_written` | per promotion | Kill-path artifact created |
| `taint_scope_written` | per promotion | Taint-scope recorded |
| `outcome_observed` | per yield outcome | One of seven outcome classes resolved |
| `marginal_value_assigned` | per review | Conductor tagged a value 0-5 |
| `retraction_triggered` | per retraction | Trigger spec fired |
| `taint_sweep_started` | per retraction | Sweep task enqueued |
| `taint_sweep_complete` | per sweep | Sweep finished; carries findings count |
| `doctrine_version_check` | per DR-dependent promotion | Version validation pass or fail |
| `calibration_run` | daily | Scorer self-calibration ran; carries pass/fail per anchor |
| `scorer_self_quiesce` | rare | Scorer detected drift; pipeline paused |
| `weekly_report_emitted` | weekly | Weekly aggregation report ran |

**Consumer pattern:** events are consumed by (a) `scripts/harmonia_summary.py` for the daily snapshot, (b) `scripts/harmonia_weekly_report.py` (NEW, §6.7) for the weekly maturation roll-up, and (c) Aletheia's dashboard via the Redis stream. New consumers can subscribe without coordination with the producer — the JSONL is append-only and the Redis stream supports multiple readers.

**Implementation requirement:** the scoring primitive (`_scorer.py`) ships with an `emit_event(event_class, event_data, **correlation_ids)` helper. Every agent's auto-promotion code path calls this helper at every event point. Code review of any new tool checks for emission coverage; missing events on the critical path is a blocking issue.

### 4.2 The yield log (`harmonia/agents/_logs/yields.jsonl`)

JSONL append-only stream. One row per downstream action that closes the loop on an artifact:

```json
{
  "agent": "iris",
  "artifact_path": "D:\\Prometheus\\harmonia\\agents\\iris\\artifacts\\candidate_block_shuffle_null_replay_20260522T134402Z.md",
  "action": "auto_promoted_to_candidates_md",
  "action_at": "2026-05-22T13:45:11+00:00",
  "auto_promote_score": 0.78,
  "tier1_method": "rule-based-v0.2",
  "kill_path": "D:\\Prometheus\\harmonia\\agents\\iris\\state\\dismissed_candidates.json",
  "taint_scope": {
    "readable_by_agents": ["iris", "argos"],
    "downstream_slots": ["harmonia/memory/symbols/CANDIDATES.md"],
    "used_for_training": false,
    "recency_keys_written": ["symbol:block_shuffle_null_replay"],
    "requires_taint_sweep_on_retract": true
  },
  "doctrine_version": null,
  "outcome": null,
  "outcome_observed_at": null,
  "marginal_substrate_value": null
}
```

**New fields in v0.2 (per reviewer §10):**

- **`taint_scope`** (§6.4) — declares what files, logs, queues, scorer labels, and recency caches may consume this promotion. Required at promote-time; if the agent cannot construct it, the promotion aborts.
- **`doctrine_version`** (§4.4) — required for DR-dependent pipelines (Phylax, Argos); null is allowed for pipelines that don't depend on the Aporia DR doctrine (Iris, Sophia, Telos).
- **`outcome`** — one of seven values, not three (see §6.5 for full semantics).
- **`marginal_substrate_value`** (§6.6) — 0-5 ordinal; filled in by the conductor at review time. Drives the anti-Goodhart scoring.

**Yield log as substrate-vocabulary artifact (new in v0.2):** once `yields.jsonl` accumulates ≥1000 rows, the patterns within it — what scoring features predict acceptance, which agents have which taint propagation depth, which TTLs are too short or too long — are themselves typed structure. The log is not a throwaway training set; it is a candidate substrate primitive. Future v0.X may promote derived patterns to `META_*` symbols (e.g., `META_AGENT_YIELD_PROFILE@v1`, `META_TAINT_PROPAGATION_DEPTH@v1`).

Bootstrapping: for the first ~50 records, the conductor does a daily review pass tagging promotions with both `outcome` (one of seven classes) and `marginal_substrate_value` (0-5). After that, the auto-retraction triggers + 30-day timeouts handle most records automatically, but `marginal_substrate_value` requires human input.

### 4.3 Per-agent auto-promotion pipelines (five micro-pipelines)

Each agent's `<agent>/daemon.py` is extended with an `_autopromote()` method that runs after `run_tick()`. The method reads the artifacts directory, applies the agent-specific Tier 0 + Tier 1 scoring (per §5), and for survivors above the auto-promote threshold:

1. Writes the substrate-state change (the actual promotion, or a `_candidates.jsonl` shadow entry per §5.2 / §5.5)
2. Writes the kill-path artifact (the exact undo command + trigger spec)
3. Writes the taint-scope record (what may consume this; §6.4)
4. Appends a row to `yields.jsonl`

If no candidate clears the threshold, the method writes nothing. The pipeline is idempotent: re-running it on the same artifact set produces no new promotions.

### 4.4 Doctrine versioning gate (new in v0.2)

Per the reviewer's open question #6 from v0.1 and the open risk noted in §1.5: any pipeline relying on the Aporia DR-prompt discipline (currently Phylax and Argos) records the doctrine version in the yield row and refuses promotion if the doctrine version field is missing, stale (> 30 days old without explicit re-confirmation), or incompatible with the pipeline's required-version range.

Implementation: each DR-dependent pipeline declares `MIN_DOCTRINE_VERSION` and `MAX_DOCTRINE_VERSION` constants. At promote-time, the pipeline reads `aporia/doctrine/dr_prompt_discipline.md` frontmatter for the version, validates against its declared range, and either proceeds or aborts with a `doctrine_version_mismatch` event in the yield log (a non-promotion that still records the gate firing).

Cost: ~half-day to implement the version-reading helper; reusable across both swarms.

---

## 5. The five typed pipelines

Each subsection below defines a single auto-promotion pipeline with: source artifacts, scoring function, auto-promote threshold, target substrate-state slot, kill-path mechanism, taint-scope shape, F043-class failure mode + mitigation, and weekly throughput target.

### 5.1 Quantified weekly targets (consolidated table — recalibrated in v0.2)

| Target | Pipeline | Current state | v0.1 target | **v0.2 target (revised)** | Survives if... |
|---|---|---|---|---|---|
| Anti-anchor candidate growth | Phylax → `anti_anchor_candidates.jsonl` | 12 entries in promoted registry | +1 / week | **+1 / month into candidates** (+ human-gated promotion to registry) | 30-day primary-lit stability + 2 independent primary-source confirmations |
| Symbol candidate growth | Iris → `CANDIDATES.md` | 24 promoted symbols | +5 candidates / week | **+5 candidates / week** (unchanged; this is the proof-of-concept) | ≥10 of 50 judged worth-keeping, ≤2 template artifacts |
| Problem lens-catalog completion | Argos → `catalogs/<problem>.md` | 3 anchor catalogs | +10 / week | **+2 / week minimum, scale to +10 contingent on routing_delta gate pass rate** | ≥1 informative verdict AND routing_delta non-zero |
| Calibrated-scorer candidate addition | Sophia → `AXIS_CLASS_candidates.jsonl` | 0 from swarm | +2 / week | **+1 / month** (much lower; bad axes are systemic) | Anchor-pass on 3 positive + 3 negative + 2 near-miss + 1 held-out specimen AND operator_delta_information > threshold |
| Specimen attention-state change | Telos → `frontier_specimen_state.md` (attention layer only) | manual today | +3 / week | **+1 / week (attention only; epistemic stays human-gated)** | Completed-audit evidence (Techne or Charon report) |
| Composition-rule discovery | Sophia + Argos joint product | 2 confirmed + 5 candidates | +1 / month | **+1 / month (unchanged; human-gated)** | 3 cross-tier validations |

The v0.2 floor is **substantially lower than v0.1** for everything except Iris (the proof-of-concept). The reviewer's correct concern was that v0.1's targets were aspirational for utilization, but each premature promotion costs more in downstream taint than the marginal value of hitting a target.

**Argos's conditional target** (in response to the reviewer's "catalog-shaped sediment" concern): the v0.2 target is `+2/week minimum`, but if the `routing_delta` gate is empirically measurable cheaply AND its pass rate is positive, the target scales linearly to `+10/week` as Argos's actual production rate × gate-pass-rate × utility-threshold allows. The cap is the gate, not the count.

### 5.2 Phylax → anti-anchor candidate pipeline (changed in v0.2)

**v0.2 change:** target slot is `anti_anchor_candidates.jsonl`, NOT `anti_anchors.jsonl`. The anti-anchor registry is too epistemically sharp to auto-write — a wrong anti-anchor suppresses future true claims. Two-step promotion: auto to candidates, human-gated (or doubly-confirmed) to registry.

**Source artifacts:** `verdict_*.md` files where `verdict ∈ {flag, block}` AND retraction-adjacency hits exist AND a doctrine-compliant Pythia DR was enqueued AND that DR has completed with a primary-source citation.

**Scoring function (Tier 0 pre-filter + Tier 1 transparent rule):**

```
score = (jaccard_score >= 0.40)
      * (DR_report has arXiv_id OR DOI present)
      * (DR_report distinguishes exact_form vs weaker_form)
      * (no anti-anchor exists for this anchor in the last 90 days)
      * (Pattern-30 grade is Level 0 or 1; Level 2+ means human-mandatory)
      * (claim_normal_form decomposable: object + invariant + relation
         + quantifier + domain restriction + exception set, all populated)

auto_promote_to_candidate if score == 1.0
```

**Auto-promote threshold:** all six conditions True. (We require unanimity here because the F043 cost is high.)

**v0.2 addition (per reviewer):** the **claim normal form** requirement. Token overlap is not semantic equivalence. Both the false form (from the retraction registry) and the new candidate claim must reduce into structured slots: `object`, `invariant`, `relation`, `quantifier`, `domain restriction`, `exception set`. The candidate must match the false form on at least 5 of 6 slots OR explicitly distinguish on a slot the DR cited.

**Target substrate slot:** `D:\Prometheus\techne\registry\anti_anchor_candidates.jsonl` — append a candidate row with `false_form`, `proposed_true_form`, `citation`, `last_verified`, `verified_against_primary=true`, `verification_source = "phylax-autoprom-<DR_row_id>"`, `claim_normal_form` (structured slots), `requires_human_promotion_to_registry=true`.

**Promotion to actual anti_anchors.jsonl:** human-gated OR auto-confirmed by **two independent primary-source citations** from separate DRs within 30 days.

**Kill-path artifact:** `D:\Prometheus\techne\registry\retracted_anti_anchor_candidates\<anchor_slug>_retracted_<utc>.md` with the exact `jq` command to remove the row from the JSONL, the DR report URL that should be re-read if reverting, and a trigger spec.

**Taint-scope shape:**
```json
{
  "readable_by_agents": ["phylax", "argos", "stygian", "lethe"],
  "downstream_slots": ["techne/registry/anti_anchor_candidates.jsonl"],
  "used_for_training": false,
  "recency_keys_written": ["anti_anchor_candidate:<slug>"],
  "requires_taint_sweep_on_retract": true,
  "cross_swarm_consumers": ["Charon swarm (Stygian primary-lit surveys may cite this candidate)"]
}
```

**Trigger spec for auto-retraction:** if any of:
- A subsequent Pythia DR (within 30 days) cites a primary source published after the original DR that contradicts the false_form classification
- A human reviewer writes `auto_retract` to the agent state directory
- The DR report URL becomes unreachable (link-rot trigger after 90 days)
- A second independent DR fails to confirm the candidate within the 30-day promotion window — candidate stays in candidates, never promotes to registry

**F043-class failure mode:** Phylax surfaces a token-overlap with a retraction registry entry, but the new claim is in fact a genuinely-distinct mathematical statement that happens to share vocabulary. Auto-promoting the new statement as an "anti-anchor" effectively bans a true claim.

**Mitigation:** the claim normal form requirement (v0.2 addition) is the structural defense — token overlap alone never auto-promotes. The two-step pipeline (candidate → registry) is the procedural defense — single-source promotion stays as candidate forever without independent confirmation.

**Weekly throughput target (v0.2 revised):** +1 anti-anchor candidate per month into `anti_anchor_candidates.jsonl`. Promotion to `anti_anchors.jsonl` is not Phylax's responsibility — it requires human review or doubly-confirmed independent DR evidence.

### 5.3 Iris → CANDIDATES.md pipeline (the proof-of-concept; strengthened in v0.2)

**Source artifacts:** `candidate_<slug>_<utc>.md` files where the underlying cluster has ≥3 distinct files AND ≥1 of those files is *not* in the agent's own corpus (i.e., the pattern is cross-corpus, not just intra-Harmonia).

**Scoring function (with v0.2 template-suppression gates):**

```
# Tier 0 hard-filter gates (NEW IN v0.2 per reviewer §4):
reject if phrase appears in >= 5 files with same section heading context
reject if phrase is mostly markdown boilerplate
       (>30% of fingerprint chars are `*`, `#`, `|`, `_`, or backtick)
reject if phrase appears in known agent prompt scaffolds
       (load list from harmonia/agents/iris/state/known_template_spans.json)
reject if token pattern overlaps known template spans

# Tier 1 transparent score (with capped entropy term per reviewer):
entropy_score = clamp(1 / max(paraphrase_entropy, 0.05), 0.0, 3.0)
score = (distinct_files_count - 2)
      * entropy_score
      * (1.0 if cross-corpus else 0.5)
      * (1.0 if slug not in dismissed_candidates else 0.0)
      * (1.0 if slug not already present in symbols/INDEX.md else 0.0)

auto_promote if score >= 1.5 AND all Tier 0 gates pass
```

**v0.2 changes (per reviewer):**

1. **Template-suppression gates** at Tier 0 — markdown boilerplate, agent prompt scaffolds, repeated section headings all auto-reject *before* scoring.
2. **Capped entropy term** — `1 / max(paraphrase_entropy, 0.05)` clamped to `[0.0, 3.0]` so near-zero entropy doesn't blow up the score.
3. **Initial template-span seed list** — Phase 0.5 (§7) ships with `known_template_spans.json` pre-populated with known boilerplate patterns from inspecting the existing artifacts directory.

**Auto-promote threshold:** score ≥ 1.5 AND all Tier 0 gates pass.

**Target substrate slot:** `D:\Prometheus\harmonia\memory\symbols\CANDIDATES.md` — append an entry with the slug, citations, sketch versioned spec, savings estimate, auto-promotion provenance, and a "promotion-to-symbol requires human review" tag.

**Kill-path artifact:** `dismissed_candidates.json` (existing) + `auto_promoted_candidates.json` (new in v0.2 — auto-revert is just moving the slug between lists).

**Taint-scope shape:**
```json
{
  "readable_by_agents": ["iris"],
  "downstream_slots": ["harmonia/memory/symbols/CANDIDATES.md"],
  "used_for_training": false,
  "recency_keys_written": ["symbol_candidate:<slug>"],
  "requires_taint_sweep_on_retract": false,
  "cross_swarm_consumers": []
}
```

**Trigger spec for auto-retraction:** if a human appends the slug to `dismissed_candidates.json` within 14 days, the CANDIDATES.md entry is auto-removed.

**F043-class failure mode:** Iris auto-promotes a phrase that is repeated across files only because of templating (e.g., section heading templates, citation formats). Promotion adds noise to `CANDIDATES.md`.

**Mitigation (strengthened in v0.2):** the template-suppression gates are *mechanical*, not relying on human review accumulating in `dismissed_candidates.json`. The first ~5 auto-promotions should still be reviewed by the conductor to seed the dismissed list and validate the template-suppression gate calibration.

**Why this remains the proof-of-concept:**

- Lowest blast radius (`CANDIDATES.md` is by definition not load-bearing — promotion to actual symbol still requires human review)
- Kill-path already exists (`dismissed_candidates.json` is the prior pattern)
- Scoring function is simple and explicit
- High candidate volume (Iris produces 200+ artifacts/day at current rates)
- Tier 0 template gates are objectively testable against the existing artifact set
- The reviewer's attention-compression metrics (§7 Phase 1) are best validated on a fast-cycle low-stakes pipeline

**Weekly throughput target (unchanged):** +5 candidate entries to `CANDIDATES.md` per week during validation phase. Of those, ≥1 should clear to a real symbol promotion via human review per the §5.1 row.

### 5.4 Argos → catalogs/ pipeline (gated by routing_delta in v0.2)

**Source artifacts:** `lens_catalog_<problem_slug>_<utc>.md` files where: applied + proposed lenses total ≥10 AND at least one applied lens has a non-null verdict AND the problem has ≥1 Pythia DR completed and committed within the last 30 days.

**Scoring function (with v0.2 routing_delta gate):**

```
# Tier 0 gates (NEW IN v0.2):
reject if catalog does not declare routing_delta
reject if catalog does not declare new_disagreement_found OR lenses_pruned
reject if catalog does not declare next_best_experiment
reject if catalog does not declare why_not_generic_catalog

# Tier 1 transparent score:
score = (lens_depth >= 10)
      * (informative_verdict_count >= 1)
      * (dr_completed_within_30d_count)
      * (problem_id not already in catalogs/)
      * (routing_delta != "none")              # NEW v0.2

auto_promote if score >= 2
```

**v0.2 additions (per reviewer):** required catalog metadata fields:

- `routing_delta`: prose describing how this catalog changes routing, prioritization, or known-disagreement structure compared to the generic lens shelf
- `new_disagreement_found`: boolean
- `lenses_pruned`: list of lenses that this catalog explicitly removes from consideration for this problem
- `next_best_experiment`: prose recommendation for the next audit / DR / test
- `why_not_generic_catalog`: prose justifying why a generic top-K-lens application would not produce the same conclusions

The Argos `_build_catalog()` method must produce all five fields or the catalog is rejected at Tier 0.

**Auto-promote threshold:** score ≥ 2 AND all Tier 0 gates pass.

**Target substrate slot:** `D:\Prometheus\harmonia\memory\catalogs\<problem_slug>.md` — new file with the full lens fingerprint, MPA scaffold, routing_delta declaration, and completed-DR cross-references.

**Kill-path artifact:** `D:\Prometheus\harmonia\memory\catalogs\<problem_slug>_retracted_<utc>.md` with `git revert <commit>` instructions. Catalogs are append-only history; retraction is by additive note, not deletion.

**Taint-scope shape:**
```json
{
  "readable_by_agents": ["argos", "telos"],
  "downstream_slots": ["harmonia/memory/catalogs/<problem_slug>.md"],
  "used_for_training": false,
  "recency_keys_written": ["catalog:<problem_slug>"],
  "requires_taint_sweep_on_retract": true,
  "cross_swarm_consumers": ["Charon swarm (Stygian primary-lit surveys may cite this catalog)"]
}
```

**Trigger spec for auto-retraction:** if a DR completed within 60 days of catalog promotion contradicts a lens verdict, the catalog gets an annotation (not a revert) and the verdict is downgraded.

**F043-class failure mode:** Argos auto-promotes a catalog whose lens verdicts are correlation-rich but the correlations are definitional (same Pattern-30 IDENTITY failure mode generalized to lens space). Promotion adds spurious "informative" verdicts to the lens-fingerprint corpus.

**Mitigation:** the informative-verdict check requires verdicts at the `map_of_disagreement` or `coordinate_invariant` tier specifically (both have explicit cross-lens-disagreement criteria). Pattern-30 grading is applied to each verdict at promote-time.

**Weekly throughput target (v0.2 revised):** +2 catalogs per week minimum, scaling to +10/week contingent on `routing_delta` gate-pass rate × utility-threshold. The cap is the gate, not the count.

### 5.5 Sophia → AXIS_CLASS candidate pipeline (changed in v0.2)

**v0.2 change:** target slot is `AXIS_CLASS_candidates.jsonl`, NOT direct symbol promotion. AXIS_CLASS additions are systemic — a bad axis is a lens distortion that affects every future measurement. Two-step pipeline.

**Source artifacts:** `proposal_<OP>_x_<FID>_<utc>.md` files where the operator-specimen pair has been auto-calibrated against the expanded calibration set (v0.2: 9 anchors total, not 3).

**Scoring function:**

```
# v0.2 expanded calibration set:
required_pass_set = {
  "positive_anchors": ["F001", "F004", "F008"],          # known-correct verdicts
  "negative_anchors": ["F010", "F012", "F043_retracted"], # known-failure cases
  "near_miss_anchors": ["F015", "F042"],                  # subtle-condition cases
  "held_out_specimen": ["F045"]                           # live, not in training
}

score = (calibration_anchors_passed == 9)              # ALL 9, not just 3
      * (non_tautology_check_passed)
      * (representation_invariance_held)
      * (operator_not_already_in_AXIS_CLASS)
      * (operator_delta_information > threshold)        # NEW v0.2

auto_promote_to_candidate if score == 1.0
```

**v0.2 additions (per reviewer):**

1. **Expanded calibration set** — 3 positive + 3 negative + 2 near-miss + 1 held-out = 9 anchors. The operator must produce expected verdicts on ALL 9 to auto-promote.
2. **`operator_delta_information` gate** — a measure (even crude) that the operator changes ranking or classification on at least one held-out case in a way later judged useful. Distinguishable ≠ useful; the operator must add incremental value, not just be different.

**Auto-promote threshold:** all five conditions True. (Unanimity required.)

**Auto-calibration mechanism:** the proposal's calibration-anchor gate spec is converted into an Agora queue task at priority 2 and dispatched to Techne or Charon for actual execution. If execution returns the expected verdict on all 9 anchors AND demonstrates incremental information value within 7 days, the proposal auto-promotes to candidates.

**Target substrate slot:** `D:\Prometheus\harmonia\memory\AXIS_CLASS_candidates.jsonl` — new row with the proposed operator name, frame, calibration evidence, delta-information measurement, and `requires_human_promotion_to_AXIS_CLASS=true` flag.

**Promotion to actual AXIS_CLASS:** human-gated.

**Kill-path artifact:** `D:\Prometheus\harmonia\memory\AXIS_CLASS_candidates_retracted\<op_name>_<utc>.md` with the candidate-row removal command and the failed-calibration record that triggered the retract.

**Taint-scope shape:**
```json
{
  "readable_by_agents": ["sophia", "telos"],
  "downstream_slots": ["harmonia/memory/AXIS_CLASS_candidates.jsonl"],
  "used_for_training": false,
  "recency_keys_written": ["axis_candidate:<op_name>"],
  "requires_taint_sweep_on_retract": true,
  "cross_swarm_consumers": ["Charon swarm (Moros may cite this as paradigm refinement)"]
}
```

**Trigger spec for auto-retraction:** if any subsequent use of the AXIS_CLASS candidate operator on a real specimen produces a verdict that contradicts its calibration (within 60 days), auto-demote and write the retraction note.

**F043-class failure mode:** a Sophia proposal passes auto-calibration because the operator is structurally equivalent to one of the anchors. Promotion adds a redundant or distorted axis.

**Mitigation (strengthened in v0.2):** the expanded 9-anchor calibration set + `operator_delta_information` gate is the structural defense. The two-step pipeline (candidates → human-gated AXIS_CLASS) is the procedural defense.

**Weekly throughput target (v0.2 revised):** +1 calibrated-scorer candidate per month. The conservative target reflects the reviewer's correct observation that bad axes are systemic distortions, not just clutter.

### 5.6 Telos → frontier_specimen_state change pipeline (split in v0.2)

**v0.2 split (per reviewer):**

- **Attention-state changes** (revive, watch, deprioritize): auto-promotable — these affect attention allocation but do not change the epistemic claim about the specimen.
- **Epistemic-state changes** (killed, live_specimen, calibration_refinement, calibration): human-gated — these change what the substrate asserts about the specimen.

**Source artifacts:** `revive_<FID>_<utc>.md` files where a completed audit has executed at least 2 of the 3 proposed lenses AND the audit result deviates from the F-ID's current `last_audit_outcome`.

**Scoring function:**

```
# Determine change class:
if proposed_change in {revive, watch, deprioritize}:
    change_class = "attention_state"
    auto_promote_allowed = True
elif proposed_change in {killed, live_specimen, calibration_refinement, calibration}:
    change_class = "epistemic_state"
    auto_promote_allowed = False    # human-gated

score = (proposed_lenses_executed >= 2)
      * (post_audit_confidence_shift >= 0.5)
      * (lens_delta_coverage >= 0.30)
      * (no_open_dispute_in_decisions_for_james)

auto_promote_attention if score >= 0.5 AND auto_promote_allowed
write_epistemic_proposal if score >= 0.5 AND not auto_promote_allowed
```

**Auto-promote threshold (attention layer only):** score ≥ 0.5.

**Target substrate slot (attention layer):** update to `D:\Prometheus\harmonia\memory\frontier_specimen_state.md` — only the `attention_priority` column (new in v0.2) and audit-cadence fields. Tier remains human-controlled.

**Target substrate slot (epistemic layer):** write a `epistemic_change_proposal_<fid>_<utc>.md` artifact for human review — never modify tier auto.

**Kill-path artifact:** `D:\Prometheus\harmonia\memory\frontier_specimen_state_changes\<fid>_<change_type>_<utc>.md` with the prior row state quoted and a `git revert` reference.

**Taint-scope shape:**
```json
{
  "readable_by_agents": ["telos", "phylax", "sophia"],
  "downstream_slots": ["harmonia/memory/frontier_specimen_state.md (attention column only)"],
  "used_for_training": false,
  "recency_keys_written": ["specimen_attention:<fid>"],
  "requires_taint_sweep_on_retract": false,
  "cross_swarm_consumers": []
}
```

**Trigger spec for auto-retraction:** if any new audit within 30 days contradicts the auto-promoted attention-state change, auto-revert and write the post-mortem.

**F043-class failure mode:** Telos auto-promotes an attention change based on a single-lens audit that happens to be a Pattern-30 Level 3 artifact. Attention is misdirected for the TTL window.

**Mitigation:** the `proposed_lenses_executed >= 2` requirement is the cross-lens consistency check. The split (attention vs epistemic) ensures the worst case is wasted audit cycles, not a misrepresented epistemic claim.

**Weekly throughput target (v0.2 revised):** +1 attention-state change per week. Epistemic-state changes route to human review and have no swarm-driven throughput target.

### 5.7 Pipeline interaction diagram

```
                     +---------------------------+
                     |  Yield log                |
                     |  yields.jsonl             |
                     |  (7 outcome classes,      |
                     |   taint_scope per row,    |
                     |   doctrine_version,       |
                     |   marginal_substrate_val) |
                     +-----------+---------------+
                                 |
                                 | trains (PHASE 3+ only)
                                 v
                     +---------------------------+
                     |  Scoring primitive        |
                     |  _scorer.py               |
                     |  Tier 0 / Tier 1          |
                     |  (Tier 2 bandit deferred) |
                     +-----------+---------------+
                                 |
                                 | used by
                                 v
   +----------+   +----------+   +----------+   +----------+   +----------+
   | Phylax   |   | Iris     |   | Argos    |   | Sophia   |   | Telos    |
   | -> AA_c  |   | -> CAND  |   | -> CAT   |   | -> AXIS_c|   | -> ATT   |
   +----+-----+   +----+-----+   +----+-----+   +----+-----+   +----+-----+
        |              |              |              |              |
        | candidate    | proposal     | catalog +    | candidate    | attn-state
        | (not yet AA) | (not yet     | routing_delta| (not yet     | (epistemic
        |              |  symbol)     | gated        |  AXIS_CLASS) |  stays human)
        v              v              v              v              v
   anti_anchor_    CANDIDATES.md   catalogs/    AXIS_CLASS_    frontier_specimen_
   candidates                                   candidates     state.md
   .jsonl                                       .jsonl         (attention col only)
        |              |              |              |              |
        | + kill-path  | + kill-path  | + kill-path  | + kill-path  | + kill-path
        | + taint-path | + taint-path | + taint-path | + taint-path | + taint-path
        | + yield row  | + yield row  | + yield row  | + yield row  | + yield row
        v              v              v              v              v
        |              |              |              |              |
        +--------------+--------------+--------------+--------------+
                                      |
                                      v
                       Watchdog daemon (NEW IN v0.2):
                       - Validates taint-scope on every promotion
                       - Runs daily anchor calibration of the scorer
                       - Monitors trigger specs; fires auto-retraction
                       - Logs marginal_substrate_value review status
                       - Refuses promotion on doctrine_version mismatch
```

---

## 6. Anti-capture safeguards (expanded from 3 to 7 rules in v0.2)

Auto-promotion at machine speed has higher risk of reward-capture (the failure mode where novelty quietly gets replaced by validation or completion as the thing being optimized for). Seven hard rules (the first three from v0.1, the last four added during v0.2 review + post-review):

### 6.1 Every auto-promotion writes a kill-path at promote-time

Not at retract-time. The kill-path file is created in the same transaction as the promotion. If the agent cannot construct a kill-path artifact, the promotion is aborted. This makes reversibility a precondition, not an afterthought.

### 6.2 Every auto-promotion has an explicit trigger spec for auto-retraction

A condition under which the promotion auto-reverts without human intervention. The trigger spec is machine-checked daily by a separate watchdog process.

### 6.3 The scoring primitive runs its own calibration daily

Once per day, the scorer runs against the seven Prometheus calibration anchors (F001-F005 + F008 + F009) under each pipeline's scoring function. If the scorer would auto-promote a known-good or known-bad anchor incorrectly, the scorer self-quiesces (stops auto-promoting) until the conductor re-tunes.

### 6.4 Every auto-promotion declares its taint scope (NEW IN v0.2)

Reversibility is not enough. Reverting a bad promotion restores file state but does not fully restore downstream attention, scorer labels, learned priors, recency caches, or agent behavior that consumed the bad state. The `taint_scope` field on every yield row declares:

- `readable_by_agents`: which agents may read this promotion (including cross-swarm)
- `downstream_slots`: which substrate files / registries may consume it
- `used_for_training`: whether any scorer / classifier has trained on it
- `recency_keys_written`: which recency-collision keys have been claimed (so re-fires don't get suppressed after retraction)
- `requires_taint_sweep_on_retract`: bool — if true, retraction must enqueue a taint-sweep task
- `cross_swarm_consumers`: free-form list of Charon-swarm or other-swarm agents that may have consumed this

**Taint-sweep on retract:** when an auto-promotion is retracted AND `requires_taint_sweep_on_retract` is true, the watchdog daemon enqueues a sweep task: scan each `readable_by_agents` agent's state for references to the retracted promotion, scan each `downstream_slots` file for citations, scan recency-key state for orphaned entries, and emit a `taint_sweep_report_<promotion>_<utc>.md` artifact listing what was found.

The taint-sweep report is itself reviewable. A clean sweep (zero downstream consumers found) means retraction was clean. A non-empty sweep means manual taint-handling is required before the substrate is fully restored.

### 6.5 Yield-label semantics — TTL survival is NOT acceptance (NEW IN v0.2)

The yield log's `outcome` field is one of seven values, not three:

| Outcome | Meaning | Trains as positive? |
|---|---|---|
| `accepted_human` | Conductor explicitly marked accept | YES |
| `accepted_downstream_use` | Another agent or human cited this promotion in subsequent work | YES |
| `survived_ttl_unreviewed` | TTL expired with no action; promotion still in place | NO (do not train as positive) |
| `dismissed_human` | Conductor marked dismiss | NO (train as negative) |
| `auto_retracted` | Trigger spec fired | NO (train as negative) |
| `contradicted` | A subsequent DR or audit contradicted the promotion | NO (train as negative) |
| `stale_unconsumed` | TTL expired AND no agent has accessed the promotion's downstream slot | NO (train as ambiguous; do not train) |

**Critical rule (per reviewer §10):** the Tier 1 scorer training set uses ONLY `accepted_human` and `accepted_downstream_use` as positive labels. `survived_ttl_unreviewed` is explicitly excluded — survival without engagement is not endorsement.

This is the single biggest anti-Goodhart move in v0.2. Without it, the scorer learns "promotions that survive without being read are good," which optimizes for invisibility, not value.

### 6.6 Marginal substrate-value scoring — anti-Goodhart (NEW IN v0.2)

Every auto-promotion eventually gets a `marginal_substrate_value` integer in {0, 1, 2, 3, 4, 5}:

| Value | Meaning |
|---|---|
| 0 | Clutter (false positive, noise) |
| 1 | Harmless but low-value (no harm, no benefit) |
| 2 | Useful local compression (saves time on one task) |
| 3 | Changes routing / experiment choice (alters what the substrate does next) |
| 4 | Prevents known failure mode (e.g., catches an F043-class adjacency) |
| 5 | Creates reusable substrate primitive (becomes a load-bearing piece) |

The conductor assigns these at review time. They drive three things:

1. **Scorer training:** higher-value labels weight the training set more heavily than mere `accepted_human` labels. A scorer that learns to predict promotions of value 3+ is more useful than one that predicts value 1+.
2. **Bandit reward signal (§4.1):** the bandit's reward is `marginal_substrate_value - taint_cost_penalty - retraction_penalty`, not raw promotion count. This makes the bandit optimize for net substrate value, not noise.
3. **Weekly maturation reporting (§6.7):** weekly metrics report not just "N promotions" but "N × mean(marginal_substrate_value)." If the system Goodharts toward many low-value promotions, mean value drops and the regression is visible.

**Calibration discipline (v0.2 addition beyond reviewer):** monthly, the conductor re-labels a fixed calibration set of 10 past promotions (5 known-good, 5 known-bad). If the new labels drift from the prior labels, the drift is logged and the scorer's training set is annotated with the inter-rater-shift event. Without this, the labels themselves drift and the trained scorer is biased toward whenever-the-label-was-applied.

### 6.7 Maturation tracking (NEW IN v0.2, post-review)

Wins, losses, and tool maturation must be visible without manual artifact inspection. Per the James direction: "We want to see wins, losses and maturation of the tools and programs."

**Weekly maturation report** (`scripts/harmonia_weekly_report.py`, NEW deliverable in Phase 0):

Reads `events.jsonl` + `yields.jsonl` for the prior 7 days; emits a markdown roll-up to `harmonia/agents/_logs/weekly_<utc>.md`. Sections:

**1. Wins (counts and rates):**
- `accepted_human` count per agent
- `accepted_downstream_use` count per agent (the real value signal)
- Mean `marginal_substrate_value` per agent (trended week-over-week)
- Promotions with `marginal_substrate_value >= 3` (the "changes routing" tier and above)

**2. Losses (counts and rates):**
- `dismissed_human` count per agent (false-positive rate)
- `auto_retracted` count per agent (trigger-spec fires)
- `contradicted` count per agent (DR or audit contradicted the promotion)
- `survived_ttl_unreviewed` count per agent (concerning if high — means promotions land but aren't read)
- `stale_unconsumed` count per agent (means agent is producing for a non-consumer)

**3. Maturation (trends, week-over-week deltas):**
- False-positive rate trend (should be flat or decreasing if maturing)
- Mean marginal_substrate_value trend (should be increasing or stable)
- Time-to-outcome median (should be decreasing — promotions getting reviewed faster)
- Tier 0 reject rate (high = good filter; sudden drop = something broken)
- Bandit explore rate per pipeline (should be decreasing on schedule per §4.1)
- Per-arm bandit performance (which arms are paying off; which have stagnant pull-counts)

**4. Health signals (alerts if thresholds breached):**
- Taint-sweep events per week (low = clean retractions; spikes = poorly-scoped promotions)
- `scorer_self_quiesce` events (should be rare; persistent quiesces mean reward signal drift)
- `doctrine_version_mismatch` events (should be rare; persistent mismatches mean Aporia/Harmonia divergence)
- Cross-swarm consumer count growth (rising means cross-swarm taint risk growing)

**5. Per-agent maturation card:**
- One small card per agent (Phylax, Sophia, Iris, Argos, Telos) with:
  - This week's count of each event class
  - Trend arrow (↑/↓/→) vs prior 4-week average
  - One-line natural-language summary ("Iris this week: 32 candidate promotions, 6 accepted (18% — below 4wk avg of 24%); marginal value held at 1.4; template-suppression filter caught 78% of pre-filter rejects.")

**Consumer:** the weekly report is reviewable in ≤5 minutes. It is the conductor's primary surface for understanding "is the system getting smarter or just busier." The report itself is emitted as a `weekly_report_emitted` event so its production cadence is also tracked.

**Daily snapshot:** `scripts/harmonia_summary.py` (already shipped) continues as the day-to-day view. The weekly report is the trend / maturation view.

---

## 7. Sequenced rollout (revised in v0.2)

### Phase 0 (week 1): foundations

- Ship `harmonia/agents/_scorer.py` with Tier 0 hard-filter pre-filter + Tier 1 transparent hand-scored rank + **Tier 2 epsilon-greedy bandit (epsilon=0.50 initial, per §4.1 risk-mitigation code)**
- Ship `harmonia/agents/_logs/yields.jsonl` with 7-class outcome semantics + taint_scope + doctrine_version fields
- Ship `harmonia/agents/_logs/events.jsonl` (NEW v0.2 §4.5) with the event-class schema + the `emit_event()` helper in `_scorer.py`
- Ship the daily calibration watchdog (`scripts/harmonia_scorer_calibration.py`) that runs anchor checks
- Ship the taint-sweep watchdog (NEW v0.2): scans for orphaned references after retractions
- Ship `scripts/harmonia_weekly_report.py` (NEW v0.2 §6.7): weekly maturation roll-up consumed from events.jsonl + yields.jsonl

### Phase 0.5 (mid-week 1): review tooling (NEW IN v0.2)

Per the pushback on the "60-min total review time" criterion: before Phase 1 starts, ship `scripts/harmonia_review.py`:

- Lists pending promotions awaiting `outcome` and `marginal_substrate_value` tags
- Surfaces each with its `taint_scope` inline (the conductor can see what may have consumed it)
- Accepts 5-second tag-and-move actions (`a` = accept, `d` = dismiss, `s` = skip; `0`-`5` for marginal value)
- Writes back to yields.jsonl in append-only mode

Without this tool, the human review burden is unergonomic and the Phase 1 success criterion is unmeasurable.

### Phase 1 (weeks 2-3): Iris pipeline as proof-of-concept

- Implement `iris._autopromote()` per §5.3 (with template-suppression gates + capped entropy + taint-scope)
- Run for 2 weeks; expect ~50 auto-promotions
- Conductor uses `harmonia_review.py` for 5 min/day; expected total ≤60 min across 14 days
- **Success criteria (revised per reviewer):**
  - ≥10 of 50 judged worth-keeping (label ≥ 2 on marginal value)
  - ≥1 clears to real symbol promotion via human review
  - ≤2 template artifacts (Tier 0 gates work)
  - ≤60 min total human review time
  - ≤5% auto-promote false-positive rate (`dismissed_human` rate)
  - Mean `marginal_substrate_value` ≥ 1.5 (the system isn't just clutter)

### Phase 2 (week 4): scoring primitive label calibration

- After Iris Phase 1 closes, manually re-label the 10-promotion calibration set
- Check inter-rater stability of `marginal_substrate_value` labels
- Validate that `accepted_human` rate × mean marginal value > a baseline threshold
- If the labels are stable, proceed to Phase 3; if not, extend Phase 1 with refined labeling protocol

### Phase 3 (weeks 5-7): learned Tier 1 + extend to remaining four agents

- ONLY IF Phase 2 label calibration passes: train Tier 1 logistic regression / GBM on the labeled set (positive = `accepted_human` ∪ `accepted_downstream_use`)
- Tier 1 replaces the rule-based fallback for Iris
- Extend pipelines in order of lowest blast-radius first: Argos (catalogs, with routing_delta gate), then Phylax (candidates), then Sophia (candidates), then Telos (attention-state only)

### Phase 4 (week 8+): cross-pipeline bandit reward sharing (conditional)

- Bandit per-pipeline isolation has been active since Phase 1 (§4.1). Phase 4 introduces *cross-pipeline reward sharing* — letting Iris's reward signal inform Sophia's exploration, etc.
- Cross-pipeline sharing is gated on:
  - The reward signal is itself calibrated per pipeline (mean marginal_substrate_value stable across 4+ weeks)
  - Inter-rater drift on the calibration set < threshold
  - At least two pipelines have independently demonstrated `marginal_substrate_value` ≥ 3 in ≥10% of promotions
- If all three gates pass, introduce a shared feature space across pipelines (still pipeline-specific decision thresholds)
- Cross-pipeline sharing NEVER applies to Phylax candidate-to-registry or Sophia candidate-to-AXIS_CLASS transitions — those remain candidate-tier auto + human-gated for final promotion

### Expected end-state at week 8

- ~5-10 substrate-state changes per week (most into candidate-tier slots, fewer into full registry)
- ≤10 min/week human-review burden
- Yield log with ≥250 labeled records, ≥50 with `marginal_substrate_value` tags
- Backlog still bounded; production rate unchanged
- Demonstrable: mean marginal_substrate_value > week-1 baseline (the system is improving, not just running)

---

## 8. Risks and open questions

### 8.1 Known risks (expanded in v0.2)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| F043-class auto-promotion | Low | High | Per-pipeline Pattern-30 gates + claim-normal-form structural check + 30-day stability checks + scorer self-quiesce + two-step candidate-to-registry pipelines |
| Reward-capture (scorer favors easy promotions) | Medium | Medium | Daily anchor-calibration of the scorer; explicit bandit gating on reward-signal calibration; `marginal_substrate_value` tracking; bandit disabled in Phase 1-3 |
| **Label poisoning by passive TTL survival** (NEW v0.2) | High | High | 7-class outcome semantics; `survived_ttl_unreviewed` explicitly excluded from positive training set |
| **Goodharting toward cheap wins** (NEW v0.2) | High | Medium | `marginal_substrate_value` 0-5 ordinal; weekly metric is `count × mean(value)`, not just `count` |
| **Taint propagation across retracted promotions** (NEW v0.2) | Medium | Medium | Taint-scope required at promote-time; taint-sweep watchdog enqueues sweep tasks on retraction; cross-swarm consumers explicitly listed |
| **`marginal_substrate_value` label drift over time** (NEW v0.2) | Medium | Medium | Monthly re-labeling of 10-promotion calibration set; inter-rater-shift events logged |
| Yield-log bootstrap takes too long | Medium | Low | Cold-start rule-based Tier 1; conductor-pace tagging via `harmonia_review.py` |
| Auto-retraction trigger TTLs are wrong | Medium | Low | TTLs are configurable per pipeline; first month is observation-only on TTL validity |
| Scoring primitive overfits to first 50 labels | High | Medium | Hold-out evaluation each week; Phase 2 label-calibration gate; alert if Tier 1 AUC < rule-based baseline |
| **Doctrine-version drift breaks DR-dependent pipelines** (NEW v0.2) | Low | Medium | `doctrine_version` field required; pipelines refuse promotion on mismatch |

### 8.2 Open questions for the reviewer (updated for v0.2)

Original v0.1 reviewer questions and the v0.2 disposition:

1. **Are weekly throughput targets calibrated correctly?** v0.2 lowered all non-Iris targets per reviewer. Question remains: is the Argos conditional target (+2/week min, scale to +10 contingent on routing_delta gate) calibrated correctly?

2. **Is F043-class mitigation strong enough at machine speed?** v0.2 adds claim-normal-form structural check, two-step candidate-to-registry pipelines, and taint-sweep on retract. Question: is this enough, or does claim-normal-form need a formal schema (e.g., a typed dataclass) rather than free-form slots?

3. **Per-pipeline vs unified scoring?** v0.2 keeps per-pipeline as recommended. Question: when (if ever) should features be shared across pipelines?

4. **Yield-log outcome signal observability for Sophia / Telos?** v0.2 makes the `accepted_downstream_use` class explicit; this partially answers but Sophia and Telos still depend on Techne/Charon audit-execution capacity. Question: at what audit-cycle latency should we add proxy signals for triage (not training)?

5. **Should TTLs be auto-tuned?** v0.2 keeps static; deferred to Phase 4+.

6. **Aporia doctrine version as hard input?** v0.2 implements this as §4.4. Question: should the doctrine version range (MIN/MAX) be per-pipeline or global?

**New open questions in v0.2:**

7. **Marginal-value calibration cadence:** monthly re-labeling of 10 calibration-set promotions — is this frequency right, or should it be tied to a "labels-since-last-calibration" trigger?

8. **Cross-swarm taint sweep:** v0.2 declares cross-swarm consumers in `taint_scope.cross_swarm_consumers` but the actual sweep across Charon's agent state is out of scope. When does the cross-swarm bridge become a v0.X scope item?

9. **The yield log as substrate-vocabulary artifact:** v0.2 notes (§4.2) that the log may itself become a candidate substrate primitive. Should this be planned for explicitly (e.g., a v0.3 META_AGENT_YIELD_PROFILE@v1 candidate), or remain implicit until empirically visible?

---

## 9. What this proposal explicitly does not include

For reviewer clarity, the following are *out of scope* of v0.2:

- Cross-swarm consumption (Charon ↔ Harmonia full bridge). Taint scope DECLARES cross-swarm consumers; actual sweeping across Charon agent state is separate roadmap item.
- Scaling agent backlog (the "heat-death-scale" thesis). Explicitly deferred until consumption is solved AND yield log demonstrates that auto-promotion improves epistemic state.
- Promotion to `Validated` precision tier or to any file under `aporia/doctrine/substrate_vocabulary/`. Those remain human-only.
- Modifying Aporia's research_queue table or Pythia's daemon. The pipelines consume Pythia output but don't modify Pythia.
- Real-time scoring (the daemon batches per-tick; sub-tick latency isn't required).
- Distributed scoring across multiple machines. Single-machine (M2) scope.
- Promotion of derived patterns from the yield log itself to META_* symbols. Acknowledged in §4.2; planned for v0.3+ only if empirically warranted.

---

## 10. Reviewer checklist (updated for v0.2)

Specific questions a reviewer could focus on, in priority order:

1. **§5 typed pipelines as revised** — Are the v0.2 changes (two-step candidate pipelines for Phylax + Sophia, routing_delta gate for Argos, template-suppression gates for Iris, attention/epistemic split for Telos) sufficient to address the v0.1 reviewer's concerns? Anything missing?
2. **§6.4 taint paths** — Is the `taint_scope` schema sufficient? Does the taint-sweep watchdog cover the right consumers?
3. **§6.5 7-class outcome semantics** — Is the line between `accepted_downstream_use` and `survived_ttl_unreviewed` defensible? What downstream signals count as "use"?
4. **§6.6 marginal-value scoring + §7 Phase 2 label calibration** — Is monthly re-labeling of 10 promotions enough to detect drift? Should the calibration set itself grow?
5. **§7 Phase 0.5 review tooling** — Is the 5-second tag-and-move action set sufficient, or does the conductor need richer tooling (e.g., side-by-side taint-scope vs artifact content)?
6. **§8.1 risks** — Are the v0.2 additions (label poisoning, Goodharting, taint propagation, marginal-value drift, doctrine drift) covering the new attack surface?
7. **§8.2 open questions 7-9** — Any single one; engage with substance, not just acknowledge.

---

## 11. Glossary (expanded in v0.2)

| Term | Meaning |
|---|---|
| **Prometheus** | The umbrella project — a falsification-first reasoning substrate for automated mathematical discovery. |
| **Harmonia** | One of the agent roles in Prometheus; owns substrate architecture and Σ-language grammar. |
| **Harmonia swarm** | Five autonomous child-agents under a rotation orchestrator: Phylax, Sophia, Iris, Argos, Telos. |
| **Σ-kernel** | The append-only typed ledger at the core of Prometheus, with 25 frozen-dataclass primitives and 9 opcodes. |
| **Substrate** | The accumulated typed state of Prometheus — symbols, anti-anchors, catalogs, retraction registry, etc. |
| **Anti-anchor** | A pinned false claim with primary-source refutation; serves as a sentinel against LLM training-data fossilized errors. |
| **Anti-anchor candidate** (v0.2) | A Phylax-proposed anti-anchor sitting in `anti_anchor_candidates.jsonl`, awaiting human promotion or doubly-confirmed independent DR evidence. |
| **AXIS_CLASS candidate** (v0.2) | A Sophia-proposed scorer sitting in `AXIS_CLASS_candidates.jsonl`, awaiting human review before joining the AXIS_CLASS symbol. |
| **F-ID** | Finding ID — a numbered specimen at some tier (calibration, live_specimen, killed, data_frontier). |
| **F043** | The retracted BSD-Sha anticorrelation finding; the load-bearing anchor case for Pattern 30 discipline. |
| **Pattern 30** | A graded (Level 0-4) algebraic-identity coupling detector. |
| **AXIS_CLASS@v1** | The promoted symbol enclosing all members of the coordinate-system / projection-operator vocabulary. |
| **PROBLEM_LENS_CATALOG@v1** | The promoted symbol for per-problem multi-perspective lens fingerprints. |
| **Pythia** | The Gemini Deep Research dispatcher daemon, owned by Aporia. |
| **Aporia** | The agent role responsible for open-problem cataloging, DR dispatch, and the substrate-vocabulary doctrine. |
| **Techne** | The agent role responsible for substrate primitives, the Σ-kernel registry, and frozen-interface discipline. |
| **Charon** | The agent role responsible for the falsification battery; also has a sibling swarm (Acheron, Lethe, Stygian, Moros, Hecate). |
| **Calibration anchor** | A finding whose verdict is so well-established that any operator producing the wrong verdict on it is miscalibrated. F001-F005 + F008 + F009. |
| **Kill-path** | The explicit, machine-actionable reversal command paired with a promotion. |
| **Trigger spec** | A machine-checkable condition under which auto-retraction fires. |
| **Taint-scope** (v0.2) | Declaration of what files, logs, queues, scorer labels, recency caches, and cross-swarm agents may have consumed a promotion. Required at promote-time. |
| **Taint-sweep** (v0.2) | Watchdog task that, on retraction, scans declared taint-scope for orphaned references and emits a sweep report. |
| **Yield log** | Append-only JSONL recording downstream actions on auto-promoted artifacts; supervision signal for the scorer. v0.2: 7 outcome classes, not 3. |
| **Marginal substrate value** (v0.2) | 0-5 ordinal label assigned by the conductor at review time, measuring how much each promotion actually advances the substrate. |
| **Scoring primitive** | The shared Tier 0 / Tier 1 / Tier 2 ranking pipeline at `harmonia/agents/_scorer.py`. v0.2: Tier 1 transparent only, no learned model in Phase 1, bandit deferred. |
| **Reward-capture** | The failure mode where novelty quietly gets replaced by validation/completion as the thing the system optimizes for. |
| **Goodharting** | (v0.2) Optimizing toward a metric in a way that degrades the underlying value the metric was supposed to measure. |
| **Routing-delta** (v0.2) | Argos catalog quality gate — does this catalog change which experiment runs next? |
| **Claim normal form** (v0.2) | Phylax structural decomposition of a candidate claim into object / invariant / relation / quantifier / domain restriction / exception set, for semantic-not-token-level adjacency checking. |
| **Doctrine version** (v0.2) | Required yield-row field for DR-dependent pipelines; refuses promotion on mismatch. |

---

## 12. Reframing acknowledgment (NEW IN v0.2)

The v0.1 design question was: *"Can we safely auto-promote?"*

The v0.2 design question is: **"Can we compress machine production into high-value, reversible, taint-tracked substrate updates without poisoning future routing?"**

The shift acknowledges that reversibility is necessary but not sufficient. A bad auto-promotion can leak into later agent prompts, yield-log training labels, downstream catalogs, scorer calibration, recency caches, human trust, and future negative-example sets. Reverting the immediate file state does not restore the epistemic state.

This is why v0.2 separates kill-paths (file-state reversal) from taint-paths (epistemic-state restoration), adds the 7-class outcome semantics (so passive TTL survival doesn't poison the training set), and introduces marginal-value scoring (so the system cannot Goodhart toward cheap promotions while metrics look healthy).

The goal is NOT many promotions. The goal is **high-value state change per conductor minute, without poisoning future routing.**

---

## 13. Changelog (v0.1 → v0.2 diff)

The v0.2 revision incorporates 10 numbered changes from external review 2026-05-22, plus 3 additions and 3 mild pushbacks from Harmonia. Each change traced below to its v0.2 location.

### Reviewer-requested changes (10)

| # | Change | v0.2 location |
|---|---|---|
| 1 | Add `taint_scope` to every yield row | §4.2 yield log schema + §6.4 anti-capture rule |
| 2 | Split `accepted` into 7 distinct outcome classes | §4.2 yield log schema + §6.5 anti-capture rule |
| 3 | Disable learned Tier 1 and bandit allocation for Phase 1 | §4.1 (transparent Tier 1 only) + §7 Phase 3+ |
| 4 | Add template-suppression gates to Iris | §5.3 Tier 0 gates + capped entropy term |
| 5 | Change Phylax output to `anti_anchor_candidates.jsonl` | §5.2 (two-step candidate-to-registry pipeline) |
| 6 | Lower weekly targets for Phylax, Argos, Sophia, Telos | §5.1 consolidated table (revised) |
| 7 | Split Telos attention-state vs epistemic-state | §5.6 (epistemic stays human-gated) |
| 8 | Require `doctrine_version` field for DR-dependent pipelines | §4.4 (new section) |
| 9 | Add `marginal_substrate_value` as 0-5 ordinal label | §6.6 (new anti-capture rule) |
| 10 | Scorer training uses only human-accepted / downstream-used as positives | §6.5 (training-set restriction) |

### Harmonia additions beyond reviewer (3)

| # | Addition | v0.2 location |
|---|---|---|
| H1 | Yield log itself may become a substrate-vocabulary artifact over time | §4.2 (closing paragraph) |
| H2 | `marginal_substrate_value` labels need their own calibration to prevent drift | §6.6 + §7 Phase 2 (monthly re-labeling) |
| H3 | Cross-swarm taint propagation acknowledged even though cross-swarm bridge out of scope | §6.4 (`cross_swarm_consumers` field) |

### Harmonia pushbacks on reviewer suggestions (3)

| # | Pushback | v0.2 location |
|---|---|---|
| P1 | Argos target: conditional on routing_delta gate, not fixed at +2/week | §5.1 (`+2/week minimum, scale to +10 contingent on gate`) + §5.4 |
| P2 | Bandit framing: tie to reward-signal calibration, not just label count | §4.1 (bandit-from-day-1 with risk-coding; cross-pipeline sharing is the Phase 4 gate, not bandit-itself) |
| P3 | Phase 1 success criterion (60 min total review) requires review tooling | §7 Phase 0.5 (new: `harmonia_review.py`) |

### James direction post-reviewer (3) — overrides specific reviewer items

| # | Direction | v0.2 location | Overrides |
|---|---|---|---|
| J1 | Keep bandit active from Phase 1 with explicit risk-mitigation code (7 mitigations spelled out), rather than disabling | §4.1 (Tier 2 active from Phase 1) | Reviewer change #3 (which said disable) |
| J2 | Mandate rich structured logging from every tool — current and future — to a swarm-wide event channel | §4.5 (new section); §7 Phase 0 ships events.jsonl + emit_event helper | New direction (not in reviewer) |
| J3 | Maturation visibility (wins / losses / trends) as a weekly report | §6.7 (new section); §7 Phase 0 ships harmonia_weekly_report.py | New direction (not in reviewer) |

The James direction on the bandit is a precise refinement of the reviewer's caution: the reviewer's correct intuition was about reward-capture risk; James's correction is that the right response is to *code defensively around the reward signal*, not refuse the tool. v0.2 §4.1 documents seven explicit risk-mitigations and §6.6 makes the reward signal multi-objective (`marginal_substrate_value - taint_cost - retraction_penalty`).

### Structural changes

- §6 anti-capture safeguards expanded from 3 rules to 7 (was 6 in mid-revision; §6.7 added per James)
- §4 design expanded from 3 components to 5 (§4.4 doctrine versioning + §4.5 structured logging)
- §12 reframing acknowledgment added (new section)
- Glossary expanded with v0.2 terms (taint-scope, marginal-value, routing-delta, claim-normal-form, doctrine-version, event-class, etc.)

---

## 14. Changelog (versions)

- **v0.2 (2026-05-22)** — Post-external-review revision + post-review James direction. 10 reviewer changes incorporated, 3 Harmonia additions, 3 mild pushbacks, 3 James direction items (incl. one explicit override of the reviewer on bandit-from-day-1). Seven anti-capture rules (was 3). Five design components (was 3 — added doctrine-version gating and structured-logging mandate). Two-step candidate-to-registry pipelines for Phylax + Sophia. Taint-paths added. Yield-log outcome semantics distinguish active acceptance from passive TTL survival. Marginal-value scoring as anti-Goodhart measure (and as bandit reward signal). Sequenced rollout adds Phase 0.5 review tooling. Structured event emission mandated swarm-wide. Weekly maturation report ships in Phase 0. See §13 for full v0.1 → v0.2 diff.

- **v0.1 (2026-05-22)** — Initial draft for external review.

---

*End of v0.2. Review feedback to be incorporated as inline annotations or a separate v0.3 spec document.*
