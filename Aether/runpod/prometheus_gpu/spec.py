"""The module contract: what a seat declares to run a GPU workload.

A seat should be able to read this file in a few minutes and learn
everything it needs. A module declares WHAT it is and WHAT it needs; it
declares nothing about RunPod, and it never sees the provider API.

    {
      "name": "my-module",
      "version": "1",
      "entrypoint": "run.py",
      "args": ["--ticks", "1000"],
      "dependencies": {"pip": ["numpy==2.2.0"]},
      "gpu": {"class": "NVIDIA A40", "min_memory_mib": 40000},
      "disk_gb": 20,
      "max_runtime_s": 1800,
      "artifacts": ["out/result.json"],
      "canary": "python3 -c \\"import numpy\\"",
      "env_allowlist": ["MY_MODULE_SEED"],
      "work_units": {"name": "site-ticks", "estimate": 1.0e9}
    }

Every field except `name` and `entrypoint` has a defensible default, so
the smallest useful spec is two lines. Validation is strict about the
things that cost money or lose data (runtime bounds, disk, artifacts,
the secrets boundary) and lenient about everything else.

DESIGN NOTE. `work_units` exists so the cost model can report dollars
per unit of USEFUL work in the module's own vocabulary -- site-ticks for
Aether, candidates or evaluations or simulation-steps for another seat.
The platform must not impose Aether's denominator on anyone.
"""

import json
import posixpath
import re

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,62}$")

# Names a module may never receive, whatever its allowlist says. These
# are the controller's credentials and they do not cross the boundary.
FORBIDDEN_ENV = (
    "RUNPOD_API_KEY", "RUNPOD_API_TOKEN", "RUNPOD_TOKEN",
    "AWS_SECRET_ACCESS_KEY", "AWS_ACCESS_KEY_ID", "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY", "GITHUB_TOKEN", "EW_DB_PASSWORD",
    "AGE_REAPER_SHARED_SECRET",
)

DEFAULTS = {
    "version": "1",
    "args": [],
    "dependencies": {"pip": []},
    "gpu": {"class": "NVIDIA A40", "count": 1, "cloud": "SECURE"},
    "disk_gb": 20,
    "max_runtime_s": 1800,
    "artifacts": [],
    "canary": None,
    "env_allowlist": [],
    "env": {},
    "telemetry": {"interval_s": 15},
    "work_units": None,
    "description": "",
}


class SpecError(ValueError):
    """A module spec that would cost money or lose data if launched."""


def _is_contained(path):
    """True if `path` is a relative POSIX path that stays inside its root.

    POSIX semantics DELIBERATELY, not the host's. The controller may run
    on Windows while the pod always runs Linux, and os.path.isabs is the
    host's answer: on Windows with Python 3.13, os.path.isabs("/etc/x")
    is False, because a rooted path with no drive letter is not absolute
    to ntpath. That path is absolutely absolute on the pod. Validating a
    pod-side path with host-side rules is how "/etc/passwd" passes review
    on a laptop and escapes the workdir in the cloud.

    Backslashes are refused outright: they are a legal filename character
    on Linux, so a Windows-style path would silently become one very
    strange file name rather than a directory.
    """
    if not path or not isinstance(path, str):
        return False
    if "\\" in path:
        return False
    if posixpath.isabs(path) or path.startswith("/"):
        return False
    parts = path.split("/")
    if any(part == ".." for part in parts):
        return False
    return not posixpath.isabs(posixpath.normpath("/root/" + path)[len("/root/"):])         and posixpath.normpath("/root/" + path).startswith("/root/")


def _require(cond, message):
    if not cond:
        raise SpecError(message)


class ModuleSpec(object):
    """A validated module declaration. Construct via `load` or `from_dict`."""

    def __init__(self, data, source=None):
        self.source = source
        self.raw = dict(data)
        merged = dict(DEFAULTS)
        merged.update({k: v for k, v in data.items() if v is not None})
        self.data = merged
        self.validate()

    # ------------------------------------------------------------ access
    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)

    @property
    def name(self):
        return self.data["name"]

    @property
    def version(self):
        return str(self.data["version"])

    @property
    def identity(self):
        return "%s@%s" % (self.name, self.version)

    # -------------------------------------------------------- validation
    def validate(self):
        d = self.data
        _require("name" in d, "spec needs a name")
        _require(NAME_RE.match(str(d["name"])),
                 "name %r must be lowercase alphanumeric with - or _, "
                 "because it becomes a pod name and an artifact path"
                 % (d["name"],))
        _require("entrypoint" in d and d["entrypoint"],
                 "spec needs an entrypoint, the file to run inside the module")
        _require(_is_contained(str(d["entrypoint"])),
                 "entrypoint %r must be a relative POSIX path inside the "
                 "module directory" % (d["entrypoint"],))

        _require(isinstance(d["args"], list), "args must be a list")
        _require(all(isinstance(a, str) for a in d["args"]),
                 "every arg must be a string; the platform does not "
                 "stringify numbers for you, because that hides typos")

        deps = d["dependencies"]
        _require(isinstance(deps, dict), "dependencies must be an object")
        pips = deps.get("pip", [])
        _require(isinstance(pips, list), "dependencies.pip must be a list")
        for p in pips:
            _require(isinstance(p, str) and p.strip(), "bad pip requirement")
            _require("==" in p or p.startswith("-") or "@" in p,
                     "pip requirement %r is unpinned; an unpinned dependency "
                     "means the bytes that ran cannot be reconstructed" % (p,))

        gpu = d["gpu"]
        _require(isinstance(gpu, dict), "gpu must be an object")
        _require(int(gpu.get("count", 1)) >= 1, "gpu.count must be >= 1")

        _require(int(d["disk_gb"]) >= 5, "disk_gb must be at least 5")
        _require(0 < int(d["max_runtime_s"]) <= 24 * 3600,
                 "max_runtime_s must be positive and at most 24 h; an "
                 "unbounded run is an unbounded bill")

        _require(isinstance(d["artifacts"], list), "artifacts must be a list")
        for a in d["artifacts"]:
            _require(_is_contained(a),
                     "artifact %r must be a relative POSIX path inside the "
                     "module workdir" % (a,))

        allow = d["env_allowlist"]
        _require(isinstance(allow, list), "env_allowlist must be a list")
        for name in allow:
            _require(name.upper() not in FORBIDDEN_ENV,
                     "env_allowlist may not contain %r: provider credentials "
                     "belong to the controller and never cross into module "
                     "code" % (name,))
        for name in d["env"]:
            _require(name.upper() not in FORBIDDEN_ENV,
                     "env may not set %r" % (name,))

        wu = d["work_units"]
        if wu is not None:
            _require(isinstance(wu, dict) and wu.get("name"),
                     "work_units needs a name, e.g. site-ticks or candidates")
            _require(float(wu.get("estimate", 0)) > 0,
                     "work_units.estimate must be positive; it is the "
                     "denominator for cost per unit of useful work")

        tel = d["telemetry"]
        _require(isinstance(tel, dict), "telemetry must be an object")
        _require(float(tel.get("interval_s", 15)) > 0,
                 "telemetry.interval_s must be positive")
        return True

    # ------------------------------------------------------------- output
    def to_dict(self):
        return dict(self.data)

    def canonical_json(self):
        """Stable bytes for hashing: sorted keys, no incidental whitespace."""
        return json.dumps(self.data, sort_keys=True,
                          separators=(",", ":")).encode("utf-8")


def from_dict(data, source=None):
    return ModuleSpec(data, source=source)


def load(path):
    """Load a module spec from JSON. YAML is accepted when PyYAML exists."""
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    if path.endswith((".yaml", ".yml")):
        try:
            import yaml
        except ImportError:
            raise SpecError(
                "%s is YAML but PyYAML is not installed; write the spec as "
                "JSON, which needs no dependency" % (path,))
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    _require(isinstance(data, dict), "a module spec must be an object")
    return ModuleSpec(data, source=path)
