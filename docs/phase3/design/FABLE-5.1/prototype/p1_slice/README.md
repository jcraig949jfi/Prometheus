# P1 calibration slice -- a working prototype of the design's central instrument

Architect: FABLE-5.1 (seat Dionysus). Built and run 2026-10-01 on SKULLPORT (M1).

**What this is.** The smallest end-to-end version of experiment P1 in
RSE_ARCHITECTURE.md: a world that demands BUILD, a tiny organism machine,
designed organisms with known answers, the rulers, and the qualification gate
as code. About 1,900 lines of Python.

**What it is not.** It is not the workspace machine, not a Prometheus engine,
and not a result about reasoning. The organisms are designed, so there is
nothing to discover. In the design's terms everything below is a C0
observation about an instrument, on one host, by one author.

**Why it exists.** A design that has never run is worth less than one whose
central part has. This answers three questions the design could otherwise
only assert: does class exclusion work mechanically; what does the gate catch;
and how fast is a compiled kernel with a world in the loop.

## Results in one table

| question | result | where |
|---|---|---|
| Does the compiled kernel match an independently written oracle? | 3,672 comparisons, 0 mismatches; a deliberately wrong oracle is caught | differential_test.py |
| Did the first run of the gate pass? | **No.** One preregistered verdict came back INDETERMINATE. The design was underpowered in three cells and I had not checked. | RECEIPT_qualify_v1_GATE_FAILED.json, PREREG_v2.md |
| Did the amended gate pass, on fresh sealed lives, with no threshold moved? | Yes. All 26 preregistered verdict cells and 8 fire tests as expected; the power gate covered 23 of the cells. | RECEIPT_qualify.json |
| Throughput with the world in the loop | 1.70 billion organism instructions per second on 12 threads (1.86 million lives per second) | RECEIPT_qualify.json, section G |
| Search power against planted targets | depends first on the acceptance rule: 24/24, 9/24 or 1/24 at one missing instruction | RECEIPT_reach.json |
| Were my forecasts right? | 5 of 6. Brier 0.179 against 0.250 for always saying one half. | RECEIPT_reach.json |
| What did blind search find from an empty program? | one builder in 24 lineages, with a different mechanism from the designed one | RECEIPT_found_exploratory.json (exploratory) |

## The world and the organism

RETAIN. A life is 8 episodes of 6 trials. A hidden mapping from 8 stimuli to 4
responses is fixed for the life. After each response the correct answer is
shown. The harness zeroes the organism's fast state (registers and fast
memory) at every episode boundary. The persistent store is not reset.

A BUILD probe is the first presentation in an episode of a stimulus met in an
earlier episode, counted once per stimulus per life. For any policy that
carries nothing across an episode boundary, each probe is correct with
probability exactly 1/4, independently. So the number of correct probes is
exactly binomial under the null, and an organism that beats it is certified
outside that class, whatever its mechanism.

WM-mini. Eight 16-bit registers, a fast memory, a persistent store, 19
opcodes, integer only, every word decodes, no backward jumps.

## The gate (qualify.py)

Calibration set on 2,400 sealed lives, 18,854 probes each:

    organism      probes correct   BUILD   HOLD    certified
    builder(8)    18854  (1.000)   PASS    PASS    >= 0.999  (2.00 bits per stimulus)
    builder(6)    15355  (0.814)   PASS    PASS    >= 0.800  (1.68)
    builder(4)    11768  (0.624)   PASS    PASS    >= 0.606  (1.28)
    builder(2)     8249  (0.438)   PASS    PASS    >= 0.420  (0.75)
    builder(0)     4746  (0.252)   FAIL    FAIL
    holder(8)      4678  (0.248)   FAIL    PASS
    constant       4746  (0.252)   FAIL    FAIL
    lookup         4766  (0.253)   FAIL    FAIL
    leak_reader    4667  (0.248)   FAIL    FAIL

- builder(m) stores the first m of the 8 mappings. Its true probe rate is
  m/8 + (1 - m/8)/4, a known answer. Observed rates match, stored stimuli are
  always correct, unstored ones sit at chance, and the certified lower bound
  never exceeds the true value.
- The holder does the same thing in fast memory. It passes HOLD and fails
  BUILD. That is the distinction the ruler exists to make.
- At this sample size the ruler passes at accuracy 0.2651 and detects 0.2686
  with power 0.8, against chance 0.25. Its false-positive bound is 1e-6.

Causal rulers:

- Store interchange. Swap the persistent store between two lives at an
  episode boundary. The builder followed the donor's hidden mapping on 5,602
  of 5,602 eligible trials (FLIP). The holder did not (NO-EFFECT, 1,465 of
  5,602, chance). A sham swap with the cells permuted did not (NO-EFFECT).
- Lesion. Zeroing the store cells the builder uses takes it to chance.
  Zeroing the same number of unused cells does nothing.
- Reset equivalence. After the harness's reset, behaviour equals that of a
  fresh machine holding only the store: 0 mismatches in 2,400 trials.

Fire tests. Each breaks one thing on purpose:

| | what is broken | what must happen | happened |
|---|---|---|---|
| FT1 | the harness stops resetting fast memory | the BUILD ruler is fooled (the holder passes), and the reset-equivalence check exposes it | yes |
| FT2 | the world's observation is the answer | the never-seen-stimulus check and the leak probe both report a leak | yes |
| FT3 | report on a life the organism was built from; search on a sealed life | both refused | yes |
| FT4 | the ruler is given the wrong null | the calibration table no longer matches, so the gate refuses | yes |
| FT5 | a loader admits nothing | INDETERMINATE, not PASS | yes |
| FT6 | fabricated records fed to the ruler | all three verdicts reachable | yes |
| FT7 | store writes switched off | the positive control stops passing | yes |
| FT8 | the power gate is given the v1 sample sizes | it calls them underpowered | yes |

FT1 is the one to remember. With a broken harness the ruler alone says PASS
for an organism that cannot build. Only a separate check on the harness
catches it. A certificate is only as good as the control of the stores.

## The failure, and what it showed

The first run failed its own gate. I had preregistered that the interchange
ruler would return NO-EFFECT for the holder. It returned INDETERMINATE: 722
of 2,785, which is at chance, but not enough trials to show "within 0.05 of
chance" at 1e-6. Exact power for that cell was 0.865. Two other cell types
were at 0.884 and 0.978 and happened to pass.

I had frozen thresholds and sample sizes without computing whether the
expected verdicts were attainable. The design's own requirement MEAS-08 says
not to. The amendment moves no threshold. It adds a gate that counts eligible
trials from the schedules alone, before any organism runs, computes exact
power for every preregistered verdict, and refuses to run below 0.99. Then it
runs on sealed lives the first run never touched.

This is the most useful thing the prototype produced. The requirement was
already written, I broke it anyway within hours, and what caught it was a
preregistered table compared by code. A rule in a document did not stop the
error. A gate in the runner now does.

## Search power (reach.py)

Target: the 8-instruction minimal builder. Knock out d instructions, then let
blind single-point mutation try to put them back, 200,000 proposals per
lineage, 24 lineages per cell. A lineage counts only if it is perfect on the
training block, at least 0.9 on selection lives it never saw, and passes the
BUILD ruler on sealed lives. The 24 lineages of a cell share the target and
the training lives and differ only in search seed, so in the design's terms
they are independence level I1, not independent founders (I2).

    recovered of 24        d=0    d=1    d=2    d=3    d=8 (empty program)
    margin rule            24     24     0      0      0
    strict rule            24      9     1      0      0
    neutral rule           24      1     0      1      1

    random programs: 0 of 2,000,000 reach 0.9 (best 42 of 126 probes)
    50.5 million proposals in 426 s on 12 threads

- The acceptance rule is a first-order factor. With one instruction missing,
  recovery was 24 of 24, 9 of 24 or 1 of 24 depending only on the rule.
- No rule dominates. The rule that was best at d=1 never recovered anything
  at d>=2. The rule that was worst at d=1 was the only one to find a builder
  from an empty program.
- Reach falls steeply with needle size under every rule.
- With 24 lineages, 1 of 24 has an exact 95% interval of roughly 0.1% to 21%.
  These are small counts. The pattern across rules is the finding, not any
  single cell.

Forecast F3 was wrong. I gave 0.97 to "no rule recovers from an empty
program". One lineage did. My stated reasoning was that the builder is all or
nothing, so nothing rewards partial progress. That was false: partial builders
exist that score above chance, and a tie-accepting walk can climb through
them. Five of six forecasts held; the miss is the informative one.

## What blind search found (exploratory, after the fact)

inspect_found.py replays five of the cells with recoveries (the three
neutral-rule cells and the two strict-rule cells) and puts each of the 13
organisms found there through the same rulers. It does not replay the
margin-rule cell at one missing instruction, whose 24 recoveries are the
easy case. It was written after the reach receipt existed and is not
preregistered.

All 13 found organisms pass BUILD on 4,711 sealed probes at 1.000, flip under
store interchange on 5,566 of 5,566 trials, do not flip under the sham, fall
to chance when the store is zeroed, and pass reset equivalence.

The one found from an empty program:

    0  PH   r5            r5 = phase
    1  XOR  r6, r4, r7    r6 = r4 xor r7
    2  IN   r7            r7 = observation
    3  STR  r1, r7        r1 = store[r7]
    4  SUB  r4, r0, r5    r4 = r0 - r5
    5  SKEQ r5, r3        skip next if r5 == r3
    6  STW  r6, r7        store[r6] = r7
    7  OUT  r1            answer r1

It has no jump. The designed builder dispatches on phase with a jump. This one
gates its write with a comparison against a register it never writes (r3,
always zero), and carries the stimulus from the first phase to the second by
xor-ing it with another register that is zero at that moment. It uses the
harness's zero-initialised registers as free constants.

Two things follow, both small and both real:

- The rulers certified it without anyone understanding it. I read the
  mechanism afterwards. That is the order the design asks for.
- Same certified level, different mechanism. The Sisyphus report notes the
  same habit in the old byte soups: zero-register initialisation used as a
  free constant. In Phase 3 terms the register reset is a world variable and
  should be swept, not assumed.

## What this does not show

- Nothing about COMPRESS, COMPOSE or RECURSE. The slice covers HOLD and BUILD.
- Nothing about the real workspace machine. WM-mini has no blocks, tags, calls
  or rent. Its store-write and store-read instructions are capability-specific
  primitives, so the from-scratch find is scaffold level S3, not S2.
- Nothing at independence level I3. Kernel and oracle have one author.
- The sealed set is a range check, not a broker with a commit-reveal protocol.
- The search-power curve is one target, one substrate, one search seed.
- Throughput is for a tiny machine. The design keeps a wide margin (it assumes
  100 million instructions per second for the real kernel, against 1.7 billion
  measured here).

## Files

    wm_mini.py                           compiled kernel: machine and world
    oracle.py                            separately written pure-Python version
    differential_test.py                 kernel against oracle, with a fire test
    organisms.py                         designed organisms
    rulers.py                            exact-arithmetic rulers, harness, census, power
    qualify.py                           the gate
    reach.py                             search-power curve, with scored forecasts
    inspect_found.py                     exploratory look at found organisms
    PREREG.md, PREREG_v2.md              what was fixed before each run
    RECEIPT_qualify_v1_GATE_FAILED.json  first run (failed)
    RECEIPT_qualify.json                 amended run (passed)
    RECEIPT_reach.json                   search-power run
    RECEIPT_found_exploratory.json       exploratory inspection

To reproduce, from this directory, with numpy and numba installed:

    python differential_test.py
    python qualify.py --power-only
    python qualify.py
    python reach.py
    python inspect_found.py

The runs are deterministic. Timing fields and the timestamp differ between
runs; every count and verdict should not.
