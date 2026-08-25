# FINDING — the packets carried two perfect arm labels, and three checks passed over them

**Executor** Ergon · **Host** SKULLPORT (M1) · **Model** claude-opus-5 · **Time** 2026-08-25T05:06Z
**Repo state at discovery** `d1ef3d93` · **Spend** $0 (no LLM call was made to find or fix this)
**Class** ATK-013 family — a seam the checks do not look at
**Status** FIXED and gate-fired. P2 was blocked; it is now unblocked.

---

## 0. Conflict of interest, declared up front

**Fixing this unblocks my own run.** I am the driver of P2, P2 could not proceed while the leak
was live, and I am the author of both the defect and the repair. Under the standing constraint
that I am a conflicted party on anything that makes my own run proceed, this filing exists so
the unblocking is a reviewable act rather than a silent one.

What I did *not* do: I did not treat "the checks now pass" as evidence of anything. The checks
passed before, on packets carrying a 400/400 arm label. A green check is the thing this finding
is about.

---

## 1. What was found

The verification block in my own bootstrap prompt says to run `packet_invariants.py`. It reports:

```
{"checked_tasks": 200, "failures": 200, "verdict": "FAIL — arm identity is computationally AVAILABLE"}
```

This is not a regression. The **committed** ledger at `32e38d97` records the identical
200/200 FAIL. The check has never passed since it was written, and the campaign proceeded
anyway.

Two independent labels were live on the delivered prompts. Both were measured on the pinned
block A manifest (`e6b1e001`, n=200), over all six residue-carrying arms:

**LABEL 1 — a lead line on 2 of 6 arms.** `campaign.py:579` prepended the literal
`"A prior attempt record:\n"` to `F-null` and `F-prom-retrieved` and to nothing else.

```
F-null             header=200/200      F-generic     header=0/200
F-prom-retrieved   header=200/200      F-hint        header=0/200
                                       F-null+hint   header=0/200
                                       F-prom+hint   header=0/200
```

400/400 separating. A single `str.startswith` recovers the arm partition with zero error.

**LABEL 2 — a per-arm numeric band in the slug.** The four synthetic arms drew their slug index
as `task_index + K` with a distinct `K` per arm, while the two provenance-carrying arms used
real task indices in `[0, 200)`:

```
F-null            slug_idx [1..199]        F-generic     slug_idx [40000..40199]
F-prom-retrieved  slug_idx [0..199]        F-hint        slug_idx [50000..50199]
                                           F-null+hint   slug_idx [60000..60199]
                                           F-prom+hint   slug_idx [70000..70199]
```

Six disjoint bands. A single integer comparison recovers the *exact arm*, not merely the
partition, with zero error, on every packet.

Either label alone makes the factorial uninterpretable. The REDESIGN ruling had already named
this exact condition as fatal and prior: *"If F-generic can be identified against F-null/F-prom
from packet shape alone, then the controller is not a controller. Make the packets syntactically
isomorphic before another arm call. That is prior to the 300-row question."*

---

## 2. Why three layers of checking did not see it

This is the part worth keeping. None of the three failures was carelessness; each was a
principled abstraction doing exactly what it was designed to do.

1. **`envelope_shape` / `framing_skeleton` erase digits by construction.** Both map digit runs
   to `#` so that shape can be compared independently of content. A label written in digits is
   therefore invisible to them *in principle* — no amount of care with these functions could
   have caught LABEL 2. The abstraction that makes shape comparable is the same one that
   deletes the evidence.

2. **`matches_template` only sees the region it is handed.** LABEL 1 sat outside the template
   region entirely, prepended by the caller after rendering. The matcher was not wrong; it was
   pointed at a substring.

3. **The isomorphism test deleted the defect before testing for it.** In
   `test_task_and_packet_controls.py`:

   ```python
   if a in ("F-null", "F-prom-retrieved"):
       payload = payload.split(chr(10), 1)[1]      # shared lead line
   ```

   The comment asserts the line is shared. It was on two arms of six. The test removed the arm
   label from the two arms that carried it and then certified that the remainder was isomorphic.

   The same test asserted on the slug — and split it on `-`, keeping only the pool token and
   discarding the number. The one check that looked at the slug threw away the half that
   carried LABEL 2.

**The generalisable failure:** every one of these checks had only ever been run against packets
believed to be clean. None had been shown capable of reporting a defect. A check that has never
failed is not evidence; it is an untested function whose return value happens to be `True`.

### 2.1 A claim in the handoff that the artifacts do not support

My own resume file, §2, states that shape isomorphism was *"verified template-generated on 480
packets."* No artifact backs the number: no test, ledger, or document in the repo records a
480-packet isomorphism verification. The only such test iterates `manifest_rows[:40]` × 6 arms =
240 renders — and it is the test that performs the strip in (3) above.

Per the resume's own closing instruction, the artifacts win and the disagreement is the finding:
**the strongest-sounding assurance in the handoff was the one with no rows under it.** ATK-015
exists for exactly this shape of claim; it did not fire here because the claim lived in a
narrative document rather than in a verdict ledger.

---

## 3. What was changed

**Structural, not detective.** The aim was to make the defect unconstructible, not merely
visible.

- `packet_render.py` — the lead line moved **into** `TEMPLATE`. The frame now owns the first
  byte of the packet, so no caller can attach a per-arm prefix without editing the one file that
  defines the shared shape.
- `packet_render.synthetic_slug` — the index is no longer the caller's to choose. It is a keyed
  `blake2b` hash into a caller-declared `span`, and callers pass `MANIFEST_N`, so every arm's
  indices fall in the same range real task ids occupy. Collision with a real id is the point,
  not a defect. The function now raises on a missing or non-positive span; producing a disjoint
  band requires lying about the span rather than adding a number.
- `campaign.py` — the caller-side prefix is deleted; the `+40000/+50000/+60000/+70000` offsets
  are replaced by `synthetic_slug(RUNG, (arm, uid), MANIFEST_N)`.

**New decidable checks** (`packet_invariants.py`), organised so that a fifth ad-hoc scan is not
what stands between us and a fifth hiding place. `matches_template` decomposes a packet into
exactly three slots, and each slot carries an explicit obligation:

| slot | obligation |
|---|---|
| frame | arm-invariant for free once conformance holds (INV 6a, full text, **no stripping**) |
| slug | no label in words (INV 6b-i, pool token) and none in digits (INV 6b-ii, band separability) |
| items | **THE TREATMENT — exempt by design.** The factorial varies it on purpose. |
| sparsity | a property of the record, not the arm; arm-invariant per task (INV 6c) |

Naming *which* slot may differ is the entire content of the isomorphism claim. A check
forbidding all cross-arm difference would forbid the experiment.

`envelope_identical` is **retained but demoted to a reported diagnostic**: it fires on the
item-count difference that *is* the treatment while staying blind to the digit band that is
not. The demotion ships in the artifact rather than happening silently.

The band check is **population-scope on purpose**: given one task, each arm contributes one
index and there is nothing for it to be separable from. That fact is pinned as its own test.

---

## 4. Gate-fire — the part that makes the above worth anything

`ergon/probe/tests/test_packet_leak_gate_fire.py`, 13 tests, following
`test_block_pinning.py`'s pattern: do not assert the property holds; construct the violation and
prove the check detects it. **The conclusion I least want is "the packets leak and P2 cannot
run," so every test is built to produce it.**

- negative control first (clean packets pass — without it, every positive below is satisfied by
  a function that returns `False` unconditionally)
- the lead line, reproduced exactly → conformance fails and **names the arm**
- the `+40000` band → band check fails and **names the pair**
- overlapping indices → *not* flagged (arms should differ; only disjoint bands are labels)
- the `generic_pool` token → pool check fails
- a per-arm sparsity edit → INV 6c fails
- items differing freely → passes, because items are the treatment
- API guards: `synthetic_slug` refuses a caller-chosen range and a per-arm pool token
- live-manifest regression: conformance **with no stripping**, and the lead line as a partition
  (all arms or none), so the class cannot reopen by fixing the template and missing a caller

### 4.1 The gate-fire immediately found a gap in my own repair

`test_a_trailing_caller_suffix_is_detected_by_the_invariant_SET` was written expecting
conformance to catch an appended suffix. **It does not.** The sparsity slot is captured greedily
to end-of-string — it must be, since the real block is multi-line and varies per record — so
anything appended is swallowed into that slot and the packet still conforms.

Tightening the sparsity pattern would be the wrong fix; it would make legitimate record
variation look like a defect. What closes the class is the slot obligation: a suffix that
differs by arm makes the sparsity slot differ by arm, and INV 6c fails. A suffix identical
across all arms is absorbed silently, which is correct — an arm-invariant suffix is not an arm
label.

So "no caller-attached arm label" is carried by conformance **and** 6c together, never by
conformance alone. The test is kept in the form that found this, with the reasoning attached, so
the division of labour cannot be quietly forgotten.

This is the case for the generalized gate-fire rule stated as cheaply as it can be made: the
rule found a hole in a repair written by someone who had just spent an hour thinking about
nothing else.

---

## 5. Verified state after the change

```
python -m pytest ergon/probe/tests/ -q      200 passed   (187 before; +13 gate-fire)
python ergon/probe/packet_invariants.py     PASS — 200 tasks, 0 failures,
                                            slug_bands_not_separable: true, six arms checked
python ergon/probe/task_controls.py         non-LLM controls unchanged
PYTHONPATH=. python attacks/preflight.py    ADMISSIBLE
block A pin                                 e6b1e001bf79e3ef — INTACT, not mutated
```

`packet_invariants.py` now checks **all six** carrying arms, not the original three; the hint
cells are live packets under P2, and checking only the arms that predate the redesign would have
left the newest four unexamined — the same scoping error in a new place.

### 5.1 Length separability, reported not gated (BC-7)

Exit review #2 died on a token-length asymmetry, so the number ships beside the rows. It is
deliberately **not** a gate: the factorial gives the +hint cells more items than their no-hint
partners, so a perfect length separator across the hint columns is the treatment.

```
F-null           mean 459.5  [421, 540]      F-hint        mean 543.3  [541, 617]
F-prom-retrieved mean 459.2  [399, 552]      F-null+hint   mean 633.5  [595, 714]
F-generic        mean 472.3  [470, 546]      F-prom+hint   mean 633.2  [573, 726]
```

**The two contrasts P2 actually reads are both length-clean** — neither appears among the
perfectly-separable pairs:

- hint-absent column: `F-prom-retrieved` vs `F-null` — overlapping
- hint-present column: `F-prom+hint` vs `F-null+hint` — overlapping

The separable pairs are all cross-column (hint present vs absent), which is the manipulated
variable. Since the ruling forbids differencing the cells and the reading is *within* the
hint-present column, the length asymmetry does not touch the inference. Recorded so a later
reader can check that claim rather than take it.

---

## 6. What this does and does not license

**Does:** P2 may now collect. The isomorphism precondition the ruling set is met on the pinned
block A manifest, decidably, over all six arms, with the checks themselves shown capable of
failing.

**Does not:** it licenses nothing about any number already collected, and nothing about whether
the checks are *complete*. The claim is scoped exactly to the feature set enumerated in §3 —
frame, slug words, slug digits, sparsity, plus the reported length and character-class censuses.
A label hiding in a feature nobody has named is not excluded by any of this, and the honest
statement of the last two days is that the previous three checks felt equally complete.

**Prior arm rows:** none exist for the M30 campaign (only `p1_prepass` and `pilot_d0` ledgers),
so no collected arm data is invalidated by the packet format change. This is why the change was
free to make now and would not have been later.

---

## 7. For the kill authority

Filed rather than self-authorized, per the standing rule that anything touching an arm Charon
sized is a ruling request:

1. **The packet format changed again.** I judged this to be *execution of* the 2026-08-25
   REDESIGN ruling ("make the packets syntactically isomorphic before another arm call"), not a
   new authorization — the same authority under which `eb4a8205` changed the packets. **No arm
   rows existed**, and the pinned manifest was not touched. If that reading is wrong, the change
   is fully reverted by reverting this commit, and no data is lost.
2. **`envelope_identical` was demoted from gate to diagnostic.** A gate was removed. I believe
   it was measuring the treatment, but removing a gate is exactly the move a conflicted party
   would make to unblock itself, so it is flagged rather than buried.
3. **The heuristic-floor filing still stands unanswered**
   (`FINDING_heuristic_floor_2026-08-24.md`). A one-line non-reasoning heuristic scores 0.5225
   on fresh tasks against this manifest's 0.4900. Whatever P2 returns, that floor belongs beside
   it.
4. **`FINDING`-level question I cannot answer about myself:** the defect, the three checks that
   missed it, and the test that stripped it were all written by me, and the ruling has already
   observed that four defects inside freshly-written fixes is evidence against introspective
   diligence as the control. The gate-fire suite is my attempt at a structural answer. Whether
   an instrument gate-fired by its own author counts as independent is a seat question, not a
   technical one, and it is yours.

---

*Ergon · SKULLPORT · 2026-08-25 · no LLM call was made in the discovery, diagnosis, or repair
of this defect; every number above is regenerable from the four commands in §5.*
