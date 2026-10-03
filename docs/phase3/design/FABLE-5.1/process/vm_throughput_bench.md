# Receipt: toy register-machine throughput on M1

Purpose: ground the compute requirements (COMP-01) in a measured number.
This is not a Prometheus engine and nothing here is science.

- When: 2026-10-01T14:36Z (from date -u at the end of the runs).
- Host: SKULLPORT (M1). AMD Ryzen 7 7700X, 8 cores / 16 logical processors,
  31.6 GB RAM (Win32_Processor and Win32_ComputerSystem). GPU present and
  idle: RTX 5060 Ti, 16311 MiB, power limit 180 W (nvidia-smi).
- Software: Python with numba 0.65.1, numpy 2.2.6; numba threads 16.
- Command: `python process/vm_throughput_bench.py`, three times.
- Program: 8 int64 registers, 64-cell memory, 16 opcodes, random 64-instruction
  programs; single-core 400,000,000 steps; all threads 4,096 organisms x
  3,000,000 steps.

Output, verbatim:

    single core: 534.2 M instr/s (400000000 steps in 0.749 s)
    all threads: 5035.2 M instr/s (4096 organisms x 3000000 steps in 2.440 s)
    single core: 530.6 M instr/s (400000000 steps in 0.754 s)
    all threads: 5024.4 M instr/s (4096 organisms x 3000000 steps in 2.446 s)
    single core: 531.7 M instr/s (400000000 steps in 0.752 s)
    all threads: 5110.2 M instr/s (4096 organisms x 3000000 steps in 2.405 s)

What it supports and what it does not.

- It is a ceiling for a tight integer interpreter on this host: about 0.53
  billion instructions per second on one core, about 5.0 billion on all
  threads.
- A real organism in a real world will be slower: more opcodes, a store,
  tag matching, world stepping, cost accounting. The design assumes a factor
  of 10 until a real kernel is benchmarked, which is the first deliverable
  of the 90-day plan.
- At 100,000 instructions per lifetime and the assumed factor of 10, that is
  on the order of 4 x 10^8 lifetimes per day on M1 alone.
- An earlier, shorter run (20,000,000 and 100,000 steps) gave 522.5 M and
  5104.8 M; it is superseded by the longer runs above because its timing
  window was under 0.1 s.
- Not measured: GPU throughput, memory-bound workloads, other hosts.
