# Lethe Charter — anti-anchor miner

## Role

One tick = pick the next least-recently-probed conjecture from the curated
catalog of recently-settled-but-LLMs-still-think-open problems, fire N cold
LLM completions (DeepSeek via the shared base helper), score each emission
against the registered true-form, emit an `anti_anchor_candidate` artifact
when the false-form fires above threshold.

Industrializes the Saxl-capture pattern (README §6): one anti-anchor
caught reverted four documents and registered two sub-anchors before a
fabrication entered the v1.0 Learner training corpus.

## Inputs

Native: the curated `CONJECTURE_CATALOG` table inline in `daemon.py`.
Seed v0 covers 10 well-documented recently-settled conjectures where the
LLM modal emission is reliably wrong:

- Schinzel-Zassenhaus (Dimitrov 2019)
- Catalan-Mihailescu (Mihailescu 2002)
- Vinogradov mean value (Wooley + BDG 2016)
- Mertens conjecture (Odlyzko-te Riele 1985 disproved)
- Sato-Tate (Newton-Thorne 2021 sym^k for non-CM EC)
- Ternary Goldbach (Helfgott 2013)
- Saxl conjecture status (open; LLMs sometimes claim solved post-Sellke 2025/26 withdrawn)
- Sensitivity conjecture (Huang 2019)
- Bounded gaps vs twin primes (Zhang 2013 bounded gaps ≠ twin primes)
- Fermat's Last Theorem (Wiles 1994; trivial calibration check)

Catalog growth: Pythia DR reports tagged `AA-VERIFY-*` add new entries
automatically (foreign-key reference to the DR report).

## Outputs (per tick)

- `anti_anchor_candidate_<conjecture-slug>_<utc>.md` under `artifacts/`
  when ≥30% of cold completions produced the registered false-form.
- `null_probe_<conjecture-slug>_<utc>.md` when below threshold — records
  that the conjecture was probed and LLMs got it right this round
  (decayed anti-anchors are themselves data).

## Anti-capture safeguard

Per-conjecture `cumulative_emission_rate` tracked across all historical
probes. If a conjecture's false-form rate drifts to ~0 over rolling
90-day window, mark `DECAYED` and demote from active rotation but keep
historical record. Re-emergence of a DECAYED false-form raises an alarm
(training-data regression signal).

## Cron slot

Floating. Lethe coordinates with Pythia's quota model; one DeepSeek-cost
tick is ~$0.001-$0.01 so this is cheap to run frequently.
