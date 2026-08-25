# Cycle 061 — the arsenal reds, by cause rather than by count

**Techne, 2026-08-25. Campaign cycle 2 of 20 under `techne/loop/CAMPAIGN_ESCAPE_RATE_PREREG.md`.**
Controls FROZEN. Section 1 was committed BEFORE the failing node ids were read.

---

## 1. PRE-REGISTRATION (committed before measuring)

**Work selected:** campaign item (b) — attack the arsenal reds, diffing by failing node id and
never by count. Plus finding #16, which I pre-announced in cycle 060 as its own isolated commit.

**The question.**

> Q: What is each red actually caused by — and how many of them are load-bearing?

The standing figure in my own brief is *"46 arsenal reds, 26+ missing optional dependencies,
gated on HITL #242."* **Cycle 060 measured 44, not 46.** The 46 is the cycle-052 baseline, which
is stale by eight cycles; the current count is 44 with a name-diff of 0 NEW and 2 GONE. That is
already one correction to a number I have been quoting, and it is the reason this cycle triages
by cause instead of attacking a total.

**Declared population, before looking.** The **complete** set of FAILED pytest node ids in
`pivot/arsenal_red_060.json`, plus the 3 collection errors in the same file. Full scan, every id
classified, no sampling and no ordered slice. The file is committed and its producing command is
recorded in it.

**Classification scheme, fixed before reading the ids** — so the buckets cannot be drawn around
whatever I happen to find:

- `MISSING_DEPENDENCY` — fails because an optional third-party package is absent. Gated on #242,
  not on me.
- `STALE_ASSERTION` — the test asserts a literal that the data or the code has since outgrown.
  The test is wrong, not the code. (#341 is a known instance.)
- `REAL_DEFECT` — the code is wrong and the test is right.
- `ENVIRONMENT` — network, filesystem, database, or platform, not mathematics.
- `UNCLASSIFIED` — I could not determine the cause within the cycle. **This bucket must exist and
  must be reported non-empty if it is non-empty**, because a triage with no residual category
  silently converts "I did not look" into "there was nothing there".

### Predictions

1. **No claim exported this cycle will be HELD by `techne/lib/claim_record.py`'s
   `Claim.promotable()`.** Confidence **high**; **D0**. This is now a mechanism claim rather than
   a guess: cycle 060 finding #17 established that the promotion rule depends on a boolean the
   author sets, so it has no capacity to block. *Opposite:* a block would mean I have
   misdiagnosed #17 and the control has some teeth after all — which would be good news and I
   would rather be wrong here.
2. **Fewer than 26 of the 44 reds are `MISSING_DEPENDENCY`.** Confidence **moderate**; **D2**.
   The "26+" figure has the same provenance as the "46" that cycle 060 measured to be 44 — an
   uncounted number carried forward across cycles. *Opposite:* 26 or more would mean the figure
   was sound and my suspicion of it is the error, which is worth knowing about my own priors on
   my own numbers.
3. **At least one red is a `STALE_ASSERTION`.** Confidence **moderate-to-high**; **D1**. #341 is
   already known to be one. *Opposite:* zero would mean #341 is not currently red, i.e. the
   outstanding ruling is about a test that is not failing.
4. **All 3 collection errors are import failures.** Confidence **high**; **D1**. *Opposite:* a
   collection error from something other than an import would be a genuinely new shape.
5. **At least one `REAL_DEFECT` exists among the reds** — arsenal code that is wrong and has a
   test saying so that nobody has acted on. Confidence **moderate**; **D2**. *Opposite:* zero
   real defects would mean the red count is entirely environmental and stale-assertion debt, and
   the "46 reds" framing has been overstating the arsenal's brokenness for eight cycles.
6. **The `UNCLASSIFIED` bucket will be non-empty.** Confidence **moderate**; **D2**. Triage of 44
   heterogeneous failures inside one cycle will not resolve every cause. *Opposite:* an empty
   residual would be suspicious and I would check whether I had widened the other buckets to
   absorb it.

### Committed in advance about finding #16

`techne/lib/cf_expansion.py::zaremba_test(1)` returns `satisfies=False` although q = 1 satisfies
Zaremba's conjecture trivially. I flagged it to James in cycle 060 as HITL #422 and said I would
fix it in cycle 061 as its own isolated commit unless told otherwise. **No ruling has arrived.**
The function is mine, the semantics are mine, and cross-role science is the only thing barred —
so I am proceeding, in a commit that touches nothing else, so that the semantic change is
reviewable on its own.

**What the fix must not do:** change any q >= 2. That is asserted, not assumed.

*— pre-registration ends here. Everything below was written after measuring.*
