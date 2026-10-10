# ALIEN RESERVE AR-1: PRODUCTION ADDENDUM (EXPLORATORY; FROZEN BEFORE ANY PRODUCTION RUN)

C-015. Directive Experiment E: an exploratory reserve. Design: alien/AR1_DESIGN.md (build 100c9c427 + merge of main).
- **Pilot (exposed pilot_v2, development only):** 0 / 7 chain-qualified, scratch fails 7 / 7, links
  UNDERDETERMINED_STONE 4, HORIZON_R1 3.
- **Purpose of the production run:** a second, non-lambda representation and search faces the same KP causal test on
  the same 15 production families. It shows whether the stepping-stone failure follows the world or the representation.
  This bears on the recommendation choice (MIGRATE_TO_ALTERNATIVE_REPRESENTATION vs the others).

## Frozen
1. **Pilot-time amendments P-A1, P-A2, P-A3 are ACCEPTED as development changes.** They were made on exposed data
   before this freeze; none changes a search.
2. **Rows:**
   - **PRIMARY only:** seed 0.
   - `r1_multiseed4` and the seed-1 / seed-2 rows are NOT run. The reserve is exploratory, and the compute is better
     kept for review.
   - The given-true-stones row stays NOT_DEFINABLE (no hand-translated row).
3. **Constants:**

   | Constant | Value |
   |---|---|
   | budget | 1e6 charges |
   | max tape | 24 |
   | restart | after 1e5 |
   | credit | the AR1_DESIGN rule |
   | loop iterations | 1024 |
   | stack depth | 128 |
   | probes | -40..40 |
4. **Verdict:** pooled, with the same bar as E3-KP: chain-qualified >= 12 / 15 AND scratch fails >= 12 / 15. It is
   reported as AR1_INSTRUMENT_QUALIFIED with first-failing-link counts.
   - It feeds NO frozen Beta-04 label directly. It is an exploratory contrast for the recommendation.
   - The comparison is confounded: representation AND search both differ from TFS-1. This is stated in every
     rendering.
5. **Compute:** 1 worker; per-process CPU guard 840 s (resumable, exit 3); projection 2.4 core-h (bound 5.9). If the
   rolling cap is threatened, the run pauses and its readout is labelled PARTIAL.
