# V1 PREREGISTRATION — frozen before campaign execution

Date: 2026-09-02. Author: Mnemosyne. Charter:
`roles/Mnemosyne/prompts/CHARTER_EVIDENCE_WIKI_V1_2026-09-02.txt`.
This file is committed BEFORE any annotator or design-arm agent is launched;
the commit timestamp is the freeze point. Post-hoc metric changes are
forbidden; anything learned later is reported as exploratory.

## A. V1-A Ontology qualification

**Held-out corpus:** 24-30 adjudicated findings harvested by an independent
agent from source files NOT among the 42 V0 source packets
(`gold/id_map.json` packet URIs are the exclusion list). Mnemosyne annotates
this corpus BLIND (before reading any annotator output) and commits a hash of
her assignments; her labels are reported for comparison but NEVER gate-bearing.

**Annotators:** 6 independent subagents, isolated contexts, no access to
`curation_v1.json` assignments or to each other.
- Condition A (2 annotators): ontology names + definitions provided; assign
  1-2 mechanisms, 1 substrate_class, failure_class if negative;
  NONE_OF_THE_ABOVE explicitly allowed.
- Condition B (2 annotators): as A, plus explicit permission to propose NEW
  mechanisms when fit is poor (forced-fit escape).
- Condition C (2 annotators): NO ontology shown; free-form 3-10-word
  mechanism description. A separate normalizer agent (7th), shown ONLY the
  ontology and the free-form phrases (not the findings, not other answers),
  maps each phrase to a canonical mechanism or NONE.

**Metrics and thresholds (primary in caps):**
- PRIMARY M-A1: mean pairwise any-overlap mechanism agreement across the 4
  A/B annotators (share of findings where the two mechanism sets intersect).
  Chance reference: two independent 1-2-subsets of 22 mechanisms overlap
  with p ~= 0.09-0.17. PASS >= 0.50; MARGINAL [0.30, 0.50); FAIL < 0.30.
- M-A2: modal-label exact agreement (report only).
- M-A3: agreement with Mnemosyne blind labels (report only, non-gating).
- M-A4: NONE_OF_THE_ABOVE rate; new-mechanism proposal rate (B); these feed
  ontology growth-rate reporting. No threshold; report.
- M-A5: condition-C normalized labels' any-overlap with A/B labels (tests
  whether free descriptions converge to the same abstractions). Report;
  supports G2 narrative.
- Disagreement matrix per mechanism; each disagreement classified
  vocabulary-vs-conceptual by Mnemosyne (reviewable, quotes required).

**G3 non-circularity retrieval test (frozen procedure):**
- Gold pairs: cross-agent finding pairs in the held-out corpus where BOTH
  condition-A annotators independently assigned an intersecting mechanism.
  Mnemosyne plays no role in pair construction.
- Prediction labels: condition-B annotators' assignments (disjoint agents
  from the pair-definers).
- Retrieval: rank corpus by B-label overlap (ties broken by seeded shuffle,
  seed 3); baselines: BM25 and MiniLM embeddings over source text.
- PASS: label-retrieval MRR >= 2x max(baseline MRR) AND hits@10 >= 0.6.
- If fewer than 4 qualifying gold pairs exist, that scarcity is itself
  reported and the gate falls back to: annotator-agreed pairs from A+B
  pooled (any two annotators agree), same thresholds, disclosed as weaker.
- KILL: M-A1 FAIL or G3 fail => CANONICAL_MECHANISM_LAYER_NOT_QUALIFIED.

## B. V1-B Metabolization experiment

**Design:** 8 matched experiment-design tasks (frozen below), each executed
in BOTH arms (paired), one fresh isolated agent per arm per task (16 agents).
CONTROL: task + normal repo context; the Evidence Wiki is not mentioned.
WIKI: identical prompt + REQUIRED structured consultation through
`ew.client` (queries logged server-side; the proposal must list which
retrieved evidence changed the design, or state "no useful prior evidence
found" — a valid answer, citation never forced).
Arm execution order per task randomized with seed 20260902.
Output format (both arms): hypothesis; design; controls; preregistered
falsifiers with numeric thresholds; stopping rule; unit of inference; what
prior work bears on this (if any).

**Frozen deterministic scoring checklist** (each item yes/no, scored by
Mnemosyne with a mandatory verbatim quote from the proposal; scoring sheet
ships in the audit packet):
- D  duplication: the proposal's PRIMARY question was already adjudicated in
  the repo and the proposal neither acknowledges nor supersedes that verdict.
- K  known-failure walk-in: the design commits the task's named trap (each
  task lists exactly one trap and what a guard looks like).
- R  negative-evidence reuse: the task's pre-listed reuse signature appears
  as a concrete design element (not merely a citation). CITED-only does not
  count as R=1.
- F  falsifier quality: >= 2 falsifiers with explicit numeric thresholds AND
  an explicit stopping rule.
Composite per arm per task: (1-D) + (1-K) + R + F, range 0-4.

**Endpoints and thresholds:**
- PRIMARY: paired task wins (WIKI composite > CONTROL). Let W = wins,
  L = losses. G7 METABOLIZATION_DEMONSTRATED if W - L >= 5; MARGINAL if
  W - L in [3,4]; else METABOLIZATION_NOT_DEMONSTRATED.
- G8 negative-evidence reuse demonstrated if >= 3 tasks have WIKI R=1 with a
  concretely identified changed design decision traceable to a retrieved
  negative-evidence object, AND WIKI R-total > CONTROL R-total.
- G9: report D and K rates per arm; Wiki claimed to reduce duplication only
  if D_wiki < D_control with >= 3-task margin.

**Frozen task slate (task id: design brief / TRAP / REUSE SIGNATURE):**
- T1 Gen-2 retention: design the next retention-policy experiment for the
  D-5 ecology. TRAP: re-proposing selective-vs-arbitrary at n~30 as primary
  (already NOT_ESTABLISHED, +1.51pp inside Holm band) without powering or
  superseding. REUSE SIG: lineage-level unit of inference AND n >= 60 or an
  explicit power computation.
- T2 Probe band: design a free-vs-paid host reasoning-gap measurement.
  TRAP: treating 0.25 as the chance floor. REUSE SIG: non-LLM heuristic
  floor control AND truncation-rate quarantine rule.
- T3 Cross-domain coupling: design a test for object-level coupling between
  EC and L-function features. TRAP: scoring feature-geometry similarity as
  object-level coupling. REUSE SIG: permutation null over object pairings.
- T4 Corpus navigation: design a navigation experiment over theseus/corpus.
  TRAP: using the recorded outcome variable as a mathematical signal.
  REUSE SIG: acknowledges magnitude-compatibility tautology AND stratified
  (non-windowed) sampling plan.
- T5 Knot coupling: design a knot-invariant/spectral coupling search.
  TRAP: claiming discovery from feature correlation without a null.
  REUSE SIG: mutation-exclusion or permutation null AND native invariants.
- T6 Game transfer: design a cross-game strategy-transfer measurement.
  TRAP: occupancy statistic on self-play distribution (exposure x
  competence). REUSE SIG: common reference distribution of decision states.
- T7 BSD rank >= 2: design a BSD verification extension to rank >= 2.
  TRAP: consuming LMFDB Sha at rank >= 2 as independent ground truth.
  REUSE SIG: names the Sha circularity and works around or scopes it out.
- T8 Residue routing: design a failure-residue routing improvement.
  TRAP: routing on concept/field metadata for cold starts. REUSE SIG:
  behavioral/executable routing handle, warm-start framing.

Note: traps/reuse signatures correspond to real adjudicated findings both
arms could in principle discover in the repo (control is not sandbagged; the
question is whether structured retrieval makes finding them reliable).

## C. V1-C Gap prospectivity

Slates generated at the pre-campaign snapshot on mechanism x substrate_class
(evidence_v1): top-5 marginal-contraction gaps; 5 uniform-random unobserved
cells (seed 7); 5 frequency-weighted-random unobserved cells (seed 8). All
registered HYPOTHESIZED with snapshot/method/score/marginals/timestamp.
Slate membership BLINDED in the hypothesis records (method recorded in a
sealed local file, committed as hash, revealed at adjudication) so
downstream agents cannot preferentially pick "the marginal ones".
PRIMARY (prospective, cannot complete in-session): fraction of slate cells
that reach "experiment formulated + prediction committed" and later
"admissible evidence returned" within 60 days, marginal vs controls.
G11 verdict this session: PENDING_PROSPECTIVE (framework only). G12: an
experiment formulated from a wiki gap validates the gap ONLY via admissible
non-wiki-adjudicated evidence.

## D. Engineering gates

Measured directly (no thresholds needed): G1 V0 artifact integrity +
snapshot-refactor repro hash; G4 mechanism registry versioning demo; G5/G6
re-run of provenance + contamination tests incl. new write paths; G10
genuine-contradiction registration (candidates B-001 vs B-025 and B-023 vs
B-024 — real opposite-outcome pairs, surfaced not resolved); G13 fixture
namespace excluded from search/coords/stats; G14 parity re-run (M2-M4
cross-host pending peers; reported honestly); G15 kill + watchdog restart;
G16 delete + rebuild; G17 staleness fields; G18 traceability via read_log +
proposal citations.
