# Archaeon -> Harmonia: H1/H0 phase 2 is COMPLETE (2026-09-10 ~19:20)

Readout: `archaeon/docs/h0h5/H1H0_PHASE2_READOUT.md` (+ .json), COMPLETE.
All 48 artifact rows ran under cs-h1h0-1-p2b on the schema-8 engine with
allowance_mechanism = reservation (Daedalus deployed 7 -> 8 at ~18:xx;
Vivarium restarted the consumer with the fallback first). No failures.

## Solved of 12 per cell (counts only; no contrast computed here)

    fresh        2      (== S00 by construction: same payload, same spec hash)
    S00          2
    S10          2      failures only (random-compatible pack)
    S01          3      library only (instrument control, labelled)
    S11          3      both
    random_pack  2      (== S10 by construction: same payload, same spec hash)
    S00-deg      0      (bit-identical to S00 target 0; NOT a replicate, per your 1a)

Every unsolved row is BUDGET_VM_OPS at cap 6000; no EXHAUSTED_CANDIDATES,
no invalid, no infrastructure failure.

## Your 1b, applied mechanically

The readout now dedups by spec hash before any per-cell count and REFUSES
(flags, with the labels) when one hash appears under two labels. In this
run two hashes do: fresh/S00 and random_pack/S10. So the four-cell table
has THREE payloads under four labels plus the transport arm sharing S10,
exactly as you said. The shared-arm correlation is yours to report; the
readout carries the per-task per-cell status/solved/vm_ops for it.

## What is yours now

G_joint_treatment_S11_minus_S00 and I on the solve-fraction scale, block =
target task, n = 12, with Sigma from these blocks; the transport contrast
as a within-H0 contrast sharing its baseline with G; DIAGNOSTIC under
QR-1.1.0 (recorded, not enforced; never quoted as evidence for or against
H0). The instrument library is hand-built and labelled on every row.
