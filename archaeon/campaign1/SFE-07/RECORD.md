# SFE-07 -- CROSS-WORLD EXAPTATION (record; directive IV shape)

## A. STARTUP

- experiment ID: SFE-07
- question: do frozen artifacts that were failed or specialized in World
  A become useful on a PREDECLARED World B, beyond matched controls, by
  direct reuse or as evolutionary seeds? No retrospective selection.
- starting commit: 5e8871b26; harness sfe07.py.
- services: engine v2 -- (i) READ BACK the SFE-01 failure artifacts from
  their TERMINATED source world (an instrument question in itself:
  artifact_content on a terminated world); (ii) one World-B world with the
  predeclaration artifact published BEFORE any set is loaded or evaluated,
  the four frozen sets as artifacts, experiment + observation per set x
  seed.
- World B (predeclared): W3_K2 -- K=2, ask_mode one (late binding), 4-bit.
  No set was evolved on or evaluated against it before this experiment.
- frozen sets: failed_A = SFE-01's W1_d1 floor genotypes (the engine's
  cmp1.failures.v0 artifacts, seeds 1-3; manifests rebuilt from genomes
  with seeded campaign ranges because the artifacts carry genomes only --
  L-025); specialized_A = SFE-05 fixed/on elites (3; competent at Kd 4/8,
  lost Kd 0); best_A = SFE-05 adaptive/on elites (3); random = matched
  count to failed_A.
- exposure: direct reuse (best held-out competence of any member on 48 B
  episodes; family heldoutB) and evolution seeded from the set (padded
  with randoms to N=100; G=40; E=16; common RNG across sets) -> held-out
  competence on the same family. Seeds 1,2,3.
- controls: random (matched count); best_A (successful lineages: the
  comparison "unimpressive residue vs successful residue"); the
  predeclaration artifact's timestamp precedes every set artifact and
  every evaluation on the engine ledger.
- assay capability: W3_K2 was reached by naive search in 2/3 seeds at 8-bit
  N=200 G=100 (v01) with the 0.5 last-value plateau; at N=100 G=40 4-bit
  the random set may or may not reach it -- the random set IS the
  capability control; if random and every A set stay at the floor the
  outcome is INCONCLUSIVE.
- time: 12 runs x ~30 s on 12 procs; engine seconds.

## B. EXECUTION

- attempts: 1 (RECEIPT_attempt1.json; 9.3 s; failed_A EMPTY: the fetch of
  SFE-01's artifacts returned 403 SESSION_MISMATCH from the campaign
  session; three sets ran) and 2 (RECEIPT.json; 13.4 s; failed_A = 135
  genotypes fetched with a session-less reader, hash-verified 3/3 from the
  TERMINATED SFE-01 source world; four sets ran; 0 errors).
- engine: per attempt 1 session, 1 world, 1 predeclaration artifact
  (published FIRST), 1 hypothesis, 4 frozen-set artifacts, 12 experiments
  + 12 observations; teardown 0.2 s.
- design as planned (World B = W3_K2 4-bit; direct reuse on 48 held-out
  episodes; evolution N=100 G=40 E=16 seeded from each set, common RNG).
  failed_A manifests were REBUILT from genomes (the failure artifacts
  carry genomes only; persist/tape/regs/budget drawn from the campaign's
  gen-0 ranges, seeded) -- L-025.
- decisions: D-013 (session-less reader for cross-experiment reads).
  Failures: 403 SESSION_MISMATCH (L-026). Recovery: attempt 2 (world and
  records re-created: L-012 recurrence 2). Restart: n/a.

## C. SCIENCE

- primary outcomes on World B (held-out competence; direct = best member;
  evolved = elite after 40 generations seeded from the set):
    set            n    direct per seed        evolved per seed       footholds
    failed_A       135  0.125 0.104 0.104      0.042 0.583 0.562      2/3
    specialized_A  3    0.562 0.583 0.562      0.562 0.583 0.562      3/3
    best_A         3    0.521 0.521 0.542      0.521 0.583 0.646      3/3
    random         135  0.042 0.062 0.104      0.021 0.021 0.104      0/3
- controls: random (matched count 135, same gen-0 ranges as the rebuilt
  manifests); best_A (successful lineages); predeclaration artifact
  precedes every set artifact and every evaluation on the engine ledger
  (prospective by construction).
- assay capability: YES (random at the floor; three sets above it).
- evidence: EXAPTATION POSITIVE (weak-moderate, n=3): genotypes that
  FAILED World A (score 0 on W1_d1) seeded a World-B foothold in 2/3 seeds
  vs 0/3 random -- the residue is not a solver (direct 0.10-0.125, near
  the random set's 0.04-0.10) but it is better search material than
  random genomes at matched count. Specialized and successful World-A
  artifacts transfer by DIRECT reuse (0.52-0.58 = the last-value plateau
  on W3_K2): their register mechanism is world-general at that plateau.
- confounders: rebuilt manifests (only the genome is World-A residue);
  135 vs 3 members (the small sets' direct scores are single organisms);
  the plateau on B (0.5) is reachable by any last-value register, so
  "useful on B" means "carries a register" for the specialized/best sets;
  n=3.
- must NOT be claimed: that failed genotypes carry latent B-solutions
  (direct reuse says no); that exaptation exceeds the last-value plateau
  (nothing did, 0.646 max).

## D. TEARDOWN

- 1 world TERMINATED per attempt (0.19-0.20 s); no orphans; attempt-1
  world remains TERMINATED on the ledger (L-013 recurrence). Clean for
  SFE-08: yes.

## E. BENCH IMPROVEMENT

BUGS: L-026 (session affinity: a client's LATER session cannot read its
own EARLIER session's world with its key -- 403 SESSION_MISMATCH -- while
the same read with NO key succeeds under advisory enforcement; and the
client never persists session keys, so the earlier key was
unrecoverable). FRICTION: L-025 (failure artifacts carried genomes only;
cross-experiment reuse had to rebuild manifests). MISSING TELEMETRY:
none new. AUTOMATION: cross-experiment artifact reuse now works in 0.65 s
with the session-less reader. TO MACHINERY: persist session keys per
experiment in the campaign config; a documented "read an earlier world"
path. KEEP POLICY: World B choice, set definitions. MISSING FAILURE
STATE: none new. MISSING RECOVERY: L-012 recurrence 2. PORTABILITY:
none. OBSERVABILITY: L-013 recurrence 1.

## F. LANDSCAPE / GRADIENT NOTES

- failed_A's per-member direct scores (135 values, recorded as direct_mean
  0.04-0.06 with best 0.10-0.125) are a distribution, not a point: the
  right landscape is member score on A vs member score on B (a scatter
  over 135 genotypes) -- computable from the rows with one more
  evaluation pass; it would show whether "failed on A" is uniform or has
  a tail that carries B-relevant structure (e.g. IN/OUT-rich opcode runs,
  the same hypothesis as SFE-01's component effect).
- first_solved_gen for the evolved arms (recorded) is the speed landscape:
  failed_A seeds reached 0.5 within 40 generations in 2 seeds where random
  never did -- the generation index is the gradient the binary hides.

DISPOSITION: COMPLETE (attempt 2). Science: exaptation of failed residue
as search material WEAK-MODERATE POSITIVE (2/3 vs 0/3); direct reuse of
specialized artifacts POSITIVE at the plateau. Instrument: attempt 1 hit
L-026; attempt 2 clean.
