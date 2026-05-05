# OEIS Prefix Extension — A152*/A153*/A154*/A155* Surrogate Hunt

**Date:** 2026-04-29
**Author:** Techne (OEIS prefix extension session)
**Mode:** test-first per `.claude/skills/math-tdd/SKILL.md` (16/16 green)

## TL;DR

We extended the calibrated Stream-C surrogate (`delta_pct > 50% AND
regime_change=True`, 100% precision/recall on Charon's 5 A149 anchors)
beyond the A14* family Charon's real battery has visited. The new
prefixes (A152*, A153*, A154*, A155*) yield **zero parseable 3-D
lattice walks** — none of these OEIS slices sample the octant-walk
step-family Charon's anchors live in. The brute-force signature
enumerator's only "high-lift" hits on A152-A155 are tautological
restatements of the kill rule itself (`has_anomaly`/`regime_change`
flags trivially correlate with `delta_pct>50% AND regime_change`).

**Verdict:** No genuinely new high-lift structural signature emerged
in any A152-A155 prefix. The OEIS A-number space outside A14*'s lattice-
walk tradition is sparse in the feature schema OBSTRUCTION_SHAPE
operates on. To extend the hunt to genuinely new territory, either
(a) pull lattice-walk-family prefixes Charon hasn't covered (e.g.
A148/A149 has 700+ sequences, but other 3-D-walk OEIS prefixes exist
elsewhere), or (b) define a richer feature schema that captures
non-lattice structure visible in the integer data itself.

This is the substantive negative result the brief asked for: the
architecture works (pipeline runs, surrogate calibration holds, REINFORCE
still rediscovers OBSTRUCTION_SHAPE on the curated portion), but the
*signature space* it explores doesn't connect to A152-A155's
mathematical content.

## Per-prefix coverage

| Prefix | sequences pulled | parseable 3-D walks | shallow-data skips | surrogate kill rate |
|--------|------------------|---------------------|--------------------|--------------------:|
| A152   | 50 (of 1000 in mirror) | 0 | 1 (insufficient terms) | 3/50 = 6.0% |
| A153   | 50 (of 1000 in mirror) | 0 | 1 (insufficient terms) | 9/50 = 18.0% |
| A154   | 50 (of 1000 in mirror) | 0 | 0 | 26/50 = 52.0% |
| A155   | 50 (of 1000 in mirror) | 0 | 4 (insufficient terms) | 2/50 = 4.0% |
| **Total** | **200** | **0** | **6** | **40/200 = 20.0%** |

The per-prefix kill rates vary widely (4% to 52%) — A154 is dominated
by oscillating-growth families (e.g. binary-grid symmetry counts) where
the `long_rate` swings sharply against `short_rate`, repeatedly
tripping `delta_pct > 50%`. A152 (squarefree with prime-divisor
constraints) and A155 (linear recurrences) have stable
asymptotics and rarely trip the rule.

The synthesized `delta_pct` is computed from the OEIS data via:

  * `short_rate := slope of log|a(n)| vs n on the first half`
  * `long_rate := slope of log|a(n)| vs n on the second half`
  * `delta_pct := 100 * (long_rate - short_rate) / |short_rate|`
  * `regime_change := |delta_pct| > 5%`

Sequences with fewer than 8 positive integer-data terms have
`delta_pct=None` and are conservatively non-killed.

## Per-prefix top-5 signatures

The brute-force enumerator was run at `max_complexity=3` with
`min_match_size=3`. Below, the lift values are large because the
non-match group on each prefix has zero surrogate-kills, so the
floor-1e-6 cap kicks in. **The signatures are tautologically
equivalent to the kill rule itself** — `has_anomaly` is `|delta|>5%`
and `regime_change` is in the kill rule. This is signature-equals-
target leakage, not discovery.

### A152 (top-5)

| lift | n_match | predicate |
|----:|----:|---|
| 69767.44 | 43 | `has_anomaly=True, rate_sign='pos'` |
| 69767.44 | 43 | `has_anomaly=True, rate_sign='pos', regime_change=True` |
| 69767.44 | 43 | `rate_sign='pos', regime_change=True` |
| 66666.67 | 45 | `has_anomaly=True` |
| 66666.67 | 45 | `has_anomaly=True, regime_change=True` |

### A153 (top-5)

| lift | n_match | predicate |
|----:|----:|---|
| 191489.36 | 47 | `has_anomaly=True` |
| 191489.36 | 47 | `has_anomaly=True, regime_change=True` |
| 191489.36 | 47 | `regime_change=True` |
| 7.83 | 3 | `has_anomaly=True, n_terms_bucket='medium'` |
| 7.83 | 3 | `has_anomaly=True, n_terms_bucket='medium', rate_sign='pos'` |

### A154 (top-5)

| lift | n_match | predicate |
|----:|----:|---|
| 650000.00 | 40 | `has_anomaly=True` |
| 650000.00 | 40 | `has_anomaly=True, regime_change=True` |
| 650000.00 | 40 | `regime_change=True` |
| 3.88 | 26 | `has_anomaly=True, rate_sign='pos'` |
| 3.88 | 26 | `has_anomaly=True, rate_sign='pos', regime_change=True` |

### A155 (top-5)

| lift | n_match | predicate |
|----:|----:|---|
| 48780.49 | 41 | `has_anomaly=True, rate_sign='pos'` |
| 48780.49 | 41 | `has_anomaly=True, rate_sign='pos', regime_change=True` |
| 48780.49 | 41 | `rate_sign='pos', regime_change=True` |
| 46511.63 | 43 | `has_anomaly=True` |
| 46511.63 | 43 | `has_anomaly=True, regime_change=True` |

### Aggregate (all four prefixes, top-5)

| lift | n_match | predicate |
|----:|----:|---|
| 228571.43 | 175 | `has_anomaly=True` |
| 228571.43 | 175 | `has_anomaly=True, regime_change=True` |
| 228571.43 | 175 | `regime_change=True` |
| 3.06 | 7 | `has_anomaly=True, n_terms_bucket='short'` |
| 3.06 | 7 | `has_anomaly=True, n_terms_bucket='short', rate_sign='pos'` |

The non-tautological lifts on A153/A154/aggregate (3-7x) are noise:
match-group sizes 3, 7, 26 with kill counts proportional to base rate.
None constitutes a high-lift discovery.

## REINFORCE on the union corpus

We ran REINFORCE for 1000 episodes × 3 seeds on the union of:

  * **A148+A149** curated surrogate corpus (701 lattice-walk entries
    with the calibrated rule applied to Charon's existing
    `asymptotic_deviations.jsonl` records — 5 surrogate kills exactly
    matching Charon's anchors).
  * **A152-A155** lattice-walk slice from this hunt: 0 entries, since
    none of those prefixes contain 3-D step-set names.

Effectively, REINFORCE ran on the curated A148+A149 corpus (no new
contributions from A152-A155 to its lattice-walk schema).

| seed | rediscoveries | discoveries | mean reward | obstr first-ep |
|-----:|--------------:|------------:|-----------:|---------------:|
|  101 | 0             | 978         | 48.90      | (not reached)  |
|  102 | 897           | 915         | 90.60      | early          |
|  103 | 0             | 701         | 35.05      | (not reached)  |

Seed 102 found OBSTRUCTION_SHAPE early and then reinforced on it for
~900 episodes. Seeds 101 and 103 plateaued on shallower predicates
(consistent with the previously-reported `OBSTRUCTION_EXTENDED_RESULTS.md`
finding of 2/3 seed rediscovery rate).

**No new high-lift signatures emerged in the discoveries from any
seed.** The "discoveries" counts in the table are just the per-episode
predicate-tag counts the env emits; on inspection they're all
OBSTRUCTION_SHAPE refinements or near-misses, no novel patterns.

## Honest framing

**The surrogate is calibrated, but the surrogate is still a surrogate.**
The Stream-C calibration (100% precision/recall on A149's 5 anchors
vs the real F1+F6+F9+F11 battery) is the strongest evidence we have
that the rule transfers — but it is calibrated on 5 sequences in a
single OEIS prefix. Any "discovery" produced by this pipeline on
prefixes outside the calibration distribution is a CANDIDATE awaiting
Charon's real battery before substrate promotion. The surrogate is a
PRE-FILTER, not a substitute.

**A152-A155 don't sample the relevant feature space.** None of those
prefixes contain 3-D N^3-octant lattice walks. The lattice-walk
feature schema (`n_steps`, `neg_x`, `pos_x`, `has_diag_neg`, etc.)
is therefore inapplicable. We backstopped with a general schema
(`n_terms_bucket`, `has_anomaly`, `regime_change`, `rate_sign`) for
the brute-force enumerator, but those features are too coarse to
distinguish kill from non-kill except through the kill rule itself —
hence the tautological top-5 signatures.

**This is a substrate-grade negative result.** The pipeline holds
(tests green, surrogate matches ground truth on the calibration set,
REINFORCE rediscovers on curated data). No false discovery slipped
through. The fact that A152-A155 yielded no new high-lift structural
signature is honest evidence about the architecture's domain ceiling
at this surrogate level.

## What the test suite covers

`prometheus_math/tests/test_oeis_prefix_extension.py` — 16 tests, all
green. Per the math-tdd rubric:

* **Authority (3):**
  * A149074's surrogate kill_verdict matches Charon's ground truth
    (delta_pct=78.89%, regime_change=True → kill via curated record).
  * The brute-force enumerator on A148+A149 finds at least one
    high-lift (>=50x) signature whose match-group is exactly the
    5 Charon anchors. It actually finds many: e.g.
    `{has_diag_neg=True, neg_x=4}` at lift=1M (n_match=5).
  * A non-lattice sequence (e.g. A152000) is skipped cleanly:
    `parseable_step_set=False`, no contribution to `entries_lattice`.
* **Property (4):**
  * Every reported lift is finite and >= 0.
  * The brute-force enumerator returns >= 1 signature on any
    non-trivial corpus (>=1 record, >=1 feature).
  * Same input → same output (deterministic).
  * `synthesize_deviation_record` handles short data gracefully
    (returns delta_pct=None, kill=False).
* **Edge (4):**
  * Empty corpus → empty signature list.
  * `max_complexity=0` → exactly one entry: the empty predicate.
  * OEIS API + local mirror both unreachable → empty list, no crash.
  * `max_complexity > 3` → `NotImplementedError` (combinatorial blowup
    refusal — defer to REINFORCE).
* **Composition (5):**
  * End-to-end pipeline (pull A152 → surrogate → enumerate →
    summary) doesn't crash, produces structured output.
  * Cross-prefix lift on the broader A148+A149+A150+A151 corpus is
    finite and non-negative; match-group of OBSTRUCTION_SHAPE is
    invariant under denominator extension.
  * Each `SurrogateRecord` carries full provenance (a_number, prefix,
    deviation_record, parseable_step_set flag).
  * `signatures_per_prefix` returns at most `top_k` per prefix.
  * REINFORCE runs without crash on the union corpus and produces a
    well-formed result dict.

## Files

* `prometheus_math/_oeis_prefix_extension.py` — main module.
  Public surface: `pull_oeis_prefix`, `compute_surrogate_kill`,
  `synthesize_deviation_record`, `get_deviation_record`,
  `extend_corpus_with_surrogate`, `enumerate_signatures`,
  `signatures_per_prefix`, `extended_pipeline_summary`,
  `OeisRawEntry`, `SurrogateRecord`, `ExtendedCorpus`.
* `prometheus_math/tests/test_oeis_prefix_extension.py` — 16 tests.
* `prometheus_math/_run_oeis_prefix_extension.py` — CLI runner that
  reproduces the results in this file.
* `prometheus_math/_oeis_prefix_extension_run.json` — machine-readable
  copy of the latest run.

## Future work

The pipeline is ready to consume better corpora. To find a genuinely
new high-lift signature, push it at:

1. **Other 3-D lattice-walk OEIS prefixes.** OEIS contains many
   octant/quadrant/octant^d walk families outside A14*. The local
   mirror has 395K sequences; a step-set-name regex scan of all
   prefixes would identify which ones the lattice-walk schema applies
   to. Charon's real battery could then be run on the surrogate-killed
   subset.
2. **Richer feature schemas for non-lattice sequences.** The current
   general-schema features (`n_terms_bucket`, `has_anomaly`,
   `regime_change`, `rate_sign`) are too coarse. Additional candidates:
   p-adic valuations of leading terms, modular residues, Newton
   polygon slopes, generating-function shape (recurrence depth,
   D-finite vs hypergeometric).
3. **Charon's real battery on the match-groups.** Any signature this
   pipeline reports as high-lift on a non-curated prefix is a
   candidate. Run F1+F6+F9+F11 on its match-group sequences. If the
   real battery agrees, promote.
