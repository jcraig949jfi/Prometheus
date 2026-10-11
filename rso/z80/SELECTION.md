# Z80 Atlas phenomenon selection and world-demand gate (C-017-T020)

Author: Cadmus[harry1-914f6281], claude-sonnet-5-5 (Q2), headless on harry1. Written 2026-10-11. Read-only against
`archaeon/`, `prometheus/z80atlas/`, `roles/Archaeon/`. No Archaeon seed or the evidence bundle was used. Base `origin/main`
`6bd9a73465cea43bb04e03b6efbcd08b522717b0`; `archaeon/z80atlas` last changed at `863d34a55` (per `rso/z80/CONTRACT.md` s2).
Pinned to engine files as read: `engine.py` 465 lines, `grammar.py` 246, `tasks.py` 93, `vm.py` 141.

## 1. Decision

**The operator's candidate question ("functional inheritance vs environmental reconstruction vs seeded copying") must be
re-scoped before an adapter exists.** The demand gate (section 3) says the world rewards REPRODUCTION OF FUNCTION under a
task-coupled reward; it does not reward endogenous heredity as such. A runner-reproduced (EXTERNAL) lineage keeps the same
function at the same level, with no copier. So retention cannot be the discriminating endpoint for a Z80 adapter.

**Carrier:** world `well_mixed / unlimited / fixed`, substrate `vmcopy`, G = 32, task `ECHO_forced`, planted starters through
the engine's own transplant path. Unit = the run.

**First Z80 question for an adapter campaign (re-worded):** *Given a final population whose members all carry a working
function, can the Observatory attribute WHO WROTE THE BYTES: parent execution (endogenous), runner (EXTERNAL), neighbour
(environmental reconstruction), or insertion (seeded/transplanted) -- from the bytes, the generation counter and the matched
arm, without trusting the engine's provenance fields?* Retention is demanded and measured as the precondition (D, section 3);
attribution is the object.

If the operator wants retention proper as the claim, the finding is: **at local budgets Z80 does not demand it** (an
EXTERNAL arm retains function as well as the endogenous one). Legitimate outcome, stated plainly.

## 2. Subjects: native, testable, and in reach

| Subject | Native? | Testable now? | Search accessibility at local budget |
|---|---|---|---|
| Planted heritable program `tasks.task_then_replicate(ECHO_forced)` (`tasks.py:90`) | yes, hand-built from engine pieces | yes, seconds | NOT in reach: random founders are exact copiers at ~9.6e-6 (`archaeon/z80atlas/census/RESULTS.json`: 95/10M EXACT_GATED, vmcopy32); DENOVO-01 0/80 (`denovo/RESULTS.json`) |
| Function-only witness `tasks.WITNESS["ECHO_forced"]` (`tasks.py:68`) | yes | yes | IN reach, but only under EXTERNAL reproduction: this packet's RANDOM_EXT_GATED found an ECHO solver in 7/24 runs at 200 epochs |
| Bare replicator `tasks.replicator` (`tasks.py:81`) | yes | yes | n/a (planted) |
| `grammar.positive_controls()` (`grammar.py:229`) | yes | not run here (full-length runs; contract s7) | not assessed |
| Anything evolved in Archaeon's committed runs | read-only | not used: registered seeds | EXTERNAL-evolved ECHO crossings exist in `postcampaign/Z80ATLAS_POSTCAMPAIGN_ADJUDICATION_2026-09-23.md` (random-origin, first crossing epochs 4-1997); none endogenous without seeded ancestry |

The join (a function that is BOTH discovered and endogenously heritable) is the unreachable cell: function is searchable under
EXTERNAL only; copiers are searchable under neither at local budget. So every endogenous-heredity subject is planted and
inserted-ancestry by construction (`engine.py:179-195`, `ORIGIN_TRANSPLANTED`). Not a limitation to hide: it IS the
engine's state, and Archaeon's own rulings reached the same place.

## 3. Demand gate (new seeds, committed with command)

`rso/z80/demand/demand_gate.py`; decision rule committed before the run in `rso/z80/demand/PREREG.md` (commit a519834c3).
Result `rso/z80/demand/demand_result.json` (sha256 prefix `90a352355ea2660a`). Command from the repo root, one process, ~10 min:

    python -m rso.z80.demand.demand_gate rso/z80/demand/demand_result.json 12 200

Seeds 17_020_001 + 100*arm + k (disjoint from 16_021_xxx, 16_020/16_030_xxx, and the small integers Archaeon registered).
12 runs per planted arm (24 for random founders), 200 epochs, N = 128, 13 planted cells. Endpoint re-derived from tapes with a
zeroed neighbour on 8 fresh ECHO cases (F), >= 0.9 window written (C), generation >= 10 (D): never the engine's `score` or
provenance flags. Replay: a 40-epoch pilot run twice (default and `PYTHONHASHSEED=77`) is byte-identical (`cmp`); the full file
was run once.

| Starter | Physics | Reward | runs with D | runs with F | extinct | F / pop | Notes |
|---|---|---|---|---|---|---|---|
| H heritable | ENDO | GATED | **12/12** | 12/12 | 0 | 1463/1489 = .983 | |
| H | ENDO | IMPL | 8/12 | 8/12 | 0 | 401/1517 = .264 | copier kept (C 1471), function eroded |
| H | EXT | GATED | 4/12 | 12/12 | 0 | 1302/1526 = .853 | copier decays (C 35) |
| H | EXT | IMPL | 0/12 | 10/12 | 0 | 290/1519 = .191 | |
| NH function only | ENDO | both | 0/12 | 0/12 | **12/12** | 0 | no child; gone by max_age (60) |
| NH | EXT | GATED | 0/12 | **12/12** | 0 | 1323/1515 = .873 | no copier at all |
| NH | EXT | IMPL | 0/12 | 11/12 | 0 | .198 | |
| BR broken copier | ENDO | both | 0/12 | 0/12 | 12/12 | 0 | |
| BR | EXT | GATED / IMPL | 0/12 | 12/12 / 12/12 | 0 | .870 / .300 | |
| NF copier only | ENDO | GATED / IMPL | 0/12 | 0/12 | 0 | 0 | copies (C 1329 / 1424), never has F |
| NF | EXT | both | 0/12 | 1/12 | 0 | .001 | one random ECHO find |
| random founders | ENDO | GATED | 0/24 | 0/24 | 24/24 | 0 | 0 endogenous births (lottery, expected ~.02) |
| random founders | EXT | GATED | 0/24 | 7/24 | 0 | 439/3037 = .145 | function search works under EXTERNAL |

Readings, kept apart (directive s4), against the rule in PREREG.md:

1. **Capacity: PASS.** H_ENDO_GATED has a functional, copying, generation >= 10 organism in 12/12 runs (1409 of 1489 final organisms).
2. **Heredity is what keeps function (endogenous arms): PASS but near-trivial.** NH_ENDO and BR_ENDO are extinct in 12/12 runs because
   unreproduced organisms die at `max_age` 60 (`grammar.py:FROZEN`). That is a construction control (can the world lose function?
   yes), not a selection finding.
3. **Reward selects: PASS, large.** Per-run F fraction in H_ENDO_GATED is .95-1.00 (12/12 runs) vs H_ENDO_IMPL 0.00-.88; the sets do
   not overlap. fF .983 vs .264 (difference .72, rule >= .10). Without a task-coupled reward the copier survives and the function
   erodes by copy noise and background mutation: 285,399 vs 100,372 endogenous births.
4. **Heredity-specific vs EXTERNAL: FAIL (important).** NH_EXT_GATED keeps F in 12/12 runs at .873, BR_EXT_GATED 12/12 at .870, H_EXT_GATED
   12/12 at .853, with C ~ 0. Endogenous .983 vs EXTERNAL .853-.873 is a modest difference; any reproducer keeps function under reward. By the
   rule: **the world demands reproduction of function, not endogenous heredity.**
5. **Run-level "has D" is a weak endpoint.** H_ENDO_IMPL passes "run has a D organism" in 8/12 runs with no task reward at all (drift
   plus a copier). Do not use the any-D indicator; use the per-run F fraction among copiers.
6. **Retention vs causal dependence vs qualification:** retention is shown (1,3); causal dependence on parent-written bytes is shown only
   against absence (2: no copier, no child) and is NOT separated from EXTERNAL reproduction (4); qualification of any detector is open.

## 4. Directive-s4 distinctions mapped to native controls

| Distinction | Native control | Machinery |
|---|---|---|
| capacity | planted H; the lawful reference | `tasks.py:90`; row H_ENDO_GATED |
| world demand | reward on/off (GATED vs IMPL), function-only and broken arms | `pressure` axis, `grammar.py:13`; rows above |
| search accessibility | random founders ENDO (copier lottery) and EXT (function search) | `census/RESULTS.json`; RANDOM_* rows |
| inheritance-as-retention | H_ENDO vs NH_ENDO vs BR_ENDO | rows above |
| causal dependence | broken copier BR (function intact, replication cut); a bytes-level cut, not a label | `smoke_heredity.py` H_broken, here BR |
| qualification | NOT done. Needs a cheat: runner-provided birth labelled endogenous (the engine halts on it, `engine.py:434`) and an ENV arm (function in the neighbour, `smoke ENV`), neither run at population scale here | |
| lottery prior | RANDOM_ENDO_GATED: 0 births in 24 runs; census 9.6e-6 | any heredity claim must be reported against it |
| transplant arms | physics swap (ENDO<->EXT) done as the H rows; world swap, environment swap (`scheduler.py:246-262`) NOT run | |
| matched control | EXTERNAL flip of every planted arm (`grammar.matched_controls`, `grammar.py:183`) | done, and it decides reading 4 |

## 5. Unit of observation

The **run** (one seed). Organisms in a run share ancestry (planted cells are clones; descendants are lineages), so organism
counts are not independent observations and the fractions above are descriptions, not test statistics. The gate is on per-run
integers (runs with D / F, 12 per arm) and on the non-overlap of per-run fractions. For lineage questions the unit is the
founder (`anc`), which this packet re-derives nothing from; a later adapter must re-derive `anc` from tapes instead of trusting
`provenance` (registry `stratified-holm-analysis` limit). `ruler-binary-retention` does not apply (not a binary bit, dependent
observations; `CONTRACT.md` s5).

## 6. C-016 lessons applied (`rso/ensorain/ONBOARDING.md` s5)

1. **No self-relative frozen contrast.** The control for "function kept by heredity" is not "the same genome with heredity switched off";
   it is the matched EXTERNAL arm and the function-only arm, which carry the function in a different way. The result of that contrast
   (reading 4) is exactly the C-016 failure mode in the other direction: the contrast that looked decisive (NH_ENDO extinct) is guaranteed
   by `max_age`.
2. **An endpoint no fixed prior satisfies.** D requires generation >= 10, so a planted tape (generation 0) cannot satisfy it by being
   planted; a fixed prior of "function + copier" cannot pass it. The weakness is reading 5: any-D is satisfied by drift in 8/12 runs.
3. **A stochastic non-learner-analogue.** NF_ENDO (a noisy copier with no function) and the IMPL arms (copy noise, no selection) play it:
   they replicate and drift and do not produce F. Qualification of a detector should include H_ENDO_IMPL, which a retention-only rule
   would wrongly credit (F/pop .264 with 385 D organisms).
4. **Structure from liveness, not declaration.** F and C are measured by running the bytes (`vm.execute`); `generation` is the one engine
   field used and it is a counter, not a claim. `provenance`, `spontaneous_replication`, `score` are not read.
5. **Hash guards are not behavioural pins** (lesson 3 there): this packet has no mutants; the broken-copier arm is the only behavioural cut.

## 7. Limits

- 12 runs per planted arm, 200 epochs, one world (well-mixed). No niche, migration or environment dynamics were tested.
- Starters are planted in 13 cells of an otherwise empty world through the transplant path; the seeded-replicator path (random fill
  + 10% seeded) was not run as an arm.
- C uses a zeroed neighbour, so organisms that copy only when a neighbour is present are not counted as copiers (conservative).
- Full file run once; replay byte-identity was checked on a reduced run, not on the full file.
- The engine's `ENDOGENOUS_PARTIAL`, `OVERWRITE`, `CONSTRUCTIVE` and `PAIR_EXECUTION` physics were not run.
- The 60-epoch pilot (2 seeds, /tmp, not committed) preceded the decision rule; the rule was fixed after it. Disclosed in PREREG.md.

## 8. Recommendation

An adapter packet, if the operator accepts the re-worded question (section 1): a small one. The Z80 side is already a pure function
of (spec, seed) with a transplant path; the new work is the bytes-level re-deriver (F, C, generation, writer attribution) plus the ENV
and runner-provided-birth cheat arms, and registering the engine files. Ensorain's registry limits apply (no entry covers a population
with a generation boundary). If the operator needs retention as the claim, record "not demanded at local budgets" and select a
different third engine.
