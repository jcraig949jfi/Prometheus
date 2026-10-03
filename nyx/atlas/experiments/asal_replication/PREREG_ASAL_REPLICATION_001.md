# PREREGISTRATION -- ASAL full-domain replication 001 (both observers; frozen before any replication score)

Author: Nyx[gandalf-d1f90ae1] (claude-opus-5-5), M3 GANDALF, 2026-10-03.

## Authority

- **Operator directive 2026-09-19 s4.** "After HARM-56, run a fresh replication over the extended port. Do not
  retroactively complete the original 1,045-draw experiment."
  - HARM-56 returned A_OBSERVER_STABLE with replication_authorised = true (Harmonia #1067).
- **Harmonia #1076.** Native column on M2, torch on M3, kept separable, not native-only. Freeze per-column host +
  witness, the anchor set through each observer, and the frames' blob hashes.
- **Operator directive 2026-10-03 N1.** Verbatim at roles/Nyx/prompts/2026-10-03_operator_unblock_queue/.

## Freeze order

Every pre-run control below ran BEFORE this file was frozen. None of them produces a replication score:

1. domain;
2. fixture (re-scores only Techne's seven fixture arms, whose values are known);
3. determinism (frames only, no observer).

The freeze commit carries this file, the packet nyx/atlas/predictions/MECH-ASAL-REPLICATION-001.json with its FREEZE,
and the executor. `replicate.py --stage search` refuses to run unless that FREEZE matches the packet bytes.

## 0. What is replicated, and what is not changed

The INSTRUMENT is Harmonia's 09-18 ruler, imported by path and used UNMODIFIED:

- the rollout (128 world, 256 steps, 8 frames at steps 0, 32, ..., 224);
- the ALIVE band (1 <= mass <= 8192 at the 8 samples and the final state);
- the observables (d_pix, d_clip, coh, disp, mass_cv);
- the four classes and their rules (asal_ruler.py:96-105);
- the S1 draw rule;
- the S2 local rule (5 starts x 40 steps; Gaussian steps on m, s, R with sd 0.02, 0.005, 1; b / kn / gn fixed).

The score is the fossil's metric (asal_metrics.py:52-64).

| What | Value |
|---|---|
| Executor | Techne's numpy Lenia port EXTENDED at 593d57096 (kn 1-4, gn 1-3, fractional rings): techne/scripts/techne107_asal_observer.py, sha256 (LF) 66294e74dc294d19688b7d16b00a449683656779b492bd0a3e67edf145948f09, unchanged since that commit. |
| Catalogue | roles/Harmonia/science/asal_ruler/fixtures/animals.json, sha256 09cf0a831c1ef8a73ebfaa9126257fbe076108362b706a98d88650ca9848d206. |
| Threshold semantics | Frozen as roles/Harmonia/science/asal_ruler/out/run_2026-09-18/thresholds.json, sha256 83c7b2aeba7703b978c2b88aae00fad62fe3b4d266b623e3d5e04c980fc4a3c7. |

The fixture stage reproduced every threshold of that file to 0.0 on this host and port (FIXTURE_CHECK.json). The
garbage conventions stay the named cutoffs of rule A7: mean 0.8167 and 2-sd line 0.7999 (0.816686 / 0.799960 in
the ruler).

**Not changed, in response to anything.** No search rule, budget, class threshold, observable or boundary was
altered in response to HARM-55 / HARM-56 (operator s4: "Do not optimize the search in response to HARM-55 findings").

## 1. The domain, enumerated and instantiated BEFORE any score (DOMAIN.json)

**Categorical and edge classes.** These are the 09-18 classes:

- b: the 8 commonest catalogue strings;
- kn 1-4, gn 1-3;
- R at 6 and 30, T at 5, 10 and 20, m at 0.05 and 0.50, s at 0.005 and 0.10;
- plus every kn x gn pair.

Accepted: all of them (refused: 0).

**Catalogue (S0).** Every entry of animals.json that has params and cells, with cells free of the 3D/4D
delimiters % # @.

- IDENTITY = the entry's POSITION in animals.json (key "S0_p<pos>"), never its code: 63 codes are duplicated
  (Harmonia #479).
- 548 members.

| Status | Count | Meaning |
|---|---|---|
| ACCEPTED | 537 | instantiated at 128 and stepped 3 times, finite |
| EXCLUDED | 11 | the pattern is larger than the 128 world |
| REFUSED | 0 | |

The one admissible exclusion reason is "pattern_larger_than_world_128". It is explicit and listed by position. Any
other refusal stops the experiment.

**Fresh draws (S1).** 300 draws by the 09-18 rule with seed 20261003 (the 09-18 seed was 20260918). The draw list's
sha256 is 56a8f3a354030e86cdbc6c0f951055f35425da45a7769e30129a74c76d0cde10. Every draw was instantiated; refused: 0.

**S2 (adaptive).** S2 cannot be enumerated in advance. Its moves stay inside classes already accepted: b, kn and gn
are those of an accepted start, and m, s and R are clipped to the accepted edges.

**Overlap with 09-18 (by position).** 154 catalogue positions were executed on 09-18 (S0_OLD). 383 accepted
positions were never executed (S0_NEW).

**Strata used by the packet:**

| Stratum | Contents |
|---|---|
| S0_NEW | the 383 never-executed accepted catalogue positions |
| S0_OLD | the 154 executed on 09-18 |
| S1 | the 300 fresh draws |
| S2 | the 200 local steps |
| NEW_ALL | S0_NEW u S1 u S2 |

**Budget.** 537 + 300 + 200 = 1,037 rollouts. Every one is scored exactly once by each observer. There is no early
stop and no re-draw.

## 2. Determinism, proven BEFORE the freeze (DETERMINISM.json; frames only, no observer)

- **SAMPLED.** All 395 rollouts executed on 09-18, regenerated on this host with this port. Their uint8 128 frames
  must hash to the 09-18 delivery manifest (frames128_manifest.json) for 395 of 395.
- **ADVERSARIAL.** A score-blind, rule-chosen subset:
  - one catalogue member per (b, kn, gn) class the 09-18 port refused;
  - the largest accepted pattern;
  - the max-R and the min-T members;
  - S1 draws at the domain edges.

  Each is run twice: once in this process, once in a fresh subprocess in reversed order. All pairs must be
  byte-identical.

**Result (before the freeze).** SAMPLED 395 of 395 identical to the 09-18 delivery (230.8 s). ADVERSARIAL: the rule
selected 161 rollouts (154 catalogue members across the previously refused b / kn / gn classes, plus the edge picks
and 4 S1 edge draws); 161 of 161 byte-identical across the two processes.

## 3. The two observer columns, separable

**TORCH column (M3 GANDALF).** The 09-18 observer:

- Techne's asal107 env: Python 3.11.9, numpy 1.26.4, torch 2.14.0+cpu, openai `clip` ViT-B/32, weights sha256
  40d36571... (the full witness block is written into the frames manifest at run time);
- the numpy score.

The torch column DRIVES the search (S2's start points and acceptance read it), as on 09-18.

**NATIVE column (M2 SPECTREX5, Harmonia).** ASAL's own `foundation_models/clip.py` (FlaxCLIPModel
openai/clip-vit-base-patch32) and ASAL's own `asal_metrics.calc_open_endedness_score`, from the hash-verified body,
through `techne/scripts/harm55_flax_score.py --path flax`, unmodified.

- The env is Harmonia's HARM-55 env: Python 3.12, jax / jaxlib 0.4.38, flax 0.10.2, transformers 4.47.1, numpy
  2.2.6.
- Any deviation is written down BEFORE the first native score, as in HARM55_EXECUTION_NOTE_2026-09-30.md.
- The native column reads the SAME frames. Nothing is regenerated on the scoring host (directive 2026-09-19 s1).

**Frames.** The uint8 (8, 128, 128) grey frames of every scored rollout (exactly what grey_to_rgb() fed CLIP):

- stored OUTSIDE git at C:\Prometheus-vault\nyx\asal_replication_001_frames128\<key>.npy, and carried to M2 on an
  orphan transfer branch;
- the manifest (in git) records each file's sha256 over its bytes. Binary files have no line-ending form, so the
  host bytes ARE the blob (Harmonia #1072 erratum E-1).

**Anchors.** The 16 HARM-55 control anchors, unchanged: origin harm55-frames-transfer:transfer/harm55_anchors/,
MANIFEST_anchors.json blob 692d4869a9dc, sha256 3c39ed16b281f145d32ef6b536f4770e1b3a1cc4b9f6331d8f8dba515c1b92f3.
They go through BOTH observers: through torch first (cheat, below), then native.

**The two columns are never merged.** rows.jsonl carries the torch score. The native score file is keyed by the
same keys. A comparison table joins them by key, re-derived from file names, never by position (HARM-56 C-ORDER).

## 4. Controls

**Before the freeze (pass required):**

| Control | Requirement |
|---|---|
| F | The seven-arm fixture within 0.002 of TECHNE-107's receipt. |
| C-METRIC | The independent score equals the port to 1e-6 (float32) and 1e-12 (float64). |
| C-NEG-BLANK | A blank world scores 0.875 and is NOT_ALIVE. |
| C-CHEAT-SCORE | GARBAGE seed-0 frames score 0.8303 regardless of the parameters. |
| C-POS-SEARCH | The free-image search reaches <= 0.8167. |
| Thresholds | Reproduce the 09-18 file to 1e-12. |
| D-SAMPLED, D-ADV | Section 2. |

All passed (FIXTURE_CHECK.json, DETERMINISM.json).

**After the torch search, before frames are delivered:**

- **C-SELF.** The torch path of harm55_flax_score.py re-scores the exported uint8 frames, and every score equals
  the search's to <= 1e-6. If not, the frames are not the frames that were scored, and nothing is delivered.
- **C-REPRO.** For every S0_OLD position, the replication's torch score equals the 09-18 torch score of the same
  catalogue entry to <= 1e-6 (same frames, same observer). A failure means the column is not the 09-18 column.

**Native column, before any native frame score:**

- **C-CHEAT-ANCHORS.** The 16 anchors through the torch path on M2 reproduce MANIFEST_anchors.json to <= 1e-6
  (HARM-55 order).
- **C-STATIC.** The STATIC anchor through the native path scores within 1e-5 of 0.875 (HARM-55: 0.8750002).
- **C-HASH.** Every frame file's sha256 equals the manifest. The scorer stops on any mismatch.

These are named here as SEPARATE ARTIFACTS, which is the second option Harmonia #1076 allows. The scorer is not
modified to emit self_check / static_control blocks.

## 5. What the packet predicts, and what it does not

The packet (MECH-ASAL-REPLICATION-001) makes four EXACT, existential-or-identity rows, all A2-exempt. Three are on the
NEW strata, which no seat has ever seen scored; one is on the observer pair. See the packet for the rows, bands,
cut_kill and indeterminate rules.

S0_OLD is a control (C-REPRO), never a prediction: its scores are known.

**Readouts requested beside the rows (descriptive, never verdicts):**

- per stratum: n, n_alive, min, argmin, crossings at both lines, and class histogram;
- the class composition of crossers;
- the cross-observer map of HARM-56 s2 (STABLE / LOST / GAINED crossing at both lines);
- the 0.01-band pairwise discordance.

**What this replication does NOT license:**

- any claim about the 11 excluded patterns;
- any claim about ASAL's JAX Lenia (the substrate is the numpy port);
- any claim beyond this budget;
- any claim that the crossings are open-endedness.

The resolution of the claim changes only by what the rows say on the strata they name.

## 6. Roles

| Seat | Role |
|---|---|
| Nyx | Authors this file and the packet; runs the torch column and the frame export on M3 (operator 2026-10-03 N1). |
| Harmonia | Runs the native column on M2 and ADJUDICATES every row. |

Nyx does not adjudicate its own rows. Its readouts are descriptive.

## 7. Cost

- Torch column: measured on 09-18 at ~1.3 s per rollout on M3 (395 in 22 min, plus fixture). About 25-35 min for
  1,037 rollouts.
- Native column: on M2, comparable to HARM-55 (395 frames).
- Inside MWO-0004 R2. No lease needed.
