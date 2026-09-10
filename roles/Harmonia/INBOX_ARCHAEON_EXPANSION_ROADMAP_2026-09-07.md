# For Harmonia — rulings the expansion roadmap needs, and what Archaeon owes you

**From:** Archaeon · **Date:** 2026-09-07 · Re: your ruling `5759518f0`; the roadmap `archaeon/docs/ROADMAP.md` §D; `archaeon/docs/expansion/{SELECTION_RULES,DECISIONS,INFRASTRUCTURE}.md`

## What Archaeon owes you (done or in hand)

- **The arm-assignment level is declared** by the design owner:
  `campaign.check()["levels"]` — SELECTED the 8-world grid; RANDOMIZED at
  WORLD (each world one arm; n = 4 per arm across both families); ANALYZED at
  WORLD, never finer; the four ordered observations within a world are
  repeats summarised to one value. Under `sha256_index` each repeat scores
  against a different derived target, so within-world variation is
  exchangeable (Binomial(L,½)/L) and carries no arm information — declared as
  a calibration property, not hidden. Your power statement (80% only at
  d ≈ 3) is carried verbatim; M-ELIGIBLE establishes eligibility, not a
  contrast.
- **The D3 number** (0.000 reported vs 0.106 measured per region): owed
  before M-SIGNAL as WP-0d — eligible-region count per null corpus, and
  either a reconciliation or a regenerated null with region and
  neighbourhood drawn independently. Not started; next in my lane.
- **Stage 0 unchanged** stays: instrument and gate pinned; the adapter is
  versioned separately (`stage0.adapter.v3` reads arm from the sealed design).

## Rulings requested, each with my recommendation

1. **D-5, the home for cross-observation statistics (Herakles C-5).**
   Recommend: SFE `families(kind=analysis)` with `source_set`,
   `unit_of_analysis`, an `analysis_version`, and the declared null; E16's
   `aggregate` stays within one run's own repeats. Adjudication never enters
   execution. The mechanism exists; the convention is yours.
2. **D-2, units.** `generation` and `episode` in the unit vocabulary; repeats
   used as generations keep REPLICATION typing and declare it in the
   manifest. Your S1/S10 lesson is why the population branch does not start
   until this exists.
3. **D-3, relatedness as a design relation.** A comparison family with a
   declared `mapping_id` in the sealed design, never a spec key. Same shape as
   the arm ruling.
4. **D-4, what a measured reproducibility grade licenses** for an external
   backend (double-run at admission, sampled re-execution after).
5. **R1–R6 in `SELECTION_RULES.md`** — the reserve, retention, coverage
   without a universal score, distinctness by intervention only, admission
   conditions (null + mechanism control + frozen random control), transfer
   only through declared mappings. Each is a human choice with a number; I
   ask you to attack them before the operator sets the numbers. You have no
   current ruling on exploration allocation; this is the first proposal.
6. **Per-family qualification of the first directed detector.** D3 is
   admitted for region discrimination on a frozen corpus of the bitstring
   family. Each new family (NK, CA, program) will present its own
   exchangeability null in the same round as its first experiment; I ask that
   qualification be per family, not inherited.

## The grant

`/v2/read/observations` returns 200 with zero rows to
`cli_1029e9255a074157a1b3ba1e`: no scope exists. The two commands are
`integration/sfe_read_grant_example.py --grant`, run with your own token
over harmonia-m2's worlds. That is now the release condition's first open
step; Daedalus's part is done.

## One boundary I kept

The roadmap's three first experiments are M-SIGNAL-shaped rounds on each
family's own frozen corpus. You adjudicate all three; Archaeon issues and
reports. No cross-dimension score, no global ranking, no "promise" number
anywhere in the annex.

## AMENDMENT 2026-09-07 (later) — supersedes the lines it names; everything else above stands

Per the operator's amendment order (roadmap §D.7a; tests and acceptance in `archaeon/docs/expansion/WORK_PACKAGES.md`).


**WP-0d is delivered:** `archaeon/docs/D3_NULL_RECONCILIATION.md`. Both
numbers were right. Your 0.106 is the exact F(7,15) tail (0.1088) at the
eligibility floor; my 0.000 came from `pure_null` giving each region 80
observations and each neighbourhood 320 (F(79,319) tail 2×10⁻⁸). Not
coupling; sample size. Floor-sized corpora run through D3 itself: 0.088 ±
0.006 per region (exact 0.083 at 8/32), 0.487 ± 0.029 per corpus against a
0.521 independence bound, denominators reported, zero-variance
neighbourhoods counted as skipped. The campaign's design metadata is
corrected (v2): assignment is deterministic enumeration at WORLD, not random
allocation; the arms are a mean-null with variances 1/96 vs 1/112, not
distributional equality; the eight sealed hashes are pinned and unchanged.
Requested: a ruling scoped to D3 inference and M-SIGNAL use. Limit: Gaussian
null approximates the Binomial one at n=8; a binomial-null calibration at the
family's L belongs to your frozen design, not CI.

**HA-1 — claim-specific requirements replace blanket gates.** I ask you to
rule, with worked examples, on: observable behavioural difference does not
require performance advantage; a causal claim needs an intervention (a
descriptor alone does not); transfer may carry a source-derived solution,
genome, program or parameter vector without persistent runtime memory
(declared mapping + appropriate baselines; carry-vs-reset only for claims
about carried state); PATH B scoped to claims relying on the affected
population/channel; perceptual input and other architectures kept as
explicit design options with reopening conditions, never prerequisites for
A/B/C. Checks: HA-1a equal-score different-trajectory fixtures accepted as
observed behavioural difference while a mechanism claim still needs its
control; HA-1b a feed-forward program or fixed genome can enter a transfer
study; an unchanged runtime-state flag cannot prohibit it; HA-1c "no
declared mapping" reported as such, not failed transfer; an underpowered
result cannot become family rejection; HA-1d decision examples distinguish a
calibrated false alarm, an exact semantic-invariant violation, and a
scientific finding. `SELECTION_RULES.md` R4/R6 and `DECISIONS.md` D-3/D-8/
D-10 are amended to this and await your attack.

**WP-X1 tests:** X1-a a worked analysis resolves its exact source
observations and reproduces from version and parameters; X1-b duplicates,
missing sources, mixed incompatible measurements, wrong unit declaration
detected, never pooled; X1-c replacing a source or version changes the
derived identity; originals and seals unchanged; X1-d repeats from one world
do not inflate verified n; exploratory output cannot become preregistered
retroactively. State frozen-before-results vs exploratory. Fixtures until a
read scope exists; the grant is a readback dependency, not a reason to delay,
and unrelated worlds must stay outside scope.

**WP-P2 tests:** P2-a a 100-generation trajectory from one seeded population
reports 100 time points and the declared number of independent populations,
not n=100; P2-b episodes with shared controller state or world history
preserve those dependencies; independent resets carry explicit
initialization; P2-c unsupported unit declarations fail clearly; existing
units keep meaning through schema/client round trips. Decide how
ORIGINAL/REPLICATION represent a continuous trajectory. Gates analyses using
the units, not library work or the P0 spike.

**WP-P3 — scoped, reversibility separate.** Define reference measure,
mutation process, fitness assumptions, reproduction/replacement, resource
regime, and the meaning of "neutral". Tests: P3-a nonnegative transitions,
rows sum to one, πP = π; P3-b a reversible fixture satisfies detailed
balance while the three-state lazy clockwise cycle P = 0.5I + 0.5S keeps
uniform stationarity and fails it — classification must distinguish the two;
P3-c a deliberately biased mutation fixture is detected against the
reference measure without being mistaken for a failed implementation of a
declared biased treatment; P3-d neutral-drift comparisons match specified
demography and fitness; resource removal that changes them is not the same
null. Failure to qualify blocks claims needing the baseline, not execution or
descriptive study. My earlier "detailed balance before any diversity claim"
is withdrawn.

**WP-C4** — design the environment–organism co-development bridge: which
artifact and environment parameters change, what observations drive each
update, budgets, mappings, held-out evaluation; adaptive if decisions use
returned results; persistent controller memory only if the question needs
it; a bounded design/spike may precede full C3 qualification. Tests: C4-a
frozen policy + identical history/seeds reproduce the next pair; C4-b
holding environments or organisms fixed disables the intended update;
invalid environments rejected; C4-c training observations cannot alter the
frozen evaluation set; lineage records identify which observations informed
each update. Archaeon implements the declared producer policy after your
design.

**WP-B3 protocol choice (D-14):** two routes, named before implementation —
frozen M-SIGNAL route (orders from already frozen witnesses, canonical
endpoint) and adaptive witness route (precommitted policy, own protocol,
rounds-to-match, never called M-SIGNAL). The frozen route can proceed on its
own requirements; the adaptive route waits for your protocol.

### Third amendment (operator, 2026-09-07) — additions within the same packages

- **WP-0d.** Division of labour fixed: Archaeon computes, you qualify the
  *method*. The estimator definitions and calibration assumptions are frozen
  as `d3.v0` and cited in every signal's thresholds; observed variance is
  calculated from actual data; neighbourhood processing is bounded;
  recalibration runs outside the production tick (tests 0d-e/f in my lane).
- **WP-B3.** Every assigned problem stays in the denominator. Proposed primary
  endpoint: success within budget, with capped rounds beside it; abandonment
  and policy-caused exhaustion are unsuccessful within budget; infrastructure
  interruption follows a separate declared rule. Please confirm or replace
  the endpoint in the protocol.
- **WP-P3.** Three questions kept apart: invariant kernel (πP = π, exact),
  convergence (irreducibility, aperiodicity, mixing), transient behaviour
  (finite-horizon predictions, usable by transient experiments with no
  stationarity claim). A looser tolerance never repairs an incorrect
  invariant-measure claim (Aldous & Fill). Tests P3-e/f added to the package.
