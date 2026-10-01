# Skopos -- forensic dossier (Tityos Phase 3, signal-vs-hallucination lane)

Crawler: Tityos worker g5_adversarial, 2026-10-01. Worktree F:/Prometheus-worktrees/tityos-phase3 at
36ffe8073. Read-only; searches excluded **/*holdout*/** and **/nestor_secrets/**.
Labels: [IMPLEMENTATION FACT] [DESIGN INTENT] [HISTORICAL CLAIM] [REPORTED RESULT -- UNVERIFIED]
[LATER CORRECTION / CONTRADICTION] [CODE-INFERRED CAPABILITY] [UNKNOWN / AMBIGUOUS].

---------------------------------------------------------------------------------------------------
## 0. Summary

Skopos ("one who watches, one who aims") was a March 2026 RELEVANCE FILTER in the literature/intelligence
pipeline (Eos -> Aletheia -> Skopos -> Metis), invoked by the Pronoia orchestrator. It did not measure
scientific signal; it measured topical relevance: an LLM scored entities extracted from papers by Aletheia
(techniques, terms, claims, tools, motifs) 0-5 against a hardcoded list of five research threads, wrote a
daily "alignment report" (which threads are fed vs STARVING), and on any score >= 4 was to auto-generate a
"Titan Council" prompt for frontier models [DESIGN INTENT: agents/skopos/README.md; IMPLEMENTATION FACT:
agents/skopos/src/skopos.py, 738 lines].

What it measured in practice: ONE entity (tools id 19 "Circuits Zoom-In"), once, in one LLM call, against
five threads, on 2026-03-23 21:21:11Z -- 5 rows -- out of 448 eligible entities; then nothing for nine more
days of daily runs [IMPLEMENTATION FACT: re-measured here from the committed agents/skopos/data/scores.db
blob]. Its reports claimed "5 scored entities" six times (a row-vs-entity units error), contradicted
themselves for four runs after a code-only thread-list change orphaned the rows, were never committed
(.gitignore agents/* and **/reports/), and were nevertheless read by Metis as model context. The orchestrator
health check said "skopos: OK" throughout [LATER CORRECTION: roles/Skopos/ARCHAEOLOGY_2026-09-11.md,
self-autopsy 2026-09-11]. Parked 2026-09-11 as INSTRUMENT_SPECIMEN by operator ruling.

Machinery strength: negligible as an instrument (no calibration, no controls, no inter-rater check, n=1).
Its value to Phase 3 is as a specimen: a selector whose rejection/"starving" signal was an eligibility
artifact ("eligible / observed / judged / accepted / rejected" accounting), and a seat-level yield
self-report inflated in the seat's favour and invisible for 163 days.

---------------------------------------------------------------------------------------------------
## 1. Charter and role evolution

- Created 2026-03-23 (first scoring write), committed 2026-03-24 in a bulk commit 7e9719cb0 ("Ignis 1.5B
  experiment suite, Skopos agent, docs, and session artifacts") [IMPLEMENTATION FACT].
- Thread list replaced in code 2026-03-27 (8af6ba9e5) [IMPLEMENTATION FACT per ARCHAEOLOGY; commit exists
  in log]. Original threads were Ignis/steering-vector interpretability topics (anti_cot_geometry,
  precipitation_signatures, tensor_decomposition, sae_features, scale_threshold); replacements (ejection
  mechanism, CMA-ES/LoRA, Forge+Sphinx eval, knowledge substrate, scale transfer) [HISTORICAL CLAIM].
- Last run 2026-04-01 07:24Z; README expanded +45/-6 on 2026-04-03 (b674a9976) describing the never-executed
  GENERATE stage [HISTORICAL CLAIM: ARCHAEOLOGY s1].
- 2026-04-02 roles/PipelineOrchestrator/DESIGN_bidirectional_skopos.md proposed three more loops on top of it
  (pillar inboxes, reverse flow, auto threads); nothing built [HISTORICAL CLAIM].
- 2026-09-11: seat adopted (b3e27f7f4 "the autopsy says it scored one entity in its life"), parked same day
  (aca768424, PARKED / INSTRUMENT_SPECIMEN; SKOPOS-06/07 discharged), defect notes to Metis and
  PipelineOrchestrator (roles/Skopos/prompts/2026-09-11_defects/), last message 8bec88eb2 (reply to Metis
  #109: third instance given, base rate declined). Metis accepted defect 01 and did not fix it (bf376bd93)
  [IMPLEMENTATION FACT: git log].
- Latent charter (not active): "Skopos does not decide what is relevant. Skopos measures whether a selector
  had a fair opportunity to decide, and whether its reported performance survives controls." Resurrection
  predicate: an active seat owning a selector requests selection instrumentation and names the surface
  [DESIGN INTENT: roles/Skopos/RESPONSIBILITIES.md].
- Host: M2 (SPECTREX5) for the 09-11 pass [HISTORICAL CLAIM: STATUS.md]. March host unknown.
- Atlas: no mention of Skopos in atlas/ or roles/Atlas/ [IMPLEMENTATION FACT: git grep with exclusions].

---------------------------------------------------------------------------------------------------
## 2. Code / system architecture

agents/skopos/src/skopos.py (738 lines) [IMPLEMENTATION FACT]:
- RESEARCH_THREADS hardcoded at line 64; configs/skopos_config.yaml says the file is "for reference".
- load_recent_entities(since_hours=24) (143-198): papers with processed_at in the last 24 h, entities whose
  source_papers intersect them, from agents/aletheia/data/knowledge_graph.db.
- already_scored() (130-136) keys on (entity_type, entity_id); table UNIQUE is (entity_type, entity_id,
  thread_id).
- call_llm (253-): provider chain -- NVIDIA nemotron-3-super-120b-a12b (env NVIDIA_MODEL), then
  qwen-3-235b-a22b-instruct-2507, then llama-3.3-70b-versatile; temperature 0.1-0.2.
- score_entities (343-): one prompt listing entities x threads, JSON back, range check 0-5 with a warning.
- report (around 505-515): total = COUNT(*) rows, labelled "scored entities".
- generate Titan prompt (603-): writes docs/titan_prompts/auto_<date>.md -- directory never existed.
- Persistence: agents/skopos/data/scores.db, table skopos_scores(id, entity_type, entity_id, entity_name,
  thread_id, score, rationale, scored_at). NO column for the model/provider that produced the score
  [IMPLEMENTATION FACT: schema read here].
- Scale: one SQLite file, 5 rows.

---------------------------------------------------------------------------------------------------
## 3. Inputs and outputs

In: Aletheia knowledge_graph.db (448 eligible entities over 163 processed papers, per ARCHAEOLOGY)
[HISTORICAL CLAIM; aletheia DB not opened here]. Out: scores.db (5 rows); six alignment reports (untracked
until annotated copies committed at roles/Skopos/artifacts/alignment/2026-03-23..04-01_alignment.md);
0 Titan prompts. Downstream: agents/metis/src/metis.py:94-103 globbed the newest report into LLM context
with `except: pass` [HISTORICAL CLAIM; Metis code not opened by me].

## 4. Claim class it was meant to police

Not scientific truth: "is this extracted item relevant enough to our live research threads to act on /
escalate to frontier models?" Also implicitly "which threads are starving for input" [DESIGN INTENT].

## 5. Measurement methodology

Single LLM judge, 0-5 ordinal relevance per (entity, thread), batched in one prompt, low temperature; no
rubric anchors beyond the prompt text; no repeat scoring, no second judge, no gold set [IMPLEMENTATION FACT].

## 6. Null/control generation -- none found (searched skopos.py, configs, README, roles/Skopos).
## 7. Positive controls -- none found. No known-relevant planted entity to show a 4+ can be produced; the
   >= 4 GENERATE branch never executed [IMPLEMENTATION FACT / HISTORICAL CLAIM].
## 8. Negative controls -- none found (no known-irrelevant entity).
## 9. Neutral controls -- none found.

## 10. Qualification criteria / thresholds

score >= 3 "relevant"; score >= 4 triggers Titan prompt generation automatically, with no deterministic
predicate and no human step (ARCHAEOLOGY D7 notes this contradicts the later base role "No LLM
adjudicates") [IMPLEMENTATION FACT / LATER CORRECTION].

## 11. Statistical methods -- counts and per-thread max/avg only.

## 12. Independence assumptions

- The judge is an LLM from a fallback chain of three providers; which one scored the 5 rows is not recorded
  (no model column) [IMPLEMENTATION FACT] -> scorer identity unrecoverable [UNKNOWN / AMBIGUOUS].
- The same pipeline family (LLM extraction by Aletheia, LLM scoring by Skopos, LLM brief by Metis) chained
  model outputs with no independent check between links [CODE-INFERRED CAPABILITY].
- Self-autopsy only: ARCHAEOLOGY is written by the subject; an independent pass (SKOPOS-08) was proposed and
  closed as PARKED [HISTORICAL CLAIM].

## 13. Provenance tracking

Failure: the seat's only outputs (reports) were untracked for 163 days because of .gitignore:200
(`agents/*`) and .gitignore:28 (`**/reports/`), yet consumed downstream; the numbers in them were
unauditable [LATER CORRECTION: ARCHAEOLOGY s1 correction]. The self-autopsy itself first asserted the
reports were tracked, then corrected that the same day (CALIBRATION L-06) [HISTORICAL CLAIM].
Win: the 09-11 pass committed annotated copies with sha256 of originals; the README annotation records the
sha256 of the annotated-from text [IMPLEMENTATION FACT: agents/skopos/README.md head].
Repository-scale finding: any directory named reports/ is ignored unless force-added; 191 tracked files
survive under four reports/ dirs (apollo/archive, charon/reports, forge/v2, ludus/atlas_of_worlds)
[REPORTED RESULT -- UNVERIFIED].

## 14. Known defects (ARCHAEOLOGY D1-D7, line references verified here for D1, D2)

D1 COUNT(*) rows labelled entities (5x inflation in its favour). D2 dedup key omits thread -> new threads
unreachable. D3 scoring key in code while config claims to hold it; thread swap orphaned rows. D4 24-h
window + D2 made reachable set ~empty after day one. D5 header "5 scored" vs body "0 entities" for four runs.
D6 no freshness/liveness record; orchestrator "skopos: OK". D7 LLM score gates an artifact with no human.
Plus (this crawl): no model provenance column.

## 15. Historical audits

By Skopos: self-archaeology (09-11); defect reports to Metis (stale/contradictory Skopos context) and
PipelineOrchestrator (design premised on a one-entity scorer); the Metis exchange on "missing input becomes
optimistic" pattern where Skopos supplied a third instance but declined to call three instances a base rate.
On Skopos: none independent found.

## 16. Historical findings

- "Threads X are STARVING" (alignment reports 03-23..04-01) -- INSTRUMENT FAILURE (eligibility artifact, not
  relevance).
- "5 scored entities | 2 relevant (3+)" -- LATER OVERTURNED (1 entity).
- Circuits Zoom-In scored 2-3 on five threads -- UNKNOWN (n=1, unrecorded model).

## 17. Later corrections (timeline)

claim "5 scored entities" (03-23..04-01, six reports) -> no challenge (health check OK) -> 09-11 self-
autopsy: rows vs entities -> L-01 recorded, README annotated in place, reports committed annotated -> status:
specimen. Second: archaeology claimed reports tracked -> same-day correction (L-06).

## 18. Pivots -- relevance filter (March) -> dormant -> parked specimen with latent "selection
instrumentation" charter (09-11).

## 19. Journals / TODOs / backlogs

roles/Skopos/journal/2026-09-11.md; roles/Skopos/BACKLOG_H0H5.md (all closed PARKED); CALIBRATION.md L-01..
L-06; roles/Skopos/prompts/2026-09-11_defects/00-03 + MANIFEST.

## 20. Research reports

agents/skopos/README.md (annotated); roles/Skopos/ARCHAEOLOGY_2026-09-11.md; roles/Skopos/artifacts/
alignment/*.md (six annotated reports); roles/Skopos/prompts/2026-09-11_defects/*.md.

## 21. Failure cases

FP: "STARVING" threads and "5 scored entities" reports; OK health verdict. FN (plausible): 447 of 448
eligible entities never judged -- any genuinely relevant extraction in the March literature corpus would
have read as "not relevant / starving" (rejection and non-observation indistinguishable). New threads
could not recover old entities (D2).

## 22. Mechanism archaeology -- n/a.

## 23. Novelty/prior-art audit -- partially relevant: Skopos sat in the literature intake chain but judged
relevance, not novelty. Its corpus was Aletheia's 163 processed papers; blind spot: 99.78% of entities never
observed, so "unfamiliar/irrelevant to Prometheus" was set by an eligibility window, not by judgement.

## 24. Lens inventory

As built: toy-grade LLM relevance tagger, no calibration. Reusable idea only: selection accounting
(eligible / observed / judged / accepted / rejected with denominators in the same artifact) and
"yield published with eligible count". Resolution ceiling unknown (n=1).

## 25. What I did not read / open questions

Not read: skopos.py beyond the cited ranges; the six annotated reports' bodies; Metis code; Aletheia DB;
PipelineOrchestrator design doc (cited via ARCHAEOLOGY). Open: which LLM produced the 5 scores; whether Metis
briefs were influenced (ARCHAEOLOGY says UNMEASURED; no brief text quotes it).
