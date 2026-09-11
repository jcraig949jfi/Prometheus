# Coeus backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-11. **FROZEN** at 11 items on the day the seat parked.

ANNOTATION, 2026-09-11 (operator ruling PARK): COEUS-XL-01 is ANSWERED --
PARK. COEUS-01 through COEUS-05 were either done differently or are
CLOSED by the park; the disposition of every row is marked below. No
filler was added to reach the schema's 20-item floor: the ruling forbade
manufacturing work to keep the seat alive, and a floor is not a reason to
invent items. This file is not rewritten again unless the reactivation
condition in RESPONSIBILITIES.md section 3A is met.

    COEUS-XL-01  ANSWERED 2026-09-11: PARK.
    COEUS-XL-02  OPEN and EXTERNAL. Kairos nominated, Mnemosyne rules,
                 Coeus disqualified. Packet delivered.
    COEUS-01/02  CLOSED-NOT-DONE. Annotating agents/coeus/README.md and
                 manifest.yaml in place was the plan while the seat
                 expected to continue. The park makes a superseding
                 document the better artifact: FINDINGS_2026-09-11.md F1
                 records all twelve contradictions with the artifact
                 values beside them. Editing a dead seat's README to point
                 at its own autopsy is churn; the autopsy is findable.
    COEUS-03     DONE, and larger than specified: science/trace_defects.py
                 plus science/ledgers/defect_trace_2026-09-11.json.
    COEUS-04     DONE: prompts/2026-09-11_park_routing/03_TO_Hephaestus...
    COEUS-05     DONE: prompts/2026-09-11_park_routing/02_TO_Mnemosyne...
    COEUS-06/07  SUPERSEDED by residue/OUTCOME_VARIABLE_HYGIENE.md, which
                 states the invariant once instead of designing a fixed
                 Coeus around it. The ruling forbade the second thing.
    COEUS-08/09  NOT DONE and left open as named gaps, not as work: the
                 distinct-tool denominator census and the enrichment
                 directive census by null-position. Both are cheap; both
                 need a seat that is running.

The original text follows, unedited.

Currency: 2026-09-11. PROVISIONAL and BELOW THE SCHEMA FLOOR. The schema
requires 20 to 60 items; this file holds 11. The archaeology
(ARCHAEOLOGY_2026-09-11.md) left zero executable science items: the seat's
only descendant belongs to the Necropolis and is RESOURCE-gated on a forge
that has been dead since 2026-05-28, and the seat itself is BLOCKED on
COEUS-XL-01. Inventing nine more rows to reach the floor would be
fabrication. This file is rewritten to the schema on the day
COEUS-XL-01 is answered with REVIVE; if the answer is PARK or RETIRE it
is annotated and frozen.

The first four items are the ones startable today; they are documentation
repair inside this seat's own paths plus one defect report, and none of
them needs a decision from anybody.

COEUS-XL-01 | Decide the seat: REVIVE with a re-premised charter, PARK, or RETIRE with machinery absorbed, given the Necropolis MEASUREMENT_FAILURE disposition and a dead forge | ENGINE | program | XL | operator decision NEW: "does Coeus exist as a seat, and if so with what consumer" (the seat's own recommendation is PARK unless a consumer for outcome-variable hygiene is named first; RESPONSIBILITIES.md section 4) | the decision id in archaeon/docs/expansion/DECISIONS.md, and either roles/Coeus/prompts/<date>_charter/ with a MANIFEST or a dated PARKED/RETIRED annotation at the top of RESPONSIBILITIES.md
COEUS-XL-02 | Decide who runs the LAW N13 independent falsification pass on coeus.dossier.json, since the subject seat has declared itself disqualified | EVIDENCE | program | XL | operator decision NEW: "which seat is the second lens on the Coeus autopsy" (routed by the Necropolis Keeper; Coeus is conflicted, ARCHAEOLOGY section 5) | a named seat in engine/necropolis/QUEUE.jsonl or a comms delegation, and the re-run result recorded against the dossier's unresolved_questions
COEUS-01 | Annotate agents/coeus/README.md in place with dated supersession markers: the stale findings table, the implementability sign flip, the four never-executed methods, the wrong rlvf_fitness path, and a pointer to the Necropolis dossier; never rewrite the original text | ENGINE | program | S | none | the annotated README with a dated marker beside each superseded block, and the diff showing no original line was deleted
COEUS-02 | Annotate agents/coeus/configs/manifest.yaml where it advertises causal-learn, lingam, dagma, dowhy and tigramite as the method stack, recording that the shipped artifact is method='lasso_regression' | ENGINE | program | S | none | the annotated manifest with the dated marker and the verifying command in the journal
COEUS-03 | Commit the artifact census that backs ARCHAEOLOGY section 1 and 3 as a re-runnable script plus its output, so the counts (95 / 50 / 1009 / 0 confounders / 4031 / 7 rows on n<=4 / sum n_tasks 37035 vs 92) can be reproduced without trusting this file | EVIDENCE | program | S | none | roles/Coeus/science/census_shipped_artifacts.py and roles/Coeus/science/ledgers/artifact_census_2026-09-11.json carrying the base SHA it read
COEUS-04 | Post the D3 defect report to Hephaestus: rlvf_fitness.py L82-96 consumes survival_rate with no minimum denominator (15 of 97 concepts have n_tasks < 10; a 1-of-1 concept contributes the maximum weight) and n_tasks counts tool-task pairings, not the 92 independent tasks | ENGINE | program | S | none | the committed body file under roles/Coeus/prompts/2026-09-11_hephaestus_rlvf/ with a MANIFEST, and the comms message id from python -m comms post --kind report
COEUS-05 | Post to the Necropolis Keeper the three defects found today (D1 sign flip, D2 stripped denominators, D3b units), for the dossier's residue and unresolved_questions sections, flagged as reported by the conflicted subject seat | EVIDENCE | program | S | none | the committed body file with MANIFEST and the comms message id; the dossier row is the Keeper's to write, not this seat's
COEUS-06 | Write the minimum-n and units fix as a PROPOSAL for the goodhart_indicators emitter in agents/coeus/src (publish n_tasks and n_survived beside every rate; refuse to emit a verdict string below a declared eligible count; rename the pairing count), without running it | ENGINE | alpha | S | COEUS-XL-01 (no code in this seat runs before the seat exists) | a design note under roles/Coeus/science/ naming the threshold, the INDETERMINATE branch, and the attainable range
COEUS-07 | State the preregistration for any future Nous-to-forge scorer as a committed file: hold out by FORGE TIME not by Nous run, exclude api_call_failed and validation-runtime rows from y rather than scoring them 0, publish the chance floor with a 500-draw permutation null, and carry a batch-id decoy as the positive control | EVIDENCE | alpha | S | none (a document; it commits this seat to a gate before any data is touched) | roles/Coeus/science/PREREGISTRATION_scorer_v2.md committed BEFORE any scorer work, with its own commit so the order is in git history
COEUS-08 | Measure how many DISTINCT tools back each concept's adversarial n_tasks, closing the D3b gap this seat opened and did not close | EVIDENCE | alpha | S | COEUS-XL-01 | roles/Coeus/science/ledgers/adversarial_denominator_census.json with the command and the sha256 of the graph it read
COEUS-09 | Classify the 4031 enrichment blocks by the strength of the directive they carry ("make this the core architectural pattern" vs "do NOT use this") and record how many rest on a concept whose forge_effect is inside the null, as a residue measurement of what was actually injected into the forge prompt | EVIDENCE | alpha | M | COEUS-XL-01 | roles/Coeus/science/ledgers/enrichment_directive_census.json and the histogram in the journal
