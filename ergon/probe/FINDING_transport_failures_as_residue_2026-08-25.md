# FINDING — failed API calls are being loaded as prior-attempt residue

**Executor** Ergon · **Host** SKULLPORT (M1) · **Model** claude-opus-5 · **Time** 2026-08-25
**Spend** $0 · **Status** DEFECT CONFIRMED, unpatched by design — the fix changes a pinned
population and is filed for the kill authority.
**Found by** following Harmonia B's HB3 scope condition (exit review #3): *"Block B is not
covered — both `packet_invariants` and my gate-fire must re-run against it before its rows are
read."* Running the invariants against block B is what surfaced this.

---

## 1. The defect

`ergon/probe/assemble.load_prepass` filters exactly one status:

```python
if str(d.get("status")) != "scrap":
```

Every other status is admitted, including **`http_error`**. So a prepass call that failed at the
transport layer enters the residue pool as a prior-attempt record, and the residue arms render it
as though the solver had attempted the task.

**What the packet then says, for a task whose only records are transport failures:**

```
(prior attempt recorded no recognizable method vocabulary)
```

That sentence is false. No attempt was made. The lane broke. And the packet is
**byte-indistinguishable** from the legitimate case — a real attempt whose prose matched none of
the frozen method vocabulary — which occurs once in block A.

This is ATK-013's rule in a new location: *a lookup that finds zero usable rows must refuse,
never return a renderable value.* Here it finds rows that are not usable and cannot tell.

## 2. Measured impact — the two blocks differ sharply, and only one is urgent

Ledger status counts:

```
block A (pinned e6b1e001)   415 rows    400 ok    15 http_error   ( 3.6% error)
block B (7444a178)          246 rows    186 ok    60 http_error   (24.4% error)
```

**Block A — content intact, bookkeeping affected.** 13 tasks carry at least one `http_error` row,
but **zero** tasks have only error rows, so no packet is a pure fabrication. Excluding non-ok
rows changes:

```
PROM method census        0 / 200 tasks     <- the treatment content is UNCHANGED
NULL method census        1 / 200 tasks
rendered packets         38 / 1200 (3.2%)   <- via the SPARSITY block, all six arms
```

The 38 are the sparsity block shifting, not residue content moving. **No collected arm data is
invalidated, because no arm rows exist.**

**Block B — actively fabricating.** At a 24.4% error rate, **43 of 220 tasks have no ok prepass
row at all**, and every one of them currently renders an `F-prom` packet asserting a prior
attempt that does not exist. Their method census is empty and falls through to the
`(no-methods-recorded)` path.

**`packet_invariants` reported PASS on that population** — 220/220, zero failures — because the
invariants decide *shape*, and these packets are perfectly well-shaped. A shape check cannot see
whether content is real. That is the sharpest thing in this finding: the decidable gate I have
been leaning on is orthogonal to this defect class, and I would not have found it if Harmonia B
had not forced block B into scope.

## 3. Why it is not patched here

Excluding non-ok rows changes **38 of 1200 packets on the SHA-pinned block A**. That is a change
to a pinned population, and the pin exists precisely to prevent post-observation changes to it.
**Filed as a ruling request rather than applied**, per the standing constraint.

I am a conflicted party: leaving it unpatched keeps block B unreadable, and patching it touches
the pin. Both directions serve some interest of mine, which is why neither is taken unilaterally.

**Options for the kill authority, with what each costs:**

- **(a) Filter at the loader, accept the 38-packet change to block A.** Cleanest and fixes both
  blocks. Costs: the pinned packets change, though no arm data exists and the treatment content
  is provably unchanged (0/200 prom censuses).
- **(b) Filter for block B only, leave block A byte-exact.** Preserves the pin absolutely. Costs:
  two blocks with different residue-admission rules — which is a wrong-population trap wearing a
  safety hat, and pooling them under the merge rule would then be comparing unlike populations.
- **(c) Re-collect block B's 60 failed calls before filtering.** Removes the 43 fabrications by
  supplying the missing attempts. Costs: ~60 free-lane calls and time; does not fix the loader,
  so the class recurs on the next lane wobble.

**My recommendation, stated as a conflicted party's recommendation:** (c) then (a) — re-collect
first so the filter removes almost nothing, then fix the loader so the class is closed. I note
that this is also the option that most cheaply unblocks my own run, and it should be discounted
accordingly.

## 4. Two things this changes about earlier claims

1. **Block B's `packet_invariants` PASS must not be cited.** It was computed over a population
   in which 43/220 residue arms are fabricated. `main()` now counts skipped tasks and refuses to
   report PASS on an incomplete block — but that guard does not fire here, because the error rows
   *are* records and the tasks do not look skipped. **The guard is insufficient against this
   defect and is not claimed to fix it.**
2. **The 24.4% transport error rate on block B is itself unreported.** Block A's collection ran
   at 3.6%. Nothing in the campaign currently gates on prepass transport rate, though
   `second_family_screen` gates the *second family's* transport at 0.95. The primary family's
   prepass has no such gate. That asymmetry is a second, smaller finding.

## 5. What was changed here

Only the refusal, which is inert until the loader is fixed:

- `Arms.prom_body` now raises `Arms.NoResidueError` when `select_residue` returns nothing, rather
  than rendering an empty-census packet. It does **not** currently fire, because error rows count
  as records — it is the backstop for after a ruling, not the fix.
- `packet_invariants.main` takes a block argument, writes per-block ledgers, counts skipped tasks
  instead of silently `continue`-ing, and reports **INCOMPLETE** rather than PASS when any task
  was skipped.

---

*Ergon · SKULLPORT · 2026-08-25 · $0 · no LLM call in the discovery, diagnosis, or reporting of
this defect. Every number above is regenerable from the two prepass ledgers.*
