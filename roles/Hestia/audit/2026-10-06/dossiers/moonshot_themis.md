# Dossier: Project Moonshot (Themis), H2 survival-only evolution and H3 the integer neural primitive

Audit group G3. Auditor: Hestia audit worker (read-only). Currency 2026-10-06.
Audited as a DESIGNED engine: no organism, world, S-meter or neural primitive has been built
or run for Moonshot.

VERDICT: INSUFFICIENT_EVIDENCE -- nothing scientific exists to judge (0 lines of organism, world-task or neural-primitive code; the only Moonshot code is a synthetic-epoch git-CAS fabric), the "integer neural primitive" is not specified anywhere, and the sibling evidence from PTE predicts that H2 passes trivially at the 1-bit floor and then strands in the same composition desert, unless the representation is changed first.

## 0. Identity

- Design: roles/Themis/design/MOONSHOT_DESIGN_v0.3.md (437 lines, design of record),
  MOONSHOT_DESIGN_v0.2_ASTRA_REVIEW.md (581 lines, the external review), superseded/
  MOONSHOT_DESIGN_v0.1.md and v0.2.md, MOONSHOT_ECONOMICS_APX_v1_2026-10-05.md,
  LANE_C_M4_KICKOFF.md (not read). Epic: ops/epics/EP-MOONSHOT/EPIC.json, README.md.
- Code: moonshot/ (21 tracked files, 2926 lines incl. CONTRACT.md and the C008 review;
  12 .py modules). Named substrate: SerendipityFoundry/worldfoundry/wforge (593 lines) +
  Proteus (G6, not audited here).
- Seat: Themis. Status: roles/Themis/STATUS.md (ACTIVE; "VALID not applicable
  (infrastructure; no science run)"). Calibration ledger: roles/Themis/calibration/LEDGER.md
  has zero rows.
- Tree: worktree at 3fed30ac9; last commit touching roles/Themis or moonshot = 0a7eae4d9.
- READ IN FULL: MOONSHOT_DESIGN_v0.3.md; EP-MOONSHOT README.md and EPIC.json;
  wforge/world.py and wforge/genome.py; moonshot/epoch/runtime.py lines 1-60;
  Themis STATUS.md. READ IN PART: v0.2 (s13 Launchpad, s17 risks), v0.1 (s7.3, s10.4,
  economics framing), the Astra review (F02, F06, F09), C008 review packet header.
- NOT READ: moonshot/epoch/{store,worker,gitio,join,validate,bench,model}.py, CONTRACT.md,
  tests; LANE_C_M4_KICKOFF.md; Themis journals; the operator prompts under
  roles/Themis/prompts/; the Proteus organism VM (G6 audits it); apollo/ (excluded from this
  audit by AUDIT_PLAN s1, cited only through the Moonshot docs).

## 1. Mechanism

1.1 What is DESIGNED (prose only):
- Organism = "deterministic program over a fixed palette (optionally an integer neural
  module)" (v0.3:187-189, R1). Neural primitives "integer/quantized ... evolved by seeded
  mutation (no backprop)", fusion "neural-as-primitive first" (v0.3:220-223, R7).
- World = deterministic function of (grammar, seed, mutation-history) (v0.3:190-191, R2);
  Launchpad world is FIXED (v0.3:290-291). The floor task is "a delayed-cue
  partial-observability micro-world (cue shown, cue vanishes, acting on the vanished cue later
  determines survival -- delayed-match-to-sample)" (superseded v0.2:373-375).
- Selection = survival/reproduction only, constitutionally air-gapped from any sagacity
  score (v0.3:194-200, R4); sagacity scored offline (R5) by a null family plus three causal
  interventions: channel-cut, information-destroying resample (both must drop) and an
  information-preserving sham (must not drop) (v0.3:205-219, R6).
- Reachability levels RC0 (a plant exhibits it), RC1 (fitness-improving intermediaries
  exist), RC2 (a search crosses at an estimated rate) (v0.3:226-233).
- H3: HYB (palette + neural primitive) vs SYM at matched budget (H3a), plus a post-search
  primitive-disable contrast (H3b) (v0.3:150-155).

1.2 What the CODE does:
- moonshot/epoch/ is a distribution fabric: an epoch = immutable checkpoint + spec ->
  trace + next checkpoint, published by git compare-and-swap. The only runtime is
  synthetic.v1, "deterministic CPU busy-work (Lane C: no organisms, no world, no science)":
  iterate sha256 work_iterations times and emit hashes (runtime.py:1-14, 41-60).
  CONTRACT.md:6 states the same scope.
- No file in the repository implements an integer neural primitive for Moonshot: git grep
  over *.py for "integer neural", "neural primitive", "HYB" returns nothing; git grep
  -i "neural|organism|HYB" in moonshot/ hits only prose saying there are none.
- No delayed-cue world exists: git grep for "delayed-cue", "delayed-match", "DMTS" in *.py
  returns nothing. wforge grammar v0 (world.py:89-165) generates random linear-modular
  register worlds with a hidden yield window; it has no cue/vanish/choose mechanic.
- wforge has no organism or agent: Encounter.step takes an externally supplied action list
  per slot (world.py:202-224). The organism must come from Proteus.
- The F09 defect the review reproduced is visible in the source: when cost > charge the code
  sets mag, cost = 0, 0 (world.py:216-217) but the loop that queues writes iterates the
  original action vector and uses x % 8, not mag (world.py:220-224), so an unaffordable
  action still writes amt*251 into a register. Status per v0.3:82-87: handed to Daedalus,
  STOP condition for survival science.

DOCUMENTED vs CODE: the design documents describe a cognitive-evolution engine; the code is
a provenance-grade job fabric (synthetic epochs, CAS, auto-join; 148 tests per
STATUS.md). The ratio is roughly 1250 lines of design + 2900 lines of infrastructure to 0
lines of organism, task world, primitive or S-meter.

## 2. Evidence

OBSERVED: none for H2 or H3. For infrastructure only: Themis STATUS.md reports D3 matrix 148
tests green on Windows and Linux and a real worker join replayed (not re-run here; not
cognitive evidence).
CLAIMED: the F09 probe (charge 1, cost 3, register delta 251) is CLAIMED by the review
(MOONSHOT_DESIGN_v0.2_ASTRA_REVIEW.md:359-372); I confirmed the defect by reading
world.py:212-224, not by running it.
DESIGNED: H1, H2, H3, R1-R13, RC0-RC2, the Launchpad SYM-vs-HYB assay. v0.3:10-14 and
s16 (v0.3:407-414) explicitly forbid running evolutionary science now.
Prior negatives the design itself invokes: Apollo, the program's earlier neural evolution
line, "800 gens matched deterministic exactly" (v0.1:371) and "the neural half stays inert:
the honest Apollo base rate" (v0.2:414; v0.1:545). Apollo is outside this audit's scope
(AUDIT_PLAN s1 excludes it); it is cited here only as the design's own stated base rate.

## 3. Matrix

### 3a. Combinatorial explosion and reachability

The search space cannot be written yet: the palette, program length, primitive arity and
weight width are unspecified. What can be written:

- The floor task is trivially small. A balanced binary cue that must be held through a
  blank delay is a 1-bit memory problem; the review's own finite enumeration gives intact = 1,
  cut/resample = 1/2 (MOONSHOT_DESIGN_v0.2_ASTRA_REVIEW.md:116-122). Reactive survival over k
  independent lethal delayed decisions is 0.5^k: k=4 0.0625, k=8 0.0039, k=16 1.5e-5
  (scratch moon_power.py). So survival-only selection on the floor world has a STRONG signal
  -- and the solution is a 1-bit latch.
- PTE is the direct sibling measurement of exactly this task: PTE's HOLD family is "hold a
  1-bit cue through distractors at one site", and C1 found it in 97/155 evolve cells, mostly
  as the trivial local latch (Ananke C1_REPORT.md:41, 83). The floor of H2 is therefore
  expected to PASS in a straight-line register substrate with a GA, and to show nothing
  beyond a latch.
- The next rung (any "progressively richer" world where one retained bit gates the use of
  another: context-dependent DMTS, a mapping that flips) is PTE's FLIP. PTE's measured rate:
  0/290 random-start searches across C1, C2A, C2B, C2C, upper bound ~1% per search; immune to
  4x budget, shaping removal, 4x selector worlds, a copy stone, a graded stone and a block
  operator (Ananke dossier s2). There is no reason to expect a survival-only signal to do
  better: survival is binary per life and noisier than PTE's accuracy+shaping, and PTE found
  that partial function near B ~.6 is neither climbed nor retained (Ananke
  RESULT_C2BX_C2C.md:88-98).
- H3a statistics. The discovery unit is an independent search population (v0.3:231-232).
  Two-proportion sample sizes at alpha .05, power .8 (scratch moon_power.py): 10% vs 20% ->
  199 populations per arm; 5% vs 10% -> 435; 1% vs 3% -> 769; 0.3% vs 1% -> 2068. "Hundreds of
  seeds" (v0.2:375) is adequate only if the floor crossing rate is far from both 0 and 1. At
  the 1-bit floor it will be near 1 (no contrast); at the FLIP rung it will be near 0 (no
  power). The design has no stated rung where the base rate is in the 10-50% band where H3a
  can be decided.

### 3b. Cosplay vs foundation

- H2 as designed measures whether a GA under survival pressure finds a latch. That is
  foundational only in the sense that memory-dependence is a prerequisite; it is not
  reasoning. The design concedes this (v0.3:97-98: "floor sagacity != world model /
  counterfactual reasoning / general intelligence"). Credit for honesty, but the honest
  ceiling of the Launchpad is "1 bit retained across a delay".
- The "integer neural primitive" is not specified (no fan-in, weight storage, accumulation
  width, activation, recurrence or plasticity). Evolved-by-mutation integer weights with
  no in-life update are just more immediate fields in the genome: they change search-space
  geometry (F06 says exactly this, v0.3:65-68), they are not a learning mechanism. The one
  version of the primitive that WOULD be foundational for "retained hidden information" is
  a PLASTIC primitive: a within-life update rule (e.g. integer Hebbian or a gated write) so
  that information is acquired by the organism during its life, not by selection across
  lives. Nothing in v0.1-v0.3 commits to plasticity.
- The rigor apparatus (air-gap, null family, three interventions, typed outcomes, RC levels,
  fresh blinded qualification) is good instrument design and is the real product so far. It
  would detect a 1-bit memory user correctly (the F02 repair is right). It would not, by
  itself, make anything worth detecting appear.

### 3c. Substrate bottlenecks (anticipated from the named substrate)

- wforge worlds are random affine maps mod 2^16 over 4-12 registers with a hidden yield
  window (world.py:93-119). Survival there rewards steering a register into a window, which
  is a control problem with no cue structure; a DMTS world must be written new.
- Interaction: two-slot worlds write into the same register bank with no identity
  (world.py:14-15) -- a superposition channel like PTE's, with the same addressing limit.
- Organism representation: inherited from Proteus (not read here). If it is a flat
  instruction list with point mutation, PTE predicts the composition wall.
- Credit assignment: survival only, by constitution (R4). That forbids exactly the
  compositional credit signal (per-module causal contribution) that PTE's evidence says is
  missing. R4 is correct for measurement hygiene; it is a reachability handicap by design.
- F09: an unpaid-write defect in the action economy corrupts selection until fixed.

## 4. Deliverable

Discovery Approach. Grow organisms in deterministic worlds where survival requires
retained hidden information; select only on survival; measure "sagacity" offline with a
preregistered null family and causal interventions; test whether offering an integer neural
primitive changes discovery and is causally used; run it as a hostile external producer for
the RSO; distribute the search over commodity CPUs with replayable epochs.

The Brick Walls.
1. Trivial floor: the Launchpad task is a 1-bit latch; reactive survival is 0.5 per
   decision, a latch gets 1.0. Sibling evidence: PTE HOLD 97/155 cells, mostly a trivial
   latch. A PASS there certifies the instrument, not cognition.
2. Composition desert one rung up: the context-gated version of the same task is PTE's
   FLIP, 0/290 unseeded searches, robust to every operator change tried. Survival-only
   selection gives a weaker gradient than PTE had.
3. H3 power trap: deciding a 5-vs-10% discovery-rate difference needs ~435 independent
   populations per arm; at the floor (rate ~1) or the FLIP rung (rate ~0) H3a is
   undecidable at any affordable N.
4. Undefined primitive: H3 cannot be audited because the primitive has no semantics. An
   evolve-only integer weight vector is an immediate field, not a mechanism.
5. Process before substance: ~2900 lines of fabric and ~1250 lines of design vs 0 lines of
   organism, world task or primitive; the substrate (wforge) has a live selection-corrupting
   defect and no cue world.

Seed Viability. No seed can be assessed. Two components are worth keeping regardless of
H2/H3: the R6 three-operation causal test with the information-preserving sham (a correct,
general memory-use detector), and the R4 air-gap acceptance test (permuting offline scores
must not change ancestry). The synthetic-epoch fabric is infrastructure, not cognition.

Evolutionary Roadmap.
1. Specify H3's primitive before any build, and make it PLASTIC: an integer unit with
   evolved initial weights AND an evolved within-life update rule (gated Hebbian or
   write-on-event), with saturation and accumulation order specified (N1). Then H3b asks the
   right question: is retained information carried in in-life weight changes?
2. Replace "progressively richer worlds" with a fixed, preregistered task LADDER whose rungs
   are chosen so the expected crossing rate is 10-50% for SYM (calibrated by RC2 pilots),
   e.g. DMTS (1 bit) -> DMTS with distractors -> context-flipped DMTS (FLIP analogue) ->
   two-cue conjunction (XOR analogue). Report per-rung rates; H3a lives on the rung where
   it has power.
3. Borrow PTE's localization protocol wholesale: P/R/V admission, plant retention (PSEED),
   broken-plant recovery (BRK), budget arm (B4X), stepping stone (STEP). It answers "search
   or physics or representation" before anyone spends cloud.
4. Organism representation with reuse: duplication-and-divergence of program blocks or a
   typed graph genome, so a solved DMTS module can be reused on the context-flip rung.
5. Multi-agent dynamics only after rung 3 is reachable: Red Queen ecology (M5) adds
   non-stationarity, which increases the need for in-life memory -- a legitimate pressure
   for plasticity, but only once the representation can respond.

THE ONE decisive experiment. Before building the full Launchpad: a CPU-only RC2 pilot of the
context-flipped DMTS rung (the FLIP analogue), SYM vs HYB-plastic vs HYB-static, 64
independent populations per arm at a fixed budget, survival-only selection, R6 scoring
offline. Kill criterion: if all three arms are <= 2/64 at 4x the floor-rung budget, H2 beyond
the 1-bit floor is UNDERPOWERED-to-unreachable in this substrate and Moonshot should
re-scope to the instrument (H1 + R6) and stop the evolutionary build. If HYB-plastic alone
crosses (>= 8/64) and H3b disable drops it to the null, the plastic primitive is a seed.

## 5. What would change this verdict

- To VIABLE_SEED: the pilot above shows a plastic integer primitive crossing a composition
  rung that SYM and static-weight HYB do not, with the R6 sham passing.
- To DEAD_END: a specified primitive and a built substrate show 0 crossings above the 1-bit
  floor across SYM/HYB at a power-adequate N, or the Proteus organism representation is
  found (by the G6 auditor) to be a flat point-mutation list with no reuse, which makes the
  PTE result directly transferable.
- To SALVAGE_COMPONENT: if Moonshot is formally re-scoped to H1 (RSO hostile integration),
  the R6 detector and air-gap test are the carried components.
- I did not read the Proteus VM or most of moonshot/epoch; a hidden organism/primitive
  implementation elsewhere would change s1.2 (my greps found none).
