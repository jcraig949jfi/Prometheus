"""Must-fail check for explib/tests/test_core_isolation.py: the same child blocker must REJECT an engine import.
Writes a temporary test into a scratch copy of the core tests (never into pkg/), runs the child, expects rc != 0."""
import overlay, shutil, subprocess, sys, os, pathlib
src = overlay.HERE / "pkg/prometheus/explib/tests/test_core_isolation.py"
ns = {}
code = src.read_text()
CHILD = code[code.index("CHILD = r'''") + len("CHILD = r'''"):code.index("'''\n\n\ndef test_core")]
d = overlay.HERE / "dev/mustfail"
(d / "test_engine_leak.py").write_text("def test_leak():\n    import prometheus.ananke.envs\n")
(d / "test_torch_leak.py").write_text("def test_leak():\n    import torch\n")
import prometheus
env = dict(os.environ, PROMETHEUS_EXTRA_PATHS=os.pathsep.join(prometheus.__path__))
boot = ("import os, sys\npaths=[p for p in os.environ['PROMETHEUS_EXTRA_PATHS'].split(os.pathsep) if p]\n"
        "sys.path[:0]=[os.path.dirname(p) for p in paths]\nimport prometheus\n"
        "[prometheus.__path__.append(p) for p in paths if p not in prometheus.__path__]\n")
for t in ("test_engine_leak.py", "test_torch_leak.py"):
    r = subprocess.run([sys.executable, "-c", boot + CHILD, str(d / t)], env=env, capture_output=True, text=True)
    print(t, "rc", r.returncode, "BLOCKED" in r.stdout + r.stderr)
