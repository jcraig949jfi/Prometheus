# PREREG -- Tyche v0: first dark-ecology lens-evolution campaign

Currency: 2026-09-30. Committed BEFORE the campaign run. Governs the run
produced by `python -m tyche.run_v0 --out tyche/runs/v0_2026-09-30`
at the commit that adds this file. Charter:
roles/Tyche/prompts/2026-09-30_charter/ (01c53f64e).

## 0. What v0 is for

The charter's first goal is not discovery. It is to show that

    lens mutation -> measurable differential capability -> reproduction
    -> residual shift -> new lens generation

works end to end WITHOUT leakage or semantic judgment, with planted
positive controls and structure-destroyed / keyed-PRF negative controls.
v0 makes machinery claims (H1-H6). Anything it finds on the Hecate alien
and adversarial worlds is DESCRIPTIVE and reported, not claimed.

## 1. Roles (separation is structural, by module)

WORLD tyche/worlds.py (X to lenses; Y never passed to a lens).
LENS tyche/lens.py (causal register programs; 27 ops; LEAD op exists
only for the cheat control and is not in the chemistry). ORGANISM and
RULER tyche/organisms.py. ECOLOGY/selection tyche/ecology.py. AUDITS
tyche/audits.py. Driver tyche/run_v0.py. Report/verdicts tyche/report.py.
No LLM or interpreter anywhere in the selection, admission or verdict
path. The model (this seat) wrote the code; it adjudicates nothing.

## 2. Worlds (32; 24 selection, 8 held out = 25%)

worlds_hash ca12482c826686f052ed8db8c3a9e4b392eddb2b8acde4363ee8843f78aff5bd
(tyche.worlds.build_worlds(20260930); law parameters in WORLDS.json).
T = 12100 per world; splits train [100,3100) val [3100,6100)
conf [6100,9100) test [9100,12100). Selection input seed 1;
replication seeds 101, 102 (Pass D only).

  selection (24): planted P1..P6 (xor of two delayed channels; running
    count mod 3; delayed-window majority; delayed gate; sign of delayed
    gaussian product; hidden 3-state automaton) | TARGET_STRUCTURE_DESTROYED
    twins TSD1..TSD4 | PRF1, PRF2 (keyed SHA-256 of a 24-step window) |
    known K1..K3 | Hecate ALIEN_LAWFUL HA_tab/graph/rewrite/vm (one
    component hidden, target = observed component with highest next-value
    entropy on seed 0) | Hecate MATCHED_NOISE HN_tab/graph (dark worlds,
    NOT negative controls) | adversarial decoy / noisy-majority / aliased
    period-11 phase
  held out (8): P1 sibling (Markov inputs), P3 sibling (p=0.45), P7
    3-way delayed parity (law not in selection), its TSD twin, PRF3, K4
    xor, Hecate HA_map, sparse delayed gaussian dependency

Consequence rulers (never collapsed): R0 predict Y[t] from Z[t];
R2 predict Y[t+2] from Z[t]. Organisms (weak by design): lin (ridge
one-vs-rest), tree (depth 4, leaf >= 20), tab (median-binarised lookup
table with a 10-feature attention budget: candidate lens first, then
admitted lenses newest first, then raw channels).

## 3. Procedure

Pass A: ecology E0 = raw observation. Baselines per world x ruler x
  organism on val and test. 96 random initial lenses (1-4 instructions);
  the best-by-val initial lens per selection world is also scored once on
  test. Frozen in PASS_A_BASELINE.json.
Pass B: residual scopes frozen at each epoch start: all / err (every
  organism wrong under the current ecology) / dis (organisms disagree).
Pass C: 4 epochs x 10 generations, N = 96. Case vector per lens = val
  marginal gain for (24 worlds x 2 rulers x 3 organisms x 3 scopes) =
  432 cases. Epsilon-lexicase parent selection (MAD epsilon). Elites: best
  lens per (world, ruler) if gain > 0.01, cap 24. Dark-ecology reserve
  15% (14 slots): age-protected members (< 3 gens), then 2/3 by behaviour-
  signature novelty, 1/3 random. Offspring: 25% cross-lineage graft,
  else 1-2 of {point, replace, insert, delete, rewire, out, temporal,
  recur, dup}. Every birth logged with parents and operators; every
  death logged as a fossil with its best case.
  Admission at each epoch end, on the CONF split only: per selection
  world, the top 5 candidates with val gain >= 0.02 are tested on their
  best case against the current ecology; admit if paired z >= 4.0 and
  gain >= 0.01; at most 1 admission per world per epoch, 48 in total.
  An admitted lens joins the global ecology E (its outputs become
  features for every organism on every world); residuals are recomputed.
Pass D (per admitted lens, against the ecology as it was at admission):
  test-split gain and z; replication on seeds 101 and 102; matched random
  null (64 random lenses, same instruction count and output width) on
  the home case; causality audit (future replaced at 5 cuts, output up to
  each cut must be bit-identical); input-channel ablation (circular shift
  997 in the lens input only); transfer to all 31 other worlds, every
  case; a transfer counts only with test z >= 4, replication z >= 3 on
  seed 101, and gain above the p95 of 32 matched random lenses on that
  world and case. Cheat control: a world whose consequence is the next
  observation, read by a LEAD lens; the gain channel must see it
  (z >= 4) and the causality audit must reject it.

Definitions: replicated = home test z >= 4 and both replication seeds
z >= 3. beats_null = home test gain > null p95. Sensor class from the
worlds that pass: LOCAL / FAMILY / TRANSFER / GENERAL; a pass on a tsd or
prf world is a FALSE_GRADIENT, never transfer. interpretation =
PLANTED_INPUTS_RECOVERED only when the channels whose ablation removes
>= 50% of the gain equal the planted law's channels (a deterministic
check against the answer key); otherwise UNKNOWN. No lens is simplified.

## 4. Hypotheses, gates and my predictions (computed by tyche/report.py)

H5 INSTRUMENT (gate on everything): cheat control instrument_ok AND every
  admitted lens passes the causality audit. FAIL voids the campaign.
  Prediction: PASS.
H1 PLANTED POSITIVE CONTROL: a planted selection world is VOID as a
  control if the best initial lens's test gain >= 0.03. It is SOLVED if
  an admitted lens with that home has test gain >= 0.10, replicated,
  beats_null, causal, and z < 3 on the world's TSD twin (where one
  exists). PASS if >= 4 valid worlds and >= 4 SOLVED; FAIL if <= 1
  SOLVED; else INDETERMINATE.
  Prediction: PASS; P1, P3, P4, P5 solved; P2 likely; P6 (automaton
  table) I expect NOT solved within 40 generations.
H2 FALSE GRADIENTS: count negative worlds (tsd, prf; selection and
  held out) on which any admitted lens shows a replicated, null-beating
  test gain. PASS if 0; INDETERMINATE if 1; FAIL if >= 2. Admissions on
  negative worlds at the conf gate are reported separately.
  Prediction: PASS, and 0 admissions on negative worlds.
H3 RESIDUAL SHIFT: on each SOLVED planted world the err-residual
  fraction (the solving lens's ruler, val) drops by >= 50% relative from
  the first epoch start to the end; on >= 80% of selection negative
  worlds it moves by <= 0.03 absolute. PASS if both; INDETERMINATE if
  nothing was solved; else FAIL. Prediction: PASS.
H4 REDUNDANCY: no admission on a known world for an (R0, organism) pair
  whose raw baseline val accuracy is already >= 0.95. Prediction: PASS
  (the weak organisms on K2/K3 may still earn admissions where the raw
  baseline is NOT saturated; those are recorded, not violations).
H6 END TO END: PASS iff H1, H2 and H5 PASS and at least one lens
  admitted in epoch >= 1 is replicated, beats_null and causal on a home
  world whose err-residual had already dropped by >= 0.01 at that epoch's
  start. FAIL if H5, H1 or H2 FAIL; else INDETERMINATE.
  Prediction: PASS.

Descriptive only (no gate): Hecate alien/null and adversarial worlds;
held-out transfer; sensor classes; lens x organism table; dark-reserve
ancestry of admitted lenses (revived lineages); opaque vs planted-input
recovered; near-chance worlds; weak gradients. My expectations, to be
scored honestly: ADV_decoy solved (it is a delayed xor under a decoy);
ADV_alias NOT solved; some admissions on Hecate worlds that are largely
organism-capacity patches (random nonlinear features beat the raw
baseline for weak organisms); HN worlds show admissions only if they
beat their matched null, which I expect rarely.

## 5. Disclosures (what I saw before freezing)

- Attainability checks (instrument calibration, before any evolution):
  hand-written planted compositions on P1..P6 and P7 give R0 val gains
  0.40-0.66 and |gain| <= 0.03 on their TSD twins; these lenses are
  never given to evolution. Two world rules were set from world
  statistics only, before any lens evaluation of those worlds: Hecate
  target by max next-value entropy (HA_graph still near-constant, 0.88
  majority, kept as a low-headroom world) and P3 sibling p 0.35 -> 0.45.
- A smoke run (N=16, 2x2 generations, older admission rules) was seen:
  it admitted lenses on P3 (PLANTED_INPUTS_RECOVERED), P4, K3, and
  Hecate worlds, and showed that transfer significance was dominated by
  organism-capacity patches. That observation produced two instrument
  changes BEFORE this freeze: transfer and home now require beating a
  matched random null, and admission is 1 per world per epoch (cap 48).
- A timing pilot (N=96, 2x2 generations) was run; only its timing and
  admission counts (8, 12) were read, and the report code was executed on
  it with output suppressed.
- 14 instrument tests pass (tyche/tests/test_v0.py): causality of 150
  mutated random lenses on two worlds, LEAD cheat caught, 2000 mutation
  validity checks, planted attainable and twins dead, raw baseline below
  0.56 on four planted worlds, consequence not in observations.

## 6. Compute

Expected < 1 CPU core-hour on M2 (16 workers, local, unpaid) -- inside
MWO-0004 R2 and below "substantial"; no Fabric lease is claimed. Actual
wall time and worker count are recorded in DONE.json / CONFIG.json.

## 7. What would stop this line

If H5 fails, the instrument is repaired before anything else. If H1
fails with H5 passing, the lens chemistry or the search cannot reach
compositions of depth 3-4 and v1 does not add worlds until it can. If H2
fails, the admission and Pass D gates are too loose and every positive in
this run is suspect. "Not worth continuing" is a legitimate outcome.
