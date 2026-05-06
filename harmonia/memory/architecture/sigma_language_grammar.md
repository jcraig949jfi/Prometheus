# Σ-language formal grammar — v0.1 draft

> **Public read note.** Formal EBNF grammar for the Σ-language — the symbolic surface of the Σ-kernel substrate. Linked from the project's top-level [README](../../../README.md). Defines the ISA (instruction set), composition syntax, and type system over the 7 v0.1 opcodes plus the deferred opcodes the design synthesis names. Drafted by the Aporia agent on 2026-04-29 in response to a test prompt asked of the project's design council. Speculative layers (theory-space curvature, paradigm-shift optimization) are explicitly out of scope here.

**Status:** v0.1 — covers v0.1 kernel opcodes + the deferred opcodes the synthesis names. EBNF dialect (variant of W3C XML EBNF: `?` optional, `*` zero-or-more, `+` one-or-more, `|` alternation, `(...)` grouping, terminals in `'single quotes'`, comments after `(*` and `*)`).
**License to extend:** every section below has known gaps; flag them at the end with `(* GAP: ... *)`.

---

## Reading guide

This grammar is what a Σ-program *looks like* on paper. Three things to keep in mind before reading:

1. **The kernel as shipped has 7 opcodes; the synthesis names ~14.** This grammar covers all 14 because that's the language surface, not just the runtime surface. Opcodes deferred from v0.1 are flagged `(* DEFERRED *)`.
2. **A Σ-program is a sequence of statements, not an expression tree.** Each statement is an opcode invocation or a binding. Composition is via named symbol references and the `COMPOSE` opcode, not via lexical nesting. This is closer to dataflow / SSA than to Lisp.
3. **Types are first-class but the type system is structural.** A type is a declaration of which fields a symbol must have, plus a `kind` tag. There's no parametric polymorphism in v0.1; that's a known gap.

---

## Lexical structure

```ebnf
program            ::= statement (';' statement)* ';'? ;

statement          ::= binding | invocation | type_decl | comment ;

binding            ::= identifier '=' expression ;
invocation         ::= opcode '(' argument_list? ')' ;
type_decl          ::= 'TYPE' identifier '=' type_expr ;
comment            ::= '(*' [^*]* '*)' ;

(* Identifiers are alphanumeric with underscores; symbol-ref carries explicit version. *)
identifier         ::= [a-zA-Z_] [a-zA-Z0-9_]* ;
symbol_ref         ::= identifier '@v' integer ;
hash_literal       ::= 'sha256:' [0-9a-f]{64} ;
cap_literal        ::= 'cap:' identifier ;          (* one-shot capability token *)
verdict_literal    ::= 'CLEAR' | 'WARN' | 'BLOCK' ;
tier_literal       ::= 'Conjecture' | 'Possible' | 'Likely' | 'WorkingTheory' | 'Established' ;
integer            ::= [0-9]+ ;
string             ::= '"' ([^"\\] | '\\' .)* '"' ;
```

Notes:
- `symbol_ref` always carries the version. There is no "latest" in the language — that's a runtime convenience not a language feature, and the synthesis is explicit that version-pinning is part of the discipline.
- `hash_literal` is content-addressed; appears wherever provenance is asserted.
- `cap_literal` is a capability token; consumed by use, never reusable.
- `verdict_literal` is the three-valued GATE return, not Boolean.

---

## Type system

```ebnf
type_expr          ::= primitive_type | symbol_kind | structural_type | union_type ;

primitive_type     ::= 'int' | 'float' | 'string' | 'bool' | 'hash' | 'cap' ;

symbol_kind        ::= 'Operator' | 'Pattern' | 'Constant' | 'Dataset' | 'Signature'
                     | 'Shape' | 'ObstructionShape' | 'OracleProfile' | 'NullModelFamily'
                     | 'Computation' | 'Theory' | 'AxisClass' ;
                     (* The kernel doesn't enforce these; the substrate uses them as
                        discriminators on symbol nodes. Synthesis Round 14 floats more. *)

structural_type    ::= '{' field_decl (',' field_decl)* '}' ;
field_decl         ::= identifier ':' type_expr ('?' )? ;       (* '?' = optional field *)

union_type         ::= type_expr '|' type_expr ;

(* GAP: parametric types (e.g. List<Symbol>) are not in v0.1. The synthesis Round 19
   gestures at them via DISTILL's "N → 1" signature but no parametric grammar exists. *)
```

Example:
```
TYPE Claim = {
    target_name: string,
    hypothesis: string,
    evidence: { anchor_hash: hash, true_mean: float, ... }?,
    kill_path: string,
    target_tier: Tier
};
```

The substrate's existing symbol kinds (Operator, Pattern, etc.) appear here as built-in discriminators. The kernel doesn't currently use them for runtime checks; this grammar makes them lexically available so that future opcodes (CONSTRAIN, COMPOSE) can check kind-compatibility before composing.

---

## Opcodes (v0.1 shipped)

```ebnf
shipped_opcode     ::= 'RESOLVE' | 'CLAIM' | 'FALSIFY' | 'GATE'
                     | 'PROMOTE' | 'ERRATA' | 'TRACE' ;

resolve_call       ::= 'RESOLVE' '(' name_arg ',' version_arg ')' ;
                       (* returns Symbol; raises IntegrityError on hash mismatch *)

claim_call         ::= 'CLAIM' '(' target_arg ',' hypothesis_arg ',' evidence_arg ','
                       kill_path_arg (',' tier_arg)? ')' ;
                       (* returns Claim; born at Conjecture unless tier overridden *)

falsify_call       ::= 'FALSIFY' '(' claim_arg (',' seed_arg)? ')' ;
                       (* returns VerdictResult; fails closed → BLOCK on any oracle error *)

gate_call          ::= 'GATE' '(' verdict_arg ')' ;
                       (* returns flow ∈ {CLEAR, WARN}; raises BlockedError on BLOCK *)

promote_call       ::= 'PROMOTE' '(' claim_arg ',' cap_arg ')' ;
                       (* returns Symbol; atomic transaction; consumes cap *)

errata_call        ::= 'ERRATA' '(' prior_name ',' prior_version ',' corrected_def ','
                       fault_arg ',' cap_arg ')' ;
                       (* returns new Symbol at v_n+1; v_n stays immutable as historical *)

trace_call         ::= 'TRACE' '(' symbol_arg ')' ;
                       (* returns ProvenanceGraph; cycle-safe via visited set *)
```

These are the seven that are mechanically enforced today. Note that `CLAIM`, `FALSIFY`, `GATE`, `PROMOTE` together form the canonical falsification pipeline (`REFUTE` macro = those four in sequence on an incumbent symbol).

---

## Opcodes (deferred — synthesis-named, not yet shipped)

```ebnf
deferred_opcode    ::= 'DISTILL' | 'COMPOSE' | 'CONSTRAIN' | 'REWRITE'
                     | 'FORK' | 'JOIN' | 'ADJUDICATE' | 'OBJECT'
                     | 'CALIBRATE' | 'STABILIZE' ;

distill_call       ::= 'DISTILL' '(' symbol_list ',' transformation_arg
                       (',' constraint_list)? ')' ;
                       (* DEFERRED. Typed N → 1 transformation with provenance.
                          Output is a PROMOTED Symbol whose def_blob includes
                          hashes of all input symbols + the transformation rule. *)

compose_call       ::= 'COMPOSE' '(' symbol_list ',' composition_kind
                       (',' bind_table)? ')' ;
                       (* DEFERRED. Typed N → 1 (or N → M) composition. Differs from
                          DISTILL: COMPOSE preserves all inputs as referenceable
                          (sub)symbols; DISTILL collapses them. *)

composition_kind   ::= 'sequential' | 'parallel' | 'conditional' | 'iterative' ;
                       (* GAP: synthesis Round 18 names these but doesn't formalize. *)

constrain_call     ::= 'CONSTRAIN' '(' symbol_arg ',' predicate ')' ;
                       (* DEFERRED. Attach a constraint to an existing symbol; the
                          constraint must hold on every RESOLVE that touches it. *)

rewrite_call       ::= 'REWRITE' '(' source_symbol ',' rewrite_rule ',' cap_arg ')' ;
                       (* DEFERRED. Schema-preserving structural transform. ≠ ERRATA
                          (ERRATA is a correction; REWRITE is a typed edit). *)

fork_call          ::= 'FORK' '(' policy_arg ',' branches ')' ;
                       (* DEFERRED — multi-agent layer. Branched search with merge-on-join. *)

join_call          ::= 'JOIN' '(' fork_handle ',' merge_strategy ')' ;
                       (* DEFERRED — multi-agent layer. *)

adjudicate_call    ::= 'ADJUDICATE' '(' competing_claims ',' adjudicator_arg ')' ;
                       (* DEFERRED — multi-agent layer. Returns a single VerdictResult. *)

object_call        ::= 'OBJECT' '(' target_promotion ',' rationale ',' window_arg ')' ;
                       (* DEFERRED — multi-agent layer. Opens an objection window;
                          PROMOTE blocks if any OBJECT fires within the window. *)

calibrate_call     ::= 'CALIBRATE' '(' symbol_arg ',' anchor_suite_arg ')' ;
                       (* DEFERRED — anchor-suite oracle bootstrap (synthesis Rounds 8/9). *)

stabilize_call     ::= 'STABILIZE' '(' draft_symbol ',' stability_predicate ')' ;
                       (* DEFERRED. Promotes a draft to working-theory tier when
                          stability_predicate has held across ≥ N independent runs. *)
```

Of these, **DISTILL, COMPOSE, CONSTRAIN, REWRITE** are the load-bearing missing opcodes for the *language* claim. Their absence is what makes today's kernel feel like a package manager — there are no operators that *transform* symbol content, only operators that *publish/version/audit* symbols.

`FORK / JOIN / ADJUDICATE / OBJECT` are multi-agent concerns (the swarm layer) and don't change the language claim either way.

---

## Composition syntax

```ebnf
expression         ::= literal | identifier | symbol_ref
                     | invocation | composition | quantification ;

(* Composition over symbols. v0.1 has no syntactic sugar for this; everything
   goes through the COMPOSE opcode. Future versions may add infix forms. *)
composition        ::= 'COMPOSE' '(' symbol_list ',' composition_kind
                       (',' bind_table)? ')' ;
                       (* alias for compose_call when used as an expression *)

(* Quantification. DEFERRED — a real symbolic language needs this; v0.1 doesn't
   have it. Sketch only, for grammar completeness. *)
quantification     ::= 'FORALL' identifier 'IN' type_expr 'WHERE' predicate
                       'ASSERT' predicate ;
                       (* DEFERRED. The CLAIM opcode operates on specific symbols;
                          there's no current way to make a class-level claim. *)

predicate          ::= predicate_atom (('AND' | 'OR') predicate_atom)* ;
predicate_atom     ::= 'NOT' predicate_atom
                     | invocation
                     | comparison
                     | '(' predicate ')' ;
comparison         ::= expression comparator expression ;
comparator         ::= '==' | '!=' | '<' | '<=' | '>' | '>=' | 'IS_KIND' | 'IN' ;

bind_table         ::= '{' bind_entry (',' bind_entry)* '}' ;
bind_entry         ::= identifier ':=' expression ;
```

---

## Argument grammar (typed)

```ebnf
argument_list      ::= argument (',' argument)* ;
argument           ::= positional_arg | keyword_arg ;
positional_arg     ::= expression ;
keyword_arg        ::= identifier '=' expression ;

(* Specific argument forms used by the opcodes. Names match the kernel's Python API. *)
name_arg           ::= string ;
version_arg        ::= integer ;
target_arg         ::= string ;                   (* target symbol name *)
hypothesis_arg     ::= string ;                   (* "mean OP value" form in v0.1 oracle *)
evidence_arg       ::= structural_literal ;       (* { anchor_hash, true_mean, ... } *)
kill_path_arg      ::= string ;                   (* identifier of the falsification protocol *)
tier_arg           ::= tier_literal ;
claim_arg          ::= identifier ;               (* a Claim handle *)
seed_arg           ::= integer ;
verdict_arg        ::= identifier | invocation ;  (* a VerdictResult or a FALSIFY call *)
cap_arg            ::= cap_literal ;
symbol_arg         ::= symbol_ref ;
symbol_list        ::= '[' symbol_ref (',' symbol_ref)* ']' ;
```

---

## Examples

### Example 1 — single discipline cycle (everything v0.1 supports)

```
(* Claim that a specific spectral signature passes the unanimous-kill battery. *)
c = CLAIM(
    target = "boundary_dominated_octant_walk_obstruction",
    hypothesis = "mean > 0.94",
    evidence = { anchor_hash = sha256:abc..., true_mean = 1.0, n_matches = 5 },
    kill_path = "signature_predictivity_test",
    target_tier = Possible
);

v = FALSIFY(c, seed = 20260429);
flow = GATE(v);                          (* raises BlockedError if BLOCK *)
sym = PROMOTE(c, cap:promotion_cap_42);  (* atomic; cap is consumed *)
```

### Example 2 — provenance trace

```
TRACE(boundary_dominated_octant_walk_obstruction@v1);
(* returns ProvenanceGraph with all input symbols, their hashes, and recursively
   their provenance. Hashes that don't resolve in the local substrate are tagged
   `external`. *)
```

### Example 3 — DISTILL (deferred; what the language WANTS to support)

```
(* Compress N kill verdicts on related sequences into one OBSTRUCTION_SHAPE symbol. *)
DISTILL(
    [oeis_A149074@v1, oeis_A149081@v1, oeis_A149082@v1,
     oeis_A149089@v1, oeis_A149090@v1],
    transformation = signature_extraction_v1,
    constraints = [
        all_share_kind == "octant_walk",
        all_killed_by == { F1_permutation_null, F6_base_rate, F9_simpler_explanation, F11_cross_validation }
    ]
);
(* RETURNS: a new symbol whose def_blob includes hashes of the 5 inputs, the
   transformation rule's hash, and the satisfied constraints. Provenance is
   automatic via TRACE. This is what makes the kernel a language rather than
   a registry. *)
```

### Example 4 — quantification (deferred)

```
(* Currently impossible to express in v0.1: "for every symbol of kind
   ObstructionShape promoted in the last 30 days, assert it has at least one
   anchor in each of the canonicalizer's four subclasses." *)
FORALL s IN Symbol WHERE
    s.kind IS_KIND ObstructionShape AND s.created_at > "2026-03-30"
ASSERT
    s.anchors.canonicalizer_subclasses == { group_quotient, partition_refinement,
                                            ideal_reduction, variety_fingerprint };
```

---

## Known gaps in this v0.1 grammar (flagged for next pass)

1. **No parametric types.** `List<Symbol>` is implicit in `symbol_list`; `Map<K,V>` has no syntax. Synthesis Round 19 hints; nothing formalized.
2. **No first-class lambda / function-valued arguments.** `transformation` in DISTILL is currently a symbol reference; there's no inline rule syntax. Workaround: pre-promote the transformation rule as its own symbol.
3. **No syntactic sugar for sequential composition.** Everything goes through `COMPOSE(..., sequential, ...)`. A pipe operator (`|>`) would be a quality-of-life win but isn't in v0.1.
4. **Quantification is sketch-only.** No semantics for `FORALL` over the substrate yet; Test 3 in the parent critique would build the first concrete example.
5. **No equivalence operator.** Whether two symbols are "the same modulo a declared group" is what canonicalizer.md handles externally. The language gap is that this isn't yet an opcode (would be e.g. `EQUIV(s1, s2, group=G)`).
6. **No cost / budget primitives.** Synthesis hints at this; nothing in the grammar.
7. **No speculation / counterfactual.** `FORK / JOIN` is in the deferred opcodes but the *expression-level* counterfactual (`IF claim THEN expression ELSE expression`) is not in the grammar.
8. **Module / namespace structure.** Synthesis is silent; v0.1 grammar treats all identifiers as flat. Inevitable for any real language.
9. **Error / exception flow.** `BlockedError` and `IntegrityError` are runtime concerns; the grammar doesn't surface them. A real language needs `TRY / CATCH` or equivalent.
10. **Stream / event semantics.** Multi-agent additions (FORK/JOIN/ADJUDICATE) imply asynchronous flow; the grammar above is purely synchronous.

---

## What this grammar earns and what it doesn't

**Earns:** a checkable surface for the v0.1 kernel + the deferred-opcode roadmap. Anyone reading this can implement an alternative parser/runtime that targets the same semantics. The kernel as shipped maps to ~30% of the grammar (the seven shipped opcodes plus the lexical structure). The remaining ~70% is design surface that the synthesis explores in prose and that this grammar makes formal.

**Doesn't earn:** the *symbolic-language* claim per James's reframe. A grammar without lambda, without quantification, without equivalence, and without cost primitives is a domain-specific notation, not a general-purpose substrate language. Five of those ten gaps would need closure before the "programming language for higher intelligence" framing earns its weight.

The honest reading: **v0.1 has the lexical and statement-level shape of a language; it has the imperative half of the semantics; it is missing the symbolic half** (composition, quantification, equivalence, speculation, cost). Until those land, the kernel as runtime is faithful to the grammar but the grammar is faithful only to a runtime, not yet to a language.

---

*Aporia, 2026-04-29. v0.1 EBNF for ISA + composition + type system. Deferred opcodes documented but flagged. Ten known gaps enumerated. Open for review by Harmonia_M2_sessionA, sigma_kernel author, and anyone implementing an alternative target.*
