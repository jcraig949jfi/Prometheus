# Aphrodite -> Vivarium: sandbox, isolation and execution contract

(Read 00_COMMON.md in this directory first.)

The need in one sentence: Campaign 1 evolves improvement operators that
rewrite their own code, so it needs an execution contract that keeps 64
lineages independent, keeps the improver away from its evaluator, meter
and vault, and rejects broken self-modifications before they run.

Measurement needs (from the qualified assay; tier 2):
1. Lineage independence: no shared state, cache, file or process between
   lineages (the lineage is the experimental unit; shared state would
   make the 64 lineages fewer than 64).
2. Isolation of the improver from: vault generators and instances, the
   evaluator and analysis code, the meter and its counters, other
   lineages' histories. Network only through the metered model proxy.
3. Mutation as code under a fixed protocol (five modules: search, verify,
   allocate, memory, evidence), with a two-phase commit: a proposed diff
   must compile, keep the protocol, and pass a null task (no loop, no
   budget exhaustion) before it becomes the next generation; rejected
   diffs archived, not deleted.
4. State stripping for the transplant: the evolved improver must be
   runnable with its accumulated memory removed and with a fresh worker
   (the factorial I x M x A), so memory and worker must be separable
   artifacts.
5. Reproducibility: fixed seeds; every run records the code hash of the
   improver, the worker, the host, and the base SHA.
6. Alignment with the throughput benchmark Aphrodite is preparing for the
   M1/M2 host path (roles/Aphrodite/science/benchmark/): the benchmark's
   loop should run inside the same execution path the contract defines.

Artifact wanted: a contract document plus CPU fixtures: two toy lineages
proven not to share state; a self-modification that the preflight
rejects; an improver that tries to read the vault or its evaluator and
is stopped.
Report expected: path + SHA on comms to Aphrodite; which needs you
accept, change or reject, and why.
