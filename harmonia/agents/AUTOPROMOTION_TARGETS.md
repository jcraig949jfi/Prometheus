# Harmonia auto-promotion targets

**Status:** DRAFT v0.1 — open for external review
**Date:** 2026-05-22
**Scope:** Auto-promotion pipeline design for the five Harmonia child-agents (Phylax, Sophia, Iris, Argos, Telos) in Project Prometheus
**Authors:** Harmonia (Claude Code agent), with James Craig
**Related:** `D:\Prometheus\harmonia\agents\ROADMAP.md` (cross-cutting upgrades), per-agent `README.md` files

---

## TL;DR

The Harmonia swarm produces ~440 well-formed artifacts per agent per ~54-hour cycle (~2200 artifacts total, zero errors). Of those, approximately **one** has been read and acted on by a downstream actor. The remaining ~2199 sit on disk as "production" but practically as noise. This document proposes an auto-promotion pipeline that converts a graded subset of those artifacts into formal substrate-state changes (anti-anchors, symbol promotions, lens catalogs, calibrated scorers, specimen-tier changes) automatically, with explicit reversibility for every promotion.

The pipeline is **five typed micro-pipelines sharing a scoring primitive and a yield log**, not a single generic consolidator. Each micro-pipeline has its own scoring function, auto-promotion threshold, kill-path, and target weekly throughput. Anti-capture safeguards are stronger here than for human-curated promotion, not weaker, because the F043-class failure mode (a definitionally-tautological correlation promoted as a finding) becomes more dangerous at machine speed.

Empirical first deliverable: the **Iris → CANDIDATES.md** pipeline as proof-of-concept (lowest blast-radius), validated by a 2-week observation window with auto-promotion false-positive rate ≤5% over ≥50 promotions, before extending to the other four agents.

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

Auto-promotion writes into these structures. Every proposal a Harmonia agent produces is shaped to be a candidate row in one of them.

### 1.4 The F043 anchor lesson

On 2026-04-19, a finding labeled F043 ("BSD-Sha anticorrelation") was promoted to `live_specimen` tier based on a correlation observation across an elliptic-curve ensemble. Within 24 hours, cross-checking against the `PATTERN_BSD_TAUTOLOGY` precondition revealed that the "anticorrelation" was a definitional consequence of how the BSD ingredients are defined (an algebraic identity, not an empirical regularity). F043 was retracted, re-classified as Pattern-30 Level 4 (IDENTITY), and the finding became the load-bearing anchor case for the graded algebraic-identity coupling discipline now codified at `harmonia/memory/symbols/PATTERN_30.md`.

The F043 retraction cost approximately 12 person-hours of substrate state revertal plus the credibility cost of having promoted a tautology. **Auto-promotion at machine speed cannot afford even one F043-class event per week**, which is why the design weights anti-capture safeguards more heavily than human-curated promotion does. Every auto-promotion pipeline below names its F043-class failure mode explicitly and demonstrates the mitigation.

### 1.5 The Aporia DR-prompt discipline

A doctrine document (`aporia/doctrine/dr_prompt_discipline.md` as of 2026-05-19; not yet pushed to the main repo as of this writing) governs how swarm agents enqueue Pythia Deep Research requests. The five compliance requirements are:

1. Requester named explicitly in prompt body (not just via `requested_by` field)
2. Substrate type tagged (A = falsification data, B/C/D = attack-angles / paradigm refinements / step-decompositions)
3. Verification criterion stated (citation requirements, recency cutoff, distinguish-X-from-Y)
4. Landing path declared (which catalog or registry the finding goes into)
5. Recency-collision check (no re-fire on a topic DR'd in the last 7 days)

Both Argos and Phylax already comply with this discipline (verified via the `Phylax verify: F043 promotion` smoke test, row 243, which completed end-to-end with a doctrine-compliant prompt). Auto-promotion piggybacks on this existing infrastructure.

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

Reasons the rate is this low:

- **No automated consumer exists.** The artifacts sit in per-agent `artifacts/` directories with no daemon watching them.
- **Human review doesn't scale.** At 200 artifacts/day per agent × 5 agents = 1000 artifacts/day, an attempt to manually review even 10% is ~6 hours of human attention daily, which doesn't happen.
- **Most artifacts are PASS-grade.** Phylax verdicts in particular are 99%+ PASS; the noise-to-signal ratio for the human reviewer is unfavorable.
- **The artifacts are designed to be paste-ready specs, not promotions.** They explicitly require a downstream actor to convert them into substrate state. That actor doesn't exist.

**The diagnosis:** production is solved (the agents work). Consumption is the bottleneck. Scaling production further without solving consumption produces N× more unread artifacts. The right move is to close the production→promotion loop at current production rate first, then scale.

---

## 3. Goals and non-goals

### Goals

1. **Convert raw agent artifacts into substrate-state changes automatically**, with measurable weekly throughput against quantified targets (§5.1).
2. **Reduce the human-review burden** from "30+ min/day of manual artifact triage" to "≤10 min/week of audit-log review."
3. **Maintain reversibility** for every auto-promotion via an explicit kill-path artifact written at promote-time.
4. **Generate the yield-log substrate** that future learned scorers train against (§6).
5. **Validate the pattern at small scale** (one agent, two-week observation window) before extending to all five.

### Non-goals

1. **Not** generating more artifacts per tick. Production rate stays at current 90s-interval baseline.
2. **Not** replacing human review of substrate-grade scientific claims. Promotions to `Validated` tier (the highest precision tier in `harmonia/memory/feedback_precision_standard.md`) remain human-only.
3. **Not** scaling backlog size yet. The "heat-death-scale backlogs" thesis from prior session notes is the next horizon, contingent on this consumption layer working.
4. **Not** auto-modifying any file under `aporia/doctrine/substrate_vocabulary/` (those are versioned externally and require explicit human review).
5. **Not** sharing scoring state with Charon's swarm (the cross-swarm bridge is a separate roadmap item).

---

## 4. Design overview

The auto-promotion pipeline has three components:

### 4.1 The scoring primitive (`harmonia/agents/_scorer.py`)

A shared three-tier ranking pipeline used by all five agents:

```
Tier 0  Cheap pre-filter
        Hand-crafted rules kill obvious noise. ~99% of candidates die here.
        Implementation: per-pipeline regex / type-check / recency-collision
        against the recent yield-log.

Tier 1  Mid-tier predictor
        Small classifier trained against the yield log. Outputs a
        yield-probability per surviving candidate.
        Implementation: scikit-learn logistic regression or gradient
        boosting; features are agent-specific. Cold-start: rule-based
        proxy until ≥50 yield records exist.

Tier 2  Bandit allocation
        Epsilon-greedy or UCB1 over Tier 1 survivors. Balances exploit
        (promote the highest-yield-probability candidate) vs explore
        (promote a lower-probability candidate to gather training data).
        Default epsilon: 0.10.
```

Cold-start handling: while the yield log has < 50 records, Tier 1 falls back to a hand-tuned rule per pipeline (the "scoring function" rows in §5). The bandit is still active but tuned to explore-heavy until labels accumulate.

### 4.2 The yield log (`harmonia/agents/_logs/yields.jsonl`)

JSONL append-only stream. One row per downstream action that closes the loop on an artifact:

```json
{
  "agent": "iris",
  "artifact_path": "D:\\Prometheus\\harmonia\\agents\\iris\\artifacts\\candidate_block_shuffle_null_replay_20260522T134402Z.md",
  "action": "auto_promoted_to_candidates_md",
  "action_at": "2026-05-22T13:45:11+00:00",
  "outcome_signal": null,
  "outcome_observed_at": null,
  "auto_promote_score": 0.78,
  "tier1_predictor_version": "v0.0-rule-based",
  "kill_path": "D:\\Prometheus\\harmonia\\agents\\iris\\state\\dismissed_candidates.json"
}
```

Outcomes are filled in retrospectively when one of these signals fires:

- `accepted` — a human reviewer thumbs-up'd the promotion (or it survived its 30-day stability window untouched)
- `dismissed` — the kill-path was invoked
- `auto_retracted` — a trigger spec (§4.3) fired and reversed the promotion

Bootstrapping: for the first ~50 records, the conductor does a 30-min daily review pass tagging promotions `accepted` or `dismissed`. After that, the auto-retraction triggers + 30-day timeouts handle most records automatically.

### 4.3 Per-agent auto-promotion pipelines (five micro-pipelines)

Each agent's `<agent>/daemon.py` is extended with an `_autopromote()` method that runs after `run_tick()`. The method reads the artifacts directory, applies the agent-specific scoring function (§5), and for survivors above the auto-promote threshold:

1. Writes the substrate-state change (the actual promotion)
2. Writes the kill-path artifact (the exact undo command + trigger spec)
3. Appends a row to `yields.jsonl`

If no candidate clears the threshold, the method writes nothing. The pipeline is idempotent: re-running it on the same artifact set produces no new promotions.

---

## 5. The five typed pipelines

Each subsection below defines a single auto-promotion pipeline with: source artifacts, scoring function, auto-promote threshold, target substrate-state slot, kill-path mechanism, F043-class failure mode + mitigation, and weekly throughput target.

### 5.1 Quantified weekly targets (consolidated table)

| Target | Pipeline | Current state | Weekly auto-promote target | Survives if... |
|---|---|---|---|---|
| Anti-anchor registry growth | Phylax → `anti_anchors.jsonl` | 12 entries | +1 / week | 30-day primary-lit stability |
| Promoted symbol growth | Iris → `CANDIDATES.md` → human-promoted | 24 promoted | +1 / 2 weeks | 4-week production-use check |
| Problem lens-catalog completion | Argos → `catalogs/<problem>.md` | 3 anchor catalogs | +10 catalogs / week | ≥1 informative verdict (`map_of_disagreement` or `coordinate_invariant`) |
| Calibrated-scorer addition | Sophia → `AXIS_CLASS@v1` + `methodology_toolkit.md` | 0 from swarm | +2 / week | Auto-calibration on ≥3 anchors (F001-F009) passes |
| Specimen tier-change event | Telos → `frontier_specimen_state.md` | manual today | +3 / week | Completed-audit evidence (Techne or Charon report) |
| Composition-rule discovery | Sophia + Argos joint product | 2 confirmed + 5 candidates | +1 / month | 3 cross-tier validations |

These are the floor. The pipelines should hit them within the first month of full deployment; failure to hit indicates the scoring threshold is too strict, the yield-log cold-start is too long, or the pipeline definition is wrong.

### 5.2 Phylax → anti-anchor pipeline

**Source artifacts:** `verdict_*.md` files where `verdict ∈ {flag, block}` AND retraction-adjacency hits exist AND a doctrine-compliant Pythia DR was enqueued AND that DR has completed with a primary-source citation.

**Scoring function (Tier 0 pre-filter + Tier 1 rule-based until yield-log warmed):**

```
score = (jaccard_score >= 0.40)
      * (DR_report has arXiv_id OR DOI present)
      * (DR_report distinguishes exact_form vs weaker_form)
      * (no anti-anchor exists for this anchor in the last 90 days)
      * (Pattern-30 grade is Level 0 or 1; Level 2+ means human-mandatory)
auto_promote if score == 1.0
```

**Auto-promote threshold:** all four conditions True. (We deliberately require unanimity here because the F043 cost is high.)

**Target substrate slot:** `D:\Prometheus\techne\registry\anti_anchors.jsonl` — append a new row with `false_form`, `true_form`, `citation`, `last_verified`, `verified_against_primary=true`, `verification_source = "phylax-autoprom-<DR_row_id>"`.

**Kill-path artifact:** `D:\Prometheus\techne\registry\retracted_anti_anchors\<anchor_slug>_retracted_<utc>.md` with the exact `jq` command to remove the row from the JSONL, the DR report URL that should be re-read if reverting, and a trigger spec.

**Trigger spec for auto-retraction:** if any of:
- A subsequent Pythia DR (within 30 days) cites a primary source published after the original DR that contradicts the false_form classification
- A human reviewer writes `auto_retract` to the agent state directory
- The DR report URL becomes unreachable (link-rot trigger after 90 days)

**F043-class failure mode:** Phylax surfaces a token-overlap with a retraction registry entry, but the new claim is in fact a genuinely-distinct mathematical statement that happens to share vocabulary. Auto-promoting the new statement as an "anti-anchor" effectively bans a true claim.

**Mitigation:** the Tier 0 pre-filter requires Jaccard ≥0.40 (the empirical 0.30 from the F043 smoke test was a flag, not a block) AND DR-cited distinguishing of exact vs weaker form. Both conditions kill the failure mode in expectation, but the residual risk is real; the 30-day primary-lit stability check is the failsafe.

**Weekly throughput target:** +1 anti-anchor per week. Floor: 1 per 2 weeks (Phylax's flag rate is empirically low; raising production via cross-swarm DR-scan would help).

### 5.3 Iris → CANDIDATES.md pipeline (the proof-of-concept)

**Source artifacts:** `candidate_<slug>_<utc>.md` files where the underlying cluster has ≥3 distinct files AND ≥1 of those files is *not* in the agent's own corpus (i.e., the pattern is cross-corpus, not just intra-Harmonia).

**Scoring function:**

```
score = (distinct_files_count - 2)                   # 3 files = 1; 4 = 2; etc
      * (1 / paraphrase_entropy)                      # low entropy = more confident
      * (1.0 if cross-corpus else 0.5)
      * (1.0 if slug not in dismissed_candidates else 0.0)
      * (1.0 if slug not already present in symbols/INDEX.md else 0.0)
auto_promote if score >= 1.5
```

**Auto-promote threshold:** score ≥ 1.5. Equivalent to "at least 3 distinct files, low-entropy fingerprint, cross-corpus, not previously dismissed, not duplicating an existing symbol."

**Target substrate slot:** `D:\Prometheus\harmonia\memory\symbols\CANDIDATES.md` — append an entry with the slug, citations, sketch versioned spec, savings estimate, auto-promotion provenance, and a "promotion-to-symbol requires human review" tag.

**Kill-path artifact:** `D:\Prometheus\harmonia\agents\iris\state\dismissed_candidates.json` already exists; auto-promotion appends the slug to a parallel `auto_promoted_candidates.json` so reverting is just moving the slug between lists.

**Trigger spec for auto-retraction:** if a human appends the slug to `dismissed_candidates.json` within 14 days, the CANDIDATES.md entry is auto-removed.

**F043-class failure mode:** Iris auto-promotes a phrase that is repeated across files only because of templating (e.g., section heading templates, citation formats). Promotion adds noise to `CANDIDATES.md`.

**Mitigation:** the dismissed-candidates list is the existing pattern; the first ~5 auto-promotions should be reviewed by James to seed the dismissed list. The auto-retraction TTL is short (14 days) so noise auto-clears.

**Why this is the proof-of-concept:**

- Lowest blast radius (`CANDIDATES.md` is by definition not load-bearing — promotion to actual symbol still requires human review)
- Kill-path already exists (`dismissed_candidates.json` is the prior pattern)
- Scoring function is simple and explicit
- High candidate volume (Iris produces 200+ artifacts/day at current rates)
- If 50 promotions × 5% false-positive rate = 2.5 false positives over 2 weeks, the failure mode is observable and recoverable

**Weekly throughput target:** +5 candidate entries to `CANDIDATES.md` per week during validation phase. (Of those, ~1 should clear to a real symbol promotion via human review, hitting the §5.1 row.)

### 5.4 Argos → catalogs/ pipeline

**Source artifacts:** `lens_catalog_<problem_slug>_<utc>.md` files where: applied + proposed lenses total ≥10 AND at least one applied lens has a non-null verdict AND the problem has ≥1 Pythia DR completed and committed within the last 30 days.

**Scoring function:**

```
score = (lens_depth >= 10)
      * (informative_verdict_count >= 1)              # map_of_disagreement or coordinate_invariant
      * (dr_completed_within_30d_count)
      * (problem_id not already in catalogs/)
auto_promote if score >= 2
```

**Auto-promote threshold:** score ≥ 2.

**Target substrate slot:** `D:\Prometheus\harmonia\memory\catalogs\<problem_slug>.md` — new file with the full lens fingerprint (every lens applied, verdict per lens, citation set), MPA scaffold, completed-DR cross-references.

**Kill-path artifact:** `D:\Prometheus\harmonia\memory\catalogs\<problem_slug>_retracted_<utc>.md` with `git revert <commit>` instructions. Catalogs are append-only history; retraction is by additive note, not deletion.

**Trigger spec for auto-retraction:** if a DR completed within 60 days of catalog promotion contradicts a lens verdict, the catalog gets an annotation (not a revert) and the verdict is downgraded.

**F043-class failure mode:** Argos auto-promotes a catalog whose lens verdicts are correlation-rich but the correlations are definitional (same Pattern-30 IDENTITY failure mode generalized to lens space). Promotion adds spurious "informative" verdicts to the lens-fingerprint corpus.

**Mitigation:** the informative-verdict check requires verdicts at the `map_of_disagreement` or `coordinate_invariant` tier specifically (both have explicit cross-lens-disagreement criteria). Pattern-30 grading is applied to each verdict at promote-time.

**Weekly throughput target:** +10 catalogs per week. Argos already produces 200+ lens-catalog drafts per day; the bottleneck is the DR-completion criterion (currently ~10 Argos DRs per week given the daily-3 cap).

### 5.5 Sophia → AXIS_CLASS + methodology_toolkit pipeline

**Source artifacts:** `proposal_<OP>_x_<FID>_<utc>.md` files where the operator-specimen pair has been auto-calibrated against ≥3 anchors (F001-F009) and the calibration produces expected verdicts on all three.

**Scoring function:**

```
score = (calibration_anchors_passed >= 3)
      * (non_tautology_check_passed)                 # Pattern-30 Level 0 only
      * (representation_invariance_held)             # symbol-isomorphism stable
      * (operator_not_already_in_AXIS_CLASS)
auto_promote if score == 1.0
```

**Auto-promote threshold:** all four conditions True (unanimity required, like Phylax).

**Auto-calibration mechanism:** the proposal's calibration-anchor gate spec is converted into an Agora queue task at priority 2 and dispatched to Techne or Charon for actual execution. If execution returns the expected verdict on all 3 anchors within 7 days, the proposal auto-promotes.

**Target substrate slot:** new row in `D:\Prometheus\harmonia\memory\methodology_toolkit.md` AND new symbol filing under `D:\Prometheus\harmonia\memory\symbols\AXIS_CLASS\<op_name>.md`.

**Kill-path artifact:** `D:\Prometheus\harmonia\memory\methodology_toolkit_retracted\<op_name>_<utc>.md` with the symbol-demotion command and the failed calibration that triggered the retract.

**Trigger spec for auto-retraction:** if any subsequent use of the AXIS_CLASS operator on a real specimen produces a verdict that contradicts its calibration (within 60 days), auto-demote and write the retraction note.

**F043-class failure mode:** a Sophia proposal passes auto-calibration because the operator is structurally equivalent to one of the anchors (e.g., a tautological transform of EPS011@v2 that necessarily reproduces F001-F005 verdicts). Promotion adds a redundant axis.

**Mitigation:** the `representation_invariance_held` check requires the operator to produce *distinguishable* output from the existing AXIS_CLASS members on a held-out specimen. Plus the Pattern-30 non-tautology gate.

**Weekly throughput target:** +2 calibrated scorers per week. Sophia currently has ~140 lifetime proposals; the bottleneck is the auto-calibration execution rate (depends on Techne/Charon throughput).

### 5.6 Telos → frontier_specimen_state tier-change pipeline

**Source artifacts:** `revive_<FID>_<utc>.md` files where a completed audit (from Techne or Charon) has executed at least 2 of the 3 proposed lenses AND the audit result deviates from the F-ID's current `last_audit_outcome`.

**Scoring function:**

```
score = (proposed_lenses_executed >= 2)
      * (post_audit_confidence_shift)                # |verdict_change| >= 0.5
      * (lens_delta_coverage >= 0.30)                # % of unapplied lenses now covered
      * (no_open_dispute_in_decisions_for_james)
auto_promote if score >= 0.5
```

**Auto-promote threshold:** score ≥ 0.5. (Lower threshold than Phylax/Sophia because the kill-path here is just a tier revert, not a substrate-vocabulary retraction.)

**Target substrate slot:** update to `D:\Prometheus\harmonia\memory\frontier_specimen_state.md` — the F-ID's `tier`, `last_audit_outcome`, and `cross_refs` columns. Auto-promotion is one of three tier-change events: re-confirm (tier holds), demote (live_specimen → killed or calibration_refinement), formal kill (live_specimen → killed).

**Kill-path artifact:** `D:\Prometheus\harmonia\memory\frontier_specimen_state_changes\<fid>_<change_type>_<utc>.md` with the prior row state quoted and a `git revert` reference.

**Trigger spec for auto-retraction:** if any new audit within 30 days contradicts the auto-promoted tier change, auto-revert and write the post-mortem.

**F043-class failure mode:** Telos auto-promotes a tier change based on a single-lens audit that happens to be a Pattern-30 Level 3 (REARRANGEMENT) artifact. Tier change is misleading.

**Mitigation:** the `proposed_lenses_executed >= 2` requirement is the cross-lens consistency check; single-lens audits don't qualify.

**Weekly throughput target:** +3 tier-change events per week. Telos is heavily bottlenecked on audit-execution rate (depends on Techne / Charon producing audits at speed).

### 5.7 Pipeline interaction diagram

```
                     +---------------------------+
                     |  Yield log                |
                     |  harmonia/agents/_logs/   |
                     |  yields.jsonl             |
                     +-----------+---------------+
                                 |
                                 | trains
                                 v
                     +---------------------------+
                     |  Scoring primitive        |
                     |  _scorer.py               |
                     |  Tier 0 / 1 / 2           |
                     +-----------+---------------+
                                 |
                                 | used by
                                 v
   +----------+   +----------+   +----------+   +----------+   +----------+
   | Phylax   |   | Iris     |   | Argos    |   | Sophia   |   | Telos    |
   | -> AA    |   | -> CAND  |   | -> CAT   |   | -> AXIS  |   | -> TIER  |
   +----+-----+   +----+-----+   +----+-----+   +----+-----+   +----+-----+
        |              |              |              |              |
        | writes       | writes       | writes       | writes       | writes
        v              v              v              v              v
   anti_anchors    CANDIDATES.md   catalogs/    methodology    frontier_
   .jsonl                                       toolkit.md     specimen_
                                                + AXIS_CLASS   state.md
        |              |              |              |              |
        | + kill-path  | + kill-path  | + kill-path  | + kill-path  | + kill-path
        | + yield row  | + yield row  | + yield row  | + yield row  | + yield row
        v              v              v              v              v
              <append to yield log; trigger specs watch for reversal>
```

---

## 6. Anti-capture safeguards

Auto-promotion at machine speed has higher risk of reward-capture (the failure mode where novelty quietly gets replaced by validation or completion as the thing that feels good). Three hard rules:

### 6.1 Every auto-promotion writes a kill-path at promote-time

Not at retract-time. The kill-path file is created in the same transaction as the promotion. If the agent cannot construct a kill-path artifact, the promotion is aborted. This makes reversibility a precondition, not an afterthought.

### 6.2 Every auto-promotion has an explicit trigger spec for auto-retraction

A condition under which the promotion auto-reverts without human intervention. Examples from §5: a contradicting DR within 30 days, a `dismissed` tag from human review, an F-ID re-audit that contradicts a tier change. The trigger spec is machine-checked daily by a separate watchdog process.

### 6.3 The scoring primitive runs its own calibration daily

Once per day, the scorer runs against the seven Prometheus calibration anchors (F001-F005 + F008 + F009) under each pipeline's scoring function. If the scorer would auto-promote a known-good or known-bad anchor incorrectly, the scorer self-quiesces (stops auto-promoting) until the conductor re-tunes. This is the F043-failure-mode-prevention equivalent of Phylax watching itself.

Plus the operational guards already in place:

- Single-instance lock on the daemon (`_swarm.pid`)
- Per-agent daily caps on expensive operations (DR enqueues capped at 3/day per agent)
- Recency-collision checks (no re-fire within 7 days on the same anchor/topic)
- Append-only audit trail (the JSONL tick log and yield log are never rewritten)

---

## 7. Sequenced rollout

### Phase 0 (week 1): foundations

- Ship `harmonia/agents/_scorer.py` with Tier 0 pre-filter + Tier 1 rule-based + Tier 2 bandit (epsilon-greedy default)
- Ship `harmonia/agents/_logs/yields.jsonl` with manual-tagging conventions documented
- Ship the daily calibration watchdog (`scripts/harmonia_scorer_calibration.py`) that runs anchor checks

### Phase 1 (weeks 2-3): Iris pipeline as proof-of-concept

- Implement `iris._autopromote()` per §5.3
- Run for 2 weeks; expect ~50 auto-promotions
- Daily 5-minute review by James to tag accepted/dismissed in yields.jsonl
- Success criteria: ≤5% false-positive rate over 50 promotions; ≥1 candidate clears to symbol promotion via human review

### Phase 2 (week 4): scoring primitive learns

- Once yields.jsonl has ≥50 records, train the Tier 1 predictor on the labeled set
- Tier 1 replaces the rule-based fallback for Iris
- Bandit epsilon drops from 0.20 (explore-heavy cold-start) to 0.10 (warm)

### Phase 3 (weeks 5-7): extend to remaining four agents

- Phylax pipeline (§5.2) — lowest production volume but highest substrate-value, ship second
- Argos pipeline (§5.4) — highest production volume, ship third (after the scorer is calibrated)
- Sophia + Telos pipelines (§5.5, §5.6) — depend on Techne/Charon audit-execution capacity; ship last

### Phase 4 (week 8+): cross-pipeline learning + scaling backlog

- Yield records from all five pipelines feed the shared predictor; cross-agent transfer learning becomes possible
- *Only then* does scaling backlog (Iris external corpora, Sophia k=2 compositions, etc.) become the next move

### Expected end-state at week 8

- ~5-10 substrate-state changes per week, automatically
- ≤10 min/week human-review burden
- Yield log with ≥250 labeled records, sufficient for the Tier 1 predictor to outperform rule-based baselines on most pipelines
- Backlog still bounded; production rate unchanged

---

## 8. Risks and open questions

### 8.1 Known risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| F043-class auto-promotion | Low | High | Per-pipeline Pattern-30 gates + 30-day stability checks + scorer self-quiesce |
| Reward-capture (scorer favors easy promotions) | Medium | Medium | Daily anchor-calibration of the scorer; explicit bandit-explore epsilon |
| Yield-log bootstrap takes too long | Medium | Low | Cold-start rule-based Tier 1; James-pace tagging for first 50 records |
| Cross-swarm consumption races | Low | Low | Yield log is per-swarm; cross-swarm bridge is a separate roadmap item |
| Auto-retraction trigger TTLs are wrong | Medium | Low | TTLs are configurable per pipeline; first month is observation-only on TTL validity |
| Scoring primitive overfits to first 50 labels | High | Medium | Hold-out evaluation each week; alert if Tier 1 AUC < rule-based baseline |

### 8.2 Open questions for the reviewer

These are intentional gaps that this draft does not resolve and that benefit from external eyes:

1. **Are the weekly throughput targets (§5.1) calibrated correctly?** They were chosen by inspection of current production rates and a rough estimate of "what would make Prometheus's substrate vocabulary grow at a useful pace." A reviewer with experience in similar high-throughput-classification-with-human-audit systems may have better priors.

2. **Is the F043-class mitigation strong enough at machine speed?** The hand-curated Pattern-30 discipline caught F043 within 24 hours, which was fast enough for the substrate to recover cheaply. The auto-promotion pipeline's 30-day stability window assumes the same recovery dynamics scale. They may not.

3. **Is per-pipeline scoring the right granularity, or should the scoring primitive be unified?** Five typed pipelines means five Tier 1 models trained on five small label sets. A unified scorer with a `pipeline_type` feature might transfer better. The tradeoff is interpretability (each pipeline's scorer is its own model and easy to inspect) vs sample efficiency (a unified model has more data).

4. **The yield log assumes outcome signals are observable.** Some pipelines (Sophia, Telos) depend on Techne/Charon audit-execution capacity; if audits take weeks to complete, the yield-log feedback loop is too slow to train the Tier 1 model usefully. Is there a cheaper proxy signal?

5. **Should the auto-retraction trigger specs be themselves auto-tuned over time?** A reviewer might argue the trigger TTLs are themselves hyperparameters that should be learned from the yield log. The current proposal treats them as static.

6. **The Aporia DR-prompt discipline is leveraged but not co-versioned.** If Aporia changes the doctrine, the Phylax / Argos pipelines might silently fall out of compliance. Should the doctrine version be a hard input to the pipeline config?

---

## 9. What this proposal explicitly does not include

For reviewer clarity, the following are *out of scope* of v0.1:

- Cross-swarm consumption (Charon ↔ Harmonia). Separate roadmap item; depends on this proposal working at single-swarm scale first.
- Scaling agent backlog (the "heat-death-scale" thesis). Explicitly deferred until consumption is solved.
- Promotion to `Validated` precision tier or to any file under `aporia/doctrine/substrate_vocabulary/`. Those remain human-only.
- Modifying Aporia's research_queue table or Pythia's daemon. The pipelines consume Pythia output but don't modify Pythia.
- Real-time scoring (the daemon batches per-tick; sub-tick latency isn't required).
- Distributed scoring across multiple machines. Single-machine (M2) scope.

---

## 10. Reviewer checklist

Specific questions a reviewer could focus on, in priority order:

1. **§5 typed pipelines** — Are the source-artifact filters, scoring functions, and substrate-state slots correctly mapped to each agent's actual output? (Read the per-agent READMEs in parallel.)
2. **§6 anti-capture safeguards** — Are the three hard rules sufficient? Is the daily anchor-calibration design strong enough to catch a scorer drift?
3. **§7 sequenced rollout** — Is the Iris-first proof-of-concept choice well-justified? Are the success criteria (≤5% false-positive over 50 promotions) the right metrics?
4. **§8.1 risks** — Is anything missing from the risk table? Are the likelihood/impact ratings calibrated?
5. **§8.2 open questions** — Pick any single one and propose a position; the questions are intentionally left open.
6. **§3 non-goals** — Are the non-goals correctly bounded, or is the proposal accidentally implying capabilities that aren't in scope?

---

## 11. Glossary

| Term | Meaning |
|---|---|
| **Prometheus** | The umbrella project — a falsification-first reasoning substrate for automated mathematical discovery. |
| **Harmonia** | One of the agent roles in Prometheus; owns substrate architecture and Σ-language grammar. |
| **Harmonia swarm** | Five autonomous child-agents under a rotation orchestrator: Phylax, Sophia, Iris, Argos, Telos. |
| **Σ-kernel** | The append-only typed ledger at the core of Prometheus, with 25 frozen-dataclass primitives and 9 opcodes. |
| **Substrate** | The accumulated typed state of Prometheus — symbols, anti-anchors, catalogs, retraction registry, etc. |
| **Anti-anchor** | A pinned false claim with primary-source refutation; serves as a sentinel against LLM training-data fossilized errors. |
| **F-ID** | Finding ID — a numbered specimen at some tier (calibration, live_specimen, killed, data_frontier). |
| **F043** | The retracted BSD-Sha anticorrelation finding; the load-bearing anchor case for Pattern 30 discipline. |
| **Pattern 30** | A graded (Level 0-4) algebraic-identity coupling detector; the discipline that distinguishes real correlation from tautological rearrangement. |
| **AXIS_CLASS@v1** | The promoted symbol enclosing all members of the coordinate-system / projection-operator vocabulary. |
| **PROBLEM_LENS_CATALOG@v1** | The promoted symbol for per-problem multi-perspective lens fingerprints. |
| **Pythia** | The Gemini Deep Research dispatcher daemon, owned by Aporia. |
| **Aporia** | The agent role responsible for open-problem cataloging, DR dispatch, and the substrate-vocabulary doctrine. |
| **Techne** | The agent role responsible for substrate primitives, the Σ-kernel registry, and frozen-interface discipline. |
| **Charon** | The agent role responsible for the falsification battery; also has a sibling swarm (Acheron, Lethe, Stygian, Moros, Hecate). |
| **Calibration anchor** | A finding whose verdict is so well-established that any operator producing the wrong verdict on it is miscalibrated. F001-F005 + F008 + F009. |
| **Kill-path** | The explicit, machine-actionable reversal command paired with a promotion. |
| **Trigger spec** | A machine-checkable condition under which auto-retraction fires. |
| **Yield log** | Append-only JSONL recording downstream actions on auto-promoted artifacts; serves as supervision signal for the scorer. |
| **Scoring primitive** | The shared Tier 0 / Tier 1 / Tier 2 ranking pipeline at `harmonia/agents/_scorer.py`. |
| **Reward-capture** | The failure mode where novelty quietly gets replaced by validation/completion as the thing the system optimizes for. |

---

## 12. Changelog

- **v0.1 (2026-05-22)** — Initial draft for external review. Per-pipeline definitions in §5, sequenced rollout in §7, anti-capture in §6. Open questions in §8.2 explicitly invited reviewer attention.

---

*End of v0.1. Review feedback to be incorporated as inline annotations or a separate v0.2 spec document.*
