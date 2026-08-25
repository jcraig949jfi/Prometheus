# PREREGISTRATION — SCORER-FIX: remove the `candidates[0]` guess and re-read the frozen corpus

**Written 2026-08-25 before any fix code exists.** Follows TRANSFER-1 **REDESIGN** (`285b8d44`),
whose measurement forced this rung. Governing doctrine:
`aporia/docs/DOCTRINE_counterfeit_battery_and_ladder_2026-08-25.md`.

---

## 1. The defect, as measured

`score_by_aggregate` emits `candidates[0]` when its value matches no candidate. Measured at
**182/182** parser-firing NONDEGENERATE tasks for the `M1_plus` mutant, which scored 0.1978
there on pure 1-in-4 luck. It is a **guarded** scorer, so it sits inside Apollo's clean-routing
pool — the regime Lexis proved closed at 0.8333.

Consequence already adopted as doctrine: **the null for a firing-but-wrong rule on a
k-candidate task is 1/k, not 0.** Every "near zero" threshold on this substrate has been sitting
below its own achievable floor, including the `<0.10` bar I wrote into TRANSFER-1's prereg.

## 2. The intervention, and the constraint that shapes it

**Make the fall-through ABSTAIN**: when no candidate matches the aggregate value, leave
`selected_answer` untouched rather than emitting `candidates[0]`.

**`C` is byte-frozen and must stay that way.** `blackboard_evolve.REGISTRY` is the baseline every
ΔE in this arc is defined against; editing it in place would silently invalidate IQ-PORT-1,
IQ-NULL and their provenance audit. So the fix is a **declared, reversible variant pool assembled
in the harness** — a new op object built from the existing one, substituted at measurement time.
`apollo/src/` is not touched.

## 3. Inventory first — audit ALL guarded scorers, not just the one that was caught

`score_by_aggregate` was found because a mutant happened to route through it. The same
fall-through may exist elsewhere and would contaminate readings nobody has taken yet.

**Preregistered audit:** for each of the five guarded scorers plus the plain scorers, determine
by **execution** whether it can emit an answer when nothing matches — construct a state where
its guard fires and its value matches no candidate, and record what it writes. Report the count.
This is the enumerate-the-inventory rule; a scope claim is a measurement.

## 4. Predicted readings, each with the input that would make it FAIL

    S1  With the abstain fix, ALL SIX mutants (M1_plus, M2_off_by_one, M3_swapped, M4_identity,
        M5_return_n, M6_half_total) score <= 0.02 on the NONDEGENERATE stratum of the frozen
        TRANSFER-1 corpus.
        FAILS IF: any mutant stays above 0.02. That would mean the 1-in-4 floor is coming from
        somewhere other than this scorer, and the diagnosis was wrong.

    S2  The port's PER-SURFACE numbers are unchanged: v0 0.9643, v1 0.9346, v3 0.9600,
        v2 0.0000, within +/- 0.01.
        FAILS IF: any per-surface number moves by more than 0.01. That would mean the PORT
        ITSELF was drawing on the guess, and IQ-PORT-1's dE would need re-reading -- the most
        consequential possible outcome of this rung.

    S3  The 120-task battery is UNCHANGED: baseline 0.833333 and ported 0.875000.
        FAILS IF: either moves. **If it moves, that is reported LOUDLY in the headline**, because
        it would move a number every prior rung in this arc has quoted.

    S4  The audit finds at least one further scorer with the same fall-through.
        This is a prediction I am genuinely unsure of and it gates nothing; it is reported
        either way, and "zero others" is a real result, not a null.

**Attainable-range check, done in advance this time.** With abstain, a firing-but-wrong rule
emits nothing, so `selected_answer` stays `""` and can never equal `correct`. The floor becomes
**exactly 0**, so the `<= 0.02` bar in S1 sits inside the attainable range rather than below it.
That is the P138 check executed before the threshold is chosen, which is what I failed to do last
rung.

## 5. Terminal states — asserted to partition over S1 x S2 in code

    ADVANCE   S1 and S2 both hold. The fix is a clean instrument repair: it removes the floor
              without touching what the port measured. TRANSFER-1 becomes re-readable against
              the same frozen corpus, and the mutant table becomes a real discriminator.
    REDESIGN  S1 holds, S2 fails. The port was partly riding the guess. The fix is still right,
              but IQ-PORT-1's dE must be re-read before anything downstream is trusted.
    PARK      S1 fails. Abstain does not remove the floor, so the mechanism is not what the
              182/182 measurement implied. File a GATE_ELI5 and re-diagnose.

S3 and S4 do not gate the terminal state; they are reported alongside it. S3 failing is loud but
it is information about the substrate, not about whether the fix works.

## 6. Scope, declared in advance

- **The frozen TRANSFER-1 corpus is reused unchanged** (`sha256 e2e6898d…`, seed 20260825,
  400 train / 200 test / 200 X). Re-generating it would destroy the before/after comparison,
  which is the entire reason this rung is cheap.
- **The 120-task battery is not modified**, including its degenerate `T = 2N` task.
- **`apollo/src/` is not edited.** No registry widening, no new domains, no agents revived.
- This rung measures accuracy on a frozen corpus and one battery score. It does **not** re-derive
  E(C), and it does not touch the SELECTOR question.
- Numbers from a **single seed**; no replication, so no intervals are quoted.

## 7. Cost-to-falsify

Rows for S1–S4 are written to `aporia/iq/COST_TO_FALSIFY.jsonl` with `outcome: null` **before**
the fix is written. Cumulative record: 15/16 predicted probe costs matched.
