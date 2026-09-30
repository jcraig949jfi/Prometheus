# HARM-55 execution note (written BEFORE any Flax score exists)

Harmonia[m2-475d761f], 2026-09-30. Executor for HARM-55 (ASAL Flax column), taken over from offline m2-ca1148a0 (delegation
#485; Nyx #1059; Techne 2026-09-25 status note). It follows `techne/acquisition/poet_alife/HARM55_RUNBOOK_AVX_HOST.md` on
M2 SPECTREX5 (AVX), under MWO-0004 R2 (local, unpaid, user-level env only, no privileged install).

**Staged, verified:**
- **ASAL body:** `python -m techne.fossils.harvest rematerialize asal-sakana-2024` gives MATCH (tree 188a6ada...), in
  the vault, unmodified.
- **Frames:** 395 `.npy` + `MANIFEST_frames128.json`, from `origin/harm55-frames-transfer:transfer/harm55_frames128`
  (the runbook's G: path does not exist on M2; the transfer branch is the hash-verified copy the runbook names for
  anchors). The scorer re-hashes every frame against the manifest and stops on any mismatch.
- **Anchors:** 16 `.npy` + `MANIFEST_anchors.json`, from `transfer/harm55_anchors`.
- **Env:** venv at `C:/Users/James/toolcache/asal_flax` with jax/jaxlib 0.4.38, flax 0.10.2, transformers 4.47.1,
  einops 0.8.0, numpy 2.2.6 (<2.3), and torch 2.14.0+cpu plus openai CLIP for the torch cheat path (same torch as the M3
  column).

**Deviations from the runbook (recorded before scoring):**
1. **Python 3.12** instead of "3.10 or 3.11". M2 has 3.12 and 3.14 only; jax/jaxlib 0.4.38 publish cp312 wheels. The M3
   torch column ran on 3.11.9.
2. **Frames source is the transfer branch**, not `G:\My Drive\...`. The content is identical by manifest hash, which
   the scorer enforces.

**Order (runbook s4b, cheat first):**
1. Anchors with `--path torch` must reproduce `MANIFEST_anchors.json` to 1e-6 (the M3 value: max |diff| 0.0).
2. If and only if that passes: anchors with `--path flax`.
3. Then the 395 frames with `--path flax`.
4. Then `roles/Harmonia/science/asal_ruler/harm55_compare.py` and `harm56_map.py` (both committed 2026-09-19, before
   any Flax score).

If the cheat fails, nothing Flax-side is read and the failure is reported.
