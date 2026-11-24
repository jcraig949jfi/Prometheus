# UNADJUDICATED

# Review of the Prometheus Strategic Reset (2026-11-22) — Claude Fable 5.2

Reviewed: `STRATEGY_AND_EXECUTION_PLAN.md` and `REVIEW_PACKET_FOR_FABLE_AND_ASTRA.md`, 2026-11-22.

**Conflict of interest.** I wrote the `rsi-bakeoff/fable-5.2` design that the plan salvages as Arm 1. Section 8
recommends cutting most of it from Phase 2; weigh that with the conflict in mind.

**Condition differs from Astra's.** The packet says no repository access is needed. I had access and used it.
Several findings below exist only because I did, which is itself a finding about the packet (section 0).

## Verdict: MODIFY

| Part | Call |
|---|---|
| Diagnosis (W1–W3), asset triage, three roles, LLM-off-at-eval contract, Claim A / Claim B split | AGREE |
| Phase 0 | AGREE, one addition |
| Phase 1 on the critical path | KILL as a gate; run the Hecate completion in parallel; move the gravity detector to just before Phase 4 |
| Phase 2 as specified | MODIFY heavily: arms, gate and scope are all wrong in ways that produce an unreadable result |
| Phase 3 default (Track 3A) | DISAGREE: 3B |
| Phase 4 | AGREE that it stays gated and unspecified |

The inversion is the right bet. The plan as written will not test it: Phase 2 can pass for a reason that is not
crystallization and can fail for a reason that is not science.

## 0. What I checked, and three places the packet misleads a reviewer without repo access

Confirmed: `origin/main` is `9884ac934`; the census line (75 seats, 54 dormant, 52 anomalies) is commit `5633cc02a`;
both bake-off branches exist at the cited commits; the cited assets exist on `origin/main`; "13 of 18 historical
defects" is in `rso/registry/entries.py`. Hecate's quoted numbers match `hecate/alien/REPORT_pilot.md`.

Not checked: the eight composition-wall counts, the file-count figures, and the "58 passing tests" (I did not run
the suite).

Three omissions change the review. Fix them before the packet goes to Astra.

1. **Hecate's own verdict on LLM detectors is left out.** The packet reports that Opus 5.5 "did not collapse
   unfamiliar lawful systems to noise" (true). It omits the report's frozen decision
   `NOVELTY_DETECTOR_NOT_VALIDATED`, that the model labelled 19 of 30 incompressible nulls RULE and 24 of 30
   COHERENT, and that it called 16 of 32 aliens FAMILIAR at the level of formalism. The report concludes novelty
   conclusions "must rest on behavioural and predictive tests ... never on LLM classification alone." Phase 1's
   Gravity Detector is LLM classification alone. The repository already holds evidence against the Phase 1
   instrument, and Astra will not see it.
2. **Beta-04's frozen labels are left out.** The packet gives the 13–15/15 figure with its conditions. It omits
   `TFS1_INSTRUMENT_QUALIFIED = NO`, `WORLD_DEMAND_QUALIFIED = NO` (5 of 12 worlds), that the admitted set is 15
   families from 2 kind pairings and 5 skeletons, and the fallback-off rows: 0 of 15 frozen, 9 of 15 with both
   repairs — **with the decomposition supplied**. Phase 2 asks for 30 families with fallback off and no
   decomposition.
3. **The bake-off branches contain no engine.** Each is design documents (mine adds one probe script). "M0
   (~1,800 LOC)" is my estimate for unbuilt code, tests included, over two weeks. And M0 is a rewrite-law miner
   only: it has no library. The plan's Arm 1 row says it yields `(L, T)`; it yields `T`.

Minor: the plan cites `CONSTITUTION.md` for the North Star. That file is not on `origin/main`, which is where
Phase 0 branches from.

## 1. Overall (Q1)

MODIFY. Highest-ROI version: Phase 0, then a two-day headroom gate, then a one-week Phase 2 with different arms
(section 4), then Track 3B. Phase 1 leaves the critical path.

## 2. The compiled-priors critique (Q2)

Phase 1 plus Phase 4 does not address it; it postpones it by seven weeks. But the trap is directly measurable in
Phase 2 at almost no cost, and the plan does not measure it.

**Add arm `PRIOR-ONLY`:** the same frontier model proposes a library and laws from the TFS-1 language
specification alone — no dev tasks, no traces, no KillVectors. Same verification, same budget, LLM off at eval.

- `MG-UNPLUGGED` ≈ `PRIOR-ONLY`: nothing was distilled from experience. The model wrote down the list-function
  library it already knew. That is compiled priors, measured, in week 1.
- `MG-UNPLUGGED` > `PRIOR-ONLY` on held-out families: experience contributed. Only this difference is evidence
  for Claim A.

Without this arm, Claim A cannot be distinguished from "frontier models know `map` and `fold`". An integer-list
DSL is close to the worst case for this: it is where model priors are most saturated.

Does the inversion compromise the North Star? Not fatally, provided the claim is kept at "experience-derived
content beyond the prior", and provided Phase 3 moves to a domain where priors do not saturate (section 7).

## 3. Phase 1 (Q3): cut from the critical path

1. **It gates nothing.** G1 reads "Done (either branch informs Phase 4)". Four of the first fourteen days are
   spent on a result consumed in week 7 or later, on a different artifact type (evolved programs, not prose
   mechanism hypotheses), probably by different model versions. That violates the plan's own sequencing rule in
   spirit.
2. **The thresholds are noise.** At 50–64 specimens, "≥5%" is three specimens against two. G1-A and G1-B are
   separated by one specimen.
3. **G1-B overclaims.** "Establishes empirically that LLM generation alone cannot escape human ontology" from
   about 60 concept triplets exceeds the pilot document's own limit: "A low-gravity result is not a novelty
   claim", and no single authoritative score.
4. **"Genuine 3-way causal knockout sensitivity" is never run.** The specimens are prose. The knockouts are the
   generator's assertions about its own text.
5. **The calibration set cannot separate alien from underspecified.** It has familiar, disguised-familiar,
   composite and nonsense controls. It has no positive control for the target class: lawful, well-specified,
   unfamiliar. Hecate's executable aliens are exactly that and already exist.

**Sharpest falsifier for the detector** (if it is run at all): a specification dose-response. Take the disguised
familiar controls and delete structure in steps. If "unexplained residual" rises as specification falls, the
detector measures underspecification and is void. Add Hecate aliens, blinded, as the lawful-unfamiliar positive
control. Note the 75% bar is 6 of 8 controls.

Keep: the Hecate Gemini and third-family completion. It is behavioural, costs under $5 by the report's estimate,
and can run in the background.

## 4. Phase 2 (Q4, Q9)

Keep TFS-1, for one week at most, behind a headroom gate. Jumping straight to a real domain throws away a working
kernel and cost meter; staying as specified produces an unreadable result. Five specific defects:

1. **Floor risk, and a gate that cannot fail.** The best known configuration reaches 9 of 15 with fallback off
   *and* the decomposition supplied. Under G2's conditions `BASE-OE` is plausibly at zero. Then "≥2× more
   families than BASE-OE" is satisfied by one lucky solve, or every arm scores zero and KILL fires on a floor
   effect that says nothing about the mechanism. No eligibility count is frozen.
2. **Scope.** Five arms, an API harness, 30 qualified families, RSO registration and ledgers, in nine days and
   2,500 lines. My estimate for Arm 1 alone was 1,800 lines and two weeks. This is the most likely week-2
   flatline, and it is the W3 pattern: plumbing overruns physics.
3. **Arm 1 is confounded and is probably not the strongest baseline.** M0 has no library, so Arm 1 against Arm 2
   varies proposer identity and artifact type together. I also put "a mined theory beats per-task OE pruning" at
   40%, with three failure reasons rated High. `BASE-OE` may be the stronger no-LLM arm.
4. **The knockout is near-tautological.** Remove primitives the solutions call and performance falls. Scrambled
   laws are unsound laws, which break search for a trivial reason. The control that can fail is a size-matched,
   sound-but-irrelevant artifact: TFS-1 already has random-library and shuffled-history arms in `e3/organism.py`,
   and an LLM library proposed for a different task distribution is a second.
5. **G2 is not a decision rule.** Criterion 1 accepts either arm; criteria 2 and 3 name only `MG-UNPLUGGED`;
   PARTIAL overlaps PASS; outcomes such as "MG beats BASE by 1.5×" or "MG beats BASE but loses to SHADOW" map to
   nothing. "≥5× lower median hitting cost on solved families" compares different solved sets across arms. No
   seeds are specified; Beta-04 moved 7 / 9 / 8 across three.

**Single most likely counterfeit positive (Q9).** A frontier model proposes list primitives; a second frontier
model authors "fresh" list tasks. Both draw from the same human distribution of natural list functions.
Cross-family does not break a shared training corpus. The proposer anticipates the author, the primitives are
genuinely used, knockout passes, the adversary finds no leakage because there is none in the ordinary sense. It
looks like transfer and is prior-matching.

**Patches, before Day 1:**

- Day 1–2 headroom gate, treatment arms not yet run: hand-built depth-1 and depth-2 reference artifacts, used as
  instruments only. If depth-2 does not beat depth-1 on the admitted families, TFS-1 has no second level; skip to
  Phase 3 rather than repair the world.
- Arms: `BASE-OE`; `ZERO-LLM-LIB` (TFS-1's existing compress/promote path — near-zero new code, and a like-for-like
  comparison); `MG-UNPLUGGED`; `PRIOR-ONLY`; `SHAM` (size-matched, sound, irrelevant). Naked prompting is
  reported, not gated (section 5).
- Half the held-out families generated procedurally (random composition over the primitive set, no model in the
  loop), and results reported per stratum. A gain present only on model-authored families is the counterfeit.
- A frozen truth table over all arm orderings, an absolute floor ("BASE-OE solves at least k and at most m of N"),
  a common opportunity set, at least three seeds, paired.
- State in advance what a pass licenses: "the harness is sound and the artifact is not cargo." Not "crystallization
  works."

## 5. The amortization rule (Q5)

There is no single honest ratio, because the answer is a function of N. Report the function:

- Convert CPU to dollars at a rate frozen before the run.
- Publish the break-even count `N* = C_sleep / (c_naked − c_unplugged)`, with per-task costs taken on the common
  set of families both arms solve, and report the solve sets separately.
- The claim permitted is "crystallization pays for deployments larger than N*", and only if N* is smaller than the
  suite actually run, so the crossing is observed and not extrapolated.
- Fix N before the run.

More important: this comparison answers an economics question, not the Sagacity question. A naked frontier model
will solve most small integer-list tasks from examples at trivial cost, so criterion 2 can sink G2 for a reason
unrelated to the thesis. Demote it from gate to reported number. It belongs as a gate in Phase 3 (the
weaker-model transfer test), where tasks are hard for a naked model.

## 6. Held-out qualification (Q6)

Four mechanical checks per family, all on existing code, no tribunal:

1. **Solvable:** the author submits a witness program; the kernel verifies it on sealed tests. No arm sees it.
2. **Non-trivial:** `BASE-OE` from scratch fails at the evaluation budget, and the foundry's existing null ladder
   (`nulls.py`) fails.
3. **Order-2:** `BASE-OE` solves it when handed both witness stones as primitives and fails with either alone.
4. **Not motif-collapsed:** at most three families per witness-skeleton pair.

Over-generate about 90, admit the first 30 that pass, report the admission rate. If fewer than 30 pass, that is
the headroom finding and it arrives before any treatment arm runs. Freeze the eligible count then.

## 7. Phase 3 domain (Q7): 3B, exact circuit synthesis

3A is the domain where the compiled-priors objection is strongest: every rewrite rule over symbolic algebra is in
a textbook or in the e-graph literature. Its verifier (a "bounded counterexample battery") admits unsound laws,
which I flagged as a live risk in my own design. OEIS and LMFDB bring back the Era-1 data plumbing.

**Pick:** minimum-size Boolean circuits over a fixed basis (AND / XOR / NOT), exhaustive truth-table verifier,
gate count as the metric.

- **Calibration slice:** all 4-input functions by NPN class, where exact optima are tabulated.
- **Training slices:** 4- and 5-input functions.
- **Held-out hard slice:** 6- to 8-input and multi-output arithmetic (adders, small multipliers, popcount, small
  S-boxes), scored against best published sizes.
- **Why it fits:** the library is reusable subcircuits; multi-output targets require sharing, which is where
  compounding would show; held-out targets can be sampled at random, so no model authors them and the foundry
  problem disappears; human priors help but do not saturate; Phase 4's non-LLM evolution has a natural home.
- **Mandatory baseline:** an off-the-shelf synthesis tool (ABC-class optimisation, and SAT-based exact synthesis
  where it terminates) at matched wall time. Beating enumeration but not ABC is a counterfeit.

The tabulated-optima and best-known-size facts are from memory; verify them before freezing. My honest estimate
of a real compounding win over that baseline in four weeks is low, perhaps one in five. It is still the domain
where a win would mean something.

## 8. Bake-off triage (Q8)

Fair in direction; inaccurate in detail.

- "Not as a standalone bet ... which Fable 5.2 itself rates at 8–20%" mixes numbers. Mine were 40% for a
  first-order M0 gain, 40% for M1 self-modification, 20% for two-generation recursion, 8% for transfer.
- **What M0-only loses:** the library–theory loop, law templates, inverse laws and the CLAMP test (machinery
  helps search but is withheld from the improver). That is everything that made the design about recursion. M0
  alone is, in my own words, "a search with a learned cache".
- The PARTIAL branch ("scale M0/M1 into Phase 3!") skips my gate W3 (does a second level exist in the world?) and
  ignores that nothing in the design fixes stone acquisition (my failure reason 5).
- **My recommendation: remove M0 from Phase 2.** `ZERO-LLM-LIB` is the cleaner control and is nearly free. If a
  zero-LLM theory miner is wanted, run only M0-E0/E1: task-free, about an hour of CPU, exact numbers.
- Worth carrying forward from my design: one work meter from the first line, the common opportunity set, the
  MATCHED arm, the break-even count, CLAMP for Phase 3's compounding claim.
- Opus 5.5's RLL: I read only its executive verdict. It recommends building a scoped M0 at 3–4 engineer-weeks
  and up to 800 core-hours; the packet's summary ("concluded no-LLM compounding recursion is unsupported") I did
  not confirm. Deferring the DSL is right. Its blank-state (`θ₀`) acceptance is the correct test for G3: accept a
  generation only if its gain survives evaluation from a blank knowledge state at matched compute.

## 9. Operating contract and Phase 0

- The 70/30 rule has no meter. Either define one (lines or commits by directory) or drop it; an unmeasured rule
  is the kind of ceremony the plan is trying to remove.
- Phase 0 addition: find what is still writing `auto: portfolio update` and census commits to `origin/main` as of
  11-13. Disabling "cron loops" assumes the source is known.
- Three roles with a cross-family adversary: agree. Note the adversary both authors held-out families and reviews
  for leakage; the procedural stratum in section 4 is the check on that concentration.

## 10. What I would cut (Q10)

1. Phase 1 as a gate (four days).
2. Arm 1 (M0) from Phase 2.
3. The `SHADOW-NAKED` criterion from G2.
4. Tracks 3A and 3C as options: choose 3B now so Phase 2 is not designed around a later choice.
5. All Phase 4 detail beyond one sentence. It is two gates away.

Resulting critical path: Phase 0 (day 1) → headroom and eligibility gate (days 2–3) → five-arm TFS-1 run
(days 4–10) → 3B.
