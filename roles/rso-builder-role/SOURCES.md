# RSO design sources -- where the current Phase 3 design lives

Currency: 2026-10-03 (Achilles, at setup). Work from these files, never from memory or a summary. When a newer
artifact supersedes one below, the seat that finds it adds a dated line here; nothing is deleted.

## A. Required before S1/S2 work (the agreed direction)

1. Latest agreed synthesis / implementation direction -- docs/phase3/synthesis/ENCELADUS-DIONYSUS-v0.4/
   (Enceladus, 2026-10-02; branch commit 3bd02f393, on main via Achilles's merge of 2026-10-03):
   - README.md                          reading order and the decision in brief
   - SYNTHESIS_AND_DECISIONS_v0.4.md     decisions D01-D11 and their resolutions
   - NEXT_ROUND_PLAN_v0.4.md             the S1-S5 slice: question, ownership/sequence (s2), minimum
                                         contract to freeze at S1 (s3), acceptance matrix T01-T08 and
                                         E01-E06 (s4), fresh challenge protocol (s5), budget proposal (s6),
                                         what follows if earned (s7)
   - VALIDATION.md                       what was actually rerun and what was not
   Its README still says "REVIEW_READY; NOT AGREED": that was its state when written. The acceptance is
   recorded in item 2.

2. Final closure review -- docs/phase3/closure/FABLE-5.1/CLOSURE_REVIEW_v0.4.md (Dionysus, FABLE-5.1;
   written 2026-10-03 UTC; commit 09dc8c38b; the operator's prompt as received at
   roles/Dionysus/prompts/2026-10-03_closure_review/). Verdict ACCEPT_WITH_MINOR_AMENDMENTS. Section C:
   mandatory amendments C1-C5, to be written into the S1 contract. Section F: the first implementation
   slice and the reviewer's role at S1/S3/S4. Section G: after C1-C5 are in S1, no further broad
   architecture or harness design review is required before implementation; the remaining conditions
   are the operator's (authorize the caps, name the anchor keeper). The sequence: freeze S1 -> build S2 ->
   first-sight attack S3 -> one repair/closure S4 -> S5 report -> one actual native witness.

## B. Supporting design and hardening (read when a task needs them; not at every boot)

These are REFERENCE AND ADVERSARIAL CORPORA. They are not competing production RSO implementations, and
builders do not concatenate their code, tests or verdict policies (NEXT_ROUND_PLAN_v0.4 s1: the two
harnesses are examples and regression corpora, not oracles for each other).

3. Fable hardening -- docs/phase3/hardening/FABLE-5.1/ (Dionysus, 2026-10-02; delivery 3669bc7f2):
   00_README.md; 01_SYNTHESIS_TWO_REVIEWS_AND_HARDENING_v0.2.md; 02_HARDENING_DESIGN_v0.2_FABLE.md (v0.2
   hardening design); 03_TEST_HARNESS_SPEC_FABLE.md; harness/ (reference harness); attack/ (attack corpus,
   including the first-version attack and closure reader); fire_test.py, check_hardening.py,
   RECEIPT_fire_test.json; MANIFEST.md.

4. Astra hardening -- docs/phase3/reviews/ASTRA-6.0/rso-v0.2/ (Enceladus/ASTRA-6.0, 2026-10-02; commit
   9af020b24, on main via the same merge): HARDENED_DESIGN_v0.3.md; HARDENED_TEST_PLAN_v0.3.md;
   reference_harness/ (finite.py, checker.py and their tests); VALIDATION.md, VALIDATION_RESULTS.json;
   reports/Comparison_and_decisions.md. The earlier round is rso-v0.1/.

5. Earlier Phase 3 design and review: docs/phase3/design/ (architect packages, incl. ASTRA-6.0 and
   OPUS-5.5), docs/phase3/review/FABLE-5.1/ (the RSO wind tunnel v0.1 and race-car portfolio R0-R9),
   docs/phase3/PHASE3_CHALLENGES.md, docs/phase3/PHASE3_ARCHITECT_PROMPT.md.

## C. Historical failure corpus (only when a task needs historical counterexamples)

6. Phase 1/2 forensic intake: docs/phase3/intake/{sisyphus,tantalus,tityos,ixion}/ -- REPORT.md,
   artifact_index.jsonl, engine_index.jsonl, per-seat notes (ixion adds an inference dependency map and an
   institutional timeline). docs/phase3/design/ASTRA-6.0/FAILURE_TO_GATE_MAP.md and its evidence/*_AUDIT.md
   map past failures to gates. Doctrine of past failures: aporia/doctrine/critical_memories.md. Do not
   re-crawl; cite the intake packages and spot-check against the underlying artifacts.
