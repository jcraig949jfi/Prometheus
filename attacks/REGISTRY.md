# Attack Registry — how claims die here

**Created:** 2026-08-20 · **Maintainer:** any seat (append-only; edits to existing entries need
a reason line) · **Consumed by:** watchers (finding rows cite `defect_class` from this file),
review-prompt authors (banned-methods forcing), the scorecard (decoy classes).
**Rule:** one entry per *defect class*, not per incident. An entry earns EXECUTABLE status only
when a committed command regenerates the detection; until then it is DESCRIBED. A registry
entry without a probe is an opinion with a filing number.

**Growth is kill-fed:** every future confirmed kill either matches an entry (increment its
kill count) or mints a new one. The registry is the program's immune memory — the concrete
form of "the environment must dominate the dirt" (THESIS v4).

Sources consolidated here: the exit-review kill record, Harmonia D's substrate audit,
`aporia/catalog_attacks/ATTACK_PATTERNS.md` (mirror encoding traps), the fleet's
operational-failure post-mortems, and my ablation card. Pattern-consolidation of the remaining
catalogs (P00–P32 substrate paradigms, kairos/patterns cards) is incremental work — entries
land as they gain a probe, not in bulk.

---

## Entry schema

```
ATK-### <name>
class:      measurement-confound | leak | vacuous-metric | provenance | ops-zombie | self-reference
signature:  how it presents when live
probe:      EXECUTABLE: <committed command>   or   DESCRIBED: <how one would be built>
kills:      incidents where this class was confirmed (pointer, date)
applies-to: claim classes this attack must be run against before the claim is believed
```

## Entries

### ATK-001 arm-identifying serialization
- **class:** measurement-confound
- **signature:** treatment identity recoverable from formatting/structure after semantic
  content is removed (JSON vs text, field order, message count, role structure).
- **probe:** DESCRIBED — render every arm's packets with content stripped; train an arm
  classifier on the residue; target is *unavailability*, not merely low accuracy
  (exit-review #3 invariant, ROUND2_CHARTER A5). Positive control: planted leak must be caught.
- **kills:** exit review #1 — probe pilot's +9.6pp; arm identity visible in serialization
  (found by rendering, not reading).
- **applies-to:** any multi-arm experiment (Tier B, residue-representation, transfer).

### ATK-002 treatment-correlated resource asymmetry
- **class:** measurement-confound
- **signature:** arms differ in token count / context length / truncation probability;
  effect tracks the resource, not the treatment.
- **probe:** DESCRIBED — token-tercile difference-in-differences across arms (exit review #2's
  exact method); alarm if effect concentrates in one tercile.
- **kills:** exit review #2 — token-tercile DiD withdrew the pilot's remaining effect.
- **applies-to:** any arm comparison; any before/after with changed prompt length.

### ATK-003 self-verdicting substrate
- **class:** self-reference
- **signature:** the system generating candidates also emits the verdicts that score them;
  phenotype and fitness function share ancestry.
- **probe:** DESCRIBED — provenance audit: fraction of verdicts whose producer == subject
  (Harmonia D's method; found 99.98%). Threshold: any load-bearing metric with self-verdict
  fraction > 0 is quarantined until a foreign judge consumes the records (R2-3).
- **kills:** Harmonia D substrate audit 2026-08 — 99.98% self-verdicting; mutation +
  self-reporting, not mutation + selection (ROUND2 A7).
- **applies-to:** every historical substrate metric; any future "the organism improved" claim.

### ATK-004 chance-floor masquerade
- **class:** vacuous-metric
- **signature:** a survival/pass metric indistinguishable from its null; selection pressure
  claimed where none exists.
- **probe:** DESCRIBED — recompute the metric under a matched null population; report the gap
  (Harmonia C's method: survivors 45.9% vs 46.1% null).
- **kills:** Harmonia C — survivor set at chance floor; 0/92 kills resurrect.
- **applies-to:** any survival, promotion, or retention statistic.

### ATK-005 answer-key leak
- **class:** leak
- **signature:** ground truth reaches the solver through headers, metadata, retrieval
  side-channels, or verdict tokens embedded in residue.
- **probe:** EXECUTABLE (probe-specific): Ergon's R3 control battery, `ergon/probe/r3_controls.py`
  (controls A–D, OC-calibrated) plus the frozen `_VERDICT_TOKEN` strip regex in
  `ergon/probe/extract.py`. Generalization to other experiments: DESCRIBED — plant a known key,
  confirm the pipeline catches it (positive control first, always).
- **kills:** none live (controls held in the pilot) — the class is registered because it is the
  most common way experiments like ours die elsewhere.
- **applies-to:** Tier B, any retrieval-augmented arm, any residue packet.

### ATK-006 prose-only number
- **class:** provenance
- **signature:** a quantitative claim circulating in journals/ROLE docs with no committed
  computation that regenerates it.
- **probe:** EXECUTABLE (per instance): demand the regenerating command; for the ablation case
  `PYTHONPATH=. python agents/hephaestus/src/knockout_ablation.py`. Standing rule (M3_STATUS §6):
  a forge number that cannot be regenerated by a committed command is E0.
- **kills:** my +11/+32pp claim — number existed only in prose; regenerated honestly by the
  knockout script, then found not independently gradeable (ABLATION_CARD §3).
- **applies-to:** every number quoted in a station file, dossier, or kickoff prompt.

### ATK-007 zombie reporter
- **class:** ops-zombie
- **signature:** a continuous process emitting fresh-looking output while its inputs are stale
  or its pipeline is broken; aliveness mistaken for liveness.
- **probe:** DESCRIBED — state-change test: does the output change when the input changes?
  (M4 rule: liveness = state change, not process aliveness.)
- **kills:** M4 reporter — continuous AND wrong for 7 weeks.
- **applies-to:** any scheduled task, daemon, or "runs continuously" proposal — including the
  watcher scorecard itself (its kill conditions, prereg §7).

### ATK-008 boot-doc fossil
- **class:** provenance
- **signature:** a stale coordination file steering live sessions — citation chains outlive
  the facts (a machine "hardware-dead" 52 days after recovery; a delivered review listed as
  requested, causing three sessions to skip its adjudication).
- **probe:** DESCRIBED — staleness sweep: for each load-bearing station-file claim, find the
  most recent artifact that contradicts it; report contradictions with commit dates.
- **kills:** stations/M1_STATUS.md §8 — four fossils documented, one of which suppressed a
  binding adjudication for three sessions.
- **applies-to:** every stations/*.md consumed at session boot.

### ATK-009 text-typed schema mirage
- **class:** measurement-confound
- **signature:** data ingested with all columns as text; downstream numeric/date comparisons
  silently string-compare; every derived result poisoned at once.
- **probe:** EXECUTABLE (instance): Aporia's mirror audit, `aporia/catalog_attacks/ATTACK_PATTERNS.md`
  (root-caused 8 encoding traps to 320/320 text-typed columns). General: DESCRIBED — type-census
  any mirror before first use; alarm at text-fraction > expected.
- **kills:** lmfdb mirror — 8 traps, one root cause.
- **applies-to:** any imported corpus or mirror.

### ATK-010 template fossil in committed code
- **class:** provenance
- **signature:** committed code that has never been imported/executed — template artifacts
  (`{{}}`), syntax errors, dead config — while docs cite it as operational.
- **probe:** EXECUTABLE — `python -c "import <module>"` per claimed-operational module; an
  import that has never been run in CI or by hand is the tell.
- **kills:** apollo/src/hephaestus_ops.py — broken in every committed version, imported for the
  first time 2026-08 after repair.
- **applies-to:** any "the fleet has a tool for that" claim.

### ATK-011 self-graded distractors
- **class:** self-reference
- **signature:** an evaluator scoring candidates from a distribution it (or its sibling)
  authored; distractor policy determines measured accuracy more than solver quality does.
- **probe:** DESCRIBED — swap the distractor supplier and remeasure; if the number moves
  materially, the distractor policy is the measurement (ABLATION_CARD §3: composed engine
  is a multiple-choice scorer, not gradeable by the free-generation oracle).
- **kills:** the ablation card's central caveat — 39.8% composed accuracy is meaningful only
  relative to its own candidate policy.
- **applies-to:** any accuracy number from a multiple-choice or ranking harness.

### ATK-012 renamed-goalpost drift
- **class:** vacuous-metric
- **signature:** a strong word ("heredity", "gradient", "sovereignty") attached to a result
  that supports only a weaker one; the word then does load-bearing work in later reasoning.
- **probe:** DESCRIBED — for each load-bearing noun in a conclusion, state the measurement
  that licenses it; if none exists, apply the rename rule (ROUND2 A1/A2: Metabolic Cycle 1 ≠
  heredity; "gradient" → failure topology).
- **kills:** external review 2026-08-20 — two renames adopted program-wide.
- **applies-to:** every conclusion paragraph, including this file's.

### ATK-013 writer/reader schema seam (silent absence)
- **class:** measurement-confound (presents as provenance)
- **signature:** a producer and its consumer disagree about a field's shape, so the consumer
  reads zero rows from a non-empty ledger — and the downstream report inverts the meaning:
  *"the substrate recorded nothing"* when the truth is *"the loader could not read it."*
  Absence is indistinguishable from unreadability to every metric computed downstream.
- **probe:** EXECUTABLE — `PYTHONPATH=. python attacks/probes/atk013_prepass_loader_seam.py`
  (exit 1 = defect present). Generalization: for any ledger, assert
  `rows_on_disk > 0 ⟹ rows_accepted > 0`, and have loaders **raise** on a zero-row parse of a
  non-empty file rather than returning `[]`.
- **kills:** `ergon/probe/assemble.py:load_prepass` filters a top-level `rep`;
  `campaign.py` writes `key: [rep, uid]`. Confirmed by execution 2026-08-22: 356 rows on disk,
  356 rep-1 by the writer's schema, **0 accepted**. Found by Techne (HITL #78) from outside
  Ergon's lane, restated across 17 cycles before root cause; realized blast radius **zero**
  (the campaign halted at P1, so P3 never built the arms) — but Tier B is a campaign that
  reaches P3.
- **applies-to:** every producer/consumer pair crossing a file boundary; **mandatory gate
  before any campaign advances past P1.**

---

## Claim × attack coverage matrix

Live claims and which registered attacks have actually been run against them. `—` = not yet
run = the claim is that much softer. The matrix is the to-do list; blanks are work.

| claim | 001 | 002 | 003 | 004 | 005 | 006 | 011 |
|---|---|---|---|---|---|---|---|
| Tier B Δ_carry (pending) | prereg'd (#3 invariant) | prereg'd | n/a (foreign oracle) | R13 floor | controls A–D | prereg committed | n/a |
| pilot +9.6pp (withdrawn) | **KILLED** | **KILLED** | — | — | held | ✓ | — |
| retention decay 8.6× (Apollo) | — | — | ✓ replay | — | — | ✓ | — |
| ablation +11.1/+32.1pp | n/a | n/a | — | — | n/a | ✓ regenerated | **CAVEAT** (§ATK-011) |
| substrate "improvement" (historical) | — | — | **KILLED** (99.98%) | **KILLED** (chance floor) | — | — | — |

## Deployment: banned-methods forcing

When multiple reviewers attack one claim, diversity is enforced by constraint, not persona:
reviewer k receives this registry **minus** the methods reviewers 1..k−1 were assigned, plus
the instruction that reusing a banned method scores zero. Orthogonal collision surfaces
compound; redundant ones saturate (n_eff at ρ=0.5: 5 reviewers ≈ 1.9 effective).

## Import queue (incremental, kill-fed — not bulk)

- [ ] P00–P32 substrate paradigms → entries for the ~6 with executable probes
- [ ] kairos/patterns cards (5) → merge into existing classes where they duplicate
- [ ] external taxonomy sweep (once, free tier): SWE-bench contamination lit., Kaggle leakage
  taxonomies, psych-methods QRP lists → DESCRIBED entries only; each earns EXECUTABLE locally
  or gets dropped in 90 days
