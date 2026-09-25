# Techne journal -- 2026-09-25 -- RESET LOG (instance gandalf-a04f7c25, host GANDALF/M3)

Operator, chat: "we're going to reset. Log anything you have for a reset. Commit, push, merge any
branches you have to main." This is that log. Continues roles/Techne/journal/2026-09-17.md and
roles/Techne/journal/2026-09-17_gandalf-a04f7c25.md (this instance's day-file, split per D-24
amendment 3 on 2026-09-17). Anchor for whoever resumes: read this file first, then the two above
in date order, then roles/Techne/BACKLOG_H0H5.md.

## 1. Git state -- VERIFIED, nothing of mine unmerged

  worktree      C:\prometheus-worktrees\techne-m3-boot-2026-09-17
  branch        techne/m3-boot-2026-09-17
  HEAD          1182e5328d369718e666d792f82b3b4689bc20d3
  origin/main   4aa6abbbcab64ebcf8ef5ec29518d7a8a49b4bed (fetched 2026-09-25 11:30Z)
  status        `git status --short` empty (clean); every push this session was branch:main
                fast-forward (WORKING_CONTRACT s2/s5), never a pushed task branch -- confirmed
                today: `git ls-remote --heads origin | grep -i techne` returns NOTHING, so there
                is no stray techne/* branch on origin to merge or delete
  ancestor      `git merge-base --is-ancestor HEAD origin/main` -> TRUE. Main has moved 2,877
                commits past my HEAD in the 4 days since my last push (fleet-wide activity,
                confirmed by Ensorain's E0-WTP-03 closures and Atlas's own pre-reboot save
                landing on main in that window); none of it is mine to merge, none of mine is
                stranded. "Commit, push, merge any branches to main" is therefore ALREADY TRUE
                for this seat as of this log; no git action remains except the worktree/branch
                cleanup in section 6.
  canonical     C:\Prometheus, main worktree, untouched all session (guard: git-dir ==
                git-common-dir there; never worked in it, per WORKING_CONTRACT s1)
  siblings      two other worktrees exist under C:\prometheus-worktrees on this host --
                harmonia-gandalf-6cd1348b-boot (Harmonia's) and nyx-boot-2026-09-17 (Nyx's).
                NOT touched (lane discipline); their reset is their own seat's business.

## 2. What this instance did, 2026-09-17 through 2026-09-21 (full detail in the two prior
   journal files; this is the index, not a repeat)

  2026-09-17  M3 first boot; host census; TECHNE-101 (native-shell capability-probe fix,
              7 controls); POET+ALife literature gather (TECHNE-103); autopsy of POET/ASAL/
              Avida/Tierra/TerraLingua source code with a discard ledger (cost-classed);
              TECHNE-107 ASAL open-endedness-score experiment on M3 (torch CLIP; preregistered
              then run; CLIP regularises pixel noise but scene/colour garbage still beats
              living Lenia); operator "refinery" directive -- 6 ALife bodies landed as records
              + vault bodies (poet-enhanced-2020, poet-original-2019, asal-sakana-2024,
              tierra-6.02-ray-1998, terralingua-2026 + its data slice, lenia-chan-2019); R36
              canonical world-manifest tool + world m3-native-python registered; FIRST
              EXECUTABLE FOSSIL PACKET (asal-sakana-2024, HANDOFF schema, PRESERVATION_GATE_OPEN
              per R38); Lenia port extended (kn 1-4, gn 1-3, fractional rings; 537/548 catalogue
              acceptance); HARM-55 instrument (harm55_flax_score.py: torch self-check
              bit-identical to Harmonia's manifest, --rgb224-dir anchor mode for the 16 control
              anchors, torch cheat 16/16 max diff 0.0).
  2026-09-18  directive 6 ("capsules, not a pile"): portable specimen CAPSULE schema
              (techne/fossils/capsule.py, 6 controls) written for 39 rollout fossils with
              ORIGINAL-observer per-frame internals; PORT CLOSURE tool
              (lenia_domain_closure.py: closed exclusion vocabulary, UNACCOUNTED fails the
              census; original 1,045-domain = 1,035 executable / 10 excluded / 0 unaccounted,
              closure TRUE); tranche-2 selector FROZEN before any native score
              (harm55_tranche2_select.py, D1-D8 + P1/P2 pair rules; dry-run control: 0 flips
              against itself); tranche 1b (18 pair-type rollouts, observer-independent)
              preserved now.
  2026-09-21  directive 7 (prior-art raid). Delivered the First Return (section XV only, by
              explicit scope call recorded in the report itself): Voyager fossilized
              (MineDojo/Voyager@55e45a88, MIT, 457 files, hash-verified) with a full
              source-level autopsy of SkillManager / CurriculumAgent / CriticAgent /
              ActionAgent; SIMA 2 and Genie 3 confirmed NO_PUBLIC_SOURCE by direct quote from
              DeepMind's own blog (research preview only, no code/weights, fetched and quoted,
              not inferred); kyegomez/SIMA graded TOY_CLONE; open Genie substitutes ranked
              (open-oasis > MineWorld > Matrix-Game, none measured); fifth-engine legs assessed
              without naming an engine. TECHNE-121 (done) / 122 (remaining 8 sections, staged,
              XL) / 123 (measure the open substitutes) filed. Report posted to Harmonia, Nyx,
              Theophrastus, Archaeon (comms #525) and re-verified intact on 2026-09-21 when the
              operator asked for confirmation.

## 3. STANDING BLOCKER, unchanged across the 4-day gap -- verified today

HARM-55's native (Flax/JAX) observer column has NOT landed on main
(`techne/acquisition/poet_alife/HARM55_FLAX_NATIVE_*.json` does not exist on origin/main as of
this fetch; every rollout capsule's `native_observer.status` is still `"PENDING"`, checked
directly on asal-rollout-S2_135's CAPSULE.json on origin/main). Last known state (2026-09-19):
Harmonia delegated the AVX run to its own M2 instance (m2-ca1148a0) with my harm55_flax_score.py
script and the runbook (techne/acquisition/poet_alife/HARM55_RUNBOOK_AVX_HOST.md); whether that
delegation completed, stalled, or was superseded by the fleet-wide reset is UNKNOWN to this
instance -- not chased further today because a reset was called before I could. The frozen
tranche-2 selector, the domain-closure tool, and 39 capsules are ready to consume the Flax file
the moment it exists; nothing needs to be rebuilt.

## 4. Open thread, informational only, not actioned

Atlas (comms #526, body at roles/Atlas/prompts/2026-09-21_to_techne/TO_TECHNE.md, on main) built
a 34-record experiment queue directly off the First Return (roles/Atlas/proposals/
2026-09-21_prior_art_raid/) and named five unblocking priorities, highest first: (1) GEA-4 needs
only an injection harness over techne/fossils CATALOG + Nyx organs, no new donor; (2) UED-4/UED-2
need facebookresearch/dcd and uber-research/poet fossilized at a pin (poet-enhanced-2020 /
poet-original-2019 ALREADY fossilized here, 2026-09-17 -- dcd is not); (3) RA-1/RA-3 need nothing
from Techne; Voyager organ 1 (the SkillManager schema, already autopsied and fossilized) gates
five further records (F5-0/F5-1/F5-4/MEM-1/EV-10). Nothing here was a request to build; it is
demand-visibility for whoever picks up TECHNE-122. Not actioned in this pass -- a reset was
called, and this log's job is to make the demand visible, not to start new work against it.

## 5. Host-local material on M3 (GANDALF) -- what a reset affects

  category                      persists a repo/session reset?      notes
  -------------------------------------------------------------------------------------------
  git-tracked records/receipts  YES (on origin/main)                 everything in section 2
  fossil BODIES (vault)         NO -- host-local, gitignored         C:\Prometheus\vault\fossils
                                                                     (208 MB, 48 specimen dirs, measured 2026-09-25)
                                                                     re-fetchable by
                                                                     `harvest rematerialize`
                                                                     from the pins on main for
                                                                     every specimen except the
                                                                     rollout fossils (kind
                                                                     "file": their SOURCE is
                                                                     Harmonia's own M3 delivery
                                                                     at C:\Prometheus-vault\
                                                                     harmonia\
                                                                     asal_001_frames128, also
                                                                     host-local -- if BOTH are
                                                                     lost the 39 rollout bodies
                                                                     have no re-fetch path
                                                                     except Harmonia's
                                                                     regen_frames128.py against
                                                                     the frozen seeds, which is
                                                                     deterministic and
                                                                     control-proven (C-TOP20,
                                                                     C-TRAJ64) but not yet
                                                                     re-run from scratch
  Google Drive mirror           YES -- not host-local                G:\My Drive\Prometheus\
                                                                     harm55\ (395 frames +
                                                                     manifest, verified
                                                                     395/395 on 2026-09-17) is
                                                                     the operator's own Drive,
                                                                     survives independent of
                                                                     this machine or session
  isolated tool env asal107     NO -- host-local                     C:\Prometheus\vault\
                                                                     techne_tools\asal107
                                                                     (torch 2.14 CPU + openai
                                                                     `clip`); rebuildable from
                                                                     the pinned versions in
                                                                     journal 2026-09-17 unit 4
                                                                     (system-site venv, pip
                                                                     install torch==2.14.0+cpu
                                                                     transformers==4.44.2 etc.)
  scratchpad ($TEMP/harm55/*)   NO, and NOT AUTHORITATIVE ANYWAY      working copies of files
                                                                     that are also committed
                                                                     (rows.jsonl, thresholds,
                                                                     manifest); nothing here was
                                                                     ever the source of truth

## 6. Cleanup performed as part of this reset

Per WORKING_CONTRACT s5 ("once merged, remove the worktree and delete the branch, locally and
`git push origin --delete` remotely, once `git branch -r --merged origin/main` lists it"): my
branch was never pushed as a remote branch (section 1), so there is no remote branch to delete.
The local worktree and branch are left in place through this log's commit (removing them now
would delete the very file being written); removal is the correct action for whoever next runs
`git worktree list` and finds techne/m3-boot-2026-09-17 fully merged -- `git worktree remove
C:\prometheus-worktrees\techne-m3-boot-2026-09-17 && git branch -d techne/m3-boot-2026-09-17`
from the canonical checkout, verified first with `git branch -r --merged origin/main` (n/a,
local-only) or simply `git merge-base --is-ancestor <branch> origin/main` as done in section 1.

## 7. Fast orientation on resume

Read in order: this file -> roles/Techne/journal/2026-09-17_gandalf-a04f7c25.md ->
roles/Techne/journal/2026-09-17.md (shared day-file with the M1 instance's 2026-09-17 hygiene
pass) -> roles/Techne/BACKLOG_H0H5.md (TECHNE-99 through 123; 113/115/122/123 are the open rows
that matter most). Entry points still valid: `python -m comms boot Techne --model <id>` with
EW_DB_HOST=192.168.1.202 (comms lives on M1 for every machine, per the 2026-09-17 wake-directive
update); `python -m techne.fossils.harvest verify --all` to re-check every pinned body once the
vault is repopulated; `python techne/scripts/lenia_domain_closure.py` and
`techne/scripts/harm55_tranche2_select.py` are ready the moment a Flax file exists.

## 8. What is NOT done (stated once, plainly)

TECHNE-122 (prior-art raid sections II-IX, 6-10 further passes) has not been started beyond the
scope note in FIRST_RETURN_2026-09-21.md. TECHNE-123 (measure the open Genie substitutes) has not
been started. HARM-55's native column has not landed (section 3). Atlas's five priorities
(section 4) have not been actioned. None of this was abandoned mid-step; each stopped at a clean
boundary with its own committed artifact, which is why this reset needed a log rather than a
rescue.

*-- Techne, instance gandalf-a04f7c25, M3/GANDALF, 2026-09-25, session end (operator reset).*
