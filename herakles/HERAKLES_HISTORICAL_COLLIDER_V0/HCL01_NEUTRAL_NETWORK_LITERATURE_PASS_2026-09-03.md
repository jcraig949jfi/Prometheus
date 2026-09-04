# HC-L01 — Neutral genotype network literature pass

**Date:** 2026-09-03
**Lane:** HC-L01, highest-priority lane of the history-conditioned accessibility (HCA) directive
**Directive:** `prompts/HC_L01_neutral_network_literature_directive.txt`
**Directive sha256:** `094c9e295853e432c63ed5b54c4dd8c4e86b89c7b09d905a32ebc3ce0685f3c7`
**Rows:** `HCA_NEUTRAL_NETWORK_ROWS.jsonl` (5 specimens), `HCA_NEUTRAL_NETWORK_NEGATIVES.jsonl` (4 negative controls)

## Scope note and relation to work already in this repo

This lane screens the **neutral genotype network / RNA genotype-phenotype map** literature. That
slice was absent from `HISTORY_CONDITIONED_ACCESSIBILITY_REGISTRY.jsonl`, which covers evolutionary
computation, gene-regulatory-network evolvability, Kashtan and Alon, and Petak et al. Nothing here
duplicates or overrides those rows.

One cross-reference matters and must travel with this document. The registry already carries
`spec-petak-2025-VERIFIED` at **H3**, cheap-state conditioning CLEARED. That specimen is a
dynamic-fitness-landscape GRN study, **not** a neutral-network study, so it does not answer this
lane's critical question, which is specifically about position on a neutral network. Both statements
are true at once: the programme has a verified H3 in one substrate class, and the neutral-network
literature contains none.

---

## THE CRITICAL QUESTION, ANSWERED

> Has anyone measured position on a neutral network at time t, then the one-step reachable phenotype
> distribution, then subsequent innovation at time t+n, and shown that the accessibility term carries
> information beyond current-state variables?

**No. Not in this literature, and not once in thirty years of it.**

The three components exist separately and are individually mature. Nobody has assembled all three in
one experiment on a neutral network.

- **Position at t plus reachable distribution** (H2) is *routine*, well-measured, and often
  exhaustive. Wagner 2008, Draghi et al. SI 6.1, Greenbury et al. 2016 and Aguirre et al. 2011 all
  do it cleanly, some by enumerating every sequence in the space.
- **Subsequent acquisition at t+n** is also routine, in Cowperthwaite et al. 2008, Draghi et al.
  SI 6.2, Zheng et al. 2019 and Wagner 2023.
- **The conditioning step** — accessibility outpredicting fitness, robustness or length — is
  attempted in exactly one paper in this pass, Wagner 2023, and that paper is not on a neutral
  network.

### Closest paper, and exactly what it is missing

**Wagner A (2023), "Evolvability-enhancing mutations in the fitness landscapes of an RNA and a
protein", Nature Communications 14:3624.** Figures 1g and 2f.

What it has: combinatorially complete empirical fitness landscapes, so the full one-mutant
neighbourhood fitness distribution is enumerated, not sampled, for both backgrounds of every pair;
10,000 stochastic adaptive walks per landscape measuring subsequent fitness gain; and — uniquely —
**the conditioning is built into the definition**. Equation 2 requires the neighbourhood improvement
to exceed the mutation's own fitness benefit, so evolvability-enhancing status is a residual after
the additive current-state contribution is subtracted. The residual confound then runs the right
way: in the protein landscape the direct benefit of EE and non-EE mutations is *similar*, and in the
RNA landscape the EE mutations' direct benefit is *smaller* than non-EE, yet the EE walks still end
higher. Protein step three: 0.81 versus 0.75, P = 8e-151. RNA: 0.51 versus 0.48, P = 2.2e-39.

What it is missing, precisely:

1. **The present state is not matched.** Only *beneficial* EE mutations are studied. The mutant and
   the wild-type differ in fitness, so the H1/H2 precondition fails even though the H3 test passes.
   The levels are not nested in this paper and must not be collapsed.
2. **It is not a neutral network.** No neutral set, no position, no phenotype held constant.
3. **Acquisition is simulated**, as adaptive walks over a static empirical landscape, not measured
   innovation in an evolving population.
4. **"Innovation" is fitness gain**, not the arrival of a novel phenotype.

The decisive sentence is Wagner's own. He defines the matched-fitness case — the neutral EE mutation,
his Equation 1, exactly the object this programme is chasing — and then writes:

> "I define but do not explicitly study neutral EE mutations further here, because such mutations
> cannot be reliably identified in large populations with today's technology to measure fitness."

That is the field's own account of why the target level is unoccupied. It is a measurement-precision
barrier, not a conceptual gap, and the barrier is smaller in silico than in vivo.

### The directive's specific question about Draghi et al. SI section 6

**A longitudinal accessibility measurement on evolving populations DOES appear in the Supplementary
Information, in section 6.2. It cannot answer the H3 question, for two reasons, both verbatim.**

SI 6.2 evolves Wright-Fisher populations of 24-nt RNA sequences (N = 500, mu = 0.0002, Vienna 1.6.1,
M = 500 or 200 designated high-fitness structures) from measured founders until the first
high-fitness phenotype arises. Per founder they measured the probability of being pre-adapted (K/P),
the mutation rate of pre-adapted genotypes to high-fitness types (1/K), and the probability that a
non-pre-adapted founder has a pre-adapted *neighbour* (f). That is a genuine accessibility-at-t /
acquisition-at-t+n design.

It fails the conditioning test **by construction**:

> "the mutation rate to high-fitness types declined monotonically with q in the RNA data, and so we
> used a linear regression of this relationship in our analytic predictions."

Accessibility was not tested against robustness — it was *modelled as a function of it*. The two are
collinear by design and no independent accessibility contribution can be read off Supplementary
Figure 12.

It also fails the matching precondition:

> "each replicate begins from a potentially unique genotype"

Founder *fitness* is matched trivially (all wild-types viable, all alternatives inviable) but founder
*phenotype* is not, and phenotype identity is precisely the variable Cowperthwaite et al. 2008 showed
drives reachability.

SI section 6.1 is separately valuable and is a clean H2 on matched phenotype: from 100,000 sampled
genotypes per sequence length, f_e ≈ 0.26–0.34, meaning roughly 30 per cent of a genotype's accessible
phenotype set is redrawn by a **single neutral mutation**. Their words: *"the phenotypic
neighbourhoods of neutral neighbors differ significantly."*

---

## NEGATIVE CONTROLS — same state, different future, no consequence

The directive asked for these explicitly. This pass found four, and one of them is the strongest
counter-evidence to the programme's hypothesis found anywhere so far.

1. **Cowperthwaite et al. 2008 — starting network position does not predict acquisition.** Across
   2,400 forward simulations, *target* phenotype abundance predicted arrival (r = 0.76, P = 2.2e-4)
   but *founding* phenotype abundance predicted nothing (r = -0.023, P = 0.17). Draghi et al.
   summarise it in their SI: *"Cowperthwaite et al. (2008) found no relation between the size of the
   neutral network on which a population began, and its success at evolving to a distant phenotypic
   optimum."* This is the imported analogue of our own K7 kill.

2. **Ancel and Fontana 2000 — the sign inverts.** Three sequence classes sharing an identical
   minimum-free-energy structure differ in neutrality (0.184 random, 0.412 neutrally evolved, 0.456
   canalised), and the class with the richest history became an evolutionary **dead end**. More
   history bought *less* acquisition. Any HCA claim needs a pre-registered direction and a reason
   for it.

3. **Wagner 2008 — a large H2 that was never connected to acquisition**, with the cheap-state
   relation pointing the wrong way at the genotype level: robustness and evolvability correlate at
   Spearman s = -0.64, p < 1e-17.

4. **Greenbury et al. 2016 and Aguirre et al. 2011 — the best-quantified H2 measurements in
   existence, with no acquisition arm at all.** Measuring the effect is demonstrably not the
   bottleneck.

**Two warnings that must travel with any citation of this literature.**

- **Tautology risk.** In Ancel and Fontana the accessibility measure *is* neutrality, i.e.
  mutational robustness. Accessibility cannot be shown to beat robustness where the two are the same
  number. Check for this before quoting any robustness-evolvability result as support.
- **Plastogenetic congruence is cross-sectional.** It is computed on a single genotype at one
  instant — its thermal plastic repertoire against the folds of its one-error mutants. It is not a
  time-t-predicts-time-t+n measurement and must never be cited as one.

**Effect-size warning.** The matched-phenotype accessibility difference is large in RNA
(Greenbury ratio 1.357) but modest elsewhere: 1.063 in Polyomino, 1.025 in HP lattice protein. A
programme betting on this phenomenon outside an RNA-like substrate should compute the standard error
before choosing a gate.

---

## What this lane recommends

1. **Wagner 2023 is the template to copy, not just cite.** Code at
   `https://github.com/andreas-wagner-uzh/EE_mutations`, protein landscape at GEO GSE153897, RNA
   landscape in the source paper's Supplementary Table S1. The neutral-EE arm he declined to run —
   bin delta-w to within measurement error of zero and repeat his analysis — is a **re-analysis of
   surviving artifacts**, not a new experiment. It is the cheapest available shot at the exact level
   this programme needs, in a substrate where present state is matched by construction.

2. **Draghi SI 6.2 is directly re-runnable** and the fix is specified: hold founder phenotype fixed,
   and enter measured accessibility and robustness as *competing* predictors rather than nesting one
   inside the other.

3. **Get the Hayden 2011 main text.** It is the closest natural-substrate analogue with a proper
   remove-the-history arm, and the only thing blocking a proper classification is access.

---

## Per-work records

Full field-by-field records are in the JSONL rows. Summary table of H-levels assigned:

| Work | Access | H-level |
|---|---|---|
| Wagner 2008, paradox resolved | FULL_TEXT (PMC extraction) | H2 |
| Draghi et al. 2010 + SI 6 | FULL_TEXT + SI verbatim | H2 |
| Wagner 2023, EE mutations | FULL_TEXT | H3 on conditioning, matched-state precondition NOT met |
| Zheng, Payne, Wagner 2019 | FULL_TEXT (SI 403) | H4-shaped, H3 untested |
| Hayden, Ferrada, Wagner 2011 | ABSTRACT + full SI | H2 verified, higher unresolved |
| Greenbury, Schaper, Ahnert, Louis 2016 | FULL_TEXT | H2 |
| Greenbury and Ahnert 2015 | FULL_TEXT | H1 |
| Greenbury, Louis, Ahnert 2022, navigability | FULL_TEXT (preprint) | H1 |
| Aguirre et al. 2011 | FULL_TEXT | H2 |
| Catalán et al. 2018, toyLIFE | FULL_TEXT | H1 |
| Fontana and Schuster 1998, Continuity | FULL_TEXT | H1 |
| Ancel and Fontana 2000, Plasticity | FULL_TEXT | H2 |
| Cowperthwaite and Meyers 2007, review | FULL_TEXT | H1 (review) |
| Cowperthwaite et al. 2008, Ascent | FULL_TEXT | H0 bordering H1 |
| Fontana and Schuster 1998, Shaping space | NOT_FOUND | unscorable |

**A note on the "navigable" result.** Greenbury, Louis and Ahnert 2022 is about accessibility and is
highly relevant background, but its navigability claim is a *structural, map-level* property — does a
monotonically-increasing-fitness path exist between a phenotype pair — established by path search
over random fitness assignments, with one representative genotype per phenotype. No comparison in it
holds present state fixed while varying only network position. The word must not be allowed to
inflate the level.
