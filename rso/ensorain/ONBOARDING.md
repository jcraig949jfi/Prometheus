# Ensorain onboarding record (C-016-T030; directive s8)

Argus[harry1-293acef8], claude-opus-5-5 (Q2), harry1, 2026-10-11. Engineering measurements for the second native
runtime. They are compared with C-010 (Ares) without normalising away the difference in difficulty.

## 1. Bespoke adapter lines

| File | Physical lines | Code lines (no comments, docstrings, blanks) | What it is |
|---|---|---|---|
| subjects.py | 139 | 86 | seed partition + conflict check, constructed controls (Smugglers, memoryless, constant), genome JSON, the subject search wrapper |
| assay.py | 206 | 156 | life -> integer row; observers; external declared-memory check; recompute check; preflight; CLI with the confirm refusal |
| analysis.py | 138 | 93 | exact sign test, G_PRE / G_R5 gates, Holm families, verdicts, exact power |
| freeze.py | 65 | 46 | LF-sha256 manifest + version set |
| **adapter total** | **548** | **381** | aspiration ~500; no control dropped to meet it |
| tests/test_assay.py | 145 | | 19 unittest cases (harry1 has no pytest) |

Counted at the freeze commit (`wc -l`; code lines by Python's tokenizer, docstrings and comments excluded).

C-010 (Ares W15) for comparison: rso/witness run_witness.py 458 + evaluate.py 480 + ares_client.py 403 +
make_configs.py 83 + dry_run.py 94 = 1,518 lines, plus ruler.py 257. Most of the difference is physics and interface,
not maturity. Ares runs as an external process: it needed a client, configs, an interrupt protocol and custody of
process output. Ensorain is importable Python with a pure `lifetime()` call, so one function call is one evidence
unit. The part that IS maturity: the exact tails and thresholds, Holm, canonical rows and LF hashing were imported,
not rewritten (s2).

## 2. Shared components (rso/registry, `python -m rso.registry.registry for-adapter`)

| Entry | Use here | Reused / modified / too narrow |
|---|---|---|
| receipt-canonical (rso/slice001/receipt.py:116-144) | `sha256_hex(rows)` over all rows (assay.py:rows_sha256) | REUSED unmodified. Its float refusal forced the integer endpoint, which is the right design here |
| ruler-binary-retention (rso/witness/ruler.py: `tail_ge`, `thresholds`) | exact one-sided sign test; integer k_pos for G_PRE and G_R5 | REUSED unmodified, INSIDE scope only because the unit is the lifetime (binary per unit, chance 1/2). TOO NARROW as named: the entry says "retention" and "per-episode"; here it is a generic exact binomial ruler on independent units. Proposed scope text: "exact binomial thresholds for any binary outcome on independent units with a known chance bound" |
| stratified-holm-analysis (rso/reach/stats.py:holm) | Holm within families P and S | REUSED: the `holm` function only. `analyze.py` NOT reused (it trusts the runner's `discovery` field, and its stratified Fisher contrast is unpaired) |
| exec-binding | not used | NOT NEEDED at this step: the confirmatory run is one process, one inventory row per life, and no parent/child run tree exists to bind. It will be needed if the run moves to Fabric or the session-independent runner |
| custody-keeper | not used | Not used in T030. The freeze is a manifest (FROZEN.json) plus the Git commit. Custody registration of the confirmatory output belongs to the run packet |
| mutation-runner | not used by the builder | For Pallas's Q3 challenge of the frozen surface |
| budget-ledger | not used | Cost is minutes of CPU (PREREGISTRATION.md s9). A ledger row would be ceremony |
| witness-driver-ares | pattern only | Pattern reused: recompute-from-bytes (here: recompute the native accuracies from observed episodes and actions), controls as their own subjects, refusal before launch on a hash mismatch |
| registry `file_sha` (rso/registry/registry.py:27) | LF-normalised hashes for FROZEN.json | REUSED. It is not a registry entry itself |

Modified shared components: **none**. No file outside rso/ensorain/ was edited.

Registry rows to add when the coordinator integrates. This packet does not edit rso/registry/, which Palamedes owns:
- `users` += "Ensorain C-016 (rso/ensorain/)" on receipt-canonical, ruler-binary-retention and
  stratified-holm-analysis (holm only).
- ruler-binary-retention `qualified_scope`: the generic exact-binomial reading above, and a counterexample. Applied
  per EPISODE in a plastic learner, it would be wrong, because episodes share the plastic parameter
  (COMPATIBILITY.md s8). Applied per LIFETIME, it is right.
- A candidate new entry, `ensorain-declared-memory-check` (assay.py:memory_check). Scope: TAPE genomes. A genome may
  change only at declared plastic keys inside PLASTIC_BOUND, and the working state is zero at block start. Not for:
  E0/E1 memory objects (ensorain/e0/memories.py:30 `audit` is their native check). Stage: AUTHOR_TESTED.

## 3. Native semantic mismatches (assumptions the Observatory carried that Ensorain broke)

1. **"The interesting state survives an interrupt."** Ares carried activation and plastic weights across a
   checkpoint. In Ensorain, activation never crosses a block, plastic parameters cross every block, and the boundary
   is a world event, not an interrupt. No mid-life resume exists. The "restart" control became a NEW life from
   learned parameters, named so.
2. **"Retention" as the phenomenon.** Family C demands REVISION. The question was reworded, and retention across a
   drift boundary is recorded as not demanded by any tested Ensorain world.
3. **"Episodes are independent units."** They are not, inside a plastic life. The unit is the lifetime.
4. **"The native certificate is a usable endpoint."** It is not: SWITCH_TRACKED does not separate the reference from
   history-shuffle at n = 40. It was replaced by integer counts.
5. **"A good score on the post-change window means the change was tracked."** It does not. Both Smuggler analogues
   score 1.0 on the coordinator's late-window endpoint. Only the pre-switch admissibility gate (G_PRE) separates
   them. This is the main instrument lesson of this onboarding: an endpoint defined on the post-change window alone
   rewards a fixed prior about the change.
6. **"The null ladder is a scalar competitor."** In family C, N1-N4 collapse to a four-policy memoryless class
   (+s, -s, +1, -1). Their pooled role-1 scalar depends on the pre/post mixture of the test sample (.542 on T020's
   seed, .392 for N1 and .608 for N4 on ours). The class was run as explicit control genomes instead.
7. **"ws_reset is the state control."** It is vacuous for family C. plast_frozen and history_shuffle are the state
   controls.
8. **Results are host-bitwise.** All arms run in one process; the runner refuses another Python or numpy version.
9. **Seed namespaces leak.** search.py derives certify seeds as 7_000_000 + run seed, so Ensorain's registered seeds
   reach into 16_5xx_xxx and 16_7xx_xxx. A partition check now runs as a test.
10. **"A searched plastic-arm elite is plastic."** 5 of 8 new elites set eta, sigma > 0 with no plastic parameter.
    Gene-level plasticity flags are not plasticity; the instrument reads `plastic_keys`.

## 4. Time, CPU, memory, interventions

| Measurement | Value |
|---|---|
| Session start (boot, harry1) | 2026-10-11 ~10:17Z |
| Claim pushed | 10:24:27Z (6451b6add) |
| Time to first native execution | 10:25:13Z, about 1 min after the claim: Cadmus's demand re-run, byte-identical to the committed result |
| RED observed | 10:29:53Z |
| First adapter-driven native lives (dev, n = 40) | 10:33:45Z, about 9 min after the claim |
| Subject search (8 x 16,000 evals, 2 processes) | 10:35:50Z..10:42:41Z, 805 CPU-s (0.22 core-h) |
| Development qualification, N = 400 | 10:45:25Z (65 s wall, one process) |
| Frozen | see FREEZE.md |
| Time to qualified result | not reached in this packet (Q3 challenge, then the confirmatory run) |
| CPU, whole packet | about 0.3 core-h |
| Peak memory, assay | 47 MB working set at N = 100 |
| Q3 reviewer time | to be recorded by the challenge packet |
| Operator interventions | 0 |
| Requests to Ensorain | 0. Nothing here needed Ensorain to change its code. ensorain/ was imported read-only; its interfaces sufficed with two observers attached from outside |

## 5. The repair round (C-016-T041; directive s9 steps 6-7)

Argus[harry1-b2f16d20], claude-opus-5-5 (Q2), harry1, 2026-10-11. One bounded round after Pallas's Q3 challenge
(C-016-T040, challenge/REPORT.md: INFERENCE, INSTRUMENT, INTERPRETATION all NOT CLOSED, nothing blocking).

| Measurement | Value |
|---|---|
| Boot / claim pushed | 12:23Z / 12:24:17Z (fefc83a4f) |
| First prototype of the new endpoint on dev lives (8 subjects x 100) | ~12:29Z, 26 s |
| Code committed (6fff93af9) | 12:38:14Z |
| RED rows (11 mutants + baseline) | 12:38:36Z..12:40:26Z |
| Amendment committed (030f1746f) | 12:43:14Z |
| Re-frozen | this commit (see FREEZE.md v1.1.0) |
| CPU | DEV_CHECK 255 s (30,800 lives), RED runner ~2 min, suite 9-11 s; well under 0.2 core-h |
| Lines changed in the frozen adapter | analysis.py +92/-23 (now 207 lines), assay.py +55/-14 (247), freeze.py +7/-3 (69); subjects.py unchanged |
| New repair code | repair_v110/dev_check.py 67, run_red.py 86; tests/test_repair_v110.py 154 (14 tests) |
| Shared components modified | none. ruler.thresholds used with a bound of 9/10 (G_R5), outside its W15 calibration but inside its stated function |
| Operator interventions | 0. Requests to Ensorain: 0 |

What the challenge taught (the reusable lessons, for the registry and the next adapter):

1. **A contrast against the subject's OWN frozen configuration is a statement about its innate value.** For a
   plastic parameter that starts on the pre-switch side, "frozen" scores 0 after the switch and any noise beats it;
   on the post-switch side "frozen" IS the Smuggler and cannot be beaten. The repair is an endpoint no fixed sign can
   satisfy (both halves of the life) plus a comparator that keeps the perturbation and removes only the update (the
   noise arm). Lesson for every engine with stochastic exploration: freezing must not remove noise and learning
   together.
2. **Every registered control was deterministic, so the noise class was invisible to qualification.** A
   qualification set needs one stochastic non-learner (here jitter, Q-d) and one positive that the original rule
   gets WRONG (learns_pre, Q-e) -- a control the rule passes trivially qualifies nothing.
3. **Hash guards are not behavioural pins.** Five of six challenge edits survived the frozen suite; only the freeze
   hash refused them. Every decision-rule line now has a behavioural test that turns RED on its mutant
   (repair_v110/red_rows.jsonl). Keeping the challenge's find strings byte-identical in the repaired code let the
   mutants be applied verbatim, which is the cheap way to make a repair round checkable.
4. **A gate threshold borrowed from a chance test has no meaning as a competence claim** (G_R5). State the bound the
   claim needs (9 lives in 10) and test against it.
5. **Declare test families from structure before the run.** 5 of 8 searched elites cannot be revisers by
   construction; testing them costs power and inflates "search accessibility". The family is now read from the
   genome (family_s), and the rest are reported, not tested.
6. Tooling note: the RED runner's failure-name parser repeats the method name (Python 3.12 unittest prints
   "FAIL: name (module.Class.name)"); the rows are correct, the field is cosmetic.

Registry rows to add when the coordinator integrates (rso/registry is Palamedes's): mutation-runner `users` +=
"C-016-T041 RED rows (rso/ensorain/repair_v110/run_red.py, unittest variant)"; ruler-binary-retention: used with a
non-1/2 bound (9/10) for G_R5; the candidate `ensorain-declared-memory-check` now refuses non-finite values (P1).

## 6. Onboarding cost against Ares (C-016-T060; directive s8; Palamedes, coordinator)

Measured from packet histories, receipts, git and the integrator's reproduction. Difficulty is NOT normalised away:
the two experiments ask different questions of different physics.

| Measurement (s8) | C-010 Ares (retained bit across an interrupt) | C-016 Ensorain (revision at a law switch) |
|---|---|---|
| Adapter implementation lines | 1,518 driver/evaluator/client/configs + 257 ruler | 662 physical / 480 code (subjects 139, assay 247, analysis 207, freeze 69); + repair tooling 153 (repair_v110) |
| Shared components reused | binding, custody, receipts, ledger (built for it in C-009 / C-004) | 4, unmodified: receipt-canonical, ruler thresholds / tail, Holm, registry file_sha |
| Shared components modified | n/a (first native engine) | 0 |
| Time to first native execution | ~1 h after open (adapter build) | 7 min after open (T020's demand re-run, 10:14Z) |
| Time to qualified result | 6.2 h open -> close | 3 h 58 min open (10:07Z) -> confirmatory RESULT (14:05Z); ~4.5 h to integration |
| Q3 reviewer time | ~1.7 h (W1 + W2) | ~1.6 h (T040 ~45-60 min, T042 ~50 min, boot included) |
| Independent challenges / defects found | 2 / 2 | 2 / 2 (T040: self-relative contrast, 5 unpinned rule lines; T042: drift passes K1-only labels, dead plastic code in family S) |
| Repair rounds | 1 | 1 (v1.1.0), plus recorded limitations L1-L5 |
| CPU | 26.2 CPU-min ledgered | ~0.9 core-h (receipts: T030 0.3, T040 0.07, T041 0.15, T042 0.17, T050 0.08; integrator re-runs ~0.15). The confirmatory run itself: ~265 CPU-s |
| Memory | not recorded | 66 MB peak (confirmatory run) |
| Operator interventions | 0 gates | 0 gates after the directive; 0 requests to Ensorain |
| Coordination waiting share | 69% | 49% (median wait to claim 3.8 min, to integrate 8.8 min; C-013 integrate 31 min) |
| Native semantic mismatches | (the Ares semantics were the baseline) | 9: s3 items 1-7 above, plus "a frozen contrast is innate-relative" (T040) and "declared plastic keys are not live plastic code" (T042) |

Reading:
- **Line count.** The bespoke line count fell from about 1,800 to about 660, near the operator's ~500 aspiration.
  Most of the fall is the interface: Ensorain is importable Python, so one call is one evidence unit, and the
  Ares-specific process client, configs and interrupt protocol vanish. The part that is maturity: exact tails,
  thresholds, Holm, canonical rows and LF hashing were imported unchanged, and no shared component needed editing.
- **No reduction in qualification.** Two challenges, two real defects, one repair round, as in C-010. The registry
  saved building, not proving.
- **The mismatches are the Observatory's lesson.** Ares-shaped assumptions failed on contact with Ensorain:
  - an interrupt as the boundary;
  - retention as the phenomenon;
  - episodes as independent units;
  - a frozen arm as the competitor.
  Each is now a scope limit or counterexample in rso/registry, so the next adapter inherits it.
