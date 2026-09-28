# Raid B -- memory in matter, amorphous computing, major transitions,
# proofreading, program semantics

Currency: 2026-09-28. Odysseus expeditionary worker (disposable). Pure ASCII.
Directive: roles/Odysseus/prompts/2026-09-28_expeditionary/ s1, s10, s11.
Format per candidate: foreign idea -> stripped mechanism -> minimal world ->
falsifier -> transplant candidate. Not a literature review.
Executed kill test: toy_mtm/ (PREREG.md, mtm.py, posthoc.py, results.json,
posthoc.json, RESULT.md). EXPLORATORY.

## 0. Prior-art sweep (done BEFORE the novelty claims)

Local grep over roles/Odysseus (incl. raw/E1..E6, I1..I6, spikes),
aporia/docs/frontier_campaign_69/, roles/Atlas/catalog/, plus a single-pass
`git grep -o -i` over every origin/* ref and local head restricted to
*.md *.txt *.py (result appended in section 7). Hits that decide fate:
- hypercycle / spatial parasites: raw/E2 item 8 + line 306; dossier 31
  (artificial chemistry, Stringmol, AlChemy). -> ALREADY KNOWN INTERNALLY.
- kinetic proofreading, "order through speed" (Ravasio ... Murugan 2024):
  raw/E2 item 18 + line 316. -> ALREADY KNOWN INTERNALLY.
- fraternal / egalitarian transitions (Moreno & Ofria): raw/E1 566-686, incl.
  the open question "can an egalitarian transition happen". -> ALREADY
  KNOWN INTERNALLY (question); the stochastic-corrector WORLD below is new.
- reaction-diffusion / Turing: raw/E2, dossiers 76, 83. -> ALREADY KNOWN.
- natural induction, coupled learning, temporal contrast, directed aging
  family: raw/E5 L5-L7, NEWLENS L2, spike S6. -> ALREADY KNOWN.
- Zeravcic appears once (raw/E5-18, multifarious assembly), not for memory.
- Self-inspection (Laing), von Neumann Mech. 1, Kleene/quines: HELD by
  Nestor (NPE-P2 and NPE-arc3 external reviews; section 7). -> KEPT-4's
  classification is ALREADY KNOWN INTERNALLY.
- NO internal hit (all origin/* refs, *.md) for: return-point memory,
  multiple transient memories, Keim/Paulsen (Nagel hits are unrelated
  names), Mullins, hysteron, Preisach, stochastic corrector, Futamura,
  growing point. "Partial evaluation" and "reflective tower" occur only as
  generic phrases in generated reports (no mechanism transplant).

## 1. Candidates (12 examined; 5 kept, 7 killed or already held)

### KEPT-1. Multiple transient memories: memory written at the margin of a drive

SOURCE PHENOMENON. Cyclically sheared non-Brownian suspensions (and
charge-density-wave conductors, glasses, jammed packings) trained with
several shear amplitudes store ALL of them for a while; continued driving
with the same inputs erases all but the largest; adding noise keeps all of
them indefinitely. No learning rule, no organism. Keim & Nagel PRL 107,
010603 (2011) VERIFIED; Paulsen, Keim & Nagel PRE 88, 032306 (2013)
VERIFIED (readout protocol and parameters read from arXiv html 1307.1184);
Keim, Paulsen, Zeravcic, Sastry & Nagel "Memory formation in matter" RMP 91,
035002 (2019) VERIFIED; Lindeman & Nagel Sci Adv 7, eabg7133 (2021)
VERIFIED (interactions between rearranging clusters needed for multiple
memories in jammed packings); "Dissipation indicates memory formation in
driven disordered systems" arXiv 2209.00572 VERIFIED existence;
"Memories of amplitude and direction coexist and compete in non-Brownian
suspensions" arXiv 2510.11825 VERIFIED existence (2025 extension).

MECHANISM (stripped; SHARPENED by the toy -- see toy_mtm/RESULT.md).
(a) units that are activated when a drive amplitude exceeds a unit-local
margin; (b) activated units are perturbed and re-settle; (c) the quiet sets
are NESTED in amplitude (quiet at a2 => quiet at a1 < a2); (d) the
perturbation is SMALL relative to the margin (source: eps = 0.005 d), so a
disturbed unit re-settles near the amplitude that disturbed it (depletion
just below each trained amplitude, pile-up just above). (a)-(c) with any
kick size write the LARGEST amplitude (toy: robust, 4 rules x 2 kick sizes x
5 seeds). The SMALLER memories were never written in the toy, even with
small kicks on a Q = 64 lattice; the particle version did not converge in
budget. Working hypothesis: the smaller memory is a second-order
rate-asymmetry imprint (units below g1 are disturbed twice as often) that
needs fine-grained margins and a long sub-critical transient. (c) is what
makes "forget all but the largest" automatic.

PROMETHEUS TRANSLATION.
 World: any lattice executable-matter world (Aether-class) with a scalar
 drive knob that can be cycled (field amplitude, energy injection per
 cycle, perturbation radius). Unit: a lattice site/cluster (no organism).
 Pressure: none -- only the drive. Observable: the ACTIVITY-VS-READOUT-
 AMPLITUDE curve C(a) (fraction of sites that would change in one trial
 cycle of amplitude a from the current state) and its second difference;
 a memory is a peak of C'' at a trained amplitude. Equivalent label-free
 readout: dissipation per trial cycle (2209.00572) -- needs no decoding of
 the state, only the world's own energy bookkeeping.

KILL TEST (executed; toy_mtm). Superficial if (i) a Prometheus-like lattice
rule with the same nested-threshold structure fails to show the signature,
or (ii) the signature needs only "any absorbing-state rule", i.e. adds
nothing beyond "the world has fixed points". Outcome: see section 3.

ALIEN CONTENT. (1) A memory whose CONTENT is a property of the drive, not of
any unit, stored in the distribution of margins across the population, and
readable only by re-driving (protocol-dependent readout). Prometheus has
records, tapes and couplings; it has no concept of a MARGIN DISTRIBUTION as
a storage medium. (2) Capacity set by noise (in the source, noise is what keeps plasticity),
the opposite of the usual Prometheus stance that noise erodes content --
NOT reproduced in the toy, where noise eroded the one memory formed.
(3) Forgetting as a consequence of a partial order (nesting), not of decay
or capacity.

Territory: F (memory with no installed rule) and B (can the substrate carry
structure: here, several numbers at once), touching D rung R0 (persistence
of a history-specific object; ACCUMULATION_v0 s3) and E (a readout that is
the world's own dissipation). Vocabulary failure: "memory" in Prometheus
means a stored copy or a coupling change; there is no word for
margin-stored, protocol-read memory. The nearest familiar explanation is
"the world has attractors and training picks one" (single-attractor
selection); the distinguishing experiment is the two-amplitude protocol:
single-attractor selection cannot hold g1 and g2 simultaneously, MTM holds
both transiently and, with noise, indefinitely.

NOVELTY AUDIT. New observable, not renamed fitness (no fitness exists).
Not a learning mechanism and not parameter adaptation: nothing improves;
it is recordability. Substrate physics, not an encoded algorithm -- BUT the
toy shows that two properties of the rule (nesting, small perturbation)
decide it, so in a designed world it is a design choice that must be
declared. Not a delayed consequence of initialisation: the RAND (t=0) control has no
peak; the peak sits at whatever amplitude was trained.

FATE: PRODUCED NEW INSTRUMENT (the C(a) trial-cycle readout: a label-free,
history-specific memory assay that works on any lattice with a cyclable
drive knob; validated in the toy for the max-amplitude memory with RAND and
SINGLE controls). The MULTIPLE-memory claim for Prometheus-class discrete
lattices is UNRESOLVED (toy did not replicate the source; K1). Transplant:
run C(a) on one Aether/PTE-class lattice after the nesting audit (KEPT-2);
if it reads a max-register only, record that as the default for discrete
worlds and test fine-margin variants.

### KEPT-2. Return-point memory and hysteron transition graphs: the world as a
### finite-state machine of its own drive history

SOURCE PHENOMENON. Systems with return-point memory (ferromagnets, Preisach
models, amorphous solids under athermal quasistatic driving) return to the
exact microstate when a drive loop is closed; the memory is a LIFO stack of
turning points. Interacting hysterons ("material bits") make driven
materials that count cycles, parse strings, and reach a target state only
for a specific drive sequence ("lock and key"). Mungan & Terzi, Ann. Henri
Poincare 20, 2819 (2019) VERIFIED; Terzi & Mungan PRE 102, 012122 (2020)
VERIFIED; Kwakernaak & van Hecke PRL 130, 268204 (2023) VERIFIED; serially
coupled hysterons PNAS (2024, doi 10.1073/pnas.2308414121) VERIFIED existence;
Sethna et al. PRL 70, 3347 (1993) UNVERIFIED (classic RPM/no-passing source).

MECHANISM. Bistable units with a lower and upper switching field; the
"no-passing" (monotonicity) property makes loops nest and gives RPM;
interactions between units break RPM in controlled ways and create
non-trivial transition graphs (the material's automaton). Computation =
the graph's response to a drive word.

PROMETHEUS TRANSLATION. World: any Prometheus lattice rule with a scalar
drive knob stepped quasistatically (relax to a fixed point after each step).
Unit: the whole world state. Observable: the AQS transition graph
(states x {up, down}) sampled from random initial states: fraction of loops
that close (RPM), number of distinct absorbing states, and the length of the
longest drive-word the graph distinguishes. This is a NESTING / NO-PASSING
AUDIT of a rule: it predicts whether the rule can hold MTM-type memories
(KEPT-1 needs nesting) and whether its memory is a stack (RPM) or a general
automaton (interacting hysterons).

KILL TEST. If the audit is uninformative -- the graph is either trivial
(one absorbing state) or a random graph with no loop closure in every
Prometheus lattice rule -- the import adds nothing; the rule has no
drive-history structure to exploit. Distinguishing experiment vs nearest
familiar explanation ("the rule is just a dynamical system with
attractors"): loop closure fraction vs a matched random automaton with the
same number of states and out-degree.

ALIEN CONTENT. Memory and computation as a property of a rule's order
structure under a drive (monotonicity), measurable without any organism,
record, or readout designed by the experimenter. Gives Prometheus a
"what can this physics remember about how it was pushed" number for free.

Territory: B and C (what the physics makes reachable/storable); a candidate
for a new sub-coordinate, see section 5. FATE: PRODUCED NEW INSTRUMENT
(design; not run). Novelty audit: substrate physics (not an encoded
algorithm) iff the drive knob is a physical parameter of the world and not
a message channel; declare the knob.

### KEPT-3. Stochastic corrector: variance from reassortment as the selector
### of a higher-level unit

SOURCE PHENOMENON. Small compartments hold a few replicators of two kinds
(a fast "selfish" one and a slow one that helps the compartment); the
compartment grows and divides with RANDOM reassortment. Small numbers make
compartment compositions vary; compartments with better compositions divide
more; within-compartment selection for the fast type is countered by
between-compartment selection. Coexistence without any heritable compartment
structure. Later, linkage (a "chromosome" fusing the two genes) is favoured.
Szathmary & Demeter J Theor Biol 128, 463 (1987) VERIFIED existence (via
search: title "Group selection of early replicators and the origin of
life"); Grey, Hutson & Szathmary Proc R Soc B 262, 29 (1995) VERIFIED;
Matsumura et al. "Transient compartmentalization of RNA replicators prevents
extinction due to parasites" Science (2016) VERIFIED; Takeuchi & Hogeweg PLoS
Comput Biol (2009) direct comparison of compartments vs spatial
self-organisation VERIFIED; Cooney/Mori/Levin origin-of-chromosomes via
multilevel selection (Bull Math Biol 2022, PLoS Genet 2020) VERIFIED
existence; "The first major transition: origin of life from a multilevel
selection perspective" arXiv 2608.22348 (2026) VERIFIED existence only.

MECHANISM. (a) Few copies per group (so sampling variance at division is
large); (b) group reproduction rate depends on composition; (c) within-group
competition favours the selfish type; (d) random reassortment at group
division. No boundary heredity needed, and no group-level genome.

PROMETHEUS TRANSLATION. World: a Z80/BEE-class tape soup partitioned into
M compartments of capacity K (K ~ 4-16 tapes); a compartment splits in two
when full, tapes assigned at random; one compartment (random or oldest) is
deleted to hold M fixed. Periodic global mixing variant = transient
compartmentalisation. Unit: the tape (lower level) and the compartment
(upper). Pressure: no task; a compartment's split rate is simply the
occupancy rate its tapes achieve (so copiers matter), and PARASITES (tapes
that get copied by others but do not copy) arise naturally in BEE/WSE
soups. Observable: does a PAIR of mutually dependent tape types (e.g. a
copier and a tape that only boosts the copier's success) persist, and does
physical LINKAGE (the two fused on one tape, or a joint copy event) arise --
an egalitarian transition (raw/E1 open question) measured, not asserted.

KILL TEST. (i) Same world with compartments replaced by pure spatial
locality at matched mixing (Takeuchi-Hogeweg arm): if persistence and
linkage are the same, compartments add nothing -- the import is the
already-known spatial-parasite story. (ii) K sweep: the corrector predicts a
sharp loss of the effect as K grows (variance ~ 1/K); no K dependence =>
not a stochastic corrector. (iii) Deterministic (non-random, composition-
preserving) division must abolish the effect.

ALIEN CONTENT. Group selection whose variance source is SAMPLING NOISE at
division, not heritable group traits; it predicts that making the world
noisier at the group level (small K) enables composition. Prometheus has
lattices and soups but no small-number group level. Novelty audit: the
compartment boundary is INSTALLED -- this is a designed group, so any
positive result is "what installed groups enable", and the non-installed
follow-up is whether soups produce their own small-number groups (clusters,
co-located tape families). Territory D (building a higher unit from lower
ones) and A (what is a one: the compartment vs the tape). FATE: PRODUCED
NEW WORLD (design; not run).

### KEPT-4. Self-inspection vs self-description: is there a passive genome?

SOURCE PHENOMENON. Von Neumann's constructor copies a DESCRIPTION that it
also interprets (dual use: translated and transcribed); Laing (J Theor Biol
1977, "Automaton models of reproduction by self-inspection", VERIFIED
existence) showed the alternative: a machine that reads its own body and
builds a copy (description made on the fly). Kleene's second recursion
theorem / quines are the program-semantics form: a fixed point that
reproduces its own text. The major-transitions literature ties the
genotype/phenotype split (a passive description) to unlimited heredity
(Szathmary; UNVERIFIED for exact wording).

MECHANISM. Two causally different replication architectures: (SI) copy
source = the executing code itself; (SD) copy source = a region that is
copied but NOT executed by the copier, and the executing machinery is (re)
built from or conditioned by that region.

PROMETHEUS TRANSLATION. World: existing Z80/BEE/WSE soups (no new world).
Unit: tape. Observable: byte-level taint over a replication event: fraction
of copied bytes that are also executed (SI) vs copied-and-never-executed
(passive payload) vs executed-and-not-copied. A "passive payload fraction"
per lineage over time. Links directly to POI-093 decorative load (non-load-
bearing parts): decorative bytes are exactly passive payload; the question
is whether any lineage ever makes passive payload LOAD-BEARING later
(a passive region that some descendant starts to execute or condition on).

KILL TEST. If every competent copier in every soup is SI with passive
payload that is never later consumed (no lineage ever converts payload into
used code), the SD distinction is empty in Prometheus worlds and the import
is analogy. If it occurs, the distinguishing experiment vs the nearest
familiar explanation ("random neutral bytes that later mutate into code") is
a provenance test: the later-used region's content descends from the
ancestor's passive payload (taint) AND scrambling it in the ancestor removes
the descendant's gain (ACCUMULATION_v0 R3 content test).

PRIOR ART INSIDE (found by the all-ref grep): Nestor's NPE-P2 external
review (origin/HEAD roles/Nestor/campaigns/npe-p2-endogenous-heredity-
2026-09-27/delegates/EXTERNAL_RESEARCH.md, Q8 and s1.8) already classifies
NPE copying as self-inspection ("von Neumann Mech. 1") and notes that a byte
the donor never reads cannot be inherited; it also cites Kleene/quines. The
SI/SD CLASSIFICATION is therefore ALREADY KNOWN INTERNALLY. What is not held
there: the passive-payload fraction as a per-lineage time series and the
payload-becomes-load-bearing provenance test below.

ALIEN CONTENT. A heredity observable that separates "what is copied" from
"what copies", i.e. the first precondition for a genotype that can carry
content the current phenotype does not use -- the storage side of
accumulation. Prometheus has "self-copier" and "copy ops" (S1) but no
passive-region concept. Territory A and D. FATE: ALREADY KNOWN INTERNALLY (classification) +
PRODUCED NEW INSTRUMENT (payload time series + provenance test; design;
cheap: S1's probe already classifies copy sources).

### KEPT-5. Mullins/aging as the degenerate case -- the max-register control

SOURCE PHENOMENON. Filled rubber softens after first loading and remembers
only the MAXIMUM strain ever applied (Mullins effect; Diani, Fayolle &
Gilormini, Eur Polym J 2009 review VERIFIED existence). Glasses age and
rejuvenate; spin glasses show hierarchical temperature-step memory
(UNVERIFIED specifics).

MECHANISM. A monotone irreversible variable (damage, broken filler links)
= a max-register of the drive. It is exactly the long-time noise-free limit
of KEPT-1 (only the largest amplitude survives).

PROMETHEUS TRANSLATION. Not a separate world: it is a CONTROL for any memory
claim. A "memory" that a max-register of the drive explains (monotone damage
or monotone depletion of hot sites) is not structured storage. Every
Prometheus persistence claim (ACCUMULATION_v0 R0) should report the
max-register baseline: does the object's content equal a monotone function
of the largest perturbation seen?

KILL TEST. If Prometheus persistence results are never explained by a
max-register (checked on one R0 candidate), the control is inert.
FATE: PRODUCED NEW CONTROL.

## 2. Killed as analogy / already held (with reasons)

- Reflective towers (Smith 3-Lisp; Black; "Collapsing towers of
  interpreters" POPL 2018 UNVERIFIED). KILLED AS ANALOGY: every level
  requires an installed meta-circular interpreter; there is no substrate
  physics that produces "a level" without the experimenter providing the
  interpreter. Nearest Prometheus content (self-modifying tapes) is already
  covered without the tower.
- Futamura projections / partial evaluation (Futamura 1971 UNVERIFIED).
  KILLED AS ANALOGY as a mechanism (no soup specialises programs unless a
  specialiser is installed). Its only transplant -- "specialisation buys
  speed, never reach" -- is ACCUMULATION_v0's recompute arm (speed vs
  ceiling), ALREADY KNOWN INTERNALLY.
- Amorphous computing / growing-point language (Abelson et al. CACM 43(5)
  2000 VERIFIED; Coore 1999 thesis UNVERIFIED). KILLED AS ANALOGY for
  "grown not designed": every particle runs the same COMPILED designed
  program; GPL is a compiler for patterns. Residue (hop-count gradients as
  self-made coordinates) is PRIOR ART ONLY.
- Turing patterns / reaction-diffusion. ALREADY KNOWN INTERNALLY (raw/E2,
  dossiers 76, 83); no new mechanism beyond symmetry breaking.
- Hypercycles and parasites; spatial rescue (Boerlijst & Hogeweg).
  ALREADY KNOWN INTERNALLY (raw/E2 #8, dossier 31).
- Kinetic proofreading / order through speed. ALREADY KNOWN INTERNALLY
  (raw/E2 #18: proofreading arising from selection for speed). Nothing
  added by re-importing Hopfield 1974.
- Error-correcting codes in biology (genetic-code error minimisation,
  Freeland & Hurst 1998 UNVERIFIED). KILLED AS ANALOGY: in Prometheus the
  opcode map is installed; "is it error-minimising" is a property of the
  designer's table, not of evolution in the world. The evolvable part
  (neutral redundancy) is territory C, ALREADY KNOWN INTERNALLY (R4_A-001).
- Directed aging / "nature's greed" (Pashine, Hexner, Liu & Nagel, Sci Adv
  2019; arXiv 1903.05776 VERIFIED) and "emergent learning as feedback-based
  aging" (arXiv 2309.04382 VERIFIED existence). ALREADY KNOWN INTERNALLY:
  same class as natural induction / coupled learning (raw/E5 L5-L7, S6).
- Egalitarian vs fraternal transitions (as a question). ALREADY KNOWN
  INTERNALLY (raw/E1); KEPT-3 is the new executable world for it.

## 3. The executed kill test (toy_mtm; details in toy_mtm/RESULT.md)

Question: can a driven, dissipative substrate with no learning rule store
several input amplitudes at once and forget all but one (the MTM
signature), and does a Prometheus-like lattice rule show it?
Worlds: W1 particles under cyclic shear (Corte/Keim-Nagel random
organisation); W2 lattice (Z_64 phases, site active if a neighbour is
within a, active sites redraw); W3 = W2 + activity leaking to quiet
neighbours (no organism boundary); W4 non-nested band rule (anti-analogy).
Readout: C(a) = fraction of units that would be disturbed by one trial
cycle of amplitude a; memory = kink (C'' peak) at a trained amplitude.

PREREGISTERED RESULT: MTM NOT REPRODUCED in any world. P1 (both memories
mid-training) and P3 (both kept under noise) FAIL everywhere; decision rule
K1 fires (toy did not replicate the source; no inference about Prometheus
by the prereg rules). The largest-amplitude memory (g2) forms everywhere,
sharply, only when trained, never in the random state (P4, P5 pass).
W3 (leaking activity) never fully absorbs and holds only a weak g2 memory
(kink 0.03 vs 0.13): spreading dissipation degrades margin memory.
POST-HOC (labelled): 100x/10x smaller kicks double the sharpness of the g2
memory on the lattice but still never write g1; the particle version stays
dominated by unresolved overlaps at 4096 cycles (underpowered; the source
used ~1e4 cycles, eps = 0.005). W4's bands tiled [0, g2) after pilot
rescaling, so the nesting hypothesis H_nest was not tested.

WHAT THIS KILLS / KEEPS. Killed: the easy reading "any absorbing-state
lattice rule has multiple transient memories" -- in coarse discrete rules
only the maximum drive is written (a Mullins-type max-register). Kept: the
readout itself (C(a)) is a working label-free memory assay for Prometheus
lattices. Open: whether fine-grained margins (Q >> amplitudes, long
sub-critical transients) restore the smaller memories; that is the next
test and it decides whether MTM transplants to Prometheus at all.

## 4. Best three transplants

1. Trial-cycle memory assay C(a) + nesting/no-passing audit (KEPT-1 +
   KEPT-2): drive any lattice world with a cyclable knob, read what it
   remembers of its own drive history with no decoder -- territory B/F/E;
   instrument, cheap, first data from the toy (max-register validated).
2. Stochastic-corrector soup (KEPT-3): Z80/BEE tapes in small compartments
   with random reassortment at division, vs a matched spatial-only arm and a
   K sweep; asks whether sampling variance builds a higher unit and
   linkage -- territory D/A; new world.
3. Passive-payload fraction (KEPT-4, self-inspection vs self-description):
   taint over replication events for bytes copied-but-never-executed, and
   whether any lineage later makes payload load-bearing -- the storage side
   of accumulation, linked to decorative load (POI-093); territory A/D;
   instrument built on S1's probe.

## 5. Map consequences

- No new top-level territory is forced. One vocabulary gap is real:
  Prometheus has no word for memory that is stored in a DISTRIBUTION OF
  MARGINS and readable only by RE-DRIVING the world (protocol-dependent
  readout). Candidate sub-coordinate "F0 -- memory formation without
  improvement" under F: F currently asks for a learning rule nobody
  installed (improvement); MTM/RPM are recordability without improvement.
  The F/F0 split matters because F0 is what D rung R0 (persistence of a
  history-specific object) would be built from in organism-free worlds.
- Candidate NEW TERRITORY, flagged not claimed: "H -- what a world
  remembers of how it was driven" (drive-history memory of the physics
  itself: RPM stacks, counting, lock-and-key sequences, max-registers). It
  would become a territory only if the nesting audit finds non-trivial
  transition graphs in Prometheus lattice rules; if every rule audits as a
  single absorbing state or a max-register, it collapses into F0.
- New control for D (KEPT-5): the max-register baseline for every
  persistence claim.

## 6. Sources (URLs used)

- https://link.aps.org/doi/10.1103/PhysRevE.88.032306 ; https://arxiv.org/abs/1307.1184
- https://link.aps.org/doi/10.1103/RevModPhys.91.035002
- https://www.science.org/doi/10.1126/sciadv.abg7133
- https://arxiv.org/pdf/2209.00572 ; https://arxiv.org/pdf/2510.11825
- https://arxiv.org/abs/1802.03096 ; https://link.aps.org/doi/10.1103/PhysRevE.102.012122
- https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.130.268204
- https://www.pnas.org/doi/10.1073/pnas.2308414121
- https://royalsocietypublishing.org/doi/10.1098/rspb.1995.0172
- https://www.science.org/doi/10.1126/science.aag1582
- https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1000542
- https://journals.plos.org/plosgenetics/article?id=10.1371%2Fjournal.pgen.1009155
- https://arxiv.org/pdf/2608.22348
- https://dl.acm.org/doi/10.1145/332833.332842
- https://link.springer.com/chapter/10.1007/3-540-59496-5_326 (self-inspection)
- https://arxiv.org/pdf/1903.05776 ; https://arxiv.org/pdf/2309.04382
- https://www.sciencedirect.com/science/article/abs/pii/S0014305708006332 (Mullins review)

## 7. Global grep appendix

Command (from /home/jcraig/Prometheus, 73 origin refs, markdown only):
  git grep -o -i -E 'return-point|transient memor|multiple memor|mullins|
  keim|nagel|hysteron|preisach|stochastic corrector|szathm.ry.*demeter|
  self-inspection|laing|futamura|partial evaluat|reflective tower|
  growing.point|rejuvenat' $(git for-each-ref refs/remotes/origin) -- '*.md'
Occurrences (summed over refs): nagel 709 (all unrelated names, e.g.
"Spitznagel" in aporia deep-research reports), reflective tower 639 and
partial evaluat 256 (generic phrases in aporia/docs/deep_research_reports,
frontier_campaign_69 dossiers, agents/hephaestus, techne/fossils, Nestor
graphworld review -- none proposes a transplant), rejuvenat 60
(roles/Bellerophon/forensics_2026-09-23, unrelated usage), self-inspection
24 and laing 5 (roles/Nestor/campaigns/npe-p2-endogenous-heredity-2026-09-27
/delegates/EXTERNAL_RESEARCH.md Q8; roles/Nestor/campaigns/npe-arc3-
2026-09-28/delegates/external/EXTERNAL_SCAFFOLDING.md s1.9 -- the real
prior art for KEPT-4). Zero occurrences: return-point, transient memor,
multiple memor, mullins, keim, hysteron, preisach, stochastic corrector,
szathmary-demeter, futamura, growing point.
Earlier broader pass (local files; roles/Odysseus, frontier_campaign_69,
Atlas catalog): reaction-diffusion 18, szathm 17, hypercycle 15, quine 13,
error correct 10, proofreading 4, fraternal 4, kinetic proofreading 3,
egalitarian 3, zeravcic 1, multilevel/group selection 1 each, amorphous
computing 1 (the directive itself). A first all-ref pass over *.py/*.txt
as well finished late (46 min): of the raid-critical terms only
"memory formation" (78, in agents/hephaestus/humanreadable/Thermodynamics---
Immune_Systems---Free_Energy_Principle.md: immune memory, not matter) and
"rejuvenat" (78, as above) occur; return-point, transient memory, Mullins,
Keim, Paulsen, hysteron, Preisach, stochastic corrector, Futamura, growing
point, Zeravcic-memory: zero in *.md/*.py/*.txt on every ref.
