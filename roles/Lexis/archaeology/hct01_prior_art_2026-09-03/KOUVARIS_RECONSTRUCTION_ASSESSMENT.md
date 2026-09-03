# KOUVARIS RECONSTRUCTION, ASSESSED AS AN INSTRUMENT TEST

Directive §7. The working position proposes a narrow reconstruction of Kouvaris 2017 as an external
positive-control / detector-calibration test, possibly ahead of further HC-T01 spend. **This section
attacks that proposal. It does not survive intact.**

---

## 1. The decisive objection: it calibrates the wrong instrument

| | HC-T01's detector | Kouvaris 2017's detector |
|---|---|---|
| what is sampled | the **one-step offspring cloud** produced by the real variation operator from the current genotype | **5000 Sobol points uniform over the whole `[-1,1]^16` cube**, developed through the current `B` |
| substrate | discrete symbol strings with rewriting operators, variable length | continuous recurrent GRN, fixed 16 traits |
| statistic | modular degree, neutral degree | chi-squared of a phenotype distribution against a Hebbian-ideal reference |
| what a correct reading proves | something about reachability *from here* | something about what the map can express *from anywhere* |

These are different objects, established earlier in this programme's own record and re-verified from
the Kouvaris Methods and from `findErrors.m`. **A detector that correctly ranks Kouvaris's four arms
has demonstrated that it can read a global expressibility distribution. It has demonstrated nothing
about one-step local accessibility**, which is the only thing HC-T01's detector measures.

This is precisely the failure mode the directive names in §7: *"would it mostly test a different
object and create false confidence?"* The answer is yes, and the false confidence would be specific
and dangerous — it would licence the sentence "our accessibility detector recovers a known published
effect" when what was recovered is a different kind of accessibility.

## 2. The calibration has, in substance, already been done — in the right substrate

HC-T01's historical-validation stage did exactly what the working position proposes, against
Toussaint rather than Kouvaris:

- **V2, and it is a detector value, not a fitness value.** Neutral degree rises **0.504 → 0.657**
  against Toussaint's published **0.45 → 0.70**, both endpoints within about 1.1 run-to-run standard
  deviations of figure-read values.
- V1 (genome length 25 → 11 by generation 200) and V6 (17.6% non-optimal against a stated "around
  20%", 0 of 10 converging) also passed, and V6 is an *ablation-arm* target.
- V4 (period-5 stripes in the mutual-information matrix) passed as a structural test of the same
  instrument.
- Unprompted, the reconstruction reproduced both misaligned modules the thesis names by hand,
  `deabc` and `bcdea`, and produced a length-11 optimum structurally identical to the thesis's.

**An external, published, quantitative target was recovered by this programme's own detector, in the
substrate where that detector is used.** Proposing a second calibration in a different substrate,
against a different statistic, is not obviously an improvement on that; it is a different test.

## 3. It could pass for the wrong reason, and the mechanism is concrete

Kouvaris's four arms differ enormously — the L1 arm reaches **zero** generalisation error while the
control over-fits. Ranking them requires only that a detector read the induced phenotype distribution
approximately correctly. **Almost any competent distribution estimator will rank them.** The test has
very low discriminating power precisely because the published effect is so strong.

A pass would therefore be weak evidence, and a reader would over-read it.

## 4. A failure would be uninterpretable, and failure is likely

The Kouvaris record carries seven enumerated ambiguities, three of which are direct
code-versus-paper contradictions:

- P(`B` mutates per step): **1/15** in Methods, **1/2** in Results, **1** in the recovered code.
- sigmoid gain `alpha`: **0.5** in S1, **0.3** in the code.
- developmental steps `T`: **10** in S1, **15** in the code.
- and most consequentially, the committed `GRN.m` **clamps `G` to the target** at each environmental
  switch with the gene-mutation line commented out, while the published Methods describe a point
  mutation on `G`. Those are different experiments.
- the phenotype-space size is `2^12` in two figure captions and `2^16` everywhere else.
- the number of evolutionary replicates is **never stated** anywhere, and the recovered main script
  has no replicate loop, so there is no historical uncertainty to inherit.

Given that, a failed reconstruction cannot distinguish (a) our detector is wrong, (b) our
reconstruction picked the wrong branch of a contradictory record, (c) the historical figures came from
a configuration nobody can now identify. **A calibration whose failure mode is uninterpretable is not
a calibration.** This is the sharpest argument against the proposal and it is not a matter of taste:
the ambiguity count is a property of the recovered record, not of our reading of it.

## 5. What genuinely transfers from Kouvaris, and it needs no reconstruction

Three design elements are worth adopting, and all three can be adopted by reading, which has already
happened:

1. **A held-out target class defined by construction**, so that generalisation has a non-circular
   meaning and `REACHES_PREVIOUSLY_UNREACHABLE` can be distinguished from `ACQUIRES_FASTER`. HC-T01
   currently has a single fixed target and cannot make that distinction.
2. **An entropy statistic with a structurally derived target value.** For `k` independent modules the
   generalising optimum is *exactly* `k` bits. That is a gate whose attainable range is computable
   before the run — rare in this literature and directly aligned with this programme's own gate
   doctrine. Note it can be computed on HC-T01's **already committed** data; Toussaint's target has
   period 5, which supplies the structural prediction.
3. **One frozen probe set reused across all arms and checkpoints.** HC-T01 already adopted this.

**None of the three requires rebuilding the GRN.**

## 6. What must NOT be reconstructed, if anyone reconstructs anything

Reconstructing these converts calibration into a research project and should be refused:

- the Fig 5 acquisition assay (1000 runs × 2500 generations × 8 targets × 4 arms);
- the `2^16` exhaustive training-set enumeration, which in the original replaced evolution with
  Hebb's rule for tractability and therefore does not even test the evolutionary claim;
- the `lambda` and `kappa` sensitivity sweeps.

## 7. Minimum useful version, if the programme overrides this assessment

If a reconstruction happens anyway, the smallest defensible version is: **the control arm and the L1
arm only, entropy as the single readout, validated against the two structurally derived values (16
bits untrained, 4 bits under L1), with the reconstruction's own run-to-run spread computed before any
tolerance is chosen.** Two arms, one statistic, two pre-derived targets. Everything else is optional.

Even this tests global expressibility, not local accessibility. It would validate that Prometheus can
*read a distribution*, not that it can read the distribution HC-T01 depends on.

## 8. Verdict on the proposal

- `KOUVARIS_RECONSTRUCTION_USEFUL` — **MARGINAL**. It would demonstrate distribution-reading
  competence and would recover a strong published effect, but against a detector class HC-T01 does not
  use, in a substrate HC-T01 does not use, with an uninterpretable failure mode.
- `KOUVARIS_RECONSTRUCTION_REQUIRED_FIRST` — **NO**. The equivalent calibration has already been
  passed against Toussaint's own published detector values in the correct substrate, and the two
  cheap re-analyses in `CAUSALITY_AUDIT.md` §1c dominate it on information per unit of compute,
  because they operate on data already committed and they interrogate the exact cells that failed.

**The working position's second clause does not survive.** Its first clause — that HC-T01's original
justification is obsolete — does survive, for reasons the working position did not state.
