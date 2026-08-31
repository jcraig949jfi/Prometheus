# Dossier — Q047 / Q060 / Q100 (with Q002, Q005): operator invention and expressivity growth

**Pass 1 of the Q100 loop.** 2026-08-31, Aporia. Research run `wf_17f1a37b-646` (104 agents,
22 sources, 104 claims extracted, 25 verified, 21 confirmed, 4 killed, 12 after synthesis).

**Questions covered:** Q002 lemma invention · Q005 proof abstractions · Q047 infer a missing
primitive · Q060 prove strictly increased expressivity · Q100 metabolize failure into new
reachable discoveries.

---

## 1. TRIAGE — headline

**The decisive test in this cluster has never been executed by anyone, and Prometheus already
owns the machinery to execute it.**

Q060's T2 — *exhaustively search bounded compositions of the existing operators; PASS if the
new operator's behaviour is NOT reproducible within the bound* — **does not appear anywhere in
the verified corpus.** Across DreamCoder, Stitch, babble, LILO and ShapeCoder, novelty is
either asserted or replaced by a compression/utility criterion. Admission rules are
compression-only, verbatim: DreamCoder — *"Program components that best increase a Bayesian
objective … are incorporated into the library, until no further increase in probability is
possible"*; ShapeCoder — *"if F(L', P') is better than F(L, P), both L and P are replaced."*

## 2. PRIOR ART — what was actually measured

**Two proxies, never expressivity or reachability.**

*Compression branch* (Stitch, babble, ShapeCoder): description-length reduction only. Stitch
measures quality *"as measured by compressivity"*; the word "downstream" occurs zero times and
no tasks-solved number appears anywhere. babble: *"we follow DreamCoder and use compression as
a metric for library learning."* ShapeCoder optimises a hand-weighted token-count objective
with hand-set constants.

*Solve-rate branch* (DreamCoder, LILO): solve rate and wall-clock under a bounded budget — a
**search-efficiency** result, not a reachability result. DreamCoder text editing 3.7% solved in
10 min (mean search 235s) before learning, 79.6% after (mean 40s); ~100% LOGO and towers; 93%
of 60 physics laws. LILO online: REGEX 77.07±14.14 vs DreamCoder 43.93±1.53; CLEVR 96.76±3.12
vs 94.50±2.44; LOGO 48.95±22.15 vs 28.53±13.79.

**Historical precedent (1994):** Koza's ADFs were certified by *search cost* — the
"computational effort" statistic — with a secondary parsimony criterion, and Koza devoted a
chapter to problems straddling the breakeven point **where ADFs do not pay off.** The honest
version of this result is thirty years old.

**Compression collapses off its home domain.** babble reaches 4.07–9.23 (no equational theory)
and 4.56–10.90 (with) on 2d CAD — Nuts & Bolts 19,009 → 1,744 AST nodes, CR 10.90 — but on
DreamCoder's own five domains the ratios fall to roughly **1.0–1.4** (List/Text), ~1.5 (Logo),
~1.8 (Towers), ~2.6 (Physics).

## 3. THE DEFINITIONAL OBJECTION IS CONCEDED IN THE PRIMARY TEXT

`AMENDMENT_1_LEVELS_AND_INSTRUMENT_RULE_2026-08-27.md` killed the widening claim on the
argument that `G(C ∪ {M}) = G(C)` extensionally when M is a composition, so M adds a **name**
and not a denotation. That argument is now externally corroborated — **by the primary sources
themselves**:

- **DreamCoder**, Fig. 1B caption, verbatim: *"Equivalent programs could in principle be
  written in the starting language, but those produced by the final learned language are more
  interpretable and much shorter."* An explicit disclaimer of extensional gain, relocating the
  benefit to interpretability and program length.
- **Stitch**, defining the new library symbol: *"We introduce a new terminal symbol t_A into
  the symbol grammar to represent the abstraction, and consider it semantically equivalent to
  (λα_0. … λα_k. A)."* A new terminal defined as semantically equivalent to a closed lambda
  term over existing primitives **is a definitional extension by construction.**
- **LILO**: library re-derived as `L <- L0 ∪ {f1..fk}` each iteration; abstractions *"ground
  out in the base DSL primitives"*; grep of the full text returns **zero** occurrences of
  `expressiv*` and **zero** of `conservative`.
- **ShapeCoder**: abstractions can only restrict parameter ranges, so the relation is strictly
  `G(C ∪ {M}) ⊆ G(C)`.

**Honesty caveat, carried:** "concedes" is our framing. DreamCoder states this descriptively in
a figure caption and **never engages the conservative-extension literature by name.** Nobody in
this branch draws the consequence — that a compression result cannot be an expressivity result.

**Consequence for Q047 and Q060 as written:** both are only passable at Level 2 —
non-conservative semantic extension. The literature they are aimed at operates at Level 0 and
reports compression. **The questions and the field are measuring different things.**

## 4. THE NEAREST EXISTING MACHINERY, AND WHY IT IS NOT A CERTIFICATE

Enumo's **derivability**: a candidate rule is redundant iff bounded equality saturation over
the existing ruleset merges the two sides. Three defects as a non-redundancy certificate:

1. **Bound-relative** — node/iteration/time/match limits, not exhaustive over compositions.
2. **Metric-dependent** — Enumo formalises two definitions (LHS and LHS-RHS) that **disagree on
   whether the same rule is redundant**; prior work (Ruler) used the looser LHS-RHS. Before
   2023 there was no standard definition at all.
3. **Circular** — derivability doubles as both the minimisation criterion and the
   ruleset-quality metric.

The strongest novelty evidence in the whole corpus is **asymmetric bidirectional derivability**,
not non-reproducibility: Enumo rulesets derive 100% of Ruler's rules in bool/bv4/bv32, while
Ruler's derive back only 38.3% (bv4, LHS), 58.3% (bv32), 62.6% (rational), 87.5% (bool).

Where bounded exhaustive search *does* exist in this literature it points the opposite way —
DreamCoder's version-space algebra enumerates refactorings that **are** reachable; Stitch's only
exhaustive step is over `2^|Matches|` rewrite subsets; ShapeCoder's e-graph saturation finds
where abstractions apply. And Stitch's pruning is **provably lossless** (Lemma 1), so the
missing certificate is not caused by incomplete search — it is caused by the candidate space
being corpus-subtree-derived and the objective being compression.

ShapeCoder's limitations section admits the opposite of non-redundancy outright: *"We find
multiple abstractions that explain the same concept … the abstracted programs can feel
redundant for downstream tasks."*

## 5. FALSIFICATION BATTERY — what the field runs, and the four controls it never runs

**Standard:** ablation of the system's own components; comparison against prior systems.
**Occasional:** compute-heavy enumeration baselines and two Memorize baselines (DreamCoder,
enumeration at 24h/task generating up to 400M programs); one dataset perturbation (babble).

**ABSENT FROM EVERY PAPER CHECKED:** random-library controls · shuffled-history / order-scrambled
controls · frequency-matched arbitrary-chunk controls · compute-matched baselines. These are
*precisely* the controls that separate library CONTENT from library PRESENCE.

Compute is not merely unmatched but explicitly mismatched: *"We ran babble … at 2.0 GHz. Each
benchmark was run on a single core. The DreamCoder results were taken from the benchmark
repository; DreamCoder was run on 8 cores … at 3.0 GHz."*

**And the marginal contribution is weakly resolved.** LILO's gains over an LLM Solver + Search
baseline are within one standard deviation in **all three** domains — LOGO's 11.11pp gap is
smaller than LILO's own SD there (22.15). DreamCoder's library alone already delivers most of
the offline-synthesis gain in two of three domains.

**PROMETHEUS ALREADY RAN TWO OF THE FOUR MISSING CONTROLS.** `agent_d5_blind` ran
**random-library** (size-matched random-walk genotypes, refreshed at the same admission points)
and **shuffled-history** (task order permuted so artifacts arrive out of correspondence), plus
no-history and frozen-half, under identical metering. Result: **shuffled-history retains 100%
of the advantage, random-library 39%** — the content-vs-presence decomposition that
DreamCoder's Memorize arm gestures at and nobody in this literature completed.

## 6. PREREQUISITES — what must exist before Q060 can be answered at all

**Already satisfied:**

- *A bounded-composition enumerator with minimal-size-per-behaviour.* `aporia/lot/world3.py`
  `build_closure()` returns `minsize[(type, signature)]` — the minimal program size for every
  extensionally distinct function reachable within the budget, by bottom-up enumeration with
  deduplication on extensional signature. **This is exactly the missing certificate machine:**
  a proposed operator whose signature has `minsize > k` is *certified* not reproducible within
  bound k, rather than asserted. Verified cheap — depth 6 costs 69,738 candidate expansions and
  18,224 distinct signatures, 0.2s.
- *A ΔE assay with two nulls reading exactly zero* — Apollo O1, `RESULT_IQ_NULL.json`.
- *Cost separation.* `C_execution = 6.0 × C_search` for every solved task in the flat arm, on
  record, so an A3 macro comparison cannot be run against a merged budget.
- *The four controls*, two of them already executed in D-5.

**NOT satisfied — and these gate the answer:**

1. **No Level 2 mechanism exists**, here or in the surveyed branch. Nothing in Prometheus
   introduces induction from observations, a new oracle, recursion, quantification, variable
   binding, or a new type constructor into a frozen operator set. Without one, Q060 cannot be
   passed by anything we can currently build — only *characterised*.
2. **The A3 rung is preregistered and unrun.** Q100's T2 (equal-compute search without
   failure-derived representation change) is that rung.
3. **Q100's T3 — transfer to ≥3 unrelated worlds — is unbuilt**, and TRANSFER-1 already
   measured 0/200 parser firing across two independent construction routes, so transfer is the
   known weak point, not a formality.
4. **No ground-truth non-redundancy fixture.** The certificate machine exists; a
   known-answer test set for it does not.

## 7. LANGUAGE-FREE FORMULATION

**Class: NATIVE.** This cluster can be posed with no natural-language labels at all, and
TINYPROG already is: 4-tuples over Z6, ten anonymous typed primitives held in an ordered list
where position is identity and the name is a label only — verified by a metamorphic relabelling
that leaves every reading **bit-identical**.

The scoring criterion, which per `report_ENDOGENOUS_MEMORY_GEOMETRY.md` is where language
normally re-enters, is here: verifier-confirmed extensional agreement on a fixed probe set, plus
metered candidate-expansion counts. No relevance judgement, no human category, no task prose.

**What the literature has that could be run language-free but is not presented that way:** LILO's
offline synthesis (freeze the library, run *unguided* enumerative search under a fixed timeout,
score solve rate) is a language-free template; ShapeCoder's objective is token count plus
geometric error; Enumo's derivability is purely extensional e-class merging. **Whether any of
these systems' central claims survive removing human ontology from task selection and DSL design
is unresolved in this corpus** — the DSL is expert-authored in every case (ShapeCoder's base set
is explicitly expert-authored).

## 8. VERDICT

    Q002, Q005   ANSWERABLE AFTER PREREQUISITES. The field measures compression; the
                 reachability instrument exists here. Needs a known-answer fixture.
    Q047, Q060   NOT ANSWERABLE AS WRITTEN by any conservative mechanism, and this is now
                 corroborated by primary text rather than argued. Passable only at Level 2,
                 and no Level 2 mechanism exists in Prometheus or in the surveyed branch.
                 The certificate machinery for T2, however, EXISTS HERE AND NOWHERE ELSE.
    Q100         ANSWERABLE AFTER PREREQUISITES. T1 has a world (TINYPROG, ADMISSIBLE on five
                 unused seeds). T2 is the unrun A3 rung. T3 is unbuilt and is the known weak
                 point.

**The single highest-value action this dossier identifies:** run Q060's T2 as a *certificate*
on TINYPROG — take a promoted macro, compute its signature's `minsize` in the frozen closure,
and report whether it is reproducible within the bound. That is a test no one in the surveyed
literature has executed, the machinery is built and costs 0.2 seconds, and the expected result
is a **negative** — the macro will be reproducible, because it is a composition. Publishing a
certified negative on our own mechanism is worth more than another compression number.

## 9. COVERAGE GAPS — read the verdict through these

**No claim survived verification** on EURISKO/AM and the Lenat self-extension critiques,
QuickSpec/Hipster/Lemmanaid/Twitch theory exploration, RL options/skill discovery, Ruler as a
primary source, or the formal logic literature on conservative vs non-conservative extension.
**Part 3's second half — what machinery is REQUIRED for a non-conservative extension — has no
verified evidence behind it at all**; the two claims touching Koza's architecture-altering
operations were both refuted 0-3. This synthesis covers **library learning and rewrite-rule
inference only.**

**Method limitation:** the run exhausted its WebSearch budget (200/200) during verification, so
verifiers substituted direct primary-source full-text extraction for an adversarial sweep of
third-party critiques. That is the *stronger* check for "what does paper X measure" and the
*weaker* check for "has anyone disputed X." The absence findings in §5 should be read as
"absent from the primary texts checked," not "absent from the literature."

**Next fire for this cluster:** the four unverified branches, especially conservative-extension
formalism and the EURISKO critiques — because the Level 2 requirement is currently a Prometheus
assertion with no external grounding, and it is now load-bearing for two questions.
