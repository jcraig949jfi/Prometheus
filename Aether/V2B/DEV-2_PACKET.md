# V2-B DEV-2 design/repair packet -- P1 mobility observatory

Cycle 2, DEV window 2 (opened 2026-10-04T19:37Z). Previous TEST: TEST-1 (prov0 QUALIFIED; content transforms in place
but does not travel).

## Limiting layer
The obvious physics bottleneck after TEST-1 is the frozen medium (TH-009). But "frozen" had never been MEASURED
against the directive's exclusions (injected perturbation, counters, cycling, residue). A mobile-medium law search
with no P1 ruler would have nothing honest to score against. So the narrowest layer is the P1 RULER.

## Built
- `Aether/observatory/aeth_mobility.py`:
  - MobilityMeter: a pure function of the state sequence giving turnover early/late, persistence, revisit share
    (L=8), constant-step counter share and active-site share;
  - provenance-based residue share, mean age, chain share and mutation share;
  - `classify` with first-failing-clause classes FROZEN / DECAYING / CYCLING / COUNTER / LOCALISED /
    ENDOGENOUSLY_MOBILE;
  - the followed window runs under the prov0 shadow, so the physics self-check holds.
- `Aether/test/test_aeth_mobility.py`: 6 synthetic qualification fixtures, one per class, including a travelling-pattern
  calibration positive.

## Repairs
- The first pilot showed add's large turnover would pass a naive mobility test. It is an unconditional COUNTER
  (constant-step increments at a few hot targets). The counter and active-share measures were added for that reason.
- A decaying fixture was itself mis-built (payload-only rate below the floor) and was corrected.

## DEV pilot (seed 100; calibration only)

| law/arm | class | turnover_late | revisit | counter | active |
|---|---|---|---|---|---|
| v1 OFF | FROZEN | 0.0006 | 0.75 | 0.00 | 0.05 |
| v1 ON | CYCLING | 0.0091 | 0.48 | 0.05 | 0.31 |
| add OFF | COUNTER | 0.0411 | 0.01 | 0.83 | 0.32 |
| rcv OFF | FROZEN | 0.0010 | 0.68 | 0.00 | 0.08 |
| fwd OFF | FROZEN | 0.0010 | 0.46 | 0.00 | 0.18 |
| rcv_add OFF | COUNTER | 0.0194 | 0.02 | 0.66 | 0.30 |
| rcv_str OFF | FROZEN | 0.0005 | 0.62 | 0.01 | 0.09 |
| rcv_adr OFF | COUNTER | 0.0222 | 0.03 | 0.81 | 0.24 |

## Frozen next TEST
Aether/V2B/TEST-2/PREREGISTRATION.md.

## Questions for external review
1. Is a constant-step detector enough to exclude "unconditional counters"? Could a law count with a state-dependent
   step and pass?
2. Should P1 require that turnover be CAUSALLY dependent on medium state (a twin test), not only non-trivial in form?
3. Is a 400-tick window after a 1500-tick warm-up long enough to call a medium frozen?
