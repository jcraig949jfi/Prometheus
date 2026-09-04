# H. TEMPORALITY ANALYSIS — Kouvaris et al. 2017

Directive §11 poses a binary and asks for it to be resolved explicitly.

---

## 1. The two patterns, and which one this is

**Pattern 1 — longitudinal precursor:**
```
detector changes at generation t  →  subsequent acquisition changes at t+n, in the SAME run
```

**Pattern 2 — treatment-level:**
```
treatment A evolves architecture X ; treatment B evolves architecture Y
                          →  X later generalises better than Y
```

**Kouvaris 2017 is Pattern 2, with a longitudinal detector attached to it.**

That is a real third thing and it deserves its own name rather than being forced into the binary.
The paper has:

- a **longitudinal detector trajectory** (Fig 3, S1 Figs B and D) — genuinely within-run, sampled at
  every recorded epoch, in all four arms; and
- an **acquisition outcome** (Fig 5) measured **once**, after evolution has stopped, on the frozen
  endpoint architecture.

The trajectory and the outcome are never joined at any point other than the endpoint. So the paper
is Pattern 2 whose treatment-level claim is *supported* by a within-run trajectory, but it is not
Pattern 1, because nothing at generation `t` is ever related to anything at `t+n`.

**Falsification question F4 — "the result is treatment-level and lacks within-run longitudinal
precursor evidence" — is TRUE**, with the qualification that the longitudinal detector itself does
exist, which is more than F4 as phrased assumes.

## 2. What is measured when

| Object | When measured | Multiplicity | Uncertainty |
|---|---|---|---|
| χ² training error | every recorded epoch, during evolution, all 4 arms | runs unstated | **none reported** |
| χ² test error | same | runs unstated | **none reported** |
| Shannon entropy of the induced distribution | over evolutionary time (S1 Fig D) | runs unstated | **none reported** |
| Regulatory coefficients `b_ij` | over evolutionary time (S1 Fig A/S4) | runs unstated | **none reported** |
| **Generations-to-target (acquisition)** | **once, after evolution ends, on frozen `B`** | 1000 runs per environment per arm | implied by boxplot spread in Fig 5 |

The asymmetry is the finding: the detector is a time series and the outcome is a single endpoint
measurement. A time series cannot be regressed on a scalar.

## 3. The one place the paper comes closest to precedence, and why it still is not

The over-fitting narrative is genuinely temporal and is the paper's best result:

> *"Natural selection initially improved the fit of the phenotypic distributions to both
> distributions of past and future selective environments. Then, while the fit to past selective
> environments continued improving over evolutionary time, the fit to potential, but yet-unseen,
> environments started to deteriorate."*

and the dashed line in Fig 3A marks *"when the problem of over-fitting begins, i.e., when the test
error first increases."*

This is a **within-run change point in the detector**, identified in time. It is exactly the kind of
object a precursor analysis needs. **But nothing is measured after it.** No acquisition assay is run
at the change point, or before it, or at a matched later time. The paper's claim is that stopping
there would have been ideal — an inference from the detector's own trajectory, supported afterwards
by the endpoint comparison, not by any measurement taken at `t+n` within the run.

**A cheap experiment the authors did not run, and the single most informative thing a reconstruction
could add:** freeze `B` at several points *along one run* — before the change point, at it, and well
after it — and run the existing Fig 5 acquisition assay at each. That converts Pattern 2 into
Pattern 1 within a single arm, needs no new instrument, and costs one extra sweep of an assay the
paper already implements. It is the first item in `O_SFE_CALIBRATION_PROPOSAL.md`.

## 4. Would precedence even be informative here? The coupling check

Herakles preregistered this test for Toussaint as TRAP 2. Applied to Kouvaris it returns a clear
answer, and the answer is worse than for Toussaint.

Both readouts are deterministic functionals of the **same frozen `B`** over the **same `G`-space**
through the **same developmental map**:

- detector = push-forward of the uniform measure on `G` through `develop(·, B)`, binned;
- acquisition = hill-climb over `G` through `develop(·, B)`, timed.

They are not two noisy views of a latent quantity; they are two deterministic reads of one object.
Consequently:

- **A "lead" would be uninterpretable.** If the detector moved before the acquisition measure in the
  same run, that would say the push-forward statistic is more sensitive to small changes in `B` than
  the hill-climbing statistic — a fact about estimator sensitivity, not about precedence in nature.
- **The only regime in which precedence would be informative is one where the two can genuinely come
  apart**, i.e. where accessibility changes while the map's expressible set does not. That regime is
  precisely where a **local** detector differs from a **global** one, which is the gap HC-T01
  targets.

So the coupling analysis does not merely narrow Kouvaris — it *explains why HC-T01's local detector
is the right instrument for a precedence claim and Kouvaris's global one is not.* That is the
strongest surviving argument for HC-T01 found anywhere in this pass, and it is worth more than the
missing-cell argument it was originally justified by.

## 5. Deep time versus micro time — a distinction the lineage uses and Prometheus should adopt

The sibling paper (Kounios et al., arXiv 1612.05955) makes the timescale separation explicit and
names it: `B` evolves over *"deep evolutionary time"* while `G` moves within a
*"microevolutionary episode"*. Under that framing the specimen's design is:

- **deep time:** `B` evolves; the detector is sampled along this axis (Fig 3).
- **micro time:** `G` hill-climbs under frozen `B`; acquisition is measured on this axis (Fig 5).

The two axes are measured in different experiments and joined only at the endpoint. Kounios does
better: it measures the micro-time outcome **at the end of every deep-time episode**, in both arms,
over 30 replicates — which is a genuine within-run interleaving of the two axes. That is why Kounios
is closer to Pattern 1 than the specimen is, and it is recorded in `K_DESCENDANT_SEARCH.md`.

**Adopting the deep/micro vocabulary sharpens HC-T01's own statement**, which currently says
"within runs" without saying within which of the two clocks. The precise version is: *the detector is
read on the deep-time clock, and the acquisition it is supposed to predict is read on the micro-time
clock nested inside it.* HC-T01's preregistration should say that explicitly, because the whole
precedence claim depends on which clock the lead is measured against.
