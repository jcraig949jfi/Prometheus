# CYCLE 138-C' — TERMINAL: KILL

**Question, verbatim as preregistered:** does conditioning proposal selection on terminal
experimental evidence measurably CHANGE which experiments Aporia proposes?

**Verdict: KILL.** What was built is retrieval middleware, not scientific memory. The hard
kill condition fired exactly as written, and it fired on the first pass. No second pass.

## What was built

- `engine/ledger/CLOSURE_RECORDS.json` — 13 closure records, one per terminal campaign
  (B, X, X-2, X-3, X-4, X-5, W, S, T, U, V, F, R). Each carries question, objects, mechanism,
  representation, assumptions tested, established, killed, surviving, unresolved, instruments,
  scope. Frozen: editing a record after its campaign closed is a falsification, not an update.
- `engine/driver/closure_gate.py` — the A/B. Proposals drawn from `engine/queues/BACKLOG.jsonl`
  (644 live PARKED/QUEUED rows), **generator-emitted, not authored for this test**. Closure
  records chronologically filtered so a proposal minted at pass P is judged only against
  campaigns that closed before P — no hindsight.

## The result

    ABLATED  644 admissible
    ENABLED  644 admissible | 0 suppressed by a closure fact
    top-20 changed: 0
    causal examples: 0

## The instrument was vacuous, and the verdict survives it anyway

This is the part that matters more than the verdict.

The preregistered similarity cut was Jaccard >= 0.14. **The maximum attainable similarity
across all 644 x 13 pairs is 0.1364.** The gate could not have fired on any input. That is a
non-measurement, not a null, and doctrine (P125, THRESHOLDS FAIL IN BOTH DIRECTIONS) requires
asking which direction the defect pushes relative to the gate before reading a zero. It pushed
toward KILL — the direction that flatters the conclusion I had already reached.

So the null was checked before it was accepted, and the verdict survives on a ground independent
of the broken cut:

- The single **substantively correct** match is PROF-Harmonia against campaign R, at 0.1364.
  It is correct: R established that `phase0` has no artifact-ingestion path, and the 44 PROF
  rows request exactly that operation. A working gate should suppress them.
- **PROF-Harmonia sits at priority 10 against a top-20 eligibility floor of 68.** It was never
  an eligible causal example at *any* threshold. Lowering the cut until it matched would have
  produced a suppression that changed no allocation decision — the definition of theatre.

The KILL therefore does not depend on the defect. Reported anyway, because a gate that cannot
fire is a gate-design failure whether or not it changed the answer, and because I would not
have found it if the doctrine had not required looking.

## Why it fails — the sharper diagnosis

Proposal vocabulary: **955 tokens.** Closure vocabulary: **129 tokens.** Intersection: **19**,
and those 19 are near-all generic — `built`, `set`, `standard`, `fields`, `exact`, `linear`,
`loop`, `sweep`.

**The two are indexed on different axes.** Proposals are minted naming *targets*: "Catalog
attack: Artin's conjecture on L-functions", "Retry batch 7/15", "PG queue client". Closures are
recorded naming *mechanisms*: log-magnitude vectors, hubness, derangement nulls, local scaling.
No lexical relation bridges them, and there is no reason one should exist. A retrieval layer over
closure records cannot condition proposal selection because the proposal generator does not speak
in the vocabulary in which findings are recorded.

This is a stronger statement than "the records did not help." It says *what would have to change*:
either proposals must be minted carrying a mechanism field, or closure records must be indexed by
target — and neither is a retrieval problem.

## The inheritance measurement the preregistration required

How many of passes 100-137 would have been impossible to propose before passes 1-99?

Measured over the WORKLOG, counting citations of a prior pass or campaign in `intent` and
`pre_stated_readings`:

- **24 of 37** late passes cite prior work at all.
- **1 of 37** cite anything below P100 (P103 cites P74).
- Nearly every citation reaches back **1 to 3 passes**; the longest is P113 -> P123.

**The loop's inheritance horizon is approximately the length of one campaign.** Within a
campaign, inheritance is real and load-bearing — X-2 was designed on X's burned split, X-3 on
X-2's unresolvable gate, W on X-5's overlap artifact. Across campaigns it is near zero. What
looks like accumulated memory is campaign-local continuity that resets at every terminal state.

So the answer to the preregistered question is: **almost none of passes 100-137 depended on
passes 1-99.** That is the honest measurement of what 137 passes have accumulated.

## Self-identified weaknesses

- The proposal set is the backlog, which the same defective generator produced. If the generator
  cannot mint a proposal that collides with a closed campaign, the test cannot observe a
  collision — the null may be a property of the generator rather than of closure records. This is
  a real limit and it does **not** license a second pass; it is the thing to fix before retrying.
- Token overlap is a weak instrument for semantic collision. A stronger one (embedding similarity,
  or an LLM adjudicating "is this proposal answered by this closure") might find collisions this
  missed. But the vocabulary-axis measurement suggests the failure is structural rather than a
  matter of matching strength.
- The inheritance measurement counts *explicit citations*. A pass could inherit a finding without
  naming its source, which would undercount. Against that: the count is drawn from `intent` and
  `pre_stated_readings`, the two fields where this loop's discipline requires naming what a pass
  builds on.
- 13 closure records over 137 passes is a coarse memory. A finer-grained record — per-pass rather
  than per-campaign — was not tested.

## Falsifier

A proposal minted by the real generator that a closure record demonstrably should have suppressed,
found at any threshold with any matching method, and sitting high enough in the queue to have
changed an allocation. Or: evidence that the backlog generator *can* mint mechanism-level
proposals, which would move the null from structural to instrumental.

## Terminal

**CYCLE 138-C': KILL.** Retrieval middleware, not scientific memory. `CLOSURE_RECORDS.json` is
retained as a record — it is accurate and it cost little — but it is **not** claimed to condition
anything, and no further pass is spent making it work.
