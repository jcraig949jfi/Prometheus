# Aether -- Runpod benchmarks, hardware, costs, deployment

Currency: 2026-09-20. No runs yet. $0 of the $19.93 budget spent.

## Budget

- Hard cap: $19.93 total, current as of 2026-09-20 (operator-stated
  account balance, not a top-up commitment).
- No Runpod spend without explicit operator approval, per run.
- Before proposing any paid run, state: the question it answers; expected
  duration; hardware; estimated maximum cost; what result determines the
  next step. A run proposal missing any of these five is incomplete.
- Failed or inconclusive runs still count as spend and must still produce
  a useful measurement (logged below regardless of outcome).

## Spend ledger

| date | run | question | hardware | est. max cost | actual cost | result -> next step |
|---|---|---|---|---|---|---|
| (none yet) | | | | | | |

## Benchmarks planned (once there is something to run)

- Correctness (does the remote build match the local/tested semantics).
- GPU compatibility.
- Throughput.
- Memory use.
- Cost per useful unit of simulation.
- Suitable GPU / serverless / Pod configuration for the workload shape.

## Topology decision (Pods vs. serverless/autoscaling)

Undecided (AETHER_OPEN_QUESTIONS.md, question 14). Deferred until a
workload shape exists to benchmark against.

## Principle

Optimize for learning per dollar, not scale. Start extremely small; do
not assume expensive GPUs are better than cheap ones until measured.
