# Harmonia swarm roadmap

> Cross-cutting plan for increasing the program-value of the five children (Phylax, Sophia, Iris, Argos, Telos). Updated 2026-05-22.

This document is the meta-layer above the per-agent READMEs. It identifies the patterns common to all five agents, names the binding constraints on their value-to-Prometheus, and proposes a sequenced set of upgrades. The per-agent READMEs cover each agent's local roadmap; this doc names the leverage that lifts all five at once.

## The pattern across all five agents

After ~54 hours of continuous operation and ~2200 artifacts produced (~440 per agent), three structural patterns are now visible:

### 1. Every agent is good at production. None has a consumer.

Each of the five agents produces well-formed, paste-ready artifacts:
- Phylax verdict envelopes with adjacency hits + Pattern-30 grades + DR-prompts
- Sophia 5-gate tensor-admission proposals with calibration sanity gates
- Iris symbol-promotion candidates with citation sets and savings estimates
- Argos lens-catalog drafts with multi-perspective-attack scaffolds
- Telos revive-task specs with seedable Agora task descriptions

Of these ~2200 artifacts, the number that have been read by a downstream actor and turned into formal substrate state is approximately **one** (Phylax's row-243 DR completed; the conductor hasn't promoted any of Iris's candidates, run any of Sophia's scorers, promoted any of Argos's catalogs, or scheduled any of Telos's revive audits).

The agents are not the bottleneck. **The consumption side is.** Without consumers, the artifacts are technically "production" but practically "noise on disk."

### 2. Every agent's selection is heuristic. None has a learned scorer.

Sophia picks lexicographically smallest untried pair. Telos picks top-stalled-by-date with anti-greedy. Argos picks under-lensed by lens-deficit count. Iris picks the next file window by cursor. Phylax picks oldest-not-audited-symbol.

None of these are scored. None of them learn from outcomes. The agents have no idea which of their picks ever produced anything downstream. This is the precondition the *backlog-extension thesis* (see prior session notes) names: scaling backlogs to "heat-death" size is only worth doing once selection-pressure can rank candidates faster than production can generate them.

### 3. The biggest agent backlogs are external; the smallest are internal.

| Agent | Backlog source | Native depth |
|---|---|---|
| Argos | Aporia's open-problem queue + lens stacks | 1100+ problems × O(C(10,3)) stacks ≈ heat-death |
| Iris | Filesystem corpus (6 dirs, 339 files now) | clamped at MAX_CORPUS_SIZE=10000 |
| Phylax | Σ-kernel PROMOTE events + git log + DR reports | episodic; falls through to ~24 promoted symbols |
| Sophia | (operators × specimens) cartesian | 140 pairs (exhausted after 17h) |
| Telos | Stalled F-IDs above threshold | ~5 live + ~25 killed |

Sophia and Telos exhaust their internal backlogs fast. Phylax depends on external promotion events being produced (which is currently rare). Iris and Argos have multi-day native depth.

## The four cross-cutting upgrades

### Upgrade 1 — Shared scoring primitive (`harmonia/agents/_scorer.py`)

This is the foundational missing piece. Every agent uses a heuristic to pick the next item from its backlog; a learned scorer would lift all five at once.

Sketch shape:

```python
class HarmoniaScorer:
    """Three-tier ranking pipeline shared across agents.

    Tier 0 (cheap pre-filter): hand-crafted rules kill obvious noise (regex,
            type-check, recency-collision). ~99% of candidates die here.
    Tier 1 (mid-tier predictor): a small classifier trained against the
            yield log — did this artifact lead to a downstream action?
            Outputs a yield-probability per candidate.
    Tier 2 (bandit allocation): epsilon-greedy or UCB1 over the Tier 1
            survivors so the agent balances exploit-vs-explore.
    """
    def pre_filter(self, candidates: list[dict]) -> list[dict]: ...
    def predict_yield(self, candidate: dict) -> float: ...
    def pick(self, candidates: list[dict], k: int = 1) -> list[dict]: ...
```

Per-agent integration: each agent subclasses HarmoniaScorer to define its `pre_filter` and `featurize(candidate)` for the predictor. The bandit and the yield log are shared infrastructure.

Cost: ~1 week of implementation work for the primitive, then ~1 day per agent to wire it in.

### Upgrade 2 — Yield log (`harmonia/agents/_logs/yields.jsonl`)

Without outcome data, the Tier 1 predictor has nothing to train against. The yield log is a JSONL append-only stream of `{agent, artifact_path, downstream_action, action_timestamp, outcome_signal}` records — one row per downstream action that closes the loop on an artifact.

Bootstrapping the yield log:

- **Manual seed** — for the first ~50 records, the conductor (or a small daily review pass) tags artifacts with `accepted`, `dismissed`, or `ignored`. That's the supervision signal the Tier 1 model trains on.
- **Auto-detected outcomes** — when an artifact's content matches a state change in the substrate (e.g., a `harmonia/memory/symbols/CANDIDATES.md` entry that quotes one of Iris's candidate slugs; a `retraction_registry.md` update that cites one of Phylax's verdict files), auto-emit a `yields.jsonl` row.

Cost: ~2 days to implement the auto-detection logic. The manual seeding is cheap (~30 min/day for a week).

### Upgrade 3 — Consolidator agent

Five agents producing artifacts but no agent promoting them is the symptom. The cure is a sixth agent whose entire job is to read all five `<agent>/artifacts/` directories on a slower cadence (hourly or daily), batch the strongest candidates by type, and promote them to formal substrate state:

- Iris candidates → `harmonia/memory/symbols/CANDIDATES.md` entries
- Argos catalogs → `harmonia/memory/catalogs/<problem_slug>.md` files
- Sophia proposals → Agora queue tasks for Techne/Charon scorer implementation
- Telos revive tasks → Agora queue tasks at appropriate priority
- Phylax FLAG/BLOCK verdicts → `techne/registry/anti_anchors.jsonl` candidate entries

The consolidator emits a single artifact per tick: a `promotion_batch_<utc>.md` listing what it promoted and why. That artifact is itself reviewable.

Cost: ~1 week for the first version (the type-specific batching logic is the bulk of the work).

### Upgrade 4 — Cross-swarm bridge

Charon's swarm (Acheron, Lethe, Stygian, Moros, Hecate) is producing its own DR demand and document corpus. Currently the two swarms run in parallel without consuming each other's output. Three concrete bridges would compound the mesh:

- **Iris scans `charon/agents/*/artifacts/`** — Charon's outputs are un-compressed prose, exactly the surface Iris should be working on
- **Phylax verifies Stygian's anti-anchor proposals** — Stygian's `forward false-anchor hunts` (visible in the Pythia queue as `BL-C-*`) are pre-verified anti-anchor candidates; Phylax's adjacency-check is the natural validator
- **Argos consumes Stygian's primary-literature surveys** — when Stygian produces a survey for a problem, Argos can use that as the prior-art baseline before proposing new lenses (deduplication of DR effort)

Cost: ~3 days for the bridge plumbing (mostly directory-watching + cross-swarm artifact-format adapters).

## Per-agent backlog expansion (quick reference)

For when an agent specifically needs more work:

### Phylax
- Scan Charon's `forward false-anchor hunts` and `coordinate-collision hunts` as inbound sources
- Subscribe to Pythia DR completions (not just enqueues) — re-audit when a DR contradicts a registered anti-anchor

### Sophia
- Add the 24 promoted symbols to the operator pool: 10 → 34 operators, 140 → 476 pairs
- k=2 operator compositions: 34² × 14 specimens ≈ 16K pairs
- Cross-disciplinary operator transplants from external corpora

### Iris
- External corpora already expanded (339 files); next step is arXiv abstracts (Pythia DR reports are a foothold) and Mathlib4 docstrings
- Relax fingerprint algorithm: tf-idf or learned embeddings instead of sorted-token-bag

### Argos
- Lens-stack depth: top-5 or top-7 per pick instead of top-3
- Recursive depth: ingest completed DR reports → propose follow-up lenses
- Cross-swarm: consume Stygian's surveys

### Telos
- Per-cell granularity (F-ID × P-ID combinations)
- Killed-F-ID revisit on regular cadence (1 in N ticks), not just fallback
- DR enqueue for "has anyone applied lens X to specimen-family Y" questions

## Consumers and transformers (new agents that would add value)

These are net-new agents (or extensions to existing ones) whose entire job is to act on the swarm's output. They sit *above* the five children in the value chain.

### Consolidator (Upgrade 3 above)
Promotes batches of agent-output into formal substrate state. The single highest-leverage net-new agent.

### Yield-tracker
Watches the substrate for state changes that match agent artifact content; emits `yields.jsonl` rows. Foundation for the learned scorer.

### Triage
Reads all five agents' artifacts daily, applies the Tier-1 scorer, produces a one-page prioritized list for human review. Replaces the "I'll open 50 random artifacts when curious" workflow with "I'll open the 5 highest-scoring artifacts this morning."

### Auto-promoter
For the small set of artifacts that score above a high-confidence threshold against a calibrated test set, file the promotion automatically. Anti-capture safeguard: must include a human-reviewable kill-path artifact so the auto-promotion can be reversed cheaply.

### Cross-swarm bridge (Upgrade 4 above)
Multi-agent ecosystem at scale. The mesh is real once Charon and Harmonia consume each other's output.

### Calliope-equivalent for the swarm
Calliope already produces daily NotebookLM narratives from commit bodies. A swarm-equivalent that reads the JSONL tick log + artifact deltas + agent state changes and emits a daily prose summary would replace the ad-hoc reports I was producing every 90 minutes during the monitoring phase.

## Sequenced plan

Priority order, all assuming the user can pick or veto any item:

1. **Yield log + manual seeding (Upgrade 2)** — 2 days. Foundation; nothing else compiles cleanly without an outcome signal.
2. **Sophia operator-pool expansion** — 30 min. Quick win, lifts Sophia out of meta-task fallback mode.
3. **Telos per-cell granularity** — 1 day. Multiplies Telos's addressable backlog by ~30.
4. **Consolidator agent — Iris path first (Upgrade 3 narrow)** — 3 days. Pick the highest-value type (Iris candidates → CANDIDATES.md) and ship that one transformer. Validates the pattern before generalizing.
5. **Shared scoring primitive (Upgrade 1)** — 1 week. Built on top of the yield log.
6. **Cross-swarm bridge (Upgrade 4)** — 3 days. Once Harmonia's consolidator is proven, the mirror for Charon's output is the same shape.
7. **Auto-promoter** — 2 days, only after scoring primitive is calibrated against ≥50 yield records.

## What this roadmap is NOT

It's not a plan to make the agents produce more. They produce plenty already — 41 artifacts/hour at steady state. It's a plan to make the artifacts actually compound into substrate value.

It's also not the full backlog-extension thesis (see prior session: "heat-death-scale backlogs that force prioritization to become the work"). That comes after this roadmap — first close the loop on production-to-promotion at current scale, then scale the backlog by 1000x. Scaling first would just produce 1000x the artifacts nobody reads.
