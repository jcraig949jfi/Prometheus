# DESIGN -- Endogenous world-record sandbox (expedition 1 apparatus)

Currency: 2026-09-28. Odysseus research worker. Pure ASCII. Stdlib only.
Implements: expedition/accumulation/ACCUMULATION_v0.md (rungs R0-R5).
Doctrine: prompts/2026-09-28_expeditionary/01_OPERATOR_DIRECTIVE_verbatim.md s3
(world-record ruling), s4 (ladder), s15 (campaign), s16 (spikes).
Frozen parameters and decision rules: PREREG.md (+ AMENDMENTS.md).

## 0. Prior work (mandatory search, 2026-09-28)

git grep over origin/main (md/py/txt/json) and over every origin/* branch's
own changes vs main, terms: stigmerg, world record, fossil, readable,
external memory, iterated learning, signalling/signaling game, referential
game, niche construction, "memory written into the world". Findings:

- roles/Odysseus/frontier/poi/raw/I5_program_memory.md TH-01 "Memory written
  into the world (stigmergic inheritance)": the question this sandbox serves;
  cites BS-memory-outside-world OPEN with no anti-experiment (BLIND_SPOTS L6)
  and "organisms-reading-fossils is a doctrine change (RM:208)".
- archaeon/docs/ROADMAP.md:208 (D.7): "organisms that read fossils (a
  program-level doctrine change, not a build)". The operator's s3 ruling is
  that doctrine change, confined to this sandbox. Archaeon fossils are
  evaluator records; nothing here reads or writes them.
- archaeon/frontier/design/artifact_worlds.py + DECISIONS.md DF-013
  (W-artifacts: 12 procedural worlds x persist_shared on/off, "niche
  construction across generations"). Digest 2026-09-21 shows persist and
  reset arms with IDENTICAL ruler trajectories in every listed world: the
  one prior in-program attempt at world-carried inheritance detected
  nothing, and had no planted positive control, so it cannot say whether
  the ruler could have. This sandbox exists to avoid that failure mode.
- roles/Odysseus/frontier/poi/raw/E5 (E5-21, E5-22, L11, bullets 2 and 8):
  stigmergy is usually DESIGNED not emergent (TERMES); memory without
  plasticity is cheap (base-rate warning -> our R0 needs an ablated twin);
  environment-as-memory capacity is set by decay/overwrite (-> eps, K).
- roles/Ananke/research/BACKLOG_TEMPORAL_DISTRIBUTED.md T-ENV-1 ("PTE has a
  write-free environment ... writable field dial (stigmergy)?") and
  CROSS_ENGINE_THREADS.md ("Ensorain WTP marks (no stigmergy finding)"):
  no engine in the program has a readable world record today.
- herakles/HERAKLES_HISTORICAL_COLLIDER_V0/A_FIELD_MAP.md fam-173 (iterated
  learning, Kirby/Smith) and fam-216 (stigmergy): catalogued, never built.
- aporia frontier_campaign_69 dossier 81 (stigmergy) and 83 (a "passive
  niche construction null" attributed to "Sharma 2026 / Genesis v3": LLM
  dossier text, UNVERIFIED; recorded only as a warning that sham controls
  are what decide such claims).
- Branch-only hits: Nestor graphworld brief ("Graph Pheromones ...
  communication becomes environmental modification -- stigmergy", design
  only); Nestor EXTERNAL_SCAFFOLDING s2.4 (Laland/Odling-Smee ecological
  inheritance; NPE carried registers read as ecological inheritance);
  Artemis SI prereg "M_export bits on the export tape (external memory the
  agent wrote)". No branch contains a world-record sandbox or a signalling
  game with destructive controls.
- "signalling game" / "referential game" hits are unrelated (forge
  candidate comments). SerendipityFoundry "NOT a world record" is about
  evidence records -- the separation s3 demands, respected here.
Verdict: no prior implementation; closest relative (Archaeon W-artifacts)
is a null without a known-answer control.

## 1. World (world.py)

  Space: G = 4 colonies ("nests"); each nest has S = 4 forage sites and a
  record of K = 2 cells over an alphabet of A = 4 symbols plus BLANK.
  Hidden environment: each colony's patch site s_g; after every generation
  it is redrawn with p = 0.10 (a slowly changing hidden regularity worth
  remembering: a record COULD pay, and genetic tracking or exploration are
  competing, record-free solutions, so it NEED NOT).
  Organism life (one generation): optionally read the whole nest record
  (cost 0.02/cell), choose a site (explore coin, else choose-table lookup
  on the record tuple), forage (reward 1.0 if at s_g; base 0.1), then
  optionally write or erase one cell (cost 0.05) according to a write
  table indexed by (site visited, found). Writes land in random order, last
  write wins (capacity is finite; overwriting is the physics).
  Physics after the generation: per-cell corruption (eps = 0.01, uniform
  over BLANK + symbols); environment redraw. All organisms then die.
  Delayed access: every read in generation t sees what generation t-1
  (now dead) left, corrupted by noise. Local access: own nest only.
  Reproduction (unplanted): roulette on energy within colony, migration
  0.02, mutation 0.02/gene, and every 20 generations the worst colony is
  replaced by a copy of the best colony's population (a group-level
  resource economy; without it writing is a pure public good and is
  selected away -- a design choice, stated, not hidden). The nest record is
  NOT copied with the population.
  Genome (36 small ints, lookup tables): read bit, explore level, choose
  table (25 entries), write address, write table (8 entries).
  Convention map sigma: a per-world permutation between an organism's write
  output index and the physical symbol stored. The physics (costs, noise,
  capacity) is exactly symmetric under sigma, so sigma is a relabeling the
  world cannot see; an INSTALLED code (designed under sigma = identity)
  breaks under random sigma, an evolved one cannot tell.
  Modes: normal; 'unreadable' (writes land and cost, reads return BLANK --
  the ruling's first control); 'none' (no record layer: the no-record twin).

## 2. Plants (known answers; world.planted_genomes)

Plants are CONTENT in the same genome space (table entries), never extra
machinery; planted worlds reproduce clonally (no selection/mutation).
  P      single code: found at site k -> write symbol k to cell 0; readers
         go to the site named by cell 0 (BLANK -> site 0); explore 0.2.
  P4     two independent objects: caste A writes the high bit of the site
         to cell 0, caste B the low bit to cell 1 (distinct founders);
         readers combine both. A planted R4 positive.
  N_a    record informative (P writers) but readers ignore it.
  N_b    record uninformative (constant per-genotype symbols; last writer
         wins) and readers decode it as P.
  C      cheat: biased environment (site 0 favoured); P writers; readers go
         to site 0 whenever cell 0 is non-BLANK. Mere presence pays.
  P_sigma P under random sigma (does the battery see the plant as installed?)

## 3. Battery (battery.py) -- every test is an intervention on saved state

Save/restore: world.snapshot() is an exact structural copy including both
RNG states (rng_phys: noise + environment; rng_bio: organism coins,
reproduction). rng_phys makes a FIXED number of draws per generation
independent of organisms, so twins and probe arms share the exact
environment event stream (asserted in r0_stat). Probe RNGs are paired
across arms within a world and independent across worlds (AMENDMENTS A1).

  R0 persistence      snapshots every 10 gens over the last 200; producers
                      removed; 5 gens of physics only; LOO decodability of
                      the producing generation's s from the record, minus
                      the same for a history-ablated twin (restored 30 gens
                      earlier, all writes suppressed, same event stream).
                      (h) history-specificity = decodability of the
                      history; (n) not-initial = ablated-twin subtraction.
  R1 later reuse      first consumer generation, own colony: intact vs
                      record deleted.
  R2 new consumer     receivers = population of another colony, placed in
                      this nest after its producers are dead; intact vs the
                      max of (deleted, no-record, unreadable). Assertion
                      that no receiver ever wrote the record (uids).
  R3 content          records permuted between colonies (capacity-matched,
                      same position and format); equal-capacity random
                      (non-BLANK cells re-drawn, BLANK kept: presence
                      pattern preserved exactly -> the cheat's signature);
                      irrelevant injection (random symbols into cells nobody
                      wrote in 20 gens) must be EQUIVALENT to intact.
                      Reported: episode permutation (own record 50 gens
                      earlier), fresh-world transfer (record into a
                      different world with its s matched).
  Convention          paired arms (P vs P_sigma, U_id vs U_sigma).
  Frozen readout      U_frozen: one random reader shared by the world, never
                      mutated; only writers evolve.
  R4 recombination    2x2 cell deletion; interaction term and pair-over-best
                      single; provenance: founder sets writing each cell
                      (evaluator-only taint), Jaccard <= 0.2.
  R5 ceiling          40-generation window, dynamics continuing, CEILING and
                      SPEED reported separately; (a) no-record probe, (b)
                      recompute arm at the v0-literal production budget
                      (and a per-consumer budget, diagnostic), (c) pristine
                      record-free worlds.
  R6                  not implemented (s7).

## 4. Forbidden-information guarantees (s3 list) and enforcement

The organism is exactly two functions, organism_choose(genome, obs_idx,
coin, rand_site) and organism_write(genome, i_write, site, found). They are
pure; they receive no world object.

  seeds / ids / labels / treatment   never arguments. tests/test_mechanics:
                                     code objects reference only their
                                     arguments + EXPLORE_LEVELS; no closures.
  evaluator state, provenance, uids  live in state['ev'] and organism tags;
                                     poisoning them leaves the trajectory
                                     bit-identical (test).
  hidden environment s               never observed; only the local outcome
                                     'found' (being at the patch) -- test:
                                     changing s changes no choice.
  future events                      environment redraw happens after all
                                     reads/writes; rewriting the physics RNG
                                     from t on leaves generation t identical
                                     (test).
  experimenter semantics             no symbol has a meaning in the physics;
                                     sigma symmetry test; unplanted initial
                                     genomes are uniform (symmetric under
                                     sigma).
  evidence store / notes / holdouts  the sandbox imports nothing from the
                                     repository and writes only JSON into
                                     its own directory; no holdout exists.
  observer-only records              snapshots and logs are evaluator-side
                                     and are never loaded into a world that
                                     continues (probes are discarded).
Residual, stated: the organism's coin draws come from a seeded RNG. The
seed is not observable, but a sufficiently complex organism could in
principle model the PRNG; with 36-entry lookup tables this is impossible
here, and would need a hardware-noise or cryptographic source in a richer
world.

## 5. Files

  world.py, battery.py            physics / battery
  run_battery.py                  `known` (gate) and `unplanted` (refuses
                                  unless known_answer.json gate PASS)
  tests/test_mechanics.py         determinism, blindness, no-lookahead
  tests/test_known_answer.py      single-world directions + gate recompute
  known_answer_run1_GATE_FAILED.json, known_answer.json, unplanted.json
  PREREG.md, AMENDMENTS.md, RESULT.md

## 6. Cost

Planted world + battery ~1-2 CPU-s; unplanted world (3000 gens) ~25-40 CPU-s.

## 7. Not built

R6 (recursive): needs a notion of "new object" beyond two cells; in a
K = 2 record there is no room for an object stock that raises the rate of
acquiring new objects. The ladder is truncated at R5 on purpose.
