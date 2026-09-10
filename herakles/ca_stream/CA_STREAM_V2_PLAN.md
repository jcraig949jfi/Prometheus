# ca_stream_v2 alpha plan. PREPARED, UNISSUED.

**Herakles, 2026-09-10.** D-18 is the operator's decision. Nothing here runs
until that decision. `reset_v2.py` stays unapplied and a test asserts the
alpha does not import it.

This exists so the re-run is ONE COMMAND on the day rather than a design
session.

---

## The one command

    python -m herakles.ca_stream.run_alpha_v2

That module does not exist yet, deliberately: writing it would be applying the
amendment. Everything it needs is decided below, so writing it is
transcription rather than design.

## Frozen configuration

    reset            seeded Bernoulli, density 0.5           (D-18 v1)
    reset seed       sha256("ca_stream.d18.v1|<root>|<position>")
    reset_root       20260910
    horizon          8       CHOSEN FROM EVIDENCE, not inherited
    n_cells          31
    ports            (0,)
    injection        overwrite, unchanged from v1
    order            inject -> exactly one CA step -> read      unchanged
    readout          capacity-limited linear over the current lattice,
                     32 parameters, one closed-form ridge solve, lambda 1.0
    partitions       64 train / 64 dev / 128 confirmation       unchanged
    tasks            delayed_recall d=0..3, temporal_xor d=0,1  unchanged

**Why horizon 8 and not 16.** Measured, 400 samples: at 16 steps between 37
and 52 per cent of resets have forgotten the input entirely for the four
responsive rules, and 81 per cent for `exp`. At 8, `particle2` retains it in
91 per cent and the others in about 77.

## The order of operations on the day

1. **Leakage probe FIRST, before any readout is fitted.** Fit the declared
   readout on reset lattices with NO input injected. Recorded on development
   partitions only. If it beats the base rate, STOP: the reset is correlated
   with the target and no downstream number means anything.
   Measured on 2026-09-10: GKL 0.5234 against a base rate of 0.5234, par
   0.5052. No leakage. Re-run it anyway; it is cheap and it is the gate.
2. **Controls, unchanged.** Shift register, shift-plus-XOR at each declared
   delay, direct input at equalised width, frozen random. The CA number is
   unreadable without them.
3. **The six genomes.**
4. **Confirmation scored once**, after everything above is frozen.

## What must be reported, and one prediction made in advance

Relaxation, driven response, the frozen horizon, and the untouched
confirmation partition.

**Predicted before the run, so it cannot be explained afterwards:** `maj` and
`exp` should score AT BASELINE. They forget the input, measured directly, so
they have nothing to score with. **If either beats baseline, that is evidence
of leakage, not of computation**, and the leakage probe should be re-run
before the number is believed.

The other four carry the input forward and may or may not be readable by a
LINEAR readout. A low score from them is not evidence of no memory: the shift
register has perfect memory and still fails temporal XOR, because XOR of two
stored bits is not linear in them.

## What is still forbidden after the re-run

Rule search. It is beta and it comes after, not before. A search run before
the baseline configuration has a number would have nothing to compare against.

## What makes this v2 rather than an edit

Changing the reset changes what every v1 number meant. `ca_stream_v1` keeps
its all-zero reset and its obstruction result, which stands as recorded for
the six rules under a single port. A new kind, a new identity, both readable.
