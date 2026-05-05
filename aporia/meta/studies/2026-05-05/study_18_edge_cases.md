# Study 18: Edge Cases That Changed Fields

**Date:** 2026-05-05
**Owner:** general-purpose subagent (Aporia delegation)
**Substrate connection:** The 17 inconclusive entries flagged by `charon/scripts/lehmer_exhaustive_deg8_14.py`; whether to spend higher-precision-verification budget on them; whether the substrate needs a separate anomaly catalog distinct from the main result catalog.

## Problem statement (Prometheus-adapted)

Yesterday's deg-14 ±5 palindromic enumeration produced 26 Mossinghoff
rediscoveries plus 17 borderline near-cyclotomic entries that the
fixed-precision M-computation could not separate from the Lehmer
ceiling. Three operational questions:

1. **Triage.** What's the historical base-rate of *anomaly investigated
   → field-changing result*? Is the prior on the 17 entries closer to
   "noise to be discarded" or to "edge case worth higher-precision
   verification"?
2. **Catalog design.** Should the substrate maintain a separate
   anomaly catalog (analog: Steen–Seebach *Counterexamples in
   Topology*) distinct from the main Charon/Aporia/Ergon CLAIM stream?
3. **Signature.** Is there a documented structural signature
   distinguishing "anomaly that became important" from "anomaly that
   stayed noise," operationalisable as a tag/score on substrate edge
   cases?

Headline findings: (a) the historical base-rate is *low absolutely but
high relative to other discovery modes* — most numerical anomalies
turn out to be noise or rediscoveries, but the small surviving fraction
includes a disproportionate share of field-opening results; (b) the
Steen–Seebach analog is the right model but should be *typed*
(noise / borderline / counterexample / paradigm-anomaly), not flat;
(c) the literature gives a soft signature — *robustness under
re-derivation*, *resistance to local explanation*, and *structural
position adjacent to a stated conjecture or definition* — that the
substrate can encode as gating fields on each anomaly entry.

## Literature scan

**Numerical anomalies that became theory.**

- **Mertens conjecture, Odlyzko–te Riele 1985.** Mertens conjectured
  |M(n)| ≤ √n for the Möbius summatory function; numerically held
  to 10¹⁰. Odlyzko & te Riele used LLL on 2000 nontrivial zeta zeros
  to prove a counterexample exists below ~10³⁰·⁴ (later sharpened
  to ~10¹⁶ by Kotnik & te Riele 2006). The conjecture's *failure*
  reshaped how analytic number theorists treated "verified to N"
  arguments. Reference: Odlyzko & te Riele, *J. reine angew. Math.*
  357 (1985), 138–160.
- **Skewes / Pólya / Littlewood family.** π(x) − li(x) numerically
  negative for all checked x; Littlewood 1914 proved sign changes
  infinitely often. Pólya conjecture similarly false at n =
  906,150,257 (Tanaka 1980). Same lesson recurring.
- **Soliton discovery, Zabusky–Kruskal 1965.** Numerical KdV
  experiments produced collision-stable pulses; led to inverse
  scattering theory (Gardner–Greene–Kruskal–Miura 1967).
- **Lorenz 1963 / Mandelbrot 1980.** Computational outputs initially
  attributed to numerical noise opened deterministic chaos and
  fractal geometry respectively.
- **BSD, EDSAC 1958–65.** Numerical rank-vs-L-function observations
  on elliptic curves became the BSD conjecture (Clay problem).
- **Monstrous Moonshine, McKay 1978.** "196,884 = 196,883 + 1"
  coincidence noticed numerically; Borcherds proved (Fields 1998);
  spawned vertex operator algebras.
- **Apéry 1978, irrationality of ζ(3).** Numerical recurrence
  observation underpinning proof initially distrusted as too
  elementary.

**Theoretical anomalies that opened fields.**

- **Russell's paradox 1901** → ZF axiomatisation (Zermelo 1908).
- **Banach–Tarski 1924** → AC's role isolated.
- **Milnor's exotic 7-spheres 1956** + Donaldson/Freedman 1982–83
  → exotic R⁴.
- **Goodstein 1944 / Kirby–Paris 1982** — true Π⁰₂ unprovable
  in PA.
- **Hensel's p-adics 1897** — non-archimedean completion; "edge
  case" of Ostrowski 1916.
- **Dirac delta 1920s → Schwartz distributions 1944–50** —
  indispensable computational object, ~25 years without a
  foundation.

**Anomalies that stayed noise (or shrank under scrutiny).**

- **Rota's spurious correlations** in combinatorial statistics —
  many "patterns" in small-n enumerations vanish at moderate n.
- **First-digit / Benford-like over-fits** that disappear under
  base-change.
- **OEIS coincidences** that resolve to "both sequences satisfy a
  trivial linear recurrence." Sloane's editorial process treats
  most reports this way; only a fraction become A-numbered with
  cross-references that cite genuine bijections.
- **The Lehmer literature itself.** Of the ~thousands of
  near-cyclotomic polynomials found in computer searches since the
  1970s, the Mossinghoff list of small-Mahler-measure polynomials
  has grown only modestly, and the 0.1762808… record has been
  *unbeaten since 1933*. Most computer-flagged "near-Lehmer"
  candidates collapse into known families (Salem numbers, products
  of cyclotomics with small perturbation) under closer analysis.
  This is directly relevant prior probability.

**On base-rates.** I found *no quantitative meta-study* of "numerical
anomalies in mathematics → field-changing results" — the closest
references are Borwein & Bailey, *Mathematics by Experiment* (AK
Peters 2003) and Bailey, Borwein, et al., *Experimental Mathematics
in Action* (2007), which catalog dozens of cases but do not estimate
denominators. **Calibrated negative finding: the absolute base-rate
is unknown and probably unknowable**; the relative base-rate (anomaly
investigation vs. random-search investigation per unit researcher
time) appears favourable in the cases above but is selection-biased
(we hear about Mertens, not the thousands of refuted near-Mertens
heuristics).

**On signatures.** Polya, *Mathematics and Plausible Reasoning*
(Princeton 1954) and Lakatos, *Proofs and Refutations* (CUP 1976)
both characterise "fertile" anomalies as those that (i) resist
*local* repairs to the surrounding theory, (ii) recur under
*independent re-derivation* by alternative methods, and (iii) sit
*adjacent to a definition or named conjecture* rather than in the
interior. The Lehmer 17 satisfy (iii) trivially (adjacent to the
Lehmer ceiling) but have not been tested for (i) or (ii).

## Substrate-relevance

Three connections:

1. **The 17 inconclusive entries should be split by signature, not
   triaged by hand.** Literature gives a usable proxy: an anomaly is
   worth higher-precision verification when it (a) arises near a
   stated bound or conjecture *and* (b) survives an alternative
   computation method, and is "noise" otherwise. For Lehmer this
   means: re-compute M(f) for each of the 17 with (i) higher mpmath
   precision, (ii) Graeffe iteration, and (iii) symbolic factoring
   over Q to detect cyclotomic factors. Anything still hugging the
   ceiling after all three independent methods is a *real* edge
   case; anything that drops away is noise. This is cheap (each
   poly is small) and is the literature-recommended discipline.
2. **The substrate already has a place for an anomaly catalog**
   (Aporia's open-questions surface, Charon's near-miss buckets),
   but it is *not typed*. A Steen–Seebach analog with explicit
   `anomaly_kind ∈ {noise, borderline, counterexample,
   paradigm_adjacent}` plus `re-derivation_count` and
   `independent_methods` fields would let the substrate
   automatically filter down from "all flagged" to "candidates
   worth precision spend."
3. **Most flagged anomalies in this domain have historically been
   noise or rediscoveries.** The Mossinghoff list has grown
   modestly over 50 years of computer search; the prior probability
   that *any one* of the 17 is a new genuinely interesting
   small-Mahler-measure polynomial is low. The right operational
   stance is: spend the higher-precision budget *because it is
   small*, with the expectation that ≥15 of the 17 will collapse
   into known families.

## Concrete operational handles

1. **Run a three-method re-derivation on the 17 entries.** Add
   `charon/scripts/lehmer_inconclusive_triage.py` that for each
   flagged poly computes M(f) via (a) `mpmath` at prec=100, (b)
   Graeffe iteration to high index, (c) explicit symbolic
   factorisation. Tag each entry with `methods_agreeing`,
   `min_M_high_prec`, `cyclotomic_factor_found`. Cheap (~minutes).
2. **Extend the anomaly schema.** Add fields
   `anomaly_kind`, `independent_method_count`,
   `adjacent_to_named_conjecture`, `survives_local_repair`,
   `precision_budget_spent`. Default values pessimistic. Mirrors
   Steen–Seebach's per-space property table.
3. **Promotion rule.** An anomaly is promoted from "noise pile" to
   "open question" only when `independent_method_count ≥ 2` and
   `survives_local_repair = true`. This formalises Polya/Lakatos
   in a tractable gate.
4. **Maintain the catalog as a separate artifact.** Do *not* mix
   anomaly entries into the main CLAIM stream; the failure modes
   are different (CLAIMs target PROMOTE/FALSIFY; anomalies target
   *investigation budget allocation*). A separate `aporia/anomaly_catalog/`
   parallels Steen–Seebach exactly.
5. **Track the base-rate longitudinally.** Each time the substrate
   triages an anomaly batch, log `(n_flagged, n_promoted,
   n_resulted_in_named_finding)`. After 6–12 months Prometheus
   will have its *own* base-rate, replacing the unknown literature
   prior. This is the operational answer to "what's the base-rate?"
   — *measure it on substrate output, since literature does not
   give it*.

## Falsification

Central claim — *most flagged near-Lehmer entries collapse under
independent re-derivation; the few that survive (i)+(ii)+(iii) are
worth precision spend; an anomaly catalog separate from the CLAIM
stream is the right architecture* — would be refuted by:

- All 17 entries surviving the three-method re-derivation as
  genuinely new small-Mahler-measure polynomials below 1.18 (would
  refute the prior; would also be a substantial result in its own
  right).
- A concrete demonstration that the literature's "robust under
  re-derivation" heuristic mis-classifies a known
  paradigm-anomaly. The Mertens case actually *failed* hand-checks
  for decades and was resolved only via a non-obvious LLL method,
  so the heuristic is imperfect — but it is the best public
  signal.
- Evidence that mixing anomalies into the CLAIM stream improves
  PROMOTE rates relative to a separate catalog. None expected.

## Open questions raised

1. Should the substrate distinguish between "anomalies adjacent to
   a stated conjecture" (Lehmer ceiling, BSD rank, Mertens bound)
   and "anomalies adjacent to a *definition*" (exotic spheres
   adjacent to "smooth structure")? Literature suggests the latter
   are rarer but more transformative.
2. The Mossinghoff list collapse rate — what fraction of
   computer-flagged near-Lehmer candidates have *historically*
   collapsed under cyclotomic factoring? Sharper number would set
   a tighter Bayesian prior on the 17.
3. The Mertens-style "verified to large N → still false" risk
   applies in reverse to substrate kills: how many *kill* CLAIMs
   were issued on the basis of finite-N negative search? Audit
   needed.
4. Does the substrate's `survives_local_repair` field require a
   formal language for "local repair" (parameter tweaks,
   precision bumps, definitional softening)? If yes, this is a
   small DSL design problem, not just a tag.
5. Is there a productive analog of *fertile vs sterile
   counterexample* for the substrate's null-test failures? A null
   that fires once is sterile; one that fires across the battery
   in a structured pattern is fertile (cf the Pattern Stratifier
   Invariance work in the recent commit log).

## Citations

- Odlyzko, A. M. and te Riele, H. J. J. "Disproof of the Mertens
  conjecture." *J. reine angew. Math.* 357 (1985), 138–160.
- Kotnik, T. and te Riele, H. J. J. "The Mertens conjecture
  revisited." *Algorithmic Number Theory, ANTS-VII*, LNCS 4076
  (2006), 156–167.
- Littlewood, J. E. *C. R. Acad. Sci. Paris* 158 (1914), 1869–1872.
- Tanaka, M. *Tokyo J. Math.* 3 (1980), 187–189.
- Zabusky, N. J. and Kruskal, M. D. *Phys. Rev. Lett.* 15 (1965),
  240–243.
- Gardner, Greene, Kruskal, Miura. *Phys. Rev. Lett.* 19 (1967),
  1095–1097.
- Lorenz, E. N. *J. Atmos. Sci.* 20 (1963), 130–141.
- Mandelbrot, B. *The Fractal Geometry of Nature*. Freeman, 1982.
- Birch, B. J. and Swinnerton-Dyer, H. P. F. *J. reine angew.
  Math.* 218 (1965), 79–108.
- Conway, J. H. and Norton, S. P. *Bull. LMS* 11 (1979), 308–339.
- Borcherds, R. E. *Invent. Math.* 109 (1992), 405–444.
- van der Poorten, A. *Math. Intelligencer* 1 (1979), 195–203.
- Milnor, J. *Ann. Math.* 64 (1956), 399–405.
- Freedman, M. H. *J. Differential Geom.* 17 (1982), 357–453.
- Donaldson, S. K. *J. Differential Geom.* 18 (1983), 279–315.
- Kirby, L. and Paris, J. *Bull. LMS* 14 (1982), 285–293.
- Hensel, K. *Jahresbericht DMV* 6 (1897), 83–88.
- Schwartz, L. *Théorie des distributions*. Hermann, 1950.
- Banach, S. and Tarski, A. *Fund. Math.* 6 (1924), 244–277.
- Polya, G. *Mathematics and Plausible Reasoning*. Princeton
  University Press, 1954.
- Lakatos, I. *Proofs and Refutations*. Cambridge University
  Press, 1976.
- Steen, L. A. and Seebach, J. A. Jr. *Counterexamples in
  Topology*, 2nd ed. Springer, 1978; reprinted Dover 1995.
- Borwein, J. and Bailey, D. *Mathematics by Experiment:
  Plausible Reasoning in the 21st Century*. AK Peters, 2003.
- Lehmer, D. H. "Factorization of certain cyclotomic functions."
  *Ann. Math.* 34 (1933), 461–479.
- Mossinghoff, M. J. "Polynomials with small Mahler measure."
  *Math. Comp.* 67 (1998), 1697–1705. Updated tables at
  https://www.mossinghoff.org/lehmer/
- Internal: `F:/Prometheus/charon/scripts/lehmer_exhaustive_deg8_14.py`,
  `F:/Prometheus/charon/scripts/lehmer_spectrum_audit.py`,
  `F:/Prometheus/aporia/meta/studies/2026-05-05/study_02_failure_surfaces.md`
  (Steen–Seebach as failure-surface analog).

*Calibrated negative finding: the absolute base-rate of "numerical
anomaly → field-changing result" is not quantified in the
literature and likely cannot be honestly estimated due to selection
bias on the published cases. The substrate-actionable answer is to
**measure its own base-rate longitudinally** rather than import a
literature prior. For the immediate triage of the 17 inconclusive
Lehmer entries, the literature-supported discipline is
re-derivation by ≥2 independent methods plus cyclotomic-factor
detection; the strong prior is that ≥15 will collapse, but the
spend is small and the 50-year stability of the 0.176280… record
makes the residual a high-leverage long-shot worth checking. A
typed anomaly catalog modelled on Steen–Seebach but indexed by
`{noise, borderline, counterexample, paradigm_adjacent}` is the
recommended architecture; do not merge into the CLAIM stream.*
