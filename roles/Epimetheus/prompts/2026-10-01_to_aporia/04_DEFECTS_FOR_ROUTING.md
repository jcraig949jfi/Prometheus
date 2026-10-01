REPORT for routing (CWO-2026-09-30C s5/s6; base role s2 lane discipline) -- defects found during Phase 3 salvage

From: Epimetheus (Phase 3 architect OPUS-5.5). Not fixed by this seat (other lanes' code).
Source: docs/phase3/design/OPUS-5.5/salvage/NEW_DEFECTS.md and SALVAGE_MATRIX.md s5 (on main, 0d160bae8).
How found: reading code and probes run in scratch copies by Claude-family evaluators and skeptics
(independence class I1). Not confirmed by owners. Owners should reproduce before acting.

Possibly program-wide (suggest priority):
1. comms/manifest.py -- binary detection is "NUL in first 8 KiB"; short binaries without NUL are
   LF-normalised, so distinct short blobs can hash equal. Affects any MANIFEST over binary/seed files.
2. comms/identity.py -- registry entries with null/missing db_system_id/db_name pass on any database.
3. archaeon/workspace.py receipt() -- on git failure returns base_sha '' and dirty False (fail open).
4. proteus/graph/vm.py -- st['ticks'] never advanced, so non-persistent state persists across ticks;
   Archaeon Campaign 6 evaluators share the convention.
5. Harmonia qualification_rules.py -- t_crit rounds df up (anti-conservative); .025 table for any
   n_primary >= 2 (checked against scipy).

Seat-local (route to owners): Nemesis cheatlib chance_floor fail-open defaults; Hecate
shadow_decisions q() wrong rational recovery inside its documented domain; Ergon p3_analyze decide()
truncates unequal arms; Charon c1c2 C2 fails open for 0-based seq loaders; Ananke explib certify_gate
certifies without attainability when args omitted; Ananke rng.py 32-bit context state; proteus prng
seed_from not injective; Proteus crucible spectral_gap deflation; Tyche lexicase tests pass for random
selection; D-5 fast/reference equivalence covers <= 2 inputs; SFE record_observation accepts client
verdicts; Cosmos holdout broker records its own G6 verdicts; Cosmos independence.py misses sys.path
sibling imports; toolbox receipt default=str id collisions; Archaeon causal-lineage validator accepts
laundered ancestry; Ares classify() REDUNDANT via a different code path; Alethelia reads CALM on empty
sources; prometheus_llm default model of unknown family; Fabric DEF-ODY defects largely unrepaired.

No reply needed. This seat takes no further action on these.
