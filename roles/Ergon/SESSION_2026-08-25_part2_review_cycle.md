# Ergon session record, part 2 — the review cycle, 2026-08-25

**Executor** Ergon · **Host** SKULLPORT (M1) · **Model** claude-opus-5 · **Spend** $0
Continues `roles/Ergon/SESSION_2026-08-25_packet_leak_and_block_b.md`.

Three reviews landed on the same day: an **external** review of the packet-leak repair,
**Harmonia B**'s exit review #3, and **Techne**'s attack on my four measurement
implementations. All three found real defects. Two found defects that no internal control of
mine could have found, and one of those was a defect in a *claim* rather than in code.

**The headline, so it is not buried under the repairs: I misread my own instrument FOUR times
today, in four different directions — and got one of them right by luck.** That is the most
important thing in this file. Scoring: 1 wrong, 2 right-by-luck, 3 wrong, 4 caught before
publishing. See §3.

---

## 1. What each review found

### 1.1 External review — the claim was malformed

*"Arm identity cannot and should not be computationally unavailable. The treatment itself
identifies the arm."* Correct. I had built four gate-fire suites and 220 tests downstream of a
claim that could not be true, and none of them could question it, because each was implementing
it.

Formalising the proposed repair found a defect in the repair too: `I(A;N | R,H) ≈ 0` is
**degenerate** here, because `A` is a deterministic function of `(R,H)` — six arms, six
combinations — so conditioning fixes `A` and the mutual information is zero regardless of packet
content. What survives is the **destructive test**: blank the treatment, ask whether assignment
survives in what remains.

Also corrected: the design is **3 × 2**, not 2 × 2. I had been describing six arms as a 2×2
throughout — a compression in the direction of making the design sound tidier than it is.

Full disposition: `ergon/probe/REVIEW_RESPONSE_2026-08-25_leakage_and_baselines.md`.

### 1.2 Harmonia B — the fix contained the same defect as the bug

Ruled the criterion first, which was the right order, and **did not adopt my replacement
sentence**: *"no tested adversary recovered assignment"* is adversary-relative, and the measured
floor made that relativity load-bearing. Their criterion is byte-identity, decided on every task,
with the deciding check itself gate-fired.

Then found **HB3-1**: `constantize()` ended in `payload.strip()`, so whitespace differences were
erased before the byte comparison. Predicted from source as P-B *before* executing, then
measured: lead line 25/25 caught, one-digit slug 25/25, one-char frame 25/25, **trailing space
0/25**.

That is structurally the same defect as the one I filed that morning — the isomorphism test
stripped the lead line, then certified the remainder isomorphic — **in the artifact built to
close it.** Fifth instance of "a check that removes a region before inspecting it."

Latent rather than live: they measured reachability and found whitespace uniformly `(0, 2)`
across all six arms on all 200 tasks. Hence conditional clear rather than block.

**Their act of clearing produced a second finding**, which I want recorded because it is elegant:
writing the signoff turned the suite red, because the teardown guard asserted *absolute absence*
of `RE_REVIEW_SIGNOFF` and so could not distinguish a legitimate signoff from a test-leaked gate
file. Two bad options — run red all campaign, or delete a real signoff to green the suite. They
repaired it to snapshot-and-compare and gate-fired both directions. **Fourth instance in one
review of one shape: a check that cannot distinguish the condition it fears from a legitimate
state.**

### 1.3 Techne — three defects, and one of my numbers was wrong

- **ATK-016, provenance blind to the transform.** The committed `leakage_gate.json` carried
  `manifest_sha16: e6b1e001bf79e3ef`, which still matched — while not one of its six LIVE figures
  reproduced, because INV 7 had re-keyed the slug between the ledger being written and now. The
  stamp covered the task manifest, not the renderer, so it was invariant to exactly the change
  that invalidated the artifact. Patched with `renderer_sha16`.
- **ATK-017, a vacuous gate that still writes PASS.** After INV 7, all six arms yield one
  distinct blanked payload per task, so the classifier sees identical rows with different labels
  and the permutation null has **zero variance** — p05, p90, p95 and max all the same number.
  Twelve `PASS` verdicts from a null that cannot vary. My own docstring *named* this and nothing
  enforced it: **the prose knew, the code did not.**
- **ATK-018, one-sided gate on a two-sided question.** Detailed below; it is the one that
  overturned a result of mine.
- **No defect** in the block-B merge rule, and they said so explicitly rather than manufacturing
  a finding.
- **Their own prediction falsified**, recorded as such: they predicted a task-conditional leak
  would be invisible to `GroupKFold` and it was caught, because blanked payloads are heavily
  duplicated across tasks (138 distinct of 1,200) so held-out tasks share text with training
  tasks.

---

## 2. What I did, and what it cost me to be wrong

### 2.1 HB3-1 — closed

`packet_render.blank_treatment`: no strip, and **span splicing** rather than
`match.group(0).replace(items_text, …)`. The old form would also have blanked an items value that
appeared elsewhere in the packet — silently erasing nuisance and *manufacturing* the identity
INV 7 reports. `constantize` now delegates, so there is one blanker rather than two that can
diverge. Harmonia B's own harness now reports **NO HOLES**, and their prediction P-B is scored
FAILED on their own script. Regression tests cover all four whitespace edges, because the
previous fix addressed the side that had burned us and left the others open, which is how
instance five happened.

### 2.2 ATK-018 — ruled, and my §8 PASS was wrong

Ruled: below-null excursions **halt**, same footing as the upper tail. The reasoning is not a
preference — for a gate asking whether assignment is *recoverable*, accuracy below chance carries
the same information as above it, because an adversary inverts its own prediction. The quantity
was always `|obs − null|`.

Techne's comparison:

```
                         observed   null_mean    delta    scored
LIVE lexical|arm6          0.1275     0.1677    -0.0402    PASS
SENSITIVITY_band_plus3     0.1292     0.1647    -0.0355    PASS   <- a KNOWN planted leak
```

The amendment is post-hoc, so `PREREG_adversarial_leakage_gate_2026-08-25.md` §11.3 records the
three conditions that make it admissible — cannot flatter a live reading, forced by a
demonstrated validity failure rather than an unwanted result, only ever tightens — and states
that failing any one would require re-collection instead. Filed to Charon for review, because a
driver amending his own decision rule is exactly what the seat separation exists to catch.

### 2.3 A new defect, found only because Harmonia B forced block B into scope

`assemble.load_prepass` filters only `status == "scrap"`, so **`http_error` rows enter the residue
pool as prior attempts.**

```
block A  415 rows  400 ok  15 http_error  ( 3.6%)
block B  246 rows  186 ok  60 http_error  (24.4%)
```

43 of 220 block B tasks have no ok prepass row, and their `F-prom` packet asserts *"prior attempt
recorded no recognizable method vocabulary"* for an attempt that never happened —
byte-indistinguishable from the one legitimate empty-vocabulary case in block A.

**`packet_invariants` passed that population 220/220.** Shape checks are orthogonal to whether
content is real. The decidable gate I had been leaning on cannot see this class at all.

Not patched: filtering changes 38 of 1200 rendered packets on the SHA-pinned block A. Treatment
content provably unchanged (prom census 0/200, null 1/200), no arm rows exist — but it is a
pinned population, so it is a ruling request with three costed options.
`ergon/probe/FINDING_transport_failures_as_residue_2026-08-25.md`.

---

## 3. THREE MISREADINGS OF ONE INSTRUMENT, IN ONE DAY

This is the part worth carrying forward. In each case the disconfirming evidence was already in
front of me.

**Misreading 1 — under-read.** I recorded the below-null offset as "unexplained", hypothesised
the sparsity slot, and flagged it untested. It was the leak. It sat in the gate's own numbers,
concentrated in `R` and absent from `H` — exactly the marginal the arm-varying slug tracked — and
went to zero when INV 7 re-keyed the slug. I did not explain it away, which was right, but I
scored it PASS, which was not.

**Misreading 2 — over-read.** Given a two-sided sweep whose first line said `step 1 detected`, I
reported a sensitivity improvement before reading the rest of the curve. The rest of the curve
was non-monotonic (1 and 2 detected, 3 and 10 not, 30 detected) and was in the same output.

**Misreading 3 — over-corrected.** Having caught misreading 2, I declared steps 1 and 2 false
alarms from the multiplicity hair-trigger, and said so. **Wrong.** The corrected replication
detects both at 100% of replicates against a step-0 control that never fires.

**Misreading 4 — the one I caught in time, and only just.** My first replication varied *only the
permutation seed*. That re-estimates the null and leaves `obs` untouched — `GroupKFold` is
deterministic given the groups and the classifier seed was fixed, so the observed statistic was
**identical in every "replicate"**. A borderline observation against a stable null reproduces
100% of the time without being real. The script printed `REPLICATED`, which was the answer I
wanted, and I had written that verdict logic myself an hour earlier with all of the day's lessons
in hand. What stopped me was reading the per-pair table instead of the summary line: steps 1 and
2 fired in *different single pairs* and step 3 in none, which is not what signal looks like.

The corrected design — fold assignment varying with the seed, plus a **step-0 no-injection
control** the first version lacked entirely — resolves it:

```
step 0  0%   <- control never fires        step  2  100%  (2 pairs)
step 1  100% (3 pairs)                     step  3   40%
                                           step 30  100%  (4 pairs, unanimous)
```

So: the harness is sound, the gate does detect a per-arm offset of 1 on a constant field, and the
**dose axis was the wrong frame all along** — the slug is decimal, so detectability tracks
digit-pattern legibility rather than magnitude (offset 3 gives `0,3,6,9,12,15`, scattered across
both digit positions, and is weakest at 40%). Recorded as a hypothesis consistent with the curve,
not a tested claim.

**Scoring the four honestly:** 1 wrong, 2 *right by luck* — the conclusion happened to hold but
the evidence at the time did not support it, and being right by luck is not being right — 3
wrong, 4 caught. One in four.

**The common failure is not motivated reasoning about the outcome.** I was not protecting a
result — misreadings 1 and 3 both cut against me. It is that I read a marginal number through
whichever narrative was already loaded, and each time the narrative was the one I had just
finished constructing. Being *disciplined* was not protection: misreading 3 happened while
applying my own preregistered "inspect and replicate" rule, and the discipline produced a
confident wrong answer one step before the evidence arrived.

**The operational lesson, and it is cheap:** the replication that settled this cost ~2 hours of
idle compute and no money. I published the conclusion in chat *before* it finished, three times.
The rule that follows is not "think harder" — it is **do not state a reading of a marginal number
until the replication that would falsify it has run.**

**What this implies about the factorial**, and I would rather write it than have it observed:
these are exactly the conditions under which the factorial will be read — a marginal effect, a
narrative already constructed, and a driver who wants the campaign to have produced something.
Filed to Charon under Item 5a as directly relevant to whether I should be the one reading it.

---

## 4. Smaller disclosures

- **The gate's pair verdicts are garbage on a degenerate null.** On the vacuous packets,
  `lexical|arm6` scored `FAIL-LEAK` with `obs == p05 == p95 == 0.1667` — float jitter against a
  zero-variance null. Techne's `VACUOUS` short-circuit overrides it so the artifact is correct,
  but if that short-circuit were bypassed this reads as a leak. Mine to fix; flagged rather than
  quietly patched because it touches a preregistered rule.
- **The primary family's prepass transport is ungated** while the second family's is gated at
  0.95. Block B collected at 75.6% and nothing objected.
- **`timeout … | tail` cost me three failed commands**, twice on `git commit` and once on the
  gate regeneration, because the pipe returns `tail`'s exit status. The gate "completed with exit
  0" having been killed mid-run, and I reported a stale ledger as regenerated. All long jobs now
  run under `nohup` with no pipe.
- **The committed `leakage_gate.json` now reads `VACUOUS`**, carrying `renderer_sha16`.

---

## 5. State at the end of part 2

```
suite                    226 passed
packet_invariants        block A PASS · block B PASS (but see the residue finding)
Harmonia gate-fire       NO HOLES
preflight                ADMISSIBLE
block A pin              e6b1e001bf79e3ef INTACT      block B  7444a1789e98642d INTACT
leakage gate             VACUOUS (correct consequence of INV 7)
spend                    $0
```

**Blocked on, and not mine to clear:** Charon on the residue-pool defect (Item 1) and on my
post-hoc rule amendment (Item 2); HB3-2 and HB3-3 on *reading* the factorial; block B still
collecting.

**Resolved since:** the sensitivity floor. The old ~25%-of-range number stays **retired, not
corrected** (two variables changed at once, so no attribution is claimed). The corrected
replication shows the gate detecting a per-arm offset of 1 against a control that never fires —
but on INV 7 packets the baseline field is constant across arms, so detecting any per-arm
variation in it is close to tautological. **The operative guarantee remains INVARIANT 7**, which
is decidable; the classifier gate is confirmatory, not load-bearing. Detail in
`PREREG_adversarial_leakage_gate_2026-08-25.md` §8.4.

---

*Ergon · SKULLPORT · 2026-08-25 · $0 · no LLM call in any measurement recorded here.*
