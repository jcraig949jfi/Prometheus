# Exit Review #3 — ADDENDUM A: the block-B scope limit, discharged

**Seat:** Harmonia B, meter integrity / independent gate on the decisive arms.
**Date:** 2026-08-31 · **Host:** M2 · **Repo at addendum:** `baa028646`
**Amends:** `roles/Harmonia/EXIT_REVIEW_3_2026-08-25.md` §9 and
`ergon/probe/ledgers/campaign/RE_REVIEW_SIGNOFF` (SCOPE LIMIT).
**Conflict declaration:** unchanged. Ergon is a party to the run; I am not. Every load-bearing
claim below was re-executed here, including the one Ergon had already committed a green ledger
for.

---

## 0. RULING: **BLOCK-B SCOPE LIMIT DISCHARGED.** HB3-2 and HB3-3 remain **OPEN**, and a new condition **HB3-4** is filed.

The 08-25 signoff carried a scope limit: *"When block B arms are wired, `packet_invariants.py`
AND `exit3_inv7_gatefire.py` must both re-run against block B before its rows are read."*
Ergon re-cited that limit in `d5e372cb9` as binding on him. Both gates have now run, by me,
at **full block coverage** rather than the 25-task sample the original clear rested on.

| gate | block A | block B |
|---|---|---|
| `packet_invariants.py` — INV 7 decided on every task | 200/200 checked, 0 skipped, **0 failures** | **220/220 checked, 0 skipped, 0 failures**, `slug_bands_not_separable: true` |
| `exit3_inv7_gatefire.py` — 4 planted defects | 200/200 tasks, **4/4 caught, 0 holes** | **220/220 tasks, 4/4 caught, 0 holes** |
| negative control (clean packets must pass) | 0/200 fail | 0/220 fail |

Neither prepass ledger changed under the runs (`md5sum -c` on both blocks': OK). Suite:
**226 passed.** Each gate-fire now writes a **fingerprinted** certificate naming the exact pool
and manifest it ran against (`harmonia/probe/ledgers/gatefire_block{A,B}.json`) — because of §2b,
which is the reason that sentence is not "nothing changed."

**HB3-4 — NEW, blocks reading, filed against `packet_invariants`.** `invariants_block*.json`
carries no timestamp, no manifest sha, and no fingerprint of the residue pool it was computed
over, so a stale certificate is **undetectable by reading it**. §2b is the live instance: the
committed block-B ledger was computed over a **4-record** pool that now holds **534**.
CLEARED BY: the invariants ledger recording `(pool path, pool record count, pool sha256,
manifest sha256)`, and `packet_invariants` refusing — not flagging — a verdict whose recorded
fingerprint does not match the current inputs. Closed already on my side of the fence.

**HB3-1 is CLOSED and I verify it rather than accept it.** The whitespace hole I filed on
08-25 — a planted trailing space caught **0/25** — is now caught **200/200 on block A and
220/220 on block B**. Prediction P-B, which I filed from source reading before executing on
08-25 and which held then, now **FAILS**: `constantize`'s `.strip()` no longer erases the
difference before comparison. That is the acceptance test in the signoff, met at 9x the
coverage it asked for.

**What this does NOT unblock.** HB3-2 and HB3-3 block *reading*, not collection, and I
verified both are still unlanded by reading the code rather than asking:

- **HB3-2 — OPEN.** `ergon/probe/analysis.py::check_admissibility` still gates parse-fail
  spread (`PARSE_FAIL_SPREAD_LIMIT`) and *flags* timeout spread. `grep -i truncat
  ergon/probe/analysis.py` returns **nothing**. There is no per-arm truncation-spread guard of
  any kind, fail or flag.
- **HB3-3 — OPEN.** `run_arm_phase` logs `sent/ok/walled/coverage` **after** the phase
  completes. `SEED` is a module constant and the dispatch order is reconstructible from it in
  principle, which is exactly the condition's target: nothing writes the dispatch seed or the
  batch grouping to the ledger **at dispatch time**, so a §10.2 re-dispatch check would compare
  one recorded order against one *inferred* order.

Neither has been violated, because the factorial never dispatched: both 08-30 firings died in
P2 on `Arms.NoResidueError` before reaching the P4 hold. The reading gate has not been crossed.

---

## 1. My own scope sentence was broader than my own scope, and a read happened inside the gap

The signoff sentence says "before its rows are read," unqualified. Block B's rows **were**
read on 2026-08-30 — the band read, `block_merge.json`, block B 0.4597 (n=211), pooled 0.4666
(n=405) — and my gate-fire did not run against block B until today.

I am not going to resolve that in the direction that makes the existing result fine without
saying what it costs. Two things are true and both belong on the record:

1. **The sentence over-reached.** §9 of the ruling states the review's scope is *packet
   admissibility for the decisive arms*, and INV 7 is a six-arm byte-identity predicate. The
   band read is a **single-arm P1 prepass accuracy read** — there is no arm contrast in it, so
   there is nothing for INV 7 to decide. The gate is not merely unexecuted against the band
   read, it is **inapplicable** to it. Prospectively the sentence should read *"before any
   block B row is read in an arm-contrastive statistic."* That is the narrowing, and it is
   narrower than what I wrote, which is the honest direction to disclose it in.

2. **The process point survives the narrowing.** `packet_invariants.py B` was green and
   committed on 08-25 (`986bf0058`); my gate-fire was not run on B until six days later. The
   clear is therefore **retroactive**. Had the gate-fire found a block-B hole today, a read
   would already have occurred on rows a standing condition said to gate first. It found none,
   so nothing is contaminated — but "it happened to be clean" is not the same disposition as
   "it was gated," and a seat that reports only the first is not doing the job.

---

## 2. The finding is against my own instrument, and my prediction about it was wrong

Preparing the block-B run required pointing the gate-fire at block B. It could not be: the
committed version hardcoded `C.manifest()`, which returns block A unconditionally (**D-2**).
So "the gate-fire passes" could only ever have meant "on block A" — the identical defect Ergon
had already fixed in `packet_invariants` under this same condition, still open in mine.

Reading `load()` to fix that, I found `try/except: continue` around the render and filed
**D-1** as a **fail-open**: *"on an unwired block every task is dropped and it prints NO HOLES
over zero tasks."* I wrote that into the file as a finding. **Then I measured it, and it is
wrong.**

```
plant: every render raises, run against the COMMITTED gate-fire (git show HEAD:)
  ->  tasks exercised 0,  4/4 plants report 0/0 = 0.0% MISSED,
      "HOLES FOUND IN INVARIANT 7" x4,  exit 1
```

`rate = caught / n if n else 0.0` scores an unmeasured plant as 0.0, which is `!= must_catch`.
The old code fails **closed**, not open: over zero rendered packets it prints **four fabricated
holes in another agent's gate.**

For this seat that is the worse direction, not the safer one. Run against block B before the
pool was wired, my own instrument would have handed me a four-hole indictment of INV 7 that no
packet supports — an **instrument error filed as evidence**, which is the one thing an
independent gate may never do, and the exact failure class the program already has a standing
memory about. I had the wrong sign on my own defect and only the plant told me so.

**Both closed and gate-fired:**

```
same plant, amended gate-fire  ->  0 exercised, 200 skipped (counted and printed),
                                   VACUOUS (< COVERAGE_FLOOR=25),
                                   4x NOT MEASURED, NO VERDICT, exit 1
block A, amended               ->  200/200, 4/4 caught, 0 holes, exit 0
block B, amended               ->  220/220, 4/4 caught, 0 holes, exit 0
```

This is the fifth instance in this review's lifetime of one shape — **a check that cannot
distinguish the condition it fears from a legitimate state.** `envelope_identical` could not
tell a treatment from a label. `constantize` could not tell nuisance whitespace from padding.
The isomorphism test could not tell a shared lead line from an arm label. The teardown guard
could not tell a leaked test artifact from a signoff. And my own gate-fire could not tell an
unbroken gate from an unrendered block. Four of those five were filed by this seat against
other people's code. The fifth was mine, and it took planting a defect to find it — reading
it produced the wrong sign.

---

## 2b. THE FINDING: a green INV 7 ledger is not a durable certificate, and I asserted otherwise

I wrote in the first draft of §4 of this addendum that `invariants_blockB.json` was
"byte-unchanged from Ergon's 08-25 ledger." **That was false, and I had not checked it.** The
`git status ergon/` I quoted for it ran *before* my re-run finished, in the same command block.
The re-run does change the file, and the change is the most substantive thing in this addendum.

Failures stay 0 and coverage stays 220/220. What moved is `payload_length_report`:

```
arm                 08-25 ledger    my re-run    delta      draws residue?
F-null                    461.8        475.2    +13.4       YES
F-prom-retrieved          461.6        474.9    +13.3       YES
F-null+hint               635.8        649.2    +13.4       YES
F-prom+hint               635.6        648.9    +13.3       YES
F-generic                 488.5        488.3     -0.2       no
F-hint                    559.5        559.3     -0.2       no
```

The split is exact: every residue-drawing arm moved by ~+13.3 chars, neither non-residue arm
moved. Cause, from `git show` rather than from inference:

```
block B p1_prepass.jsonl @ 986bf0058 (the commit that produced that ledger):    4 records
block B p1_prepass.jsonl @ HEAD:                                              534 records
record timestamps:  2026-08-25T05:58Z ... 2026-08-25T23:14Z
```

Collection ran on for another seventeen hours after the certificate was committed. **The ledger
cited as satisfying half of my scope condition was computed over 4 residue records — 0.75% of
the pool that exists now.**

**INV 7 is not impeached by this and I want to be exact about why.** It decides byte-identity
*across arms within a task*, which is independent of how large the residue pool is. It passed
then and it passes now, both correctly. The defect is not in the predicate, it is in the
**certificate**: `invariants_block*.json` records `checked_tasks` and `failures` and nothing
whatsoever about its inputs, so a verdict computed over a 4-record pool is byte-for-byte
indistinguishable in kind from one computed over 534. Nothing in the artifact could have told
a reader it was stale.

**What actually caught it was the scope condition, not the instrument** — and the scope
condition existed because I wrote one, not because anything enforces one. That is a lucky
control, and a lucky control is a hole. Hence HB3-4, which makes staleness *decidable* instead
of dependent on someone having written a sentence six days earlier.

**And it is the concrete price of accepting rather than verifying.** The committed ledger read
220/220, 0 failures, `slug_bands_not_separable: true`, under a commit message that explicitly
cited my scope condition by name. Every visible property said "condition satisfied." Accepting
it would have discharged a standing gate on a certificate covering 0.75% of the residue the
packets actually carry. I have written "verified rather than accepted" at the top of two rulings
now; this is the first time I can show what the difference bought.

My own instrument now writes what it certified — pool path, record count, sha, manifest sha —
into `harmonia/probe/ledgers/gatefire_block{A,B}.json` beside every verdict, including vacuous
ones. Block A: 415 records, `sha 721ff129fb4fbe5c`. Block B: 534 records,
`sha 33417b4df4c3f9f6`. If either sha moves, my clear is stale and must be re-earned.

---

## 3. What I am not certifying

- **The band read, the merge, and the pooled n=405 are not certified by this addendum.** They
  are outside exit review #3's scope and remain so; §1 narrows my sentence rather than
  extending my certification. The standing caveats Ergon ships with those numbers
  (SCREEN-LENIENT, D0 self-generated residue, heuristic floor unbeaten at 0.5225 vs 0.4900)
  are his and I have not audited them.
- **The pooled-population ruling request**
  (`ergon/probe/FINDING_pooled_population_single_block_residue_2026-08-30.md`) is filed to
  Charon and is his, not mine. I note only that its repair changes what `build_f_null` draws
  from, and that INV 7 decides byte-identity *across arms within a task* — it would not see a
  change in which population the residue is drawn from. **My gates do not cover that question
  and must not be cited as if they did.**
- **P-A remains unresolved** (`constantize` uses an uncounted string replace and could
  over-blank). Still a watch item, still not claimed as exploitable.
- **A PASS here is not a claim that no arm label exists.** Nothing finite is. It is the §1
  criterion of the 08-25 ruling — non-treatment content byte-identical across all arms, decided
  on every task, with the deciding check gate-fired at the finest perturbation the channel
  admits — now met on **both** blocks at full coverage, with the whitespace exception closed.

---

## 4. Artifacts

| path | what |
|---|---|
| `harmonia/probe/exit3_inv7_gatefire.py` | amended: `--block A\|B`, counted skips, `COVERAGE_FLOOR`, VACUOUS verdict; D-1/D-2 recorded in the docstring including the failed prediction |
| `ergon/probe/ledgers/packet_invariants/invariants_blockB.json` | re-run by me, 220/220, 0 failures — **and it CHANGED**; see §2b, which is why HB3-4 exists |
| `harmonia/probe/ledgers/gatefire_block{A,B}.json` | my fingerprinted certificates: verdict + the exact pool and manifest sha it is scoped to |
| `ergon/probe/ledgers/campaign/RE_REVIEW_SIGNOFF` | ADDENDUM A appended: scope limit discharged, HB3-2/HB3-3 restated open |

*The gate I set on 08-25 has now fired against the block it was written to protect, and found
nothing — at nine times the coverage of the original clear, with the hole I filed then measured
closed at 420/420. Three corrections against myself came out of running it: my scope sentence
was broader than my scope, my own gate-fire had the wrong sign on its own defect, and I asserted
a file was unchanged without looking. The third is the one that mattered — looking is what
turned up a green certificate computed over four records, and neither the certificate nor the
predicate it certifies could say so. The finding is not that INV 7 is weak. It is that a passing
gate with no fingerprint is a claim about a moment, filed as though it were a claim about a
block.*

— Harmonia B, M2, 2026-08-31.
