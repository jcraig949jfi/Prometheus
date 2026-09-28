# RESULT -- Endogenous world-record sandbox: known-answer gate + exploratory unplanted run

Currency: 2026-09-28. Odysseus research worker. Pure ASCII.
Spec: DESIGN.md. Frozen rules: PREREG.md. Amendment: AMENDMENTS.md (A1).
Data: known_answer_run1_GATE_FAILED.json, known_answer.json, unplanted.json.
Tests: tests/ (13 pass: determinism, save/restore replay, forbidden-
information blindness, no-lookahead, sigma symmetry, known-answer
directions, gate recomputed from per-world data).
Compute: gate run 1 7.3 min wall, run 2 6.7 min, unplanted 16.3 min (4
workers on a host at load ~40 from sibling jobs); total ~31 min wall.
n = 20 independent worlds per arm throughout. delta = 0.05.

## 1. Known-answer gate: PASS (on run 2, after one prereg'd-process amendment)

Run 1 FAILED on one criterion only: the A/A control in arm C excluded 0
(0.008 [0.004, 0.012]). Cause: eval seeds were identical across worlds
(pseudo-replication; the world bootstrap assumed independence). Repair A1:
salt probe seeds per world (paired within world, independent across).
Nothing else changed. Run 2 is the verdict.

Arm      highest  key statistics (mean [95% CI], success-rate units)
P        R3       D0 .594[.556,.631] D1 .470[.387,.553] D2 .470 Dp .489[.409,.570]
                  Dr .461[.393,.530] Di 0 ; R4: I 0, J 1.0 -> no ; R5: no
P4       R3*      D1 .411 Dp .420 Dr .424 Dx .148[.046,.248] I .109[-.002,.212] J 0
N_a      R0       D0 .606 ; D1 = D2 = Dp = Dr = 0 exactly
N_b      none     D0 -.018[-.058,.026] ; D1 .051[-.040,.151]
C        R2       D0 .224 D1 .460[.310,.598] D2 .460 ; Dp 0, Dr 0 exactly -> R3 FAIL
P_sigma  R0       D1 .041[-.088,.153] (the planted code breaks under relabeling)
A/A      all arms CI contains 0.
Convention qualifier for P: INSTALLED (D1 .470 identity vs .041 sigma).

Gate criteria (PREREG s5): P awards R0-R3 YES; P not R4/R5 YES; P
INSTALLED YES; N_a nothing above R0 YES; N_b nothing above R0 YES; C fails
R3 YES, on content (perm and random-record) with R2 awarded YES; A/A valid
YES. Secondary: P4 planted R4 was awarded in run 1 (I lo +.002) and NOT in
run 2 (I lo -.002). R4 detection is UNVALIDATED (underpowered at n = 20;
Dx passes firmly, the interaction term sits on the threshold).

Speed vs ceiling (P): window ceiling .733 intact vs .264 deleted/no-record;
time-to-0.5 after a switch 1.5 vs 5.7 generations. R5 not awarded: (a) and
(c) pass, (b) the v0-literal recompute arm saturates (see s4, C1).

## 2. Unplanted run (EXPLORATORY, 3000 generations, random genomes)

Highest rung reached: NONE (not even R0) in every unplanted arm.

Arm       D0              D1               Dp               ceiling  evo success
U_sigma   .031[-.011,.076] .005[-.003,.016] .012[-.005,.036]  .543     .553
U_id      .029[-.013,.072] .007[-.001,.018] -.021[-.043,-.003] .553    .546
U_frozen  -.005           -.094[-.187,-.009] -.060            .245     .252
U_unread  --              --               --                .560     .570
U_norec   --              --               --                .564     .562
Convention: benefit absent in both U_id and U_sigma (the code prints
"INSTALLED" -- a labelling defect, see C2; the honest reading is ABSENT).

Reading: the ecologies solved the environment WITHOUT the record. Record-
free worlds (U_norec, U_unread) reach .56, the same as record-bearing
worlds; readers were mostly selected out (median reader fraction ~0.01-
0.03; reading costs and pays nothing at first -- the classic chicken-and-
egg of signalling: a reader is useless without a writer and vice versa).
Frozen readout: a random fixed reader made the record HARMFUL (D1 -.094):
writers did not adapt to a fixed code in 3000 generations.

One outlier world, reported and not promoted: U_sigma seed 1016 (reader
fraction .72) shows D1 .094, D2 .217 (novel receivers .35 vs .14 without
record), Dp .219, Dr .113 -- the per-world R1-R3 pattern -- yet its D0 is
-.150 (the evaluator's decoder of s does worse than the ablated twin). 1/20
worlds; no aggregate claim. It is a live lead for a frozen follow-up
(more worlds, longer runs, seeded from its dynamics class, not its genome).

Boundary rung (this world, this budget): below R0 in aggregate. The v0
prediction (boundary at R2/R3) is not tested yet: the unplanted ecology
never bootstrapped a reader-writer pair at population scale. The first
wall is BOOTSTRAP of a two-sided convention, before any accumulation rung.

## 3. What the gate shows the battery can and cannot do

- It separates use of content (P) from use of presence (C) exactly: C's
  permutation and presence-preserving random records cost nothing (0.000)
  while deletion costs .46. Without R3 the cheat would be awarded R2.
- It separates information-in-the-world (N_a: R0 only) from use.
- Convention invariance detects an installed plant (P vs P_sigma).
- It does NOT reliably detect planted recombination at n = 20 (P4).

## 4. Critique of ACCUMULATION_v0 (what it got wrong or underspecified)

C1. RECOMPUTE ARM BUDGET IS UNDEFINED AND, AS WRITTEN, MAKES R5 UNREACHABLE
    IN SMALL WORLDS. "A consumer without X but given the budget it cost to
    produce X": the production budget of a colony record is >= 24 foraging
    trips; a record-free searcher with 24 trips over 4 sites finds the patch
    with certainty (recompute 1.0 > any ceiling). Every planted arm fails
    R5(b) for this reason alone. v0 must say WHOSE budget (the consumer's
    per-decision budget vs the ecology's total production budget), must
    require the recompute arm to face the same per-decision constraint as
    the consumer, and must report R5 as unreachable-by-construction when
    the search space is smaller than the production budget.

C2. CONVENTION INVARIANCE IS A 3-WAY OUTCOME, NOT 2, AND IS VACUOUS FOR
    SYMMETRIC INITIAL CONDITIONS. (i) invariance presupposes a benefit;
    "not invariant" conflates INSTALLED with ABSENT (my code's qualifier
    has this exact defect -- unplanted arms print INSTALLED with zero
    benefit). (ii) With genomes drawn uniformly, invariance under sigma
    holds by symmetry whatever happens, so the test only audits the
    experimenter's plant, not the physics. The installed-semantics risk in
    an unplanted world lives in the AFFORDANCES (here: the write table is
    indexed by (site, found), which pre-selects WHAT is worth writing).
    v0 needs an affordance audit, not only an alphabet relabeling.

C3. R0 AS DEFINED CAN VETO A WORLD WHOSE CONSUMERS PROVABLY USE CONTENT.
    "History-specific content" must be operationalized by an evaluator
    decoder of a chosen variable; v0 names neither. World 1016 passes the
    R1-R3 interventions and fails R0 (decoder of s pooled across colonies
    underperforms the ablated twin). The ladder's strict ordering (each rung
    requires every lower rung) is then wrong: consumer-based interventions
    (R1-R3) are stronger evidence of content than any evaluator decoder.
    Fix: define R0 by intervention too (the record at t+T still changes a
    fixed probe consumer's behaviour vs the ablated twin), or drop R0 as a
    prerequisite and report it alongside.

Further, smaller:
C4. Pseudo-replication: "matched counterfactual" / common random numbers
    must be specified as WITHIN-world pairing only (AMENDMENTS A1; the A/A
    control caught it; v0 does not require an A/A control -- it should).
C5. R1 vs R2 collapse in generational worlds: when every producer dies
    before any read, "same producer" reuse does not exist; D1 = D2 exactly
    in all planted arms. And "different individual" is trivially met by
    clonal populations (founder overlap 0 by uid, genomes identical). R2
    needs a GENOTYPE/lineage-distance requirement for the novel consumer.
C6. R4 has no power requirement; a bounded success metric compresses the
    interaction term (P4: superadditive by construction, I = .109 with CI
    touching 0). v0 should prereg a detectable effect and n, or use the
    pair-over-best (Dx) plus provenance as primary.
C7. Irrelevant-record injection is often inapplicable (in steady state every
    cell is rewritten each generation; Di = 0 by construction here). v0
    should define "irrelevant" by capacity added (extra cells), not by
    unwritten cells.
C8. v0 omits the BOOTSTRAP rung: the unplanted result says the first wall
    is the joint emergence of a reader and a writer (the signalling-game
    coordination problem), which the ladder does not name. Add R(-1):
    "a record-mediated coupling exists at all" (reader fraction and a
    D1 > 0 in any world), with its own base rate.

## 5. Not done / limits

R6 not implemented. One environment family, one K, one alphabet, one
cost setting; no parameter sweep (a sweep over read/write costs would test
the bootstrap wall directly). Unplanted results are EXPLORATORY (s16); no
holdout was consumed; nothing here is evidence for any word in s15's
forbidden list.
