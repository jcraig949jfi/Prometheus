# W2-23 PREREG: Harvard confinement as a causal test of the wrap / partner-execution field

Frozen at 2026-10-01T01:43:03Z (from `date -u`), worktree HEAD 01fc02f91, BEFORE any scoring run.

## Hypothesis H-WRAP
The N1 / N2 / W2-16 / W2-3 K3 effects share one cause: a context's pc leaves its own half (63->64, 127->0)
and executes the partner's code with the wrong context. Harvard confinement (W2-7 `HARV_*`: a context may only
fetch opcodes inside its own half) removes exactly that route and leaves the data path (LDIR reads/writes
across halves) untouched.

## Physics arms
- STOCK: the VM each source experiment used (DENSE for W2-16 / CVT-R; stock PLAIN z8 for K3 and N1/N2).
- HARV_HALT: pc outside own half -> context stops (W2-7 injection, unchanged anchor).
- HARV_WRAP: pc outside own half -> wraps inside own half (no terminator).
For K3 / N2 the HARV injection is applied to the PLAIN z8 source with the same anchor text as W2-7
(`alien_vm.build` only builds on DENSE). Self-tested before scoring (see below).

## Predictions (if H-WRAP is the cause)
- **P1.** Side-1 copiers (the 17 Artemis ROWS certified on side 1), CVT-R on side 1 with Artemis's
  certs unchanged and the step function's `p11.interact` running under HARV_HALT: accept >= 14/17.
  Stock reference: 3/17 on side 1 (record; "4/17" in the brief is either-side, c_zero_specific:4 accepts on side 0).
- **P2.** K3 single-site chain (k3_site_hazard.chain, unchanged; 40 chains/cell, same seeds) with the
  7ae3 implant in 9cba / e160: relabel share <= 0.10 in BOTH cells under HARV_HALT (stock 24/40, 17/40).
- **P3.** N2 X-TICKET epoch-1 prediction = 0.5 x (side-0 predecessor-accepted overwrite rate of the
  intact 7ae3 founder in its own cell, zero context, N1's magnet_rate protocol, 750 per side):
  <= 0.05 under HARV_HALT (stock 0.5 x 320/750 = 0.21). The random-context arm is reported alongside
  (stock 0.5 x 242/750 = 0.16); P3 is scored on the zero-context arm (N2's stated prediction) AND must not
  exceed 0.05 on the random arm either for a clean PASS.

## Decision rules
- PASS: criterion met AND the STOCK control for that prediction reproduces the source number
  (P1 3/17 side-1 accept, +-1; P2 24/40 and 17/40 exactly (deterministic seeds); P3 320/750 exactly).
- FAIL: criterion not met with the stock control reproducing.
- NOT_VERIFIED: stock control fails to reproduce, or a self-test fails, or the run cannot complete.
  NOT_VERIFIED is never counted as a pass.

## Controls
- C-STOCK: as above.
- C-TERM (confinement vs terminator): the same measurement under HARV_WRAP.
  - If HARV_WRAP also meets the criterion -> confinement is sufficient (terminator not needed).
  - If only HARV_HALT meets it -> the effect is confounded with the added terminator; report as such,
    not as a clean confinement result.
  - Pre-stated expectation for P1 under HARV_WRAP: may be LOWER than HALT, because a copier whose pc wraps
    inside its own half re-runs its own setup+LDIR (W2-7 S8: the long count is also the terminator).
    That would be a terminator effect on the donor, not evidence against H-WRAP for the partner route.
- C-NOPARTNER reference: W2-16 s4 no-partner-run CVT-R side 1 = 17/17.
- Side-0 copiers (18 W2-16 s4 set) CVT-R under HARV: reported, no prediction scored (W2-7: 128/128 competent).

## Self-tests (must pass before scoring)
- ST1: PLAIN-HARV builder: bit-identical to stock PLAIN z8 on every random run where the HARV hit counter
  stays 0; changes state in some runs where it fires (liveness).
- ST2: the PLAIN-builder's injection applied to the DENSE source reproduces alien_vm.build('HARV_*') bit for
  bit on random tapes.
- ST3: same-physics ruler: p11.assay(vm=HARV) equals alien_pair.assay(vm=HARV) on a sample, i.e. the P-11
  re-execution uses the HARV VM; CVT-R step and P-11 both receive the same module object (asserted).
- ST4: the 17 side-1 copiers remain P-11 competent under HARV_HALT (alien_pair.competent) - reported.

## Budget
<= 45 CPU-min total, python -B, static single interactions and single-site chains only.

## Amendment A1 (2026-10-01T01:47:40Z, from `date -u`; after P1 was scored, BEFORE any P2 or P3 run)
- N1's magnet_rate.py seeds its generators with `hash((sp, ctxname, vname))`, which is per-process randomized
  for str tuples (PYTHONHASHSEED). The source 320/750 and 242/750 cannot be reproduced draw for draw. The P3 stock
  control is amended from "exactly" to "inside the binomial 95% interval of 320/750 (zero) and 242/750 (random)".
  P3 arms here use a fixed string seed. Thresholds for P3 itself are unchanged.
- P1 was scored before this amendment; nothing about P1 is changed.
