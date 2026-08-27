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
  · `95916588` (2026-08-22) — P1 prepass killed as TRUNCATION-CONFOUNDED: truncated rows scored
  0.000 and parse-fails also scored 0.000, dragging the estimate *into* the band. The defect was
  flattering the gate.
  · **2026-08-23 — the mutation harness itself, one day later.** `cap=20` sampled the first 20
  mutable sites in AST traversal order (top of file), never reaching the verdict functions, and
  printed no truncation warning. Published `canon_r6_falsification` at 100%; full enumeration
  reads **85.2%** (52/9/61). Survival 0/20 inside the sampled window, 9/41 outside, Fisher
  p=0.024. Found by an adversarial red team, not by the instrument's author. **Three kills in
  this class in one fortnight, twice in instruments built by the seat that had just killed the
  previous one — a sampling window is the program's most-repeated defect.**
- **applies-to:** any arm comparison; any before/after with changed prompt length; **any
  instrument that samples a subset of its own measurement space — the sample order must be
  shown to be independent of the quantity measured, or the run reports `sampled/total` and no
  bare score.**

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
- **kills (2):** 2026-08-23, Charon --- `drip_coldband.py` computes its truncation gate from
  `completion_tokens`, a field its own writer never emits, so `truncation_rate` is identically
  `0.0000`: a gate that cannot fail. Proxy rate 4.75% against a 2% gate, at the same 8192 cap
  that confounded P1. Consequence is ATK-014-shaped (vacuous metric); root cause is this seam.
  Detail: `charon/probe/ADDENDUM_2026-08-23_drip_truncation.md`.
- **applies-to:** every producer/consumer pair crossing a file boundary; **mandatory gate
  before any campaign advances past P1.** Generalization extends to METRICS, not only loaders:
  a gate whose input field is absent must RAISE, never return a passing value.

### ATK-015 verdict without rows (aggregate committed, ledger untracked)
- **class:** provenance
- **signature:** the summary artifact of a measurement is committed; the row-level ledger it
  summarises is untracked, and is then destroyed by ordinary git hygiene (`stash -u` + `drop`,
  a clean, a checkout). Nothing raises. The verdict keeps being cited, recomputed from, and
  ruled on — but it is no longer a measurement, it is an assertion with a filename. The tell is
  a timestamp: an aggregate whose `ts_utc` predates the first row of the ledger beneath it.
- **probe:** EXECUTABLE — `PYTHONPATH=. python attacks/probes/atk015_unsourced_verdict.py`
  (exit 1 = an aggregate on disk has no committed rows under it). Generalization: for every
  committed verdict artifact, assert its source ledger is tracked by git AND reproduces the
  artifact's load-bearing fields.
- **kills:** 2026-08-23, found by Charon while auditing the evidence for a rung ruling:
  `campaign/p1_prepass.jsonl` (1,248 rows, underwriting M20 `UNDECIDED-UNDERPOWERED`) and
  `coldband_m30_free/coldband.jsonl` (410 rows, underwriting M30 `LEVELED`) were both destroyed
  by the incident recorded in `e16ca9bc` and both were absent from git. For ~14 hours every
  number in the 2026-08-23 rulings kickoff had no rows beneath it. Both recovered via
  `git fsck --unreachable` and verified to reproduce every committed figure exactly
  (`ergon/probe/ledgers/RECOVERY_NOTE_charon_2026-08-23.md`, commit `cf45ac05`). Aggravating
  factor: `campaign.p1()` returns early whenever the aggregate exists, so the destroyed pre-pass
  would never have been re-collected, and `assemble.load_prepass` returns `[]` silently for an
  absent file — the loss was unobservable from inside the pipeline. Compare ATK-013: absence
  indistinguishable from unreadability; here, absence indistinguishable from evidence.
- **applies-to:** every committed verdict, band read, ledger meta, or scorecard.
  **STANDING RULE (Charon, binding on the probe track): a ledger that underwrites a committed
  verdict is committed in the same commit as that verdict. An aggregate whose rows are not in
  git is `UNSOURCED` and cannot gate a phase.**

### ATK-014 confirmatory estimator (an instrument that cannot disagree with its hypothesis)
- **class:** vacuous-metric / self-reference
- **signature:** a statistic whose computation silently discards exactly the evidence that
  would refute the hypothesis it tests, so it is correct *only when the hypothesis is true*
  and biased toward the hypothesis whenever it is false. Presents as a strong confirmation.
- **probe:** EXECUTABLE — `python attacks/probes/atk014_confirmatory_estimator.py`
  (exit 1 = defect present). It runs the committed scanner unmodified over a synthetic corpus
  with known ground truth. General method (Techne's rule, HITL #129/#133): **before trusting an
  instrument, construct the input on which it MUST report the answer you do not want.**
- **kills:** `ergon/probe/corpus_scan_full.py` — the `cond` loop builds each cell's conditional
  distribution as patterns *exclusive* to that cell, dropping every cross-cell pattern. Measured
  2026-08-22: on a corpus where 66.7% of records carry a crossing pattern, ground truth
  H(kill_pattern | cell) = 0.9183 bits, **estimator reports 0.0000** — i.e. "the cell fully
  determines the failure mode," the maximally strong form of the claim, manufactured by the data
  that refutes it. The committed 3.119 is arithmetically fine *only because* crossing is
  currently 0 — and Ergon's own §3c ruling says that 0 is a tautology of the raw prefixed form
  (`kill_pattern` embeds `generator_id`). The proposed remedy (measure the prefix-stripped form)
  is precisely the condition that detonates this bug.
- **applies-to:** every entropy/diversity/coverage statistic in the program; any instrument whose
  filter mentions the quantity under test.

### ATK-016 provenance stamp blind to the transform
- **class:** provenance
- **signature:** a committed artifact carries a provenance hash that still MATCHES, while the
  numbers it reports no longer reproduce — because the stamp covers the artifact's *inputs* and
  not the *transform* applied to them. Every field checks out and the artifact is stale. The
  mirror of ATK-015: there the rows were destroyed and the verdict survived; here the rows are
  intact and the code between them and the verdict changed underneath it.
- **probe:** EXECUTABLE — `PYTHONPATH=. python techne/attacks/probe_ergon_leakage_gate_2026-08-25.py`
  (exit 1 = a defect is present). Generalization: for every committed measurement artifact,
  stamp a hash of **every module that transforms the inputs into the reported number**, not only
  the input manifest; and re-derive at least one load-bearing figure before citing it.
- **kills:** 2026-08-25, Techne, on `ergon/probe/ledgers/adversarial_leakage/leakage_gate.json`.
  Committed `verdict: PASS`, `manifest_sha16: e6b1e001bf79e3ef`; the current manifest hashes to
  the same value; **not one of the six LIVE observed figures reproduces** (lexical|arm6 committed
  0.1275, recomputes 0.1667; R targets 0.2667/0.3125/0.3133 all recompute to 0.3333).
  INVARIANT 7 re-keyed the packet slug on the task in between, which changed the gate's inputs
  entirely, and no provenance field on the artifact could see it.
- **applies-to:** every committed ledger, band read, scorecard or gate verdict whose inputs pass
  through a renderer, encoder, prompt template or feature extractor — i.e. all of them.

### ATK-017 vacuous gate reported as passing
- **class:** vacuous-metric
- **signature:** a gate's INPUT is constant across the conditions it is meant to discriminate, so
  its statistic is arithmetic rather than measurement — and it reports the passing verdict. The
  tell is a null distribution with **zero variance**: p05 == p90 == p95 == max == mean, and an
  observed value sitting exactly at `1/n_classes`. Distinct from ATK-004 (chance-floor
  masquerade), where the metric merely *sits at* an estimated null; here the constancy of the
  input is **decidable**, and the defect is in the verdict path rather than in the statistic.
- **probe:** EXECUTABLE — `ergon/probe/adversarial_leakage.py::input_vacuity` returns
  `VACUOUS: true` when every group has a single distinct input; `main()` refuses to emit PASS.
  Generalization: before reading any discriminative gate, assert that its inputs actually VARY
  across the conditions, and assert the null has non-zero spread. A gate whose input field is
  absent must raise (ATK-013); a gate whose input field is CONSTANT must report VACUOUS.
- **kills:** 2026-08-25, Techne, on `ergon/probe/adversarial_leakage.py`. After INVARIANT 7
  re-keyed the slug on the task, all **200/200** tasks yield one distinct blanked payload across
  all six arms (138 distinct texts across 1,200 packets). Measured: 12 pairs, **all PASS**, with
  observed 0.1667 and null_p05 == null_p95 == null_max == 0.1667. Aggravating and instructive:
  the author had already NAMED the vacuity in `packet_invariants.check_invariant_7`'s docstring
  — *"a vacuous reading reported as a passing one is its own defect class"* — and nothing
  enforced it. **The prose knew; the code did not.**
- **applies-to:** every classifier gate, leakage probe, discrimination test or A/B screen;
  **mandatory whenever an upstream change is claimed to have "closed a channel by
  construction", because closing the channel is exactly what makes the downstream gate vacuous.**

### ATK-018 one-sided gate on a two-sided question
- **class:** vacuous-metric
- **signature:** a gate asks whether a quantity is RECOVERABLE but tests only the upper tail, so
  a systematic excursion BELOW the null is scored as passing. Recovery below chance is recovery
  — the adversary inverts the prediction — so the decision quantity is `|obs − null|` and a
  one-sided rule cannot fail in the direction where the evidence actually sits.
- **probe:** EXECUTABLE — `PYTHONPATH=. python techne/attacks/probe_ergon_leakage_gate_2026-08-25.py`
  reports `W4_verdict_is_one_sided`. Generalization: for any gate over a symmetric statistic,
  assert that a planted effect of the opposite sign fires it; report the signed AND absolute
  delta beside every verdict.
- **kills:** 2026-08-25, Techne, on `ergon/probe/adversarial_leakage.py::run_gate`
  (`FAIL-LEAK if obs > p95 else UNDECIDED if obs > p90 else PASS`; no lower-tail branch).
  **The live world was below its null on 9 of 12 pairs**, and its lexical|arm6 signature
  (obs 0.1275, null 0.1677, delta −0.0402) is quantitatively indistinguishable from the file's
  OWN planted-leak control `SENSITIVITY_band_plus3` (obs 0.1292, null 0.1647, delta −0.0355) — a
  leak the sensitivity sweep documents the gate as unable to detect. Both were scored PASS. The
  arm-varying slug was real; INVARIANT 7 later removed it by a decidable byte comparison; the
  evidence had been inside the gate's own numbers, concentrated on exactly the R-involving
  targets, and the one-sided verdict discarded it.
- **applies-to:** every permutation-null gate, every equivalence/absence claim, and any check
  whose pass condition is written as a single inequality against a null percentile.

### ATK-019 documented hazard, unguarded code
- **class:** ops-zombie (presents as measurement-confound when it fires)
- **signature:** a docstring or comment states a limit, a hazard, or a vacuity condition
  **correctly and specifically** — and no code enforces it. The author understood the failure
  precisely enough to write it down, and the understanding stayed in prose. The tell is that the
  bug report, when it finally arrives, can be answered by quoting the module's own comment.
  Distinct from ordinary missing validation: here the knowledge is already present and
  *localised*, so the defect is purely the gap between knowing and enforcing.
- **probe:** DESCRIBED — for any module, extract quantitative or conditional claims from
  docstrings and comments ("more than N", "must not", "causes X with 12+", "is now vacuous",
  "only when") and assert that a guard, test, or refusal references the same quantity. Cheap
  approximation available today: grep comments for a numeral-plus-hazard and check whether that
  numeral appears anywhere in executable code in the same file.
- **kills:** three in three days, all found by Techne, two in other seats' code and one in its
  own — which is why this is a class and not an incident.
  · 2026-08-25 — `techne/lib/claim_record.py`: the `Adjudicator` ordering's docstring rates
  `DIFFERENTIAL_TEST` weak *"if implementations share an assumption"*, and nothing anywhere
  checks whether they do. Logged as finding #21.
  · 2026-08-25 — `ergon/probe/packet_invariants.py::check_invariant_7`: its docstring states
  *"the adversarial gate is now VACUOUS on these packets ... a vacuous reading reported as a
  passing one is its own defect class"*. Nothing enforced it; the gate went on emitting 12 PASS
  verdicts against a permutation null with **zero variance**. See ATK-017.
  · 2026-08-27 — `prometheus_math/lehmer_brute_force.py`: the worker-pool comment states that
  each process allocates ~1 GB of PARI stack and that this "caus[es] memory exhaustion with 12+
  workers", while the default resolved to `cpu_count - 1` = **15** on the machine it runs on.
  The HITL #311 re-run died on `Unable to allocate 7.48 MiB`. Fixed by
  `_cap_workers_by_memory`, which reads available memory and reduces the width rather than
  failing.
- **applies-to:** every module carrying a numeric limit, a resource cost, a vacuity condition or
  a "must not" in prose. **Standing rule earned by the third kill: a hazard worth writing down
  is a hazard worth a guard, in the same commit. If it cannot be guarded, the comment must say
  why not — an unenforceable hazard is a finding, not a footnote.**

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
