# PROPOSAL V2-T02 (arm)

## Hypothesis
A record sanitizer implemented as a maintained **denylist** of known-bad record
patterns cannot be certified safe for production admission on the strength of
its pass rate alone. Two independent prior instances of exactly this
mechanism in this codebase — a seam leak gate and a prepass residue loader —
both shipped believing they were leak-free/defect-free and both admitted
unenumerated bad records once adversarially probed. We hypothesize the same
failure recurs here: a denylist-built sanitizer will (a) admit records whose
bad-pattern instance is not literally enumerated (paraphrase/format/near-miss
variants of a known-bad pattern), (b) show admission-rate correlated with
true record quality (a selection-bias artifact, not neutral screening), and
(c) not have been shown to actually fire on any real bad record (vacuous
gate) unless a positive control is built into the validation protocol itself.
Certification therefore requires validating the *gate construction* (denylist
vs. allowlist-by-construction) and the *gate's live behavior* (CAPTURE:
coverage + a positive control that must fire), not just an aggregate
pass/fail count.

## Motivating evidence
Two SAME_MECHANISM-linked findings in the [retrieval system], both about gates
that screen records before they enter a training/eval pipeline:

1. Ergon's seam-fidelity leak gate (`theseus/handoff/ergon_handoff.py`,
   pre-2026-06-22) was a denylist: cut canonical text at a delimiter, reject
   only if a hardcoded token survived. Charon's 50,125-record stratified
   probe (40/265 batches) found it passed verdict words `CONFIRMED` /
   `REFUTED` / `FALSIFIED`, bare `TRUE`/`FALSE`, and the decision statistics
   `r_raw=` / `p=` straight into training prompts — none of these were on
   the enumerated list ([REF], REFUTED; negative evidence
   [REF]). The same probe also found renderability correlated with
   verdict (kill 96.9% vs survivor 84.2%, a 12.7pp gap) — the gate was not
   neutral. The fix (`roles/Ergon/SEAM_ALLOWLIST_REBUILD_2026-06-22.md`)
   replaced the denylist with an allowlist of 18 per-kind structural
   renderers built only from identifier fields, never answer/verdict/stat
   fields; re-running Charon's exact probe found 0/38,028 leaks and cut the
   renderability gap to 1.7pp.
2. Independently, a prepass loader admitted `http_error` rows as legitimate
   prior-attempt residue: at a 24.4% transport error rate, 43/220 tasks in
   one block had no `ok` prepass row yet still rendered packets asserting a
   prior attempt — fabricated residue byte-indistinguishable from the
   legitimate empty-vocabulary case ([REF], OBSERVED). Its stated
   fix principle: "a lookup that finds zero usable rows must refuse, never
   return a renderable value" — i.e., fail-closed, not fail-open.
3. A separate but structurally related finding: an instrumentation *parity*
   gate (proves the instrument didn't change the phenomenon) is
   insufficient alone — a *CAPTURE* gate (coverage + a positive control that
   must fire) is required alongside it, because an instrument can be
   bit-identical to baseline while capturing almost none of what it claims
   to record ([REF], SUPPORTED, Ergon Gen-1A/Gen-2 persistence
   instruments).
4. A later adversarial re-attack of the *fixed* (allowlist) leak gate found
   the gate did detect a planted task-conditional leak (good), but also
   surfaced a pre-committed null on live packets that recovered nothing —
   flagged as "the gate's silence about its own vacuity," not a hidden leak
   ([REF], OBSERVED). This shows even a passing gate needs an
   explicit, reported positive-control result, not silence, to be trusted.

## Prospective predictions
- P1: If the sanitizer's screening logic is a denylist (rejects only if a
  record matches an enumerated bad pattern), a stratified adversarial probe
  of the real corpus will find at least one bad record admitted whose
  defect is a paraphrase/format/near-miss variant of an enumerated pattern
  (escape rate > 0%).
- P2: Admission rate will correlate with true record quality (a
  quality-vs-kind selection artifact), with a measurable pass-rate gap
  between good and bad records, unless the sanitizer is built
  allowlist-first.
- P3: A denylist version will fail a planted-positive-control test at some
  nonzero rate on near-miss variants, even while passing 100% on literal
  copies of already-enumerated patterns.
- P4: Rebuilding the gate as an allowlist-by-construction (only admit
  records matching a positive structural specification of "good") reduces
  escape rate on the same probe, with the same statistical power, to 0/N —
  mirroring the 0/38,028 result Ergon measured after its 2026-06-22 fix.

## Experiment
Four-phase validation, run against the real corpus the sanitizer will
actually screen (not synthetic-only):

- **Phase 0 — construction audit.** Static review of the sanitizer's gate
  logic: is admission governed by "reject if matches known-bad" (denylist)
  or "admit only if matches known-good structure" (allowlist)? Is the
  default on lookup-miss reject or admit (fail-closed vs fail-open)? Record
  this as a first-class result, not an aside.
- **Phase 1 — CAPTURE gate / positive control.** Inject N_planted records
  that are exact instances of currently enumerated bad patterns into a
  shadow admission run. Require 100% rejection before any further phase
  runs. This directly answers [REF]'s "gate's silence about its
  own vacuity" concern — a gate that has never been shown to reject
  anything is not validated by an all-pass count.
- **Phase 2 — stratified real-corpus adversarial probe.** Stratified sample
  across record kind, source, and time window (never alphabetical/prefix
  sampling — feedback_sampling_strategy_is_analysis /
  feedback_prefix_sampling_invalidated_three_passes) sized to match
  Charon's precedent power: ≥40 batches, ≥1,500 records/batch (~50K+
  records, ≥30 kinds). Include analyst-crafted "near-miss" bad records:
  token substitution, field reordering, whitespace/casing variants, and
  truncation-boundary placements of each enumerated bad pattern.
- **Phase 3 — selection-bias / per-kind coverage report.** Report admission
  rate broken out by (a) proxy quality label if available, (b) record
  kind, mirroring Ergon's `renderable_rate_by_verdict` disclosure
  discipline — every kill/admit split must carry its own selection-bias
  check in the same artifact as the headline number.
- **Phase 4 — drift probe.** Freeze the denylist/allowlist as shipped, then
  probe against records from a time window or source that postdates the
  list's last update, to measure staleness decay independent of the
  in-sample result.

## Controls
- **Null-admit control:** a sanitizer stub that admits everything —
  upper bound on escape rate, sanity-checks the probe's own defect
  density.
- **Null-reject control:** a stub that rejects everything — upper bound on
  coverage loss, sanity-checks that Phase 2's sample actually contains
  admissible good records.
- **Before/after control:** if a denylist version exists, run the identical
  frozen probe (same sampled records, same planted near-misses) against
  both the denylist and any allowlist-by-construction candidate, exactly as
  Ergon re-ran Charon's probe post-fix — same instrument, two gate
  constructions, so the comparison isolates gate logic, not sample luck.

## Confound defenses
- Renderability/admission may itself correlate with record kind or quality
  label — defended by Phase 3's mandatory per-kind, per-label breakdown
  reported beside the headline pass rate, not separately or only on
  request.
- Denylist tuning on the same sample used to certify it is circular — the
  planted near-miss set in Phase 1/2 must include patterns not used to
  author or tune the current list (held-out defect variants), otherwise the
  probe measures memorization of its own test set.
- Alphabetical, prefix, or first-N sampling of the corpus is a known
  antipattern that hid 137/141 relations and 5/8 edge-bearing generators in
  a prior pass — Phase 2 sampling must be stratified and the stratification
  scheme stated before the probe runs.
- A gate that has never rejected anything in its history is not evidence
  of safety, only of an untested (possibly fail-open) path — defended by
  making Phase 1's positive control a hard precondition for Phase 2, not
  an optional nice-to-have.

## Preregistered falsifiers (numeric thresholds)
1. **F1 (escape):** any bad record (planted near-miss or real) admitted in
   Phase 2 → escape rate > 0% → certification BLOCKED. (Precedent: prior
   denylist version measured 3/3 known leak-vector families passing on a
   50,125-record probe.)
2. **F2 (CAPTURE):** Phase 1 positive-control rejection rate < 100% (any
   planted known-bad record admitted) → gate is vacuous → certification
   BLOCKED regardless of Phase 2 result.
3. **F3 (selection bias):** admission-rate gap between proxy-good and
   proxy-bad records > 2 percentage points (calibrated against the
   measured 1.7pp post-fix / 12.7pp pre-fix precedent) → bias must be
   disclosed and fixed before certification.
4. **F4 (kind coverage):** ≥5 record kinds render 0% admitted records
   (systematic false-kill of a whole kind, as conservation_law did
   pre-fix) → certification BLOCKED pending a kind-specific fix.
5. **F5 (near-miss generalization):** any near-miss adversarial variant of
   an enumerated bad pattern is admitted at nonzero rate → sanitizer is
   matching literal strings, not the underlying defect signature →
   certification BLOCKED.

## Stopping rule
Run Phases 0–3 to completion at the prereg'd sample size (~40 batches /
~50K records, ≥30 kinds) unless a falsifier trips earlier, in which case
HALT immediately and report the failing rows — do not continue sampling to
average a tripped falsifier back under threshold. Certify only if F1–F5 all
pass at full sample size with escape rate 0/N and CAPTURE-gate 100%. Phase 4
(drift) is a standing recurring check, not a one-time gate: re-run on a
fixed interval (e.g., monthly) or whenever the denylist/allowlist is
updated, since list staleness is a decay process, not a one-time defect.

## Expected failure modes
- Denylist enumerates surface tokens (specific strings) rather than the
  underlying defect signature, so paraphrase/reformat variants escape —
  directly repeats [REF]'s mechanism.
- Fail-open default: a lookup that finds no match "passes" instead of
  refusing — directly repeats [REF]'s mechanism ("a lookup that
  finds zero usable rows must refuse, never return a renderable value").
- Gate reports an all-pass or all-clean headline number that has never
  actually been tested against a real bad record — the [REF]
  vacuity concern; discovered only because an adversarial re-attack ran a
  planted-leak positive control.
- List maintenance becomes reactive: patterns are added only after an
  external party (not this protocol) catches an escape in production,
  producing false confidence between updates (motivates Phase 4's
  recurring cadence rather than a one-time certification).
- Reasonable but wrong assumption that "known-bad patterns" screening is
  inherently a denylist task with no positive spec available — if the
  record schema has no analog to Ergon's per-kind identifier-only
  renderers, allowlist-by-construction (P4) may not be achievable here, and
  the protocol should say so explicitly rather than force a fit.

## Compute estimate
Sanitizer calls over ~50K stratified records plus a few hundred
analyst/LLM-crafted near-miss variants: pattern/schema matching, no model
inference required beyond drafting near-miss variants. Wall-clock:
minutes of CPU for the probe run itself; the dominant cost is analyst/LLM
time to design the stratification and craft held-out near-miss defect
variants (order ~200-500 crafted records). Total: well under 1 CPU-hour of
compute; no GPU required.

## Prior evidence that materially changed this design (or 'none found')
[REF] + [REF] (Ergon/Charon denylist leak-gate failure)
directly set the falsifier thresholds (F1, F3, F5) and the stratified
real-corpus probe scale (40 batches / 1,500/batch). [REF] (prepass
residue admission of http_error rows) set the fail-closed design check in
Phase 0 and the F4 per-kind coverage falsifier. [REF] (CAPTURE
gate doctrine) is the direct source of Phase 1 (positive control as a hard
precondition, not an optional check). [REF] (adversarial re-attack
of the fixed gate) is the direct source of treating "never observed to
reject anything" as a vacuity risk requiring an explicit reported result
rather than a silent pass.

## Unresolved uncertainty
Whether the actual sanitizer's target record schema supports an
allowlist-by-construction redesign (P4) — i.e., a positive structural
specification of "good" analogous to Ergon's identifier-only per-kind
renderers — was not established; no such sanitizer implementation was
located in the repository search performed for this design (search budget
was spent on the wiki precedent and prior repo fix, not on locating the
new sanitizer's code, which may not yet exist). Phase 0 must resolve this
before Phase 1-4 are run: if no positive spec is feasible, the falsifiers
above still apply to the denylist-only case, but P4 and the
before/after control become inapplicable and should be dropped rather than
forced.

