<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-AB; sha256(report)=20997f7ab8810c1f; delimited; see REPORT.provenance.json -->
W2-AB REPORT: PTE-C2 design memo, prereg-ready DRAFT (Opus worker W2-AB, Ananke Wave 2)
Directory: roles/Ananke/research/harvest/wave2/W2-AB/

Files:
- PREREG_PTE_C2_DRAFT.md: the deliverable. DRAFT, NOT FROZEN, NOT AUTHORIZED.
- design_numbers.py and design_numbers2.py, with their .json outputs: all the design arithmetic (statistics and compute). No engine, no torch.
- patch/inference_keep_f.NEUTRAL.diff, scratch/orig and scratch/patched copies of inference.py, and tests/test_keep_prob_f.py.

Custody: nothing was edited outside W2-AB. No git writes. CPU only, 2 threads. No search was run and nothing was frozen.

## 0. Summary of the C2 design

**Question.** At admitted cells, is the C1 search limited by search (S), by selection (U), or by neither? If it is S, does it respond to search-side changes (W2-D's F-S)? A cell is admitted only if all of these hold:
- link P is excluded: the joint ceiling is at least A90(gate) + .05;
- link R is excluded: a certified plant exists inside the C2 genome space (prog_len 16, rules 1, economy off);
- link V is excluded: the family ruler is SOUND for the property claimed;
- placement is corrected and the actuator is reachable.

**Families.**
- Core: RELAY multi-hop, FLIP, MAJ one-hop. XOR only if XOR_SYM gets a power certificate before freeze.
- Positive controls: RELAY one-hop and HOLD (with jittered distractors).
- Each core family has 4 admitted cells. At least 2 of the 4 are random draws from the admitted pool and were never searched by C1. The verdict must also hold on those fresh cells alone.

**Arms per core cell.** Search seeds are paired by index across arms.
- BASE: the C1 protocol, 12 seeds.
- W0: shaping terms switched off.
- M32: 32 training worlds instead of 8.
- B4X: 4x the generations.
- PSEED: the plant injected at generation 0.
- KSEED: the plant mutated at k = 1, 2 or 4 fields.
- STEP: a stepping-stone program injected (for example RELAY_LATCH for FLIP).

**Rulers and controls.**
- FLIP uses the B certificate: mean of same-cue and changed-cue accuracy, lo99 > .75.
- XOR uses XOR_SYM.
- MAJ uses INTEGRATION plus a paired comparison against single-sensor transport (DICT).
- RELAY reach uses REACH_BEYOND_HOP_NEAREST plus a native 2-hop check.
- zero_comm, env_permutation, max_loss and shuffle_dest-on-global are retired as evidence. They are replaced by a packet ablation over the corrected window [cue onset, readout] inclusive. Its cut is relative and competence-gated, it must pass the identity audit, and its designated mutants must be killed by self-alarm.

**Statistics.**
- BOOTT intervals; held set of 64 mirror pairs.
- Every reading goes through reading3 with a 2.605 SE margin: keep = Phi(d/(sqrt2·f)) at f = 1.12 and keep .95.
- The search seed is the unit. BH q = .05 over the declared contrasts.
- Specimens are the cluster unit; duplicate measurements are removed.
- Burden symmetry: "no response" is claimed only if the upper 95% bound on the difference is below .25.

**Verdicts.**
- Per cell: S-LOCATED needs at most 1/12 BASE successes and the plant retained in 4/4 PSEED runs. SEARCH-SUCCEEDS needs at least 6/12.
- Per family: H6-S is true if at least 3 of 4 cells are S-LOCATED.
- The memo also contains: the compute table per arm; a risk statement for each of 11 predictions, giving what is attainable under each outcome; and 12 conditions that would make C2 uninformative.

## 1. Findings

**F1 [V] The C2 replication gate cannot be expressed in the current code.**
- `prometheus/ananke/inference.py` keep_prob, margin_for_keep and replication_gate have no f argument. W2-N's gate (f = 1.12) is therefore not implementable as written.
- Check: `python -m pytest -q -p no:cacheprovider tests/test_keep_prob_f.py`. Current code: 3 failed, 2 passed. Patched copy (`W2AB_INF=scratch/patched/inference.py`): 5 passed. `git apply --check` passes.
- With the default f = 1, every value equals the current function (tested).
- Confidence: high.
- Objection: callers can divide d by f themselves. True, but then the margin lives only in caller code, which is the "assumption encoded only in code" pattern.

**F2 [V] The "multi-hop-only task distribution" test is not a new experiment in its per-search form.**
- `search.evolve(ph, env, ...)` trains each GA on one physics and one env (search.py:81-90).
- Each of C1's 30 light-cone-reachable multi-hop RELAY rows was therefore a GA trained only on its multi-hop task. 2/30 became competent, 2/9 where a plant works (P-1b).
- The "77% one-hop" figure describes the population of cells, which no single GA ever sees.
- Confidence: high.
- Objection: P-1 may have meant a mixed curriculum. That is covered by the STEP arm (seeded with a one-hop law).

**F3 [V] At n = 8, per-cell arm contrasts are underpowered.**
- One-sided Fisher power at n = 8 per arm: 0→.5 gives .64; .1→.5 gives .34 (design_numbers.json).
- Family-level pooling (BASE 48 vs arm 32) gives .77 for .05→.25 and .81 for .10→.35.
- Consequences: BASE uses n = 12, and response claims are made at family level only.
- Cell-rule error at n = 12: a true rate of .10 is classed S-LOCATED with probability .66, a true rate of .30 is classed SEARCH-SUCCEEDS with probability .12, and .50 with probability .61.
- Confidence: high.

**F4 [I] Compute.**
- Full core design (12 cells): 1,392 units = 14.3-23.2 GPU-hours at 37-60 s per C1-scale search. Decisive tier: 9.4-15.2. With 4 XOR cells: 18.7-30.4 (full) and 12.2-19.7 (decisive).
- On CPU this is 464-1,856 core-hours, which is not feasible.
- Confidence: medium.
- Objection: the M32 and B4X arms (4 units each) assume cost is linear in M and in generations, and batched GPU evaluation may be sublinear. Measure at the pilot.

**F5 [I] Selector ceiling at M = 32 is about .525-.54.**
- This scales W2-D F7's .55-.58 at M = 8 by the square root of 8/M.
- Confidence: low-medium. It assumes the ceiling's noise term dominates; mostly-deaf populations break that assumption.

## 2. Proposed fixes

- NEUTRAL: `patch/inference_keep_f.NEUTRAL.diff`, test `tests/test_keep_prob_f.py`. Adds f (default 1) to keep_prob, margin_for_keep and replication_gate.
- SEMANTIC for C2 only (fixes the memo depends on; none is mine):
  - MAJ inward placement (W2-I / W2-A1);
  - XOR actuator reachable from both sensors (W2-A1);
  - causal_label competence precondition (W2-C);
  - G12 judges the normal arm only (W2-O);
  - transplant matched normal (W2-E).

## 3. Disagreements

1. **P-1 v3 (iii) and the handoff's "multi-hop-only distribution" as a distinguishing test.** Already tested per search (F2).
2. **W2-D s5, "≥ 3 cells each with ≥ 3 failed searches" for a family-level H6.** 0/3 has a CP95 upper bound of .71, which is too weak. C2 needs n_BASE = 12 (0/12 gives ≤ .265).
3. **W2-P admission at .614 (the 50%-power level).** Too lax: a cell sitting at 50% power is a coin flip. C2 uses A90 + .05.
4. **W2-K's component margin of 2.33 SE (f = 1).** For C2, use 2.605 SE (the f = 1.12 robustness bound, W2-N). Certificates use 3.69 SE.
5. **W2-K "n ≥ 8".** That is a floor for rate confidence intervals, not for comparing arms (F3).
6. **W2-L FLIP_CHANGE and W2-B FLIP_FEEDBACK as C2 rulers.** Replaced by the B certificate (agrees with W2-S).
7. **W2-B's actuator-isolation control.** Not adopted, because it changes the task (agrees with W2-F D6).

## 4. Next questions (ranked)

1. Run the admission census now on CPU: ceilings plus at least 2 plant designs on about 200 candidates per family. This gives the per-family eligibility counts that decide whether C2 has 3 or 4 core families. About 3-5 core-hours, no search.
2. XOR_SYM power and size at the admitted XOR physics, against the 14 non-parity readouts. This decides whether XOR enters C2.
3. A 16-line decay-robust FLIP plant (W2-L Q2). If none exists, FLIP is restricted to decay 0, or the prog_len 24 fallback is triggered.
4. The pilot known-answer gate for the seeded-GA harness on one disjoint cell. It is a search and needs authorization.
5. Does GPU batch cost scale linearly with M and with generations? This re-prices the M32 and B4X arms.
6. A ≤ 16-line FLIP clock cheat, or an anti-copy mixture with B > .75 at the admitted FLIP physics. Either would make the B certificate CHEATABLE there.
7. Unify the freeze rule (Harmonia's freeze_precedes vs tools/freeze_check.py, W2-F D5) before the C2 freeze.

## 5. Inference ledger

question | evidence | result | confidence | strongest objection | unresolved | next
- Most decisive C2 question? | P-1 v3, W2-T (11% plant-backed), W2-D chain | H6 at admitted cells; w=0, M-sweep and multi-hop folded in as arms | med-high | depends on the eligibility counts | per-family N admitted | Q1
- Is multi-hop-only a new test? | search.py:81-90; P-1b 2/30 | no, per search | high | curriculum meaning | — | STEP arm
- Is the C2 gate implementable? | inference.py; test 3F/2P vs 5P | needs f; patch provided | high | callers could scale d themselves | — | apply patch
- Seed counts and power? | design_numbers*.json | BASE 12; family pooling; .77-.81 power | high | binomial model, no seed clustering | — | —
- Compute? | C1 37 s/search; W2-K and W2-D CPU timings | 9-15 GPU-h decisive tier; 14-23 full | medium | M scaling | — | Q5
- Uninformative conditions? | DEFECT_PATTERNS 1-7; W2-O/T | 12 listed, including asymmetric censoring and anchor dependence | med-high | — | — | —

## 6. Compute

About 0.02 core-hours: two scipy scripts and two pytest runs, each under 1 minute. CPU only, 2 threads, no engine runs, no GPU, no leases.
