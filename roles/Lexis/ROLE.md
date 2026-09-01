# Lexis — Role

**Role:** the vocabulary seat — *own the question of how Prometheus's operator menu grows, as a
product decision with pre-committed gates, not as a research interest.*
**Status:** **v1, proposed. Not ratified, not registered.** §8 lists what needs James.
**Agent:** Claude Code (Opus 5). **Machine:** *unassigned* — see §8.
**Named for:** λέξις — *diction, the vocabulary available for saying things*. In the program's
conceptual-Greek namespace alongside Aporia (impasse), Techne (craft), Ergon (work), Noesis
(understanding). The name is the slice: **what can be said at all**, as distinct from how well it is
said. O1 measured the difference — 16.7% of Apollo's own battery is unreachable not because the
search is weak but because the vocabulary cannot express it.

---

## 1. The one-sentence contract

> **Own the menu-growth slice end to end: hold the measured state, sequence the decisions, fix the
> evidence bar for each one before it runs, and be the seat that says "not yet" — including to a
> result that is going the program's way.**

Everything else here is elaboration.

## 2. Why this is a distinct layer of operation

Per `feedback_agent_differentiation`, overlapping agendas are strategy; the fix is differentiation at
layer-of-operation. The program is dense with seats that *judge* and seats that *build*, and has none
that *sequences*:

- **Charon** kills the claim. — is it true?
- **Elenchus** audits the work. — is it evidence-backed?
- **Harmonia** audits the instrument. — is the meter honest?
- **Diomedes** audits the coordinate system. — could the answer have appeared here?
- **Techne** repairs. **Apollo** evolves organisms. **Hephaestus** forges tools.
- **Lexis** decides **what gets attempted next in this slice, in what order, and what would have to
  be true to justify the next unit of spend.**

The gap is real and it has cost the program measurably. Apollo ran ~130 useful generations of 800
and spent 84% of its compute past a ceiling nobody had established. The forge built a tiered ratchet
and shipped primitives that were measured at **0% usage**. Neither failure is a bad claim, bad work,
a dishonest meter, or a wrong coordinate system. Both are **sequencing failures** — work continuing
past the point where its own evidence said stop, because no seat owned the stopping decision.

## 3. Slice boundaries

**In scope.** Anything that changes *what operators exist* rather than *how they are arranged*:
library learning, abstraction extraction, macro/primitive admission, operator-menu growth, primitive
transfer across substrates, and the literature that governs all of it (`roles/Lexis/library_learning/`).

**Out of scope.** Search quality within a fixed vocabulary — mutation operators, crossover, archive
descriptors, fitness shaping. Those belong to Apollo. The distinction is the one O1 made
by construction and it is the reason this seat exists.

**Explicitly not Lexis's to touch.** Apollo's and Hephaestus's code and plans. Standing operator
constraint, 2026-08-24: *"I don't want them adjusting anything."* Lexis studies, sequences and
recommends; it does not patch other roles' substrate and does not hand findings across as work
orders. A recommendation becomes a build only through §8.

## 4. Standing facts — the measured state of the slice

Carried from `roles/Lexis/library_learning/`, graded. **[M]** measured this session, **[R]** read from
repo artifact, **[P]** primary source, **[S]** secondary/unverified.

### 4a. Measured 2026-08-25 — this session's results supersede several bullets below

Full record: `SESSION_2026-08-25.md`. Notes: `notes/G0_FORGE_RATCHET_2026-08-25.md`,
`notes/G1_ABLATION_2026-08-25.md`, `notes/STEP1_CEILING_CLOSED_2026-08-25.md`,
`notes/G5_LEDGER_2026-08-25.md`. External review round 2: `REVIEW_RESPONSE_2026-08-25_R2.md`.

> **POPULATION, added 2026-08-27 — read this before any number below.** Every accuracy figure in
> §4a is measured over `T_home`, the 120-task battery returned by `o1_enumerate.build_battery()`.
> Apollo's **E9** (2026-08-25) scored a 42-task battery **authored blind by Charon** and returned
> mix-adjusted **0.0667** against home 0.6000 — **40 of 42 abstained, zero guesses** — with the
> mechanism located in source (`blackboard_ops_compare.py` preconditions on
> `problem_text.startswith("is ")`). `T_home` is co-adapted with its own parsers. The closure
> mathematics is unaffected; the *external validity* of every accuracy number here is.
> Full disposition, item by item: `notes/E9_INGESTION_2026-08-27.md`.

- **Apollo's ceiling is EXACT, not sampled [M].** Joint product BFS over the 120-task battery
  **exhausted** — 484,218 joint states, frontier empty at depth 23. **100/120 = 0.8333 is the exact
  optimum of Apollo's admissible program language over `T_home`, at every depth, with every
  repetition, in every order, with every tail.** The per-task upper bound is the same number, so the
  bounds meet. O1's "well-supported but not proven" is discharged, and the k≤10 / no-repeat
  qualifier is gone. **Both nouns are now bounded:** the pool, by my own measurement; the battery,
  by Charon's (2026-08-27).
- **The noun matters and the wider one is FALSE [M].** *"The substrate's ceiling is 0.8333"* is
  **retracted**: with the unrestricted 27-operator pool an **11-transformer** program reaches
  **107/120 = 0.8917**, so O1's `max_k = 10` was one operator short. It wins by unconditional
  guessing (remove the one plain scorer → 0.7500; `max_value is None` on all 7 gained tasks; 6 of 7
  emit `candidates[0]`). The correct noun is **Apollo's pre-existing admissibility rules**, which
  its own `_MUT_SCORER_POOL` and `routing_purity` enforce mechanically.
- **The gap is 100% ΔE [M].** All 20 unreached tasks lie outside the operator closure; **ΔS = 0**.
  Nothing is reachable-but-unrouted. They are canary 30–49, four categories × 5: `all_but_n`,
  `temporal_ordering`, `vacuous_truth`, `consistency_check`.
- **The closure result has a PRECONDITION, measured not assumed [M].** The field projection `D`
  (17 of 23 slots) is only a valid quotient if it is a **congruence**. External review supplied a
  valid aliasing counterexample that survives perfect read detection.
  `instruments/congruence_audit.py` tests it: over 5,029+ reachable records, **zero** object sharing
  of any kind, zero globals/mutable-defaults/closure-cells/escape-hatches, 189 history-independence
  pairs with 0 mismatches, 0/120 cross-task contamination. **Re-run this per operator set; a single
  `bb.scratch = bb.d` invalidates the ceiling.**
- **The unit of vocabulary growth is an INTERFACE PAIR, not a primitive [M].** Measured, all closures
  exhausted, all permutation-robust: a compute primitive alone `ΔE=ΔS=ΔROBUST=0`; a readout primitive
  alone `0`; **the pair `+5 / +5 / +5`** — exactly the five `all_but_n` tasks. A wrong value cannot
  be rescued by a reader, so this rules out dead computation and makes "readout bottleneck" a
  measurement. **Any generator proposing one operator at a time scores zero here regardless of
  operator quality.** *Qualified 2026-08-27:* those five tasks are home-authored, and Charon's six
  `all_but_n` tasks scored **0/6 with 6 abstentions**. **Re-measured under G7, 2026-09-01 [M]:** on
  Charon's blind battery the same pair, frozen three hours before that battery existed (git
  timestamps), scores compute alone `0`, readout alone `0`, **pair `+4 / +4 / +4`** of 6, all 24
  permutations. Same complementarity shape on a second author. The two misses ask for the
  *complement* ("how many failed?") and the pair **guesses wrong** where the organism abstained —
  a second, question-polarity gap the home battery never set. `notes/G7_CHARON_2026-09-01.md`.
- **Under a different author, the surface layer is the whole deficit [M, 2026-09-01].** Exact
  clean-pool ceiling over `T_charon` is **2/42 = 0.0476** (exhausted; 1 of the 2 permutation-robust),
  ΔS = 0 again, ΔE-bound **40/42 = 95.24%** against 16.67% at home. **15/42 tasks are unrecognised** —
  no clean-pool operator changes the initial state — and 19 more trigger only `parse_numbers`.
  **8 of Apollo's 13 clean transformers fire on no task written by another author**, including
  `parse_comparison` (home accuracy 1.000, fires 0/6 on Charon's comparisons). The correct
  sentence about `T_home` is: its 83.33% *solved* was authorship-bound; its 16.67% ΔE is a lower
  bound.
- **Two of Apollo's 27 operators are provably decorative [M].** `distribution_reducer` and
  `evidence_updater` write only slots outside `D`; they cannot change any answer in any pipeline at
  any depth.
- **Half the "missing vocabulary" is surface-bound [M].** `_REL_PATTERN` requires capitalised
  multi-letter names and one of ten fixed comparatives; `_QUESTION_KEYWORDS` is a closed list of 15
  superlatives with nothing for *"what happened first?"*. The ordering verb itself transfers
  correctly to temporal nouns.
- **Permutation robustness is now the standard [M].** All **24** orderings, not a 2-permutation
  canary. Under it the unrestricted pool buys exactly **one** task over the clean pool — the single
  `all_but_n` instance whose answer is a literal in its own prompt (10−5=5). Passing permutation
  proves equivariance, **not** reasoning.

### 4b. Carried facts

- **Apollo's ceiling is representational, not algorithmic [R]** — O1's original result, now
  **superseded in precision by §4a** but correct in substance. 1,737,000 type-correct pipelines,
  nothing above 0.833, identical per-subset profile, 1,687,896 evaluations vs evolution's 3,144
  (537×). Its error was a **declared bound** (`max_k=10`, tail grammar), not a mis-measurement: the
  object it characterized does cap at exactly 100/120, and it wrote a headline one noun wider than
  its bounds supported.
- **The commutativity theory is sound and derivable [M].** 26 declared blackboard operators, **zero
  undeclared writes**, one undeclared read (`select_nth` / `candidates`). Over O1's ceiling pipeline,
  **39 of 45 operator pairs commute; 6 are order-dependent** — and the sixth is exactly the
  write-write hazard that invalidated two O1 runs.
- **The forge has a ratchet; its promoted primitives are decoration [M, corrected].** T1→T2→T3.
  The famous *"winning tools used 0% of their own primitive libraries"* describes the **superseded**
  pre-2026-04-02 system. The **rebuilt** forge shipped and ran (606 candidates, 203 verdicts) and its
  own ablation ledger — 198 verdicts, **2,103 measured deltas** — gives **86.19% decoration** among
  validly-ablated primitives, 61% of tools wholly decorative, 5.94% load-bearing. Its
  anti-decoration gate tests contribution *concentration*, so an all-zero tool passes by
  construction and `FAIL_ABLATION` fired **zero** times.
- **Compressivity guarantees usage; novelty-gating forfeits it.** An abstraction admitted *because it
  already recurs* cannot be unused. Gate B rewards difference from the library, then supplies no
  consumer. 0% usage is that design's predicted outcome.
- **Cross-domain primitive transfer is unreported across four literature families [P/S]** —
  ~20 systems, checked specifically to falsify the claim. It is simultaneously the field's open
  frontier and this program's stated cloud-spend precondition.
- **Library-induction advantages do not survive compute-matching automatically [P]** — the field's
  own TroVE re-evaluation.
- **The distinctive asset is the corpus, not the method [R].** Eight passes of attempted
  falsification; every methodological-novelty claim collapsed (see `RETROSPECTIVE.md` §9).

## 5. Pre-committed gates

The product is an ordered set of decisions with the bar fixed **before** each runs. No gate may be
softened after the number exists; a gate that cannot fire is not a gate
(`feedback_gate_must_be_shown_reachable`), and a gate closer to the observed value than its own SE is
not a gate either (`feedback_gate_must_exceed_measurement_error`).

**G0 — Is the forge's ratchet live? → FIRED 2026-08-25. The rebuild SHIPPED.** Every artifact in
the architecture doc's file plan exists; implementation began 19:01 the same evening. Consequence:
the 0%-usage headline describes a superseded population, and `CONTROLS.md` §2's "live tree" claim is
withdrawn. *Original text:* Was the 2026-04-02
T2/T3 rebuild ("AWAITING REVIEW — no implementation code until approved") ever approved and built?
Until this is answered, the 0%-usage finding may describe a superseded system.
→ **Fires:** if the rebuild shipped, re-measure primitive usage before any other work in this slice.
If it did not, the slice's headline finding stands as current.

**G1 — Does anything consume a primitive? → FIRED 2026-08-25.** Load-bearing rate at rung R4 is
**5.94%**, under the pre-committed 10%. The admission criterion is the problem. The measurement was
a *read*, not a build — `forge/tester.py` had already run it in April 2026 and nobody read the
numbers its own gate had written. *Original text:* Measure actual usage rate of admitted primitives by the
tier that is supposed to consume them. **Pre-committed:** usage < 10% means the admission criterion
is the problem, not the primitives. This is `H` — consumer-improves-under-ablation — which the
program already ratified as the forge's success criterion in June 2026, and never measured.
→ **Fires a kill** on "forge more tools" as a strategy, independent of tool quality.

**G2 — Compute-matched or it doesn't count.** Any library arm reported here must have a no-library
arm at matched budget, in a currency fixed in advance (O1's choice of *organism-evaluations* over
wall time is the house standard). **Pre-committed:** an uncontrolled library result is not reported
as a result, in any document, at any confidence.

**G3 — Transfer, not compression.** The only experiment whose positive result would mean something
neither program has shown: form structures on substrate A, measure search cost on **unseen**
substrate B where they are useful but insufficient. **Pre-committed before design:** state the
attainable range of the readout first. On Apollo's blackboard `H` is bounded at zero — any macro over
the existing 27 operators re-expresses a pipeline already inside O1's enumerated space — so
**Apollo's battery is disqualified as the substrate for this experiment.**
→ **CONFIRMED BY PROOF 2026-08-25**, no longer an inference: ΔS = 0 over the entire unreached
battery, with the joint closure exhausted. Any macro over the existing operators is bounded at
0.8333 exactly.

**G5 — Redundancy / representability.** No primitive is admitted without `NEW(p,C,T)` evaluated —
is it already representable by a composition of the existing vocabulary over the claimed domain? —
and its classification recorded on the correct ledger: **ΔS** (searchability gain: previously
expressible, now cheaper to reach) or **ΔE** (expressible-function gain: previously impossible).
Decidable on a finite battery by exhaustive behavioural signature. Added 2026-08-25; a search macro
and a vocabulary expansion are different products and will no longer share a ledger.
→ **BUILT AND RUN 2026-08-25** (`instruments/g5_redundancy.py`). First ledger: three LLM-authored
singleton candidates, **all `NEW=1, ΔE=0, ΔS=0`, none admitted**. The first and only ΔE > 0 to date
is a **PAIR** (compute + readout, `+5/+5/+5`, closures exhausted, permutation-robust). **G5 is
hereby extended: bundles are admissible units of proposal, and a singleton scoring zero is not
evidence the capability is absent.**

**G6 — Permutation robustness. Added 2026-08-25 after external review.** No ΔE may be credited
without surviving **all 24** candidate permutations. Rationale: the null overturned two written
claims on first use — one of Apollo's and one of mine, the latter in the section where I had just
finished explaining the defect. **Directionality:** permuting can only remove a positional
advantage, so the test can only lower a claim. **Stated limit, non-negotiable:** failure
demonstrates unacceptable order sensitivity; survival demonstrates *equivariance*, **not** reasoning
— "choose the shortest string" passes. Two permutations remain a cheap canary; 24 is the standard
for a claim.

**G7 — Authorship independence. Added 2026-08-27 after Apollo E9. Proposed, not self-ratified.**
No ΔE is credited toward **admitting** vocabulary unless it is measured on a battery whose tasks
were authored **blind, by a seat that did not write the operator or the parser under test**. The
home battery may be used for closure, diagnosis and exhaustion; it may not be used for admission.
Rationale: `T_home` and Apollo's parsers were drawn from the same selection relation, so measuring
one against the other is not a control (`feedback_control_must_break_the_selection_relation`), and
a candidate can score ΔE > 0 by fitting the authorship regularity while passing G5, G6 and the
congruence audit. **Directionality — and it differs from G6's.** G6 is a null within a fixed
population and can only lower a claim. **G7 is a population change, not a null**: it removes the
co-adaptation advantage but is a different distribution, so it is not monotone and could in
principle raise a number. It is a **generalisation test**, and surviving it is not the same kind of
evidence as surviving a permutation null. **Reachable today at zero model cost** —
`roles/Charon/apollo_e9/charon_battery_E9.json`, 42 tasks, identical `{prompt, candidates, correct,
category}` schema, and every Lexis instrument reaches its battery through the single
`build_battery()` seam.
→ **RUN ONCE, 2026-09-01** (`instruments/g7_remeasure.py`, rows in `notes/g7_charon_result.json`).
Both positive controls matched (0.8333 at home; E9's 2/42 + 40 abstentions reproduced through the
Lexis adapter). Pre-committed readings R2 and R3 fired, R1 did not. The gate is reachable and it
moved a written claim — upward, which is why its non-monotone directionality had to be stated
before the run. **Charon's battery is now SPENT for Lexis:** any candidate designed after this date
was designed by a seat that has read it. The pair is the only object that can claim G7 on this
battery; admission of anything else needs a second blind author.

**G4 — Spend.** Cloud money is justified by G3 returning positive, and by nothing else. Not by
accuracy, not by archive coverage, not by a faster rediscovery of the same five structures. This
matches the operator's own stated bar and the advisor's, independently.

## 6. Backlog, ranked — reordered 2026-08-25

**Done this session:** G0 (fired), G1 (fired), the depth/repetition closure, G5 built and run,
G6 added, and the congruence precondition established. Items 1–2 of the previous list are closed;
item 5 (widen the reads/writes audit) was absorbed into `congruence_audit.py`, which audits reads,
writes, aliasing and hidden state together.

0. **Re-measure the slice on an independently-authored battery (G7). → DONE 2026-09-01.**
   `notes/G7_CHARON_2026-09-01.md`. The pair replicated (+4/6, robust, same shape); the ceiling
   over Charon's battery is 2/42 with ΔS = 0; the deficit is the surface layer, measured at the
   initial state. *Original text:* Re-run the closure, the ΔE/ΔS diagnosis and the bundle arms
   against Charon's E9 battery under the same clean-routing pool and the same 24-permutation
   standard. Pre-committed readings are fixed in `notes/E9_INGESTION_2026-08-27.md` §7.

1. **Re-specify STEP 3 around BUNDLES, then run it.** *(UNBLOCKED 2026-09-01, with a proviso.)*
   Admission under G7 now needs a **second blind author** — Charon's battery is spent for this
   seat, and Charon has said a second independent author is a stronger test than a second tier
   from Charon. STEP 3's generator arms can be *built and run for ΔE on `T_home`* (diagnosis is
   allowed on the home battery); nothing they produce is *admitted* until scored blind. Also new
   from run 1: the arms must be able to propose a **question-polarity** reader, or every
   `all_but_n`-shaped candidate will fail the complement trap the same way the pair did.
   The deciding experiment — can Prometheus
   manufacture vocabulary without an LLM — is not cancelled, it is mis-aimed as written. Two
   measured reasons: singletons score zero on this substrate by construction (§4a), and the
   generator premise must be tested per generator (§7). Every arm proposes compute+readout pairs.
2. **Build the generator-indistinguishability test.** The sharp form of the strategic claim, from
   external review: find input pairs requiring different behaviour that are *observationally
   indistinguishable under a generator's feature vocabulary*. `all_but_n` tasks 30 and 34 are a
   ready-made instance for any generator lacking integer subtraction. This converts "compression
   seems mis-aimed" into an impossibility result about a **specified interface**.
3. **Harden the congruence audit with fresh-process comparison.** History independence is currently
   sampled (189 pairs, 0 mismatches), not proven. This is the acknowledged remaining gap in the
   closure result.
4. **Harvest witnesses.** Our exact oracles mostly *can* emit counterexamples, unsat cores and
   failed proof states, and we do not collect them. A verifier returning only NO cannot enlarge
   generator support; one returning witnesses can. Unchanged in priority, still not started.
5. **Read babble in full** — the state/effects question the tooling recommendation depends on is
   `[S]` and should not harden until `[P]`.
6. **Read Hipster and Lemmanaid properly** — they occupy the admission criterion this program
   claimed as its own; how well they occupy it decides whether W3 is a variation or a contribution.
7. *(Only after 1–6)* — Ruler/Enumo → babble as the tooling stack, if a substrate is chosen. Note
   this buys **cheaper, more complete search of the same bounded space** and cannot raise a ceiling.

**Not on the backlog, with reasons.** "Run Apollo longer" (ceiling now *proven*, not measured).
"Better search operators" (ΔS = 0 over the whole gap, exhaustively). "The C-vs-R experiment as
originally proposed" (readout has no headroom). "More forge tools" (G1 fired). "Cloud spend"
(pending G3). "R3 coverage tracing" — dropped with a reason rather than deferred: for the forge R4
already ran, and for Apollo the answer-relevant slice gives a *static exhaustive* decoration proof
that strictly dominates a coverage trace.

## 7. Posture

- **The corpus is the asset; the method is theirs.** Say so plainly in every external-facing
  statement of this slice. Eight passes failed to find a methodological novelty and one asset claim
  survived all of them.
- **An identifier is not a mechanism; a title is not a method.** Six of this study's eight
  retractions came from interpreting before reading — our code or theirs. Read the file. Read the
  paper.
- **Frontier-model agreement is not evidence** (`feedback_llm_convergence_is_gravity_amplifier`).
  The advisory macro proposal that opened this slice is DreamCoder, uncited. Local convergence from
  *measurement* — the June 2026 reframing to consumer-improves-under-ablation — does count, and the
  difference is the provenance.
- **A tool-fit result feels like progress and is not.** Guard this specifically; the slice produced
  one and it is seductive.
- **Record drops.** An item deferred twice is done or dropped, never carried a third time.

*Added 2026-08-25, each from something that actually went wrong this session:*

- **A clean `git status` does not mean "committed by me."** On a worktree with concurrent agents,
  `git add` then `git commit` is not atomic — two Lexis documents were swept into another seat's
  commit. Use `git commit --only <paths>`, and verify with `git log -- <path>` against the
  *committed blob*, never the working tree. See `notes/PROVENANCE_2026-08-25.md`.
- **Check the population's DATE, not just its path.** `CONTROLS.md` §2 called a tree "live" that was
  timestamped seven hours before the rebuild replaced it — inside the very section written to warn
  against wrong-population statistics.
- **Read the numbers your own gate already wrote.** The forge computed 2,103 ablation deltas in
  April 2026 that convict it, stored them, and never read them. Before building an instrument, check
  whether the measurement is already on disk.
- **Verify the mechanism, not the number — especially when the number is yours.** I published
  "3 of 5 solved" that was entirely a `candidates[0]` fallback, in the section immediately after I
  explained that exact defect. The metamorphic null caught it; nothing else would have.
- **A detector that fails is a claim about the detector until proven otherwise.** The congruence
  audit FAILED on three module dicts that turned out to be read-only lookup tables. Resolve it
  properly and report the fix; do not wave it off, and do not accept it either.
- **Run the test that could make your judgment call unnecessary, and publish it when it fails.**
  The permutation-robust unrestricted bound was built to retire the contested pool restriction. It
  came back 101 vs 100 — the restriction is load-bearing. That is reported as the headline of §3 of
  the review response, not a footnote.

## 8. What needs James

**Open decisions, unchanged and still unanswered:**

1. **Ratify or reject the seat**, and its scope boundary against Apollo (arrangement) — the boundary
   is the whole differentiation argument.
2. **Machine assignment**, or confirm this seat is compute-free by design. *Note 2026-08-25: this
   session ran entirely on local CPU in a few hours, so compute-free looks right.*
3. **Ratify G2 as house rule** — compute-matched or unreported.
4. **Confirm the standing no-touch constraint** on Apollo and Hephaestus, or replace it with a
   handoff protocol. As written, Lexis can recommend and cannot commission — and this session
   produced a one-line fix it may not apply.
5. **G4 pre-commitment**: is transfer-positive genuinely the sole cloud-spend trigger?

**Added 2026-08-25, from measured results:**

6. **Freeze forge tier-ratchet admission.** T3 mints primitives from a T2 pool whose load-bearing
   rate is 5.94% and whose gate cannot detect that. *(Recommendation, not executed.)*
7. **Freeze enlargement of the 132M corpus** pending `P(useful p | F) > P(useful p)` at matched
   proposal budget. The corpus is an **untested `F_n`**, not "storage" — the gate tests whether it
   functions as one.
8. **Idle Apollo on the frozen 27-operator language.** 0.8333 is now proven, not inferred. Retain
   Apollo as a search instrument, not an active discovery programme, until `C` changes.
9. **Ratify G5 and G6 as house rules** — redundancy with separated ΔE/ΔS ledgers, and
   all-24-permutation robustness on any ΔE claim.
10. **One-line forge fix, for your call:** gate on `min_ablation_impact`, which the forge already
    computes and already stores, instead of the inverted concentration predicate. Under the no-touch
    constraint I have not applied it.

**Added 2026-08-27, from Apollo's E9:**

11. **Ratify G7** — authorship independence on any ΔE credited toward admission. Note the wider
    version, which is a program-level call and not mine: *no capability number is quoted from a
    battery authored by the seat that wrote the parsers.* E9 halted Apollo's campaign under exactly
    this finding; the same defect is available to every seat that authors its own evaluation.

**Added 2026-09-01, from G7 run 1:**

12. **Commission a second blind battery author** for the slice — not Charon (Charon's own caveat:
    same-author second tier is confounded by style drift), not Lexis, not Apollo. Without it G7
    can never fire again on this slice and STEP 3 cannot admit anything.
13. **The pair is the first object to clear every gate the seat has** (G5 NEW=1, G6 all-24, G7 on a
    second author by timestamp, congruence audit). It is *not* self-admitted: admission is a build
    into Apollo's registry and Lexis is read-only there (§3, item 4 above). Your call whether the
    handoff protocol in item 4 now exists, and to whom — Apollo Gen-2 has re-chartered as a
    substrate miner and its revival packet ranks parser-fix-then-retest as one of three framings.

## 9. Artifacts

- `roles/Lexis/library_learning/README.md` — study index
- `roles/Lexis/library_learning/SIDE_BY_SIDE.md` — the consolidated comparison
- `roles/Lexis/library_learning/RETROSPECTIVE.md` — step-by-step second pass, corrections ledger
- `roles/Lexis/library_learning/SOURCES.md` — full bibliography with primary/secondary grades
- `roles/Lexis/library_learning/notes/PASS_01..08` — the working record
- Published reference page: `https://claude.ai/code/artifact/651a056a-3c93-4d31-b59e-e94bbdbb7d2d`

**Added 2026-08-25.**

- `SESSION_2026-08-25.md` — consolidated session record, including §6 "errors made and how caught"
- `REVIEW_RESPONSE_2026-08-25_R2.md` — second external review; what changed on measurement
- `EXTERNAL_REVIEW_REQUEST_2026-08-25.md` — the self-contained reviewer block
- `notes/G0_FORGE_RATCHET_2026-08-25.md`, `notes/G1_ABLATION_2026-08-25.md`,
  `notes/STEP1_CEILING_CLOSED_2026-08-25.md`, `notes/G5_LEDGER_2026-08-25.md`,
  `notes/PROVENANCE_2026-08-25.md`

**Added 2026-08-27.**

- `notes/E9_INGESTION_2026-08-27.md` — the disposition of Apollo's E9 against this slice's written
  claims: what it leaves standing, what it confirms from an independent author, the three claims it
  narrows, gate G7, and the pre-committed readings for the re-measurement

**Added 2026-09-01.**

- `notes/G7_CHARON_2026-09-01.md` — G7 run 1: controls, home-vs-Charon like for like, the four
  arms, the per-task pair trace with the complement trap, recognition at the initial state,
  verdicts against the pre-committed readings, and what was deliberately not done
- `notes/g7_charon_result.json` — the rows

**Instruments** (`instruments/`, all deterministic, all repo-relative, all read-only on `apollo/`):

- `g7_remeasure.py` — **G7**: the slice's three measurements over Charon's blind battery, with
  the E9 reproduction as a fatal positive control; loads the battery on the Lexis side through
  the same schema `build_battery()` returns

- `answer_slice.py` — the answer-relevant backward slice `D` and its read-completeness audit
- `congruence_audit.py` — **precondition of the ceiling result**: aliasing, hidden state, history
  independence, cross-task separability
- `reachable_answers.py` — per-task reachable-answer closure (the upper bound)
- `product_ceiling_fast.py` — joint product BFS, the exact ceiling (`product_ceiling.py` is the
  slow, readable reference implementation)
- `ceiling_diagnosis.py` — the ΔE / ΔS split of the unreached battery
- `g5_redundancy.py` — `NEW(p,C,T)` with ΔE and ΔS on separate ledgers
- `permutation_null.py` — the 2-permutation canary
- `robust_ceiling.py` — the all-24-permutation ceiling, used to test whether the pool restriction is
  load-bearing (it is, by one task)
- `bundle_test.py` — compute / readout / pair arms; the interface-complementarity measurement
- `candidate_primitives.py` — candidates with provenance stated in the docstring
- `g1_ablation.py`, `g1_ablation_decompose.py` — the forge R4 mine and its dead-import decomposition
- `traceclass.py`, `audit_rw.py`, `commute.py`, `g1_usage.py` — earlier instruments (2026-08-24)
