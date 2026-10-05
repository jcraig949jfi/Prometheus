# TECHNE-123A -- Open-Oasis 500M as an experimental interactive world substrate: experimental draft

Techne[gandalf-4c0c7e64], M3, 2026-10-05. Operator directive 8 (roles/Techne/prompts/2026-10-05_techne123a/).
Committed BEFORE any paid flight. Frozen for the production run at the commit that records Flight 2's
disposition; until then the arms and rules below may be tightened by what the flights expose, and every
change is a dated edit of this file, never a silent one.

## 0. Candidate, pinned

    code      github.com/etched-ai/open-oasis master @ f59deef2c019c212bd0c5a3a5b986a51f3701847 (2024-11-08, MIT)
              five source files vendored unmodified under oasis/ with per-file sha256 (oasis/PROVENANCE.json)
    weights   Etched/oasis-500m @ 4ca7d2d8 is GATED on Hugging Face (401 without a logged-in account).
              camenduru/oasis-500m @ b40bf434 is ungated and its oasis500m.pt / vit-l-20.pt carry the SAME
              LFS sha256 as the official files (7890c09c...9486 and bd9edac4...b220, read from both repos'
              API listings). The module downloads from the mirror and REFUSES to load unless the bytes hash
              to the OFFICIAL sha256. Grade of the weights read: CONTEMPORARY_COPY, hash-identical.
    model     DiT-S/2 (16 latent channels, 18x32 latent grid for 360x640 frames), ViT-VAE-L/20; the DiT
              conditions on at most max_frames = 32 previous frames (sliding window); 25-dim action vector
              per frame (one-hot keys + camera yaw/pitch in [-1, 1]); DDIM 10 steps per frame, noise level
              15 for context frames (upstream generate.py, reproduced in run.py:rollout, seeded).

## 1. Questions (operator s1) and how each is read

Q1 REPLAY. Same prompt, same action trace, same seed, same configuration: how reproducible is the
   trajectory?  Rulers: REPLICATE pairs (label X vs X_rep). Read:
     DETERMINISTIC     latent_sha256 identical, or latent MSE == 0 at every frame
     BOUNDED           latent MSE(t) stays below the SAME_ACTION_DIFF_SEED band at every frame
     UNCONTROLLED      replicate MSE(t) reaches the different-seed band
   plus the STOCHASTIC SPREAD: SAME_ACTION_DIFF_SEED pairs (FWD_si vs FWD_sj): the curve
   D_same(t) with its spread over pairs. This band is the null for Q2 and Q3.

Q2 ACTION CAUSALITY. Same prompt, same seed, different action family: do futures differ beyond the
   same-action stochastic variation?  Statistic, per horizon t:
     E(t) = D_cf(t) - D_same(t)
   where D_cf(t) is the latent MSE between FWD_s and TURN_s (same seed s) and D_same(t) the latent MSE
   between FWD_si and FWD_sj (different seeds), both averaged over the available pairs, with a
   bootstrap (resample pairs, 2000 draws) 95% interval on E(t). Read:
     CAUSAL            E(t) > 0 with the interval excluding 0 for >= 75% of horizons t in [4, T-1]
     NOT DETECTED      otherwise
   Pixel MAE on the 90x160 frames is reported beside the latent MSE as the second ruler; the two must
   agree in sign or the reading is INDETERMINATE.
   Controls: NOOP_s vs FWD_s is a second counterfactual (a weaker action); its E(t) is reported, not
   gated. If E_NOOP(t) ~ E_TURN(t) the model may not be reading actions at all, only noise.

Q3 PERSISTENCE HORIZON. INTERVENE_s equals FWD_s for frames 1-23, turns for frames 24-31 (cameraX
   0.5, forward off), then resumes FWD. Same seed as FWD_s. Statistic, for t >= 32:
     P(t) = D_intervene(t) - D_same(t)
   Read:
     PERSISTENT        P(t) stays above 0 (interval excluding 0) through t = T-1 (T = 64 in production,
                       which is 32 frames past the end of the intervention and past the context window)
     DECAYING          P(t) is above 0 just after the intervention and the horizon h* = the last t with
                       the interval excluding 0 is reported as the practical persistence horizon
     NO EFFECT         P(t) never excludes 0
   "Visually persistent but causally shallow" is the case where pixel MAE persists while latent MSE
   decays, or TURN diverges but INTERVENE's post-turn difference does not; it is reported as such.

Claim ceiling: operator s2. The strongest positive statement is that Open-Oasis exhibits stable,
action-conditioned, persistent generated state sufficient to justify further Prometheus experiments
using it as an external interactive substrate. Nothing about physics, memory in any mental sense,
intelligence or generality.

## 2. Arms (all from the upstream sample prompt oasis/sample_image_0.png; T frames; seeds s = 0..K-1)

    FWD_s        forward = 1 every frame
    TURN_s       cameraX = 0.25 every frame (about +5 degrees of yaw per frame), no forward
    NOOP_s       all actions zero
    INTERVENE_s  FWD, except frames 24-31: forward 0 and cameraX 0.5 (an eight-frame turn), then FWD
    X_rep        exact replicates (same seed) of FWD_s0, FWD_s1, INTERVENE_s0

    flight1      FWD_s0, FWD_s0_rep, TURN_s0                      T = 32    3 trajectories,  93 frames
    flight2      s in {0,1} x {FWD, TURN, INTERVENE} + FWD_s0_rep + NOOP_s0   T = 64   8 traj, 504 frames
    production   K = 6 seeds x {FWD, TURN, INTERVENE, NOOP} + 3 replicates    T = 64   27 traj, 1,701 frames

Pairs read from each plan (run.py:pairs_for): REPLICATE, SAME_ACTION_DIFF_SEED (all FWD pairs),
COUNTERFACTUAL_TURN / _NOOP / _INTERVENE (each against FWD at the same seed).

## 3. Measurements (operator s3: simple rulers, computed on the pod into result.json and again on M3)

  - latent MSE per frame between two trajectories (mean over 16 x 18 x 32 latent cells, float32 math
    on the stored float16 latents);
  - pixel MAE per frame on the 90x160 downsampled decoded frames (0..1);
  - per-frame generation seconds; GPU, torch, CUDA, cudnn.deterministic flag; peak GPU memory.
  No learned evaluator. Human inspection of frame strips is descriptive only.

## 4. Stop rules

  spend     total RunPod spend cap $10 (operator). Flight 1 <= 1 paid hour, budget guard $0.75.
            Flight 2 <= 1 paid hour, guard $0.75. Production: max_runtime_s set from Flight 2's
            measured seconds per frame x 1,701 x 1.5, capped at 4 h; budget guard $3.00. If the
            projection from Flight 2 exceeds $3.00, K drops to 4 (19 trajectories) before T drops.
  time      production wall-clock ceiling 12 h (operator); a pod is reaped at the end of every flight.
  flight 1  stops at the first of: WEIGHTS_HASH_MISMATCH (refuse, do not load), model load failure,
            canary failure, > 30 s per generated frame (MODEL_NOT_RUNNABLE_IN_ENVELOPE at T = 64 x 27),
            artifact not retrievable to M3 (EVIDENCE_CUSTODY_BLOCKER).
  science   no arm, seed, horizon or threshold above changes after a production score is seen; a change
            found necessary after Flight 2 is a dated edit here BEFORE the production launch.

## 5. Projected remote compute (E0 until Flight 1 measures it)

  A40 48 GB at $0.49/h (Aether COST_MODEL). Weights 3.3 GB download + pip + load: ~5-8 min. Generation:
  unknown; DiT-S/2 over <= 32 context frames x 10 DDIM steps per frame; a guess of 0.3-1.0 s/frame gives
  Flight 1 ~ 1-2 min of generation, production ~ 10-30 min. Projected total spend < $3 across all flights
  if the guess holds; Flight 1 exists to replace the guess with a measurement.

## 6. Evidence paths

  module (bundle identity)   techne/experiments/techne123a/{run.py, module_spec.json, oasis/}
                             bundle sha256 in the receipt; built copy under Aether/runpod/examples/dist/
  receipts                   Aether/runpod/receipts/<run_id>.json (+ <run_id>/ with telemetry, platform
                             samples and every artifact <= 1 MB: result.json, telemetry.jsonl)
  large artifact             trajectories.npz (latents float16 + frames uint8 + actions), kept by the
                             controller outside the repository (<checkout parent>/Prometheus-data/
                             runpod_artifacts) with path + sha256 in the receipt's large_artifacts
  analysis on M3             techne/experiments/techne123a_analyze.py over result.json (and the npz when
                             present) -> techne/experiments/TECHNE123A_ANALYSIS_<run_id>.json + a text table
  credential                 the record says only: RunPod credential access ESTABLISHED via
                             Techne/Aether coordination; secret not persisted in experiment artifacts.

## 7. What Flight 1 must show (operator s6, items 1-11) and its disposition vocabulary

  GPU type and rate (receipt), code revision (PROVENANCE.json), weights identity (result.json
  weights.*.sha256_official verified true), model loaded (result.json model.*), one trajectory
  (FWD_s0), evidence retrieved (receipt artifacts_verified), analyzable on M3 (analyze.py runs on the
  receipt copy), pod destroyed (receipt cleanup.observed_absent), dollars (receipt cost.usd_estimated;
  billing reconciliation later per Aether's rule).
  Disposition: FLIGHT1_PASS | DEPENDENCY_BLOCKER | MODEL_LOAD_BLOCKER | EVIDENCE_CUSTODY_BLOCKER |
  COST_BLOCKER | MODEL_NOT_RUNNABLE_IN_ENVELOPE.
