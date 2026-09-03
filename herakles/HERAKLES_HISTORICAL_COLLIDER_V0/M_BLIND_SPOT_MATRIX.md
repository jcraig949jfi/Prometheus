# M. BLIND-SPOT MATRIX

Signals the historical instruments were incapable of seeing. Rows are phenomena from directive §1; columns are the eight §17 questions. Filled provisionally for three families. **Amended 2026-09-03 after primary-source verification: read the AMENDED section before using anything here.** Detector-capability entries remain `MODEL_RECALL_UNVERIFIED` except where the amendment cites a source.

Codes: `Y` yes · `N` no · `P` partial · `?` unknown. Information gain: `HI/MED/LO`.

---

## fam-124 — EvCA density classification (GA-evolved CA)

| phenomenon | observable then | recorded | preserved | reconstructable | SFE-detectable | causal test possible | modern replication | info gain |
|---|---|---|---|---|---|---|---|---|
| mutation changing future distribution of useful mutations | N | N | N | Y | Y | Y | Y | HI |
| structure making later structures easier to acquire | P | N | N | Y | Y | Y | Y | HI |
| neutral precursor later necessary | N | N | N | Y | Y | Y | Y | HI |
| representation change (block-expanding → particle) | Y (by hand) | P | P (published rules) | Y | Y | Y | Y | MED |
| historical contingency | P | N | N | Y | Y | Y (mass replay) | Y | HI |
| reachable-region change | N | N | N | Y | Y | Y | Y | HI |
| new failure modes before capability change | N | N | N | Y | Y | Y | Y | MED |
| acquisition cost of the next capability | P (gen of first appearance) | P | P | Y | Y | Y | Y | MED |

**Verdict:** historical silence on six of eight rows is **detector blindness**, not absence. The instrument retained elites and hand-analysed a few rules; it could not have seen a change in the descendant mutation distribution even if one occurred.

**Verified 2026-09-03, and it cuts both ways.** Two of these rows are now sourced rather than guessed, and both were *self-reported by the original authors*: they documented that their biased initial-condition sampling *"turns out to impede the GA in later generations"*, and they identified the 0.02 noise floor of the fitness measure as the impediment preventing resolution of GKL-quality rules. So this detector was not naively blind. Its designers diagnosed two of its own limits in print and could not afford to fix them. That is a better description of the historical situation than "blindness", and the seat should use it.

---

## fam-051 — Lindgren IPD with memory-length genomes

| phenomenon | observable then | recorded | preserved | reconstructable | SFE-detectable | causal test possible | modern replication | info gain |
|---|---|---|---|---|---|---|---|---|
| duplication followed by divergence | Y | P (visible in frequency plots) | P | Y | Y | Y | Y | HI |
| neutral precursor later necessary | P | N | N | Y | Y | Y (no-duplication arm) | Y | HI |
| persistent internal state emerging | Y | Y | P | Y | Y | Y | Y | MED |
| altered mutation tolerance | N | N | N | Y | Y | Y | Y | HI |
| historical contingency across runs | N (1-10 runs) | N | N | Y | Y | Y | Y | HI |
| ecological interaction altering evolvability | P | P | P | Y | Y | Y | Y | MED |

**Verdict:** the phenomenon of interest (duplication changing accessibility) was **structurally invisible**: the published output is strategy frequency over time, which cannot express a statement about the descendant mutation-effect distribution.

---

## fam-013a — Avida EQU (2003)

| phenomenon | observable then | recorded | preserved | reconstructable | SFE-detectable | causal test possible | modern replication | info gain |
|---|---|---|---|---|---|---|---|---|
| deleterious precursor later necessary | Y | Y | Y (line of descent) | Y | Y | Y (done: reversion) | Y | LO |
| stepping-stone dependency | Y | Y | Y | Y | Y | Y (done: reward ablation) | Y | LO |
| **base rate of the same precursor leading nowhere** | N | N | N | Y | Y | Y | Y | **HI** |
| population-wide neutral occupancy | P | P | ? | Y | Y | Y | Y | MED |
| altered mutation tolerance | N | N | N | Y | Y | Y | Y | MED |

**Verdict:** the original detector was **good on the successful lineage and blind on the population**. The single high-gain row is the false-positive base rate: how often the same deleterious intermediate arose and produced nothing. Without it, "stepping stone" is a survivorship description.

---

## AMENDED 2026-09-03 AFTER PRIMARY-SOURCE VERIFICATION -- THE HYPOTHESIS BELOW IS PARTLY DEAD

The V0 version of this section claimed that historical instruments measured state and almost never measured change in what is reachable, and offered it as the seat's opening thesis. **A research pass found two counterexamples, both unanimous at 3-0, and both were on the seat's own list of places to look.** The section is amended rather than deleted, so the record shows what was claimed and what killed it.

**Altenberg 1994** (`dynamics.org/Altenberg/FILES/LeeEEGP.pdf`) formalises evolvability as a property of the offspring distribution, via Price's theorem, and Theorem 4 gives a rate law for its *change*: evolvability increases at a rate proportional to the variance in constructional fitnesses of a program's blocks. That is a reachability-change formalism from thirty-two years ago, and it couples structural duplication to evolvability change directly.

**Mengistu, Lehman and Clune 2016** (GECCO 2016 pp.141-148) make the offspring-effect distribution the fitness function itself, and run an explicit transfer test measuring the fraction of an unseen 450x450 environment an organism's offspring cloud reaches, beating novelty and objective search at p<0.001. The measure is **inherited, not invented**: Lehman and Stanley 2013 already enumerated genomes reachable by all single-connection mutations, with precedent cited to 2011 and to Reisinger and Miikkulainen 2006.

### What survives

Only this, and it must be quoted with its qualifiers:

> The formalism for reachability change was available from 1994 and neighbourhood-diversity measurement from 2011 or earlier, but population-wide measurement of reachability change **over a lineage** was not performed in the specimens profiled here.

Two things keep even that alive, both fragile:
- the 2016 statistic is a scalar count at a threshold, a **snapshot** of neighbourhood size at a point, not a lineage-level measure of change;
- Altenberg wrote that his quantity *"should be possible to measure in GP runs"* and reported no such measurement, so in that chapter the concept exists and the measurement does not.

### The honest prior going forward

Of the eight candidates the seat itself nominated as likely counterexamples, only two were checked, and **both were genuine counterexamples**. A 2/2 hit rate on a self-selected list is weak evidence about a base rate, but it points one way. Six remain unchecked: Wagner and Altenberg 1996; Hu and Banzhaf on accessibility in linear genetic programming; Dolson and Ofria's MODES toolbox; Toussaint on neutral traits shaping the exploration distribution; Andreas Wagner; Draghi; Hordijk and Stadler on landscape accessibility; and Bedau-Packard evolutionary activity. **The residue above may not be quoted anywhere until those six are cleared.**

This claim is also time-sensitive in a way the specimen facts are not. The evolvability-measurement literature is active, so any "nobody has measured this" statement decays continuously and needs a date stamp whenever it is used.

---

## The original V0 claim, retained for the record

The three families filled below are blind on the same four rows:

1. change in the descendant mutation-effect distribution;
2. base rate of a precursor that led nowhere;
3. reachable-region change, as opposed to fitness change;
4. acquisition cost of the next capability.

The V0 inference was that the historical corpus is systematically missing the derivative, and that this would explain why forty years of work reads as "no open-endedness" while saying little about microscopic accessibility change.

**That inference over-reached.** What the three profiles actually support is the narrower statement that *these three experiments* did not record those four quantities, which is a fact about three detectors and not about the field. Extending it to the field was the error, and it is exactly the confirmation shape the seat declared as a conflict of interest in its own review packet.
