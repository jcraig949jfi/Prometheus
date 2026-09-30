# HT-37e311ce05 / W5 -- design notes (Pass 3 v2)

Prompt: hecate/programs/_prompts/pass3_v2.md (sha256 2adcfc8d...bd461).
Bound by roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md. Layer: an
implemented candidate with controls only; no treatment exists and no
observation about the treatment has been made.

## What the world tests

Mechanism M5 (coset-bounded sanctions), lenses L5 (cheater coset census)
and L3 (Donoho-Tanner placement). A host pays a symbiont according to how
well the host's m compressed measurements of the symbiont's contribution x
match those of the cooperative contribution x_good (10-sparse, n=64). Every
x in the coset x_good + ker A is paid in full. Under an L1 production cost
the cheapest such x is x_good itself exactly when m is above the
basis-pursuit recovery transition m* for x_good, and a cheaper,
less beneficial alias below it. The question is whether EVOLVED symbionts
(not optimal ones) find those aliases so that the exploitation gap (reward
paid minus benefit delivered) is finished by the end of the transition and
is zero above it, where an L2-cost twin with everything else equal keeps
exploiting the host all the way to m = n.

The three concepts each carry weight: Compressed Sensing supplies the L1
transition that ends exploitation; Measure Theory supplies the coset as the
equivalence class "equal as far as the host can measure"; Symbiosis
supplies the reward/sanction relation that selects on that class.

## Why it avoids the earlier failures of this program

- W1 (INSTRUMENT_FAIL): a clause needed a treatment-minus-control
  difference of 0.3 when the control already sat at 0.99, and the positive
  control did not require the mechanism. Here both success clauses are
  absolute, the positive control IS the mechanism's endpoint (the LP
  optimum), and ATTAINABILITY.json shows it meets both clauses (0.93, 0.0)
  while the twin meets neither (0.63, 0.17).
- W4 (SPEC_UNATTAINABLE): two mechanisms conjoined in one success
  criterion, and the null twin already satisfied one conjunct. Here there is
  one mechanism, and each clause was checked separately for attainability
  and discrimination on control rows before freezing.
- No clause refers to another world; m* is calibrated inside controls.py
  (20 draws per m) and equals the spec's frozen 28.

## Controls

- POSITIVE_CONTROL: minimum-L1 element of the coset (scipy HiGHS LP) per
  (seed, m); reward 1 by construction.
- NULL_TWIN: population evolved under cost c*||x||_2^2, same world, reward,
  matrices, selection, mutation, population, generations; cost of x_good is
  10 under both costs, so the cooperator starts at equal fitness.
- CHEAT: gap injected as 0.8 below m*, 0 above, genome stored as the honest
  cooperator. The audit recomputes each row's gap from its stored genome and
  world seed: it flags all 40 injected-and-different rows and no PC or twin
  row; the ruler also fires on CHEAT (sensitivity).

## Ambiguities resolved

1. "Positive control (effect present by construction)" for an evolutionary
   claim: read as the optimal cheater that the mechanism says selection
   should approach; it is not run through the evolutionary search, so the
   world can fail if search does not reach it (that is F2).
2. Reward is soft (Gaussian in relative measurement mismatch, tau=0.25):
   a hard tolerance made evolution abandon the reward entirely in the
   exploration run (reward -> 0 within 300 generations at tau=0.05).
   Exploration runs were of the NULL_TWIN dynamics only (L2 cost) and of the
   LP; the L1-cost evolution (treatment) was never run.
3. k was raised from 6 to 10 during exploration so that m* (28) sits inside
   the m grid with room on both sides; this preceded the first spec.
4. Observable per (seed, m) is the population median gap; clauses read the
   10-seed mean curve.
5. CHEAT rows at m >= m* inject gap 0, equal to the honest value, so they are
   not falsified; cheat_detected counts only the rows that were falsified.
6. Revision 1 replaced sharpness by completion after seeing rev0 values
   (PC 0.659 vs threshold 0.6 was a knife-edge); recorded in
   ATTAINABILITY.json with rev0 rows kept in _rev0/.

## Known risks for the treatment (not repaired, stated)

- The evolved population's reward is below 1 (twin reward about 0.85-0.95),
  so the treatment gap has a floor set by tau, not by the coset: see stupid
  explanation 1. S2 (<= 0.05) could fail for this reason alone.
- A success would largely mean "selection approximately solves basis
  pursuit", which is known compressed-sensing theory acting through a
  fitness function (the alternative explanation). The symbiosis content is
  the claim that a sanctioning host's exposure is set by its sensing
  geometry, not by its effort.
