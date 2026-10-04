# D06 -- DEV WINDOW 6 REPORT: decision packet

C-006 (C-P2B-APH-BETA-01), cycle 6, DEV. Evidence tier 2.

## 1. Bottleneck after TEST-5
GTC was INCONCLUSIVE_INSTRUMENT: the UNSEEN stratum is a transfer floor for every library, and the rule genomes left
selections unchanged. Repairing R7 properly needs a world with MORE THAN ONE derivable class, plus a PROPOSAL-level
lever (T52: candidacy is the binding limit). That is world-design work. It is queued for DEV-7, with an
authorisation check: a new world is allowed, but a representation-changing W5P is not.

## 2. Decision
TEST-6 = a FROZEN CONFIRMATION of T51's only non-recovery positive (endogenous base-class derivation) on fresh LIN
seeds 8-15. Reasons:
- It is the strongest candidate statement for the Beta-01 close ("naturally generated worlds supply X at rate Y").
- It is currently exploratory, so it must be confirmed before it is used.
- It costs about 7 core-h, which fits the rolling budget.

## 3. Changes
- `t51_natural.py`: ARMS is now environment-overridable (V2B_T51_ARMS). The default is unchanged.
- `t06_confirm.py`: the frozen absolute endpoint and the H1/H2/H3 rules.

## 4. Qualification
- **F1 on seeds 8-15: 8/8** after calling W8's `init()` (W5 world).
- **Process note, recorded:** a first check WITHOUT init() returned 0/8. W8's generator needs the W5 world switch.
  That is a check-procedure error, not a generator defect. The seeds 0-7 check had called init().

## 5. Next
TEST-6: `beta01/windows/T06_T51C_SPEC.md`.
- DEV-7: R7 repair design (a multi-class world; a proposal-level genome; a charge endpoint; a pre-verified overfitter
  control).
