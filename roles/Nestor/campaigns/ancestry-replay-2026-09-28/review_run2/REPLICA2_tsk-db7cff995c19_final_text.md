# Review of NPE ancestry replay, production run 2 (task tsk-db7cff995c19)

**Verdict: INTEGRITY HOLDS WITH NOTES. s4_run.py: DOES NOT CONFORM.** Two findings are BLOCKING: they must be resolved before run 2's exports feed Archaeon's synthesis. Neither shows that run 2 itself is corrupt. The s4 deviations are real but change no existing run-2 tally for the 9 distinct simulations.

**Limits of this review.**
- Bash was denied to me and to the subagent I tried, so I recomputed no sha256.
- I could not read Archaeon's branch: GO_FINAL v1/v2, addenda 1/2, NPE_T003_HASHES.txt, SEALED_HASHES_SET2 and the prereg v5 text.
- I could not read git history or the run-1 files in `_scratch/`.

These claims are therefore **unverified by me**:
- the freeze and binding hashes;
- "v3 -> v4 changed `run_production.py` only";
- run 1 vs run 2 byte and content identity;
- equality with `NPE_T003_HASHES.txt`;
- the sealed set-2 hashes.

I judged s4 conformance against the rules as restated in the code's docstrings and GATES.json, not the prereg text.

One check did pass: all 11 lineage hashes in `PRODUCTION_INDEX.json` equal those in `pin/PIN_REPRODUCE.json`. So production replayed the pinned simulations unchanged, end to end.

Paths below are relative to the campaign directory.

## BLOCKING
- **B1 – The 1% production agreement check has not happened.** `roles/Nestor/WORK_STATE.json:29` says the sample transfer to M2 is blocked (no key-only route). So the reference tracer has never run on production interactions; G2 covered only fuzz and fresh pre-states. The packet lists the sample hashes (`REVIEW_PACKET_RUN2.md:16-17`) without saying the check is pending.
- **B2 – The s4 flip-test coverage floor fails in both classes, and the packet does not say so.**
  - The floor is 50% (`tracer/s4_run.py:19`). Observed: other = 0.125, self = 0.4472 (`exports/S4_SUMMARY.json:9,26`).
  - With identified loci as the denominator it still fails: 41/301 and 182/395.
  - The code never evaluates the floors (`s4_run.py:84-92` only reports shares), so nothing flagged it.
  - This is an instrument reading, not a Q result. No attribution for run 2 may rest on the flip test unless Archaeon rules otherwise.

## SHOULD-FIX
- **S1 – "identified" uses the wrong flip rule.** It uses the strict rule (`interventions.py:261`, via :212), not the gating prefix rule (C7.2; `s4_run.py:10`, `GATES.json:15`). No effect in run 2: `S4_RESULTS.jsonl` contains no FAILED at all.
- **S2 – Mutated loci are not excluded from the MOVE arms,** although the docstring says they are (`interventions.py:5`). Labels are taken before the mutation (:94-120, :186, :194); mutation labels are applied only in `observe.py:170-176`. No effect in run 2: all 34 birth records have `"mutations": []`.
- **S3 – The coverage denominator is every flip-tested locus** (`s4_run.py:74-78`), not "rule-identified MOVE loci" as stated at :19.
- **S4 – Per-byte R5/C1 runs on a 20% seeded subset** (`s4_run.py:12-13,44`), while :4 says every birth is tested. That subset is 6 births, and only 2 are in class "other" (s9200004/257 and s9200008 B/256). The "0 leaks" R5 pass for "other" is therefore very thin. Confirm the 20% subset against the v5 text.
- **S5 – The seeded subset is outcome-independent in form but not blind.**
  - The per-byte selection key depends only on run and child ids (`s4_run.py:44`).
  - All 34 run/child keys were known from the pin step (P5) before SEED = 20260928 was fixed (`s4_run.py:31`).
  - So the seed could in principle have been picked knowing which births it selects. Low suspicion, but it should be declared.
- **S6 – The freeze does not cover everything production runs.**
  - `TRACER_FREEZE.json` omits `s4_run.py`, `production_launch.py`, the engine files, and `pin/pin_reproduce.py`, which `run_trace.py:25-27,140` imports for the job list.
  - The launcher only records the s4 and launcher hashes (`production_launch.py:41`); it does not refuse on a mismatch.
  - `GO_FINAL_SHA` is a constant never compared with any file (:24), and there is no clean-tree check.
  - The matching lineage hashes cover the engine and job list, but not `s4_run.py`. Someone with git should confirm that 68779d3e is the blob committed in 0e22fa57e and that GO_FINAL v2 binds it.
- **S7 – The byte-identity restart check was redefined after it failed, and GATES.json was not updated.**
  - `PRODUCTION_RUN1_INVALIDATED.json:27` promised byte-identical sample exports. That was impossible: `run_trace.py:153,157` writes gzip with no fixed mtime.
  - Addendum 2 relaxed the check to content identity. `GATES.json` (last updated 23:17Z, before run 2) does not list that change.
  - `SAMPLE_MANIFEST_CONTENT.json` was written by hand, and the run-1 content hashes are not in git, so the 11/11 content identity can't be verified from git.
- **S8 – No receipt binds the per-run `summary.json` files.** They carry the L3/L4 readings, P4 tallies and child genomes; only the git commit protects them.
- **S9 – "identified" says nothing about which donor byte was the source.**
  - For a donor-sourced, donor-performed locus, R1 randomises only the victim's material and registers (`interventions.py:237,165-173`). Only the flip test checks the source, and its coverage for "other" is 0.125.
  - Some children are 0x36 near-homopolymers (s9200004 summary), the painting signature in `FINDINGS.md:511-512`.
  - So L2 (`run_trace.py:117`) must not be read as copying.

## NOTES
- **N1 – Experimental units.**
  - 29 births / 9 simulations is applied correctly in the S4 per-class tallies: duplicates are excluded at `s4_run.py:70`, and their classes mirror the A arms.
  - A 34 count can still leak: `n_births_tested: 34`, PIN "34 births", and summaries with no duplicate marker. 6A/6C and 8A/8C report identical P4 tallies, so anyone summing summaries double-counts.
  - The 1% sample covers the duplicated simulations twice, because its key includes the run name.
- **N2 – A missing index entry would count a record as distinct.** `s4_run.py:62` fails open.
- **N3 – The class tie-break is unspecified** (`s4_run.py:50`).
- **N4 – The persisted-origin field in ENTITY labels was never validated.** G2 fresh runs build labels without origin vectors (`fresh_run.py:71` → `interventions.py:94`); production uses them (`observe.py:143`). It must feed nothing, like ctrl_slice and pdom.
- **N5 – Stale text in frozen files makes the chain hard to audit.**
  - `fresh_run.py:1-4` cites the v2 tracer and set-1 seed, while `GATES.json:48` says "frozen v3".
  - `compare_fresh.py:1-2` cites the set-1 hashes.
  - `production_launch.py:4-8` cites the v1 hashes.
  - `s4_run.py:8` says "v3 freeze".
  - `GATES.json:11` still describes the GO_FINAL v1 bindings.
  - Confirm with git which freeze produced fresh set 2.
- **N6 – The MUTATION_content 0/212 diagnostic is a parser mismatch, as declared.** `compare_fresh.py:53-55` compares a side value with a list, and `fresh_run.py:54` writes the key "k", not "call".
- **N7 – Independence.**
  - No tracer code reads the reference output; only `compare_fresh.py:25` opens it.
  - The tracer was revised after seeing the raw set-1 disagreements (C9 re-freeze; `z8shadow.py:66-67`), and fixture K16b was added after validation (`npe_fixtures.py:244`). Both are declared, and a fresh set followed.
  - 1.0 agreement on set 2 cannot rule out co-adaptation on the behaviour the C9 text fixed from set 1.
- **N8 – L1–L5 are kept separate in the exports** (`run_trace.py:116-120,220`). They state "construction is NOT heredity", and none makes a heredity claim from P-11 or from attribution.
- **N9 – `run_production.py` gates only on the hand-written GATES.json statuses.** This is by design.

**Before synthesis:**
1. Complete the 1% sample check (B1).
2. Get Archaeon's ruling on the flip-coverage failure (B2).
3. Fix S1–S3 under a new freeze. The run-2 tallies for the 9 distinct simulations should reproduce exactly, which is a useful check.
4. Have a reviewer with git and branch access verify the hash claims I could not.

The full report is in `/home/jcraig/fabric-work/worker.ubu002/attempts/att-fe4f19b048c6/out/REVIEW_RUN2_FINDINGS.md`.