# AMA — Preregistration: the A0 baseline and the navigation comparison

**Registered:** 2026-08-25
**Protocol version:** v0.1-alpha
**Status:** frozen before any epoch is played
**Binding on:** conditions A0, B, C, D and every comparison between them

This document exists because the rulebook, as written, could not be falsified.
It defines a primary metric — expected verifier cost to reach a correct
disposition on an unseen claim — and a navigation experiment in which condition
D must beat controls, but it does not require the controls to be measured before
the graph exists. Play first and measure later, and there is no uncontaminated
baseline left to measure against; the comparison quietly becomes unfalsifiable
after the fact.

Nothing below may be changed once A0 has been run. Changing it forks the
protocol version and the prior data does not carry over.

---

## 1. Sequencing (binding)

1. **Build the problem/evaluation generator.** It creates and seals problems and
   their truth/oracle metadata. Player-visible material and oracle metadata live
   in separate files with separate permissions; no player prompt is ever
   assembled from an oracle file.
2. **Calibrate the scoring machinery** against sealed calibration claims
   (section 5). This is an instrument check.
3. **Run and freeze A0.** Fresh-context assessors, problem and claim only.
4. **Then play AMA.** Accumulate attacks, defenses, bypasses, repairs.
5. **Later, replay matched held-out samples under B, C, D.**
6. **Only after the manual protocol works**, automate the hourly loop.

The hourly runner is not built until step 6. An arena that automates before it
can measure itself just generates contaminated data faster.

**A0 must be run against an empty graph.** The SHA-256 of `state/graph.jsonl` at
A0 launch is recorded in the A0 result file and must equal the hash of the empty
file. This is the evidence that no play preceded the baseline.

---

## 2. Evaluation sets are disjoint from play, and disjoint from each other

The reused-held-out-set hole: if A and D are scored on the *same* claims, and
the arena played in between, the graph can indirectly memorize the evaluation
set. The memorization need not be verbatim — a defense written against a played
claim that happens to be an evaluation claim transfers the answer without ever
quoting it.

Binding rules:

- **A frozen generator emits all evaluation claims.** Generator source, seed,
  and parameter vector are committed before A0 and never edited during a
  protocol version.
- **Evaluation claims never enter play.** The play pool and the evaluation pool
  are drawn from the generator into separate directories. No evaluation claim,
  its verifier, its witness, or its oracle record may be read by a player seat,
  cited in a submission, or merged into the graph. Ever.
- **Each condition gets its own matched sample.** `EVAL_A`, `EVAL_B`, `EVAL_C`,
  `EVAL_D` are disjoint sets drawn i.i.d. from the same generator, same
  parameters, same difficulty strata, same defect-family mix, different seeds.
  They are matched by *construction*, not by pairing.
- **Mutation holdout.** The defect families are split before play into a play
  pool (M1–M8) and a sealed holdout (M9–M12), frozen in
  `generator/MUTATION_SPLIT.json`. Holdout families never appear in an item any
  player sees during play. Without this, D beating C could mean nothing more
  than that the graph contains a worked example of every defect type in the test
  set. The holdout also makes Purple's promotion bar operational: a defense is
  promoted when it catches an attack drawn from a pool frozen *before the
  defense was written*, rather than when Purple declares the new attack
  independent.
- **Three transfer cells**, declared in `generator/PLAY_SCOPE.json` before play:
  same mutation on a new problem (basic reuse), new mutation in a played domain
  (abstraction), new mutation in an unplayed domain (the interesting one).
- **Consequence, stated up front:** this is an unpaired comparison and therefore
  has less power than reusing items. That cost is accepted. The alternative —
  paired items with a contaminated graph — buys precision on a quantity that is
  no longer the quantity of interest.
- Strata are balanced across sets: each set contains the same count per
  (domain × defect-family × difficulty) cell.

---

## 3. Primary metric, defined before any data exists

For a single assessment run on evaluation claim *i* under condition *X*:

- `correct_i` = 1 if the returned disposition equals the oracle disposition,
  else 0. `UNRESOLVED` is correct exactly when the oracle marks the claim
  undecidable within the frozen budget, and incorrect otherwise.
- `cost_i` = verifier + solver invocations consumed. **If `correct_i = 0`, the
  run never reached a correct disposition, and `cost_i` is set to the full
  budget cap `BUDGET_VERIFIER_CALLS`.**

That last convention is load-bearing and is fixed now specifically so it cannot
be chosen later to suit a result. Without it, a condition that answers only the
easy claims and abstains-wrongly on the rest posts a flatteringly low mean cost.

**Primary statistic:** `EVC(X) = mean_i(cost_i)` over the condition's evaluation
set.

**Unit of analysis is the claim, not the verifier call.** n = number of
evaluation claims in the set. Standard errors are computed on that n.

Secondary, reported alongside and never in place of the primary:

- accuracy — mean `correct_i`;
- false-accusation rate — `FALSE` returned on claims the oracle marks `TRUE`,
  denominator = count of oracle-`TRUE` claims in the set;
- invalid-falsifier rate — kills whose witness fails oracle re-execution,
  denominator = count of kills submitted;
- unresolved rate, split by whether the oracle marks the claim decidable;
- wall time, output tokens, max search size, artifact code bytes.

**Minimum detectable effect is computed before A0 is run,** from a pilot of the
generator, and written into the A0 result file. A threshold nearer to the
observed value than its own standard error is not a gate. If the achievable MDE
on the planned n is larger than the effect size that would make the arena
interesting, the honest move is to enlarge n or to say so, not to run the
comparison and read the noise.

---

## 4. Parity between conditions

A condition can win for reasons that have nothing to do with graph structure:
more guidance, more compute, more text. All three are controlled.

- **Instruction parity.** Every condition uses the identical common preamble and
  the identical role block. Only the block below `--- CONTEXT PACKAGE ---`
  varies. `prompts/assemble.py parity-check` hashes the condition-invariant
  portion per role and must report `PASS`; the hashes are recorded in each run's
  manifest. Parity is verified mechanically, not asserted.
- **Budget parity.** `prompts/budget.json` is frozen for the protocol version
  and applies identically to every seat and condition.
- **Volume parity between C and D.** Both context packages are capped at
  `CONTEXT_TOKEN_CAP`. Where D's relevant subgraph exceeds the cap it is
  truncated by relevance rank and the truncation is disclosed in the package.
  **C versus D is the load-bearing comparison** — it is the only one that
  isolates graph *structure* from mere retrieval of similar past failures, and
  it is worthless if D simply gets more text.
- A versus D is not volume-matched and cannot be, since A's package is empty by
  definition. A is the absolute baseline; C is the control that matters.

---

## 5. Calibration gate before players are unleashed

Between 20 and 50 sealed calibration claims are generated, balanced across five
named classes. The names are load-bearing — they make the epistemic distinction
explicit in a way "five oracle classes" does not:

- `TRUE_VALID_ARGUMENT` — true, and the argument establishes it;
- `FALSE_WITH_WITNESS` — false, with a counterexample cheap to reach;
- `TRUE_BUT_INVALID_ARGUMENT` — correct conclusion, one planted invalid step;
- `FALSE_BUT_HARD_WITHIN_BUDGET` — false, but the witness sits deep enough that
  naive search inside the budget will not reach it;
- `UNRESOLVED_WITHIN_BUDGET` — truth known to the sealed generator, player-side
  budget deliberately insufficient to establish it.

The last class is **operational, not Gödelian**. Nothing undecidable is imported
into the alpha; the generator simply enumerates under a budget the player does
not have. Its truth status is balanced 50/50 by construction, so guessing the
truth value gains nothing on the one class built to measure calibration.

`TRUE_BUT_INVALID_ARGUMENT` is generated **compositionally, never by hand**: a
mechanically certified true claim with a valid derivation, then one mutation
operator applied to one step, then re-verification that the mutated step is the
unique invalid one. Hand-authoring "convincing bad proofs" is not permitted —
it would put a human in the loop on exactly the abstraction this experiment is
meant to test for.

Scripted mock submissions of each type are fed to the scorer, together with a
**bogus falsifier** — a kill whose witness does not actually break the claim, or
lies outside the quantified domain. The gate passes when the scorer's confusion
matrix against the oracle is diagonal across all five classes and both bogus
kills are rejected by re-execution rather than by assertion.

**Passing this gate is an instrument calibration, not evidence the game works.**
It shows the scoring machinery can tell the five outcomes apart on synthetic
input it was built to handle. It says nothing about whether live agents produce
anything worth scoring. Do not report it as a result.

---

## 6. Problem selection for the alpha

Choose domains where the oracle is unambiguous and cheap, not domains that are
impressive. We are debugging the epistemic game, and every hour Purple spends
discovering that our oracle is ambiguous is an hour it is not spending catching
reasoning defects.

Admissible for the alpha:

- finite combinatorics;
- modular arithmetic;
- integer identities and inequalities with bounded counterexamples;
- graph properties on small graphs;
- small recurrence claims;
- elementary number theory;
- polynomial identities.

Inadmissible for the alpha: anything whose truth depends on an open conjecture,
anything requiring a proof assistant to settle, anything where the natural
statement has two defensible readings, anything whose verification cost exceeds
the frozen budget.

**Every problem ships with an independent oracle** — a decision procedure that is
not Red's verifier and does not share code with it. A problem whose oracle is
Red's verifier cannot detect solver-encoding mismatch, which is one of the
defect families we most want to catch.

---

## 7. First playtest is homogeneous

Four fresh instances of the same model (Opus 5) for the first playtest.

This removes model capability as a variable while we find out whether the *rules*
work. Heterogeneous Opus/Sonnet/Fable/Codex tournaments become interesting only
after the arena has survived a homogeneous run — at that point a difference
between models can be read as a genuine ecological niche (better deceiver,
cheaper falsifier, better auditor, better defense writer) rather than confounded
with a bug in v0.1.

Model identity is recorded privately per seat and withheld from opponents in
both regimes. Note that homogeneity also removes stylometric attack as a
confound for the first run, which matters because "successful attacks mostly
exploit model/style fingerprints" is a declared kill condition.

---

## 8. What result would kill the navigation claim

Declared now, so it cannot be renegotiated later:

- `EVC(D)` not lower than `EVC(C)` by more than the MDE → **the graph adds
  nothing beyond nearest-failure retrieval.** This is the primary kill.
- `EVC(D)` lower than `EVC(C)` but with a higher false-accusation rate → D bought
  cost reduction with credulity, not navigation.
- `EVC(B)` matching `EVC(D)` → generic falsification guidance is doing the work;
  the arena's specific history is decorative.
- Graph size growing while `EVC` stays flat → the arena has recreated the
  original problem in graph form.
- Defenses failing on fresh agents, or failing cross-domain → no transfer.
