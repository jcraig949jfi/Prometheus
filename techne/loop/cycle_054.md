# Cycle 054 — the catalog is sound, and cycle 053's finding was my error

Prereg `fd0fd693`, with a disclosure at the top: I read `_mahler_data.py`'s header **before**
writing the predictions, because it changes what may honestly be predicted.

## 1. Cycle 053's finding is RETRACTED — the error was mine

Cycle 053 reported: *"MAHLER_TABLE holds 8,625 entries while documenting itself as a snapshot
of Mossinghoff's ~178-entry list — the table is ~48x that."* I escalated it to James as a
finding, and noted that three of my own recent citations were downstream of it.

**It was wrong.** `_mahler_data.py`'s header documents the whole expansion, and has since
2026-04-29:

> *Loaded `Known180.gz` (the canonical Mossinghoff "M < 1.3 through degree 180" list, **8438
> polynomials**) ... appended after the original 178-entry Phase-1 curated section.*

**Mossinghoff's own canonical list is 8,438 entries, not 178.** The 178 was one curated
Phase-1 section of it. I took the *test's* docstring as the authority on what Mossinghoff
published and never opened the data module sitting one import away.

**This is the same failure as cycle 053's other correction, one layer up.** There I named a
function without importing it; here I characterised a data source without opening it. Both
times the *measurement* was fine and the *citation* was invented.

## 2. The provenance chain, verified against the artifact rather than the docstring

A docstring asserting its own provenance is not evidence for it. The bundled raw file is.

```
_known180_raw.gz            128,035 bytes, present
polynomial records          8,438        EXACTLY the header's claim
non-record lines            32           Mossinghoff's own header block, with
                                         "Michael Mossinghoff / Department of Mathematics"
M range in the raw list     1.176281 .. 1.299999
degree range                8 .. 180
```

**The arithmetic closes exactly:**

```
178 (Phase-1 curated)  +  8,438 (Known180)  +  9 (named literature)  =  8,625
```

and the residual 9 are individually named: **Sac-Épée 4, Idris/Sac-Épée 3,
Drungilas–Jankauskas–Šiurys 1, Hare–Mossinghoff 1.**

**KILL TEST PASSED: zero of 8,438 Known180 entries exceed their own M < 1.3 cutoff.** Had any
exceeded it, the table would have been *contaminated* rather than mislabelled, and every
conclusion drawn over "all 8,625 entries" — including my cycle-048 closure of HITL #266 —
would have needed re-examination. It did not fire.

**Verdict: the data is sound.** Every entry traces to a named source. My cycle-048
recomputation over all 8,625 stands, and so does the HITL #266 closure that rested on it.

## 3. What IS actually wrong — two stale docs, no bad data

- **`test_authority_mossinghoff_178_entries`** asserts 178 and has been red since the
  2026-04-29 refresh. It is a **stale test**, not a contamination detector — though it is the
  reason any of this got looked at.
- **`mahler.py`'s wrapper docstring** (prediction 5, held) still reads *"178 catalog entries ...
  Degrees 2..30 plus 36"* for a table holding 8,625 over degrees 2–180. The data module was
  updated; the wrapper above it was not.

**Not fixed this cycle, deliberately.** The prereg committed to not editing either until the
provenance was established. It now is — but "the test is stale, update it to 8,625" is a change
to an *authority* test, and after two cycles of my own citation errors I would rather propose
that than perform it quietly in the same cycle that cleared the data. Queued with the evidence
attached.

## 4. Predictions — 4 of 5, and the miss was reasoned backwards

The **difficulty axis** is new this cycle (cycle 053's trap: a clean sweep of already-understood
calls is not calibration evidence). All five below are tagged **OPEN** — none was determined at
write time.

- **P1 `moderate-to-high` OPEN — raw parses to 8,438: HELD**, exactly.
- **P2 `moderate` OPEN — arithmetic closes with a named residual: HELD**, 9 entries, all named.
- **P3 `moderate-to-high` OPEN — no Known180 entry exceeds M < 1.3: HELD.** The kill test.
- **P4 `low-to-moderate` OPEN — Phase-1 is a SUBSET of Known180: FALSIFIED.** Only **1 of 178**
  appears in both; they are essentially disjoint.
- **P5 `moderate` OPEN — the wrapper docstring is stale: HELD.**

**P4's rationale was backwards, and that matters more than the miss.** I wrote *"a SUBSET ...
so the table double-counts nothing."* If Phase-1 were a subset of Known180 and both sit in the
table, that **is** double-counting. Disjointness is the outcome that avoids it. I predicted the
wrong structure *and* attached reasoning that inverted the consequence, and only measuring
caught it. The disjointness has a clean cause: Phase-1 spans M ∈ [1.0, 1.84] including
cyclotomic and Pisot entries, while Known180 is capped at 1.3 — different territory by
construction.

## 5. Calibration, now with difficulty

```
band                 before    new     after   rate
high                    7/8    0/0       7/8   0.88
moderate-to-high        5/5    2/2       7/7   1.00
moderate               6/11    2/2      8/13   0.62
low-to-moderate         4/5    0/1       4/6   0.67
low                     0/3    0/0       0/3   0.00
TOTAL                 22/32    4/5     26/37  0.703
```

All five rows this cycle are `OPEN`, unlike cycle 053's five-for-five sweep on a `PRIOR`
mechanism — so these are worth more per row even though the hit rate is lower.
`moderate-to-high` is now 7/7 and `low` remains 0/3; `low-to-moderate` (0.67) and `moderate`
(0.62) have converged rather than separated. **Not claiming H1a.**

## TLDR — ELI5

**I raised an alarm last cycle. It was a false alarm, and the fault was mine.**

I reported that a data table claiming to be a copy of a mathematician's published catalogue was
48 times too big — and flagged that I'd cited it three times myself. Today I opened the file
that builds the table. It explains everything, and has since April: the catalogue really does
have **8,438** entries. The number I'd called "his published list" — 178 — was one curated
slice of it, and I'd taken that figure from a *test's* comment rather than from the data.

So I checked the whole chain properly, against the actual compressed file rather than anyone's
description of it. It contains exactly 8,438 polynomials, with the mathematician's own name and
department in its header. The arithmetic comes out exactly: 178 + 8,438 + 9 individually-named
extras = 8,625. And the important safety check — every entry in his list must be below the
cutoff his list is defined by — passed on all 8,438. **The data is fine.**

What's actually wrong is boring: two comments that were never updated when the table legitimately
grew in April. One of them is the failing test that made me look, which is the only reason any
of this was checked at all.

**Same mistake as last cycle, one level up.** Last cycle I named a function without importing
it. This cycle I described a data source without opening it. Both times the numbers I measured
were right and the *label* I put on them was made up.

## For ChatGPT

```
Prometheus loop, cycle 054. I RETRACT CYCLE 053'S FINDING. THE CATALOG IS SOUND AND THE ERROR
WAS MINE.

*** THE RETRACTION ***
Cycle 053 reported: "MAHLER_TABLE holds 8,625 entries while documenting itself as a snapshot of
Mossinghoff's ~178-entry list -- 48x". I escalated it as a finding. IT WAS WRONG.
_mahler_data.py's header has documented the whole expansion since 2026-04-29: Known180.gz, "the
canonical Mossinghoff M<1.3 through degree 180 list, 8438 polynomials", appended after the
original 178-entry Phase-1 curated section. MOSSINGHOFF'S OWN LIST IS 8,438, NOT 178. I took
the TEST's docstring as the authority on what he published and never opened the data module one
import away.
SAME FAILURE AS 053'S OTHER CORRECTION, ONE LAYER UP: there I named a function without
importing it; here I characterised a data source without opening it. Both times the MEASUREMENT
was fine and the CITATION was invented.

*** THE CHAIN, VERIFIED AGAINST THE ARTIFACT NOT THE DOCSTRING ***
  _known180_raw.gz      128,035 bytes, present
  polynomial records    8,438  EXACTLY the header's claim
  non-record lines      32     Mossinghoff's own header, with his name and department
  M range               1.176281 .. 1.299999      degrees 8..180
ARITHMETIC CLOSES EXACTLY: 178 (Phase-1) + 8,438 (Known180) + 9 (named literature) = 8,625.
The 9 are individually named: Sac-Epee 4, Idris/Sac-Epee 3, Drungilas-Jankauskas-Siurys 1,
Hare-Mossinghoff 1.
KILL TEST PASSED: ZERO of 8,438 Known180 entries exceed their own M < 1.3 cutoff. Had any
exceeded it the table would be CONTAMINATED rather than mislabelled, and every conclusion over
"all 8,625 entries" -- including my cycle-048 closure of HITL #266 -- would need re-examination.
VERDICT: DATA IS SOUND. Every entry traces to a named source. Cycle 048's closure stands.

*** WHAT IS ACTUALLY WRONG: TWO STALE DOCS, NO BAD DATA ***
test_authority_mossinghoff_178_entries is a STALE TEST, red since the April refresh -- though it
is the only reason any of this got looked at. mahler.py's wrapper docstring (P5, held) still says
"178 catalog entries, degrees 2..30 plus 36" for a table of 8,625 over degrees 2-180. NOT FIXED
this cycle: the prereg committed to not editing either until provenance was established, and
after two cycles of my own citation errors I would rather PROPOSE an authority-test change than
perform it in the same cycle that cleared the data.

*** PREDICTIONS 4 OF 5, ALL TAGGED "OPEN" (new difficulty axis) ***
 P1 mod-high  raw parses to 8,438              HELD exactly
 P2 moderate  arithmetic closes, named residual HELD, 9 entries all named
 P3 mod-high  no entry exceeds M < 1.3          HELD -- the kill test
 P4 low-mod   Phase-1 is a SUBSET of Known180   FALSIFIED, only 1 of 178 in both
 P5 moderate  wrapper docstring is stale        HELD
P4'S RATIONALE WAS BACKWARDS AND THAT MATTERS MORE THAN THE MISS. I wrote "a SUBSET ... so the
table double-counts nothing". If Phase-1 WERE a subset and both sit in the table, that IS
double-counting; DISJOINTNESS is what avoids it. I predicted the wrong structure AND inverted
the consequence. Clean cause: Phase-1 spans M in [1.0, 1.84] with cyclotomic and Pisot entries,
Known180 caps at 1.3 -- different territory by construction.

CALIBRATION 26/37 = 0.703: high 7/8 | mod-high 7/7 | moderate 8/13 = 0.62 | low-mod 4/6 = 0.67 |
low 0/3. All five rows this cycle are OPEN, unlike 053's five-for-five on a PRIOR mechanism, so
they are worth more per row despite the lower hit rate. low-to-moderate and moderate have
CONVERGED rather than separated. NOT CLAIMING H1a.

What I want attacked:
1. Two cycles running, my error was a citation rather than a measurement. Is there a check that
   catches "I described a source I never opened" other than always opening it?
2. The kill test passed, so I concluded the data is sound. But I verified Known180 against
   ITSELF (its own cutoff). What would independently confirm the bundled gz is really
   Mossinghoff's, given the live host is DNS-unreachable?
3. I falsified P4 and my rationale for it inverted the consequence. Should a prereg require
   stating what the OPPOSITE outcome would imply, to catch inverted reasoning before measuring?
```

## Traps ledger additions

- **Citing a data source without opening it.** I characterised Mossinghoff's list from a test's
  comment. Defence: an authority claim about a dataset must be checked against **the dataset's
  own build module or raw artifact**, never against a third file's description of it.
- **A prediction whose rationale inverts its consequence.** P4 predicted "subset, so no
  double-counting" when subset *is* double-counting. Defence: state what the **opposite**
  outcome would imply before measuring — an inverted rationale survives only while both
  branches go unexamined.
- **Verifying an artifact against itself.** The kill test checked Known180 against Known180's
  own cutoff. That detects internal inconsistency and cannot detect a wholesale substitution.
  Defence: name explicitly which failure modes a self-consistency check can and cannot see.
