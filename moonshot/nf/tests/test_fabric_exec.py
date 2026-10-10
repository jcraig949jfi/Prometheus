"""C-012-T003: the approved Fabric executor `moonshot.epoch.fabric_exec`, run exactly as Fabric's script executor runs
it (python -E -s -m <module> <args>, cwd = the pinned checkout, an allow-listed environment, FABRIC_OUT_DIR). No
database: these tests need nothing but this checkout."""
import ast
import base64
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from moonshot.epoch import canonical as C
from moonshot.epoch import model

REPO = Path(__file__).resolve().parents[3]
MODULE = "moonshot.epoch.fabric_exec"
APPROVED = "c0de" * 10
FILES = {"manifest": "MANIFEST.json", "spec": "SPEC.json", "trace": "TRACE", "checkpoint": "CHECKPOINT"}


def genesis(cid="Q1", epochs=3):
    return model.make_genesis(cid, epochs=epochs, params={"work_iterations": 60, "trace_every": 20,
                                                          "checkpoint_bytes": 64},
                              approved_code_sha=APPROVED, initial_checkpoint=b"fabric exec " + cid.encode())


def args_for(g, k, inp, namespace="qual", input_sha=None):
    return ["--namespace", namespace, "--genesis-b64", base64.b64encode(g.bytes).decode(), "--epoch-index", str(k),
            "--input-b64", base64.b64encode(inp).decode(), "--input-sha256", input_sha or C.sha256_hex(inp)]


class ExecCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="fx-")
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / "out"
        self.out.mkdir()
        self.faults = Path(self.tmp.name) / "faults"
        self.faults.mkdir()

    def run_exec(self, args, out=True):
        """As fabric.executors.run_script does: no shell, a minimal environment, cwd = the checkout."""
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8", "HOME": self.tmp.name,
               "MOONSHOT_FAULT_DIR": str(self.faults)}
        if out:
            env["FABRIC_OUT_DIR"] = str(self.out)
        if os.name == "nt":                       # Windows cannot start Python without these
            env.update({k: os.environ[k] for k in ("SYSTEMROOT", "TEMP", "TMP") if k in os.environ})
        return subprocess.run([sys.executable, "-E", "-s", "-m", MODULE] + args, cwd=str(REPO), env=env,
                              capture_output=True, timeout=120)

    def files(self):
        return {k: (self.out / name).read_bytes() for k, name in FILES.items() if (self.out / name).exists()}

    def fault(self, namespace, **spec):
        (self.faults / (namespace + ".json")).write_text(json.dumps([spec]), encoding="utf-8")


class TestExecutor(ExecCase):
    def test_one_epoch_lands_in_the_out_dir_byte_for_byte(self):
        g = genesis()
        r = self.run_exec(args_for(g, 1, g.initial_checkpoint))
        self.assertEqual(r.returncode, 0, r.stderr.decode()[-800:])
        self.assertEqual(self.files(), model.execute(g.obj, 1, g.initial_checkpoint).files())
        self.assertEqual(sorted(p.name for p in self.out.iterdir()), sorted(FILES.values()))

    def test_stdout_reports_the_identity_and_whether_a_fault_was_applied(self):
        g = genesis()
        r = self.run_exec(args_for(g, 2, b"some input"))
        line = json.loads(r.stdout.decode().strip().splitlines()[-1])
        ref = model.execute(g.obj, 2, b"some input")
        self.assertEqual((line["chain_id"], line["epoch_index"], line["work_id"], line["epoch_digest"], line["fault"]),
                         ("Q1", 2, ref.work_id, ref.epoch_digest, None))

    def test_an_input_that_does_not_match_its_hash_is_refused(self):
        g = genesis()
        r = self.run_exec(args_for(g, 1, g.initial_checkpoint, input_sha="0" * 64))
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.files(), {})

    def test_a_non_canonical_genesis_is_refused(self):
        g = genesis()
        a = args_for(g, 1, g.initial_checkpoint)
        a[a.index("--genesis-b64") + 1] = base64.b64encode(json.dumps(g.obj, indent=1).encode()).decode()
        self.assertEqual(self.run_exec(a).returncode, 2)
        self.assertEqual(self.files(), {})

    def test_an_epoch_outside_the_genesis_is_refused(self):
        g = genesis(epochs=3)
        self.assertEqual(self.run_exec(args_for(g, 4, g.initial_checkpoint)).returncode, 2)

    def test_without_an_out_dir_nothing_runs(self):
        g = genesis()
        self.assertEqual(self.run_exec(args_for(g, 1, g.initial_checkpoint), out=False).returncode, 2)

    def test_existing_output_is_never_overwritten(self):
        g = genesis()
        (self.out / "TRACE").write_bytes(b"already here")
        self.assertEqual(self.run_exec(args_for(g, 1, g.initial_checkpoint)).returncode, 2)
        self.assertEqual((self.out / "TRACE").read_bytes(), b"already here")
        self.assertEqual(sorted(p.name for p in self.out.iterdir()), ["TRACE"])     # no partial output


class TestNodeLocalFaults(ExecCase):
    """Faults model a faulty host. They are node-local files (no task submitter can set one) and are honoured only
    for TEST namespaces (test, test-*, qual, qual-*): a production namespace ignores them."""

    def test_flip_checkpoint_gives_a_self_consistent_wrong_answer(self):
        g = genesis()
        self.fault("qual", chain_id="Q1", epochs=[1], mode="flip_checkpoint")
        r = self.run_exec(args_for(g, 1, g.initial_checkpoint))
        self.assertEqual(r.returncode, 0, r.stderr.decode()[-800:])
        honest = model.execute(g.obj, 1, g.initial_checkpoint)
        files = self.files()
        self.assertEqual(model.verify_epoch(files), [])                  # internally consistent ...
        m = C.parse_canonical(files["manifest"])
        self.assertEqual(m["work_id"], honest.work_id)                     # ... same work ...
        self.assertNotEqual(m["epoch_digest"], honest.epoch_digest)        # ... different result
        self.assertEqual(json.loads(r.stdout.decode().strip().splitlines()[-1])["fault"], "flip_checkpoint")

    def test_corrupt_trace_breaks_the_manifest(self):
        g = genesis()
        self.fault("qual", chain_id="Q1", epochs=[1], mode="corrupt_trace")
        self.assertEqual(self.run_exec(args_for(g, 1, g.initial_checkpoint)).returncode, 0)
        self.assertIn("TRACE does not match the manifest", model.verify_epoch(self.files()))

    def test_a_fault_applies_only_to_its_chain_and_epochs(self):
        g = genesis()
        self.fault("qual", chain_id="Q1", epochs=[2], mode="flip_checkpoint")
        self.run_exec(args_for(g, 1, g.initial_checkpoint))
        self.assertEqual(self.files(), model.execute(g.obj, 1, g.initial_checkpoint).files())

    def test_production_namespaces_ignore_fault_files(self):
        g = genesis()
        self.fault("prod", chain_id="Q1", epochs=[1], mode="flip_checkpoint")
        r = self.run_exec(args_for(g, 1, g.initial_checkpoint, namespace="prod"))
        self.assertEqual(r.returncode, 0, r.stderr.decode()[-800:])
        self.assertEqual(self.files(), model.execute(g.obj, 1, g.initial_checkpoint).files())


class TestBoundary(unittest.TestCase):
    def test_the_executor_imports_no_database_network_or_git_code(self):
        """What the node runs touches only the stdlib and the pure epoch model: no psycopg2, sockets, subprocesses,
        HTTP or git -- its inputs arrive in argv and its outputs leave through FABRIC_OUT_DIR."""
        allowed = {"argparse", "base64", "binascii", "hashlib", "json", "os", "re", "sys", "time", "pathlib",
                   "moonshot.epoch", "moonshot.epoch.canonical", "moonshot.epoch.model", "moonshot.epoch.runtime",
                   # native epochs (C-012-T007): the runtime loads wforge, itself stdlib-only (scanned below)
                   "moonshot.epoch.native_wforge", "wforge", "wforge.genome", "wforge.world"}
        files = [(REPO / "moonshot" / "epoch" / (n + ".py"), "moonshot.epoch")
                 for n in ("fabric_exec", "model", "runtime", "canonical", "native_wforge")]
        files += [(REPO / "SerendipityFoundry" / "worldfoundry" / "wforge" / n, "wforge")
                  for n in ("__init__.py", "world.py", "genome.py")]
        seen = set()
        for path, package in files:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    seen.update(a.name for a in node.names)
                elif isinstance(node, ast.ImportFrom):
                    seen.add(package + ("." + node.module if node.module else "") if node.level else node.module)
        self.assertEqual(sorted(seen - allowed - {"dataclasses", "__future__"}), [])


if __name__ == "__main__":
    unittest.main()
