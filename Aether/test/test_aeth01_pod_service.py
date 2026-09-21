"""Offline stdlib tests: in-memory HTTP, temporary files, synthetic subprocesses.

No listener/network, GPU imports, real credentials, provider API, or paid calls.
Run directly with python Aether/test/test_aeth01_pod_service.py (or via pytest).
Linux additionally checks real process-group cleanup and the legacy shell wrapper.
"""

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


CANARY_DIR = Path(__file__).resolve().parents[1] / "runpod" / "aeth01_canary"


def load_service():
    spec = importlib.util.spec_from_file_location("_aeth01_pod_service_test", CANARY_DIR / "pod_service.py")
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {
        "numpy": None, "cupy": None, "run_canary": None,
        "aeth01_gpu_kernel": None, "aeth01_cpu_oracle": None,
    }):
        spec.loader.exec_module(module)
    return module


class MemorySocket:
    """Exercise the real stdlib HTTP parser/handler without opening a socket."""

    def __init__(self, request):
        self.input = io.BytesIO(request)
        self.output = bytearray()
        self.timeout = None

    def settimeout(self, value):
        self.timeout = value

    def makefile(self, mode, buffering):
        assert mode == "rb"
        return self.input

    def sendall(self, data):
        self.output.extend(data)


class PodServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = load_service()
        temporary = tempfile.TemporaryDirectory(prefix="test-aeth01-service-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.token = secrets.token_urlsafe(24)  # Synthetic, never printed or sent over a network.
        self.run_id = "offline-synthetic-run"
        self.config = {"AGE_ARTIFACT_TOKEN": self.token, "AETH01_RUN_ID": self.run_id}

    def request(self, path, authorization=True, method="GET", extra_headers=(), root=None):
        headers = []
        if authorization is True:
            headers.append("Authorization: Bearer " + self.token)
        elif authorization is not None:
            headers.append("Authorization: " + authorization)
        headers.extend(extra_headers)
        raw = (f"{method} {path} HTTP/1.1\r\nHost: offline.invalid\r\n"
               + "\r\n".join(headers) + "\r\n\r\n").encode("latin-1")
        connection = MemorySocket(raw)
        server = SimpleNamespace(
            artifact_dir=root or self.root, authorization=("Bearer " + self.token).encode("ascii"),
        )
        output = io.StringIO()
        with redirect_stderr(output), redirect_stdout(output):
            self.service.ArtifactHandler(connection, ("127.0.0.1", 0), server)
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(connection.timeout, 5)
        head, body = bytes(connection.output).split(b"\r\n\r\n", 1)
        lines = head.split(b"\r\n")
        status = int(lines[0].split()[1])
        response_headers = dict(line.split(b": ", 1) for line in lines[1:])
        self.assertEqual(int(response_headers[b"Content-Length"]), len(body))
        self.assertEqual(response_headers[b"Cache-Control"], b"no-store")
        return status, body

    def receipt(self, **changes):
        value = {"status": "PASS", "run_id": self.run_id, "finished_at_utc": "2026-01-01T00:00:00Z"}
        value.update(changes)
        (self.root / "receipt.json").write_text(json.dumps(value), encoding="utf-8")

    def child_env(self, timeout=5):
        # Only the service's explicit allowlist is read from the real environment.
        source = {name: os.environ[name] for name in self.service.CHILD_ENV_NAMES if name in os.environ}
        return self.service.child_environment(source, self.root, self.run_id, timeout)

    def run_stub(self, source, timeout=5):
        runner = self.root / "synthetic_runner.py"
        runner.write_text(source, encoding="utf-8")
        with patch.object(self.service, "RUNNER_PATH", runner):
            self.service.run_child(self.root, self.run_id, timeout, self.child_env(timeout))
        result = json.loads((self.root / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(set(result), {"run_id", "exit_code", "finished"})
        self.assertEqual(result["run_id"], self.run_id)
        self.assertIs(result["finished"], True)
        return result

    def test_import_is_gpu_and_runner_isolated(self):
        self.assertEqual(self.service.RUNNER_PATH, CANARY_DIR / "run_canary.py")

    def test_config_accepts_bounds_and_default(self):
        self.assertEqual(self.service.load_config(self.config)[1:], (self.run_id, 600))
        for value in ("1", "9", "001", "600"):
            with self.subTest(value=value):
                config = dict(self.config, AETH01_CANARY_TIMEOUT_SECONDS=value)
                self.assertEqual(self.service.load_config(config)[2], int(value))

    def test_invalid_timeout_auth_run_binding_fail_before_child_or_listener(self):
        configs = [dict(self.config, AETH01_CANARY_TIMEOUT_SECONDS=value) for value in (
            "", "0", "000", "-1", "601", "1.5", "1e2", "+1", " 1", "1\n", "\u0661", "9" * 5000,
        )]
        configs += [dict(self.config, AGE_ARTIFACT_TOKEN=value) for value in ("", " ", "x\ny", "\u00ff")]
        configs += [{"AETH01_RUN_ID": self.run_id}]
        configs += [dict(self.config, AETH01_RUN_ID=value) for value in ("", "bad id", "a" * 257)]
        configs += [{"AGE_ARTIFACT_TOKEN": self.token}]
        for config in configs:
            with patch.dict(os.environ, config, clear=True), patch.object(self.service, "ArtifactServer") as server:
                with patch.object(self.service.subprocess, "Popen") as child, redirect_stderr(io.StringIO()):
                    self.assertEqual(self.service.main(), 2)
                    server.assert_not_called()
                    child.assert_not_called()

    def test_rejects_provider_credential_variable_names(self):
        for name in ("RUNPOD_API_KEY", "RUNPOD_API_TOKEN", "runpod_token"):
            # Empty marker only: there are no provider credentials in these tests.
            with self.assertRaises(ValueError):
                self.service.load_config(dict(self.config, **{name: ""}))

    def test_minimal_child_environment_excludes_auth_and_arbitrary_inheritance(self):
        source = dict(self.config, PATH="/usr/bin", LD_LIBRARY_PATH="/usr/local/cuda/lib64",
                      CUDA_VISIBLE_DEVICES="0", PYTHONPATH="untrusted", RUNPOD_API_KEY="",
                      ARBITRARY_VARIABLE="do-not-inherit", AETH01_CANARY_REQUIRE_GPU="0")
        env = self.service.child_environment(source, self.root, self.run_id, 7)
        for name in ("AGE_ARTIFACT_TOKEN", "RUNPOD_API_KEY", "PYTHONPATH", "ARBITRARY_VARIABLE"):
            self.assertNotIn(name, env)
        self.assertNotIn(self.token, env.values())
        self.assertEqual(env["AETH01_RUN_ID"], self.run_id)
        self.assertEqual(env["AETH01_CANARY_TIMEOUT_SECONDS"], "7")
        self.assertEqual(env["LD_LIBRARY_PATH"], source["LD_LIBRARY_PATH"])
        self.assertEqual(env["AETH01_CANARY_REQUIRE_GPU"], "0")
        self.assertEqual(env["HOME"], str(self.root))

    def test_all_three_exact_endpoints_require_bearer_constant_time_auth(self):
        for name in ("receipt.json", "canary.log", "result.json"):
            (self.root / name).write_bytes(b"synthetic-artifact")
        for path in self.service.ARTIFACTS:
            for auth in (None, "", "Bearer wrong", "Basic wrong", "Bearer \xff"):
                self.assertEqual(self.request(path, authorization=auth), (401, b""))
            self.assertEqual(self.request(path), (200, b"synthetic-artifact"))
        with patch.object(self.service.hmac, "compare_digest", wraps=self.service.hmac.compare_digest) as compare:
            self.assertEqual(self.request("/receipt.json")[0], 200)
            self.assertEqual(compare.call_count, 1)
            self.assertTrue(all(isinstance(arg, bytes) for arg in compare.call_args.args))
        self.assertEqual(self.request("/receipt.json", extra_headers=("Authorization: Bearer other",))[0], 401)
        self.assertEqual(self.request("/does-not-exist", authorization=None)[0], 401)

    def test_no_listings_traversal_aliases_or_other_files(self):
        (self.root / "receipt.json").write_bytes(b"receipt")
        (self.root / "private.txt").write_bytes(b"not-an-artifact")
        for path in (
            "/", "/../receipt.json", "/%2e%2e/receipt.json", "/%72eceipt.json",
            "/receipt.json?query=1", "/receipt.json#fragment", "/receipt.json/",
            "/private.txt", "/result.tmp", "//receipt.json", "///receipt.json",
            "http://offline.invalid/receipt.json", "/sub/../receipt.json", "/RECEIPT.JSON",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.request(path), (404, b""))
        for method in ("POST", "PUT", "DELETE", "HEAD"):
            self.assertEqual(self.request("/receipt.json", method=method), (501, b""))

    def test_missing_artifacts_and_oversized_reads(self):
        for path, (name, _, limit) in self.service.ARTIFACTS.items():
            self.assertEqual(self.request(path), (404, b""))
            with (self.root / name).open("wb") as stream:
                stream.truncate(limit + 1)
            self.assertEqual(self.request(path), (413, b""))
        with patch.object(self.service.os, "open", side_effect=OSError("not echoed")):
            self.assertEqual(self.request("/receipt.json"), (500, b""))

    def test_read_is_bounded_even_if_size_metadata_is_stale(self):
        path = self.root / "receipt.json"
        path.write_bytes(b"0123456789")
        with patch.object(self.service.os, "fstat", return_value=SimpleNamespace(st_mode=0o100600, st_size=0)):
            with self.assertRaises(ValueError):
                self.service.read_artifact(path, 4)

    @unittest.skipUnless(sys.platform == "linux", "POSIX symlinks/FIFOs")
    def test_symlinks_and_nonregular_artifacts_are_not_served(self):
        outside = self.root / "private.txt"
        outside.write_bytes(b"private")
        (self.root / "receipt.json").symlink_to(outside)
        os.mkfifo(self.root / "canary.log")
        self.assertEqual(self.request("/receipt.json"), (404, b""))
        self.assertEqual(self.request("/canary.log"), (404, b""))

    def test_log_drain_caps_storage_and_consumes_excess(self):
        failed = threading.Event()
        pipe = io.BytesIO(b"abcdefgh" * 100000)
        with patch.object(self.service, "ARTIFACT_LIMIT", 100):
            self.service.drain_log(pipe, self.root / "canary.log", failed)
        self.assertTrue(pipe.closed)
        self.assertFalse(failed.is_set())
        self.assertEqual((self.root / "canary.log").read_bytes(), (b"abcdefgh" * 13)[:100])

    def test_zero_without_final_bound_pass_receipt_is_never_success(self):
        self.assertFalse(self.service.has_success_receipt(self.root, self.run_id))
        for changes in ({"status": "FAIL_INCOMPLETE"}, {"status": "FAIL_ERROR"},
                        {"run_id": "old-run"}, {"finished_at_utc": None}, {"finished_at_utc": ""}):
            self.receipt(**changes)
            self.assertFalse(self.service.has_success_receipt(self.root, self.run_id))
        for data in (b"not json", b"null", b"[]", b"{", b"\xff"):
            (self.root / "receipt.json").write_bytes(data)
            self.assertFalse(self.service.has_success_receipt(self.root, self.run_id))
        self.receipt()
        self.assertTrue(self.service.has_success_receipt(self.root, self.run_id))

    def test_result_is_final_atomic_fsynced_and_not_visible_before_replace(self):
        real_replace, real_fsync = self.service.os.replace, self.service.os.fsync
        events = []

        def fsync(fd):
            real_fsync(fd)
            events.append("fsync")

        def replace(source, target):
            self.assertEqual(events, ["fsync"])
            self.assertEqual(Path(source).parent, self.root)
            self.assertEqual(self.request("/result.json"), (404, b""))
            self.assertIs(json.loads(Path(source).read_text(encoding="utf-8"))["finished"], True)
            real_replace(source, target)
            events.append("replace")

        with patch.object(self.service.os, "fsync", side_effect=fsync):
            with patch.object(self.service.os, "replace", side_effect=replace):
                self.service.write_result(self.root, self.run_id, 124)
        self.assertEqual(events, ["fsync", "replace"])
        status, body = self.request("/result.json")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"run_id": self.run_id, "exit_code": 124, "finished": True})
        self.assertEqual(list(self.root.iterdir()), [self.root / "result.json"])

    def test_failed_atomic_write_cleans_temp_and_never_publishes_partial_result(self):
        for operation in ("fsync", "replace"):
            with patch.object(self.service.os, operation, side_effect=OSError("synthetic failure")):
                with self.assertRaises(OSError):
                    self.service.write_result(self.root, self.run_id, 1)
            self.assertEqual(list(self.root.iterdir()), [])
            self.assertEqual(self.request("/result.json")[0], 404)

    def test_launch_failure_publishes_nonzero_result_and_empty_log(self):
        with patch.object(self.service.subprocess, "Popen", side_effect=OSError("synthetic launch failure")):
            self.service.run_child(self.root, self.run_id, 1, self.child_env(1))
        self.assertEqual(json.loads((self.root / "result.json").read_bytes())["exit_code"], 127)
        self.assertEqual(self.request("/canary.log"), (200, b""))
        self.assertEqual(self.request("/receipt.json")[0], 404)

    def test_linux_timeout_uses_new_session_and_sigkill_on_whole_process_group(self):
        child = Mock(pid=12345, stdout=io.BytesIO(b"partial output\n"))
        child.wait.side_effect = [subprocess.TimeoutExpired("synthetic", 1), -9]
        env = self.child_env(1)
        with patch.object(self.service.sys, "platform", "linux"):
            with patch.object(self.service.os, "killpg", create=True) as killpg:
                with patch.object(self.service.signal, "SIGKILL", 9, create=True):
                    with patch.object(self.service.subprocess, "Popen", return_value=child) as popen:
                        self.service.run_child(self.root, self.run_id, 1, env)
        killpg.assert_called_once_with(12345, 9)
        kwargs = popen.call_args.kwargs
        self.assertIs(kwargs["start_new_session"], True)
        self.assertEqual(kwargs["stdin"], subprocess.DEVNULL)
        self.assertEqual(kwargs["stderr"], subprocess.STDOUT)
        self.assertIs(kwargs["env"], env)
        self.assertNotIn("AGE_ARTIFACT_TOKEN", env)
        self.assertEqual(popen.call_args.args[0], [sys.executable, "-u", str(self.service.RUNNER_PATH)])
        self.assertEqual(json.loads((self.root / "result.json").read_bytes())["exit_code"], 124)

    def test_subprocess_success_bound_receipt_and_both_output_streams(self):
        result = self.run_stub(
            "import json, os, sys\n"
            "assert 'AGE_ARTIFACT_TOKEN' not in os.environ\n"
            "assert not any(k.startswith('RUNPOD_') for k in os.environ)\n"
            "print('synthetic stdout')\nprint('synthetic stderr', file=sys.stderr)\n"
            "with open('receipt.json', 'w') as f:\n"
            "    json.dump(dict(status='PASS', run_id=os.environ['AETH01_RUN_ID'], finished_at_utc='synthetic'), f)\n"
        )
        self.assertEqual(result["exit_code"], 0)
        status, body = self.request("/canary.log")
        self.assertEqual(status, 200)
        self.assertEqual(body.replace(b"\r\n", b"\n"), b"synthetic stdout\nsynthetic stderr\n")
        self.assertEqual(json.loads(self.request("/receipt.json")[1])["run_id"], self.run_id)

    def test_running_child_has_no_result_until_exit_and_log_cleanup(self):
        runner = self.root / "synthetic_runner.py"
        runner.write_text(
            "import pathlib, time\n"
            "print('started', flush=True)\n"
            "pathlib.Path('ready').touch()\n"
            "while not pathlib.Path('release').exists():\n"
            "    time.sleep(0.01)\n"
            "print('finished', flush=True)\n",
            encoding="utf-8",
        )
        errors = []

        def supervise():
            try:
                self.service.run_child(self.root, self.run_id, 5, self.child_env())
            except Exception as exc:
                errors.append(type(exc).__name__)

        with patch.object(self.service, "RUNNER_PATH", runner):
            worker = threading.Thread(target=supervise, daemon=True)
            worker.start()
            try:
                deadline = time.monotonic() + 3
                while not (self.root / "ready").exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue((self.root / "ready").exists())
                self.assertEqual(self.request("/result.json"), (404, b""))
                self.assertEqual(self.request("/canary.log")[0], 200)
            finally:
                (self.root / "release").touch()
                worker.join(timeout=15)
        self.assertFalse(worker.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(json.loads(self.request("/result.json")[1])["exit_code"], 1)
        self.assertEqual(self.request("/canary.log")[1].replace(b"\r\n", b"\n"), b"started\nfinished\n")

    def test_subprocess_zero_exit_missing_receipt_becomes_failure(self):
        self.assertEqual(self.run_stub("print('no receipt')\n")["exit_code"], 1)
        self.assertEqual(self.request("/receipt.json")[0], 404)

    def test_subprocess_nonzero_exit_is_preserved(self):
        self.assertEqual(self.run_stub("import sys\nsys.exit(7)\n")["exit_code"], 7)

    def test_noisy_subprocess_does_not_block_after_log_cap(self):
        with patch.object(self.service, "ARTIFACT_LIMIT", 1024):
            result = self.run_stub("import sys\nsys.stdout.write('x' * 2000000)\nsys.exit(3)\n")
        self.assertEqual(result["exit_code"], 3)
        self.assertEqual((self.root / "canary.log").stat().st_size, 1024)

    def test_subprocess_timeout_keeps_partial_artifacts_and_final_124(self):
        self.receipt(status="FAIL_INCOMPLETE", finished_at_utc=None)
        result = self.run_stub("import time\nprint('before timeout', flush=True)\ntime.sleep(30)\n", timeout=1)
        self.assertEqual(result["exit_code"], 124)
        self.assertEqual(self.request("/canary.log")[1].replace(b"\r\n", b"\n"), b"before timeout\n")
        self.assertEqual(self.request("/receipt.json")[0], 200)

    @unittest.skipUnless(sys.platform == "linux", "real Linux process-group regression")
    def test_timeout_kills_term_ignoring_descendant_not_just_leader(self):
        grandchild = (
            "import os, signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
            "open('grandchild.pid', 'w').write(str(os.getpid())); time.sleep(30)"
        )
        try:
            result = self.run_stub(
                "import os, subprocess, sys, time\n"
                "open('leader.pid', 'w').write(str(os.getpid()))\n"
                f"subprocess.Popen([sys.executable, '-c', {grandchild!r}])\n"
                "time.sleep(30)\n", timeout=3,
            )
            self.assertEqual(result["exit_code"], 124)
            pid = int((self.root / "grandchild.pid").read_text())
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                try:
                    state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
                except FileNotFoundError:
                    break
                if state == "Z":  # Dead; reaping an orphan belongs to PID 1.
                    break
                time.sleep(0.02)
            else:
                self.fail("descendant remained live after timeout")
        finally:
            leader = self.root / "leader.pid"
            if leader.exists():
                try:
                    os.killpg(int(leader.read_text()), 9)
                except ProcessLookupError:
                    pass

    def test_main_serves_after_child_finishes_and_uses_fixed_port_fresh_directory(self):
        class StopServing(Exception):
            pass

        class InlineThread:
            def __init__(self, target, daemon):
                self.target = target

            def start(self):
                self.target()

        for exit_code in (0, 1, 124):
            events = []

            def server_factory(address, directory, token):
                self.assertEqual(address, ("0.0.0.0", 8080))
                self.assertTrue(token == self.token)
                self.assertEqual(list(directory.iterdir()), [])
                events.append("bound")
                server = Mock()
                server.__enter__ = Mock(return_value=server)
                server.__exit__ = Mock(return_value=False)

                def serve():
                    self.assertEqual(events, ["bound", "child-finished"])
                    self.assertEqual(json.loads(self.request("/result.json", root=directory)[1])["exit_code"], exit_code)
                    raise StopServing

                server.serve_forever.side_effect = serve
                return server

            def child(directory, run_id, timeout, env):
                self.assertEqual(run_id, self.run_id)
                self.assertNotIn("AGE_ARTIFACT_TOKEN", env)
                self.service.write_result(directory, run_id, exit_code)
                events.append("child-finished")

            with patch.dict(os.environ, self.config, clear=True), redirect_stderr(io.StringIO()):
                with patch.object(self.service, "ArtifactServer", side_effect=server_factory):
                    with patch.object(self.service, "run_child", side_effect=child):
                        with patch.object(self.service.threading, "Thread", InlineThread):
                            with self.assertRaises(StopServing):
                                self.service.main()

    def test_bind_failure_never_starts_child(self):
        with patch.dict(os.environ, self.config, clear=True):
            with patch.object(self.service, "ArtifactServer", side_effect=OSError("busy")):
                with patch.object(self.service.subprocess, "Popen") as child:
                    with self.assertRaises(OSError):
                        self.service.main()
                    child.assert_not_called()

    def test_image_uses_system_python_and_service_entrypoint(self):
        dockerfile = (CANARY_DIR / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("python3 python3-pip", dockerfile)
        self.assertIn("python3 -m pip install --no-cache-dir numpy cupy-cuda12x", dockerfile)
        self.assertNotIn("python3.11", dockerfile)
        self.assertIn("pod_service.py watchdog.sh /app/", dockerfile)
        self.assertIn('CMD ["python3", "/app/pod_service.py"]', dockerfile)
        self.assertIn("EXPOSE 8080", dockerfile)

    @unittest.skipUnless(sys.platform == "linux" and shutil.which("bash"), "Linux bash wrapper")
    def test_legacy_watchdog_rejects_zero_and_invalid_timeout_before_command(self):
        marker = self.root / "must-not-run"
        for value in ("0", "000", "", "601", "-1", "1.5", "not-an-integer"):
            env = self.child_env()
            env["AETH01_CANARY_TIMEOUT_SECONDS"] = value
            completed = subprocess.run(
                [shutil.which("bash"), str(CANARY_DIR / "watchdog.sh"), sys.executable, "-c",
                 "from pathlib import Path; Path('must-not-run').touch()"],
                env=env, cwd=self.root, capture_output=True, timeout=5,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()