# C-018-T050 -- RESULT: Aether confirmatory run, FREEZE_AETHER_ANCESTRY_CONTENT v1.1.0

Run by Argus[harry1-b0323ab0] (claude-sonnet-5-5, Q2), harry1 (M4) CPU only, nothing on M2, 2026-10-12.
Release: rso/aether/RELEASE.json (release_ref `C018-T042-cleared-2026-10-12`).
Procedure: `python -B -m rso.aether.confirm run <shard> --cleared-by C018-T042-cleared-2026-10-12` for RX.0-RX.3 and V1.0, V1.1
(detached OS processes, two at a time, wrapper `runs/meta/runshard.ps1`), then `python -B -m rso.aether.confirm analyse`
(full JSON: `runs/meta/analyse_full.out`). No file pinned in rso/aether/FROZEN.json was changed; neither `run` nor `analyse` refused.
No re-run, no other seeds, no unit selection, nothing in Aether/ or roles/Aether/ touched. Every shard ran once and completed.

## 1. Dispositions (the registered rule decides; PREREGISTRATION s6, s11)

| law | disposition (label) | evaluable / min | need | classes | reach band | content excess (registered, conditioned) | over CONFIRMED seeds | decoder null |
|---|---|---|---|---|---|---|---|---|
| **RX (primary)** | **CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT** `[evaluable 13 of 48 units; minimum 8; need 3 CONFIRMED at r >= 2]` | 13 / 8 | 3 | CONFIRMED 8, NOT_INTERVENTIONAL 5, CONTROL_VACUOUS 8, INSUFFICIENT 3, NO_CUT 24, NONSPECIFIC 0, MULTI_SOURCE 0 | 6 | 0.0135 (= content_excess_all 0.0135) | 0.0099 | 0.0002 |
| V1 (comparison) | **ANCESTRY_UNEVALUABLE** `[evaluable 0 of 16 units; minimum 8; need 3 CONFIRMED at r >= 2]` = "not evaluated" (not absent, not present) | 0 / 8 | 3 | NO_CUT 13, INSUFFICIENT 3, others 0 | 0 | n/a; content_excess_all 0.0041 | n/a | 0.0001 |

RX evaluable 13 = CONFIRMED 8 + NOT_INTERVENTIONAL 5. All 8 CONFIRMED units have r_int >= 2: r_int 2 (8201, 8207, 8226, 8231), 4 (8237),
6 (8219, 8223, 8228). Attribution agreement (descriptive): pooled 0.7475 -> MIXED. Light-cone violations 0. Completeness COMPLETE
(manifest b9bc5cf5...). `problems` empty; qualification true. Evidence block: freeze_check OK; 64 rows, 64 distinct arrays_sha256;
64 snapshot-bound; 64 attribution trees replayed (s10.6); 6 fully replayed.

The content reading is the registered one. The conditioned excess is below 0.05 over the registered band (0.0135) and over the CONFIRMED units' own
seeds (0.0099); both are on the same side of the 0.05 margin, so no disagreement across the margin arises. Per s11.6 the bound stands: an excess
below ~0.05-0.10 is not excluded (Pallas's 24 challenge units read 0.012 with null -0.0004).

## 2. REPORT s5 items 1-5 (rso/aether/challenge/R2/REPORT.md, "Limitations the RESULT must carry")

1. **Clamp arrays (R1c).** The CUT_B / CUT_N first-divergence arrays of 58 of 64 units were not replayed. For those units the class (CONFIRMED /
   NONSPECIFIC / NOT_INTERVENTIONAL) rests on producer bytes bound by the seed's warm snapshot, the replayed attribution tree (site for site,
   tick for tick), the tree invariants and clamp fidelity; an invariant-respecting rewrite of one clamp array changes the class of a non-sampled
   unit without any check failing (C-018-T042 R1c: NONSPECIFIC -> CONFIRMED on 0x3003). The six fully replayed units (first seed of each shard;
   arrays_sha256 and meta tree / B / N / origin reproduced) are **8192 (RX.0), 8204 (RX.1), 8216 (RX.2), 8228 (RX.3), 8192 (V1.0), 8200 (V1.1)**.
   Of the 8 RX CONFIRMED units only 8228 is among them.
2. **The pin (R6b).** The analysis ran under rso/aether/FROZEN.json blob sha256
   `9fe0fcb4e2ab59f1547d36652141d90380d81771495180b970a3802e8382d306` at commit `1f2d2444f52a8c2411ee2b1d1032b1b4a7da0be3` (as named in
   RELEASE.json). `freeze check` binds the analysis to that file and the file to git, not to the analyser. The release record names the same
   commit. The RELEASE.json design_manifest_sha256 check reads FROZEN.json too (confirm.py:68), so it is part of the same trust. `confirm design`
   prints `d9e8f885c8d43a237854359c7a8ef7394485bc69483600c43d220821314c8d47` = the release's; the committed design manifest is unchanged.
3. **The N window (W2).** N is chosen on B's own wavefront (ftick(B) <= ftick(N) < min ftick(targets)). There is no NONSPECIFIC unit. Among the
   8 CONFIRMED units N is 4-adjacent to a target of B in **5** (8201, 8207, 8226, 8231, 8237) and at Chebyshev distance 2 in 3 (8219, 8223, 8228).
   NONSPECIFIC would mean "damage spreading or a lateral path the single-parent attribution did not record"; the class of a unit is conditional
   on the registered N rule. In those same 5 CONFIRMED units N was moved off v1.0.0's first-ranked N, which first diverged at tick 1, before B.
   Per-unit values (distance = toroidal Chebyshev from N to the nearest tree descendant of B; record: `runs/meta/result_tables.json`, produced by
   `runs/meta/result_tables.py`, which imports the frozen adapter/evaluate read-only; its ftick values equal the analyser's):

   | seed | class | r_int | ftick(B) | ftick(N) | N -> nearest target | v1.0.0's N diverged before B? |
   |---|---|---|---|---|---|---|
   | 8201 | CONFIRMED | 2 | 5 | 9 | 1 (4-adj) | yes |
   | 8207 | CONFIRMED | 2 | 8 | 8 | 1 (4-adj) | yes |
   | 8219 | CONFIRMED | 6 | 1 | 36 | 2 | no (same N) |
   | 8223 | CONFIRMED | 6 | 1 | 1 | 2 | no (same N) |
   | 8226 | CONFIRMED | 2 | 5 | 6 | 1 (4-adj) | yes |
   | 8228 | CONFIRMED | 6 | 1 | 4 | 2 | no (same N) |
   | 8231 | CONFIRMED | 2 | 5 | 5 | 1 (4-adj) | yes |
   | 8237 | CONFIRMED | 4 | 13 | 13 | 1 (4-adj) | yes |
   | 8200 | NOT_INTERVENTIONAL | 5 | 3 | 3 | 1 (4-adj) | yes |
   | 8202 | NOT_INTERVENTIONAL | 2 | 1 | 1 | 2 | no (same N) |
   | 8224 | NOT_INTERVENTIONAL | 2 | 16 | 17 | 1 (4-adj) | yes |
   | 8199, 8203 | NOT_INTERVENTIONAL | 3, 2 | 5, 3 | none (not needed, s10.2 item 4) | n/a | yes, yes |
   | 8214 | INSUFFICIENT | 2 | 3 | 3 | 2 | yes |
   | 8220 | INSUFFICIENT | 3 | 1 | 3 | 1 (4-adj) | no (same N) |
   | 8235 | INSUFFICIENT | 2 | 35 | 38 | 2 | yes |
   | 8195, 8208, 8210, 8211, 8216, 8222, 8233, 8236 | CONTROL_VACUOUS | | | no candidate in the window | n/a | 8210, 8216, 8222 yes; others no |

   Across all 24 RX units with a cut, 14 have a v1.0.0 N that diverged before B. **What this does not say:** the 5 CONFIRMED units whose N was moved
   might have classed NONSPECIFIC under v1.0.0's N; no world was run under another rule (no re-execution), so this is an observation about N's
   position, not a measured reclassification. The window also left 8 RX units without a matched control (CONTROL_VACUOUS, s12).
4. **The denominator (R2d).** P2 at depth needs 3 CONFIRMED units at r >= 2 among >= 8 evaluable units of 48 (need = max(3, ceil(10% evaluable))
   binds above 30 evaluable). v1.1.0 reading: 8 CONFIRMED at r >= 2 >= 3, among 13 evaluable (>= 8): **P2 HELD**. Under v1.0.0's registered need
   (5 over all 48 units; computed here from the per-unit classes and r_int the analyser prints, the frozen analyser not edited): 8 >= 5: **P2 HELD**.
   The two readings do not differ, so the disposition sentence carries no denominator caveat.
5. **The minimum (R2e) and content conditioning (R3).** ANCESTRY_UNEVALUABLE with >= 3 CONFIRMED units at depth is "not evaluated", not "absent" and
   not "present"; here V1 has 0 evaluable of 16 and reads "not evaluated". For RX the minimum is met (13 >= 8). content_excess_cond over the
   CONFIRMED units' own seeds is 0.0099 beside the registered 0.0135; the disposition is the registered one. The ancestry reading rests on 13 evaluable of
   48 RX units (27%): 24 have no cut (NO_CUT), 8 are CONTROL_VACUOUS, 3 INSUFFICIENT.

CONFIRMED units' target first-tick distribution (s11.4; "never diverges in CUT_B" = "not within 400 ticks"), min / q1 / med / q3 / max (n targets):
8201 11/13/15/15.5/16 (3); 8207 13/14/15/16.5/18 (3); **8219 302/304.5/307/308/309 (3; all after tick 300)**; 8223 3/20.5/192/202.5/267 (15; 4 after 200);
8226 11/16.5/22/26.5/31 (3); 8228 11/11.8/57.5/114.8/150 (4); 8231 6/7/7/8/49 (5); 8237 14/16.8/20.5/26.5/49 (12). For 8219 the removal is partly a
delayed-divergence reading (every target diverges after tick 300).

## 3. Interpretation carried (s11, s12)

- V1 ANCESTRY_UNEVALUABLE = "not evaluated". P4 transformation stays UNSUPPORTED natively (PREREGISTRATION.md s0 table), recorded, not constructed.
- **TEST-4 is preserved** (`RECOIL_EXCHANGE_CAUSAL_REACH_NOT_SUPPORTED`; content gone beyond radius 3); nothing here reclassifies it (s11.7). This run
  used 128^2 / warm 300, TEST-4 512^2 / warm 1000.
- CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT: interventional ancestry reaches r >= 2 in the 13 evaluable units (reach band 6) while Aether's decoder
  recovers essentially no content (excess ~0.01) at those radii. It is a statement about this decoder at the radius-band level; the bound in s11.6 stands.
- NONSPECIFIC incidence is 0 under v1.1.0, as s11.3 anticipates. The N window was chosen after reading Pallas's challenge outcomes (s10.2 disclosure).
- Ambiguity under the registered rule: none found. Every unit fell in a registered class; both P2 denominators agree; null and light-cone checks clean.

## 4. Resources (measured, harry1, one core per shard, two concurrent)

| step | wall | CPU-s | peak working set |
|---|---|---|---|
| RX.0 | 1067.9 s (16:38:33-16:56:21Z) | not captured | 43.8 MB |
| RX.1 | 1053.9 s | not captured | 43.9 MB |
| RX.2 | 1085.9 s (16:57:36-17:15:42Z) | 1017.4 (external sampler, last sample) | 43.0 MB (sampler); 44.0 MB (wrapper) |
| RX.3 | 1069.7 s | 1016.9 (sampler) | 42.9 MB (sampler); 43.9 MB (wrapper) |
| V1.0 | 624.8 s (17:16:32-17:26:57Z) | 620.1 | 43.6 MB |
| V1.1 | 588.5 s | 584.3 | 43.4 MB |
| analyse (full-output run) | ~35 min | 1832.8 | 344 MB |

Shard CPU is ~95% of wall (single-threaded). RX.0 / RX.1 CPU-s were not captured: the Windows PowerShell 5.1 wrapper read `TotalProcessorTime` and
`ExitCode` after exit without a cached process handle (fixed before the V1 shards); RX.2 / RX.3 were sampled externally every 10 s from Win32_Process
(`runs/meta/samples.csv`). RX.0 / RX.1 are the same design and wall, so about 1000 CPU-s each is an inference, not a measurement. The RX.0-RX.3 exit codes
read null for the same reason; their completion is evidenced by the shard files and the COMPLETE completeness check.
`analyse` ran twice: the first run's stdout was cut by my own `| head` (`runs/meta/analyse.out` is partial and not a record); the second wrote the full
output (`runs/meta/analyse_full.out`). Both read the same committed shards and the first run's visible lines match the full run. About an hour was
lost to a wrapper path error before the second launch.

## 5. Process notes (disclosed)

- `confirm run` prints a per-unit line (seed, B site, N site) to stdout, so a few such lines for the first units of the first shards were visible when
  I checked logs, before all six shards existed. No class, r_int, excess or disposition was seen before `analyse`; nothing was changed in response.
- Q3 provenance: T040 (Pallas, claude-fable-5-1) and T042 (Pallas, claude-fable-5-1; 0 fallbacks) are genuine Fable 5.1, continuity verified
  (RELEASE.json `basis`; challenge/R2/REPORT.md s0). This T050 execution is Q2 (claude-sonnet-5-5), red_required false.
- Ordinary reversible choices: detached wrapper per shard, two at a time; `analyse` rerun for full output; result tables via a read-only script that
  imports the frozen adapter/evaluate.
- Files: runs/CONFIRM/ (6 shard files + 64 unit json/npz), runs/meta/ (logs, wrapper scripts, resource files, analyse_full.out, result_tables.*).
