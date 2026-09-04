# PROPOSAL T6 (control)

Designer note: this specification measures CROSS-GAME STRATEGY TRANSFER on the LUDUS
games-as-worlds bench. It executes nothing; it preregisters everything. All quantities
below are exact (dynamic-programming value functions over compiled world state spaces,
zero model calls, zero Monte Carlo), so the noise axis is across WORLDS, not within them.
Circuit IDs, worlds, and machinery refer to `ludus/bench/` and `ludus/atlas/` as of
commit d332658cf (2026-09-01).

## Hypothesis

H1 (interface mediation): Cross-game transfer of a stopping-rule circuit is mediated by
the DECLARED INTERFACE PRECONDITION of the STOP axis — specifically, total-loss
forfeiture ("death loses the entire pot") — and not by genre surface. Operationally: the
frozen circuit r0003 (`STOP iff P(death|continue) * pot >= E[immediate gain|continue]`,
definition verbatim from `ludus/fossils/FOSSIL_r0003_2026-08-27.json`, byte-identical,
never retuned), invented on FLIP7 and MARTIAN_DICE, will

- retain >= 0.95 of optimal EV (minimum over the eligible-partner envelope, defined
  below) in every ELIGIBLE untouched world exposing a total-loss STOP interface,
  regardless of surface (themed push-your-luck or themeless FOUNDRY synthetic); and
- fail (retention < 0.75) in worlds where forfeiture is partial or absent
  (COLORETTO, LUCKY_NUMBERS, low-forfeiture FOUNDRY-PARTIAL), with retention
  MONOTONE INCREASING in the forfeiture fraction lambda.

H0 (genre mediation / no transfer): retention tracks genre surface or world identity
rather than the interface parameter; or the transferable circuit is dominated by a
one-parameter in-world fit (r0006-fitted), in which case "transfer" carries no advantage
over trivially refitting a threshold per world.

The second clause of H1 is the load-bearing one. The bench's standing weakness
(`ludus/atlas/BACKLOG.md`) is that every total-loss world to date is push-your-luck, so
interface and genre are confounded on the diagonal. This design fills the off-diagonal
cells: same-genre/different-interface (COLORETTO, LUCKY_NUMBERS) and
different-surface/same-interface (FOUNDRY grid), plus a parametric interface
dose-response (FOUNDRY-PARTIAL) that genre cannot produce.

## Design

### Circuits under test (all frozen before any recipient measurement; sha256 of
`ludus/bench/circuits.py` recorded at registration)

- r0003 — myopic one-step stop (PRIMARY transfer candidate; ABLATION_SUPPORTED)
- r0015 — two-ply myopic stop (secondary; carries a standing collision risk with r0003)
- r0007 — survival-rate stop (pot-blind CONTROL, never promoted)
- r0004 (never bank) and r0005 (bank immediately) — floor circuits
- SELECT arm (secondary): r0010, r0011, r0012, r0013 (null), r0014 on live-SELECT worlds

### World roster (fixed at registration; four tiers)

- DONOR (excluded from evidence, per `ludus/atlas/CIRCUIT_LEDGER.md` line 3: worlds used
  to invent a circuit are not evidence for it): FLIP7, MARTIAN_DICE.
- R1 — untouched, total-loss STOP, push-your-luck genre: INCAN_GOLD, CANT_STOP
  (both already prospective passes for r0003), plus PIRATEN_KAPERN, to be implemented
  from `ludus/atlas/BACKLOG.md` item 3 AFTER this registration and audited per
  `ludus/bench/RULES_AUDIT.md` before any claim about the named game is promoted.
- R2 — interface-violating negative controls, adjacent genre: COLORETTO (partial loss,
  already implemented in `ludus/bench/worlds2.py`), LUCKY_NUMBERS (no death anywhere).
- R3 — surface-stripped, same interface: the existing FOUNDRY grid
  [gate in {0,1}] x [k in {2,3}] x [cap in {2,4}], h=6, plus FOUNDRY-DECAY variants
  (`ludus/atlas/transfer_matrix.json`).
- R4 — NEW, the dose-response arm: FOUNDRY-PARTIAL[lambda], identical to FOUNDRY
  except death forfeits fraction lambda of the pot, lambda in
  {0.0, 0.25, 0.5, 0.75, 1.0}, with 5 structural seeds per lambda (25 worlds;
  satisfies the 5-seed replication doctrine). lambda = 1.0 reproduces the declared
  total-loss interface; lambda = 0.0 makes never-stopping optimal by construction.

### Evaluation distribution

Two distributions, both exact:

1. On-policy EV from the canonical initial state under the world's own transition
   dynamics (the `solve()` DP in `ludus/bench/compiled.py`). Retention
   rho(c, w, p) = EV(circuit c, SELECT partner p, world w) / EV*(w).
2. Per-decision regret under the COMMON REFERENCE occupancy of decision states
   (optimal-play occupancy, identical for every circuit in a world), exactly as
   implemented in `ludus/bench/occupancy.py`. Self-occupancy is circular and uniform
   weighting is degenerate (both documented failures in this repo); neither is used
   for inference.

### Transfer metric

- Partner eligibility (computed BEFORE any candidate circuit is scored, breaking the
  circularity that produced the r0003 fossil): a SELECT partner p is eligible in world
  w iff rho(optimal_stop, p, w) >= 0.75. Candidate envelope: {optimal_select,
  greedy_select, one_ply_select} restricted to eligible members.
- Transfer score T(c, w) = min over eligible partners of rho(c, w, p). The MINIMUM,
  not the best partner, is the reported number.
- World informativeness gate (computed from floors only, before candidates): world w is
  ELIGIBLE for STOP-transfer inference iff max(rho(r0004, w), rho(r0005, w)) <= 0.90.
  A world whose floors already sit at 0.95 cannot separate circuits and its pass would
  be vacuous (the gate-must-be-reachable doctrine). Ineligible worlds are recorded,
  not silently dropped.
- Per-world fitted bar: r0006-fitted (threshold T swept in-world, per
  `transfer_matrix.json`) is the price-of-one-refit comparator every transfer claim
  must be measured against.

### Procedure

1. Register this document; freeze circuit definitions and record sha256 hashes.
2. Build PIRATEN_KAPERN and FOUNDRY-PARTIAL[lambda, seed]; compile; run the
   compile-time exclusion gates (below); run floor circuits and partner-eligibility
   solves; publish the eligible-world list BEFORE any candidate circuit touches any
   recipient world.
3. Evaluate all circuits x all eligible worlds x full partner envelope in one pass.
4. Compute T(c, w), reference-weighted regret decomposition (circuit / world /
   circuit x world shares across eligible recipients), the lambda dose-response curve,
   and the SELECT ordering correlations.
5. Emit verdict strictly against the falsifiers below; ship raw per-cell JSON in the
   SAME commit as the verdict (verdict-without-rows doctrine).

## Controls

- Donor exclusion: FLIP7 and MARTIAN_DICE appear in no evidentiary cell. This breaks
  the selection relation between where the circuit was invented and where it is scored.
- Pot-blind control (r0007): reads risk, ignores stake. If r0003 does not beat r0007 on
  total-loss recipients, the "strategy" content of the transfer is the trivial part.
- Floor circuits (r0004, r0005): bound what zero strategy earns; also drive the world
  informativeness gate.
- Null SELECT circuit (r0013): reads nothing; any SELECT circuit it outranks is dead.
- Per-world fitted comparator (r0006-fitted): distinguishes "the circuit transferred"
  from "any one-parameter refit would have done as well".
- Partner envelope with pre-committed eligibility: the r0003 fossil showed a 0.0000
  reading manufactured entirely by a pathological optimal-select partner in gated k=3
  FOUNDRY worlds. Reporting min-over-eligible-partners, with eligibility fixed before
  scoring, prevents both the false kill and the flattering best-partner cherry-pick.
- Exposure/competence separation: world-level EV is exposure x competence
  (cycle 005 demotion). All mediation inferences additionally use the common reference
  occupancy so a claim of world-dependent competence cannot be support mismatch.
- Surface-stripped worlds (FOUNDRY): genre removed, interface kept — the positive
  control for "interface, not theme".
- Interface dose-response (FOUNDRY-PARTIAL): lambda is a within-family manipulation of
  ONLY the interface parameter; genre, state topology, and reward scale held fixed
  across lambda within each seed. This is the axis-perturbing null the mediation claim
  actually varies on.
- Frozen artifacts: circuits byte-frozen; any modification mid-experiment creates a new
  circuit ID and is out of scope for this cycle.
- Rules audit: PIRATEN_KAPERN remains HYPOTHESIZED until audited; results on it are
  reported about the reconstruction, not the commercial game.

## Preregistered falsifiers (each with an explicit numeric threshold)

- F1 (transfer failure): T(r0003, w) < 0.95 in ANY eligible untouched total-loss world
  (R1 or R3 gate-passing worlds, or R4 lambda = 1.0 seeds). Fires -> the registered
  interface-transfer claim (ledger kill condition "materially below 0.97",
  operationalized here at 0.95) is dead in its registered scope.
- F2 (transfer without advantage): T(r0003, w) < rho(r0006-fitted, w) - 0.03 in >= 2
  eligible total-loss recipients. Fires -> transfer is dominated by per-world refitting;
  the cross-game claim is demoted to "cheap to refit", not "transferable".
- F3 (specificity failure): T(r0003, w) >= 0.90 on COLORETTO or on LUCKY_NUMBERS, or
  mean T(r0003) >= 0.90 over the 5 seeds at any lambda <= 0.25. Fires -> the total-loss
  precondition is not load-bearing and interface mediation is falsified from the
  permissive side (the circuit "transfers" where its own scope says it must not).
- F4 (dose-response failure): Spearman rho between lambda and per-lambda mean T(r0003)
  across the 5 lambda levels (each level the mean of its 5 seeds) < +0.5. Registered
  point prediction is rho >= +0.8 and strictly monotone level means. Fires -> the
  interface parameter does not govern transfer magnitude.
- F5 (exposure confound): circuit x world share of reference-weighted regret variance
  across eligible recipient worlds > 0.30 (cycle 005 measured 0.1021 on the real
  worlds; 0.30 is triple that benchmark). Fires -> circuits are not stable primitives
  and no world-level transfer number may be read as circuit competence.
- F6 (partner non-robustness): partner spread over ELIGIBLE partners > 0.10 for r0003
  in any eligible recipient. Fires -> that cell's value is not a function of
  (circuit, world); the cell is VOID (neither pass nor kill), the world is flagged,
  and no promotion may cite it. Three or more void cells -> the whole cycle returns
  MEASUREMENT_INVALID rather than a verdict.
- F7 (SELECT ordering, secondary): Spearman rho of the SELECT-circuit ordering
  (r0010, r0011, r0012, r0013, r0014 by T) between MARTIAN_DICE and any live-SELECT
  eligible recipient < +0.60, or r0013 (null) outranks any circuit currently marked
  transferable. Fires -> SELECT-axis transfer is genre-mediated or illusory.
- F8 (collision): |T(r0003, w) - T(r0015, w)| < 0.01 in EVERY eligible world of the
  roster. Fires -> the roster cannot separate the pair; one of the two names is
  redundant and one must be retired or a separating world must be hunted before either
  is cited again.

## Stopping rule

- The roster is closed at registration. No world is added, removed, or re-parameterized
  after the first candidate-circuit evaluation on any recipient world.
- Compile-time exclusion (before any candidate evaluation, recorded with reasons):
  a world is excluded iff n_states > 1,000,000 or exact compile-and-solve wall time
  > 4 hours. Floor/eligibility solves are not candidate evaluations.
- All quantities are exact; there is no sampling to extend, no seed to add, and
  therefore no data-dependent optional stopping anywhere. The experiment stops when
  every (circuit x eligible world x eligible partner) cell in the closed roster is
  computed once, or when a MEASUREMENT_INVALID condition (F6, >= 3 void cells) fires,
  whichever is first.
- One pass. If a falsifier fires, the verdict is written from this pass; repairs,
  circuit revisions, and interface splits (e.g. STOP-with-ruin vs STOP-with-decay)
  are NEW registrations in a subsequent cycle, never edits to this one.

## Unit of inference

The (circuit, world) cell is the observation; WORLDS are the replicates. Decision
states within a world are numerous (6,176 in MARTIAN_DICE; 68,873 in CANT_STOP) but are
NOT independent draws and confer no degrees of freedom — the SE-on-the-wrong-unit
failure is explicitly excluded. Within a cell the EV is exact (zero variance), so no
within-cell CI is reported; cross-world claims are counts over eligible worlds. Primary
confirmation count: r0003 satisfies (not-F1 and not-F2 and beats r0007 by >= 0.05
retention) in K of K eligible total-loss recipients, K >= 8 expected
(INCAN_GOLD, CANT_STOP, PIRATEN_KAPERN, eligible gate-passing FOUNDRY worlds, and the
five lambda = 1.0 seeds); the directional sign test against the pot-blind control at
K = 8 has two-sided binomial p = 2^-7 ~= 0.008 under the null of no stake-sensitivity
advantage. The lambda dose-response uses the 5 lambda-level means (n = 5 levels,
seeds nested within level, never pooled as 25 independent observations).

## Prior work bearing on this design (cite repo paths if any; 'none found' is acceptable)

- `ludus/atlas/transfer_matrix.json` — the existing 4-real + FOUNDRY transfer matrix;
  source of all retention baselines quoted here (r0003: 0.9998 / 1.0 / 0.9872 / 1.0 on
  the four real worlds; r0006-fitted per-world bars).
- `ludus/atlas/CIRCUIT_LEDGER.md` — circuit provenance, registered predictions and kill
  conditions; the "invention worlds are not evidence" rule; r0003's registered scope
  explicitly names partial-loss worlds as untested (its Coloretto backlog note).
- `ludus/atlas/CIRCUIT_MATURITY.md` — r0003 blocked at PARTNER_ROBUST by a 1.0000
  partner spread in FOUNDRY[gate=1,k=3,cap=4]; F6 and the eligibility-gated partner
  envelope answer exactly this block.
- `ludus/fossils/FOSSIL_r0003_2026-08-27.json` — the false-kill fossil: 0.0000 readings
  on LUCKY_NUMBERS/COLORETTO/gated FOUNDRY produced by the partner, not the world;
  motivates min-over-eligible-partners and the pre-committed eligibility gate.
- `roles/Ludus/CYCLE_002_stochastic_stopping.md` §8.1 — the original preregistration of
  r0003's >= 0.97 prospective prediction, made before INCAN_GOLD and CANT_STOP existed.
- `roles/Ludus/CYCLE_004_PREREG_basis_audit.md`, `CYCLE_004_VERDICT_basis_audit.md`,
  `roles/Ludus/CYCLE_005_verdict_demotion.md`, `ludus/atlas/cycle005_occupancy.json`,
  `ludus/bench/occupancy.py` — the exposure-vs-competence demotion; source of the
  common reference occupancy and the 0.1021 circuit x world benchmark behind F5.
- `ludus/atlas/BACKLOG.md` — the monoculture diagnosis, the FOR_SALE / COLORETTO /
  PIRATEN_KAPERN ordering by information gain, and the standing rules-audit constraint.
- `ludus/bench/worlds2.py` — LUCKY_NUMBERS (live SELECT, no death) and COLORETTO
  (partial loss) implementations used as the R2 negative controls.
- `ludus/bench/run.py`, `ludus/bench/compiled.py`, `ludus/bench/circuits.py` — the
  pairing-envelope evaluation machinery and frozen circuit implementations (hashes in
  the r0003 fossil).
- `roles/Ludus/CHARTER.md` §40-§42 — keep breaking the representation that appears
  sufficient; fossil discipline for failed circuits.
