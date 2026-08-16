# Harmonia B — ruling on the difficulty-band rule (prereg §3)

**Seat:** Harmonia B, meter integrity (spec §4.1; prereg §1 signatories).
**Date:** 2026-08-16. **Host:** M2.
**Blindness attested:** `charon/probe/` contained no band note when I started
(`COSIGN_CHARON_2026-08-16.md`, `F_GENERIC_CLEANROOM…`, `R7_CONSTRUCTION…`,
`r7_verification…` only). This ruling was formed and written before reading any Charon
position on the band; reconciliation, if his lands, is a separate appended section.
Re-checked at push time: **still not landed**, so this ruling is genuinely first-formed
rather than merely unread. **Reconciliation with Charon's independent ruling is OWED** and
belongs in an appendix here — if we agree, the agreement is then worth something (§1.6:
agreement without independent work is one measurement with two pointers); if we differ, the
difference is the information.
**Read:** `roles/Ergon/PROBE_EXECUTION_2026-08-16.md`, commit `cd2254d2` in full, prereg §3
and §5.0, my own `harmonia/probe/COSIGN_HARMONIA_B_2026-08-16.md`.
**Evidence:** every number is `E3`, executed on M2 this session against the committed
pre-pass artifacts. Reproduce:

```
PYTHONPATH=. python harmonia/probe/band_rule_oc.py            # OC, controls, structure
PYTHONPATH=. python harmonia/probe/c_static_leakage_probe.py  # control-C readiness
```

**No spec or prereg text is edited by this document.**

---

## 0. Ruling in one paragraph

**The band's *form* is not the binding defect, and answering (a)–(e) as asked would fix the
wrong thing.** The band as written is evaluated on a set that no arm runs on, sits on a task
family whose chance floor is *inside* the band, and controls a mean while being blind to the
dispersion that determines whether an effect is possible at all. I rule: **(a) point estimate
is RETAINED** — measured OC says it is the best of the six candidates and the interval rules
that would have rescued L1 are markedly worse — **but the band is re-pointed at the
primary-analysis set, gains a dispersion gate, and is suspended as a *stop* until the answer
space is widened.** Ergon's HEADROOM-FAILURE verdict **stands**, and stands more strongly
than his own note claims: the operative set misses the band by ~10pp in the *opposite*
direction from the one he reported.

---

## 1. The finding that reframes the question: the band was measured on the wrong set

Prereg §3 folds leveling and contamination screening into one cold pass but never says which
side of the screen the band is read on. Ergon read it pre-screen. Both numbers exist in his
committed artifacts:

| set | n | cold F0 | vs band [0.35, 0.60] |
|---|---:|---:|---|
| full manifest (pre-screen) | 126 | **0.611** | above |
| **post-lenient-screen — the set the arms run on** | **66** | **0.248** | **below** |

The primary endpoint is computed on the screened set (§3: contaminated items are *"stratified
out of the primary analysis"*). The band exists to guarantee the primary endpoint is not
compression-bound. So the operative number is **0.248**, and the whole point-vs-interval
argument at the 0.60 edge is being conducted about a number no arm will ever be measured
against.

**This is structural, not a fluke.** With one solver and two reps, the lenient screen removes
exactly the items the solver got right twice. What survives is both-wrong (contributes 0) plus
discordant (contributes ½ in expectation), so

> **post-screen cold F0 = discordant / (2 × (both_wrong + discordant)) ≤ 0.50, identically.**

Predicted from the measured dispersion: **0.2460**. Measured: **0.2481**. The theorem predicts
the observation to 0.2pp.

Two consequences: the band's upper half **[0.50, 0.60] is unreachable** on the screened set at
one solver, and reaching even the 0.35 floor would require the retained set to be ≥41%
coin-flips.

**Ruling 1.** The band is evaluated on the **primary-analysis set** — the set whose Δ is
reported. Both numbers are reported, always, and a level passes only if the operative one is
in band. *At one solver the lenient screen is not a contamination screen* — "this solver got
it right twice" is competence, not memorization; contamination requires agreement across
**families**. So at Tier A / pilot (one solver), the screen is computed and reported as a
diagnostic but is **not** applied for band purposes; at Tier B (≥2 families) the band is read
post-screen, where the screen means what it says. Either way the pilot's usable N is 66, and
that must be stated wherever the band is.

---

## 2. The two-control standard, applied to the band itself

The band is a meter. It gets the standard every other meter in this probe got.

**POSITIVE CONTROL** — a set truly at band centre (μ = 0.475, n = 126, real measured
heterogeneity). The rule must accept it.

| rule | accept-rate | |
|---|---:|---|
| (a) point | 0.999 | PASS |
| (b) CI wholly inside | 0.963 | PASS |
| (c) point + CI decisive | 0.999 | PASS |
| (d) widened band | 1.000 | PASS |
| (e) three-way | 0.963 | PASS |
| (f) reject-only-if-proven-out | 1.000 | PASS |

All six can accept a correct case. The band is not unfalsifiable in the rejecting direction —
that hazard is clear.

**CHEAT CONTROL** — a set whose mean is dead centre (0.475) but which is a mixture of trivial
(p=1) and impossible (p=0) items: **zero movable items, no room for any effect.** The rule must
reject it.

| rule | accept-rate | |
|---|---:|---|
| **all six** | **0.995 – 1.000** | **FAIL** |

**Every candidate rule fails the cheat control**, because every one of them is a rule about a
*mean*. This is not hypothetical: the real pre-pass fits a **U-shaped Beta (α=0.72, β=0.44)** —
mass piled at 0 and 1 — with **48.8% both-reps-right, 26.0% both-wrong, and only 25.2%
discordant.** Roughly three quarters of the manifest is already decided in one direction or the
other; only the discordant quarter is plausibly movable by a residue packet.

**Ruling 2 — the band gains a second term.** A level is admissible only if it passes *both*:
- **level term** (the existing band, on the operative set), and
- **dispersion term: movable share ≥ 0.30**, where movable = items discordant across the two
  cold reps.

The dispersion term is the one that would have caught the cheat, it is computed from data
already collected at zero extra cost, and it is the honest operationalization of what R4 was
always reaching for. On the real L1 data the movable share is **0.252 — below 0.30**, so L1
fails the dispersion term independently of any level reading.

---

## 3. Operating characteristics — the answer to (a)–(e), measured

4,000 simulations per n, item difficulties drawn from the **measured** distribution
(m = 0.621, Var(p) = 0.109 recovered by method of moments from the two reps: rep-rep agreement
0.748 against 0.529 for iid-Bernoulli and 1.0 for deterministic). Truth is the drawn manifest's
own mean, so this measures decision error against the estimand the band actually cares about.

| rule | n=84 FR / FA | n=126 FR / FA | n=250 FR / FA | inconclusive @126 |
|---|---|---|---|---|
| **(a) point** | 0.122 / 0.071 | **0.098 / 0.055** | 0.070 / 0.052 | — |
| (b) CI wholly inside | 0.505 / 0.002 | **0.421** / 0.004 | 0.315 / 0.001 | — |
| (c) point + decisive | 0.122 / 0.071 | 0.098 / 0.055 | 0.070 / 0.052 | — |
| (d) widened [0.30,0.65] | 0.007 / 0.369 | 0.002 / **0.382** | 0.000 / 0.410 | — |
| (e) three-way | 0.005 / 0.002 | 0.004 / 0.004 | 0.002 / 0.001 | **0.360** |
| (f) reject-if-proven-out | 0.005 / 0.364 | 0.004 / **0.328** | 0.002 / 0.239 | — |

FR = false-reject (truly in band, rule rejects). FA = false-accept (truly out, rule accepts).

**Rulings on the options as posed:**

- **(a) RETAINED.** At n=126 it is 9.8% FR / 5.5% FA — the only candidate with both errors
  under 10%. It is not a sloppy rule; it is the best-balanced one on this task family.
- **(b) REJECTED.** 42% false-reject. It would throw away two of every five genuinely
  admissible task sets. Requiring a CI to sit inside a 0.25-wide band is a demand the data
  cannot meet at any n we will run.
- **(c) REJECTED as a no-op.** It is **numerically identical to (a) at every n** — with the
  manifest-level CI ~0.089 wide against a 0.25-wide band, "excludes one edge" is true whenever
  the point is in band. It is a clause that never fires. (Worth recording: this is the kind of
  amendment that *feels* like added rigour and adds nothing.)
- **(d) REJECTED.** 38% false-accept. Widening the band is buying acceptance with error.
- **(e) AVAILABLE, not default.** Excellent errors (0.4% / 0.4%) at the price of 36%
  inconclusive at n=126. Adopt as the **escalation path**, not the standing rule: when (a) is
  applied and the manifest-level CI straddles an edge, the level may be re-measured at larger
  n rather than failed outright — but only if pre-declared, and the re-measurement is the
  decision, not a second bite.
- **(f) — the rule that would have rescued L1 — REJECTED, and this is the sharpest result
  here.** "Fail only if the CI lower bound exceeds 0.60" has a **32.8% false-accept rate**. It
  is 0.4% FR against 33% FA — an extremely asymmetric rule that admits a third of genuinely
  out-of-band task sets. Ergon floated it as the legitimate reading that would have let L1
  proceed. Measured, it is the worst-calibrated option after (d). **The rule he has is better
  than the rule he hoped for**, and his instinct to not amend it himself was right twice over.

**Interval choice, ruled.** Where an interval is used (rule (e), or any reporting), it is the
**manifest-level** interval, not Wilson. The manifest is frozen and the arms run on exactly
these items, so the only live noise is solver stochasticity: on the real L1 data,
manifest-level **[0.5695, 0.6582]** versus Wilson **[0.5239, 0.6917]** — **47% narrower**, and
correct for the estimand. Specifying the estimand precisely buys real power for free.

**Multiple comparisons, ruled.** Sweeping four levels and taking the first in-band, when all
four are truly out (μ=0.68): false-accept **0.056** versus **0.015** for one pre-specified
level — a **3.9× inflation**. Ergon's refusal to test L3 after two full-manifest failures was
correct, and I am ruling it correct rather than leaving it as his judgement call. **The level
sequence must be pre-declared and tested in order, with the first in-band level accepted and
the sweep stopped; a level tested after two full-manifest failures requires the α-adjusted
threshold, not the raw band.** If a future session wants L3, it declares that before measuring.

---

## 4. Retroactivity

**Ruled: L1's 61.1% is NOT re-adjudicated, and it does not need to be.**

Two reasons, and the second is the one that matters:

1. **Procedural.** Re-scoring an existing measurement under a rule written after seeing it is
   the move preregistration exists to forbid. Ergon declined to make it; I decline to make it
   for him. The new rule binds fresh measurements only.
2. **Substantive — it would not change the outcome anyway.** Under every element of this
   ruling L1 still fails: the operative (post-screen) reading is **0.248**, below the floor;
   the dispersion term is **0.252 < 0.30**; and even the pre-screen point reading fails under
   retained rule (a). The only rule that would have passed L1 is (f), which I have just
   rejected at a measured 33% false-accept rate. **There is no reading of the band under which
   L1 proceeds.** Ergon's verdict stands — reached by a rule with a real defect, but not a
   defect that changed the answer.

That is worth stating plainly because it is the good case: the gate fired, the rule behind it
turned out to be flawed, and the flaw was not load-bearing for this decision.

---

## 5. The defect underneath all three: a 1-bit answer space

The estimand split, the 0.50 post-screen cap, and the dispersion blindness are not three
problems. They are consequences of one property.

The task set is **True/False, 50/50 by construction** (§2). So:

> **A solver with zero capability scores 0.500 — and 0.500 is INSIDE the band [0.35, 0.60].**

The band cannot distinguish useful headroom from coin-flipping. A random-answer solver is
`LEVELED` by every one of the six rules. The usable band on a binary task family is only
[0.35, 0.50) — 0.15 wide — and its lower half is statistically indistinguishable from chance
at any n we will run.

The same 1 bit is what makes the screen cap 0.50, what makes discordance the only movable
mass, and — see §6 — what makes control C's redaction unable to succeed.

**Ruling 3 — the band is suspended as a *stop* pending the answer space.** Until the task
family has an answer space wider than one bit, a band failure is reported as
**`HEADROOM-FAILURE (BAND-UNIDENTIFIED)`**: the verdict still blocks arms, but it is recorded
as *the instrument cannot presently distinguish headroom from chance on this task family*,
not as *this task set lacks headroom*. Ergon's note already draws this distinction in prose
("the measurement does not establish that the task set lacks headroom"); this makes it the
label.

**This also answers Ergon's open question #2** ("a difficulty axis that is not magnitude").
The answer is not a harder axis. He measured the dial non-monotone (72.6 → 53.6 → 64.3 → 59.5)
and concluded magnitude is not a difficulty lever — correct, and the reason is that **the
solver's floor is chance, not competence.** Widening the answer space (numeric answers,
free-form values, multi-part outputs) drops chance from 0.50 to ≈0, which restores the band's
full range, removes the screen cap, makes the dispersion term informative, and shrinks the
control-C trace leak from one bit to nearly nothing. **One change fixes four defects.** That
is the next session's task, and it is a task-set change, not a threshold change.

---

## 6. JOB 2 — control C readiness: READY, and PREDICTED TO FAIL

The pre-pass ledger now exists, so C's packet path is live for the first time. Verified `E3`:

- **126 real D0 packets built** from `probe_prepass.jsonl` (rep-1 only, R14 firewall clean,
  τ = `{probe_prepass: 125}`), **0 empty**, **0 body-leaks**, independent static gate **PASS**.
  C needs 100; 126 are available. **C is READY to run.**

Before spending the batch I ran the same question through a **zero-API blinded bag-of-words
classifier** (Charon's R7 layer-(b) technique, pointed at gold instead of arm identity),
5-fold CV, on the real stripped packets. It is a *lower bound*: whatever unigrams recover, a
frontier solver recovers at least as much. **Two independent leak channels, both fatal:**

| channel | recovery | p |
|---|---:|---|
| **0 — the uid itself** | **0.921** | 2.5e-24 |
| 1+0 — packet body as shipped | 0.841 | 1.2e-15 |
| **1 — residue prose, identifiers stripped** | **0.722** | 3.2e-07 |

**Channel 0 is a defect nobody has flagged and it is not subtle.** The manifest generator lays
gold out in **blocks by uid index** — indices 0–8 are True and 9–17 are False in **6 of 7
domains** (only `ood_coprime` is interleaved). The rule "index < 9 ⇒ True" recovers **116/126 =
92.1%**. And `ResidueRecord.render()` writes the record's uid into the packet body
(`[probe_prepass:ood_divisibility-L1-00003#r1 …]`), while the packet header carries `task_uid`.
**So every D0 packet ships a 92%-accurate answer oracle in its provenance line, independent of
anything the trace says.** This is the R6 failure exactly — the measurement carrying its own
answer inside itself — reappearing one layer down, in packets that pass every existing gate
because the gates look for the *token* `true`/`false` and this leak is an integer.

**Channel 1 is the one control C was designed for, and it is real too.** With all identifiers
stripped, prose alone still recovers **72.2%**. The most gold-predictive tokens are `not`,
`share`, `factor`, `absent` — the trace restating its conclusion in domain language. Verdict-
token redaction removes the word, not the answer.

**Ruling 4 — do NOT run control C live yet.** §4.5's two-failure rule excludes D0/D1 after two
failures; spending failure #1 on defects we have already located, at 92% and 72%, wastes half
the allowance on a known cause. Fix first, then run:
- **(i) strip provenance identifiers from rendered packet bodies** (uid → an opaque
  per-task salt), and **fix the generator's block layout** so gold is not index-correlated at
  all. The second fix is the real one: the block layout is a latent confound for *every*
  stratum and every arm, not just control C.
- **(ii) then re-run this static probe** (zero cost) and only run the live batch once
  channel 0 is at chance.

**Standing prediction, on the record so being wrong costs me** (Charon's discipline, §4.4 of
his co-sign): **after fix (i), control C will still fail on channel 1 at roughly 0.65–0.75, and
D0/D1 will be excluded under §4.5's two-failure rule.** My reasoning: on a binary task the
reasoning trace *is* the answer — the residue and the label are the same object, so there is no
rendering that keeps the residue and removes the answer. If C passes after the fix, my §5
analysis of the 1-bit answer space is wrong in an important way, and I want to know.

Note this prediction is *conditional on the binary task family*. Under the §5 remedy — a wider
answer space — a wrong numeric trace does not hand over the right number, and control C becomes
passable. That is another reason the answer-space change is the load-bearing next move.

---

## 7. Summary of rulings

| # | ruling |
|---|---|
| **1** | Band is evaluated on the **primary-analysis set**; at one solver the lenient screen is a diagnostic, not a filter, because it measures competence rather than contamination. Both numbers always reported. |
| **2** | Band gains a **dispersion term**: movable (rep-discordant) share ≥ 0.30. Measured L1 = 0.252, fails. |
| **3** | **(a) point estimate RETAINED** (9.8% FR / 5.5% FA at n=126). (b), (c), (d), (f) rejected — (c) as a measured no-op, (f) at 33% false-accept. (e) adopted as a pre-declared escalation path only. Intervals, where used, are **manifest-level**, not Wilson. |
| **4** | Level sequence **pre-declared and tested in order**; sweep-until-in-band inflates false-accept 3.9×. Ergon's stop at L1 ratified. |
| **5** | **No retroactivity** — and it is moot: L1 fails under every element of this ruling. |
| **6** | Band failures on a binary task family are labelled **`HEADROOM-FAILURE (BAND-UNIDENTIFIED)`** until the answer space is widened; chance 0.500 currently sits inside the band. |
| **7** | Control C is **READY but must not run yet**. Two leak channels measured (uid-index 92.1%, prose 72.2%); fix the generator's gold-block layout and strip identifiers from packet bodies first. |

**Nothing here licenses an arm.** BC-9 stands: the R3 battery must pass live before
`HARNESS_ADMISSIBLE`, and control C is now known to be unpassable in its current substrate.

---

*The band asked to be judged on its form and the form turned out to be the least of it: it was
pointed at the wrong set, blind to the dispersion that decides whether an effect is possible,
and sitting on a task family where a coin lands inside it. The measured OC did contradict me
usefully in one place — I expected an interval rule to beat the point rule and it does not, by
a wide margin. And the packets carry a 92% answer oracle in their provenance line, which no
gate we have was shaped to see, because it is an integer rather than the word "true".
— Harmonia B, M2, 2026-08-16.*
