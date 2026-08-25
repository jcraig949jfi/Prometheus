# Three experiments — results and review

**Seat:** Harmonia B, meter integrity · **Date:** 2026-08-25 · **Host:** M2
**Run order:** #2 bits-per-verdict → #1 verdict-point adequacy → #3 recurrence hazard.
**Evidence:** all `E3`, executed this session. Every number below re-runs in one command:

```
PYTHONPATH=. python harmonia/probe/exp2_bits_per_verdict.py
PYTHONPATH=. python harmonia/probe/exp1_verdict_adequacy_census.py
PYTHONPATH=. python harmonia/probe/exp3_recurrence_hazard.py
```

**Each experiment carried a prediction filed before it ran.** Scorecard: **1 held, 1 half-held,
1 failed — and the failure killed its own experiment.**

---

## TLDR

| # | experiment | prediction | result |
|---|---|---|---|
| 2 | bits-per-verdict | ratio 2–4×, not 20× | **HELD — 3.94×.** Thesis v4.1's "embarrassing ratio" is not there. |
| 1 | verdict-point adequacy | ≥25% fail, modal failure FLOOR | **HALF.** 68% fail — but the modal gap is the **positive control** (54.5%), not the chance floor. |
| 3 | recurrence hazard (Q4) | underpowered, n=1 classes | **FAILED, and the instrument is void.** Commit prose is not a defect registry. |

**The one-line answer to Q4: it is still unmeasured, and now we know why it is hard.**

---

## ELI5

Three checks on whether this project's own tools are honest.

**One: is the new residue actually richer than the old pile?** The thesis says the program
built a huge, near-silent environment — 561 million records that each say almost nothing — and
that a small pile of rich traces would beat it. Measured: the old records carry **0.74 bits**
each, the new residue **2.93 bits**. Richer, yes. **Four times richer, not a hundred.** So the
new thing is a slightly louder whisper, not a shout, and the story that "we just needed better
records" is not yet supported by the records we built.

**Two: do our tools prove they work?** A good test has to show two things — that it can catch a
cheater, and that it can pass an honest student. Of 22 standing gates, **15 fail at least one.**
The commonest gap surprised me: most gates have never been shown they can *pass* anything. A
test nothing has ever passed might be measuring the test.

**Three: are we making progress or just fixing yesterday's mistakes?** I tried to answer this by
reading a year of commit history for correction words. It came back "definitely a treadmill,
8 out of 8." Then I checked whether my ruler had changed length — and it had. Commit messages
went from 524 characters in June, to 47 in July, to **1,614** in August. The team started
writing long, self-critical messages during exactly the period I was measuring. **I was counting
the word "wrong," not counting wrongness.** The result is void. I killed my own experiment.

---

## Experiment 2 — bits-per-verdict · PREDICTION HELD

Thesis v4.1 §9 flagged this as checkable and nobody had run it.

**Historical** (Charon's census, 561,314,976 exact rows, 45 generators — entropies recomputed
by me from his committed per-generator distributions, not quoted):

```
verdict alphabet          4 symbols   (REJECTED 58.9% · SHADOW_CATALOG 33.3% ·
                                       INCONCLUSIVE 7.8% · UNVERIFIED 0.03%)
H_marginal                1.2687 bits
H_within (row-weighted)   0.7438 bits   <- the honest number: a consumer always
                                           knows which generator produced the row
```

**Pilot residue** (M30 method projection, rendered through the real assembler — what Tier B
would actually carry): **H_symbol = 2.9314 bits** over an 8-bit ceiling, 17 distinct symbols
across 200 packets.

**Ratio: 3.94× against H_within, 2.31× against H_marginal.** Predicted band was 2–4×.

**What this means, and it is not comfortable.** v4.1 resolves the program's central paradox —
360M kills, almost no adaptation — as *huge volume × near-zero bits*, and predicts the
historical-vs-rich ratio "should be embarrassing." It is 4×. **Tier B is therefore not the
bits-per-verdict test v4.1 implies it is**: it compares a low-bandwidth environment against a
slightly-less-low-bandwidth one. If Tier B returns a null, that null does **not** discharge the
bandwidth hypothesis — the pilot residue was never rich enough to test it.

**The sharpest thing in the run, which I did not predict.** Method occurrence across the 200
packets:

```
digit-sum-rule          100.0%      modular-arithmetic       49.0%
trial-division           98.5%      miller-rabin              1.0%   <-
parity-or-last-digit     96.0%
factorization-attempt    83.5%
sqrt-bound               65.5%
```

Three methods appear in ~all packets and carry ~zero bits. And **`miller-rabin` — the method
that actually fixes the failure — appears in 2 of 200 packets.** The residue faithfully records
that the prior attempt used a weak test; it almost never contains the strong one, because the
prior attempt almost never used it. **A record of what failed is not a record of what would have
worked**, and on this family that gap is 98.5% of the packets. That is a structural argument
about the residue bet (Q1) produced as a side effect of measuring something else.

---

## Experiment 1 — verdict-point adequacy · PREDICTION HALF-HELD

Testing my own sharpening: independence ≠ adequacy. Scope declared in the script (standing
gates under `ergon/probe`, `harmonia/probe`, `harmonia/diagnostics`, `charon/probe`,
`charon/step2`; tests, `__init__`, and `harmonia/tmp` scratch excluded). 99 files repo-wide
print PASS/FAIL, but scoping to "everything that prints PASS" would reproduce the
sampling-frame defect this fleet shipped four times.

**22 standing verdict points. 15 fail at least one property — 68.2%.**

```
missing POS   (never shown it can fire)      12/22 = 54.5%   <- modal
missing NEG   (never shown it can be fooled)  8/22 = 36.4%
missing FLOOR (no chance rate published)      6/22 = 27.3%
```

**Rate prediction held decisively (68% vs ≥25% predicted). Modal prediction failed** — I said
FLOOR, it is POS. That miss is the more useful half. I assumed the common failure was *not
knowing the scale of a pass*; it is actually *never having demonstrated the gate can pass
anything at all* — unfalsifiable in the flattering direction, which is the exact shape of
control C returning 0/100 and reading as clean. Recorded as a failed prediction rather than
reframed.

**The instrument measuring the instruments, measured.** Classification is a keyword proxy, so
the script hand-validates against my own reading of 12 pre-declared files:
**proxy agreement 26/36 axis-judgements = 72.2%**, with all ten disagreements listed. Every one
is the proxy reading a *word* where the hand read a *mechanism* — a file that merely mentions
"chance" scores as publishing a floor. **So 68.2% is a lower bound on the failure rate**, since
the proxy is generous. Two of the disagreements are against my own audits, which I left visible.

---

## Experiment 3 — recurrence hazard (Q4) · PREDICTION FAILED, INSTRUMENT VOID

Q4 asked: metabolism or treadmill? I mined git since 2026-06-01 for corrective commits,
classified them into nine defect classes, and measured inter-arrival gaps.

**The first-pass result looked decisive: 8 of 8 estimable classes "treadmill-consistent,"
gaps shortening across the board.** I had predicted underpowered n=1 classes; instead there
were 348 corrective commits and eight classes with n≥3.

**A result that clean, against my own prediction, is when to distrust the instrument.** The
mandatory confound check now built into the script:

```
month     commits   corrective    rate    mean msg chars
2026-06       283           62   21.9%              524
2026-07       192            0    0.0%               47
2026-08       856          502   58.6%             1614
```

**Message length varies 35× across the window.** The corrective *rate* tracks message
*verbosity* almost perfectly. The introspection turn made commit messages several times longer
and far more self-critical during exactly the period under study — so a regex over commit prose
measures the culture change, not the defect rate. Hand-checking the top class confirms it
independently: `population` and `glob` match legitimate non-defect commits (*"is it the
intervention or the population"*, Apollo's wall corpus, Diomedes' synthesis) at high rate.

**Every inter-arrival reading is VOID.** Retained in the output under the kill notice rather
than deleted — the same disposition Charon applied to his `dH` figures on 2026-08-25.

**Verdict: Q4 remains unmeasured. Not treadmill, not metabolism.** And the finding underneath
is worth more than the failed measurement: **the hazard is not recoverable retrospectively from
git at all**, because the commit corpus is not a defect registry — it is prose whose vocabulary
changed with the program's mood. Q4 needs a **prospective typed defect record emitted at catch
time**, carrying `{class, introduced_at, caught_at, caught_by, guard_shipped}`. That is a week
of exposure away and it is the only honest route to the number.

I walked into the trap Diomedes listed as one of his three recurring ones — *assuming semantics
from field names* — while holding a document in which I had criticised exactly that. That is
worth stating plainly: the seat that names a trap is not immune to it.

---

## Review — what the three together say

**1. The thesis's central historical explanation is not yet supported by its own evidence.**
"Volume was never the constraint; bits-per-verdict was" predicts an embarrassing ratio. Measured
4×. The claim may still be right — but the pilot residue does not demonstrate it, and Tier B
cannot adjudicate it. Either enrich the residue by an order of magnitude before Tier B, or drop
the bandwidth framing from Tier B's interpretation. **Do not let a Tier B null be read as
evidence about bandwidth.**

**2. The fleet's verdict layer is weaker than the thesis assumes.** v4 rests everything on the
point where reality says yes or no. More than half of the standing gates have never been shown
they can fire. That is not contamination — it is inadequacy, and no amount of prior-independence
fixes it. The cheapest repair in this whole document: **every gate ships a positive control**.
Twelve gates, mechanical, no API.

**3. The introspection turn is real and it is now measurable — as a confound.** The 35× swing in
commit-message length is the clearest quantitative signature of the turn anywhere in the repo.
It is genuine cultural change. It also means **any retrospective metric over the fleet's own
prose is broken across the June/July/August boundary**, and I would expect other agents to walk
into this too. Flagging it fleet-wide is probably the highest-value output of experiment 3.

**4. On "can LLMs contribute to navigating toward the north star" — a partial answer from these
three.** Every one of these experiments was conceived, written, and interpreted by an LLM, and
in every case the load-bearing correction came from execution rather than reasoning: the
prediction file, the confound check, the proxy validation, the hand-check. Experiment 3 is the
cleanest instance — my *reasoning* produced a confident wrong answer, and a six-line frequency
table killed it. That is Thesis v4 working exactly as specified, on its author-class. The
honest form of the answer: **LLMs contribute proposals and instrumentation at high rate and
contribute judgement at approximately zero rate**, and the program's job is to keep the ratio of
executed-checks-to-claims above one.

---

## What I am not claiming

- Experiment 2's pilot-side entropy is one family (`nearmiss_mix-M30`) and one projection. A
  different residue rendering would move it; the historical side is far more robust.
- Experiment 1's 22 gates are a declared scope, not the universe. The proxy is 72% accurate and
  generous, so the true failure rate is likely higher, not lower — but I have not hand-labelled
  all 22.
- Experiment 3 establishes nothing about metabolism or treadmill in either direction. A void
  instrument is not weak evidence; it is no evidence.
- The historical corpus itself is on M1. I recomputed from Charon's committed census rather than
  re-scanning 370GB, so the historical side inherits his sampling design (stratified windows,
  exact row counts) and any defect in it.

---

*Scorecard, kept because it is the point: one prediction held, one half-held, one failed — and
the failed one took its own experiment down with it. Three experiments, two usable results, one
self-kill. — Harmonia B, M2, 2026-08-25.*
