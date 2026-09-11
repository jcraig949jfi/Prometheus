# Nous -- Necromancer evidence pack (2026-09-11)

Investigator: Rhadamanthus (Necromancer fork). Branch rhadamanthus/native-trial-2026-09-11,
baseline e17934d9a82855b6e0ae1c0bf54c0cce569b7795. No LLM calls, no network, no Postgres, no git writes.
Dossier: engine/necropolis/dossiers/nous.dossier.json. Every number below is from a script in this
directory (result file named) unless labelled HISTORICAL (quoted from a repository document).

## 1. Primary sources read

| source | what it is | used for |
|---|---|---|
| agents/nous/README.md, configs/manifest.yaml | self-description (397B model, 20-30% yield, 18 fields) | claims to test |
| agents/nous/src/nous.py (737 L), scorer.py, concepts.py, rescore.py | generator, self-rating parser, dictionary, rescorer | mechanism; scorer replay |
| agents/nous/runs/* (13 dirs) | 12 responses.jsonl + meta/checkpoint/rankings; one .bak | run census |
| agents/nous/data/priority_triples.json | 15 gap-targeted triples (wired 302c002d3, 2026-03-28) | was the wire exercised |
| agents/hephaestus/src/hephaestus.py, ledger.jsonl (6661 L), runs/*/meta.json | the only coded consumer | gate trace, forge join |
| agents/coeus/graphs/concept_scores.json | sampling weights fed back to Nous | skew check |
| forge/v2/nous_t2, forge/v3/nous_t3, forge/STATUS_T1_T2_20260403.md | descendants | supersession dating |
| techne/registry/build_concepts_index.py + concepts_index.jsonl; engine/queues/CONSUMPTION.jsonl | prior salvage certificate (fbd94b997) | reproduced |
| dossiers/_keeper_evidence/intelligence_outputs_census_result.json | Keeper capture of agora.intelligence_outputs (M1) | second channel, cited |
| pivot/agents_nous_resume_2026-05-13.md, COMPONENT_DISPOSITION_PLAN_2026-06-23.md, COMPONENT_THOUGHTWORK_REVIEW_2026-06-24.md, COMPONENT_DOSSIERS_2026-06-24.md | later interpretations | certificates under review |
| git log/show on agents/nous, ledger.jsonl, da42cc7e0, 2f3e4eb6f, 9e189d683, b674a9976 | dating | prompt regime split, supersession |

Not read (by rule): agents/nous/.env or any key file. Presence checked by listing only (absent in worktree).

## 2. Built / Ran / Observed

BUILT: a generator that samples concept triples from a 95-concept dictionary (cross-field bias 0.8,
Coeus-weighted from 03-25, priority queue from 03-28), asks an NVIDIA-hosted LLM for a hypothesis plus
four 1-10 self-ratings, parses the ratings (composite = mean of reasoning/metacognition/hypothesis;
implementability excluded; high_potential = all three >= 7), writes responses.jsonl per run.

RAN: 12 runs with data, 2026-03-24 11:23 .. 2026-03-28 04:00; 5918 entries, 5727 unique triples;
5915 by nvidia/nemotron-3-super-120b-a12b, 3 by qwen/qwen3.5-397b-a17b (the manifest default).
Longest run 53.6 h (20260325_132552, 3030 entries). One dir (20260325_132516) is meta-only, started 36 s
before the next. Cost: never logged (nous.py has no usage/token accounting). Beyond the tree: the forge
ledger holds 1212 Nous-shaped keys attempted 2026-03-31 10:53 .. 04-02 12:43 with no committed Nous
record, including 9 of the 15 priority triples -> uncommitted M4 output, or an unnamed second producer.
The Keeper's agora.intelligence_outputs capture (15502 rows, M1 store) has 0 Nous rows and no heartbeat;
Nous's Agora/heartbeat surface was added 2026-05-13, after every run.

OBSERVED: the forge attempted 5625/5918 entries (95.1%), 2176 of them api_call_failed (forge instrument);
413 entries / 385 keys forged. high_potential 41.8% under the March-24 theorist prompt, 0.84% under the
engineer prompt that ships (same model). Pooled composite->forged AUC 0.755; within forge day 0.519
(null [0.464,0.535], p=0.12). Scorer replay 5918/5918. Lineage re-targeted to forge/v2/nous_t2 on
2026-04-02 (33 runs, 1515 entries, through 04-04).

Why it stopped: not directly evidenced. Strongest dated event is supersession (b674a9976, 2026-04-03).
The resume doc "last activity 03-27, UNKNOWN" is a lower bound from committed run dirs.

## 3. Scripts and headline results

| script | question | result file | headline |
|---|---|---|---|
| nous_run_census.py | what ran, per run | nous_run_census_result.json | 13 dirs/12 with data; 5918 entries; 91 (1.5%) unparseable ratings, 79 in the 800-token run (.bak: 87/87); hp 719 (12.2%); 95/95 concepts used, freq ratio 10.2; 4.1% of C(95,3) |
| nous_forge_join.py | did the score predict forge outcome, separating instrument state | nous_forge_join_result.json | attempted 95.1%; AUC pooled 0.755 / excl. apifail 0.778 / v1 0.576 / v2 0.653 / STRATIFIED BY FORGE DAY 0.519 n.s.; hp by regime v1 41.8% vs v2 0.84%; forge rate by day 8.5%/58.0%/23.4%/10.6%/0/0/<=2.6% |
| nous_gate_trace.py | is the "Nous gate" a capability dependency or orchestration | nous_gate_trace_result.json | hephaestus.py has one input path (_load_nous), 0 Learner/failure-cluster inputs; 6 forge dirs start 4-5 s after a Nous dir; 1212 ledger orphans (03-31..04-02, 1210 scrap/2 forged, 0 records on disk); priority triples 2 committed/11 in ledger; dictionary 95/20/4 (README: 18); nous_t2 33 runs; no keys.py use |
| nous_scorer_replay.py | does the stored score reproduce; what is it | nous_scorer_replay_result.json | 5918/5918 composite/hp/novelty/unproductive match; composite = mean of 3 self-ratings from the same completion; 9 priority triples in ledger 03-31 with no Nous record |
| nous_salvage_reproduce.py | does the techne salvage certificate reproduce; second channel | nous_salvage_reproduce_result.json | build_concepts_index.main() into scratch: rc 0, 95 rows/20 fields/4 mechanisms (28/38/15/14), row-for-row equal to committed index; its docstring still says 18-field; Keeper census: nous rows 0 (pollux 286, erebos 213) |

Run from the worktree root: python engine/necropolis/dossiers/nous_evidence/(script).py. Scripts resolve
the repo root from __file__ (no drive letters). nous_forge_join.py stubs the openai module to import hephaestus.

## 4. Hunt log

HITS
- Contradictory commit: da42cc7e0 (2026-03-25 10:46) replaced the theorist prompt with an engineer prompt;
  high_potential fell 41.8% -> 0.84% with the model fixed; README 20-30% claim was never revised.
- Vacuous gate: filter_results min_score default 0.0; the "Nous gate" checks format, not quality.
- Dead consumer alternative: the disposition plan "forge reads Learner failure clusters directly"
  names an input path that does not exist in hephaestus.py (0 references).
- Instrumentation failure: no run log, no cost, Agora emission added after the last run; 0 rows in the
  second channel; 1212 forge-attempted keys with no Nous record (uncommitted execution).
- Schema/README mismatch: 397B model (3/5918 entries), 18 fields (20), and the techne salvage that
  corrected 18->20 still says "18-field" in its own docstring.
- Config change: max_tokens 800 -> 2048 after run 115258 (87/87 unparseable before rescore.py).
- Supersession: forge/v2/nous_t2 first commit 2026-04-03, runs 04-02..04-04; the March lineage stops there.
- Ledger commit 9e189d683 (04-01, "Pipeline health, backoff fixes") dates the api_call_failed epidemic.

MISSES
- No autopsy row for Nous in engine/ledger/AGENT_AUTOPSIES.jsonl.
- No control arm anywhere: no random-triple or non-Nous seed was ever forged.
- No evidence of what killed the M4 process; no host/daemon log in the tree.
- Coeus weight skew: per-run boosted-slot fraction 0.21-0.37 vs 0.22 uniform, but 0.26 already on 03-24
  before the weight file existed -> inconclusive, not attributable.
- Cost: unrecoverable.

## 5. Primary observations vs later interpretations

| primary (files/ledger/git) | later interpretation | status |
|---|---|---|
| 5625/5918 entries in forge ledger; +1212 orphans | "zombie gate stranding Hephaestus" (disposition plan) | OVERTURNED |
| no Learner input path in hephaestus.py | "forge reads Learner failure clusters directly" | OVERTURNED |
| last committed run 03-28 04:00; ledger to 04-02; nous_t2 04-02..04-04 | "last activity 03-27; stopped, UNKNOWN" (resume) | lower bound, PARTIALLY_UPHELD |
| hp 41.8% (v1) / 0.84% (v2) | "20-30% warrant forging" (README) | prompt-v1 artifact, OVERTURNED |
| stratified AUC 0.519 n.s. | "high-potential" as a quality signal (README, Coeus) | not supported |
| no control arm | "claim-space exhaust" (thoughtwork) | unsupported in either direction |
| 385 forged keys; salvage 08-20 | "realized 0" (thoughtwork/pivot dossier) | PARTIALLY_UPHELD |
| 95/20/4 reproduced | SALVAGE-NOUS certificate | reproduced; docstring defect |

## 6. Residue: executed vs read

EXECUTED here: concepts.py census (twice, incl. the techne build re-run into scratch); scorer replay
5918/5918; combo_key join to the ledger; permutation nulls. READ only (not re-executed): generate_combinations
sampler, priority injection, rescore.py, replay_multiframe.py, nous_t2/nous_t3 code, Agora telemetry.
Data: responses.jsonl (5918 hypothesis texts keyed by triple) is joinable and intact.

## 7. PORTABILITY DEFECTS (recorded, not resolved)

1. No AGENT_AUTOPSIES row for Nous: the doctrine "prior verdict" slot is empty; the reviewer must
   choose which document counts as the death certificate (this pass chose four plus README plus QUEUE).
2. Layer assignment of the prompt change (da42cc7e0): DESIGN here; a second reader could file it under
   CONFIGURATION (it is a string constant) or EXECUTION (it happened mid-series). Verdict-changing.
3. load_bearing semantics: read as "changed the historical answer", but which historical answer
   (resume doc, disposition plan, amended PENDING-REVIEW, thoughtwork) is undefined for a grave with an
   amended record.
4. Classification collision: NO_FAIR_TEST_ON_RECORD, MEASUREMENT_FAILURE and
   SUPERSEDED_BUT_ORGANS_SALVAGEABLE all pass the validator for this stack; the choice lives in
   rationale prose only.
5. Whether supersession by a descendant is ECOSYSTEM_FAILURE or not a failure at all is not stated in
   the taxonomy; filed here as ECOSYSTEM INVALID (load-bearing for the LIMBO status).
6. "dossier" naming collision: pivot COMPONENT_DOSSIERS (June, code unread) vs Necropolis dossier
   (schema-validated); QUEUE.jsonl dossier_exists is ambiguous between them.
7. The Keeper-supplied second channel is a DB capture that this pass cannot re-query; its evidentiary
   weight for a M4-only agent is "absence in a channel Nous never wrote to". Doctrine does not say
   whether such absence counts as EXECUTION evidence or INSTRUMENTATION evidence; recorded under both.
8. validate.py path resolution: when run from a scratch copy the cited-path notes report 10/37
   resolving (relative to the scratch root); all 37 resolve in the worktree (checked by existence test).
   The resolver also extracts "data/priority_triples.json" from a parenthetical as a separate path.
9. Certificate review enum: a certificate that is correct in substance but carries a defect in its own
   source (the "18-field" docstring) can only be PARTIALLY_UPHELD, since UPHELD forbids listing errors.
10. Frankenstein fields: SCHEMA requires changed_design as an array; the charter A/Y/M/C->C'/R/kill
    template is prose. Encoded here as four array items; another reader might split differently.

## 8. Final validate.py output (scratch copy, never run in the worktree)

Scratch: (scratchpad)/nous_validate = copy of engine/necropolis with nous.dossier.json dropped in
dossiers/. First run: 2 schema errors (descendant_candidate.changed_design and preserved_mechanism must
be arrays) + 2 STALE regenerations of ORGANS.jsonl / COUNTERFACTUAL_HISTORY.jsonl in the scratch copy.
After fixing the arrays:

```
=== Necropolis validate.py ===
schema:   SCHEMA.json OK
roster:   48 agents, 0 duplicate ids
dossiers: 6 files checked
selftest: FAILED-classification rejection FIRED (ok)
organs:   55 organs in ORGANS.jsonl; executed_by_necromancer=true for 13
history:  29 counterfactual rows (mistake -> symptom -> verdict -> corrected cause -> repair -> post-repair); 1 with a repair filed
monsters: 2 files checked; kill_condition-rejection self-test FIRED (ok); repair-without-counterfactual self-test FIRED (ok)
note:     nous.dossier.json: stack 6 INVALID / 1 NOT_EXAMINED; fair_test=UNFAIR; primary=DESIGN_ERROR; certificates OVERTURNED,PARTIALLY_UPHELD,PARTIALLY_UPHELD,OVERTURNED,OVERTURNED,PARTIALLY_UPHELD,NOT_REVIEWED

ALL GREEN
```

Note for the Keeper: ORGANS.jsonl and COUNTERFACTUAL_HISTORY.jsonl in the WORKTREE were not touched;
validate.py will regenerate them (organs 39 -> 55 with the Nous residue) when the Keeper runs it.
ASCII check (grep -nP for bytes above 0x7F under LANG=C.UTF-8) over this directory and nous.dossier.json
returns nothing.
