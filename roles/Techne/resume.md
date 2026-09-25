# Techne -- resume (the seat's entry file; base-role boot step 2)

Currency: 2026-09-25, instance gandalf-5983e3f7 (M3/GANDALF). Replaces the 2026-09-01 cartography
anchor, which is in git history (`git log -- roles/Techne/resume.md`) and is not live work.

## 1. Read in this order, nothing else first

  1. this file
  2. the newest roles/Techne/journal/<date>_<instance>.md (today: 2026-09-25_gandalf-5983e3f7.md),
     then 2026-09-25_gandalf-a04f7c25_RESET.md (the reset log: what 09-17..09-21 built, what a
     reset destroys on this host, what is NOT done)
  3. roles/Techne/BACKLOG_H0H5.md -- rows 113/115 (HARM-55 Flax column), 122/123 (prior-art raid),
     124/125 (lineage key, catalog snapshot), 65/100 (mirror destination) are the live ones
  4. roles/Techne/CHARTER.md, roles/base-role/RESPONSIBILITIES.md, roles/base-role/WORKING_CONTRACT.md
  5. the newest prompt to Techne under roles/*/prompts/ (as of 09-25: roles/Atlas/prompts/
     2026-09-21_to_techne/TO_TECHNE.md, informational) and `git log --oneline -25 origin/main`

Boot mechanics: fetch-only in C:\Prometheus; `git worktree add C:\prometheus-worktrees\techne-<task>
-b techne/<task> <origin/main sha>`; `python -m comms boot Techne --model <id> --capabilities any`
and `python -m comms sync Techne` with EW_DB_HOST=192.168.1.202 (comms lives on M1 for every host).

## 2. Work items, in the order I would start them (each with its proof and its blocker)

  A. TECHNE-124 lineage key -- DONE 2026-09-25 (see journal). Nothing left but Nyx dropping the
     read-side fallback if they choose.
  B. Fossilize facebookresearch/dcd at a pin (Atlas #526 priority 2; UED-2/UED-4 need it; POET is
     already here as poet-original-2019 / poet-enhanced-2020). Proof: specimen record + vault body
     `harvest verify` clean + licence read. Blocker: none but network. Size S.
  C. GEA-4 injection harness over techne/fossils CATALOG + Nyx organs with an irrelevant-fossil
     control set of matched size (Atlas #526 priority 1). Proof: harness + a null run that shows
     the control set is indistinguishable in shape. Blocker: the harness CONTRACT (what is injected
     into what, and who scores) must be agreed with Atlas and Nyx first -- one message each. Size M.
  D. TECHNE-122 prior-art raid sections II/III (auto-curricula, QD). Proof: one DONOR.md-format
     report per section with primary sources and a fossil where licensed. Blocker: operator
     confirms the phased order or redirects. Size XL, 6-10 passes.
  E. HARM-55 (ASAL Flax column, gandalf-6cd1348b) -- TECHNE-115. Everything on the Techne side is
     built and frozen (harm55_flax_score.py, runbook, tranche-2 selector, closure tool, 39 capsules
     with native fields PENDING). Blocker: an AVX host with jax/flax; Harmonia's M2 delegation had
     not run when both seats parked (question posted 09-25). Not actionable from M3.
  F. TECHNE-125 catalog snapshot policy (S; decision, then one command).

## 3. Standing facts a new instance would otherwise re-derive

  - Techne owns NO monitor row (base-role step 8: nothing to feed; say so in the journal).
  - Whole `techne/tests` on M2/M3 has 17 collection errors from absent modules (hypothesis,
    chipfiring, python-sat, ...). Run the fossil files by name; 641 passed / 7 skipped on 09-25.
  - archaeon/tests/test_base_role.py is the fleet self-test; green on dd42d1adb (10 passed, 1 skipped).
  - Host-local and gitignored on M3: C:\Prometheus\vault\fossils (208 MB, 48 of 168 specimens have
    bodies here), vault\techne_tools\asal107 (torch CPU env), G:\My Drive\Prometheus\harm55 (395
    frames, the operator's Drive). Re-fetch path for bodies: `harvest rematerialize`.
  - Two "HARM-55" ids exist (Harmonia Q6). Mine refers to gandalf-6cd1348b's ASAL row at 2ead5e011.
  - The M0.5 promotion-replay audit (2026-06-23) and the cartography campaign (2026-09-01) are
    closed arcs; their docs stand: roles/Techne/M05_PROMOTION_REPLAY_FINDINGS_2026-06-23.md,
    roles/Techne/CARTOGRAPHY_FROZEN_TESTS_2026-09-01.md.

*-- Techne, gandalf-5983e3f7, 2026-09-25.*
