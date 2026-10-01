# AUDIT Z5 -- provenance of the 16 historical triplicates

Auditor: Z5 subagent for Hecate[m1-dd0c3882]. Written 2026-10-01T01:43Z
(clock). Worktree HEAD 7ab70b843. Read-only: no model/API calls, no git
writes. Rebuilds and reruns went to the session scratchpad (Z5/) only:
rebuild.py (corpus.build + select.select with OUT_DIR redirected) and
compare.py (program.json vs frozen selection vs rebuilt corpus vs raw
source lines).

## Verdict

PASS on identity and wiring: all 16 match their historical records with
zero drift; provenance.source is "hephaestus" on every historical record;
the selection reruns byte-equal; the meta units are the stated ones.
Three findings qualify that pass (F1-F3 below), and none of them is drift.

## 1. Per-program table (program.json vs source)

Checks per program (all 16 pass all of them):
- id, key, stratum, concepts, history equal selection.json (frozen) AND
  equal a fresh corpus rebuild.
- provenance (minus the added selected_by) equals both of those.
- the raw line at sourceArtifact re-sorts to the same key. historicalId
  equals the ledger "key" field verbatim.
- the field, mechanism and short_description of each concept equal
  agents/nous/src/concepts.py (the worktree copy differs from the
  F:/Prometheus copy only in CRLF line endings).
- history is recomputed from the raw lines: nous_composite_max and
  nous_unproductive_any come from the upstream_nous lines, and forged
  comes from the ledger_lines statuses.
- the humanreadable pointer exists on disk.

| HT id | stratum | source (historicalId = ledger key) | hist. verdict (ledger) | Nous novelty | match |
|---|---|---|---|---|---|
| HT-056d3ac561 | S1 | ledger.jsonl#L3859 | scrap: api_call_failed | novel | MATCH |
| HT-8a87057933 | S1 | ledger.jsonl#L4282 | scrap: api_call_failed | novel, unproductive | MATCH |
| HT-a9e2ba7618 | S1 | ledger.jsonl#L1480 | scrap: trap_battery_failed acc=20% | novel | MATCH |
| HT-974471f045 | S2 | ledger.jsonl#L1448 | forged, accuracy 0.20 | novel | MATCH |
| HT-55162c0ac0 | S2 | ledger.jsonl#L618 | forged, accuracy 0.20 | novel | MATCH |
| HT-37e311ce05 | S2 | ledger.jsonl#L866 | forged, accuracy 0.267 | novel | MATCH |
| HT-2a8a3aedeb | S3 | ledger.jsonl#L2160 | scrap: api_call_failed | novel | MATCH |
| HT-e106e1603b | S3 | ledger.jsonl#L2240 | scrap: api_call_failed | novel | MATCH |
| HT-321a8fd8e0 | S3 | ledger.jsonl#L714 | scrap: trap_battery_failed acc=40% | novel | MATCH |
| HT-e743909f97 | S4 | ledger.jsonl#L4971 | scrap: runtime_error (UnboundLocalError) | novel | MATCH |
| HT-47f4c02be4 | S4 | ledger.jsonl#L6417 | scrap: trap_battery_failed acc=34% | novel | MATCH |
| HT-ae38c641b1 | S4 | ledger.jsonl#L6449 | scrap: trap_battery_failed acc=37% | novel | MATCH |
| HT-79e904e13a | S5 | ledger.jsonl#L489 | scrap: trap_battery_failed acc=27% | novel | MATCH |
| HT-71b65251aa | S5 | ledger.jsonl#L1736 | scrap: trap_battery_failed acc=38% | novel | MATCH |
| HT-faa9277e02 | S5 | ledger.jsonl#L6368 | scrap: trap_battery_failed acc=26% | novel | MATCH |
| HT-5b0b3ebb8d | S5 | ledger.jsonl#L3012 | scrap: api_call_failed | novel | MATCH |

All 16 sourceArtifacts are ledger lines, and every one has at least one
upstream Nous line. The HT-<sha256(key)[:10]> id is minted by Hecate. It
sits beside the historical id, which is kept verbatim as historicalId,
and does not replace it. This complies with the charter rule "do not
rename historical ... IDs".

## 2. Provenance field coverage

| record | provenance.source | result |
|---|---|---|
| 16 program.json (top level) | "hephaestus" + sourceArtifact + historicalId + upstream_nous + ledger_lines | OK 16/16 |
| hecate/schema.py validate_provenance | requires sourceArtifact + historicalId when source=hephaestus | enforced |
| 16 DOSSIER.md "ORIGINAL PROVENANCE" | source hephaestus, artifact, historicalId | OK (sampled HT-8a87057933) |
| hecate/index/nodes.jsonl | 16 historical_artifact nodes + 16 triplicate nodes carry it (32 lines) | OK |
| hypotheses/lenses/experiments inside programs | no provenance field; derivation edge = triplicateId + passId | ACCEPTABLE (see F4) |
| hecate/meta/arms_v1.jsonl (40 rows) | no provenance field; triplicateId only | ACCEPTABLE (see F4) |
| matcher/detector rows | no provenance field. Matcher distractors are drawn from selection.json, as preregistered | OK |
| hecate/autopsy reach_rows (62) | items are SYS-* alien-assay systems, not historical triples | N/A, correctly not labelled hephaestus |
| FLOW.json / REACH.json / RESULTS_v1.json | aggregates; no per-triple provenance | N/A |

No record carries any source label other than "hephaestus" for a
historical triple. No historical file was modified: the worktree
ledger.jsonl and all 12 Nous responses.jsonl are sha256-identical to
F:/Prometheus.

## 3. Selection reproducibility

- Rebuilt corpus (worktree sources): LF sha256 d78f9d66...313885, 6939
  triples. This equals CORPUS_RECEIPT.json and PREREG.md.
- select.select at seed 20260929 gives the 16 ids in the frozen order and
  strata. The eligible counts are S1 2346, S2 385, S3 554, S4 941, S5
  6939, and the cuts are 5.33/7.33, all as stated in PREREG.md. The
  rerun JSON equals selection.json (deep equality). The manifest hashes
  of FROZEN_IDS.txt, PREREG.md and selection.json all verify.
- corpus.py and select.py are unchanged since the freeze commit
  e0bd2e312. The first pass content came later, in 00c99410b, so the
  freeze-before-passes claim holds.
- Not verifiable from git: "the rule was written before the selector
  first ran". The rule and its output landed in the same commit
  (e0bd2e312), so this rests on the author's statement.
- SCOPE CAVEAT, see F1. The same code run against F:/Prometheus does NOT
  reproduce the selection. That tree has 10105 Nous responses and 9397
  triples, against 5918 and 6939 here. Its corpus sha is ba891e30...,
  the top-decile cut there is 7.0 rather than 7.33, and S1 starts with
  HT-c56fb19bc4.

## 4. Meta-experiment units

hecate.meta.units recomputes these units from selection.json:

  0 HT-e106e1603b  1 HT-79e904e13a  2 HT-faa9277e02  3 HT-2a8a3aedeb
  4 HT-ae38c641b1  5 HT-8a87057933  6 HT-056d3ac561  7 HT-5b0b3ebb8d

All 40 arms_v1 rows match the recomputed rows on (unit, arm),
triplicateId and concept order. In every row, the sha256 of the
re-rendered prompt equals that row's recorded prompt_sha256 (0
mismatches). The units are the stated triplicates.

Composition (a consequence of the preregistered seed, not an error):
S1 x2, S3 x2, S4 x1, S5 x3, S2 x0. None of the three forged triplicates
is a meta unit. Five of the 8 units (e106, 2a8a, 8a87, 056d, 5b0b) were
historical api_call_failed scraps, which means Hephaestus never actually
evaluated them (see F2).

## 5. Findings

F1 (MEDIUM, scope) The corpus is the git-tracked Nous history, not the
whole Nous history. corpus.py globs agents/nous/runs/*/responses.jsonl
under its own ROOT. In a worktree, that finds only the 12 tracked runs.
F:/Prometheus also has 11 gitignored runs, 20260328_052541 through
20260402_090737, which hold 4187 more responses and 2458 Nous-only
triples. RESPONSIBILITIES s2 quotes the 5,918 figure, and PREREG says
"rebuilt byte-identically from tracked sources". Neither document states
that newer historical Nous runs exist and were excluded. Effects:
(a) The 16 are a valid draw from the tracked sub-corpus, not from the
full history.
(b) One frozen triple's history is incomplete. HT-8a87057933 has
nous_n 3 in the full tree, not 2, although its composite and
unproductive flags are unchanged.
(c) Anyone who reruns `python -m hecate.corpus` in F:/Prometheus gets a
different hash and a different 16.
Fix: one sentence in PREREG/README pinning the corpus to tracked runs.
Optionally, set ROOT explicitly. No re-selection is needed.

F2 (MEDIUM, interpretation) The historical "verdict" is mostly not a
verdict. Five of 16 ledger outcomes are api_call_failed, and one is a
forge-code UnboundLocalError. Six of 16 were therefore never assessed by
Hephaestus. This includes 2 of the 3 S3 "nous_high, never forged"
picks. Corpus-wide, 2861 of 6939 triples have only api_call_failed
ledger reasons, as do 149 of the 554 S3-eligible triples. "Never forged"
mixes "forge failed" with "forge never ran". program.json keeps the
reason string, so this can be recovered. However, any OLD-vs-NEW
comparison (the Hephaestus 2.0 pilot) or any reading of S2 vs S3/S4 as
historical success vs failure must exclude these six or label them.

F3 (LOW-MEDIUM, dropped fields) The following historical fields are not
in program.json:
- the ledger fields accuracy, calibration, margin_*, frame and status.
  ledger_reasons is split at " (", which drops the "acc=/cal=/ncd_*"
  numbers.
- the Nous fields response_text (the original mechanism text), ratings
  (reasoning/metacognition/hypothesis_generation/implementability),
  novelty label, concept_fields and triple indices.
- the humanreadable report body. Only a pointer is kept.
Everything is recoverable through upstream_nous, ledger_lines and
humanreadable. The pass prompt (pass0_3_v1.md) deliberately forbids
reading agents/nous and agents/hephaestus, so Hecate's passes are
independent of the original text. This is a design choice, not a loss.
Two points matter later:
(a) "forged" in S2 means forge accuracy 0.20-0.27 on the trap battery.
That is a pass of the old gate, not a strong result. Without accuracy,
S2 reads as success.
(b) The historical familiarity note is saturated. Nous labelled 5462 of
5918 responses "novel" and only 4 "existing". It also labelled all 16
"novel". Meta v1's detector found 0 of 399 UNFAMILIAR. The two rulers
are saturated in opposite directions on the same triples. This supports
the CWO-B withdrawal of the novelty ruler. The dropped label carries no
signal, so dropping it cost nothing, but the contrast is worth one line
in the autopsy.
No original mechanism text was needed for any decision taken so far.
It will be needed for the prior-art pass and the OLD-vs-NEW comparison.

F4 (LOW, charter form) Derived items carry back-pointers, not
provenance. Hypotheses, lenses, experiments and meta arm rows link to
the program only through triplicateId (+ passId). They have no
provenance.source (charter: "generated", attributed to Hecate) and no
derived_from. The derivation edge exists transitively through the
program's provenance, so nothing is unrecoverable. Strictly, though, the
charter asks each new hypothesis or experiment to be attributed to
Hecate "while retaining an explicit derivation edge". schema.py already
defines "generated" + derived_from, but it applies that only to program
provenance. Adding a pass-level or item-level attribution would close
this gap.

F5 (INFO) No drift found anywhere: no concept, field, mechanism,
description, key, historicalId, score or forged-flag drift in any of the
16. No historical file was edited. The charter's two example triples are
correctly outside the 16.

## Reproduce

    python <scratch>/Z5/rebuild.py wt     # corpus sha d78f9d66..., 16 ids
    python <scratch>/Z5/rebuild.py main   # F:/Prometheus: ba891e30..., differs (F1)
    python <scratch>/Z5/compare.py        # 16 x MATCH
