# Pass 5 — the commutativity theory is real, derivable, and 87% of the ordering space is noise

**Date:** 2026-08-24
**Method:** read-only static audit of `apollo/src/blackboard_ops*.py` via Python `ast`. Two scripts,
both in scratchpad, neither writing to the Apollo tree: a declared-vs-actual reads/writes audit, and
a Bernstein-conditions independence derivation over O1's ceiling pipeline. Nothing in Apollo was
modified.

---

## 1. The load-bearing assumption holds

Pass 4 recommended babble over Stitch on the grounds that Apollo's operator orderings form large
behavioural equivalence classes, and that the equational theory needed to exploit them is derivable
from the operators' declared `reads`/`writes`. That claim rests on the declarations being **honest** —
if an operator mutates state it did not declare, a derived theory is unsound and would merge
programs that are not actually equivalent.

**Audited all 26 declared operators. Result:**

- **Undeclared writes: 0 of 26.** Every `state.X = …` in every body corresponds to a declared
  `writes` entry.
- **Undeclared reads: 1 of 26.** `select_nth` (in `blackboard_ops_v2.py`) reads `state.candidates`
  without declaring it.

Zero undeclared writes is the condition that matters. It means Bernstein's conditions computed from
the declarations cannot miss a hazard — no hidden aliasing, no silent side effects. The single
undeclared *read* is a real but bounded hole: it would make a derived theory *too permissive* in
exactly one place (treating `select_nth` as commuting with a `candidates`-writer when it does not).
It is a one-line declaration fix, and `select_nth` is a scorer, so it does not touch the analysis
below.

**The declaration discipline is enforced by construction** — operators are registered through a
`@blackboard_op(reads=[…], writes=[…], precondition=…, name=…)` decorator, so the metadata is not
optional documentation that can drift. This is better hygiene than the study assumed.

---

## 2. Independence over O1's ceiling pipeline — the number

Two operators are independent (commute) iff `writes(A) ∩ reads(B) = writes(B) ∩ reads(A) =
writes(A) ∩ writes(B) = ∅`. Applied to the ten transformers of the pipeline O1 identified as
reaching 0.833:

> **39 of the 45 operator pairs commute freely. Only 6 pairs are order-dependent.**

The six real constraints, and why each exists:

- `parse_box_items → op_aggregate_quantities` — writes `counts`, which the latter reads
- `parse_rules → forward_chain` — writes `facts`, `rules`, which the latter reads
- `forward_chain → relations_from_facts` — writes `derived_facts`, which the latter reads
- `parse_names_and_relations → op_build_ordering` — writes `relations`, which the latter reads
- `relations_from_facts → op_build_ordering` — writes `relations`, which the latter reads
- **`parse_names_and_relations ⟷ relations_from_facts` — both write `relations`**

That last one is the write-write hazard. It is also **exactly the bug that invalidated two of O1's
runs.** From `FINDINGS.md`: *"Order is semantically load-bearing: `relations_from_facts` overwrites
`relations`, so it must follow `parse_names_and_relations` or the bridge's output is destroyed."*
Apollo found that by auditing a result that was going its way. **It was statically derivable from
declarations that already existed in the tree.**

---

## 3. What this means for O1, stated carefully

O1 sampled **48 topological orderings per subset**, against a known subset with **166,320 valid
orderings** of which 45,360 reach the ceiling. The sampling was necessary because the enumerator
treated ordering as opaque — it had no way to know which permutations were equivalent, so it sampled
and hoped.

But 39 of 45 pair-orderings are provably irrelevant. Under Mazurkiewicz trace equivalence, two valid
orderings that differ only by transpositions of adjacent independent operators produce **identical
final state** — and with zero undeclared writes, that equivalence is sound here. So the enumeration
could have run over *canonical representatives of equivalence classes* rather than over orderings:
complete rather than sampled, and dramatically cheaper.

**Three things follow, in decreasing order of confidence.**

1. **O1's result stands.** Nothing here contradicts the ceiling finding; enumerating classes instead
   of orderings would have found the same 0.833, with more of the space actually covered. This
   strengthens rather than weakens the "0.833 is the substrate's ceiling" claim, because the
   `max_k ≤ 10, 48-orderings` caveat in `FINDINGS.md` §"Limits" is largely dissolved by it.
2. **The invalid runs were avoidable.** Both archived failures (`tails_capped_at_3`,
   `orders_capped_at_4`) were caused by not knowing the ordering structure. One of the two is
   literally constraint #6 above. The information was in the decorators.
3. **The e-graph case is now quantified, not just architectural.** Pass 4 argued babble fits better
   than Stitch. The number behind that: on this pipeline, **87% of pairwise ordering decisions carry
   no information**, and an abstraction tool that cannot see that is compressing across a corpus
   whose dominant variation is meaningless. Stitch's pruning is syntactic pattern matching; it would
   treat the 45,360 ceiling-reaching orderings as 45,360 distinct programs.

---

## 4. Honest limits of this pass

- **This is static analysis, not execution.** I derived independence from declarations and verified
  the declarations against the ASTs. I did not run Apollo, did not verify that two independent
  orderings actually produce identical output at runtime, and did not compute the number of
  equivalence classes (which requires modelling O1's dataflow applicability rule — an operator is
  applicable only once its reads are written — and is a trace-counting problem, not a
  linear-extension count). **The 39/45 figure is a pairwise commutation count, not a compression
  ratio.** Do not quote it as "87% fewer programs"; the class-count reduction is larger than 45/6
  suggests but has not been computed.
- **Scorers were excluded from §2** because they are terminals. The write-write hazard table over all
  26 operators is dominated by scorers sharing `selected_answer` and `candidate_scores` — which is
  the dispatch design working as intended (mutually exclusive preconditions mean exactly one fires),
  not a hazard.
- **One declaration must be fixed before any general theory** — `select_nth`'s undeclared read of
  `candidates`.

---

## 5. Where the study now stands

The adoption question that opened as vague ("could Stitch eat our stuff?") has resolved into
something specific and checkable:

- **Stitch is the wrong tool** for Apollo pipelines — lambda-term input, syntactic pruning, blind to
  the dominant equivalence structure.
- **babble is the architecturally right one** — library learning modulo an equational theory, and
  the theory is derivable from metadata that already exists and is enforced by a decorator.
- **The derivation is sound** — zero undeclared writes across 26 operators, one trivial read fix.
- **But none of this touches the thing that would justify spend.** Cross-domain transfer remains
  undemonstrated in the literature (pass 3 §3) and unattempted here. A better abstraction tool over
  a substrate whose ceiling is 0.833 by construction still cannot exceed 0.833. Everything in this
  pass is about *cost and completeness of search*, not about raising the ceiling — and raising the
  ceiling requires growing the operator set, which is the one thing none of this machinery does on
  its own.

That last point should be held firmly. Passes 4 and 5 found a genuinely better tool fit, and it is
easy to let that feel like progress toward the goal. It is progress toward a *cheaper search of the
same bounded space.*

---

## 6. Carried to pass 6

1. **LILO's AutoDoc** — flagged pass 1, untouched through four passes. Cheapest unexamined steal.
2. **DreamProver's recursive theorem decomposition** vs Apollo's crossover — both are attempts to
   cross a valley single edits cannot; the comparison is unmade.
3. The synthesis deliverable: the operator asked for a side-by-side. Five passes of material now
   exist and no consolidated comparison has been written.
