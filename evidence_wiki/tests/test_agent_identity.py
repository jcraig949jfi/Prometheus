"""Per-agent scoped tokens in identity() (KAIROS-02, 2026-09-11).

In-process: identity() is called with a stub request, so no service, no
database and no real token is involved. The committed registry holds only a
sha256; the test mints its own throwaway token and registers its hash.

Controls:
    positive   the agent token reads (scopes read) and is attributed to the
               agent name the registry binds, whatever the header claims
    cheat      the same token asking to WRITE is refused 403 (a read-only
               identity cannot submit by accident)
    negative   a token whose hash is not registered is 401, exactly as before
    binding    a mismatching X-Prometheus-Agent header is 401, so an agent
               token cannot be borrowed under another name
    unchanged  machine tokens and the legacy token keep read+write
"""
import hashlib
import secrets
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ew import service  # noqa: E402


class _Req:
    def __init__(self, **headers):
        self.headers = {k.lower().replace("_", "-"): v for k, v in headers.items()}


@pytest.fixture
def agent_token(monkeypatch):
    tok = secrets.token_urlsafe(24)
    reg = {"TestReader": {"scopes": ["read"],
                          "token_sha256": hashlib.sha256(tok.encode()).hexdigest()}}
    monkeypatch.setitem(service.CFG, "agent_identities", reg)
    return tok


def test_positive_agent_token_reads_and_binds_name(agent_token):
    ident = service.identity(_Req(authorization=f"Bearer {agent_token}",
                                  x_prometheus_machine="M1"))
    assert ident["auth"] == "agent_token"
    assert ident["agent"] == "TestReader"
    assert ident["scopes"] == ["read"]
    assert ident["machine"] == "M1"


def test_cheat_read_only_token_cannot_write(agent_token):
    with pytest.raises(HTTPException) as e:
        service.identity(_Req(authorization=f"Bearer {agent_token}",
                              x_prometheus_machine="M1",
                              x_prometheus_agent="TestReader"), write=True)
    assert e.value.status_code == 403
    assert "read" in str(e.value.detail)


def test_negative_unregistered_token_is_401(agent_token):
    with pytest.raises(HTTPException) as e:
        service.identity(_Req(authorization="Bearer " + secrets.token_urlsafe(24)))
    assert e.value.status_code == 401


def test_binding_wrong_agent_header_is_401(agent_token):
    with pytest.raises(HTTPException) as e:
        service.identity(_Req(authorization=f"Bearer {agent_token}",
                              x_prometheus_agent="SomeoneElse"))
    assert e.value.status_code == 401


def test_unchanged_machine_and_legacy_tokens_keep_write(agent_token):
    m1 = service.CFG["machine_tokens"]["M1"]
    ident = service.identity(_Req(authorization=f"Bearer {m1}",
                                  x_prometheus_agent="x"), write=True)
    assert ident["auth"] == "machine_token" and "write" in ident["scopes"]
    ident = service.identity(_Req(authorization=f"Bearer {service.CFG['auth_token']}",
                                  x_prometheus_machine="M1",
                                  x_prometheus_agent="x"), write=True)
    assert ident["auth"] == "legacy_shared" and "write" in ident["scopes"]


def test_committed_registry_holds_no_token_value():
    """The real config: every agent identity carries a 64-hex sha256 and no
    field that looks like a token value."""
    import json
    cfg = json.loads((Path(service.__file__).resolve().parent.parent / "config.json")
                     .read_text(encoding="utf-8"))
    for name, spec in (cfg.get("agent_identities") or {}).items():
        assert len(spec["token_sha256"]) == 64 and int(spec["token_sha256"], 16)
        assert "token" not in {k for k in spec if k != "token_sha256"}, name
        assert spec["scopes"], name
