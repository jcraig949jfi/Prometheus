# ALIEN-CIRCUITRY-01 (AC-01)

Question: when an explicit inference frontier is combinatorially large, does its decision-relevant consequence
structure occupy a substantially smaller representational space, and can that structure be used to avoid search
while preserving mechanically verified correctness?

Status (2026-09-12): **Phase A/B, instrument construction.** No compression method has been implemented, run, or
inspected. See `RECEIPT_PHASE_AB.md` for the current receipt and `PREREGISTRATION_DRAFT.md` for proposed (not
committed) kill criteria. The Datalog universe from the first receipt is rejected; see `DATALOG_FAILURE.md`.

## Layout

```
alien_circuitry/
  README.md                     this file
  DATALOG_FAILURE.md            the rejected first universe, classified INSTRUMENTALLY INSUFFICIENT, with measurements
  RECEIPT_PHASE_AB.md           Phase A/B receipt
  PREREGISTRATION_DRAFT.md      proposed kill thresholds and justification (draft; nothing frozen)
  universe/
    directed_rewriting.py       operational semantics, word indexing, vectorised transition generation, layered BFS
    presentations.py            U-A1 ABELIAN, U-A2 BRAID_B3, U-A3 candidate BRAID_B3_ONEWAY (diagnostic), PC2 clones
    enumerate.py                exhaustive universal graph + exact distance chart D (reverse BFS per target)
    metrics.py                  strata, trap topology, target stats, BFS/bi-BFS/oracle baselines, D/M charts, mask proposal
  controls/construct.py         NC1-A, NC1-B, PC3, NC2 construction (no compressor is run)
  diagnostics/target_classes.py Phase A diagnostics: traps by target class; one-way relator variant
  tests/test_universe.py        determinism, canonicalisation, scalar-vs-vector semantics, D consistency, baselines agree,
                                budget accounting, trap definition, masks, controls behave, chart accounting
  evidence/instrument_failure/  verbatim scratchpad probes + results that falsified the Datalog universe (PROVENANCE.md)
  results/                      JSON results per (presentation, L) and diagnostics; sweep_log.txt
  data/                         (gitignored) enumerated graphs and D charts as .npz, with .hash.json beside each
  run_phase_ab.py               runner: python -m alien_circuitry.run_phase_ab BRAID_B3 10
```

## Reproduce

```
python -m pytest alien_circuitry/tests -q
python -m alien_circuitry.run_phase_ab BRAID_B3 10          # ~45 s, writes results/BRAID_B3_L10.json and data/*.npz
python -m alien_circuitry.run_phase_ab ABELIAN 10
python -m alien_circuitry.diagnostics.target_classes BRAID_B3 10 reduced3
python -m alien_circuitry.diagnostics.target_classes BRAID_B3_ONEWAY 10 nf2
```

Everything is deterministic: state indexing is a bijection, transitions are generated in a fixed order, sampling uses
seed 20260912, and every results file carries sha256 of the nominal edge list, the distinct edge list and D.

## Doctrine carried from the first receipt

- A target-conditioned trap needs an action that is both irreversible and non-monotone.
- The honest uninformed baseline is the strongest uninformed search for the universe, never plain forward BFS by default.
- Compression ratios are measured against an entropy-coded sparse reference, never raw dense bytes.
- Problem-level splits hold out nothing in a universal graph; masks are hashed over states, entries and target columns.
- Rediscovery of known mathematics (exponent vectors, Garside normal form, confluence) is instrument success, not alien circuitry.
