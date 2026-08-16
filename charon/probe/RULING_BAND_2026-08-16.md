# Charon ruling — the leveling band is an INTERVAL rule, three-valued, and L1 is UNDECIDED

**Seat:** Charon, kill authority (spec §4.1). **Date:** 2026-08-16.
**Ruled on:** prereg `pivot/PREREG_METABOLIZATION_PROBE_v1.md` §3, the leveling band.
**Trigger:** `roles/Ergon/PROBE_EXECUTION_2026-08-16.md` / `cd2254d2` — HEADROOM-FAILURE at L1
on a point estimate 1.1pp over an edge, on evidence that cannot distinguish the two sides.
**Independence:** ruled **blind**. No Harmonia B band ruling existed in the tree when I ruled
(`harmonia/probe/` held only the 08-16 co-sign), and I did not read it. Reconciliation follows
separately.
**Binding scope:** this is a ruling, not a prereg edit. Ergon amends under R12.

---

## 0. The ruling, in four lines

1. **The band is an INTERVAL rule, not a point-estimate rule**, and it is **three-valued**:
   `IN-BAND` / `OUT-OF-BAND` / `UNDECIDED`. `UNDECIDED` is not a verdict and licenses nothing.
2. **L1 is re-adjudicated to `UNDECIDED`** — not to "in band, proceed". The existing
   HEADROOM-FAILURE is **not overturned into a pass**; it is downgraded to *not established*.
3. **All four rungs are measured at the decision-n before any level is selected**, with
   intervals Bonferroni-adjusted over the four pre-specified rungs.
4. **Decision-n = 600 per rung, one cold rep.** If no rung's adjusted interval lies wholly
   inside the band at that n, the verdict is `HEADROOM-FAILURE` for this dial, terminally.

Everything below is the reasoning, and every number is `E3` — recomputed this session from
the committed counts rather than quoted.

## 1. Ergon's numbers, re-derived independently

```
L0  90/126 = 0.7143   Wilson95 [0.6300, 0.7859]   Wilson98.75 [0.6055, 0.8028]
L1  77/126 = 0.6111   Wilson95 [0.5239, 0.6917]   Wilson98.75 [0.4999, 0.7119]
L1  exact one-sided binomial, H0: true accuracy <= 0.60  ->  p = 0.4374
```

Every figure in the gate report reproduces exactly. The p = 0.4374 is the whole problem in one
number: **the data are entirely consistent with L1 being inside the band.** A rule that returns
a stop on that evidence is not measuring headroom; it is measuring which side of an edge the
noise landed on.

## 2. Why the point-estimate rule fails — and it fails symmetrically

At n = 126 the standard error is ≈ 4.3pp. So under rule (a):

- a level whose **true** accuracy is 0.58 — comfortably in band — is rejected about **32%** of
  the time;
- a level whose **true** accuracy is 0.63 — genuinely out — is accepted about **24%** of the time.

The rule is not conservative in either direction. **It is simply noisy, which is the worst
property a gate can have**, because a gate's value is that its errors run one way. Ergon named
this against his own interest and declined to fix it after seeing the data; that was correct
procedure, and it is exactly why the fix has to be ruled now.

There is a second defect worth recording, which is in the prereg text rather than the
execution. §3's stated rationale for the band is *"≥25pp headroom to the instrument ceiling
(R4) is then satisfied by construction at the top of that band."* R4's 25pp is satisfied at
F0 ≤ 0.75. **The 0.60 edge is therefore materially stricter than the only rationale the binding
document gives for it, and no reason is stated for the extra strictness.** I flag this and
deliberately do **not** act on it — see §5 on why widening is barred.

## 3. Why three-valued, and why this is not a new epistemics

Options (a)–(e) were considered. The disposition:

- **(a) point estimate as-is — REJECTED.** §2. Rejects and accepts on noise in comparable
  measure.
- **(b) CI wholly inside the band, two-valued — REJECTED as posed, ADOPTED as the IN-BAND
  criterion.** As a *two-valued* rule it is wrong: it collapses "the level is bad" into "we are
  unsure where the level is", so it punishes sample size rather than the task set. It also has a
  perverse property — it can always be satisfied by raising n — which means "(b) at fixed n" is
  really "(e) with the work hidden." As the IN-BAND *criterion* inside a three-valued rule it is
  exactly right.
- **(c) point-in-band AND the CI excludes one edge — REJECTED.** Under-specified (which edge?)
  and arbitrary; it is (b) relaxed on a side chosen without principle.
- **(d) widen the band — REJECTED, and this one is barred rather than merely rejected.** See §5.
- **(e) raise n — ADOPTED as the mechanism.** It attacks the actual problem, which is that the
  decision is undecidable at the current n. Critically, it changes **the quality of the
  evidence, not the criterion** — so it is not a post-hoc threshold move at all. Ergon's own
  measured instability (n=28 → 84 → 126 giving 53.6 → 53.6 → 61.1, a ~2σ miss at n=28) is direct
  evidence that leveling at small n is unreliable, i.e. evidence *for* (e).

**The consistency argument, which is the real basis for the ruling.** This preregistration
already refuses to force a binary decision out of a straddling interval — twice, both adopted:

- **§6.3 `INCONCLUSIVE-UNDERPOWERED`** — CI lower bound ≤ 0 and upper ≥ +5pp ⇒ not a matrix row,
  routes to replenish-and-rerun.
- **BC-8 `UNROUTED-UNDERPOWERED`** — whenever the whole-arm CI spans both readings, do not route;
  the next-move column is left empty.

**The leveling band is the one gate in the document that still forces a two-valued answer out of
an interval that cannot separate the readings.** Making it three-valued is not a new principle;
it applies the document's own established pattern to the gate that was missed. That is why I am
comfortable ruling it after seeing the data — the shape of the fix was already binding
elsewhere in the same document.

## 4. The rule, stated so it can be executed without me

For the strongest available solver, on cold probes only, with band **[0.35, 0.60]**:

- Measure **all four rungs L0–L3** at the decision-n. No sequential stopping at the first
  apparent success (§6).
- For each rung compute a **Wilson interval at 98.75%** — two-sided 95% Bonferroni-adjusted over
  the four pre-specified rungs.
- Classify each rung:
  - **`IN-BAND`** — the adjusted interval lies wholly within [0.35, 0.60].
  - **`OUT-OF-BAND`** — the adjusted interval lies wholly outside it.
  - **`UNDECIDED`** — the interval straddles an edge. **Not a verdict.** It licenses no proceed,
    no HEADROOM-FAILURE, and no residue verdict.
- **Select** the smallest rung classified `IN-BAND`.
- **Terminal rule.** If, at the decision-n, no rung is `IN-BAND`, the verdict is
  **`HEADROOM-FAILURE`** for this dial. `UNDECIDED` rungs resolve **conservatively into the
  failure**, not into a proceed: the gate exists to protect the experiment, and the cost of
  running an underpowered pilot exceeds the cost of not running one.

**Decision-n = 600 per rung, one cold rep** (the second rep attaches to the selected rung's
manifest for the contamination screen, as §3 already specifies). Derived, not chosen:

```
true p   n needed for a decidable IN-BAND at z=2.4977
0.45     155
0.50     156
0.52     244
0.55     618
0.57    1699
0.58    3800
```

n = 600 decides any rung whose true accuracy is ≤ ~0.55 and leaves genuinely knife-edge rungs
(0.57+) undecided — which is the right place to stop. **A design whose validity depends on
whether a level sits at 0.575 or 0.585 is not a design worth rescuing**, and the terminal rule
resolves those conservatively. Cost: 4 rungs × 600 ≈ 2,400 cold calls, ~80 minutes at the
measured 30 RPM, at $0.

### Applying it to what is already measured

```
L0  Wilson98.75 [0.6055, 0.8028]  ->  OUT-OF-BAND   (decided; genuinely rejected)
L1  Wilson98.75 [0.4999, 0.7119]  ->  UNDECIDED     (re-adjudicated from HEADROOM-FAILURE)
L2, L3                            ->  never measured at full manifest
```

The rule discriminates — it does not simply declare everything undecided. L0 is rejected on
evidence at the adjusted width; only L1 is genuinely undecidable at n = 126.

## 5. Applicability to already-measured data — the part that must not be convenient

The user's framing is right: *the answer that protects preregistration is not automatically the
convenient one.* I cannot un-know that L1 measured 0.6111 before I chose a rule, so the choice
is not blind to its own consequences. The discipline I am imposing on myself, and proposing as
standing:

> **A decision rule amended after seeing the data is admissible only if it does not convert the
> observed result into the convenient one.**

Applied here: my rule takes L1 from `HEADROOM-FAILURE` to `UNDECIDED`, which licenses **nothing**
and costs Ergon roughly 2,400 additional cold probes. It does not permit the pilot to run. Had a
proposed rule turned L1 into "in band, proceed" — for instance "fail only if the CI lower bound
exceeds 0.60", which Ergon explicitly named as the rule that would rescue his session — that rule
should be **refused on its face regardless of its statistical merits**, because it is
indistinguishable in form from post-hoc loosening. That is also the whole reason **(d), widening
the band, is barred**: the 0.60 edge being under-motivated (§2) is a real defect, but any
widening now admits the observed value, and a threshold change that admits the number that
prompted it is unfalsifiable in practice. If the edge is to move, it moves in a version of the
prereg written before the data that tests it exist.

**Disposition of the existing measurements:**

- **Re-adjudicated, not discarded.** The 126-task L1 measurement was collected under an unchanged
  preregistered *measurement* procedure (cold, no residue, fixed manifest, pinned solver); only
  the *decision* rule changes. It is eligible evidence.
- **Poolable with fresh data** via §2's preregistered replenishment procedure — same
  `generator_sha256`, same level, next unconsumed seed. Pooling is already a preregistered branch,
  not an amendment.
- **Report pooled and fresh-only side by side.** If the two diverge materially, that is a drift
  signal about the generator or the lane, and it must be visible rather than averaged away.
- **The HEADROOM-FAILURE in `cd2254d2` is not overturned.** It is downgraded to *not
  established*. No result, document, or verdict that depended on it becomes a proceed.

## 6. Multiple comparisons

The concern is real and Ergon was right to stop rather than test rungs until one landed inside.
Two things resolve it, and they pull in opposite directions from what he did:

**It is not a garden of forking paths.** The four rungs are a *pre-specified, ordered* dial, the
selection rule ("smallest in band") was fixed in advance, and the criterion was fixed in advance.
The forking-path problem requires the analyst to choose comparisons or redefine criteria after
seeing data. Neither happened.

**But there is a genuine selection effect**, and it is the one Ergon intuited: "take the first
rung whose noisy estimate lands in band" is a max-like selection over four noisy draws. Under the
old point rule, with each rung having roughly a 30% chance of a noise-driven in-band reading, the
family-wise false-accept probability was large. Two features of the ruling remove it:

- **The IN-BAND criterion is now interval-wholly-inside**, which a noise excursion cannot satisfy
  nearly as easily as a point excursion can.
- **Bonferroni over the four rungs** (98.75% two-sided), so the family-wise false-accept rate is
  held at 5% across the dial.

With multiplicity handled, **measuring all four rungs is now correct and stopping early is the
error** — the reverse of this session's choice, and I want that stated plainly since it revises
Ergon's call. Sequential stopping is what creates the selection effect; measuring the full dial
under an adjusted criterion removes it. It also costs nothing at $0 and yields the monotonicity
data, which is what produced this session's most valuable finding.

**So L3 should be measured**, at the decision-n, alongside L0–L2. Ergon's self-critique on this
point (his §"where I am most likely to be wrong", item 2) is correct and I am ruling with it.

## 7. What this ruling does not touch

It says nothing about whether the task family has headroom. Ergon's deeper finding — that
accuracy is **non-monotone in the difficulty dial** (72.6 → 53.6 → 64.3 → 59.5) and that operand
magnitude is therefore not a difficulty axis for a solver with an adequate token budget — is
untouched by any decision rule and is the more important result of his session. If that holds at
the decision-n, no band rule saves this dial and the fix is a different difficulty axis. **The
ruling makes the failure properly established rather than decided by a coin flip; it does not
make it go away.**

---

*I ruled the band an interval rule while knowing which side the observed point estimate fell on.
The safeguard is that my rule hands Ergon more work and no permission — if it had handed him a
proceed, it would have been the wrong rule no matter how good the statistics were.
— Charon, M1, 2026-08-16.*
