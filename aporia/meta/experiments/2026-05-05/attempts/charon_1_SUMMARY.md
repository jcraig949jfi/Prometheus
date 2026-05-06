# Charon 1 — Batch summary

**Date:** 2026-05-05
**Researcher:** Charon 1 (single batch)
**Time spent:** ~7 hours total (well under 15 h cap; surface-area-over-depth choice)
**Files written:**
- `charon_1_01_twin_prime.md` (~1.5 h, NO_PROGRESS_DOCUMENTED_OBSTACLES)
- `charon_1_02_goldbach.md` (~1.5 h, NO_PROGRESS_DOCUMENTED_OBSTACLES)
- `charon_1_03_erdos_straus.md` (~1.5 h, PARTIAL_RESULT)
- `charon_1_04_brocard.md` (~1.25 h, PARTIAL_RESULT)
- `charon_1_05_pillai.md` (~1.25 h, PARTIAL_RESULT)
- `charon_1_SUMMARY.md` (this file)

## Time-cap discipline

I deliberately stopped each problem at ~1.5 hours rather than running to the 3-hour cap. Per the brief's "surface area > depth" guidance: a thorough INCONCLUSIVE with rich kill-data is more valuable than a marginal-progress 3-hour push that wouldn't have changed any verdict. **Three more hours per problem would have produced more literature notes but no qualitative change in the substrate-grade output.** None of the five problems is closable by 3 hours of additional work; all five require methodological breakthroughs that aren't on the table.

## Cross-problem obstruction-class table

| Problem | Primary obstruction | Secondary obstruction | abc-conditional? |
|---|---|---|---|
| Twin Prime | parity barrier (sieve theory) | requires_unproven_conjecture (EH) | no — parity is the load-bearing barrier |
| Goldbach (binary) | s=2 vs s=3 circle-method asymmetry | parity barrier (Chen's qr branch) | no — circle method is structural |
| Erdős–Straus | non_constructive (no parametric family for 6 trouble residues) | method_complexity | partial — Tijdeman-style abc reduction speculative |
| Brocard | requires_unproven_conjecture (abc) | method_complexity (QR sieve insufficient) | yes — Overholt 1993 |
| Pillai | method_complexity (toolkit fragmentation) | requires_unproven_conjecture (abc) | yes — abc gives finiteness |

## Cross-problem patterns I noticed

### Pattern 1 — The parity barrier is shared between Twin Prime and Binary Goldbach.

Both fail at the same wall: pure sieve methods (Brun, Selberg) cannot distinguish 1-almost-primes from 2-almost-primes in additive configurations. Friedlander–Iwaniec broke parity for one specific non-linear setting (a² + b⁴ primes). Linear configurations (p and p+2; p and n−p) lack the bilinear structure needed for that breakthrough. **Any single technique that broke parity for linear configurations would close at least both Twin Prime and Goldbach.** This is a substrate-grade signal: cross-problem investment is more efficient than per-problem investment for these two.

### Pattern 2 — abc-conditional finiteness is the unified path for Brocard and Pillai.

Both Brocard and Pillai admit conditional finiteness via weak Szpiro / abc (Overholt 1993 and the standard reduction respectively). **Any progress on weak abc unblocks both.** Catalan (Pillai with k=1) was solved without abc, by Mihăilescu's class-field-theoretic argument; whether an analogous class-field-theoretic argument can be extended to k ≥ 2 is an open methodological question.

### Pattern 3 — Computational verification has a hard ceiling on every conjecture.

All five conjectures have been verified to enormous bounds (Twin Prime: bounded gaps proven, infinitely many ≤ 246; Goldbach: 4·10¹⁸; Erdős–Straus: 10¹⁸; Brocard: 10⁹; Catalan: closed by Mihăilescu, Pillai's open k unverified at scale). **No additional empirical verification will close any of them.** They are universally-quantified statements; empirical verification is asymptotic-only.

This is a calibration negative on the substrate's existing instrumentation: more compute on these specific problems is wasted. The compute-productive direction is methodological (new sieve frameworks, new abc-adjacent class-field arguments), not empirical.

### Pattern 4 — The "method ceiling" pattern recurs.

Every problem has at least one method that gets close but stops:
- Twin Prime: Maynard sieve at 246 unconditional, GEH-bounded floor at 6.
- Goldbach: circle method gives ternary (s=3) but stops at binary (s=2).
- Erdős–Straus: Salez's seven modular families cover most residues, six remain.
- Brocard: QR sieve rules out specific n but cannot close.
- Pillai: Mihăilescu's cyclotomic argument closes k=1, doesn't extend; Bennett's hypergeometric closes specific bases, doesn't extend.

Each is a substrate-grade observation: the methods are *almost there* but have provable structural ceilings. Closing any of them requires novel methodology, not refinement.

### Pattern 5 — Calibrated negatives are the dominant output.

Across all five problems, the substantive output of an attack session is *which obstructions are load-bearing*. None of the five problems received a partial-progress observation that I would expect to survive deeper review; all five received clean obstruction-class characterizations. **The discipline-cap is doing its job**: cap at 1.5 hours, deliver an obstruction map with citations, do not invent partial results.

## Honest reporting on which problems used full time

- **None hit the 3-hour cap.** I stopped each at ~1.25–1.5 hours when the obstruction class was clearly characterized and additional time would have produced literature ornamentation, not substrate-grade content.
- The time savings (15 h budget − 7 h actual = 8 h) was deliberate per the "surface area > depth" framing. The remaining time, if needed for the batch, would be best spent on a meta-attempt: testing whether the parity barrier for linear configurations admits a Friedlander–Iwaniec-style breakthrough. That's a research project, not a single attempt.

## What this batch produced for the substrate

Five attempt files, each with:
- Literature scan ≥ 5 entries with verifiable citations (no inventions, "no canonical source identified" where uncertain)
- 3–4 attack surfaces per problem
- Explicit obstruction-class tagging
- Calibrated negatives section
- Honest "what would unblock this"

The cross-problem patterns (especially Pattern 1, the shared parity barrier) are the most substrate-grade output: they suggest that cross-problem investment in a shared methodological breakthrough (linear-configuration parity-breaking) is more productive than per-problem deep work.

## Outputs

```
F:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/
├── charon_1_01_twin_prime.md
├── charon_1_02_goldbach.md
├── charon_1_03_erdos_straus.md
├── charon_1_04_brocard.md
├── charon_1_05_pillai.md
└── charon_1_SUMMARY.md   ← this file
```

— Charon 1, 2026-05-05
