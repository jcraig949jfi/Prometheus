# HT-e106e1603b / W5 -- probe round 3 implementation notes

Prompt: hecate/programs/_prompts/probe_impl_v3.md (sha256 a34a8c61...1685),
{TID}=HT-e106e1603b, {W}=W5. Bound by roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md
and roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Written BEFORE any treatment statistic existed. spec.json, controls.py,
ATTAINABILITY.json, control_rows.jsonl are frozen and not touched.

## Arms (world.py)

All arms import controls.py and use its make_graph(seed), channel(cv, seed),
arm_t(arm, w, s, seed) and g_statistic(w, s, t, seed) unchanged, so graph,
channel draw, features, folds and G are one code path. controls.main() is
NOT called (it would rewrite the frozen control_rows.jsonl); the three
control arms are re-run through arm_t + g_statistic inside world.py.

- POSITIVE_CONTROL, NULL_TWIN, CHEAT: controls.arm_t, unchanged.
- TREATMENT: t = real min-sum iteration count, decoder below.

Seeds 0-4 (spec), 3000 blocks each, n=504, cap 60. One row per
(arm, seed) in rows.jsonl, flushed per row. Per-block (p, w, s, t) for the
treatment saved to treatment_blocks_seed{k}.npz for evaluate.py (F2,
diagnostic and secondary report).

## Decoder (treatment)

Flooding min-sum on the hard received word, all-zero codeword.
- Channel LLR: +1 for received 0, -1 for received 1 (fixed magnitude 1;
  min-sum is scale-invariant, so the magnitude is arbitrary and the
  decoder never sees p or w).
- Init: variable-to-check Q = channel LLR on every edge.
- Iteration: check-to-variable R = (product of signs of the other 5
  incoming Q) * (min of |Q| over the other 5); variable total =
  LLR + sum of the 3 incoming R; hard decision; if its syndrome is zero,
  stop, t = that iteration number; else Q = total - R (extrinsic).
- t = 0 if the received word's syndrome is already zero; t = 60 if no
  zero syndrome by iteration 60.
- Plain min-sum: no normalisation, no offset, no damping (spec says
  "min-sum"; any correction factor would be an invented parameter).
- Float64 messages.

## Ambiguities and readings chosen (no threshold changed)

1. Sign of a zero-valued message: taken as +. It cannot change any
   output: a zero |Q| makes the min (hence R magnitude) of every other
   edge at that check zero, and it is excluded from its own outgoing
   sign.
2. Hard decision when total LLR == 0 (possible, messages are integers):
   fall back to the received hard bit. Recorded; the alternative (0)
   would bias toward the known codeword.
3. "Converged" = zero syndrome of the hard decision, as the spec says;
   a zero syndrome at a non-zero codeword (decoder error) still stops
   the decoder. The count of such blocks is reported as a diagnostic.
4. F2 ratio: median t over blocks with 0.06 <= p <= 0.09 divided by
   median t over blocks with 0.02 <= p <= 0.04, pooled over seeds 0-4,
   closed intervals. If the denominator median is 0 the ratio is +inf
   (numerator > 0) or undefined (both 0 -> treated as F2 holding,
   "no slowing down"); recorded if it happens.
5. Positive control "detected" = PC meets S1 and S2 and not F1 (F2 is a
   decoder-premise clause, applied to the treatment only; its value for
   the synthetic arms is reported for information). Cheat detected =
   cheat meets S1 and S2. Null twin meets success = twin meets S1 and S2.
6. Reproducibility check: evaluate.py recomputes S1/S2 on the re-run
   PC and twin rows and compares attainable/discriminating with
   ATTAINABILITY.json; any difference -> INSTRUMENT_FAIL. Numeric
   deviation of per-seed control G from ATTAINABILITY.json beyond 1e-9 is
   also recorded as an anomaly (not by itself a fail).
7. Outcome order (in code): reproducibility mismatch -> INSTRUMENT_FAIL;
   PC or cheat not detected -> INSTRUMENT_FAIL; twin meets success ->
   CONFOUNDED; treatment S1 and S2 and neither F1 nor F2 -> SIGNAL;
   otherwise NULL (G in [0.05, 0.20) without S1 marked "weak").
8. Secondary (not a clause, spec's alternative_explanation): G with t
   replaced by 1[t = 60], same g_statistic path.
9. CPU: OMP/BLAS threads pinned to 1; core-minutes = process CPU time.
