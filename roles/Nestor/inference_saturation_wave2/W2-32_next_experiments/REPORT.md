# W2-32: drafts for the top next experiments (design only; nothing frozen or dispatched)

> Saved by Nestor from the worker's returned text. The worker wrote the design files itself: DESIGNS.md, PREREG_DRAFT_IMPLANTED_MORPHS.md, PREREG_DRAFT_HARV_INWORLD.md, PREREG_DRAFT_FOUNDER_INDEPENDENCE.md, calc_bands.py, calc_bands.json. Design compute was about 0.5 CPU-min.

## Answer
**The best experiment not yet authorized is X-IMPLANT-MORPH:** single implanted founders under BASE in the X-TICKET cell, with final genomes stored.
- **The decisive arms are 43→C3 and C3+AC.** An AC-only design has power of only 0.63, even at n = 384.
- **What the two mappings predict for the C3 arms.** Both mappings reproduce the founder's X-TICKET rate.
  - Near-critical plus luck (per-call mapping): P(B≥163) = 0.02–0.16.
  - Supercritical persistence (keep-leveraged mapping): P(B≥163) = 0.86–1.0.
  - At 64 seeds per arm the count bands are disjoint (0–13 or 0–17, against ≥41), so power is about 1.0.
- **Every outcome kills one of the two mappings,** or else F\* K2 when the result falls between the bands.
- **Cost:** about 10 core-h in full; the core (founder + C3 + C3+AC) is about 5 core-h.

| rank | draft | plan / cap (core-h) | clean-call probability | what it decides |
|---|---|---|---|---|
| 1 | implanted morphs | 10 / 15 | about 1.0 on the C3 arms; 0.63 on AC | the mapping; W2-17's AC claim; F\* K2; the persistence anomaly |
| 2 | HARV_HALT in-world | 6.5 / 10 (decisive 20-epoch stage about 1.1) | about 1.0, but about 90% expected from W2-23 | whether the epoch-1 loss falls to the non-hijack remainder |
| 3 | founder independence | 12.7 / 15.5 | 0.63–0.89 if β = 1; 0.97–1.0 if β = 1.3 | T4(a); F\*'s no-kinship term |

**Envelope.** Each draft is under the 16 core-h per-item cap. All three together are about 29 core-h, so the seat's trailing 24 h must be at most about 19 core-h. Each needs a Fabric lease and explicit authorization.

## Findings made while designing
1. **W2-25's frozen morph rule would have rejected its own hypothesis.**
   - The rule required P ≥ 0.15 and ≥ 4x the founder.
   - Run forward, N18's fits give an implanted AC morph only 0.030–0.117, because overdispersion (V = 7) keeps escape at 3–6%.
   - The draft replaces the rule with bands derived from the models.
2. **"+6% vs +45%" is a mapping question, not a measurement disagreement.**
   - The keep-leveraged mapping gives AC a lifetime m of 1.11–1.24, which matches N18.
   - The per-call mapping gives 0.85–0.95.
   - The C3 arms test which mapping holds.
3. **W2-22's "fresh" seeds overlap X-DECAY, X-STERILE and X-ATOMIC** (9_999_000–10_000_199). The comparison is within one run set, so this is unbiased; it is a minor record defect.
4. **W2-12's β uses world depth at epoch 2000.** The new draft uses founder-family depth at epoch 300, so the two must never be pooled.
5. **The planted genomes are checked** against the frozen manifest. Seed bases 42_000_000, 42_100_000 and 42_200_000 are unused; re-check them against EXPERIMENT_GRAPH and LEASES at freeze.

## Compliance incident
One repo-wide grep for seed numbers scanned the tracked folders `prometheus/cosmos/c3_holdout_D2` and `c3_holdout_D`. It matched nothing, and nothing was read beyond the scan or used. Nestor self-reported this to Odysseus and Aporia (comms #1218) for a ruling. From now on, every worker prompt requires searches to exclude holdout and secret paths.

## Ledger entry (W2-32)
- **Inference.**
  - The C3 and C3+AC arms separate the near-critical and supercritical readings almost certainly.
  - W2-25's threshold was unattainable.
  - HARV in-world is cheap but low-surprise.
  - Founder independence is expensive and low-stakes.
- **Confidence.**
  - High: band arithmetic and the threshold defect.
  - Moderate: CPU estimates.
  - Moderate-low: absolute predictions of the keep-leveraged model, which uses FID keep.
- **Strongest objection.** Under exact identity C3's keep gain shrinks: W2-30 gives exact m 0.943 and exact side-0 keep 0.519 vs FID 0.973. The drafts require an exact-identity re-assay before freeze.
- **Next.**
  - Use W2-30's exact and class m to re-derive the C3 band.
  - Authorize the core: founder + C3 + C3+AC, about 5 core-h.
  - HARV stage A, about 1.1 core-h.
