# PKG-S1: Sufficiency-class ladder with exact oracles (research-ready package, design v0.1)

Owner: Ensorain (ARC3), thread T17 (with T19, T21, T18 as variants). It needs NO WTP code and NO M2: pure
numpy/scipy sequence worlds, runnable on any node. Readable cold.

## 1. Question

Given worlds where the minimal sufficient statistic for prediction is KNOWN EXACTLY, does each memory strategy retain
what is provably sufficient and nothing more? Where does its loss come from:
- missing sufficient information (storage);
- a readout that cannot use what is stored (readout / V-information);
- estimation error (hypothesis)?

## 2. Why

LM01's WTP worlds have no Bayes reference, so "who wins" cannot be converted into "how far from optimal, and why". This
ladder gives every learner two answer-keyed numbers:
- excess loss = loss - Bayes loss;
- excess retention = retained bits - minimal sufficient bits.
Both are reported against a constant/marginal twin. (Grounding: lit/LIT_THEORY.md section 8c, D1/D2/D8/D10.)

## 3. Worlds (each has an exact Bayes predictor and a known sufficient statistic)

| id | world | sufficient statistic | exact history needed? |
|----|-------|----------------------|-----------------------|
| W0 | iid Bernoulli(p) known | nothing | no |
| W1 | Bernoulli/categorical, unknown p ~ Dirichlet | counts | no (ordering is nuisance) |
| W2 | order-k Markov (k = 2, 3) | last k symbols | no (finite window) |
| W3 | Even process / golden mean | a finite causal state, NO finite window | no |
| W4 | nonunifilar HMM (simple nonunifilar source) | the belief state (mixed state) | no, but the statistic is continuous |
| W5 | key-value long tail (queries ask for arbitrary earlier items; Zipf keys) | the growing set of seen (key, value) | YES |

Bayes predictors:
- W0/W1: closed form (Dirichlet-multinomial);
- W2/W3: the epsilon-machine by construction;
- W4: the forward algorithm (belief state);
- W5: a lookup (the value if the key was seen, else the prior).
Exact quantities: C_mu = H(stationary causal-state distribution); E by block-entropy convergence; I_pred(T).

## 4. Learners (the three compression loci, lit D8) at matched declared budgets

- L-STAT: stores a fixed-size statistic online (counts / last-k window / a learned finite-state tracker).
  Compression at STORAGE.
- L-VERB+SUM: stores the verbatim history (a bounded reservoir B or the full store) and computes a summary at query time
  (counts / window / a fitted order-k model).
  Compression at RETRIEVAL/READOUT.
- L-VERB+RESTRICT: verbatim history with a RESTRICTED readout family (e.g. only the last-k window readable, or a linear
  readout over n-gram features).
  Exposes V-information limits.
- L-NEAREST: k-NN over history suffixes (the LM01 L-K analogue).
- Budget ladder per learner: memory bits in {2, 4, 8, ..., 2^14}; query compute counted.

## 5. Discriminators (each a pre-declared prediction from theory; the answer key)

- P1 (W1-W3): L-STAT = L-VERB+SUM = Bayes at the sufficient rate. L-VERB+RESTRICT with a window shorter than the causal
  memory fails on W3 (the Even process is infinite-order Markov).
- P2 (W5): L-STAT loses, increasingly with the query tail. The verbatim learners lose only if retrieval is bounded.
- P3 (truncation curve, W2/W3; Crutchfield and Feldman 2003): h(L) - h_mu vs the window/state budget L. The shape shows
  which world class the learner has effectively assumed.
- P4 (crypticity pair, D10): two worlds with equal E, different C_mu. A learner whose retained bits track E rather than
  C_mu cannot predict the cryptic world exactly.
- P5 (streaming parity, T19; Raz 2016): n in {10, 14, 18}, memory above/below ~n^2/25 bits. A cliff in samples-to-solve.
- P6 (monotone wrapper, T21; Bousquet et al. 2022): any non-monotone loss-vs-history curve is re-run with a
  holdout-accept wrapper. If the bump vanishes, it was a learner property.
- P7 (misspecification, T21; Grunwald and van Ommen 2017): an order-k Bayes fit to W3. Does loss rise with n? Does
  tempering fix it?
- P8 (nuisance geometry, T18; Ng 2004): append m iid bits, axis-aligned vs rotated (random orthogonal on a continuous
  embedding). The Bayes loss is invariant.
  - Ridge (rotation-invariant) should degrade ~linearly in m, L1 ~log m.

## 6. Metrics

- Excess log-loss vs Bayes (primary);
- excess retention (bits);
- query ops and write ops;
- the constant twin.
Decision tolerance: 0.02 nats/symbol excess, reported with a 90% CI over 32 seeds. Declared here, before any run.

## 7. Minimal build (estimate)

- ~400 LOC: worlds (6), learners (4 families x budget ladder), oracles, metrics, tests (each oracle verified against
  Monte Carlo).
- Compute: < 1 CPU-hour for the full ladder at 32 seeds.
- Any node.

## 8. What it cannot establish

- Anything about high-dimensional, continuous-field generalization (the WTP / LM01 regime).
- It calibrates concepts and instruments. It does not replace LM01.
- Learned (not hand-specified) sufficient statistics are only covered by the "learned finite-state tracker" arm, which
  is the weakest part.

## 9. Link back

Its oracle-scored locus-of-compression result is the answer-keyed version of the LM01 storage-vs-readout question
(T02). If the two disagree, that disagreement is itself a finding about the WTP worlds.
