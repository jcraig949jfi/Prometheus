"""Write holdout D's sealed spec ONCE (pattern: prometheus/cosmos/holdout/seal.py).

  COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D.seal

The nonce comes from the OS CSPRNG (secrets), so the hidden world list is independent of every seed the
author ever used. The spec records the worlds, the nonce, the sha256 of every source file of the family
(LF-normalised bytes, so a CRLF checkout hashes the same), and the Python / numpy versions. The seal
commitment is the sha256 of the sealed spec file's bytes as written (LF line endings).
"""
from __future__ import annotations

import hashlib
import json
import platform
import secrets
import sys
from pathlib import Path

import numpy as np

from prometheus.cosmos.c3_holdout_D import medium

HERE = Path(__file__).resolve().parent
SPEC = HERE / "sealed_spec_D.json"
N_WORLDS = 128
SOURCES = ("__init__.py", "medium.py", "seal.py")


def src_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canon_sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> str:
    if SPEC.exists():
        raise SystemExit("sealed spec already exists; sealing is once-only (sha %s)"
                         % hashlib.sha256(SPEC.read_bytes()).hexdigest())
    nonce = secrets.token_hex(32)
    rng = np.random.default_rng(int(nonce, 16) % (2 ** 128))
    worlds = [w.as_dict() for w in medium.draw_worlds(N_WORLDS, rng)]
    run_seeds = [int(x) for x in rng.integers(0, 2 ** 31 - 1, N_WORLDS)]
    spec = {
        "family": medium.FAMILY_NAME, "family_version": medium.FAMILY_VERSION,
        "author": "Nestor (delegate), machine M1 SKULLPORT",
        "family_src_sha256": src_sha(HERE / "medium.py"),
        "src_sha256": {f: src_sha(HERE / f) for f in SOURCES},
        "src_sha_convention": "sha256 of file bytes with CRLF normalised to LF",
        "nonce": nonce, "nonce_source": "secrets.token_hex(32) (OS CSPRNG); world rng = "
                 "numpy default_rng(int(nonce,16) mod 2^128)",
        "n_worlds": N_WORLDS, "worlds": worlds, "run_seeds": run_seeds,
        "python": sys.version, "numpy": np.__version__, "platform": platform.platform(),
        "lattice": {k: list(v) for k, v in medium.LATTICE.items()},
    }
    spec["spec_id"] = canon_sha(spec)
    SPEC.write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    commit = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    print("sealed", SPEC, "commitment sha256", commit)
    return commit


if __name__ == "__main__":
    main()
