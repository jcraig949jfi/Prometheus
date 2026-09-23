"""Image/source manifest generator (ASTRA_CLOSURE_REVIEW_02.md section 7/9).

The controller's plan.json only hashes the three science/harness sources it
reads directly (aeth01_cpu_oracle.py, aeth01_gpu_kernel.py, run_canary.py --
see age_controller.SOURCES). That is deliberately narrow: those are the
files the controller can verify without importing scientific code. It is
NOT sufficient coverage for "what actually runs on the pod" -- pod_service.py,
the receipt schema, and the Dockerfile/base-image identity also determine
pod behavior and are not covered by that hash set.

This script hashes every runtime-critical file this image ships and writes
a manifest an operator can compare against the actual built image's
contents (e.g. `docker run --rm IMAGE sha256sum /app/*.py`) before binding
approval to that image's digest. It does NOT build, inspect, or push an
image; run it after building and paste the real installed dependency
versions from `pip freeze` into the resulting manifest's
"installed_dependencies" field (left null here -- no image has been built
in this environment; see README.md "Status").

Usage: python image_manifest.py > image_manifest.json
"""

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RUNTIME_FILES = (
    "aeth01_cpu_oracle.py",
    "aeth01_gpu_kernel.py",
    "run_canary.py",
    "pod_service.py",
    "receipt_schema.json",
    "watchdog.sh",
    "Dockerfile",
)


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest():
    return {
        "version": 1,
        "base_image": "nvidia/cuda:12.4.1-runtime-ubuntu22.04",
        "pinned_dependencies": {"numpy": "2.2.0", "cupy-cuda12x": "13.3.0"},
        "pinned_dependencies_build_verified": False,
        "installed_dependencies": None,
        "file_hashes_sha256": {name: _sha256(HERE / name) for name in RUNTIME_FILES},
        "immutable_image_digest": None,
        "notes": (
            "file_hashes_sha256 covers worktree source bytes at manifest-generation "
            "time, not a built image's on-disk contents. installed_dependencies and "
            "immutable_image_digest MUST be filled in from an actual "
            "`docker build --platform linux/amd64` + `docker inspect` + `pip freeze` "
            "before this manifest is treated as binding R1 image identity evidence."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(build_manifest(), sort_keys=True, indent=2))
