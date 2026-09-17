# Archaeon -> Theophrastus: two contrast families from the WSE survey v01 (delegation)

From: Archaeon[m2-411504ab], 2026-09-16 ~20:40 UTC. Kind: delegation.
Authority: the operator's directive of 2026-09-16 (roles/Archaeon/prompts/
2026-09-16_workspace_ecology/00_OPERATOR_DIRECTIVE.md, sections III and
XVII): "Whenever Archaeon finds an interesting adaptation, Theophrastus
should expand outward ... Do not spend the full budget repeatedly
reproducing the central cell while leaving its neighborhood unknown."
Reporting: a comms report to Archaeon with committed paths; dispositions
in your closed set (NO_SIGNAL / WEAK_SIGNAL / REPRODUCIBLE_SIGNAL /
REPRESENTATION_BLOCKED / INSTRUMENT_BLOCKED). No discovery language.

## What exists (all on main at b7518c392)

    archaeon/wse/DESIGN_v0.1.md          the preregistered grammar, knobs,
                                         economics, interventions, predicates
    archaeon/wse/READOUT_v01.md          the survey read by failure shape
    archaeon/wse/ledgers/wse-survey-v01/ 126 rows (world hash, knobs, seed,
                                         economics, elite manifest, trace,
                                         held-out rewards, intervention
                                         vector + erase ceiling, K-curve)
    archaeon/wse/{worlds,economics,evolve,interventions,controls,survey,
                  readout}.py            every cell is replayable from
                                         (campaign_seed, world_id, regime,
                                         seed); no LLM anywhere; timing-free
                                         digest fe1142bf30484f15...

Substrate is Proteus's player VM unmodified; the loop is
archaeon.wse.evolve.run_cell; evaluate() takes a manifest and episodes;
episodes_for(spec, campaign_seed, family, index, n) gives held-out
families that never overlap training.

## Contrast family 1 -- the cost-extinction boundary (Shape A)

Central cell: W0 (K=1 D=1 delay=0), E0 vs E1. Under E0 two of three seeds
solve (held-out 1.000); under E1 (alpha 0.02/kop, beta 0.01/64 words)
all three seeds go to persist=none, 2 ops, reward 0 within ~3
generations. Same for E2 and E3 and for every other cell.
Stencil to run (each cell: N=200, G=100, E=24, seeds 1,2,3; the runner's
--only flag and a Regime(name, alpha, beta) are all you need):
  - alpha in {0.02, 0.005, 0.001, 0.0002, 0} with beta = 0 on W0 and W1_d1
  - beta  in {0.01, 0.0025, 0.0005, 0} with alpha = 0 on the same two cells
  - the same alpha sweep at N = 400 (does the boundary move with
    population size, i.e. is it a drift/selection-strength effect?)
Controls the stencil needs: the E0 cell itself (positive), a cost applied
to a population SEEDED with the W0 solver (if the solver survives E1
when it starts alive, extinction is about ORDER, not scale -- that is the
hypothesis Archaeon's v0.2 cost ramp presupposes, and you can falsify it
first). The W0 solver manifests are in rows W0__E0__s1.json / s2.json
under final_elite_manifests.
Question: where between alpha 0.02 and 0 does the E0 behaviour reappear,
and is the boundary sharp (phase-like) or a slope? Report per cell the
persist-share trace (rows carry persist_shares per generation).

## Contrast family 2 -- the 1/K plateau of the one-register solver (Shape B)

Central cells: W2_K2 E0 s1 (held 0.500), W3_K2 E0 s1 (0.562), and their
K-curves 1.00/0.50/0.25/0.12/0.06. Every elite that solved anything has
ERASE_REGS = ERASE_ALL, ERASE_TAPE = SCRAMBLE_* = 0.000.
Stencil:
  - the same elites (manifests in the rows) evaluated on ask_mode=one vs
    all, and on interleave=random vs sequential, at K = 2,4,8 (no
    evolution; evaluate() only): does the plateau stay at 1/K?
  - the shortcut-kill knob Archaeon will add in v0.2 (ask order = reverse
    of put order) applied to the SAME elites: predicted plateau 1/K^2 for
    a last-value organism. If the plateau does not move, the elites are
    not last-value organisms and Shape B is misread.
  - RESET_IP vs ERASE_REGS on W2_K4 s1 and W3_K4 s3 (the two elites whose
    instruction pointer carries reward: drops 0.12 and 0.25) at 96
    episodes, three intervention seeds: is the ip contribution stable?
Note the ceiling: erase-type interventions are bounded by the printed
erase_ceiling (share of asks whose stream completed before the
intervention tick); compare drops with it, not with 1.0.

## Not asked

Do not evolve new populations on the harder cells (W4-W10): Archaeon's
v0.2 owns the world mutations there (READOUT s8) and will preregister
them. Do not touch the v01 rows. If a stencil needs a knob the grammar
lacks, file it to Archaeon as a one-line requirement, not a patch.

## Report back

One comms report: per stencil cell the disposition, the numbers, the
paths; the cells you did NOT run and why (your standing rule). Archaeon
consumes it in DESIGN_v0.2.
