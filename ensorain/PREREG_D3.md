# D-series Round 3 preregistration: coupling search INSIDE the competent
# regime

Currency: 2026-09-24. Committed after Rounds 1-2 and dev-only sensitivity
work, BEFORE any Round-3 row. Why: Rounds 1-2 sampled dials uniformly
over wide ranges; 97% of lives landed where nothing is learned or the
memory diverges, and a clipped floor compressed couplings (Round 2's own
control failed there). Round 3 gives the coupling thesis its fair test
where learning happens.

## Dev basis for the ranges (dev seeds only; rows d3_dev.jsonl,
## d3_sensitivity.jsonl)

A first local design (ranges as wide as "x/4 around the competent point")
still left 3% of lives learning and 56% diverging (d3_dev.jsonl). A
one-at-a-time scan from the competent point (TT memory, TT world, lam 30,
sweeps 10, scratch 128, cap 192, all extras 0; median held-out R^2 0.93,
75% learn) found (8 dev worlds per level):
  KILLERS  replay_frac >= .05 and err_frac >= .05 at cap 192 (R^2 -0.2 to
           -1.2): the stores are carved out of the cap and shrink the
           model below the world's true size (192 floats) -- the
           compression<->fidelity trade made physical; cap 128 (-0.64);
           surprise_alpha 1.0 (-1.82), .3 (.34); start random (-1.13).
  HARMLESS dream_ratio up to 1 (.89); forget up to .1 (.82-.92); kappa;
           p_restruct up to .3 (.92).
  GRADED   lam low (7.5: .48); scratch small (32: .31); drift .6 (.47);
           noise .3 (.47); p_restruct 1.0 (-.18).
Ranges below are chosen by ONE stated criterion: keep every knob's range
wide enough to span a visible effect while centring capacity with SLACK
(cap >= 192) so that the stores can be tested as a trade rather than as
a guaranteed loss. The criterion never looks at any coupling.

## Design

LOCAL random design, TT memory in a TT world, each dial independent:
  lam log [15, 120]; sweeps int [5, 20]; scratch log-int [64, 512];
  cap log-int [192, 512]; replay_frac [0, .3]; err_frac [0, .15];
  persist int [1, 20]; dream_ratio [0, 1]; surprise_alpha [0, .3];
  disturb [0, .05]; forget [0, .1]; p_restruct [0, 1];
  drift [0, .6]; noise [.05, .25]; kappa_mult log [.25, 4];
  start in {correct, random} (50/50).
N = 4,800 lives, seeds 80000-84799; same trace and NOMEM twin.
Rulers: NLMSE = -log10(held-out MSE vs the current field) -- unclipped,
no floor; held-out R^2 clipped (continuity); L2; EFF.
Analysis: ensorain/d1/analyze.py generalised (primary rulers NLMSE and
EFF; dial set = the 16 varied dials), committed before the rows: main
effects, all-pair couplings with shuffled and planted controls (control
ruler NLMSE), rank-scale check, crossover flags, phases (membership
held-out R^2 >= .5), precursors; discovery = even life, validation = odd.

## Instrument positive control built into the design

p_restruct x start MUST be nominated if the instrument sees real
mechanisms (restructuring can only help a memory that starts in the wrong
mode order; with the correct order it can only perturb). If it is not
nominated, Round 3's nulls are not evidence.

## Round 4 (fixed now)

Every Round-3 nomination other than the planted control gets a
fresh-seed grid (90000+, >= 16 instances per cell, local background at
the range midpoints) with the Round-2 test; replication = interaction
p < .05/k and pattern r > .5.

## Seat predictions (losable)

P1 p_restruct x start nominated, crossover (p .7).
P2 replay x cap nominated: replay hurts at low cap (steals the model's
   capacity) and is neutral-to-helpful with slack (p .5); same for
   err_frac x cap (p .4).
P3 lam x drift nominated -- stability helps without drift and hurts with
   it (p .3).
P4 at most 4 nominations besides the control (p .6).
P5 phases still not supported (p .6).

## Dev check of the final ranges (d3_dev.jsonl, 200 lives, before any
## Round-3 row)

9% of lives reach held-out R^2 >= .5 (18% with correct start, 1% with
random start), 33% diverge, 45 fire (precursor analysis powered). Knobs
that are tolerable one at a time degrade learning JOINTLY -- itself a
Round-3 question (sub- or super-additive damage). The primary ruler
NLMSE is unclipped, so the analysis is not floor-bound at this learning
fraction. Ranges are NOT narrowed further: narrowing toward the learners
would select the answer.
