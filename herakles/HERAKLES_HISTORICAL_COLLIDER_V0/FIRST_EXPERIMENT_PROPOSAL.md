# THE FIRST ARCHAEOLOGICAL EXPERIMENT — recommendation

**Recommended specimen: `spec-evca-density` — GA-evolved one-dimensional cellular automata for density classification (EvCA, Santa Fe Institute, 1993-1999; Mitchell, Crutchfield, Das, Hraber, Hordijk).**

Status: recommendation STANDS, and is now primary-sourced. **Updated 2026-09-03 after a verification pass.** Nothing has been run and no code or data recovered, but the papers have been read and the parameters confirmed. See `RESEARCH_PASS_2026-09-03.md`.

> **THE ONE CHANGE THAT MATTERS: target the PPSN III configuration, not the Physica D one.**
> The Physica D 1994 experiment ran 50 runs and produced **zero** particle-based strategies; the word "particle" does not occur in its results text. The separate PPSN III experiment ran 300 runs and found particle-based computation on exactly **7 (2.3%)**. V0 conflated the two. A reconstruction aimed at the Physica D setup would have targeted a configuration in which the phenomenon of interest never occurred, and would have burned the first experiment.

---

## Why this one, against the §28 preferences

| §28 preference | EvCA | Runner-up: Lindgren IPD | Runner-up: RNA relay |
|---|---|---|---|
| small physics | 128-bit rule table, 149-cell ring, ~300 steps. Smaller than almost anything else in the registry | smaller still | small but needs a folding library |
| surviving source | rule tables published in hex (digits UNVERIFIED); code survival UNRESOLVED, both directions | believed none | ViennaRNA survives, era parameters may not |
| surviving experimental description | **VERIFIED complete**: every GA parameter, lattice size and IC distribution in print | ECAL93 verified; 1991 model not yet obtained | protocol published |
| known lineage phenomenon | epochs of innovation; rare transition to particle-based strategies | duplication then divergence | relay series (explicitly a lineage) |
| affordable massive replication | 1e4-1e5 runs per CPU-day | even cheaper | cheap |
| meaningful detector blindness | six of eight rows blind, but the authors **diagnosed two of their own limits in print** | six of six blind | **weak: the original detector was good** |
| causal counterfactual opportunity | mass replay from pre-epoch checkpoints; rule-bit ablation | no-duplication arm | position-pinning control |

EvCA wins on the combination of published artifacts to check a reconstruction against, and blindness on exactly the rows Prometheus cares about. **Verification strengthened the first half and weakened the second**: the specification is complete enough for a faithful rebuild, but the original team was less blind than assumed. Lindgren is cheaper and has the cleaner mechanism but no artifact to validate the rebuild. RNA is deliberately kept as runner-up because its strong original detector makes it the best place to discover that we add nothing.

**Anti-fame check (§18):** this is not the famous choice. Tierra and Avida are more cited. EvCA is chosen because its physics fits in a page and its interesting event is rare and seed-dependent, which is precisely what 1e4 replicates converts from anecdote to distribution.

---

## The three-stage shape (§19)

**Stage 1 — faithful physics, observation only.** Reimplement the GA and the CA exactly as specified, **targeting the PPSN III configuration** (the Physica D configuration produced zero particle strategies in 50 runs). Pin seeds. Run 1e4 times. Single question: *does the transition to particle-based strategies recur, and at what rate with a confidence interval?* Compare against the originally reported rate. If the reconstruction cannot reproduce the original's reported outcome distribution, stop and report a reconstruction failure. That is a valid and useful ending.

**Stage 2 — add resolution, do not touch physics.** Emit into SFE: every genome every generation (not just elites), full lineage DAG, per-initial-condition failure classes, neutral-variant occupancy around the elite, first-divergence points between forks, content-addressed rule tables.

**Stage 3 — the question they could not afford.** Mass replay: fork 1e3 times from the generation immediately preceding each detected transition, and 1e3 times from a fitness-matched control generation with no subsequent transition. Measure the conditional probability of transition from each. Then ablate individual rule-table bits of the pre-transition elite and measure which ones the transition required.

**The Stage 3 question in one sentence:** was the pre-transition rule table *already special* in a way that changed what was reachable, or was the transition a coin flip that happened to land?

That question is answerable now for a few CPU-days and was economically impossible in 1996. It is also exactly the §1 primary question, instantiated on real historical physics.

---

## Verified physics (PRIMARY_SOURCE_READ, 3-0 unanimous)

From Mitchell, Crutchfield and Hraber, *Physica D* 75 (1994) 361-391, and Das, Mitchell and Crutchfield, PPSN III 1994 pp.344-353, both read as author-hosted PDFs.

k=2, r=3, periodic boundaries. Rule-table chromosome 2^(2r+1)=128 bits over a 2^128 space. Lattice N=149. Population P=100. Elite E=20, generation gap 0.8, top 20% copied unmodified. Remaining offspring by single-point crossover between elite parents chosen **with replacement**. Exactly m=2 point mutations per offspring. I=100 initial conditions per evaluation, **regenerated fresh every generation, including for the elite**. Relaxation time drawn per simulation from a Poisson with mean 320. Generations: 100 in Physica D, 50 (100 in some runs) in PPSN III.

**Two confounds the reconstruction must carry, both self-reported by the original authors.**

1. Initial conditions are sampled uniformly over density in [0,1], half either side of the critical density, **not** unbiased binomial. The authors write that this *"turns out to impede the GA in later generations because, as increasingly fitter rules are evolved, the IC sample becomes less and less challenging"*. The initial population is likewise seeded uniformly over the fraction of 1s, not per bit.
2. The fitness measure has a noise floor of about 0.02 standard deviation, which the authors identify as the impediment preventing the GA from resolving GKL-quality rules.

Both push **against** finding late-run innovation, which is the direction-of-confound question the seat is required to ask before reading any null.

---

## Pre-registered outcomes, now quantitative

Original rate: 7/300 = 0.0233. Wilson 95% interval **[0.0113, 0.0474]**; normal-approximation SE 0.0087.

| Replication | Expected transitions | SE | 95% half-width |
|---|---|---|---|
| n = 1,000 | 23 | 0.0048 | 0.0094 |
| n = 10,000 | 233 | 0.0015 | 0.0030 |

- **HISTORICAL_PHENOMENON_RECURS**, reconstruction rate falls inside [0.0113, 0.0474], the Wilson interval of the original.
- **RECONSTRUCTION_FAILS**, it does not. Name the responsible unspecified parameter. At n=10^4 our interval is about fifteen times tighter than the historical one, so this is a sharp call rather than a judgement.
- **CONTINGENT**, replay from pre-transition checkpoints exceeds fitness-matched controls by more than the gate below.
- **NOT_CONTINGENT**, the two replay sets are indistinguishable. `bump-evca-transition` dies.
- **NO_PARTICLE_STRATEGIES**, zero transitions in 10^4 runs. Under the original rate that has probability of order e^-233, so it would be decisive evidence of a reconstruction defect rather than of a failed replication.

### The CONTINGENT gate, computed in advance and shown reachable

Comparing conditional transition probability between forks from a pre-transition checkpoint and forks from a fitness-matched control generation, control rate taken as the base rate 0.023:

| Forks per arm | Minimum detectable precursor rate at 2 sigma | Enrichment required |
|---|---|---|
| 1,000 | 0.0381 | 1.7x |
| 3,000 | 0.0312 | 1.4x |

The attainable range of the difference is 0 to 1 and the gate sits 0.015 above control, so **the gate can fire on real inputs**. This closes the defect behind two earlier Prometheus failures, where one gate sat closer to the observed value than its own standard error and another sat above the maximum attainable value.

---

## The sixteen §25 answers

1. **What did the original researchers want to measure?** Whether a GA discovers CA rules that perform a global computation, and what computational strategy those rules embody.
2. **What did their experiment actually measure?** Best-of-generation fitness on sampled initial conditions, final rule tables, and hand computational-mechanics analysis of a few selected rules.
3. **What information did it discard?** Non-elite genomes, neutral variants, extinct lineages, per-initial-condition failures, seeds, and (believed) the trajectories of runs that never reached particle strategies.
4. **What phenomenon are we interested in that they were not measuring?** Whether the pre-transition rule table changed what was reachable, i.e. a change in the descendant search distribution rather than in fitness.
5. **What evidence suggests it may nevertheless have occurred?** **VERIFIED**: 7 of 300 runs, 2.3%, discovered particle-based computation while most runs settled into one of two block-expanding strategies; the papers' own phrase is "epochs of innovation ... each corresponding to the discovery of a new, fitter strategy". Rare, epochal and convergent across search physics is the signature a contingent precursor would leave. It is equally the signature of a low-probability mutation with no precursor at all, which is exactly what the replay test separates.
6. **What alternative mundane explanation exists?** The transition is a low-probability mutation with no precursor structure; epochs are drift; convergence across search methods reflects the task, not a reachability structure.
7. **Does original data survive?** Rule tables **are** published as hexadecimal in the 1996 review's Table 1, but a transcription of the digits failed adversarial verification 0-3, so the digits and the neighbourhood-ordering convention must be re-read from source. Run logs, populations and seeds: no evidence either way.
8. **Does source code survive?** **UNRESOLVED IN BOTH DIRECTIONS.** A claim that the project archive publishes no code, no rule tables and no run data was refuted 0-3, and no verifier found a positive location either. This must be re-run as a dedicated artifact hunt and must NOT be recorded as "no artifact survives". It matters less than V0 thought: the GA is fully specified in print, so a faithful REIMPLEMENTATION is available regardless.
9. **Can the physics be reconstructed?** Yes. The CA is unambiguous. The GA has parameters that may be underdetermined; each will be enumerated and given variants.
10. **What would SFE record that the original system did not?** Full population per generation, lineage DAG, neutral occupancy, per-initial-condition failure classes, fork divergence points, ablation results, content-addressed rule identity.
11. **What would 10,000x replication buy?** Transition rate with a CI instead of an anecdote; seed-versus-initialisation variance decomposition; the conditional probability of transition given ancestral structure; the false-positive rate of epoch-like fitness jumps with no strategy change.
12. **What counterfactual becomes possible now?** Blount-style mass replay from pre-transition checkpoints against fitness-matched controls.
13. **What ablation would most strongly test it?** Bit-level ablation of the pre-transition elite rule table, measuring which entries the subsequent transition required.
14. **Which recovered part does this specimen contain?** `part-particle-computation`, `part-epochal-innovation`; candidate presence of `part-neutral-drift-precursor`.
15. **What other historical part might compose with it?** `part-cross-context-transfer` (comp-05: do particle rules transfer to a second task?), and `part-innovation-protection` (would protection raise the transition rate?).
16. **What observation would kill our interest immediately?** Replay from pre-transition checkpoints is statistically indistinguishable from fitness-matched controls. The precursor is then not special, and the specimen drops out of the programme.

---

## What must happen before any code is written

1. ~~Read the primary sources and fix the GA parameters, IC distribution, run count and transition rate.~~ **DONE 2026-09-03.**
2. ~~Compute the SE and attainable range for the CONTINGENT gate.~~ **DONE 2026-09-03.**
3. **Re-read the hex rule tables** from the 1996 review Table 1, pinning the neighbourhood-ordering convention. These are the validation target for the rebuild, and the transcription in circulation failed verification.
4. **Run the dedicated EvCA artifact hunt** (SFI archive, author pages, GitHub migrations, Internet Archive snapshots). Hash anything recovered into manifest J. A documented "not found after searching X, Y, Z" is an acceptable and useful outcome; "no artifact survives" is not, because it was refuted.
5. Write the physics sheet enumerating every remaining unspecified parameter, with variants for each; fix the provenance class at REIMPLEMENTATION.
6. Send the SFE world proposal to Daedalus, and this pre-registration to Elenchus for an independent failure mode.

## A standing warning about this specimen

The seat chose EvCA partly because it believed the original detector was blind. The verification pass showed the original authors **diagnosed two of their own instrument's limits in print** and could not afford to fix them. That is a better and less flattering description of the historical situation, and it changes what a success here would mean: not "we saw what they could not conceive of", but "we bought the measurement they specified and could not afford". The second claim is smaller, defensible, and still worth the CPU-day.
