# D-LEVEL SURVEY 1 — 2026-09-03 — clearing the six remaining reachability candidates

Run under ruling authorisation 1: *"Finish the remaining six detector candidates before making any historical-blindness claim."* Ladder defined in `Q_DETECTOR_PARTS_REGISTRY.md`.

**Headline: no clean D4 or D5 was found. The residual hypothesis survives its first serious attack.** But two of the seat's priors were wrong, three D3s exist where fewer were expected, and two unread papers are D4-shaped on their face and could still overturn it.

Method note, which bears on how much weight this carries: the search budget was exhausted before the sweep began, so every source was located without keyword search, via open-access APIs, bibliographic records and author archives. Every PDF was extracted locally rather than trusted to a fetch summariser, after the summariser confabulated a plausible but wrong answer on one paper and local extraction corrected it. Nothing below is quoted from memory.

---

## Results

| Candidate | D-level | Basis |
|---|---|---|
| Wagner & Altenberg 1996 | **D0** paper-level, **D3** for Figure 3 alone | Review, but Figure 3 is simulation data |
| Hu & Banzhaf, main line | **D2** | Exhaustive enumeration, no population |
| Hu, Banzhaf & Moore PPSN 2014 | **D3** | Population mean per generation, n=1 run |
| Dolson & Ofria MODES 2019 | **D0** on this ladder | Activity and persistence, not accessibility |
| Toussaint 2001; PhD thesis 2003 | **D3** twice | Monte Carlo exploration density over generations |
| Toussaint FOGA 2003; arXiv 2002 | **D0** | The papers whose *titles* promise it contain no measurement |
| Toussaint & Igel CEC 2002 | **D3** | Population-averaged, 10,000 generations, with ablation |
| Andreas Wagner 2008 | **D3** | Longitudinal population accessibility, Results 2(d) |
| Ciliberti, Martin & Wagner 2007 | **D2** | Metropolis sampler, selection explicitly excluded |
| Bedau & Packard 1992-1998 | **D0** on this ladder | Usage and persistence counters |
| Draghi et al. 2010 (bonus) | **D5-synthetic / D2-measured** | Accessibility is a model parameter, not an observable |
| Cowperthwaite et al. 2008 (bonus) | **D2 + outcome** | Closest structural template for a real D4 |
| Franke et al. 2011 (bonus) | **D0** | Combinatorics on a fixed landscape; "generation" appears zero times |

---

## THE FINDING THAT MATTERS: Toussaint had every part and never assembled them

This is the single most important result of the sweep, and it is a direct empirical confirmation of the ruling's reframe, one level up from where the reframe was aimed.

By 2003 Marc Toussaint possessed, in his own published work:

1. a **formal definition** of the phenotypic exploration distribution, with the σ-embedding and the σ-evolution theorem;
2. a **working Monte Carlo estimator** for it, at 2000 samples per individual per generation;
3. a **population-wide longitudinal readout**, tracked over 1000 to 2000 generations;
4. a **clean 2x2 ablation** of the mechanism that changes accessibility, with second-type mutations at 0.1 versus 0, ten trials per cell.

He never ran item 2 inside item 4.

Where accessibility is measured longitudinally, selection is deliberately flat on a neutral set, so by construction nothing can be acquired. Where acquisition happens and the mechanism is causally perturbed, only fitness is plotted. **Running his own estimator inside his own ablation would have produced a D4 or D5 result in 2003, with no new theory and no new instrument.**

The ruling said: lots of microscopes were built, pointed at different things, and rarely assembled into one instrument. This is that statement instantiated inside a *single researcher's own body of work* across two years. The parts were not distributed across decades and disciplines here. They were distributed across two experiments by one person.

That materially raises the prior that the composition opportunity is real and general, and it lowers the prior that anyone will have gotten there first by accident.

A second, weaker instance of the same shape: MODES already performs a per-generation, population-wide, single-site knockout and null-substitution scan on every organism, and the authors note a refinement substituting all possible alternatives. That is genuine one-mutant-neighbourhood instrumentation, running every generation, **reduced to a scalar count of informative sites**. MODES is one reduction step away from being a D3 accessibility detector and does not take it.

---

## Two corrections to the seat's priors

**Andreas Wagner 2008 is D3, not D2.** The seat expected a static genotype-network analysis. Figure 2 is indeed that. But Results section 2(d) establishes a population of 500 identical sequences, subjects it to repeated rounds of mutation and neutrality-filtered selection, and after each round determines the number of unique structures in the neighbourhood of the **entire population**, plotted against generations. That is longitudinal population accessibility.

Two caveats keep it out of D4. Selection is a viability filter only, with no directional pressure toward a target. And the seat's own random-walk warning fires on one panel, where the author states that at low mutation supply the population is monomorphic and performs a random walk sampling the network uniformly. The defensible D3 panel is the one with genuinely polymorphic dynamics. It is not D4 because the acquisition experiment uses single-lineage random walks, a different unit of analysis from the populations in the longitudinal figure, so the measure and the outcome are never joined.

**Wagner and Altenberg 1996 is not purely conceptual.** Figure 3 plots mutational variance of a quantitative character against time in an evolving population over roughly 4000 generations. Mutational variance is a scalar second moment of the offspring phenotype distribution, tracked longitudinally at population level. The figure caption even places the accessibility change and the adaptive outcome side by side, noting that variability changes much more slowly than the characters. But it presents that as a timescale contrast, not a prediction, it is one illustrative run of a single scalar, and it reports a model from a companion paper rather than new work.

---

## A definitional trap, now recorded so the seat cannot fall into it

Hu and Banzhaf use the word **accessibility**, and it is not this programme's meaning.

Theirs is defined as a sum over inbound transition frequencies to a phenotype: high when a phenotype is easy to reach *from anywhere*. It is **inbound, phenotype-indexed and landscape-global**. This programme's ladder concerns an **outbound, individual-indexed, local** quantity: what is reachable *from here*.

The mechanical consequence is decisive. A quantity indexed by phenotype rather than by individual **cannot be carried on a population through time**, which is the structural reason their line never reaches D3 or above except once, and that once measures a robustness proxy instead. In their vocabulary, the programme's quantity maps onto *genotypic evolvability* and *variability*, not onto their *accessibility*.

Any future retrieval that matches on the word alone will mis-classify this entire body of work.

---

## Near-misses worth keeping

- **Hu et al. EuroGP 2011** predicts acquisition time from accessibility with a power law at R² = 0.99. From a static enumeration with a single unselected walker, so it is D2 with an outcome, not D4.
- **Hu et al. GECCO 2009** makes an explicitly D4-shaped claim, that settling into a neutral network's centre slows later phenotypic variation, in runs where variability is **never measured**. It is asserted from activity data.
- **Cowperthwaite et al. 2008** computes a static enumerated accessibility statistic, then runs 20 replicate populations for a million generations and correlates the two. Not D4, because accessibility is never re-measured on the evolving populations, but it is the closest structural template for what a genuine D4 would look like.
- **Toussaint and Igel CEC 2002** is arguably the best-designed accessibility perturbation in the corpus, tracking a population-averaged quantity over 10,000 generations with a fixed-parameter ablation. It fails D4 on its **outcome variable**, not its design: on a unimodal sphere there is no "what" that gets acquired, only "how fast".

---

## Two unread papers that could still overturn the hypothesis

Both were behind publisher blocks and are abstract-only, therefore `UNVERIFIED`. These are the highest-value unread items in the programme.

- **Draghi & Wagner 2008**, "Evolution of evolvability in a developmental model", *Evolution* 62(2):301-315. The abstract states that mutant genotypes with higher evolvability are more likely to increase to fixation. That is an evolvability quantity attached to genotypes inside an evolving population and tied to a subsequent outcome. **D4-shaped on its face.**
- **Draghi & Wagner 2009**, "The evolutionary dynamics of evolvability in a gene network model", *J Evol Biol* 22(3):599-611. The abstract speaks of quantifying the evolutionary forces responsible for **changes in** evolvability. Longitudinal language.

Also unresolved: the supplementary information of Draghi et al. 2010, section 6, the one remaining place a longitudinal accessibility measurement on their evolving populations could be hiding. And Hordijk and Stadler amplitude spectra, not accessed, no D-claim made.

**GATE-2 therefore does not open.** The six named candidates are cleared, but the honest position is that the strongest remaining threat to the residual hypothesis is now identified rather than eliminated. Clearing these two is cheap and must precede any historical-blindness claim.

---

## A self-caught error in the seat's own brief

Two paper titles the seat supplied as Hu and Banzhaf works appear in neither author's bibliographic record. They were `MODEL_RECALL_UNVERIFIED` citations that survived into a research brief because briefs were not being held to the same evidence standard as registry rows.

**Corrective rule, effective now:** citations inside briefs and handoffs carry the same evidence tier as registry rows. A brief that sends an agent hunting for a paper that does not exist wastes the budget that the real question needed.

---

## Effect on the registries

`Q_DETECTOR_PARTS_REGISTRY.md` gains D-level assignments for det-part-05 through det-part-07, and its provisional guess that Bedau-Packard activity statistics sit at D0 on the accessibility axis is **confirmed** by direct reading of both the 1992 and 1998 papers, including the incrementation function, which is literally existence.

The standing bet recorded in Q was: plenty of D1 and D2, possibly more D3 than expected, very little clean D4 or D5. **First survey scores that bet as correct on all three clauses**, with the caveat that a single survey of eight self-nominated candidates is not a base rate over the field.
