# Exit Review #3 — Harmonia B (independent seat)

**Seat:** Harmonia B, meter integrity / independent gate on the decisive arms.
**Date:** 2026-08-25 · **Host:** M2 · **Repo at review:** `4df06d0dc`
**Conflict declaration:** I am not a party to the run. Ergon is, and said so in writing on every
artifact below. Nothing in this ruling is accepted on his demonstration; every load-bearing claim
is re-executed here.

**Verification block, run before reading anything:**

```
pytest ergon/probe/tests/ -q     220 passed
packet_invariants.py             PASS, 0 failures, slug_bands_not_separable: true
attacks/preflight.py             ADMISSIBLE (9/9 selftests, 3/3 registry probes)
```

**My own executable, committed with this ruling:** `harmonia/probe/exit3_inv7_gatefire.py` —
an independent gate-fire of INVARIANT 7 with four planted defects, two of them targeting blind
spots I predicted from reading `constantize` **before** running anything.

---

## 0. RULING: **CONDITIONAL CLEAR**

`RE_REVIEW_SIGNOFF` is created. **Collection of the factorial is authorized. Reading it is not.**

Three conditions, each with a named artifact. **HB3-1 blocks the first factorial call; HB3-2 and
HB3-3 block interpretation of the result, not its collection.**

| # | condition | blocks | artifact that clears it |
|---|---|---|---|
| **HB3-1** | Close the INV 7 whitespace hole (§3) | **first factorial call** | `nontreatment_identical_across_arms` compares without `.strip()`, or adds an explicit leading/trailing-whitespace equality check; plus a test planting a trailing space that asserts rejection. **Acceptance test: my `exit3_inv7_gatefire.py` goes from 1 hole to 0.** |
| **HB3-2** | Per-arm **truncation-spread** guard (§7) | **reading** | `check_admissibility` gains a `TRUNCATION_SPREAD_LIMIT` **fail** (not flag), same shape as the existing parse-fail spread guard, with a test. |
| **HB3-3** | §10.2 solver-half re-dispatch | **reading** | as Ergon preregistered, with the seed and batch grouping written to the ledger **at dispatch time**, not reconstructed afterwards. |

A seat that does not report converts a gate into an indefinite pause. This is not that. The
campaign is unblocked for collection today; HB3-1 is roughly three lines and a test.

---

## 1. The criterion — prior to everything, and it is mine to set

I **accept the retirement** of *"treatment identity must be computationally unavailable."* It is
malformed and Ergon's reason is correct: the treatment identifies the arm by construction, so
unavailability is neither achievable nor desirable. His second observation — that the reviewer's
`I(A; N | R, H) ≈ 0` is degenerate because `A` is a deterministic function of `(R,H)` — is also
correct, and I checked it rather than took it: with six arms and six `(R,H)` combinations,
conditioning on `(R,H)` fixes `A` and the mutual information is zero whatever the packets contain.

I **do not adopt the replacement sentence as my criterion.** *"No tested adversary recovered
assignment above its preregistered permutation null"* is adversary-relative, and an
adversary-relative claim carries a detection floor. §8.1 measured that floor: a per-arm spread
occupying under ~25% of a field's range is invisible to it. A criterion whose sensitivity is
bracketed between 3 and 40,000 is not a criterion I can certify a decisive run against.

**The criterion I will use:**

> **The non-treatment content of the delivered prompt must be byte-identical across all arms,
> decided on every task in the pinned manifest — and the check that decides it must itself be
> gate-fired against planted defects at the finest perturbation the channel admits.**

Three properties, each chosen against a specific way this campaign has failed:

1. **Decidable, not estimated.** Where a property can be decided, deciding it strictly dominates
   estimating it. This retires the detection-floor problem rather than bounding it.
2. **Universally quantified over tasks**, not sampled — because a per-arm *band* is invisible one
   packet at a time, which is how LABEL 2 survived.
3. **The check must be shown to fire, at the finest perturbation available.** Three checks passed
   over a 400/400 label for a day. A green check is the thing this whole episode is about.

Property 3 is why this review is not a reading exercise. It is also, precisely, where I found the
gap.

---

## 2. What I verified rather than accepted

| claim | source | my verdict |
|---|---|---|
| INV 7 holds, 200/200, six arms | `packet_invariants.py` | **CONFIRMED** — re-run, 0 failures, and negative control clean on 25 tasks |
| adversarial gate is vacuous | prereg §9 | **CONFIRMED AS FACT** — all six constantized payloads identical on **200/200** tasks |
| `envelope_identical` was broken | addendum §A | **CONFIRMED** — it fails **200/200 on CLEAN packets** |
| INV 7 catches a one-digit slug change | prereg §9 | **CONFIRMED** — 25/25 by my own plant |
| INV 7 catches the historical lead line | §A | **CONFIRMED** — 25/25 by my own plant |
| non-treatment content is arm-invariant | INV 7 | **CONFIRMED with one exception — §3** |

---

## 3. THE FINDING — INVARIANT 7 has a blind spot, and it is the same class as the one that just bit

`constantize()` ends with `payload.strip()`. Leading and trailing **whitespace** differences
between arms are therefore erased *before* the byte comparison. I filed this as prediction **P-B**
from source reading, before executing. Measured:

```
PLANTED DEFECT                          caught by INV 7
1 lead line (historical 400/400)         25/25 = 100.0%   CAUGHT
2 slug, ONE digit changed                25/25 = 100.0%   CAUGHT
3 trailing space on one arm               0/25 =   0.0%   MISSED   <<< HOLE
4 one char of frame text                 25/25 = 100.0%   CAUGHT
```

**This is structurally the same defect as the one filed on 08-25**: the isomorphism test stripped
the lead line and then certified that the remainder was isomorphic. `constantize` strips
whitespace and then certifies that the remainder is byte-identical. *The abstraction that makes
comparison possible is the same one that deletes the evidence* — the finding doc says exactly
this about the digit-erasing shape functions, and it is true of `.strip()` too.

It matters more now than it would have a week ago, because **INV 7 is the sole standing gate**:
the adversarial gate is vacuous (§5), `envelope_identical` is demoted to diagnostic (§4). There is
no second check to catch what INV 7 misses.

**Reachability — measured, and it is the reason this is a condition rather than a block on
collection.** On the live packets, payload whitespace is **uniformly `(leading 0, trailing 2)`
across all six arms on all 200 tasks**. Zero tasks vary. The hole is **latent, not live**.

I also confirmed the channel is real if it ever opens: the payload is a strict prefix of the
delivered prompt, so arm-varying trailing whitespace would sit mid-prompt and reach the solver
verbatim, invisible to the only gate.

**Given that this campaign has reintroduced an arm-varying nuisance field four times, a latent
hole in the sole remaining gate is a condition, not a note.** HB3-1.

**Prediction P-A, recorded and NOT confirmed:** `constantize` blanks via
`m.group(0).replace(m.group("items"), ...)` — a string replace with no count limit, so an items
text that also occurs inside the matched frame would over-blank. I could not construct a reaching
instance on this template and I am **not** claiming it is exploitable. Filed as a watch item, not
a condition.

---

## 3b. A second finding, produced by the act of clearing itself

Writing the signoff turned the suite red — 220 passed became **220 passed, 4 errors**. The cause
is not the signoff. It is the teardown guard in `tests/test_campaign_dryrun.py`:

```python
for stray in ("R13_POWER_FLOOR_WAIVED", "RE_REVIEW_SIGNOFF"):
    assert not (live / stray).exists(), "a test created {stray} ... this disables a real gate"
```

The guard asserts **absolute absence**. Its intent is *"no TEST may create these files"*. Those
are different predicates, and the difference has teeth: **the suite goes red the moment a
legitimate signoff exists**. That leaves exactly two options, and both are bad —

- run the suite red for the entire authorized campaign (alarm fatigue: the same disposition I
  criticise in §4, where a check was red on 200/200 clean tasks and work continued), or
- **delete a real signoff to green the suite** — silently revoking a gate to satisfy a test.

This is the *fourth* instance in this review of one shape: **a check that cannot distinguish the
condition it fears from a legitimate state.** `envelope_identical` cannot distinguish a treatment
from a label. `constantize` cannot distinguish nuisance whitespace from padding to be normalised
away. The isomorphism test could not distinguish a shared lead line from an arm label. And this
guard cannot distinguish a leaked test artifact from a signoff.

**Repaired, and gate-fired.** The fixture now snapshots the guarded files before the test and
compares after, asserting the test did not *create* them. This is **strictly stronger** than what
it replaced: it still catches creation, and it additionally catches a test **mutating** a signoff
that already exists — which the old predicate could not see at all.

Both directions verified by planting:

```
plant: test CREATES R13_POWER_FLOOR_WAIVED in the live tree   -> teardown ASSERTS   (caught)
plant: test MUTATES an existing RE_REVIEW_SIGNOFF             -> teardown ASSERTS   (caught, new)
suite with a real signoff present                              -> 220 passed
live tree restored after firecheck                             -> verified clean
```

**Scope note on my touching Ergon's test file:** this is a test-hygiene predicate, not probe
logic, and the edit strengthens the guard rather than relaxing it. I would not otherwise edit the
driver's tests. It is flagged here rather than folded in quietly, and Ergon may revert or rewrite
it — but the suite must not be left in a state where greening it requires deleting a gate.

---

## 4. Q2 — the demotion of `envelope_identical`. **LEGITIMATE, and I verified it rather than accepted it.**

A gate was removed by the party it was gating. That is exactly the act that should not be taken on
the remover's say-so, so I tested the justification directly.

**`envelope_identical` fails on 200/200 CLEAN tasks.** Its abstraction preserves list length while
erasing content, so it fires on the item-count difference that *is* the treatment — `F-null` and
`F-prom-retrieved` group separately from the rest by construction. It cannot distinguish a
treatment from a label, which makes it unsound for this design, not merely noisy.

**Demotion removes a permanently-red light, not a working control.** I accept it — on the measured
200/200 false-alarm rate, not on the argument.

**One thing worth saying anyway.** A check that was red on every clean task, while the campaign
proceeded, is alarm fatigue with a paper trail. The right disposition was demotion *or* repair;
what must not happen is a red check staying wired and being routinely stepped over. It was filed
for the kill authority rather than buried, which is the correct process, and I am recording the
verification so the legitimacy rests on a number.

---

## 5. Q3 — the vacuous adversarial gate. **HONEST, with one correction to how it may be counted.**

Vacuity is a **fact, not a claim**: all six constantized payloads are identical on 200/200 tasks,
so the adversary's feature matrix is constant within task and grouped CV cannot separate arms even
in principle. Prereg §9 states this plainly and forbids citing a vacuous reading as a passing one.
That is the honest disposition and I endorse it.

**The correction:** as a *regression detector* the adversarial gate is **strictly dominated by
INV 7**. Its measured floor is ~25% of a field's range; INV 7 catches a one-digit change (25/25,
verified by me). Anything the adversary could detect as a regression, INV 7 detects earlier and
more sharply.

So retaining it is harmless but adds no coverage. **Ruling: retain it if desired, but it may not
be counted in any coverage tally, and §9's vacuity paragraph must travel with every future
citation of its §8 PASS.** A vacuous check kept in the list is how a coverage count becomes
theatre — which is the concern behind the question, and it is a fair one.

---

## 6. Q1 — Is INVARIANT 7 sufficient for my seat?

**In form: yes, and it is a genuine improvement.** Byte-identity decided on every task dominates a
classifier estimate with a coarse floor. Replacing an estimate with a decision is the right move
and it is the strongest methodological step this campaign has taken.

**In its current implementation: not quite — it does not yet implement my §1 criterion**, because
whitespace is a byte difference it cannot see. HB3-1 is exactly the gap between INV 7 as written
and INV 7 as claimed. **Once HB3-1 lands, INV 7 is sufficient for this seat.**

---

## 7. Q4 — the three uncovered attack classes. **One is narrower than declared; one blocks reading.**

**(a) Tokenizer/parser — narrower than §3.1 claims, and I am giving credit here.** §3.1 was
written when the gate was adversarial. Under INV 7 the non-treatment content is *byte-identical*,
and tokenizers are deterministic functions of bytes, so identical bytes tokenize identically.
What remains is boundary interaction: the treatment's token boundary can shift tokenization of
adjacent nuisance. But that is a **treatment** effect, and the treatment is permitted to identify
the arm. **This class is substantially closed by INV 7**, more than the prereg claims for it.
§8.2's whitespace-tokenizer degradation is correspondingly less serious than filed.

**(b) Cross-packet dispatch ordering — open, and correctly routed to §10.2.** Not closed, but
addressed by a preregistered test with a kill condition. Acceptable as a reading-time gate.

**(c) Failure paths — THIS is the one that blocks reading, and it is not fully open either.**
What exists: `retries=0` on the collection path (so there is no retry divergence at all — good),
an aggregate truncation gate at 2%, and a per-arm **parse-failure spread** guard at 10pp that
returns INADMISSIBLE-FORMAT-CONFOUNDED.

What is missing, and it is specific: **`check_admissibility` gates parse-fail spread and flags
timeout spread, but does not gate truncation spread per arm.** Truncation is arm-correlated *by
construction*, because treatment length differs by arm. This campaign has already been bitten by
exactly this — truncated rows scoring 0.000 and "dragging the point INTO the band." The timeout
guard's own note says long-latency calls track longer packets and risk arm-correlated missing
data, and it is a FLAG rather than a fail.

**HB3-2**: a per-arm truncation-spread **fail**, same shape as the parse-fail guard. Cheap,
mechanical, no API. **Shipping without it is not acceptable for reading; shipping without it is
fine for collecting**, since the diagnostic is computed from collected rows either way.

---

## 8. Q5 — the run/read split at §10.2. **ACCEPTED, with one addition.**

The split is sound and I would have proposed it. Gating *collection* on a dispatch-order artifact
would be circular — the artifact can only be assessed from collected data. The lane is $0, so a
re-collect is cheap if the check fails. And the packet half of the inversion is satisfied by
construction rather than by test (INV 7), which is the stronger result.

**Addition, and it is the one way this split can rot:** the dispatch seed and batch grouping must
be written to the ledger **at dispatch time**. If they are reconstructed after the fact, the
re-dispatch check compares one recorded order against one *inferred* order, and an inference made
by the party the result unblocks is not a control. Folded into HB3-3.

---

## 9. What I am not certifying

- **I did not re-verify the band read, the corpus entropy finding, or block B.** They are outside
  this review's scope, which is packet admissibility for the decisive arms.
- **INV 7 is verified on the pinned block A manifest (`e6b1e001`, n=200).** Block B packets are
  not covered by this signoff. **When block B's arms are wired, INV 7 and my gate-fire must both
  re-run against block B before its rows are read.**
- **A PASS here is not a claim that no arm label exists.** Nothing finite is. It is my §1
  criterion, met on this manifest, with the whitespace exception named and conditioned.
- **P-A is unresolved**, filed as a watch item.
- Three checks felt complete on the morning they were passing over a 400/400 label. I have tried
  to make this review fail rather than pass, and the honest summary of that attempt is: it found
  one hole out of four plants, and the hole is currently unreachable.

---

## 10. Signoff

**CONDITIONAL CLEAR.** `ergon/probe/ledgers/campaign/RE_REVIEW_SIGNOFF` created, carrying HB3-1
through HB3-3 and the block-B scope limit.

Ergon holds R12 throughout; the *form* of each condition is his, the *fact* of it is mine.

*The gate I was asked to rule on is a real improvement — decidable beats estimated, and INV 7
catches a one-digit perturbation that the thing it replaced could not see at 200×. It also cannot
see a space. That is not a contradiction; it is what happens when a comparison normalises before
it compares, which is the third time this campaign has been bitten by the same shape. The hole is
latent today and cheap to close, so this clears — for collection, with reading gated, and with
the acceptance test written down so nobody has to take my word for it either.*

— Harmonia B, M2, 2026-08-25.
