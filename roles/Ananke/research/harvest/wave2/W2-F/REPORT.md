<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-F; sha256(report)=cbb3816fd70d9983; delimited; see REPORT.provenance.json -->
# W2-F REPORT: explib, a shared below-engine experiment library (Ananke Wave-2, 2026-10-01)

Worker W2-F. Worktree F:/Prometheus-worktrees/ananke-base-role. I wrote only under `roles/Ananke/research/harvest/wave2/W2-F/`. No git writes, no edits outside my directory, no campaigns, CPU only.

## What was built

**Library** (`W2-F/explib/`, pure Python plus numpy, no engine import):

| module | primitive |
|---|---|
| `outcomes` | PASS / FAIL / NOT_VERIFIED; NOT_VERIFIED never counts as a pass |
| `trace` | (2) difference record, three-part closure invariant (node / arrival / edge source), LOCAL vs TRANSPORTED paths, backward cones, cone cuts, dynamic write causes |
| `lockstep` | `LockstepEngine` protocol (the engine supplies make / step / trace and optionally intervene / inputs / arrivals / inflight / edges / readout), the runner, and `crn_check` (a determinism and common-random-numbers self-test) |
| `reach` | (1) UNAPPLIED / NOT_REACHED / ABSORBED / REACHED with path, plus INCONSISTENT (fails closed) |
| `authority` | (3) WriteLedger (who wrote, whether the writer is the owner), declared-authority check, difference-vs-use |
| `controls` | (4) identity audit A1-A4, relation audit, data-identity screen |
| `metamorphic` | (5) metamorphic relations, mutation adequacy, and an operator suite using W2-C's vocabulary |
| `attainable` | (6) gate certification: null, adversary, positive plant, eligibility count, attainable labels |
| `provenance` | (7) hook digest, seed digest, intervention record, plan-precedes check (read-only git), seed reuse, claim support, append-only ledger |
| `stats` | (8) independence-unit declaration, count check, stratified Simpson / MIXED guard; (9) joint-arm (paired) intervals, ratio guard, margin and predictive replication label |
| `toys` | numpy fixture engines used by the core tests |

**Other files:**
- `W2-F/adapters/pte.py`: the only file that imports `prometheus.ananke`. It converts H-INST's DiffTrace into an explib DiffRecord and wraps the PTE reach certificate, pair tables, the C1 zero_comm panel, light-cone ceilings and swap_rel intervals.
- Tests in `W2-F/tests/`: 35 core tests plus 5 PTE adapter tests. Every primitive has at least one test that reproduces a real historical failure.
- `W2-F/checks/core_isolation.py` runs the core tests with `prometheus` and `torch` blocked from import.
- `W2-F/API.md`: the API, a fit-to-existing-machinery table, the "would have caught" table (20 rows), the promotion path and known limits.

**Commands (from W2-F/), with the logs:**
- `CUDA_VISIBLE_DEVICES=-1 OMP_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -p no:cacheprovider` gave 40 passed in 53.5 s, RC=0 (logs/pytest_all.log).
- `PYTHONDONTWRITEBYTECODE=1 python checks/core_isolation.py` gave 35 passed with the engine blocked, RC=0 (logs/core_isolation.log).

**What already existed, and how the API fits it:**
- **prometheus/toolbox (Bellerophon's Worlds Kernel)** is the existing shared library. It has hashed, chained receipts, control-power tests, admission probes and a mutation ledger. explib is the audit layer it lacks.
- **H-INST pte_trace** is generalised by explib's trace and reach modules.
- **Harmonia AP-1.1.0:** explib uses R-A semantics for attainable labels and R-C semantics for the adversary check, with compatible keys. R-B and R-D are not duplicated.
- **freeze_check and deposit.py** have the same semantics as `plan_precedes` and `Ledger`.
- **Nestor's B2/B5 specs** map to the WriteLedger's writer/owner fields.
- **W2-B's certifier** feeds `certify_gate`; `map_w2b` names the corresponding check.
- **W2-C's classification vocabulary** is adopted verbatim in the operator suite. I coordinated with W2-B and W2-C by reading their directories only.

## 1. Findings

**F1 [V] Every primitive reproduces at least one real PTE failure.**
- Evidence: the 20-row table in API.md s4, all asserted in tests.
- Real-data sources: the real engine (P1, P4), real C1 rows (P4, P7), real git (P7), the real W-Z pair arrays and row table (P4, P8, P9), and real H-PLANT outputs (P6).
- Confidence: high.
- Objection: the toy fixtures are structural analogues, not PTE.
- Unresolved: (3) difference-vs-use has a toy reproduction only. The W-Y Kp[0] case sits on a dense champion I did not run.

**F2 [V] explib's reach certificate reproduces H-INST's four hold_latch verdicts exactly on the real engine.**
- The four verdicts are REACHED / ABSORBED / NOT_REACHED / UNAPPLIED, with closure PASS.
- It also certifies NOT_REACHED where `lens.applied_ticks` is > 0 and `verify_reach` says NOT_VERIFIED.
- Check: tests/test_pte_adapter.py::test_P1.
- Confidence: high.
- Objection: one plant, one trial.
- Unresolved: cost on dense champions.

**F3 [V] zero_comm is FORCED, on the real engine and in the real rows.**
- On the engine, relay_flood (c1b_da_physics, RELAY d=1, 16 worlds):
  - normal accuracy is > .9;
  - zero_comm accuracy is exactly .5, and readouts are identical within every mirror pair while targets are negated (the A3 mirror identity fails).
- Negative control: hold_latch on HOLD under zero_comm scores 1.0, with no identity.
- C1 rows: zero_comm is exactly .5 in 213/213 RELAY, 174/174 MAJ and 95/95 XOR rows, so the audit says FORCED. In HOLD it spans .49-1.0, so the "not constant" check passes.
- Check: test_P4 (both tests).
- Confidence: high.
- Objection: the audit says nothing about which replacement control is valid.

**F4 [V] NEW: the site_all + channel_all swap identity, and double-counting in W-Z/AUDIT3.**
- In real W-Z pair arrays, s(site_all) + s(channel_all) equals the maximum (4) at every (pair, trial):
  - in 93/93 RELAY and MAJ groups swapped at offset >= 1;
  - in 0/13 groups at offset <= 0, while the cue is still arriving.
- HOLD: it holds at offsets 5, 8 and 9 (8 groups) and fails at offsets 0, 4, 6 and 10 (8 groups).
- Consequence: at offset >= 1, z(channel_all) = -z(site_all) exactly. These are ONE measurement, not two (W-M's identity, now exact in real data). Among AUDIT3's 22 inconsistent rows, at least groups 16fe8d4b, fb9a22da, 16fbc4ad and 59b89e9d list mirrored site_all and channel_all rows (their |z| values are equal).
- Check: test_P4_site_plus_channel... and the inline census script whose output is quoted in this session.
- Confidence: high on the identity; the HOLD pattern is unresolved (I suspect even-offset phase or post-swap teacher/distractor inputs).
- Objection: W-Z's class logic may already treat the two arms as one. I did not audit the class logic.

**F5 [V] NEW: H-INST B4's proposed replication guard cannot fire on certificates.**
- B4's rule: a verdict within one CI half-width of a bar needs 2 namespaces.
- A one-sided certificate's interval excludes the bar, so its margin is always > 1 half-width. On real AUDIT3 data the rule catches 0 of 20 certified seed flips.
- The predictive replication probability (P(replicate certifies) < .95) catches:
  - 14/20 at inflation 1;
  - 20/20 at inflation 2, at a cost of flagging 52/256 stable rows.
- Check: test_stats::test_single_draw_certificates_near_threshold_W_Z, and the swap_rel H2 version in the adapter test.
- Confidence: high on B4's impossibility; medium on the threshold choice.

**F6 [V calculation, I interpretation] The pair-bootstrap intervals under-predict variation between namespaces.**
- Under pair independence, the expected number of label flips among the 276 certified W-Z rows is 8.3 (sum of 1 - P_rep). 20 were observed, 2.4 times as many.
- At group level, 4.6 were expected and 8 observed.
- An SE inflation of about 2 reproduces both numbers.
- Confidence: medium.
- Objection: the W-U labels come from REL3's non-strict column, and the model assumes a normal replicate shift. Interval method cannot be the cause, though: the harvest census found H2 = REL3 on all 439 real group-arms.
- Unresolved: a direct replicate-seed estimate of the inflation.

**F7 [V] Independent re-derivation of all 301 W-Z certificates.**
- Recomputing swap_rel H2 certificates from W-Z's saved pair arrays, using the pair statistic = trial-mean count / 4, reproduces all 301 DETERMINED-row certificates with 0 mismatches.
- Check: adapter test.
- Useful to W2-G.

**F8 [V] AUDIT3's 22 inconsistent rows are 10 independent units.**
- The 22 rows fall in 10 specimen x offset groups, so `count_check` fails: 22 claimed vs 10 units.
- Check: test_stats.

**F9 [V] Gate attainability: the one-flag XOR readout and the P3 ring rows.**
- One-flag XOR: H-PLANT's real "+ iff P" readout scores .237 [.221, .252]. Its negation has lo99 .748 > .55, so the gate is FLAGGED by the adversary check.
- P3 eligibility from the light-cone census (bound > .55):
  - XOR ring 2/19 eligible;
  - global 81/81;
  - torus 83/87;
  - smallworld 10/18;
  - random 7/13.
- Check: test_attainable.
- Caution [I]: my toy twin gate uses .80, above the .75 that any non-XOR 2-input rule reaches on uniform inputs. The real environment gives .763 > .75, so its inputs are not uniform. A real twin threshold must come from a real adversary panel, not the toy bound.

**F10 [V] Provenance checks on real history.**
- `plan_precedes` reproduces freeze_check's known answers: REL4 PASS (017259a48), W-O FAIL (93e2e544b = 93e2e544b).
- `support_check` refuses fac4aaa23 (kind transfer) as evidence for a search NULL.
- Check: test_provenance.

**F11 [I] H-PLANT's must-fail gate MF-XOR-a may pass by construction.**
- MF-XOR-a zeroes sensor 2. It reads exactly .500 in every one of the 128 pairs (M=256, xor_mf.json).
- That is the signature of a design identity, so as a must-fail gate it may be satisfiable whatever the program does.
- Confidence: low-medium; the raw outputs were not stored.
- Next: run mirror_identity on the raw outputs.

**F12 [V] The fail-closed guards caught two bugs in my own code during development.**
- The runner first read readouts after interventions; reach returned INCONSISTENT on a post-readout flip.
- `_boot_arm_stat` first used row counts in place of arm counts; the Simpson known-answer test failed.
- Both are fixed before any result was read. This is evidence that the guards fire.

## 2. Proposed fixes

- **No code fixes to existing or frozen code.** The library is purely additive, so there are no diff files.
- **Proposals (NEUTRAL, additive):**
  - Adopt explib per the API.md s5 promotion path.
  - Replace H-INST B4's rule with the predictive rule (F5).
  - Report the reach certificate next to verify_reach in new preregistrations.
  - Exclude zero_comm as COMM evidence in comm families, with a BX-7 transition table. This is SEMANTIC for any future report; it is not a retro-edit.

## 3. Disagreements

- **D1 (H-INST B4):** the half-width rule is a guard that cannot fire on issued certificates (F5).
- **D2 (H-INST B2):** a cross-specimen "shuffle_pairs" null cannot detect within-specimen design identities. z_site = -z_chan holds within each group, but |z| differs across groups, so a cross-group shuffle breaks the relation and it would read INFORMATIVE. Specimen-level null SETS under the same design are required. [I, reasoning plus W-Z data.]
- **D3 (W-Z REPORT):** "seed sensitivity, not an instrument defect" is only part of it. The intervals are about 2 times too narrow between namespaces (F6), which supports T_SWAP_REL4's strongest alternative.
- **D4 (W-Z / AUDIT3 counting):** at offset >= 1, site_all and channel_all are one measurement (F4). Counting both as rows double-counts.
- **D5 (three freeze-rule implementations):** Harmonia's `freeze_precedes` does not check that the plan blob is unchanged, while `tools/freeze_check.py` does. A plan edited after its results can PASS Harmonia's check and FAIL Ananke's. [V, code reading.] One implementation should exist.
- **D6 (PTE_INSTRUMENT_GAPS rank 1):** I agree zero_comm must be replaced. Any replacement must first pass identity-audit A4 with a declared witness. The proposed "actuator not a neighbour" variant changes the task, so it needs its own transition table.

## 4. Next questions (ranked)

1. Replicate-seed run (AUDIT3 A3b) on 10 flip and 10 stable groups to estimate the inflation directly. Prediction: f ≈ 2. This decides how many intermediate-z carrier claims survive.
2. Why does the site + channel identity fail at HOLD offsets 0, 4, 6 and 10 but hold at 5, 8 and 9? Zero compute: inspect the post-swap HOLD inputs and the update phase.
3. Is H-PLANT's MF-XOR-a pinned by the mirror identity? One cheap run with raw outputs.
4. BX-7 transition table: which C1 COMM_DEPENDENT / CAUSAL_SUPPORT verdicts change when zero_comm is excluded?
5. Do any W-O, W-Z or W-U group classes count site_all and channel_all as two corroborating observations at offset >= 1? Re-tabulate with one arm dropped.
6. A toolbox adapter: can worlds with `ext.snapshot.v1` and BIT replay provide lockstep common random numbers for reach certificates in Worlds-Kernel experiments?
7. Reach over multi-node readouts (MAJ actuator sets).
8. Unify the freeze rule (D5).

## 5. Inference ledger

```
W2F-1 shared lib design | repo search (toolbox, Harmonia AP, H-INST, freeze_check, deposit, Nestor B1-B8, W2-B/W2-C) | explib 9 primitives + PTE adapter, 40 tests pass, core engine-free | high | toy fixtures are analogues | dense-champion cost | promote per API.md s5
W2F-2 reach generalisation | test_P1 vs H-INST reach_certificate | 4/4 verdicts identical, closure PASS | high | one plant/trial | multi-node readouts | PTE adoption beside verify_reach
W2F-3 zero_comm competence | engine run + 482 C1 comm rows | FORCED (mirror identity, constant .5); HOLD competent | high | says nothing about the replacement | transition table | BX-7 table
W2F-4 site+chan identity in real data | W-Z pairs, 106 RELAY/MAJ groups | exact at offset>=1 (93/93), absent at <=0 (13/13); HOLD mixed | high (RELAY/MAJ) | W-Z class logic may already merge arms | HOLD pattern | Q2, Q5
W2F-5 B4 replication guard | W-Z certified rows, H2 intervals | B4 catches 0/20; predictive rule 14/20 (f1), 20/20 (f2) | high / medium | normal-shift model | inflation value | Q1
W2F-6 interval coverage between namespaces | expected vs observed flips | 8.3 vs 20 rows, 4.6 vs 8 groups, f~2 | medium | W-U label source | direct estimate | Q1
W2F-7 W-Z re-derivation | swap_rel on saved pairs | 301/301 certificates reproduced | high | none | none | hand to W2-G
W2F-8 attainability of XOR SIGNAL | H-PLANT xor_mf + lc_census | gate gameable (.748); ring 2/19 eligible | high | toy .75 bound not valid on the real env | real adversary panel | W2-B certifier
W2F-9 provenance known answers | git + C1 rows | REL4 PASS, W-O FAIL, fac4aaa23 refused | high | none | freeze-rule divergence | D5
W2F-10 MF-XOR-a forced? | xor_mf pairs all .500 | suspected identity | low-medium | no raw outputs | raw outputs | Q3
```

## 6. Compute used

- CPU only, CUDA_VISIBLE_DEVICES=-1, at most 2 threads.
- Pytest runs and short census scripts, each under 2 minutes of wall time, about 0.05 core-hours in total.
- No GPU, no leases, no git writes.

Hygiene: two `__pycache__` directories, W2-F/explib/ and W2-F/tests/, were created by early runs made without PYTHONDONTWRITEBYTECODE. My `rm` was denied by the permission system, so the principal may delete them. I found no files of mine outside W2-F, and git status shows no tracked changes.
