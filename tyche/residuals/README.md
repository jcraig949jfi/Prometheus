# tyche/residuals/ -- the residual catalogue (CWO 2026-09-30, TYCHE CURRENT)

Phenomena that Prometheus experiments observed and left unexplained,
contradictory, weak, unreplicated, parked or instrument-ambiguous, each
with provenance to the generating experiment. The catalogue asserts
nothing about any phenomenon's truth; it is the frontier Tyche searches.

    catalogue.py        schema + validate(): the ONLY admission rule
                        (path exists at sha; quote is an exact substring;
                        raw_rows exist at the pinned ref)
    import_artemis.py   deterministic import of Artemis harvest D1-D5
                        entries of kind anomaly / contradiction /
                        parked-experiment (links.artemis keeps the H-id)
    drafted_survey.jsonl  entries drafted by a survey agent for phenomena
                        Artemis's harvest does not hold (39); admitted
                        only through validate()
    build.py            assemble v0 at a pinned ref
    v0/CATALOGUE_v0.jsonl  admitted entries
    v0/REJECTED_v0.jsonl   rejected entries with the reason
    v0/SUMMARY_v0.json     counts, ref, inputs

v0 (ref 7510264263a8e876cc5097c843e6b6815746ce63): 122 admitted (83 from
Artemis, 39 surveyed), 10 rejected (quote not in the cited file at the
cited sha: 8; no parseable source: 2), 30 seats. 19 entries cite
committed raw rows; 39 carry provisional behaviour tags.

Known limits: behaviour_tags are model-assigned descriptors for the NEXT
clustering assay and are not evidence; the importer's "seat" field is
parsed from prose and a few values are not seat names (e.g. "Agent");
imported Artemis entries carry no raw_rows or tags yet; a validated quote
proves the text exists at that sha, not that the phenomenon is real.
Tests: tyche/tests/test_residuals.py (real quote admitted; fabricated
quote, wrong sha, missing rows, bad kind rejected).

v0.1 (ref 282f01c45): enrich.py applied an agent-drafted enrichment
(enrich_artemis_with_flags.jsonl) to the 83 imported entries -- tags,
raw rows (re-validated by build.py), engine, seat fixes where the fix is a
real seat name; 31 entries carry a verbatim `framing_note` (a reader's
flag that the source does not support the entry's framing -- e.g. already
answered, numbers misquoted, pattern on too little; not a verdict).
Result v0_1/: 122 admitted, 10 rejected, 67 with committed raw rows, 122
tagged. cluster.py -> v0_1/CLUSTERS_v0_1.json: 17 cross-engine niches
(tag present in >= 3 engines), led by context_dependence (14 engines),
measure_disagreement (10), control_shows_effect (9). Work tags
(untested_precondition 39, control_never_run 10) mark missing experiments
and never form niches. Per the operator's v1 directive the natural
residuals are NOT perturbed until v1 gate 6 is shown.
