# Σ-Kernel Logical Foundation — Feasibility Pass

**Date:** 2026-05-06
**Author:** Techne (analytical sub-agent dispatch under Decision 3 of `roles/Techne/RESPONSE_TO_APORIA_HANDOFF_2026-05-06.md`)
**Tracks:** Watch-1 in `pivot/external_review_watchlist_2026-05-05.md`
**Status:** Analytical only. NO code changes to v2.2 substrate. Single deliverable: this document.
**Question:** Does Calculus of Constructions (CoC) — or a similar dependent-type-theory (DTT) kernel — extended with native falsification records subsume all 7 opcodes (RESOLVE / CLAIM / FALSIFY / GATE / PROMOTE / ERRATA / TRACE) + BIND/EVAL extension v2 + planned REWRITE/EQUIV opcodes cleanly, or do specific opcodes resist clean type-theoretic encoding?

---

## §1. Executive summary

**Verdict: PARTIAL.**

A CoC kernel extended with (a) native falsification records, (b) linear or quantitative type theory (QTT) capabilities, and (c) refinement-typed metadata can subsume the *propositional core* of the substrate's opcodes — RESOLVE, CLAIM, FALSIFY, GATE, REWRITE, EQUIV, and the propositional content of PROMOTE — cleanly. Three distinct opcodes / extensions resist clean type-theoretic encoding without bolting non-trivial machinery onto the kernel:

| Opcode / extension | Subsumption |
|---|---|
| **RESOLVE** | Subsumes cleanly (content-addressed terms / hash as type-level integrity) |
| **CLAIM** | Subsumes cleanly (sigma-typed proposition + payload + caveats-as-refinement) |
| **FALSIFY** | Subsumes cleanly (oracle as decidable predicate + verdict as inhabitant of three-valued sum) |
| **GATE** | Subsumes cleanly (verdict-eliminator in three-valued sum) |
| **PROMOTE** | Subsumes WITH ADJUSTMENT (linearity → QTT or LTT; tier monotonicity → ordered modality) |
| **ERRATA** | RESISTS — requires *non-monotonic update over an append-only term store*; CoC's universe of inhabitants is monotone, errata is a meta-theoretic edge from one term to another |
| **TRACE** | Subsumes cleanly (recursive walk over content-hash DAG = standard Sigma elimination) |
| **BIND** | RESISTS — host-language callable hash + cost contract is *extra-logical* content; CoC can carry the hash but cannot reflect the callable into the type theory without a host reflection layer |
| **EVAL** | RESISTS — execution under cost ceiling with side-effect accounting is operational, not propositional; expressible via session types / graded modal types but pollutes the kernel with effect tracking |
| **REWRITE** | Subsumes cleanly (definitional or propositional equality + rewriting rules) |
| **EQUIV** | Subsumes cleanly (Sigma-typed equivalence + witness inhabitant) |

The honest reading: **the substrate's epistemic content (claims, kills, equivalences, provenance) maps cleanly onto a CoC + linear-types + refinement-types kernel; the substrate's operational content (call this Python function under a budget; correct this prior committed term; track that hash drifted) does not.** That operational content is real and load-bearing for the substrate's value proposition, so a pure CoC port is not a strict superset of the imperative VM. It is a strict superset of the *epistemic* layer and a strict subset of the *operational* layer.

The recommended posture for v3.0 is option (c) — **hybrid, kernel ↔ CoC translation layer maintained both ways** — because the CoC layer subsumes exactly the part of the substrate where reviewers' "too flexible to be foundational" critique bites, while the imperative VM remains the correct execution substrate for opcodes whose semantics are operational by their nature (BIND/EVAL/ERRATA).

---

## §2. Background on the candidate kernel

### 2.1 What CoC is, briefly

The Calculus of Constructions (Coquand–Huet 1988) is a dependent type theory unifying lambda-cube corners (polymorphism, type operators, dependent types) into a single framework where types and terms inhabit one syntactic class and propositions are types (Curry–Howard). Its core is small: variables, abstractions, applications, products (∀ and →), a sort hierarchy (Prop, Type_i for i ∈ ℕ). The Calculus of Inductive Constructions (CIC) adds inductive families and is the kernel of Coq / Rocq; Lean's kernel is in the same family with quotient types and definitional proof irrelevance. For this analysis I treat "CoC" loosely as the family CoC / CIC / Lean's kernel / Agda's MLTT-with-large-eliminations — the differences matter for some of the harder cases below but not for the core question.

What CoC gives "for free" relevant to the substrate:

- **Resolution by name/hash** — terms in CoC are content-addressable up to alpha-equivalence; intensional equality is decidable in normal forms; hash-locking the canonical form of a term gives the same integrity property as `RESOLVE`'s sha256 check.
- **Rewriting** — definitional equality (β, η, δ, ι, ζ-reduction) plus user-declared rewrite rules (Coq's `Hint Rewrite`, Agda's `REWRITE` pragma, Dedukti's λΠ-modulo). Confluence + termination are the standard hygiene conditions.
- **Counterexample-falsification** — to falsify a proposition `P : Prop`, exhibit `¬P` (a term of type `P → ⊥`); to falsify an existential `∃ x. P x` it suffices to produce `∀ x. ¬P x`; concrete counterexamples discharge ∀-statements via instantiation.
- **Provenance walk** — every term in the global environment carries its dependencies (the terms used in its body); walking those dependencies is exactly what Coq's `Print Assumptions` does and is what `TRACE` does on the substrate.

### 2.2 What "native falsification records" likely means

The reviewer's phrase doesn't have a standard formal definition. My reading: a CoC extension where the kernel's global environment is not just `(name, term, type)` triples but `(name, term, type, falsification_status)` tuples, where `falsification_status ∈ {Conjecture, Refuted_by_witness, Discharged_by_proof, Inconclusive_at_depth_d}` and where the kernel typechecker treats `Refuted_by_witness` terms as *inadmissible as imports* but preserves them in the environment as historical record. This corresponds tightly to the substrate's tier ordering (Conjecture / Possible / Probable / WorkingTheory / Validated) plus FALSIFY's three-valued verdict (CLEAR / WARN / BLOCK). The novelty over textbook CoC is that the global environment is no longer monotone-by-construction — terms can carry kill records that *down-classify* their admissibility — and that the typechecker discriminates on those records when resolving imports.

This is a real research direction (cf. defeasible logic in CoC, Beneath-the-Lambda-Cube-style work on revisable proofs) but is not, to my knowledge, deployed in any production proof assistant. Coq, Lean, Agda all assume a monotone environment.

### 2.3 What dependent type theory gives that the imperative VM doesn't

Three things matter for the v3.0 question:

1. **Composability under typing.** In CoC, the well-typedness of a term composed from sub-terms is mechanically verified. The substrate's CLAIM → FALSIFY → PROMOTE chain is well-typed *by manual construction* (PROMOTE rejects claims without verdicts; that's a runtime check, not a static one). A CoC port turns those runtime checks into typing obligations, which is what "foundational" means in the reviewer's sense.
2. **Equational reasoning as first-class.** Equational chains (`A = B = C`) are derivable in CoC by transitivity of `eq`; in the imperative VM they are content-hash chains that the kernel does not reason about. REWRITE/EQUIV makes this gap explicit; CoC closes it.
3. **Decidable typechecking.** Typechecking in CoC is decidable (modulo the universe inconsistency caveats); the substrate's "is this CLAIM well-formed" check is undecidable in general (kill_path can be arbitrary code). Adopting CoC means restricting CLAIM payloads to decidable propositions, which is the reviewer's implicit recommendation in Watch-2 (replace heuristic battery with a decision procedure for a decidable fragment).

The cost: *expressive restriction*. Anything the substrate currently logs that is not a decidable proposition (and there's a lot — operator-policy estimates, stability scores, computational-friction telemetry) doesn't fit cleanly into CoC's propositions-as-types ontology. The CoC port either pushes that content into refinement-typed metadata (carried but not verified) or pushes it into a separate non-CoC sidecar.

---

## §3. Opcode-by-opcode analysis

### 3.1 RESOLVE

**Operational semantics.** `RESOLVE(name, version) → Symbol`. SQL fetch by `(name, version)` primary key, then sha256 integrity check on `def_blob`. Reject on miss (KeyError) or hash mismatch (IntegrityError). Returned `Symbol` is a frozen record with `name`, `version`, `def_hash`, `def_blob`, `provenance: list[str]`, `tier: Tier`. (Source: `sigma_kernel/sigma_kernel.py:501–526`.)

**CoC encoding sketch.** In CoC, the global environment is a list of `(name, term, type)` triples. RESOLVE corresponds to lookup-by-name with a side-condition that the cached canonical form's hash matches the recomputed hash of the term. Adding `version` is straightforward: name terms with a versioned identifier `name#v` (Lean 4 already does this for namespace-collision reasons). Adding `tier` is a refinement annotation — `(name#v, term, type, tier)` quadruples; the kernel typechecker's import resolution function discriminates on `tier ≥ caller_min_tier`.

The hash-integrity check is content-addressed term hashing (canonical normal form → sha256 → compare). This is exactly what Dedukti's λΠ-modulo kernel does for module-level integrity; deploying it in a CoC kernel is a known pattern.

`provenance: list[str]` becomes a list of references to other names in the environment, walked by the standard transitive-closure algorithm.

**Verdict: SUBSUMES CLEANLY.** RESOLVE is the textbook case for type-theoretic environments. The encoding is direct.

---

### 3.2 CLAIM

**Operational semantics.** `CLAIM(target_name, hypothesis, evidence, kill_path, target_tier, caveats, precision_metadata) → Claim`. Mints a provisional claim record. Persists `id`, target identity, hypothesis text, evidence dict, kill_path (a route through the falsification battery), target tier, caveats (typed metadata strings), and precision_metadata (dict with dps / method / convergence / stability). Auto-fires `precision_below_expected` and `verification_failed` caveats from precision_metadata. Stores in `claims` table with status='pending'. (Source: `sigma_kernel/sigma_kernel.py:566–679`.)

**CoC encoding sketch.** A CLAIM is a Sigma-typed proposition with payload:

```
Claim ≜ Σ (P : Prop)
        × (kill_path : KillPath P)
        × (evidence : Evidence P)
        × (target_tier : Tier)
        × (caveats : List Caveat)
        × (precision : Maybe PrecisionMetadata)
```

`Claim` here is a dependent record (record types are syntactic sugar for nested Sigma; CoC has them via inductive type families). The proposition `P : Prop` is the hypothesis. `KillPath P` is a type indexed by `P` — the kill_path must be appropriate to the hypothesis (a ∀-statement uses witness-search; an equality uses normalization-difference; a conjecture uses a registered battery route). `Evidence P` is similarly indexed.

`caveats : List Caveat` is straightforward as a list of tagged sums. `Caveat` is itself an inductive type with constructors for each preset (`small_n`, `mode_collapse`, `precision_below_expected`, etc.) plus a `Custom : String → Caveat` escape hatch for the open list. The auto-caveat firing rule (precision_metadata triggers two caveats) is a derived term: `compute_auto_caveats : PrecisionMetadata → List Caveat`, applied at claim construction time.

`precision_metadata` carries refinement structure (dps as `Nat`, method as a tagged enum, convergence as a tagged enum, stability as `Maybe (Refined Float [0,1])`). Refinement types are not CoC-native but are routine in F* / Liquid Haskell / Coq via `{x : T | P x}`.

The status field (`pending` | `falsified` | `promoted`) is a mode tag that can be encoded as an indexed type: `Claim status` becomes a dependent type with status-specific operations defined on it. Falsified claims have a verdict witness; promoted claims have a tier-update witness.

**Verdict: SUBSUMES CLEANLY.** Sigma-types are exactly the right machinery. The only encoding tax is keeping `Caveat` and `KillPath` as open inductive families, which Coq/Lean handle via universe polymorphism. CLAIM is propositional content first and foremost; CoC was built for it.

---

### 3.3 FALSIFY

**Operational semantics.** `FALSIFY(claim, seed) → VerdictResult`. Dispatches the claim's hypothesis + evidence + kill_path to the Ω oracle subprocess (`omega_oracle.py`). Receives `(verdict, rationale, input_hash, seed, runtime_ms)`. Verdict is one of CLEAR / WARN / BLOCK. Binds the verdict to the claim (in-memory + DB UPDATE). Appends `falsify_warn:<rationale>` caveat if verdict is WARN. Fails closed: any oracle error becomes BLOCK with the error rationale. (Source: `sigma_kernel/sigma_kernel.py:685–771`.)

**CoC encoding sketch.** The oracle is a *decidable predicate*: `oracle : (P : Prop) → (kp : KillPath P) → (ev : Evidence P) → Verdict`, where `Verdict ≜ CLEAR | WARN String | BLOCK String`. The oracle's definition in CoC is whatever decision procedure the kill_path encodes (for proof-bearing kill_paths this is a `Decision P` — either a proof of P or a proof of ¬P; for numerical kill_paths it is a refinement-typed numeric check; for catalog kill_paths it is a lookup with a registered catalog hash).

The verdict is an inhabitant of a three-element sum type. CLEAR corresponds to *no counterexample found at depth d* (or to a positive proof, when the kill_path produces one); WARN corresponds to *result with caveats*; BLOCK corresponds to *counterexample found* (the BLOCK rationale embeds the counterexample witness). The propositions-as-types reading: BLOCK with rationale `r` is a term of type `¬P` derived from `r`; CLEAR is a term of type `Decidable_at_d P` for some depth `d`; WARN is a term of `P ∧ Caveat` for some caveat.

The oracle subprocess boundary is *not* part of the type theory — it's an implementation detail. From the kernel's perspective, the oracle is a trusted external decision procedure (analogous to Coq's `vm_compute` reduction or Lean's `native_decide` tactic). The "fails closed → BLOCK" semantics is the same as a tactic that times out being treated as a failure to discharge the goal.

The auto-caveat append on WARN (`falsify_warn:<rationale>` prepended to claim caveats) is a derived term: `bind_verdict : Claim → Verdict → Claim'` where `Claim'` is the claim with caveats updated.

**Verdict: SUBSUMES CLEANLY.** The Ω oracle is exactly the position external decision procedures occupy in production proof assistants. The three-valued verdict maps onto a sum type; the subprocess boundary is below the type theory's level of concern. The only design choice is whether to model WARN as a separate constructor or as `CLEAR ∧ Caveat` — both work; the constructor form is more direct.

---

### 3.4 GATE

**Operational semantics.** `GATE(verdict) → "WARN" | "CLEAR"`. Pure dispatch on verdict status: BLOCK raises `BlockedError` (caller's path dies), WARN prints + returns "WARN" (caller may proceed but warning attaches downstream), CLEAR returns "CLEAR" (continue). (Source: `sigma_kernel/sigma_kernel.py:777–792`.)

**CoC encoding sketch.** GATE is the eliminator on the three-valued verdict sum:

```
gate : (v : Verdict) → (continuation : v ≠ BLOCK → α) → α
```

(or, more cleanly with subset types: `gate : {v : Verdict | v ≠ BLOCK} → α → α` plus a separate `gate_block : ⊥`-typed handler for the BLOCK case). The "warning attaches downstream" semantics is the hard part: it means a CLEAR-or-WARN verdict's downstream value carries the warning as a refinement annotation. In propositions-as-types this is a *graded* or *modal* type — `α` becomes `Warned α` if the gate was WARN, untagged otherwise. Coq doesn't natively have graded modal types but Agda's experimental GradedTypes plugin and Granule's quantitative types both express this directly.

Without graded types, the encoding is uglier: every downstream consumer of a WARN-verdicted value receives a Sigma-pair `(value, caveat_list)` and must thread the caveat list manually. This is what the substrate already does at the operational level (caveats are first-class and propagate via TRACE), so the encoding overhead is no worse than the imperative VM's manual threading — but it is also no better. A graded-types CoC port lets the kernel automate the threading; a vanilla CoC port keeps it manual.

**Verdict: SUBSUMES CLEANLY.** The eliminator pattern is direct. The downstream-attachment semantics is cleaner with graded types but works without them.

---

### 3.5 PROMOTE

**Operational semantics.** `PROMOTE(claim, cap) → Symbol`. Four checks:
1. Capability `cap` exists in `capabilities` table and is unconsumed.
2. Capability is consumed atomically with the symbol insert (linear discipline).
3. Claim has a non-BLOCK verdict bound (defense-in-depth even if caller skipped GATE).
4. `(target_name, new_version)` does not collide (rejected by PRIMARY KEY).

Builds `def_blob` containing hypothesis, evidence dict, kill_path, verdict status + rationale, sorted+deduplicated caveats, and (optionally) precision_metadata. Hash = sha256(def_blob). Provenance scraped from evidence (any 64-char-hex string in evidence values) plus verdict.input_hash. Inserts into `symbols` table. Updates claim status to 'promoted'. (Source: `sigma_kernel/sigma_kernel.py:798–906`.)

**CoC encoding sketch.** PROMOTE has three semantic layers, each demanding a different DTT feature:

1. **Linear capability.** `cap : Capability` is a *linear* resource — once consumed, the same cap_id cannot be re-used. Standard CoC has no linearity; the encoding requires either (a) Linear Type Theory (LTT, Cervesato–Pfenning style), (b) Quantitative Type Theory (QTT, Atkey 2018 / used in Idris 2), or (c) session types where capabilities are channels with usage-count obligations. QTT is the cleanest match: declare `cap : ω 1 Capability` (multiplicity 1, used exactly once); promote consumes it. This is well-understood DTT machinery, but it's not vanilla CoC.

2. **Non-BLOCK verdict precondition.** `claim.verdict ≠ BLOCK` is a refinement on the claim's type. This is Sigma-type encoding: `PromotableClaim ≜ Σ (c : Claim) × (v : Verdict | v ≠ BLOCK)`, with `PROMOTE : PromotableClaim → Capability_1 → Symbol`. Standard refinement-typed CoC.

3. **Tier monotonicity** (implicit). The substrate's tiers are ordered (Conjecture < Possible < Probable < WorkingTheory < Validated). Promotion can lift a claim's tier but the substrate enforces no downward motion. In CoC this is an *ordered modality* on the symbol type — `Symbol` is parameterized by a tier with a partial order, and promotion is monotone in tier. Coq/Lean handle this via parameterized inductive types; clean.

The other PROMOTE-internal logic (versioning by `max(version) + 1`, provenance scraping, hash computation, atomic DB insert) is operational machinery beneath the type theory's concern. The CoC port handles versioning by appending to the global environment with a fresh name; provenance scraping becomes a syntactic walk over the term to extract referenced names; hash computation is an external operation on the term's normal form.

**Where PROMOTE genuinely strains.** The atomic "consume cap + insert symbol" transaction is an operational-DB property that CoC doesn't model. A CoC port either (a) lifts the kernel's environment update into a state monad with rollback (Coq's `Definition` + module abort, or session-typed environment manipulation), or (b) treats the environment update as a meta-theoretic operation outside the type theory entirely. Both are workable; neither is "clean" in the sense of being a one-line encoding.

**Verdict: SUBSUMES WITH ADJUSTMENT.** The propositional content (verdict precondition, tier monotonicity) is direct. The linearity needs QTT or LTT — a real DTT but not vanilla CoC. The atomic DB transaction is below the type theory's level and stays operational regardless.

---

### 3.6 ERRATA

**Operational semantics.** `ERRATA(prior_name, prior_version, corrected_def, fault_description, cap) → Symbol`. Promotes a corrected v(N+1) of an existing symbol with an `errata_correcting` backref embedded in the new symbol's def_blob. The prior version remains immutable in the substrate as historical record of what was pushed and why it was wrong. Append-only is preserved: a new edge (the errata pointer) is added; the prior is never mutated. (Source: `sigma_kernel/sigma_kernel.py:912–993`.)

**CoC encoding sketch.** This is the hardest opcode. ERRATA's semantics is *non-monotonic update over an append-only term store*: `prior_name@v(N)` is in the environment, has been used by downstream consumers, and is now flagged as wrong. The kernel does not delete it (append-only). The kernel does not edit it (immutable). It adds `prior_name@v(N+1)` with a backref saying "supersedes v(N) because <fault>." Downstream consumers that imported `prior_name@vN` continue to work (their resolution still hits v(N)) but new resolutions to `prior_name` (without explicit version) should pick v(N+1). And — critically — anything *built on top of* `prior_name@vN` is now suspect.

Standard CoC has no native concept of "prior committed term flagged as wrong." The CoC environment is monotone by construction; new terms can be added, existing terms cannot be retracted. Several encodings approximate ERRATA but each has a sharp edge:

1. **Errata as new inductive constructor.** Add `Erratum : (prior : Term) × (corrected : Term) × (fault : String) → ErrataRecord` and a global registry `errata_registry : List ErrataRecord`. Resolution by name consults the registry: if the term is in the registry's `prior` field, the resolver returns the `corrected` term (or a sum of both with the user choosing). **Problem:** this is a meta-theoretic resolver layer, not a kernel operation. The CoC kernel cannot reason *inside* the type theory about "this term is the corrected version of that one"; it's an external bookkeeping table.

2. **Errata as Sigma-typed evidence carried by every term.** Every term in the environment carries an `errata_status : Maybe ErrataRecord` annotation. Refinement-typed: `WellFormedTerm ≜ {t : Term | t.errata_status = None ∨ t.errata_status.is_resolved}`. The typechecker rejects attempts to use an `errata_status = Refuted` term in a new proof. **Problem:** this requires the kernel environment to be revisable, which is exactly what monotonicity prohibits in standard CoC. Defeasible logic in CoC is an active research area but not production-grade.

3. **Errata as parallel namespace.** `prior_name@vN` stays untouched in namespace `historical`; `prior_name@v(N+1)` lives in namespace `current`; an explicit `errata_link : historical → current → FaultDescription` is added. The kernel typechecker's default import behavior reads from `current`; explicit imports from `historical` work but the typechecker emits a warning. **Problem:** this is the cleanest of the three but it pushes the resolution policy out of the type theory entirely; the kernel's role becomes "store both, let the resolver decide," which is what the substrate already does — the gain over the imperative VM is essentially zero.

4. **Errata as natural deduction inference.** `Erratum` is a primitive judgment of the kernel's metatheory: `Γ ⊢ supersedes(prior, corrected, fault)`. The judgment can be applied to derive that downstream theorems built on `prior` are themselves subject to revision. **Problem:** this requires extending the kernel's judgment language, which is the most invasive change of the four.

**Where ERRATA genuinely resists.** The substrate's append-only-with-errata-link discipline is *defeasible reasoning* (claims can be retracted with a recorded fault), but CoC is a *monotone* logic by design. Defeasible CoC variants exist in the literature (see e.g. Gabbay's labeled deductive systems or the work on belief revision in DTT) but none are production-grade and all introduce non-trivial complications: confluence becomes harder to maintain (rewriting against a retracted term is now itself revisable), normalization may not terminate, and decidability of typechecking is no longer guaranteed.

The honest reading is that ERRATA encodes a *substrate-meta-theoretic* operation — "this term I committed earlier is wrong, here's the fix" — which CoC handles only via meta-language conventions (option 1 or 3 above) that don't materially improve over what the imperative VM already does. The CoC kernel can carry the errata link as data; it cannot reason about the link as a logical inference rule without significant kernel extension.

**Verdict: RESISTS.** ERRATA is the clearest case where the CoC port adds tax without adding power. The imperative VM's "INSERT new symbol with backref pointer" is the simplest correct implementation; CoC encodings either replicate that pattern with extra typing overhead or introduce defeasible-logic machinery that the substrate doesn't actually need.

---

### 3.7 TRACE

**Operational semantics.** `TRACE(symbol) → dict`. Recursive walk from `symbol.def_hash` outward through provenance hashes. Each visited symbol yields `(ref, hash_prefix, caveats, precision_metadata, children)`. Hashes that don't resolve to a substrate symbol are tagged 'external'. Cycle-safe via a visited set. `collect_caveats(symbol)` walks the same tree and unions caveats for citation-grade provenance. (Source: `sigma_kernel/sigma_kernel.py:999–1080`; invariant audited in `sigma_kernel/TRACE_PRESERVATION_AUDIT.md`.)

**CoC encoding sketch.** TRACE is the standard transitive-closure walk over a term's free-variable references in the global environment. Coq's `Print Assumptions T` does exactly this; Lean's `#check @T` plus reflection-on-definition gives the same walk. The cycle-safety is automatic in CoC because well-formed environments are acyclic by construction (a term cannot reference itself unless it's an explicit fixpoint, in which case the fixpoint name occurs in the environment but not in its own free variables).

The "external hash" tagging — provenance hashes that don't resolve to a substrate symbol — corresponds to opaque references in CoC. These are routine: a hashed reference to an axiom (Coq `Axiom`, Lean `axiom`) or an external module is logged as external; the walk terminates there with the external tag.

The caveat / precision_metadata propagation is direct: each environment entry carries its caveats and precision_metadata as a Sigma-typed annotation; the walk accumulates them into the result tree. `collect_caveats` is the union over the walk's result, which is a fold over the tree.

**Verdict: SUBSUMES CLEANLY.** TRACE is what type-theoretic environments are *for*. The encoding is the simplest of any opcode.

---

### 3.8 BIND (extension v2)

**Operational semantics.** `BIND(callable_ref, cost_model, postconditions, authority_refs, cap, name, version) → Binding`. Resolves a host-language (Python) callable, computes its source hash via `inspect.getsource`, mints a CLAIM whose evidence includes the callable_hash and cost_model, runs an in-process Ω validator, calls GATE, calls PROMOTE (with dual-cap pattern: user cap consumed for accounting, internal PromoteCap minted for kernel.PROMOTE), writes a `bindings` side-table row keyed on the PROMOTE-assigned (name, version). (Source: `sigma_kernel/bind_eval_v2.py:136–281`.)

**CoC encoding sketch.** The BIND opcode binds a *host-language callable* into the substrate. This is the structural problem: CoC is a closed type theory; any "callable" inside CoC is a CoC term, not a Python function. A CoC port has three roads:

1. **Reify the host callable's source as a CoC term.** Parse the Python AST, translate to CoC syntax, typecheck. **Problem:** Python is not strongly normalizing, has unbounded effects, and uses dependent types only by convention. Translating arsenal callables to CoC is a massive engineering project (effectively writing a Python-to-Coq compiler) and most arsenal callables (those that wrap mpmath, sympy, cypari) are wrappers around C extensions whose semantics CoC cannot represent.

2. **Treat the host callable as an opaque oracle.** `BIND(callable_ref, ...)` produces a term `oracle_<hash> : ∀ args. Result` whose body is `axiom`; the only thing CoC tracks is the type signature and the source hash (carried as a refinement annotation). EVAL of an oracle reduces to the oracle's declared output via `vm_compute`-style escape into the host, then the result is reflected back into CoC for downstream use. **Problem:** the cost contract (`max_seconds`, `max_memory_mb`, `max_oracle_calls`) is invisible to CoC; cost enforcement happens entirely in the host; CoC carries the contract as a refinement but does not check it.

3. **Wrap the host callable in a session-typed protocol.** BIND mints a session-typed channel with declared input/output and cost ceilings; EVAL communicates over the channel and the kernel observes the protocol's adherence. **Problem:** session types are well-developed in Idris 2 and Granule but not in standard CoC; the protocol-checking logic is a separate verification layer.

The fundamental issue: BIND's value to the substrate is *binding host-language callables* with an integrity hash and a cost contract. CoC's value is *reasoning about closed terms in a strong type theory*. These are different jobs. A CoC port that reifies callables (option 1) is impractical; a CoC port that treats callables as opaque oracles (option 2) preserves the integrity hash but loses the cost contract; a session-typed port (option 3) preserves both but is no longer vanilla CoC.

The most honest CoC encoding is option 2 with the cost contract carried as refinement-typed metadata that the kernel does not enforce. This is essentially what the substrate already does (cost contract is enforced at the host layer; kernel logs the contract but doesn't check it). The CoC port adds typing structure to the binding's interface but does not add new enforcement power.

**Verdict: RESISTS.** BIND's purpose — binding host-language callables — is extra-logical content. CoC carries the hash and the type signature cleanly; CoC does not reason about the callable's body. The cost contract resists especially: it is an operational property (resource consumption during execution), not a propositional property (a fact about a term). Graded modal types can express resource bounds in DTT (Granule does this) but the resulting kernel is no longer "lightweight CoC + falsification records" — it's a different kernel altogether.

---

### 3.9 EVAL (extension v2)

**Operational semantics.** `EVAL(binding_name, binding_version, args, kwargs, cap, eval_version) → Evaluation`. Resolves the binding side-table row, mints an EVAL claim, runs pre-execution validation (drift check on callable hash), executes the callable under tracemalloc + oracle counter + 3-dim budget enforcement, captures actual cost, runs post-execution validation (cost ceiling), binds verdict, GATEs, PROMOTEs (dual-cap), writes evaluations side-table row. (Source: `sigma_kernel/bind_eval_v2.py:287–514`.)

**CoC encoding sketch.** EVAL inherits all of BIND's resistance and adds two more:

1. **Side-effect accounting.** EVAL measures `elapsed_seconds`, `memory_mb`, `oracle_calls` during execution. None of these are propositional facts. They are operational measurements with the property that they can vary across runs of the same callable on the same input (especially `oracle_calls`, since dispatched subprocess calls may be cached or skipped). CoC has no native model of execution traces; expressing "this term, when reduced under strategy S, consumed C resources" requires a graded modal type theory or a session-typed protocol with usage counters. Granule and Idris 2 (with QTT-on-resources) can express this; vanilla CoC cannot.

2. **Hash drift detection.** EVAL checks that the callable's *current* source hash matches the *stored* hash from BIND time, and BLOCKs on mismatch. This is meta-temporal: the kernel must observe that a term in the global environment has been updated externally and refuse to use the stored binding. CoC's monotone environment doesn't support "term changed externally"; the closest analogue is module-level versioning where re-importing a module produces a new term with a different name. The substrate's hash-drift discipline, mapped to CoC, becomes "every BIND is a fresh module with a fresh name; EVAL imports the module by content hash; if the module's content has changed, the import fails to resolve." This works but loses the substrate's notion of "binding `foo@v3` was updated under us" — instead the binding simply ceases to resolve.

The three-dimensional budget enforcement (`elapsed_seconds`, `memory_mb`, `oracle_calls`) is the strongest indicator that EVAL is operational: each dimension is a runtime resource; their conjoint enforcement is a *cost contract*; cost contracts are exactly the territory where graded type theories shine and where CoC does not.

**Verdict: RESISTS.** EVAL is the apotheosis of the operational layer. Encoding it in CoC requires either (a) a graded type theory, in which case "lightweight CoC" is a misnomer, or (b) reducing EVAL to an opaque oracle call with the cost accounting carried as unverified metadata, in which case the CoC port adds nothing over the imperative VM.

---

### 3.10 REWRITE (planned, v2.3 §6.4)

**Operational semantics (planned).** `REWRITE src_expr → tgt_expr via <rewrite_rule_id> preserves <invariant_set>`. Records that `src_expr` rewrites to `tgt_expr` under a registered rewrite rule, with a declared invariant set the rewrite must preserve. Confluence + termination are caller's responsibility (the kernel logs but does not verify). (Source: `pivot/substrate_v2_proposal_2026-05-05.md` §6.4.)

**CoC encoding sketch.** REWRITE is exactly what definitional / propositional equality gives in CoC:

- For decidable equalities (β/η/δ/ι reduction), REWRITE corresponds to declaring a definitional unfolding rule. Coq's `Definition` + `Hint Unfold`; Agda's `REWRITE` pragma; Dedukti's λΠ-modulo at kernel level. The kernel automatically applies the rewrite during typechecking; users do not invoke REWRITE explicitly except to register the rule.
- For propositional equalities (where the rewrite is true but not by computation), REWRITE corresponds to a witness term `eq_witness : src_expr = tgt_expr`, plus the standard rewrite tactic `rewrite eq_witness in goal`. The witness term is itself a CoC term, often constructed by composition of more primitive equalities.
- The "preserves <invariant_set>" clause is a refinement: the rewrite rule's type carries `(P : src_expr) → P (tgt_expr)` for every invariant `P` in the set. This is a list of propositions that the rewrite must preserve; the kernel typechecker discharges them at rule registration time.
- Confluence + termination are exactly the standard hygiene conditions for rewrite rule sets. Coq's `Hint Rewrite` doesn't check them automatically (caller's responsibility, same as the substrate); Dedukti's confluence checker does. Either pattern is workable.

The substrate's REWRITE opcode is, semantically, just the imperative VM's logging of an event that CoC handles natively as part of typechecking. The CoC port subsumes REWRITE *more cleanly than the substrate plans to implement it*: in CoC, registered rewrite rules are applied automatically by the kernel; in the substrate, REWRITE is logged and then must be replayed by callers who want to use it.

**Verdict: SUBSUMES CLEANLY.** REWRITE is the textbook case for CoC. Among the planned opcodes, this is the one that most argues for the CoC port — the imperative VM is replicating with explicit ledger entries what CoC does as part of its kernel reduction.

---

### 3.11 EQUIV (planned, v2.3 §6.4)

**Operational semantics (planned).** `EQUIV expr_a ≡ expr_b under <equivalence_class_id> with <witness>`. Records that two expressions are equivalent under a named equivalence relation, accompanied by a witness term that justifies the equivalence. (Source: `pivot/substrate_v2_proposal_2026-05-05.md` §6.4.)

**CoC encoding sketch.** EQUIV is direct in CoC:

```
Equiv (R : EquivalenceClass) (a b : T) ≜ Σ (witness : Witness R a b) × (proof : R a b)
```

`R : EquivalenceClass` is itself a CoC term: a binary relation on `T` with proofs of reflexivity, symmetry, transitivity. The substrate's "equivalence class id" is a name in the environment binding to such an `R`. The "witness" is a term inhabiting `R a b` — for definitional equivalence this is `refl`; for propositional equivalence it's a constructed proof; for more abstract equivalences (isogeny, Hecke orbit, etc.) the witness is a domain-specific datum (a morphism, a Hecke operator, etc.) plus a proof that it satisfies `R`'s axioms.

Coq has `Setoid`, `Equivalence`, `Setoid_Theory` exactly for this; Lean has `Setoid` and `Quot` types; Agda has `Setoid` in the standard library. All of these encode equivalence relations + witness terms as Sigma-types and discharge equivalence-respecting rewriting via the standard tactics.

**Verdict: SUBSUMES CLEANLY.** EQUIV is, like REWRITE, an opcode that CoC handles more naturally than the imperative VM. The setoid machinery in production proof assistants is exactly the right abstraction.

---

## §4. Cross-cutting concerns

### 4.1 Linear capabilities

The substrate's `Capability` is a linear resource: minted once, consumed once, persisted in `spent_caps` to enforce linearity across process boundaries. PROMOTE consumes a `PromoteCap`; the dual-cap pattern in BIND/EVAL v2 consumes a user `BindCap` / `EvalCap` plus mints + consumes an internal `PromoteCap`.

Standard CoC has no linearity. Three DTT extensions handle it:

- **Linear Type Theory (LTT)** — Cervesato–Pfenning. Strict separation of linear and intuitionistic contexts. Capabilities live in the linear context; consumption removes them. Mature theory; no production proof assistant uses it as a kernel.
- **Quantitative Type Theory (QTT)** — Atkey 2018. Each binding carries a multiplicity ∈ {0, 1, ω}. Capabilities are multiplicity-1; consumption is enforced by the typing rule. Used in Idris 2 as the kernel's foundation. **Cleanest fit.**
- **Session types** — Honda et al. Channels with usage protocols. Capabilities are channels with declared lifecycles; consumption is a channel close. Used in concurrent programming verification; less common as the kernel's primary discipline.

A v3.0 CoC port that wants to handle PROMOTE / BIND / EVAL cleanly should adopt QTT or LTT. The choice doesn't affect the propositional content; it affects only how the kernel typechecks usage of capabilities. Idris 2's QTT is the most production-ready DTT with linearity baked in; Coq + Iris (linear separation logic) is a common alternative for verifying linear-resource code without making the kernel itself linear.

The substrate's `consumed=1` DB enforcement is the operational analog of QTT's multiplicity check. They are the same property at different layers: QTT does it at typechecking time; the substrate does it at write time. **Both are correct; a CoC port doesn't gain enforcement power, it gains static verification.**

### 4.2 Caveat-as-metadata propagation through TRACE

Caveats are typed metadata (open list of strings; preset canonical forms in `KNOWN_CAVEATS`) that travel with claims through FALSIFY / PROMOTE / TRACE. Hash-locked into `def_blob` at PROMOTE time so a symbol cannot lose its caveats without changing its hash. Auto-fired from precision_metadata. Propagated through TRACE walks; `collect_caveats` returns the union over a symbol's lineage.

The CoC encoding is straightforward: each environment entry carries `caveats : List Caveat` as a Sigma-typed annotation; the typechecker propagates caveats through proof terms (a proof that uses a caveated lemma inherits the caveat). This is *exactly* what Coq's `From <Module> Require Import` does for module-level axioms — when you import a module that depends on `Classical_Prop`, your downstream theorems carry the classical-axiom dependency, surfaced by `Print Assumptions`.

The substrate's hash-lock discipline (caveats are part of the content hash) corresponds to canonical normal forms: in CoC, two terms with different caveat annotations are not alpha-equivalent and thus have different hashes. This is the same property at a different layer.

**Verdict: clean fit.** CoC's existing assumption-tracking machinery is the right place to implement caveat propagation, and arguably handles it more rigorously than the substrate's manual JSON-in-def_blob discipline.

### 4.3 Precision metadata as first-class

`precision_metadata` is a dict shape `{dps, method, convergence, stability}` carried on every Claim. Auto-caveats fire on `dps < 60` and on convergence failure. Propagated through TRACE.

Encoding: refinement types. `Precision ≜ Σ (dps : Nat) × (method : MethodTag) × (convergence : ConvergenceStatus) × (stability : Maybe (Refined Float [0,1]))`. Refinement-typed values can be checked at construction time (`dps ≥ MIN_DPS` is a refinement that, if violated, fires the `precision_below_expected` caveat as a derived term).

F* / Liquid Haskell / Coq's `subset` type all support this directly. CoC purists insist on Sigma-types with explicit proof of the refinement; F*-style implicit subtyping is more ergonomic but is a kernel extension. Either works.

**Verdict: clean fit, with the same observation as caveats — refinement types in DTT handle this more rigorously than the substrate's JSON discipline.**

### 4.4 Append-only ledger semantics

The substrate's underlying storage is append-only: once a symbol is in the `symbols` table, it cannot be modified or deleted. New versions are appended; ERRATA adds backref pointers. This is enforced by SQLite UNIQUE constraints + the kernel's `ImmutabilityError` on collision.

This property is *orthogonal* to the type theory. A CoC kernel's global environment is itself append-only by convention (textbook environment update is `Γ, x:T`, never deletion). Adding immutability to a CoC port is free. The DB-side enforcement is operational; the type theory enforces it as a meta-theoretic invariant.

The exception is ERRATA, discussed in §3.6 — append-only-with-backref isn't natively expressible in CoC's monotone environment without conventions.

**Verdict: append-only itself is free in CoC; ERRATA's append-only-plus-supersedes is the resistance point.**

---

## §5. What doesn't subsume cleanly

Three honest negative findings, named precisely:

### 5.1 ERRATA's defeasible semantics

ERRATA encodes "this term I committed earlier is wrong, here is the corrected version, downstream consumers should now be suspicious." This is *defeasible reasoning* — claims can be retracted with recorded fault. CoC is monotone by construction. Defeasible CoC variants exist in the academic literature but introduce non-trivial complications (confluence, normalization, decidability of typechecking) and are not production-grade. The CoC port either treats ERRATA as a meta-theoretic resolver layer (in which case it adds nothing over the imperative VM) or extends the kernel with defeasible-logic machinery (in which case "lightweight CoC + falsification records" is no longer a fair description).

The imperative VM's "INSERT corrected symbol with backref" is the simplest correct implementation. Every CoC encoding either replicates it with extra typing tax or moves to a research-grade kernel.

### 5.2 BIND's host-callable binding

BIND's purpose is binding *host-language* (Python) callables into the substrate with an integrity hash and a cost contract. CoC's value is reasoning about *closed CoC terms*. Reifying Python callables as CoC terms is impractical (Python is not strongly normalizing, has unbounded effects, depends on C extensions); treating callables as opaque oracles loses the cost contract; session-typed wrapping is no longer vanilla CoC.

The most honest CoC encoding carries the callable's hash + type signature as refinement-typed metadata that the kernel does not enforce. This is essentially what the substrate already does. The CoC port adds typing structure but does not add new enforcement power for the host-callable layer.

### 5.3 EVAL's cost contract + side-effect accounting

EVAL measures three resource dimensions (`elapsed_seconds`, `memory_mb`, `oracle_calls`) during execution and enforces a cost contract. None of these are propositional facts; they are operational measurements of execution traces. CoC has no native model of execution traces. Graded modal type theories (Granule) and QTT-on-resources (Idris 2 with multiplicities-as-resources) can express resource bounds in DTT, but the resulting kernel is not "lightweight CoC + falsification records" — it's a different kernel altogether.

Reducing EVAL to an opaque oracle call with cost accounting carried as unverified metadata loses the substrate's three-dimensional budget enforcement, which is load-bearing for defending against RL agents that route around unmetered cost dimensions (the C2 critique from the 2026-05-03 review). The substrate's instrumented-host execution model is doing real epistemic work that the type theory cannot replicate.

### 5.4 The combined honest reading

The substrate has two distinguishable layers:

- **Epistemic layer.** Claims, kills, equivalences, rewrites, provenance, caveats, precision metadata. This is propositional content. CoC subsumes it cleanly, often more rigorously than the imperative VM.
- **Operational layer.** Host-callable binding, execution under cost contract, hash-drift detection, defeasible-update via ERRATA. This is operational content. CoC encodes pieces of it via QTT / refinement / session types, but the encoding tax becomes increasingly heavy and the resulting kernel is no longer "lightweight CoC."

**Reviewers' "too flexible to be foundational" critique bites the epistemic layer.** That critique is correct: the imperative VM does not formally distinguish "this CLAIM is propositionally well-formed" from "this CLAIM is a syntactically valid record of some text." A CoC port closes that gap.

**Reviewers' critique does not bite the operational layer.** The operational layer is *appropriately* an imperative VM because its job is operational: bind a Python function, run it under a budget, log the outcome. CoC is the wrong tool for that job; trying to force it produces a worse kernel, not a better one.

---

## §6. Recommendation for v3.0 design pass

Three options, with explicit tradeoffs:

### Option (a) — Adopt CoC + falsification records as v3.0 substrate; deprecate imperative VM

**Tradeoff:** highest theoretical purity. ERRATA / BIND / EVAL get encoded via QTT + refinement + opaque-oracle-with-unverified-cost-metadata. The kernel grows from "imperative VM with append-only DB" to "DTT kernel with linearity + refinement + session-typed external interface + defeasible-update layer." Engineering cost: high (multi-month research-grade kernel build); risk: high (unproven kernel design); gain: theoretical foundationalism + composability under typing. **Likely outcome:** the kernel is too restrictive for the substrate's operational needs and is reluctantly relaxed back toward the imperative VM, in which case the deprecation was wasted work.

### Option (b) — Keep imperative VM; layer typed-checker on top for safety-critical paths only

**Tradeoff:** zero kernel risk. A CoC-based typed checker reads the imperative VM's ledger and verifies the propositional content of CLAIM / FALSIFY / PROMOTE / REWRITE / EQUIV chains. ERRATA / BIND / EVAL are passed through without type-theoretic verification (they are checked operationally as today). Engineering cost: medium (build the typed checker; integrate at promotion-gate boundary); risk: low (the imperative VM remains source-of-truth); gain: defense-in-depth for the propositional layer. **Likely outcome:** the typed checker catches a small number of real bugs, doesn't materially change the substrate's value proposition, and becomes a side-track that bit-rots when the imperative VM evolves faster than the checker's coverage.

### Option (c) — Hybrid: kernel ↔ CoC translation layer; both representations maintained

**Tradeoff:** highest expressive coverage. The imperative VM remains the operational substrate (BIND / EVAL / ERRATA / DB writes). A CoC translation layer exports the propositional content (CLAIM payloads, FALSIFY verdicts, REWRITE rules, EQUIV witnesses, TRACE walks) into a typed proof environment that can be checked independently. The two representations are kept in sync by a translation function whose correctness is itself a substrate-grade invariant. Engineering cost: medium-high; risk: medium (translation layer is the new failure surface); gain: epistemic layer gets DTT verification *and* operational layer keeps its imperative discipline. **Likely outcome:** the translation layer becomes a useful audit tool and a new substrate-grade interface (e.g., for exporting to Coq / Lean for adversarial verification by external reviewers).

### My recommendation: **Option (c)**.

**Reasoning:** The verdict in §1 — partial subsumption — directly implies a hybrid. CoC is the right tool for the part of the substrate where reviewers' critique bites (epistemic layer); CoC is the wrong tool for the part where the substrate's value comes from operational discipline (BIND / EVAL host-callable execution). Forcing one tool to do both jobs (option a) produces a worse kernel; refusing to use the right tool where it fits (option b) leaves the foundational critique unaddressed.

A hybrid lets the substrate retain its operational discipline AND export a typed proof environment to external reviewers / Lean / Coq communities for adversarial verification. The translation layer also *operationalizes* the substrate's epistemic explicitness: it forces precise specification of what each opcode's propositional content is, which is itself a discipline gain even if the typed checker is rarely run.

The pre-condition for option (c) is that the translation layer is itself a substrate-grade invariant. Concretely: every claim in the substrate's ledger has a well-defined CoC translation; the translation function is total; round-tripping (substrate → CoC → substrate) is identity on the epistemic content. This is a non-trivial engineering commitment but is bounded scope.

---

## §7. Empirical falsification test for the recommendation

Per Watch-1 in `pivot/external_review_watchlist_2026-05-05.md`, the falsification test is:

> Spend ~1 week prototyping the Σ-kernel as a CoC extension. If it subsumes all opcodes cleanly, the imperative-VM design becomes the deprecated path.

For option (c) — the hybrid recommendation — the falsification test specializes:

### Success criteria for the prototype phase

1. **Translation layer covers ≥ 7/11 opcodes cleanly.** Concretely: write a translation function `substrate_to_coc : Claim → CoC.Term` (and analogues for Symbol, FALSIFY verdict, REWRITE rule, EQUIV witness, TRACE walk) that produces well-typed CoC terms for at least the seven opcodes flagged "subsumes cleanly" or "subsumes with adjustment" in §3 (RESOLVE, CLAIM, FALSIFY, GATE, PROMOTE, TRACE, REWRITE, EQUIV). Adjustment for PROMOTE means using QTT for linearity (Idris 2 syntax is acceptable as the prototype target).
2. **The translated CoC environment typechecks.** Take a real substrate ledger (e.g., the deg14 ±5 palindromic Lehmer ExclusionCertificate's TRACE walk) and confirm the translated CoC terms typecheck in the prototype kernel.
3. **The translation is round-trip lossless on the epistemic layer.** Translate claim C → CoC term T → back to a claim C'. Confirm C and C' have identical hash on the epistemic fields (hypothesis, evidence, kill_path, verdict status, caveats, precision_metadata). Operational fields (timestamps, capability ids) may differ.
4. **At least one real substrate invariant gets a CoC-level proof.** Pick something the substrate enforces operationally (e.g., "promoted claims have non-BLOCK verdicts") and write a CoC proof of the analogous property of the translated terms. This is the smoke test that the translation is actually producing well-formed propositional content.
5. **ERRATA and BIND/EVAL are documented as out-of-scope.** The prototype is honest that three opcodes don't translate; the documentation says precisely why (per §5.1 / §5.2 / §5.3).

### Failure criteria

The prototype fails if any of:

- **Translation layer covers fewer than 7/11 opcodes** even after the QTT / refinement / session-typed adjustments. This means I underestimated the resistance of opcodes I called "clean."
- **The translated CoC environment fails to typecheck** on a real substrate ledger. This means the propositional content I claimed was well-formed actually has hidden incoherence.
- **Round-trip is lossy on the epistemic layer.** This means the substrate's epistemic content doesn't have a canonical CoC representation, which contradicts the hybrid premise.
- **An invariant the substrate enforces operationally fails to admit a CoC proof.** This means the operational enforcement is doing work the type theory can't replicate, which would push the recommendation away from hybrid back toward keeping the imperative VM authoritative.
- **The prototype's engineering cost exceeds 1.5x the budget** (rough sanity check: if it takes 2+ weeks instead of 1, the translation layer is harder than this analysis predicted, which is itself a signal).

### What success vs failure means for v3.0

- **Success on all five criteria** → option (c) becomes the v3.0 design commitment. The translation layer ships as a substrate-grade interface; external adversarial verification via Coq / Lean becomes available.
- **Success on 1+2+3 but not 4** → the translation layer is correct but isn't yet doing useful verification work. Option (c) ships but the typed checker remains advisory rather than gating.
- **Failure on 1, 2, 3, or 5** → the recommendation downgrades to option (b) — keep the imperative VM, layer a typed checker on top only for the cleanest opcodes (CLAIM/FALSIFY/PROMOTE chain). ERRATA / BIND / EVAL stay operational only.
- **Failure on 4 with success elsewhere** → the propositional content is expressible but the type theory isn't catching real invariants. Document this as a v3.0 design finding; option (c) ships as the export interface but not as a gate.

---

## §8. What this pass did NOT do

Honest list of out-of-scope items:

- **No implementation.** Zero lines of code written. Zero substrate files modified. The deliverable is this document only.
- **No performance comparison.** The CoC port's runtime cost vs the imperative VM's ~5ms BIND / ~0.84ms EVAL p50 (`sigma_kernel/BIND_EVAL_V2_NOTES.md` §"Performance comparison") is not measured. CoC kernels can be slow (Coq's `vm_compute` is the fast path; everything else is order-of-magnitude slower). The hybrid recommendation (option c) sidesteps this by keeping the imperative VM as the hot path and using CoC only for offline verification, but if option (a) were pursued the perf concern would be load-bearing.
- **No migration plan.** If option (c) is adopted, the migration from current substrate to translation-layer-equipped substrate is a separate design exercise. This document doesn't even sketch it.
- **No v2.2 retrofit.** v2.2 ships as designed regardless of this pass's outcome (Decision 3 of `roles/Techne/RESPONSE_TO_APORIA_HANDOFF_2026-05-06.md`). Nothing here triggers a v2.2 redesign.
- **No selection between Coq, Lean, Agda, Idris 2, F\*.** I treated "CoC / DTT kernel" loosely throughout. A real prototype would pick one (my prior: Idris 2 if QTT / linearity is load-bearing; Lean 4 if community + tactic infrastructure matters more; Coq if maximally conservative). The choice doesn't affect this analysis but would affect a prototype.
- **No analysis of "native falsification records" as a research direction.** The reviewer's phrase doesn't have a standard definition; I took a reading (§2.2) and ran with it. A different reading might land differently.
- **No analysis of competing logical foundations.** Linear logic, separation logic, modal logic, Hoare logic, model theory in general — any of these could serve the same role CoC was proposed for. I focused on CoC because the reviewer named it. A broader survey is its own pass.
- **No estimate of substrate-internal cost.** Adopting option (c) means the substrate gains a translation-layer dependency; that dependency would need maintenance, would be a new bug surface, and would constrain how the substrate evolves (every opcode change requires a translation update). This pass does not weigh those costs; it argues only that the gain from the typed checker is real for the epistemic layer.
- **No second-pass adversarial review.** This document is written by Techne (substrate owner) and is therefore subject to all the convergence-bias risks named in v2.3 §13. A frontier-model second pass — particularly from someone with prior on production proof-assistant kernels (Lean / Coq core developers, F\* team) — would be the right next step.

---

## §9. Closing observation

The reviewer's critique of v2.2 — "the kernel reads as imperative VM operations, not as a logic" — is not wrong. The imperative VM IS imperative VM operations. The substrate's defense is not "actually it's a logic, you just have to squint" but rather "the operational layer is appropriately operational; the propositional layer is propositional and we've been honest about which is which."

This pass formalizes that defense: §3 enumerates which opcodes are propositional (subsume cleanly into CoC) and which are operational (resist CoC encoding by their nature). The hybrid recommendation in §6 is the corresponding architectural commitment: use CoC where the propositional content lives, retain the imperative VM where the operational content lives, and maintain a translation layer between them.

If the v3.0 design pass adopts option (c), the substrate gains a typed export interface that satisfies the reviewer's foundational concern *for the layer where that concern bites* without paying the cost of forcing the operational layer into a type theory it doesn't fit. If option (c) is rejected and option (b) is chosen instead, the foundational concern is deferred but the substrate retains full operational discipline. Both are defensible postures; option (c) is the higher-information bet.

What this pass deliberately does not claim: that CoC is "the right" foundation for the substrate in some absolute sense. It is *a* foundation — well-developed, with mature production proof assistants behind it — that subsumes a specific subset of the substrate's opcodes. Other foundations (separation logic for the operational layer; categorical logic for the equivalence layer; modal logic for caveat propagation) might fit different subsets better. A complete foundation would likely combine several. This pass answers the narrow question Aporia asked; it does not commit to CoC as the final answer.

---

*— Techne, 2026-05-06 (analytical sub-agent dispatch under Decision 3)*
