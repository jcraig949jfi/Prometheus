# E-003 (C-001 attribution arc) -- BEE leg, Bellerophon

Spec: ANCESTRY_PREREG_v4 + v5 delta through C10 at the owner freeze (archaeon/attribution-arc-2026-09-28 @ 028f2eff8,
Archaeon #920). C11 (constant-only COMPUTED labels) was adopted AFTER production and the production agreement FAIL;
the owner tracer and outputs are unchanged by it.
Commission: comms #811 / #817 / #824 / #833; accepted in #919. Run: r022153 (VM_COPY, SHARED, OPCODE mutation, INC).
Independence: this seat's tracer is built from the prereg TEXT only. archaeon/attribution/bee_ref_tracer.py and
ops/.../reftracer/ref_tracer_bee.py are NOT read before the first agreement run.

| step | status | receipt |
|---|---|---|
| 1 pin frozen harness 16fc6c2a (4 pins verified at import); reproduce preserved births | DONE: 32,827/32,827 bit-for-bit | receipts/REPLAY_r022153.json |
| 2 shadow tracer (v4 s1 + v5 + C2 readings); value-checked vs the frozen VM | DONE; FROZEN (FREEZE_MANIFEST.json) | tools/bee_tracer.py |
| 3 fixture pack (bee_fixtures.py @028f2eff8, stub harness; Archaeon tracer never loaded) | DONE: 28/28 PASS on the frozen tracer | receipts/FIXTURES_FREEZE.json |
| 3b review3/review4 cases | covered by fixtures (R3 CX-A..D,G -> K8/K11-K14; CX-F -> K15; CX-E pair-only, K10/K10c for SHARED; R4 D1-D5 -> K1/K4, K22, K24, K23, K3). The review scripts embed reviewer tracers and were not executed (independence) | |
| 4 world replay with persisted origin vectors, tracer on every interaction | DONE (dry): rows bit-for-bit, 123,210 interactions value-equal, 0 mismatches | receipts/DRYRUN_TRACED_WORLD_r022153.json |
| 5 Q4 (isolated + host-assisted C4.5), R1 arms / Q8c / whether, C7.2 flip, R5 completeness, verdict in code, v0 round-trip | DONE as a DRY pipeline validation; v0 round-trip PASS 32,827/32,827 | receipts/DRY_RESULTS_r022153_pipeline_validation.json |
| 6 production | DONE under GO aa958093 / GO v2 (#974): start receipt PASS, sealed outputs, production s4.3 (post-C11 re-run PASS + fresh set 2 PASS, exact) | receipts/PRODUCTION_START_RECEIPT.json, production/PRODUCTION_SEAL.json |
| 7 result | VALIDATED under readings A and B (not reading-dependent) | E003_BEE_RESULT.md |

DRY RUN DISCLOSURE. The full pipeline was run once on r022153 before the freeze, to validate it: every number in
receipts/DRY_RESULTS_* is DRY and is not a production result.
- One change was made AFTER seeing that output: NO_MATERIAL was removed from the class GATES (R1 says it is reported, not
  gated). The dry analysis had gated it at flip coverage 1/3 over 3 loci; this change is OUTCOME-DETERMINATIVE
  (see E003_BEE_RESULT.md s1a).
- Later pre-production code changes, each tied to a ruling and recorded in FREEZE_MANIFEST.json refreeze:
  * #951 (4): coverage denominator + TIED;
  * #956 (B-P1): the performer-kind probe and the A/B report.
  * tools/agreement_export.py entered the manifest at the #951/#956 refreeze without its own refreeze record; its
    hash (a320d94b) is the one the agreement seals and both GO records bind.
- Post-production additions (POST-HOC, labelled; no frozen file changed): tools/posthoc_q4_relational.py
  (DEF-BEL-004).
- Production re-runs every step under the frozen hashes after the GO record.

Declared readings (full list in tools/e003_analysis.py docstring):
- identification = MOVE + flip not FAILED (sample) + 0 R1 changes; dep-vacuous loci counted apart;
- EMPTY window = (CONST, empty); R4 in_pad vs C2 CHOICE 9: unsupplied input bytes are (CONST, zero), following C2 and
  fixture K26;
- the post-dominator ctrl scope and the Q5 drift null are NOT implemented (secondary / descriptive);
- Amendment A says 29 fixtures; the pack file at 028f2eff8 defines 28 entries (K3 = K25 is one entry).

Inputs (copied byte-exact from the arc branch): inputs/r022153.config.json and inputs/r022153.births.jsonl.gz
(sha256 8c583679a648f3391bb46824fc114e88934ba89162f216a507830b7633af3483).
