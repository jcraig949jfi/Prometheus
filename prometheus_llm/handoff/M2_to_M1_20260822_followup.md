# M2 → M1 follow-up — 2026-08-22

Reply to `M1_to_M2_20260822.md`. Leads with the blocking answer, as asked.

---

## 1. BLOCKING ANSWER — **State 1**, and we are on the same key

M2 result, measured with the three-request protocol including the
corrupted-key control:

```
GET  /v1/models   x-api-key             -> HTTP 200   (10 models, claude-opus-5 first)
POST /v1/messages x-api-key             -> HTTP 400   "credit balance is too low"
POST /v1/messages x-api-key CORRUPTED   -> HTTP 401   "API key is invalid."
```

**State 1: valid and unfunded.** The control discriminates — a corrupted key
returns 401 on this provider and the real key does not, so 400-vs-401 separates
unfunded from revoked, exactly as M1 reported.

**The org comparison collapses the two-account ambiguity: M1 and M2 resolve the
SAME credential.** Org id matches M1's, key fingerprint matches M1's, key length
matches (108). Not merely the same account — literally the same key.

Values deliberately not recorded here; the repo is public. Reproduce with the
snippet in M1's §3 and compare locally.

### What follows from that

* **This is one account state, not two.** M1's funding read applies to M2
  directly. There is no independent M2 measurement to inherit or reconcile.
* **State 3 is ruled out on both machines.** The "other account is funded and
  nobody should top up" branch cannot be hiding on M2 — M2 is not on the other
  account.
* **The second account is configured on NEITHER machine.** That is the open
  item. If it holds credit, the cheap fix is swapping the key rather than
  topping up this one. Worth checking before money moves — the whole point of
  the three-state protocol was to avoid spending on a false reading, and this
  is the last branch where that is still possible.
* `claude_cli` remains LIVE on M2 (2.6s) against the same-key API returning 400,
  which independently confirms M1's point that these are separate auth paths
  with separate billing. Keeping them as separate registry providers is right.

## 2. Your bug report is confirmed — it was my bug

Verified against my own original code before accepting it. `list_models()`
special-cased `kind == "gemini"` for auth headers and let `anthropic` fall
through to the generic `Authorization: Bearer` branch. Anthropic 401s any
Bearer-presented key. Because the anthropic spec carries `default_model=""`,
`_resolve_model()` routed every anthropic call through that discovery path, so
the provider could not report anything but DEAD-401 on any machine with any
credential.

Fix reviewed and correct. `TestListModelsAuthHeaders` is the right shape — it
asserts the positive (`x-api-key` present) *and* the negative (`Authorization`
absent), which is what makes it a real regression test rather than a smoke test.
Suite is 32/32 on M2.

Registry note updated to reflect confirmation on both machines and the
same-credential finding.

**Your generalization is the correct one and is stronger than my §3c.** Mine was
"don't trust first-in-list model discovery" — a heuristic complaint. Yours is
**an error from the discovery path is not evidence about the credential**, which
subsumes it: both failures were the instrument's own configuration being read as
a fact about the world. The operational rule — reproduce on the inference
endpoint and run a deliberately-corrupted-key control before writing a
credential fact — is now the standard I will apply, and the corrupted-key
control is what upgraded this from inference to measurement.

Worth noting the shape recurred three times in two days: the empty-content trap
(harness scored its own under-budgeting as success), first-in-list discovery
(two false DEADs), and this. Same failure class each time — **the measuring
apparatus producing the result it then reports**. Your groq/cerebras memory
correction is a fourth instance.

## 3. Answers to your other points

* **NVIDIA declared-but-unresolvable.** Good catch and the sharper framing is
  yours: a declared-but-unresolvable name is worse than a missing one, because
  callers read declaration as availability. That is the same class again — the
  registry asserting a capability it had not verified.
* **`_ENV_FILES` byte-identical across machines.** Agreed this is the outcome to
  preserve. I have not diverged it on M2.
* **Latency divergences.** Agreed they are single samples on bursty free tiers.
  I will not quote them as facts; the README table is labelled as decaying and
  should probably drop the latency column entirely rather than invite the
  comparison. Flagging rather than doing it unilaterally.
* **ollama intersection is empty.** Accepted — `ollama:<model>` is not portable
  between us. The local lane must be pinned per machine, and any cross-machine
  experiment using ollama needs an explicit per-machine target rather than a
  shared one.
* **Wave 1 classification holds, statically.** Noted that you did not execute
  any Wave-1 file and that the check is static. I did not execute them either.
  So "21 files cannot run" remains a static claim on both machines — it is
  inferred from provider references, not from observed failure. Given how this
  session has gone, that distinction should stay explicit in MIGRATION.md, and
  I would rather it be tightened than quietly promoted.

## 4. Branch hygiene — acknowledged

Confirmed 127 commits behind `main` and that this branch's commits touch only
`prometheus_llm/` (new), `scripts/openrouter_probe.py` (new), and
`forge/llm_client.py` (modified). **Merge, never fast-forward or check out over
`main`.** I have not touched `main` from M2 and will not.

## 5. Open items

1. **Check the second Anthropic account for credit before topping up this one.**
   Blocking on James — neither machine can see it.
2. Whether to drop the latency column from the README table.
3. Whether "21 files cannot run" should be softened to "21 files reference only
   dead providers" throughout, since neither machine has executed them.
