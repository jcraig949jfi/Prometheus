# Techne -- resume (the seat's entry file; base-role boot step 2)

Currency: 2026-09-30 (evening), instance gandalf-4c0c7e64 (M3/GANDALF). Replaces the 2026-09-25 text, which
is in git history (`git log -- roles/Techne/resume.md`).

## 1. Read in this order, nothing else first

  0. origin/main:ops/work_orders/CURRENT.md (MWO-0004 as of 09-30; verify the blob sha256 against
     ops/work_orders/PUBLICATIONS.md), then roles/Techne/WORK_STATE.json. Techne's section is in
     MWO-0001 s10 (NYX / TECHNE / THEOPHRASTUS / CRIUS: existing authorized work only). The
     2026-09-30 fleet activation order (ops/fleet/) does not list Techne.
  1. this file
  2. the newest roles/Techne/journal/<date>_<instance>.md (2026-09-30_gandalf-4c0c7e64.md)
  3. roles/Techne/BACKLOG_H0H5.md -- rows 122 (prior-art raid, with its 09-30 annotation), 123,
     128, 129 (rollout grade question), 131 (successor scorer), 65/100 (mirror destination) are
     the live ones
  4. roles/Techne/CHARTER.md, roles/base-role/RESPONSIBILITIES.md (section 2a is the work loop),
     roles/base-role/WORKING_CONTRACT.md
  5. the newest prompt to Techne under roles/*/prompts/ (as of 09-30 still roles/Atlas/prompts/
     2026-09-21_to_techne/TO_TECHNE.md, informational) and `git log --oneline -25 origin/main`

Boot mechanics: fetch-only in the canonical checkout; `git worktree add <worktrees>\techne-<task>
-b techne/<task> <origin/main sha>` (give it 15 minutes, never a short timeout); `python -m comms
boot Techne --model <id> --capabilities any` and `python -m comms sync Techne` with
EW_DB_HOST=192.168.1.202 (comms lives on M1 for every host). `comms inbox Techne --all` re-reads
messages a sync already marked seen. A woken seat with no task line runs the work loop; it does
not wait.

## 2. Work items, in the order I would start them (each with its proof and its blocker)

  0. REGIME since 2026-09-30 evening: CWO-2026-09-30C governs. A seat does NOT self-promote NEXT; when
     CURRENT finishes it writes receipts, pushes, heartbeats Aporia and goes READY (awaiting Aporia
     dispatch). Direct operator instructions outrank that and are executed. Heartbeat Aporia on
     adoption, launch, completion and every 90 min (format: CWO-C s14; example under
     roles/Techne/prompts/2026-09-30_heartbeats/). Nyx #1071 was answered by ruling #1188.
  A. TECHNE-122 section II report (auto-curricula: MCC, POET, ATEP, PLR, ACCEL, JaxUED, OMNI-EPIC)
     in DONOR.md format with primary sources and pins. The two bodies it needs most are here:
     dcd-facebookresearch-2022 (09-30) and poet-enhanced-2020 / poet-original-2019. Proof: the
     report, with organs named by file and function at the pins. Blocker: none (MWO-0004 R1 took
     the phased order as the default). Size L.
  B. TECHNE-122 section III (quality diversity: QDax, AURORA). After A. Size L.
  C. TECHNE-128: a committed list of the techne/tests files expected to run without the optional
     modules, and one command that runs exactly that list. Proof: the list + the command + a green
     run. Blocker: none. Size S.
  D. GEA-4 injection harness (Atlas 09-21 nomination). RESERVE, not started: it is a proposal from
     a parked seat, not an operator directive, and the harness contract (what is injected into
     what, who scores) would have to be agreed with Nyx first. One message, when A/B leave room.
  E. TECHNE-131: a dated successor to harm55_flax_score.py (LF output, self_check and
     static_control blocks on both paths) before the ASAL replication domain reuses the scorer.
     HARM-55 itself is CLOSED (Harmonia ran the Flax column on M2 on 09-30, A_OBSERVER_STABLE);
     the 39 capsules are filled and tranche 2 added no fossil. Open with Harmonia: whether to
     preserve the 7 rounding-noise D1 keys anyway (TECHNE-130).
  F. TECHNE-123 (measure open-oasis / MineWorld / Matrix-Game). BLOCKED on a GPU-class host.
  G. TECHNE-65/100 off-host mirror destination: the operator's one line (external side effect).

Done 2026-09-30: TECHNE-127 (dcd fossil), TECHNE-126 (recipe axis: NO_RECIPE), TECHNE-125
(host-neutral catalog snapshot with a staleness test), TECHNE-129 (nyx_handoff filled for 10
records; the 39 rollout records wait on a grade answer from Harmonia or Nyx), TECHNE-115
(native Flax column consumed: 39 capsules filled), TECHNE-130 (tranche 2: no new fossil).
Evening 2026-09-30: ruling #1071 (TECHNE-134); batch 17 -- 20 donors for Nyx (TECHNE-132; deferred
list in the batch docstring); TECHNE-133 filed (bytecode written into a body by a consumer import).

## 3. Standing facts a new instance would otherwise re-derive

  - Techne owns NO monitor row (base-role step 8: nothing to feed; say so in the journal).
  - Whole `techne/tests` on M2/M3 has 17 collection errors from absent modules (hypothesis,
    chipfiring, python-sat, ...; 954 collected, re-measured 09-30). Run by name:
    techne/tests/test_fossil*.py test_lenia_port_extension.py test_world_manifest.py
    test_preservation.py test_instrument_hygiene.py -- 761 passed / 13 skipped on 09-30.
    A file outside that list went red for 14 days unseen (TECHNE-128).
  - A NEW FOSSIL RECORD NOW REQUIRES A CATALOG REGEN, or test_fossil_catalog_snapshot.py is red:
    `python -m techne.fossils.catalog --no-body-check --out techne/fossils/CATALOG.json`.
  - New batch recipe (batch 17): reader agents draft facts from clones at the pin into a committed
    READER_DRAFTS dir; the batch script builds records from drafts + overrides; then acquire, verify
    --all, Defender scan, `finalize_handoff --all-empty --write`, catalog regen, fossil test set.
  - A NEW FOSSIL RECORD ALSO NEEDS ITS nyx_handoff FILLED (or a CAPSULE.json), or
    test_fossil_handoff.py is red: record.skeleton writes it empty; see
    techne/fossils/batches/finalize_handoff_20260930.py handoff_of().
  - record.preservation.recipe_status is a closed set (harvest.RECIPE_STATES); NO_RECIPE means no
    recipe.json exists, not that the body is self-sufficient to run.
  - archaeon/tests/test_base_role.py is the fleet self-test; 14 passed, 1 skipped on 09-30.
  - Heredocs containing an apostrophe are rejected by this shell even with a quoted delimiter;
    write prose files with the file tool and keep inline scripts apostrophe-free.
  - Host-local and gitignored on M3: the fossil vault under the canonical checkout (49 of 169
    specimens have bodies here, 217 MB), vault\techne_tools\asal107 (torch CPU env), the operator's
    Drive folder Prometheus\harm55 (395 frames). Re-fetch path for bodies: `harvest rematerialize`.
  - To add the native column to EXISTING capsules use `capsule fill-native`, never `capsule build
    --flax` (a rebuild without --internals drops the captured observer internals).
  - Hash the BLOB, not the checkout: working copies here are CRLF, so `sha256sum <file>` is not
    the committed hash. Use `git show <ref>:<path> | sha256sum` or capsule.lf_sha256.
  - Two "HARM-55" ids exist (Harmonia Q6). Mine refers to gandalf-6cd1348b's ASAL row at 2ead5e011.
  - The M0.5 promotion-replay audit (2026-06-23) and the cartography campaign (2026-09-01) are
    closed arcs; their docs stand: roles/Techne/M05_PROMOTION_REPLAY_FINDINGS_2026-06-23.md,
    roles/Techne/CARTOGRAPHY_FROZEN_TESTS_2026-09-01.md.

*-- Techne, gandalf-4c0c7e64, 2026-09-30.*
