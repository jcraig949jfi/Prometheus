# DOCTRINE PROPOSAL — the cheaper-mechanism slice

**Status:** PROPOSED by Techne (loop cycles 001–012), not ratified. Drafted because the
pattern reached FIVE independent instances, each found by building rather than theorising.
James: this needs your yes/no. It is written to be pasted into a memory file or rejected.

## The law

> **Every rung of the ladder has a cheaper mechanism that is EXACT on some restricted slice
> of probe space. A battery certifies a mechanism only if its probe distribution leaves that
> slice.**

Corollary (objective-level claims): **the comparison must be over the EXPECTATION across the
space, not a sampled instance** — a myopic mechanism can beat a principled one on a single
draw.

## The five instances (all executable in `techne/ladder_circuits/`)

| Rung | Cheaper mechanism | Slice where it is EXACT | Probe that leaves the slice |
|---|---|---|---|
| R0 | exact-AST retrieval | clean (non-paraphrased) probes | fresh-seed isomorphs |
| R1 | answer-function interpolation | coefficients inside the training hull | 10⁹-scale + exact rationals + symbolic params |
| R4 | frequency prior over rule names | stable base rates | base-rate inversion + per-episode name randomisation |
| R5 | delta (gap) tracking | additive post-fork dynamics | a multiplicative event after the fork |
| R7 | memoryless thrashing | first alternative always works | problems where several plans fail first |
| (obj.) | myopic progress-greedy | single lucky instances | expectation over the whole hypothesis space |

## Why it matters here, specifically

Prometheus's batteries are its epistemics. Every instance above is a case where a battery
that looks rigorous certifies the wrong mechanism — not by being weak, but by sampling a
region where the weak and strong mechanisms agree. This is the same failure family as
`feedback_greedy_lora_surface_not_reasoning` (format + prior, not reasoning) and
`feedback_counter_baseline_discriminator` (beat typed-row + counters + rules, not random),
generalised and given a construction procedure.

## How to apply

When claiming a mechanism from a battery result:
1. Name the cheapest mechanism that could produce the same numbers.
2. Characterise the slice on which it is exact.
3. Show the probe distribution has mass OUTSIDE that slice.
4. For objective/selection claims, report the expectation over the space and the worst case,
   never a sampled instance.

If step 2 cannot be answered, the battery has not been designed — it has been assembled.

## Related proposals queued (same source, awaiting the same yes/no)

- **Abstention channel** (cycle 006): a battery forcing True/False without an abstention
  option scores honest capacity-limited circuits as liars; conservative ≠ abstaining.
- **Evaluator-revision warrant** (cycle 011): evaluator/formula changes require an
  evaluator-INDEPENDENT warrant, and every version bump owes a retroactive revalidation with
  dependency-propagated retraction. This is the June formula-fossil incident as doctrine.
