# CAMPAIGN S — TERMINAL: **ADVANCE** (S1). 259 verified relations, and an honest name for what they are.

## 1. Independent re-verification — 80/80, zero failures

80 ledger pairs re-checked by operator implementations **written in the terminal script, not imported
from the scanner** — because importing the scan's own code path would reproduce its errors silently.
**80 of 80 matched exactly, including the recorded term count.** The counts are trustworthy.

## 2. Triviality audit — the measurement that decides what the 301 are

Run over **all 679 non-shift SB hit records**, not a sample:

    genuine_unstated    633  (93.2%)   ->  259 DISTINCT targets
    already_named        45  ( 6.6%)
    trivial / duplicate   1  ( 0.1%)

"Already named" means the relation is stated in words in one of the two OEIS titles — a title that
literally says *"Partial sums of A0…"* or names the partner. `names.gz` was read here; that is
adjudication, not blinded retrieval, and no retrieval decision depended on it.

## 3. A finding the audit forced, which weakens the campaign's own framing

**23.9% of the sampled targets have titles that name some A-number** (162 of 679). If a sequence's
title references another sequence in prose, that relation was recorded — the cross-reference
*extraction* simply did not capture it.

**So "zero-connectivity" means "no extracted OEIS xref", not "unreferenced".** The sleeping-beauty
framing is weaker than pass 1 assumed, and this is a property of the April dump's extraction rather
than of the mathematics. Reported because it cuts against the campaign's headline.

## 4. Branch adjudication

**S1 DISCOVERY fires.** `K_nonshift = 301` distinct zero-connectivity targets hit under a non-trivial
operator; 132 more reachable only by the trivial `shift` control and excluded from that count.

**The D-branch is DECLINED, not fired.** Pass 2 established that the control is selected on the very
quantity being measured — connectedness in OEIS is largely conferred *by* someone documenting a
relation, and a cross-reference is frequently the record of exactly the relation type this scan
searches for. No control breaking that selection relation is buildable from the data on hand.
`D = −0.0378, CI [−0.0406, −0.0350]` is reported **descriptively only**. Firing a contaminated branch
would have been worse than declining one.

## 5. TERMINAL: ADVANCE — and what it does and does not license

**What is established:** an exact operator sweep over 230,694 sources × 5 operators, completed in 4
seconds with a passing positive control, yields **259 distinct OEIS sequences with no extracted
cross-reference that satisfy a verified exact relation — holding over 20 to 45 terms — stated in
neither their own title nor their partner's.** Every one is recorded with full provenance in
`sb_candidate_relations.jsonl` (633 records, sorted by term count).

**What it does NOT establish, and I want this in the same breath:** that any of them is a discovery.
The top hit is `partsum(A001313) = A001305` over 45 terms, where A001305 is *"Expansion of
1/((1−x)²(1−x²)(1−x⁵)(1−x¹⁰)(1−x²⁰))"*. Taking partial sums corresponds to multiplying a generating
function by 1/(1−x) — a completely standard operation. Most of these 259 are almost certainly
relations a specialist would call obvious, unwritten only because nobody had occasion to write them.

**The honest name for the product is a machine-generated candidate set for human triage**, not a set
of findings. That distinction was committed in pass 1 — *"a hit is a verified exact relation, not a
claim that it is interesting or unknown"* — and the audit is what turns that caution into a measured
93.2% / 6.6% / 0.1% split rather than a disclaimer.

**Why ADVANCE rather than REDESIGN:** the method works and produced a usable artifact on its first
run, at a cost of seconds. The campaign asked whether exact search finds anything in the neglected
set. It does, at scale, verifiably. The next question — which of them matter — is a triage problem
for someone who knows the literature, not a search problem.

## 6. The product

`aporia/search/sb_candidate_relations.jsonl` — 633 verified records over 259 distinct targets, each
carrying source and target A-numbers with their OEIS titles, the operator, the offset, the exact term
count, a plain-language claim, and provenance. Status on every row: **CANDIDATE — verified exact, not
checked against literature.**

This is the first artifact this loop has produced that a mathematician could open and act on
directly. Six campaigns of the X-line produced method; this one produced a list.

## Campaign S TERMINAL: ADVANCE
