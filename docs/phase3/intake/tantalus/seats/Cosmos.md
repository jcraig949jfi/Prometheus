# Seat dossier: Cosmos

Crawler: Tantalus (worker)
Tree SHA: 21a47402a (origin/main, worktree F:/Prometheus-worktrees/tantalus-phase3-intake)
Date: 2026-10-01

Summary. Cosmos is an M2 (SPECTREX5) seat created 2026-09-23 that, in one ~7 hour window the same day,
built the "Cosmos World-Graph Engine" (CWE): a numpy-only chamber that runs three hand-written
"substrate families" (a register machine, a delay-line ring, a block cellular tape) on one shared
cue-distractor-ask task, labels each parameter point with a phenomenon certificate (SELECTIVE_PAYS.v1),
and mines a restricted grammar of threshold laws over author-declared dimensionless coordinates with
leave-one-lineage-out scoring, a whole-search permutation null, an adversary, a boundary-LOCATION attack
and three sealed holdout families. Two laws survived three sealed universes, but [CORRECTION] they were
later restricted because a zero-parameter rule written from the certificate's own economics ties them on
every sealed universe (RESULTS R-0001/2, 2026-09-29, after Artemis R-14). A successor campaign (C3, P1
decodability + P2 interchange-ablation certificate over "causal accessibility of past information")
produced a preliminary law that was KILLED BEFORE HOLDOUT on 2026-09-29: its main coordinate restated the
P2 certificate and the others fingerprinted the substrate family. C4 (upstream physical causes of usable
history) is a design (v0.2) under review with 5 BLOCKING interim findings; no C4 build exists. The
"substrate-independent law mining" in code is threshold-classifier search over a 4-5 variable feature
space whose variables were written by the same author who wrote every substrate; both campaigns' central
lesson is that the mined law re-derived the label's definition. The "location confound" is that LOLO
balanced accuracy cannot see where a phase boundary sits (pooled metrics hid opposite-signed per-family
offsets), and the "selection confound" is that location-aware selection and the location gate share one
criterion and that selection effects were confounded with seed.

## 1. Identity, charter and pivots

- Created 2026-09-23 06:21 (local -04:00) on M2 with "You're new... I'll give you direction" [IMPL]
  (roles/Cosmos/superseded/RESPONSIBILITIES_precharter_2026-09-23.md; commit 7a90be1d8).
- Charter the same morning: "BUILD THE COSMOS WORLD-GRAPH ENGINE (CWE)", up to 8 h autonomous, "an
  adversarial physics chamber for counterfactual universes... Change almost everything and measure what
  refuses to change"; objective "Qualify the instrument", not discover laws [INTENT]
  (roles/Cosmos/prompts/2026-09-23_charter/00_DIRECTIVE_verbatim.md; 37bdeb690). The directive names
  donors BEE, Archaeon/WSE, Nestor/NPE, Aphrodite, Aether/AGE, Atlas.
- Pivots, in order [IMPL from commit log; CLAIM for dispositions]:
  1. C0 family (C0, C0b, C0e, C0m, C0s, C1, C2, eta2, c2abl, c2x) 2026-09-23 07:41-13:29 local; CLOSED
     PERMANENTLY at af2af37f4 by operator.
  2. C3 "causal accessibility of past information" design draft 2026-09-23 (design/03), Session 1 on
     2026-09-24 (certificate gate public; law, coordinates and visible substrates WITHHELD on local M2
     branches cosmos/c3-s1-2026-09-24 head e73e5eb26 and cosmos/c3-autopsy-2026-09-30).
  3. 2026-09-28 operator research-structure directive: Cosmos = "LAW FOUNDRY"; research/ workspace with
     THREADS/RESULTS/GRAVEYARD/FREEZES (roles/Cosmos/prompts/2026-09-28_operator_research_structure/).
  4. 2026-09-29 coordinate audit REJECT; 2026-09-30 operator: C3 CLOSED / KILLED BEFORE HOLDOUT.
  5. C4 design v0.1 (c37e2c687) -> v0.2 (99541a365), 2026-09-30; build NOT authorized (BOOTSTRAP.md s1).
- Hosts: M2 SPECTREX5 worktree D:/Prometheus-worktrees/cosmos-base-role; runtime state under
  C:/Users/James/cosmos_runs (not in git) [CLAIM, BOOTSTRAP.md s0, HANDOFF s11].
- Relationships: Nestor (writer/custodian of C3 holdouts D and D2), Bellerophon (first D author, notice
  withdrawn; later R-MECH reviewer of C4), Harmonia (audit role offered then moved; ruled the D2 grep
  incident NO_INFORMATION #1110), Artemis (R-14 independent re-derivation of the definition-rung tie),
  Ananke (R-STAT reviewer of C4), Theseus (assigned foreign C4 visible family, not started as of
  2026-10-01), Atlas (ATLAS-37 adapter), Aporia (fleet scheduler under CWO-B), Aether (holdout E reserved
  "for Aether from M4 only", not commissioned) [CLAIM; reports/STATUS_2026-10-01.md, BOOTSTRAP.md].
- Seat status 2026-10-01: ACTIVE, waiting on the foreign family (reports/STATUS_2026-10-01.md) [CLAIM].

## 2. Engine/system inventory

E1. CWE C0 chamber (prometheus/cosmos/*.py, ~3,900 lines incl. tests; numpy 2.4.4 + stdlib only) [IMPL]
- Purpose: find a compact threshold law over declared coordinates that predicts a certificate verdict
  across three code-independent families and transfers to sealed families.
- Entrypoints: `python -m prometheus.cosmos.runtest [--full] [--config c2]`; campaign0.py configs c0, c0b,
  c1, c2 (+ c2abl, c2none, c2rep, c1s29, c2none28); follow-up runners c0e.py, c0m.py, stress.py, g6b.py,
  c1f.py, eta2.py; audit.py.
- Key modules: contract.py (family contract + coordinate maps v1-v4), substrates/{regs,ring,ca}.py,
  phenomenon.py (certificate), world.py (CRN evaluation), miner.py (589 lines; grammar, quotient, LOLO,
  null, mu), pipeline.py (Chamber, MIN_LINEAGES=3), sampler.py, adversary.py, locate.py, select.py,
  boundary.py, quotient.py, independence.py (AST lineage audit), broker.py (sealed holdout broker),
  store.py (SQLite world graph + receipt chain), atlas_export.py, planted/ (pa pb pc ps1 ps2).
- State/persistence: SQLite cwe.sqlite + receipts.jsonl per store under COSMOS_HOME (M2 only); compact
  JSON/TXT copies committed under roles/Cosmos/campaigns/ [IMPL/CLAIM].
- Execution model: single CPU box, process pool for permutation null (memory-bounded, serial fallback,
  D10/D18 in design/02).
- Scale (HANDOFF s4) [RESULT-UNVERIFIED]: 4,619 world nodes, 2,299 typed edges, 4,733 recorded runs,
  ~18,000 private-oracle evaluations, 720 sealed-world runs; default 400 episodes per world.
E2. Sealed holdout families D (well), E (swarm), F (clone): prometheus/cosmos/holdout/ (well.py,
  swarm.py, clone.py, seal.py, run.py, sealed_spec*.json) [IMPL that they exist, from `git ls-files`;
  NOT OPENED by this crawl because the path matches *holdout*]. Sealed at 800072c1e, da57b0ac4,
  7c9e0d58f; all three spent by end of 2026-09-23 [CLAIM, HANDOFF s3].
E3. C3 certificate package (prometheus/cosmos/c3/: task.py, system.py, certify.py, probe.py, calib.py,
  gate.py; ~460 lines) [IMPL]. Public. The C3 visible substrates A/B/C, coordinate construction, law
  search and adversary are NOT on main (withheld branch) [CLAIM, BOOTSTRAP s2; confirmed absent by file
  listing].
E4. C3 holdouts: prometheus/cosmos/c3_holdout_D/ (Nestor, seal a56ef7787, treated as EXPOSED) and
  prometheus/cosmos/c3_holdout_D2/ (encrypted hidden_D2.enc, firewall, custody; SEALED/UNREAD/UNSPENT)
  [IMPL that they exist; NOT OPENED].
E5. C4 power simulation: prometheus/cosmos/c4/power_s0.py (84 lines) [IMPL exists; not read in depth].
E6. research_check.py (195 lines): machine checker for research/ files (RESULTS/GRAVEYARD key schema;
  must PASS before research commits) [IMPL from docstring and BOOTSTRAP].
E7. Atlas adapter (owned by Atlas, ATLAS-37): atlas/harvest/cosmos.py (176 lines), atlas/sql/
  012_m1-a5680f90_cosmos_vocab.sql, atlas/tests/test_cosmos.py; ingests
  roles/Cosmos/campaigns/atlas_export_c0 (10 stores) with sha256 verification, fail closed [IMPL].

## 3. Code architecture and dataflow (C0, from code read)

1. A family exposes `space()` (knob lattice), `coords(params, cmap)` (DECLARED coordinates computed from
   the spec, never from running), `units()`, `run(params, mech, seed, E)` returning per-episode reward
   and cost arrays, `deform`, `coord_preserving`, `sham`, `slots`, optional `expected_cost_factor`
   (contract.py) [IMPL].
2. `world.evaluate` runs the three hand-written mechanisms SEL / LOG / LAST on common random numbers and
   calls `phenomenon.certify`: fitness = (reward - cost)/R per episode; margin = mean(SEL) -
   max(mean(LOG), mean(LAST)); PAYS iff margin >= 0.10 (bootstrap SE reported, not used in the verdict)
   [IMPL, phenomenon.py].
3. `pipeline.Chamber.observe` stores one row per world with y = 1[PAYS] and four coordinate maps
   (v1..v4) [IMPL].
4. `miner.Miner` enumerates every expression of size <= 6 over terminals C N K G (+ Q under v3/v4),
   unary log and exp(-x), binary + - * /; collapses expressions with identical rank order on the probe
   rows (13,272 expressions to ~4,400 classes, design/02 D5); fits a 1-D threshold per class maximising
   balanced accuracy; laws are one atom or a conjunction of two atoms (coordinate ascent); scored by
   leave-one-LINEAGE-out BA minus 0.004 x complexity with a worst-fold gate 0.75; the whole search is
   rerun on labels permuted within family (19 perms default, p gate 0.05); outputs NONE when no law
   passes [IMPL, miner.py header and lines 262-307].
5. `pipeline.mine_rows` downgrades CANDIDATE to INSUFFICIENT_INDEPENDENCE if fewer than 3 lineages, where
   lineage = union-find over shared imported modules (independence.py: "detects SHARED CODE. It cannot
   detect shared IDEAS") [IMPL].
6. Adversary (adversary.py): band / coordpres (microscopically different worlds with identical declared
   coordinates) / extreme / errorseek; a contradiction is confirmed only by two fresh 4x-episode
   replicates; kill if confirmed/confident > 5% [IMPL].
7. Location attack (locate.py): for >= 4 confidently-PAYS bases per family, scan the cost knob over
   0.6-1.4 x the law's predicted upper flip (33 points, 1,600 episodes, CRN), fit a logistic location,
   delta = log2(f_obs/f_pred); LOCATION_BIASED if |mean delta| > max(2 SE, 0.05) [IMPL]. Campaign gate
   tolerance was 0.10 log2 (GRAVEYARD header) [CLAIM].
8. Location-aware selection (select.py): among near-top LOLO candidates (within 0.03, up to 6 per map),
   refit, run locate, choose the smallest worst-family |offset| [IMPL].
9. Broker (broker.py) runs sealed families in a subprocess only after receipted predictions; audit.py
   checks receipt chains, freeze hashes, reveal-after-prediction [IMPL from docstrings/HANDOFF].
Code/doc disagreements noted: docs say miner "MAX_SIZE 6"; select.py refits with max_size=3,
conj=False (refit only, not search) - consistent. Design/02 lists `holdout/well.py` as "family D"; the
tree contains spent D/E/F plus two later C3 holdout packages, which the HANDOFF does not mention because
they postdate it. The Atlas registry lists Cosmos code_paths as roles/Cosmos only, omitting
prometheus/cosmos/ (atlas/registry.json engines[11]) [IMPL].

C3 dataflow (prometheus/cosmos/c3) [IMPL]: Task(V=4, k=6, h) emits integer observations (cue at t=0, k
distractors, query at k+1, optional hint). A System implements init/noise/step/readout_features/
full_state. `train_readout` fits a multinomial logistic policy on readout features (the readout is part
of the system). P1 = cross-validated cross-entropy gain in bits from (S_t, O_t) over O_t alone, max of a
generic full-state probe and a readout probe, permutation null within O strata (49 perms), held iff p <=
0.02. P2 = paired episodes sharing distractors and noise, full-state swap at t=k, effect = J_intact -
J_ablated, held iff effect > 3 bootstrap SE. Classes NONE / PASSIVE / FUNCTIONAL / INCOHERENT /
INDETERMINATE.

## 4. Claimed computational primitive vs actual mechanism

E1 CWE C0.
- Label: "substrate-independent phase-boundary invariant" / "cross-substrate law" recovered by "active
  experimentation" in "counterfactual universes".
- Smallest actual mechanism [IMPL]: brute-force enumeration of <= 6-node arithmetic expressions over
  4-5 author-declared scalars, each thresholded once; pick the best one- or two-atom conjunction by
  grouped cross-validated balanced accuracy. A small symbolic-classification search.
- Organisms: SEL/LOG/LAST are three fixed hand-written retention programs per family (e.g. regs.py: SEL
  allocates one register, LOG one per input, LAST none). No learning, no search over organisms.
- What it could express: any 2-atom threshold rule over the declared coordinates; it cannot introduce a
  variable it was not given (missing coordinates had to be added by hand: Q in v3, expected cost in v4).
- Phenomenon the ruler tried to observe: when "selective retention pays" (an economic phase boundary).
- Could the organism perform it: trivially yes by construction; whether SEL pays is set by the author's
  cost and noise formulas.
- Could the ruler tell it from a shortcut: no, in the decisive sense. The zero-parameter rule "G e^-N - C
  >= .10 AND (Q < 1 OR CK/2 >= .10)" written from the certificate economics reaches D .973, E .971, F
  .887 vs law A .983/.972/.930, McNemar p .688/.688/.125 [RESULT-UNVERIFIED as numbers; CORRECTION as
  status; research/RESULTS.md R-0001]. The seat itself had found 97.5% agreement with a hand-derived law
  on the day (41ca2d5b2) [CLAIM].
E3 C3 certificate.
- Label: "causal accessibility of past information"; FUNCTIONAL memory = P1 and P2.
- Smallest mechanism [IMPL]: a logistic-regression decodability test plus a state-swap ablation on paired
  CRN episodes of a one-cue delayed-recall task.
- Planted calibration systems (calib.py) are hand-built: N0 (no memory), PV (passive), FX, FD
  (functional), MC (misleading correlate), NZ (noisy functional) [IMPL].
- Ruler target: whether history is encoded AND causally used.
- Shortcut: the preliminary C3 law's coordinate was built from the same paired-CRN construction as P2,
  so it restated P2; a zero-parameter rule reproduced 104/120 visible classes [RESULT-UNVERIFIED;
  research/reviews/COORD_AUDIT_C3_2026-09-29.md, AUTOPSY_C3_PUBLIC_2026-09-30.md].
- Could the C3 visible systems perform the phenomenon: the substrates are withheld [UNKNOWN]; design/03
  intended a recurrent controller (A), graph dynamics (B) and stigmergic marks (C) with retention NOT
  hand-coded [INTENT]. R-MECH reports the planted suite has no continuous family (F5) [CLAIM].

## 5. Representation/state architecture

C0 [IMPL]: per world, integer/float numpy arrays per episode: regs = E x nreg int64 registers with
per-bit flip noise; ring = packets in flight with hop loss and eviction; ca = binary tape blocks with
optional 3-cell majority repair. No representation is learned; the "law" representation is a symbolic
expression tree (tuples) with thresholds. World identity = hash(family, version, params). Coordinates
are declared floats (C maintenance cost / reward, N corruption events, K distractors, G = 1 - 1/V, Q
capacity).
C3 [IMPL for planted systems]: state dicts of arrays; full_state exports a (E, D) matrix; readout is a
logistic policy. Substrate state architectures withheld [UNKNOWN].

## 6. Organism/player architecture

C0: three reference mechanisms per family, hand-written, no parameters beyond the world's knobs; one
alternative mechanism (regs repetition code, C0m) [IMPL]. No evolution, no training ("C0 is search-free by
charter", design/02). C3: Systems with trained linear readouts; dynamics parameterised (planted systems
hand-coded; substrate systems withheld). C4: no organisms built.

## 7. World/environment architecture (toy scale flagged)

TOY SCALE. One functional demand everywhere: a cue among V <= 16 symbols, K <= 7 distractors, horizon H
<= 40 ticks, reward iff the cue is emitted at the ask (contract.py; regs.py space V {2,4,8,16}, H
{8,16,32}, K {0..7}) [IMPL]. Knob lattices of ~6 dimensions with 3-10 levels each; pools of 1,200 worlds
per family (HANDOFF s4). C3 task: V = 4, k = 6 (gate), ~3,000 test episodes per certificate [IMPL,
gate.py, certify.py]. Every visible and sealed family in C0 was written by Cosmos (one author lineage);
the sealed ones were written "knowing the law's form" (HANDOFF s10) [CLAIM].

## 8. Search/training/adaptation mechanism

- Law search: exhaustive enumeration (no gradient, no evolution) [IMPL].
- World sampling: random / grid / boundary-bisection / kernel-uncertainty "active" / cost lines
  (sampler.py) [IMPL]. Active ~ random (0.790 vs 0.788 at B=30; 0.807 vs 0.831 at B=60); cost lines
  worse than random (.767 vs .946) [RESULT-UNVERIFIED, HANDOFF s7].
- Collapse modes: (a) the grammar re-finds the certificate's economics (T-I1: 11 of 15 atoms of C0-C2
  laws re-express the definition rung beyond a matched null; the robustly killed atoms are the
  non-certificate ones) [RESULT-UNVERIFIED, GRAVEYARD "T-I1 fragment test result"]; (b) LOLO BA is flat
  across near-tied laws whose boundaries differ by 30% in cost (design/02 D17) [CLAIM]; (c) the selected
  law depends on the seed (c2x attribution matrix) [RESULT-UNVERIFIED].

## 9. Measurement/ruler stack

- SELECTIVE_PAYS.v1 margin >= 0.10 (fixed, from WSE contract archaeon/wse/ssf.py) [IMPL].
- Miner gates: LOLO worst-fold BA >= 0.75; whole-search permutation null p <= 0.05; family-dependence mu
  (bits/row gained by per-family refit vs permuted family labels) [IMPL].
- Universality gate: >= 3 code lineages by AST import closure [IMPL].
- Adversary kill rate 5% with replicate confirmation [IMPL].
- Location gate: per-family offset tolerance 0.10 log2 in campaigns (TOL 0.05 in locate.py's own
  verdict) [IMPL + CLAIM].
- Holdout gates: G5 BA on sealed family vs 5-NN and majority; G6/G6b/G6E/G6F intervention prescriptions
  (direction and magnitude along the cost knob) [CLAIM; campaigns/*/PREREG.md].
- Audit: receipt chains, freeze hashes, reveal-after-prediction, with cheat controls (tests/test_audit.py)
  [IMPL].
- C3: P1/P2 certificate v3 gate PASS on 6 planted systems x 5 fresh seeds (c3/runs/
  GATE_v3_PASS_seeds6to10.json); v2 FAILED (NZ INCOHERENT on one seed; GATE_v2_FAIL.json) [IMPL of the
  JSON contents; result itself RESULT-UNVERIFIED].
- Blind spots recorded by the seat: contradiction rule cannot see a boundary shifted inside its own band;
  pooled residuals hid per-family offsets of opposite sign (regs -.147, ca -.105, ring +.142); the G6
  engine assumed one flip; G6/G6b lacked a chance floor (a constant prescription passes magnitude 10/12);
  repeated adversary rounds re-fired identical attacks; the independence audit cannot see shared ideas;
  selection and location gate share a criterion (design/02 D14-D17; HANDOFF s9-10) [CLAIM].

## 10. Baselines and controls

C0 [CLAIM/RESULT-UNVERIFIED]: majority, 5-NN transfer, climatology Brier; planted-truth suite (positive,
interaction, substrate artifact, broken universality, null world, shared-code artifact, location-aware
selection) 7/7; sham twin per family (the ask no longer depends on the cue); coordinate-preserving pairs.
Missing at the time and added 2026-09-29: the ZERO-PARAMETER DEFINITION RUNG, plus replicate noise ceiling
and near-boundary BA (both still NOT MEASURED by Cosmos) [CORRECTION; research/RESULTS.md baseline
ladder]. C3: planted N0/PV/FX/FD/MC/NZ; preregistered baselines were single-coordinate threshold,
constant and 5-NN; the definition rung was NOT preregistered (AUTOPSY s2) [CLAIM]. C4 design adds T0,
T1a/b, T2a/b, T3-DOWN (the shortcut) rungs and two strata (c4/DESIGN_C4.md s3) [INTENT].

## 11. Historical experiment campaigns

C0 (2026-09-23, PREREG 1d4465df9, run 2 at f31339054; result 54ca84228). Q: recover a cross-family
SELECTIVE_PAYS boundary law. Organism: SEL/LOG/LAST. World: regs/ring/ca. Pressure: none (search-free).
Measurement: miner + adversary + sealed D. Result: three laws (v1, v2, v1) all FAILED by adversary
(15.7%, 10.2%, 23.1%; G-0001..3); "no surviving invariant", D still sealed. Run 1 crashed (BrokenProcess
Pool). Paths roles/Cosmos/campaigns/c0/. Label: REPORTED NEGATIVE/NULL.

C0b (PREREG 21fd1b2cc; v3 coordinates adding Q and post-repair N). Law A f852d782cb survived, frozen; D
revealed: BA .983; G6 FAIL 0/12 (engine defect), G6b 12/12 direction (5b84b66e0). Later: ceiling bias
+0.045 (S2b 9/9) explains D/E false positives; definition rung ties it. Label: LATER OVERTURNED (as a
discovery; status RESTRICTED).

C0e (da57b0ac4, 0ed2fced1, 41ca2d5b2). Sealed E (swarm) sealed after law A froze: BA .972; G6E 10/12.
Same-day post-hoc: mined law == task economics, 97.5% agreement. Label: LATER OVERTURNED (as discovery).

C0m (8a49baf16, 618980588). Alternative mechanism (regs repetition code): law holds BA .961 vs .958; M3
lost by .005; repetition code flips 43/300 verdicts. Label: MIXED.

C0s (7ed653563, 14d4a4522, e25a0d7cd, 396917639). Post-freeze stress + ceiling-bias test; S2 LOST by
ladder-resolution defect; S2b bias +0.045 in C (9/9); locate.py introduced; ring "dead memory is free"
coordinate defect (offset tracks N, corr 0.99). Label: INSTRUMENT FAILURE (S2) / REPORTED NEGATIVE for
the frozen law's location.

C1 (e51fc75ae; v4 expected cost, cost-line sampler, location gate). Three laws killed by adversary AND
location (offsets -0.37..-0.55 log2) (G-0004). Run 1 MemoryError. Label: REPORTED NEGATIVE/NULL.

C2 (7b14ec99e, 29600e550, 383fd90b4). Location-aware selection. First law c5cd50beb1 killed by location
alone (regs -0.168, 1.01 SE over tolerance; G-0005); law B a079ad5ec1 survived and frozen; sealed F: A
.930, B .955, discordant 10 vs 10 p 1.0; G6F 11/12. Later: definition rung on F .943 with v4 coords,
McNemar law vs rung p .227. Label: LATER OVERTURNED (as discovery; RESTRICTED).

eta2 (22a38c06a, 643117832). Cost lines vs random, budget matched, 3 seeds: .767 vs .946. Post-holdout.
Label: REPORTED NEGATIVE/NULL.

c2abl / c2x (c2none, c2rep, c1s29, c2none28) (bba06b62a..836515e50). Selection x cost-lines 2x2 on
seeds 28/29/31, one run per cell; 6 of 7 arms survive; on seed 29 selection picked a WORSE initial law
than plain LOLO; "C1 -> C2 improvement was mostly seed"; method attribution UNRESOLVED. Post-holdout, no
sealed test. Label: INCONCLUSIVE.

Reproducibility (12df92a11, d2827fbae, 94a0efa83): c2none and C2 full reruns byte-identical; pinned C0b
replay partial (OOM). Label: REPORTED POSITIVE (determinism only).

C3 Session 1 (2026-09-24..25; prereg roles/Cosmos/c3/S1_PREREG_P1P2_GATE.md written ~07:10Z before code).
Certificate gate v1/v2 FAIL then v3 PASS on fresh seeds (public). Visible-family law search, adversary and
substitution attacks run on withheld branch; preliminary law passed its own gates L1-L5 [CLAIM]. Coordinate
audit 2026-09-29 (2 `claude -p` read-only replicas + Cosmos-executed VERIFY): REJECT; zero-parameter rule
104/120 (40/40, 34/40, 30/40 per family), 12/12 substitution; law vs rule 6:1 discordant in-sample (p
.125), OOS confident stratum 42 = 42; coordinate rank-corr .875 with P2 effect; family recoverable .77 vs
.33 [RESULT-UNVERIFIED]. Holdout D2 never spent. Label: LATER OVERTURNED (killed before holdout;
GRAVEYARD G-0006).

T-I1 fragment archaeology (2026-09-29, d2ede5652; analysis scripts roles/Cosmos/research/analysis/
t_i1_fragments{,_v2,_v3}.py). v1 null gate unreachable (q99 = 1.000) -> v3: 11/15 atoms re-express the
definition rung on 720 spent sealed rows. Exploratory. Label: REPORTED POSITIVE (for the restatement
reading).

C4 (2026-09-30, design only). Interim R-STAT (Ananke, ded6f5729): a family-constant predictor passes S0-A
(a)-(d) in 200/200 sims; per-family CIs uncorrected; no discovery/confirmation split. Interim R-MECH
(Bellerophon, branch 164df3cdd): a guard-compliant SYSID coordinate restates Certificate A (BA .91 vs
T3-DOWN .50); Certificate B agrees with A on 47/48. Label: UNKNOWN (no data campaign).

## 12. Reported results and later corrections (timelines)

T1. Law A. Claim 2026-09-23: survived three sealed universes (D .983, E .972, F .930) -> same-day seat
note 97.5% agreement with hand-derived economics, "planted-invariant recovery, not a discovery"
(HANDOFF s1 V2) -> Artemis R-14 (worker claim; #878): analytic formula ties A and B -> Cosmos recompute
2026-09-29: no significant margin over definition rung on D/E/F -> status PROVISIONAL -> RESTRICTED
(RESULTS R-0001). Current: RESTRICTED, "Nothing was re-scored". [CORRECTION]
T2. Law B. Same path; plus "law B" exists because its predecessor died by a 1.01-SE location margin
(G-0005; under tolerance 0.15 it would have lived) -> RESTRICTED (R-0002). [CORRECTION]
T3. Location. Claim: law A frozen and surviving -> C0s S2b ceiling bias +0.045, then locate.py shows
per-family offsets of opposite sign (regs -.147, ca -.105, ring +.142) that cancel when pooled; ring's
offset tracks N (corr 0.99) = coordinate defect -> location gate added as a kill criterion from C1 (D15);
v4 expected-cost coordinates (D16). Current: location gate retained as the robust effect of the method
arms (c2x). [CORRECTION]
T4. Selection. Claim (C2 commit subject): "location-aware selection yields a surviving v4 law" -> c2abl /
c2x: 6/7 arms survive without it; selection picked a worse law on seed 29 -> UNRESOLVED; "selection and
gate share a criterion" (HANDOFF s10). Current: not shown necessary. [CORRECTION]
T5. Intervention G6. Claim: G6b PASS 12/12 magnitude -> post-hoc: a constant prescription also passes
10/12; precision vs best constant becomes the evidence (gate added from G6E). [CORRECTION]
T6. C3 law. Passed own gates -> audit REJECT -> autopsy -> operator CLOSED / KILLED; must not be revived
(G-0006). [CORRECTION]
T7. C3 certificate. v1 fixed 0.05-bit P1 floor vs 3-SE P2 gave NZ INCOHERENT; v2 MC passed on a 4-decimal
tie; v3 max-statistic P1 incl. readout probe, 3,000 episodes -> PASS on fresh seeds 6-10 (seeds 1-5
informed the amendment) [CLAIM]. Artemis R-10 (worker claim, via Atlas digest): at V=2, k=8 NZ is
FUNCTIONAL only 3/5; fixed swap at t=k insufficient for periodic-update engines [CLAIM, not verified
here].
T8. Counts. Hour-4 status said 10 laws / 8 failed; ledger says 9 / 7 ("the ledger wins") [CORRECTION,
HANDOFF s5].

## 13. False-positive archaeology

- Restatement of the label: twice (C0 economics; C3 P2 machinery). Cause: the coordinates and the
  certificate share author and, in C3, code paths (paired-noise construction and swap time). Lesson L1-L7
  (AUTOPSY s3) bind C4.
- Sealed transfer as false evidence: all six C0 families written by one author with the same task
  economy; "independence" = code-level only (independence.py docstring).
- Family fingerprinting: C3 coordinate set predicts family at .77 (chance .33); one family identified
  40/40 by a bitwise identity between two coordinates; export choices (readout size, encoding, noise
  lattice) act as free parameters (L7).
- Preregistered expectation equals construction output (L6): the winning C3 rule was preregistered as
  expected (credence .5); all 12 top candidates share one coordinate.
- Pooled-metric masking: pooled location offset hid opposite-signed family offsets.
- Gate without a chance floor: constant prescription passes G6b magnitude 10/12.
- Tolerance-decided survival: G-0005 / law B succession at 1.01 SE.

## 14. Likely false-negative regimes

- Laws needing a variable outside the declared coordinate vocabulary are unreachable: the miner cannot
  invent coordinates (missing capacity/repair/expected-cost were found only by attack and hand-added).
- C3's P2 swaps the state at exactly t = k; per Artemis R-10, periodic-update or delayed-readout engines
  can be misclassified; P1 probed at k+1 cannot localise memory [CLAIM].
- Expression size <= 6 and at most 2 atoms; anything needing more structure returns NONE.
- C4 S2(c) alone would fail a truly universal law ~40% of the time (R-STAT A4) [CLAIM].
- Families are discrete-symbol toy channels; continuous-noise families make T3-DOWN register 60/60
  (R-MECH F4), so the shortcut rung itself breaks there [CLAIM].

## 15. Phase 3 audit (per engine)

E1 CWE C0 (law miner + three families)
a. Representation richness: hierarchy NO (flat 2-atom conjunction); compositional structure PARTIAL
   (expression trees of <= 6 nodes, no reuse across laws); variable binding NO; memory NO in the miner
   (substrates hold a cue in a register/packet/tape, hand-coded); recurrence NO; counterfactual state
   PARTIAL (CRN-paired worlds, sham twins, coordinate-preserving transforms); latent variables NO
   (coordinates declared, never inferred); temporal abstraction NO; spatial abstraction NO; reusable
   substructure PARTIAL (rank-order quotient of expressions); dynamic routing NO; self-reference NO.
b. Reasoning opportunity: none beyond fixed heuristics. The organisms are three fixed retention
   programs; the world is a one-cue delayed recall with an economic cost; the "reasoning" is the miner
   fitting a threshold.
c. Shortcut surface: the certificate's own economics written in the declared coordinates (definition
   rung) matches every surviving law; family identity via coordinate lattice points; tolerance choice.
d. Ruler resolving power: high for determinism and leakage hygiene (receipts, seals, byte-identical
   reruns, cheat-controlled audit); location attack resolves ~0.035 log2; cannot separate "law" from
   "definition restated" without the definition rung, which arrived 6 days late.
e. Scale: 4-5 coordinates; V <= 16, K <= 7, H <= 40; 3 visible + 3 sealed families; 1,200-world pools
   per family; 400-1,600 episodes per world; ~4.6k graph nodes; one CPU box, ~6.5 h.
E3 C3 certificate (+ withheld substrates)
a. hierarchy NO; compositional NO; variable binding NO; memory YES as the measured property (decodable
   cue in state); recurrence PARTIAL (system step functions; planted ones hand-coded); counterfactual
   state YES (full-state interchange on paired CRN episodes); latent variables PARTIAL (probe decodes
   hidden cue); temporal abstraction NO (single delay k); spatial NO; reusable substructure NO; dynamic
   routing NO; self-reference NO.
b. Reasoning opportunity: delayed recall of one of V=4 symbols over k=6 distractors (memorisation /
   simple FSM). Nothing more is demanded.
c. Shortcut surface: coordinates built from P2's paired-noise machinery restate P2; perturbation size
   ("distance") passes for information (L5); export choices fingerprint family (L7).
d. Ruler resolving power: separates 6 planted classes 5/5 on fresh seeds at V=4, k=6; reported weaker at
   V=2, k=8 (worker claim).
e. Scale: 120 visible worlds (40 per family x 3), 12 substitution, 90 adversary worlds; 2,000 train /
   3,000 test episodes per certificate; 49 permutations.
E5 C4 (design only): no implementation to audit; R-STAT and R-MECH interim findings say the v0.2 gates can
   be passed by a family-constant predictor or a remeasurement [CLAIM].

## 16. Research reports and substantial documents

- roles/Cosmos/prompts/2026-09-23_charter/00_DIRECTIVE_verbatim.md - the CWE charter.
- roles/Cosmos/design/00_source_verbatim_2026-09-23.md - operator source material verbatim.
- roles/Cosmos/design/01_engine_design_2026-09-23.md - WGE/CWE design (4,983 words).
- roles/Cosmos/design/02_cwe_as_built_2026-09-23.md - as-built components and decisions D1-D19.
- roles/Cosmos/design/03_c3_design_draft_2026-09-23.md - C3 design: P1/P2, firewall, holdout ration.
- roles/Cosmos/campaigns/HANDOFF_2026-09-23.md - full C0-C2 handoff, three verdicts, law ledger.
- roles/Cosmos/campaigns/REVIEW_PACKET_CWE_2026-09-23.txt - external review packet for C0-C2.
- roles/Cosmos/campaigns/REVIEW_PACKET_COSMOS_D_SEAL_2026-09-26.txt - D seal packet (not read in full).
- roles/Cosmos/campaigns/*/PREREG.md - per-campaign preregistrations with appended results.
- roles/Cosmos/campaigns/AUDIT_2026-09-23T1630Z.txt - audit of 9 stores.
- roles/Cosmos/c3/S1_PREREG_P1P2_GATE.md - C3 certificate prereg and amendments.
- roles/Cosmos/c3/D_CONTRACT.md, INFO_LEDGER.md, PUBLICATION_PLAN.md - holdout contract, info ledger,
  withheld-branch publication plan.
- roles/Cosmos/research/{README,THREADS,RESULTS,GRAVEYARD,FREEZES,PRE_RESULT_REVIEW}.md - law-foundry
  workspace; four-layer results; killed-law ledger.
- roles/Cosmos/research/reviews/COORD_AUDIT_C3_2026-09-29.md - REJECT record.
- roles/Cosmos/research/reviews/AUTOPSY_C3_PUBLIC_2026-09-30.md - public autopsy, lessons L1-L7.
- roles/Cosmos/research/reviews/REVIEW_PACKET_C3AUTOPSY_C4DESIGN_2026-09-30.txt - packet (not read).
- roles/Cosmos/c4/DESIGN_C4.md, S0_TRIVIAL_RULES.md, VISIBLE_FAMILY_CONTRACT.md, REVIEW_BRIEF_v0.2.md,
  POWER_S0_v0.2.json, reviews/R-STAT_Ananke_2026-09-30_INTERIM.md - C4 design and review.
- roles/Cosmos/reports/STATUS_2026-10-01.md - current status and critical path.

## 17. Journals/TODOs/backlogs/pivots/abandoned branches

- Journals 2026-09-23, -25, -28, -30, -10-01 (roles/Cosmos/journal/).
- BACKLOG_H0H5.md, WORK_STATE.json, MIGRATION_REPORT_MWO-0002.json, calibration/LEDGER.md.
- THREADS: T-C3 (closed), T-C4, T-A1 open-vocabulary mining, T-A2 theory-free observables, T-B1
  transplant, T-C1 re-encodings, T-D1 minimal failing intervention, T-E1 compression, T-F1 discriminating
  worlds, T-G1 generator independence, T-H1 mechanism, T-I1 archaeology. Under CWO-B the non-C4 threads
  are not started without assignment [CLAIM].
- Local-only branches (not on origin): cosmos/c3-s1-2026-09-24 (e73e5eb26), cosmos/c3-autopsy-2026-09-30
  (c9f8aff17) [CLAIM]. Public branch cosmos/c3-public-2026-09-24 has zero commits ahead of main (Atlas
  digest) [CLAIM].
- superseded/RESPONSIBILITIES_precharter_2026-09-23.md.

## 18. Dependencies on other engines and seats

- Archaeon WSE: SELECTIVE_PAYS margin 0.10 and SEL/LOG/TRIVIAL analogy (archaeon/wse/ssf.py cited in
  phenomenon.py) [IMPL].
- Aphrodite: denotational quotient idea (miner D5) [CLAIM]. BEE: snapshot/interchange idea for P2 [CLAIM].
- No code import of BEE/WSE/NPE (clean-room, D1) [IMPL: substrates import only numpy + contract].
- Nestor (D, D2 custody), Harmonia, Artemis, Ananke, Bellerophon, Theseus, Atlas, Aporia (see s1).
- Fabric/ubu001 hosted some Cosmos Tasks that failed 2026-09-29 on a full disk (roles/Aether/DEFECTS.md)
  [CLAIM].

## 19. Scaling limitations

- Coordinates are hand-declared per family; adding a family means writing its coordinate formulas, which
  is exactly where the definitional leakage enters.
- Exhaustive grammar search is exponential in MAX_SIZE; the whole-search permutation null multiplies it
  by n_perm; worker pools OOM'd twice on one box.
- One author, one task economy; generator independence is the binding constraint (T-G1; C4's foreign
  family is the first attempt to break it and has not been written).
- Holdouts are consumable: D, E, F all spent in one day; C3's D exposed; only D2 remains.

## 20. Lens potential for Phase 3 (descriptive)

- Substrate: tiny numpy channels with explicit cost/noise physics (C0); state-exporting systems with
  swap/restore (C3 contract).
- Organisms: fixed reference mechanisms; trained linear readouts in C3.
- Worlds: one delayed-recall task family; parameter lattices.
- Pressures: none (search-free); the "pressure" is the economic phase boundary itself.
- Phenomenon family: retention/usable-history phase boundaries.
- Current resolving mechanism: grouped CV threshold search + adversary + location attack + sealed
  holdouts + receipts; P1/P2 certificate.
- Likely resolution ceiling: the definition rung; laws over author-built coordinates cannot exceed what
  the certificate defines.
- Noise sources: episode sampling (400-1,600), seed variation in selection, tolerance choice, export
  encoding.
- Architectural limit: declared-coordinate vocabulary; single author.
- Reusable parts: receipt/seal/broker/audit machinery with cheat controls; location attack; whole-search
  permutation null; LOLO-by-lineage; four-layer RESULTS and GRAVEYARD discipline; lessons L1-L7; the
  P1/P2 certificate and its planted calibration suite.
- Toy-grade parts: the three C0 families, the SELECTIVE_PAYS economy, kernel active sampler, cost lines.
- Unknowns: the C3 visible substrates and law (withheld); whether a foreign family changes anything.

## 21. Open questions / coverage gaps

- NOT read: design/01 in full (4,983 words; headings only via design/02), design/00, per-campaign
  PREREG bodies beyond c2x and result lines, adversary.json / receipts / atlas_export JSONL contents,
  REVIEW_PACKET_COSMOS_D_SEAL and REVIEW_PACKET_C3AUTOPSY_C4DESIGN, research/THREADS bodies, FREEZES,
  PRE_RESULT_REVIEW, calibration/LEDGER.md (taken via Atlas digest), journals except 09-25, c4/power_s0.py,
  stress.py, eta2.py, c0e.py, c0m.py, c1f.py, broker.py, audit.py, store.py bodies, ring.py and ca.py
  bodies (docstrings only), planted/*.py, tests.
- NOT opened by rule: prometheus/cosmos/holdout/ (spent D/E/F), prometheus/cosmos/c3_holdout_D/,
  prometheus/cosmos/c3_holdout_D2/. Their existence was recorded from `git ls-files` only.
- Unreachable: the C3 withheld branches (local to M2); the C3 visible substrates, coordinates and law
  are therefore UNKNOWN to this crawl.
- Artemis R-10 / R-14 were taken from Cosmos and Atlas citations, not read at source.
- No code was executed by this crawl.
- Atlas registry omits prometheus/cosmos/ from Cosmos code_paths; the Atlas ECOSYSTEMS catalog "cosmos"
  entry is an unrelated external Tierra derivative (University of Edinburgh) - a name collision.
