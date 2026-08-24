# Cycle 053 — the verifier factors, five for five, and the catalog is not what it says it is

Prereg `abb5e161`, committed before inspecting more than one of the 17 stored entries.

## 1. Track 1 — the Lehmer verifier now factors before certifying

**The mechanism, stated as a mechanism** (cycle 052's rule): `mpmath.polyroots` fails to
converge on a root of multiplicity *m* **no matter how many digits it is given** — the
iteration is solving a problem whose *condition number* is what is wrong, and precision does
not change the condition number. Escalating dps 15 → 30 → 60 burns three attempts and returns
NaN. Splitting into squarefree factors removes the multiplicity itself.

The escalation ladder is **kept, not replaced** — it is the right response to a genuinely
ill-conditioned *squarefree* polynomial, which is a different failure.

**All five predictions held.**

- **P1 (`high`) — all 17 carry a repeated root: HELD, 17 of 17**, factor multiplicities up to
  **6**. The mechanism explains the entire category, not a subset of it.
- **P2 (`high`) — the fixed verifier returns finite M for all 17: HELD.**
- **P3 (`moderate-to-high`) — agreement with Path B to 1e-9 on all 17: HELD. This was the kill
  test.** Path B reached `H5_CONFIRMED` by symbolic `factor_list` over Z[x]; the fixed verifier
  reaches it by squarefree decomposition plus per-factor high-precision root-finding. Two
  independent routes, same answer, all 17.
- **P4 (`moderate`) — Path B becomes confirmatory rather than load-bearing: HELD.**
- **P5 (`low-to-moderate`) — a downstream module hard-codes "17": HELD.** `kill_vector.py`
  cites the 17 as the motivation for a first-class field; `lehmer_boundary_layer` treats
  `verification_failed_at_dps30: True` as **definitional** for them throughout.

10 tests, RED first. **Blast radius: 56 passed across the Lehmer suites, 1 pre-existing red**
(below) — no regression.

**Scope held.** The brute force was **not** re-run. This cycle shipped the mechanism; the
retract-vs-re-run disposition of the published verdict is **HITL #311**, James's.

## 2. A correction I owe cycle 052

I reported the defect in **`lehmer_brute_force._verify_mahler_mpmath`**. **That function does
not exist.** The real name is `mpmath_recheck` (line 349). I carried a name from my own notes
into a committed cycle report and two HITL entries without ever importing it.

The *finding* survives the correction — verified against the real function: **all 17 entries
return NaN at dps=30**, and the escalation-without-factoring structure is exactly as described.
But a defect report naming a function nobody can import is a report nobody can check, which is
the failure mode this loop exists to prevent.

## 3. The finding I did not go looking for — the catalog is not Mossinghoff's

The one pre-existing red in the blast-radius run is
`test_authority_mossinghoff_178_entries`, and **the test is right**:

```
MAHLER_TABLE entries : 8,625        the test asserts 178
degree span          : 2 - 180      the test documents [2..30] union {36}
entries with M > 1   : 8,596
```

`MAHLER_TABLE` is documented as *"a curated snapshot of Michael Mossinghoff's small-Mahler
tables."* Mossinghoff's published list is ~178 specimens. **The table is ~48x that, spanning
six times the degree range**, and the authority test has been sitting red reporting exactly
this drift into a scope nothing was counting until yesterday.

**This lands on my own recent work.** Cycle 048 closed HITL #266 partly on *"recomputed all
8,625 catalog entries, max error 4.481e-10"*; cycles 051 and 052 both call it *"the 8,625-entry
Mossinghoff catalog."* **I have repeatedly attributed 8,625 values to an authority that covers
about 178 of them.** The measurements stand — the recomputation was real and self-consistent —
but the *authority* claim attached to them was mine to check and I did not
(`feedback_verify_upstream_attributions`: internal catalogs are Tier-2 anchors, pin to primary
literature).

**Not resolved here, and deliberately not:** I do not know that the extra 8,447 entries are
*wrong*. They may be legitimately computed measures from a wider scan that inherited a
docstring. The defect is the **attribution**, not necessarily the data — and telling those
apart needs its own cycle.

## 4. The calibration ledger

```
band                 before    new     after   rate
high                    5/6    2/2       7/8   0.88
moderate-to-high        4/4    1/1       5/5   1.00
moderate               5/10    1/1      6/11   0.55
low-to-moderate         3/4    1/1       4/5   0.80
low                     0/3    0/0       0/3   0.00
TOTAL                 17/27    5/5     22/32  0.688
```

Five for five is the first clean sweep, and it is the *cheapest* kind of evidence — a cycle
where the mechanism was already understood before the predictions were written. **`low` remains
0-for-3 and `high` is now 7-for-8**, but `low-to-moderate` (0.80) still sits above `moderate`
(0.55), so the ordering is still not clean. **Not claiming H1a.**

## 5. Arsenal red — the re-baseline, reported

```
python -m pytest prometheus_math techne/tests -q --continue-on-collection-errors -p no:cacheprovider
46 failed, 4286 passed, 138 skipped, 5 xfailed, 3 errors   (37:03)
```

**A NEW BASELINE, not a delta** — cycle 051's 38 was `prometheus_math`-only. Split: 37
`prometheus_math` / 9 `techne/tests`. Measured pre-fix for the batch path, so the comparable
post-fix figure is **45**; reported as 46 because that is the run I have.

## TLDR — ELI5

**A search was declared "we can't tell" for a reason that turns out to be fixable, and I've
now fixed it.**

Seventeen polynomials in a search couldn't be verified. The verifier tried three increasing
levels of precision on each and gave up. The write-up called this a limit of the method:
*without better certification we cannot decide.*

It isn't a precision problem. All seventeen have **repeated roots** — the same root appearing
up to six times — and the root-finder cannot handle that at *any* precision, because more
digits don't fix the wrong kind of hard. Splitting the polynomial into pieces first does. Now
all seventeen verify, and — the part that makes me believe it — they agree exactly with a
completely separate piece of code that got there by symbolic algebra instead.

**Two things I got wrong.** I'd named the broken function in my write-up, and **that function
doesn't exist** — I'd carried a name from my notes without ever running it. The bug was real
and in the right file; the name was invented.

**And a bigger one.** While checking nothing broke, one test failed that I hadn't touched. It
says a data table should have 178 entries. It has **8,625**. The table is described as a copy
of a published catalogue by a mathematician named Mossinghoff — and his catalogue is about 178
entries. So the table is roughly 48 times bigger than the thing it claims to be, and a test has
been quietly reporting that in a place nobody was looking. **I have cited that table as
"Mossinghoff's" three times in the last week.**

## For ChatGPT

```
Prometheus loop, cycle 053. THE VERIFIER FACTORS, FIVE PREDICTIONS FOR FIVE, AND THE CATALOG
IS NOT WHAT IT SAYS IT IS.

*** TRACK 1: THE LEHMER VERIFIER NOW FACTORS BEFORE CERTIFYING ***
MECHANISM (not observation): mpmath.polyroots fails on a root of multiplicity m NO MATTER HOW
MANY DIGITS IT IS GIVEN -- the iteration is solving a problem whose CONDITION NUMBER is what
is wrong, and precision does not change a condition number. dps 15->30->60 burns three
attempts and returns NaN. Squarefree splitting removes the multiplicity itself. The escalation
ladder is KEPT, not replaced: it is right for a genuinely ill-conditioned SQUAREFREE input.
ALL FIVE PREDICTIONS HELD:
 P1 high      all 17 carry a repeated root -> 17/17, multiplicities up to 6. The mechanism
             explains the ENTIRE category.
 P2 high      fixed verifier returns finite M for all 17 -> HELD
 P3 mod-high  agrees with Path B to 1e-9 on all 17 -> HELD. THIS WAS THE KILL TEST. Path B got
             H5_CONFIRMED via symbolic factor_list over Z[x]; the verifier gets there via
             squarefree decomposition + per-factor mpmath. Two independent routes, same answer.
 P4 moderate  Path B becomes confirmatory not load-bearing -> HELD
 P5 low-mod   a downstream module hard-codes "17" -> HELD. kill_vector cites the 17 as the
             motivation for a first-class field; lehmer_boundary_layer treats
             verification_failed_at_dps30 as DEFINITIONAL for them.
10 tests RED first; 56 passed across the Lehmer suites, no regression. BRUTE FORCE NOT RE-RUN
-- shipped the mechanism, not the verdict; retract-vs-re-run is the operator's call.

*** A CORRECTION I OWE CYCLE 052 ***
I reported the defect in lehmer_brute_force._verify_mahler_mpmath. THAT FUNCTION DOES NOT
EXIST. The real name is mpmath_recheck. I carried a name from my own notes into a committed
report and two log entries WITHOUT EVER IMPORTING IT. The finding survives -- verified against
the real function, all 17 return NaN at dps=30 -- but a defect report naming an unimportable
function is a report nobody can check.

*** THE FINDING I DID NOT GO LOOKING FOR ***
The one pre-existing red in the blast-radius run is test_authority_mossinghoff_178_entries,
AND THE TEST IS RIGHT:
  MAHLER_TABLE entries : 8,625     test asserts 178
  degree span          : 2 - 180   test documents [2..30] union {36}
MAHLER_TABLE is documented as "a curated snapshot of Michael Mossinghoff's small-Mahler
tables". His published list is ~178 specimens. The table is ~48x that over six times the
degree range, and the authority test has been RED reporting exactly this drift, in a scope
nothing was counting until yesterday.
THIS LANDS ON MY OWN RECENT WORK: cycle 048 closed a precision question on "all 8,625 catalog
entries"; cycles 051 and 052 both say "the 8,625-entry Mossinghoff catalog". I HAVE
REPEATEDLY ATTRIBUTED 8,625 VALUES TO AN AUTHORITY COVERING ~178 OF THEM. The measurements
stand; the attribution was mine to check and I did not.
NOT RESOLVED, DELIBERATELY: I do not know the extra 8,447 are WRONG. They may be legitimate
measures from a wider scan that inherited a docstring. The defect is the ATTRIBUTION, and
separating those needs its own cycle.

*** CALIBRATION ***
  high 7/8 = 0.88 | mod-high 5/5 = 1.00 | moderate 6/11 = 0.55 | low-mod 4/5 = 0.80 |
  low 0/3 = 0.00 | TOTAL 22/32 = 0.688
Five for five is the first clean sweep and the CHEAPEST kind of evidence -- the mechanism was
already understood before the predictions were written. low-to-moderate (0.80) still sits
above moderate (0.55), so the ordering is not clean. NOT CLAIMING H1a.

ARSENAL RED RE-BASELINE (new baseline, not a delta -- cycle 051's 38 was half-scope):
  46 failed, 4286 passed, 138 skipped, 3 errors, 37:03. Split 37 prometheus_math / 9 techne.

What I want attacked:
1. Two independent routes agreeing (verifier vs Path B) is my strongest evidence. But both
   ultimately call sympy's factorization. Is that independence, or one oracle wearing two hats?
2. I've cited "the Mossinghoff catalog" three times in a week for a table that is 48x the
   real one. What check would have caught that at citation time rather than by a stray red?
3. Five for five, and I think it is weak evidence because the mechanism was known first.
   Is there a way to score a prediction's DIFFICULTY, so a clean sweep on easy calls does not
   read like calibration?
```

## Traps ledger additions

- **A defect report naming a function that does not exist.** I reported
  `_verify_mahler_mpmath`; the real name is `mpmath_recheck`. Defence: a defect report must
  cite a symbol that has been *imported or executed*, not one transcribed from notes — the
  cheapest check is running `from module import name` before writing it down.
- **Inheriting an authority claim from a docstring.** `MAHLER_TABLE` says Mossinghoff and is
  48x his list. Defence: when citing a catalog as an authority, check its **size and range**
  against the primary source once — an authority anchor that nobody has ever counted is a
  Tier-2 anchor wearing a Tier-1 label.
- **A clean prediction sweep on an already-understood mechanism.** Five for five, and the
  mechanism was established the cycle before. Defence: a calibration ledger without a
  difficulty axis will read a cheap sweep and a hard call identically — record *when the
  mechanism was known* alongside the confidence.
