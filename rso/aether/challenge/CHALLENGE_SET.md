# C-018-T040 -- Q3 challenge set against FREEZE_AETHER_ANCESTRY_CONTENT v1.0.0 (committed BEFORE any outcome)

Pallas[harry1-d78f77ce], claude-fable-5-1 (Q3; runtime recorded at comms boot 2026-10-12T11:11Z, tier heavy; no harness
message has reported a different model at the time of this commit), headless on harry1 (M4), 2026-10-12. Surface:
rso/aether at FREEZE_AETHER_ANCESTRY_CONTENT v1.0.0 (FROZEN.json: 32 LF sha256, Python 3.12, design pin 0e9519bd;
freeze f1e65a8ff on argus/c018-t030; integrated on main 9e51c80b3 = this branch's base). `freeze check` OK before the
claim (cdea3c8bd on main). Authority: operator directive OBSERVATORY GENERATION 4 s9 (roles/Palamedes/prompts/
2026-10-12_generation4/01_OPERATOR_DIRECTIVE_verbatim.md); packet ops/campaigns/C-018/tasks/C-018-T040/TASK.json;
Palamedes's launch note (attacks named; the NO_CUT incidence question; <= 2 processes; python -B).

Rules: no production file changed in any commit; mutants (E1-E5) and the B6 pin forgery are applied to THIS worktree's
working copy only and restored byte for byte (sha256 + `git diff --quiet`), `freeze check` OK after each; Aether/ and
roles/Aether/ read-only (never edited, not even transiently); nothing run on M2; no confirmatory seed (k = 0x2000+i)
executed, no RELEASE.json written into the repo, `confirm run` never passed; burned block 0x1000..0x10FF untouched.
Seeds: Pallas's k = 0x3000 + i with the adapter's bases (natives.py docstring; disjoint from every registered range,
checked by set intersection and grep); labels 0x3100..0x31FF are names on forged copies, never executed.
Frame: every case tests a scientific instrument; the builder's implementation is not repaired here (directive s13).

## 1. Scoring

    case    AS_EXPECTED       the frozen machinery does what PREREGISTRATION v1.0.0 says and the prediction held
            SURVIVOR          a demonstrated gap between what the registered instrument / inference / evidence chain
                              CLAIMS and what the frozen machinery can SUPPORT (the predicted fault appeared)
            NOT_AS_PREDICTED  the prediction failed; reported with the observed value
            RECORDED          a probe with its prediction checked; bears on the interpretation, not on a verdict
    edit    RED               the frozen suite fails on the mutant (behaviour pinned)
            SURVIVES          the 33-test suite passes on the mutant; the witness shows the behaviour that moved
    surface CLOSED            no survivor whose bearing requires a narrowing, a limitation or a repair before the
                              confirmatory result is read; NOT CLOSED otherwise (with exactly what the result must state)

The mechanical check of each prediction is the `check` expression in expected.json (cases.py score); the narrative
verdict and the bearing are in REPORT.md. Surfaces: INSTRUMENT (recorder + classes), INFERENCE (band, disposition),
EVIDENCE CHAIN (completeness, binding, replay, pin, guard), INTERPRETATION (what the result text must say).

## 2. Attack map (directive s9 -> cases)

| Directive s9 attack | Cases |
|---|---|
| causal ancestry mistaken for information transmission | B3 (the reverse: content credited to a band where ancestry was shown by other units), N1 (first native readings of the three evaluable classes) |
| a decoder exploiting initial geometry | N1 (native null on 24 RX units), S3 (audit rows C4/C10, C7/C8 re-derived); the content branches are multi-site BY DESIGN and the t0 check does not apply to them: stated in REPORT, not a case |
| a negative control unable to pass (or fail) | B4 / B4n (late N: C3 cannot remove targets that diverged first), B2 (V1 arm cannot reach P2 if its trees are 1-2 generations), S3 (C1 cannot fail natively, conceded) |
| observations predictable from recipes alone | S3 (audit `reads_answer` is vacuous: no detector reads the scrubbed fields; fixture sites ARE the recipe, conceded in PREREG s4); native arms have no recipe beyond (law, seed) -- stated |
| the evaluator trusting derived producer fields | B1 (parent / gen / type of the tree), E2 (root check unpinned), S4 (replay compares the tree only because I added that comparison; the frozen replay compares arrays) |
| missing or altered evidence preserving a qualified result | S6, B5 (duplicates and a substituted first seed), B6 (pin read from a mutable file; analyse never runs the freeze check), E1 / E3 / E5 (the analyser's three guards are unpinned by the suite), P1 (refusal prints the verdict numbers) |
| results not surviving relevant counterfactual interventions | B7 (horizon), B8 (the instrument's own choice of N), S4 (clamp timing) |
| NO_CUT incidence: too few evaluable units, does the rule say so | B2, N1 |

## 3. Cases and predictions (expected.json is the answer key)

### Sound (verification of the builder's claims)

S1 FREEZE. `freeze check`; the 32 pins recomputed without freeze.py from the HEAD blobs and from disk (LF); the design
manifest sealed, equal to the pin, equal to `confirm.design_manifest()` from the code constants. PREDICTION: all hold.

S2 SUITE + RED. 33 tests OK; `run_red` into scratch reproduces 21/21 KILLED, identical rows. PREDICTION: identical.

S3 QUALIFY / AUDIT. `qualify verdict` and `controls` re-derive QUALIFICATION.json and FALSIFIABILITY_AUDIT.json from the
committed records (bytes backed up and restored). PREDICTION: identical as JSON; freeze check OK after.

S4 REPLAY + CLAMP TIMING. Dev RX k=0 and V1 k=0 replayed: arrays_sha256 and the tree equal. Fixture A (48^2, H 100):
clamping from B's / N's first divergence (PROP01, prop01_run.py:220) vs the recorder's clamp from tick 1 (adapter.py:80):
identical first-tick arrays and digests. PREDICTION: all equal.

S5 RUN GUARD. `confirm run RX.0` exit 2; with `--cleared-by not-a-release` exit 2; `release_problem` with a forged
RELEASE.json (scratch path, three fields, the pinned design) returns None. PREDICTION: 2, 2, None. RECORDED: the gate is
a process control (who may commit rso/aether/RELEASE.json), not a cryptographic one; nothing is executed.

S6 COMPLETENESS BASICS. On the frozen design with synthetic rows: missing -> INCOMPLETE; duplicate -> REFUSED
(DUPLICATE); foreign id -> REFUSED (UNEXPECTED); short shard -> COUNT_MISMATCH; stray seed -> SEED_PARTITION; source
change -> SOURCE_MISMATCH; re-sealed smaller design REFUSED when pinned and COMPLETE when not; early_stop null, so a
missing shard is never COMPLETE_EARLY_STOP. PREDICTION: as listed.

### Broken (constructions; synth.py, forge.py)

B1 TREE TAMPER. tree_check (evaluate.py:86-106) verifies the tree's `site` and `ftick` against the arrays and that the
recorded B / N equal the rules' output on the tree; it never looks at `parent`, `gen` or `type`, and the replay sample
(confirm.py:157-159) compares arrays_sha256 only. (i) dev RX k=0 (INSUFFICIENT, 1 target): re-parent three sites of the
interventional set I under B -> CONFIRMED, problems []. (ii) The same respecting every structural invariant a native tree
has (parent is a 4-neighbour, parent diverged earlier, gen = parent + 1; synth.tree_invariants: 0 violations on all six
dev trees) -> CONFIRMED, problems [], 0 violations. (iii) dev RX k=3 (NO_CUT; 21 generations; the only generation-2 child
is RULE-type, PREREG s5): flip that one `type` byte to CARRY, write the B / N the rules now give into the meta -> an
evaluable class read from clamp arrays that are all -1 because no clamp world was ever run (adapter.py:150-151): predicted
NONSPECIFIC (every target 'removed' by both clamps). PREDICTION: as stated. Bearing (EVIDENCE CHAIN): the trust boundary
(PREREG s7 'never from producer fields') is overstated for the attribution's structure; a replay that compared
meta["tree"] would close (i)-(iii) at no extra cost (S4 shows the replayed tree is equal); the structural invariants are a
cheap second line that closes (i) and (iii) but not (ii).

B2 NO_CUT HONESTY. disposition() (evaluate.py:177-194) and reach_band (:135-143) count `need = max(3, ceil(0.1 n))` over
ALL units, NO_CUT included, and have no status for a population with too few evaluable units. Synthetic rows through the
frozen law_summary + disposition with accuracy dictionaries supplied directly: (a) 48 NO_CUT with decodable content ->
CONTENT_WITHOUT_INTERVENTIONAL_ANCESTRY; (b) 44 NO_CUT + 4 CONFIRMED r_int 3 -> NEITHER; (c) 16 V1 all NO_CUT -> NEITHER;
(e) 43 NO_CUT + 5 CONFIRMED r_int 2 at chance -> CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT. PREDICTION: exactly
these strings. Bearing (INFERENCE / INTERPRETATION): 'NEITHER' and 'CONTENT_WITHOUT_INTERVENTIONAL_ANCESTRY' are
statements about ancestry that the rule can emit after zero clamp tests; with the dev incidence (5 of 6 NO_CUT) this is
the likely shape of the V1 arm and a possible shape of RX. The result must state the evaluable count beside the label, and
the rule should name the case (ANCESTRY_UNEVALUABLE below a preregistered minimum of evaluable units).

B3 RADIUS-ONLY CONDITIONING. conditioned_excess (evaluate.py:146-152) averages the held-out accuracy over EVERY seed at
radii 2..band; the band comes from the CONFIRMED units. 5 CONFIRMED units (r_int 2) whose own held-out accuracy is chance
+ 43 NO_CUT units at accuracy 1.0 -> ANCESTRY_WITH_CONTENT, while the excess over the CONFIRMED units' features is 0.0.
PREDICTION: as stated. Bearing (INTERPRETATION): the label reads as content carried by the demonstrated ancestry; the rule
only shows co-occurrence at the band level, possibly in disjoint units (Argus's own open question, ONBOARDING s6). The
result must report the conditioned excess restricted to CONFIRMED units beside the registered one.

B4 LATE N (synthetic, exact). CUT_N is identical to IMPULSE until N first diverges (adapter.py:66-90: the clamp of a site
equal to CONTROL is the identity), so a target that diverged BEFORE N cannot be removed by N; ancestry() (evaluate.py:67)
calls N vacuous only if it never diverged. Chain with targets at ticks 3-5 and N first divergent at tick 50 ->
CONFIRMED, removed_N 0.0, zero N-live targets. PREDICTION: as stated. Bearing (INSTRUMENT): C3 is live only for the
targets that diverge after N; removed_N should be computed over those (and the unit CONTROL_VACUOUS when there are none),
or the N rule should require ftick(N) <= min ftick(targets). B4n measures how often this bites natively.

### Natives (Pallas seeds; natives.py, altn.py; <= 2 processes; DEVELOPMENT-class observations, not a result)

N1 NATIVE CLASSES. 24 RX (k = 0x3000..0x3017) and 8 V1 (k = 0x3000..0x3007) through the frozen recorder and evaluator.
PREDICTION: 0 binding / tree problems; light cone 32/32; t0 identity 32/32; structural invariants 32/32; RX NO_CUT >= 8
of 24; >= 1 RX unit in CONFIRMED / NONSPECIFIC / NOT_INTERVENTIONAL (PREREG s9: none seen natively yet); the modal
evaluable RX class is NOT CONFIRMED (Cadmus's lead, SELECTION s5: deep attributed trees whose single clamp removes
little); V1 NO_CUT >= 6 of 8; |RX null excess| < 0.03. The 24-unit RX reading (classes, agreement, reach band, content
excess, disposition-if-complete) is reported as a DEV-class observation and is not the confirmatory answer.

B4n LATE N, natively. PREDICTION: >= 1 evaluable RX unit has >= 1 target with ftick <= ftick(N). Reported: the N-live
fraction per evaluable unit and removed_N over the live targets.

B7 HORIZON. On the stored arrays, divergences after H' are set to 'never' (recorder with H' = 100 / 200 / 300) and the
class re-read. PREDICTION: >= 1 evaluable RX unit changes class at H' = 200. RECORDED: 'never diverges in CUT_B' means
'not within 400 ticks' (dev RX k=0's only target first diverged at tick 349).

B8 ALTERNATIVE N. For up to 4 evaluable RX units: the warm snapshot recomputed (adapter.py:129-137), the second-ranked
non-ancestor candidate clamped instead of N, the class read with the frozen thresholds. PREDICTION: warm digest, snapshot
and impulse world replay equal; the class flips for at most 1 unit. RECORDED.

### Evidence chain (forge.py; the frozen confirm.analyse, only RUNS / DESIGN_PATH / pin pointed at a scratch set
### because the frozen design's seeds may not be executed here; stated per case when the replay is stubbed)

B5 DUPLICATED EVIDENCE. A 6-shard set in the frozen design's shape (4 x 12 RX, 2 x 8 V1) on Pallas seeds: each shard's
first row is a genuine unit, every other row a COPY of it with the seed label rewritten (arrays identical, meta re-saved);
RX.3's first row is a copy of RX 0x3002 under the label 0x3003 (the one row the replay sample looks at). PREDICTION:
completeness COMPLETE; 64 rows, 5 distinct arrays_sha256; the unit-file, binding and tree checks raise nothing on the
copies; exactly one problem, RX.3's replay; disposition REFUSED_RECORD_INCONSISTENT. Bearing (EVIDENCE CHAIN): at the
first analysis the design's digests are FILLED from what is presented (confirm.py:93-99), so the gate checks presence,
partition, count and the CURRENT source bytes, never provenance; provenance rests on 6 replays of 64 units; a duplicate
arrays_sha256 across rows is not checked (a one-line refusal would defeat copying); duplicated units also inflate the
reach count and leak test features into the decoder's training set.

P1 REFUSAL LEAK. From B5's output: the class counts and content excess are printed with the REFUSED_RECORD_INCONSISTENT
disposition. PREDICTION: yes. RECORDED (the stopping rule forbids an interim look; a refusal should not show the numbers).

B6 PIN FROM A MUTABLE FILE. analyse() (confirm.py:135-168) takes its only pin from FROZEN.json and never calls
freeze.mismatches(); the 13 design sources are checked, FROZEN.json and the manifest are not. A re-sealed 5-shard design
is written over the frozen manifest; FROZEN.json's design pin and the manifest's own hash are rewritten to match; the
real analyse() path runs (only RUNS redirected) on a 5-shard forged set with genuine first rows. PREDICTION: COMPLETE,
exit 0, a verdict disposition for a 5-shard experiment; freeze.mismatches() at the same moment reports 'design manifest
differs from the frozen one' (confirm run would refuse); both files restored, sha256 equal, git diff quiet, freeze check
OK. Bearing (EVIDENCE CHAIN): one line (`freeze.mismatches()` first in analyse) closes it; until then the design pin at
analysis time is git, not the analyser.

### Edits (edits.json; run_edits.py) -- behaviours the frozen suite does not pin

| Id | Edit | Prediction | Witness |
|---|---|---|---|
| E1 | the replay sample is never taken (confirm.py:156) | SURVIVES | W1: dup6 -- REFUSED_RECORD_INCONSISTENT (1 problem) -> verdict (0 problems) |
| E2 | tree_check's root/origin check removed (evaluate.py:99) | SURVIVES | W2: root-relabelled dev tree -- ['origin: ...'] -> [] |
| E3 | analyse's unit-file-vs-row check removed (confirm.py:152) | SURVIVES | W3: one row's arrays_sha256 edited, shard meta re-digested -- 1 problem -> 0 (replay stubbed) |
| E4 | control: the builder's mutant 0 (REMOVED_MIN 0.7) | RED | test_threshold_edges |
| E5 | the completeness short-circuit removed (confirm.py:142) | SURVIVES | W5: 5 of 6 shards -- exit 3, nothing printed -> class counts and content excess printed (replay stubbed) |

Bearing (EVIDENCE CHAIN): the analyser's three guards (completeness stop, unit-file binding, replay) are enforced by one
untested line each; a repair round that touches confirm.py has nothing that would turn RED.

## 4. Ordering

This file, expected.json, edits.json, synth.py, natives.py, altn.py, forge.py, run_edits.py, cases.py, __init__.py and
EXPOSURE.md are committed in one commit before `cases sound|synth`, `natives`, `altn`, `forge-build|b5|b6`, `run_edits`
or `score` is run. Results: rows_natives.jsonl, results.jsonl, the scratch JSONs copied under results/, REPORT.md and the
receipt in a later commit. Harness fixes after the first run, if any, are committed separately with the reason; no
prediction in this file or expected.json is altered after this commit.

## 5. Budget

Natives 24 RX + 8 V1 at ~66 s / ~61 s on one core, 2 processes: ~20 min wall. B5 six replays ~7 min; B6 five ~6 min; B8
up to 4 x ~40 s; S2 red 21 x ~2 s; S4 ~2.5 min. Total <= ~0.9 core-hours, <= 2 processes, nothing paid, nothing on M2.
