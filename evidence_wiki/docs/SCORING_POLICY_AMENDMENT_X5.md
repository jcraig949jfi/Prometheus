# Scoring Policy Amendment (X5 precedent) — binding on FUTURE preregistrations

Trigger: in V3, tasks B2/B3 put one value in the answer field and a
different decomposition in prose notes ("537 lines / 534 unique"); the
frozen disjunctive criterion admitted the notes, and scoring by the letter
was correct but uncomfortable. This amendment prevents recurrence. It is
FUTURE-ONLY: V3 is not rescored and remains frozen under its original
criterion.

Every future PEW-controlled preregistration MUST specify, before any
execution output exists:

1. AUTHORITATIVE ANSWER FIELD(S). Exactly which field(s) of the output are
   scored. Everything else is non-scoring context by default.
2. MACHINE-READABLE REPRESENTATION. The exact type/format of the answer
   (e.g., JSON integer at $.answer), so scoring is parse-then-compare,
   never read-then-interpret.
3. NOTES PARTICIPATION. Whether prose/notes fields participate in scoring
   at all. Default: NO.
4. PRECEDENCE. When a structured answer and prose disagree, which wins.
   Default: the structured answer wins; prose can never rescue a wrong
   structured answer.
5. DISJUNCTIVE CRITERIA. Any criterion of the form "A or B" must enumerate
   the admissible sources for each disjunct. A disjunct satisfiable from a
   non-authoritative field is a design defect; fix it before freezing.
6. MALFORMED OUTPUT. Explicit handling for unparseable/missing answers
   (default: score 0 for that item, recorded as MALFORMED, never re-prompted
   or hand-parsed).

Objective: no post-output interpretive rescue, in either direction — neither
softening a miss nor promoting a hit found outside the authoritative field.

Enforcement point: prereg documents are checked against this list before the
gold/criteria freeze commit; a prereg missing any of the six items does not
freeze.
