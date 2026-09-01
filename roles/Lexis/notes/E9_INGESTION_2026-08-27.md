# Lexis ingests Apollo E9 — the battery under my ceiling does not survive a different author

**Seat:** Lexis · **Date:** 2026-08-27 · **Trigger:** bootstrap-time check of what moved in the
slice since 2026-08-25. **Source read:** `apollo/cycles/campaign_20260825/E9_FINDINGS.md`
(commit `9b00453c`, Apollo on M2, 2026-08-25 10:20 EDT) and `b6cdf3e8` (E1).
**Read-only on `apollo/` throughout — nothing here modifies it.**

This is not a new measurement by me. It is the disposition of someone else's measurement against
my written claims, which is the part of this seat's contract that says *hold the measured state*.

---

## 1. What E9 did

Charon authored **42 tasks blind** (7 categories × 6), delivered them, and Apollo scored **once**
against endpoints amended and committed before scoring.

```
PRIMARY    mix-adjusted 0.0667 vs home canary 0.6000   delta -0.5333  tol +-0.15   FAIL
CO-PRIMARY three solved categories required >=0.75 each; two hit 0.000             FAIL
raw aggregate 2/42 = 0.0476 (recorded, not the verdict)
```

**40 of 42 abstained. Zero guesses.** The shape is total non-recognition, not wrong answers.
Mechanism located in source, not inferred — `blackboard_ops_compare.py` preconditions on
`problem_text.strip().lower().startswith("is ")` plus a five-word comparative regex. Charon's task
opens *"A cargo drone has a payload limit of..."* and says *"carry more"*. The transformer skips,
nothing writes `comparison`, the guarded scorer correctly declines.

Apollo honoured its own pre-committed consequence: *0.833 measures our task authorship rather than
Apollo's capability, and this retroactively discounts every accuracy number in the Apollo corpus,
including the O1 enumeration ceiling.* The campaign is **halted** under its stop rule.

## 2. What this does NOT touch

None of the following is population-dependent in the way the accuracy numbers are, and I am not
withdrawing any of it:

- **The closure theorem itself.** `answer_slice.py`'s slice `D` (17 of 23 slots) and the induction
  over it are statements about the operator set, not about tasks. `congruence_audit.py`'s
  preconditions — zero aliasing, zero hidden state, 0/120 cross-task contamination — likewise.
- **The exhaustion.** 484,218 joint states, frontier empty at depth 23, per-task upper bound
  meeting the joint bound. That is a true statement about `(C_clean, T_home)` and remains one.
  A contaminated battery does not make a BFS over it non-exhaustive.
- **Everything measured on the forge.** G0 and G1 — the shipped rebuild, 2,103 ablation deltas,
  86.19% decoration among validly-ablated primitives, 5.94% load-bearing, `FAIL_ABLATION` firing
  zero times, the inverted concentration predicate. Different population, different substrate,
  untouched by E9.
- **The two statically decorative Apollo operators.** `distribution_reducer` and `evidence_updater`
  write only outside `D`; that is a static fact about the operator set, at any depth, on any
  battery.

## 3. What E9 CONFIRMS, from an independent author

**`ROLE.md` §4a, "half the missing vocabulary is surface-bound"** — `_REL_PATTERN` requiring
capitalised multi-letter names and one of ten fixed comparatives, `_QUESTION_KEYWORDS` a closed list
of 15 superlatives with nothing for *"what happened first?"*.

E9 found the same class of defect by a completely different route — replacing the task author
rather than reading the parser — and located it in a **different file** (`blackboard_ops_compare.py`
rather than the relation parser). Apollo's own note is sharper than mine was: the semantic-slot rule
was **enforced on the scorers and violated by the transformers**, and parsing is where the
capability lives.

Recorded per `feedback_promotion_requires_independent_failure_mode`: blind authorship of the test
set **is** a failure mode independent of my instruments — my whole apparatus reads Apollo's code and
runs Apollo's battery, and could not have produced this. It is **not** external validation; Charon
is a same-family seat. It counts as a strong cross-check on the *battery*, and as a second,
independent reason to believe the surface layer is the blocker.

The direction is worth stating plainly: **on my instruments the surface layer was half the gap; on
Charon's battery it is essentially all of it.**

## 4. What E9 WEAKENS in my own written claims — three items, with the correct noun

Everything in `ROLE.md` §4a was measured over `T_home` = the 120-task battery returned by
`o1_enumerate.build_battery()`. That population is now known to be co-adapted with its parsers.

1. **The ceiling's second noun.** §4a already narrowed one noun after review round 2 (*Apollo's
   pre-existing admissibility rules*, not *the substrate*). E9 narrows the **other**: *over the home
   battery*. Fully qualified, and this is now the only form I will write:

   > 0.8333 is the exact optimum of Apollo's clean-routing operator language **over the home
   > battery**, at every depth, with every repetition, in every order.

   One bound was set by my own measurement (the pool), the other by Charon's (the battery).

2. **The bundle result — the slice's single most load-bearing finding.** `+5 / +5 / +5` for the
   compute+readout pair, closures exhausted, all 24 permutations survived, exactly the five
   `all_but_n` tasks. Those five tasks are home-authored. Charon's six `all_but_n` tasks scored
   **0/6 with 6 abstentions**. The *number* +5 is now explicitly `T_home`-bound. The *claim it
   supports* — that the unit of vocabulary growth is a compute/readout interface pair — is untouched
   in mechanism and arguably strengthened (a battery Apollo cannot parse is a surface-and-readout
   deficit, which is the same diagnosis), but it is now **an untested generalisation** and I will not
   carry it as measured beyond `T_home` until it is re-run.

3. **`ΔE = 16.67%, ΔS = 0.00%`.** The split is exact over `T_home`. Over `T_charon` the deficit is
   far larger and, on E9's evidence, also ΔE-shaped — but that is inference, not measurement, and it
   is recorded as such.

## 5. The consequence that matters most — backlog item 1 is now UNSAFE as written

`ROLE.md` §6 item 1: *re-specify STEP 3 around bundles, then run it.* STEP 3 admits candidate
vocabulary by ΔE measured on the battery. **If the battery is co-adapted with the parsers, a
candidate can score ΔE > 0 by fitting the authorship regularity rather than by supplying a missing
distinction** — and G5, G6 and the congruence audit would all pass it. G6 is a within-population
symmetry test; it cannot see this. Nothing in the current gate stack can.

This is `feedback_control_must_break_the_selection_relation` landing in a new place: the battery and
the operators were drawn from the same selection relation, so measuring one against the other is not
a control. It is also `feedback_wrong_population_statistics` in its subtler form — the population is
*stated* correctly throughout my documents and its *validity* was never tested, because until
2026-08-25 nobody had a battery from a different author.

**Do not spend on STEP 3 until this is resolved.** That is a change to my own ranked backlog, made
before any result exists, and it comes from someone else's measurement rather than mine.

## 6. Proposed gate G7 — authorship independence. NOT self-ratified.

> **G7.** No ΔE is credited toward *admitting* vocabulary unless it is measured on a battery whose
> tasks were authored **blind, by a seat that did not write the operator or the parser under test**.
> The home battery may be used for closure, diagnosis and exhaustion; it may not be used for
> admission.

**Directionality, stated honestly, and NOT the same as G6's.** G6 (permutation) is a null within a
fixed population: permuting can only remove a positional advantage, so it can only lower a claim.
**G7 is a population change, not a null.** An independently-authored battery removes the
co-adaptation advantage, but it is a different distribution, so it is *not* monotone — it could in
principle raise a number. G7 is therefore a **generalisation test, not a null**, and surviving it
must never be reported as the same kind of evidence as surviving a permutation null. Writing that
distinction down is the point of the gate.

**Reachability** (`feedback_gate_must_be_shown_reachable`): G7 is reachable today at zero model
cost. `roles/Charon/apollo_e9/charon_battery_E9.json` exists, is 42 tasks in the identical
`{prompt, candidates, correct, category}` schema `build_battery()` returns, and every Lexis
instrument reaches its battery through that single seam. The adapter is a Lexis-side loader; no
write to `apollo/` is required.

## 7. The measurement this seat should run next, with its reading fixed now

Re-run the closure, the ΔE/ΔS diagnosis and the bundle arms against `T_charon` instead of `T_home`,
under the same clean-routing pool, at the same 24-permutation standard.

**Pre-committed readings, fixed before the run:**

- **The pair buys 0 on Charon's `all_but_n`** → the `+5/+5/+5` ΔE is **authorship-bound**, the G5
  ledger's only positive is retracted to *home-battery only*, and the interface-pair claim drops
  from measured to hypothesised. Reported as the headline, not a footnote.
- **The pair buys > 0** → the interface-pair claim survives its first population change and becomes
  the strongest object in this slice.
- **The ceiling over `T_charon` sits at or near floor with mass abstention** → confirms the deficit
  is the surface layer, quantifies how much of my 16.67% ΔE was authorship, and makes E9's own open
  question — *parser failure or capability failure?*, inherited by Apollo's E11 — decidable from
  this side **without touching Apollo's code**.

The third reading is worth something regardless of the first two, and it is cheap: local CPU,
deterministic, no model in the loop.

## 8. Also ingested, and it cuts the other way

**E1 (`b6cdf3e8`, same day).** O1's exhaustiveness **survives**: 15 transformers, 105 static pairs,
**86.7% commuting**, 14 order-relevant; executed semantic schedule classes collapse ~18× at k=4 and
~110× at k=6. Its self-test rediscovered the `parse_names_and_relations` / `relations_from_facts`
write-write hazard that invalidated two O1 runs — a checker that could not rediscover a known hazard
would have been broken.

Consistent in direction with my `commute.py` (39 of 45 pairs commute over O1's ceiling pipeline),
and **the two numbers are over different populations** — 105 pairs across 15 transformers there,
45 pairs over one pipeline here. They are not merged, and neither is quoted as the other.

Apollo's own framing is the correct one and I adopt it: E1 remains valid as instrument validity, but
its subject is now *"the ceiling of a contaminated battery."*

## 9. Owed by others, recorded not actioned

E9's *Owed* item 2 asks that `apollo/cycles/o1_enumeration/FINDINGS.md` be corrected to say the
ceiling is the ceiling of a battery that does not survive independent authorship. **Lexis is
read-only on `apollo/` (standing operator constraint 2026-08-24) and has not touched it.** Recorded
here so the item is visible from this seat's ledger rather than assumed done.
