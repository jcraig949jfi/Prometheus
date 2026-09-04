# PROPOSAL T6 (wiki)

Designer: V1B-T6-wiki (M1) | Date: 2026-09-02
Target seat: Ludus (games-as-worlds bench, `ludus/`)
Reference artifacts: `ludus/atlas/CIRCUIT_LEDGER.md`, `ludus/atlas/circuit_maturity.json`,
`ludus/atlas/transfer_matrix.json`, `ludus/atlas/cycle005_occupancy.json`,
`ludus/fossils/FOSSIL_r0003_2026-08-27.json`.

## Hypothesis

**H-T6: Cross-game strategy transfer in Ludus is acquisition-cost reduction, and it is
interface-mediated.** Concretely: a circuit library acquired on source push-your-luck worlds
(the registered STOP circuits: r0003, r0007, r0015, plus floors r0004/r0005) lowers the COST —
number of exact candidate-circuit evaluations — of reaching a fixed competence threshold in an
UNTOUCHED target world exposing a total-loss STOP interface, by a factor of at least 1.5x over
an identical from-scratch searcher, and this reduction (a) exceeds what an equally sized random
library from the same DSL buys, and (b) is absent in target worlds with no STOP axis.

Rationale: every existing Ludus transfer number is a *policy retention score* — the claim
ceiling on C-a9fc01aa3892 states verbatim: "all numbers are policy scores, not
learning-cost measurements." The bench's own maturity ladder (`circuit_maturity.json`)
defines its top rung, TRANSFER_SUPPORTED, as "prior acquisition measurably lowers the COST
of reaching a competence threshold in a new world" — and no circuit has any evidence at that
rung. This experiment measures exactly the missing quantity.

## Design

**Learner (frozen before any run).** A single deterministic circuit-search procedure S over
the bench's existing circuit grammar (the DSL implicitly defined by `ludus/bench/circuits.py`
primitives: state readers pot, p_dead, e_gain, capacity, depth; comparators; scalar
constants from a frozen grid). S proposes candidate STOP circuits in a priority order and
evaluates each candidate EXACTLY (compiled world, no sampling, as in `ludus/bench/compiled.py`).
Cost C = index of the first evaluated candidate that meets the competence threshold (below).
S is identical across arms; ONLY its initialization differs.

**Arms (4).**
- A-TRANSFER: S initialized with the acquired library — the registered STOP circuits ordered
  by their source-world (FLIP7, MARTIAN_DICE) mean retention — evaluated first, then the
  library's sub-expressions seed the proposal ordering (library terms get priority weight).
- B-SCRATCH: S with no library; proposal order is the DSL's canonical enumeration order,
  tie-broken by seeded RNG.
- C-RANDOM-LIB: S initialized with a size-matched, depth-distribution-matched library drawn
  uniformly at random from the same DSL (new draw per seed). This breaks the selection
  relation (acquisition-on-source-worlds) while preserving library size and shape.
- D-SHUFFLED-LIB: the acquired library with its priority ordering permuted (per seed).
  Separates "having the right terms" from "knowing which to try first."

**Competence threshold (frozen).** A candidate circuit meets threshold in world W iff its
retention (EV from the start distribution / optimal EV) is >= 0.95 under EVERY partner in the
frozen SELECT-partner envelope {optimal_select, greedy_select, one_ply_select} (min over
envelope, per the r0003 fossil lesson that a circuit's value is not a function of
(circuit, world) alone). Reference-weighted regret per cycle 005 is also recorded at the
threshold event but does not gate.

**Target worlds (all UNTOUCHED for every library circuit; predictions registered before any
new world is implemented).** Three preregistered lanes:
- Lane 1 (total-loss STOP, in-scope): INCAN_GOLD + 2 new worlds where death forfeits the
  entire pot (backlog order frozen in advance).
- Lane 2 (partial-loss STOP, scope-attacking): 2 new worlds where loss is partial
  (Coloretto-class, per `CIRCUIT_LEDGER.md` r0003 "current scope" caveat and BACKLOG item 2).
- Lane 3 (no STOP axis, placebo): 2 worlds with only a live SELECT axis (CANT_STOP-class),
  searched for a SELECT circuit with the STOP library as the "prior." Any cost reduction here
  is a menu artifact, not interface-mediated transfer.

**World admissibility gates (computed BEFORE enrollment; a failed world is replaced from the
frozen backlog order, never chosen post hoc).**
- G1 headroom: neither floor circuit (r0004, r0005) nor the first 5 canonical-enumeration
  candidates reach threshold; and one-ply greedy play retains < 0.95 of optimal (per
  C-ba882ad5cc7e: a world can instantiate a genre and contain no strategic decision).
- G2 reachability: exhaustive or budget-capped sweep certifies that AT LEAST one circuit in
  the DSL reaches threshold within the max budget (a gate that cannot fire is not a gate).
  Worlds failing G2 are logged as INELIGIBLE, not as transfer failures.

**Runs.** For each (arm, world): 5 seeds (seeded RNG controls tie-breaking and, in C/D,
library draw/permutation). Budget cap: 10,000 exact evaluations per run; a run hitting cap
scores C = 10,000 (censored, flagged). Per-world statistic: median C over seeds. Primary
effect per world: ratio T_W = median C_B-SCRATCH / median C_A-TRANSFER. Specificity effect:
R_W = median C_C-RANDOM-LIB / median C_A-TRANSFER. Ordering effect:
O_W = median C_D-SHUFFLED-LIB / median C_A-TRANSFER.

**Uncertainty.** Bootstrap over seeds within world (10,000 resamples) gives a CI on each
ratio; the world-level verdict is read only if the CI excludes the falsifier threshold —
if the CI straddles it, that world reads UNRESOLVED, never PASS or FAIL (gate must exceed
measurement error).

## Controls

1. **C-RANDOM-LIB** — breaks the acquisition/selection relation while matching library size
   and expression-depth distribution. Required because a control drawn from the treatment's
   selection relation IS the treatment; any speedup shared with random libraries is menu
   shape, not transfer.
2. **D-SHUFFLED-LIB** — isolates ordering information (knowing WHICH acquired circuit to try
   first) from term possession.
3. **Lane 3 placebo worlds (no STOP axis)** — interface-mediation control; the STOP library
   should be inert there.
4. **Partner envelope {optimal, greedy, one_ply} on the SELECT axis** — every threshold event
   must hold under min-over-envelope; per-partner retentions and partner_spread are recorded.
   (The r0003 fossil shows a single-partner protocol can read 0.0000 and 1.0000 in the same
   world.)
5. **Common-reference weighting recorded beside the gate** — reference-weighted regret at
   threshold per cycle 005's protocol, so exposure/occupancy conflation (the cycle 004
   demotion) is auditable even though the gate itself is EV retention from start states.
6. **Untouched-world discipline** — no target world may appear in any circuit's invented-on
   or tuned-on list (`CIRCUIT_LEDGER.md` header rule); all lane membership, backlog
   replacement order, and thresholds are committed (verbatim + sha256) before any new world
   is implemented.
7. **Censoring symmetry check** — capped runs are counted per arm; if capping is asymmetric
   (>=2 capped runs difference in any world), the ratio for that world is reported with the
   cap-direction disclosed (which DIRECTION the confound pushes relative to the gate).

## Preregistered falsifiers (each with an explicit numeric threshold)

- **F1 (no cost transfer).** If the median over Lane 1 worlds of T_W < 1.5 (bootstrap CI
  excluding 1.5 required to read either way), H-T6's main clause is FALSIFIED for the STOP
  library; no circuit is promoted toward TRANSFER_SUPPORTED.
- **F2 (menu artifact).** If median over Lane 1 of R_W < 1.25, the speedup is not
  acquisition-specific: any T_W passes are attributed to DSL menu shape and H-T6 is
  FALSIFIED even if F1 passed.
- **F3 (interface mediation fails).** If the median T_W in Lane 3 (placebo, no STOP axis)
  >= the median T_W in Lane 1, the "interface-mediated" clause is FALSIFIED — transfer, if
  any, is not carried by the STOP interface.
- **F4 (partner artifact).** If in >= 2 worlds the threshold event under min-over-envelope
  and under optimal_select alone disagree AND the resulting world verdict flips, those
  worlds' readings are VOID (not negative), and the experiment reports an instrument fault
  per the r0003 fossil precedent. Numeric trigger: |retention_min_envelope −
  retention_optimal| > 0.05 at the first-threshold candidate.
- **F5 (scope boundary).** In Lane 2 (partial-loss), if median T_W >= 1.5, r0003's
  registered total-loss scope precondition is too narrow (scope-extending evidence); if
  median T_W < 1.25, the total-loss precondition is load-bearing. Between 1.25 and 1.5:
  UNRESOLVED. This lane cannot falsify H-T6; it bounds its scope.
- **F6 (ceiling sanity).** If in any admissible world B-SCRATCH reaches threshold in <= 10
  evaluations (median), that world had no headroom despite G1 and is retro-flagged
  INELIGIBLE; if that leaves fewer than 2 admissible Lane 1 worlds, the experiment reads
  UNDERPOWERED, not passed.

## Stopping rule

Fixed-design, no optional stopping. The experiment ends when all preregistered cells
(4 arms x 7 worlds x 5 seeds = 140 runs, each capped at 10,000 exact evaluations) have been
run exactly once, or when a hard compute wall (any single world's compile-and-solve exceeding
30 minutes on M1) forces that world's replacement from the frozen backlog order — replacement
is allowed at most twice per lane, and only for worlds whose admissibility gates or compile
wall fired, NEVER for worlds whose results were seen. No new arms, worlds, seeds, thresholds,
or weightings may be added after the first result row exists. Verdicts are read once, from a
pre-committed analysis script hashed before any run.

## Unit of inference

The TARGET WORLD (n = 3 Lane-1 worlds for the primary claim; Lanes 2-3 are scope/placebo
lanes). Seeds are within-world replicates summarized to a per-world median before any
cross-world statistic; decision-state counts and evaluation counts are NEVER the n
(per the SE-on-the-wrong-unit rule). With n = 3 worlds the primary readout is estimation
against preregistered thresholds with per-world CIs — explicitly NOT a population-level
significance claim about "all games"; the claim ceiling to be registered with any resulting
claim: "3 solitaire worlds, one DSL, one search procedure; cost is DSL-relative."

## Prior work bearing on this design

- `ludus/atlas/circuit_maturity.json` — TRANSFER_SUPPORTED rung definition (cost-to-threshold);
  r0003 blocked at PARTNER_ROBUST with partner spread 1.0000 in FOUNDRY[gate=1,k=3,cap=4].
- `ludus/fossils/FOSSIL_r0003_2026-08-27.json` — the 0.0000 readings were partner artifacts;
  verdict UNRESOLVED; "r0003's measured value is NOT a function of (circuit, world) alone."
- `ludus/atlas/CIRCUIT_LEDGER.md` — untouched-world doctrine ("Worlds used to invent or tune
  a circuit are not evidence for it"); r0003 scope caveat (total-loss only; Coloretto chosen
  to attack it); r0012 kill condition (SELECT ordering reversal = genre-mediated).
- `ludus/atlas/cycle005_occupancy.json` — occupancy-controlled competence protocol
  (unweighted / occupancy-weighted / reference-weighted regret triple).
- Evidence Wiki C-a9fc01aa3892, C-b3b4b28a3a62, C-ba882ad5cc7e, C-6f69aafca4e1,
  C-f8fd488fda5b, R-e68c9331eca2 — detailed in the next two sections.
- Memory doctrine applied: control must break the selection relation; gate must be shown
  reachable; gate must exceed measurement error; SE on the correct unit; truncation
  direction disclosed; 5+ seeds; significant prompts committed verbatim + hashed.

## Evidence Wiki consultation log (queries run + object ids retrieved)

Client: `ew.client.EvidenceWiki(machine='M1', agent='V1B-T6-wiki')`, canonical_revision 521.

1. `search_evidence("cross-game strategy transfer circuit")` → C-ba882ad5cc7e (OBSERVED),
   C-b3b4b28a3a62 (RETRACTED), C-01f913ae81af (REFUTED), C-b287aa6823b0 (SUPPORTED),
   C-6f69aafca4e1 (SUPPORTED), C-f8fd488fda5b (SUPPORTED).
2. `search_evidence("stopping rule push-your-luck occupancy")` → C-a9fc01aa3892 (SUPPORTED),
   C-ec2958821325, C-6f69aafca4e1, C-55004a4674b8, C-5168060736c5 (NOT_ESTABLISHED),
   C-0a16e694799e (REFUTED), C-5a1e687671e3.
3. `get_claim("C-a9fc01aa3892")` → claim + evidence E-9bded1559a1c (TRANSFER_TEST,
   CONFIRMED; metrics: r0003 retains 0.9991 Flip 7, 0.9095 Martian Dice untuned; residual
   decomposition: stop-rule upgrade −0.0005 vs claim-rule upgrade +0.0777 = 86% of residual;
   paired retention 0.9872), experiment X-b537db75c8de, packet SP-031fe12770ae.
   Claim ceiling read verbatim: "Worlds are solitaire, small, and reconstructed from memory
   (HYPOTHESIZED rules); all numbers are policy scores, not learning-cost measurements."
4. `get_counterevidence("C-a9fc01aa3892")` → counter_relations: [], negative_evidence: []
   (no standing counterevidence).
5. `related_findings("C-a9fc01aa3892")` → semantic: C-ba882ad5cc7e (0.509), C-01f913ae81af,
   C-b287aa6823b0, C-5a1e687671e3, C-6f69aafca4e1, C-b3b4b28a3a62, C-aba202675bd8,
   C-3d12c440f087, C-053572137688, C-7dceb2ca2886; graph edges: none.
6. Negative-evidence/demotion query:
   `search_evidence("retracted demoted circuit partner artifact contextual competence ludus")`
   → C-b3b4b28a3a62 (RETRACTED), C-aba202675bd8 (NOT_ESTABLISHED), C-b037a49b641c
   (RETRACTED), C-e3c149ca4f7e (REFUTED), C-e5e726a050c1 (RETRACTED), C-353ec1eb022a
   (RETRACTED); followed by `get_claim("C-b3b4b28a3a62")` → evidence E-e2f0736dfff5
   (REFUTED; reference-occupancy decomposition: circuit 0.8528 / world 0.0451 /
   circuit x world 0.1021 vs cycle 004 on-policy 0.2126 / 0.0696 / 0.4374; three weightings
   disagree violently; cross-world rank mean tau +0.1079 with 3 of 6 pairs negative),
   packet SP-d50f087628e4.
7. `contradictions()` → R-e68c9331eca2: C-3a1c49fa5a78 CONTRADICTS C-3d12c440f087
   ("accumulated executable history improves future search": D-5 SUPPORTED +10.95pp vs D-8
   S0 NO_EFFECT; classification APPARENT_UNDER_DIFFERING_CONDITIONS, differing on substrate).
8. `find_gaps()` → H-c86a0f5fdb25, H-b05639aa9fb2, H-f59eb0aaaedf, H-afa5c888484a,
   H-0e8a458b6628, H-49d0a76a8b32 (transfer_mediation x lmfdb_arithmetic MISSING_CELL),
   H-2412024b5c96.

## Evidence that changed this design (specific ids + the concrete design decision each changed)

- **C-a9fc01aa3892 (claim ceiling, via get_claim)** — the ceiling "all numbers are policy
  scores, not learning-cost measurements" fixed the DEPENDENT VARIABLE: this experiment
  measures cost-to-threshold (evaluations), not retention. Retention transfer is already
  SUPPORTED with no counterevidence (step 4), so re-measuring it would add nothing; the
  unmeasured rung (TRANSFER_SUPPORTED) is the target.
- **E-9bded1559a1c (86% of Martian Dice residual sits OFF the stop axis)** — motivated the
  partner-envelope gating and the F4 void condition: the transferred computation is the easy
  part, so a threshold event must be shown not to be a partner artifact before it counts.
- **C-b3b4b28a3a62 + E-e2f0736dfff5 (RETRACTED cycle 004 verdict; support mismatch =
  exposure, not competence; the three weightings disagree violently)** — changed the
  competence measurement: reference-weighted regret is recorded beside every threshold event
  (Control 5), and the gate itself was moved to start-state EV retention (weighting-free)
  precisely because on-policy occupancy weighting was the retracted instrument.
- **C-ba882ad5cc7e (worlds can instantiate a genre and contain no strategic decision;
  one-ply greedy optimal in 85-100% of states)** — created admissibility gate G1
  (headroom: greedy/floors/first-5-enumeration must NOT reach threshold) and falsifier F6;
  without it, Lane 1 could "pass" on worlds where transfer is trivially cheap for everyone.
- **C-6f69aafca4e1 (SELECT circuit ordering completely reversed between two worlds sharing
  an interface)** — changed the hypothesis from "transfer exists" to "transfer is
  interface-mediated" with an explicit placebo lane (Lane 3) and falsifier F3, and put the
  D-SHUFFLED-LIB arm in: if ordering knowledge doesn't survive across worlds, possession and
  priority must be separable in the design.
- **C-f8fd488fda5b (incubation v2: experienced learner re-acquired a program at >=600x lower
  acquisition cost)** — precedent that cost-to-threshold ratios are measurable and can be
  large; this set the effect metric as a RATIO with a deliberately modest floor (1.5x) rather
  than a difference, and informed the 10,000-evaluation budget cap.
- **R-e68c9331eca2 (contradiction: accumulated-history-helps SUPPORTED on one substrate,
  NO_EFFECT on another, classified APPARENT_UNDER_DIFFERING_CONDITIONS on the substrate
  dimension)** — warned that "prior acquisition helps" is substrate-dependent, which is why
  the C-RANDOM-LIB control (breaking the acquisition relation within THIS substrate) is
  mandatory (F2) rather than optional, and why the claim ceiling registered with any result
  is DSL- and procedure-relative.
- **get_counterevidence("C-a9fc01aa3892") returning empty** — confirmed no standing negative
  evidence against retention-level transfer, which licensed building ON TOP of it (using the
  registered STOP circuits as the acquired library) rather than re-litigating it.
- **find_gaps() H-49d0a76a8b32 (transfer_mediation x lmfdb_arithmetic missing cell)** — did
  NOT change this design (wrong substrate class); recorded here to keep the no-citation-
  without-consequence rule honest.
