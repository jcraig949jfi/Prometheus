# LEXIS G7 HANDOFF — what is frozen, what is negative, what a consumer does with it

**Seat:** Lexis · **Date:** 2026-09-01 · **State after this document:** IDLE.
**Governing prompt:** `PROMPT_CLOSEOUT_2026-09-01.txt` (authoritative; body sha256
`91fbd86bfeb73af2c0c65838a4a5345424fb0469dfdff31e90cb4ad156f7a35d`).
**Verify everything here without model judgment:** `python roles/Lexis/handoff/verify_handoff.py`
(exit 0 = all artifacts reproduce byte-identically and every frozen number below is asserted).

---

## 1. Frozen claims (the record of evidence; do not inflate)

Measured, deterministic, local CPU, read-only on `apollo/`. Rows: `../notes/g7_charon_result.json`,
`../notes/product_ceiling_clean.json`, `../notes/bundle_test_result.json`.

- Apollo home ceiling of the clean pool: **100/120 = 0.8333** (joint BFS exhausted).
- Charon ceiling of the same pool: **2/42 = 0.0476** (exhausted; 1 of the 2 permutation-robust).
- Charon decomposition under the production organism: **ΔS = 0, ΔE = 40/42**.
- **15/42** Charon tasks completely unrecognised (no clean-pool operator changes the initial state).
- **19/42** reach only number extraction (`parse_numbers` is all that fires).
- **34/42** therefore fail before the capability layer is exercised.
- The frozen pair `lexis_op_subtract` + `lexis_score_by_value_match__g`:
  - each primitive alone: **+0** (home and Charon, all three ledgers);
  - together: **+4/6** on Charon `all_but_n` (+5/5 at home);
  - survives all **24** candidate permutations on every credited task;
  - primitives committed **before** the blind battery entered the repo
    (`043dc92ac` 02:20, `30b96a91e` 06:49 vs `5097b0c8f` 09:36, all 2026-08-25);
  - also converts **two** `all_but_n` abstentions into wrong guesses (Charon 22, 23: the
    prompt asks for the complement).

**Permitted description of the pair:** MEASURED ACROSS TWO AUTHORS / ONE INDEPENDENT AUTHORSHIP
CHANGE. Not "generally transferable", not "generally useful", not "promoted", not "admitted".

## 2. Negative evidence found during closeout (first-class; not repaired)

These came out of building the consumer-level acceptance test the prompt asked for. Every one is
in `consumer_utility_result.json` and asserted by `verify_handoff.py`.

1. **The pair, dropped into the production organism, regresses the home battery.** The compute
   primitive alone flips **9** home synth `two_stage_count` tasks CORRECT→WRONG when placed after
   the organism's transformers (the same 9 under `readout_last` and `readout_first`; **9 on all 5
   hash-seed draws**). Mechanism, read from source: **write-write hazard on the reused `max_value`
   slot**. `op_aggregate_quantities` writes the box total; the compute primitive overwrites it with
   (max − second max); `score_by_aggregate__g`, guarded on `counts`, routes the wrong value. The
   primitive's docstring calls the slot reuse deliberate. That reuse is the defect.
2. **A `compute_first` placement orders around it** (`parse_numbers, compute, T…, S…, readout`):
   +5 CORRECT, 0 WRONG on every draw, because `op_aggregate_quantities` then overwrites the
   compute value on box tasks. The hazard is not removed. Placement is the consumer's decision and
   must be re-measured on the consumer's own organism.
3. **Charon, organism level, is 4 correct / 3 wrong, not 2.** The third is task 11
   (`numeric_stated_premise`: "240 per minute … 45 seconds" → 240 − 45 = 195, and Charon placed
   195 among the distractors). The pair fires on any two-number prompt whose difference is a
   candidate.
4. **Break-even on Charon is exactly L\* = 4/3** for payoffs (1, 0, −L). The pair helps under
   (1, 0, −1) by +1, hurts under (1, 0, −2) by −2 and under fail-closed (1, 0, −5) by −11.
   Under "answer rate" (1, 0, 0) it looks like +4, which is what reach/ceiling silently assume.
5. **The home battery is not one object.** Its `synth` subset (tasks 50–79) is redrawn with
   `PYTHONHASHSEED` (the generator samples names through a set). The ceiling and the P1 control
   are draw-invariant; per-task home numbers are not. Artifacts pin seed 0 and carry a 5-seed
   sweep. This is a hidden dependency of *every* home number in the Lexis slice.
6. **Why the ceiling instruments did not show 1–4:** the joint BFS reports the best program in the
   closure, which is free to order around the hazard and to not fire the pair where it hurts. A
   fixed organism is not.

Nothing above was repaired. No complement/polarity primitive, no parser patch, no fresh slot, no
re-tuning against Charon's battery.

## 3. Exact limits of inference

- Two authors is two. G7 is a population change, not a null; it is not monotone; it moved a claim
  upward once. It licenses "survived one authorship change", nothing wider.
- Charon's battery is **spent for Lexis** (read 2026-08-27, measured 2026-09-01). Anything designed
  after that date by this seat cannot claim G7 on it. The pair can, by timestamp.
- n = 6 per Charon category. +4/6 and 3 wrong are counts, not estimates with intervals.
- The `+5` at home and the `+4` on Charon are ΔE on `all_but_n` only; every other category is 0
  under every arm on both batteries.
- The state-injection fixture's oracle states are authored from Charon's gold; the fixture
  self-check proves the paths are mechanically live, it is **not** the experiment and reports no
  P(solve | oracle) as a result.
- Category labels are docstrings: Charon's `numeric_stated_premise` is products; the home
  category of the same name is "which number is larger". Same label, different verb.

## 4. What is consumable, file by file

- `interface_pair_manifest.json` — the frozen pair: sha256 + git blob of the source file, the
  three commits and timestamps, reads/writes/preconditions, output semantics, why each alone is
  zero, why the pair is complementary, all failure modes above, and the prohibitions.
- `lexis_pair.py` — `load()` imports the two ops and **refuses if the source hash drifted**;
  `augmented_program(placement)` builds the production organism + `parse_numbers` + the pair in
  `readout_last`, `readout_first`, or `compute_first` order. Nothing is registered anywhere.
- `state_injection_fixture.json` — 42 tasks (keyed by Charon's original index; `g7_sorted_index`
  maps to the G7 rows) with: category, prompt, candidates in original order, correct answer and
  slot, Charon's length/position flags, recognition (which operators fire at the initial state,
  closure size, unrecognised, number-only), baseline outcome and whether it was a positional
  fallback (task 15), ΔE/ΔS class, reachable/robust with and without the pair, and the **oracle
  semantic state per injection level** with the existing operators to run after injection.
  Summary: parsed-level path exists on 9 tasks (all 9 self-check true), no consuming operator on
  22, no slot on 11; derived-level path exists on 39 (all 39 self-check true), no slot on 3;
  **13 of the 39 derived paths are `readout_only`** (a boolean one string match from the answer:
  all `vacuous_truth`, all `consistency_check`, transitivity 16) and must be reported apart.
  What each task can discriminate: A-vs-rest 9, B-vs-C 17, C-only 13, nothing 3.
- `consumer_utility.py` / `consumer_utility_result.json` — CORRECT / ABSTAIN / WRONG per task,
  transition matrix, utility under four payoff triples plus any the consumer passes on the command
  line, break-even penalty, both batteries, five arms, 5-seed home sweep.
- `ADMISSION_PROTOCOL.md` — six stages, who owns each, what a manifest must carry, what happens to
  a rejected artifact.
- `build_handoff.py` / `verify_handoff.py` — deterministic build; byte-identity verification.

## 5. Consumer instructions

**Intended first consumer:** Apollo Gen-2, whose charter (`roles/Apollo/CHARTER_GEN2_serendipity_
20260901.md` §"Task 2 — state injection") lists exactly this experiment as OWED with three
preregistered arms (A raw, B oracle injection, C corrupted injection), and whose `STATUS.txt`
records it as `Task2 state-injection OWED`. Apollo's revival packet (`apollo/pivot/
APOLLO_REVIVAL_REVIEW_2026-09-01.md` §7) names it the cheapest discriminating experiment on the
board. No substitution: the lane exists in the live repo and is unstarted.

**The experiment, made executable by the fixture:**

> If the surface layer is bypassed and the correct semantic state is injected, can the existing
> substrate solve the task?

For each of the 42 tasks, per injection level with a `PATH_EXISTS` status:

1. Arm A — raw prompt through KNOWN_0833 (reproduces E9: 2/42, 40 abstain).
2. Arm B — build `BlackboardState(prompt, candidates)`, set the slots in
   `injection.<level>.slots`, run the operators in `then_run`, score.
3. Arm C — consumer-owned corrupted injection of the same shape (swapped relation direction,
   off-by-one count, negated boolean); the gold must NOT come out. A level whose corrupted arm also
   scores is an answer leak, not a capability.
4. Report `readout_only` rows separately from the rest, always.

Readings, fixed here: parsed-level solves → **A, surface**; parsed level has no consumer or fails
and derived-level solves → **B, capability**; derived-level fails or exists only as
`readout_only` → **C, readout**. Per category the fixture already says which of these it can
separate; `numeric_comparison` is the case the prompt flagged — Apollo's home readout for it
selects yes/no, Charon's candidates are entity names, and the only clean readout that can select a
name is `select_nth__g` over an injected ordering (5 of 6 tasks; the equality task has no slot).

**Then, for the pair,** run `python roles/Lexis/handoff/consumer_utility.py --battery both
--loss <name>=<c>,<a>,<w>` with the consumer's own payoffs, on the consumer's own organism if it
differs from KNOWN_0833, in the placement the consumer would actually use. Admit, reject, or
shelve under `ADMISSION_PROTOCOL.md` stage 5. Lexis does not vote.

## 6. Reopening criteria (what would wake Lexis)

Any one of:

- a consumer trial shows a Lexis artifact changed the consumer's held-out objective under its
  actual error cost, and the consumer wants the next gate run;
- a consumer hits an admission ambiguity a Lexis gate resolves (ΔE vs ΔS ledger, permutation
  robustness, authorship independence, congruence);
- generalisation uncertainty is the stated blocker to a deployment decision, and the consumer says
  a second blind battery would change that decision;
- an independent blind battery exists for reasons unrelated to Lexis.

## 7. What keeps Lexis idle

- no consumer runs the fixture or the acceptance test;
- the consumer rejects the pair;
- the pair's improvement disappears under the consumer's wrong-answer cost (it already does at
  L ≥ 4/3 on Charon and under every loss at home in the placements that clobber `max_value`);
- state injection reveals a capability failure in the compute layer unrelated to Lexis's
  interface work.

## 8. Hidden dependencies found, and what was done about them

1. **`numbers` is not written by the production organism.** The compute primitive reads `numbers`;
   `parse_numbers` is in Apollo's registry but not in KNOWN_0833. The consumable unit relative to
   that organism is `parse_numbers` + pair. *Fixed in the loader (`augmented_program` inserts
   it); stated in the manifest.*
2. **`max_value` write-write hazard** (§2.1). *Documented, measured in three placements, not
   repaired.*
3. **`PYTHONHASHSEED` redraws 30 of 120 home tasks.** *Build re-execs under seed 0; verifier runs
   subprocesses under seed 0; 5-seed sweep recorded; stated in the manifest and ROLE.md.*
4. **Hash pin must be line-ending-normalised** or a CRLF checkout refuses the frozen pair. *Fixed
   in `lexis_pair.py` and `verify_handoff.py`.*
5. **`select_nth` has no `last`** (`parse_ordinal` emits `last`; `select_nth` indexes only
   first/second/third/fourth/fifth/tallest/largest/biggest/shortest/smallest). *Not touched; the
   fixture spells index −1 as `smallest` and says so per task.* Recorded for Apollo; not a Lexis
   repair.

None of these became a research programme.
