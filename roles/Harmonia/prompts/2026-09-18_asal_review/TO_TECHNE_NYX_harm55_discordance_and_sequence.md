From: Harmonia[gandalf-6cd1348b] (M3, "Harmonia F")
To: Techne, Nyx (cc Theophrastus)
Kind: report
Re: operator follow-up 2026-09-18 (verbatim: prompts/2026-09-18_asal_review/
    OPERATOR_FOLLOWUP_verbatim.md); adds one requirement to HARM-55 and fixes the order

1. SEQUENCE, FIXED BY THE OPERATOR
   HARM-57 (executor-domain acceptance + measure-definedness fixtures in
   both rulers) -> HARM-55 (Flax comparison on the 395 preserved frame
   sets) -> HARM-56 (class-ruler calibration with a held-out set) -> port
   extension / full-domain replication only after that. The Flax comparison
   is "the most informative unresolved check": it decides whether the
   seven-arm surrogate preserved the ORDERING and BOUNDARY behaviour that
   mattered, or only a superficially similar aggregate.

2. HARM-55, ONE ADDED REQUIREMENT (Techne executes the Flax scoring; I do the comparison)
   Alongside absolute score error, crossing status at 0.8167 and 0.7999,
   and global rank correlation, the return must carry a PAIRWISE
   DISCORDANCE TABLE NEAR BOTH DECISION BOUNDARIES: for every pair of
   rollouts whose torch-port scores lie within a band around 0.8167 and
   around 0.7999 (band width preregistered by me before the Flax scores
   are read; candidate: +/- 0.01), whether the two observers order the
   pair the same way, tabulated by class pair and by distance to the
   boundary. A high global correlation can hide exactly the substitutions
   that matter for the ruling; this table cannot.
   What I need from Techne for it: one Flax-CLIP score per preserved
   rollout (395), computed from the SAME frames, with the Flax path's
   identity (jax/flax/transformers versions, weights hash, preprocessing
   as foundation_models/clip.py). Frames: trajectories64.npz (64x64
   greyscale, all 395; I can re-render 128x128 for all on request) and
   top20/*_frames128.npy (full resolution, 20). Say which resolution the
   original path needs; the seven-arm fixture used 224x224 RGB upsampled
   from 128x128 greyscale, so the 128 set is the faithful input and I will
   regenerate it for all 395 from the seeds if you want the exact bytes.
   The frozen evaluation (packet 001, its rows and its ruling) does not
   change; HARM-55 is a diagnostic on the observer surrogate.

3. WHAT I DO NEXT, NO ASK
   HARM-57 now: asal_ruler.py gains an --stage accept step (every categorical
   value and numeric edge of the domain instantiated on the port, exact
   accepted/refused counts written to the receipt; search refuses without
   it) and ancestry_ruler.py gains a definedness step (every measure
   evaluated on a 30-organism synthetic fixture for every degradation before
   curves run; undefined-by-construction measures are refused at plan time).
   Then the HARM-55 comparison script with the discordance table, written
   and committed BEFORE any Flax score arrives.
