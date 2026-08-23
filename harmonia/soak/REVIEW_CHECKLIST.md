# Review checklist — derived from the Harmonia-A shadow soak

**Provenance rule:** every item below cites the finding that earned it. Nothing here is
general advice; each check caught something real during 48 passes (2026-08-20 → 08-21).
Source record: `engine/shadow/WORKLOG.jsonl` (120 findings, 30 of them corrections).

The soak's own headline: **more defects were found in the reviewer's instruments than in
the code under review.** Weight the checklist accordingly — Section A first.

---

## Fast path — five checks with the highest yield

If you do nothing else, do these. Between them they caught most of what the soak caught.

| # | Check | The tell |
|---|---|---|
| 1 | **A uniform result is a claim about your instrument** | `0 of N`, `N of N`, or every case identical |
| 2 | **Search before claiming absence** | "there is no test for X" without a grep |
| 3 | **Measure the effect before stating severity** | a severity reached by tracing a mechanism forward |
| 4 | **Check the runner before believing a red** | errors describing the harness, not the code |
| 5 | **Count the population before building an instrument** | machinery for a question with <10 candidates |

---

## A. Before you trust a number

**A1 — A uniform result is a statement about the instrument first.**
`0 of 140`, `5 of 5`, `115 of 115`, "no change in any of five cases." Stop and diagnose.
*Caught: a false contamination finding (P27), a false "registry entries don't matter" (P36), a
vacuous production census (P41), a meaningless 100% audit (P47).* — SOAK-63, SOAK-106, SOAK-116

**A2 — Report a pass rate only with a measured power to fail.**
Perturb known-good inputs; count how often the check notices. A check that cannot fail
produces a number shaped exactly like evidence.
*An auditor returning 115/115 measured at **59% power** — four in ten wrong values passed.* — SOAK-115

**A3 — Count the population before building the instrument.**
Below ~10 candidates, reading is cheaper and correct.
*Two consecutive passes built censuses for a question whose population was **2 tests in 1 file**.* — SOAK-110

**A4 — A marker regex cannot make a semantic distinction.**
Pattern-matching a name where the question is about meaning yields a confident wrong number.
*Three over-broad censuses in four passes: counted `/` in comments, tested syntax before
validity, matched a namedtuple field name.* — SOAK-108

**A5 — Write the instrument's rule down before running it.**
A tuned rule and a validated rule are indistinguishable in the finished artifact.
*A rule fixed in advance failed calibration by one case; the temptation to add a clause and
rerun was immediate and would have been invisible.* — SOAK-111

**A6 — Check the intended runner before believing a failure.**
*A self-running validator reported "7 errors" under pytest and **34 passed** under its own
runner. The docstring said so; the automated runner cannot read docstrings.* — P29

**A7 — Byte-identical restore does not restore the machine.**
Python validates `.pyc` on **mtime + size only**. A same-length edit restored in the same
second leaves stale bytecode.
*A `finally` block, a byte-identity assertion and a clean `git status` all passed while the
host served mutated code for **3.5 hours**.* — SOAK-82

**A8 — Watch for two module objects with separate state.**
A bare `import x` alongside `from pkg import x` gives you two modules; mutating one changes
nothing. *Tell: a mutation that "takes" but has no effect.* — P36

---

## B. When the artifact is a test or a pin

**B1 — Existence is not efficacy. Simulate the regression.**
Reading a new assertion is exactly as uninformative as reading the old one was. — P12, P26

**B2 — One regression shape is not verification.**
*A pin that survived full removal was blind to two partial rots — **2 of 4**.* — P30

**B3 — Input variety is uncorrelated with discriminating power.**
*Five distinct-looking malformed inputs caught the **identical** mutation set — five shapes,
one bit between them.* — SOAK-65

**B4 — Report the crash-vs-assertion split with any mutation score.**
A test runner reports "failed" whether the code crashed or an assertion discriminated.
*Two pins both scoring 4/4: one got **3 of 4 catches from the loader crashing**, the other
**3 of 3 from its own assertions**. Same number, opposite engineering.* — SOAK-88, SOAK-94

**B5 — Does the test quantify over a hardcoded population?**
*A test asserting "every cid is registered" iterated a **literal five-entry dict**, not the
generator's list. Adding a sixth turned nothing red.* — SOAK-77

**B6 — Is a soundness check standing in for a completeness one?**
"The recorded answer **is** a solution" ≠ "it is **the** solution set."
*A green suite visited a degenerate case **22 times per run** and certified an incomplete
ground truth. Both its assertions were true.* — SOAK-103

**B7 — A contract declared as a tuple is a coverage checklist.**
*`transform_errors = (ValueError, OverflowError)` — every operator in the pin raised only the
first. Half the declared contract was untested.* — SOAK-68

**B8 — Asymmetric pinning may be rational. Check traffic before calling it neglect.**
*Two sibling paths, one pinned. The pinned one carried **15%** of traffic and the unpinned one
**0%** — the asymmetry tracked the traffic.* — SOAK-70 → SOAK-74

---

## C. When the artifact is a claim

**C1 — Existence and reachability are separate obligations.**
A real defect can be unreachable. State which you measured. — P14, P32→P33

**C2 — Measure the effect before stating severity.**
*Six consecutive passes had a severity deflated on measurement. Every escalation came from
tracing a mechanism forward; every deflation from measuring an effect.* — SOAK-78, SOAK-93

**C3 — Base rate before disposition. N instances are not a pattern.**
*A finding generalised at N=2 was demoted to two instances.* — SOAK-28, SOAK-106

**C4 — Publish the denominator with every rate.**
*`8 of 8` correct is meaningless without `of 42 claims, chosen by their own author`.* — P16, SOAK-119

**C5 — Distinguish correct-by-instrument from correct-by-luck.**
*A staleness claim survived re-checking only because the file had one commit in its history;
the broken guard would have missed a change had there been one.* — SOAK-74

**C6 — Search before claiming absence.**
*The one method failure a reviewer named in this channel nearly recurred nine passes later —
and what prevented it was remembering the **criticism**, not the finding.* — SOAK-76

**C7 — Adopted is not verified. Re-measure the shipped form.**
*A two-line patch was adopted with a **substitution**; the shipped shape worked, by a
different mechanism than the one verified.* — SOAK-69

**C8 — Reproduction is not correctness.**
Re-running the same probe proves it wasn't corrupted, not that it was right. Replicate with a
mechanism whose failure modes are disjoint. — P37 → P38

---

## D. When the artifact is a document

**D1 — Re-execute the document against live data. Docs decay like code.**
*A trap checklist described brace-literal arrays; the table stored JSON brackets, and its
stated Python hazard did not apply. Both halves wrong, carried forward and cited for months.* — SOAK-97

**D2 — A documented instance gets read as THE instance.**
*A trap documented as one column in one table was present in **four**. Nothing in the format
distinguishes an example from an inventory.* — SOAK-101

**D3 — Citation frequency is not registration.**
*The soak's most-cited finding (~40 commit messages) was the **only** id with no structured
record. The more often something is referenced, the less likely anyone checks it was entered.* — SOAK-112

**D4 — Say whether you are citing a summary or the record.**
*The verdict artifact cited **64 of 110** findings. A summary presented as a record inflates
coverage by exactly what it omits.* — SOAK-113

**D5 — Restatement blocks mechanical cross-checking.**
*A log saying `4/4` where the record says `{M1,M2,M3,M4}` is faithful and unverifiable by any
token matcher. Where a summary paraphrases, the only audit is reading.* — SOAK-118

---

## E. Loop hygiene

**E1 — Re-check your inputs immediately before acting, not only at setup.**
*Reviews arriving mid-pass were structurally guaranteed to be answered a pass late, because
the procedure re-read steering before pushing but never re-read reviews.* — SOAK-73

**E2 — Check rotation mechanically; praise hides narrowing.**
*Fifteen consecutive passes used one arm of a three-arm rotation. A reviewer had just called
that chain the strongest structural pattern in either channel — which is what made the
narrowing invisible.* — SOAK-99

**E3 — A finding that retires work must carry the command that revives it.**
*A retirement was cited for 20 passes without re-checking whether its subject had changed.* — SOAK-105

**E4 — A weakness list should obligate something downstream.**
*48 records contain many named-but-unpaid costs. The difference between a list that documents
and one that obligates is whether anything consumes it.* — SOAK-120

---

## Known limits of this checklist

- Derived from **one** worker, **one** channel, **48** passes. No second party has verified the
  findings it rests on.
- Weighted toward instrument failure because that is what this soak produced; a different
  workload would surface different classes.
- Items A1 and A2 overlap: A1 is a shape you notice, A2 is a check you run. A1 caught four
  errors here and depends on the result *happening* to look odd; A2 would have caught all
  four and does not.
