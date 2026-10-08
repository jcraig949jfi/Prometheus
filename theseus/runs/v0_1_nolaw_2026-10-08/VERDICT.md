# THESEUS-28 verdict (prereg roles/Theseus/prereg/2026-10-08_law_ablation/, df2cf1acd;
# code governed by 0b8e3740b's CODE_SHA256, defaults only)

Run: PYTHONHASHSEED=0 python -m theseus.synth.run_v0 --tag v0_1_nolaw_2026-10-08 --no-law
--ecology-only --workers 4. Ecology wall 1510 s, CPU 5108 s. Analysis:
python -m theseus.synth.r5_trend v0_1_2026-09-30 v0_1_nolaw_2026-10-08 (R5_TREND_vs_v0_1.json).

Viable DEEP+VERY_DEEP children: ON (v0_1) 338, OFF 311.
  rho_ON  = Spearman(generation, R5) = +0.027 [-0.080, 0.137]
  rho_OFF = -0.109 [-0.221, 0.001]
  rho_OFF - rho_ON = -0.136 [-0.294, 0.004]
  medD ON .727 [.727, .773]; OFF .727 [.727, .773]; difference 0.000 [-0.045, 0.045]
  viable fraction ON .774 (908/1173), OFF .762 (894/1173); max generation 28 vs 26.

Verdict by the frozen rule: NO-EROSION-TO-EXPLAIN (rho_ON CI contains 0). The deep-vs-
one-shot R5 gap (23a post-hoc, AUC .438) is a LEVEL difference of the deep lanes, not a
decline with generation; removing the generated law does not raise R5 (if anything rho
falls). Predictions L1, L2, L3 all WRONG (ledger).
