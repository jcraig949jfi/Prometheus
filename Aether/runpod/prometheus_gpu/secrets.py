"""The secrets boundary: provider credentials never reach module code.

The controller needs a RunPod API key. The module never does. The
boundary is enforced in three places, because one place is a single
point of failure:

1. the spec cannot ALLOWLIST a forbidden name (spec.validate);
2. the environment handed to the pod is built from an allowlist, so a
   credential cannot arrive by accident;
3. the bootstrap script UNSETS the forbidden names immediately before
   exec-ing module code, so a credential injected by the provider
   itself -- which RunPod does -- is gone before the module starts.

Point 3 is not hypothetical. RunPod injects RUNPOD_API_KEY into the pod
environment, and an earlier AETH-01 smoke test failed precisely because
pod-side code saw a provider-injected key it was not supposed to have.
That is why the unset is unconditional rather than conditional on what
the controller happened to set.
"""

import re

from .spec import FORBIDDEN_ENV

# Anything that looks like a credential, whatever it is called.
_SECRET_SHAPES = (
    re.compile(r"\brpa_[A-Za-z0-9]{16,}"),
    re.compile(r"\bsk-[A-Za-z0-9]{16,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{16,}"),
    re.compile(r"\bAKIA[0-9A-Z]{12,}"),
)


class SecretsViolation(RuntimeError):
    """Raised rather than logged. A leak must stop the run."""


def build_module_env(spec, run_meta):
    """The complete environment the module will see.

    Built additively from an allowlist. Nothing is inherited from the
    controller's environment, so a credential cannot arrive by being
    present where the controller happens to run.
    """
    env = {}
    for name in spec["env_allowlist"]:
        env[name] = ""
    env.update({k: str(v) for k, v in spec["env"].items()})
    env.update({
        "PROMETHEUS_RUN_ID": run_meta["run_id"],
        "PROMETHEUS_MODULE": spec.identity,
        "PROMETHEUS_SEAT": run_meta.get("seat", ""),
        "PROMETHEUS_WORKDIR": run_meta.get("workdir", "/app/module"),
        "PROMETHEUS_ARTIFACT_DIR": run_meta.get("artifact_dir", "/app/out"),
        "PROMETHEUS_TELEMETRY_PATH": run_meta.get("telemetry_path",
                                                  "/app/out/telemetry.jsonl"),
        # Per-run bearer token for the pod's artifact server. Generated
        # fresh for every launch, never reused, and not a provider
        # credential -- it authorises reading this one run's own output.
        # `scrub_request` drops its value from anything written down.
        "PROMETHEUS_ARTIFACT_TOKEN": run_meta.get("artifact_token", ""),
        "PROMETHEUS_ARTIFACT_PORT": str(run_meta.get("artifact_port", 8080)),
    })
    assert_no_credentials(env, where="module environment")
    return env


def assert_no_credentials(mapping, where="mapping"):
    """Refuse forbidden names and credential-shaped values."""
    for key, value in mapping.items():
        if key.upper() in FORBIDDEN_ENV:
            raise SecretsViolation(
                "%s contains forbidden key %r" % (where, key))
        for shape in _SECRET_SHAPES:
            if isinstance(value, str) and shape.search(value):
                raise SecretsViolation(
                    "%s value for %r looks like a credential" % (where, key))
    return True


def scrub_text(text):
    """Redact credential-shaped substrings before anything is recorded."""
    if not isinstance(text, str):
        return text
    for shape in _SECRET_SHAPES:
        text = shape.sub("[REDACTED]", text)
    return text


def scrub_request(body):
    """A pod request safe to commit as evidence.

    Environment VALUES are dropped and replaced by their key names: the
    evidence should prove which variables were set without recording
    what they were set to. Keys are kept because "which variables
    existed" is exactly what a later reader needs.
    """
    safe = {}
    for key, value in body.items():
        if key == "env" and isinstance(value, dict):
            safe["env_keys"] = sorted(value)
            safe["env_value_bytes"] = {k: len(str(v)) for k, v in value.items()}
        elif key == "cmd" and isinstance(value, list):
            safe["cmd"] = [scrub_text(c) for c in value]
        else:
            safe[key] = scrub_text(value) if isinstance(value, str) else value
    return safe


def unset_prelude():
    """Shell that removes provider credentials before module code runs.

    Unconditional: the provider injects some of these itself, so
    unsetting only what the controller set would leave exactly the ones
    that caused the original incident.
    """
    return "unset " + " ".join(FORBIDDEN_ENV)


def verification_snippet():
    """Shell that PROVES the boundary held, on the pod, at runtime.

    A check that runs where the module runs is worth more than a check
    that runs where the controller runs. Non-zero exit aborts before the
    module starts.
    """
    names = " ".join(FORBIDDEN_ENV)
    return (
        'for _v in %s; do\n'
        '  if [ -n "$(eval echo \\$$_v)" ]; then\n'
        '    echo "SECRETS_BOUNDARY_VIOLATION $_v still set" >&2\n'
        '    exit 92\n'
        '  fi\n'
        'done\n'
        'echo "SECRETS_BOUNDARY_OK"' % names)
