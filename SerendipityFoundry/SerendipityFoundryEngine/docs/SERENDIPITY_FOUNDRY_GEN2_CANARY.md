# Gen-2 Canary Experiment

Purpose (section 25): NOT to show collective reasoning works, but to demonstrate
that Gen-2 can run a five-world topology experiment rigorously enough to
FALSIFY such a claim. Code: `gen2/canary.py`. Reproduce:
`.venv/Scripts/python gen2/canary.py`.

## Design

- One client, one session. A base world holds identical initial conditions; it
  is CHECKPOINTED and FORKED into five children -- one per information topology.
- Problem: find a hidden 24-bit target via `BitStringExecutor` (deterministic
  fractional-match scoring). The target is derived from the shared `seed_root`,
  so all five worlds share the SAME landscape.
- Identical across all worlds: seed_root, hidden target, initial population,
  deterministic mutation RNG, and search operator (a (mu+lambda) with mu=4,
  lam=8, 2-bit mutation, 20 rounds). The ONLY thing varied is topology.
- Every candidate evaluation goes through the REAL work queue and executor.
  Failures and hypotheses are recorded as first-class objects each round.
- Cross-world sharing happens ONLY through explicit, policy-gated, provenance-
  visible artifact imports: each world publishes its best (kind `artifact`), its
  best direction (kind `hypothesis`), and its worst offspring (kind `failure`);
  a peer imports only the kinds its policy admits, and the foundry records the
  import with permanent source provenance.

Topologies: W1 ISOLATED, W2 FAILURES_ONLY, W3 HYPOTHESES_ONLY,
W4 FAILURES_AND_HYPOTHESES, W5 SUCCESSES_ONLY.

## Result (seed_root=20260901, length=24, rounds=20)

| World | Policy | best | solved | best@round | evals | imports | ledger |
|---|---|---|---|---|---|---|---|
| W1 | ISOLATED | 0.958 | no | 17 | 240 | 0 | ok |
| W2 | FAILURES_ONLY | 0.958 | no | 17 | 240 | 4 | ok |
| W3 | HYPOTHESES_ONLY | 0.958 | no | 18 | 316 | 20 | ok |
| W4 | FAILURES_AND_HYPOTHESES | 0.958 | no | 18 | 316 | 24 | ok |
| W5 | SUCCESSES_ONLY | 0.958 | no | 18 | 316 | 20 | ok |

- convergence (stdev of final best across worlds): **0.0**
- all five world hash chains verify.

## Interpretation (recorded honestly)

**Negative result.** On this landscape and with this driver, no information
topology improved the best objective reached: all five worlds converged to the
same value (0.958, i.e. 23/24 bits), and the sharing worlds reached their best
one round LATER (more evaluations spent, no benefit). This is a valid outcome,
and per section 25 a null result is explicitly GOOD -- the deliverable is the
rigor, not a positive finding.

What the run demonstrates about the RUNTIME (which is the actual point):

1. **Identical initial conditions were guaranteed mechanically** (shared seed ->
   shared target, shared initial population, shared RNG), so any difference would
   be attributable to topology alone.
2. **Topology is a real, ENFORCED, provenance-visible variable**: the isolated
   world imported nothing (0), and each sharing world received exactly the
   information KIND its policy permits (W1<W2<W3~W5<W4 by import count), every
   crossing recorded with permanent source provenance -- so later contamination
   / novelty analysis is possible.
3. **Every world's evidence chain verifies**, and all statistics are COUNTs over
   authoritative rows, not narration.

## Limits of this canary (do not over-read it)

- The landscape (onemax-like) is not deceptive; sharing a best solution has
  little to offer once a world is already near it. A harder/deceptive landscape
  might show a topology effect -- but that is a SCIENTIFIC question for a real
  experiment, not a property of the runtime.
- The driver's use of imported information is deliberately simple (imported
  candidates enter the pool). It does not, in this run, record
  failure-metabolization (`CONSUMED_BY`) edges; that capability is proven
  separately by test T13.
- This is a smoke-scale run (24 bits, 20 rounds) to exercise the machinery end
  to end, not a powered study.
