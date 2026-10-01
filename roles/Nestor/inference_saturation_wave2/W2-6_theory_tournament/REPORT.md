# W2-6: theory tournament on the seven NPE theories (directive item F)

> Saved by Nestor from the worker's returned text; the harness blocks report-file writes by subagents.
> - The 13 scripts and their outputs (C1–C9) are in this folder.
> - About 8 CPU-min in total; read-only JSON plus single world interactions.
> - The C7c and C8 map-built processes are illustrative only. They are not `world.Runner`.
> - No world runs and no git writes.

## Summary
1. **Only T4 has real rivals.**
   - Of the 21 pairs: 6 RIVAL, 7 NESTED, 8 ORTHOGONAL.
   - Every RIVAL pair involves T4, except T1–T2.
   - T1–T2 dissolves into a choice of **counting unit** (C5b). Per copy event, state-free variants are 6x more common under noisy registers (T2's reading, p = 6e-4). Per interaction attempt they are not (T1's reading), because a conversion in a noisy context is itself a sieve.
2. **One theory, F (the "supplied rewrite field"), absorbs six.** T1, T2, T3, T5, T6 and T7 become its levels:
   - content: T3;
   - rules: T2 and T5;
   - dynamics: T7 as the branching limit, T1 as the mutation kernel, inside an *iterated* T6.
3. **T4 is eliminated as a theory.** It loses every contest the existing data decide:
   - (c) epistasis: S3, re-read by stratum (C1);
   - (b) convergent mechanism: 15 classes across 26 independent runs (C4). This is provisional, because it uses the W1/FOR panel, not C-A3 origins;
   - founding-stage kin benefit: lost to T7.

   **T4(a)** (a home/kin advantage beyond the iterated map) survives as an untested residual hypothesis **R**.
4. **The revival attack reopened T4(c′), generic evolved epistasis.**
   - Evolved copiers have 3.7% fully-dispensable synthetic-lethal pairs; planted minimal copiers have 0.45%.
   - But 2 never-evolved random-hit competent genomes show 5.1%.
   - So it may just be executed-chain length. The static test costs about 25 CPU-min.
5. **Erosion under BASE is the iterated map.**
   - Founder conversion decays 0.46 → 0.01 over 9 interactions under BASE, and stays at about 0.44 under ATOMIC.
   - A map-built process reproduces ATOMIC establishment (0.55 vs 0.52 observed).
   - It overpredicts BASE about 6x (0.18 vs 0.03).
6. **E2 as designed would "kill T1" from its counting unit alone.** Count per interaction attempt, or drop it.
7. **Transience does not strain T2.**
   - Three events are low-copy flickers that never exceeded 11 copies. One is a collapse of the whole competent pool.
   - No event lost a swept trait while its competent pool persisted.
   - Borderline STATE_FREE calls flip on re-tag, so some of the 8 C-A3 events may be assay artefacts.
8. **The C7-vs-CF cell axis is at the noise floor.** The code-inert structure factor shows an effect as large as representation (C9).
9. **Undecided contests, by information per cost:**
   - U1: generic epistasis vs chain length;
   - U3: F's calibration;
   - U2: C-A3 event repeatability;
   - U6: the S2 execution audit;
   - U5: E4 genealogy;
   - U4: E1 HOME.

## 1. The 21 pairs

Classes:
- **RIVAL:** contradictory claims about the same observable.
- **NESTED:** one theory is a component or limit of the other.
- **ORTHOGONAL:** different levels, compatible.
- **EQUIVALENT:** identical predictions.

| # | pair | class | verdict / note |
|---|---|---|---|
| 1 | T1–T2 | RIVAL on appearance → dissolved (C5b) | Per conversion: Z 1.24% vs R 7.2% (p 6e-4). Per attempt: Z 1.05% vs R 0.56%. Random context cuts conversions 10x, and the survivors are enriched for state-independent copies. E2 must count per attempt. |
| 2 | T1–T3 | NESTED | T3 is T1's density term. |
| 3 | T1–T4 | RIVAL, T4(b) | **For T1, provisional** (C4): state-free genomes fall into 15 classes in 26 runs; P(two runs share a class) = 0.05. E4 Q2 on C-A3 origins decides it. |
| 4 | T1–T5 | ORTHOGONAL | |
| 5 | T1–T6 | NESTED: T1 is the mutation kernel | The cell-axis rival clause is void (C8, C9). |
| 6 | T1–T7 | ORTHOGONAL | |
| 7 | T2–T3 | ORTHOGONAL | E6's phase dose makes the same prediction under both (S1: real donors reload pointers). |
| 8 | T2–T4 | RIVAL | **Undecided.** E1 HOME decides it. |
| 9 | T2–T5 | ORTHOGONAL | |
| 10 | T2–T6 | NESTED: T2 names the parts of Φ/W that are supplied | The migration route is inert in code (C9). |
| 11 | T2–T7 | ORTHOGONAL; transience clause dissolved (C3) | 3 events swept and persist; 1 swept, then the whole competent pool vanished; 3 are low-copy flickers (max 1, 1, 11), which T2 with s ≈ 0.044/epoch loses with joint P 0.31; 1 is intermediate. |
| 12 | T3–T4 | RIVAL on (a), (b), (c) | **(c) for T3.** S3 frozen: T4(c) DEAD. C1 stratum-matched: SF = SD (1.01, CI 0.68–1.50); the 16000006 cluster has *fewer* lethal pairs (2.4% vs 4.0%, p 0.057). (b) for T3/T1, provisional. **(a) undecided. (c′) open** (C2). |
| 13 | T3–T5 | ORTHOGONAL | |
| 14 | T3–T6 | NESTED, near-equivalent | S1b passes at the first-donor stage. |
| 15 | T3–T7 | ORTHOGONAL | |
| 16 | T4–T5 | ORTHOGONAL | Kin overwrites rarely register (C5c: 52 conversions in 1,620 state-dependent kin trials). |
| 17 | T4–T6 | RIVAL | **Undecided** where T4 speaks. F's misses are *over*predictions, whereas T4(a) predicts the opposite sign. |
| 18 | T4–T7 | RIVAL | **For T7 at founding** (X-DOSE-CURVE LRT p 0.42; joint p 0.108; U-W5 shows no Allee effect). Post-takeover: undecided. |
| 19 | T5–T6 | NESTED: Φ contains partner execution | The "beyond Φ" clause is undecided and low priority. S2 decides it. |
| 20 | T5–T7 | NESTED | The hijack is part of T7's early death term. C7: 7ae3 is overwritten in 0.197 of single interactions (random side) against an epoch-1 loss of 0.28, so about 70% is supplied. |
| 21 | T6–T7 | NESTED | Erosion is the iterated Φ under BASE (C7b). The 6x BASE gap is unexplained by both. |

## 2. Checks

| check | what it measured | result |
|---|---|---|
| C1 | S3 re-read by stratum | Null-0 stratum: SF 131/3,495 vs SD 101/2,722 (ratio 1.01). The 0/3+1/3 stratum: SF < SD (0.70, p 0.001). 16000006 e700 2.35% vs other SF 4.03%. |
| C2 | S3 pipeline on 15 never-evolved competent genomes | Planted minimal motifs 0.45% (5/1,107). Random-hit competent genomes 5.1% (7/136, n = 2). Evolved genomes 3.7%. |
| C3 | the transience classification | See row 11. |
| C4 | address-source mechanism classes | State-free: 15 classes in 26 runs, all side-0. State-dependent: 22 classes in 60 runs, 20 of them side-1. |
| C5 / C5b | variant production by donor context | Most forward hits come from **borderline parents** with max(R1, R2) ≥ 0.3. The STATE_FREE call is seeded by the genome hex, so a one-byte change re-draws the seeds. This is assay repeatability, now measured on real children. Reverse loss is about 15% per conversion, mostly loss of competence. |
| C5c | kin partners | Conversions nearly vanish (SD 52/1,620; SF 2/840). A near-copy victim fails the predecessor test, and ATOMIC discards the write. So in a converged family few births register, and variation comes mostly from point mutation. |
| C7 / C7b | X-TICKET cell, BASE vs ATOMIC | Step-1 conversion 0.453 and overwrite 0.197 under both. Under BASE the founder changes about 8 bytes per interaction, and conversion decays from 0.46 to 0.01 over 9 interactions. |
| C7c | map-built branching (illustrative) | ATOMIC 0.55; BASE 0.175. |
| C8 | iterated map, cell axis | 16 BRIDGE donors × 10 lineages: C7 0.44 and CF 0.39, against observed 0.125 and 0.44. |
| C9 | BRIDGE as a factorial | PERSIST: structure (code-inert) 24/64 vs 13/64 (p 0.05); representation 23/64 vs 14/64 (p 0.12); CF vs C7 14/32 vs 4/32 (p 0.011). |

## 3. The collapse

| step | grounds |
|---|---|
| T3 ⊂ T6 | T3's unique prediction (map-matched twins perform alike) is T6's. |
| T2 ⊂ T6 | Every scaffold function is part of Φ or W; migration is inert. |
| T5 ⊂ T6 | Partner execution is part of Φ. |
| T7 ⊂ T6 | Erosion arises from iterated Φ under BASE, and the map-built branching reproduces ATOMIC. |
| T1 ⊂ T6 | T1 is the mutation kernel and rare-transition rate. |
| T1 ≡ T2 on appearance | They differ only in the counting unit. |

**F, the supplied rewrite field.** The fate of any content is computable from the *iterated* single-interaction map (Φ under W, with the mutation kernel) against the realized partner distribution, with **no lineage-level term**. It has three levels:
- **content (T3):** a supplied half-duplicator plus an incidental operand chain; state-free variants differ in source and side; mechanisms are diverse;
- **rules (T2, T5):** supplied W and placement, HL = 0, the victim-register newborn, entry noise as demand, and partner execution;
- **dynamics (T7, T1):** a branching process with a step-dependent offspring law (erosion under BASE); rare transitions = kernel × registered births (rare after takeover); selection acts first at birth (the sieve), then on occupancy.

**R = T4(a)**, untested, is the only claim that would make the alteration stage irreducible to F.

**F's open anomalies:**
- BASE overpredicted about 6x;
- C7 under carried registers overpredicted (0.44 vs 0.125);
- the foreign magnet;
- the 16000006 path;
- 27000053;
- the k = 4 excess.

None of these favours R: they are deficits, not home advantages.

## 4. Adversarial loop

- **A1. "F is just the simulation."** Answer: F is restricted to "no lineage term". That makes predictions that can fail, and two quantitative misses are listed openly.
- **A2. "C8 fails, so T6 should be eliminated."** Answer: the contrast it fails on is noise (C9). F is a good *ordinal* theory and a poor *calibrated* one.
- **A3. "The T1 ≡ T2 merge uses random partners, but internalization is post-takeover against kin."** Answer: true; the kin regime differs (C5c). The merge is about units. Which factor dominates in a regime is a parameter of F.

**Revival case for T4.** Each point, with its rebuttal:
- (1) Pairwise knockouts do reveal synthetic lethality (3.7% vs 0.45% planted). Rebuttal: random-hit unevolved genomes show 5.1%, consistent with chain length. Reopened as T4(c′).
- (2) The 16000006 walk. Rebuttal: n = 1, and it has *less* pairwise organization.
- (3) F overpredicts. Rebuttal: that is the wrong sign for T4(a).
- (4) C4 is not on C-A3 origins. Rebuttal: granted; it is provisional.

**Third round.** "This is burden-shifting." Answer: the collapse rests on nesting shown in data. The tournament also weakened F.

## 5. Surviving undecided contests, by information per cost

| rank | contest | cheapest decisive step | cost |
|---|---|---|---|
| U1 | T4(c′) generic evolved epistasis vs chain length | S3 on about 20 random-hit competent genomes; regress the null-0 lethal rate on executed pre-copy length, evolved vs unevolved | about 25 CPU-min, static |
| U3 | F's calibration | Re-run C7c/C8 with the in-world ruler, partners drawn from the evolving lineage, and the realized horizon | about 10–20 CPU-min |
| U2 | C-A3 event repeatability | Static flip-rate proxy now; decisive within E4 | about 5 CPU-min |
| U6 | T5's "beyond Φ" clause | S2 EXEC-motif audit | ≤ 1 core-h |
| U5 | T4(b) on real C-A3 origins | E4 Q2 | about 6 core-h |
| U4 | R = T4(a) | E1 HOME | about 14 core-h + E4 |

Do not run E2 as designed. Drop the cell axis as a theory target.

## 6. Ledger entry (W2-6)

- **Result:**
  - 6 RIVAL, 7 NESTED, 8 ORTHOGONAL pairs.
  - F absorbs six theories.
  - T4 is eliminated; R = T4(a) and T4(c′) remain open.
  - E2's ruler decides by its unit.
  - Some C-A3 events are flickers.
  - The cell axis is noise.
  - Erosion is iterated Φ.
- **Confidence:**
  - pair classes: medium-high;
  - T4(c) dead as specified: high;
  - T4(b) against: low-medium;
  - T1 ≡ T2 by unit: medium;
  - erosion: high for direction, low for magnitude;
  - cell axis as noise: medium.
- **Strongest objection:** F overpredicts 2–6x and "wins" partly by absorbing its rivals. A population-level term could be hiding in that gap.
- **Next:** U1, U3, U2, E2 re-specification, and the X-TICKET epoch-1 residual (0.28 vs 0.20).
