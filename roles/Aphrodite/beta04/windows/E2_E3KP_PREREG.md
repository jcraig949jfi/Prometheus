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
