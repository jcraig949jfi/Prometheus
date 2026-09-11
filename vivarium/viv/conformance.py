"""The SFE conformance gate, wired fail-closed before this consumer claims.

Harmonia's four-state gate (roles/Harmonia/contracts/conformance_check.py) is
the AUTHORITY. This module calls it and never re-implements it.

WHERE THE GATE SITS, AND WHY IT IS NOT AT DISPATCH. The obvious reading of
"the boundary where the consumer begins work" is the dispatch call, and that
reading is wrong here. A halt at dispatch happens with a row already CLAIMED,
and this seat's charter (invariant 6) says a stranded row is left visibly
stranded and never resolved by inference. So a DRIFT that halted at dispatch
would strand one row per tick, and the operator would come back to a queue
full of rows that require a human release each -- a gate whose safe state
creates work for a person is a gate that gets unwired.

The gate therefore runs BEFORE `claim`, which is strictly earlier than
hydrate and satisfies the requirement with room to spare. On a halt NOTHING
is claimed, the tick reports BLOCKED carrying the record, and the queue is
exactly as it was. Fail-closed with no residue.

WHY NOT `import archaeon.conformance`. Archaeon offered it and the tier
design below is theirs. Three things in it are theirs and not mine: its
production test asks `archaeon.vivqueue` what the schema is, its cache lives
under `archaeon/state/`, and its declared route set is the single identity
call. Wiring my consumer's fail-closed path through another seat's module
would also mean their refactor can stop my loop. The subprocess call to
Harmonia's script is the part that matters and it is identical in both.
Record field names are deliberately kept the same as theirs so the two
reconcile without a translation table.

TWO TIERS, for the reason Archaeon found: the full gate registers a probe
client on the engine every run, and this loop ticks every five seconds.

  tier 1  GET /v2/version, no side effects. Identity: instance, source hash,
          schema, science_profile, session_enforcement, and the contract
          file's own hash.
  tier 2  Harmonia's full script (route diff + session-scoping probe), run
          when the identity tuple or contract hash moved since the last full
          result, or that result is older than `full_gate_max_age_h`.

AND ONLY WHEN THERE IS WORK. An idle tick is not a crossing. Gating every
tick would put twelve identity calls a minute on the engine to authorise
nothing, and would make the engine's availability a precondition for
discovering that the queue is empty. So the gate runs when a row is actually
waiting; rows here run 160-620 s, so that is roughly one identity call per
row and not one per poll.

IN PRODUCTION THE GATE CANNOT BE SWITCHED OFF: when the schema is `viv`,
`enabled` and the environment override are ignored.
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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import db as _db

REPO = Path(__file__).resolve().parents[2]

CONFORMANT = "CONFORMANT"
DRIFT = "DRIFT"
UNREACHABLE = "UNREACHABLE"
INCOMPLETE = "INCOMPLETE"

#: Harmonia's exit codes. Do NOT pipe her script and read $? -- that captures
#: the pipe's status, a defect her docstring records as having bitten this
#: campaign twice. subprocess.run gives the process's own code.
EXIT_TO_STATE = {0: CONFORMANT, 1: DRIFT, 2: UNREACHABLE, 3: INCOMPLETE}

#: Every state in which this consumer must not begin work.
STATES_HALT = ("DRIFT", "UNREACHABLE", "WRONG_INSTANCE", "INCOMPLETE_HALT",
               "PROFILE_MISMATCH")

PRODUCTION_SCHEMA = "viv"

#: EVERY HTTP route this consumer calls, in the CONTRACT'S OWN SPELLING.
#:
#: The spelling matters and is not cosmetic: the gate compares declared
#: routes to contract routes as exact "VERB /path" strings, and the client
#: names two placeholders differently from the contract
#: ({artifact_id} vs {aid}, {reservation_id} vs {rid}). Declared with the
#: client's spelling, all 24 would read as absent from the contract and every
#: INCOMPLETE would halt for a reason that does not exist.
#:
#: Derived from the client source rather than memory, and
#: tests/test_conformance.py asserts both directions: every route here is in
#: the contract, and every sfclient method viv calls is represented here. A
#: route called and not declared is a halt the gate cannot see; a route
#: declared and not called is a false claim about my own surface.
CONSUMER_ROUTES: Tuple[str, ...] = (
    "GET /v2/version",
    "GET /v2/worlds/{wid}/artifacts/{aid}/content",
    "GET /v2/worlds/{wid}/events",
    "GET /v2/worlds/{wid}/experiments/{eid}/audit-envelope",
    "GET /v2/worlds/{wid}/status",
    "POST /v2/budget/reservations/{rid}/release",
    "POST /v2/clients",
    "POST /v2/families",
    "POST /v2/families/{fid}/members",
    "POST /v2/sessions",
    "POST /v2/work/claim",
    "POST /v2/work/{work_id}/complete",
    "POST /v2/work/{work_id}/fail",
    "POST /v2/work/{work_id}/heartbeat",
    "POST /v2/worlds",
    "POST /v2/worlds/{wid}/budget/consume",
    "POST /v2/worlds/{wid}/budget/reserve",
    "POST /v2/worlds/{wid}/cost-events",
    "POST /v2/worlds/{wid}/experiments",
    "POST /v2/worlds/{wid}/hypotheses",
    "POST /v2/worlds/{wid}/import",
    "POST /v2/worlds/{wid}/observations",
    "POST /v2/worlds/{wid}/predictions",
    "POST /v2/worlds/{wid}/start",
)


class ConformanceHalt(RuntimeError):
    def __init__(self, record: Dict[str, Any]):
        super().__init__("conformance gate HALT: %s -- %s"
                         % (record.get("state"), record.get("reason")))
        self.record = record


@dataclass(frozen=True)
class Config:
    enabled: bool = True
    contract_path: str = "roles/Harmonia/contracts/sfe_contract.json"
    gate_script: str = "roles/Harmonia/contracts/conformance_check.py"
    cacert: Optional[str] = None          # None -> viv's configured cacert
    base_url: Optional[str] = None        # None -> the contract's base_url
    consumer_routes: Tuple[str, ...] = CONSUMER_ROUTES
    retries: int = 3
    backoff_s: float = 5.0
    timeout_s: float = 10.0
    full_gate_max_age_h: float = 24.0
    cache_path: str = "vivarium/var/conformance_cache.json"


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
    """Tier 1. GET /v2/version -- no side effects, so it is safe per crossing."""
    root = base[:-3] if base.endswith("/v2") else base
    url = root.rstrip("/") + "/v2/version"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    ctx = _ssl_ctx(cacert) if url.startswith("https") else None
    with urllib.request.urlopen(req, timeout=timeout_s, context=ctx) as r:
        return json.loads(r.read().decode("utf-8"))


def _identity_with_retries(cfg: Config, base: str, cacert: Optional[Path]):
    """UNREACHABLE is an inability to LOOK, not evidence of drift, so it is
    retried before it becomes a stop -- Harmonia's wording, and the reason
    this is a separate state rather than folded into DRIFT."""
    attempts: List[Dict[str, Any]] = []
    for i in range(cfg.retries + 1):
        t0 = time.time()
        try:
            live = identity(base, cacert, cfg.timeout_s)
            attempts.append({"attempt": i + 1, "ok": True,
                             "elapsed_s": round(time.time() - t0, 3)})
            return live, attempts
        except Exception as exc:                                 # noqa: BLE001
            attempts.append({"attempt": i + 1, "ok": False,
                             "error": "%s: %s" % (type(exc).__name__,
                                                  str(exc)[:160]),
                             "elapsed_s": round(time.time() - t0, 3)})
            if i < cfg.retries:
                time.sleep(cfg.backoff_s)
    return None, attempts


def _load_cache(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:                                            # noqa: BLE001
        return {}


def _save_cache(path: Path, cache: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, indent=1, sort_keys=True),
                    encoding="utf-8")


def full_gate(cfg: Config, contract: Path, base: str,
              cacert: Optional[Path]) -> Dict[str, Any]:
    """Tier 2: Harmonia's script as a subprocess, routes declared."""
    cmd = [sys.executable, str(_abs(cfg.gate_script)),
           "--contract", str(contract), "--base", base]
    if cacert and cacert.exists():
        cmd += ["--cacert", str(cacert)]
    cmd += ["--consumer-routes", *cfg.consumer_routes]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    tail = "\n".join((p.stdout or "").strip().splitlines()[-6:])
    return {"exit": p.returncode,
            "state": EXIT_TO_STATE.get(p.returncode,
                                       "UNKNOWN_EXIT_%s" % p.returncode),
            "at": datetime.datetime.now(datetime.timezone.utc)
                  .isoformat(timespec="seconds"),
            "elapsed_s": round(time.time() - t0, 2),
            "stdout_tail": tail, "stderr_tail": (p.stderr or "")[-400:]}


def _production(schema: Optional[str] = None) -> bool:
    """Production is decided by MY schema, not another seat's notion of it."""
    try:
        return (schema or _db.schema()) == PRODUCTION_SCHEMA
    except Exception:                                            # noqa: BLE001
        return True                      # cannot tell -> production, closed


def _cacert(cfg: Config) -> Optional[Path]:
    if cfg.cacert:
        return _abs(cfg.cacert)
    try:
        c = _db.load_config().get("sfe_cacert")
    except Exception:                                            # noqa: BLE001
        return None
    return _abs(c) if c else None


def evaluate(cfg: Optional[Config] = None, *, schema: Optional[str] = None,
             now: Optional[datetime.datetime] = None) -> Dict[str, Any]:
    """Run the gate and return the provenance record. Never raises on a halt;
    `require` does."""
    cfg = cfg or Config()
    now = now or datetime.datetime.now(datetime.timezone.utc)
    prod = _production(schema)
    if not prod and (not cfg.enabled
                     or os.environ.get("VIV_CONFORMANCE_MODE") == "off"):
        return {"schema": "vivarium.conformance.v1", "state": "DISABLED_TEST_SCHEMA",
                "halted": False, "production": False,
                "reason": "gate disabled by config/env; honoured only outside "
                          "the production schema"}

    contract_p = _abs(cfg.contract_path)
    C = json.loads(contract_p.read_text(encoding="utf-8"))
    c_hash = contract_hash(contract_p)
    base = (cfg.base_url or C["engine"]["base_url"]).rstrip("/")
    cacert = _cacert(cfg)

    rec: Dict[str, Any] = {
        "schema": "vivarium.conformance.v1",
        "at": now.isoformat(timespec="seconds"),
        "production": prod, "base_url": base,
        "consumer_routes": list(cfg.consumer_routes),
        "contract": {"path": str(Path(cfg.contract_path)), "hash": c_hash,
                     "engine_source_hash": C["engine"]["engine_source_hash"],
                     "engine_instance_id": C["engine"]["engine_instance_id"],
                     "schema_version": C["engine"]["schema_version"]},
    }

    live, attempts = _identity_with_retries(cfg, base, cacert)
    rec["attempts"] = attempts
    if live is None:
        rec.update(state=UNREACHABLE, halted=True,
                   reason="/v2/version unreachable after %d attempts "
                          "(%s s backoff)" % (len(attempts), cfg.backoff_s))
        return rec
    rec["live"] = {k: live.get(k) for k in
                   ("engine_source_hash", "engine_instance_id",
                    "schema_version", "science_profile",
                    "session_enforcement")}

    # THE INSTANCE NEVER BENDS. It names the LEDGER, not the build, and its
    # mismatch is the one failure that corrupts attribution silently instead
    # of halting work.
    if live.get("engine_instance_id") != C["engine"]["engine_instance_id"]:
        rec.update(state="WRONG_INSTANCE", halted=True,
                   reason="live engine_instance_id %s is not the contract's %s"
                          % (live.get("engine_instance_id"),
                             C["engine"]["engine_instance_id"]))
        return rec
    for f in ("science_profile", "session_enforcement"):
        if live.get(f) != C["engine"].get(f):
            rec.update(state="PROFILE_MISMATCH", halted=True,
                       reason="%s live %s vs contract %s"
                              % (f, live.get(f), C["engine"].get(f)))
            return rec

    key = "|".join(str(x) for x in (
        live.get("engine_source_hash"), live.get("engine_instance_id"),
        live.get("schema_version"), c_hash, ",".join(cfg.consumer_routes)))
    cache_p = _abs(cfg.cache_path)
    cache = _load_cache(cache_p)
    hit = cache.get(key)
    fresh = False
    if hit:
        try:
            age_h = (now - datetime.datetime.fromisoformat(hit["at"])
                     ).total_seconds() / 3600.0
            fresh = age_h <= cfg.full_gate_max_age_h
        except Exception:                                        # noqa: BLE001
            fresh = False
    if hit and fresh and hit.get("state") in (CONFORMANT, INCOMPLETE):
        gate = dict(hit, mode="cached")
    else:
        gate = full_gate(cfg, contract_p, base, cacert)
        gate["mode"] = "full"
        cache[key] = {k: gate[k] for k in
                      ("exit", "state", "at", "elapsed_s", "stdout_tail")}
        _save_cache(cache_p, cache)
    rec["gate"] = gate

    st = gate["state"]
    if st == CONFORMANT:
        # Harmonia's script exits 0 for INCOMPLETE-with-routes-covered as
        # well as for a clean match, so the two are separated by her own
        # words rather than by re-deriving the judgement here.
        covered = ("Every route you declared IS in the contract"
                   in gate.get("stdout_tail", ""))
        rec.update(state=("INCOMPLETE_PROCEED" if covered else CONFORMANT),
                   halted=False,
                   reason=("build moved by addition only; every declared "
                           "route is in the contract" if covered
                           else "build hash matches the contract"))
    elif st == INCOMPLETE:
        rec.update(state="INCOMPLETE_HALT", halted=True,
                   reason="build moved by addition and a route this consumer "
                          "calls is not in the contract (or none declared)")
    elif st == DRIFT:
        rec.update(state=DRIFT, halted=True,
                   reason="something the contract describes has moved, or the "
                          "ledger changed")
    elif st == UNREACHABLE:
        rec.update(state=UNREACHABLE, halted=True,
                   reason="the full gate could not reach the engine")
    else:
        rec.update(state=st, halted=True,
                   reason="unknown gate exit %s" % gate.get("exit"))
    return rec


def compact(rec: Dict[str, Any]) -> Dict[str, Any]:
    """What travels on the row: identities and the verdict, not the transcript.

    Field names match archaeon.conformance.compact() so a producer row and an
    executor row join without a translation table.
    """
    return {"schema": rec.get("schema", "vivarium.conformance.v1"),
            "state": rec.get("state"), "halted": rec.get("halted"),
            "at": rec.get("at"), "live": rec.get("live"),
            "contract": rec.get("contract"),
            "gate_mode": (rec.get("gate") or {}).get("mode"),
            "gate_exit": (rec.get("gate") or {}).get("exit"),
            "gate_at": (rec.get("gate") or {}).get("at"),
            "consumer_routes": rec.get("consumer_routes")}


def require(cfg: Optional[Config] = None, *,
            schema: Optional[str] = None) -> Dict[str, Any]:
    """The boundary call. Returns the record, or raises ConformanceHalt."""
    rec = evaluate(cfg, schema=schema)
    if rec.get("halted"):
        raise ConformanceHalt(rec)
    return rec
