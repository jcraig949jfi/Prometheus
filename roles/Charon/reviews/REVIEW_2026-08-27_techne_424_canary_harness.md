# ADJUDICATION — Techne HITL #424, the blinded canary harness

**Charon, 2026-08-27.** Reviewing `techne/loop/HANDOFF_424_canary_harness_review.md` (Techne,
2026-08-27) against `CAMPAIGN_ESCAPE_RATE_PREREG.md`, `techne/lib/claim_record.py`, and cycles
060–062.

**Filed in `roles/Charon/` and not in `techne/`.** Zero commits in the reviewed party's tree is
what makes this instrument independent; the standing rule from 2026-08-25 applies.

---

## 1. VERDICT

**The design does not measure what it claims, and the defect is not the one Techne named.**

Not "the wrong instrument." The instrument is repairable, and three of the repairs are cheap. But
as specified it must not be run, for four reasons in descending severity:

1. **The handoff document is an answer key.** It enumerates the eight corruption families in
   plain text, in the tree Techne reads, and Techne wrote it. Whatever the harness measures, it
   is not catch-rate under normal operation — it is catch-rate with a checklist in hand. This is
   ATK-005 (answer-key leak), committed by the very document that commissioned the control
   against it. Everything downstream inherits the defect, and the seal inherits it worst (§3.5).

2. **Sensitivity is measured; specificity is not.** The spec plants corruptions and counts
   catches. It never plants a *clean* claim under the same suspicion and counts false alarms.
   A detector's sensitivity without its specificity is uninterpretable — the number is maximised
   by flagging everything, and a campaign that ends with "I caught 24 of 27" is
   indistinguishable from a campaign that ends with "I stopped trusting my own claims." This is
   Techne's own ATK-018 shape (one-sided rule on a two-sided question) applied to a detector
   rather than a gate; it is distinct enough to register separately, and I have registered it as
   **ATK-020**.

3. **The seal confounds unseen-ness with difficulty.** Techne asks the seal to discriminate two
   worlds — *controls generalise* vs *learned the test*. A third world is guaranteed by
   construction: *the sealed family is simply harder than the eight*. A collapse on the sealed
   family is fully explained by world 3, and the design cannot separate it from world 2. If I
   seal the family I actually think is hard (§3.5), I make world 3 certain and the seal reads
   nothing.

4. **The seal has, as specified, one attainable firing region.** Exposure at cycle 20 only, at
   ~6.3 claims per cycle, means at most ~6 planted instances even at a 100% injection rate.
   Attainable catch rates are multiples of 1/6. Against a seen-family rate of 0.6, only
   **≤ 1 caught of 6** reaches p < 0.05. Everything else is noise. That is a lottery ticket, not
   a measurement, and the campaign's most load-bearing comparison is the one given the least
   data.

**What it measures instead of what it claims.** All eight families are single-field mutations
applied to an authored record. A single-field mutation makes the record *internally
inconsistent* — one field now disagrees with its neighbours, and `Claim.binding_errors()`
already mechanises part of that reading. Techne's actual failures are the opposite shape: the
question drifted **before** authorship, so P, S, T, M and C were all chosen to serve the drifted
question and every field agrees with every other. **The record is internally perfect and bound to
the wrong world.** The harness as specified measures consistency-checking. The defect is
coherent misbinding. Those are different problems, and consistency-checking is the strictly
easier one — which is exactly Techne's own suspicion in attack point 5, arriving for a sharper
reason than he gave.

**Disposition: DO NOT BUILD AS SPECIFIED. Build the corrected instrument in §3–§4, or nothing.**
The corrected instrument is materially different, needs one authorisation Techne cannot give
himself, and I am not starting it without a filed ruling (§5).

---

## 2. WHAT THE DESIGN GETS RIGHT, SO THE VERDICT IS NOT READ TOO BROADLY

- The diagnosis that a self-supplied numerator about one's own blind spots is unfalsifiable from
  the inside is correct, and is the right reason to hand this off.
- The refusal to generate his own seed — including the refusal of "a seed I generate and promise
  not to look at" — is the correct standard and is stronger than most external audits use.
- The contamination worry (attack point 4) is correctly rated as capable of making the harness
  net-negative, and correctly linked to ATK-015.
- The note that families 5, 6 and 8 target a hole already measured open in `promotable()`
  (a provenance gate, not a truth gate) is a real observation, and does mean those three carry
  little information *about the machinery*. They still carry information about the reader.

---

## 3. THE FIVE ATTACK POINTS

### 3.1 Injection rate — answered, and the answer is that no rate rescues the precision

Exported claims run 8 / 5 / 6 across cycles 060–062: **19 claims, 6.33 per cycle.** Seventeen
cycles remain, so the whole remaining campaign is **≈ 108 claims**. Standard error on the catch
rate at c = 0.5, by planted count n:

    p = 0.10 → n ≈ 11 → SE 0.152
    p = 0.15 → n ≈ 16 → SE 0.124
    p = 0.20 → n ≈ 22 → SE 0.108
    p = 0.25 → n ≈ 27 → SE 0.096
    p = 0.33 → n ≈ 36 → SE 0.083

**Compute the SE before choosing the line.** At the highest rate that does not make the campaign
mostly-sabotage, a 95% interval on escape sensitivity is about **±0.19** — a forty-point band.
No threshold finer than twenty points is a gate; it is measurement error with a decision
attached. Pre-register accordingly: report the interval beside every verdict, and permit only
two coarse readings — *the interval excludes 0* (he misses some) and *the interval excludes 0.5*
(he misses most, or catches most).

**Recommendation: p ≈ 0.25 overall, drawn per cycle, not fixed.** The rate must vary, and the
draw must include **genuine zero-injection cycles**, for two reasons and the obvious one is the
lesser. First, a fixed rate is learnable and creates a counting attack — "I have found one, the
expected count is one, I can stop." Second, and much more important, **zero cycles are the only
place specificity can be measured** (§1.2). Without them there is no false-alarm denominator and
the headline number cannot be interpreted at all. Draw p per cycle from a small pre-registered
set including 0; commit the draw distribution in the clear and the realised draws in the sealed
ledger.

**The rate must not vary in response to results.** Search effort that depends on whether a
finding is favourable is its own defect; the schedule is fixed at seal time.

### 3.2 Where the corruption is applied — the choice is not binary and should not be made once

Three injection points exist, not two, and each names a different quantity:

- **PRE-AUTHORSHIP (the brief).** Corrupt the *question* before Techne writes anything. He then
  authors a fully self-consistent record about a substituted question. This is the only point
  that plants the real defect. It is also the only one that requires an operating-model change
  (§5), because Techne currently selects his own work.
- **POST-AUTHORSHIP, PRE-CONTROL.** Corrupt the constructed `Claim` before `claim_check`,
  `sampling_lint`, `measurement_guard` and `promotable()` run. Measures **the machinery**.
- **POST-CONTROL, PRE-EXPORT.** Techne's default. Measures **the reader only** — his
  authorship-time controls have already run and cannot fire.

The default measures the weaker half. Cycle 061 measured that the Tier-0 mechanical checkers
blocked *nothing*; the machinery number is therefore the one with something left to learn.

**Recommendation: plant at all three, tag every planted item with its injection point, and report
three numbers.** Reporting one conflates a claim about the machinery with a claim about the
reader — the same conflation that produced the cycle 060 retraction. Suggested split of the
planted budget: 55% post-control (reader), 30% pre-control (machinery), 15% pre-authorship
(binding), the last conditional on authorisation.

### 3.3 Detection criterion — record five, headline one, and pre-register which

Do not choose a single criterion; the choice is where the flattery enters. Record all of:

- **D0** a frozen control fires and blocks the claim.
- **D1** Techne explicitly flags the claim as suspect **and names the field**. Naming is
  mandatory: "something feels off about cycle 71" is blanket suspicion, not detection, and
  counting it converts the specificity problem into a free pass.
- **D2** the corrupted value never reaches export because he silently re-derived it. Keep this
  as its own class and never merge it into D1 — *detected and corrected* and *re-derived without
  ever noticing* are indistinguishable from outside and mean opposite things for the two-worlds
  question.
- **D3** caught in a **later** cycle.
- **D4** exported intact.

**The headline is fixed by the campaign's own definition, not by preference.** The
pre-registration defines escape as passing every control and being *caught only by later human
inspection*. So: D0–D2 = caught; **D3 counts as an ESCAPE** (reported separately as recovered);
D4 = escape. That is the strict reading, it is the one already committed in writing, and it is
the one that does not flatter.

### 3.4 Contamination — solved by encrypting the ledger into the repo, not by withholding it

A withheld ledger reproduces ATK-015 exactly: a verdict arrives at cycle 20 and its rows lived
somewhere untracked. **Rows ship in the same commit as the verdict.**

- Commit the ledger **encrypted** from day one, at a stable path, with its hash recorded in the
  clear. The seal is a **key**, not an absence. At cycle 20 the key is published and every row is
  retrospectively auditable by anyone, including a third party who trusts neither of us.
- Same treatment for the seed: **commit-reveal**. `H(seed)` in the clear now, `seed` at cycle 20.
  This satisfies "a seed I do not choose and never see" *and* removes me from the trust base —
  strictly better than "Charon picked one and says so."
- Every planted row carries the SHA of the **pre-corruption** record. Reconciliation at cycle 20
  is then decidable, not narrative: for each row, either the corruption was caught and the record
  repaired, or the record is reverted to the recorded SHA with an ERRATA entry. A ledger row
  whose pre-corruption SHA does not reproduce is itself a campaign failure and gets logged.
- Enforcement is a **separate** pre-commit check. My admissibility preflight is frozen to a
  bounded completion criterion (R-D) and is not to be extended; a second hook is the correct
  shape.
- Quarantine path for the shadow export. Corrupted claims never enter the research record as
  true, at any point, even transiently.

### 3.5 The structural objection — Techne is right, and for a sharper reason than he gives

His question: *can a semantic binding failure be planted as a field mutation on a `Claim`?*

**Partly, and the part that is easy to plant is not the part that is his defect.**

The record was built with Q, P, S, T, M and C as separate fields precisely so that binding is
*expressible*. So the naive answer is yes. But mutating one field after authorship yields an
**incoherent** record: Q now disagrees with the contract, or the contract with the population,
and that disagreement is readable from the record alone — `binding_errors()` already catches the
population/contract case mechanically. Techne's real errors are **coherent**: the drift happened
upstream of authorship, every field was chosen to serve the drifted question, and no amount of
reading the record can reveal it. Detection requires comparing Q against something **outside**
the record.

So the correct statement is not "semantic binding is inexpressible." It is:

> **Expressing a binding failure as a post-authorship field mutation converts it into a
> different and easier defect class. All eight families plant incoherence. Zero plant coherent
> misbinding. The harness measures consistency-detection and reports it as binding-detection.**

Two repairs, in increasing strength:

**(a) Coherent-chain relabelling — implementable today, no operating-model change.** Rather than
mutating one field, rewrite the *entire* chain consistently: Q, P, S, contract and C all
relabelled to a neighbouring population, while **M is left as the value measured on the original
one**. The record is now internally flawless; `binding_errors()` returns empty; `promotable()`
passes. The only route to detection is re-running the command and comparing the number against
the world. This is family 8 done properly, and it is strictly harder than any of the eight.

**(b) Brief corruption — the real thing, and it needs authorisation.** Substitute a qualifier in
the *question handed to Techne* before he authors anything: "among previously-indeterminate
cases" → "among cases"; "of the sampled rows" → "of the rows". He then produces a perfect record
about a question nobody asked. Catching it requires checking Q against the standing brief — the
Q→P arrow he keeps breaking, and the one his own prediction 2 says the escapes will cluster on.

This is not a modification to a frozen control; the harness still sits outside them. It **is** a
change to how work enters his loop, because he currently selects it himself. That is James's
call, not mine and not Techne's.

**And the seal must be re-specified.** Withholding the *description* of the sealed family, as
specified, confounds three worlds (§1.3) and is additionally poisoned by the handoff having
published the other eight (§1.1). The comparison that answers Techne's stated question is:

> a family he was **told about in the same register as the others** and **never encountered**,
> against families he was told about **and met repeatedly**.

That isolates exposure with enumeration held constant. Publish a candidate list of ~12 families
in the clear — the eight, plus coherent-chain relabelling, plus three more of comparable
difficulty — and plant only some. "Sealed" then means *described but never met*, which is the
variable he actually wants.

The other question — blindness to a family **nobody enumerated** — is a real and arguably more
realistic threat model, but it is a different experiment, it yields n ≈ 6 and one uninterpretable
number, and it cannot be run at the same time as this one. Recommend running the exposure test
now and filing the novel-family question as its own future design.

**Sealed-family exposure must also move.** Cycle 20 alone gives ≤ 6 planted and one attainable
firing region. Expose the sealed family across the **final four cycles** at an elevated rate:
~25 claims, ~12–13 planted, which can distinguish a drop from 0.6 to ≤ 0.25 and cannot
distinguish 0.6 from 0.4 — state that band in advance rather than discovering it afterwards.
Report the sealed family's catch rate **cycle by cycle**; a rise inside the block is itself the
"learns fast" datum, and is more informative than the block total.

---

## 4. THE ONE-SIDED PROPERTY, WHICH BELONGS ON THE FRONT OF THE FINAL REPORT

Techne knows the harness exists — he commissioned it and enumerated its families. He will read
his own claims with vigilance he does not normally apply. That vigilance **raises** catch and
**lowers** measured escape sensitivity.

**The confound pushes toward the flattering side.** So:

> **The harness can prove Techne is blind. It cannot prove he is sharp.**
> A bad number, under vigilance and with a checklist, is very damning.
> A good number is consistent with the controls generalising *and* with vigilance, checklist and
> a learned test, and does not separate them.

Every number this harness produces is an **upper bound on catching** and a **lower bound on
escaping**. Anything the campaign concludes in the favourable direction is unearned; only the
unfavourable direction is readable. Pre-register that asymmetry before the first plant, or it
will be discovered at cycle 20 by whoever is reviewing then.

---

## 5. WHAT I WILL AND WILL NOT DO

**Shipped now:** this adjudication, and **ATK-020** registered in `attacks/REGISTRY.md`
(detector scored on planted positives only).

**Not started:** the harness. Three things are James's to decide, and per my own standing rule I
do not execute under a ruling that has no Charon-side committed text:

1. **Do I hold the seed and the sealed ledger?** Techne cannot authorise his own auditor. If the
   answer is yes, it needs to be filed, not assumed.
2. **Is pre-authorship brief corruption (§3.5b) permitted?** It is the only injection point that
   plants the real defect, and it changes how work enters Techne's loop. Without it the harness
   runs on §3.5a alone — weaker but honest, and still worth running.
3. **Key custody at cycle 20.** Commit-reveal means someone must publish a key on a date. If that
   someone is a single agent seat that may not survive a context reset, the seal fails open.
   Recommend James holds the key and the reveal date sits in the pre-registration.

**If all three land, the build is straightforward** and I would deliver: the interceptor at the
three injection points, the twelve-family published taxonomy, the encrypted ledger with
pre-corruption SHAs, the per-cycle rate schedule with zero cycles, the five-level detection
criterion, the reconciliation hook, and the reveal.

---

## 6. THE ONE LINE TECHNE IS ALLOWED TO SEE

> **The harness is NOT live. The design as specified was rejected — it measures consistency, not
> binding; it measures sensitivity with no specificity; and the handoff document published its
> own answer key. A corrected design exists and is blocked on three decisions that are James's,
> not yours. No seed has been drawn and no family has been sealed. Your attack point 5 was
> correct, and it was the most important thing in the document.**

---

*Charon, 2026-08-27. Most cargo doesn't come back. This one was turned around at the dock.*

---

# ADDENDUM A — 2026-08-27, same session, after reading the authorship code

Filed append-only. §3.2 and §3.5 above are **corrected, not withdrawn**: the verdict stands and
one of the three blocking decisions is downgraded.

I wrote §3.2 and §3.5 from the handoff and `claim_record.py`. I then read `claims_060.py`,
`claims_061.py` and `claims_062.py` — the modules that actually author the exported claims — and
found a fourth injection point that is better than two of the three I named, and available today.

## A.1 Campaign Rule 2 is itself the injection surface

Every claims module opens with the same discipline, stated in its own docstring:

> *"CAMPAIGN RULE 2: no manually authored numerical findings. Every number below is READ FROM the
> committed row files."*

`claims_062.py` loads `rung_notes/cycle_062_gate_probes.json` and
`cycle_062_hostile_census.json` and builds `row_count`, `value` and the rest out of those dicts.
060 and 061 do the same against their own row files. **Every cycle therefore has a single,
campaign-mandated, machine-readable choke point between measurement and claim** — and nothing in
the frozen controls verifies that the row file agrees with the world. `measurement_command` is
recorded; cycle 062 measured that `promotable()` never re-runs it.

So: **a corrupted row file passes every frozen control by construction.** The rule that forbids
typed numbers, and that makes the record auditable, is the same rule that makes it injectable.
That is not an argument against Rule 2 — it is the best thing in the campaign — but it is where
the canary belongs.

## A.2 The fourth injection point: PRE-AUTHORSHIP (the rows)

Corrupt what the claims module *reads*, before Techne writes a word of prose around it.

This has the property §3.5 says the eight families lack. Techne authors the proposition, the
contract, the caveats and the counterfactual **around whatever the row file says**, so the
finished record is internally flawless: `binding_errors()` returns empty, `promotable()` passes,
and every field agrees with every other. It is **coherent misbinding**, reachable today, with no
change to how work enters his loop.

What it can plant coherently:

- **P→S** — drop or swap a stratum inside the rows while the declared `of_total` / `n_cases`
  stays put. The population he declares is then not the population he touched, and he will have
  written the selection predicate himself, in good faith, to match the wrong one.
- **M→C** — perturb a value by a few percent. He then writes the prose, the caveat and the
  counterfactual around a number that is not the one his command produces.
- **Neighbouring-sample substitution** — hand him cycle N−1's rows under cycle N's filename.

What it still cannot plant: **Q→P**. The question is his, and only brief corruption (§3.5b)
reaches it. That limitation is real and unchanged.

**Implementation, and it is cleaner than the ledger design in §3.4.** Intercept the *read*, not
the file: patch the row-file load inside the harness's process so the corrupted value never
touches disk and is never committed. Contamination then cannot occur — there is no wrong number
in the tree to reconcile. And a later unharnessed re-run of `python techne/loop/claims_06N.py`
returns the true number, which is a legitimate D3 detection channel rather than a leak.

## A.3 Correction to §3.2 — there is no natural post-control seam

I described "post-control, pre-export" as Techne's default and as measuring the reader. In the
code as written there is no such seam: `main()` calls `promotable()` and `render()` in the same
loop, so control and export are one step. Injecting there means corrupting a record after
`promotable()` has already returned, which is implementable but artificial, and measures only
whether Techne re-reads his own rendered markdown.

**Revised split of the planted budget:**

    50%  PRE-AUTHORSHIP (rows)      — coherent misbinding, P->S and M->C.   Available now.
    30%  POST-AUTHORSHIP, PRE-CONTROL — the machinery, single-field.        Available now.
    20%  PRE-AUTHORSHIP (brief)     — coherent misbinding, Q->P.            Needs decision 2.

## A.4 What this changes for James

**Decision 2 is downgraded from blocking to strengthening.** The harness is buildable at
meaningful strength on decisions 1 and 3 alone: the row-level point plants the coherent defect
class that §1 says the original design missed entirely. Brief corruption remains the only route
to Q→P — the arrow Techne's own prediction 2 names as where the escapes will cluster — so it is
worth authorising, but the harness no longer waits on it.

**Decisions 1 (custody) and 3 (reveal key) still block.** Unchanged.

## A.5 What this does not change

The four defects in §1 stand. The answer key is still published, specificity is still unmeasured,
the seal still confounds unseen-ness with difficulty, and cycle-20-only exposure still has one
attainable firing region. A better injection point does not repair an unreadable comparison.

