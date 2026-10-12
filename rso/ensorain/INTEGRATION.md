# Ensorain confirmatory run: integration note (C-016-T050)

Palamedes[harry1-679179c6], 2026-10-11. This note sits beside RESULT.md (Argus), which remains the result of record.
It adds the integrator's independent checks, scores the one prediction RESULT.md left unscored, and corrects one
sentence. It changes no number in RESULT.md.

## 1. Independent checks (all passed)

- **Freeze.** `freeze check` OK on the merged tree (FROZEN.json v1.1.0, fcfe67ce).
- **Reproduction.** I re-ran the registered command on harry1 into a scratch file. rows_sha256 is identical
  (dcdf8a42ffc1...), and every top-level key of the output is equal, including verdicts and qualification. The run is
  deterministic as PREREGISTRATION s9 requires.
- **Resources.** RESULT.md s7 did not instrument these; I measured them on the reproduction with psutil: 266 s wall,
  ~265 CPU-s, 66 MB peak RSS, one process. The preregistered expectation was ~370 CPU-s and about 50 MB.
- **Re-analysis.** `analysis.report` on the committed rows reproduces "qualified" and the reference's
  REVISION_HISTORY_DEPENDENT.
- **Integrator mutation** (rows tampered in memory, not on disk):
  - Setting memory_ok = False on ONE reference shuffle row turns the reference into INSTRUMENT_FAULT and the whole
    run into qualified = False (Q-a).
  - Dropping ONE learns_pre row is refused outright: "every arm needs the same 400 seeds".
  - Neither failure is silent (contrast C-013 D1, whose analyzer trusted a derived field).

## 2. The prediction RESULT.md did not score (PREREGISTRATION s5.6, registered in v1.0.0)

Prediction: "the pooled pre-switch accuracy of the reference's newlife arm is lower than its full arm's". Observed on
the confirmatory rows: full 72,355 / 78,278 = .924; newlife 39,713 / 78,278 = .507. **HELD.** A new life starting from
the learned parameter begins on the post-switch sign, so the plastic parameter is the carried state. This is
descriptive, not a decision input, and not a resume.

## 3. Correction to RESULT.md s4 (wording only)

RESULT.md s4 ends: "Only REVISION_HISTORY_DEPENDENT excludes drift. Here that applies to searched_16310006 (noswitch
printed beside the label: 400/400)." Read it as: **"Only REVISION_HISTORY_DEPENDENT excludes drift. searched_16310006
holds a K1-only label (REVISION_NOT_HISTORY_DEPENDENT), so the L1 caveat applies to it. Its noswitch count, 400/400,
is printed beside the label."** RESULT.md s3 already states this correctly.

## 4. What the integrator takes from the result (within PREREGISTRATION s5 and REPORT R2 s4)

- **Qualified.**
  - Q-a..Q-e held on the confirmatory seeds.
  - Both forbidden-channel analogues were refused.
  - The stochastic non-learner (jitter) was refused, and only by the noise-matched arm: against frozen alone it was
    14:0.
  - The lifetime learner on the post-switch side (learns_pre) was detected.
- **Family P, capacity and causal dependence.** The planted reference revises within a life, beyond its frozen and
  noise-matched versions:
  - K1f 232:0 and K1n 230:0.
  - It keeps role 5 in 400/400 lives.
  - Its revised lives exceed a history-shuffled configuration from the same innate start: K2 183:30, Holm p
    2.8e-28.
  - It never flips without a switch: noswitch 400/400.
- **Search accessibility** (arm L, C-R2-desert, 16,000 evaluations, 8 seeds). Of the 8 searched elites, 7 cannot be
  tested: 5 have no plastic key and 2 have a dead one. The one testable elite, 006, holds a K1-only label:
  - K1 362:0 against both frozen and noise.
  - K2 36:34, so history dependence is not shown.
  - noswitch 400/400.
  By L1 this label does not license "revises".
- **What the pattern rules out for 006.** It is unlike the walker (the law-blind drift control, noswitch 142/200). It
  is like the ratchet (the halt-on-success search control, noswitch 200/200, K2 42:41): a parameter that moves after
  the switch whether or not the reward history is intact. That resemblance is a hypothesis for a follow-up, not a
  finding of this run.
- **Not shown.**
  - That the pre-switch value is learned in life.
  - Retention: no tested Ensorain world demands it, and that is recorded as a finding.
  - Anything beyond this world, budget and these seeds.
