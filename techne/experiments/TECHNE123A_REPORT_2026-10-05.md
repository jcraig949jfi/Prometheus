# TECHNE-123A -- Open-Oasis 500M as an experimental interactive world substrate: result

Techne[gandalf-4c0c7e64], M3, 2026-10-05. Operator directive 8. Preregistration:
TECHNE123A_PREREG_2026-10-05.md (Amendment A dated 11:10Z, before the production launch).
Runs: Flight 1 ...104502Z (PASS), Flight 2 ...105036Z (PASS), production attempt 1 ...110513Z
(FAILED, my save-path defect), production attempt 2 ...110938Z (PASS, the run of record).
Analysis: TECHNE123A_ANALYSIS_techne123a-oasis-20261005T110938Z.{json,txt}. Every number below is
from those committed files (E3) unless marked.

## 1. Answer in one paragraph (inside the claim ceiling of directive 8 s2)

Open-Oasis 500M, at the pinned code and official-hash weights, is bit-exactly replayable (same seed,
same action trace, same GPU: three replicate pairs identical at every one of 64 frames) and is
action-conditioned at short horizons: a sustained turn produces futures that differ from a forward
walk by more than two seeds differ, from frame 4 to frame 46 under the preregistered forward-walk
baseline, and through frame 63 under the secondary backward-walk baseline. It is NOT a long-lived
stateful world in this test: the divergence between two seeds under identical actions keeps growing
(latent MSE 0.40 at frame 8, 0.71 at frame 63), an eight-frame turn embedded in a walk leaves no
measurable trace beyond that seed noise at any later frame, forward and backward walks are not
distinguishable beyond seed noise, and 10 of 33 trajectories stall into a static image by frame 63.
The preregistered primary gate for action causality (75% of horizons) was NOT met (67%); the
secondary non-colliding baseline met it (100%). Reading: ACTION-SENSITIVE BUT RAPIDLY FORGETTING,
with a practical horizon of roughly 30-45 frames (1.5-2 s at the model's 20 fps) in this prompt.
It is usable for short-horizon, seed-controlled, action-conditioned experiments; it is not, on
this evidence, a substrate in which an intervention persists.

## 2. What was run

    candidate   etched-ai/open-oasis @ f59deef2c (MIT); DiT-S/2 607,943,792 params, ViT-VAE-L/20
                229,246,160; weights oasis500m.pt / vit-l-20.pt verified on the pod against the
                OFFICIAL Etched/oasis-500m LFS sha256 (fetched from an ungated hash-identical mirror
                because the official repo is gated); DDIM 10; context window 32 frames
    hardware    RunPod NVIDIA A40 48 GB at $0.49/h, stock image runpod/pytorch 2.4; torch 2.4.1+cu124
    prompt      the upstream sample image (sha256_lf e078b690...), one prompt only
    arms        6 seeds x {FWD, BACK, TURN, INTERVENE, NOOP} + 3 exact replicates = 33 trajectories
                x 64 frames = 2,079 generated frames; 1.096 s/frame mean (1.384 max), 42 min of pod
                time, $0.3427 estimated
    rulers      latent MSE per frame (16 x 18 x 32 cells) and pixel MAE on 90 x 160 frames; bootstrap
                (2,000 draws over pairs) 95% intervals on E(t) = D_cf(t) - D_same(t)
    spend       four pods: $0.0220 + $0.0915 + $0.0251 + $0.3427 = $0.4813 estimated of the $10 cap;
                provider billing so far: $0.0223 (Flight 1, x1.014 of estimate) and a partial $0.0162
                for Flight 2; the two production pods not yet in a billing bucket at 12:00Z
                (TECHNE123A_BILLING_2026-10-05.json; re-run `cli billing` later)
    credential  RunPod credential access: ESTABLISHED via Techne/Aether coordination; secret not
                persisted in experiment artifacts

## 3. Results against the preregistered rules

    Q1 REPLAY                 DETERMINISTIC. 3 replicate pairs (FWD_s0, FWD_s1, INTERVENE_s0): latent
                              MSE 0.0 and pixel MAE 0.0 at all 64 frames; latent sha256 equal.
                              Stochastic spread under the SAME action, different seeds (15 FWD pairs):
                              latent MSE mean 0.396 (t=8), 0.446 (16), 0.520 (32), 0.503 (48),
                              0.713 (63) -- large and still rising at the end. BACK pairs: 0.279,
                              0.243, 0.224, 0.252, 0.306 (bounded, not rising).
    Q2 TURN vs FWD (primary)  NOT_DETECTED by the 75% rule: interval excludes 0 for 40 of 60 horizons
                              (67%), frames 4..46 inclusive, peak E = 0.609 at t=19, E = -0.010 at
                              t=63. Pixel ruler agrees in shape (41 of 60 horizons, frames 4..44).
                              Read plainly: a clear causal effect through ~frame 45, lost in seed
                              noise afterwards.
    Q2 NOOP vs FWD            INDETERMINATE (rulers disagree): latent excludes 0 at 60 of 60 horizons
                              and grows to 0.399 at t=63; pixel at 29 of 60. NOOP holds the scene
                              static while FWD drifts; the pixel ruler is saturated by FWD's own
                              seed-to-seed texture differences.
    Q2 BACK vs FWD            NOT_DETECTED: 0 of 60 horizons; point estimates within [-0.05, +0.04].
                              Walking forward and walking backward are not distinguishable beyond
                              seed noise under these rulers.
    Q2 TURN vs BACK (secondary, Amendment A)   CAUSAL: 60 of 60 horizons; peak 0.858 at t=22;
                              E = 0.239 [0.152, 0.323] at t=63. With a normal arm that does not
                              collide with the tree, the turn's effect stays above seed noise to
                              the end of the window.
    Q3 PERSISTENCE            NO_EFFECT: P(t) never excludes 0 above for t >= 32 (peak 0.017 at
                              t=32); P = -0.199 [-0.338, -0.072] at t=63, i.e. the intervened
                              trajectory ends CLOSER to its forward twin than two seeds are to each
                              other. Read: an eight-frame turn inside a forward walk leaves no trace
                              beyond seed noise, in this prompt, under this baseline.
    stalls (descriptive)      10 of 33 trajectories have frame-to-frame latent change < 0.01 over
                              the last 8 frames: 5 of 6 NOOP (expected: no action, static world) and
                              5 of 6 TURN (the view pans onto uniform grass and stops changing).
                              0 of 8 FWD, 0 of 6 BACK, 0 of 7 INTERVENE.
    drift from prompt         latent MSE to frame 0 at t=63, mean per family: FWD 1.005, INTERVENE
                              0.966, TURN 0.918, BACK 0.658, NOOP 0.277.

Human inspection, descriptive only (TECHNE123A_PRODUCTION_strip_seed2_t0_16_32_48_63.png and the
Flight 2 strip): FWD walks into the birch and the view becomes wood and sand plates; BACK recedes
and keeps the tree, horizon and sky coherent to frame 63; TURN pans onto grass and then shows a
near-uniform green with a chest-like object; NOOP keeps the tree and stairs sharp and still.

## 4. What this does and does not establish

Established (E3): bit-exact replay on one GPU type; a short-horizon causal effect of a strong
action; growing seed-to-seed divergence under identical actions; no persistence of an 8-frame
intervention beyond seed noise; forward and backward walks not separable by these rulers; the
engineering facts (load 13 s, 1.1 s/frame at 64 frames, 5.4 GB GPU memory, $0.35 for 2,079 frames).

Not established: anything about a different prompt (one prompt only); anything about longer
interventions, repeated interventions, or interventions that leave an object in view (the turn here
happened while facing a tree trunk); replay across GPU types or driver versions (one SKU);
behaviour beyond 64 frames; anything the claim ceiling forbids. The preregistered primary Q2 rule was
not met, and the secondary baseline that met it was added after Flight 2 (dated, before launch,
with the reason); a reader who weights only the preregistered primary reads Q2 as NOT_DETECTED.

Confound to carry: the forward-walk family collides with the tree in this prompt, which both
inflates its seed spread (texture churn) and makes the intervention happen at a wall. That is a
property of this prompt + action design, found in Flight 2, disclosed before production, and not
repaired by re-choosing the prompt after seeing production numbers.

## 5. Recommendation

Do not adopt Open-Oasis 500M as a persistent world substrate on this evidence. Do consider it for
experiments that need only 1-2 seconds of action-conditioned, seed-replayable continuation from a
fixed prompt (for example an action-effect assay over many prompts), at about $0.0002 per generated
frame on an A40. The one follow-up that would move the Q3 reading is cheap and decisive: the same
design with BACK as the carrier and the intervention applied while the scene is in view, on three
prompts, ~$1. The one follow-up that would falsify "rapidly forgetting" is a longer intervention
(16-32 frames) measured against the BACK baseline. Neither is started.
