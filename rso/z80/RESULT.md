# C-017-T050 RESULT -- Z80 Atlas attribution assay, frozen confirmatory run (PREREGISTRATION v1.1.0)

Run by Argus[harry1-2a8591f8] (claude-sonnet-5-5, Q2) on harry1, 2026-10-11. Built from base 2504b063c, branch argus/c017-t050, worktree
C:/Prometheus-worktrees/argus-c017-t050. `python -B -m rso.z80.freeze check` -> OK before and after the run; no file pinned in
rso/z80/FROZEN.json was changed (FROZEN.json sha256 ba1a3b58...7360, in every shard meta). Six shards, one per foreground call, each
exit 0; no shard died, none re-run. Seeds, N and arms exactly as registered (s6): 11 arms, 312 runs + 48 forgeries = 360 rows
(58+58+61+62+61+60). No other seeds, no arm selection, no partial outcome read to decide anything.
Machine output: rso/z80/runs/CONFIRM.analysis.json (verbatim `analysis` output).

## 1. Verdict: ATTRIBUTION_QUALIFIED (registered rule, rso/z80/analysis.py; no ambiguity)

Q1 (per class; wrong = runs not classed as the GT class; pass iff wrong <= w_max):

| class | n | wrong | w_max | pass |
|---|---|---|---|---|
| ENDO | 71 | 0 | 6 | yes |
| ENV | 72 | 1 | 6 | yes |
| EXT | 83 | 0 | 8 | yes |
| INS | 48 | 0 | 3 | yes |

All four classes powered. The one ENV miss is a RECON_ENDO_IMPL run classed ENDO. (H_ENDO_IMPL also has one run with no functional
organism, class NONE, which is outside the n=71 by the s5 definition.)
Q2 (origin, pooled): n 274, wrong 0, w_max 39 -> pass. Per s5/A3 this is a test of INSERTED origin only (see s2).
Q3 forgeries (zero tolerance): LABELS 0/8 bad, PLANT 0/8, PHYS 0/16, TAPE 0/8, GEN 0/8 -> pass (label edits did not move class or origin;
byte / physics / generation edits were refused with the expected REFUSED).
Q4 baselines (each must FAIL Q1; all did, so none passes -> not UNINFORMATIVE):
- b1 (label reader): fails ENV, wrong 72 of 72 (w_max 6); passes ENDO/EXT/INS. Failure guaranteed (no ENV output), not tested.
- b2 (bytes-only): fails ENV, wrong 72/72 (guaranteed), and EXT, wrong 23 of 83 (w_max 8; the 10-epoch horizon of H_EXT_SHORT).
- b4 (recipe reader): fails ENV only, wrong 24 of 72 (w_max 6) -- exactly the 24 CDIST_ENDO_IMPL runs, which it reads as ENDO
  while truth is ENV; passes ENDO (72, 0), EXT (96, 0), INS (48, 0).
Confusion (class by arm), unforged: CDIST ENV 24; H_ENDO_GATED ENDO 24; H_ENDO_IMPL ENDO 23 / NONE 1; H_EXT_GATED EXT 24; H_EXT_SHORT EXT 24;
NH_ENDO_SHORT INS 48; NH_EXT_GATED EXT 24; RANDOM_ENDO_GATED NONE 24; RANDOM_EXT_GATED EXT 11 / NONE 13; RECON ENV 47 / ENDO 1;
SEEDED_ENDO_GATED ENDO 24.

## 2. Scope (PREREGISTRATION s11 narrowing; this verdict licenses only this)

- ENDO = written by the parent's execution with no counted window read, and invariant under the two registered alterations
  (exec_foreign / SEAL). A target dependence entering only through foreign execution or SEAL and invariant under both is
  OBSTRUCTED, not EXCLUDED (s11.5; none constructed). ENDO counts are lower bounds. ENV = the target cell's prior content, nothing else.
- Origin is INSERTED only. ARISEN is NOT tested: ARISEN rows come only from RANDOM_EXT_GATED (here 11 EXT-functional runs, whose
  GT origin is ARISEN, are among the 274) and an always-INSERTED detector would pass Q2; "ARISEN detection is not tested by Q2".
- Replay-dependent (records whose (spec, seed) the pinned engine can replay), engine-pinned, horizon-bounded (10-200 epochs) ground
  truth; longer evolution is labelled by the instrument but not checked against truth by any arm.
- b4's separation from the recipe rests on CDIST_ENDO_IMPL alone (24 runs, one construction): the recipe reads CDIST as ENDO, truth is
  ENV. A recipe table that included CDIST would be right on all eleven arms; the separation otherwise rests on Q3 and the replay.
  b1/b2 fail by construction (no ENV output; horizon), not by test.
- The label is filler-dependent: the zero filler is pinned (A7), not shown to be the only reasonable choice (s11.6).
- Half-solver per-run bar: functional = 8 probe cases per run; registered arms carry no half-solvers; an evolved one is judged by its run's
  eight cases (s11.8). ECHO_forced only; run-level majority class (s11.7-8).
- Not licensed: "independent of the target" for ENDO; "ARISEN detectable"; "better than the recipe" in general.

## 3. Q3 provenance (challenge of the frozen surface)

T040 challenge (Pallas): genuine Fable 5.1. T042 re-check: MIXED -- Fable exploration, but Opus 4.8 predictions and report after a
refusal fallback (accepted as a re-check, rso/z80/challenge/R2/REPORT.md; escalation response NEW_Pallas_2026-10-11_1_RESPONSE.md).
This is NOT a full genuine-Q3 re-check of the repaired surface. This run (T050) is Q2 execution by claude-sonnet-5-5.

## 4. What this does not say (T020 finding restated)

The T020 finding stands: the Z80 world demands reproduction of function, not endogenous heredity. Nothing here says a Z80 organism
discovered heredity. The result is about whether the Observatory can attribute who wrote the bytes of constructed populations.

## 5. Resources (directive s13; psutil process-tree sampling, 0.1 s; rso/z80/runs/CONFIRM.resources.json)

| shard | rows | wall s | CPU s | peak RSS MB | rows sha256 |
|---|---|---|---|---|---|
| 0/6 | 58 | 322.4 | 321.1 | 37.9 | a59f37e912977e96576fbabfd487ba5b0e9bb2ecd444caed90cf78209ae81e78 |
| 1/6 | 58 | 324.9 | 323.6 | 39.0 | 0db1d1692829f3459374bfea255358f0a8435c61ae91fd4230db70935e2f5954 |
| 2/6 | 61 | 317.1 | 315.6 | 38.2 | 41c3c262ee4e478a212286f4cdfabfb980f3cd7e26341584fa63e385acecf226 |
| 3/6 | 62 | 350.0 | 348.5 | 37.9 | 9d9842a6968490c0d3d7d1691719bc8d6d3f5bb7f3ae07c28a88b03d0ba9e249 |
| 4/6 | 61 | 320.0 | 318.8 | 38.1 | 8aca5e0c17f6c5a1c486e229d94b9f2a5b1cdf7d1431eddfb06ecec035bae0c0 |
| 5/6 | 60 | 323.8 | 322.6 | 38.3 | ab4475a46246d0231bca2c3cf0e64a0d409382f57c04ee13f2f36164b090c7f1 |

Total: 1950 CPU-s (~0.54 core-h), 1958 s wall (~33 min, one process at a time), peak 39 MB. Local CPU only, no paid compute. (Prereg
estimate: ~0.8 core-h, ~25 min at 2 processes, < 100 MB.)

## 6. Deviations and choices (ordinary, reversible, recorded)

1. TASK.json gives `--cleared-by "C-017-T042 integrated (Palamedes; rso/z80/challenge/R2/REPORT.md; ...)"`. assay.py:242 refuses any REF
   containing "/" (it would be mistaken for the shard argument). The first call was REFUSED at once (exit 2, 0.2 s, nothing written; freeze
   clean). I re-issued with the same REF text minus the path slashes: "C-017-T042 integrated (Palamedes; challenge R2 REPORT.md; escalation
   response NEW_Pallas_2026-10-11_1_RESPONSE.md)". No pinned file touched. Integrator: consider fixing the packet command / REF rule in a later amendment.
2. Shards run one at a time (headless, no background jobs), not two; this only changes wall time.
3. The shard logs print per-run classes as they run; no decision was based on them, and the command sequence was fixed in advance.
