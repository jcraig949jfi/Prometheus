# Nous -- Phase 3 intake dossier

Seat: Nous
Crawler: Tantalus (worker)
Tree SHA: 21a47402a (origin/main)
Date: 2026-10-01

Summary. Nous (agents/nous/, written 2026-03-24, last own commit 2026-03-29)
was the first stage of the March 2026 forge pipeline, Nous -> Coeus ->
Hephaestus -> Nemesis -> Coeus -> Nous [CLAIM] (agents/nous/README.md
"Pipeline Position"). What was BUILT and RUN [IMPL]: a loop that samples a
triple from a hand-written 95-concept, 20-field dictionary
(agents/nous/src/concepts.py), sends one fixed prompt to a hosted NVIDIA NIM
model asking what scoring algorithm the three concepts suggest and asking the
SAME model to rate its own answer 1-10 on four dimensions, then parses the
ratings with regexes and labels novelty by substring counting
(agents/nous/src/nous.py:63-96, scorer.py). The committed corpus is 5,918
rows in 12 run directories (2026-03-24..03-27); 4,187 more rows exist only on
one disk, never committed [RESULT-UNVERIFIED] (roles/Nous/ARCHAEOLOGY_2026-09-11.md
s2-s3). The seat's 2026-09-11 self-audit found the novelty label returns
"novel" 92.3% of the time, the composite is nearly constant, and the
composite cannot separate the scorer's own reject class (p = 0.31)
[RESULT-UNVERIFIED]. The README's scoring rationale (implementability weight
+0.221) is contradicted by the artifact it cites (-0.467); this crawl went
further and found that NO committed version of that artifact ever carried
+0.221 (section 12). Nous is an LLM-prompt sampler with self-rating; it has no
organism, no world and no independent ruler. The 2026-09-29 Collider
visualizer (collider/) is built on its corpus and is described below as a
shared surface.

## 1. Identity, charter and pivots

- agents/nous/: 11 commits 2026-03-24..2026-05-13 (last one not this lane:
  8b8676272) [IMPL] (git log). roles/Nous/: 2 commits, 2026-09-11
  (4b8a15365, dcafe3047) [IMPL].
- First commit 2f3e4eb6f 2026-03-24 "Ignis v2 + Nous + Hephaestus" [IMPL].
- Charter: none ("Charter: NONE, and this file does not invent one")
  [CLAIM] (roles/Nous/RESPONSIBILITIES.md). Manifest: agents/nous/configs/
  manifest.yaml (provider nvidia, default qwen/qwen3.5-397b-a17b) [IMPL];
  CLI default model nvidia/nemotron-3-super-120b-a12b (nous.py:474) [IMPL].
  5,915 of 5,918 committed responses are nemotron-3-super-120b, 3 are qwen
  [RESULT-UNVERIFIED] (collider/FINDINGS.md).
- Pivots: 03-27 Coeus-weighted sampling (8af6ba9e5 "Nous weights"); 03-28
  gap-targeted priority triples (302c002d3); last output 2026-04-02 when the
  API call never returned [RESULT-UNVERIFIED] (ARCHAEOLOGY s1). Dormant 162
  days; 2026-09-11 adoption, BLOCKED on NOUS-XL-01, recommendation PARKED
  [CLAIM] (STATUS).
- Relationships: Coeus (consumer; agents/coeus/), Hephaestus (forge queue
  sorted by Nous composite + Coeus priority), Nemesis (attack) [CLAIM];
  Hecate 2026-09-29/30 used the Hephaestus/Nous triples (6,939 triples) as a
  corpus [CLAIM] (roles/Atlas/inference_harvest_2026-09-30/workers/digests/
  cosmos_aether_hecate.md:56,195).

## 2. Engine/system inventory

Engine N1: Nous generator.
- Paths: agents/nous/src/nous.py (28 KB: sampling, prompt, API, checkpoint,
  rankings), scorer.py (7 KB), concepts.py (22 KB, CONCEPTS = 95 dicts),
  rescore.py (one-time re-scorer), data/priority_triples.json (15 triples),
  configs/manifest.yaml, runs/<ts>/{responses.jsonl, rankings.md,
  checkpoint.json, meta.json} [IMPL].
- Entrypoints: `python agents/nous/src/nous.py --unlimited | --n-combos N |
  --resume` [IMPL] (README Usage).
- Execution: hand-launched continuous loop, batches of 500, 2.0 s delay,
  temperature 0.7, max_tokens 2048 [IMPL] (nous.py:329-330; manifest).
- Persistence: append-per-entry JSONL; runs after 2026-03-28 swallowed by
  .gitignore:140 [RESULT-UNVERIFIED] (ARCHAEOLOGY s2).
- Scale: committed 5,918 rows, 5,727 unique triples; largest run 3,030 rows
  (20260325_132552, 12 MB responses.jsonl) [IMPL file sizes;
  counts RESULT-UNVERIFIED].
September instruments: roles/Nous/science/corpus_audit.py (reproduces the
audit numbers, `--check` against values frozen at 363120e08) and
test_guard.py [IMPL].

## 3. Code architecture and dataflow

sample triple (80% cross-field bias; Coeus weights 3.0x if forge_effect >
0.3, 0.3x if < -0.2, 0.5x Goodhart, 2.0x undervalued; priority triples first)
-> PROMPT_TEMPLATE -> chat completion -> score_response(text) -> JSONL ->
rankings by composite [IMPL] (nous.py:113-150, 177-305; scorer.py).

The prompt itself tells the model what succeeds: "The tools that succeed in
our pipeline use structural parsing ... constraint propagation ... Tools that
rely on hash similarity or bag-of-words fail" [IMPL] (nous.py:84-87). The
rating lines are appended to the generation prompt, so generator and rater
are one call [IMPL] (nous.py:91-95).

Code-vs-doc disagreements (several found by the seat, CITED; checked here):
- README "95 concepts x 18 fields" vs dictionary 20 distinct fields [IMPL:
  verified by importing concepts.py in this crawl, a zero-cost inspection].
- README key `mechanism_type`; code key `mechanism` [CLAIM] (collider/FINDINGS.md).
- README "Out of 1,500+ evaluated combinations, roughly 20-30% score high"
  vs committed 5,918 and 12.1% high_potential [RESULT-UNVERIFIED] (ARCHAEOLOGY s5).
- README scoring table (+0.221 implementability, 0.000 others): see s12.

## 4. Claimed computational primitive vs actual mechanism

- Label: "Combinatorial Hypothesis Engine"; "cross-domain concept collisions
  could produce a new computable reasoning criterion" [INTENT] (README).
- Smallest actual mechanism: uniform-ish sampling of 3 indices from 95, a
  single LLM call, and regex extraction of four integers the LLM wrote about
  its own text [IMPL].
- Novelty mechanism: count of substrings from two hand lists; "novel" is
  itself a novel-signal substring, so a response saying "not novel" adds to
  both counts [IMPL] (scorer.py assess_novelty: novel_signals contains
  "novel", existing_signals contains "not novel"); any "unproductive" signal
  ("forced", "superficial") overrides [IMPL]. The prompt asks "Is this
  combination novel, or does it map to existing work?" so the word "novel"
  is primed in every answer [CODE-INFERRED]. This plausibly explains 92.3%
  "novel" vs 0.07% "existing" [CODE-INFERRED].
- Composite = mean of reasoning, metacognition, hypothesis_generation;
  high_potential = all three >= 7 [IMPL] (scorer.py score_response).
- Phenomenon the ruler sought: which concept collisions yield implementable
  reasoning tools [INTENT].
- Could the "organism" perform it: there is no organism; the LLM proposes
  prose. Whether a proposal becomes working code is decided downstream by
  Hephaestus [CLAIM].
- Ruler vs shortcut: none; the rater is the generator, no controls of any
  kind exist (no content-free arm, no shuffled-concept arm, no repeat-triple
  self-consistency) [RESULT-UNVERIFIED] (ARCHAEOLOGY s4 M4).

## 5. Representation/state architecture

Concept = {name, field, description, mechanism in constraint/structure/
dynamics/measure} [IMPL] (concepts.py). Response row = triple indices, names,
fields, response_text, score{ratings, composite_score, novelty,
high_potential, is_unproductive}, model, timestamp [IMPL] (README schema;
FINDINGS.md). No embeddings or learned representations.

## 6. Organism/player architecture

None found.

## 7. World/environment architecture

None. The "space" is C(95,3) = 138,415 unordered triples [CODE-INFERRED];
5,727 unique triples were evaluated in committed data [RESULT-UNVERIFIED].

## 8. Search/training/adaptation mechanism

Sampling reweighted by Coeus concept_scores.json (forge_effect thresholds)
and seeded by 15 gap-targeted priority triples [IMPL]. The feedback signal
(Coeus forge effects) came from a regression the Coeus seat later recorded
as MEASUREMENT_FAILURE [CLAIM] (roles/Nous/STATUS.md).

## 9. Measurement/ruler stack

Self-ratings 1-10 x 4, composite, novelty label, high_potential [IMPL].
September audit numbers [RESULT-UNVERIFIED] (ARCHAEOLOGY s4): reasoning sd
0.532, mode 7 = 57.7%; five composite values cover 91.4% of rows;
unproductive vs productive composite 6.4696 vs 6.4067, z = +1.28,
permutation p = 0.308 (2,000 shuffles); disk corpus z = +2.76, p = 0.026,
retracted as not surviving restriction to committed rows.

## 10. Baselines and controls

None in the engine [RESULT-UNVERIFIED] (audit printed all 8 "control"
keyword hits; all are concept names). September: the audit's
label-permutation test is the only control ever run on this channel.

## 11. Historical experiment campaigns

C-N1 March generation runs. 2026-03-24..03-27 committed (12 dirs), to
2026-04-02 on disk (22 dirs). Q: which triples are worth forging. Organism:
LLM. Pressure: none beyond sampling weights. Measurement: self-rating.
Scale: 5,918 committed / 10,105 disk rows. Reported: rankings.md per run;
"1,748 Nous combos" (45f225f51). Later: ranking channel falsified (09-11).
Paths: agents/nous/runs/. Label: LATER OVERTURNED (as a selection signal).

C-N2 2026-09-11 self-audit. 4b8a15365. Q: is the shipped instrument
informative. Result: M1-M4 above. Label: REPORTED NEGATIVE/NULL.

## 12. Reported results and later corrections

Scoring-weight timeline (this crawl checked every committed version of
agents/coeus/graphs/causal_graph.json, key score_dag.implementability):
- da42cc7e0 (2026-03-25): 0.0 (metacognition 0.6872, hypothesis 0.2494)
  [IMPL] (git show da42cc7e0:agents/coeus/graphs/causal_graph.json). The same
  commit's agents/coeus/README.md already states "Implementability is the
  only Nous score dimension predicting forge success (+0.221)" [IMPL]
  (git show da42cc7e0, coeus README line ~97).
- 45f225f51 / fbb92a11a (2026-03-25): implementability 0.4142, metacognition
  0.5904, others 0.0 [IMPL]. agents/nous/README.md's "+0.221" was added in
  this window [IMPL] (git log -S"0.221" -- agents/nous -> 45f225f51).
- 5573808c7 (2026-03-27) to HEAD: implementability -0.467, metacognition
  +0.4819, hypothesis_generation +0.5708, reasoning -0.2042 [IMPL]
  (agents/coeus/graphs/causal_graph.json:436-442 at 21a47402a).
- Seat correction 2026-09-11: README +0.221 vs shipped -0.4670 [CORRECTION]
  (ARCHAEOLOGY s5; CALIBRATION.md:62-63; BACKLOG NOUS-02).
- This crawl's addition [CORRECTION]: +0.221 never appears as an
  implementability weight in any committed causal_graph.json (values were
  0.0 -> 0.4142 -> -0.467); the README number has no committed source.
  The only "0.221x" strings in agents/coeus history are rate_without fields
  and a concept-pair score (git log -S"0.221" -- agents/coeus: da42cc7e0,
  5573808c7, 8af6ba9e5). Also, the README's "Metacognition ... weight 0.000"
  is contradicted by every committed version (0.6872, 0.5904, 0.4819).
- The README's "Active Inference forge effect +0.69 / Topology -0.21" vs
  shipped +0.2007 / -0.0563 [CORRECTION] (ARCHAEOLOGY s5, CITED from Coeus
  archaeology D1; not re-derived here).
- The scorer's design (implementability kept separate from the composite
  "because it's the only dimension Coeus found to predict forge success")
  rests on a number with no committed source [CODE-INFERRED].
- Nous withdrew its own draft correction of Coeus's "last run 2026-03-27"
  (disk vs repository) [CORRECTION] (ARCHAEOLOGY s2).

## 13. False-positive archaeology

- Self-rated "HIGH POTENTIAL" (12.1%) used as forge priority with no
  independent oracle.
- Novelty label structurally biased to "novel" (substring design + primed
  prompt).
- The 2.76-sigma disk-corpus effect, retracted by the seat itself.
- Downstream (Coeus) regressed forge outcome on these self-ratings; the
  sign of the "predictive" dimension flipped across commits within two days.

## 14. Likely false-negative regimes

A content-bearing proposal channel would be invisible here: ratings
saturate at one integer, so any real signal in response_text is unread by
the ruler. The response texts themselves (5,918 committed, with 2,740
model-named mechanisms per Collider ingest) were never scored by anything
independent [RESULT-UNVERIFIED] (collider commit 49d1f9651).

## 15. Phase 3 audit (engine N1)

a. Representation richness: hierarchy NO; compositional structure PARTIAL
   (a triple is a 3-way combination, unordered for scoring); variable
   binding NO; memory NO (checkpoint only dedups); recurrence NO;
   counterfactual state NO; latent variables NO; temporal abstraction NO;
   spatial abstraction NO; reusable substructure NO; dynamic routing NO;
   self-reference PARTIAL (the model rates its own output -- the defect).
b. Reasoning opportunity: none required by the loop; the LLM's prose may
   contain reasoning but nothing tests it.
c. Shortcut surface: rating mode-collapse; word "novel" in answer; prompt
   telling the model which tools succeed; concept-name priors (e.g.
   "Property-Based Testing" in 9 of top 20 in one run) [RESULT-UNVERIFIED].
d. Ruler resolving power: essentially zero (cannot separate its own
   rejects, p = 0.31).
e. Scale: 95 concepts, 20 fields, 138,415 possible triples, 5,727 unique
   committed, 1 model, 1 prompt, 12 committed runs.

## 16. Research reports and substantial documents

- agents/nous/README.md -- architecture and (contradicted) scoring rationale.
- roles/Nous/ARCHAEOLOGY_2026-09-11.md -- death, 41% uncommitted output,
  M1-M4 audit, README mismatch, queue classified.
- roles/Nous/CALIBRATION.md -- self-corrections.
- roles/Nous/RESPONSIBILITIES.md -- re-premise proposal: corpus as a
  "measured null" calibration fixture.
- agents/nous/runs/*/rankings.md -- per-run top 50.
- collider/FINDINGS.md -- independent survey of the Nous/Hephaestus/Coeus
  artifacts (2026-09-29).

## 17. Journals/TODOs/backlogs/pivots/abandoned branches

roles/Nous/journal/2026-09-11.md; BACKLOG_H0H5.md (NOUS-01 preserve 4,187
uncommitted rows + nous.log, NOUS-02 README annotation, NOUS-03 diagnose 153
unclear novelty rows and ~100 missing implementability ratings, NOUS-06
notify sibling seats about ignored output); NOUS-XL-01 revive/park/retire.

## 18. Dependencies on other engines and seats

Coeus (concept_scores.json weights; causal_graph.json), Hephaestus (ledger,
forge), Nemesis; NVIDIA NIM via openai client [IMPL]. Downstream re-use:
Collider (below), Hecate first cycle [CLAIM].

## 19. Scaling limitations

API-rate bound (2 s delay, minutes per call near the end); a single hosted
model; hand-written dictionary is a fixed prior.

## 20. Lens potential for Phase 3 (descriptive)

Substrate: LLM text. Organisms: none. Worlds: none. Pressure: self-rating.
Phenomenon family: idea proposal / cross-domain recombination. Reusable:
5,918-row committed corpus as a negative-control fixture for any proposal
scorer (seat's own proposal); dictionary of 95 typed concepts. Toy-grade:
the scorer. Unknowns: whether response texts contain implementable
mechanisms an independent grader would rank differently.

## 21. Open questions / coverage gaps

Read: agents/nous/README.md, manifest.yaml, scorer.py in full, nous.py
prompt and sampling skeleton, concepts.py (imported to count), roles/Nous
STATUS, RESPONSIBILITIES, ARCHAEOLOGY s0-s5, causal_graph.json score_dag at
four commits, collider FINDINGS/README head, genome.ts head, collider commit
message. Not read: rescore.py beyond its header; rankings.md files; the
response JSONL (not opened); CALIBRATION.md and journal in full; Coeus
archaeology; Hephaestus ledger; collider render code. Disk-only rows and
nous.log are outside the tree and were not seen.

## Appendix S. Shared surface: collider/ (built 2026-09-29, no seat prefix)

Attribution: 2 commits, 49d1f9651 and df7a328fe, both 2026-09-29, author
James Craig with Claude co-author, subject prefix "collider:", no seat name
[IMPL] (git log -- collider). The commit message says the historical ingest
reads 95 Nous concepts, 5,727 unique triples from 12 Nous runs (5,918
responses), joined to the Hephaestus forge ledger (6,661 entries, 385
forged) [CLAIM]. Atlas digests mention a "Cyclops collider survey" with the
same counts [CLAIM] (cosmos_aether_hecate.md:195), and the Achilles census
attributes collider/ to Cyclops on the single evidence of
roles/Hecate/RESPONSIBILITIES.md:49 ("collider/, Cyclops lane"), calling the
owner "weakly evidenced" [CLAIM] (roles/Achilles/census/registry/engines.json,
collider entry). Not one of this crawl's five seats; owner Cyclops is
plausible but unconfirmed [UNKNOWN].
What it is [IMPL]: a TypeScript + Vite + three.js/WebGL2 mobile "swipe feed";
collider/src/model/genome.ts maps a concept triple deterministically (FNV-1a
hash + mulberry32 PRNG, hand-set field/mechanism affinity tables, positional
weights, calibration offsets fitted so 8 visual archetypes each take 11-13.5%)
to a "VisualGenome" rendered as crystallization, vortex, Gray-Scott
reaction-diffusion, RK4 strange attractors, Hopf fibration etc.
(collider/src/render/archetypes/, 9 files). scripts/ingest_hephaestus.py is a
read-only ingest with sha256 manifest (public/data/ingest-manifest.json).
Tests: vitest 15/15 claimed [CLAIM]. Deployed to GitHub Pages via
.github/workflows/pages.yml [CLAIM] (collider/README.md).
Computational primitive: none in the scientific sense -- a deterministic
visual hash of concept names; the "collision" and "emergence" are rendering
archetypes, not computation on the concepts [CODE-INFERRED]. The README
labels Nous texts "historical LLM output, never validated science" [CLAIM].
Value for intake: FINDINGS.md is a clean independent inventory of the March
pipeline's artifacts and schema mismatches.
