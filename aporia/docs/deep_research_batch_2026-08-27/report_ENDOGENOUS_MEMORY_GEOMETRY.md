# Report — ENDOGENOUS MEMORY GEOMETRY

**Question:** can a machine construct its own indexing/retrieval structure over its own
memories, entirely without human language or human-supplied semantic labels?

**Fired:** 2026-08-28, deep-research harness run `wf_60f55b24-abe` (106 agents, 24 sources
fetched, 120 claims extracted, 25 verified, 12 confirmed, 13 killed, 11 after synthesis).
**Author:** Aporia. **Raw:** workflow task `w8337oxgs`.

---

## HEADLINE

**Index CONSTRUCTION can be genuinely language-free. Index EVALUATION almost never is, and
that is where human ontology re-enters in every case the run examined.**

This is the trap named before the fire went out — if the only way to score an index is a
human-chosen retrieval task, the language excluded from the construction walks back in
through the evaluator. The run confirms it as the dominant empirical pattern, with the
contamination author-acknowledged in at least one peer-reviewed survey.

## THE ONE CLEAN EXISTENCE PROOF

Billion-scale approximate nearest neighbour (Jegou, Tavenard, Douze, Amsaleg, ICASSP 2011;
BIGANN/SIFT1B) is end-to-end label-free on both sides:

- **Construction:** PQ/IVFADC codebooks fit by unsupervised k-means over a 100M-vector
  learning set. No class labels, task labels or semantic supervision.
- **Evaluation:** correctness is agreement with exact Euclidean nearest neighbours computed
  by brute force over 1e9 128-d vectors. No relevance judgements anywhere.

Quality in that regime is dominated by **bit budget**, not semantics: recall@1 rises
0.075 -> 0.258 -> 0.434 -> 0.656 as 0/8/16/32 re-ranking bytes are added; recall@10 reaches
0.970, at near-zero time cost (5.626s -> 5.689s per query). Verification narrowed the gloss:
allocation matters at fixed budget (32B as 16+16 gives recall@1 0.571 vs 32+0 giving 0.487),
and OPQ/LOPQ move recall ~10% at identical bit budgets via rotation. So bits dominate but do
not exhaust the label-free levers.

**What is NOT eliminated:** the L2 metric, the hand-designed SIFT descriptor, the corpus, and
the choice of recall@r. Language is gone; human *choice of geometry* is not.

## THE THREE CONTAMINATION ROUTES, ORDERED BY DEPTH

**1. Evaluation stage — near-universal.** Indexes trained without labels are selected and
scored entirely against a human ontology. SPQ's sole success metric is mAP with relevance
defined by human class-label match. "Unsupervised" covers the objective function only.

**2. Training stage — author-acknowledged.** A peer-reviewed survey (ACM CSUR 2022) states
outright that because deep unsupervised hashing methods cannot acquire label information,
semantic information is instead obtained from ImageNet-pretrained networks — converting the
problem into a supervised one. The canonical learned-index paper's *existence*-index result
likewise abandons the distribution-only framing for a supervised binary classifier over
human-curated "phishing" labels and character-level linguistic structure.

**3. Similarity-relation stage — the subtlest and the one that matters most to us.** What
counts as "the same memory" is not discovered by the system but imported. SPQ's positive
pairs come from five hand-chosen human-designed augmentations (resized crop, horizontal
flip, colour jitter, ...), and the jitter strength was tuned against a label-based metric.
**The equivalence relation is the contamination bottleneck, not the labels.**

**Quantified residual:** SPQ-S, identical except for ImageNet-pretrained initialisation,
beats truly-unsupervised SPQ by 2.1pp mAP on CIFAR-10 (0.814 vs 0.793), 1.2pp on FLICKR25K,
1.4pp elsewhere. Small, consistent, non-zero — under a label-defined metric.

## LABEL-FREE EVALUATION MEASURES DO NOT YET SUBSTITUTE

In a systematic SOM study the internal (label-free) quality measures **disagreed with each
other** and several were systematically over-optimistic — trustworthiness and neighbourhood
preservation never fell below 90%, including on datasets known to admit no valid 2-D
embedding. The same author names label-free evaluation as *future work*, not achieved.

Caveat carried: single MS thesis, n=6 datasets, one map size per dataset, and an
author/advisor conflict of interest on the winning measure.

## ONE POSITIVE ON EMERGENT STRUCTURE

A 16-layer LM's feed-forward key space stratifies by abstraction with no supervision
specifying that stratification: layers 1-9 dominated by shallow patterns (n-grams, shared
last word), layers 10-16 by semantic ones. But the organising principle is *inherited
linguistic structure from a human-language corpus*, and the measurement rests on 160
hand-annotated keys from one model. It is evidence that key spaces self-organise; it is not
evidence that they self-organise language-free.

## COVERAGE — THE LARGEST CAVEAT

**The run answers roughly 1.5 of the 5 requested areas.**

    area                                            surviving claims
    (1) learned/self-organising index structures     well covered
    (4) contamination                                very well covered, strongest result
    (2) neural memory addressing                     nearly empty (all DNC claims killed)
    (3) behavioural/functional embeddings as keys     ZERO
    (5) theory and limits (MDL, Kleinberg)           ZERO

Area (3) is the one closest to this programme — novelty-search behaviour characterisation,
program-trace and execution-fingerprint similarity, bisimulation metrics, successor
representations, place/grid cells as the organism-built-index existence proof. **Nothing
survived.** Area (5) — whether an index can be evaluated at all without a human-specified
downstream task — likewise nothing.

**Treat these as UNSEARCHED, not as negative results.** That distinction is the whole
difference between "no evidence" and "evidence of no".

## INSTRUMENT DEFECT IN THE HARNESS ITSELF — VERIFIED, NOT SUSPECTED

The adversarial verifier killed 13 of 25 claims, and **at least two of those kills are
false**, verified by hand against the primary source:

- KILLED 0-3: "Learned indexes ... outperform cache-optimized B-Trees by up to 70% in speed
  with an order-of-magnitude memory saving." The abstract of arXiv:1712.01208 reads verbatim:
  *"by using neural nets we are able to outperform cache-optimized B-Trees by up to 70% in
  speed while saving an order-of-magnitude in memory"*.
- KILLED 1-2: "any index is a model of the data's own key distribution." The same abstract
  opens: *"Indexes are models: a B-Tree-Index can be seen as a model to map a key to the
  position of a record within a sorted array"*.

The run's own confirmed finding 0 also carries a note that its construction-side detail came
from "a companion claim that failed its own vote on **wording, not substance**" — the
harness diagnosing its own false-kill in passing, without acting on it.

**This is the same defect family as the W5 gate two days ago, in a different instrument.** A
verdict rule is an instrument. This verifier has never been shown to pass a known-TRUE
fixture, so under the program-wide instrument rule adopted 2026-08-27 its refutations are
`INSTRUMENT_UNVALIDATED`, not scientific FAILs. The failures are in the **false-negative
direction**, which is the direction that destroys evidence quietly.

**Scope of my own check:** I verified 2 kills against 1 source. I have NOT shown the other 11
are wrong, and I am not claiming it. The correct reading is that the kill list is unreliable
in an unmeasured proportion, not that it is uniformly wrong.

## WHAT THIS CHANGES

1. **The evaluator is the contamination bottleneck, not the encoder.** Any future claim of a
   language-free index in this programme must state its scoring criterion first and defend
   *that* as language-free. Building a label-free encoder and scoring it with mAP against
   human categories is the standard move and it does not answer the question.

2. **The equivalence relation is the real target.** A machine that had to DISCOVER what
   counts as "the same memory" — from its own action consequences, prediction failures, or
   execution traces — is the actual test. No evidence in the set addresses whether that is
   achievable or how it would be validated. This is precisely where unsearched area (3) and
   this programme's behaviour-only distance work meet.

3. **The decisive untested experiment is a re-coding invariance test on the ontology.** Hold
   the index fixed, swap the evaluation ontology (different label set, permuted or synthetic
   categories, different task), and measure how much of the quality ordering survives. Stable
   ordering means a genuine geometry; collapse means the index was a shadow of the label set.
   D-4 already runs byte-level re-coding invariance on substrates; this is the same instrument
   pointed at the evaluator instead of the encoder.

4. **Do not re-fire this question as asked.** Re-fire areas (3) and (5) as their own targeted
   dispatch, because they went unsearched rather than unanswered.

## OPEN QUESTIONS CARRIED

- Does any label-free evaluation protocol exist stronger than geometric agreement with a
  human-chosen metric? BIGANN removes labels but not the choice of metric, feature space and
  corpus. Nothing tests an index against a criterion the system itself generated —
  self-set goal completion, predictive compression of future observations, or description
  length of the indexed corpus.
- Do self-built index coordinates transfer to criteria they were never scored on?
- Is the invariance set, rather than the labels or the metric, the real bottleneck?
- What organises neural memory key spaces once the DNC claims are excluded? All DNC-specific
  findings were killed; only the transformer FFN result survived, and it suggests
  corpus-inherited linguistic structure.

## SOURCES

24 fetched. Primary anchors: arXiv:1102.3828 (PQ/IVFADC, BIGANN), corpus-texmex.irisa.fr
(SIFT1B ground truth), arXiv:1712.01208 (learned index structures), ACM CSUR 10.1145/3532624
(deep hashing survey), SPQ and PQ-VAE retrieval papers, DigitalCommons URI SOM thesis,
Gershman/Fiete/Irie 2025 (key-value memory review), arXiv:1904.10278 (DNC critique).
