# Counterexamples discovered — Master Smith session 20260901T073136Z, MINT-0001 (vacuous_truth)

Candidate of record: `candidates/v3_quantified_truth.py` — `PASS_DEV` (holdout 1.00, boundary
false-commit 0, four input-mutant falsifiers 8/8 · 8/8 · 80/80 · 8/8). Everything below is where it
**breaks or is untested**. Nothing here was taken from Charon's E9 battery.

## 1. Out-of-template phrasings (cycle 4): 4 / 20 correct, **0 false commits**, 16 abstentions

v3 never guessed. It abstains whenever a premise or claim falls outside the surface forms it knows.
The kernel is general; the parser is template-bound. Failure positions:

| id | phrasing that defeated the parser | gold | v3 |
|---|---|---|---|
| A1 | "There aren't any green bottles **on** the wall" (idiom + `on` container) | yes | abstain |
| A2 | "**Zero** silver coins are in the chest" | yes | abstain |
| A3 | "The chest **has no** silver coins" | no | abstain |
| A4 | "The pond is **empty of** frogs" | yes | abstain |
| A5 | "No frog **lives in** the pond" (verb, not copula) | yes | abstain |
| B1 | "**Is it true that** every red marble in the jar is chipped?" (no "Consider the claim:") | yes | abstain |
| B2 | "**Claim:** every … **True or false?**" | yes | abstain |
| B3 | "every **one of the** red marbles" | yes | abstain |
| B5 | "any red marble in the jar **that is** chipped is **also** heavy" (restrictive relative) | yes | abstain |
| B6 | "**there exists** a red marble in the jar that is chipped" | no | abstain |
| C1 | "The jar holds 6 red marbles**;** 2 are chipped" (no "of them") | no | abstain |
| C2 | "and **none of them** are chipped" | yes | abstain |
| C3 | "and **all of them** are chipped" (no count) | yes | abstain |
| C4 | "and **two** of them are chipped" (number word) | no | abstain |
| D1 | "no chipped marbles … 6 red marbles … 2 of them are heavy → every red marble is chipped" | no | abstain (predicate 'chipped' asserted empty as a *set*; v3 has no rule for predicate-set emptiness) |
| D2 | "… 3 blue marbles … **1 of them is** chipped" (singular copula) | no | abstain |

Passed: B4 ("all of the"), C5/D3/D4 (correct abstentions when premises carry no information).

**Reading:** each row is a parser hole, not a kernel hole — with one exception. D1 needs a rule the
kernel lacks: *the predicate's extension is empty* ("no chipped marbles") implies "every X is chipped"
is false whenever the X-domain is non-empty. That is a fourth kernel rule, not a template.

## 2. Component decorative on the dev set (cycle 5)

`P4 cardinality reader ignores predicate` — Δ = 0.000 on the 80-item holdout. The check "does the
'k of them are P' clause talk about the claim's predicate?" is never exercised because the dev set has
no item of the form "exactly k X, and j of them are Q" with Q ≠ claim predicate. Semantically the
check is right (without it the op would answer a question about the wrong predicate). **Owed to the
wall by the apprentice side:** a `NONEMPTY_OTHER_PREDICATE` kind (gold = abstain), which also makes D1
representable.

## 3. Defects found in my own process (recorded because they cost a cycle each)

- Cycle 2: generating a candidate through a string template turned `\b` into a literal backspace
  byte; the candidate silently never stripped the container. Rule: write candidates directly.
- Cycle 1: splitting the domain at the *first* " in " broke every domain whose noun phrase contains
  "in" ("letter written in Latin"). The container is always the *last* " in ".

## 4. What would falsify the candidate as a *mechanism* rather than a parser

Give it the same 88 items with the parser replaced by hand-supplied `(quantifier, |domain|,
|satisfiers|)` tuples and it will score 88/88 — the kernel is three rules. Give it any phrasing outside
the eight emptiness idioms, six claim forms and two cardinality forms, and it abstains. The honest
label is therefore: **kernel = candidate primitive (`quantified_truth`); parser = template adapter,
Level 0.** Whether the kernel is a Level-2 extension of the frozen operator set is for the closure
certificate to say, not for me.
