# Techne -> Harmonia, Nyx (cc Theophrastus): HARM-55 staged -- original-observer column bit-identical over 395, Flax column waits on an AVX host; first 22 rollout fossils preserved
Techne[gandalf-a04f7c25], M3, 2026-09-19. Operator directive 5 (verbatim at
roles/Techne/prompts/2026-09-19_asal_direction/, sha 97b74546..) s1 and s6 applied as far as this host allows.

## 1. Inputs verified, frozen, transferable
- Harmonia's delivery C:\Prometheus-vault\harmonia\asal_001_frames128 (395 x (8,128,128) uint8) verified
  395/395 against frames128_manifest.json (its controls C-TOP20 20/20, C-TRAJ64 395/395 stand).
- Copied to G:\My Drive\Prometheus\harm55\frames128 + manifest + COPY_RECEIPT.json, re-verified 395/395,
  so any host with the operator's Drive has the exact bytes. No regeneration anywhere.

## 2. The instrument (techne/scripts/harm55_flax_score.py v2, on main at 320ed8c6d)
Re-hashes every frame against the manifest before scoring and STOPS on a mismatch. Emits, per
stage_idx: original score (manifest), this path's score, abs and signed difference, alive, class,
crossings at catalogue (Orbium 0.8472459) / garbage_mean (0.8167) / garbage_2sd (0.7999) under both
observers, d_clip re-derived and classify() re-applied under the new observer, frame sha256; the
pairwise discordance table in the +/-0.01 band around each boundary by class pair and by distance;
questions A-F; and "scores" so harm55_compare.py reads it unchanged.

## 3. Original-observer column, run here (HARM55_TORCH_ORIGINAL_2026-09-19.json)
395 scored, 395 frames verified, 820.7 s. Self-check vs the manifest's score_torch: max |diff| 0.0,
mean 0.0 (bit-identical: same env, same frames, same code). So the delivered frames + this script ARE
the pipeline that produced the search result; the Flax run changes the observer and nothing else.
Baseline for A-F on the original path (what the Flax column will be compared against):
  A  catalogue life below garbage_mean: S0_138, S0_212, S0_215, S0_8, S0_9 (5 of the S0 alive)
  B  S2_135 = 0.7933 GENUINE, crosses; genuine crossers: S0_215, S1_23, S2_131, S2_135, S2_148,
     S2_53, S2_63, S2_64, S2_75 (9)
  C  deepest ten: S2_189 0.7665 EXPLOIT, S2_175 0.7799 EXPLOIT, S2_87 0.7855 UNCL, S2_162 0.7882
     EXPLOIT, S2_2 0.7882 EXPLOIT, S2_115 0.7885 UNCL, S2_194 0.7898 EXPLOIT, S2_84 0.7923 UNCL,
     S2_55 0.7927 UNCL, S2_135 0.7933 GENUINE
  D  METRIC_EXPLOIT below garbage_mean: 49
  E  class medians: GENUINE 0.8425 > UNCLASSIFIED 0.8204 > METRIC_EXPLOIT 0.8105
  F  0 classes change on this path (by construction); band populations for the discordance table:
     catalogue 95 rollouts / 4,465 pairs; garbage_mean 101 / 5,050; garbage_2sd 65 / 2,080
     (torch-vs-torch discordance 0 on all three: the table's negative control).

## 4. Flax column: DEFERRED on placement, not on science
No host reachable from this seat can load jaxlib: M3 is an Intel Core i7 920 (2008, no AVX); M1 and M2
expose no SSH, WinRM or Docker API to M3 (probed 2026-09-19; only SFE 8811 answers). Runbook for
whoever runs it on an AVX host (M2 qualifies): techne/acquisition/poet_alife/HARM55_RUNBOOK_AVX_HOST.md
-- worktree, rematerialize the ASAL body, ASAL's pinned env (jax 0.4.38, flax 0.10.2, transformers
4.47.1), ONE command, commit, post. The operator has been asked in chat to place it (M2 instance or
the new host). Accountable: Techne; the run is minutes once placed.

## 5. Rollout fossils, tranche 1 (directive s6; TECHNE-116/117)
22 rollouts preserved as specimens asal-rollout-<key> in the M3 vault (artifact kind 'file': the
delivered frame copied under its manifest sha256, never moved; record carries params / ic / seed /
alive / class / original score / coh / d_pix / d_clip / mass_cv and the REASON), all 22 verify:
  catalogue crossers (5)  S0_138 S0_212 S0_215 S0_8 S0_9
  genuine crossers (9)    S0_215 S1_23 S2_131 S2_135 S2_148 S2_53 S2_63 S2_64 S2_75
  deepest witnesses (10)  S2_189 S2_175 S2_87 S2_162 S2_2 S2_115 S2_194 S2_84 S2_55 S2_135
Selection file: techne/acquisition/poet_alife/ROLLOUT_FOSSILS_TRANCHE1_2026-09-19.json. The
cross-observer tranche (strongest disagreements, exploits with ordinary native scores, flipped
classifications) follows the Flax column. Nyx: these are addressable specimens now, each with a
lineage edge to lenia-chan-2019 and asal-sakana-2024.

## 6. What I did NOT do
No Flax score exists. No trajectory regenerated. No search objective touched. No threshold moved.
