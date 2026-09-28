"""fabric.gateway -- a THIN, STATELESS A2A v1.0 boundary (JSON-RPC binding) over fabric.store.

Nothing canonical lives here: every request opens a store connection and
answers from Postgres, so restarting the gateway loses nothing.

Implemented (A2A 1.0, binding JSONRPC, protocolVersion "1.0"):
  GET  /.well-known/agent-card.json   Agent Card (skills derived from live worker capabilities)
  POST /a2a/jsonrpc                   SendMessage, GetTask, ListTasks, CancelTask
                                      SendStreamingMessage / SubscribeToTask -> -32004 (streaming false)
                                      push-notification config methods        -> -32003 (push false)
                                      GetExtendedAgentCard                    -> -32007
  GET  /artifacts/<artifact_id>       artifact bytes (for url parts)
Prometheus data rides ONLY in `metadata` under the extension URI EXT (declared
in the card, required: false). Principals pass routing there:
  message.metadata[EXT] = {"principal", "capabilities", "threadId", "baseSha", "executor", "params",
                           "resources", "host", "target", "priority", "maxAttempts", "title"}
A message with no EXT metadata is treated as the "a2a.conformance" skill
(synthetic worker behaviours keyed on messageId prefixes, for the TCK).
PILOT-ONLY deviations (documented in fabric/PROTOCOL.md): no authentication
(LAN only), ListTasks is not scoped to the caller, blocking SendMessage waits
at most BLOCK_CAP_S then returns the in-progress Task.
"""
from __future__ import annotations

import base64
import datetime
import json
import os
import socket
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Optional

from . import store as S

EXT = "https://prometheus.local/ext/fabric/v1"
BLOCK_CAP_S = float(os.environ.get("FABRIC_BLOCK_CAP_S", "120"))
AGENT_VERSION = "0.1.0"
DELIVERABLE_KINDS = ("file", "patch", "report", "bundle")
STATE = {"submitted": "TASK_STATE_SUBMITTED", "working": "TASK_STATE_WORKING", "input-required": "TASK_STATE_INPUT_REQUIRED",
         "completed": "TASK_STATE_COMPLETED", "canceled": "TASK_STATE_CANCELED", "failed": "TASK_STATE_FAILED",
         "rejected": "TASK_STATE_REJECTED"}
STATE_BACK = {v: k for k, v in STATE.items()}
INTERRUPTED = ("input-required",)
TCK = [  # messageId prefix -> synthetic params (longest prefix first); values from a2a-tck scenarios/core_operations.feature
    ("tck-artifact-file-url", {"files": [["output.txt", "output", "url:https://example.com/output.txt"]]}),
    ("tck-artifact-file", {"files": [["output.txt", "Generated file content", "raw"]]}),
    ("tck-artifact-text", {"files": [["output.txt", "Generated text content", "text"]]}),
    ("tck-artifact-data", {"files": [["output.json", "{\"key\": \"value\", \"count\": 42}", "data"]]}),
    ("tck-input-required", {"final_state": "input-required", "text": "Please provide input"}),
    ("tck-reject-task", {"final_state": "rejected", "text": "rejected"}),
    ("tck-complete-task", {}),
]


class RpcError(Exception):
    def __init__(self, code: int, message: str, reason: str = ""):
        super().__init__(message); self.code, self.message, self.reason = code, message, reason or message


def _iso(t) -> str:
    if t is None:
        t = datetime.datetime.now(datetime.timezone.utc)
    return t.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (t.microsecond // 1000)


def base_url(handler=None) -> str:
    if os.environ.get("FABRIC_GATEWAY_URL"):
        return os.environ["FABRIC_GATEWAY_URL"].rstrip("/")
    host = handler.headers.get("Host") if handler is not None else None
    return "http://" + (host or "{}:{}".format(socket.gethostname(), os.environ.get("FABRIC_GATEWAY_PORT", "8710")))


# ------------------------------------------------------------------ card
def agent_card(conn, base: str) -> Dict[str, Any]:
    caps = set()
    for a in S.agents(conn):
        if a["live"] and a["kind"] == "worker":
            caps.update(a["capabilities"])
    skills = [{"id": c, "name": c, "description": "Prometheus fabric capability {} (served by live pull workers).".format(c),
               "tags": ["prometheus", c.split(".")[0]]} for c in sorted(caps)]
    skills.insert(0, {"id": "fabric.submit", "name": "Submit a durable research task",
                      "description": "Create a durable Task routed by capability to Prometheus pull workers; poll GetTask.",
                      "tags": ["prometheus", "durable", "async"],
                      "examples": ['metadata["{}"] = {{"capabilities":["research.repo_readonly"],"threadId":"thr-...","baseSha":"<sha>"}}'.format(EXT)]})
    if "a2a.conformance" not in caps:
        skills.append({"id": "a2a.conformance", "name": "a2a.conformance", "description": "TCK conformance behaviours (synthetic).",
                       "tags": ["test"]})
    return {"name": "Prometheus Agent Fabric", "description": "Durable task fabric for the Prometheus research program (pilot).",
            "supportedInterfaces": [{"url": base + "/a2a/jsonrpc", "protocolBinding": "JSONRPC", "protocolVersion": "1.0"}],
            "version": AGENT_VERSION,
            "capabilities": {"streaming": False, "pushNotifications": False, "extendedAgentCard": False,
                             "extensions": [{"uri": EXT, "description": "Prometheus fabric routing and provenance metadata",
                                             "required": False}]},
            "defaultInputModes": ["text/plain", "application/json"], "defaultOutputModes": ["text/plain", "application/json"],
            "skills": skills}


# ------------------------------------------------------------------ objects
def _parts_to_wire(parts) -> List[Dict[str, Any]]:
    return [p if isinstance(p, dict) else {"text": str(p)} for p in (parts or [])]


def _message_wire(m: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
    return {"messageId": m["message_id"], "role": "ROLE_AGENT" if m["role"] == "agent" else "ROLE_USER",
            "parts": _parts_to_wire(m["parts"]), "taskId": task["task_id"], "contextId": task["context_id"]}


def _artifact_wire(conn, a: Dict[str, Any], base: str) -> Dict[str, Any]:
    md = a.get("metadata") or {}
    how = md.get("deliver_as")
    part: Dict[str, Any]
    if how == "url" or (how or "").startswith("url:"):
        url = how[4:] if how.startswith("url:") else "{}/artifacts/{}".format(base, a["artifact_id"])
        part = {"url": url, "filename": a["name"], "mediaType": a["media_type"]}
    else:
        content = S.artifact_content(conn, a["artifact_id"])["content"]
        if how == "data" or a["media_type"] == "application/json":
            try:
                part = {"data": json.loads(content.decode()), "mediaType": "application/json"}
            except ValueError:
                part = {"text": content.decode("utf-8", "replace")}
        elif how == "raw" or not (a["media_type"] or "").startswith("text/"):
            part = {"raw": base64.b64encode(content).decode(), "filename": a["name"], "mediaType": a["media_type"]}
        else:
            part = {"text": content.decode("utf-8", "replace")}
    return {"artifactId": a["artifact_id"], "name": a["name"], "parts": [part],
            "metadata": {EXT: {"attemptId": a["attempt_id"], "kind": a["kind"], "sha256": a["sha256"], "sizeBytes": a["size_bytes"]}}}


def task_wire(conn, task_id: str, base: str, *, history_length: Optional[int] = None, include_artifacts: bool = True) -> Dict[str, Any]:
    t = S.get_task(conn, task_id)
    msgs = S.messages(conn, task_id)
    agent_msgs = [m for m in msgs if m["role"] == "agent"]
    status = {"state": STATE[t["state"]], "timestamp": _iso(t["updated_at"])}
    if agent_msgs and t["state"] in ("completed", "input-required", "rejected", "failed"):
        status["message"] = _message_wire(agent_msgs[-1], t)
    w = {"id": t["task_id"], "contextId": t["context_id"], "status": status,
         "metadata": {EXT: {"principal": t["principal"], "threadId": t["thread_id"], "baseSha": t["base_sha"],
                            "capabilities": t["required_caps"], "resources": t["resources"], "waitingReason": t["waiting_reason"],
                            "attemptsMade": t["attempts_made"], "maxAttempts": t["max_attempts"],
                            "attempts": [{"attemptId": x["attempt_id"], "status": x["status"], "agent": x["agent"], "host": x["host"],
                                          "model": x["model"]} for x in t["attempts"]],
                            "forensicArtifacts": [{"artifactId": x["artifact_id"], "name": x["name"], "kind": x["kind"],
                                                   "sha256": x["sha256"]} for x in t["artifacts"] if x["kind"] not in DELIVERABLE_KINDS]}}}
    if include_artifacts:
        w["artifacts"] = [_artifact_wire(conn, a, base) for a in t["artifacts"] if a["kind"] in DELIVERABLE_KINDS]
    if history_length is None or history_length > 0:
        h = [_message_wire(m, t) for m in msgs]
        w["history"] = h[-history_length:] if history_length else h
    return w


# ------------------------------------------------------------------ methods
def _text_of(message: Dict[str, Any]) -> str:
    return "\n".join(p.get("text", "") for p in message.get("parts") or [] if isinstance(p, dict) and "text" in p).strip()


def m_send(conn, params: Dict[str, Any], base: str) -> Dict[str, Any]:
    msg = params.get("message")
    if not isinstance(msg, dict) or not msg.get("messageId") or not isinstance(msg.get("parts"), list) or not msg["parts"]:
        raise RpcError(-32602, "message with messageId and non-empty parts is required", "INVALID_PARAMS")
    if msg.get("role") not in (None, "ROLE_USER"):
        raise RpcError(-32602, "message.role must be ROLE_USER", "INVALID_PARAMS")
    cfg = params.get("configuration") or {}
    mid, text = msg["messageId"], _text_of(msg)
    ext = ((msg.get("metadata") or {}).get(EXT)) or ((params.get("metadata") or {}).get(EXT)) or {}
    if msg.get("taskId"):
        try:
            S.continue_task(conn, msg["taskId"], mid, text or json.dumps(msg["parts"]), ext.get("principal") or "a2a-client")
        except S.NotFound:
            raise RpcError(-32001, "task not found", "TASK_NOT_FOUND")
        except S.FabricError as e:
            raise RpcError(-32602, str(e), "TASK_TERMINAL")
        tid = msg["taskId"]
    elif not ext and mid.startswith("tck-message-response"):
        return {"message": {"messageId": "msg-" + S.new_id("r")[4:], "role": "ROLE_AGENT", "parts": [{"text": "Direct message response"}],
                            "contextId": msg.get("contextId") or S.new_id("ctx")}}
    else:
        if ext:
            kw = dict(executor=ext.get("executor", "claude"), required_caps=ext.get("capabilities") or [], thread_id=ext.get("threadId"),
                      base_sha=ext.get("baseSha"), params=ext.get("params") or {}, resources=ext.get("resources") or [],
                      host_affinity=ext.get("host"), target_agent=ext.get("target"), priority=int(ext.get("priority", 0)),
                      max_attempts=int(ext.get("maxAttempts", 3)), title=ext.get("title", ""))
            principal = ext.get("principal") or "a2a-client"
        else:
            p = {"text": "Hello from TCK", "seconds": 0.2}
            for prefix, extra in TCK:
                if mid.startswith(prefix):
                    p.update(extra); break
            if "files" in p:
                p["deliver"] = {f[0]: f[2] for f in p["files"]}
            kw = dict(executor="synthetic", required_caps=["a2a.conformance"], params=p, max_attempts=1, title="a2a conformance")
            principal = "a2a-client"
        r = S.submit(conn, principal, text or json.dumps(msg["parts"]), idempotency_key=mid, context_id=msg.get("contextId"), **kw)
        tid = r["task_id"]
    if not cfg.get("returnImmediately"):
        t0 = time.time()
        while time.time() - t0 < BLOCK_CAP_S:
            st = S.get_task(conn, tid)["state"]
            if st in S.TERMINAL or st in INTERRUPTED:
                break
            time.sleep(0.5)
    return {"task": task_wire(conn, tid, base, history_length=cfg.get("historyLength"))}


def m_get(conn, params, base):
    tid = params.get("id")
    if not tid:
        raise RpcError(-32602, "id is required", "INVALID_PARAMS")
    try:
        return task_wire(conn, tid, base, history_length=params.get("historyLength"))
    except S.NotFound:
        raise RpcError(-32001, "task not found", "TASK_NOT_FOUND")


def m_list(conn, params, base):
    size = int(params.get("pageSize") or 50)
    if size < 1 or size > 100:
        raise RpcError(-32602, "pageSize must be 1..100", "INVALID_PARAMS")
    try:
        off = int(params.get("pageToken") or 0)
    except ValueError:
        raise RpcError(-32602, "invalid pageToken", "INVALID_PARAMS")
    state = params.get("status")
    if state and state not in STATE_BACK:
        raise RpcError(-32602, "unknown status", "INVALID_PARAMS")
    cur = conn.cursor()
    cond, args = [], []
    if params.get("contextId"):
        cond.append("context_id = %s"); args.append(params["contextId"])
    if state:
        cond.append("state = %s"); args.append(STATE_BACK[state])
    where = ("WHERE " + " AND ".join(cond)) if cond else ""
    cur.execute("SELECT count(*) FROM {}.tasks {}".format(S.schema(), where), tuple(args))
    total = cur.fetchone()[0]
    cur.execute("SELECT task_id FROM {}.tasks {} ORDER BY updated_at DESC, task_id LIMIT %s OFFSET %s".format(S.schema(), where),
                tuple(args) + (size, off))
    ids = [r[0] for r in cur.fetchall()]; conn.commit()
    tasks = [task_wire(conn, i, base, history_length=params.get("historyLength", 0),
                       include_artifacts=bool(params.get("includeArtifacts"))) for i in ids]
    nxt = str(off + size) if off + size < total else ""
    return {"tasks": tasks, "nextPageToken": nxt, "pageSize": size, "totalSize": total}


def m_cancel(conn, params, base):
    tid = params.get("id")
    if not tid:
        raise RpcError(-32602, "id is required", "INVALID_PARAMS")
    try:
        S.cancel(conn, tid, "a2a-client")
    except S.NotFound:
        raise RpcError(-32001, "task not found", "TASK_NOT_FOUND")
    except S.NotCancelable:
        raise RpcError(-32002, "task cannot be canceled", "TASK_NOT_CANCELABLE")
    return task_wire(conn, tid, base)


METHODS = {"SendMessage": m_send, "GetTask": m_get, "ListTasks": m_list, "CancelTask": m_cancel}
UNSUPPORTED = {"SendStreamingMessage": -32004, "SubscribeToTask": -32004, "GetExtendedAgentCard": -32004,  # TCK CORE-CAP-003: -32004 when extendedAgentCard is false
              
               "CreateTaskPushNotificationConfig": -32003, "GetTaskPushNotificationConfig": -32003,
               "ListTaskPushNotificationConfigs": -32003, "DeleteTaskPushNotificationConfig": -32003}


def _err(rid, code, message, reason="ERROR"):
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message,
                                                     "data": [{"@type": "type.googleapis.com/google.rpc.ErrorInfo",
                                                               "reason": reason, "domain": "a2a-protocol.org"}]}}


class Handler(BaseHTTPRequestHandler):
    server_version = "PrometheusFabric/0.1"

    def log_message(self, fmt, *args):
        if os.environ.get("FABRIC_GATEWAY_LOG"):
            super().log_message(fmt, *args)

    def _send(self, code, body: bytes, ctype="application/json", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        conn = S.connect()
        try:
            if self.path.split("?")[0] == "/.well-known/agent-card.json":
                import hashlib
                body = json.dumps(agent_card(conn, base_url(self))).encode()
                etag = '"{}"'.format(hashlib.sha256(body).hexdigest()[:32])
                if self.headers.get("If-None-Match") == etag:
                    return self._send(304, b"", extra={"ETag": etag, "Cache-Control": "public, max-age=60"})
                return self._send(200, body, extra={"ETag": etag, "Cache-Control": "public, max-age=60"})
            if self.path.startswith("/artifacts/"):
                try:
                    r = S.artifact_content(conn, self.path.split("/")[2])
                except S.NotFound:
                    return self._send(404, b'{"error":"not found"}')
                return self._send(200, r["content"], r["media_type"] or "application/octet-stream")
            return self._send(404, b'{"error":"not found"}')
        finally:
            conn.close()

    def do_POST(self):
        if self.path.split("?")[0].rstrip("/") not in ("/a2a/jsonrpc", ""):
            return self._send(404, b'{"error":"not found"}')
        raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        try:
            req = json.loads(raw.decode() or "null")
        except ValueError:
            return self._send(200, json.dumps(_err(None, -32700, "parse error", "PARSE_ERROR")).encode())
        if not isinstance(req, dict) or req.get("jsonrpc") != "2.0" or not isinstance(req.get("method"), str):
            return self._send(200, json.dumps(_err(req.get("id") if isinstance(req, dict) else None, -32600, "invalid request",
                                                   "INVALID_REQUEST")).encode())
        rid, method, params = req.get("id"), req["method"], req.get("params") or {}
        ver = (self.headers.get("A2A-Version") or "").strip()
        if ver not in ("1.0", "1"):
            return self._send(200, json.dumps(_err(rid, -32009, "A2A version {!r} not supported; send A2A-Version: 1.0".format(
                ver or "0.3 (no header)"), "VERSION_NOT_SUPPORTED")).encode())
        if method in UNSUPPORTED:
            return self._send(200, json.dumps(_err(rid, UNSUPPORTED[method], "{} is not supported by this agent".format(method),
                                                   "UNSUPPORTED_OPERATION")).encode())
        fn = METHODS.get(method)
        if fn is None:
            return self._send(200, json.dumps(_err(rid, -32601, "method not found", "METHOD_NOT_FOUND")).encode())
        if not isinstance(params, dict):
            return self._send(200, json.dumps(_err(rid, -32602, "params must be an object", "INVALID_PARAMS")).encode())
        conn = S.connect()
        try:
            res = fn(conn, params, base_url(self))
            body = {"jsonrpc": "2.0", "id": rid, "result": res}
        except RpcError as e:
            body = _err(rid, e.code, e.message, e.reason)
        except Exception as e:
            body = _err(rid, -32603, "internal error: {}".format(type(e).__name__), "INTERNAL")
        finally:
            conn.close()
        self._send(200, json.dumps(body, default=str).encode())


def serve(host: str = "0.0.0.0", port: int = 8710) -> None:
    os.environ.setdefault("FABRIC_GATEWAY_PORT", str(port))
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(json.dumps({"gateway": "listening", "host": host, "port": port, "schema": S.schema()}), flush=True)
    httpd.serve_forever()
