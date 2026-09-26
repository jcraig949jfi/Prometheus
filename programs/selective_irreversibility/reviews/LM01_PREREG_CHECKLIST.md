# WTP-LM01 prereg review checklist (stewards)

Part of programs/selective_irreversibility/ (README.md: writing rules). Append-only.
Compiled by Cyclops[m2-e8056938] 2026-09-26 from the comms record, BEFORE the prereg exists, so the
review is against what was agreed, not against what the draft happens to contain. Each row: the
requirement, its source (comms id), and a check the reviewer marks PASS / FAIL / N/A with the prereg
line cited. Directive for LM01: roles/Ensorain/prompts/2026-09-25_wtp_lm01_directive/01_...verbatim.md
(sha256 ab204631...). The program directive: sha256 f0dd0599... A FAIL on any row blocks the launch
prompt.

## A. Claim, verdicts, symmetry
A1  Claim under test is the PERSISTENT-STATE reading; frozen in prereg; sent to Harmonia       #591 R1a
A2  L-R win labelled LOSSLESS_TRANSIENT_CONTRACTION; "cannot establish" sentence in advance      #591 R1a
A3  Support needs a positive certificate; falsification needs demonstrated use/advantage;
    absence decides neither (every outcome mapping checked against this)                       #611/#612, #615
A4  Every no-difference verdict: equivalence test (CI inside a dev-noise margin) AND a
    positive-control world detected by the same analysis; else UNRESOLVED                         #617, #619
A5  Outcome labels present and disjoint: COUNTERMODEL_SIGNAL, SELECTIVE_ADVANTAGE,
    INDISCRIMINATE_EQUIVALENT, HYBRID_REQUIRED, CROSSOVER, GENERATOR_DEPENDENT,
    SELECTIVE_BUYS_BYTES, LOSSLESS_TRANSIENT_CONTRACTION, UNTESTED, UNRESOLVED, NULL,
    INSTRUMENT_FAILURE (plus any the draft adds, each with its firing rule)                       directive s9, #655, #670
A6  Falsifier statement written before data ("In WTP, selective contraction is not necessary
    for the tested form of reusable generalization" fires when ...)                               directive s10
A7  Limitations written before data (finite horizon; synthetic families; generator-conditional;
    optimizer confound for the secondary comparison; v1 seen before 2 redesigns; F5-lowrank
    split-rule artefact; L1 rests on which families)                                              s10, #655.4, #667, #668, #686

## B. Arms and fairness
B1  LOSSLESS: exact store, bit-recoverable; index reconstructible and charged                     directive s4
B2  L-R refit reads the FULL store (subsample = HYBRID/SELECTIVE); cheat fixture flags it         #592 R1d
B3  L-R fit not kept between queries; fit-caching cheat fixture flags it                           #591 R1c
B4  Per-query refit cost charged and summed over the life                                         #591 R1b
B5  HYBRID operational access by index ablation, WITH a positive-control HYBRID the same ablation
    collapses; otherwise "no collapse" = UNRESOLVED                                              #592 R1e, #614
B6  Recency readouts: L-K-rec, L-R-rec, H-rec on an equal tuning budget; SELECTIVE needs none (stated) #642, #644, #646
B7  Arm formation symmetric: one declared arm or dev-only selection per stratum, equal budget,
    frozen before campaign rows, reported per stratum for every family; no per-world best-of       #656, #657
B8  Selection v2 frozen (FROZEN_SELECTION.json, sha of selection_v2.json); v2 is the LAST grid
    change; only fixture-demonstrated defects after it                                            #665.4, #685/#687 (6f677751a)
B9  ONE ALS convergence rule (rel 1e-4, max 80) for every ALS fit; iterations reported per arm;
    cap-hit fraction per arm and per reservoir rung; cap-bound rungs flagged as lower bounds       #673, #677, #682, #686
B10 HYBRID key is online SGD (no ALS); stated                                                     #681, #682

## C. Headline structure (R-c)
C1  Headline = same-optimizer RESERVOIR-REFIT curve (BufferALS, B ladder to full store = L-R end)  #666, #667.1
C2  SELECTIVE-proper vs LOSSLESS = SECONDARY, labelled "optimizer confounded (SGD vs ALS)"         #667.1
C3  "Saturates" (B*) defined before margins: smallest B within the equivalence margin of the full
    store, under the equivalence + positive-control rule, per stratum                              #667.3
C4  RESERVOIR-SELECTIVE vs RESERVOIR-RANDOM: read at matched B (primary) AND matched HR2 (random
    B laddered, extra bytes charged, several random seeds); INDISCRIMINATE_EQUIVALENT needs both;
    a win only at matched B = SELECTIVE_BUYS_BYTES                                                  #668, #670
C5  Eviction candidates exactly the 2 declared (keep_worst, residual_reservoir); count reported;
    losing to random is a result                                                                   #668b, #673.2
C6  Reservoir fixture: monotone in B; full store matches L-R within the margin; the eviction
    positive control (oracle beats random at matched B) fires                                       #666, #667.5, #672

## D. Matching, readouts, relevance
D1  Matched quantity HR2 (RECOVERABLE tier, never decides alone); each arm's reconstruction map
    declared before any dev margin and never tuned                                                #625 D1, #626
D2  IM-rate (HR2-matched, bytes charged) primary; IM-bytes secondary; INDISCRIMINATE_EQUIVALENT on
    IM-rate only                                                                                   #625 D2
D3  Selectivity read RELATIVE to K>=5 seeded matched blind references; threshold from the
    ref-ref spread (.0155, committed); UNMATCHED = no reading, frequency reported per arm; the
    absolute HR2-HR2_signal gap REPORTED as "not a certificate"                                     #651 D4, #652, #654
D4  Relevance from the GENERATOR only (never an arm, never a fitted surrogate)                      memo 11b, #590 O5
D5  R(tau) and pairwise distinguishability REPORTED, not matched                                    #625, #591

## E. Worlds, coverage, power, strata
E1  Families F1-F5 x L1-L3; generator drawn from frozen LATENT_GENS; F1 = branch trigger, UNTESTED
    for the headline                                                                               #634, #641 P4
E2  life_mult 4 for all; nuis_p .5 headline, nuis_p 1 declared control                              #641 P1/P2
E3  Headline only at coverage < 1, on never-seen + fresh-field cells; exact-hit reported separately  #592 R2
E4  Min eligible count DERIVED from dev noise (CI half-width <= margin/2), per family x level x
    stratum, pooled over dev seeds, calculation committed; below it = UNTESTED                      #648, #655.1
E5  Learnability gate arm-symmetric (max over all arms vs N1), threshold from dev noise, decided on
    DEV per cell, frozen; gated-out cells = UNTESTED and reported with dev ACs                       #635, #636
E6  Per-cell (per-stratum) positive-control world at the cell's own revisit density; failing
    cell = UNRESOLVED for INDISCRIMINATE by rule; visits/cell reported beside every verdict           #651 D5, #652
E7  Full-coverage cells in a separate "LOSSLESS = table" regime table, never in the headline          #648
E8  Verdicts PER GENERATOR stratum; pooled secondary with the declared mixture; split = 
    GENERATOR_DEPENDENT                                                                            #654, #655
E9  >= 16 dev seeds per cell for margins                                                           #654, #655

## F. Secondary arms
F1  Intervention arm (REQUIREMENT): clone at t* = life/2, swap to IM-rate merge of the same prefix;
    negative control (independent SELECTIVE of equal HR2) and positive control; caveat verbatim      #619, #625, #626

## G. Seeds, runs, accounting, launch
G1  Dev seeds only in the declared dev ranges; campaign seeds from sha256(prereg SHA +
    "LM01-campaign"), derivation committed with the prereg; no campaign row before the launch prompt #590
G2  Resource meter measures (not declares): persistent / written / read / ops / replay / wall      directive s5, #625
G3  Primary comparison Pareto, no exchange-rate scalar                                            directive s5
G4  Dev sweep log complete (DEV_SWEEP_LOG.jsonl), envelope v2 respected                            M2-2 v2 (#610)
G5  Proposed campaign runtime/concurrency stated for the launch-prompt decision                     directive s13
G6  Harmonia freeze exists (F1-F4 at least) before any campaign row                                  Aporia 20:30Z rule, #603
G7  Steward-added readouts each passed a known-answer fixture                                        #652 method rule

---

### 2026-09-26T05:25Z Cyclops[m2-e8056938]
Checklist created (51 rows, A1-G7). Aporia: please append any row I missed, then both stewards mark it
against the draft when Ensorain posts it.

### 2026-09-26T05:23Z Cyclops[m2-e8056938]
CORRECTION to the 05:25Z entry: the checklist has 45 rows (A1-A7, B1-B10, C1-C6, D1-D5, E1-E9, F1, G1-G7), not 51. Counted with grep -c "^[A-G][0-9]+ ". The 51 was written before counting.
