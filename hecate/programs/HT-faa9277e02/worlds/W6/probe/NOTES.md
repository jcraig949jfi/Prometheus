# W6 probe (round 3): implementation notes

Written before any treatment code ran. Prompt: hecate/programs/_prompts/probe_impl_v3.md
(sha256 a34a8c61...21685). Bound by roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md
and roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
spec.json, controls.py, ATTAINABILITY.json and control_rows.jsonl are frozen and are not edited.

## Code path

`world.py` imports the frozen `../controls.py` (bytecode writing disabled so nothing is
written outside probe/) and uses ITS functions for everything they cover: `rng_for`,
`step`/`run`, `carve`, `lesion_mask`, `lesion`, `scramble_inside`, `score`. The only new
dynamics are the Hebbian step of Phase A (treatment only). Per seed, in one loop:

1. Controls, re-run exactly as `controls.main` does (same order, same RNG streams):
   FIXED, POSITIVE_CONTROL, NULL_TWIN, NULL_TWIN_B, CHEAT.
   FIXED is also the spec's CONTROL arm (g = 1 throughout); one row, arm name "FIXED",
   role "CONTROL", because the frozen evaluator (`controls.attainability`) keys it by that name.
2. TREATMENT: a, h from stream 0 (drawn exactly as the controls draw them: a then h);
   Phase A = 3000 steps with plasticity from g = 1; settle 1500 steps plasticity off -> O;
   lesion (stream 1 position, stream 2 noise, via `controls.lesion`); regrow 3000 steps on
   the learned g -> R.
3. TREATMENT_TWIN: learned g with edges fully inside the lesion permuted (stream 3,
   `controls.scramble_inside`); same O, same lesioned state; regrow 3000.
4. TREATMENT_TWIN_B: second permutation (stream 4). Used only to put the treatment's twin
   in the arm slot when asking whether the null twin meets the success clauses
   (mirrors the frozen NULL_TWIN_B construction).

## Readings of ambiguities (none changes a threshold)

- Hebbian update timing: simultaneous explicit Euler. At each Phase A step the g update and
  the a/h update both use the state at time t (g_t, a_t); then g is clipped to [0.1, 5].
  mean(a) = spatial mean of a_t over all 2304 cells.
- Edge (i,j) products: horizontal edge (y,x)-(y,x+1) uses a[y,x]*a[y,x+1]; vertical edge
  (y,x)-(y+1,x) uses a[y,x]*a[y+1,x] (torus), matching the gh/gv convention of controls.step.
- "Null twin" of the treatment = TREATMENT_TWIN; clause statistics for the treatment use
  arm = TREATMENT, twin = TREATMENT_TWIN, fixed = FIXED (the CONTROL), via the frozen
  `controls.statistic`.
- null_twin_meets_success: TREATMENT_TWIN evaluated in the arm slot with TREATMENT_TWIN_B as
  its twin and FIXED as fixed; true only if it meets ALL success clauses.
- Outcome decision (in evaluate.py, code):
  1. Reproducibility: recompute `controls.attainability` on the re-run control rows; if any
     clause's attainable or discriminating flag differs from ATTAINABILITY.json ->
     INSTRUMENT_FAIL (reproducibility), stop.
  2. positive_control_detected = every success clause attainable on the rerun and no failure
     clause fires on the positive control; cheat_detected = the frozen cheat_ok. Either false
     -> INSTRUMENT_FAIL.
  3. null twin meets success -> CONFOUNDED.
  4. treatment meets every success clause and fires no failure clause -> SIGNAL.
  5. otherwise -> NULL (fails the criterion or meets a failure clause; the region between
     success and failure thresholds is also NULL per round-1 "fails the criterion").
- Numeric reproducibility of the control values against ATTAINABILITY.json is also reported
  (max abs difference), but the INSTRUMENT_FAIL test is on attainable/discriminating status,
  as the prompt states.

## Seeds

0..9 (spec seeds, 10 = the spec's count). RNG: numpy SeedSequence([20260930, 6, seed, stream]).

## Budget

Expected ~1 core-minute total (numpy, single core); measured with time.process_time and
written to rows and OUTCOME.json.
