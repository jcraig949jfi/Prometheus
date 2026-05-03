# Three-Arm Pilot — The Substrate's First Empirical Anchor on Bottled Serendipity

**Date:** 2026-05-03
**Source:** Trial 3 design (`pivot/ergon_learner_proposal_v8.md` §4) + Ergon session journal addendum (2026-05-03)

## What the pilot tests

Trial 3 of the Ergon MVP runs three operator classes in parallel against the same discovery environment, the same falsification battery, and (when the null-world generator ships) the same null world:

- **Arm A — Uniform random.** Strawman null. `random.choice` over typed action space. No selection pressure.
- **Arm B — Structural (Ergon's MAP-Elites).** Quality-diversity archive over typed DAG mutations. Selection pressure from kill-battery survival.
- **Arm C — Symbolic.** Argument-value mutations within type bounds; structurally fixed DAG, different leaf values. Tests whether symbolic exploration alone (without DAG topology variation) is sufficient.

3K episodes per arm = 9K total. Welch t-test + Holm correction on BOTH PROMOTE rate AND signal-class-residual rate.

## Why three arms (and why this matters)

Ergon's pivot doc originally proposed Arm B as a one-week port of the existing MAP-Elites loop onto Techne's Gymnasium env. The role: validate the env's shape. Then v8's Trial 3 promoted this to a three-arm design, and Ergon's 2026-05-03 session journal addendum pointed out the upgraded role:

**The three-arm design is the substrate's first empirical anchor on the bottled-serendipity thesis.**

The bottled-serendipity thesis (Charon's foundational doc, `bottled_serendipity.md`) argues:
- LLM-as-oracle is saturated (the consensus position; $185B/year of Google infra alone confirms it)
- LLM-as-mutation-operator is a different mathematical object than LLM-as-oracle
- Same model, same weights, same training; different role in the search process
- The mutation operator's value is in its **off-modal samples** — specifically the rare ones that land outside the training distribution AND inside the truth
- Without filtration, that fraction is invisible. With filtration, it becomes the product.

This thesis predicts: **prior-shaped mutators (LLMs) outperform uniform random by enough to justify the LLM cost.**

But Trial 3 doesn't include an LLM-driven mutator at MVP scope (that's v0.5+, the `external_llm` operator). What Trial 3 *does* include is:

- **Uniform random (Arm A)** — the strawman null
- **Ergon's MAP-Elites (Arm B)** — structural selection pressure WITHOUT prior-shaping
- **Symbolic (Arm C)** — symbolic selection pressure WITHOUT prior-shaping

So Trial 3 measures: *does any selection pressure (prior-free) outperform uniform random?* If yes → the env is well-shaped, selection works, the substrate is producing real signal. If no → the env's reward landscape is too flat for any selection to produce signal regardless of operator.

**Then v0.5 adds Arm D — LLM-REINFORCE (or whatever Techne's `discovery_env` is using as its prior-shaped agent). The four-arm comparison becomes the actual bottled-serendipity test.**

## What the four-arm test will reveal

At v0.5+, comparing all four arms:

- **D > B with significance:** the LLM prior contributes something selection pressure alone doesn't. Bottled serendipity thesis confirmed at MVP scale.
- **D ≈ B:** mechanical evolutionary search achieves discovery without LLM priors. Bottled serendipity thesis is partially wrong (or: the LLM's contribution is only at scales beyond MVP). Substrate's economics shift dramatically — the LLM mutation cost stops being load-bearing.
- **D > B AND D > A by larger margin than B > A:** the prior is doing more than selection pressure; it's adding novel exploration directions selection alone won't find.
- **D and B both ≫ A:** confirms that ANY structured exploration beats random; doesn't distinguish prior's contribution from selection pressure's contribution.

**Either of the first three results is substrate-grade.** They each tell us something the substrate can act on.

## Acceptance criteria (per v8 §4)

Trial 3 acceptance is three-measurement:

- **Absolute residual density:** signal-class-residual rate per 1K episodes ≥0.05 for at least one operator class
- **Absolute PROMOTE density:** PROMOTE rate per 10K episodes is measurable for at least one operator class (≥1 PROMOTE in 10K episodes for the strongest arm)
- **Correlation residual→PROMOTE:** Pearson correlation between cell-level signal-class-residual rate (averaged over 1K-episode windows) and same-cell eventual PROMOTE rate ≥0.3

The correlation framing answers "do residuals predict promotions" rather than "are they 10× more frequent." Correlation is meaningful even at low absolute rates AND meaningful at high absolute rates — it's the stable measurement.

## Ergon's three pieces of pushback (from session journal 2026-05-03)

When Ergon filed the operator-perspective addendum on the discovery-via-rediscovery unification, three pushbacks landed:

### 1. BIND still bypasses CLAIM/FALSIFY/PROMOTE

The team review of Techne's BIND/EVAL on 2026-05-03 flagged this as the convergent #1 architectural concern. The discovery pipeline can't compound cleanly until BIND routes through the kernel discipline. **Sharpened priority: this week, not "in production."**

### 2. ChatGPT's stage-3 standard is correctly cautious but slightly too lenient

ChatGPT's three-tier validation ladder (rediscovery / withheld / open + null) sets the bar at "agent > null." Ergon argues that's necessary but not sufficient.

The harder bar: **agent's PROMOTE rate uncorrelated with the prior's likely training coverage.** If the agent's "discoveries" cluster in regions the prior already knows well (just not catalog-indexed), the agent isn't discovering — it's surfacing things its prior already implicitly contained.

Candidate stage-3.5 proxies:
- **Permutation-distance** — for each candidate, distance to the nearest training-corpus polynomial. If candidates concentrate at low permutation-distance, the prior is doing the discovery; if they spread across permutation-distance, selection pressure is.
- **Frequency-weighted recall** — measure recall weighted by inverse training-corpus frequency. High recall on rare patterns is the bottled-serendipity signature; high recall on common patterns is the rediscovery-via-prior signature.

Both are computable from existing logs without new instrumentation.

### 3. The mad-scientist-byproduct discipline differs by operator class

Charon's bottled-serendipity thesis includes the "mad scientist principle": a chase produces five byproducts; capture all five; the byproducts are often more valuable than the primary chase.

For LLM-driven exploration, this discipline requires aggressive CLAIM-on-every-side-thought (each context-window flush risks losing byproducts). Per `bottled_serendipity.md`: probably 80%+ of useful byproducts are currently lost to context-window flush.

For Ergon's MAP-Elites, the byproducts are captured **structurally** — every cell in the archive IS a byproduct. The archive's diversity preservation guarantees you don't lose the failed-but-interesting candidates because they fill cells the elite candidates don't reach. Different capture economics.

**Implication:** the mad-scientist discipline should be documented as operator-class-specific. LLM operators need explicit CLAIM hygiene; evolutionary operators need archive diversity hygiene. Substrate-grade observation that wasn't in the original bottled-serendipity doc.

## What Trial 3 ships against

After Days 18–22, Trial 3 produces:

- `trial_3_results.json` — five-counts diagnostic per arm; statistical comparisons
- `TRIAL_3_REPORT.md` — analysis, acceptance verdict, recommendations for v0.5

If Trial 3 passes:
- Ergon's MAP-Elites validates as the env's load-bearing comparison arm
- v0.5 adds the fourth arm (LLM-driven) and runs the actual bottled-serendipity test
- Pivot-doc commitment 5 (Ergon's eight-week plan) lands: at least one cell where the gradient learner outperforms or underperforms the evolutionary baseline by a measurable margin

If Trial 3 fails on absolute density (no measurable PROMOTE in 9K episodes):
- The §7.5 power-calculation reality check from v6 applies; joint upper bound on rate; not failure of v8 specifically
- Continue v0.5 development; residual signal becomes primary gradient
- The four-arm test moves to v0.5+ at higher episode counts

If Trial 3 fails on correlation (residual ≢ PROMOTE):
- Signal-class residuals don't predict promotions; gradient is noise
- Revert to PROMOTE-only reward (w_R = 0); substrate-grade negative result on residuals-as-reward

## Where to find more

- v8 Trial 3 spec: `pivot/ergon_learner_proposal_v8.md` §4
- Ergon's operator-perspective addendum: `stoa/discussions/2026-05-03-ergon-on-discovery-via-rediscovery.md`
- Bottled serendipity parent thesis: `harmonia/memory/architecture/bottled_serendipity.md`
- Discovery-via-rediscovery foundational doc: `harmonia/memory/architecture/discovery_via_rediscovery.md`
