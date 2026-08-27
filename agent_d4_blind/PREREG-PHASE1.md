# PREREG-PHASE1 — D-4 frozen constitution

Status: DRAFT — becomes BINDING when the "FROZEN" section at the bottom is
filled with file hashes and committed. After that commit: no primitive
addition/deletion, no threshold movement, no mutation reweighting outside
the preregistered counterfactuals, no probe/target/navigator repair, no
horizon extension, no rerun-to-positive. Fatal defects discovered during
the binding run: preserve the run, mark invalid, stop.

## 0. Question and claim ladder

Once computational physics is fixed, does it provide broad and navigable
access to executable behavioral change, or has the designer already
constructed privileged corridors? This generation tests P1–P4 only:

- P0 executable self-transformations exist (witness programs)
- P1 generic mutation reaches viable behavioral diversity (G1, G2)
- P2 the viable phenotype space is intrinsically navigable (G4', G6)
- P3 navigation does not depend on designer-privileged corridors (G5, G7, G8)
- P4 strong history-free M0 can fairly navigate it (two mechanisms compete)

P5/P6 are not claimed under any outcome. No learner exists in Phase 1.

## 1. Substrates (frozen; run once each; die independently; no repair)

Four machine-native computational bases, all with TOTAL DECODE (every byte
string executes — validity is trivially ~1.0 by construction, disclosed,
never rewarded). Implementations in substrates/vm_substrates.py.

- S1_REG: 48 x 16-bit words; 4 x 16-bit registers; dense 16-opcode decode
  (ALU, shifts, load/move/swap, skip-if-zero/greater, relative jump, IN,
  OUT, HLT); pc wraps mod 48; 128-step budget.
- S2_STACK: 96 one-byte instructions; circular 16-deep 16-bit stack (over/
  underflow wraps); 8 dense op families (push, ALU, stack ops, compare,
  branch-if-zero, branch, IN, OUT); pc wraps mod 96; 128-step budget.
- S3_REWRITE: 16 rules x 3 bytes over an 8-symbol alphabet; leftmost-first
  pair rewriting; rule = (lhs pair, rhs of length 0-3, active bit, 6
  reserved bits); tape cap 16; halts when no rule matches; 64-rewrite budget.
- S4_MEM: 72 ops (low 3 bits of each byte; 5 reserved bits); 16-cell
  wrapping byte tape; inc/dec/left/right/IN/OUT/skip-if-zero/back-jump-6;
  pc wraps mod 72; 128-step budget.

Expressivity witnesses (P0, checked before census; a substrate whose
witness is not viable dies immediately): hand-written echo/collapse
programs defined in code (witness_genome()).

## 2. Behavioral probes and fingerprints (frozen)

- 8 probe inputs, each 8 nibbles, drawn once from seed 20260827.
- Per-probe fingerprint row: (output tuple <= 8 nibbles, log2-bucketed step
  count, log2-bucketed touched-locations count, halted flag, trace set).
- Phenotype key: exact identity of (outputs, buckets, halted) across probes.
- d1 (primary distance): mean over probes of positional nibble mismatch on
  outputs padded to 8 with a sentinel; in [0,1].
- Auxiliary distances (reported, never gated alone): step-profile L1,
  touched-profile L1, trace Jaccard.
- VIABLE := output nonempty on >= 4 probes AND >= 2 distinct output tuples
  across probes (input sensitivity) AND >= 1 executed step.
- Finite-probe disclosure: phenotype equality is equality on the frozen
  probes; no global equivalence claim is made.

## 3. Mutation physics (frozen; content-blind; identical across substrates)

Five single-parent operators on raw encodings (cell = the substrate's
natural alignment unit: 2 bytes for S1, 3 for S3, 1 for S2/S4):

- OP0 bitflip burst: k bit flips, k = 1 + min(Geom(0.5), 7)
- OP1 cell substitution: one uniform cell replaced with uniform bytes
- OP2 block copy: 2-8 cells duplicated within the genome
- OP3 block swap: two disjoint equal-length blocks exchanged
- OP4 rotation: whole genome rotated by a uniform cell offset

Plus one registered two-parent mechanism: one-point crossover at a cell
boundary, reachable ONLY through navigator N4, censused separately, and
ablated as a counterfactual like any other mechanism.

Menu distribution is physics: uniform over OP0-OP4 via sample_op();
navigators never choose named operators.

## 4. Operator causal census (frozen protocol)

1,200 viable parents x 5 ops x 4 reps (= 24,000 transitions) + 500
crossover pairs. Per operator: identity rate, child-viability, effective
rate (non-identity AND viable), displacement distribution (d1 mean/median/
p90), reach support, pairwise reach-overlap Jaccard, reversibility (400
sampled non-identity transitions x 8 inverse tries), downstream stats.
An operator with effective rate < 0.02 is DEAD and disclosed.

Mutation-source identifiability (PRIV-1): frozen softmax classifier
(d4core/classifier.py: 300 epochs, lr 0.5, L2 1e-4, seed 7700), trained on
non-identity transitions from viable parents, features = behavioral
displacement only, 70/30 split grouped by parent, full confusion matrix +
Wilson CI + chance level reported. Displacement anisotropy: top-1
covariance eigenshare of non-identity displacement features (PRIV-2).

## 5. Target selection (frozen; deterministic; independent of navigation)

64 random-viable starts; uniform-menu random walks of 150 accepted viable
steps (attempt cap 5x); pool = deduped phenotypes recorded at every
accepted step. Remoteness = mean d1 to 48 fresh random-viable references.
Strata = remoteness EXTremes: near = bottom decile, mid = middle decile
(45-55%), far = top decile. Within each stratum: 4 lowest-density + 4
highest-density members (density = pool-mates within d1 <= 0.15 against a
400-member deterministic subsample), SHA-256 tie-break. 24 targets total.
Disclosure: this measures reproducible accessibility of phenotypes the
physics itself exhibited under an independent seed — not reachability of
arbitrary mathematically-existing phenotypes.

## 6. Navigator suite (frozen; history-free; interface-only)

Budget 1,200 metered evaluations per run; hit = d1 <= 0.10 (reachable by
construction: the target phenotype scores 0). Per target: N1 x 3 seeds,
N2 x 5, N3 x 2, N4 x 5 (= 360 runs per substrate).

- N1 RESTART-WALK: random-accept viable walk, restart after 25 consecutive
  non-viable children.
- N2 HILLCLIMB: greedy d1 descent, plateau tolerance (accept equal w.p.
  0.5), restart after 60 non-improving or 25 non-viable evaluations.
- N3 NOVELTY: archive novelty walk (k=5 nearest, add threshold 0.05, cap
  400); targetless mapper; incidental hits recorded.
- N4 RECOMBINER: population 16, tournament k=3 on d1-to-target, one-point
  crossover + 50% menu mutation, 5% fresh injection.

Competitive pair for gates: (N2, N4) — single-trajectory local descent vs
population recombination. Coverage runs: N1, N3 x 2 seeds x 3,000 evals.

## 7. Oracle (analysis only)

Per-episode attribution: reverse BFS from each target's hit-ball over the
observed single-parent transition graph (crossover edges excluded); an
episode is oracle-reachable iff its own start lies in the basin. Output
never reaches any navigator. Used only to attribute navigation failure
(topology vs search weakness) and report navigation regret.

## 8. Counterfactual suite (frozen)

Navigation-based counterfactuals run the baseline best pair navigator on
all 24 targets x 2 seeds at the same budget:

- ablation: remove OP_i (5 variants) + remove crossover (N4 without
  crossover)
- reweight: menu weights ~ Dirichlet(2), seeds 101/102/103
- radius: bitflip burst k = 1 + min(Geom(0.75), 15) (doubled radius)
- representation: frozen per-byte nonlinear bijection (random permutation
  of byte values, seed 3301) applied at decode. Phenotype set unchanged
  (bijection); bit-level mutation adjacency genuinely altered; cell-level
  operators commute with the re-coding. Fresh targets under the same frozen
  procedure on the re-coded substrate, then the same navigator.

No counterfactual result feeds back into the frozen physics.

## 9. Budgets and meters

Census 10,000; operator census 24,000 (+500 crossover, +3,200 max
reversibility); targets ~ <= 64x150x5 attempts; navigation 360 runs x
<= 1,200; coverage 4 x 3,000; counterfactuals (6 ablations + 3 reweights +
1 radius + 1 encoding) x 48 runs x <= 1,200. Every evaluate() metered per
component; cache hits metered identically (no cache asymmetry); no
post-budget success (hit checks inside the budget loop).

## 10. Gates (thresholds FROZEN at commit; see d4core/gates.py)

Evaluated in causal order; primary flag = first failure; all flags reported
with margins and CIs.

- G1 PHENOTYPE_POVERTY: viable fraction < 0.005 (n=10,000; SE at gate
  ~0.0007) OR viable phenotype classes < 250.
- G2 DISPLACEMENT_COLLAPSE: pooled identity rate > 0.85 OR pooled effective
  rate < 0.05 (n=24,000; SE < 0.003) OR alive operators < 3 of 5.
- G3 ACCESSIBILITY_FRAGMENTED: navigation fails AND oracle far-stratum
  episode reach < 0.20 (topology attribution).
- G4 NAVIGATION_FAILURE: fewer than 2 competitive-pair navigators with
  pooled hit >= 0.25 (n=120 runs each; SE at gate ~0.040) OR best pair
  navigator far-stratum hit < 0.10 (n=40; SE at gate ~0.047 — CI reported
  beside the verdict).
- G5 PRIVILEGED_CORRIDOR (evaluated only around a passing navigation
  baseline; diagnostics always reported): any single-mechanism ablation
  with per-stratum baseline >= 0.15, relative drop > 0.60, AND two-
  proportion z >= 1.96; OR identifiability accuracy > 0.35 jointly with
  anisotropy top-share > 0.85 (calibration: neutral pole C5 acc 0.201 (chance 0.200) /
  aniso 0.412; corridor C3 aniso 0.999, ablation drop 1.0 at z=6.5 — the joint trigger targets common+
  directional menu partitioning; rare corridor ops are caught by ablation).
- G6 REFINDABILITY_FAILURE: best pair navigator re-find ratio < 0.40
  (mean over once-hit targets of per-seed hit fraction; per-target rows
  reported).
- G7 REPRESENTATION_SENSITIVE: |pooled hit (re-coded) - baseline| > 0.15.
- G8 COUNTERFACTUAL_UNSTABLE: worst |pooled hit (reweight/radius) -
  baseline| > 0.15.
- PASS = ACCESSIBILITY_GEOMETRY_ESTABLISHED for that substrate.

Overall verdict: NO_BASIS_PASSED if no substrate passes. If >= 1 passes, it
is frozen; a Phase-2 preregistration MAY then be designed (not executed).

## 11. Human-taxonomy red team (post-run; can only weaken)

After the binding run, recognizable edit-family classifications may be
applied retrospectively to ask whether cheap edits/bottlenecks correspond
to designed semantics. Results can downgrade a PASS to PRIVILEGED_CORRIDOR
in the verdict narrative; they can never strengthen a verdict. OTHER/
UNKNOWN residues are never counted as novelty.

## 12. Instrument provenance

Metric suite validated against seven synthetic geometry controls with known
pathologies (C1 fragmented, C2 identity-dominated, C3 privileged corridor,
C4 one-way trap, C5 navigable, C6 chaos, C7 tiny) — see
PREREG-INSTRUMENT.md and synthetic_geometry_controls/. Instrument
iterations v1->v3 are preserved in git history; the binding instrument is
the one that classifies all seven controls correctly.

## 13. Statistical discipline

Unit of analysis for navigation = (target x seed) runs; for census =
genomes; for operator census = transitions (clustered by parent — grouped
split in the classifier). Wilson 95% CIs on every gated proportion. Seeds:
5 per competitive-pair navigator on the binding run. Every gate value was
checked for attainability before freeze (chance levels and ceilings
documented above; hit criterion reachable by construction; oracle reports
the topological ceiling for navigation gates).

## FROZEN (filled at freeze commit)

- files + SHA-256: TBD
- thresholds status: TBD
- freeze commit: TBD
