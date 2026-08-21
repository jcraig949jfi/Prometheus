# DOCTRINE PROPOSAL — the immutable-observation bottom

**Status:** PROPOSED by Techne (loop cycle 013), not ratified. Supersedes the cycle-011
"evaluator-revision warrant" draft, which was necessary but too weak — this version answers
*who may change the constitution* and grounds it in something Prometheus already needs.

## The rule

> **The historical relation between declared predictions and observed outcomes is immutable.**
>
> You may reinterpret its importance. You may replace metrics. You may discover that a test
> was confounded. You may not alter *"we predicted y; under protocol P we observed z."*

Everything above that line stays plastic — including what counts as evidence.

## Why a bottom is needed at all

Unrestricted self-validation collapses: `E_t` validates `E_{t+1}`, and `E_{t+1}` validates
its own replacement of `E_t` — circular legitimisation. Either there is a fixed bottom, or the
system regresses. **This proposal takes the fixed-bottom side**, and makes the bottom as thin
as possible so almost everything remains revisable.

## The regress separator (executable)

`techne/ladder_circuits/tests/test_round5_foldin.py`:

1. Evaluator `E_0` fails on counterexample `c_0`; the observation is recorded.
2. Propose `E_1`. Fine.
3. Propose constitutional amendment `K_1` **whose sole effect is to make `c_0` stop counting
   as a failure.**

A regress-permitting system accepts `K_1` and the failure evaporates. The fixed-bottom system
**refuses** — the recorded prediction/observation relation cannot be erased. Amendments that
merely change metrics or thresholds are accepted in the same test, showing the bottom is thin
rather than paralysing.

## What the constitution actually contains (bookkeeping physics, not scientific doctrine)

- no contradiction accepted as proof
- declared deterministic checks reproduce
- evidence provenance is immutable
- revision cannot rewrite historical observations
- a new evaluator must defeat the old one on **pre-declared** counterexamples

None of these say what mathematical evidence *is*. They say how changes must be demonstrated.

## Why this is urgent for Prometheus specifically

The 2,351-promotion incident is exactly the failure this prevents: certifications under a gate
that was later replaced, with no immutable record tying claims to the regime that certified
them and no obligation to revalidate. The reviewer's phrasing is the right prescription —
**make the bottom aggressively boring**: immutable observations, hashes and provenance,
predictions declared before seeing outcomes, deterministic replay where available.

## The companion machinery (built cycle 013, `certification_provenance.py`)

- **Certification provenance, not consumed evidence.** Storing `evaluator_version + evidence`
  is necessary but *not sufficient*: a short-circuiting evaluator consumes `e1` only, so a
  change to a predicate over `e2` leaves no trace that the claim is affected. Certificates
  must record the predicates and assumptions *invoked*, making revision a build-system
  dirty-set computation over evaluator components.
- **Negative dependencies.** "Accepted because no counterexample existed under query Q at
  snapshot v" consumes no evidence record at all, yet database *growth* invalidates it. Any
  index keyed on consumed evidence misses these permanently.
- **Justification vs influence.** Retraction propagates only through justificatory
  dependency, tested operationally: `A ∈ JustDeps(B)` iff `Verify(B | Evidence_B \ A)` fails.
  A false conjecture that merely *inspired* a search does not invalidate what the search
  independently certified — otherwise one bad early heuristic annihilates a whole lineage.
  Keep the influence graph for bias audits; never for automatic deletion.
