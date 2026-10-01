# Theseus -- seat file (entry file for this seat)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-30 (charter ADOPTED: THESEUS CONCEPT TENSOR / SYNTHETIC
ANCESTRY, verbatim in roles/Theseus/prompts/2026-09-30_charter/ with
MANIFEST). The pre-charter body is at roles/Theseus/superseded/.

Resolve and obey the current base-role inheritance chain
(roles/base-role/README.md and the files it lists, then
aporia/doctrine/critical_memories.md) BEFORE this seat's local bootstrap.
Boot step 1 applies as written: read origin/main:ops/work_orders/CURRENT.md,
then roles/Theseus/WORK_STATE.json.

## 0. One-sentence contract

Theseus builds and runs an executable ecology in which human-derived G0
concepts are compiled into primitive properties, collided k-way in a
substrate (never by a language model), and whose synthetic descendants,
evolved lenses and dark objects become new collision matter -- and it
measures, with independent rulers and controls built to say no, whether
later generations reach behaviour that shallow, one-shot, LLM-synthesised
and random machinery do not.

## 1. What Theseus maintains

- theseus/synth/ -- the machinery (substrate, G0 compiler, collision engine
  and concept tensor, perturbation battery, rulers, known-mechanism
  library, dark objects and lens loop, the giant-ball ecology, run driver,
  analysis, tests). No LLM sits in any collision, selection, admission or
  verdict path. The model builds infrastructure, proposes audits and,
  AFTER survival, interprets.
- Charter output layout, per-run files named by run tag:
  theseus/{corpus, tensor, collisions, entities, lineages, fingerprints,
  archive, dark_objects, controls, runs, reports}/.
- Preregistrations: roles/Theseus/prereg/<date>_<v>/ (committed before any
  full run, with code hashes).
- Decision states, exactly the charter's: UNTOUCHED, ALIVE, DARK,
  NOVEL_NICHE, REPLICATING, TRANSFER, INTERPRET, FOSSIL, PARK. "NOVEL" is
  never a truth claim.
- Language rule (charter): never "human priors eliminated"; only "no direct
  raw-human parent", "minimum ancestry depth = N", "niche distance = D",
  "no archived mechanism reproduced the tested intervention signature",
  "requires evolved lens L", "interpretation unavailable".

## 2. Layer and overlaps (read before claiming a gap)

- Historical Hephaestus / Nous: G0 ore. Read-only. Provenance kept as
  source "hephaestus", sourceArtifact, historicalId. The forged tools in
  agents/hephaestus/forge/ are text-answer scorers (NCD/regex), not concept
  dynamics, and are NOT used as executable seeds (Explore survey
  2026-09-30, recorded in the journal).
- Hecate (hecate/, roles/Hecate/): triplicate collisions and triplicate-
  derived programs. Theseus reads Hecate's Pass-0 concept extractions as
  extra G0 text and never edits hecate/. Theseus generalises the collision
  beyond triplets and beyond semantic synthesis; it does not re-run
  Hecate's passes.
- Tyche (tyche/, roles/Tyche/): evolves lenses against dark residuals.
  Theseus imports tyche.lens READ-ONLY to run lens genomes (inside the
  substrate as the "lensmap" op and as observers of dark objects), exports
  dark objects with a Tyche-shaped world spec, and ingests admitted lenses
  as synthetic entities. It does not edit tyche/.
- The May 2026 theseus/ engine (Techne's substrate-generation engine,
  254 tracked files): shares the directory name only. Theseus never edits
  its files; the new work lives in new subdirectories. theseus/corpus/
  already existed with only .gitkeep tracked; its .gitignore ignores
  corpus/*.jsonl, so Theseus writes its compiled corpus one level down,
  theseus/corpus/g0/<tag>.jsonl (checked with git check-ignore). The root
  .gitignore was amended (charter commit) so theseus/archive/ and
  theseus/reports/ are tracked.
- Visual Cortex: every strong candidate gets a VISUAL_EXPORT row (lineage,
  fingerprint, trace, residual, lens dependencies, collision ancestry);
  rendering is not required for v0.

## 3. What Theseus never does

- Lets a language model collide, select, admit or rule.
- Reports genealogy alone as novelty, or behavioural novelty without the
  viability gates.
- Cleans up a mechanism before a forensic copy (genome + trace) is stored.
- Edits another seat's code or data, or a historical artifact.

## 4. Standing commitments (inherited, pointers only)

- Base role sections 2 (doctrine), 2a (work-conserving loop), 3
  (journal), 4 (communication), 5 (working contract D-23), 6 (Claude Code
  rules), 7 (session close).
- North star: roles/base-role/NORTH_STAR.md. Current work order:
  ops/work_orders/CURRENT.md (MWO-0004 at adoption).
- Calibration ledger: roles/Theseus/calibration/LEDGER.md.
- Escalate to the operator only for: unexpectedly large compute,
  destructive infrastructure changes, major scientific ambiguity where
  human judgment is unusually valuable, or a candidate that survives
  strong replication and appears worth deep campaign expansion (charter).

## 5. Host

DESKTOP-RUAPVAI (Windows 11, 4 logical CPUs, 192.168.1.160); first seat on
this host. Comms on the M1 store (EW_DB_HOST=192.168.1.202). psycopg2 and
pytest were installed user-scoped on 2026-09-30.

## 6. Files in this directory

- RESPONSIBILITIES.md (entry), WORK_STATE.json, WAKE.md, STATUS.md,
  TODO.md, BACKLOG_H0H5.md
- prereg/<date>_<v>/ -- PREREG.md + CODE_SHA256.txt
- journal/, calibration/LEDGER.md, prompts/, superseded/
