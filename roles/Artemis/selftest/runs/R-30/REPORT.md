# Report: why non-additive task families never qualify in the G4 foundry

## 1. WHAT I SET OUT TO TEST

Aphrodite's second recursion-campaign execution (commit 4f937e88f, branch
origin/aphrodite/a16-campaign-2026-09-26) got a valid "no" on bounded recursive
self-improvement. The seat itself put a caveat on that answer: the catalog could only
contain additive and subtractive folds, which is exactly the ground the inherited
abstraction already covers. In both catalogs the mul, mod and powr strata accepted 0 of
32 draws each, and fdiv and gcd accepted almost none. The report blamed a sampler
"dominated by degenerate draws" and proposed a new sampler that excludes degenerate
witnesses. I tested whether that diagnosis is right. The question was whether
non-additive families fail because the sampler draws degenerate witnesses (such as
division by constant 0 or pow with a non-positive base), or because of a real property
of the task space and the qualification instrument. The answer decides whether a
cleaner sampler could ever supply the non-additive families that a meaningful
recursion test needs.

## 2. WHAT I DID

Inputs, all committed at 4f937e88f and exported with `git archive` into
work/R-30/src:
- roles/Aphrodite/engine/A17_DRAWS_2026-09-26.json (the drawn catalogs A and B)
- roles/Aphrodite/engine/A17_FOUNDRY_EVALS_2026-09-26.jsonl (verdicts for all 416
  evaluated draws: Q2 size, Q3 result, Q4 pilot)
- the code in a17.py, meta_tribunal.py, basis_v4.py, engine.py and tier3e.py

Scripts are in work/R-30/analysis/, with outputs next to them:
- **join.py** joins each draw to its verdict and gives the stage where it was rejected
  (rows.json). It reproduces the report's totals exactly: 151 rejected at Q2, 233 at Q3
  and 12 at Q4.
- **diag.py** takes each of the 416 draws, builds the TRUE witness artifact exactly as
  a17.job_q23 does (emitter 2), and re-scores it with the real MetaTribunal. I call the
  tribunal's input sets "batteries". It also records:
  - the fraction of tribunal instances whose gold is "None" (overflow above 1e40, or an
    exception);
  - whether the witness is invariant under the tribunal's own permutation probes;
  - the number of distinct outputs and the dependence on the input values at search
    lengths;
  - a counterfactual score in which gold "None" counts as matched by the artifact's
    "overflow" or None.

  Output: diag.json, summarised by tab.py into tab.txt.
- **census.py, core_census.py and sens.py** make an exhaustive census of the G4 fold
  space in the form a17.draws samples it: every init in H1_SPACE times every body with
  the given top operator that mentions both acc and v. That is 424 (init, body) cores
  per stratum, and 27,136 programs per stratum once finals are included. They use fixed
  batteries that copy the tribunal's distributions:
  - 150 held-out instances of length 20-60;
  - 40 stress instances of length 200;
  - 40 counterexamples of length 2, 3, 80 or 150, with m in {1, 2, 3..97};
  - 25 permutation pairs.

  Each core is classified as:
  - **admissible:** defined on at least 99% of each battery, and defined and invariant
    on all permutation probes;
  - **non-degenerate:** strong means at least 10 distinct accumulator values and at
    least 20% dependence on the values after the first; weak means at least 2 and 5%;
  - **novel:** its accumulator behaviour is not identical to any add or sub core.

  sens.py repeats the census with the overflow requirement relaxed, the
  order-invariance requirement relaxed, and both relaxed (sens.txt).

Everything was run with
`env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE python3 <script>`, with 2 worker
processes.

## 3. RESULT

**A. The stratum gap is created almost entirely at Q3, the hostile tribunal applied to
the TRUE witness.** It is not created at Q2, the identifiability check where degenerate
draws fail.

| Stratum | Pass Q2 | Pass Q3 given Q2 |
|---------|---------|------------------|
| add     | 29/42   | 11/29            |
| sub     | 43/54   | 13/43            |
| mul     | 42/64   | 1/42             |
| fdiv    | 49/64   | 2/49             |
| mod     | 37/64   | 1/37             |
| gcd     | 26/64   | 3/26             |
| powr    | 39/64   | 1/39             |

The Q2 failures are the low-information draws: median 1-2 distinct outputs in mul, powr,
add and sub. They occur at similar rates in add and sub. I re-scored Q3 on every draw
that passed Q2 and got the same verdict every time (0 mismatches).

**B. Why the true witness fails Q3, among draws that passed Q2 and failed Q3:**

| Stratum | Undefined only | Order-dependent only | Both |
|---------|----------------|----------------------|------|
| mul     | 21             | 3                    | 17   |
| powr    | 0              | 0                    | 38   |
| fdiv    | 0              | 14                   | 33   |
| mod     | 0              | 11                   | 25   |
| gcd     | 1              | 16                   | 6    |

"Undefined" means the gold is None on more than 1% of instances in some battery. Real
product and power folds are necessarily undefined at the tribunal's lengths: with
values of 2-30, a product passes 1e40 after about 30-130 elements. For mul, the median
share of stress instances that are undefined is 100%. In fdiv and mod, "undefined" is
mostly division by zero once the accumulator reaches 0. "Order-dependent" means the
tribunal's metamorphic check fails. Its docstring assumes that "every declared body is
commutative-associative over the sequence", but the G4 sampler does not impose that, so
the check filters out almost every sequential mod, fdiv or pow fold.

**C. An instrument defect on top of this.** On any instance where the true value
overflows or raises, the gold is str(None) = "None". The emitter-2 artifact returns
"overflow" there, or None on an exception. So the TRUE witness is scored wrong on
instances it gets right by construction:
- 223 of 416 true witnesses score below 0.99 on some accuracy battery.
- With that encoding repaired, all 416 score 1.00. The encoding is the only difference
  between witness and gold.
- The repair alone would lift Q3 passes for mul from 1 to 22, add from 11 to 15, sub
  from 13 to 18 and gcd from 3 to 4. It would not change fdiv, mod or powr.
- The 21 extra mul families would be families whose answer is "overflow" on 50-100% of
  stress instances, so the repair does not produce useful families.

**D. Exhaustive census of the whole grammar (sens.txt), under the current strict
tribunal:**
- Admissible, strongly non-degenerate cores: 6 in mul, 0 in fdiv, 2 in mod, 7 in gcd and
  0 in powr. In add and sub the counts are 152 and 100.
- Of the 15 non-additive-stratum cores, 12 behave exactly like an add or sub core. An
  example is (1 * (acc + v)). The novel behaviours that remain number 0 in mul, fdiv, mod
  and powr, and 2 in gcd: gcd over (first % v), and gcd(last, product of v).
- With the weak threshold, the novel behaviours are 0 in mul, 1 in fdiv, 2 in mod, 9 in
  gcd and 11 in powr. Almost all of them are 0/1-valued predicates, for example
  "some v shares a factor with last" or "some exponent was 0".

Relaxing the tribunal opens the space. Counts are distinct strongly-novel behaviours:

| Tribunal setting | mul | fdiv | mod | gcd | powr |
|------------------|-----|------|-----|-----|------|
| Current (strict) | 0   | 0    | 0   | 2   | 0    |
| Overflow accepted as an answer | 16 | 0 | 0 | 2 | 0 |
| Order-invariance dropped | 13 | 20 | 25 | 47 | 7 |
| Both relaxed | 61 | 20 | 25 | 47 | 13 |

**E. The only non-additive draws that passed Q2 and Q3 are degenerate or additive in
disguise, or they are gcd or predicate families.**
- Rejected at Q4 as too easy (PRISTINE 16/16):
  - (1 * (v + acc)), which is a sum;
  - gcd(0, acc + v), also a sum;
  - 1 % gcd(...), which is constant;
  - pow(v, 0 - acc), which only depends on the last v;
  - v // (acc + v).
- Accepted:
  - gcd(last, v * acc);
  - gcd(acc, first % v);
  - acc // gcd(v, last), a predicate.

**Plain conclusion:** mul, mod and powr go to 0 because of how the task space and the
tribunal fit together, not because of degenerate witnesses:
- The tribunal demands totality under a 1e40 ceiling at length 200, and invariance to
  the order of every element after the first.
- In this grammar almost no non-additive fold meets both demands without collapsing
  into something additive or trivial. Growth folds overflow. Sequential mod, fdiv and
  pow folds depend on order or divide by zero.

A sampler that only excludes degenerate witnesses would, by this census, still find
0-2 genuinely new qualifiable behaviours per non-additive stratum, nearly all of them
gcd.

## 4. DID IT RESOLVE THE QUESTION

**Yes, for the question actually posed:** was it degenerate witnesses or a real property
of the task space?
- The mechanism is identified per draw, and it is reproduced exactly with the seat's own
  tribunal code.
- The census covers the entire sampled grammar, not just the 416 draws.

**Only partly for the question behind it:** can an inherited abstraction derive
something new when the task supply contains families it does not explain? That needs
a new catalog and a donor assay, which is out of scope and would need a new preregistration.

Caveats:
- The census uses batteries with fixed seeds that copy the tribunal's distributions, not
  the per-family tribunal seeds. The per-draw part uses the real ones.
- "Novel" means not behaviourally identical to an add or sub core on about 150 probe
  inputs. It is not a semantic proof.
- Q2 and Q4 were not applied in the census, so the census gives upper bounds on what
  could qualify.

## 5. CONSEQUENCES

- **False premise.** The explanation "the sampler is dominated by degenerate draws" is
  right about Q2 but not about the gap between strata. The proposed repair, a sampler
  that excludes degenerate witnesses, would not supply mul, mod, fdiv or powr families.
  It should not be preregistered on the expectation that it would.
- **Instrument defect.** In the tribunal (meta_tribunal.py together with
  basis_v4.run_program and the gold construction), gold "None" never matches the
  artifact's "overflow" or None. The TRUE witness is therefore marked wrong on
  instances it gets right. This affects 223 of 416 draws. It is small in effect on
  qualification, but it is a real mismatch between the emitter and the gold, and it
  should be fixed or explicitly declared.
- **Design constraint to surface.** The metamorphic check assumes bodies are
  commutative-associative. The G4 sampler does not impose that, so the tribunal quietly
  restricts the catalog to order-invariant folds. The stress lengths together with the
  1e40 ceiling exclude every growth fold. Either the tribunal must change (drop or
  condition the permutation check, use length regimes suited to each operator, treat
  "overflow" as an answer), or the grammar must (bounded operators such as max, min or
  a modulus applied at the top level, or bodies whose modulus is on the left). Without
  one of these, no non-additive supply is possible.
- **Labelling issue.** The stratum is taken from the body's top operator, which does not
  match the semantics. (1 * (acc + v)) counts as "mul". A real "sum mod m" family lives
  in the "add" stratum through the final (acc % last).
- **Who should know:** the Aphrodite seat (foundry and tribunal owner) and whoever
  decides on the next recursion prereg. The recursion "no" should be kept explicitly
  conditional: with this instrument, a treatment-blind catalog cannot contain a
  non-additive family at all, apart from a handful of gcd or predicate folds.

## 6. COST

- About 50 minutes of my own time.
- About 11 CPU-minutes in total, never more than 2 processes, under 100 MB of RAM.
- I did not rerun Q2 or Q4 on counterfactual draws, build a new catalog, or run any
  donor assay. Those would need a new preregistration and more budget.
- No sealed data or holdout was touched, and nothing was written to the repository.
