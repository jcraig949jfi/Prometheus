# W5: design notes (Pass 3 v2 generator, HT-faa9277e02)

Prompt: hecate/programs/_prompts/pass3_v2.md (sha256 2adcfc8d...bd461).
Bound by roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md.
Layer: implemented candidate design only. No treatment code exists and
none was run. The numbers below come from control constructions.

## What the world tests

M9 / lens L7. Morphogen waves always travel in +x. A timing-asymmetric
Hebbian (STDP-like) rule acts on the directed transport rates of each edge.
The question is whether it writes an arrow, antisymmetric
`eps_e > 0`, that points downstream, and whether that arrow still biases
the spread of a morphogen released one decay time (100 time units) after the
waves stop.

There are two readouts. One is structural: the polarity index P. The other is
functional: the downstream bias B of released pulses. A pass needs both.
- P alone passes for a uniform arrow of any size, however tiny (stupid
  explanation 4).
- B alone could pass from centroid drift that has no antisymmetry behind it.

## Why it avoids the earlier failures

- **W1 (positive control could not reach its own threshold).** The positive
  control ran through the real read-out and was checked against every
  threshold before freezing:
  - P = 0.992 against a 0.5 threshold.
  - B = 0.563 against a 0.15 threshold.
- **W1 A1 (positive-control clause folded into success, so the cheat was not
  detected).** No clause refers to the positive control. The cheat meets all
  four success clauses and fires no failure clause.
- **W2 (null twin already near optimal, so clause (b) was unattainable).** The
  twin keeps g and |eps| exactly and destroys only the orientation. Its values
  are P = 0.007 and B = -0.008. Relative clauses also have a twin value in the
  arm slot, from a second independent twin draw (NULL_TWIN_B), so
  "discriminating" is checked, not assumed.
- **W2 A2 (a hard cap made clauses jointly unattainable).** B is bounded in
  [-1, 1] and P in [-1, 1]. The thresholds are well inside the range the
  positive control reaches.
- **Spec deferred to another world.** The spec is self-contained.

## Pre-computed expectation for the treatment (not a result)

With jitter-free waves, eta is fixed so that the equilibrium eps = 0.2. After
the 480-unit wave epoch, eps is about 0.198. The 100-unit quiet epoch
multiplies it by exp(-1), giving about 0.073. By the CALIBRATION rows, that
corresponds to B of about 0.22:
- eps 0.05 gives B 0.153
- eps 0.1 gives B 0.301

The per-cell timing jitter (sd 0.5 cells against a 1-cell neighbour delay)
lowers the mean asymmetry and reverses about 8% of edges.

So the margin over S2 (0.15) is small, and the outcome is not settled in
advance. The qualitative existence of some downstream arrow, however, nearly
follows from the construction of an antisymmetric STDP rule under
one-directional waves. A SIGNAL here would therefore be read as "the
implemented candidate behaves as its linear theory predicts and the arrow is
functionally large enough to survive one decay time". It would not be read as
a novel phenomenon.

Of the two worlds, W6 is the one that could fail most cleanly. W5 is kept
because it is cheap and exact. It is the only world touching M9/L7, which no
earlier world tested.

## Ambiguities resolved

1. **"Travelling morphogen waves".** Imposed kinematically: plane waves,
   speed 1, width 3, period 48 (the torus length), per-cell fixed jitter
   N(0, 0.5). They are not simulated excitable dynamics. This removes
   wave-generation parameters that could fail for reasons unrelated to M9. The
   cost is a weaker morphogenesis leg (the waves are given, not generated).
2. **"D_ij - D_ji".** Each edge has directed rates
   D0*g*(1 +/- eps). The antisymmetric part is 2*D0*g*eps and the symmetric
   part is g (fixed, lognormal, gradient-free).
3. **eta.** Fixed a priori by a normalization rule stated in the spec, not
   tuned to any outcome: the jitter-free analytic equilibrium eps = 0.2, which
   equals the positive-control mean. The analytic STDP integral per passage is
   1.1088 (delay 1, width 3, tau 2).
4. **"After waves stop".** The quiet epoch is one decay time, 1/lambda = 100.
5. **The spec's control.** First written as a timing-symmetric Hebbian arm.
   That arm makes eps identically zero, so it could never fire. It was replaced
   by a reversed-wave control, which must flip the arrow: F4 fires if
   seed-mean P > -0.2. The F4 reference value from controls is the negated
   positive control, P = -0.992.
6. **Twin in the arm slot for relative clauses.** S3 and S4 compare an arm
   against its own twin. For the twin's value, a second independent sign draw
   (NULL_TWIN_B) serves as the twin's twin.
7. **CHEAT.** Twin couplings with the observables overwritten:
   - P computed on |A|
   - upstream pulse mass mirrored downstream

   It is not a realizable coupling field; it only proves the evaluator
   registers success.
8. **Seeds.** 10, paired across arms. Clauses use seed means and seed counts.
   There are no p-values, so the minimum attainable p is not an issue.

## Budget

Control runs for this world took about 12 CPU-seconds in total: revs 0-2 plus
the final run. The cap is 5 core-minutes.
