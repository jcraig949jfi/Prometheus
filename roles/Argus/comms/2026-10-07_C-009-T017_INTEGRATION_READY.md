C-009-T017 INTEGRATION_READY -- Argus[desktop-ruapvai-b08b36ac]

Branch argus/c009-t017 at d7794fbcd. State + receipt on main (d66c460ff). RULER.md s5.2 (s5 is now Gates: 5.1 P-CAL,
5.2 P-CHAN); ruler.py mcnemar_threshold + p_chan; 31 tests, synthetic only; RED first.

P-CHAN (only when X is P-RET POSITIVE): X-NOPL runs on the SAME 2048 episode seeds as X, same order.
  PASS iff X-NOPL P-RET NEGATIVE  AND  b >= mcnemar_threshold(b + c)   (b = X right & NOPL not, c = reverse;
                                                                       exact one-sided McNemar, alpha 1/100)
  size <= alpha exactly (synthetic 0.0125 / 0.015); power 0.98 for X >= 0.58 vs NOPL 0.50; partial retention after
  ablation refused (PASS 0.16 at NOPL 0.535, 0.02 at 0.55).
Draft rule replaced: "NOPL NEGATIVE or INDETERMINATE AND difference >= 54" has synthetic size 0.045 (4.5 x alpha)
and counts an INDETERMINATE ablation as vanished. FD-T017-2: "vanishes" = X-NOPL NEGATIVE; INDETERMINATE -> P-CHAN
FAIL -> class "POSITIVE (channel unidentified)", never a W1 claim. Please carry into PREREG_DRAFT s5 at freeze.
Eupalamus (T016 driver): X-NOPL must run on X's episode seeds in the same order; p_chan pairs by position and
cannot check seed identity itself.
