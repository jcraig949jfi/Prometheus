# Step 2 — the c1 regret experiment: pre-registration

**Charon, M1, 2026-08-25.** Filed BEFORE any estimator is fitted. Design inherited verbatim from
`roles/Charon/PLAN_2026-08-25_post_reset.md` §4 step 2. The plan's kill rule and filed prediction
are **not** re-derived, re-weighted, or re-scoped here. What is added is the material the plan
itself demands be stated before the run — frame declaration, attainable range, threshold-vs-SE —
plus one correction to the population that the plan could not have known.

---

## 0. Population correction (measured, and it runs in the program's FAVOUR)

The plan pre-registers the population as:

> `c1 x equal_mod_2, both windows: 411,580 rows / 222,715 states`

**That figure is a strided sample quoted as a total.** Provenance traced to
`charon/CROSSCUT_2026-08-24_aporia_diomedes.md`, which reports c1 as *"GZ window (188,060 rows)"*
and *"stride-7 over the 165-file window ... c1 rows=34,440"*. Against that, the step 1 census
measured — by exact count of every line of 370.9 GB —

```
c1  rows_EXACT = 30,031,376
```

and a single 398 MB gz file (`batch-20260519T135527Z-a03302.jsonl.gz`) contains **1,921,286** c1
rows on its own, one file of a hundred in that window. (A head-of-corpus probe suggested c1's
`relation` field was near-uniform over four values; the exact count in §1 shows that is also
wrong — there is a long tail. Recorded here rather than quietly fixed.)

`charon/extract_c1.py` recounts c1 exactly, per relation, over the deduplicated union (263 files;
the two byte-identical `.gz` copies dropped). **Measured population is filled into §1 below before
this file is committed, and this file is committed before any estimator runs.**

**This correction must be treated as hostile, not welcome.** The plan's kill rule is *"if P(A|S)
does not beat P(A) on the PARENT holdout by more than its own SE, the corpus-rebuild proposal is
DEAD"*. Standard error shrinks as 1/sqrt(n). Multiplying n by ~19x shrinks the SE by ~4.4x and
therefore makes the rebuild proposal **easier to keep alive**. This is the drift guard *"you will
find a number that flatters the program and not check it"* firing on my own correction, so it is
audited here rather than banked.

---

## 1. Population (measured — `charon/step2/c1_extract_summary.json`, `preflight_pass1.json`)

Exact, every line of 369.5 GB, 263 files, duplicate `.gz` copies dropped:

```
c1 rows_EXACT                                    30,031,376
c1 x equal_mod_2 rows_EXACT                       7,062,044   ( 17.16x prereg 411,580 )
  distinct parents                                3,060,875   ( 13.74x prereg 222,715 )
  parents with BOTH actions                         932,852   ( 19.68x prereg  47,389 )
  parents DIVERGENT (both actions, outcomes differ) 383,800   ( 14.02x prereg  27,370 )
  rows with no parent pointer                              0
action    b 3,630,073 | a 3,431,971          -> floor P(A) = 0.514026
outcome   holds=True 3,823,296 | False 3,238,748
```

**The pre-registered figures are not merely undercounts — the RATE is wrong too.** The plan reports
divergence as *"27,370 (57.8%)"* of both-action parents. Measured: **383,800 / 932,852 = 41.1%**. A
uniform undercount preserves a rate; this one does not. The original sample was therefore
**unrepresentative**, not just small, which is a stronger statement than a scale correction and
removes any temptation to treat the prereg numbers as "the same experiment, smaller".

`relation` is also not the four-valued field the head of the corpus suggests. Exact counts show a
long tail of hundreds of `abs_diff_le_N` thresholds (N up to ~9,900); four values
(`equal`, `equal_mod_2`, `divides`, `abs_diff_le_3`) cover 28.2M of 30.0M c1 rows. This matters for
the structural-regime holdout, which must not silently pool the tail with the head.

**Degeneracy preflight: PASS.** Outcome not constant, action not constant, divergent subset
non-empty, both actions present. State fields populated on every row except `catalog_a`/`catalog_b`,
present on 6,415,589 of 7,062,044 (90.8%) — the 9.2% missing is declared here and carried as an
explicit missing category, never imputed.

---

## 2. Frame declaration — the unit of analysis

The estimand is a decision about **which side to mutate**, emitted once per child record. Children
sharing a `parent_record_id` are the same decision problem revisited and are **not independent**.

- **Unit for the estimate:** the child row (one predicted action each).
- **Unit for the standard error:** the **parent cluster**. All SEs are clustered on
  `parent_record_id`; effective n is the number of parent clusters, not the number of rows.

This is filed explicitly because the failure it guards against has already happened in this program:
a per-row SE on a model emitting one decision per cell inflated precision 57x and turned 14 coin
flips into an apparent leak. Row-level SE on this population would be ~0.0002 and would make every
comparison "significant".

## 3. Attainable range (stated before the run)

A gate that cannot be reached, or cannot be missed, is not a gate. Computed and reported before the
holdout results are read:

- **Floor** — `P(A)`, the majority-action rate over the population. Any predictor scoring at the
  floor has learned nothing.
- **Ceiling** — the **within-state-cell majority rate**: the accuracy of an oracle that knows the
  empirical majority action inside each exact state cell `(catalog_a, catalog_b, invariant_a,
  invariant_b, object_a, object_b, value_a, value_b)`. This is the Bayes rate *under this state
  representation*; no estimator using these features can exceed it.
- If ceiling − floor is smaller than the clustered SE, **the experiment is structurally incapable of
  a positive result** and gets recorded as VACUOUS rather than as a null. That reading is
  pre-committed here, before the numbers exist.
- **Regret** `R = Y(S,A*) − Y(S,Â)` is defined only on **divergent parents** — those whose two
  recorded actions produced different outcomes. On that subset R ∈ [−1, +1]; the coin-flip value is
  0 and the oracle value is the divergent-parent rate. Reported with its own clustered SE.

## 4. Degeneracy preflight

Run and reported before the estimator:

- `holds` must not be constant over the population (a constant outcome makes regret undefined).
- The divergent-parent subset must be non-empty and must not collapse onto a single state cell.
- Every holdout split must leave both actions present in train and test.

Any of these failing is a **VACUOUS** reading, not a null.

## 5. What is measured

```
primary      REGRET  R = Y(S,A*) - Y(S,Â)  on divergent parents
diagnostic   action-prediction accuracy (imitation) -- reported, NEVER the headline (plan R-C)
baselines    majority action | P(A) | P(A | coarse state) | P(A | S)
holdouts     random -> parent -> object-family -> structural-regime -- ALL FOUR reported
```

Holdout definitions, fixed here:

- **random** — rows split at random. Parents straddle the split; expected to be optimistic, and it
  is included precisely so that the gap to the parent holdout is visible.
- **parent** — whole parents held out. No parent appears in both sides.
- **object-family** — no `object_a`/`object_b` value appears in both sides.
- **structural-regime** — no `(catalog_a, catalog_b, invariant_a, invariant_b)` combination appears
  in both sides.

## 6. Kill rule — inherited, NOT re-derived

> **KILL RULE:** if `P(A|S)` does not beat `P(A)` on the **parent** holdout by more than its own SE,
> the corpus-rebuild proposal is DEAD.

Two statements filed before the run, neither of which alters the rule:

1. SE in the rule is the **parent-clustered** SE per §2. That is the correct unit, not a
   tightening chosen after seeing data.
2. At the corrected n, "beat by more than one SE" is a **weak** gate — a fraction of a percentage
   point may clear it. I will therefore report the **effect size and its confidence interval beside
   the rule's verdict**, and if the rule fires on an effect too small to matter, I will say so in
   those words. The rule stands as pre-committed; its weakness is disclosed rather than patched.

## 7. Filed prediction (restated from the plan, unchanged)

> A win on the random holdout and a **loss on the parent holdout**, reporting **NO-TRANSFER**.

Same verdict shape that already retracted the h4 ranking positive when it turned out to be
memorisation of 14 constants. **If I find myself explaining why a parent-holdout loss is actually
fine, that is the disease, and this line is here to catch it.**

## 8. Scope stamp

ONE generator (`c1`), ONE relation (`equal_mod_2`), binary action space `mutation_side ∈ {a,b}`
enriched by object choice. Licenses **no** claim about mathematical navigation in general, and none
about the other 10 parent-carrying generators. The step 1 census showed `h1` and `c3` also carry
pre-decision action fields on real failure signals; `h1` in particular shows ~13x c1's multi-action
parents. **h1 is NOT folded into this experiment.** It gets its own pre-registration, filed before
its own measurement, or it does not run.

---

## 9. Where the rows live

The extracted population is 30,031,376 rows / 12 GB in `charon/step2/shards/`, which is too large to
commit and is gitignored. What is committed is the exact counts (`c1_extract_summary.json`,
`preflight_pass1.json`), the sampled parent ids, and the scripts that regenerate the shards
deterministically from the corpus (`charon/extract_c1.py`). The verdict, when it comes, ships with
those counts in the same commit.

---

# AMENDMENT 1 — the corpus is a content-addressed DAG (filed before any estimator)

Measured by `charon/step2/dup_probe.py` on the 12 GB c1 extract:

```
c1 rows                30,031,376
distinct record_ids    10,053,478
duplication factor           2.99x
```

Duplicate rows are **not byte-identical**. They differ in exactly one field —
`parent_record_id` — and agree on state, action and outcome. So `record_id` is a **content hash of
the child claim**, and the corpus is a **DAG**: the same child is reachable from several parents.
Mutating side `a` of `(knot X, ec E)` and of `(knot Y, ec E)` to the same new knot yields the
identical child. That is legitimate structure, not corruption.

It has three consequences, all of which bite before a single estimator is fitted.

**C1 — Row counts overstate distinct claims by ~3x.** This applies to the step 1 census as well:
its `rows_EXACT` column counts *records emitted*, not *distinct claims*. The census verdict does not
depend on it (the qualifier test is existential), but no row count from that table may be quoted as
a count of distinct mathematical claims. Recorded against `feedback_wrong_population_statistics`.

**C2 — The pre-registered parent holdout LEAKS, and it leaks in the flattering direction.** Holding
out a parent does not hold out the child content: the same `record_id` sits under other parents on
the train side. A win on the parent holdout is therefore consistent with pure content leakage.
**That outcome would present as a refutation of the filed NO-TRANSFER prediction — i.e. as a success
for the thesis this seat exists to attack.** It is precisely the shape that must not be allowed to
pass unexamined.

*Added control, declared before the run:* a fifth holdout, **content** — no `record_id` appears on
both sides — and **deduplication by `record_id` as the primary analysis population**. Adding a
stricter control is not a retrofit; removing one would be. All five splits are reported. The
original four remain exactly as pre-registered so the plan's prediction stays scoreable against the
split it named.

**C3 — The effective sample is ~3x smaller than the row count**, compounding the frame declaration
in §2. Clustered SEs are computed over deduplicated content, not emitted rows.

## Amendment 1b — the action is only PARTLY recorded

`mutation_side ∈ {a, b}` names which side was mutated but not **what it was mutated to**. The
outcome `holds` depends heavily on the replacement object, which is part of the action taken and is
not part of the action modelled. Regret attributed to the side choice therefore absorbs variance
driven by object choice — the plan's own scope stamp calls this *"binary-side action space enriched
by object choice"*, and here it is a confound, not a footnote.

**Pre-committed reading:** if regret on the side choice is indistinguishable from zero while
outcomes vary strongly with the replacement object, the correct verdict is **UNDER-SPECIFIED ACTION**
— the corpus recorded a decision it did not fully record — and *not* "navigation does not work".
Those are different findings and must not be reported as the same one.

## Consequence for the build

The triple needs the parent's pre-decision state, and parent pointers resolve (47.67% inside c1;
the remainder chiefly in `a1`, plus `c3 f1 f4 f2 g5 g4 f3`). Parent states must therefore be
extracted before the experiment can run. That extraction is the next step; nothing is fitted until
it lands.
