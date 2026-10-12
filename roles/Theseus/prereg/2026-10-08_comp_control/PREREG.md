# THESEUS-30a preregistration -- can the composition detector fire? (constructive controls)

Currency: 2026-10-08. Committed before any run of theseus/synth/comp_control.py.

## Why

THESEUS-23b found 0 two-part compositions in every arm and could not separate a real
wall from a blind detector, because the v0 op set has no primitive that is inert
alone. This adds two CONDITIONAL primitives (substrate.py: "inject" x += a*M[dst];
"modulate" x += a*M[dst]*S[src]) that read only the memory field, which only
"remember" writes. They are excluded from the v0 random-op pool (BASIC_OPS unchanged,
18 ops), so every earlier configuration is unaffected.

## Design

40 genomes per class, seed 20261008, detector = composition._job with frozen v0_1
EPS 1.63 / TAU 4.31:
  planted    writer block (1-2 remember) + reader block (1-2 inject/modulate on the
             written memory), either order -- each block inert alone by construction
  neg_active two rules that each act alone (from diffuse/decay/advect/mirror/rank)
  neg_recall writer + recall (recall is active alone)
  neg_inert  2-3 remember rules only (inert as a whole)

## Decision rule

  DETECTOR VALID   planted flagged >= 80% AND every negative class flagged <= 5%
  DETECTOR WEAK    planted flagged in [20%, 80%) with negatives <= 5%: report which
                   planted genomes fail and on which clause (whole not > TAU, or a
                   part not <= EPS)
  DETECTOR BLIND   planted flagged < 20%
  DETECTOR LEAKY   any negative class flagged > 5%

## Predictions

C1 DETECTOR VALID.                                              p = 0.55
C2 every negative class flagged <= 5%.                          p = 0.9
C3 if planted genomes fail, it is mostly on "whole not > TAU".  p = 0.7

Compute: 160 genomes, small (<= 3 rules) -> minutes.
