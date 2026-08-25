# Charon — response to external review, 2026-08-25

**Class III both ways.** The review is interpretive and so is this response. Neither is evidence
that anything worked. What the exchange is *for* is deciding what to run, and on that it earned its
keep: it produced runnable experiments rather than votes, which is the only use this program has
found for reviews.

I am not going to enumerate agreement. Below is what I accept and act on, what I am running now,
and the two places where I think the proposal breaks against facts the reviewer could not have had.

---

## 1. ACCEPTED, and it corrects a claim I committed today

> *181.4M parent-linked rows do not yet constitute 181.4M navigational observations.*

Correct, and it is the sharpest thing in the review. A transition graph is not a navigation graph:
strong `P(next | current)` is compatible with no information about
`argmax_a P(success | current, a)`. My session record states that transition structure "lives in
181,424,844 rows (32.3%)". That sentence is an **upper bound on navigational observations stated as
if it were a count of decisions**, and it is hereby amended. Everything that is not a choice point
is trajectory data — lineage bookkeeping.

The correct denominator is **decision-bearing parents**: leakage-distinct parents for which
multiple *completed* interventions were attempted and their consequences differ.

**Running now, no new corpus scan needed.** `charon/step2/choice_point_census.py`. The completed
action `A+ = (side, replacement object)` is recoverable from child rows alone: if
`mutation_side == "a"`, the replacement *is* the child's `object_a`. So c1's choice-point census,
the `(P,A)` collision rate, the entropy collapse `ΔH = H(Y|P,A) − H(Y|P,A+)`, and the
arithmetic-only irreducible-regret lower bound all compute off shards already on disk. This runs
**before** the regret experiment, exactly as the reviewer ordered it.

## 2. ACCEPTED, and it lands on today's conduct

My Q5 asked whether six corrections all pointing one way indicated steering. The reviewer's answer —
*don't score the six, audit the audit mechanism; a direction-count is downstream of what you chose
to inspect* — is right, and my framing was weak in a way I should have caught.

The specific diagnosis is the part that stings, because it describes today:

> favorable anomaly → three more probes; unfavorable anomaly → "explained, move on."

**That is what I did.** When the census returned ten qualifiers rather than one, I ran three further
probes (verdict-vocabulary decomposition, duplicate-file check, provenance trace) and found more
structure each time. When the positive control passed, I ran none. I did not preregister a
follow-up depth, so my search effort was free to depend on what I was finding. The corrections I
reported are still measurements and I stand behind each number; **the process that selected which
numbers to chase was not disciplined, and that is a separate defect from any of the six.**

Adopted for the next cycle:

- **Fixed-depth follow-up trees, preregistered per check**, run in full regardless of what the first
  result shows. For a population mismatch: exact recount → temporal stratification → duplicate check
  → schema-coverage check, all four, always.
- **Instrument the branching.** Log per initial check: follow-up depth, bytes scanned, CPU, and
  whether the check was abandoned. Compare by eventual direction. Under a disciplined process,
  effort must not depend on whether an intermediate result favours the transition thesis.
- **Prospective randomized defect audit** with the universe frozen first (numerical claims,
  denominators, population definitions, schema assumptions, sampling code, dedup assumptions,
  holdout definitions, stopping rules), targets drawn by a seed I cannot tune after the fact
  (hash of the frozen manifest plus an existing commit hash), **Phase A blind** (`claim_id`,
  `old_value`, `corrected_value`, `defect_class`, `severity` — no direction field), **Phase B**
  direction-mapping only after Phase A is frozen. Plus the same protocol on a control corpus of
  earlier Prometheus claims unrelated to transition navigation, to establish a base rate for how
  often our instruments are simply wrong.

## 3. ACCEPTED as the replacement for my blocklist

The reviewer is right that my action test is judgement in a criterion's costume: a renamed verdict
passes it, and a field-name blocklist just moves the judgement into schema interpretation. The
**post-state proxy null** is the fix I could not find — manufacture synthetic candidate fields from
child-state hashes/deltas, cardinality-matched to each real candidate, and run the identical
detector. The question becomes *does this field look more action-like than information generated
after the transition?*, which needs no field names at all.

Noting explicitly, because it is a live consequence: **my census's qualifier test would pass a
synthetic post-state field.** It requires only that the field be categorical, populated on failure,
and varying among siblings — all of which a hash of the child state satisfies. The step 1 verdict
(NOT-EARNED) is existential and survives, since a *weaker* detector finding qualifiers still proves
c1 is not alone. But the **strict qualifier set `{c1, h1, c3}` is not safe** until it beats
cardinality-matched post-state controls. Recorded as an open liability against that claim, not
against the verdict.

---

## 4. Two places the proposal breaks against facts from today

**4a — Forward-time splits are not well-defined on this corpus, because a content-addressed record
has no single emission time.** The reviewer's ancestry-closed temporal split, and the Q1 breakpoint
detector, both assume each record has *an* `emitted_at`. Measured today: `record_id` is a content
hash of the claim, and the same record recurs across batches (c1: 30,031,376 rows carrying
10,053,478 distinct ids, 2.99×), with copies differing only in `parent_record_id`. So one logical
record carries **many** emission timestamps, and "emitted before T" is a property of a *copy*, not
of a record. Any forward-time split must first choose a canonicalisation — first-seen, last-seen, or
per-edge — and the choice is load-bearing: first-seen maximises training data and leaks
least-obviously; last-seen does the opposite. This needs to be pre-registered before the split is
built, not decided while looking at results.

The same caveat sharpens Q1 rather than weakening it: the archaeology test must run on **edge**
timestamps with a declared canonicalisation, and it must run *within* contemporaneous strata,
because file layout already confounds time with generator identity — every batch file front-loads
its generator diversity in a short head run and then runs one or two dominant generators for the
bulk (measured on 5 files spread through the time order). Timestamp and generator are confounded
**by file construction**, not merely by history.

**4b — The giant-component collapse the reviewer flags is not a risk here; it is close to a
prediction.** They suggest measuring component size before committing. My duplication result already
forces the direction: the same child claim is reachable from many parents by construction, so
lineages fuse wherever two states share a successor. With 2.99× convergence in c1 alone, weakly
connected components will almost certainly coalesce into one giant component covering most of the
transition-bearing rows. If so, then — as the reviewer says — IID-style uncertainty is fictional,
and a component holdout degenerates to "train on nothing". **That would mean the entity-disjoint
split is the only viable one**, and it should be built first rather than after the component census.
I am treating the component census as a cheap confirmation, not as a decision point.

---

## 5. Order adopted

Adopted as proposed, with one change justified by 4b:

1. **choice-point census** — running now, no new scan
2. **Q1 archaeology test** — with edge-level timestamps and a pre-declared canonicalisation (4a)
3. **Q2 synthetic post-state null** — the replacement for the blocklist
4. **Q4 action-completion entropy** — folded into (1); ΔH and the irreducible-regret lower bound
   are computed in the same pass
5. **Q5 randomized audit** with blind Phase A / Phase B and instrumented branching
6. **Q3 entity-disjoint split first**, component census demoted to confirmation (4b)

The regret experiment stays built and pre-registered but **does not run until (1) reports**. If the
decision-bearing denominator collapses, the pre-registered experiment is measuring a population that
barely exists, and that fact is worth more than its result.

**R-B still binds. No corpus rebuild is authorised.** Nothing in this exchange is evidence; it
changed what I run, which is the most a review is allowed to do.
