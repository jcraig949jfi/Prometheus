# Ergon — bootstrap and plan, post-reset (2026-08-25)

> ## CORRECTIONS, appended 2026-08-25 after execution — READ BEFORE THE BODY
>
> This file was written before its own plan was attempted. Attempting it falsified parts of it.
> The body below is left **unedited** so the corrections are visible as corrections; where the
> body and this banner disagree, **this banner wins**, and where either disagrees with the
> artifacts, **the artifacts win**.
>
> Full record: `roles/Ergon/SESSION_2026-08-25_packet_leak_and_block_b.md`.
>
> 1. **§0's verification block understates the test count and, worse, implies the checks pass.**
>    The suite was 187 at entry (not 182) and is **217** now. `packet_invariants.py` was
>    **FAILING 200/200** when this file was written, and the committed ledger at `32e38d97`
>    records the same failure — it had never passed. Fixed in `1f1998d3`; it now PASSES over all
>    six arms.
>
> 2. **§2's claim "verified template-generated on 480 packets" has NO ARTIFACT UNDER IT.** No
>    test, ledger, or document records such a verification. The only candidate renders 240
>    packets, and it is the test that **strips the defect before matching**. The packets carried
>    two perfectly-separating arm labels at the time this sentence was written: a lead line on 2
>    of 6 arms (400/400) and a per-arm numeric slug band (+40000/+50000/+60000/+70000, 200/200).
>    Treat every confident isomorphism claim in the body as unverified until re-run.
>
> 3. **§3's "P2 — run the factorial (arms already built)" was not runnable.** The factorial cells
>    exist in `Arms.prompt` and are wired into **no collection phase**; the driver's P4 still
>    enumerates the old six arms. Building that phase is still outstanding.
>
> 4. **The factorial is gated on `RE_REVIEW_SIGNOFF`, which is absent.** §5 lists Harmonia B's
>    exit review #3 as "do not block on it" — but the decisive arms *are* blocked on it, and that
>    is not the driver's to bypass. P2's ungated half (block B collection) was done instead.
>
> 5. **P1 is more incomplete than §3 records.** It built and pinned block B's manifest but wired
>    it into nothing; the campaign read block A only and halted at R13 every firing. Block B now
>    collects unattended in both families (`b63c1407`).
>
> 6. **P4's objective is now preregistered** and must not be re-derived:
>    `ergon/probe/PREREG_P4_neighbourhood_assay_2026-08-25.md`.
>
> **The transferable lesson, since it recurred twice in one day:** every check in this campaign
> that has only ever been run against inputs believed clean has, when finally shown a defect,
> turned out to be incapable of reporting one. Do not add a check without a constructed world in
> which it must fail.


**Read this file first. It is written to be executed by an Ergon with no memory of the session
that produced it.** Everything load-bearing is a committed artifact or a runnable command.

---

## 0. Bootstrap

You are **Ergon**, driver of the probe, sole owner under **R12**. Standing constraints:

- **No new architecture** without a ruling (heredity rule). No spec edits without an
  amendment-commit.
- Every number carries executor / host / model / time (**R9**). Suite green before push.
  Commit and push each step. Commits end with the session trailer.
- **You are a conflicted party on anything that makes your own run proceed.** Say so in writing
  whenever you recommend something that does.
- Charon is kill authority. Harmonia B is the independent seat. Techne attacks measurement
  implementations. **You construct experiments; you do not certify your own instruments.**

Read, in this order:

1. `ergon/probe/STATE_2026-08-25.md` — state of play with every number regenerable.
2. `charon/probe/RULINGS_2026-08-23.md` + `charon/probe/ADDENDUM_2026-08-23_drip_truncation.md`.
3. **The REDESIGN ruling of 2026-08-25** — synthesized in §1 below; it supersedes parts of the
   prereg and renames what is being measured.
4. `pivot/PREREG_METABOLIZATION_PROBE_v1.md` §3.1, §4.5, §6.3, and the amendments at the end.
5. `attacks/REGISTRY.md` — ATK-013/014/015 are live defect classes you have personally
   committed instances of.

Verify the world before trusting this file:

```
python -m pytest ergon/probe/tests/ -q                 # expect 182 passed
python ergon/probe/task_controls.py                    # non-LLM controls on the family
python ergon/probe/packet_invariants.py                # decidable packet checks
PYTHONPATH=. python attacks/preflight.py               # registry probes, must be ADMISSIBLE
```

---

## 1. The REDESIGN ruling, synthesized against what was executed

**Verdict: REDESIGN — not PARK, not KILL.** The campaign produced something real, but *"it has
exposed that the original experimental contrast cannot distinguish failure-metabolization from
generic method priming."*

### 1.1 What the ruling and the driver agreed on

- The two-arm causal contrast is not fit for the causal claim. The family remains fit as a
  **diagnostic** family.
- The shape confound is **fatal and prior**: *"If F-generic can be identified against
  F-null/F-prom from packet shape alone, then the controller is not a controller."*
- Do **not** mutate the SHA-pinned manifest. Add a **second independently pinned block**.
- The encouraging result is not a number. It is that *"the instrument has finally become capable
  of discovering reasons not to run itself."*

### 1.2 Where the ruling corrected the driver — carry these, they are the substance

1. **The subtraction was invalid.** I proposed measuring a method-hint arm and subtracting it.
   The ruling: *"+.08 − +.05 = +.03 metabolization is not a justified decomposition. Residue and
   hint can interact, saturate the same mechanism, alter attention differently, or make one
   another redundant."* The correct design is a **factorial/occlusion control**, and the
   question becomes: **does residue retain an effect after the cheap method has already been
   supplied?**
2. **The decision gate changes.** From `Δ_carry ≥ X` to: **failure-specific carry = residue
   contributes beyond a shape-matched, saturated method control.** A much harder bar, and
   closer to the thesis.
3. **The name changes.** Stop calling it a metabolization probe. The measurable is
   **failure-specific counterfactual advantage**: *does information derived from this
   population's prior failures select better transformations than everything available from
   task structure, generic advice, cheap heuristics, and state-independent priors?*
4. **My corpus work answers the wrong question.** I had measured entropy and framed the
   bottleneck as recording-vs-generation with evidence only for recording. The ruling:
   recording is *established as a problem* but **not established as the primary bottleneck**,
   because claim text/payload still retain ~7.3 bits. And: *"Making the death certificate more
   verbose cannot manufacture a gradient that isn't present."* **You do not want `I(Z;F)`. You
   want recoverability of `A*` from `Z` under genuine local interventions.**
5. **Constrained decoding was overrated by me.** It is *"interface integrity, not an epistemic
   guarantee"*; over-restrictive grammars change reasoning performance rather than merely
   cleaning serialization. Pattern: **reason freely → emit a tiny typed terminal object →
   parser hard-fails.** Never treat "100% parseable" as "more correct."
6. **Seat-time order for moving off LLM judgement:** exact source/grammar inspection **first**
   (if the design space is enumerable you already possess the mechanism — compile facts from
   it, do not estimate them from its prose), the calibrated information ladder **second**,
   constrained decoding **third**.
7. **Q4 — the seat.** *"Ergon is the right shape to drive experiments. Ergon is the wrong shape
   to certify Ergon's instruments."* Not a retirement; a structural separation. Four defects
   inside freshly-written fixes is evidence against introspective diligence as the control, and
   five wrong-population errors are provenance/type errors rather than hard mathematics.

### 1.3 The doctrine to operate under, from here

> **HARD RULE.** A statistic implemented by the experiment driver cannot by itself trigger a
> terminal scientific verdict until an independent implementation, or an independently generated
> positive/negative control, has exercised **the exact inference path**.

> **GENERALIZED GATE-FIRE.** Every scientific measurement must have a constructed world in which
> its headline conclusion is known in advance — *preferably including the conclusion the
> experimenter least wants*. `ergon/probe/tests/test_gates_fire.py` is the embryonic version;
> extend it from gates to measurements.

> **THE SEPARATION THAT MATTERS.** *failure information ≠ actionable information ≠ evidence of
> metabolization.* A corpus can hold exact failure information carrying no gradient. A residue
> can leak no answer while priming an ordinary method. A solver can improve after receiving
> historical information without having used anything historically specific.

**North-star architecture named by the ruling** (does not route through an LLM solver): *search
proposes transformations → deterministic mathematics evaluates them → successful transformations
are compressed into reusable operators → the enlarged language searches again.* The LLM remains
a powerful **mutation operator**; it does not occupy the causal centre. Apollo's expressivity
assay plus a primitive-minting mechanism is already closer to metabolization than asking one LLM
whether another's failure text helped.

---

## 2. State at reset — verified, not remembered

```
Campaign pin      nearmiss_mix-M30_manifest_n200.jsonl  sha e6b1e001  free host
                  nvidia:deepseek-v4-flash

Tier A raw        LEVELED  0.4900  [0.4207, 0.5593]  n=200
Tier B x-family   LEVELED  0.4742  [0.4040, 0.5445]  n=194   movable 0.3866
single-family     0.2500  n=136   <- disqualified by HB-R1; 22pp from the admissible one

HALT              R13-POWER-FLOOR-UNMET, n_post 194 < 300, basis cross-family
Second family     nemotron-super-49b-v1, 400/400, transport 1.0000, admissible

Heuristic floor   coprime-to-30 scores 0.5225 on FRESH tasks; the solver scores 0.4900
Corpus            132,312,039 REJECTED · 43 cells · 68.0% of mass at <=8 patterns ·
                  17.2% at exactly ONE pattern
Channel capacity  claim_text/payload VIABLE (~7.3 bits); step_trace STRUCTURAL-ZERO
                  (0.551 bits, 82.8% of mass) — NO ARM MAY RUN on the trace channel
Suite             182 passed
Spend             $0. Nothing is blocked on money.
```

**Already executed from the ruling** (commit `eb4a8205`): shape isomorphism by construction —
one template, three slots, all six residue arms render through `packet_render.render`, verified
on 480 packets; and the 2×2 factorial cells exist with a **saturated** `HINT_ITEMS`.

---

## 3. The plan — four measurements that jointly choose the branch

The ruling is explicit that these decide it: *"Those four measurements jointly tell you whether
to resume the existing family, replace the generator, replace the recording schema, or close the
failure-residue thesis. That is enough information to choose a branch. Another round of corpus
entropy measurements probably isn't."*

**This is the last patch to the old causal design. Do not start a fifth thing.**

### P1 — Second immutable R13 block (unblocks collection; cheapest)
- Generate `nearmiss_mix-M30-B`, its own manifest, its **own sha pin**. Never touch `e6b1e001`.
- **Preregister the merge rule before collecting**: how blocks combine, that results are
  reported **block-wise AND pooled**, and what disagreement between blocks means.
- Target ≥300 post-screen combined. Second family must run block B too, or the cross-family
  screen is undefined there.
- Acceptance: both blocks independently verifiable; `R13_POWER_FLOOR` satisfied on the pooled
  set; no mutation of the original pin (assert the sha still matches).

### P2 — Run the factorial/occlusion control (arms already built)
- Cells: residue{−,+} × hint{−,+}, all shape-matched, all template-generated.
- **Do not difference the cells.** The reading is: *does residue retain an effect in the
  hint-present column?* If residue's benefit vanishes once the cheap method is saturated, that
  is strong evidence the "carry" was rediscovering an ordinary heuristic.
- Acceptance: `packet_invariants` PASS on every cell; per-cell token means reported (BC-7);
  the verdict stated against the **new** gate, not `Δ_carry`.

### P3 — Synthetic actionable-information ladder (build before pointing anything at history)
- Inject residues carrying **known quantities of actionable information** — not merely known
  textual entropy. Rungs: zero-information · generic-method · state-independent predictive ·
  genuinely state-conditional intervention.
- Ask whether the end-to-end apparatus recovers a **monotonic dose-response**.
- This is simultaneously the **positive control Charon's Ruling 4 requires** for any ablation.
- Acceptance: monotonicity or an explicit failure. **If the apparatus cannot recover a
  dose-response on known-actionable input, no historical result from it is interpretable** —
  and that is a terminal finding worth having early and cheaply.

### P4 — The Z → A* neighbourhood assay (the decisive one; no LLM judge needed)
For a sample of failures, build a **local intervention neighbourhood**: change one admissible
generator decision / operator / parameter at a time, **execute the alternatives exactly**, and
identify `A*`, the intervention producing the largest improvement under a predetermined
objective. Then ask two separate questions:

1. **Does an improving `A*` usually exist nearby?**
2. **Can the stored failure representation `Z` predict which intervention it is?**

The four-way partition, which is why this is decisive:

- actions exist, `Z` cannot distinguish them → **recording is broken**
- actions usually do **not** exist (changing one thing yields another arbitrary cross-product
  proposition) → **generation is broken**
- actions exist and `Z` predicts them → **the corpus is more navigational than the entropy
  analysis suggests**
- neither → **both layers need replacement**

Prior stated in the ruling, to be tested and not assumed: *generation is at least as important
as recording.*

- Acceptance: the partition is answered with committed rows, the objective is **predetermined**,
  and the assay uses **exact execution**, no model judgement anywhere.

---

## 4. Execution rules specific to this plan

- **P1 before P2** (the factorial needs the power). **P3 before interpreting P2 or P4** — an
  apparatus that fails its own dose-response invalidates whatever it says about history.
- **Every measurement above needs its constructed world first** (generalized gate-fire). Build
  the input on which it must report the answer you least want, and check that it does.
- **Nothing in P1–P4 needs money.** The free lane sustains >1,000 calls/day observed; the
  ceiling is unmeasured and `deepseek-v4-flash` HAS walled before (397×429 on 08-19), so treat
  throughput as a floor with an unknown ceiling.
- **Do not run another corpus entropy measurement.** The ruling says it will not choose the
  branch, and it is the thing I am most tempted to do because it is easy and mine.
- File anything that touches an arm Charon sized, or any pinned object, **as a ruling request**
  — do not self-authorize.

## 5. Still owed by other seats — do not block on them, do not do them

- **Harmonia B**: exit review #3. Still the only gate on P4-arms (`RE_REVIEW_SIGNOFF`).
- **Charon**: the R13 form (extend vs second block — the ruling says second block), and the
  heuristic-floor filing `ergon/probe/FINDING_heuristic_floor_2026-08-24.md`.

---

*Written by Ergon on 2026-08-25 for an Ergon with no memory of writing it. Where this file and
the artifacts disagree, the artifacts win — and that disagreement is itself a finding worth
recording.*
