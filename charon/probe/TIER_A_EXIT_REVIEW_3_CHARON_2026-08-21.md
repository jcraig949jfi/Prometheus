# Tier-A Exit Review #3 — Charon (kill authority, M1)

**Charter authority:** `pivot/ROUND2_CHARTER_2026-08-20.md` R2-1 · **Prompt:**
`pivot/KICKOFF_PROMPT_exit_review_3_charon_2026-08-21.md` · **Executed:** 2026-08-23
**Cost:** $0 — local compute only, zero API calls.
**Independence:** no Harmonia B artifact dated after 2026-08-19 was read before this file was
committed. Harmonia B runs the same invariant on M2.

**Attack code:** `charon/probe/exit_review_3_attack.py` (mine, not the pipeline's)
**Evidence:** `charon/probe/exit_review_3_evidence_LIVE.json` (verdict-bearing, post-fix
pipeline) and `charon/probe/exit_review_3_evidence.json` (pre-fix, retained as the record of
the state the review opened against).
**Regenerate:** `ER3_STATES=live PYTHONPATH=. python charon/probe/exit_review_3_attack.py`

---

## VERDICT

**PASS, bounded — and the bound is the substance of this review.**

> *Treatment identity is computationally unavailable, after semantic content is removed, on the
> only arm pair where the invariant is a coherent test: `F-prom-retrieved` vs `F-null` — the
> pair the preregistration names as the center of gravity.*

Everywhere else the invariant is **not satisfiable by any implementation**, because on those
pairs the treatment *is* the presence or the size of a prepended block. I state that as a
finding about the invariant, not as a pass I am granting myself.

**No third defect class. The R2-1 stopping rule does not fire.** Reasoning in §5 — it is the
call I most expect to be argued with, so it is argued for at length rather than asserted.

**I do NOT create `RE_REVIEW_SIGNOFF`.** My PASS is one of the two it requires, and P4 is
blocked on other grounds anyway (§6).

---

## 1. Method — and why it is not the pipeline's own

The prompt requires a stripper I write; reusing `ergon.probe`'s redaction would test the
pipeline with the pipeline. Everything below is independent of `ergon/` except for calling it
to render the packets under attack. **`ergon/` was not modified by this review.**

Packets are rendered for all six decisive P4 arms across the full **n=620** campaign manifest —
generated, not described, per the prompt.

**Two strippers**, because "semantic content removed" has a defensible range and I would rather
report the range than pick a point on it and call it the answer:

- **STRICT** (verdict-bearing) — every alphanumeric run collapses to one class token. What
  survives: token counts, punctuation, line and blank-line structure, whitespace, field
  ordering, block position. What dies: word lengths, all lexical content.
- **SHAPE** (supplementary) — every alphanumeric *character* maps to its class, preserving run
  lengths. Strictly more information. A leak visible only here means fixed boilerplate is
  recoverable from its silhouette.

**Classifier:** logistic regression over char 1–4-grams of the stripped text (TF-IDF, 5k
features) **plus 21 explicit non-content numeric features** — length, token count, line and
blank-line counts, max/mean line length, block-break count and position, punctuation histogram,
capital count, whitespace mass, leading-whitespace, and JSON-framing indicators. 3-fold
**GroupKFold keyed on task uid**, so no task straddles the split.

**Two readings are reported and the stronger one governs.** The invariant says *unavailable*,
not *hard*. So alongside classifier accuracy I report `separable_exactly` — whether the sets of
stripped strings are disjoint. A perfect separator is a leak whatever a permutation null says.
The permutation null (10 refits) is computed where the observed accuracy is imperfect, which is
where a null is what decides the question.

### Positive control — mandatory, and it passed

Planted into a **copy**: one trailing space on one arm. Nothing else. A reader cannot see it.

```
POSITIVE CONTROL   observed 1.0000   separable_exactly TRUE   -> leak CAUGHT
```

The attack detects a one-character non-content leak at ceiling. **A meter without a positive
control is not a meter**; this one has one, and it works.

---

## 2. Results — live pipeline, n=620, all 15 arm pairs

```
pair                              STRICT            SHAPE           separable   verdict
F-prom-retrieved | F-null         0.5000            0.4979          NO          AT NULL
  perm-null mean 0.4829, 95% hi 0.5383, z=0.60      (SHAPE: 0.4912 / 0.5310 / z=0.33)
all 14 other pairs                1.0000            1.0000          YES         separable
POSITIVE CONTROL                  1.0000                            YES         caught
```

**The decisive pair sits on its permutation null in both strippers, and is not exactly
separable.** Per-task paired token deltas confirm it independently:

```
F-null - F-prom-retrieved, paired per task (count_tokens):  mean 0.02   sd 0.98   max|d| 4
```

Two arms matched to a **hundredth of a token on average, four tokens at worst, over 620
tasks.** `f_null.build_f_null` is doing real matched-null work. That is the single most
important number in this review and it is a credit to the construction.

### Per-arm size census (BC-7), live pipeline, n=620

```
arm                 count_tokens        word-runs      chars    ratio vs F-prom
F0                    80.2 +- 5.0        35.0 +- 0.0    212.2       0.404x
F-answer              89.2 +- 5.0        42.0 +- 0.0    252.2       0.449x
F-oracle             144.4 +- 16.5       83.0 +- 10.2   501.1       0.727x
F-generic            151.2 +- 9.9        94.7 +- 6.0    592.1       0.761x
F-null               198.7 +- 9.8        96.8 +- 3.6    650.0       1.000x
F-prom-retrieved     198.6 +- 9.8        96.8 +- 3.7    650.0       —
```

---

## 3. The bound: where the invariant is not a coherent test

Fourteen pairs separate at 1.000. Before calling that fourteen defects, ask what the treatment
*is* on each pair.

For 13 of them the treatment is **the presence, absence, or size of a prepended block**: `F0` is
the bare task; `F-answer` prepends one short sentence; `F-oracle` prepends a diagnosis; the
residue arms prepend a packet. An arm that adds text cannot be structurally indistinguishable
from one that does not. **No implementation can satisfy the invariant on those pairs**, so a
classifier reaching 1.000 there measures the experimental design, not a defect in it.

The preregistration already knows this and routes inference away from it: *"the center of
gravity is F-prom vs F-null and never F-prom vs F0."* The invariant is a coherent test exactly
where the arms are **matched by construction**, and there it holds.

**This is a defect in the invariant as written, not in the pipeline**, and the prompt invited me
to say so. A5 says "for every arm, compare … then train arm classifiers." Applied literally to
every pair it returns 14 unfixable failures and buries the one result that matters. The
operational form that survives contact with the pipeline is:

> **Among arms whose difference is intended to be semantic, treatment identity must be
> computationally unavailable after semantic content is removed.**

I recommend that wording to Harmonia B and to whoever writes exit review #4. It is strictly
narrower, it is testable, and it is the version that would have caught both prior kills —
serialization and token-length were both asymmetries *between arms meant to be matched.*

---

## 4. Two findings that are real, and are not passes

### 4a. `F-generic` is 24% shorter than `F-prom`, and the ruling that sized it is a fossil

`F-generic` carries the **`TOPIC-CONDITIONING`** matrix row (`F-prom ≈ F-null ≈ F-generic ≫ F0`)
— a comparison that carries inference. Measured on the live pipeline:

```
requested target = count_tokens(F-prom body)   114.4
produced by render_f_generic                    96.1     ratio 0.84x
whole-prompt ratio F-generic / F-prom                    ratio 0.761x
empty-packet fallback fired                     0 / 200
```

The R12 ruling in `campaign.py` sizes this arm on the premise that *"projected prom packets are
tiny (15–60 tokens) — below the pool's preamble floor — so exact matching returns UNDER-FLOOR"*,
and therefore ships the pool's smallest unit (~27 tokens). **That premise is now false.** Prom
bodies are ~114 tokens, the sizing machinery engages, the smallest-unit fallback never fires,
and the arm lands 16% under its own target and 24% under `F-prom`.

The ruling was calibrated against packets produced **while ATK-013 was live** — i.e. against the
degenerate pool. It is a measurement of a broken state carried forward as a rule. This is not a
`FAIL` of the invariant: BC-7 requires per-arm token means be *reported* so the size
relationship is "a number, not an assumption", and the number is above. But **the ruling should
be re-derived post-fix before P4**, and the 0.761× must be stamped on any `TOPIC-CONDITIONING`
verdict. Direction, per the standing question: a shorter `F-generic` biases *against* the
topic-conditioning explanation and therefore *toward* crediting residue — it flatters the arm
the program wants to be true. That is the direction that gets checked first.

### 4b. The two prior kills stay dead — with one regression not runnable

- **ATK-001 (arm-identifying serialization): HOLDS.** Zero of 1,200 rendered packets across all
  six arms open with `{` or `[`. The `assert not body.lstrip().startswith("{")` guard in
  `null_body` is live and the JSON-framing features in my classifier are constant-zero.
- **ATK-002 (token-length asymmetry), input side: HOLDS on the decisive pair** — 0.02 tokens
  mean paired delta (§2). Fails informationally on `F-generic` (§4a).
- **ATK-002, token-tercile DiD: NOT RUNNABLE, and I am recording that rather than skipping it.**
  A difference-in-differences on token terciles needs per-arm *outcomes*. No arm rows exist on
  the free-host pin — P2/P3/P4 have never run, the campaign is halted at P1. The regression is
  **owed at first arm data** and I am filing it as a standing debt, not as a completed check.
  A review that silently drops an unrunnable check reports better coverage than it has.

---

## 5. Why the stopping rule does not fire

R2-1: *a third distinct defect class means the design, not the plumbing, is the problem — stop,
do not patch, re-pose.* This review surfaced two serious problems. Neither is a third class.

**ATK-013 (writer/reader schema seam) was live when this review opened, and its realized blast
radius was worse than the registry recorded.** With the pool empty, `F-prom-retrieved` and
`F-null` rendered **byte-identical on 620/620 tasks** — the decisive contrast of the entire probe
comparing a packet with itself, `Δ_carry ≡ 0` by construction, reported as a bounded null. The
registry's "realized blast radius zero" was true only because P3 had not run. I have measured
what it becomes when it does, and the entry should carry that number.

It is nonetheless **not a new class**: ATK-013 was registered 2026-08-22 with an executable
probe, found by Techne from outside Ergon's lane. A known class recurring is a repair debt, not
evidence that the design is unsound. **It was repaired mid-review** by Techne (`c6736671`,
2026-08-23 02:43 EDT), and the repair closed two defects my own shim did not reproduce — a
filename-prefix routing proxy that would have shipped raw count-family prose into
`F-prom-retrieved`, and a gold screen sitting downstream of the rep filter. I re-ran the entire
attack against the live post-fix code; §2 is that run.

**The evidence-custody failure (§ATK-015, newly registered) is not a measurement confound.** It
destroyed the rows under two verdicts; it did not bias an arm. It is fully recovered and
verified (`ergon/probe/ledgers/RECOVERY_NOTE_charon_2026-08-23.md`, commit `cf45ac05`).

Both prior kills and the stopping rule concern **arm-identifying measurement confounds**. This
review found **none**. On the pair where such a confound would matter, the arms are matched to
0.02 tokens and sit on the permutation null. The honest reading is the opposite of "the design
is the problem": *the design's matched-null construction is sound, and its plumbing keeps
failing at file boundaries.*

**A process finding, recorded because it will recur.** The object under review changed while the
review was running: `assemble.py` was repaired at 02:43, between my first measurement and my
last. Nothing was lost — I detected it, traced it, and re-ran — but a review whose subject can
move mid-flight is a review whose verdict needs a commit hash on it. **This verdict is against
`c6736671`.** I recommend that exit reviews from here pin the SHA they certify, and that a
repair to code under active review be announced on the ledger before it lands.

---

## 6. Gates

1. **My exit review #3: PASS**, bounded as stated in the VERDICT and §3.
2. **`RE_REVIEW_SIGNOFF`: NOT CREATED.** It requires Harmonia B's independent #3 as well as
   mine. When hers is committed, the sign-off is a mechanical step and I will take it.
3. **P4 remains blocked independently of the sign-off**, on grounds outside this review:
   - the co-sign and its tightening (`charon/probe/RULINGS_2026-08-23.md` §4);
   - **no second family exists on the campaign manifest**, and Tier B's band is read
     cross-family post-screen (`RULINGS` §1). A campaign with one solver cannot execute a
     Tier B read at all.
4. **Owed before P4, assigned:** re-derive the `F-generic` sizing ruling post-fix (Ergon);
   run the token-tercile DiD at first arm data (me).

---

*Charon, M1, 2026-08-23. The pipeline's matched null is the best-built thing in this probe and
the review says so. Its file boundaries have now produced two of the three worst incidents in
the campaign's history, and both were invisible to every metric computed downstream — which is
the pattern worth carrying out of here.*
