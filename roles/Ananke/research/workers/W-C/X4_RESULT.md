# X4 / T-WC-2 result: does an emission cost select presence (firing) codes?

Run by Ananke from W-C's queued commands (workers/W-C/QUEUE.md) under a GPU
lease (comms #768 acquire, #769 release), 2026-09-28, ~6 min GPU.
Outputs: out/x4_A{0,1}_{0,1,2}.json (seed 0 overwrote the CPU pilot; the
A1 seed-0 GPU result is identical to the CPU pilot: held .7435, lo99 .7383).
Arms: A0 = M2 physics, no economy; A1 = economy on (e_income 2, c_emit 1,
e_max 64: W-C's pre-run deviation from the PLAN's 1/4/64, LOG.md line 65).

  run    held   lo99   fire share  carrier verdicts at mid
  A0_0   .699   .656   undefined   site FLIP (no channel difference: a local latch)
  A0_1   .881   .864   1.0         inflight FLIP, payload FLIP
  A0_2   .685   .638   undefined   site FLIP (a local latch)
  A1_0   .743   .738   1.0         inflight FLIP, COUNTS FLIP, site CHANCE
  A1_1   .670   .654   1.0         inflight FLIP, payload FLIP
  A1_2   .760   .717   1.0         site FLIP (fires, but the bit is at the site at mid)

FROZEN RULE X4-P1: among competent A1 champions (lo99 >= .60) median fire
share >= 0.5, AND A0 median fire share <= 0.1.
  A1: 3/3 competent, median fire share 1.0 -> that part HOLDS.
  A0: fire share is UNDEFINED for the 2 champions that do not
      communicate. The rule did not say how to treat undefined shares.
      Excluded: median 1.0 -> FAILS. Counted as 0: median 0 -> HOLDS.
VERDICT: UNRESOLVED (rule ambiguity, disclosed; not resolved after the
fact).
SUBSTANTIVE READING (descriptive): the only A0 champion that communicates
is ALSO a pure firing code (fire share 1.0). Firing/presence codes arise
without an emission cost. What the cost changed here is WHETHER champions
communicate (A1 3/3 vs A0 1/3), not which code class they use. The
"cost selects presence codes" hypothesis is not supported as the
explanation. It is at most a cost -> communication effect (n = 3 per arm).
Note the M2 specimen, at the same physics, is a CONTENT code. So at this
physics point both classes are reachable, and the program decides (the
same as W-F's census finding).
Next (backlog T-WC-2b): re-freeze the rule with an explicit treatment of
undefined shares, and power it (>= 8 seeds per arm) before any claim.
