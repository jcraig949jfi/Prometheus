# W2-9: statistical-method review of the NPE confirmatory verdicts

> Saved by Nestor from the worker's returned text: the worker could not write report files. The scripts and outputs in this
> folder were written by the worker: `stats_review.py` → `stats_review.json` + `digest.txt`, and `fdr_marginal.py` →
> `fdr_marginal.json`. The worker used about 4 CPU-minutes, read-only.

## Scope
- 20 decisions in total:
  - every C-lane verdict in c9x (14 decisions from 11 experiments);
  - W1 (3);
  - P2 (1);
  - ARC3 (1);
  - the frontier audit X-MAT-INTERNALIZE.
- Every decision was recomputed from committed results JSON and checked against its frozen `run_*.py` docstring.
- Each verdict then went through an adversarial loop.
- Tests are one-sided exact unless stated. "✓" means the frozen statistic reproduced exactly; none was wrong.

## Summary
1. All 20 frozen statistics reproduce exactly. Every problem is in design, endpoint, power or interpretation.
2. **ROBUST:**
   - C-SELFLOC;
   - C-ENERGY;
   - C-DENSE (only as "certified replication occurs");
   - C-ABLATE LOC;
   - C-ATOMIC C1;
   - C-DENSE-COPY;
   - C-STATELESS-FFA6 (unconditional p = 2.3e-6);
   - C-CRITICAL-MASS. Its weak claim also passes under independent founders (P(confirm) = 0.28–0.76).
3. **FRAGILE:**
   - C-ABLATE SEARCH: deleting any one of its 10 up-cells gives p = 0.0107.
   - C-RUNAWAY: 7/150 is exactly the minimum passing count, prior power was 0.05–0.56, and it was the second try at the splice claim.
   - C-CORE: 17/27 against a bar of 16.2. It fails at SPECIFIC < 15% or at freq 0.9.
4. **C-A3-INTERNALIZE is FRAGILE.**
   - 8 events, but only 4 (exactly the bar) under stricter definitions: free share ≥ 0.25, or still held at 2000.
   - There is no null or control arm.
   - The 4 large events are real.
5. **ARTIFACT-RISK: C9-H1R.**
   - Under FREE the gate is satisfied at entry by construction (`tasks.py:153-168`), so M = −I/2 always.
   - The label only says whether the ungated-VM mean falls between 0.15 and 0.30.
   - Only "gated+VM = 0/60" stands.
6. **ARTIFACT-RISK: X-MAT.**
   - 7 of 8 endpoints are at L_share = 1.0, where X ≈ 0 by structure.
   - If the 18–56% MUT bytes counted as foreign, the verdict would be MIXED (2 endogenous / 2 transplanted).
   - There is no positive control.
7. **C-ZERO-SPECIFIC is donor-clustered** (ICC 0.44).
   - The donor-level sign test gives p = 0.003, which fails the frozen 0.001.
   - Every donor was admitted by a zero-state screen, so ZERO > CONST is partly built in by selection.
8. **NOT_CONFIRMEDs that carry no information:**
   - ENERGY_FOR_DEPTH: unattainable once FULL D2 = 3;
   - C-NORECOMB: power about 0.08;
   - C-ATOMIC C2: only 2 of 15 specimens were capable.

   C-SWAP-ACQUIRE is a near-miss (p = 0.0018). It flips at depth ≥ 10.
9. **Multiplicity** over 17 p-valued decisions:
   - all CONFIRMEDs survive Holm at 0.05 and BH at 0.05;
   - C-RUNAWAY and SEARCH fail Holm at 0.01;
   - expected false CONFIRMEDs about 0.02–0.05.

   The bigger risks are winner's-curse shrinkage and second tries after a failure.
10. **Fix first:**
    - the bare-threshold rules: C-CORE, C-A3, X-MAT and H1;
    - a cheap VM-only check: screen the 16 C-ZERO donors from a 0x5A register state.

## 1. Verdict table

| # | verdict | test recomputed | issues | robustness | revised confidence |
|---|---|---|---|---|---|
| 1 | C-SELFLOC CONFIRMED | Fisher d≥1 24/36 vs 0/36, p = 1.57e-10 ✓; paired McNemar 24/0, p = 6.0e-8; d≥3 13 vs 0 | Paired data tested with unpaired Fisher (harmless); arms share the implant, so there is no D24 issue | Leave-one-physics-out passes all 3; d≥2/3/5 all p < 5e-4; power 0.97 | ROBUST (implanted copier only) |
| 2 | C-ENERGY CONFIRMED | sign 17/1, p = 7.25e-5 ✓ | The mechanism is confounded with energy-ordered reaping (dossier B A3). The effect sits at the depth-1 wall: d≥5 5 vs 4, d≥1 29 vs 29 | 0/40 single-cell deletions flip; leave-one-pressure-out passes; 10 up-cells removable; power 0.97 | ROBUST (effect); mechanism not separated |
| 3 | C-DENSE CONFIRMED | Fisher 13/40 vs 0/40, p = 3.8e-5 ✓; McNemar 1.2e-4 | The endpoint is ≥ 1 replication event. 5/13 cells have exactly 1, and there are 151 events in 42,934 births. d≥2 4 vs 0, p = 0.058 | ≥ 2 events: 8 vs 0, p = 0.0027, which fails both frozen bars | ROBUST for "certified replication occurs"; FRAGILE read as "heredity" |
| 4a | C-ABLATE LOC CONFIRMED | sign 14/0, p = 6.1e-5 ✓ | none | 0 flips; Holm 1.8e-4 | ROBUST |
| 4b | C-ABLATE SEARCH CONFIRMED | sign 10/1, p = 0.00586 ✓; diff 9 vs bar 8 | It needed exactly 10 up and got 10. "Necessary" here means a 60% drop; exploration showed 81% | 10 of 40 single-cell deletions flip it (p → 0.0107); Holm within the experiment 0.0117 | FRAGILE |
| 4c | ENERGY_FOR_DEPTH NOT_CONFIRMED | D2 3 vs 3, p = 1 ✓ | Unattainable once FULL D2 = 3 (best possible p = 0.125); power at exploratory rates 0.16 | n/a | Uninformative |
| 5 | C-RUNAWAY CONFIRMED | Fisher 7/150 vs 0/150, p = 0.00727 ✓; paired 0.0078 | 7 is the minimum passing count. The endpoint was chosen post hoc after C-NORECOMB failed (declared; fresh seeds). It is the highest of 4 identical-condition blocks (7/150, 2/80, 1/80, 1/24; heterogeneity p = 0.54) | Thresholds 15–100 all give 7/0; at d≥10, 14 vs 3 fails the BASE = 0 bar. Prior P(confirm) 0.05 / 0.23 / 0.56. Claim-level Bonferroni ×2 gives 0.0145 > 0.01 | FRAGILE (P(H0 given confirm) ≤ 0.04: fragile, not false) |
| 6 | C-CRITICAL-MASS CONFIRMED | Fisher 41/80 vs 5/80, p = 8e-11 ✓ | The endpoint cannot separate the claim from independent lottery tickets: P(confirm under independence) 0.28 / 0.53 / 0.76 at p1 = 0.0625 / 0.08 / 0.108. Superadditivity p = 0.013, which fails at pooled p1 (already retracted) | d≥3/10/20/50 all p < 0.005 | ROBUST for the weak stated claim; "critical mass" unsupported |
| 7 | C-NORECOMB NOT_CONFIRMED | 5 vs 5 of 48, p = 0.63 ✓ | Power about 0.08 (pooling with c2a8 at 0/0 halved the effect). 7ae3 BASE d≥5 was 5/24 here vs 4/150 in C-RUNAWAY's BASE (two-sided p = 0.003) | — | Uninformative; partly a BASE-arm fluke |
| 8a | C-ATOMIC C1 CONFIRMED | 46/80 vs 1/80, p = 4.4e-17 ✓ | Composite intervention (the keep rule also deletes self-writes); world-level depth; 2 runaways with 0 founder births | d≥5..100 all p < 2e-11 | ROBUST (composite) |
| 8b | C-ATOMIC C2 NOT_CONFIRMED | 1/120 vs 0/120 ✓ | Only 2 of 15 specimens ever reached d≥5; the rule needs ≥ 4 favouring ATOMIC | — | Uninformative (ineligible) |
| 9 | C-SWAP-ACQUIRE NOT_CONFIRMED | 9/240 vs 0/240, p = 0.0018 ✓ (minimum passing count 10) | Only 1 of 9 hits is founder-rooted. The unpaired analysis is correct (D24) | Flips to CONFIRMED at d≥10 (11 vs 0, p = 4.3e-4) or at alpha 0.002. Power at the observed rate 0.41 | FRAGILE null; read as underpowered |
| 10 | C-CORE CONFIRMED | 17/27 vs bar 16.2 ✓ | A proportion bar, not a test. Wilson CI 0.44–0.78; P(theta ≥ 0.6) = 0.60 | One classification flip fails it. SPECIFIC < 15% gives 14/27; freq 0.9 gives 15/27. CORE4 19/27 vs about 0.0008 by chance | FRAGILE ("conserves SELF+LDIR": ROBUST; "and little else": FRAGILE) |
| 11 | C9-H1R COST_INTERACTION_ONLY | M = −0.10, I = +0.20 ✓. Bootstrap I [0.117, 0.289], M [−0.144, −0.058]; sign-flip p for I < 5e-5 | Degenerate 2×2: under FREE the gate is satisfied at entry by construction, so the FREE arms are identical 60/60, M = −I/2 always, and I = the ungated-VM mean. "GATE_EFFECT" alone is unattainable. The competence ruler is also cached (dossier B A1) | P(abs(I) ≥ 0.15) = 0.88 | ARTIFACT-RISK (label); robust fact: gated+VM 0/60 |
| 12 | C-DENSE-COPY CONFIRMED | 39/64 vs 1/64, p = 1e-14 ✓ | 2 cells | 7ae3 14/32 vs 0 (p = 1e-5); ffa6 25 vs 1. L2 at ≥ 2 checkpoints 30 vs 0; at the final checkpoint 21 vs 1 | ROBUST |
| 13 | C-STATELESS NOT_CONFIRMED | conditional Fisher 23/29 vs 11/24, p = 0.0122 ✓ | Conditions on L2, which is post-treatment. The effect is only in ffa6, and it shrank 36% from exploration | unconditional 0.0091, paired 0.0085, cell-stratified 0.014: all fail 0.001 | Correct; a real effect below the bar |
| 14 | C-STATELESS-FFA6 CONFIRMED | 34/42 vs 11/33, p = 3.3e-5 ✓ | Post-hoc cell (declared; fresh seeds). L2 differs by arm (p = 0.047), but against the effect | unconditional 34/48 vs 11/48, p = 2.3e-6; paired 25/2, p = 2.8e-6; 0 single-run flips; claim-level ×2 passes | ROBUST ("persistence" reading later withdrawn) |
| 15 | C-ZERO-SPECIFIC CONFIRMED | 26/48 vs 2/48, p = 2.4e-8 ✓ | 16 donors × 3 seeds, ICC 0.44, design effect 1.87. Every donor was admitted by a zero-register competence screen, re-screened to 16/16 before the freeze | Donor-level sign 11/1, p = 0.0032; Wilcoxon 0.0016 (both fail 0.001). Within-donor permutation p < 5e-6. Cluster bootstrap diff [0.27, 0.71], P(< 0.25) = 0.011. Leave-one-donor-out max p 3.7e-7 | ROBUST effect / ARTIFACT-RISK for "zero is special" |
| 16 | C-A3-INTERNALIZE CONFIRMED | 8 events vs bar 4 ✓ | No control arm and no null calibration. The 20-seed threshold assay flickers (17 of 215 free checkpoints followed by 0). Two events rest on 1 genome each. The "last checkpoint with" rule ignores persistence | free ≥ 2 genomes: 6; free share ≥ 0.25: 4; held at 2000: 4; ≥ 3 checkpoints: 5. The 4 strong events (84–199 genomes, share up to 0.98) are not noise | FRAGILE as "8"; ROBUST that ≥ 4 internalizations occurred |
| 17 | X-MAT ENDOGENOUS 8/8 | recomputed from rows and tags ✓ | 7 of 8 endpoints at L_share = 1.0, so X ≈ 0 by structure. No planted positive control. MKL is keyed on the audited label | X at the first free checkpoint ≤ 0.14 in all 8. Counting MUT (18–56%) as XENO gives 2 endogenous / 2 transplanted, i.e. MIXED | ARTIFACT-RISK |

## 2. Cross-cutting findings

**Units, pairing and independence.**
- Units were correct everywhere.
- Unpaired Fisher on paired designs changes no verdict once McNemar is recomputed.
- D24 stream shifts are analysed unpaired, which is valid.
- The one material independence issue is donor clustering in C-ZERO-SPECIFIC. The within-donor fixed-effect test passes 0.001, but the donor-population test gives p = 0.002–0.003.
- Clustering elsewhere is checked and harmless.

**Tests.**
- All p-values reproduce, and sidedness matches what was declared.
- The exact tests are conservative (C-RUNAWAY mid-p 0.0036).
- Four rules have no sampling distribution: C-CORE, C-A3, X-MAT and H1. All four come out FRAGILE or ARTIFACT-RISK.

**Power and eligibility.**
- Three NOT_CONFIRMEDs were eligibility failures: ENERGY_FOR_DEPTH, NORECOMB and ATOMIC C2.
- The eligibility-count rule was applied only from C-SWAP-ACQUIRE onward.

**Endpoint validity.**
1. World max depth is not founder establishment:
   - C-SWAP-ACQUIRE: 1 of 9 founder-rooted;
   - C-ATOMIC: 2 runaways with 0 founder births;
   - C-ZERO CARRY: 5 of 11 with anc0 < 0.9.
2. Depth is bistable, so a threshold of ≥ 20 gives the same answer anywhere from 15 to 100.
3. The "last checkpoint with" rule (C-A3) counts transients.
4. Conditioning on L2 in C-STATELESS blurs establishment with acquisition.
5. The H1 2×2 is degenerate by design.
6. C-ZERO's contrast is built by donor selection.
7. X-MAT's endpoint is structural after takeover. The informative window is the takeover itself, where XENO peaked at 0.02–0.22 and was then purged.

**Post-hoc elements.** All were declared. The real exposure is second confirmatory tries after a failure.

## 3. Program-level multiplicity

- **Family:** 17 p-valued decisions plus 3 rule-based ones.
- **Results:**
  - Holm at 0.05 and BH at 0.05: no CONFIRMED fails.
  - Holm at 0.01: C-RUNAWAY (adjusted 0.036) and C-ABLATE SEARCH (0.035) fail.
  - Expected false CONFIRMEDs about 0.02–0.05 at a 0.5 prior; about 0.05–0.17 at a 0.2 prior.
- **Winner's curse:** exploration → confirmation shrinkage of −70% (SWAP), −52% (SEARCH), −36% (STATELESS), −34% (DENSE) and −21% (CORE). NORECOMB and ENERGY_FOR_DEPTH vanished.
- **Second tries:**
  - splice (NORECOMB fail → RUNAWAY pass);
  - persistence (STATELESS fail → FFA6 pass);
  - 7ae3 portability (ATOMIC C2 fail → SWAP fail).

## 4. Adversarial loop on the three closest calls

- **C-RUNAWAY.** Probably real; FRAGILE. The four splice-off blocks are homogeneous (p = 0.54).
- **C-ZERO-SPECIFIC.** ROBUST at the donor level at alpha 0.01, not at the frozen 0.001. The reading carries selection risk. Unresolved: 0x5A competence of the donors.
- **X-MAT.** Bookkeeping is unlikely, given the takeover purge, but no test that could have failed has excluded it. ARTIFACT-RISK.

## 5. Recommendations

1. **Re-label in FINDINGS.**
   - Mark as fragile CONFIRMEDs: SEARCH, RUNAWAY, CORE and A3.
   - Mark H1R as a degenerate design.
   - Report X-MAT as ENDOGENOUS under the MUT-neutral convention and MIXED if MUT counts as foreign.
   - Re-label ENERGY_FOR_DEPTH, NORECOMB and ATOMIC C2 as INELIGIBLE/UNDERPOWERED, and SWAP-ACQUIRE as a near-miss.
2. **Future frozen rules.**
   - Use cluster-level tests.
   - Give every rule a sampling distribution.
   - Compute eligibility at half the exploratory effect.
   - Set a claim-level alpha budget for second tries.
3. **VM-only check.** Screen the 16 C-ZERO donors from a 0x5A register state.
4. **X-MAT.** Add a planted-transplant control, and split MUT by the host class at the time of mutation.

## 6. Ledger entry (W2-9)

- **Question:** do NPE confirmatory verdicts survive a statistical-method review?
- **Evidence:** 20 decisions, recomputed.
- **Result:** all 20 statistics reproduce.
  - **ROBUST:** 8 decisions in 7 experiments.
  - **FRAGILE:** 4.
  - **ARTIFACT-RISK:** 3.
  - **Uninformative nulls:** 3.
  - **Near-miss null:** 1.
  - **Expected false CONFIRMEDs:** about 0.02–0.05.
- **Confidence:** high on the recomputations; medium on power and on the C-ZERO selection argument.
- **Strongest objection:** FRAGILE is not false. The C-ZERO screen argument is moot if the donors copy from 0x5A. The all-MUT-foreign case is an extreme bound.
- **Unresolved:**
  - the C-ZERO donors' 0x5A competence;
  - an assay-repeatability null for C-A3;
  - the splice-on BASE seed-block gap (5/24 vs 4/150, p = 0.003);
  - the X-MAT MUT split.
- **Next questions:**
  - random-effects analyses for P2 and ARC3;
  - C-CORE "little else" against a purifying-selection null;
  - a per-verdict "flip distance" in FINDINGS;
  - other "last checkpoint with" endpoints.
