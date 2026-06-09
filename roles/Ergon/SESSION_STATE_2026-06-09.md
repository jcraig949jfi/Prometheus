# Ergon — session state & resume point (2026-06-09)

Single "resume here" doc. Written before a machine reboot (clearing network
errors). Nothing below is lost on reboot — all committed locally + on disk.

## GIT — the one thing to do after reboot

- Branch `main`, **49 commits ahead of `origin/main`, 0 known behind**. Working tree
  **clean** (only `theseus/handoff/ergon_outbox/quarantine_20260607/` left on disk on
  purpose — junk d2 placeholder bundle, do not commit).
- **Push is blocked: github.com is unreachable from this machine** (TCP connect timeout
  on :443 AND :22, with and without sandbox). HuggingFace + raw.githubusercontent work;
  github.com / api.github.com do not. Environmental (firewall/VPN/DNS), not auth/repo.
- After reboot, when github.com is reachable, sync with **pull-then-push** (remote may
  have advanced from the other machine → avoid non-fast-forward rejection):
  ```
  git pull origin main
  git push origin main
  ```
- Last local commit: `781fe2e9` (cross-role catch-all checkpoint).

## ENVIRONMENT (verified this session)

- Python with torch+CUDA: `C:/Users/jcrai/AppData/Local/Programs/Python/Python311/python.exe`
  (torch 2.11+cu128; the default `python` is 3.12 with NO torch). sympy 1.14 present.
- Model: local Qwen2.5-Math-1.5B-Instruct under `E:/hf_cache/hub` (rig auto-resolves).
- RTX 5060 Ti; LoRA rank-16 run ≈ 10 min. PARI prints stack-size noise on import (ignore).
- Network: github.com blocked; HF + raw.githubusercontent reachable.

## WHAT HAPPENED THIS SESSION (2026-06-07 → 06-09)

Role: Ergon (the Learner march). Three connected pieces, all committed:

### 1. Greedy-LoRA follow-up — the kill (committed 996d8186)
Four tasks (ablation, real OOD number, transfer test, handoff un-stall). Result:
the greedy LoRA's "+0.68" decomposes into **format ≫ False/kill prior ≫ per-template
classes ≫ reasoning**, with **no cross-domain transfer**. Failure-reasoning sources add
~0 to the metric. Real OOD ≈ chance (prior-driven). Handoff: fixed the stall root cause
(unbounded 346GB walk → bounded to newest-N batches), raised falsify floor 0.20→0.40,
and found the deeper monoculture cause — the `training_anchor` mapper renders ONLY
`invariant_equality`, so all other kill kinds become garbage; it's now gated to ship
nothing-or-clean. Docs: `GREEDY_FOLLOWUP_FINDINGS_2026-06-07.md`, `..._PROGRESS_...md`.

### 2. Training-data expansion survey (committed 594cdfcb)
5-subsystem survey. Governing principle from the kill: shape completions as WORKED
TRACES (not verdicts), target computation, keep gold computed. Tiers:
- T1 (build first): prometheus_math test suites + databases + cartography battery
  cascades = computation ground truth.
- T2: Theseus `step_trace` retrofit, OEIS programs, Nous syntheses.
- T3: Hephaestus failure-mining (+32pp proof) & Apollo lineage = routing signal —
  but needs a routing eval first.
Doc: `TRAINING_DATA_SURVEY_2026-06-07.md`.

### 3. Computation-trace experiment (committed 9955237c)
Built the Tier-1 computation-trace corpus (`compute_traces.py`, 8 ops, gold-checked,
reason-first WORKED completion vs no-work ablation; hard negatives after an adversarial
self-catch of a v1 parity leak). Result:
- **In-op held-out (excl. leaky gcd): work 0.78 vs no-work 0.61, +0.16** — showing the
  derivation teaches the model to compute the TRAINED ops on new instances.
- **Cross-op transfer: work ≈ no-work (~0.62); summation still unsolved (~0.45)** — no
  transferable computation. modexp ~0.52 even with traces = 1.5B capability ceiling.
- Refines the kill: **lever is COVERAGE (many ops × traces), not transfer**; harder
  procedures need a bigger model. Falsifiable prediction partially FALSIFIED.
Doc: `COMPUTE_TRACE_RESULT_2026-06-08.md`. Memory: `feedback_greedy_lora_surface_not_reasoning.md`.

## NEXT MOVES (planned, not started)

Two clear directions; James to pick (offered at session end). Both are local-only work.

1. **Scale the coverage** — build a BROAD computation-trace corpus from the Tier-1
   survey sources: `prometheus_math/tests/test_*.py` (property/composition tests =
   verified input→output→why over 24+ ops) + `prometheus_math/databases/*.json.gz`
   (genus2 6K, modular_forms 7.8K, bsd_rich 1K) + cartography battery cascades (F15–F24
   multi-test chains). Many ops × worked traces, possibly a larger adapter (rank↑), then
   re-run the in-op + cross-op evals to test whether broad coverage starts to transfer.
   Rationale: the compute-trace result says per-op worked training works; coverage is the
   untested lever. Reuse `compute_traces.py` op-spec pattern + `eval_greedy.py --cot`.

2. **Build the routing eval** — the Learner's ACTUAL objective (predict productive search
   moves / route by failure) has NO eval; every result so far is on the narrow gold-
   judgement metric. Seed: Hephaestus `agents/hephaestus/failure_mining_results.json`
   (`wrong_probes_solved` per scrap) + the +11pp/+32pp failure-mining result — it already
   pairs "mined failure → which problems it now solves." This is the deeper gap and the
   only thing that tells us if any of this serves the north star.

My recommendation when work resumes: do (1) first (cheap, directly extends a positive
result, falsifiable), but (2) is the higher-strategic-value gap. Defer to James.

## OPEN THREADS / CAVEATS

- gcd retains an intrinsic shortcut (answer must divide inputs → cheap divisibility check),
  so gcd no-work cheated (0.98); excluded from headline. Other ops are clean.
- modexp / multi-step modular procedures exceed 1.5B reliable generation — capacity, not data.
- Handoff still can't ship useful failure data until Theseus-side fixes land: (a) port the
  greedy per-claim_kind serializers into the `training_anchor` mapper; (b) recalibrate
  `training_weight`/threshold so `invariant_equality` kills clear the bar (they score ~0.2).
  These are Theseus's lane (flagged in the progress doc).
- The 781fe2e9 catch-all includes Theseus's in-flight predicate_kind v3c calibration — if
  Theseus wants to recommit it with their own context, it can be reset (`git reset`) before push.

## TASK LEDGER (this session)
All 6 tasks completed: ablation · OOD · Charon/transfer · handoff · compute-trace builder ·
trace-vs-verdict experiment.

— Ergon, 2026-06-09
