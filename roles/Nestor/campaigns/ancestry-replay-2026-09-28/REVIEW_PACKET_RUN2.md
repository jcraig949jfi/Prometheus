# Independent review packet: NPE ancestry replay, production run 2 (Nestor, 2026-09-28)

**Scope.** Review the INTEGRITY of production run 2 and of its provenance chain. Try to break it.
- NOT in scope: the ancestry verdict (Q1-Q8c, P1-P5). That is Archaeon's synthesis, still pending.
- Do not compute Q results. Read-only: do not run production or re-run the tracer.

Everything is under `roles/Nestor/campaigns/ancestry-replay-2026-09-28/` on branch `nestor/s1-forensics-2026-09-23`, unless a
path says otherwise. Archaeon's side is under `ops/campaigns/C-001/ATTRIBUTION_ARC_2026-09-28/` on branch
`archaeon/attribution-arc-2026-09-28`.

## What run 2 is
- **What it is:** an observation-only replay of the 11 T-003 run records (9 distinct simulations; s9200006 C and s9200008 C
  duplicate their A arms, defect C9-D24) on the frozen NPE engine `roles/Nestor/campaigns/z80atlas-verify-2026-09-22/`.
- **Tracer:** an independent Z8 shadow tracer (`tracer/z8shadow.py`, `observe.py`).
  - It is asserted value-identical to the frozen VM on EVERY interaction: 256,000 per record.
  - It exports every birth (`exports/*.births.jsonl`) and a seeded 1% agreement sample (outside git; hashes in
    `exports/SAMPLE_MANIFEST*.json`).
- **Tests:** the owner's s4 instrument tests on every birth (`tracer/s4_run.py`; `exports/S4_RESULTS.jsonl`,
  `S4_SUMMARY.json`). Their tallies are UNUSED until an independent check of `s4_run.py` (Archaeon addendum 1).

## Provenance chain to check
1. **Pin and reproduce:** `pin/PIN_REPRODUCE.json`. The T-003 harness is pinned at 53b1bc2b3, and result_sha256 efba5535...
   equals T-003's. Per-run lineage hashes equal Archaeon's `NPE_T003_HASHES.txt`.
2. **Gates:** `GATES.json`, G1-G4 with their evidence. Also Archaeon's `gate_close/ANCESTRY_REPLAY_PRODUCTION_GO_FINAL.md`, `_v2.md`
   and `GO_FINAL_ADDENDUM_1/2.md`.
3. **Freezes:** `tracer/TRACER_FREEZE.json`, v4 (sha256 LF c1ce6d93...). v3 -> v4 changed `run_production.py` only.
4. **Run 1 was invalidated:** `PRODUCTION_RUN1_INVALIDATED.json`, for the duplicate_of bookkeeping defect.
5. **Run 2 receipts:** `exports/START_RECEIPT.json` (13 binding checks), `END_RECEIPT.json` and `PRODUCTION_INDEX.json`.
6. **Run 1 vs run 2:**
   - births exports byte-identical, 11/11;
   - sample content identical, 11/11. The gzip header mtime differs, and Archaeon ruled that acceptable in addendum 2.
7. **Tracer agreement (G2):**
   - fresh set 2 (`g2_fresh/NESTOR_FRESH2_OUTPUT.jsonl`, `NESTOR_COMPARISON_SET2.json`) vs Archaeon's sealed reference output;
   - raw per-class agreement is 1.0 on every gated field;
   - ctrl_slice (S3, open) and pdom are NOT validated and must feed nothing.

## Questions to attack
- **Freeze integrity:** does any production file differ from the freeze, or from GO_FINAL v2's bindings? Were any rules changed
  after exposure without being declared? (Declared exposures are listed in GATES.json and the invalidation record.)
- **Independence:** is there evidence that Nestor's tracer was adapted to agree with the reference, or that the reference was
  read? (The rule: implement from amendment text; see C6-C10.)
- **Experimental units:** is 9 simulations / 29 births applied consistently? Could any "34 births" count leak into a statistic?
- **Construction vs heredity:** do the exports keep L1-L5 separate? Is any heredity claim made from P-11 or from attribution?
  (CVT-R context: Artemis #891; roles/Nestor/FINDINGS.md "QUALIFICATION".)
- **s4_run.py:** does it implement v4 s4 / v5 R1, R5 and C1 correctly, and is its seeded sampling outcome-independent?
- **Anything else** that would let a wrong attribution survive.

## Deliverable
Findings with severity (BLOCKING / SHOULD-FIX / NOTE), each with file:line evidence, and a verdict:
- INTEGRITY HOLDS / HOLDS WITH NOTES / BROKEN;
- and s4_run.py: CONFORMS / DOES NOT CONFORM.
