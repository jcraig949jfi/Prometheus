# OPERATOR DIRECTIVE 2026-10-05 (verbatim, received in session 0f14ab93 after the Beta-01 close)

I would accept T12 as a real positive first-order improver-change result, but I would not spend it on R8 yet. The result is too interesting—and too thin—to build the recursion claim on without one stronger replication.

The key discovery is narrower and cleaner than “g11 is better”: the original improver systematically confuses memorization with transferable abstraction, and deleting the memorization option changes downstream capability. That is a genuine change to the improvement machinery. The 5/0/3 result is enough to earn the next experiment, not enough to settle the mechanism.

My order would be 1 → decomposition → R8, while option 3 is designed in parallel and option 4 stays parked.

I would authorize a Beta-02 like this:

APHRODITE — BETA-02: IMPROVER REPLICATION → MECHANISM SPLIT → R8

Accept Beta-01/T12 as:

IMPROVER_CHANGE_REPLICATED_LOCAL = YES

EVIDENCE_TIER = 2

FIRST_ORDER_ONLY = YES

R8 = UNTESTED

Do not call this recursive self-improvement.

E1 — Higher-powered fresh-seed replication

Use only newly generated lineage seeds, beginning at 24.

Pre-register a substantially larger paired sample before running; 24 fresh seeds is a reasonable minimum.

Reproduce the frozen T12 comparison exactly:

g11 @ O10 versus the original I_0 comparator under matched seeds, budgets, tasks, tribunal, and held-out families.

Preserve:

* junk-schema negative control;
* known-answer controls;
* held-out family endpoint;
* exact paired test;
* no sample-size increase after outcomes are visible.

Report effect size and per-seed differences, not only p-value.

E2 — Factorial mechanism split

On the same fresh seeds, test whether the gain requires wider observation.

At minimum compare:

g11 @ O4

g11 @ O10

and the appropriate frozen I_0 controls at the same observation depths.

The question is:

Is the T12 effect caused by the selection-rule change, the larger observation set, or their interaction?

Do not infer this from Beta-01 retrospectively.

Report:

MEMORISE_EXCLUSION_EFFECT

OBSERVATION_WIDTH_EFFECT

INTERACTION

separately.

If g11 only works at O10, say so. That is still a result.

E3 — R8, conditional

Freeze the R8 assay before E1/E2 results are inspected, but execute it only if the preregistered replication gate passes.

R8 asks:

Does a library produced by the improved improver (g11) make the next generation’s improvement process better than a library produced by I_0?

The treatment is not “g11 solves more tasks.”

The treatment is the heritable output of g11’s improvement process.

Build two donor libraries under paired conditions:

L_g11

L_I0

Freeze and hash both.

Destroy donor state.

Transplant each into fresh next-generation improvers with identical machinery, budgets, task sequence, and evaluator access.

Primary comparison:

fresh improver + L_g11

versus

fresh improver + L_I0

on previously unseen improvement opportunities.

R8 passes only if the library produced by g11 causes the next generation to improve better, not merely solve more inherited tasks.

No donor history, caches, task identities, scoring traces, or selection state may cross.

If R8 passes, stop. Do not immediately recurse again.

E4 — Principled replacement for g11

In parallel, design but do not use to reinterpret E1–E3:

replace the hard “exclude MEMORISE” rule with a general criterion that scores candidate libraries according to the same property ultimately demanded at transfer.

The desired rule should distinguish:

* high local fit / poor transfer;
* reusable abstraction;
* memorization;
* false-positive shortcuts.

g11 remains the experimental positive comparator.

A new scoring rule is a new improver hypothesis, not a repair of g11.

LLM test

Do not run it yet.

The local-engine prediction should first survive the larger replication and mechanism split. Only then is a model-scale skill-library experiment worth inference budget.

The factorial is important. Right now you have a surprisingly crisp clue:

g10 + O10 = I₀, while g11 + O10 wins.

That strongly implicates memorization exclusion, but the untested g11 @ O4 cell leaves a causal hole. Close that before R8.

And I like R8 much more now than I did before Beta-01. Earlier we were trying to manufacture a second abstraction in a tiny grammar. Now there is a much more natural recursive object: the improver’s own library-production policy has changed. R8 can ask whether the product of that improved policy makes the next improver better.

That is a cleaner recursion assay:

I₀ → g11 improves library production → g11-produced library → fresh next-generation improver improves better.

If that passes, the recursive claim is substantially stronger than merely deriving another hand-shaped macro.
