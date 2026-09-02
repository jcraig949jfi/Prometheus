# V1-C Prospective Gap Surfacing — Report

Question (charter s10-s11): do high-ranked missing-cell candidates yield
useful experiments more often or more cheaply than controls? This is
PROSPECTIVE by construction; V1 delivers the blinded apparatus and the first
observed chain link, not a verdict.

## Slates (registered 2026-09-02, before any downstream consumption)

Three 5-cell slates on mechanism x substrate_class (snapshot
SN-1a257d803512, 224 eligible unobserved cells; the 5 cells whose method was
exposed by V0-era registrations were excluded as blinding-burned):
- marginal-contraction top-5;
- uniform-random 5 (seed 7);
- frequency-weighted random 5 (seed 8).

All 15 registered as `ew.hypotheses` MISSING_CELL rows with method
`v1c_sealed` — downstream agents cannot see which slate a cell belongs to.
True mapping: `derived/v1c_sealed_methods.json` (uncommitted), committed
hash `a11168818abbc10e2b57e3c84a6a5d18114c2971779f29ad25ff67ac210aba8b` in
`benchmarks/gap_prospective_v1.json`.

## Adjudication protocol (frozen)

Chain to track per cell: gap proposed -> experiment formulated -> prediction
committed -> executed -> admissible evidence returned -> verdict. Fraction
of slate reaching each stage within 60 days, marginal vs the two controls.
G12: an experiment formulated FROM a wiki gap validates the gap ONLY via
admissible evidence adjudicated by non-wiki instruments.

    G11 (this session) = PENDING_PROSPECTIVE  (apparatus qualified, no verdict)

## First observed chain link (exploratory)

During V1-B, the T3 wiki-arm designer spontaneously retrieved gap
`H-bac36ae694a2` (projection_equivalence x lmfdb_arithmetic — a V0-era,
method-exposed cell, hence NOT part of the blinded slates) and produced a
full preregistered design to fill it (`v1b/proposals/T3_wiki.md`). Chain
state: gap proposed -> experiment formulated. Nothing further is claimed;
under G12 this cannot count as gap validation, and because that cell's
method was public it cannot enter the marginal-vs-control comparison.

## What V0 already measured (context, frozen)

Held-out missing-cell ranking at 99 coordinates put marginal (0.787) above
CP (0.735), Tucker (0.633), TT (0.364 < random 0.5). Hence the blinded
slates use marginal as the "treatment" ranking and the tensor plays no role
in V1-C.
