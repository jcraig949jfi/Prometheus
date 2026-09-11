"""The SFE conformance gate, WIRED at Archaeon's work boundaries (operator
2026-09-11: "priority infrastructure work, not backlog grooming").

Harmonia's four-state gate (roles/Harmonia/contracts/conformance_check.py)
is the authority; this module calls it rather than re-implementing it, and
makes it FAIL-CLOSED at the two places where Archaeon begins work:

  * archaeon.vivqueue.submit  -- every row Archaeon writes to the queue
  * archaeon.producer.tick    -- before the tick reads a single fossil

and stamps the result into the row's source_evidence and the tick receipt,
so conformance is PROVENANCE on the corpus, not an ephemeral preflight.

STATES AND CONSEQUENCES (Harmonia's ruling, RULING_CONFORMANCE_GATE_SPLIT):

  CONFORMANT        proceed
  INCOMPLETE        proceed ONLY if every route this consumer calls is in
                    the contract (declared below); otherwise halt
  DRIFT             halt
  wrong instance    halt (the ledger is not the one the contract describes)
  UNREACHABLE       retry `retries` times with `backoff_s`, then halt

TWO TIERS, because the full gate registers a client on the engine every
run and Archaeon crosses this boundary many times a day:

  tier 1 (every crossing, no side effects)  GET /v2/version; compare
      engine_source_hash, engine_instance_id, schema_version,
      science_profile, session_enforcement with the contract, and the
      contract file's own sha256 with the cached one.
  tier 2 (Harmonia's full gate: route diff + scoping probe)  runs when the
      identity tuple or the contract hash differs from the last full result,
      or the last full result is older than `full_gate_max_age_h`.

A tier-1 mismatch on instance / profile / enforcement halts at once. A
tier-1 change in source hash or schema is not classified here: it forces
tier 2, which says INCOMPLETE or DRIFT.

IN PRODUCTION THE GATE CANNOT BE SWITCHED OFF: when the queue schema is
`viv`, `enabled` and the test-only environment override are ignored.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import ssl
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
CONFORMANT, DRIFT, UNREACHABLE, INCOMPLETE = "CONFORMANT", "DRIFT", "UNREACHABLE", "INCOMPLETE"
STATES_HALT = ("DRIFT", "UNREACHABLE", "WRONG_INSTANCE", "INCOMPLETE_HALT", "PROFILE_MISMATCH")
EXIT_TO_STATE = {0: CONFORMANT, 1: DRIFT, 2: UNREACHABLE, 3: INCOMPLETE}
PRODUCTION_SCHEMA = "viv"


class ConformanceHalt(RuntimeError):
    def __init__(self, record: Dict[str, Any]):
        super().__init__("conformance gate HALT: {} -- {}".format(record.get("state"), record.get("reason")))
        self.record = record


@dataclass(frozen=True)
class ConformanceConfig:
    enabled: bool = True
    contract_path: str = "roles/Harmonia/contracts/sfe_contract.json"
    gate_script: str = "roles/Harmonia/contracts/conformance_check.py"
    cacert: str = "SerendipityFoundry/SerendipityFoundryEngine/deploy/m1.crt"
    base_url: Optional[str] = None                  # None -> the contract's engine.base_url
    #: every HTTP route this consumer calls today. Archaeon reads the ledger
    #: FILE under declared tenancy (archaeon.fossils, guarded by
    #: expected_schema_version) and writes Vivarium's queue; its only engine
    #: route is the identity call. The B1 read routes join this list when
    #: the grant lands.
    consumer_routes: Tuple[str, ...] = ("GET /v2/version",)
    retries: int = 3
    backoff_s: float = 5.0
    timeout_s: float = 10.0
    full_gate_max_age_h: float = 24.0
    cache_path: str = "archaeon/state/conformance_cache.json"


def _abs(p: str) -> Path:
    q = Path(p)
    return q if q.is_absolute() else REPO / q


def contract_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _ssl_ctx(cacert: Optional[Path]):
    ctx = ssl.create_default_context()
    if cacert and cacert.exists():
        ctx.load_verify_locations(str(cacert))
    return ctx


def identity(base: str, cacert: Optional[Path], timeout_s: float) -> Dict[str, Any]:
    root = base[:-3] if base.endswith("/v2") else base
    url = root.rstrip("/") + "/v2/version"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout_s, context=_ssl_ctx(cacert) if url.startswith("https") else None) as r:
        return json.loads(r.read().decode("utf-8"))


def _identity_with_retries(cfg: ConformanceConfig, base: str, cacert: Optional[Path]) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    attempts = []
    for i in range(cfg.retries + 1):
        t0 = time.time()
        try:
            live = identity(base, cacert, cfg.timeout_s)
            attempts.append({"attempt": i + 1, "ok": True, "elapsed_s": round(time.time() - t0, 3)})
            return live, attempts
        except Exception as exc:                                     # noqa: BLE001
            attempts.append({"attempt": i + 1, "ok": False, "error": "{}: {}".format(type(exc).__name__, str(exc)[:160]),
                             "elapsed_s": round(time.time() - t0, 3)})
            if i < cfg.retries:
                time.sleep(cfg.backoff_s)
    return None, attempts


def _load_cache(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:                                                # noqa: BLE001
        return {}


def _save_cache(path: Path, cache: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, indent=1, sort_keys=True), encoding="utf-8")


def full_gate(cfg: ConformanceConfig, contract: Path, base: str, cacert: Optional[Path]) -> Dict[str, Any]:
    """Harmonia's gate, as a subprocess, with this consumer's routes declared."""
    cmd = [sys.executable, str(_abs(cfg.gate_script)), "--contract", str(contract), "--base", base]
    if cacert and cacert.exists():
        cmd += ["--cacert", str(cacert)]
    cmd += ["--consumer-routes", *cfg.consumer_routes]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    tail = "\n".join((p.stdout or "").strip().splitlines()[-6:])
    return {"exit": p.returncode, "state": EXIT_TO_STATE.get(p.returncode, "UNKNOWN_EXIT_{}".format(p.returncode)),
            "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "elapsed_s": round(time.time() - t0, 2), "stdout_tail": tail, "stderr_tail": (p.stderr or "")[-400:]}


def _production() -> bool:
    try:
        from . import vivqueue
        return vivqueue._schema() == PRODUCTION_SCHEMA
    except Exception:                                                # noqa: BLE001
        return True                     # cannot tell -> treat as production (fail closed)


def evaluate(cfg: ConformanceConfig, *, now: Optional[datetime.datetime] = None) -> Dict[str, Any]:
    """Run the gate at a boundary and return the provenance record. Never
    raises on a halt; `require` does."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    prod = _production()
    if not prod and (not cfg.enabled or os.environ.get("ARCHAEON_CONFORMANCE_MODE") == "off"):
        return {"state": "DISABLED_TEST_SCHEMA", "halted": False,
                "reason": "gate disabled by config/env; honoured only outside the production schema", "production": False}
    contract_p = _abs(cfg.contract_path)
    C = json.loads(contract_p.read_text(encoding="utf-8"))
    c_hash = contract_hash(contract_p)
    base = (cfg.base_url or C["engine"]["base_url"]).rstrip("/")
    cacert = _abs(cfg.cacert) if cfg.cacert else None
    rec: Dict[str, Any] = {"schema": "archaeon.conformance.v1", "at": now.isoformat(timespec="seconds"),
                           "production": prod, "base_url": base, "consumer_routes": list(cfg.consumer_routes),
                           "contract": {"path": str(Path(cfg.contract_path)), "hash": c_hash,
                                        "engine_source_hash": C["engine"]["engine_source_hash"],
                                        "engine_instance_id": C["engine"]["engine_instance_id"],
                                        "schema_version": C["engine"]["schema_version"]}}
    live, attempts = _identity_with_retries(cfg, base, cacert)
    rec["attempts"] = attempts
    if live is None:
        rec.update(state="UNREACHABLE", halted=True,
                   reason="/v2/version unreachable after {} attempts ({} s backoff)".format(len(attempts), cfg.backoff_s))
        return rec
    rec["live"] = {k: live.get(k) for k in ("engine_source_hash", "engine_instance_id", "schema_version", "science_profile", "session_enforcement")}
    # tier 1: identity
    if live.get("engine_instance_id") != C["engine"]["engine_instance_id"]:
        rec.update(state="WRONG_INSTANCE", halted=True,
                   reason="live engine_instance_id {} is not the contract's {}".format(live.get("engine_instance_id"), C["engine"]["engine_instance_id"]))
        return rec
    for f in ("science_profile", "session_enforcement"):
        if live.get(f) != C["engine"].get(f):
            rec.update(state="PROFILE_MISMATCH", halted=True, reason="{} live {} vs contract {}".format(f, live.get(f), C["engine"].get(f)))
            return rec
    key = "|".join(str(x) for x in (live.get("engine_source_hash"), live.get("engine_instance_id"), live.get("schema_version"), c_hash, ",".join(cfg.consumer_routes)))
    cache_p = _abs(cfg.cache_path)
    cache = _load_cache(cache_p)
    hit = cache.get(key)
    fresh = False
    if hit:
        try:
            age_h = (now - datetime.datetime.fromisoformat(hit["at"])).total_seconds() / 3600.0
            fresh = age_h <= cfg.full_gate_max_age_h
        except Exception:                                            # noqa: BLE001
            fresh = False
    if hit and fresh and hit.get("state") in (CONFORMANT, INCOMPLETE):
        gate = dict(hit, mode="cached")
    else:
        gate = full_gate(cfg, contract_p, base, cacert)
        gate["mode"] = "full"
        cache[key] = {k: gate[k] for k in ("exit", "state", "at", "elapsed_s", "stdout_tail")}
        _save_cache(cache_p, cache)
    rec["gate"] = gate
    st = gate["state"]
    if st == CONFORMANT:
        # Harmonia's script returns 0 for INCOMPLETE-with-routes-covered too; keep her word for it
        covered = "Every route you declared IS in the contract" in gate.get("stdout_tail", "")
        rec.update(state=("INCOMPLETE_PROCEED" if covered else CONFORMANT), halted=False,
                   reason=("build moved by addition only; every declared route is in the contract" if covered else "build hash matches the contract"))
    elif st == INCOMPLETE:
        rec.update(state="INCOMPLETE_HALT", halted=True, reason="build moved by addition and a route this consumer calls is not in the contract (or none were declared)")
    elif st == DRIFT:
        rec.update(state=DRIFT, halted=True, reason="something the contract describes has moved or the ledger changed")
    elif st == UNREACHABLE:
        rec.update(state=UNREACHABLE, halted=True, reason="the full gate could not reach the engine")
    else:
        rec.update(state=st, halted=True, reason="unknown gate exit {}".format(gate.get("exit")))
    return rec


def compact(rec: Dict[str, Any]) -> Dict[str, Any]:
    """What travels on a row's source_evidence: identities and the verdict."""
    return {"schema": rec.get("schema", "archaeon.conformance.v1"), "state": rec.get("state"), "halted": rec.get("halted"),
            "at": rec.get("at"), "live": rec.get("live"), "contract": rec.get("contract"),
            "gate_mode": (rec.get("gate") or {}).get("mode"), "gate_exit": (rec.get("gate") or {}).get("exit"),
            "gate_at": (rec.get("gate") or {}).get("at"), "consumer_routes": rec.get("consumer_routes")}


def require(cfg: Optional[ConformanceConfig] = None) -> Dict[str, Any]:
    """The boundary call. Returns the record, or raises ConformanceHalt."""
    cfg = cfg or ConformanceConfig()
    rec = evaluate(cfg)
    if rec.get("halted"):
        raise ConformanceHalt(rec)
    return rec
