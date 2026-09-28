# Pre-registration of the causal tests (written BEFORE causal.py was run)

Forensic 16000006, 2026-09-28. Computational artificial life (z8 VM programs), nothing biological.

## Candidate heritable change (from localization, genealogy + paths700)
`LD DE,3200` at offset 0x14 = bytes 20..22 := `11 00 32` (D0 has `E2 1A E2` there: nop / LD A,(DE) / nop),
immediately before `LD (HL),B ; LDDR*(E7)` at 0x17/0x18. HL is already fixed by `LD HL,553F ; INC HL` in D0. The
hypothesis: fixing DE (block-copy destination; 0x3200 = 0 mod 128, i.e. aligned with HL = 0x40 mod 128) makes the
copy independent of the carried register state.

## Measurement (all tests)
25 seeds x 2 sides, seed tag `F16-CAUSAL`, the world copy criterion `run_nc.copies` against a blank partner
(measure.py), from start states FRESH, SELF_k for k = 1..6 (own blank-partner executions), CONST (0x5A), RANDOM.
- STATE_ROBUST (the task's definition, X-DD-SELFSTATE rule): FRESH > 0 and SELF1 >= 0.25 FRESH.
- FULLY_ROBUST (FR, stricter, added because the k=1 rule was shown to be fooled by period-2/3 state cycles):
  FRESH > 0 and every one of SELF1..SELF6, CONST, RANDOM >= 0.25 FRESH.
- FUNCTIONAL: FRESH >= 0.25 and COMPETENT (run_de cached fresh-start P-11 screen).

## Thresholds
(a) KNOCK-IN into the 5 distinct D0 genomes (epoch 340). Precondition: each unmodified D0 is not FR.
    PASS if >= 4 of 5 knock-ins are FUNCTIONAL and FR. FAIL if <= 1 of 5. PARTIAL otherwise.
(b) REVERT in the 8 most common live competent genomes at epoch 700 (all FR in kcurve.json):
    b1: bytes 20..22 := D0's `E2 1A E2`; b2: only byte 20 := `00` (the immediate pre-transition parent value).
    A revert COUNTS if the reverted genome stays FUNCTIONAL and is not FR. A revert that kills FRESH copying
    is DESTRUCTIVE (uninformative), reported separately.
    PASS if >= 6 of 8 b1 reverts count. FAIL if <= 2 of 8. PARTIAL otherwise. b2 is reported alongside.
(c) CROSS-GRAFT into state-fragile competent genomes from delegates/corpus/q1_partial.jsonl (DENSE, 7ae3,
    rate_full >= 0.5, genome contains E5 or E7, and measured here: FUNCTIONAL and SELF1 < 0.25 FRESH). Take the
    first 12 such genomes in file order. Graft c1 (literal, counts for the verdict): the 3 bytes immediately before
    the first block-copy byte the donor executes from FRESH := `11 00 32`. Graft c2 (adapted, reported only):
    same position, `11 lo hi` with DE = (HL_at_copy + 0x40) mod 0x10000 read from the FRESH trace (the lineage's
    alignment principle rather than its literal bytes; for LDIR the same +0x40 offset).
    Transfer PASS if >= 1 grafted genome (c1) becomes FUNCTIONAL and STATE_ROBUST; STRONG if >= 50%.
(d) All of FRESH / SELF1..6 / CONST / RANDOM are reported for every genome in (a)-(c) and their controls.
    Prediction: knock-in moves CONST and RANDOM from ~0 to >= 0.25 FRESH; revert moves them back to < 0.25 FRESH.

## Verdict rule
SURVIVES: (a) PASS and (b) PASS and (c) transfer PASS. KILLED: (a) FAIL or (b) FAIL. PARTIAL otherwise.
