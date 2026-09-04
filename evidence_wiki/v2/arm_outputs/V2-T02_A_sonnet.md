# PROPOSAL V2-T02 (arm A)

## Hypothesis
A record sanitizer built as a **denylist of known-bad patterns** (reject only records that match an enumerated bad pattern; admit everything else) cannot be certified safe by its own self-reported flag/pass metric. A denylist passes anything it does not enumerate, so its true escape rate (bad records that slip through into the training corpus) is systematically underestimated by in-sample statistics computed on the same population the list was curated from. Certification requires an **adversarial, out-of-list probe** — structural variants of the known-bad patterns, plus a stratified real-candidate-stream sample — run by a party independent of the list's authorship, before the sanitizer is trusted with production admission.

## Motivating evidence
This is not a hypothetical failure mode — it already happened once at a structurally identical seam in this codebase, and the fix pattern is the template for this design:

- `roles/Ergon/SEAM_ALLOWLIST_REBUILD_2026-06-22.md` and `charon/SEAM_FIDELITY_ADVERSARIAL_VERDICT_2026-06-17.md`: Ergon's prompt-leak gate (`_leak_safe_claim`) was a denylist — reject only if a hardcoded token survived. Charon ran a stratified real-corpus probe (40 batches of a 265-batch corpus, 1,500 records/batch, 50,125 sampled) plus crafted+real unit demonstrations, and found the denylist **passed** (i.e. failed to catch) verdict words `CONFIRMED`/`REFUTED`/`FALSIFIED`, bare `TRUE`/`FALSE`, and the decision statistics `r_raw=`/`p=` — exactly the answer-bearing content the gate existed to remove. The gate's own claim ("leak audit: 0") was false; the true escape rate was found only by adversarial probing, not by trusting the gate's aggregate.
- The fix replaced the denylist with an **allowlist** of per-kind structural renderers (build only from identifier fields, skip anything without a registered renderer) and re-verified on the same real corpus: 0/38,028 leaks, this time by construction rather than enumeration. The rebuild doc explicitly frames this as "denylist → allowlist (leak-free by construction)" and states the general lesson: *"An allowlist trades coverage for safety... this is the correct trade at this seam (a leaked answer poisons the eval; a dropped small kind costs coverage)."*
- Charon's probe also surfaced two confound classes beyond raw escape rate that a naive certification would miss: (a) **whole-pattern-class holes** — kinds/classes with 100% escape or 100% skip, invisible in an aggregate rate; (b) **selection bias** — the gate's pass-through rate was correlated with a legitimate record covariate (verdict: kill 96.9% renderable vs survivor 84.2% renderable), meaning the gate's action was silently reshaping corpus composition, not just filtering bad records.
- `roles/Daedalus/RESPONSIBILITIES.md` independently reflects the same standing preference repo-wide: the Serendipity Foundry Engine's release-identity boundary is built as an **allowlist** (`foundry/tests/third_party/scripts`), not a denylist, for the same reason — enumerated-bad is a weaker boundary than enumerated-good.

## Prospective predictions
- P1: On an adversarial variant set (structural perturbations of each denylisted pattern — reordering, case-fold, whitespace/homoglyph insertion, synonym substitution, field-split/recombination), the sanitizer's escape rate (bad variants admitted) will be **non-trivially greater than zero**, i.e. its 95% CI lower bound will exceed 0.
- P2: Escape rate will not be uniform across pattern classes — at least one class will show near-total escape (≥50%) while the aggregate escape rate looks acceptable, mirroring Charon's "100% leak-skip" whole-kind holes.
- P3: The sanitizer's admission decision will show measurable correlation with a legitimate record covariate unrelated to badness (e.g. record source, generator, or record age/batch) — i.e. it is not covariate-neutral, and will reshape corpus composition as a side effect of filtering.
- P4: The sanitizer's own self-reported pass/flag statistics, computed on the population the denylist was tuned against, will disagree materially (>2x) with the adversarial-probe escape rate — replicating the "leak audit: 0" vs. true-nonzero gap already observed at the Ergon seam.

## Experiment
Certification protocol, run once before production sign-off and on a fixed recurring cadence after (denylist drift):

1. **Stratified real-stream sample.** Draw a stratified sample of actual candidate records from the live admission stream (not synthetic-only), stratified across source/generator/batch, sized to mirror Charon's precedent (order ~40 strata × ~1,500 records; scale to the actual candidate volume). Enforce `feedback_prefix_sampling_invalidated_three_passes`: never sample only the earliest-arriving batches.
2. **Adversarial variant construction (independent authorship).** For every pattern currently in the denylist, a party who did NOT author or curate that list constructs k≥30 structural variants per pattern (reorder, case-fold, whitespace/unicode perturbation, synonym substitution, cross-field composition of two individually-clean fields into a jointly-bad record). This mirrors Charon's crafted+real unit demonstration of the exact leak vectors the denylist missed.
3. **Held-out freeze.** The variant set is frozen and not shown to the denylist maintainers before the probe runs (breaks the "control drawn from the treatment's selection relation" failure — `feedback_control_must_break_the_selection_relation`).
4. **Run the sanitizer** over (stratified real sample) ∪ (adversarial variants) ∪ (clean negative-control records, see Controls) and log every per-record decision (admit/reject, matched pattern id if any) to a ledger — never aggregate-only (`feedback_verdict_without_rows_is_an_assertion`).
5. **Compute:** escape rate (bad admitted / bad tested) with Wilson/Clopper-Pearson CI overall and per pattern-class; false-positive rate on the clean control; admission-rate-by-covariate table (the `renderable_rate_by_verdict`-style disclosure Ergon adopted).

## Controls
- **Clean negative control**: a stratified sample of records already known-good (e.g. previously admitted, human-reviewed, or synthetically constructed to be unambiguously clean) — measures false-positive rate, the mirror statistic to escape rate.
- **Random-perturbation null**: apply the *same* perturbation operators (reorder/case-fold/whitespace/synonym) to clean records with no attempt to land on a bad pattern. Establishes the baseline nuisance-flag rate so a raised flag rate on adversarial variants can be attributed to the variants actually encoding the bad pattern, not to generic sensitivity to perturbation.
- **Independent-authorship control**: adversarial variants and the stratified sample are constructed/drawn by a role other than whoever maintains the denylist, per `feedback_promotion_requires_independent_failure_mode` — a same-author re-run of the sanitizer's own metric is not evidence.
- **Structural-renderer comparison arm (optional but recommended)**: run the same probe corpus through an allowlist-style rebuild of the sanitizer (admit only records matching known-good structural templates; reject/skip anything else) as a comparison arm, replicating the Ergon fix, to quantify the coverage-vs-safety trade this design explicitly predicts.

## Confound defenses
- **Wrong population** (`feedback_wrong_population_statistics`): the adversarial/held-out probe corpus must be drawn from a population disjoint from whatever data the denylist was curated against, or the escape-rate estimate measures the list's fit to its own training population, not production safety.
- **Prefix sampling** (`feedback_prefix_sampling_invalidated_three_passes`): stratify across the full candidate stream; do not read only the first N arriving files/batches.
- **Gate vs. measurement-error threshold** (`feedback_gate_must_exceed_measurement_error`): compute the SE of the escape-rate estimator BEFORE setting the pass/fail line; a certification threshold within 1 SE of the observed value is not a gate.
- **Selection-artifact disclosure** (Charon's Finding 3 precedent): report admission-rate-by-covariate alongside the headline escape rate in every certification writeup; a "sanitizer removes X% of bad records" claim without this table is not certifiable per the extract-list rule this repo already applies to distribution claims.
- **Same-model/self-audit**: the sanitizer (or its maintainer) may not serve as its own adjudicator of the adversarial set's difficulty or realism.

## Preregistered falsifiers (numeric thresholds)
(Thresholds anchored to the Ergon/Charon precedent as calibration priors — this system has not yet been measured, so these are pre-registered decision lines, not historical values of this sanitizer.)
- **F1 — aggregate escape rate.** Certification FAILS if the 95% CI lower bound of the adversarial-variant escape rate is > 0% (i.e. cannot exclude nonzero escape) OR the point estimate exceeds 2%.
- **F2 — whole-class hole.** Certification FAILS if any single pattern class shows escape rate ≥ 50% on its ≥30-variant probe set, regardless of the aggregate (this is the "100% leak-skip kind" failure mode from Charon's Finding 2).
- **F3 — false positive rate.** Certification FAILS if false-positive rate on the clean negative control exceeds 5%, or if it exceeds the pre-sanitizer baseline reject rate by more than 2×.
- **F4 — selection bias.** Certification FAILS if admission rate differs by more than 5 percentage points across any legitimate covariate stratum (source/generator/age) without a documented, deliberate reason (mirroring the disclosed-not-hidden standard Ergon set for `renderable_rate_by_verdict`).
- **PASS bar**: all four falsifiers clear AND the sanitizer's self-reported pass statistic on the same probe corpus agrees with the independently-computed escape rate within its CI (closes the "leak audit: 0 but actually nonzero" gap).

## Stopping rule
Run the full probe once at the pre-registered sample size (stratified real sample + ≥30 variants/class + clean control). If F1–F4 all clear, certify with the ledger attached. If any single falsifier fails, STOP — do not iteratively patch the denylist and re-run the same probe set (that re-introduces the "control drawn from the treatment's selection relation" failure); instead route the failing pattern class back to maintainers for either (a) a fix analogous to Ergon's conservation_law repair, or (b) explicit retirement/documentation as an uncovered class, then re-run on a **freshly constructed** adversarial set before re-certifying. No more than 2 re-certification cycles on the same denylist version before escalating to the allowlist-rebuild comparison arm.

## Expected failure modes
- Token/keyword-level escape: the denylist matches literal strings but misses reordered, cased, or whitespace/homoglyph-perturbed variants of the same pattern (directly observed at the Ergon seam).
- Compositional escape: two individually-clean fields combine into a bad record; a per-field denylist check never sees the joint pattern.
- Whole-pattern-class holes: at least one bad-pattern class is structurally invisible to the sanitizer (renderer/matcher bug, not a coverage gap the maintainers are aware of).
- Selection-artifact drift: the sanitizer disproportionately rejects or admits a legitimate subgroup, silently reshaping corpus composition (verdict-correlated in the Ergon precedent; could be source- or generator-correlated here).
- List staleness: a denylist certified today degrades as new bad-pattern variants appear post-freeze; no probe run once is evidence of ongoing safety without a recurring cadence.

## Compute estimate
Cheap, no GPU/training involved: CPU-only pattern matching over a stratified sample on the order of Charon's precedent (~50K records), plus a few thousand constructed adversarial variants (≥30 per denylist entry). Estimated ~1 engineer-day to construct the independent adversarial set and stratified sample, plus a single-machine batch run (minutes to low hours depending on candidate-stream size). No distinct infrastructure beyond the existing record/ledger tooling used for the Ergon seam probe.

## Prior evidence that materially changed this design
Yes — two documents changed the design from a generic "test the filter" plan into the specific adversarial-probe protocol above:
- `roles/Ergon/SEAM_ALLOWLIST_REBUILD_2026-06-22.md` — supplied the denylist→allowlist fix pattern and the "coverage vs. safety" trade-off framing used in the Controls section.
- `charon/SEAM_FIDELITY_ADVERSARIAL_VERDICT_2026-06-17.md` — supplied the actual probe methodology (stratified real-corpus sampling size/shape, crafted+real unit demonstration of specific escape vectors, and the two confound classes — whole-kind holes and verdict-correlated selection bias — that this design's F2 and F4 falsifiers directly encode).
- `roles/Daedalus/RESPONSIBILITIES.md` — corroborates that allowlist-over-denylist is a standing repo-wide preference (D-13 release-identity boundary), not a one-off Ergon fix, supporting the recommended allowlist comparison arm.

## Unresolved uncertainty
- The actual denylist's pattern classes, size, and maintenance process were not located in this search (out of scope: evidence_wiki excluded; general repo search budget exhausted before finding a sanitizer-specific spec). The numeric thresholds above are calibration priors borrowed from the Ergon/Charon precedent, not measurements of this system — they should be revisited once the real pattern inventory is available.
- It is unresolved whether "record" here means the same claim/prompt-record shape as the Ergon seam (structured fields with a canonical text span) or a different record type (e.g. raw log lines, config blobs); the field-composition escape mode (P1/F1) assumes structured multi-field records and may need reshaping for unstructured text.
- No information was found on whether an independent-authorship reviewer role already exists for this sanitizer (analogous to Charon's role at the Ergon seam) or would need to be newly assigned.

## Operation log (numbered; ops used / 15, documents opened / 12)
1. Grep `sanitiz|denylist|allowlist` over F:\Prometheus — timed out (too broad), no results returned.
2. Grep `known-bad|known_bad|record pattern|admission gate|corpus admission` over F:\Prometheus — timed out (too broad), no results returned.
3. Grep `denylist|allowlist` scoped to F:\Prometheus\aporia — 5 files found.
4. Grep `denylist|allowlist|sanitiz` scoped to F:\Prometheus\roles — 15 files found, including `roles/Ergon/SEAM_ALLOWLIST_REBUILD_2026-06-22.md`.
5. Read `roles/Ergon/SEAM_ALLOWLIST_REBUILD_2026-06-22.md` (document 1) — primary motivating evidence.
6. Grep `poison|adversarial record|corrupt.*ledger|contamina` scoped to F:\Prometheus\roles\Ergon — 5 files found (no new document opened from this).
7. Read `charon/SEAM_FIDELITY_ADVERSARIAL_VERDICT_2026-06-17.md` (document 2) — probe methodology and confound classes.
8. Grep `ATK-015|verdict without rows|raw ledgers destroyed` scoped to F:\Prometheus\aporia — no files found.
9. Glob `aporia/doctrine/critical_memories.md` — no files found.
10. Grep `poison|gold.*contaminat|training gold` scoped to F:\Prometheus\aporia\doctrine — 2 files found (not opened; judged marginal to design, budget conserved).
11. Grep `provenance|admission` in `roles/Ergon/resume_ergon.md` — no matches.
12. Grep `denylist|allowlist|sanitiz` in `roles/Daedalus/RESPONSIBILITIES.md` with content mode (document 3) — corroborating D-13 allowlist precedent.

Ops used: 12/15. Documents opened: 3/12. Unused budget: 3 ops, 9 documents — not spent; stopped once the design had a load-bearing precedent, its probe methodology, and one corroborating cross-check.
