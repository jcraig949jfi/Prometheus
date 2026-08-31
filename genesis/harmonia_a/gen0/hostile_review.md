# Harmonia A Gen 0 — hostile-review packet

Kickoff §17 attacks, pre-registered in the freeze, answered against the
shipped rows. Attacks I could not fully discharge are marked OPEN.

| # | attack | disposition |
|---|--------|-------------|
| 1 | Alternate representation leaking consequence information | DISCHARGED. Every rep is a pure function of the truth table; no rep receives anything but f. Decode equality asserted at encode time (SHAM, TT), verified by census (ANF, C5). |
| 2 | "Small edit" defined circularly | DISCHARGED. Edit spaces enumerated mechanically in `bench.py` (hash journaled pre-run); no consequence value enters any edit definition. The ε grid was fixed and the primary named in the freeze before any row existed. |
| 3 | Decoder smoothing manufactures the result | INVERTED — smoothing is measured, not hidden. TT neutral rate IS the smoothing channel: 100% absorption at ε=0.125, 99.4% at 0.5. Since the verdict is a NULL, smoothing worked against the alternate rep, not for it. Pre-round L2 recorded per row. |
| 4 | Lossy reconstruction manufactures locality | DISCHARGED. Census C3: exact roundtrip 60/60 required and passed; runtime assertions abort on violation. |
| 5 | Random projection achieves the same result | CONFIRMED, and reported as a finding, not a defect: TT_SCR ≥ TT in local mass at every ε. Structure bought compression (45–128x), not reachability. Handoff §5d. |
| 6 | Comparing different objects | DISCHARGED. Same-object assertions on every encode path; any violation raises. |
| 7 | Result is simply more compute | DISCHARGED for the verdict (a null cannot be bought with compute). Costs shipped anyway: wall times and rep sizes in `results/arm_meta.json`. |
| 8 | Representation adds hidden primitives | DISCHARGED. All reps decode through the same evaluator into the same 1024-vector; the ruler sees only truth tables. |
| 9 | One-seed artifact | DISCHARGED STRUCTURALLY (D-13 B1 class): every cell has identical row counts (60 objects × 128), no join filter exists, per-seed tables shipped in `results/analysis.json`. |
| 10 | Cheap deterministic algorithm explains it | PRE-REGISTERED AS AN ARM. VT is that algorithm, run as the triviality ceiling and excluded from claim-bearing status in the freeze. |

## Attacks on my own design the kickoff didn't list

- **A. The population is degenerate (median 4 live variables), so the null is about toy objects.**
  Partially discharged, honestly bounded: the exploratory complexity gradient
  (handoff §5b) shows native local mass *rising* with complexity — the rescue
  predicts the opposite direction. But the population tops out at 8 live
  variables; a saturated-liveness regime is unmeasured. This is exactly Gen 1's
  controlled axis. Status: **OPEN at the family boundary, closed within it.**
- **B. The forced cells (ANF/VT/SHAM) make the run look bigger than it is.**
  Conceded and declared in the freeze §4 before running: the only empirical
  cells were NAT and TT/TT_SCR. The forced cells are harness controls and all
  reproduced their arithmetic (G_ANALYTIC PASS) — which is what makes the
  empirical cells trustworthy.
- **C. K=128 with replacement undersamples the 1056-edit native space.**
  True; sampling noise is bounded by the cluster bootstrap CI ([0.102, 0.137]
  on NAT local), and the G1 threshold (0.05) sits 6 CI-widths below the
  observed value. The verdict does not move under any resampling of this size.
- **D. The TT ε scale is rms-relative, so "small" differs across cores.**
  Correct, and mechanical (frozen §4). An absolute-δ variant is a legitimate
  successor arm; nothing in the null depends on the choice, since all three
  doses are reported and the largest dose still spills 25% FAR.
