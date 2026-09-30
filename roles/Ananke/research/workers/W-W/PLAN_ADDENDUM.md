# W-W PLAN_ADDENDUM (POST-FREEZE; plan = roles/Ananke/research/plans/T-SWAP-REL4_PLAN.md, first added in
# 017259a48 2026-09-30T05:19:12-04:00, merged a7cba8221). Written 2026-09-30 ~09:25Z BEFORE any REL4 simulation.
# These are implementation readings of under-specified plan text, not changes to candidates/thresholds/grid.

D1 (H2 floor scale, literal reading). sd_floor = sqrt(1/(4K))/sqrt(P)*0.5 is applied exactly as written, to the
   bootstrap resample SD sd*_b (the pair-statistic SD, ddof 1), i.e. t*_b = (m*_b - m)/(max(sd*_b, sd_floor)/sqrt P).
   Note: the /sqrt(P) makes this floor SE-scaled although it is applied to an SD; it is therefore small
   (P64 K11: 0.0094). Implemented literally; not tuned. The original-sample sd=0 case keeps the REL3 point
   interval [m,m] (the plan floors only sd*_b).
D2 (H1 degeneracy test). "sd*_b = 0" uses REL3's own test bsd <= 1e-9. Share = fraction of the B=2000
   resamples; fallback iff share > 0.05, per statistic (DF and DN decided separately), to the 99% t-interval
   m +- t_{P-1,.995} sd/sqrt P (sd=0 -> point interval, as TINT in W-U).
D3 (H3 resampling). The pseudo-pair value 0 is appended to DF and to DN separately (P -> P+1 values); the
   REL3 BOOTT is then run on the P+1 values with resample counts boot_counts(P+1) (same seed-0 draw rule,
   B=2000), mean, sd and se all taken on the P+1 values.
D4 (seeds). FC simulation reuses W-U's exact data seeds ([10+stage, P, K, p*1000, z*1000+5000, model]) so
   that H0 must reproduce W-U's BOOTT counts EXACTLY where the same stage set is run (a stronger harness check
   than "within simulation error"). Stage-2 is triggered by the plan's candidates H0-H3 only (controls T90,
   PCT excluded, as W-U excluded T90); where W-U ran stage 2 and I do not (or vice versa), H0 is compared
   within simulation error. Power seeds: [41, P, K, p, z, model] (new), n=2000.
D5 (quantiles). Order statistics are taken with np.partition at the exact indices W-U's 'linear' quantile
   reads (identical values to full sort), for speed.
D6 (KA "recovers W-U's KA1/KA2/KA3 known answers"). Scored at the CERTIFICATE level of each candidate (label
   can only demote a certificate, so certificate-level false certificates are the stricter count), using
   W-U's validate3 cell construction and truths unchanged. PASS iff 0 false certificates in KA1, KA2 (P32/64/128)
   and KA3, AND the candidate issues the true verdict on every cell where W-U's H0 (BOOTT) issued it at the
   certificate level (recovery >= H0). REL3 label/p_min tables are not rebuilt for hybrids (no REACH curves in
   this plan).
D7 (s4.2/4.3 metric). "power" at p=.95/.99, P=64, K=11, realistic = the s3 power simulation (n=2000).
D8 (written 09:30Z, before any result was inspected) H0 is a listed candidate in s2; if it is eligible it
   competes in s4.2, and on an exact tie a hybrid is preferred (H1 < H2 < H3 < H0). If H0 is chosen, nothing is
   promotable (REL3 stays; s4.4).
