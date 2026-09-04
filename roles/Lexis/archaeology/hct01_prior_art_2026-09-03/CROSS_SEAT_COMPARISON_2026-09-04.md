# Cross-seat comparison, from the Lexis vantage

**Date:** 2026-09-04. **Written after** Elenchus published its own comparison (`7cb1693e9`), so this
does not repeat it. Elenchus covered the sixteen-minute miss, the three-seat convergence on buried
instruments, the Techne convergence, and where its siblings are stronger. **Read that one first.**
This adds four things it does not contain, two of which are charges against me.

---

## 1. A fourth convergence Elenchus did not name: three seats, three degenerate decision rules

Elenchus's convergence is about *instruments that existed and were not reported*. There is a second
one running through the same commits, about *rules that could not do their job*, and it has three
instances in four days:

| Seat | Rule | How it failed |
|---|---|---|
| Herakles / HC-T01 | kill condition K7, preregistered | Computed at a window where the conditioner-outcome Spearman is **exactly −1.0000** and gain is a deterministic function of the conditioner. **It could not have failed to fire.** |
| Herakles / HC-T01 | mechanical-effect null at generation zero, preregistered | Measured **identically 0.00000** because a one-symbol founder gives the operator nothing to act on. **Unimplementable in its own substrate.** |
| Lexis (me) | the RA-1 decision rule in packet section 16 | **Two branches for a three-outcome test.** RA-1 returned INDETERMINATE — zero eligible points — and my second branch, applied literally, would have abandoned the line on a test that never ran. |

The programme already has doctrine for one shape of this: a gate that cannot fire. These are three
different shapes of the same disease — a gate that cannot *not* fire, a gate whose baseline does not
exist, and a rule with no branch for insufficient data. **The common cause is that all three were
fixed in advance without first computing the attainable range of their own inputs.** Preregistration
without an eligibility calculation is a ritual, not a control.

What went right, and it is the reason none of the three caused a wrong conclusion: RA-1's executing
seat refused to collapse INDETERMINATE into NO_SIGNAL even though my rule invited it, and HC-T01's
seat reported its vacuous null rather than quietly substituting the replacement.

## 2. Where I was stronger than my siblings

Recorded because the user asked for a comparison, not a confession.

- **Independent recomputation rather than reading.** I did not accept HC-T01's noise floor; I
  regrouped its committed repeat files at fixed generation, confirmed one distinct genotype per
  group, and recovered 0.02061 at generation 100 — which is exactly the quoted 0.021 and is the
  maximum of the three checkpoints, so the reported multiples are conservative. Same for the vacuous
  null. Elenchus notes this distinction against itself: reproducing a historical figure is
  reproduction; recomputing a sibling's number from their rows is adjudication.
- **A corpus-boundary measurement instead of a search.** Sweeping 19,986 GP Bibliography entries and
  finding "mutational neighbourhood" occurs **zero** times converts "we did not find it" into "the
  concept is absent from this literature's vocabulary", which is a different and stronger statement.
  It also explains why every 5-of-6 paper is Avida or Aevol.
- **Two hazards that were later confirmed by measurement.** H-2 and H-3 were arguments when I wrote
  them and are numbers now.

## 3. Where I was weaker, including one charge Elenchus levelled at itself that lands on me too

- **No preregistration.** Elenchus criticises itself for choosing a verdict after reading the
  evidence. My adjudication has the same property. An adjudication pass is not an experiment and a
  frozen verdict would be odd, but the *decision rule* I attached to my recommendation was a
  preregistration in everything but name, and it is the artifact of mine that failed.
- **I adjudicated a supplement I had not fully retrieved.** My section 14 item 1 said the evidence I
  held did not decide the Parter longitudinality question. True, but I had not obtained Figure 9C —
  a facilitated-variation scalar plotted against generations with SE over 30–40 runs. I was
  therefore ruling on a partial view of exactly the kind of supplement I had spent the pass
  insisting other seats should read in full. **Elenchus resolved it from the bytes: both readings
  were right about different figures.** My reading holds for the neighbourhood-content measures and
  for the entire NBVG comparison, which are endpoint; theirs holds for 9C, which I had not seen.
- **I missed the best available test.** NC1, the reverse-precedence control, is cheaper than either
  re-analysis I proposed and asks the prior question mine both skipped — does the detector lead or
  lag at all? It lags, by a factor of three to seven. That is not my finding.
- **I proposed the citation-set intersection nowhere.** My EC/ALife sweep was keyword-and-domain.
  Elenchus's intersection over 1187 citing records is the technique that draws the population
  correctly the first time, and I recorded the *diagnosis* (population mis-drawn twice) without
  reaching the *fix*.

## 4. One thing this comparison changes in my own record

Elenchus's adjudication produces a sharper open question than the disagreement it settled, and it
belongs in my scorecard rather than theirs, because it is a statement about what the literature
does *not* contain:

> **Parter 2008 has a longitudinal measure of HOW MUCH and an endpoint measure of WHAT, and never
> both at once. No work in this lineage has a trajectory of neighbourhood CONTENT** — when the
> previously-rewarded phenotypes entered the one-mutant neighbourhood, and whether that entry
> preceded the acquisition advantage.

That is the same gap NC1 reaches from the other side, and it narrows my section 6 finding usefully.
The six-element composition is unoccupied as an intersection; this says something stronger about one
of the cells. **A trajectory of neighbourhood content, with a reverse-precedence control, is a
better-specified successor experiment than anything in my packet's section 16** — and it is now
specified jointly by three seats that were not coordinating.

Scorecard row for Parter 2008 and contradiction CT-01 are both updated accordingly.

## 5. Repo hygiene, flagged not actioned

Thirty-eight untracked scratch files sit in the repository root — Alon-lab and Dryad HTML, PubMed
elink JSON, a JBQuim record, Wayback dumps. Timestamps and content place them in the MVG deep-dive's
working set, not mine; Elenchus has already moved four of its own out. **I have not deleted them.**
Another seat's working residue is not mine to remove on a staleness argument, and this programme has
a standing rule about exactly that. Flagged here so whoever owns them can clear them.
