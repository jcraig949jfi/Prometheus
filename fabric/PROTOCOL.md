# Fabric A2A gateway: protocol and compliance

This covers the A2A **v1.0** JSON-RPC binding only. The gateway is `python -m fabric gateway --port 8710`. It is
stateless and every answer comes from the fabric store.

## Endpoints

| path | purpose |
|---|---|
| `GET /.well-known/agent-card.json` | Agent Card, with `supportedInterfaces` = one JSONRPC interface at `/a2a/jsonrpc`, `protocolVersion` 1.0 |
| `POST /a2a/jsonrpc` | JSON-RPC 2.0; header `A2A-Version: 1.0` required (otherwise -32009); `Content-Type: application/json` required (otherwise -32005) |
| `GET /artifacts/<artifact_id>` | artifact bytes (content-addressed, sha256-verified) |

The card is built live from registered worker capabilities. It declares:
- capabilities `streaming=false`, `pushNotifications=false` and `extendedAgentCard=false`;
- extension `https://prometheus.local/ext/fabric/v1`;
- `ETag` and `Cache-Control: max-age=60` headers.

## Methods

| method | behaviour |
|---|---|
| `SendMessage` | Creates a Task, or continues an input-required Task when `message.taskId` is set. It blocks until the task is terminal or interrupted, up to `FABRIC_BLOCK_CAP_S` (120 s by default), unless `configuration.returnImmediately` is set. |
| `GetTask` | Honours `historyLength`: 0 omits history, n returns the last n messages. |
| `ListTasks` | Filters by `contextId` and `status`; cursor pagination via `pageToken`/`nextPageToken`; `totalSize`. |
| `CancelTask` | submitted -> canceled; working -> `cancel_requested` (the worker kills the executor and the attempt ends canceled); terminal -> -32002 TaskNotCancelable. |
| `SendStreamingMessage`, `SubscribeToTask`, `GetExtendedAgentCard` | -32004 UnsupportedOperation |
| push-notification config methods | -32003 PushNotificationNotSupported |

- Errors carry `error.data` as an array of ErrorInfo.
- Request keys are accepted in lowerCamel and in proto field-name form (`historyLength` / `history_length`), as
  ProtoJSON parsers must accept both.

## Prometheus metadata (extension `https://prometheus.local/ext/fabric/v1`)

Put this in `message.metadata[EXT]` or `params.metadata[EXT]`:
- `executor`, `capabilities[]`, `resources[]`, `host`, `target`;
- `baseSha`, `threadId`, `params{}`, `priority`, `maxAttempts`, `title`, `principal`;
- `idempotencyKey`.

A message **without** this metadata is treated as the `a2a.conformance` skill. That skill runs the synthetic
behaviours keyed by the TCK's messageId prefixes and never reaches a Claude worker.

Idempotency applies only with an explicit `idempotencyKey`. A2A does not make `messageId` an idempotency key, and the
TCK legitimately reuses a messageId across separate requests. For the same reason, message history is kept in
arrival order and is not deduplicated by messageId.

Task metadata returns `attempts[]` (id, status, agent, host, model), `waitingReason` and `forensicArtifacts[]`
(stdout, stderr, env receipt, final text). Deliverable artifacts (output files, patch, report, bundle) appear as
A2A `artifacts`. The worker's final message is `status.message`.

## Compliance: what was measured

We used the official **a2a-tck** at commit 263b9cf (2026-09-01) with `--transport=jsonrpc`. Evidence is in
`validation/`: the pytest logs `tck_*_2026-09-28_v01.txt` and the per-requirement reports `tck_*_compatibility.json`.

| level | tests | requirements (TCK per-requirement report) |
|---|---|---|
| MUST | **68 passed, 0 failed**, 167 skipped | 56 PASS, 0 FAIL, 36 SKIPPED, 22 NOT TESTED |
| SHOULD | **8 passed, 0 failed, 0 xfail**, 12 skipped | 7 PASS, 0 FAIL, 4 NOT TESTED |

Why tests were skipped:
- **gRPC and HTTP+JSON bindings** are not implemented.
- On the JSON-RPC binding, every skip is for a feature the card declares unsupported: streaming/SSE, push
  notifications, the extended agent card, and the TCK's required-extension probe.

NOT TESTED means the TCK has no test for the requirement: card signing, auth/TLS, version negotiation, and
cross-binding equivalence.

**What we claim:** no MUST or SHOULD requirement exercised by the TCK on the JSON-RPC binding fails.
**What we do not claim:** full A2A v1.0 compliance. Streaming, push notifications, the extended card, other
bindings, card signing and auth are absent.

History of this claim, kept because it was wrong at first:
1. The first TCK run was reported as "MUST 65/65, SHOULD 5/5". Those were test counts, not coverage.
2. Several JSON-RPC tests had silently **skipped** because gateway bugs broke their preconditions:
   - `messageId` was used as an idempotency key, so a "new" task returned an old, canceled one;
   - snake_case request keys were ignored;
   - a continued task kept its previous behaviour;
   - a wrong Content-Type was accepted.
3. Two SHOULD history requirements were **xfail**, which is a recorded failure, not a pass.
4. All of these were fixed in v0.1. The rerun is the table above.

## Pilot-only deviations (v0)

- There is **no authentication**. Bind the gateway to the LAN only. Anyone who can reach it can submit work.
  Workers are still sandboxed, and conformance tasks are synthetic.
- `ListTasks` is not scoped to the caller: every task is visible.
- A blocking `SendMessage` returns the non-terminal task once the cap is reached.
