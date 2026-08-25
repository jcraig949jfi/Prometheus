# Retrospective — a second pass over eight iterations, with hindsight

**Written:** 2026-08-24, after the loop stopped.
**Purpose:** the operator asked for a step-by-step account of what was done, what data it rested on,
what was concluded, and what stone was left unturned at each step. This is that account. It is
deliberately unkind to the earlier passes where they deserve it.

**How to read the evidence grades.** Every load-bearing claim below is graded:
**[M]** measured by me this session from primary artifacts; **[P]** primary source read directly;
**[S]** secondary — abstract or search summary only, unverified; **[R]** repository artifact read
directly. Full citations in `SOURCES.md`.

---

## 0. What triggered this, and the frame it arrived in

Aporia surfaced `arXiv:2006.08381` (DreamCoder) via a literature cross-reference. It arrived wrapped
in two interpretations that were already in tension:

- **Aporia + the frontier advisor:** the field scores abstractions by *compressivity* — cheap, and a
  proxy — whereas Apollo measures the *reachable ceiling by construction*, which is the thing
  compressivity approximates. Proposed experiment: measure `C(a)` compression gain, `R(a)`
  reachability gain, `H(a)` held-out downstream gain, and test whether `R` predicts `H` after
  conditioning on `C`.
- **Diomedes**, same day, in `RECON_2026-08-24_navigational_information.md` **[R]**:
  *"Program synthesis / DreamCoder-line library learning: the operator-menu-growth answer, already
  named in the ladder canon's H2 precondition 3."* And: *"We are not looking at a new idea; we are
  looking at a corpus that could test an old idea cheaply."*

**Hindsight verdict:** Diomedes was right, and the study spent five passes discovering it the hard
way. Every attempt to locate a methodological novelty on the Prometheus side collapsed under
examination (§2 corrections 1, 2, 5, 7 below, plus pass 8's correction to criterion 5). What did
*not* collapse — through eight passes and four literature families — is the corpus claim. The single
most efficient thing that could have happened is for the study to have started by trying to falsify
Diomedes' sentence, rather than by elaborating the advisor's framing.

**Stone left unturned at step 0:** nobody checked whether the *advisor's* proposal was itself
recalled from the literature rather than derived. It was. Pass 2 caught it, four hours late — the
macro mechanism the advisor "derives from Apollo's document alone" (typed inputs/outputs, frozen
internals, atomicity under mutation, retained provenance, recursive formation) is DreamCoder's
mechanism, specified accurately and uncited. Per `feedback_llm_convergence_is_gravity_amplifier`,
that is corpus gravity and must not be counted as independent validation. **It should have been the
first check, not an incidental finding.**

---

## 1. Pass 1 — lineage map

**What I did.** Fetched the four named nodes' abstract pages and two repositories; read
`apollo/README.md` and `apollo/ARCHITECTURE.md`; grepped the repo for prior mentions.

**Data obtained [P]:** DreamCoder's full author list and abstract; Stitch's POPL 2023 venue of record
(PACMPL 7, Article 41, pp. 1182–1213) and its headline — 3–4 orders of magnitude faster, 2 orders
less memory than DreamCoder's compression, *quality measured by compressivity*; LILO's three modules
and ICLR 2024 venue; Twitch's authors, IJCAR 2026 submission, and full method — the
`s(l=r) := |T(l=r)| / |l=r|²` interestingness score, k=50–100, the critical-pair weight modification
`w(Aσ) = w_A + Σ w(xσ)`, and the τ re-verification threshold. DreamCoder's architecture **[P]** from
`ec/docs/software-architecture.md`: OCaml backend / Python frontend, JSON over the process boundary,
`Program`/`Type`/`Grammar`/`Task`/`Frontier`.

**What I concluded.** That the delta was *compression of yesterday vs reachability of tomorrow*.

**What held.** The bibliographic and architectural facts. All of them.

**What did not.** The delta. Pass 3 killed it: both 2026 mathematics-facing nodes had already left
compressivity.

**The one thing pass 1 got right that mattered.** It went looking for the "Apollo measures the
reachable ceiling" machinery and **could not find it** — `apollo/ARCHITECTURE.md` contains no
occurrence of *reachable*, *ceiling*, *abstraction*, or *by construction*; it is a v2_d gradient-
recovery document describing a population at **0% raw accuracy** with LLM structural mutations
winning selection **0 times in 485 elite entries** **[R]**. Flagging that as `[UNVERIFIED]` rather
than proceeding on it is the reason the C-vs-R experiment did not get designed on a false premise.

**Stones left unturned:**
- `apollo/cycles/o1_enumeration/` appeared in pass 1's own grep output and was not opened until
  pass 2. **The single most important artifact in the study sat in a search result for a full pass.**
  A grep hit in a directory named after the exact experiment under discussion should be opened
  immediately, not queued.
- The repo-wide scan was launched with `head -20` per pattern and timed out at 120 s. It returned
  worktree duplicates and was never re-run scoped. Pass 8's finding that four literature families
  exist would not have come from the repo, but the habit — accepting a truncated scan as a scan — is
  the same one `feedback_prefix_sampling_invalidated_three_passes` warns about.

---

## 2. Pass 2 — the Apollo crossmap

**What I did.** Read the O1 preregistration, findings, and result JSON.

**Data obtained [R]:** O1 preregistered 2026-08-23 *before* the enumerator ran, stop rule ratified in
advance. Verdict `EVOLUTION_MORE_EFFICIENT` — enumeration reached 0.833 in **1,687,896** organism-
evaluations against evolution's **3,144**, a 537× ratio; kill condition did not fire. Secondary and
decisive: **enumeration's ceiling is also exactly 0.833, with an identical per-subset profile**
(canary 0.6 / synth 1.0 / inference 1.0 / cross_tier 1.0) across 1,737,000 pipelines in 3,000 s.
Apollo's own reading: *"0.833 is the substrate's ceiling, not evolution's… an expressivity limit,
now measured by construction rather than inferred from a plateau."*

**What I concluded.** That Apollo had measured, one day early, the exact wall the DreamCoder lineage
exists to break — a coincidence of timing, not causation.

**What held.** This. It is the study's central structural finding and nothing in six subsequent
passes touched it.

**What did not.** Two things.
- I wrote that the transfer experiment "has positive prior art in the literature." **Wrong** —
  within-domain reuse has prior art; cross-domain transfer does not (pass 3, confirmed pass 8 across
  four families).
- I framed llm2's zero-lift result as possibly explained by a flat landscape. The sharper and correct
  statement: llm2 mutated *a flat list of operator names*, so it could only reorder existing
  operators. It tested LLM-as-arrangement-mutator, never LLM-as-primitive-author — on a substrate
  where the menu cannot grow **[R]**. H2 precondition 3 cites it for a claim about menu growth. The
  conclusion may hold; that evidence does not reach it.

**What pass 2 established that should not be lost.** The C-vs-R experiment as proposed **is not
runnable on Apollo**: `H` has no headroom, because any macro built from the existing 27 operators is
a re-expression of a pipeline already inside O1's enumerated space, so downstream gain on that
battery is bounded at zero. A readout whose attainable range excludes the effect is not a readout —
`feedback_gate_must_be_shown_reachable`, applied to an experiment design rather than a threshold.

**Stone left unturned:** I read O1's `FINDINGS.md` and quoted its *limits* section — "k ≤ 10, 48
orderings per subset, some subsets have 166,320" — without asking what that ratio implied. The
166,320/45,360 numbers were on the page in pass 2 and their significance was not extracted until
pass 5. **Three passes of latency on a number I had already read and quoted.**

---

## 3. Pass 3 — widening, and the first real correction

**What I did.** Searched for who cites Stitch; fetched DreamProver, the TroVE re-evaluation, and
LaSR.

**Data obtained [P]:** DreamProver — Lean+Mathlib, wake/sleep, admission by semantic K-Means
clustering + provability under a small sampling budget + tree-edit-distance deduplication + LRU
eviction + hard cap under 100 lemmas; +61% average over Hilbert (+114% number theory, +50%
combinatorics, +20% inequalities), 48% fewer output tokens, 50% shorter proofs, **58% of learned
lemmas reused on test sets contributing to 71% of all proofs**; and — decisively — **no cross-domain
transfer reported, each domain gets its own library**. TroVE re-evaluation **[P]**: compute-matching
dissolves the library-induction advantage on MATH.

**What I concluded.** Three things, all of which held: the admission-criterion taxonomy is plural,
not compression-monolithic; cross-domain transfer is the field's open frontier *and* our spend gate;
and any result here needs a compute-matched control in a currency fixed in advance.

**What did not hold.** I read `gene_extractor.py`'s *docstring* and reported that Prometheus already
had the O4 macro mechanism in prototype. That was reading a filename and a comment, not a program.

**Stone left unturned:** the correction above was available in the same pass. I had already grepped
`_create_macro_gene` and `compute_portability_score` **and read the line numbers of their
definitions** without opening either function. Reporting on a mechanism from its identifiers is the
same error as reporting on a paper from its title.

---

## 4. Pass 4 — reading the code, and the first genuinely useful finding

**What I did.** Read `gene_extractor.py` in full; read `RESULT.json`'s config; fetched babble.

**Data obtained [R]:** `compute_portability_score` starts at 1.0 and subtracts −0.3 for string
literals ≥ 20 chars, −0.2 for >3 English pattern words, −0.3 for off-convention `ctx[…]` keys, −0.2
for regexes with arguments >30 chars. **It never reads a corpus.** And the macro branch fires on
`avg_portability < 0.4 and len(non_utility) > 2`, hardcoding `portability_score=0.3` — a macro is
created *because the tool scored badly*.

**What I concluded.** Correction 2 (above). And, newly: Stitch is the wrong tool because it consumes
lambda terms and prunes syntactically, while an Apollo pipeline is state-mutating — but **babble**
does library learning modulo an equational theory, and O1's own 166,320-orderings / 45,360-reaching
number *is* an equivalence class.

**What held.** Both. Pass 8 extended the second: the full recommendation is Ruler/Enumo → babble, not
babble alone.

**Stone left unturned:** I recommended a tool on architecture fit without fetching babble's full
text. `SOURCES.md` records babble as **[S]**. Whether it handles effects/state — the exact property
the recommendation depends on — **is still unverified**. That should have been the next fetch and
was not.

**A process note worth keeping.** Pass 4 also formally *dropped* the Twitch rating-1 vs rating ≥ 0.9
discrepancy after four deferrals, rather than carrying it silently forever. Recording a drop is
better than letting an item decay. But four deferrals is three too many: an item that keeps losing
priority should be either done or dropped on its second appearance.

---

## 5. Pass 5 — the measurement

**What I did.** Wrote two read-only AST instruments (`audit_rw.py`, `commute.py`) and ran them
against `apollo/src/blackboard_ops*.py`. Nothing in Apollo was modified.

**Data measured [M]:**
- **26 declared operators. Zero undeclared writes. One undeclared read** (`select_nth` reads
  `state.candidates` without declaring it).
- Over the ten transformers of O1's ceiling pipeline: **39 of 45 operator pairs commute freely; 6 are
  order-dependent.** The six: `parse_box_items → op_aggregate_quantities` (`counts`);
  `parse_rules → forward_chain` (`facts`, `rules`); `forward_chain → relations_from_facts`
  (`derived_facts`); `parse_names_and_relations → op_build_ordering` (`relations`);
  `relations_from_facts → op_build_ordering` (`relations`); and the write-write hazard
  `parse_names_and_relations ⟷ relations_from_facts` on `relations`.

**What I concluded.** The commutativity theory is sound (zero undeclared writes ⇒ Bernstein's
conditions cannot miss a hazard). And the sixth constraint **is exactly the bug that invalidated two
of O1's runs** — statically derivable from decorators already in the tree.

**What held.** All of it. This is the study's only original measurement.

**What I was careful about, correctly.** I stated explicitly that 39/45 is a *pairwise commutation
count, not a compression ratio*, and did not compute the equivalence-class count (which needs
modelling O1's dataflow applicability rule and is a trace-counting problem). Quoting it as "87% fewer
programs" would have been the natural over-claim.

**And the guard that mattered most.** Pass 5 closes by insisting that all of this makes search over
the *same bounded space* cheaper — a better abstraction tool over a substrate capped at 0.833 by
construction still cannot exceed 0.833. Tool-fit results feel like progress toward the goal. They are
not.

**Stone left unturned:** the audit covered `blackboard_ops*.py` only. Operators registered elsewhere
— `blackboard_evolve.py` maps names to functions including quarantined v1 answer-producers — were not
audited. The "zero undeclared writes" claim is scoped to the files audited, and pass 5 said so, but
the scope should have been widened rather than annotated.

---

## 6. Pass 6 — consolidation

**What I did.** Fetched LILO's repository and DreamProver's decomposition mechanism; wrote
`SIDE_BY_SIDE.md`; designed and published the artifact.

**Data obtained [P/S]:** LILO's AutoDoc feeds documented libraries back as **few-shot context for the
synthesizer** **[S]**; DreamProver's recursive decomposition — sketch → extract `sorry` holes as
standalone theorems → LLM-validate → formally verify → admit to library; on failure, inform the next
wake-sleep cycle rather than retry with more budget **[P]**.

**What I concluded.** Correction 4: AutoDoc is *not* the cheap steal I called it in pass 1, because
Apollo has no LLM consumer of its library. And the crossover/decomposition comparison, which answers
Apollo's own §9.2 question: crossover jumps *within* a vocabulary, decomposition grows the vocabulary
*from a failure*.

**What did not hold.** `SIDE_BY_SIDE.md` asserted "There is no ratchet," citing `genome.py`. True of
Apollo. **False of the forge**, whose README opens with *"The forge is an evolutionary ratchet. Each
tier's output becomes the next tier's primitives."*

**Stone left unturned — the worst one in the study.** The operator's original instruction named
**"Apollo, Hephaestus, forge."** Six passes examined Apollo. `forge/README.md` is 137 lines and its
first substantive sentence is the one that falsifies the deliverable's opening claim. **The
instruction contained the pointer and I did not follow it for six passes.** This is not a subtle
miss; it is a failure to read the brief.

---

## 7. Pass 7 — the forge half

**What I did.** Read `forge/README.md`, `forge/ARCHITECTURE_T2_T3.md`,
`forge/STATUS_T1_T2_20260403.md`, `agents/hephaestus/README.md`, `agents/hephaestus/STATUS.md`.

**Data obtained [R]:**
- The tiering: T1 forges from scratch with **no primitives available**; T2's primitives are all
  passing T1 tools; T3's are all passing T1+T2 tools plus Frame H's 27 building blocks.
- From the T2/T3 failure analysis: **"Winning tools used 0% of their own primitive libraries —
  primitives were decoration."** Alongside: same session saw tests and wrote tools (answer-key
  construction); 93% hand-coded regex/if-blocks; 100% scores collapsing to 79–96% under seed
  variation; no diversity enforcement; no pre-committed thresholds.
- Gate A: beat the NCD baseline (42% accuracy, 46% calibration). **Gate B: structural novelty**,
  explicitly rewarding difference from the library.
- T1 coverage 80/89 categories, best tool 55.91%. T2: 7/77 evaluated tools passing (9.1%) — two
  gem-forged at 97.5%/96.7% with 8.3pp seed drops, five at 40–45% reaching passing status via
  **threshold recalibration**, with 12.5–16.7pp seed drops.
- The 2026-06-22/23 reassessment: *"'The forge succeeding' no longer means 'pass a gate'; it means a
  consumer measurably improves because of your output, and that survives ablation."*

**What I concluded, and it is the study's sharpest inference.** **Compressivity guarantees usage by
construction; novelty-gating forfeits it.** An abstraction admitted *because it already recurs* cannot
be unused — usage is the evidence that promoted it, observed before promotion. Gate B promotes what
does *not* recur, then places it in the next tier's pool with nothing connecting admission to use.
0% usage is that design's predicted outcome, and it is what was measured.

**And a genuine convergence.** The June 2026 reframing to consumer-improves-under-ablation is
held-out downstream gain as the admission criterion — the exact fix — reached from local failure
analysis two months before this contact. Unlike the advisor's macro proposal, it did not come from
the corpus. It counts.

**Stone left unturned:** I did not check whether the T2/T3 rebuild — dated 2026-04-02 and marked
*"AWAITING REVIEW — no implementation code until approved"* — was ever approved or built. The
0%-usage finding is about the *previous* attempt. Whether the Five Iron Laws shipped is unknown, and
it changes what the finding means today. **This is the highest-value open item in the study.**

---

## 8. Pass 8 — the wider survey

**What I did.** Searched deliberately outside the single lineage.

**Data obtained [S, mostly]:** four families exist — MIT library learning (A), UW e-graphs (B),
Chalmers theory exploration (C), LLM tool/skill libraries (D). Ruler infers rewrite rules; Enumo
makes theory exploration programmable and handles undecidable equality; ShapeCoder discovers
abstractions from *unstructured primitives*; Hipster has a **proof mode** that finds the missing
lemmas needed for *the current goal*; Lemmanaid has an LLM generate lemma **templates** with symbolic
methods filling details; ReGAL verifies abstractions **via execution**; LATM splits tool-maker from
tool-user; Voyager admits skills by **self-verification of task success** with relevance retrieval.

**What it overturned.** Criterion 5 — "verifier-gated correctness from a typed diagnosis" — was
claimed as unoccupied in passes 3, 6, and the deliverable. **Hipster's proof mode has occupied it
since 2014, and Lemmanaid occupies the LLM-template half.** What survives is the narrower claim:
the *mechanism* is theirs; the *corpus* is ours.

**What it confirmed by failing to falsify.** Cross-domain transfer is unreported across four families
and roughly twenty systems. This was checked *specifically to try to break it* and it did not break.

**Stone left unturned:** most of this pass is **[S]**. The Hipster correction rests on a secondary
source — adequate to withdraw an over-claim (the correct response to "someone may already occupy
this" is to stop claiming novelty), inadequate to build on.

---

## 9. The corrections ledger, consolidated

Eight claims made and withdrawn across eight passes:

1. **P1–2:** "compression of yesterday vs reachability of tomorrow is the delta" → both 2026
   mathematics nodes had already left compressivity.
2. **P3:** "`gene_extractor.py` already contains the O4 macro mechanism" → it inverts the logic;
   macros are a containment strategy for un-portable code.
3. **P1:** "llm2's zero-lift may be a flat-landscape artifact" → sharper: llm2 could only reorder,
   never author; it never tested menu growth at all.
4. **P1:** "AutoDoc is the cheapest steal" → not for Apollo, which has no LLM consumer. It lands on
   the forge.
5. **P2:** "the transfer experiment has positive prior art" → within-domain does; cross-domain does
   not.
6. **P2:** "the C-vs-R experiment is the thing to run" → not runnable on Apollo; `H` has no headroom.
7. **P6:** "There is no ratchet" → true of Apollo, false of the forge — whose ratchet exists and was
   measured at 0% primitive usage.
8. **P3/P6:** "verifier-gated admission from a typed diagnosis is unoccupied in that lineage" →
   Hipster's proof mode (2014) and Lemmanaid occupy it.

**Pattern across all eight.** Six of the eight are the same error: **claiming Prometheus novelty
without having read the thing being compared** — either our own code (2, 3, 7) or theirs (1, 5, 8).
The two exceptions (4, 6) are errors of scope, where a true statement was applied to the wrong
target. There is no instance of a *measurement* being wrong. Every retraction is of an
*interpretation* made before the relevant artifact was read.

**The operational lesson.** This study's error rate was not driven by insufficient analysis. It was
driven by analysing before reading. Each correction arrived when — and only when — I opened the file
or the paper. `feedback_assume_wrong` covers the posture; what this adds is the specific failure
shape: *an identifier is not a mechanism, and a title is not a method.*

---

## 10. What survived everything

Stated plainly, with grades:

- **0.833 is an expressivity ceiling of Apollo's blackboard substrate, measured by exhaustive
  enumeration [R].** 16.7% unreachable by any composition of at most 10 transformers without operator
  repetition. **Scope corrected 2026-08-25** after external review: this is a *bounded-language*
  ceiling, not an expressivity ceiling. The ordering axis is now exhaustive — 166,320 valid orderings
  collapse to exactly 4 trace classes, and the 45,360 reaching 0.833 are exactly one class. Depth and
  repetition bounds remain part of the hypothesis.
- **39 of 45 operator pairs in O1's ceiling pipeline commute; zero undeclared writes across 26
  declared operators [M].** The commutativity theory is derivable and sound; the bug that voided two
  O1 runs was statically derivable.
- **The forge has a tiered ratchet whose promoted primitives were measured at 0% usage [R]** — and
  compressivity would have prevented that by construction, while novelty-gating invites it.
- **Cross-domain transfer of learned primitives is unreported across four families [P/S]**, and is
  the stated cloud-spend precondition.
- **Library-induction advantages do not automatically survive compute-matching [P]** — the field's
  own re-evaluation of TroVE.
- **The distinctive Prometheus asset is the corpus, not the method [R + eight passes of failed
  falsification].**

## 11. Open items, ranked

1. **Was the T2/T3 rebuild ever approved and built?** Changes what the 0%-usage finding means today.
   Local, cheap, unchecked.
2. **Read babble's full text** — the state/effects question the pass-4/5 recommendation depends on.
3. **Read Hipster and Lemmanaid properly** — they occupy the criterion we claimed; how well they
   occupy it decides whether W3 is a variation or a contribution.
4. **Widen the reads/writes audit** beyond `blackboard_ops*.py`.
5. Stitch's formal utility definition — two failed fetches; low priority, nothing rests on it.
6. Twitch rating-1 vs rating ≥ 0.9 — formally dropped; reopen only if Twitch becomes load-bearing.
