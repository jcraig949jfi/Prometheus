# External frontier -- what outside research says that Prometheus should know

Currency: 2026-09-27. Compressed from six raids (raw/E1..E6, ~130 idea
entries, ~200 sources; every citation there carries VERIFIED / UNVERIFIED).
Verified by Odysseus personally (arXiv abstract pages, 2026-09-27): the two
2026 soup papers in s1. Everything else: as the raw file marks it.
Prior coverage by the program (raw/I5 s2): Atlas catalogue (365 systems,
09-19/21), frontier_campaign_69 (97 dossiers, 09-07/11), Lexis library
learning (08-24) and EC prior art (09-03). NEVER covered before this raid:
thermodynamics of computation, information theory as a field,
origin-of-life chemistry, free-energy/active inference; stale: the May AI
items. Pure ASCII.

## 1. The closest external work is now running Prometheus's own experiment

- Cicala, Niklasson, Randazzo, ... Aguera y Arcas, Richards, "Coevolution of
  self-replication and function in a digital primordial soup",
  arXiv:2607.09211 (v1 2026-07-10, v2 2026-09-02). VERIFIED (abstract):
  random 32-byte Z80 programs; replication from random mutation plus
  pairwise interaction; polynomial-evaluation task raises interaction
  probability; findings: replication and problem-solving coevolve;
  pressure to compute yields compact robust replicators; a runtime cost
  yields conditional execution; niches yield an emergent curriculum.
  Per raw/E1,E2 (full text): LDIR block copy is available; a tape-filling
  replicator is displaced by a 4-byte LDIR replicator; robustness: LDIR
  replicators survive 8 random single-byte mutations ~85% vs ~2% for
  load-push. No code link found.
  -> Direct prior art for BEE / NPE / Archaeon Z80 worlds. Their gifts:
  a block-copy instruction and an installed task reward.
- Knierim, Versari, Obryk, Aguera y Arcas, Saurous, "BFF: Simple
  explanations for complex phenomena", arXiv:2607.01483 (2026-07-01).
  VERIFIED (abstract): mutation random walks find self-replicators at
  least as easily as soup interaction; capping ancestry depth/width stops
  TAKEOVER, not EMERGENCE. Per raw/E1,E3 (full text): up to ~25x faster
  with a tuned byte distribution; the 2024 compression signal tracked
  takeover, not first appearance.
  -> Any Prometheus claim that interaction or ecology CREATES replicators
  needs a matched-budget random-walk and random-sampling baseline, and an
  estimate of the ISA's replicator density.
- Cotler, Hongler, Hudcova (2025, arXiv:2510.08342 per raw/E1): computational
  universality does not imply that self-replicators can arise; SUBLEQ soups
  fail empirically. Copy-primitive density is a first-order variable.
- Replicators from random code are 30+ years old (Pargellis; Adami & LaBar
  Avida enumeration). Parasites and well-mixed collapse are expected
  (Tierra, Stringmol, Ichihashi). NOVELTY FOR PROMETHEUS IS AFTER
  REPLICATION.

## 2. Accumulation is the unsolved problem everywhere

- No published system shows abstraction or evolvability accumulating over
  many levels with no human DSL, no LLM prior and no designed fitness
  (raw/E6 s3). BFF/evoloop: emergence without accumulation (evoloops
  shrink). Tierra: shallow arms races. Avida: accumulation only on a
  designed reward ladder (EQU never evolved unscaffolded).
- LLM-driven evolution: library learning shows near-zero reuse under audit
  (arXiv 2410.20274, 2504.03048); simple baselines match AlphaEvolve-style
  pipelines (arXiv 2602.16805); 87% of LLM mutation chains revisit prior
  structure (arXiv 2606.05408); AlphaEvolve mostly rediscovers best-known
  values (arXiv 2511.02864). All VERIFIED per raw/E6/E4.
- Self-modifying agents (Darwin / Huxley / Mendel / Red Queen Goedel
  machines, 2025-26) modify scaffolds around frozen models; lessons that
  transfer: an individual's score poorly predicts its descendants'
  (Clade-Metaproductivity is a lineage measure), and agents tamper with
  their evaluators (DGM fabricated test logs).
- Candidate conditions for accumulation (raw/E6 s3, each with evidence for
  and against): reuse cheaper than re-derivation; environments that change
  with shared structure; uniform physical costs; neutral networks; stepping
  stones; transmission with a bottleneck; self-reference; REPRODUCTION THAT
  REQUIRES COMPUTATION (judged the most important missing one); coevolving
  evaluators.

## 3. Learning without an installed rule has a known minimum

- Almost every "learning without a computer" result installs the
  element-level rule or keeps a computer in the loop (raw/E5 s2). Where a
  local learning rule comes from unaided is open -- Prometheus's niche.
- Habituation: linear time-invariant systems cannot habituate; two fading-
  memory timescales plus a static nonlinearity suffice (2024, 2026; raw/E5).
- Recurring minimum across non-neural learning mechanisms (raw/E5 s3):
  separated timescales; nonlinearity/multistability; use-dependent change
  with decay; a contrast signal (can be supplied by TIMING, e.g. periodic
  forcing); repeated perturbation; competition/frustration; dissipation.
  Candidate minimal set for rule-free learning: timescales + use-dependent
  decay + repeated perturbation + dissipation ("natural induction",
  Watson et al.; mostly simulation).
- Memory without plasticity is generic in random dynamics: any "memory
  found" claim needs a random-system base rate of the same class.

## 4. Measurement: Prometheus already owns the strongest tool

- Intervention with replay beats every observational emergence measure
  (TE, EI, Phi, criticality are contested because observational or
  arbitrary). Keep it the final test; use observational measures only to
  nominate candidates (raw/E3 s3).
- Content vs influence: byte taint = content propagation (CUBFF tracer
  tokens); matched perturbation = influence. Their DISAGREEMENT is a finding
  (content copied but inert; influence without copying).
- Birth authorship is a partial-information-decomposition problem
  (sources executor / material / host -> offspring); fix the redundancy
  function first and report sensitivity.
- Boundary-free objects: local causal states on light cones (Rupe &
  Crutchfield), individuality scans (Krakauer et al.), dynamic Markov
  blanket segmentation (Beck & Ramstead 2025, method only).
- Semantic information = graded scrambling + viability curve (Kolchinsky &
  Wolpert); Prometheus's per-carrier resets are all-or-nothing versions.
- Compression / assembly statistics measure redundancy and takeover, not
  capability; assembly index reduces to straight-line grammar size.
- Learned life/agency detectors are spoofable by a hill climber in ~150
  queries (Gupta & Adami 2026); a soup under selection is a hill climber.
- Open-endedness measures need neutral shadow controls and are
  observer-relative.

## 5. Thermodynamics and origins give sanity bounds Prometheus lacks

- Heredity costs energy: a persistent correlated copy needs sustained
  driving; accuracy -> 0 as driving -> 0 (Poulton, ten Wolde, Ouldridge
  2019). Prometheus Z80 worlds overwrite bytes for free.
- "More dissipation = more adapted" has no universal footing (Kolchinsky
  2024 removes the England-2013 bound); efficient predictors and copiers
  keep dissipation LOW (Still 2012; Ouldridge).
- Eigen error threshold L < ln(sigma)/mu; Landauer 0.0179 eV/bit at 300 K;
  learning efficiency (info gained / entropy produced) <= 1 (Goldt &
  Seifert). Usable as checks on measured copy fidelities.
- GARD critique (Vasas 2010): does selection create NEW attractors or only
  reweight existing ones? The exact test for "heredity without evolution".
- AlChemy revisited (2024): stable organizations that do not compose into
  higher-order ones -- a precise "no major transition" failure mode.

## 6. Current AI: what is substrate-general and what is gravity

Substrate-general (raw/E4 s3): delayed generalisation after memorisation
under a cost pressure (grokking also in non-neural RFMs); complexity
signals move BEFORE task metrics (LLC in nets; high-order entropy in soups);
metric-induced "emergence"; general strategies can be transient; refinement
loops (variation + feedback + retention) drive search-based capability;
evolvability is a lineage property; optimisers exploit evaluators.
RLVR mostly SHARPENS what a base model contains (random-reward controls);
tiny data-free systems (CompressARC 76K params) reach ~20% ARC-AGI-1.
Gravity traps: an LLM in the mutation step; "zero data" that starts from a
pretrained model; benchmark chasing; importing transformer mechanisms and
SAE-style tools; scale or gradients as the explanation; CLIP-style novelty.

## 7. Dead ends the field already hit (do not rediscover)

trivial-copier collapse to one species; designed self-reproducers shrinking;
well-mixed replicator/parasite extinction; "Turing complete => replicators";
"interaction discovers replicators"; unscaffolded complex targets;
unnormalised open-endedness statistics; learned life classifiers as ground
truth; universal dissipation bounds; assembly index as biosignature;
metabolism-first compositional genomes as a route to open-ended evolution.
