# HARM-55 runbook -- the native (Flax/JAX) ASAL observer over the 395 preserved rollouts, on any AVX host

Operator directive 2026-09-19 s1. Everything below is staged; the host is the only missing piece
(GANDALF/M3 is a 2008 Core i7 920: no AVX, jaxlib refuses to load; no SSH/WinRM/Docker API is open on
M1 or M2 from M3, so Techne cannot place the job remotely). One person on one AVX host runs this once.

## 0. What the host needs
- x86-64 with AVX (any machine newer than ~2011; M2 SPECTREX5 qualifies), Python 3.10 or 3.11, git,
  network to github.com, huggingface.co and pypi.org. ~1 GB disk (CLIP weights 600 MB + env).
- The frames: G:\My Drive\Prometheus\harm55\frames128\<key>.npy (395 files, uint8 (8,128,128)) and
  ..\harm55\frames128_manifest.json beside them (Harmonia's manifest, also on main at
  roles/Harmonia/science/asal_ruler/out/run_2026-09-18/frames128_manifest.json). COPY_RECEIPT.json
  records that the copy verified 395/395 against the manifest on M3. The script re-verifies every
  file's sha256 before scoring and STOPS on any mismatch (directive s1: never score altered frames).

## 1. Worktree (WORKING_CONTRACT s1-s3; never in the canonical checkout)
    git -C <canonical> fetch origin
    git -C <canonical> worktree add <worktrees>\techne-harm55 -b techne/harm55-<host> origin/main
    cd <worktrees>\techne-harm55
    set EW_DB_HOST=192.168.1.202          (comms boot/sync as Techne, per the wake directive)

## 2. The ASAL body (the observer is imported from it, unmodified)
    python -m techne.fossils.harvest rematerialize asal-sakana-2024      -> MATCH (tree 188a6ada..)
  (needs git; fetches SakanaAI/asal@677ba0ea + the 3 npz; ~46 MB)

## 3. Environment (ASAL's own pins; nothing else)
    python -m venv <toolcache>\asal_flax && <toolcache>\asal_flax\Scripts\activate
    pip install "jax==0.4.38" "jaxlib==0.4.38" "flax==0.10.2" "transformers==4.47.1" "einops==0.8.0" \
                "numpy<2.3" "pillow" "huggingface-hub" "safetensors"
    python -c "import jax; print(jax.devices())"                          -> [CpuDevice(id=0)]
  (Windows Defender / your host's scan on the env: standing order 7.)

## 4. Run (one command; ~395 x 8 CLIP forwards, minutes)
    python techne/scripts/harm55_flax_score.py --path flax \
        --frames-dir "G:\My Drive\Prometheus\harm55\frames128" \
        --out techne/acquisition/poet_alife/HARM55_FLAX_NATIVE_<date>.json
  Output: schema techne.harm55.scores/2 -- per-row original vs flax score, abs/signed diff, alive,
  class, crossings at catalogue / garbage_mean / garbage_2sd under both observers, d_clip and the
  re-derived class under Flax, frame sha256; the pairwise discordance table in the +/-0.01 band; the
  six questions A-F; and "scores" so Harmonia's harm55_compare.py reads it unchanged:
    python roles/Harmonia/science/asal_ruler/harm55_compare.py --flax techne/acquisition/poet_alife/HARM55_FLAX_NATIVE_<date>.json

## 5. Commit and post (explicit paths, message file; push branch:main after tests; verify ancestor)
    git add techne/acquisition/poet_alife/HARM55_FLAX_NATIVE_<date>.json
    python -m comms post --from "Techne[<tag>]" --to Harmonia,Nyx --kind report --subject "HARM-55 native Flax scores: 395 rollouts" --body-file <the json>

## What must NOT happen on the scoring host
No regeneration of trajectories; no change to seeds, sampling, frame timing or preprocessing; no
edit to foundation_models/clip.py or asal_metrics.py in the body; no "fixing" of a frame that fails
its hash (report it and stop).
