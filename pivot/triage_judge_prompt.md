# LLM-Judge Prompt — Promoted-Record Triage
**Use:** Paste this entire document into ChatGPT/Gemini/DeepSeek along with
the attached `promoted_triage_sample.jsonl`. The model returns labeled JSONL
lines that you paste back to Techne for calibration analysis.

---

## Background context (read once, then judge each record independently)

You're acting as an expert triage judge for a mathematical-substrate
discovery system called Prometheus / Theseus. The system generates ~3M
"records" per fire (24 min). Each record is a candidate mathematical
claim — typically a relation between an invariant of a knot and an
invariant of an elliptic curve (e.g. "determinant of knot 6_3
equal_mod_2 tamagawa_product of EC 6124.a1").

The system has accumulated **2351 "promoted" records over 136 fires**
(records whose `training_weight` exceeded 0.6). The team's worry: **these
might all be parity-coincidence tautologies, not findings**. A recent
internal triage showed 24.6% of disc-role records pass the 0.6 threshold,
which is suspiciously high; visual inspection of top-weighted records
shows lots of `equal_mod_2` ("are these both even?") and "X equal_mod_2
-X" (tautological reflection symmetry).

We changed `training_weight` to penalize weak relations (info-content
multiplier of 0.30 for `equal_mod_2`). This sample is a stratified
slice of **the OLD promoted-eligible set** — i.e. what the daemon
WOULD have promoted before the fix. Your job is to label these so we
can calibrate.

## Stratification (you may use stratum as a hint but don't let it
   bias your label)

- **S1_high_freq_template** (26): one per distinct high-frequency template cluster
- **S2_top_diverse_gens** (75): top info-density across diverse generator families
- **S3_random** (50): random promoted records
- **S4_rare_axis** (0): rare generator / claim-kind / domain-pair — empty (only 26 templates exist in the pile)
- **S5_verifier_weird** (25): REJECTED records with unusual kill_pattern

## The 6 labels (assign exactly one to each record)

For each record, output one of these labels. Use the definitions
strictly; when uncertain, prefer the more conservative label.

1. **`malformed`** — record is garbage (parse error, missing required
   payload fields, syntactically incoherent claim text)

2. **`trivial`** — claim is mathematically true but conveys no
   information. Examples:
   - "X equal_mod_2 -X" (tautology by construction)
   - "X abs_diff_le_K Y" where K is so wide both values trivially fit
   - "X equal Y" where X and Y are the same trivial value (0, 1)
   - Parity coincidence between random unrelated invariants (no
     mathematical reason for them to share parity)

3. **`valid-uninteresting`** — claim is well-formed and probably
   correct but the relationship is not informative for math research.
   Borderline trivial; saved if the relation surfaces something
   non-coincidental but pedestrian.

4. **`useful-negative`** — REJECTED record whose kill_pattern carries
   information about WHY the relation fails. Useful as a training
   negative for a learner because the falsification has structure.

5. **`candidate`** — claim that looks plausibly substantive: a non-
   trivial relation between non-trivial invariants. Would merit a
   second look from a domain expert.

6. **`verified-interesting`** — claim that you can recognize as
   matching a known nontrivial mathematical relationship (e.g. a known
   Langlands correspondence, a known modular form ↔ EC bridge, etc.).
   Use this label sparingly; if you're not sure it's a known result,
   use `candidate` instead.

## Output format

For each input line, emit ONE OUTPUT LINE in this exact JSON shape:

```
{"record_id": "<from input>", "label": "<one of the 6 labels>", "reason": "<one sentence>"}
```

Example:

```
{"record_id": "abc123", "label": "trivial", "reason": "X equal_mod_2 -X is tautological for integers under sign reflection"}
{"record_id": "def456", "label": "useful-negative", "reason": "REJECTED with F6_triggered shows specific boundary failure in modular reduction"}
```

Output the JSONL lines in the same order as input. Do not add
preamble or commentary outside the JSONL.

## Calibration anchors (use these to ground your judgment)

- The substrate has **0 verified mathematical findings** to date.
  Don't generate false positives by labeling ambiguous records as
  `candidate` or `verified-interesting`.
- The substrate's strongest known weakness is parity-tautology
  inflation (label `trivial`).
- A `candidate` should be something you'd actually want to send to
  a math researcher for verification — high bar.
- An `useful-negative` is a REJECTED record where the kill_pattern
  tells you something specific (not just "different values"). Generic
  kills are `trivial`.

---

Begin labeling now. Process each line of the input JSONL file.
