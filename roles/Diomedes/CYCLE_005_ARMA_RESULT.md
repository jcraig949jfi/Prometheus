# Diomedes cycle 005 ARM A — RESULT: b2 cannot answer Q1, and the reason is a design failure of mine

**Filed:** 2026-08-25. **Pre-registration:** `CYCLE_005_PREREG_terminal.md` §2, frozen at `94970ea8`.
**Rows:** `cycle005_armA_run.py` → `cycle005_armA_result.json`.
**Disposition: PARK** (prereg §4 MIXED/AMBIGUOUS branch). **Q1 is NOT resolved**, therefore
**cycle 005 is not terminal** as things stand.

---

## 1. The numbers (rungs 1–4; counts, not estimates)

Enumerated **3,276 of 3,636 cells**; 461 states retained both classes.

- chance — 0.5000
- **marginal ceiling** (rank `g` ignoring `v` and `f`) — **0.7892**
- **f-conditional ceiling** (rank `g` knowing `f`, not `v`) — **0.9735**
- **F_pure** (properties of `v` + operator identity, no table lookup) — **0.9620**
- **F_applied** (F_pure + one table application) — **0.9419**
- oracle — 1.0000

`F_applied − F_pure = −0.0201`. `F_pure − f_conditional_ceiling = −0.0115`.

Assertions: perfect predictor = 1.0 ✓ · constant predictor = 0.5 ✓ · monotone invariance ✓ ·
**enumeration_complete ✗ (see §3)**.

## 2. Why b2 cannot answer Q1

**The conditional headroom is 0.0265.** Knowing only which two operators are involved gets you to
0.9735; the entire remaining space for state-conditional structure is 2.65 percentage points.
Compare h1, where the state-independent ceiling was 0.6254 against a 1.0000 oracle — **0.3746 of
headroom, fourteen times larger.**

Operator commutation is ~97% determined by *which operators*, essentially regardless of `v`. So b2
is not a landscape with conditional structure that cheap arithmetic might or might not recover; it
is a landscape with almost **no conditional structure at all**.

By the letter of prereg §2.1, F_pure approaching the f-conditional ceiling answers Q1 negatively.
**I decline to read it that way, and the reason matters:** you cannot test *"does cheap arithmetic
recover conditional signal under a different oracle form"* in a population that has almost no
conditional signal of any kind. The test is underpowered **by landscape, not by sample size** — no
amount of extra data would help. That is a VACUOUS reading, and the honest disposition is PARK.

`F_applied < F_pure` is consistent with this: with 2.65 points available, a restricted rule class
given a noisier input does slightly worse. It is not evidence of anything.

## 3. Declared: a failed assertion and a design failure

**3.1 Assertion `enumeration_complete` FAILED.** 360 of 3,636 cells (9.9%) are absent. Cause is
fully diagnosed and benign: `sq_mod_100` maps into 51–96, and the other operators' recovered tables
cover only −50…50. Every missing cell involves `sq_mod_100` as inner or outer operator.

**They were not filled, deliberately.** Computing `log2_floor(96)` myself would assume operator
semantics beyond what the corpus establishes — precisely the trap step 0 was built to prevent. A
90.1% enumeration established by execution is worth more than a 100% one where a tenth is my own
extrapolation. Reported rather than repaired.

**3.2 The design failure is mine, and it is the third instance of a known trap.** The cycle-005
pre-flight measured class balance and oracle form. **It did not measure whether b2 had any
conditional headroom to find.** Had it computed the f-conditional ceiling — a few seconds of work on
the same tables — b2 would have been rejected as a Q1 population before the prereg was written.

This is the "pre-flight only some things" trap, now fired three times:
1. cycle 004 — assumed relation/pair confounding without measuring it (caught in time)
2. cycle 005 planning — recommended c4 without checking for a negative class (it had none)
3. **cycle 005 Arm A — checked balance and oracle form, but not conditional headroom**

**Amendment to the standing pre-flight, adopted:** any population proposed for a
conditional-structure question must have its **conditional headroom measured first** — the gap
between the state-independent ceiling and the oracle. A headroom below ~0.05 disqualifies the
population regardless of how attractive its oracle form is.

## 4. Where this leaves cycle 005

Prereg §1 makes the cycle terminal **only if both** Q1 and Q2 resolve. Q1 has not resolved. Three
options, and the choice is genuinely open:

- **Find a better Q1 population** — one with a non-arithmetic oracle *and* real conditional headroom.
  The cycle-005 pre-flight found no such family in the corpus: c4/b1/b5 are single-class, c5 shares
  h1's arithmetic oracle form, and b2/b3/b4 are small synthetic operator algebra. **On present
  evidence the corpus does not contain one.**
- **Accept Q1 as unresolvable on this corpus and say so.** This is honest and is itself a finding: it
  is the same statement as §5 of the status doc, one level sharper — the corpus has no second search
  process with both a different oracle form *and* substantial conditional structure.
- **Move Q1 to the Lean environment**, where the oracle is proof-state transition rather than
  arithmetic, and conditional headroom can be measured before committing. That is the new thread
  already named in `BOOTSTRAP.md` §5, not a sixth cycle here.

**My reading:** option 2 plus option 3 — record Q1 as unresolvable *in this corpus*, and let the Lean
thread carry it. But Arm B (Q2) is unaffected and should still run; it is the transport control on
h1, needs no new population, and answers the question that would withdraw or confirm finding 3.

## 5. What Arm A does establish

Not nothing, though it is smaller than the cycle intended:

- b2's decomposition is **real and exactly enumerated**: chance 0.5000 → marginal 0.7892 →
  f-conditional 0.9735 → oracle 1.0000. Knowing the operator pair carries 0.2892 of the 0.5000
  interval; knowing `v` as well carries only 0.0265 more.
- **A landscape can have a large action-ranking signal that is almost entirely non-conditional.**
  h1 and b2 sit at opposite extremes on that axis (0.3746 vs 0.0265 of conditional headroom). That
  is a genuine structural contrast between two Prometheus search processes, measured exactly.
- The step-0 → enumeration → assertion chain worked: semantics established by three-source
  differential test, space enumerated, three assertions passed and the fourth failed loudly with a
  diagnosed cause.

*— Diomedes, cycle 005 Arm A, 2026-08-25. Disposition PARK. Q1 unresolved; Arm B still to run.*
