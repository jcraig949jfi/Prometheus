"""Credential-isolated, stdlib-only AETH-01 artifact service (no GPU imports).

Launch: python3 /app/pod_service.py; listens on 0.0.0.0:8080. Required env:
AGE_ARTIFACT_TOKEN (nonempty printable ASCII without whitespace), AETH01_RUN_ID
(nonempty, <=256 characters, no whitespace). AETH01_CANARY_TIMEOUT_SECONDS is
an ASCII integer 1..600, default 600. Never provision RunPod API credentials on
the pod; only the external controller may use them or terminate the pod.

GET /receipt.json, /canary.log, /result.json require Authorization: Bearer TOKEN.
All other paths (including queries/encoded aliases) are 404. Missing artifacts
are 404; oversized artifacts are 413. Reads and stored logs are capped at 4 MiB
(result: 4 KiB). Logs retain the first bytes; excess output is drained/discarded.
Receipts/logs may be provisional; result.json exists only after cleanup and is
atomic JSON {run_id, exit_code, finished: true}. Timeout is 124; launch failure
is 127; a zero exit without a readable, final, run-bound PASS receipt becomes 1.
The controller must still validate the receipt/schema, not just the exit code.

Artifacts live in a fresh private temporary directory, not a reused receipt
directory. Child env is allowlisted and NEVER includes AGE_ARTIFACT_TOKEN or
RunPod credentials. Linux children start in a new session; the process group
is SIGKILLed on timeout (and any residual descendants on normal completion).
The HTTP service stays alive after completion so the controller can retrieve
artifacts BEFORE terminating the pod. This does NOT stop pod billing. No
request/error logs, credentials in argv, RunPod API calls, or outbound HTTP.
Use the provider's HTTPS proxy; the in-container listener itself is plain HTTP.
"""

import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import tempfile
import threading


ARTIFACT_LIMIT = 4 * 1024 * 1024
RESULT_LIMIT = 4096
RUNNER_PATH = Path(__file__).resolve().with_name("run_canary.py")
ARTIFACTS = {
    "/receipt.json": ("receipt.json", "application/json", ARTIFACT_LIMIT),
    "/canary.log": ("canary.log", "text/plain; charset=utf-8", ARTIFACT_LIMIT),
    "/result.json": ("result.json", "application/json", RESULT_LIMIT),
}
CHILD_ENV_NAMES = (
    "PATH", "LD_LIBRARY_PATH", "CUDA_VISIBLE_DEVICES", "CUDA_DEVICE_ORDER",
    "NVIDIA_VISIBLE_DEVICES", "NVIDIA_DRIVER_CAPABILITIES", "SYSTEMROOT", "WINDIR",
    "AETH01_CANARY_REQUIRE_GPU", "AETH01_CANARY_HOURLY_RATE",
    "AETH01_CANARY_MAX_DOLLAR_BUDGET",
)


def load_config(environ):
    """Validate before opening a listener or starting any child; never echo input."""
    token = environ.get("AGE_ARTIFACT_TOKEN", "")
    if not token or len(token) > 4096 or any(not 33 <= ord(c) <= 126 for c in token):
        raise ValueError("AGE_ARTIFACT_TOKEN must be nonempty printable ASCII without whitespace")
    run_id = environ.get("AETH01_RUN_ID", "")
    if not run_id or len(run_id) > 256 or any(c.isspace() or ord(c) < 32 for c in run_id):
        raise ValueError("AETH01_RUN_ID must be nonempty, <=256 characters, without whitespace")
    raw_timeout = environ.get("AETH01_CANARY_TIMEOUT_SECONDS", "600")
    if (not raw_timeout or len(raw_timeout) > 3
            or any(c not in "0123456789" for c in raw_timeout)
            or not 1 <= int(raw_timeout) <= 600):
        raise ValueError("AETH01_CANARY_TIMEOUT_SECONDS must be an integer in 1..600")
    if any(name.upper() in {"RUNPOD_API_KEY", "RUNPOD_API_TOKEN", "RUNPOD_TOKEN"}
           for name in environ):
        raise ValueError("RunPod API credentials must stay off-pod")
    return token, run_id, int(raw_timeout)


def child_environment(environ, artifact_dir, run_id, timeout):
    env = {name: environ[name] for name in CHILD_ENV_NAMES if name in environ}
    env.update({
        "HOME": str(artifact_dir), "TMPDIR": str(artifact_dir),
        "TEMP": str(artifact_dir), "TMP": str(artifact_dir),
        "PYTHONUNBUFFERED": "1", "PYTHONNOUSERSITE": "1",
        "AETH01_RUN_ID": run_id, "AETH01_CANARY_TIMEOUT_SECONDS": str(timeout),
    })
    return env


def read_artifact(path, limit):
    """Read only bounded regular files, without following a final symlink."""
    if path.is_symlink():
        raise FileNotFoundError
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    flags |= getattr(os, "O_BINARY", 0)
    with os.fdopen(os.open(path, flags), "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise FileNotFoundError
        if info.st_size > limit:
            raise ValueError("artifact exceeds limit")
        payload = stream.read(limit + 1)
    if len(payload) > limit:
        raise ValueError("artifact exceeds limit")
    return payload


def write_result(artifact_dir, run_id, exit_code):
    payload = {"run_id": run_id, "exit_code": exit_code, "finished": True}
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=artifact_dir,
            prefix="result.", suffix=".tmp", delete=False,
        ) as stream:
            temporary = stream.name
            json.dump(payload, stream, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, artifact_dir / "result.json")
    finally:
        if temporary is not None and os.path.exists(temporary):
            os.unlink(temporary)


def has_success_receipt(artifact_dir, run_id):
    try:
        receipt = json.loads(read_artifact(artifact_dir / "receipt.json", ARTIFACT_LIMIT))
        return (isinstance(receipt, dict) and receipt.get("status") == "PASS"
                and receipt.get("run_id") == run_id
                and isinstance(receipt.get("finished_at_utc"), str)
                and bool(receipt["finished_at_utc"]))
    except (OSError, ValueError, RecursionError):
        return False


def kill_child_group(child):
    """The new session's PGID equals the child PID, even after its leader exits."""
    try:
        if sys.platform == "linux":
            os.killpg(child.pid, signal.SIGKILL)
        elif child.poll() is None:
            child.kill()
    except ProcessLookupError:
        pass


def drain_log(pipe, log_path, failed):
    """Bound disk and memory while continuing to drain a noisy child's pipe."""
    try:
        with pipe, log_path.open("wb", buffering=0) as log:
            remaining = ARTIFACT_LIMIT
            while True:
                chunk = pipe.read(65536)
                if not chunk:
                    break
                if remaining:
                    kept = chunk[:remaining]
                    log.write(kept)
                    remaining -= len(kept)
    except (OSError, ValueError):
        failed.set()


def run_child(artifact_dir, run_id, timeout, env):
    """Run only the bundled script, not an imported GPU module; publish final once."""
    child = None
    reader = None
    failed = threading.Event()
    exit_code = 127
    # Ensure the log is available even if Popen fails. Never reuse old artifacts.
    (artifact_dir / "canary.log").touch(exist_ok=False)
    try:
        child = subprocess.Popen(
            [sys.executable, "-u", str(RUNNER_PATH)], cwd=artifact_dir, env=env,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            start_new_session=(sys.platform == "linux"), bufsize=0,
        )
        reader = threading.Thread(
            target=drain_log, args=(child.stdout, artifact_dir / "canary.log", failed),
            daemon=True,
        )
        reader.start()
        try:
            exit_code = child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            exit_code = 124
    except (OSError, RuntimeError):
        exit_code = 127 if child is None else 1
    finally:
        if child is not None:
            kill_child_group(child)
            child.wait(timeout=5)
        if reader is not None:
            reader.join(timeout=5)
            if reader.is_alive():
                # Do not publish finished while output can still be changing.
                raise RuntimeError("child log did not finish")
            if failed.is_set():
                exit_code = 124 if exit_code == 124 else 1
    if exit_code == 0 and not has_success_receipt(artifact_dir, run_id):
        exit_code = 1
    write_result(artifact_dir, run_id, exit_code)


class ArtifactServer(HTTPServer):
    """One bounded request at a time; child supervision uses its own thread."""

    def __init__(self, address, artifact_dir, token):
        self.artifact_dir = artifact_dir
        self.authorization = ("Bearer " + token).encode("ascii")
        super().__init__(address, ArtifactHandler)

    def handle_error(self, request, client_address):
        # Suppress tracebacks as well as access logs; never log request data.
        pass


class ArtifactHandler(BaseHTTPRequestHandler):
    def setup(self):
        self.request.settimeout(5)
        super().setup()

    def log_message(self, format, *args):
        pass

    def send_error(self, code, message=None, explain=None):
        self.reply(code)

    def reply(self, code, payload=b"", content_type="text/plain"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        if payload:
            self.wfile.write(payload)

    def do_GET(self):
        headers = self.headers.get_all("Authorization", [])
        supplied = headers[0].encode("latin-1") if len(headers) == 1 else b""
        if not hmac.compare_digest(supplied, self.server.authorization):
            self.reply(401)
            return
        # BaseHTTPRequestHandler normalizes leading //; reject those aliases too.
        target = self.requestline.split()[1]
        artifact = ARTIFACTS.get(target)
        if artifact is None:
            self.reply(404)
            return
        name, content_type, limit = artifact
        try:
            payload = read_artifact(self.server.artifact_dir / name, limit)
        except FileNotFoundError:
            self.reply(404)
        except ValueError:
            self.reply(413)
        except OSError:
            self.reply(500)
        else:
            self.reply(200, payload, content_type)


def main():
    try:
        token, run_id, timeout = load_config(os.environ)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)  # Validation messages contain no values.
        return 2
    with tempfile.TemporaryDirectory(prefix="aeth01-artifacts-") as directory:
        artifact_dir = Path(directory)
        env = child_environment(os.environ, artifact_dir, run_id, timeout)
        # Bind before starting expensive work: a listener failure launches no child.
        with ArtifactServer(("0.0.0.0", 8080), artifact_dir, token) as server:
            def supervise():
                try:
                    run_child(artifact_dir, run_id, timeout, env)
                except Exception:
                    # Missing result remains a failure; never fabricate success.
                    print("[pod_service] supervision failed; controller must terminate pod", file=sys.stderr)

            threading.Thread(target=supervise, daemon=True).start()
            print("[pod_service] artifact listener active; pod billing continues until external termination",
                  file=sys.stderr)
            server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())