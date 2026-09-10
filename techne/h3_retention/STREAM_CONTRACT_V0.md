# H3 candidate stream — declared fixture contract, v0

Techne, 2026-09-10. Written because the real stream does not exist yet: H3 alpha is NOT
STARTED (`roles/Archaeon/H0H5_STATUS.md`), and the operator's instruction is to build the
adapter against a **declared fixture stream** until Archaeon hands over the format from the
first complete compatible stream (Track B's C3 corpus or Track E's NK).

This contract is therefore a **proposal with a working implementation**, not a specification
of Archaeon's stream. When the real format arrives, the expected outcome is that this file is
amended or replaced. What should survive is the set of properties the adapter needs in order
for a retention comparison to mean anything — those are argued below, each with the failure it
prevents.

## The five required properties, and what each one is for

The operator named five. Each is a refusal in `stream.validate()`, not a convention.

### 1. Stable ordered ids

`seq` is 0-based, contiguous and strictly increasing; `candidate_id` is unique across the
stream. A retention policy is a function of the order candidates arrive in — first-writer-wins
on a tie is *literally* an order rule — so a stream without a declared total order does not
determine its own replay. Two policies compared over an ambiguously ordered stream differ by
an amount that includes the ordering.

REFUSES: gaps, repeats, non-monotone `seq`, duplicate `candidate_id`.

### 2. Candidate digests

`candidate_digest` is `sha256` over the canonical JSON of the candidate payload. Identity by
content, independent of position. Without it, "the same candidate" means "the same id", and an
id is an assertion by the producer; a digest is checkable by the consumer.

REFUSES: a digest that does not match the payload it is attached to. Also DETECTS (and
records, without refusing) two different ids carrying the same digest — a duplicate candidate
under two names, which inflates every count a policy reports.

### 3. Birth status

`birth.status` in `{SEEDED, MUTATED, RECOMBINED, REPLAYED}` with `parent_ids`. `SEEDED` has no
parents; every other status has at least one, and every parent must have appeared EARLIER in
the stream. A retention policy that prefers novelty, or that charges a candidate's cost to its
lineage, needs provenance; and a stream whose parents appear after their children cannot be
replayed forward at all.

REFUSES: `SEEDED` with parents, non-`SEEDED` without, a parent id never seen, a parent
appearing at a later `seq`.

### 4. Fixed assay references

Every row carries `assay_ref = {assay_id, assay_version, digest}`, and **every row in one
stream must carry the same one**. "Fixed" is the whole point: retention policies are compared
on the objective and measures the assay produced, so a stream that changes assay mid-way makes
the comparison a mixture of policy effect and instrument change, with no way to separate them
after the fact. This is the same shape as a number measured over one population and quoted as
a property of another.

REFUSES: any row whose `assay_ref` differs from the header's.

### 5. Recoverable results

Every row carries `result_ref = {kind, ref, digest, bytes}` resolving to the full result, not
just the scalars the archive keeps. This encodes *eviction is not deletion*
(`proteus/contracts/RETENTION_AND_MEASUREMENT_V0.md`): a candidate the archive drops is still
recoverable by reference, so a later policy can re-admit it and a reviewer can audit what was
lost. An archive whose evictions are unrecoverable cannot be compared against a more permissive
one, because the difference between them is exactly the material that no longer exists.

REFUSES: a missing `result_ref`, or one whose declared `bytes` disagrees with the payload the
resolver returns.

## Two caps, both required, and why they are not one cap

`max_retained` (count) and `max_bytes` (bytes) are separate because they bind on different
streams and a retention result that quotes only one of them is not reproducible.

- A count cap alone lets a policy retain the cap in enormous results and exhaust the host.
- A byte cap alone lets a policy retain an unbounded number of tiny results, which changes
  every per-candidate statistic the comparison reports.

Both are enforced by the adapter and **both are reported with which one bound**. A run where
neither bound is a run whose caps were not exercised, and the receipt says so rather than
implying the caps were tested.

`GridArchive`'s cell count is a *third*, implicit bound (`prod(dims)`). It is reported
alongside the two declared caps so a reader can see which of the three was actually operative.
A run in which the grid bound first is not a test of the declared caps.

## Cap semantics, stated so they can be argued with

Occupancy in a `GridArchive` only grows when a candidate lands in an EMPTY cell. So:

- A candidate landing in a **new** cell when `retained == max_retained` is **REFUSED**
  (`CAP_REFUSED_COUNT`). It is not silently dropped: it is logged with its `result_ref`, so it
  stays recoverable.
- A candidate **improving an occupied** cell does not change occupancy and is not subject to
  the count cap.
- The byte cap is evaluated on the **delta**. A new-cell insert costs its own
  `payload_bytes`; a replacement costs `new_bytes - displaced_bytes`, which can be negative. An
  insert whose delta would exceed `max_bytes` is **REFUSED** (`CAP_REFUSED_BYTES`), including a
  replacement that grows the total.

Every disposition — `RETAINED_NEW_CELL`, `RETAINED_IMPROVED_CELL`, `REJECTED_BY_ARCHIVE`,
`CAP_REFUSED_COUNT`, `CAP_REFUSED_BYTES` — is written to an append-only log keyed by
`candidate_id`, with `result_ref` preserved. The retained set is derivable from the log; the
log is not derivable from the retained set. That asymmetry is the point.

## Exact-tie policy: FIRST_WRITER_WINS, declared and verified

The adapter **declares** `TIE_POLICY = "FIRST_WRITER_WINS"` and then **verifies** that the
installed pyribs implements it, at both granularities, before any stream is replayed:

- **one-at-a-time**: insertion requires *strictly* greater than the cell threshold, and the
  default threshold is the incumbent's own objective, so an exactly equal objective does not
  displace the incumbent.
- **batch**: upstream documents that among solutions tying for the highest objective in one
  cell, the one appearing first in the batch is inserted.

`verify_tie_policy()` runs a two-row probe at each granularity and **raises** if the observed
behaviour differs from the declaration. This is deliberate: the policy must not be inherited
silently from a donor's default, because a future pyribs release that changes it would
otherwise change every retention result without changing a line of our code. Declaring it and
failing loudly is the difference between a policy and an assumption.

## No emitters, no schedulers

The adapter constructs neither, and asserts at the end of every replay that no `EmitterBase`
and no `Scheduler` instance is alive. An emitter would generate candidates from the archive's
own state, making the stream a function of the retention policy under test — a control drawn
from the treatment's own selection relation.

Note the gate is on **instances**, not module imports: `import ribs.archives` eagerly imports
28 emitter and scheduler modules, so a gate on module presence could never pass.

## What this contract does NOT claim

- It is **not** Archaeon's stream format. It is a proposal, and it will lose to the real one.
- The adapter's passing qualification against this fixture is **ADAPTER_QUALIFICATION against a
  fixture**, which is not qualification against H3's stream and is certainly not evidence that
  any retention policy is better than any other.
- Nothing here evaluates a retention policy. The adapter replays one; comparing them is H3's
  experiment and Archaeon's to run.
