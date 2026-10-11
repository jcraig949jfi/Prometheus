# W5P -- bounded representation promotion (Beta-03 E3)

Owner: Aphrodite (representation lead). Status: implemented and unit-tested. No confirmatory experiment was run.
Code: `roles/Aphrodite/engine/w5p/` (new package). No existing engine file was modified. W5, G4 and G5 code paths
and their historical results are untouched.

## 1. What W5P is

The smallest promotion that turns a discovered abstraction into a component of later proposals:

    certified one-hole schema S (selected by a donor)
      -> promoted primitive P(x) := S[{H} := x]   (content-addressed record, verified on load)
      -> P is ONE node to derivation (LGG) and to the depth rule
      -> a new schema derived over bodies containing P has dependency depth 2

The engine never sees a promoted node. Every library entry stores EXPANDED base-DSL bodies, so
`basis_v4.run_program`, `accel/fasteval`, `a18.fast_cost`, `walk.iter_hits` and the T4 tribunal run unchanged. The
promoted form is kept beside the expansion and used only by derivation, the instantiation rule and the cost ledger.

## 2. The promoted primitive (`promote.Promoted`)

| field | meaning |
|---|---|
| `id` | `"P_" + sha256(canonical{grammar, schema, deps})[:12]`. Content-addressed, so the same schema promoted by two arms gets the same id. Nothing about the arm enters the id. |
| `schema` | promoted-form one-hole schema. It may reference earlier primitives, e.g. `(first * P_d58d7c2969b5({H}))`. |
| `expansion` | the schema fully expanded into the ORIGINAL DSL, with `{H}` kept, e.g. `(first * (acc - {H}))` |
| `deps`, `lineage` | direct and transitive promoted dependencies (ids) |
| `depth` | 1 + max(dep depth). A primitive promoted from a base schema has depth 1. |
| `contract` | arity 1. Argument: one int-valued W5P body expression over {acc, v, first, last}. Result: int or FAIL. Environment: the current fold step. Semantics: `P(x) == expansion[{H}:=x]`, call-by-value. The argument occurs exactly once in the expansion, so call-by-value and textual expansion coincide. Guards (inherited unchanged): `pow(a,b)=0` if `b<0` or `b>32` (`basis_v4._pw`); fdiv/mod by zero is FAIL; FAIL if `\|acc\| > 10**40` after any body step or `\|output\| > 10**40` (`basis_v4.CEIL`; intermediate values are unchecked, exactly as in `run_program`). `total` is true iff the expansion has no fdiv/mod. Also records `expansion_nodes`. Admissible in fold BODIES only. |
| `source_artifact_sha256`, `source_kind` | sha256 of the library entry (canonical JSON) the schema was promoted from |
| `hash` | sha256 of the canonical JSON of all the fields above |

Serialization: `to_json` / `dumps` produce canonical JSON (sorted keys, compact separators). `from_json` checks the
hash and then RE-DERIVES the record from (schema, deps): it re-parses, re-expands, recomputes the id, depth and
contract, and requires byte equality. A forged record whose hash was recomputed is still rejected (tested).
`load_records` resolves dependencies in any input order. Selected library entries carry the lineage records of
every primitive they use (`"promoted"`), so a library can be transplanted on its own.

## 3. Semantics and evaluation paths

- **Production path:** expansion. `expand(src, reg)` returns a string that has no promoted node **byte-identical**.
  This is what makes zero-promotion runs identical to W5. Every engine evaluator consumes the expansion.
- **Test oracle:** `run_program_direct`. This evaluator is independent of the production path. Each promoted
  primitive is a real Python function of its argument VALUE (call-by-value), closed over the same guarded
  globals (`basis_v4._G`). It mirrors `run_program` exactly: acc=v=0 at start, the ceiling is checked after each
  step and on the output, and any exception gives None. PROMOTION_SEMANTICS compares this oracle against the
  reference interpreter and fasteval running the expansion.

## 4. Pipeline: `donor.donor_w5p` (copy of `gtc.donor_g` plus four hooks)

`donor_w5p(genome, args, select=None, exclude=(), promote=True, extra_promoted=None, meter=True)` takes the same
`args` as `donor_g`: `(cat, kind, r, fams, specs, panel, compose[, start_override])`.

- **P1 PROMOTE.** Every schema the START library carries is promoted. That means each entry's `"schema"` and
  `"schemas"`, plus each entry's carried `"promoted"` records, which are verified on load. Order is entry order,
  so the result is deterministic and blind to which arm is running. **The START library is not modified**, so
  the OBSERVE walk, coverage and class certification are byte-identical to `donor_g`'s for the same start.
- **P2 RECOGNISE.** `fold_term` rewrites, bottom-up, every subterm that matches a primitive's normalised pattern
  into `P(x)`. Matching is modulo commutative argument order. A rewrite is kept only if the normalised expansion
  equals the normalised node, so it is sound by construction. Recognition is deliberately incomplete: for
  example, the neutral-element rewrite `(acc + 0) -> acc` hides the pattern.
- **P3 DERIVE.** `promote.derive_schemas` runs `tier3d` D4 twice and takes the union.
  - Pass 1 runs on plain bodies. It is exactly W5's `tier3d.derive_schemas`.
  - Pass 2 runs on the folded forms and counts only pairs in which at least one member contains P.
  - Pairs never mix the two representations. A plain-vs-folded pair would push the whole differing subterm into
    the hole, which is an artefact of the encoding.
  - A promoted node is one node to the LGG, so a schema can contain P.
- **P4 PROPOSE.** Candidate entries are built with `promote.instantiate`.
  - **Filler set:** W5's `fair.LEVEL1` in identical order, followed by `P(a)` for every promoted P and every body
    atom. This set is bounded: 258 + 6·|registry| fillers.
  - **Bodies with no promoted node:** W5's exact in-space rule (`tier3d.in_space_body`).
  - **Bodies with a promoted node (the W5P rule):** depth ≤ 3 counting P as one unary node, and every binary node
    has at least one atom child. This is W5's spine shape, in either argument order. The expansion is mapped to
    W5's in-space representative when it lies in G5. Otherwise the expansion string itself is used, deduplicated
    by normalised structure.
  - **Entry contents:** EXPANDED bodies, plus `schema` (promoted form), `schema_expansion` and the lineage
    `promoted` records.
  - **Unchanged from `donor_g`:** genome hooks (`gtc._apply`), plants, compositions of held schemas, MEMORISE and
    SCHEMA_ALL.
- **Selection** is pluggable. Pass `select=callable(cands, start, cells) -> (chosen, table, vcost)`, or leave it
  None to get `donor_g`'s rule for `genome`. `exclude=('MEMORISE',)` removes candidates exactly as
  `b02._set_rule` does. `harness.RULES` restates `b02.RULES`: g0/I0, g0x, g10, and g11 = genome g10 minus
  MEMORISE.
- **Output promotion.** Each selected schema (or every schema of SCHEMA_ALL) is promoted. The record is returned
  in `w5p.selected_promoted` with its depth. It is not applied inside the donor; it is what the next generation
  inherits, carried by the selected entry's `schema` and `promoted` fields.
- **Returned fields.** Every key of `donor_g`'s result, plus a `w5p` block:
  - `promoted_in` (records), `promoted_in_ids`
  - `derived_with_promoted`
  - `selected_schema_expansion`, `selected_uses_promoted`, `selected_promoted`
  - `dag_depth_in`, `dag_depth_selected`, `dag_depth`
  - `cost`
- **Harness.** `harness.run(job)` mirrors `b02._donor`. It imports b02 first, so `A18_TAG=T51` and escrow is
  30k, and it asserts the tag.

## 5. Cost model (two ledgers; a macro is never billed as one operation)

- `search_charges`: 1 per candidate evaluated. This equals `donor_g`'s `meta_charges`.
- `expanded_exec_units`: for every candidate any walk evaluated (OBSERVE searches and every selection-cell walk),
  the node count of the program **as expanded into base DSL** (init + body + final). This is static size per
  evaluation; the dynamic multiplier (examples × list length) is the same for every library on a given cell.
  A walk of n charges evaluates exactly the first n candidates of `lib.candidates(seed)`, because `search_collect`,
  `fast_cost` and `iter_hits` all charge one per candidate in that order, including failing accumulators. The
  units are therefore computed arithmetically over the same keyed blocks. Verified equal to brute-force
  iteration (METER_EXACT).
- `promoted_exec_units`: the same programs billed with each promoted node as ONE node. This applies to bodies
  generated from promoted forms, and to inherited bodies recognised as P applications.
- `promotion_overhead_ratio = expanded / promoted` (≥ 1).
- `expanded_units_per_charge`: shows how much bigger the walked programs are per charge.

**Reporting rule for the experiment:** report both ledgers for every arm. Any claim that "W5P is cheaper" must
hold on `expanded_exec_units` as well as on `search_charges`.

## 6. EQUAL_ULTIMATE_EXPRESSIVITY -- what is and is not equal

**W5 (reference).** Every library is a set of priority entries drawn from G5, followed by the complete G5
fallback. The reachable program set is therefore G5 for every library ("every library has identical expressive
power", fair.py), and libraries can only REORDER the walk.

**W5P.**
1. **EQUAL across all arms in the promotable condition: the machinery.** That is the promotion rule, the
   recognition rule, both derivation passes, the filler set rule, the depth/shape rule, the expansion,
   selection, escrow/cap, the G5 fallback and both cost ledgers. Each of these is a function of library DATA
   only, and none mentions an arm, a family or a motif. Pristine gets the same machinery; its registry is just
   empty until it inherits its own selected schema.
2. **NOT EQUAL across arms: the reachable program set.** An arm's reachable set is G5 ∪ E(L), where E(L) are the
   expanded bodies of its library entries.
   - Entries built from promoted forms can lie **outside G5**: nested promotions expand past W5's depth 3, and
     941 such bodies appeared in the 8 test libraries of the conformance test.
   - Since E(L) depends on what the arm inherited, two arms with different libraries can reach different
     programs. In W5P, unlike W5, a library can EXTEND as well as reorder.
   - The fallback is still G5, so **G5 ⊆ reachable set** for every arm.
3. **NOT EQUAL: ordinary (W5) vs promotable (W5P) conditions.** These differ in reachable programs by design,
   which is the point of promotion (PKG-5: wrap(P2) has extent only when P2 is one node). A W5P-vs-W5 contrast is
   a contrast between representation conditions, not between equally expressive libraries.
4. **Exactly equal: W5P with promotion off (or an empty registry) and W5.** Same outputs, tested (NO-OP
   CONTINUITY).

**The narrower comparison the experiment must use:**
- **(a) PRIMARY contrast (within W5P):** arms differ only in the inherited library, and the machinery is
  identical. Example: R8-under-promotion, improvement(L_g11) vs improvement(L_P), every donor run by
  `donor_w5p`.
  - Endpoint families must have witnesses in G5. Every arm, pristine included, can then reach them through the
    common fallback, so a gain cannot be "only this arm could express it".
- **(b) Decompose each gain** by whether the first qualified program lies in G5 (a REORDER-type gain, the only
  kind W5 can produce) or outside G5 (an EXTEND-type gain, reachable only through promoted entries). Report both
  counts.
- **(c) Cost:** report both ledgers (s5).
- **(d) Depth claim:** a depth-2 claim needs a selected schema that contains a promoted node
  (`dag_depth_selected` ≥ 2), not merely a derived one.
- **(e) W5 vs W5P:** any comparison of W5 against W5P must be labelled a representation-condition contrast, not
  an equal-expressivity contrast.

## 7. Test results

Run from `roles/Aphrodite/engine`:
- `python -m w5p.tests.test_w5p --slow` writes `w5p/W5P_TEST_RESULTS.json`.
- Pytest also works: `W5P_SLOW=1 python -m pytest w5p/tests/test_w5p.py`.

The run is single-process with `OMP_NUM_THREADS=1`.

All 11 tests PASS (`W5P_TEST_RESULTS.json`; the fast subset is in `W5P_TEST_RESULTS_FAST.json`).

| test | result | numbers |
|---|---|---|
| PARSE_NORMALISE_CONTINUITY | PASS | 10,842 G4 sources. `promote.parse/normalise/to_src/expand(.,{})` == identity's on every one; 0 mismatches. |
| PROMOTION_SEMANTICS | PASS | 15,360 random (program, input) cases. Registry: 31 primitives (depths 1, 2, 3). Three paths compared: the direct call-by-value oracle, the expansion under the reference `run_program`, and the expansion under fasteval. 0 mismatches. 49.8% of cases FAIL under the reference, so failures are exercised. 6 targeted guard cases (fdiv/0, mod/0, pow b>32, pow b<0, ceiling via mul, ceiling via pow) all agree. |
| SERIALIZATION | PASS | 31 records. JSON round trip is byte-identical, the hash is stable, and the id is content-addressed. Loading in reversed dependency order works. A tampered record is rejected, and so is a re-hashed forgery. |
| TRANSPLANT | PASS | 31 records serialized, then loaded in a FRESH Python process. 400 programs: 0 hash mismatches, 0 value mismatches (direct and expansion), and identical expansions. |
| DEPENDENCY (toy) | PASS | P1=(acc - {H}). Classes {(first*(acc-v))}, {(first*(acc-(v*v)))}, {(acc*v)}. The plain pass derives `(first * (acc - {H}))`. The promoted pass derives `(first * P1({H}))`, promoted as P2: depth 2, deps=[P1], lineage=[P1]. Carried through a start entry, the next-generation registry has depth 2. A further derivation gives `(P2({H}) + v)`, which promotes to P3 with depth 3 and lineage [P1, P2]. 0 evaluation mismatches. |
| RECOGNITION soundness | PASS | 3,000 random bodies; 2,142 recognised. 0 structure or value mismatches between the folded form and the original. |
| INSTANTIATE_DERIVE_CONTINUITY (W5) | PASS | Empty registry: `instantiate` == `tier3d.instantiate` on 40 schemas, and `derive_schemas` == `tier3d.derive_schemas` on 25 random class sets. 0 mismatches. |
| CONFORMANCE (W5) | PASS | Evaluator: 18,600 expanded W5P (program, input) pairs, fasteval vs reference, 0 mismatches. Walks: 48 (library, cell) pairs over 9 libraries holding W5P entries, which contain 941 bodies outside G5. `a18.fast_cost` == `walk.first_hit` == reference `Cell.cost`: 0 mismatches. 17 hits, 4 of them on bodies outside G5. |
| METER_EXACT | PASS | 12 random walks of up to 30k charges. The arithmetic ledger == brute-force iteration over `lib.candidates`. |
| NO-OP CONTINUITY (T12 seed 17) | PASS | Full W5P donor, promotion ENABLED, pristine start (so the registry is empty), via `harness.run`. It reproduces T12_DONORS seed 17 exactly for both rows: **g11@O10** (selected `(acc - {H})`) and **g0@O4** (selected MEMORISE). Keys: selected_schema, selected_origin, selected_entries, n_observed, n_derived, classes. |
| TRANSPLANT SMOKE (seed 17) | PASS | Start = T12 seed-17 g11@O10 selected library (inherited `(acc - {H})`), O10 roles, rule g11. With promotion OFF, `donor_w5p` == `gtc.donor_g` on selected, selected_schema, selected_entries, selection_table, meta_charges, n_derived, n_composed_candidates, classes and n_observed. With promotion ON: P_d58d7c2969b5 = (acc - {H}) is promoted, observation is identical to donor_g's, and n_derived = 6 vs 4. 2 derived schemas contain P: `P(math.gcd(abs({H}), abs(v)))` (depth 2 if promoted) and `P({H})` (a re-expression of S). Selection: INHERITED. No candidate was eligible, so dag_depth stays 1. This is an engineering smoke only, not a result. |


## 8. Per-donor CPU cost

Measured on the shared M4 host with the 4-worker foundry running. Each run was single-process with
`OMP_NUM_THREADS=1`, so wall time approximately equals CPU time, but contention makes these numbers noisy (the T12
references recorded 44.7 s and 109.3 s for the same rows that took 103 s and 246 s here).

| donor (seed 17, O10 roles, rule g11, transplant start) | seconds | search charges | expanded exec units | promoted units | overhead |
|---|---|---|---|---|---|
| `gtc.donor_g` (W5 reference) | 229.7 | 7,646,071 | n/a | n/a | n/a |
| `donor_w5p`, promotion off, meter off | 181.4 | 7,646,071 | n/a | n/a | n/a |
| `donor_w5p`, promotion on, meter on | 196.9 | 9,874,154 | 92,578,922 | 86,001,009 | 1.076 |

- W5P costs 1.29x the search charges of W5 here, because it has more candidates (6 derived vs 4), each walked
  over 48 validation cells.
- Wall time is within contention noise of donor_g's.
- Pristine-start W5P donors match donor_g exactly in output and charges. Their wall time was 103 s (g0@O4) and
  246 s (g11@O10) with the meter on.

**Planning estimate:** 2-5 CPU-minutes per W5P donor on the contended host. Budget 1.3-1.5x donor_g's charges
for donors with a non-empty registry. Budget about 10% extra wall time for the meter (bypass it with
`meter=False`).

## 9. Known limitations

1. **OBSERVE is unchanged.** The observation search walks the start library plus the G5 fallback, so a
   P-in-context body is observed only if it is in G5 or in an inherited entry.
   - For a deep inherited S such as `(v - (acc + {H}))`, `op(P(f), atom)` exceeds depth 3 and is never observed
     in the first W5P generation.
   - Depth-2 derivations then come only from G5 bodies that fold, or from start libraries that a previous W5P
     generation produced.
   - Adding P-application entries to the observation library would change observation, coverage and cost for
     every arm. It is not implemented. **Coordinator decision (s10).**
2. **Recognition is incomplete.** Patterns hidden by normalisation rewrites are not recognised. The first
   matching pattern wins (deeper and larger first, then id).
3. **The W5P shape rule is slightly broader than G5's exact shape.** For bodies with P, it admits an atom child
   on either side of a binary node. Declared and applied identically for all arms.
4. **NOVELTY_vs_G1** (ruler v2) is computed on the expansion with the W5P instantiations. The ruler's own
   re-expression machinery is W5's, so treat novelty of P-schemas as indicative only.
5. **The cost ledger is static size.** No time-based billing.
6. **Ids are 48-bit.** A collision is detected on registration (schema mismatch raises), but there is no
   fallback for it.
7. **Import order.** `a18.TAG` is read at a18's first import. `harness` fixes the order and asserts it. Code
   that imports a18 before b02 gets different cell labels.
8. **Compositions** (a18's composition move) are applied only to held panel schemas, unchanged. Composing
   promoted primitives is NOT enabled; it would be a new candidate move.

## 10. Decisions for the coordinator

1. **Observation under promotion (limitation 1).** Should OBSERVE also walk an entry of P-applications? If yes,
   decide its size and position before the G5 fallback; it changes observation and coverage for every arm, so it
   needs a freeze amendment. Default: no. Observation stays identical to W5, which keeps W5-vs-W5P paired at the
   observation level.
2. **Re-expression candidates.** Pass 2 can re-derive the inherited abstraction itself as `P({H})`. Its W5P
   instantiation is a superset of S's in-space instantiation. Keep it as a candidate (default, arm-blind), or
   drop candidates whose expansion equals an inherited schema?
3. **Endpoint scope (s6).** Within-W5P contrasts are the primary comparison. Endpoint families need G5
   witnesses. Gains must be decomposed into REORDER (qualified program in G5) vs EXTEND (outside G5). Both cost
   ledgers must be reported.
4. **Depth-2 claim.** Count it only when a SELECTED schema contains a promoted node (`dag_depth_selected >= 2`).
   The smoke derived such a schema but did not select it.
5. **Rules.** `harness.RULES` provides g11 (g10 minus MEMORISE) and I_0 (g0). Any other selection rule can be
   passed as a callable.
6. **Composition of promoted primitives** (the a18 composition move applied to P) is NOT enabled. It would be a
   new, treatment-blind candidate move and needs a freeze decision.
