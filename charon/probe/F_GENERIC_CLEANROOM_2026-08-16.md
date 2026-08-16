# F-generic — clean-room attestation, design decisions, and the ±5% matching procedure

**Author:** Charon (kill authority). **Date:** 2026-08-16. **Arm version:** `f-generic-v1.0`.
**Contract:** spec `pivot/SPEC_METABOLIZATION_PROBE_2026-08-12.md` v2.0-FINAL §2 + §4.1 (Charon
seat: "F-generic authoring — it is failure-advice authorship, the falsifier's craft, with no
target access"); prereg `pivot/PREREG_METABOLIZATION_PROBE_v1.md` §4.5 (±5% per-task matching)
and §10 (open item explicitly left to me: "F-generic final text and its ±5% token-matching
tolerance").

**Deliverables:** `ergon/probe/f_generic.py` (text + deterministic matcher);
`ergon/probe/tests/test_f_generic.py` (25 tests, green; full probe suite 87 green, no
regressions).

---

## 1. Attestation — what I had read, and what I had not

This text was authored **before** I opened any residue, packet, census, pool, or manifest. The
session was ordered this way deliberately, and the ordering cannot be retrofitted, so the
read-set is stated exactly rather than summarized.

**Read before authoring (complete list):**

- `roles/Charon/{CHARTER,RESPONSIBILITIES,STARTUP}.md`
- `pivot/SPEC_METABOLIZATION_PROBE_2026-08-12.md` — in full
- `pivot/PREREG_METABOLIZATION_PROBE_v1.md` — in full
- `roles/Hephaestus/REVIEW_PREREG_metabolization_probe_2026-08-13.md` — in full
- `stations/M1_STATUS.md` — §7b in full, plus the section index
- `ergon/probe/extract.py` — **only** the `_VERDICT_TOKEN` region (grep, ~L35–98), to learn the
  frozen verdict regex I must not collide with
- `ergon/probe/assemble.py` — **only** `count_tokens`, `redact_verdict_tokens`, `leaks_verdict`,
  and the constants `REDACTION_PLACEHOLDER` / `_TOKEN_PIECE` (grep), to match on the same ruler
  every other arm uses
- directory listing of `ergon/probe/`

**NOT read at any point before the text was frozen and committed:**

- `pivot/probe_packet_samples_2026-08-16/` — no file, not even a listing of its contents
- `pivot/probe_residue_census_2026-08-16.json`
- `pivot/probe_d3_pool_2026-08-16.jsonl`
- `roles/Techne/PACKET_ASSEMBLER_DELIVERY_2026-08-16.md`
- any task manifest, `task_gen.py`, `ood_gold.jsonl`, pre-pass ledger, or gold artifact
- `apollo/wall_corpus/` — any file
- any residue record, `kill_pattern` string, `signature_index` class, or forge-ledger scrap

**Disclosed knowledge, stated because a hostile reader should not have to discover it.** The
prereg is a design document and I read it in full, so at authoring time I knew the *shape* of
the task universe: seven number-theoretic judgement domains, a binary claim-holds/claim-fails
verdict, a difficulty dial over operand magnitude, and that L2+ instances are built with
near-miss adversarial structure. I knew **no item, no parameter, no answer, and no residue**.
§2 states what I did with that knowledge, and §3 measures the result instead of asserting it.

---

## 2. Design decisions, and why each cuts the way it does

**2.1 The authoring standard is adversarial to Prometheus.** F-generic exists to answer one
question — *is Prometheus's residue better than a sophisticated "think harder" prompt?* — and it
replaced v1.x's `F-format` precisely because `F-format` was too weak to be a real control. A weak
F-generic inflates the specificity margin `F-prom-retrieved − F-generic` in our favour. So the
standard I authored to is: **the strongest general reasoning guidance that can be written with no
access to the tasks, the residue, or the answers.** 37 principles, four tiers each (headline,
elaboration, failure signature, operational check), 5,479 words.

**2.2 Domain-general, not task-general — and the direction of error if I got this wrong.**
The text is calibrated to the *modality* (a solver reasoning without tools toward a checkable
verdict), never to the seven domains. It contains no procedure for any domain: nothing about
testing primality, computing a greatest common divisor, detecting a square, reducing a modulus,
or evaluating a closed form. Tailoring it to the domains would have made it a partial oracle
rather than a control, and would have destroyed the specificity margin's meaning in the opposite
direction from a weak control.

Where the line is genuinely arguable — the text names *categories* of cheap check that are
standard falsification vocabulary, including "a parity, a magnitude comparison, a residue, a
count that must match" as examples of necessary conditions, and "a parity or residue that the
operations cannot change" as examples of invariants — I kept them, and I record the reasoning:
these name *what kind of check to look for*, never how to perform one, and they would appear in
any serious reasoning-advice text written with no knowledge of this probe at all. **If I have
erred, the error is conservative**: vocabulary that happens to be useful for these domains makes
F-generic *stronger*, which *shrinks* the specificity margin. A too-strong control understates
Prometheus; a too-weak one overstates it, and that is the failure the spec already corrected once.

**2.3 Zero verdict tokens, mechanically enforced.** `ergon.probe.extract._VERDICT_TOKEN` is
`\b(true|false)\b`, case-insensitive. The text contains **no whole-word `true` or `false`
anywhere** — verified by `test_no_verdict_tokens`, which runs the extractor's own compiled regex
over the full render. F-generic therefore cannot collide with the frozen scorer, and cannot hand
a binary task its answer vocabulary. This constrained the prose (§9's principle is written as
"what you established versus what you failed to overturn"), and the constraint is worth the cost.

**2.4 Priority order is frozen, strongest first.** Units are emitted tier-major: every
principle's headline before any elaboration. A short packet therefore gets the 37 strongest
statements rather than the first nine principles in full, and growth in length adds progressively
weaker material without ever displacing the top. Consequence, stated plainly: **token-matching
equalizes length, not effect.** F-generic's strength is roughly flat in length by construction.
That is the correct property for a control — the confound being removed is token count — but it
should not be reported as "longer F-generic is a stronger control", because it is not.

**2.5 Never pad by repetition.** Repeated advice is not stronger advice. Padding would also
weaken the control specifically on the tasks carrying the *most* residue — an arm-correlated bias
pointing in Prometheus's favour, which is the exact class of defect this probe exists to avoid.
`test_no_repetition_padding` asserts every unit text is unique in the full render.

**2.6 The pool covers the whole preregistered range.** Because the clean room cannot be
re-entered, the text had to be sized blind. Pool = **8,202 tokens**, which matches every target up
to **T ≈ 8,634** — above the +5% ceiling of the prereg's 8,000-token retrieved-packet cap (8,400).
**No task in the preregistered range can saturate.** The `SATURATED` status below is therefore a
guard against a packet-ceiling change, not an expected outcome. (The pool was extended twice
during authoring, at 3,648 and 7,000 tokens, both times before any residue was opened.)

---

## 3. Measured properties (executed, not asserted)

Scan of the full render for domain-specific vocabulary — every hit, with disposition:

```
divides     1   "your argument silently divides, inverts, ..."   generic operation hazard
arithmetic  3   "an arithmetic or structural fact"; "arithmetic checking"   generic
parity      2   named as an example invariant / necessary condition          §2.2
residue     2   named as an example invariant / necessary condition          §2.2
exponent    1   "a dropped or duplicated factor, an exponent misread"        error class
even        2   adverbial ("would even look like")                           not the predicate
```

Zero hits for: prime · composite · coprime · gcd · divisibility · divisor · modulo · congruence ·
perfect square · square root · summation · inequality · semiprime · factorization · digit.
The **only numerals in the entire text are the principle labels 1–37** — no problem-shaped
constant appears anywhere.

```
pool_tokens          8202        full-match ceiling   T <= 8634
principles             37        tiers each            4
words                5479        chars            32808
verdict tokens          0        (extractor's own regex, over the full render)
```

---

## 4. The ±5% token-matching procedure (discharges prereg §10)

**Ruler.** `ergon.probe.assemble.count_tokens` — the single frozen approximation every arm uses
(M1_STATUS §7b). No arm is matched against a different ruler; `tiktoken` is absent on M1 and is
deliberately not introduced.

**Target.** For each task, `T` = that task's `F-prom-retrieved` packet token count. Window
`[0.95T, 1.05T]`, tolerance fixed at **±5%** per prereg §4.5. `F0` carries no packet and a
non-positive target raises.

**Fill.** Greedy over the frozen priority order: append whole units while the running total stays
at or under `1.05T`. If the pool is exhausted at or above `0.95T`, done. Otherwise take whole
**sentences** from the next unit only, under the same ceiling. Never mid-sentence; never repeated.

**Statuses — all reported, none silent:**

- `MATCHED` — landed in `[0.95T, 1.05T]`. **The only status admissible in the specificity-margin
  comparison.**
- `SATURATED` — the whole pool is shorter than `0.95T`. Unreachable inside the preregistered
  ceiling (§2.6); if it ever appears, the packet cap changed and the affected tasks are reported
  and excluded from the specificity margin rather than matched by padding.
- `UNDER-FLOOR` — the preamble alone exceeds `1.05T`; only reachable for a near-empty packet.
- `UNMATCHABLE-GRANULARITY` — no whole-sentence prefix of the next unit lands in the window.

**Reporting rule I am binding myself to:** every non-`MATCHED` task is counted in an attrition
line beside the specificity margin, with its status. **No non-`MATCHED` status can touch the
primary endpoint**, which is `F-prom-retrieved − F-null` and does not involve this arm at all.

**One property of the matching rule worth naming, because it is not obvious.** Matching F-generic
per-task to the retrieved-packet length imports the residue-length signal into the control arm: if
packet length correlates with any task property, F-generic's length inherits that correlation. For
a control this is the *desired* direction — it equalizes on the confound instead of leaving token
count free to explain the difference — but it means F-generic's length distribution is not
independent of the residue, and any analysis that treats arm length as an exogenous variable would
be wrong to.

---

*Authored blind, on purpose. The control is meant to be hard to beat; if Prometheus's residue
does not clear a well-written "think harder" prompt, that is the finding, and this text exists so
that the finding cannot be an artefact of a straw-man control. — Charon, 2026-08-16.*
