# API preflight — live reachability & latency measurement for the Metabolization Probe

**Role:** Ergon (driver, spec R12). **Date:** 2026-08-13. **Evidence class:** `E3` — every
number below was executed on M1 this session, not cited.
**Trigger:** James: *"Verify that the NVIDIA models work via the API. We've had problems with
them in the past where they time out."*
**Verdict:** the concern is **confirmed and still live — but it is per-model, not endpoint-wide.**
Four models serve reliably under a realistic packet payload; the rest fail in four distinct ways.

Harness: `scratchpad/api_probe.py` (stdlib `urllib` only — no global installs). Raw per-trial
records: `api_probe_results.jsonl`. Keys read via the `.env` fallback; values never printed.

---

## 1. Method

Two payload sizes, because packet size is the variable that actually matters for this probe:

- **small** — one probe-shaped judgement task (`"8566 and 907 are coprime — True or False?"`),
  ~40–103 prompt tokens. 2–3 trials per model.
- **big** — the same task preceded by ~16K tokens of synthetic residue text, standing in for an
  `F-prom-retrieved` packet. This is **2× the 8,000-token packet ceiling** in prereg §4.5, so a
  pass here is conservative.

`max_tokens=64`, `temperature=0.0`, no retries, no streaming. Timeout 90s (round 1) / 60s
(round 2) — a solver needing longer than that for a 64-token verdict is unusable at 2,800 calls
regardless.

## 2. Results — admissible solvers

All four passed every small trial **and** the 16K-token payload:

```
model                                       small latency   16K payload   family
deepseek-ai/deepseek-v4-flash-0731          2.3 - 5.2s       1.7s         DeepSeek
nvidia/llama-3.3-nemotron-super-49b-v1      2.5 - 4.3s       8.5s         NVIDIA / Nemotron
nvidia/llama-3.3-nemotron-super-49b-v1.5    1.8 - 6.2s       7.7s         NVIDIA / Nemotron
openai/gpt-oss-120b                         1.4 - 8.7s      23.1s         OpenAI (open weights)
```

`deepseek-v4-flash` being *faster* on 17,270 input tokens (1.7s) than on 40 (2.3–5.2s) is
cold-start noise on the small calls, not a payload effect — consistent with the NVIDIA
cold-start behavior Harmonia logged on 2026-06-05.

**Consequence for the prereg:** R2 requires ≥2 solvers from **different families**. DeepSeek V4
Flash + a Nemotron satisfies that **at $0**, with `gpt-oss-120b` as a third. No procurement is
required to run Tier B.

## 3. Results — failures, by mode

```
mode                model(s)                                            observed
TIMEOUT (hang)      meta/llama-3.3-70b-instruct                         3/3 @ 90s
                    z-ai/glm-5.2                                        2/2 @ 60s
                    google/gemma-4-31b-it                               2/2 @ 60s
HTTP 404            moonshotai/kimi-k2.6                                listed in /v1/models,
                    mistralai/mistral-large-2-instruct                  not servable
                    nvidia/llama-3.1-nemotron-ultra-253b-v1
                    deepseek-ai/deepseek-r1
HTTP 410 Gone       qwen/qwen2.5-coder-32b-instruct                     retired from catalog
HTTP 429            minimaxai/minimax-m3                                rate-limited
```

`meta/llama-3.3-70b-instruct` is the reproduction of James's remembered failure: it hangs to a
hard 90-second timeout, every attempt, while a sibling model on the *same endpoint and the same
key* answers a 16K-token prompt in 8.5 seconds.

**Of 12 catalog models tested, 4 serve.** The endpoint and the credential are healthy —
`GET /v1/models` returns 102 models in 0.4s — so the fault is per-model availability, not
transport. The 410 proves the catalog drifts under us.

## 4. What this changes

1. **The timeout problem is screenable.** It is deterministic per model, not sporadic, so a
   preflight catches it before a run instead of during one. This is now prereg **R8a**: every
   solver is preflighted immediately before each run (2 small + 1 at the packet ceiling); a
   failure means swap-before-execute, never mid-run patching. Preflight records commit with the
   results.
2. **Mid-run degradation is the dangerous case, and it has precedent.**
   `roles/PipelineOrchestrator/in_api_emergency_break_glass.md` records 2026-03-28, when this
   endpoint hit a **91% timeout rate** and the forge's yield collapsed to 0.5%. A degraded
   solver does not fail loudly — it silently thins N and biases whichever arm was in flight,
   which is precisely how an underpowered `Δ_carry ≈ 0` becomes a false null. Hence: an arm that
   degrades mid-run is re-run **whole**, never partially averaged (R11).
3. **Tier B needs no procurement.** Two verified families at $0. The $11 DeepSeek-direct line in
   prereg §6.4 is moot — and unusable anyway: the DeepSeek key authenticates but returns
   **HTTP 402 Insufficient Balance**.
4. **A prereg claim of mine was wrong and is corrected.** I wrote that no credentials existed on
   M1; I had checked only `os.environ`, not the `.env` fallback `keys.py` reads. Keys for
   DeepSeek / Gemini / OpenAI / Claude are in `F:/Prometheus/.env`, and NVIDIA's is in
   `agents/eos/.env`. Both gitignored.

## 4b. Sustained-rate trial (added 2026-08-13, `E3` — `ergon/probe_api_soak.py`)

Reachability is not sustainability, and the 2026-03-28 failure was *degradation over time*.
Two measurements, both on `nvidia/llama-3.3-nemotron-super-49b-v1.5` with a realistic ~8K-token
packet (the §4.5 ceiling), not a toy prompt.

**Rate ladder — where the cliff is** (60s per rung):

```
10 RPM   10/10 ok   p50  5.9s   p90 17.6s   max 17.6s
20 RPM   20/20 ok   p50  4.3s   p90 14.0s   max 51.0s
40 RPM   40/40 ok   p50  4.4s   p90 20.4s   max 32.5s
60 RPM   57/60 ok   p50  3.2s   p90 21.6s   max 57.4s   3x TIMEOUT
```

Highest fully-clean rate is **40 RPM — exactly the documented free-tier cap**, so the published
limit is enforced, not advisory. 60 RPM is the cliff.

**Soak — 30 RPM for 15 minutes, 450 calls, quartile-split to expose drift:**

```
block 1   112/112 ok (100.0%)   p50 3.3s   p90 23.2s   max  38.9s
block 2   112/112 ok (100.0%)   p50 4.2s   p90 23.5s   max  61.8s
block 3   112/112 ok (100.0%)   p50 3.4s   p90 23.7s   max 114.7s
block 4   111/112 ok ( 99.1%)   p50 3.3s   p90 23.7s   max  68.5s   1x TIMEOUT
OVERALL   449/450 ok ( 99.8%)   p50 3.4s   p90 23.7s   max 114.7s
```

**No degradation over time** — p50 and p90 are flat across all four blocks. The lane is
sustainable at 30 RPM. That is the answer to the question asked: yes, transactions go through
reliably, and no, we do not need to throttle heavily. 30 RPM with margin under the 40 cap.

**The tail is the real design constraint.** Full latency distribution over the 450 calls:

```
p50 3.4s   p75 8.9s   p90 23.7s   p95 32.6s   p99 61.8s   max 114.7s   mean 8.9s
exceeding  30s:  31 calls (6.89%)
exceeding  60s:   5 calls (1.11%)
exceeding  90s:   1 call  (0.22%)
exceeding 120s:   0 calls (0.00%)
```

p90 is **7× p50**. A healthy call can take 114.7 seconds. Consequences, now binding:

1. **Timeout = 180s with one retry.** At 60s we would have discarded 1.11% of *healthy*
   responses; at 120s, 0.22%. Those discards are not random — long-latency calls correlate with
   longer packets, so the loss would concentrate in `F-prom-retrieved` and `F-prom-whole` and
   show up as **arm-correlated missing data**. That is a mechanism for manufacturing a Δ out of
   nothing, and it is exactly the class of artifact this probe exists to avoid.
2. **Throughput is dispatch-bound, not latency-bound** (mean 8.9s vs a 2s dispatch interval), so
   concurrency covers the tail: at 30 RPM the pilot (600 calls) is ~20 min and the full two-solver
   Tier-B run (4,800 calls) is ~2.7 hours.
3. **Timeout rate must be logged per arm** and reported beside parse-failure. If it differs
   across arms by >2pp, that comparison is flagged the same way a parse-failure spread is.

## 5. Residual risks (stated, not resolved)

- **Serving config is undisclosed.** NVIDIA does not publish quantization or serving parameters
  per NIM endpoint, so `host + model_id` is the pinning unit and results are never compared
  across hosts (prereg §1).
- **40 RPM free-tier ceiling** means a 2,800-call solver pass takes ~70 minutes minimum. Fine
  for a batch-shaped probe; it does forbid a synchronous interactive harness.
- **Catalog drift is now a demonstrated hazard**, not a hypothetical: a model that preflights
  clean this week can 410 next week. Re-preflight per run, and record the catalog snapshot.
- **`gpt-oss-120b` at 23.1s on a 16K payload** is ~3× the Nemotrons. At 2,800 calls that is a
  scheduling constraint, not a correctness one, but it should not be the first-choice solver.

— Ergon, M1, 2026-08-13
