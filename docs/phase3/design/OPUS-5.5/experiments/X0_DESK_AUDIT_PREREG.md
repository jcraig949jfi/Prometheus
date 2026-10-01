# X0 -- Desk audit of historical apparatus nulls and false positives (PREREGISTRATION)

Status: FROZEN before any coding of items. Author: Epimetheus (OPUS-5.5). Date 2026-10-01.

## Question

Which repair would have most cheaply made each historical failure interpretable? Specifically: how often would a
SECOND SUBSTRATE have been the cheapest repair, and how often was a shared substrate the element that produced a false
positive or false agreement? The answer decides between two Phase 3 architectures that the critic panel's judge left
open: depth-first on one primary substrate (second substrate on measured triggers) versus an early multi-substrate
portfolio.

This is a zero-compute experiment on the fossil record. It uses no engine source for salvage purposes.

## Population (frozen)

All rows of docs/phase3/design/OPUS-5.5/evidence/historical_profiles.jsonl (353 rows, produced by workflow
wf_09904c9a-c86 readers from the four intake packages and their cited artifacts) whose primary_class is one of:
organism_insufficiency, world_insufficiency, pressure_insufficiency, search_insufficiency, ruler_insufficiency,
statistical_insufficiency, implementation_defect, provenance_defect, false_positive, other. Count at freeze: 210 items.
Excluded: instrument_positive, survives_as_anomaly, true_negative, hypothesis_failure (no repair question).
Item key: "<group>:<id>".

## Coding (two questions per item)

A. CHEAPEST_REPAIR: the single cheapest change that would have made the result interpretable (a real positive, an
   interpretable null, or a caught false positive), one of:
   WORLD (demand proof, admission baselines, world redesign), SEARCH (budget, acceptance policy, reachability
   estimate), RULER (qualification, planted control, baseline ladder, leak audit), CAPACITY_SAME_SUBSTRATE
   (constructive proof or added affordance within the same substrate), SECOND_SUBSTRATE (only a different substrate
   could settle it), STATISTICS (power, unit, multiplicity), PROVENANCE_IMPLEMENTATION (code or custody fix),
   INDEPENDENCE (independent author, model family or reimplementation), OTHER.
B. SHARED_ELEMENT (for false positives, false agreements and any item where several results agreed spuriously):
   the element shared between the producer and the check that produced the error, one of: SUBSTRATE,
   RULER_OR_NULL_CODE, MODEL_FAMILY, AUTHOR, PROMPT, DATA, WORLD_GENERATOR, NONE.

Coders read the row and, where needed, the cited artifact. Each code carries a one-line reason.

## Decision rule (frozen; taken from the judge's ruling, wf_dfa6b90b-886)

    p2 = fraction of coded items with CHEAPEST_REPAIR = SECOND_SUBSTRATE
    s  = fraction of items coded under B (SHARED_ELEMENT != NONE) whose SHARED_ELEMENT = SUBSTRATE

    p2 < 0.10 and s < 0.25          -> DEPTH-FIRST CONFIRMED (one primary substrate with lattice; second on triggers)
    p2 > 0.30                       -> EARLY PORTFOLIO FAVOURED (second substrate inside the 90-day MVP)
    otherwise                       -> INTERMEDIATE (depth-first; probe kernel in month 2; trigger review at day 90)

## Reliability control

A second coder, blind to the first coder's labels, codes the deterministic sample of keys with
sha256(key) mod 5 == 0 (41 items at freeze). Cohen's kappa on question A is reported. If kappa < 0.40 the outcome is
INDETERMINATE and the INTERMEDIATE architecture applies by default.

## Known limitations (declared before running)

- Both coders are Claude-family agents (independence class I1); no cross-family coder is available in this session.
- Items are coded from reader digests and cited artifacts, not by re-execution.
- The population inherits the readers' primary classifications; reclassification errors propagate.
- 'Cheapest' is judged qualitatively; there is no cost model per repair.

## Outputs

experiments/X0_codes.jsonl (all codes), experiments/X0_RESULT.md (counts, p2, s, kappa, outcome).
