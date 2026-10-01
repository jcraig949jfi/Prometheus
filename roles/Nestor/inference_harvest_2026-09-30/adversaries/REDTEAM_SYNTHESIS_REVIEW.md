# Red-team review of the NPE inference-harvest synthesis (2026-09-30)

Fresh-context reviewer. I was asked to be exacting, not agreeable.

**What I reviewed.** The six deliverables: SYNTH (`NPE_MECHANISTIC_SYNTHESIS_2026-09-30.md`), THEO (`NPE_COMPETING_THEORIES.md`),
UNM (`NPE_UNMINED_EVIDENCE.md`), EXP (`NPE_DECISIVE_EXPERIMENTS_NEXT.md`), BLD (`BUILDER_EXPERIMENT_SPECS_PRIMITIVES.md`) and
HO (`INFERENCE_HARVEST_HANDOFF.md`).

**What I checked them against.**
- dossiers A–G;
- ADV1 and ADV2;
- `forensics/FORENSIC_FUNCTIONAL_CORE.md` (FOR) and its JSON;
- the raw campaign files under `campaigns/`.

`FORENSIC_MAP_PREDICTS_OUTCOMES.md` does **not exist**. `map_offspring.log` is partial: 21 donor rows at the time of review.

**My own checks.** All read-only, with `python -B` and PYTHONDONTWRITEBYTECODE. The scripts are in the session scratchpad, not
the repo. About 3 CPU-min in total. The only file I wrote is this one. I made no git writes, ran no world, and touched no
holdout, D2 or secrets path.
- **R1.** Re-ran `forensics/nestor_hijack_check.py`. It reproduces 200/400, 0/400 and 0/400, 1/400, and 12,485 vs 64
  authored bytes exactly.
- **R2.** The same hijack probe, retargeted to cells 7ae3, ffa6, 9cba and e160, under zero and random register contexts.
- **R3.** A side-0 and side-1 overwrite probe on 24 FOR corpus copiers (12 state-free, 12 not), zero context, 100 random
  partners each, with and without their E5/E7 bytes. Changed bytes were attributed with `prov`.
- **R4.** Re-ran `nestor_exposure_hazard.py`, and recomputed ADV1's compartment counts and size bins from
  `c_a3_internalize/results/*.json`.
- **R5.** Re-counted the ATOMIC runaway pool (`c_atomic/VERDICT.json`, `x_atomic/SUMMARY.json`, `c_core/VERDICT.json`) and
  the cb7f C-ATOMIC rows.
- **R6.** Read the ops masks of the donor-swap cells from the constructed runners.

Numbers from these checks are tagged **[RT]**.

**What I verified as correct**, and do not discuss further:
- 109/208 (46/80 + 36/64 + 27/64);
- U-T5 exposures: ffa6 976.9k, 7ae3 1,150.7k, 7 events vs 1;
- cb7f: 8/8 ATOMIC runs, 163–1,053 events, depth 4–6, total 3,946;
- FOR's 3/14,024;
- the GW arithmetic 1 − p0/p2 in ADV2's table;
- 12,485 / 12,549;
- the directive sha256 96d06e58…27d2 and commit c8023bde4;
- U-F1 12/0/3/26;
- the k = 4 figure 98 vs 76.3;
- the splice figures 0/222 vs 22/630 and 81 vs 77;
- 8/8 and 17/21 (reproduced only with L-dominated = L_share ≥ 0.95; see B3).

---

## BLOCKING

### B1. The "victim-magnet" in foreign cells is attributed to a mechanism that does not operate in those cells

- **Where:**
  - UNM:100, 115 ("This explains B's victim-magnet (100/240 founder overwrites in foreign cells…)");
  - SYNTH:109–112 ("That is also the 'victim-magnet' effect of foreign cells");
  - THEO:248;
  - HO:40;
  - SYNTH:197.
- **Problem.** The 100/240 comes from C-SWAP-ACQUIRE in **9cba and e160** (dossier B U1). The hijack that Nestor verified
  runs through 7ae3's **SELF** (ADV2 §1.3: "SELF returns the *partner's* base, so LDIR copies the partner"). SELF is not in
  the ops mask of either foreign cell ([RT] R6: 7ae3 0x2a, ffa6 0x2a, 9cba **0x2c**, e160 **0x28**; SELF = 0x02; dossier
  A:280 says the same for 9cba). Nestor's own probe, run in those cells:

  | cell (ops mask) | zero context: intact / KO | random context: intact / KO |
  |---|---|---|
  | 7ae3 (0x2a) | **200/400** / 0 | **157/400** / 0 |
  | ffa6 (0x2a) | 200/400 / 0 | n/a |
  | 9cba (0x2c) | **1/400** / 0 | **6/400** / 0 |
  | e160 (0x28) | **1/400** / 0 | **6/400** / 0 |

  Single-interaction side-0 hijack therefore gives about 0.1–0.75% per side-0 pairing in the foreign cells. The observed
  founder loss there is 31–46% of runs. The mechanism cannot account for it.
- **Secondary problem.** "100/240 vs 0/320" (SYNTH:111, UNM:115, THEO:248) mixes denominators. The matched control in the same
  experiment is 0/240 (B U1). The 0/320 adds X-ATOMIC-RANDOM, which ran in the own cell.
- **Fix.**
  - Replace the claim with: "In SELF-enabled cells (7ae3, ffa6), partners hijack 7ae3's SELF+LDIR at side 0 (verified). The
    foreign-cell victim-magnet (100/240 vs 0/240) is **not** explained by this. The single-interaction hijack rate in
    9cba/e160 is ≤ 1.5%."
  - Move the foreign magnet back to §5 (unexplained).
  - The founder-loss statement ("much of the 28%", SYNTH:109, HO:40) can stay only if X-TICKET ran in a SELF-enabled cell.
    State this explicitly.

### B2. The acquisition "prediction" is misquoted, and it is presented as a quantitative fit when its source calls it order-of-magnitude

- **Where:** SYNTH:32, 99–100; THEO:29–30 ("with no free parameters"); HO:30.
- **Problem 1: the numbers.** FOR's own computation (FOR:244–245) gives **5%** at the first checkpoint and **66%** over a run:
  1 − e^(−0.054) and 1 − e^(−1.07). The deliverables copy FOR's summary line (FOR:34–35), which says "about 7%" and "about
  64%". So the headline "about 7% vs 7/96" is a perfect-looking match that the computation does not produce. FOR is
  internally inconsistent here, and the synthesis took the wrong line.
- **Problem 2: the strength.** FOR:247–248 says: "this is an order-of-magnitude agreement, not a fit." The 95% CI on the rate,
  4e-5 to 6e-4 from 3 hits (FOR:234, 303), maps to roughly 1–14% at the first checkpoint and roughly 20–95% over a run. The
  observed values sit inside a band about 10x wide. "Predicts quantitatively" and "no free parameters" are overclaims.
  - The genome-screen rate (COMPETENT at the zero context) is also a different ruler from the in-world acquisition endpoint
    (first L2 event).
  - In-run genomes are neither independent nor uniform.
- **Fix.**
  - Quote 5% vs 7.3% and 66% vs about 55%.
  - Say "consistent in order of magnitude with a random-genome base rate (2e-4, CI 4e-5 to 6e-4, 3 hits)".
  - Drop "quantitatively" and "no free parameters".
  - Also correct FOR:34–35.

### B3. "Generic internalization" and "replacements hold it more stably" rest on compartments whose founders' state was never measured

- **Where:**
  - SYNTH:35, 158–159;
  - HO:44;
  - THEO:38, 195, 387, 404;
  - UNM:270–277;
  - EXP:146 (the E2 T4-kill).
- **Problem 1: "becomes" is not supported.** C-A3's instrument tests only D0 for state-freedom. Dossier E §6.2 reading 3 says
  explicitly that whether the replacement founders were state-free "is unmeasured". [RT] R4 shows how much this matters.
  - In **4 of the 17** non-L compartments that "became state-free", state-freedom is already the majority at the
    compartment's **first** competent checkpoint:
    - 7ae3 27000037: 147/148 at epoch 300;
    - ffa6 27000002: 177/187;
    - ffa6 27000003: 157/182;
    - ffa6 27000035: 89/117.
  - In **7 of 17** it is already the majority at the first checkpoint with ≥ 25 competent genomes. Add 27000070 (81/135),
    27000063 (79/89) and 27000033 (45/58).
  - These populations may simply have been founded by state-free donors.
- **Problem 2: the persistence comparison is unmatched.** The comparison "16/18 vs 4/8" (U-C3) sets *internalized*
  state-freedom (D0 required not free) against state-freedom that may be *ancestral*. Higher persistence of the latter is
  expected and says nothing about T4.
- **Problem 3: "any" is definition-dependent.**
  - "8/8 L-dominated" holds only with L-dominated = L_share ≥ 0.95 plus ≥ 3 checkpoints of ≥ 25 competent genomes.
  - With L_share ≥ 0.5 it is **8/11**. The three misses are exactly U-N1's near-misses (7ae3 27000008 and 27000061; ffa6
    27000053). They drop out of the ≥ 0.95 count because their competence collapsed or stayed below 25.
  - 17/21 is not "any" either.
  - So SYNTH:35 and 158, which say "any sustained competent population", contradict SYNTH §5 and U-N1 in the same documents.
- **Fix.**
  - Reword to: "state-free genomes are present in 25/29 large, sustained competent compartments (L_share ≥ 0.95 or ≤ 0.05).
    For non-D0 compartments it is unknown whether state-freedom was acquired or founding."
  - Remove the persistence ordering as evidence against T4, or re-run it only on compartments whose first-competent-
    checkpoint state-free share is below 0.2.
  - Drop E2's "T4 dead if non-D0 compartments internalize at ≥ 0.75", or define "internalize" by a first-appearance event.

### B4. E1 cannot kill T4 as T4 is written, and its ruler is likely to fail for every arm, positive control included

- **Where:** EXP:50–110 (kill criteria at EXP:95–101); HO:100–111; THEO:204–211.
- **Problem 1: E1 tests the condition in which T4 predicts nothing.** T4's first unique prediction is (a): "evolved genomes
  outperform their own computed P_est **in their home population but not in a naive one**; kin-context benefit"
  (THEO:206–207). E1 implants into a **random background population**, which is the naive case. A null E1 result is what T4
  predicts, yet E1 declares T4 dead on a null. E1 is therefore not the aggressive organization-vs-compact-instruction test
  the directive asked for.
- **Problem 2: the ruler probably cannot fire.** O_F is the share of sites ≥ 0.9 identical to the **implant** on transmitted
  positions. The deliverables' own evidence says identity to the implant decays even under full takeover:
  - U-I6 / ADV2 D6: label 256/256 while ≥ 0.9-founder-like sites fall to 0 by epoch 100;
  - U-I1: D0 bytes 0.94 → 0.04;
  - D:U9: about 5/64 shared bytes.

  So "O_F ≥ 0.5 by epoch 500" and "O_F ≥ 0.5 at 1,000" are likely to read 0 for EVO, SCR, SYN and the 7ae3 positive control
  alike. All residuals then equal −P_est, and "T4 dead" fires vacuously. This is a guard that cannot fail in T4's favour.
- **Problem 3: SCR may not be state-free.** SCR scrambles everything outside the "FOR necessary set" (EXP:60). That set was
  measured against **COMPETENT at the zero context** (FOR Q1), not against STATE_FREE (R1/R2). SCR genomes can therefore lose
  state-freedom, and EVO > SCR would then be a trivial T3-compatible result.
- **Problem 4: the prediction cannot be frozen as written.** "P_est under ATOMIC with VICTIM contexts" (EXP:68) cannot be
  computed from a single interaction. VICTIM contexts are a population property. The model, for example map_offspring's
  CARRY_L, has to be named and frozen.
- **Problem 5: pseudo-replication and cell.**
  - "The 8 epoch-700 16000006 modal genomes plus corpus late genomes" (EXP:58) cannot fit into 8 EVO slots.
  - The 8 modal genomes are one lineage.
  - They are 7ae3-cell genomes run in the ffa6 cell.
- **Problem 6: power and ceiling.**
  - With 8 seeds per genome and a true +0.15 advantage (p 0.5 → 0.65), P(x ≥ 6 of 8) ≈ 0.43 per genome. P(≥ 5 of 8 genomes)
    is then ≈ 0.2, so the T3/T6 kill has about 20% power.
  - If P_est > 0.85 (the robust 16000006 genomes), a residual ≥ 0.15 is unattainable.
  - "Mean EVO residual ≤ SYN + 0.10 (95% CI)" is ambiguous: which bound?
- **Fix.**
  1. Define the family by **content ancestry** (B2/B7 genealogy), not by identity to the implant.
  2. Before freezing, show on an existing X-ATOMIC or X-CONTENT replay that the ruler reads 7ae3 at about 0.52.
  3. Add a home-population arm: EVO implanted into its own late population vs a naive one. That arm is what T4 predicts.
  4. Derive the scramble mask from STATE_FREE knockouts.
  5. Name the context model behind P_est.
  6. Use 8 lineages, not 8 genomes.
  7. Pre-register power and eligibility (G §2.1).
  8. Until then, drop "the only design here that separates…" (EXP:108–110) and "T4 is dead if…".

### B5. E2's "ZERO" arm is not a no-payoff null, and its T1/T2 predictions overlap

- **Where:** EXP:114–151.
- **Problem 1: state-freedom still pays in ZERO.** E2 changes **only** the newborn's registers on an accepted overwrite
  (EXP:119–120). Every other organism still carries its own post-execution registers between interactions. So self-poisoning,
  a pointer advance under carried context (U-F1, U-F2, ADV2 D4), still penalizes copiers that are not state-free. State-
  freedom still pays, and "ZERO: always-scaffolded, so no payoff" (EXP:121) is false.
  - ADV1 K2 and ADV2 §5 item 10 meant a world *reset every interaction*.
  - As written, the T1 kill ("ZERO appearance hazard < 1/3 of VICTIM") and the T2 kill are both mis-anchored.
- **Problem 2: the sweep predictions do not separate T1 from T2.**
  - T1: "sweep only where it pays (VICTIM, RANDOM ≫ ZERO)". T2: "sweep ordered RANDOM ≥ VICTIM > ZERO". These are the same
    sweep prediction.
  - The T2 kill ("ZERO sweep ≥ 0.75 × VICTIM") would kill T1 as well.
  - Only the *appearance* hazard separates them. Appearance measured by sampled detection is itself confounded with sweep:
    a variant that never rises is rarely sampled.
- **Fix.**
  - Add a true reset-every-interaction arm as the no-payoff null.
  - State which kill targets which theory.
  - Measure appearance by genealogy (E4's instrument), not by first detection.

### B6. E4's "opposite" predictions are not opposite: T1's own hazard predicts monophyletic sweeps

- **Where:** EXP:155–190 (kill at 184–186).
- **Problem 1: the kill would falsely kill T1.** T1 says selection decides what persists. At the ffa6 hazard (about 1 per 140k
  organism-epochs, U-T5) and N = 256, T1 expects about one new origin per ~550 epochs. A variant that pays sweeps in about 100
  epochs (U-C5). So T1 plus selection **predicts** monophyletic sweeps, and "T1's recurrence claim is dead if ≥ 6/8 are
  monophyletic" would kill T1 on T1's own expectation.
- **Problem 2: monophyly is not specific to T4.** A single origin that sweeps is ordinary selection. It is not evidence of a
  "self-maintaining lineage process".
- **Problem 3: assay noise inflates origin counts.** STATE_FREE is a 20-seed threshold at 0.5 per vector, so borderline
  genomes flip between states. A per-content "most recent non-free ancestor" rule will count assay flicker as origins. The
  shuffled-parent null does not control for this.
- **Fix.**
  - Derive T1's expected origin count from the U-T5 hazard and the sweep time, and state it as T1's prediction.
  - Say that monophyly does not separate T4 from T1 plus selection. What would separate them is heritability of the trait's
    *mechanism* across independent origins, or kin-context dependence.
  - Add an assay-repeatability null: re-assay the same genome with new seeds.

### B7. "7ae3 verified" is a false verification status, and the establishment test is validated against the ruler the synthesis retires

- **Where:** SYNTH:197 ("(7ae3 verified)"), 33, 118–122; HO:33–35; UNM:216–220 (tagged REPORTED); THEO:198, 302–303, 390.
- **Problem 1: status.** U-S1 is tagged REPORTED (ADV2 [P]). Nestor has not re-derived it. `map_offspring.py` describes the
  7ae3 row as a "sanity anchor for the **earlier** 0.49–0.52 probe", and it is still running. Calling it "verified" overstates
  it.
- **Problem 2: the observed value uses the retired ruler.** "0.52 observed" is 109/208 **runaways at depth ≥ 20**. The same
  documents retire depth as an establishment ruler (SYNTH:195, BLD B6, EXP "What NOT to do"). They also argue that depth
  misses takeover without turnover (cb7f). If that argument is right, 0.52 undercounts establishment, and the match to 0.52
  is partly coincidental.
- **Problem 3: selective context.**
  - ADV2's table gives BASE: ZERO context P_est **0.26** (m 1.11, supercritical) and RAND context P_est 0 (m 0.98).
  - The observed BASE runaway rate for 7ae3 is 1/80 + 3/64 = **4/144 ≈ 0.03** ([RT] R5).
  - The deliverables report only the RAND row, relabel it "carried context" (SYNTH:121, UNM:219, HO:35), and present it as a
    success.
  - The founder in fact starts in the ZERO context. That row misses by about 8x.
  - "Carried" is also the name of a *different* context (CARRY) that map_offspring is computing now.
- **Problem 4: m does not explain the cessation.** m = 0.98 is near-critical. It does not predict a ~470-fold collapse in the
  losers' write rate (0.0012 vs 0.56) by epoch 12 (U-W3). That is content sterility (erosion), not subcriticality. "Which is
  why copying stops" (SYNTH:121, HO:35) does not follow.
- **Fix.**
  - Tag the result REPORTED.
  - State both BASE rows and the BASE miss.
  - Say "RAND context", not "carried".
  - Validate against an occupancy-based establishment once E9 exists, or state the depth caveat.
  - Fill in, or drop, "establishment is computable" pending S1.

---

## MAJOR

### M1. U-T5 "8x matches 7x" is not a test

- **Where:** SYNTH:35, 157; HO:42–43; THEO:33–34, 386; UNM:38–50, 251.
- **The data cannot separate 8x from almost anything.** Conditional on 8 events, [RT] finds that the 95% CI on the ffa6/7ae3
  hazard ratio is about **1.1x to about 370x**: Clopper-Pearson on 7/8, times the exposure ratio 1,150.7/976.9.
  - Equal hazards are rejected only at p ≈ 0.02 (one-sided).
  - A true 2x ratio still gives P(≥ 7 of 8 in ffa6) ≈ 0.14, and 3x gives ≈ 0.29.
- **Three further problems.**
  - The unit is organism-epochs, which T1 itself says is the wrong supply term (THEO:51–52).
  - Dossier E rates T-STATE-3 a "HYPOTHESIS … confounded by cell (tape layout, slots)" (E §4). That caveat is dropped.
  - The one 7ae3 event is **91% MKL and ≤ 6% MUT** (E anomaly 4, §6.2). Its state-free bytes were computed by execution,
    not supplied by the OPERAND operator whose 34-vs-239 count is the "supply". This is a competing account that none of the
    deliverables mentions.
- **ffa6 27000053 is an outlier under the stated hazard.** Its exposure is 409k with 0 events; under the ffa6 hazard,
  P ≈ e^−2.9 ≈ 0.055.
- **Fix.** Replace "matches" and "supply-limited" (HO:42) with "consistent with (n = 1 in 7ae3; 95% CI on the ratio about
  1–370x)", and add the MKL caveat.

### M2. "Reproductive machinery is public" is generalized from one SELF-using genome

- **Where:** SYNTH:57–58, 182 ("Contradicted… execution is public"); THEO:237–256 ("A copier is therefore a public good");
  UNM:113–117; HO:36; BLD B5.
- **7ae3 is atypical.** It uses SELF. SELF is necessary in only 2/128 FOR genomes (FOR:137, 151). 95.7% of the 51,007-genome
  corpus is SELF-free (ADV1 §1.1), and D:770 describes donors as "SELF-free, single-sided".
- **The typical overwrite is mostly self-executed.** [RT] R3 on 24 corpus copiers:
  - Partner-like overwrites of the copier's half do occur, and they vanish when the E5/E7 bytes are removed:
    - state-free copiers at side 1: 489/1,200 intact vs 3/1,200 knocked out;
    - not-state-free copiers at side 0: 174/1,200 vs 20/1,200.
  - The changed bytes are mostly written by the **copier's own context**:
    - state-free at side 1: 17,203 own vs 13,391 partner;
    - not-state-free at side 0: 10,277 own vs 648 partner.
  - For typical copiers the dominant mode is therefore wrong-side **self-import** (ADV2 §1.8), with partner execution a
    minority or mixed. 7ae3's 12,485 partner vs 64 own bytes is the atypical case.
- **Prior work.** "Shown here for the first time" (SYNTH:109) ignores Artemis's execution-order (side-1) hijack
  (F:33, 359), which T5 itself cites (THEO:254).
- **Fix.**
  - Scope T5 to: "Copy code can be executed by a partner. That is shown for 7ae3 in SELF-enabled cells. For typical SELF-free
    copiers, loss of the copier's own half is mostly its own wrong-side copy."
  - Change "Contradicted" to "Qualified".

### M3. The grounds given for demoting T4 are weaker than stated (answer to check 2e)

- **Where:** THEO:193–202, 219–221, 387–390, 400–406; SYNTH:181.
- **Verdict on the demotion.** Removing T4 as the *default reading* is **fair**. T4 was never positively certified, and burden
  symmetry puts it on T4. But three of the four stated grounds do not bear on T4, and the fourth is compromised by B3.
  - **1.009 is close to tautological.** L_share is bistable (only 5/236 free-bearing checkpoints are intermediate), so
    Σ free × L_share ≈ free_in_L by construction. The test cannot come out in T4's favour. THEO §9.7 (line 420) itself calls
    it uninformative, yet §9.1 (402) counts it as "pointing the wrong way".
  - **The GW match is a test on the unevolved founder genome.** It says nothing about whether *evolved* lineages carry
    organization beyond their map. The collision-table entry "contradicts (no lineage term)" (THEO:390) is a category error.
  - **"Core ≈ 8 bytes" uses single-site knockouts.** T4's prediction (c) is multi-site epistasis (THEO:210), which single
    knockouts cannot see. "Contradicts" (THEO:388) should read "untested".
  - **The generic count** is weakened by B3.
- **What is missing.** The one residue T4 owns (the 16000006 walk; ADV1 R1–R2) is n = 1. That is why T4 is *unsupported*.
  It is not *contradicted*.
- **Fix.** Reword to: "T4 is not required by any current evidence and none of its lineage-level predictions has been tested.
  It is no longer the default." Change the three collision-table cells to "untested", and delete 1.009 from §9.1.

### M4. The status of the depth ruler is inconsistent, and an untested adversary hypothesis is promoted to fact (answer to check 2f)

- **Depth is retired as a ruler.** See SYNTH:195, BLD:204, and EXP "What NOT to do", which adds "(E9 decides)".
- **Yet depth carries weight elsewhere:**
  - the GW validation (B7);
  - "8/11 given takeover" (SYNTH:192; BLD:243), which is 8/11 given takeover **and depth ≥ 20**. Given takeover alone
    (L ≥ 0.5) it is **8/15** (E §6.1);
  - E9 (EXP:276–284), which is designed to decide the very question already declared settled.
- **cb7f's takeover is asserted.** SYNTH:132–134 presents cb7f as "a family that takes over without turnover", while §5.6 and
  U-N2 say that one replay would decide it. That is ADV2's untested D5 promoted to fact.
- **No withdrawn interpretation is re-asserted.** I found none. The promotions are of untested adversary readings: this one
  and B1.
- **Fix.**
  - Use "depth is suspected (E9 pending)".
  - Use 8/15, or say "given takeover and runaway".
  - Remove the cb7f assertion from §2.4.

### M5. X-MAT's endogeneity is reported as "Supported" without its instrument caveats

- **Where:** SYNTH:177; SYNTH:156 ("X-MAT ENDOGENOUS … real material change"); HO:41.
- **What is missing:**
  - There is no planted-transplant positive control (Harmonia #1057 / F8; E anomaly 6). The instrument has never been shown
    able to detect import (memory: a frozen instrument is not a validated instrument).
  - MKL is keyed on the audited label (F §3.1).
  - The pilot started before the freeze.
  - After L = 1.0 no non-L source exists, so X ≈ 0 is nearly guaranteed (E §6.2 reading 1).
- **Fix.** Say "Supported, but not validated". Add these caveats to the table row and to HO item 4.

### M6. Donor side is an unmentioned confound of "state-freedom"

- **Evidence in FOR.**
  - FOR Q2: all **48/48** state-free genomes pass from **side 0**, against 23/80 dependent genomes passing from side 1.
  - FOR Q5: the side-1 share falls from 24/99 to 12/124.
- **Why it matters.** Part of what the STATE_FREE assay registers, and part of the "drift toward state-freedom", is a switch
  to side-0 copying. The side-0 copier runs first, so the partner cannot interfere (FOR:190–191). The synthesis attributes the
  whole change to "address source moves into constants" (SYNTH:161; HO:45). It also matters for:
  - T5: side-0 copiers are exposed to hijack differently;
  - E1: every EVO genome is side-0, while SYN's `LD L,0 ; LD E,40 ; E5` is side-0-only as well.
- **Fix.** Report the side switch alongside the address-source change, and randomize or stratify side in E1 and E2.

### M7. EXP is not prereg-ready as claimed, and several budgets do not add up

- **Prereg-readiness (EXP:7).** "Every design below is prereg-ready in content" is false for four designs, which lack fields
  the directive requires:
  - E3: no unit, no ruler definition, no null, no confounds;
  - E8: no ruler, no positive or null control, no per-theory outcomes;
  - E9: no controls, and a kill in one direction only;
  - E10: incomplete.
- **Budgets.**
  - E1a = 224 runs × 4.5 min = **16.8 core-h** before the positive and negative control arms: the 7ae3 control, the ZERO-world
    synthetic, the random implant, the painter and the sham. It does not fit the ≤ 16 core-h R2 envelope (EXP:4, 106).
  - The costs in the ranking table disagree with the bodies: E1 is 16 in the table vs 21 in the body; E9 is 1 vs 3 (EXP:27
    vs 284).
  - EXP:149 contradicts itself ("each fits R2 except E2a, which … is still within R2").
- **Missing eligibility counts.** No design gives one, although the header requires it (EXP:11).
  - E3 is the worst case. C-A3 had **1** 7ae3 event in 72 runs and about 5 eligible 7ae3 runs. At 24–36 seeds per arm, the
    OPERAND arm expects fewer than 1 event, so "rises by < 2x" (EXP:252) is not computable.
- **Fix.** Downgrade E3, E8, E9 and E10 to "sketch". Add eligibility and power to E1–E4, and re-cost E1a with its controls.

### M8. E6's "no other theory predicts that pattern" is a strawman against T3

- **Where:** EXP:193–219; THEO:320–324.
- **Problem 1.** Phase arithmetic follows from LDIR semantics: count mod 128. The deflationary account attributes self-
  poisoning to exactly that (ADV1 §1.9, table row 16). So T3 and T7 predict the same non-monotone pattern. E6 separates T6
  from T2 at most, not from T3.
- **Problem 2.** A world-wide change of slice budget also changes the background population.
- **Fix.** Restate the separation as T6/T3 vs T2, and hold the background fixed. For example, vary the budget only for the
  focal site, as a site-level parameter.

### M9. S1 placeholders and a live dependency

- **Where:** SYNTH:126, 219, 223–226; HO:96, 159–161; EXP:23.
- **Problem.** The synthesis and the handoff end in unfilled "S1 result" sections. Their conclusions ("establishment is
  computable", "E1 run with S1's per-genome map predictions") depend on S1, which had not finished at the time of review.
  EXP:3 says "Nothing here is … started", while EXP:23 says "running now".
- **Fix.** Do not hand off until §6 and §8 are filled, or removed and replaced by "pending". Reconcile EXP:3 with EXP:23:
  S1 is a static analysis in progress, not a campaign.

---

## MINOR

| # | where | problem | fix |
|---|---|---|---|
| m1 | SYNTH:96, 98; THEO:129, 145 | FOR's "5 beyond" is beyond the ~7-position last-setter motif (FOR:145–148), not the 3-byte minimal motif. "IQR 6–10" is the collapse set; the necessary set has IQR 7–13. | Say "beyond the last-setter motif"; label the IQR as collapse. |
| m2 | SYNTH:99; THEO:418 | The "500x" compares against the offset-0 prior. FOR's reachability-integrated prior of (3–4)e-6 gives about 50–70x, and FOR says the motif is about 2% of random competence. | Use "about 50x (reachable motif)". |
| m3 | SYNTH:148 vs UNM:252 and E §6.2 | The ffa6 MUT share is "43–49%" in one place and "43–67%" in another. | Use 43–67%. |
| m4 | UNM:273; THEO:37 | The size series leaves out the 75–124 bin, which is 0.67 (68/101) [RT]. The full series 0.08 / 0.25 / 0.71 / 0.67 / 0.78 is not monotone. | Report all bins. |
| m5 | BLD:243 | "8/11 (U-T4)": U-T4 has no 8/11, and 8/11 is conditional on runaway. | Cite E §6.1; use 8/15. |
| m6 | SYNTH:10; UNM:3–4 | "Every new number comes from committed data or single-genome VM calls" is false. ADV2 ran a 256-site toy population process (3 seeds × 2 genomes), which is cited as U-I6 and cb7f 3/3. | Disclose it. It is not a world campaign. |
| m7 | SYNTH:213; HO:91 | The k = 4 p = 0.0013 is reported without the joint LRT p = 0.108 or the runaway endpoint p = 0.70 (A W2). | Add both. |
| m8 | UNM:100–111 | ADV2 found 9/39 side-0 overwrites persisting after the SELF+LDIR knockout (30/39 vanished). Nestor found 0/400. The difference is not reconciled. | State the context and copy-error differences. |
| m9 | EXP:58 | The EVO draw is internally inconsistent (see B4). | Specify the 8 lineages. |
| m10 | FOR:34–35 vs 244–245; FOR:171 | FOR's summary contradicts its own body (7% / 64% vs 5% / 66%). "All three stock-VM genomes are state-dependent" is contradicted by `core_map.json` (7ae3 15000022 row 1: state_free true, R1 0.9, R2 1.0). | Correct FOR. |
| m11 | BLD:48 | The fixture "all-zero genome: L1 must FAIL" tests a trivially inert genome. The real anomaly 5e20dc8a (95% 0x00) **passed** P-11 3/3 (C:651–655). | Use the real specimen, with expected L1 PASS and L2 FAIL. |
| m12 | THEO:135 | "All BYTEWISE P-11 survivors are painters (U-X5)". U-X5 says "near-homopolymers". | Keep the source wording. |
| m13 | THEO:301–311 | T6 was required to avoid program vocabulary, yet its "Explains" list is written in it: establishment, internalization, poisoning, runaway. | Restate it in site/content/context/Φ/W terms. |
| m14 | HO:47; THEO:177 | "Founder bytes fall to 3–33%": 3–33% is the D0 share of the endpoint state-free L genomes (U-I2), not a trajectory. | Cite U-I1 (0.94 → 0.04) for the fall. |
| m15 | EXP:283 | E9 states only the "retire depth" outcome. | Add the converse: O_F < 0.5 in ≥ 5/8 means cb7f failed to establish. |
| m16 | SYNTH:111 | "shown here for the first time": see M2. | Credit Artemis for the side-1 hijack. |

---

## Checklist answers

- **Numbers (1).** Most numbers trace correctly: see the verified list at the top. The mismatches are:
  - B2 (7% vs 5%, 64% vs 66%);
  - B1 (0/320 vs 0/240);
  - m1 (IQR and motif);
  - m3 (43–49 vs 43–67);
  - M4 (8/11 vs 8/15);
  - m4 (bins);
  - m10 (FOR internals).
- **Claim strength (2).**
  - (a) Overclaimed; M1.
  - (b) "Computable" is overclaimed, and "verified" is false; B7.
  - (c) Overgeneralized, and wrong for the foreign-cell magnet; B1, M2.
  - (d) Order of magnitude only; B2.
  - (e) The demotion is fair; the stated reasons are not; M3.
  - (f) No withdrawn interpretation is re-asserted, but two untested adversary readings are promoted to fact: B1 and M4
    (cb7f).
- **Consistency (3).**
  - 1.009 is "points the wrong way" in THEO §9.1 but "uninformative" in §9.7.
  - Depth is retired but still used.
  - cb7f is asserted in one place and open in another.
  - "Any" (8/8) contradicts the U-N1 near-misses.
  - EXP:3 contradicts EXP:23.
  - Costs differ between the table and the bodies.
- **Designs (4).**
  - E1: can the ruler fire? It probably fires vacuously (B4).
  - E2: the null is not a null, and the predictions overlap (B5).
  - E4: the predictions are the same, not opposite (B6).
  - E6: strawman (M8).
  - E3: eligibility is unattainable (M7).
  - Does E1 separate compact instruction from organization? **No, not as written** (B4).
- **Missing alternatives (5).**
  - The 7ae3 event is built from computed (MKL) bytes (M1).
  - Side switch as a component of state-freedom (M6).
  - Wrong-side self-import as the typical mode of copier self-loss (M2).
  - Founder state of the non-L compartments (B3).
  - X-MAT's lack of a positive control (M5).
- **Boundaries (6).**
  - No world campaign is claimed as run.
  - No self-start: HO:116 and EXP:3 are explicit.
  - D2 is untouched.
  - Only m6 (the toy population process) and M9 (S1 "running now") need wording.

## Overall verdict

**NOT READY for fleet handoff. Revise before release.** The core deflationary picture is broadly well supported: a supplied
half-duplicator, world-set write-back, a label that is not the causal unit, and material turnover. The certificate-ladder
lesson (B1 primitive) is sound, and the demotion of T4 from default is defensible. But:
- the synthesis replaces one over-reading with several new ones, stated at the same confidence the program is trying to
  unlearn:
  - public machinery (B1, M2);
  - quantitative base rates (B2);
  - generic internalization (B3);
  - computable establishment (B7);
  - supply-matched hazards (M1);
- the flagship experiment E1 would, as designed, most likely return "T4 dead" regardless of the truth (B4);
- two other lead designs have null or kill logic that fails (B5, B6).

Fix B1–B7 and M1–M4 before the handoff goes to Aporia. The remaining items can be done alongside.

---

## 10-line summary

```
1. BLOCKING: foreign-cell victim-magnet (100/240, 9cba/e160) is NOT the verified SELF hijack: those cells lack SELF; hijack probe 1/400 (zero ctx), 6/400 (random) vs 200/400 in 7ae3/ffa6.
2. BLOCKING: acquisition "predicted quantitatively" quotes FOR's summary 7%/64%; FOR's own math is 5%/66% and FOR calls it order-of-magnitude (rate CI 4e-5..6e-4, 3 hits).
3. BLOCKING: "any competent population becomes state-free" / replacements persist better: non-L founders never assayed; 4/17 compartments are majority state-free at first sight (7/17 at first >=25).
4. BLOCKING: E1 tests T4 in a naive population where T4 itself predicts no residual; implant-identity O_F likely decays to 0 (U-I6), so "T4 dead" fires vacuously.
5. BLOCKING: E2 ZERO resets only newborn registers, so state-freedom still pays (self-poisoning); E4 monophyly is also T1's own prediction; neither kill separates theories.
6. BLOCKING: "(7ae3 verified)" is false (U-S1 REPORTED); 0.52 is depth>=20 runaways (the retired ruler); BASE ZERO row (0.26 vs 0.03 observed) omitted; RAND mislabelled "carried".
7. MAJOR: 8x vs 7x is non-diagnostic (95% CI of ratio ~1.1x-370x); 7ae3 event is 91% MKL / <=6% MUT, so operator supply is not its source; E rated it a cell-confounded HYPOTHESIS.
8. MAJOR: "execution is public" generalizes one SELF-user; for 24 corpus copiers self-loss is mostly own-context wrong-side import (17,203 vs 13,391; 10,277 vs 648 bytes).
9. MAJOR: T4 demotion is fair but 3 of 4 stated grounds are void (1.009 tautological under bistable L; GW on unevolved founder; single-KO core); X-MAT lacks a positive control; side confound; EXP not prereg-ready.
10. Verdict: NOT READY; fix B1-B7, M1-M4 before handoff. Boundaries OK (no runs claimed, no self-start); disclose ADV2's toy process and finish S1 placeholders.
```

Path: `F:/Prometheus-worktrees/nestor-d2v13/roles/Nestor/inference_harvest_2026-09-30/adversaries/REDTEAM_SYNTHESIS_REVIEW.md`
