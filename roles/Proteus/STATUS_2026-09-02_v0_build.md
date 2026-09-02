# Proteus — V0 build status, 2026-09-02

**Disposition:** BUILT and STOPPED, per the addendum. Foundry-local tests only. No world
touched, no campaign launched, no qualification run, no channel layout authored.

## Deliverables (brief §15) — status with the artifact that proves it

| # | deliverable | status | artifact |
|---|---|---|---|
| 1 | architecture | done | `proteus/ARCHITECTURE.md` |
| 2 | genome/manifest schema | done | `proteus/contracts/player_manifest.schema.v0.json`, enforced by `vm.validate_manifest` |
| 3 | mutation grammar | done, **neutrality gate NOT PASSED** | `proteus/foundry/grammar.py` v0.2, `proteus/MUTATION_GRAMMAR.md` |
| 4 | deterministic generation | done | `generate.py`; `tests/test_replay.py` |
| 5 | lineage/checkpoint semantics | done | `lineage.py`, `contracts/lineage_record.schema.v0.json` |
| 6 | resource-accounting hooks | done | `vm.Meter` (vector, no fitness, proxies declared) |
| 7 | world-interface contract | done | `contracts/WORLD_INTERFACE.md` (no layout, no adapter) |
| 8 | multiplayer interface | done | `WORLD_INTERFACE.md` §4 (operator wiring; nothing player-side) |
| 9 | SFE integration contract | done, provisional | `contracts/SFE_INTEGRATION.md`, `export.py`; four questions to Daedalus |
| 10 | PEW export contract | done, unexercised | `contracts/PEW_EXPORT.md`, `export.pew_rows`; client not on main |
| 11 | semantic-quarantine audit | done, string layer PASS | `audits/quarantine.py`; ontology layer is the reviewer's |
| 12 | small diversity demonstration | done ×3, instrument qualified | `v0/DIVERSITY_*`, `v0/demo_grammar_v0_1/`, `v0/demo_grammar_v0_2/` |
| 13 | replay tests | done, 9 pass | `tests/test_replay.py` |
| 14 | mutation tests | done, 7 pass; **A6 hard gate FAIL after 3 preregistered runs** | `tests/test_mutation.py`, `v0/NEUTRALITY_*` |
| 15 | failure tests | done, 7 pass | `tests/test_failure.py`, `qualify.py` |
| 16 | first campaign proposal | done, not launched | `v0/CAMPAIGN_1_PROPOSAL.md` |

## The one thing that did not pass

The neutrality hard gate (A6). Three grammars, three frozen preregistrations, three runs, all
kept: v0 grew everywhere it was not pinned (a real weight defect, mine); v0.1 was flat at the
middle cohort and failed at both bound-adjacent cohorts; v0.2 removed the moving-cap pin (cap
occupancy 0.081 → 0.018 → 0.000) and still failed at the small cohort (reflection off the
minimum, predicted in the prereg) and at the large cohort's median and last-half slopes (mean
slope interval spans zero). Under the preregistered criteria the verdict is FAIL. The
disposition — whether drift toward the interior near a reflecting bound is a "ratchet" — is
the reviewer's. I committed in the prereg not to revise a fourth time in V0 and have not.

## What changed relative to the pre-execution packet

- C5's per-operator lens tags were withdrawn (A3 makes them meaningless); the knockout vector
  replaces them. Recorded in `MUTATION_GRAMMAR.md`.
- The probe battery is no longer Proteus-authored (A4): inputs derive from the addendum hash.
- `coordinate_census.py` is not used at all (A5), not even as a secondary diagnostic.
- "Subtraction mass exceeds addition mass" was true of operator weights and false of expected
  instructions. Caught by the gate, as the gate was meant to.

## Read ledger

No new world-side file was opened during the build. `roles/Proteus/READ_LEDGER.md` is
unchanged from the kickoff.

## Compute

Everything ran on the F: machine, single core, pure Python 3.12: tests <1 s; each neutrality
run 3–5 s; each diversity demonstration ~19 s. No GPU, no LLM, no API, no spend.
