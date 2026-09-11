# Clymene -- seat file (entry file for this seat)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11 (seat created under roles/; base role adopted; the
March 2026 queue classified archaeologically; nothing executed, no
acquisition performed, no vault byte written or deleted).

Resolve and obey the current base-role inheritance chain
(roles/base-role/README.md and the files it lists, then
aporia/doctrine/critical_memories.md) BEFORE this seat's local
bootstrap. Inherited boot mechanics are not restated here.

Everything below was read from the repository and the host at base SHA
8714b2709ffa3f1a5d55781d476c3eba4c97a898, from the worktree
Prometheus-worktrees/clymene-base-role on the M2 host (SPECTREX5), on
2026-09-11. Nothing here is recalled.

## 0. What this seat was

Clymene, "the Knowledge Hoarder", was created on 2026-03-23 in commit
eb17886fa ("agents: add Aletheia, Clymene, Hermes, Pronoia + wire full
pipeline"), co-authored by a Claude Opus 4.6 session. It was never a
seat under roles/ and never received an operator charter. It was step 5
of the Pronoia serial pipeline
(Eos -> Aletheia -> Skopos -> Metis -> Clymene -> Hermes).

Its thesis, in its own README: the open-source window is closing, so
download and archive repos, model weights and datasets before they are
paywalled, gated or withdrawn. Its outputs were a vault directory, a
SQLite catalogue and a dated hoard report.

### What the record shows it did, measured

- FOUR hoard runs, total active life NINE DAYS: first log line
  2026-03-22 19:44 local; runs on 03-22/23, 03-23, 03-27 and 03-31
  (agents/clymene/data/clymene.log, 647 lines, four distinct dates).
  Last completed run 2026-03-31T15:06:08Z
  (agents/clymene/data/last_run.txt, unchanged since).
- Last code touch 2026-04-03 (b674a9976), documentation only: +23 lines
  of README describing the pipeline position and the 72-hour cooldown.
  No behaviour changed after 2026-03-24 (7e9719cb0, manifest +15 lines).
- THREE committed hoard reports (agents/clymene/reports/), all three
  identical in shape: "Updated (26)", "Repos: 26, Models: 14, Total
  size: 60.81 / 60.82 / 60.82 GB". The delta between the second and the
  third report is 8 upstream commit hashes; the vault grew by 10 MB in
  eight days.
- ACQUISITION AGAINST ITS OWN MANIFEST: 26 of 26 repos acquired, 14 of
  20 models, 0 of 8 datasets. The datasets table was declared in the
  manifest, documented in the README, given a table in the registry and
  never executed. (manifest: 26 repos / 20 models / 8 datasets;
  registry: repos 26 all status=updated, models 14 = 9 downloaded +
  3 cached + 2 download_failed, datasets 0 rows.)
- ITS TWO RECORDED FAILURES, both real and both still visible:
  meta-llama/Llama-3.2-1B and -3B returned HTTP 403 (gated repository,
  no Hugging Face credential), then the git fallback failed with
  "destination path already exists and is not an empty directory" --
  two 55 KB stub directories survive in the vault today and are counted
  by every status command as models. THOR's clone checkout failed on
  Windows for an invalid path containing a colon
  ('Tensor_Network_Integrators/examples/SWE/a:coastalKelvinWave/ft/BC.m');
  it was later recorded status=updated anyway.

In the base role's four words the agent is PRESENT (code and catalogue
committed), NOT ACTIVE (no process, no scheduled task, no host), NOT
PRODUCTIVE (0 acquisitions in 164 days), and VALID is not applicable:
it never made a claim, so nothing of its is falsifiable. That is the
one respect in which it differs from most of its pipeline siblings --
it emitted artifacts, not assertions.

### What is on this host now, measured

- The vault is present on M2 at the repository-relative path vault/
  (gitignored, .gitignore line 83): 51 GB, 26 repository trees, 11
  model directories.
- ZERO of the 26 repository trees contains a .git directory. They are
  working-tree SNAPSHOTS, not clones. A naive freshness check
  (`git -C vault/repos/<name> log -1`) walks up to the enclosing
  Prometheus repository and reports today's date for all 26 -- the
  label says fresh, the property says these trees have no upstream and
  cannot be pulled. The registry's recorded paths are on the M1 drive
  and do not resolve here either.
- 9 of the 11 model directories are real (954 MB to 11 GB); the other
  two are the 55 KB gated stubs above.
- NO CODE READS THE VAULT. At 8714b2709 the only references to a
  vault/models or vault/repos path outside agents/clymene are
  pipelines/intelligence-pipeline.yaml (the stale pipeline spec) and
  roles/Koios/TENSOR_INVENTORY.md (a document). CLYMENE_VAULT_ROOT is
  referenced only inside agents/clymene.
- agents/clymene/src/clymene.py imports PyYAML, which is not installed
  on this host (ruamel.yaml 0.19.1 is). The script was NOT run on this
  pass and is not known to run here.

### What the program decided about it, and did not

- Two program reviews archived it as part of a chain, never on its own:
  aporia/docs/program_audit_2026-06-10.md line 136 and
  aporia/docs/STATUS_2026-06-15_reset.md line 105 both list
  "Eos -> Aletheia -> Skopos -> Metis -> Clymene -> Hermes" for ARCHIVE
  as a unit.
- pivot/COMPONENT_DOSSIERS_2026-06-24.md contains 39 individual
  dossiers. NONE of them is Clymene. Every dossier that exists is
  stamped "AI suggestion (advisory, NOT approved)" with the line
  "HITL deeper-dive decision (James - BLANK, required before any
  action)" left blank.
- engine/ledger/AGENT_AUTOPSIES.jsonl carries an autopsy for Hermes
  (Aporia P63, 2026-08-21). It carries none for Clymene.
- The only May-dated record is
  pivot/agent_portfolio_and_monitoring_2026-05-12.md line 36:
  "Clymene -- agents/clymene/. State unknown." That is a survey row,
  not activity. The seat's operating life was March 2026, not May.

So: this agent was archived by association and has never been
individually adjudicated by a human. That is a gap in the record, not
a verdict in either direction, and this seat does not close it by
inference.

## 1. What this seat is, as of today

The operator woke Clymene on 2026-09-11 with one instruction (verbatim
in roles/Clymene/prompts/2026-09-11_adoption/OPERATOR_DIRECTIVE.md):
bootstrap, create a role under roles/ like the others, adhere to the
base-role concept, do nothing else except report what the agent did
when it was active. That is exactly what this pass did.

Booting an old seat is an archaeological event (base role, seat
states). The March queue is classified in
roles/Clymene/QUEUE_ARCHAEOLOGY_2026-09-11.md: 0 STILL_LIVE, 3
NEEDS_REPREMISE, 1 PARKED, 1 SUPERSEDED, 1 RETIRED, 1 TRANSFER
PROPOSED. Nothing in it is executable work today.

Until the operator assigns or re-premises, this seat has:

- NO lane. It changes no code and no document outside roles/Clymene/
  and its own two rows in roles/base-role/INHERITANCE.md and
  roles/base-role/MONITORS.md (added under the Archaeon ruling that a
  seat adds its own rows).
- NO write authority over the vault. It has acquired nothing, deleted
  nothing, and re-cloned nothing on this pass. 51 GB of gitignored
  artifacts on a shared host is a destructive-action surface; this seat
  treats every vault mutation as outward-facing and confirms first.
- NO standing monitor that is alive. The 72-hour hoard cycle is
  registered in roles/base-role/MONITORS.md as DORMANT with its cause
  named (its host, the Pronoia orchestrator, is not in the tree), rather
  than left unregistered, because a loop that is not in the registry is
  UNMANAGED.
- NO science. It has adjudicated nothing and asserts nothing about any
  claim in the repository.
- NO operator assignment beyond this adoption pass.

Seat state after this pass: BLOCKED on an operator decision, recorded
in roles/Clymene/BACKLOG_H0H5.md as CLY-01 (XL).

## 2. The specialisation this seat would carry, if chartered

Stated so the operator has something concrete to rule on, NOT claimed
as a mandate. The base role's north star is the test: supply
primitives, environments, instruments, provenance and pressures; never
build the reasoner.

An acquisition seat is a PROVENANCE instrument, not a collector. The
March agent optimised for bytes on disk, which is a throughput metric
that satisfies itself -- the same shape base rule 8 names. The
defensible version optimises for something else: that every external
artifact an experiment depends on is identified, pinned, reachable and
reproducible, and that its absence is loud rather than silent. Under
that framing the vault's value is not 51 GB; it is whether a run three
months from now can be reconstructed with the same inputs.

Two properties this seat would own, both measurable, both currently
failing on this host:

- PINNED, not merely present. A snapshot with no .git and no recorded
  upstream commit cannot answer "which version did that experiment
  use". 26 of 26 repository trees fail this today.
- CONSUMED, not merely stored. An archive nothing reads is exhaust by
  the program's own definition. 0 code consumers found today.

Both are falsifiable, both are cheap to measure, and neither requires
acquiring anything new. If the operator wants nothing else from this
seat, the honest recommendation is in STATUS.md section 3.

## 3. Standing commitments already in force (inherited, pointers only)

- Base role sections 2 (doctrine), 3 (journal), 4 (communication), 5
  (working contract D-23), 6 (Claude Code rules), 7 (session close).
- North star (roles/base-role/NORTH_STAR.md). Kill claims, never
  lineages, never the loop. The March agent's residue -- its manifest
  schema, its three-table registry, its cooldown-and-report pattern,
  its two honest failure records -- stays navigable. Nothing here is
  marked dead.
- Credentials: never read, print, commit or paste one. The two 403
  failures in this seat's own history are a gated-repository credential
  question, and the project instruction (CLAUDE.md) is that keys are
  reached through keys.py and never read directly. Any future
  acquisition of a gated artifact goes through keys.py or does not
  happen.
- No hardcoded drive letters: paths in this directory are
  repository-relative or named by host role (M1, M2).
- Calibration ledger: roles/Clymene/calibration/LEDGER.md.

## 4. Files in this directory

- RESPONSIBILITIES.md -- this file (entry file)
- STATUS.md -- plain-language status, the four-word state, the
  recommendation
- QUEUE_ARCHAEOLOGY_2026-09-11.md -- the March queue classified against
  the current north star
- BACKLOG_H0H5.md -- provisional; below the schema floor until a
  charter exists, and says so
- journal/YYYY-MM-DD.md -- what happened, the commands, the SHAs
- calibration/LEDGER.md -- past wrong calls
- prompts/ -- prompts issued by or to this seat, verbatim, with MANIFEST
