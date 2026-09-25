# ENSORAIN WTP-01 "WILD TENSOR PHYSICS" -- campaign report

Currency: 2026-09-24. Seat Ensorain[m2-14baf7d5]. Preregistration
ensorain/PREREG_WTP01.md (c5d31985f); engine ensorain/wtp/ (93998df6f),
both committed before any world ran. Rows: ensorain/runs/wtp01/
(waveA.jsonl, waveB.json, waveC.json, waveD.json, waveE.json,
summary.json, fossils/ -- 35 anomaly fossils with genome, seed and the
replayed event stream).

## VERDICT (preregistered rule, computed by ensorain/wtp/campaign.py)

    SEARCH SPACE MOSTLY DEGENERATE -- REDESIGN

  (a) >= 3 REPLICATED non-ARTIFACT anomalies over >= 2 mechanism classes
      PASS as scored (18 replicated, 15 classes) -- but see s3: under
      diagnosis none of the 18 is a structure-driven competence finding
  (b) >= 1 phase boundary                               FAIL (0 of 3 sweeps)
  (c) >= 5% competent valid worlds and >= 20 niches     FAIL (4.5%; 42 niches)

The seat's reading AGREES with the verdict and is harder on the campaign
than the rule: WTP-01 found no reproducible, structure-dependent
competence phenomenon. It did produce a working foundry that caught its
own false discovery.

## 1. What was run

    world genomes attempted          3,000  (6 generations x 500)
      by generator                   random 1,262 / grammar 488 /
                                     novelty 473 / mutation 487 /
                                     recombination 290
    valid (passed preflight)         2,370
    illegal (died in preflight)        613  (mostly graphs made
                                            unreachable by direction laws)
    crashed (kept as rows)              17
    world runs                       6,000 in Wave A (each genome + its shuffled-latent twin),
                                     plus 350 (B) + 324 (C) + ~40 (D) + 200 (E)
    compute                          single CPU host, ~30 min wall
    behavioural niches (competent)      42
    anomalies flagged (Wave A)         733 worlds
    anomalies selected (Wave B)         35 (stratified by detector)
      REPLICATED 18 / WEAK SIGNAL 4 / FALSIFIED 13
      replay digest check              35/35 deterministic
    phase boundaries                     0 (3 capacity sweeps)
    TRANSFERRED                          0 (Wave D)
    Wave E recombinants                191 valid; flag mix A4 44, A6 29,
                                       A1 16, A2 10, A5 2

## 2. The strangest specimens

S1 -- THE FALSE DISCOVERY (dec8a39d07b2c182; also ad338376629fb633,
19eea2a88c3412e2). CP / TT memories (evolve, anti-Hebbian, SGD) in
BINARY worlds (2^7-2^9 cells) with a small catastrophe rate. Flagged as
the campaign's top competence outliers (CG ~ 20: the end-of-life error
10^20 times below birth), REPLICATED in 3-4 of 5 seeds, shuffled-latent
control hits 0-2 of 5 -- so the preregistered ARTIFACT rule did not fire.
Autopsy: in every seed where it "fired", the field's variance at end of
life is EXACTLY 0. Catastrophes zero a slice of the tensor; with binary
modes each zeroes half the world; a few of them kill it. The normalised
competence metric (error / current field variance) then divides by ~0.
Wave C had already pointed at the cause -- "frozen_world" (no
catastrophes) is one of the variants that removes the property.
Status: ARTIFACT (diagnosed after the frozen scoring; the frozen verdict
is not changed by it). Instrument defect, recorded in the ledger.

S2 -- THE JUMP INTO FAILURE (b235013022100e1f). TT memory, Hebbian rule,
random 15x10 field. Replicated a sudden single-checkpoint jump (A2) in
4/5 seeds, while ending far worse than birth (CG -2.5 to -10.6); the
shuffled control shows it too in 2/5. Its world family: removed by no
credit delay, shuffled latents, reversibility, extra noise, no rollouts
or a frozen world; kept under memory x0.5/x2, shuffled topology, no
marks. UNEXPLAINED: a failure mode that needs delayed credit, world
structure, irreversibility and a moving world together. Not a competence
finding; logged as a failure fossil.

S3 -- RICH WITHOUT KNOWING (A6 x 7; e.g. 01931366e7cf718a,
d2593f285c22facb). Memoryless or mark-only organisms, often random walk,
in generous economies (metabolism 0.1-0.7, harvest threshold below 0,
long regrow). Top-5% energy with zero competence. Shuffled controls hit
equally (3-5 of 5); only "reversible" or "no marks" removes it in two of
four families. The economy is winnable without learning -- the E0 lesson,
rediscovered by a machine.

S4 -- THE BEST GENUINE COMPETENCE IS MEMORISATION. 26 valid worlds (1.1%)
beat the trivial mean predictor by > 0.1 decades; the best
(f91d3941ac427dce, NLMSE 0.85) is a lookup TABLE of 508 floats in a
3x6x4 = 72-cell world. WTP-01's preflight never required memory to be
smaller than the world, so its competence tail is mostly storage, not
structure: 16 of the 26 are tables, 11 live in sparse worlds.

A4 (x7): anti-learning (updates that diverge) replicates in 3-5 of 5 seeds
and equally in shuffled controls -- mechanical, structure-independent.

## 3. What the campaign established

WORKED (the foundry itself):
- 3,000 executable, hashable, replayable world genomes across 8 field
  generators, 34 registry atoms, 12 geometries, 10 memory substrates,
  7 learning rules, 7 search policies, marks, hazards, irreversibility.
- Deterministic replay: 35/35 digest matches.
- The attack machinery worked as designed: shuffled-latent twins exposed
  A4 and A6 as structure-independent; a world-family variant located the
  real cause of S1 before a human looked.

DEGENERATE (the search space as drawn):
- Competence is almost absent (1.1% real), and where it exists it is
  memorisation in worlds smaller than the memory.
- Every replicated anomaly is an artifact (S1), a mechanical failure
  (A4, S2) or an economy that needs no mind (A6).
- No phase boundary along capacity.

## 4. Redesign (what WTP-02 must change before it runs)

R1 METRIC. Competence against a FIXED reference (the initial field's
   variance) and against the mean predictor, never against the
   organism's own birth memory; a world whose variance collapses is
   terminated and labelled, not scored.
R2 NECESSITY PREFLIGHT. A world is legal only if (i) memory budget <
   world size (bounded memory is the premise), (ii) a memoryless random
   walker loses energy (no free economies), (iii) a planted learner with
   the matched representation gains competence (the world is learnable
   at all). Illegal otherwise.
R3 RNG STREAMS. Separate generators for world, organism and
   instrumentation; WTP-01's transplant autopsies were confounded because
   a transplanted memory skipped rng draws and the world evolved
   differently (Wave D "same-world" numbers are not interpretable).
R4 CONTROLS PER DETECTOR. Every detector gets its twin: shuffled latents
   for competence, memoryless/random-policy twin for economy (A6),
   frozen-learning twin for anti-learning (A4); ARTIFACT applies to all.
R5 BUDGET SHAPE. Fewer, longer lives in legal-by-necessity worlds rather
   than 3,000 short lives; E0-E2 showed learners need thousands of
   samples.
R6 SWEEPS where the family attack shows causal dependence, not capacity
   by default.

## 5. Seat predictions scored

    REDESIGN p .45     RIGHT (verdict); the substance is closer to PARK
                       than the rule records
    "factorised memory matched to a factorised field" as the main class
                       WRONG -- the top class was an artifact; real
                       competence was mostly tables
    "boundaries possible along capacity"  WRONG (0/3)
