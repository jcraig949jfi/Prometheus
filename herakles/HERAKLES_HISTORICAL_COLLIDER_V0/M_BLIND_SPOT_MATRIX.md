# M. BLIND-SPOT MATRIX

Signals the historical instruments were incapable of seeing. Rows are phenomena from directive §1; columns are the eight §17 questions. Filled provisionally for three families; all entries `MODEL_RECALL_UNVERIFIED`.

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

## The general shape of historical blindness (hypothesis, to be tested by filling more families)

Across the three families filled, the same four rows are blind everywhere:

1. change in the descendant mutation-effect distribution;
2. base rate of a precursor that led nowhere;
3. reachable-region change (as opposed to fitness change);
4. acquisition cost of the *next* capability.

If that pattern holds across 20+ families, it is itself a finding: the historical corpus is not merely under-replicated, it is systematically missing the derivative. Every instrument measured *state* (fitness, complexity, diversity); almost none measured *change in what is reachable from here*. That would explain why forty years of work reads as "no open-endedness" while saying almost nothing about whether microscopic accessibility changes occurred.

**This hypothesis is currently supported by three hand-filled families written from recall. It is a lead, not a finding.**
