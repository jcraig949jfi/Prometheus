# RECORD: HARM-55 native Flax column and HARM-56 disposition

Harmonia[m2-475d761f], 2026-09-30. Taken over from offline m2-ca1148a0 / gandalf-6cd1348b. CWO 2026-09-30 / MWO-0004.
Execution note (committed before any Flax score): `roles/Harmonia/science/asal_ruler/HARM55_EXECUTION_NOTE_2026-09-30.md`
(43ad5b853).

## Disposition

**HARM-56 disposition (AMENDMENT_A, VIEW 2 native anchors): A_OBSERVER_STABLE.**
VIEW 1 verdicts A/B/C: OBSERVER_STABLE. The phenomenon does not disappear under the native observer.
`replication_authorised`: true, with the control caveat below.

## Order of execution (B2 cheat first)

| Step | Result |
|---|---|
| 1. Torch cheat: anchors through the torch path must reproduce `MANIFEST_anchors.json` to 1e-6 | **PASS 16/16**, max abs diff 5.96e-7, weights 40d36571 |
| 2. Native anchors through Flax (FlaxCLIPModel, body 677ba0ea, tree 188a6ada) | 16/16 hash-verified. STATIC 0.8750002 (scale check vs 0.875 passes); garbage mean 0.81669 sd 0.00836; LENIA 0.84725; noise mean 0.86629. **Controls coherent.** |
| 3. 395 frames through Flax | 395/395 hash-verified against the frames manifest |
| 4. `harm55_compare.py` (pre-committed) | n 333 compared, 0 missing; max abs error 4.77e-7 (mean 1.08e-7); Spearman 1.0; best-crosser identity and class preserved |
| 5. `harm56_map.py` (frozen at 68713424d, unmodified) | map: every row STABLE (catalogue 61 crossing / 272 not; mean 105 / 228; 2sd 24 / 309); classification 324 stable / 9 unresolved; subset survival under both views: catalogue 5/5, genuine 9/9, deep 10/10; no B hits |

## Deviation, disclosed: the first HARM-56 run could not compute VIEW 2

- `harm56_map.py` reads the native anchors from `fx["anchors"]` inside the `--flax` file. The Flax scorer wrote frames
  and anchors to **separate** files, so the first run (kept at
  `out/harm56_map_2026-09-30_view1only/`) returned `UNRESOLVED (native anchors absent: VIEW 2 not computable)`.
- Fix: **input assembly only.** `HARM55_FLAX_NATIVE_WITH_ANCHORS_2026-09-30.json` is the frames file plus
  `anchors` = the anchors file's `scores`, copied verbatim, with an `anchors_merge` block that records both source
  sha256s (frames 1411ff24...6560, anchors 815d8348...a30e). No score changed and no tool changed. VIEW 1 is identical
  in both runs.
- The VIEW 2 disposition was not seen before the re-run: the first run could not compute it.

## Control caveat

- `C-SELF` and `C-STATIC` read **null** ("no self_check block returned", "no static_control returned"). The Flax scorer
  did not emit those blocks. `replication_authorised` treats null as not-failed.
- In substance both are covered elsewhere: the torch cheat (step 1) is the self-reproduction control, and the native
  STATIC anchor (step 2) is the static control, which passes. They are **not** in the fields the tool reads. So the
  authorisation stands on those two separate artifacts, not on the tool's own control fields.

## Admissibility

- Python 3.12.10 (not the manifest's), and frames from the transfer branch: both recorded before scoring in the
  execution note.
- The Flax and torch observers agree to float32 rounding (4.8e-7). HARM-56 therefore shows that **observer
  reconstruction is not the source** of the crossing phenomenon. It says nothing new about whether the crossings are
  open-endedness. Scope is unchanged from the HARM-56 contract.

## Artifacts (sha256 of the committed bytes)

| File | sha256 |
|---|---|
| `techne/acquisition/poet_alife/HARM55_FLAX_NATIVE_2026-09-30.json` | 1411ff24...6560 |
| `techne/acquisition/poet_alife/HARM55_ANCHORS_FLAX_NATIVE_2026-09-30.json` | 815d8348...a30e |
| `techne/acquisition/poet_alife/HARM55_FLAX_NATIVE_WITH_ANCHORS_2026-09-30.json` | a938ee8f...c113 |
| `roles/Harmonia/science/asal_ruler/out/run_2026-09-18/harm55_comparison.json` | 8a755d93...c68c |
| `roles/Harmonia/science/asal_ruler/out/harm56_map_2026-09-30_view2/harm56_map.json` | 8457af0a...52ba |

## ERRATUM E-1 (2026-09-30, after Techne #1072 note 3a): two artifact hashes were not blob hashes

- The table above says "sha256 of the committed bytes". For the first two rows it gave the hash of the file **as the
  scorer wrote it on the scoring host** (CRLF, text mode). Those are not the committed blobs. Rows 3-5 were correct.
- Blob hashes (`git show origin/main:<path> | sha256sum`), verified by Harmonia:

| File | blob sha256 | host-written (CRLF) sha256 |
|---|---|---|
| `HARM55_FLAX_NATIVE_2026-09-30.json` | 10f714c8...ffbc1 | 1411ff24...6560 |
| `HARM55_ANCHORS_FLAX_NATIVE_2026-09-30.json` | 4ff59911...38582 | 815d8348...a30e |
| `HARM55_FLAX_NATIVE_WITH_ANCHORS_2026-09-30.json` | a938ee8f...c113 | (written LF) |
| `harm55_comparison.json` | 8a755d93...c68c | (same) |
| `harm56_view2/harm56_map.json` | 8457af0a...52ba | (same) |

- The `anchors_merge` block inside the merged file records the **host-written** hashes of its two sources. That is
  what the merge actually read; it is now labelled as such here. No score and no verdict is affected.
- This is the same class of error as my MWO hash fix earlier (CRLF working tree vs LF blob). Rule for my own records
  from now on: an artifact table states which bytes it hashes, and "committed" means `git show <rev>:<path>`.
