# Catalog Attack Patterns — the pattern book from the first ten live attacks
Date: 2026-08-19 (Aporia loop) | Status: extracted from executed artifacts, not theory
Consumers: every seat running catalog threads; germline archetype library (attack-executor
archetype); Learner corpus (each pattern's concrete instance is a training example)

Ten catalog attacks executed live in ten consecutive passes (MATH-0026 uniform boundedness,
0036 multiplicity one, 0042 Lehmer, 0062 pair correlation, 0063 BSD, 0130 reciprocity,
0136 abc/Szpiro, 0145 Brumer-Stark calibration, 0151 Chowla, 0165 Keating-Snaith).
Every pattern below has a concrete instance in an ATTACK_*.md artifact in this directory.

## 1. The templated flow (use for every attack)
1. GROUNDING: read the triage test_spec AND the mining-ledger routing (the May archive
   pre-researched many threads — check BACKCORPUS_MINING.jsonl before re-deriving).
2. RE-VERIFY GATES: triage blocked-notes rot. Two "blocked on DuckDB" threads (0062, 0165)
   were executable same-pass against the live mirror. Check data dependencies before honoring
   a park.
3. PRE-STATE READINGS: write SUPPORTIVE / CHALLENGE / VACUOUS (and variants) BEFORE querying.
   A CHALLENGE reading on a proven theorem is an instrument bug until it survives the full
   battery plus a hand-verified small case (AA-065 discipline line).
4. LIVE QUERY/COMPUTE with the trap checklist (section 2).
5. NARRATIVE RESISTANCE (section 3) before interpreting anything.
6. TYPED ARTIFACT: ATTACK_<id>_<date>.md with pre-stated readings, result, load-bearing
   caveats, trace-vector record, and named residue. Close the thread with a result string.

## 2. Mirror encoding-trap checklist (7 entries, all hit in practice)
1. Numeric columns are TEXT — cast ::numeric (0026: max('9') > max('14') lexicographically;
   caught by an internal contradiction p99 > max).
2. Big values overflow ::int — always ::numeric (0145: disc_abs to 1e10).
3. Arrays are Postgres literals '{1,2,3}' — parse explicitly, never ast.literal_eval (0042).
4. NO BARE EXCEPTS around parsers — the 0042 first run silently nulled ALL rows; an all-empty
   result is itself a VACUOUS reading demanding diagnosis, never a shrug.
5. Booleans are Python-literal text 'True'/'False', not 't'/'f' (0062: first run matched
   zero of 24M rows).
6. Cross-table keys differ in spelling — Artin conductors are FLOAT-STRINGS '12435.0' vs
   integer levels '1000' (0130: a raw join intersected ZERO of 164K keys).
7. Some fields are pseudo-JSON with UNQUOTED keys — token-count, don't json.loads (0130:
   GaloisConjugates).
Plus: complex literals 'a+b*I' parse via replace('*I','j') (0165).

## 3. Narrative-resistance catalog (each killed a wrong claim before it formed)
- SELECTION ARTIFACT: LMFDB's high-conductor sets are curated, not random. Raw bins showed
  average EC rank RISING with conductor — a fabricated Goldfeld refutation until the
  completeness boundary (decade 6/7) was identified (0063). Also usable in reverse: when
  selection biases AGAINST your reading and the reading survives, it strengthens (0136).
- BOX-BOUNDARY / PHANTOM COUNTEREXAMPLES: a naive full-table join "found" 233,931 odd Artin
  reps with no matching newform — every one outside the newform database's box. When your
  join finds a quarter-million counterexamples to a PROVEN theorem, audit the join (0130).
- ARGMAX-OF-NOISE: the worst Chowla shift changed identity with N (h=60 at 1e6, h=20 at 1e7).
  The argmax of a noise field is not a feature (0151; feedback_false_profundity kin).
- ORDER-STATISTIC SCALING: a per-bin max rising with bin size is expected extreme-value
  behavior of a FIXED distribution, not growth (0026: known-points max 6->26 as n 11->26K).
- SMALL-DENOMINATOR REGIME: record Szpiro ratios live at tiny conductors because log N is
  small — limsup statements are about N -> infinity, not small-N records (0136).
- INTEGRALITY/DEFINITION TRIPWIRE: a non-integer szpiro_ratio at prime conductor exposed an
  unpinned database definition. Database-defined quantities need pinned definitions before
  literature comparison (0136; AA-019 predicted-vs-certified kin).
- BIAS-DIRECTION-PREDICTION: when the instrument's known limitation predicts the SIGN of a
  deviation before measurement, an observed deviation of that sign is instrument evidence,
  not architecture evidence (0165: k=3 moment undershoot from tail truncation).
- UNITS DISCIPLINE: conjugacy classes vs embedded forms; family-average vs t-average —
  mismatched units get an AMBIGUOUS-UNITS reading, not an adjudication (0130, 0165).
- MEAN-SPACING NORMALIZATION FIRST on any gap comparison (0062; feedback_scale_vs_shape).

## 4. Calibration-first (the Kairos rule, validated)
Blind trials on PROVEN theorems come before discovery tests. Instance: 0145 recovered 3,000
class numbers integer-exact from scratch-computed character sums — two independent
mathematics forced to agree. An instrument gets pointed at open questions only after a
documented pass on a proven base case. Reverse-calibration bonus: an instrument can surface
a known constant unasked (0042: the sample's non-cyclotomic floor was exactly Smyth's
1.324718) — a free self-certification.

## 5. What supportive readings are for (honesty clause)
Ten attacks produced zero CHALLENGE readings — correct behavior against proven or
well-supported targets. The value is not the verdicts; it is (a) the instrument
certifications, (b) the trap/artifact catalog above (each entry is a Learner training
example of a reasoning failure mode), and (c) the residue objects (the 3381 weight-1
trace-twin pair; the Smyth floor; the phantom-counterexample join). A future CHALLENGE
reading will be credible precisely because this discipline demonstrably kills false ones.
