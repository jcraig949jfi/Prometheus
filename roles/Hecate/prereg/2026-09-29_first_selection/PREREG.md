# PREREG -- Hecate first selection (HECATE-03)

Frozen: 2026-09-30Z, in its own commit, BEFORE any pass content (Pass 0
or later) exists for any triplicate. Author: Hecate[m1-dd0c3882].

## What is frozen

The 16 triplicate ids in FROZEN_IDS.txt (full rows in selection.json),
produced by `python -m hecate.select` at seed 20260929 over the corpus
built by `python -m hecate.corpus` whose LF sha256 is
d78f9d669eeecc10071adbba30da44e5c93cf8f63bd7a0c6920f8c2466313885
(hecate/corpus/CORPUS_RECEIPT.json; the jsonl is gitignored because it
is rebuilt byte-identically from tracked sources).

## Rule (as written in hecate/select.py before its first run)

Five strata filled in order, seeded shuffle per stratum, and no concept
may appear in two selected triples (16 x 3 = 48 distinct concepts of 95):

    S1 cross_extreme  3  three fields and three mechanism classes differ
    S2 forged         3  Hephaestus forged it at least once
    S3 nous_high      3  Nous composite >= 7.33 (top decile), never forged
    S4 nous_failure   3  Nous unproductive, or composite <= 5.33 (bottom decile)
    S5 random         4  no filter (the charter's bizarre/random slots)

Eligible counts: S1 2346, S2 385, S3 554, S4 941, S5 6939 (of 6939).

## Honesty notes

- The rule and seed were written before the selector first ran; it ran
  once, and the output was not rerun or edited. The author saw the 16
  names before this commit (unavoidable: the commit contains them).
- Nous's scores are historical LLM ratings, not evidence of anything;
  they are used only as stratification variables, because the charter
  asks for failures and high-potential specimens side by side.
- Not in the 16, and not replacing any of them: the charter's two
  examples. Topology x Gauge Theory x Evolution is historical (Nous
  composite 0.0 per collider/FINDINGS.md) and Epigenetics x Emergence x
  Hoare Logic is not. Both may be run later as labelled operator
  examples (HECATE-22); they are outside every comparison in this
  selection.

## What this selection is for

Pass 0-3 on all 16 (HECATE-04/05), then a preregistered predicate
chooses which go to Pass 4 (HECATE-08). The meta-experiment's units are
drawn from these 16 (see ../2026-09-29_meta_experiment_v1/).
