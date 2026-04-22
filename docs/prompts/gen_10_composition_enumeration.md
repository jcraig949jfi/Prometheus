# Generator #10 — Operator Composition Enumeration

**Status:** Tier 1 (low infra, days).
**Role:** Producer.
**Qualification:** Harmonia session; familiarity with the symbol registry.
**Estimated effort:** 2–3 ticks for scorer + first enumeration pass.

---

## Why this exists

Every promoted symbol composes with every other symbol type-compatible with it. As the registry grows, the combinatorial space of compositions grows quadratically, and most compositions have never been tried. Manually selecting which compositions to run is attention-limited. A systematic enumeration, scored by expected information gain, surfaces compositions that no individual researcher would have proposed but that are empirically informative.

Current registry: 5 promoted symbols (NULL_BSWCD@v2, Q_EC_R0_D5@v1, LADDER@v1, EPS011@v2, SIGNATURE@v1). As #2 null-family adds 4 more nulls, and #3 adds adapter P-IDs, and new `computation` and `dataset` symbols land, the composition space explodes. This generator keeps the exploration tractable by ranking.

---

## Infrastructure to build

### 1. Composition type-compatibility rules

Not every pair composes. Rules:

| Composition | Validity |
|---|---|
| `operator ∘ dataset` | valid — apply operator to data |
| `operator ∘ operator` | valid only if output-type-input-type matches |
| `dataset ∘ dataset` | INVALID (unless one is a filter — and filter is an operator) |
| `shape ∘ signature` | INVALID (no runtime semantics) |
| `constant ∘ anything` | INVALID (constants are not callable) |
| `signature ∘ anything` | INVALID (signatures are schemas, not values) |

Validator implementation: `harmonia/composers/validator.py`. Returns `{valid: bool, reason: str}` for each proposed composition.

### 2. Composition-scoring function

Score = expected information gain per compute unit. Components:

- **Novelty:** how many (F, P) tensor cells would this composition touch that are currently untested?
- **Resolving prior:** if the operators in the composition have resolved anything before (via their prior SIGNATUREs), that's a prior signal.
- **Stratification fanout:** if the composition produces stratified output, count the expected number of sub-cells.
- **Cost:** expected runtime from the component operators' recorded runtimes (in their promoted metadata).

Return `score = (novelty + resolving_prior + 0.5 * stratification_fanout) / sqrt(cost)`.

Implementation: `harmonia/composers/scorer.py`.

### 3. Enumeration driver

Implementation: `harmonia/composers/enumerate.py`. Takes the current symbol registry state, produces the full type-valid composition set, scores it, emits the top-N as Agora tasks.

---

## Process

1. Implement validator + scorer + driver per above.
2. Run driver against the current registry. Expected output: some number of compositions in the tens (small registry today).
3. For each top-N composition, seed an Agora task at priority derived from score.
4. As registry grows (#2 adds 4 nulls; #3 adds adapter P-IDs; etc.), re-run the driver. It should be idempotent — compositions already run don't re-enqueue.
5. Every completed composition run updates the composition's recorded runtime (feeds back into scorer).

---

## Outputs

- `harmonia/composers/` package with validator, scorer, driver.
- `harmonia/memory/composition_queue.md` — sorted top-50 compositions with scores and status.
- Agora tasks seeded for top-N compositions.
- `harmonia/memory/composition_results_log.md` — completed compositions with their verdicts + any new F-IDs or cells they produced.

---

## Epistemic discipline

1. **Top-scored ≠ top-interesting.** The scorer is a heuristic. A composition with high novelty but low resolving prior is a gamble; a composition with low novelty but high resolving prior is a safe probe. The queue lets the conductor pick; the scorer only ranks.
2. **Pattern 30 gate applies to every composition that produces a correlation.** If the composition is `correlation_scorer ∘ dataset_with_algebraically_coupled_cols`, it BLOCKS.
3. **Type compatibility is a hard constraint.** The validator rejects, not warns. If someone finds a composition the validator wrongly rejects, they submit a rule exception, not a bypass.
4. **Keep a "retired compositions" list.** Compositions that consistently return noise after ≥ 3 tries should be deprioritized, not re-queued.

---

## Acceptance criteria

- [ ] `harmonia/composers/` package shipped with validator + scorer + driver + tests.
- [ ] First enumeration run produces a ranked queue.
- [ ] `composition_queue.md` committed with top-50 listing.
- [ ] At least 10 Agora tasks seeded from the top of the queue.
- [ ] One worked example: a composition enumerated, claimed, run, verdict recorded.
- [ ] Commit cites this spec.

---

## Composes with

- **#1 Map-Elites** (when live) — Map-Elites selects from this generator's queue, prioritizing by behavior-cell novelty.
- **#2 null-family** — every null added to the family spawns N new compositions to enumerate.
- **#6 pattern auto-sweeps** — gate on every composition's result before tensor landing.
- **#3 cross-domain transfer** — adapter P-IDs extend the composition space multiplicatively.

---

## Claim instructions (paste-ready)

> Claim `gen_10_composition_enumeration_seed`. Implement `harmonia/composers/` (validator + scorer + driver) per `docs/prompts/gen_10_composition_enumeration.md`. Run first enumeration; commit `composition_queue.md`. Seed top-10. Post `WORK_COMPLETE` with queue length and top-5 compositions.

---

## Version

- **v1.0** — 2026-04-20 — initial spec from generator pipeline v1.0.
