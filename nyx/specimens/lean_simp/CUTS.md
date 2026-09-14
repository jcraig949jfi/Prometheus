# Lean/mathlib simp -- the cuts

Currency: 2026-09-11. Ledger: cuts.json (machine-read by nyx/chop/cutledger.py).
This file is the human-readable side: the reading log, one line per candidate
with the reason for its disposition, and the numbers AFTER they were computed.
CUT-1 is never rewritten; CUT-2 and later are appended below it.

## Reading log (CUT-1, in the preregistered order)

Read, with line numbers cited in the organ records: Types.lean (skeleton +
24-36, 61-122, 283-340, 421-450), Main.lean (skeleton + 213-256, 531-551,
637-657, 672-722), Rewrite.lean (skeleton + 27-56, 57-107, 114-176, 203-274,
525-537, 608-656), SimpTheorems.lean (skeleton + 143-166, 261-378),
DiscrTree/Types.lean 1-60, DiscrTree/Main.lean (skeleton + 69-115, 188-247),
LoopProtection.lean (whole), SimpAll.lean (skeleton + 20-60), Simproc.lean
(skeleton + 216-252), Elab/Tactic/Simp.lean (skeleton only). mathlib:
Simps/Basic.lean 1-40, SimpRw.lean 1-30, Lean/Meta/Simp.lean (skeleton),
FieldSimp.lean 1-60 + grep for simp calls, FieldSimp/Discharger.lean header.

NOT read: CongrTheorems.lean, SimpCongrTheorems.lean, ACLt.lean, Arith/,
BuiltinSimprocs/* bodies, Elab/Tactic/Simp.lean bodies, Simps/Basic.lean
bodies, the Simproc/ mathlib files. Where an organ record leans on one of
these it says so and grades the source "unknown".

No Lean executed. No mathlib built.

## CUT-1 candidates (23), disposition and reason

    id  origin      disp             one-line reason
    c01 INHERITED   ORGAN            preprocess: every Prop shape -> oriented Eq rules; the adapter between a fact store and a rewriter
    c02 DISCOVERED  ORGAN            key abstraction: the forgetting table (proofs, instances, non-type implicits, offsets, reducible heads) separated from the trie
    c03 INHERITED   SCAFFOLDING      the trie: a generic data structure; nothing specimen-specific
    c04 INHERITED   UNRESOLVED       priority sort + first success: is "first applicable wins" a mechanism or a policy over c05?
    c05 INHERITED   UNRESOLVED       unify + synthesize + no-op reject: the rule-application step; may be the true organ with c04/c06/c07 as policies on it
    c06 DISCOVERED  ORGAN            perm flag at ingestion + acLt at application: ordered rewriting, spans two files
    c07 INHERITED   ORGAN            the default discharger is simp itself, depth-capped, cache-protected
    c08 INHERITED   ORGAN            simpLoop: pre / reduce / descend / post / loop / memo
    c09 INHERITED   ORGAN            congruence descent; most of it lives OUTSIDE the Simp directory (CongrTheorems.lean)
    c10 INHERITED   UNRESOLVED       reduceStep: config-gated calls into Meta reducers; simp's or the kernel's?
    c11 INHERITED   POLICY           the fixed order of the pre/post slot chains
    c12 INHERITED   SCAFFOLDING      simproc dispatch: c04 over a different payload
    c13 INHERITED   ORGAN            simp_all: hypotheses as rules, mutual saturation
    c14 DISCOVERED  COUPLED_CLUSTER  memo validity: five fields/flags across three files with a contract nobody checks
    c15 INHERITED   SCAFFOLDING      used-theorem accounting; simp? minimisation is instrumentation of c08
    c16 INHERITED   SCAFFOLDING      loop protection is a post-mortem linter, not a preventer
    c17 INHERITED   DATA             the store's organisation (two trees, erased set, priorities) is how DATA is arranged
    c18 INHERITED   UNRESOLVED       @[simps] generates rules from structure projections: an organ that produces DATA, or DATA tooling?
    c19 INHERITED   SCAFFOLDING      mathlib sequencing wrappers
    c20 INHERITED   DEAD_CUT         field_simp: at this pin the name survives and the mechanism left (own normal form; borrows Simp.Result)
    c21 INHERITED   DATA             the 48,076 attribute sites and the orientation convention that humans apply at tagging time
    c22 INHERITED   POLICY           dsimp is a mode flag on c08
    c23 INHERITED   ORGAN            closed-term evaluation: decide / literal folders / arith / seval

Prompt-named failed cut check: parser / simplifier / theorem database /
result. c17+c21 together ARE "theorem database" and are dispositioned DATA,
not ORGAN. c08 alone would be "simplifier" and is an ORGAN only because its
record names the Step protocol and the memo contract rather than the word.
The Elab front end (parser) was not made a candidate. Whether c08 as
recorded is "simplifier" wearing a longer name is the first CUT-2 question.

## CUT-1 numbers (computed by cutledger AFTER the records were written)

    candidates 23; live 22; ORGAN 8; UNRESOLVED 4; POLICY 2; DATA 2;
    SCAFFOLDING 5; COUPLED_CLUSTER 1; DEAD_CUT 1
    inherited-boundary rate 20/23 = 0.87        (P1 predicted >= 0.60: CONFIRMED)
    organs with an independent test RUN: 0/8   (all 8 "specified"; no Lean executed)
    organs with an ancestor-free contract asserted: 5/8
    unknown fields at CUT-1: 0                  (see observation O2)
    cheat controls: 8 declared, 8 not_run
    record bytes: 49,587 over 8 organs

## Observations at CUT-1 (findings about the Chopper, not about Lean)

O1. The knife followed the def-name skeleton. 20 of 23 boundaries were
    drawn where `grep -n "^def"` had already drawn them. The three that were
    not (c02, c06, c14) are the three Nyx would defend most readily, and two
    of them are about STATE the source spreads across files. This is the
    same habit journaled after DreamCoder; it did not go away by knowing
    about it.
O2. Zero fields say "unknown". Every field is prose, and the prose hedges
    ("claimed, not measured", "designed, not measured"). That defeats the
    ledger's unknown-tracking metric while looking more complete than a
    literal "unknown" would. The Chopper prefers fluent hedging to the
    legal word. CUT-2 must convert every field whose honest value is
    unmeasured into a string that BEGINS with "unknown" so the ledger can
    count it; the ledger's unknown detection must accept the prefix.
O3. The pressure LEAK check fired twice on substrings ("trie" in
    "tried", "simp" in "simpler"). Rephrased rather than weakening the
    validator; recorded so the false-positive class is known. Not a
    consumer failure, so the validator is NOT changed (charter XV).
O4. P3 (mathlib extension files yield zero organs) holds at CUT-1: c18
    UNRESOLVED, c19 SCAFFOLDING, c20 DEAD_CUT. The mathlib half of
    "Lean/mathlib simp" is DATA (c21) plus tooling. The operator's specimen
    name spans two repositories and one mechanism.
O5. P4 (the most transferable candidate does not coincide with a file
    boundary): c02 and c06 are the two Nyx rates most transferable and
    both are DISCOVERED. Consistent with P4 but Nyx is grading her own
    transferability guess; the consumer decides.
O6. The specimen ships its own perturbations: Simp.Config.index,
    memoize, singlePass, decide, ground, arith, and the erase syntax. Every
    "ablation" field that cites one of these is cheap to run and none was
    run. That is the first thing a consumer with a Lean toolchain should
    do, and the reason Techne's non-management of the pin matters.
O7. "unknown"-graded sources: ACLt.lean, CongrTheorems.lean,
    SimpCongrTheorems.lean. c06 and c09 depend on them. Their contracts
    are asserted from call sites only.

## CUT-2 (2026-09-11, same day; the twelve attack questions applied on paper)

Records: organs/*.cut2.json for c01, c02, c06, c07, c23 (narrowed copies;
the .cut1 files are untouched); pressures/mutual_normalisation.cut2.json
(c13 demoted to a pressure). Ledger vocabulary change: "unknown" is now a
PREFIX convention in organ fields ("unknown -- <what would make it known>")
because CUT-1 had zero literal unknowns while hedging in prose (O2).

    id  CUT-1 -> CUT-2       relation   reason
    c01 ORGAN -> ORGAN       SURVIVED   scale MECHANISM -> PRIMITIVE; the census gives A9 a number (33.8% non-Eq)
    c02 ORGAN -> ORGAN       SPLIT      relevance table out as c25 POLICY; flattening + root-reduction stays
    c04 UNRES -> POLICY      DEMOTED    first-applicable-wins by priority has no independent behaviour
    c05 UNRES -> COUPLED     DEMOTED    unifier is Meta's and shared with rw; cut B preserved
    c06 ORGAN -> ORGAN       SURVIVED   passes all twelve; assumptions honestly unknown (ACLt unread)
    c07 ORGAN -> ORGAN       SPLIT      cache protection -> c14; depth cap + success criterion named as policy
    c08 ORGAN -> POLICY      SPLIT      "simplifier" wearing a longer name; Step protocol out as c24
    c09 ORGAN -> COUPLED     DEMOTED    contract NOT independent of Lean (dependent types); cut C
    c10 UNRES -> SCAFF       DEMOTED    glue over Meta reducers
    c13 ORGAN -> PRESSURE    DEMOTED    its distinctive feature is a failure (F7); the condition transfers
    c14 COUPLED -> COUPLED   SURVIVED   grew (absorbed the discharge cache discipline); pressure candidate, held
    c18 UNRES -> SCAFF       DEMOTED    DATA tooling
    c23 ORGAN -> ORGAN       SPLIT      decide route only; folders -> c27 DATA; arith -> c28 UNRESOLVED
    c24 NEW    SCAFFOLDING   from c08   the Step protocol (an interface)                       origin DISCOVERED
    c25 NEW    POLICY        from c02   the relevance table (every retrieval prior)             origin DISCOVERED
    c27 NEW    DATA          from c23   per-type literal folders                                origin INHERITED
    c28 NEW    UNRESOLVED    from c23   arithmetic normaliser, unread                           origin INHERITED
    others unchanged.

CUT-2 numbers: candidates 27; ORGAN 8 -> 5; POLICY 2 -> 5; COUPLED 1 -> 3;
kind changes 7; split products 8; materially revised 15; record bytes
49,587 -> 37,720 (-24%); VERBOSITY_FAILURE false; literal-unknown fields
0 -> 12; inherited rate among the 4 new candidates 2/4.
P5 ("fewer than half of CUT-1 ORGANs survive as ORGAN at CUT-2"): 5/8
survived. FALSIFIED. Nyx predicted a harsher knife than she used.

## CUT-3 (2026-09-11; from completed ablations, no consumer return yet)

The pinned v4.30.0 toolchain was executed read-only on a core-only file
(ablations/cut3_ablations.lean; RECEIPT_2026-09-11.json; exit 0 with every
#guard_msgs matching the observed message). PREREG s2 said no Lean for
CUT-1; the stopping rule allowed CUT-3 on "a completed ablation".

Run: A1 index off, A2 memoize off, A3 singlePass, A6 discharge depth 0,
D3 planted loop, positives for c01 c06 c07 c08 c23. Not run: A4 A5 A7 A8
A9 A10 (need a patched build or source edits).

Results that did NOT change the cut: A1, A2, A3, A6 as predicted; D3 FIRED
(the planted two-rule loop hits "maximum number of steps exceeded", not
"no progress"); c01 c06 c07 c08 positives pass.

The result that changed the cut: the c23 NEGATIVE control did not fire.
2 + 2 = 4 closes with decide := false and the Nat folders erased. The
trace names eq_self. Two things Nyx had not enumerated:
  c29 `simp only` is not only: eq_self and iff_self are always loaded
      (Elab/Tactic/Simp.lean 410, 463). POLICY; origin PERTURBED.
  c30 unification decides 2 + 2 =?= 4 by definitional Nat-literal
      evaluation (Meta.isDefEq / WHNF, OUTSIDE the boundary), so any
      reflexive rule closes closed arithmetic. COUPLED_CLUSTER; origin
      PERTURBED. Confirmed both ways: erase eq_self -> no progress; make
      the literal non-reducible (k + k = 4) -> no progress.
  c23 ORGAN -> UNRESOLVED (DEMOTED): its headline fitness value belongs
      to c30. Attack question "could a much smaller mechanism reproduce
      the claimed fitness value?" answered YES by experiment. The
      residual (Props not closable by defeq) is untested.
  The c07 positive control was discharged BY c29 (the guard 3 = 3 closed
      via eq_self): the discharge demonstration leans on a hidden
      default. Recorded on c07; disposition unchanged.

CUT-3 numbers: candidates 29; ORGAN 4 (c01 c02 c06 c07); UNRESOLVED 2
(c23 c28); COUPLED 4; POLICY 6; kind changes 1; new 2; materially revised
1 (+2 PERTURBED discoveries); bytes 37,720 -> 32,206 (-15%);
VERBOSITY_FAILURE false; cheat controls fired 1 (D3), did not fire 1
(c23), not run 7. Independent-of-ancestor tests run: 0 -- every run above
is INSIDE the ancestor and the ledger says so.
Inherited-boundary rate by cut of introduction: CUT-1 20/23 = 0.87;
CUT-2 2/4 = 0.50; CUT-3 0/2 = 0.00 (both PERTURBED). The knife found
boundaries by intervention only after it was allowed to run something.
