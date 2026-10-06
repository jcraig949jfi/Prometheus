# PREREG WTP-04 -- Habitable Islands (map stage)

Seat: Ensorain[ubu006-4b001784]. Date: 2026-10-06. Host: ubu006 (Linux, 4 cores, 15 GB).
Authority: operator direction 2026-09-30 (roles/Ensorain/prompts/2026-09-30_operator_direction/, verbatim):
NEXT = "map the WTP-03 habitable islands and their boundaries", with "cheap competitors first, always".
Promoted to CURRENT when the instrument line froze (ensorain/arc3/INSTRUMENT_LINE_FREEZE_2026-09-30.md).
Operator chat 2026-10-06: "All three. Go" (host move, Aporia heartbeat, start WTP-04).
Fleet context: M1 drain manifest, recommended first P2B campaign = "WTP-04 small and preregistered".
This document, the engine ensorain/wtp4/ and its tests are committed BEFORE any evaluation row.

## 0. Question

What physics must a world have before learning is physically useful in it at all? And where it is useful,
does a cheap mechanism suffice, or does a structured substrate pay?

This is the MAP stage only. Substrate collision inside the islands (the operator's THEN step) and
non-tensor-native grammars (RESERVE) are out of scope. They get their own preregistrations.

## 1. Engine (frozen WTP-03 executor, unchanged)

- ensorain/wtp4/ imports ensorain/wtp3 (world3.run_life, collider.carrier/make) and edits nothing in it.
- New code:
  - families.py (s2);
  - axes.py (s3);
  - habit.py (unit + classify, s4-s5);
  - campaign4.py (runner, s6);
  - score4.py (s5, s7).
- Python 3.14.4 / numpy 2.3.5 / scipy 1.16.3 (ensorain/requirements.txt).
- Rows are bitwise ubu006-bound. Nothing is compared bit-for-bit with WTP-03 M2 rows.

## 2. Founding families (rule fixed in families.py before any WTP-04 row)

- Source: the 181 admitted worlds of WTP-03 Wave A (ensorain/runs/wtp03/waveA.json), grouped by founder
  lineage (13 lineages).
- Independence rule: two lineages are the same family when their representatives share all three genes that
  decide what the stream can carry:
  - generator class;
  - dims style (binary / few_big <= 3 modes / many_small);
  - observation kind.
- Representative: the lineage member with the highest WTP-03 information demand (ties: genome hash).
- Result: 12 families F00-F11 (the 13 lineages minus one merge, F11).
  - 4 were "learning pays" at WTP-03 admission (F03, F07, F08, F09).
- Disclosed limitation: the rule is genome-level, not behavioural.
  - Two families can still share a mechanism.
  - The map reports per family, so a hidden duplicate double-counts in pooled rates only.

## 3. Axes (axes.py)

- Each axis moves ONE gene, or one coupled pair, of the representative outward.
- Every other gene stays at the representative's value, including the WTP-03 calibrated economy (kappa,
  metabolism).
- `native` (unchanged) is always run as the anchor.

    axis                 gene(s)                                  levels (benign -> harsh)
    memory_ratio         memory.band (cap = band x cells)          .5 .25 .1 .03 .01 .003
    change_timescale     transition.drift=.3, drift_period         static, p800 p200 p50 p12
    information_cost     p_read p_write p_probe p_rollout x        .1 1 10 100
    observation_noise    observation.noise_sd                      0 .1 .3 1 3
    irreversibility      irreversibility.door_close                0 .1 .3 .6
    credit_delay         credit.delay                              0 4 16 64
    topology (categ.)    geometry.kind + irreversibility.oneway=0  tensor_index ring small_world erdos tree scale_free
    compute_cost         p_compute x                               .1 1 10 100 1000
    forgetting           memory.forget_rate (none -> decay)        0 .02 .1 .3
    active_sensing (cat) search.policy                             random greedy novelty probe_greedy rollout
    recurrence_lifetime  time.lifetime x                           4 2 1 .5 .25

Notes on the axes:
- recurrence_lifetime is the learning-time / lifetime ratio that WTP-03 s4 named as the latent control of
  inhabitability.
- Recurrence is MEASURED per life (steps / distinct cells seen), not assumed.
- Mapping "compute budget" to the price of compute, and "recurrence" to lifetime, are seat choices. They are
  disclosed here; another reading is possible.

## 4. Unit (habit.unit)

One (perturbed genome, seed) runs immortal lives (metabolism 0, energy 1e9), the WTP-03 G3 measurement. Death
therefore never confounds earning. The lives:
- trivial twins: random policy without memory, and frozen memory;
- the oracle twin;
- CHEAP carriers: constant, table, additive;
- STRUCTURED carriers: lowrank, cp, tt, dct.

Each carrier is the world's own physics with organism 0's memory replaced (collider.carrier, fixed WTP-03
recipes). A carrier is run only if it fits the memory cap. Rate = U / steps. Cheap carriers are always run and
always reported.

## 5. Labels

Unit (habit.classify):
- tmax = best trivial rate; gap = oracle - tmax.
- TRAPPED if the oracle life itself ends DEGENERATE/topology (confined; exploration impossible).
- INFO_VALUELESS if gap <= .02 or gap <= .2|tmax| (the WTP-03 G3 "valuable" test).
- margin m = max(.01, .1 gap).
- DEAD if no carrier beats tmax by m.
- STRUCT_PAYS if the best structured carrier also beats the best cheap carrier by m.
- CHEAP_PAYS otherwise.
- H = (best - tmax) / gap (the fraction of the information gap that learning captures).

Cell (family x axis x level) over the seeds (score4.cell_label):
- PAYS only if every seed pays.
- STRUCT_PAYS only if every seed is STRUCT_PAYS.
- TRAPPED if every seed is TRAPPED; INFO_VALUELESS if every seed is.
- DEAD if every seed is DEAD, INFO_VALUELESS or TRAPPED (mixed).
- SPLIT if the seeds disagree.

Boundary: two adjacent levels of an ordered axis where PAYS flips. Neither side may be SPLIT or ILLEGAL.

## 6. Run

- Seeds:
  - dev: 9_900_001 (native check), 9_900_002 (axis check, F08/F09).
  - EVAL: 41_004_001 and 41_004_002, never used before this commit.
- Grid: 12 families x 54 points (native + 53 axis levels) x 2 seeds = 1,296 units.
- Envelope: <= 3 workers, nice 10, no new job below 3 GB available RAM.
- Runner:

      python -m ensorain.wtp4.campaign4 eval --seeds 41004001,41004002

- Scorer: `python -m ensorain.wtp4.score4 eval`.
- Rows go to ensorain/runs/wtp04/ (tracked).

## 7. Verdict (score4, mechanical)

    NO_HABITABLE_REGION  fewer than 2 families have any PAYS cell
    NOISE_LIMITED        >= 30% of non-native cells are SPLIT
    ISLANDS_MAPPED       >= half the families have at least one replicated PAYS<->DEAD boundary on an ordered axis
    PARTIAL_MAP          otherwise

Instrument check: axis liveness = the share of perturbed units in which some life's (event digest, U) differs
from native at the same seed. Levels whose genome equals the native genome are NO-OPs, excluded from the
denominator. An axis below 50% live is reported as INERT and is not interpreted.

Also reported:
- the per-axis pooled PAYS / STRUCT / DEAD / SPLIT table;
- every boundary with its bracket;
- the carrier-class changes along an axis among paying cells. This is a preview of the THEN step and is not
  a claim.

## 7a. Dev-stage instrument changes (seeds 9_900_002 F08/F09 all axes; 9_900_003 F03/F07/F08/F09 x 3 axes)

All were made before this commit and before any eval row:
- Liveness compared event digests only. Cost axes change U but not events, so they read as falsely "inert".
  Liveness now compares (digest, U) and excludes NO-OP levels. After the fix every axis is live on the dev
  rows; none is inert.
- Every non-lattice topology, and door_close > 0 in F08, ended DEGENERATE/topology in every life, and the
  scorer labelled these ILLEGAL. Two changes:
  - Confinement is a real way to die, so it gets its own label, TRAPPED.
  - The topology axis now zeroes one-way edges, which belong to irreversibility.
  - F08/F09 are still TRAPPED off-lattice. Their geometry.directed fraction is left at the family value:
    disclosed, not hacked.
- "constant" is called "none" in the in-life memory registry (a mapping fix).
- The dev rows stay in runs/wtp04/dev_axes*.jsonl, with their scores. They are never pooled with eval.

## 8. Predictions (made after the dev native check, before any eval row)

Written after the dev native check. The dev axis checks were run before this commit, so two families' full
maps (F08, F09) and four families' maps on 3 axes were SEEN. P2 and P6 were written before those rows; the
other predictions were not changed after them.
What the dev check had shown (seed 9_900_001, one seed, natives only):
- several families pay at native;
- some are dead;
- a cheap carrier wins in at least two.

The predictions:
- P1 recurrence_lifetime: the PAYS share is non-decreasing in lifetime (x.25 -> x4), pooled over families.
- P2 information_cost x100 kills paying in at least half of the families that pay at x1.
- P3 memory_ratio: no STRUCT_PAYS cell at band .003.
- P4 change_timescale p12: STRUCT_PAYS falls more than CHEAP_PAYS relative to static. Fast change favours
  recency/cheap carriers.
- P5 overall: structured carriers win fewer than 40% of the paying cells. Cheap competitors explain most of
  the habitability.
- P6 observation_noise sd 3: no PAYS cell in any family.
- P7 verdict: PARTIAL_MAP .40, ISLANDS_MAPPED .35, NOISE_LIMITED .20, NO_HABITABLE_REGION .05.

## 9. What would change the plan

- A structured carrier that pays where every cheap carrier is DEAD earns that region substrate-collision
  time (THEN). That collision must include N6, the tuned same-class batch fit (WTP-03 W4).
- If only cheap carriers ever pay, the next step is RESERVE (non-tensor-native grammars), not more tensor
  collision.

## 10. Limitations

- Two seeds per cell; SPLIT is reported, never rounded.
- Margins are the WTP-03 G3 margins, not re-tuned.
- The fixed WTP-03 economy means each axis is read "all else equal at the admitted calibration".
- Immortal twins measure earning, not survival.
- No N6 here: this stage asks whether learning pays, not whether it beats known batch physics.
