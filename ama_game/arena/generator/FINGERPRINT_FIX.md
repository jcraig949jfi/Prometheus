# Fingerprint fix — from 84% to chance

**Protocol fork:** v0.1-alpha → **v0.2-alpha**, 2026-08-26.

## The hazard

Under v0.1 every mutation operator appended its own phrase to the step it
rewrote: `CONVERSE:`, `Cancelling the factor`, `the same estimate is taken to
hold from n = 0 onward`. A falsifier could grep those and locate the planted
defect without doing any mathematics — the mirror image of the rulebook's own
kill condition about attacks exploiting fingerprints.

## Measured before and after

The old measure was a hand-written tell list, which can only find signatures
someone already noticed. `fingerprint_audit.py` is the stronger test: it trains
a bag-of-words classifier on step prose and asks it to point at the planted step
in derivations it has never seen. It finds tells nobody thought of.

```
                         before      after
grep tell list              85%         0%
classifier top-1          84.4%      17.2%
chance                    10.9%       9.4%
lift over chance         +73.4%      +7.8%
```

Both arms measured on the same audit, the "before" figure taken by checking out
the v0.1 generator into a scratch tree and running the identical script against
it — so the comparison is like for like rather than an old weak number against a
new strong one.

## What actually fixed it, in the order the audit forced

Patching the offending phrases would have removed only the tells I noticed. Each
step below was driven by what the classifier keyed on next, and every one of
them was a leak I had not predicted.

**1. One renderer for every step.** `render.py` generates each step's prose from
its own machine check. A mutated step and an untouched step of the same kind are
written by the same code path with different parameters, so a lexical signature
is impossible in principle. `render()` sees a check and nothing else — it cannot
know whether what it describes is true.
→ 84.4% to 31.2%. Grep list to 0%.

**2. Parameter tells.** Top token was `modulo|24`: mutations always substituted
the same replacement modulus, and no honest step ever used it. Randomised the
substitution and diversified the legitimate moduli.
→ 31.2% to 25.0%.

**3. The modulus was printed inside its own expression.** The congruence family
was `f ≡ f + m*g (mod m)`, so a reader only had to compare two printed numbers.
Rebuilt as `f ≡ f + C (mod m)` with `m | C`, which costs one division to judge.
→ 25.0% to 23.4%.

**4. A memorisable vocabulary.** Constants came from a seven-element menu, so a
model could learn which `(C, m)` pairs were honest instead of dividing. `C` is
now a random product of distinct primes; the pairs essentially never repeat.
→ no gain on its own, and that null result was the clue for step 5.

**5. The real leak: one instance per targetable kind.** Token `1173` gave it
away. Each derivation had exactly one congruence step, so a model never needed
to tell a true congruence from a false one — it only had to learn that
congruence steps are disproportionately targeted. M7 and M12 scored 9/9 while
M3, M6 and M8 scored 0: that is one bet paying off, not detection. Every
targetable kind now appears at least twice with independent parameters, leaving
a coin flip that only arithmetic settles.
→ 27.3% to **17.2%**, and the verdict flipped.

## Negative control (added after external review) — the earlier PASS was wrong

Zero above-chance predictability is the wrong standard: legitimate mathematics
predicts where mistakes live. The real question is whether the planted step can
be found WITHOUT checking the mathematics. The audit now runs the same
classifier over content-destroying representations plus a position-only
baseline.

Run 1: FAIL. Lift survived digit masking; skeleton beat full text (24.2% vs
17.2%, chance 9.4%). Causes: argmax broke ties by position, and M4/M9/M7
targeted the only step of their shape, so the planted step could be pinned by
kind.

Run 2: the entire residue was positional — position_only scored exactly what
full text scored.

Final: full 4.7%, digits_masked 3.1%, digits_shuffled 4.7%, skeleton 3.1%,
position_only 6.2%, against chance 5.4%. All at or below chance.

This shows a lexical or positional reader has no signal. It does not show a
semantically capable reader has none — but that reader would be doing the
mathematics, which is the point.

## The residue under the earlier, weaker standard

+7.8% over chance is not zero. It sits in the two modulus families (M12 6/9,
M7 5/9) and in domain widening (M4 4/10). Judging those steps takes one
division or one endpoint evaluation, so some signal there is *legitimate
mathematical content that a reader should see* rather than a stylistic tic. The
families that carried pure operator signatures — M3, M6, M9, M8, M10 — are now
at or below chance.

I am not claiming the leak is eliminated, only that it no longer lets a reader
skip the mathematics. If a live Blue posts suspiciously high detection
concentrated in M7/M12, this is the first thing to check.

## Consequences

- **The protocol version forks to v0.2-alpha.** Per `PREREG_A0.md` §4, prior
  data does not carry over.
- **The v0.1 A0 baseline is superseded** as a baseline for B/C/D. Its freeze is
  preserved as `FREEZE_A0_v0.1-alpha.json` and `freeze.py --verify` now reports
  drift against it, correctly — the instrument changed.
- **A0 must be re-run under v0.2** before any navigation comparison. That run is
  not urgent: A0's three blockers (at ceiling, unpowered at n = 30, one class
  unscoreable) are untouched by a prose change and still gate B/C/D.
- Generator pilot: PASS under v0.2. Cycle simulation: unchanged separation
  (bypasses 18.50 vs 10.10, p = 0.001), with the fingerprint hazard now
  reporting 0%.
