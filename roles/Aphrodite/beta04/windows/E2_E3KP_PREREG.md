# E3-KP + E2 PRE-REGISTRATION (frozen before any E2 / E3-KP production outcome)

C-015, W02.
- **Inputs:** the E1 production set (foundry 8d16a3288). E1 = WORLD_DEMAND_NOT_QUALIFIED (strict).
- **Admitted:** 15 R3 / R4 families in 7 worlds, all in 2 mechanism-kind pairings (fp, fs); R2 38.
- **Every claim below is restricted to this motif-limited admitted set,** and labelled as such.
- **Runners:** tfs1/e3/e3_known_positive.py (E3-KP); atlas/ (E2). Hashes are in beta04/FREEZE_E2_E3KP.json.

## A. E3-KP: TFS1_INSTRUMENT_QUALIFIED (directive Exp 3 known-positive)
- **Families:** the 15 admitted R3 / R4 families.
- **Procedure:** the substrate is INDEPENDENT of the foundry (interpreter B / TFS-1 enumeration; K-AB-conformant).
  - (i) TFS-1 base enumeration, budget 1e6, on each constituent mechanism's R1 families in the arm view. The FIRST
    dev-consistent program is taken (no hindsight; the same rule as foundry Addendum D).
  - (ii) Promote the found program's function-typed mechanism subterm (closed; alias-collapsed; v0.1-1). The
    foundry-config "readout fallback" is kept, as implemented and documented in E3_RUNNER.md.
  - (iii) TFS-1 enumeration on the R3 / R4 family with ONLY its constituent primitives, budget 1e6. The first
    dev-consistent program is then judged on test + tribunal by the evaluator view.
  - (iv) From-scratch control: TFS-1 enumeration at 1e6 with no library.
- **TFS1_INSTRUMENT_QUALIFIED = YES** iff (iii) qualifies on >= 80% (>= 12/15) AND (iv) fails on >= 80%.
  - Otherwise **TFS1_REACHABILITY_INSTRUMENT = FAIL** (per the directive). That is not a scientific rejection.
  - The first failing link is reported per family: R1 acquisition / under-determined stepping stone / horizon /
    composition search.
- **Gate:** the E3 2x2 lifetime screen (E3_DESIGN_DRAFT) runs ONLY if TFS1_INSTRUMENT_QUALIFIED = YES. Its own
  budget / K / filter decisions are frozen then, before it runs.

## B. E2: screening reachability atlas (directive Exp 2; atlas decisions O1-O12 frozen here)
- **Families:**
  - the 15 admitted R3 / R4 families;
  - plus 8 admitted R2 families drawn by a seeded rule `APHRODITE/B04/E2/R2/<idx>` (a contrast with lower demand).
- **Seeds:** 8 CRN seeds per (family, arm). This is screening; no confirmatory significance is claimed (directive).
- **Budget B:** 2e5 search charges per run (1x).
  - 4x (8e5) is run only for the arms and families pre-listed below, and only if the 1x screen leaves the frozen
    question unresolved.
  - 16x is not run in Beta-04 (compute cap).
- **Arms** (all from the same mutation chain base operator; atlas module; dev-only feedback):

  | Arm | Description |
  |---|---|
  | `chain_strict` | ordinary credit-climbing chain (exact partial credit on dev) |
  | `chain_neutral` | credit-BLIND chain: the same moves, acceptance ignores credit (desert-vs-rarity control) |
  | `X1` | genome retention: restore uniformly from retained programs |
  | `X2` | count / descriptor selection: uses D-BEH ONLY on families where D-BEH passed qualification; otherwise X2 is INSTRUMENT_UNVALIDATED for that family and not run |
  | `X3` | worse-into-new-cell admission |
  | `X3G` | matched structure-free control: cell count AND restore frequency matched to X3 |

  The arms derive from Nyx's design (3318a2098) via C-013 D1 (Palamedes).
- **Atlas open decisions, frozen:**
  - O1: descriptor probe runs are billed on a separate INFRA ledger. Arms are matched on search charges; both ledgers
    are reported.
  - O2: mutator max size = 20 (>= witness sizes).
  - O3: the D1 one-step ladder is PRIMARY; the B-arms are descriptive.
  - O4: the qualification ruler is R1 (C-013 procedure), with R1c reported.
  - O5: the "new certified mechanism" count is not used as an E2 endpoint.
  - O6: numeric-closeness credit is a diagnostic only, not a credit channel.
  - O7: route-based labels are descriptive only (uncalibrated).
  - The other O-items are as defaulted in ATLAS_DESIGN.md.
- **Descriptor qualification** runs first on every E2 family (outcome-free; the C-013 R1 procedure using the known
  witness route). Its result determines X2 eligibility.
- **Endpoint per (family, arm):** the number of seeds (of 8) in which the run reaches a program that QUALIFIES on test +
  tribunal within B. Final evaluation is archive-OFF (autonomous).
- **Frozen readouts:**
  - **DESERT_VS_RARITY per family**, on chain_strict vs chain_neutral hits:

    | Result | Label |
    |---|---|
    | strict > neutral, by >= 3 seeds | CREDIT_GRADIENT |
    | both 0 | DESERT_OR_HORIZON (reported with route length) |
    | otherwise | RARITY |
  - **FRONTIER_ARCHIVE_EFFECT (screen):** an exact sign-flip test over families on (best pre-specified archive arm,
    X1 / X2 / X3, chosen per family BEFORE the run as X2 if eligible, else X3) minus chain_strict hit counts, AND that
    arm minus its matched X3G.
    - **YES_SCREEN:** both one-sided p < 0.05 with sum > 0.
    - **NO:** the sum is <= 0 against chain_strict.
    - **INCONCLUSIVE:** otherwise.
    - Any arm judged INSTRUMENT_UNVALIDATED is excluded and listed.
  - **Pre-listed 4x escalation:**
    - condition: FRONTIER_ARCHIVE_EFFECT is INCONCLUSIVE, or every family is DESERT_OR_HORIZON at 1x;
    - scope: chain_strict, the per-family archive arm and X3G at 8e5, on the 15 R3 / R4 families only.
- **Cognitive ledger:** archive = SEARCH_INFRASTRUCTURE. A program found only with archive assistance is
  ARCHIVE-ASSISTED; its autonomous qualification is reported separately.

## C. Compute
- **E3-KP:** about 2-3 core-h (7 worlds; staged and cached).
- **E2 1x:** about 23 families x 6 arms x 8 seeds x about 40 s = about 12 core-h, plus descriptor qualification
  (about 1 core-h).
- **4x, if triggered:** about 15 x 3 x 8 x 160 s = about 16 core-h. That runs in a later cap window.
- **Rolling cap:** 48 / 24 h; <= 4 workers.

## AMENDMENT A1 (pre-data; red team reviews/REDTEAM_E2_E3KP_PREFREEZE.md: 5 BLOCKER / 13 MAJOR; supersedes s A-C where they conflict)

### A1-A. E3-KP
1. **Labelled an INSTRUMENT TEST that is GIVEN the decomposition** (constituent mechanisms named). It is not
   discovery (M1 / M8).
2. **Predicted outcome, written before data:** FAIL is likely (about 4-7 / 15). The TFS-1 size-8 Int-output class
   spans ranks 627k-6.0M, so 1e6 covers about 7% of it; 10 / 15 families depend on such an R1 stone.
3. **Primary:** as in s A, with the readout fallback ON (labelled). **Secondary rows:**
   - fallback OFF;
   - the foundry's acquired primitives given directly (skips TFS-1 R1 acquisition: isolates the composition step);
   - 2 extra keyed seeds;
   - the all-acquired library.

   Each family reports its FIRST failing link: R1_ACQUISITION / UNDERDETERMINED_STONE / HORIZON_R1 /
   COMPOSITION_HORIZON / COMPOSITION_UNDERDETERMINED.
4. **Verdict is POOLED over the 15 families:** >= 12 / 15 chain-qualified, AND from-scratch fails >= 12 / 15. The KP
   code is aligned to this.
5. **The single permitted neutral repair is pre-registered now:** observational-equivalence (OE) pruning in TFS-1
   enumeration (exact charges; OE classes on dev inputs). It is applied ONLY if the primary is FAIL with
   HORIZON_R1 / COMPOSITION_HORIZON as the dominant link, and re-run ONCE. If that still fails:
   **TFS1_REACHABILITY_INSTRUMENT = FAIL.**

### A1-B. E2: re-specified
1. **Library (B1).**
   - **Primary arms:** the family's constituent mechanisms as the FOUNDRY-ACQUIRED (learner-found, not sealed)
     primitives.
   - **DESERT REFERENCE:** a no-library credit-blind chain.
   - This tests whether credit and archives help cross the composition step given stepping stones.
2. **Arms (B2 / B4), at the code level:**

   | Arm | Code |
   |---|---|
   | `credit_blind` | `credit="none"` |
   | `chain_strict` | strict improvement |
   | `chain_neutral` | accept >=, as atlas/arms.py |
   | `D1-X3` | descriptor-guided worse-into-new-cell |
   | `X3G` | matched structure-free; matched to D1-X3 on cell count and restore frequency |
   | `desert_ref` | no-library credit_blind |

   D1-X3 / X3G run ONLY on families where D-BEH passes qualification (C-013 R1). Elsewhere: INSTRUMENT_UNVALIDATED,
   not run.
3. **Families:** the 15 admitted R3 / R4 families. The R2 contrast is dropped (compute). Atlas measurements run on all
   53 admitted families: existence, hitting rank, mutation robustness, feedback gradient.
4. **Primary endpoint (M6):** the FIRST dev-consistent program found qualifies on test + a fresh tribunal.
   - Secondary: any qualified program within B, with certifier-assisted hits tagged.
   - Archive OFF at final evaluation.
5. **Per-family labels:**

   | Label | Rule |
   |---|---|
   | REACHED | chain_neutral primary hits >= 1 / 8 |
   | CREDIT_GRADIENT | chain_strict or chain_neutral beats credit_blind by >= 3 seeds |
   | CREDIT_MISLEADING | credit_blind beats both credit chains by >= 3 |
   | DESERT_OR_HORIZON | all arms 0 / 8 |
   | UNRESOLVED | otherwise |
6. **FRONTIER_ARCHIVE_EFFECT (B3, M11).**
   - **Contrasts:** D1-X3 vs chain_neutral AND D1-X3 vs X3G.
   - **Unit:** skeleton clusters (merged skeletons; 5 clusters).
   - **Informative unit:** >= 1 hit in any arm.
   - < 5 informative units: **INCONCLUSIVE_CENSORED.**
   - **YES_SCREEN:** both one-sided cluster sign-flip p < 0.05 with sum > 0. Note that with 5 units the minimum p is
     1 / 32 = 0.031, so this is attainable only if all 5 point the same way.
   - **NO:** >= 5 informative units AND sum <= 0 vs chain_neutral.
   - Otherwise **INCONCLUSIVE.**
7. **4x escalation (M7):** only for (family, arm) pairs with >= 1 hit at 1x (Hestia's rule).
8. **Pre-launch checks (amendment item 6):**
   - certifier re-check of all 53 witnesses and the foundry route solutions;
   - start-at-target control (each arm started at the witness must "hit" at charge 0);
   - a constant / lookup control family;
   - a target-blindness test on production families (perturb test / witness -> decisions unchanged).
9. **REACHABILITY_ATLAS_COMPLETE = YES** iff:
   - the atlas measurements are complete on all 53 admitted families;
   - the arm screen is complete on the 15 R3 / R4 families at 1x;
   - the pre-launch checks pass.
10. **Compute (M13):**
    - Per-run costs for D1-X3 / X3G / chains at 2e5 are MEASURED first on an EXPOSED pilot_v2 family.
    - If the 1x screen is projected above 24 core-h, the frozen TRUNCATION ORDER applies:
      1. drop chain_strict first;
      2. then reduce to 6 seeds;
      3. then drop desert_ref on families whose admission evidence already shows from-scratch failure.
    - Each truncation is recorded.
11. **Claim limits and gates (M12):**
    - All E2 / E3 claims are restricted to the motif-limited admitted set (2 pairings).
    - The E3 2x2 lifetime screen requires E3-KP QUALIFIED AND E2 complete.
    - **E4 is BARRED on these worlds** (E1 not qualified; R5 = 0).

### A1-C. Open disagreement, recorded
The red team judged the readout fallback acceptable when it is labelled and paired with a fallback-OFF row; a
stricter reading would make fallback-OFF primary. **Decision:** fallback-ON stays primary (it is the foundry's
documented readout rule) and fallback-OFF is mandatory beside it. If they disagree, the report states both, and the
recommendation uses the fallback-OFF row.
