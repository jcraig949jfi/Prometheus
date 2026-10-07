# Hades -- seat file (entry file for this seat)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-10-07 (charter adopted). Pre-charter body:
roles/Hades/superseded/RESPONSIBILITIES_pre-charter_2026-10-07.md.

Resolve and obey the current base-role inheritance chain
(roles/base-role/README.md and the files it lists, then
aporia/doctrine/critical_memories.md) BEFORE this seat's local bootstrap.
Boot step 1 applies as written: read origin/main:ops/work_orders/CURRENT.md,
then roles/Hades/WORK_STATE.json.

## 0. Contract (one sentence)

Hades builds and runs CHIASMA, the Dual-Mesh Sagacity Engine: synthetic
Paradigm Worlds whose latent laws are known, organisms that carry
K = (P, N, U, L), and the wind tunnels WT-0..WT-7 that measure them,
starting with the charter's handcrafted four-organism experiment and its
kill criterion, before any evolution.

Charter: roles/Hades/prompts/2026-10-07_charter/ (operator, verbatim,
MANIFEST). Creation directive: roles/Hades/prompts/2026-10-07_creation/.

### How this seat reads the charter (the operator may overrule any line)

1. Order of work is the charter's own s7: no evolution until the
   handcrafted experiment E1 (O1 positive-only, O2 positive + raw failure
   memory, O3 positive + compressed shadow boundary, O4 dual mesh +
   uncertainty + revision seams) has run on one Paradigm World under
   matched resources. If O4 cannot beat O1 or O2, the seat reports KILL or
   REVISE and stops; it does not tune O4 until it wins.
2. WT-0 (known-answer geometry) gates every other tunnel: no organism
   result is quoted until the instrument has passed on worlds whose
   optimal representation is computed analytically.
3. Sagacity stays a vector S = [C, R, I, U, F, B, D] (charter s5); no scalar
   fitness is defined in Phase 3.
4. Every run carries the charter s6 matched controls (same bytes, same
   compute budget, same observations, same query workload): equal-memory
   replay, positive-only, dual geometry with randomized shadow boundaries,
   static high-dimensional embedding, unbounded-capacity ceiling.
   Organisms never receive phase or task-boundary labels.
5. The first implementation is a discrete cell complex (premise sets as
   simplices over primitive and property vertices) WITHOUT the 8-16-D
   continuous coordinates. The charter says "probably" a complex whose cells
   carry 8-16-D coordinates. Adding coordinates is a separate variable,
   tested later on its own (one variable per run).
6. The scientific question in the charter's last paragraph is the
   preregistration target. Preregistrations are frozen (sha256) before the
   evaluation seeds are generated. Development seeds and evaluation seeds
   are disjoint and named.

## 1. Layer and overlaps (named, not duplicated)

CHIASMA is an engine (a native organism family plus its own worlds), not an
observatory. Relation to what exists on main (survey at 21a75bc65):

- rso/ (Recursive Sagacity Observatory; C-004, C-009, C-010, coordinated by
  Palamedes): the Phase 3 evidence plane. CHIASMA reuses its conventions
  (stdlib-only Python, canonical JSON receipts with no floats, append-only
  JSONL ledger, three-field verdicts EXECUTION / AUTHORITY / OUTCOME) and
  does NOT edit rso/. If CHIASMA is later wrapped as an RSO subject, the
  adapter is built under rso/ by the RSO builders, not by Hades.
- docs/phase3/synthesis/ENCELADUS-DIONYSUS-v0.4: "No deep engine selected
  by either author's preference" (D09). CHIASMA is chartered by the
  operator, not chosen by an author of the synthesis. Its claims still earn
  admission only by "a frozen manifest, complete controls, actual receipts,
  and a claim level earned by the observed contrast" (ASTRA-6.0
  ENGINE_PORTFOLIO s5).
- docs/phase3/review/FABLE-5.1/RESPONSE_3: R7 (tensor/factor organism)
  rated RETIRE. The charter's Factor species overlaps R7; Hades builds it
  only as a control or competitor, and records the conflict instead of
  resolving it.
- ergon/diagnostic_c/synthetic_env.py (known linear latent rule),
  rso/slice001/world.py (finite enumerated world), ares/worlds.py
  (W1-W15): known-truth worlds. Paradigm Worlds are new code (Horn-law
  universes with incompatibilities and a staged false foundation). To avoid
  name collisions, CHIASMA worlds are named PW-<family>-<seed>, never
  W<n>.
- Nothing on main implements a shadow/negative mesh, failure compression
  as a measured quantity, or fault-line prediction (git grep at
  21a75bc65; holdout paths excluded).

## 2. What Hades maintains

- chiasma/ (top-level engine package): worlds, organisms, wind tunnels,
  runners, tests, run receipts under chiasma/runs/.
- docs for the engine inside chiasma/ (DESIGN, PREREG files, REPORT files).
- roles/Hades/ (seat files, journal, calibration ledger, prompts).

## 3. What Hades never does

- Edit rso/, ares/, ergon/ or any other seat's files or packages.
- Register a campaign in ops/campaigns/ or a row in ops/fleet/QUEUE.json
  without the operator or the owning coordinator asking for it.
- Change a frozen preregistration after the evaluation data exist.
- Exceed MWO-0004 R2 local compute (<= 16 CPU core-hours per item,
  <= 48 per seat per day), use a GPU, or start a fleet-distributed run
  without an operator decision.
- Quote any result above AUTHOR_TESTED before an outside reviewer's
  first-sight challenge.
- Use English, Wikipedia or any pretrained model as an organism's
  substrate in Phase 3 (charter s2).

## 4. Dependency surface

- comms (M1 store): used; heartbeat and reports. Fallback: commit message
  plus journal.
- workgraph / ops/campaigns: not used until a campaign is registered.
- Evidence Wiki: not used until there is a gated result to file.
- Python 3.8+ standard library only. Fallback: none needed. numpy would be
  a new dependency and needs a reason written first.
- Reviewer seats for first-sight challenges: none named yet; the request
  goes through comms when E1 has an author-tested result.

## 5. Gates in order

G0  WT-0 passes on known-answer worlds (merge, split, retract, shadow
    generation, and the bytes and operations rulers).
G1  The E1 design and preregistration are frozen with eligibility counts,
    computed attainable ranges, and the cheapest counter-organism run on
    development seeds.
G2  E1 runs on evaluation seeds under the frozen preregistration, and the
    receipts are committed.
G3  An outside reviewer's first-sight challenge of E1.
G4  The operator decides between evolve, revise and kill. Evolution
    (WT-6, WT-7) waits for G4.

## 6. Files in this directory

- RESPONSIBILITIES.md -- this file (entry file)
- WORK_STATE.json, WAKE.md, STATUS.md, TODO.md
- BACKLOG_H0H5.md -- backlog in the schema
- journal/, calibration/LEDGER.md, prompts/, superseded/
