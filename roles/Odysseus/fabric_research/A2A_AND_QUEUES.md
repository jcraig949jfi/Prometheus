# A2A Protocol v1.0 boundary + proven queue machinery (research note)

Author: research delegate for Odysseus. Date: 2026-09-28.
Tagging: VERIFIED = fetched from the primary source during this session
(WebFetch, curl of GitHub/PyPI APIs, or reading the downloaded SDK source
tarball a2a-python v1.1.5). UNVERIFIED = recalled/inferred, not fetched.
Note: the session WebSearch budget was exhausted, so all verification was
done by direct fetch of known primary URLs (spec repo, PyPI JSON API,
GitHub API, SDK source tarball, vendor docs).

Primary sources used:
- Spec (rendered): https://a2a-protocol.org/latest/specification/
- Spec (source):   https://github.com/a2aproject/A2A/blob/main/docs/specification.md
- Normative proto: https://github.com/a2aproject/A2A/blob/main/specification/a2a.proto
- 0.3 -> 1.0 diff: https://a2a-protocol.org/latest/whats-new-v1/
- Releases:        https://github.com/a2aproject/A2A/releases
- Python SDK:      https://github.com/a2aproject/a2a-python (tag v1.1.5), https://pypi.org/project/a2a-sdk/
- TCK:             https://github.com/a2aproject/a2a-tck
- Inspector:       https://github.com/a2aproject/a2a-inspector
- Samples:         https://github.com/a2aproject/a2a-samples

Caveat: proto/spec text was read from the `main` branch on 2026-09-28, not
from the v1.0.1 tag. The TCK's own spec snapshot records it was taken from
the A2A `v1.0.0` branch (specification/version.json). Before freezing our
wire schema, diff main vs tag v1.0.1 once (cheap; UNVERIFIED that they are
identical for the fields below).

====================================================================
PART 1 -- A2A PROTOCOL
====================================================================

## 1.1 Current version, location, changes from 0.2/0.3

- Current released spec: **v1.0.1 (GitHub release 2026-05-28)**; v1.0.0 was
  released 2026-03-12. Prior: v0.3.0 (2025-07-30), v0.2.6 (2025-07-17),
  v0.2.5 (2025-06-30). VERIFIED (GitHub releases API).
- The spec page header says "Latest Released Version 1.0.0" and links
  https://a2a-protocol.org/v1.0.0/specification ; patch versions do not
  affect compatibility: "Patch version numbers SHOULD NOT be used in
  requests, responses and Agent Cards" -- the wire version string is
  `"1.0"` (Major.Minor). VERIFIED (spec 3.6).
- Normative source of truth: `specification/a2a.proto` (proto package
  `lf.a2a.v1`); "the file spec/a2a.proto is the single authoritative
  normative definition of all protocol data objects". VERIFIED.
- Home: a2a-protocol.org (docs) and github.com/a2aproject/A2A (spec repo).
  VERIFIED.

Method renames 0.3 -> 1.0 (VERIFIED, whats-new-v1 + spec 5.3 + SDK
jsonrpc_dispatcher.METHOD_TO_MODEL):

| 0.3 JSON-RPC method                | 1.0 JSON-RPC method                  |
|------------------------------------|--------------------------------------|
| message/send                       | SendMessage                          |
| message/stream                     | SendStreamingMessage                 |
| tasks/get                          | GetTask                              |
| (none)                             | ListTasks  (NEW in 1.0)              |
| tasks/cancel                       | CancelTask                           |
| tasks/resubscribe                  | SubscribeToTask                      |
| tasks/pushNotificationConfig/*     | CreateTaskPushNotificationConfig, GetTaskPushNotificationConfig, ListTaskPushNotificationConfigs, DeleteTaskPushNotificationConfig |
| agent/getAuthenticatedExtendedCard | GetExtendedAgentCard                 |

Other 1.0 breaking changes (VERIFIED, whats-new-v1 / SDK migration guide):
- Enums are ProtoJSON SCREAMING_SNAKE: "submitted" -> "TASK_STATE_SUBMITTED",
  "user" -> "ROLE_USER".
- TextPart/FilePart/DataPart and the `kind` discriminator are GONE. One
  unified `Part`; type is by member presence (`text` | `raw` | `url` |
  `data`). `mimeType` -> `mediaType`; `file.fileWithUri` -> `url`.
- Stream events lose `kind`; wrapper objects `statusUpdate` / `artifactUpdate`.
- Agent Card: top-level `url` and `preferredTransport` removed; new
  `supportedInterfaces[]`; `protocolVersion` moved into each interface;
  `supportsAuthenticatedExtendedCard` -> `capabilities.extendedAgentCard`.
- `A2A-Version` header introduced; `/v1/` removed from REST paths;
  cursor pagination; `tenant` field for multi-tenancy; `final` removed
  from TaskStatusUpdateEvent; OAuth implicit/password flows removed.
- Blocking flag is now `returnImmediately` (default false = blocking) in
  `SendMessageConfiguration`. VERIFIED (proto: `bool return_immediately = 4`).

Push notifications in 1.0 (VERIFIED): four CRUD methods above; gated by
`capabilities.pushNotifications`; if false/absent, those methods "MUST
return PushNotificationNotSupportedError" (-32003). A push config can also
be passed inline in `SendMessageConfiguration.taskPushNotificationConfig`.

## 1.2 Bindings

Three standard bindings, all normative (VERIFIED, spec 5 / 9 / 10 / 11):
- `JSONRPC`   -- JSON-RPC 2.0 over HTTP(S), `Content-Type: application/json`,
  PascalCase method names, streaming via SSE (`text/event-stream`).
- `GRPC`      -- service `A2AService` in a2a.proto.
- `HTTP+JSON` -- REST: `POST /message:send`, `POST /message:stream`,
  `GET /tasks/{id}`, `GET /tasks`, `POST /tasks/{id}:cancel`,
  `POST /tasks/{id}:subscribe` (proto annotation says GET for subscribe;
  spec table says POST -- inconsistency noted, VERIFIED both texts),
  push config under `/tasks/{id}/pushNotificationConfigs`,
  `GET /extendedAgentCard`.

Required vs optional (VERIFIED by reading spec 5.1/5.2/8.3):
- No binding is individually mandated. An agent MUST declare every
  binding it supports in `supportedInterfaces`; if it supports more than
  one, all MUST be functionally equivalent (same ops, same errors, same
  auth). Custom bindings are allowed but MUST define error mappings and
  service-parameter transport.
- So "JSON-RPC only" is a legitimate compliant configuration. The TCK
  tests only the transports the card declares (VERIFIED, TCK README).
- All "Core Operations" in spec 3.1 are described as what "all A2A
  implementations must support", but capability gating applies:
  - `capabilities.streaming` false/absent -> `SendStreamingMessage` and
    `SubscribeToTask` MUST return UnsupportedOperationError (-32004).
  - `capabilities.pushNotifications` false/absent -> push-config methods
    MUST return PushNotificationNotSupportedError (-32003).
  VERIFIED (spec 3.3.4 capability validation).
- Therefore a minimal compliant JSON-RPC server must really implement:
  SendMessage, GetTask, ListTasks, CancelTask, GetExtendedAgentCard (or
  its error), plus correct errors for the gated methods, version header
  handling, and the Agent Card at the well-known path.

Versioning rules (VERIFIED, spec 3.6):
- Clients MUST send `A2A-Version: 1.0` (HTTP header for JSON-RPC).
- "Agents MUST interpret empty value as 0.3 version." If a version is not
  supported: VersionNotSupportedError (-32009). => A 1.0-only server
  must reject header-less requests with -32009 (or implement 0.3 too).
- `A2A-Extensions` header: comma-separated extension URIs.

JSON conventions (VERIFIED, spec 5.5/5.6):
- camelCase field names in all JSON bindings.
- Enums as proto names (`TASK_STATE_COMPLETED`, `ROLE_AGENT`).
- Timestamps: ISO 8601 UTC with `Z`, millisecond precision SHOULD,
  pattern `YYYY-MM-DDTHH:mm:ss.sssZ`.
- `bytes` (Part.raw) is base64 per ProtoJSON (UNVERIFIED detail; standard
  ProtoJSON behavior).

JSON-RPC error codes (VERIFIED, spec 5.4 / 9.5):
-32700 parse, -32600 invalid request, -32601 method not found,
-32602 invalid params, -32603 internal;
-32001 TaskNotFoundError, -32002 TaskNotCancelableError,
-32003 PushNotificationNotSupportedError, -32004 UnsupportedOperationError,
-32005 ContentTypeNotSupportedError, -32006 InvalidAgentResponseError,
-32007 ExtendedAgentCardNotConfiguredError, -32008 ExtensionSupportRequiredError,
-32009 VersionNotSupportedError.
`error.data` is an ARRAY of objects each with an `@type` key (ProtoJSON Any,
e.g. `google.rpc.ErrorInfo`). VERIFIED.

Wire examples (VERIFIED, spec 9.4):

```
POST /a2a/jsonrpc HTTP/1.1
Content-Type: application/json
A2A-Version: 1.0

{"jsonrpc":"2.0","id":1,"method":"SendMessage",
 "params":{"message":{"messageId":"m-1","role":"ROLE_USER",
                      "parts":[{"text":"run job X"}]},
           "configuration":{"returnImmediately":true,"historyLength":0}}}

-> {"jsonrpc":"2.0","id":1,"result":{"task":{...Task...}}}   (or {"message":{...}})

{"jsonrpc":"2.0","id":2,"method":"GetTask","params":{"id":"task-uuid","historyLength":10}}
{"jsonrpc":"2.0","id":3,"method":"ListTasks","params":{"contextId":"ctx","status":"TASK_STATE_WORKING","pageSize":50,"pageToken":"cursor"}}
{"jsonrpc":"2.0","id":4,"method":"CancelTask","params":{"id":"task-uuid"}}
```

Semantics that bite a long-running-task server (VERIFIED, spec 3.1/3.2.2/3.3.1):
- SendMessage is BLOCKING by default: with `returnImmediately` false/unset
  the server "MUST wait until the task reaches a terminal state ... or an
  interrupted state ... before returning". With `returnImmediately: true`
  it MUST return immediately with an in-progress task; client then polls
  GetTask. Our research tasks can take hours, so the adapter needs a
  blocking path that holds the HTTP request while polling Postgres (with a
  server-side cap -- the cap itself is a spec deviation to document).
- ListTasks: cursor pagination; `nextPageToken` MUST always be present
  ("" on last page); sort by status timestamp DESC; when
  `includeArtifacts` is false the `artifacts` field MUST be omitted
  entirely; results MUST be scoped to the caller. Response also requires
  `pageSize` and `totalSize` (proto REQUIRED).
- CancelTask: idempotent; TaskNotCancelableError if already terminal.
- SendMessage MAY be idempotent using `messageId` for dedupe (good: map
  messageId -> our idempotency key).
- SubscribeToTask on a terminal task -> UnsupportedOperationError.

## 1.3 Agent Card (v1)

Well-known path: **`/.well-known/agent-card.json`** (not agent.json).
VERIFIED (spec 8.2; SDK constant AGENT_CARD_WELL_KNOWN_PATH).

AgentCard fields (VERIFIED from a2a.proto, `REQUIRED` = field_behavior):

| field (JSON)          | req | notes |
|-----------------------|-----|-------|
| name                  | R   | |
| description           | R   | |
| supportedInterfaces[] | R   | AgentInterface: url R, protocolBinding R ("JSONRPC"/"GRPC"/"HTTP+JSON"), protocolVersion R ("1.0"), tenant opt |
| version               | R   | the AGENT's version, e.g. "0.1.0" |
| capabilities          | R   | streaming?, pushNotifications?, extensions[] (AgentExtension{uri, description, required, params}), extendedAgentCard? |
| defaultInputModes[]   | R   | media types, e.g. "text/plain", "application/json" |
| defaultOutputModes[]  | R   | |
| skills[]              | R   | AgentSkill: id R, name R, description R, tags[] R; examples[], inputModes[], outputModes[], securityRequirements[] optional |
| provider              | opt | if present: organization R, url R |
| documentationUrl      | opt | |
| securitySchemes       | opt | map name -> SecurityScheme (apiKey/http/oauth2/openIdConnect/mtls) |
| securityRequirements  | opt | |
| signatures[]          | opt | JWS card signatures |
| iconUrl               | opt | |

There is NO top-level `url`, `preferredTransport`, or `protocolVersion` in
v1 (moved into supportedInterfaces). VERIFIED.

Minimal valid v1 card for us (constructed from the proto; field set
VERIFIED, the document itself is ours):

```json
{
  "name": "Prometheus Agent Fabric",
  "description": "Durable task fabric for the Prometheus research program.",
  "supportedInterfaces": [
    {"url": "http://ubu001.local:8765/a2a/jsonrpc",
     "protocolBinding": "JSONRPC",
     "protocolVersion": "1.0"}
  ],
  "version": "0.1.0",
  "capabilities": {"streaming": false, "pushNotifications": false},
  "defaultInputModes": ["text/plain", "application/json"],
  "defaultOutputModes": ["text/plain", "application/json"],
  "skills": [
    {"id": "fabric.run",
     "name": "Run fabric task",
     "description": "Submit a capability-routed task to Prometheus workers.",
     "tags": ["prometheus", "batch"],
     "examples": ["{\"capability\":\"gpu.small\",\"cmd\":\"...\"}"]}
  ]
}
```

(Set `capabilities` booleans explicitly: the spec's field-presence rules
say explicitly-set optional fields are included in JSON; VERIFIED spec 5.7
example `{"capabilities":{"pushNotifications":false,"streaming":false},...}`.)

## 1.4 Task / Message / Part / Artifact (v1)

TaskState (VERIFIED, proto + SDK a2a_pb2.pyi):
`TASK_STATE_UNSPECIFIED`, `TASK_STATE_SUBMITTED`, `TASK_STATE_WORKING`,
`TASK_STATE_COMPLETED`, `TASK_STATE_FAILED`, `TASK_STATE_CANCELED`,
`TASK_STATE_INPUT_REQUIRED`, `TASK_STATE_REJECTED`, `TASK_STATE_AUTH_REQUIRED`.
- There is NO "unknown" state in v1 (UNSPECIFIED is the proto zero value).
- Terminal: COMPLETED, FAILED, CANCELED, REJECTED.
- Interrupted: INPUT_REQUIRED, AUTH_REQUIRED.
- Spelling: "CANCELED" (one L, American). VERIFIED.
- Oddity: the SDK AgentExecutor docstring mentions `TASK_STATE_ERROR`,
  which does not exist in the enum -- doc bug; ignore. VERIFIED (source).

Task: `id` R, `contextId`, `status` R (TaskStatus{`state` R, `message`
(Message), `timestamp`}), `artifacts[]`, `history[]` (Messages),
`metadata` (Struct = free JSON object). VERIFIED.

Message: `messageId` R, `contextId`, `taskId`, `role` R (`ROLE_USER` |
`ROLE_AGENT`), `parts[]` R, `metadata`, `extensions[]` (URIs),
`referenceTaskIds[]`. VERIFIED.

Part (one of): `text` (string) | `raw` (bytes, base64 in JSON) | `url`
(string) | `data` (any JSON value, google.protobuf.Value); plus `metadata`,
`filename`, `mediaType`. JSON: `{"text":"hi"}`,
`{"url":"https://x/y.txt","filename":"y.txt","mediaType":"text/plain"}`,
`{"data":{"k":1},"mediaType":"application/json"}`. VERIFIED.

Artifact: `artifactId` R, `parts[]` R, `name`, `description`, `metadata`,
`extensions[]`. VERIFIED.

SendMessageResponse: oneof `task` | `message`. VERIFIED.

Where our custom data goes (VERIFIED spec 3.2.5 / 4.6):
- Every Task / Message / Artifact / Part / SendMessageRequest / CancelTask
  request has a free-form `metadata` object. Convention from the spec's
  own example: key the metadata by the extension URI, e.g.
  `"metadata": {"https://prometheus.local/ext/fabric/v1": {"attemptId": ..., "capability": ..., "sha256": ...}}`
  and list that URI in `message.extensions` / `artifact.extensions`.
- Declare the extension in `capabilities.extensions[]` with `uri`,
  `description`, `required: false`. Extension URIs SHOULD be versioned; a
  breaking change needs a new URI. If `required: true` and the client did
  not request it -> ExtensionSupportRequiredError (-32008).
- Recommendation: put our Attempt ids, lease info, sha256 artifact
  digests, and capability routing hints under one versioned extension URI
  in `metadata`; never invent new top-level fields.

## 1.5 Official Python SDK

- PyPI package: **`a2a-sdk`**, import name `a2a`. Latest **1.1.5**
  (uploaded 2026-09-21). 1.0.0 was 2026-04-20; 0.3.26 was the last 0.3.
  VERIFIED (PyPI JSON API).
- Spec support: implements A2A **1.0** on JSON-RPC, HTTP+JSON, gRPC
  (client and server), plus a 0.3 compatibility mode for all three.
  VERIFIED (README "Compatibility").
- Python: `requires_python >=3.10`; classifiers list 3.10-3.14. VERIFIED.
  Wheels for 3.14/x86_64 exist for the compiled deps: pydantic-core 2.49.0
  (cp314 manylinux), grpcio 1.84.0 (cp314), asyncpg 0.31.0 (cp314),
  protobuf 7.36.2 (abi3). VERIFIED (PyPI). Actual install on 3.14.4 not
  tested (nothing installed per instructions) -- UNVERIFIED in practice.
- Core deps (VERIFIED): httpx>=0.28.1, pydantic>=2.11.3, protobuf>=5.29.5,
  google-api-core>=1.26.0, googleapis-common-protos>=1.70.0,
  json-rpc>=1.15.0, packaging>=24.0, culsans (only on Python <3.13).
  Extras: `http-server` (starlette, sse-starlette), `fastapi`, `grpc`
  (grpcio, grpcio-tools, grpcio-reflection), `postgresql`
  (sqlalchemy[asyncio,postgresql-asyncpg]>=2.0), `sql`, `sqlite`, `mysql`,
  `telemetry`, `encryption`, `signing`, `db-cli` (alembic), `all`.
  NOTE: `uvicorn` is NOT a dependency of any extra; add it yourself.
- Data types are protobuf messages (`a2a.types.a2a_pb2`), not pydantic
  models, in 1.x. VERIFIED (source).

Server-side interfaces (VERIFIED, source of v1.1.5):

```python
# a2a/server/tasks/task_store.py
class TaskStore(ABC):
    async def save(self, task: Task, context: ServerCallContext) -> None
    async def get(self, task_id: str, context: ServerCallContext) -> Task | None
    async def list(self, params: ListTasksRequest, context: ServerCallContext) -> ListTasksResponse
    async def delete(self, task_id: str, context: ServerCallContext) -> None
```
- Implementations shipped: `InMemoryTaskStore`, `DatabaseTaskStore`
  (SQLAlchemy async; `DatabaseTaskStore(engine: AsyncEngine,
  create_table=True, table_name='tasks', owner_resolver=...,
  core_to_model_conversion=None, model_to_core_conversion=None)`; stores
  status/artifacts/history/metadata as JSON columns plus id, context_id,
  owner, last_updated, protocol_version), `CopyingTaskStore`. Push:
  `PushNotificationConfigStore` / `InMemoryPushNotificationConfigStore` /
  `DatabasePushNotificationConfigStore`, `BasePushNotificationSender`.
- YES, a custom TaskStore over our own Postgres schema is straightforward:
  4 async methods. Either subclass TaskStore directly (psycopg2 via
  `asyncio.to_thread`, or asyncpg), or use DatabaseTaskStore with
  custom `core_to_model_conversion`/`model_to_core_conversion`. `list`
  must implement the spec's cursor pagination/ordering itself.
- `AgentExecutor` (ABC): `async execute(context: RequestContext,
  event_queue: EventQueue)` and `async cancel(context, event_queue)`.
  Executor publishes Task / TaskStatusUpdateEvent / TaskArtifactUpdateEvent
  (helper: `TaskUpdater`). On cancel the framework cancels the asyncio
  task running execute() and calls cancel().
- `RequestHandler` (ABC) with `on_get_task`, `on_list_tasks`,
  `on_cancel_task`, `on_message_send`, `on_message_send_stream`,
  `on_subscribe_to_task`, `on_*_task_push_notification_config(s)`,
  `on_get_extended_agent_card`. Default: `DefaultRequestHandler`
  (= `DefaultRequestHandlerV2`; `LegacyRequestHandler` also exported):
  `DefaultRequestHandler(agent_executor, task_store, agent_card,
  push_config_store=None, push_sender=None, request_context_builder=None,
  extended_agent_card=None, ...)`.
- IMPORTANT architectural fact: DefaultRequestHandlerV2 runs the executor
  in the server process and "delegates event streaming to an in-memory
  ActiveTaskRegistry, so custom or distributed QueueManager
  implementations are ignored" (quoted from its DeprecationWarning).
  VERIFIED. I.e. the SDK assumes the A2A server process is where work
  runs; with our pull workers on other nodes, the executor would only
  enqueue into Postgres and then poll it -- the SDK adds nothing to
  durability; Postgres stays the truth either way.
- App wiring: the 0.3-era classes `A2AStarletteApplication`,
  `A2AFastApiApplication`, `A2ARESTFastApiApplication` were REMOVED in 1.0.
  Now route factories: `create_agent_card_routes(agent_card)`,
  `create_jsonrpc_routes(request_handler, rpc_url='/a2a/jsonrpc',
  enable_v0_3_compat=False)`, `create_rest_routes(request_handler)`,
  `add_a2a_routes_to_fastapi(app, ...)`; mount into
  `starlette.applications.Starlette(routes=routes)` and run with uvicorn.
  gRPC: `GrpcHandler`. VERIFIED (source + docs/migrations/v1_0/README.md).
- Client: `ClientFactory` (`create_from_url(...)`, `create(...)`),
  `Client` ABC with `send_message`, `get_task`, `list_tasks`,
  `cancel_task`, `subscribe`, push-config methods,
  `get_extended_agent_card`; transports `jsonrpc`, `rest`, `grpc`;
  `ClientConfig`; `minimal_agent_card(...)`. VERIFIED (source).

Sketch (SDK route; VERIFIED API names, code is ours, untested):

```python
from starlette.applications import Starlette
import uvicorn
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
handler = DefaultRequestHandler(agent_executor=FabricExecutor(),
                                task_store=PgFabricTaskStore(dsn),
                                agent_card=card)
routes = create_agent_card_routes(card) + create_jsonrpc_routes(handler, rpc_url='/a2a/jsonrpc')
uvicorn.run(Starlette(routes=routes), host='0.0.0.0', port=8765)
```

## 1.6 Validation tools

### A2A TCK (github.com/a2aproject/a2a-tck) -- VERIFIED (README, pyproject, docs)
- What: pytest-based "Technology Compatibility Kit" for A2A 1.0 across
  gRPC, JSON-RPC, HTTP+JSON. Fetches `{sut-host}/.well-known/agent-card.json`
  and tests every interface the card declares (filter with `--transport`).
  Its bundled spec snapshot comes from the A2A `v1.0.0` branch.
- pyproject name `a2a-tck` version 1.0.0; git tags up to `1.0.0.alpha2`
  (no final 1.0.0 tag yet); main last commit 2026-09-01.
- Requirements: Python >=3.11 (classifiers list 3.11-3.13, not 3.14 --
  UNVERIFIED whether it runs on 3.14), deps: pytest, pytest-asyncio,
  httpx, grpcio, protobuf, googleapis-common-protos, jsonschema,
  pytest-html, gherkin-official, Jinja2. Docs use `uv`, but run_tck.py
  just runs `sys.executable -m pytest`, so a plain venv + pip works
  (UNVERIFIED in practice).
- Compliance levels = RFC 2119: `--level must` (hard failure),
  `should` (xfail, non-blocking), `may` (skipped unless capability
  declared). Reports: `reports/compatibility.json`,
  `reports/compatibility.html`, `reports/tck_report.html`,
  `reports/junitreport.xml`.
- CRITICAL: the SUT must implement test behaviors keyed on
  `message.messageId` PREFIXES (scenarios/*.feature), e.g.
  `tck-complete-task` -> complete with message "Hello from TCK";
  `tck-artifact-text|file|file-url|data` -> complete with that artifact;
  `tck-message-response` -> return a Message not a Task;
  `tck-input-required` -> TASK_STATE_INPUT_REQUIRED (used for the cancel
  test); `tck-reject-task` -> reject; streaming prefixes `tck-stream-*`
  and `test-resubscribe-message-id` (task must live >= 2 x
  TCK_STREAMING_TIMEOUT). So we need a "tck" test skill in our executor
  (best routed through the real queue + a worker, which doubles as an
  end-to-end fabric test).
- Older 0.3-era flags (`--sut-url`, `--category mandatory|capabilities|
  quality|features`) appear in older docs and in the SDK's CI, which
  still pins TCK `0.3.0.beta3`; the 1.0 TCK uses `--sut-host` and
  `--level`. Use the 1.0 TCK (main) for us.

Commands (VERIFIED from README; install step adapted to pip):
```
sudo apt install python3-venv          # one-time, needed on these nodes
git clone https://github.com/a2aproject/a2a-tck.git && cd a2a-tck
python3 -m venv .venv && . .venv/bin/activate && pip install -e .
# (README form: uv venv; source .venv/bin/activate; uv pip install -e .)
./run_tck.py --sut-host http://127.0.0.1:8765 --transport jsonrpc --level must
./run_tck.py --sut-host http://127.0.0.1:8765 --transport jsonrpc --level should
./run_tck.py --sut-host http://127.0.0.1:8765 --transport jsonrpc -v
TCK_STREAMING_TIMEOUT=5.0 ./run_tck.py --sut-host ...   # only if streaming declared
```
`--sut-host` is the BASE URL (card is fetched from it); the JSON-RPC URL
comes from the card's supportedInterfaces.

### A2A Inspector (github.com/a2aproject/a2a-inspector) -- VERIFIED (README, pyproject)
- Web UI (FastAPI backend + TypeScript frontend): fetches and displays the
  Agent Card, runs "basic validation on the agent card", live chat, and a
  debug console showing raw JSON-RPC traffic. It is a debugging aid, not a
  conformance suite. Depends on `a2a-sdk[all]>=1.1.2` => targets v1.0.
  Needs Python >=3.12 (pyproject), uv, Node.js+npm -- OR Docker.
- Neither uv, node/npm, pip nor docker is present on this node today
  (VERIFIED `which`). Run the Inspector from another machine or after
  installing tooling.
```
git clone https://github.com/a2aproject/a2a-inspector.git && cd a2a-inspector
uv sync && (cd frontend && npm install)
bash scripts/run.sh            # or: cd frontend && npm run build -- --watch
                               #     cd backend && uv run -- uvicorn app:app --host 127.0.0.1 --port 5001 --reload
# open http://127.0.0.1:5001 and enter http://<node>:8765
# Docker alternative:
docker build -t a2a-inspector . && docker run -d -p 8080:8080 a2a-inspector   # http://127.0.0.1:8080
```

## 1.7 Samples relevant to async long-running tasks / cancel

- SDK repo `tck/sut_agent.py`: full v1 wiring (card with JSONRPC +
  HTTP+JSON + GRPC interfaces, DefaultRequestHandler, all three route
  factories, `execute()` with `asyncio.sleep(3)` simulated work and a
  `cancel()`), pluggable `serve(task_store)` -- plus
  `tck/sut_agent_with_vertex_task_store.py` showing a non-memory
  TaskStore. Best reference for us. VERIFIED (source).
- SDK `samples/hello_world_agent.py` + `samples/cli.py`: TaskUpdater
  status/artifact updates, all transports, v1 and 0.3 compat, card at
  /.well-known/agent-card.json, 1 s delay. VERIFIED (samples/README.md).
- a2a-samples/samples/python/agents (VERIFIED names only, contents
  UNVERIFIED): `helloworld`, `veo_video_gen` (long-running generation),
  `langgraph` (input-required multi-turn), `dice_agent_rest`,
  `dice_agent_grpc`, `multitenancy`, `a2a-mcp-without-framework`,
  `headless_agent_auth`, `sign_and_verify_agent_card`.
  Many samples may still be on 0.3 APIs -- check before copying.

====================================================================
PART 2 -- BORING, PROVEN MACHINERY (rules to copy)
====================================================================

## 2.1 Postgres job claiming: FOR UPDATE SKIP LOCKED
- Postgres docs: "Skipping locked rows provides an inconsistent view of
  the data, so this is not suitable for general purpose work, but can be
  used to avoid lock contention with multiple consumers accessing a
  queue-like table." VERIFIED (postgresql.org sql-select).
- Rule: claim = one short transaction that selects the oldest eligible
  row `FOR UPDATE SKIP LOCKED LIMIT n`, flips it to running, stamps
  `lease_expires_at = now() + interval`, increments attempt, COMMITS.
  Do the work OUTSIDE the transaction (never hold a row lock for the
  duration of a job). pg-boss, River, graphile-worker, Oban, Procrastinate
  all use this shape (pg-boss README: SKIP LOCKED lets "concurrent
  workers claim jobs without blocking each other" -- VERIFIED; others
  UNVERIFIED in detail this session).

```sql
WITH c AS (
  SELECT id FROM fabric.task
  WHERE state = 'queued' AND run_after <= now()
    AND required_capability = ANY(%(caps)s)
  ORDER BY priority DESC, created_at
  FOR UPDATE SKIP LOCKED LIMIT 1)
UPDATE fabric.task t
   SET state='running', lease_owner=%(worker)s,
       lease_expires_at = now() + %(lease)s::interval,
       lease_epoch = t.lease_epoch + 1, attempts = t.attempts + 1
  FROM c WHERE t.id = c.id
RETURNING t.id, t.lease_epoch;   -- plus INSERT INTO fabric.attempt(...) in same txn
```

## 2.2 Jobs vs attempts; retries with backoff
- Temporal: an Activity Execution is retried per its Retry Policy; each
  try is a separate attempt bounded by Start-to-Close timeout; the whole
  execution by Schedule-to-Close; Heartbeat timeout detects dead workers;
  activities must be idempotent because retries re-run them. VERIFIED
  (docs.temporal.io/activity-execution). Map: A2A Task == workflow/
  activity execution (client-visible, stable id); our Attempt == one
  activity task attempt (internal, many per Task). Keep Attempt out of
  the A2A object model except via extension metadata.
- River: default max 25 attempts, backoff `attempt^4 + jitter(+-10%)`
  (1s, 16s, 81s, ... ~3 weeks at 25). VERIFIED (riverqueue docs).
- graphile-worker: backoff `exp(least(10, attempt))` seconds, i.e. caps
  at ~6 h between tries. VERIFIED.
- Rule: store `attempts`, `max_attempts`, `run_after`, `last_error` on the
  task; failure => if attempts < max, state back to queued with
  `run_after = now() + backoff(attempts)`; else terminal FAILED
  ("discarded"/dead-letter). pg-boss also has dead-letter queues with
  redrive (VERIFIED README summary).

## 2.3 Leases, heartbeats, rescue of stuck jobs
- SQS visibility timeout: default 30 s, heartbeat by extending it
  (ChangeMessageVisibility), hard cap 12 h from first receive; delivery is
  at-least-once, so processing must be idempotent; DLQ after repeated
  failure. VERIFIED (AWS docs).
- PGMQ: `read(queue, vt, qty)` hides a message for vt seconds, `read_ct`
  counts deliveries, `set_vt` extends, `archive` vs `delete`. VERIFIED
  (github tembo-io/pgmq).
- River rescuer: re-queues (or discards at max attempts) jobs stuck
  running longer than RescueStuckJobsAfter (default 1 h, or JobTimeout +
  1 h). VERIFIED. Procrastinate: worker heartbeat every 10 s; jobs of
  workers without heartbeat for 30 s are "stalled", found via
  `get_stalled_jobs()` and retried. VERIFIED.
- Kleppmann fencing: a lease alone is unsafe (GC pause / network delay
  lets an expired holder keep writing); the lock service issues a
  monotonically increasing token and the storage "rejects the request with
  token 33" once it has seen 34. VERIFIED (kleppmann.com 2016).
- Rules:
  1. All lease arithmetic uses the DB clock (`now()` in SQL), never the
     worker clock -- two laptops will skew; one clock makes expiry a
     single-authority decision.
  2. `lease_epoch` (fencing token) increments on every claim; every
     heartbeat/complete/fail/artifact write is
     `UPDATE ... WHERE id=$1 AND lease_epoch=$2 AND state='running'` and
     the worker aborts if rowcount = 0.
  3. A reaper (any node, idempotent SQL) moves `running AND
     lease_expires_at < now()` back to queued (or FAILED at max_attempts)
     and closes the Attempt as `lost`.
  4. Heartbeat interval <= lease/3.

## 2.4 Idempotent submission
- Stripe: client-generated key (V4 UUID suggested, <=255 chars); server
  saves status code + body of the first request "regardless of whether it
  succeeds or fails" and replays it, including 500s; reused key with
  different parameters is an error; keys may be pruned after >=24 h;
  nothing saved if validation fails or a concurrent request with the same
  key is executing (client can retry). VERIFIED (docs.stripe.com).
- graphile-worker `job_key` (replace / preserve_run_at / unsafe_dedupe):
  if the keyed job is already locked (running), a second job is scheduled
  (except unsafe_dedupe). pg-boss `singletonKey`. VERIFIED.
- A2A: "Send Message operations MAY be idempotent. Agents may utilize the
  messageId to detect duplicate messages." VERIFIED.
- Rule: `UNIQUE (principal, idempotency_key)` on task (key = A2A
  messageId by default); insert with `ON CONFLICT DO NOTHING RETURNING`,
  on conflict compare a stored request hash -- same hash returns the
  existing task, different hash returns an error (-32602).

## 2.5 Artifact storage
- Postgres TOAST kicks in above ~2 kB per row; max field 1 GB; values are
  compressed/chunked (~2000-byte chunks). VERIFIED (postgresql.org).
- Rules (UNVERIFIED as numbers; common practice):
  1. Content-address every artifact: `sha256` is the id; rows are
     immutable; store (sha256, size, media_type) metadata in Postgres.
  2. Inline bytes in Postgres (bytea) only when small (suggest <= 1 MiB);
     larger blobs go to a filesystem / object store path keyed by sha256
     (`ab/cd/<sha256>`), written to temp then atomically renamed, and the
     DB row is inserted only after the blob is durable (+ fsync).
  3. A2A exposure: small results as `{"data":...}` / `{"text":...}`
     parts; large ones as `{"url": ..., "mediaType": ..., "filename": ...}`
     with the sha256 in Part/Artifact metadata under our extension URI.
  4. Garbage-collect blobs by reference count from the DB, never the
     reverse.

====================================================================
PART 3 -- RECOMMENDATION
====================================================================

Options:
(a) Official `a2a-sdk` 1.1.5 in an isolated venv (needs `apt install
    python3-venv`; then pip installs ~15-25 packages incl. protobuf,
    pydantic, google-api-core, starlette, sse-starlette, uvicorn, and
    asyncpg/sqlalchemy if using DatabaseTaskStore), with a custom
    `TaskStore` over our schema and an `AgentExecutor` that enqueues into
    our Postgres queue and polls it.
(b) Thin stdlib adapter: `http.server.ThreadingHTTPServer` serving
    `/.well-known/agent-card.json` and a JSON-RPC 2.0 endpoint that maps
    SendMessage / GetTask / ListTasks / CancelTask / GetExtendedAgentCard
    onto our core (psycopg2), with streaming=false and
    pushNotifications=false and exact error codes for everything else.

What each lets us claim:
- (a) out of the box: "built on the official A2A 1.0 Python SDK"; wire
  serialization, error codes, version negotiation (and 0.3 compat, REST,
  gRPC if wanted) come from the reference implementation, which is itself
  run against the TCK in CI. Still NOT a compliance claim for us until we
  run the TCK against our deployment, because our TaskStore.list
  (pagination/order/scoping) and executor semantics are ours.
- (b): "implements the A2A 1.0 JSON-RPC binding with streaming and push
  notifications not supported (declared false)". Legitimate per spec
  (single binding allowed; gated ops return -32004 / -32003). We may say
  "A2A 1.0 compatible (JSON-RPC, TCK MUST level)" only after
  `run_tck.py --transport jsonrpc --level must` passes; SHOULD failures
  are xfail and do not block.

Recommendation: **(b) for the pilot**, with the TCK as the gate, and (a)
kept as the fallback. Reasons:
1. Architecture match: the SDK's v2 handler assumes execution happens
   inside the server process (in-memory ActiveTaskRegistry). Our truth is
   Postgres with pull workers on two nodes; with (a) the executor is a
   shim that enqueues and polls, i.e. we write the hard part anyway and
   carry an asyncio/protobuf stack on top of it.
2. The boundary we need is small and fully specified: 5 methods + card +
   9 error codes + header rule + JSON conventions (all captured above).
   Roughly a few hundred lines of stdlib; no new runtime deps on the
   worker nodes, no venv in the production path.
3. Crash recovery is simpler: the adapter is stateless; every request
   reads/writes Postgres; restart loses nothing.
4. The validator (TCK) is a client -- it needs a venv once (or runs from
   another machine) but never becomes a runtime dependency.
5. Escape hatch: if we later need streaming/push/gRPC or TCK MUST
   failures prove costly, switch to (a) and reuse the same Postgres
   schema behind a 4-method TaskStore.

Must-do details for (b):
- Reject missing/unknown `A2A-Version` with -32009 (empty header = 0.3 by
  spec), or implement 0.3 method aliases -- choose reject.
- Blocking SendMessage default: hold request and poll DB until terminal/
  interrupted; document a server max wait. Tell clients to send
  `configuration.returnImmediately: true` and poll GetTask.
- ListTasks: cursor token over (status_timestamp DESC, id), always emit
  `nextPageToken` ("" at end), `pageSize`, `totalSize`; omit `artifacts`
  unless includeArtifacts.
- CancelTask: terminal -> -32002; else set cancel_requested, workers
  observe it at heartbeat (fenced), final state TASK_STATE_CANCELED.
- Add a `tck` capability worker implementing the messageId-prefix
  scenarios so the TCK exercises the real queue end-to-end.
- Validate outgoing JSON in tests against the TCK's
  `specification/a2a.json` schema (in the TCK venv).

The 5 queue rules to copy:
1. Claim with one short `FOR UPDATE SKIP LOCKED LIMIT n` transaction that
   marks running + creates an Attempt; do work outside it.
2. All time from DB `now()`; lease = `lease_expires_at`; heartbeats extend
   it; a reaper re-queues expired leases and marks the Attempt lost.
3. Fencing: `lease_epoch` increments per claim; every worker write is
   conditional on (id, lease_epoch, state='running').
4. Task (stable, client-visible, A2A id) vs Attempt (per try, internal);
   retries with capped exponential backoff via `run_after`, `max_attempts`,
   then terminal FAILED with last_error preserved.
5. Idempotent submission via `UNIQUE(principal, idempotency_key)` (default
   key = A2A messageId) + stored request hash; content-addressed immutable
   artifacts (sha256), small inline, large on disk, DB row after blob is
   durable.
