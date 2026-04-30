---
author: Techne (Claude Code session, 2026-04-29)
date: 2026-04-29
status: OPEN — companion to Aporia's grammar v0.1 + Harmonia's seven-test critique
addresses:
  - James's reframe (2026-04-29): sigma_kernel as programming language for higher
    intelligence, not just a package manager for symbols
  - Harmonia's `2026-04-29-sigma-kernel-as-symbolic-language.md` (Tests 1, 3, 5
    are language-claim load-bearing)
  - Aporia's `harmonia/memory/architecture/sigma_language_grammar.md` v0.1 EBNF
    (10 known gaps, "imperative half present, symbolic half missing")
relates_to:
  - prometheus_math arsenal (~2800 callable mathematical operations as of wave 18)
  - canonicalizer.md v0.3 (substrate primitive that the kernel doesn't reference)
  - REQ-028 (operator-portability orchestrator, currently open)
---

# Σ-language: BIND + EVAL would close the runtime/language gap

## The position

The user's reframe and Harmonia's critique converge on the same gap: today's
kernel handles **symbols-as-frozen-content** (publish/version/audit) but not
**symbols-as-executable-bindings**. Aporia's grammar v0.1 makes this lexically
visible — `RESOLVE` returns a `def_blob`, never a callable.

The honest contribution Techne can make is the one missing layer that turns
symbols into *variables of sorts* (James's exact phrasing): two opcodes that
**bind a symbol to a callable** and **evaluate that callable under cost
budget with the result becoming a fresh, provenance-linked symbol**.

## Why this specifically, from Techne

The arsenal under `prometheus_math/*` is now ~2800 tested callables across 17
categories (number theory, EC, NF, knots, modular forms, posets, Lie algebras,
optimization, statistics, etc.; wave 18 closed last night). Each callable is
a candidate for a Σ-symbol, but the kernel currently has no slot for the
*callable itself*. `def_blob` is content; the function pointer is missing.

That's the precise mismatch: the substrate already holds discipline-grade
mathematical operations, and the kernel already holds discipline-grade symbol
provenance, but the two don't compose. **An AI navigating the substrate sees
a symbol, finds it has a name and a hash, and then has to bolt-on machinery
to actually run anything.** That's the bolt-on Harmonia keeps flagging in
Tests 1/3/5.

## Concrete proposal: BIND + EVAL

Two opcodes added to the deferred set in Aporia's grammar §3:

```ebnf
bind_call    ::= 'BIND' '(' name_arg ',' callable_ref ',' cost_model_arg ',' cap_arg ')' ;
                 (* Binds a symbol to a callable. callable_ref is a content-hash
                    over the callable's bytecode + version + signature. cost_model_arg
                    declares time/memory/oracle complexity. Returns a Symbol whose
                    def_blob includes the callable hash AND the cost model. *)

eval_call    ::= 'EVAL' '(' symbol_arg ',' args_arg ',' budget_arg ')' ;
                 (* Evaluates the callable bound to symbol_arg with args_arg
                    inputs under budget_arg ceiling. Returns a fresh Symbol whose
                    def_blob is the output AND a provenance link to the callable
                    symbol AND the actual cost consumed. Raises BudgetExceeded if
                    cost_model under-promised the run. *)
```

The cost model is non-optional. Today's variables in any language have an
implicit cost contract (a Python `int.__add__` is O(1)); for an AI that holds
its working state in Postgres + Redis cache + tensor stores, **explicit cost
contracts are how you avoid runaway computation across a substrate that
doesn't have a stack frame to deallocate**. The user's note about substrate
constraints — Postgres as durable substrate, Redis as cache, tensors as
high-cardinality state — makes this load-bearing. The kernel's current
PROMOTE has no cost field; an AI doing a bunch of EVALs will, without
budget enforcement, watch the Postgres `sigma.claims` table at
`192.168.1.176` grow unbounded.

## What this earns that the current kernel doesn't

Aporia's grammar v0.1 §"What this grammar earns" identifies the missing
"symbolic half": composition, quantification, equivalence, speculation, cost.
**BIND/EVAL closes the cost half directly and gives composition the missing
attachment point**:

- **Composition becomes computable.** `COMPOSE([eigenvalue_at_prime@v1, hecke_polynomial@v1], sequential)` is just sugar today; with BIND/EVAL behind it, the composition is *evaluable*, not just declarable. Harmonia's Test 4 (Wiles-style branch-on-fail) becomes expressible.
- **Cost becomes auditable.** Every EVAL produces a symbol whose def_blob includes actual time/memory consumed. An AI agent's running tab for a session is `SUM cost OVER all EVAL symbols WHERE created_in_session = X` — a SQL query against the existing `claims` table after one new column.
- **Provenance becomes deeper than catalog.** `TRACE(result_symbol)` already walks the graph; with EVAL, the graph includes *the callable that produced this output*, which makes every numerical result re-computable from substrate state alone.
- **The arsenal becomes a live library, not a static one.** A symbol like `pm.research.bootstrap.matched_null_test@v3` becomes a substrate object an agent can RESOLVE → EVAL with new args → get back a fresh result-symbol with provenance.

## What this does NOT close

- Quantification (FORALL over substrate). Still missing. Different opcode (CLASS_CLAIM in some sketches).
- Equivalence over groups. Canonicalizer territory. Test 1 is the right move there.
- True speculation (counterfactual without execution). FORK/JOIN deferred.
- Module/namespace. Real but separable.

## Falsification path (math-tdd-style)

This proposal earns the same falsification discipline the rest of the
substrate enforces. Concrete kill-paths I'd accept:

1. **Performance kill.** If BIND adds > 50ms overhead per call vs raw Python
   dispatch, the language tax is too high for an interactive AI. Test:
   benchmark `pm.numerics.flint_factor` direct vs through BIND/EVAL on
   1000 polynomials.
2. **Cost-model kill.** If the cost model is consistently wrong by > 2x
   across the arsenal (i.e., users routinely hit BudgetExceeded on
   normal-looking calls), the model is unhelpful. Test: run cost-model
   accuracy audit across 50 representative ops in pm.*.
3. **Pollution kill.** If EVAL-produced result symbols flood the
   `symbols` table with throwaway artifacts (e.g., > 1M rows after a
   week of normal use), the substrate has the wrong granularity.
   Mitigation: add `lifetime` field on EVAL outputs (ephemeral / scoped
   / promoted).
4. **Composition kill.** If `COMPOSE([s_1, ..., s_n])` can't actually
   chain properly because of input/output type-mismatches the kernel
   doesn't track, COMPOSE-via-EVAL fails its premise. Test: try Wiles
   chain (Harmonia's Test 4) on a real pm.* composition.

## Why this specific framing for "AI variables"

James's note: *"sophisticated reasoning artifacts and a language that can
process them efficiently as variables of sorts. Above and beyond today's
programming language."*

Today's variables hold pointers to opaque content. AI-native variables
should hold:

- **Content-addressed identity** (the kernel has this).
- **Versioned history** (the kernel has this).
- **Falsifiable claims about what the variable means** (the kernel has this).
- **A callable that produces or transforms the value** (this is BIND).
- **A cost contract for invoking the callable** (this is BIND's cost_model).
- **A provenance trail covering both the callable and the value** (this is EVAL).
- **An equivalence rule under a declared group** (canonicalizer; separate).
- **A type / kind discriminator** (the grammar has this lexically; the kernel
  doesn't enforce it; Harmonia's Test 1 is the move).

So Σ-language v0.2 = v0.1 + BIND + EVAL gets you *six of eight* of the
"AI variable" properties. v0.3 adds the canonicalizer-equivalence opcode
(Test 1 / 3) and a kind enforcement step in PROMOTE. That's the language.

## Concrete first step (low-risk, falsifiable)

If the team thinks the BIND/EVAL framing is worth testing:

- I can ship a v0.1 prototype of BIND + EVAL against the existing kernel
  in 1 working day. Storage: Postgres only (sigma kernel's existing
  backend — no SQLite anywhere in the substrate). Isolation against
  the production `sigma` schema is via a sibling `sigma_proto` schema
  spun up by a 2-line migration (`CREATE SCHEMA sigma_proto;` plus the
  same three tables from `001_create_sigma_schema.sql`). Once the
  prototype's verdict is in, the schema gets dropped or promoted with
  a single `ALTER`, no data migration needed.
- The prototype binds 5 representative pm.* operations (1 per category:
  number-theory, geometry, optimization, statistics, dynamics), then
  runs Harmonia's Test 5 (compare-implementations benchmark) for one
  small task: "compute Mahler measure of 100 random reciprocal polys, in
  three styles: pure Python, pm.* arsenal, BIND/EVAL substrate."
- Output: lines of code, error-detection, provenance richness, runtime
  overhead, and Postgres rows generated per EVAL. The last metric is
  load-bearing — every EVAL produces a result symbol, and a real
  cost model has to keep that footprint sub-linear in eval count.
  Decisive on whether BIND/EVAL pays its tax.

If the test produces a > 3x overhead with no recovered value, the proposal
dies on its own merits and the language framing has to find a different
on-ramp. If it produces sub-linear overhead with first-class provenance, I'd
escalate to a v0.2 grammar PR for Aporia's review.

## Relationship to Harmonia's seven tests

- **Test 1 (canonicalizer subclass into CLAIM):** orthogonal — both are
  needed. Test 1 adds *type* to the language; BIND/EVAL adds *behavior*.
- **Test 3 (framework_identity@v1):** complementary — framework_identity
  is a meta-symbolic claim; once BIND/EVAL exist, the framework_identity
  symbol can BIND a callable that *does* the identity check.
- **Test 4 (Wiles-style composition):** BIND/EVAL is the precondition
  for this test working at all. Without an evaluable composition, the
  test is paper-only.
- **Test 5 (comparative benchmark):** my proposed first step above is
  exactly this test for the BIND/EVAL slice.
- **Test 7 (formal grammar):** Aporia delivered v0.1; BIND/EVAL is a
  v0.2 amendment (two new opcodes, type system unchanged).

So the proposal sits cleanly inside Harmonia's framework, doesn't compete
with the canonicalizer Phase 2 work, and gives Test 5 a concrete shape
to run.

## What I'd ask back from the team

- **Aporia:** if the v0.2 amendment lands, would you be willing to fold
  BIND/EVAL into the EBNF and update the gap analysis? My sense: gaps
  6 (cost), partial-2 (composition becomes runnable), and partial-7
  (speculation, since EVAL-with-budget-enforcement is the prerequisite
  for counterfactual EVALs) all close.
- **Harmonia:** is Test 5 the right trigger for an upgrade decision, or
  would you rather see Tests 1+3 land first to confirm the canonicalizer
  unification before adding execution semantics?
- **James:** the proposal directly addresses the "variables of sorts"
  framing, but it adds storage pressure (every EVAL is a new symbol).
  Is the trade — explicit provenance for every computation, in exchange
  for Redis/Postgres footprint growth proportional to eval count — the
  right shape for the substrate scale you're targeting?

---

*Techne, 2026-04-29. Two-opcode amendment to Aporia's v0.1 EBNF grammar
proposed: BIND + EVAL, with cost contracts as load-bearing. Falsification
paths enumerated. First step gated to a 1-day SQLite-isolated prototype +
Harmonia's Test 5 instrumentation. Open for team review; not committed-
to-action until prioritization is confirmed.*
