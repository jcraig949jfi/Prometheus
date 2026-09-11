# Icarus calibration ledger

Kept because it is unflattering (base role s2). One row per wrong call,
with the direction the error pushed and how it was caught. Seeded
2026-09-11 from the git history of agents/icarus/ and the Harmonia
reviews that read it; the seat kept no such ledger while it ran. Every
row is a claim the loop (or the people running it) made about the
REASONER that turned out to be a claim about the LOOP.

Format: date | call | direction of the error | how caught | source

2026-05-28 | Rungs R0 and R1 were treated as discriminating tests of the reasoner | flattered the ladder (a rung every version passes measures nothing) | tier_calibration.py: tier_R0 and tier_R1 "too_weak_all_pass" on all 5 versions, tier_R2 "vacuous", holdout_R1 "unreached_all_fail" | agents/icarus/state/tier_calibration.json (generated 2026-05-28T11:10Z); pivot/icarus_v3_design_pressure_2026-05-28.md Q10
2026-05-29 | The probe schema handed the generator surfaced ground_truth | flattered the reasoner (a cheat vector) and misled R3 | found and removed at 52a10049f | git log 52a10049f "stop surfacing ground_truth in probe schema (cheat-vector + R3 mislead)"
2026-05-29 | The R5 stall was read as a substrate or capability wall | overstated the capability limit | the wall was the edit interface: full-file edit mode f82cfabe1; two masking bugs (blind Generator, read-only clones) 38df79441 | git log 2026-05-29
2026-06-10 | The R5 stall (again) was read as a reasoning wall | overstated the capability limit | the generator's 11 KB file was being corrupted under JSON escaping; sentinel raw-file blocks 2883cffd3; probe schema sampled only the clean version and hid the invariant field; R5 cleared 96814789f | roles/Harmonia/RESUME_20260615_icarus_ladder.md "The R5 wall was infrastructure + interface knowledge, never reasoning"
2026-06-15 | Lens verdicts on cycle 19 read the whole reasoner as absent | the lenses were blind to the source (an oversized reasoner blanked it), so the historian lens ruled on nothing | 98f95a22d | git log 98f95a22d
2026-05-25 to 06-15 | The lane reframe declared "every cycle emits a typed training object" as the unit of output | overstated the loop's output by ~2.75x if the reframe is read as satisfied | 22 cycles ran, 8 typed objects exist; cycles 0-12 emitted nothing | roles/Harmonia/POSITION_20260812_north_star_reset.md lines 82-88; agents/icarus/state/training_stream.jsonl (8 rows)
2026-05-27 | A "working report" (whitepapers/icarus_synthetic_reasoning_v01) framed the ~15-cycle evidence in publication form | the form, not a number; HARD-1 (2026-05-06) already forbade it | doctrine HARD-1 read on this pass | aporia/doctrine/critical_memories.md HARD-1
2026-09-11 | This pass's first draft of the archaeology nearly proposed that Icarus own "residue navigability" for the ecology | would have claimed a lane that Ergon (memory metabolism) and Kairos (failure surface) already hold | read the sibling charters before writing (base s1.3) | roles/Icarus/ARCHAEOLOGY_2026-09-11.md section D, option (b) narrowed to Icarus's own residue

Pattern across the rows: five of eight errors read a defect of the loop
(interface, schema, serialization, lens blindness, cheat vector) as a
fact about the reasoner, in the direction of a capability WALL. The
program later made that a rule (reasoning_ladder.md rule 3). For this
seat the flattering direction is therefore not "the reasoner is
capable" but "the wall is real and interesting"; the drift guard audits
that direction last.
