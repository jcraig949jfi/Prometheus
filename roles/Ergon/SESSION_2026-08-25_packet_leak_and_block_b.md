# Ergon session record — 2026-08-25: the packet leak, block B, and P4's objective

**Executor** Ergon · **Host** SKULLPORT (M1) · **Model** claude-opus-5 · **Spend** $0
**Entry state** `d1ef3d93` · **Commits** `1f1998d3`, `b63c1407`, `21d5f2c7` (all pushed)
**For** James (HITL), Charon (kill authority), Harmonia B (independent seat), external review.

**Conflict of interest, up front.** Every action in this session either unblocked my own run or
built the instrument that will judge it. I am the driver, the author of the defects found, and
the author of their repairs. Said in writing here because the standing constraint requires it,
and because two of the three items below are exactly the moves a conflicted party would make.

---

## 0. One-paragraph summary

I was told to start P2 (run the factorial). I could not: the pre-flight check named in my own
bootstrap prompt was **failing, and had been failing since the day it was written** — the arm
packets carried two independent, perfectly-separating arm labels, which the REDESIGN ruling had
already declared fatal and prior to any further arm call. I fixed both labels structurally and
built the gate-fire suite that can prove the checks are capable of failing. The factorial itself
remains blocked on an independent seat (`RE_REVIEW_SIGNOFF`, Harmonia B), so I built the ungated
half of P2 instead — block B now collects itself unattended in both families under the
preregistered merge rule — and preregistered P4's objective, which must be fixed before its data
exists. Three defects in my own work were caught by the tests I wrote to catch them, and each is
recorded in the form that found it.

---

## 1. Verification before starting — and where the world disagreed with the handoff

Commands from the bootstrap prompt, run first:

```
python -m pytest ergon/probe/tests/ -q      187 passed   (resume said 182; it predates P1's tests)
python ergon/probe/task_controls.py         clean
PYTHONPATH=. python attacks/preflight.py    ADMISSIBLE
python ergon/probe/packet_invariants.py     FAIL — 200/200 — "arm identity is computationally AVAILABLE"
```

Three disagreements with the prompt, in descending order of consequence:

1. **`packet_invariants` was failing, and the committed ledger at `32e38d97` records the same
   200/200 FAIL.** This was never a regression. The check has never passed since it was written,
   and the campaign proceeded anyway.
2. **The factorial cells are wired into no collection phase.** They exist in `Arms.prompt`; the
   driver's P4 phase still enumerates the old six arms. "Run the factorial" was not a runnable
   instruction.
3. **The decisive arms are gated on `RE_REVIEW_SIGNOFF`**, which is absent. Owed by Harmonia B,
   and the prompt says not to do it myself.

### 1.1 A handoff claim with no artifact under it

The resume file §2 states shape isomorphism was *"verified template-generated on 480 packets."*
No artifact backs the number. No test, ledger, or document records a 480-packet isomorphism
verification; the only such test renders `manifest_rows[:40] × 6 arms = 240` — and it is the test
that strips the defect before matching (§2.3 below).

Per the resume's own closing instruction the artifacts win, and the disagreement is the finding:
**the strongest-sounding assurance in the handoff was the one with no rows beneath it.** ATK-015
exists for this shape of claim and did not fire, because the claim lived in a narrative document
rather than in a verdict ledger.

---

## 2. Finding 1 — the packets carried two perfect arm labels

Full filing: `ergon/probe/FINDING_packet_arm_labels_2026-08-25.md`.

### 2.1 The two labels

Measured on pinned block A (`e6b1e001`, n=200), all six residue-carrying arms:

**LABEL 1 — a lead line on 2 of 6 arms.** `campaign.py:579` prepended the literal
`"A prior attempt record:\n"` to `F-null` and `F-prom-retrieved` and to nothing else.

```
F-null            header 200/200        F-generic     header 0/200
F-prom-retrieved  header 200/200        F-hint        header 0/200
                                        F-null+hint   header 0/200
                                        F-prom+hint   header 0/200
```

400/400 separating. One `str.startswith` recovers the arm partition with zero error.

**LABEL 2 — a per-arm numeric band in the slug.**

```
F-null            [1..199]              F-generic     [40000..40199]
F-prom-retrieved  [0..199]              F-hint        [50000..50199]
                                        F-null+hint   [60000..60199]
                                        F-prom+hint   [70000..70199]
```

Six disjoint bands. One integer comparison recovers the **exact arm**, not merely the partition,
on every packet.

The ruling had already named this condition: *"If F-generic can be identified against
F-null/F-prom from packet shape alone, then the controller is not a controller. Make the packets
syntactically isomorphic before another arm call. That is prior to the 300-row question."*

### 2.2 Why three layers of checking did not see it

None of the three failures was carelessness. Each was a principled abstraction doing exactly what
it was designed to do.

1. **`envelope_shape` / `framing_skeleton` erase digits by construction.** Both map digit runs to
   `#` so shape can be compared independently of content. A label written in digits is invisible
   to them *in principle* — no amount of care with these functions could have caught LABEL 2.
2. **`matches_template` only sees the region it is handed.** LABEL 1 sat outside the template
   region, prepended by the caller after rendering.
3. **The isomorphism test deleted the defect before testing for it.**

### 2.3 The line that cost the day

```python
if a in ("F-null", "F-prom-retrieved"):
    payload = payload.split(chr(10), 1)[1]      # shared lead line
```

The comment asserts the line is shared. It was on two arms of six. The test removed the arm label
from the two arms carrying it and then certified the remainder isomorphic. The same test asserted
on the slug and split it on `-`, keeping only the pool token — discarding the digits that carried
LABEL 2.

**The generalisable failure:** every one of these checks had only ever been run against packets
believed to be clean. None had ever been shown capable of reporting a defect. A check that has
never failed is not evidence; it is an untested function whose return value happens to be `True`.

### 2.4 The repair — structural, not detective

- `packet_render.TEMPLATE` now **contains** the lead line, so the frame owns the packet's first
  byte and no caller can attach a per-arm prefix without editing the one file defining the
  shared shape.
- `synthetic_slug` no longer accepts a caller-chosen integer. It hashes into a caller-declared
  `span` (callers pass `MANIFEST_N`), so every arm's indices occupy the range real task ids
  occupy. Collision with a real id is the point. Producing a disjoint band now requires lying
  about the span rather than adding a number.
- `campaign.py` drops the prefix and the four offsets.

**New invariants** decompose a packet into its three template slots, each with an explicit
obligation:

| slot | obligation |
|---|---|
| frame | arm-invariant for free once conformance holds (INV 6a, full text, **no stripping**) |
| slug | no label in words (6b-i, pool token); none in digits (6b-ii, band separability) |
| items | **THE TREATMENT — exempt by design.** The factorial varies it on purpose. |
| sparsity | a property of the record, not the arm; arm-invariant per task (INV 6c) |

Naming *which* slot may differ is the entire content of the isomorphism claim. A check
forbidding all cross-arm difference would forbid the experiment.

`envelope_identical` was **demoted from gate to reported diagnostic** — it fires on the
item-count difference that *is* the treatment while staying blind to the digit band that is not.
Flagged for Charon in §6, because removing a gate is precisely what a conflicted party would do.

The band check is **population-scope on purpose**: on a single task each arm contributes one
index and there is nothing to be separable from. Pinned as its own test.

### 2.5 Length separability, reported not gated (BC-7)

Exit review #2 died on a token-length asymmetry, so the number ships beside the rows. It is not a
gate: the factorial gives the +hint cells more items, so a perfect length separator across the
hint columns is the treatment.

```
F-null           mean 459.5  [421, 540]     F-hint        mean 543.3  [541, 617]
F-prom-retrieved mean 459.2  [399, 552]     F-null+hint   mean 633.5  [595, 714]
F-generic        mean 472.3  [470, 546]     F-prom+hint   mean 633.2  [573, 726]
```

**The two contrasts P2 actually reads are both length-clean** — neither appears among the
perfectly-separable pairs:

- hint-absent column: `F-prom-retrieved` vs `F-null` — overlapping
- hint-present column: `F-prom+hint` vs `F-null+hint` — overlapping

All separable pairs are cross-column, i.e. the manipulated variable. Since the ruling forbids
differencing the cells and the reading is *within* the hint-present column, the asymmetry does
not touch the inference. Recorded so a later reader can check that rather than take it.

---

## 3. P2's ungated half — block B collects itself

The factorial is blocked on Harmonia B. Block B collection is not, so that is what was built.

**What P1 had left undone:** P1 built and pinned block B's manifest but wired it into nothing.
`_campaign()` read block A only and halted at R13 (194 < 300) every firing; the 30-minute
scheduler had been spending one probe call per firing to re-learn a fact already on disk.

**`ergon/probe/blocks.py` is a registry, not a second driver.** Block B re-points the ledger
paths and calls the **same** `p1` — one estimator, two populations. Forking the statistic that
decides the campaign is ATK-014's defect class exactly (a confirmatory estimator that agrees with
itself because it *is* itself).

**`merge_reading()` is the preregistered merge rule in code, and it can refuse.** When the
blocks' cross-family intervals do not overlap, pooling is `FORBIDDEN` and `n_pooled` is `None` —
deliberately, so a driver reading the number without reading the verdict beside it gets a
`TypeError` rather than a satisfied floor. That is the clause a party wanting its own floor met
would most want to soften, so it is gate-fired.

**The drip is block-aware too.** A cross-family screen is undefined on rows the second family
never saw, so block B contributes nothing without its own nemotron leg. Block A keeps its
original unprefixed ledger name so its 400 collected rows are not orphaned, and a test asserts
that the name the drip **writes** equals the name the screen **reads** — drift there would fill a
ledger nobody opens while the campaign halted every firing, and nothing would raise.

**Verified live, bounded on purpose rather than by launching a collection:**

```
campaign block B leg   4 rows · executor ergon · host SKULLPORT · status ok · latency 89s
drip block A           "complete" (no spend; its band read is finalized)
drip block B           "progress 2/440 (+2/2)" · real nemotron rows
block A pin            e6b1e001bf79e3ef INTACT · 415 prepass rows untouched
```

Collection now proceeds unattended on `PrometheusCampaign` (30 min) and
`PrometheusColdbandDrip`. Pooling stays `UNAVAILABLE` — correctly — until both legs of block B
are complete.

---

## 4. Three defects in my own work, found by the tests written to find them

Each is kept in the form that found it, with the reasoning attached.

**4.1 The greedy sparsity capture.** `template_conformance` does **not** catch a trailing
suffix: the sparsity slot is captured greedily to end-of-string — it must be, since the real
block is multi-line and varies per record — so anything appended is swallowed into that slot and
the packet still conforms. Tightening the pattern would make legitimate record variation look
like a defect. What closes the class is the slot obligation: a per-arm suffix makes the sparsity
slot differ by arm and INV 6c fails; an arm-invariant suffix is absorbed silently, which is
correct, because an arm-invariant suffix is not an arm label. **So the property is carried by
conformance AND 6c together, never conformance alone.**

This is the case for the generalized gate-fire rule as cheaply as it can be made: the rule found
a hole in a repair written by someone who had just spent an hour thinking about nothing else.

**4.2 The containment hole — 142 fabricated rows in a live ledger.** `block_dir()` first returned
a repo-absolute path. The dry-run test drives the whole campaign against a mocked lane with
`campaign.DIR` sandboxed; the block-B leg ignored the sandbox and wrote **142 synthetic
`executor: dryrun / host: TESTHOST` rows into the real block B prepass ledger.** Nothing was
spent and nothing was lost — the directory was untracked — but a later scheduled firing would
have computed block B's band read over invented rows. Quarantined as
`ergon/probe/ledgers/campaign_blockB.DRYRUN-POLLUTED-2026-08-25` rather than deleted.

**My own gate-fire suite proved block A was safe and never asked whether block B was.** A
containment test scoped to one of two directories is a containment test with a hole in it —
the same shape as the packet leak found hours earlier: *the check was pointed where the last
failure happened.*

Fixed by deriving every block path from the live `DIR` **by suffix**, which makes the sandbox
transitive. A second correction was needed: a fixed name under `DIR.parent` sandboxed the live
tree correctly but sent every dry-run to one shared `<temp>/campaign_blockB`, where consecutive
runs would inherit each other's rows.

**4.3 A silent halt.** The new R13 branch returned after logging only a progress line, so the
halt no longer carried a verdict. Caught by the dry-run's `"the halt must be recorded, not
silent"` assertion — the guard doing exactly its job. Every firing that ends there now logs
`R13-POWER-FLOOR-UNMET` with the block-B status beside it.

---

## 5. P4's objective, preregistered

Full document: `ergon/probe/PREREG_P4_neighbourhood_assay_2026-08-25.md`. P4's objective must be
**predetermined**, so writing it is the first real step of P4, not paperwork ahead of it.

**Grounded in the live schema, not memory.** Reading actual rejected records showed
`claim_payload` is a structured decision vector — `catalog/invariant/object` for both sides, plus
`relation` and `holds` — so the local intervention neighbourhood is literally "change one field",
executable by table lookup against 52 knots and 1,000 elliptic curves. `RELATIONS` is a 4-tuple
read from `a1_catalog_cross_product.py:49`. The design space is enumerable, so per the ruling's
seat-time order it is **compiled from source, not estimated from prose**. **No LLM appears
anywhere in P4** — not as solver, judge, or feature extractor.

Load-bearing design decisions, each fixed in advance:

- `Z` is named field-by-field from the real record, with the **intervened field masked** per
  candidate; unmasked, a predictor reads the answer off its own input.
- `generator_id` is **excluded** from `Z`: raw `kill_pattern` embeds it, and a predictor given
  both scores well by learning each stratum's modal answer.
- `step_trace` is excluded by prior measurement — a 0.551-bit structural zero, and `None` on
  inspection.
- The objective is a **continuous per-relation margin**, never the binary verdict flip (which is
  unanswerable for the majority of rows that stay false), and **never pooled across relations**:
  four scales on four populations is the naive-combination error.
- Q2's baseline is **not chance**. It is the best of random, the stratum's modal intervention,
  and a **magnitude-only** predictor — because a prior finding established this corpus's outcome
  largely measures magnitude compatibility, so if `Z` recovers only that it must read as a null.
- The held-out split is **by generator and by object, never by row**: a row split is what let 14
  memorised constants produce the h4 positive that was later retracted.
- Sampling is **stratified with the inventory enumerated first**; prefix sampling previously hid
  137 of 141 relations in this same corpus.
- Quotas set so `SE ≤ 0.02` **before** the 0.50 threshold is compared against it, and the
  attainable range checked so the gate can fire at all.

**Written down in advance because it is the flattering outcome:** the most likely `A*` is "swap
in an invariant of comparable magnitude", which would mean improving actions exist and are
**units arithmetic**. Recorded now so it cannot later be sold as a discovery.

**Four gate-fire worlds must pass before the first real record is read** — recording-broken,
generation-broken, navigable, and magnitude-only — including Charon's required positive control
and the world for the conclusion I least want to mis-report. Noted as necessary but **not
sufficient**: I wrote them too, so an independent implementation of the margin function is
requested.

---

## 6. For the kill authority — filed, not self-authorized

1. **The packet format changed again.** Judged to be *execution of* the 2026-08-25 REDESIGN
   ruling ("make the packets syntactically isomorphic before another arm call"), not new
   authorization — the same authority under which `eb4a8205` changed the packets. **No arm rows
   existed**, and the pinned manifest was not touched. If that reading is wrong, reverting
   `1f1998d3` reverts the change and loses no data.
2. **`envelope_identical` was demoted from gate to diagnostic.** A gate was removed. I believe it
   was measuring the treatment, but removing a gate is exactly the move a conflicted party makes
   to unblock itself, so it is flagged rather than buried.
3. **Block B now spends the free lane unattended.** ~880 calls across two families over roughly a
   day. Nothing is blocked on money, and the merge rule can still refuse to pool the result.
4. **The heuristic-floor filing remains unanswered**
   (`FINDING_heuristic_floor_2026-08-24.md`). A one-line non-reasoning heuristic scores 0.5225 on
   fresh tasks against this manifest's 0.4900 — the solver is below the trivial baseline.
   Whatever P2 eventually returns, that floor belongs stamped beside it.
5. **A question I cannot answer about myself.** The defect, the three checks that missed it, and
   the test that stripped it were all mine; so were the three defects in §4. The ruling has
   already observed that four defects inside freshly-written fixes is evidence against
   introspective diligence as the control. The gate-fire suites are my attempt at a structural
   answer. Whether an instrument gate-fired by its own author counts as independent is a seat
   question, not a technical one, and it is yours.

---

## 7. Verified state at end of session

```
python -m pytest ergon/probe/tests/ -q      217 passed   (187 at entry; +13 packet, +17 block)
python ergon/probe/packet_invariants.py     PASS — 200 tasks · 0 failures · 6 arms
                                            slug_bands_not_separable: true
PYTHONPATH=. python attacks/preflight.py    ADMISSIBLE
block A pin  e6b1e001bf79e3ef  INTACT       block B sha  7444a1789e98642d  INTACT
blockA prepass 415 · drip 400               blockB prepass 8 · drip 2   (collecting)
schedulers   PrometheusCampaign Ready · PrometheusColdbandDrip Ready
spend        $0
```

**Housekeeping, recorded rather than hidden.** I stopped the running campaign process once to
free a file handle git needed for a merge; `push_jobs` fsyncs every row, so it loses at most one
in-flight call, and the driver takes over a dead holder's lock on the next firing. A stale
`.git/index.lock` was removed after confirming no `git.exe` was running. One untracked file
belonging to Diomedes blocked a merge; it was byte-identical to the incoming tracked version and
was backed up before removal.

---

## 8. What the next Ergon should do

1. **Do not trust this file either.** Run the four verification commands in §7 first. Where this
   file and the artifacts disagree, the artifacts win.
2. **Do not run the factorial** until `RE_REVIEW_SIGNOFF` exists. It is Harmonia B's, not yours.
3. **Let block B collect.** Do not add a third block; the merge rule forbids it in writing.
4. **Build P4** to the committed preregistration. The four gate-fire worlds pass **before** the
   first real corpus record is read.
5. **P4's corpus results may not be interpreted before P3 reports.** P3 is a dose-response ladder
   on the arm apparatus; P4 is an assay on the corpus. Different questions, and an apparatus that
   fails its own dose-response invalidates whatever it says about history.
6. **Do not run another corpus entropy measurement.** The prohibition stands.

---

*Ergon · SKULLPORT · 2026-08-25 · $0 spent · no LLM call was made in the discovery, diagnosis, or
repair of any defect recorded here.*
