# Memory versus Lock-In

The machinery that stores useful historical correlations is the same machinery that can trap
the system in its past. This separates the two readings of one mechanism.

## The source says it itself — RECOVERED

S1, on its own generalisation result:

> "this type of generalisation is (necessarily) equivalent to a 'failure' to restrict
> phenotypes to a set of training patterns accurately."

Memory and lock-in are not two mechanisms with a dial between them. They are one mechanism
described from two directions. A map that reproduces the training set exactly has no
generalisation; a map that generalises has necessarily lost the ability to be arbitrary.

## When memory helps and when it constrains

| regime | effect | evidence |
|---|---|---|
| future targets share the structural regularity of past targets | memory HELPS — fewer mutations to a good phenotype | S1 (within-family), S3 (unseen environments, same regularity) |
| future targets violate that regularity | memory CONSTRAINS — orthogonal phenotypes become expensive or unreachable | DERIVED; **not measured** in the recovered text |
| few, noiseless training targets | OVER-FITTING: the map memorises instead of generalising | S3, explicitly |
| noisy targets, or costly connections | generalisation improves | S3, RECOVERED |

**S3 is the important result here**: it identifies the *controls* on the balance, and they are
the standard learning-theory ones. RECOVERED — "training with noisy data, i.e., adding noise
during the learning phase (jittering)" and "introducing a connection cost term into the
objective function that favours connections of small values (L2) or fewer connections (L1)",
mapped respectively to "extrinsic noise in selection" and "the reproduction and maintenance
costs of the gene regulatory interactions".

## Failure modes predicted by the motif — DERIVED, none measured in S1–S3

Hebbian outer-product accumulation is unnormalised, which predicts specific pathologies. These
are consequences of the motif, listed as things to look for. They are **not findings**.

1. **Spurious attractors** — unnormalised superposition creates mixture states never selected.
2. **Capacity saturation** — too many uncorrelated targets in one `W` degrades all of them.
3. **Historical over-representation** — frequently selected combinations acquire deeper basins,
   so the generator drifts toward historical modes regardless of current selection.
4. **Orthogonal inaccessibility** — a phenotype orthogonal to the stored structure requires the
   mutation to fight `W`. The bias that accelerates within-family search decelerates
   out-of-family search.
5. **Rigidity under environment switch** — a map tuned to regularity R1 must *unlearn* R1
   before it can acquire R2.

## The Prometheus-relevant statement

> A machine that becomes better at producing yesterday-like solutions is not thereby more
> evolvable. It is more evolvable **only over the family of futures that resemble its past.**

This is the sharpest caution the lineage offers, and it is why "developmental memory + open-ended
environmental novelty" is the highest-value untested composition: that experiment looks for the
ceiling rather than the benefit.
