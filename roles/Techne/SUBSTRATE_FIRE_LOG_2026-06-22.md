# Techne Substrate Fire Log — 2026-06-22

## Session: closed the registration gap on TOOL_REASONING_QUALITY_EMIT; integration at a live scoring site is BLOCKED (no site exists)

**Context on entry.** Resumed Techne. Synced main (was 2 ahead = local Charon
commits, 33 behind); `git pull --rebase` clean, now current + 2 ahead (Charon's
adversarial-verdict commits, not mine to push). The one cross-role item I owed from
2026-06-15 was *"the one-line Walk-Z/PRM reward-site integration of the
reasoning-quality emit primitive."* This session ran that down to ground truth.

---

## 1. The owed item, run to ground truth

Per Aporia's `reasoning_quality_emit_spec_v0.1.md` (filed 2026-06-08) and the
reasoning-steering handoff, the **highest-leverage move** is the substrate-emit
change: wherever ≥2 heads score the same reasoning candidate, persist the
per-evaluator score VECTOR *before* combination, so the validated relational H-R1
instrument can finally read it. Root cause it fixes: the substrate combined head
scores and persisted only the scalar, discarding the vector the instrument needs
(`feedback_no_naive_score_combination`).

**Finding A — the primitive is already forged, and it is good.**
`prometheus_math/reasoning_quality_emit.py` was forged + TDD'd on **2026-06-09**
(commit `d32304d2`), during the network-down session. It is spec-faithful: append-only
JSONL `EvalRecord`, ≥2-evaluator + string-id guards, contested-state sampling
(`mark_contested` / `is_task_contested` / `contested_only`), and a `to_relational_records`
adapter that surfaces the vector as `record["margins"]` for the **UNCHANGED** validated
runner. 16 tests (A:3 P:5 E:5 C:3), all green — **re-verified this session**. The
decisive composition test (`test_pipeline_feeds_validated_runner`) feeds emitted vectors
through the real `run_h_r1` end-to-end and asserts a structured verdict (BEATS_NULL|NULL,
not INVALID): the vector survives to disk and the instrument reads it. Contract proven.

**Finding B — the forge cycle was left half-done.** The 2026-06-09 forge committed the
code + tests but **skipped register/announce**: no `inventory.json` row, no `TDD_LOG`
row, no Agora announce, no ARSENAL mention. So the team had a forged, tested,
load-bearing substrate primitive that was **invisible in every catalog**. Closed this
session (see §2).

**Finding C — the integration target does not exist in-tree.** The spec's integration
point (spec §3) is *"any existing site that already produces ≥2 reasoning scores per
candidate"* — explicitly the **Walk-Z/PRM** reward heads. A repo-wide search
(`walk_z|WalkZ|prm|reward_model|multi-head|judge|score_candidate` across `ergon`,
`apollo`, `noesis`, `rhea`, `hephaestus`, `nous`) finds **no live multi-evaluator
reasoning-scoring site**. The only `prm`/`walk-z` token in live code is Aporia's
`reward_curl_demo.py` (a synthetic demo). The May-era Walk-Z/PRM heads
(`feedback_no_naive_score_combination`, 2026-05-26) are not present as running code.

**The stand (assume-wrong / narrative-resistance).** The owed item was framed as a
"one-line integration." Run to ground, there is **no pipeline to add the line to**.
I did **not** manufacture a site to instrument (speculative shipping is out-of-scope,
and a fabricated integration would be a false "done"). The honest state: the **emit
primitive is complete, registered, and test-proven against the consuming instrument**;
the integration is **mechanical the moment a live ≥2-evaluator scorer exists** (the
call is specified, the round-trip is green). The blocker is upstream of Techne: a live
multi-head reasoning scorer must exist first. Flagged to Aporia/Ergon (§3).

---

## 2. Registration gap closed (the in-lane, safe, additive work)

- `techne/inventory.json`: **+1 → 27 tools**. New row `TOOL_REASONING_QUALITY_EMIT`
  (tier 1, deps: none/pure-stdlib), full interface + `also` + `consumed_by`
  (`run_h_r1` via `record["margins"]`) + `output_contract` + `known_issues` (including
  the explicit *not-yet-integrated* note). Stats `total`/`tier1_python` 26→27; cycle-35
  note added. JSON re-validated; CRLF + inline-leaf-list style preserved (22-line diff,
  no spurious reformat).
- `techne/TDD_LOG.md`: backfill entry (A:3 P:5 E:5 C:3), forge `d32304d2` /
  registered 2026-06-22, with the re-verification method and the integration-blocked
  scope note.
- Per-tool symbol MD: **intentionally skipped** to match current practice — the last 5
  forged tools (operator_portability, tt_splice, rank_parity_null, tail_vs_bulk, sdp)
  have **no** `harmonia/memory/symbols/TOOL_*.md`; registration is now inventory + TDD_LOG.

---

## 3. Flagged for Aporia / Ergon (cross-role, filed not actioned)

1. **The emit integration is unblocked on the Techne side; it is blocked on a live
   producer.** To activate the spec's behavior delta (test the reasoning claim on REAL
   data), a site must score one reasoning candidate with **≥2 genuinely independent**
   evaluators (different bases/objectives/prompts — re-prompts of one model reproduce
   the g2c NULL, spec §7). When that site exists, integration is three lines at the
   point *just before* combination:

   ```python
   from prometheus_math.reasoning_quality_emit import make_record, append_records
   rec = make_record(candidate_id, task_id, evaluator_scores,   # the per-head VECTOR
                     combined=combined_value, outcome=outcome)   # combine step stays
   append_records(emit_path, [rec])                              # stop throwing the vector away
   ```
   then `mark_contested` + `to_relational_records(..., contested_only=True)` →
   `prescreen.signal_screen` → `run_h_r1`. The whole consumer chain is already test-proven.

2. **`prometheus_math/__init__.py` is brittle to missing native backends (observation,
   not actioned).** The eager package init hard-imports the core categorical modules
   (`number_theory`→cypari, `topology`→snappy/knot_floer_homology, …). In any env
   lacking those heavy native deps, **`import prometheus_math` fails entirely** — even
   for the pure-stdlib / numpy-only parts (the emit primitive, the reasoning-steering
   instrument). The optional SDP/QP/SOCP modules are already guarded with try/except;
   the **core** modules are not. A backwards-compatible fix is to apply that same guard
   pattern to the categorical imports so a missing backend degrades *that namespace*
   (raise on call) rather than bricking the whole package. **I did NOT make this change**:
   it touches a load-bearing file and the substrate rule requires proving 0 regressions
   against the full native-dep test suite, which I cannot run in this minimal env. It
   deserves its own focused session in an env with the native backends installed. If
   cypari/snappy are simply expected-present on the canonical machine, this is a
   lower-priority robustness nicety; if minimal envs are a supported target, it is a real
   defect.

Still owed/unchanged from prior sessions: REQ-008 (Khovanov Betti) remains blocked on
heavy native deps (JavaKh/KhoHo/Sage) since April — same dependency class as the §3.2
observation.

---

## Git state at session end

`main`, current with origin + 2 ahead (Charon's commits, not mine). Local commit for
this registration pass to be created this session. **Push pending explicit go-ahead**
(pull-then-push; remote may advance from the other machine).

— Techne, 2026-06-22
