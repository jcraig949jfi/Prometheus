# PREREGISTRATION — CEILING-UNDER-ABSTAIN: is 0.8333 partly a guess?

**Written 2026-08-25 before any code exists.** This is the question SCORER-FIX (`5971288b`)
explicitly withheld rather than reached for.

---

## 1. The measured facts this builds on

From SCORER-FIX's per-scorer audit (each probed with a state tailored to fire **its own** guard,
after a first audit that was vacuous):

    GUESS candidates[0] when nothing matches   8 of 10
      score_by_aggregate · score_by_aggregate__g · score_by_derivability ·
      score_by_derivability__g · score_by_max_entity · score_by_max_value ·
      select_nth · select_nth__g
    abstains                                   score_by_comparison__g
    UNRESOLVED                                 score_by_extreme_number__g

**Three of the eight are guarded**, so they sit inside Apollo's clean-routing pool.
**`select_nth__g` guesses and is a member of the known 0.8333 ceiling organism.**
Fixing `score_by_aggregate` alone moved the 120-task battery by **exactly zero**.

## 2. The question, and why the direction is knowable in advance

Replace the `candidates[0]` fall-through with abstention in **all eight**, as a harness-side
variant pool. `blackboard_evolve.REGISTRY` and everything in `apollo/src/` stay untouched — `C`
is the byte-frozen baseline every ΔE in this arc is defined against.

**Directional check, preregistered:** removing a guess can only lose tasks the guess happened to
win. It can never create a correct answer. So

    ceiling_after <= ceiling_before = 0.833333        ported_after <= 0.875000

**A RISE IS AN INSTRUMENT BUG, not a finding**, and the run reports it as such and PARKs.

**Attainable range, computed before any threshold is chosen:** `ceiling_after ∈ [0, 0.833333]`
and `ported_after ∈ [0, 0.875]`. Every branch below is stated as a direction and a count, not as
a cut against a number the instrument may not be able to produce.

## 3. Predicted readings, each with the input that would make it FAIL

    C1  ceiling_after < 0.833333 — the ceiling FALLS. `select_nth__g` guesses and is in the
        organism, so at least one currently-won task should depend on it.
        FAILS IF: ceiling_after == 0.833333 exactly. That would mean no task the organism wins
        is won by a guess, and Lexis's 0.8333 stands untouched as a capability number.

    C2  the fall is bounded: ceiling_after >= 0.70 (at most 16 of 120 tasks lost).
        FAILS IF: it drops below 0.70. I am not confident in this bound and I am recording that
        it is the weakest prediction here.

    C3  ported_after - ceiling_after is reported as dE_port under the abstain regime, ALONGSIDE
        the guess-regime value of +0.041667. Neither replaces the other silently.

    C4  score_by_extreme_number__g is resolved — a state is found that fires its guard — or it
        is reported UNRESOLVED again. It is NEVER called an abstainer on the strength of a probe
        that did not fire it.

    C5  per-category accounting of every task lost, so the fall is attributable rather than a
        bare delta.

## 4. What I will do about ΔE_port — decided BEFORE seeing the number

If the baseline moves, **ΔE_port is recomputed under the abstain regime and BOTH values are
reported with their regime named.** I will not quietly re-baseline, and I will not keep quoting
+0.041667 as if it were regime-free.

The specific commitment: **the abstain regime becomes the honest one going forward**, because a
scorer that guesses cannot support a claim about expressivity — but **every prior rung in this
arc quoted the guess-regime baseline**, and that fact gets stated wherever those numbers appear
rather than being silently superseded.

If ΔE_port *changes*, that is a correction to IQ-PORT-1's headline and is reported as one.
If it does not change, that is evidence the port's 5 tasks were never guess-dependent — which
SCORER-FIX already showed for `score_by_aggregate` alone and this would extend to all eight.

## 5. Terminal states — asserted to partition over the direction in code

    ADVANCE   ceiling_after == 0.833333. No won task depends on a guess. Lexis's proven ceiling
              stands as a capability number and the guessing pathology, while real, is inert on
              this battery.
    REDESIGN  ceiling_after < 0.833333. **LOUD**: the proven 0.8333 is partly guessing, dE_port's
              baseline moves, and every number this arc has quoted carries a regime qualifier.
    PARK      ceiling_after > 0.833333. Impossible by the argument in §2, therefore an instrument
              bug. File a GATE_ELI5 and re-derive the variant construction.

Three directions, three states, mutually exclusive and exhaustive over the reals. Asserted by
enumeration in code.

## 6. Scope

- The 120-task battery is **not modified**. No registry widening, no domains, no agents revived.
- Two pipelines only: the ceiling organism and the ported pipeline. This rung does **not**
  re-run the joint product BFS, so it measures **these two programs**, not a new ceiling over all
  programs. **A fall here shows 0.8333 is guess-dependent for the known organism; establishing
  the true abstain-regime ceiling would require re-running Lexis's BFS and is not done here.**
  That distinction travels with every number below.
- Single seed where seeds apply; no intervals quoted.

## 7. Cost-to-falsify

Rows for C1–C5 are written to `aporia/iq/COST_TO_FALSIFY.jsonl` with `outcome: null` **before**
the variants are built. Cumulative: 18/20 predicted probe costs matched.
