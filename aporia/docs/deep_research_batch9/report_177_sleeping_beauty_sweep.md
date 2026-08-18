# Deep Research Report #177: Sleeping Beauty OEIS Frequency Sweep — Top-10 Most Isolated Sequences as V5 Targets

**Target Agent:** Aporia (with Ergon execution)
**Date:** 2026-04-26
**Front:** Cross-region / V5 strategy (Batch 9 Tier 2)

## 1. Problem Statement

A **Sleeping Beauty** is an OEIS sequence with high internal structure score (compressibility, regularity, recurrence depth) but cross-domain coupling ≤ 0.05 in the current Prometheus tensor — internally rich, externally silent. We have flagged 68,770 such sequences (`project_sleeping_beauties.md`). They are not noise: they are structural regions our existing operator basis fails to read.

The **V5 strategy** (`roles/Aporia/RESPONSIBILITIES.md`) sweeps each Beauty across all 11 phoneme operators — Megethos (magnitude/scale), Flajolet-Odlyzko (singularity class), and the nine proposed Batch-5 phonemes (Rhythma, Taxis, Schema, Topos, …) — to identify which operator, if any, *activates* the sequence: produces a non-trivial structural signature that cross-links it into another tensor region.

Target outcome: for each of the top-10 most-isolated Beauties, identify the activating operator (or report null). This is a direct test of the doctrine `feedback_tensor_first` + `feedback_domains_are_docstrings`: structure is operator-driven, not domain-labelled.

## 2. Literature

- **Flajolet & Odlyzko, *Singularity analysis of generating functions* (1990):** the classification we use as one of two implemented phonemes; output already cached at `ergon/logs/flajolet_odlyzko_results.json`.
- **Belov-Kanel & Konyagin, extremal-sequence bounds:** characterizes how isolated a sequence can be while retaining internal structure — informs our top-10 selection threshold.
- **Erdős & Sárközy, on B_2[g] and Sidon-like sets:** classical examples of high-structure low-coupling sequences; useful priors for what activation should look like.
- **OEIS itself** as a corpus of 370K+ entries; Beauties are the long tail.
- **Megethos paper** (`project_megethos.md`): demonstrates that magnitude with natural basis e accounts for 44% of cross-domain structure and extends past primes — the existence proof that operator-natural framings beat domain labels.

## 3. Computational Handle

68,770 sequences × 11 operators = 756,470 evaluations. Each is O(N) on the first N=100 terms, so ~10^8 scalar ops total — trivial (seconds on CPU, milliseconds on GPU). For the top-10 sweep specifically, cost is 10 × 11 = 110 evaluations.

The actual bottleneck is **operator implementation completeness**. We have two of eleven phonemes built: Megethos and Flajolet-Odlyzko. The remaining nine (Rhythma, Taxis, Schema, Topos, Morphe, Klima, Stasis, Kinesis, Genesis — Batch-5 proposals) are specified but uncoded; their absence bounds the sweep's recall. Ergon can run today's pass; Techne backlog must close the gap.

## 4. Test Design

**Step 1.** Pull the top-10 most-isolated Beauties by ascending cross-region coupling score from the current tensor (`ergon/tensor.npz`); break ties by descending internal-structure score.

**Step 2.** For each Beauty, run Megethos + Flajolet-Odlyzko + any other implemented phoneme on its first N=100 terms. Record the output signature vector for each operator.

**Step 3.** Define **activation**: an operator activates a Beauty if its output signature has cosine similarity ≥ 0.30 to ≥ 1 existing tensor region centroid, with permutation-null p < 0.01 (per `feedback_permutation_null`). Single-region links are reported but flagged as weak.

**Step 4.** Cluster the activated Beauties by activating operator. Report the top-3 most-promising bridges (Beauty → operator → linked region), with effect size and replicate-seed stability (`feedback_replicate_seeds`, ≥5 seeds for the null shuffle).

## 5. Falsification

Quantitative outcomes on the top-10:
- **≥3 activate** under the two existing operators → V5 strategy validated; immediately expand the tensor with these bridges and queue a 1,000-Beauty sweep.
- **1-2 activate** → V5 alive but operator basis under-resourced; file Techne requests for the next three highest-priority phonemes and re-run.
- **0 activate** under any implemented operator → either the top-10 cohort is genuinely beyond reach of {Megethos, Flajolet-Odlyzko}, or the V5 hypothesis is wrong. Distinguish via Step 4 on the next 100 Beauties (random sample) — if base rate is also 0%, V5 needs revision.

Sanity gate: shuffled (Beauty ↔ operator) pairings must show <10% spurious activation; otherwise the activation threshold is too lax.

## 6. Budget

Aporia ~4 hours design (selection criteria, activation threshold calibration, null protocol). Ergon ~2 hours execution (pull top-10, run 110 evaluations, permutation null × 5 seeds, write artifact). Existing tensor data plus Megethos and Flajolet-Odlyzko sufficient for the immediate test — no new infrastructure required. Phoneme expansion via Techne is downstream work, scoped only if Step 5 returns 1-2 activations.

## 7. Expected Outcome

This is the first systematic V5 sweep on the top of the Sleeping Beauty distribution. Deliverables: (a) top-10 Beauty list with isolation scores; (b) per-Beauty activation table across implemented operators; (c) top-3 candidate bridges with effect size, null p-value, and seed stability; (d) a structural-region map measurement of cross-region coupling strength conditioned on operator activation.

The deeper value is doctrinal: a positive result is direct empirical support for `feedback_tensor_first` and `feedback_domains_are_docstrings` — operator-driven partition is the right substrate, and the silence of `project_silent_islands` is a receiver-channel problem, not a content problem. A null result is equally informative: it tells us the existing two phonemes do not span the structural space, and ranks the Batch-5 phoneme backlog by expected yield rather than aesthetic appeal.

**Word count: 778**
