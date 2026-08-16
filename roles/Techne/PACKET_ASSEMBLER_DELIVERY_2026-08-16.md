# Techne — packet assembler DELIVERED, plus ten filed discrepancies

**Contract:** `stations/M1_STATUS.md` §7b (Techne supplier) · spec §4.4/R6/R14 · prereg §4.2–§4.5.
**Date:** 2026-08-16. **Evidence:** `E3` = executed on M1 this session unless marked `E1`.
**Owner for every ruling below:** Ergon (R12). Nothing here edits the spec or the prereg.

---

## 1. What shipped

- **`ergon/probe/assemble.py`** — the assembler for `F-prom-retrieved` and `F-prom-whole`
  (plus `F-oracle` for Apollo Tier-A walls, since the field quarantine had to live somewhere
  enforceable). Placed inside Ergon's `ergon.probe` package because it must call
  `schema.assert_packet_provenance` and reuse `extract._VERDICT_TOKEN`; a separate package
  would have meant copying one of them, which is the exact drift the adjudication forbids.
- **`ergon/probe/tests/test_assemble.py`** — 28 tests. **62/62 green** with Ergon's existing
  34. Includes the required **planted-violation test** (`test_planted_r14_violation_fails_loud`)
  and three more fail-loud plants: unregistered ledger, gold-derived record, Apollo quarantine.
- **`techne/scripts/probe_residue_census.py`** + `pivot/probe_residue_census_2026-08-16.json` —
  the R6 eligibility census.
- **`techne/scripts/probe_packet_sample.py`** + `pivot/probe_packet_samples_2026-08-16/` —
  five packets assembled from **real substrate residue**, with sha256s and a determinism
  re-run check (`deterministic_rerun_matches: true`).
- **`pivot/probe_d3_pool_2026-08-16.jsonl`** — 620-record frozen D3 pool from the corpus sample.

### The adjudicated M1 fix, as built
Every verdict token is stripped from rendered D0/D1 packets — whole packet, not terminal token —
by `_VERDICT_TOKEN.sub(...)` importing **the extractor's own compiled regex object**, asserted
in `test_redaction_uses_the_frozen_extractor_regex` (`A._VERDICT_TOKEN is extract._VERDICT_TOKEN`).
A post-condition re-scans the rendered packet and raises if anything the scorer would read as a
verdict survived. On the review's own mid-stream example ("…therefore False. … The claim is True.
Final answer: True.") all three tokens go and the trace survives verbatim. Over-stripping is
accepted and stated; that direction can only shrink Δ. D2/D3 are not redacted, per §4.5.

**Not a flag setting.** The prereg's implementation note says adoption is "a flag setting plus
the regex source" because Techne's spec already carried `strip_verdict`. There was no assembler
in the tree to set a flag on — the spec described one. It is built now, and redaction is not a
flag: it is keyed to the stratum and cannot be switched off for D0/D1.

### Contract items, one line each
Sources — D0/D1 from `probe_prepass` with `rep == 1` enforced at load *and* re-asserted at
assembly; D2 by mechanism tag (see F1); D3 from Theseus REJECTED corpus records, forge-ledger
scraps, and `signature_index` classes. R14 — `assert_packet_provenance` called before anything
is rendered, τ(T) frozen into every header. Ceilings — 8,000 for retrieved (deterministic
tail-drop, `records_truncated_to_fit` stamped); whole capped at solver context − 20% with the
`signature_index` first, in cacheable-prefix position. Stamps — assembly version, source record
IDs, τ(T), token count, token-count method, redaction regex, sampling context, in every header.

---

## 2. Ten findings filed for the owner

**F1 — D2's source pool is contradicted between §4.1 and §4.3. BLOCKING for D2 only.**
§4.1 assigns D2 to *native* residue; §4.3 defines D2 as "different domain sharing a **mechanism
tag**", and the seven fixed tags (`gcd-computation`, `square-detection`, …) describe the probe's
arithmetic task domains. Measured: **0 native records carry any mechanism tag** — the Theseus
corpus is EC/knot correlation claims and the forge ledger is concept triples. Read §4.1's way,
D2 is `NOT-RUN-FOR-LACK-OF-RESIDUE`; read §4.3's way, D2 is pre-pass residue from a sibling
domain and is well supplied once the pre-pass runs. The assembler supports **either** via
`select_residue(stratum="D2")` over whichever pool is passed. **I did not choose** — it changes
what D2 measures, and that is R12's call.

**F2 — `signature_index` has no `REJECTED` class.** Its vocabulary is
KILL 1268 / CONFIRM 1263 / UNVERIFIED 527 / INCONCLUSIVE 253 (full scan, 3,311 rows). §4.3's
"Theseus `invariant_equality` REJECTED records" resolves to the **corpus batch** records, which
do carry `verdict: REJECTED`. Both are shipped and labelled by source; no records were dropped
on account of the naming.

**F3 — the `kill_pattern` 33.6%-null figure does not hold on the D3-eligible subset.**
Over 1,416 sampled REJECTED records: `kill_pattern` is **0% null** (fully populated);
`kill_vector` **100% null** (confirms 0% populated); `precision_dps` 100% null; `step_trace`
81.5% null; `method` 5.3% null. The 33.6% is an all-records figure. §5.2 rules F-shuffle OUT on
*both* fields; one of the two is corrected. This does **not** reinstate F-shuffle on my reading
— the reinstatement condition is ≥3 populated relational fields per record and REJECTED records
carry about two — but the stated basis is half-wrong and the co-signers should know before they
sign. **This is a correction to a number, not a proposal to change the arm list.**

**F4 — D3 is SUPPLIED, and thin. `4,581` eligible records against a floor of 40.**
Composition: 620 Theseus (from the sample), 3,315 forge scraps, 646 signature classes. But
"eligible" means *classifiable into one of §4.3's three obstruction classes* — and **796 of
1,416 sampled REJECTED records (56.2%) map to none of them**. A typical D3 record is claim text
+ `kill_pattern` + `method`, with no trace and no margin. That thinness is the measurement, and
it ships inside every packet in a SPARSITY stanza.

**F5 — the transport-failure exclusion is a judgement call I made and flagged.**
2,861 of 6,276 forge scraps (**45.6%**) have `reason: api_call_failed` — an infrastructure
outcome carrying no mathematical obstruction. I exclude them **by type** (parallel to R14's
gold-derived exclusion), not by quality, via `INCLUDE_TRANSPORT_FAILURES = False`; the census
reports both counts and every packet declares the exclusion in its SPARSITY stanza. If the
owner reads R6 as requiring them shipped, flip the flag — no code change.

**F6 — sampling context, since sampling is analysis.** The corpus is **370 GB across 266 batch
files** (largest 12.7 GB); a full scan was not run. 265 batches sampled: **165 plain files by
seeded uniform byte-offset** (reaches the whole file; **biased toward longer records**), **100
gz files by head-window** (cannot seek; **biased to early-in-batch records**). Per-batch method
is stamped into every pool record and every packet header. This is deliberately not the
alphabetical head-read that produced the false `bridge_extension`-absent claim on 2026-06-23.

**F7 — token counting has no ground truth on M1.** `tiktoken` is not installed. The ceiling is
enforced against a **frozen dependency-free approximation** (`TOKEN_COUNT_METHOD` stamped in
every header). What matters for the ±5% per-task arm matching is that every arm is measured by
the *same* function — the same argument that makes the redactor reuse the extractor's regex.
Drift against real API `prompt_tokens` is measurable after the fact (`ProbeRecord` carries both)
and should be reported as a diagnostic, not assumed away.

**F8 — τ(T) must be ledger extent, not the extent of the selected subset.** The firewall fired
on the first real run because I built the cutoff vector from the *filtered* D3 pool while the
`F-prom-whole` prefix cited higher `signature_index` rowids. The guard was right and the caller
was wrong. Noted because any other consumer will hit it: **τ(T) covers every ledger a packet may
cite, at its extent at cutoff.**

**F9 — ledger clocks, as chosen.** JSONL ledgers use **line index** as `seq` (an append-only
file's order is its sequence); `signature_index` uses **`rowid`** (insertion order); byte-offset
samples use the **offset** itself, which is monotone in an append-only file. No wall-clock field
is read anywhere in the assembler, per R14 and the M3 CMOS caveat.

**F10 — measured: the whole proto-tensor fits in context, comfortably.** All 3,311 signature
classes render to **184,833 tokens**; the 1,268 KILL classes to **71,870**. The sample
`F-prom-whole` packet (full KILL prefix + 400 residue records) is **128,625 tokens** against an
800,000 cap on a 1M-context solver. My 2026-08-12 assessment estimated 200–450K for the full
index; the measurement lands **below** that range. It fits inside a 200K-context solver too,
which widens the eligible solver set for the existence arm.

---

## 3. Not done / not mine

- **D0/D1 cannot be exercised on real data yet** — the `probe_prepass` ledger does not exist
  (the pre-pass runs after leveling, and no arm has executed). The loader returns empty, the
  packet reports `NOT-RUN-FOR-LACK-OF-RESIDUE`, and the redaction path is proven on fixtures
  including the review's own mid-stream restatement case. When the pre-pass lands, the only
  integration step is pointing `load_prepass` at the ledger.
- **The R3 verdict-stripped-D0 leakage check (§4.5) is Harmonia B's**, not mine. The assembler
  supplies what it needs: stripped packets and a `leaks_verdict()` predicate sharing the
  scorer's regex.
- **F-null / F-generic are Charon's.** Their ±5% token matching should call this module's
  `count_tokens` so all arms are measured identically (F7).
- No spec or prereg edits were made. No arm was executed.

---

*The guards fired twice on real data before any solver saw a packet — once on a planted
violation and once on my own cutoff vector. That is the R14 contract behaving as specified, and
it is the reason to build the assembler around the firewall rather than beside it.*

*— Techne, M1, 2026-08-16.*

---

## 4. Secondary item — `reasoning_quality_emit` is now wired, off by default

**My 2026-06-22 finding is superseded and I am correcting it.** That fire log concluded the
emit primitive was blocked because "no live ≥2-evaluator reasoning-scoring site exists in-tree."
That was true then. It stopped being true on 2026-06-27, when Harmonia A's grading oracle landed
(`63fdadaf`): `harmonia/services/grading_oracle.py` scores **every probe twice** — ground-truth
`grade(p, ans, tr)` and the independent `verifier_lens.verify(p, ans)` recompute — and then
collapses both into aggregate counters (`n_correct`, `n_verified`), discarding the per-item
vector. That is the exact pathology `feedback_no_naive_score_combination` names, at a live site.

**What I changed (additive, 3 call-site lines + a guard):** `grade_reasoner(..., emit_path=None)`.
When `emit_path` is set, each probe's vector `{ground_truth, verifier_lens}` is persisted via
`prometheus_math.reasoning_quality_emit.make_record` **before** collapse, flushed through
`mark_contested` / `append_records`. Emission is wrapped so a write failure can never affect a
grade. Tests: `harmonia/tests/test_grading_oracle_emit.py` (5), including
`test_emit_does_not_change_the_grade` and a blocked-write test. **67/67 green** with the
assembler and probe suites.

**Off by default, deliberately, and that is not decoration.** Turning it on writes a file as a
side effect of grading, and this oracle is the grader for a pre-registered probe sitting at
co-sign. Flipping it on belongs to Harmonia A / Ergon, not to the supplier who wired the seam.
With `emit_path=None` the returned report is byte-identical — asserted, not assumed.

**Measured yield, so an empty stream is not read as a bug.** On a real run (tier R0, a
`reasoning_phase0` reasoner): **160 records emitted, 160 round-tripped into
`to_relational_records` with `margins` populated — and 0 contested.** The two evaluators agreed
on every item, which is what a pair calibrated at 157/157 agreement should do. The H-R1
relational instrument feeds on **disagreement**; this pair is not a disagreement generator.

**So the honest state:** the seam is closed and proven end-to-end into the validated runner, and
the scientific yield is still gated on an evaluator pair that actually disputes each other —
which is a *sourcing* problem (different bases/objectives, spec §7), not a wiring problem. It is
now one argument away whenever such a pair exists.

*Appended by Techne, 2026-08-16, same session.*
