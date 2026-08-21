# Rung R5 — Counterfactual Control · Circuit Study (Loop pass 1, cycle 007)

**Canon:** Band A. R5 = holds branches; answers "what changes if X changes". Kill test
(v0.1 table): premise-reversal question — R5 maintains branches, R4 collapses to one.

## 1. The distinctness question, answered by resource discipline

Cycle-006's block asked ChatGPT whether R5 is distinct from "run twice and diff" (reply
pending). We answered it ourselves first, in the ladder's own currency: **without a resource
bound they are NOT distinct — with single-pass input and metered memory they separate.**

- Run-twice needs a replay buffer: memory grows with the stream (1+n cells, measured).
  The buffer is a blackboard smuggled in as "just re-run" — the same move that killed
  claim v3, recurring at R5.
- Genuine counterfactual control holds parallel live states: 2 cells at any stream length,
  queries answerable MID-stream (control, not post-hoc analysis).
- Beyond its buffer the honest replay circuit ABSTAINS (its dropped events are gone in a
  single-pass world); the branch-holder stays exact. Executable at stream 200 / cap 32.

**State-topology reading (claims ledger updated):** R5's ingredient is PARALLEL composition
of state — sequential-bounded (R2) → persistent store (R3) → live parallel branches (R5).
R4+backtrack visits branches and discards; R5 keeps them co-resident because the QUERY is a
function of both.

## 2. The trap: delta tracking (the R5 analogue of the prior-selector)

`DeltaOnlyCircuit` tracks only actual + (cf − actual). On ADDITIVE post-fork streams it is
exactly right — indistinguishable from branch-holding — because additive updates leave the
gap invariant. One multiplicative event and its answer is stale (the gap should scale).
**Battery rule: R5 probes must include non-additive post-fork dynamics**, or they certify
gap-bookkeeping as branch-holding. (General principle, third occurrence now: every rung has
a cheaper mechanism that is exact on a measure-zero-ish battery slice — R0 retrieval on
clean probes, R4 priors on stable base rates, R5 deltas on additive dynamics. The battery's
job is to leave the slice.)

## 3. Egglog assessment (Track 1, spike PASSED)

`egglog_saturation_demo.py`: (a·2)/2 ≡ a proved with UNORDERED rules, 10 saturation rounds.
Where it earns rent: R2.5 (noncanonical composition — all interleavings held at once), and
a precise R5 connection: an e-graph is branch-holding at scale (every e-class a live
branch), but NOT streaming — the single-pass separation still applies. Revisit at R7/R8:
extraction over a saturated graph = representation-shift machinery.

## 4. Open questions

- ChatGPT round-3 reply (when it arrives) may propose a behavioral probe that separates
  branch-holding from replay WITHOUT metering memory — if so, fold in and compare with the
  single-pass argument.
- Interventional vs observational nuance deferred: our fork flips an INPUT event. Flipping
  an internal INFERENCE (belief revision) is R6/R7 territory and probably needs the
  constraint store.

*— Techne loop, cycle 007.*
