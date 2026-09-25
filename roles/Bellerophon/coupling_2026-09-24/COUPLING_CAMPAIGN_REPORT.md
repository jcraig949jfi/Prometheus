# COUPLING CAMPAIGN REPORT -- Bellerophon, physics v3 (computation -> copy resource -> reproduction)

Written 2026-09-25 after the frozen analysis point. Prereg: COUPLING_CAMPAIGN_PREREG.md (frozen c9bed96de; Amendment 1
6607b3cb5, operational only). Analysis: tools/coupling_analysis.py, byte-identical to the frozen file (git diff
c9bed96de..HEAD empty), run 2026-09-25 ~19:20-19:38Z with --replay 0.03 --workers 12 (the worker count is scheduling
only). Machine-readable results: receipts/COUPLING_RESULTS.json, receipts/OPS_ACCOUNTING.json,
COUPLING_CAUSAL_LEDGER.jsonl (439 rows), COUPLING_ORIGIN_LEDGER.jsonl (68 rows).

## 0. Header (directive format)

1. Runtime: 8.63 h ACTIVE (3 segments), 23.03 h wall clock (2026-09-24T20:07:31Z -> 2026-09-25T19:09:26Z).
2. Total runs: 11,657 = 11,372 Phase 1 (fixed) + 285 Phase 2 AUTO (19 candidates x 3 seeds x 5 arms). EXT: 0
   planned (no cell's ON-YOKED 95% half-width exceeded 0.10). NOT_RUN 0 in every phase.
3. Failures/voids: 0 VOID runs, 0 ledger imbalances, 0 duplicate ids. Operational: one host-OOM kill (F4) and one
   operator-requested stop for a reboot; neither lost or altered an observation.
4. Control status: A8 positive reproducer (physics v2) persists 40/40. All negative arms (OFF, SHUFFLED,
   RANDOM_REWARD, DELAYED, IRRELEVANT, YOKED, NOCOMP, NOCOPY, RANDOUT) behave as controls: none maintains competence
   (Lane C comp_final mean 0 to 0.0002 in every non-ON arm, both K).
5. Reproducibility: seeded 3% replay 341/341 byte-identical (Phase 1 + Phase 2).
6. Readiness classification (frozen rule s11): **READY_FOR_MULTIDAY** -- instrument_ok, core (P1 P2 P3),
   novelty (7 AUTO CAUSAL_COUPLED over 6 distinct mechanism keys), generality (6/6 Lane F tasks, 6/8 Lane G
   perturbations). Section 5 states the scope limits that the frozen rule does not see; they constrain the next
   design, they do not change the classification.

## 1. Confirmatory tests (K16, seed-pair sign tests, Holm across P1-P6)

| test | result | numbers |
|---|---|---|
| P1 correct computation raises reproductive output (A1 HYB ON > A3 NOCOMP ON, paid births) | HOLDS | 40/40 pairs, mean +38,926 births, p_holm < 1e-11 |
| P2 competence enriched under contingent earning (C comp_final ON > YOKED) | HOLDS | 149 vs 0 (1 tie), mean +0.767 [0.749, 0.784] |
| P3 heritability (r_cc - r_nc > 0, ON runs) | HOLDS | 150/150 runs, mean gap 0.9987 [0.9984, 0.9989] |
| P4 contingent computation lowers extinction (YOKED > ON) | HOLDS | 67 vs 1 (82 ties), +0.44 |
| P5 preservation across reproduction (r_cc ON > YOKED) | FAILS, reversed | 0 vs 114, mean -0.0007 (both arms ~0.999: ceiling) |
| P6 conflict repair (E2 comp_sr_alive ON > OFF) | FAILS (underpowered) | 4/60 vs 0/60, p = 0.125 |

K40 (secondary) replicates the direction of P1, P2 and P4 (C comp_final ON 0.563 vs YOKED 0.0; ON persists 143/150
vs YOKED 66/150); E2 at K40 1/60 vs 0/60.

## 2. The ten plain questions

**Did useful computation causally affect reproduction?** Yes. With identical base income and identical coupling,
the organism whose first output is correct (A1) outbreeds its OUT-ablated twin (A3) in 40/40 seeds and persists 40/40
vs 18/40; SHUFFLED (answer compared to an unseen input) and RANDOUT (constant output) collapse to control level. The
effect needs contingency, not just supply: YOKED gets the ON run's bonus total tick by tick, spread evenly, and
still goes extinct in 67/150 (K16) where ON loses 1.

**Did descendants become more computationally competent?** In seeded populations, competence was MAINTAINED rather
than gained: ON holds 0.77 of the world competent at tick 500; every other arm, including the 83 YOKED worlds that
survive, ends at 0 -- mutation erodes unpaid task code to nothing within 500 ticks. Genuine GAIN from a population
with no task code occurred in one place only: pure copiers under the ECHO task (Lane B-cop). ECHO K40: a de novo
competent self-replicator present at the end in 29/150 ON worlds vs 6/150 in each of OFF, YOKED and SHUFFLED
(comp_final ON vs YOKED p = 3.5e-6). ECHO K16: 7 vs 2-3, not significant. CONST (both K): 0-1. Fully random worlds
(B-rand, 3,200 runs): 0 de novo competent replicators in any arm.

**Was competence heritable?** Yes, in the transmission sense: competent self-replicating parents produce competent
children 99.9% of the time, non-competent parents almost never. This is copy fidelity of whole-window LDIR copiers,
not an evolved property; the test would pass for any faithful copier of any code (see s5, F7).

**Did evolution begin protecting computation from reproductive damage?** No evidence. P5 is reversed by a negligible
margin (r_cc 0.999 in both arms; the measure is at ceiling and cannot see protection). P6 (repair of a copier that
wrecks its own task) went 4/60 vs 0/60, not significant. The three E2 repair candidates that were transplanted all
came out CAUSAL_COUPLED (s3), so repair occurs and is coupling-dependent, but rarely.

**Did reproductive architecture change causally?** Only weakly observed. Dominant ON architectures in Lane F are the
seeded shape (single LDIR, copy_covers_task true, copy length 64); the architecture descriptors show no preregistered
shift that the frozen analysis tests. The E2 repairs are the only architecture changes with a causal verdict.

**Which effects replicated across tasks/substrates?** Maintenance of seeded competence under ON vs YOKED/OFF replicated
in 6/6 tasks (CONST 0.76, ECHO 0.79, INC 0.79, SUM2 0.72, COND_ONE 0.35, COND_MULTI 0.18; OFF and YOKED ~0) and in
6/8 substrate perturbations (copy_cost2, undefined->HALT, mutation LOW and VLOW, VM_COPY, BYTECODE32). Not in
ldir_cost4 (worlds die in both arms: 3/80 persist) or CONSTRUCTIVE (worlds persist 80/80 in both arms and coupling
changes nothing). Both parameterizations agree in direction.

**Which candidate phenomena collapsed?** (a) Heritability as evidence of evolution: it is copier fidelity. (b)
Preservation (P5): unmeasurable at ceiling. (c) 12/19 AUTO candidates SURVIVE_WITHOUT_COUPLING_OR_TASK -- 7 of them
from ECHO K40, where the base income alone keeps copiers viable, so their persistence is not attributable to the
task. (d) Lane J historical specimens: nothing resurrected as a coupled computer except 4/6 copier-damaged-task
grafts (ON) and single cases elsewhere; failed non-replicators 0/20 in both arms. (e) Any origin-of-computation claim
from random soup: B-rand 0/3,200.

**What exploits or confounds appeared?** (1) Correct outputs by organisms whose own tape is not competent (partner-code
execution in the SHARED window, lucky partial solvers): 1-6% of paid correct outputs in most lanes, 14.6% in Lane F,
25% in Lane J, 67% of a tiny total in B-rand. Designed probes (Lane I: slider, input corrupter, multi-OUT) did not
turn into dominant exploits: HYB persisted 30/30 and competent organisms made ~98% of correct outputs. (2) The exploit
specimen ledger is truncated at 400 rows, all from Lane A (F9) -- the specimen record is not representative. (3)
YOKED supply is identical in total but not per capita over time; the contingency interpretation of P2/P4 rests on the
fact that YOKED survivors (83/150) also end at 0 competence, which a pure supply story does not predict.

**What is the strongest surviving mechanism?** Contingent earning selects FOR task code that would otherwise be lost to
mutation, strongly enough to (i) keep 18-85% of a world competent across six tasks and six substrates, and (ii)
multiply the rate at which pure copiers acquire the simplest I/O computation by ~5x (ECHO K40: 29 vs 6 of 150),
with 4 transplanted de novo acquirers that succeed ON 3/3 and fail OFF and RANDOM_REWARD 0/3. That is the
computation -> resource -> reproduction -> heritable variation loop the directive asked about, closed at the
lowest rung.

**Is a 2-3 day Bellerophon campaign scientifically justified?** By the frozen rule, yes (READY_FOR_MULTIDAY). My own
reading adds a scope: the justification is the B-cop/E2 evidence (acquisition and repair), not the large seeded
effects, which show maintenance only. See NEXT_MULTIDAY_CAMPAIGN.md.

**If yes, what should it search for?** Whether coupling can carry copiers up a task ladder beyond ECHO (acquisition
of the next task given the previous one), whether protection/modularization of task code evolves when a
damage-sensitive preservation metric replaces r_cc, and whether repair (E2) becomes common over longer horizons.
Details and falsifiers in NEXT_MULTIDAY_CAMPAIGN.md.

## 3. Phase 2 (AUTO) verdicts

19 candidates (frozen rule: dominant competent SR tape at the end of an ON run in B-rand, B-cop, E2; not a fixture;
fully competent alone). Transplanted alone into fresh random worlds, 3 seeds x {ON, OFF, RANDOM_REWARD, TASK_ABLATED
ON, COPY_ABLATED ON}.

| source cell | CAUSAL_COUPLED | SURVIVES_WITHOUT_COUPLING_OR_TASK |
|---|---|---|
| B-cop ECHO K16 ON | 3 | 3 |
| B-cop ECHO K40 ON | 1 | 7 |
| E2 ON (K16 2, K40 1) | 3 | 2 |
| B-rand (any) | 0 candidates | -- |

Causal candidates: 7, distinct mechanism keys 6 (laneH). In all 7, ON succeeded 2-3/3 while OFF and RANDOM_REWARD
succeeded 0/3 each. Tapes and per-arm counts: COUPLING_CAUSAL_LEDGER.jsonl kind auto_candidate.

## 4. Secondary and descriptive

- Lane A (K16): A1 persists 40/40; A2 OFF 8, A3 NOCOMP 18, A4 NOCOPY 7, A5 SHUFFLED 5, A6 RANDOUT 10, A7 REP ON 9.
- Lane C extinction (K16): ON loses 1/150; OFF, DELAYED, IRRELEVANT lose ~122; RANDOM_REWARD 128; YOKED 67.
- Enrichment (share of births by competent writers / time-mean competent share): ON median 1.26, YOKED 1.91, others
  ~5.2-5.8. The ratio saturates when nearly everyone is competent (ON) and is inflated when a few surviving
  fixtures breed briefly before dying (controls); not interpretable as a selection coefficient (F8).
- Lane E2 rate: K16 ON 4/60, OFF 0, YOKED 0; K40 ON 1/60.
- Lane G, persistence ON vs OFF (of 80): BYTECODE32 65/5, VM_COPY 80/16, copy_cost2 77/5, mut_low 76/30,
  mut_vlow 80/39, undefined_halt 80/80 (competence 0.85 vs 0), ldir_cost4 3/3, CONSTRUCTIVE 80/80 (no competence
  difference).
- Origin ledger: 68 de novo runs, 62 distinct tapes, 59 distinct mechanism keys; by arm B-cop ON 37, OFF 9, SHUFFLED
  9, YOKED 8, E2 ON 5. Fixture-descendant variants (C/F/G) are counted separately and are not origins.

## 5. Scope limits the frozen rule does not see (self-dissent, recorded before any next design)

1. Core P1-P3 are satisfied by seeded hand-written fixtures. They prove the coupling is a working causal channel;
   they do not show evolution creating computation.
2. P3 is a copy-fidelity measure (F7); P5 sits at its ceiling (F7). Neither can detect protection.
3. Generality (6/6 tasks, 6/8 substrates) is generality of MAINTENANCE of seeded code.
4. The only acquisition evidence is ECHO, the simplest I/O task, significant at K40 only; CONST never; random soup
   never. The novelty clause passed on 7 transplants (4 acquisition, 3 repair).
5. 500 ticks is short; nothing here says what happens over thousands of generations.

The classification stands as the frozen rule computed it. These limits are why the next campaign targets
acquisition and protection rather than more of the maintenance effect.

## 6. Operations accounting (restart authorization, "Final accounting")

| item | value |
|---|---|
| total wall-clock elapsed | 23.03 h (20:07:31Z 09-24 -> 19:09:26Z 09-25) |
| active campaign runtime | 8.63 h: seg 1 20:07:31-21:23:31Z (1 h 16 min, per operator), seg 2 10:35:24-10:59:15Z, seg 3 12:11:44-19:09:26Z |
| OOM suspension | 13.2 h (21:23:31Z 09-24 -> 10:35:24Z 09-25); a further 1.2 h reboot pause 10:59:15-12:11:44Z (operator stop) |
| pre-OOM observations retained | 959 (retained exactly once) |
| post-restart observations | 10,698 |
| concurrency over time | 20 workers seg 1 (pre-amendment); 20 workers, recycled every 6 runs, segs 2-3 |
| co-running heavy job | ENVGATE-02 (Archaeon, 6 workers) 18:30:33Z -> campaign end 19:09:26Z (38.9 min), from its OPS_LOG.jsonl; min free RAM in that window 17.2 GB, no pause events (Cyclops M2-1, #585/#589/#593) |
| peak memory | min free RAM 13.67 GB over 884 samples; peak driver-tree RSS 3,044 MB; peak worker RSS 300 MB (pre-amendment ~400 MB, no recycling) |
| worker recycling / recovery | every 6 runs; 0 supervisor relaunches after crashes; 2 relaunches after stops (OOM, reboot), each preceded by a passing integrity gate |
| NOT_RUN | 0 (phase 1, phase 2, ext) |
| did any execution amendment change scientific content | No. Plan sha256 a3bc8c8e... unchanged; scientific modules byte-identical to the c9bed96de pin; replay 341/341 identical |

Runtime evidence (not committed; C:/Users/James/z80atlas_coupling_2026-09-24), sha256:
results.jsonl 23b55f7843525f35f358ec288ba50f171b44a1b633c20b192f638c41b067bf75;
PHASE2_PLAN.json 430159527bedbbc66a7a4fba76e444b2baba42fad00a1259375b988d2265dd85;
STATUS.json cb5e12bf23c97f70d5f0041f9c97da4f9bb86adaaaa93002f2e461d3ffe674e6;
supervisor.jsonl ec92ac3523b038972989e791047a63b1cec23346b6d625ea4ec10c28b73190b6;
memory.jsonl dbcb6ef163837fdd3945b285dd2c5c05b447199a9ab05a98427117350f318950.
