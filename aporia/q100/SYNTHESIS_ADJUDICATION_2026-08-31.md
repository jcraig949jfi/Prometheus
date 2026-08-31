# Three syntheses, three corpora — adjudicated

**2026-08-31, Aporia.** DeepSeek, Gemini and ChatGPT were each asked whether their list's
questions intersect mathematically. This adjudicates the three answers.

---

## 1. First: they are not three answers to one question

**Each model synthesised a different corpus, and none says so.**

- **DeepSeek** synthesised **L4** — its own 100 questions.
- **Gemini** synthesised **L3** — its own 50.
- **ChatGPT** synthesised **L1** — the operator list. Confirmed, not assumed: its citations
  (#7, #15, #29, #31, #46, #55 for quotients; #2, #24, #39, #40, #45, #47 for the
  search/representation boundary) all land on L1 content, and **#55 is beyond Gemini's 50-row
  list**, so it cannot be describing L3.

Reading the three as convergent or divergent is therefore a category error. They are three
taxonomies of three different objects. Any impression that "the models agree" is an artifact of
comparing unlike things.

## 2. The empirical check on the shared-core claim

All three assert a small shared mathematical core underneath their list. That claim has a
testable consequence: **if a tight core generates these questions, independently generated lists
should converge on it.**

Measured (`OVERLAP_ANALYSIS_2026-08-31.md`): L1 and L2 have a **strong** counterpart for 32% and
37% of their rows respectively, and the disagreement is structured by discipline lineage — L2 is
nearly silent on formal deduction (2/10) and analogical reasoning (**0/2**); L1 is nearly silent
on scaling (1/8) and grounding (2/8).

**So a synthesis of one list cannot be validated by that list.** Each model found a coherent core
in its own sample, and the samples do not agree. That is consistent with each generator
projecting a real core differently — but it is equally consistent with a narrative imposed
post hoc on a heterogeneous set, and the data here cannot separate those.

## 3. Ranking, with the reason

**ChatGPT's is the strongest, and it is the one to be most careful with.**

It is the only one that is *checkable*: it names specific rows and makes structural claims that
can be tested against them. I tested all twelve. They land. **L1-055 is literally a bisimulation
quotient** — "an equivalence relation over reasoning states that preserves all future
solution-relevant information" — so the quotient-space claim is supported by actual list content
rather than by vocabulary.

**And that is exactly why the gravity warning applies hardest to it.** ChatGPT writes: *"this is
precisely why I think your Prometheus framing keeps circling representation, failure geometry,
operator invention and navigability."* That is the advisor restating the programme's own thesis
in the programme's own words. Per `feedback_llm_convergence_is_gravity_amplifier`, and with an
exact precedent in this repo — Lexis pass 2 found the advisor's macro mechanism, presented as
"derived from Apollo's document alone", was DreamCoder's mechanism specified accurately and
uncited — **agreement between this synthesis and the charter is not independent validation.**

The parts that survive the warning are the parts with row-level citations that check out. The
part that does not survive is the closing frame.

**Gemini's is the weakest, and the reason is evidenced rather than stylistic.** It asserts a
single monolithic thesis — topological incompatibility between continuous vector spaces and
discrete algebraic structure — that is (a) unfalsifiable as stated, (b) a claim about *neural
networks* while its own list contains many questions that are not about neural networks, and (c)
the same signature as the list it describes. That list measured **28% theorem-blocked and 84%
unreachable**. Sweeping, confident, unmeasured, in both the questions and the synthesis of them.

**DeepSeek's is honest and low-information.** Its ten clusters map closely onto the thirteen
category labels it had already assigned, so it is largely a taxonomy of its own taxonomy. Nothing
in it is wrong; little in it is new. Consistent with its list being the best-posed of the four —
**16% blocked, 76% reachable** — and the least in need of reinterpretation.

## 4. Where the best synthesis is missing the binding constraint

ChatGPT's §4 states basis discovery as: find a basis B such that `G(B) ≈ G(A)`, "or ideally
exceed them after discovering a new primitive p: `G(B ∪ {p}) ⊋ G(B)`."

**That proper superset is impossible for any p that is itself a composition of B.**
`AMENDMENT_1_LEVELS_AND_INSTRUMENT_RULE_2026-08-27.md` killed it: `G(C ∪ {M}) = G(C)`
extensionally, so M adds a name and not a denotation. Corroborated 2026-08-31 from primary text —
DreamCoder's own figure caption (*"Equivalent programs could in principle be written in the
starting language"*), Stitch defining each new terminal as *"semantically equivalent to"* a closed
lambda term, LILO's full text containing zero occurrences of `expressiv*` or `conservative`.

So the strongest of the three syntheses reaches the right mathematical object and **states it
without the constraint that makes it hard.** Prometheus is ahead of the synthesis on exactly this
point, with a committed kill and external corroboration.

## 5. The one place agreement is NOT gravity

ChatGPT: *"#45 may secretly be one of the most important questions in the set."*

I triaged L1-Q045 to Tier B **earlier the same day**, before this synthesis existed, with the
note that D-4's per-episode viable-only oracle may be the cleanest existing instrument for it:

    substrate   achieved far   oracle far-reach   attribution
    S1_REG      0.00-0.02      0.41               SEARCH weakness at this budget
    S3_REWRITE  0.00           0.00               TOPOLOGY failure

That convergence has an ordering in git and was reached from a different direction — the
substrate side, not the taxonomy side. It is the only agreement in this whole exchange that is
not corpus gravity, and it points at the same question.

## 6. The actionable result: ChatGPT's killer experiment is runnable here, with one correction

Proposed: *"a controlled universe where we know the initial basis is insufficient, know exactly
what representational transformation makes the problem tractable, and ask whether a system can
infer that transformation from the geometry of its failures alone."*

**We have the pieces.**

- **The world.** TINYPROG (`aporia/lot/world3.py`) — WORLD_ADMISSIBLE on five never-before-
  generated seeds, five nuisance-matched classes, 734x search headroom, language-free by
  construction (metamorphic relabelling leaves every reading bit-identical).
- **The discriminator.** D-4's viable-only oracle already separates search failure from topology
  failure on real substrates.
- **The certificate.** `build_closure()` returns `minsize` per extensional signature, so
  "not reproducible within bound k" is *certified* rather than asserted — the test the entire
  library-learning literature has never executed.

**The correction, and it is the whole validity of the experiment: the planted transformation must
be Level 2 — non-conservative.** A new type constructor, a new oracle, recursion, quantification,
or variable binding. If you plant a *composition* as the "representational transformation the
system must discover", the system can at best find a search shortcut, and you will measure
**search compression and call it representational change** — which is precisely the error the
whole surveyed literature makes, and which Amendment 1 forbids naming as widening.

Stated as the design rule: **plant a transformation whose signature has `minsize > k` in the
frozen closure, or the experiment cannot distinguish the two hypotheses it exists to separate.**

## 7. Disposition

- The three syntheses are recorded, not adopted. None is evidence about the field; each is a
  description of one generator's sample.
- ChatGPT's quotient and search-vs-representation observations are **promoted to loop content**
  because they are row-checkable and they checked out. Its closing frame is **not**, because it
  is the programme's own thesis returned.
- The basis-discovery correction (§4) is the standing amendment any future use of this frame must
  carry.
- The killer experiment (§6) is the strongest single candidate the Q100 loop has produced. It is
  the A3 rung with a sharper design constraint than A3 currently carries, and it should be
  preregistered before it is built.
