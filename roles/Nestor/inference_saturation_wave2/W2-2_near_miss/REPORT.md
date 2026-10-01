# W2-2 near-miss science: do successful lineages differ qualitatively before the threshold?

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes
> by subagents.
> - Scripts and JSON are in this folder (a1–a7, h1, h2).
> - Boundaries: read-only outside this folder; no git writes; no world or evolution runs.
> - New numbers come from committed JSON or from single `world._pair_interact` calls in the specimen's own frozen cell,
>   about 6 CPU-min.

## Answer first

**1. Under BASE write-back (7ae3, X-TICKET physics), the "near-misses" are ordinary draws from one subcritical law.**
- This covers the bursts and the "WIN, depth 5–19" class.
- The individual law, built from single interactions:
  - P-11-certified births per individual per lifetime: m_c = 0.77;
  - all accepted births: m = 0.93;
  - 93% of births happen at age ≤ 6;
  - parent–offspring heritability of fecundity: ρ = 0.02.
- It reproduces X-TICKET's lineage sizes:

  | lineage size | predicted | observed |
  |---|---|---|
  | 0 | 0.57 | 0.54 |
  | 1–4 | 0.28 | 0.29 |
  | 5–26 | 0.13 | 0.14 |

**Runaways are not the tail of that law.**
- Predicted 0.03%, observed 4/128 = 3.1% (P ≈ 9e-8).
- Intermediates (27–162 births): predicted 2.4%, observed 1 vs 7.7 expected over 320 runs (P = 0.004).

So BASE has a **qualitatively different second regime**. Nothing on disk distinguishes it before epoch 10:
- demography up to epoch 10 is uninformative (runaway seed 35 had N10 = 4, B10 = 6);
- the founder genome is identical in every run;
- there is no common heritable variant;
- child fertility does not separate runaways from bursts;
- a lineage-written partner pool does not help (m_c 0.74 vs 0.77).

**2. Under ATOMIC the threshold is quantitative.**
- The same law is supercritical (m_c 2.2, m 2.6).
- It predicts all-or-nothing outcomes with no intermediates.
- It predicts escape at 0.43–0.50, vs 0.575 observed.

**3. Several named near-misses are ruler or horizon artifacts (§4).**

**Early warning.** Births continuing in epochs 11–15 is the best early warning. It reports the crossing itself, about 80 epochs ahead of depth 20.

## Candidate precursor signatures (128 X-TICKET runs: 4 runaways, 124 others)

| candidate | observation | verdict |
|---|---|---|
| **C1** Early size | B5 ≥ 4: hit 4/4, FA 17/124. B10 ≥ 16: 2/4, 2/124. Partly tautological, because depth ≥ 5 needs ≥ 5 births. | Quantitative, necessary-ish filter only |
| **C2** Persistence of per-capita fecundity | See the table after this one. Any birth in epochs 11–15: 4/4 hit, 3/124 FA. ≥ 3 births in epochs 11–15: 4/4, 0/124. | **The best available observable.** It is the crossing as it happens, not a precursor |
| **C3** Label leakage | 1/4 hit | Weak |
| **C4** Child fertility at birth | Ordering reverses between g = 1 and g = 0 | Not usable |
| **C5** Heritable fecund variants | See the notes after this table | BASE: common heritable variation ruled out (a rare switch at ≤ 0.3% per birth could be missed). ATOMIC: a post-threshold sweep, not a precursor |
| **C6** Partner-environment feedback | m_c: random 0.774 → 100% lineage-touched 0.737 → 25% touched 0.707. Survival to 60 epochs falls 0.60 → 0.28 | Rejected: touched partners kill lineage members more |
| **C7** Erosion dial | At f = 0, the 27–162 gap fills: 6/98 copiers vs 1/93 at f = 1 | Erosion acts on the bulk; runaway counts do not track it |
| **C8** Kin density | Not testable with single interactions | Unlikely switch: 2–12% kin pairing at 5–30 members |

**C2: per-capita fecundity by epoch window.**

| window (epochs) | WIN | runaway |
|---|---|---|
| 1–5 | 0.44 | 0.41 |
| 6–10 | 0.13 | 0.20 |
| 11–15 | 0 | 0.17–0.40 |

**C5 notes.**
- **BASE:** ρ = 0.02 over 1,167 pairs.
- **ATOMIC: byte 42 (`LD (BC),A`) variants.**
  - Fitness: 12.2 vs 2.0 births, and 51% vs 4% survival.
  - Frequency in the tree: 103/1,920; generation means rise from 2.0 to 3.9.
  - The founder byte at 42 is lost in 19/27 C-CORE runaways, after takeover (X-CORE-TIME).

## Bistability (a7)

Certified births, BASE:

| lineage size | predicted | observed |
|---|---|---|
| 0 | 0.568 | 0.539 |
| 1–4 | 0.278 | 0.289 |
| 5–26 | 0.130 | 0.141 |
| 27–162 | 0.024 | 0 |
| ≥ 163 | 0.0003 | 0.031 |

- An empty gap plus a 100x excess of runaways means a second regime. A fat tail would fill the gap first.
- ATOMIC is supercritical (founder m_c 1.76, descendants 2.30). It predicts 0.44–0.50 escape and < 0.001 intermediates.

## Near-misses as ruler artifacts (§4)

| case | reading | detail |
|---|---|---|
| X-TICKET "WIN 5–19" | **artifact of the depth ≥ 5 cut** | 20/138 burst lineages have depth ≥ 5; seed 126 has depth 7 with 4 founder births. anc0 at epoch 300: ≤ 28 vs 131–256. |
| World depth | **world ruler, not founder heredity** | 4/13 depth ≥ 20 runs have 0–2 founder births. |
| C-CORE depth 6/10/16 | **genuine losses** | anc0 0.004–0.063. Unexplained. |
| cb7f ATOMIC | **very probably takeover without depth** | Its own law: escape 0.95/0.88, founder survival 0.97, certified share 0.30 (vs 0.85 for 7ae3). Chain index 0.25–0.42 vs 2–23. E9 decides. |
| cb7f BASE | **genuine failure, predicted** | m 0.66, m_c 0.18. |
| C-A3 near-misses | **mostly artifacts** | 3 cut off by the horizon (7ae3 27000000, 27000061; ffa6 27000016). 1 replacement (ffa6 27000043). 2 competence-ruler collapses under an intact label (7ae3 27000008, 27000009: competent = 0 in 11/15 and 17/18 checkpoints while L = 1.0 or 0.7). |
| ffa6 27000053 | **the one genuine qualitative near-miss** | Slow creep (L 0.18 → 1.0 over 1,200 epochs) with ≤ 33 competent genomes (median 18), vs 105–185 in 6/8 events. |

## Early-warning observables (in-sample)

| id | observable | performance | caveat |
|---|---|---|---|
| EW-1 | ≥ 3 founder-lineage births in epochs 11–15 → runaway | 4/4 hit, 0/124 FA | X-TICKET |
| EW-1b | ≥ 2 births in one epoch within epochs 11–20 | 4/4, 0/124 | |
| EW-2 | B5 ≥ 4 | 4/4, 17/124 | screen only |
| EW-3 | lineage ≥ 20 at D0 + 20 epochs | 5/7, 0/41 | W1, post hoc |
| EW-4 | S1 ≤ 10 epochs | 196/199, 193/238 among copiers | necessary, not sufficient |
| EW-5 | GW escape from the single law | ATOMIC 0.43–0.50 vs 0.575. BASE 0.0003 vs 0.031 | fails exactly where the switch is |
| EW-6 | post-takeover competent count ≥ 50 → internalization | 6/8, 2/7 | confounded by cell |

## Preregistrable test W2-2-EW (specification only; not run)

**Question.** Is the runaway already in the genomes at epochs 5–15?

**Hypotheses.**
- **H_variant:** a runaway lineage has a member with m_c ≥ 1.2 by epoch 10, and burst lineages do not.
- **H_context:** members of both kinds have m_c ≤ 1, so the switch is in the world context.

**Sample.**
- 256 fresh X-TICKET seeds, run to epoch 300.
- Snapshots of every live causal-lineage member (genome + registers) at epochs 5, 10 and 15.
- About 8 runaways expected. If fewer than 4 occur, the result is INCONCLUSIVE.

**Static readout.** h1-law m_c per member: 20 lives × 60 interactions, about 20 CPU-min.

**Rules.**
- Primary: EW-1 out of sample. PASS if hit ≥ 0.75 and FA ≤ 0.03.
- Secondary: maximum member m_c at epoch 10.
  - H_variant if ≥ 75% of runaways and ≤ 10% of controls are ≥ 1.2.
  - H_context if ≤ 25% of runaways are.

**Controls.**
- The founder under ATOMIC must show m_c ≥ 1.5 (1.76 measured).
- The founder under BASE must show ≤ 1 (0.79 measured).

**Companion.** E9 (cb7f occupancy).

## Ledger entry (W2-2)

- **Result.**
  - **BASE:** the bulk is one homogeneous subcritical law; runaways are a qualitative second regime with no on-disk precursor before epoch 10.
  - **ATOMIC:** the threshold is quantitative.
  - cb7f is very probably takeover without depth.
  - C-A3 near-misses are mostly artifacts; 27000053 is the one genuine near-miss.
  - A byte-42 post-takeover sweep exists under ATOMIC.
  - The best early warning is births in epochs 11–15.
- **Confidence.**
  - medium-high for the BASE bulk law and for ATOMIC being quantitative;
  - medium for the second regime (n = 4) and for cb7f;
  - low for the identity of the BASE switch.
- **Strongest objection.** The single-interaction law omits kin pairing, density and field-shaped partner states. A rare variant could also have been missed.
- **Next.**
  - Run W2-2-EW and E9.
  - Byte 42 vs X-MAT state-free genomes.
  - k = 2–8 identical founders under BASE.
- **Nestor note.** This contradicts W2-6's map-built BASE process, which *over*predicts (0.175 vs 0.03). The two models disagree by about 600x. Reconciliation has been sent to W2-14.
