# CW01 priority loop — boundary report, cycle 1 (2026-09-18), BEFORE execution

Pool built from e01-e09, all defects (D001-D069), fossils, unrun interventions, anomalies
and translations. Records are immutable (`TRAJECTORIES.jsonl`); states and evidence are
append-only. Rank allocates compute, never truth. Exclusion is waiting.

## Sizes

| quantity | value |
|---|---|
| trajectories in the pool | 20 (9 experiment, 11 anomaly/hypothesis) |
| in TEMPORAL_STASIS at reconcile | 2 (T-E09: composition needs machinery not yet available; T-X06: an instrument fact fully mapped by its probe curve) |
| reactivated from history (never allocated before) | 11 anomaly/hypothesis trajectories: T-X01 hitchhiking, T-X02 train8/held64 decoupling, T-X03 composability predictor, T-X04 invasion-direction reversal, T-X05 burden drop at unchanged capability, T-X07 composition on a generalising task, T-X08 inverted generality, T-X09 ratchet valley, T-X10 free-lunch conditionality, T-X11 precision plateau |
| candidate perturbations | 23 (batch A 12, batch B 11) |
| protected slots | 2 serendipity (P-A11, P-B05), 2 anti-gravity/stasis (P-A04, P-B09) |
| execution budget | ~73 min compute (sum of candidate cost estimates), CPU only, in-process, no Redis, no GPU |

## The frozen ten

| rank | id | parent | delta (what changes) | unchanged | attacks | why now |
|---|---|---|---|---|---|---|
| 1 | P-A11 (serendipity) | T-X07 <- e09 | the e09 chain organism (4 digit args, 3 ops) on e07's accumulate-and-report task with held-out lifetimes; single-op ceiling vs 3-op vs scrambled ops | chain representation, op tables, GA | was e09's boundary the substrate (w13 does not generalise) or the idea? | both code pieces exist |
| 2 | P-B05 (serendipity) | T-E02 | e02's world under e07-style weather (random deletion of bound region cells between steps) with a matched sham arm; fixation ORDER and neutral drift under damage | e02 economics, organism, selection, fixation ruler | whether disruption is the missing pressure that makes a foundation load-bearing | never considered together |
| 3 | P-A04 (anti-gravity) | T-X02 <- e08/e09 | TT lineages on w13 selected on 8 vs 32 vs 128 train seeds; held64 competence rate vs training breadth | organism, world, assay | the assumption behind e08 and e09 that train8 fitness tracks held64 (D065, D069) | gates every future w13 experiment |
| 4 | P-B09 (anti-gravity) | T-X08 <- e04 | evolve e04 under a TTL distribution {7,15,30} vs fixed 15; test across TTLs with cost-matched sham shocks | world otherwise, organism, MI ruler | the inverted generality (improves under LESS pressure) | e07's schedule-generalisation contrast, runnable here in seconds |
| 5 | P-B03 | T-E07 x T-E01 | e07's representation-blind deletion + bit-identical sham + rho0/AURC rulers transplanted into e01's world, where state use DID evolve; STATIC / WEATHER / SHAMWEATHER, 6 lineages each, exact relabelling | e01 economics and organism; e07's damage, sham and ruler definitions; lineage as unit | e07's D059 boundary; e01's I4 gap | the question e07 could not pose is posable here in minutes |
| 6 | P-A08 (anti-gravity) | T-X04 <- e06 | interpolate target geometry between the legacy tree-native and the operation-graph generators (0, .25, .5, .75, 1); invasion both ways per fraction; locate a crossing | both substrates, sharing, price list, selection | a substrate-neutral generator produced the OPPOSITE asymmetry rather than neutrality | both generators exist in world_e06.py |
| 7 | P-A10 (anti-gravity) | T-X01 <- e02/e06 | neutral fixation time vs population structure in e06's world, control A only: elitist tournament vs no-elitism vs 4-deme islands | world, substrate, mutation | the 26-vs-96-generation hitchhiking floor seen in two worlds | it corrupts every ecological noise floor in the campaign |
| 8 | P-A07 | T-E06 | variation regime swap holding world and price list fixed: mutation-only vs crossover-heavy for both substrates; invasion against evolved residents | generator, sharing, price list, selection | D055: TREE's only plausible advantage is dynamic and was never given the chance | e07 showed representation alone did nothing there; search is the untested axis |
| 9 | P-B04 | T-X09 <- e02 | T2 REFUSED unless normalised (impossible, not expensive, without T1); K1 revert actually executed; weaker selection (elite 0.5, sigma 0.06); 4 replicates | world otherwise, 9 genes, T1/T3/T4, detector procedure | e02's stated design consequence; the valley; the never-run knockout | e02 said exactly what to change |
| 10 | P-A01 | T-E08 | representatives chosen on a DISJOINT held-out selection seed set; minimum competent count from the pilot RATE with margin | w13, organism, arms, lambda 390, schedule, assay, statistic | D066 eligibility surface | exact failure known and cheap to remove |

## Waiting, not rejected (13)

P-A05 composability predictor (35.0), P-A09 one-gene persistence re-pose of e07, P-A02
e08 fossil rank-profile ablation, P-B08 powered J1 re-run, P-B02 e01 2-D conditionality
map, P-B06 e03 I3/I4, P-B10 e03 plateau sweep, P-A03 lambda dose, P-A12 tax on e07's
organism, P-B07 tax on e03's policy, P-B01 e01 I2 scramble, P-B11 e02 K1 as recorded,
P-A06 conjunctive-fraction sweep. Each keeps its record and its score for the next pass.

## Diversity check on the ten

Families: composition, ratchet (2), substrate screen, triage, robustness, representation
ecology (2), population genetics, burden economics. Parent dispositions: COMPLETE (e01
via P-B03), NULL (e02 x2), INCONCLUSIVE (e04, e06 x2, e07, e08), unallocated anomalies
(4). Perturbation types: serendipity (2), search-boundary (2), exploratory (3),
transplant (1), break-null (1), break-inconclusive (1). Ages: 09-17 (6) and 09-18 (4).

## Execution contract for the cycle

Each perturbation runs as `experiments/cw01-loop1/<id>/` with its own `PREREG.json`
(parent, delta, unchanged, attacks, claim type, decision rule and null written BEFORE the
run), a driver, `RESULT.json`, and appends to `loop/EVIDENCE.jsonl` and `loop/STATE.jsonl`
(material-change verdict, stasis decision). Frozen old world modules are imported and
wrapped, never edited. Exploratory and serendipity runs make descriptive claims only;
transplant/break-null/break-inconclusive runs preregister a null and a decision rule.
Seeds: attempt ids `cw01-loop1-<id>`; no production seed from any prior experiment.

## Dependencies blocking execution

None. Every parent world module runs in-process on this interpreter (redis absent; only
e08/e09 touch the substrate and they bypass the redis-importing entry module). e01's
elite fraction is hardcoded (world_e01.py:301) and will be wrapped, not edited.
