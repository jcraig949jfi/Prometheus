r"""foundry_creds.py -- Apollo's credential + client boundary for the Serendipity Foundry.

This is the ONE stable piece of the adapter boundary: it survives Foundry API changes,
because loading a token and pinning a cert does not depend on which endpoints exist.

Security posture (Prometheus CLAUDE.md): the bearer token is NEVER read into a human's
view, NEVER logged, NEVER journaled, NEVER committed. It is loaded from the operator's
credential kit at RUNTIME and handed straight to the client. Callers must not print it.

Kit location (operator-provisioned, D-12/D-13 shared kit):
    C:\ZeusD-var\d11\remote\{token.txt, m1.crt}
Override with env APOLLO_FOUNDRY_KIT, or set FOUNDRY_ADMIN_TOKEN / FOUNDRY_M1_CERT
directly (env wins, so a scoped Apollo token can be swapped in without touching code).

World isolation (charter S5): the token is admin-scope and CAN touch other seats'
worlds. Isolation is Apollo's discipline, not the token's -- every experiment carries
CLIENT_ID and an apollo/ world namespace, and Apollo never mutates, deletes, or resets
another seat's worlds (D-12/D-13 on the ZeusE console; Harmonia A on genesis/harmonia_a).
"""
from __future__ import annotations

import os
import ssl
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # vendored canonical remote.py (sha256 bdd6f0771f5c)

from remote import FoundryClient  # noqa: E402

CLIENT_ID = "apollo"
BASE_URL = os.environ.get("FOUNDRY_BASE_URL", "https://192.168.1.202:8799")
_KIT = Path(os.environ.get("APOLLO_FOUNDRY_KIT", r"C:\ZeusD-var\d11\remote"))


def _token_path() -> Path:
    return _KIT / "token.txt"


def cert_path() -> str:
    return os.environ.get("FOUNDRY_M1_CERT") or str(_KIT / "m1.crt")


def _load_token() -> str:
    """Runtime-only. Env wins; else the kit file. Returned value is a secret --
    the caller hands it to FoundryClient and does not print or store it."""
    env = os.environ.get("FOUNDRY_ADMIN_TOKEN")
    if env:
        return env.strip()
    return _token_path().read_text(encoding="utf-8").strip()


def tls_context() -> ssl.SSLContext:
    """Pin the Foundry's self-signed cert. TLS is never blanket-disabled."""
    return ssl.create_default_context(cafile=cert_path())


def preflight() -> dict:
    """Cheap, secret-free readiness check for cron jobs. Reports what EXISTS,
    never a token value. {kit_present, token_present, cert_present, base_url}."""
    return {
        "base_url": BASE_URL,
        "client_id": CLIENT_ID,
        "kit": str(_KIT),
        "kit_present": _KIT.is_dir(),
        "token_present": bool(os.environ.get("FOUNDRY_ADMIN_TOKEN"))
                         or _token_path().is_file(),
        "cert_present": Path(cert_path()).is_file(),
    }


def make_client(expected_release_hash: str | None = None,
                timeout_s: float = 30.0) -> FoundryClient:
    """Construct a release-pinned Foundry client. Pass expected_release_hash to
    gate against a specific instrument identity; pass None to run unpinned (e.g. a
    version probe that needs to LEARN the current release). The token is loaded here
    and never leaves the client object."""
    return FoundryClient(
        BASE_URL,
        token=_load_token(),
        expected_release_hash=expected_release_hash,
        tls_context=tls_context(),
        timeout_s=timeout_s,
    )
