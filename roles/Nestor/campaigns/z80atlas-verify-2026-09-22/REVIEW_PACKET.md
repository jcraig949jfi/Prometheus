# Cycle-9 repair packet - FOR OPERATOR REVIEW

**STOP STATE. Nothing is frozen and nothing has launched.** No final hash is written into
`PREREGISTRATION.md`. No production observatory exists. The predecessor's 72-hour
evidence is untouched: this directory carries its own copy of the substrate and every
tool here reads `z80atlas-2026-09-19/observatory` read-only.

---

## 1. Repair commit

Repairs are implemented and staged on branch `nestor/sidequest-graphworld-2026-09-14`.
The commit SHA is recorded at the end of this file after the commit lands; the packet is
written first so the SHA covers it.

## 2. Test matrix - repaired substrate

Every gate exits 0.

| gate | file | checks | result |
|---|---|---|---|
| T-P1, T-P2, T-P3, T-P8, T-P9, T-P10 | `tests/test_repairs.py` | 18 | PASS |
| T-P4 reservoir certificate | `tests/test_p4_reservoir.py` | 8 | PASS |
| T-P5 index-only adjudication | `tests/test_p5_index.py` | 9 | PASS |
| T-P7 bundle integrity | `tests/test_p7_bundles.py` | 18 | PASS |
| P-6 report audit (predecessor) | `../z80atlas-2026-09-19/test_report_audit.py` | 15 | PASS |
| 10 calibration controls | `controls.py` | 10 of 10 | PASS, 8.8 s |

Detail on the six substrate repairs:

| check | measured |
|---|---|
| T-P1 certificate built | founder niche 0, migration 0 to 2, lineage_len 2 |
| T-P1 truncated lineage | certificate is `None`, not a weaker certificate |
| T-P2 A star | ancestry 1, causal 1, propagating 0 |
| T-P2 B ordinary descent | ancestry 4, causal 0 - causal does not increase |
| T-P2 C causal chain | causal depth 4, equal to the constructed chain |
| T-P3 historical vs final | ever True / 1.00, final False / 0.00 |
| T-P8 isolated niches | initial [32, 32, 32, 32], spread 0, migrations 0 |
| T-P8 reservoir | easy-niche share at t=0 is 0.250 |
| T-P9 composition | niche 0 easy, niche 1 hard, coevolution live, deterministic |
| T-P10 grammar | `ENV_MIG` absent from Cycle-9 structure levels |
| T-P10 inertness | predecessor `env_difficulty` returns 1.0 for every niche under `ENV_MIG`, so the `< 0.5` migration skip can never fire |

## 3. Negative-control matrix - every test must be able to fail

A guard that cannot fire proves nothing, and the predecessor shipped three such flags.
Each repair test was rerun against an injected defect restoring the predecessor's exact
behaviour.

| injected defect | restores | test | result |
|---|---|---|---|
| migration events not logged | `ct["migrations"] += 1` with no lineage event | T-P1 | caught |
| every birth edge marked causal | untagged lineage tuple | T-P2 B | caught, causal rose to 4 |
| `_initial_niche` returns 0 | `_place(g, anc)` default | T-P8 isolated | caught, initial [128, 0, 0, 0] |
| `_initial_niche` returns 0 | as above | T-P8 reservoir | caught, easy share 1.000 |
| legacy `_env_spec_for` | verbatim predecessor method | T-P9 | caught, niche 0 easy=False |
| order leaked into content | arrival index inside scientific content | T-P7 | caught, 2 distinct blobs |
| adjudication on incomplete bundle | no completeness precondition | T-P7 | caught |
| conflicting re-run overwrites | silent overwrite | T-P7 | caught |
| real numeric change | sanity of the comparison itself | T-P7 | caught |
| legacy reservoir flag condition | structure + moat + any crossing | T-P4 | 5 divergent cases, all caught |
| drop each required index field | Z80A-D03 whitelist omission | T-P5 | all 11 fields change a verdict |

## 4. Exact semantic diffs against the predecessor

| module | lines | change |
|---|---|---|
| `world.py` | +277 / -22 | P-1 migration events, birth-niche map, ancestry certificate; P-2 causal depth and propagating replicators; P-3 four separate outcome fields; P-8 balanced niche init; P-9 explicit env/structure composition; H2 implant arms; H3 migration disable |
| `tasks.py` | +37 / -3 | `output_gate` and `cue_cost` on `TaskSpec`, `cue_index()`, gate wiring in `score()` |
| `z8.py` | +17 / -1 | `out_gate_reads` on `Ctx`; `OUT` discarded while `in_reads < out_gate_reads` |
| `grammar.py` | +10 / -2 | `ENV_MIG` removed from `structure` and from the niches constraint |
| `observatory.py` | +9 / -4 | tagged lineage records; a complete lineage is never thinned by the disk budget |
| `bundles.py`, `specials.py`, `manifest.py`, `specimens.py`, `smoke.py` | new | P-7, P-4, the fixed manifest, the frozen panel, the smoke |
| `adjudicate.py` | rewritten | P-5, index-only, no per-run fallback path |

**VM equivalence.** With the gate unrestricted the VM is bit-identical to the
predecessor: 400 random programs compared on outputs, op count, input reads and final
arena bytes, **0 differences**. The H1 intervention therefore adds no confound to the
ungated arm.

## 5. Smoke timings

Short runs at 120 epochs, projected to full tier budgets.

| hypothesis | tier | arms measured | runs | est. s/run | est. cpu-h |
|---|---|---|---|---|---|
| H1 | S | 1.39 to 1.44 s across all four arms | 240 | 7.1 | 0.47 |
| H2 | M | 6.28 to 6.53 s across three arms | 240 | 107.3 | 7.15 |
| H3 | M | 5.56 to 6.13 s across three arms | 144 | 98.8 | 3.95 |
| H4 | L | endogenous 0.62 s, external 2.46 s | 128 | 51.3 | 1.82 |

Total 13.40 cpu-hours, 2.23 wall-hours at 6 workers, against 20.40 usable hours
(24 h envelope at 0.85 drain margin). **Fits. `SCALE_RULE` was not triggered.**

Bundle integrity on real engine output: two completion orders with a simulated kill and
resume between arms produced **byte-equivalent scientific content and identical
verdicts**.

## 6. Fixed job manifest

| quantity | value |
|---|---|
| bundles | 252 |
| runs | 752 |
| H1 / H2 / H3 / H4 bundles | 60 / 80 / 48 / 64 |
| validation problems | 0 |

Every arm names a grammar-valid cell and every bundle's declared cardinality matches its
arm list. After freeze the runner consumes this manifest only: no UCB, no promotion, no
exploration floor, no replacement sampling, no result-dependent allocation.

## 7. Proposed hashes - NOT written into the preregistration

| hash | value |
|---|---|
| grammar | `61da6513ea0b36e04d4b2164a208fe4e1fd700e078076db847dc037f1c327f4e` |
| manifest | `eac49e63f53aba0a2eb7c108117fadbfecf9e750e43dff9822415c6accabb187` |
| specimen panel | `005a495cdcaf183ac17e9047e3c19f8995da558e2905141294b2e4b4ba2e8c12` |
| protocol (module digest) | `911a1754d3bd06db4c653eaee3e197aa69f37854a78124af7e9e1690a7b37a79` |

## 8. Revised preregistration

`PREREGISTRATION.md` is at **rev B** with a 14-row amendment log covering every review
finding: the H1 redesign and the withdrawal of the cycle-8 misattribution, causal
replication depth, the frozen specimen panel, the three-arm reservoir design, the H4
block decomposition, the fixed manifest, and new repairs P-7 through P-10.

---

## 9. Newly discovered defects

Three, found while implementing. All are recorded, none is silently repaired.

### C9-D01 - the predecessor's spontaneity result has ZERO reproduction diversity

**All 1,031 admissible spontaneous replicators are `PAIR_EXECUTION`.** Not a majority:
every single one.

| reproduction | admissible spontaneity runs |
|---|---|
| PAIR_EXECUTION | 1031 |
| every other level | 0 |

This materially narrows the predecessor's headline result, and it was not in REPORT.html
revision 2. Pair-tape replication is detected by a different code path from the
ALLOC/BIRTH evidence gate: a tape half counts as replicated when the donor wrote at least
25 percent of it. So the finding reads more precisely as *one half of a shared tape
overwriting the other, in the one physics where that is possible*, and it rarely
propagates, since 911 of the 1,031 have ancestry depth 1.

Consequence for H2: the specimen panel **cannot** be reproduction-diverse. The panel is
diverse over structure and representation within `PAIR_EXECUTION`, and H2 is therefore a
test of pair-tape propagation specifically. The manifest records
`reproduction_diversity_available: 1` rather than letting "mechanism-diverse" imply
otherwise. **Reviewer decision: accept this scope, or add a non-pair-tape arm that the
predecessor evidence cannot motivate.**

### C9-D02 - P-10 and the H2 panel collide

`ENV_MIG` is removed by P-10, but **177 of the 1,031** admissible specimens sit in
`ENV_MIG` cells and cannot be instantiated under the Cycle-9 grammar. They are excluded
from the panel rather than repaired into a neighbouring cell, which would make a specimen
a different experiment from the one it was selected for. 854 candidates remain and the
16-specimen panel is drawn from those.

### C9-D03 - the audit receipt certified a deleted temp file

Found while verifying the predecessor report on main. `report_audit.py` wrote
`AUDIT_RECEIPT.json` next to itself rather than next to the report it audited, so
`test_report_audit.py` - which audits twelve mutated copies in a temp directory -
overwrote the real receipt with the last mutation's FAIL. The committed receipt named a
file that no longer existed. Fixed at the cause in commit `b05a34f1b`; the receipt now
lands beside the artifact it certifies.

---

## 10. Open questions for the reviewer

1. **Envelope underused.** The manifest projects to 2.23 of 20.40 usable wall-hours,
   about 11 percent. `SCALE_RULE` only reduces, so I did not enlarge it. H4's decision
   rule needs 6 of 16 seed-pairs and H2's needs 3 of 5 seeds; both would be better
   powered with more seeds, and roughly 9x the manifest would still fit. **Raising seed
   counts before freeze is a reviewer decision, not mine.**
2. **C9-D01 scope.** Does H2 proceed as a pair-tape propagation test, which is what the
   evidence supports, or is the hypothesis rewritten?
3. **H4 arm asymmetry.** The endogenous arm ran 0.62 s against the external arm's 2.46 s
   at equal epochs, which means the endogenous population is dying early. If it goes
   extinct before validation in most seeds, block A measures extinction rather than
   competence. Worth a targeted pre-freeze check.
4. **Two notes from implementation**, outside the repair scope and not acted on:
   `adjudicate()` computes `n_rows` via `len(list(rows))`, which misbehaves for a
   generator, harmless on the file-backed path; and `bundles.default_rule` reads the P-3
   final-state pair with `CROSS`/`MARGIN` mirroring `adjudicate.py`, so if those
   constants ever drift apart the gate should say so.

---

## 11. Gate status

| # | gate | state |
|---|---|---|
| 1 | Operator review of PREREGISTRATION rev B | **pending** |
| 2 | Operator review of repair tests T-P1..T-P10 | **pending** |
| 3 | Every T-P test fails on injected defect, passes on repaired substrate | **done**, section 3 |
| 4 | 10 calibration controls | **done**, 10 of 10 |
| 5 | Verification smoke: real bundles, same-seed controls, reordered completions, forced restart | **done**, section 5 |
| 6 | Freeze: write hashes, record CALIBRATION.json | **NOT DONE, awaiting review** |

Cycle 9 does not launch until rows 1, 2 and 6 are complete.
