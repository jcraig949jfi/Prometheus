# T-M2-2  What sets M2's echo interval, and can a PTE law hold several?

QUESTION. M2 is a tuned two-stage echo: accuracy peaks at the trained gap
(6-8) and is at chance for gap >= 12 in all 4 champions (S-M2b). Is the
interval fixed by the program's pipeline depth, by physics (latency,
update period, hop distance), or by both? Can evolution find a law that
holds a bit across SEVERAL gaps?

WHY. It decides whether PTE's in-flight carriers are only interval-tuned
delay lines, or can become interval-general memory. That matters for any
future memory campaign (C2, SI01).

EVIDENCE. ../SPIKES_2026-09-27_LOG.md (S-M2b table). The decompiled
program is in ../C1B_REVIEW_AND_MECHANISMS.md s2 (PAY0 := SENSE;
PAY1 := IN0_0; S0 := IN0_0 + IN0_1; always emit). Physics: ring N=144
r=3, sync update_period 2, lat 1 + 1*hop + jitter 1, loss .1, cap 2
saturate. Prior art: delay lines and fiber-loop buffers (../PRIOR_ART s1).

STEPS
1 Predict the round-trip time from the program and physics: two hops of
  (lat_base + hop*d + jitter), plus the sync wait. Write it in the PLAN.
2 Re-evaluate the 4 champions (specimen + champions_m2.json) with the
  gap swept 2..16 under lat_base in {0,1,2} and update_period in {1,2,3}.
  Does the accuracy peak move as predicted? (~100 short runs; CPU is ok.)
3 Only if step 2 shows physics-set tuning: a small evolution (C1
  SearchSpec, 4 seeds) with the gap drawn per trial from {6,8,10,12}.
  Does a multi-gap law appear, and what is its carrier (lens swaps)?

DECISION. "physics-set" if the peak moves with the predicted round trip
in >= 3/4 champions; "program-set" if it does not move. Label step 3's
outcome by carrier-swap verdicts.

DELIVERABLES. PLAN, LOG, spikes/s_t_m2_2*.py, out/*.json, a one-page
result; update the backlog entry.

STOP. 3 h of wall time. Skip step 3 if step 2 is inconclusive.
