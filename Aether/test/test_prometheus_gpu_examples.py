"""Conformance: the example modules are EXECUTED, not trusted.

An example that does not satisfy the contract is worse than no example,
because a seat copies it and inherits the defect. `hello_gpu` shipped
emitting `utc` and `monotonic_s`, which the telemetry validator rejects,
and nothing caught it because nobody had ever run the example through the
validator. These tests run each module the way a pod would -- same
environment variables, same working directory -- and then validate what
it produced.

`param_sweep` is the honest check on generality. It was written from
another seat's point of view: it counts `evaluations`, has no relation to
Aether's physics, and imports nothing from `prometheus_gpu`. If a platform
change breaks it while `hello_gpu` still passes, the platform has grown a
dependency on its own first example.
"""

import json
import os
import subprocess
import sys

import pytest

RUNPOD = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
                                     "runpod"))
sys.path.insert(0, RUNPOD)

from prometheus_gpu import dryrun                      # noqa: E402
from prometheus_gpu import secrets as secrets_mod      # noqa: E402
from prometheus_gpu import spec as spec_mod            # noqa: E402
from prometheus_gpu import telemetry as tel_mod        # noqa: E402

EXAMPLES = {
    "hello_gpu": {"SWEEP": False, "env": {"HELLO_STEPS": "3"},
                  "result": "result.json", "banner": "HELLO_GPU_OK"},
    "param_sweep": {"SWEEP": True,
                    "env": {"SWEEP_CANDIDATES": "8", "SWEEP_GRID": "256"},
                    "result": "sweep.json", "banner": "PARAM_SWEEP_OK"},
}


def example_dir(name):
    return os.path.join(RUNPOD, "examples", name)


def run_example(name, tmp_path, extra_env=None):
    """Run the module as the pod would: declared env only, own workdir."""
    conf = EXAMPLES[name]
    out_dir = tmp_path / "out"
    out_dir.mkdir(parents=True)
    # Start from the real environment with the forbidden names REMOVED,
    # which is what the pod-side prelude leaves behind. Building it from
    # scratch is tempting but it broke the interpreter here: numpy lives in
    # a user site-packages directory that needs APPDATA, so a stripped
    # environment made every example fail with ModuleNotFoundError and told
    # us nothing about the examples.
    env = {k: v for k, v in os.environ.items()
           if k.upper() not in spec_mod.FORBIDDEN_ENV}
    env.update({"PROMETHEUS_RUN_ID": "conformance-%s" % name,
                "PROMETHEUS_ARTIFACT_DIR": str(out_dir),
                "PROMETHEUS_TELEMETRY_PATH": str(out_dir / "telemetry.jsonl"),
                "PROMETHEUS_MODULE": name})
    env.update(conf["env"])
    env.update(extra_env or {})
    proc = subprocess.run(
        [sys.executable, os.path.join(example_dir(name), "run.py")],
        cwd=str(tmp_path), env=env, capture_output=True, text=True,
        timeout=300)
    return proc, out_dir


@pytest.mark.parametrize("name", sorted(EXAMPLES))
def test_the_example_spec_is_valid_and_plans(name):
    spec = spec_mod.load(os.path.join(example_dir(name), "module_spec.json"))
    plan = dryrun.plan(spec, example_dir(name), inventory=None)
    assert plan["pod_created"] is False
    assert plan["bundle"]["bundle_sha256"]
    # An example that triggers its own dry-run warnings teaches the wrong
    # habits, so the two that matter must not fire.
    findings = " ".join(plan["findings"])
    assert "no artifacts declared" not in findings
    assert "no canary declared" not in findings


@pytest.mark.parametrize("name", sorted(EXAMPLES))
def test_the_example_runs_and_its_telemetry_validates(name, tmp_path):
    proc, out_dir = run_example(name, tmp_path)
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert EXAMPLES[name]["banner"] in proc.stdout

    tel_path = str(out_dir / "telemetry.jsonl")
    assert os.path.exists(tel_path), "the module emitted no telemetry"
    records, summary = tel_mod.validate_file(tel_path)
    assert summary["complete"] is True, "no `end` record"
    assert summary["module_status"] == "ok"
    assert summary["units_final"], "no `units` counter to divide cost by"
    kinds = summary["kinds"]
    assert kinds.get("start") == 1
    assert kinds.get("end") == 1

    # Both clocks on every record. This is the check that hello_gpu failed.
    for rec in records:
        assert "t_utc" in rec and "t_elapsed_s" in rec


@pytest.mark.parametrize("name", sorted(EXAMPLES))
def test_the_example_writes_every_artifact_it_declares(name, tmp_path):
    spec = spec_mod.load(os.path.join(example_dir(name), "module_spec.json"))
    _proc, out_dir = run_example(name, tmp_path)
    for declared in spec["artifacts"]:
        # Declared relative to the artifact dir, and nothing here may
        # rewrite that: the "out/" prefix this test used to strip is the
        # mismatch that cost Iteration 1 two flights.
        assert "/" not in declared, (
            "artifact %r is not relative to the artifact directory; the "
            "artifact server's document root IS that directory" % declared)
        assert (out_dir / declared).exists(), (
            "declared artifact %r was never written; the run would return "
            "nothing for it" % declared)
    with open(str(out_dir / EXAMPLES[name]["result"]), encoding="utf-8") as fh:
        assert json.load(fh)


@pytest.mark.parametrize("name", sorted(EXAMPLES))
def test_an_example_refuses_to_run_with_a_leaked_credential(name, tmp_path):
    """Deliberately inject a fake credential into the module's environment.

    The platform scrubs before the module starts, so in practice this
    cannot happen; the module checking anyway is defence in depth, and a
    module that carried on regardless would hide a platform defect.
    """
    proc, _out = run_example(name, tmp_path,
                             extra_env={"RUNPOD_API_KEY": "rpa_" + "F" * 24})
    assert proc.returncode == 92, (
        "the module continued with a provider credential in its environment")
    assert "SECRETS_BOUNDARY_VIOLATION" in proc.stderr
    assert "F" * 24 not in proc.stderr, "the module printed the credential"
    assert "F" * 24 not in proc.stdout


@pytest.mark.parametrize("name", sorted(EXAMPLES))
def test_the_bootstrap_scrubs_before_the_example_starts(name):
    spec = spec_mod.load(os.path.join(example_dir(name), "module_spec.json"))
    _plan, request, _meta, _built = dryrun.prepare(
        spec, example_dir(name), inventory=None)
    boot = request["cmd"][0]
    assert boot.index(secrets_mod.unset_prelude()) < boot.index(
        spec["entrypoint"]), "credentials are scrubbed after the module starts"
    secrets_mod.assert_no_credentials(request["env"])


def test_param_sweep_does_not_import_the_platform():
    """The generality check only means something if it is independent."""
    with open(os.path.join(example_dir("param_sweep"), "run.py"),
              encoding="utf-8") as fh:
        source = fh.read()
    imports = [line.strip() for line in source.splitlines()
               if line.strip().startswith(("import ", "from "))]
    assert not any("prometheus_gpu" in line for line in imports), imports
    assert not any("Aether" in line for line in imports), imports
    assert "import json" in imports and "import os" in imports


def test_param_sweep_is_reproducible_from_its_recorded_seed(tmp_path):
    """A sweep whose points come from an unrecorded random state cannot be
    re-run, which makes its results unusable later."""
    first, out1 = run_example("param_sweep", tmp_path / "a")
    second, out2 = run_example("param_sweep", tmp_path / "b")
    assert first.returncode == second.returncode == 0
    with open(str(out1 / "sweep.json"), encoding="utf-8") as fh:
        a = json.load(fh)
    with open(str(out2 / "sweep.json"), encoding="utf-8") as fh:
        b = json.load(fh)
    assert a["scores"] == b["scores"]
    assert a["seed"] == b["seed"]
