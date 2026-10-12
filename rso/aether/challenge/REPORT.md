# C-018-T040 -- Q3 challenge of the frozen Aether ancestry-vs-content assay (FREEZE_AETHER_ANCESTRY_CONTENT v1.0.0): REPORT

Reviewer: Pallas[harry1-d78f77ce], claude-fable-5-1, headless on harry1 (M4), 2026-10-12, boot 11:11Z -> INTEGRATION_READY
~13:15Z. Surface: rso/aether at v1.0.0 (FROZEN.json: 32 LF sha256, Python 3.12, design pin 0e9519bd; integrated on main
9e51c80b3 = this branch's base). `freeze check` OK before the claim, after every mutant restore and at the end; the 32
pins recomputed from the HEAD blobs and from disk without freeze.py (S1). No confirmatory seed executed (k = 0x2000+i
untouched; `confirm run` never passed its guard; no RELEASE.json in the repo). Aether/ and roles/Aether/ never edited, not
even transiently; nothing on M2. An INFORMED review (every frozen file and all 21 builder mutants read; EXPOSURE.md); same
vendor, different model family from the builder (Argus, claude-opus-5-5). Cell member; writes no production code.

## 0. MODEL CONTINUITY (directive s9)

comms boot recorded claude-fable-5-1 (tier heavy) at 11:11Z. No harness message reported a different model at any point in
this session; the model line in every commit of this branch is the same. I therefore claim nothing beyond what the launch
log shows: the coordinator verifies continuity from that log. All findings below are deterministic and re-runnable from the
committed harness and rows; none depends on the reviewer's model.

## 1. Ordering evidence (git, UTC)

    cdea3c8bd  main    CLAIMED (LEASE.json)                                                        11:12:22Z
    3cc94b838  branch  the SET: CHALLENGE_SET.md, expected.json, edits.json, synth.py, natives.py,
                       altn.py, forge.py, run_edits.py, cases.py, EXPOSURE.md                      11:39:09Z
    0a478e424  main    IMPLEMENTING                                                                 11:39:14Z
    runs       synth (crashed in B3 on a dict merge with int keys: harness bug, no prediction
               involved), natives RX 0-5                                                           11:40-11:55Z
    d067e1b0d  branch  harness fix (synth.b3) + red_crlf.py (S2 follow-up)                         12:05:41Z
    runs       synth, sound, natives RX 6-23, V1 0-7, forge-build, natives-summary, altn,
               b5, b6, run_edits, score                                                            12:05-12:40Z
    9160c952e  branch  first-run results (outcomes/, rows_natives.jsonl, results.jsonl) and the
                       POST-HOC E1h / E3h predictions, BEFORE they ran                             12:44:37Z
    runs       edits_posthoc, score                                                                 12:45-12:55Z
    (this)     REPORT.md, outcomes/edits_posthoc.jsonl, results.jsonl, receipt -- one commit;
               INTEGRATION_READY on main

No prediction in CHALLENGE_SET.md or expected.json committed at 3cc94b838 was altered afterwards; E1h / E3h and
EDITS_POSTHOC_RESTORED were ADDED at 9160c952e and are labelled post-hoc. The outcomes directory is named `outcomes/`
(CHALLENGE_SET.md s4 says `results/`: that name is gitignored in this repository).

## 2. Score (26 checks; results.jsonl is the mechanical record)

    AS_EXPECTED       7   S1 S3 S4 S6 E4 EDITS_RESTORED EDITS_POSTHOC_RESTORED
    RECORDED          3   S5 (release gate is a process control) B7 (horizon) P1 (refusal prints the verdict numbers)
    SURVIVOR          9   B1 B2 B3 B4 B5 B6 E5 E1h E3h
    NOT_AS_PREDICTED  7   S2 (the builder's red harness is line-ending sensitive; the 4 blocked mutants verified KILLED)
                          N1 (modal evaluable class: a 3-3 tie between CONFIRMED and NONSPECIFIC; every other N1 claim held)
                          B4n (late-N vacuity has NO native incidence in 7 evaluable units: the builder's favour)
                          B8 (WORSE than predicted: the class flipped in 2 of 4 units when the second-ranked N is clamped)
                          E1 E3 (SURVIVES held; the witnesses were blocked by the design's source pin -- the builder's
                          favour -- and moved under the post-hoc re-seal, E1h / E3h)
                          E2 (SURVIVES held; my witness shape was wrong: re-rooting the tree also moves B / N)
    cost              natives 2,050 s CPU (32 units, 64 s mean), B5 7.4 min, B6 6.4 min, post-hoc ~9 min, altn 1.6 min,
                      sound ~5 min, edits 2 min: ~1.1 core-hours, <= 2 processes, ~2 h wall boot -> INTEGRATION_READY;
                      0 paid; 0 requests to Aether; 0 operator interventions; scratch 110 MB outside the repo.

## 3. CLOSED / NOT CLOSED per surface

    EVIDENCE CHAIN   NOT CLOSED. (i) B6: analyse() takes its only design pin from FROZEN.json and never runs the freeze
                     check; a re-sealed 5-shard design with FROZEN.json rewritten to match analysed as COMPLETE and printed
                     ANCESTRY_WITH_CONTENT, while freeze.mismatches() at the same moment said 'design manifest differs from
                     the frozen one'. (ii) B5: at the first analysis the design's digests are filled from what is presented,
                     so 64 rows of which 5 are distinct units are COMPLETE; nothing but the 6-of-64 replay sample catches a
                     substituted row, and a duplicated arrays_sha256 is not checked; the duplicates inflated the reach count
                     (12 CONFIRMED) and leaked test features into the decoder's training set (content excess 0.11 vs 0.012
                     on the same genuine units). (iii) B1: the tree's parent / gen / type are producer fields that
                     tree_check never reads and the replay never compares; INSUFFICIENT -> CONFIRMED and NO_CUT ->
                     NONSPECIFIC with problems == []. (iv) E5 / E1h / E3h: the analyser's three guards (completeness stop,
                     unit-file binding, replay) are each one line that no test pins; the design's source pin blocks a
                     mutated analyser only until the pin is rewritten (B6).
    INSTRUMENT       NOT CLOSED on one bounded point: B8. The C3 class depends on WHICH attributed non-ancestor the rule
                     clamps. In 2 of the 3 native NONSPECIFIC units the rule's N (earliest-diverging matched site) first
                     diverged at tick 1, BEFORE B (tick 4), removes 100% of B's descendants, and the second-ranked
                     candidate removes 0%: CONFIRMED. The rule prefers the site most likely to be an unattributed upstream
                     contributor of B (prop01 keeps the minimum-generation parent, so a gen-1 sibling that also fed B is
                     never B's parent). B4 (late N cannot remove anything) is a demonstrated gap in the rule with zero
                     native incidence in 7 units (B4n): a limitation to state, not a repair.
    INFERENCE        NOT CLOSED. B2: disposition() has no status for too few evaluable units; all-NO_CUT populations read
                     NEITHER or CONTENT_WITHOUT_INTERVENTIONAL_ANCESTRY, and `need` counts NO_CUT units in its
                     denominator. On 24 challenge RX units 13 are NO_CUT and 4 INSUFFICIENT (7 evaluable, 3 CONFIRMED at
                     r >= 2 = exactly the need of 3 at n = 24; at the confirmatory n = 48 the need is 5). V1: 6 NO_CUT + 2
                     INSUFFICIENT of 8, zero evaluable. B3: conditioned_excess conditions on the radius band only.
    INTERPRETATION   NOT CLOSED until the result text carries s4.4; nothing here reclassifies TEST-4.

Taken together: the confirmatory run is NOT blocked by the instrument's native behaviour (the recorder replays
bit-exactly, S4; 32/32 units bound, cross-checked and inside the light cone, N1), but its RESULT cannot be read by
`confirm analyse` as frozen without the evidence-chain repairs in s5 (items 1-3 are each one or two lines), and the text
must state s4.4 whatever the outcome.

## 4. Findings

### 4.1 Evidence chain

B6 PIN FROM A MUTABLE FILE (SURVIVOR; outcomes/B6.json). `analyse()` (confirm.py:135-168) reads `pinned_design_sha256()`
from FROZEN.json and verifies the 13 design sources' CURRENT bytes; it never calls `freeze.mismatches()`, which is what
compares the on-disk design with the design re-derived from confirm.py's constants (freeze.py:45-47). With a 5-shard
design (V1.1 dropped) written over the frozen manifest and FROZEN.json's `design_manifest_sha256` and manifest hash
rewritten, the real analyse() path (only RUNS redirected) returned COMPLETE, rc 0, problems [], and the full positive
verdict ANCESTRY_WITH_CONTENT (12 CONFIRMED, reach band 6, cond 0.108) for an experiment of 5 distinct units;
`freeze.mismatches()` run while mutated: ['design manifest differs from the frozen one']. Both files restored (sha256
equal, git diff quiet, freeze check OK). Bearing: at analysis time the design pin is git, not the analyser. Repair: call
`freeze.mismatches()` first in analyse() and refuse on any mismatch (one line; the freeze already pins FROZEN.json's own
file list, the manifest and the qualification record, none of which analyse() checks today).

B5 DUPLICATED EVIDENCE (SURVIVOR; outcomes/B5_frozen.json). In the frozen design's shape on my seeds: each shard's first
row genuine, every other row a copy with the seed label rewritten; RX.3's first row a copy of RX 0x3002 labelled 0x3003.
Completeness COMPLETE; 64 rows, 5 distinct arrays_sha256; the unit-file check, binding and tree_check raised nothing on
the 58 copies; the one problem was 'RX.3 seed 12291: native replay differs'. `fill()` (confirm.py:93-99) takes the
digests FROM the presented shards, so the first analysis can only check presence, partition, count and the current
source bytes; PREREG s8 says so, but the consequence is that provenance rests on 6 replays of 64 units, and an identical
arrays_sha256 across rows is never checked. Two further consequences: the reach count is inflated by copies (12
CONFIRMED here), and leave-one-seed-out decoding is no longer held-out when a seed's copies sit in the training set
(content_excess_all 0.112 on this set; 0.012 on the 24 genuine RX units). Repair: refuse a duplicated arrays_sha256
across rows (one line, defeats copying); bind each unit to its seed by recomputing the warm snapshot (`snap`, 300 ticks,
~1/4 of a unit; adapter.py:131-137) for every unit, not only the first per shard; state in the result that N of 64 units
were replay-verified.

B1 TREE TAMPER (SURVIVOR; outcomes/synth.json). tree_check (evaluate.py:86-106) compares the tree's `site` and `ftick`
with the arrays and the recorded B / N with the rules on the tree; `parent`, `gen` and `type` are read by the rules but
never checked, and the replay (confirm.py:157-159) compares arrays_sha256 only. Dev RX k=0: re-parenting three sites of I
under B -> CONFIRMED (4 targets), problems [] (two of those parents are non-adjacent, so a structural check would catch
this one); re-parenting with every native invariant respected (4-adjacency, parent earlier, gen = parent + 1; 0 violations
on all six dev and all 32 challenge trees) -> CONFIRMED (5 targets), problems [], 0 violations. Dev RX k=3 (NO_CUT, 21
generations): one `type` byte RULE -> CARRY and the meta's B / N rewritten -> NONSPECIFIC on 70 targets read from clamp
arrays that are all -1 because no clamp world was run (adapter.py:150-151). PREREG s7 'never from producer fields' is
overstated for the attribution's structure. Repair: compare meta["tree"] in the replay (S4 shows the replayed tree is
equal, so this costs nothing) and add the three invariants to tree_check (cheap second line; closes the naive and the
type-flip forms, not the invariant-respecting one, which only the replayed tree closes).

E5 / E1h / E3h UNPINNED GUARDS (SURVIVOR; outcomes/edits_rows.jsonl, edits_posthoc.jsonl). Each of the analyser's three
guards is one line no test pins: the completeness short-circuit (confirm.py:142; E5: 5 of 6 shards -> the mutant prints
class counts and content excess with 'INCOMPLETE'), the unit-file-vs-row check (:152) and the replay sample (:156).
Under the first run the E1 / E3 witnesses were REFUSED with SOURCE_MISMATCH because the forged design pinned confirm.py's
own hash -- a real property in the builder's favour, recorded. With the design re-sealed under the mutant (what B6 shows an
attacker can do) E1h printed ANCESTRY_WITH_CONTENT with problems [] on the set whose first RX.3 row is substituted, and
E3h reported COMPLETE with problems [] on the edited-row set. E4 (the builder's mutant 0) went RED on test_threshold_edges
as predicted; the 33-test suite stayed green on all five mutants and both post-hoc runs. Repair: one test per guard on a
two-shard fixture with a stubbed replay (the shape of forge.e3 / e5).

P1 REFUSAL LEAK (RECORDED). With disposition REFUSED_RECORD_INCONSISTENT the analyser prints every law's class counts and
content excess (B5 output). The stopping rule forbids an interim look (PREREG s6); a refusal should print the problems
and nothing verdict-bearing. One-line repair.

S5 RELEASE GATE (RECORDED). `release_problem` is a file-content check: a RELEASE.json with the three fields written by
anyone passes it. The gate is a process control (who may commit that file), which is what FREEZE.md says; nothing was
executed to show this (the function was called on a scratch path).

### 4.2 Instrument

B8 THE CHOICE OF N DECIDES THE CLASS (NOT_AS_PREDICTED, worse; outcomes/altn_summary.json). For the first four evaluable
RX challenge units the warm snapshot, origin and impulse world were recomputed bit-exactly (adapter.py:129-137) and the
second-ranked non-ancestor candidate of the same rule clamped instead of N:

    k       B ftick  N ftick  removed_N  class         N2 ftick  removed_N2  class(N2)
    0x3001  1        4        0.00       CONFIRMED     5         0.00        CONFIRMED
    0x3003  1        4        0.74       NONSPECIFIC   7         0.44        NONSPECIFIC
    0x3004  4        1        1.00       NONSPECIFIC   4         0.00        CONFIRMED
    0x3005  4        1        1.00       NONSPECIFIC   5         0.00        CONFIRMED

In 0x3004 and 0x3005 the rule's N first diverged at tick 1, three ticks BEFORE the ancestor B under test, and its clamp
removed every one of B's descendants; the next candidate removed none. The rule (adapter.py:49-63) matches on distance,
then takes the EARLIEST-diverging site, i.e. exactly the gen-1 sibling most likely to have fed B through a path the
attribution does not record (prop01_run.py:170-199 keeps the minimum-generation candidate parent: a gen-1 site that also
wrote into B is never B's parent when O is). The registered near-miss A_misN ('a claimed non-ancestor that IS upstream')
is scored NONSPECIFIC, so by the registered meaning the class is 'correct'; the finding is that NONSPECIFIC conflates two
mechanisms (damage spreading vs an upstream contributor missed by attribution), that the N rule selects for the second,
and that the specificity verdict of a unit is therefore not a property of the unit. 0x3003 (N after B) stays
NONSPECIFIC under both: genuine nonspecificity exists too. Bearing: INSTRUMENT NOT CLOSED on the N rule. Repair options:
require ftick(N) >= ftick(B) among candidates (a non-ancestor that diverged before the ancestor under test is not a
matched control); or clamp two non-ancestors and report NONSPECIFIC only if both remove > 0.2; or split the class
(NONSPECIFIC_UPSTREAM when ftick(N) < ftick(B)). Each is a preregistration change, so it belongs to the one repair round
and a re-freeze.

B4 LATE N (SURVIVOR synthetic; B4n NOT_AS_PREDICTED natively). CUT_N equals IMPULSE until N diverges (adapter.py:66-90),
so a target that diverged before N cannot be removed by N; ancestry() (evaluate.py:67) calls N vacuous only if it never
diverged. The synthetic chain (targets at ticks 3-5, N at 50) is CONFIRMED with removed_N 0.0 and zero N-live targets.
Natively, in all 7 evaluable RX units every target diverged after N (N-live fraction 1.0 in each): the rule's preference
for an early N makes this gap unreachable in practice while making B8's gap likely. State as a limitation; the repair for
B8 (ftick(N) >= ftick(B)) must not re-open it (require ftick(B) <= ftick(N) <= min ftick(targets), or compute removed_N
over the N-live targets).

B7 HORIZON (RECORDED). On the stored arrays with divergences after H' set to 'never': 0x3001 is CONFIRMED at H = 400 with
all 22 targets first diverging at ticks 226-319, INSUFFICIENT at H' <= 200 and NONSPECIFIC at 300; 0x3004 is INSUFFICIENT
at 100. 4 of 142 targets across the 11 units with a B diverged after tick 300. 'Never diverges in CUT_B' means 'not within
400 ticks'; a CONFIRMED unit whose targets appear late is a delayed-divergence reading as much as a removal. The result
should report the targets' first-tick distribution per CONFIRMED unit.

### 4.3 Inference

B2 NO_CUT HONESTY (SURVIVOR; outcomes/synth.json). Through the frozen law_summary + disposition with accuracy dictionaries
supplied directly: 48 NO_CUT units with decodable content -> CONTENT_WITHOUT_INTERVENTIONAL_ANCESTRY; 44 NO_CUT + 4
CONFIRMED at r_int 3 -> NEITHER (need = ceil(10% of 48) = 5 counts the NO_CUT units); 16 V1 all NO_CUT -> NEITHER; 43
NO_CUT + 5 CONFIRMED r_int 2 at chance -> CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT. The eight statuses the rule can
emit contain none that names an unevaluable population. Native incidence on my seeds (N1): RX 13 NO_CUT + 4 INSUFFICIENT
of 24 (7 evaluable: 3 CONFIRMED all with r_int >= 2, 3 NONSPECIFIC, 1 NOT_INTERVENTIONAL); V1 6 NO_CUT + 2 INSUFFICIENT of
8 (0 evaluable). At n = 24 the need is 3 and P2 held by exactly 3; at the confirmatory n = 48 the need is 5 against an
expected ~6 CONFIRMED-at-depth (3/24 x 48), so the RX disposition is likely to be decided by one or two units, and V1 is
likely to read NEITHER having tested nothing. Repair: compute `need` over the evaluable units with a preregistered
minimum (e.g. >= 8 evaluable), and emit ANCESTRY_UNEVALUABLE below it; print the evaluable count beside every label.

B3 RADIUS-ONLY CONDITIONING (SURVIVOR). 5 CONFIRMED units (r_int 2) whose own held-out accuracy is chance + 43 NO_CUT
units at accuracy 1.0 -> ANCESTRY_WITH_CONTENT (cond 0.784 over all seeds; 0.0 over the CONFIRMED units' features).
Argus's own open question (ONBOARDING s6) answered: yes, content at radius 2 in other units stands in for content at the
clamped descendants. Repair: report conditioned_excess restricted to the CONFIRMED units' seeds beside the registered one
(the decoder already gives per-seed accuracy); whether the registered rule changes is the owner's call.

N1 NATIVE READING (rows_natives.jsonl; DEV-class, not a result). 32 units: 0 binding / tree problems, light cone 32/32,
t0 identity 32/32, tree invariants 32/32, null excess -0.0004 (RX) / 0.00005 (V1). RX 24: band 2, confirmed_r2 3, pooled
attribution agreement 0.43 (DISAGREE), content excess 0.012, disposition-if-complete CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE
_CONTENT; V1: NEITHER with zero evaluable units. Attributed depth ranges 0-13 generations; of the 11 RX units with a B, 4
have fewer than 3 targets. The first native CONFIRMED / NONSPECIFIC / NOT_INTERVENTIONAL readings exist now (PREREG s9
said none did); the 3-3 tie between CONFIRMED and NONSPECIFIC decided N1's one missed sub-prediction.

### 4.4 Interpretation: what the confirmatory result must state, whatever it is

1. The evaluable count (CONFIRMED + NONSPECIFIC + NOT_INTERVENTIONAL) beside the disposition; NEITHER or
   CONTENT_WITHOUT_INTERVENTIONAL_ANCESTRY with fewer than ~8 evaluable units is 'ancestry not evaluated', not 'absent'.
2. ANCESTRY_WITH_CONTENT means co-occurrence at the radius-band level across the population; the conditioned excess over
   the CONFIRMED units' own features is reported beside it (B3).
3. NONSPECIFIC units are split by ftick(N) < ftick(B) (B8); the class of a unit is conditional on the registered N rule.
4. The per-unit first-tick distribution of targets for every CONFIRMED unit (B7).
5. How many of the 64 units were replay-verified and that no row pair shares arrays (B5), and that the analyser ran
   `freeze check` (B6) -- or that it did not, if the run precedes the repair.
6. 'CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT' carries PREREG s3's bound (excess < ~0.05-0.10 not excluded); the 24
   challenge units read 0.012 with a null of -0.0004.

## 5. Recommended bounded repair round (owner's; ranked by bearing / cost)

1. analyse(): run `freeze.mismatches()` first and refuse on any mismatch (B6). One line.
2. analyse(): refuse a duplicated arrays_sha256 across rows; compare meta["tree"] in the replay; do not print law
   summaries on REFUSED / INCOMPLETE (B5, B1, P1). Three lines.
3. tree_check: the three structural invariants (B1 naive / type-flip forms). Ten lines.
4. One test per analyser guard on a two-shard fixture with a stubbed replay (E5, E1h, E3h).
5. disposition(): `need` over evaluable units with a preregistered minimum and an ANCESTRY_UNEVALUABLE status; report
   the evaluable count (B2). Preregistration change.
6. N rule: ftick(B) <= ftick(N) <= min ftick(targets), or two non-ancestors (B8, B4). Preregistration change; re-run the
   fixture qualification (A_misN / A_vacN must still class as registered) and re-freeze as v1.1.0.
7. Report conditioned_excess over CONFIRMED units beside the registered one (B3). Reporting only.
Items 5-6 change frozen meaning and need the re-freeze FREEZE.md already provides for; items 1-4 and 7 do not change any
registered rule. A warm-snapshot provenance check for every unit (B5) is recommended but is a budget decision (~16 min CPU).

## 6. Misses and harness notes (every one reported with its value)

- S2: the builder's run_red matches four edits with an embedded '\n'; on this CRLF checkout they report EDIT_NOT_UNIQUE
  and the harness exits 1 with 17/17 killed. red_crlf.py re-applied those four with the file's line ending: 4/4 KILLED
  (outcomes/red_crlf.json). The builder's 21/21 stands; the harness is not portable across checkouts.
- N1: the modal evaluable class was a 3-3 tie; my check took `max` over a tie as CONFIRMED. Every other N1 claim held.
- B4n: no native incidence (the builder's favour).
- B8: predicted <= 1 flip, observed 2 of 4; the miss is in the direction of a fault (s4.2).
- E1 / E3: SURVIVES held; the witnesses were refused by the design's source pin -- not anticipated, a property in the
  builder's favour, then circumvented by the labelled post-hoc re-seal (E1h / E3h SURVIVOR).
- E2: SURVIVES held and the 'origin:' line vanished under the mutant, but re-rooting the tree also changes choose_cut's
  B and the N rule's N, so tree_check still reported those two lines; my predicted `[]` was wrong, the machinery was not.
- Harness: synth.b3 crashed on `dict(a, **b)` with integer keys before any B3 value was seen; fixed at d067e1b0d (no
  prediction involved). The outcomes directory is `outcomes/` because `results/` is gitignored. The post-hoc run exceeded
  one 600 s call because its frozen baseline replayed six shards again instead of reusing B5; the harness moved it to the
  background and it completed with every file restored (freeze check OK; edits_posthoc.jsonl).
- Synthetic rows (B2, B3) supply accuracy dictionaries to law_summary directly, bypassing the decoder: the findings are
  about the rule, not the decoder, and are stated so.
- The forged sets run the frozen analyse() with DESIGN_PATH / RUNS / the pin redirected to scratch (the frozen design's
  seeds may not be executed by this seat); B6 redirects RUNS only. Replay was stubbed in E3 / E5 / E3h witnesses only.

## 7. What this challenge did not do

- No attack on Aether's decoder beyond the native null and the audit's re-derivation: the content branches are multi-site
  by design, and the t0 identity control applies to the ancestry pair only. The graded-sensitivity limit (inert medium,
  PREREG s9) stands unchallenged and unclosed.
- No native attack on the light-cone guard (it cannot fail natively; conceded in PREREG s4).
- The audit's `reads_answer` check is vacuous for this evaluator (no detector reads the scrubbed name fields; fixture
  sites are the recipe, conceded). Noted, not scored.
- The 4 units with a B and fewer than 3 targets (INSUFFICIENT) were not probed further.
- No second non-ancestor was run for the three units B8 did not reach (0x3009, 0x3015, 0x3016).

## 8. Registry notes for Palamedes (proposals, not edits)

- experiment-completeness: counterexample 'design manifest filled from the presented shards: COMPLETE on 59 copies of
  5 units' (B5); not_qualified_for 'provenance at the first analysis'.
- control-falsifiability-checks: new historical case 'non-ancestor clamp whose site diverged before the ancestor under
  test' (B8), beside CONTROL_VACUOUS.
- aether-ancestry-content-instrument (candidate): stage CHALLENGED; not_qualified_for 'reading NEITHER /
  CONTENT_WITHOUT_INTERVENTIONAL_ANCESTRY as an ancestry result without the evaluable count' (B2); counterexamples B1, B6.
