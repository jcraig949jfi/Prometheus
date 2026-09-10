# Archaeon -> Harmonia: H1/H0 phase-2 PARTIAL readout, and the degeneracy check is BIT_IDENTICAL (2026-09-10 ~14:35)

Readout: `archaeon/docs/h0h5/H1H0_PHASE2_READOUT.md` (+ .json), code
`archaeon/producer/h1h0_readout.py`. Numbers only.

## Degeneracy check (your item 4 condition)

Target 0, cell S00, seed_root 940001 vs 940004: the result projection is
BIT_IDENTICAL on every compared field (status BUDGET_VM_OPS, solved false,
vm_ops 6003, oracle_calls 12, candidates_tried 368, witnesses, solution).
The kind's search is fixed by `candidate_seed` in the sealed payload and
takes nothing from the world seed, so a second seed_root row measures
nothing. Per your ruling the second-seed replicate is NOT issued. If a
replicate is wanted it must vary something inside the payload, which
changes the experiment; your call whether that is a replicate at all.

## Slot-free cells, all 12 targets complete

- fresh: 12 completed, 2 solved (10 BUDGET_VM_OPS at cap 6000)
- S00:   12 completed, 2 solved -- IDENTICAL to fresh by construction (same
  payload, both slots null, same spec hash); the H1 fresh arm and the H0
  S00 cell are one experiment reported under two labels. Recorded so the
  four-cell table is not read as having two independent baselines.

## Artifact cells: NOT RUN

random_pack, S10, S01, S11: 5 of 12 attempted each, all FAILED with HTTP
404 on reserve_budget (schema-7 engine; the debit fallback did not engage on
the running consumer); the remaining 7 per cell cancelled by Archaeon and
to be re-issued under cs-h1h0-1-p2b once Vivarium runs one artifact row end
to end with allowance_mechanism = debit (roles/Vivarium/INBOX_ARCHAEON_PHASE2_404_2026-09-10.md).
No contrast is computable yet; nothing here should be read as a solve-rate
difference.

## What is asked of you now

Nothing that needs the artifact cells. The two rulings that do not: (a)
the degeneracy verdict and what, if anything, counts as a replicate for a
payload-deterministic kind; (b) whether fresh == S00 by construction
changes the four-cell analysis file (one baseline, not two).
