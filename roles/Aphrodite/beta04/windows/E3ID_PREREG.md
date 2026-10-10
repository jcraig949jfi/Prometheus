# E3-ID: STEPPING-STONE IDENTIFIABILITY DIAGNOSTIC (NEW PRE-REGISTRATION; DRAFT, NOT FROZEN)

C-015, W03. A new preregistration under the directive ("no more than one neutral repair per experiment without a new
preregistration"). It does NOT re-test or relabel E3-KP. **TFS1_INSTRUMENT_QUALIFIED = NO stays frozen.** E3-ID
answers a different question: where exactly does the causal chain break, and which repair class does the evidence
point to?

## Context (data already in hand; this is why the diagnostic exists)

| E3-KP row | Chain-qualified | Main failure |
|---|---|---|
| primary | 7 / 15 | UNDERDETERMINED_STONE 7 |
| fallback-off | 0 / 15 | |
| given-foundry-primitives | 14 / 15 | |
| all-acquired | 7 / 15 | |

So composition succeeds given the right stones, and TFS-1's own first-dev-consistent stone is often behaviourally wrong.

## Questions
- **ID-1 (world / ruler: identifiability).** How many behaviourally distinct mechanisms are consistent with the dev data
  of the R1 families the chain uses?
- **ID-2 (search order).** At what rank in TFS-1 enumeration does the sealed-equivalent stone first appear among the
  dev-consistent candidates?
- **ID-3 (developmental machinery: hypothesis retention).** If the organism RETAINS the first k behaviour-distinct
  dev-consistent stones per constituent (k = 4), instead of committing to the first, does the composite become
  reachable? The R3 / R4 dev data then selects among the hypotheses.

## Procedure (target-blind during search; sealed data used only after search, for scoring)

**ID-1 / ID-2.** For each constituent mechanism m of the 15 families, on the R1 family used by the E3-KP primary,
TFS-1 base keyed enumeration (the same order as the primary, budget 1e6, max size 12):
1. Collect EVERY dev-consistent program and extract its stone (the same extraction as E3-KP, fallback on).
2. Group the stones into behaviour classes on the fixed probe inputs [-40, 40] (Int->Int / Int->Bool) or the pair grid
   [-12, 12]^2 (Int->Int->Int). FAIL counts as a value. Probes are inputs only, so this is target-blind.
3. Report:
   - n_classes;
   - the rank (by charge) of the first program in the sealed-equivalent class (scored afterwards against the sealed
     mechanism);
   - the class rank of that class;
   - whether that class's first program also passes the R1 test + tribunal.

**ID-3 RETAIN-k (k = 4).**
- Library for the R3 / R4 chain search = the first k behaviour-distinct stones per constituent, in enumeration order,
  taken from ID-1 (distinctness on probes; no sealed information).
- Chain search: TFS-1 enumeration, budget 1e6, max size 12; the first dev-consistent program is judged on test +
  tribunal (E3-KP rules).
- Also report RETAIN-1 (= the E3-KP primary, as a consistency check) and RETAIN-2.
- **Cost accounting:**
  - the library is larger, so the chain search space is larger;
  - charges are reported as is;
  - no budget compensation.

## Outcomes (frozen before any production E3-ID run)

**ID_IDENTIFIABILITY** (per stone used by a failed E3-KP family):
- AMBIGUOUS if n_classes >= 2 and the first class is not sealed-equivalent;
- UNIQUE otherwise.

Pooled: the fraction of UNDERDETERMINED_STONE units that are AMBIGUOUS, reported with counts.

**ID_RETENTION_REPAIR:**
- RETAIN-4 chain-qualified >= 12 / 15: **YES** (hypothesis retention repairs the chain);
- otherwise **NO**, with first-failing-link counts.

Scratch is already 15 / 15 failing (E3-KP); it is not re-run.

**Interpretation map (fixed now):**
1. If ID-1 is mostly AMBIGUOUS and RETAIN-4 is YES: the first failure is DEVELOPMENTAL MACHINERY (premature
   commitment to one stone), a candidate for CHANGE_SEARCH_OR_DEVELOPMENTAL_MACHINERY.
2. If ID-1 is mostly AMBIGUOUS and RETAIN-4 is NO: the first failure is WORLD / RULER identifiability (R1 dev data too
   weak to pin the stone, and the composite does not disambiguate within budget).
3. If ID-1 is mostly UNIQUE: the extraction or promotion step is at fault (an instrument defect). Reported as
   INSTRUMENT.

None of these relabels TFS1_INSTRUMENT_QUALIFIED, and none counts as COMPOSITIONAL_DISCOVERY: the stones come from
sealed-family-indexed R1 tasks given to the organism, not from an autonomous lifetime.

## Predicted outcome (written before data)
Map 1 is the most likely. The pilot and production primary stones look like threshold / offset variants (e.g. x > 3
vs x > 4), and the foundry's enumerator found the sealed-equivalent stone, which suggests it lies within a few classes.

## Compute
- About 2-4 core-h (ID-1 enumeration over full budgets: 1e6 x about 20 stones at about 45 s each = about 0.25 core-h;
  RETAIN chains 15 x 3 rows x up to 60 s each).
- <= 2 workers.

## AMENDMENT ID-A1 (pre-data rulings; build 767ee7adf; no production E3-ID run yet)

Rulings on E3_RUNNER s4C:

1. **Unit family.**
   - Use the R1 family the primary acquired from.
   - If the unit was not acquired, use the first attempted family that yielded a dev-consistent program.
   - If every attempt hit the horizon, the unit keeps its horizon label.
2. **Designated rows: the UNCERTIFIED RETAIN-k**, as the draft literally says.
   - The choice is made from the prereg text, NOT from the pilot (pilot: uncertified RETAIN-4 3/7; CERT 4/7).
   - RETAIN-k-CERT is a reported secondary.
   - If designated and CERT disagree on ID_RETENTION_REPAIR, both are reported and the synthesis states the
     disagreement.
3. **Pooled fraction.** It counts units whose E3-KP primary first link is UNDERDETERMINED_STONE. The "all units of
   failed families" count is reported beside it.
4. **Label edge cases.**
   - Zero classes: NO_STONE (excluded).
   - **One class that is NOT sealed-equivalent: UNIQUE_WRONG.** Within budget the dev data admit only a wrong mechanism,
     so the sealed class is beyond the R1 horizon. This maps to WORLD / RULER-or-HORIZON (not INSTRUMENT).
   - **INSTRUMENT** applies only to UNIQUE units that ARE sealed-equivalent yet were labelled UNDERDETERMINED_STONE in
     E3-KP (an extraction / promotion defect).
5. **"Mostly"** = a strict majority. A tie is MIXED, and both readings are reported.
6. The RETAIN failing-link rule "no sealed-equivalent stone retained", the dual probe sets, the empty-slot handling and
   no budget compensation (s4C items 6-9) are CONFIRMED.
