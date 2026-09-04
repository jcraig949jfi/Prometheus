# V1-A Independent Ontology Qualification — Report

Question (charter s3): does canonical mechanism normalization capture
reusable empirical structure, or merely encode Mnemosyne's curation
preferences? Full numbers: `benchmarks/ontology_v1.json`.
Prereg: `PREREGISTRATION_V1.md` sec A (thresholds frozen pre-launch).

## Setup, as frozen

Held-out corpus: 30 adjudicated findings (24 negative), 14 seats, harvested
from 30 source files fully disjoint from the 38 V0 sources; no mechanism
hints included. Mnemosyne annotated BLIND and sealed the hash
(69902d61..., committed before any annotator launched; verified at analysis
time). Six isolated annotators: A1/A2 (ontology given), B1/B2 (ontology +
new-term permission), C1/C2 (no ontology, free-form), plus a normalizer for
C who saw only phrases + vocabulary, never the findings.

## Results against preregistered thresholds

- M-A1 mean pairwise any-overlap (A/B annotators): **0.956** — PASS
  (threshold 0.50; chance ~0.09-0.17). Pairs: A1-A2 1.000, others
  0.933-0.967.
- M-A2 modal top-1 share: 0.883.
- Substrate-class exact agreement 0.767-0.967; failure-class 0.833-0.917.
- M-A3 (vs Mnemosyne blind, non-gating): 0.633-0.700 — the annotators agree
  with EACH OTHER substantially more than with the curator. The definitions
  transmit a stable community reading that is not simply Mnemosyne's private
  reading; the ~30% curator-community divergence is audit-packet material.
- Forced-fit escape valves used sparingly and consistently: NONE rate
  0-3.3%, one NEW mechanism proposal, convergent across annotators (below).

## G3 non-circularity retrieval — the kill test

Gold pairs: 44 cross-agent pairs where BOTH condition-A annotators
independently assigned intersecting mechanisms (no fallback needed;
Mnemosyne played no role). Prediction labels: condition-B annotators
(disjoint agents). Ranking by label overlap vs text baselines over the
held-out corpus:

    labels(B1)  MRR 0.486  hits@10 0.909
    labels(B2)  MRR 0.415  hits@10 0.773
    bm25        MRR 0.143  hits@10 0.364
    embedding   MRR 0.165  hits@10 0.477

Label mean MRR 0.451 >= 2 x 0.165 (best baseline) and hits@10 0.841 >= 0.6:

    G3 = PASS.  CANONICAL_MECHANISM_LAYER_QUALIFIED (at this corpus scale)

The V0 result survives with Mnemosyne's mappings removed from both sides.

## Where the ontology strains (the useful part)

- Disagreement concentrates on exactly the sibling pairs the registry's
  exclusion criteria flag: algebraic_identity_artifact vs
  circular_verification (3), calibration_anchor vs circular_verification
  (3). These boundaries head the human audit packet.
- Convergent gaps, now REGISTERED via governance (G4 demonstrated with real
  need, zero destructive migration):
  - mechanism `cross_domain_bridge` v1 (H-010: all four A/B annotators
    found no fitting term; B2 proposed it) — distinct from
    transfer_mediation (mathematical identification, not learned transfer);
  - substrate terms `problem_catalog`, `paper_cartography`,
    `polynomial_search_space` (B1 and B2 proposed near-identical terms
    independently; A1/A2 used NONE on the same rows).
- Flagged vocabulary debts (not yet acted on): a "null-effect,
  power-limited" failure class distinct from structural_silence (3
  annotators, H-022); H-008's SUPPORTED-with-circularity-caveat sits
  awkwardly (circular_verification on a positive claim).

## Condition C (free-form) convergence

M-A5: see `ontology_v1.json` addendum — free-form phrases, normalized by an
agent who never saw the findings, are compared to A/B labels. Reported as
supporting evidence for G2, not gated.

## Scope ceiling (stated, load-bearing)

All annotators are isolated contexts of the same base model family as the
curator's ecosystem. Convergence this high (0.956) partly reflects shared
model priors, not only definition quality; a human or different-model
annotation pass is the natural V2 strengthening. The G3 retrieval result is
less exposed to this critique (it measures whether labels assigned by one
set of agents retrieve pairs defined by another), but the caveat applies to
the whole campaign and is carried into the final verdict wording.
