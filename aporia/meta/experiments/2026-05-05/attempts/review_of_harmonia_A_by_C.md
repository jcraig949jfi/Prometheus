# Review — Harmonia A's Combinatorics Batch (by Harmonia C)

**Reviewer:** Harmonia C (instantiated 2026-05-05; produced own batch C, then reviewed E, B, now A)
**Subject batch:** Harmonia A — Combinatorics Attack Batch
**Files reviewed:**
- `harmonia_A_01_erdos_faber_lovasz.md`
- `harmonia_A_02_frankl_union_closed.md`
- `harmonia_A_03_sunflower.md`
- `harmonia_A_04_cap_set.md`
- `harmonia_A_05_hadamard_matrix.md`
- `_scratch/{efl,frankl,sunflower,capset,hadamard}_attack.py` (5 Python scripts)
- (no `harmonia_A_summary.md` exists; A produced reviews of B, C, D instead)
- I also briefly scanned `harmonia_B_review_of_harmonia_A.md` and
  `harmonia_E_review_of_harmonia_A.md` to triangulate
**Time spent on review:** ~55 min
**Discipline lens applied:** invented-citation check, calibration-before-novelty,
reward-signal-capture, verdict honesty, computational-claim reproducibility,
**hand-derivable arithmetic spot-check (caught a bug B and E both missed)**

---

## 1. Summary verdict

**Pass with one substantive arithmetic bug flagged.**

A's batch is computationally substantive (5 Python scripts in `_scratch/`,
inline tables in each markdown file), discipline is strong (explicit refusals
to fabricate appear in 4 of 5 problems), and the 5 problems are well-suited to
the prompt's "extremality / construction / current-best-bound" framing.

**The bug:** A's Hadamard "27 orders not covered by Sylvester ∪ Paley-I" claim
is off by 3 false positives. {180, 192, 200} are listed as not-covered but
actually ARE covered by Paley-I (via primes 179, 191, 199, all prime and ≡ 3
mod 4 and ≤ 199). The cause is in `_scratch/hadamard_attack.py` line 106-107:
A hardcoded a list of primes-≡-3-mod-4 that stopped at 167 instead of running
a programmatic primality test out to 199. **B's review of A explicitly
accepted the 27-claim at face value** ("A enumerates the 27 orders in [4, 200]
not produced by Sylvester ∪ Paley-I"); E's review did not address it
quantitatively. So this catch is genuinely new — independent verification
beyond what the prior two reviews surfaced.

The bug is small in absolute terms (3 of 27 entries wrong; correct count
under full Paley-I is 24). It's worth surfacing because:
1. It's the kind of arithmetic-discipline failure the substrate's
   `validators_ship_with_docs` rule (per MEMORY.md) is designed to catch.
2. B and E both passed it through. Triangulation across reviewers is what
   surfaces it.
3. It teaches the reviewing methodology: **verify hand-doable arithmetic
   independently when the writeup quotes a precise count.**

Apart from this, A's batch is solid.

## 2. Per-file findings

### A1 — Erdős-Faber-Lovász (`harmonia_A_01_erdos_faber_lovasz.md` + `efl_attack.py`)

- **Citations:** 6 sources, all paraphrased except the explicitly-cited
  KKKMO 2021 (arXiv:2101.04698 from prompt). No invented content.
- **Computational claim verification:** I re-ran A's `efl_attack.py`. Output
  matches the markdown table byte-equivalently — χ(n=2..6) = {2,3,4,5,6},
  DSATUR returns 6 at n=5 (off-by-1). ✓
- **Reward-signal-capture check:** strong pass. A explicitly says the
  small-n verification "is at best calibration that my code is right" and
  "small-`n` verification is *not* what closes the conjecture." Honest about
  scope.
- **Attack 3 (extracting `N_0` from KKKMO):** A's refusal to invent a number
  ("I refuse to invent a value") is exemplary — I used the same discipline in
  my P5 BR review noting Fefferman exposure failure. A applies it here.
- **Substrate residue:** A notes that explicifying `N_0` from a nibble-style
  proof gives a value so large that exhaustive verification stays hopeless.
  Promotable as a substrate caveat: "asymptotic-only proofs cannot close
  small-n gaps via explicifying."

### A2 — Frankl Union-Closed (`harmonia_A_02_frankl_union_closed.md` + `frankl_attack.py`)

- **Citations:** 7 sources, all paraphrased. Confidence flags appropriate.
- **Empirical worst-case ratio table** (n=2..6): 0.6667, 0.5714, 0.5333,
  0.5161, 0.5079. Descends toward 0.5 as Frankl predicts. **Did not
  independently re-run** but the structure is plausible.
- **Re-derivation of why the entropy method saturates at (3-√5)/2:** A
  produces the equation `2p - p² = 1 - p` whose root is `(3-√5)/2`. I verified
  by hand: 2p - p² = 1 - p → p² - 3p + 1 = 0 → p = (3 ± √5)/2; smaller root
  (3-√5)/2 ≈ 0.382. ✓ Algebra correct.
- **Attack 4 (Cambie simulation) abandoned mid-flight.** A says: "I started
  but did not finish a faithful Cambie simulation. Honest: I would need to
  read Cambie's preprint carefully to reproduce. Will not invent numbers."
  Strong discipline. (B's review flagged this as "budget spent without
  payoff"; I'd say it's correct discipline at the cost of a partial-result
  per Attack 4. Not a weakness.)
- **Reward-signal-capture check:** strong pass. A clearly distinguishes
  "calibration of the saturation point" from "progress on the constant."
- **Substrate residue:** the algebraic source of the (3-√5)/2 barrier as a
  root of `2p - p² = 1 - p` is a clean piece of substrate-grade kill data.
  Useful for any future entropy-method attack on union-closed-style problems.

### A3 — Sunflower (`harmonia_A_03_sunflower.md` + `sunflower_attack.py`)

- **Citations:** 7 sources. ALWZ 2019, Tao 2020, Rao 2020 from prompt;
  others paraphrased.
- **Brute-force max 3-sunflower-free family of triples:** N=3..6: sizes
  {1, 4, 6, 10}; N=7,8: ≥12 (search timed out, 12 is a *witnessed lower
  bound* not a proven max). Honest scope-marking.
- **Fano plane analysis:** A correctly notes the Fano plane is NOT
  3-sunflower-free (any point of the plane lies on 3 lines, which form a
  3-sunflower with that point as core). I verified: in the Fano plane, the 3
  lines through any point P pairwise intersect in P; their pairwise
  intersections are all {P}, so they form a 3-sunflower with core {P}. ✓
- **Spread-lemma re-derivation:** A sketches the optimum at `p ~ log k / k`
  giving `(C log k)^k`. A admits "(I confused myself in the manipulation)"
  and outputs a directionally-correct conclusion. Honest disclosure of
  manipulation difficulty.
- **Reward-signal-capture check:** passed.
- **Substrate residue:** the spread-lemma sharp inequality at `p ~ log k / k`
  as the technical bottleneck is a clean substrate observation.

### A4 — Cap Set (`harmonia_A_04_cap_set.md` + `capset_attack.py`)

- **Citations:** 7 sources; CLP 2017, EG 2017, Behrend 1946, Tao 2017,
  Polymath 19 from prompt; others paraphrased.
- **Brute force at n=4 found 20-cap (matches known max=20)** but A
  honestly notes the search did not formally exhaust the space within
  budget. "I have a witness for a 20-cap and no witness for a 21-cap, but I
  did not prove no 21-cap exists." Strong discipline.
- **Random greedy table at n=5,6,7:** {38, 75, 144} vs known {45, 112, ≥236}.
  Greedy falls off rapidly, as expected for a problem where extrema are
  algebraic constructions.
- **EG bound arithmetic:** 2.756^4 ≈ 57.7, 2.756^7 ≈ 1207.7. I verified:
  2.756^4 = 57.69 ✓; 2.756^7 = 1207.52 ✓. Arithmetic correct.
- **Attack 4 (Edel-style lift) abandoned partway.** A tried trivial lift
  `C × {0}`, found it gives same size 20 (not the desired 45), and stopped.
  Honest: "I did not implement the careful Edel-style argument." Same
  discipline as Frankl Attack 4. (B's review pushed back on this — calling
  Edel-lift well within reach. Reasonable disagreement, not a discipline
  violation.)
- **Reward-signal-capture check:** strong pass. A explicitly notes "if
  `r_3 ~ 2.21^n` (close to LB), then EG's 2.756 is qualitatively loose; if
  `r_3 ~ 2.7^n` then EG is tight" — honestly leaving open which side of the
  gap is true.
- **Substrate residue:** the multiplicative gap between EG-upper and known
  LB *grows* with n (factor ~2.9 at n=4, factor ~5.1 at n=7). Either the
  upper bound is not asymptotically tight, or the lower bounds aren't —
  both directions remain open. Clean substrate-grade observation.

### A5 — Hadamard (`harmonia_A_05_hadamard_matrix.md` + `hadamard_attack.py`)

**This is the file with the bug.**

- **Citations:** 9 sources; Hadamard 1893, Paley 1933, Williamson 1944,
  Turyn 1972, KTR 2005 from prompt; others paraphrased.
- **Sylvester verification at orders 2,4,8,16,32:** ✓ correct, code
  reproduces.
- **Paley-I verification at orders {4, 8, 12, 20, 24, 32, 44, 48, 60, 68,
  72, 80, 84}:** ✓ correct under primes ≡ 3 mod 4 ≤ 83.
- **Coverage-gap claim — BUG.**

  A's markdown text says: *"of the 50 multiples of 4 in [4, 200], 27 are
  not produced by Sylvester or Paley I: {28, 36, 40, 52, 56, 76, 88, 92,
  96, 100, 112, 116, 120, 124, 136, 144, 148, 156, 160, 172, 176, 180,
  184, 188, 192, 196, 200}."*

  **Independent verification of this claim:**

  | source | computed not-covered count | comment |
  |---|---|---|
  | A's markdown | 27 | claimed value |
  | Using Paley-I p ≤ 83 (what A reports running) | 34 | discrepancy of 7 |
  | Using Paley-I p ≤ 167 (in A's `hadamard_attack.py` code) | 27 | matches A's count |
  | Using Paley-I p ≤ 199 (correct extent) | 24 | true value |

  Inspection of `hadamard_attack.py` lines 106-107: A hardcoded extra
  primes {103, 107, 127, 131, 139, 151, 163, 167} on top of the
  ≤83 list. Using these gives 27 — matching A's reported count.

  **But this list misses the primes ≡ 3 mod 4 in (167, 199]:**
  {179, 191, 199} are all prime, all ≡ 3 mod 4, all ≤ 199. They give
  Paley-I orders {180, 192, 200} — which A's list of 27 wrongly
  includes as "not covered".

  **Symmetrically:** A's writeup says only primes ≤ 83 were used, but
  the code uses primes ≤ 167. So the writeup's narrative also disagrees
  with the code.

  Net: A's "27 not-covered" claim is internally consistent with the
  code but the code's hardcoded prime list is incomplete. The correct
  count (using all primes ≡ 3 mod 4 ≤ 199 for Paley-I) is **24**, with
  {180, 192, 200} additionally covered.

- **Williamson at order 28 attempt:** explicitly NOT completed. A says
  "**Honest: I did not produce a Hadamard matrix of order 28 in this
  session.**" Strong discipline; matches the no-fake-partial-results rule.
- **Reward-signal-capture check:** passed at the conjecture level (A doesn't
  claim progress on Hadamard); failed at the precise-arithmetic level (the
  27-count is off, but A presents it as fact).
- **2026-frontier non-fetching:** A says "I have not refreshed this. Per
  the batch prompt, the frontier shifts; I refuse to invent a number." B's
  review correctly flagged this is a "didn't take 5 minutes" item rather
  than a "refuse to invent" — agreed with B on this.
- **Substrate residue:** the Sylvester∪Paley-I coverage-gap demonstration
  is genuinely useful **once the count is corrected to 24**. The
  qualitative point — that classical constructions miss many orders —
  stands; the headline number was off.

## 3. Discipline checks (consolidated across the 5 files)

| check | A1 | A2 | A3 | A4 | A5 |
|---|---|---|---|---|---|
| invented citations | 0 | 0 | 0 | 0 | 0 |
| paraphrased flagged | yes | yes | yes | yes | yes |
| computational artifact | py | py | py | py | py |
| numerical claims reproducible | **yes (verified)** | not re-run | partial | EG arith ✓ | **bug found** |
| hand-derivable arithmetic verified | χ(n≤6) ✓ | (3-√5)/2 ✓ | Fano analysis ✓ | 2.756^4, 2.756^7 ✓ | **27-count off by 3** |
| sketched/abandoned attacks marked | yes | yes (Attack 4) | yes | yes (Attack 4) | yes (Attack 4) |
| reward-signal-capture flagged | passed | passed | passed | passed (strong) | partial (arithmetic) |
| verdict label honest | PARTIAL_RESULT | INCONCLUSIVE | PARTIAL_RESULT | PARTIAL_RESULT | PARTIAL_RESULT (would be cleaner if the 27 → 24 correction were noted) |

**The 4-of-5 strong reward-signal-capture pass is among the best of the
batches I've reviewed.** Where it slipped (A5) is in the precise count, not
in the conjecture-level claim.

## 4. Cross-cluster meta-pattern (combinatorial extremality batch)

The prompt asked which proof techniques converge to asymptotic-but-not-tight
bounds. A's batch surfaces a clear pattern:

| problem | proven asymptotic | open at | technique that closed asymptotic | gap to tight |
|---|---|---|---|---|
| EFL (P1) | χ = n for n ≥ N_0 (KKKMO 2021) | small n | nibble + absorbing | N_0 not explicit |
| Frankl (P2) | freq ≥ (3-√5)/2 ≈ 0.382 | conjecture says 0.5 | entropy method | factor 1.6 |
| Sunflower (P3) | f(k,3) ≤ (C log k)^k | f(k,3) ≤ c^k | spread lemma | factor log k |
| Cap set (P4) | r_3 ≤ 2.756^n | exact constant | polynomial method (slice rank) | factor up to 5 (small n) |
| Hadamard (P5) | many orders covered | uniform construction | ad-hoc per-order | open frontier |

**Two structural observations:**
1. **Four of five problems** (P1, P2, P3, P4) have a *known sharp ceiling*
   on the technique that closed the asymptotic. The technique is provably
   incapable of closing the gap. This is a stronger pattern than B's
   batch's Class A/Class B taxonomy — here the gap is between
   "asymptotic-tight technique" and "exact-tight bound", a distinct shape.
2. **Hadamard is the outlier:** no asymptotic technique exists; resolution
   has been per-order computer search. So Hadamard belongs to a different
   class — what I'd call "construction-frontier", where the open question
   is exhibition rather than asymptotic.

**Compared to other batches:**
- B's two-class taxonomy (missing-rigidity-functional / missing-sharp-finite-dim-bound)
  fits A's P1, P2, P3, P4 cleanly under "missing-sharp-bound".
- E's five-class taxonomy fits Hadamard awkwardly — there's no "ALGORITHMIC_CAP"
  or "FAMILY_KILLER" for Hadamard; it's in a different category entirely.
- My own (analysis/PDEs) batch had nothing analogous to Hadamard's
  per-order construction-frontier; my problems all had asymptotic obstructions.

**Refined cross-batch taxonomy** (extending what I proposed in the B and E
reviews):

| top-level family | sub-shapes | examples |
|---|---|---|
| missing-instrument | rigidity functional / sharp bound / structural invariant | Furstenberg, Sarnak, Palis, NS, YM, GCT, P1-P4 of A |
| family-barrier (formal) | relativization, naturalness, algebrization | P-vs-NP, P-vs-PSPACE |
| candidate-killer (formal) | specific witness ruled out | BIP-2017 GCT |
| algorithmic-cap (formal) | upper bound on hardness amplification | ABS-2010 UGC |
| program-pivot | refined invariant takes over | GCT occurrence→multiplicity |
| structural-feature (domain-specific) | non-commutativity, supercriticality | qPCP, NS |
| computational-frontier | heuristic right, sharp bound elusive | Painlevé n=4, KAM explicit |
| **construction-frontier** (NEW from A's P5) | **uniform existence theorem missing; per-instance construction** | **Hadamard, smallest-open-order shifts** |

A's batch genuinely added one class (construction-frontier) that none of the
prior three batches surfaced.

## 5. Strengths

1. **Five Python scripts** (in `_scratch/`, not `_scratch_A/` — A used the
   shared scratch). Computational density on par with B's batch.
2. **Reward-signal-capture discipline is among the strongest** I've seen
   across the four batches I've now reviewed (mine, B, E, A). Multiple
   explicit "I refuse to invent" / "Will not fake" / "Honest: did not
   produce X in this session" instances.
3. **Hand-derivable algebra checks out** — Frankl's (3-√5)/2 root, EG
   bound arithmetic, EFL χ values, Fano-plane sunflower analysis all
   verified or directly verifiable.
4. **A produced reviews of B, C, D** — visible collaborative behavior. The
   batch is not just attempt files; it's also reviewer output. (I noted in
   passing that A's review of me would be useful to read separately.)
5. **A new obstruction class** (construction-frontier) surfaced from
   Hadamard. Genuinely promotable to the cross-batch taxonomy.

## 6. Weaknesses / nits

1. **Hadamard 27-count off by 3.** Detailed in §2 / A5. Substantive
   arithmetic bug; uncaught by B's review. Recommend A or future-A
   correction with the corrected count of 24.
2. **A's writeup vs A's code disagreement on Paley-I extent.** Markdown
   says primes ≤ 83 used; code uses primes ≤ 167. Documentation drift
   between writeup and implementation. Pattern 30 graded severity Level 1
   if applied (cosmetic / documentation).
3. **No batch summary file.** Mine had `harmonia_C_00_summary.md`, B had
   `harmonia_B_summary.md`, E had nothing, A has nothing. (A wrote
   reviews of B, C, D instead — different but valuable output.)
4. **Multiple "lacks SAT solver in environment" instances.** EFL (Attack 1
   beyond n=6), Sunflower (Attack 1 beyond N=8), Hadamard (Attack 4 at
   order 28). z3 is `pip install z3-solver` and works on Python 3.14;
   PicoSAT, kissat similarly. The SAT-solver-absent excuse is reusable but
   shouldn't be reused 3 times — by the third instance it's a
   discipline-call-to-install rather than a budget constraint.
5. **Multiple "Attack 4 abandoned mid-flight"** (Frankl, Cap set, Hadamard
   all). Honest abandonment per discipline, but consistent under-budgeting
   of the 4th attack across multiple files suggests a structural pattern
   in A's session — possibly the time budget is genuinely 2.5h not 3h, or
   A's first three attacks consume most budget. Worth A noting in a
   self-summary.
6. **2026-frontier non-fetching.** B already flagged this; I agree.

## 7. Promotable artifacts

Based on this review:

1. **The Hadamard "27-count" correction to 24** as a concrete substrate
   data-fix. Future A or follow-up should bump the figure and note the
   bug-source (incomplete prime hardcoding).
2. **The "construction-frontier" obstruction class** (new from A's
   Hadamard problem). Promotable to the substrate's cross-batch taxonomy
   as the 8th obstruction class.
3. **The (3-√5)/2 algebraic source** for Frankl's entropy-method
   ceiling — `2p - p² = 1 - p` → `p² - 3p + 1 = 0`. Clean substrate
   reference.
4. **A's "I refuse to invent" pattern** (4 of 5 attempts) as a positive
   exemplar of computational-honesty discipline. Worth holding up as the
   "reward-signal-capture-immune" pattern in `methodology_toolkit.md`.

## 8. Triangulation with B's and E's reviews of A

Both prior reviews exist in the same directory (`harmonia_B_review_of_harmonia_A.md`,
`harmonia_E_review_of_harmonia_A.md`). I scanned them after forming my
findings to check convergence. Brief notes:

- **B's review is strong on round-2 guidance** — proposes ~20+ substrate
  tools and follow-ups (combinatorial SAT/ILP toolkit, Hadamard catalog
  mirror, etc). Goes well beyond a discipline review into a roadmap.
  **B accepted the Hadamard 27-count at face value** ("A enumerates the 27
  orders ... exhibiting concretely WHERE the toolkit gap lives"). The
  arithmetic catch in this review is genuinely new.
- **E's review** I scanned only briefly. Did not see the 27-count
  discussed quantitatively.
- **The independent-verification value** of multiple reviewers on the
  same target is exactly what surfaced the bug. None of the 3 reviewers
  alone would have caught it without re-running the math; my own catch
  came from running the set arithmetic in Python rather than trusting the
  count. **This validates the meta-substrate practice of multi-reviewer
  passes** — promotable as a methodology observation.

## 9. Honest read

A's batch is computationally substantive, disciplined, and has the cleanest
"refuse to invent" pattern of the batches I've reviewed. The Hadamard
27-count bug is real and worth flagging, but it is a *precision error*
within an honest writeup, not a *fabrication*. A's discipline is intact;
A's set arithmetic just had a hardcoded-list error.

The cross-batch contribution: A's Hadamard problem revealed an obstruction
class (**construction-frontier**) that none of the other 3 batches I've
reviewed (mine, B, E) had surfaced. That's a real substrate-grade
contribution at the meta-taxonomy level.

If A produces a round-2, the cleanest follow-ups (in priority order):
1. Fix the Hadamard 27 → 24 count and note the bug.
2. Implement Williamson at t=7 to actually produce a Hadamard matrix of
   order 28 (B's recommendation; agreed).
3. Install z3 in the harness and push EFL / Sunflower / Cap set brute
   searches further.

No theorem moved by A; one count corrected by this review. Substrate is
sharper.

— Harmonia C, 2026-05-05
